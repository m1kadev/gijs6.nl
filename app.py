from flask import (
    Flask,
    redirect,
    render_template,
    send_from_directory,
    url_for,
    request,
    session,
)
from datetime import timedelta, datetime, timezone
from werkzeug.security import check_password_hash, generate_password_hash
import json
import locale
import os
import random
import string
import subprocess

# Modules
from modules import load_modules


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
        raise FileNotFoundError("Password file not found in production environment.")


# Modules

for module_instance, prefix in load_modules():
    try:
        app.register_blueprint(module_instance, url_prefix=prefix)
    except Exception as e:
        print(
            f"An error occurred while trying to load {module_instance} as a module: {e}"
        )


# Filters


@app.template_filter("dt_fmt")
def format_datetime(value, fmt="%Y-%m-%d %H:%M:%S"):
    if not value:
        return ""
    try:
        return datetime.strptime(value, "%Y-%m-%dT%H:%M:%S%z").strftime(fmt)
    except ValueError:
        return value


@app.template_filter("dt_iso")
def isoformat(value, fmt="%Y-%m-%dT%H:%M:%S%z"):
    if not value:
        return None
    return datetime.strptime(value, fmt).isoformat()


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
    return redirect(url_for("securitytxt"), code=301)


@app.route("/robots")
@app.route("/robots.txt")
def robots():
    return send_from_directory("static", "txts/robots.txt", mimetype="text/plain")


def get_commit_and_deploy_date():
    # Set deploy date to current time (when app starts)
    deploy_dt = datetime.now(tz=timezone.utc)
    latest_deploy_date = deploy_dt.strftime("%d-%m-%Y at %H:%M:%S")

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
    latest_commit_dt = datetime.fromtimestamp(latest_commit_timestamp, tz=timezone.utc)
    latest_commit_date = latest_commit_dt.strftime("%d-%m-%Y at %H:%M:%S")

    comdepdata = {
        "latest_deploy_date": latest_deploy_date,
        "latest_deploy_date_iso": deploy_dt.isoformat(),
        "latest_commit_hash": latest_commit_hash,
        "latest_commit_hash_long": latest_commit_hash_long,
        "latest_commit_date": latest_commit_date,
        "latest_commit_date_iso": latest_commit_dt.isoformat(),
    }

    return comdepdata


comdepdata = get_commit_and_deploy_date()


def get_homepage_graph_data():
    # Get homepage graph data from memory. If empty, try loading from disk.
    if not homepage_graph_data["graphdata"]:
        try:
            with open(
                os.path.join(BASE_DIR, "data", "homepagegraph", "graphdata.json"), "r"
            ) as file:
                graphdatafull = json.load(file)
            homepage_graph_data["graphdata"] = graphdatafull["data"]
            homepage_graph_data["last_updated"] = graphdatafull.get("last_updated", "")
            homepage_graph_data["last_updated_iso"] = graphdatafull.get(
                "last_updated_iso", ""
            )
        except FileNotFoundError:
            homepage_graph_data["graphdata"] = []

        try:
            with open(
                os.path.join(BASE_DIR, "data", "homepagegraph", "headers.json"), "r"
            ) as file:
                headers = json.load(file)
            homepage_graph_data["headers"] = [str(h).zfill(2) for h in headers]
        except FileNotFoundError:
            homepage_graph_data["headers"] = []

    return homepage_graph_data


def set_homepage_graph_data(graphdata, headers, last_updated, last_updated_iso):
    homepage_graph_data["graphdata"] = graphdata
    homepage_graph_data["headers"] = [str(h).zfill(2) for h in headers]
    homepage_graph_data["last_updated"] = last_updated
    homepage_graph_data["last_updated_iso"] = last_updated_iso


def get_library_data():
    try:
        with open(os.path.join(BASE_DIR, "data", "libdata.json"), "r") as file:
            loaded_data = json.load(file)
        return loaded_data
    except FileNotFoundError:
        return []


homepage_graph_data = {
    "graphdata": [],
    "headers": [],
    "last_updated": "",
    "last_updated_iso": "",
}

libdata = get_library_data()


# Security headers
@app.after_request
def add_security_headers(response):
    response.headers["Strict-Transport-Security"] = (
        "max-age=31536000; includeSubDomains"
    )

    response.headers["X-Frame-Options"] = "DENY"

    response.headers["X-Content-Type-Options"] = "nosniff"

    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

    response.headers["X-XSS-Protection"] = "1; mode=block"

    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"

    return response


@app.context_processor
def inject_comdepdata():
    return comdepdata


@app.route("/")
def home():
    data = get_homepage_graph_data()

    return render_template(
        "home.html",
        graphdata=data["graphdata"],
        headers=data["headers"],
        last_updated=data["last_updated"],
        last_updated_iso=data["last_updated_iso"],
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


@app.route("/lib")
def lib():
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
