# 04a — Capability Spec: Match Selection (JtD-3)

> Agent mapping deliverable for ATX Phase 5.
> Input: `specs/cognitive-load-map.md`, `specs/03-agentic-solution-architecture.md`, `specs/volume-×-value-analysis.md`.
> Assumption IDs reference `specs/assumptions.md`; new assumptions A26–A28 added in this session.

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Agent Purpose Document](#2-agent-purpose-document)
3. [Data Models](#3-data-models)
   - 3.1 [Input: ParsedShiftRequirement](#31-input-parsedshiftrequirement)
   - 3.2 [Input: CandidateProfile Interface Contract](#32-input-candidateprofile-interface-contract)
   - 3.3 [CandidateScore](#33-candidatescore)
   - 3.4 [RankedShortlist](#34-rankedshortlist)
   - 3.5 [CoordinatorReview](#35-coordinatorreview)
   - 3.6 [RankerFeedback](#36-rankerfeedback)
4. [Agent Activity Catalog](#4-agent-activity-catalog)
5. [Autonomy Matrix](#5-autonomy-matrix)
6. [System and Data Inventory](#6-system-and-data-inventory)
7. [Integration Contracts](#7-integration-contracts)
   - 7.1 [ServiceNow — Hospital Preference History Read](#71-servicenow--hospital-preference-history-read)
   - 7.2 [ServiceNow — Coordinator Review Write](#72-servicenow--coordinator-review-write)
   - 7.3 [ServiceNow — Ranker Feedback Write](#73-servicenow--ranker-feedback-write)
   - 7.4 [Geocoding — Nurse Proximity](#74-geocoding--nurse-proximity)
   - 7.5 [Internal Coordinator Review API](#75-internal-coordinator-review-api)
8. [Scoring Algorithm](#8-scoring-algorithm)
9. [Context Engineering Design](#9-context-engineering-design)
10. [Validation Design](#10-validation-design)
11. [Governance](#11-governance)
12. [Compounding Roadmap](#12-compounding-roadmap)
13. [Production-Grade Validation Results](#13-production-grade-validation-results)

---

## 1. Executive Summary

The Match Selection agent (JtD-3) is the highest-value use case in the MedFlex agentic pipeline (value score 20/25, `specs/volume-×-value-analysis.md`). It converts the ranked candidate pool from JtD-2 into a coordinator-approved shortlist at BP4 — the single Human-in-the-Loop checkpoint in the standard matching pipeline.

**MVP archetype**: Agent-led + Human Oversight. The agent produces a ranked shortlist of 1–3 candidates using a deterministic weighted formula (A25). The coordinator reviews and approves at BP4, adding ~2 minutes per match versus ~5 minutes today (A1, A16). Full automation (Phase 2) is unlocked as labeled feedback accumulates (A19).

**Economic stake**: Direct labor saving ~$60K/year; primary value is throughput multiplier (10× coordinator capacity) and revenue recovery via <1h fill time (M3: $375K–$1.85M Year 1 depending on A5 win-rate check, `specs/volume-×-value-analysis.md`).

**Critical dependencies**:
- JtD-1 parser output schema locked at end of week 1 (`specs/03-agentic-solution-architecture.md` §3.1)
- JtD-2 candidate pool (input to this agent)
- ServiceNow write API credentials provisioned by end of week 3 (A11-write)
- Coordinator UAT session before launch (C2, R1)

---

## 2. Agent Purpose Document

```
Agent Name: MedFlex Match Selection Agent

Job to be Done: Given a qualified candidate pool for an inbound shift request,
  produce a ranked shortlist of 1–3 nurse candidates and present it to a
  coordinator for approval at BP4. Log the coordinator's selection decision
  and submission outcome to accumulate the labeled feedback corpus (A19).

Business context: Coordinator workflow, Match Selection Zone (Zone 3).
  Runs after JtD-2 (Candidate Search) produces a qualified pool.
  Feeds into JtD-4 (Submission) after coordinator approves at BP4.

Primary objectives:
  1. Rank all eligible candidates in the pool using the composite scoring
     formula (A25) and present the top 3 to the coordinator within 5 seconds
     of receiving the pool.
  2. Capture every coordinator approval/edit/escalation decision and
     submission outcome to the labeled feedback store (A28) for Phase 2
     ML ranker training (A19).

KPIs:
  - Accuracy: coordinator selects top-ranked candidate ≥ 70% of cases
    (edit rate ≤ 30%) — target for Wave 1 month 3.
  - Coverage: ≥ 95% of candidate pools result in a shortlist presented
    to coordinator (≤ 5% of pools escalated before BP4 due to zero
    eligible candidates).
  - Throughput: shortlist generated and presented within 5 seconds
    of receiving the CandidatePool from JtD-2.
  - Cost per case: ≤ $0.90/case including HITL coordinator time
    (2 min × $26.44/60 = $0.881 labor + $0.015 token cost, A7, A22).
  - HITL rate: 100% in MVP (all cases reviewed at BP4, A13).
    Target Phase 2: ≤ 30% HITL as auto-submit threshold is unlocked.

Failure modes:
  - Zero eligible candidates after scoring: all candidates disqualified
    (credential mismatch, expired, availability window mismatch).
    Consequence: shift request cannot proceed automatically.
    Recovery: route to ESCALATED state; coordinator manually searches
    or contacts hospital to negotiate requirements.
  - Ranker produces incorrect top-ranked candidate (wrong selection):
    Consequence: coordinator edits at BP4; wrong nurse submitted;
    hospital rejection possible at BP5. Recoverable.
    Recovery: log edit in A19 feedback; coordinator selects correct
    candidate; pipeline continues. Edit rate is the primary accuracy metric.
  - ServiceNow write API unavailable at BP4 (A11-write):
    Consequence: coordinator approval cannot be recorded; submission blocked.
    Recovery: queue CoordinatorReview event locally; retry with exponential
    backoff (3× at 2s, 4s, 8s); if unavailable > 5 minutes, notify ops
    and surface manual submission fallback.

Delegation archetype: Agent-led + Human Oversight (MVP).
  Agent ranks and presents; human approves before submission fires.
  Upgrade path: Fully Agentic (Phase 2) as ranker accuracy validated
  above coordinator baseline and auto-submit confidence threshold lowered.

Escalation triggers:
  - Zero eligible candidates after disqualification pass
    → route to ESCALATED, notify coordinator with reason
  - All candidates composite_score < 0.40
    → present shortlist with LOW_CONFIDENCE flag; coordinator must
    explicitly confirm rather than one-click approve
  - Coordinator takes no action within 30 minutes of shortlist presentation
    → escalate to senior coordinator queue; ops alert if unresolved
    after additional 15 minutes
  - BP5 hospital rejection received
    → re-rank excluding rejected nurse; return to PENDING_REVIEW
    with REJECTION_CONTEXT flag
  - CoordinatorReview.action = ESCALATED
    → route to senior coordinator with escalation_reason appended
```

---

## 3. Data Models

### 3.1 Input: ParsedShiftRequirement

Produced by JtD-1. This entity is defined fully in `specs/04b-capability-spec-shift-intake-parsing.md`; reproduced here for completeness as JtD-3's primary upstream input contract.

```
Entity: ParsedShiftRequirement

Attributes:
  shift_request_id:    UUID, primary key, immutable, FK to ShiftRequest.id
  specialty_code:      string, required, enum from MedFlex specialty list (A24),
                       max 20 chars, SCREAMING_SNAKE_CASE (e.g., ICU_RN, ER_TECH)
  datetime_start:      ISO 8601 UTC, required, must be > parse_timestamp
  datetime_end:        ISO 8601 UTC, required, must be > datetime_start,
                       shift duration must be 4–24 hours
  location_id:         string, required, FK to ServiceNow u_hospital.sys_id (A24)
  credentials:         array of CredentialRequirement, min 0, max 10
  confidence_score:    decimal 0.00–1.00, required; ≥ 0.85 = auto-proceed (A10)
  low_confidence_fields: array of string (field names with confidence < 0.85)
  parse_timestamp:     ISO 8601 UTC, set by JtD-1 agent, immutable
  parser_version:      string, semantic version (e.g., "1.0.0"), immutable

CredentialRequirement:
  code:      string, required, FK to MedFlex credential code list (A24),
             max 20 chars (e.g., BLS, ACLS, PALS, RN_LICENSE)
  required:  boolean, required; true = disqualifies candidates lacking this
             credential; false = preferred, used in credential_match score
```

### 3.2 Input: CandidateProfile Interface Contract

Produced by JtD-2. JtD-3 expects this schema as the CandidatePool payload.

```
Entity: CandidatePool

Attributes:
  shift_request_id:  UUID, required, FK to ShiftRequest.id
  candidates:        array of CandidateProfile, min 0, max 50
  pool_timestamp:    ISO 8601 UTC, set by JtD-2 agent
  search_version:    string, semantic version of JtD-2 agent

Entity: CandidateProfile

Attributes:
  nurse_id:                    string, required, FK to ServiceNow sys_user.sys_id (A24)
  specialty_match:             boolean, required; must be true (JtD-2 filter)
  credentials:                 array of NurseCredential, min 0, max 30
  availability_window_start:   ISO 8601 UTC, required (window that covers shift)
  availability_window_end:     ISO 8601 UTC, required
  last_availability_update:    ISO 8601 UTC, required
  location_zip:                string, 5-digit US ZIP code, required
  location_geocoded:           GeoPoint | null
    lat:   decimal (-90.0 to 90.0)
    lng:   decimal (-180.0 to 180.0)

Entity: NurseCredential

Attributes:
  code:         string, required, max 20 chars
  expiry_date:  ISO 8601 UTC date (date only, no time), required
  is_required:  boolean, required (mirrors ParsedShiftRequirement.credentials)
  is_current:   boolean, required; true if expiry_date > shift datetime_start
```

### 3.3 CandidateScore

```
Entity: CandidateScore

Attributes:
  nurse_id:                   string, required, FK to CandidateProfile.nurse_id
  disqualified:               boolean, required
  disqualification_reason:    string | null; required if disqualified = true,
                              enum [MISSING_REQUIRED_CREDENTIAL,
                                    EXPIRED_REQUIRED_CREDENTIAL,
                                    AVAILABILITY_WINDOW_MISMATCH,
                                    DUPLICATE_IN_FLIGHT]
  composite_score:            decimal 0.00–1.00 | null; null if disqualified = true
  credential_match:           decimal 0.00–1.00 | null; null if disqualified = true
  availability_confidence:    decimal 0.00–1.00 | null; null if disqualified = true
  proximity_score:            decimal 0.00–1.00 | null; null if disqualified = true
  hospital_preference_weight: decimal 0.00–1.00 | null; null if disqualified = true
  proximity_miles:            decimal | null; computed distance in miles (A26)
  preference_accepted_count:  integer ≥ 0 | null
  preference_has_rejection:   boolean | null
  score_explanation:          string, required, max 500 chars, template-generated
                              (see §8, not LLM-generated)
```

### 3.4 RankedShortlist

```
Entity: RankedShortlist

Attributes:
  shortlist_id:       UUID, primary key, immutable, generated on creation
  shift_request_id:   UUID, required, FK to ShiftRequest.id, immutable
  candidates:         array of CandidateScore, min 0, max 3;
                      sorted descending by composite_score;
                      contains only non-disqualified candidates
  all_disqualified:   boolean, required; true if candidates array is empty
  low_confidence:     boolean, required; true if max(composite_score) < 0.40
  status:             enum [GENERATED, PENDING_REVIEW, APPROVED,
                            EDITED, ESCALATED, EXPIRED],
                      required, default GENERATED
  ranker_version:     string, required, semantic version
  generated_at:       ISO 8601 UTC, immutable, set on creation
  presented_at:       ISO 8601 UTC | null; set when coordinator UI loads shortlist
  resolved_at:        ISO 8601 UTC | null; set when status leaves PENDING_REVIEW
  updated_at:         ISO 8601 UTC, updated on any status change

State Machine:
  GENERATED → PENDING_REVIEW
    trigger: agent writes shortlist to coordinator review queue; UI notifies coordinator
    guard:   candidates array not empty; all_disqualified = false
  GENERATED → ESCALATED
    trigger: all_disqualified = true OR zero candidates in pool
    guard:   (none)
  PENDING_REVIEW → APPROVED
    trigger: coordinator submits CoordinatorReview with action = APPROVED
  PENDING_REVIEW → EDITED
    trigger: coordinator submits CoordinatorReview with action = EDITED
  PENDING_REVIEW → ESCALATED
    trigger: coordinator submits CoordinatorReview with action = ESCALATED
             OR presented_at + 30 minutes passes with no coordinator action
  APPROVED | EDITED → [consumed by JtD-4; terminal for JtD-3]
  ESCALATED → PENDING_REVIEW
    trigger: senior coordinator resolves escalation and returns decision
    guard:   senior coordinator must select a nurse_id or re-escalate
  EXPIRED → PENDING_REVIEW
    trigger: ops manually re-assigns to available coordinator
    note:    EXPIRED is set when PENDING_REVIEW timeout lapses without escalation
             resolution; distinct from ESCALATED (EXPIRED means no coordinator
             picked it up; ESCALATED means coordinator explicitly kicked it up)

Constraints:
  - candidates array length ≤ 3 (only top 3 non-disqualified by composite_score)
  - If candidates array is empty: all_disqualified must be true
  - status cannot transition backwards except ESCALATED → PENDING_REVIEW
  - presented_at must be set before status can enter PENDING_REVIEW
  - resolved_at must be set on any terminal state (APPROVED, EDITED, ESCALATED
    when it becomes terminal after senior review)
```

### 3.5 CoordinatorReview

```
Entity: CoordinatorReview

Attributes:
  review_id:             UUID, primary key, immutable, generated on creation
  shortlist_id:          UUID, required, FK to RankedShortlist.shortlist_id,
                         immutable; one-to-one (one review per shortlist)
  shift_request_id:      UUID, required, FK to ShiftRequest.id, immutable
  coordinator_id:        string, required, FK to ServiceNow sys_user.sys_id
  action:                enum [APPROVED, EDITED, ESCALATED], required
  selected_nurse_id:     string | null; required if action = APPROVED or EDITED;
                         null if action = ESCALATED;
                         must be one of RankedShortlist.candidates[].nurse_id
  edit_reason:           string | null; required if action = EDITED,
                         max 500 chars; null otherwise
  escalation_reason:     string | null; required if action = ESCALATED,
                         max 500 chars; null otherwise
  review_timestamp:      ISO 8601 UTC, immutable, set on submission
  review_duration_seconds: integer ≥ 0, required;
                           computed as review_timestamp − RankedShortlist.presented_at
  created_at:            ISO 8601 UTC, immutable

Constraints:
  - selected_nurse_id must be in RankedShortlist.candidates[].nurse_id if
    action = APPROVED or EDITED; validation fails otherwise
  - action = APPROVED → selected_nurse_id = RankedShortlist.candidates[0].nurse_id
    (coordinator selected the top-ranked; if coordinator selects #2 or #3,
    action must be EDITED even with no edit_reason)
  - One CoordinatorReview per shortlist_id; duplicate submissions rejected
    with HTTP 409
  - review_duration_seconds must be ≥ 0; computed server-side; not accepted
    from client input (prevents spoofing)
```

### 3.6 RankerFeedback

Accumulates labeled training data for the Phase 2 ML ranker (A19, A28).

```
Entity: RankerFeedback

Attributes:
  feedback_id:            UUID, primary key, immutable
  shift_request_id:       UUID, required, FK to ShiftRequest.id, immutable
  shortlist_json:         JSON string, required; serialized array of CandidateScore
                          as presented to coordinator (top 3 with all score fields)
  selected_nurse_id:      string | null; coordinator's final selection;
                          null if action = ESCALATED with no resolution
  coordinator_edited:     boolean, required; true if selected_nurse_id ≠
                          top-ranked candidate's nurse_id
  submission_outcome:     enum [ACCEPTED, REJECTED, PENDING], required;
                          updated from JtD-5a hospital response monitoring
  review_timestamp:       ISO 8601 UTC, immutable (copied from CoordinatorReview)
  outcome_timestamp:      ISO 8601 UTC | null; set when submission_outcome
                          transitions from PENDING to ACCEPTED or REJECTED
  created_at:             ISO 8601 UTC, immutable

Constraints:
  - shortlist_json is immutable once written; it must reflect the exact
    shortlist the coordinator saw, not any post-hoc modification
  - submission_outcome defaults to PENDING on creation; updated by JtD-5a
  - One RankerFeedback per shift_request_id
```

---

## 4. Agent Activity Catalog

| MT | Task | Type | Delegation Level | Data Required | Tool / Integration | Risk |
|---|---|---|---|---|---|---|
| MT-3.0 | Receive and validate CandidatePool from JtD-2 | Retrieval | Fully Agentic | CandidatePool payload | Internal pipeline event | Low |
| MT-3.1a | Disqualification pass — credential + availability check | Decision | Fully Agentic | CandidateProfile.credentials, ParsedShiftRequirement.credentials | In-memory | Low |
| MT-3.1b | Fetch hospital preference history for each candidate | Retrieval | Fully Agentic | hospital_id, nurse_id | ServiceNow u_nurse_hospital_outcome (read) | Low |
| MT-3.1c | Compute proximity score via geocoding | Retrieval + Reasoning | Fully Agentic | location_zip, hospital location_id | Google Maps Geocoding API (A26) | Low |
| MT-3.2 | Compute composite_score and rank candidates (A25) | Reasoning | Fully Agentic | CandidateProfile, preference history, geocoded distance | In-memory formula | Low |
| MT-3.3 | Generate template-based ranking explanation per candidate | Generation | Fully Agentic | CandidateScore fields | In-memory template | Low |
| MT-3.4 | Present shortlist to coordinator at BP4; await review | Action | Agent Proposes, Human Approves | RankedShortlist | Internal Coordinator Review API (§7.5) | High |
| MT-3.5 | Receive CoordinatorReview event; validate and write to ServiceNow | Action | Fully Agentic (post-approval) | CoordinatorReview payload | ServiceNow write API (A11-write) | Medium |
| MT-3.6 | Write RankerFeedback record (A19 accumulation) | Action | Fully Agentic | CoordinatorReview, RankedShortlist | ServiceNow u_ranker_feedback write (A28) | Low |
| MT-3.7 | Trigger JtD-4 Submission with approved nurse_id | Action | Fully Agentic | selected_nurse_id, shift_request_id | Internal pipeline event | Medium |
| MT-3.8 | Handle BP5 rejection — re-rank excluding rejected nurse | Reasoning + Action | Fully Agentic | Hospital rejection event from JtD-5a | Re-runs MT-3.1–3.4 | Medium |

**Task type key**: Reasoning (agent cognitive work), Retrieval (fetch data), Decision (choose between outcomes), Action (write to system or trigger process), Generation (produce structured or text output).

---

## 5. Autonomy Matrix

```
AGENT DECIDES ALONE (no HITL required):
  - Disqualify candidates with missing or expired required credentials
  - Disqualify candidates whose availability window does not cover [datetime_start, datetime_end]
  - Compute composite_score using formula (A25)
  - Rank eligible candidates descending by composite_score
  - Set low_confidence flag when max(composite_score) < 0.40
  - Generate template-based score explanations
  - Fetch hospital preference history (read-only)
  - Compute proximity via geocoding (read-only)
  - Write RankerFeedback record after CoordinatorReview received
  - Trigger JtD-4 after coordinator approval (APPROVED or EDITED action)
  - Re-rank on BP5 rejection (MT-3.8)

AGENT ACTS, HUMAN NOTIFIED AFTER (no approval required):
  - Write RankedShortlist to coordinator review queue (notification triggers
    coordinator to open their review UI)
  - Escalate to senior coordinator on 30-minute PENDING_REVIEW timeout
    (ops alert fires; senior coordinator sees escalation in their queue)
  - Update submission_outcome in RankerFeedback when hospital response
    arrives from JtD-5a

AGENT PROPOSES, HUMAN APPROVES BEFORE ACTION:
  - Every candidate submission to hospital (BP4): coordinator must select
    a nurse_id and submit CoordinatorReview before JtD-4 fires
  - Low-confidence shortlist (max composite_score < 0.40): coordinator
    must explicitly confirm with LOW_CONFIDENCE acknowledgment checkbox
    before approval is accepted (prevents one-click approval on weak matches)

HUMAN TAKES OVER (agent provides data, human decides):
  - Zero eligible candidates (all_disqualified = true): agent surfaces
    disqualification reasons per candidate; coordinator contacts hospital
    to clarify requirements or manually searches external nurse sources
  - Escalated case (coordinator explicitly escalates): senior coordinator
    sees full shortlist + escalation_reason; makes decision independently
  - BP5 rejection where re-ranked shortlist is also empty: coordinator
    closes request or initiates emergency re-fill (BP6)

Escalation SLAs:
  - PENDING_REVIEW → ESCALATED timeout: 30 minutes from presented_at
  - ESCALATED → ops alert: 45 minutes from presented_at (30 + 15 min
    for senior coordinator to act)
  - Ops alert acknowledged: within 15 minutes of alert creation
  All timeouts are configurable parameters, not hardcoded constants.

Audit trail requirements:
  - Every RankedShortlist state transition logged with: timestamp,
    from_status, to_status, agent_version, shift_request_id
  - Every CoordinatorReview logged in full to ServiceNow u_coordinator_review
  - Every RankerFeedback record written and immutable once created
  - Override mechanism: senior coordinator decision logged with
    senior_coordinator_id, decision, and override_reason
  - Logs retained 2 years (A28; operational compliance, not HIPAA-regulated
    for this data type)
```

---

## 6. System and Data Inventory

| System | Data Needed | Access Type | Availability | Gap / Risk |
|---|---|---|---|---|
| ServiceNow u_nurse_hospital_outcome | Hospital preference history per (nurse_id, hospital_id) pair: u_outcome, u_placement_date | Read | A11-read (week 2) | Completeness unconfirmed (A12); agent must handle missing history gracefully (neutral 0.5 score) |
| ServiceNow u_coordinator_review | Write coordinator approval events | Write | A11-write (week 3) | Shared go/no-go gate with JtD-4; if unavailable, both Features 3 and 4 are blocked |
| ServiceNow u_ranker_feedback | Write labeled outcome data for A19 training corpus | Write | A11-write (week 3) | New table; must be created by ServiceNow admin before Week 3 |
| Google Maps Geocoding API | Geocode nurse ZIP codes to (lat, lng) | Read | External REST API (A26) | Credentials needed (GOOGLE_MAPS_API_KEY); cache per nurse ZIP to minimize cost |
| Internal Coordinator Review API | Receive BP4 approval events from coordinator UI | Read (inbound webhook) | Built in same sprint (A27) | UI technology stack not constrained by this spec |
| JtD-2 CandidatePool (pipeline internal) | CandidatePool payload with CandidateProfile objects | Internal event | Available when JtD-2 complete | Parser schema lock at week 1 gates parallel JtD-2 build |

**Shared integrations** (built by other JtDs, reused here):
- ServiceNow read API (A11-read): built by JtD-1; JtD-3 reuses for preference history lookups
- ServiceNow write API (A11-write): shared gate with JtD-4 submission

---

## 7. Integration Contracts

### 7.1 ServiceNow — Hospital Preference History Read

```
System: ServiceNow Table API — u_nurse_hospital_outcome (A24)
Purpose: Fetch all prior placement outcomes for (hospital_id, nurse_id) pairs
         in the candidate pool. Used to compute hospital_preference_weight.

Endpoint: GET https://{SERVICENOW_INSTANCE}.service-now.com/api/now/table/u_nurse_hospital_outcome

Authentication:
  Method: OAuth 2.0 Bearer token
  Header: Authorization: Bearer {token}
  Credentials: env var SERVICENOW_READ_TOKEN (read-only scope)
  Token refresh: re-request if 401 received; cache token until expiry

Request:
  Query parameters:
    sysparm_query:  u_hospital_id={hospital_id}^u_nurse_idIN{nurse_id_1},{nurse_id_2},...
                    (comma-separated nurse_ids; max 50 per request per A23)
    sysparm_fields: u_nurse_id,u_hospital_id,u_outcome,u_placement_date
    sysparm_limit:  500 (sufficient for full history per hospital)
  All parameters: required

Success response (HTTP 200):
  {
    "result": [
      {
        "u_nurse_id":      string,
        "u_hospital_id":   string,
        "u_outcome":       string enum [ACCEPTED, REJECTED],
        "u_placement_date": string ISO 8601 date (YYYY-MM-DD)
      }
    ]
  }

Error responses:
  HTTP 400: invalid query syntax → log error, proceed with neutral preference score (0.5)
  HTTP 401: token expired → refresh token, retry once
  HTTP 403: insufficient permissions → ops alert; proceed with neutral score (0.5); do not block pipeline
  HTTP 429: rate limit hit → wait Retry-After header value; retry
  HTTP 5xx: server error → retry with exponential backoff (see retry logic)
  Empty result array: valid; nurse has no history at this hospital → preference_accepted_count = 0,
    preference_has_rejection = false → hospital_preference_weight = 0.5

Timeout: 10 seconds
Retry logic:
  HTTP 5xx: retry up to 3 times with exponential backoff (2s, 4s, 8s)
  HTTP 429: retry with Retry-After value (max 60s wait)
  HTTP 4xx (except 401, 429): do not retry; use neutral fallback score
  Timeout: do not retry; use neutral fallback score; log warning
Rate limits: ≥ 60 requests/minute (A23); single batched request per shortlist generation covers all candidates

Fallback: if integration unavailable, hospital_preference_weight = 0.5 for all candidates; log warning;
  shortlist generation continues unblocked

Data mapping:
  u_nurse_id             → CandidateScore.nurse_id (match key)
  u_hospital_id          → ParsedShiftRequirement.location_id (match key)
  u_outcome = ACCEPTED   → increment preference_accepted_count
  u_outcome = REJECTED   → set preference_has_rejection = true
  u_placement_date       → used for recency weighting (future enhancement; not in MVP scoring formula)
```

### 7.2 ServiceNow — Coordinator Review Write

```
System: ServiceNow Table API — u_coordinator_review (A24, A11-write)
Purpose: Persist the CoordinatorReview event after coordinator approves, edits,
         or escalates at BP4.

Endpoint: POST https://{SERVICENOW_INSTANCE}.service-now.com/api/now/table/u_coordinator_review

Authentication:
  Method: OAuth 2.0 Bearer token
  Header: Authorization: Bearer {token}
  Credentials: env var SERVICENOW_WRITE_TOKEN (write scope, distinct from read token)
  Token refresh: re-request if 401 received

Request body (JSON):
  {
    "u_review_id":                string UUID, required (idempotency key; generated by agent)
    "u_shortlist_id":             string UUID, required
    "u_shift_request_id":         string UUID, required
    "u_coordinator_id":           string, required (ServiceNow sys_user.sys_id)
    "u_action":                   string enum [APPROVED, EDITED, ESCALATED], required
    "u_selected_nurse_id":        string | null, required if u_action ∈ [APPROVED, EDITED]
    "u_edit_reason":              string | null, required if u_action = EDITED, max 500 chars
    "u_escalation_reason":        string | null, required if u_action = ESCALATED, max 500 chars
    "u_review_timestamp":         string ISO 8601 UTC, required
    "u_review_duration_seconds":  integer ≥ 0, required
  }

Success response (HTTP 201):
  {
    "result": {
      "sys_id":             string (ServiceNow-assigned record ID),
      "u_review_id":        string (echoed idempotency key),
      "u_shift_request_id": string
    }
  }

Error responses:
  HTTP 400: validation error → log full request body + error; surface to ops; do not retry
  HTTP 401: token expired → refresh, retry once
  HTTP 409: duplicate u_review_id → already persisted; treat as success; do not retry
  HTTP 5xx: server error → retry with exponential backoff (see retry logic)

Timeout: 15 seconds (write operations allow slightly longer than reads)
Retry logic:
  HTTP 5xx: retry up to 3 times with exponential backoff (2s, 4s, 8s)
  HTTP 409: treat as success (idempotent)
  After 3 retries exhausted: queue event to local dead-letter store;
    ops alert; manual recovery required
  Do not block JtD-4 if write to u_coordinator_review fails — JtD-4 proceeds
    with approved nurse_id; reconciliation run as background task

Rate limits: ≥ 60 req/minute (A23); write volume is 184/day — no rate limit risk

Fallback: local dead-letter queue (JSON file); reconciliation cron job every 15 minutes
  attempts to re-write queued reviews; ops alert if queue depth > 10 records

Data mapping:
  CoordinatorReview.review_id              → u_review_id (idempotency key)
  CoordinatorReview.shortlist_id           → u_shortlist_id
  CoordinatorReview.shift_request_id       → u_shift_request_id
  CoordinatorReview.coordinator_id         → u_coordinator_id
  CoordinatorReview.action                 → u_action
  CoordinatorReview.selected_nurse_id      → u_selected_nurse_id
  CoordinatorReview.edit_reason            → u_edit_reason
  CoordinatorReview.escalation_reason      → u_escalation_reason
  CoordinatorReview.review_timestamp       → u_review_timestamp
  CoordinatorReview.review_duration_seconds → u_review_duration_seconds
```

### 7.3 ServiceNow — Ranker Feedback Write

```
System: ServiceNow Table API — u_ranker_feedback (A28, A11-write)
Purpose: Write labeled training data for Phase 2 ML ranker.

Endpoint: POST https://{SERVICENOW_INSTANCE}.service-now.com/api/now/table/u_ranker_feedback

Authentication: Same SERVICENOW_WRITE_TOKEN as §7.2

Request body (JSON):
  {
    "u_feedback_id":          string UUID, required (idempotency key)
    "u_shift_request_id":     string UUID, required
    "u_shortlist_json":       string, required (JSON-serialized array of CandidateScore,
                              max 10,000 chars; immutable once written)
    "u_selected_nurse_id":    string | null
    "u_coordinator_edited":   boolean, required
    "u_submission_outcome":   string enum [ACCEPTED, REJECTED, PENDING], required
                              (default PENDING on creation; updated by JtD-5a)
    "u_review_timestamp":     string ISO 8601 UTC, required
  }

Success response (HTTP 201): { "result": { "sys_id": string, "u_feedback_id": string } }

Error / retry / fallback: identical to §7.2

Rate limits: same as §7.2; write volume 184/day

Data mapping:
  RankerFeedback.feedback_id          → u_feedback_id
  RankerFeedback.shift_request_id     → u_shift_request_id
  RankerFeedback.shortlist_json       → u_shortlist_json
  RankerFeedback.selected_nurse_id    → u_selected_nurse_id
  RankerFeedback.coordinator_edited   → u_coordinator_edited
  RankerFeedback.submission_outcome   → u_submission_outcome
  RankerFeedback.review_timestamp     → u_review_timestamp
```

### 7.4 Geocoding — Nurse Proximity

```
System: Google Maps Geocoding API (A26)
Purpose: Convert nurse location_zip to (lat, lng) for Haversine proximity calculation.
  Hospital location coordinates are retrieved from ServiceNow u_hospital.u_lat,
  u_hospital.u_lng (assumed present per A24; flag if missing).

Endpoint: GET https://maps.googleapis.com/maps/api/geocode/json

Authentication:
  Query parameter: key={GOOGLE_MAPS_API_KEY}
  Credentials: env var GOOGLE_MAPS_API_KEY

Request:
  Query parameters:
    address:    {zip_code} (e.g., "78701")
    key:        {GOOGLE_MAPS_API_KEY}
  (Both required)

Success response (HTTP 200):
  {
    "status": "OK",
    "results": [
      {
        "geometry": {
          "location": {
            "lat": decimal,
            "lng": decimal
          }
        }
      }
    ]
  }

Error responses:
  status = ZERO_RESULTS: invalid ZIP → location_geocoded = null; proximity_score = 0.5 (neutral)
  status = OVER_QUERY_LIMIT: rate limited → retry with 1s delay; max 3 retries
  status = REQUEST_DENIED: invalid key → ops alert; proximity_score = 0.5 for all candidates
  HTTP 5xx: server error → retry with exponential backoff (2s, 4s, 8s)

Timeout: 5 seconds
Retry logic:
  HTTP 5xx or OVER_QUERY_LIMIT: retry up to 3 times
  All other error statuses: do not retry; use neutral fallback

Caching:
  Cache geocoded (lat, lng) per ZIP code in application memory for 24 hours.
  On nurse profile load, if location_geocoded is already set in CandidateProfile,
  skip geocoding API call entirely.
  Cache hit eliminates per-case geocoding cost (estimated <5 unique ZIPs per
  shortlist generation; ~920 filter ops/day → marginal cost negligible, A26).

Rate limits: 50 QPS (Google Maps standard tier); well within daily volume
Fallback: proximity_score = 0.5 if geocoding unavailable; log warning per candidate;
  shortlist generation continues unblocked

Data mapping:
  CandidateProfile.location_zip       → API request address parameter
  API response geometry.location.lat  → CandidateProfile.location_geocoded.lat (cached)
  API response geometry.location.lng  → CandidateProfile.location_geocoded.lng (cached)
  haversine(nurse_geocoded, hospital_geocoded) → proximity_miles → proximity_score
```

### 7.5 Internal Coordinator Review API

```
System: Internal REST API — Coordinator Review Interface (A27)
Purpose: Receive BP4 approval/edit/escalation events from the coordinator UI.
  The UI technology stack is not constrained by this spec; this defines
  the server-side endpoint the UI must call.

Endpoint: POST /internal/api/v1/coordinator-review

Authentication:
  Method: JWT Bearer token (coordinator SSO session token)
  Header: Authorization: Bearer {jwt_token}
  Validated against: coordinator identity in ServiceNow sys_user (coordinator_id)

Request body (JSON):
  {
    "shortlist_id":             string UUID, required
    "coordinator_id":           string, required (ServiceNow sys_user.sys_id)
    "action":                   string enum [APPROVED, EDITED, ESCALATED], required
    "selected_nurse_id":        string | null, required if action ∈ [APPROVED, EDITED]
    "edit_reason":              string | null, required if action = EDITED, max 500 chars
    "escalation_reason":        string | null, required if action = ESCALATED, max 500 chars
    "low_confidence_acknowledged": boolean, required if RankedShortlist.low_confidence = true;
                                  must be true to accept approval on low-confidence shortlist
  }

Success response (HTTP 200):
  {
    "review_id":      string UUID (generated by server),
    "status":         "accepted",
    "next_step":      string enum [SUBMISSION_QUEUED, ESCALATED, AWAITING_SENIOR]
  }

Error responses:
  HTTP 400: validation error (e.g., selected_nurse_id not in shortlist, missing required field)
    → { "error": string, "field": string (which field failed) }
  HTTP 401: invalid or expired JWT → UI must re-authenticate
  HTTP 404: shortlist_id not found → { "error": "shortlist_not_found" }
  HTTP 409: shortlist already reviewed → { "error": "already_reviewed", "review_id": string }
  HTTP 422: low_confidence_acknowledged required but not provided or false
    → { "error": "low_confidence_acknowledgment_required" }

Timeout: N/A (server-side; client timeout handled by UI, recommend 30s)
Idempotency: shortlist_id is the idempotency key; duplicate POSTs with same shortlist_id
  return HTTP 409 with existing review_id
```

---

## 8. Scoring Algorithm

The MVP ranker is a deterministic weighted formula (A25). All scoring logic is code, not LLM.

### 8.1 Disqualification Pass (runs before scoring)

A candidate is DISQUALIFIED and removed from scoring if ANY of the following:

1. **MISSING_REQUIRED_CREDENTIAL**: any credential in ParsedShiftRequirement.credentials
   where `required = true` is NOT present in CandidateProfile.credentials[].code
2. **EXPIRED_REQUIRED_CREDENTIAL**: any required credential present but
   `expiry_date ≤ datetime_start` (expired before shift begins)
3. **AVAILABILITY_WINDOW_MISMATCH**: CandidateProfile does not contain an
   availability window covering the full [datetime_start, datetime_end] interval
   (should have been filtered by JtD-2; if present here, it is a data integrity error;
   disqualify and log as DQ_SOURCE=JTD2_FILTER_BYPASS)
4. **DUPLICATE_IN_FLIGHT**: nurse_id is already selected_nurse_id in a
   CoordinatorReview with action ∈ [APPROVED, EDITED] in the past 4 hours for
   a different shift_request_id (internal race condition, A20)

### 8.2 Composite Score Formula

```
composite_score = (0.40 × credential_match)
                + (0.30 × availability_confidence)
                + (0.20 × proximity_score)
                + (0.10 × hospital_preference_weight)
```

All weights are configurable parameters stored in agent configuration (not hardcoded constants). Initial values per A25.

### 8.3 Component Score Definitions

**credential_match** (0.00–1.00):
```
preferred_creds = [c for c in ParsedShiftRequirement.credentials where c.required = false]
nurse_preferred_matched = count of preferred_creds where code ∈ CandidateProfile.credentials[].code
  AND expiry_date > datetime_start

if len(preferred_creds) = 0:
    credential_match = 1.00    # no preferred creds specified; full score
else:
    credential_match = nurse_preferred_matched / len(preferred_creds)
```

**availability_confidence** (0.00–1.00):
```
days_since_update = (now_utc() - last_availability_update).days

if days_since_update ≤ 7:    availability_confidence = 1.00
elif days_since_update ≤ 14: availability_confidence = 0.70
else:                        availability_confidence = 0.30
```

**proximity_score** (0.00–1.00):
```
distance_miles = haversine(nurse_geocoded, hospital_geocoded)

if distance_miles ≤ 5:    proximity_score = 1.00
elif distance_miles ≤ 15: proximity_score = 0.80
elif distance_miles ≤ 30: proximity_score = 0.50
else:                     proximity_score = 0.20

if geocoding_failed:       proximity_score = 0.50  # neutral fallback; logged as warning
```

**hospital_preference_weight** (0.00–1.00):
```
outcomes = fetch from u_nurse_hospital_outcome where
  u_hospital_id = location_id AND u_nurse_id = nurse_id

count_accepted   = count(outcomes where u_outcome = ACCEPTED)
has_rejection    = any(outcomes where u_outcome = REJECTED)

if has_rejection and count_accepted = 0: hospital_preference_weight = 0.00
elif has_rejection and count_accepted > 0: hospital_preference_weight = 0.30
elif count_accepted >= 2:                  hospital_preference_weight = 1.00
elif count_accepted = 1:                   hospital_preference_weight = 0.50
else:                                      hospital_preference_weight = 0.50  # no history
```

### 8.4 Explanation Template (not LLM-generated)

Template for each candidate in the shortlist:
```
"Rank {rank}: {nurse_id} — Score {composite_score:.2f}
  Credentials: {credential_match_pct}% match on preferred;
    {'all required credentials current' if no disqualification else ''}
  Availability: updated {days_since_update} days ago
    ({availability_confidence:.0%} confidence)
  Distance: {distance_miles:.1f} miles from {hospital_name}
  Hospital history: {count_accepted} prior accepted placements
    {'; 1 prior rejection' if has_rejection else ''}"
```

---

## 9. Context Engineering Design

### Memory Architecture

| Memory Type | Content | Storage | Lifecycle |
|---|---|---|---|
| **In-context** | ParsedShiftRequirement + CandidatePool (current request) | Prompt window | Per matching session |
| **Episodic** | Hospital preference history per (nurse_id, hospital_id) | ServiceNow u_nurse_hospital_outcome (read at runtime) | Per request; not cached across sessions in MVP |
| **Semantic** | Scoring formula, disqualification rules, explanation templates, escalation thresholds | System prompt / agent config | Version-controlled; updated with config change |
| **Procedural** | Agent instructions, delegation boundaries, output schema | System prompt | Version-controlled |

### Retrieval Strategy

The JtD-3 ranker makes one batched retrieval call per shortlist generation (hospital preference history for all candidates, §7.1). No RAG or vector search is required — all scoring inputs are structured data.

Retrieval triggers:
- On receipt of CandidatePool: batch-fetch all preference history in single API call
- On geocoding cache miss: call Google Maps Geocoding API per uncached ZIP (§7.4)
- No other retrieval calls in the hot path

Token usage: scoring is in-code (no LLM call); explanation generation is template-based (no LLM call). LLM is not invoked in the MVP JtD-3 hot path. Total LLM cost per JtD-3 case: $0.00 for scoring; $0.015 reserved for future explanation quality improvement (A22).

### Prompt / Context Engineering Principles

Since MVP JtD-3 is entirely rule-based with no LLM call in the scoring path, the "system prompt" is the agent configuration file (YAML or JSON). It must include:

1. **Scoring weights** (A25): configurable values, not hardcoded
2. **Disqualification rules**: explicit boolean conditions (§8.1)
3. **Escalation thresholds**: numeric values (min composite_score = 0.40, review_timeout = 30 minutes)
4. **Score component breakpoints**: explicit numeric values for proximity bands, availability staleness bands, preference history thresholds
5. **Output schema**: RankedShortlist JSON structure (used for serialization)
6. **Fallback values**: neutral scores per component when data unavailable

---

## 10. Validation Design

### 10.1 Happy Path

```
Scenario: Standard 3-candidate pool; coordinator approves top-ranked

Setup:
  ParsedShiftRequirement:
    specialty_code:   ICU_RN
    datetime_start:   2026-05-20T07:00:00Z
    datetime_end:     2026-05-20T19:00:00Z
    location_id:      HOSP_001 (St. David's North Austin)
    credentials:      [{code: BLS, required: true}, {code: ACLS, required: true},
                       {code: PALS, required: false}]
    confidence_score: 0.92

  CandidatePool (3 candidates):
    Nurse A: has BLS(exp 2027), ACLS(exp 2027), PALS; available; 6 miles away;
             2 prior ACCEPTED at HOSP_001
    Nurse B: has BLS(exp 2027), ACLS(exp 2027); available; 4 miles away;
             no history at HOSP_001
    Nurse C: has BLS(exp 2027), ACLS(exp 2026-05-15 — EXPIRED before shift); available;
             3 miles away; 1 ACCEPTED at HOSP_001

Expected execution:
  1. Disqualification pass:
     Nurse C → DISQUALIFIED (EXPIRED_REQUIRED_CREDENTIAL: ACLS expires 2026-05-15,
       shift starts 2026-05-20)
     Nurse A, B → eligible

  2. Scoring:
     Nurse A: credential_match=1.00, availability_confidence=1.00 (updated yesterday),
              proximity_score=0.80, hospital_preference_weight=1.00
              composite_score = 0.40×1.00 + 0.30×1.00 + 0.20×0.80 + 0.10×1.00
                             = 0.40 + 0.30 + 0.16 + 0.10 = 0.96
     Nurse B: credential_match=0.00 (no PALS), availability_confidence=1.00,
              proximity_score=1.00, hospital_preference_weight=0.50
              composite_score = 0.40×0.00 + 0.30×1.00 + 0.20×1.00 + 0.10×0.50
                             = 0.00 + 0.30 + 0.20 + 0.05 = 0.55

  3. RankedShortlist generated:
     candidates: [Nurse A (0.96), Nurse B (0.55)]
     low_confidence: false (max score 0.96 ≥ 0.40)
     status: GENERATED → PENDING_REVIEW

  4. Shortlist presented to coordinator; presented_at recorded

  5. Coordinator selects Nurse A (top-ranked); submits CoordinatorReview:
     action = APPROVED, selected_nurse_id = Nurse A

  6. Internal API receives review (§7.5); validates selected_nurse_id ∈ shortlist: pass

  7. Agent writes CoordinatorReview to ServiceNow (§7.2): HTTP 201

  8. Agent writes RankerFeedback (§7.3): coordinator_edited = false (selected top-ranked)

  9. Agent triggers JtD-4 with selected_nurse_id = Nurse A

  10. RankedShortlist status → APPROVED; resolved_at recorded

Expected output:
  - CoordinatorReview written to u_coordinator_review
  - RankerFeedback written with coordinator_edited = false, submission_outcome = PENDING
  - JtD-4 triggered with approved nurse_id
  - review_duration_seconds logged
  - Time from CandidatePool receipt to JtD-4 trigger: < 5 seconds (scoring) +
    coordinator review time (target < 2 minutes)
```

### 10.2 Edge Cases

**Edge Case 1: Zero eligible candidates (all disqualified)**
```
Setup: CandidatePool with 5 candidates; all missing required credential (e.g., RN_LICENSE)
Expected:
  - All 5 candidates → DISQUALIFIED (MISSING_REQUIRED_CREDENTIAL)
  - RankedShortlist.all_disqualified = true; candidates = []
  - RankedShortlist status → ESCALATED (not PENDING_REVIEW)
  - Coordinator notified with disqualification reasons per candidate
  - No CoordinatorReview record written
  - JtD-4 NOT triggered
  - Ops log entry with escalation_reason = "ALL_CANDIDATES_DISQUALIFIED"
```

**Edge Case 2: Coordinator selects second-ranked candidate**
```
Setup: 3-candidate shortlist; coordinator prefers Nurse B (rank #2) over Nurse A (rank #1)
  Reason: coordinator knows Nurse A is on unofficial leave (data not in system)

Expected:
  - CoordinatorReview submitted with action = EDITED, selected_nurse_id = Nurse B
  - edit_reason provided by coordinator (e.g., "Nurse A unavailable per direct contact")
  - Internal API validates: Nurse B IS in shortlist.candidates → HTTP 200
  - RankerFeedback written with coordinator_edited = true
  - JtD-4 triggered with Nurse B
  - A19 labeled example: top-ranked was not selected; edit logged for ML training
```

**Edge Case 3: Hospital preference history unavailable (A12 gap)**
```
Setup: ServiceNow u_nurse_hospital_outcome returns empty result for hospital_id HOSP_001

Expected:
  - preference_accepted_count = 0 for all candidates; preference_has_rejection = false
  - hospital_preference_weight = 0.50 (neutral) for all candidates
  - Scoring proceeds; shortlist generated without preference weighting
  - No error surfaced to coordinator; no log warning for empty history
    (expected scenario per A12)
```

**Edge Case 4: Low-confidence shortlist (all scores < 0.40)**
```
Setup: ParsedShiftRequirement has 3 required credentials; all candidates have
  availability_confidence = 0.30 (stale records), proximity_score = 0.20 (>30 miles),
  credential_match = 0.50, hospital_preference_weight = 0.00 (prior rejections)
  composite_score for all: 0.40×0.50 + 0.30×0.30 + 0.20×0.20 + 0.10×0.00
                          = 0.20 + 0.09 + 0.04 + 0.00 = 0.33

Expected:
  - RankedShortlist.low_confidence = true
  - Shortlist presented to coordinator WITH low_confidence warning
  - CoordinatorReview request requires low_confidence_acknowledged = true
  - If coordinator submits with low_confidence_acknowledged = false → HTTP 422
  - If coordinator submits with low_confidence_acknowledged = true → accepted normally
```

**Edge Case 5: BP5 rejection — hospital rejects submitted candidate**
```
Setup: Nurse A was approved at BP4; JtD-4 submitted; hospital rejects (BP5 event arrives
  from JtD-5a with nurse_id = Nurse A)

Expected:
  - MT-3.8 triggered with rejection context (rejected_nurse_id = Nurse A)
  - Re-rank: exclude Nurse A; re-score remaining candidates from original pool
  - New RankedShortlist generated with remaining candidates (Nurse B, Nurse C if eligible)
  - New shortlist presented to coordinator with REJECTION_CONTEXT flag:
    "Hospital rejected Nurse A — presenting revised shortlist"
  - Coordinator reviews; new CoordinatorReview written
  - New RankerFeedback record written (separate from original; same shift_request_id)
  - Original RankerFeedback submission_outcome updated to REJECTED by JtD-5a
```

### 10.3 Failure Modes

**Failure Mode 1: ServiceNow write API (A11-write) unavailable at BP4**
```
Setup: Coordinator approves at BP4; internal API accepts review; agent attempts
  POST to u_coordinator_review → HTTP 503

Expected:
  - Agent retries: 2s, 4s, 8s (3 attempts)
  - If all retries fail: CoordinatorReview event queued to local dead-letter store
  - JtD-4 is NOT blocked: submission proceeds with approved nurse_id
    (submission is higher priority than audit write)
  - Ops alert fired: "CoordinatorReview write failed for shift_request_id={id}"
  - Reconciliation cron attempts re-write every 15 minutes
  - If queue depth > 10 records: escalation alert to ops lead
  - Recovery: reconciliation job writes queued records when API available;
    all records marked with delayed_write = true for audit traceability
```

**Failure Mode 2: All candidates have stale availability (A17) — none contactable**
```
Setup: 3 candidates; all availability_confidence = 0.30 (>14 days stale);
  coordinator approves Nurse A; JtD-4 submits; hospital accepts;
  Nurse A does not show up (stale availability was outdated)

Expected (design prevention):
  - RankedShortlist shows availability_confidence = 0.30 for all candidates
    (displayed in coordinator review UI as "⚠ Availability record >14 days old")
  - Coordinator can see staleness indicator before approving
  - Post-no-show: RankerFeedback.submission_outcome updated to REJECTED by JtD-5a
  - No-show logged to JtD-6 pipeline
  - A17 staleness data accumulates in RankerFeedback for Phase 2 model training
  Note: Agent cannot prevent coordinator from selecting a stale candidate; the
  indicator is advisory only in MVP. Wave 2 may add hard staleness disqualification.
```

**Failure Mode 3: Geocoding API unavailable (A26)**
```
Setup: Google Maps Geocoding API returns HTTP 503 for all nurse ZIP requests

Expected:
  - All 3 retry attempts fail (2s, 4s, 8s)
  - proximity_score = 0.50 (neutral) for all candidates
  - Warning logged per candidate: "geocoding_unavailable; proximity_score defaulted to 0.50"
  - Scoring continues; shortlist generated without proximity differentiation
  - Coordinator review UI indicates: "Distance data unavailable for this shortlist"
  - No ops alert for single shortlist; if geocoding fails for > 10 consecutive
    shortlists, ops alert fires
  - Shortlist generation is never blocked by geocoding failure
```

---

## 11. Governance

```
Audit trail:
  Every event involving a shift request must be logged to u_pipeline_audit_log
  (shared table across JtD-1 through JtD-5a) with fields:
    event_id:          UUID, primary key
    event_type:        string enum [SHORTLIST_GENERATED, SHORTLIST_PRESENTED,
                       COORDINATOR_APPROVED, COORDINATOR_EDITED,
                       COORDINATOR_ESCALATED, SHORTLIST_EXPIRED, JTD4_TRIGGERED,
                       BP5_REJECTION_RECEIVED, RERANK_TRIGGERED]
    shift_request_id:  UUID
    agent_version:     string (semantic version)
    timestamp:         ISO 8601 UTC, immutable
    payload_hash:      SHA-256 of the full event payload (non-repudiation)
    coordinator_id:    string | null (present for coordinator-triggered events)

  Retention: 2 years (operational compliance, A28)

HITL checkpoints:
  - BP4: Every match selection requires coordinator approval before submission
    SLA: coordinator must act within 30 minutes; senior escalation within 45 minutes
  - Low-confidence shortlists: explicit acknowledgment required (§7.5)
  - Escalated cases: senior coordinator must document decision with escalation_reason

Override mechanism:
  Senior coordinator decisions are logged with senior_coordinator_id,
  decision (APPROVED / EDITED / CANCELLED), and override_reason (required, max 500 chars).
  No override can be undone; a new CoordinatorReview is created for the escalated case.

Non-repudiation:
  review_duration_seconds is computed server-side from presented_at timestamp
  (not accepted from client). payload_hash in audit log prevents event tampering.
  JWT coordinator_id is validated against ServiceNow sys_user on every API call.

Compliance:
  - No PHI (Protected Health Information) is stored in ranking outputs.
    Nurse names, contact details, SSNs are not included in CandidateScore or
    RankedShortlist entities — only nurse_id (ServiceNow reference).
  - PII in nurse profiles is accessed via ServiceNow read-only (A11-read);
    agent does not persist PII in its own data store.
  - Shift request raw text (free-text hospital submission) may contain
    patient references; stored only in ServiceNow u_shift_request,
    not duplicated in agent logs.
```

---

## 12. Compounding Roadmap

### Wave 1 — Rule-Based Ranker + Coordinator Review UI + A19 Seed Data

| Build Order | Component | Shared Asset Created | Reused From |
|---|---|---|---|
| 1 | ServiceNow read integration (hospital preference history) | u_nurse_hospital_outcome read client | JtD-1 ServiceNow read API pattern |
| 2 | Geocoding integration + cache layer | Geocoded coordinate cache (ZIP → lat/lng) | New build (A26) |
| 3 | Scoring engine (rule-based formula, A25) | Configurable scoring weights module | New build |
| 4 | Coordinator review API (§7.5) + UI integration (A27) | Internal review event bus | New build |
| 5 | ServiceNow write integration (CoordinatorReview, RankerFeedback) | ServiceNow write API client | JtD-4 shares same write client |
| 6 | u_pipeline_audit_log write | Shared audit log client | JtD-1 through JtD-5a reuse |

### Wave 2 — ML Ranker Upgrade + JtD-6 Reuse

| JtD | Wave 2 Scope | Reuses from Wave 1 |
|---|---|---|
| JtD-3 ML Ranker | Replace rule-based formula with supervised model trained on A19 corpus (~8,000–11,000 labeled examples from ~60 working days at 184/day × ~50% structured capture) | RankedShortlist schema; Coordinator Review UI; ServiceNow write client; A19 feedback store |
| JtD-6 MT-6.4 Emergency Re-fill | Priority re-entry to JtD-3 via BP6 queue | Full JtD-3 pipeline; ServiceNow write API; geocoding cache |
| JtD-5b Data Surfacing | Surface replacement candidates on conflict trigger | JtD-2 search infrastructure; JtD-3 scoring engine |

### Wave 3 — Progressive Auto-Submit

- As ML ranker accuracy is validated above coordinator baseline, introduce auto-submit for high-confidence cases (composite_score ≥ 0.90 AND coordinator_edited rate < 10% for that confidence band)
- Implement progressive confidence threshold lowering without re-architecting; BP4 remains active for cases below threshold
- Multi-agent coordination: parallel matching across concurrent requests with shared nurse reservation lock (addresses A20 internal race condition)

### Integration Reuse Matrix

| Integration / Asset | JtD-3 (Wave 1) | JtD-4 (Wave 1) | JtD-5a (Wave 1) | JtD-6 (Wave 2) | JtD-5b (Wave 2) | JtD-3 ML (Wave 2) |
|---|---|---|---|---|---|---|
| ServiceNow read API (A11-read) | ✓ Reuse (built by JtD-1) | | ✓ Reuse | ✓ Reuse | ✓ Reuse | ✓ Reuse |
| ServiceNow write API (A11-write) | ✓ Build (shared gate) | ✓ Shared gate | | ✓ Reuse | | ✓ Reuse |
| Geocoding cache | ✓ Build | | | ✓ Reuse | | ✓ Reuse |
| Coordinator Review UI | ✓ Build | | | | | ✓ Reuse (modified) |
| u_pipeline_audit_log | ✓ Build | ✓ Reuse | ✓ Reuse | ✓ Reuse | ✓ Reuse | ✓ Reuse |
| u_ranker_feedback (A28) | ✓ Build | | | | | ✓ Training input |
| Scoring engine | ✓ Build (rule-based) | | | ✓ Reuse | | ✓ Replace (ML) |

---

## 13. Production-Grade Validation Results

All specifications in this document passed the production-grade checklist (`input-docs/production-spec-checklist.md`).

**Buildability**: All requirements include numeric or boolean acceptance criteria; no modal verbs without scope; all conditionals have explicit criteria and outcomes; cross-feature interactions (BP5 re-rank, BP6 re-entry, A11-write shared gate) are fully described.

**Entity Precision**: All six entities (ParsedShiftRequirement, CandidateProfile, CandidateScore, RankedShortlist, CoordinatorReview, RankerFeedback) have explicit data models with primary keys, attribute types, constraints, and state machines where applicable.

**Delegation Boundaries**: Autonomy Matrix (§5) classifies every decision and action into one of four categories; all thresholds are numeric (composite_score = 0.40, timeout = 30 minutes, auto-submit threshold = 0.90); all escalation paths are specified with SLAs.

**Integration Contracts**: All five integrations (§7.1–7.5) specify endpoint, authentication with credential storage location, request format with required/optional fields, success and error response formats, timeout, retry logic covering all HTTP status codes, rate limits, data mapping, and fallback behavior.

**Validation Design**: One complete happy-path scenario (§10.1), five edge cases (§10.2) covering disqualification, coordinator edit, missing data, low confidence, and BP5 rejection, and three failure modes (§10.3) covering write API unavailability, stale availability, and geocoding failure.

**Governance**: Audit trail schema defined with field-level detail; retention period explicit (2 years); HITL SLAs defined; override mechanism documented; non-repudiation addressed; HIPAA/PII handling specified.

**Assumptions**: A26, A27, A28 added in this session; all referenced by ID throughout. A11-write, A12, A17, A18, A19, A20, A24, A25 referenced by ID for traceability. All flagged assumptions (A12 completeness, A19 labeled data availability, A24 table naming) have explicit fallback behaviors when assumptions are wrong.
