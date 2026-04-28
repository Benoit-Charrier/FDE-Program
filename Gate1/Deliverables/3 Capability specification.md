# Capability Specification
## FNOL Processing Agent — Insurance Claims Automation

---

## 1. Purpose and scope

### Purpose
The FNOL Processing Agent automates the first-notice-of-loss intake workflow for a mid-size insurance company receiving 300 claims per day as unstructured text across three input channels (email, phone transcript, web form). The agent parses incoming claims, classifies claim type and severity, validates policy coverage against the legacy policy administration system, routes the claim to the appropriate adjuster via the CRM, and sends a claimant acknowledgement — all within the 2-hour SLA window. Routine claims are handled end-to-end without specialist involvement. Claims that exceed confidence thresholds, are high-value, are ambiguous, or carry special handling flags are escalated to human specialists with a structured briefing note. The agent does not make final decisions on coverage disputes or escalation communications; those remain human-owned per the delegation boundaries in Deliverable 2.

### In scope
- Ingestion of unstructured claim text from email, phone transcript, and web form
- Extraction of structured claim attributes using NLP (loss date, loss description, claim type, policy identifier, estimated loss value)
- Claim type classification (motor, property, liability, health, other)
- Severity assessment (LOW, MEDIUM, HIGH, CRITICAL) with delegation-tier routing
- Special handling flag detection (fatality, legal representation, vulnerable claimant, fraud indicator)
- Policy record retrieval from the legacy policy administration system via SOAP
- Policy in-force validation (active status at date of loss)
- Coverage match confidence scoring and delegation-tier routing
- Coverage exclusion candidate identification
- Adjuster specialty derivation and workload-balanced assignment via CRM
- Claimant receipt acknowledgement (sent within 5 minutes of claim receipt, unconditionally)
- Claimant routing confirmation (sent on successful adjuster assignment, standard claims only)
- Structured escalation briefing note generation for specialist-handled claims
- Claim document storage in the document management system
- SLA monitoring and breach-prevention alerting
- Duplicate claim detection
- Full audit logging of all agent decisions and actions

### Out of scope
- Claims adjustment (determining settlement amounts or reserve values)
- Fraud investigation (the agent flags; investigation is out of scope)
- Coverage dispute resolution (human-only per D2 tier 2.6)
- Escalation and special-handling claimant communications (human-only per D2 tier 4.3)
- Policy issuance, renewal, or endorsement
- Adjuster workforce scheduling or capacity management
- Legal proceedings management
- Any action on claims with status COVERAGE_DENIED (handed off to specialist)
- Integration with any system not named in the scenario (CRM, policy admin system, DMS)

---

## 2. Inputs and outputs

### Inputs

| Input | Source system | Format | Required / Optional | Validation rule |
|---|---|---|---|---|
| Email claim text | Email inbox (CRM-integrated) [ASSUMED: CRM polls or webhooks the inbox] | Plain text or HTML, max 50,000 chars | Required | Must contain at least one of: policy number pattern `[A-Z]{2}-[0-9]{8}` OR claimant name; reject and log if neither present |
| Phone transcript text | Call centre transcription system [ASSUMED: transcripts delivered to CRM or shared folder] | Plain text, max 50,000 chars | Required | Must be non-empty string of length ≥ 50 chars; reject and log if below minimum |
| Web form submission | CRM web form endpoint | JSON object (see REQ-1 for field list) | Required | All required fields present per web form schema; validated at ingestion before processing begins |
| Policy record | Legacy policy administration system (SOAP) | XML SOAP response (see §7 integration contract) | Required for coverage validation | Policy ID extracted from claim input must match exactly one policy record; if zero or multiple, enter COVERAGE_UNCERTAIN state |
| Adjuster pool | CRM (REST) | JSON array of adjuster objects | Required for routing | Must contain ≥ 1 adjuster with matching specialty; if empty, enter QUEUE_OVERFLOW state |

### Outputs

| Output | Target system / recipient | Format | Trigger condition |
|---|---|---|---|
| ClaimRecord | CRM (REST POST) | JSON (see Entity: Claim) | On every claim ingestion; created before processing begins |
| ClaimAuditLog entry | Audit log store [ASSUMED: CRM audit module or separate logging service — see D5-U6] | JSON (see §10 audit schema) | On every agent action |
| Claimant receipt acknowledgement | Claimant (email via CRM) | Plain text email, templated (see REQ-7) | Within 5 minutes of ClaimRecord creation, unconditionally |
| Claimant routing confirmation | Claimant (email via CRM) | Plain text email, templated (see REQ-8) | When claim transitions to ROUTED state AND special_handling_flags = [] |
| Adjuster assignment notification | Adjuster (CRM notification) | CRM notification (see REQ-6) | When ClaimAssignment record is created |
| Specialist escalation briefing | Human specialist (CRM review queue) | Structured JSON briefing note (see REQ-9) | When claim enters any PENDING_REVIEW or ESCALATED state |
| Claim document | Document management system | Original input text + extracted attributes as PDF [ASSUMED: PDF generation is within agent scope — see D5-U7] | On claim ingestion, before triage begins |
| SLA breach warning | Operations team [ASSUMED: via CRM alert or email — see D5-U6] | CRM alert | When remaining time to SLA deadline ≤ 30 minutes AND claim status ≠ COMPLETED |

---

## 3. Entity definitions

```
Entity: Claim
Attributes:
- id: UUID v4, primary key, required, generated on creation, immutable
- external_reference: string, format [A-Z]{2}-[0-9]{8}, required, generated on creation, immutable, unique
- source_channel: enum [EMAIL, PHONE_TRANSCRIPT, WEB_FORM], required, immutable
- raw_input: string, max 50,000 chars, required, immutable
- policy_id: string, format [A-Z]{2}-[0-9]{8}, required (extracted from raw_input), immutable
- loss_date: ISO 8601 date (YYYY-MM-DD), required [ASSUMED: always extractable from input — see D5-U5]
- loss_description: string, max 5,000 chars, required (extracted), immutable
- claim_type: enum [MOTOR, PROPERTY, LIABILITY, HEALTH, OTHER], required after TRIAGING
- classification_confidence: decimal(4,3), range 0.000–1.000, required after TRIAGING
- severity: enum [LOW, MEDIUM, HIGH, CRITICAL], required after TRIAGING
- severity_score: integer, range 0–100, required after TRIAGING [TODO: scoring model to be validated with client — see D5-U1]
- special_handling_flags: array of enum [FATALITY, LEGAL_REPRESENTATION, VULNERABLE_CLAIMANT, FRAUD_INDICATOR], default [], updated after TRIAGING
- fraud_score: decimal(4,3), range 0.000–1.000, optional [TODO: fraud scoring model — see D5-U2]
- parse_confidence: decimal(4,3), range 0.000–1.000, required after PARSING
- policy_status: enum [IN_FORCE, LAPSED, UNCERTAIN], required after VALIDATING
- coverage_match_confidence: decimal(4,3), range 0.000–1.000, required after VALIDATING
- coverage_status: enum [COVERED, NOT_COVERED, UNCERTAIN, DISPUTED], required after VALIDATING
- exclusion_candidates: array of strings (policy clause references), default []
- status: enum [see state machine below], required, default RECEIVED
- sla_deadline: ISO 8601 timestamp UTC, = created_at + 7200 seconds, required, immutable
- sla_breached: boolean, default false, set to true when current_time > sla_deadline AND status ≠ COMPLETED
- agent_id: string (agent version identifier), required, immutable
- created_at: ISO 8601 timestamp UTC, required, immutable
- updated_at: ISO 8601 timestamp UTC, required, updated on every state transition

State machine:
- RECEIVED → PARSING: on ClaimRecord creation
- PARSING → PARSED: parse_confidence ≥ 0.70
- PARSING → PARSE_UNCERTAIN: parse_confidence < 0.70
- PARSE_UNCERTAIN → PARSING: specialist corrects extracted fields and triggers re-parse
- PARSED → TRIAGING: automatic, no condition
- TRIAGING → TRIAGED: severity ∈ {LOW, MEDIUM} AND special_handling_flags = [] AND classification_confidence ≥ 0.85
- TRIAGING → TRIAGE_PENDING_REVIEW: severity ∈ {HIGH, CRITICAL} OR special_handling_flags ≠ [] OR classification_confidence < 0.85
- TRIAGE_PENDING_REVIEW → TRIAGED: specialist confirms within review window
- TRIAGE_PENDING_REVIEW → ESCALATED: review window expires (30 min for severity; 15 min for flags) with no specialist action
- TRIAGED → VALIDATING: automatic, no condition
- VALIDATING → COVERAGE_CONFIRMED: coverage_match_confidence ≥ 0.85 AND exclusion_candidates = [] AND policy_status = IN_FORCE
- VALIDATING → COVERAGE_PENDING_REVIEW: (coverage_match_confidence ≥ 0.70 AND coverage_match_confidence < 0.85) OR exclusion_candidates ≠ []
- VALIDATING → COVERAGE_DISPUTED: coverage_match_confidence < 0.70 OR policy_status = UNCERTAIN
- VALIDATING → COVERAGE_LAPSED: policy_status = LAPSED
- COVERAGE_PENDING_REVIEW → COVERAGE_CONFIRMED: specialist approves within review window
- COVERAGE_PENDING_REVIEW → COVERAGE_DISPUTED: specialist refers to dispute resolution
- COVERAGE_PENDING_REVIEW → ESCALATED: review window expires (30 min) with no specialist action
- COVERAGE_DISPUTED → COVERAGE_CONFIRMED: specialist resolves — coverage accepted
- COVERAGE_DISPUTED → COVERAGE_DENIED: specialist resolves — coverage denied
- COVERAGE_CONFIRMED → ROUTING: automatic, no condition
- ROUTING → ROUTED: adjuster_available_count ≥ 1 AND adjuster assigned in CRM
- ROUTING → QUEUE_OVERFLOW: adjuster_available_count = 0 for required specialty
- QUEUE_OVERFLOW → ROUTED: specialist manually assigns adjuster
- ROUTED → ACKNOWLEDGED: receipt acknowledgement delivered (always fires ≤ 5 min post-RECEIVED regardless of routing state)
- ACKNOWLEDGED → COMPLETED: routing confirmation sent (standard claims)
- Any non-terminal state → INTEGRATION_ERROR: required external system unavailable after retry exhaustion
- INTEGRATION_ERROR → [state at time of error]: specialist resolves integration issue; agent retries
- RECEIVED → DUPLICATE: duplicate detection check fires within 60 seconds of RECEIVED

Terminal states: COMPLETED, COVERAGE_DENIED, DUPLICATE

Invalid transitions:
- COMPLETED → any state (terminal — cannot be re-opened by agent)
- COVERAGE_DENIED → ROUTING (denied claims must not be routed to an adjuster)
- DUPLICATE → any state other than COMPLETED (duplicate claims must not be processed)
- ROUTING → VALIDATING (routing cannot loop back to coverage validation)
- TRIAGED → PARSING (triage result cannot revert to parse state without specialist reset)

Constraints:
- sla_deadline must equal created_at + 7200 seconds; cannot be modified after creation
- coverage_status = COVERED must not be set when policy_status = LAPSED
- status = ROUTED requires ClaimAssignment.claim_id = this.id to exist
- special_handling_flags = [LEGAL_REPRESENTATION] requires claim_status ≠ ACKNOWLEDGED until specialist confirms communication channel
```

```
Entity: ClaimAssignment
Attributes:
- id: UUID v4, primary key, required, generated on creation, immutable
- claim_id: UUID, foreign key → Claim.id, required, immutable, on delete: restrict
- adjuster_id: string (CRM adjuster identifier), required
- adjuster_specialty: enum [MOTOR, PROPERTY, LIABILITY, HEALTH, GENERAL], required
- assignment_method: enum [AGENT_ALGORITHM, MANUAL_SPECIALIST], required, immutable
- queue_depth_at_assignment: integer, ≥ 0, required
- assigned_by: string (agent_id or specialist_id), required, immutable
- created_at: ISO 8601 timestamp UTC, required, immutable
- superseded_at: ISO 8601 timestamp UTC, null by default; set if reassignment occurs
- superseded_by: UUID → ClaimAssignment.id, null by default

State machine:
- ACTIVE: current assignment
- ACTIVE → SUPERSEDED: a new ClaimAssignment is created for the same claim_id
- SUPERSEDED: previous assignment; retained for audit

Terminal states: SUPERSEDED (once superseded, never re-activated)

Constraints:
- At most one ClaimAssignment per claim_id with status = ACTIVE at any time
- adjuster_specialty must match Claim.claim_type mapping (see Decision 3)
- Cannot create a new ACTIVE assignment if Claim.status = COMPLETED or COVERAGE_DENIED
```

```
Entity: AdjusterQueueEntry
Attributes:
- adjuster_id: string, required (CRM identifier)
- adjuster_specialty: enum [MOTOR, PROPERTY, LIABILITY, HEALTH, GENERAL], required
- current_queue_depth: integer, ≥ 0, required
- is_available: boolean, required
- last_updated: ISO 8601 timestamp UTC, required

State machine:
- AVAILABLE: is_available = true
- AVAILABLE → UNAVAILABLE: is_available set to false (out of office, at capacity [ASSUMED: CRM exposes availability flag])
- UNAVAILABLE → AVAILABLE: is_available set to true

Constraints:
- Agent reads AdjusterQueueEntry as read-only; CRM is authoritative source
- Agent must re-query AdjusterQueueEntry within 30 seconds before creating ClaimAssignment to prevent stale assignment [ASSUMED: CRM supports real-time availability — see D5-U4]
```

```
Entity: AcknowledgementRecord
Attributes:
- id: UUID v4, primary key, required, generated on creation, immutable
- claim_id: UUID, foreign key → Claim.id, required, immutable, on delete: restrict
- acknowledgement_type: enum [RECEIPT, ROUTING_CONFIRMATION, ESCALATION_NOTICE], required, immutable
- recipient_contact: string (email address), required, immutable [ASSUMED: claimant email always available — see D5-U5]
- template_id: string (template version identifier), required, immutable
- rendered_content: string (final message text), required, immutable
- sent_at: ISO 8601 timestamp UTC, required, immutable
- delivery_status: enum [SENT, DELIVERED, FAILED], required, default SENT
- delivery_confirmed_at: ISO 8601 timestamp UTC, null until delivery confirmed
- retry_count: integer, ≥ 0, default 0, max 1 (one retry only)

State machine:
- SENT → DELIVERED: delivery confirmation received from email provider
- SENT → FAILED: delivery failure received OR no confirmation within 60 seconds
- FAILED → SENT: retry triggered (max 1 retry; if second attempt fails, status = FAILED and specialist notified)

Constraints:
- acknowledgement_type = RECEIPT must have sent_at ≤ Claim.created_at + 300 seconds
- One RECEIPT AcknowledgementRecord per claim_id (cannot send two initial receipts)
- acknowledgement_type = ROUTING_CONFIRMATION requires Claim.status = ROUTED before creation
- acknowledgement_type = ROUTING_CONFIRMATION must not be created if Claim.special_handling_flags ≠ []
```

```
Entity: EscalationBriefing
Attributes:
- id: UUID v4, primary key, required, generated on creation, immutable
- claim_id: UUID, foreign key → Claim.id, required, immutable, on delete: restrict
- escalation_reason: enum [LOW_PARSE_CONFIDENCE, LOW_CLASSIFICATION_CONFIDENCE, HIGH_SEVERITY, SPECIAL_FLAG_DETECTED, AMBIGUOUS_COVERAGE, COVERAGE_DISPUTE, QUEUE_OVERFLOW, SLA_RISK, INTEGRATION_ERROR], required, immutable
- escalation_detail: string (structured summary), max 2,000 chars, required, immutable
- claim_snapshot: JSON (Claim attributes at time of escalation), required, immutable
- policy_snapshot: JSON (policy record at time of escalation), optional
- review_window_deadline: ISO 8601 timestamp UTC, required (= escalation created_at + review window in seconds)
- assigned_to_specialist_id: string, optional (null until specialist picks up)
- created_at: ISO 8601 timestamp UTC, required, immutable
- resolved_at: ISO 8601 timestamp UTC, null until specialist acts
- resolution: enum [CONFIRMED, CORRECTED, REFERRED, OVERRIDDEN], optional (null until resolved)

State machine:
- OPEN: awaiting specialist review
- OPEN → RESOLVED: specialist acts within review_window_deadline
- OPEN → EXPIRED: review_window_deadline passes with no action; claim transitions to ESCALATED

Constraints:
- One OPEN EscalationBriefing per claim_id at any time (cannot open two simultaneous escalations for the same claim)
- resolved_at must be ≤ review_window_deadline to count as within-SLA
```

---

## 4. Requirements

```
REQ-1: Claim Ingestion and Attribute Extraction
Description: The agent must ingest claim inputs from all three source channels (EMAIL, PHONE_TRANSCRIPT, WEB_FORM) and extract the following structured attributes using NLP: policy_id, loss_date, loss_description, estimated_loss_value [ASSUMED: always estimable from input — see D5-U5], claimant_contact_email [ASSUMED: always present — see D5-U5], claim_narrative (cleaned text for downstream classification). Extraction must assign a parse_confidence score in range 0.000–1.000.
Acceptance criterion: For a test set of 50 representative claim inputs (to be defined by client before build [TODO: D5-U8 — no sample data available]), extraction must achieve parse_confidence ≥ 0.70 on ≥ 85% of inputs within 10 seconds of receipt per claim.
Delegation tier: AGENT_ONLY (1.1)
Error handling: If parse_confidence < 0.70, claim transitions to PARSE_UNCERTAIN. EscalationBriefing created with escalation_reason = LOW_PARSE_CONFIDENCE. Specialist notified within 5 minutes via CRM review queue. Claim processing halts until specialist corrects extracted fields and triggers re-parse.
```

```
REQ-2: Claim Type Classification
Description: The agent must classify every parsed claim into exactly one claim_type: MOTOR, PROPERTY, LIABILITY, HEALTH, or OTHER. Classification must produce a classification_confidence score in range 0.000–1.000. If classification_confidence ≥ 0.85, classification is accepted as AGENT_LOG. If classification_confidence < 0.85, claim transitions to TRIAGE_PENDING_REVIEW.
Acceptance criterion: On a held-out test set validated against client ground-truth labels [TODO: D5-U8], classification must achieve ≥ 90% accuracy at confidence ≥ 0.85, measured as (correct classifications / total classifications at threshold). Classification latency must be ≤ 5 seconds per claim.
Delegation tier: AGENT_LOG (1.2) / AGENT_REVIEW (1.2, when confidence < 0.85)
Error handling: If classification_confidence < 0.85, EscalationBriefing created with escalation_reason = LOW_CLASSIFICATION_CONFIDENCE. Specialist confirms or corrects within 30-minute review window. If window expires, claim transitions to ESCALATED; specialist notified with SLA remaining time displayed.
```

```
REQ-3: Severity Assessment
Description: The agent must assess claim severity as LOW, MEDIUM, HIGH, or CRITICAL using a severity scoring model that takes as inputs: claim_type, estimated_loss_value, claim_narrative, and special_handling_flags. The severity_score (0–100) maps to severity tiers as follows: 0–39 = LOW, 40–59 = MEDIUM, 60–79 = HIGH, 80–100 = CRITICAL [TODO: scoring model and value thresholds to be validated with client — see D5-U1]. Claims with severity ∈ {LOW, MEDIUM} are processed via AGENT_LOG. Claims with severity ∈ {HIGH, CRITICAL} are escalated to AGENT_REVIEW.
Acceptance criterion: Severity assessment must complete within 3 seconds of classification_confidence being set. For LOW/MEDIUM claims, claim must transition to TRIAGED within 3 seconds of severity assignment with no human action required. For HIGH/CRITICAL claims, EscalationBriefing must be created within 5 seconds of severity assignment.
Delegation tier: AGENT_LOG for LOW/MEDIUM (1.3); AGENT_REVIEW for HIGH/CRITICAL (1.4)
Error handling: If severity scoring model fails to produce a score (e.g., model service unavailable), default severity = HIGH and escalate. Log failure with claim_id and error detail. Never default to LOW or MEDIUM on scoring failure.
```

```
REQ-4: Special Handling Flag Detection
Description: The agent must scan every parsed claim for four special handling flags. Detection rules:
  - FATALITY: claim_narrative contains any of keyword set F [TODO: keyword set to be defined with client legal/compliance team — see D5-U9]; OR claim_type = MOTOR AND loss_description contains "fatal" OR "death" OR "deceased"
  - LEGAL_REPRESENTATION: claim_narrative contains "solicitor" OR "lawyer" OR "legal representative" OR "my attorney" [TODO: expand keyword set — see D5-U9]
  - VULNERABLE_CLAIMANT: claim_narrative sentiment_score < 0.20 [ASSUMED: sentiment model available; threshold assumed — see D5-U2] OR claimant_age > 75 [ASSUMED: age extractable from input — see D5-U5]
  - FRAUD_INDICATOR: fraud_score ≥ 0.60 [TODO: fraud model and threshold — see D5-U2]
Any detected flag triggers AGENT_REVIEW with a 15-minute review window. Multiple flags are reported in a single EscalationBriefing.
Acceptance criterion: False negative rate (flag present but not detected) must be < 2% on a labelled test set [TODO: D5-U8]. False positive rate must be < 20% (acceptable cost for safety-critical flags). Detection must complete within 5 seconds of parse_confidence being set.
Delegation tier: AGENT_REVIEW (1.5)
Error handling: If any flag detection model fails, default to SPECIAL_FLAG_DETECTED = true for FATALITY and LEGAL_REPRESENTATION categories, and escalate. Log model failure. Never suppress flag detection on model failure.
```

```
REQ-5: Policy Coverage Validation
Description: The agent must retrieve the policy record from the policy administration system using policy_id, validate policy in-force status at loss_date, and compute coverage_match_confidence for the classified claim_type against the policy's covered perils. Coverage routing follows:
  - policy_status ≠ IN_FORCE: transition to COVERAGE_LAPSED; EscalationBriefing created
  - coverage_match_confidence ≥ 0.85 AND exclusion_candidates = []: AGENT_LOG; transition to COVERAGE_CONFIRMED
  - coverage_match_confidence ≥ 0.70 AND coverage_match_confidence < 0.85, OR exclusion_candidates ≠ []: AGENT_REVIEW; 30-minute review window
  - coverage_match_confidence < 0.70: HUMAN_ONLY; transition to COVERAGE_DISPUTED; specialist assigned
Acceptance criterion: Policy retrieval must complete within 8 seconds of TRIAGED state. Coverage confidence scoring must complete within 5 seconds of successful policy retrieval. Total validation step (retrieve + validate) must complete within 15 seconds of TRIAGED state for 95% of claims.
Delegation tier: AGENT_ONLY for retrieval (2.1); AGENT_LOG for in-force check (2.2); AGENT_LOG for high-confidence match (2.3); AGENT_REVIEW for ambiguous match (2.4, 2.5); HUMAN_ONLY for disputes (2.6)
Error handling: If policy retrieval fails after 3 retries (see §7 integration contract), claim transitions to INTEGRATION_ERROR. Specialist notified within 5 minutes. Manual policy lookup triggered. If policy_id matches zero records, coverage_status = UNCERTAIN and claim escalated. If policy_id matches multiple records [ASSUMED: policy IDs are unique — see D5-U3], claim escalated with escalation_reason = COVERAGE_DISPUTE.
```

```
REQ-6: Adjuster Routing
Description: The agent must assign every claim with status COVERAGE_CONFIRMED to an available adjuster with matching specialty. Specialty mapping: MOTOR → MOTOR, PROPERTY → PROPERTY, LIABILITY → LIABILITY, HEALTH → HEALTH, OTHER → GENERAL. Selection algorithm: lowest current_queue_depth among available adjusters with matching specialty [TODO: confirm selection algorithm with client — see D5-U4]. Assignment is written to CRM as a ClaimAssignment record. Adjuster is notified via CRM notification within 60 seconds of assignment.
Acceptance criterion: Routing must complete within 10 seconds of COVERAGE_CONFIRMED state for 95% of claims. CRM assignment write must be confirmed (HTTP 200 or 201) before claim transitions to ROUTED. Adjuster notification must be sent within 60 seconds of ClaimAssignment creation.
Delegation tier: AGENT_LOG for specialty derivation (3.1); AGENT_ONLY for adjuster selection (3.2); AGENT_LOG for CRM assignment (3.3); AGENT_ONLY for adjuster notification (3.4)
Error handling: If no adjuster available for required specialty, claim transitions to QUEUE_OVERFLOW. EscalationBriefing created with escalation_reason = QUEUE_OVERFLOW. Specialist notified immediately. Agent retries routing every 5 minutes for up to 60 minutes; if no adjuster available after 60 minutes, claim remains in QUEUE_OVERFLOW and SLA breach warning fires.
```

```
REQ-7: Claimant Receipt Acknowledgement
Description: The agent must send a receipt acknowledgement to the claimant within 300 seconds (5 minutes) of ClaimRecord.created_at. This step fires unconditionally — it does not wait for triage, coverage validation, or routing to complete. The acknowledgement must contain: (a) claim external_reference, (b) statement that the claim has been received and is being processed, (c) the 2-hour SLA commitment (i.e. "you will be contacted within 2 hours"), (d) a contact number or email for queries [TODO: client to provide contact details — see D5-U9]. The message must not contain any statement about coverage status, adjuster identity, or claim outcome.
Acceptance criterion: AcknowledgementRecord with acknowledgement_type = RECEIPT must be created with sent_at ≤ Claim.created_at + 300 seconds for 100% of claims (no exceptions). Delivery confirmation must be received within 60 seconds of sending. If delivery fails, one retry fires immediately; if retry fails, specialist is notified within 5 minutes for manual send.
Delegation tier: AGENT_ONLY (4.1)
Error handling: If email delivery fails on first attempt, retry once immediately. If retry fails, create AcknowledgementRecord with delivery_status = FAILED and add to specialist manual-send queue within 5 minutes. Log failure with claim_id, recipient_contact, failure_reason, and retry_count.
```

```
REQ-8: Claimant Routing Confirmation
Description: The agent must send a routing confirmation to the claimant after claim transitions to ROUTED, provided special_handling_flags = []. The confirmation must contain: (a) claim external_reference, (b) assigned adjuster name [ASSUMED: available in CRM — see D4 from D2], (c) adjuster contact channel [ASSUMED: email or phone available in CRM — see D4 from D2], (d) expected next-contact timeframe [TODO: client to confirm standard expected contact SLA — see D5-U9], (e) claim external_reference for further queries. If special_handling_flags ≠ [], routing confirmation is suppressed; specialist handles claimant communication per HUMAN_ONLY tier 4.3.
Acceptance criterion: AcknowledgementRecord with acknowledgement_type = ROUTING_CONFIRMATION must be created within 120 seconds of Claim transitioning to ROUTED state, for all claims where special_handling_flags = []. Routing confirmation must never be sent for claims with special_handling_flags ≠ [].
Delegation tier: AGENT_LOG (4.2)
Error handling: Same retry logic as REQ-7. If adjuster name or contact channel is not available in CRM, send generic confirmation ("your claim has been assigned; you will be contacted within [X] hours") and log missing data fields for specialist follow-up.
```

```
REQ-9: Human Escalation and Review Queue
Description: For every claim that enters a PENDING_REVIEW, ESCALATED, COVERAGE_DISPUTED, or QUEUE_OVERFLOW state, the agent must create an EscalationBriefing and add it to the CRM specialist review queue. The briefing must contain: claim_id, external_reference, escalation_reason, escalation_detail (plain-text summary of what triggered escalation and what the agent determined), claim_snapshot (all Claim attributes at escalation time), policy_snapshot (if available), review_window_deadline, and time remaining before SLA breach. The review queue must be orderable by review_window_deadline ascending (most urgent first).
Acceptance criterion: EscalationBriefing must be created and visible in CRM review queue within 30 seconds of claim entering a review state. Review queue must support sort by review_window_deadline. Specialist must be able to action (confirm/correct/refer) a briefing from within the CRM interface without switching systems.
Delegation tier: AGENT_REVIEW / AGENT_SUPPORT / HUMAN_ONLY (varies per sub-task)
Error handling: If CRM write fails for EscalationBriefing, retry 3× with exponential backoff. If all retries fail, send email alert directly to on-call specialist with briefing content in email body. Log CRM write failure with claim_id and error detail.
```

```
REQ-10: SLA Monitoring and Breach Prevention
Description: The agent must monitor every active claim's time-to-SLA-deadline. At T-30 minutes (30 minutes before sla_deadline), if claim status ≠ COMPLETED, the agent must fire a breach-prevention alert. The alert must include: claim_id, external_reference, current status, time remaining, and the next step required to progress the claim. Alert destination: operations team [ASSUMED: CRM alert or email — see D5-U6]. The agent must also set Claim.sla_breached = true when current_time > sla_deadline AND claim status ≠ COMPLETED. SLA status must be visible on each EscalationBriefing.
Acceptance criterion: Breach-prevention alert must fire within 60 seconds of T-30 minutes for 100% of at-risk claims. Claim.sla_breached must be set to true within 60 seconds of sla_deadline passing for any non-COMPLETED claim. Alert must include all five required fields.
Delegation tier: AGENT_LOG (monitoring); AGENT_ONLY (alert send)
Error handling: If alert delivery fails, retry once immediately. If retry fails, log failure with claim_id. SLA breach status is still recorded in ClaimRecord regardless of alert delivery failure.
```

---

## 5. Decision logic

```
Decision: Severity Triage
Input: claim_type (enum), estimated_loss_value (decimal), severity_score (integer 0–100), special_handling_flags (array)
Logic:
  IF special_handling_flags ≠ [] THEN
    → escalate to AGENT_REVIEW (tier 1.5); create EscalationBriefing (escalation_reason = SPECIAL_FLAG_DETECTED)
  ELSE IF severity_score ≥ 80 THEN
    → severity = CRITICAL; escalate to AGENT_REVIEW (tier 1.4); create EscalationBriefing (escalation_reason = HIGH_SEVERITY)
  ELSE IF severity_score ≥ 60 THEN
    → severity = HIGH; escalate to AGENT_REVIEW (tier 1.4); create EscalationBriefing (escalation_reason = HIGH_SEVERITY)
  ELSE IF severity_score ≥ 40 THEN
    → severity = MEDIUM; log decision (tier 1.3); transition to TRIAGED
  ELSE
    → severity = LOW; log decision (tier 1.3); transition to TRIAGED
  [TODO: severity_score thresholds require validation with client against historical claim data — see D5-U1]
Output: Claim.severity set; Claim.status updated; EscalationBriefing created if AGENT_REVIEW triggered
Delegation tier: AGENT_LOG for LOW/MEDIUM; AGENT_REVIEW for HIGH/CRITICAL
```

```
Decision: Coverage Validation
Input: policy_status (enum), coverage_match_confidence (decimal), exclusion_candidates (array), loss_date (date), policy_start_date (date), policy_end_date (date)
Logic:
  IF policy_status ≠ IN_FORCE OR loss_date < policy_start_date OR loss_date > policy_end_date THEN
    → coverage_status = NOT_COVERED; Claim.status = COVERAGE_LAPSED; create EscalationBriefing
  ELSE IF coverage_match_confidence < 0.70 THEN
    → coverage_status = DISPUTED; Claim.status = COVERAGE_DISPUTED; create EscalationBriefing (HUMAN_ONLY)
  ELSE IF coverage_match_confidence ≥ 0.70 AND coverage_match_confidence < 0.85 THEN
    → coverage_status = UNCERTAIN; Claim.status = COVERAGE_PENDING_REVIEW; create EscalationBriefing (AGENT_REVIEW); 30-min window
  ELSE IF exclusion_candidates ≠ [] THEN
    → coverage_status = UNCERTAIN; Claim.status = COVERAGE_PENDING_REVIEW; create EscalationBriefing (AGENT_REVIEW); 30-min window
  ELSE
    → coverage_status = COVERED; Claim.status = COVERAGE_CONFIRMED; log decision
Output: Claim.coverage_status set; Claim.coverage_match_confidence set; Claim.status updated
Delegation tier: AGENT_LOG for confirmed coverage; AGENT_REVIEW for ambiguous; HUMAN_ONLY for disputes
```

```
Decision: Adjuster Routing
Input: claim_type (enum), severity (enum), AdjusterQueueEntry[] (array of available adjusters)
Logic:
  specialty_required = specialty_map[claim_type]
    where specialty_map = {MOTOR: MOTOR, PROPERTY: PROPERTY, LIABILITY: LIABILITY, HEALTH: HEALTH, OTHER: GENERAL}
  candidates = [a for a in AdjusterQueueEntry where a.adjuster_specialty = specialty_required AND a.is_available = true]
  IF candidates = [] THEN
    → Claim.status = QUEUE_OVERFLOW; create EscalationBriefing (escalation_reason = QUEUE_OVERFLOW)
  ELSE
    → selected = candidates.sort_by(current_queue_depth ASC)[0]  [TODO: confirm selection algorithm — see D5-U4]
    → create ClaimAssignment(adjuster_id = selected.adjuster_id, assignment_method = AGENT_ALGORITHM)
    → Claim.status = ROUTED
Output: ClaimAssignment created; Claim.status = ROUTED or QUEUE_OVERFLOW
Delegation tier: AGENT_ONLY
```

```
Decision: Escalation Trigger
Input: Claim.status, EscalationBriefing.review_window_deadline, current_time
Logic:
  IF Claim.status ∈ {TRIAGE_PENDING_REVIEW, COVERAGE_PENDING_REVIEW} AND
     current_time > EscalationBriefing.review_window_deadline AND
     EscalationBriefing.resolved_at IS NULL THEN
    → Claim.status = ESCALATED; EscalationBriefing.status = EXPIRED
    → send urgent CRM alert to operations team with claim_id and time_overdue
  ELSE IF current_time > Claim.sla_deadline - 1800 AND Claim.status ≠ COMPLETED THEN
    → fire SLA breach-prevention alert (REQ-10)
  ELSE IF current_time > Claim.sla_deadline AND Claim.status ≠ COMPLETED THEN
    → Claim.sla_breached = true; log breach with claim_id, final_status, breach_duration_seconds
Output: Claim.status updated if escalated; alert sent if SLA at risk; Claim.sla_breached set if deadline passed
Delegation tier: AGENT_LOG
```

---

## 6. Escalation triggers

| Trigger condition | Threshold | Action | Notified party | SLA | If SLA breached |
|---|---|---|---|---|---|
| Parse confidence low | parse_confidence < 0.70 | Create EscalationBriefing; halt processing | On-call specialist (CRM queue) | Specialist must act within 60 minutes | Claim.status = ESCALATED; operations notified |
| Classification confidence low | classification_confidence < 0.85 | Create EscalationBriefing; await specialist confirmation | On-call specialist (CRM queue) | 30 minutes | Claim.status = ESCALATED; SLA warning sent |
| High / Critical severity | severity_score ≥ 60 | Create EscalationBriefing; await specialist confirmation | On-call specialist (CRM queue) | 30 minutes | Claim.status = ESCALATED; SLA warning sent |
| Special handling flag detected | special_handling_flags ≠ [] | Create EscalationBriefing; 15-min window | On-call specialist (CRM queue) | 15 minutes | Claim.status = ESCALATED; escalate to senior specialist |
| Ambiguous coverage | coverage_match_confidence ≥ 0.70 AND < 0.85 | Create EscalationBriefing; await specialist confirmation | On-call specialist (CRM queue) | 30 minutes | Claim.status = ESCALATED; SLA warning sent |
| Exclusion candidate identified | exclusion_candidates.count ≥ 1 | Create EscalationBriefing; await specialist confirmation | On-call specialist (CRM queue) | 30 minutes | Claim.status = ESCALATED; SLA warning sent |
| Coverage disputed | coverage_match_confidence < 0.70 OR coverage_type = DISPUTED | Create EscalationBriefing; HUMAN_ONLY; no agent action until specialist decides | Senior specialist (CRM queue) | No automated window; claim stays in COVERAGE_DISPUTED | Claim.sla_breached flagged; operations notified |
| Policy lapsed | policy_status ≠ IN_FORCE | Create EscalationBriefing; HUMAN_ONLY | Senior specialist (CRM queue) | No automated window | Claim.sla_breached flagged; operations notified |
| No adjuster available | adjuster_available_count = 0 for required specialty | Create EscalationBriefing; retry every 5 min for 60 min | On-call specialist (CRM queue) | 60 minutes to manual assignment | Claim.status = ESCALATED; SLA breach imminent |
| SLA breach risk | current_time > sla_deadline - 1800 seconds AND status ≠ COMPLETED | Send SLA breach-prevention alert | Operations team | Alert must fire ≥ 30 min before breach | N/A (alert IS the action) |
| Receipt ACK delivery failed | AcknowledgementRecord.delivery_status = FAILED after retry | Add to manual-send queue | On-call specialist | 15 minutes to manual send | Log; escalate to operations |
| Integration unavailable | External system returns HTTP 5xx × 3 OR timeout × 3 | Transition to INTEGRATION_ERROR; notify specialist | On-call specialist | 30 minutes to manual resolution | Claim.sla_breached flagged if no resolution within SLA |

---

## 7. Integration contracts

### 7.1 CRM (Modern — REST API)

```
Integration: CRM
Purpose: Create and update Claim records; read and write ClaimAssignment records;
         read AdjusterQueueEntry data; send adjuster notifications; post to specialist
         review queue; send claimant acknowledgement emails via CRM email service
Protocol: REST / HTTPS
Base URL: [ASSUMED: https://crm.client.internal/api/v1 — to be confirmed with client]
Authentication: OAuth 2.0 Bearer token; client_credentials grant;
                token stored in environment variable CRM_ACCESS_TOKEN;
                token endpoint: [ASSUMED: https://crm.client.internal/oauth/token];
                token TTL: 3600 seconds; refresh 60 seconds before expiry

Operations:

  CREATE_CLAIM:
    Method: POST
    Path: /claims
    Request (JSON):
      {
        "external_reference": string (required, format [A-Z]{2}-[0-9]{8}),
        "source_channel": enum [EMAIL, PHONE_TRANSCRIPT, WEB_FORM] (required),
        "raw_input": string (required, max 50000 chars),
        "policy_id": string (required),
        "loss_date": string ISO 8601 date (required),
        "loss_description": string (required, max 5000 chars),
        "status": string = "RECEIVED" (required),
        "sla_deadline": string ISO 8601 datetime UTC (required),
        "agent_id": string (required),
        "created_at": string ISO 8601 datetime UTC (required)
      }
    Response (HTTP 201):
      { "id": UUID, "external_reference": string, "created_at": string }
    Response (HTTP 400): { "error": string, "field": string }
    Response (HTTP 409): { "error": "duplicate_external_reference" }
    Response (HTTP 5xx): { "error": string, "trace_id": string }
    Timeout: 5000ms
    Retry: HTTP 5xx or timeout: 3 retries, exponential backoff 1s/2s/4s
           HTTP 4xx: no retry; log and escalate
    Rate limit: [UNKNOWN — flag for client confirmation; assume 100 req/min]
    Fallback: If CREATE_CLAIM fails after retries, write claim to local buffer file
              (claim_id + raw_input + timestamp); alert specialist within 5 minutes;
              retry from buffer when CRM recovers

  UPDATE_CLAIM_STATUS:
    Method: PATCH
    Path: /claims/{claim_id}
    Request (JSON):
      {
        "status": enum (required),
        "updated_at": string ISO 8601 datetime UTC (required),
        "[any other fields being updated]": value
      }
    Response (HTTP 200): { "id": UUID, "status": string, "updated_at": string }
    Response (HTTP 404): { "error": "claim_not_found" }
    Response (HTTP 409): { "error": "invalid_status_transition", "from": string, "to": string }
    Timeout: 3000ms
    Retry: HTTP 5xx or timeout: 3 retries, exponential backoff 1s/2s/4s
    Rate limit: [UNKNOWN]
    Fallback: If status update fails after retries, log failure with claim_id and target_status;
              add to retry queue; alert specialist if claim is in a time-critical state

  GET_ADJUSTER_QUEUE:
    Method: GET
    Path: /adjusters?specialty={specialty}&is_available=true
    Request: Query params only
    Response (HTTP 200):
      {
        "adjusters": [
          {
            "adjuster_id": string,
            "adjuster_specialty": enum,
            "current_queue_depth": integer,
            "is_available": boolean,
            "last_updated": string ISO 8601 datetime UTC
          }
        ]
      }
    Response (HTTP 200, empty): { "adjusters": [] }
    Timeout: 3000ms
    Retry: HTTP 5xx or timeout: 2 retries, exponential backoff 1s/2s
    Rate limit: [UNKNOWN]
    Fallback: If GET_ADJUSTER_QUEUE fails after retries, transition claim to QUEUE_OVERFLOW;
              notify specialist immediately

  CREATE_CLAIM_ASSIGNMENT:
    Method: POST
    Path: /claim-assignments
    Request (JSON):
      {
        "claim_id": UUID (required),
        "adjuster_id": string (required),
        "adjuster_specialty": enum (required),
        "assignment_method": enum [AGENT_ALGORITHM, MANUAL_SPECIALIST] (required),
        "queue_depth_at_assignment": integer (required),
        "assigned_by": string (required),
        "created_at": string ISO 8601 datetime UTC (required)
      }
    Response (HTTP 201): { "id": UUID, "claim_id": UUID, "adjuster_id": string }
    Response (HTTP 409): { "error": "active_assignment_exists" }
    Timeout: 5000ms
    Retry: HTTP 5xx or timeout: 3 retries, exponential backoff 1s/2s/4s
    Rate limit: [UNKNOWN]
    Fallback: If assignment fails after retries, transition claim to QUEUE_OVERFLOW; notify specialist

  SEND_EMAIL:
    Method: POST
    Path: /emails
    Request (JSON):
      {
        "to": string (email address, required),
        "subject": string (required, max 200 chars),
        "body": string (required, max 10000 chars, plain text),
        "claim_id": UUID (required, for audit linkage),
        "template_id": string (required),
        "send_at": string ISO 8601 datetime UTC (optional; omit for immediate send)
      }
    Response (HTTP 202): { "message_id": string, "queued_at": string }
    Response (HTTP 400): { "error": string, "field": string }
    Timeout: 5000ms
    Retry: HTTP 5xx or timeout: 1 retry after 2s (receipt ACK only; one retry maximum per REQ-7)
    Rate limit: [UNKNOWN]
    Fallback: Log FAILED AcknowledgementRecord; add to manual-send queue; alert specialist

  CREATE_ESCALATION_BRIEFING:
    Method: POST
    Path: /review-queue
    Request (JSON):
      {
        "claim_id": UUID (required),
        "escalation_reason": enum (required),
        "escalation_detail": string (required, max 2000 chars),
        "claim_snapshot": object (required),
        "policy_snapshot": object (optional),
        "review_window_deadline": string ISO 8601 datetime UTC (required),
        "created_at": string ISO 8601 datetime UTC (required)
      }
    Response (HTTP 201): { "briefing_id": UUID }
    Timeout: 5000ms
    Retry: HTTP 5xx or timeout: 3 retries, exponential backoff 1s/2s/4s
    Rate limit: [UNKNOWN]
    Fallback: If CRM write fails after retries, send email to on-call specialist with full briefing content in body; log failure

Data mapping (internal → CRM):
  Claim.id → /claims/{id} path parameter
  Claim.external_reference → claims.external_reference
  Claim.source_channel → claims.source_channel
  Claim.status → claims.status
  Claim.sla_deadline → claims.sla_deadline
  ClaimAssignment.adjuster_id → claim-assignments.adjuster_id
  AdjusterQueueEntry.adjuster_id ← adjusters[].adjuster_id
  AdjusterQueueEntry.current_queue_depth ← adjusters[].current_queue_depth
```

---

### 7.2 Policy Administration System (Legacy — SOAP)

```
Integration: Policy Administration System
Purpose: Retrieve policy record by policy_id to validate in-force status and
         coverage terms against claim type
Protocol: SOAP over HTTPS
Base URL / endpoint: [ASSUMED: https://policy-admin.client.internal/ws — to be confirmed with client]
Authentication: [ASSUMED: WS-Security UsernameToken; credentials stored in environment
                variables POLICY_ADMIN_USER and POLICY_ADMIN_PASS — to be confirmed with client]

[SCOPE-OUT: Full SOAP contract (WSDL, operation names, request/response XML schemas,
fault codes) is not specifiable from the scenario. The scenario confirms the system
exists and uses SOAP endpoints but provides no WSDL or API documentation.

Resolution: Client to provide WSDL file before build begins.
Build approach: Stub this integration with a configurable mock that accepts a
policy_id and returns a configurable policy record (in-force / lapsed / not-found).
Mock must be replaceable with the real SOAP client by changing one configuration flag
(USE_POLICY_ADMIN_MOCK = true/false in .env).

Known operations required (to be confirmed against WSDL):
  - GetPolicyByID(policy_id: string) → PolicyRecord
  - PolicyRecord fields required by agent:
      policy_id: string
      policy_status: enum [ACTIVE, LAPSED, CANCELLED, SUSPENDED]
      policy_start_date: date
      policy_end_date: date
      covered_perils: array of strings (peril types covered)
      exclusions: array of strings (exclusion clause references)
      policy_holder_name: string
      policy_tier: string [ASSUMED: used in severity scoring — see D5-U1]

Timeout: 8000ms (legacy systems may be slow; confirmed assumption — see D5-U3)
Retry: SOAP fault (server-side): 3 retries, exponential backoff 2s/4s/8s
       SOAP fault (client-side, e.g. invalid policy_id): no retry; log and escalate
       Timeout: 2 retries, same backoff
Rate limit: [UNKNOWN — legacy systems may have undocumented concurrency limits;
             assume max 10 concurrent connections until client confirms — see D5-U3]
Fallback: If policy retrieval fails after retries, transition claim to INTEGRATION_ERROR;
          notify specialist within 5 minutes for manual policy lookup;
          agent cannot proceed with coverage validation until policy record is available]
```

---

### 7.3 Document Management System (DMS)

```
Integration: Document Management System
Purpose: Store original claim input (raw text) and extracted attributes as a
         document associated with the claim record, for adjuster reference and
         regulatory retention
Protocol: [ASSUMED: REST over HTTPS — protocol not stated in scenario; see D5-U6]
Base URL: [ASSUMED: https://dms.client.internal/api/v1 — to be confirmed with client]
Authentication: [ASSUMED: API key in Authorization header; stored in environment
                variable DMS_API_KEY — to be confirmed with client]

Operations:

  STORE_CLAIM_DOCUMENT:
    Method: POST
    Path: [ASSUMED: /documents]
    Request (multipart/form-data or JSON [ASSUMED]):
      {
        "document_type": string = "FNOL_CLAIM" (required),
        "claim_id": UUID (required),
        "external_reference": string (required),
        "content_text": string (raw_input, required),
        "extracted_attributes": object (JSON of extracted claim fields, required),
        "source_channel": enum (required),
        "created_at": string ISO 8601 datetime UTC (required)
      }
    Response (HTTP 201 [ASSUMED]):
      { "document_id": string, "stored_at": string }
    Response (HTTP 400 [ASSUMED]): { "error": string }
    Timeout: 10000ms
    Retry: HTTP 5xx or timeout: 3 retries, exponential backoff 2s/4s/8s
           HTTP 4xx: no retry; log and alert specialist
    Rate limit: [UNKNOWN]
    Fallback: If DMS storage fails after retries, store document to local fallback
              directory (./fallback_docs/{claim_id}.json); log failure;
              alert specialist; retry DMS storage when system recovers.
              Claim processing continues — DMS failure must not block triage or routing.

Data mapping (internal → DMS):
  Claim.id → document.claim_id
  Claim.external_reference → document.external_reference
  Claim.raw_input → document.content_text
  Claim.{all extracted fields} → document.extracted_attributes
  Claim.source_channel → document.source_channel
  Claim.created_at → document.created_at
```

---

## 8. State model

```
States (SCREAMING_SNAKE_CASE):
  RECEIVED, PARSING, PARSED, PARSE_UNCERTAIN,
  TRIAGING, TRIAGE_PENDING_REVIEW, TRIAGED,
  VALIDATING, COVERAGE_PENDING_REVIEW, COVERAGE_DISPUTED, COVERAGE_CONFIRMED,
  COVERAGE_LAPSED, COVERAGE_DENIED,
  ROUTING, QUEUE_OVERFLOW, ROUTED,
  ACKNOWLEDGED, COMPLETED,
  ESCALATED, INTEGRATION_ERROR, DUPLICATE

Transitions:
  RECEIVED → PARSING: ClaimRecord created; DMS store initiated in parallel
  RECEIVED → DUPLICATE: duplicate check returns match within 60 seconds of RECEIVED
  PARSING → PARSED: parse_confidence ≥ 0.70
  PARSING → PARSE_UNCERTAIN: parse_confidence < 0.70
  PARSE_UNCERTAIN → PARSING: specialist submits corrected extracted fields
  PARSED → TRIAGING: automatic
  TRIAGING → TRIAGED: severity ∈ {LOW, MEDIUM} AND special_handling_flags = [] AND classification_confidence ≥ 0.85
  TRIAGING → TRIAGE_PENDING_REVIEW: severity ∈ {HIGH, CRITICAL} OR special_handling_flags ≠ [] OR classification_confidence < 0.85
  TRIAGE_PENDING_REVIEW → TRIAGED: specialist confirms within review window
  TRIAGE_PENDING_REVIEW → ESCALATED: review window expires with no specialist action
  TRIAGED → VALIDATING: automatic
  VALIDATING → COVERAGE_CONFIRMED: policy_status = IN_FORCE AND coverage_match_confidence ≥ 0.85 AND exclusion_candidates = []
  VALIDATING → COVERAGE_PENDING_REVIEW: policy_status = IN_FORCE AND (coverage_match_confidence ≥ 0.70 AND < 0.85 OR exclusion_candidates ≠ [])
  VALIDATING → COVERAGE_DISPUTED: policy_status = IN_FORCE AND coverage_match_confidence < 0.70
  VALIDATING → COVERAGE_LAPSED: policy_status ≠ IN_FORCE
  COVERAGE_PENDING_REVIEW → COVERAGE_CONFIRMED: specialist approves within review window
  COVERAGE_PENDING_REVIEW → COVERAGE_DISPUTED: specialist refers to dispute resolution
  COVERAGE_PENDING_REVIEW → ESCALATED: review window expires with no specialist action
  COVERAGE_DISPUTED → COVERAGE_CONFIRMED: specialist resolves — coverage accepted
  COVERAGE_DISPUTED → COVERAGE_DENIED: specialist resolves — coverage denied
  COVERAGE_CONFIRMED → ROUTING: automatic
  ROUTING → ROUTED: adjuster selected and ClaimAssignment created in CRM
  ROUTING → QUEUE_OVERFLOW: no available adjuster of required specialty
  QUEUE_OVERFLOW → ROUTED: specialist manually creates ClaimAssignment
  ROUTED → ACKNOWLEDGED: AcknowledgementRecord (ROUTING_CONFIRMATION) created
    NOTE: AcknowledgementRecord (RECEIPT) is created at RECEIVED → PARSING transition,
    independently of routing state. ACKNOWLEDGED state reflects routing confirmation sent.
  ACKNOWLEDGED → COMPLETED: all required steps complete
  Any non-terminal state → INTEGRATION_ERROR: required external system unavailable after retry exhaustion
  INTEGRATION_ERROR → [state at time of error]: specialist resolves; agent retries from last stable state

Terminal states: COMPLETED, COVERAGE_DENIED, DUPLICATE

Invalid transitions:
  COMPLETED → any state (COMPLETED is terminal; re-opening requires manual specialist action outside agent scope)
  COVERAGE_DENIED → ROUTING (a denied claim must never be assigned to an adjuster)
  DUPLICATE → any state other than remaining DUPLICATE (duplicate claims are frozen)
  ROUTED → VALIDATING (routing cannot reverse to coverage validation without specialist reset)
  COVERAGE_CONFIRMED → TRIAGE_PENDING_REVIEW (coverage confirmation cannot revert to triage review)
  ACKNOWLEDGED → TRIAGING (acknowledged claims cannot revert to triage)
```

---

## 9. Error handling

| Failure | Detection | Agent action | Human notification | Recovery |
|---|---|---|---|---|
| CRM unavailable | HTTP 5xx × 3 or connection timeout × 3 within 12s total retry window | Transition claim to INTEGRATION_ERROR; write claim to local buffer file with claim_id + status + timestamp | On-call specialist via email within 5 minutes (fallback to email if CRM is down) | Retry from buffer every 5 minutes; resume from last confirmed CRM state when CRM recovers; specialist confirms recovery |
| Policy admin system unavailable | SOAP fault (server) × 3 or timeout × 3 within 28s total retry window | Transition claim to INTEGRATION_ERROR; halt at VALIDATING; log policy_id and failure reason | On-call specialist via CRM (if CRM available) or email within 5 minutes | Specialist performs manual policy lookup; enters policy record via CRM interface; agent resumes VALIDATING on specialist action |
| DMS unavailable | HTTP 5xx × 3 or timeout × 3 | Write to local fallback directory ./fallback_docs/{claim_id}.json; log failure; continue processing (DMS failure is non-blocking) | Specialist notified via CRM alert within 30 minutes (non-urgent) | Retry DMS storage every 15 minutes; specialist confirms when resolved |
| Coverage data missing | policy record retrieved but covered_perils field is empty or null | Set coverage_match_confidence = 0.0; transition to COVERAGE_DISPUTED; create EscalationBriefing | Senior specialist via CRM review queue immediately | Specialist obtains policy details from insurer system directly; enters coverage determination manually |
| Classification confidence below threshold | classification_confidence < 0.85 | Create EscalationBriefing (LOW_CLASSIFICATION_CONFIDENCE); 30-min review window | On-call specialist via CRM review queue | Specialist confirms or corrects claim_type; agent resumes from TRIAGING with corrected classification |
| SLA breach imminent | current_time > sla_deadline - 1800s AND status ≠ COMPLETED | Fire SLA breach-prevention alert (REQ-10) | Operations team via CRM alert | Operations team escalates to senior specialist; manual intervention to accelerate processing |
| Duplicate claim detected | claim with same policy_id AND loss_date AND claim_type exists AND was created within 24 hours [ASSUMED: 24-hour dedup window — see D5-U9] | Transition to DUPLICATE; do not process further; log duplicate_of = original_claim_id | On-call specialist via CRM alert within 5 minutes | Specialist confirms or overrides duplicate status; if override, agent resumes from RECEIVED |
| Receipt ACK delivery failed | AcknowledgementRecord.delivery_status = FAILED after 1 retry | Log ACK_FAILED; add to manual-send queue | On-call specialist via CRM alert within 5 minutes | Specialist sends manual acknowledgement; updates AcknowledgementRecord manually |
| No adjuster available | adjuster_available_count = 0 for required specialty | Transition to QUEUE_OVERFLOW; create EscalationBriefing; retry every 5 minutes for 60 minutes | On-call specialist via CRM review queue immediately | Specialist manually assigns adjuster; agent transitions claim to ROUTED on manual assignment confirmation |

---

## 10. Audit and governance

### Audit log schema
Every agent action writes one audit log entry. All entries include the following base fields:

```
Base audit fields (all entries):
- log_id: UUID v4, generated on write, immutable
- claim_id: UUID, foreign key → Claim.id
- action_type: enum [CLAIM_CREATED, STATUS_TRANSITION, EXTRACTION_COMPLETE,
                     CLASSIFICATION_COMPLETE, SEVERITY_ASSESSED, FLAG_DETECTED,
                     POLICY_RETRIEVED, COVERAGE_VALIDATED, ADJUSTER_SELECTED,
                     ASSIGNMENT_CREATED, ACK_SENT, ESCALATION_CREATED,
                     SPECIALIST_REVIEW_COMPLETE, SLA_WARNING_FIRED, ERROR_LOGGED]
- agent_id: string (agent version identifier)
- timestamp: ISO 8601 datetime UTC, immutable
- duration_ms: integer (processing time for this action)

Additional fields by action_type:
  EXTRACTION_COMPLETE: parse_confidence, extracted_fields (JSON)
  CLASSIFICATION_COMPLETE: claim_type, classification_confidence
  SEVERITY_ASSESSED: severity, severity_score, delegation_tier
  FLAG_DETECTED: flags_detected (array), confidence_per_flag (object)
  POLICY_RETRIEVED: policy_id, retrieval_method, policy_status_returned
  COVERAGE_VALIDATED: coverage_match_confidence, coverage_status, exclusion_candidates (array)
  ADJUSTER_SELECTED: adjuster_id, adjuster_specialty, queue_depth_at_selection, selection_method
  ASSIGNMENT_CREATED: assignment_id, adjuster_id
  ACK_SENT: acknowledgement_type, recipient_contact (masked to first 3 chars + @domain), delivery_status
  ESCALATION_CREATED: escalation_reason, review_window_deadline
  SPECIALIST_REVIEW_COMPLETE: reviewer_id, review_decision, original_value, corrected_value (if applicable)
  SLA_WARNING_FIRED: time_remaining_seconds, current_status
  ERROR_LOGGED: error_type, error_detail, retry_count, recovery_action
  STATUS_TRANSITION: from_status, to_status, transition_trigger
```

### Retention periods

| Log type | Retention period | Basis |
|---|---|---|
| Claim audit log (all entries) | 7 years | [ASSUMED: financial services regulatory requirement — see D5-A-Regulatory] |
| Claimant personal data (name, contact, raw claim text) | As per client data retention policy [UNKNOWN — see D5-U10] | GDPR / data protection |
| Integration error logs | 2 years | [ASSUMED: operational audit requirement] |
| SLA breach logs | 7 years | [ASSUMED: regulatory reporting] |
| Specialist review decisions | 7 years | Professional accountability audit |

### Compliance constraints
- **Data protection [ASSUMED: GDPR applies — see D5-A-Regulatory]:** Raw claim text (raw_input) may contain personal data (name, address, bank details). raw_input must be encrypted at rest. PII fields must be anonymisable on subject access request without deleting the audit record.
- **FCA / insurance regulatory requirements [ASSUMED: UK FCA rules apply — see D5-A-Regulatory]:** Claims handling SLAs and escalation decisions are subject to regulatory audit. Audit trail must be immutable and available for regulator inspection. Coverage dispute decisions must be logged with the name and authorisation level of the deciding specialist.
- **PCI-DSS [ASSUMED: may apply if payment card details appear in claim text]:** Agent must detect and redact payment card numbers (pattern: 16-digit sequences) from raw_input before storage. [TODO: confirm with client whether PCI-DSS applies — see D5-U10]

### HITL checkpoints with SLAs

| Checkpoint | Trigger | Review window | Escalation if breached |
|---|---|---|---|
| Parse uncertainty review | parse_confidence < 0.70 | 60 minutes | Claim.status = ESCALATED; senior specialist assigned |
| Low-confidence classification review | classification_confidence < 0.85 | 30 minutes | Claim.status = ESCALATED; SLA warning fired |
| HIGH/CRITICAL severity confirmation | severity ∈ {HIGH, CRITICAL} | 30 minutes | Claim.status = ESCALATED; senior specialist assigned |
| Special handling flag confirmation | special_handling_flags ≠ [] | 15 minutes | Claim.status = ESCALATED; senior specialist assigned immediately |
| Ambiguous coverage review | 0.70 ≤ coverage_match_confidence < 0.85 | 30 minutes | Claim.status = ESCALATED; SLA warning fired |
| Exclusion check confirmation | exclusion_candidates ≠ [] | 30 minutes | Claim.status = ESCALATED |
| Coverage dispute resolution | coverage_match_confidence < 0.70 | No automated window; specialist owns SLA | Senior specialist; operations notified if sla_deadline within 60 minutes |
| Queue overflow manual routing | adjuster_available_count = 0 | 60 minutes | SLA breach imminent; operations escalated |

---

## 11. Build artefacts

The following artefacts must be produced in `agent_build/` alongside the specification.

### Console application (`agent_build/src/main.py` or equivalent)

The console application must demonstrate the agent's core workflow end-to-end using a single configurable input file. It is not a production runtime; it is a closed build loop demonstration.

**Inputs:**
- `--input` (required): path to a JSON file containing a claim object with fields: source_channel, raw_input, policy_id, loss_date
- `--mock-policy` (required): path to a JSON file containing a mock policy record (used in place of the real SOAP endpoint)
- `--mock-adjusters` (required): path to a JSON file containing a mock adjuster pool array
- `--output-dir` (optional, default: `./output`): directory for HTML report and log output

**Behaviour:**
The application must execute and log each processing step in sequence:
1. Load input claim
2. Parse and extract attributes (log parse_confidence)
3. Classify claim type (log classification_confidence)
4. Assess severity (log severity_score and tier)
5. Detect special handling flags (log any flags found)
6. Validate policy coverage against mock policy record (log coverage_match_confidence)
7. Route to adjuster from mock adjuster pool (log selected adjuster_id and queue_depth)
8. Output final Claim state as JSON
9. Generate HTML report

Each step must print to console: step number, action taken, key output values, delegation tier applied, and whether the step triggered an escalation.

**On escalation:** The console app must print `[ESCALATION] reason: {reason}, review_window: {minutes} min` and continue processing as if a specialist confirmed the agent's recommendation (simulating the happy path through review).

### HTML report (`agent_build/output/report.html`)

The HTML report must be generated after the console application run and must contain:
- Header: claim external_reference, source_channel, processing date/time, total processing time (ms)
- Processing summary table: each step, duration (ms), outcome, delegation tier, escalation triggered (Y/N)
- Claim outcome section: final claim_type, severity, coverage_status, assigned adjuster_id, SLA status (MET / BREACHED)
- Assumptions flagged during run: list of [ASSUMED] markers encountered during processing with their field values

The HTML report must use inline CSS only (no external dependencies) and must render correctly when opened as a local file.

### Workflow diagram (`agent_build/docs/workflow.md` — Mermaid format)

```
flowchart TD
  A([EMAIL / PHONE_TRANSCRIPT / WEB_FORM]) --> B[PARSE & EXTRACT\nREQ-1 · AGENT_ONLY]
  B -->|parse_confidence ≥ 0.70| C[CLASSIFY CLAIM TYPE\nREQ-2 · AGENT_LOG]
  B -->|parse_confidence < 0.70| R1[SPECIALIST REVIEW\nPARSE_UNCERTAIN]
  R1 --> B
  C -->|confidence ≥ 0.85| D[ASSESS SEVERITY\nREQ-3]
  C -->|confidence < 0.85| R2[SPECIALIST REVIEW\nTRIAGE_PENDING_REVIEW]
  R2 --> D
  D -->|LOW / MEDIUM| E[DETECT FLAGS\nREQ-4 · AGENT_REVIEW]
  D -->|HIGH / CRITICAL| R3[SPECIALIST REVIEW\nTRIAGE_PENDING_REVIEW]
  R3 --> E
  E -->|no flags| F[VALIDATE COVERAGE\nREQ-5]
  E -->|flag detected| R4[SPECIALIST REVIEW\n15-min window]
  R4 --> F
  F -->|confidence ≥ 0.85, in force| G[ROUTE TO ADJUSTER\nREQ-6 · AGENT_ONLY]
  F -->|confidence 0.70–0.84 or exclusion| R5[SPECIALIST REVIEW\n30-min window]
  F -->|confidence < 0.70 or disputed| R6[HUMAN ONLY\nCOVERAGE_DISPUTED]
  F -->|policy lapsed| R7[HUMAN ONLY\nCOVERAGE_LAPSED]
  R5 --> G
  G -->|adjuster available| H[ASSIGN IN CRM\nREQ-6 · AGENT_LOG]
  G -->|no adjuster| R8[SPECIALIST MANUAL\nQUEUE_OVERFLOW]
  R8 --> H
  H --> I[NOTIFY ADJUSTER\nREQ-6 · AGENT_ONLY]
  I --> J[SEND ROUTING CONFIRMATION\nREQ-8 · AGENT_LOG]
  J --> K([COMPLETED])

  A -.->|within 5 min, unconditional| ACK[SEND RECEIPT ACK\nREQ-7 · AGENT_ONLY]
  style ACK fill:#d4edda
  style R6 fill:#f8d7da
  style R7 fill:#f8d7da
```

The diagram must be saved as `agent_build/docs/workflow.md` containing the Mermaid block above, and also rendered as a PNG using a Mermaid CLI command documented in `agent_build/docs/README.md`.
