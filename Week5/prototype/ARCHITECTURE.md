# WS1 Prototype — Architecture Overview

**Agent:** WS1 Administrative Adjudication Agent  
**Core file:** `agents/ws1_agent.py`  
**Entry point:** `process_claim(claim: dict) -> dict`

---

## What it is

A Python implementation of the WS1 Administrative Adjudication Agent — the 10-step pipeline that processes a claim from intake through payment or escalation. One file is the brain (`ws1_agent.py`); the rest are tool stubs.

---

## The pipeline — step by step

`process_claim(claim: dict)` takes a normalized claim dict and runs it through this sequence:

| Step | Component | What happens | Real or stub |
|---|---|---|---|
| Startup | `tools/calibration.py` — `startup_validate()` | Agent refuses to process any claim unless a valid CMO-signed calibration record exists. Validates 6-field check at import time; sets `_STARTUP_ERROR` if invalid; `process_claim()` raises `RuntimeError` on any call while error is set. | Stub — hardcoded fixture (`id: cal-rec-2026-05-001`, recall 0.997, CMO sign-off set) |
| T-01 | `ClaimContext.transition()` + `write_audit()` | Accepts the incoming normalized claim and opens the adjudication record. Transition `NORMALISED → ADMIN_VALIDATING`; write and commit first audit entry; ET-07 fires if audit write fails. | Real — state machine + optimistic locking |
| T-02/03 | `tools/eligibility.py` — `check_eligibility()` | Checks whether the member had active insurance coverage on the date of service. If coverage cannot be confirmed, the claim stops here and goes to the HITL exception queue. `status == discrepancy` → escalate ET-03 and stop. | Stub — returns `confirmed` for all members except sentinel `GHS-MBR-INVALID` → `discrepancy` |
| T-04/05 | `tools/code_validity.py` — `check_code_validity()` | Checks that every procedure and diagnosis code on the claim is a real, valid code in the current code set; write audit entry. | Stub — always returns `valid` |
| T-06/07 | `tools/prior_auth.py` — `check_prior_auth()` | Checks whether the procedure required prior approval from the insurer and whether that approval was obtained before the service was rendered; write audit entry. | Stub — always returns `NOT_REQUIRED` |
| T-08 | `tools/clinical_classifier.py` — `classify_clinical_content()` | The AI decision point. Transition `ADMIN_VALIDATING → ROUTING`; live Sonnet 4.6 call reads procedure code, diagnosis code, and provider specialty, then returns `{classification, confidence, reasoning}`. `clinical` → ET-01 (physician HITL); `uncertain` at any confidence OR `admin` below threshold → ET-02 (physician HITL); both stop. Write audit entry. | **Real** — live Sonnet 4.6 API call |
| FM-A-5 | `ws1_agent.py` line 350 | Before calculating any payment, confirms the claim legitimately cleared the admin routing gate. Transition `ROUTING → ADMIN_CLEARED`; T-09 immediately checks `ctx.state != "ADMIN_CLEARED"` before any external call; if check fails → ET-07 `GOVERNANCE_VIOLATION`, state preserved, stop. | Real — explicit hard stop in code |
| T-09 | `tools/fee_schedule.py` — `get_payment_amount()` | Looks up the contracted payment rate for the procedure. Transition `ADMIN_CLEARED → PAYMENT_CALCULATING`; write `PAYMENT_APPROVED` audit entry; confirm COMMITTED **before** issuing APPROVED transition; ET-07 fires if audit not committed. | Stub — always returns `85.0`; audit-first ordering is real |
| Done | `ClaimContext.transition()` | Marks the claim approved and returns the result. Transition `PAYMENT_CALCULATING → APPROVED`; return `payment_amount`, `calibration_record_id`, and full `audit_trail`. | Real — state machine |

---

## Three governance invariants built into the code

**1. Audit-first ordering**  
`write_audit()` calls `entry.commit()` synchronously and returns the entry. The caller checks `if not audit.committed` before issuing any state transition. If the audit write fails, ET-07 fires and `payment_amount` is never written.

**2. FM-A-5 hard stop**  
`if ctx.state != "ADMIN_CLEARED"` is literally T-09's first line. If anything has corrupted state between the routing step and the payment step, the agent aborts, fires ET-07 with `trigger_type=GOVERNANCE_VIOLATION`, and preserves the incoming state as the diagnostic signal.

**3. CalibrationRecord startup validation**  
Runs once at module import via `startup_validate()`. If the record fails its 6-field check (threshold value, recall ≥ 0.995, holdout size ≥ 500, labelling date, CMO name, CMO sign-off date), `_STARTUP_ERROR` is set and every subsequent call to `process_claim()` raises `RuntimeError`.

---

## The state machine

`ClaimContext` wraps the claim data and enforces transitions with optimistic locking:

```
NORMALISED → ADMIN_VALIDATING → ROUTING → ADMIN_CLEARED → PAYMENT_CALCULATING → APPROVED
                                        ↘ PENDING_PHYSICIAN_REVIEW  (ET-01/ET-02)
              ↘ PENDING_HITL_EXCEPTION  (ET-03, ET-07)
```

Every `ctx.transition(to, from_state=expected)` raises `ConflictError` if the current state isn't what was expected — the in-memory equivalent of the S-07 PATCH with a `from_state` guard.

---


## The three demo paths

| Path | Input | What fires | Output |
|---|---|---|---|
| Happy path | CLAIM-ADMIN-01 — clean admin claim | All stubs pass; classifier returns `admin` at 0.91; FM-A-5 passes; audit committed | `status: approved`, `payment_amount: 85.0`, 6 COMMITTED audit entries |
| HITL escalation | CLAIM-UNCERTAIN-01 — ambiguous claim | Classifier returns `uncertain` at 0.48 → ET-02 | `status: escalated`, physician HITL queue, no payment |
| Governance hard stop | Test patches state to `ROUTING` after `ADMIN_CLEARED` | T-09 pre-condition check trips → ET-07 GOVERNANCE_VIOLATION | `status: escalated`, `payment_amount` absent, state preserved |

---

## Key configuration

```python
# config.py
CLINICAL_CONTENT_CONFIDENCE_THRESHOLD = 0.70
CLASSIFIER_VERSION = "sonnet-4-6:ws1-routing:v1"
```

The threshold is the boundary condition for the FM-A-5 / ET-02 gate. Claims with `admin` classification at confidence ≥ 0.70 proceed to payment. Everything else escalates to physician HITL.
