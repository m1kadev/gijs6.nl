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
    with open('/home/gijs3/mysite/homepagegraph/graphdata.json', 'r') as file:
        graphdata = json.load(file)

    with open('/home/gijs3/mysite/homepagegraph/headers.json', 'r') as file:
        headers = json.load(file)


    return render_template("public/home.html", graphdata=graphdata, headers=headers)


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
    max_value = int(max(data.values()))

    def value_to_color(value, theme):
        max_color="#06C749"
        if theme == "light":
            min_color = "#FFFFFF"
        else:
            min_color = "#000000"
        if value and value != 0:
            normalized_value = max(0, min(1, (int(value) - min_value) / (max_value - min_value)))

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

            value = data.get(datetime.strftime(thiscelldate, "%Y-%m-%d"), 0)

            tabledata[weekday][indexweeknumstuff] = {"value": value, "date": thiscelldate.strftime('%d-%m-%Y'), "darkcolor": value_to_color(value, "dark"), "lightcolor": value_to_color(value, "light")}

    return tabledata, headers



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


@app.route("/colophon")
def colofon():
    return render_template("public/colophon.html")





# SAMENVATTINGEN


@app.route("/school")
def school():
    with open("samenvattingen.pkl", "rb") as bestand:
        data = pickle.load(bestand)
    with open("laatst_samva_data_bijgewerkt.txt", 'r') as f:
        laatst_bijgewerkt = f.read().strip()

    isErBinnenkort = any(item["Weergave"] == "JA" for item in data)
    isErLater = any(item["Weergave"] == "JA_DEELS" for item in data)
    isErEerder = any(item["Weergave"] == "NEE" for item in data)


    return render_template("public/samenvattingen.html", data=data, laatst_bijgewerkt=laatst_bijgewerkt, isErBinnenkort=isErBinnenkort, isErLater=isErLater, isErEerder=isErEerder)



@app.route("/school/min")
def school_min():
    with open("samenvattingen.pkl", "rb") as bestand:
        data = pickle.load(bestand)
    return render_template("public/samva_min.html", data=data)




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
