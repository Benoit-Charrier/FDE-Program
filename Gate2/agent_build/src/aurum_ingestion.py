"""Aurum CSV ingestion layer with schema-drift detection.

All column names sourced directly from Gate2-Artefacts CSV headers (2026-04-13/14).
Schema version is detected by hashing the header row; a mismatch raises
SchemaChangeAlert before any data is read.

Spec source: D4 §4 T-003, T-004, T-014; scenario_context.md §6 (quarterly schema
changes without notice — confirmed cause of the prior RPA project failure).
"""

import csv
import hashlib
from pathlib import Path
from typing import Any


# Canonical schemas derived from artefact CSV headers. These are facts, not assumptions.
CANONICAL_SCHEMAS: dict[str, list[str]] = {
    "APEX_BILL_DAILY": [
        "INVOICE_NO", "CUSTOMER_ID", "CUSTOMER_NAME", "INVOICE_DT",
        "AMT_NET", "AMT_FUEL_SURCH", "AMT_VAT", "AMT_GROSS", "ROUTE_CODE", "DEPOT",
    ],
    "APEX_DISPUTES_OPEN": [
        "DISPUTE_ID", "INVOICE_NO", "CUSTOMER_ID", "OPEN_DT", "DISPUTE_TYPE",
        "DISPUTE_AMT", "ASSIGNED_TO", "STATUS", "LAST_UPDT",
    ],
    "APEX_CREDITS": [
        "CREDIT_ID", "INVOICE_NO", "CUSTOMER_ID", "CREDIT_AMT", "REASON_CODE",
        "APPROVER_ID", "AUDIT_REF", "APPLIED_DT",
    ],
    "APEX_RECON": [
        "RECON_ID", "INVOICE_NO", "EXPECTED_AMT", "RECEIVED_AMT",
        "VAR", "AGEING_DAYS", "FLAG",
    ],
    # APEX_CUSTOMER_MASTER schema is unknown — not present in Gate2-Artefacts.
    # See Build_loop_analysis.md Q-8. Add here when schema is confirmed.
}


class SchemaChangeAlert(Exception):
    """Raised when the live CSV header does not match the canonical schema.

    On SchemaChangeAlert: halt all agent processing for this file type and
    switch to 100% HITL until the schema is updated and re-validated.
    (D5 §4 Risk R-2; scenario_context.md: prior RPA failure root cause.)
    """


def _header_hash(headers: list[str]) -> str:
    return hashlib.md5(",".join(headers).encode()).hexdigest()


CANONICAL_HASHES: dict[str, str] = {
    name: _header_hash(cols) for name, cols in CANONICAL_SCHEMAS.items()
}


def load_csv(file_type: str, path: Path) -> list[dict[str, Any]]:
    """Load a named Aurum CSV file, validating the header schema first.

    Raises SchemaChangeAlert if the header does not match the canonical schema.
    Raises ValueError for unknown file_type values.
    Returns a list of dicts, one per data row.
    """
    if file_type not in CANONICAL_SCHEMAS:
        raise ValueError(
            f"Unknown Aurum file type: {file_type!r}. "
            f"Known types: {list(CANONICAL_SCHEMAS.keys())}"
        )

    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        actual_headers = list(reader.fieldnames or [])
        actual_hash = _header_hash(actual_headers)

        if actual_hash != CANONICAL_HASHES[file_type]:
            raise SchemaChangeAlert(
                f"{file_type} schema has changed.\n"
                f"  Expected: {CANONICAL_SCHEMAS[file_type]}\n"
                f"  Actual:   {actual_headers}\n"
                "All processing halted. Switch to 100% HITL until schema is updated "
                "and canonical schema in this module is revised."
            )

        return [dict(row) for row in reader]
