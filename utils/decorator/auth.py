import hashlib
from flask import redirect, url_for, session, request
from functools import wraps
from utils.config import credentials_username, credentials_password

sha512_hash = hashlib.sha512()
credentials = credentials_username + credentials_password
sha512_hash.update(credentials.encode("utf-8"))
hashed_credentials = sha512_hash.hexdigest()

def is_logged_in(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "username" not in session or "credentials" not in session:
            return redirect(url_for("login", next=request.url))
        elif "credentials" in session and session["credentials"] != hashed_credentials:
            return redirect(url_for("login", next=request.url))
        return f(*args, **kwargs)
    return decorated_function

