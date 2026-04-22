import json
import os
from datetime import datetime, timezone
from pathlib import Path

AUDIT_FILE = Path("data/audit.jsonl")


def log_event(contract_id: str, event_type: str, payload: dict) -> None:
    AUDIT_FILE.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "contract_id": contract_id,
        "event_type": event_type,
        "payload": payload,
    }
    with open(AUDIT_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


def query_by_contract(contract_id: str) -> list[dict]:
    if not AUDIT_FILE.exists():
        return []
    events = []
    with open(AUDIT_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                event = json.loads(line)
                if event.get("contract_id") == contract_id:
                    events.append(event)
            except json.JSONDecodeError:
                continue
    return events


def query_all() -> list[dict]:
    if not AUDIT_FILE.exists():
        return []
    events = []
    with open(AUDIT_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return events
