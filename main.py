from flask import Flask, flash, request, redirect, url_for, render_template, send_from_directory
import locale
import pickle
import time

from formdata import opslaan

locale.setlocale(locale.LC_TIME, "nl_NL")

app = Flask(__name__)


@app.route("/.well-known/security.txt")
def securitytxt():
    return send_from_directory('static', "security.txt", mimetype="text/plain")


@app.route("/security.txt")
def securitytxtredirect():
    return redirect(url_for('securitytxt')), 301


@app.route("/contact", methods=["GET", "POST"])
def contact():
    prefillEmpty = {
        "name": "",
        "mail": "",
        "message": ""
    }

    if request.method == "POST":
        lang = request.args.get('lang', 'en')

        name = request.form.get("name", "")
        email = request.form.get("email", "")
        message = request.form.get("message", "")

        if not message:
            if lang == "nl":
                flash("Vul een bericht in", "error")
            else:
                flash("Please enter a message.", "error")
            prefilldata = {
                "name": name,
                "mail": email,
                "message": message
            }
            return render_template("contact.html", lang=lang, prefill=prefilldata)

        status = opslaan({"name": name, "email": email, "message": message, "time": time.time()})

        if not status:
            if lang == "nl":
                flash("Er is een fout opgetreden. Probeer het later opnieuw.", "error")
            else:
                flash("An error has occurred. Please try again later.", "error")

            prefilldata = {
                "name": name,
                "mail": email,
                "message": message
            }
            return render_template("contact.html", lang=lang, prefill=prefilldata)

        if lang == "nl":
            flash("Succesvol verstuurd!", "goed")
        else:
            flash("Sent successfully", "goed")

        return render_template("contact.html", lang=lang, prefill=prefillEmpty)
    else:
        lang = request.args.get('lang', 'en')
        return render_template("contact.html", lang=lang, prefill=prefillEmpty)


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
    with open("laatst_samva_data_bijgewerkt.txt", 'r') as f:
        laatst_bijgewerkt = f.read().strip()

    isErBinnenkort = any(item["Weergave"] == "JA" for item in data)
    isErLater = any(item["Weergave"] == "JA_DEELS" for item in data)
    isErEerder = any(item["Weergave"] == "NEE" for item in data)


    return render_template("samenvattingen.html", data=data, laatst_bijgewerkt=laatst_bijgewerkt, verschil=verschil_format, legenda_tonen=legenda_blokken_en_tekst_tonen, isErBinnenkort=isErBinnenkort, isErLater=isErLater, isErEerder=isErEerder,)


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
