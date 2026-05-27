# CLAUDE.md — WS1 Administrative Adjudication Agent (Prototype)

**Engagement:** Greenfield Health Systems — Medical Claims Adjudication Transformation
**Agent:** WS1 — Administrative path (65% of volume)
**Entry point:** `process_claim(claim: dict) -> dict` in `agents/ws1_agent.py`

---

## What this prototype does

Runs a normalized claim record through a 10-step adjudication pipeline. The pipeline checks eligibility, code validity, prior auth, and classifies the claim's clinical content. Admin-classified claims above the confidence threshold are approved with a payment amount. All other claims escalate to a human queue with a pre-filled packet.

One file is the brain (`agents/ws1_agent.py`). Everything else is a tool stub or the live classifier.

---

## NormalizedClaimInput — required input schema

`process_claim()` expects a dict with these fields. All are required unless marked optional.

| Field | Type | Example | Notes |
|---|---|---|---|
| `claim_id` | string | `"CLAIM-ADMIN-01"` | Unique claim identifier |
| `member_id` | string | `"GHS-MBR-0042891"` | Payer member ID |
| `provider_npi` | string | `"GHS-PRV-NPI-7124893"` | Provider NPI |
| `provider_specialty` | string | `"Primary Care Physician"` | Used by clinical classifier |
| `date_of_service` | string | `"2026-04-15"` | ISO 8601 date |
| `diagnosis_codes` | list[str] | `["Z00.00"]` | ICD-10; at least one required |
| `procedure_codes` | list[str] | `["99213"]` | CPT; at least one required |
| `procedure_quantities` | list[int] | `[1]` | Parallel to procedure_codes |
| `billed_amount` | float | `120.00` | Submitted charge |
| `payer_id` | string | `"GHS-PPO-2026"` | Payer/plan identifier |
| `source_format` | string | `"PORTAL_FORM"` | Origin format: `EDI_837P`, `EDI_837I`, `PORTAL_FORM`, `CMS_1500`, `FHIR_R4`, `EMAIL`, `FAX`, `EXCEPTION_NOTE` |
| `source_file` | string | `"CLAIM-ADMIN-01.json"` | Source filename for tracing |
| `intake_warnings` | list[str] | `[]` | Parser warnings; empty list if none |

**Field name discipline:** Never use `plan_id`, `provider_id`, or `submission_format` — these are old names that were renamed during C13 field alignment. The canonical names are `payer_id`, `provider_npi`, and `source_format`.

---

## ClaimContext — state machine

`ClaimContext` wraps the claim data and enforces state transitions with optimistic locking.

### Valid state transitions

```
NORMALISED → ADMIN_VALIDATING          (T-01: claim accepted)
ADMIN_VALIDATING → ROUTING             (T-08: classification started)
ROUTING → ADMIN_CLEARED                (T-08: classifier returned admin above threshold)
ROUTING → PENDING_PHYSICIAN_REVIEW     (T-08: clinical or uncertain or below threshold)
ADMIN_CLEARED → PAYMENT_CALCULATING   (T-09: fee schedule lookup started)
PAYMENT_CALCULATING → APPROVED        (T-09: audit committed, payment issued)
any → PENDING_HITL_EXCEPTION          (ET-07 AUDIT_FAILURE: audit write failed)
```

### `ctx.transition(to_state, *, from_state)` — optimistic locking

- Raises `ConflictError` (409) if `ctx.state != from_state`
- Every transition call must carry `from_state` explicitly — no exceptions
- In production this maps to a PATCH S-07 with the from_state guard

---

## AuditEntry

Created by `ctx.write_audit(action, delegation_tier, input_summary, output_summary)`.

- `status` starts as `PENDING_WRITE`, moves to `COMMITTED` after `.commit()`
- `ctx.write_audit()` calls `.commit()` immediately (synchronous stub)
- Always check `entry.committed` before issuing the next state transition

### `delegation_tier` values

| Value | When to use |
|---|---|
| `AGENT_ALONE` | Agent decides and acts without human input |
| `AGENT_LOGS` | Agent logs an outcome (payment write) |
| `HUMAN_DECIDES` | Human makes the decision; agent records it |

---

## Escalation triggers

| ID | Condition | Queue | State after |
|---|---|---|---|
| ET-01 | Classifier returns `clinical` or `uncertain` | `PHYSICIAN_HITL` | `PENDING_PHYSICIAN_REVIEW` |
| ET-02 | Classifier returns `admin` but confidence < threshold | `PHYSICIAN_HITL` | `PENDING_PHYSICIAN_REVIEW` |
| ET-03 | Eligibility check returns `discrepancy` | `EXCEPTION_PROCESSOR` | `PENDING_HITL_EXCEPTION` |
| ET-07 | Audit write failure OR FM-A-5 governance violation | `EXCEPTION_PROCESSOR` | `PENDING_HITL_EXCEPTION` (AUDIT_FAILURE) or unchanged (GOVERNANCE_VIOLATION) |

All escalation packets are saved to `escalations/<claim_id>.json`.

---

## FM-A-5 hard stop — never remove or weaken

Location: `ws1_agent.py` line ~350, first operation of T-09.

```python
if ctx.state != "ADMIN_CLEARED":
    return _fire_et07(ctx, ..., trigger_type="GOVERNANCE_VIOLATION", preserve_state=True)
```

**What it does:** T-09 checks `ctx.state == "ADMIN_CLEARED"` before any external call. If the check fails, `_fire_et07` fires with `trigger_type="GOVERNANCE_VIOLATION"`, `payment_amount` is never written, and the incoming state is preserved (not overwritten) so the exception processor gets the diagnostic signal.

**Why it is redundant by design:** In the normal flow T-09 is reached only after the `ROUTING → ADMIN_CLEARED` transition. The check is still present because in production T-09 can be invoked independently, and the check is the last line of defence against approving a claim that was not legitimately admin-cleared.

**Never remove it. Never move it below any other T-09 operation.**

---

## Audit-first ordering — never reverse

Pattern in T-09:
1. Write audit entry (`PAYMENT_APPROVED`)
2. Confirm `entry.committed == True`
3. **Only then** call `ctx.transition("APPROVED", ...)`
4. **Only then** set `ctx.payment_amount = payment`

If step 2 fails → ET-07 fires, `payment_amount` is NOT written, state stays at `PAYMENT_CALCULATING`.

**Never write `payment_amount` before the audit entry is COMMITTED.**

---

## CalibrationRecord — startup validation

`tools/calibration.py` runs `startup_validate()` at module import. 6-field check:

| Field | Requirement |
|---|---|
| `state` | Must equal `"SIGNED"` |
| `cmo_signoff_date` | Must not be null |
| `recall_achieved` | Must be ≥ 0.995 |
| `holdout_set_size` | Must be ≥ 500 |
| `call_site` | Must equal `"ROUTING"` (cross-contamination guard — WS1 must not load a WS2 VERIFICATION record) |
| `classifier_version` | Must match `config.CLASSIFIER_VERSION` |

If any check fails → `CalibrationError` is raised → `_STARTUP_ERROR` is set → `process_claim()` raises `RuntimeError` on every call. No claims may be processed.

The prototype uses a hardcoded stub record (`id: cal-rec-2026-05-001`, recall 0.997, CMO sign-off Dr. Marcus Webb).

---

## Configuration — `config.py`

| Variable | Value | What it controls |
|---|---|---|
| `CLINICAL_CONTENT_CONFIDENCE_THRESHOLD` | `0.70` | Minimum confidence for admin classification to proceed without HITL |
| `CLASSIFIER_VERSION` | `"sonnet-4-6:ws1-routing:v1"` | Must match `CalibrationRecord.classifier_version` at startup |

**The threshold is a named, configurable parameter — never hardcode `0.70` in pipeline logic. Always read from `config.CLINICAL_CONTENT_CONFIDENCE_THRESHOLD`.**

---

## Tools — real vs stub

| Tool | Status | Notes |
|---|---|---|
| `tools/clinical_classifier.py` | **Real** — live Sonnet 4.6 API call | Reads `ANTHROPIC_API_KEY` from environment. Returns `{classification, confidence, reasoning}`. |
| `tools/calibration.py` | Stub | Hardcoded mock record; 6-field check logic is real |
| `tools/eligibility.py` | Stub | Returns `confirmed` for all members except sentinel `member_id="GHS-MBR-INVALID"` → `discrepancy` |
| `tools/code_validity.py` | Stub | Always returns `valid` |
| `tools/prior_auth.py` | Stub | Always returns `NOT_REQUIRED` |
| `tools/fee_schedule.py` | Stub | Always returns `85.0` |

**Stub return values are fixed by design for the prototype — do not add variability unless explicitly asked.**

---

## Intake parsers — `tools/intake/`

These run before `process_claim()`. They produce NormalizedClaimInput dicts. WS1 is format-agnostic.

| Parser | Status | Notes |
|---|---|---|
| `edi_parser.py` | Production-ready | EDI 837P + 837I; hard-required fields: `claim_id`, `procedure_codes`, `diagnosis_codes` |
| `portal_json_adapter.py` | Production-ready | Portal JSON; hard-required: `submission_id`, `service_lines`, `diagnoses` |
| `cms1500_ocr_parser.py` | Not production-ready | 41% PARSE_FAILED rate — deferred; do not use in demo |

---

## Output schemas

### Approved claim

```json
{
  "claim_id": "...",
  "status": "approved",
  "payment_amount": 85.0,
  "classification": "admin",
  "confidence": 0.91,
  "calibration_record_id": "cal-rec-2026-05-001",
  "audit_trail": ["claim_intake_validated [COMMITTED]", "...", "payment_approved [COMMITTED]"]
}
```

### Escalated claim (ET-01 / ET-02)

```json
{
  "claim_id": "...",
  "status": "escalated",
  "escalation_trigger_id": "ET-01",
  "trigger_type": "CLINICAL_ROUTING",
  "routing_queue": "PHYSICIAN_HITL",
  "required_resolution": "Route as: [CLINICAL_CONFIRMED / ADMIN_CONFIRMED / NEEDS_ADDITIONAL_INFO]",
  "classification": "clinical",
  "confidence": 0.94,
  "escalation_reason": "...",
  "claim_context": {"procedure_code": "...", "diagnosis_code": "...", "provider_specialty": "..."},
  "audit_trail": [...]
}
```

### ET-07 governance violation

```json
{
  "claim_id": "...",
  "status": "escalated",
  "escalation_trigger_id": "ET-07",
  "trigger_type": "GOVERNANCE_VIOLATION",
  "routing_queue": "EXCEPTION_PROCESSOR",
  "required_resolution": "Governance violation: [INVESTIGATE_STATE_MACHINE / REJECT_CLAIM / ESCALATE_TO_COMPLIANCE]",
  "trigger_signal_values": {"error": "GOVERNANCE_HARD_STOP_T09", "actual_state": "...", "expected_state": "ADMIN_CLEARED", "claim_id": "..."},
  "claim_state_at_escalation": "ROUTING",
  "audit_trail": [...]
}
```

**`payment_amount` must never appear in any escalated output.**

---

## Running the prototype

```bash
# Prerequisites
pip install -r requirements.txt
export ANTHROPIC_API_KEY="sk-ant-..."   # required for live classifier (Paths 1 and 2)

# Single claim — named fixture
python run_claim.py --fixture CLAIM-ADMIN-01

# Single claim — any NormalizedClaimInput file
python run_claim.py --file normalized-tier1/CLM-2026-1000001.json

# Path 3 demo — governance hard stop (no API key needed)
python run_governance_demo.py

# Corpus batch (no API key needed — uses mock classifier)
python run_batch.py --dir normalized-tier1 --limit 0

# All tests (no API key needed — classifier is mocked)
pytest tests/ -v
```

---

## Testing

Tests live in `tests/test_ws1_pipeline.py`. The clinical classifier is always mocked in tests — no API calls.

Mock pattern:
```python
with patch("agents.ws1_agent.classify_clinical_content", return_value=_ADMIN_MOCK):
    result = process_claim(claim)
```

### 5 tests and what they cover

| Test | Fixture | Key assertion |
|---|---|---|
| `test_happy_path` | CLAIM-ADMIN-01 | `status=approved`, `payment_amount > 0`, 6 COMMITTED audit entries including `payment_approved` |
| `test_hitl_escalation` | CLAIM-CLINICAL-01 | `status=escalated`, `escalation_reason` names the procedure signal |
| `test_uncertain_classification` | CLAIM-UNCERTAIN-01 | `status=escalated`, `classification=uncertain`, `payment_approved` absent from audit trail |
| `test_eligibility_stub_returns_discrepancy_for_sentinel` | inline | `member_id=GHS-MBR-INVALID` → `status=discrepancy` from stub |
| `test_governance_hard_stop` | CLAIM-ADMIN-01 | ET-07 fires, `trigger_type=GOVERNANCE_VIOLATION`, `payment_amount` absent, `claim_state_at_escalation != "PENDING_HITL_EXCEPTION"` |

---

## What Claude must never do without explicit FDE instruction

- Remove or weaken the FM-A-5 pre-condition check (`ctx.state != "ADMIN_CLEARED"` at the top of T-09)
- Write `payment_amount` before the audit entry is COMMITTED
- Add a state machine transition without FDE sign-off
- Call `get_payment_amount()` before the FM-A-5 check passes
- Hardcode the confidence threshold — always read from `config.CLINICAL_CONTENT_CONFIDENCE_THRESHOLD`
- Use old field names: `plan_id`, `provider_id`, `submission_format`
- Mark a test as passing when any of the 5 key assertions fail

## When to ask vs decide

**Decide and proceed:**
- Fixing a test failure by reading the spec and correcting the code
- Adding a new fixture that follows the NormalizedClaimInput schema
- Extending a stub tool's return logic for a new test case

**Ask before proceeding:**
- Any change to the FM-A-5 hard stop logic
- Any change to the state machine transitions
- Any change to audit-first ordering in T-09
- Changing the CalibrationRecord 6-field validation thresholds
- Adding a real API call to any stub tool
