from flask import Blueprint, render_template, jsonify, request, session, redirect, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime, timezone
import json
import os
import string
import random

jstd_bp = Blueprint("jstd_bp", __name__, template_folder="templates", static_folder="static")

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


try:
    with open(os.path.join(BASE_DIR, "password.txt"), "r") as f:
        PASSWORD_HASH = f.read().strip()
except FileNotFoundError:
    if __name__ == "__main__":
        password = ''.join(random.choices(string.ascii_letters + string.digits, k=random.randint(25, 45)))
        # Only in development. If this would be executed on production that would be very very bad...
        print(f"\033[91mThere is no password registred for the JSTD. You can use the password '{password}'.\033[0m")
        PASSWORD_HASH = generate_password_hash(password)
    else:
        raise FileNotFoundError


@jstd_bp.before_request
def login_check():
    if "login" not in request.path and "static" not in request.path:
        if not session.get("jstd_logged_in"):
            return redirect(url_for("jstd_bp.login"))


@jstd_bp.route("/login", methods=["GET", "POST"])
def login():
    if not session.get("jstd_logged_in"):
        if request.method == "POST":
            password = request.form.get("password")
            if check_password_hash(PASSWORD_HASH, password):
                session["jstd_logged_in"] = True
                session.permanent = True

                return redirect(url_for("jstd_bp.jstd_index"))
            else:
                return render_template("login_jstd.html", error="WRONG LOL")
            
        return render_template("login_jstd.html")
    return redirect(url_for("jstd_bp.jstd_index"))

@jstd_bp.route("/")
def jstd_index():
    return render_template("main.html")

@jstd_bp.route("/api/list_all", methods=["GET"])
def list_all():
    try:
        with open(os.path.join(BASE_DIR, "data", "list.json")) as jf:
            data = json.load(jf)

        data_sorted = dict(sorted(data.items()))

        return jsonify(data_sorted)
    except Exception as e:
        return str(e), 500

@jstd_bp.route("/api/set_checked", methods=["PUT"])
def set_checked():
    try:
        req_data = request.get_json()

        collection = req_data.get("collection")
        listitem_index = req_data.get("listitemIndex")
        checked = req_data.get("checked")

        with open(os.path.join(BASE_DIR, "data", "list.json")) as jf:
            data = json.load(jf)
        
        data[collection][int(listitem_index)]["checked"] = checked

        with open(os.path.join(BASE_DIR, "data", "list.json"), "w") as jf:
            json.dump(data, jf, indent=4)
        
        return jsonify({"status": "success"}), 200
    except Exception as e:
        return str(e), 500

@jstd_bp.route("/api/set_info", methods=["PUT"])
def set_info():
    try:
        req_data = request.get_json()

        collection = req_data.get("collection")
        listitem_index = req_data.get("listitemIndex")

        title = req_data.get("title")
        datetime = req_data.get("datetime")
        content = req_data.get("content")

        with open(os.path.join(BASE_DIR, "data", "list.json")) as jf:
            data = json.load(jf)
        
        data[collection][int(listitem_index)]["title"] = title
        data[collection][int(listitem_index)]["datetime"] = datetime
        data[collection][int(listitem_index)]["content"] = content


        with open(os.path.join(BASE_DIR, "data", "list.json"), "w") as jf:
            json.dump(data, jf, indent=4)
        
        return jsonify({"status": "success"}), 200
    except Exception as e:
        return str(e), 500

@jstd_bp.route("/api/make_new", methods=["POST"])
def make_new():
    try:
        req_data = request.get_json()

        collection = req_data.get("collection")

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

        return jsonify({"status": "success"}), 200
    except Exception as e:
        return str(e), 500

@jstd_bp.route("/api/delete_item", methods=["DELETE"])
def delete_item():
    try:
        req_data = request.get_json()

        collection = req_data.get("collection")
        listitem_index = req_data.get("listitemIndex")

        with open(os.path.join(BASE_DIR, "data", "list.json")) as jf:
            data = json.load(jf)
        
        data[collection].pop(int(listitem_index))

        with open(os.path.join(BASE_DIR, "data", "list.json"), "w") as jf:
            json.dump(data, jf, indent=4)
        
        return jsonify({"status": "success"}), 200
    except Exception as e:
        return str(e), 500

@jstd_bp.route("/api/new_collection", methods=["POST"])
def new_collection():
    try:
        with open(os.path.join(BASE_DIR, "data", "list.json")) as jf:
            data = json.load(jf)
        
        chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        name = "".join(random.choices(chars, k=5))

        data[f"Collection{name}"] = []

        with open(os.path.join(BASE_DIR, "data", "list.json"), "w") as jf:
            json.dump(data, jf, indent=4)
        
        return jsonify({"status": "success"}), 200
    except Exception as e:
        return str(e), 500

@jstd_bp.route("/api/rename_collection", methods=["PUT"])
def rename_collection():
    try:
        req_data = request.get_json()

        old_name = req_data.get("oldName")
        new_name = req_data.get("newName")

        with open(os.path.join(BASE_DIR, "data", "list.json")) as jf:
            data = json.load(jf)
        
        data[new_name] = data.pop(old_name)

        with open(os.path.join(BASE_DIR, "data", "list.json"), "w") as jf:
            json.dump(data, jf, indent=4)
        
        return jsonify({"status": "success"}), 200
    except Exception as e:
        return str(e), 500

@jstd_bp.route("/api/delete_collection", methods=["DELETE"])
def delete_collection():
    try:
        req_data = request.get_json()

        collection = req_data.get("collection")

        with open(os.path.join(BASE_DIR, "data", "list.json")) as jf:
            data = json.load(jf)
        
        data.pop(collection)

        with open(os.path.join(BASE_DIR, "data", "list.json"), "w") as jf:
            json.dump(data, jf, indent=4)
        
        return jsonify({"status": "success"}), 200
    except Exception as e:
        return str(e), 500

if __name__ == "__main__":
    jstd_bp.run(port=1000, debug=True)
