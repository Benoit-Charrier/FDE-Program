# Prompt: Deliverable D7 — Validation Plan

## Scenario (read this first)
See `Scenario/scenario_context.md` for the full scenario, work streams, tooling, and named-systems guidance. Do not invent numbers, systems, or constraints not present in the scenario. Every number you use must trace back to the scenario or be explicitly labelled as an assumption.

**Agent context:** Write the validation plan for the WS1 Administrative Adjudication Agent designed in `Deliverables/D4a_capability_spec.md`. The plan must be consistent with:
- D4a's autonomy matrix (§8), escalation triggers (§7), and failure modes (§6)
- D4_preamble's shared entity definitions (ClaimRecord, AuditLogEntry, EscalationPacket, CalibrationRecord)
- D3's delegation suitability matrix — the specific archetype assignments that must be stress-tested
- The build-loop output: the five spec gaps resolved during the build loop (Q2 procedure_quantities, Q4 required_resolution text, Q9 CalibrationRecord.call_site, GAP-10 governance hard-stop state preservation, GAP-14 GOVERNANCE_VIOLATION trigger_type) and the remaining open assumptions
- The hard stops, governance controls, and HITL triggers defined in `Deliverables/D4a_capability_spec.md` §6 (FM-A-1 through FM-A-7)

---

## Scope split — prototype vs. full production

**This is the most important structural decision in the plan.** The validation scope differs materially between the prototype and the full production build. Produce two clearly separated sets of test requirements:

### Prototype scope
The prototype contains one real LLM call (T-08 clinical content classifier via `claude-sonnet-4-6`) and stubs for all other pipeline steps. Prototype validation targets **decision boundary enforcement** — does the agent stop at exactly the right moments?

Prototype validation must cover:
1. **Classifier routing at the threshold boundary** — confidence score at exactly `CLINICAL_CONTENT_CONFIDENCE_THRESHOLD` (0.70); one unit above; one unit below (to six decimal places). The threshold is a configurable parameter, not a hardcoded value — tests must verify the threshold is read from config, not hardcoded.
2. **FM-A-5 governance hard stop** (REQ-A-6) — T-09 must abort and fire ET-07 with `trigger_type = GOVERNANCE_VIOLATION` before any fee schedule call when `ClaimRecord.state != ADMIN_CLEARED`. ClaimRecord.state must be preserved unchanged.
3. **Audit-first ordering** — AuditLogEntry must reach `status = COMMITTED` before the corresponding S-07 state PATCH is issued. If audit write fails, ET-07 fires and no state transition occurs.
4. **CalibrationRecord startup validation** — all 6 startup checks must pass before the first claim is processed; agent must refuse to start with DRAFT state, recall < 0.995, holdout < 500, version mismatch, wrong call_site.
5. **EscalationPacket field completeness** — all three escalation paths (ET-01/02 clinical routing, ET-03 eligibility, ET-07 audit/governance) must carry spec-exact field values: `escalation_trigger_id`, `trigger_type`, `routing_queue`, `required_resolution` (exact string per §7 table), `trigger_signal_values`.

The prototype validation plan does NOT need to cover: integration fidelity against real systems, volume/concurrency, URAC/NCQA compliance documentation, model drift, regulatory drift, or SCOPE-OUT pipeline steps (T-05, T-10, ET-05, ET-06).

### Full production scope (additional requirements)
The production validation plan adds **system integrity** — does the agent stay correct at scale, across failures, over time?

Production validation must additionally cover:
1. **Integration fidelity** — all 16 named systems (S-01 through S-16) tested against contracted APIs, not stubs. S-02 (eligibility) and S-05 (fee schedule) must be tested under unavailability conditions (5xx, timeout after retry).
2. **Volume and concurrency** — 2,000 claims/day peak load; concurrent claim processing must not produce state machine conflicts (409 Conflict responses from S-07 must be handled, not silently swallowed).
3. **URAC/NCQA compliance gate** — every claim escalated to PENDING_PHYSICIAN_REVIEW must have a licensed reviewer sign-off recorded in AuditLogEntry before the claim can transition out of PENDING_PHYSICIAN_REVIEW. The agent must never advance a claim past this state without the sign-off field populated. This is a regulatory hard stop — it cannot be marked as "acceptable variation."
4. **Model accuracy drift** — a golden-set evaluation (minimum 200 claims with ground-truth labels across all three classification outcomes) must run on every LLM model update. If classification agreement with the golden set drops below a threshold defined by the CMO, the model version must be frozen. The CalibrationRecord CMO sign-off workflow must be re-run before the new version can be deployed. Owner: CMO-designated clinical reviewer.
5. **Regulatory drift** — CPT code set updates (annual), ICD-10 code updates (annual), prior auth rule changes (ad hoc), and compact licence changes must trigger a re-validation run against the golden set before the updated rule set is deployed. Mitigation must name: the mechanism for detecting rule changes (e.g., versioned reference data in S-03/S-15 with `valid_through` field), the re-validation cadence, and the sign-off owner.
6. **Cross-agent coherence** — WS1 output format (`EscalationPacket` for ET-01/ET-02) must match WS2 input contract. Any field added to WS1's escalation packet must be reflected in WS2's intake schema. Contract version must be pinned in both specs.
7. **CalibrationRecord lifecycle** — DRAFT → SIGNED workflow must be exercised: a DRAFT record must be rejected at startup; a SIGNED record that is superseded mid-day must not be reloaded mid-session (the record loaded at startup is used for the full session); the superseding record must be picked up at the next agent restart.
8. **Infrastructure SPOF mitigations** — four SPOFs must be named with explicit agent behaviour when unavailable: S-02 (eligibility), S-05 (fee schedule), LLM API (clinical classifier), S-10 (audit log). For each: what does the agent do when the system is unavailable after one retry? What is the maximum acceptable outage duration before coordinator workflow is materially disrupted? Who is notified, within what SLA?
9. **ET-06 contract exception path** — currently SCOPE-OUT in the prototype; production validation must include the stub-to-live promotion path for T-10 and the full ET-06 escalation packet structure.

---

## Your task
Produce a Validation Plan. Be concise. Output file: `Deliverables/D7_validation_plan.md`.

Structure the document with a clear **Prototype scope** section and a **Full production scope (additions)** section within each relevant section — rather than two separate documents. A reader should be able to extract the prototype subset by reading only the prototype rows/sections, and understand the full production requirements by reading all rows/sections.

Reference: `References/spec-ambiguity-vs-builder-mistakes.md` — use the failure taxonomy (spec ambiguity / builder misread / design gap / acceptable variation) to categorise every failure mode you identify.

---

## What strong looks like

A strong validation plan covers four dimensions simultaneously. A plan that addresses fewer than four is incomplete.

1. **Accuracy + edge cases** — the plan tests not just the happy path but the cases that sit exactly at decision boundaries: a confidence score at exactly `CLINICAL_CONTENT_CONFIDENCE_THRESHOLD` (0.70), a prior auth unit count at exactly `PRIOR_AUTH_UNIT_TOLERANCE_PCT` (15%), a CalibrationRecord with `recall_achieved = 0.995` (the minimum), an eligibility check where S-02 returns a partial match. Each edge case specifies the input field values, the expected branch, and the observable output that proves the correct branch fired — not prose describing expected behaviour.

2. **Failure modes** — the plan names quiet failures explicitly: cases where the agent produces output, no exception is raised, no human is alerted, but the output is wrong. Each failure mode names the specific mechanism (not "classification error" — the precise condition, e.g., "classifier returns admin at confidence 0.71 for a claim that requires medical necessity determination because the procedure code is used in both admin and clinical workflows and the provider specialty is ambiguous"), what was written or omitted, why no one notices immediately, and the specific detection check (field name, threshold, person, schedule).

3. **Compliance risk** — the plan names every regulatory constraint the agent can violate silently: a claim advanced through the admin path that contains a procedure requiring medical necessity review per URAC/NCQA criteria, a payment calculated without a prior CMO-signed CalibrationRecord, an EscalationPacket delivered to the wrong queue (EXCEPTION_PROCESSOR instead of PHYSICIAN_HITL) because trigger_type was wrong. Each compliance risk has a detection check and a mitigation strategy — not just a flag that the risk exists.

4. **Infrastructure failure modes with named mitigations** — a strong plan names the following four specifically; a plan that omits any of them is missing a production risk category:

   - **LLM API rate limits and model versioning** — the clinical classifier (T-08) calls `claude-sonnet-4-6` for every claim on the admin path. At 2,000 claims/day with potential batching, rate limits may cause T-08 to timeout. Additionally, if Anthropic updates `claude-sonnet-4-6`, the classifier's output distribution may shift without any code change, causing claims that previously routed correctly to route incorrectly. Mitigation must name: the retry and backoff policy for T-08 timeouts, the golden-set evaluation cadence triggered on model updates, the alert threshold (if agreement with golden set drops below X%, freeze the model version and notify CMO), and who owns the threshold review.
   - **Regulatory drift** — ICD-10 and CPT code sets update annually; prior auth requirement lists change ad hoc; URAC/NCQA accreditation criteria evolve. The clinical classifier's behaviour for specific code combinations may be correct today and incorrect after a code set update — without any change to the agent code. Mitigation must name: the mechanism for detecting code set changes (versioned reference data with `valid_through` field in S-03/S-15), the re-validation cadence against the golden set, and the sign-off owner before the updated reference data is deployed.
   - **CalibrationRecord lifecycle** — the CalibrationRecord loaded at startup governs all routing decisions for that session. If the CMO revokes or supersedes the CalibrationRecord mid-session (e.g., a precision issue is discovered), the agent continues using the invalidated record until the next restart. Mitigation must name: whether the agent polls for CalibrationRecord revocation during a session or only at startup, the maximum acceptable exposure window between revocation and agent shutdown, and who initiates the shutdown.
   - **Single points of failure** — the agent has at least four SPOFs: S-02 (member eligibility — all eligibility checks block if unavailable), S-05 (fee schedule — all payment calculations block), the LLM API (all clinical routing blocks — the prototype would fail open or closed depending on error handling), and S-10 (audit log — audit-first ordering means all claims block if S-10 is unavailable). Each SPOF must be named with: the agent behaviour when unavailable after one retry (graceful degrade, block, fallback to cached data with staleness flag), the maximum acceptable outage duration before claims processing is materially disrupted, and the alert path (who is notified, within what SLA).

**Anti-patterns to avoid:**
- A validation plan that names risk categories but does not provide specific mitigations is a risk register, not a validation plan.
- "Monitor logs" and "review periodically" are not mitigations — name the field, threshold, person, and schedule.
- A compliance risk entry that says "the agent may route a clinical claim through the admin path" without specifying the detection check (e.g., "spot audit of 5% of APPROVED claims against CMO-reviewed clinical criteria, reviewed by Dr. Marcus Webb's team monthly") and the recovery path is incomplete.
- Prototype-scope tests that reference real system integrations (S-02 through S-16) — the prototype uses stubs; tests must mock at the stub boundary, not at the API boundary.

---

## Required structure

### 0. Executive summary
Three bullet points, written first. Each bullet is one sentence. Cover in order:
1. The validation approach in one sentence — how correctness is confirmed on the autonomous path and how silent failure is detected (name the specific field or signal, not "monitoring")
2. The delegation boundary being stress-tested in S-3 — what the cheaper implementation would build and why that is wrong
3. The highest-risk quiet failure — the specific mechanism by which the agent produces wrong output with no exception raised, and what detects it

This section must be self-contained — a reader who reads only this section should understand how the agent proves it is right, where the hardest boundary test is, and what the most dangerous undetected failure looks like.

### 0b. Table of contents
List all sections by number and title as markdown anchor links, in order. Generate this after the full document is written — section titles must match exactly. Format each entry as `[N. Section title](#n-section-title)` using lowercase and hyphens for spaces.

---

### 1. Validation philosophy
One paragraph maximum. Answer two questions — both must be answered explicitly:
- How do you confirm the agent is right on the cases it handles autonomously?
- How do you detect the agent is wrong — especially when it fails silently, with no exception raised and no human immediately notified?

Do not write generic statements about "monitoring" or "logging." Name the specific field, the specific threshold, the specific person or queue that receives the alert, and the SLA for response. Distinguish prototype and production detection mechanisms where they differ.

---

### 2. Test scenarios

Produce exactly three scenarios. Each must use the following structure:

| Field | Content |
|-------|---------|
| **Scenario ID** | S-1 / S-2 / S-3 |
| **Name** | A specific descriptive name — not "happy path" or "failure mode" |
| **Type** | Happy path / Edge case / Failure mode |
| **Scope** | Prototype / Full production / Both |
| **Delegation boundary tested** | Name the specific archetype assignment from D3/D4a being stressed — the claim that this step is AGENT_ALONE, or this trigger pushes to HITL, or this action is HUMAN_DECIDES |
| **Input** | Describe the specific ClaimRecord fields and values the agent receives. Include numeric values (confidence scores, threshold values, state values, field counts). Do not describe inputs generically — name the field values, thresholds, and the condition that makes this case non-standard |
| **Expected agent behaviour** | Step-by-step: what does the agent do at each decision point in the pipeline? What does it write, enqueue, flag, or halt? |
| **Pass criteria** | Observable outputs that confirm correct behaviour — name the field, the value, the queue entry, the AuditLogEntry action, the EscalationPacket field |
| **Failure signal** | What does wrong look like — not the exception, but the quiet wrong: what would be written, enqueued, or omitted that no one would notice without a specific check? |

The three scenarios must span:

1. **Happy path (S-1)** — the agent operates fully autonomously end-to-end. All pipeline conditions met (eligibility confirmed, codes valid, prior auth present, clinical classifier returns admin above threshold), no HITL triggered, APPROVED state written to S-07 with payment_amount, complete AuditLogEntry trail committed. This test must also verify that the autonomous path is not broken by defensive coding added to handle edge cases (e.g., FM-A-5 check must not prevent ADMIN_CLEARED claims from reaching T-09).

2. **Edge case (S-2)** — a ClaimRecord with `confidence_score` at exactly `CLINICAL_CONTENT_CONFIDENCE_THRESHOLD` (0.70). The test must verify that the threshold comparison is implemented as `confidence >= threshold` (inclusive, not exclusive) per D4a §6 D-A-4 — the cheaper implementation would use `>` and this claim would incorrectly escalate to ET-02 at exactly 0.70. The test must verify the exact comparison operator, not just the direction.

3. **Delegation boundary failure (S-3)** — design the scenario so that a coding agent reading only D4a could reasonably implement T-09 without the FM-A-5 pre-condition check (the cheapest option: skip the state guard and call `get_payment_amount()` directly). Describe explicitly: (a) what the coding agent would build if it defaulted to the cheaper implementation, (b) why that implementation is wrong per REQ-A-6 and URAC/NCQA governance requirements, and (c) why the test fails if the cheaper implementation was built. The test fixture must inject a ClaimRecord with `state = PENDING_PHYSICIAN_REVIEW` directly into the T-09 entry point, bypassing the routing step.

---

### 3. Quiet failure catalogue

List at least 4 failure modes where the agent produces output, no exception is raised, and no human is immediately alerted — but the output is wrong. Label each entry as **[P]** (prototype scope), **[PROD]** (production only), or **[BOTH]**.

| QF ID | Scope | Mechanism | What was written (or not written) | Why no one notices immediately | Detection check | Taxonomy category |
|-------|-------|-----------|-----------------------------------|-------------------------------|-----------------|-------------------|
| QF-1 | | | | | | spec ambiguity / builder misread / design gap / acceptable variation |
| QF-2 | | | | | | |
| QF-3 | | | | | | |
| QF-4 | | | | | | |

Suggested candidates (do not copy verbatim — each entry must have the specific mechanism, not a label):
- Classifier returns admin at confidence 0.71 for a claim that requires medical necessity review: the three signals are ambiguous but the model's confidence is above threshold, so no escalation fires and the claim auto-approves
- GOVERNANCE_VIOLATION ET-07 fires but the exception processor routes it to the audit reconciliation queue (not the governance incident queue) because trigger_type was AUDIT_FAILURE in the first implementation — the spec gap was fixed, but the integration contract with S-09 was never updated
- CalibrationRecord startup validation passes at agent start, but the CalibrationRecord is superseded by the CMO 30 minutes into the session — the agent continues routing against the invalidated calibration for the remainder of the session
- Prior auth tolerance arithmetic accepts a claim with 16% unit excess because PRIOR_AUTH_UNIT_TOLERANCE_PCT was misconfigured as 0.16 (a fraction) instead of 16 (a percentage), and the comparison is `excess_pct > tolerance_pct` — both evaluate to approximately 0.16 and the comparison is falsely satisfied

**Mechanism** means the specific condition that produced the wrong output — not "classification error," but the precise scenario, field values, and comparison that caused it.

**Detection check** must name a concrete action: a field audit on a named field (e.g., "monthly spot audit of 100 APPROVED claims against ICD-10 clinical criteria by Dr. Webb's team"), a review of override rates against a threshold (e.g., "weekly review: if ET-02 borderline_confidence_flag rate exceeds 5% of admin-path claims, CMO initiates threshold review"), a downstream system rejection, or a periodic check by a named person on a named schedule.

**Taxonomy category** uses the four categories from `References/spec-ambiguity-vs-builder-mistakes.md`. The category tells you where the fix belongs: in the spec, in a re-prompt, in a new test, or in a note that the variation is acceptable.

---

### 4. Build-loop diagnostic test

Write one concrete test — expressed as pytest-style pseudocode — that would detect if the coding agent defaulted to the wrong delegation archetype for the boundary tested in S-3.

The test must include:
- **Fixture:** the exact ClaimRecord field names and values (state, procedure_codes, diagnosis_codes, member_id, plan_id) that reproduce the failure
- **Assertion:** the specific field value, EscalationPacket key, or absence of write that proves the correct archetype was implemented (e.g., `assert result["trigger_type"] == "GOVERNANCE_VIOLATION"`)
- **Anti-assertion:** what the cheaper implementation would produce instead — so the failure mode is unambiguous (e.g., `# cheaper impl would set payment_amount and status=approved`)
- **Taxonomy classification:** is this test catching a spec ambiguity, a builder misread, or a design gap? State which and why. Refer to the specific build-loop finding that first surfaced this gap.

---

### 5. Assumption log

Use this format for every non-trivial claim:

> **Assumption [A1]:** [what you are taking as given]
> **Why it matters:** [what test outcome or detection check it drives]
> **If wrong:** [what breaks — which test passes when it should fail, or which quiet failure goes undetected]
> **Confidence:** low / medium / high

Minimum 2 assumptions, covering at minimum: (a) a numeric threshold not derivable from the scenario (e.g., the golden-set evaluation agreement threshold), and (b) the CalibrationRecord re-validation cadence.

---

## Acceptance criteria (all must pass)

- [ ] Prototype scope and full production scope are clearly separated throughout the document
- [ ] Validation philosophy answers both questions (confirm right AND detect wrong) with specific fields, thresholds, people, and SLAs — and distinguishes prototype from production detection mechanisms
- [ ] Three scenarios present, each with Scope field marked as [P], [PROD], or [Both]
- [ ] S-2 specifies the exact comparison operator (`>=` vs `>`) being tested at the confidence threshold boundary
- [ ] S-3 describes explicitly what the cheaper implementation would build, why it violates REQ-A-6, and why the test fails for the cheaper implementation
- [ ] Quiet failure catalogue has at least 4 entries, each with Scope tag, mechanism (not label), detection check (not generic "monitor"), and taxonomy category
- [ ] Build-loop diagnostic test has a fixture, assertion, anti-assertion, and taxonomy classification citing the specific build-loop finding
- [ ] Every numeric value (confidence threshold, prior auth tolerance, recall minimum, holdout minimum) traces to D4a or the scenario — or is labelled as an assumption
- [ ] Taxonomy categories from `References/spec-ambiguity-vs-builder-mistakes.md` used correctly throughout
- [ ] Four infrastructure failure modes named with agent behaviour on unavailability, maximum acceptable outage duration, and alert path

## Fail signals — do not produce output that contains these

- Scenarios named "happy path," "edge case," or "failure mode" without a specific descriptive name encoding what is being tested
- Pass criteria that describe behaviour in prose without naming a specific field, value, EscalationPacket key, or AuditLogEntry action
- Quiet failure entries where the mechanism is "classification error" or "wrong routing" — name the specific condition (confidence score, comparison operator, field value) that caused it
- Detection checks that say "monitor logs" or "review periodically" without naming who, what field, what threshold, and what schedule
- A delegation boundary failure scenario (S-3) that does not describe what the cheaper implementation would produce and why the test catches it
- Taxonomy categories applied without a one-sentence justification for the categorisation
- Production-scope infrastructure mitigations applied to prototype-scope tests without noting that the prototype uses stubs
