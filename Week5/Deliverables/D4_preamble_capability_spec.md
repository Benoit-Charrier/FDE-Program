# D4 — Capability Specification Preamble
## Greenfield Health Systems: Medical Claims Adjudication Transformation

*Source inputs: `Deliverables/D3_agentic_solution_architecture.md`, `Deliverables/D4_agent_purpose_document.md`, `Deliverables/D2A_cognitive_load_map.md`, `Deliverables/D2B_delegation_suitability_matrix.md`, `Deliverables/D2C_volume_value_analysis.md`, `Scenario/scenario_context.md`. Every design decision traces to one of these inputs or is flagged as an assumption.*

---

## §1. Agent Selection

### Selected agents

**Agent A: WS1 Administrative Adjudication Agent**

Selected as Spec A because:
- Highest D2C Wave 1 priority: covers ~1,300 claims/day (65% of total volume) and directly targets the 5.7× daily capacity deficit that produces active SLA penalties (D3 §0, scenario_context.md Exchange 3).
- Covers the three JtDs with the strongest case for Wave 1 production deployment: WS1-JtD-1 (administrative validation, D2B score 1/7 under Agent-led + Human Oversight), WS1-JtD-2 (clinical content routing — the AI-native moment in the architecture), and WS1-JtD-3 (payment determination, D2B score 4/7 — strongest suitability in the primary pipeline).
- Named as primary agentic target in D3 §0 Executive Summary.
- D3 ADR-3 confirms WS1 is designed as a single orchestrating agent — a single capability spec is architecturally coherent.
- D3 autonomy matrix rows: EDI parsing, duplicate detection, eligibility lookup, code validity, prior auth lookup, fee schedule calculation, clinical flag verification (high-confidence), payment approval (standard claim), and multiple AGENT PROPOSES rows — 15 of 29 autonomy matrix rows belong to this agent.

**Agent B: WS2 Clinical Review Support Agent**

Selected as Spec B because:
- WS2 is the direct downstream recipient of WS1's clinical routing output; the two agents share the clinical content classifier component (D3 ADR-2) and operate on the same ClaimRecord entity in sequence — specifying both in this deliverable enables cross-spec consistency checks on shared entity definitions and the shared classifier's confidence threshold design.
- WS2-JtD-1 (clinical content flag verification) is a structural URAC/NCQA compliance gate: without it, claims entering the clinical path proceed to physician review without a second-pass classifier check, increasing false-negative exposure from WS1's routing call. D3 autonomy matrix places this step at "Agent decides alone" for high-confidence cases.
- WS2-JtD-2 (clinical context assembly) is a Wave 2 build conditional on clinical notes source system API availability; specifying it now ensures the capability design is ready when the API prerequisite is resolved (D3 §5).
- D3 autonomy matrix includes WS2 actions in 4 of 29 rows — clinical flag verification (high-confidence), clinical flag verification (below threshold), documentation retrieval (complete), and pre-filled packet delivery — confirming it is a designed agentic component, not inferred.

### Deferred agents

| Agent | Deferral reason |
|-------|----------------|
| **Intake & Anomaly Agent** | Wave 1 infrastructure prerequisite, not a primary capability spec target. Both JtDs (INT-JtD-1, INT-JtD-2) are Fully Agentic with D2B scores 3/7 and 5/7; no HITL gates, no clinical compliance dimension, no confidence threshold design problem. D2C Wave 1 positions this agent as prerequisite infrastructure (normalised claim records are input to WS1), not the primary agentic transformation target. A capability spec adds minimal design value for this deliverable. |
| **Queue & SLA Management Agent** | Fully Agentic on both JtDs (QMG-JtD-1 and QMG-JtD-2, D2B scores 5/7 each). No HITL gates, no compliance constraints, no confidence threshold. Both JtDs are state-machine-driven by deterministic contractual rules (7-day SLA threshold). A capability spec here would add breadth but not depth to the engagement design. |
| **Appeals Support Agent** | Wave 3 deferral from D3 — build explicitly blocked until WS1 produces steady-state quality data and the residual appeal volume and root-cause distribution are measurable (D3 §5, APP-JtD-1/APP-JtD-2). Specifying it before WS1 is in production requires specifying against an unknown claim population. D3 governance constraint: Wave 3 build must not begin until 90 days post-WS1 go-live. |

---

## §2. Shared Entity Definitions

*All entities used by more than one agent are defined here at Tier 3 standard. Per-agent specs reference these by name — they do not redefine them.*

---

```
Entity: ClaimRecord
Scope: SHARED — used by WS1 (read, update), WS2 (read, update), Queue & SLA Management Agent
       (read, update), and Intake & Anomaly Agent (create, update)

Attributes:
- id: UUID, primary key, immutable, generated on creation
- external_claim_id: string, max 64 characters, optional, provider-assigned identifier,
  mutable until state = ADMIN_VALIDATING, immutable thereafter
- submission_format: enum [EDI_837P, EDI_837I, PORTAL_FORM, FHIR_R4, CMS1500_PDF, EMAIL_EML, FAX_PDF, EXCEPTION_NOTES_PDF], required, immutable after creation
- member_id: string, max 32 characters, required, set on creation, immutable
- provider_npi: string, max 32 characters, required, set on creation, immutable
- provider_specialty: string, max 128 characters, required, set on creation, immutable
- date_of_service: ISO 8601 date (not timestamp), required, immutable
- diagnosis_codes: array of strings (ICD-10 format: letter + 2–7 alphanumeric characters),
  required, min 1 element, immutable after state = ADMIN_VALIDATING
- procedure_codes: array of strings (CPT format: 5-digit numeric), required, min 1 element,
  immutable after state = ADMIN_VALIDATING
- procedure_quantities: array of integers, required, min 1 element, position-aligned with
  procedure_codes (procedure_quantities[i] is the claimed unit count for procedure_codes[i]);
  each value must be ≥ 1; array length must equal procedure_codes array length;
  immutable after state = ADMIN_VALIDATING; used by T-07 (prior auth tolerance arithmetic)
  and required in AuditLogEntry.output_summary for tolerance-approved claims (REQ-A-7)
- modifier_codes: array of strings, optional, max 10 elements,
  immutable after state = ADMIN_VALIDATING
- billed_amount: decimal, USD, range 0.01–999999.99, required, immutable
- state: enum [RECEIVED, PARSING, PARSE_FAILED, NORMALISED, ADMIN_VALIDATING, ROUTING,
  ADMIN_CLEARED, PAYMENT_CALCULATING, PENDING_PHYSICIAN_REVIEW, CLINICAL_PACKET_ASSEMBLY,
  PENDING_ADDITIONAL_INFO, PHYSICIAN_REVIEWING, PENDING_HITL_EXCEPTION, APPROVED,
  REJECTED, CLOSED], required, mutable
- payment_amount: decimal, USD, range 0.01–999999.99, optional, null unless state = APPROVED
- rejection_codes: array of strings, optional, null unless state = REJECTED;
  each value must be from the validated rejection code reference set
- clinical_classification_id: UUID, optional, null until T-08 (WS1) executes;
  foreign key to ClinicalClassificationResult
- clinical_classification_id_ws2: UUID, optional, null until T-B-02 (WS2) executes;
  foreign key to ClinicalClassificationResult (call_site = VERIFICATION)
- hitl_queue_type: enum [PHYSICIAN_REVIEW, EXCEPTION_PROCESSOR, ROUTING_REVIEW],
  optional, null unless state ∈ {PENDING_PHYSICIAN_REVIEW, PENDING_HITL_EXCEPTION}
- hitl_assigned_to: UUID, optional, null unless claim is in HITL state;
  foreign key to reviewer record
- hitl_disposition: string, max 512 characters, optional, null until HITL reviewer records
  resolution
- sla_deadline: ISO 8601 timestamp, UTC, required, set on creation as
  created_at + 604800 seconds (exactly 7 days), immutable
- sla_breach_flag: boolean, default false; set to true when current timestamp
  exceeds sla_deadline − 172800 seconds (48 hours)
- created_at: ISO 8601 timestamp, UTC, set on creation, immutable
- updated_at: ISO 8601 timestamp, UTC, updated on any modification
- created_by: UUID, agent instance ID or system identifier, immutable
- updated_by: UUID, agent instance ID or human reviewer ID who last modified it

Relationships:
- clinical_classification_id: UUID, foreign key to ClinicalClassificationResult,
  optional/1:1, on delete: set null
- clinical_classification_id_ws2: UUID, foreign key to ClinicalClassificationResult,
  optional/1:1, null until WS2 T-B-02 executes; on delete: set null
- audit_entries: 1:many via AuditLogEntry.entity_id, on delete: restrict
  (audit entries must be archived before any claim record deletion;
  claim record deletion is not permitted in normal production operations)
- escalation_packets: 1:many via EscalationPacket.claim_id, on delete: restrict

State machine:
- Initial state: RECEIVED

- RECEIVED → PARSING: Intake Agent begins format extraction
- PARSING → PARSE_FAILED: format cannot be extracted; required fields absent after all
  extraction attempts exhausted
- PARSING → NORMALISED: all required fields extracted and schema-validated
- NORMALISED → ADMIN_VALIDATING: WS1 agent picks up claim from normalised queue
- ADMIN_VALIDATING → ROUTING: T-01 through T-07 complete; eligibility confirmed, all codes
  valid, prior auth confirmed or within PRIOR_AUTH_UNIT_TOLERANCE_PCT
- ADMIN_VALIDATING → PENDING_HITL_EXCEPTION: any of ET-03 (eligibility), ET-04 (prior auth),
  ET-05 (coding plausibility), ET-07 (audit failure) fires and cannot be auto-resolved
- ROUTING → ADMIN_CLEARED: clinical content classifier (T-08) returns ADMIN with
  confidence_score ≥ CLINICAL_CONTENT_CONFIDENCE_THRESHOLD
- ROUTING → PENDING_PHYSICIAN_REVIEW: classifier returns CLINICAL or UNCERTAIN at any
  confidence level (ET-01), OR returns ADMIN with confidence_score <
  CLINICAL_CONTENT_CONFIDENCE_THRESHOLD (ET-02)
- ADMIN_CLEARED → PAYMENT_CALCULATING: no contract exception flag; T-09 begins
- ADMIN_CLEARED → PENDING_HITL_EXCEPTION: contract exception flag triggered during T-10 (ET-06)
- PAYMENT_CALCULATING → APPROVED: payment amount calculated within confirmed fee schedule
  and contract terms
- PAYMENT_CALCULATING → PENDING_HITL_EXCEPTION: payment calculation anomaly (contract
  exception references a clause outside the pre-validated reference set)
- PENDING_PHYSICIAN_REVIEW → CLINICAL_PACKET_ASSEMBLY: WS2 agent picks up claim;
  routing verification classification meets WS2 confidence threshold
- PENDING_PHYSICIAN_REVIEW → PENDING_HITL_EXCEPTION: WS2 routing verification confidence
  below threshold (BP-WS2-1)
- CLINICAL_PACKET_ASSEMBLY → PHYSICIAN_REVIEWING: pre-filled review packet assembled and
  delivered to physician HITL queue
- CLINICAL_PACKET_ASSEMBLY → PENDING_ADDITIONAL_INFO: required clinical documentation not
  retrievable (BP-WS2-2)
- PHYSICIAN_REVIEWING → APPROVED: physician records approval token with payment determination
- PHYSICIAN_REVIEWING → REJECTED: physician records denial determination with reason code(s)
- PHYSICIAN_REVIEWING → PENDING_ADDITIONAL_INFO: physician flags assembled packet as
  insufficient; WS2 drafts additional information request
- PENDING_ADDITIONAL_INFO → CLINICAL_PACKET_ASSEMBLY: provider supplies missing
  documentation; WS2 re-triggers assembly from CLINICAL_PACKET_ASSEMBLY state
- PENDING_HITL_EXCEPTION → ADMIN_VALIDATING: HITL exception processor resolves and returns
  claim to validation pipeline
- PENDING_HITL_EXCEPTION → ROUTING: HITL processor resolves routing question
- PENDING_HITL_EXCEPTION → PAYMENT_CALCULATING: HITL processor approves exception;
  payment calculation proceeds
- PENDING_HITL_EXCEPTION → REJECTED: HITL processor issues denial
- APPROVED → CLOSED: payment confirmation received from payment processing system
- REJECTED → CLOSED: rejection notice confirmed delivered to provider
- Terminal states: PARSE_FAILED, CLOSED — no valid exit

Invalid transitions (at least 3):
- ADMIN_CLEARED → PHYSICIAN_REVIEWING: FORBIDDEN — a claim classified as admin must not
  enter the physician review path without re-routing via ROUTING state; bypassing this
  transition is a URAC/NCQA compliance event
- PENDING_PHYSICIAN_REVIEW → APPROVED: FORBIDDEN — T-09 (payment calculation) is
  architecturally blocked from executing against claims in PENDING_PHYSICIAN_REVIEW state;
  this is a system-enforced constraint, not procedure-dependent (D4a §8)
- APPROVED → PAYMENT_CALCULATING: FORBIDDEN — APPROVED is a terminal state; no
  re-adjudication from this state; corrections require a new claim submission
- REJECTED → APPROVED: FORBIDDEN — REJECTED is a terminal state; re-determination requires
  new claim submission
- CLOSED → any state: FORBIDDEN — CLOSED is terminal; no valid exit under any condition

Validation rules:
- date_of_service must be ≤ created_at date (claim cannot be for future service)
- billed_amount > 0.00; null is never valid
- diagnosis_codes array must have ≥ 1 element matching ICD-10 format at state ≥ ADMIN_VALIDATING
- procedure_codes array must have ≥ 1 element matching CPT format (5-digit numeric) at
  state ≥ ADMIN_VALIDATING
- payment_amount must be null unless state = APPROVED; must be > 0.00 when non-null
- rejection_codes must be null unless state = REJECTED; all values must be in the validated
  rejection code reference set when non-null
- sla_deadline = created_at + exactly 604800 seconds (no rounding)
- hitl_queue_type must be non-null if and only if state ∈ {PENDING_PHYSICIAN_REVIEW,
  PENDING_HITL_EXCEPTION}

Naming conventions:
- Table name: claim_records (snake_case, plural)
- Primary key column: id (not claim_id)
- Foreign key columns: {entity}_id pattern (e.g., clinical_classification_id)
- Enum values: SCREAMING_SNAKE_CASE
- Array fields: stored as JSON arrays; validated at application layer against type rules
- Timestamps: ISO 8601 with timezone (UTC stored; display timezone per UI layer)
```

---

```
Entity: ClinicalClassificationResult
Scope: SHARED — produced by the shared clinical content classifier when called by WS1
       (call_site = ROUTING) and by WS2 (call_site = VERIFICATION); read by both agents
       and by the audit/governance system

Attributes:
- id: UUID, primary key, immutable, generated on creation
- claim_id: UUID, required, immutable, foreign key to ClaimRecord
- call_site: enum [ROUTING, VERIFICATION], required, immutable —
  ROUTING = called by WS1 T-08; VERIFICATION = called by WS2 JtD-1
- classification: enum [ADMIN, CLINICAL, UNCERTAIN], required, immutable —
  set when state transitions to CLASSIFIED
- confidence_score: float, range 0.000–1.000 (three decimal places), required, immutable —
  the classifier's output confidence for the assigned classification value
- threshold_applied: float, range 0.000–1.000, required, immutable —
  the value of CLINICAL_CONTENT_CONFIDENCE_THRESHOLD at the time of this call
- threshold_met: boolean, required, immutable, computed —
  true if confidence_score ≥ threshold_applied; false otherwise; must not be manually set
- signal_diagnosis_codes: array of strings, required, immutable —
  the diagnosis codes provided as classifier input
- signal_procedure_codes: array of strings, required, immutable —
  the procedure codes provided as classifier input
- signal_provider_specialty: string, max 128 characters, required, immutable —
  the provider specialty provided as classifier input
- reasoning_chain: string, max 4096 characters, required, immutable —
  the classifier's reasoning output in structured text; minimum 20 characters;
  required for audit defence; null is never valid when state = CLASSIFIED
- classifier_version: string, max 64 characters, required, immutable —
  version identifier of the classifier model and system prompt used
- calibration_record_id: UUID, required, immutable —
  foreign key to the signed calibration artefact used to set threshold_applied;
  must reference a CalibrationRecord with CMO sign-off date non-null before go-live
- state: enum [PENDING, CLASSIFIED, SUPERSEDED, ARCHIVED], required, mutable
- superseded_by: UUID, optional, null unless state = SUPERSEDED;
  foreign key to the ClinicalClassificationResult that supersedes this one
- created_at: ISO 8601 timestamp, UTC, immutable
- updated_at: ISO 8601 timestamp, UTC, updated on any modification
- created_by: UUID, agent instance ID, immutable

Relationships:
- claim_id: UUID, foreign key to ClaimRecord, required, many:1 (one claim may have multiple
  classification results — one per call_site), on delete: restrict
- superseded_by: UUID, foreign key to ClinicalClassificationResult, optional, 1:1,
  on delete: set null
- calibration_record_id: UUID, foreign key to CalibrationRecord, required, on delete: restrict

State machine:
- Initial state: PENDING

- PENDING → CLASSIFIED: classifier returns result with confidence_score and reasoning_chain;
  all required fields populated
- CLASSIFIED → SUPERSEDED: a subsequent classification call on the same claim_id (different
  call_site, or a recalibration re-run) produces a new ClinicalClassificationResult; the earlier
  result is SUPERSEDED and superseded_by is set to the new record's id
- CLASSIFIED → ARCHIVED: retention period has elapsed per compliance retention schedule
- SUPERSEDED → ARCHIVED: retention period has elapsed
- Terminal states: ARCHIVED — no valid exit (archived records are read-only, immutable)

Invalid transitions:
- CLASSIFIED → PENDING: FORBIDDEN — a completed classification cannot be undone; if the
  classification is wrong, the claim is re-routed via a new ClinicalClassificationResult record
- ARCHIVED → CLASSIFIED: FORBIDDEN — archived results cannot be reactivated
- SUPERSEDED → CLASSIFIED: FORBIDDEN — a superseded result cannot revert to active;
  the superseding record is the current authoritative classification

Validation rules:
- confidence_score must be in range [0.000, 1.000] inclusive; null is never valid
- threshold_met must equal (confidence_score ≥ threshold_applied) — this is a computed
  field; any record where this equation does not hold is a data integrity violation
- reasoning_chain must be non-null and non-empty (≥ 20 characters) when state = CLASSIFIED
- calibration_record_id must reference a CalibrationRecord with CMO sign-off date non-null
  before the first production classification
- call_site = ROUTING requires ClaimRecord.state = ROUTING at time of creation
- call_site = VERIFICATION requires ClaimRecord.state = CLINICAL_PACKET_ASSEMBLY at time
  of creation

Naming conventions:
- Table name: clinical_classification_results (snake_case, plural)
- Primary key: id
- Enum values: SCREAMING_SNAKE_CASE
- call_site enum values are identical across both specs: ROUTING and VERIFICATION —
  no aliases permitted in either D4a or D4b
```

---

```
Entity: AuditLogEntry
Scope: SHARED — every agent action that transitions claim state, produces a classification,
       triggers escalation, or issues a determination must produce one record; read by
       compliance, governance, and audit systems

Attributes:
- id: UUID, primary key, immutable, generated on creation
- timestamp: ISO 8601 timestamp, UTC, millisecond precision, immutable, set on creation
- agent_id: string, max 64 characters, required, immutable —
  identifier of the agent instance producing this entry (format: {agent_name}:{version}:{instance_id})
- action: string, max 64 characters, required, immutable —
  representative base values: CLAIM_STATE_TRANSITION, CLASSIFICATION_COMPLETED,
  ESCALATION_TRIGGERED, PAYMENT_CALCULATED, PAYMENT_APPROVED, CLAIM_REJECTED,
  HITL_EXCEPTION_RAISED, HITL_RESOLVED, AUDIT_RECORD_COMMITTED,
  ADDITIONAL_INFO_REQUESTED, PACKET_DELIVERED, REFERENCE_DATA_MISS;
  complete per-agent value sets are defined in D4a §13 (WS1) and D4b §13 (WS2) —
  those per-spec enums are authoritative; no value outside the applicable per-spec
  §13 enum is valid for that agent's audit records
- entity_type: string, max 64 characters, required, immutable —
  identifies the entity this entry records an action on
  (e.g., "ClaimRecord", "ClinicalClassificationResult")
- entity_id: UUID, required, immutable —
  foreign key to the entity identified in entity_type
- input_summary: JSON object, required, immutable —
  key input fields used to make the decision; must include at minimum: entity_id of the
  primary entity, state of that entity before the action, and the specific trigger condition
  that caused this action
- output_summary: JSON object, required, immutable —
  what changed; must include at minimum: previous state, new state, and the primary output
  value (e.g., payment_amount for PAYMENT_APPROVED, classification for CLASSIFICATION_COMPLETED)
- delegation_tier: enum [AGENT_ALONE, AGENT_LOGS, AGENT_PROPOSES, HUMAN_DECIDES],
  required, immutable
- human_id: UUID, optional, null if no human was involved —
  required (non-null) when delegation_tier ∈ {HUMAN_DECIDES, AGENT_PROPOSES}
- confidence_score: float 0.000–1.000, optional, null for non-LLM actions —
  required when action ∈ {CLASSIFICATION_COMPLETED} or when escalation_trigger_id ∈
  {ET-01, ET-02, BP-WS2-1}
- escalation_triggered: boolean, required, default false
- escalation_trigger_id: string, max 16 characters, optional, null unless
  escalation_triggered = true; must match a defined trigger ID from the agent spec escalation
  table (ET-01 through ET-07 for WS1; BP-WS2-1 or BP-WS2-2 for WS2)
- compliance_flags: array of strings, required, default [] —
  each value is a string identifier from the compliance flag reference set
  (e.g., "URAC_NCQA_CLINICAL_GATE", "SLA_BREACH_IMMINENT", "AUDIT_TRAIL_COMPLETE")
- state: enum [PENDING_WRITE, COMMITTED, ARCHIVED], required, mutable
- created_at: ISO 8601 timestamp, UTC, immutable (same value as timestamp;
  separate field for query optimisation)
- created_by: UUID, agent instance ID, immutable

Relationships:
- entity_id: polymorphic foreign key; entity type identified by entity_type field;
  on delete: restrict — audit entries must be archived before any referenced entity deletion;
  entity deletion is not permitted in normal production operations

State machine:
- Initial state: PENDING_WRITE

- PENDING_WRITE → COMMITTED: all required fields validated; record written to append-only
  audit store; no field values may change after this transition
- COMMITTED → ARCHIVED: retention period for this log type has elapsed per the compliance
  retention schedule (see §13 of per-agent specs)
- Terminal states: ARCHIVED — no valid exit (archived log entries are read-only, immutable)

Invalid transitions:
- COMMITTED → PENDING_WRITE: FORBIDDEN — committed audit entries are immutable;
  any modification attempt is a compliance violation requiring a new AuditLogEntry record
  documenting the correction
- ARCHIVED → COMMITTED: FORBIDDEN — archived entries cannot be restored to active status
- PENDING_WRITE → ARCHIVED: FORBIDDEN — an uncommitted entry cannot be archived;
  skipping COMMITTED creates a gap in the audit trail

Validation rules:
- input_summary must include at minimum: entity_id, entity_type, and the pre-action state
  of the primary entity
- output_summary must include at minimum: the post-action state and the primary output
  value relevant to the action enum
- confidence_score must be non-null for action = CLASSIFICATION_COMPLETED or when
  escalation_trigger_id ∈ {ET-01, ET-02, BP-WS2-1}
- human_id must be non-null when delegation_tier ∈ {HUMAN_DECIDES, AGENT_PROPOSES}
- compliance_flags must include "URAC_NCQA_CLINICAL_GATE" when action =
  CLAIM_STATE_TRANSITION and output_summary.new_state = PENDING_PHYSICIAN_REVIEW
- escalation_trigger_id must be non-null when escalation_triggered = true

Naming conventions:
- Table name: audit_log_entries (snake_case, plural)
- Primary key: id
- Enum values: SCREAMING_SNAKE_CASE
- JSON object fields (input_summary, output_summary): snake_case keys;
  no camelCase transformation in stored records
```

---

```
Entity: EscalationPacket
Scope: SHARED — produced by WS1 on any of ET-01 through ET-07 and by WS2 on BP-WS2-1 or
       BP-WS2-2; read by HITL exception processors, physician reviewers, and audit system

Attributes:
- id: UUID, primary key, immutable, generated on creation
- claim_id: UUID, required, immutable, foreign key to ClaimRecord
- escalation_trigger_id: string, max 16 characters, required, immutable —
  must exactly match a defined trigger ID (ET-01 through ET-07 for WS1;
  BP-WS2-1 or BP-WS2-2 for WS2); no freeform values
- routing_queue: enum [PHYSICIAN_HITL, EXCEPTION_PROCESSOR, ROUTING_REVIEW,
  CONTRACT_OWNER, CODING_SPECIALIST], required, immutable
- producing_agent: enum [WS1_ADMINISTRATIVE_ADJUDICATION, WS2_CLINICAL_REVIEW_SUPPORT],
  required, immutable
- trigger_type: enum [ELIGIBILITY_DISCREPANCY, PRIOR_AUTH_MISMATCH,
  CODING_PLAUSIBILITY, CLINICAL_ROUTING, CONTRACT_EXCEPTION, AUDIT_FAILURE,
  GOVERNANCE_VIOLATION, DOCUMENTATION_MISSING, ROUTING_VERIFICATION_BELOW_THRESHOLD,
  ROUTING_VERIFICATION_CONFLICT, HITL_SLA_BREACH],
  required, immutable
- trigger_signal_values: JSON object, required, immutable —
  the specific numeric or enumerated values that caused the trigger condition;
  all values must be machine-parseable JSON (no free-text descriptions);
  minimum required fields depend on trigger_type (see per-agent §7 escalation tables)
- pipeline_state_at_escalation: JSON object, required, immutable —
  snapshot of all pipeline step outputs completed before escalation was triggered
- classification_result_id: UUID, optional, null unless trigger_type ∈
  {CLINICAL_ROUTING, ROUTING_VERIFICATION_BELOW_THRESHOLD};
  foreign key to ClinicalClassificationResult
- required_resolution: string, max 512 characters, required, immutable —
  the specific question the HITL reviewer must answer; must be a yes/no or
  choose-from-enumerated-options question; open-ended questions are not valid
- response_sla_hours: integer, values: 1, 2, or 4 only (set by escalation trigger table
  in per-agent specs; no other value is valid), required, immutable
- sla_deadline: ISO 8601 timestamp, UTC, required, immutable —
  created_at + (response_sla_hours × 3600) seconds
- state: enum [DELIVERED, ACKNOWLEDGED, RESOLVED, SLA_BREACHED, CLOSED],
  required, mutable
- resolution_decision: string, max 512 characters, optional, null until state = RESOLVED
- resolved_by: UUID, optional, null until state = RESOLVED;
  foreign key to reviewer record
- resolved_at: ISO 8601 timestamp, UTC, optional, null until state = RESOLVED
- created_at: ISO 8601 timestamp, UTC, immutable
- updated_at: ISO 8601 timestamp, UTC, updated on any modification
- created_by: UUID, agent instance ID, immutable

Relationships:
- claim_id: UUID, foreign key to ClaimRecord, required, many:1, on delete: restrict
- classification_result_id: UUID, foreign key to ClinicalClassificationResult,
  optional, 1:1, on delete: set null

State machine:
- Initial state: DELIVERED

- DELIVERED → ACKNOWLEDGED: HITL reviewer opens the packet; acknowledgement timestamp
  recorded
- DELIVERED → SLA_BREACHED: response_sla_hours elapsed without acknowledgement;
  Queue & SLA Management Agent triggers breach action
- ACKNOWLEDGED → RESOLVED: reviewer records a resolution_decision with resolved_by set
- ACKNOWLEDGED → SLA_BREACHED: sla_deadline elapsed without resolution after acknowledgement
- RESOLVED → CLOSED: corresponding ClaimRecord state updated to reflect resolution outcome
- SLA_BREACHED → RESOLVED: reviewer records resolution after SLA breach
  (breach event is permanently logged regardless of resolution)
- Terminal states: CLOSED — no valid exit

Invalid transitions:
- RESOLVED → DELIVERED: FORBIDDEN — a resolved escalation cannot be re-opened;
  a new escalation event requires a new EscalationPacket record
- CLOSED → any state: FORBIDDEN — CLOSED is terminal
- DELIVERED → RESOLVED: FORBIDDEN — resolution requires prior acknowledgement;
  an unacknowledged packet cannot be resolved (no audit trail of reviewer review)

Validation rules:
- response_sla_hours must be exactly 1, 2, or 4; any other value is a data integrity error
- sla_deadline = created_at + (response_sla_hours × 3600) seconds exactly
- resolved_by must be non-null when state transitions to RESOLVED
- resolution_decision must be non-null and non-empty (≥ 1 character) when state = RESOLVED
- trigger_signal_values must be valid JSON; all leaf values must be scalar types
  (string, number, boolean) — no nested objects or arrays without a defined schema
  in the per-agent escalation trigger table
- classification_result_id must be non-null when trigger_type ∈
  {CLINICAL_ROUTING, ROUTING_VERIFICATION_BELOW_THRESHOLD}

Naming conventions:
- Table name: escalation_packets (snake_case, plural)
- Primary key: id
- Enum values: SCREAMING_SNAKE_CASE
- JSON fields (trigger_signal_values, pipeline_state_at_escalation): snake_case keys
```

---

## §3. Data and System Requirements

*Every system named here is the starting inventory for the integration preamble (Pass 2). Systems not explicitly named in `Scenario/scenario_context.md` are labelled as assumptions with confidence level.*

### Input data

| Data | Consumer agent | Source system | Granularity | Latency requirement |
|------|---------------|---------------|-------------|---------------------|
| Inbound claim submission (EDI 837P, EDI 837I, Portal JSON, FHIR R4, CMS-1500 PDF, Email .eml, Fax PDF, Exception Notes PDF — all 8 intake formats) | INT Intake Agent | Clearinghouse or provider portal [Assumption A-P1-1: intake mechanism not named in scenario; Medium confidence — standard payer architecture] | Individual claim record | On-demand at submission receipt |
| `NormalizedClaimInput` record (canonical normalized claim; all required fields validated by INT) | WS1 (T-01) | INT Intake Agent output queue | Individual normalized claim record | On-demand queue pickup after INT processing completes |
| Member eligibility record | WS1 (T-02, T-03) | Member eligibility system [Assumption A-P1-2: system not named in scenario; High confidence — payer operations require one] | Member ID + plan ID + date-of-service tuple | Real-time lookup — response required before T-03 can branch (P95 ≤ 5 seconds) |
| ICD-10 / CPT code validity reference | WS1 (T-04) | Code validation table or licensed API [Assumption A-P1-3: assumed structured; High confidence] | Individual code lookup | Batch-loaded — updated on code set publication cycle (annually at minimum) |
| Coding plausibility reference | WS1 (T-05) | Code pairing rules table [Assumption A-P1-3] | Procedure-diagnosis-specialty combination | Batch-loaded |
| Prior authorisation record | WS1 (T-06, T-07); WS2 (JtD-2 packet assembly) | Prior auth system [Assumption A-P1-4: system not named; High confidence — prior auth is a required adjudication step per scenario_context.md] | Member ID + procedure code + service date | Real-time lookup |
| Fee schedule and cost-sharing rules | WS1 (T-09) | Fee schedule system [Assumption A-P1-5: system not named; High confidence] | Provider + procedure code + plan rate + modifier | On-demand retrieval |
| Contract exception rules | WS1 (T-10) | Contract document store [Assumption A-P1-6: accessibility unconfirmed — A-D0C-6 in D3; Low confidence] | Provider + payer contract clause | On-demand retrieval; API accessibility unconfirmed — Wave 1 hard prerequisite for ADR-1 revisit |
| Claim record with routing classification and confidence score | WS2 (JtD-1) | Internal: ClaimRecord in PENDING_PHYSICIAN_REVIEW state (from WS1 pipeline output) | Individual claim + ClinicalClassificationResult (ROUTING call site) | Real-time queue pickup |
| Clinical notes from treating provider | WS2 (JtD-2) | Clinical notes source system [Assumption A-P1-7: A-D0C-7 in D3 — system unknown; Low confidence — Wave 2 hard blocker] | Provider-submitted clinical documentation for this episode of care | On-demand retrieval; API availability unconfirmed |
| Member prior claims history | WS2 (JtD-2) | Claims history database [Assumption A-P1-8: assumed queryable; system not named; Medium confidence] | Member ID + relevant diagnosis range + configurable lookback period | On-demand retrieval |

### Reference data

| Data | Consumer agent | Format | Source |
|------|---------------|--------|--------|
| Medical necessity criteria (InterQual, Milliman, or proprietary) | WS2 (JtD-1 verification, JtD-2 packet assembly) | Format unknown — may be PDF, structured database, or licensed API [Assumption A-P1-9: must be confirmed in Pass 2; Low confidence on format] | Clinical criteria vendor or CMO-maintained reference [Assumption A-P1-10] |
| Clinical content criterion definition (formal definition of "clinical content") | WS1 (T-08), WS2 (JtD-1) | Must be machine-readable and classifier-encodable — not yet produced (scenario_context.md A-4) | CMO team design output; required pre-deployment artefact; not a system prerequisite but blocks go-live |
| URAC / NCQA accreditation requirements relevant to claims adjudication | WS1 (governance), WS2 (governance) | Text-extractable policy document [Assumption A-P1-11: assumed publicly available; specific relevant sections must be identified by the compliance team] | Regulatory body publication |
| Rejection reason code reference | WS1 (T-11, T-12), WS2 (JtD-1) | Structured — validated enumeration | Internal claims operations standard [Assumption A-P1-12] |
| Classifier calibration artefact (signed CMO sign-off record) | WS1 (T-08), WS2 (JtD-1) | Structured JSON with defined schema: threshold value, recall achieved, holdout set size, labelling date, CMO reviewer name | Produced at pre-deployment calibration event; stored in configuration management system |

### Output targets

| Output | Producing agent | Target system | Format |
|--------|----------------|--------------|--------|
| Approved claim → payment processing queue | WS1 (T-09, T-11) | Payment processing system [Assumption A-P1-13: system not named; High confidence] | Structured claim record with payment_amount, approval token, audit_log_entry ID |
| Rejected claim → provider resubmission queue | WS1 (T-11, T-12) | Provider portal or clearinghouse [Assumption A-P1-14] | Rejection notice with machine-readable rejection_codes array |
| Clinical or uncertain claim → physician HITL queue | WS1 (T-12 — routing escalation), WS2 (JtD-2 — packet delivery) | Physician review queue interface [Assumption A-P1-15: system not named; Hard prerequisite for WS2 Wave 2] | EscalationPacket (WS1 routing); pre-filled review packet with completeness indicator (WS2) |
| HITL exception escalation → exception processor queue | WS1 (T-12) | HITL exception management system [Assumption A-P1-16: assumed part of claims management platform] | EscalationPacket with trigger_type, trigger_signal_values, required_resolution |
| Routing verification below threshold → routing review queue | WS2 (JtD-1) | Routing review queue [Assumption A-P1-17: may be same as HITL exception queue — confirmation required in Pass 2] | EscalationPacket with classification_result_id from both ROUTING and VERIFICATION call sites |
| Append-only audit log entries | WS1 (T-11), WS2 (all actions) | Audit log system [Assumption A-P1-18: compliance-grade append-only store; retention period per §13 of per-agent specs] | AuditLogEntry records |

### Approval / governance channels

| Channel | Purpose | How captured | Auditable? |
|---------|---------|--------------|-----------|
| CMO-authorised physician sign-off on clinical claims | URAC/NCQA compliance gate — every clinical claim must have physician or APR review before finalisation | Physician records a signed approval token in the physician review queue interface; token stored in ClaimRecord.hitl_disposition and referenced in AuditLogEntry.human_id; compliance_flags include URAC_NCQA_CLINICAL_GATE | Required — approval token must be queryable by entity_id, reviewer identity, and timestamp |
| HITL exception processor disposition | Resolution of eligibility discrepancies, coding plausibility flags, prior auth mismatches, contract exceptions | Exception processor records resolution_decision in EscalationPacket; triggers ClaimRecord state transition; AuditLogEntry written with action = HITL_RESOLVED | Required — EscalationPacket.resolved_by and resolved_at are immutable once set |
| CMO sign-off on classifier threshold calibration | Pre-deployment and recalibration governance gate (D4 APD §3, post-deployment miscalibration feedback loop) | CMO records signed calibration artefact: threshold value, recall achieved, holdout set size, labelling date, reviewer name; stored in configuration management system; referenced by ClinicalClassificationResult.calibration_record_id | Required — calibration artefact ID stored in every ClinicalClassificationResult produced under that threshold |
| Monthly audit findings recording | Post-deployment miscalibration and quality detection | CMO-authorised clinical reviewer records audit sample results as AuditLogEntry records; miscalibration findings trigger threshold recalibration protocol per D4 APD §3 | Required — audit cohort and findings are permanent AuditLogEntry records |

---

## §4. Context Engineering Design

### Memory architecture

| Memory type | Content | Storage mechanism | Lifecycle |
|-------------|---------|-------------------|-----------|
| In-context (short-term) | Current ClaimRecord with all pipeline step outputs accumulated; active ClinicalClassificationResult for this claim; current configuration values (CLINICAL_CONTENT_CONFIDENCE_THRESHOLD, PRIOR_AUTH_UNIT_TOLERANCE_PCT); current pipeline step completion status; EscalationPacket being assembled | Accumulated in agent context window during single-claim processing | Per-claim: loaded at queue pickup; released after terminal state write (APPROVED, REJECTED, PENDING_PHYSICIAN_REVIEW, or PENDING_HITL_EXCEPTION reached) |
| Semantic (long-term, retrieval) | Medical necessity criteria sections chunked by clinical decision type (ICD chapter × procedure type × severity flag); contract exception rule summaries indexed by provider/payer/procedure combination; coding plausibility reference patterns indexed by procedure code range and specialty; clinical content classifier boundary-case examples (few-shot examples for T-08) | Vector store with metadata filtering; chunks tagged with: source document version identifier, procedure code range, ICD chapter, and expiry date | Loaded at agent deployment; refreshed when reference version identifier changes; stale chunks (past expiry date) excluded from retrieval at query time |
| Procedural (static instructions) | Full adjudication pipeline logic (T-01 through T-12 for WS1; JtD-1 through JtD-2 for WS2); escalation trigger conditions (ET-01 through ET-07; BP-WS2-1, BP-WS2-2); hard stop rules; governance constraint language (URAC/NCQA clinical gate; CMO certification requirement); delegation tier decision logic | System prompt; loaded once per agent instantiation | Static; updated only through a versioned system prompt release with change review; version identifier included in AuditLogEntry.agent_id format |

### Retrieval strategy

**What triggers a retrieval call:**

| Trigger | Task ID | What is retrieved | Why |
|---------|---------|-------------------|-----|
| Coding plausibility assessment begins for a procedure-diagnosis-specialty combination not found in the structured code pairing table | WS1 T-05 | Coding reference: top-3 chunks by cosine similarity to the specific code combination (similarity threshold ≥ 0.70) | T-05 Decision Determinism = L per D2B; structured table covers enumerated pairs; plausibility assessment across novel combinations requires reasoning over reference context |
| Clinical content routing classification begins | WS1 T-08 | Medical necessity criteria: sections relevant to the primary procedure code range and ICD chapter (top-3 chunks; filtered by procedure_code_range and icd_chapter metadata tags; similarity threshold ≥ 0.75) | Classifier accuracy on borderline claims improves with criteria text in-context; without it, the classifier reasons from codes alone — replicating the inconsistency that produces the 41% overturn rate (D3 §1 AI-native moment) |
| WS2 routing verification begins | WS2 JtD-1 | ClinicalClassificationResult for this claim (ROUTING call site) — structured lookup by claim_id; plus medical necessity criteria section for this procedure type (same retrieval as T-08, from VERIFICATION call site) | Verification compares the WS2 call result against the WS1 routing result; inconsistency between the two calls is the primary BP-WS2-1 signal |
| WS2 context assembly: criteria section for review packet | WS2 JtD-2 | Medical necessity criteria: exact section applicable to this procedure-diagnosis combination; retrieved by exact section ID if available from prior classification call on this claim; otherwise top-3 by similarity | The pre-filled review packet must include the specific criteria the physician will apply; an incorrect criteria section is a packet quality failure and a compliance risk |
| Contract exception check triggers during payment calculation | WS1 T-10 | Contract exception rule: exact record match by (provider_npi, payer_id, procedure_code_range) — structured lookup, not vector retrieval | Contract exceptions are point-specific; a top-K similarity retrieval risks surfacing an adjacent clause that does not apply to this claim |

**Retrieval target:**
- Code validity and fee schedule: structured API lookup — no vector retrieval
- Code plausibility reference (novel combinations): top-3 chunks, cosine similarity ≥ 0.70; if no chunk reaches threshold, T-05 proceeds on codes alone and this is noted in AuditLogEntry.input_summary
- Medical necessity criteria: top-3 chunks, cosine similarity ≥ 0.75, filtered by metadata tags; exact section if section ID is available; if no chunk reaches threshold, classification proceeds without augmentation and this is flagged in AuditLogEntry.compliance_flags as RETRIEVAL_THRESHOLD_NOT_MET
- Contract exception rules: exact structured record lookup only — no vector retrieval; if no record matches, ET-06 fires

**Retrieval quality evaluation:**

False-positive retrieval matches in medical necessity criteria (retrieving an irrelevant criteria section for a claim) are a compliance risk in two directions: an irrelevant clinical criteria section in context can bias the classifier toward clinical classification for genuinely administrative claims (inflating physician HITL queue volume); an irrelevant section retrieved for WS2 packet assembly delivers incorrect criteria to the physician (a packet quality failure). The inverse — failing to retrieve the relevant section — causes both agents to reason from codes alone.

Retrieval quality is evaluated pre-deployment as follows:
1. The CMO clinical team labels a holdout set of ≥500 claims with the applicable criteria section ID for each claim.
2. The retrieval system is run against each claim's code combination; retrieved chunks are compared against the labelled section ID.
3. Section precision@1 (correct section as top-1 result) must be ≥ 85%; section recall@3 (correct section in top-3 results) must be ≥ 95% — both thresholds are required before deployment. If either threshold is not met, the chunking strategy is revised before deployment; the thresholds are not lowered.
4. Post-deployment: a random 5% sample of classified claims has retrieved criteria sections reviewed by a clinical reviewer in the monthly audit cohort. Retrieval precision@1 below 80% in the monthly sample triggers a retrieval index rebuild and evaluation before the next processing batch.

**Retrieval cost management:**
- Claim intake data (EDI fields, member IDs, codes) is structured — API lookup, no vector retrieval
- Medical necessity criteria are chunked by clinical decision type: one chunk per unique (ICD chapter × procedure type × severity flag) combination; target chunk size 500–800 tokens; sub-section splitting applied when a section exceeds 1,000 tokens; chunking follows document section headings
- The retrieval index is cached in-memory for the agent processing session — no per-claim index load overhead
- Index refresh is event-triggered (reference version identifier change), not scheduled — no unnecessary refresh cost during steady-state processing
- Token cost per retrieval augmentation is bounded: 3 chunks × 800 tokens = 2,400 input tokens per claim for criteria retrieval; this cost is included in the C1 token economics model (WS1 Sonnet call for T-08)

### Pre-deployment prerequisite checklist

| # | What must be confirmed | Confirmed by | If unconfirmed |
|---|------------------------|--------------|----------------|
| 1 | Medical necessity criteria document format — machine-readable (structured JSON, XML, or text-extractable PDF) vs. image or scan-based; if any section is image-based, OCR preprocessing must produce text-extractable output before the retrieval index can be built | CMO clinical team + IT | WS2 JtD-2 (packet assembly) is blocked; the review packet cannot include criteria sections; physicians review without clinical context support |
| 2 | Medical necessity criteria version control — a machine-readable "last updated" timestamp or version identifier that is queryable by the agent at retrieval time; criteria are updated periodically and stale sections produce incorrect classification signals | CMO clinical team + IT | Agent cannot detect when retrieval index is stale; outdated criteria bias classification; retrieval quality evaluation cannot be scoped to a specific criteria version |
| 3 | Claims management system write API confirmed for all required operations — ClaimRecord state transitions (all 18 defined in §2), physician HITL queue write, exception processor queue write, and audit log append; custom field write access for clinical_classification_id and hitl_disposition | IT / integration team | WS1 cannot write payment determinations or rejections; WS2 cannot update ClaimRecord after packet delivery; both agents cannot produce audit entries; full deployment blocked |
| 4 | Inbound claim trigger mechanism confirmed — the mechanism by which normalised ClaimRecords are delivered to WS1 (API push, event bus subscription, or database polling) approved by IT security before deployment | IT / IT security | WS1 has no trigger; claim processing does not start |
| 5 | Approval / audit trail system confirmed — physician approval token capture system confirmed to log: physician identity, timestamp, claim_id, and decision; immutability after write; queryable by claim_id and reviewer identity; this system is the primary URAC/NCQA compliance evidence | IT / compliance team / CMO | URAC/NCQA certification cannot be completed; clinical claims cannot be finalised; go-live is blocked |
| 6 | Clinical content criterion definition produced by CMO team — the formal definition of "clinical content" (scenario_context.md A-4) must be classifier-encodable before the classifier can be trained or validated; this is a design output, not a system prerequisite | CMO clinical team | Classifier cannot be trained or calibrated; WS1 T-08 and WS2 JtD-1 cannot be deployed; full pipeline blocked regardless of system readiness |
| 7 | Clinical notes source system API availability confirmed — whether clinical notes can be retrieved programmatically; if fax-only or EHR vendor API restriction applies, WS2 JtD-2 is not deployable as specified (D3 §5 conditional assignment) | IT / clinical ops | WS2 packet assembly (JtD-2) cannot be deployed; claims reach physician queue without pre-filled context; WS2 HITL efficiency value is not realised |
| 8 | Contract exception rules accessibility confirmed — whether all in-scope contract exception rules for Wave 1 providers and payers are encoded in a structured, API-accessible data store (D3 ADR-1 revisit condition) | VP Operations / legal / IT | WS1-JtD-3 remains at Agent-led + Human Oversight indefinitely; 85% auto-adjudication benchmark cannot be achieved; ET-06 HITL exception volume remains above minimum |
| 9 | Prior auth system API scope confirmed as read-only from the agent's perspective — write access must be explicitly excluded from the integration contract | IT | Risk of inadvertent prior auth record modification; regulatory compliance exposure |
| 10 | Member eligibility API latency SLA confirmed — P95 response time ≤ 5 seconds for the expected lookup volume (≥1,300 WS1 lookups/day plus retry headroom) | IT / eligibility system owner | T-02 response time cannot be guaranteed within the 7-day SLA window if eligibility lookup is batch-only or subject to multi-hour latency |

---

*Pass 1 complete. Pass 2 (integration preamble) reads §3 system inventory as its starting input.*
