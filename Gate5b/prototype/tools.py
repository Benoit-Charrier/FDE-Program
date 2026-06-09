"""Data loading tool functions for LACRA prototype.

Each function maps to a data source defined in spec Section 7.
Returns None (not raises) when a file is absent — graceful degradation per spec Section 6.
"""
from pathlib import Path
import json
import csv
import glob
import re

MOCK_DATA = Path(__file__).parent.parent / "mock-data"


def read_kyc(customer_id: str) -> dict | None:
    path = MOCK_DATA / "kyc-profiles" / f"{customer_id}_kyc.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def read_transactions(customer_id: str) -> list[dict] | None:
    path = MOCK_DATA / "transaction-history" / f"{customer_id}_90day.csv"
    if not path.exists():
        return None
    rows = []
    with path.open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            rows.append(dict(row))
    return rows if rows else None


def read_watchlist(customer_id: str) -> str | None:
    matches = glob.glob(str(MOCK_DATA / "watchlist-screenings" / f"{customer_id}_*"))
    if not matches:
        return None
    return Path(matches[0]).read_text(encoding="utf-8")


def read_network(customer_id: str) -> dict | None:
    path = MOCK_DATA / "counterparty-network" / f"{customer_id}_linked_network.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def read_rfi_history(customer_id: str) -> str | None:
    matches = glob.glob(str(MOCK_DATA / "customer-rfi-emails" / f"{customer_id}_*"))
    if not matches:
        return None
    return "\n\n---\n\n".join(Path(m).read_text(encoding="utf-8") for m in sorted(matches))


def read_sanctions_extract(sdn_entry_name: str) -> str | None:
    """sdn_entry_name may be in screening-report format ('KHAN, Muhammad') or
    file-name format ('KHAN_Muhammad'). Both are normalised to the file-name format."""
    normalized = sdn_entry_name.replace(", ", "_").replace(" ", "_")
    path = MOCK_DATA / "sanctions-list-extracts" / f"OFAC_SDN_{normalized}.txt"
    if not path.exists():
        return None
    return path.read_text(encoding="utf-8")


def parse_sdn_name_from_screening(screening_text: str) -> str | None:
    """Extract the SDN entry name from a watchlist screening report.
    Looks for lines like: SDN List Entry: "KHAN, Muhammad"
    Returns the raw name string; read_sanctions_extract handles normalisation."""
    match = re.search(r'SDN List Entry:\s*"([^"]+)"', screening_text)
    return match.group(1) if match else None
