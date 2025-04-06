from flask import Flask, redirect, render_template, send_from_directory, url_for, request
from collections import defaultdict
from datetime import timedelta, datetime, date
from werkzeug.security import check_password_hash
import json
import locale
import os
import subprocess

# Blueprints
from bps import load_blueprints


locale.setlocale(locale.LC_TIME, "nl_NL")

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.permanent_session_lifetime = timedelta(days=365)

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Blueprints

for bp, prefix in load_blueprints():
    app.register_blueprint(bp, url_prefix=prefix)


# Files

@app.route("/favicon.ico")
@app.route("/favicon")
def favicon():
    return send_from_directory("static", "favs/dice.ico", mimetype="image/vnd.microsoft.icon")

@app.route("/.well-known/security.txt")
def securitytxt():
    return send_from_directory("static", "txts/security.txt", mimetype="text/plain")

@app.route("/security.txt")
def securitytxtredirect():
    return redirect(url_for("securitytxt")), 301

@app.route("/robots")
@app.route("/robots.txt")
def robots():
    return send_from_directory("static", "txts/robots.txt", mimetype="text/plain")



def get_commit_and_deploy_date():
    with open(os.path.join(BASE_DIR, "data", "last_deploy.txt"), "r") as f:
        latest_deploy_date = f.read().strip()

    latest_commit_hash = subprocess.check_output(["git", "log", "-1", "--pretty=format:%h"], cwd=BASE_DIR).strip().decode()
    latest_commit_hash_long = subprocess.check_output(["git", "log", "-1", "--pretty=format:%H"], cwd=BASE_DIR).strip().decode()
    latest_commit_timestamp = int(subprocess.check_output(["git", "log", "-1", "--pretty=format:%ct"], cwd=BASE_DIR).strip())
    latest_commit_date = datetime.fromtimestamp(latest_commit_timestamp).strftime("%d-%m-%Y at %H:%M:%S")

    comdepdata = {
        "latest_deploy_date": latest_deploy_date,
        "latest_commit_hash": latest_commit_hash,
        "latest_commit_hash_long": latest_commit_hash_long,
        "latest_commit_date": latest_commit_date
    }

    return comdepdata


comdepdata = get_commit_and_deploy_date()


@app.context_processor
def inject_comdepdata():
    return comdepdata


@app.route("/")
def home():
    with open(os.path.join(BASE_DIR, "data", "homepagegraph", "graphdata.json"), "r") as file:
        graphdatafull = json.load(file)

    graphdata = graphdatafull["data"]
    last_updated = graphdatafull["last_updated"]

    with open(os.path.join(BASE_DIR, "data", "homepagegraph", "headers.json"), "r") as file:
        headers = json.load(file)

    return render_template("home.html", graphdata=graphdata, headers=headers, last_updated=last_updated)


@app.route("/code")
def code():
    return render_template("code.html")

@app.route("/lib")
def lib():
    with open(os.path.join(BASE_DIR, "data", "libdata.json"), "r") as file:
        libdata = json.load(file)
    
    return render_template("lib.html", data=libdata)


@app.route("/projects")
def projects():
    return render_template("projects.html")

@app.route("/colophon")
def colofon():
    return render_template("colophon.html")


with open(os.path.join(BASE_DIR, "auth.txt"), "r") as f:
    AUTH_HASH = f.read().strip()


@app.route("/homegraphupdate", methods=["POST"])
def homepage_graph_api():
    if not check_password_hash(AUTH_HASH, request.headers.get("auth")):
        return "No valid auth", 401
    else:
        try:
            data = request.get_json()
            if not data:
                return "Invalid JSON data", 405
        except Exception as e:
            app.logger.info(f"Error reading JSON: {e}")
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


        min_value = 0
        max_value = int(max(item["value"] for item in data.values()))

        def value_to_color(value, theme):
            max_color="#06C749"
            if theme == "light":
                min_color = "#ECFAF1"
                zero_color = "#FFFFFF"
            else:
                min_color = "#000E05"
                zero_color = "#000000"
            if value and value != 0:
                value = int(value)
                normalized_value = max(0, min(1, (value - min_value) / (max_value - min_value)))

                min_color_rgb = [int(min_color[i:i+2], 16) for i in (1, 3, 5)]
                max_color_rgb = [int(max_color[i:i+2], 16) for i in (1, 3, 5)]

                interpolated_color = [
                    int(min_color_rgb[i] + (max_color_rgb[i] - min_color_rgb[i]) * normalized_value)
                    for i in range(3)
                ]

                hex_color = "#" + "".join(f"{x:02X}" for x in interpolated_color)
                return hex_color
            else:
                return zero_color

        tabledata = [["" for _ in range(52)] for _ in range(7)]
        for weekday in range(7):
            for indexweeknumstuff in range(52):
                weeknumthiscell = headers[indexweeknumstuff]
                if weeknumthiscell > datetime.now().isocalendar()[1]:
                    year = datetime.now().year - 1
                else:
                    year = datetime.now().year
                first_day = date(year, 1, 1) + timedelta(weeks=weeknumthiscell-1)
                thiscelldate = first_day - timedelta(days=first_day.weekday()) + timedelta(days=weekday)

                celldata = data.get(datetime.strftime(thiscelldate, "%Y-%m-%d"), {"value": 0, "repos": {}})
                value = celldata.get("value", 0)
                repo_list = celldata.get("repos", {})

                repo_list_sorted = sorted(repo_list.items(), key=lambda x: x[1], reverse=True)

                repo_list_formatted = "\n".join(f"{key}: {value}" for key, value in repo_list_sorted)

                formatted_date = thiscelldate.strftime("%d-%m-%Y")

                if value == 0:
                    message = f"No lines changed on {formatted_date}"
                elif value == 1:
                    message = f"1 line changed on {formatted_date}\n\n{repo_list_formatted}"
                else:
                    message = f"{value} lines changed on {formatted_date}\n\n{repo_list_formatted}"

                tabledata[weekday][indexweeknumstuff] = {
                    "value": value,
                    "date": thiscelldate.strftime("%d-%m-%Y"),
                    "message": message,
                    "darkcolor": value_to_color(value, "dark"),
                    "lightcolor": value_to_color(value, "light")
                }

        saved_data = {
            "data": tabledata,
            "last_updated": datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        }

        with open(os.path.join(BASE_DIR, "data", "homepagegraph", "graphdata.json"), "w") as f:
            json.dump(saved_data, f, indent=4)

        with open(os.path.join(BASE_DIR, "data", "homepagegraph", "headers.json"), "w") as f:
            json.dump(headers, f, indent=4)

        return "Lekker bezig", 201



@app.errorhandler(404)
def not_found(e):
    with open(os.path.join(BASE_DIR, "data", "redirects.json"), "r") as file:
        redirects = json.load(file)

    path = request.path.strip("/")
    if path in redirects:
        return redirect(redirects[path], code=308)
    return render_template("404.html", e=e), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template("500.html", e=e), 500


if __name__ == "__main__":
    app.run(port=7000, debug=True)
