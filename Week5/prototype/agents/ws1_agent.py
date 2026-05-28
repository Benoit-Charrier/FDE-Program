"""
WS1 Administrative Adjudication Agent — core claim pipeline.

Improvements over initial prototype (build loop pass 1):
- ClaimContext: explicit state machine with optimistic-locking transitions
- FM-A-5 hard stop: T-09 pre-condition check fires ET-07 if state != ADMIN_CLEARED;
  no external calls are made before the check passes
- CalibrationRecord 6-field startup validation runs once at module import;
  process_claim() raises if called on an agent that failed startup
- Audit-first ordering: AuditLogEntry reaches COMMITTED before state PATCH is issued;
  payment step aborts and fires ET-07 if audit write fails
- from_state carried on every state transition (409 Conflict detection)
"""

import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

from config import CLINICAL_CONTENT_CONFIDENCE_THRESHOLD
from tools.calibration import CalibrationError, startup_validate
from tools.eligibility import check_eligibility
from tools.code_validity import check_code_validity
from tools.prior_auth import check_prior_auth
from tools.clinical_classifier import classify_clinical_content
from tools.fee_schedule import get_payment_amount

_ESCALATIONS_DIR = os.path.join(os.path.dirname(__file__), "..", "escalations")

# ---------------------------------------------------------------------------
# Startup validation — runs once when the module is first imported.
# If CalibrationRecord is invalid, _CALIBRATION_RECORD is None and
# process_claim() refuses to run.
# ---------------------------------------------------------------------------

_CALIBRATION_RECORD: Optional[dict] = None
_STARTUP_ERROR: Optional[str] = None

try:
    _CALIBRATION_RECORD = startup_validate()
except CalibrationError as _err:
    _STARTUP_ERROR = str(_err)


# ---------------------------------------------------------------------------
# ClaimContext — state machine wrapper with optimistic locking
# ---------------------------------------------------------------------------

class ConflictError(RuntimeError):
    """409 Conflict: state transition attempted from unexpected state."""


@dataclass
class AuditEntry:
    action: str
    delegation_tier: str
    input_summary: dict
    output_summary: dict
    status: str = "PENDING_WRITE"
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def commit(self) -> None:
        """
        Simulate writing to S-10 and waiting for COMMITTED confirmation.
        In production: POST to DISCOVERY_REQUIRED/audit-log-entries, poll for status=COMMITTED.
        In prototype: sets status directly (synchronous stub).
        """
        self.status = "COMMITTED"

    @property
    def committed(self) -> bool:
        return self.status == "COMMITTED"


@dataclass
class ClaimContext:
    data: dict
    state: str = "NORMALISED"
    audit_entries: list = field(default_factory=list)
    payment_amount: Optional[float] = None

    def transition(self, to_state: str, *, from_state: str) -> None:
        """
        State transition with optimistic locking.
        Raises ConflictError (409) if current state != from_state.
        Represents the S-07 state PATCH with from_state guard.
        """
        if self.state != from_state:
            raise ConflictError(
                f"409 Conflict: attempted {from_state} → {to_state} "
                f"but current state is {self.state!r}"
            )
        self.state = to_state

    def write_audit(self, action: str, delegation_tier: str,
                    input_summary: dict, output_summary: dict) -> AuditEntry:
        """
        Audit-first pattern: creates entry, commits it, appends to log.
        Returns the committed entry. Caller must check entry.committed before
        issuing any state transition PATCH.
        """
        entry = AuditEntry(
            action=action,
            delegation_tier=delegation_tier,
            input_summary=input_summary,
            output_summary=output_summary,
        )
        entry.commit()  # write to S-10 stub; status → COMMITTED
        self.audit_entries.append(entry)
        return entry

    @property
    def audit_trail(self) -> list:
        return [
            f"{e.action.lower()} [{e.status}]" for e in self.audit_entries
        ]


# ---------------------------------------------------------------------------
# Escalation helpers
# ---------------------------------------------------------------------------

def _save_escalation(escalation: dict) -> None:
    os.makedirs(_ESCALATIONS_DIR, exist_ok=True)
    path = os.path.join(_ESCALATIONS_DIR, f"{escalation['claim_id']}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(escalation, f, indent=2)


def _fire_et07(ctx: ClaimContext, signal_values: dict,
               trigger_type: str = "AUDIT_FAILURE",
               preserve_state: bool = False) -> dict:
    """
    ET-07 escalation.

    trigger_type = "AUDIT_FAILURE" (default): audit write failure — state → PENDING_HITL_EXCEPTION.
    trigger_type = "GOVERNANCE_VIOLATION": T-08/T-09 invoked with wrong state — state is NOT
    changed; the incoming state is the diagnostic signal and must be preserved.
    """
    if preserve_state:
        state_at_escalation = ctx.state  # leave state unchanged per REQ-A-6(c)
    else:
        ctx.state = "PENDING_HITL_EXCEPTION"
        state_at_escalation = "PENDING_HITL_EXCEPTION"

    escalation = {
        "claim_id": ctx.data["claim_id"],
        "status": "escalated",
        "escalation_trigger_id": "ET-07",
        "trigger_type": trigger_type,
        "routing_queue": "EXCEPTION_PROCESSOR",
        "required_resolution": (
            "Governance violation: [INVESTIGATE_STATE_MACHINE / REJECT_CLAIM / ESCALATE_TO_COMPLIANCE]"
            if trigger_type == "GOVERNANCE_VIOLATION"
            else "Audit failure: [RECONSTRUCT_AND_CONTINUE / REJECT_CLAIM / ESCALATE_TO_COMPLIANCE]"
        ),
        "trigger_signal_values": signal_values,
        "claim_context": {
            "procedure_code": ctx.data["procedure_codes"][0],
            "diagnosis_code": ctx.data["diagnosis_codes"][0],
            "provider_specialty": ctx.data["provider_specialty"],
        },
        "audit_trail": ctx.audit_trail,
        "claim_state_at_escalation": state_at_escalation,
    }
    _save_escalation(escalation)
    return escalation


def _build_escalation_reason(result: dict) -> str:
    classification = result["classification"]
    confidence = result["confidence"]
    reasoning = result["reasoning"]
    threshold = CLINICAL_CONTENT_CONFIDENCE_THRESHOLD

    if classification == "uncertain":
        return (
            f"Clinical content classifier returned uncertain — contradictory signals: "
            f"{reasoning} Cannot confirm administrative path."
        )
    if classification == "clinical":
        return (
            f"Clinical content classifier returned clinical — {reasoning} "
            f"Physician review required."
        )
    return (
        f"Clinical content classifier returned confidence {confidence:.2f} — "
        f"below threshold {threshold}. {reasoning} "
        f"Cannot confirm administrative path without physician review."
    )


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------

def process_claim(claim: dict) -> dict:
    """
    Runs a ClaimRecord through the WS1 pipeline.

    Raises RuntimeError if called on an agent whose startup validation failed —
    no claims may be processed without a valid signed CalibrationRecord.
    """
    if _STARTUP_ERROR:
        raise RuntimeError(
            f"Agent startup failed — CalibrationRecord invalid. "
            f"No claims may be processed. Error: {_STARTUP_ERROR}"
        )

    ctx = ClaimContext(data=claim)

    # --- T-01: Intake → ADMIN_VALIDATING -----------------------------------
    ctx.transition("ADMIN_VALIDATING", from_state="NORMALISED")

    audit = ctx.write_audit(
        action="CLAIM_INTAKE_VALIDATED",
        delegation_tier="AGENT_ALONE",
        input_summary={"claim_id": claim["claim_id"], "pre_action_state": "NORMALISED"},
        output_summary={"new_state": "ADMIN_VALIDATING"},
    )
    if not audit.committed:
        return _fire_et07(ctx, {"error": "AUDIT_WRITE_FAILED", "pipeline_step": "T-01"})

    # --- T-02/T-03: Eligibility --------------------------------------------
    eligibility = check_eligibility(claim)
    if eligibility["status"] == "discrepancy":
        ctx.state = "PENDING_HITL_EXCEPTION"
        escalation = {
            "claim_id": claim["claim_id"],
            "status": "escalated",
            "escalation_trigger_id": "ET-03",
            "trigger_type": "ELIGIBILITY_DISCREPANCY",
            "routing_queue": "EXCEPTION_PROCESSOR",
            "required_resolution": "Eligibility: [CONFIRM_ELIGIBLE / CONFIRM_INELIGIBLE / RETURN_TO_SUBMITTER]",
            "escalation_reason": (
                f"Eligibility check failed — "
                f"{eligibility.get('eligibility_status', 'UNKNOWN')} for member "
                f"{claim['member_id']}."
            ),
            "trigger_signal_values": {
                "eligibility_status": eligibility.get("eligibility_status", "UNKNOWN"),
                "member_id": claim["member_id"],
                "payer_id": claim.get("payer_id", "UNKNOWN"),
            },
            "claim_context": {
                "procedure_code": claim["procedure_codes"][0],
                "diagnosis_code": claim["diagnosis_codes"][0],
                "provider_specialty": claim["provider_specialty"],
            },
            "audit_trail": ctx.audit_trail,
        }
        _save_escalation(escalation)
        return escalation

    ctx.write_audit(
        action="ELIGIBILITY_CONFIRMED",
        delegation_tier="AGENT_ALONE",
        input_summary={"member_id": claim["member_id"], "payer_id": claim.get("payer_id", "UNKNOWN")},
        output_summary={"eligibility_result": "CONFIRMED"},
    )

    # --- T-04/T-05: Code validity ------------------------------------------
    codes = check_code_validity(claim)
    ctx.write_audit(
        action="CODE_VALIDITY_CHECKED",
        delegation_tier="AGENT_ALONE",
        input_summary={"procedure_codes": claim["procedure_codes"],
                       "diagnosis_codes": claim["diagnosis_codes"]},
        output_summary={"validity_result": codes["status"]},
    )

    # --- T-06/T-07: Prior auth --------------------------------------------
    prior_auth = check_prior_auth(claim)
    ctx.write_audit(
        action="PRIOR_AUTH_CONFIRMED",
        delegation_tier="AGENT_ALONE",
        input_summary={"procedure_codes": claim["procedure_codes"],
                       "member_id": claim["member_id"]},
        output_summary={"prior_auth_status": prior_auth["prior_auth_status"]},
    )

    # --- T-08: Clinical routing → ROUTING → ADMIN_CLEARED or PENDING_PHYSICIAN_REVIEW --
    ctx.transition("ROUTING", from_state="ADMIN_VALIDATING")

    result = classify_clinical_content(claim)
    classification = result["classification"]
    confidence = result["confidence"]

    ctx.write_audit(
        action="CLINICAL_CLASSIFICATION_COMPLETED",
        delegation_tier="AGENT_ALONE" if (
            classification == "admin" and confidence >= CLINICAL_CONTENT_CONFIDENCE_THRESHOLD
        ) else "HUMAN_DECIDES",
        input_summary={
            "diagnosis_codes": claim["diagnosis_codes"],
            "procedure_codes": claim["procedure_codes"],
            "provider_specialty": claim["provider_specialty"],
            "threshold_applied": CLINICAL_CONTENT_CONFIDENCE_THRESHOLD,
            "calibration_record_id": _CALIBRATION_RECORD["id"],
        },
        output_summary={
            "classification": classification,
            "confidence_score": confidence,
            "threshold_met": classification == "admin" and confidence >= CLINICAL_CONTENT_CONFIDENCE_THRESHOLD,
        },
    )

    approved_routing = (
        classification == "admin"
        and confidence >= CLINICAL_CONTENT_CONFIDENCE_THRESHOLD
    )

    if not approved_routing:
        trigger = "ET-01" if classification in ("clinical", "uncertain") else "ET-02"
        ctx.transition("PENDING_PHYSICIAN_REVIEW", from_state="ROUTING")
        escalation = {
            "claim_id": claim["claim_id"],
            "status": "escalated",
            "escalation_trigger_id": trigger,
            "trigger_type": "CLINICAL_ROUTING",
            "routing_queue": "PHYSICIAN_HITL",
            "required_resolution": "Route as: [CLINICAL_CONFIRMED / ADMIN_CONFIRMED / NEEDS_ADDITIONAL_INFO]",
            "classification": classification,
            "confidence": round(confidence, 2),
            "escalation_reason": _build_escalation_reason(result),
            "claim_context": {
                "procedure_code": claim["procedure_codes"][0],
                "diagnosis_code": claim["diagnosis_codes"][0],
                "provider_specialty": claim["provider_specialty"],
            },
            "audit_trail": ctx.audit_trail,
            "original_claim": claim,
        }
        if trigger == "ET-02":
            escalation["borderline_confidence_flag"] = True
            escalation["threshold_applied"] = CLINICAL_CONTENT_CONFIDENCE_THRESHOLD
        _save_escalation(escalation)
        return escalation

    ctx.transition("ADMIN_CLEARED", from_state="ROUTING")

    # --- T-09: Payment calculation — FM-A-5 hard stop ---------------------
    #
    # PRE-CONDITION CHECK: first operation, before any external call.
    # If ClaimRecord.state != ADMIN_CLEARED, abort immediately and fire ET-07.
    # This is REQ-A-6 enforcement. The check is redundant here (we just
    # transitioned to ADMIN_CLEARED) but must be present as an explicit guard
    # because in production T-09 can be invoked independently of the routing step.
    #
    if ctx.state != "ADMIN_CLEARED":
        return _fire_et07(
            ctx,
            signal_values={
                "error": "GOVERNANCE_HARD_STOP_T09",
                "actual_state": ctx.state,
                "expected_state": "ADMIN_CLEARED",
                "claim_id": claim["claim_id"],
            },
            trigger_type="GOVERNANCE_VIOLATION",
            preserve_state=True,
        )

    ctx.transition("PAYMENT_CALCULATING", from_state="ADMIN_CLEARED")
    payment = get_payment_amount(claim)

    # Audit-first: write PAYMENT_APPROVED entry, confirm COMMITTED,
    # then — and only then — issue the APPROVED state PATCH (S-07).
    audit = ctx.write_audit(
        action="PAYMENT_APPROVED",
        delegation_tier="AGENT_LOGS",
        input_summary={
            "claim_id": claim["claim_id"],
            "pre_action_state": "PAYMENT_CALCULATING",
            "procedure_codes": claim["procedure_codes"],
            "payer_id": claim.get("payer_id", "UNKNOWN"),
        },
        output_summary={
            "payment_amount": payment,
            "new_state": "APPROVED",
        },
    )

    if not audit.committed:
        # Audit write failed — ET-07 fires; payment_amount is NOT written;
        # claim stays in PAYMENT_CALCULATING (not advanced to APPROVED).
        return _fire_et07(ctx, {
            "error": "AUDIT_WRITE_FAILED_BEFORE_PAYMENT_PATCH",
            "pipeline_step": "T-09",
            "claim_id": claim["claim_id"],
        })

    # Audit confirmed COMMITTED — now issue the state PATCH (S-07).
    ctx.transition("APPROVED", from_state="PAYMENT_CALCULATING")
    ctx.payment_amount = payment

    return {
        "claim_id": claim["claim_id"],
        "status": "approved",
        "payment_amount": payment,
        "classification": classification,
        "confidence": round(confidence, 2),
        "calibration_record_id": _CALIBRATION_RECORD["id"],
        "audit_trail": ctx.audit_trail,
    }


def process_physician_approved_claim(
    claim: dict,
    physician_id: str = "DR-REVIEWER-001",
    prior_audit_trail: list = None,
) -> dict:
    """
    Entry point for ADMIN_CONFIRMED physician determinations (GAP-15).

    Implements D4a §10: PHYSICIAN_REVIEWING -> ADMIN_CLEARED (authorized_by:
    PHYSICIAN_DETERMINATION) -> PAYMENT_CALCULATING -> APPROVED.

    Called by the HITL reviewer after physician records ADMIN_CONFIRMED.
    Eligibility, code validity, prior auth, and classification are already
    committed — this function restores those audit entries and runs T-09 only.
    """
    if _STARTUP_ERROR:
        raise RuntimeError(
            f"Agent startup failed — CalibrationRecord invalid. "
            f"Error: {_STARTUP_ERROR}"
        )

    ctx = ClaimContext(data=claim)

    # Restore prior committed audit entries from the escalation record.
    if prior_audit_trail:
        for entry_str in prior_audit_trail:
            action_part = entry_str.split(" [")[0].upper().replace(" ", "_")
            restored = AuditEntry(
                action=action_part,
                delegation_tier="AGENT_ALONE",
                input_summary={},
                output_summary={"restored_from": "escalation_record"},
            )
            restored.status = "COMMITTED"
            ctx.audit_entries.append(restored)

    ctx.state = "PENDING_PHYSICIAN_REVIEW"

    # Physician determination audit entry — HUMAN_DECIDES delegation tier.
    audit = ctx.write_audit(
        action="PHYSICIAN_ADMIN_CONFIRMED",
        delegation_tier="HUMAN_DECIDES",
        input_summary={
            "claim_id": claim["claim_id"],
            "authorized_by": physician_id,
            "determination": "ADMIN_CONFIRMED",
        },
        output_summary={
            "new_state": "ADMIN_CLEARED",
            "authorized_by": "PHYSICIAN_DETERMINATION",
        },
    )
    if not audit.committed:
        return _fire_et07(ctx, {
            "error": "AUDIT_WRITE_FAILED",
            "pipeline_step": "PHYSICIAN_DETERMINATION",
            "claim_id": claim["claim_id"],
        })

    # PENDING_PHYSICIAN_REVIEW -> ADMIN_CLEARED (physician-authorized, GAP-15).
    ctx.transition("ADMIN_CLEARED", from_state="PENDING_PHYSICIAN_REVIEW")

    # --- T-09: Payment calculation — FM-A-5 hard stop ----------------------
    if ctx.state != "ADMIN_CLEARED":
        return _fire_et07(
            ctx,
            signal_values={
                "error": "GOVERNANCE_HARD_STOP_T09",
                "actual_state": ctx.state,
                "expected_state": "ADMIN_CLEARED",
                "claim_id": claim["claim_id"],
            },
            trigger_type="GOVERNANCE_VIOLATION",
            preserve_state=True,
        )

    ctx.transition("PAYMENT_CALCULATING", from_state="ADMIN_CLEARED")
    payment = get_payment_amount(claim)

    # Audit-first ordering — same invariant as the classifier-cleared path.
    audit = ctx.write_audit(
        action="PAYMENT_APPROVED",
        delegation_tier="AGENT_LOGS",
        input_summary={
            "claim_id": claim["claim_id"],
            "pre_action_state": "PAYMENT_CALCULATING",
            "procedure_codes": claim["procedure_codes"],
            "payer_id": claim.get("payer_id", "UNKNOWN"),
            "authorized_by": physician_id,
        },
        output_summary={
            "payment_amount": payment,
            "new_state": "APPROVED",
        },
    )

    if not audit.committed:
        return _fire_et07(ctx, {
            "error": "AUDIT_WRITE_FAILED_BEFORE_PAYMENT_PATCH",
            "pipeline_step": "T-09",
            "claim_id": claim["claim_id"],
        })

    ctx.transition("APPROVED", from_state="PAYMENT_CALCULATING")
    ctx.payment_amount = payment

    return {
        "claim_id": claim["claim_id"],
        "status": "approved",
        "payment_amount": payment,
        "classification": "admin",
        "authorized_by": "PHYSICIAN_DETERMINATION",
        "physician_id": physician_id,
        "calibration_record_id": _CALIBRATION_RECORD["id"],
        "audit_trail": ctx.audit_trail,
    }
