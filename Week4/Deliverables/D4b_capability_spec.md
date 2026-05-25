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
| Additional information request draft | S-08 (delivered to physician for approval) then forwarded to provider portal S-12 | Structured draft with: `claim_id`, `missing_documentation_items` (array, from `completeness_flags`), `provider_id`, `provider_contact_details` (from S-07), draft request text (structured, not free-form) | T-B-09 executes on physician-triggered `PENDING_ADDITIONAL_INFO` transition; physician approves before dispatch to provider |
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

Relationships:
- claim_id: UUID, foreign key to ClaimRecord, required, 1:1 (one packet per claim per assembly),
  on delete: restrict — packet cannot be deleted while ClaimRecord exists in non-CLOSED state
- ws1_classification_result_id: UUID, foreign key to ClinicalClassificationResult,
  required, 1:1, on delete: restrict
- ws2_verification_result_id: UUID, foreign key to ClinicalClassificationResult,
  required once set, 1:1, on delete: restrict
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
| T-B-05 | Clinical notes retrieval (Wave 2) | Retrieval | Agent-led + HITL on condition | member_id, provider_id, date_of_service, episode diagnosis range | Clinical notes source system API (S-13) [SCOPE-OUT — Wave 2 only] | **High** |
| T-B-06 | Medical necessity criteria retrieval | Retrieval | Fully agentic | procedure_codes[0] (procedure_code_range mapping), icd_chapter(diagnosis_codes[0]), minimum cosine similarity 0.75 | Medical necessity criteria vector store RAG (S-15) [SCOPE-OUT] | Medium |
| T-B-07 | Packet completeness assessment and flagging | Decision | Fully agentic | Results of T-B-03 through T-B-06; list of expected context elements per claim type; SCOPE-OUT status of S-13 and S-15 | Internal completeness rule set; SCOPE-OUT status flags | Low |
| T-B-08 | Pre-filled review packet assembly and delivery | Generation + Action | Agent-led + HITL on condition | All T-B-01 through T-B-07 outputs; PhysicianReviewPacket schema; ClaimRecord.sla_deadline | S-08 physician review queue interface (write); S-07 (state write) | **High** |
| T-B-09 | Additional information request drafting | Generation | Agent-led + HITL on condition | completeness_flags array; provider_id (from ClaimRecord); provider contact details (from S-07); ClaimRecord.diagnosis_codes and procedure_codes | Haiku 4.5 (draft generation); S-08 (physician approval delivery); S-12 (provider portal dispatch after physician approval) | Medium |
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
  - ClaimRecord: provider_id (string), ClaimRecord.id
  - Provider contact details: from S-07 provider record
  - Current timestamp; ClaimRecord.sla_deadline

Logic:
  IF physician action = ADDITIONAL_INFO_REQUIRED:
    call Haiku 4.5 to draft additional information request:
      inputs: {completeness_flags, claim_id, provider_id, diagnosis_codes,
        procedure_codes, date_of_service, missing_item_descriptions
        (derived from completeness_flags mapping)}
      output: structured draft with: {missing_documentation_items (array),
        provider_id, draft_request_text — factual and non-leading only,
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
| ET-B-04 | Physician has not responded to an assembled PhysicianReviewPacket (no action token received from S-08) within the HITL review SLA, OR physician has not approved/rejected the additional information request draft within 2 hours | No physician action token received from S-08 within 4 hours of packet delivery_at (matching CP-B-1 SLA below); OR no draft approval/rejection within 2 hours of T-B-09 delivery | EscalationPacket assembled with trigger_type = HITL_SLA_BREACH, trigger_signal_values = {claim_id, packet_id, delivered_at, elapsed_hours, sla_hours}; delivered to S-09; SLA_BREACHED flag set on PhysicianReviewPacket; escalation re-delivered to S-08 with URGENT flag | Physician HITL queue re-notified with URGENT flag; senior physician reviewer notified; VP Operations and CMO notified within 15 minutes of breach | 4 hours from PhysicianReviewPacket.delivered_at (primary SLA); 2 hours from draft delivery for additional info requests | Same as CP-B-1 breach action; daily SLA breach summary to VP Operations |
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
      provider_id, draft_approved_by: physician_id}
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
