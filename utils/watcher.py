import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
import threading
from pathlib import Path
from datetime import datetime, timedelta
from .monitor import load_monitor_list, find_element_by_path
from .common import check_path_type
from .logger import logger

observer = Observer()

class Handler(FileSystemEventHandler):
    def __init__(self):
        self.last_modified = datetime.now()

    def on_modified(self, event):
        self.handle_event("MODIFIED", event, src_path=event.src_path)

    def on_created(self, event):
        self.handle_event("CREATED", event, src_path=event.src_path)

    def on_deleted(self, event):
        self.handle_event("DELETED", event, src_path=event.src_path)

    def on_moved(self, event):
        event_type = event.event_type
        src_path = os.path.dirname(event.src_path)
        dest_path = os.path.dirname(event.dest_path)
        if src_path == dest_path:
            event_type = "RENAMED"

        self.handle_event(event_type, event, src_path=event.src_path, dest_path=event.dest_path)

    def handle_event(self, event_type, event, **log_message):
        if datetime.now() - self.last_modified < timedelta(seconds=1):
            return
        
        if not event.is_directory:
            parent_dir = os.path.dirname(event.src_path)
            parent = find_element_by_path(parent_dir) or find_element_by_path(event.src_path)

            if parent:
                if parent["files"]:
                    for file in parent["files"]:
                        if file["path"] == event.src_path:
                            logger.log_event(event_type, file["level"], **log_message)
                            self.last_modified = datetime.now()
                            break
                else:
                    logger.log_event(event_type, parent["level"], **log_message)
                    self.last_modified = datetime.now()

def monitor_path(path, recursive=False):
    path = str(Path(path))
    handler = Handler()
    observer.schedule(handler, path=path, recursive=recursive)

def start_monitoring():
    monitor_list = load_monitor_list()
    for element in monitor_list:
        if element["category"] == "directory":
            path = element["path"]
            if path and check_path_type(path) == "directory":
                monitor_path(path)

    observer.start()

    def keep_alive():
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()

    threading.Thread(target=keep_alive, daemon=True).start()