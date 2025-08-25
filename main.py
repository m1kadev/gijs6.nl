from flask import (
    Flask,
    redirect,
    render_template,
    send_from_directory,
    url_for,
    request,
    session,
)
from datetime import timedelta, datetime
from werkzeug.security import check_password_hash, generate_password_hash
import json
import locale
import os
import random
import string
import subprocess

# Blueprints
from blueprints import load_blueprints


locale.setlocale(locale.LC_TIME, "nl_NL")

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config["SESSION_PERMANENT"] = True
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=31)

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

try:
    with open(os.path.join(BASE_DIR, "password.txt"), "r") as f:
        PASSWORD_HASH = f.read().strip()
except FileNotFoundError:
    if __name__ == "__main__":
        password = "".join(
            random.choices(
                string.ascii_letters + string.digits, k=random.randint(25, 45)
            )
        )
        # Only in development. If this would be executed on production that would be very very bad...
        print(
            f"\033[91mThere is no password registred. You can use the password '{password}' but since you do not have access to the JSON files needed to load most pages that are locked, it isn't a big deal\033[0m"
        )
        PASSWORD_HASH = generate_password_hash(password)
    else:
        raise FileNotFoundError


# Blueprints

for bp, prefix in load_blueprints():
    try:
        app.register_blueprint(bp, url_prefix=prefix)
    except Exception as e:
        print(f"An error occurred while trying to load {bp} as a blueprint: {e}")

# Files


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


def get_commit_and_deploy_date():
    try:
        with open(os.path.join(BASE_DIR, "data", "last_deploy.txt"), "r") as f:
            latest_deploy_date = f.read().strip()
    except FileNotFoundError:
        latest_deploy_date = "unknown"
        print("No latest deploy date found.")

    latest_commit_hash = (
        subprocess.check_output(
            ["git", "log", "-1", "--pretty=format:%h"], cwd=BASE_DIR
        )
        .strip()
        .decode()
    )
    latest_commit_hash_long = (
        subprocess.check_output(
            ["git", "log", "-1", "--pretty=format:%H"], cwd=BASE_DIR
        )
        .strip()
        .decode()
    )
    latest_commit_timestamp = int(
        subprocess.check_output(
            ["git", "log", "-1", "--pretty=format:%ct"], cwd=BASE_DIR
        ).strip()
    )
    latest_commit_date = datetime.fromtimestamp(latest_commit_timestamp).strftime(
        "%d-%m-%Y at %H:%M:%S"
    )

    comdepdata = {
        "latest_deploy_date": latest_deploy_date,
        "latest_commit_hash": latest_commit_hash,
        "latest_commit_hash_long": latest_commit_hash_long,
        "latest_commit_date": latest_commit_date,
    }

    return comdepdata


comdepdata = get_commit_and_deploy_date()


@app.context_processor
def inject_comdepdata():
    return comdepdata


@app.route("/")
def home():
    try:
        with open(
            os.path.join(BASE_DIR, "data", "homepagegraph", "graphdata.json"), "r"
        ) as file:
            graphdatafull = json.load(file)
    except FileNotFoundError:
        graphdatafull = {"data": [], "last_updated": ""}
        print("No graphdatafull found.")

    graphdata = graphdatafull["data"]
    last_updated = graphdatafull["last_updated"]

    try:
        with open(
            os.path.join(BASE_DIR, "data", "homepagegraph", "headers.json"), "r"
        ) as file:
            headers = json.load(file)
    except FileNotFoundError:
        headers = []
        print("No headers found.")

    headers = [str(h).zfill(2) for h in headers]

    return render_template(
        "home.html", graphdata=graphdata, headers=headers, last_updated=last_updated
    )


@app.route("/login", methods=["GET", "POST"])
def login():
    if not session.get("logged_in"):
        if request.method == "POST":
            password = request.form.get("password")
            if check_password_hash(PASSWORD_HASH, password):
                session["logged_in"] = True
                session.permanent = True

                next_page = request.args.get("next")
                return redirect(next_page)
            else:
                return render_template("login.html", error="Wrong! Lol!")

        return render_template("login.html")
    return redirect("/")


@app.route("/code")
def code():
    return render_template("code.html")


@app.route("/lib")
def lib():
    try:
        with open(os.path.join(BASE_DIR, "data", "libdata.json"), "r") as file:
            libdata = json.load(file)
    except FileNotFoundError:
        libdata = [
            {
                "title": "Lorem Picsum",
                "link": "https://picsum.photos",
                "icon": "fa-solid fa-camera",
            },
            {
                "title": "BiNaS online",
                "link": "https://archive.org/details/BiNaSpdf/mode/1up",
                "icon": "fa-solid fa-flask-vial",
            },
            {
                "title": "Dimensions",
                "link": "https://dimensions.com",
                "icon": "fa-solid fa-up-right-and-down-left-from-center",
            },
        ]

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

    with open(os.path.join(BASE_DIR, "data", "redirects.json"), "r") as file:
        redirects = json.load(file)

    if path in redirects:
        return redirect(redirects[path], code=308)
    return render_template("404.html", e=e), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template("500.html", e=e), 500


if __name__ == "__main__":
    app.run(port=7000, debug=True)
