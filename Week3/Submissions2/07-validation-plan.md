# Deliverable D7 — Validation Plan: WS1 Intake & WS2 Matching Agent

*Sources: D4a (WS1 spec + §12 failure modes), D4b (WS2 spec), D5 (build-loop response memo), D5B (build-loop analysis), D2B (delegation archetypes), scenario_context.md. Every numeric value is traced to one of these sources or labelled as an assumption.*

---

## 0. Executive Summary

- The agent is confirmed correct on the autonomous path when a `MatchingBrief` reaches ServiceNow with `status = ADVANCED_TO_WS2`, all six per-field `confidence_score ≥ 0.70` in `audit_log.confidence_scores`, `audit_log.hitl_items = []`, and `facility_id` resolving to a confirmed registry entry; silent failure is detected by a weekly Monday QA audit (owned by QA lead) pulling all briefs auto-accepted with any field confidence in the 0.70–0.79 window, cross-referencing extracted `specialty_required` against coordinator-confirmed final placement specialties, with a >5% mismatch rate as the alert threshold that triggers a calibration freeze before further autonomous processing resumes.

- S-3 stress-tests the WS2-JtD-3 Human Only boundary (D2B §3): the cheaper implementation reads D4b Decision 3's complete ranking algorithm and auto-writes a `PlacementSubmission` with `selected_nurse_id = "NRS-101"` and `approved_by = null` — bypassing coordinator involvement entirely because the ranking algorithm is mechanically complete and D4b contains no explicit halt instruction at that step; the correct implementation writes the ranked `CandidateShortlist` with `status = PENDING_COORDINATOR_REVIEW`, creates a `HITLQueueItem` with `gap_type = CANDIDATE_SELECTION_REQUIRED`, and blocks submission until a coordinator ID populates `approved_by`.

- The highest-risk quiet failure is LLM confidence miscalibration (QF-1): the extraction model self-reports `confidence = 0.71` for `specialty_required = "RN_ICU"` when the facility message uses "step-down ICU" — a term the model maps to ICU by token pattern, not by verified credential scope — the brief clears the confidence gate, advances to WS2 without HITL, the coordinator receives a pre-populated shortlist for the wrong acuity level, and the failure surfaces only when the facility rejects the submitted nurse; the sole detection is the weekly Monday audit cross-referencing 0.70–0.79 confidence briefs against final placement outcomes.

---

## 0b. Table of Contents

- [0. Executive summary](#0-executive-summary)
- [0b. Table of contents](#0b-table-of-contents)
- [1. Validation philosophy](#1-validation-philosophy)
- [2. Test scenarios](#2-test-scenarios)
- [3. Quiet failure catalogue](#3-quiet-failure-catalogue)
- [4. Build-loop diagnostic test](#4-build-loop-diagnostic-test)
- [5. Assumption log](#5-assumption-log)

---

## 1. Validation Philosophy

Correctness on the autonomous path is confirmed by verifying four co-present conditions on every `MatchingBrief` that reaches `status = ADVANCED_TO_WS2`: (1) all six gated fields carry `confidence_score ≥ 0.70` in `audit_log.confidence_scores`; (2) `audit_log.hitl_items` is an empty list, confirming no escalation was created and then bypassed; (3) `facility_id` is non-null and resolves to a confirmed registry entry; and (4) `specialty_required ≠ UNRESOLVED` and `credential_level ≠ UNRESOLVED`, enforcing the D4a §10 guard conditions for the `READY_FOR_REVIEW → ADVANCED_TO_WS2` transition. Silent failure — where the agent writes output with no exception raised and no human notified — is detected through two mechanisms: a scheduled Monday QA audit run by the QA lead that pulls all briefs auto-accepted in the prior week with any field-level confidence in the 0.70–0.79 "barely passed" window, cross-references the extracted `specialty_required` against `placement_specialty_actual` from coordinator outcome records, and triggers a calibration freeze if the mismatch rate on that population exceeds 5% (alert sent to QA lead within one business hour of the weekly run); and a daily HITL rate monitor that alerts the QA lead within one business hour if the rate of briefs routed to HITL drops below 50% of the prior 4-week baseline — a rate collapse signals the confidence gate is admitting briefs it should not, not that intake quality improved.

---

## 2. Test Scenarios

### S-1: All-fields-confident autonomous intake — brief committed to WS2 without human intervention

| Field | Content |
|-------|---------|
| **Scenario ID** | S-1 |
| **Name** | All-fields-confident autonomous intake — brief committed to WS2 without human intervention |
| **Type** | Happy path |
| **Delegation boundary tested** | WS1-JtD-2 parameter extraction (Human-led + Agent Support, D2B §3): D4a §6 Decision 2 defines a confidence gate that allows autonomous advancement when all six gated fields score ≥ 0.70 — an autonomous sub-path within the D2B archetype for clean, high-confidence intake. S-1 tests that this path fires correctly AND that it is not inadvertently broken by defensive coding from spec revision R-7, which removed `urgency` from the confidence gate loop after D5B signal S-7 identified it as a spec ambiguity. |
| **Input** | ServiceNow message: `"St. Francis Memorial - ICU, RN required, BSN+ACLS, shift 2026-06-15 07:00–19:00, ASAP fill"`. Fields: `message_type = STANDARD_SHIFT_REQUEST` (keyword match), `prior_shift_id_present = false`. LLM extraction: `facility_id = "FAC-044"` (WRatio = 0.95 against registry "St. Francis Memorial Hospital"), `unit_type = "ICU"` (confidence 0.91), `specialty_required = "RN_ICU"` (confidence 0.88), `credential_level = "RN"` (confidence 0.85), `shift_datetime_start = "2026-06-15T07:00:00"` (confidence 0.97), `shift_datetime_end = "2026-06-15T19:00:00"` (confidence 0.96), `facility_id` confidence 0.95. All six gated fields ≥ 0.70. `urgency` is classified deterministically as STANDARD (shift datetime > 4h from receipt) — NOT LLM-extracted, NOT in confidence gate loop. |
| **Expected agent behaviour** | (1) `classify_message_type` → `STANDARD_SHIFT_REQUEST`. (2) `classify_urgency` → `STANDARD` (shift > 4h out; deterministic). (3) LLM extraction runs on the eight entity fields; only the six gated fields enter the confidence gate loop — `urgency` is absent from the loop (R-7 applied). (4) `apply_confidence_gate` on six fields → `accepted = True`, `review_flags = []`, `missing_fields = []`. (5) `evaluate_completeness` → `READY_FOR_REVIEW`. (6) Guard conditions checked: `specialty_required ≠ UNRESOLVED`, `credential_level ≠ UNRESOLVED`, `facility_id` resolves. (7) `MatchingBrief.transition_to(ADVANCED_TO_WS2)`. (8) Brief written to ServiceNow. (9) No `HITLQueueItem` created. Audit log written with all six confidence scores and empty `hitl_items`. |
| **Pass criteria** | (a) `brief.status = "ADVANCED_TO_WS2"` in ServiceNow. (b) `brief.facility_id = "FAC-044"`. (c) `brief.audit_log.hitl_items = []`. (d) `audit_log.confidence_scores` contains exactly the six gated fields, all ≥ 0.70. (e) `brief.urgency = "STANDARD"` is present on the entity AND absent from `confidence_scores` — confirms R-7 was applied correctly. (f) No `HITLQueueItem` record exists with `source_brief_id` matching this brief. |
| **Failure signal** | Quiet wrong: `urgency` is incorrectly included in confidence gate (R-7 not applied); `urgency` has no LLM confidence score in the dict (defaults to 0.0 in the gate); brief status becomes `NEEDS_COORDINATOR_INPUT` with `missing_fields = ["urgency"]` — the brief stalls in HITL with a meaningless gap on a deterministically classified field. Coordinator resolves by re-entering "STANDARD." No exception is raised; no one notices the autonomous path is broken; HITL volume inflates permanently for every standard brief. |

---

### S-2: Facility fuzzy match at WRatio threshold boundary — score exactly 80/100

| Field | Content |
|-------|---------|
| **Scenario ID** | S-2 |
| **Name** | Facility fuzzy match at WRatio threshold boundary — score exactly 80/100 |
| **Type** | Edge case |
| **Delegation boundary tested** | WS1-JtD-1 message classification routing sub-step — facility resolution: spec revision R-3 specifies `rapidfuzz.fuzz.WRatio` scorer with threshold ≥ 80/100. The boundary is WRatio = 80 → autonomous resolution (no HITL for `facility_id`) vs. WRatio = 79 → `HITLQueueItem` with `gap_type = MISSING_REQUIRED_FIELD`. S-2 tests that the boundary is implemented as non-strict `≥ 80` using the WRatio scorer — not `> 80`, not a different scorer (ratio, partial_ratio), and not a floating-point comparison that rounds differently. This tests that CLAUDE.md's spec boundary is honoured as written. |
| **Input** | ServiceNow message: `"Metro General Hosp - ER, RN needed, shift 2026-06-20 19:00–07:00"`. Registry entry for `FAC-031`: name = `"Metro General Hospital"`. `rapidfuzz.fuzz.WRatio("Metro General Hosp", "Metro General Hospital") = 80` (see Assumption A2 for caveat). All other fields extracted with confidence ≥ 0.70: `unit_type = "ER"` (0.93), `specialty_required = "RN_ED"` (0.82), `credential_level = "RN"` (0.91), `shift_datetime_start = "2026-06-20T19:00:00"` (0.97), `shift_datetime_end = "2026-06-21T07:00:00"` (0.97). Urgency = STANDARD (7 days out). |
| **Expected agent behaviour** | (1) `classify_message_type` → `STANDARD_SHIFT_REQUEST`. (2) Facility resolver calls `rapidfuzz.fuzz.WRatio("Metro General Hosp", "Metro General Hospital")`; result = 80. (3) Per R-3, score ≥ 80 → facility resolves to `FAC-031`; `facility_resolved = true`; no `HITLQueueItem` for `facility_id`. (4) All six fields pass confidence gate. (5) Brief transitions to `ADVANCED_TO_WS2`. Written to ServiceNow with `facility_id = "FAC-031"`. Audit log records `facility_fuzzy_score = 80` and `facility_resolved = true`. |
| **Pass criteria** | (a) `brief.facility_id = "FAC-031"`. (b) No `HITLQueueItem` with `gap_type = "MISSING_REQUIRED_FIELD"` for `facility_id`. (c) `brief.status = "ADVANCED_TO_WS2"`. (d) `audit_log.facility_fuzzy_score = 80` and `audit_log.facility_resolved = true`. (e) Anti-pass: when the fixture input is changed to a string pair that produces WRatio = 79, a `HITLQueueItem` with `gap_type = MISSING_REQUIRED_FIELD` and `agent_note` referencing `facility_id` must be created and the brief must remain at `NEEDS_COORDINATOR_INPUT`. |
| **Failure signal** | Quiet wrong (under-escalation): strict `> 80` instead of `>= 80` — WRatio = 80 triggers HITL; coordinator manually resolves to `FAC-031`; output is correct but the autonomous path is broken at the boundary; HITL volume inflates permanently for all facilities whose abbreviated names score exactly 80; no alarm fires because the brief eventually resolves. Quiet wrong (over-resolution): wrong scorer used — `partial_ratio` returns 92 for the same pair; a WRatio = 79 case resolves autonomously; a different or ambiguous `facility_id` advances to WS2 with the wrong DNR list and unit profile, no alert raised. |

---

### S-3: WS2 candidate selection as autonomous top-pick — cheaper auto-select bypasses Human Only gate

| Field | Content |
|-------|---------|
| **Scenario ID** | S-3 |
| **Name** | WS2 candidate selection as autonomous top-pick — cheaper auto-select bypasses Human Only gate |
| **Type** | Delegation boundary failure |
| **Delegation boundary tested** | WS2-JtD-3 (optimal candidate selection, Human Only, D2B §3): the agent presents a ranked shortlist and must halt until a coordinator selects. D4b Decision 3 defines a complete ranking algorithm with a tiebreaker sequence across credential score, proximity, and note classification. A coding agent reading only D4b sees a mechanically complete ranking algorithm with no halt instruction — the spec describes "rank the candidates" but not "wait for coordinator selection before proceeding." |
| **Input** | Brief `BRF-2210`: `status = ADVANCED_TO_WS2`, `specialty_required = RN_ICU`, `facility_id = "FAC-044"`, `shift_datetime_start = "2026-06-15T07:00:00"`. Nurse DB returns 3 qualified candidates after HR-1/HR-2/HR-3/HR-4/HR-5 filter: `NRS-101` (ranking_score 0.91, note_classification = NO_NOTES, 12 miles), `NRS-087` (ranking_score 0.87, note_classification = NEUTRAL, 8 miles), `NRS-203` (ranking_score 0.78, note_classification = NO_NOTES, 3 miles). D4b Decision 3 tiebreaker sequence produces ranked order: NRS-101 > NRS-087 > NRS-203. |
| **Expected agent behaviour** | (1) Agent generates `CandidateShortlist`, writes to ServiceNow with `shortlist_id = "SL-2210"`, `status = PENDING_COORDINATOR_REVIEW`. (2) Agent creates `HITLQueueItem`: `gap_type = CANDIDATE_SELECTION_REQUIRED`, `shortlist_id = "SL-2210"`, `sla_deadline = now + 30 min`. (3) Agent halts — no `PlacementSubmission` is written. (4) Coordinator opens HITL queue, reviews ranked shortlist, selects NRS-101, writes `approved_by = "COORD-05"` to the shortlist record. (5) Agent detects `approved_by` is populated, transitions shortlist to `SELECTION_CONFIRMED`, creates `PlacementSubmission` with `selected_nurse_id = "NRS-101"` and `approved_by = "COORD-05"`. |
| **Pass criteria** | (a) After Steps 1–2: `CandidateShortlist.status = "PENDING_COORDINATOR_REVIEW"`. (b) `HITLQueueItem` exists with `gap_type = "CANDIDATE_SELECTION_REQUIRED"` and `shortlist_id = "SL-2210"`. (c) No `PlacementSubmission` record exists for `brief_id = "BRF-2210"` before coordinator action. (d) After coordinator action: `PlacementSubmission.selected_nurse_id = "NRS-101"` and `PlacementSubmission.approved_by = "COORD-05"`. |
| **Failure signal** | (a) *What the cheaper implementation builds:* agent reads D4b Decision 3, ranks candidates, selects NRS-101 (highest score 0.91), writes `PlacementSubmission` with `selected_nurse_id = "NRS-101"`, `approved_by = null` (field absent or set to `"agent"`), and dispatches to FAC-044 immediately. No `HITLQueueItem` is created. (b) *Why it is wrong:* WS2-JtD-3 is Human Only in D2B §3 because the coordinator's tacit knowledge about NRS-101's history with FAC-044 — not encoded in any structured field — must be applied. This replicates the failed recommendation engine pattern (D2B §3 anti-pattern check; D3 ADR-1). (c) *Why the test fails:* criterion (c) is violated — a `PlacementSubmission` exists before any coordinator action; `approved_by` is null or `"agent"`; no `HITLQueueItem` with `gap_type = CANDIDATE_SELECTION_REQUIRED` is present. The facility may receive a nurse the coordinator would have overridden, with no audit trail of human approval. |

---

## 3. Quiet Failure Catalogue

| QF ID | Mechanism | What was written (or not written) | Why no one notices immediately | Detection check | Taxonomy |
|-------|-----------|----------------------------------|-------------------------------|-----------------|----------|
| QF-1 | LLM self-reports `confidence = 0.71` for `specialty_required = "RN_ICU"` on a message using "step-down ICU" — a unit the model maps to ICU by textual token similarity, not by clinical credential scope; the model has no access to the facility's unit taxonomy | `brief.specialty_required = "RN_ICU"`, `confidence = 0.71`, `status = ADVANCED_TO_WS2`; no `HITLQueueItem` created for specialty | Brief enters WS2 normally; coordinator receives a pre-populated ICU shortlist; selects without auditing the extraction because the confidence appears sufficient; failure surfaces only when the facility rejects the submitted nurse for wrong acuity | QA lead runs Monday audit: pull all briefs auto-accepted with `specialty_confidence` in 0.70–0.79 range during prior week; cross-reference extracted `specialty_required` against `placement_specialty_actual` from coordinator outcome records; alert if mismatch rate >5% on this population. *Compliance mitigation:* HITL auto-trigger for any `specialty_confidence < 0.80` on briefs where `unit_type` contains "step-down," "SDU," "PCU," or equivalent intermediate-acuity terms — these terms are systematically ambiguous. | design gap — D4a §6 Decision 2 defines the 0.70 threshold precisely but is entirely silent on the calibration mechanism, recalibration trigger, and golden-set validation cadence; the spec is precise about what was stated and missing an entire production-readiness category; systematic over-confidence goes undetected without the Monday audit |
| QF-2 | LLM used for profile note classification (D4b §6 Decision 2, WS2-T8) is updated by provider; note `"coordinator flagged: do not send to FAC-044 without prior approval"` — previously `RISK_SIGNAL` — is now classified `NEUTRAL` because the updated model weights facility-restriction language as advisory rather than blocking | `shortlist_candidate.note_classification = "NEUTRAL"` written to `CandidateShortlist`; no HITL flag for manual note review; coordinator is not prompted to read the raw note | Shortlist presented with NRS-101 at `note_classification = NEUTRAL`; coordinator selects without reviewing the raw note text (accessible only via drill-down, not surfaced inline); nurse submitted to FAC-044; facility relationship incident | On every model update: run 50-note golden-set evaluation (25 RISK_SIGNAL, 15 NEUTRAL, 10 BLOCKING ground-truth labels — see Assumption A1); if any RISK_SIGNAL gold label is classified NEUTRAL or BLOCKING is classified NEUTRAL, freeze model version immediately; alert ML team within 24h. `audit_log.model_version` pinned per classification run. *Alert path:* ML team notified via automated alert; QA lead receives daily model_version consistency report. | design gap — D4b §6 Decision 2 specifies the classification prompt and label categories but defines no drift detection mechanism, model version pinning requirement, or golden-set evaluation cadence |
| QF-3 | Orchestration polling loop checks `brief.status` at T=0 (status = `READY_FOR_REVIEW`); HITL factory fires at T=+0.3s for an unresolved urgency field; the WS2 advancement trigger fires at T=+0.2s against the already-set `READY_FOR_REVIEW` status; brief advances before the `HITLQueueItem` is written | `brief.status = "ADVANCED_TO_WS2"` written; `HITLQueueItem` created 0.1s later for the same `source_brief_id` with `status = OPEN`; brief is simultaneously in WS2 pipeline and has an unresolved open HITL item | WS2 receives brief and begins matching; coordinator queue shows an OPEN HITL item for this brief_id but the brief is already in the matching pipeline; neither system checks the other's state | WS2 entry-point pre-check: query `HITLQueueItem WHERE source_brief_id = brief_id AND status NOT IN ('RESOLVED', 'EXPIRED')`; if any exist, reject and alert coordinator queue within 10 min with `HITL_NOT_RESOLVED` error. Additionally, daily query: `MatchingBriefs WHERE status = ADVANCED_TO_WS2` joined with open HITLQueueItems — count must be 0; any non-zero result triggers immediate supervisor alert. *Compliance note:* a brief that advances without HITL resolution has an incomplete audit trail — the coordinator could not have reviewed the flagged field — which undermines the HITL record required by D4a §13. | design gap — D4a §8 autonomy matrix notes enforcement is "procedure-dependent"; D4a §10 state model defines the guard conditions but specifies no cross-state consistency check at the WS2 entry point |
| QF-4 | Nurse DB REST API is unavailable (30s timeout, 3 retries with exponential backoff) at shortlist generation; agent falls back to 4-hour-cached nurse profiles; the DNR list is not cached (only profiles are); null DNR response is treated as "no DNR record" (pass) rather than "list unavailable" (block); NRS-155, added to FAC-044's DNR list 6 hours ago, appears in the shortlist with `dnr_status = "CLEAR"` | `shortlist_candidate.dnr_status = "CLEAR"` written for NRS-155 (correct value is `"EXCLUDED"`); NRS-155 appears in the coordinator shortlist with no exclusion flag | Coordinator selects NRS-155 without knowing the DNR check was performed against a null list; `PlacementSubmission` is created and dispatched; facility may reject the placement or — worse — accept and discover the DNR issue at shift start | Pre-shortlist validation: all candidates must have `dnr_status ∈ {"CLEAR", "EXCLUDED", "UNAVAILABLE"}`; any candidate with `dnr_status = "UNAVAILABLE"` must be removed from the shortlist and a `HITLQueueItem` created with `gap_type = DNR_CHECK_REQUIRED`; submission gate must reject any `PlacementSubmission` where `dnr_status ≠ "CLEAR"`. *SPOF mitigation:* Nurse DB unavailability triggers: (a) coordinator SMS alert within 5 min; (b) all new shortlist generation blocks until DB recovers; (c) max acceptable outage before coordinator workflow materially disrupted: 15 minutes. | design gap — D4b §6 Decision 1 specifies HR-4 DNR check must be performed; fallback behavior when the DNR list returns null is not specified; null is not distinguished from a confirmed empty list in the current spec |
| QF-5 | State licensing database returns HTTP 429 during 08:00–10:00 peak window; agent exhausts backoff (3 retries: 5s, 10s, 20s), falls back to 23-hour-old cached credential status, sets `stale_credential_flag = true` in `audit_log`; the submission gate does not check this flag; a nurse whose license was suspended 20 hours ago (suspension not in cache) is included in the shortlist with `credential_status = "ACTIVE"` | `PlacementSubmission.credential_status_at_submission = "ACTIVE"` written; `stale_credential_flag = true` present in `audit_log` JSON but not surfaced in any coordinator-visible UI field | Coordinator sees no warning; `PlacementSubmission` dispatches to facility; credential suspension not discovered until facility verifies independently or a patient safety incident occurs | Submission gate: if `stale_credential_flag = true` on any candidate in the shortlist, block submission and create `HITLQueueItem` with `gap_type = CREDENTIAL_REFRESH_REQUIRED`; retry nurse DB query once before blocking; alert QA lead within 5 min via SMS. *Rate limit mitigation:* request queuing for state portal queries with exponential backoff (3 retries, 5s/10s/20s); if all retries fail, `stale_credential_flag = true` propagates to the submission gate as a hard block, not a flag-and-continue. Fallback to cached status is permitted only with explicit coordinator acknowledgement of staleness. | design gap — D4a §9 integration contract specifies the nurse DB query at intake time but does not specify staleness propagation to the D4b submission gate or what the coordinator must acknowledge before proceeding on a stale credential |
| QF-6 | State X joins the Nurse Licensure Compact effective 2026-07-01; the agent's HR-3 gate has a hardcoded compact-state list that was last updated before 2026-07-01; agent continues requiring a state-specific license for State X when a compact license is now sufficient; NRS-312 (compact license holder, newly eligible for State X) is filtered out of every shortlist for State X facilities after the effective date | NRS-312 absent from `CandidateShortlist` for State X facilities; shortlist has 2 candidates instead of 3; NRS-312 is the best-matched available nurse but is never surfaced | Coordinator sees a valid shortlist with 2 credentialed candidates; selects from available options; no exception raised; fill succeeds with a suboptimal candidate; NRS-312's exclusion surfaces only if a coordinator manually notices the nurse is not appearing on expected shifts | Quarterly credential rules review by compliance team; any NLC membership change triggers a `credential_rules.yaml` version bump (v_N → v_N+1); agent deployments are blocked by a compliance team sign-off gate that checks `credential_rules.yaml` version against the last compliance-reviewed version before any deployment; `audit_log.credential_rules_version` pinned per shortlist run. *Regulatory drift mitigation:* compliance team receives a calendar-based quarterly review reminder; any state compact membership change or scope-of-practice update triggers an ad hoc review within 5 business days of announcement. | design gap — D4b §6 Decision 1 HR-3 specifies state-aware credential logic but defines no mechanism for detecting or incorporating changes to state licensing rules; hardcoded state lists become incorrect without a code change and without an alert |

---

### Infrastructure Failure Modes

All four required infrastructure failure modes with agent behaviour, maximum acceptable outage duration, and alert paths:

#### State portal / external API rate limits

State licensing databases (used for HR-3 credential re-check at shortlist generation and pre-submission re-check) are rate-limited. At 960 decisions/day ≈ 2 queries/minute average, peak fill windows (08:00–10:00) may reach 10× = 20 queries/minute (see Assumption A4). Mitigation: request queuing with exponential backoff (3 retries: 5s, 10s, 20s); on retry exhaustion, `stale_credential_flag = true` is written to `audit_log` and the submission gate treats this as a hard block (not a flag-and-continue) until a fresh query succeeds or the coordinator explicitly acknowledges the staleness. ServiceNow REST API (60 req/min, D4a §9 A-3): requests queued in an in-memory queue; if queue depth exceeds 30 pending items, on-call coordinator is alerted via SMS within 5 minutes.

#### Regulatory drift

State licensing rules change (new compact license states, updated scope-of-practice rules, new certification requirements). The agent's HR-2/HR-3 credential gate logic becomes incorrect without a code change. Mitigation: `credential_rules.yaml` versioned config (bumped on every rule change); agent deployments are blocked by a compliance team sign-off gate that verifies the deployed `credential_rules_version` matches the latest compliance-reviewed version; `audit_log.credential_rules_version` is pinned per shortlist run so any placement can be audited against the rules version active at decision time; quarterly scheduled review owned by the compliance team; ad hoc review within 5 business days of any NLC membership change or scope-of-practice update.

#### Model accuracy drift

The LLM used for profile note classification (D4b WS2-T8) or field extraction (D4a WS1-T3) produces different outputs over time as the model is updated by the provider. Mitigation: 50-note golden-set evaluation (see Assumption A1 for sample size caveat) run on every model update before production deployment; if classification agreement with ground-truth labels drops below 92% (46/50 correct), the model version is frozen, the previous version is restored, and the ML team is alerted within 24 hours; `audit_log.model_version` is pinned per classification run; the ML team owns the threshold review and is the alert recipient.

#### Single points of failure

| SPOF | Agent behaviour when unavailable | Max acceptable outage before coordinator workflow is materially disrupted | Alert path and SLA |
|------|----------------------------------|--------------------------------------------------------------------------|-------------------|
| **ServiceNow** (all reads and writes fail) | Pause message polling; buffer inbound messages to a local dead-letter queue (JSON, keyed by `source_message_id`); freeze all open briefs in current status; no new `MatchingBriefs` created | 15 minutes — beyond this, the coordinator queue is stale and no new intake is processed, creating competitive fill losses | On-call coordinator notified via SMS within 5 minutes of first HTTP 503 after 3 retries; supervisor escalated at 10 minutes; dead-letter queue reviewed manually at recovery |
| **Nurse DB** (all shortlist generation blocks) | Block all new `CandidateShortlist` creation; log `NURSE_DB_UNAVAILABLE` per affected brief; existing open HITL items remain actionable; coordinators continue manual matching using existing records | 15 minutes — same-day urgent fills that miss the submission window are competitive losses; beyond 15 minutes the fill pipeline is materially disrupted | On-call coordinator notified via SMS within 5 minutes of DB unavailability; QA lead notified within 10 minutes with count of blocked briefs; each blocked brief ID logged to the dead-letter record |
| **LLM API** (profile note classification unavailable) | Fall back to `note_classification = RISK_SIGNAL` for all candidates with any profile notes (conservative default); all such candidates are routed to coordinator review; HITL rate rises from ~15% baseline (Assumption A3) to an estimated ~40% (the population of candidates with notes); no submission is blocked — coordinator reviews notes manually | 30 minutes — coordinator can manually classify notes; beyond 30 minutes, HITL backlog exceeds one coordinator's capacity and fill cycle time lengthens materially | QA lead notified within 15 minutes with estimated HITL surge volume; coordinator lead notified to expect manual note review queues; `audit_log.model_version = "FALLBACK_RISK_SIGNAL"` written to all affected classification events for audit traceability |

---

## 4. Build-Loop Diagnostic Test

The following test detects whether the coding agent implemented the WS2-JtD-3 boundary as Human Only (correct) or as a fully agentic auto-selection (cheaper). The boundary tested is S-3: does the agent halt after ranking and await coordinator selection, or does it auto-select the top-ranked candidate and create a `PlacementSubmission` immediately?

```python
# Taxonomy: DESIGN GAP
# D4b Decision 3 specifies the ranking algorithm precisely but contains no halt instruction.
# The human-only archetype for WS2-JtD-3 lives in D2B §3, not in D4b §8 autonomy matrix.
# A coding agent reading only D4b has everything needed to implement ranking + auto-selection
# as a valid interpretation of "identify optimal candidate from shortlist."
# This test catches the design gap: the halt constraint is missing from D4b.

import pytest
from src.matching import generate_shortlist, create_placement_submission
from src.models import CandidateShortlist


@pytest.fixture
def brief_at_ws2():
    return {
        "brief_id": "BRF-2210",
        "status": "ADVANCED_TO_WS2",
        "specialty_required": "RN_ICU",
        "facility_id": "FAC-044",
        "shift_datetime_start": "2026-06-15T07:00:00",
    }


@pytest.fixture
def qualified_candidates():
    # Three candidates that cleared HR-1 through HR-5 gates
    return [
        {"nurse_id": "NRS-101", "ranking_score": 0.91, "note_classification": "NO_NOTES", "distance_miles": 12},
        {"nurse_id": "NRS-087", "ranking_score": 0.87, "note_classification": "NEUTRAL",  "distance_miles": 8},
        {"nurse_id": "NRS-203", "ranking_score": 0.78, "note_classification": "NO_NOTES", "distance_miles": 3},
    ]


def test_shortlist_halts_and_requires_coordinator_selection(brief_at_ws2, qualified_candidates):
    """
    Correct implementation (WS2-JtD-3 = Human Only):
    After ranking, agent writes PENDING_COORDINATOR_REVIEW shortlist and
    a CANDIDATE_SELECTION_REQUIRED HITL item — then halts.
    No PlacementSubmission is created before coordinator acts.
    """
    result = generate_shortlist(brief_at_ws2, qualified_candidates)

    # ASSERTION: shortlist exists and awaits coordinator ownership
    assert result.shortlist is not None
    assert result.shortlist.status == "PENDING_COORDINATOR_REVIEW"

    # ASSERTION: HITL item routes the decision to a coordinator
    assert result.hitl_item is not None
    assert result.hitl_item.gap_type == "CANDIDATE_SELECTION_REQUIRED"
    assert result.hitl_item.shortlist_id == result.shortlist.shortlist_id

    # ASSERTION: no submission created without coordinator action
    assert result.placement_submission is None

    # ANTI-ASSERTION: the cheaper implementation auto-selects NRS-101 (top rank 0.91)
    # and writes PlacementSubmission immediately with approved_by = None or "agent".
    # If a submission was created, it must carry a coordinator ID — not a system value.
    if result.placement_submission is not None:
        assert result.placement_submission.approved_by is not None, (
            "CHEAPER IMPLEMENTATION DETECTED: PlacementSubmission written without "
            "coordinator approval — WS2-JtD-3 is Human Only; auto-selection is wrong."
        )
        assert result.placement_submission.approved_by != "agent", (
            "CHEAPER IMPLEMENTATION DETECTED: approved_by = 'agent' — "
            "the agent cannot make this selection; a coordinator ID is required."
        )


def test_submission_is_blocked_without_approved_by(brief_at_ws2, qualified_candidates):
    """
    PlacementSubmission creation must raise if CandidateShortlist.approved_by is absent.
    """
    shortlist = CandidateShortlist(
        shortlist_id="SL-2210",
        brief_id="BRF-2210",
        candidates=qualified_candidates,
        status="PENDING_COORDINATOR_REVIEW",
        approved_by=None,  # coordinator has not yet acted
    )

    # ASSERTION: submission creation must fail when coordinator has not approved
    with pytest.raises(ValueError, match="approved_by must be a coordinator ID"):
        create_placement_submission(shortlist, selected_nurse_id="NRS-101")

    # ANTI-ASSERTION: cheaper implementation calls create_placement_submission here
    # without raising — it succeeds and writes the submission. This test confirms it does not.


def test_submission_succeeds_after_coordinator_approval(brief_at_ws2, qualified_candidates):
    """
    After coordinator writes approved_by, submission is created correctly.
    """
    shortlist = CandidateShortlist(
        shortlist_id="SL-2210",
        brief_id="BRF-2210",
        candidates=qualified_candidates,
        status="SELECTION_CONFIRMED",
        approved_by="COORD-05",  # coordinator has acted
    )

    submission = create_placement_submission(shortlist, selected_nurse_id="NRS-101")

    # ASSERTION: submission carries coordinator attribution, not agent self-attribution
    assert submission.selected_nurse_id == "NRS-101"
    assert submission.approved_by == "COORD-05"
    assert submission.approved_by is not None
    assert submission.approved_by != "agent"
```

**Taxonomy classification: Design gap.** D4b Decision 3 specifies the ranking algorithm precisely and correctly. The spec is not ambiguous about *how to rank*. The spec is silent about *what happens after ranking* — specifically that the agent must halt, write the shortlist to the coordinator queue, and block submission until `approved_by` is populated. The Human Only constraint for WS2-JtD-3 lives in D2B §3, not in D4b §8 autonomy matrix. A coding agent reading only D4b would implement ranking + auto-selection as a valid and complete interpretation. The fix is a D4b spec addition: §8 autonomy matrix must explicitly state for WS2-JtD-3 "agent role = display and halt; coordinator role = select; no PlacementSubmission may be created until `CandidateShortlist.approved_by` is set to a coordinator ID."

---

## 5. Assumption Log

> **Assumption [A1]:** The golden-set for model accuracy drift detection uses N = 50 notes (25 RISK_SIGNAL, 15 NEUTRAL, 10 BLOCKING ground-truth labels) with a 92% agreement threshold (46 of 50 labels must match the ground truth on every model update).
> **Why it matters:** QF-2 detection and the infrastructure model accuracy drift mitigation both depend on this golden-set producing reliable signal. If N = 50 is too small, a model that has drifted significantly could achieve ≥ 92% agreement on 50 samples by chance — especially if NEUTRAL is the dominant label in the corpus.
> **If wrong:** A drifted model passes the golden-set threshold; RISK_SIGNAL notes are classified NEUTRAL in production; QF-2 fails silently until a placement complaint surfaces. N should be increased to ≥ 200 with stratified sampling across all four label categories; sample size must be validated by the ML team against the expected base rate of RISK_SIGNAL and BLOCKING notes in the production corpus before deployment.
> **Confidence:** Low — N = 50 is a placeholder assumption; no statistical power calculation was performed.

> **Assumption [A2]:** `rapidfuzz.fuzz.WRatio("Metro General Hosp", "Metro General Hospital")` returns exactly 80 for the string pair used in S-2, under the specific version of rapidfuzz deployed in the build environment.
> **Why it matters:** S-2 is designed to test the WRatio = 80 boundary. If the actual score for this pair is 79 or 81, the test does not exercise the exact threshold condition and the boundary validation is invalid.
> **If wrong:** The S-2 fixture must be replaced with a verified string pair that produces WRatio = exactly 80 in the deployed rapidfuzz version. The test must also bracket the boundary: a string pair at WRatio = 79 must trigger HITL, and a string pair at WRatio = 81 must resolve autonomously — both must be confirmed in the build environment before S-2 is considered valid.
> **Confidence:** Medium — string pair chosen to approximate the boundary; exact score is version- and normalization-dependent; must be verified in the build environment before test execution.

> **Assumption [A3]:** The HITL baseline rate is approximately 15% of total briefs processed. The daily HITL rate monitor alert threshold ("drop below 50% of the 4-week rolling baseline") is calibrated against this estimate.
> **Why it matters:** If the true baseline is 8%, the 50%-of-baseline alert fires at 4% — plausible within normal day-to-day variance and produces frequent false positives. If the true baseline is 30%, the alert fires at 15% — a meaningful signal. The alert threshold is only useful if calibrated against the measured baseline.
> **If wrong:** The alert threshold must be recalibrated after the first 4 weeks of production operation using the observed rolling HITL rate. Do not use the 15% estimate as a permanent threshold — measure and set.
> **Confidence:** Low — 15% is derived from the confidence gate parameters and estimated input quality; actual rate is not stated in the scenario and must be measured in production.

> **Assumption [A4]:** State licensing databases rate-limit queries at approximately 2 per minute on average (derived from 960 decisions/day × 2 credential checks per decision ÷ 1,440 minutes/day), with peak at 10× = 20 queries/minute during 08:00–10:00 fill windows. The backoff strategy (3 retries: 5s, 10s, 20s) and staleness handling are calibrated against this estimate.
> **Why it matters:** QF-5 (stale credential propagated due to rate limiting) and the infrastructure rate limit mitigation are both calibrated against this rate. If the actual rate limit is 1 query/minute, the backoff strategy must be more aggressive and the stale-credential window shorter. If the limit is 60 queries/minute, QF-5 is substantially less likely.
> **If wrong:** The backoff parameters, retry cap, and staleness handling must be re-calibrated based on measured state portal response behaviour during peak load testing before the credential re-check integration is deployed to production.
> **Confidence:** Low — specific state portal rate limits are not stated in the scenario; this is an estimate. Must be validated by the compliance team during integration testing.
