from flask import Blueprint, render_template, jsonify, request, session, redirect, url_for
from datetime import datetime, timezone
from werkzeug.security import check_password_hash
import json
import os
import random

proli_bp = Blueprint("proli_bp", __name__, template_folder="templates", static_folder="static")

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(BASE_DIR, "password.txt"), "r") as f:
    PASSWORD_HASH = f.read().strip()


@proli_bp.before_request
def require_login():
    if "login" not in request.url:
        if not session.get("is_logged_in"):
            return redirect(url_for("proli_bp.proli_login"))


@proli_bp.route("/")
def proli_index():
    return render_template("main.html")

@proli_bp.route("/login", methods=["GET", "POST"])
def proli_login():
    if request.method == "POST":
        password = request.form.get("password")
        if check_password_hash(PASSWORD_HASH, password):
            session["is_logged_in"] = True
            session.permanent = True
            return redirect(url_for("proli_bp.proli_index"))
        else:
            return render_template("login.html", error="Wrong! Lol!")
        
    return render_template("login.html")


@proli_bp.route("/api/list_all", methods=["GET"])
def list_all():
    try:
        with open(os.path.join(BASE_DIR, "data", "list.json")) as jf:
            data = json.load(jf)

        
        data = dict(sorted(data.items(), key=lambda item: len(item[1])))

        return jsonify(data)
    except Exception as e:
        return str(e), 500

@proli_bp.route("/api/set_checked", methods=["PUT"])
def set_checked():
    try:
        data = request.get_json()

        collection = data.get("collection")
        listitem_index = data.get("listitemIndex")
        checked = data.get("checked")

        with open(os.path.join(BASE_DIR, "data", "list.json")) as jf:
            data = json.load(jf)
        
        data[collection][int(listitem_index)]["check"] = checked

        with open(os.path.join(BASE_DIR, "data", "list.json"), "w") as jf:
            json.dump(data, jf, indent=4)
        
        return "Success", 200
    except Exception as e:
        return str(e), 500

@proli_bp.route("/api/set_info", methods=["PUT"])
def set_info():
    try:
        data = request.get_json()

        collection = data.get("collection")
        listitem_index = data.get("listitemIndex")

        title = data.get("title")
        datetime = data.get("datetime")
        content = data.get("content")

        with open(os.path.join(BASE_DIR, "data", "list.json")) as jf:
            data = json.load(jf)
        
        data[collection][int(listitem_index)]["title"] = title
        data[collection][int(listitem_index)]["datetime"] = datetime
        data[collection][int(listitem_index)]["content"] = content


        with open(os.path.join(BASE_DIR, "data", "list.json"), "w") as jf:
            json.dump(data, jf, indent=4)
        
        return "Success", 200
    except Exception as e:
        return str(e), 500

@proli_bp.route("/api/make_new", methods=["POST"])
def make_new():
    try:
        data = request.get_json()

        collection = data.get("collection")

        with open(os.path.join(BASE_DIR, "data", "list.json")) as jf:
            data = json.load(jf)
        
        data[collection].append(
            {
                "title": "Title",
                "content": "Content",
                "datetime": datetime.now(timezone.utc).isoformat(),
                "checked": False,
            }
        )

        with open(os.path.join(BASE_DIR, "data", "list.json"), "w") as jf:
            json.dump(data, jf, indent=4)

        return "Success", 200
    except Exception as e:
        return str(e), 500

@proli_bp.route("/api/delete_item", methods=["DELETE"])
def delete_item():
    try:
        data = request.get_json()

        collection = data.get("collection")
        listitem_index = data.get("listitemIndex")

        with open(os.path.join(BASE_DIR, "data", "list.json")) as jf:
            data = json.load(jf)
        
        data[collection].pop(int(listitem_index))

        with open(os.path.join(BASE_DIR, "data", "list.json"), "w") as jf:
            json.dump(data, jf, indent=4)
        
        return "Success", 200
    except Exception as e:
        return str(e), 500

@proli_bp.route("/api/new_collection", methods=["POST"])
def new_collection():
    try:
        with open(os.path.join(BASE_DIR, "data", "list.json")) as jf:
            data = json.load(jf)
        
        chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        name = "".join(random.choices(chars, k=5))

        data[f"Collection{name}"] = [{
                "title": "Title",
                "content": "Content",
                "datetime": datetime.now(timezone.utc).isoformat(),
                "checked": False,
            }]

        with open(os.path.join(BASE_DIR, "data", "list.json"), "w") as jf:
            json.dump(data, jf, indent=4)
        
        return "Success", 200
    except Exception as e:
        return str(e), 500

@proli_bp.route("/api/rename_collection", methods=["PUT"])
def rename_collection():
    try:
        data = request.get_json()

        old_name = data.get("oldName")
        new_name = data.get("newName")

        with open(os.path.join(BASE_DIR, "data", "list.json")) as jf:
            data = json.load(jf)
        
        data[new_name] = data.pop(old_name)

        with open(os.path.join(BASE_DIR, "data", "list.json"), "w") as jf:
            json.dump(data, jf, indent=4)
        
        return "Success", 200
    except Exception as e:
        return str(e), 500

@proli_bp.route("/api/delete_collection", methods=["DELETE"])
def delete_collection():
    try:
        data = request.get_json()

        collection = data.get("collection")

        with open(os.path.join(BASE_DIR, "data", "list.json")) as jf:
            data = json.load(jf)
        
        data.pop(collection)

        with open(os.path.join(BASE_DIR, "data", "list.json"), "w") as jf:
            json.dump(data, jf, indent=4)
        
        return "Success", 200
    except Exception as e:
        return str(e), 500

if __name__ == "__main__":
    proli_bp.run(port=1000, debug=True)
