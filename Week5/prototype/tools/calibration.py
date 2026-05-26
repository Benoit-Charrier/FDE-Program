"""
CalibrationRecord startup validation (REQ-A-2, IC-S-16).

In production, the agent queries S-16 (config management system) at
GET DISCOVERY_REQUIRED/calibration-records?call_site=ROUTING&state=SIGNED.
In the prototype S-16 is stubbed as a mock record stored in-module.

The 6-field check is real — if any field fails, startup_validate() raises
CalibrationError, the agent must not start, and no claims may be processed.
"""

from config import CLASSIFIER_VERSION


class CalibrationError(RuntimeError):
    """Raised on any startup calibration failure. Agent must not start."""


# ---------------------------------------------------------------------------
# Mock CalibrationRecord (S-16 stub)
# ---------------------------------------------------------------------------

_MOCK_CALIBRATION_RECORD = {
    "id": "cal-rec-2026-05-001",
    "state": "SIGNED",
    "cmo_signoff_date": "2026-05-01",
    "recall_achieved": 0.997,
    "holdout_set_size": 612,
    "call_site": "ROUTING",
    "classifier_version": CLASSIFIER_VERSION,
    "threshold_value": 0.70,
    "cmo_reviewer_name": "Dr. Marcus Webb",
    "cmo_reviewer_id": "GHS-CMO-001",
}


def _fetch_calibration_record() -> dict:
    """Stub for GET S-16/calibration-records?call_site=ROUTING&state=SIGNED."""
    return _MOCK_CALIBRATION_RECORD


# ---------------------------------------------------------------------------
# 6-field startup validator
# ---------------------------------------------------------------------------

def startup_validate() -> dict:
    """
    Validates the CalibrationRecord at agent startup.
    Returns the record on success.
    Raises CalibrationError (with specific field name) on any failure.
    Agent must call this before processing the first claim.
    """
    record = _fetch_calibration_record()

    if record.get("state") != "SIGNED":
        raise CalibrationError(
            f"CalibrationRecord.state = {record.get('state')!r} — expected SIGNED. "
            "Agent startup aborted."
        )

    if not record.get("cmo_signoff_date"):
        raise CalibrationError(
            "CalibrationRecord.cmo_signoff_date is null — CMO sign-off required. "
            "Agent startup aborted."
        )

    recall = record.get("recall_achieved", 0)
    if recall < 0.995:
        raise CalibrationError(
            f"CalibrationRecord.recall_achieved = {recall} — minimum 0.995 required. "
            "Agent startup aborted."
        )

    holdout = record.get("holdout_set_size", 0)
    if holdout < 500:
        raise CalibrationError(
            f"CalibrationRecord.holdout_set_size = {holdout} — minimum 500 required. "
            "Agent startup aborted."
        )

    if record.get("call_site") != "ROUTING":
        raise CalibrationError(
            f"CalibrationRecord.call_site = {record.get('call_site')!r} — expected ROUTING. "
            "Cross-contamination guard: WS1 must not load a VERIFICATION record. "
            "Agent startup aborted."
        )

    if record.get("classifier_version") != CLASSIFIER_VERSION:
        raise CalibrationError(
            f"CalibrationRecord.classifier_version = {record.get('classifier_version')!r} — "
            f"deployed binary version = {CLASSIFIER_VERSION!r}. Version mismatch. "
            "Agent startup aborted."
        )

    return record
