from flask import Blueprint, render_template, jsonify, request
import flask
from datetime import datetime, timezone
from dotenv import load_dotenv
import os
import json
import jinja2
import requests
import re
import platform
import subprocess
import http


from decorators import login_required

admin_bp = Blueprint("admin_bp", __name__, template_folder="templates", static_folder="static")

BASE_DIR = os.path.dirname(__file__)

project_dir = os.path.dirname(__file__)
while not os.path.isdir(os.path.join(project_dir, ".git")):
    project_dir = os.path.dirname(project_dir)
project_dir =  os.path.abspath(project_dir)




load_dotenv()

token = os.getenv("API_TOKEN")



# Dashboard

@admin_bp.route("/")
@login_required
def dashboard():
    os_info = platform.platform()

    version_info = {
        "Python": platform.python_version(),
        "Flask": flask.__version__,
        "Jinja": jinja2.__version__
    }

    return render_template("dashboard.html", os_info=os_info, version_info=version_info)



@admin_bp.route("/api/dashboard/reload", methods=["POST"])
@login_required
def dashboard_reload():
    try:
        response = requests.post("https://eu.pythonanywhere.com/api/v0/user/gijs3/webapps/www.gijs6.nl/reload/", headers={"Authorization": f"Token {token}"})
        response.raise_for_status()
        
        return "Success", 200
    except Exception as e:
        print(e)
        return str(e), 500

@admin_bp.route("/api/dashboard/redeploy", methods=["POST"])
@login_required
def dashboard_redeploy():
    try:
        script_path = os.path.join(project_dir, "deploy.py")
        subprocess.run(["python", script_path], capture_output=True, text=True, check=True)

        return "Success", 200
    except Exception as e:
        return str(e), 500

@admin_bp.route("/api/dashboard/disable", methods=["POST"])
@login_required
def dashboard_disable():
    try:
        response = requests.post("https://eu.pythonanywhere.com/api/v0/user/gijs3/webapps/www.gijs6.nl/disable/", headers={"Authorization": f"Token {token}"})
        response.raise_for_status()

        return "Success", 200
    except Exception as e:
        return str(e), 500





# Libeditor

@admin_bp.route("/lib")
@login_required
def libeditor():
    return render_template("libeditor.html")


@admin_bp.route("/api/libeditor/list_all", methods=["GET"])
@login_required
def libeditor_list_all():
    try:
        with open(os.path.join(project_dir, "data", "libdata.json")) as jf:
            data = json.load(jf)

        return jsonify(data)
    except Exception as e:
        return str(e), 500

@admin_bp.route("/api/libeditor/set_info", methods=["PUT"])
@login_required
def libeditor_set_info():
    try:
        data = request.get_json()

        listitem_index = data.get("listitemIndex")

        title = data.get("title")
        url = data.get("url")
        icon = data.get("icon")

        with open(os.path.join(project_dir, "data", "libdata.json")) as jf:
            data = json.load(jf)
        
        data[int(listitem_index)]["title"] = title
        data[int(listitem_index)]["link"] = url
        data[int(listitem_index)]["icon"] = icon


        with open(os.path.join(project_dir, "data", "libdata.json"), "w") as jf:
            json.dump(data, jf, indent=4)
        
        return "Success", 200
    except Exception as e:
        return str(e), 500
    

@admin_bp.route("/api/libeditor/make_new", methods=["POST"])
@login_required
def libeditor_make_new():
    try:
        with open(os.path.join(project_dir, "data", "libdata.json")) as jf:
            data = json.load(jf)
        
        data.append(
            {
                "title": "TITLE",
                "link": "URL",
                "icon": "fa-solid fa-arrow-up-right-from-square"
            }
        )

        with open(os.path.join(project_dir, "data", "libdata.json"), "w") as jf:
            json.dump(data, jf, indent=4)

        return "Success", 200
    except Exception as e:
        return str(e), 500

@admin_bp.route("/api/libeditor/delete_item", methods=["DELETE"])
@login_required
def libeditor_delete_item():
    try:
        data = request.get_json()

        listitem_index = data.get("listitemIndex")

        with open(os.path.join(project_dir, "data", "libdata.json")) as jf:
            data = json.load(jf)
        
        data.pop(int(listitem_index))

        with open(os.path.join(project_dir, "data", "libdata.json"), "w") as jf:
            json.dump(data, jf, indent=4)
        
        return "Success", 200
    except Exception as e:
        return str(e), 500

status_code_dict = {status.value: status.phrase for status in http.HTTPStatus}

http_status_colors = {
    "1": "blue",
    "2": "green",
    "3": "blue",
    "4": "yellow",
    "5": "red"
}

http_method_colors = {
    "GET": "green",
    "POST": "blue",
    "PUT": "yellow",
    "PATCH": "yellow",
    "DELETE": "red",
    "HEAD": "green",
    "OPTIONS": "blue"
}



@admin_bp.route("/log")
@login_required
def logview():
    today = datetime.now(timezone.utc).strftime('%d %b')
    return render_template("logview.html", today=today)


@admin_bp.route("/api/logview/listall")
@login_required
def logview_listall():
    days_ago = request.args.get("days_ago")
    formatted_suffix = f".{days_ago}" + (".gz" if days_ago != "1" else "") if days_ago and days_ago != "0" else ""

    try:
        with open(f"/var/log/www.gijs6.nl.access.log{formatted_suffix}") as f:
            loglines = f.readlines()
    except FileNotFoundError:
        try:
            with open(os.path.join(BASE_DIR, "data", "log.txt")) as f:
                loglines = f.readlines()
        except FileNotFoundError:
            loglines = ['123.123.123.123 - - [02/May/2025:02:46:44 +0000] "GET /wp-includes HTTP/1.1" 404 4046 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36" "123.123.123.123" response-time=0.001']
    

    pattern = re.compile(
        r'(?P<ip>\d+\.\d+\.\d+\.\d+)\s+- - '
        r'\[(?P<datetime>[^\]]+)\] '
        r'"(?P<method>\w+) (?P<path>[^ ]+) (?P<protocol>[^"]+)" '
        r'(?P<status_code>\d+) (?P<size>\d+) '
        r'"(?P<referrer>[^"]*)" '
        r'"(?P<user_agent>[^"]*)" '
        r'"(?P<alt_ip>[^"]+)" '
        r'response-time=(?P<response_time>[\d\.]+)'
    )

    finallog = []
    
    for line in loglines:
        match = pattern.match(line)

        if match:
            log_dict = match.groupdict()
            log_dict["status"] = f"{log_dict['status_code']} {status_code_dict.get(int(log_dict['status_code']), 'UNKNOWN')}"
            log_dict["status_color"] = http_status_colors.get(log_dict["status_code"][0], "gray")
            log_dict["method_color"] = http_method_colors.get(log_dict["method"], "gray")
            log_dict["datetime"] = datetime.strptime(log_dict["datetime"], "%d/%b/%Y:%H:%M:%S %z").strftime("%d %b %H:%M:%S")
            log_dict["referrer"] = re.sub(r"https://www\.gijs6\.nl", "~", log_dict["referrer"]) if log_dict["referrer"] != "-" else "None"
            #log_dict["referrer"] = re.sub(r"https?://(www\.)?gijs6\.nl", "", log_dict["referrer"])
            finallog.append(log_dict)

    
    path = request.args.get("path")
    methods = request.args.get("methods")
    statuses = request.args.get("statuses")

    if methods:
        methods_list = methods.split(",")
    else:
        methods_list = []

    if statuses:
        statuses_list = statuses.split(",")
    else:
        statuses_list = []

    print(statuses)

    def checkList(list, key):
        if list and key:
            return key in list
        else:
            return True

    finallog = [logitem for logitem in finallog if path in logitem["path"] and checkList(methods_list, logitem["method"]) and checkList(statuses_list, logitem["status_code"][0])]

    return jsonify(finallog)
