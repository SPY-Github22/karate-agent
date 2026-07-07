import json
import os
from datetime import datetime

DATA_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'sessions.json')

def log_session(session_summary: dict):
    """
    Takes the output of review_session() and stores it in data/sessions.json
    with a timestamp.
    """
    sessions = _load_sessions()
    
    entry = {
        "timestamp": datetime.now().isoformat(),
        "summary": session_summary
    }
    
    sessions.append(entry)
    _save_sessions(sessions)

def get_trend(checkpoint_id: str) -> str:
    """
    Returns a string indicating if the pass rate for a given checkpoint
    improved across stored sessions.
    """
    sessions = _load_sessions()
    if len(sessions) < 2:
        return "Not enough data to calculate trend."
    
    rates = []
    for session in sessions:
        rate = session.get("summary", {}).get("checkpoint_pass_rate", {}).get(checkpoint_id)
        if rate is not None:
            rates.append(rate)
            
    if len(rates) < 2:
        return "Not enough data for this checkpoint."
        
    first_rate = rates[0]
    last_rate = rates[-1]
    
    if last_rate > first_rate:
        return f"Improved (from {first_rate*100:.0f}% to {last_rate*100:.0f}%)"
    elif last_rate < first_rate:
        return f"Declined (from {first_rate*100:.0f}% to {last_rate*100:.0f}%)"
    else:
        return f"Unchanged (steady at {last_rate*100:.0f}%)"

def _load_sessions():
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []

def _save_sessions(sessions):
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, 'w') as f:
        json.dump(sessions, f, indent=2)
