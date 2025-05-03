from flask import session, render_template, request, url_for
from functools import wraps

def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not session.get("logged_in"):

            # So my bookmarks for proli, grade and admin are not just the login fav
            if "proli" in request.path:
                fav = url_for("proli_bp.static", filename="fav.ico")
            elif "grade" in request.path:
                fav = url_for("priv_bp.static", filename="favs/grade.ico") 
            elif "admin" in request.path:
                fav = url_for("admin_bp.static", filename="favs/admin.ico")
            else:
                fav = url_for("static", filename="favs/login.ico")


            next_page = request.args.get("next")
            
            if not next_page:
               next_page = request.url

            return render_template("login.html", fav=fav, next_page=next_page)
        return func(*args, **kwargs)
    return wrapper
