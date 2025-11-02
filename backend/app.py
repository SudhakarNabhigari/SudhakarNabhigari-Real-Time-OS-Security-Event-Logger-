from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from datetime import datetime
import json
import sys, os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from db import SessionLocal, Event, Alert, init_db

app = Flask(__name__)
CORS(app)
init_db()

# ----------- Simple Rule Engine -----------
def evaluate_rules(event):
    alerts = []
    etype = event.get('event_type')
    details = str(event.get('details', ''))

    # Rule 1: Process executed from /tmp or /var/tmp
    if etype == 'process_exec' and ('/tmp/' in details or '/var/tmp/' in details):
        alerts.append({
            'severity': 'high',
            'message': 'Process executed from temporary directory',
            'meta': details
        })

    # Rule 2: File written under /etc
    if etype == 'file_write' and '/etc/' in details:
        alerts.append({
            'severity': 'high',
            'message': 'File written under /etc directory',
            'meta': details
        })

    # Rule 3: Failed SSH login
    if etype == 'auth' and 'Failed password' in details:
        alerts.append({
            'severity': 'medium',
            'message': 'Failed authentication attempt detected',
            'meta': details
        })

    return alerts


# ----------- Routes -----------

@app.route('/')
def index():
    """Render dashboard with recent events and alerts."""
    db = SessionLocal()
    events = db.query(Event).order_by(Event.timestamp.desc()).limit(50).all()
    alerts = db.query(Alert).order_by(Alert.timestamp.desc()).limit(50).all()
    return render_template('index.html', events=events, alerts=alerts)


# ✅ Route to receive event data from collector
@app.route('/event', methods=['POST'])
def receive_event():
    """Receive events from collector.py"""
    data = request.get_json(force=True)
    db = SessionLocal()

    # Store event
    ev = Event(
        timestamp=datetime.utcnow(),
        host=data.get('host', 'unknown'),
        event_type=data.get('event_type', 'unknown'),
        details=json.dumps(data.get('details'))
    )
    db.add(ev)
    db.commit()

    # Evaluate rules
    rule_alerts = evaluate_rules({
        'event_type': data.get('event_type'),
        'details': data.get('details')
    })

    # Store any generated alerts
    created_alerts = []
    for a in rule_alerts:
        al = Alert(
            severity=a['severity'],
            message=a['message'],
            meta=a['meta']
        )
        db.add(al)
        created_alerts.append(a)
    db.commit()

    return jsonify({'status': 'ok', 'alerts': created_alerts})


# ✅ Route to receive alert data (optional, if collector sends directly)
@app.route('/alert', methods=['POST'])
def receive_alert():
    """Receive pre-generated alerts (optional)"""
    data = request.get_json(force=True)
    db = SessionLocal()

    al = Alert(
        timestamp=datetime.utcnow(),
        severity=data.get('severity', 'low'),
        message=data.get('message', ''),
        meta=json.dumps(data.get('meta', {}))
    )
    db.add(al)
    db.commit()

    return jsonify({'status': 'alert saved'})


# ✅ API route to fetch events
@app.route('/api/events', methods=['GET'])
def get_events():
    db = SessionLocal()
    q = db.query(Event).order_by(Event.timestamp.desc()).limit(200).all()
    out = []
    for e in q:
        out.append({
            'id': e.id,
            'timestamp': e.timestamp.isoformat(),
            'host': e.host,
            'event_type': e.event_type,
            'details': e.details
        })
    return jsonify(out)


# ✅ API route to fetch alerts
@app.route('/api/alerts', methods=['GET'])
def get_alerts():
    db = SessionLocal()
    q = db.query(Alert).order_by(Alert.timestamp.desc()).limit(200).all()
    out = []
    for a in q:
        out.append({
            'id': a.id,
            'timestamp': a.timestamp.isoformat(),
            'severity': a.severity,
            'message': a.message,
            'meta': a.meta
        })
    return jsonify(out)


# ----------- Run Server -----------
if __name__ == '__main__':
    app.run(debug=True)
