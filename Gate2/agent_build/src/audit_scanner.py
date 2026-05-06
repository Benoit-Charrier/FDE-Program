"""FM-3 / FM-5: Daily APEX_CREDITS compliance audit scanner.

Scans the daily APEX_CREDITS batch export for four violation types:

  NULL_APPROVER_ID     — APPROVER_ID is empty; credit has no named approver (FM-3)
  SYSTEM_APPROVER_ID   — APPROVER_ID matches a system-placeholder pattern, indicating
                         the approval gate was bypassed (FM-5: BDRA-SYSTEM-* or AUTO-*)
  MISSING_AUDIT_REF    — AUDIT_REF is empty; credit cannot be traced to a CRM case (FM-3)
  UNKNOWN_REASON_CODE  — REASON_CODE is not in the confirmed taxonomy

This scanner implements the daily compliance check referenced in:
  D4 §3 KPI (audit trail compliance rate — 100% target within 30 days)
  D4 §7 FM-3 (audit evidence incompleteness detection)
  D4 §7 FM-5 (approval gate bypass detection — detection latency ≤24 hours)

REASON_CODE taxonomy:
Sourced from APEX_CREDITS artefact (Gate2-Artefacts/APEX_CREDITS_20260414.csv).
Values confirmed: FUEL_RECALC, GOODWILL, INV_CORR.
Assumption: this is the complete set. If the credit policy (D4 A-6) introduces
additional codes, KNOWN_REASON_CODES must be updated. See Build_loop_analysis.md Q-7.

Spec source: D4 §3 KPI; D4 §7 FM-3, FM-5.
"""

import re
from dataclasses import dataclass, field
from typing import Sequence


# Derived from APEX_CREDITS artefact. Assumption: complete set (Build_loop_analysis.md Q-7).
KNOWN_REASON_CODES: frozenset[str] = frozenset({"FUEL_RECALC", "GOODWILL", "INV_CORR"})

# System-placeholder pattern for FM-5 detection (D4 §7 FM-5; D4 §5 enforcement note).
SYSTEM_ID_PATTERN = re.compile(r"^(BDRA-SYSTEM-|AUTO-)", re.IGNORECASE)


@dataclass
class AuditViolation:
    credit_id: str
    violation_type: str   # NULL_APPROVER_ID | SYSTEM_APPROVER_ID | MISSING_AUDIT_REF | UNKNOWN_REASON_CODE
    field_value: str
    description: str


@dataclass
class AuditScanResult:
    total_records: int
    violations: list[AuditViolation] = field(default_factory=list)

    @property
    def compliance_rate(self) -> float:
        if self.total_records == 0:
            return 1.0
        violating_ids = {v.credit_id for v in self.violations}
        return (self.total_records - len(violating_ids)) / self.total_records


def scan_credits(records: Sequence[dict]) -> AuditScanResult:
    """Scan a sequence of APEX_CREDITS dicts for compliance violations.

    Each dict must contain keys: CREDIT_ID, APPROVER_ID, AUDIT_REF, REASON_CODE.
    Missing keys are treated as empty values (violation).

    Returns AuditScanResult with all violations found and a compliance rate.
    compliance_rate = (records with no violations) / total_records.
    """
    violations: list[AuditViolation] = []

    for record in records:
        credit_id = record.get("CREDIT_ID", "UNKNOWN")
        approver_id = record.get("APPROVER_ID", "") or ""
        audit_ref = record.get("AUDIT_REF", "") or ""
        reason_code = record.get("REASON_CODE", "") or ""

        if not approver_id:
            violations.append(AuditViolation(
                credit_id=credit_id,
                violation_type="NULL_APPROVER_ID",
                field_value="",
                description="APPROVER_ID is null or empty — credit record has no named approver. "
                            "This is the compliance gap confirmed in Artefact 2 (Sandra's £170 credit).",
            ))
        elif SYSTEM_ID_PATTERN.match(approver_id):
            violations.append(AuditViolation(
                credit_id=credit_id,
                violation_type="SYSTEM_APPROVER_ID",
                field_value=approver_id,
                description=f"APPROVER_ID '{approver_id}' matches a system-placeholder pattern. "
                            "FM-5: approval gate bypass detected. Alert COO and operations lead immediately.",
            ))

        if not audit_ref:
            violations.append(AuditViolation(
                credit_id=credit_id,
                violation_type="MISSING_AUDIT_REF",
                field_value="",
                description="AUDIT_REF is null or empty — credit record cannot be traced to a CRM case. "
                            "FM-3: audit evidence incomplete.",
            ))

        if reason_code not in KNOWN_REASON_CODES:
            violations.append(AuditViolation(
                credit_id=credit_id,
                violation_type="UNKNOWN_REASON_CODE",
                field_value=reason_code,
                description=f"REASON_CODE '{reason_code}' is not in the confirmed taxonomy "
                            f"{set(KNOWN_REASON_CODES)}. If the credit policy introduces new codes, "
                            "update KNOWN_REASON_CODES in this module.",
            ))

    return AuditScanResult(total_records=len(records), violations=violations)
