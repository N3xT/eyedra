import os
from datetime import datetime
from pathlib import Path

def check_path_type(path):
    path = str(Path(path))
    
    if not os.path.exists(path): 
        return False
    return "file" if os.path.isfile(path) else "directory" if os.path.isdir(path) else False


def time_ago(timestamp):
    timestamp = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S,%f")
    now = datetime.now()
    diff = now - timestamp
    seconds = int(diff.total_seconds())

    if seconds < 60:
        return f"{seconds} seconds ago"
    elif seconds < 3600:
        minutes = seconds // 60
        return f"{minutes} minutes ago"
    elif seconds < 86400:
        hours = seconds // 3600
        return f"{hours} hours ago"
    else:
        days = seconds // 86400
        return f"{days} days ago"

def validate_monitor_structure(data):
    if not isinstance(data, list):
        return False
    for item in data:
        if not all(k in item for k in ["id", "path", "category", "files", "level"]):
            return False

        if not isinstance(item["files"], list):
            return False
        else:
            if item["files"]:
                for f in item["files"]:
                    if not all(k in f for k in ["id", "path", "file_name", "category", "level"]):
                        return False

    return True
