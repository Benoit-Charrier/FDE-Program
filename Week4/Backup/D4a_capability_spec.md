# D4a — Capability Specification: WS1 Administrative Adjudication Agent
**Engagement:** Greenfield Health Systems — Medical Claims Adjudication Transformation
**Deliverable:** D4 Pass 2 — Spec A, §0–§8 + §10–§11 + §14
**Output file:** `Deliverables/D4a_capability_spec.md`
**Preamble reference:** `Deliverables/D4_preamble_capability_spec.md` — shared entities (§2) and data requirements (§3) are defined there; this spec references them by name and does not redefine them.
**Integration contracts:** Produced separately in `Deliverables/D4a_integration_specs.md`

---

## §0. Agent Identity

**Agent name:** WS1 Administrative Adjudication Agent *(from D3 §2 Agent 2 — name unchanged)*

**Job to be Done:** Process every normalised inbound claim through the full administrative adjudication pipeline — eligibility verification, coding validation, prior auth check, clinical content routing, and payment determination — producing a defensible AUTO_APPROVED, AUTO_REJECTED, or CLINICAL_REVIEW_QUEUE disposition for each claim, so that administrative claims are cleared without physician involvement and clinical claims reach the physician queue correctly routed.

**D3 reference:** D3 §2 Agent 2; D3 Autonomy Matrix §3 rows: member eligibility lookup, eligibility discrepancy resolution, code validity check, coding plausibility assessment, prior auth lookup, prior auth partial match tolerance resolution, clinical content routing (both confidence tiers), fee schedule calculation, contract exception handling, payment approval — standard administrative claim.

**Delegation archetype:** Agent-led + Human Oversight — consistent with D3 Autonomy Matrix and D2B §3 for WS1-JtD-1, WS1-JtD-2, and WS1-JtD-3. Standard processing paths are fully agentic; exceptions at defined breakpoints escalate to HITL. Clinical content routing below the confidence threshold hands full control to a human reviewer.

**KPIs:**

| KPI | Baseline | Target | How measured | Review cadence |
|-----|----------|--------|--------------|----------------|
| Auto-adjudication rate | 22% (scenario.md) | ≥80% | % of claims reaching AUTO_APPROVED state without a HITLEscalation record | Weekly |
| Cycle time — administrative path | 8–9 days (Exchange 3, VP Operations) | ≤5 days | Median days from ClaimRecord.submitted_at to AdjudicationDecision.decided_at for AUTO_APPROVED claims | Weekly |
| Clinical classifier recall | No baseline (classifier does not exist) | ≥99.5% | % of clinical claims correctly classified on CMO-labelled holdout set (≥500 claims, labelled by Dr. Webb's team); measured against labelled ground truth, NOT model self-reported confidence | Pre-deployment mandatory gate; monthly 5% audit post-deployment |
| HITL rate | Unknown (not measured in current process) | ≤25% | % of claims with at least one HITLEscalation during WS1 processing, measured per rolling 7-day window | Weekly |
| Auto-adjudication error rate | 1.2% overall (scenario_enriched.md) | ≤0.3% | % of AUTO_APPROVED decisions subsequently overturned at appeal review | Monthly |

**Confidence threshold validation — mandatory pre-deployment protocol:**
CLINICAL_CONTENT_CONFIDENCE_THRESHOLD must be calibrated as follows before WS1 goes live:
1. CMO clinical team labels ≥500 claims as CLINICAL or ADMINISTRATIVE (ground truth holdout set)
2. Classifier is run against the holdout set at candidate threshold values
3. Threshold is set at the lowest value that achieves ≥99.5% recall (≤0.5% false negative rate) on the holdout set
4. The threshold value and holdout set recall result are recorded in a signed configuration artefact co-signed by Dr. Marcus Webb
5. The signed artefact is a hard go-live gate — no production routing may begin without it

**Post-deployment recalibration path:**
Monthly: audit a 5% random sample of AUTO_APPROVED claims for clinical content. If ≥2% of audited claims are reclassified as clinical by the audit reviewer, trigger recalibration: hold all new routing decisions at CLINICAL_CONTENT_CONFIDENCE_THRESHOLD + 0.05 (more conservative) while CMO team reviews. Recalibrate threshold and re-certify before releasing the hold.

**Governance hard stop:** No claim for which the clinical content classifier returns CLINICAL, or for which ClinicalClassificationResult.confidence_score is less than CLINICAL_CONTENT_CONFIDENCE_THRESHOLD, may receive a payment approval (AUTO_APPROVED) without a HITLEscalation record showing a human reviewer confirmed the administrative routing. This constraint is enforced by the ClaimRecord state machine guard condition on the IN_ADMINISTRATIVE_VALIDATION → AUTO_APPROVED transition: the transition is blocked unless ClinicalClassificationResult.classification = ADMINISTRATIVE AND ClinicalClassificationResult.confidence_score ≥ CLINICAL_CONTENT_CONFIDENCE_THRESHOLD. This is a URAC/NCQA accreditation requirement (Dr. Marcus Webb, Exchange 2).

---

## §1. Purpose and Scope

**Purpose statement:** The WS1 Administrative Adjudication Agent processes normalised medical claim records through the complete administrative adjudication pipeline, replacing the current 20-person manual review process for the administrative claim path. It verifies member eligibility, validates diagnosis and procedure codes against formal pairing rules and clinical plausibility patterns, confirms prior authorisation is present and matching, classifies each claim's clinical content using a shared confidence-scored classifier, calculates the applicable payment amount, and produces a final disposition. The agent does not make medical necessity determinations and does not produce any output that constitutes a clinical judgment — those functions belong exclusively to licensed physicians in WS2.

**In scope:**
- Receiving ClaimRecord from the normalised intake queue (NORMALISED state) and initiating WS1 processing
- Member eligibility lookup: binary check on enrollment status and plan type on the date of service
- Eligibility discrepancy assessment: classifying ambiguous eligibility results (termination date near service date, dependent eligibility uncertainty) and escalating to HITL when the binary result is not available
- ICD-10-CM and CPT/HCPCS code validity check: confirming all submitted codes are valid and that diagnosis-procedure pairings are within formal crosswalk rules
- Clinical coding plausibility assessment: detecting diagnosis-procedure-provider specialty combinations that pass formal pairing rules but are clinically implausible (multi-factor pattern recognition against historical plausibility data)
- Prior authorisation requirement check: determining whether the procedure requires prior auth and whether a valid auth is on file
- Prior auth partial match resolution: applying PRIOR_AUTH_UNIT_TOLERANCE_PERCENT to unit variances; escalating date and code variant mismatches to HITL
- Prior auth absent handling: transitioning the claim to PENDING_PROVIDER_RESPONSE and dispatching a prior auth request to the provider
- Clinical content routing classification: calling the shared clinical content classifier (ADR-2); routing to CLINICAL_REVIEW_QUEUE when classification = CLINICAL and confidence ≥ threshold; routing to administrative payment path when classification = ADMINISTRATIVE and confidence ≥ threshold; escalating to HITL when confidence < threshold
- Fee schedule rate lookup: retrieving the applicable rate for this procedure-provider-plan combination
- Member cost-sharing calculation: applying deductible, co-pay, and out-of-pocket amounts per the member's plan
- Duplicate submission detection: confirming no identical or near-identical claim has already been adjudicated for this member-date-procedure combination
- Contract exception flag and HITL routing: detecting when the standard fee schedule has no applicable rate and the exception path is required
- Payment approval record creation: writing an AdjudicationDecision(AUTO_APPROVED) with the calculated payment amount and the complete audit record
- Rejection record creation: writing an AdjudicationDecision(AUTO_REJECTED) with specific rejection codes
- Audit log entry creation for every action taken on every claim

**Out of scope:**
- Claim intake normalisation and format parsing — handled by the Intake & Anomaly Agent (D3 §2 Agent 1); WS1 only processes claims in NORMALISED state
- Medical necessity determination — Human Only per D2B §3, WS2-JtD-3; URAC/NCQA hard stop; no agent action at this step regardless of classifier confidence
- Clinical context assembly (pre-filled physician review packet) — handled by the Clinical Review Support Agent (Spec B); WS1 only routes the claim to the clinical queue
- Queue prioritisation and SLA monitoring — handled by the Queue & SLA Management Agent (D3 §2 Agent 4); WS1 creates ClaimRecord state transitions but does not manage the queue
- Denial appeal determination — Wave 3, deferred per D3 §2; WS1 AUTO_REJECTED decisions may generate appeals but WS1 does not process them
- Contract exception rules encoding — a data engineering prerequisite; WS1 detects exception cases and escalates; it does not encode new exception rules
- Fee schedule management (adding or updating rates) — out of MVP scope; WS1 reads the fee schedule system; it does not write to it

---

## §2. Inputs and Outputs

**Inputs:**

| Input | Source system | Format | Required / Optional | Validation rule |
|-------|--------------|--------|---------------------|-----------------|
| ClaimRecord in NORMALISED state | Intake & Anomaly Agent output queue | Structured JSON (ClaimRecord schema — see preamble §2) | Required | current_state = NORMALISED; all required ClaimRecord fields non-null; sla_deadline in future |
| Member eligibility status | Member eligibility system [UNKNOWN — see §14 item A-A-4] | Structured API response (enrollment status, plan type, effective/termination dates) | Required | Response includes service_date coverage decision; enrollment effective_date ≤ service_date required for ELIGIBLE result |
| ICD-10-CM / CPT-HCPCS code reference | Code validation service or reference tables [UNKNOWN — see §14 item A-A-5] | Structured lookup (code → valid/invalid + pairing rules) | Required | Reference must reflect current-year codes; stale reference tables are a pre-deployment checklist item |
| Prior authorisation record | Prior auth system [UNKNOWN — see §14 item A-A-6] | Structured API response (PriorAuthRecord schema — see preamble §2) | Required for procedures flagged as auth-required | auth_status must be one of the defined enum values; LOOKUP_FAILED treated as an exception requiring HITL |
| Clinical content classifier result | Shared clinical content classifier service (ADR-2) | Structured API response: {classification: enum, confidence_score: float} | Required for every claim | confidence_score in [0.0, 1.0]; classification must be ADMINISTRATIVE, CLINICAL, or UNCERTAIN |
| Fee schedule rates | Fee schedule system [UNKNOWN — see §14 item A-A-7] | Structured API response (rate for procedure_code × provider_id × plan_type) | Required | Rate returned as integer cents; zero-rate response treated as CONTRACT_EXCEPTION flag, not as free service |
| Contract exception rules | Contract exception rules store [UNKNOWN — see §14 item A-A-3] | Structured lookup (provider_id + procedure_code + payer_id → exception rate) | Required when fee schedule returns no standard rate | If store returns NO_EXCEPTION_FOUND for a non-standard-rate claim, raise HITLEscalation(CONTRACT_EXCEPTION) |
| Submission history | Claims management system [UNKNOWN — see §14 item A-A-8] | Structured query result (prior claims for this member_id + service_date + procedure_codes within 90-day window) | Required for duplicate check | Empty result = no duplicate; non-empty result triggers duplicate assessment logic |
| CLINICAL_CONTENT_CONFIDENCE_THRESHOLD | Agent configuration (procedural memory) | Float 0.0–1.0 in signed configuration artefact | Required | Must be set from CMO-certified holdout calibration; not hardcoded in agent code |
| PRIOR_AUTH_UNIT_TOLERANCE_PERCENT | Agent configuration (procedural memory) | Integer 0–100 | Required | Set by VP Operations; not hardcoded; value 0 = no tolerance (exact match required) |

**Outputs:**

| Output | Target system / recipient | Format | Trigger condition |
|--------|--------------------------|--------|-------------------|
| AdjudicationDecision(AUTO_APPROVED) | Claims management / adjudication system | AdjudicationDecision record (preamble §2 schema) + ClaimRecord state transition to AUTO_APPROVED | All administrative checks pass AND classification = ADMINISTRATIVE AND confidence ≥ threshold |
| AdjudicationDecision(AUTO_REJECTED) | Claims management / adjudication system | AdjudicationDecision record with rejection_codes array + ClaimRecord state transition to AUTO_REJECTED | Eligibility INELIGIBLE confirmed; or irresolvable invalid code; or duplicate confirmed |
| ClaimRecord state transition to CLINICAL_REVIEW_QUEUE | Claims management system; WS2 clinical intake queue notification | ClaimRecord.current_state update + routing_decision = CLINICAL | classification = CLINICAL AND confidence ≥ threshold |
| HITLEscalation record | HITL exception queue / workflow system | HITLEscalation record (preamble §2 schema) + ClaimRecord state transition to HITL_EXCEPTION_QUEUE | Any of: eligibility discrepancy; coding plausibility flag; prior auth partial match outside tolerance; confidence < threshold; contract exception; duplicate suspected |
| Prior auth request to provider | Provider communication system | Structured request message (member_id, claim_id, procedure requiring auth, required documentation list) | auth_status = ABSENT; ClaimRecord transitions to PENDING_PROVIDER_RESPONSE |
| Audit log entry | Append-only audit log | AuditLogEntry (see §13 schema) | Every agent action on every claim |

---

## §3. Entity Definitions

*Shared entities used by this agent: ClaimRecord, ClinicalClassificationResult, HITLEscalation, PriorAuthRecord, AdjudicationDecision. See preamble §2 for full definitions. This section defines WS1-specific entities only.*

---

### Agent-specific Entity: EligibilityCheckResult

Immutable snapshot of the eligibility lookup result for this claim. Created by T-02; referenced by T-03 for discrepancy assessment and by the audit log.

```
Entity: EligibilityCheckResult

Attributes:
- id: UUID, primary key, immutable, generated on creation
- claim_id: UUID, foreign key to ClaimRecord, required, immutable
- member_id: UUID, required, immutable; must match ClaimRecord.member_id
- service_date: ISO 8601 date, required, immutable; must match ClaimRecord.service_date
- eligibility_status: enum [ELIGIBLE, INELIGIBLE, DISCREPANCY_DETECTED, LOOKUP_FAILED],
  required
- plan_type: string, max 50 characters; required if eligibility_status = ELIGIBLE; null otherwise
- discrepancy_type: enum [TERMINATION_DATE_AMBIGUOUS, DEPENDENT_ELIGIBILITY_UNCERTAIN,
  ENROLLMENT_LAG_SUSPECTED]; null if eligibility_status ≠ DISCREPANCY_DETECTED;
  required if eligibility_status = DISCREPANCY_DETECTED
- discrepancy_detail: string, max 500 characters; required if eligibility_status =
  DISCREPANCY_DETECTED; null otherwise
- lookup_error_code: string, max 100 characters; required if eligibility_status = LOOKUP_FAILED;
  null otherwise; records the API error code or timeout classification
- retrieved_at: ISO 8601 timestamp, UTC, required, immutable
- created_at: ISO 8601 timestamp, UTC, set on creation, immutable

Relationships:
- claim_id: UUID, foreign key to ClaimRecord, cardinality one-to-one per lookup attempt;
  multiple records permitted if re-check is needed after discrepancy resolution,
  on delete: RESTRICT

State machine:
- Initial state: SNAPSHOT_CREATED
- Terminal state: SNAPSHOT_CREATED (immutable snapshot — no state transitions)

Invalid transitions:
- SNAPSHOT_CREATED → any state: FORBIDDEN — immutable after creation
- Any field update after created_at is set: FORBIDDEN

Validation rules:
- If eligibility_status = DISCREPANCY_DETECTED: discrepancy_type must be non-null
- If eligibility_status in [ELIGIBLE, INELIGIBLE, LOOKUP_FAILED]: discrepancy_type and
  discrepancy_detail must be null
- If eligibility_status = ELIGIBLE: plan_type must be non-null
- If eligibility_status = LOOKUP_FAILED: lookup_error_code must be non-null

Naming conventions:
- Table: eligibility_check_results
- Enum values: SCREAMING_SNAKE_CASE
```

---

### Agent-specific Entity: CodeValidationResult

Result of the code validity check (T-04) and clinical plausibility assessment (T-05) for this claim. Immutable after creation.

```
Entity: CodeValidationResult

Attributes:
- id: UUID, primary key, immutable, generated on creation
- claim_id: UUID, foreign key to ClaimRecord, required, immutable
- diagnosis_codes_checked: array of objects, required, min length 1; each object:
  {code: string (ICD-10-CM format), status: enum [VALID, INVALID, UNKNOWN]}
- procedure_codes_checked: array of objects, required, min length 1; each object:
  {code: string (CPT/HCPCS format), status: enum [VALID, INVALID, UNKNOWN]}
- all_codes_valid: boolean, required; true if and only if all entries in
  diagnosis_codes_checked and procedure_codes_checked have status = VALID
- pairing_valid: boolean, required; true if all diagnosis-procedure pairings pass formal
  crosswalk rules; false if any pairing is on the invalid pairing list
- plausibility_flag: boolean, required; true if agent raises a clinical plausibility concern
  on this combination; can be true even when pairing_valid = true
- plausibility_detail: string, max 500 characters; required if plausibility_flag = true;
  null otherwise; describes the specific plausibility concern (e.g., "Cardiologist billing
  for gynecological procedure under cardiac diagnosis code — combination is clinically
  implausible per historical pattern data")
- invalid_code_list: array of strings; codes that failed validity check; empty array if
  all_codes_valid = true
- validated_at: ISO 8601 timestamp, UTC, required, immutable
- created_at: ISO 8601 timestamp, UTC, set on creation, immutable

Relationships:
- claim_id: UUID, foreign key to ClaimRecord, cardinality one-to-one per validation run;
  a re-check after HITL resolution creates a new record, on delete: RESTRICT

State machine:
- Initial state: SNAPSHOT_CREATED
- Terminal state: SNAPSHOT_CREATED (immutable)

Invalid transitions:
- SNAPSHOT_CREATED → any state: FORBIDDEN — immutable after creation

Validation rules:
- all_codes_valid must equal true if and only if every entry in diagnosis_codes_checked
  and procedure_codes_checked has status = VALID
- invalid_code_list must be empty if all_codes_valid = true; non-empty if all_codes_valid = false
- If plausibility_flag = true: plausibility_detail must be non-null and length > 0
- If plausibility_flag = false: plausibility_detail must be null
- pairing_valid and plausibility_flag are independent — a claim can have pairing_valid = true
  and plausibility_flag = true simultaneously

Naming conventions:
- Table: code_validation_results
- Enum values: SCREAMING_SNAKE_CASE
```

---

## §4. Activity Catalog

| Task ID | Task name | Task type | Delegation level | Data required | Tool required | Risk level |
|---------|-----------|-----------|-----------------|---------------|---------------|------------|
| T-01 | Receive normalised claim from queue | Retrieval | Fully agentic | ClaimRecord (NORMALISED state) | Claims queue API | Low |
| T-02 | Member eligibility lookup | Retrieval | Fully agentic | ClaimRecord.member_id, ClaimRecord.service_date | Member eligibility API | Medium |
| T-03 | Eligibility discrepancy assessment | Reasoning | Agent-led + HITL on condition | EligibilityCheckResult, member enrollment history | Member eligibility API (secondary context query) | High |
| T-04 | ICD-10/CPT code validity and pairing check | Decision | Fully agentic | ClaimRecord.diagnosis_codes, ClaimRecord.procedure_codes | Code validation API / reference tables | Medium |
| T-05 | Clinical coding plausibility assessment | Reasoning | Agent-led + HITL on condition | ClaimRecord.diagnosis_codes, ClaimRecord.procedure_codes, ClaimRecord.provider_specialty, plausibility knowledge base | Code plausibility knowledge base (vector store) | High |
| T-06 | Prior auth requirement check and lookup | Retrieval | Fully agentic | ClaimRecord.procedure_codes, ClaimRecord.provider_id | Prior auth system API | Medium |
| T-07 | Prior auth partial match resolution | Reasoning | Agent-led + HITL on condition | PriorAuthRecord, PRIOR_AUTH_UNIT_TOLERANCE_PERCENT | Prior auth system API | Medium |
| T-08 | Clinical content routing classification | Decision | Agent-led + HITL on condition | ClaimRecord (all fields), CLINICAL_CONTENT_CONFIDENCE_THRESHOLD | Shared clinical content classifier service | High |
| T-09 | Fee schedule rate lookup and payment calculation | Action | Fully agentic | ClaimRecord.procedure_codes, ClaimRecord.provider_id, ClaimRecord.member_id (plan type from EligibilityCheckResult) | Fee schedule API | Low |
| T-10 | Contract exception handling | Reasoning | Agent-led + HITL on condition | ClaimRecord.procedure_codes, ClaimRecord.provider_id, fee schedule lookup result | Contract exception rules store | High |
| T-11 | Payment approval or rejection record creation | Action | Agent acts, human notified after (AUTO_APPROVED); Fully agentic (AUTO_REJECTED) | All prior check results, AdjudicationDecision schema | Claims management system write API | Medium |
| T-12 | Audit log entry creation | Action | Fully agentic | All inputs and outputs from the current task being logged | Audit log append API | Low |

**Notes:**
- T-03 is HITL on condition: if EligibilityCheckResult.eligibility_status = DISCREPANCY_DETECTED or LOOKUP_FAILED, escalate to HITL. Standard ELIGIBLE result requires no HITL.
- T-05 is HITL on condition: if CodeValidationResult.plausibility_flag = true, escalate to HITL. Valid and plausible combinations proceed autonomously.
- T-07 is HITL on condition: if PriorAuthRecord.tolerance_flag = false AND auth_status = PRESENT_PARTIAL_MATCH, escalate to HITL. Exact match and tolerance-within-range proceed autonomously.
- T-08 is HITL on condition: if ClinicalClassificationResult.confidence_score < CLINICAL_CONTENT_CONFIDENCE_THRESHOLD, human takes over routing. High-confidence classifications proceed autonomously.
- T-10 is HITL on condition: if fee schedule returns no standard rate (CONTRACT_EXCEPTION), escalate to HITL. Standard-rate claims proceed autonomously.
- Every High-risk task (T-03, T-05, T-08, T-10) has a corresponding escalation trigger in §7.

---

## §5. Requirements

```
REQ-A-1: Administrative adjudication pipeline completeness
Description: The agent MUST process every ClaimRecord in NORMALISED state through all seven
  pipeline checks (eligibility, code validity, plausibility, prior auth, clinical content
  classification, duplicate detection, payment calculation) in sequence before producing any
  terminal state transition. No check may be skipped even if a prior check returns a flag.
Acceptance criterion: For any ClaimRecord in AUTO_APPROVED state, the audit log MUST contain
  one entry for each of T-02, T-04, T-05, T-06, T-08, T-09, and T-11 in sequence. Absence of
  any required entry is a pipeline violation; automated pipeline completeness check runs at
  decision write time.
Delegation tier: AGENT_ALONE
Error handling: If any required tool call fails before the pipeline is complete, the claim
  transitions to HITL_EXCEPTION_QUEUE with escalation_type matching the failed check; processing
  is not abandoned.
```

```
REQ-A-2: Clinical content classifier confidence gate
Description: The agent MUST NOT produce an AUTO_APPROVED decision for any claim unless
  ClinicalClassificationResult.classification = ADMINISTRATIVE AND
  ClinicalClassificationResult.confidence_score ≥ CLINICAL_CONTENT_CONFIDENCE_THRESHOLD.
Acceptance criterion: A database CHECK constraint enforces this condition on the
  AdjudicationDecision table: any INSERT with decision_type = AUTO_APPROVED where the
  corresponding ClinicalClassificationResult does not meet both conditions is rejected at
  the database layer. Zero violations in 30-day production audit.
Delegation tier: AGENT_ALONE (blocking constraint — the system enforces it, not the agent's
  judgment)
Error handling: If the classifier service is unavailable, T-08 cannot complete; claim
  transitions to HITL_EXCEPTION_QUEUE with escalation_type = CLASSIFICATION_BELOW_THRESHOLD
  and context_snapshot.failure_reason = CLASSIFIER_SERVICE_UNAVAILABLE.
```

```
REQ-A-3: HITL escalation for below-threshold clinical classification
Description: The agent MUST raise a HITLEscalation(CLASSIFICATION_BELOW_THRESHOLD) and
  transition the claim to HITL_EXCEPTION_QUEUE whenever
  ClinicalClassificationResult.confidence_score < CLINICAL_CONTENT_CONFIDENCE_THRESHOLD,
  regardless of the classification value (ADMINISTRATIVE, CLINICAL, or UNCERTAIN).
Acceptance criterion: For every claim in AUTO_APPROVED state, a ClinicalClassificationResult
  record exists with confidence_score ≥ CLINICAL_CONTENT_CONFIDENCE_THRESHOLD. For every claim
  where confidence_score < threshold, a HITLEscalation with escalation_type =
  CLASSIFICATION_BELOW_THRESHOLD exists in RESOLVED state before any terminal state is reached.
  Verified by automated audit query monthly.
Delegation tier: HUMAN_DECIDES (routing verification — see §8 autonomy matrix)
Error handling: If the HITL queue write fails, the agent MUST NOT proceed to payment
  calculation; claim remains in IN_ADMINISTRATIVE_VALIDATION with a retry flag until the
  HITLEscalation is successfully written.
```

```
REQ-A-4: Audit log entry on every agent action
Description: The agent MUST write an AuditLogEntry to the append-only audit log for every
  action it takes on every claim — including tool calls, state transitions, escalations raised,
  and decisions produced. No agent action may occur without a corresponding log entry.
Acceptance criterion: For any ClaimRecord in a terminal state, the total count of audit log
  entries with entity_id = claim_id MUST equal the total count of tasks completed in the
  pipeline for that claim (verified by pipeline completeness check at AdjudicationDecision
  creation time). Any claim with an audit gap is flagged as AUDIT_INCOMPLETE and routed to
  HITL for manual review before the decision record is released.
Delegation tier: AGENT_LOGS
Error handling: If the audit log write fails, the agent MUST retry up to 3 times with
  exponential backoff before raising an ops alert; the associated claim action is not reversed
  but the AdjudicationDecision.audit_complete flag is held at false until the log entry is
  confirmed written.
```

```
REQ-A-5: Integration failure handling — required system unavailable
Description: The agent MUST handle unavailability of any required external system (eligibility
  API, code validation, prior auth system, classifier service, fee schedule API) without losing
  claim state or producing a decision on incomplete data.
Acceptance criterion: For each required integration, the agent implements a retry policy (3
  attempts, exponential backoff, defined per §11 error handling table). After max retries, the
  claim MUST transition to HITL_EXCEPTION_QUEUE with a context_snapshot capturing: which system
  failed, the HTTP status or timeout type, and the last successful check completed. Zero claims
  in AUTO_APPROVED state that have a LOOKUP_FAILED record for any required check.
Delegation tier: AGENT_LOGS (retry) → HUMAN_DECIDES (after max retries)
Error handling: After max retries, raise HITLEscalation with appropriate escalation_type and
  context_snapshot.failure_reason = [SYSTEM]_UNAVAILABLE; ops team notified within 2 hours SLA.
```

```
REQ-A-6: Governance hard stop — payment blocked without classifier certification
Description: The agent MUST refuse to begin production routing (T-08 clinical content
  classification) if the CLINICAL_CONTENT_CONFIDENCE_THRESHOLD configuration artefact has not
  been loaded and verified as CMO-certified. The threshold MUST NOT default to any hardcoded
  value.
Acceptance criterion: On agent startup, the configuration loader MUST confirm that
  CLINICAL_CONTENT_CONFIDENCE_THRESHOLD was set from a signed configuration artefact with
  co-signer = Dr. Marcus Webb CMO. If the configuration check fails, the agent MUST enter
  CONFIGURATION_INVALID state and route all inbound claims directly to HITL_EXCEPTION_QUEUE
  with escalation_type = CLASSIFICATION_BELOW_THRESHOLD and context_snapshot noting the
  configuration failure. Zero auto-adjudicated claims produced while agent is in
  CONFIGURATION_INVALID state.
Delegation tier: AGENT_ALONE (the block is automatic — no human approval required to block;
  human approval required to resume)
Error handling: Configuration failure raises an immediate ops alert; agent does not process
  claims in isolation while unconfigured.
```

```
REQ-A-7: Prior auth tolerance enforcement
Description: The agent MUST apply PRIOR_AUTH_UNIT_TOLERANCE_PERCENT as the sole configurable
  parameter governing prior auth unit variance acceptance. Tolerance MUST be applied only to
  unit variances (UNIT_VARIANCE partial_match_reason); date and code variant mismatches MUST
  always escalate to HITL regardless of tolerance setting.
Acceptance criterion: For every PriorAuthRecord with tolerance_flag = true, the unit variance
  percentage = (claimed_units - authorised_units) / authorised_units × 100 MUST be ≤
  PRIOR_AUTH_UNIT_TOLERANCE_PERCENT. For every PriorAuthRecord with partial_match_reason in
  [DATE_VARIANCE, CODE_VARIANT], a HITLEscalation(PRIOR_AUTH_PARTIAL_MATCH) MUST exist.
Delegation tier: AGENT_ALONE (tolerance application) / HUMAN_DECIDES (tolerance exceeded or
  non-unit variance)
Error handling: If PRIOR_AUTH_UNIT_TOLERANCE_PERCENT is not set in configuration, treat as 0
  (no tolerance) and escalate all partial matches to HITL; do not default to any positive value.
```

```
REQ-A-8: Duplicate submission detection before payment approval
Description: The agent MUST query submission history for a matching prior claim before
  producing any AUTO_APPROVED decision. A duplicate is confirmed when: member_id, service_date,
  and at least one procedure_code match a prior claim that reached AUTO_APPROVED or
  PHYSICIAN_APPROVED state within the preceding 90 days.
Acceptance criterion: For every AUTO_APPROVED decision, an audit log entry exists confirming
  the duplicate check was performed and returned no confirmed match. For every claim where a
  confirmed duplicate is detected, AdjudicationDecision(AUTO_REJECTED) is produced with
  rejection_code = DUPLICATE_SUBMISSION. Suspected duplicates (partial match — same member and
  date, different procedure codes) raise HITLEscalation(CONTRACT_EXCEPTION) with context noting
  the suspected duplication.
Delegation tier: AGENT_ALONE (confirmed duplicate) / AGENT_PROPOSES (suspected duplicate,
  human reviews)
Error handling: If submission history API is unavailable after max retries, DO NOT proceed to
  payment approval; transition to HITL_EXCEPTION_QUEUE; note history API failure in escalation
  context.
```

---

## §6. Decision Logic

```
Decision: D-A-1 — Eligibility determination
Input: EligibilityCheckResult for this claim (produced by T-02)
Logic:
  IF eligibility_status = ELIGIBLE
    THEN proceed to T-04 (code validation); log T-02 result as ELIGIBLE
  ELSE IF eligibility_status = INELIGIBLE
    THEN create AdjudicationDecision(AUTO_REJECTED, rejection_code = MEMBER_INELIGIBLE);
         transition claim to AUTO_REJECTED
  ELSE IF eligibility_status = DISCREPANCY_DETECTED
    THEN raise HITLEscalation(ELIGIBILITY_DISCREPANCY) with context_snapshot =
         {discrepancy_type, discrepancy_detail, enrollment history excerpt};
         transition claim to HITL_EXCEPTION_QUEUE; STOP — do not proceed to T-04
  ELSE IF eligibility_status = LOOKUP_FAILED
    THEN apply retry policy (T-02 retry, max 3 attempts, exponential backoff);
         IF retries exhausted: raise HITLEscalation(ELIGIBILITY_DISCREPANCY) with
         context_snapshot.failure_reason = ELIGIBILITY_API_UNAVAILABLE;
         transition to HITL_EXCEPTION_QUEUE; STOP
Output: Claim proceeds to T-04 (ELIGIBLE), or claim reaches terminal/HITL state
Delegation tier: AGENT_ALONE (ELIGIBLE, INELIGIBLE) / HUMAN_DECIDES (DISCREPANCY_DETECTED,
  LOOKUP_FAILED)
Confidence gate: Not applicable — eligibility lookup is deterministic; there is no
  confidence score on the binary result. Ambiguity is classified as DISCREPANCY_DETECTED
  and escalated structurally.
Worked example:
  Input values: member_id = M-10045; service_date = 2026-03-15; eligibility API returns
    {status: ELIGIBLE, plan_type: "PPO_GOLD", effective_date: "2024-01-01",
     termination_date: null}
  Branch taken: eligibility_status = ELIGIBLE → proceed to T-04
  Output: EligibilityCheckResult created (eligibility_status = ELIGIBLE, plan_type = PPO_GOLD);
    audit log entry written; claim pipeline continues to T-04
```

```
Decision: D-A-2 — Code validity and plausibility determination
Input: CodeValidationResult for this claim (produced by T-04 + T-05)
Logic:
  IF all_codes_valid = false AND irresolvable_invalid_codes present (code not in ICD-10/CPT
    reference and no near-match available)
    THEN create AdjudicationDecision(AUTO_REJECTED, rejection_codes = INVALID_CODE_COMBINATION);
         transition claim to AUTO_REJECTED
  ELSE IF all_codes_valid = false AND invalid codes are correctable (known format error with
    unambiguous intended code — e.g., trailing digit missing from ICD-10 code)
    THEN raise HITLEscalation(CODING_PLAUSIBILITY) with context_snapshot noting the
         correction candidate; transition to HITL_EXCEPTION_QUEUE; STOP
  ELSE IF all_codes_valid = true AND pairing_valid = true AND plausibility_flag = false
    THEN proceed to T-06 (prior auth check)
  ELSE IF all_codes_valid = true AND plausibility_flag = true
    THEN raise HITLEscalation(CODING_PLAUSIBILITY) with context_snapshot =
         {plausibility_detail, diagnosis_codes, procedure_codes, provider_specialty};
         transition to HITL_EXCEPTION_QUEUE; STOP
  ELSE IF all_codes_valid = true AND pairing_valid = false
    THEN raise HITLEscalation(CODING_PLAUSIBILITY) with context_snapshot noting the
         invalid pairing; transition to HITL_EXCEPTION_QUEUE; STOP
Output: Claim proceeds to T-06 (all valid + plausible), AUTO_REJECTED (irresolvable invalid),
  or HITL_EXCEPTION_QUEUE (correctable invalid, plausibility flag, invalid pairing)
Delegation tier: AGENT_ALONE (irresolvable AUTO_REJECTED, plausible proceed) /
  HUMAN_DECIDES (plausibility flag, correctable invalid, invalid pairing)
Confidence gate: Not applicable to code validity (deterministic). Plausibility flag is
  a boolean produced by the plausibility knowledge base query; the query returns
  a flag, not a confidence score. If the knowledge base is unavailable after retries,
  treat as plausibility_flag = true (conservative) and escalate to HITL.
Worked example:
  Input values: diagnosis_codes = ["K92.1"] (hematemesis), procedure_codes = ["58661"]
    (laparoscopic salpingectomy), provider_specialty = "Gastroenterology"
  Branch taken: all_codes_valid = true; pairing_valid = true (no formal crosswalk violation);
    plausibility_flag = true — a gastrointestinal diagnosis code paired with a gynecological
    procedure from a gastroenterology provider is clinically implausible
  Output: HITLEscalation(CODING_PLAUSIBILITY) raised; context_snapshot includes plausibility_detail
    = "GI diagnosis K92.1 paired with gynecological procedure 58661 billed by gastroenterologist —
    combination is clinically implausible; possible billing error or wrong procedure code";
    claim transitions to HITL_EXCEPTION_QUEUE
```

```
Decision: D-A-3 — Prior authorisation resolution
Input: PriorAuthRecord for this claim (produced by T-06 + T-07)
Logic:
  IF auth_status = NOT_REQUIRED
    THEN proceed to T-08 (clinical content classification)
  ELSE IF auth_status = PRESENT_EXACT_MATCH
    THEN proceed to T-08
  ELSE IF auth_status = PRESENT_PARTIAL_MATCH AND tolerance_flag = true
    THEN proceed to T-08; log tolerance acceptance in audit entry with authorised_units,
         claimed_units, and PRIOR_AUTH_UNIT_TOLERANCE_PERCENT
  ELSE IF auth_status = PRESENT_PARTIAL_MATCH AND tolerance_flag = false
    THEN raise HITLEscalation(PRIOR_AUTH_PARTIAL_MATCH) with context_snapshot =
         {partial_match_reason, authorised_units, claimed_units, auth_start_date,
          auth_end_date, procedure_codes_authorised};
         transition to HITL_EXCEPTION_QUEUE; STOP
  ELSE IF auth_status = PRESENT_EXPIRED
    THEN raise HITLEscalation(PRIOR_AUTH_PARTIAL_MATCH) with context_snapshot noting
         expired auth and auth_end_date; transition to HITL_EXCEPTION_QUEUE; STOP
  ELSE IF auth_status = ABSENT
    THEN dispatch prior auth request to provider (T-06 action);
         transition claim to PENDING_PROVIDER_RESPONSE; STOP
  ELSE IF auth_status = LOOKUP_FAILED
    THEN apply retry policy (T-06 retry, max 3);
         IF retries exhausted: raise HITLEscalation(PRIOR_AUTH_PARTIAL_MATCH) with
         context_snapshot.failure_reason = PRIOR_AUTH_API_UNAVAILABLE;
         transition to HITL_EXCEPTION_QUEUE; STOP
Output: Claim proceeds to T-08, or transitions to PENDING_PROVIDER_RESPONSE, or escalates
  to HITL_EXCEPTION_QUEUE
Delegation tier: AGENT_ALONE (NOT_REQUIRED, EXACT_MATCH, tolerance_flag = true) /
  AGENT_PROPOSES (tolerance_flag = false, EXPIRED) / HUMAN_DECIDES (LOOKUP_FAILED) /
  AGENT_ACTS_HUMAN_NOTIFIED (ABSENT — provider request dispatched, ops team notified)
Confidence gate: Not applicable — prior auth lookup is deterministic.
Worked example:
  Input values: auth_status = PRESENT_PARTIAL_MATCH; partial_match_reason = UNIT_VARIANCE;
    authorised_units = 10; claimed_units = 11; PRIOR_AUTH_UNIT_TOLERANCE_PERCENT = 15
  Calculation: variance = (11 - 10) / 10 × 100 = 10%; 10% ≤ 15% → tolerance_flag = true
  Branch taken: tolerance_flag = true → proceed to T-08
  Output: PriorAuthRecord with tolerance_flag = true; audit log entry: "Prior auth partial
    match accepted under 15% unit tolerance — authorised 10 units, claimed 11 units (10%
    variance)"; claim pipeline continues to T-08
```

```
Decision: D-A-4 — Clinical content routing
Input: ClinicalClassificationResult for this claim (produced by T-08)
Logic:
  IF confidence_score < CLINICAL_CONTENT_CONFIDENCE_THRESHOLD
    THEN raise HITLEscalation(CLASSIFICATION_BELOW_THRESHOLD) with context_snapshot =
         {classification, confidence_score, threshold_applied, feature_snapshot};
         transition to HITL_EXCEPTION_QUEUE; STOP — human reviewer determines routing
  ELSE IF confidence_score ≥ CLINICAL_CONTENT_CONFIDENCE_THRESHOLD AND
          classification = ADMINISTRATIVE
    THEN proceed to T-09 (fee schedule and payment calculation)
  ELSE IF confidence_score ≥ CLINICAL_CONTENT_CONFIDENCE_THRESHOLD AND
          classification = CLINICAL
    THEN transition claim to CLINICAL_REVIEW_QUEUE;
         notify WS2 clinical intake; STOP — WS1 processing complete for this claim
  ELSE IF classification = UNCERTAIN (regardless of confidence_score)
    THEN treat as confidence_score < threshold (conservative);
         raise HITLEscalation(CLASSIFICATION_BELOW_THRESHOLD); transition to
         HITL_EXCEPTION_QUEUE; STOP
Output: Claim proceeds to T-09 (ADMINISTRATIVE, high confidence), routes to WS2
  (CLINICAL, high confidence), or escalates to HITL (below threshold or UNCERTAIN)
Delegation tier: AGENT_ALONE (high-confidence ADMINISTRATIVE or CLINICAL routing) /
  HUMAN_DECIDES (below threshold or UNCERTAIN — human determines routing)
Confidence gate: CLINICAL_CONTENT_CONFIDENCE_THRESHOLD (configurable, CMO-certified).
  Any confidence_score below this value, for any classification output including
  ADMINISTRATIVE, triggers HITL. There is no "ADMINISTRATIVE auto-pass" below threshold.
Worked example:
  Input values: classification = ADMINISTRATIVE; confidence_score = 0.71;
    CLINICAL_CONTENT_CONFIDENCE_THRESHOLD = 0.92
  Branch taken: confidence_score (0.71) < threshold (0.92) → HITL regardless of classification
  Output: HITLEscalation(CLASSIFICATION_BELOW_THRESHOLD) raised; context_snapshot includes
    {classification: ADMINISTRATIVE, confidence_score: 0.71, threshold_applied: 0.92,
     feature_snapshot: {diagnosis_codes: ["M54.5"], procedure_codes: ["99213"], provider_specialty:
     "Internal Medicine"}}; claim transitions to HITL_EXCEPTION_QUEUE; note: the ADMINISTRATIVE
    classification cannot be trusted at this confidence level — human reviewer determines routing
```

```
Decision: D-A-5 — Payment calculation and contract exception detection
Input: Fee schedule lookup result for this claim's procedure_code × provider_id × plan_type;
  duplicate check result; CodeValidationResult, EligibilityCheckResult (for cost-sharing)
Logic:
  IF duplicate_check_result = CONFIRMED_DUPLICATE
    THEN create AdjudicationDecision(AUTO_REJECTED, rejection_code = DUPLICATE_SUBMISSION);
         transition to AUTO_REJECTED
  ELSE IF fee_schedule_lookup = RATE_FOUND AND no exception flag
    THEN calculate payment: base_rate = fee_schedule_rate;
         member_cost_share = apply_plan_deductible_copay(plan_type, billed_amount_cents,
           member_ytd_accumulator);
         payment_amount_cents = base_rate - member_cost_share;
         create AdjudicationDecision(AUTO_APPROVED, payment_amount_cents);
         transition claim to AUTO_APPROVED
  ELSE IF fee_schedule_lookup = NO_STANDARD_RATE (contract exception indicated)
    THEN attempt contract exception rules store lookup (T-10):
         IF exception_rule_found = true: propose payment_amount_cents from exception rate;
           raise HITLEscalation(CONTRACT_EXCEPTION) — human approves before payment is written
         IF exception_rule_found = false OR store_unavailable: raise
           HITLEscalation(CONTRACT_EXCEPTION) with context noting no rule found;
           transition to HITL_EXCEPTION_QUEUE; STOP
  ELSE IF duplicate_check_result = SUSPECTED_DUPLICATE (partial match)
    THEN raise HITLEscalation(CONTRACT_EXCEPTION) with context_snapshot noting suspected
         duplication; transition to HITL_EXCEPTION_QUEUE; STOP
Output: AdjudicationDecision(AUTO_APPROVED) with payment amount, or
  AdjudicationDecision(AUTO_REJECTED) with rejection code, or claim escalated to HITL
Delegation tier: AGENT_ALONE (confirmed duplicate AUTO_REJECTED) /
  AGENT_ACTS_HUMAN_NOTIFIED (AUTO_APPROVED standard path) /
  AGENT_PROPOSES_HUMAN_APPROVES (contract exception — agent proposes amount, human approves)
Confidence gate: Not applicable to fee schedule calculation (deterministic arithmetic).
Worked example:
  Input values: procedure_code = 99213; provider_id = 1234567890; plan_type = PPO_GOLD;
    fee_schedule API returns {rate_cents: 12500}; billed_amount_cents = 18000;
    member_ytd_deductible_remaining_cents = 0; plan_copay_cents = 3000;
    duplicate check returns NO_MATCH
  Branch taken: RATE_FOUND; no exception; no duplicate → standard payment calculation
  Calculation: payment_amount_cents = 12500 - 3000 = 9500
  Output: AdjudicationDecision(AUTO_APPROVED, payment_amount_cents = 9500);
    ClaimRecord transitions to AUTO_APPROVED; audit log entry written; ops team notified
```

---

## §7. Escalation Triggers

| Trigger ID | Trigger condition | Threshold | Action | Notified party | SLA | If SLA breached |
|-----------|-------------------|-----------|--------|----------------|-----|-----------------|
| ET-A-1 | Clinical content confidence below threshold | confidence_score < CLINICAL_CONTENT_CONFIDENCE_THRESHOLD (boolean) | Raise HITLEscalation(CLASSIFICATION_BELOW_THRESHOLD); claim to HITL_EXCEPTION_QUEUE | HITL reviewer team | 4 hours from raised_at | QMG agent flags claim as SLA-risk; supervisor notified; if claim age > 5 days, escalation priority = URGENT |
| ET-A-2 | Eligibility discrepancy detected | eligibility_status = DISCREPANCY_DETECTED or LOOKUP_FAILED (boolean) | Raise HITLEscalation(ELIGIBILITY_DISCREPANCY); claim to HITL_EXCEPTION_QUEUE | HITL reviewer team | 4 hours from raised_at | Escalate to supervisor; if claim sla_deadline < 24 hours, reclassify as URGENT |
| ET-A-3 | Coding plausibility flag or invalid pairing | plausibility_flag = true OR pairing_valid = false (boolean) | Raise HITLEscalation(CODING_PLAUSIBILITY); claim to HITL_EXCEPTION_QUEUE | HITL reviewer team (coding-qualified) | 8 hours from raised_at | Escalate to senior coder; if sla_deadline < 24 hours, reclassify as URGENT |
| ET-A-4 | Prior auth partial match outside tolerance or expired | tolerance_flag = false AND auth_status = PRESENT_PARTIAL_MATCH, OR auth_status = PRESENT_EXPIRED (boolean) | Raise HITLEscalation(PRIOR_AUTH_PARTIAL_MATCH); claim to HITL_EXCEPTION_QUEUE | HITL reviewer team | 4 hours from raised_at | Escalate to supervisor; draft provider outreach requesting updated auth |
| ET-A-5 | Prior auth absent — provider response required | auth_status = ABSENT (boolean) | Dispatch prior auth request to provider; claim to PENDING_PROVIDER_RESPONSE | Provider + ops queue manager | 72 hours from request dispatch | QMG agent re-escalates; if no response and claim age ≥ 5 days, escalate to HITL for manual decision |
| ET-A-6 | Contract exception — no standard fee schedule rate | fee_schedule_lookup = NO_STANDARD_RATE (boolean) | Raise HITLEscalation(CONTRACT_EXCEPTION); agent proposes exception rate if rule found; claim to HITL_EXCEPTION_QUEUE pending approval | HITL reviewer team (contract-qualified) | 8 hours from raised_at | Escalate to Finance team; do not process payment until resolved |
| ET-A-7 | Required integration unavailable after max retries | HTTP 5xx or timeout on 3 consecutive attempts to same API (boolean) | Raise HITLEscalation for the affected check step; claim to HITL_EXCEPTION_QUEUE | Ops / IT team | 2 hours from raised_at | Open incident ticket; all claims in the current batch that required the same system are queued for manual review |

---

## §8. Autonomy Matrix

**AGENT DECIDES ALONE (no HITL required):**
- Member eligibility lookup — standard path with unambiguous ELIGIBLE result (T-02)
- ICD-10/CPT code validity check — standard path with all codes valid (T-04)
- Prior auth presence check — standard path (T-06)
- Prior auth acceptance — auth_status = PRESENT_EXACT_MATCH or NOT_REQUIRED (T-06)
- Prior auth unit variance acceptance — tolerance_flag = true within PRIOR_AUTH_UNIT_TOLERANCE_PERCENT (T-07)
- Clinical content routing — classification = ADMINISTRATIVE or CLINICAL with confidence_score ≥ CLINICAL_CONTENT_CONFIDENCE_THRESHOLD (T-08)
- Fee schedule rate lookup and payment amount arithmetic — standard rate path, no exception (T-09)
- Duplicate submission detection — exact match confirmed (T-08 duplicate check)
- AUTO_REJECTED decision — confirmed duplicate submission (D-A-5)
- AUTO_REJECTED decision — irresolvable invalid code with no correction candidate (D-A-2)
- AUTO_REJECTED decision — INELIGIBLE confirmed (D-A-1)
- Audit log entry creation for every action (T-12)

**AGENT ACTS, HUMAN NOTIFIED AFTER:**
- AUTO_APPROVED payment decision — standard path with all checks passed and confidence ≥ threshold (T-11); ops team receives batch notification within 1 hour of each approved decision
- Prior auth request dispatch to provider — auth_status = ABSENT (T-06); ops queue manager notified
- Claim routing to CLINICAL_REVIEW_QUEUE — classification = CLINICAL with confidence ≥ threshold (T-08); WS2 clinical intake team notified; CMO queue manager receives daily volume report
- Provider return (RETURNED_TO_PROVIDER) — claim cannot be processed due to irreparable submission error (T-01); provider notified with specific error code

**AGENT PROPOSES, HUMAN APPROVES BEFORE ACTION:**
- Contract exception payment amount — agent looks up exception rate and proposes payment_amount_cents; HITL reviewer (contract-qualified) must approve via HITLEscalation(CONTRACT_EXCEPTION) resolution before AdjudicationDecision is written (T-10). The agent prepares: proposed payment amount from exception rules, the applicable contract exception rule citation, and the standard fee schedule rate for comparison. The reviewer authorises by resolving the HITLEscalation with resolution_action = APPROVE and the agreed payment amount.
- Coding plausibility concern resolution — agent flags concern with plausibility_detail; HITL reviewer (coding-qualified) confirms or overrides (T-05)
- Eligibility discrepancy resolution — agent classifies discrepancy type; HITL reviewer confirms or overrides resolution (T-03)
- Prior auth partial match tolerance call — agent documents variance; HITL reviewer decides tolerance acceptance or denial (T-07, tolerance_flag = false cases)

**HUMAN TAKES OVER (agent supports only):**
- Clinical content routing when confidence_score < CLINICAL_CONTENT_CONFIDENCE_THRESHOLD — human reviewer receives the claim with full feature_snapshot and determines routing; agent has no authority to route in either direction until HITLEscalation is resolved
- Any claim where sla_response_deadline has been exceeded on an open HITLEscalation — QMG agent escalates to supervisor; human coordinator determines priority and reassignment

**Enforcement mechanism:** The primary governance gate — blocking payment approval for clinical claims — is **system-enforced**. The ClaimRecord state machine implements a guard condition on the IN_ADMINISTRATIVE_VALIDATION → AUTO_APPROVED transition: the transition is rejected at the database layer if ClinicalClassificationResult.classification ≠ ADMINISTRATIVE or ClinicalClassificationResult.confidence_score < CLINICAL_CONTENT_CONFIDENCE_THRESHOLD for the associated claim. No agent code path can produce AUTO_APPROVED state without satisfying both conditions; the enforcement does not depend on the agent following a procedure. Cross-reference: this assessment must be confirmed consistent with the sign-off integrity risk entry in D4-INT Preamble §6 once integration specifications are finalised.

---

> **§9 Integration contracts:** Produced in `Deliverables/D4a_integration_specs.md` using `prompt_D4_integration_specs.md`. Every system named in §2 inputs and every "Tool required" entry in §4 feeds that deliverable.

---

## §10. State Model

*This section documents the WS1 Administrative Adjudication Agent's authority over the ClaimRecord state machine — specifically which transitions WS1 drives, what guard conditions apply, and which states are outside WS1's authority. The complete ClaimRecord state machine is defined in preamble §2.*

```
States owned or driven by WS1 (subset of full ClaimRecord state machine):
  NORMALISED — entry state for WS1 (produced by Intake & Anomaly Agent)
  IN_ADMINISTRATIVE_VALIDATION — active WS1 processing state
  PENDING_PROVIDER_RESPONSE — async wait for prior auth response
  HITL_EXCEPTION_QUEUE — WS1 exception routing (any of the 7 escalation types)
  CLINICAL_REVIEW_QUEUE — terminal state for WS1 (claim handed off to WS2)
  AUTO_APPROVED — terminal state for WS1 administrative path
  AUTO_REJECTED — terminal state for WS1 administrative path
  RETURNED_TO_PROVIDER — terminal state for malformed claims

States outside WS1 authority (WS1 cannot initiate these transitions):
  IN_PHYSICIAN_REVIEW — owned by Clinical Review Support Agent / physician
  PENDING_ADDITIONAL_INFO — owned by Clinical Review Support Agent
  PHYSICIAN_APPROVED — owned by Clinical Review Support Agent (documents physician decision)
  PHYSICIAN_DENIED — owned by Clinical Review Support Agent (documents physician decision)

WS1-driven transitions:
  NORMALISED → IN_ADMINISTRATIVE_VALIDATION:
    trigger: WS1 agent picks up claim from normalised intake queue
    guard: ClaimRecord.current_state = NORMALISED; no prior WS1 processing record exists
  IN_ADMINISTRATIVE_VALIDATION → PENDING_PROVIDER_RESPONSE:
    trigger: T-06 returns auth_status = ABSENT
    guard: prior auth request has been dispatched to provider; provider communication system
      write confirmed successful
  IN_ADMINISTRATIVE_VALIDATION → HITL_EXCEPTION_QUEUE:
    trigger: any escalation condition in §7 is met
    guard: HITLEscalation record has been successfully written before state transition
  IN_ADMINISTRATIVE_VALIDATION → CLINICAL_REVIEW_QUEUE:
    trigger: D-A-4 branch: classification = CLINICAL AND confidence ≥ threshold
    guard: ClinicalClassificationResult.classification = CLINICAL AND
      ClinicalClassificationResult.confidence_score ≥ CLINICAL_CONTENT_CONFIDENCE_THRESHOLD;
      WS2 clinical intake queue notification sent
  IN_ADMINISTRATIVE_VALIDATION → AUTO_APPROVED:
    trigger: D-A-5 branch: payment calculation succeeds, no duplicate, no exception
    guard: (1) EligibilityCheckResult.eligibility_status = ELIGIBLE;
           (2) CodeValidationResult.all_codes_valid = true AND plausibility_flag = false;
           (3) PriorAuthRecord.auth_status in [NOT_REQUIRED, PRESENT_EXACT_MATCH] OR
               (PRESENT_PARTIAL_MATCH AND tolerance_flag = true);
           (4) ClinicalClassificationResult.classification = ADMINISTRATIVE AND
               confidence_score ≥ CLINICAL_CONTENT_CONFIDENCE_THRESHOLD;
           (5) duplicate_check_result = NO_MATCH;
           (6) fee_schedule_lookup = RATE_FOUND;
           (7) AdjudicationDecision record successfully written;
           (8) audit log entry written
    ALL 8 guard conditions must be true — this is the complete payment gate
  IN_ADMINISTRATIVE_VALIDATION → AUTO_REJECTED:
    trigger: D-A-1 (INELIGIBLE), D-A-2 (irresolvable invalid code), or D-A-5
      (CONFIRMED_DUPLICATE)
    guard: AdjudicationDecision(AUTO_REJECTED) with non-empty rejection_codes array written
      before state transition
  IN_ADMINISTRATIVE_VALIDATION → RETURNED_TO_PROVIDER:
    trigger: T-01 cannot process claim (missing required fields after normalisation)
    guard: provider notification with specific error code sent successfully
  PENDING_PROVIDER_RESPONSE → IN_ADMINISTRATIVE_VALIDATION:
    trigger: provider response received and documented (QMG agent triggers; WS1 resumes)
    guard: prior auth response has been written to the prior auth system and a new
      PriorAuthRecord can be retrieved; claim sla_deadline not yet exceeded
  HITL_EXCEPTION_QUEUE → IN_ADMINISTRATIVE_VALIDATION:
    trigger: HITLEscalation resolved with resolution_action = REQUEST_MORE_INFO or
      resolution that requires agent to resume processing
    guard: HITLEscalation.current_state = RESOLVED; resolved_by non-null

Invalid transitions for WS1 (beyond those listed in shared ClaimRecord definition):
  IN_ADMINISTRATIVE_VALIDATION → IN_PHYSICIAN_REVIEW: FORBIDDEN — WS1 cannot place a claim
    directly in physician review; it can only route to CLINICAL_REVIEW_QUEUE, and the
    Clinical Review Support Agent drives the transition to IN_PHYSICIAN_REVIEW
  AUTO_APPROVED → any state: FORBIDDEN — enforced at database layer (see §8 enforcement
    mechanism)
  HITL_EXCEPTION_QUEUE → AUTO_APPROVED: FORBIDDEN — WS1 cannot approve a claim that is in
    the HITL queue; approval from exception queue must be executed by the human reviewer's
    resolution action, which triggers a separate system write

Guard conditions for the AUTO_APPROVED transition (complete list):
  The IN_ADMINISTRATIVE_VALIDATION → AUTO_APPROVED transition requires ALL of the following
  to be true simultaneously. Missing any one of these conditions causes the transition to be
  rejected at the database layer:
  (1) EligibilityCheckResult exists with eligibility_status = ELIGIBLE for this claim_id
  (2) CodeValidationResult exists with all_codes_valid = true AND plausibility_flag = false
  (3) PriorAuthRecord exists with auth_status in [NOT_REQUIRED, PRESENT_EXACT_MATCH,
      PRESENT_PARTIAL_MATCH with tolerance_flag = true]
  (4) ClinicalClassificationResult exists with classification = ADMINISTRATIVE AND
      confidence_score ≥ CLINICAL_CONTENT_CONFIDENCE_THRESHOLD
  (5) No confirmed duplicate (duplicate check audit log entry confirms NO_MATCH)
  (6) Fee schedule lookup audit log entry confirms RATE_FOUND
  (7) AdjudicationDecision record with decision_type = AUTO_APPROVED is written first
  (8) Audit log entry for T-11 is confirmed written
```

---

## §11. Error Handling

| Failure | Detection method | Agent action | Human notification | Recovery path |
|---------|-----------------|--------------|-------------------|---------------|
| Integration unavailable — member eligibility API returns HTTP 5xx or connection timeout | HTTP status code or timeout exception captured per attempt; failure confirmed after 3 consecutive attempts with exponential backoff (1s, 2s, 4s) | Raise HITLEscalation(ELIGIBILITY_DISCREPANCY) with context_snapshot.failure_reason = ELIGIBILITY_API_UNAVAILABLE; transition claim to HITL_EXCEPTION_QUEUE | Ops / IT team via ops alert channel within 2 hours | IT resolves API availability; HITL reviewer re-queues claim to IN_ADMINISTRATIVE_VALIDATION; agent retries T-02 |
| Required data missing or malformed — ClaimRecord missing required fields after normalisation (e.g., diagnosis_codes array is empty; member_id is null) | Pre-processing field validation check at T-01: validate all required ClaimRecord fields are non-null before beginning pipeline | Log specific missing fields; transition claim to RETURNED_TO_PROVIDER with specific error code(s); send provider notification | Provider receives structured rejection notice with the specific missing fields | Provider resubmits corrected claim; Intake & Anomaly Agent re-normalises; WS1 receives a new NORMALISED ClaimRecord |
| Agent confidence below threshold — classifier returns confidence_score < CLINICAL_CONTENT_CONFIDENCE_THRESHOLD | ClinicalClassificationResult.threshold_met = false detected at T-08 | Raise HITLEscalation(CLASSIFICATION_BELOW_THRESHOLD) with full feature_snapshot; transition to HITL_EXCEPTION_QUEUE; log that routing was not completed autonomously | HITL reviewer team notified (SLA 4 hours per ET-A-1) | Human reviewer determines routing by resolving HITLEscalation; agent resumes from routing decision outcome |
| Governance hard stop triggered — attempt to write AUTO_APPROVED for a CLINICAL claim | Database CHECK constraint rejects the AdjudicationDecision INSERT; constraint violation exception raised in agent runtime | Log constraint violation as a critical audit event; raise HITLEscalation(CLASSIFICATION_BELOW_THRESHOLD) if not already present; do not retry the INSERT; alert ops team immediately | Ops team alerted within 15 minutes; incident ticket opened | Engineering investigates constraint violation cause (classifier failure, configuration error, or code defect); claim held in HITL_EXCEPTION_QUEUE until root cause is resolved and certified safe to resume |
| Duplicate or conflicting record detected — submission history query returns a match | Duplicate check at T-09 returns CONFIRMED_DUPLICATE (exact member_id + service_date + procedure_code match within 90 days) | Create AdjudicationDecision(AUTO_REJECTED, rejection_code = DUPLICATE_SUBMISSION); transition to AUTO_REJECTED | Provider receives AUTO_REJECTED notice with rejection code and original claim reference | Provider reviews; if the submission was a legitimate re-submission (e.g., corrected after prior rejection), provider submits a new claim referencing the original; the new claim is treated as a separate record |
| SLA breach imminent — claim sla_deadline is ≤ 24 hours away and claim is still in IN_ADMINISTRATIVE_VALIDATION or HITL_EXCEPTION_QUEUE | QMG agent monitors sla_deadline across all active claims; triggers alert when sla_deadline - now ≤ 86400 seconds | QMG agent reclassifies any open HITLEscalation for this claim to priority = URGENT; WS1 logs the SLA proximity in the claim's audit trail | HITL reviewer team and supervisor notified immediately | Human reviewer prioritises this claim to the front of the HITL queue; if still unresolved at sla_deadline, supervisor makes a manual decision to prevent SLA penalty |

---

## §14. Spec Ambiguity Register

| Item | Type | Confidence | Description | Impact if unresolved | Resolution |
|------|------|------------|-------------|----------------------|------------|
| A-A-1 | Design gap | Low | PRIOR_AUTH_UNIT_TOLERANCE_PERCENT value is not set. The scenario provides no tolerance threshold for prior auth unit variances. This is a configurable design parameter requiring VP Operations alignment. | Without a defined value, D-A-3 cannot be implemented (tolerance_flag calculation is undefined); all prior auth partial matches default to HITL escalation — increasing HITL queue volume above the 25% target | VP Operations (James Liu) must specify the tolerance percentage during discovery. If he cannot specify it, default to 0% (no tolerance, all partial matches escalate) and document this as a conservative starting point for Wave 1. |
| A-A-2 | Spec ambiguity | Low | Contract exception rules storage format and API access are unknown (A-D2A-5). It is assumed that exception rules exist in documents or email rather than in a structured, accessible system. | If contract rules cannot be accessed programmatically, T-10 cannot be implemented on any standard path — all claims hitting the exception path escalate to HITL. This directly affects the auto-adjudication rate KPI (unlikely to reach 80% if contract exceptions are high-frequency) and means ADR-1's revisit condition cannot be met. | Discovery audit: confirm whether all contract exception rules for in-scope providers are encoded in a structured system. If not, estimate the volume of contract exception claims per day to assess HITL queue impact. Data engineering effort to encode rules is a Wave 1 prerequisite activity if exception volume is material. |
| A-A-3 | Design gap | Low | CODING_PLAUSIBILITY_THRESHOLD (the cutoff below which the plausibility knowledge base flags a combination) is not defined. The knowledge base query returns a boolean flag, but the threshold that determines when the flag fires must be set based on training data. | If the plausibility threshold is too sensitive, the HITL queue is flooded with borderline cases that a processor would approve. If too permissive, plausibility errors pass through, contributing to the 41% overturn rate. | The plausibility knowledge base must be calibrated on historical claims data before go-live. The calibration process mirrors the clinical content classifier calibration: a labelled holdout set of plausibility-flagged claims is reviewed by a coding-qualified reviewer to set the threshold. This is a pre-deployment checklist item for the coding plausibility knowledge base (not yet on the checklist in preamble §7 — flag for addition). |
| A-A-4 | Unknown | Low | Member eligibility API response structure for discrepancy cases is unknown. No eligibility system is named in the scenario. It is assumed the API can return an explicit DISCREPANCY_DETECTED signal; if the API only returns binary ELIGIBLE/INELIGIBLE, discrepancy detection logic must be built on top of the binary result (e.g., detect cases where the service_date is within N days of the termination_date). | If the API cannot surface discrepancy signals, T-03 must implement its own heuristic detection, which increases the risk of false escalations (every near-boundary case gets flagged) or false negatives (discrepancies missed). | Confirmed by IT/ops team during discovery when the eligibility system is identified. If the system is binary-only, define a N-day boundary window parameter that triggers DISCREPANCY_DETECTED classification (e.g., termination_date within 30 days of service_date → DISCREPANCY_DETECTED). |
| A-A-5 | Unknown | Low | Clinical plausibility knowledge base does not exist. No tool currently supports clinical plausibility assessment (MT-WS1-5, Tool Coverage L per D2A). The agent design assumes this can be built as a vector store of historical plausibility flags from prior claims, but the training data source and volume are unknown. | If the plausibility knowledge base cannot be built (insufficient historical labelled data, no access to prior claim adjudication rationale), T-05 cannot perform plausibility assessment — the agent falls back to code validity only, and the plausibility escalation path is unavailable. This means plausibility errors that currently produce the 41% overturn rate continue unchecked. | Confirm whether historical claims data includes adjudication rationale notes that can serve as plausibility training examples. If historical data is insufficient, the plausibility knowledge base is a Wave 1 build-phase deliverable requiring clinical coder input to label training examples. |
| A-A-6 | Unknown | Low | Prior auth system API structure and rate limits are unknown. No prior auth system is named in the scenario. | If the prior auth system is API-accessible but rate-limited below the WS1 throughput requirement (1,300 lookups/day = ~162/hour assuming 8-hour batch window), T-06 must implement throttling and batching logic that adds latency to the pipeline. If the system is not API-accessible (manual lookup only), WS1-JtD-1 prior auth check cannot be automated, and this step remains human-led — blocking the auto-adjudication rate target. | IT discovery: confirm whether the prior auth system has a documented API, what the rate limits are, and whether a BAA is in place for programmatic access. Document in D4a_integration_specs.md. |
| A-A-7 | Unknown | Low | Fee schedule API structure, data model, and the exact representation of CONTRACT_EXCEPTION cases are unknown. It is assumed the API returns a rate (in cents) or a signal indicating no standard rate exists. If the API returns zero for no-standard-rate cases, the agent must distinguish between a legitimately zero-cost procedure and a missing-rate exception. | If zero is ambiguous (free procedure vs. missing rate), the duplicate detection step described in D-A-5 cannot reliably identify contract exceptions — the agent may approve zero-payment claims that should be flagged for exception review, producing an undetected financial error. | IT discovery: confirm the fee schedule API response structure for zero-rate and no-rate cases. Define a clear CONTRACT_EXCEPTION signal distinct from zero-cost procedures. Document in D4a_integration_specs.md. |
| A-A-8 | Unknown | Medium | Submission history query scope (what counts as a duplicate window) is set at 90 days in REQ-A-8 as an assumption. The correct window for duplicate detection may vary by plan type or procedure category; 90 days may produce false positives (resubmissions of previously denied claims are not duplicates) or false negatives (duplicate submissions spaced further apart). | If the window is too short, duplicate submissions go undetected. If too long, legitimate resubmissions are incorrectly rejected, increasing the appeals load and provider relationship risk. | VP Operations to confirm the appropriate duplicate detection window during discovery. If no guidance is available, 90 days is the working assumption pending post-launch calibration. A false-positive duplicate rejection can always be corrected through appeal; a false-negative duplicate is a payment integrity risk. |
