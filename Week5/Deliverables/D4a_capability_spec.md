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
