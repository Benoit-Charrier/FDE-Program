# D4 — Capability Specifications: Preamble
**Engagement:** Greenfield Health Systems — Medical Claims Adjudication Transformation
**Deliverable:** D4 Pass 1 — Shared preamble (§1–§3 + §7)
**Output file:** `Deliverables/D4_preamble_capability_spec.md`
**Inputs:** `C3_agentic_solution_architecture.md`, `D2A_cognitive_load_map.md`, `D2B_delegation_suitability_matrix.md`, `Scenario/scenario_context.md`

> **Note:** Preamble §4 (system inventory), §5 (gap analysis), and §6 (integration risk register) are produced separately in `Deliverables/D4_integration_preamble.md` using `prompt_D4_integration_specs.md`. The system names surfaced in §3 below are the input list for that exercise.

---

## Preamble §1: Agent Selection

### Agents specified in this deliverable

**Spec A: WS1 Administrative Adjudication Agent**

Source: D3 §2 Agent 2. Present in D3 Autonomy Matrix (§3) across the following action rows: member eligibility lookup; eligibility discrepancy resolution; code validity check; coding plausibility assessment; prior auth lookup; prior auth partial match tolerance resolution; clinical content routing (high-confidence and below-threshold); fee schedule calculation; fee schedule contract exception handling; payment approval — standard administrative claim.

Priority rationale: D3 §0 identifies WS1 as the primary agentic target for Wave 1. D2C classifies this agent at the highest-volume × highest-value position in the portfolio: 1,300 claims/day on the administrative path after routing, carrying the greatest throughput leverage and the best-documented financial case. This agent also hosts the clinical content classifier (WS1-JtD-2), which is the single most consequential design element in the entire engagement — it determines whether WS2 is triggered at all.

**Spec B: Clinical Review Support Agent**

Source: D3 §2 Agent 3. Present in D3 Autonomy Matrix (§3) across the following action rows: clinical content flag verification (high-confidence and below-threshold); clinical documentation retrieval (complete and incomplete); pre-filled review packet delivery to physician queue; additional information request (physician-triggered); determination documentation and reason coding.

Priority rationale: D3 Wave 2. Directly dependent on WS1 clinical classifier go-live (shared classifier component — ADR-2). Dr. Webb's 20 claims/hour throughput target (Exchange 3) is the primary WS2 economic case and depends on this agent producing complete, well-structured review packets. Specified here alongside WS1 because the two agents share the clinical content classifier and the PriorAuthRecord entity — specifying them together prevents glossary divergence at the shared boundary.

### Agents deferred (not specified in this deliverable)

**Intake & Anomaly Agent** (D3 §2 Agent 1): Deferred. Both JtDs (INT-JtD-1, INT-JtD-2) are Fully Agentic with deterministic decision logic. Lower specification complexity; no shared entities with WS1 or WS2 at the classification boundary. Recommended as a separate specification exercise once WS1 is approved.

**Queue & SLA Management Agent** (D3 §2 Agent 4): Deferred. Both JtDs (QMG-JtD-1, QMG-JtD-2) are Fully Agentic state-machine implementations with no LLM judgment content. The pending claims state management depends on ClaimRecord state produced by WS1; defer until WS1 specification is finalised to avoid defining ClaimRecord twice.

**Appeals Support Agent** (D3 §2 Agent 5): Explicitly Wave 3. Per D3 §2: "Wave 3 build should not begin until WS1 steady-state data confirms the residual appeal volume and root-cause distribution." No specification work is warranted before WS1 has been in production for at least 90 days.

---

## Preamble §2: Shared Entity Definitions

*Entities used by both Spec A (WS1) and Spec B (Clinical Review Support). Defined once here. Per-agent specs reference these by entity name — they do not redefine them.*

---

### Shared Entity: ClaimRecord

The canonical claim record that flows through the full adjudication pipeline. Created by the Intake & Anomaly Agent; read and updated by WS1 and the Clinical Review Support Agent.

```
Entity: ClaimRecord

Attributes:
- id: UUID, primary key, immutable, generated on creation by Intake & Anomaly Agent
- external_claim_id: string, max 50 characters, provider's submission identifier; required; immutable after creation
- submission_format: enum [EDI_837, PDF, PORTAL], required, immutable
- member_id: UUID, foreign key to external MemberRecord; required, immutable
- provider_id: string, max 10 characters, NPI format (10-digit numeric), required, immutable
- service_date: ISO 8601 date (YYYY-MM-DD), required, immutable
- submitted_at: ISO 8601 timestamp, UTC, required, immutable
- diagnosis_codes: array of strings; ICD-10-CM format (1 letter + 2–7 alphanumerics each);
  min length 1, max length 12; required
- procedure_codes: array of strings; CPT (5-digit numeric) or HCPCS (1 letter + 4 alphanumerics) format;
  min length 1, max length 25; required
- place_of_service: string, max 3 characters, CMS place of service code; required
- provider_specialty: string, max 100 characters; optional; used in clinical content classification
- billed_amount_cents: integer, USD cents, range 1–10,000,000; required
- current_state: enum [RECEIVED, NORMALISED, IN_ADMINISTRATIVE_VALIDATION,
  PENDING_PROVIDER_RESPONSE, CLINICAL_REVIEW_QUEUE, IN_PHYSICIAN_REVIEW,
  PENDING_ADDITIONAL_INFO, HITL_EXCEPTION_QUEUE, AUTO_APPROVED, AUTO_REJECTED,
  PHYSICIAN_APPROVED, PHYSICIAN_DENIED, RETURNED_TO_PROVIDER], required
- routing_decision: enum [ADMINISTRATIVE, CLINICAL, PENDING_CLASSIFICATION]; null until
  classification completes
- routing_confidence: float 0.0–1.0; null until classifier runs; set to null on human override
- classification_result_id: UUID, foreign key to ClinicalClassificationResult; null until
  classification completes; optional
- adjudication_decision_id: UUID, foreign key to AdjudicationDecision; null until decision issued; optional
- hitl_escalation_ids: array of UUID, foreign keys to HITLEscalation; empty array on creation
- sla_deadline: ISO 8601 timestamp, UTC; computed as submitted_at + 7 × 86400 seconds; required
- created_at: ISO 8601 timestamp, UTC, set on creation, immutable
- updated_at: ISO 8601 timestamp, UTC, updated on every field change or state transition
- created_by: UUID, reference to Intake & Anomaly Agent instance; immutable

Relationships:
- classification_result_id: UUID, foreign key to ClinicalClassificationResult,
  cardinality 0..1, on delete: RESTRICT
- adjudication_decision_id: UUID, foreign key to AdjudicationDecision,
  cardinality 0..1, on delete: RESTRICT
- hitl_escalation_ids: array of UUID, foreign keys to HITLEscalation,
  cardinality 0..many, on delete: RESTRICT

State machine:
- Initial state: RECEIVED
- RECEIVED → NORMALISED: Intake & Anomaly Agent completes format parsing with no blocking flags
- NORMALISED → IN_ADMINISTRATIVE_VALIDATION: WS1 agent picks up claim from intake queue
- IN_ADMINISTRATIVE_VALIDATION → PENDING_PROVIDER_RESPONSE: prior auth check returns
  auth_status = ABSENT; provider response request dispatched; SLA countdown maintained
- IN_ADMINISTRATIVE_VALIDATION → CLINICAL_REVIEW_QUEUE: clinical content classifier returns
  CLINICAL with confidence_score ≥ CLINICAL_CONTENT_CONFIDENCE_THRESHOLD
- IN_ADMINISTRATIVE_VALIDATION → HITL_EXCEPTION_QUEUE: any of: (a) eligibility discrepancy
  detected, (b) coding plausibility flag raised, (c) prior auth partial match outside tolerance,
  (d) classifier confidence < CLINICAL_CONTENT_CONFIDENCE_THRESHOLD, (e) contract exception
  flagged, (f) duplicate suspected
- IN_ADMINISTRATIVE_VALIDATION → AUTO_APPROVED: all administrative checks pass AND classifier
  returns ADMINISTRATIVE with confidence_score ≥ CLINICAL_CONTENT_CONFIDENCE_THRESHOLD AND
  payment calculation succeeds with no exception flag
- IN_ADMINISTRATIVE_VALIDATION → AUTO_REJECTED: eligibility confirmed ineligible with no
  discrepancy OR coding check returns irresolvable invalid pairing OR duplicate confirmed
- IN_ADMINISTRATIVE_VALIDATION → RETURNED_TO_PROVIDER: claim cannot be normalised or is
  missing required fields after extraction
- PENDING_PROVIDER_RESPONSE → IN_ADMINISTRATIVE_VALIDATION: provider response received with
  complete documentation; QMG agent triggers re-queue
- PENDING_PROVIDER_RESPONSE → AUTO_REJECTED: SLA deadline exceeded AND QMG agent has issued
  final escalation with no response
- HITL_EXCEPTION_QUEUE → IN_ADMINISTRATIVE_VALIDATION: HITL reviewer resolves exception and
  instructs agent to resume processing
- HITL_EXCEPTION_QUEUE → AUTO_APPROVED: HITL reviewer approves in exception review
- HITL_EXCEPTION_QUEUE → AUTO_REJECTED: HITL reviewer rejects in exception review
- HITL_EXCEPTION_QUEUE → CLINICAL_REVIEW_QUEUE: HITL reviewer overrides routing to clinical
- CLINICAL_REVIEW_QUEUE → IN_PHYSICIAN_REVIEW: Clinical Review Support Agent delivers
  pre-filled packet to physician queue; physician opens the claim
- IN_PHYSICIAN_REVIEW → PENDING_ADDITIONAL_INFO: physician requests additional information
  from provider
- IN_PHYSICIAN_REVIEW → PHYSICIAN_APPROVED: physician signs approval determination
- IN_PHYSICIAN_REVIEW → PHYSICIAN_DENIED: physician signs denial determination with reason code
- PENDING_ADDITIONAL_INFO → IN_PHYSICIAN_REVIEW: provider supplies additional information;
  Clinical Review Support Agent updates the packet
- PENDING_ADDITIONAL_INFO → PHYSICIAN_DENIED: SLA deadline exceeded with no provider response
  AND escalation has been issued
- Terminal states: AUTO_APPROVED, AUTO_REJECTED, PHYSICIAN_APPROVED, PHYSICIAN_DENIED,
  RETURNED_TO_PROVIDER — no valid exit from any terminal state

Invalid transitions (minimum required list):
- AUTO_APPROVED → any state: FORBIDDEN — auto-approved claims are immutable; any reconsideration
  requires a new claim submission
- PHYSICIAN_APPROVED → any state: FORBIDDEN — physician approval is the compliance audit record;
  modification requires a formal appeal (new APP record)
- AUTO_REJECTED → IN_ADMINISTRATIVE_VALIDATION: FORBIDDEN — rejected claims require provider
  resubmission; the ClaimRecord is immutable from rejection forward
- CLINICAL_REVIEW_QUEUE → AUTO_APPROVED: FORBIDDEN — a claim that has entered the clinical queue
  cannot be auto-approved; it must receive physician review or be returned
- IN_PHYSICIAN_REVIEW → IN_ADMINISTRATIVE_VALIDATION: FORBIDDEN — claims in physician review
  cannot be re-routed to the administrative path without a formal HITLEscalation record capturing
  the routing override rationale
- HITL_EXCEPTION_QUEUE → PHYSICIAN_APPROVED: FORBIDDEN — physician sign-off requires
  IN_PHYSICIAN_REVIEW state; HITL queue cannot skip the physician review workflow

Validation rules:
- service_date must be on or before submitted_at date
- sla_deadline must equal submitted_at + 604800 seconds (7 days), no rounding
- routing_confidence must be null if routing_decision is null or PENDING_CLASSIFICATION
- routing_confidence must be in [0.0, 1.0] if routing_decision is ADMINISTRATIVE or CLINICAL
- classification_result_id must be non-null when routing_decision is ADMINISTRATIVE or CLINICAL
- If current_state = CLINICAL_REVIEW_QUEUE: routing_decision must = CLINICAL
- billed_amount_cents must be > 0

Naming conventions:
- Table: claim_records
- Primary key: id (UUID)
- Enum values: SCREAMING_SNAKE_CASE
- Amount fields: suffix _cents, integer
- Date/time fields: suffix _at for timestamps, no suffix for dates
- Foreign key fields: [entity_name]_id
```

---

### Shared Entity: ClinicalClassificationResult

Output of the shared clinical content classifier (ADR-2). Produced by WS1 for routing (WS1-JtD-2); read by the Clinical Review Support Agent for routing verification (WS2-JtD-1). One record per classification call; a new record is created if the classifier is re-run.

```
Entity: ClinicalClassificationResult

Attributes:
- id: UUID, primary key, immutable, generated on creation
- claim_id: UUID, foreign key to ClaimRecord, required, immutable
- call_site: enum [WS1_ROUTING, WS2_VERIFICATION], required, immutable; identifies which
  agent produced this result
- model_version: string, max 50 characters, required, immutable; classifier model version string
- classification: enum [ADMINISTRATIVE, CLINICAL, UNCERTAIN], required
- confidence_score: float 0.0–1.0, required
- threshold_applied: float 0.0–1.0, required, immutable; value of
  CLINICAL_CONTENT_CONFIDENCE_THRESHOLD at time of classification
- threshold_met: boolean, required; true if confidence_score ≥ threshold_applied
- feature_snapshot: JSON object, required, immutable; the exact input values used for this
  classification: {diagnosis_codes: [...], procedure_codes: [...], provider_specialty: string or null}
- override_applied: boolean, required, default false
- override_by: UUID, optional; reference to human reviewer; required if override_applied = true
- override_reason: string, max 500 characters, optional; required if override_applied = true
- overridden_classification: enum [ADMINISTRATIVE, CLINICAL, UNCERTAIN], optional;
  required if override_applied = true
- created_at: ISO 8601 timestamp, UTC, set on creation, immutable
- updated_at: ISO 8601 timestamp, UTC, updated only when override is applied

Relationships:
- claim_id: UUID, foreign key to ClaimRecord, cardinality many-to-one (a claim may have
  multiple classification results across call sites), on delete: RESTRICT

State machine:
- Initial state: PENDING
- PENDING → CLASSIFIED: classifier inference completes and returns classification + confidence_score
- CLASSIFIED → OVERRIDDEN: human reviewer applies override (sets override_applied = true,
  override_by, override_reason, overridden_classification)
- Terminal states: CLASSIFIED (if no override applied), OVERRIDDEN

Invalid transitions:
- PENDING → OVERRIDDEN: FORBIDDEN — override requires a prior machine classification;
  a human cannot override a result that does not yet exist
- OVERRIDDEN → CLASSIFIED: FORBIDDEN — once a human override is recorded it cannot be removed;
  a new ClinicalClassificationResult must be created if a correction is needed
- CLASSIFIED → CLASSIFIED: FORBIDDEN — re-running the classifier on the same claim at the same
  call site creates a new ClinicalClassificationResult record, not an in-place update

Validation rules:
- confidence_score must be in [0.0, 1.0]
- threshold_applied must match the runtime value of CLINICAL_CONTENT_CONFIDENCE_THRESHOLD
  at the moment the classifier was invoked
- If override_applied = true: override_by, override_reason, overridden_classification must
  all be non-null
- If override_applied = false: override_by, override_reason, overridden_classification must
  all be null
- One WS1_ROUTING result and one WS2_VERIFICATION result are permitted per claim_id;
  a second WS1_ROUTING result for the same claim is only permitted if the first was OVERRIDDEN

Naming conventions:
- Table: clinical_classification_results
- Enum values: SCREAMING_SNAKE_CASE
```

---

### Shared Entity: HITLEscalation

Raised by either agent when a decision exceeds the agent's authority or confidence boundary. Read and resolved by a human reviewer. Both agents create HITLEscalation records; resolution feeds back into the claim state machine.

```
Entity: HITLEscalation

Attributes:
- id: UUID, primary key, immutable, generated on creation
- claim_id: UUID, foreign key to ClaimRecord, required, immutable
- escalation_type: enum [ELIGIBILITY_DISCREPANCY, CODING_PLAUSIBILITY, PRIOR_AUTH_PARTIAL_MATCH,
  CLASSIFICATION_BELOW_THRESHOLD, CONTRACT_EXCEPTION, DOCUMENTATION_INCOMPLETE,
  ROUTING_VERIFICATION_FAILED, AUDIT_RECORD_INCOMPLETE], required, immutable
- raised_by_agent: string, max 100 characters, agent instance identifier; required, immutable
- raised_at: ISO 8601 timestamp, UTC, required, immutable
- sla_response_deadline: ISO 8601 timestamp, UTC, required; raised_at + sla_minutes per
  escalation_type (see §7 escalation triggers in each per-agent spec); immutable
- assigned_to: UUID, optional; reference to human reviewer assigned to this escalation; null
  until assignment
- current_state: enum [OPEN, ASSIGNED, IN_REVIEW, RESOLVED, UNRESOLVABLE], required
- context_snapshot: JSON object, required, immutable; the claim fields and agent analysis
  relevant to this escalation at the moment it was raised
- resolution_action: enum [APPROVE, REJECT, OVERRIDE_TO_CLINICAL, OVERRIDE_TO_ADMINISTRATIVE,
  REQUEST_MORE_INFO, ESCALATE_FURTHER], optional; null until resolved
- resolution_notes: string, max 1000 characters, optional
- resolved_by: UUID, optional; reference to human reviewer; required when current_state = RESOLVED
- resolved_at: ISO 8601 timestamp, UTC, optional; required when current_state = RESOLVED
- created_at: ISO 8601 timestamp, UTC, set on creation, immutable
- updated_at: ISO 8601 timestamp, UTC, updated on every state transition

Relationships:
- claim_id: UUID, foreign key to ClaimRecord, cardinality many-to-one,
  on delete: RESTRICT

State machine:
- Initial state: OPEN
- OPEN → ASSIGNED: a human reviewer is assigned (assigned_to set, routing system action)
- ASSIGNED → IN_REVIEW: assigned reviewer opens the escalation record
- IN_REVIEW → RESOLVED: reviewer submits a resolution action (resolution_action, resolved_by,
  resolved_at set)
- IN_REVIEW → UNRESOLVABLE: reviewer determines the escalation cannot be resolved with
  available information (reviewer notes required)
- OPEN → UNRESOLVABLE: sla_response_deadline exceeded with no assignment; system-triggered
  timeout; triggers emergency escalation alert to supervisor
- Terminal states: RESOLVED, UNRESOLVABLE

Invalid transitions:
- RESOLVED → any state: FORBIDDEN — a resolved escalation is immutable; errors in the
  resolution outcome require opening a new HITLEscalation
- UNRESOLVABLE → RESOLVED: FORBIDDEN — unresolvable escalations cannot be retroactively
  resolved; a new escalation must be opened with additional context
- OPEN → IN_REVIEW: FORBIDDEN — reviewer must be formally assigned (ASSIGNED state) before
  review begins; unassigned review bypasses the assignment audit trail

Validation rules:
- If current_state = RESOLVED: resolved_by, resolved_at, and resolution_action must all be
  non-null
- If current_state in [OPEN, ASSIGNED, IN_REVIEW]: resolved_by, resolved_at, and
  resolution_action must all be null
- resolution_notes required (length > 0) if resolution_action in [REQUEST_MORE_INFO,
  ESCALATE_FURTHER, OVERRIDE_TO_CLINICAL, OVERRIDE_TO_ADMINISTRATIVE]
- sla_response_deadline must be strictly greater than raised_at

Naming conventions:
- Table: hitl_escalations
- Enum values: SCREAMING_SNAKE_CASE
```

---

### Shared Entity: PriorAuthRecord

An immutable point-in-time snapshot of prior authorization data retrieved from the external prior auth system. Read by WS1 during prior auth validation (MT-WS1-6, MT-WS1-7) and by the Clinical Review Support Agent during context assembly (MT-WS2-3). The external system is the source of truth; this record captures the state at time of retrieval for the audit trail.

```
Entity: PriorAuthRecord

Note: This is a read snapshot entity. It is immutable after creation. If a re-check is needed
(e.g., after provider supplies additional documentation), a new PriorAuthRecord is created.

Attributes:
- id: UUID, primary key, immutable, generated on creation
- claim_id: UUID, foreign key to ClaimRecord, required, immutable
- call_site: enum [WS1_VALIDATION, WS2_CONTEXT_ASSEMBLY], required, immutable
- external_auth_id: string, max 100 characters; the prior auth system's record identifier;
  null if auth_status is ABSENT, NOT_REQUIRED, or LOOKUP_FAILED
- auth_status: enum [PRESENT_EXACT_MATCH, PRESENT_PARTIAL_MATCH, PRESENT_EXPIRED,
  NOT_REQUIRED, ABSENT, LOOKUP_FAILED], required
- procedure_codes_authorised: array of strings; CPT/HCPCS format; empty array if auth_status
  is ABSENT, NOT_REQUIRED, or LOOKUP_FAILED
- authorised_units: integer, range 0–999; null if auth_status is ABSENT, NOT_REQUIRED,
  or LOOKUP_FAILED
- claimed_units: integer, range 1–999; required; units of service on the claim
- auth_start_date: ISO 8601 date; null if auth_status is ABSENT, NOT_REQUIRED, or LOOKUP_FAILED
- auth_end_date: ISO 8601 date; null if auth_status is ABSENT, NOT_REQUIRED, or LOOKUP_FAILED
- tolerance_flag: boolean, required; true if and only if auth_status = PRESENT_PARTIAL_MATCH
  AND partial_match_reason = UNIT_VARIANCE AND the variance is within PRIOR_AUTH_UNIT_TOLERANCE_PERCENT
- partial_match_reason: enum [UNIT_VARIANCE, DATE_VARIANCE, CODE_VARIANT]; null if auth_status
  is not PRESENT_PARTIAL_MATCH
- retrieved_at: ISO 8601 timestamp, UTC, required, immutable; time of API call to prior auth system
- created_at: ISO 8601 timestamp, UTC, set on creation, immutable

Relationships:
- claim_id: UUID, foreign key to ClaimRecord, cardinality many-to-one (multiple snapshots may
  exist for the same claim across different call sites or re-checks), on delete: RESTRICT

State machine:
- Initial state: SNAPSHOT_CREATED
- Terminal state: SNAPSHOT_CREATED (only state; entity is immutable after creation)

Invalid transitions:
- SNAPSHOT_CREATED → any other state: FORBIDDEN — immutable snapshot; no modifications
  permitted after creation
- Any field update after creation: FORBIDDEN — the snapshot preserves the exact state of the
  external system at retrieval time for audit integrity

Validation rules:
- If auth_status = PRESENT_PARTIAL_MATCH: partial_match_reason must be non-null
- If auth_status in [ABSENT, NOT_REQUIRED, LOOKUP_FAILED]: external_auth_id,
  procedure_codes_authorised (must be empty array), authorised_units, auth_start_date,
  auth_end_date, partial_match_reason must all be null (or empty array for procedure_codes_authorised)
- If tolerance_flag = true: auth_status must = PRESENT_PARTIAL_MATCH AND partial_match_reason
  must = UNIT_VARIANCE
- If auth_end_date is non-null and auth_start_date is non-null: auth_end_date must be on or
  after auth_start_date
- claimed_units must be ≥ 1

Naming conventions:
- Table: prior_auth_records
- Enum values: SCREAMING_SNAKE_CASE
```

---

### Shared Entity: AdjudicationDecision

The canonical output record of the adjudication pipeline, regardless of path. WS1 creates it for `AUTO_APPROVED` and `AUTO_REJECTED` outcomes. The Clinical Review Support Agent creates it when documenting the physician's `PHYSICIAN_APPROVED` or `PHYSICIAN_DENIED` decision (WS2 determination documentation). Referenced by `ClaimRecord.adjudication_decision_id`.

```
Entity: AdjudicationDecision

Attributes:
- id: UUID, primary key, immutable, generated on creation
- claim_id: UUID, foreign key to ClaimRecord, required, immutable
- decision_type: enum [AUTO_APPROVED, AUTO_REJECTED, PHYSICIAN_APPROVED, PHYSICIAN_DENIED],
  required, immutable
- decision_source: enum [WS1_AGENT, HITL_REVIEWER, PHYSICIAN], required, immutable;
  WS1_AGENT for auto-path decisions; HITL_REVIEWER for exception-queue approvals/rejections;
  PHYSICIAN for physician-signed determinations
- decided_by: UUID, required, immutable; agent instance ID if decision_source = WS1_AGENT;
  reviewer UUID if HITL_REVIEWER; physician UUID if PHYSICIAN
- decided_at: ISO 8601 timestamp, UTC, required, immutable
- payment_amount_cents: integer, USD cents, range 0–10,000,000; required if decision_type =
  AUTO_APPROVED or PHYSICIAN_APPROVED; null for rejected/denied decisions
- rejection_codes: array of strings, max 10 elements; each string max 20 characters; required
  if decision_type = AUTO_REJECTED or PHYSICIAN_DENIED; empty array otherwise
- rejection_reason_narrative: string, max 2000 characters; required if decision_type =
  PHYSICIAN_DENIED (regulatory content requirement per denial notice rules); optional for
  AUTO_REJECTED (coded reason sufficient)
- confidence_score_at_decision: float 0.0–1.0; the ClinicalClassificationResult.confidence_score
  that was active when this decision was made; null if decision_source = PHYSICIAN (not
  applicable to physician sign-off)
- audit_complete: boolean, required, default false; set to true when all required audit log
  entries for this decision have been confirmed written; a false value at query time signals
  an incomplete audit record
- created_at: ISO 8601 timestamp, UTC, set on creation, immutable
- updated_at: ISO 8601 timestamp, UTC; updated only when audit_complete transitions to true

Relationships:
- claim_id: UUID, foreign key to ClaimRecord, cardinality one-to-one (one decision per
  claim per lifecycle), on delete: RESTRICT

State machine:
- Initial state: PENDING
- PENDING → DECIDED: decision_type, decision_source, decided_by, decided_at are set;
  payment_amount_cents or rejection_codes set as applicable
- DECIDED → AUDIT_COMPLETE: all required audit log entries confirmed written
  (audit_complete set to true)
- Terminal states: AUDIT_COMPLETE

Invalid transitions:
- DECIDED → PENDING: FORBIDDEN — a recorded decision cannot be withdrawn; any reconsideration
  requires a new claim submission or appeal (new APP record)
- AUDIT_COMPLETE → DECIDED: FORBIDDEN — audit_complete is a one-way flag; an incomplete audit
  record after AUDIT_COMPLETE would require a separate audit remediation record
- PENDING → AUDIT_COMPLETE: FORBIDDEN — audit cannot complete before the decision is made

Validation rules:
- payment_amount_cents must be non-null if decision_type in [AUTO_APPROVED, PHYSICIAN_APPROVED]
- payment_amount_cents must be null if decision_type in [AUTO_REJECTED, PHYSICIAN_DENIED]
- rejection_codes must be non-empty array if decision_type in [AUTO_REJECTED, PHYSICIAN_DENIED]
- rejection_reason_narrative must be non-null and length > 0 if decision_type = PHYSICIAN_DENIED
- decided_by must match a valid agent instance ID if decision_source = WS1_AGENT
- One AdjudicationDecision record per claim_id; a second record is FORBIDDEN (enforce at
  database unique constraint on claim_id)

Naming conventions:
- Table: adjudication_decisions
- Enum values: SCREAMING_SNAKE_CASE
- Amount fields: suffix _cents, integer
```

---

## Preamble §3: Data and System Requirements

*Derived from the activity catalogs in D3 §2 (Agent 2 WS1 and Agent 3 Clinical Review Support) and the micro-task inventory in D2A §2d (WS1) and §3d (WS2). All system names are assumptions — no systems are named in scenario_context.md §6.*

### Input data

| Data element | Source | Consumer agent | Required latency | Notes |
|---|---|---|---|---|
| Canonical claim record (ClaimRecord) | Intake & Anomaly Agent output queue | WS1 | On-demand, event-triggered per claim | WS1 reads ClaimRecord in NORMALISED state; WS2 reads it in CLINICAL_REVIEW_QUEUE state |
| Member eligibility status (enrollment date, plan type, dependent status) | External member eligibility system | WS1 (MT-WS1-2, MT-WS1-3) | Real-time lookup per claim | Binary result for standard path; ambiguous result (data lag vs. genuine gap) requires HITL |
| Prior authorisation records (auth status, codes authorised, units, dates) | External prior auth system | WS1 (MT-WS1-6, MT-WS1-7), WS2 (MT-WS2-3) | On-demand retrieval per claim | Shared retrieval interface used by both agents per D2A §4 cross-work-stream observation 2 |
| Clinical documentation (physician notes, operative reports, clinical narratives) | Clinical notes source system | WS2 (MT-WS2-2) | On-demand retrieval per claim | Source system unknown (A-D0C-7); programmatic API access is a hard prerequisite for WS2 |
| Member prior claims history (for WS2 context assembly) | Claims management system | WS2 (MT-WS2-2) | On-demand retrieval per claim; last 12 months of claims for this member + diagnosis relevant to current claim | Depth and format of historical record unknown — assumption |

### Reference data

| Data element | Consumer agent | Format | Notes |
|---|---|---|---|
| ICD-10-CM diagnosis code reference + CPT/HCPCS procedure code reference + pairing rules | WS1 (MT-WS1-4) | Structured enumerated tables; pairing rules are rule-based lookup | Standard codes; commercial code reference databases available |
| Clinical plausibility knowledge base (known implausible diagnosis-procedure-specialty combinations) | WS1 (MT-WS1-5) | Not named in scenario; must be built from historical claims data or commercial code validation service | Tool Coverage L per D2A; requires training data or commercial pairing validation service |
| Fee schedule (procedure × provider × plan type payment rates) | WS1 (MT-WS1-9) | Structured rate tables; must be machine-readable | Source system unnamed; assumed structured |
| Contract exception rules (negotiated rates for carve-out procedures and specific providers) | WS1 (MT-WS1-10) | Currently unknown — assumed to reside in documents or email (A-D2A-5); must be encoded in structured accessible format before MT-WS1-10 standard path is possible | Tool Coverage L per D2A; encoding is a prerequisite for ADR-1 revisit condition |
| Clinical content criterion definition (formal specification of what constitutes "clinical content" for classifier training) | WS1 (WS1-JtD-2), WS2 (WS2-JtD-1) | Machine-encodable training specification; must be produced by Dr. Marcus Webb's CMO team | Not a system — a design output; no equivalent exists in the current process (scenario_context.md Assumption A-4); blocking prerequisite for both agents |
| CLINICAL_CONTENT_CONFIDENCE_THRESHOLD (configurable float, 0.0–1.0) | WS1, WS2 | Procedural configuration (system prompt / config file) | Certified by CMO team against labelled holdout set; value not set here — to be determined via calibration |
| PRIOR_AUTH_UNIT_TOLERANCE_PERCENT (configurable integer, 0–100) | WS1 (MT-WS1-7) | Procedural configuration | Tolerance threshold for partial match resolution; value is a design parameter requiring VP Operations alignment |
| Medical necessity criteria (InterQual, Milliman, or proprietary — A-D2A-9) | WS2 (MT-WS2-3, MT-WS2-4 context) | Text-extractable document sections; retrieval by procedure type + diagnosis code | Used for pre-filling context packet (not for determination); must be accessible for RAG indexing |

### Output targets

| Output | Target | Producer agent | Access type |
|---|---|---|---|
| AUTO_APPROVED decision record | Claims management / adjudication system | WS1 | Write |
| AUTO_REJECTED decision record with specific failure code | Claims management / adjudication system | WS1 | Write |
| Claim routed to clinical review queue | WS2 clinical intake queue | WS1 | Write (state transition trigger) |
| HITL escalation record (WS1 exceptions) | HITL exception queue / workflow system | WS1 | Write |
| Pre-filled clinical review packet | Physician review queue interface | WS2 | Write |
| HITL escalation record (WS2 exceptions — routing verification failed, documentation incomplete) | HITL exception queue / workflow system | WS2 | Write |
| Additional information request draft (physician-triggered) | Provider communication system | WS2 (drafts; physician or ops dispatches) | Write (draft) |
| Determination documentation (reason code, audit record) | Claims management / adjudication system | WS2 (documents the physician's decision) | Write |
| Audit log entry (every agent action) | Append-only audit log | WS1, WS2 | Write (append only) |

### Approval / governance channels

| Channel | Purpose | Required by |
|---|---|---|
| HITL reviewer sign-off system | Records human reviewer decision on escalated items with reviewer identity (UUID), timestamp, and resolution action; must be queryable for audit | Both agents; system-enforced vs. procedure-dependent to be assessed in D4-INT §6 |
| Physician sign-off capture | Records physician determination with physician identity (UUID), timestamp, reason code, and determination type; this is the URAC/NCQA compliance record | WS2 / Clinical Review Support Agent; system-enforced blocking gate required — physician sign-off must be captured before ClaimRecord transitions to PHYSICIAN_APPROVED or PHYSICIAN_DENIED |

> **Prerequisite note:** All system names in this section are assumptions — no systems are named in `scenario_context.md §6`. Full system inventory, gap analysis, and integration risk register are produced in `Deliverables/D4_integration_preamble.md`.

---

## Preamble §7: Context Engineering Design

### Memory architecture

| Memory type | Content | Storage mechanism | Lifecycle |
|-------------|---------|-------------------|-----------|
| In-context (short-term) | Current ClaimRecord (all fields); current check results (eligibility status, coding flags, PriorAuthRecord snapshot, ClinicalClassificationResult); current HITLEscalation state if active; current session error flags | Serialised JSON included in each agent prompt at claim processing time; max ~8KB per claim context | Single claim processing session; cleared when claim reaches a terminal state or is handed off to HITL or physician queue |
| Semantic (long-term, retrieval) | WS1: contract exception rules for fee schedule calculation (MT-WS1-10); clinical plausibility patterns (MT-WS1-5). WS2: medical necessity criteria sections keyed by procedure type and diagnosis category (MT-WS2-3) | Vector store with chunked documents; retrieval by composite key (procedure_code + diagnosis_code category + provider_specialty where relevant) | Updated when source documents are revised; TTL aligned to document version cycle (quarterly minimum or on document change); stale document detection is a pre-deployment checklist item |
| Procedural (static instructions) | Adjudication workflow rules (eligibility decision logic, code pairing validation rules, prior auth tolerance thresholds); escalation trigger definitions; CLINICAL_CONTENT_CONFIDENCE_THRESHOLD; PRIOR_AUTH_UNIT_TOLERANCE_PERCENT; compliance constraints (URAC/NCQA physician sign-off requirement); autonomy matrix tier assignments | System prompt / agent configuration loaded at agent startup; version-controlled | Updated only when rules change; changes require ops team approval, version increment, and re-deployment; prior version retained for audit of claims processed under previous configuration |

### Retrieval strategy

**What triggers a retrieval call:**

| Trigger | Task | Retrieval target | Retrieval type |
|---------|------|-----------------|----------------|
| ICD-10 + CPT pair passes formal crosswalk but plausibility is questionable | MT-WS1-5 (coding plausibility assessment) | Known implausible combination patterns for this diagnosis-procedure-specialty class; top-3 matches | Semantic similarity (vector store) |
| Fee schedule lookup returns no standard rate for this provider-procedure combination | MT-WS1-10 (contract exception handling) | Exact contract exception rule for this provider_id + procedure_code + payer_id combination | Exact match (structured lookup; not semantic) |
| Clinical Review Support Agent begins context assembly for WS2-JtD-2 | MT-WS2-3 (medical necessity criteria assembly) | Medical necessity criteria sections relevant to this procedure type and primary diagnosis category; top-3 sections by relevance | Semantic similarity (vector store, chunked by procedure type) |
| WS1 clinical content classification (MT-WS1-8 / WS1-JtD-2) | WS1-JtD-2 (routing classification) | Classifier inference call — not a retrieval; separate model inference endpoint returning (classification, confidence_score) | Model inference call (not vector retrieval) |

**Retrieval target precision rules:**
- Eligibility, prior auth, and claims history lookups: **exact structured record retrieval** — no semantic similarity; wrong record is a compliance violation, not a retrieval quality issue
- Contract exception rules: **exact match by composite key** — semantic similarity is unacceptable; an incorrect rate is a financial error with no visible detection signal until contract reconciliation
- Medical necessity criteria: **semantic top-K (K=3)** — acceptable because the physician reviews the assembled packet; false-positive retrieved sections waste physician attention but do not cause a compliance violation; false-negative sections (missing a critical criteria section) are detectable by the physician's "insufficient packet" flag

**Retrieval quality evaluation:**
- Clinical content classifier recall is the primary quality gate. Calibration method: labelled holdout set of ≥500 claims reviewed by CMO clinical team (not model self-reported confidence). CLINICAL_CONTENT_CONFIDENCE_THRESHOLD is set to achieve ≥99.5% recall (false negative rate ≤0.5%) on the holdout set before any production routing. This threshold cannot be set from model training outputs alone.
- Medical necessity criteria retrieval quality: monitored post-deployment by physician packet quality flags. If ≥10% of assembled packets in a 30-day window are flagged by physicians as missing key context sections, retrieval configuration (chunk size, index structure, K value) requires tuning before the next billing cycle.
- Contract exception retrieval quality: audited monthly against contract reconciliation data. If any AUTO_APPROVED payment is found to have applied an incorrect rate due to a missed or mismatched exception rule, the exception rules store is reviewed and corrected before the next batch run.

**Retrieval cost management:**
- In-context claim record is capped at ~8KB structured JSON (ClaimRecord + current check results). This keeps WS1 processing within a single context window per claim without truncation.
- Medical necessity criteria RAG index is chunked by procedure type category, not by individual criteria section, to limit the retrieval surface area and reduce top-K false positives.
- The clinical content classifier is called as a separate inference service (not embedded in the main agent prompt). Fee schedule and eligibility lookups are deterministic tool calls that incur no LLM inference cost.
- Semantic retrieval calls (plausibility patterns, criteria sections) are cached per (procedure_code, diagnosis_code) composite key with a 24-hour TTL to avoid redundant vector store calls for common claim types.

### Pre-deployment prerequisite checklist

| Item | What must be confirmed | Confirmed by | If unconfirmed |
|------|----------------------|--------------|----------------|
| Fee schedule format | All provider-procedure-plan rate combinations in scope are machine-readable (structured tables, API-accessible); no rates exist only in spreadsheets or email | VP Operations (James Liu) | WS1 MT-WS1-9 payment calculation cannot proceed on standard path; all payment determinations fall to HITL |
| Contract exception rules encoding | All contract carve-outs for in-scope providers and payers are encoded in a structured, API-accessible format; no exception rules exist only in documents or email | VP Operations (James Liu) + Finance team | ADR-1 revisit condition is not met; WS1-JtD-3 exception path remains HITL-only |
| Medical necessity criteria format | Medical necessity criteria document is text-extractable (not scan/image-based); all sections relevant to in-scope procedure types are available for RAG indexing | Dr. Marcus Webb (CMO) | WS2 pre-filled packets cannot include criteria mapping; physicians receive claim context without criteria reference (degrades packet quality; does not block WS2) |
| Adjudication system API write access | API write access confirmed for: claim state transitions, AUTO_APPROVED and AUTO_REJECTED decision records, audit log append, custom fields required by agent design | VP Operations (James Liu) + IT Security | WS1 agent cannot write decisions; entire pipeline is blocked at this step |
| Inbound trigger mechanism | WS1 agent intake trigger (event queue, polling interval, or webhook from Intake & Anomaly Agent) confirmed and IT security-approved | IT Security | Agent cannot begin processing; Intake Agent output has no consumer |
| HITL sign-off audit trail | HITL reviewer decisions are logged with reviewer identity (UUID), timestamp, and resolution action in a queryable system | VP Operations (James Liu) | HITL decisions are unauditable; compliance record is incomplete |
| Clinical content confidence threshold certification | CLINICAL_CONTENT_CONFIDENCE_THRESHOLD value is validated against a CMO-labelled holdout set of ≥500 claims; threshold achieves ≥99.5% recall; value is documented in a signed configuration artefact co-signed by Dr. Marcus Webb | CMO (Dr. Marcus Webb) | WS1 clinical content routing (WS1-JtD-2) cannot go live; the administrative/clinical routing split is not implemented |
| Physician sign-off system — system-enforced enforcement | Physician approval is recorded by a system-enforced workflow state transition (not a procedural agreement); claims in IN_PHYSICIAN_REVIEW state are technically blocked from transitioning to a terminal state without a recorded physician sign-off token | IT Security + CMO (Dr. Marcus Webb) | URAC/NCQA compliance cannot be architecturally guaranteed; physician sign-off becomes procedure-dependent (governance risk — see D4-INT §6) |
| Clinical notes API access (WS2-specific) | Programmatic API access to clinical notes source system (lookup by member_id + service_date + provider_id) is technically feasible; HIPAA/BAA data access agreement is in place | IT Security + Legal/Compliance | Clinical Review Support Agent (WS2) cannot retrieve clinical documentation; WS2-JtD-2 reverts to Human-led + Agent Support; WS2 economic case degrades significantly |

---

*End of Preamble. Pass 2 produces Spec A (WS1 Administrative Adjudication Agent), §0–§8 + §10–§11 + §14.*
