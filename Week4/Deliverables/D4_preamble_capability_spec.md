# D4 — Preamble: Shared Foundation for WS1 and WS2 Capability Specifications

*This preamble is written once and covers both agents. Per-agent specifications (D4a: WS1 Module, D4b: WS2 Module) reference this document by section — they do not redefine content established here.*

*Sources: `Deliverables/D3_solution_architecture.md`, `Deliverables/D4a_capability_spec_WS1_lean.md`, `Deliverables/D4b_capability_spec_WS2_lean.md`, `Scenario/scenario.md`.*

---

## Preamble §1: Agent Selection

### Agents specified

**Agent 1 — Intake & Matching Agent: WS1 Module** (`D4a_capability_spec_WS1_lean.md`)
- JtDs covered: WS1-JtD-1 (message classification), WS1-JtD-2 (parameter extraction), WS1-JtD-4 (urgency classification), WS2-JtD-1 (completeness gate)
- D3 archetype: Human-led + Agent Support (WS1-JtD-1, WS1-JtD-2); Agent-led + Human Oversight (WS1-JtD-4, WS2-JtD-1)
- D3 selection rationale: WS1 is the required intake feeder for WS2 — without a validated structured MatchingBrief, the WS2 matching agent cannot function. ADR-3 (D3 §5) sequences WS1 deployment before full WS2 rollout; WS1-lite (Week 6 pilot schema) is the earliest intake layer. Even at D2B score 1/7, WS1-JtD-2 is the minimum required capability — no rule-based alternative exists for unstructured free-text intake [DS-confirmed].

**Agent 2 — Intake & Matching Agent: WS2 Module** (`D4b_capability_spec_WS2_lean.md`)
- JtDs covered: WS2-JtD-2 (candidate pool identification), WS2-JtD-5 (submission + multi-submission state), WS2-JtD-6 (withdrawal execution); WS3-JtD-1 (credential re-check, embedded tool call); WS4-JtD-4 (parallel replacement query on no-show trigger)
- D3 archetype: Fully Agentic for WS2-JtD-2 and WS3-JtD-1; Agent-led + Human Oversight for WS2-JtD-5 and WS2-JtD-6
- D3 selection rationale: WS2-JtD-2 has the highest D2C AV Score in the engagement (20) and is the primary business-case driver — reducing the 4.2-hour time-to-fill to ≤60 minutes. D3 autonomy matrix scores it 5/7 on all three enabling dimensions (Input Structure H, Decision Determinism H, Tool Coverage H). It is the core agentic target in D3 §0 executive summary.

### Architecture note

Both agents are implemented as modules of a single Intake & Matching Agent context (ADR-2, D3 §5) — the WS1→WS2 handoff uses a stable MatchingBrief schema as the interface contract, not a separate inter-agent message-passing boundary. The distinction between WS1 module and WS2 module in these specs reflects sequential functional stages within one agent invocation, not two independently deployed agents.

### Explicitly deferred

| JtD | Why deferred |
|-----|-------------|
| WS1-JtD-3: Credential requirement ambiguity resolution | Human Only — D2B 0/7; no structured facility preference profiles [D0C: U-3]; any delegation replicates the recommendation engine failure [A13]. D3 §6 names the future delegation path: once facility profiles are built. |
| WS2-JtD-3: Optimal candidate selection | Human Only — D2B 0/7; selection among qualified candidates requires facility heuristics that live in coordinator memory, not any structured system [DS-confirmed]; blocked on Tool Coverage L. D3 ADR-1 documents the revisit condition. |
| WS2-JtD-4: Exception / no-candidate resolution | Human Only — D2B 0/7; Decision Determinism L; expanded search vs. waiver request vs. unfillable flag has no governing rule; submitting below-threshold without human authorisation is a compliance event. |
| WS4-JtD-1, WS4-JtD-2: Confirmation & acknowledgement monitoring | Rule-based automation (RPA) — D2B 7/7 and 4/7; no LLM reasoning required; fully deterministic, templated, event-triggered; delivered as a separate RPA workstream per D3 §3. |
| WS4-JtD-3: Nurse withdrawal/renegotiation | Human Only — D2B 0/7; Input Structure L (inbound phone call); relationship management decision with no structured supporting data [A2A5, A2A6]. |

---

## Preamble §2: Shared Entity Definitions

The following entities are used by both the WS1 and WS2 modules. They are defined once here. Both per-agent specifications reference these definitions — they do not redefine them.

### Entity: MatchingBrief

```
Entity: MatchingBrief

Purpose: The WS1→WS2 interface contract. Created by WS1 from an inbound shift request;
consumed and acted upon by WS2. The stable schema is the architectural decoupling
mechanism per ADR-2 (D3 §5): WS2 is always built to consume this schema regardless
of whether WS1-lite, Wave 1 WS1, or Wave 2 WS1 produced it.

Attributes:
- id: UUID, primary key, immutable, generated on creation
- source_message_id: string, max 128 chars, required, immutable
  — ServiceNow record sys_id of the inbound message that produced this brief
- facility_id: UUID, required, foreign key to Facility registry, on delete: restrict
- facility_state: string, ISO 3166-2 US state code (e.g. "TX"), required
  — derived from facility_id via facility registry at WS1 brief creation time;
    used by WS2 HR-3 gate (placement-state licence check); must not be null
    when brief_status = ADVANCED_TO_WS2
- unit_type: string, max 64 chars, required — e.g., "ICU", "Med/Surg", "ED"
- specialty_required: enum [RN_GENERAL, RN_ICU, RN_ED, RN_PACU, RN_OR, LPN,
    CNA, RN_TELE, UNRESOLVED], required
  — UNRESOLVED triggers NEEDS_COORDINATOR_INPUT; MUST NOT be UNRESOLVED
    when brief_status = ADVANCED_TO_WS2 (governance hard stop, D4a §0)
- credential_level: enum [RN, LPN, CNA, NP, UNRESOLVED], required
- shift_datetime_start: ISO 8601 timestamp UTC, required
- shift_datetime_end: ISO 8601 timestamp UTC, required; must be > shift_datetime_start
- urgency: enum [EXPLICIT_URGENT, IMPLICIT_URGENT, STANDARD], required
- message_type: enum [STANDARD_SHIFT_REQUEST, MULTI_SHIFT_BLOCK, CANCELLATION,
    MODIFICATION, UNCLASSIFIABLE], required
- special_notes: string, max 1000 chars, optional
  — verbatim extracted text not mapped to structured fields; passed to WS2 for
    coordinator context
- brief_status: enum [READY_FOR_REVIEW, NEEDS_COORDINATOR_INPUT, ADVANCED_TO_WS2,
    CANCELLED], required
- confidence_scores: JSON object, required
  — keys: all extracted field names; values: float 0.0–1.0 per field;
    must contain a key for every field in the extraction attempt
- missing_fields: array of strings, optional (empty array [] when none)
  — populated when brief_status = NEEDS_COORDINATOR_INPUT; lists field names
    that are null or UNRESOLVED
- created_at: ISO 8601 timestamp UTC, immutable, set on creation
- updated_at: ISO 8601 timestamp UTC, updated on any modification
- created_by: string — "AGENT" when WS1 creates; UUID of coordinator if created manually

Relationships:
- facility_id: UUID, foreign key to Facility registry, many-to-one, on delete: restrict

State machine:
- Initial state: READY_FOR_REVIEW or NEEDS_COORDINATOR_INPUT
  (set at creation based on completeness gate; never created in ADVANCED_TO_WS2)
- NEEDS_COORDINATOR_INPUT → READY_FOR_REVIEW:
    coordinator submits all missing fields via HITL resolution
- READY_FOR_REVIEW → ADVANCED_TO_WS2:
    completeness guard passes AND coordinator approves (or urgency = EXPLICIT_URGENT
    AND all fields confidence ≥ 0.85)
- READY_FOR_REVIEW → NEEDS_COORDINATOR_INPUT:
    coordinator requests correction on a previously accepted brief
- READY_FOR_REVIEW → CANCELLED:
    CANCELLATION message received for same source_message_id
- NEEDS_COORDINATOR_INPUT → CANCELLED:
    coordinator marks request as withdrawn
- ADVANCED_TO_WS2 → CANCELLED:
    coordinator cancels after WS2 pipeline initiated (WS2 must also cancel its pipeline)
- Terminal states: CANCELLED — no valid exit

Invalid transitions (WS1 enforces; WS2 validates on intake):
- NEEDS_COORDINATOR_INPUT → ADVANCED_TO_WS2: FORBIDDEN
    — governance hard stop; completeness gate must pass and coordinator must approve first
- CANCELLED → any state: FORBIDDEN
    — terminal; create a new MatchingBrief if re-submission required
- ADVANCED_TO_WS2 → READY_FOR_REVIEW: FORBIDDEN
    — WS2 pipeline already initiated; cancel and resubmit required
- READY_FOR_REVIEW → GENERATING: FORBIDDEN
    — state does not exist on MatchingBrief (belongs to CandidateShortlist)

Guard conditions:
- Transition READY_FOR_REVIEW → ADVANCED_TO_WS2 requires all of:
    specialty_required != UNRESOLVED
    credential_level != UNRESOLVED
    facility_id is a valid UUID resolvable in the facility registry
    facility_state is a non-null, valid ISO 3166-2 US state code
    shift_datetime_end > shift_datetime_start

Validation rules:
- shift_datetime_end > shift_datetime_start: boolean; reject on creation if false
- specialty_required != UNRESOLVED when brief_status = ADVANCED_TO_WS2: boolean
- credential_level != UNRESOLVED when brief_status = ADVANCED_TO_WS2: boolean
- facility_state is non-null when brief_status = ADVANCED_TO_WS2: boolean
- confidence_scores contains a key for every extracted field: boolean
- missing_fields is an empty array [] when brief_status = READY_FOR_REVIEW: boolean

Naming conventions:
- ServiceNow table: x_medflex_matching_briefs (assumed — see Preamble §5 G-3)
- Field naming: snake_case throughout
- Enum values: SCREAMING_SNAKE_CASE, exhaustive — no "other" bucket
```

---

### Entity: HITLQueueItem

```
Entity: HITLQueueItem

Purpose: Routes escalations from either agent module to the coordinator review queue.
Created by WS1 on: missing required field, unclassifiable message, implicit urgency
confirmation. Created by WS2 on: no-candidate shortlist, credential re-check failure,
race condition, withdrawal failure, shortlist expiry, nurse database unavailability.
One entity definition covers both modules — same fields, same state machine.

Attributes:
- id: UUID, primary key, immutable, generated on creation
- matching_brief_id: UUID, foreign key to MatchingBrief, required, on delete: cascade
- gap_type: enum [MISSING_REQUIRED_FIELD, UNCLASSIFIABLE_MESSAGE,
    IMPLICIT_URGENCY_CONFIRMATION, SPECIALTY_AMBIGUITY, NO_CANDIDATES,
    CREDENTIAL_RECHECK_FAILED, RACE_CONDITION, WITHDRAWAL_FAILED,
    SHORTLIST_EXPIRED, DATABASE_UNAVAILABLE], required
  — exhaustive; no "other" bucket; gap_type values are additive as agent scope grows
- missing_fields: array of strings, optional
  — e.g., ["specialty_required", "shift_datetime_end"];
    MUST be populated (non-empty) when gap_type = MISSING_REQUIRED_FIELD;
    empty [] is a serialisation error for this gap_type (see D4a §12 FM-A-3)
- agent_note: string, max 500 chars, optional
  — human-readable explanation of why item was escalated; included for coordinator context
- assigned_to: UUID (coordinator user ID), optional — null if unassigned
- status: enum [OPEN, IN_REVIEW, RESOLVED, EXPIRED], required
- sla_deadline: ISO 8601 timestamp UTC, required
  — set at creation: created_at + SLA per gap_type (see HITL checkpoint tables in
    D4a §13 and D4b §13 for per-gap_type SLA values)
- resolved_at: ISO 8601 timestamp UTC, optional — set when status → RESOLVED
- resolved_by: UUID (coordinator user ID), optional
- created_at: ISO 8601 timestamp UTC, immutable
- updated_at: ISO 8601 timestamp UTC, updated on any state change

Relationships:
- matching_brief_id: UUID, foreign key to MatchingBrief, many-to-one, on delete: cascade
  — cascade: if MatchingBrief is CANCELLED, associated HITLQueueItems are also removed

State machine:
- Initial state: OPEN
- OPEN → IN_REVIEW: coordinator opens the item in the HITL queue interface
- IN_REVIEW → RESOLVED:
    coordinator submits the required action (field completion, selection, instruction);
    the upstream record (MatchingBrief or CandidateShortlist) is updated accordingly
- OPEN → EXPIRED: current_time > sla_deadline AND status = OPEN
- IN_REVIEW → EXPIRED: current_time > sla_deadline AND status = IN_REVIEW
- EXPIRED → OPEN: supervisor re-activates manually (supervisor-only action)
- Terminal states: RESOLVED, EXPIRED (unless supervisor re-activates to OPEN)

Invalid transitions:
- RESOLVED → IN_REVIEW: FORBIDDEN
    — create a new HITLQueueItem if re-work is needed; do not modify a resolved record
- EXPIRED → RESOLVED: FORBIDDEN
    — must be re-activated to OPEN first (supervisor action), then resolved normally
- OPEN → RESOLVED: FORBIDDEN
    — must pass through IN_REVIEW; skipping IN_REVIEW bypasses the coordinator's
      acknowledgement record

Validation rules:
- sla_deadline > created_at: boolean; reject on creation if false
- resolved_at is set when status = RESOLVED: boolean
- resolved_by is a valid coordinator UUID when status = RESOLVED: boolean
- missing_fields is non-empty when gap_type = MISSING_REQUIRED_FIELD: boolean

Naming conventions:
- ServiceNow table: x_medflex_hitl_queue (assumed — see Preamble §5 G-3)
- gap_type values: SCREAMING_SNAKE_CASE, exhaustive
```

---

## Preamble §3: Data and System Requirements

Requirements are derived from the WS1 and WS2 activity catalogs (D4a §4, D4b §4). Each requirement is grouped into one of four categories.

### Input data — what each agent reads to do its work

| Data element | Agent(s) | Source | Required latency |
|---|---|---|---|
| Inbound shift request text (message body, sender, received_at) | WS1 (WS1-T1, WS1-T2) | ServiceNow inbound message queue | Real-time lookup — polling every 10 seconds; < 10s latency acceptable |
| Facility name → facility_id mapping (all known facilities) | WS1 (WS1-T4) | ServiceNow facility registry | On-demand retrieval per message; must be current at time of brief creation |
| Existing open placement records for facility (duplicate/modification detection) | WS1 (WS1-T2) | ServiceNow placement records | On-demand retrieval per message; staleness window ≤ 10 seconds acceptable |
| Validated MatchingBrief (status = ADVANCED_TO_WS2) | WS2 (WS2-T1) | ServiceNow matching_briefs table | On-demand retrieval per WS2 invocation; must be the latest committed record |
| NurseProfile records (credential_status, specialty_credentials, placement_states, availability, proximity, profile_notes, dnr_facility_ids, last_shift_end, offboarded) | WS2 (WS2-T2 through WS2-T8) | Nurse database (structured, [DS-confirmed]) | On-demand retrieval per MatchingBrief; fresh data required — no stale cache for credential status |
| Single NurseProfile record for pre-submission credential re-check | WS2 (WS2-T13) | Nurse database | On-demand, immediately before each submission write; staleness of any kind is not acceptable |
| Facility confirmation events (submission_id, confirmed_by_facility_id, confirmed_at) | WS2 (WS2-T16) | ServiceNow placement_submissions (polling) | On-demand polling every 15 seconds; confirmation must trigger withdrawal within ≤ 60 seconds of event |

### Reference data — policy documents and materials the agents consult

| Data element | Agent(s) | Format | Notes |
|---|---|---|---|
| Specialty taxonomy reference (canonical enum values and synonym mappings) | WS1 (WS1-T3) | Structured JSON config | Currently in coordinator knowledge and informal documents — not machine-readable; documentation workshop is a prerequisite before WS1 extraction calibration (see Preamble §7 checklist) |
| HR gate rules (HR-1 credential completeness, HR-2 specialty-to-credential match, HR-3 placement-state, HR-4 DNR exclusion, HR-5 rest period) | WS2 (WS2-T3 through WS2-T7) | Structured decision rules in agent system prompt | Static — changes require a deployment event; rules are deterministic boolean checks |
| Profile note classification guidelines (LLM prompt) | WS2 (WS2-T8) | Text prompt template | Embedded in agent procedural memory; versioned alongside agent deployments |
| Urgency classification rules (keyword list for EXPLICIT_URGENT; 4-hour threshold for IMPLICIT_URGENT) | WS1 (WS1-T5) | Structured config (keyword list + threshold constant) | Static; changes require version bump |

### Output targets — systems the agents write to

| Output | Target system | Tables / queues written | Agent |
|---|---|---|---|
| MatchingBrief record | ServiceNow | x_medflex_matching_briefs | WS1 (WS1-T7) |
| HITLQueueItem record | ServiceNow | x_medflex_hitl_queue | WS1 (WS1-T8), WS2 (WS2-T6, WS2-T11, WS2-T13, WS2-T18) |
| Agent audit log entry | ServiceNow | x_medflex_agent_audit_log | WS1 (WS1-T9), WS2 (multiple tasks) |
| CandidateShortlist record | ServiceNow | x_medflex_candidate_shortlists | WS2 (WS2-T11) |
| PlacementSubmission record | ServiceNow | x_medflex_placement_submissions | WS2 (WS2-T14, WS2-T15) |
| MultiSubmissionRecord (create + update) | ServiceNow | x_medflex_multi_submission_records | WS2 (WS2-T15, WS2-T17) |
| Withdrawal status update | ServiceNow | x_medflex_placement_submissions (PATCH) | WS2 (WS2-T17) |

### Approval and governance channels — how approver sign-off is captured and made auditable

| Gate | Channel | Captured in | Audit evidence |
|---|---|---|---|
| WS2 advance gate — coordinator validates MatchingBrief before WS2 matching begins | HITLQueueItem resolution (HITL queue IN_REVIEW → RESOLVED); or EXPLICIT_URGENT auto-advance with audit flag | HITLQueueItem.resolved_by + resolved_at; or MatchingBrief audit log entry with auto-advance flag | Queryable: ServiceNow HITL queue + agent_audit_log |
| Submission approval — coordinator selects candidate and approves placement before execution | Coordinator selection event in CandidateShortlist (selected_by + selected_at); PlacementSubmission write requires approved_by UUID | PlacementSubmission.approved_by + approved_at; CandidateShortlist.selected_by + selected_at | Queryable: ServiceNow placement_submissions join coordinator user table |
| Race condition resolution — coordinator selects which facility confirmation to honour | HITLQueueItem(gap_type=RACE_CONDITION) resolved by coordinator; coordinator instruction triggers withdrawal execution | HITLQueueItem.resolved_by + agent audit log entries for withdrawal execution | Queryable: HITLQueueItem + placement_submissions |
| Implicit urgency pre-emption — coordinator confirms queue jump | HITLQueueItem(gap_type=IMPLICIT_URGENCY_CONFIRMATION) resolution; 10-minute SLA; auto-advances if unconfirmed (logged as auto-advance in compliance_flags) | HITLQueueItem + agent_audit_log compliance_flags entry if auto-advanced | Queryable: ServiceNow audit log |

---

## Preamble §4: System and Data Inventory

For every system or data source required by either agent.

**Access types:** Read / Write / Read-Write / RAG / Event trigger
**Inferred availability:** API likely available / API unknown / Manual or document-only / Unknown
**Priority:** Required / Important / Optional

| # | System / Source | Data needed | Access type | Inferred availability | Gap / Risk | Priority |
|---|---|---|---|---|---|---|
| 1 | ServiceNow — inbound message queue | Inbound shift request text, sender email, received_at timestamp, channel (email / portal / phone) | Read | API likely available | Table name x_medflex_inbound_messages is assumed; not named in scenario. Named in scenario context (discovery-session confirmed [DS-confirmed]) — table names and API specifics are assumptions beyond what is stated. | Required |
| 2 | ServiceNow — facility registry | facility_name → facility_id mapping; facility_state (ISO 3166-2 state code) per facility | Read | API likely available | Table structure and field names assumed. Named in scenario context [DS-confirmed] — API specifics are assumptions. | Required |
| 3 | ServiceNow — case management tables (matching_briefs, candidate_shortlists, placement_submissions, multi_submission_records) | MatchingBrief records (WS1 write / WS2 read); CandidateShortlist (WS2 write); PlacementSubmission (WS2 write / update); MultiSubmissionRecord (WS2 write / update) | Read-Write | API likely available | All table names are assumed; custom tables require ServiceNow admin setup before build sprint 1. Named in scenario context [DS-confirmed] — table names and write-access scope are assumptions. | Required |
| 4 | ServiceNow — HITL queue (hitl_queue table) | HITLQueueItem records — written by both modules; read by coordinators; status transitions captured as audit trail | Read-Write | API likely available | Table name assumed; coordinator-facing UI must be built or configured in ServiceNow. Named in scenario context [DS-confirmed] — module configuration capability is an assumption [A-D3-5]. | Required |
| 5 | ServiceNow — agent audit log (agent_audit_log table) | One log entry per agent action per message processed; schema defined in D4a §13 | Write | API likely available | Table name assumed; retention policy (7 years for compliance logs) must be configured in ServiceNow. Named in scenario context [DS-confirmed] — retention configuration is an assumption. | Required |
| 6 | Nurse database | NurseProfile records: credential_status, specialty_credentials, credential_expiry_dates, placement_states, availability_status, availability_schedule, proximity_km_to_facility, profile_notes, dnr_facility_ids, last_shift_end, offboarded | Read | API unknown | Database confirmed as structured [DS-confirmed]. API endpoint, authentication method, query parameter schema, rate limits, and sandbox access are unconfirmed [A-D3-1]. Not named in scenario — existence as structured DB is discovery-session confirmed; API availability is assumed. | Required |
| 7 | DNR list per facility (nurse exclusions) | nurse_id exclusions per facility_id — used for HR-4 gate in WS2-T6 | Read | API unknown | May be embedded in the nurse database (as dnr_facility_ids[] on NurseProfile) or maintained separately. Structure and queryability not confirmed [A-D3-2]. Not named in scenario — existence is contractual assumption; data representation is unknown. | Required |
| 8 | Specialty taxonomy reference | Canonical specialty enum values (RN_ICU, RN_ED, etc.) and synonym mappings used for NLP extraction normalisation in WS1-T3 | Read | Manual or document-only | Currently lives in coordinator knowledge and informal documents (email threads, verbal convention); no machine-readable taxonomy confirmed in scenario or discovery. Not named in scenario — must be extracted from coordinators in a documentation workshop before build begins. | Required |
| 9 | LLM API (claude-sonnet-4-6) | Profile note classification for WS2-T8: classifies free-text profile notes as BLOCKING / RISK_SIGNAL / NEUTRAL per facility and specialty context | Read (API call) | API likely available | Anthropic API access assumed; rate limits and cost per call are configuration decisions. Model ID confirmed in session environment. Not named in scenario — existence and API availability are assumed. | Required |
| 10 | Historical shift request samples | 200+ prior inbound messages with ground-truth field extractions — used for WS1 threshold calibration and WS2 golden-set validation of profile note classification | Read | Unknown | Existence in ServiceNow or legacy archive not confirmed. Not named in scenario — existence and accessibility are assumed. | Important |
| 11 | SMS/email notification gateway | Outbound SLA breach alerts to on-call coordinator and supervisor; used for HITL SLA expiry alerts and governance hard stop escalations | Write | API likely available (likely same gateway used for nurse confirmation notifications [DS-confirmed]) | Gateway tech stack assumed to be the same as nurse confirmation dispatch (WS4 RPA workstream); may require separate routing config for agent-generated alerts. Named in scenario context [DS-confirmed for nurse notifications] — separate use for agent alerts is an assumption. | Important |

**How this table drives §9 in per-agent specs:**
- Rows 1–5, 9: Required + API likely available → full integration contracts in D4a §9 and D4b §9
- Row 6 (nurse database): Required + API unknown → `[SCOPE-OUT]` in D4b §9 with resolution plan; full entry in D4b §14
- Row 7 (DNR list): Required + API unknown → `[SCOPE-OUT]` in D4b §9 with stub behaviour; full entry in D4b §14
- Row 8 (specialty taxonomy): Required + Manual or document-only → addressed in §7 pre-deployment checklist; not an API integration
- Rows 10–11: Important → noted in D4a §14 and D4b §14; omitted from §9 unless required for MVP

---

## Preamble §5: Gap Analysis

For every inventory row rated "API unknown," "Manual or document-only," or "Unknown."

---

> **Gap [G-1]: Nurse database — API access**
> **What the agent cannot do without it:** WS2-T2 (candidate pool identification — primary agentic task, D2B 5/7), WS2-T13 (pre-submission credential re-check — governance hard stop). Both are fully blocked. The entire WS2 shortlist generation pipeline cannot run without a queryable nurse database API.
> **Severity:** Blocking — WS2 module cannot launch; the primary business-case metric (time-to-fill compression) is undeliverable
> **Mitigation options:**
> (1) MedFlex IT documents the nurse database API spec (endpoint, auth, query params, response schema) before build sprint 1; agent is built to that spec — fastest path
> (2) If no REST API exists, build a thin API wrapper on top of the existing database connection; MedFlex IT owns the wrapper; agent team provides the query contract spec
> (3) Defer WS2 matching automation until the API is available; run the Week 6 pilot against a manually maintained flat-file export of NurseProfile records (limited to the pilot facility and specialty) as a stub — acceptable for 1-facility pilot only, not for production
> **Discovery action:** "What is the nurse database system name and technology stack? Does it expose a REST API today? If so, where is the API documentation and who controls access credentials? If not, is there a supported direct database connection method (e.g., JDBC, ODBC)?"

---

> **Gap [G-2]: DNR list — data structure and queryability**
> **What the agent cannot do without it:** WS2-T6 (HR-4 DNR exclusion check). The agent cannot enforce the facility-specific Do Not Return exclusion before submitting a candidate. Without HR-4, an excluded nurse may be submitted to a facility that has a standing relationship-based or safety-based exclusion — a compliance and relationship risk.
> **Severity:** Blocking — HR-4 is a non-negotiable hard exclusion gate; the agent cannot be certified as credential-safe for production deployment without it
> **Mitigation options:**
> (1) Confirm that the nurse database already stores dnr_facility_ids[] as a field on each NurseProfile record (the D4b §3 NurseProfile entity models this); if confirmed, no separate DNR API is needed — Gap G-2 is resolved by the answer to Gap G-1
> (2) If DNR lists are maintained separately (ServiceNow facility record, spreadsheet, email threads), scope a DNR data migration into the nurse database as a Wave 1 prerequisite before WS2 pilot
> (3) For the Week 6 pilot only: stub HR-4 with empty exclusion list; flag every shortlist in the audit log with compliance_flag = "HR4_DNR_UNVERIFIED"; coordinator must manually verify DNR status before approving each pilot submission — acceptable for 1-facility, 2-coordinator pilot scope only
> **Discovery action:** "Are facility Do Not Return lists for nurses currently stored in a structured system, or are they maintained informally? If structured, are they in the nurse database as a field on each nurse record, or stored per facility in a separate system?"

---

> **Gap [G-3]: Specialty taxonomy — machine-readable format**
> **What the agent cannot do without it:** WS1-T3 (structured field extraction — specialty_required normalisation). Without a confirmed canonical taxonomy, the WS1 NLP extraction cannot reliably map free-text specialty strings (e.g., "ICU experienced," "ER nurse," "trauma-trained RN") to the enum values used in the nurse database query (e.g., RN_ICU, RN_ED). Systematic extraction errors at WS1 propagate directly to WS2 matching — the cascade error path identified in D2A Observation 1.
> **Severity:** Degrading — WS1 launches but UNRESOLVED escalation rate will be systematically high on first deployment; coordinator HITL queue flooded with specialty resolution requests
> **Mitigation options:**
> (1) Run a 2-hour coordinator taxonomy workshop before build begins: have two coordinators list the 10–15 most common specialty terms seen in inbound shift requests, including facility-specific shorthand; document as structured JSON config file; version-control it
> (2) Begin with a limited taxonomy (5–6 specialty types covering the highest-volume facilities) sufficient for the Week 6 pilot; expand the taxonomy in Wave 1 before full WS2 deployment
> (3) Run WS1 in high-sensitivity mode (accept-threshold = 0.85 for specialty extraction; everything below escalates) for the first 4 weeks; use coordinator resolutions to build a human-curated synonym map as the production taxonomy
> **Discovery action:** "What are the specialty credential labels that appear most frequently in inbound shift requests from your hospital clients? Are there facility-specific shorthand terms or informal labels that coordinators recognise but are not in any published credential list?"

---

> **Gap [G-4]: Historical shift request samples — existence and accessibility**
> **What the agent cannot do without it:** WS1 confidence threshold calibration (D4a §14 A-6: threshold values 0.70 / 0.50 are design assumptions, not validated calibrations); WS2 golden-set evaluation for profile note classification (D4b §14 — weekly 20-note audit requires ground-truth labels derived from historical notes).
> **Severity:** Degrading — the agent can be deployed with assumed thresholds; systematic calibration errors will surface post-deployment through HITL volume metrics; delayed calibration extends the period of elevated coordinator workload
> **Mitigation options:**
> (1) Export 200 inbound shift request messages from ServiceNow with coordinator-completed extraction results; use as calibration set for WS1 threshold tuning before Wave 2 deployment
> (2) If historical data is insufficient (< 200 messages), use live shadow mode for the first 4 weeks of Wave 1 WS1 (agent extracts alongside coordinator on the same messages); coordinator-resolved extractions become the calibration dataset
> (3) Defer threshold calibration to post-pilot data; deploy with conservative defaults (0.70 accept / 0.50 flagged-accept) and plan a calibration sprint after 4 weeks of pilot data
> **Discovery action:** "Are historical inbound shift request messages stored in ServiceNow with coordinator-completed field extractions? If so, how many messages from the past 12 months are available and accessible via API?"

---

## Preamble §6: Integration Risk Register

| System | Risk type | Risk description | Likelihood (H/M/L) | Impact (H/M/L) | Mitigation |
|---|---|---|---|---|---|
| ServiceNow | API availability risk | ServiceNow API downtime affects all read/write operations for both modules simultaneously — intake queues, HITL queues, and submission records all depend on the same instance | M | H | Dead-letter queue + local buffer for in-flight records; alert on-call engineering within 5 minutes of API failure; no fill proceeds without ServiceNow write confirmation; polling resumes automatically on recovery |
| ServiceNow | Audit trail risk | If agent_audit_log writes fail and are not detected, compliance evidence is incomplete; HIPAA 7-year retention requirement is not met for records that were never written | L | H | Per REQ-A-6 (D4a §5): audit log write failure triggers rollback of the triggering action; daily reconciliation job: messages_received count = audit_log_entries count; mismatch triggers alert |
| ServiceNow | Sign-off integrity risk — **procedure-dependent enforcement** | The submission approval gate (AGENT PROPOSES, HUMAN APPROVES) is **procedure-dependent in Phase 1**: the agent validates the approved_by UUID field in code before writing the PlacementSubmission record, but ServiceNow does not enforce a workflow state that **technically blocks** the write without a prior coordinator approval event. A code path error, race condition, or deliberate bypass could produce a PlacementSubmission without a valid approved_by value. **This is procedure-dependent enforcement, not system-enforced.** The transition from procedure-dependent to system-enforced requires a ServiceNow workflow lock on PlacementSubmission creation that requires a coordinator approval event as a prerequisite — this is a pre-deployment prerequisite per D4b §8 and Preamble §7 checklist item 5. | M | H | Technical mitigation: deploy the ServiceNow workflow lock before Wave 2 Phase 1 go-live; this converts the gate from procedure-dependent to system-enforced. Operational mitigation until then: daily automated query — any PlacementSubmission with approved_by = null or invalid UUID is a governance breach alert; supervisor notified immediately. Per-submission audit log entry with compliance_flag if approved_by is invalid |
| ServiceNow | Data quality risk | Facility registry staleness: a facility is renamed in the client's source system but the registry record is not updated; WS1 resolves the old name to the old facility_id via fuzzy match, and WS2 queries the wrong facility's credential and DNR profile | M | H | Monthly facility registry audit (compare inbound request facility names against current registry exact-match names); any coordinator HITL resolution that maps a name to "known facility" triggers a registry update review; D4a §12 FM-A-4 |
| Nurse database | API availability risk | Nurse database API downtime blocks all WS2 shortlist generation and pre-submission credential re-checks; WS2 cannot produce any shortlist or execute any submission without fresh nurse data | H | H | Block shortlist / submission immediately on 3-retry exhaustion; write HITLQueueItem (DATABASE_UNAVAILABLE); no stale-cache fallback permitted for credential checks; alert engineering on-call; auto-retry every 60 seconds |
| Nurse database | Data quality risk | Credential status in the nurse database may not be updated in real time after a licence expires or a renewal is issued; the agent queries a stale credential_status value and passes a nurse whose credential has since lapsed | M | H | Pre-submission credential re-check (WS2-T13) runs immediately before write, not at shortlist generation time; 30-day expiry flag surfaces near-expiry credentials to coordinator at shortlist time (WS2-T10); D4b §12 FM-B-4 (stale data) |
| DNR list | API availability risk | DNR list data structure unknown at spec time; if stored in a system separate from the nurse database, a separate API must be built, confirmed, and integrated; if that integration is missing, HR-4 gate cannot be enforced | H | H | Stub with empty exclusion list for pilot only (all shortlists flagged "HR4_DNR_UNVERIFIED"); confirm DNR data structure before Wave 2 production go-live; see Gap G-2 mitigation options |
| Specialty taxonomy | Data quality risk | Taxonomy is documented informally (coordinator knowledge, email threads); if the agent is calibrated against an incomplete or inaccurate taxonomy, specialty extraction errors are systematic and propagate into WS2 matching — wrong specialty_required → wrong candidate pool → mismatch risk | M | M | Taxonomy documentation workshop before WS1 build sprint (see Gap G-3); taxonomy is version-controlled and the agent rejects requests to operate against a version older than the client's confirmed current version |
| LLM API (claude-sonnet-4-6) | API availability risk | LLM profile note classification call may fail on timeout or API error; if the fallback (RISK_SIGNAL conservative default) is not applied, a candidate with a BLOCKING note might appear on the shortlist without a flag | L | M | Conservative failure path: on any LLM call failure, classify as RISK_SIGNAL and add display_flag "Note classification unavailable — review manually" (REQ-B-2, D4b §5); NEUTRAL is never the failure default |
| LLM API | Legal / compliance risk | Profile note classification may correlate with protected characteristics if the profile note text includes demographic signals (age, disability, national origin); an agent that systematically classifies notes about protected characteristics as BLOCKING could create disparate-impact liability | L | H | Classification prompt explicitly constrains reasoning to facility-relationship and reliability evidence, not personal characteristics; output must cite specific facility-relevant text (profile_note_excerpt field); weekly audit of BLOCKING classifications reviews excerpts for compliance; legal review of prompt before deployment |

---

## Preamble §7: Context Engineering Design

### Memory architecture

| Memory type | Content | Storage mechanism | Lifecycle |
|---|---|---|---|
| In-context (short-term) | WS1: inbound message text, extracted field values, per-field confidence scores, facility resolution result, urgency classification, completeness gate result. WS2: MatchingBrief fields, NurseProfile records for all shortlisted candidates (credentials, availability, proximity, profile notes), profile note classification results, shortlist ranking state, withdrawal confirmation event. | Agent context window (LLM prompt + sequential tool call results within one invocation) | Per fill cycle — one context window per inbound message / per MatchingBrief processed; cleared between invocations; no state persists in the context window across separate fill cycles |
| Semantic (long-term, retrieval) | Specialty taxonomy reference (canonical labels + synonym mappings for WS1 NLP extraction normalisation); facility registry snapshot (facility_name → facility_id + facility_state, cached for the current polling window). | Specialty taxonomy: static JSON config file deployed with the agent; Facility registry: ServiceNow API query result cached in-memory for the active polling cycle (10-second window) | Specialty taxonomy: persistent across deployments; updated on version bump after client taxonomy workshop; agent must reject if running on a version older than the confirmed current version. Facility registry: refreshed per polling cycle; stale cache from the previous cycle is not used for the current invocation |
| Procedural (static instructions) | HR gate rules (HR-1 through HR-5 decision conditions and threshold values); completeness gate required-field schema; urgency classification rules (keyword list + 4-hour threshold); profile note classification LLM prompt template; confidence threshold rules (0.70 auto-accept / 0.50 flagged-accept); shortlist ranking tiebreaker sequence; SLA timer values per gap_type; governance hard stop conditions. | Agent system prompt and configuration file (versioned; stored in source control alongside agent code) | Static between deployments; changes to any rule require a deployment event + version bump; no runtime mutation permitted; configuration version is logged in every audit log entry |

### Retrieval strategy

**What triggers a retrieval call?**

| Task ID | Trigger | Retrieval target |
|---|---|---|
| WS1-T4 | Facility name string extracted from inbound message text | ServiceNow facility registry — exact string match first; fuzzy match (score ≥ 0.80) if exact fails; returns facility_id and facility_state |
| WS1-T3 | Specialty string extracted from inbound message text | Static specialty taxonomy config — canonical enum lookup + synonym expansion; returns canonical enum value or UNRESOLVED |
| WS2-T2 | MatchingBrief with status = ADVANCED_TO_WS2 received | Nurse database query API — structured filter on specialty_required, credential_level, placement_states, shift_datetime window, max_proximity_km; returns NurseProfile array |
| WS2-T13 | Coordinator selects candidate and approves submission | Nurse database — single NurseProfile record by nurse_id; credential_status field; must be a fresh read, not a cached result from WS2-T2 |
| WS2-T8 | Non-empty profile_notes field on a shortlisted candidate | LLM API (claude-sonnet-4-6) — single inference call per candidate; input: profile_notes text + facility_id name + specialty_required; output: classification JSON |

**Retrieval quality evaluation**

- **Facility registry (WS1-T4):** Pass if exact match score = 1.0 or fuzzy match score ≥ 0.80. Below 0.80 → UNCLASSIFIABLE escalation. False positive risk: a facility name with fuzzy score 0.80–0.89 that resolves to the wrong facility_id propagates an incorrect facility into all downstream gates. Monthly audit: compare inbound request facility names against registry names; any coordinator-confirmed resolution that required manual mapping triggers a registry record update review.
- **Specialty taxonomy (WS1-T3):** Pass if canonical match found in the taxonomy config. No match → UNRESOLVED; write HITLQueueItem. False positive risk: a novel specialty term that fuzzy-matches to a wrong canonical value produces a wrong specialty_required — the most consequential extraction error because it bypasses all downstream gates without a flag. The taxonomy must be versioned and tested against a held-out set of inbound requests before each taxonomy update is deployed.
- **Nurse database query (WS2-T2):** Quality is evaluated by gate failure code distribution. If all candidates fail a single gate (e.g., 100% HR-2 failures for a specialty_required = RN_ICU query), this signals either an unusually thin database for that specialty or a brief with a specialty value not present in any nurse record — coordinator must be notified via HITLQueueItem gap_type = NO_CANDIDATES with gate filter counts. If HR-3 failures dominate (all nurses lack the facility's state licence), this signals a facility that MedFlex does not have coverage for — escalate to operations.
- **Pre-submission re-check (WS2-T13):** Binary pass/fail (credential_status = ACTIVE or not). No false-positive risk — if the check passes incorrectly (returns ACTIVE for an expired credential), the data quality risk is in the nurse database, not the retrieval mechanism. The expiry flag (WS2-T10) and the weekly credential audit (D4b §13) are the backstop.
- **Profile note classification (WS2-T8):** Weekly golden-set evaluation: 20 known-profile notes with ground-truth labels (BLOCKING / RISK_SIGNAL / NEUTRAL) run through the LLM; agreement must be ≥ 80% in each weekly run. **False-positive risk is asymmetric:** a false BLOCKING classification silently removes a valid candidate from the shortlist without coordinator awareness — this is the highest-consequence retrieval error in either agent. The agent_audit_log records profile_note_classification = BLOCKING for every excluded candidate, with the reasoning excerpt, making the exclusion auditable by the coordinator or compliance team on demand. If coordinator reports a "surprise" shortlist omission (expected candidate not present), the audit log is the primary investigation path.

**How retrieval costs are managed**

| Retrieval | Cost structure | Management strategy |
|---|---|---|
| Specialty taxonomy | Static config — zero per-call cost; one load per agent startup | No management needed; update on taxonomy version bump only |
| Facility registry | ServiceNow API call per inbound message | Cache result within the current 10-second polling batch; if the same facility appears in two messages in the same batch, second lookup hits cache; cache invalidated on new polling cycle |
| Nurse database query | One structured API call per MatchingBrief for shortlist generation; one single-record call per submission for re-check | No caching between invocations (credential status must be fresh); query parameters pre-filtered (specialty, state, availability date) to reduce result set size; max_proximity_km cap limits result set; avoid returning all records for in-memory filtering |
| Pre-submission re-check | Same API, single-record call | Always a fresh read; no caching; cost is per submission, not per candidate |
| LLM profile note classification | One API call per non-empty profile note on a shortlisted candidate; max 5 candidates per shortlist | At current volume (120 shortlists/day × max 5 notes = max 600 LLM calls/day), cost is manageable; monitor at 14× scale target; if cost becomes significant, batching multiple notes in one API call with a structured output schema can reduce call count |

### Pre-deployment prerequisite checklist

The following must be confirmed before build begins. Each item names what is confirmed, who confirms it, and what is blocked if unconfirmed.

- [ ] **Specialty taxonomy format — machine-readable documentation**
  Content: The specialty taxonomy used by MedFlex coordinators must be documented as a structured JSON config file (canonical enum values + synonym mappings per specialty type) before WS1 extraction prompt calibration begins.
  **Confirmed by:** MedFlex Operations Lead (provides taxonomy content) + FDE (validates coverage against inbound request samples)
  **If unconfirmed:** WS1 extraction prompt is calibrated against assumed enum values; UNRESOLVED escalation rate will be systematically elevated on first deployment; coordinator HITL queue flooded with specialty resolution tasks; Gap G-3 remains open

- [ ] **Specialty taxonomy version control — machine-readable versioning**
  Content: The taxonomy config file must have a machine-readable version number and last_updated timestamp; the agent must reject operation if its loaded taxonomy version is older than the client's confirmed current version.
  **Confirmed by:** MedFlex Operations Lead + IT (version control mechanism)
  **If unconfirmed:** Agent continues operating on a stale taxonomy after client updates specialty labels; new specialty types go unresolved; systematic UNRESOLVED escalation spike with no detection mechanism

- [ ] **Primary write-target system — ServiceNow custom table schema**
  Content: All required custom tables (inbound_messages, matching_briefs, hitl_queue, agent_audit_log, candidate_shortlists, placement_submissions, multi_submission_records) must be created in the ServiceNow instance with confirmed table names and schema before integration contracts in D4a §9 and D4b §9 can be implemented.
  **Confirmed by:** MedFlex IT / ServiceNow admin (table creation and API confirmation)
  **If unconfirmed:** Integration contracts use assumed table names; builder creates wrong connectors; migration cost at sprint 1

- [ ] **Inbound trigger mechanism — intake path confirmation**
  Content: Whether the agent polls the ServiceNow inbound message queue (10-second polling) or receives a webhook push from ServiceNow must be confirmed; polling must be approved by MedFlex IT security for the agent host.
  **Confirmed by:** MedFlex IT security
  **If unconfirmed:** Agent defaults to polling; if IT blocks outbound API access from the agent host, intake is entirely blocked; webhook alternative adds integration scope

- [ ] **Approval and audit trail — ServiceNow submission approval workflow**
  Content: The coordinator approval event for PlacementSubmission creation must be capturable as a structured record write (approved_by UUID + approved_at timestamp) in ServiceNow. The recommended system-enforced mechanism — a ServiceNow workflow state that blocks PlacementSubmission creation without a prior coordinator approval event — must be confirmed as technically buildable and deployed before Wave 2 Phase 1 go-live.
  **Confirmed by:** MedFlex IT / ServiceNow admin
  **If unconfirmed:** Submission gate remains procedure-dependent only; governance risk per D4a §8 and D4b §8 is active; procedure-dependent enforcement is acceptable for pilot but not for production at full volume (960+ decisions/day)

- [ ] **Known-stale reference sections — credential rules and specialty taxonomy**
  Content: Any credential type, specialty classification, or HR gate rule known to be outdated (e.g., deprecated credentials, revised state licensing requirements, retired specialty categories) must be identified, excluded from agent scope, and documented before deployment; the agent must not classify nurses against retired credential categories.
  **Confirmed by:** MedFlex Compliance Lead
  **If unconfirmed:** Agent applies outdated credential categories; systematic gate misclassification possible; compliance team cannot certify agent outputs as regulatory-safe

- [ ] **Nurse database API access — endpoint, authentication, and sandbox (Required + API unknown)**
  Content: API endpoint (base URL, supported query operations), authentication method (OAuth 2.0 service account, API key, or other), query parameter schema (field names, types, filter operators), rate limits, and sandbox access for development and testing must all be confirmed before WS2 build sprint begins.
  **Confirmed by:** MedFlex IT (nurse database system owner)
  **If unconfirmed:** WS2 shortlist generation (WS2-T2), all HR gate checks (WS2-T3 through WS2-T7), and pre-submission credential re-check (WS2-T13) are entirely blocked; WS2 cannot be built or tested; Gap G-1 remains open; Wave 2 deployment timeline cannot be committed

- [ ] **DNR list data structure — storage location and queryability (Required + API unknown)**
  Content: Whether DNR lists are stored as a field on each NurseProfile record in the nurse database (dnr_facility_ids[]) or in a separate system must be confirmed. If separate, API spec and update cadence are required before HR-4 gate implementation.
  **Confirmed by:** MedFlex Operations Lead (owns DNR list maintenance process)
  **If unconfirmed:** HR-4 gate cannot be implemented; all shortlists for the pilot must be flagged "HR4_DNR_UNVERIFIED" in the audit log; pilot must not be used to make final submission decisions without coordinator manual DNR verification; Gap G-2 remains open; agent cannot be certified as credential-safe for production deployment
