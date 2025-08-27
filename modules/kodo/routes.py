from flask import Blueprint, Response, request
import os

kodo_module = Blueprint("kodo_module", __name__)

BASE_DIR = os.path.dirname(__file__)


# This is the API to store the kodo (https://git.dupunkto.org/~dupunkto/kodo) highscore


@kodo_module.route("/get")
def kodo_get():
    with open(os.path.join(BASE_DIR, "highscore.txt"), "r") as f:
        data = f.read().strip()
    resp = Response(data)
    resp.headers["Access-Control-Allow-Origin"] = "*"
    return resp


@kodo_module.route("/new")
def kodo_new():
    new = request.args.get("s")

    with open(os.path.join(BASE_DIR, "highscore.txt"), "r") as f:
        old = f.read().strip()

    try:
        if int(new) > int(old):
            with open(os.path.join(BASE_DIR, "highscore.txt"), "w") as file:
                file.write(new)
            resp = Response("", status=200)
            resp.headers["Access-Control-Allow-Origin"] = "*"
            return resp
        else:
            resp = Response("", status=400)
            resp.headers["Access-Control-Allow-Origin"] = "*"
            return resp
    except Exception:
        resp = Response("", status=400)
        resp.headers["Access-Control-Allow-Origin"] = "*"
        return resp
