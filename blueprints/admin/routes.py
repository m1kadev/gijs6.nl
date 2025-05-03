from flask import Blueprint, render_template, jsonify, request, current_app
import flask
from datetime import datetime
from ua_parser import parse
from dotenv import load_dotenv
import os
import json
import jinja2
import requests
import re
import platform
import subprocess
import http
import gzip


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

    result = subprocess.check_output(["git", "log", "-n 50", '--pretty=format:%h|%s|%ad', '--date=iso'], text=True, cwd=project_dir)
    
    commits = []
    for line in result.strip().split('\n'):
        short_hash, message, datetime = line.split('|', 3)
        commits.append({
            "hash": short_hash.strip(),
            "message": message.strip(),
            "datetime": datetime.strip()
        })
    return render_template("dashboard.html", os_info=os_info, version_info=version_info, commits=commits)



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
        subprocess.check_output(["python", script_path], text=True)

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


@admin_bp.route("/api/dashboard/list_urls")
@login_required
def dashboard_list_urls():
    urls = []
    for rule in current_app.url_map.iter_rules():
        #if ('.' in rule.endpoint and "blog" not in rule.endpoint) or "<" in rule.rule:
        #    continue
        if "<" in rule.rule or "api" in rule.rule or "kodo" in rule.rule:
            continue

        urls.append({
            "url": rule.rule,
            "method": [method for method in rule.methods if method not in ("OPTIONS", "HEAD")][0],
            "endpoint": rule.endpoint
        })

    
    return jsonify(urls)



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
    return render_template("logview.html")


@admin_bp.route("/api/logview/listall")
@login_required
def logview_listall():
    log_num = request.args.get("log_num")
    formatted_suffix = f".{log_num}" + (".gz" if log_num != "1" else "") if log_num and log_num != "0" else ""

    try:
        path = f"/var/log/www.gijs6.nl.access.log{formatted_suffix}"
        if "gz" in path:
            with gzip.open(path, "rt") as log_gz_file:
                loglines = log_gz_file.readlines()
        else:
            with open(f"/var/log/www.gijs6.nl.access.log{formatted_suffix}", encoding="utf-8") as f:
                loglines = f.readlines()
    except FileNotFoundError:
        try:
            with open(os.path.join(BASE_DIR, "data", "log.txt")) as f:
                loglines = f.readlines()
        except FileNotFoundError:
            loglines = [f'999.999.999.999 - - [31/Dec/9999:23:59:59 +0000] "ERROR ERROR ERROR" 999 999 "-" "FILENOTFOUND: {path}" "999.999.999.999" response-time=ERROR']
    

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


            ua = parse(log_dict["user_agent"])
            user_agent_formatted = f"{getattr(ua.user_agent, 'family', '?')} {getattr(ua.user_agent, 'major', '?')} - {getattr(ua.os, 'family', '?')} {getattr(ua.os, 'major', '?')} - {getattr(ua.device, 'brand', '?')} {getattr(ua.device, 'family', '?')} ({getattr(ua.device, 'model', '?')})"
            
            if user_agent_formatted.count('?') > 3:
                log_dict["user_agent_formatted"] = ua.string
            else:
                log_dict["user_agent_formatted"] = user_agent_formatted


            log_dict["referrer"] = re.sub(r"https://www\.gijs6\.nl", "~", log_dict["referrer"]) if log_dict["referrer"] != "-" else "None"
            #log_dict["referrer"] = re.sub(r"https?://(www\.)?gijs6\.nl", "", log_dict["referrer"])
            finallog.append(log_dict)

    
    path = request.args.get("path", "None")
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

    def checkList(list, key):
        if list and key:
            return key in list
        else:
            return True

    finallog = [logitem for logitem in finallog if path in logitem["path"] and checkList(methods_list, logitem["method"]) and checkList(statuses_list, logitem["status_code"][0])]

    return jsonify(finallog.reverse())
