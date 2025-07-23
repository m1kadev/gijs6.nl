from flask import Blueprint, request
from werkzeug.security import check_password_hash
from datetime import datetime, date, timedelta
from collections import defaultdict
import os
import json

api_bp = Blueprint("api_bp", __name__)

project_dir = os.path.dirname(__file__)

while not os.path.isdir(os.path.join(project_dir, ".git")):
    project_dir = os.path.dirname(project_dir)

project_dir = os.path.abspath(project_dir)

try:
    with open(os.path.join(project_dir, "auth.txt"), "r") as f:
        AUTH_HASH = f.read().strip()
except Exception:
    AUTH_HASH = None
    print("No auth hash found.")


@api_bp.route("/homegraphupdate", methods=["POST"])
def homepage_graph_api():
    if AUTH_HASH:
        if not check_password_hash(AUTH_HASH, request.headers.get("auth")):
            return "No valid auth", 401
        else:
            try:
                data = request.get_json()
                if not data:
                    return "Invalid JSON data", 405
            except Exception as e:
                return f"Error reading JSON: {e}", 404

            headers = ["" for _ in range(52)]
            weeknumindex = defaultdict(int)
            currentweeknum = datetime.now().isocalendar()[1]
            weeknumindex[currentweeknum] = 0
            weekprocess = currentweeknum + 1
            weekprocessheaders = currentweeknum + 1

            for i in range(1, 53):
                weeknumindex[weekprocess] = i
                headers[i - 1] = weekprocessheaders
                weekprocess += 1
                weekprocessheaders += 1
                if weekprocess > 51:
                    weekprocess = 0
                if weekprocessheaders > 52:
                    weekprocessheaders = 1

            tabledata = []

            for weekday in range(7):
                for indexweeknumstuff in range(52):
                    weeknumthiscell = headers[indexweeknumstuff]
                    if weeknumthiscell > datetime.now().isocalendar()[1]:
                        year = datetime.now().year - 1
                    else:
                        year = datetime.now().year
                    first_day = date(year, 1, 1) + timedelta(weeks=weeknumthiscell - 1)
                    thiscelldate = (
                        first_day
                        - timedelta(days=first_day.weekday())
                        + timedelta(days=weekday)
                    )

                    celldata = data.get(
                        datetime.strftime(thiscelldate, "%Y-%m-%d"),
                        {"value": 0, "repos": {}},
                    )
                    value = celldata.get("value", 0)
                    repo_list = celldata.get("repos", {})

                    repo_list_sorted = sorted(
                        repo_list.items(), key=lambda x: x[1], reverse=True
                    )

                    repo_list_formatted = "\n".join(
                        f"{key}: {value}" for key, value in repo_list_sorted
                    )

                    formatted_date = thiscelldate.strftime("%d-%m-%Y")

                    if value == 0:
                        message = f"No lines changed\non {formatted_date}"
                    elif value == 1:
                        message = f"1 line changed\n on {formatted_date}\n\n{repo_list_formatted}"
                    else:
                        message = f"{value} lines changed\n on {formatted_date}\n\n{repo_list_formatted}"

                    tabledata.append(
                        {
                            "message": message,
                            "value": value,
                            "grid_area": f"{weekday + 2} / {indexweeknumstuff + 2} / {weekday + 3} / {indexweeknumstuff + 3}",
                        }
                    )

            min_value = 0
            max_value = int(max(item["value"] for item in tabledata))

            def value_to_color(value, theme):
                max_color = "#06C749"
                if theme == "light":
                    min_color = "#E8FAEE"
                    zero_color = "#FFFFFF"
                else:
                    min_color = "#011207"
                    zero_color = "#000000"
                if value and value != 0:
                    value = int(value)
                    normalized_value = max(
                        0, min(1, (value - min_value) / (max_value - min_value))
                    )

                    min_color_rgb = [int(min_color[i : i + 2], 16) for i in (1, 3, 5)]
                    max_color_rgb = [int(max_color[i : i + 2], 16) for i in (1, 3, 5)]

                    interpolated_color = [
                        int(
                            min_color_rgb[i]
                            + (max_color_rgb[i] - min_color_rgb[i]) * normalized_value
                        )
                        for i in range(3)
                    ]

                    hex_color = "#" + "".join(f"{x:02X}" for x in interpolated_color)
                    return hex_color
                else:
                    return zero_color

            for cell in tabledata:
                value = cell["value"]
                cell["lightcolor"] = value_to_color(value, "light")
                cell["darkcolor"] = value_to_color(value, "dark")

            saved_data = {
                "data": tabledata,
                "last_updated": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
            }

            with open(
                os.path.join(project_dir, "data", "homepagegraph", "graphdata.json"),
                "w",
            ) as f:
                json.dump(saved_data, f, indent=4)

            with open(
                os.path.join(project_dir, "data", "homepagegraph", "headers.json"), "w"
            ) as f:
                json.dump(headers, f, indent=4)

            return "Lekker bezig", 201
    return "No valid auth", 401
