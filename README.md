# OS Security Event Logger 


**What this repo contains**
- `collector.py` — lightweight local agent that monitors process creations (polling), filesystem events (watchdog), and auth log tailing; it sends JSON events to the backend.
- `backend/` — Flask application with a small SQLite DB, ingestion endpoint, simple rule engine that creates alerts, and a basic web UI.


**Quick start (Linux VM)**
1. Create a Python 3.10+ venv and install requirements:
```bash
python -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt
pip install -r requirements.txt
