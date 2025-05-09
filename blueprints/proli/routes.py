from flask import Blueprint, render_template, jsonify, request
from datetime import datetime, timezone
import json
import os
import random

from decorators import login_required

proli_bp = Blueprint("proli_bp", __name__, template_folder="templates", static_folder="static")

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


@proli_bp.route("/")
@login_required
def proli_index():
    return render_template("main.html")

@proli_bp.route("/api/list_all", methods=["GET"])
@login_required
def list_all():
    try:
        with open(os.path.join(BASE_DIR, "data", "list.json")) as jf:
            data = json.load(jf)

        data_sorted = dict(sorted(data.items()))

        return jsonify(data_sorted)
    except Exception as e:
        return str(e), 500

@proli_bp.route("/api/set_checked", methods=["PUT"])
@login_required
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

@proli_bp.route("/api/set_info", methods=["PUT"])
@login_required
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

@proli_bp.route("/api/make_new", methods=["POST"])
@login_required
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

@proli_bp.route("/api/delete_item", methods=["DELETE"])
@login_required
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

@proli_bp.route("/api/new_collection", methods=["POST"])
@login_required
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

@proli_bp.route("/api/rename_collection", methods=["PUT"])
@login_required
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

@proli_bp.route("/api/delete_collection", methods=["DELETE"])
@login_required
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
    proli_bp.run(port=1000, debug=True)
