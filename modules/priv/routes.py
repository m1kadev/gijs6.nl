from flask import Blueprint, Response, render_template
import os
import json
import requests
import re

from decorators import login_required

priv_module = Blueprint(
    "priv_module",
    __name__,
    template_folder="priv_templates",
    static_folder="priv_static",
)

BASE_DIR = os.path.dirname(__file__)


def read_data_file(file_name):
    file_path = os.path.join(BASE_DIR, "data", file_name)
    with open(file_path, "r") as f:
        return json.load(f)


@priv_module.route("/grade")
@login_required
def grade_check():
    data = read_data_file("grade.json")
    return render_template("grade.html", **data)


ical_data = read_data_file("ical.json")
first_ical_path = "/" + ical_data["path_first"]


@priv_module.route(first_ical_path)
def first_schedule_ical():
    ICAL_URL = ical_data["url_first"]
    response = requests.get(ICAL_URL)
    response.raise_for_status()
    ics_content = response.text
    modified_ics = []
    pattern = r"^(.+?) - (.+?) - (.+?)$"
    subjects = {
        "BIOL": "Biologie",
        "CKV": "CKV",
        "ENTL": "Engels",
        "FATL": "Frans",
        "MAAT": "Maatschappijleer",
        "NAT": "Natuurkunde",
        "NLT": "NLT",
        "NETL": "Nederlands",
        "SCHK": "Scheikunde",
        "WISB": "Wiskunde B",
        "LO": "Gym",
        "MEN": "Mentoruur",
    }

    for line in ics_content.splitlines():
        if "SUMMARY" in line:
            isClass = re.match(pattern, line.strip().replace("SUMMARY:", ""))
            if isClass:
                classroom = isClass.group(1)
                classGroup = isClass.group(2)
                teacher = isClass.group(3)

                subjectAbbreviation = ""

                for abbreviation in subjects.keys():
                    if abbreviation in classGroup:
                        subjectAbbreviation = subjects[abbreviation]
                if not subjectAbbreviation:
                    subjectAbbreviation = classGroup

                new_line = (
                    "SUMMARY:"
                    + subjectAbbreviation
                    + " ("
                    + classroom
                    + " - "
                    + teacher
                    + ")"
                )
            else:
                new_line = line.capitalize()

        else:
            new_line = line
        modified_ics.append(new_line)

    new_ics_content = "\n".join(modified_ics)

    return Response(
        new_ics_content,
        mimetype="text/calendar",
        headers={"Content-Disposition": "attachment; filename=modified.ics"},
    )
