from flask import Blueprint, render_template, jsonify, request, session, redirect, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime, timezone
import json
import string
import os
import random


shopping_bp = Blueprint("shopping_bp", __name__, template_folder="templates", static_folder="static")

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


try:
    with open(os.path.join(BASE_DIR, "password.txt"), "r") as f:
        PASSWORD_HASH = f.read().strip()
except FileNotFoundError:
    if __name__ == "__main__":
        password = ''.join(random.choices(string.ascii_letters + string.digits, k=random.randint(25, 45)))
        # Only in development. If this would be executed on production that would be very very bad...
        print(f"\033[91mThere is no password registred for the shopping list. You can use the password '{password}'.\033[0m")
        PASSWORD_HASH = generate_password_hash(password)
    else:
        raise FileNotFoundError


@shopping_bp.before_request
def login_check():
    if "login" not in request.path:
        if not session.get("logged_in_shopping"):
            return redirect(url_for("shopping_bp.login"))

@shopping_bp.route("/login", methods=["GET", "POST"])
def login():
    if not session.get("logged_in_shopping"):
        if request.method == "POST":
            password = request.form.get("password")
            if check_password_hash(PASSWORD_HASH, password):
                session["logged_in_shopping"] = True
                session.permanent = True

                return redirect(url_for("shopping_bp.shopping_index"))
            else:
                return render_template("login_shopping.html", error="FOUT")
            
        return render_template("login_shopping.html")
    return redirect(url_for("shopping_bp.shopping_index"))

@shopping_bp.route("/")
def shopping_index():
    return render_template("shopping.html")

@shopping_bp.route("/api/list_all", methods=["GET"])
def list_all():
    try:
        with open(os.path.join(BASE_DIR, "data", "list.json")) as jf:
            data = json.load(jf)

        return jsonify(data)
    except Exception as e:
        return str(e), 500

@shopping_bp.route("/api/set_checked", methods=["PUT"])
def set_checked():
    try:
        req_data = request.get_json()

        listitem_index = req_data.get("listitemIndex")
        checked = req_data.get("checked")

        with open(os.path.join(BASE_DIR, "data", "list.json")) as jf:
            data = json.load(jf)
        
        data[int(listitem_index)]["checked"] = checked

        with open(os.path.join(BASE_DIR, "data", "list.json"), "w") as jf:
            json.dump(data, jf, indent=4)
        
        return "Success", 200
    except Exception as e:
        return str(e), 500

@shopping_bp.route("/api/set_info", methods=["PUT"])
def set_info():
    try:
        req_data = request.get_json()

        listitem_index = req_data.get("listitemIndex")

        title = req_data.get("title")
        datetime = req_data.get("datetime")
        content = req_data.get("content")

        with open(os.path.join(BASE_DIR, "data", "list.json")) as jf:
            data = json.load(jf)
        
        data[int(listitem_index)]["title"] = title
        data[int(listitem_index)]["datetime"] = datetime
        data[int(listitem_index)]["content"] = content


        with open(os.path.join(BASE_DIR, "data", "list.json"), "w") as jf:
            json.dump(data, jf, indent=4)
        
        return "Success", 200
    except Exception as e:
        return str(e), 500

@shopping_bp.route("/api/make_new", methods=["POST"])
def make_new():
    try:
        with open(os.path.join(BASE_DIR, "data", "list.json")) as jf:
            data = json.load(jf)
        
        data.append(
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

@shopping_bp.route("/api/delete_item", methods=["DELETE"])
def delete_item():
    try:
        req_data = request.get_json()

        listitem_index = req_data.get("listitemIndex")

        with open(os.path.join(BASE_DIR, "data", "list.json")) as jf:
            data = json.load(jf)
        
        data.pop(int(listitem_index))

        with open(os.path.join(BASE_DIR, "data", "list.json"), "w") as jf:
            json.dump(data, jf, indent=4)
        
        return "Success", 200
    except Exception as e:
        return str(e), 500

if __name__ == "__main__":
    shopping_bp.run(port=1000, debug=True)
