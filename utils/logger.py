import os
import json
from datetime import datetime, timedelta
from collections import defaultdict
from .common import check_path_type
from .config import log_file

LOG_PATH = log_file

class FileLogger:
    def log_event(self, event_type, level, **paths):
        id = 1
        last_row = self.parse_logs(last_n=1, last_hour=False, sort_by_newest=True)

        if last_row and "id" in last_row[0]:
            id = int(last_row[0]["id"]) + 1
        
        log_entry = {
            "id": id,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S,%f")[:-3],
            "event": event_type.upper(),
            "level": level.upper()
        }

        if paths:
            log_entry.update(paths)

        os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry) + "\n")

    def parse_logs(self, last_n=False, last_hour=False, sort_by_newest=False):
        log_entries = []

        if check_path_type(LOG_PATH) == "file":
            with open(LOG_PATH, "r", encoding="utf-8") as file:
                if last_n:
                    from collections import deque
                    lines = deque(file, maxlen=last_n)
                else:
                    lines = file

                for line in lines:
                    log_entry = json.loads(line.strip())

                    if last_hour:
                        entry_time = datetime.strptime(log_entry["timestamp"], "%Y-%m-%d %H:%M:%S,%f")
                        cutoff = datetime.now() - timedelta(hours=last_hour)
                        if entry_time < cutoff:
                            continue

                    log_entries.append(log_entry)

                if sort_by_newest:
                    log_entries.sort(key=lambda x: datetime.strptime(x["timestamp"], "%Y-%m-%d %H:%M:%S,%f"), reverse=True)

        return log_entries

    
    def parse_logs_by_path(self, path, **args):
        log_entries = []
        
        dir = check_path_type(path) == "directory"
        for entry in logger.parse_logs(**args):
            if "src_path" in entry:
                entry_path = entry["src_path"]
                if (dir and entry_path.startswith(path)) or entry_path == path:
                    log_entries.append(entry)

        return log_entries
    
    def parse_logs_by_level(self, level, **args):
        log_entries = []

        for entry in logger.parse_logs(**args):
            if "level" in entry and entry["level"].lower() == level.lower():
                log_entries.append(entry)

        return log_entries
    
    def parse_logs_by_event(self, event, **args):
        log_entries = []

        for entry in logger.parse_logs(**args):
            if "event" in entry and entry["event"].lower() == event.lower():
                log_entries.append(entry)

        return log_entries

    def parse_most_active_files(self, **args):
        file_activity = defaultdict(int)

        for entry in self.parse_logs(**args):
            src_path = entry.get("src_path")
            
            if src_path:
                file_activity[src_path] += 1

        most_active_files = [{"src_path": path, "count": count} for path, count in sorted(file_activity.items(), key=lambda x: x[1], reverse=True)]

        return most_active_files

    def parse_chart_activity(self, **args):
        activity_data = []
        chart_data = self.parse_logs(**args)

        for log in chart_data:
            dt_obj = datetime.strptime(log["timestamp"], "%Y-%m-%d %H:%M:%S,%f")
            dt_obj = dt_obj.replace(minute=0, second=0, microsecond=0)        
            time = dt_obj.strftime("%Y-%m-%dT%H:%M:%S")

            found = False
            for entry in activity_data:
                if entry["time"] == time:
                    entry["count"] += 1
                    found = True
                    break
            
            if not found:
                activity_data.append({"time": time, "count": 1})

        return activity_data
    
logger = FileLogger()
