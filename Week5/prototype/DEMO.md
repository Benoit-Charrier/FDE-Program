# WS1 Prototype — Demo Script (under 5 minutes)

**Agent:** WS1 Administrative Adjudication Agent  
**Scope:** Administrative path (65% of volume) — eligibility check, code validity, prior auth routing, clinical classification, payment calculation  
**Format coverage:** Tier 1 formats — EDI 837P (50%), EDI 837I (10%), Portal JSON (20%) = 80% of intake volume. All three parsers validated against the full 1,493-file Tier 1 corpus. WS1 operates on a normalized claim record; format parsing is Intake Agent scope. See "Format coverage" section at the bottom for the coach Q&A answer.

---

## Before you start

From the `prototype/` directory:

```bash
pip install -r requirements.txt   # one-time
pytest tests/ -v                  # confirm all 6 tests passing before the demo
```

Expected output: `6 passed` with no failures or warnings.

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

## Path 2 — Uncertain classification escalation + HITL review loop (ET-01/ET-02)

**What this shows:** When the classifier returns `uncertain` (confidence 0.48, below threshold 0.70), the agent routes to physician HITL queue rather than auto-deciding. The physician reviews the escalation packet and records a determination — ADMIN_CONFIRMED re-enters WS1 at T-09 and issues payment. This is the full agentic HITL loop: agent pre-fills, human decides, agent executes.

**Step 2a — generate the escalation:**

```bash
python run_claim.py --fixture CLAIM-UNCERTAIN-01
```

**What to say:**  
"CLAIM-UNCERTAIN-01 is therapeutic exercise (97110) for low back pain (M54.5) from a General Practitioner. The procedure code is used for both routine physiotherapy and post-surgical rehabilitation — the provider type doesn't resolve the ambiguity. Classifier returns `uncertain` at confidence 0.48. Below threshold, so the agent escalates to the physician HITL queue. Critically: the agent has already run eligibility, code validity, and prior auth, so the escalation packet the physician receives is fully pre-filled — five committed audit entries. That's the operational lift."

**Step 2b — physician reviews and closes the loop:**

```bash
python review_claim.py --claim-id CLAIM-UNCERTAIN-01
```

This opens the interactive reviewer. It displays the pre-filled packet — classification, confidence, escalation reason, and every completed audit step. The physician picks a determination:

```
  1. ADMIN_CONFIRMED
     Confirm as administrative -- re-enter WS1 T-09 and issue payment
  2. CLINICAL_CONFIRMED
     Confirm as clinical -- route for medical necessity determination (WS2)
  3. NEEDS_ADDITIONAL_INFO
     Request additional documentation from provider
```

**Choosing 1 (ADMIN_CONFIRMED):**  
The reviewer records `PHYSICIAN_ADMIN_CONFIRMED` with `delegation_tier: HUMAN_DECIDES`, transitions `PENDING_PHYSICIAN_REVIEW → ADMIN_CLEARED` (GAP-15), and re-enters WS1 at T-09. FM-A-5 runs again. Audit-first ordering holds. Output is `status: approved` with `authorized_by: PHYSICIAN_DETERMINATION` and the complete extended audit trail.

**What to say for the HITL loop:**  
"Path 2a showed the agent escalating and handing off. Path 2b closes the loop — the physician sees the formatted packet the agent prepared, picks ADMIN_CONFIRMED, and the system writes a PHYSICIAN_ADMIN_CONFIRMED audit entry with delegation_tier HUMAN_DECIDES, transitions back to ADMIN_CLEARED, and re-enters T-09. The same FM-A-5 hard stop and audit-first ordering apply — there's no separate payment path for physician-approved claims. The audit trail shows who made the determination and when."

**Key fields to point out after Step 2a:**
- `"status": "escalated"`, `"classification": "uncertain"`, `"confidence": 0.48`
- `"escalation_reason"` — names the contradictory signals
- `"audit_trail"` — 5 COMMITTED entries; `payment_approved` absent

**Key fields to point out after Step 2b (ADMIN_CONFIRMED):**
- `"status": "approved"`, `"payment_amount": 85.0`
- `"authorized_by": "PHYSICIAN_DETERMINATION"` — distinguishes physician-approved from classifier-cleared
- `"audit_trail"` — 8 entries: 5 restored + `physician_admin_confirmed [COMMITTED]` + `payment_approved [COMMITTED]`

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

## Path 4 — End-to-end: raw claim file → Intake parse → WS1 adjudication

**What this shows:** The full pipeline starting from a raw claim file exactly as received from a provider or clearinghouse — no pre-normalization. The Intake Agent parses the raw format into a NormalizedClaimInput, then WS1 adjudicates it. Three stages printed: raw content preview, normalized record, adjudication result.

**API key required for Stage 3.** Use `--skip-ws1` to show Stages 1 + 2 only (no API key needed).

```bash
# EDI 837P — approved outcome (99214 office visit, Z00.00 wellness, Physician MD — all signals agree)
python run_e2e_demo.py --file "../Capstone-A-Claims-Pack/edi-837p/CLM-2026-1000804.edi"

# Portal JSON — escalation outcome (97110 therapeutic exercises + bronchitis/headache — procedure/diagnosis mismatch)
python run_e2e_demo.py --file "../Capstone-A-Claims-Pack/portal-json/CLM-2026-1001201.json"

# Stages 1 + 2 only (no API key needed):
python run_e2e_demo.py --file "../Capstone-A-Claims-Pack/edi-837p/CLM-2026-1000804.edi" --skip-ws1
```

**What to say:**

"Everything shown in Paths 1–3 started from a pre-normalized fixture. Path 4 starts from a raw file exactly as the clearinghouse would deliver it.

Run the EDI first: CLM-2026-1000804 is a 99214 office visit, Z00.00 wellness exam, Physician MD. All three signals agree — the classifier returns admin above threshold and the claim is approved. Stage 1 shows the raw EDI segments. Stage 2 is the Intake Agent parsing them into a NormalizedClaimInput. Stage 3 is the full WS1 pipeline on that normalized record.

Then run the Portal JSON: CLM-2026-1001201 has CPT 97110 (therapeutic exercises) with bronchitis and headache diagnoses — a procedure/diagnosis mismatch. The classifier flags it as uncertain or clinical and escalates. Same pipeline, different outcome, different format.

The point: WS1 is completely format-agnostic. The same pipeline runs regardless of whether the input was EDI or portal JSON. The Intake Agent's job is to make every claim look identical before it reaches WS1."

**Key fields to point out — EDI (CLM-2026-1000804, approved):**

Stage 1 (raw): `ISA`, `GS`, `ST`, `CLM` segments — structured but not human-readable  
Stage 2 (normalized): `source_format: EDI_837P`, `procedure_codes: [99214]`, `diagnosis_codes: [Z0000]`, `provider_specialty: Physician (MD)`  
Stage 3: `status: approved`, `payment_amount: 85.0`, full audit trail

**Key fields to point out — Portal JSON (CLM-2026-1001201, escalated):**

Stage 1 (raw): human-readable JSON, but different schema from NormalizedClaimInput  
Stage 2 (normalized): `source_format: PORTAL_FORM`, `procedure_codes: [97110]`, `diagnosis_codes: [J20.9, R51.9]`  
Stage 3: `status: escalated`, `escalation_reason` names the mismatch — 97110 with bronchitis/headache has no clinical logic  

**Format coverage answer (if asked here):**

"The two parsers shown — EDI 837P and Portal JSON — cover 70% of intake volume on their own. EDI 837I adds another 10%. All three Tier 1 parsers are validated against the full 1,493-file corpus. The remaining 20% — CMS-1500 OCR, FHIR R4, email, fax, exception notes — are Wave 1 Intake Agent scope and not yet built. That gap is named and documented."

---

## Optional — run all 6 tests in sequence to close the demo

```bash
pytest tests/ -v
```

Shows all six paths in ~2 seconds: happy path, HITL escalation, uncertain classification, eligibility discrepancy stub, governance hard stop, and physician-approved HITL path (GAP-15).

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
| `pytest` pre-check (all 6 pass) | ~15 sec |
| Path 1 — happy path | ~30 sec to run, ~60 sec to explain |
| Path 2a — uncertain escalation | ~30 sec to run, ~30 sec to explain |
| Path 2b — HITL reviewer loop (ADMIN_CONFIRMED) | ~30 sec interactive, ~60 sec to explain |
| Path 3 — governance hard stop test | ~15 sec to run, ~60 sec to explain |
| Path 4 — end-to-end raw file (optional) | ~30 sec to run, ~60 sec to explain |
| Wrap + format coverage question | ~60 sec |
| **Total (Paths 1–3 including HITL loop)** | **~5 min** |
| **Total (with Path 4)** | **~7 min** |

**Note:** Path 4 is the optional add-on for coaches who ask to see the end-to-end flow. Run it after Path 3 if time allows, or lead with it if the coach specifically asks. Paths 1–3 are the primary demo — they cover the three required paths (happy path, escalation, governance hard stop) and run cleanly in under 5 minutes.
