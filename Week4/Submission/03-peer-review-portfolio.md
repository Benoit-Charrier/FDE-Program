# Gate 4 Deliverable 3 — Peer Review Portfolio

---

## Spec 1 Review

**Spec name:** D4a — Capability Spec: Intake Agent (WS4)
**File reviewed:** `Spec_review_input1/04a-capability-spec-intake-Dmytro.md`
**Status declared in spec:** FINAL
**Spec creator:** Dmytro

---

### Overall Assessment

This is a well-structured spec. The autonomy matrix is precise, the state machine is complete, the integration contracts have proper error tables, and the worked examples follow through on the pass criteria. The PHI handling and audit trail design are above average.

Three of the five blockers would cause a builder to implement incorrect logic silently — they produce definite-but-wrong behaviour rather than obvious ambiguity a careful builder would catch and ask about.

**Recommendation: return with required fixes on B1–B5 before build starts. Concerns C1–C3 can be resolved in sprint 1 without blocking the build kick-off.**

---

### What Can Be Built Now

The following areas are complete enough to implement immediately — every decision is made and every edge case is covered:

- **Full email polling loop** (Contract 1): polling, retry logic with exponential backoff, mark-as-read idempotency gate, and crash recovery guarantee are all specified
- **Clarification response detection** (Contract 1, steps 1–6): thread-header matching logic, the single-record fallback, and the new-intake path are unambiguous
- **Complete email parsing** (Contract 6): system prompt is exact, output schema defined, post-parse validation rules listed, and the specialty mapping algorithm (cosine similarity → EXACT/MAPPED/UNMAPPABLE) is fully specified
- **Autonomy matrix — all 13 conditions**: every delegation level, agent action, and human action is defined; SLAs are stated
- **CRM state machine**: all transitions defined except the `MULTI_CLARIFICATION_CONFLICT` path (see B2)
- **Audit trail**: full schema defined, retention policy stated (6 years, HIPAA), append-only constraint explicit
- **Coordinator queue record creation**: schema defined, fallback behaviour on API unavailability specified
- **PHI handling**: extraction rules and routing triggers clearly defined; "log the flag, not the content" rule is explicit
- **Outbound email templates**: exact content given for both acknowledgement and clarification emails; substitution rules cover all field states
- **Agent startup sequence**: four-step order specified including specialty vocabulary caching and clarification timeout resume
- **All worked examples** (after applying B5 date fix): Examples 1–5 have clear pass criteria covering happy path, clarification loop, cancellation, modification, and UNMAPPABLE specialty

---

## Issues Requiring Fixes

Each issue includes the reviewer finding and the builder consequence if built as-is.

---

### Blockers

Issues that must be fixed before the build starts — either a builder would implement wrong behaviour silently, or a required decision has no answer in the spec.

---

#### B1 — Duplicate detection omits specialty: produces silent false positives

**Type:** Spec gap — functional logic error
**Checklist criterion:** Buildability — "Every conditional ('if,' 'when,' 'unless') has explicit criteria and outcomes"; the duplicate detection conditional omits a load-bearing field from its criteria
**Location:** Autonomy Matrix → duplicate detection row; Race Conditions table, first row; Contract 3 → duplicate detection query

**Finding:**

The duplicate condition is `hospital_id + shift_date + shift_start_time ±30min + received_at ±60min`. Specialty is not part of it. A hospital legitimately requesting an ICU nurse and an ER nurse for the same shift window on the same date would have the second request silently merged into the first — WS1 is triggered once, the second shift is never filled, and no coordinator alert fires. This is a data-loss failure mode, not an edge case.

**If built as-is:** Builder implements exactly the condition stated and produces an agent that drops legitimate shift requests with no alert. The failure would only surface operationally when a hospital reports an unfilled shift.

**Fix:** Add `specialty_required` to the deduplication criteria and update the Contract 3 query: `GET /shift-requests?hospital_id={id}&shift_date={date}&specialty_required={code}&status=...`. For `UNMAPPABLE` specialty (not yet resolved), add a note: *"Skip specialty filter in deduplication; treat as distinct record."*

---

#### B2 — `MULTI_CLARIFICATION_CONFLICT` has no CRM status transition defined

**Type:** Spec gap — missing state machine row
**Checklist criterion:** Entity Precision — "State machine is complete: for each state, list all valid transitions and prerequisites"; MULTI_CLARIFICATION_CONFLICT is a named routing path with no corresponding state machine entry
**Location:** Contract 1 → clarification response detection, step 5; Coordinator Queue → `reason_code` enum; CRM Request Status State Machine

**Finding:**

Contract 1 step 5 routes to the coordinator queue when multiple `CLARIFICATION_PENDING` records exist and no thread header match — but no CRM status is specified for this path, and the state machine has no row for this event. The inbound email has no CRM record yet. The builder cannot know: what status to set, whether to create a new record, and what `crm_request_id` to put in the coordinator queue item.

**If built as-is:** Builder invents a status (likely `TYPE_AMBIGUOUS`) and creates a new record arbitrarily. Coordinator experience is undefined and unpredictable; the builder's guess may not match what the coordinator queue UI expects.

**Fix:** Add a state machine row: *"Inbound email matches multiple `CLARIFICATION_PENDING` records; no thread header match → WS4 creates new record with status `TYPE_AMBIGUOUS`; routes to coordinator queue with `reason_code = MULTI_CLARIFICATION_CONFLICT` and note listing affected record IDs."*

---

#### B3 — `EMAIL_POLL_INTERVAL_SECONDS` referenced in Contract 1 but missing from Configuration table

**Type:** Spec gap — incomplete configuration
**Checklist criterion:** Integration Contracts — configurable values must have a defined source (env var or config table); EMAIL_POLL_INTERVAL_SECONDS is named in two spec sections but absent from the configuration table, forcing the builder to supply the value
**Location:** Contract 1 → first paragraph ("configurable via `EMAIL_POLL_INTERVAL_SECONDS` — add to Configuration if confirmed"); Configuration table

**Finding:**

Contract 1 names `EMAIL_POLL_INTERVAL_SECONDS` as configurable with a 60-second default, then defers its addition to the config table with "if confirmed." It is not there. The circuit breaker section also recommends "increasing `EMAIL_POLL_INTERVAL_SECONDS`" — but if it's not a config parameter, ops cannot act on that recommendation without a code change.

**If built as-is:** Builder hardcodes 60 seconds. Polling rate is not adjustable at deployment. If the CRM write API is under pressure, ops has no lever to back off the poll rate without redeploying.

**Fix:** Add to the Configuration table: `EMAIL_POLL_INTERVAL_SECONDS | integer (seconds) | 60 | Email polling cadence. Ops can increase this value if EMAIL_POLL_COST_BUDGET_USD_PER_HOUR alert fires.` Remove the "add to Configuration if confirmed" qualifier from Contract 1.

---

#### B4 — MedFlex operating states list is undefined: `facility_state` validation cannot be implemented

**Type:** Spec gap — missing configuration
**Checklist criterion:** Integration Contracts — "Data mapping from internal to external is documented"; the facility_state validation rule references an operating-states list with no defined source anywhere in the spec
**Location:** Shared Glossary → `facility_state` field constraints; Contract 6 → post-parse validation

**Finding:**

The spec requires `facility_state` to be validated against MedFlex's operating states, but this list is nowhere defined — not in the config table, not in the Shared Glossary, not in any referenced file.

**If built as-is:** Builder hardcodes all 50 US states (safest guess) — making the validation vacuous and allowing out-of-state placement requests through to WS1, creating a compliance risk for unlicensed placements.

**Fix:** Add to the Configuration table: `MEDFLEX_OPERATING_STATES | JSON array of strings | ["IL","NY","TX"] (sample — confirm with Aaron) | List of 2-letter US state codes MedFlex operates in. Aaron must supply the production list before deployment.` Update the `facility_state` Shared Glossary constraint to reference this parameter.

---

#### B5 — Worked examples use dates that are now in the past

**Type:** Spec inconsistency — test case breakage
**Checklist criterion:** Validation Design — "At least one end-to-end happy-path scenario with concrete inputs and outputs"; hardcoded past dates make the worked examples non-reproducible as test fixtures
**Location:** Worked Examples → Example 1 (`shift_date = 2026-05-15`); Example 2 (`shift_date = 2026-05-19`); Contract 6 → post-parse validation

**Finding:**

Example 1 specifies `shift_date = 2026-05-15`. Today is 2026-05-19. Per post-parse validation, any `shift_date` less than today is rejected and routed to the coordinator queue. Example 1 hits the rejection path, not the `INTAKE_COMPLETE` path its pass criterion requires. Example 2 resolves to today's date — borderline and non-deterministic depending on UTC time.

**If built as-is:** Builder runs the happy-path test and sees it fail. They investigate whether the rejection rule is wrong or the example is wrong, losing time on a spec error rather than a real build issue.

**Fix:** Replace hardcoded dates in all examples with relative references: *"T+14 days from test run date."* Add a note at the top of the Worked Examples section: *"All dates are illustrative. Test execution requires a future shift_date ≥ 1 day from test run date. Parameterise dates in test fixtures — do not hardcode."*

---

### Concerns

Real design risks. Not immediate build blockers — a builder can start — but must be resolved before pilot.

---

#### C1 — Clarification loop has no maximum round cap: unbounded wait condition

**Type:** Spec risk — explicit design choice with unacknowledged failure mode
**Checklist criterion:** Delegation Boundaries — "Escalation paths are complete: if escalated, what happens next?"; no escalation trigger is defined for the case where clarification rounds accumulate without resolution
**Location:** State machine → `CLARIFICATION_PENDING` self-loop note; Example 2

**Finding:**

A partial clarification response resets `CLARIFICATION_TIMEOUT_MINUTES`. With no cap on rounds, a hospital that sends one field per response before each timeout keeps a request in `CLARIFICATION_PENDING` indefinitely. The coordinator never receives the item; the shift is never filled. The spec acknowledges "no cap in v1" but does not flag this as a risk.

**If built as-is:** The agent behaves exactly as specified. The failure surfaces operationally when a hospital reports an unfilled shift after a multi-day clarification loop.

**Fix:** Add `MAX_CLARIFICATION_ROUNDS` (default: 3) to the Configuration table. Update the self-loop state machine note: *"If round count exceeds `MAX_CLARIFICATION_ROUNDS`, transition to `CLARIFICATION_TIMEOUT` regardless of timeout clock."*

---

#### C2 — Specialty vocabulary cache TTL undefined

**Type:** Spec gap — missing configuration
**Checklist criterion:** Integration Contracts — configurable values must have a defined source; SPECIALTY_VOCABULARY_CACHE_TTL_HOURS is referenced in prose ("Refresh when cache TTL expires") but absent from the configuration table
**Location:** Agent Startup Behavior → step 1; Configuration table

**Finding:**

The spec says to cache specialty vocabulary embeddings and "Refresh when cache TTL expires" but no TTL parameter is defined anywhere. If the CRM vocabulary changes (new specialty added) and the cache is stale, the agent classifies the new specialty as `UNMAPPABLE` and routes it to the coordinator queue, producing false escalations until the next agent restart.

**If built as-is:** Builder invents a cache policy (likely a hardcoded constant). Ops has no lever to force a vocabulary refresh without redeploying.

**Fix:** Add to the Configuration table: `SPECIALTY_VOCABULARY_CACHE_TTL_HOURS | integer (hours) | 24 | How long specialty vocabulary embeddings are retained before re-fetching from CRM.`

---

#### C3 — Portal intake: who triggers WS1 for portal submissions is undefined

**Type:** Spec gap — missing integration boundary
**Checklist criterion:** Integration Contracts — "Fallback behavior: if the integration is unavailable, what does the agent do?"; more precisely, the boundary between portal intake and WS1 is unnamed despite PORTAL being a defined enum value — WS1 builder cannot determine whether to expect or ignore portal records
**Location:** Scope → portal intake (out of scope); Shared Glossary → `intake_channel` enum

**Finding:**

Portal submissions are out of WS4's scope, but the Shared Glossary includes `intake_channel = PORTAL`. WS1 is triggered by CRM status `INTAKE_COMPLETE`. If the portal creates records without setting that status, WS1 never processes portal shifts. The WS1 builder needs to know whether to expect `PORTAL` records.

**If built as-is:** WS1 builder either handles `PORTAL` records identically to `EMAIL` (safe but undocumented) or ignores them entirely (drops portal shifts).

**Fix:** Add one sentence to the Scope section: *"Portal submissions are expected to arrive in the CRM with all Shared Glossary fields populated and status `INTAKE_COMPLETE` — WS1 picks them up via its existing CRM polling. WS4 takes no action on portal records."*

---

### Acceptable Differences

Items that look like issues but are not.

**LLM provider (OpenAI, not Claude):** `PARSING_LLM_MODEL` and `SPECIALTY_EMBEDDING_MODEL` are configurable. The OpenAI API structure in Contract 6 is internally consistent, and models are named as defaults, not hardcoded. Not an issue.

**No `created_by` field on CRM record:** Provenance is tracked via the audit log `agent_id` field (Shared Glossary → Record provenance note). Adequate for HIPAA audit purposes. Design rationale is stated. Not an issue.

**`TRUNCATION_ESCALATED` reason_code vs. `TYPE_AMBIGUOUS` CRM status:** The queue reason_code doesn't match the CRM status for the token-ceiling case, but the behaviour is unambiguous from context. Coordinators see `TRUNCATION_ESCALATED` in their queue, which is more informative than `TYPE_AMBIGUOUS`. Minor documentation cleanup only.

**Cancellation supersedes clarification in concurrency:** Correct call for healthcare staffing — a cancellation received during an open clarification loop means the shift is no longer needed. Not an issue.

---

## Build Readiness Summary

### Build now — no fixes required

| Area | Spec sections |
|------|--------------|
| Email polling loop, retry logic, idempotency | Contract 1 |
| Clarification response detection (steps 1–6) | Contract 1 |
| Email parsing, specialty mapping algorithm | Contract 6 |
| All 13 autonomy matrix conditions + SLAs | Autonomy Matrix |
| CRM state machine (all transitions except MULTI_CLARIFICATION_CONFLICT) | State Machine |
| Audit trail, PHI handling, coordinator queue creation | Audit Trail, Compliance, Coordinator Queue |
| Outbound email templates (acknowledgement + clarification) | Contract 5 |
| Agent startup sequence | Agent Startup Behavior |
| Worked examples 1–5 (with future dates substituted) | Worked Examples |

### Fix first — spec must be updated before builder proceeds

| ID | Issue | Fix complexity |
|----|-------|----------------|
| B1 | Duplicate detection omits specialty → silent data loss | Low — add specialty to dedup condition |
| B2 | `MULTI_CLARIFICATION_CONFLICT` has no state machine row → builder guesses status | Low — add one state machine row + note |
| B3 | `EMAIL_POLL_INTERVAL_SECONDS` absent from config table → hardcoded, non-tunable | Trivial — add table row |
| B4 | MedFlex operating states list undefined → validation is vacuous | Trivial — add config parameter |
| B5 | Worked example dates are in the past → happy-path test fails | Low — replace hardcoded dates with relative references |
| C1 | No clarification round cap → unbounded wait condition | Low — add config parameter + state machine note |
| C2 | Specialty vocabulary cache TTL undefined → builder hardcodes policy | Trivial — add config parameter |
| C3 | Portal → WS1 trigger undefined → WS1 builder makes undocumented assumption | Low — add one clarifying sentence to Scope |

---

### Production Spec Checklist Report

Sections from `production-spec-checklist.md` evaluated against this spec. **Pass** = no findings trace here. **Partial** = concerns (C#) only. **Fail** = one or more blockers (B#) trace here.

| Section | Status | Key findings |
|---------|--------|--------------|
| Buildability | **Fail** | B1: duplicate conditional omits specialty — criteria are incomplete. B3: `EMAIL_POLL_INTERVAL_SECONDS` referenced in two sections, absent from config table — builder-supplied constant. B4: operating states list has no defined source — validation rule is unimplementable. |
| Entity Precision | **Fail** | B2: `MULTI_CLARIFICATION_CONFLICT` is a named routing path with no state machine entry — builder must invent a status and record-creation rule. |
| Delegation Boundaries | **Partial** | All 13 autonomy matrix conditions are defined with explicit SLAs. C1: no clarification round cap means the escalation path for a persistent partial-response loop is undefined. |
| Integration Contracts | **Fail** | B3/B4: two config parameters are referenced in contracts but absent from the config table (poll interval, operating states). C2: specialty cache TTL referenced in prose but absent from config table. C3: `PORTAL` channel code is defined in the Shared Glossary but the WS1 trigger boundary has no contract. |
| Validation Design | **Fail** | B5: two worked example dates are in the past — the happy-path test is non-reproducible as a fixture. All other examples (clarification loop, cancellation, modification, UNMAPPABLE) are complete. |
| Assumptions Register | **Partial** | Portal intake constraint and operating states list are acknowledged as open items in the spec text, but neither is formally registered with a confidence level, failure mode, or named validation owner. |
| Economics Alignment | **Partial** | Circuit breaker and `EMAIL_POLL_COST_BUDGET_USD_PER_HOUR` alert are referenced, showing cost awareness. No token budget or batch opportunity analysis is documented. |
| Governance | **Pass** | Audit trail schema fully defined, 6-year HIPAA retention stated, PHI "flag not log" rule is explicit, append-only constraint documented. No gaps. |

---

### Attribution

> **Spec reviewed:** `04a-capability-spec-intake-Dmytro.md`
> **Spec creator:** Dmytro
> **Reviewer:** Benoit Charrier

---

---

## Spec 2 Review

**Spec name:** 04a — Capability Spec: Match Selection (JtD-3)
**File reviewed:** `Spec_review_input2/04a-capability-spec-match-selection-Alexandra.md`
**Status declared in spec:** Not explicitly stated (§13 self-certifies production-grade checklist compliance)
**Spec creator:** Alexandra

---

### Overall Assessment

This is the most complete spec in the cohort. The scoring algorithm is fully deterministic with explicit pseudocode, all five integration contracts have endpoint, auth, retry logic, and fallback defined, and the six data models are precise enough to generate schema migrations from. The governance section is thorough, the edge cases cover BP5 rejection and low-confidence handling, and the delegation rationale is well-argued.

Four blockers exist — none are architectural gaps; all are internal contradictions or missing contracts that a builder would hit in the first sprint. The most consequential is the JtD-5a update path: without a PATCH contract for `submission_outcome`, the entire A19 training corpus accumulates no actual outcomes, blocking the Phase 2 ML ranker permanently.

**Recommendation: return with required fixes on B1–B4 before build starts. Concerns C1–C3 can be resolved in sprint 1 without blocking kick-off.**

---

### What Can Be Built Now

The following areas are complete enough to implement immediately:

- **Full disqualification pass** (§8.1): all four conditions (MISSING_REQUIRED_CREDENTIAL, EXPIRED_REQUIRED_CREDENTIAL, AVAILABILITY_WINDOW_MISMATCH, DUPLICATE_IN_FLIGHT) are precise boolean logic
- **Composite scoring formula** (§8.2–8.4): weights, component breakpoints, edge cases (no preferred creds, missing geocode, no history), and explanation template are all fully specified
- **All integration contracts §7.1–7.3, 7.5**: ServiceNow preference history read, coordinator review write, ranker feedback write, and internal coordinator API are complete with auth, error handling, retry logic, and data mapping
- **Geocoding integration** (§7.4): nurse ZIP-to-coordinates, caching logic, retry, neutral fallback, and rate limit handling all specified
- **Six data models** (§3.1–3.6): ParsedShiftRequirement, CandidatePool/CandidateProfile, CandidateScore, RankedShortlist (except EXPIRED entry), CoordinatorReview, RankerFeedback — all have types, constraints, and primary keys
- **Autonomy matrix** (§5): all four delegation categories with explicit conditions, thresholds, and SLAs
- **Happy path and edge cases 1–5** (§10.1–10.2): complete with setup, expected execution, and pass criteria (after resolving B1 and B3 contradictions)
- **Failure modes** (§10.3): three failure modes with setup, expected behaviour, and recovery paths
- **Governance and audit trail** (§11): audit log schema with full field-level detail, HITL SLAs, override mechanism, non-repudiation, and compliance scope
- **Wave 1 build order** (§12): six-component sequence with shared asset tracking and integration reuse matrix

---

## Issues Requiring Fixes

---

### Blockers

---

#### B1 — `RankerFeedback` uniqueness constraint contradicts BP5 re-rank requirement

**Type:** Spec inconsistency — contradictory data model constraint
**Checklist criterion:** Entity Precision — "No contradictory rules (e.g., 'status is immutable' AND 'status can change')"; the uniqueness constraint and the BP5 re-rank flow directly contradict each other in the same spec
**Location:** §3.6 RankerFeedback → Constraints (last line); §10.2 Edge Case 5

**Finding:**

§3.6 states: *"One RankerFeedback per shift_request_id."* Edge Case 5 (BP5 rejection) then states: *"New RankerFeedback record written (separate from original; same shift_request_id)."* These are directly contradictory. The BP5 re-rank is a named, defined flow — it is not an edge case a builder might skip. A builder must choose one or the other.

**If built as-is:** Builder implements the uniqueness constraint (it is the formal data model constraint), then hits Edge Case 5 and finds the re-rank write is rejected with HTTP 409. They investigate, find both instructions, and invent a resolution — likely adding a round_number field or dropping the uniqueness constraint — without spec authority. A19 training labels for re-ranked cases are unpredictably structured.

**Fix:** Remove the uniqueness constraint and replace with: *"Multiple RankerFeedback records per shift_request_id are permitted; each BP5 re-rank creates a new record. Add a `round_number` field (integer ≥ 1, default 1; incremented on each BP5 re-rank) to distinguish records for the same request."* Update §3.6, §7.3 request body, and the data mapping.

---

#### B2 — JtD-5a update path for `submission_outcome` has no integration contract

**Type:** Spec gap — missing integration contract
**Checklist criterion:** Integration Contracts — "For every external system integration: endpoint URL, request format, response format, timeout, retry logic"; the PATCH endpoint for submission_outcome updates has none of these defined anywhere in the spec
**Location:** §3.6 RankerFeedback → `submission_outcome` attribute; §7.3 RankerFeedback Write

**Finding:**

§3.6 states `submission_outcome` is *"updated from JtD-5a hospital response monitoring."* §7.3 defines only a POST contract — the initial write with `u_submission_outcome = PENDING`. There is no PATCH/PUT endpoint defined anywhere for updating an existing RankerFeedback record. The JtD-5a builder has no contract to implement the update; the JtD-3 builder has no endpoint to specify.

**If built as-is:** `submission_outcome` is written as PENDING on creation and never updated. The A19 training corpus has no settled outcomes (ACCEPTED/REJECTED) — ever. Phase 2 ML ranker training is not just delayed; it is permanently blocked because the feedback store will contain only PENDING records.

**Fix:** Add §7.6 *"ServiceNow — Ranker Feedback Update (owned by JtD-5a)"*: `PATCH https://{instance}/api/now/table/u_ranker_feedback/{sys_id}` with body `{ "u_submission_outcome": "ACCEPTED" | "REJECTED", "u_outcome_timestamp": ISO 8601 UTC }`. Specify: auth reuses SERVICENOW_WRITE_TOKEN; idempotent (same PATCH with same outcome is safe); retry identical to §7.3. Add note: *"JtD-5a owns the call; JtD-3 owns the endpoint definition. JtD-5a must query for `sys_id` using `u_shift_request_id` before patching."*

---

#### B3 — `edit_reason` required vs. optional for `EDITED` action contradicts state machine note

**Type:** Spec inconsistency — contradictory field constraints
**Checklist criterion:** Entity Precision — "No contradictory rules"; edit_reason is simultaneously required and nullable for the same action type in two different locations in the same spec
**Location:** §3.5 CoordinatorReview → `edit_reason` attribute; §3.5 Constraints → action = APPROVED bullet

**Finding:**

The data model states: *"edit_reason: required if action = EDITED, max 500 chars; null otherwise."* The constraints note states: *"if coordinator selects #2 or #3, action must be EDITED even with no edit_reason."* A builder implementing server-side validation on `/internal/api/v1/coordinator-review` (§7.5) faces a direct contradiction: require edit_reason on all EDITED submissions (data model), or allow it to be null for rank-override EDITED (constraint note)?

**If built as-is:** Builder follows the formal data model (more likely — it's the schema definition). Coordinators selecting candidates[1] or candidates[2] receive HTTP 400 unless they provide an edit_reason — even for a simple rank preference with no explainable reason. This creates operational friction at the highest-frequency HITL point in the system and risks coordinator non-adoption of the review UI.

**Fix:** Choose one of: (a) *"edit_reason is always required for EDITED — coordinator must state a reason for any rank override or substantive change"* (simpler, improves A19 data quality); or (b) *"edit_reason is required if action = EDITED AND the coordinator is explicitly overriding the top-ranked candidate due to system data being wrong (not a rank preference). Null is acceptable if EDITED is triggered only by selecting candidates[1] or candidates[2]."* Option (a) is recommended. Update both the data model and the constraint note to say the same thing.

---

#### B4 — `EXPIRED` status has no entry transition in the state machine

**Type:** Spec gap — incomplete state machine
**Checklist criterion:** Entity Precision — "State machine is complete: for each state, list all valid transitions and prerequisites"; EXPIRED has an exit transition defined but no entry transition — it is currently unreachable dead code
**Location:** §3.4 RankedShortlist → State Machine; §5 Autonomy Matrix → Escalation SLAs note

**Finding:**

The `EXPIRED` status appears in the status enum and has an exit transition defined (`EXPIRED → PENDING_REVIEW`). But no transition in the state machine sets a shortlist TO EXPIRED. The prose description in §3.4 says *"EXPIRED is set when PENDING_REVIEW timeout lapses without escalation resolution"* — but the state machine routes the 30-minute PENDING_REVIEW timeout to ESCALATED, not EXPIRED. The distinction between ESCALATED (explicit coordinator escalation) and EXPIRED (timeout with no coordinator action) is explained in §3.4's note, but the trigger and timing for EXPIRED are never formalized.

**If built as-is:** Builder implements the 30-minute timeout → ESCALATED path as written. EXPIRED is never set — it is dead code. The ops alert at 45 minutes fires, but if no senior coordinator acts, the record stays in ESCALATED forever with no further state transition. Ops has no structured way to reclaim abandoned shortlists.

**Fix:** Add two state machine rows: *"PENDING_REVIEW → EXPIRED: trigger: `presented_at` + 30 minutes passes AND coordinator has not submitted a CoordinatorReview (distinct from ESCALATED — EXPIRED fires when no coordinator opens the review UI; ESCALATED fires when a coordinator explicitly escalates); add config param `SHORTLIST_REVIEW_TIMEOUT_MINUTES` (default: 30)."* Also add: *"ESCALATED → EXPIRED: trigger: escalated_at + `ESCALATED_RESOLUTION_TIMEOUT_MINUTES` (default: 15) passes with no senior coordinator action; ops escalation alert fires."* Update §5 SLAs to reference the new config parameters.

---

### Concerns

---

#### C1 — DUPLICATE_IN_FLIGHT 4-hour window is a magic constant despite "all timeouts are configurable" claim

**Type:** Spec inconsistency — self-contradicting configurability claim
**Checklist criterion:** Delegation Boundaries — "All decision thresholds are numeric or boolean (no fuzzy 'might' conditions)"; the threshold is numeric but the spec's own claim that all timeouts are configurable is violated — the value is hardcoded in prose and absent from the config table
**Location:** §8.1 Disqualification Pass → DUPLICATE_IN_FLIGHT condition; §5 Autonomy Matrix → Escalation SLAs note

**Finding:**

§8.1 hardcodes the DUPLICATE_IN_FLIGHT detection window as *"in the past 4 hours."* §5 states: *"All timeouts are configurable parameters, not hardcoded constants."* The 4-hour window is not named as a configuration parameter anywhere in the spec, and no default is listed in the config file description (§9).

**If built as-is:** Builder hardcodes 4 hours. For 12-hour ICU shifts, a nurse approved at hour 0 could be re-submitted at hour 5 for an overlapping shift — the 4-hour window is too short to prevent double-booking. Ops cannot tune without redeployment.

**Fix:** Add to the agent configuration file (§9): `DUPLICATE_IN_FLIGHT_WINDOW_HOURS | integer (hours) | 4 | Detection window for in-flight nurse assignments. Set to max shift duration (24h) for safest deduplication; lower values permit same-nurse concurrent bookings at non-overlapping shifts.` Update §8.1 to reference this parameter by name.

---

#### C2 — APPROVED action does not enforce `candidates[0]` selection at the API validation layer: silent A19 training corruption

**Type:** Spec gap — missing server-side validation
**Checklist criterion:** Delegation Boundaries — "Every action is labeled: [Agent Alone] [Agent + Log] [Agent + Review] [Human]"; the APPROVED→candidates[0] enforcement boundary is declared in the data model but absent from the API delegation contract, creating a gap between what is specified and what is enforced
**Location:** §3.5 CoordinatorReview → Constraints; §7.5 Internal Coordinator Review API → Error responses

**Finding:**

§3.5 states: *"action = APPROVED → selected_nurse_id = RankedShortlist.candidates[0].nurse_id."* But §7.5 HTTP 400 validation only names *"selected_nurse_id not in shortlist"* as a validation error — it validates membership, not rank position. No server-side check enforces that APPROVED requires the top-ranked candidate. A coordinator can submit `action = APPROVED` with `selected_nurse_id = candidates[1]` and the API accepts it.

**If built as-is:** `RankerFeedback.coordinator_edited` is set based on `action` (APPROVED vs. EDITED). With this gap, a coordinator selecting rank 2 can submit APPROVED instead of EDITED; the feedback record logs `coordinator_edited = false` — a wrong label. The A19 training corpus accumulates silently mislabeled examples where the ranker appeared to predict correctly when it did not. Phase 2 ML ranker trains on corrupted data.

**Fix:** Add to §7.5 HTTP 400 validation: *"action = APPROVED but selected_nurse_id ≠ candidates[0].nurse_id → HTTP 400 `{ 'error': 'approved_requires_top_ranked', 'field': 'selected_nurse_id' }`."* This is a one-line server-side check that eliminates the silent label corruption.

---

#### C3 — Hospital geocoded coordinates have no integration contract

**Type:** Spec gap — missing integration dependency
**Checklist criterion:** Integration Contracts — "For every external system integration: endpoint URL, request format, response format, timeout, retry logic, fallback behavior"; hospital location coordinates are consumed in the scoring hot path but the retrieval contract has none of these defined
**Location:** §7.4 Geocoding → data mapping note; §8.3 proximity_score definition

**Finding:**

§7.4 states: *"Hospital location coordinates are retrieved from ServiceNow u_hospital.u_lat, u_hospital.u_lng (assumed present per A24; flag if missing)."* §8.3 uses `hospital_geocoded` in the haversine formula. But there is no integration contract specifying how to fetch these fields. §7.1 covers preference history reads; no contract covers hospital record reads. *"Flag if missing"* is undefined — log warning? Set proximity_score = 0.5? Ops alert?

**If built as-is:** Builder infers a GET to u_hospital filtered by `sys_id = location_id`, reusing the §7.1 ServiceNow read pattern. The fallback for null lat/lng is invented (likely 0.5 by analogy with geocoding failure fallback). The spec's stated proximity score neutralisation on geocoding failure (§7.4) does not cover the case where the hospital record exists but u_lat/u_lng is null — a builder can't tell if the neutral score should trigger or if it's a data error.

**Fix:** Add §7.6 *"ServiceNow — Hospital Location Read"*: `GET /api/now/table/u_hospital?sysparm_query=sys_id={location_id}&sysparm_fields=u_lat,u_lng`; success: extract lat/lng; error handling: if HTTP 4xx or lat/lng is null → `proximity_score = 0.5` for all candidates; log warning `"hospital_geocode_unavailable for location_id={id}"`; same retry and auth pattern as §7.1. If null lat/lng persists for > 10 requests, fire ops alert.

---

### Acceptable Differences

**No LLM in the scoring hot path:** The spec explicitly states *"LLM is not invoked in the MVP JtD-3 hot path"* (§9). The agent config file replaces the system prompt. This is a well-reasoned design choice — the scoring formula is deterministic and template generation needs no language model. Not an issue.

**ServiceNow `u_` prefix table naming:** `u_coordinator_review`, `u_ranker_feedback`, `u_nurse_hospital_outcome` follow ServiceNow custom table convention. Internally consistent. Not an issue.

**Audit log retention 2 years (not 6):** §11 explicitly states *"(operational compliance, not HIPAA-regulated for this data type)"* — this is matching-coordinator decision data, not PHI. The rationale is stated and is correct. Not an issue.

**`u_outcome` enum [ACCEPTED, REJECTED] with no PENDING or CANCELLED:** The preference history table records settled placements only; unsettled or cancelled placements are correctly excluded from preference scoring. Not an issue.

**Self-certification in §13:** The spec author self-certifies against the production-grade checklist. This review has found four items the self-certification missed. This is the expected value of a peer review, not a spec design failure.

---

## Build Readiness Summary

### Build now — no fixes required

| Area | Spec sections |
|------|--------------|
| Disqualification pass (4 conditions, all boolean) | §8.1 |
| Composite scoring formula, component breakpoints, explanation template | §8.2–8.4 |
| ServiceNow preference history read (Contract 1) | §7.1 |
| ServiceNow coordinator review write (Contract 2) | §7.2 |
| ServiceNow ranker feedback initial write (Contract 3) | §7.3 |
| Geocoding integration for nurse ZIP (Contract 4) | §7.4 |
| Internal Coordinator Review API (Contract 5) | §7.5 |
| All six data models with constraints | §3.1–3.6 |
| Autonomy matrix — all four delegation categories with SLAs | §5 |
| Happy path and edge cases 1–5 (after B1/B3 fixes applied) | §10.1–10.2 |
| Failure modes (API unavailability, stale availability, geocoding failure) | §10.3 |
| Governance: audit trail, HITL checkpoints, override mechanism, compliance | §11 |
| Wave 1 build order and integration reuse matrix | §12 |

### Fix first — spec must be updated before builder proceeds

| ID | Issue | Fix complexity |
|----|-------|----------------|
| B1 | `RankerFeedback` uniqueness constraint contradicts BP5 re-rank → builder invents schema | Low — add round_number field; update constraint |
| B2 | JtD-5a `submission_outcome` update has no PATCH contract → A19 corpus permanently PENDING | Low — add §7.6 PATCH endpoint contract |
| B3 | `edit_reason` required vs. optional for EDITED → validation blocks rank-override at UI | Trivial — choose one rule; update model and constraint note |
| B4 | EXPIRED status has no entry transition → dead code, abandoned shortlists unrecoverable | Low — add two state machine rows + config params |
| C1 | DUPLICATE_IN_FLIGHT 4-hour window not in config → hardcoded, non-tunable | Trivial — add config parameter |
| C2 | APPROVED action doesn't validate candidates[0] → silent A19 label corruption | Trivial — add one HTTP 400 validation case to §7.5 |
| C3 | Hospital lat/lng retrieval has no integration contract → builder invents fallback logic | Low — add §7.6 ServiceNow hospital location read |

---

### Production Spec Checklist Report

Sections from `production-spec-checklist.md` evaluated against this spec. **Pass** = no findings trace here. **Partial** = concerns (C#) only. **Fail** = one or more blockers (B#) trace here.

| Section | Status | Key findings |
|---------|--------|--------------|
| Buildability | **Fail** | B1 and B3 create direct implementation contradictions — builder cannot implement RankerFeedback writes (uniqueness vs. re-rank) or EDITED validation (required vs. nullable edit_reason) without inventing a resolution. Both contradictions are in formal schema definitions, so the builder will follow the schema and get one of the two wrong. |
| Entity Precision | **Fail** | B1: uniqueness constraint directly contradicts BP5 re-rank requirement. B3: `edit_reason` is simultaneously required and nullable for the same action type in two separate spec locations. B4: `EXPIRED` status has an exit transition but no entry transition — it is unreachable dead code. |
| Delegation Boundaries | **Fail** | C1: DUPLICATE_IN_FLIGHT window (4 hours) is hardcoded in prose despite the spec's explicit claim that "all timeouts are configurable parameters." C2: APPROVED→candidates[0] enforcement is declared in the data model but absent from the API validation contract — the delegation boundary is not enforced at the system boundary. |
| Integration Contracts | **Fail** | B2: `submission_outcome` update path has no PATCH contract — endpoint, request, response, retry, and auth are all undefined. C3: hospital location coordinates are consumed in the scoring formula but the ServiceNow retrieval contract (endpoint, error handling, null-lat/lng fallback) is absent. |
| Validation Design | **Pass** | Five named edge cases with explicit setup, expected execution, and pass criteria. Three failure modes with recovery paths. Happy-path scenario is complete. Conditional on B1 and B3 fixes for the BP5 re-rank test case. |
| Assumptions Register | **Pass** | A1–A24 explicitly listed with confidence levels, failure modes, and named validation owners. Flagged assumptions have specific stakeholders assigned. This is the strongest section in the spec. |
| Economics Alignment | **Pass** | LLM is explicitly excluded from the MVP scoring hot path with rationale. Deterministic formula eliminates per-request LLM cost. §9 config file enables model substitution without code changes. No token budget issues to flag. |
| Governance | **Pass** | Audit log schema with full field-level detail, 2-year retention with explicit compliance rationale (non-PHI operational data), HITL SLAs, override logging with non-repudiation, and compliance scope all defined. |

---

### Attribution

> **Spec reviewed:** `04a-capability-spec-match-selection-Alexandra.md`
> **Spec creator:** Alexandra
> **Reviewer:** Benoit Charrier
