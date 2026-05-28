"""
WS1 pipeline tests — three required paths per C1c_prototype_scope.md.
The clinical classifier is mocked so tests are deterministic and do not
make live API calls. Mock return values are chosen to be realistic for
each fixture's codes and provider type.
"""

import json
import os
import sys
from unittest.mock import patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from agents.ws1_agent import process_claim, process_physician_approved_claim

_FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "..", "fixtures")


def _load(fixture_id: str) -> dict:
    with open(os.path.join(_FIXTURES_DIR, f"{fixture_id}.json"), encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# test_happy_path
# ---------------------------------------------------------------------------

_ADMIN_MOCK = {
    "classification": "admin",
    "confidence": 0.91,
    "reasoning": (
        "Routine office visit (99213) for annual wellness exam (Z00.00) billed "
        "by a Primary Care Physician — all three signals unambiguously administrative."
    ),
}


def test_happy_path():
    """
    Admin claim with all stubs passing and classifier returning admin above threshold.
    Asserts: status=approved, payment_amount present and > 0, no escalation fields.
    """
    claim = _load("CLAIM-ADMIN-01")
    with patch("agents.ws1_agent.classify_clinical_content", return_value=_ADMIN_MOCK):
        result = process_claim(claim)

    assert result["status"] == "approved", f"Expected approved, got: {result['status']}"
    assert "payment_amount" in result, "payment_amount missing from approved result"
    assert result["payment_amount"] > 0, "payment_amount must be > 0"
    assert "escalation_reason" not in result, "Approved result must not contain escalation_reason"
    assert result["classification"] == "admin"
    assert result["confidence"] == 0.91
    assert any("eligibility_confirmed" in s for s in result["audit_trail"])
    assert any("clinical_classification_completed" in s for s in result["audit_trail"])
    assert any("payment_approved" in s for s in result["audit_trail"])


# ---------------------------------------------------------------------------
# test_hitl_escalation
# ---------------------------------------------------------------------------

_CLINICAL_MOCK = {
    "classification": "clinical",
    "confidence": 0.94,
    "reasoning": (
        "Total knee arthroplasty (27447) for primary osteoarthritis (M17.11) billed "
        "by an Orthopaedic Surgeon — major elective surgery requiring medical necessity "
        "determination; physician review required per standard clinical criteria."
    ),
}


def test_hitl_escalation():
    """
    Boundary claim where classifier returns clinical.
    Asserts: status=escalated, escalation_reason non-empty and names the signal,
    confidence present, claim_context includes all three signal fields.
    """
    claim = _load("CLAIM-CLINICAL-01")
    with patch("agents.ws1_agent.classify_clinical_content", return_value=_CLINICAL_MOCK):
        result = process_claim(claim)

    assert result["status"] == "escalated", f"Expected escalated, got: {result['status']}"
    assert "escalation_reason" in result, "escalation_reason missing from escalated result"
    assert len(result["escalation_reason"]) > 0, "escalation_reason must not be empty"
    assert "confidence" in result, "confidence missing from escalated result"
    ctx = result.get("claim_context", {})
    assert "procedure_code" in ctx, "claim_context.procedure_code missing"
    assert "diagnosis_code" in ctx, "claim_context.diagnosis_code missing"
    assert "provider_specialty" in ctx, "claim_context.provider_specialty missing"
    # escalation reason must name the procedure or a signal that caused the escalation
    assert any(
        token in result["escalation_reason"]
        for token in ("27447", "knee", "clinical", "physician", "Orthopaedic")
    ), "escalation_reason does not name the ambiguous signal"


# ---------------------------------------------------------------------------
# test_uncertain_classification
# ---------------------------------------------------------------------------

_UNCERTAIN_MOCK = {
    "classification": "uncertain",
    "confidence": 0.48,
    "reasoning": (
        "Therapeutic exercise (97110) with low back pain (M54.5) billed by a "
        "General Practitioner — procedure code is used for both routine physiotherapy "
        "billing and post-surgical rehabilitation; provider type does not resolve ambiguity."
    ),
}


def test_uncertain_classification():
    """
    Ambiguous claim where classifier returns uncertain.
    Asserts: status=escalated, classification=uncertain, confidence present,
    escalation_reason names the contradictory signals, pipeline does not exit early
    (audit_trail shows all steps up to routing completed).
    """
    claim = _load("CLAIM-UNCERTAIN-01")
    with patch("agents.ws1_agent.classify_clinical_content", return_value=_UNCERTAIN_MOCK):
        result = process_claim(claim)

    assert result["status"] == "escalated", f"Expected escalated, got: {result['status']}"
    assert result["classification"] == "uncertain", (
        f"Expected classification=uncertain, got: {result['classification']}"
    )
    assert "confidence" in result, "confidence missing"
    assert result["confidence"] == 0.48
    assert "escalation_reason" in result, "escalation_reason missing"
    assert "uncertain" in result["escalation_reason"].lower() or "contradict" in result["escalation_reason"].lower(), (
        "escalation_reason must name the contradictory signals for an uncertain classification"
    )
    # pipeline must not exit early — eligibility, codes, prior_auth, routing all present
    trail = result.get("audit_trail", [])
    assert any("eligibility_confirmed" in s for s in trail), "audit_trail missing eligibility step"
    assert any("code_validity_checked" in s for s in trail), "audit_trail missing codes step"
    assert any("prior_auth_confirmed" in s for s in trail), "audit_trail missing prior_auth step"
    assert any("clinical_classification_completed" in s for s in trail), "audit_trail missing routing step"
    # payment step must NOT be present — uncertain claim must not reach fee schedule
    assert not any("payment_approved" in s for s in trail), (
        "payment step must not appear in audit_trail for an uncertain/escalated claim"
    )


# ---------------------------------------------------------------------------
# eligibility stub wiring check (not a required demo path — no dedicated test function)
# ---------------------------------------------------------------------------

def test_eligibility_stub_returns_discrepancy_for_sentinel():
    from tools.eligibility import check_eligibility
    sentinel_claim = {"member_id": "GHS-MBR-INVALID"}
    result = check_eligibility(sentinel_claim)
    assert result["status"] == "discrepancy"


# ---------------------------------------------------------------------------
# test_governance_hard_stop — FM-A-5
# ---------------------------------------------------------------------------

def test_governance_hard_stop():
    """
    FM-A-5: T-09 must abort and fire ET-07 if ClaimRecord.state != ADMIN_CLEARED
    at the start of the payment calculation step.

    Simulates the production scenario where T-09 is invoked independently of
    the routing step (state can be anything at that point).

    Strategy: let the ADMIN_CLEARED transition succeed, then corrupt the state
    so the FM-A-5 pre-condition check fires on the very next line.
    """
    from agents.ws1_agent import ClaimContext

    claim = _load("CLAIM-ADMIN-01")

    original_transition = ClaimContext.transition

    def patched_transition(self, to_state, *, from_state):
        original_transition(self, to_state, from_state=from_state)
        # Corrupt state immediately after ADMIN_CLEARED is set to force the hard stop
        if to_state == "ADMIN_CLEARED":
            self.state = "ROUTING"

    with patch("agents.ws1_agent.classify_clinical_content", return_value=_ADMIN_MOCK):
        with patch.object(ClaimContext, "transition", patched_transition):
            result = process_claim(claim)

    assert result.get("escalation_trigger_id") == "ET-07", (
        f"FM-A-5 hard stop must fire ET-07, got escalation_trigger_id={result.get('escalation_trigger_id')!r}"
    )
    assert result.get("trigger_type") == "GOVERNANCE_VIOLATION", (
        f"Governance hard-stop ET-07 must carry trigger_type=GOVERNANCE_VIOLATION, "
        f"got {result.get('trigger_type')!r}"
    )
    assert result.get("status") == "escalated", (
        f"FM-A-5 hard stop must set status=escalated, got {result.get('status')!r}"
    )
    assert "payment_amount" not in result, (
        "payment_amount must not be written when FM-A-5 hard stop fires"
    )
    # REQ-A-6(c): state must NOT be overwritten to PENDING_HITL_EXCEPTION —
    # the incoming state is the diagnostic signal and must be preserved.
    assert result.get("claim_state_at_escalation") != "PENDING_HITL_EXCEPTION", (
        "Governance hard-stop must preserve the incoming state, not overwrite it to PENDING_HITL_EXCEPTION"
    )


# ---------------------------------------------------------------------------
# test_physician_approved_path — GAP-15
# ---------------------------------------------------------------------------

_PRIOR_AUDIT_TRAIL = [
    "claim_intake_validated [COMMITTED]",
    "eligibility_confirmed [COMMITTED]",
    "code_validity_checked [COMMITTED]",
    "prior_auth_confirmed [COMMITTED]",
    "clinical_classification_completed [COMMITTED]",
]


def test_physician_approved_path():
    """
    GAP-15: PHYSICIAN_REVIEWING -> ADMIN_CLEARED -> T-09 -> APPROVED.

    Simulates a physician recording ADMIN_CONFIRMED on an uncertain claim.
    Asserts: status=approved, payment_amount present, authorized_by=PHYSICIAN_DETERMINATION,
    full audit trail includes physician_admin_confirmed and payment_approved,
    prior audit entries restored, no escalation fields.
    """
    claim = _load("CLAIM-UNCERTAIN-01")

    result = process_physician_approved_claim(
        claim,
        physician_id="DR-TEST-001",
        prior_audit_trail=_PRIOR_AUDIT_TRAIL,
    )

    assert result["status"] == "approved", f"Expected approved, got: {result['status']}"
    assert "payment_amount" in result, "payment_amount missing from physician-approved result"
    assert result["payment_amount"] > 0, "payment_amount must be > 0"
    assert result["authorized_by"] == "PHYSICIAN_DETERMINATION", (
        f"Expected authorized_by=PHYSICIAN_DETERMINATION, got: {result.get('authorized_by')}"
    )
    assert result["physician_id"] == "DR-TEST-001", (
        f"Expected physician_id=DR-TEST-001, got: {result.get('physician_id')}"
    )
    assert result["classification"] == "admin", (
        "Physician-confirmed admin claim must carry classification=admin"
    )
    assert "calibration_record_id" in result, "calibration_record_id missing"
    assert "escalation_reason" not in result, "Approved result must not contain escalation_reason"

    trail = result.get("audit_trail", [])
    # Prior entries must be restored
    assert any("claim_intake_validated" in s for s in trail), "Prior audit entry claim_intake_validated missing"
    assert any("eligibility_confirmed" in s for s in trail), "Prior audit entry eligibility_confirmed missing"
    assert any("clinical_classification_completed" in s for s in trail), "Prior audit entry classification missing"
    # Physician determination entry must be present
    assert any("physician_admin_confirmed" in s.lower() for s in trail), (
        "physician_admin_confirmed must appear in audit_trail"
    )
    # Payment approved must be the last committed action
    assert any("payment_approved" in s for s in trail), (
        "payment_approved must appear in audit_trail for physician-approved claim"
    )
