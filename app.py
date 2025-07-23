from flask import (
    Flask,
    redirect,
    render_template,
    send_from_directory,
    url_for,
    request,
)

from datetime import timedelta, datetime
import json
import locale
import os
import subprocess
from blueprints import load_blueprints



locale.setlocale(locale.LC_TIME, "nl_NL")


app = Flask(__name__)


for bp, prefix in load_blueprints():
    try:
        app.register_blueprint(bp, url_prefix=prefix)
    except Exception as e:
        print(f"An error occured while trying to load {bp} as a blueprint: {e}")


@app.route("/favicon.ico")
@app.route("/favicon")
def favicon():
    return send_from_directory(
        "static", "favs/new_fav.ico", mimetype="image/vnd.microsoft.icon"
    )


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


with app.app_context():
    latest_commit_hash = (
        subprocess.check_output(
            ["git", "log", "-1", "--pretty=format:%h"], cwd=app.root_path
        )
        .strip()
        .decode()
    )

    latest_commit_hash_long = (
        subprocess.check_output(
            ["git", "log", "-1", "--pretty=format:%H"], cwd=app.root_path
        )
        .strip()
        .decode()
    )

    latest_commit_timestamp = int(
        subprocess.check_output(
            ["git", "log", "-1", "--pretty=format:%ct"], cwd=app.root_path
        ).strip()
    )
    latest_commit_date = datetime.fromtimestamp(latest_commit_timestamp).strftime(
        "%d-%m-%Y at %H:%M:%S"
    )

    commit_data = {
        "latest_commit_hash": latest_commit_hash,
        "latest_commit_hash_long": latest_commit_hash_long,
        "latest_commit_date": latest_commit_date,
    }


@app.context_processor
def inject_commit_data():
    return commit_data


@app.route("/")
def index():
    with open(
        os.path.join(app.root_path, "data", "homepagegraph", "graphdata.json"), "r"
    ) as file:
        graphdatafull = json.load(file)

    graphdata = graphdatafull["data"]
    last_updated = graphdatafull["last_updated"]

    try:
        with open(
            os.path.join(app.root_path, "data", "homepagegraph", "headers.json"), "r"
        ) as file:
            headers = json.load(file)
    except FileNotFoundError:
        headers = []
        print("No headers found.")

    headers = [str(h).zfill(2) for h in headers]

    return render_template(
        "index.html", graphdata=graphdata, headers=headers, last_updated=last_updated
    )


@app.route("/lib")
def lib():
    with open(os.path.join(app.root_path, "data", "libdata.json"), "r") as file:
        libdata = json.load(file)

    return render_template("lib.html", data=libdata)


@app.route("/projects")
def projects():
    return render_template("projects.html")


@app.route("/colophon")
def colophon():
    return render_template("colophon.html")


@app.errorhandler(404)
def not_found(e):
    path = request.path.strip("/")

    if "api" in path:
        return "That URL was not found.", 404

    with open(os.path.join(app.root_path, "data", "redirects.json"), "r") as file:
        redirects = json.load(file)

    if path in redirects:
        return redirect(redirects[path], code=308)

    return render_template("404.html", e=e), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template("500.html", e=e), 500


if __name__ == "__main__":
    app.run(port=7000, debug=True)
