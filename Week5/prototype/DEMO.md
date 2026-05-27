# WS1 Prototype — Demo Script (under 5 minutes)

**Agent:** WS1 Administrative Adjudication Agent  
**Scope:** Administrative path (65% of volume) — eligibility check, code validity, prior auth routing, clinical classification, payment calculation  
**Format coverage:** Portal-JSON normalized fixtures (20% of intake volume). WS1 operates on a normalized claim record; format parsing is Intake Agent scope. See "Format coverage" section at the bottom for the coach Q&A answer.

---

## Before you start

From the `prototype/` directory:

```bash
pip install -r requirements.txt   # one-time
pytest tests/ -v                  # confirm all 5 tests passing before the demo
```

Expected output: `5 passed` with no failures or warnings.

**API key (required for Path 1 and Path 2 — live classifier calls):**

```powershell
$env:ANTHROPIC_API_KEY = "sk-ant-..."
```

Set this once in your terminal session before running any `run_claim.py` command. The key is read from the environment by the clinical classifier (`tools/clinical_classifier.py`). If it is missing you will get: `Could not resolve authentication method. Expected either api_key or auth_token to be set.`

Path 3 and the corpus validation pass (`run_batch.py` without `--live`) do not call the API — they use the mock classifier and will run without the key.

---

## Path 1 — Happy path (S-1): clean administrative claim → approved

**What this shows:** An admin-classified claim clears all checks and is approved with a payment amount. The audit trail confirms audit-first ordering — every entry is COMMITTED before the payment step executes.

```bash
python run_claim.py --fixture CLAIM-ADMIN-01
```

**What to say:**  
"CLAIM-ADMIN-01 is a routine office visit — CPT 99213, diagnosis Z00.00, Primary Care Physician. The agent runs eligibility, code validity, prior auth, and clinical classification in sequence. Classifier returns `admin` at confidence 0.91, which is above the 0.70 threshold. All checks pass. The agent writes the audit entry — status COMMITTED — before issuing the payment. Output is `status: approved`, `payment_amount: 85.0`, and the full audit trail showing all six committed entries."

**Key fields to point out in the output:**
- `"status": "approved"`
- `"payment_amount": 85.0`
- `"classification": "admin"`, `"confidence": 0.91`
- `"calibration_record_id"` — governance chain back to CMO-signed CalibrationRecord
- `"audit_trail"` — 6 entries, all COMMITTED, `payment_approved` is the last entry

---

## Path 2 — Uncertain classification escalation (ET-01/ET-02): ambiguous claim → HITL

**What this shows:** When the classifier returns `uncertain` (confidence 0.48, below threshold 0.70), the agent routes to physician HITL queue rather than auto-deciding. The agent does NOT exit early — it completes eligibility, codes, and prior auth before routing, so the physician receives a fully pre-filled escalation packet.

```bash
python run_claim.py --fixture CLAIM-UNCERTAIN-01
```

**What to say:**  
"CLAIM-UNCERTAIN-01 is therapeutic exercise (97110) for low back pain (M54.5) from a General Practitioner. The procedure code is used for both routine physiotherapy and post-surgical rehabilitation — the provider type doesn't resolve the ambiguity. Classifier returns `uncertain` at confidence 0.48. Below threshold, so the agent escalates to the physician HITL queue. Critically: the agent has already run eligibility, code validity, and prior auth, so the escalation packet the physician receives is fully pre-filled. That's the operational lift — the agent does the administrative pre-work even for claims it can't auto-decide."

**Key fields to point out in the output:**
- `"status": "escalated"`
- `"classification": "uncertain"`, `"confidence": 0.48`
- `"escalation_reason"` — names the contradictory signals
- `"audit_trail"` — eligibility, codes, prior_auth, routing all present; `payment_approved` absent

---

## Path 3 — Governance hard stop (FM-A-5, ET-07): state corruption → GOVERNANCE_VIOLATION

**What this shows:** FM-A-5 is a hard stop: T-09 (payment calculation) checks `state == ADMIN_CLEARED` as its first operation. If state was corrupted — by a concurrent request, a race condition, or a future spec addition that adds a transition — the agent aborts and fires ET-07 with `trigger_type: GOVERNANCE_VIOLATION`. `payment_amount` is never written.

```bash
python run_governance_demo.py
```

**What to say:**  
"This is the same claim as Path 1 — CLAIM-ADMIN-01, which would normally be approved. The demo script patches the state machine to corrupt state to `ROUTING` immediately after `ADMIN_CLEARED` is set, simulating a race condition or a future spec addition that adds an unexpected transition. T-09's first operation is the FM-A-5 pre-condition check: `state == ADMIN_CLEARED`. It fails. ET-07 fires immediately — `trigger_type: GOVERNANCE_VIOLATION`, routed to `EXCEPTION_PROCESSOR`. `payment_amount` is absent. The incoming state `ROUTING` is preserved in `claim_state_at_escalation` — not overwritten — so the exception processor gets the diagnostic signal it needs to investigate."

**Key fields to point out in the output:**
- `"status": "escalated"`
- `"escalation_trigger_id": "ET-07"`
- `"trigger_type": "GOVERNANCE_VIOLATION"`
- `"payment_amount"` — absent (the hard stop worked)
- `"claim_state_at_escalation": "ROUTING"` — incoming state preserved, not overwritten
- `"trigger_signal_values"` — names `actual_state` vs `expected_state` for the exception processor

---

## Optional — run all 5 tests in sequence to close the demo

```bash
pytest tests/ -v
```

Shows all five paths in ~2 seconds: happy path, HITL escalation, uncertain classification, eligibility discrepancy stub, and governance hard stop.

---

## Format coverage — defense Q&A answer

**Coach question:** "Your fixtures have `submission_format: EDI_837`. Does your prototype actually handle EDI? What about the PDF and email formats in the Claims Pack?"

**Answer:**  
WS1 operates on a normalized claim record — a flat JSON structure with `claim_id`, `member_id`, `provider_npi`, `procedure_codes`, etc. Format parsing is Intake Agent scope (Wave 1, separate agent). By the time a claim reaches WS1, the Intake Agent has already extracted it from whichever of the 8 intake formats it arrived in.

The 8 formats split into three tiers:
- **Electronic structured (80% of volume):** EDI 837P, EDI 837I, Portal JSON. Clearinghouse extraction — no LLM cost; output is the same normalized record WS1 receives.
- **Paper PDF (10%):** CMS-1500 forms. OCR at the clearinghouse or via the `cms1500-ocr/` pre-extracted text in the Claims Pack. Higher extraction failure rate (~5%); the integration spec IC-S-01 defines the failure path.
- **Unstructured (10%):** Email `.eml`, fax PDF, exception notes PDF. One Haiku call per claim for LLM extraction (~$0.0004/claim). Integration spec IC-S-01 §9 defines extraction failure escalation.

The prototype has been validated against all three Tier 1 format parsers — not just the four hand-crafted fixtures. The corpus validation pass ran all 1,493 pre-normalised Tier 1 files (EDI_837P: 936, PORTAL_FORM: 374, EDI_837I: 183) through the full WS1 pipeline and confirmed 6/6 structural assertions with zero violations: no crashes, no payment without a committed audit entry, no `payment_amount` in any escalated result, `calibration_record_id` present on every approved claim, all three formats represented. The WS1 adjudication logic is format-agnostic — eligibility, code validity, prior auth, clinical classification, and payment behave identically regardless of which parser produced the normalized input.

**What would break this in production that the prototype doesn't show:** The Intake Agent (Wave 1) is not yet built. For the 20% of unstructured and PDF claims, we have no tested extraction logic. The integration contract IC-S-01 §9 defines the failure escalation path, but the end-to-end path from raw email or PDF to WS1 input is a known gap. That gap is named in the validation plan (D7 §2b) and is the first Wave 1 build item.

---

## Optional — corpus validation pass (if asked about format coverage or scale)

```bash
python run_batch.py --dir normalized-tier1 --limit 0
```

**What to say:**  
"This runs all 1,493 pre-normalised Tier 1 claims through the pipeline — 936 EDI 837P, 374 Portal JSON, 183 EDI 837I — using a heuristic mock classifier. The result confirms the pipeline handles all three format parser outputs without structural failures: 975 approved, 276 clinical escalations, 242 uncertain escalations, zero errors. Note: the routing split reflects the mock classifier's CPT-range rules, not production accuracy — there are no golden labels for this corpus. What it proves is that the canonical field contract holds across every input shape the three parsers produce."

---

## Timing guide

| Step | Time |
|---|---|
| `pytest` pre-check (all 5 pass) | ~15 sec |
| Path 1 — happy path | ~30 sec to run, ~60 sec to explain |
| Path 2 — uncertain escalation | ~30 sec to run, ~60 sec to explain |
| Path 3 — governance hard stop test | ~15 sec to run, ~60 sec to explain |
| Wrap + format coverage question | ~60 sec |
| **Total** | **~5 min** |
