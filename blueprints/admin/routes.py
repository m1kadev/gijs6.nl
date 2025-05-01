from flask import Blueprint, render_template, jsonify, request
import flask
from dotenv import load_dotenv
import os
import json
import jinja2
import requests
import sys
import platform
import subprocess


from decorators import login_required

admin_bp = Blueprint("admin_bp", __name__, template_folder="templates", static_folder="static")

BASE_DIR = os.path.dirname(__file__)

project_dir = os.path.dirname(__file__)
while not os.path.isdir(os.path.join(project_dir, ".git")):
    project_dir = os.path.dirname(project_dir)
project_dir =  os.path.abspath(project_dir)




load_dotenv()

token = os.getenv("API_TOKEN")


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



# Libeditor

@admin_bp.route("/lib")
@login_required
def lib_editor():
    return render_template("lib_editor.html")


@admin_bp.route("/api/libeditor/list_all", methods=["GET"])
@login_required
def lib_editor_list_all():
    try:
        with open(os.path.join(project_dir, "data", "libdata.json")) as jf:
            data = json.load(jf)

        return jsonify(data)
    except Exception as e:
        return str(e), 500

@admin_bp.route("/api/libeditor/set_info", methods=["PUT"])
@login_required
def lib_editor_set_info():
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
def lib_editor_make_new():
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
def lib_editor_delete_item():
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
        result = subprocess.run([sys.executable, script_path])

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
