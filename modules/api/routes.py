from flask import Blueprint, request
from werkzeug.security import check_password_hash
from datetime import datetime, date, timedelta, timezone
import os
import json

api_module = Blueprint("api_module", __name__)

project_dir = os.path.dirname(__file__)
while not os.path.isdir(os.path.join(project_dir, ".git")):
    project_dir = os.path.dirname(project_dir)
project_dir = os.path.abspath(project_dir)

try:
    with open(os.path.join(project_dir, "api_auth.txt"), "r") as f:
        AUTH_HASH = f.read().strip()
except Exception:
    AUTH_HASH = None
    print("No auth hash found.")


@api_module.route("/homegraphupdate", methods=["POST"])
def homepage_graph_api():
    if not AUTH_HASH:
        return "No valid auth", 401

    if not check_password_hash(AUTH_HASH, request.headers.get("auth")):
        return "No valid auth", 401

    try:
        data = request.get_json()
        if not data:
            return "Invalid JSON data", 400
    except Exception as e:
        return f"Error reading JSON: {e}", 400

    # Color constants
    MAX_COLOR = "#06C749"
    MIN_COLOR = "#011207"
    ZERO_COLOR = "#000000"

    def hex_to_rgb(hex_color):
        return [int(hex_color[i : i + 2], 16) for i in (1, 3, 5)]

    def rgb_to_hex(rgb):
        return "#" + "".join(f"{x:02X}" for x in rgb)

    def interpolate_color(value, min_value, max_value):
        if not value or value == 0:
            return ZERO_COLOR

        normalized_value = max(0, min(1, (value - min_value) / (max_value - min_value)))
        min_rgb = hex_to_rgb(MIN_COLOR)
        max_rgb = hex_to_rgb(MAX_COLOR)

        interpolated_rgb = [
            int(min_rgb[i] + (max_rgb[i] - min_rgb[i]) * normalized_value)
            for i in range(3)
        ]

        return rgb_to_hex(interpolated_rgb)

    def generate_week_headers():
        headers = [0] * 52
        current_week = datetime.now().isocalendar()[1]

        for i in range(52):
            week_num = current_week + 1 + i
            if week_num > 52:
                week_num = week_num - 52
            headers[i] = week_num

        return headers

    def get_date_for_cell(week_num, weekday):
        current_week = datetime.now().isocalendar()[1]
        year = (
            datetime.now().year - 1 if week_num > current_week else datetime.now().year
        )

        first_day = date(year, 1, 1) + timedelta(weeks=week_num - 1)
        week_start = first_day - timedelta(days=first_day.weekday())
        return week_start + timedelta(days=weekday)

    def format_cell_message(value, formatted_date, repo_list):
        repo_list_sorted = sorted(repo_list.items(), key=lambda x: x[1], reverse=True)
        repo_list_formatted = "\n".join(
            f"{key.lower()}: {value}" for key, value in repo_list_sorted
        )

        if value == 0:
            return f"No lines changed\non {formatted_date}"
        elif value == 1:
            return f"1 line changed\n on {formatted_date}\n\n{repo_list_formatted}"
        else:
            return (
                f"{value} lines changed\n on {formatted_date}\n\n{repo_list_formatted}"
            )

    headers = generate_week_headers()
    tabledata = []

    # Build table data for each cell
    for weekday in range(7):
        for week_index in range(52):
            week_num = headers[week_index]
            cell_date = get_date_for_cell(week_num, weekday)

            date_str = cell_date.strftime("%Y-%m-%d")
            cell_data = data.get(date_str, {"value": 0, "repos": {}})
            value = cell_data.get("value", 0)
            repo_list = cell_data.get("repos", {})

            formatted_date = cell_date.strftime("%d-%m-%Y")
            message = format_cell_message(value, formatted_date, repo_list)
            grid_area = (
                f"{weekday + 2} / {week_index + 2} / {weekday + 3} / {week_index + 3}"
            )

            tabledata.append(
                {"message": message, "value": value, "grid_area": grid_area}
            )

    min_value = 0
    max_value = int(max(item["value"] for item in tabledata))

    for cell in tabledata:
        cell["color"] = interpolate_color(cell["value"], min_value, max_value)

    # Save data
    now_utc = datetime.now(tz=timezone.utc)
    saved_data = {
        "data": tabledata,
        "last_updated": now_utc.strftime("%d-%m-%Y %H:%M:%S"),
        "last_updated_iso": now_utc.isoformat(),
    }

    # Update in-memory cache
    from app import set_homepage_graph_data

    set_homepage_graph_data(
        tabledata,
        headers,
        saved_data["last_updated"],
        saved_data["last_updated_iso"],
    )

    # Save to disk
    graphdata_path = os.path.join(
        project_dir, "data", "homepagegraph", "graphdata.json"
    )
    headers_path = os.path.join(project_dir, "data", "homepagegraph", "headers.json")

    with open(graphdata_path, "w") as f:
        json.dump(saved_data, f, indent=4)

    with open(headers_path, "w") as f:
        json.dump(headers, f, indent=4)

    return "Lekker bezig", 201
