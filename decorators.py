from flask import session, redirect, url_for, request

def login_required(func):
    def wrapper(*args, **kwargs):
        if not session.get("logged_in"):
            return redirect(url_for("login", next=request.path))
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper
