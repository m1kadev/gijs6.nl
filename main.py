from flask import Flask, request, redirect, url_for, render_template, jsonify, send_from_directory, Response
import locale
import pickle

locale.setlocale(locale.LC_TIME, "nl_NL")

app = Flask(__name__)


def read_file(filename):
    with open(filename, 'r') as f:
        return f.read().strip()


@app.route("/.well-known/security.txt")
def securitytxt():
    return send_from_directory('static', "security.txt", mimetype="text/plain")

@app.route("/security.txt")
def securitytxtredirect():
    return redirect(url_for('securitytxt')), 301


@app.route("/")
def home():
    lang = request.args.get('lang', 'en')

    with open("homeitems.pkl", "rb") as bestand:
        data = pickle.load(bestand)
    for key in data:
        for item in data[key]:
            item['title'] = {
                'en': item['title'],
                'nl': item.get('title_nl') or item['title']
            }

            item['popupdescript'] = {
                'en': item['popupdescript'],
                'nl': item.get('popupdescript_nl') or item['popupdescript']
            }

    return render_template('home.html', lang=lang, **data)


@app.route("/code")
def code():
    lang = request.args.get('lang', 'en')
    return render_template("code.html", lang=lang)


@app.route("/lib")
def bieb():
    lang = request.args.get('lang', 'en')

    with open("homeitems.pkl", "rb") as bestand:
        data = pickle.load(bestand)
    for key in data:
        for item in data[key]:
            item['title'] = {
                'en': item['title'],
                'nl': item.get('title_nl') or item['title']
            }

            item['popupdescript'] = {
                'en': item['popupdescript'],
                'nl': item.get('popupdescript_nl') or item['popupdescript']
            }

    return render_template("bieb.html", lang=lang, **data)


@app.route("/colophon")
def colofon():
    lang = request.args.get('lang', 'en')
    return render_template("colofon.html", lang=lang)


# SAMENVATTINGEN

@app.route("/school")
def school():
    with open("samenvattingen.pkl", "rb") as bestand:
        data = pickle.load(bestand)
    laatst_bijgewerkt = read_file("laatst_samva_data_bijgewerkt.txt")

    return render_template("school.html", data=data, laatst_bijgewerkt=laatst_bijgewerkt)


# OVERIG

@app.route("/binas")
def binas():
    return send_from_directory("static", "Binas 7e editie.pdf")


@app.route("/klok")
def klok():
    return render_template("klokstuff.html")


# ERRORS

@app.errorhandler(404)
def not_found(e):
    return render_template("404.html", e=e), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html', e=e), 500


if __name__ == '__main__':
    app.run()