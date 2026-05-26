# D7A — Validation Design Diagnosis

**Source scenarios:** `Deliverables/D7_validation_plan.md`
**Prototype:** `prototype/agents/ws1_agent.py`
**Date:** 2026-05-25

---

## Table of contents

- [1. Test run summary](#1-test-run-summary)
- [2. S-1 — Admin claim approved end-to-end](#2-s-1--admin-claim-approved-end-to-end)
- [3. S-2 — Confidence at exactly the threshold](#3-s-2--confidence-at-exactly-the-threshold)
- [4. S-3 — FM-A-5 governance hard stop](#4-s-3--fm-a-5-governance-hard-stop)
- [5. Residual observation surfaced during testing](#5-residual-observation-surfaced-during-testing)

---

## 1. Test run summary

All three D7 scenarios passed every pass criterion. No failures detected.

| Scenario | Result | Key assertions |
|----------|--------|----------------|
| S-1 Happy path | PASS | `status=approved`, `payment_amount=85.0`, `calibration_record_id=cal-rec-2026-05-001`, 6 COMMITTED audit entries, no escalation fields |
| S-2 Confidence at 0.70 | PASS | `status=approved` — `>=` comparison confirmed inclusive; no ET-02 fired |
| S-3 FM-A-5 hard stop | PASS | `escalation_trigger_id=ET-07`, `trigger_type=GOVERNANCE_VIOLATION`, `payment_amount` absent, `claim_state_at_escalation=ROUTING` (state preserved, not overwritten) |

---

## 2. S-1 — Admin claim approved end-to-end

**Result:** PASS

**Output:**
```json
{
  "status": "approved",
  "payment_amount": 85.0,
  "calibration_record_id": "cal-rec-2026-05-001",
  "confidence": 0.91,
  "audit_trail": [
    "claim_intake_validated [COMMITTED]",
    "eligibility_confirmed [COMMITTED]",
    "code_validity_checked [COMMITTED]",
    "prior_auth_confirmed [COMMITTED]",
    "clinical_classification_completed [COMMITTED]",
    "payment_approved [COMMITTED]"
  ]
}
```

All pass criteria met. Audit-first ordering confirmed: `payment_approved [COMMITTED]` is entry 6, written before the state PATCH to `APPROVED`. `calibration_record_id` present in the approved output — the governance chain is traceable from payment back to the CMO-signed CalibrationRecord.

**Diagnosis:** Nothing broke. No category required. If it had broken, the most likely failure would have been `payment_amount` written without `payment_approved [COMMITTED]` in the audit trail — a **builder misread** of the audit-first requirement (D4a §10, REQ-A-4), which is stated explicitly and has no ambiguous reading.

---

## 3. S-2 — Confidence at exactly the threshold

**Result:** PASS

**Output:**
```json
{
  "status": "approved",
  "payment_amount": 85.0,
  "confidence": 0.7
}
```

The `>=` comparison in `ws1_agent.py` (`confidence >= CLINICAL_CONTENT_CONFIDENCE_THRESHOLD`) correctly treats 0.70 as an approved-routing case. No ET-02 fired. No `borderline_confidence_flag` in output.

**Diagnosis:** Nothing broke. If it had broken — `status=escalated` with `escalation_trigger_id=ET-02` — the category would be **builder misread**: D4a §6 D-A-4 states "confidence_score `≥` CLINICAL_CONTENT_CONFIDENCE_THRESHOLD" with the `≥` symbol explicit. A builder who used `>` (strict greater-than) contradicts the spec as written. No ambiguity; the symbol is unambiguous. Fix: re-prompt with the relevant line highlighted — do not change the spec.

**Note:** `result["confidence"]` displays as `0.7` (Python drops the trailing zero from `0.70`). `0.7 == 0.70` in Python is `True`, so the assertion passes. This is an **acceptable variation** — the numeric value is identical; the display difference is a JSON serialisation artifact with no functional consequence.

---

## 4. S-3 — FM-A-5 governance hard stop

**Result:** PASS

**Output:**
```json
{
  "status": "escalated",
  "escalation_trigger_id": "ET-07",
  "trigger_type": "GOVERNANCE_VIOLATION",
  "claim_state_at_escalation": "ROUTING",
  "trigger_signal_values": {
    "error": "GOVERNANCE_HARD_STOP_T09",
    "actual_state": "ROUTING",
    "expected_state": "ADMIN_CLEARED"
  }
}
```

FM-A-5 pre-condition check fired correctly before `get_payment_amount()` was called. `payment_amount` absent. `claim_state_at_escalation = ROUTING` — the injected state was preserved, not overwritten to `PENDING_HITL_EXCEPTION`, consistent with REQ-A-6(c) and the GAP-10 resolution. `trigger_type = GOVERNANCE_VIOLATION` consistent with GAP-14 resolution.

**Diagnosis:** Nothing broke. If it had broken in two different ways:

1. `status=approved` with `payment_amount=85.0` — the FM-A-5 state check was skipped entirely. **Builder misread**: REQ-A-6 states the check is "the first operation of T-09, before any fee schedule lookup." Unambiguous. Fix: re-prompt with REQ-A-6 highlighted.

2. `trigger_type=AUDIT_FAILURE` instead of `GOVERNANCE_VIOLATION` — the pre-GAP-14 implementation. **Spec ambiguity** (pre-resolution): the original ET-07 spec defined only `AUDIT_FAILURE` as the trigger_type, so a builder reading §7 before GAP-14 was resolved would have implemented correctly per the old spec. Fixed by adding `GOVERNANCE_VIOLATION` to the preamble `EscalationPacket.trigger_type` enum and updating the ET-07 action column.

---

## 5. Residual observation surfaced during testing

**What was observed:** S-3 output contains `required_resolution = "Audit failure: [RECONSTRUCT_AND_CONTINUE / REJECT_CLAIM / ESCALATE_TO_COMPLIANCE]"` while `trigger_type = GOVERNANCE_VIOLATION`. An exception processor reviewer looking at this ticket would see a governance violation classified under an "Audit failure" resolution prompt — the two fields tell different stories about what happened.

**Why it matters:** The `required_resolution` field is defined per `escalation_trigger_id` in §7 (one text per ET-01 through ET-07). GAP-14 split ET-07 into two causes — `AUDIT_FAILURE` and `GOVERNANCE_VIOLATION` — but the §7 required_resolution table was not updated to reflect the split. The required_resolution text for both ET-07 causes is still "Audit failure: [...]".

**Category:** Spec ambiguity. The spec is internally consistent (§7 maps ET-07 → one required_resolution text), but the GAP-14 resolution created a new cause that the required_resolution text does not cover. The builder implemented correctly per the spec; the spec needs a small update.

**Fix:** Add a second row to the §7 required_resolution table for the governance-violation sub-cause of ET-07:

| Trigger ID | Cause | `required_resolution` |
|------------|-------|----------------------|
| ET-07 | Audit write failure | `"Audit failure: [RECONSTRUCT_AND_CONTINUE / REJECT_CLAIM / ESCALATE_TO_COMPLIANCE]"` |
| ET-07 | Governance hard-stop (state mismatch) | `"Governance violation: [INVESTIGATE_STATE_MACHINE / REJECT_CLAIM / ESCALATE_TO_COMPLIANCE]"` |

The prototype should select the appropriate text based on `trigger_type`. This does not require a re-prompt of the builder — it is a spec update that the builder should receive before the next build pass.
