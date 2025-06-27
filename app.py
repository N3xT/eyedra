import os
import hashlib

from flask import Flask, render_template, session, request, redirect, url_for, send_file, jsonify, abort
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from utils.monitor import load_monitor_list, build_categories, find_element_by_id, add_element, remove_element
from utils.watcher import start_monitoring
from utils.logger import *
from utils.decorator.auth import *
from utils.common import *
from utils.config import *

from markupsafe import escape

app = Flask(__name__)
app.config["SECRET_KEY"] = secret_key
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=int(session_timeout))
limiter = Limiter(get_remote_address, app=app, default_limits=[limiter_limit])

@app.route("/")
@is_logged_in
def index():
    return render_template("index.html", 
        page="dashboard", 
        username=session["username"]
    )

@app.route("/monitor/")
@is_logged_in
def monitor():
    monitor_list = load_monitor_list()
    categories = build_categories(monitor_list)
    return render_template("monitor.html", page="monitor", username=session["username"], categories=categories)

@app.route("/monitor/<int:id>")
@is_logged_in
def access_event(id):
    monitor_list = load_monitor_list()
    artifact = find_element_by_id(id, monitor_list)

    if artifact == None:
        return render_template("error.html", page="error", username=session.get("username", False), message="An error occured")
    
    logs = logger.parse_logs_by_path(artifact["path"], last_n=False, last_hour=False, sort_by_newest=True)

    if artifact["category"] == "directory":
        if artifact["files"]:
            abort(404)
            
        for log in logs:
            file_name = os.path.basename(log["src_path"])
            log["file_name"] = file_name

            if "dest_path" in log:
                file_name = os.path.basename(log["dest_path"])
                log["new_file_name"] = file_name

    for log in logs:
        log["time_ago"] = time_ago(log["timestamp"])

    return render_template("artifact_monitor.html", page="monitor", username=session["username"], artifact=artifact, logs=logs)

@app.route("/config/", methods=["GET", "POST"])
@is_logged_in
def config():
    if request.method == "GET":
        monitor_list = load_monitor_list()
        categories = build_categories(monitor_list)
        return render_template("config.html", page="config", username=session["username"], categories=categories, message=False)
    else:
        path = request.form.get("path")
        level = request.form.get("level")
        action = request.form.get("action")
        path_type = check_path_type(path)
        monitor_list = load_monitor_list()
        categories = build_categories(monitor_list)
        response = {"type": "error", "message": "Unknown error"}

        if action == "add":
            if not level:
                response["message"] = "Please specify a level"
            elif not path_type:
                response["message"] = f"{path} is invalid. Please try again"
            else:
                success = add_element(path, path_type, level)
                if success:
                    monitor_list = load_monitor_list()
                    categories = build_categories(monitor_list)
                    response = {"type": "success", "message": f"Started monitoring {path}"}
                else:
                    response["message"] = f"{path} is already being monitored"

        elif action == "remove":
            if remove_element(path):
                monitor_list = load_monitor_list()
                categories = build_categories(monitor_list)
                response = {"type": "success", "message": f"Stopped monitoring {path}"}
            else:
                response["message"] = f"{path} is not being monitored"

        return render_template(
            "config.html",
            page="config",
            username=session["username"],
            categories=categories,
            **response
        )

@app.post("/config/import")
@is_logged_in
def import_list():
    path = monitor_file
    file = request.files.get("file")
    response = {"type": "error", "message": "Unknown error"}

    if file and file.filename.endswith(".json"):
        try:
            data = json.load(file)
            if data and validate_monitor_structure(data):
                file.seek(0)
                file.save(path)
                response = {"type": "success", "message": "Successfully imported new monitor file"}
            else:
                response["message"] = "Invalid file format"
        except Exception as e:
            response["message"] = f"An error occured while reading the file"
    else:
        response["message"] = "Invalid file format"

    monitor_list = load_monitor_list()
    categories = build_categories(monitor_list)

    return render_template(
        "config.html",
        page="config",
        username=session["username"],
        categories=categories,
        **response
    )

@app.get("/config/export")
@is_logged_in
def export_list():
    path = monitor_file
    if check_path_type(path) == "file":
        return send_file(path, as_attachment=True)
    else:
        return render_template("error.html", page="error", username=session.get("username", False), message="Opsss..<br>Monitor file was not found")

@app.route("/login/", methods=["GET", "POST"])
@limiter.limit("5 per minute; 50 per hour")
def login():
    if "username" in session and "credentials" in session:
        if session["credentials"] == hashed_credentials:
            return redirect(url_for("monitor"))
    
    next_page = request.args.get("next")

    if request.method == "GET":
        return render_template("login.html", next_page=next_page)
    else:
        username = escape(request.form["username"])
        password = escape(request.form["password"])

        if username == credentials_username and password == credentials_password:
            session["credentials"] = hashed_credentials
            session["username"] = username
            if next_page:
                return redirect(next_page)
            return redirect(url_for("index"))
        else:
            return render_template("login.html", message="Invalid username or password!")
   
@app.route("/logout")
@is_logged_in
def logout():
    session.pop("username", None)
    return redirect(url_for("login"))

@app.route("/logs/<type>", methods=["POST"])
@limiter.exempt
@is_logged_in
def get_logs(type):
    data = request.get_json()
    try:
        logs = False
        if type == "chart":
            last_hour = float(data.get("last_hour", 6))
            logs = logger.parse_chart_activity(last_n=False, last_hour=last_hour, sort_by_newest=False)
        elif type == "recent":
            last_hour = float(data.get("last_hour", 0.5))
            logs = logger.parse_logs(last_n=False, last_hour=last_hour, sort_by_newest=True)
        elif type == "most":
            last_hour = float(data.get("last_hour", 0.5))
            logs = logger.parse_most_active_files(last_n=False, last_hour=last_hour, sort_by_newest=True)
        elif type == "level_activity":
            logs = {}
            last_hour = float(data.get("last_hour", 0.5))
            logs["total"] = len(logger.parse_logs(last_n=False, last_hour=last_hour, sort_by_newest=False))
            logs["critical"] = len(logger.parse_logs_by_level("critical", last_n=False, last_hour=last_hour, sort_by_newest=False))
            logs["high"] = len(logger.parse_logs_by_level("high", last_n=False, last_hour=last_hour, sort_by_newest=False))
            logs["medium"] = len(logger.parse_logs_by_level("medium", last_n=False, last_hour=last_hour, sort_by_newest=False))
            logs["low"] = len(logger.parse_logs_by_level("low", last_n=False, last_hour=last_hour, sort_by_newest=False))
        elif type == "event_activity":
            logs = {}
            last_hour = float(data.get("last_hour", 0.5))
            logs["total"] = len(logger.parse_logs(last_n=False, last_hour=last_hour, sort_by_newest=False))
            logs["modified"] = len(logger.parse_logs_by_event("modified", last_n=False, last_hour=last_hour, sort_by_newest=False))
            logs["created"] = len(logger.parse_logs_by_event("created", last_n=False, last_hour=last_hour, sort_by_newest=False))
            logs["deleted"] = len(logger.parse_logs_by_event("deleted", last_n=False, last_hour=last_hour, sort_by_newest=False))
            logs["renamed"] = len(logger.parse_logs_by_event("renamed", last_n=False, last_hour=last_hour, sort_by_newest=False))
        return jsonify({"logs": logs})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.errorhandler(404)
def not_found(e): 
    return render_template("error.html", page="error", sername=session.get("username", False), message="Page not found"), 404

@app.errorhandler(429)
def ratelimit_handler(e):
    return render_template("error.html", page="error", username=session.get("username", False), message="Slow down..<br>Too many requests"), 429

if __name__ == "__main__":
    monitor_list = load_monitor_list()
    if validate_monitor_structure(monitor_list):
        start_monitoring()
        app.run(debug=True, use_reloader=False)
    else:
        print("Invalid monitor list file!")
