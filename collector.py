import time
import requests
from datetime import datetime

BACKEND_URL = "http://127.0.0.1:5000"  # Make sure this matches your Flask URL

while True:
    data = {
        "timestamp": datetime.utcnow().isoformat(),
        "host": "windows-pc",
        "event_type": "file_create",
        "details": "Created test.log in C:\\temp",
    }
    requests.post(f"{BACKEND_URL}/event", json=data)

    alert = {
        "timestamp": datetime.utcnow().isoformat(),
        "severity": "LOW",
        "message": "Periodic check completed",
        "meta": "No issues found",
    }
    requests.post(f"{BACKEND_URL}/alert", json=alert)

    print("✅ Sent test data to dashboard")
    time.sleep(10)
