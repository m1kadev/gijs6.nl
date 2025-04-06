from flask import Blueprint

extra_bp = Blueprint("extra_bp", __name__)

@extra_bp.route("/")
def extra_home():
    return "yeah, things work lol"
