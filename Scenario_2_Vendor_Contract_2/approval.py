from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path
import audit

APPROVALS_FILE = Path("data/approvals.json")


def _load() -> dict:
    if not APPROVALS_FILE.exists():
        return {}
    with open(APPROVALS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def _save(data: dict) -> None:
    APPROVALS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(APPROVALS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def initialise_approval_packet(contract_id: str, redline_families: list[str]) -> None:
    data = _load()
    if contract_id not in data:
        data[contract_id] = {"release_status": "blocked", "clauses": {}}
    for family in redline_families:
        if family not in data[contract_id]["clauses"]:
            data[contract_id]["clauses"][family] = {
                "approved": False,
                "lawyer_name": None,
                "timestamp": None,
            }
    _save(data)
    audit.log_event(contract_id, "approval_packet_initialised", {"families": redline_families})


def record_approval(contract_id: str, clause_family: str, lawyer_name: str) -> str:
    data = _load()
    if contract_id not in data:
        return f"ERROR: contract '{contract_id}' not found in approval records."
    if clause_family not in data[contract_id]["clauses"]:
        return f"ERROR: clause '{clause_family}' is not in the approval packet for '{contract_id}'."

    ts = datetime.now(timezone.utc).isoformat()
    data[contract_id]["clauses"][clause_family] = {
        "approved": True,
        "lawyer_name": lawyer_name,
        "timestamp": ts,
    }

    # Auto-clear if all clauses approved
    all_approved = all(v["approved"] for v in data[contract_id]["clauses"].values())
    if all_approved:
        data[contract_id]["release_status"] = "cleared"

    _save(data)
    audit.log_event(contract_id, "approval_recorded", {
        "clause_family": clause_family,
        "lawyer_name": lawyer_name,
        "timestamp": ts,
        "all_approved": all_approved,
    })

    msg = f"[APPROVED] {clause_family} in {contract_id} — signed off by {lawyer_name} at {ts}"
    if all_approved:
        msg += f"\n[CLEARED] {contract_id} — all clauses approved, package may be released."
    return msg


def check_release(contract_id: str) -> tuple[str, list[str]]:
    data = _load()
    if contract_id not in data:
        return "blocked", [f"Contract '{contract_id}' has no approval record."]

    clauses = data[contract_id].get("clauses", {})
    if not clauses:
        return "cleared", []

    unapproved = [fam for fam, v in clauses.items() if not v["approved"]]
    if unapproved:
        return "blocked", unapproved
    return "cleared", []


def set_release_status(contract_id: str, status: str) -> None:
    data = _load()
    if contract_id in data:
        data[contract_id]["release_status"] = status
        _save(data)
    audit.log_event(contract_id, f"release_{status}", {"release_status": status})


def get_approval_state(contract_id: str) -> dict:
    data = _load()
    return data.get(contract_id, {})


def get_all_approvals() -> dict:
    return _load()
