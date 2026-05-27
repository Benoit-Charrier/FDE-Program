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


---

# D4a — Capability Specification: Spec A
## WS1 Administrative Adjudication Agent
### Greenfield Health Systems: Medical Claims Adjudication Transformation

*Source inputs: `Deliverables/D4_preamble_capability_spec.md` (Pass 1), `Deliverables/D4_integration_preamble.md` (Pass 2), `Deliverables/D3_agentic_solution_architecture.md`, `Deliverables/D4_agent_purpose_document.md`, `Scenario/scenario_context.md`. Every design decision traces to one of these inputs or is flagged as an assumption.*

*Pass 3a covers §0–§4. Pass 3b appends §5–§8. Pass 4 appends §10–§14.*

---

## §0. Agent Identity

- **Agent name:** WS1 Administrative Adjudication Agent
- **Job to be Done:** Adjudicate the estimated 65% of Greenfield Health Systems medical claims (~1,300/day) that contain no genuine clinical content — running each through a pipeline of eligibility verification, code validation, prior auth confirmation, clinical content routing, and payment calculation — replacing the current 35-minute full-manual review workflow for administrative claims and producing an approved payment determination, a rejected claim with specific actionable codes, or a structured escalation packet, with a complete defence-ready audit record for every output.
- **D3 reference:** D3 §2 Agent 2 — "WS1 Administrative Adjudication Agent"
- **Delegation archetype:** Agent-led + Human Oversight — consistent with D3 autonomy matrix; the agent executes autonomously across the administrative path and initiates HITL escalation only when specific detectable conditions are met.

**KPIs:**

| KPI | Baseline | Target | How measured | Review cadence |
|-----|----------|--------|--------------|----------------|
| Clinical classifier recall (% of clinical claims correctly routed to physician queue) | Not measured — all claims currently manual | ≥99.5% — hard go-live gate | CMO-labelled holdout set (≥500 claims) pre-deployment; monthly 5% random audit sample of auto-approved claims post-deployment, reviewed by CMO-authorised clinical reviewer, recorded in audit log | Pre-deployment: once before go-live; post-deployment: monthly |
| Auto-adjudication rate (% of admin-path claims reaching terminal status without any HITL queue entry) | 22% across all claim types (scenario.md); admin-path baseline not measured separately [Assumption A-D4a-3] | ≥80% of administrative-path claims | Count of claims reaching APPROVED or REJECTED without entering any HITL queue ÷ total admin-path claims processed, from claims management system (S-07) | Weekly |
| HITL rate (% of admin-path claims entering exception processor queue, excluding physician queue escalations) | 100% — all claims currently manual | ≤20% of administrative-path claims | Count of PENDING_HITL_EXCEPTION entries ÷ total admin-path claims, excluding PENDING_PHYSICIAN_REVIEW transitions | Weekly |
| Cycle time — admin path (calendar days from claim receipt to APPROVED or REJECTED) | 8 days average; 9+ days per VP Operations (Exchange 3) | ≤5 days | Timestamp delta: ClaimRecord.created_at to terminal state transition timestamp, from S-07 | Daily; SLA breach alert fires at day 4 (sla_breach_flag = true) |
| Throughput (claims processed per agent-hour, excluding HITL wait time) | ~1.7 claims/hour per processor (35 min/claim; scenario.md) | ≥120 claims/hour | Claims reaching terminal state ÷ agent-hours logged, from execution metrics | Daily |

**Confidence threshold validation — pre-deployment requirement:**

`CLINICAL_CONTENT_CONFIDENCE_THRESHOLD` (default 0.70) must not be set from model self-reported confidence scores alone. Before deployment:
1. CMO clinical team labels a holdout set of ≥500 historical claims as `admin` or `clinical`.
2. Classifier is run against the holdout set at threshold values 0.50 to 0.90 in 0.05 increments.
3. Threshold is set at the lowest value achieving ≥99.5% recall on the holdout set (recall prioritised over precision).
4. The calibration result is stored as a signed `CalibrationRecord` (see §3) with CMO sign-off date non-null before go-live. The agent refuses to load a threshold value that lacks a signed `CalibrationRecord`.

**Post-deployment miscalibration path:** If the monthly 5% audit reveals auto-approved claims a clinical reviewer classifies as clinical: (1) lower `CLINICAL_CONTENT_CONFIDENCE_THRESHOLD` by 0.05 immediately; (2) expedite clinical review of all auto-approved claims in the prior 30 days; (3) run full recalibration within 5 business days; (4) CMO sign-off required before restoring any threshold.

- **Governance hard stop:** Never issue a payment determination on a claim in `PENDING_PHYSICIAN_REVIEW` state. The payment calculation step (T-09) is architecturally blocked from executing against this queue state. This constraint cannot be overridden by configuration, by a high classifier confidence score, by claim volume pressure, or by a runtime instruction. Any code path that would allow T-09 to execute on a `PENDING_PHYSICIAN_REVIEW` claim is a critical defect.

---

## §1. Purpose and Scope

**Purpose statement:** The WS1 Administrative Adjudication Agent solves the adjudication capacity deficit at Greenfield Health Systems — where a 45-person manual review team (20 processors plus overhead) processes claims at a 5.7× shortfall against daily volume, producing a 9+ day average cycle time against a 7-day contractual SLA and active penalty exposure (VP Operations, Exchange 3). The agent processes the estimated 65% of claims that contain no genuine clinical content through a fully documented, auditable pipeline, producing payment approvals, rejections, and structured escalation packets. It does not make medical necessity determinations, does not perform physician-level clinical judgment, and does not process claims that the clinical content classifier routes to the physician review queue.

**In scope:**
- Receiving normalised `ClaimRecord` objects in `NORMALISED` state from the inbound intake queue and initiating the WS1 pipeline (T-01)
- Member eligibility verification via real-time API lookup against the member eligibility system (S-02) — T-02
- Eligibility discrepancy resolution using the deterministic correction rule set; HITL escalation when no rule applies — T-03
- ICD-10 and CPT code validity check against the validated code reference (S-03) — T-04
- Coding plausibility assessment using the structured pairing table and Haiku 4.5 retrieval-augmented reasoning for novel code combinations — T-05
- Prior authorisation presence lookup (S-04) and partial-match tolerance resolution within `PRIOR_AUTH_UNIT_TOLERANCE_PCT` — T-06, T-07
- Clinical content routing classification using Sonnet 4.6 with medical necessity criteria augmentation (S-15); producing a `ClinicalClassificationResult` with `call_site = ROUTING` — T-08
- Payment calculation against the fee schedule (S-05) and standard contract terms for claims in `ADMIN_CLEARED` state — T-09
- Contract exception handling lookup against S-06 for claims with a contract exception flag; HITL escalation when the clause is outside the validated reference set — T-10
- Audit record generation for every pipeline step output and every terminal or escalation action — T-11
- Escalation packet assembly on any of ET-01 through ET-07 — T-12
- Writing `ClaimRecord` state transitions to the claims management system (S-07)
- Writing approved claims to the payment processing queue (S-11)
- Writing rejected claims with machine-readable rejection codes to the provider portal / clearinghouse outbound (S-12)
- Writing `EscalationPacket` records to the physician HITL queue (S-08) and HITL exception management system (S-09)
- Appending `AuditLogEntry` records to the audit log system (S-10)

**Out of scope:**
- Medical necessity determination — regulatory hard stop: URAC/NCQA accreditation requires physician or advanced practice provider sign-off on every claim with clinical content; no agent confidence level changes this assignment (D3 §5)
- Clinical context assembly (pre-filled physician review packet) — deferred to WS2 (D3 §2 Agent 3); WS1 delivers the `EscalationPacket` to the physician queue and WS2 takes over from `PENDING_PHYSICIAN_REVIEW` state
- Denial appeal processing — Wave 3 deferral (D3 §5); appeals are handled by the Appeals Support Agent after WS1 reaches steady-state quality
- Claim intake from clearinghouse and EDI normalisation — prerequisite handled by the Intake & Anomaly Agent (D3 §2 Agent 1); WS1 receives only normalised `ClaimRecord` objects
- Queue prioritisation and SLA management across all claims — handled by the Queue & SLA Management Agent (D3 §2 Agent 4); WS1 sets `sla_deadline` on `ClaimRecord` at creation and monitors its own SLA clock but does not manage the global queue
- Writing to or modifying member eligibility records, prior auth records, fee schedule data, or any reference data system — data dependency: write access to these systems is not granted; corrections are made by the data-owning team after HITL escalation
- Contract exception rule encoding or maintenance — outside MVP: contract exception rule encoding is a pre-deployment prerequisite (D3 ADR-1; S-06 is SCOPE-OUT in D4 integration preamble)
- Provider communication other than rejection notices — outside MVP: provider outreach for missing documentation is handled by the Queue & SLA Management Agent

---

## §2. Inputs and Outputs

*Input contract alignment note: WS1 receives claims as a `NormalizedClaimInput` dict (the Intake Agent's output contract, defined in `D4_canonical_claim_record.md`). The canonical field names are: `provider_npi` (NPI string), `payer_id` (payer/plan identifier), `source_format` (intake format enum). `ClaimRecord` stores the NPI under column `provider_npi`; `payer_id` is passed through from NormalizedClaimInput and is not a ClaimRecord column. Any reference to `plan_id` in this spec is superseded by `payer_id` from the canonical record.*

**Inputs:**

| Input | Source system | Format | Required / Optional | Validation rule |
|-------|---------------|--------|---------------------|-----------------|
| Normalised claim record in NORMALISED state | S-07 Claims management system (internal queue) | `NormalizedClaimInput` canonical record (see `D4_canonical_claim_record.md §2`); HARD required fields: `claim_id`, `diagnosis_codes`, `procedure_codes`; SOFT required with defaults: `member_id`, `provider_npi`, `date_of_service`, `billed_amount`; source tracking: `source_format`, `source_file`, `intake_warnings` | Required | `ClaimRecord.state = NORMALISED`; all HARD required fields present and non-empty; `date_of_service ≤ created_at` date; `diagnosis_codes` ≥ 1 element matching ICD-10 format; `procedure_codes` ≥ 1 element matching CPT 5-digit format |
| Member eligibility data | S-02 Member eligibility system | HIPAA 270/271 eligibility response; fields: `eligibility_status` (ACTIVE / INACTIVE / NOT_FOUND / PLAN_ID_MISMATCH / COVERAGE_GAP), `coverage_start_date`, `coverage_end_date`, `error_code` | Required | Response received within 5 seconds (P95); non-null `eligibility_status`; coverage dates are ISO 8601 dates when status = ACTIVE |
| ICD-10 / CPT code validity reference | S-03 Code validation reference | Structured lookup table — flat file or API; fields: code value, code type (ICD10 / CPT), valid_from date, valid_through date, description | Required | Reference version identifier non-null; `valid_through` date ≥ today at pipeline startup; confirmed licensed for agent use |
| Coding plausibility reference | S-03 Code validation reference (plausibility table) + vector store (S-15 medical necessity criteria, novel combinations) | Structured procedure-diagnosis-specialty pairing table; vector store chunks tagged by `procedure_code_range` and `icd_chapter` | Required (structured table); Optional (vector augmentation) | Structured table version non-null; vector store index version matches criteria document version identifier; stale chunks (past expiry) excluded at query time |
| Prior authorisation record | S-04 Prior authorisation system | PA query response; fields: `prior_auth_status` (PRESENT_EXACT_MATCH / PRESENT_PARTIAL_MATCH / NOT_REQUIRED / NOT_FOUND / EXPIRED), `authorized_units`, `expiry_date`, `procedure_code`, `member_id` | Required for procedures requiring PA; NOT_REQUIRED is a valid response | Response received within 5 seconds (P95); `authorized_units` non-null when `prior_auth_status ∈ {PRESENT_EXACT_MATCH, PRESENT_PARTIAL_MATCH}`; write access to S-04 explicitly excluded |
| Fee schedule and cost-sharing rules | S-05 Fee schedule system | Rate record keyed by `provider_npi + procedure_code + payer_id + modifier_codes`; fields: `contracted_rate` (decimal USD), `cost_sharing_proportion` (float 0.00–1.00), `rate_version`, `rate_valid_through` | Required | `rate_valid_through` ≥ today; `contracted_rate > 0.00`; `cost_sharing_proportion` in range [0.00, 1.00] |
| Contract exception rules | S-06 Contract document store | Exception clause record keyed by `provider_npi + payer_id + procedure_code_range`; fields: `exception_rate` (decimal USD), `amendment_flag` (boolean), `clause_id` | Required for WS1-JtD-3 full automation — **[SCOPE-OUT — see §14 A-D4a-1]** | S-06 is SCOPE-OUT in D4 integration preamble §1; until confirmed accessible, all T-10 lookups route to ET-06 |
| Medical necessity criteria chunks | S-15 Medical necessity criteria system | Vector store chunks tagged by `procedure_code_range`, `icd_chapter`, source document `version_id`, chunk `expiry_date` | Optional (retrieval augmentation for T-08 and T-05 novel combinations) — **[SCOPE-OUT — see §14 A-D4a-2]** | Cosine similarity ≥ 0.75 for T-08 retrieval; ≥ 0.70 for T-05; chunks past `expiry_date` excluded; if no chunk reaches threshold, T-08 logs `RETRIEVAL_THRESHOLD_NOT_MET` in `compliance_flags` |
| Signed calibration artefact | S-16 Configuration management system | `CalibrationRecord` JSON object (see §3) | Required — loaded at agent startup | `CalibrationRecord.state = SIGNED`; `cmo_signoff_date` non-null; `recall_achieved ≥ 0.995`; `holdout_set_size ≥ 500`; `classifier_version` matches current deployed classifier; agent refuses to start if any condition fails |

**Outputs:**

| Output | Target system / recipient | Format | Trigger condition |
|--------|---------------------------|--------|-------------------|
| Approved claim — payment instruction | S-11 Payment processing system | `ClaimRecord` in `APPROVED` state with `payment_amount` (decimal USD), `AuditLogEntry.id` (approval audit reference), provider routing fields | `ClaimRecord.state` transitions to `APPROVED` after T-09 payment calculation succeeds within confirmed fee schedule and contract terms |
| Rejected claim — rejection notice | S-12 Provider portal / clearinghouse outbound | Structured rejection notice with `ClaimRecord.id`, `rejection_codes` array (machine-readable, from validated rejection code reference set), `reason_descriptions` array (human-readable), `resubmission_guidance` string | `ClaimRecord.state` transitions to `REJECTED`; triggers on: ineligible member, invalid codes, missing required prior auth |
| Clinical routing escalation packet | S-08 Physician review queue interface | `EscalationPacket` with `trigger_type = CLINICAL_ROUTING`, `routing_queue = PHYSICIAN_HITL`, `escalation_trigger_id ∈ {ET-01, ET-02}`, full `ClinicalClassificationResult` (ROUTING call site), all three signal values, reasoning chain, complete `ClaimRecord` to point of escalation | ET-01 fires (classifier returns CLINICAL or UNCERTAIN at any confidence) or ET-02 fires (classifier returns ADMIN but `confidence_score < CLINICAL_CONTENT_CONFIDENCE_THRESHOLD`) |
| HITL exception escalation packet | S-09 HITL exception management system | `EscalationPacket` with `trigger_type ∈ {ELIGIBILITY_DISCREPANCY, PRIOR_AUTH_MISMATCH, CODING_PLAUSIBILITY, CONTRACT_EXCEPTION, AUDIT_FAILURE, GOVERNANCE_VIOLATION}`, corresponding `escalation_trigger_id ∈ {ET-03, ET-04, ET-05, ET-06, ET-07}`, `trigger_signal_values` (all specific numeric/enum values that caused the trigger), `required_resolution` (yes/no or enumerated-options question) | Any of ET-03 through ET-07 fires |
| ClaimRecord state update | S-07 Claims management system | Write to `ClaimRecord` fields: `state`, `payment_amount` (when APPROVED), `rejection_codes` (when REJECTED), `clinical_classification_id` (after T-08), `hitl_queue_type` (when entering HITL state), `hitl_assigned_to` (when HITL reviewer assigned), `updated_by`, `updated_at` | Every pipeline step that produces a state transition or field update |
| AuditLogEntry | S-10 Audit log system | `AuditLogEntry` record (append-only); see shared entity definition in preamble §2 and §13 schema | Every T-11 execution; one record per terminal decision, per escalation trigger, per HITL state transition, and per classification |

---

## §3. Entity Definitions

**Shared entities — do not redefine here:**
- See shared entity definition — `ClaimRecord`
- See shared entity definition — `ClinicalClassificationResult`
- See shared entity definition — `AuditLogEntry`
- See shared entity definition — `EscalationPacket`

All four are defined in `D4_preamble_capability_spec.md` §2. Field names, types, enum values, and state machine transitions are authoritative there. This spec uses them without redefinition.

---

**Per-spec entity: CalibrationRecord**

*This entity is defined in D4a because the calibration governance workflow is initiated by WS1's pre-deployment certification process. It is also read by WS2 (via `ClinicalClassificationResult.calibration_record_id`). D4b references this definition — it does not redefine it.*

```
Entity: CalibrationRecord
Scope: D4a (defined here) — read by both WS1 (startup validation) and WS2
       (ClinicalClassificationResult.calibration_record_id lookup);
       stored in S-16 (configuration management system)

Attributes:
- id: UUID, primary key, immutable, generated on creation
- threshold_value: float, range 0.000–1.000, three decimal places, required, immutable —
  the CLINICAL_CONTENT_CONFIDENCE_THRESHOLD value certified at this calibration event
- recall_achieved: float, range 0.000–1.000, three decimal places, required, immutable —
  classifier recall on the holdout set at threshold_value;
  must be ≥ 0.995 for a valid production artefact; artefacts with recall_achieved < 0.995
  cannot transition to SIGNED
- precision_achieved: float, range 0.000–1.000, three decimal places, required, immutable —
  classifier precision on the holdout set at threshold_value;
  informational — does not gate SIGNED transition, but must be non-null
- holdout_set_size: integer, range 500–∞ (no upper bound), required, immutable —
  number of labelled claims in the holdout set; must be ≥ 500 for a valid production artefact
- holdout_set_labelling_date: ISO 8601 date (not timestamp), required, immutable —
  date on which the CMO clinical team completed labelling of the holdout set
- threshold_sweep_range_low: float, range 0.000–1.000, required, immutable —
  lowest threshold value tested in the calibration sweep; must be ≤ 0.50 (a sweep starting
  above 0.50 is not a valid full sweep)
- threshold_sweep_range_high: float, range 0.000–1.000, required, immutable —
  highest threshold value tested in the sweep; must be ≥ 0.90
- threshold_sweep_step: float, required, immutable —
  step increment used in the sweep; standard value is 0.05; any other value requires a note
  field entry explaining the deviation
- classifier_version: string, max 64 characters, required, immutable —
  version identifier of the classifier model and system prompt evaluated in this calibration;
  must match the classifier_version field in ClinicalClassificationResult records produced
  under this calibration artefact
- call_site: enum [ROUTING, VERIFICATION], required, immutable —
  identifies which agent role this calibration artefact governs;
  ROUTING = WS1 T-08 (clinical content routing classifier, default threshold 0.70);
  VERIFICATION = WS2 JtD-1 (routing verification classifier, default threshold 0.85);
  WS1 startup validation must confirm call_site = ROUTING; WS2 must confirm call_site = VERIFICATION;
  a credential that returns a VERIFICATION record when ROUTING is queried must be rejected
  at startup (cross-contamination guard); IC-S-16 uses this field as a query parameter
- cmo_reviewer_name: string, max 256 characters, required, immutable —
  full name of the CMO-authorised clinical reviewer who signed this artefact;
  must be non-null before state can transition to SIGNED
- cmo_reviewer_id: UUID, required, immutable —
  authenticated identity of the CMO reviewer; must reference a confirmed CMO-role account
  in the identity management system; must be non-null before state = SIGNED
- cmo_signoff_date: ISO 8601 date (not timestamp), optional until SIGNED, immutable once set —
  date on which the CMO reviewer recorded sign-off; null in DRAFT state;
  non-null is the gating condition for state = SIGNED; immutable once set
- state: enum [DRAFT, SIGNED, SUPERSEDED, ARCHIVED], required, mutable
- superseded_by: UUID, optional, null unless state = SUPERSEDED;
  foreign key to the CalibrationRecord that supersedes this one;
  set when a newer CalibrationRecord transitions to SIGNED
- notes: string, max 2048 characters, optional —
  CMO-authored context notes on calibration decisions; no interpretation by the agent;
  not required for a valid artefact
- created_at: ISO 8601 timestamp, UTC, immutable, set on creation
- updated_at: ISO 8601 timestamp, UTC, updated on any modification
- created_by: UUID, identity of the person or system that created the draft record, immutable

Relationships:
- superseded_by: UUID, foreign key to CalibrationRecord, optional, 1:1,
  on delete: set null
- (reverse) classification_results: 1:many via ClinicalClassificationResult.calibration_record_id,
  on delete: restrict — a CalibrationRecord cannot be deleted while ClinicalClassificationResult
  records reference it; archiving is the correct terminal action

State machine:
- Initial state: DRAFT

- DRAFT → SIGNED: CMO reviewer sets cmo_signoff_date; cmo_reviewer_name and cmo_reviewer_id
  are non-null; recall_achieved ≥ 0.995; holdout_set_size ≥ 500; threshold_sweep_range_low ≤ 0.50;
  threshold_sweep_range_high ≥ 0.90; all required fields populated
- SIGNED → SUPERSEDED: a new CalibrationRecord transitions to SIGNED, superseding this one;
  superseded_by is set to the new record's id; the agent loads the new record at next startup
- SIGNED → ARCHIVED: compliance retention period elapsed; no ClinicalClassificationResult
  records reference this artefact in an active or non-archived state
- SUPERSEDED → ARCHIVED: compliance retention period elapsed
- Terminal states: ARCHIVED — no valid exit (archived records are read-only, immutable)

Invalid transitions (at least 3):
- SIGNED → DRAFT: FORBIDDEN — a signed calibration record cannot be reversed to draft;
  if the signed record contains an error, it must be superseded by a corrected SIGNED record;
  reverting to DRAFT would erase the governance evidence of an error
- ARCHIVED → SIGNED: FORBIDDEN — archived artefacts cannot be restored to active status;
  a new calibration event produces a new CalibrationRecord
- DRAFT → ARCHIVED: FORBIDDEN — an unsigned artefact cannot be archived;
  skipping the SIGNED state creates a governance gap (no evidence of CMO review)
- SUPERSEDED → SIGNED: FORBIDDEN — a superseded record cannot become the active artefact
  again; the superseding record is the current authoritative threshold

Validation rules:
- recall_achieved must be ≥ 0.995 before state can transition to SIGNED;
  validation is enforced at write time — a SIGNED transition with recall_achieved < 0.995
  must be rejected with a 422 Unprocessable Entity response
- holdout_set_size must be ≥ 500; artefacts with smaller holdout sets are rejected at
  agent startup with a startup failure and an alert to the compliance team
- cmo_signoff_date must be non-null when state = SIGNED; null in SIGNED state is a data
  integrity violation that blocks agent startup
- threshold_sweep_range_low ≤ threshold_value ≤ threshold_sweep_range_high; a threshold
  value outside the swept range is not valid (the recall at that threshold was not measured)
- threshold_sweep_range_low must be ≤ 0.50; threshold_sweep_range_high must be ≥ 0.90
- classifier_version must match the classifier_version field of all ClinicalClassificationResult
  records produced while this artefact is SIGNED; a version mismatch is a data integrity violation

Naming conventions:
- Table name: calibration_records (snake_case, plural)
- Primary key: id
- Enum values: SCREAMING_SNAKE_CASE
- Date fields (holdout_set_labelling_date, cmo_signoff_date): ISO 8601 date (YYYY-MM-DD);
  no time component; not timestamp
```

---

## §4. Activity Catalog

| Task ID | Task name | Task type | Delegation level | Data required | Tool required | Risk level |
|---------|-----------|-----------|-----------------|---------------|---------------|------------|
| T-01 | Claim record intake and schema validation | Retrieval + Decision | Fully agentic | `ClaimRecord` in `NORMALISED` state; required-fields schema | Internal queue read (S-07); schema validator | Low |
| T-02 | Member eligibility verification | Retrieval | Fully agentic | `member_id`, `payer_id`, `date_of_service` from `NormalizedClaimInput` | Eligibility API read-only (S-02) | Medium |
| T-03 | Eligibility discrepancy resolution | Reasoning + Decision | Agent-led + HITL on condition | Eligibility API response; member record; claim `date_of_service`; eligibility correction rule set | eligibility correction rule set (internal) | Medium |
| T-04 | Procedure and diagnosis code validity check | Retrieval + Decision | Fully agentic | `diagnosis_codes` (ICD-10 array), `procedure_codes` (CPT array) from `ClaimRecord`; code validity reference | Code validation reference (S-03) | Low |
| T-05 | Coding plausibility assessment | Reasoning + Decision | Agent-led + HITL on condition | `diagnosis_codes`, `procedure_codes`, `provider_specialty`; structured pairing table; top-3 vector chunks if novel combination | Haiku 4.5; code plausibility reference table (S-03); medical necessity criteria vector store (S-15) [SCOPE-OUT] | Medium |
| T-06 | Prior authorisation lookup | Retrieval | Fully agentic | `member_id`, `procedure_codes`, `date_of_service` | Prior auth system API read-only (S-04) | Medium |
| T-07 | Prior auth partial-match tolerance resolution | Reasoning + Decision | Agent-led + HITL on condition | Prior auth record (`authorized_units`); `ClaimRecord.procedure_codes` (claimed units); `PRIOR_AUTH_UNIT_TOLERANCE_PCT` | arithmetic; prior auth system API (S-04) | Medium |
| T-08 | Clinical content routing classification | Decision | Agent-led + HITL on condition | `diagnosis_codes`, `procedure_codes`, `provider_specialty`; `CLINICAL_CONTENT_CONFIDENCE_THRESHOLD`; medical necessity criteria top-3 chunks (if available); signed `CalibrationRecord` | Sonnet 4.6; medical necessity criteria vector store (S-15) [SCOPE-OUT]; configuration management (S-16) | **High** |
| T-09 | Payment calculation | Retrieval + Decision | Fully agentic (standard path) | `ClaimRecord` in `ADMIN_CLEARED` state; fee schedule record (`contracted_rate`, `cost_sharing_proportion`, `modifier_codes`); contract exception flag from T-10 | Fee schedule system API (S-05) | Medium |
| T-10 | Contract exception handling | Reasoning + Decision | Agent-led + HITL on condition | `provider_npi`, `payer_id`, `procedure_codes`; contract exception rule record (if S-06 accessible); `amendment_flag` | contract document store (S-06) [SCOPE-OUT] | **High** |
| T-11 | Audit record generation | Generation | Fully agentic | All pipeline step outputs; confidence scores; matched references; timestamps; escalation reason if applicable; `delegation_tier` for each action | Audit log system append-only API (S-10) | Medium |
| T-12 | Escalation packet assembly | Generation | Fully agentic | Pipeline step outputs to point of escalation; trigger type and trigger ID; specific signal values that caused the trigger; `required_resolution` question | Escalation formatter; HITL exception management (S-09) or physician review queue (S-08) | Medium |

**High-risk task cross-reference:**
- T-08 → ET-01 (CLINICAL classification), ET-02 (UNCERTAIN classification or ADMIN below confidence threshold)
- T-10 → ET-06 (contract clause outside validated reference set or pending amendment)

**Configurable parameters referenced in this catalog:**
- `CLINICAL_CONTENT_CONFIDENCE_THRESHOLD`: float, default 0.70, CMO-certified via `CalibrationRecord`; governs T-08 routing branch
- `PRIOR_AUTH_UNIT_TOLERANCE_PCT`: float, default 0.15 (15%), set by VP Operations; governs T-07 partial-match tolerance
- `CODING_PLAUSIBILITY_CONFIDENCE_THRESHOLD`: float, default 0.75, set by VP Operations; governs T-05 Haiku 4.5 confidence gate — below this threshold, implausibility finding is logged but does not escalate ET-05; at or above this threshold with IMPLAUSIBLE result, ET-05 fires

---

*Pass 3a complete. Pass 3b appends §5–§8 to this file.*

---

## §5. Requirements

```
REQ-A-1: Clinical content routing classification on every claim before payment
Description: The agent MUST execute T-08 (clinical content routing classification) on every
  ClaimRecord that reaches ROUTING state, producing a ClinicalClassificationResult with
  call_site = ROUTING before any downstream action. No ClaimRecord MAY transition from
  ROUTING to ADMIN_CLEARED or PAYMENT_CALCULATING without a linked ClinicalClassificationResult
  in CLASSIFIED state with a non-null reasoning_chain.
Acceptance criterion: Zero ClaimRecords in APPROVED state lack a linked ClinicalClassificationResult
  with call_site = ROUTING and state = CLASSIFIED. Verified by post-processing audit query:
  SELECT COUNT(*) FROM claim_records cr
  LEFT JOIN clinical_classification_results ccr
    ON cr.clinical_classification_id = ccr.id AND ccr.call_site = 'ROUTING'
  WHERE cr.state = 'APPROVED' AND (ccr.id IS NULL OR ccr.state != 'CLASSIFIED')
  must return 0.
Delegation tier: AGENT_ALONE
Error handling: If T-08 fails to produce a ClinicalClassificationResult (classifier call error,
  timeout, or missing CalibrationRecord), T-11 triggers ET-07 (audit failure); ClaimRecord
  transitions to PENDING_HITL_EXCEPTION with hitl_queue_type = EXCEPTION_PROCESSOR;
  pipeline does not advance to T-09 under any failure condition.
```

```
REQ-A-2: Signed CalibrationRecord required before any classification
Description: The agent MUST verify at startup that a CalibrationRecord with state = SIGNED,
  cmo_signoff_date non-null, recall_achieved ≥ 0.995, holdout_set_size ≥ 500, and
  classifier_version matching the deployed classifier is present in S-16. The agent MUST
  refuse to start and MUST produce a startup failure alert if any condition is not met.
  The agent MUST NOT load a CLINICAL_CONTENT_CONFIDENCE_THRESHOLD value that lacks this artefact.
Acceptance criterion: Agent startup fails with exit code 1 and a structured alert message
  when tested against: (a) missing CalibrationRecord, (b) CalibrationRecord with state = DRAFT,
  (c) CalibrationRecord with recall_achieved = 0.990 (below 0.995), (d) CalibrationRecord with
  holdout_set_size = 450 (below 500), (e) CalibrationRecord.classifier_version not matching
  deployed classifier. All five conditions produce startup failure, not a warning.
Delegation tier: AGENT_ALONE
Error handling: Startup failure is the correct and complete error handling. The agent does not
  degrade gracefully or operate without a valid CalibrationRecord. Ops team and CMO are
  notified via the startup failure alert before any claim enters the pipeline.
```

```
REQ-A-3: HITL escalation on any of ET-01 through ET-07 trigger conditions
Description: The agent MUST assemble and deliver an EscalationPacket to the correct HITL queue
  within 60 seconds of the trigger condition being detected, for all seven defined escalation
  triggers. The EscalationPacket MUST include: escalation_trigger_id (exact match to ET-01
  through ET-07), trigger_type (from the EscalationPacket.trigger_type enum), all
  trigger_signal_values (specific numeric and enum values that caused the trigger — no
  free-text descriptions), required_resolution (a yes/no or enumerated-options question),
  and pipeline_state_at_escalation (snapshot of all pipeline outputs completed before escalation).
Acceptance criterion: (a) EscalationPacket assembled and written to target queue within 60 seconds
  of trigger detection (measured from AuditLogEntry.timestamp for ESCALATION_TRIGGERED to
  EscalationPacket.created_at). (b) Zero EscalationPackets with null trigger_signal_values
  or a required_resolution field containing free-text without enumerated options. (c) Routing
  queue matches the trigger: ET-01 and ET-02 → PHYSICIAN_HITL; ET-03, ET-04, ET-06, ET-07 →
  EXCEPTION_PROCESSOR; ET-05 → CODING_SPECIALIST.
Delegation tier: AGENT_ALONE (packet assembly); HUMAN_DECIDES (resolution)
Error handling: If EscalationPacket write to the target queue fails (S-08 or S-09 unavailable),
  the agent retries once after 5 seconds, then falls back to writing the packet to S-07
  (claims management system) with a QUEUE_DELIVERY_FAILED flag and alerts ops. ClaimRecord
  remains in PENDING_PHYSICIAN_REVIEW or PENDING_HITL_EXCEPTION — it does not advance.
```

```
REQ-A-4: Complete AuditLogEntry for every terminal decision and every state transition
Description: The agent MUST produce an AuditLogEntry record for every ClaimRecord state
  transition, every ClinicalClassificationResult creation, every EscalationPacket creation,
  every payment instruction write, and every rejection notice write. Each AuditLogEntry MUST
  include all required fields as defined in the shared entity definition in
  D4_preamble_capability_spec.md §2. An AuditLogEntry with any required field null or absent
  MUST trigger ET-07 before the associated action is issued.
Acceptance criterion: Zero ClaimRecords in APPROVED, REJECTED, PENDING_PHYSICIAN_REVIEW, or
  PENDING_HITL_EXCEPTION state lack a corresponding AuditLogEntry with action matching the
  state transition and state = COMMITTED. Tested by audit integrity query post-processing.
  ET-07 fires in 100% of test cases where a required AuditLogEntry field is absent.
Delegation tier: AGENT_ALONE
Error handling: If S-10 (audit log system) is unavailable when T-11 attempts to write,
  the agent queues the AuditLogEntry locally (in-memory, max 50 records), retries at 10-second
  intervals for up to 5 minutes. If S-10 remains unavailable after 5 minutes, the agent
  suspends claim processing and alerts ops. No ClaimRecord reaches a terminal state while
  S-10 is confirmed unavailable.
```

```
REQ-A-5: Graceful degradation when a required integration is unavailable
Description: The agent MUST handle unavailability of S-02 (eligibility), S-04 (prior auth),
  S-05 (fee schedule), and S-07 (claims management) by: (a) retrying the failed call once
  after 5 seconds, (b) escalating to ET-03 (eligibility), ET-04 (prior auth), or ET-07
  (claims management / audit log) if retry also fails, and (c) suspending the affected claim
  in PENDING_HITL_EXCEPTION state without advancing the pipeline. The agent MUST NOT
  auto-approve or auto-reject a claim based on an assumed response from an unavailable system.
Acceptance criterion: When S-02 is simulated as returning a 503 error on both the initial call
  and the one retry: (a) ClaimRecord transitions to PENDING_HITL_EXCEPTION within 15 seconds,
  (b) EscalationPacket is written with trigger_type = ELIGIBILITY_DISCREPANCY and
  trigger_signal_values includes the system error code, (c) no ClaimRecord in that test
  batch reaches APPROVED or REJECTED state. Same behaviour verified for S-04 and S-05.
Delegation tier: AGENT_ALONE (detection and escalation); HUMAN_DECIDES (resolution)
Error handling: This requirement IS the error handling specification. The named failure path
  is: retry once → escalate to HITL → suspend claim. There is no further fallback.
```

```
REQ-A-6: Governance hard stop — T-09 MUST NOT execute on PENDING_PHYSICIAN_REVIEW claims
Description: The agent MUST enforce that T-09 (payment calculation) reads only ClaimRecord
  objects in ADMIN_CLEARED state. The agent MUST abort T-09 immediately and escalate ET-07
  if at the point of T-09 invocation the ClaimRecord.state is any value other than
  ADMIN_CLEARED. This check MUST occur as the first operation of T-09, before any fee
  schedule lookup or payment arithmetic is performed.
Acceptance criterion: When a test ClaimRecord with state = PENDING_PHYSICIAN_REVIEW is
  injected directly into the T-09 input queue by a test harness: (a) T-09 aborts within
  100 milliseconds without writing any payment_amount to the ClaimRecord, (b) ET-07 fires
  with EscalationPacket.trigger_type = GOVERNANCE_VIOLATION and trigger_signal_values
  including {claim_id, actual_state: PENDING_PHYSICIAN_REVIEW, expected_state: ADMIN_CLEARED},
  (c) ClaimRecord.state remains PENDING_PHYSICIAN_REVIEW — it does not transition to
  PENDING_HITL_EXCEPTION (the incoming state is the diagnostic signal; overwriting it would
  destroy the evidence). This test MUST pass on every build before deployment.
Delegation tier: AGENT_ALONE (detection and abort); HUMAN_DECIDES (investigation)
Error handling: Abort and escalate ET-07. This is not a recoverable condition — it is a
  critical defect signal. Any code path that produces a PENDING_PHYSICIAN_REVIEW claim in
  the T-09 input queue is a build failure, not a runtime error to be handled gracefully.
```

```
REQ-A-7: Prior auth tolerance application must be logged and reported
Description: When T-07 applies the PRIOR_AUTH_UNIT_TOLERANCE_PCT to approve a partial-match
  prior auth case (claimed units exceed authorized units by ≤ PRIOR_AUTH_UNIT_TOLERANCE_PCT),
  the agent MUST log the tolerance application in AuditLogEntry with action =
  CLAIM_STATE_TRANSITION, delegation_tier = AGENT_LOGS, and output_summary including:
  authorized_units, claimed_units, pct_excess (computed), PRIOR_AUTH_UNIT_TOLERANCE_PCT
  value at time of application. These records MUST be included in a daily batch summary
  report to the HITL exception team.
Acceptance criterion: Zero tolerance-approved claims lack an AuditLogEntry with the four
  required output_summary fields. Daily batch summary query returns the correct count of
  tolerance-approved claims for the prior processing day.
Delegation tier: AGENT_LOGS
Error handling: If AuditLogEntry write fails for a tolerance-approved claim, ET-07 fires
  before the approval is issued — the claim is suspended; the approval is not written.
```

```
REQ-A-8: Reference data version check at pipeline startup
Description: The agent MUST verify at startup that all loaded reference data sources have
  a non-expired version: S-03 code validity reference (valid_through ≥ today), S-05 fee
  schedule (rate_valid_through ≥ today), and the medical necessity criteria index version
  identifier (if S-15 is accessible). If any reference source is expired, the agent MUST
  log an expired_reference warning and route all claims that require that reference to
  ET-06 rather than applying the stale reference.
Acceptance criterion: When S-03 is loaded with a valid_through date of yesterday: (a) agent
  logs an expired_reference event at startup, (b) all T-04 and T-05 calls that would use
  S-03 route to ET-06 with flag = not_in_validated_set, (c) agent does not apply the expired
  reference to any claim. Claims not requiring the expired reference continue to process normally.
Delegation tier: AGENT_ALONE (version check and routing); HUMAN_DECIDES (reference refresh)
Error handling: Expired reference routes affected claims to ET-06. The reference owner
  (VP Operations / IT) refreshes and commits a new validated version; claims are re-queued.
```

---

## §6. Decision Logic

---

```
Decision D-A-1: Member eligibility determination
Input:
  - NormalizedClaimInput: member_id (string), payer_id (string), date_of_service (ISO 8601 date)
  - S-02 eligibility API response: eligibility_status enum
    [ACTIVE, INACTIVE, NOT_FOUND, PLAN_ID_MISMATCH, COVERAGE_GAP],
    coverage_start_date (ISO 8601 date or null), coverage_end_date (ISO 8601 date or null),
    error_code (string or null)
  - Eligibility correction rule set (internal): keyed by discrepancy_type; each rule has
    a match_condition (boolean expression) and a corrective_action (string)

Logic:
  IF S-02 returns HTTP 5xx or times out after 5 seconds:
    retry once after 5 seconds
    IF retry also fails:
      THEN escalate ET-03 with trigger_signal_values = {error_type: "API_UNAVAILABLE",
        member_id, payer_id, date_of_service}
      GOTO end
  IF eligibility_status = ACTIVE
    AND coverage_start_date ≤ date_of_service
    AND date_of_service ≤ coverage_end_date:
    THEN eligibility_result = CONFIRMED; pipeline advances to T-04
  ELSE IF eligibility_status ∈ {INACTIVE, NOT_FOUND, PLAN_ID_MISMATCH, COVERAGE_GAP}:
    check eligibility correction rule set for a rule where match_condition(member_id,
      payer_id, date_of_service, eligibility_status) = true
    IF matching rule found:
      THEN apply corrective_action; eligibility_result = CORRECTED;
        log AuditLogEntry with action = CLAIM_STATE_TRANSITION, delegation_tier = AGENT_LOGS,
        output_summary.correction_rule_applied = rule.id; pipeline advances to T-04
    ELSE (no matching correction rule):
      THEN escalate ET-03 with trigger_signal_values = {eligibility_status,
        member_id, payer_id, date_of_service, error_code}
  ELSE (API returned null eligibility_status or unrecognised value):
    THEN escalate ET-03 with trigger_signal_values = {error: "NULL_OR_UNKNOWN_STATUS",
      raw_response_code: error_code}

Output: eligibility_result ∈ {CONFIRMED, CORRECTED, ESCALATED_ET03}
Delegation tier: AGENT_ALONE for CONFIRMED; AGENT_LOGS for CORRECTED; HUMAN_DECIDES for ESCALATED_ET03
Confidence gate: not applicable — this decision is binary rule-based, not confidence-scored

Worked example:
  Input values: member_id = "GHS-MBR-0042891", payer_id = "GHS-PPO-2026",
    date_of_service = "2026-04-15"
  API response: eligibility_status = ACTIVE, coverage_start_date = "2026-01-01",
    coverage_end_date = "2026-12-31"
  Branch taken: First IF fires — ACTIVE AND 2026-01-01 ≤ 2026-04-15 ≤ 2026-12-31
  Output: eligibility_result = CONFIRMED; AuditLogEntry written with action =
    CLAIM_STATE_TRANSITION, input_summary = {member_id, payer_id, date_of_service,
    eligibility_status: "ACTIVE"}, output_summary = {eligibility_result: "CONFIRMED"};
    pipeline advances to T-04
```

---

```
Decision D-A-2: Code validity and plausibility check
Input:
  - ClaimRecord: diagnosis_codes (ICD-10 array), procedure_codes (CPT array),
    provider_specialty (string)
  - S-03 code validity reference: valid_through date, set of valid ICD-10 codes,
    set of valid CPT codes
  - S-03 code plausibility reference table: rows keyed by
    (procedure_code_range, icd_chapter, provider_specialty), result ∈ {PLAUSIBLE, IMPLAUSIBLE}
  - S-15 vector store (novel combinations): top-3 chunks by cosine similarity ≥ 0.70
  - CODING_PLAUSIBILITY_CONFIDENCE_THRESHOLD: float (default 0.75)

Logic — T-04 (code validity, runs first):
  IF S-03.valid_through < today:
    THEN log expired_reference warning; route to ET-06 with
      trigger_signal_values = {expired_reference: "S-03", valid_through, today};
    GOTO end
  FOR EACH code in diagnosis_codes:
    IF NOT (code matches ICD-10 format AND code ∈ S-03 valid ICD-10 set):
      THEN add code to invalid_codes list
  FOR EACH code in procedure_codes:
    IF NOT (code matches CPT format (5-digit numeric) AND code ∈ S-03 valid CPT set):
      THEN add code to invalid_codes list
  IF invalid_codes list is non-empty:
    THEN ClaimRecord.state → REJECTED; rejection_codes populated with one
      INVALID_CODE entry per invalid code; T-12 assembles rejection notice; pipeline terminates
  (all codes valid — advance to T-05)

Logic — T-05 (coding plausibility, runs after all codes confirmed valid):
  look up (procedure_codes[0], icd_chapter(diagnosis_codes[0]), provider_specialty)
    in structured plausibility table
  IF combination found in table AND table_result = PLAUSIBLE:
    THEN plausibility_result = PLAUSIBLE; pipeline advances to T-06
  ELSE IF combination found in table AND table_result = IMPLAUSIBLE:
    THEN call Haiku 4.5 to review for overriding context
    IF Haiku returns IMPLAUSIBLE AND confidence_score ≥ CODING_PLAUSIBILITY_CONFIDENCE_THRESHOLD:
      THEN escalate ET-05 with trigger_signal_values = {procedure_codes, diagnosis_codes,
        provider_specialty, haiku_result: "IMPLAUSIBLE", haiku_confidence: confidence_score,
        table_result: "IMPLAUSIBLE"}
    ELSE (Haiku returns PLAUSIBLE OR confidence < threshold):
      THEN plausibility_result = PLAUSIBLE; log haiku result in AuditLogEntry.input_summary;
        pipeline advances to T-06
  ELSE (combination not in table — novel combination):
    retrieve top-3 chunks from S-15 vector store (similarity ≥ 0.70)
    IF at least 1 chunk retrieved above threshold:
      THEN call Haiku 4.5 with chunks as context
      IF Haiku returns IMPLAUSIBLE AND confidence_score ≥ CODING_PLAUSIBILITY_CONFIDENCE_THRESHOLD:
        THEN escalate ET-05
      ELSE:
        THEN plausibility_result = PLAUSIBLE; log "retrieval_augmented_plausibility"
          in AuditLogEntry; pipeline advances to T-06
    ELSE (no chunks above 0.70 similarity threshold):
      THEN plausibility_result = PLAUSIBLE (proceed on structured codes alone);
        log AuditLogEntry with compliance_flags += ["RETRIEVAL_THRESHOLD_NOT_MET"];
        pipeline advances to T-06

Output: plausibility_result ∈ {PLAUSIBLE, ESCALATED_ET05} OR ClaimRecord.state = REJECTED
Delegation tier: AGENT_ALONE for PLAUSIBLE and REJECTED; HUMAN_DECIDES for ESCALATED_ET05
Confidence gate: CODING_PLAUSIBILITY_CONFIDENCE_THRESHOLD = 0.75 (default); below threshold,
  implausibility finding is logged but does not escalate; at or above threshold with
  IMPLAUSIBLE result, ET-05 fires

Worked example (valid codes, standard path):
  Input values: diagnosis_codes = ["J06.9"], procedure_codes = ["99214"],
    provider_specialty = "Internal Medicine"
  T-04: J06.9 valid ICD-10 (acute upper respiratory infection, unspecified);
    99214 valid CPT (E&M level 4) — no invalid codes
  T-05: combination (99214, J chapter, Internal Medicine) found in structured table → PLAUSIBLE
  Branch taken: T-04 all valid → T-05 table lookup → PLAUSIBLE
  Output: plausibility_result = PLAUSIBLE; AuditLogEntry written; pipeline advances to T-06

Worked example (novel combination, escalation):
  Input values: diagnosis_codes = ["I25.10"], procedure_codes = ["59400"],
    provider_specialty = "Cardiology"
  T-04: I25.10 valid; 59400 valid (global OB care package) — no invalid codes
  T-05: combination (59400, I chapter, Cardiology) not in structured table
    → retrieve from S-15 vector store → 2 chunks retrieved (similarity 0.73, 0.81)
    → Haiku 4.5 with context: "Global OB care billed under a cardiac diagnosis by a
      cardiologist is inconsistent with clinical practice — OB care requires an OB provider
      billing under a pregnancy diagnosis"
    → Haiku result: IMPLAUSIBLE, confidence_score = 0.91 ≥ 0.75
  Branch taken: novel combination → retrieval augmented → Haiku IMPLAUSIBLE above threshold
  Output: escalate ET-05; EscalationPacket with trigger_signal_values = {procedure_codes:
    ["59400"], diagnosis_codes: ["I25.10"], provider_specialty: "Cardiology",
    haiku_confidence: 0.91, source: "retrieval_augmented"}
```

---

```
Decision D-A-3: Prior authorisation determination
Input:
  - ClaimRecord: procedure_codes (CPT array), member_id, date_of_service
  - S-04 prior auth API response: prior_auth_status enum
    [PRESENT_EXACT_MATCH, PRESENT_PARTIAL_MATCH, NOT_REQUIRED, NOT_FOUND, EXPIRED],
    authorized_units (integer or null), expiry_date (ISO 8601 date or null),
    auth_record_id (string or null)
  - PRIOR_AUTH_UNIT_TOLERANCE_PCT: float (default 0.15)
  - claimed_units: integer (derived from ClaimRecord procedure code quantity field)

Logic:
  IF S-04 returns HTTP 5xx or times out after 5 seconds:
    retry once after 5 seconds
    IF retry also fails:
      THEN escalate ET-04 with trigger_signal_values = {error_type: "API_UNAVAILABLE",
        procedure_codes, member_id, date_of_service}
      GOTO end
  IF prior_auth_status = NOT_REQUIRED:
    THEN auth_result = CONFIRMED (no prior auth needed for this procedure); pipeline advances to T-08
  ELSE IF prior_auth_status = PRESENT_EXACT_MATCH
    AND authorized_units = claimed_units:
    THEN auth_result = CONFIRMED; pipeline advances to T-08
  ELSE IF prior_auth_status = PRESENT_EXACT_MATCH
    AND authorized_units ≠ claimed_units:
    THEN escalate ET-04 with trigger_signal_values = {prior_auth_status: "PRESENT_EXACT_MATCH",
      authorized_units, claimed_units, error: "UNIT_COUNT_CONTRADICTION",
      note: "S-04 returned PRESENT_EXACT_MATCH but authorized_units ≠ claimed_units —
        contradictory API response; cannot auto-resolve; HITL exception processor must
        confirm correct authorised unit count before adjudication proceeds"}
  ELSE IF prior_auth_status = PRESENT_PARTIAL_MATCH
    AND claimed_units > authorized_units:
    compute pct_excess = (claimed_units - authorized_units) / authorized_units
    IF pct_excess ≤ PRIOR_AUTH_UNIT_TOLERANCE_PCT:
      THEN auth_result = TOLERANCE_APPROVED;
        log AuditLogEntry with action = CLAIM_STATE_TRANSITION, delegation_tier = AGENT_LOGS,
        output_summary = {authorized_units, claimed_units, pct_excess, PRIOR_AUTH_UNIT_TOLERANCE_PCT};
        add to daily tolerance batch report; pipeline advances to T-08
    ELSE (pct_excess > PRIOR_AUTH_UNIT_TOLERANCE_PCT):
      THEN escalate ET-04 with trigger_signal_values = {prior_auth_status, authorized_units,
        claimed_units, pct_excess, PRIOR_AUTH_UNIT_TOLERANCE_PCT, auth_record_id}
  ELSE IF prior_auth_status = NOT_FOUND:
    THEN escalate ET-04 with trigger_signal_values = {prior_auth_status: "NOT_FOUND",
      procedure_codes, member_id, date_of_service}
  ELSE IF prior_auth_status = EXPIRED:
    THEN escalate ET-04 with trigger_signal_values = {prior_auth_status: "EXPIRED",
      auth_record_id, expiry_date, date_of_service}
  ELSE (null or unrecognised status):
    THEN escalate ET-04 with trigger_signal_values = {error: "NULL_OR_UNKNOWN_STATUS",
      raw_status: prior_auth_status}

Output: auth_result ∈ {CONFIRMED, TOLERANCE_APPROVED, ESCALATED_ET04}
Delegation tier: AGENT_ALONE for CONFIRMED; AGENT_LOGS for TOLERANCE_APPROVED;
  HUMAN_DECIDES for ESCALATED_ET04
Confidence gate: not applicable — rule-based numeric comparison

Worked example (tolerance approval):
  Input values: procedure_code = "97110" (therapeutic exercises, PT),
    member_id = "GHS-MBR-0042891", date_of_service = "2026-04-15"
  API response: prior_auth_status = PRESENT_PARTIAL_MATCH, authorized_units = 20,
    auth_record_id = "PA-2026-004891"
  ClaimRecord claimed_units = 22; PRIOR_AUTH_UNIT_TOLERANCE_PCT = 0.15
  Branch taken: PRESENT_PARTIAL_MATCH; pct_excess = (22-20)/20 = 0.10 ≤ 0.15
  Output: auth_result = TOLERANCE_APPROVED; AuditLogEntry written with output_summary =
    {authorized_units: 20, claimed_units: 22, pct_excess: 0.10,
    PRIOR_AUTH_UNIT_TOLERANCE_PCT: 0.15}; pipeline advances to T-08

Worked example (exceeds tolerance):
  Input values: same claim with claimed_units = 25
  pct_excess = (25-20)/20 = 0.25 > 0.15
  Branch taken: PRESENT_PARTIAL_MATCH; pct_excess > PRIOR_AUTH_UNIT_TOLERANCE_PCT
  Output: escalate ET-04; EscalationPacket with trigger_signal_values = {authorized_units: 20,
    claimed_units: 25, pct_excess: 0.25, PRIOR_AUTH_UNIT_TOLERANCE_PCT: 0.15,
    auth_record_id: "PA-2026-004891"}
```

---

```
Decision D-A-4: Clinical content routing classification
Input:
  - ClaimRecord: diagnosis_codes (ICD-10 array), procedure_codes (CPT array),
    provider_specialty (string); state must = ROUTING at call time
  - CLINICAL_CONTENT_CONFIDENCE_THRESHOLD: float (default 0.70), loaded from
    signed CalibrationRecord in S-16
  - CalibrationRecord: state must = SIGNED, recall_achieved ≥ 0.995 (validated at startup)
  - S-15 medical necessity criteria: top-3 chunks retrieved by cosine similarity ≥ 0.75,
    filtered by metadata procedure_code_range and icd_chapter (may be empty if SCOPE-OUT
    or no chunk reaches threshold)

Pre-condition check (runs before classifier call):
  IF CalibrationRecord.state ≠ SIGNED OR CalibrationRecord.cmo_signoff_date is null:
    THEN abort T-08; escalate ET-07 with trigger_signal_values =
      {error: "CALIBRATION_RECORD_INVALID", calibration_record_id, actual_state};
    ClaimRecord.state → PENDING_HITL_EXCEPTION; GOTO end
  IF ClaimRecord.state ≠ ROUTING:
    THEN abort T-08; escalate ET-07 with trigger_signal_values =
      {error: "WRONG_CLAIM_STATE_FOR_T08", actual_state: ClaimRecord.state,
      expected_state: "ROUTING"}; GOTO end

Logic:
  Attempt to retrieve top-3 criteria chunks from S-15 (similarity ≥ 0.75)
  IF S-15 SCOPE-OUT or no chunk reaches threshold:
    THEN criteria_chunks = []; log AuditLogEntry.compliance_flags += ["RETRIEVAL_THRESHOLD_NOT_MET"]
  ELSE:
    criteria_chunks = retrieved chunks

  Call Sonnet 4.6 classifier with {diagnosis_codes, procedure_codes, provider_specialty,
    criteria_chunks}
  Classifier returns: classification ∈ {ADMIN, CLINICAL, UNCERTAIN},
    confidence_score (float 0.000–1.000), reasoning_chain (string ≥ 20 characters)

  Create ClinicalClassificationResult:
    call_site = ROUTING; classification; confidence_score;
    threshold_applied = CLINICAL_CONTENT_CONFIDENCE_THRESHOLD;
    threshold_met = (confidence_score ≥ threshold_applied);
    signal_diagnosis_codes = diagnosis_codes; signal_procedure_codes = procedure_codes;
    signal_provider_specialty = provider_specialty; reasoning_chain; classifier_version;
    calibration_record_id; state → CLASSIFIED

  Link ClaimRecord.clinical_classification_id = ClinicalClassificationResult.id

  IF classification = ADMIN AND confidence_score ≥ CLINICAL_CONTENT_CONFIDENCE_THRESHOLD:
    THEN ClaimRecord.state → ADMIN_CLEARED;
      AuditLogEntry written with action = CLAIM_STATE_TRANSITION, compliance_flags = [];
      pipeline advances to T-09
  ELSE IF classification = CLINICAL (any confidence_score):
    THEN ClaimRecord.state → PENDING_PHYSICIAN_REVIEW;
      hitl_queue_type = PHYSICIAN_REVIEW;
      AuditLogEntry written with compliance_flags = ["URAC_NCQA_CLINICAL_GATE"];
      T-12 assembles EscalationPacket with escalation_trigger_id = ET-01;
      deliver to S-08; pipeline terminates for WS1
  ELSE IF classification = UNCERTAIN (any confidence_score):
    THEN ClaimRecord.state → PENDING_PHYSICIAN_REVIEW;
      hitl_queue_type = PHYSICIAN_REVIEW;
      AuditLogEntry written with compliance_flags = ["URAC_NCQA_CLINICAL_GATE"];
      T-12 assembles EscalationPacket with escalation_trigger_id = ET-01;
      deliver to S-08; pipeline terminates for WS1
  ELSE IF classification = ADMIN AND confidence_score < CLINICAL_CONTENT_CONFIDENCE_THRESHOLD:
    THEN ClaimRecord.state → PENDING_PHYSICIAN_REVIEW;
      hitl_queue_type = PHYSICIAN_REVIEW;
      AuditLogEntry written with compliance_flags = ["BORDERLINE_CONFIDENCE"];
      T-12 assembles EscalationPacket with escalation_trigger_id = ET-02,
        additional field borderline_confidence_flag = true;
      deliver to S-08; pipeline terminates for WS1

Output: ClaimRecord.state ∈ {ADMIN_CLEARED, PENDING_PHYSICIAN_REVIEW};
  ClinicalClassificationResult created and linked
Delegation tier: AGENT_ALONE when classification = ADMIN AND confidence ≥ threshold;
  HUMAN_DECIDES for all other outcomes
Confidence gate: CLINICAL_CONTENT_CONFIDENCE_THRESHOLD (default 0.70, CMO-certified);
  below threshold on ADMIN result → ET-02, HUMAN_DECIDES

Worked example (admin path, above threshold):
  Input values: diagnosis_codes = ["I25.10"], procedure_codes = ["93306"],
    provider_specialty = "Cardiology", CLINICAL_CONTENT_CONFIDENCE_THRESHOLD = 0.70
  S-15 retrieval: 2 chunks retrieved (cosine similarity 0.81, 0.76) for
    procedure_code_range "93000–93799" (cardiac procedures) × icd_chapter "I" (circulatory)
  Classifier output: classification = ADMIN, confidence_score = 0.87,
    reasoning_chain = "Standard transthoracic echocardiography (CPT 93306) for documented
    atherosclerotic coronary artery disease (ICD-10 I25.10) billed by a cardiologist —
    consistent with routine diagnostic surveillance per InterQual criteria for ischemic
    cardiac monitoring; no surgical intervention, inpatient admission, or medical necessity
    determination required."
  Branch taken: classification = ADMIN AND 0.87 ≥ 0.70 → first IF fires
  Output: ClaimRecord.state → ADMIN_CLEARED; ClinicalClassificationResult (ROUTING, ADMIN,
    0.87, threshold_met = true) created; AuditLogEntry written; pipeline advances to T-09

Worked example (clinical escalation):
  Input values: diagnosis_codes = ["M17.11"], procedure_codes = ["27447"],
    provider_specialty = "Orthopedics", CLINICAL_CONTENT_CONFIDENCE_THRESHOLD = 0.70
  S-15 retrieval: 3 chunks retrieved (similarity 0.89, 0.84, 0.78) for
    procedure_code_range "27000–27999" (musculoskeletal) × icd_chapter "M" (musculoskeletal)
  Classifier output: classification = CLINICAL, confidence_score = 0.94,
    reasoning_chain = "Total knee arthroplasty (CPT 27447) for primary osteoarthritis
    (ICD-10 M17.11) is a major elective surgical procedure; medical necessity determination
    requires physician assessment of conservative treatment history (physical therapy,
    weight management, NSAIDs), functional impairment grade, and surgical risk stratification —
    this is a clinical claim requiring physician review per InterQual criteria."
  Branch taken: classification = CLINICAL (any confidence) → second IF fires
  Output: ClaimRecord.state → PENDING_PHYSICIAN_REVIEW; EscalationPacket ET-01 assembled
    and delivered to S-08; AuditLogEntry with compliance_flags = ["URAC_NCQA_CLINICAL_GATE"];
    pipeline terminates for WS1

Worked example (borderline — below threshold):
  Input values: diagnosis_codes = ["J06.9"], procedure_codes = ["99214"],
    provider_specialty = "Internal Medicine", CLINICAL_CONTENT_CONFIDENCE_THRESHOLD = 0.70
  Classifier output: classification = ADMIN, confidence_score = 0.61,
    reasoning_chain = "E&M level 4 for acute upper respiratory infection — typically
    administrative; however signal ambiguity present due to multiple concurrent diagnosis
    modifiers on this claim; confidence below threshold."
  Branch taken: classification = ADMIN AND 0.61 < 0.70 → fourth ELSE IF fires
  Output: ClaimRecord.state → PENDING_PHYSICIAN_REVIEW; EscalationPacket ET-02 assembled
    with borderline_confidence_flag = true, confidence_score = 0.61,
    threshold_applied = 0.70; delivered to S-08; pipeline terminates for WS1
```

---

```
Decision D-A-5: Payment calculation
Pre-condition (runs as first operation of T-09, before any external call):
  IF ClaimRecord.state ≠ ADMIN_CLEARED:
    THEN abort T-09 immediately (no external calls made);
      escalate ET-07 with trigger_signal_values =
        {error: "GOVERNANCE_HARD_STOP_T09", actual_state: ClaimRecord.state,
        expected_state: "ADMIN_CLEARED", claim_id};
      GOTO end — this is REQ-A-6 enforcement

Input (only read after pre-condition passes):
  - NormalizedClaimInput: provider_npi, procedure_codes, modifier_codes, payer_id, member_id
  - S-05 fee schedule response: contracted_rate (decimal USD), cost_sharing_proportion
    (float 0.00–1.00), rate_version, rate_valid_through
  - contract_exception_flag (boolean): set true if T-10 found an applicable exception
  - contract_exception_rate (decimal USD or null): the exception rate if applicable

Logic:
  IF S-05.rate_valid_through < today:
    THEN log expired_reference; escalate ET-06 with trigger_signal_values =
      {expired_reference: "S-05", rate_valid_through, today}; GOTO end
  IF fee_schedule_response returns no rate for (provider_npi, procedure_codes[0], payer_id):
    THEN escalate ET-06 with trigger_signal_values =
      {error: "NO_RATE_FOUND", provider_npi, procedure_codes, payer_id}; GOTO end
  IF contract_exception_flag = false:
    THEN payment_amount = contracted_rate × (1 - cost_sharing_proportion)
      (rounded to 2 decimal places, half-up)
    ClaimRecord.payment_amount = payment_amount
    ClaimRecord.state → APPROVED
    write payment instruction to S-11 with {ClaimRecord.id, payment_amount,
      provider_npi, payer_id, audit_log_entry_id}
    AuditLogEntry written with action = PAYMENT_APPROVED, delegation_tier = AGENT_LOGS,
      output_summary = {payment_amount, contracted_rate, cost_sharing_proportion,
      rate_version, audit_confirmation: true}
  ELSE IF contract_exception_flag = true AND contract_exception_rate is non-null:
    THEN payment_amount = contract_exception_rate × (1 - cost_sharing_proportion)
    proceed same as standard path above; log exception application in AuditLogEntry
  ELSE IF contract_exception_flag = true AND contract_exception_rate is null
    (S-06 SCOPE-OUT or clause not found):
    THEN ClaimRecord.state → PENDING_HITL_EXCEPTION;
      escalate ET-06 with trigger_signal_values =
        {error: "CONTRACT_EXCEPTION_UNRESOLVED", provider_npi, procedure_codes}

Output: ClaimRecord.state ∈ {APPROVED, PENDING_HITL_EXCEPTION}
Delegation tier: AGENT_LOGS for APPROVED (payment approval is AGENT ACTS, HUMAN NOTIFIED AFTER)
Confidence gate: not applicable — arithmetic computation

Worked example (standard admin approval):
  Input values: ClaimRecord.state = ADMIN_CLEARED (pre-condition passes),
    provider_npi = "GHS-PRV-NPI-7124893", procedure_codes = ["93306"],
    payer_id = "GHS-PPO-2026", modifier_codes = [], contract_exception_flag = false
  S-05 response: contracted_rate = 312.50, cost_sharing_proportion = 0.20,
    rate_version = "2026-Q2", rate_valid_through = "2026-06-30"
  Branch taken: pre-condition passes; no exception; rate found; standard path
  payment_amount = 312.50 × (1 - 0.20) = 312.50 × 0.80 = 250.00
  Output: ClaimRecord.state → APPROVED, payment_amount = 250.00; payment instruction written
    to S-11 with {claim_id, payment_amount: 250.00, provider_npi, audit_log_entry_id};
    AuditLogEntry: action = PAYMENT_APPROVED, output_summary = {payment_amount: 250.00,
    contracted_rate: 312.50, cost_sharing_proportion: 0.20, rate_version: "2026-Q2"}
```

---

```
Decision D-A-6: Contract exception handling
Note: S-06 is SCOPE-OUT per D4_integration_preamble.md §1 and §2 (G-2 gap — API
  availability unconfirmed). Until S-06 is confirmed accessible, the first branch below
  fires for every T-10 call. This decision logic is the full specification for when
  S-06 becomes available; it is also the correct stub behaviour in SCOPE-OUT state.

Input:
  - NormalizedClaimInput: provider_npi, procedure_codes (CPT array), payer_id
  - S-06 contract document store (SCOPE-OUT until confirmed): exception record keyed by
    (provider_npi, payer_id, procedure_code_range); fields: exception_rate (decimal USD),
    amendment_flag (boolean), clause_id (string)

Logic:
  IF S-06 is not accessible (SCOPE-OUT or API unavailable):
    THEN contract_exception_flag = true; contract_exception_rate = null;
      escalate ET-06 with trigger_signal_values =
        {error: "S06_SCOPE_OUT", provider_npi, procedure_codes[0], payer_id,
        scope_out_reason: "S-06 API not confirmed accessible (G-2)"};
      ClaimRecord.state → PENDING_HITL_EXCEPTION; GOTO end
  ELSE (S-06 accessible — post-G-2 resolution):
    query S-06 for (provider_npi, payer_id, procedure_codes[0])
    IF exception record found AND amendment_flag = false:
      THEN contract_exception_flag = true; contract_exception_rate = exception_record.exception_rate;
        log AuditLogEntry with action = CLAIM_STATE_TRANSITION, delegation_tier = AGENT_LOGS,
        output_summary = {clause_id, exception_rate, amendment_flag: false};
        return to T-09 with contract_exception_flag = true and rate
    ELSE IF exception record found AND amendment_flag = true:
      THEN escalate ET-06 with trigger_signal_values =
        {clause_id, amendment_flag: true, provider_npi, procedure_codes[0]};
      ClaimRecord.state → PENDING_HITL_EXCEPTION
    ELSE (no exception record for this provider/procedure combination):
      THEN contract_exception_flag = false; contract_exception_rate = null;
        return to T-09 with contract_exception_flag = false (standard fee schedule applies)

Output: contract_exception_flag (boolean), contract_exception_rate (decimal or null),
  OR escalate ET-06
Delegation tier: AGENT_LOGS when exception applied; HUMAN_DECIDES when ET-06 escalated
Confidence gate: not applicable — rule-based lookup

Worked example (SCOPE-OUT state — current behaviour):
  Input values: provider_npi = "GHS-PRV-NPI-7124893", procedure_codes = ["93306"],
    payer_id = "GHS-MAIN-PAYER", S-06 status = SCOPE-OUT
  Branch taken: first IF fires — S-06 not accessible
  Output: escalate ET-06; EscalationPacket with trigger_signal_values =
    {error: "S06_SCOPE_OUT", provider_npi: "GHS-PRV-NPI-7124893",
    procedure_codes: ["93306"], payer_id: "GHS-MAIN-PAYER",
    scope_out_reason: "S-06 API not confirmed accessible (G-2)"};
  ClaimRecord.state → PENDING_HITL_EXCEPTION
```

---

## §7. Escalation Triggers

| Trigger ID | Trigger condition | Threshold | Action | Notified party | SLA | If SLA breached |
|------------|-------------------|-----------|--------|----------------|-----|-----------------|
| ET-01 | Clinical content classifier (T-08) returns `CLINICAL` at any confidence level | Any confidence — classification value alone determines escalation | ClaimRecord.state → PENDING_PHYSICIAN_REVIEW; EscalationPacket assembled with trigger_type = CLINICAL_ROUTING, routing_queue = PHYSICIAN_HITL; all three signal values, full reasoning chain, complete ClaimRecord delivered to S-08 | Physician HITL queue (CMO-authorised clinical reviewer) | 4 hours from EscalationPacket.created_at | SLA_BREACHED flag set on EscalationPacket; escalation re-delivered with URGENT flag to senior physician reviewer; ops dashboard alert; VP Operations and CMO notified within 15 minutes of breach |
| ET-02 | Clinical content classifier (T-08) returns `UNCERTAIN` at any confidence level; OR returns `ADMIN` with confidence_score < CLINICAL_CONTENT_CONFIDENCE_THRESHOLD | UNCERTAIN at any confidence — classification value alone determines escalation; OR ADMIN with confidence_score < CLINICAL_CONTENT_CONFIDENCE_THRESHOLD (default 0.70) | ClaimRecord.state → PENDING_PHYSICIAN_REVIEW; EscalationPacket assembled with trigger_type = CLINICAL_ROUTING, escalation_trigger_id = ET-02, escalation_reason naming contradictory signals (UNCERTAIN) or borderline_confidence_flag = true (ADMIN below threshold), confidence_score and threshold_applied values included; deliver to S-08 | Physician HITL queue (CMO-authorised clinical reviewer) | 4 hours | Same as ET-01 breach action |
| ET-03 | Member eligibility check (T-02/T-03) returns a discrepancy that cannot be resolved by a deterministic correction rule, OR S-02 unavailable after one retry | No matching rule in eligibility correction rule set; OR API returns 5xx/timeout on both attempts | ClaimRecord.state → PENDING_HITL_EXCEPTION; hitl_queue_type = EXCEPTION_PROCESSOR; EscalationPacket with trigger_type = ELIGIBILITY_DISCREPANCY, trigger_signal_values = {eligibility_status, member_id, payer_id, date_of_service, error_code} | HITL exception processor | 2 hours | Exception processor supervisor notified; claim re-tagged URGENT in exception queue; SLA breach event written to AuditLogEntry |
| ET-04 | Prior auth lookup (T-06/T-07) returns: claimed units exceed authorized units by > PRIOR_AUTH_UNIT_TOLERANCE_PCT; OR prior auth absent for a procedure requiring it; OR prior auth EXPIRED; OR S-04 unavailable after one retry | Unit excess > PRIOR_AUTH_UNIT_TOLERANCE_PCT (default 15%); OR status ∈ {NOT_FOUND, EXPIRED}; OR API 5xx/timeout | ClaimRecord.state → PENDING_HITL_EXCEPTION; EscalationPacket with trigger_type = PRIOR_AUTH_MISMATCH, trigger_signal_values = {prior_auth_status, authorized_units, claimed_units, pct_excess, PRIOR_AUTH_UNIT_TOLERANCE_PCT, auth_record_id} | HITL exception processor | 2 hours | Exception processor supervisor notified; URGENT flag added; SLA breach event logged |
| ET-05 | Coding plausibility assessment (T-05) — Haiku 4.5 returns IMPLAUSIBLE with confidence_score ≥ CODING_PLAUSIBILITY_CONFIDENCE_THRESHOLD, on either a table-confirmed implausible combination or a retrieval-augmented novel combination | confidence_score ≥ CODING_PLAUSIBILITY_CONFIDENCE_THRESHOLD (default 0.75) with IMPLAUSIBLE result | ClaimRecord.state → PENDING_HITL_EXCEPTION; EscalationPacket with trigger_type = CODING_PLAUSIBILITY, routing_queue = CODING_SPECIALIST, trigger_signal_values = {procedure_codes, diagnosis_codes, provider_specialty, haiku_result: "IMPLAUSIBLE", haiku_confidence, retrieval_source: "table" or "vector"} | HITL coding specialist | 2 hours | Coding specialist supervisor notified; URGENT flag; SLA breach event logged |
| ET-06 | Contract exception handler (T-10) references a clause not in the validated reference set, has amendment_flag = true, OR S-06 is SCOPE-OUT; OR fee schedule (S-05) returns no rate for the procedure/provider combination; OR reference data (S-03, S-05) is expired | S-06 SCOPE-OUT / clause absent / amendment_flag = true; OR no fee schedule rate; OR reference valid_through < today | ClaimRecord.state → PENDING_HITL_EXCEPTION; EscalationPacket with trigger_type = CONTRACT_EXCEPTION, routing_queue = EXCEPTION_PROCESSOR (+ CONTRACT_OWNER for amendment_flag cases), trigger_signal_values = {error_type, provider_npi, procedure_codes, clause_id (if applicable)} | HITL exception processor; CONTRACT_OWNER for amendment cases | 4 hours | Contract owner notified via secondary alert channel; claim remains in PENDING_HITL_EXCEPTION; VP Operations notified; daily breach summary generated |
| ET-07 | Audit record generation (T-11) produces a record with any required field absent; OR T-08 or T-09 invoked with wrong ClaimRecord.state; OR CalibrationRecord not SIGNED at T-08 execution | Any required AuditLogEntry field null or absent; OR ClaimRecord.state mismatch at T-08 or T-09 invocation | **State behavior splits by cause:** (a) Audit write failure: ClaimRecord.state → PENDING_HITL_EXCEPTION; EscalationPacket with trigger_type = AUDIT_FAILURE, trigger_signal_values = {missing_fields (list), claim_id, pipeline_step}. (b) Governance hard-stop (state mismatch at T-08/T-09 invocation): ClaimRecord.state unchanged (preserved as it was before the check — the incoming state itself is the diagnostic signal); EscalationPacket with trigger_type = GOVERNANCE_VIOLATION, trigger_signal_values = {claim_id, pipeline_step, actual_state, expected_state}. Both causes: partial AuditLogEntry written with available fields; HITL_EXCEPTION_RAISED audit action logged. | HITL exception processor | 1 hour | Agent pipeline suspended for this claim type; system quality incident opened; CMO and VP Operations notified within 15 minutes; no further claims advance to terminal state until root cause is identified |

---

### Required resolution text per trigger

*Authoritative enumerated question text for `EscalationPacket.required_resolution`. These values satisfy REQ-A-3(b): zero EscalationPackets may carry free-text required_resolution. T-12 must use exactly these strings — no paraphrase. The resolution_decision recorded by the HITL reviewer must be one of the bracketed options.*

| Trigger ID | `required_resolution` value (exact string) | Valid `resolution_decision` values |
|------------|--------------------------------------------|------------------------------------|
| ET-01 | `"Route as: [CLINICAL_CONFIRMED / ADMIN_CONFIRMED / NEEDS_ADDITIONAL_INFO]"` | `CLINICAL_CONFIRMED`, `ADMIN_CONFIRMED`, `NEEDS_ADDITIONAL_INFO` |
| ET-02 | `"Route as: [CLINICAL_CONFIRMED / ADMIN_CONFIRMED]"` | `CLINICAL_CONFIRMED`, `ADMIN_CONFIRMED` — `NEEDS_ADDITIONAL_INFO` is not valid for ET-02; see CP-A-2: this is a routing decision, not a clinical determination |
| ET-03 | `"Eligibility: [CONFIRM_ELIGIBLE / CONFIRM_INELIGIBLE / RETURN_TO_SUBMITTER]"` | `CONFIRM_ELIGIBLE`, `CONFIRM_INELIGIBLE`, `RETURN_TO_SUBMITTER` |
| ET-04 | `"Prior auth: [APPROVE_WITH_EXCEPTION / REJECT / RETURN_TO_SUBMITTER]"` | `APPROVE_WITH_EXCEPTION`, `REJECT`, `RETURN_TO_SUBMITTER` |
| ET-05 | `"Coding: [CONFIRM_VALID / CONFIRM_IMPLAUSIBLE / RETURN_TO_SUBMITTER]"` | `CONFIRM_VALID`, `CONFIRM_IMPLAUSIBLE`, `RETURN_TO_SUBMITTER` |
| ET-06 | `"Contract exception: [APPLY_EXCEPTION / USE_STANDARD_RATE / REJECT / RETURN_TO_SUBMITTER]"` | `APPLY_EXCEPTION`, `USE_STANDARD_RATE`, `REJECT`, `RETURN_TO_SUBMITTER` |
| ET-07 (audit write failure) | `"Audit failure: [RECONSTRUCT_AND_CONTINUE / REJECT_CLAIM / ESCALATE_TO_COMPLIANCE]"` | `RECONSTRUCT_AND_CONTINUE`, `REJECT_CLAIM`, `ESCALATE_TO_COMPLIANCE` |
| ET-07 (governance hard-stop) | `"Governance violation: [INVESTIGATE_STATE_MACHINE / REJECT_CLAIM / ESCALATE_TO_COMPLIANCE]"` | `INVESTIGATE_STATE_MACHINE`, `REJECT_CLAIM`, `ESCALATE_TO_COMPLIANCE` |

*Note: ET-01 and ET-02 share the same required_resolution text because both route claims to PHYSICIAN_HITL for the same routing decision. The escalation_trigger_id distinguishes the source (CLINICAL/UNCERTAIN classification vs. below-threshold ADMIN classification); the reviewer's decision task is identical in both cases.*

*Note: ET-07 has two required_resolution strings distinguished by trigger_type. `trigger_type = AUDIT_FAILURE` (missing AuditLogEntry field) uses the audit failure text. `trigger_type = GOVERNANCE_VIOLATION` (T-08 or T-09 invoked with wrong ClaimRecord.state) uses the governance violation text. T-12 must select the string by trigger_type, not by escalation_trigger_id alone.*

---

## §8. Autonomy Matrix

The operational contract between the WS1 Administrative Adjudication Agent and Greenfield Health Systems. Every agent action appears in exactly one tier.

**AGENT DECIDES ALONE (no HITL required):**
- Auto-approve claims where: clinical content classifier returns `ADMIN` with `confidence_score ≥ CLINICAL_CONTENT_CONFIDENCE_THRESHOLD`; member eligibility confirmed with no discrepancy; all procedure and diagnosis codes are valid and plausible per T-04/T-05; prior auth is present and matches claimed units exactly or within `PRIOR_AUTH_UNIT_TOLERANCE_PCT`; payment calculation falls within confirmed fee schedule with no contract exception flag; all upstream gate results validated at T-09 execution time.
- Auto-reject claims where: member is ineligible on date of service with no correctable discrepancy; a required procedure or diagnosis code is invalid per S-03; required prior auth is absent with no matching approval; fee schedule returns no rate and no contract exception applies.
- Code validity check (T-04): accept or reject codes against S-03 reference — binary, rule-based, no judgment required.
- Prior auth lookup (T-06): confirm present / not required / absent — binary API response.
- Member eligibility lookup (T-02): confirm active / not active — binary API response.
- Audit record generation (T-11): assemble and write `AuditLogEntry` for every pipeline action.
- Escalation packet assembly (T-12): assemble and deliver `EscalationPacket` on any ET trigger.
- Schema validation of inbound `ClaimRecord` at T-01.
- Reference version check at pipeline startup (REQ-A-8).

**AGENT ACTS, HUMAN NOTIFIED AFTER:**
- Payment approval — standard administrative claim: agent writes payment instruction to S-11 directly after T-09 calculation completes; VP Operations and claims ops team receive daily batch summary including all approved payment amounts. This is the highest-autonomy action in the WS1 pipeline and is permitted only when all upstream gates (eligibility, coding, prior auth, clinical routing) have passed and the T-09 pre-condition check (state = ADMIN_CLEARED) succeeds.
- Prior auth partial-match tolerance approval (T-07): when claimed units exceed authorised units by ≤ `PRIOR_AUTH_UNIT_TOLERANCE_PCT` — logged to `AuditLogEntry` with `delegation_tier = AGENT_LOGS`; included in daily exception team batch report.
- Eligibility discrepancy correction via deterministic correction rule (T-03): correction applied and logged; weekly correction volume report to ops team.
- Rejection notice delivery to provider portal (T-11/T-12): machine-readable rejection codes written to S-12; VP Operations notified of daily rejection volume.

**AGENT PROPOSES, HUMAN APPROVES BEFORE ACTION:**
- **Clinical routing gate — primary URAC/NCQA governance hard stop:** Any claim where the clinical content classifier (T-08) returns `CLINICAL` or `UNCERTAIN` at any confidence level is placed in `PENDING_PHYSICIAN_REVIEW` state. The agent assembles an escalation packet containing: classification result, confidence score, all three input signals (diagnosis codes, procedure codes, provider specialty), the full Sonnet 4.6 reasoning chain, complete `ClaimRecord` to the point of escalation, and applicable criteria section retrieved (if available). A CMO-authorised physician or advanced practice provider must review the packet and record a signed approval token in S-08 before the claim transitions from `PHYSICIAN_REVIEWING` to `APPROVED`. The WS1 agent has no further role after delivering the escalation packet — WS2 takes over from `PENDING_PHYSICIAN_REVIEW`.
- Borderline confidence routing (ET-02): agent routes `ADMIN`-classified claim with confidence below threshold to physician review, not to the exception processor. Physician reviewer resolves the routing question before any payment action.
- HITL exception escalations (ET-03, ET-04, ET-05, ET-06): agent assembles and delivers `EscalationPacket` with specific trigger type and all signal values; exception processor or coding specialist reviews and issues a disposition; the claim either re-enters the pipeline at the appropriate state or is rejected.

**HUMAN TAKES OVER (agent supports only):**
- Clinical routing below confidence threshold (ET-02 resolution): physician reviewer determines the routing — admin or clinical — after reviewing the escalation packet; the claim proceeds based on the reviewer's decision, not any further agent classification.
- Any claim whose `ClaimRecord` state machine guard has been violated (ET-07 with state mismatch): agent suspends the claim; human investigates the cause before processing resumes.
- Any claim where the contract exception handler (T-10) references a clause outside the validated reference set (ET-06): exception processor and contract owner resolve the reference question before the payment path proceeds.
- Any claim where the audit record is incomplete (ET-07): exception processor reconstructs missing fields from system logs before the determination is issued.
- Any claim in `PENDING_ADDITIONAL_INFO` state: physician has flagged the assembled packet as insufficient; the ops team coordinates provider outreach; the agent provides all assembled context but takes no further processing action until new documentation arrives.

---

**Enforcement mechanism:**

The primary governance gate — blocking `PENDING_PHYSICIAN_REVIEW` claims from reaching T-09 payment calculation — is classified as **procedure-dependent until confirmed**, per `D4_integration_preamble.md` §3 sign-off integrity risk entry (S-07, critical assessment row).

**Architectural intent:** T-09 reads only from `ClaimRecord` objects in `ADMIN_CLEARED` state. The `PENDING_PHYSICIAN_REVIEW → APPROVED` transition is explicitly listed as a FORBIDDEN invalid transition in the `ClaimRecord` state machine (D4 preamble §2). This is the intended system-enforced design.

**Why procedure-dependent until confirmed:** System-enforced classification holds only if the claims management platform (S-07) enforces state machine transitions at the API layer — rejecting a write request to move a claim from `PENDING_PHYSICIAN_REVIEW` to `PAYMENT_CALCULATING` with a 4xx error unless a valid physician approval token is present. If S-07 accepts any state transition write without validating against the state machine, the gate relies on agent code correctness only. A bug, misconfiguration, or direct API call bypasses the gate. This has not been confirmed via G-3 discovery.

**Classification decision:** Procedure-dependent, with the following controls in place until G-3 is resolved:
1. REQ-A-6 enforces the T-09 pre-condition check in agent code (state = ADMIN_CLEARED before any fee schedule call).
2. G-3 mitigation option 2 (middleware state transition guard) is the recommended path to system-enforced status — a dedicated API wrapper validates all state transitions against the defined state machine before forwarding to S-07.
3. Monthly verification query: confirm zero T-09 execution records exist for any claim that was simultaneously in `PENDING_PHYSICIAN_REVIEW` state at execution time.

**This classification is a governance risk. It must appear in §12 (Pass 4) as failure mode FM-A-5 (governance hard stop bypass).** If G-3 discovery confirms S-07 enforces state machine transitions at the API layer, update this section and §12 to system-enforced.

**Physician sign-off capture (S-08) is also procedure-dependent** per D4 integration preamble §3 (S-08 sign-off integrity row): the physician review queue system is unknown; whether it requires individual authenticated login before recording a determination has not been confirmed. This is a separate governance risk that must also appear in §12.

---

*Pass 3b complete. Pass 4 appends §10–§14 to this file.*

---

## §10. State Model

*The full ClaimRecord state machine is defined in `D4_preamble_capability_spec.md` §2 (shared entity definition) and is authoritative for field names, enum values, and transition triggers. This section specifies (a) the WS1-owned transitions with their guard conditions, (b) the states outside WS1 scope for completeness, and (c) invalid transitions relevant to WS1's governance boundaries.*

---

```
Primary entity: ClaimRecord
Full state machine: see D4_preamble_capability_spec.md §2

States (16 total — SCREAMING_SNAKE_CASE):
  RECEIVED, PARSING, PARSE_FAILED, NORMALISED, ADMIN_VALIDATING,
  ROUTING, ADMIN_CLEARED, PAYMENT_CALCULATING, PENDING_PHYSICIAN_REVIEW,
  CLINICAL_PACKET_ASSEMBLY, PENDING_ADDITIONAL_INFO, PHYSICIAN_REVIEWING,
  PENDING_HITL_EXCEPTION, APPROVED, REJECTED, CLOSED

Initial state: RECEIVED (set by Intake & Anomaly Agent on claim creation)
Terminal states: PARSE_FAILED, CLOSED — no valid exit under any condition

WS1 ownership: WS1 reads and writes ClaimRecord in states
  NORMALISED through PAYMENT_CALCULATING (inclusive), plus writes
  PENDING_PHYSICIAN_REVIEW and PENDING_HITL_EXCEPTION on escalation.
  States CLINICAL_PACKET_ASSEMBLY, PENDING_ADDITIONAL_INFO,
  PHYSICIAN_REVIEWING are owned by WS2 (read-only for WS1).
  APPROVED, REJECTED: written by WS1 (PAYMENT_CALCULATING → APPROVED)
  or WS2/HITL (PHYSICIAN_REVIEWING → APPROVED/REJECTED); confirmed CLOSED
  by external payment/portal confirmation.

Transitions — WS1-owned (with guard conditions):

  NORMALISED → ADMIN_VALIDATING
    Trigger: WS1 agent picks up ClaimRecord from normalised queue (T-01)
    Guard conditions:
      1. ClaimRecord.state = NORMALISED (checked before any write)
      2. CalibrationRecord.state = SIGNED with cmo_signoff_date non-null
         (loaded at agent startup — startup fails if not met)
      3. S-03 code validity reference: valid_through ≥ today
      4. S-05 fee schedule reference: rate_valid_through ≥ today
      5. S-07 writable (confirmed responsive at startup health check)
    If guard 2, 3, or 4 fails: agent does not start; ops alert fired;
      ClaimRecord remains in NORMALISED until agent restarts with valid state

  ADMIN_VALIDATING → ROUTING
    Trigger: T-01 through T-07 pipeline completes without triggering
      ET-03, ET-04, ET-05, or ET-07
    Guard conditions:
      1. eligibility_result ∈ {CONFIRMED, CORRECTED} (D-A-1 resolved)
      2. plausibility_result = PLAUSIBLE (D-A-2 resolved without escalation)
      3. auth_result ∈ {CONFIRMED, TOLERANCE_APPROVED} OR
         prior_auth_status = NOT_REQUIRED (D-A-3 resolved)
      4. No pending ET-03, ET-04, ET-05, or ET-07 trigger outstanding
      5. AuditLogEntry written for each of T-02 through T-07 steps
         (T-11 confirms all written before advancing state)
    If any guard fails: ClaimRecord transitions to PENDING_HITL_EXCEPTION
      via the triggering escalation trigger (ET-03, ET-04, ET-05, or ET-07)

  ADMIN_VALIDATING → PENDING_HITL_EXCEPTION
    Trigger: ET-03 (eligibility), ET-04 (prior auth), ET-05 (coding),
      or ET-07 (audit failure) fires and cannot be auto-resolved
    Guard conditions:
      1. Specific escalation trigger ID populated in EscalationPacket
      2. EscalationPacket delivered to S-09 (confirmed write)
      3. hitl_queue_type set to EXCEPTION_PROCESSOR

  ROUTING → ADMIN_CLEARED
    Trigger: T-08 classifier returns ADMIN with confidence_score ≥
      CLINICAL_CONTENT_CONFIDENCE_THRESHOLD (D-A-4, first branch)
    Guard conditions:
      1. ClinicalClassificationResult.state = CLASSIFIED
      2. ClinicalClassificationResult.classification = ADMIN
      3. ClinicalClassificationResult.confidence_score ≥ threshold_applied
      4. ClaimRecord.clinical_classification_id set to result id
      5. AuditLogEntry written with compliance_flags = [] (no URAC flags)
      6. T-08 pre-condition passed (ClaimRecord.state was ROUTING at call time)

  ROUTING → PENDING_PHYSICIAN_REVIEW
    Trigger: T-08 returns CLINICAL or UNCERTAIN at any confidence (ET-01),
      OR returns ADMIN with confidence_score < threshold (ET-02)
    Guard conditions:
      1. ClinicalClassificationResult.state = CLASSIFIED
      2. EscalationPacket assembled and confirmed written to S-08
      3. hitl_queue_type = PHYSICIAN_REVIEW
      4. AuditLogEntry written with compliance_flags including
         URAC_NCQA_CLINICAL_GATE (ET-01) or BORDERLINE_CONFIDENCE (ET-02)
    WS1 pipeline terminates after this transition — WS2 takes over

  ADMIN_CLEARED → PAYMENT_CALCULATING
    Trigger: T-09 pre-condition check passes and fee schedule rate found
    Guard conditions:
      1. ClaimRecord.state = ADMIN_CLEARED (T-09 pre-condition, REQ-A-6)
      2. S-05 fee schedule rate found for (provider_npi, procedure_codes[0],
         payer_id) with rate_valid_through ≥ today
      3. contract_exception_flag = false OR contract_exception_rate non-null
      4. payment_amount = null (not yet calculated — no double-payment)

  ADMIN_CLEARED → PENDING_HITL_EXCEPTION
    Trigger: ET-06 fires — contract exception clause not in validated
      reference set, or fee schedule returns no rate
    Guard conditions:
      1. EscalationPacket assembled with trigger_type = CONTRACT_EXCEPTION
      2. hitl_queue_type = EXCEPTION_PROCESSOR

  PAYMENT_CALCULATING → APPROVED
    Trigger: T-09 payment arithmetic completes; payment instruction written
      to S-11
    Guard conditions:
      1. payment_amount > 0.00 and non-null
      2. S-11 write confirmed (not queued/pending)
      3. AuditLogEntry written with action = PAYMENT_APPROVED,
         delegation_tier = AGENT_LOGS, output_summary fields complete
      4. ClaimRecord.payment_amount set to computed value

  PAYMENT_CALCULATING → PENDING_HITL_EXCEPTION
    Trigger: ET-06 fires during T-09 (contract exception unresolved, or
      rate expired during calculation window)
    Guard: EscalationPacket written; payment_amount remains null

  PENDING_HITL_EXCEPTION → ADMIN_VALIDATING (HITL resolution path)
    Trigger: Exception processor resolves the discrepancy and requeues
    Guard: hitl_disposition non-null; human reviewer ID in updated_by

Transitions outside WS1 scope (defined in preamble, listed for
completeness — WS1 does not write these):
  RECEIVED → PARSING: Intake Agent
  PARSING → PARSE_FAILED / NORMALISED: Intake Agent
  PENDING_PHYSICIAN_REVIEW → CLINICAL_PACKET_ASSEMBLY: WS2
  CLINICAL_PACKET_ASSEMBLY → PHYSICIAN_REVIEWING / PENDING_ADDITIONAL_INFO: WS2
  PHYSICIAN_REVIEWING → APPROVED / REJECTED / PENDING_ADDITIONAL_INFO: Human + WS2
  APPROVED → CLOSED: Payment system confirmation
  REJECTED → CLOSED: Provider portal confirmation

Invalid transitions (WS1-relevant — in addition to those defined in preamble):

  PENDING_PHYSICIAN_REVIEW → APPROVED: FORBIDDEN
    Reason: T-09 (payment calculation) is architecturally blocked from
    executing against claims in PENDING_PHYSICIAN_REVIEW state (REQ-A-6).
    Enforcement mechanism: procedure-dependent until G-3 gap resolved;
    see §8 enforcement mechanism and FM-A-5 in §12.
    Any code path that produces this transition is a critical defect —
    not a runtime error to handle gracefully.

  ROUTING → PAYMENT_CALCULATING: FORBIDDEN
    Reason: Clinical content routing classification (T-08, REQ-A-1) is
    mandatory between ADMIN_VALIDATING and any payment path. A claim cannot
    skip T-08 under any condition. Skipping T-08 is a URAC/NCQA compliance
    event regardless of whether the claim was eventually classified as admin.

  ADMIN_VALIDATED → APPROVED: FORBIDDEN
    (also written ADMIN_VALIDATING → APPROVED)
    Reason: WS1 cannot short-circuit the pipeline. Every claim must pass
    through ROUTING (T-08 classification) before any payment path. This
    transition would skip the clinical routing gate.

  ADMIN_CLEARED → PHYSICIAN_REVIEWING: FORBIDDEN
    Reason: An ADMIN_CLEARED claim cannot enter the physician review path
    without re-running T-08 from ROUTING state. A direct transition would
    bypass the required ClinicalClassificationResult creation.

  APPROVED → PAYMENT_CALCULATING: FORBIDDEN
    Reason: APPROVED is terminal within the WS1 pipeline. Re-adjudication
    is not permitted; it requires a new claim submission with a new
    ClaimRecord.id.
```

---

## §11. Error Handling

All six required failure categories are present. Every row names a detection method.

| Failure | Detection method | Agent action | Human notification | Recovery path |
|---------|-----------------|--------------|-------------------|---------------|
| **Integration unavailable — S-02 (member eligibility)** | S-02 API returns HTTP 5xx or timeout after 5-second wait; retry fires after 5 seconds; second timeout or 5xx received | ClaimRecord.state → PENDING_HITL_EXCEPTION; EscalationPacket assembled with trigger_type = ELIGIBILITY_DISCREPANCY, trigger_signal_values = {error_type: "API_UNAVAILABLE", member_id, payer_id}; written to S-09 (ET-03); pipeline suspended for this claim | Ops alert via S-09 notification; exception processor notified within 2 minutes | Exception processor verifies S-02 availability; when confirmed, claim re-queued to ADMIN_VALIDATING; S-02 incident tracked in ops runbook |
| **Integration unavailable — S-05 (fee schedule)** | S-05 API returns HTTP 5xx or no rate found for (provider_npi, procedure_codes[0], payer_id); or rate_valid_through < today | ET-06 fires; ClaimRecord.state → PENDING_HITL_EXCEPTION; EscalationPacket with trigger_type = CONTRACT_EXCEPTION, trigger_signal_values = {error: "NO_RATE_FOUND" or "RATE_EXPIRED", provider_npi, procedure_codes, rate_valid_through} | Contract owner and VP Operations notified; daily breach summary if SLA triggered | Contract owner refreshes fee schedule; claims re-queued; T-09 retries against new version |
| **Integration unavailable — S-10 (audit log)** | S-10 API returns HTTP 5xx or timeout when T-11 attempts write; retry fires at 10-second interval | Agent queues AuditLogEntry locally (in-memory, max 50 records); retries every 10 seconds for up to 5 minutes; if still unavailable at 5 minutes, agent suspends claim processing and alerts ops; no claim reaches terminal state while S-10 unavailable | Ops alert immediately at first failure; escalation to ops lead at 5-minute threshold | Ops restores S-10; agent flushes queued entries in order; processing resumes |
| **Integration unavailable — S-08 (physician HITL queue)** | S-08 write returns HTTP 5xx or timeout; retry after 5 seconds; second failure | Agent retries once; on second failure, writes EscalationPacket to S-07 (claims management) with QUEUE_DELIVERY_FAILED flag; AuditLogEntry written with action = ESCALATION_DELIVERY_FAILED; ClaimRecord remains in PENDING_PHYSICIAN_REVIEW | Ops alert; VP Operations notified within 15 minutes | Ops confirms S-08 recovery; EscalationPacket re-delivered; QUEUE_DELIVERY_FAILED flag cleared |
| **Required data missing or malformed — ClaimRecord schema validation failure** | T-01 schema validator: required field absent, date format invalid, ICD-10 or CPT format mismatch, diagnosis_codes array empty | T-01 rejects the record; ClaimRecord.state → PENDING_HITL_EXCEPTION with hitl_queue_type = EXCEPTION_PROCESSOR; AuditLogEntry written with action = SCHEMA_VALIDATION_FAILED and the specific failed fields listed | Exception processor receives EscalationPacket with trigger_signal_values = {failed_fields: [...], record_excerpt}; VP Operations daily summary | Exception processor corrects or contacts submitter; corrected record re-submitted as new ClaimRecord |
| **Required data missing or malformed — ClinicalClassificationResult missing reasoning chain** | T-11 validates ClinicalClassificationResult before writing AuditLogEntry; checks reasoning_chain non-null and ≥ 20 characters | ET-07 fires; ClaimRecord.state → PENDING_HITL_EXCEPTION; partial AuditLogEntry written with available fields; reasoning chain absence flagged in trigger_signal_values | Ops alert; CMO notified if pattern recurs (> 1% of classifications in any hour) | Ops investigates classifier output; if systematic, CMO-authorised rerun of classification; reasoning chain backfilled by clinical reviewer for audit defence |
| **Agent confidence below threshold — T-08 returns ADMIN at confidence < CLINICAL_CONTENT_CONFIDENCE_THRESHOLD** | T-08 classification evaluates confidence_score < threshold_applied; ET-02 threshold comparison (§6 D-A-4, fourth branch) | ET-02 fires; ClaimRecord.state → PENDING_PHYSICIAN_REVIEW; EscalationPacket with escalation_trigger_id = ET-02, borderline_confidence_flag = true, confidence_score and threshold_applied values included; delivered to S-08; WS1 pipeline terminates | Physician HITL queue notified; ops dashboard BORDERLINE_CONFIDENCE count incremented | Physician reviewer determines routing (admin or clinical); claim proceeds on physician's decision; if borderline rate exceeds 5% of admin-path claims in a rolling 7-day window, CMO-triggered threshold review is initiated |
| **Governance hard stop triggered — T-09 invoked on non-ADMIN_CLEARED claim** | T-09 first operation: state pre-condition check reads ClaimRecord.state; any value other than ADMIN_CLEARED detected | T-09 aborts immediately (no external call made); ET-07 fires with trigger_signal_values = {error: "GOVERNANCE_HARD_STOP_T09", actual_state, expected_state: "ADMIN_CLEARED", claim_id}; ClaimRecord state unchanged; no payment_amount written | CMO and VP Operations notified within 15 minutes; agent pipeline suspended for this claim type; quality incident opened; all in-flight claims for the same claim type flagged for manual review | Root cause investigation before pipeline resumes; see FM-A-5 in §12 |
| **Duplicate or conflicting record detected** | T-01 schema validation: duplicate check query against S-07 for claims with identical (external_claim_id, member_id, date_of_service, provider_npi) combination | If duplicate found: ClaimRecord.state → PENDING_HITL_EXCEPTION; EscalationPacket with trigger_type = DUPLICATE_DETECTED, trigger_signal_values = {existing_claim_id, new_claim_id, match_fields}; duplicate record not advanced | Exception processor notified; daily duplicate summary to VP Operations | Exception processor determines original vs. resubmission; correct record advanced; duplicate closed |
| **SLA breach imminent** | ClaimRecord.sla_breach_flag field monitor: computed as sla_deadline − 172800 seconds (48 hours) reached; checked on every ClaimRecord state write | sla_breach_flag = true set on ClaimRecord; SLA_BREACH_IMMINENT event written to AuditLogEntry; Queue & SLA Management Agent (external to WS1) prioritises claim; no WS1 pipeline logic changes | VP Operations receives SLA breach imminent alert via daily dashboard; if claim is in HITL queue (PENDING_PHYSICIAN_REVIEW, PENDING_HITL_EXCEPTION), human reviewer is re-notified with URGENT flag | HITL reviewer expedites review; if claim is in WS1 pipeline, current step completes at normal priority (SLA management is the Queue Agent's responsibility, not WS1's) |

---

## §12. Failure Modes

**Distinct from §11.** These are wrong-output failures — the agent runs successfully but produces an incorrect or incomplete result. Integration failures are in §11 and are not repeated here.

---

```
Failure Mode FM-A-1: False routing — clinical claim misrouted as administrative
What bad output looks like: T-08 returns ADMIN with confidence_score ≥
  CLINICAL_CONTENT_CONFIDENCE_THRESHOLD for a claim that a clinical reviewer
  would classify as clinical. The claim is classified as ADMIN_CLEARED and
  proceeds to T-09 payment calculation and approval without physician review.

Consequence:
  - Immediate: Greenfield Health Systems issues a payment determination on a
    claim that required physician review under URAC/NCQA accreditation — a
    compliance event regardless of whether the payment amount is correct.
  - Downstream: The approved claim cannot be un-approved without a formal
    re-determination process. The member's benefit year counts the claim as
    adjudicated. The provider is paid without the required clinical review
    having been completed.
  - Business: URAC/NCQA audit exposure; potential accreditation penalty if
    the rate of uncaught clinical claims exceeds accreditation tolerance;
    medical-legal liability if the claim involved a procedure with an adverse
    outcome that should have had prior clinical scrutiny.

Detection:
  - Primary: Monthly 5% random audit sample of APPROVED claims — CMO-authorised
    clinical reviewer checks auto-approved claims for clinical content.
    Latency: up to 30 days post-approval (scenario: monthly cadence).
  - Secondary: Post-payment clinical review triggered by member appeal or
    provider dispute. Latency: 30–90 days.
  - Systematic indicator: If the monthly 5% audit catches ≥ 1 misrouted
    clinical claim, CMO initiates full recalibration.

Recovery path:
  1. CMO clinical reviewer classifies the caught claim as clinical.
  2. Claims ops team re-opens the ClaimRecord (APPROVED → new PENDING_PHYSICIAN_REVIEW
     via administrative re-determination process, not automated pipeline).
  3. Physician conducts belated clinical review.
  4. If original approval was correct on clinical grounds, record physician
     sign-off retroactively; if not, issue corrected determination.
  5. Compliance team documents the event; reports to URAC/NCQA if required.
  Responsibility: CMO (re-review); Claims Ops (re-determination); Compliance (reporting)
```

---

```
Failure Mode FM-A-2: Systematic confidence miscalibration — classifier
  underestimates clinical probability at scale
What bad output looks like: The Sonnet 4.6 classifier consistently returns
  ADMIN with confidence_score ≥ CLINICAL_CONTENT_CONFIDENCE_THRESHOLD for a
  specific procedure type or ICD chapter where claims actually require
  clinical review. Not a one-off misclassification (FM-A-1) but a systematic
  directional bias in the confidence output for a defined population of claims.

Consequence:
  - A population of clinical claims flows through the admin path.
  - Detection latency is high because each individual claim passes all
    per-claim checks; only aggregate analysis reveals the pattern.
  - Downstream: Multiple compliance events in a short window; potential
    URAC/NCQA audit trigger; retrospective clinical review of a batch
    of already-approved claims.

Detection:
  - Monthly 5% random audit: if ≥ 2 claims in one audit cycle from the same
    procedure code range are caught as clinical misroutes, CMO flags it as
    a potential systematic issue (not a one-off).
  - Population-level signal: Monitoring the monthly ratio of
    CLINICAL/UNCERTAIN escalations per CPT code range against historical
    base rates; a drop in escalation rate for a code range that previously
    produced CLINICAL routing is a systematic miscalibration signal.
    Latency: 30 days.

Recovery path — threshold retuning mechanism:
  1. CMO initiates emergency recalibration: new holdout set drawn specifically
     from the affected procedure code range (≥ 200 claims labelled by
     CMO-authorised reviewers within 5 business days).
  2. Threshold sweep re-run at 0.05 increments from 0.50 to 0.90 on the
     new holdout set.
  3. If recall on the new holdout falls below 0.995, the threshold is
     LOWERED to the highest value achieving ≥ 0.995 recall.
  4. New CalibrationRecord created with state = DRAFT; CMO signs to SIGNED;
     current SIGNED record transitions to SUPERSEDED.
  5. Agent restarted with new signed CalibrationRecord.
  6. All claims from the affected code range approved in the prior 30 days
     are placed in an expedited clinical review queue (manual retrospective
     review, not WS1 pipeline re-run).
  Responsibility: CMO (labelling, sign-off, retrospective review oversight);
    IT/MLOps (threshold sweep and model evaluation); Claims Ops (re-review queue)

  Note: "Re-run the audit" is not a complete recovery path. Threshold retuning
  is mandatory — the monthly audit confirms the problem; the retuning resolves it.
```

---

```
Failure Mode FM-A-3: Audit evidence incompleteness — approver cannot defend
  a determination if challenged
What bad output looks like: The agent issues an APPROVED or REJECTED
  ClaimRecord determination, or delivers an EscalationPacket, but the
  AuditLogEntry for that action is missing one or more of: reasoning_chain,
  confidence_score, input_summary.eligibility_result, input_summary.auth_result,
  delegation_tier, or compliance_flags. An auditor or regulator reviewing
  the record cannot reconstruct the basis for the determination.

What a complete output must contain (per §13 audit log schema):
  - timestamp (ISO 8601 with timezone)
  - agent_id (non-null)
  - action (from validated enum — PAYMENT_APPROVED, CLAIM_REJECTED, etc.)
  - entity_id (ClaimRecord.id, non-null)
  - input_summary: must include {eligibility_result, auth_result,
    plausibility_result, classification, confidence_score, threshold_applied}
    for APPROVED; {rejection_codes, reason_descriptions} for REJECTED;
    {escalation_trigger_id, trigger_signal_values} for escalations
  - output_summary: must include the state transition and all changed fields
  - delegation_tier: must be set (AGENT_ALONE / AGENT_LOGS / etc.)
  - compliance_flags: array (may be empty but must be present)
  - For APPROVED: confidence_score and reasoning_chain of the T-08
    ClinicalClassificationResult must be retrievable via
    clinical_classification_id (foreign key)

What the approver does if they receive an incomplete record:
  1. Do not proceed with the determination. Escalate ET-07 if the incomplete
     record is discovered in-flight.
  2. If discovered post-hoc (after APPROVED/REJECTED written), notify
     Compliance immediately; attempt to reconstruct from S-07 state history,
     system logs, and any partial AuditLogEntry fields present.
  3. If reasoning_chain is absent and cannot be reconstructed, treat the
     determination as undefended; initiate re-determination under CMO oversight.

Consequence:
  - Regulatory audit: any APPROVED claim without a complete audit trail is a
    HIPAA and URAC/NCQA compliance finding.
  - Provider dispute: if a REJECTED claim's AuditLogEntry lacks rejection reason
    descriptions, the provider cannot be given a meaningful explanation,
    violating prompt payment law requirements for denial reasons.

Detection:
  - ET-07 fires synchronously when T-11 detects a missing required field
    before the determination is issued (primary detection path).
  - Post-processing audit query (daily): counts claims in terminal state without
    a complete AuditLogEntry; should return 0.
  - Latency for ET-07 path: detected before the determination is issued.
  - Latency for post-processing path: up to 24 hours.

Recovery path:
  Responsibility: Compliance team (determination); IT (log reconstruction);
  Claims Ops (re-determination if unresolvable)
```

---

```
Failure Mode FM-A-4: Stale data input — agent acts on data that was current
  when retrieved but changed before the action was issued
What bad output looks like:
  Scenario A (eligibility): Member eligibility confirmed ACTIVE at T-02
  (retrieved 2026-04-15 09:00 UTC). Member's plan is terminated 2026-04-15
  09:30 UTC (system update in S-02). WS1 pipeline completes at 09:45 UTC
  and issues APPROVED. Payment is made to a provider for a claim by a
  now-ineligible member.

  Scenario B (fee schedule): Fee schedule rate retrieved at ADMIN_CLEARED
  transition. Rate version updated in S-05 between ADMIN_CLEARED and T-09
  execution (rate decreased by 15%). WS1 calculates payment using the higher
  stale rate.

  Scenario C (prior auth expiry): Prior auth retrieved as PRESENT_EXACT_MATCH
  at T-06. Prior auth expires during the WS1 pipeline window. T-09 issues
  payment against an expired prior auth.

Consequence:
  - Scenario A: Payment issued to an ineligible member — potential recovery
    action required; denial of benefits exposure.
  - Scenario B: Overpayment; financial recovery action required;
    VP Operations operational cost.
  - Scenario C: URAC/NCQA audit exposure for payment without current
    prior authorization.

Detection:
  - Scenario A: Post-payment eligibility reconciliation (daily batch, Claims Ops).
    Latency: up to 24 hours.
  - Scenario B: Rate reconciliation in payment processing (S-11 comparison to
    current fee schedule). Latency: 24–48 hours.
  - Scenario C: Prior auth audit query comparing payment dates to auth expiry dates.
    Latency: daily.

Recovery path:
  - For Scenario A: Claims Ops flags for benefit recovery; notifies member and
    provider of error; adjusts member's benefit record.
  - For Scenario B: Overpayment recovery process initiated by VP Operations;
    corrected payment issued.
  - For Scenario C: Clinical review of the post-expiry claim; retroactive
    prior auth request if procedure was medically necessary.

Mitigation (design): The pipeline reference data version check (REQ-A-8) at
  startup reduces stale reference risk for S-03 and S-05. Stale eligibility
  and prior auth data (Scenarios A and C) cannot be eliminated within WS1's
  pipeline scope — they require near-real-time event streaming from S-02 and
  S-04 (a Wave 2 integration enhancement, not a Wave 1 capability).
  Responsibility: Claims Ops (reconciliation); IT (event streaming roadmap)
```

---

```
Failure Mode FM-A-5: Governance hard stop bypass — PENDING_PHYSICIAN_REVIEW
  claim reaches T-09 payment calculation
What bad output looks like: A ClaimRecord in PENDING_PHYSICIAN_REVIEW state
  enters the T-09 input and WS1 calculates and issues a payment determination
  without physician review having been completed. The APPROVED record carries
  payment_amount and no ClinicalClassificationResult from a PHYSICIAN sign-off.

How this could occur (the bypass conditions):
  1. Agent code defect: REQ-A-6 pre-condition check in T-09 is missing,
     disabled, or evaluates the wrong field.
  2. S-07 API not enforcing state machine transitions at the API layer
     (G-3 gap — confirmed procedure-dependent in §8): a direct S-07 API
     call (not through WS1) writes ClaimRecord.state = ADMIN_CLEARED for
     a claim that was PENDING_PHYSICIAN_REVIEW, allowing T-09 to pass the
     pre-condition check on the next agent execution.
  3. Time pressure: An operator bypasses the queue directly in S-07 to clear
     a backlog, inadvertently advancing a claim that should be in physician
     review.
  4. Automated integration test that injects a manipulated ClaimRecord into
     the T-09 input queue (test harness misconfiguration, not confined to
     test environment).

Consequence:
  - A payment is issued for a procedure requiring physician review without
    the mandated clinical sign-off — a direct URAC/NCQA accreditation
    violation. Unlike FM-A-1 (a misclassification that may have been
    clinically defensible), FM-A-5 is a process bypass: no physician ever
    reviewed the claim.
  - Medical-legal: if the procedure was medically inappropriate and a
    payment was made, Greenfield faces potential fraud, waste, and abuse exposure.
  - Compliance: must be reported to URAC/NCQA under accreditation incident
    reporting requirements if discovered in audit; potential accreditation
    suspension.

Detection:
  - Primary (synchronous): REQ-A-6 pre-condition check in T-09 detects the
    wrong state and fires ET-07, aborting before any external call. This is
    the intended detection mechanism.
  - Secondary (asynchronous): Monthly verification query checking for
    AuditLogEntry records where action = PAYMENT_APPROVED AND the
    corresponding ClaimRecord has any prior ClinicalClassificationResult
    with call_site = ROUTING AND classification ∈ {CLINICAL, UNCERTAIN}
    at any point in its history (regardless of final routing). Should return 0.
  - Tertiary: G-3 discovery question to confirm whether S-07 enforces
    state transitions at the API layer; if not, bypass condition 2 is latent.
  - Latency: Condition 1 (code defect) — detected at next T-09 invocation.
    Condition 2 (S-07 direct write) — detected by monthly verification query
    (up to 30-day latency). Condition 3 (operator bypass) — same.

Recovery path:
  1. ET-07 fires; agent pipeline suspended for all claims; CMO and VP Operations
     notified within 15 minutes.
  2. Compliance team identifies all claims processed via the bypass (query
     APPROVED claims with PENDING_PHYSICIAN_REVIEW history since last clean
     verification query).
  3. Each bypass-approved claim undergoes retroactive physician clinical review.
  4. For claims where physician confirms approval: sign-off recorded retroactively
     in audit trail; URAC/NCQA incident reported.
  5. For claims where physician finds medical necessity issue: reversal process
     initiated.
  6. Root cause addressed: code defect patched (Condition 1); middleware guard
     added to S-07 integration (Condition 2, G-3 mitigation option 2); operator
     access to S-07 direct write reviewed (Condition 3).
  Responsibility: CMO (retrospective review); Compliance (reporting);
    IT (root cause and patch); VP Operations (operator access audit)

  This failure mode is a governance risk pending G-3 resolution.
  If G-3 confirms S-07 enforces state machine transitions at the API layer,
  bypass conditions 2 and 3 are eliminated; only condition 1 (code defect)
  remains, and it is already detected synchronously by REQ-A-6.
```

---

## §13. Audit and Governance

### Audit Log Schema

Every WS1 agent action produces an AuditLogEntry using the shared entity definition in `D4_preamble_capability_spec.md` §2. The full field list is restated here with WS1-specific enum values and field constraints.

```json
{
  "id": "UUID — primary key, immutable, generated on creation",
  "timestamp": "ISO 8601 with timezone — UTC; set at write time; immutable",
  "agent_id": "string — WS1 agent instance identifier; non-null; format: 'ws1-adj-{instance_uuid}'",
  "action": "enum — exhaustive list of all WS1 action values:
    CLAIM_INTAKE_VALIDATED,
    CLAIM_STATE_TRANSITION,
    ELIGIBILITY_CONFIRMED,
    ELIGIBILITY_CORRECTED,
    ELIGIBILITY_ESCALATED,
    CODE_VALIDITY_CHECKED,
    CODE_PLAUSIBILITY_ASSESSED,
    PRIOR_AUTH_CONFIRMED,
    PRIOR_AUTH_TOLERANCE_APPLIED,
    PRIOR_AUTH_ESCALATED,
    CLINICAL_CLASSIFICATION_COMPLETED,
    CLINICAL_ESCALATED_ET01,
    CLINICAL_ESCALATED_ET02,
    PAYMENT_APPROVED,
    CLAIM_REJECTED,
    ESCALATION_TRIGGERED,
    ESCALATION_DELIVERED,
    ESCALATION_DELIVERY_FAILED,
    SCHEMA_VALIDATION_FAILED,
    GOVERNANCE_HARD_STOP_TRIGGERED,
    AUDIT_LOG_QUEUED_LOCAL,
    REFERENCE_DATA_EXPIRED,
    STARTUP_CALIBRATION_CHECK_PASSED,
    STARTUP_CALIBRATION_CHECK_FAILED",
  "entity_type": "string — 'ClaimRecord' | 'ClinicalClassificationResult' |
    'EscalationPacket' | 'CalibrationRecord'",
  "entity_id": "UUID — foreign key to the entity being logged; non-null",
  "input_summary": "object — key fields used to make the decision:
    For ELIGIBILITY_CONFIRMED: {member_id, payer_id, date_of_service, eligibility_status}
    For CODE_VALIDITY_CHECKED: {codes_checked: count, invalid_codes: array}
    For PRIOR_AUTH_TOLERANCE_APPLIED: {authorized_units, claimed_units, pct_excess,
      PRIOR_AUTH_UNIT_TOLERANCE_PCT}
    For CLINICAL_CLASSIFICATION_COMPLETED: {classification, confidence_score,
      threshold_applied, threshold_met, signal_diagnosis_codes, signal_procedure_codes,
      signal_provider_specialty}
    For PAYMENT_APPROVED: {contracted_rate, cost_sharing_proportion, contract_exception_flag,
      rate_version}
    For CLAIM_REJECTED: {rejection_codes, reason_descriptions}
    For ESCALATION_TRIGGERED: {escalation_trigger_id, trigger_signal_values}",
  "output_summary": "object — what changed:
    For CLAIM_STATE_TRANSITION: {from_state, to_state, hitl_queue_type (if applicable)}
    For PAYMENT_APPROVED: {payment_amount, provider_npi, s11_confirmation_id}
    For CLAIM_REJECTED: {rejection_codes, resubmission_guidance}
    For ESCALATION_DELIVERED: {escalation_packet_id, target_queue, delivery_confirmed: boolean}",
  "delegation_tier": "enum [AGENT_ALONE, AGENT_LOGS, AGENT_PROPOSES, HUMAN_DECIDES] —
    non-null; AGENT_ALONE for binary rule decisions; AGENT_LOGS for tolerance approvals
    and payment approvals; HUMAN_DECIDES for HITL escalations",
  "human_id": "UUID or null — set when a human is the acting party (HITL resolution);
    null for all fully agentic actions; must be set for any action with
    delegation_tier = HUMAN_DECIDES",
  "confidence_score": "float 0.000–1.000 or null — non-null for T-08 (clinical classification)
    and T-05 (Haiku plausibility); null for binary rule-based decisions",
  "escalation_triggered": "boolean — true if this log entry corresponds to an ET-01
    through ET-07 trigger; false otherwise",
  "compliance_flags": "array of strings — zero or more values from:
    URAC_NCQA_CLINICAL_GATE (any PENDING_PHYSICIAN_REVIEW transition),
    BORDERLINE_CONFIDENCE (ET-02 trigger),
    RETRIEVAL_THRESHOLD_NOT_MET (S-15 below threshold),
    TOLERANCE_APPLIED (PRIOR_AUTH_UNIT_TOLERANCE_PCT applied),
    CONTRACT_EXCEPTION_APPLIED,
    REFERENCE_DATA_EXPIRED,
    GOVERNANCE_HARD_STOP_TRIGGERED — empty array [] is valid; null is not"
}
```

---

### Retention

| Log type | Retention period | Basis |
|----------|-----------------|-------|
| Compliance logs — all AuditLogEntry records for APPROVED, REJECTED, PENDING_PHYSICIAN_REVIEW state transitions; all CLINICAL_CLASSIFICATION_COMPLETED records | 7 years from ClaimRecord.created_at | HIPAA 45 CFR § 164.530(j) — covered entity must retain documentation for 6 years from creation date or last effective date; 7-year standard provides one year buffer; state regulations (e.g., California, New York) impose up to 7-year requirements |
| Operational logs — agent startup/shutdown events, reference data version checks, S-10 queue flush events, API retry events | 90 days from event timestamp | Operational troubleshooting; no regulatory requirement beyond reasonable retention for incident investigation |
| Audit trail — all AuditLogEntry records regardless of type (superset of compliance logs) | 7 years from ClaimRecord.created_at | Same basis as compliance logs; the audit trail is a superset and the longest retention applies |
| CalibrationRecord — signed calibration artefacts | 7 years from CalibrationRecord.cmo_signoff_date | URAC/NCQA accreditation: calibration evidence must be available for accreditation audits; 7-year standard consistent with HIPAA documentation retention |
| EscalationPacket records | 7 years from EscalationPacket.created_at | Any HITL decision in the escalation path is a covered clinical workflow record; same 7-year basis |

---

### HITL Checkpoints

| Checkpoint | Trigger condition | Notified party | Required response | SLA | If SLA breached |
|------------|-------------------|----------------|-------------------|-----|-----------------|
| CP-A-1: Clinical routing review (ET-01) | T-08 returns CLINICAL or UNCERTAIN at any confidence level; ClaimRecord enters PENDING_PHYSICIAN_REVIEW | CMO-authorised physician or advanced practice provider via S-08 physician HITL queue | Physician records a signed approval token in S-08 with one of: APPROVED (proceed to payment), REJECTED (denial with reason codes), or ADDITIONAL_INFO_REQUIRED (return to PENDING_ADDITIONAL_INFO). A free-text note is permitted but does not substitute for the structured token. | 4 hours from EscalationPacket.created_at | SLA_BREACHED flag set on EscalationPacket; escalation re-delivered with URGENT flag to senior physician reviewer; VP Operations and CMO notified within 15 minutes; daily SLA breach log generated |
| CP-A-2: Borderline confidence routing review (ET-02) | T-08 returns ADMIN with confidence_score < CLINICAL_CONTENT_CONFIDENCE_THRESHOLD; ClaimRecord enters PENDING_PHYSICIAN_REVIEW | CMO-authorised physician or advanced practice provider via S-08 | Physician records structured token: CONFIRMED_ADMIN (claim may proceed through WS1 pipeline from ADMIN_CLEARED state) or RECLASSIFIED_CLINICAL (claim remains PENDING_PHYSICIAN_REVIEW, proceeds via WS2). Physician may not record ADDITIONAL_INFO_REQUIRED for ET-02 cases — this is a routing decision, not a clinical determination. | 4 hours from EscalationPacket.created_at | Same as CP-A-1 breach action |
| CP-A-3: Eligibility discrepancy exception (ET-03) | Eligibility discrepancy not resolvable by deterministic correction rule, or S-02 unavailable after retry; ClaimRecord enters PENDING_HITL_EXCEPTION | HITL exception processor via S-09 exception management system | Exception processor records one of: ELIGIBILITY_CONFIRMED (member eligibility manually verified — state advanced to ROUTING), ELIGIBILITY_REJECTED (claim denied — state to REJECTED with INELIGIBLE_MEMBER rejection code), RETURN_TO_SUBMITTER (insufficient information — EscalationPacket forwarded to submitter). | 2 hours from EscalationPacket.created_at | Exception processor supervisor notified; claim re-tagged URGENT in exception queue; SLA breach event written to AuditLogEntry |
| CP-A-4: Prior auth or coding exception (ET-04, ET-05) | Prior auth mismatch exceeding tolerance (ET-04), or coding implausibility above threshold (ET-05) | ET-04 → HITL exception processor; ET-05 → HITL coding specialist | For ET-04: exception processor records PRIOR_AUTH_CONFIRMED (manual verification), PRIOR_AUTH_DENIED, or RETURN_TO_SUBMITTER. For ET-05: coding specialist records CODING_CONFIRMED_PLAUSIBLE, CODING_CONFIRMED_IMPLAUSIBLE (proceed to rejection), or RETURN_TO_SUBMITTER. | 2 hours from EscalationPacket.created_at | Supervisor notified for both ET-04 and ET-05; URGENT flag; SLA breach event logged |
| CP-A-5: Contract exception / fee schedule anomaly (ET-06) | Contract clause outside validated reference set, fee schedule no-rate-found, or reference data expired; ClaimRecord enters PENDING_HITL_EXCEPTION | HITL exception processor (primary); CONTRACT_OWNER for amendment_flag = true cases | Exception processor and contract owner record one of: EXCEPTION_RESOLVED (correct rate confirmed — claim advanced to PAYMENT_CALCULATING with correct rate), CLAIM_REJECTED (no valid contract basis), RETURN_TO_SUBMITTER. Contract owner must countersign for any case with amendment_flag = true. | 4 hours from EscalationPacket.created_at | Contract owner notified via secondary alert channel; claim remains in PENDING_HITL_EXCEPTION; VP Operations notified; daily breach summary generated |

---

### Compliance Constraints

| Framework | Specific requirement for this agent |
|-----------|-------------------------------------|
| **HIPAA — 45 CFR Part 164 (Security and Privacy)** | All ClaimRecord data and AuditLogEntry records constitute Protected Health Information (PHI). The agent must transmit to and from S-02, S-04, S-05, S-07, S-08, S-09, S-10, S-11, S-12, S-15, S-16 only over encrypted channels (TLS 1.2 minimum). The minimum-necessary principle applies: the agent reads only the fields required for each pipeline step — it does not retrieve full medical records or claims history beyond the current adjudication record. AuditLogEntry records must be retained 7 years per §13 Retention above. |
| **URAC/NCQA Accreditation Standards — Clinical Review** | A physician or advanced practice provider must review and sign off on every claim involving clinical content before a payment determination is issued. This is the primary driver of the PENDING_PHYSICIAN_REVIEW state and the ET-01/ET-02 escalation design. The agent must never issue payment_amount for any claim where the ClinicalClassificationResult for that claim (call_site = ROUTING) was CLINICAL or UNCERTAIN at any confidence level, regardless of any subsequent override attempt. The CMO-labelled calibration process (CalibrationRecord, §3) is specifically designed to demonstrate to accreditation auditors that the clinical content classifier meets the recall threshold required for this standard. |
| **Prompt Payment Laws — State Insurance Regulations** | Most US states require insurers to process clean electronic claims within 30–45 days of receipt (e.g., California Insurance Code §10123.13: 30 days; New York Insurance Law §3224-a: 30 days). The WS1 agent's 5-day cycle time target (§0 KPI) must be achieved in the context of a 30-day legal maximum. The agent must set sla_deadline correctly on every ClaimRecord (created_at + 604800 seconds = 7 days per internal SLA) and the Queue & SLA Management Agent uses this field to prioritise processing ahead of the statutory deadline. |
| **ICD-10-CM / CPT Coding Standards** | The agent's code validity check (T-04) must use current-year ICD-10-CM and CPT code tables licensed for payer use. The agent must never apply a procedure or diagnosis code from an expired reference as valid. The reference data version check at startup (REQ-A-8) and the expired-reference routing to ET-06 are the implementation of this standard. |
| **CMS Claims Adjudication Requirements** | For Medicare Advantage claims (if any portion of the Greenfield claims population is Medicare Advantage — not confirmed in scenario [Assumption A-D4a-5, Low confidence]): CMS requires documentation of prior authorisation decisions and medical necessity determinations. The AuditLogEntry compliance_flags array and the URAC/NCQA_CLINICAL_GATE flag are the implementation mechanism for this requirement. The CalibrationRecord and reasoning_chain in ClinicalClassificationResult are designed to satisfy CMS audit documentation standards. |
| **State Insurance Fraud, Waste, and Abuse (FWA) Requirements** | The coding plausibility assessment (T-05) and the duplicate detection check (§11) are partial compliance implementations for FWA prevention requirements imposed by state insurance departments and CMS (for MA claims). The AuditLogEntry records for both steps provide the audit trail required by FWA investigation processes. |

---

## §14. Spec Ambiguity Register

| Item | Type | Confidence | Description | Impact if unresolved | Resolution |
|------|------|------------|-------------|----------------------|------------|
| A-D4a-1 | Spec ambiguity | Low | **S-06 contract document store — API availability unconfirmed (SCOPE-OUT).** The contract document store referenced in §2 (inputs), §4 T-10, §6 D-A-6, and §1 out-of-scope justification for contract exception rule encoding is not named in the scenario. No API, vendor, format, or availability information is known. The D4 integration preamble §2 classifies this as gap G-2 (Blocking severity for WS1-JtD-3 full automation). | If S-06 does not have a machine-readable API, T-10 contract exception handling (D-A-6 first branch) fires for every claim with a contract exception flag: all such claims route to ET-06 and PENDING_HITL_EXCEPTION. WS1-JtD-3 (full payment path automation) is partially blocked. Builder would need to implement the D-A-6 SCOPE-OUT stub behaviour (ET-06 on every T-10 call) and cannot build the post-G-2-resolution branch. | Discovery action (from integration preamble G-2): Ask Greenfield IT: "Does a machine-readable contract document store exist, and does it have an API? If not, what is the authoritative source for payer-provider contract exceptions?" Resolution owner: IT/VP Operations. Until resolved: builder implements D-A-6 SCOPE-OUT stub behaviour only. |
| A-D4a-2 | Spec ambiguity | Low | **S-15 medical necessity criteria — vector store API availability unconfirmed (SCOPE-OUT).** The medical necessity criteria system used for T-08 retrieval augmentation and T-05 novel combination assessment is not named in the scenario. The integration preamble §2 classifies this as gap G-6. T-08 and T-05 degrade to classifier-only operation when S-15 is unavailable, which may affect recall (especially for novel code combinations). | Without S-15 retrieval augmentation: T-08 operates on classifier signal only — recall at the CMO-certified threshold is unconfirmed. The CalibrationRecord hold-out set process at §0 will need to be run without augmentation, which may require a higher or lower threshold. T-05 novel code combination assessment reverts to structured table lookup only (less coverage). Builder would need to implement T-08 and T-05 without the retrieval path and ensure the CalibrationRecord calibration sweep accounts for non-augmented operation. | Discovery action: Ask Greenfield IT and CMO: "Does an electronic medical necessity criteria source exist (e.g., InterQual, MCG Health)? Is there an API or vector-indexable document set?" Resolution owner: CMO / IT. Until resolved: builder implements T-08 without S-15 retrieval; threshold calibration must be run on non-augmented operation; compliance_flags += ["RETRIEVAL_THRESHOLD_NOT_MET"] on every T-08 call. |
| A-D4a-3 | Design gap | Medium | **Auto-adjudication rate baseline — admin-path-only baseline not measured.** §0 KPI states "22% across all claim types" as the current auto-adjudication rate baseline, sourced from scenario.md. However, this is the all-claims baseline; the admin-path-only baseline (the relevant denominator for the ≥80% target) is not measured separately. The 80% target is the design intent but cannot be validated against a baseline before go-live. | Builder cannot establish a pre-deployment baseline for this KPI. The ≥80% target may be conservative or aggressive depending on the actual composition of the admin-path claim population. If the baseline auto-adjudication rate for admin-path claims is already 60–70%, the target is easily achievable; if it is near the 22% all-claims figure, the target requires significant exception reduction beyond the agent's core pipeline. | Discovery action: Ask Claims Ops (VP Operations): "Of the current 22% auto-adjudication rate, what percentage applies to claims that would be classified as administrative under the proposed routing criteria? Can this be measured from existing claims data?" Confidence will remain Low until this is measured. For go-live planning, the FDE should confirm this data is retrievable before agreeing the ≥80% target as a performance SLA. |
| A-D4a-4 | Spec ambiguity | Low | **G-3 gap — S-07 claims management platform does not confirm state machine enforcement at the API layer.** §8 enforcement mechanism classifies the PENDING_PHYSICIAN_REVIEW → payment path block as procedure-dependent until G-3 is resolved. The integration preamble §2 gap G-3 discovery action asks Greenfield IT whether S-07 rejects state transition writes that violate the defined state machine. This is the foundational sign-off integrity risk for the governance hard stop. | If S-07 does not enforce state machine transitions, the PENDING_PHYSICIAN_REVIEW → payment bypass (FM-A-5) becomes a latent risk addressable only by the middleware guard (G-3 mitigation option 2). Builder must implement REQ-A-6 as the primary control, and the middleware guard as a recommended second layer; the spec cannot rely on S-07 as a system-enforced barrier until confirmed. §8 classification and FM-A-5 severity both depend on this answer. | Discovery action: Ask Greenfield IT: "Does the claims management platform (S-07) enforce state machine transition rules at the API layer — specifically, does it return a 4xx error if a write request attempts a transition that is not permitted from the current state?" If yes: update §8 to system-enforced, reduce FM-A-5 severity. If no: implement G-3 mitigation option 2 (middleware state transition guard). Resolution owner: IT. |
| A-D4a-5 | Design gap | Low | **Medicare Advantage population — not confirmed in scenario.** §13 compliance constraints reference CMS claims adjudication requirements with a note that the MA claim population is unconfirmed. If Greenfield's claims include Medicare Advantage, additional CMS regulatory requirements apply (prior auth documentation, medical necessity standards, appeal rights). The scenario does not specify Greenfield's lines of business beyond "health insurance payer." | If MA claims are in scope: additional compliance requirements apply that are not fully captured in §13. The audit trail design (particularly reasoning_chain storage for T-08) would need to explicitly satisfy CMS audit standards. The rejection code set may need CMS-specific codes. Builder would need to add a plan_type field to ClaimRecord and branch compliance_flags logic based on plan_type. | Discovery action: Ask Greenfield (CFO/CMO): "Does Greenfield Health Systems administer Medicare Advantage plans? If so, what proportion of the 2,000 claims/day are MA claims?" Confidence will remain Low until confirmed. For MVP design: treat as commercial payer only; add plan_type to ClaimRecord as a Wave 2 enhancement if MA confirmed. |

*Pass 4 complete. Pass 5a begins Spec B (WS2) in `Deliverables/D4b_capability_spec.md`.*


---

# D4b — Capability Specification: Spec B
## WS2 Clinical Review Support Agent
### Greenfield Health Systems: Medical Claims Adjudication Transformation

*Source inputs: `Deliverables/D4_preamble_capability_spec.md` (Pass 1), `Deliverables/D4_integration_preamble.md` (Pass 2), `Deliverables/D3_agentic_solution_architecture.md`, `Deliverables/D4_agent_purpose_document.md`, `Deliverables/D4a_capability_spec.md` (cross-spec consistency reference), `Scenario/scenario_context.md`. Every design decision traces to one of these inputs or is flagged as an assumption.*

*Pass 5a covers §0–§4. Pass 5b appends §5–§8. Pass 6 appends §10–§14.*

---

## §0. Agent Identity

- **Agent name:** WS2 Clinical Review Support Agent
- **Job to be Done:** Receive claims in `PENDING_PHYSICIAN_REVIEW` state from WS1, verify that each was correctly classified as clinical using a second-pass application of the shared clinical content classifier, and assemble a complete pre-filled physician review packet — combining routing verification result, prior auth history, member claims history, and retrieved clinical notes — so that CMO-authorised physicians can make a medical necessity determination on complete, auditable evidence without manual document hunting, reducing physician decision time and protecting against incomplete-packet determinations.
- **D3 reference:** D3 §2 Agent 3 — "Clinical Review Support Agent"
- **Delegation archetype:** Agent-led + Human Oversight — consistent with D3 autonomy matrix; the agent verifies routing and assembles context autonomously and escalates to HITL when verification confidence is below threshold, when documentation retrieval is incomplete, or when the physician flags the assembled packet as insufficient.

**KPIs:**

| KPI | Baseline | Target | How measured | Review cadence |
|-----|----------|--------|--------------|----------------|
| Routing verification classification agreement rate (% of WS2 verifications that confirm WS1's CLINICAL/UNCERTAIN routing — i.e., WS2 also returns CLINICAL at confidence ≥ `CLINICAL_CONTENT_VERIFICATION_THRESHOLD`) | Not measured — all claims currently manual; WS1 routing does not yet exist | < 1% disagreement rate — WS2 and WS1 disagree on more than 1% of verified claims is a calibration signal requiring CMO review [Assumption A-D4b-1] | Count of ClinicalClassificationResult pairs where call_site = ROUTING classification ≠ call_site = VERIFICATION classification (at or above their respective thresholds), divided by total WS2 verifications per week; from AuditLogEntry | Weekly; if weekly disagreement rate exceeds 1%, CMO review initiated |
| WS2 routing verification HITL rate (% of clinical-path claims triggering BP-WS2-1 — below verification threshold) | Not measured | < 10% of clinical-path claims entering BP-WS2-1 escalation [Assumption A-D4b-2] | Count of EscalationPackets with trigger_type = ROUTING_VERIFICATION_BELOW_THRESHOLD ÷ total WS2 claims processed per week | Weekly |
| Packet completeness rate — Wave 2 (% of physician review packets with completeness_indicator = 1.000, meaning all required context elements retrieved) | Not applicable in Wave 1 (S-13 clinical notes SCOPE-OUT); Wave 1 baseline = completeness_indicator reflects prior auth + claims history only | ≥ 85% complete packets when S-13 accessible (Wave 2 target) [Assumption A-D4b-4] | Count of PhysicianReviewPackets with completeness_indicator = 1.000 ÷ total packets delivered; from S-08 delivery log and AuditLogEntry | Weekly (Wave 2) |
| Time to packet delivery (elapsed minutes from ClaimRecord.state = PENDING_PHYSICIAN_REVIEW to PhysicianReviewPacket delivered to S-08) | Not measured — current process is manual chart pull by physician; estimated 30–45 minutes per claim (no scenario reference — [Assumption A-D4b-5]) | ≤ 30 minutes from PENDING_PHYSICIAN_REVIEW to delivery confirmation | Timestamp delta: ClaimRecord state transition to PENDING_PHYSICIAN_REVIEW vs. AuditLogEntry with action = PACKET_DELIVERED | Daily |
| Additional information request cycle time (days from PENDING_ADDITIONAL_INFO to provider documentation received and re-queued) | Not measured | ≤ 5 business days [Assumption A-D4b-6] | Timestamp delta: ClaimRecord.state = PENDING_ADDITIONAL_INFO to re-queue action; from S-07 | Weekly; breach alert at day 3 |

**Confidence threshold validation — pre-deployment requirement:**

`CLINICAL_CONTENT_VERIFICATION_THRESHOLD` (default 0.85, CMO-certified — see §3 and assumption A-D4b-3) must be calibrated independently from `CLINICAL_CONTENT_CONFIDENCE_THRESHOLD` (WS1's routing threshold), per D3 ADR-2 consequence: the architecture must support two separately configurable thresholds on the same underlying model. Before deployment:
1. The same CMO-labelled holdout set used for WS1 calibration (≥500 claims) is used as the validation set for WS2 verification threshold calibration.
2. The classifier is run at `call_site = VERIFICATION` against the holdout set across threshold values 0.50 to 0.95 in 0.05 increments.
3. Threshold is set at the lowest value achieving ≥99.5% recall of genuinely clinical claims at the VERIFICATION call site (same recall standard as WS1 routing).
4. The calibration result is stored as a separate signed `CalibrationRecord` (defined in D4a §3) with `classifier_version` matching the deployed classifier and CMO sign-off date non-null before go-live. The WS2 agent refuses to start if no valid `CalibrationRecord` for the VERIFICATION call site is present.

**Note:** If D3 ADR-2 revisit condition is triggered (calibration reveals that WS1 and WS2 optimal thresholds materially conflict), the CalibrationRecord schema already supports this: `threshold_value` and `recall_achieved` are independent per record, and WS1 and WS2 may reference different CalibrationRecords.

- **Governance hard stop:** This agent MUST NOT produce, approximate, or pre-fill a medical necessity determination. The pre-filled review packet is an input to the physician's judgment — it is not a recommendation, a provisional determination, or a pre-filled answer to the medical necessity question. Packet completeness must be explicitly surfaced to the physician as a `completeness_indicator` value and `completeness_flags` array before physician review begins. A physician making a determination on an incomplete packet without knowing it is incomplete violates the quality standard this agent exists to support. If the physician is not informed that documentation is missing, any resulting determination is undefended.

---

## §1. Purpose and Scope

**Purpose statement:** The WS2 Clinical Review Support Agent solves the physician review inefficiency in Greenfield Health Systems' clinical claims path — where claims arriving in the physician review queue require physicians to manually retrieve prior authorisation history, clinical notes, member history, and applicable medical necessity criteria before making a determination, consuming 30–45 minutes of physician time per claim in document hunting rather than clinical judgment (Assumption A-D4b-5). The agent receives claims in `PENDING_PHYSICIAN_REVIEW` state, runs a second-pass verification classification to confirm the routing is correct, assembles all available clinical context into a structured review packet, and delivers it to the physician HITL queue with an explicit completeness indicator. It does not make medical necessity determinations, does not approve or deny claims, and does not take any action that reduces the physician's authority to review the full assembled context before recording a determination.

**In scope:**
- Receiving `ClaimRecord` objects in `PENDING_PHYSICIAN_REVIEW` state from S-07 and initiating the WS2 pipeline
- Routing verification classification using the shared clinical content classifier (Sonnet 4.6) with `call_site = VERIFICATION`, producing a `ClinicalClassificationResult` with `call_site = VERIFICATION` — T-B-02
- Escalation to HITL routing review (BP-WS2-1) when routing verification confidence is below `CLINICAL_CONTENT_VERIFICATION_THRESHOLD` or when classifier returns `ADMIN` (contradicting WS1's routing) — T-B-02
- Prior authorisation history retrieval for the member + procedure type from S-04 — T-B-03
- Member claims history retrieval from S-14 for the relevant diagnosis cluster and configurable lookback period — T-B-04
- Clinical notes retrieval from S-13 (Wave 2 capability — SCOPE-OUT in Wave 1; see §14 A-D4b-1) — T-B-05
- Medical necessity criteria retrieval from S-15 RAG index for the applicable procedure code range and ICD chapter (SCOPE-OUT until confirmed — see §14 A-D4b-2) — T-B-06
- Packet completeness assessment: computing `completeness_indicator` (float 0.000–1.000) and `completeness_flags` array identifying missing elements — T-B-07
- Pre-filled physician review packet assembly and delivery to S-08, with completeness indicator and all retrieved context — T-B-08
- Flagging incomplete packets (BP-WS2-2) to physician via structured `completeness_flags` array before review begins — T-B-07/T-B-08
- Drafting an additional information request to the provider when physician flags the assembled packet as insufficient (physician-triggered) — T-B-09
- Writing `ClaimRecord` state transitions to S-07 (PENDING_PHYSICIAN_REVIEW → CLINICAL_PACKET_ASSEMBLY → PHYSICIAN_REVIEWING; and → PENDING_ADDITIONAL_INFO on physician flag)
- Appending `AuditLogEntry` records to S-10 for every pipeline step, every packet delivery, and every state transition
- Re-triggering context assembly from `CLINICAL_PACKET_ASSEMBLY` state when provider supplies missing documentation and Queue Agent re-queues the claim

**Out of scope:**
- Medical necessity determination (approve / deny / pend) — regulatory hard stop: URAC/NCQA accreditation requires a licensed physician or advanced practice provider to make all clinical determinations; no agent confidence level or completeness metric changes this assignment (D3 §1 WS2-JtD-3, D3 §5)
- Payment calculation — WS1 handles the administrative path; physician records a determination token in S-08; the payment step downstream of physician approval is handled by the payment processing system, not WS2
- Claim intake and normalisation — handled upstream by the Intake & Anomaly Agent (D3 §2 Agent 1); WS2 receives only `ClaimRecord` objects in `PENDING_PHYSICIAN_REVIEW` state
- Rejection notice generation — WS2 does not generate provider rejection notices; that output is created by the physician's denial determination token in S-08 and formatted by the Queue & SLA Management Agent
- Queue prioritisation and SLA management across all clinical-path claims — handled by the Queue & SLA Management Agent (D3 §2 Agent 4); WS2 monitors its own delivery SLA (time to packet delivery) but does not manage the global queue
- Routing the claim back to the administrative path after WS2 verification — any case where WS2 routing verification returns `ADMIN` (contradicting WS1's routing) routes to HITL exception processor via BP-WS2-1; WS2 does not autonomously reroute to the admin pipeline (this would require a full re-run of T-07/T-08/T-09, which is WS1's pipeline)
- Appeal processing — Wave 3 deferral (D3 §5); appeals involving clinical content require the same physician sign-off constraint
- Wave 2 capabilities until S-13 API availability is confirmed: clinical notes retrieval, full completeness_indicator computation including notes presence, additional information request based on missing clinical notes

---

## §2. Inputs and Outputs

**Inputs:**

| Input | Source system | Format | Required / Optional | Validation rule |
|-------|---------------|--------|---------------------|-----------------|
| ClaimRecord in PENDING_PHYSICIAN_REVIEW state | S-07 Claims management system (internal queue) | `ClaimRecord` JSON object in `PENDING_PHYSICIAN_REVIEW` state; `clinical_classification_id` non-null; `hitl_queue_type = PHYSICIAN_REVIEW` | Required | `ClaimRecord.state = PENDING_PHYSICIAN_REVIEW`; `clinical_classification_id` non-null; linked `ClinicalClassificationResult` with `call_site = ROUTING` and `state = CLASSIFIED` readable from S-07; `sla_deadline` non-null and in the future |
| ClinicalClassificationResult from WS1 routing (call_site = ROUTING) | S-07 (via ClaimRecord.clinical_classification_id foreign key) | `ClinicalClassificationResult` JSON object with `call_site = ROUTING`, `state = CLASSIFIED`, `reasoning_chain` non-null and ≥ 20 characters | Required | `call_site = ROUTING`; `classification ∈ {ADMIN, CLINICAL, UNCERTAIN}`; `confidence_score` non-null; `reasoning_chain` ≥ 20 characters; `calibration_record_id` non-null and references a `CalibrationRecord` with `state = SIGNED` |
| Medical necessity criteria chunks | S-15 Medical necessity criteria system | Vector store chunks tagged by `procedure_code_range`, `icd_chapter`, source document `version_id`, chunk `expiry_date` | Optional — SCOPE-OUT until confirmed; see §14 A-D4b-2 | Cosine similarity ≥ 0.75 for T-B-02 verification retrieval and T-B-08 packet criteria section; chunks past `expiry_date` excluded; if no chunk reaches threshold, `completeness_flags += ["CRITERIA_SECTION_UNAVAILABLE"]` |
| Prior authorisation history | S-04 Prior authorisation system | PA history query response for `member_id + procedure_code_range + configurable lookback period (default 12 months)`; array of prior auth records, each with: `auth_record_id`, `procedure_code`, `authorized_units`, `start_date`, `expiry_date`, `prior_auth_status` | Required | At least one prior auth query attempted; S-04 unavailable after retry → `completeness_flags += ["PRIOR_AUTH_HISTORY_UNAVAILABLE"]`; packet delivered without prior auth history |
| Member claims history | S-14 Claims history database | Claims history query response for `member_id + diagnosis_code_range (ICD chapter) + lookback_period_days (default 365)`; array of prior claim summaries: `claim_id`, `date_of_service`, `procedure_codes`, `diagnosis_codes`, `state` (terminal), `payment_amount` | Required | At least one history query attempted; S-14 unavailable after retry → `completeness_flags += ["CLAIMS_HISTORY_UNAVAILABLE"]`; packet delivered without history |
| Clinical notes | S-13 Clinical notes source system | Provider clinical notes for this member + episode: treatment notes, operative reports, lab results in supported format (FHIR Bundle, CDA, or structured text) | Required for Wave 2 completeness — SCOPE-OUT in Wave 1; see §14 A-D4b-1 | In Wave 1: S-13 SCOPE-OUT; `completeness_flags += ["CLINICAL_NOTES_SCOPE_OUT"]`; `clinical_notes_available = false` on every packet. In Wave 2: FHIR or CDA format only; S-13 unavailable after retry → `completeness_flags += ["CLINICAL_NOTES_UNAVAILABLE"]` |
| Signed calibration artefact (VERIFICATION call site) | S-16 Configuration management system | `CalibrationRecord` JSON object (defined in D4a §3) with `classifier_version` matching deployed classifier | Required — loaded at agent startup | `CalibrationRecord.state = SIGNED`; `cmo_signoff_date` non-null; `recall_achieved ≥ 0.995`; `holdout_set_size ≥ 500`; `classifier_version` matches current deployed classifier; agent refuses to start if any condition fails |

**Outputs:**

| Output | Target system / recipient | Format | Trigger condition |
|--------|---------------------------|--------|-------------------|
| PhysicianReviewPacket | S-08 Physician review queue interface | `PhysicianReviewPacket` JSON object (see §3); includes: `ClinicalClassificationResult` from WS1 (ROUTING) and WS2 (VERIFICATION), `completeness_indicator`, `completeness_flags`, prior auth history array, member claims history summary, criteria section (if available), clinical notes (Wave 2), all field values explicit | T-B-08 completes packet assembly; `ClaimRecord.state` transitions to `CLINICAL_PACKET_ASSEMBLY`; delivery confirmed to S-08 |
| ClinicalClassificationResult (call_site = VERIFICATION) | S-07 (linked to ClaimRecord.clinical_classification_id_ws2 — see §3) | `ClinicalClassificationResult` JSON object with `call_site = VERIFICATION`, `state = CLASSIFIED`, full classification output; calibration_record_id referencing WS2's CalibrationRecord | T-B-02 routing verification classification completes |
| HITL routing verification escalation packet | S-09 HITL exception management system | `EscalationPacket` with `trigger_type = ROUTING_VERIFICATION_BELOW_THRESHOLD` or `ROUTING_VERIFICATION_CONFLICT`, `escalation_trigger_id = ET-B-01`, `trigger_signal_values = {ws1_classification, ws1_confidence, ws2_classification, ws2_confidence, threshold_applied}`, `routing_queue = ROUTING_REVIEW` | BP-WS2-1 fires: WS2 verification confidence < `CLINICAL_CONTENT_VERIFICATION_THRESHOLD`, OR WS2 returns `ADMIN` (conflicting with WS1's clinical routing) |
| ClaimRecord state update | S-07 Claims management system | Write to `ClaimRecord` fields: `state`, `clinical_classification_id_ws2` (after T-B-02), `hitl_queue_type` (when entering HITL state), `updated_by`, `updated_at` | Every pipeline step producing a state transition: PENDING_PHYSICIAN_REVIEW → CLINICAL_PACKET_ASSEMBLY; CLINICAL_PACKET_ASSEMBLY → PHYSICIAN_REVIEWING; CLINICAL_PACKET_ASSEMBLY → PENDING_ADDITIONAL_INFO |
| Additional information request draft | S-08 (delivered to physician for approval) then forwarded to provider portal S-12 | Structured draft with: `claim_id`, `missing_documentation_items` (array, from `completeness_flags`), `provider_npi`, `provider_contact_details` (from S-07), draft request text (structured, not free-form) | T-B-09 executes on physician-triggered `PENDING_ADDITIONAL_INFO` transition; physician approves before dispatch to provider |
| AuditLogEntry | S-10 Audit log system | `AuditLogEntry` record (append-only); all required fields per shared entity definition and §13 schema (Pass 6) | Every T-B-10 execution: one record per routing verification result, per packet delivery, per state transition, per escalation trigger |

---

## §3. Entity Definitions

**Shared entities — do not redefine here:**
- See shared entity definition — `ClaimRecord` (D4_preamble_capability_spec.md §2)
- See shared entity definition — `ClinicalClassificationResult` (D4_preamble_capability_spec.md §2)
- See shared entity definition — `AuditLogEntry` (D4_preamble_capability_spec.md §2)
- See shared entity definition — `EscalationPacket` (D4_preamble_capability_spec.md §2)

All four are defined in `D4_preamble_capability_spec.md` §2. Field names, types, enum values, and state machine transitions are authoritative there.

**Per-spec entity: CalibrationRecord (WS2 reference)**

*This entity is defined in D4a §3. WS2 loads a separate `CalibrationRecord` for the VERIFICATION call site (different `threshold_value` from WS1's ROUTING calibration, per D3 ADR-2). WS2 does not redefine `CalibrationRecord` — it references the D4a §3 definition. The same validation rules and state machine apply; the distinguishing attribute is that the WS2 CalibrationRecord's `classifier_version` corresponds to the VERIFICATION call site configuration.*

---

**Per-spec entity: PhysicianReviewPacket**

*Defined here because WS2 creates, updates, and delivers this entity. It is not used by WS1. WS2 is the sole writer; S-08 (physician review queue) is the delivery target; S-10 stores the delivery AuditLogEntry.*

```
Entity: PhysicianReviewPacket
Scope: D4b (defined here) — created and delivered by WS2; read by physician reviewers
       via S-08; referenced by AuditLogEntry.entity_id when entity_type = "PhysicianReviewPacket"

Attributes:
- id: UUID, primary key, immutable, generated on creation
- claim_id: UUID, required, immutable, foreign key to ClaimRecord —
  the claim this packet supports
- ws1_classification_result_id: UUID, required, immutable —
  foreign key to ClinicalClassificationResult with call_site = ROUTING;
  the WS1 routing result that placed this claim in PENDING_PHYSICIAN_REVIEW;
  must be non-null before packet assembly begins
- ws2_verification_result_id: UUID, required once T-B-02 completes, immutable once set —
  foreign key to ClinicalClassificationResult with call_site = VERIFICATION;
  must be non-null before state can transition to COMPLETE or INCOMPLETE_DELIVERED
- completeness_indicator: float, range 0.000–1.000 (three decimal places), required —
  computed ratio of successfully retrieved context elements to total expected elements;
  1.000 = all expected elements retrieved; 0.000 = no context retrieved;
  mutable until state transitions to COMPLETE or INCOMPLETE_DELIVERED
- completeness_flags: array of strings, required (may be empty), mutable until delivery —
  each element identifies a specific missing context item; valid values:
  CRITERIA_SECTION_UNAVAILABLE, PRIOR_AUTH_HISTORY_UNAVAILABLE,
  CLAIMS_HISTORY_UNAVAILABLE, CLINICAL_NOTES_SCOPE_OUT,
  CLINICAL_NOTES_UNAVAILABLE, CLINICAL_NOTES_PARTIAL (some notes retrieved,
  not all), PRIOR_AUTH_EXPIRED_NO_CURRENT, MEMBER_HISTORY_INSUFFICIENT_LOOKBACK;
  empty array [] means all expected elements retrieved
- prior_auth_history: JSON array, required (may be empty array if none on record) —
  array of prior auth summary objects, each with:
  {auth_record_id: string, procedure_code: string, authorized_units: integer,
  start_date: ISO 8601 date, expiry_date: ISO 8601 date,
  prior_auth_status: enum [PRESENT_EXACT_MATCH, PRESENT_PARTIAL_MATCH,
  NOT_REQUIRED, NOT_FOUND, EXPIRED]}
- member_claims_history: JSON array, required (may be empty array) —
  array of prior claim summary objects for relevant diagnosis cluster,
  each with: {claim_id: UUID, date_of_service: ISO 8601 date,
  procedure_codes: array of strings, diagnosis_codes: array of strings,
  terminal_state: enum [APPROVED, REJECTED, CLOSED], payment_amount: decimal USD or null}
- claims_history_lookback_days: integer, required, immutable, set at assembly time —
  the lookback period used for the member claims history query (default 365)
- clinical_notes_available: boolean, required —
  true if at least one clinical note was successfully retrieved from S-13;
  false in Wave 1 (S-13 SCOPE-OUT) and when S-13 is unavailable
- clinical_notes_summary: string, max 8192 characters, optional —
  structured summary of retrieved clinical notes; null in Wave 1;
  must not contain a medical necessity recommendation or determination
- criteria_section_available: boolean, required —
  true if at least one medical necessity criteria chunk was retrieved from S-15
  above the cosine similarity threshold; false if S-15 SCOPE-OUT or below threshold
- criteria_section_content: string, max 8192 characters, optional —
  top retrieved criteria chunks concatenated with source metadata;
  null if criteria_section_available = false
- criteria_section_version_id: string, max 64 characters, optional —
  version identifier of the criteria document from which chunks were retrieved;
  null if criteria_section_available = false
- delivery_target: enum [PHYSICIAN_HITL], required, immutable —
  always PHYSICIAN_HITL for WS2 delivery; enum is single-value to allow
  future extension without schema change
- delivered_at: ISO 8601 timestamp UTC, optional, null until delivery confirmed —
  set when S-08 write is confirmed; immutable once set
- physician_review_sla: ISO 8601 timestamp UTC, required —
  = ClaimRecord.sla_deadline; copied from ClaimRecord at assembly start;
  immutable; used by S-08 to display SLA countdown to physician
- additional_info_request_id: UUID, optional, null unless state = AWAITING_ADDITIONAL_INFO —
  foreign key to the additional information request record when T-B-09 has been executed
- state: enum [ASSEMBLING, COMPLETE, INCOMPLETE_DELIVERED, AWAITING_ADDITIONAL_INFO,
  SUPERSEDED], required, mutable
- created_at: ISO 8601 timestamp UTC, immutable, set on creation
- updated_at: ISO 8601 timestamp UTC, updated on any modification
- created_by: UUID, WS2 agent instance ID, immutable
- updated_by: UUID, agent instance ID or human reviewer ID who last modified
- supersedes_packet_id: UUID, optional, null unless this packet was assembled after an
  additional-info cycle; foreign key to the PhysicianReviewPacket superseded by this one;
  set when WS2 creates a new packet on the AWAITING_ADDITIONAL_INFO → ASSEMBLING transition

Relationships:
- claim_id: UUID, foreign key to ClaimRecord, required, 1:1 (one packet per claim per assembly),
  on delete: restrict — packet cannot be deleted while ClaimRecord exists in non-CLOSED state
- ws1_classification_result_id: UUID, foreign key to ClinicalClassificationResult,
  required, 1:1, on delete: restrict
- ws2_verification_result_id: UUID, foreign key to ClinicalClassificationResult,
  required once set, 1:1, on delete: restrict
- supersedes_packet_id: UUID, foreign key to PhysicianReviewPacket,
  optional, 1:1, null unless this is a replacement packet after an additional-info cycle;
  on delete: set null
- (reverse) audit_entries: 1:many via AuditLogEntry.entity_id where
  entity_type = "PhysicianReviewPacket", on delete: restrict

State machine:
- Initial state: ASSEMBLING

- ASSEMBLING → COMPLETE: all expected context elements retrieved
  (completeness_indicator = 1.000 OR all non-SCOPE-OUT elements retrieved —
  SCOPE-OUT items do not reduce completeness_indicator); ws2_verification_result_id set;
  WS2 verification returned CLINICAL at confidence ≥ CLINICAL_CONTENT_VERIFICATION_THRESHOLD;
  delivered_at set; ClaimRecord transitions to PHYSICIAN_REVIEWING
- ASSEMBLING → INCOMPLETE_DELIVERED: one or more expected context elements could not
  be retrieved (completeness_indicator < 1.000 AND at least one non-SCOPE-OUT
  completeness_flag present); ws2_verification_result_id set; packet delivered to S-08
  with completeness_flags array visible to physician; delivered_at set;
  ClaimRecord transitions to PHYSICIAN_REVIEWING
- COMPLETE → AWAITING_ADDITIONAL_INFO: physician records that the assembled packet
  is insufficient and requests additional information from provider; T-B-09 executes;
  additional_info_request_id set; ClaimRecord transitions to PENDING_ADDITIONAL_INFO
- INCOMPLETE_DELIVERED → AWAITING_ADDITIONAL_INFO: same trigger as above
- AWAITING_ADDITIONAL_INFO → ASSEMBLING: provider submits additional documentation;
  Queue & SLA Management Agent re-queues the claim from PENDING_ADDITIONAL_INFO;
  WS2 picks it up and creates a new PhysicianReviewPacket (new id), superseding this one
- COMPLETE → SUPERSEDED: a new PhysicianReviewPacket is created for the same claim_id
  (after additional documentation received and claim re-queued)
- INCOMPLETE_DELIVERED → SUPERSEDED: same trigger
- Terminal state: SUPERSEDED — the superseded packet is read-only; retained for audit trail

Invalid transitions:
- ASSEMBLING → PHYSICIAN_REVIEWING: FORBIDDEN — ASSEMBLING is an internal WS2 state;
  ClaimRecord cannot transition to PHYSICIAN_REVIEWING until PhysicianReviewPacket
  state is COMPLETE or INCOMPLETE_DELIVERED and packet is confirmed delivered to S-08
- COMPLETE → ASSEMBLING: FORBIDDEN — a completed and delivered packet cannot revert to
  assembly; the correct path when additional documentation arrives is to create a new
  packet (COMPLETE → SUPERSEDED, new packet starts ASSEMBLING)
- SUPERSEDED → COMPLETE: FORBIDDEN — superseded packets are read-only; audit evidence
  must not be modified after supersession

Validation rules:
- completeness_indicator must equal the computed ratio:
  (non-SCOPE-OUT elements successfully retrieved) ÷ (total non-SCOPE-OUT expected elements);
  SCOPE-OUT items are excluded from both numerator and denominator
- completeness_flags must contain an entry for every element where retrieval failed
  or where the element is SCOPE-OUT; empty array is only valid when
  completeness_indicator = 1.000 considering SCOPE-OUT adjustments
- delivered_at must be null when state = ASSEMBLING; must be non-null when
  state ∈ {COMPLETE, INCOMPLETE_DELIVERED}
- ws2_verification_result_id must be non-null before state can transition from ASSEMBLING;
  a packet delivered without a VERIFICATION ClinicalClassificationResult is a data
  integrity violation that fires ET-B-07

Naming conventions:
- Table name: physician_review_packets (snake_case, plural)
- Primary key: id
- Enum values: SCREAMING_SNAKE_CASE
- JSON array fields (prior_auth_history, member_claims_history): stored as JSON arrays;
  validated at application layer against type rules
- Timestamps: ISO 8601 with timezone (UTC stored)
```

---

## §4. Activity Catalog

| Task ID | Task name | Task type | Delegation level | Data required | Tool required | Risk level |
|---------|-----------|-----------|-----------------|---------------|---------------|------------|
| T-B-01 | Claim retrieval from PENDING_PHYSICIAN_REVIEW queue | Retrieval | Fully agentic | ClaimRecord in PENDING_PHYSICIAN_REVIEW state; ClinicalClassificationResult (call_site = ROUTING) via clinical_classification_id | Claims management system queue read (S-07); schema validator | Low |
| T-B-02 | Routing verification classification | Decision | Agent-led + HITL on condition | ClaimRecord: diagnosis_codes, procedure_codes, provider_specialty; CLINICAL_CONTENT_VERIFICATION_THRESHOLD; medical necessity criteria top-3 chunks (if S-15 available); signed CalibrationRecord (VERIFICATION call site); WS1 ClinicalClassificationResult (ROUTING) for reference | Sonnet 4.6; medical necessity criteria vector store (S-15) [SCOPE-OUT]; configuration management (S-16) | **High** |
| T-B-03 | Prior authorisation history retrieval | Retrieval | Fully agentic | member_id, procedure_codes (CPT array), lookback period (default 12 months) | Prior auth system API read-only (S-04) | Medium |
| T-B-04 | Member claims history retrieval | Retrieval | Fully agentic | member_id, diagnosis_code_range (ICD chapter from ClaimRecord.diagnosis_codes[0]), claims_history_lookback_days (default 365) | Claims history database read-only (S-14) | Low |
| T-B-05 | Clinical notes retrieval (Wave 2) | Retrieval | Agent-led + HITL on condition | member_id, provider_npi, date_of_service, episode diagnosis range | Clinical notes source system API (S-13) [SCOPE-OUT — Wave 2 only] | **High** |
| T-B-06 | Medical necessity criteria retrieval | Retrieval | Fully agentic | procedure_codes[0] (procedure_code_range mapping), icd_chapter(diagnosis_codes[0]), minimum cosine similarity 0.75 | Medical necessity criteria vector store RAG (S-15) [SCOPE-OUT] | Medium |
| T-B-07 | Packet completeness assessment and flagging | Decision | Fully agentic | Results of T-B-03 through T-B-06; list of expected context elements per claim type; SCOPE-OUT status of S-13 and S-15 | Internal completeness rule set; SCOPE-OUT status flags | Low |
| T-B-08 | Pre-filled review packet assembly and delivery | Generation + Action | Agent-led + HITL on condition | All T-B-01 through T-B-07 outputs; PhysicianReviewPacket schema; ClaimRecord.sla_deadline | S-08 physician review queue interface (write); S-07 (state write) | **High** |
| T-B-09 | Additional information request drafting | Generation | Agent-led + HITL on condition | completeness_flags array; provider_npi (from ClaimRecord); provider contact details (from S-07); ClaimRecord.diagnosis_codes and procedure_codes | Haiku 4.5 (draft generation); S-08 (physician approval delivery); S-12 (provider portal dispatch after physician approval) | Medium |
| T-B-10 | Audit record generation | Generation | Fully agentic | All pipeline step outputs; ClinicalClassificationResult (VERIFICATION); PhysicianReviewPacket delivery confirmation; timestamps; escalation reason if applicable; delegation_tier for each action | Audit log system append-only API (S-10) | Medium |
| T-B-11 | Escalation packet assembly | Generation | Fully agentic | Pipeline step outputs to point of escalation; trigger type and trigger ID (ET-B-01 through ET-B-05); specific signal values that caused the trigger; required_resolution question | Escalation formatter; S-09 HITL exception management | Medium |

**High-risk task cross-reference:**
- T-B-02 → ET-B-01 (routing verification below threshold or classification conflict)
- T-B-05 → ET-B-02 (clinical notes not retrievable — Wave 2)
- T-B-08 → ET-B-03 (packet delivery failure to S-08)

**Configurable parameters referenced in this catalog:**
- `CLINICAL_CONTENT_VERIFICATION_THRESHOLD`: float, default 0.85 [Assumption A-D4b-3: set higher than WS1's 0.70 because WS2 is a second-pass safety check and a higher confirmation threshold reduces erroneous re-routing attempts; exact value requires CMO calibration per D3 ADR-2]; CMO-certified via `CalibrationRecord` for the VERIFICATION call site; governs T-B-02 routing branch
- `WS2_CLAIMS_HISTORY_LOOKBACK_DAYS`: integer, default 365 (12 months); governs T-B-04 lookback window for member claims history; set by VP Operations
- `WS2_PRIOR_AUTH_HISTORY_LOOKBACK_MONTHS`: integer, default 12; governs T-B-03 lookback window for prior auth records; set by VP Operations

---

*Pass 5a complete. Pass 5b appends §5–§8 to this file.*

---

## §5. Requirements

```
REQ-B-1: Routing verification classification on every clinical-path claim before packet assembly
Description: The agent MUST execute T-B-02 (routing verification classification) on every
  ClaimRecord that enters WS2 processing, producing a ClinicalClassificationResult with
  call_site = VERIFICATION before any packet assembly action. No ClaimRecord MAY transition
  from PENDING_PHYSICIAN_REVIEW to CLINICAL_PACKET_ASSEMBLY without a linked
  ClinicalClassificationResult with call_site = VERIFICATION and state = CLASSIFIED.
Acceptance criterion: Zero ClaimRecords in CLINICAL_PACKET_ASSEMBLY, PHYSICIAN_REVIEWING,
  or PENDING_ADDITIONAL_INFO state lack a linked ClinicalClassificationResult with
  call_site = VERIFICATION and state = CLASSIFIED. Verified by post-processing audit query:
  SELECT COUNT(*) FROM claim_records cr
  LEFT JOIN clinical_classification_results ccr_v
    ON cr.clinical_classification_id_ws2 = ccr_v.id
    AND ccr_v.call_site = 'VERIFICATION'
  WHERE cr.state IN ('CLINICAL_PACKET_ASSEMBLY','PHYSICIAN_REVIEWING','PENDING_ADDITIONAL_INFO')
    AND (ccr_v.id IS NULL OR ccr_v.state != 'CLASSIFIED')
  must return 0.
Delegation tier: AGENT_ALONE (when CLINICAL at or above threshold); HUMAN_DECIDES (BP-WS2-1)
Error handling: If T-B-02 fails to produce a ClinicalClassificationResult (classifier
  call error, timeout, or missing CalibrationRecord), ET-B-05 fires; ClaimRecord remains
  in PENDING_PHYSICIAN_REVIEW; pipeline does not advance to packet assembly under any
  failure condition.
```

```
REQ-B-2: Signed CalibrationRecord (VERIFICATION call site) required before any classification
Description: The agent MUST verify at startup that a CalibrationRecord with state = SIGNED,
  cmo_signoff_date non-null, recall_achieved ≥ 0.995, holdout_set_size ≥ 500, and
  classifier_version matching the deployed classifier is present in S-16 for use at
  call_site = VERIFICATION. This is a separate CalibrationRecord from WS1's routing
  calibration artefact, per D3 ADR-2. The agent MUST refuse to start and MUST produce a
  startup failure alert if any condition is not met. The agent MUST NOT load a
  CLINICAL_CONTENT_VERIFICATION_THRESHOLD value without this artefact.
Acceptance criterion: Agent startup fails with exit code 1 and a structured alert message
  when tested against: (a) missing CalibrationRecord for VERIFICATION call site, (b)
  CalibrationRecord with state = DRAFT, (c) CalibrationRecord with recall_achieved = 0.990,
  (d) CalibrationRecord with holdout_set_size = 450, (e) classifier_version mismatch.
  All five conditions produce startup failure, not a warning.
Delegation tier: AGENT_ALONE
Error handling: Startup failure is the correct and complete error handling. The agent does
  not degrade gracefully or operate without a valid CalibrationRecord. Ops team and CMO
  are notified via the startup failure alert before any claim enters the WS2 pipeline.
```

```
REQ-B-3: HITL escalation on BP-WS2-1 and BP-WS2-2 within 60 seconds of trigger detection
Description: The agent MUST assemble and deliver an EscalationPacket to the correct HITL
  queue within 60 seconds of the trigger condition being detected, for all defined escalation
  triggers: ET-B-01 (routing verification below threshold or conflict), ET-B-02 (clinical
  notes not retrievable — Wave 2), ET-B-03 (packet delivery failure), ET-B-04 (SLA imminent
  for HITL checkpoint), ET-B-05 (audit failure or state mismatch). The EscalationPacket
  MUST include: escalation_trigger_id, trigger_type, all trigger_signal_values (specific
  numeric and enum values — no free-text descriptions), and required_resolution.
Acceptance criterion: (a) EscalationPacket assembled and written to target queue within
  60 seconds of trigger detection (measured from AuditLogEntry.timestamp for
  ESCALATION_TRIGGERED to EscalationPacket.created_at). (b) Zero EscalationPackets with
  null trigger_signal_values. (c) Routing queue matches trigger: ET-B-01 → ROUTING_REVIEW
  queue (exception processor); ET-B-02 → ops alert + completeness_flags on packet;
  ET-B-03 → ops alert; ET-B-04 → HITL queue re-notification with URGENT flag;
  ET-B-05 → EXCEPTION_PROCESSOR.
Delegation tier: AGENT_ALONE (packet assembly); HUMAN_DECIDES (resolution)
Error handling: If EscalationPacket write to target queue fails (S-09 unavailable),
  the agent retries once after 5 seconds, then writes the packet to S-07 with a
  QUEUE_DELIVERY_FAILED flag and alerts ops. ClaimRecord remains in PENDING_PHYSICIAN_REVIEW
  — it does not advance.
```

```
REQ-B-4: Complete AuditLogEntry for every WS2 action, state transition, and packet delivery
Description: The agent MUST produce an AuditLogEntry record for every ClaimRecord state
  transition initiated by WS2, every ClinicalClassificationResult (VERIFICATION) creation,
  every PhysicianReviewPacket creation and delivery confirmation, every EscalationPacket
  creation, and every additional information request dispatch. Each AuditLogEntry MUST
  include all required fields per the shared entity definition and §13 schema (Pass 6).
  An AuditLogEntry with any required field null or absent MUST trigger ET-B-05 before the
  associated action is issued.
Acceptance criterion: Zero ClaimRecords in CLINICAL_PACKET_ASSEMBLY, PHYSICIAN_REVIEWING,
  or PENDING_ADDITIONAL_INFO state lack a corresponding AuditLogEntry with action matching
  the state transition and state = COMMITTED. ET-B-05 fires in 100% of test cases where a
  required AuditLogEntry field is absent.
Delegation tier: AGENT_ALONE
Error handling: If S-10 (audit log system) is unavailable when T-B-10 attempts to write,
  the agent queues the AuditLogEntry locally (in-memory, max 50 records), retries at
  10-second intervals for up to 5 minutes. If S-10 remains unavailable after 5 minutes,
  the agent suspends claim processing and alerts ops. No ClaimRecord advances while S-10
  is confirmed unavailable.
```

```
REQ-B-5: Graceful degradation when context retrieval systems are unavailable
Description: The agent MUST handle unavailability of S-04 (prior auth), S-14 (claims
  history), S-13 (clinical notes — Wave 2), and S-15 (medical necessity criteria — SCOPE-OUT)
  by: (a) retrying the failed call once after 5 seconds, (b) adding the specific
  completeness_flag to the PhysicianReviewPacket for the unavailable element (not aborting
  packet assembly), (c) delivering the packet with completeness_indicator reflecting the
  missing element and completeness_flags array explicitly identifying what is missing.
  The agent MUST NOT deliver a packet without explicitly marking missing context. A packet
  delivered without a completeness_indicator and completeness_flags array is a data
  integrity violation (ET-B-05).
Acceptance criterion: When S-04 is simulated as returning a 503 error on both the initial
  call and the one retry: (a) completeness_flags += ["PRIOR_AUTH_HISTORY_UNAVAILABLE"],
  (b) completeness_indicator decremented by the prior auth element weight, (c) packet
  delivered to S-08 with the flag present and completeness_indicator < 1.000, (d) physician
  receives the packet with the flag visible — not a blank prior auth section. Same behaviour
  verified for S-14 and S-13 (Wave 2).
Delegation tier: AGENT_ALONE (degradation and delivery); HUMAN_DECIDES (clinical review on
  incomplete packet)
Error handling: This requirement IS the error handling specification for context retrieval.
  The named failure path is: retry once → add completeness_flag → deliver incomplete packet
  with explicit indicator. There is no further fallback beyond marking the gap.
```

```
REQ-B-6: Governance hard stop — PhysicianReviewPacket MUST NOT contain a determination
  or recommendation
Description: The agent MUST NOT include in any PhysicianReviewPacket field any text,
  structured value, or computed field that approximates a medical necessity determination
  or recommendation (e.g., "recommend approval," "likely medically necessary," "probable
  denial," "predicted outcome"). The clinical_notes_summary and criteria_section_content
  fields MUST contain retrieved content only — verbatim or structured extracts from source
  documents, with source attribution. The ClinicalClassificationResult (VERIFICATION) in the
  packet indicates whether the claim was correctly classified as clinical; it does not
  indicate whether the medical procedure is medically necessary. These are distinct questions.
Acceptance criterion: A content review of 100 consecutive PhysicianReviewPackets by a
  CMO-authorised clinical reviewer returns zero packets containing any of the following
  patterns in any field: recommendation language, predicted outcome language, pre-filled
  determination fields. All free-text fields in the packet contain only retrieved source
  content or structured metadata. This review is conducted monthly as part of the WS2
  governance audit cadence.
Delegation tier: AGENT_ALONE (content generation); HUMAN_DECIDES (determination)
Error handling: If the content generation step (T-B-08 packet assembly using Haiku 4.5
  for notes summarisation) produces a clinical_notes_summary field that a post-generation
  validation check flags as containing recommendation language (keyword detection against
  a validated exclusion list), the field is replaced with the raw retrieved text and
  ET-B-05 fires as an audit flag. The packet is delivered with raw text, not blocked.
```

```
REQ-B-7: Completeness indicator must be explicit and visible before physician review begins
Description: Every PhysicianReviewPacket delivered to S-08 MUST include:
  completeness_indicator (float 0.000–1.000), completeness_flags (array — may be empty),
  and physician_review_sla (ISO 8601 timestamp). These three fields MUST be present at
  the top level of the packet structure delivered to S-08 — they MUST NOT be embedded
  in a sub-object that requires navigation to find. The S-08 interface implementation
  MUST surface completeness_indicator and completeness_flags to the physician before
  any clinical content is shown.
Acceptance criterion: Zero PhysicianReviewPackets delivered to S-08 with
  completeness_indicator null, completeness_flags absent, or physician_review_sla null.
  Verified by packet schema validation at T-B-08 before the S-08 write is issued.
Delegation tier: AGENT_ALONE
Error handling: If the packet schema validation at T-B-08 detects any of the three required
  fields as null or absent, the delivery is aborted; ET-B-05 fires; ClaimRecord remains in
  CLINICAL_PACKET_ASSEMBLY; no partial packet is delivered.
```

---

## §6. Decision Logic

---

```
Decision D-B-1: Routing verification classification
Input:
  - ClaimRecord: diagnosis_codes (ICD-10 array), procedure_codes (CPT array),
    provider_specialty (string); state must = PENDING_PHYSICIAN_REVIEW at call time
  - WS1 ClinicalClassificationResult (call_site = ROUTING): classification,
    confidence_score, reasoning_chain — for reference context in verification prompt,
    not as an override
  - CLINICAL_CONTENT_VERIFICATION_THRESHOLD: float (default 0.85), loaded from
    signed CalibrationRecord (VERIFICATION call site) in S-16
  - CalibrationRecord (VERIFICATION call site): state must = SIGNED,
    recall_achieved ≥ 0.995 (validated at startup)
  - S-15 medical necessity criteria: top-3 chunks by cosine similarity ≥ 0.75
    (may be empty if SCOPE-OUT or no chunk reaches threshold)

Pre-condition check (runs before classifier call):
  IF CalibrationRecord (VERIFICATION call site) state ≠ SIGNED OR cmo_signoff_date null:
    THEN abort T-B-02; fire ET-B-05 with trigger_signal_values =
      {error: "VERIFICATION_CALIBRATION_RECORD_INVALID", calibration_record_id,
      actual_state}; ClaimRecord remains PENDING_PHYSICIAN_REVIEW; GOTO end
  IF ClaimRecord.state ≠ PENDING_PHYSICIAN_REVIEW:
    THEN abort T-B-02; fire ET-B-05 with trigger_signal_values =
      {error: "WRONG_CLAIM_STATE_FOR_TB02", actual_state: ClaimRecord.state,
      expected_state: "PENDING_PHYSICIAN_REVIEW"}; GOTO end

Logic:
  Attempt to retrieve top-3 criteria chunks from S-15 (similarity ≥ 0.75)
  IF S-15 SCOPE-OUT or no chunk reaches threshold:
    THEN criteria_chunks = []; completeness_flags (pre-packet) +=
      ["CRITERIA_SECTION_UNAVAILABLE"]
  ELSE:
    criteria_chunks = retrieved chunks

  Call Sonnet 4.6 classifier at call_site = VERIFICATION with
    {diagnosis_codes, procedure_codes, provider_specialty, criteria_chunks,
    ws1_reasoning_chain (for context — not as override signal)}
  Classifier returns: classification ∈ {ADMIN, CLINICAL, UNCERTAIN},
    confidence_score (float 0.000–1.000), reasoning_chain (string ≥ 20 characters)

  Create ClinicalClassificationResult:
    call_site = VERIFICATION; classification; confidence_score;
    threshold_applied = CLINICAL_CONTENT_VERIFICATION_THRESHOLD;
    threshold_met = (confidence_score ≥ threshold_applied);
    signal_diagnosis_codes = diagnosis_codes; signal_procedure_codes = procedure_codes;
    signal_provider_specialty = provider_specialty; reasoning_chain; classifier_version;
    calibration_record_id (VERIFICATION artefact); state → CLASSIFIED

  Link ClaimRecord.clinical_classification_id_ws2 = ClinicalClassificationResult.id

  IF classification = CLINICAL AND confidence_score ≥ CLINICAL_CONTENT_VERIFICATION_THRESHOLD:
    THEN verification_result = CONFIRMED_CLINICAL;
      AuditLogEntry written with action = ROUTING_VERIFICATION_CONFIRMED,
        compliance_flags = ["URAC_NCQA_CLINICAL_GATE"];
      pipeline advances to T-B-03 (context retrieval begins)
  ELSE IF classification = UNCERTAIN (any confidence_score):
    THEN verification_result = VERIFICATION_UNCERTAIN;
      fire ET-B-01 with trigger_type = ROUTING_VERIFICATION_BELOW_THRESHOLD,
        trigger_signal_values = {ws1_classification, ws1_confidence, ws2_classification:
        "UNCERTAIN", ws2_confidence: confidence_score, threshold_applied};
      ClaimRecord.state → PENDING_HITL_EXCEPTION with hitl_queue_type = ROUTING_REVIEW;
      pipeline terminates for WS2 pending HITL resolution
  ELSE IF classification = CLINICAL AND confidence_score < CLINICAL_CONTENT_VERIFICATION_THRESHOLD:
    THEN verification_result = CLINICAL_BELOW_THRESHOLD;
      fire ET-B-01 with trigger_type = ROUTING_VERIFICATION_BELOW_THRESHOLD,
        trigger_signal_values = {ws2_classification: "CLINICAL",
        ws2_confidence: confidence_score, threshold_applied:
        CLINICAL_CONTENT_VERIFICATION_THRESHOLD, shortfall:
        CLINICAL_CONTENT_VERIFICATION_THRESHOLD - confidence_score};
      ClaimRecord.state → PENDING_HITL_EXCEPTION with hitl_queue_type = ROUTING_REVIEW;
      pipeline terminates for WS2 pending HITL resolution
  ELSE IF classification = ADMIN (any confidence_score):
    THEN verification_result = ROUTING_CONFLICT;
      fire ET-B-01 with trigger_type = ROUTING_VERIFICATION_CONFLICT,
        trigger_signal_values = {ws1_classification, ws1_confidence,
        ws2_classification: "ADMIN", ws2_confidence: confidence_score,
        threshold_applied, conflict: true};
      ClaimRecord.state → PENDING_HITL_EXCEPTION with hitl_queue_type = ROUTING_REVIEW;
      pipeline terminates for WS2 pending HITL resolution — WS2 does not autonomously
      reroute to admin path; HITL routing review exception processor resolves the conflict

Output:
  verification_result ∈ {CONFIRMED_CLINICAL, VERIFICATION_UNCERTAIN,
    CLINICAL_BELOW_THRESHOLD, ROUTING_CONFLICT}
  ClaimRecord.state: PENDING_PHYSICIAN_REVIEW (when CONFIRMED_CLINICAL, advances to
    CLINICAL_PACKET_ASSEMBLY on packet delivery) OR PENDING_HITL_EXCEPTION (all others)
Delegation tier:
  AGENT_ALONE for CONFIRMED_CLINICAL;
  HUMAN_DECIDES for VERIFICATION_UNCERTAIN, CLINICAL_BELOW_THRESHOLD, ROUTING_CONFLICT
Confidence gate:
  CLINICAL_CONTENT_VERIFICATION_THRESHOLD (default 0.85, CMO-certified);
  CLINICAL below threshold → ET-B-01, HUMAN_DECIDES;
  ADMIN at any confidence → ET-B-01 conflict, HUMAN_DECIDES

Worked example (clinical confirmed — standard path):
  Input values: diagnosis_codes = ["M17.11"], procedure_codes = ["27447"],
    provider_specialty = "Orthopedics",
    CLINICAL_CONTENT_VERIFICATION_THRESHOLD = 0.85
  WS1 context: classification = CLINICAL, confidence_score = 0.94 (already in
    PENDING_PHYSICIAN_REVIEW via ET-01)
  S-15 retrieval: 3 chunks retrieved (cosine similarity 0.91, 0.87, 0.79) for
    procedure_code_range "27000–27999" × icd_chapter "M"
  Classifier output (VERIFICATION call): classification = CLINICAL,
    confidence_score = 0.91,
    reasoning_chain = "Total knee arthroplasty for primary osteoarthritis confirmed
    as clinical by verification classifier: procedure requires physician assessment
    of conservative treatment history and surgical risk stratification per InterQual
    criteria — routing to physician review is correct."
  Branch taken: CLINICAL AND 0.91 ≥ 0.85 → CONFIRMED_CLINICAL
  Output: ClinicalClassificationResult (VERIFICATION, CLINICAL, 0.91, threshold_met = true)
    created and linked; AuditLogEntry: action = ROUTING_VERIFICATION_CONFIRMED,
    compliance_flags = ["URAC_NCQA_CLINICAL_GATE"]; pipeline advances to T-B-03

Worked example (routing conflict — WS2 returns ADMIN):
  Input values: diagnosis_codes = ["I25.10"], procedure_codes = ["93306"],
    provider_specialty = "Cardiology",
    CLINICAL_CONTENT_VERIFICATION_THRESHOLD = 0.85
  WS1 context: classification = CLINICAL, confidence_score = 0.78 (claim routed
    via ET-01 — WS1 returned CLINICAL at moderate confidence)
  S-15 retrieval: 2 chunks (similarity 0.81, 0.77) for cardiac surveillance procedures
  Classifier output (VERIFICATION call): classification = ADMIN,
    confidence_score = 0.89,
    reasoning_chain = "Standard echocardiographic surveillance for documented coronary
    artery disease: verification classifier finds no medical necessity determination
    required; routine diagnostic monitoring for a stable chronic condition — WS1 routing
    classification at CLINICAL may reflect edge-case signal; verification returns ADMIN."
  Branch taken: ADMIN at any confidence → ROUTING_CONFLICT
  Output: fire ET-B-01 with trigger_type = ROUTING_VERIFICATION_CONFLICT,
    trigger_signal_values = {ws1_classification: "CLINICAL", ws1_confidence: 0.78,
    ws2_classification: "ADMIN", ws2_confidence: 0.89, conflict: true};
  ClaimRecord.state → PENDING_HITL_EXCEPTION; hitl_queue_type = ROUTING_REVIEW;
  HITL routing review exception processor decides whether to return to admin path
  (full WS1 pipeline re-run) or proceed with physician review

Worked example (below threshold):
  Input values: diagnosis_codes = ["J06.9"], procedure_codes = ["99214"],
    provider_specialty = "Internal Medicine",
    CLINICAL_CONTENT_VERIFICATION_THRESHOLD = 0.85
  WS1 context: classification = ADMIN, confidence_score = 0.61 (ET-02 borderline
    threshold — claim is in PENDING_PHYSICIAN_REVIEW from ET-02)
  Classifier output (VERIFICATION call): classification = CLINICAL,
    confidence_score = 0.72
  Branch taken: CLINICAL AND 0.72 < 0.85 → CLINICAL_BELOW_THRESHOLD
  Output: fire ET-B-01 with trigger_signal_values = {ws2_classification: "CLINICAL",
    ws2_confidence: 0.72, threshold_applied: 0.85, shortfall: 0.13};
  ClaimRecord.state → PENDING_HITL_EXCEPTION; hitl_queue_type = ROUTING_REVIEW
```

---

```
Decision D-B-2: Packet completeness determination
Input:
  - Results of T-B-03 (prior auth history retrieval): retrieved (boolean), record_count
  - Results of T-B-04 (member claims history retrieval): retrieved (boolean), record_count
  - Results of T-B-05 (clinical notes retrieval — Wave 2): clinical_notes_available
    (boolean, always false in Wave 1 SCOPE-OUT), notes_count
  - Results of T-B-06 (criteria retrieval): criteria_section_available (boolean),
    chunk_count
  - Current SCOPE-OUT status: S-13_scope_out (boolean), S-15_scope_out (boolean)

Logic:
  Initialise:
    completeness_flags = []
    retrieved_count = 0
    expected_count = 0 (starts at 0; SCOPE-OUT items excluded from both numerator
      and denominator)

  Evaluate prior auth history (T-B-03):
    expected_count += 1
    IF T-B-03 retrieved = true (at least one record or confirmed none on file):
      retrieved_count += 1
    ELSE:
      completeness_flags += ["PRIOR_AUTH_HISTORY_UNAVAILABLE"]

  Evaluate member claims history (T-B-04):
    expected_count += 1
    IF T-B-04 retrieved = true (at least one record or confirmed empty history):
      retrieved_count += 1
    ELSE:
      completeness_flags += ["CLAIMS_HISTORY_UNAVAILABLE"]

  Evaluate clinical notes (T-B-05):
    IF S-13_scope_out = true:
      completeness_flags += ["CLINICAL_NOTES_SCOPE_OUT"]
      (do NOT increment expected_count or retrieved_count — excluded from ratio)
    ELSE (S-13 accessible — Wave 2):
      expected_count += 1
      IF T-B-05 retrieved = true AND notes_count ≥ 1:
        retrieved_count += 1
      ELSE IF T-B-05 retrieved = true AND notes_count = 0:
        completeness_flags += ["CLINICAL_NOTES_UNAVAILABLE"]
      ELSE:
        completeness_flags += ["CLINICAL_NOTES_UNAVAILABLE"]

  Evaluate medical necessity criteria (T-B-06):
    IF S-15_scope_out = true:
      completeness_flags += ["CRITERIA_SECTION_UNAVAILABLE"]
      (do NOT increment counts — SCOPE-OUT excluded)
    ELSE (S-15 accessible):
      expected_count += 1
      IF T-B-06 criteria_section_available = true AND chunk_count ≥ 1:
        retrieved_count += 1
      ELSE:
        completeness_flags += ["CRITERIA_SECTION_UNAVAILABLE"]

  Compute:
    IF expected_count = 0:
      completeness_indicator = 0.000 (all expected items are SCOPE-OUT;
        fire ET-B-05 — a packet with no non-SCOPE-OUT context is a data
        integrity condition requiring ops review)
    ELSE:
      completeness_indicator = retrieved_count / expected_count
        (rounded to 3 decimal places)

Output:
  completeness_indicator (float 0.000–1.000)
  completeness_flags (array — may be empty)
Delegation tier: AGENT_ALONE
Confidence gate: not applicable — arithmetic computation

Worked example (Wave 1, S-13 and S-15 SCOPE-OUT):
  T-B-03: prior auth retrieved = true (2 records: PA-2026-004891, PA-2025-018203)
  T-B-04: claims history retrieved = true (7 prior claims in 365-day window)
  T-B-05: S-13_scope_out = true
  T-B-06: S-15_scope_out = true
  expected_count = 2 (prior auth + claims history; S-13 and S-15 excluded)
  retrieved_count = 2
  completeness_indicator = 2/2 = 1.000
  completeness_flags = ["CLINICAL_NOTES_SCOPE_OUT", "CRITERIA_SECTION_UNAVAILABLE"]
  Interpretation: packet is fully complete for Wave 1 scope (both non-SCOPE-OUT
    items retrieved); SCOPE-OUT flags inform physician but do not reduce
    completeness_indicator

Worked example (Wave 2, S-13 unavailable):
  T-B-03: prior auth retrieved = true (1 record)
  T-B-04: claims history retrieved = false (S-14 returned 503 after retry)
  T-B-05: S-13_scope_out = false; retrieved = false (S-13 accessible but no notes found)
  T-B-06: S-15_scope_out = false; criteria_section_available = true (2 chunks)
  expected_count = 4
  retrieved_count = 2 (prior auth + criteria section)
  completeness_indicator = 2/4 = 0.500
  completeness_flags = ["CLAIMS_HISTORY_UNAVAILABLE", "CLINICAL_NOTES_UNAVAILABLE"]
  Output: packet delivered as INCOMPLETE_DELIVERED with completeness_indicator = 0.500
    and both flags visible to physician
```

---

```
Decision D-B-3: Additional information request gating (physician-triggered)
Input:
  - Physician action token from S-08: action ∈ {APPROVED, REJECTED,
    ADDITIONAL_INFO_REQUIRED}
  - completeness_flags array from PhysicianReviewPacket (identifies what was missing)
  - ClaimRecord: provider_npi (string), ClaimRecord.id
  - Provider contact details: from S-07 provider record
  - Current timestamp; ClaimRecord.sla_deadline

Logic:
  IF physician action = ADDITIONAL_INFO_REQUIRED:
    call Haiku 4.5 to draft additional information request:
      inputs: {completeness_flags, claim_id, provider_npi, diagnosis_codes,
        procedure_codes, date_of_service, missing_item_descriptions
        (derived from completeness_flags mapping)}
      output: structured draft with: {missing_documentation_items (array),
        provider_npi, draft_request_text — factual and non-leading only,
        must not pre-answer the clinical question}
    Deliver draft to S-08 for physician review and approval
    ClaimRecord.state → PENDING_ADDITIONAL_INFO
    AuditLogEntry written with action = ADDITIONAL_INFO_REQUEST_DRAFTED,
      delegation_tier = AGENT_PROPOSES

    IF physician approves the draft (approval token received from S-08):
      dispatch request to provider portal S-12
      AuditLogEntry written with action = ADDITIONAL_INFO_REQUEST_DISPATCHED,
        delegation_tier = HUMAN_DECIDES, human_id = physician reviewer ID
      (claim remains in PENDING_ADDITIONAL_INFO pending provider response;
       Queue & SLA Management Agent monitors for provider response)

    IF physician does not approve the draft within 2 hours:
      fire ET-B-04 with trigger_signal_values = {sla_type: "ADDITIONAL_INFO_DRAFT_REVIEW",
        physician_id, claim_id, elapsed_minutes}; URGENT flag to physician queue

    IF physician rejects the draft and provides revised text:
      physician's revised text is used (not agent re-draft); dispatched to S-12;
      AuditLogEntry with human_id set and delegation_tier = HUMAN_DECIDES;
      original agent draft retained in audit log for comparison

  ELSE IF physician action = APPROVED (with payment determination token):
    WS2 pipeline complete; write ClaimRecord state transition
    PHYSICIAN_REVIEWING → APPROVED to S-07 with physician's determination token;
    AuditLogEntry with human_id, delegation_tier = HUMAN_DECIDES
    (payment processing picks up from APPROVED state)

  ELSE IF physician action = REJECTED (with denial reason codes):
    Write ClaimRecord state transition PHYSICIAN_REVIEWING → REJECTED to S-07
    with physician's denial reason codes; AuditLogEntry with human_id,
    delegation_tier = HUMAN_DECIDES
    (rejection notice formatted and delivered to provider by downstream process)

Output:
  ClaimRecord.state ∈ {APPROVED, REJECTED, PENDING_ADDITIONAL_INFO}
Delegation tier:
  AGENT_PROPOSES for draft assembly;
  HUMAN_DECIDES for dispatch approval, determination, and denial
Confidence gate: not applicable — physician decision drives the branch

Worked example (additional information requested, draft approved):
  Physician action: ADDITIONAL_INFO_REQUIRED
  completeness_flags = ["CLINICAL_NOTES_UNAVAILABLE"]
  Provider_id = "GHS-PRV-NPI-7124893", claim_id = "GHS-CLM-2026-091547"
  Date of service = "2026-04-15", procedure = "27447" (total knee arthroplasty)
  Haiku 4.5 draft:
    missing_documentation_items: ["Operative notes or treatment plan for CPT 27447 —
      total knee arthroplasty dated 2026-04-15", "Conservative treatment history
      (physical therapy, NSAIDs, weight management records) for ICD-10 M17.11"]
    draft_request_text: "Please provide operative notes and documented conservative
      treatment history for member GHS-MBR-0042891, date of service 2026-04-15,
      procedure 27447, within 5 business days."
  Physician approves draft without modification.
  dispatch to S-12 confirmed; ClaimRecord.state = PENDING_ADDITIONAL_INFO;
  AuditLogEntry: action = ADDITIONAL_INFO_REQUEST_DISPATCHED, human_id =
    physician reviewer UUID, delegation_tier = HUMAN_DECIDES
```

---

## §7. Escalation Triggers

| Trigger ID | Trigger condition | Threshold | Action | Notified party | SLA | If SLA breached |
|------------|-------------------|-----------|--------|----------------|-----|-----------------|
| ET-B-01 | Routing verification classifier (T-B-02) returns `UNCERTAIN` at any confidence, OR returns `CLINICAL` with confidence_score < `CLINICAL_CONTENT_VERIFICATION_THRESHOLD`, OR returns `ADMIN` (conflict with WS1's routing to PENDING_PHYSICIAN_REVIEW) | UNCERTAIN: any confidence; CLINICAL: confidence_score < 0.85 (default); ADMIN: any confidence | ClaimRecord.state → PENDING_HITL_EXCEPTION; hitl_queue_type = ROUTING_REVIEW; EscalationPacket assembled with trigger_type = ROUTING_VERIFICATION_BELOW_THRESHOLD or ROUTING_VERIFICATION_CONFLICT, trigger_signal_values = {ws1_classification, ws1_confidence, ws2_classification, ws2_confidence, threshold_applied, conflict: boolean}; delivered to S-09 HITL exception management | HITL routing review (exception processor); CMO notified if conflict rate in rolling 7-day window > 1% | 2 hours from EscalationPacket.created_at | Exception processor supervisor notified; claim re-tagged URGENT in ROUTING_REVIEW queue; SLA breach event written to AuditLogEntry; if weekly conflict rate > 1%, CMO-initiated calibration review |
| ET-B-02 | Clinical notes retrieval (T-B-05) fails after one retry — S-13 returns 5xx/timeout or returns empty result set for a claim where clinical notes are expected (Wave 2 only; does not fire in Wave 1 SCOPE-OUT) | S-13 HTTP 5xx or timeout on both initial call and one retry; OR S-13 returns 0 notes for a claim with a procedure code that ordinarily has associated notes | completeness_flags += ["CLINICAL_NOTES_UNAVAILABLE"]; completeness_indicator decremented; packet assembly continues and delivers INCOMPLETE_DELIVERED; ops alert via AuditLogEntry with action = INTEGRATION_DEGRADED; NO EscalationPacket to HITL queue — physician receives packet with explicit flag | Ops team via AuditLogEntry alert; physician receives completeness_flag | Packet delivery SLA (30 minutes from PENDING_PHYSICIAN_REVIEW) — the degradation must not delay packet delivery | If packet delivery SLA breached due to S-13 retry loop: cap retries at 1 (5 seconds after first failure); deliver packet without notes; do not wait for S-13 recovery |
| ET-B-03 | PhysicianReviewPacket delivery to S-08 fails (T-B-08 write returns HTTP 5xx or timeout) after one retry | S-08 HTTP 5xx or timeout on both the initial write and one retry (5 seconds after first failure) | Agent retries once after 5 seconds; on second failure, writes packet to S-07 with QUEUE_DELIVERY_FAILED flag; AuditLogEntry with action = PACKET_DELIVERY_FAILED; ops alert; ClaimRecord remains in CLINICAL_PACKET_ASSEMBLY — does not advance to PHYSICIAN_REVIEWING | Ops team via alert; VP Operations via daily dashboard | 15 minutes for ops to restore S-08 and confirm re-delivery | Ops escalation to senior IT; if S-08 unavailable > 1 hour, CMO notified; all clinical-path claims in CLINICAL_PACKET_ASSEMBLY suspended until S-08 confirmed restored |
| ET-B-04 | Physician has not responded to an assembled PhysicianReviewPacket (no action token received from S-08) within the HITL review SLA, OR physician has not approved/rejected the additional information request draft within 2 hours | No physician action token received from S-08 within 4 hours of packet delivered_at (matching CP-B-1 SLA below); OR no draft approval/rejection within 2 hours of T-B-09 delivery | EscalationPacket assembled with trigger_type = HITL_SLA_BREACH, trigger_signal_values = {claim_id, packet_id, delivered_at, elapsed_hours, sla_hours}; delivered to S-09; SLA_BREACHED flag set on PhysicianReviewPacket; escalation re-delivered to S-08 with URGENT flag | Physician HITL queue re-notified with URGENT flag; senior physician reviewer notified; VP Operations and CMO notified within 15 minutes of breach | 4 hours from PhysicianReviewPacket.delivered_at (primary SLA); 2 hours from draft delivery for additional info requests | Same as CP-B-1 breach action; daily SLA breach summary to VP Operations |
| ET-B-05 | Audit record generation (T-B-10) produces a record with any required field absent; OR T-B-02 invoked with wrong ClaimRecord.state; OR CalibrationRecord (VERIFICATION call site) not SIGNED at T-B-02 execution; OR PhysicianReviewPacket delivered with null completeness_indicator or absent completeness_flags | Any required AuditLogEntry field null or absent; OR ClaimRecord.state ≠ PENDING_PHYSICIAN_REVIEW at T-B-02 invocation; OR CalibrationRecord.state ≠ SIGNED at T-B-02 invocation; OR packet schema validation failure | ClaimRecord.state → PENDING_HITL_EXCEPTION; partial AuditLogEntry written with available fields; HITL_EXCEPTION_RAISED logged; EscalationPacket with trigger_type = AUDIT_FAILURE, trigger_signal_values = {missing_fields (list), claim_id, pipeline_step, actual_state (for state mismatch), packet_id (for completeness failures)} | HITL exception processor | 1 hour | Agent pipeline suspended for this claim; quality incident opened; CMO and VP Operations notified within 15 minutes; no further claims advance while root cause is unresolved |

---

## §8. Autonomy Matrix

The operational contract between the WS2 Clinical Review Support Agent and Greenfield Health Systems. Every agent action appears in exactly one tier.

**AGENT DECIDES ALONE (no HITL required):**
- Routing verification classification (T-B-02): when the Sonnet 4.6 classifier returns `CLINICAL` with confidence_score ≥ `CLINICAL_CONTENT_VERIFICATION_THRESHOLD` — agent confirms the routing is correct and advances to packet assembly without any intermediate human check.
- Prior authorisation history retrieval (T-B-03): binary API call; agent retrieves all records in the lookback window — no judgment required.
- Member claims history retrieval (T-B-04): binary API call; agent retrieves all records matching diagnosis cluster and lookback period — no judgment required.
- Medical necessity criteria retrieval (T-B-06): vector store query; agent retrieves top-3 chunks above similarity threshold — selection is algorithmic, not editorial.
- Packet completeness assessment (T-B-07): arithmetic computation of completeness_indicator and completeness_flags from retrieval results — fully deterministic rule set.
- Audit record generation (T-B-10): assembles and writes AuditLogEntry for every pipeline action — no judgment required.
- Escalation packet assembly (T-B-11): assembles and delivers EscalationPacket on any ET-B-01 through ET-B-05 trigger — no judgment required.
- Schema validation of inbound ClaimRecord at T-B-01.
- Reference data version check at pipeline startup (startup CalibrationRecord validation).

**AGENT ACTS, HUMAN NOTIFIED AFTER:**
- Pre-filled physician review packet delivery (T-B-08): agent assembles and delivers the PhysicianReviewPacket to S-08 directly after all context retrieval completes; VP Operations and CMO receive a daily batch summary including total packets delivered, average completeness_indicator, and counts of SCOPE-OUT and unavailable flags. This is the highest-autonomy action in the WS2 pipeline and is permitted only when routing verification is CONFIRMED_CLINICAL and all context retrieval has been attempted (with completeness result explicit).
- Incomplete packet delivery (T-B-08 with completeness_indicator < 1.000): agent delivers the packet with explicit completeness_flags — physician is informed of what is missing before reviewing. Ops team receives an alert for every CLINICAL_NOTES_UNAVAILABLE or CLAIMS_HISTORY_UNAVAILABLE flag (Wave 2). VP Operations receives daily count of incomplete deliveries by flag type.
- Clinical notes retrieval degradation (ET-B-02): when S-13 fails, agent marks the gap in the packet and delivers — physician is explicitly notified via completeness_flags; ops team receives an integration degradation alert.

**AGENT PROPOSES, HUMAN APPROVES BEFORE ACTION:**
- Additional information request draft assembly (T-B-09): when a physician flags a packet as insufficient and requests additional information, the WS2 agent drafts the provider outreach using Haiku 4.5. The physician must review and approve the draft in S-08 before it is dispatched to the provider portal (S-12). **The physician's approval is the gate** — the agent cannot dispatch the request without it.
- Routing verification conflict escalation (ET-B-01, ROUTING_VERIFICATION_CONFLICT): when WS2 returns ADMIN and WS1 returned CLINICAL, the escalation packet is delivered to the HITL routing review queue. The exception processor's resolution decision — return to admin pipeline or proceed with physician review — is the gate before either path advances. The agent proposes the escalation; the exception processor decides the routing.
- **Physician clinical determination — primary URAC/NCQA governance hard stop:** All clinical determinations (APPROVED with payment token, REJECTED with denial codes, PENDING_ADDITIONAL_INFO re-determination) are physician-issued tokens recorded in S-08. The WS2 agent has no role in this decision. The agent delivers the assembled packet and waits. The physician's signed token in S-08 is what transitions `PHYSICIAN_REVIEWING` to `APPROVED` or `REJECTED`. This is the terminal WS2 governance gate.

**HUMAN TAKES OVER (agent supports only):**
- Routing verification below threshold or uncertain (ET-B-01): exception processor in the ROUTING_REVIEW queue resolves the routing question. Once resolved, they record a disposition token in S-09: PROCEED_WITH_PHYSICIAN_REVIEW (agent re-queues the claim from PENDING_HITL_EXCEPTION to resume WS2 packet assembly) or RETURN_TO_ADMIN_PATH (WS1 pipeline is re-triggered from ROUTING state). The agent takes no further routing action until the token is received.
- Clinical documentation assembly when notes are fax-only or system-inaccessible: if clinical notes cannot be retrieved programmatically (system down, FHIR endpoint not available, or fax-only submission), the WS2 economic case for packet assembly partially collapses — a human coordinator must retrieve physical documentation and attach it to the S-08 record. The agent marks the gap; a human fills it.
- Any claim where the PhysicianReviewPacket completeness_indicator = 0.000 and no non-SCOPE-OUT context was retrieved (ET-B-05): exception processor assesses whether to proceed to physician review with a fully manual packet or to pend until retrieval is restored.
- Physician determination: medical necessity approval, denial, or additional information request. No agent action substitutes for this in any scenario. The physician owns the terminal determination.

---

**Enforcement mechanism:**

The primary governance gate for WS2 — blocking an automated outcome for clinical claims and requiring a physician determination token before `PHYSICIAN_REVIEWING` transitions to `APPROVED` or `REJECTED` — is classified as **procedure-dependent until confirmed**, consistent with the enforcement mechanism classification in D4a §8 and per `D4_integration_preamble.md` §3 sign-off integrity risk entry for S-08 (physician review queue interface).

**Architectural intent:** The `PHYSICIAN_REVIEWING → APPROVED` transition in the ClaimRecord state machine requires a physician-issued determination token recorded in S-08. The WS2 agent has no T-B-XX task that writes an APPROVED or REJECTED state to S-07 directly — it can only write state transitions up to and including `PHYSICIAN_REVIEWING`. All determination writes originate from physician action in S-08.

**Why procedure-dependent until confirmed:** System-enforced classification holds only if S-08 (physician review queue interface) enforces individual authenticated login before accepting a determination token — ensuring that every determination is attributable to a specific licensed reviewer and cannot be submitted by a non-physician or by automation. The integration preamble §3 S-08 sign-off integrity row notes that S-08 is Unknown availability (SCOPE-OUT) — the authentication model, whether it requires individual physician login, and whether it enforces an immutable audit trail of token submissions have not been confirmed. Until G-4 discovery resolves this, the gate is procedure-dependent.

**Classification decision:** Procedure-dependent, with the following controls until G-4 is resolved:
1. WS2 pipeline design: no task in the WS2 activity catalog writes `APPROVED` or `REJECTED` state to S-07. The pipeline physically terminates at `PHYSICIAN_REVIEWING`.
2. AuditLogEntry with `human_id` non-null is required for every `PHYSICIAN_REVIEWING → APPROVED` or `→ REJECTED` transition; an AuditLogEntry with `human_id = null` for these transitions is an ET-B-05 condition.
3. Monthly governance audit: verify zero `APPROVED` ClaimRecords whose AuditLogEntry for the PHYSICIAN_REVIEWING → APPROVED transition has `human_id = null` or `updated_by` equal to any agent instance ID.

**Consistency with D4a §8:** Both WS1 and WS2 enforcement mechanisms are classified procedure-dependent until the respective discovery gaps (G-3 for S-07 state machine enforcement, G-4 for S-08 authentication model) are resolved. The two governance gates are distinct: WS1's gate blocks the admin payment path from bypassing physician review; WS2's gate ensures physician review determinations are attributable to individual licensed reviewers. Both must appear as governance risks in their respective §12 failure modes sections (Pass 4 FM-A-5 for WS1; Pass 6 FM-B-5 for WS2).

**If G-4 discovery confirms S-08 requires individual authenticated physician login with an immutable audit trail:** update this section and WS2 §12 FM-B-5 to system-enforced. The AuditLogEntry human_id control (point 2) remains as defence-in-depth regardless.

---

*Pass 5b complete. Pass 6 appends §10–§14 to this file.*

---

## §10. State Model

*The full ClaimRecord state machine is defined in `D4_preamble_capability_spec.md` §2 (shared entity definition) and is authoritative for field names, enum values, and transition triggers. This section specifies (a) the WS2-owned transitions with their guard conditions, (b) the states outside WS2 scope for completeness, and (c) invalid transitions relevant to WS2's governance boundaries.*

---

```
Primary entity: ClaimRecord
Full state machine: see D4_preamble_capability_spec.md §2

States (16 total — SCREAMING_SNAKE_CASE):
  RECEIVED, PARSING, PARSE_FAILED, NORMALISED, ADMIN_VALIDATING,
  ROUTING, ADMIN_CLEARED, PAYMENT_CALCULATING, PENDING_PHYSICIAN_REVIEW,
  CLINICAL_PACKET_ASSEMBLY, PENDING_ADDITIONAL_INFO, PHYSICIAN_REVIEWING,
  PENDING_HITL_EXCEPTION, APPROVED, REJECTED, CLOSED

Initial state: RECEIVED (set by Intake & Anomaly Agent on claim creation)
Terminal states: PARSE_FAILED, CLOSED — no valid exit under any condition

WS2 ownership: WS2 reads and writes ClaimRecord beginning from
  PENDING_PHYSICIAN_REVIEW (the WS1 handoff state). States NORMALISED
  through PAYMENT_CALCULATING are owned by WS1 (read-only for WS2).
  States CLINICAL_PACKET_ASSEMBLY, PENDING_ADDITIONAL_INFO, and
  PHYSICIAN_REVIEWING are exclusively owned by WS2. APPROVED and REJECTED:
  WS2 writes these states only when recording a physician determination
  token received from S-08 — the physician is the decision maker; WS2 is
  the state transition recorder.

Transitions — WS2-owned (with guard conditions):

  PENDING_PHYSICIAN_REVIEW → CLINICAL_PACKET_ASSEMBLY
    Trigger: T-B-02 routing verification classification returns
      verification_result = CONFIRMED_CLINICAL
    Guard conditions:
      1. ClaimRecord.state = PENDING_PHYSICIAN_REVIEW at T-B-02 call time
         (enforced as T-B-02 pre-condition; fires ET-B-05 if violated)
      2. CalibrationRecord (VERIFICATION call site).state = SIGNED,
         cmo_signoff_date non-null (validated at agent startup; agent refuses
         to start without a valid VERIFICATION CalibrationRecord)
      3. ClinicalClassificationResult (call_site = VERIFICATION).state = CLASSIFIED
      4. ClinicalClassificationResult.classification = CLINICAL AND
         confidence_score ≥ CLINICAL_CONTENT_VERIFICATION_THRESHOLD
      5. ClaimRecord.clinical_classification_id_ws2 set to result id
      6. AuditLogEntry written with action = ROUTING_VERIFICATION_CONFIRMED,
         compliance_flags = ["URAC_NCQA_CLINICAL_GATE"]

  PENDING_PHYSICIAN_REVIEW → PENDING_HITL_EXCEPTION
    Trigger: ET-B-01 fires — routing verification returns UNCERTAIN (any
      confidence), ADMIN (conflict with WS1 routing), or CLINICAL below
      CLINICAL_CONTENT_VERIFICATION_THRESHOLD
    Guard conditions:
      1. EscalationPacket assembled with trigger_type =
         ROUTING_VERIFICATION_BELOW_THRESHOLD or ROUTING_VERIFICATION_CONFLICT
      2. EscalationPacket confirmed written to S-09 (ROUTING_REVIEW queue)
      3. hitl_queue_type = ROUTING_REVIEW set on ClaimRecord
      4. AuditLogEntry written with action = ROUTING_VERIFICATION_ESCALATED,
         input_summary including ws1_classification, ws1_confidence,
         ws2_classification, ws2_confidence, threshold_applied

  CLINICAL_PACKET_ASSEMBLY → PHYSICIAN_REVIEWING
    Trigger: T-B-08 delivers PhysicianReviewPacket to S-08 with confirmed write
    Guard conditions:
      1. PhysicianReviewPacket.state ∈ {COMPLETE, INCOMPLETE_DELIVERED}
         (both are valid delivery states; INCOMPLETE_DELIVERED requires
         completeness_flags set and non-empty)
      2. PhysicianReviewPacket.completeness_indicator non-null (float 0.000–1.000)
      3. PhysicianReviewPacket.completeness_flags array present (may be empty)
      4. PhysicianReviewPacket.physician_review_sla non-null (ISO 8601)
      5. S-08 write confirmed — delivery_at timestamp set in PhysicianReviewPacket
      6. AuditLogEntry written with action = PACKET_DELIVERED,
         entity_id = PhysicianReviewPacket.id, entity_type = "PhysicianReviewPacket"

  CLINICAL_PACKET_ASSEMBLY → PENDING_HITL_EXCEPTION
    Trigger: ET-B-03 (S-08 delivery fails after one retry) OR ET-B-05
      (packet schema validation failure — required fields null or absent)
    Guard conditions:
      1. For ET-B-03: initial write + one retry both failed; fallback write
         to S-07 attempted with QUEUE_DELIVERY_FAILED flag;
         AuditLogEntry written with action = PACKET_DELIVERY_FAILED
      2. For ET-B-05: T-B-08 schema validation detected completeness_indicator
         null, completeness_flags absent, or physician_review_sla null before
         S-08 write was attempted; delivery aborted
      3. EscalationPacket assembled and written; PhysicianReviewPacket
         state remains ASSEMBLING (not advanced to delivered)

  PHYSICIAN_REVIEWING → APPROVED
    Trigger: Physician records APPROVED determination token in S-08;
      WS2 receives the token and writes ClaimRecord.state = APPROVED to S-07
    Guard conditions:
      1. Physician determination token received from S-08 with
         determination_type = APPROVED and physician_id non-null
      2. AuditLogEntry.human_id = physician_id (non-null — URAC/NCQA hard stop;
         fires ET-B-05 if null; see FM-B-5 and §8 enforcement mechanism)
      3. AuditLogEntry.delegation_tier = HUMAN_DECIDES
      4. PhysicianReviewPacket.state ∈ {COMPLETE, INCOMPLETE_DELIVERED}
         (packet was delivered before determination was issued; confirmed
         by PhysicianReviewPacket.delivery_at non-null)
      5. ClaimRecord.state = PHYSICIAN_REVIEWING at time of token receipt
         (fires ET-B-05 if state mismatch)

  PHYSICIAN_REVIEWING → REJECTED
    Trigger: Physician records REJECTED determination token in S-08
    Guard conditions: same as PHYSICIAN_REVIEWING → APPROVED; additionally:
      1. denial_reason_codes (array) non-null and non-empty in physician token
      2. AuditLogEntry.output_summary includes denial_reason_codes array

  PHYSICIAN_REVIEWING → PENDING_ADDITIONAL_INFO
    Trigger: Physician records ADDITIONAL_INFO_REQUIRED token in S-08
    Guard conditions:
      1. AuditLogEntry.human_id = physician_id (non-null)
      2. AuditLogEntry.delegation_tier = HUMAN_DECIDES
      3. T-B-09 triggered immediately: Haiku 4.5 draft assembled from
         completeness_flags and claim context; delivered to S-08 for physician
         approval; AuditLogEntry written with action = ADDITIONAL_INFO_REQUEST_DRAFTED

  PENDING_ADDITIONAL_INFO → CLINICAL_PACKET_ASSEMBLY
    Trigger: Queue & SLA Management Agent notifies WS2 that provider
      documentation has been received (new documentation event on S-12)
    Guard conditions:
      1. Re-queue event received with provider_response_timestamp and
         documentation_reference non-null
      2. Prior PhysicianReviewPacket.state → SUPERSEDED (prior packet
         retained in audit trail — not deleted; id recorded in new packet's
         supersedes_packet_id field)
      3. New PhysicianReviewPacket.id assigned (UUID, distinct from prior)
      4. AuditLogEntry written with action = NEW_PACKET_ASSEMBLED_FOR_REVIEW,
         input_summary including prior_packet_id and
         reason = "ADDITIONAL_INFO_RECEIVED"
    Note: WS2 does NOT re-run T-B-02 routing verification on re-entry;
      CONFIRMED_CLINICAL routing is already established from the original
      T-B-02 result; only context retrieval (T-B-03 through T-B-06)
      and packet assembly (T-B-07 through T-B-08) are repeated

  PENDING_HITL_EXCEPTION → CLINICAL_PACKET_ASSEMBLY
    Trigger: HITL routing review exception processor resolves ET-B-01 with
      disposition PROCEED_WITH_PHYSICIAN_REVIEW (exception processor
      determines WS1's CLINICAL routing was correct)
    Guard conditions:
      1. Exception processor disposition token received from S-09 with
         resolution_type = PROCEED_WITH_PHYSICIAN_REVIEW
      2. AuditLogEntry.human_id = exception_processor_id (non-null)
      3. ClaimRecord.hitl_disposition = PROCEED_WITH_PHYSICIAN_REVIEW

  PENDING_HITL_EXCEPTION → ADMIN_VALIDATING (exception processor re-route)
    Trigger: HITL routing review exception processor resolves ET-B-01 with
      disposition RETURN_TO_ADMIN_PATH (exception processor determines
      WS1's CLINICAL routing was incorrect — claim is administrative)
    Guard: Exception processor token received; WS1 re-triggered from
      ROUTING state; WS2 pipeline terminates for this claim.
    Note: WS2 does not own this transition write — it belongs to the HITL
      exception processor or orchestration layer; included here for
      state machine completeness

Transitions outside WS2 scope (listed for completeness — WS2 does not write these):
  RECEIVED → PARSING: Intake & Anomaly Agent
  PARSING → PARSE_FAILED / NORMALISED: Intake & Anomaly Agent
  NORMALISED → ADMIN_VALIDATING → ROUTING: WS1
  ROUTING → ADMIN_CLEARED → PAYMENT_CALCULATING → APPROVED: WS1 (admin path)
  ROUTING → PENDING_PHYSICIAN_REVIEW: WS1 (WS2 pickup — ET-01 or ET-02)
  APPROVED → CLOSED: Payment system confirmation
  REJECTED → CLOSED: Provider portal confirmation

Invalid transitions (WS2-relevant — in addition to those defined in preamble):

  PHYSICIAN_REVIEWING → APPROVED (human_id = null): FORBIDDEN
    Reason: URAC/NCQA accreditation requires every clinical determination
    to be attributable to a specific licensed reviewer. An APPROVED
    transition with human_id = null is an unattributed determination —
    a direct compliance violation and the WS2 equivalent of the D4a
    PENDING_PHYSICIAN_REVIEW → APPROVED governance hard stop.
    Enforcement: ET-B-05 fires synchronously before any S-07 state write
    if the determination token from S-08 carries a null physician_id.
    See §8 enforcement mechanism and FM-B-5.

  CLINICAL_PACKET_ASSEMBLY → APPROVED: FORBIDDEN
    Reason: The PhysicianReviewPacket has been assembled but physician review
    has not commenced — no determination token has been issued.
    Any code path producing this transition is a critical defect: the
    physician review step was skipped entirely.

  PENDING_ADDITIONAL_INFO → APPROVED: FORBIDDEN
    Reason: Additional documentation was flagged as needed; the physician
    cannot have issued a final determination from PENDING_ADDITIONAL_INFO
    state. The required path is: additional info received →
    CLINICAL_PACKET_ASSEMBLY (new packet) → PHYSICIAN_REVIEWING →
    determination. This transition would bypass the mandatory re-review step.

  PENDING_PHYSICIAN_REVIEW → PHYSICIAN_REVIEWING: FORBIDDEN
    Reason: A ClaimRecord in PENDING_PHYSICIAN_REVIEW must pass through
    CLINICAL_PACKET_ASSEMBLY before physician review begins.
    CLINICAL_PACKET_ASSEMBLY is where WS2 runs routing verification (T-B-02)
    and assembles the pre-filled context packet. A direct transition to
    PHYSICIAN_REVIEWING would place the physician in review without
    verification and without a pre-filled packet — nullifying WS2's
    core job to be done.

  PHYSICIAN_REVIEWING → CLINICAL_PACKET_ASSEMBLY: FORBIDDEN
    Reason: Once physician review has commenced, WS2 cannot autonomously
    rebuild the packet. If additional context is needed, the physician must
    record ADDITIONAL_INFO_REQUIRED (→ PENDING_ADDITIONAL_INFO), which
    then triggers a new CLINICAL_PACKET_ASSEMBLY cycle via D-B-3.
    A direct re-entry to assembly would create a new packet without the
    physician's knowledge or consent — violating the physician's authority
    over the review process.
```

---

## §11. Error Handling

All failure categories are present. Every row names a detection method. Integration retrieval failures (S-04, S-14, S-13) degrade gracefully rather than aborting — the packet is delivered with explicit completeness flags.

| Failure | Detection method | Agent action | Human notification | Recovery path |
|---------|-----------------|--------------|-------------------|---------------|
| **Integration unavailable — S-04 (prior auth history)** | S-04 API returns HTTP 5xx or timeout after 5-second wait; retry fires after 5 seconds; second timeout or 5xx received | completeness_flags += ["PRIOR_AUTH_HISTORY_UNAVAILABLE"]; completeness_indicator decremented; packet assembly continues with missing element explicitly flagged; AuditLogEntry written with action = INTEGRATION_DEGRADED and trigger_signal_values = {system: "S-04", error_type: "API_UNAVAILABLE"} | Ops team via AuditLogEntry alert; physician receives packet with flag visible before clinical content | Ops confirms S-04 recovery; if physician has not yet reviewed the packet, WS2 can re-retrieve prior auth and deliver an updated packet (new PhysicianReviewPacket supersedes prior); if physician has already reviewed, the gap is documented in audit trail |
| **Integration unavailable — S-14 (member claims history)** | S-14 API returns HTTP 5xx or timeout after 5-second wait; retry fires; second failure received | completeness_flags += ["CLAIMS_HISTORY_UNAVAILABLE"]; completeness_indicator decremented; packet assembly continues; AuditLogEntry written with action = INTEGRATION_DEGRADED | Ops alert; physician receives packet with flag visible | Same recovery path as S-04 — WS2 can deliver an updated packet if S-14 recovers before physician reviews |
| **Integration unavailable — S-13 (clinical notes — Wave 2 only)** | S-13 returns HTTP 5xx or timeout on both initial call and one retry (Wave 2 only; does not fire in Wave 1 SCOPE-OUT where S-13_scope_out = true) | ET-B-02 fires: completeness_flags += ["CLINICAL_NOTES_UNAVAILABLE"]; completeness_indicator decremented; NO EscalationPacket to HITL queue; packet assembly continues; AuditLogEntry with action = INTEGRATION_DEGRADED; S-13 retry capped at 1 to prevent delaying packet delivery | Ops alert via AuditLogEntry; physician receives packet with flag visible | Ops investigates S-13 availability; if clinical notes are on a fax-only or inaccessible system, human coordinator retrieves and attaches documentation to S-08 record directly; WS2 delivers updated packet when documentation is attached |
| **Integration unavailable — S-08 (physician HITL queue)** | T-B-08 S-08 write returns HTTP 5xx or timeout; one retry fires after 5 seconds; second failure received | Agent retries once; on second failure, writes PhysicianReviewPacket to S-07 (claims management) with QUEUE_DELIVERY_FAILED flag; AuditLogEntry written with action = PACKET_DELIVERY_FAILED; ET-B-03 fires; ClaimRecord remains in CLINICAL_PACKET_ASSEMBLY — does not advance to PHYSICIAN_REVIEWING | Ops alert within 15 minutes; VP Operations via daily dashboard; CMO notified if S-08 unavailable > 1 hour | Ops confirms S-08 recovery; packet re-delivered; QUEUE_DELIVERY_FAILED flag cleared; ClaimRecord advances to PHYSICIAN_REVIEWING |
| **Integration unavailable — S-10 (audit log)** | S-10 API returns HTTP 5xx or timeout when T-B-10 attempts write; retry fires at 10-second intervals | Agent queues AuditLogEntry locally (in-memory, max 50 records); retries at 10-second intervals for up to 5 minutes; if S-10 unavailable at 5 minutes, agent suspends claim processing and alerts ops; no ClaimRecord advances while S-10 unavailable | Ops alert at first failure; escalation to ops lead at 5-minute threshold | Ops restores S-10; agent flushes queued entries in order; claim processing resumes |
| **Required data missing — PhysicianReviewPacket schema validation failure** | T-B-08 pre-delivery schema validation detects completeness_indicator null, completeness_flags absent, or physician_review_sla null before S-08 write is issued | Delivery aborted; ET-B-05 fires with trigger_signal_values = {missing_fields: [...], packet_id, pipeline_step: "T-B-08"}; ClaimRecord remains in CLINICAL_PACKET_ASSEMBLY; no partial packet delivered | HITL exception processor notified (1-hour SLA); CMO and VP Operations notified within 15 minutes | Exception processor investigates root cause; if a transient assembly error, T-B-07 and T-B-08 re-run; if a systematic defect, agent pipeline suspended |
| **Required data missing — ClinicalClassificationResult (VERIFICATION) reasoning chain absent or < 20 characters** | T-B-10 validates ClinicalClassificationResult before writing AuditLogEntry; checks reasoning_chain non-null and length ≥ 20 characters | ET-B-05 fires; ClaimRecord remains in CLINICAL_PACKET_ASSEMBLY; partial AuditLogEntry written with available fields; reasoning chain absence flagged in trigger_signal_values | Ops alert; CMO notified if pattern recurs (> 1% of verifications in any hour) | Ops investigates classifier output; if systematic, CMO-authorised re-run of T-B-02 classification; reasoning chain backfilled by clinical reviewer for audit defence |
| **Agent confidence below threshold — T-B-02 returns CLINICAL with confidence < CLINICAL_CONTENT_VERIFICATION_THRESHOLD** | T-B-02 classification evaluates confidence_score < CLINICAL_CONTENT_VERIFICATION_THRESHOLD; ET-B-01 threshold comparison (§6 D-B-1, CLINICAL_BELOW_THRESHOLD branch) | ET-B-01 fires with trigger_type = ROUTING_VERIFICATION_BELOW_THRESHOLD; ClaimRecord.state → PENDING_HITL_EXCEPTION; EscalationPacket with shortfall = threshold − confidence_score delivered to ROUTING_REVIEW queue | HITL routing review queue notified; ops dashboard BELOW_THRESHOLD count incremented | Exception processor reviews escalation and records disposition: PROCEED_WITH_PHYSICIAN_REVIEW (WS2 re-queues claim to CLINICAL_PACKET_ASSEMBLY) or RETURN_TO_ADMIN_PATH (WS1 re-triggered); if below-threshold rate exceeds 10% in a rolling 7-day window, CMO initiates VERIFICATION threshold review |
| **Governance hard stop triggered — REQ-B-6 content validation detects recommendation language in packet field** | Keyword detection against a CMO-validated exclusion list applied to clinical_notes_summary and any free-text packet field immediately after Haiku 4.5 content generation (T-B-08) | Flagged field replaced with raw retrieved text; ET-B-05 fires as audit flag (pipeline not suspended for this case alone — packet is delivered with raw text, not blocked); AuditLogEntry with action = GOVERNANCE_HARD_STOP_TRIGGERED and trigger_signal_values = {flagged_field, detected_pattern, packet_id} | CMO notified via AuditLogEntry; monthly governance review includes count of flagged content events | CMO reviews exclusion list adequacy; if systematic, T-B-08 prompt template updated and revalidated; all packets from the affected period reviewed for undetected bias |
| **SLA breach — physician has not responded within 4 hours of packet delivery** | ET-B-04 SLA monitor: elapsed time since PhysicianReviewPacket.delivery_at exceeds 4 hours (14,400 seconds) with no physician action token received from S-08 | ET-B-04 fires; EscalationPacket assembled with trigger_type = HITL_SLA_BREACH; SLA_BREACHED flag set on PhysicianReviewPacket; escalation re-delivered to S-08 with URGENT flag; AuditLogEntry written | Physician HITL queue re-notified with URGENT flag; senior physician reviewer notified; VP Operations and CMO notified within 15 minutes of breach; daily SLA breach summary | Senior physician reviewer assumes the claim; if systemic physician capacity issue, CMO and VP Operations convene to address queue staffing |

---

## §12. Failure Modes

**Distinct from §11.** These are wrong-output failures — the agent runs successfully but produces an incorrect, incomplete, or governance-violating result. Integration failures are in §11 and are not repeated here. All five failure modes are distinct from D4a §12: WS2's failure modes centre on packet content quality, verification accuracy, and physician sign-off attribution rather than payment path bypass.

---

```
Failure Mode FM-B-1: Packet content bias — Haiku-generated content
  approximates a recommendation
What bad output looks like: The clinical_notes_summary field in the
  PhysicianReviewPacket contains language generated by Haiku 4.5 that
  characterises the clinical content as supporting or not supporting
  medical necessity — e.g., "conservative treatment appears to have been
  exhausted," "the documentation indicates strong medical necessity,"
  or "prior claims history suggests the procedure may not be medically
  necessary." The content is framed as editorial interpretation rather
  than factual retrieval.

Why this is distinct from an integration failure: The packet is
  delivered successfully; the problem is the quality of the content
  assembled by the agent, not a missing field or a system error.

Consequence:
  - The physician reviews a packet that includes an implicit recommendation
    rather than neutral clinical context. The physician's judgment may be
    anchored by the agent-generated framing rather than being independent.
  - If the patient's claim is denied and the denial is appealed, the
    physician's determination may be challenged as having been influenced
    by an agent recommendation — undermining the clinical independence
    required by URAC/NCQA accreditation.
  - Regulatory: a pattern of recommendation-language packets is a
    systematic process failure that would require CMO-level corrective
    action under accreditation standards.

Detection:
  - Primary (synchronous): REQ-B-6 keyword detection at T-B-08 applied
    to Haiku 4.5 output; flagged content replaced with raw text and
    ET-B-05 audit flag fired. Latency: detected at generation time.
  - Secondary (asynchronous): Monthly content review of 100 consecutive
    PhysicianReviewPackets by a CMO-authorised clinical reviewer checking
    for recommendation language not caught by the keyword list. Latency:
    up to 30 days.
  - Systematic indicator: If the monthly content review catches ≥ 2
    packets with recommendation language not caught by keyword detection,
    CMO initiates prompt template review and exclusion list expansion.

Recovery path:
  1. Identified packet is flagged in S-08; physician reviewer is notified
     that the packet contains content under review.
  2. Physician issues determination based on raw source documents,
     not the flagged summary; the agent-generated summary is removed
     from the clinical decision record.
  3. CMO reviews the Haiku 4.5 prompt template used in T-B-09 and T-B-08
     content generation; expands the exclusion list.
  4. Retrospective review of packets from the prior 30 days using the
     updated exclusion list.
  Responsibility: CMO (prompt review, exclusion list); Clinical reviewer
    (retrospective audit); IT (prompt template update)
```

---

```
Failure Mode FM-B-2: Systematic verification miscalibration — WS2 confirms
  routing for claims that should have triggered HITL review
What bad output looks like: T-B-02 routing verification consistently returns
  CONFIRMED_CLINICAL for a specific procedure or diagnosis cluster at
  confidence_score ≥ CLINICAL_CONTENT_VERIFICATION_THRESHOLD, when
  a more careful review would return UNCERTAIN or identify the claim as
  ADMIN — i.e., WS2's VERIFICATION call is not providing genuine
  independent verification of WS1's routing, but rather echoing WS1's
  output due to shared bias in the classifier at a specific call site
  or for a specific code combination.

Why this is distinct from FM-B-1: FM-B-1 concerns content quality of the
  packet; FM-B-2 concerns the accuracy of the routing verification
  classification decision itself.

Consequence:
  - Claims that WS1 routed to PENDING_PHYSICIAN_REVIEW proceed to packet
    assembly without being caught by WS2 verification. If WS1's routing
    was correct, this is invisible. If WS1's routing was wrong (the claim
    is actually administrative), WS2 fails to surface the conflict.
  - The WS1/WS2 verification agreement rate KPI (< 1% disagreement target)
    may appear healthy when in fact both agents are systematically wrong
    in the same direction — a correlated failure mode that the agreement
    rate alone cannot detect.
  - Downstream: physicians review clinical packets for claims that do not
    require clinical review; physician time is consumed; physician queue
    depth grows.

Detection:
  - Monthly retrospective review of a random 5% sample of claims that
    WS2 verified as CONFIRMED_CLINICAL and that proceeded to physician
    review, checked against CMO-labelled ground truth.
    Latency: up to 30 days.
  - Population-level signal: If the physician determination outcome for
    a specific code range shows a high rate of APPROVED outcomes at
    low-complexity claims that CMO reviewers assess as routine, this
    suggests systematic over-routing to clinical review by both WS1
    and WS2. Latency: 30–60 days of data accumulation.

Recovery path — threshold retuning mechanism (same structure as FM-A-2):
  1. CMO initiates emergency recalibration for the VERIFICATION call site:
     new holdout set drawn from the affected procedure code range
     (≥ 200 claims labelled by CMO-authorised reviewers within 5 business days).
  2. Threshold sweep re-run at 0.05 increments from 0.50 to 0.95 on the
     new holdout set at call_site = VERIFICATION.
  3. If verification recall on the new holdout falls below 0.995 at the
     current threshold, the threshold is adjusted to the lowest value
     achieving ≥ 0.995 recall for genuinely clinical claims.
  4. New CalibrationRecord (VERIFICATION call site) created with
     state = DRAFT; CMO signs to SIGNED; current SIGNED record
     transitions to SUPERSEDED.
  5. Agent restarted with new signed VERIFICATION CalibrationRecord.
  6. CMO reviews whether the WS1 ROUTING CalibrationRecord also requires
     recalibration (correlated failure condition — per D3 ADR-2, the two
     thresholds are independent but the underlying model is shared).
  Responsibility: CMO (labelling, sign-off); IT/MLOps (threshold sweep);
    Claims Ops (retrospective review queue)
```

---

```
Failure Mode FM-B-3: Completeness indicator computed incorrectly —
  SCOPE-OUT items improperly included in denominator
What bad output looks like: PhysicianReviewPacket.completeness_indicator
  is calculated as retrieved_count / expected_count, where expected_count
  incorrectly includes SCOPE-OUT items (S-13 in Wave 1, S-15 throughout).
  A Wave 1 packet that successfully retrieved prior auth history and
  claims history (the only two non-SCOPE-OUT items) shows
  completeness_indicator = 0.500 (2/4) instead of 1.000 (2/2). The
  physician sees an apparent 50% incomplete packet for a claim where
  all retrievable context was actually assembled.

Consequence:
  - Primary: Physician may flag the packet as insufficient and trigger
    an additional information request (D-B-3) for documentation that
    does not exist in Wave 1 scope. An unnecessary provider outreach
    is dispatched — causing provider friction, adding cycle time to
    the claim, and consuming physician review time on an artificial gap.
  - Secondary: The packet completeness rate KPI (§0) is understated;
    Wave 1 performance appears worse than it is; CMO and VP Operations
    receive a misleading completeness picture.
  - Audit: If the completeness_indicator is wrong in the AuditLogEntry,
    the record understates the quality of the assembled context.

Detection:
  - Post-processing audit query (daily): count PhysicianReviewPackets in
    Wave 1 where completeness_indicator < 1.000 AND completeness_flags
    contains only SCOPE-OUT entries (CLINICAL_NOTES_SCOPE_OUT,
    CRITERIA_SECTION_UNAVAILABLE). If any such records exist, the D-B-2
    computation has a bug. Should return 0.
    Latency: up to 24 hours.
  - Build-time test: inject a Wave 1 claim with S-13_scope_out = true
    and S-15_scope_out = true; T-B-03 and T-B-04 return retrieved = true;
    expected completeness_indicator = 1.000. Test fails if any other value
    is computed (REQ-B-7 acceptance criterion covers this).

Recovery path:
  1. Identify all Wave 1 packets with incorrect completeness_indicator
     from the daily audit query.
  2. Recalculate completeness_indicator for each affected packet; update
     S-08 and AuditLogEntry records; notify physicians who received the
     affected packets.
  3. For any claims where an unnecessary additional information request
     was triggered: close the request; notify provider that no further
     documentation is needed; re-queue claim for physician review with
     corrected packet.
  4. IT patches the D-B-2 computation (ensure SCOPE-OUT items excluded
     from both numerator and denominator as specified in §6 D-B-2).
  Responsibility: IT (bug fix); Claims Ops (affected packet remediation);
    VP Operations (provider notification)
```

---

```
Failure Mode FM-B-4: Stale context — prior auth or claims history
  superseded between retrieval and physician review
What bad output looks like:
  Scenario A (prior auth renewal): Prior authorisation history retrieved
  by T-B-03 at 09:00 UTC shows PA-2026-004891 as the only active
  authorisation with expiry 2026-04-15. New prior auth PA-2026-011203
  is approved and added to S-04 at 10:00 UTC. Physician reviews the packet
  at 11:00 UTC and sees only the expiring prior auth — the new approval
  is not visible. Physician issues ADDITIONAL_INFO_REQUIRED for documentation
  that is already available in S-04.

  Scenario B (adverse prior history): Member claims history retrieved by
  T-B-04 at 09:00 UTC does not include a same-day claim from a different
  provider submitted to S-14 at 09:30 UTC (system processing lag).
  Physician reviews the packet without the same-day claim context —
  a prior history gap that could affect the medical necessity
  determination for a duplicate procedure.

Consequence:
  - Scenario A: Unnecessary additional information cycle (typically 5
    business days); physician time consumed; claim cycle extended;
    provider may receive a confusing additional info request.
  - Scenario B: Physician determination is based on incomplete member
    history. Depending on the clinical context, this could affect the
    medical necessity decision. The determination is not necessarily wrong,
    but it is made on incomplete context — an audit defensibility concern.

Detection:
  - No synchronous detection mechanism — WS2 retrieves context once and
    packages it; it does not re-query S-04 or S-14 between assembly and
    physician review.
  - Post-determination review: If a physician's determination is appealed
    and the appeals reviewer identifies a context gap (e.g., a prior auth
    that was present but not in the packet), this is the detection mechanism.
    Latency: appeal timelines (30–60 days post-determination).
  - Systematic signal: If the daily count of additional information requests
    citing PRIOR_AUTH_HISTORY_UNAVAILABLE exceeds a threshold (> 5% of
    clinical-path claims in a rolling 7-day window), investigate whether
    the cause is retrieval lag rather than genuine absence.

Recovery path:
  - For Scenario A: When the additional info request returns and the
    provider references existing documentation in S-04, Claims Ops
    recognises the retrieval lag scenario; WS2 re-retrieves prior auth
    and delivers an updated packet without the additional info cycle.
    Mitigation (design Wave 2): add a pre-delivery S-04 re-query to T-B-08
    if more than 60 minutes have elapsed since T-B-03 retrieval.
  - For Scenario B: If the gap is discovered post-determination via appeal,
    CMO clinical reviewer assesses whether the missed history would have
    changed the determination. If yes: re-determination initiated.
  Responsibility: Claims Ops (scenario A lag identification);
    CMO (scenario B re-determination assessment)
```

---

```
Failure Mode FM-B-5: Governance hard stop bypass — physician determination
  issued without attributed human_id
What bad output looks like: A ClaimRecord transitions from PHYSICIAN_REVIEWING
  to APPROVED or REJECTED and the AuditLogEntry for that transition has
  human_id = null — meaning no specific licensed physician was recorded as
  having issued the determination. The APPROVED or REJECTED state carries
  no attributable clinical reviewer sign-off.

How this could occur (the bypass conditions):
  1. Agent code defect: The §8 enforcement mechanism check — verifying
     that the physician token from S-08 carries a non-null physician_id
     before writing the state transition — is missing, disabled, or
     evaluates the wrong field.
  2. S-08 authentication model not enforcing individual login (G-4 gap —
     confirmed procedure-dependent in §8): If S-08 allows a shared account
     or a service account to submit a determination token without a
     physician-specific identifier, human_id in the token is null or a
     non-physician agent ID; WS2 cannot distinguish a physician token
     from an automated submission.
  3. Integration test harness misconfiguration: A test harness submits
     a synthetic determination token to WS2 with null physician_id;
     if the pre-production environment is not fully isolated, the
     synthetic token could advance a real ClaimRecord.
  4. Operator emergency bypass: An operator under time pressure submits
     a determination token directly to WS2's input queue without routing
     through the S-08 authentication flow, bypassing physician attribution.

Consequence:
  - An APPROVED or REJECTED clinical claim determination is unattributable —
    no licensed reviewer of record. This is a direct URAC/NCQA accreditation
    violation: clinical determinations must be made by licensed practitioners,
    and the identity of the practitioner must be recorded for accreditation
    audit purposes.
  - Unlike FM-B-2 (miscalibration — the routing decision may have been
    clinically justified), FM-B-5 is a process attribution bypass:
    a physician may have reviewed the claim in practice, but the record
    cannot prove it. The determination is undefendable under accreditation
    audit conditions.
  - Medical-legal: If the claim involves a denial and a member appeal is
    filed, the absence of a named reviewing physician in the determination
    record is a legal vulnerability for Greenfield Health Systems.
  - Compliance: Must be reported to URAC/NCQA under accreditation incident
    reporting if discovered in audit; potential accreditation suspension.

Detection:
  - Primary (synchronous): ET-B-05 check: before writing ClaimRecord.state =
    APPROVED or REJECTED to S-07, WS2 validates that the physician token
    from S-08 has non-null physician_id. If null: ET-B-05 fires; no state
    write occurs; ClaimRecord remains in PHYSICIAN_REVIEWING. This is the
    intended detection mechanism.
  - Secondary (asynchronous): Monthly governance audit query — verify zero
    AuditLogEntry records where action = PHYSICIAN_DETERMINATION_RECEIVED
    AND human_id is null. Should return 0.
  - Tertiary: G-4 discovery question to confirm whether S-08 enforces
    individual authenticated login before accepting a determination token.
    If not, bypass condition 2 is latent and persistent until G-4 mitigation
    is implemented.
  - Latency: Condition 1 (code defect) — detected at next physician
    determination receipt. Condition 2 (S-08 authentication gap) — detected
    by monthly governance audit (up to 30-day latency).

Recovery path:
  1. ET-B-05 fires; agent pipeline suspended for affected claim;
     CMO and VP Operations notified within 15 minutes.
  2. Compliance team identifies all determinations issued via the bypass
     (query APPROVED/REJECTED claims with human_id = null since last clean
     monthly audit).
  3. Each bypass-determination claim undergoes retroactive physician review:
     a named CMO-authorised physician reviews the clinical record and
     issues a signed retroactive determination token.
  4. If the retroactive determination confirms the original outcome:
     retroactive sign-off recorded; URAC/NCQA incident reported if
     the gap is material to accreditation.
  5. If the retroactive determination differs from the original outcome:
     re-adjudication process initiated.
  6. Root cause addressed: code defect patched (Condition 1);
     G-4 mitigation implemented if S-08 authentication model confirmed
     insufficient (Condition 2 — update S-08 to require individual
     physician login); test environment isolation enforced (Condition 3);
     operator access to WS2 input queue audited (Condition 4).
  Responsibility: CMO (retroactive review); Compliance (reporting);
    IT (root cause and G-4 mitigation); VP Operations (operator audit)

  This failure mode is a governance risk pending G-4 resolution.
  If G-4 confirms S-08 requires individual authenticated physician login
  with an immutable token audit trail, bypass conditions 2 and 4 are
  significantly mitigated; only conditions 1 (code defect) and 3
  (test harness) remain, and condition 1 is already detected synchronously
  by the ET-B-05 pre-write check.
```

---

## §13. Audit and Governance

### Audit Log Schema

Every WS2 agent action produces an AuditLogEntry using the shared entity definition in `D4_preamble_capability_spec.md` §2. The full field list is restated here with WS2-specific enum values and field constraints.

```json
{
  "id": "UUID — primary key, immutable, generated on creation",
  "timestamp": "ISO 8601 with timezone — UTC; set at write time; immutable",
  "agent_id": "string — WS2 agent instance identifier; non-null;
    format: 'ws2-crs-{instance_uuid}'",
  "action": "enum — exhaustive list of all WS2 action values:
    CLAIM_RECEIVED_BY_WS2,
    ROUTING_VERIFICATION_CONFIRMED,
    ROUTING_VERIFICATION_ESCALATED,
    PRIOR_AUTH_HISTORY_RETRIEVED,
    CLAIMS_HISTORY_RETRIEVED,
    CLINICAL_NOTES_RETRIEVED,
    CRITERIA_SECTION_RETRIEVED,
    INTEGRATION_DEGRADED,
    PACKET_COMPLETENESS_ASSESSED,
    PACKET_ASSEMBLED,
    PACKET_DELIVERED,
    PACKET_DELIVERY_FAILED,
    PHYSICIAN_DETERMINATION_RECEIVED,
    ADDITIONAL_INFO_REQUEST_DRAFTED,
    ADDITIONAL_INFO_REQUEST_DISPATCHED,
    ADDITIONAL_INFO_RECEIVED,
    NEW_PACKET_ASSEMBLED_FOR_REVIEW,
    CLAIM_STATE_TRANSITION,
    ESCALATION_TRIGGERED,
    ESCALATION_DELIVERED,
    ESCALATION_DELIVERY_FAILED,
    SCHEMA_VALIDATION_FAILED,
    GOVERNANCE_HARD_STOP_TRIGGERED,
    AUDIT_LOG_QUEUED_LOCAL,
    STARTUP_CALIBRATION_CHECK_PASSED,
    STARTUP_CALIBRATION_CHECK_FAILED",
  "entity_type": "string — 'ClaimRecord' | 'ClinicalClassificationResult' |
    'PhysicianReviewPacket' | 'EscalationPacket' | 'CalibrationRecord'",
  "entity_id": "UUID — foreign key to the entity being logged; non-null",
  "input_summary": "object — key fields used to make the decision:
    For ROUTING_VERIFICATION_CONFIRMED: {ws1_classification, ws1_confidence,
      ws2_classification, ws2_confidence, threshold_applied,
      calibration_record_id, call_site: 'VERIFICATION'}
    For ROUTING_VERIFICATION_ESCALATED: {ws1_classification, ws1_confidence,
      ws2_classification, ws2_confidence, threshold_applied,
      conflict: boolean, shortfall (if CLINICAL_BELOW_THRESHOLD)}
    For PACKET_DELIVERED: {completeness_indicator, completeness_flags,
      packet_id, physician_review_sla}
    For PHYSICIAN_DETERMINATION_RECEIVED: {determination_type,
      physician_id (human_id), packet_id, elapsed_hours_since_delivery}
    For ADDITIONAL_INFO_REQUEST_DISPATCHED: {missing_documentation_items,
      provider_npi, draft_approved_by: physician_id}
    For INTEGRATION_DEGRADED: {system_id, error_type,
      completeness_flag_added}",
  "output_summary": "object — what changed:
    For CLAIM_STATE_TRANSITION: {from_state, to_state, hitl_queue_type
      (if applicable), packet_id (if applicable)}
    For PHYSICIAN_DETERMINATION_RECEIVED: {determination_type,
      denial_reason_codes (if REJECTED), new_claim_state}
    For ESCALATION_DELIVERED: {escalation_packet_id, target_queue,
      delivery_confirmed: boolean}
    For PACKET_DELIVERY_FAILED: {fallback_target: 'S-07',
      QUEUE_DELIVERY_FAILED: true, packet_id}",
  "delegation_tier": "enum [AGENT_ALONE, AGENT_LOGS, AGENT_PROPOSES,
    HUMAN_DECIDES] — non-null; AGENT_ALONE for verification, retrieval,
    assembly, and completeness assessment; AGENT_PROPOSES for additional
    info draft; HUMAN_DECIDES for physician determination and draft approval",
  "human_id": "UUID or null — set when a physician or exception processor
    is the acting party; null for all fully agentic actions; MUST be
    non-null for PHYSICIAN_DETERMINATION_RECEIVED, for any
    PHYSICIAN_REVIEWING → APPROVED or → REJECTED state transition, and
    for ADDITIONAL_INFO_REQUEST_DISPATCHED (physician approval required);
    null human_id on any of these actions triggers ET-B-05",
  "confidence_score": "float 0.000–1.000 or null — non-null for T-B-02
    (routing verification classification); null for retrieval,
    arithmetic completeness assessment, and physician determination receipt",
  "escalation_triggered": "boolean — true if this log entry corresponds
    to an ET-B-01 through ET-B-05 trigger; false otherwise",
  "compliance_flags": "array of strings — zero or more values from:
    URAC_NCQA_CLINICAL_GATE (any ROUTING_VERIFICATION_CONFIRMED entry and
      any PHYSICIAN_DETERMINATION_RECEIVED transition),
    PHYSICIAN_ATTRIBUTION_REQUIRED (any APPROVED/REJECTED determination),
    RETRIEVAL_THRESHOLD_NOT_MET (S-15 below similarity threshold),
    SCOPE_OUT_S13 (clinical notes SCOPE-OUT in Wave 1),
    SCOPE_OUT_S15 (medical necessity criteria SCOPE-OUT throughout),
    INCOMPLETE_PACKET_DELIVERED (completeness_indicator < 1.000),
    GOVERNANCE_HARD_STOP_TRIGGERED — empty array [] is valid; null is not"
}
```

---

### Retention

| Log type | Retention period | Basis |
|----------|-----------------|-------|
| Compliance logs — all AuditLogEntry records for PHYSICIAN_DETERMINATION_RECEIVED, PHYSICIAN_REVIEWING → APPROVED/REJECTED state transitions, ROUTING_VERIFICATION_CONFIRMED records, and all CLINICAL_PACKET_ASSEMBLY transitions | 7 years from ClaimRecord.created_at | HIPAA 45 CFR § 164.530(j); URAC/NCQA accreditation audit evidence requirements — clinical determination records must be available for accreditation review |
| Operational logs — agent startup/shutdown, CalibrationRecord validation events, S-10 queue flush events, API retry events, INTEGRATION_DEGRADED events | 90 days from event timestamp | Operational troubleshooting; no regulatory requirement beyond incident investigation retention |
| Audit trail — all AuditLogEntry records regardless of type (superset of compliance logs) | 7 years from ClaimRecord.created_at | Same basis as compliance logs; the audit trail is a superset and the longest retention applies |
| CalibrationRecord (VERIFICATION call site) — signed calibration artefacts | 7 years from CalibrationRecord.cmo_signoff_date | URAC/NCQA accreditation: calibration evidence for the routing verification classifier must be available for accreditation audits |
| PhysicianReviewPacket records — all versions including SUPERSEDED | 7 years from ClaimRecord.created_at | Each packet version is part of the clinical review record; SUPERSEDED packets from additional-info cycles must be retained as the full clinical decision history |
| EscalationPacket records — ET-B-01 through ET-B-05 | 7 years from EscalationPacket.created_at | Any HITL routing or physician review escalation is a covered clinical workflow record; same 7-year basis |

---

### HITL Checkpoints

| Checkpoint | Trigger condition | Notified party | Required response | SLA | If SLA breached |
|------------|-------------------|----------------|-------------------|-----|-----------------|
| CP-B-1: Physician clinical determination (primary URAC gate) | PhysicianReviewPacket delivered to S-08; ClaimRecord.state = PHYSICIAN_REVIEWING | CMO-authorised physician or advanced practice provider via S-08 physician HITL queue | Physician records a signed determination token in S-08 with one of: APPROVED (proceed; determination written to S-07), REJECTED (denial with reason codes; rejection notice queued), or ADDITIONAL_INFO_REQUIRED (triggers D-B-3 additional info cycle). A free-text note is permitted but does not substitute for the structured token. The token must carry a non-null physician_id attributable to a licensed reviewer. | 4 hours from PhysicianReviewPacket.delivery_at | SLA_BREACHED flag set on PhysicianReviewPacket; ET-B-04 fires; escalation re-delivered with URGENT flag to senior physician reviewer; VP Operations and CMO notified within 15 minutes; daily SLA breach log generated |
| CP-B-2: Routing verification conflict or below threshold (ET-B-01) | T-B-02 routing verification returns ROUTING_VERIFICATION_CONFLICT (WS2 returns ADMIN contradicting WS1's CLINICAL routing), ROUTING_VERIFICATION_BELOW_THRESHOLD (CLINICAL below 0.85), or VERIFICATION_UNCERTAIN | HITL routing review exception processor via S-09 exception management; CMO notified if weekly conflict rate > 1% | Exception processor records disposition: PROCEED_WITH_PHYSICIAN_REVIEW (WS2 re-queues claim from PENDING_HITL_EXCEPTION to CLINICAL_PACKET_ASSEMBLY) or RETURN_TO_ADMIN_PATH (WS1 re-triggered from ROUTING state; WS2 pipeline terminates for this claim). Exception processor may not leave the claim in PENDING_HITL_EXCEPTION without recording a disposition within the SLA. | 2 hours from EscalationPacket.created_at | Exception processor supervisor notified; claim re-tagged URGENT in ROUTING_REVIEW queue; SLA breach event written to AuditLogEntry; if weekly conflict rate > 1%, CMO-initiated calibration review triggered |
| CP-B-3: Additional information request draft approval (D-B-3 physician gate) | Physician records ADDITIONAL_INFO_REQUIRED token in S-08; Haiku 4.5 drafts additional information request; draft delivered to S-08 for physician review | CMO-authorised physician (same physician who flagged the packet as insufficient) via S-08 | Physician records one of: DRAFT_APPROVED (draft dispatched to provider portal S-12 as-is), DRAFT_APPROVED_WITH_MODIFICATIONS (physician's edited version dispatched — original agent draft retained in audit trail), or DRAFT_REJECTED (physician provides replacement text; replacement dispatched). Agent never dispatches the request without one of these three responses. | 2 hours from draft delivery to S-08 | ET-B-04 fires (HITL_SLA_BREACH); URGENT re-notification to physician; if physician non-responsive after re-notification, CMO assigns a covering reviewer for the additional info request |
| CP-B-4: Physician SLA re-notification — ET-B-04 breach | No physician action token received from S-08 within 4 hours of PhysicianReviewPacket.delivery_at; OR no draft approval within 2 hours of CP-B-3 draft delivery | Senior physician reviewer via escalation path; VP Operations and CMO within 15 minutes of breach | Senior reviewer assumes responsibility for the claim and records a determination or draft approval within the escalation SLA. VP Operations records the breach in the daily SLA report. | No additional SLA defined — escalation to senior reviewer is immediate; daily SLA breach summary to CMO and VP Operations captures accumulated breach count | CMO convenes capacity review if weekly SLA breach count exceeds threshold; VP Operations adjusts physician queue staffing |

---

### Compliance Constraints

| Framework | Specific requirement for this agent |
|-----------|-------------------------------------|
| **HIPAA — 45 CFR Part 164 (Security and Privacy)** | All ClaimRecord data, PhysicianReviewPacket contents (diagnosis codes, procedure codes, clinical notes, prior auth history, member claims history), and AuditLogEntry records constitute Protected Health Information (PHI). The agent must transmit to and from S-04, S-07, S-08, S-09, S-10, S-12, S-13, S-14, S-15, S-16 only over encrypted channels (TLS 1.2 minimum). The minimum-necessary principle applies to WS2 specifically: the agent retrieves prior auth history and claims history scoped to the current procedure type and a defined lookback period — it does not retrieve the member's full medical record. PhysicianReviewPacket contents are pre-assembled context; the physician does not need to access raw S-04 or S-14 directly. AuditLogEntry records must be retained 7 years per the Retention table above. |
| **URAC/NCQA Accreditation Standards — Clinical Review (primary WS2 obligation)** | A physician or advanced practice provider must make every clinical necessity determination and must be individually identifiable in the determination record. This is the primary driver of the human_id = non-null hard stop in §8 and FM-B-5. The pre-filled PhysicianReviewPacket is the mechanism by which WS2 supports clinical review quality and efficiency — it must not substitute for clinical judgment. The VERIFICATION CalibrationRecord (§0 and §3) is the audit artefact demonstrating that the routing confirmation mechanism meets the accreditation-required recall threshold. The agent must never produce or approximate a determination in any packet field. |
| **Prompt Payment Laws — State Insurance Regulations** | The WS2 packet delivery SLA (≤ 30 minutes from PENDING_PHYSICIAN_REVIEW) and physician review SLA (4 hours, CP-B-1) are internal targets designed to ensure the aggregate adjudication cycle time stays within the statutory 30-day maximum. The additional information request cycle time (≤ 5 business days, §0 KPI) is a secondary SLA that must be managed to preserve the 30-day statutory deadline for the overall claim. The Queue & SLA Management Agent monitors ClaimRecord.sla_deadline and escalates if the cycle time is at risk of breaching the statutory deadline — WS2 does not own deadline enforcement; it owns packet delivery and physician queue management within the clinical path. |
| **URAC/NCQA — Physician Attribution and Sign-Off Integrity** | Every determination on a clinical claim must be attributable to a licensed practitioner. The physician's determination token (CP-B-1) must carry a non-null physician_id that maps to a CMO-authorised reviewer. The agent is responsible for verifying that the token it receives from S-08 carries a non-null, non-agent-instance physician_id before writing the state transition. If S-08 does not enforce individual physician authentication (G-4 gap — see §8 enforcement mechanism), this requirement cannot be fully system-enforced; it is procedure-dependent and subject to the FM-B-5 governance risk until G-4 is resolved. |
| **State Insurance Fraud, Waste, and Abuse (FWA) Requirements** | The additional information request cycle (D-B-3, T-B-09) generates an AuditLogEntry trail of every request dispatched to providers. This trail supports FWA investigation for patterns of provider behaviour (e.g., repeated submission of incomplete documentation, systemic omission of specific documentation types). The completeness_flags array in the PhysicianReviewPacket and the ADDITIONAL_INFO_REQUEST_DISPATCHED AuditLogEntry records are the audit artefacts for this requirement. |

---

## §14. Spec Ambiguity Register

| Item | Type | Confidence | Description | Impact if unresolved | Resolution |
|------|------|------------|-------------|----------------------|------------|
| A-D4b-1 | Spec ambiguity | Low | **S-13 clinical notes system — SCOPE-OUT in Wave 1; API availability unconfirmed for Wave 2.** The clinical notes system referenced in §2 (inputs), §4 T-B-05, §6 D-B-2, and §7 ET-B-02 is not named in the scenario. No EHR system, FHIR endpoint, document management platform, or API is identified. The integration preamble §2 classifies this as gap G-5. Wave 1 operates without clinical notes; Wave 2 requires a confirmed API before clinical notes retrieval can be built. The completeness_indicator logic correctly excludes S-13 from the Wave 1 denominator (D-B-2), but the Wave 2 retrieval task (T-B-05) cannot be implemented without a confirmed integration. | Without a confirmed S-13 API: T-B-05 cannot be built for Wave 2; the packet completeness rate KPI (≥ 85% Wave 2 target, §0) cannot be validated; the CMO's benefit case for WS2 — specifically the reduction in physician document-hunting time — depends on clinical notes being retrievable. If notes are fax-only or EHR-inaccessible, the Wave 2 completeness target is unachievable and the physician time savings estimate must be revised downward. Builder implements Wave 1 behaviour (S-13 SCOPE-OUT stub) only; Wave 2 T-B-05 implementation blocked until discovery resolved. | Discovery action (from integration preamble G-5): Ask Greenfield IT and CMO: "What system holds clinical notes for procedures requiring physician review? Does it have a FHIR R4 API or structured query interface? If not, what is the retrieval mechanism (fax, portal, manual)?" Resolution owner: IT / CMO. Until resolved: builder implements D-B-2 with S-13_scope_out = true; T-B-05 is stubbed out for Wave 1. |
| A-D4b-2 | Spec ambiguity | Low | **S-15 medical necessity criteria vector store — SCOPE-OUT; API availability unconfirmed.** S-15 is referenced in §1 (out-of-scope), §2 (inputs, SCOPE-OUT), §4 T-B-06, §6 D-B-1, and D-A-2 (WS1 uses S-15 for T-05 plausibility as well). Both WS1 and WS2 are affected. The integration preamble §2 classifies this as gap G-6. Without S-15, T-B-02 routing verification runs without criteria augmentation; this may affect the VERIFICATION threshold calibration results (the CMO holdout set process at §0 would need to be run without retrieval augmentation). | Without S-15: T-B-02 operates on classifier signal only; the CalibrationRecord calibration sweep must account for non-augmented operation; the threshold required to achieve ≥ 99.5% recall may differ from the augmented case. Builder implements T-B-02 without S-15 retrieval; criteria_chunks = [] on every call; compliance_flags += ["CRITERIA_SECTION_UNAVAILABLE"] on all verification results in SCOPE-OUT state. The WS1/WS2 agreement rate KPI must be monitored in SCOPE-OUT mode to establish a baseline before S-15 is added. | Discovery action: Ask Greenfield IT and CMO: "Does an electronic medical necessity criteria source exist (e.g., InterQual, MCG Health)? Is there an API or vector-indexable document set?" Resolution owner: CMO / IT. Until resolved: builder implements D-B-1 without S-15 retrieval; threshold calibration must be run on non-augmented operation. |
| A-D4b-3 | Spec ambiguity | Low | **G-4 gap — S-08 physician review queue authentication model unconfirmed.** §8 enforcement mechanism classifies the PHYSICIAN_REVIEWING → APPROVED determination gate as procedure-dependent until G-4 is resolved. The integration preamble §3 S-08 sign-off integrity row records that S-08 is Unknown availability (SCOPE-OUT) — whether S-08 requires individual authenticated physician login before accepting a determination token has not been confirmed. This is the foundational risk for FM-B-5 (governance hard stop bypass). | If S-08 does not enforce individual physician authentication: the human_id = non-null check in WS2 (§8 control 2) can be satisfied by any submitter who can access the S-08 token endpoint. Bypass conditions 2 and 4 in FM-B-5 (shared account submission, operator direct submission) become latent risks that cannot be mitigated purely in agent code. Builder must implement the synchronous ET-B-05 pre-write check as the primary control; cannot rely on S-08 as a system-enforced authentication barrier until confirmed. §8 classification and FM-B-5 severity both depend on this answer. | Discovery action: Ask Greenfield IT and CMO: "Does the physician review queue system (S-08) enforce individual authenticated login for each determination submission? Does it generate an immutable audit trail recording the specific licensed practitioner who submitted each token?" If yes: update §8 to system-enforced; reduce FM-B-5 severity. If no: require G-4 mitigation (S-08 system update or middleware authentication wrapper). Resolution owner: IT / CMO. |
| A-D4b-4 | Design gap | Low | **Routing verification agreement rate baseline — not measured.** §0 KPI states a target of < 1% disagreement rate between WS1 routing and WS2 verification classifications. This target is set on the basis of the design intent (verification should largely confirm routing), but the baseline disagreement rate — what WS1 and WS2 would actually disagree on at their respective calibrated thresholds — has not been measured against any labelled data. The 1% target may be achievable or may be inconsistent with the calibrated threshold values. | Builder cannot establish a pre-deployment baseline for this KPI. If the calibrated WS1 threshold (ROUTING, default 0.70) and WS2 threshold (VERIFICATION, default 0.85) create a systematic divergence on borderline cases (i.e., claims that WS1 classifies CLINICAL at 0.71 that WS2 classifies ADMIN at 0.85+), the disagreement rate may structurally exceed 1% without either classifier being miscalibrated. The KPI target would need to be revised. | Discovery action: Run the calibration sweep for both call sites simultaneously on the CMO holdout set and compute the disagreement rate at the calibrated thresholds. Adjust the KPI target based on measured disagreement at optimal thresholds. This discovery action should occur during the CalibrationRecord creation process before go-live, not separately. Resolution owner: CMO / MLOps. Confidence will remain Low until the calibration sweep is complete. |
| A-D4b-5 | Design gap | Low | **Physician document-hunting time baseline — no scenario measurement.** §0 KPI and §1 purpose statement reference 30–45 minutes of physician time per claim consumed in manual document hunting as the baseline being eliminated. This estimate appears in the purpose statement as Assumption A-D4b-5. The scenario does not provide a measured baseline; the 30–45 minute figure is an assertion without a source. The WS2 business case (estimated time savings × physician hourly cost × clinical claim volume) depends entirely on this assumption. | If the actual physician document-hunting time is materially different (e.g., 10–15 minutes because current systems have a basic chart-pull integration, or > 60 minutes because documentation is entirely fax-based), the time savings KPI (§0 Time to packet delivery ≤ 30 min) may be trivially achievable or structurally impossible. The financial justification for WS2 investment changes significantly. | Discovery action: Ask CMO and a sample of clinical reviewers: "How long does it currently take to manually assemble prior auth history, claims history, and clinical notes for a clinical claim before beginning the medical necessity review? Is there an existing time-motion study or physician time log?" Resolution owner: CMO. Until confirmed: FDE should present the 30–45 minute estimate as unvalidated in stakeholder communications; the ≤ 30 minute packet delivery target is achievable by design regardless of baseline. |

*Pass 6 complete. Pass 7 writes integration contracts to `Deliverables/D4_integration_specs.md`.*


---

# D4 — Canonical Normalized Claim Record
## Greenfield Health Systems: Intake Agent Output Contract

*Schema derived from: representative sampling of 2–3 files per Claims Pack format family (all 8 formats). Parse success/failure rates in §9 are empirically validated against the full Tier 1 population: 1,000 EDI 837P + 200 EDI 837I + 400 Portal JSON files (1,600 total). Tier 2 and Tier 3 format rates (CMS-1500 OCR, FHIR R4, email, fax, exception notes) are sample-only estimates.*

*This document is the architectural contract between the Intake Agent and WS1 (Administrative Adjudication Agent). Both agents are bound by this contract: the Intake Agent produces it, WS1 consumes it. Neither may deviate from it without a versioned contract change reviewed by both agent owners.*

---

## §1. Rationale for a Separate Canonical Record

WS1 operates on a normalized claim record. By the time a claim reaches WS1, the Intake Agent has already extracted it from whichever of the 8 intake formats it arrived in. WS1 sees the same normalized structure regardless of source format — this is the architectural isolation that allows WS1 adjudication logic to be tested independently of format parsing.

The canonical record is **not** the same as `ClaimRecord` in `D4_preamble_capability_spec.md §2`. `ClaimRecord` is the database entity with state, SLA, and audit relationships. The canonical normalized record is the **intake output payload** — the flat dict/JSON that the Intake Agent writes and WS1 reads at the start of each pipeline invocation. The two are related: the canonical record fields map 1:1 onto the creation-time fields of `ClaimRecord`. The distinction matters because:

- The canonical record is a wire format (Python dict / JSON payload), not a database row
- It exists from the moment extraction completes until WS1 consumes it
- It carries source tracking metadata (`source_format`, `source_file`, `intake_warnings`) that `ClaimRecord` does not need to persist after creation

---

## §2. Entity: NormalizedClaimInput

```
Entity: NormalizedClaimInput
Version: 1.0
Owner: Intake Agent (producer), WS1 (consumer)
Format: flat JSON object / Python dict

HARD REQUIRED — extraction fails, claim → PARSE_FAILED if absent:
  claim_id             str       Unique claim identifier from the source document.
                                 Max 64 chars. Must be non-empty after whitespace strip.
  diagnosis_codes      list[str] ICD-10 codes. Min 1 element. Each element must match
                                 the pattern: letter + 2–7 alphanumeric chars (e.g. "E11.9",
                                 "M54.5", "Z00.00"). Codes are upper-cased on normalization.
  procedure_codes      list[str] CPT or HCPCS codes. Min 1 element. For CPT: 5-digit numeric
                                 string (e.g. "99213"). For HCPCS Level II: letter + 4 digits.
                                 Extracted without modifiers (modifiers go in modifier_codes).

SOFT REQUIRED — missing triggers intake_warning entry, default applied, pipeline continues:
  member_id            str       Insurance member ID. Default: "UNKNOWN_MEMBER".
                                 Max 32 chars.
  provider_npi         str       Rendering provider NPI (10-digit numeric string per CMS).
                                 Default: "UNKNOWN_NPI". Max 10 chars.
  provider_specialty   str       Provider specialty label. Default: "Unknown".
                                 Derived from: structured field (portal-JSON), name heuristics
                                 (EDI), FHIR provider.display (text parse), or LLM extraction.
                                 Max 128 chars.
  date_of_service      str       Service date, ISO 8601 format YYYY-MM-DD.
                                 For multi-line claims: earliest line item date.
                                 Default: "unknown".
  procedure_quantities list[int] Unit count per procedure line. Position-aligned with
                                 procedure_codes: procedure_quantities[i] is the unit count for
                                 procedure_codes[i]. Each value ≥ 1.
                                 Default: [1] × len(procedure_codes).
                                 Array length must equal procedure_codes length.
  billed_amount        float     Total billed amount in USD. Default: 0.0. Min: 0.0.

OPTIONAL — populated when available in the source format, null otherwise:
  payer_id             str|null  Payer / insurance plan identifier. Null if not extractable.
                                 Note: email and CMS-1500 OCR may yield a plan name, not a
                                 machine-readable ID. When a name is extracted (not an ID),
                                 the value is stored and "payer_id_is_name" added to
                                 intake_warnings. Null if neither name nor ID available.
  group_id             str|null  Insurance group or plan identifier. Available in: portal-JSON
                                 (insurance.group_id), CMS-1500 OCR (field 11), email (body
                                 "Group:" field). Not available in: EDI 837P/837I, FHIR R4.
  place_of_service     str|null  CMS place-of-service code (2-digit string). Available in:
                                 EDI 837I (CLM element 5 component 1), CMS-1500 OCR (field
                                 24B), portal-JSON (service_lines[].place_of_service if
                                 present). Not in FHIR R4 core Claim resource.
  modifier_codes       list[str] CPT modifier codes (2-character alphanumeric). Available in:
                                 EDI SV1 or SV2 modifier elements, portal-JSON, FHIR item.modifier.
                                 Default: [].
  prior_auth_number    str|null  Prior authorization reference number. Available in: EDI REF
                                 segment with qualifier G1 or F5, portal-JSON
                                 (service_lines[].prior_auth_number if present). Null if absent.
  resubmission_of      str|null  Original claim ID this submission corrects. Available in: EDI
                                 CLM element 19 (frequency code 7 or 8), portal-JSON
                                 (resubmission_of if present). Null if not a resubmission.

SOURCE TRACKING — always present, set by Intake Agent, never null:
  source_format        str       Format of the source document. Enum:
                                   EDI_837P        — X12 837 Professional
                                   EDI_837I        — X12 837 Institutional
                                   PORTAL_FORM     — Portal JSON (nested submitter/patient/
                                                     insurance/service_lines/diagnoses shape)
                                   FHIR_R4         — FHIR R4 Claim resource
                                   CMS1500_OCR     — CMS-1500 paper form, OCR-extracted text
                                   EMAIL           — RFC 5322 .eml with X-Submitter-NPI header
                                   FAX             — Fax cover sheet PDF
                                   EXCEPTION_NOTES — Exception notes PDF (typed, handwritten,
                                                     call logs)
  source_file          str       Original filename from the intake queue.
                                 e.g. "CLM-2026-1000001.edi", "CLM-2026-0000001.json"
  intake_warnings      list[str] Quality issues detected during extraction. Empty list if none.
                                 Standardized warning strings (see §4).
```

---

## §3. Format-to-Field Extraction Map

This table shows the extraction source for each field in each format. "LLM" means one Haiku call per document is required; "Parser" means deterministic rule-based extraction.

| Field | EDI 837P | EDI 837I | Portal JSON | FHIR R4 | CMS-1500 OCR | Email .eml | Fax / Exception |
|-------|----------|----------|-------------|---------|--------------|------------|-----------------|
| **claim_id** | CLM[1] | CLM[1] | `submission_id` | `id` | Field 26 (OCR) | Body: "Claim reference:" | LLM |
| **member_id** | NM1\*IL[9] | NM1\*IL[9] | `insurance.member_id` | `patient.reference` strip "Patient/" | Field 1a (OCR) | Body: "Member ID:" | LLM |
| **provider_npi** | NM1\*85[9] | NM1\*85[9] (may be empty) | `submitter.npi` | `provider.reference` strip "Practitioner/" | Field 33 NPI box (OCR, often empty) | `X-Submitter-NPI` header | LLM |
| **provider_specialty** | Name heuristics on NM1\*85[3] | "Hospital/Institutional" (institutional always) | `submitter.specialty` | Text parse on `provider.display` (e.g. "Sophia Reyes, MD") | Field 31 or 17 (OCR) | Body: "Specialty:" | LLM |
| **date_of_service** | DTP\*472[3] → YYYY-MM-DD | DTP\*472[3] → YYYY-MM-DD | min(`service_lines[].date_of_service`) | min(`item[].servicedDate`) | Field 24A (OCR, MMDDYYYY) | Body: service date | LLM |
| **diagnosis_codes** | HI segments with AB-prefix qualifiers (ABK, ABF) | HI segments with AB-prefix qualifiers | `[d.code for d in diagnoses]` | `diagnosis[].diagnosisCodeableConcept.coding[0].code` | Field 21 (OCR, up to 12 codes) | Body: ICD code patterns | LLM |
| **procedure_codes** | SV1[1] component after "HC:" | SV1[1] or SV2[1] component after "HC:" | `[sl.cpt_code for sl in service_lines]` | `item[].productOrService.coding[0].code` | Field 24D (OCR, 5-digit CPT) | Body: "CPT XXXXX" patterns | LLM |
| **procedure_quantities** | SV1[4] (units) | SV1[4] or SV2[4] | `[sl.units for sl in service_lines]` | `item[].quantity.value` | Field 24G (OCR) | Body: "N unit(s)" | LLM |
| **billed_amount** | CLM[2] | CLM[2] | `total_charge_amount` | `total.value` | Field 28 (OCR, dollar amount) | Body: total or per-line sum | LLM |
| **payer_id** | NM1\*40[9] | NM1\*40[9] | `insurance.payer_id` | `insurer.reference` strip "Organization/" | Field 11c (payer name, not ID — warns) | Body: "Plan:" (name — warns) | LLM |
| **group_id** | Not available | Not available | `insurance.group_id` | Not in core Claim | Field 11 (OCR) | Body: "Group:" | LLM |
| **place_of_service** | CLM[4][0] (POS in CLM compound) | CLM[4][0] or BHT facility | Not standard | Not in core R4 | Field 24B (OCR) | Not standard | LLM |
| **modifier_codes** | SV1 elements [5]–[8] | SV1/SV2 modifier elements | `service_lines[].modifiers` (if present) | `item[].modifier[].coding[0].code` | Field 24D suffix (OCR) | Rare | LLM |
| **prior_auth_number** | REF\*G1 or REF\*F5[2] | REF\*G1 or REF\*F5[2] | `service_lines[].prior_auth_number` (if present) | `item[].careTeamSequence` (indirect) | Field 23 (OCR) | Rare | LLM |
| **source_format** | "EDI_837P" (from GS[8] 005010X222A1) | "EDI_837I" (from GS[8] 005010X223A2) | "PORTAL_FORM" | "FHIR_R4" | "CMS1500_OCR" | "EMAIL" | "FAX" / "EXCEPTION_NOTES" |
| **source_file** | Filename | Filename | Filename | Filename | Filename | Filename | Filename |

---

## §4. Standardized intake_warnings Strings

| Warning key | Trigger condition | Impact |
|-------------|-------------------|--------|
| `member_id_missing` | No member ID extractable | Default applied; eligibility check will fail |
| `provider_npi_missing` | No NPI in source document | Default applied; code validity may fail |
| `provider_npi_empty_segment` | NPI segment present but value empty (EDI 837I institutional) | Common for hospital billing; default applied |
| `provider_specialty_unknown` | No specialty extractable or derivable | Default "Unknown"; classifier loses one signal |
| `date_of_service_missing` | No service date extractable | Default applied; downstream date validation will flag |
| `payer_id_is_name` | Payer field contains a plain-text name, not a machine ID (email, CMS-1500) | payer_id stored as name string; eligibility lookup may fail |
| `diagnosis_codes_none` | Zero ICD codes extracted — hard failure | Claim → PARSE_FAILED |
| `procedure_codes_none` | Zero CPT codes extracted — hard failure | Claim → PARSE_FAILED |
| `ocr_confidence_low` | CMS-1500 OCR confidence score below 0.80 | Extracted fields may have OCR errors; verify against billed amount |
| `ocr_field_unparseable` | Specific OCR field could not be parsed (e.g. field 26 claim ID garbled) | Named field set to null or default |
| `quantities_length_mismatch` | procedure_quantities length ≠ procedure_codes length | Quantities reset to [1] × len(codes) |
| `billed_amount_zero` | billed_amount extracted as 0.0 or not found | Default applied; downstream payment calculation will flag |
| `fhir_billable_period_reversed` | FHIR billablePeriod.start > billablePeriod.end (data quality) | Logged; date_of_service derived from item-level dates instead |
| `llm_extraction_low_confidence` | LLM extraction (Haiku) returned confidence < 0.70 | Fields marked as uncertain; claim may need human review |
| `resubmission_detected` | CLM frequency code 7 or 8 in EDI; resubmission_of populated | WS1 duplicate check should treat as correction, not duplicate |

---

## §5. Validation Rules (Intake Agent enforces before emitting)

These are applied by the Intake Agent before writing the NormalizedClaimInput. A claim that fails a HARD rule is routed to PARSE_FAILED state. A claim that fails a SOFT rule gets a warning appended and a default applied.

**HARD rules (PARSE_FAILED if violated):**
- `claim_id` is non-null and non-empty after whitespace strip
- `len(diagnosis_codes) >= 1`
- `len(procedure_codes) >= 1`
- `len(procedure_codes) == len(procedure_quantities)` after default-fill

**SOFT rules (warning + default if violated):**
- `member_id` non-null and non-empty → default "UNKNOWN_MEMBER" + warning `member_id_missing`
- `provider_npi` non-null and non-empty → default "UNKNOWN_NPI" + warning `provider_npi_missing`
- `date_of_service` is a valid YYYY-MM-DD → default "unknown" + warning `date_of_service_missing`
- `billed_amount >= 0.0` → default 0.0 + warning `billed_amount_zero`
- `procedure_quantities[i] >= 1` for all i → reset element to 1

**Format rules (applied to code values):**
- All `diagnosis_codes` values upper-cased
- All `procedure_codes` values stripped of leading service type qualifiers (e.g. "HC:" prefix from EDI SV1)
- `provider_npi` stripped of non-numeric characters before storing (OCR noise)
- `date_of_service` converted from YYYYMMDD (EDI) or MMDDYYYY (OCR field 24A) to YYYY-MM-DD

---

## §6. Mapping to ClaimRecord (D4_preamble_capability_spec.md §2)

On intake, the Intake Agent creates a `ClaimRecord` database row. The canonical fields map as follows:

| NormalizedClaimInput field | ClaimRecord field | Notes |
|---------------------------|-------------------|-------|
| `claim_id` | `external_claim_id` | ClaimRecord generates its own `id` (UUID) as PK |
| `member_id` | `member_id` | Direct map |
| `provider_npi` | `provider_npi` | Direct map |
| `provider_specialty` | `provider_specialty` | Direct map |
| `date_of_service` | `date_of_service` | Direct map |
| `diagnosis_codes` | `diagnosis_codes` | Direct map |
| `procedure_codes` | `procedure_codes` | Direct map |
| `procedure_quantities` | `procedure_quantities` | Direct map |
| `modifier_codes` | `modifier_codes` | Direct map |
| `billed_amount` | `billed_amount` | Direct map |
| `payer_id` | — | Not persisted in ClaimRecord; used only by WS1 eligibility and audit |
| `group_id` | — | Not persisted in ClaimRecord; used only for eligibility lookup |
| `place_of_service` | — | Not in current ClaimRecord; add if prior auth lookup requires it |
| `source_format` | `submission_format` | ClaimRecord stores as `submission_format`; 8-value enum applied — see §7 |
| `source_file`, `intake_warnings` | — | Not persisted in ClaimRecord; Intake Agent logs these to AuditLogEntry |

---

## §7. ClaimRecord Updates Applied (D4_preamble_capability_spec.md §2)

The `submission_format` enum in `ClaimRecord` was updated from the original 3-value coarse enum (`[EDI_837, PDF, PORTAL]`) to the full 8-value enum aligned with `NormalizedClaimInput.source_format`. The applied values (per `D4_preamble_capability_spec.md §2`) are:
```
[EDI_837P, EDI_837I, PORTAL_FORM, FHIR_R4, CMS1500_PDF, EMAIL_EML, FAX_PDF, EXCEPTION_NOTES_PDF]
```
This change is backward-compatible for WS1 (WS1 does not branch on `submission_format` — it uses the already-normalized fields). WS2 and the Queue & SLA Management Agent are also unaffected. The Queue agent does not route by format; SLA deadlines are format-agnostic.

`ClaimRecord.provider_id` was also renamed to `provider_npi` in the preamble, aligning with the `NormalizedClaimInput` canonical field name.

---

## §8. WS1 Process_Claim() Input Contract

When WS1's `process_claim(claim: dict)` is called, the dict it receives is the `NormalizedClaimInput` payload (passed through directly from the Intake Agent output, no transformation). WS1 accesses the following fields:

| WS1 access pattern | Field | Required by WS1 |
|-------------------|-------|-----------------|
| `claim["claim_id"]` | `claim_id` | Hard required |
| `claim["member_id"]` | `member_id` | Hard required (eligibility lookup) |
| `claim["payer_id"]` | `payer_id` | Used in audit entries and eligibility trigger; null-safe |
| `claim["procedure_codes"]` | `procedure_codes` | Hard required (code validity, classifier) |
| `claim["diagnosis_codes"]` | `diagnosis_codes` | Hard required (code validity, classifier) |
| `claim["provider_specialty"]` | `provider_specialty` | Used by classifier as signal; null-safe |
| `claim["procedure_quantities"]` | `procedure_quantities` | Used by prior-auth tolerance check (T-07) |
| `claim["billed_amount"]` | `billed_amount` | Used by payment calculation (T-09) |

WS1 does **not** access: `provider_npi`, `group_id`, `place_of_service`, `modifier_codes`, `prior_auth_number`, `source_format`, `source_file`, `intake_warnings`. These are available for future tool calls but are not part of the current WS1 pipeline.

---

## §9. Known Data Quality Patterns (from Claims Pack population run)

This section records what the **parser** produces — parse success vs. PARSE_FAILED — for each format. WS1 routing outcomes (approved/escalated) are downstream of the parser and belong in WS1 test reports, not here.

**Tier 1 full-population parse results** (empirical — 2026-05-26):

| Format | n | Parse success | PARSE_FAILED |
|--------|--:|--------------|--------------|
| EDI 837P | 1,000 | **936 (93.6%)** | **64 (6.4%)** |
| EDI 837I | 200 | **183 (91.5%)** | **17 (8.5%)** |
| Portal JSON | 400 | **374 (93.5%)** | **26 (6.5%)** |
| **Total Tier 1** | **1,600** | **1,493 (93.3%)** | **107 (6.7%)** |

All 107 PARSE_FAILED events share one root cause: missing `diagnosis_codes`. No `claim_id` or `procedure_codes` failures were observed in Tier 1.

**Canonical cache — no need to re-run the parser for WS1 testing:**

The 1,493 successfully parsed claims are saved as NormalizedClaimInput JSON in `prototype/normalized-tier1/`. These files are the direct output of the intake parsers and can be fed straight into WS1 without re-parsing the raw EDI/JSON source files.

```
# Run a single cached claim through WS1:
python run_claim.py --file normalized-tier1/CLM-2026-1000001.json

# Run all 1,493 cached claims through WS1 (heuristic classifier):
python run_batch.py --dir normalized-tier1 --limit 0

# Run a live-classifier sample against the cache (costs ~$0.004/claim):
python run_batch.py --dir normalized-tier1 --limit 50 --live
```

The batch runner detects the `normalized` format from the directory name and skips the parse step entirely — `process_claim()` receives the cached dict directly.

**Per-format data quality patterns:**

| Format | Pattern | Empirical frequency | Handling |
|--------|---------|---------------------|---------|
| EDI 837I | `NM1*85` segment has empty NPI element (`NM1*85*2*...*****XX*~`) | Multiple files (sample only) | `provider_npi_empty_segment` warning; default "UNKNOWN_NPI" |
| EDI 837P | No HI segment with AB-prefix qualifiers (diagnosis codes missing) | **6.4%** (64/1,000 — full population) | PARSE_FAILED |
| EDI 837I | No HI segment with AB-prefix qualifiers (diagnosis codes missing) | **8.5%** (17/200 — full population) | PARSE_FAILED |
| Portal JSON | `diagnoses` array is empty | **6.5%** (26/400 — full population) | PARSE_FAILED |
| FHIR R4 | `billablePeriod.start > billablePeriod.end` | Observed in CLM-2026-1001805 (sample only) | `fhir_billable_period_reversed` warning; use item-level dates |
| CMS-1500 OCR | Claim ID garbled (e.g. "CLM" → "CL -" OCR error) | Observed in CLM-2026-1001601 (sample only) | `ocr_field_unparseable` warning; attempt cleanup |
| CMS-1500 OCR | Procedure code garbled (e.g. "97110" → "9 110") | Observed (sample only) | `ocr_field_unparseable` warning; flag for human review |
| Email .eml | `X-Submitter-TaxID` header empty with call-to-action text | Observed in CLM-2026-1001903 (sample only) | Warning in `intake_warnings`; TaxID not part of NormalizedClaimInput |
| Email .eml | Payer field is plan name, not ID | All email samples | `payer_id_is_name` warning; stored as string |

---

### CMS-1500 OCR — Batch Findings and Deferral Decision

A deterministic regex parser (`tools/intake/cms1500_ocr_parser.py`) was built and run against all 200 pre-extracted CMS-1500 OCR text files in the Claims Pack. After two rounds of fixes addressing the most common failure patterns, the PARSE_FAILED rate remained at **41% (82/200)**.

**OCR noise patterns observed (beyond the 3-file sample):**

| Pattern | Example | Effect |
|---------|---------|--------|
| Field label digit dropped | `"24."` → `" 2. SERVICE LINE"` | Service section anchor fails — no procedure codes extracted |
| Letter/digit substitution in keywords | `"SERVICE"` → `"5ERVICE"` | Anchor regex misses the section |
| Dropped character in field keyword | `"ACCOUNT"` → `"ACCONT"` | Claim ID regex fails; fallback uses filename |
| Truncated date (1-digit day) | `"2026-04-0"` | Date normalisation returns None; `date_of_service_missing` warning |
| Missing second hyphen in date | `"2026-0412"` | Requires explicit 4-digit-without-separator branch |
| Service lines merged with header | Column header and first data row on same line | Row regex skips the line entirely |
| Diagnosis section anchor missing | Field 21 label absent or unrecognisable | `diagnosis_codes` empty → PARSE_FAILED |

**Root cause of 82 PARSE_FAILED events:** All are missing `diagnosis_codes` (Field 21 section unrecognisable) or `procedure_codes` (Field 24 section unrecognisable) — the two hard-required fields. The extreme label noise means the regex anchors that reliably anchor against EDI and portal-JSON cannot anchor reliably against CMS-1500 OCR text.

**Decision: CMS-1500 OCR parsing is deferred from prototype scope.**

The parser file exists (`tools/intake/cms1500_ocr_parser.py`) and handles ~59% of files correctly. It is not production-ready. Bringing it to acceptable quality (target: <10% PARSE_FAILED) would require one of:

- A significantly more fault-tolerant layout-aware parser (positional matching instead of label anchoring)
- Tier 3 LLM extraction (Haiku or Sonnet) as a fallback for files where the regex parser fails

Neither is in scope for the Week 5 prototype.

**Impact on coverage:** The prototype empirically covers Tier 1 formats (EDI 837P + EDI 837I + Portal JSON = 1,600 files, ~80% of the 2,000-claim pack). CMS-1500 OCR (200 files, ~10%) is deferred. This is consistent with the stated prototype scope in CLAUDE.md and DEMO.md — scope discipline requires naming this gap explicitly rather than reporting a flattering metric from the 59% that do parse.


---

# D4c — Capability Specification: Intake & Anomaly Agent
## Greenfield Health Systems: Medical Claims Adjudication Transformation

*Inputs: `D4_canonical_claim_record.md` (output contract), `D4_preamble_capability_spec.md` (shared entities), `Capstone-A-Claims-Pack/README.md` (format inventory), direct Claims Pack sampling (all 8 format families).*

*Relationship to Gate5a deliverables: This spec is Wave 1 prerequisite infrastructure. It is deferred as a primary Gate5a capability spec target (see `D4_preamble_capability_spec.md §1` deferral rationale). It is produced here because the canonical normalized claim record (D4_canonical_claim_record.md) requires an explicit producing agent, and because the adapters in `prototype/tools/intake/` implement a subset of this spec.*

---

## §0. Agent Purpose

**Agent name:** Intake & Anomaly Agent (INTAKE)

**One-sentence purpose:** Accept claims arriving in any of the 8 intake formats, extract required fields, normalize them to the `NormalizedClaimInput` canonical record, and route the result to WS1's adjudication queue — or to `PARSE_FAILED` when extraction cannot recover required fields.

**What this agent does not do:**
- Does not make adjudication decisions (approve, deny, escalate for clinical reasons)
- Does not validate clinical appropriateness of diagnosis or procedure codes
- Does not hold claims for human review beyond what extraction failure requires
- Does not manage SLA timers (Queue & SLA Management Agent scope)

**Wave position:** Wave 1 — prerequisite infrastructure for WS1. WS1 cannot run without a normalized claim record; this agent produces it.

---

## §1. Jobs-to-be-Done

### INT-JtD-1: Format detection and extraction

**Trigger:** A claim file arrives in the intake queue.

**Inputs:** Raw file (EDI text, JSON, PDF text, .eml text)

**Output:** `NormalizedClaimInput` dict (see `D4_canonical_claim_record.md §2`)

**Autonomy:** Fully Agentic — no HITL gate. D2B score 3/7 (high input structure variance, but decision determinism is high once format is identified, no compliance constraint on the extraction decision itself). Parse failures route to PARSE_FAILED queue for human handling without agent review.

**Success criteria:**
- All HARD required fields populated (`claim_id`, `diagnosis_codes`, `procedure_codes`)
- All SOFT required fields populated or defaulted with warning
- `intake_warnings` list accurate and complete
- `source_format` correct

### INT-JtD-2: Anomaly detection and quality flagging

**Trigger:** Extraction complete; record passes HARD validation.

**Inputs:** Extracted `NormalizedClaimInput` dict

**Output:** `intake_warnings` list appended with anomaly flags; no field values changed

**Autonomy:** Fully Agentic — no HITL gate. D2B score 5/7. Pattern matching against known anomaly signatures.

**Anomaly checks (deterministic, no LLM):**
- `duplicate_claim_detected` — ClaimRecord lookup by (member_id, date_of_service, procedure_codes[0]); if a prior ClaimRecord with state ∉ {PARSE_FAILED, REJECTED} exists for the same tuple, append `duplicate_claim_detected` and set `resubmission_of = <prior_claim_id>`; WS1 inspects this flag during T-01 deduplication
- `resubmission_detected` — CLM frequency code 7 or 8 (EDI) or `resubmission_of` field non-null (portal-JSON)
- `billed_amount_zero` — billed_amount = 0.0 after default fill
- `quantities_length_mismatch` — lengths don't match before default fix
- `fhir_billable_period_reversed` — FHIR billablePeriod.start > billablePeriod.end
- `date_of_service_missing` — date_of_service = "unknown" after extraction
- `payer_id_is_name` — payer field is a text name, not a machine-readable ID

---

## §2. Format Detection

Format is determined from the file extension and header content. The agent applies the following rules in order:

| Priority | Rule | Assigned format |
|----------|------|----------------|
| 1 | File extension is `.edi` or `.x12`; content starts with `ISA*` | EDI (type determined from GS[8] transaction set) |
| 2 | EDI content and `GS[8]` contains `005010X222A1` | `EDI_837P` |
| 3 | EDI content and `GS[8]` contains `005010X223A2` | `EDI_837I` |
| 4 | File extension is `.json` and top-level key `resourceType == "Claim"` | `FHIR_R4` |
| 5 | File extension is `.json` and top-level key `submission_id` present | `PORTAL_FORM` |
| 6 | File extension is `.json` and neither of the above | Unknown — PARSE_FAILED |
| 7 | File extension is `.txt`; content contains "HEALTH INSURANCE CLAIM FORM" or "CMS-1500" | `CMS1500_PDF` |
| 8 | File extension is `.eml`; MIME type `message/rfc822` | `EMAIL_EML` |
| 9 | File extension is `.pdf`; content contains fax header patterns | `FAX_PDF` |
| 10 | File extension is `.pdf`; no fax header | `EXCEPTION_NOTES_PDF` |
| 11 | No rule matches | Unknown — PARSE_FAILED with warning `format_unrecognized` |

---

## §3. Extraction Tiers

### Tier 1 — Electronic structured (deterministic parser, no LLM)

**Formats:** EDI 837P, EDI 837I, Portal JSON, FHIR R4
**Volume:** ~85% of claims
**LLM cost:** $0

**EDI X12 extraction:**
- Element separator detected from ISA[3] character position (0-indexed position 3)
- Segment terminator detected from last character of stripped ISA segment
- Segments split on terminator; elements split on element separator
- Component values split on `:` separator
- Parsing rules per segment:
  - `GS`: element[8] → transaction_set (determines 837P vs 837I)
  - `CLM`: element[1] → claim_id; element[2] → billed_amount (float)
  - `NM1*85`: element[9] → provider_npi; element[3] → provider_name (for specialty heuristics)
  - `NM1*IL`: element[9] → member_id
  - `NM1*40`: element[9] → payer_id
  - `HI`: each element, if it contains `:`, split on `:` — if qualifier starts with `AB`, second component is a diagnosis code
  - `SV1`: element[1] split on `:` — second component is procedure code (strip `HC:` prefix); element[4] → unit quantity
  - `DTP*472`: element[3] → date_of_service (convert YYYYMMDD → YYYY-MM-DD)
  - `REF*G1` or `REF*F5`: element[2] → prior_auth_number
  - `CLM` element[4] component[0] → place_of_service

**Portal JSON extraction:** Field mapping per `D4_canonical_claim_record.md §3`.

**FHIR R4 extraction:**
- `id` → claim_id
- `patient.reference` strip "Patient/" prefix → member_id
- `provider.reference` strip "Practitioner/" prefix → provider_npi
- `provider.display` → text parse for specialty heuristics (same `_SPECIALTY_HINTS` table as EDI)
- `insurer.reference` strip "Organization/" prefix → payer_id
- `diagnosis[].diagnosisCodeableConcept.coding[0].code` → diagnosis_codes
- `item[].productOrService.coding[0].code` → procedure_codes
- `item[].quantity.value` → procedure_quantities
- `item[].servicedDate` min → date_of_service
- `total.value` → billed_amount
- `item[].modifier[].coding[0].code` → modifier_codes
- `billablePeriod.start > billablePeriod.end` → append `fhir_billable_period_reversed`

### Tier 2 — OCR text (deterministic parser on pre-OCR'd text, no LLM)

**Formats:** CMS-1500 OCR
**Volume:** ~10% of claims
**LLM cost:** $0 (OCR is pre-done by clearinghouse; only pattern matching required)
**OCR failure rate:** ~5% (assumption A6, low confidence — no measured baseline; see §8)

**CMS-1500 OCR extraction:**
The Claims Pack pre-extracts CMS-1500 forms to plain text in `cms1500-ocr/`. The agent parses this text using field number anchors:

| CMS-1500 field | Content | Extraction pattern |
|----------------|---------|-------------------|
| Field 1a | Member ID | After "1A. INSURED'S I.D. NUMBER" or "INSURED'S ID NUMBER" |
| Field 11 | Group number | After "11. INSURED'S GROUP OR FECA NUMBER" |
| Field 11c | Payer / insurance | After "11C." or "INSURANCE PLAN NAME"; sets `payer_id_is_name` warning |
| Field 21 | Diagnosis codes | ICD regex: `[A-Z][0-9]{2}[\\.][0-9A-Z]{0,4}` across 4 positions |
| Field 23 | Prior auth number | After "23." or "PRIOR AUTHORIZATION NUMBER" |
| Field 24A | Date of service | MMDDYYYY pattern; convert to YYYY-MM-DD |
| Field 24D | CPT codes | 5-digit numeric strings in service line area |
| Field 24G | Units | Numeric value after CPT code on same line |
| Field 26 | Claim ID | After "26." or "PATIENT'S ACCOUNT NO"; cleanup OCR artifacts ("CL -" → "CLM-") |
| Field 28 | Billed amount | Dollar amount after "28." or "TOTAL CHARGE" |
| Field 33 | Provider NPI | 10-digit string in "NPI" box; often empty in OCR |

OCR confidence scoring: if any of field 26, 21, or 24D fail to match expected format, append `ocr_confidence_low`.

### Tier 3 — Unstructured LLM extraction (one Haiku call per document)

**Formats:** Email .eml, Fax PDF, Exception Notes PDF
**Volume:** ~5% of claims (30 email + 30 fax + 40 exception notes = 100 / 2,000)
**LLM cost:** ~$0.0004 / claim (Haiku input ~500 tokens + output ~200 tokens)

**Email (.eml) pre-processing:**
- Parse MIME structure (multipart/alternative or plain text)
- Extract `X-Submitter-NPI` header → provider_npi (structured, no LLM needed)
- Extract `X-Submitter-TaxID` header → internal reference (not in NormalizedClaimInput)
- Extract plain text body (prefer text/plain over text/html)
- Pass body + NPI header to Haiku for field extraction

**Haiku prompt template (Email):**
```
You are extracting structured claim data from an insurance claim email.
Extract these fields from the email body text below.
Return a JSON object with exactly these keys (null if not found):
  claim_id, member_id, payer_id (plan name or ID),
  group_id, provider_specialty, date_of_service (YYYY-MM-DD),
  billed_amount (float), diagnosis_codes (list of ICD-10 strings),
  procedure_codes (list of 5-digit CPT strings), procedure_quantities (list of ints)

Email body:
{body_text}
```

**Haiku prompt template (Fax / Exception Notes):**
Same field set, body replaced with OCR-extracted text from the PDF.

**Post-LLM validation:** Apply same HARD and SOFT rules as Tier 1. If Haiku returns null for `diagnosis_codes` or `procedure_codes`, claim → PARSE_FAILED with `llm_extraction_failed_required_field`.

**LLM confidence guard — SOFT fields:** If the LLM response contains a malformed value for a SOFT field (e.g., negative billed_amount, non-10-digit provider_npi, malformed date_of_service), set the field to its normalization default and append `llm_extraction_low_confidence` to `intake_warnings`. Claim continues to WS1 with warning intact.

**LLM confidence guard — HARD fields:** If the LLM response contains a malformed or null value for a HARD required field (`diagnosis_codes`, `procedure_codes`, `claim_id`), do NOT set to default. Trigger PARSE_FAILED_LLM_REQUIRED_FIELD. The claim does not continue to WS1.

---

## §4. Normalization Rules

Applied after extraction, before validation, regardless of format:

1. All `diagnosis_codes` values → `.upper().strip()`
2. All `procedure_codes` values → strip leading `HC:`, `WK:`, or other X12 service type qualifiers; strip whitespace; result must be 4–5 characters
3. `provider_npi` → strip all non-numeric characters; if result is not 10 digits, set to "UNKNOWN_NPI" + warning `provider_npi_format_invalid`
4. `date_of_service`:
   - If YYYYMMDD (8 digits, EDI) → `YYYY-MM-DD`
   - If MMDDYYYY (CMS-1500) → `YYYY-MM-DD`
   - If already `YYYY-MM-DD` → no change
   - Otherwise → "unknown" + warning `date_of_service_missing`
5. `billed_amount` → cast to float; if cast fails → 0.0 + warning `billed_amount_zero`
6. `procedure_quantities` → ensure same length as `procedure_codes`; fill missing positions with 1; reset any value < 1 to 1
7. `claim_id` → `.strip()`; remove null bytes and control characters

---

## §5. Validation, Escalation Triggers, and Routing

### State transitions

| Transition | Trigger |
|-----------|---------|
| (new) → RECEIVED | File dequeued from intake queue |
| RECEIVED → PARSING | Agent begins format detection |
| PARSING → NORMALISED | All HARD required fields extracted and validated |
| PARSING → PARSE_FAILED | Any hard failure condition below |

Each state transition requires a COMMITTED `AuditLogEntry` with `action = CLAIM_STATE_TRANSITION` before the next processing step proceeds.

### Hard failures → PARSE_FAILED

| Trigger | Condition | ClaimRecord state |
|---------|-----------|-------------------|
| PARSE_FAILED_NO_CLAIM_ID | `claim_id` is null or empty after normalization | PARSE_FAILED |
| PARSE_FAILED_NO_DIAGNOSES | `len(diagnosis_codes) == 0` after extraction | PARSE_FAILED |
| PARSE_FAILED_NO_PROCEDURES | `len(procedure_codes) == 0` after extraction | PARSE_FAILED |
| PARSE_FAILED_FORMAT_UNKNOWN | Format detection found no matching rule | PARSE_FAILED |
| PARSE_FAILED_LLM_REQUIRED_FIELD | Haiku extraction returned null for a HARD required field | PARSE_FAILED |

PARSE_FAILED claims are written to the `parse_failed_queue`. **No EscalationPacket is produced** — the parse_failed_queue uses a separate `ParseFailedQueueMessage` schema:

| Field | Type | Content |
|-------|------|---------|
| `claim_id` | UUID | ClaimRecord.id |
| `source_file` | string | Original filename |
| `source_format` | string | Detected format enum value, or `UNKNOWN` |
| `failure_reason` | string | Trigger ID from table above (e.g., `PARSE_FAILED_NO_DIAGNOSES`) |
| `raw_content` | string | First 4,096 characters of raw file content |
| `extraction_output` | JSON object | Fields successfully extracted before failure (may be empty) |
| `queued_at` | ISO 8601 timestamp, UTC | When the message was enqueued |

On PARSE_FAILED, the Intake Agent:
1. Transitions `ClaimRecord.state`: PARSING → PARSE_FAILED.
2. Writes `AuditLogEntry`:
   - `action = CLAIM_PARSE_FAILED` (see §11)
   - `entity_type = "ClaimRecord"`, `entity_id = ClaimRecord.id`
   - `input_summary = { "source_file": source_file, "failure_reason": failure_reason, "source_format": source_format }`
   - `output_summary = { "previous_state": "PARSING", "new_state": "PARSE_FAILED" }`
   - `delegation_tier = AGENT_ALONE`
   - Transition `AuditLogEntry.state`: PENDING_WRITE → COMMITTED before step 3.
3. Writes `ParseFailedQueueMessage` to `parse_failed_queue`.

**SLA:** No SLA timer applies to `PARSE_FAILED` claims from the Intake Agent's perspective; operator review SLA is set by operations. `PARSE_FAILED` is a terminal ClaimRecord state — no pipeline retry. A human operator reviews parse_failed_queue messages; they are never routed to WS1.

**PARSE_FAILED rate targets:**
- Tier 1 (EDI): < 15% (observed ~9% for 837P, ~8.5% for 837I from Claims Pack sampling — missing diagnosis codes)
- Tier 2 (OCR): < 20% (OCR error compounding; 5% target for field-level failures)
- Tier 3 (LLM): < 5% (Haiku extraction; hard failures only)

### Successful extraction → NORMALISED

On success, the Intake Agent:
1. Creates a `ClaimRecord` row with `state = RECEIVED`; writes a COMMITTED `AuditLogEntry` (`action = CLAIM_STATE_TRANSITION`, `entity_type = "ClaimRecord"`, `entity_id = ClaimRecord.id`, `output_summary = { "previous_state": "RECEIVED", "new_state": "PARSING" }`, `delegation_tier = AGENT_ALONE`); transitions `ClaimRecord.state` to PARSING.
2. Transitions `ClaimRecord.state`: PARSING → NORMALISED.
3. Writes `AuditLogEntry`:
   - `action = CLAIM_NORMALISED` (see §11)
   - `entity_type = "ClaimRecord"`, `entity_id = ClaimRecord.id`
   - `input_summary = { "source_file": source_file, "intake_warnings": intake_warnings, "source_format": source_format }`
   - `output_summary = { "previous_state": "PARSING", "new_state": "NORMALISED" }`
   - `delegation_tier = AGENT_ALONE`
   - Transition `AuditLogEntry.state`: PENDING_WRITE → COMMITTED before step 4.
4. Writes `NormalizedClaimInput` dict to the normalised claim queue.

---

## §6. Output Contract Reference

The canonical output format is fully defined in `D4_canonical_claim_record.md`. This spec does not duplicate that definition; it specifies how to produce it.

Key constraint: the `NormalizedClaimInput` the Intake Agent emits is passed directly to `WS1.process_claim(claim: dict)` without transformation. If the Intake Agent emits a field name that WS1 does not access (e.g. `group_id`), that field is silently ignored by WS1. If WS1 accesses a field that the Intake Agent did not emit (e.g. `payer_id` missing from dict), WS1 must handle `KeyError` gracefully with `.get(field, default)`.

---

## §7. LLM Model Routing and Cost

| Format tier | Model | Tokens/claim | Cost/claim | Monthly cost (100 claims/day) |
|-------------|-------|-------------|-----------|-------------------------------|
| Tier 1 (EDI, Portal JSON, FHIR R4) | None | 0 | $0 | $0 |
| Tier 2 (CMS-1500 OCR) | None | 0 | $0 | $0 |
| Tier 3 (Email, Fax, Exception Notes) | Haiku 4.5 | ~700 in + ~200 out | ~$0.0004 | ~$1.20 |

Tier 3 volume: ~100 files/day × $0.0004 = $0.04/day = ~$14.60/year. Negligible relative to WS1 LLM costs.

Haiku is selected (not Sonnet) because:
- The extraction task is structured field-extraction from text, not clinical judgment
- Haiku has sufficient accuracy for well-structured email and typed notes
- Cost is 10× lower than Sonnet for this high-frequency, low-complexity task
- Sonnet is reserved for WS1 clinical content classification (non-trivial decision)

Exception: if Haiku extraction confidence is flagged as low (`llm_extraction_low_confidence`) for a SOFT field, the claim is still passed to WS1 with the warnings intact. WS1 does not re-invoke a higher-tier model — that is out of scope for the intake contract. The warning is surfaced in the physician review packet if the claim escalates. HARD field failures (null or malformed `diagnosis_codes`, `procedure_codes`, `claim_id`) always route to PARSE_FAILED and are never passed to WS1.

---

## §8. Open Assumptions

| ID | Assumption | Why it matters | Confidence |
|----|-----------|----------------|------------|
| A5 | OCR text in `cms1500-ocr/` was produced by the clearinghouse before reaching the Intake Agent. The agent does not need to run OCR itself. | If wrong: agent must add a PDF→text OCR step (Tesseract or cloud OCR), increasing complexity and Tier 2 failure rate | Medium — Claims Pack README implies pre-extraction, but production path is unconfirmed |
| A6 | OCR failure rate ~5% for CMS-1500 (claim → PARSE_FAILED). | Drives PARSE_FAILED queue staffing estimate. | Low — no measured baseline |
| A7 | Haiku extraction accuracy ≥ 95% for email and fax formats. | If wrong: Tier 3 PARSE_FAILED rate rises. Mitigation path is expanding PARSE_FAILED queue staffing, not adding a Sonnet fallback tier — Sonnet fallback is out of scope for Wave 1. | Low — no measured baseline; needs validation run |
| A8 | The Intake Agent processes claims synchronously — one file at a time in sequence. | If parallelism is required (throughput > 50 claims/min), the agent design needs a queue-worker pattern. 2,000 claims/day ÷ 8 hours = ~4 claims/min — synchronous is adequate. | High |
| A9 | `X-Submitter-NPI` header is present in all email submissions. | If absent: provider_npi defaults to "UNKNOWN_NPI" for all email claims, degrading code validity and billing audit quality. | Medium — observed in Claims Pack samples, but custom headers could be stripped by mail servers |
| A10 | CMS-1500 PARSE_FAILED rate in production will be materially lower than the 41% rate observed in Claims Pack sampling (empirically measured in `D4_canonical_claim_record.md §9`). The Claims Pack rate is driven by OCR quality on the synthetic dataset. | Drives PARSE_FAILED queue staffing for Tier 2 claims. If the production rate exceeds 30%, CMS-1500 should be escalated to a Tier 2b path with clearinghouse OCR pre-validation before intake. | Medium — Claims Pack rate is empirically measured but on synthetic data only |

---

## §9. Integration with WS1

The Intake Agent writes the `NormalizedClaimInput` to a normalised claim queue. WS1 reads from this queue. The interface is:

- **Queue:** normalised_claims_queue (FIFO, persistent)
- **Message schema:** `NormalizedClaimInput` as defined in `D4_canonical_claim_record.md §2`
- **Acknowledgement:** WS1 acknowledges each message after `process_claim()` completes (success or escalation); the Intake Agent does not retry acknowledged messages
- **PARSE_FAILED handling:** Routed to separate `parse_failed_queue`; WS1 never receives these

The Intake Agent does not wait for WS1 to complete processing. It emits the normalized record and moves to the next file.

---

## §11. Audit Log Schema

*Authoritative per-spec audit action enum for the Intake & Anomaly Agent. Referenced by `D4_preamble_capability_spec.md` AuditLogEntry.action field constraint — no action value outside this table is valid for records produced by this agent.*

| Action value | When written | delegation_tier |
|-------------|-------------|----------------|
| `CLAIM_RECEIVED` | ClaimRecord created with `state = RECEIVED` | AGENT_ALONE |
| `CLAIM_STATE_TRANSITION` | Any ClaimRecord.state transition (RECEIVED → PARSING; PARSING → NORMALISED; PARSING → PARSE_FAILED) | AGENT_ALONE |
| `CLAIM_NORMALISED` | PARSING → NORMALISED completed; NormalizedClaimInput written to normalised claim queue | AGENT_ALONE |
| `CLAIM_PARSE_FAILED` | PARSING → PARSE_FAILED completed; ParseFailedQueueMessage written to parse_failed_queue | AGENT_ALONE |
| `ANOMALY_FLAGS_APPENDED` | INT-JtD-2 completes with one or more flags appended to `intake_warnings` | AGENT_ALONE |

All Intake Agent audit records must use `agent_id` in format `INTAKE_AGENT:{version}:{instance_id}`.

---

## §10. Prototype Scope Note

The `prototype/tools/intake/` directory implements a subset of this spec:
- `edi_parser.py` implements Tier 1 EDI extraction for 837P and 837I
- `portal_json_adapter.py` implements Tier 1 portal-JSON extraction
- FHIR R4, CMS-1500 OCR, and Tier 3 LLM extraction are not implemented in the prototype

This is consistent with the prototype scope declaration: the prototype covers the portal-JSON path (20% of volume) plus the EDI path (60%) via the batch runner. The missing formats (FHIR R4, OCR, unstructured) are Intake Agent production build items. Their omission is explicitly disclosed in `prototype/DEMO.md §Format coverage`.
