from flask import session, redirect, url_for, request
from functools import wraps

def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not session.get("logged_in"):
            return redirect(url_for("login", next=request.path))
        return func(*args, **kwargs)
    return wrapper
