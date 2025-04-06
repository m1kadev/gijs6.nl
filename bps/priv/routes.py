from flask import Blueprint, Response, request, session, url_for, redirect, render_template
from werkzeug.security import check_password_hash
import os
import json
import requests
import re

priv_bp = Blueprint("priv_bp", __name__, template_folder="templates", static_folder="static")

BASE_DIR = os.path.dirname(__file__)

with open(os.path.join(BASE_DIR, "password.txt"), "r") as f:
    PASSWORD_HASH = f.read().strip()

SESSION_VERSION = "4"


def login_required(func):
    def wrapper(*args, **kwargs):
        if not session.get("logged_in") or session.get("session_version") != SESSION_VERSION:
            nextparam = None
            if "grade" in request.path:
                nextparam = url_for("grade_check")
            elif "homework" in request.path:
                nextparam = url_for("homework_check")
            else:
                nextparam = request.path 
            return redirect(url_for("login", next=nextparam))
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper


@priv_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        password = request.form.get("password")
        if check_password_hash(PASSWORD_HASH, password):
            session["logged_in"] = True
            session["session_version"] = SESSION_VERSION
            session.permanent = True
            next_page = request.args.get("next", url_for("grade_check"))
            return redirect(next_page)
        else:
            return render_template("login.html", error="Ongeldig wachtwoord!")

    next_param = request.args.get("next")
    if next_param:
        message = "Het lijkt erop dat je een beveiligd deel van deze website wil bezoeken. Log in met je wachtwoord."
    else:
        message = "Ik weet niet wat je hier doet maar welkom! Log maar in denk ik?"

    return render_template("login.html", tekst=message)


def read_data_file(file_name):
    file_path = os.path.join(BASE_DIR, "data", file_name)
    with open(file_path, "r") as f:
        return json.load(f)


@priv_bp.route("/grade")
@login_required
def grade_check():
    data = read_data_file("grade.json")
    return render_template("grade.html", **data)


@priv_bp.route("/check/huiswerk")
@login_required
def homework_check():
    homework_data = read_data_file("homework.json")

    return render_template("homework.html", homework=homework_data)

ical_data = read_data_file("ical.json")
first_ical_path = ical_data["path_first"]
second_ical_path = ical_data["path_second"]

@priv_bp.route(f"/rooster-ical-{first_ical_path}")
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
        "MEN": "Mentoruur"
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

                new_line = "SUMMARY:" + subjectAbbreviation + " (" + classroom + " - " + teacher + ")"
            else:
                new_line = line.capitalize()

        else:
            new_line = line
        modified_ics.append(new_line)

    new_ics_content = "\n".join(modified_ics)

    return Response(
        new_ics_content,
        mimetype="text/calendar",
        headers={"Content-Disposition": "attachment; filename=modified.ics"}
    )

@priv_bp.route(f"/rooster-ical-{second_ical_path}")
def second_schedule_ical():
    ICAL_URL = ical_data["url_second"]
    response = requests.get(ICAL_URL)
    response.raise_for_status()
    ics_content = response.text
    modified_ics = []
    pattern = r"^(.+?) - (.+?) - (.+?)$"
    subjects = {
        "ENTL": "Engels",
        "DUTL": "Duits",
        "NAT": "Natuurkunde",
        "NLT": "NLT",
        "NETL": "Nederlands",
        "SCHK": "Scheikunde",
        "WISB": "Wiskunde B",
        "IN": "Informatica",
        "MEN": "Mentoruur"
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

                new_line = "SUMMARY:" + subjectAbbreviation + " (" + classroom + " - " + teacher + ")"
            else:
                new_line = line.capitalize()

        else:
            new_line = line
        modified_ics.append(new_line)

    new_ics_content = "\n".join(modified_ics)

    return Response(
        new_ics_content,
        mimetype="text/calendar",
        headers={"Content-Disposition": "attachment; filename=modified.ics"}
    )
