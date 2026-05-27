# D7 — Validation Plan: WS1 Administrative Adjudication Agent

**Engagement:** Greenfield Health Systems — claims processing transformation
**Agent:** WS1 Administrative Adjudication Agent (`D4a_capability_spec.md`)
**Date:** 2026-05-25

---

## 0. Executive summary

- Correctness on the autonomous path is confirmed by asserting that `payment_amount` is only written when `audit_trail` contains `payment_approved [COMMITTED]` and `ClaimRecord.state = APPROVED`, and that `calibration_record_id` in every approved result matches the CMO-signed record loaded at startup; silent failure on the clinical routing boundary is detected by a monthly spot audit of 100 randomly sampled APPROVED claims reviewed against CPT/ICD-10 clinical criteria by Dr. Marcus Webb's team, with any incorrectly auto-approved claim triggering a compliance report to VP Operations within 48 hours.
- S-3 stress-tests the FM-A-5 governance hard stop (REQ-A-6): a cheaper implementation would call `get_payment_amount()` directly after the routing step without checking `ClaimRecord.state = ADMIN_CLEARED`, writing `payment_amount` for a claim that is in `PENDING_PHYSICIAN_REVIEW` — a direct URAC/NCQA violation because a claim subject to physician review would be auto-approved without licensed reviewer sign-off.
- The highest-risk quiet failure is the clinical classifier returning `admin` at confidence 0.71 for a dual-use inpatient procedure code (e.g., CPT 99232 inpatient evaluation billed by a hospitalist for ICD-10 J18.9 pneumonia): confidence is above the 0.70 threshold so no escalation fires, `payment_amount` is written, and the claim auto-approves without physician review — detectable only by the monthly APPROVED-claim spot audit described above.

---

## 0b. Table of contents

- [0. Executive summary](#0-executive-summary)
- [0b. Table of contents](#0b-table-of-contents)
- [1. Validation philosophy](#1-validation-philosophy)
- [2. Test scenarios](#2-test-scenarios)
- [§2b. Pass 2 — Corpus validation](#2b-pass-2--corpus-validation-1493-normalised-tier-1-claims)
- [3. Quiet failure catalogue](#3-quiet-failure-catalogue)
- [4. Build-loop diagnostic test](#4-build-loop-diagnostic-test)
- [5. Assumption log](#5-assumption-log)
- [6. Measured baselines](#6-measured-baselines-from-claims-pack--not-assumptions)
- [7. Live classifier sample — mini validation study](#7-live-classifier-sample--mini-validation-study-2026-05-26)

---

## 1. Validation philosophy

**Prototype:** Validation runs in two passes. **Pass 1 (§2 — scenario fixtures):** four deterministic mocked tests, each targeting a specific delegation boundary — happy path approval, confidence threshold boundary, governance hard stop, and uncertain-classification escalation. **Pass 2 (§2b — corpus validation):** all 1,493 pre-normalised Tier 1 claims from `normalized-tier1/` fed through WS1 to assert structural invariants at population scale. Pass 1 correctness is confirmed by running all three required demo paths with mocked classifier values and asserting exact `EscalationPacket` field values against the §7 required_resolution table — specifically that `escalation_trigger_id ∈ {ET-01, ET-02, ET-03, ET-07}`, `required_resolution` matches the exact spec string, and `payment_amount` is absent from every escalated result. Silent failure is detected by asserting the negative: the `test_governance_hard_stop` test confirms `claim_state_at_escalation != PENDING_HITL_EXCEPTION` and `trigger_type = GOVERNANCE_VIOLATION` for the FM-A-5 path; the `test_uncertain_classification` test confirms `payment_approved` never appears in `audit_trail` for an uncertain claim. The prototype has no "monitor logs" fallback — every failure mode has a deterministic assertion that fails the build.

**Full production (adds):** Silent failure on the clinical routing boundary is detected by a monthly spot audit: Dr. Marcus Webb's team reviews 100 randomly sampled APPROVED claims stratified by procedure code prefix against CPT/ICD-10 clinical criteria; any claim identified as requiring medical necessity review triggers a compliance incident report to VP Operations within 48 hours. The ops dashboard fires an alert within 30 minutes if the rolling 7-day rate of `ET-02 borderline_confidence_flag = true` escalations exceeds 5% of admin-path claims — this is the leading indicator that the confidence threshold needs CMO review before the audit finds misrouted claims. CalibrationRecord integrity is confirmed at each session start; any mismatch between `_CALIBRATION_RECORD.id` and the current S-16 `state = SIGNED` record triggers an immediate halt and ops alert within 5 minutes.

---

## 2. Test scenarios

---

### S-1 — Admin claim processed end-to-end: all gates pass, classifier unambiguous

| Field | Content |
|-------|---------|
| **Scenario ID** | S-1 |
| **Name** | Admin claim processed end-to-end: all gates pass, classifier unambiguous |
| **Type** | Happy path |
| **Scope** | Both (prototype uses mocked classifier; production uses live LLM) |
| **Delegation boundary tested** | T-09 payment calculation is AGENT_LOGS — agent writes `payment_amount` to S-07 without HITL, with VP Operations receiving a daily batch summary. This is the highest-autonomy action in the pipeline; all upstream gates must have passed and T-09 pre-condition check must succeed. |
| **Input** | `CLAIM-ADMIN-01`: `procedure_codes = ["99213"]`, `diagnosis_codes = ["Z00.00"]`, `provider_specialty = "Primary Care Physician"`, `billed_amount = 120.00`, `procedure_quantities = [1]`. Classifier mock: `{"classification": "admin", "confidence": 0.91, "reasoning": "all three signals unambiguously administrative"}`. Eligibility stub: CONFIRMED. Code validity stub: VALID. Prior auth stub: PRESENT_EXACT_MATCH. |
| **Expected agent behaviour** | T-01: NORMALISED → ADMIN_VALIDATING; AuditEntry `CLAIM_INTAKE_VALIDATED [COMMITTED]`. T-02/03: eligibility CONFIRMED; AuditEntry `ELIGIBILITY_CONFIRMED [COMMITTED]`. T-04: code validity VALID; AuditEntry `CODE_VALIDITY_CHECKED [COMMITTED]`. T-06/07: prior auth PRESENT_EXACT_MATCH; AuditEntry `PRIOR_AUTH_CONFIRMED [COMMITTED]`. T-08: ADMIN_VALIDATING → ROUTING; classifier returns admin, confidence 0.91 ≥ 0.70; ROUTING → ADMIN_CLEARED; AuditEntry `CLINICAL_CLASSIFICATION_COMPLETED [COMMITTED]` with `delegation_tier = AGENT_ALONE`. T-09: FM-A-5 check passes (state = ADMIN_CLEARED); ADMIN_CLEARED → PAYMENT_CALCULATING; `get_payment_amount` returns 85.0 (contracted_rate 106.25 × (1 - 0.20)); AuditEntry `PAYMENT_APPROVED [COMMITTED]` written before state PATCH; PAYMENT_CALCULATING → APPROVED; `payment_amount = 85.0` written. |
| **Pass criteria** | `result["status"] == "approved"`. `result["payment_amount"] == 85.0`. `result["calibration_record_id"] == "cal-rec-2026-05-001"`. `result["classification"] == "admin"`. `result["confidence"] == 0.91`. `audit_trail` has exactly 6 entries, all `[COMMITTED]`. `"payment_approved [COMMITTED]"` present. `"escalation_reason"` absent from result. No file written to `escalations/`. |
| **Failure signal** | `payment_amount` written even though an earlier step set `ctx.state` to something other than `PAYMENT_CALCULATING` — state machine was bypassed. Or `audit_trail` contains fewer than 6 COMMITTED entries — an audit write was skipped. Or `payment_amount` present despite an eligibility or prior auth failure — stub guards were not enforced. |

---

### S-2 — Confidence score at exactly the threshold: inclusive boundary enforcement

| Field | Content |
|-------|---------|
| **Scenario ID** | S-2 |
| **Name** | Confidence score at exactly the threshold: inclusive boundary enforcement |
| **Type** | Edge case |
| **Scope** | Both |
| **Delegation boundary tested** | T-08 clinical routing: `AGENT_ALONE` when `classification = admin AND confidence_score ≥ CLINICAL_CONTENT_CONFIDENCE_THRESHOLD`. D4a §6 D-A-4 specifies `≥` (inclusive). A builder implementing `>` (exclusive) would escalate ET-02 at confidence = 0.70 exactly. |
| **Input** | `CLAIM-ADMIN-01` fixture. Classifier mock: `{"classification": "admin", "confidence": 0.70, "reasoning": "direction is clear but one signal has mild ambiguity"}`. All other stubs: nominal (eligibility CONFIRMED, codes VALID, prior auth PRESENT_EXACT_MATCH). `CLINICAL_CONTENT_CONFIDENCE_THRESHOLD = 0.70` (read from `config.py`). |
| **Expected agent behaviour** | T-08: confidence 0.70 evaluated against threshold 0.70. Comparison `0.70 >= 0.70` is True. Approved routing fires. ROUTING → ADMIN_CLEARED. Pipeline continues to T-09. `payment_amount` calculated and written. Claim APPROVED. |
| **Pass criteria** | `result["status"] == "approved"`. `result["payment_amount"] == 85.0`. `result["confidence"] == 0.70`. `"escalation_trigger_id"` absent from result. `"borderline_confidence_flag"` absent. No file written to `escalations/`. |
| **Failure signal** | `result["status"] == "escalated"` with `escalation_trigger_id = ET-02` and `borderline_confidence_flag = True` — indicates builder implemented `>` (strict) instead of `≥` (inclusive). This is the cheapest mistake: Python's `>=` and `>` look identical to a quick reader; a builder who copied a threshold check from memory would likely use `>`. |

---

### S-3 — FM-A-5 governance hard stop: payment rejected for non-ADMIN_CLEARED claim

| Field | Content |
|-------|---------|
| **Scenario ID** | S-3 |
| **Name** | FM-A-5 governance hard stop: payment rejected for non-ADMIN_CLEARED claim |
| **Type** | Failure mode — delegation boundary |
| **Scope** | Both |
| **Delegation boundary tested** | REQ-A-6: T-09 is AGENT_LOGS for APPROVED claims — but only when `ClaimRecord.state = ADMIN_CLEARED` at T-09 entry. T-09 on a non-ADMIN_CLEARED claim is HUMAN_DECIDES (ET-07 fires, exception processor investigates). A builder who implemented T-09 without reading REQ-A-6 would call `get_payment_amount()` directly after the routing step, making T-09 incorrectly AGENT_ALONE for all claims regardless of state. |
| **Input** | `CLAIM-ADMIN-01` fixture. Classifier mock: admin, confidence 0.91. **Injected defect:** `ClaimContext.transition` is patched to corrupt `ctx.state` from `ADMIN_CLEARED` back to `ROUTING` immediately after the ADMIN_CLEARED transition fires — simulating a production scenario where T-09 is invoked independently of the routing step with a non-ADMIN_CLEARED claim. |
| **Expected agent behaviour** | T-09 entry: FM-A-5 pre-condition check reads `ctx.state = ROUTING` (not ADMIN_CLEARED). Check fails. `_fire_et07` called with `trigger_type = GOVERNANCE_VIOLATION`, `preserve_state = True`. `payment_amount` is not calculated; `get_payment_amount()` is not called. `claim_state_at_escalation = ROUTING` (preserved — not overwritten to PENDING_HITL_EXCEPTION per REQ-A-6(c)). EscalationPacket written to `escalations/CLAIM-ADMIN-01.json`. |
| **Pass criteria** | `result["escalation_trigger_id"] == "ET-07"`. `result["trigger_type"] == "GOVERNANCE_VIOLATION"`. `result["status"] == "escalated"`. `"payment_amount"` key absent from result. `result["claim_state_at_escalation"] != "PENDING_HITL_EXCEPTION"` (state preserved). `result["required_resolution"] == "Audit failure: [RECONSTRUCT_AND_CONTINUE / REJECT_CLAIM / ESCALATE_TO_COMPLIANCE]"`. |
| **Failure signal (cheaper implementation)** | A builder who skips the REQ-A-6 pre-condition check calls `get_payment_amount()` unconditionally. Result: `result["status"] == "approved"`, `result["payment_amount"] == 85.0`. No EscalationPacket written. The claim auto-approves. A URAC/NCQA audit would find a payment instruction written for a claim that was never ADMIN_CLEARED — a regulatory violation. The failure is completely silent: no exception, no alert, no queue entry. |
| **Why the cheaper implementation is wrong** | (a) REQ-A-6 is explicit: "This check MUST occur as the first operation of T-09, before any fee schedule lookup or payment arithmetic." (b) A claim in `PENDING_PHYSICIAN_REVIEW` that reaches T-09 without the check would be auto-approved without physician sign-off — violating URAC/NCQA accreditation requirements for medical necessity review. (c) The test fails for the cheaper implementation because `payment_amount` appears in the result when it must be absent. |

---

## §2b. Pass 2 — Corpus validation (1,493 normalised Tier 1 claims)

| Field | Content |
|-------|---------|
| **Pass** | Pass 2 — Corpus validation |
| **Scope** | Prototype |
| **Corpus** | `prototype/normalized-tier1/` — 1,493 pre-parsed `NormalizedClaimInput` JSON files derived from the full Tier 1 Claims Pack population (EDI_837P: 936, PORTAL_FORM: 374, EDI_837I: 183). Source: C13 canonical claim record derivation run against all 1,600 Tier 1 files. The remaining 107 files (6.7%) are excluded — all PARSE_FAILED due to missing `diagnosis_codes`; they are routed to the intake exception queue before reaching WS1. |
| **Tool** | `run_batch.py --dir normalized-tier1` — detects `normalized-*` directory prefix and skips the parser, reading pre-normalised files directly |
| **Mock strategy** | Fixed admin mock applied uniformly: `{"classification": "admin", "confidence": 0.91, "reasoning": "corpus validation — fixed mock"}`. Forces all 1,493 claims down the approval path, making structural assertions fully deterministic. Clinical/uncertain path boundary behaviour is covered by Pass 1 (S-1 through S-3 and `test_hitl_escalation`). |
| **What this validates** | Structural robustness across the full Tier 1 population: canonical field contract holds for all three intake formats; no unhandled exceptions on any of the 1,493 files; payment and audit invariants hold at scale regardless of input variation introduced by the three parsers. |
| **What this does not validate** | Routing accuracy — no golden labels exist for the corpus. Clinical/admin classification accuracy on real claim content requires a labelled evaluation set; that is a production concern (see §1, Full production). |

**Assertions (applied to every result in the batch run):**

| Assertion | What a failure indicates |
|-----------|--------------------------|
| `result["status"] ∈ {"approved", "escalated"}` for every file | An unhandled exception silently swallowed a claim — structural gap not caught by Pass 1 fixtures |
| `result["payment_amount"] > 0` for every `status == "approved"` result | Fee schedule stub does not return a valid amount for some canonical field shape — field contract gap between parsers |
| `"payment_approved [COMMITTED]"` in `result["audit_trail"]` for every `status == "approved"` result | Audit-first ordering violated for some input shape — `payment_amount` written before audit entry committed |
| `"payment_amount"` absent from every `status == "escalated"` result | FM-A-5 guard or escalation path failed to suppress payment for some input shape not represented in Pass 1 |
| `result["calibration_record_id"]` present and non-null for every `status == "approved"` result | Governance chain not traceable for some approved claim — CalibrationRecord field dropped for a specific input shape |
| `source_format ∈ {"EDI_837P", "EDI_837I", "PORTAL_FORM"}` represented across results | Confirms all three Tier 1 intake paths produced structurally valid WS1 input; detects a silent format exclusion |

**Run command:**

```
cd prototype
python run_batch.py --dir normalized-tier1 --limit 0
```

**Pass criteria:** Zero unhandled exceptions; all six assertions above satisfied for every result; all three Tier 1 format strings represented; run completes in under 60 seconds.

**Results — 2026-05-26 (heuristic mock classifier):**

| Metric | Value |
|--------|-------|
| Total processed | 1,493 / 1,493 |
| Approved (admin path) | 975 (65.3%) |
| Escalated — clinical | 276 (18.5%) |
| Escalated — uncertain | 242 (16.2%) |
| Escalated (total) | 518 (34.7%) |
| Unhandled exceptions | 0 |

| Assertion | Result | Violations |
|-----------|--------|------------|
| `status ∈ {approved, escalated}` for all files | PASS | 0 |
| `payment_amount > 0` for all approved | PASS | 0 |
| `payment_approved [COMMITTED]` in audit trail for all approved | PASS | 0 |
| `payment_amount` absent from all escalated | PASS | 0 |
| `calibration_record_id` present on all approved | PASS | 0 |
| All 3 Tier-1 formats represented | PASS | EDI_837P, EDI_837I, PORTAL_FORM all present |

**6/6 assertions pass. Corpus validation complete.**

*Note: the 65/35 approved/escalated split is an artefact of the heuristic classifier's CPT-range rules — surgical codes (10000–69999) route clinical, E&M and lab codes route admin, therapy/misc codes route uncertain. This split does not represent production routing accuracy; it reflects the Claims Pack procedure code distribution against the mock.*

---

## 3. Quiet failure catalogue

| QF ID | Scope | Mechanism | What was written (or not written) | Why no one notices immediately | Detection check | Taxonomy category |
|-------|-------|-----------|-----------------------------------|-------------------------------|-----------------|-------------------|
| QF-1 | [PROD] | Clinical classifier returns `admin` at confidence 0.71 for CPT 99232 (inpatient E&M visit) billed by a hospitalist for ICD-10 J18.9 (pneumonia, unspecified). Confidence is above the 0.70 threshold — the calibration holdout set was outpatient-majority, so the model generalises poorly to inpatient codes above threshold without triggering ET-02. | `payment_amount` written to S-07; `APPROVED` state committed; `AuditLogEntry` with `delegation_tier = AGENT_LOGS` and `calibration_record_id` pointing to the signed record. Everything looks correct in the audit trail. | The claim processes normally, the provider is paid, and no patient harm is immediate. The AuditLogEntry records the classification correctly (admin, 0.71) — the problem is visible only if someone looks at the procedure code and asks "should this have required medical necessity review?" | Monthly spot audit: Dr. Marcus Webb's team reviews 100 randomly sampled APPROVED claims, filtered for inpatient procedure code prefixes (99231-99233, 99291-99292, 99231-99300 inpatient range). Any claim identified as requiring medical necessity review triggers a compliance incident report to VP Operations within 48 hours. Audit owner: CMO office. Schedule: first Monday of each month. | Design gap — the spec requires CalibrationRecord CMO sign-off but does not require a periodic clinical spot audit of auto-approved claims. The governance framework has the calibration gate but lacks the post-deployment audit loop. Fix: add the monthly spot audit requirement to the operational runbook (not to the agent spec). |
| QF-2 | [BOTH] | `GOVERNANCE_VIOLATION` EscalationPacket silently dropped by S-09 because the integration contract was not updated after GAP-14 resolution. S-09's routing rules accept `trigger_type ∈ {ELIGIBILITY_DISCREPANCY, PRIOR_AUTH_MISMATCH, CODING_PLAUSIBILITY, CONTRACT_EXCEPTION, AUDIT_FAILURE}` — `GOVERNANCE_VIOLATION` hits a default handler (or is dropped) and never reaches the exception processor queue. | EscalationPacket written correctly by the agent to S-09 (the agent's behaviour is spec-compliant). No exception raised in agent code. `ClaimRecord.state` correctly preserved. AuditLogEntry written. | The agent produced correct output. The failure is in the integration layer — S-09 discards the packet silently. The exception processor never receives a ticket. The governance incident sits unresolved indefinitely. The agent's audit log shows `ET-07 GOVERNANCE_VIOLATION` but no one on the exception processor team knows. | Weekly S-09 queue audit: any EscalationPacket with `escalation_trigger_id = ET-07` that has `resolution_status != in_review` after 1 hour triggers an ops dashboard alert to VP Operations. **Prerequisite for production deployment:** integration contract with S-09 must be updated to add `GOVERNANCE_VIOLATION` to the accepted `trigger_type` enum — verified by a contract version check in the deployment checklist. | Design gap — GAP-14 was correctly resolved in the agent spec (D4_preamble and D4a) and in the prototype, but the S-09 integration contract in the integration spec was not updated. The fix is not in the agent code; it is in the integration spec and the S-09 routing configuration. |
| QF-3 | [PROD] | CalibrationRecord `cal-rec-2026-05-001` is superseded by the CMO at 10:15am after a precision issue is discovered. The agent loaded the record at startup (9:00am) and caches it in `_CALIBRATION_RECORD` for the full session. Claims processed from 10:15am to session end (e.g., 6:00pm) use an invalidated calibration. `startup_validate()` ran once at import time and is not re-run during the session. | Correctly structured APPROVED results with `calibration_record_id = cal-rec-2026-05-001` (the superseded ID). All AuditLogEntries point to the superseded record. | Revocation is not surfaced to the agent. All output is structurally correct. A regulator reviewing AuditLogEntries post-hoc would find a superseded record ID — but this only becomes visible in a compliance audit, not at processing time. | S-16 must emit a revocation event when a CalibrationRecord transitions from SIGNED to SUPERSEDED. The agent must subscribe to S-16 revocation events (or poll at 5-minute intervals) and halt processing with an immediate ops alert when the loaded record is revoked. Maximum acceptable exposure: 0 claims processed after revocation confirmation. Alert path: ops dashboard within 5 minutes of revocation event; VP Operations and CMO notified. | Design gap — the spec requires CalibrationRecord validation at startup (REQ-A-2) but is silent on mid-session revocation. The startup check is necessary but not sufficient for production deployments that run for hours. Fix: add a revocation detection requirement to REQ-A-2 and §3 CalibrationRecord lifecycle. This is a production-only concern (prototype uses an in-module mock record). |
| QF-4 | [PROD] | `PRIOR_AUTH_UNIT_TOLERANCE_PCT` is misconfigured as `0.15` (decimal fraction) instead of `15` (percentage integer). The tolerance arithmetic computes `excess_pct = (claimed_units - authorized_units) / authorized_units`. For a claim with 4 claimed units vs 3 authorised: `excess_pct = 0.333`. Comparison: `0.333 > 0.15` → True → ET-04 correctly fires. But for a claim with exactly 15% excess (e.g., 23 claimed vs 20 authorised): `excess_pct = 0.15`. Comparison: `0.15 > 0.15` → False → claim routes as TOLERANCE_APPROVED when a strict implementation would also catch it. Worse, if the formula is `excess_pct > tolerance_pct / 100` (interpreting the config as a percentage), then `0.15 > 0.0015` → always True for any excess, causing all partial-match prior auth claims to incorrectly escalate ET-04 regardless of actual excess. | `prior_auth_status = TOLERANCE_APPROVED` written to AuditLogEntry with `delegation_tier = AGENT_LOGS`; claim APPROVED with `payment_amount` written. No exception raised. | The claim processes and payment is calculated. The TOLERANCE_APPROVED state is a valid state — it does not indicate a problem without examining the exact unit counts and the configured tolerance value simultaneously. | Config validation at startup: `PRIOR_AUTH_UNIT_TOLERANCE_PCT` must be in range [1.0, 100.0]; values < 1.0 trigger a startup warning and ops alert ("configured value < 1.0 — may be a fraction instead of percentage; halting until operator confirms"). Monthly audit of all `TOLERANCE_APPROVED` claims: if any claim has `excess_pct` within 0.1% of the configured tolerance, flag for exception team review. Alert owner: VP Operations. | Design gap — D4a §6 defines `PRIOR_AUTH_UNIT_TOLERANCE_PCT` as "float, default 15%" but does not specify the unit (fraction vs percentage), the valid range, or startup validation requirements. The spec must be updated to add: unit (percentage integer, e.g., 15 means 15%), valid range [1, 100], and a startup check that rejects values < 1.0. |

---

## 4. Build-loop diagnostic test

Tests the S-3 delegation boundary: does the builder implement REQ-A-6 (FM-A-5 pre-condition check) or default to the cheaper T-09 implementation that calls `get_payment_amount()` unconditionally?

```python
def test_governance_hard_stop_delegation_boundary():
    """
    Detects if the builder defaulted to the cheaper T-09 implementation:
    calling get_payment_amount() without the FM-A-5 state pre-condition check.

    Cheaper impl: process_claim() calls get_payment_amount() regardless of
        ClaimRecord.state after the routing step completes.
    Correct impl: process_claim() checks ctx.state == "ADMIN_CLEARED" as the
        FIRST operation of T-09 and fires ET-07 (GOVERNANCE_VIOLATION) if not.

    Taxonomy: Builder misread.
        REQ-A-6 explicitly states: "This check MUST occur as the first operation
        of T-09, before any fee schedule lookup or payment arithmetic is performed."
        The spec is unambiguous. A builder who implemented T-09 without reading
        REQ-A-6 would produce the cheaper path — payment writes for non-ADMIN_CLEARED
        claims — which passes all structural validations except this test.
        Surfaced as GAP-10 (state preservation vs overwrite) and resolved as
        GOVERNANCE_VIOLATION trigger_type (GAP-14) in the build loop.
    """
    from agents.ws1_agent import ClaimContext

    claim = _load("CLAIM-ADMIN-01")

    # Patch: corrupt state from ADMIN_CLEARED to ROUTING after the transition fires.
    # Simulates T-09 invoked independently with a non-ADMIN_CLEARED claim.
    original_transition = ClaimContext.transition

    def corrupt_after_admin_cleared(self, to_state, *, from_state):
        original_transition(self, to_state, from_state=from_state)
        if to_state == "ADMIN_CLEARED":
            self.state = "ROUTING"  # inject wrong state at T-09 entry

    _ADMIN_MOCK = {
        "classification": "admin", "confidence": 0.91,
        "reasoning": "all three signals unambiguously administrative",
    }

    with patch("agents.ws1_agent.classify_clinical_content", return_value=_ADMIN_MOCK):
        with patch.object(ClaimContext, "transition", corrupt_after_admin_cleared):
            result = process_claim(claim)

    # --- CORRECT IMPLEMENTATION ASSERTIONS ---

    assert result.get("escalation_trigger_id") == "ET-07", (
        "FM-A-5 must fire ET-07 when ClaimRecord.state != ADMIN_CLEARED at T-09 entry"
    )
    assert result.get("trigger_type") == "GOVERNANCE_VIOLATION", (
        "Governance hard-stop ET-07 must carry GOVERNANCE_VIOLATION, not AUDIT_FAILURE "
        "(GAP-14 resolution: GOVERNANCE_VIOLATION added to EscalationPacket.trigger_type enum)"
    )
    assert result.get("status") == "escalated"
    assert "payment_amount" not in result, (
        "payment_amount must not be written when FM-A-5 hard stop fires"
    )
    # REQ-A-6(c): state preserved — incoming state is the diagnostic signal
    assert result.get("claim_state_at_escalation") != "PENDING_HITL_EXCEPTION", (
        "Governance hard-stop must preserve incoming state, not overwrite it "
        "(GAP-10 resolution: state preservation for GOVERNANCE_VIOLATION path)"
    )

    # --- ANTI-ASSERTIONS: what the cheaper implementation would produce ---
    # cheaper impl skips the state check; calls get_payment_amount() unconditionally:
    #   assert result["status"] == "approved"       # WRONG
    #   assert result["payment_amount"] == 85.0     # WRONG — payment must not be calculated
    #   assert result["trigger_type"] == "AUDIT_FAILURE"  # WRONG — pre-GAP-14 impl
    #   assert result["claim_state_at_escalation"] == "PENDING_HITL_EXCEPTION"  # WRONG
```

**Taxonomy classification:** Builder misread. REQ-A-6 states the check is required "as the first operation of T-09, before any fee schedule lookup." No reasonable reading of REQ-A-6 permits skipping the check — this is not a spec ambiguity. A builder who reached T-09 without reading REQ-A-6, or who read only the D-A-6 payment formula section, would implement the cheaper path. This test would catch that misread deterministically. The GOVERNANCE_VIOLATION assertion additionally catches the pre-GAP-14 implementation (where all ET-07 cases carried AUDIT_FAILURE), confirming both the governance check and the correct trigger_type were implemented.

---

## 5. Assumption log

> **Assumption [A1]:** `CLINICAL_CONTENT_CONFIDENCE_THRESHOLD = 0.70` is the default threshold and the comparison operator is `>=` (inclusive), not `>` (exclusive).
> **Why it matters:** S-2 and the entire ET-02 boundary test depend on the comparison being inclusive. If `>` is used, confidence = 0.70 incorrectly escalates ET-02 rather than approving.
> **If wrong:** S-2 test fails, indicating a builder misread of §6 D-A-4. The spec says "confidence_score ≥ CLINICAL_CONTENT_CONFIDENCE_THRESHOLD" — this is derivable from D4a and is high-confidence, but the test is the backstop.
> **Confidence:** High (derivable from D4a §6 D-A-4; stated explicitly as `≥`)

> **Assumption [A2]:** The golden-set evaluation agreement threshold (production model drift gate) is 95% — if classifier agreement with the golden set drops below 95%, the model version is frozen and CMO review is triggered.
> **Why it matters:** QF-1 detection relies on a golden-set evaluation cadence. If the threshold is set too low (e.g., 80%), drift that produces misrouted claims would not trigger the freeze.
> **If wrong:** Model drift proceeds silently until the monthly spot audit catches it — a lag of up to 30 days. The 95% assumption should be validated with Dr. Marcus Webb before the production calibration framework is designed.
> **Confidence:** Low — not derivable from the scenario. This is an FDE assumption pending CMO input.

> **Assumption [A3]:** `PRIOR_AUTH_UNIT_TOLERANCE_PCT` is expressed as a percentage integer (e.g., `15` meaning 15%), not a decimal fraction (`0.15`). The tolerance arithmetic divides by 100 before comparison.
> **Why it matters:** QF-4 is only detectable at startup if the config validation rejects values < 1.0. If the spec intends a decimal, the detection logic changes.
> **If wrong:** QF-4 detection fails — the startup validation would incorrectly halt for a valid fractional configuration.
> **Confidence:** Medium — D4a §6 says "default 15%" which implies an integer, but the unit is never stated explicitly. Spec update required (noted in QF-4 detection check).

> **Assumption [A4]:** The CalibrationRecord revocation polling interval is 5 minutes in production.
> **Why it matters:** QF-3 mitigation names this interval as the maximum exposure window between CMO revocation and agent halt. A 5-minute window means at most ~17 claims (at 2,000/day) could be processed against a revoked record.
> **If wrong:** Longer intervals increase exposure. The interval must be agreed with the CMO and CMO office before the CalibrationRecord lifecycle requirement is added to the spec.
> **Confidence:** Low — not derivable from the scenario. Provisional value pending CMO and IT input on S-16 event capability.

---

## 6. Measured baselines (from Claims Pack — not assumptions)

These are empirical facts derived from running the C13 canonical claim record derivation against the full Claims Pack. They ground §2b corpus scope and replace any estimated parse-failure rates.

| Baseline | Value | Source | Relevance to D7 |
|----------|-------|--------|-----------------|
| Tier 1 parse success rate | 93.3% (1,493 / 1,600 files) | C13 derivation run | Defines the Pass 2 corpus size — 1,493 files, not 1,600 |
| Tier 1 PARSE_FAILED rate | 6.7% (107 / 1,600 files) | C13 derivation run | All 107 failures due to missing `diagnosis_codes`; these claims are routed to the intake exception queue and never reach WS1 — not a WS1 failure mode |
| CMS-1500 OCR PARSE_FAILED rate | 41% | C13 derivation run | CMS-1500 is deferred (not Tier 1); not relevant to WS1 Pass 2 corpus |
| Tier 1 format distribution in corpus | EDI_837P: 936 (62.7%), PORTAL_FORM: 374 (25.1%), EDI_837I: 183 (12.3%) | C13 derivation run | Expected distribution for the "format coverage" assertion in §2b |

---

## 7. Live classifier sample — mini validation study (2026-05-26)

**Method:** 30 claims sampled from `normalized-tier1/` (10 per Tier 1 format), run through the live Sonnet 4.6 classifier via `classify_clinical_content()`. FDE manually labelled each claim admin / clinical / uncertain based on CPT code, ICD-10 chapter, and provider specialty. Labels compared to classifier output.

**Sample:** random seed 42, 10 × EDI_837P + 10 × EDI_837I + 10 × PORTAL_FORM.

**Agreement: 15 / 30 (50%)**

| | LLM: admin | LLM: uncertain | LLM: clinical |
|---|---|---|---|
| **Manual: admin** | 0 | 10 | 2 |
| **Manual: uncertain** | 0 | 11 | 0 |
| **Manual: clinical** | 0 | 4 | 3 |

**Key findings:**

**1. Zero dangerous misses.** No case where LLM returned `admin` and manual label was `clinical`. The failure mode the design most needs to prevent — silently approving a claim that requires physician review — did not appear in this sample.

**2. LLM over-labels as `uncertain`: 22/30 (73%).** Many claims with obvious CPT/ICD-10 mismatches (chest X-ray for headache, HbA1c for URI, immunization for headache, epidural injection for dermatitis, MRI lumbar for annual wellness) were returned as `uncertain` rather than being separated into "coding plausibility issue" (ET-05) versus "clinical content issue" (ET-01/ET-02). The classifier correctly detects something is wrong but routes to HITL rather than discriminating the issue type. These are 10 of the 15 disagreements.

**3. Two over-routes to `clinical`.** Claims 20 (99205 + hyperlipidemia, hospital) and 28 (85025 CBC + coronary artery disease, Family Medicine) — the LLM appears to anchor on the serious underlying diagnosis and escalate a routine office visit or lab to clinical review. Conservative but burdens the physician queue.

**4. Four under-routes from `clinical` to `uncertain`.** Claims 17 (64483 epidural + URI), 18 (72148 MRI lumbar + annual wellness), 21 (72148 MRI lumbar + annual wellness), 24 (64483 epidural + dermatitis). Manual label: clinical (interventional procedure or imaging requiring medical necessity determination). LLM label: uncertain. Outcome is the same — all four still escalate to physician HITL — but the EscalationPacket reasoning cites classification uncertainty rather than clinical procedure type, degrading signal quality for the physician reviewer.

**Confidence scores are working correctly.** All 22 uncertain labels carried confidence ~0.41–0.52, well below the 0.70 threshold. All clinical labels carried confidence 0.72–0.92. The threshold correctly prevents auto-approval even when the uncertain label may be imprecise.

**Implication for A2 (golden-set composition):** The CalibrationRecord golden set must include deliberate CPT/ICD-10 mismatch cases to measure how the classifier separates coding plausibility issues (ET-05) from genuine clinical content (ET-01/ET-02). A golden set drawn only from well-formed claims will not surface the over-labelling-as-uncertain pattern observed here. This should be a named requirement in the clinical content definition workshop (C10 precondition 1).
