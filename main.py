from flask import Flask, redirect, render_template, send_from_directory, url_for
from datetime import datetime, date, timedelta
from collections import defaultdict
import json
import locale
import pickle

locale.setlocale(locale.LC_TIME, "nl_NL")

app = Flask(__name__)




# Files

@app.route('/favicon.ico')
@app.route('/favicon')
def favicon():
    return send_from_directory('static', "favs/dice.ico", mimetype='image/vnd.microsoft.icon')

@app.route("/.well-known/security.txt")
def securitytxt():
    return send_from_directory('static', "txts/security.txt", mimetype="text/plain")

@app.route("/security.txt")
def securitytxtredirect():
    return redirect(url_for('securitytxt')), 301


@app.route("/sitemap")
@app.route("/sitemap.xml")
def sitemap():
    return send_from_directory("static", "sitemap.xml", mimetype="application/xml")


@app.route("/robots")
@app.route("/robots.txt")
def robots():
    return send_from_directory("static", "txts/robots.txt", mimetype="text/plain")




# Public site

@app.route("/")
def home():
    with open('graphdata.json', 'r') as file:
        graphdatafull = json.load(file)

    graphdata = graphdatafull["data"]
    last_updated = graphdatafull["last_updated"]

    with open('headers.json', 'r') as file:
        headers = json.load(file)

    return render_template("public/home.html", graphdata=graphdata, headers=headers, last_updated=last_updated)


# This function is used in another script

def homepagegraphdataparser(data):
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
            min_color = "#FFFFFF"
        else:
            min_color = "#000000"
        if value and value != 0:
            value = int(value)
            normalized_value = max(0, min(1, (value - min_value) / (max_value - min_value)))

            min_color_rgb = [int(min_color[i:i+2], 16) for i in (1, 3, 5)]
            max_color_rgb = [int(max_color[i:i+2], 16) for i in (1, 3, 5)]

            interpolated_color = [int(min_color_rgb[i] + (max_color_rgb[i] - min_color_rgb[i]) * normalized_value) for i in range(3)]

            hex_color = '#' + ''.join(f'{x:02X}' for x in interpolated_color)
            return hex_color
        else:
            return min_color

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

            formatted_date = thiscelldate.strftime('%d-%m-%Y')

            if value == 0:
                message = f"No commits on {formatted_date}"
            elif value == 1:
                message = f"1 commit on {formatted_date}\n\n{repo_list_formatted}"
            else:
                message = f"{value} commits on {formatted_date}\n\n{repo_list_formatted}"

            tabledata[weekday][indexweeknumstuff] = {
                "value": value,
                "date": thiscelldate.strftime('%d-%m-%Y'),
                "message": message,
                "darkcolor": value_to_color(value, "dark"),
                "lightcolor": value_to_color(value, "light")
            }


    saved_data = {
        "data": tabledata,
        "last_updated": datetime.now().strftime('%d-%m-%Y %H:%M:%S')
    }
    
    return saved_data, headers



@app.route("/code")
def code():
    return render_template("public/code.html")


lib_data = [
    {
        "title": "Lorem Picsum",
        "link": "https://picsum.photos/",
        "fa_icon_class": "fa-solid fa-camera"
    },
    {
        "title": "BiNaS pdf",
        "link": "/binas",
        "fa_icon_class": "fa-solid fa-file-pdf"
    },
    {
        "title": "BiNaS online",
        "link": "https://archive.org/details/BiNaSpdf/mode/1up",
        "fa_icon_class": "fa-solid fa-flask-vial"
    },
    {
        "title": "Dimensions",
        "link": "https://www.dimensions.com/",
        "fa_icon_class": "fa-solid fa-up-right-and-down-left-from-center"
    },
    {
        "title": "BGJar",
        "link": "https://bgjar.com/",
        "fa_icon_class": "fa-solid fa-file-image"
    },
    {
        "title": "Simpleicons",
        "link": "https://simpleicons.org/",
        "fa_icon_class": "fa-solid fa-icons"
    },
    {
        "title": "FontAwesome to .ico",
        "link": "https://gauger.io/fonticon/",
        "fa_icon_class": "fa-solid fa-icons"
    },
    {
        "title": "Column text editor",
        "link": "https://columneditor.com/",
        "fa_icon_class": "fa-solid fa-table-columns"
    },
    {
        "title": "MetroDreamin'",
        "link": "https://metrodreamin.com/",
        "fa_icon_class": "fa-solid fa-train-subway"
    },
    {
        "title": "Traffic data things",
        "link": "https://wegkenmerken.ndw.nu/verkeersborden",
        "fa_icon_class": "fa-solid fa-route"
    },
    {
        "title": "Train positions",
        "link": "https://treinposities.nl/",
        "fa_icon_class": "fa-solid fa-train"
    },
    {
        "title": "Biocubes",
        "link": "https://biocubes.net/",
        "fa_icon_class": "fa-solid fa-cube"
    },
    {
        "title": "Map of the universe",
        "link": "https://mapoftheuniverse.net/",
        "fa_icon_class": "fa-solid fa-map"
    },
    {
        "title": "Quantum Cloud",
        "link": "https://www.lusas.com/case/civil/gormley.html",
        "fa_icon_class": "fa-solid fa-hexagon-nodes"
    },
    {
        "title": "FlappyFavi",
        "link": "https://mewtru.com/flappyfavi",
        "fa_icon_class": "fa-solid fa-dove"
    }
]

@app.route("/lib")
def lib():
    return render_template("public/lib.html", data=lib_data)


@app.route("/projects")
def projects():
    return render_template("public/projects.html")

@app.route("/colophon")
def colofon():
    return render_template("public/colophon.html")




@app.route("/school")
def school():
    return redirect("https://school.gijs6.nl")


@app.route("/school/min")
def school_min():
    return redirect("https://school.gijs6.nl")




# OVERIG

@app.route("/binas")
def binas():
    return send_from_directory("static", "Binas 7e editie.pdf")


@app.route("/clock")
def clock():
    return render_template("public/clock.html")


# ERRORS

@app.errorhandler(404)
def not_found(e):
    return render_template("404.html", e=e), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html', e=e), 500



if __name__ == '__main__':
    app.run()
