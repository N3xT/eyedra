
# 🧿 Eyedra

**Eyedra** is a lightweight file activity monitoring web application built with Flask. It lets you track modifications, creations, deletions, and renames of critical files or directories in real-time, complete with severity levels and a clean dashboard—supporting both dark and light mode.

---

## 🚀 Features

- 📂 **Track Files & Directories**
  - Add any file or folder to monitor with a severity level (Low, Medium, High, Critical).
  - Supports system paths like `/etc/passwd` or custom user paths.

- 🔍 **Real-Time Monitoring**
  - Detects and logs file system events: Created, Modified, Deleted, Renamed.
  - Displays recent activity and most active files.

- 📊 **Dashboard**
  - Overview of activity trends.
  - Visual breakdown of event types and severity levels.
  - Activity charts grouped by time.

- 💡 **Light/Dark Mode**
  - Toggle between clean light mode and sleek dark mode.
  - All screens fully support both themes.

- 🛠️ **Configuration Interface**
  - Add/remove files and directories to watch.
  - Assign severity levels on the fly.
  - Import/export watchlists for portability.

- 🔐 **Authentication**
  - Basic login system with session timeout.
  - Credentials stored in `config.ini`.

- 📦 **Docker Support**
  - One-command deployment with Docker.

---

## 🖼️ Screenshots

### ⚫ Dark Mode
![alt text](https://github.com/N3xT/eyedra/blob/main/screenshots/dark_dashboard.png?raw=true)
![alt text](https://github.com/N3xT/eyedra/blob/main/screenshots/config_dark.png?raw=true)
![alt text](https://github.com/N3xT/eyedra/blob/main/screenshots/dark_monitor.png?raw=true)
![alt text](https://github.com/N3xT/eyedra/blob/main/screenshots/dark_monitor_artifact.png?raw=true)


### ⚪ Light Mode
![alt text](https://github.com/N3xT/eyedra/blob/main/screenshots/light_dashboard.png?raw=true)
![alt text](https://github.com/N3xT/eyedra/blob/main/screenshots/config_light.png?raw=true)
![alt text](https://github.com/N3xT/eyedra/blob/main/screenshots/light_monitor.png?raw=true)
![alt text](https://github.com/N3xT/eyedra/blob/main/screenshots/light_monitor_artifact.png?raw=true)

---

## ⚙️ Installation

### 🔧 Requirements
- Python 3.11+
- `pip` for Python dependencies

### 📥 Clone and Run Locally
```bash
git clone https://github.com/N3xT/eyedra.git
cd eyedra
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Access it at: `http://localhost:5000`

---

## 🔐 Configuration

Update `config.ini`:
```ini
[config]
secret_key = <your_random_secret>

[credentials]
username = <your_username>
password = <your_password>

[session]
timeout = 60

[limiter]
limit = 100 per minute

[files]
log = logs/activity_log.jsonl
monitor = utils/monitor_list.json
```

---

## ✍️ Author

Created by [Khaled Alsalmi](http://linkedin.com/in/khaled-alsalmi)
