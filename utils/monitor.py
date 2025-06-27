import os
import json
from pathlib import Path
from .config import monitor_file

FILE_PATH = monitor_file

def load_monitor_list():
    try:
        if not os.path.exists(FILE_PATH) or os.path.getsize(FILE_PATH) == 0:
            with open(FILE_PATH, "w") as f:
                json.dump([], f)
            return []
        with open(FILE_PATH, "r") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        return False

monitor_list = load_monitor_list()

def build_categories(monitor_list):
    categories = {}
    def add_element_cat(element):
        category = element["category"]
        if category == "directory" and not element["files"]:
            categories.setdefault(category, []).append(element)
        elif category == "file":
            categories.setdefault(category, []).append(element)

        if category == "directory" and element["files"]:
            for f in element["files"]:
                add_element_cat(f)

    for element in monitor_list:
        add_element_cat(element)
    return categories

def find_element_by_id(id, data=None):
    if data is None:
        data = monitor_list
    for element in data:
        if element["id"] == id:
            return element
        if element.get("category") == "directory" and "files" in element:
            found = find_element_by_id(id, element["files"])
            if found:
                return found
    return None

def find_element_by_path(path, data=None):
    path = str(Path(path))

    if data is None:
        data = monitor_list
    for element in data:
        if element["path"] == path:
            return element
        if element.get("category") == "directory" and "files" in element:
            found = find_element_by_path(path, element["files"])
            if found:
                return found
    return None

def is_path_being_monitored(path):
    path = str(Path(path))

    parent_dir = os.path.dirname(path)
    if find_element_by_path(path) or find_element_by_path(parent_dir):
        return True
    return False

def write_json(data):
    with open(FILE_PATH, "w") as f:
        json.dump(data, f, indent=4)

def add_element(path, category, level):
    from .watcher import monitor_path

    global monitor_list, categories
    path = str(Path(path))
    
    parent_dir = os.path.dirname(path)
    el = find_element_by_path(path)
    if el and is_path_being_monitored(path):
        if el.get("category") == "directory" and el["files"]:
            remove_element(path)
        else:
            return False

    def get_max_id(data):
        max_id = 0
        for el in data:
            max_id = max(max_id, el["id"])
            if el.get("category") == "directory" and "files" in el:
                max_id = max(max_id, get_max_id(el["files"]))
        return max_id

    new_id = get_max_id(monitor_list) + 1
    new_element = {
        "id": new_id,
        "path": path,
        "category": category,
        "files": [],
        "level": level
    }

    if category == "file":
        parent_dir = os.path.dirname(path)
        parent_element = find_element_by_path(parent_dir)
        if not parent_element or not parent_element.get("category") == "directory":
            parent_element = add_element(parent_dir, "directory", "")
            new_id += 1

        new_element = {
            "id": new_id,
            "path": path,
            "file_name": os.path.basename(path),
            "category": category,
            "level": level
        }

        parent_element["files"].append(new_element)
    else:
        monitor_list.append(new_element)
        monitor_path(path)

    write_json(monitor_list)

    monitor_list = load_monitor_list()
    categories = build_categories(monitor_list)
    return find_element_by_path(path)

def remove_element(path):
    global monitor_list, categories
    path = str(Path(path))

    def remove_from_list(path, data):
        new_data = []
        removed = False
        for el in data:
            if el["path"] == path:
                removed = True
                continue

            if el.get("category") == "directory" and "files" in el:
                files_removed = False
                el["files"], files_removed = remove_from_list(path, el["files"])
                if files_removed:
                    removed = True
            new_data.append(el)
        return new_data, removed

    monitor_list, removed = remove_from_list(path, monitor_list)

    if not removed:
        return False
    
    parent_dir = os.path.dirname(path)
    parent = find_element_by_path(parent_dir)
    if parent and "files" in parent and len(parent["files"]) == 0:
        monitor_list, removed = remove_from_list(parent_dir, monitor_list)

    write_json(monitor_list)

    monitor_list = load_monitor_list()
    categories = build_categories(monitor_list)
    return True