# D4b — Capability Specification (Lean): WS2 Matching Module
### Intake & Matching Agent — WS2 Nurse-to-Shift Matching Module

> **Lean version:** Sections abbreviated for rapid build. Sections skipped: Preamble §3–§7 (context engineering, risk register, gap analysis), §12 failure modes, §13 audit governance detail. All decisions and entities are builder-precise. Shared entities with D4a (MatchingBrief, HITLQueueItem) are referenced, not redefined.

---

## Shared entity reference

The following entities are defined in [D4a_capability_spec_WS1_lean.md §3](D4a_capability_spec_WS1_lean.md) and used by both specs. Do not redefine them here:

- **MatchingBrief** — input to the WS2 pipeline; status must be `READY_FOR_REVIEW` or `ADVANCED_TO_WS2` before WS2 begins
- **HITLQueueItem** — used to route escalations to the coordinator queue; same entity, same SLA rules

---

## §0. Agent Identity

| Field | Value |
|-------|-------|
| **Agent name** | Intake & Matching Agent — WS2 Module |
| **Job to be Done** | Given a validated MatchingBrief, query the nurse database, apply all hard credential and exclusion rules, classify profile notes, produce a ranked candidate shortlist, present it to the coordinator for selection, execute the approved submission to the facility, and manage multi-submission state and withdrawal. Replaces the coordinator's manual database-query-to-submission cycle (~120 decisions/coordinator/day). |
| **D3 reference** | WS2-JtD-1 (completeness gate), WS2-JtD-2 (candidate pool), WS2-JtD-5 (submission + multi-submission), WS2-JtD-6 (withdrawal); WS3-JtD-1 (credential re-check, embedded tool call) |
| **Delegation archetype** | Fully Agentic for WS2-JtD-2 (database query + credential gate + profile note classification); Agent-led + Human Oversight for WS2-JtD-5 and WS2-JtD-6; Human Only for WS2-JtD-3 (final candidate selection) and WS2-JtD-4 (exception resolution) |
| **Governance hard stop** | The agent MUST NOT execute a submission to a facility for a nurse whose credential status fails the HR-1/HR-2/HR-3 gate at the time of submission. The credential re-check (WS3-JtD-1) runs immediately before every submission and is non-bypassable. A nurse who passed the database query filter at shortlist-generation time but whose credential status has since changed MUST be removed from the shortlist and the coordinator MUST be notified. |

**KPIs:**

| KPI | Baseline | Target | How measured | Review cadence |
|-----|----------|--------|--------------|----------------|
| Time from MatchingBrief → shortlist in coordinator queue | 4.2-hr composite (baseline); shortlist step unquantified [assumption B1] | ≤ 8 minutes per brief | ServiceNow: brief ADVANCED_TO_WS2 timestamp → shortlist status = PRESENTED timestamp | Weekly |
| Shortlist accuracy (coordinator selects top-ranked candidate without editing shortlist) | 0% automated baseline | ≥ 70% of shortlists: coordinator selects agent's top-ranked candidate | ServiceNow: coordinator selection vs. agent rank order; weekly sample of 50 fills | Weekly |
| Pre-submission credential gate pass rate (no credential violations in agent-generated submissions) | 7% mismatch rate [scenario] — note: mismatch has two causes; credential portion not isolated [assumption B2] | 0% HR-1/HR-2/HR-3 violations in agent-submitted placements | Compliance team audit of agent-generated placements; monthly | Monthly |
| Withdrawal execution time after first confirmation | Unknown baseline [assumption B3] — coordinator manual; estimated minutes | ≤ 60 seconds from confirmation received to all other submissions withdrawn | ServiceNow: confirmation_received timestamp → withdrawal_executed timestamp | Weekly |
| HITL escalation rate for WS2 (exception fills) | Unknown baseline — all fills currently require coordinator judgment | ≤ 30% of fills route to WS2-JtD-4 exception path | ServiceNow: count of ShortlistResults with status = NO_CANDIDATES vs. PRESENTED | Weekly |

---

## §1. Purpose and Scope

**Purpose:** The WS2 module consumes a validated MatchingBrief (status = ADVANCED_TO_WS2), queries the structured nurse database to identify a credential-verified candidate pool, classifies profile notes on shortlisted candidates, ranks and presents the shortlist to the coordinator for selection, executes the approved submission to the facility, and manages multi-submission withdrawal state. It does not perform intake parsing (WS1), autonomous candidate selection (Human Only — coordinator), or nurse-facing communication (WS4 RPA).

**In scope:**
- Read MatchingBrief from ServiceNow; validate status = ADVANCED_TO_WS2 before proceeding
- Query nurse database on: specialty_required match, credential_level match, placement_state match (HR-3), availability on shift_datetime_start/end, proximity to facility
- Apply hard exclusion gates: HR-1 (credentials complete), HR-2 (credential-to-specialty match), HR-4 (DNR exclusion), HR-5 (rest period check)
- Read and classify nurse profile notes as BLOCKING, RISK_SIGNAL, or NEUTRAL per decision logic §6
- Rank shortlisted candidates: credential strength → availability confidence → proximity → profile note cleanliness
- Write CandidateShortlist record to ServiceNow and notify coordinator (AGENT_LOGS tier)
- Re-check credential status immediately before submission execution (WS3-JtD-1 embedded gate)
- Execute submission to facility via ServiceNow after coordinator selects candidate and approves
- Write PlacementSubmission record; update MultiSubmissionRecord for the submitted nurse
- Monitor open submissions for the same nurse; execute withdrawal from all other open submissions when the first facility confirmation is received (single confirmation path)
- Detect simultaneous confirmation (race condition); pause withdrawal and route to coordinator HITL (simultaneous path)
- Flag credential expiry proximity (≤ 30 days) on any candidate in the shortlist

**Out of scope:**
- Final candidate selection — Human Only per D3 ADR-1; agent presents the shortlist, coordinator selects
- Exception resolution when no candidate passes first-pass shortlist — Human Only per D3 (WS2-JtD-4)
- Specialty requirement ambiguity resolution (hard vs. soft) — resolved upstream in WS1; WS2 consumes the resolved value from MatchingBrief
- Nurse-facing communication (shift offer, confirmation request) — WS4 RPA workstream
- Credential verification for the compliance team — WS3 is compliance-team-owned; WS2 reads pre-verified status from the database
- Facility preference profile ranking (soft preferences, relationship heuristics) — data dependency; no structured facility profiles exist [D0C: U-3]; deferred to v2

---

## §2. Inputs and Outputs

**Inputs:**

| Input | Source system | Format | Required / Optional | Validation rule |
|-------|---------------|--------|---------------------|-----------------|
| MatchingBrief | ServiceNow — matching_briefs table | Structured JSON | Required | Status must be ADVANCED_TO_WS2; all required fields non-null and non-UNRESOLVED |
| Nurse database query result | Nurse database (structured DB confirmed by Marcus Reyes [DS-confirmed]) | Structured JSON array of NurseProfile records | Required | At least one record returned to proceed; zero records → NO_CANDIDATES path |
| DNR list per facility | [UNKNOWN — see §14 A-1] | Structured list of nurse_ids excluded per facility_id | Required | Must be checked before shortlist is finalised; if DNR list unavailable → [SCOPE-OUT] |
| Profile notes per candidate | Nurse database — notes field on NurseProfile | Free text, max 2000 chars per nurse | Optional | If notes field is null or empty → classify as NEUTRAL automatically |
| Confirmation event | ServiceNow — placement_submissions table (change event or polling) | Structured JSON (submission_id, confirmed_by_facility_id, confirmed_at) | Required for withdrawal step | Must contain submission_id resolvable to an open PlacementSubmission |

**Outputs:**

| Output | Target | Format | Trigger condition |
|--------|--------|--------|-------------------|
| CandidateShortlist record | ServiceNow — candidate_shortlists table | Structured JSON (see §3) | Every MatchingBrief with status ADVANCED_TO_WS2 that produces ≥ 1 qualifying candidate |
| HITLQueueItem (no candidates) | ServiceNow — hitl_queue table | Structured JSON; gap_type = MISSING_REQUIRED_FIELD (repurposed: no_candidates) | When zero candidates pass the credential and exclusion gates |
| PlacementSubmission record | ServiceNow — placement_submissions table | Structured JSON (see §3) | After coordinator selects candidate and approves submission |
| MultiSubmissionRecord update | ServiceNow — multi_submission_records table | Structured JSON (see §3) | After every PlacementSubmission write |
| Withdrawal execution (PlacementSubmission status update) | ServiceNow — placement_submissions table | PATCH to set status = WITHDRAWN | When first_confirmation received; simultaneous confirmation → HITLQueueItem instead |
| Agent audit log entry | ServiceNow — agent_audit_log table | JSON (same schema as D4a §13) | Every major action (query, shortlist write, submission, withdrawal) |

---

## §3. Entity Definitions

### Entity: NurseProfile (read-only from nurse database)

```
Entity: NurseProfile

Source: Nurse database (read-only; not written by this agent)

Attributes:
- nurse_id: UUID, primary key, immutable
- credential_status: enum [ACTIVE, EXPIRED, PENDING_RENEWAL, SUSPENDED], required
- specialty_credentials: array of enum [RN_GENERAL, RN_ICU, RN_ED, RN_PACU, RN_OR, LPN, CNA, RN_TELE], required — list of credentials held
- credential_expiry_dates: JSON object — specialty → ISO 8601 date, optional per specialty
- placement_states: array of strings — ISO 3166-2 US state codes where nurse holds active licence, required
- availability_status: enum [AVAILABLE, UNAVAILABLE, PARTIAL], required
- availability_schedule: JSON object — date range → available boolean, optional (null = rely on availability_status only)
- proximity_km_to_facility: float, units km, range 0–500, optional (null = proximity unknown; treat as valid but unranked)
- profile_notes: string, max 2000 chars, optional
- dnr_facility_ids: array of UUIDs — facilities from which this nurse is excluded (HR-4), required (empty array if none)
- last_shift_end: ISO 8601 timestamp UTC, optional — used for HR-5 rest period check
- offboarded: boolean, required — offboarded nurses MUST NOT appear in any shortlist regardless of other criteria

State machine: Not owned by this agent — read-only. No transitions.

Naming conventions:
- Table: nurse_profiles (assumed name — see §14 A-2)
- Fields: snake_case
```

---

### Entity: CandidateShortlist

```
Entity: CandidateShortlist

Attributes:
- id: UUID, primary key, immutable, generated on creation
- matching_brief_id: UUID, required, foreign key to MatchingBrief, on delete: restrict, immutable
- facility_id: UUID, required, copied from MatchingBrief, immutable
- shift_datetime_start: ISO 8601 timestamp UTC, required, copied from MatchingBrief, immutable
- candidates: array of ShortlistCandidate (see below), required — min 0, max 10 entries
- status: enum [GENERATING, PRESENTED, SELECTION_MADE, EXPIRED, NO_CANDIDATES], required
- selected_nurse_id: UUID, optional — set when coordinator makes selection; null until then
- selected_at: ISO 8601 timestamp UTC, optional
- selected_by: UUID (coordinator user ID), optional
- generated_at: ISO 8601 timestamp UTC, required, set on creation, immutable
- presented_at: ISO 8601 timestamp UTC, optional — set when shortlist written to coordinator queue
- expires_at: ISO 8601 timestamp UTC, required — generated_at + 60 minutes [assumption B4: shortlist validity window]
- created_at: ISO 8601 timestamp UTC, immutable
- updated_at: ISO 8601 timestamp UTC

Relationships:
- matching_brief_id: UUID, foreign key to MatchingBrief, many-to-one, on delete: restrict

State machine:
- Initial state: GENERATING
- GENERATING → PRESENTED: shortlist written to coordinator queue with ≥ 1 candidate
- GENERATING → NO_CANDIDATES: zero candidates pass all gates; HITLQueueItem created
- PRESENTED → SELECTION_MADE: coordinator selects a candidate and approves submission
- PRESENTED → EXPIRED: current_time > expires_at and status = PRESENTED
- SELECTION_MADE → (terminal): coordinator selection triggers PlacementSubmission creation
- NO_CANDIDATES → (terminal): HITLQueueItem owns the escalation path
- EXPIRED → (terminal): coordinator must re-trigger matching (new MatchingBrief or re-run)

Invalid transitions:
- NO_CANDIDATES → PRESENTED: FORBIDDEN — if no candidates found, shortlist cannot be presented; re-run matching with updated criteria
- EXPIRED → SELECTION_MADE: FORBIDDEN — expired shortlist cannot be acted upon; re-run required
- SELECTION_MADE → PRESENTED: FORBIDDEN — selection is final; changes require a new shortlist cycle
- PRESENTED → GENERATING: FORBIDDEN — shortlist cannot revert to in-progress once presented

Validation rules:
- expires_at > generated_at: boolean, reject on creation if false
- selected_nurse_id must reference a nurse_id present in candidates[] when status = SELECTION_MADE: boolean
- candidates[] length ≤ 10: boolean

Naming conventions:
- Table: candidate_shortlists (assumed — see §14 A-2)
- ShortlistCandidate is an embedded JSON object, not a separate table
```

### Embedded type: ShortlistCandidate

```
ShortlistCandidate (embedded in CandidateShortlist.candidates[])

Attributes:
- nurse_id: UUID, required, references NurseProfile
- rank: integer, required, range 1–10, 1 = top-ranked
- credential_match_score: float, required, range 0.0–1.0 — proportion of required credentials held
- availability_confirmed: boolean, required — true if availability_schedule confirms shift window; false if inferred from availability_status only
- proximity_km: float, optional, units km — null if unknown
- profile_note_classification: enum [BLOCKING, RISK_SIGNAL, NEUTRAL, NO_NOTES], required
- profile_note_excerpt: string, max 500 chars, optional — relevant text from profile_notes; null if NO_NOTES or NEUTRAL with no notable content
- credential_expiry_warning: boolean, required — true if any held credential expires within 30 days of shift_datetime_start
- dnr_cleared: boolean, required — true if nurse_id not in facility's dnr_facility_ids
- rest_period_cleared: boolean, required — true if HR-5 rest period check passes
- display_flags: array of strings — human-readable flags shown to coordinator (e.g., "Credential expires in 14 days", "Profile note: risk signal")
```

---

### Entity: PlacementSubmission

```
Entity: PlacementSubmission

Attributes:
- id: UUID, primary key, immutable, generated on creation
- shortlist_id: UUID, required, foreign key to CandidateShortlist, on delete: restrict, immutable
- matching_brief_id: UUID, required, foreign key to MatchingBrief, on delete: restrict, immutable
- nurse_id: UUID, required, immutable — nurse submitted
- facility_id: UUID, required, immutable — facility submitted to
- shift_datetime_start: ISO 8601 timestamp UTC, required, immutable
- shift_datetime_end: ISO 8601 timestamp UTC, required, immutable
- status: enum [OPEN, CONFIRMED, WITHDRAWN, EXPIRED_UNFILLED], required
- submitted_at: ISO 8601 timestamp UTC, required, immutable — set when agent executes submission
- submitted_by_agent: boolean, required, immutable — true for agent-executed submissions
- approved_by: UUID (coordinator user ID), required — coordinator who approved the submission
- approved_at: ISO 8601 timestamp UTC, required, immutable
- confirmation_received_at: ISO 8601 timestamp UTC, optional — set on CONFIRMED
- withdrawal_executed_at: ISO 8601 timestamp UTC, optional — set on WITHDRAWN
- withdrawal_reason: enum [CONFIRMED_ELSEWHERE, RACE_CONDITION_RESOLVED_BY_COORDINATOR, COORDINATOR_CANCELLED], optional
- created_at: ISO 8601 timestamp UTC, immutable
- updated_at: ISO 8601 timestamp UTC

Relationships:
- shortlist_id: UUID, foreign key to CandidateShortlist, many-to-one, on delete: restrict
- matching_brief_id: UUID, foreign key to MatchingBrief, many-to-one, on delete: restrict

State machine:
- Initial state: OPEN
- OPEN → CONFIRMED: facility confirmation event received for this submission_id
- OPEN → WITHDRAWN: withdrawal executed (either automatically on another submission being confirmed, or by coordinator)
- OPEN → EXPIRED_UNFILLED: shift_datetime_start has passed and status is still OPEN
- CONFIRMED → WITHDRAWN: FORBIDDEN — a confirmed placement cannot be withdrawn by the agent; only coordinator can cancel (out of scope for agent)
- WITHDRAWN → OPEN: FORBIDDEN — withdrawn is terminal for this submission; a new submission must be created
- EXPIRED_UNFILLED → any: FORBIDDEN — terminal state

Invalid transitions:
- CONFIRMED → WITHDRAWN: FORBIDDEN — once confirmed, only coordinator-initiated cancellation applies; out of agent scope
- WITHDRAWN → CONFIRMED: FORBIDDEN — terminal; new submission required
- OPEN → OPEN: FORBIDDEN — no self-transitions

Guard conditions:
- Transition OPEN → CONFIRMED requires: confirmation_received_at is set AND confirmation event facility_id matches this submission's facility_id
- Transition OPEN → WITHDRAWN (automated) requires: another PlacementSubmission for the same nurse_id has transitioned to CONFIRMED AND withdrawal is not for the confirming submission itself

Naming conventions:
- Table: placement_submissions (assumed — see §14 A-2)
```

---

### Entity: MultiSubmissionRecord

```
Entity: MultiSubmissionRecord

Attributes:
- id: UUID, primary key, immutable
- nurse_id: UUID, required, immutable — nurse being tracked
- open_submission_ids: array of UUIDs, required — IDs of all OPEN PlacementSubmissions for this nurse
- last_updated_at: ISO 8601 timestamp UTC, required
- race_condition_detected: boolean, required — set true if two confirmations arrive before withdrawal completes
- race_condition_submission_ids: array of UUIDs, optional — the two submission IDs in conflict (populated when race_condition_detected = true)
- created_at: ISO 8601 timestamp UTC, immutable
- updated_at: ISO 8601 timestamp UTC

State machine:
- Not a primary workflow entity; updated as a side effect of PlacementSubmission state changes.
- Invariant: open_submission_ids must always reflect current OPEN PlacementSubmissions for nurse_id.
- Terminal condition: record deleted when open_submission_ids becomes empty (no more open submissions for this nurse).

Naming conventions:
- Table: multi_submission_records (assumed — see §14 A-2)
```

---

## §4. Activity Catalog

| Task ID | Task name | Task type | Delegation level | Data required | Tool required | Risk level |
|---------|-----------|-----------|-----------------|---------------|---------------|------------|
| WS2-T1 | Validate MatchingBrief status before beginning | Decision | Fully agentic | MatchingBrief from ServiceNow | ServiceNow read API | Medium |
| WS2-T2 | Query nurse database — credential, availability, proximity | Retrieval | Fully agentic | NurseProfile records; MatchingBrief fields | Nurse database query API | High |
| WS2-T3 | Apply HR-1 credential completeness gate | Decision | Fully agentic | credential_status field per nurse | Nurse database | High |
| WS2-T4 | Apply HR-2 credential-to-specialty match gate | Decision | Fully agentic | specialty_credentials[] per nurse; specialty_required from brief | Nurse database | High |
| WS2-T5 | Apply HR-3 placement-state licence check | Decision | Fully agentic | placement_states[] per nurse; facility_state from brief | Nurse database | High |
| WS2-T6 | Apply HR-4 DNR exclusion check per facility | Decision | Fully agentic | dnr_facility_ids[] per nurse; facility_id from brief | DNR list lookup [SCOPE-OUT if unavailable — see §14 A-1] | High |
| WS2-T7 | Apply HR-5 mandatory rest period check | Decision | Fully agentic | last_shift_end per nurse; shift_datetime_start from brief | Nurse database | Medium |
| WS2-T8 | Classify profile notes (BLOCKING / RISK_SIGNAL / NEUTRAL) | Reasoning | Fully agentic | profile_notes text per candidate; facility_id; specialty context | LLM (claude-sonnet-4-6 tool_use) [assumption B5] | High |
| WS2-T9 | Rank shortlisted candidates | Decision | Fully agentic | All ShortlistCandidate fields | None (in-process calculation) | Medium |
| WS2-T10 | Flag credential expiry proximity (≤ 30 days) | Decision | Fully agentic | credential_expiry_dates per candidate; shift_datetime_start | None | Medium |
| WS2-T11 | Write CandidateShortlist to ServiceNow and notify coordinator | Action | Agent acts, human notified | CandidateShortlist object | ServiceNow write API | Medium |
| WS2-T12 | Receive coordinator candidate selection | Retrieval | Human decides | Coordinator input from HITL queue | ServiceNow read API | High |
| WS2-T13 | Re-check credential status immediately before submission (WS3-JtD-1) | Decision | Fully agentic | NurseProfile for selected nurse at time of submission | Nurse database query API | High |
| WS2-T14 | Execute submission to facility via ServiceNow | Action | Agent proposes, human approves | PlacementSubmission fields; coordinator approval token | ServiceNow write API | High |
| WS2-T15 | Write PlacementSubmission and update MultiSubmissionRecord | Action | Fully agentic | Submission result | ServiceNow write API | Medium |
| WS2-T16 | Monitor open submissions for same nurse; detect confirmation event | Retrieval | Agent acts, human notified | MultiSubmissionRecord; placement_submissions table | ServiceNow polling or event | High |
| WS2-T17 | Execute withdrawal from other open submissions (single confirmation) | Action | Agent acts, human notified | Other open PlacementSubmission IDs; confirmed submission ID | ServiceNow write API | High |
| WS2-T18 | Detect simultaneous confirmation (race condition) and route to HITL | Decision + Action | Agent proposes, human approves | Two confirming facility IDs; MultiSubmissionRecord | ServiceNow write API; HITL queue | High |

---

## §5. Requirements

```
REQ-B-1: Credential gate non-bypassability (governance hard stop)
The agent MUST NOT write a PlacementSubmission record for any nurse whose credential status
fails the HR-1/HR-2/HR-3 check at the time WS2-T13 (pre-submission re-check) runs,
regardless of whether the nurse passed the initial shortlist gate at WS2-T2 through WS2-T5.
Acceptance criterion: 0 PlacementSubmission records written where the corresponding
NurseProfile had credential_status != ACTIVE at submission time — verified by weekly
automated join query: placement_submissions ⋈ nurse_profiles on nurse_id,
filtered to submissions in the past 7 days.
Delegation tier: AGENT_ALONE for the gate check; submission is BLOCKED if gate fails.
Error handling: If credential status has changed since shortlist generation (nurse was on
shortlist but fails re-check at WS2-T13): remove nurse from shortlist; write a flag to
the CandidateShortlist record; notify coordinator via HITLQueueItem that the previously
selected candidate is no longer eligible; coordinator must select an alternative.

REQ-B-2: Profile note classification — AI-native matching
The agent MUST classify every non-empty profile note on a shortlisted candidate as
BLOCKING, RISK_SIGNAL, or NEUTRAL relative to the specific facility_id and
specialty_required in the MatchingBrief (not in the abstract).
Acceptance criterion: BLOCKING candidates MUST NOT appear on the presented shortlist;
RISK_SIGNAL candidates MUST appear with the display_flag "Profile note: risk signal —
review before approving" and the profile_note_excerpt field populated;
NEUTRAL and NO_NOTES candidates appear without flags.
Verified by: weekly audit of 20 random shortlists; coordinator reports of surprise
profile note content are the primary detection mechanism for miscalibration.
Delegation tier: AGENT_ALONE.
Error handling: If the LLM classification call fails (API error, timeout), treat the
note as RISK_SIGNAL (conservative default); flag with display_flag "Note classification
unavailable — review manually"; do NOT classify as NEUTRAL on failure.

REQ-B-3: Pre-submission credential re-check (WS3-JtD-1)
The agent MUST re-query the nurse database for the selected nurse's current credential_status
immediately before writing the PlacementSubmission record (WS2-T13). The re-check MUST
occur after coordinator approval and before the ServiceNow submission write.
Acceptance criterion: Every PlacementSubmission record has a corresponding audit log entry
with action = PRE_SUBMISSION_CREDENTIAL_RECHECK and a timestamp within 60 seconds of
the PlacementSubmission.submitted_at timestamp — verified by daily audit log reconciliation.
Delegation tier: AGENT_ALONE.
Error handling: If the nurse database is unavailable at re-check time: BLOCK the submission;
write HITLQueueItem notifying coordinator that submission is held pending database availability;
do NOT proceed without a successful re-check.

REQ-B-4: Withdrawal execution on single confirmation
When the agent detects that one PlacementSubmission for a given nurse_id has transitioned
to CONFIRMED status, it MUST execute withdrawal (status → WITHDRAWN) on all other OPEN
PlacementSubmissions for the same nurse_id within 60 seconds of the confirmation event.
Acceptance criterion: Time from confirmation_received_at to latest withdrawal_executed_at
across all withdrawn submissions ≤ 60 seconds — measured weekly from ServiceNow timestamps.
Delegation tier: AGENT_ACTS_HUMAN_NOTIFIED (withdrawal executes automatically; coordinator
is notified of which facilities were withdrawn from).
Error handling: If a ServiceNow write fails during withdrawal, retry up to 3 times with
5-second backoff; if all retries fail, alert coordinator immediately with the specific
submission IDs that failed withdrawal — coordinator must manually withdraw to prevent
double-booking.

REQ-B-5: Race condition detection and HITL escalation
When two or more PlacementSubmissions for the same nurse_id receive a CONFIRMED event
within the same 60-second window (simultaneous confirmation), the agent MUST:
(1) NOT execute automated withdrawal for either confirmation;
(2) Set race_condition_detected = true on the MultiSubmissionRecord;
(3) Write a HITLQueueItem with gap_type = RACE_CONDITION and the two conflicting
submission IDs, SLA 10 minutes;
(4) Notify the coordinator to select which facility confirmation to honour.
Acceptance criterion: 100% of simultaneous confirmation events result in a HITLQueueItem
within 30 seconds; 0 automated withdrawals executed in a race condition window —
verified by audit log + MultiSubmissionRecord.race_condition_detected = true check.
Delegation tier: AGENT_PROPOSES, HUMAN_DECIDES.
Error handling: If race condition detection fails (two withdrawals both fire), flag as
a governance breach in the audit log; alert supervisor immediately; log both submission IDs.

REQ-B-6: Shortlist escalation when no candidates pass gates
When zero NurseProfile records pass all hard gates (HR-1 through HR-5), the agent MUST:
(1) Write a CandidateShortlist with status = NO_CANDIDATES and candidates = [];
(2) Write a HITLQueueItem notifying the coordinator of the no-candidate result, including
the count of candidates filtered at each gate (e.g., "12 filtered at HR-2, 3 at HR-4");
(3) NOT attempt to submit a below-threshold candidate without coordinator instruction.
Acceptance criterion: 100% of NO_CANDIDATES shortlists have a corresponding HITLQueueItem
with gate-level filter counts populated — verified by weekly join query.
Delegation tier: AGENT_ACTS_HUMAN_NOTIFIED (shortlist status written automatically);
exception resolution is HUMAN_DECIDES.
Error handling: If gate-level filter counts cannot be computed (database query error),
write HITLQueueItem without counts and add note: "Gate filter counts unavailable —
database error. See audit log [entry ID]."
```

---

## §6. Decision Logic

```
Decision: Candidate qualification gate (hard rules)
Input: NurseProfile record for each candidate; MatchingBrief fields (specialty_required,
credential_level, placement_state derived from facility_id, shift_datetime_start,
shift_datetime_end)
Logic:
  FOR EACH candidate IN nurse_database_results:
    IF candidate.offboarded == true THEN
      exclude — no further checks
    IF candidate.credential_status != ACTIVE THEN
      exclude — HR-1 violation; log gate = HR1_FAIL
    IF specialty_required NOT IN candidate.specialty_credentials THEN
      exclude — HR-2 violation; log gate = HR2_FAIL
    IF facility_placement_state NOT IN candidate.placement_states THEN
      exclude — HR-3 violation; log gate = HR3_FAIL
    IF facility_id IN candidate.dnr_facility_ids THEN
      exclude — HR-4 violation; log gate = HR4_FAIL
    IF candidate.last_shift_end is not null AND
       (shift_datetime_start - candidate.last_shift_end) < 8 hours THEN
      exclude — HR-5 violation; log gate = HR5_FAIL
      [assumption B6: 8-hour minimum rest period — not explicitly stated in scenario;
      derived from FLSA and standard travel nursing contracts; see §14 A-3]
    IF candidate.availability_status == UNAVAILABLE THEN
      exclude — not available; log gate = AVAILABILITY_FAIL
    IF candidate.availability_schedule is not null AND
       shift_datetime_start NOT IN candidate.availability_schedule[available=true] THEN
      exclude — schedule conflict; log gate = AVAILABILITY_SCHEDULE_FAIL
    ELSE
      include in shortlist
  IF shortlist is empty THEN
    write CandidateShortlist(status=NO_CANDIDATES) → trigger REQ-B-6 path
Output: Filtered candidate list; gate failure counts per gate code
Delegation tier: AGENT_ALONE — all checks are binary rule evaluations
Confidence gate: N/A — deterministic rule application; no scoring
Worked example:
  Input: 18 candidates returned from DB query for RN_ICU at Facility FAC-0042, state TX, shift 2026-05-20 19:00–07:00
  HR-1 filter: 2 with credential_status=EXPIRED excluded → 16 remaining
  HR-2 filter: 4 without RN_ICU in specialty_credentials excluded → 12 remaining
  HR-3 filter: 1 with no TX licence excluded → 11 remaining
  HR-4 filter: 1 on FAC-0042 DNR list excluded → 10 remaining
  HR-5 filter: 1 whose last shift ends at 2026-05-20 15:00 (only 4 hours rest) excluded → 9 remaining
  AVAILABILITY filter: 3 with UNAVAILABLE status excluded → 6 remaining
  Output: 6 candidates passed all gates; proceed to profile note classification

Decision: Profile note classification
Input: profile_notes string (free text, max 2000 chars); facility_id; specialty_required;
shift context from MatchingBrief
Logic:
  IF profile_notes is null OR profile_notes == "" THEN
    classification = NO_NOTES — no LLM call needed
  ELSE
    Call LLM (claude-sonnet-4-6) with prompt:
      "You are classifying a nurse profile note for a specific placement.
       Facility: {facility_id_name}. Shift specialty: {specialty_required}.
       Profile note: {profile_notes}
       Classify this note as exactly one of:
       BLOCKING: The note contains explicit exclusions or prior incidents that directly
         prevent this nurse from being submitted to this facility for this specialty.
         Examples: 'Do not submit to Facility X', 'prior medication error at this unit',
         'terminated by this facility'.
       RISK_SIGNAL: The note contains information that should be reviewed by the coordinator
         before approving submission — it does not hard-block but warrants human judgment.
         Examples: 'two late arrivals in Q3', 'complained about shift length', 
         'prefers day shifts but will accept nights'.
       NEUTRAL: The note contains no information relevant to this specific placement.
         Examples: 'prefers east-side facilities' (nurse is being submitted to west-side),
         'speaks Spanish' (no Spanish-language requirement for this shift).
       Return JSON: {'classification': 'BLOCKING'|'RISK_SIGNAL'|'NEUTRAL',
                     'reasoning': '<one sentence>', 'relevant_excerpt': '<max 200 chars>'}"
    IF LLM call fails (timeout or API error) THEN
      classification = RISK_SIGNAL [conservative default — REQ-B-2]
  IF classification == BLOCKING THEN
    exclude candidate from shortlist; log profile_note_classification = BLOCKING
  ELSE
    include candidate; set profile_note_classification and profile_note_excerpt
Output: Classification per candidate; BLOCKING candidates excluded from shortlist
Delegation tier: AGENT_ALONE — LLM reasoning, reviewed by coordinator via shortlist flags
Confidence gate: No numeric threshold — classification is categorical from LLM.
  If the LLM returns anything other than one of the three valid values: treat as RISK_SIGNAL;
  flag display: "Note classification parse error — review manually."
Worked example:
  Input: nurse_id = N-1042, facility = "St. Mary's ICU", specialty = RN_ICU
  profile_notes = "Declined two consecutive ICU shifts at St. Mary's citing acuity concerns.
                   Coordinator Jess flagged: 'may not be reliable for complex ICU assignments here.'"
  LLM output: {"classification": "RISK_SIGNAL", "reasoning": "History of declining at this
    facility raises reliability concern but is not a hard exclusion.",
    "relevant_excerpt": "Declined two ICU shifts at St. Mary's; reliability concern flagged."}
  Output: candidate included; profile_note_classification = RISK_SIGNAL;
  display_flag = "Profile note: risk signal — review before approving"

Decision: Candidate ranking
Input: Filtered, note-classified ShortlistCandidate list
Logic:
  Rank by the following tiebreaker sequence (lower rank number = higher priority):
  1. Profile note cleanliness: NO_NOTES or NEUTRAL ranked above RISK_SIGNAL
  2. Credential expiry: no expiry warning ranked above expiry_warning = true
  3. Availability confidence: availability_confirmed = true ranked above false
  4. Proximity: lower proximity_km ranked higher; null proximity ranked last within tier
  Assign rank 1 to the top candidate; increment for each subsequent candidate.
  Maximum 5 candidates presented on the shortlist [assumption B7: coordinator UX limit].
  If more than 5 pass all gates, take top 5 by the ranking logic above.
Output: ShortlistCandidate list with rank field set, max 5 entries
Delegation tier: AGENT_ALONE
Confidence gate: N/A — deterministic tiebreaker sequence
Worked example:
  Input: 6 qualifying candidates after gate + note classification
    N-1042: RISK_SIGNAL note, no expiry, availability_confirmed=true, proximity=8km
    N-2031: NO_NOTES, expiry in 25 days, availability_confirmed=true, proximity=5km
    N-3105: NO_NOTES, no expiry, availability_confirmed=true, proximity=12km
    N-4088: NEUTRAL note, no expiry, availability_confirmed=false, proximity=3km
    N-5017: NO_NOTES, no expiry, availability_confirmed=true, proximity=22km
    N-6204: NO_NOTES, no expiry, availability_confirmed=true, proximity=7km
  Ranking:
    Tier 1 (NO_NOTES/NEUTRAL, no expiry, confirmed, sorted by proximity):
      rank 1: N-3105 (NO_NOTES, no expiry, confirmed, 12km) — wait, N-6204 (7km) < N-3105 (12km)
      rank 1: N-6204 (NO_NOTES, no expiry, confirmed, 7km)
      rank 2: N-3105 (NO_NOTES, no expiry, confirmed, 12km)
      rank 3: N-5017 (NO_NOTES, no expiry, confirmed, 22km)
      rank 4: N-4088 (NEUTRAL, no expiry, not confirmed, 3km) — drops for availability_confirmed=false
    Tier 2 (NO_NOTES but expiry warning):
      rank 5: N-2031 (NO_NOTES, expiry in 25 days, confirmed, 5km)
    RISK_SIGNAL (N-1042): rank 6 — excluded from presented shortlist (max 5)
  Output: [N-6204 rank 1, N-3105 rank 2, N-5017 rank 3, N-4088 rank 4, N-2031 rank 5]
  N-1042 included in shortlist record but not shown in the top-5 presented view;
  coordinator can expand to see all qualifying candidates on request.

Decision: Withdrawal trigger — single vs. simultaneous confirmation
Input: Confirmation events received in the last 60 seconds for a given nurse_id;
MultiSubmissionRecord for that nurse_id
Logic:
  IF COUNT(confirmation events for nurse_id in last 60 seconds) == 1 THEN
    confirming_submission = the confirmed PlacementSubmission
    all_other_open = MultiSubmissionRecord.open_submission_ids
                     EXCLUDING confirming_submission.id
    FOR EACH submission_id IN all_other_open:
      PATCH PlacementSubmission(id=submission_id, status=WITHDRAWN,
            withdrawal_executed_at=now(),
            withdrawal_reason=CONFIRMED_ELSEWHERE)
    UPDATE MultiSubmissionRecord(open_submission_ids=[confirming_submission.id])
    LOG action=WITHDRAWAL_EXECUTED, submission_ids=all_other_open
    NOTIFY coordinator: "Nurse {nurse_id} confirmed at {facility}. Withdrawn from {n} other submissions."
  ELSE IF COUNT(confirmation events for nurse_id in last 60 seconds) > 1 THEN
    SET MultiSubmissionRecord.race_condition_detected = true
    SET MultiSubmissionRecord.race_condition_submission_ids = [all confirming IDs]
    DO NOT execute any withdrawal
    WRITE HITLQueueItem(gap_type=RACE_CONDITION,
          agent_note="Simultaneous confirmations received from {facility_list}.
          Please select which facility to honour and withdraw from the other(s).",
          sla_deadline=now() + 10 minutes)
    LOG action=RACE_CONDITION_DETECTED
  ELSE
    no action (COUNT == 0)
Output: Withdrawal records updated (single path) or HITL created (race condition)
Delegation tier: AGENT_ACTS_HUMAN_NOTIFIED for single; AGENT_PROPOSES for race condition
Confidence gate: N/A — deterministic event counting; 60-second window is the discriminator
Worked example (single):
  Input: nurse_id = N-6204; confirmation from FAC-0042 at 14:33:05; 
         open_submission_ids = [SUB-001 (FAC-0042), SUB-002 (FAC-0077), SUB-003 (FAC-0011)]
  Branch taken: 1 confirmation in 60-second window → single confirmation path
  Output: SUB-001 → CONFIRMED; SUB-002 and SUB-003 → WITHDRAWN;
  Coordinator notified: "N-6204 confirmed at FAC-0042. Withdrawn from FAC-0077 and FAC-0011."
```

---

## §7. Escalation Triggers

| Trigger condition | Threshold | Action | Notified party | SLA | If SLA breached |
|-------------------|-----------|--------|----------------|-----|-----------------|
| Zero candidates pass all hard gates (REQ-B-6) | candidates[] length = 0 | Write CandidateShortlist(NO_CANDIDATES); write HITLQueueItem with gate filter counts | On-call coordinator | 30 minutes | HITLQueueItem → EXPIRED; supervisor SMS alert |
| Selected candidate fails pre-submission credential re-check (REQ-B-3) | credential_status != ACTIVE at WS2-T13 | Block submission; flag CandidateShortlist; write HITLQueueItem | On-call coordinator | 15 minutes | Supervisor alert; submission remains blocked |
| Race condition: simultaneous confirmations (REQ-B-5) | ≥ 2 confirmations for same nurse_id within 60 seconds | Halt all withdrawals; write HITLQueueItem(RACE_CONDITION) | On-call coordinator | 10 minutes | Supervisor alert; both confirmations remain OPEN; risk of double-booking escalates |
| Credential expiry ≤ 30 days on shortlisted candidate | expiry_days_until ≤ 30 | Add display_flag "Credential expires in N days" to ShortlistCandidate; no block; notify in shortlist | Coordinator (via shortlist) | N/A — informational only | N/A |
| Withdrawal ServiceNow write fails after 3 retries | 3 retries exhausted | Alert coordinator of specific submission IDs that failed withdrawal | On-call coordinator | 5 minutes | Supervisor alert; coordinator must manually withdraw |
| CandidateShortlist expires without selection (PRESENTED → EXPIRED) | current_time > expires_at | Set status = EXPIRED; write HITLQueueItem notifying coordinator | On-call coordinator | 30 minutes | Coordinator re-runs matching; supervisor alert if repeat expiry on same brief |
| Nurse database unavailable at re-check time (WS2-T13) | API error or timeout after 3 retries | Block submission; hold in HITLQueueItem pending DB recovery | On-call coordinator | 5 minutes | Supervisor + engineering on-call alert |

---

## §8. Autonomy Matrix

**AGENT DECIDES ALONE:**
- Apply all hard gate checks (HR-1 through HR-5) to candidate pool
- Apply offboarded exclusion check
- Classify profile notes as BLOCKING, RISK_SIGNAL, NEUTRAL, NO_NOTES
- Exclude BLOCKING candidates from presented shortlist
- Rank candidates by tiebreaker sequence
- Write CandidateShortlist (GENERATING → PRESENTED or NO_CANDIDATES)
- Flag credential expiry warnings on shortlist candidates
- Re-check credential status before submission (WS2-T13)
- Log multi-submission record updates
- Execute single-confirmation withdrawal (within 60 seconds)
- Write all audit log entries

**AGENT ACTS, HUMAN NOTIFIED AFTER:**
- Present ranked shortlist to coordinator (coordinator sees it; no approval needed to view)
- Execute single-confirmation withdrawal and notify coordinator of which facilities were withdrawn from
- Flag profile note risk signals on shortlist (coordinator sees flags without being asked to approve)
- Flag credential expiry warnings on shortlist

**AGENT PROPOSES, HUMAN APPROVES BEFORE ACTION:**
- Execute submission to facility — coordinator must select a candidate AND click to approve before PlacementSubmission is written (Phase 1; see D3 ADR-1 and hardest boundary note)
- Resolve race condition — agent writes HITLQueueItem; coordinator selects which facility to honour; agent executes withdrawal only after coordinator instruction is received
- Resume a blocked submission after credential re-check failure — coordinator must re-select from updated shortlist

**HUMAN TAKES OVER (agent supports only):**
- Select final candidate from shortlist — Human Only; agent presents, coordinator selects
- Resolve no-candidate exception (WS2-JtD-4) — agent writes the NO_CANDIDATES shortlist and HITL item; coordinator decides to expand search, seek facility exception, or flag unfillable
- Decide whether to block, hold, or escalate borderline credential — if coordinator asks for guidance, agent can surface the credential expiry date and renewal status; decision is Human Only
- Manage facility communication in a race condition — agent flags it; coordinator makes and handles the apology

**Enforcement mechanism:** The submission gate (AGENT PROPOSES, HUMAN APPROVES) is **procedure-dependent in Phase 1** — the agent requires an `approved_by` UUID field populated on the PlacementSubmission before writing it, but ServiceNow does not currently enforce a workflow lock that technically prevents a write without a prior approval token. The `approved_by` field is validated by the agent code before executing the write. A ServiceNow workflow state that blocks PlacementSubmission creation without a coordinator approval event is the recommended technical enforcement and is a **pre-deployment prerequisite** (same risk as D4a enforcement gap). Until that constraint is confirmed, the governance is procedure-dependent and is logged as a governance risk in the audit log per submission.

---

## §9. Integration Contracts

### Integration: Nurse Database — Candidate Query (Read)

1. **Purpose:** Query the structured nurse database to retrieve candidate NurseProfile records matching the MatchingBrief's credential, availability, and proximity requirements. Agent reads only — does not write to the nurse database.
2. **System:** Nurse database (structured DB — confirmed by Marcus Reyes; specific system name not stated in scenario [DS-confirmed]). Base URL: `[SCOPE-OUT — system identity and API spec not confirmed; see §14 A-2]`.
3. **Authentication:** `[SCOPE-OUT — auth method unknown; assume API key or OAuth 2.0 service account; see §14 A-2]`.
4. **Endpoint (assumed REST pattern — see §14 A-2):**
   ```
   POST /api/nurses/query
   Body:
   {
     "specialty_credentials": ["RN_ICU"],            // required — from specialty_required
     "credential_level": "RN",                        // required
     "placement_states": ["TX"],                      // required — derived from facility location
     "availability_date": "2026-05-20",               // required — from shift_datetime_start
     "shift_start": "2026-05-20T19:00:00Z",           // required
     "shift_end": "2026-05-21T07:00:00Z",             // required
     "max_proximity_km": 100,                         // optional; null = no proximity filter
     "include_fields": ["nurse_id", "credential_status", "specialty_credentials",
                        "credential_expiry_dates", "placement_states",
                        "availability_status", "availability_schedule",
                        "proximity_km_to_facility", "profile_notes",
                        "dnr_facility_ids", "last_shift_end", "offboarded"]
   }

   Success response (200):
   {
     "results": [
       {
         "nurse_id": "uuid-here",
         "credential_status": "ACTIVE",
         "specialty_credentials": ["RN_ICU", "RN_TELE"],
         "credential_expiry_dates": {"RN_ICU": "2027-03-01"},
         "placement_states": ["TX", "OK"],
         "availability_status": "AVAILABLE",
         "availability_schedule": null,
         "proximity_km_to_facility": 8.2,
         "profile_notes": "Two late arrivals Q3 2025 at St. Mary's.",
         "dnr_facility_ids": [],
         "last_shift_end": "2026-05-18T07:00:00Z",
         "offboarded": false
       }
     ],
     "total_count": 18,
     "query_time_ms": 240
   }

   Error responses:
     400 → log invalid query parameters; do NOT retry; alert on-call
     401 → refresh credentials and retry once; alert if still 401
     404 → no results (treat as empty result set, not an error)
     429 → wait 10 seconds, retry; log throttle event
     500/503 → retry 3x with 5s/10s/20s backoff; if all fail → block submission,
               write HITLQueueItem (REQ-B-3 applies)
   ```
5. **Error handling:** 400 → no retry. 401 → 1 retry after credential refresh. 429 → 10s wait + retry. 500/503 → 3 retries then block + HITL.
6. **Rate limits:** `[SCOPE-OUT — rate limits for nurse database API not confirmed; see §14 A-2]`. Conservative default: 30 queries/minute; 1 query per MatchingBrief at shortlist-generation time + 1 re-check query per submission.
7. **Data mapping:**
   - `nurse_id` → `ShortlistCandidate.nurse_id`, `PlacementSubmission.nurse_id`
   - `credential_status` → HR-1 gate input; `ACTIVE` = pass
   - `specialty_credentials[]` → HR-2 gate: must contain MatchingBrief.specialty_required
   - `placement_states[]` → HR-3 gate: must contain facility_placement_state
   - `dnr_facility_ids[]` → HR-4 gate: must NOT contain MatchingBrief.facility_id
   - `last_shift_end` → HR-5 gate: shift_datetime_start - last_shift_end must be ≥ 8 hours
   - `profile_notes` → WS2-T8 LLM classification input
   - `credential_expiry_dates` → WS2-T10 expiry flag (≤ 30 days from shift_datetime_start)
8. **State sync:** On-demand query per MatchingBrief (shortlist generation) + on-demand re-check per submission (WS2-T13). No caching — credential status must be fresh at submission time.
9. **Fallback:** If unavailable: block; do not proceed without fresh data. No stale-cache fallback for credential checks.
10. **Logging:** Log per query: matching_brief_id, query parameters, total_count returned, candidates passing each gate, query latency.

---

### Integration: ServiceNow — CandidateShortlist and PlacementSubmission Write

1. **Purpose:** Write shortlist results and submission records; update PlacementSubmission status for withdrawals; write MultiSubmissionRecord updates.
2. **System:** ServiceNow (same instance as D4a). Tables: `candidate_shortlists`, `placement_submissions`, `multi_submission_records` (all assumed names — see §14 A-2).
3. **Authentication:** Same OAuth 2.0 token as D4a integration.
4. **Endpoints:**
   ```
   POST /api/now/table/candidate_shortlists  — write new shortlist
   PATCH /api/now/table/candidate_shortlists/{id}  — update status (SELECTION_MADE, EXPIRED)

   POST /api/now/table/placement_submissions  — write new submission
   PATCH /api/now/table/placement_submissions/{id}  — update status (CONFIRMED, WITHDRAWN)

   POST /api/now/table/multi_submission_records  — create record for new nurse
   PATCH /api/now/table/multi_submission_records/{id}  — update open_submission_ids[], race flags

   Success: 201 (POST) / 200 (PATCH)
   Errors: same handling as D4a §9 (401 → refresh; 409 → idempotent skip; 500 → 3x retry)
   ```
5. **Error handling:** Same policy as D4a. For withdrawal failures specifically: see REQ-B-4 and escalation triggers §7.
6. **Rate limits:** Same assumptions as D4a (60 req/min conservative default [§14 A-2]).
7. **Data mapping:** All PlacementSubmission fields map 1:1 to ServiceNow table columns. `approved_by` is required before writing — validated in agent code.
8. **State sync:** Event-based confirmation detection: poll `placement_submissions` table every 15 seconds for status changes (webhook preferred but assumed unavailable [D4a §14 A-4]).
9. **Fallback:** Same as D4a — dead-letter log + coordinator alert on write failure.
10. **Logging:** Log per write: action, entity_id, status written, HTTP response, timestamp.

---

### Integration: DNR List Lookup

**[SCOPE-OUT]** — DNR list existence and API availability are not confirmed in the scenario or discovery session (see D0C assumption A9; §14 A-1 in this spec).

What is needed before build:
- Client to confirm whether facility DNR lists are maintained in ServiceNow (as a field on the facility record), in the nurse database (already modelled as `dnr_facility_ids[]` on NurseProfile), or in a separate system
- If `dnr_facility_ids[]` is already in the nurse database and populated correctly, no separate DNR API is needed — the query in §9 Integration 1 already retrieves it
- If DNR is in a separate system: provide API spec, auth method, and update cadence before build

Who provides it: MedFlex operations team / IT

Stub behaviour during development: hardcode `dnr_facility_ids = []` for all test nurses; log a warning that DNR check is stub-mode; flag in audit log per shortlist that DNR was not verified.

---

## §10. State Model

```
CandidateShortlist state machine (full lifecycle):

States: GENERATING, PRESENTED, SELECTION_MADE, NO_CANDIDATES, EXPIRED
Initial state: GENERATING
Terminal states: SELECTION_MADE, NO_CANDIDATES, EXPIRED

Transitions:
  GENERATING → PRESENTED: ≥ 1 candidate passes all gates; shortlist written to coordinator queue
  GENERATING → NO_CANDIDATES: 0 candidates pass all gates; HITLQueueItem written
  PRESENTED → SELECTION_MADE: coordinator selects candidate AND approves submission;
                               PlacementSubmission created with approved_by set
  PRESENTED → EXPIRED: current_time > expires_at AND status still = PRESENTED

Invalid transitions:
  NO_CANDIDATES → PRESENTED: FORBIDDEN — re-run matching with different criteria
  EXPIRED → SELECTION_MADE: FORBIDDEN — expired shortlist; create new CandidateShortlist
  SELECTION_MADE → PRESENTED: FORBIDDEN — selection is final; new shortlist cycle required
  PRESENTED → GENERATING: FORBIDDEN — shortlist cannot revert to in-progress

Guard conditions:
  Transition PRESENTED → SELECTION_MADE requires:
    selected_nurse_id is set AND references a nurse_id in candidates[]
    AND approved_by is a valid coordinator UUID
    AND WS2-T13 credential re-check has passed for selected_nurse_id

PlacementSubmission state machine:

States: OPEN, CONFIRMED, WITHDRAWN, EXPIRED_UNFILLED
Initial state: OPEN
Terminal states: CONFIRMED, WITHDRAWN, EXPIRED_UNFILLED

Transitions:
  OPEN → CONFIRMED: facility confirmation event received for this submission_id
  OPEN → WITHDRAWN: automated withdrawal (single confirmation path) OR coordinator-initiated
  OPEN → EXPIRED_UNFILLED: shift_datetime_start has passed, status still OPEN

Invalid transitions:
  CONFIRMED → WITHDRAWN: FORBIDDEN — out of agent scope; coordinator-only cancellation
  WITHDRAWN → any: FORBIDDEN — terminal; new submission required
  EXPIRED_UNFILLED → any: FORBIDDEN — terminal
```

---

## §11. Error Handling

| Failure | Detection method | Agent action | Human notification | Recovery path |
|---------|-----------------|--------------|-------------------|---------------|
| Nurse database unavailable (shortlist generation or re-check) | HTTP 500/503 or timeout after 3 retries | Block shortlist or submission; write HITLQueueItem | On-call coordinator (5-min SLA for re-check; 30-min for shortlist) | Auto-retry every 60s; resume when DB responds; re-run matching for shortlist; hold submission for re-check |
| LLM profile note classification fails (timeout or API error) | Exception or HTTP error on LLM call | Set note classification = RISK_SIGNAL (conservative default); add display_flag "Note classification unavailable" | Coordinator sees flag in shortlist | No recovery action — RISK_SIGNAL default is safe; LLM retry can be triggered on next shortlist generation |
| Candidate credential status changed between shortlist and re-check (WS2-T13 fails) | credential_status != ACTIVE at re-check time | Block submission; update CandidateShortlist; write HITLQueueItem | On-call coordinator (15-min SLA) | Coordinator selects alternative candidate from shortlist or re-runs matching |
| Governance hard stop: submission attempted without approved_by | approved_by field null or invalid UUID at write time | Block write; log governance_hard_stop_triggered = true in audit log | Supervisor immediately | Coordinator re-submits approval; agent re-executes write with valid approved_by |
| MultiSubmissionRecord update fails (open_submission_ids stale) | Withdrawal writes succeed but MultiSubmissionRecord PATCH fails | Log inconsistency; alert coordinator with nurse_id and affected submission IDs | On-call coordinator | Coordinator manually reconciles; agent re-attempts PATCH on next polling cycle |
| CandidateShortlist expires without coordinator action | Scheduled job checks expires_at vs. now() every 60 seconds | Set status = EXPIRED; write HITLQueueItem | On-call coordinator (30-min SLA) | Coordinator re-runs matching for the same MatchingBrief |

---

## §14. Spec Ambiguity Register

| Item | Type | Confidence | Description | Impact if unresolved | Resolution |
|------|------|------------|-------------|----------------------|------------|
| A-1 | Unknown | Low | DNR list system identity not confirmed — may be in nurse database (already in NurseProfile.dnr_facility_ids[]), ServiceNow, or a separate system | If separate system: builder writes wrong integration; DNR check fails silently if list is not queried | Client IT to confirm: where is the DNR list stored, and who maintains it? Is dnr_facility_ids[] already populated in the nurse database? |
| A-2 | Unknown | Low | Nurse database system identity, base URL, auth method, table/endpoint names, and rate limits not confirmed in scenario or discovery — all are assumptions derived from "it's a database" [DS-confirmed] | Builder cannot write integration contracts; all endpoint names and auth are placeholders | Client to provide: nurse database system name, API documentation, sandbox access, auth credentials type |
| A-3 | Design gap | Medium | HR-5 rest period minimum (8 hours) is not stated in the scenario — derived from FLSA and travel nursing domain knowledge | If MedFlex applies a different minimum (e.g., 10 or 12 hours per facility contract), the gate will either over-restrict or under-restrict | Ask Marcus/ops team: "Is there a minimum rest period between shifts that we enforce? Is it 8 hours or different per facility or state?" |
| A-4 | Spec ambiguity | Medium | Maximum shortlist size is set to 5 (assumption B7 — coordinator UX limit). Spec does not state how many candidates to present | If coordinator expects to see all qualifying candidates (e.g., 12), the 5-candidate cap hides options; if 5 is too many for the queue UI, the cap should be lower | Validate with coordinators: how many candidates do they typically review before selecting? What is the target coordinator review time per shortlist? |
| A-5 | Design gap | Low | CandidateShortlist validity window (60 minutes — assumption B4) is not in the scenario | If 60 minutes is too short (e.g., coordinator is in a call and cannot review in time), shortlists expire and must be regenerated — wasted DB queries and coordinator friction | Ask coordinators: "How quickly do you typically act on a matching result once it's in front of you? What is a reasonable expiry time?" |
| A-6 | Unknown | Medium | The `facility_placement_state` (used for HR-3) is not a field on the MatchingBrief entity in D4a — it must be derived from facility_id via a facility registry lookup. The lookup is not specified | Builder cannot implement HR-3 gate without this lookup; if it's assumed to be on the MatchingBrief already, field must be added to D4a §3 entity definition | Add `facility_state: string (ISO 3166-2 US state code)` to the MatchingBrief entity in D4a §3, populated from the facility registry at WS1 brief creation time |
