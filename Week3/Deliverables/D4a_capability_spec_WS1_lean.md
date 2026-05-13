# D4a — Capability Specification (Lean): WS1 Intake Agent
### Intake & Matching Agent — WS1 Shift Request Intake Module

> **Lean version:** Sections abbreviated for rapid build. Sections skipped: Preamble §3–§7 (context engineering, risk register, gap analysis). §12 and §13 added for D7 compatibility. All decisions and entities are builder-precise.

---

## §0. Agent Identity

| Field | Value |
|-------|-------|
| **Agent name** | Intake & Matching Agent — WS1 Module |
| **Job to be Done** | Parse an unstructured inbound shift request from ServiceNow, extract a structured matching brief, classify urgency, and route to the coordinator HITL queue or advance to WS2 matching. Replaces coordinator manual read-and-parse of free-text shift requests (~120/coordinator/day). |
| **D3 reference** | WS1-JtD-1, WS1-JtD-2, WS1-JtD-4, WS2-JtD-1 (completeness gate) |
| **Delegation archetype** | Human-led + Agent Support (WS1-JtD-1, JtD-2); Agent-led + Human Oversight (WS1-JtD-4) |
| **Governance hard stop** | Agent MUST NOT advance a brief to WS2 matching if any required field is missing or ambiguous (specialty type, credential level, shift datetime, facility ID). Incomplete briefs are BLOCKED at WS2-JtD-1 gate and written to the HITL queue with specific gaps identified. |

**KPIs:**

| KPI | Baseline | Target | How measured |
|-----|----------|--------|--------------|
| Brief extraction accuracy (required fields correct) | ~0% automated (all manual) | ≥ 92% of fields correct without coordinator edit | Sample audit: 50 briefs/week, coordinator edit rate logged in ServiceNow |
| Time from inbound request to structured brief in queue | 4.2-hr composite time-to-fill (baseline) — extraction step unquantified [assumption A1] | ≤ 3 minutes per request | ServiceNow timestamp: message received → brief_status = READY_FOR_REVIEW |
| HITL escalation rate for WS1 | Unknown baseline [assumption A2] | ≤ 25% of requests require coordinator correction | ServiceNow: count of briefs returned to HITL vs. advanced to WS2 |
| Urgency misclassification rate | Unknown [assumption A2] | ≤ 2% of same-day shifts misclassified as non-urgent | Post-hoc audit: fill loss events traced to urgency misclassification |

---

## §1. Purpose and Scope

**Purpose:** The WS1 module reads unstructured free-text shift requests arriving in ServiceNow, extracts the matching brief fields, classifies message type and urgency, validates brief completeness, and either advances the brief to WS2 or writes it to the coordinator HITL queue with specific gaps flagged. It does not perform nurse matching, credential verification, or any decision requiring facility preference knowledge.

**In scope:**
- Classify inbound ServiceNow message as: STANDARD_SHIFT_REQUEST, MULTI_SHIFT_BLOCK, CANCELLATION, MODIFICATION, UNCLASSIFIABLE
- Extract structured fields from free text: facility_id, unit_type, specialty_required, credential_level, shift_datetime_start, shift_datetime_end, urgency_signal, special_notes
- Classify urgency: EXPLICIT_URGENT (stated keyword or same-day), IMPLICIT_URGENT (datetime proximity ≤ 4 hours at time of processing), STANDARD
- Validate brief completeness against required-field schema
- Write structured MatchingBrief record to ServiceNow with status READY_FOR_REVIEW or NEEDS_COORDINATOR_INPUT
- Write HITL queue item when: message type is UNCLASSIFIABLE, any required field is missing, urgency is IMPLICIT_URGENT (coordinator must confirm pre-emption)
- Log all extraction decisions with confidence scores per field

**Out of scope:**
- Nurse matching, shortlisting, or credential checks — deferred to WS2 module
- Resolving credential ambiguity (hard vs. soft specialty requirement) — coordinator-only per D3 (WS1-JtD-3, D2B 0/7)
- Modifying or building hospital intake channels — out of engagement scope per D2
- After-hours intake routing logic — data dependency (after-hours coordinator coverage not confirmed [D0C: U-4])

---

## §2. Inputs and Outputs

**Inputs:**

| Input | Source system | Format | Required / Optional | Validation rule |
|-------|---------------|--------|---------------------|-----------------|
| Inbound shift request text | ServiceNow — inbound message queue | Unstructured free text (email body or portal submission) | Required | Non-empty string, max 10,000 chars |
| Facility ID lookup table | ServiceNow — facility registry | Structured key-value (facility_name → facility_id) | Required | Facility name extracted from text must resolve to a known facility_id; no match → UNCLASSIFIABLE flag |
| Specialty taxonomy reference | Static config (agent procedural memory) | Structured JSON list of accepted specialty labels and synonyms | Required | Used to normalise extracted specialty string to canonical enum value |
| Existing open placement records for facility | ServiceNow — placement records | Structured JSON | Optional | Used to detect if request is a duplicate or modification of existing open shift |

**Outputs:**

| Output | Target | Format | Trigger condition |
|--------|--------|--------|-------------------|
| MatchingBrief record | ServiceNow — matching_briefs table | Structured JSON (see §3) | Every inbound message that is classifiable |
| HITL queue item | ServiceNow — hitl_queue table | Structured JSON with gap_type and missing_fields[] | When: UNCLASSIFIABLE, required field missing, urgency = IMPLICIT_URGENT |
| Agent audit log entry | ServiceNow — agent_audit_log table | JSON (see §13 schema) | Every message processed |

---

## §3. Entity Definitions

### Entity: MatchingBrief

```
Entity: MatchingBrief

Attributes:
- id: UUID, primary key, immutable, generated on creation
- source_message_id: string, max 128 chars, required, immutable — ServiceNow record sys_id of inbound message
- facility_id: UUID, required, foreign key to Facility registry, on delete: restrict
- unit_type: string, max 64 chars, required — e.g., "ICU", "Med/Surg", "ED"
- specialty_required: enum [RN_GENERAL, RN_ICU, RN_ED, RN_PACU, RN_OR, LPN, CNA, RN_TELE, UNRESOLVED], required
  — UNRESOLVED triggers NEEDS_COORDINATOR_INPUT status
- credential_level: enum [RN, LPN, CNA, NP, UNRESOLVED], required
- shift_datetime_start: ISO 8601 timestamp UTC, required
- shift_datetime_end: ISO 8601 timestamp UTC, required; must be > shift_datetime_start
- urgency: enum [EXPLICIT_URGENT, IMPLICIT_URGENT, STANDARD], required
- message_type: enum [STANDARD_SHIFT_REQUEST, MULTI_SHIFT_BLOCK, CANCELLATION, MODIFICATION, UNCLASSIFIABLE], required
- special_notes: string, max 1000 chars, optional — verbatim extracted text not mapped to structured fields
- brief_status: enum [READY_FOR_REVIEW, NEEDS_COORDINATOR_INPUT, ADVANCED_TO_WS2, CANCELLED], required
- confidence_scores: JSON object — per-field extraction confidence, float 0.0–1.0, required
- missing_fields: array of strings, optional — populated when brief_status = NEEDS_COORDINATOR_INPUT
- created_at: ISO 8601 timestamp UTC, immutable
- updated_at: ISO 8601 timestamp UTC, updated on any modification
- created_by: string "AGENT" or UUID of coordinator who created manually

Relationships:
- facility_id: UUID, foreign key to Facility, many-to-one, on delete: restrict

State machine:
- Initial state: READY_FOR_REVIEW or NEEDS_COORDINATOR_INPUT (set at creation based on completeness check)
- READY_FOR_REVIEW → ADVANCED_TO_WS2: WS2-JtD-1 completeness gate passes
- READY_FOR_REVIEW → NEEDS_COORDINATOR_INPUT: coordinator sends back with corrections request
- NEEDS_COORDINATOR_INPUT → READY_FOR_REVIEW: coordinator completes missing fields
- READY_FOR_REVIEW → CANCELLED: inbound CANCELLATION message received for same source_message_id
- ADVANCED_TO_WS2 → CANCELLED: coordinator cancels after advancing
- Terminal states: CANCELLED — no valid exit

Invalid transitions:
- NEEDS_COORDINATOR_INPUT → ADVANCED_TO_WS2: FORBIDDEN — brief must pass READY_FOR_REVIEW before WS2 advance
- ADVANCED_TO_WS2 → READY_FOR_REVIEW: FORBIDDEN — WS2 pipeline already initiated; cancel and resubmit required
- CANCELLED → any state: FORBIDDEN — terminal

Validation rules:
- shift_datetime_end > shift_datetime_start: boolean, reject on creation if false
- specialty_required != UNRESOLVED when brief_status = ADVANCED_TO_WS2: boolean
- confidence_scores contains a key for every extracted field: boolean
```

### Entity: HITLQueueItem (WS1)

```
Entity: HITLQueueItem

Attributes:
- id: UUID, primary key, immutable
- matching_brief_id: UUID, foreign key to MatchingBrief, required, on delete: cascade
- gap_type: enum [MISSING_REQUIRED_FIELD, UNCLASSIFIABLE_MESSAGE, IMPLICIT_URGENCY_CONFIRMATION, SPECIALTY_AMBIGUITY], required
- missing_fields: array of strings, optional — e.g., ["specialty_required", "shift_datetime_end"]
- agent_note: string, max 500 chars, optional — human-readable explanation of why item was escalated
- assigned_to: UUID (coordinator user ID), optional — null if unassigned
- status: enum [OPEN, IN_REVIEW, RESOLVED, EXPIRED], required
- sla_deadline: ISO 8601 timestamp UTC, required — set at creation as created_at + 30 minutes
- resolved_at: ISO 8601 timestamp UTC, optional
- resolved_by: UUID, optional
- created_at: ISO 8601 timestamp UTC, immutable
- updated_at: ISO 8601 timestamp UTC

State machine:
- Initial state: OPEN
- OPEN → IN_REVIEW: coordinator opens the item
- IN_REVIEW → RESOLVED: coordinator submits corrections; MatchingBrief updated
- OPEN → EXPIRED: current_time > sla_deadline and status = OPEN
- IN_REVIEW → EXPIRED: current_time > sla_deadline and status = IN_REVIEW
- EXPIRED → OPEN: supervisor re-activates (manual only)
- Terminal states: RESOLVED, EXPIRED (unless re-activated)

Invalid transitions:
- RESOLVED → IN_REVIEW: FORBIDDEN — create new HITLQueueItem if re-work needed
- EXPIRED → RESOLVED: FORBIDDEN — must be re-activated to OPEN first
- OPEN → RESOLVED: FORBIDDEN — must pass through IN_REVIEW
```

---

## §4. Activity Catalog

| Task ID | Task name | Task type | Delegation level | Data required | Tool required | Risk level |
|---------|-----------|-----------|-----------------|---------------|---------------|------------|
| WS1-T1 | Receive and parse inbound ServiceNow message | Retrieval | Fully agentic | ServiceNow message queue | ServiceNow read API | Low |
| WS1-T2 | Classify message type | Reasoning | Agent-led + HITL on condition | Message text, facility lookup | Facility registry lookup | Medium |
| WS1-T3 | Extract structured fields from free text | Reasoning | Agent-led + HITL on condition | Message text, specialty taxonomy | Specialty taxonomy config | Medium |
| WS1-T4 | Resolve facility name to facility_id | Retrieval | Fully agentic | Facility registry | ServiceNow read API | Medium |
| WS1-T5 | Classify urgency | Decision | Agent-led + HITL on condition | Extracted shift_datetime_start, message text | System clock | High |
| WS1-T6 | Validate brief completeness (required fields gate) | Decision | Fully agentic | Extracted MatchingBrief fields | None | High |
| WS1-T7 | Write MatchingBrief record to ServiceNow | Action | Fully agentic | Completed MatchingBrief object | ServiceNow write API | Medium |
| WS1-T8 | Write HITL queue item with gap details | Action | Fully agentic | HITLQueueItem fields, missing_fields list | ServiceNow write API | High |
| WS1-T9 | Write agent audit log entry | Action | Fully agentic | All decision inputs and outputs | ServiceNow write API | Low |
| WS1-T10 | Advance completed brief to WS2 pipeline | Action | Fully agentic | MatchingBrief (status = READY_FOR_REVIEW, all fields non-UNRESOLVED) | ServiceNow write API | High |

---

## §5. Requirements

```
REQ-A-1: Structured brief extraction
MUST extract all eight required fields from inbound free text and populate a MatchingBrief record.
Acceptance criterion: ≥ 92% of required fields extracted correctly (measured by coordinator edit rate on 50-brief weekly sample).
Delegation tier: AGENT_PROPOSES — coordinator validates in HITL queue before WS2 advance.
Error handling: If extraction confidence for any required field < 0.70, set that field to UNRESOLVED, add to missing_fields[], set brief_status = NEEDS_COORDINATOR_INPUT, write HITLQueueItem.

REQ-A-2: Completeness gate (governance hard stop)
MUST block any MatchingBrief with specialty_required = UNRESOLVED or any required field absent from advancing to WS2.
Acceptance criterion: 0 MatchingBriefs with status = ADVANCED_TO_WS2 where specialty_required = UNRESOLVED or any required field is null — verified by weekly automated query against ServiceNow.
Delegation tier: AGENT_ALONE — this is a hard schema enforcement check, not a judgment call.
Error handling: Brief is written with status = NEEDS_COORDINATOR_INPUT; HITLQueueItem is created; WS2 pipeline is not triggered.

REQ-A-3: Urgency classification with HITL for implicit signals
MUST classify urgency as EXPLICIT_URGENT when message contains same-day language or stated deadline. MUST classify as IMPLICIT_URGENT when shift_datetime_start − now() ≤ 4 hours. MUST write a HITLQueueItem for coordinator confirmation before pre-empting the active queue for IMPLICIT_URGENT cases.
Acceptance criterion: ≤ 2% of same-day fills misclassified as STANDARD (measured monthly by fill-loss audit).
Delegation tier: AGENT_ALONE for EXPLICIT_URGENT; AGENT_PROPOSES for IMPLICIT_URGENT.
Error handling: If shift_datetime_start cannot be parsed, set urgency = STANDARD and add shift_datetime_start to missing_fields[].

REQ-A-4: Facility resolution
MUST resolve the facility name extracted from message text to a known facility_id using the ServiceNow facility registry. MUST NOT proceed to brief creation with an unresolved facility_id.
Acceptance criterion: 100% of briefs with status ≠ NEEDS_COORDINATOR_INPUT have a valid facility_id foreign key (not null, not a synthetic placeholder).
Delegation tier: AGENT_ALONE.
Error handling: If facility name does not match any entry in the registry (exact or fuzzy match score < 0.80), set message_type = UNCLASSIFIABLE, write HITLQueueItem(gap_type = UNCLASSIFIABLE_MESSAGE).

REQ-A-5: Escalation to HITL queue with SLA
MUST write a HITLQueueItem with sla_deadline = created_at + 30 minutes for every escalated brief. MUST mark HITLQueueItem status = EXPIRED if unresolved at sla_deadline.
Acceptance criterion: 100% of HITL items have sla_deadline populated; expiry flag set within ±60 seconds of deadline (verified by ServiceNow scheduled job log).
Delegation tier: AGENT_ALONE.
Error handling: If ServiceNow write fails for HITLQueueItem, retry up to 3 times with 5-second exponential backoff; if all retries fail, write to local dead-letter log and alert on-call coordinator via SMS fallback.

REQ-A-6: Audit log per message
MUST write one agent_audit_log entry per inbound message processed, containing: source_message_id, all extracted field values, per-field confidence scores, final brief_status, escalation_triggered (boolean), timestamp.
Acceptance criterion: 100% of processed messages have a corresponding audit log entry with all fields populated (verified by daily count reconciliation: messages received = audit log entries).
Delegation tier: AGENT_ALONE.
Error handling: If audit log write fails, the MatchingBrief write is rolled back; the message is re-queued for reprocessing.
```

---

## §6. Decision Logic

```
Decision: Message type classification
Input: Raw message text
Logic:
  IF text contains any of ["cancel", "cancellation", "no longer need"] AND references a prior shift ID THEN
    message_type = CANCELLATION
  ELSE IF text contains ["block", "multiple shifts", "recurring"] AND shift count > 1 parseable THEN
    message_type = MULTI_SHIFT_BLOCK
  ELSE IF text contains ["change", "update", "modify"] AND references a prior shift ID THEN
    message_type = MODIFICATION
  ELSE IF facility name is resolvable AND shift_datetime_start is parseable THEN
    message_type = STANDARD_SHIFT_REQUEST
  ELSE
    message_type = UNCLASSIFIABLE → write HITLQueueItem(gap_type = UNCLASSIFIABLE_MESSAGE)
Output: message_type field set on MatchingBrief
Delegation tier: AGENT_ALONE (standard types); AGENT_PROPOSES for UNCLASSIFIABLE (coordinator resolves)
Confidence gate: N/A — this is rule-based pattern matching, not a scored inference
Worked example:
  Input: "Hi, we need to cancel shift request #SN-2891 for Saturday night ICU."
  Branch taken: text contains "cancel" AND "SN-2891" is a parseable shift ID → CANCELLATION
  Output: message_type = CANCELLATION; no MatchingBrief created; existing brief for SN-2891 set to CANCELLED

Decision: Field extraction confidence gate
Input: Per-field LLM extraction confidence score (float 0.0–1.0) for each of 8 required fields
Logic:
  FOR EACH required_field IN [facility_id, unit_type, specialty_required, credential_level, shift_datetime_start, shift_datetime_end, urgency_signal]:
    IF confidence_score[required_field] >= 0.70 THEN
      accept extracted value, populate field
    ELSE IF confidence_score[required_field] >= 0.50 THEN
      populate field with extracted value AND add to review_flags[] (coordinator sees flagged value in HITL)
    ELSE
      set field = UNRESOLVED, add to missing_fields[]
  IF missing_fields[] is non-empty THEN
    brief_status = NEEDS_COORDINATOR_INPUT
    write HITLQueueItem(gap_type = MISSING_REQUIRED_FIELD, missing_fields = missing_fields[])
  ELSE
    brief_status = READY_FOR_REVIEW
Output: Populated MatchingBrief with brief_status set
Delegation tier: AGENT_ALONE
Confidence gate: Threshold = 0.70 for auto-accept; 0.50–0.69 for flagged-accept; < 0.50 → UNRESOLVED
Worked example:
  Input: specialty confidence = 0.45 (message said "ER or maybe trauma, not sure")
  Branch taken: 0.45 < 0.50 → specialty_required = UNRESOLVED, added to missing_fields[]
  Output: brief_status = NEEDS_COORDINATOR_INPUT; HITLQueueItem created with missing_fields = ["specialty_required"]

Decision: Urgency classification
Input: message text, shift_datetime_start (extracted), now() system timestamp
Logic:
  IF message text contains any of ["urgent", "ASAP", "immediately", "emergency", "same day", "today"] THEN
    urgency = EXPLICIT_URGENT — advance without HITL confirmation
  ELSE IF shift_datetime_start != UNRESOLVED AND (shift_datetime_start − now()) <= 4 hours THEN
    urgency = IMPLICIT_URGENT — write HITLQueueItem(gap_type = IMPLICIT_URGENCY_CONFIRMATION) before pre-empting queue
  ELSE
    urgency = STANDARD
Output: urgency field set; HITL written if IMPLICIT_URGENT
Delegation tier: AGENT_ALONE for EXPLICIT/STANDARD; AGENT_PROPOSES for IMPLICIT_URGENT
Confidence gate: N/A — datetime arithmetic and keyword match are deterministic
Worked example:
  Input: message text = "We need a tele nurse for Thursday 7am" — submitted Tuesday 4:10pm; shift_datetime_start = Thursday 07:00 UTC; now() = Tuesday 16:10 UTC → delta = ~38 hours
  Branch taken: no urgency keyword; delta > 4 hours → urgency = STANDARD
  Output: urgency = STANDARD, no HITL written for urgency; proceed to completeness gate

Decision: Brief completeness gate (WS2 advance decision)
Input: MatchingBrief record — all field values
Logic:
  required_fields = [facility_id, unit_type, specialty_required, credential_level, shift_datetime_start, shift_datetime_end]
  IF ALL required_fields are non-null AND specialty_required != UNRESOLVED AND credential_level != UNRESOLVED THEN
    brief_status = READY_FOR_REVIEW
    trigger WS2 pipeline (if coordinator reviews and approves) OR advance directly if urgency = EXPLICIT_URGENT and all fields confidence >= 0.85
  ELSE
    brief_status = NEEDS_COORDINATOR_INPUT (already set by field extraction decision)
    do NOT trigger WS2 pipeline
Output: MatchingBrief status update; WS2 trigger or HITL block
Delegation tier: AGENT_ALONE — hard schema enforcement
Worked example:
  Input: facility_id = "FAC-0042", unit_type = "ICU", specialty_required = "RN_ICU", credential_level = "RN", shift_datetime_start = "2026-05-15T19:00:00Z", shift_datetime_end = "2026-05-16T07:00:00Z", urgency = STANDARD
  Branch taken: all required fields populated, no UNRESOLVED → brief_status = READY_FOR_REVIEW
  Output: MatchingBrief written to ServiceNow with status = READY_FOR_REVIEW; coordinator sees it in matching queue
```

---

## §7. Escalation Triggers

| Trigger condition | Threshold | Action | Notified party | SLA | If SLA breached |
|-------------------|-----------|--------|----------------|-----|-----------------|
| Required field extraction confidence < 0.50 | < 0.50 per field | Write HITLQueueItem(MISSING_REQUIRED_FIELD); block WS2 advance | On-call coordinator | 30 minutes | HITLQueueItem status → EXPIRED; supervisor SMS alert sent |
| Message type = UNCLASSIFIABLE (facility not resolved or no shift structure) | Boolean | Write HITLQueueItem(UNCLASSIFIABLE_MESSAGE); do not create MatchingBrief | On-call coordinator | 30 minutes | HITLQueueItem status → EXPIRED; supervisor SMS alert sent |
| Urgency = IMPLICIT_URGENT (shift within 4 hours) | shift_datetime_start − now() ≤ 4 hours | Write HITLQueueItem(IMPLICIT_URGENCY_CONFIRMATION); surface to top of coordinator queue | On-call coordinator | 10 minutes | Auto-classify as EXPLICIT_URGENT and advance; log override in audit log |
| ServiceNow write failure after 3 retries | 3 retries exhausted | Write to local dead-letter queue; send SMS to on-call coordinator | On-call coordinator | 5 minutes | Escalate to engineering on-call; message held in dead-letter |

---

## §8. Autonomy Matrix

**AGENT DECIDES ALONE:**
- Classify message type for STANDARD_SHIFT_REQUEST, MULTI_SHIFT_BLOCK, CANCELLATION, MODIFICATION
- Extract all fields from free text and score confidence per field
- Accept fields with confidence ≥ 0.70
- Classify urgency as EXPLICIT_URGENT (keyword match) or STANDARD (no signal, datetime > 4hrs)
- Validate brief completeness schema (required fields present / UNRESOLVED check)
- Write MatchingBrief record to ServiceNow
- Write HITL queue item
- Write audit log entry
- Advance READY_FOR_REVIEW brief to WS2 pipeline when coordinator approves

**AGENT ACTS, HUMAN NOTIFIED AFTER:**
- Flag fields with confidence 0.50–0.69 in the HITL review interface (field is populated but marked for coordinator check)

**AGENT PROPOSES, HUMAN APPROVES BEFORE ACTION:**
- Extracted matching brief before WS2 advance (coordinator sees brief in queue, approves or edits before matching begins)
- IMPLICIT_URGENT pre-emption (coordinator confirms queue jump before it executes; 10-minute SLA; auto-advances if unconfirmed)
- UNCLASSIFIABLE message resolution (coordinator manually classifies and populates fields)

**HUMAN TAKES OVER:**
- Any message where facility_id cannot be resolved after fuzzy match < 0.80
- Specialty requirement ambiguity (hard vs. soft) — WS1-JtD-3, D2B 0/7; agent surfaces the ambiguous text, coordinator decides
- Any coordinator-initiated correction to a brief already in READY_FOR_REVIEW status

**Enforcement mechanism:** The MatchingBrief state machine enforces the governance hard stop **procedurally, not technically** in Phase 1 — the database permits a write of status = ADVANCED_TO_WS2 even if required fields are UNRESOLVED. The agent MUST validate completeness before writing ADVANCED_TO_WS2. A database-level CHECK constraint on specialty_required ≠ UNRESOLVED when status = ADVANCED_TO_WS2 is the recommended technical enforcement and is a **prerequisite before production deployment**. Until that constraint is confirmed in ServiceNow, this is a governance risk (procedure-dependent).

---

## §9. Integration Contracts

### Integration: ServiceNow — Inbound Message Queue (Read)

1. **Purpose:** Poll for new unprocessed inbound shift request records. Agent reads message body and metadata. Agent does NOT modify records in this queue — read-only.
2. **System:** ServiceNow, instance URL: `[SCOPE-OUT — instance URL not confirmed; see §14 A-1]`. Table: `x_medflex_inbound_messages` [assumed table name — A-2].
3. **Authentication:** OAuth 2.0 client credentials flow. Client ID and secret stored in environment secrets manager (not hardcoded). Token TTL: 3600s. Refresh: 60s before expiry. Fallback if token unavailable: pause polling, write to dead-letter, alert on-call.
4. **Endpoint:**
   ```
   GET /api/now/table/x_medflex_inbound_messages
   Query params:
     sysparm_query=processed=false^ORDERBYsys_created_on
     sysparm_limit=50
     sysparm_fields=sys_id,body,sender_email,received_at,channel
   
   Success response (200):
   {
     "result": [
       {
         "sys_id": "abc123",
         "body": "We need an ICU RN for Thursday night 7pm...",
         "sender_email": "scheduling@hospital.org",
         "received_at": "2026-05-15T14:22:00Z",
         "channel": "email"
       }
     ]
   }
   
   Error responses:
     401 → refresh token and retry once; if still 401 → alert, stop polling
     429 → wait 60 seconds, retry; log throttle event
     500/503 → retry with backoff (see error handling); escalate after 3 failures
   ```
5. **Error handling:** 401 → token refresh + 1 retry. 429 → 60s wait + retry. 500/503 → exponential backoff: 5s, 10s, 20s; after 3 failures, write all pending message IDs to dead-letter log, alert on-call coordinator.
6. **Rate limits:** [SCOPE-OUT — ServiceNow instance rate limits not confirmed; assume 60 requests/minute as conservative default; A-3]. Agent MUST NOT exceed 1 poll/10 seconds.
7. **Data mapping:**
   - `sys_id` → `MatchingBrief.source_message_id`
   - `body` → input to LLM extraction prompt
   - `received_at` → used for urgency datetime arithmetic
8. **State sync:** On-demand polling every 10 seconds. No webhook available [assumed — A-4].
9. **Fallback:** If ServiceNow read is unavailable for > 5 minutes, write alert to coordinator dashboard. No auto-retry beyond the 3-attempt policy — hold queue, do not drop messages.
10. **Logging:** Log per poll: timestamp, records_returned count, any error codes received.

---

### Integration: ServiceNow — MatchingBrief Write (Write)

1. **Purpose:** Agent writes the structured MatchingBrief record and updates inbound message record as processed=true.
2. **System:** ServiceNow. Table: `x_medflex_matching_briefs` [assumed — A-2].
3. **Authentication:** Same OAuth 2.0 token as read integration above.
4. **Endpoint:**
   ```
   POST /api/now/table/x_medflex_matching_briefs
   Body (JSON):
   {
     "source_message_id": "abc123",         // string, required
     "facility_id": "FAC-0042",             // UUID string, required
     "unit_type": "ICU",                    // string, required
     "specialty_required": "RN_ICU",        // enum string, required
     "credential_level": "RN",             // enum string, required
     "shift_datetime_start": "2026-05-15T19:00:00Z",  // ISO 8601 UTC, required
     "shift_datetime_end": "2026-05-16T07:00:00Z",    // ISO 8601 UTC, required
     "urgency": "STANDARD",                // enum string, required
     "message_type": "STANDARD_SHIFT_REQUEST", // enum string, required
     "special_notes": "Prefers Spanish-speaking nurse if available", // string, optional
     "brief_status": "READY_FOR_REVIEW",   // enum string, required
     "confidence_scores": {"facility_id": 0.95, "specialty_required": 0.88, ...}, // JSON, required
     "missing_fields": []                  // array, required (empty if none)
   }
   
   Success response (201):
   { "result": { "sys_id": "brief-uuid-here", "brief_status": "READY_FOR_REVIEW" } }
   
   Error responses:
     400 → log validation error, do NOT retry; write to dead-letter with full payload
     401 → token refresh + retry once
     409 → duplicate source_message_id; log and skip (idempotency)
     500 → retry 3x with backoff; alert on-call if all fail
   ```
5. **Error handling:** 400 → no retry (bad payload); log and alert. 409 → idempotent skip. 500 → 3 retries with 5s/10s/20s backoff.
6. **Rate limits:** Same as read integration — assume 60 req/min [A-3].
7. **Data mapping:** All MatchingBrief fields map 1:1 to ServiceNow table columns. Field names must match exactly — no aliasing.
8. **State sync:** Write-once on creation. Updates via PATCH to `x_medflex_matching_briefs/{sys_id}` when coordinator resolves HITL.
9. **Fallback:** If write fails after 3 retries, store brief payload in local dead-letter JSON file with source_message_id and retry timestamp. Alert on-call.
10. **Logging:** Log per write: source_message_id, brief_status written, HTTP response code, timestamp.

---

## §10. State Model

```
States: READY_FOR_REVIEW, NEEDS_COORDINATOR_INPUT, ADVANCED_TO_WS2, CANCELLED
Initial state: READY_FOR_REVIEW or NEEDS_COORDINATOR_INPUT (set at creation based on completeness check)
Terminal states: CANCELLED, ADVANCED_TO_WS2 (WS2 module owns state from this point)

Transitions:
  NEEDS_COORDINATOR_INPUT → READY_FOR_REVIEW: coordinator submits all missing fields via HITL resolution
  READY_FOR_REVIEW → ADVANCED_TO_WS2: completeness gate passes AND coordinator approves (or EXPLICIT_URGENT + all fields confidence ≥ 0.85)
  READY_FOR_REVIEW → NEEDS_COORDINATOR_INPUT: coordinator requests correction
  READY_FOR_REVIEW → CANCELLED: CANCELLATION message received for same source_message_id
  NEEDS_COORDINATOR_INPUT → CANCELLED: coordinator marks request as withdrawn
  ADVANCED_TO_WS2 → CANCELLED: coordinator cancels after WS2 initiated (WS2 must also cancel its pipeline)

Invalid transitions:
  NEEDS_COORDINATOR_INPUT → ADVANCED_TO_WS2: FORBIDDEN — hard stop; completeness gate must pass first
  CANCELLED → any: FORBIDDEN — terminal state; no recovery; create new MatchingBrief if re-submission required
  ADVANCED_TO_WS2 → READY_FOR_REVIEW: FORBIDDEN — WS2 pipeline already running; cancel and resubmit

Guard conditions:
  Transition READY_FOR_REVIEW → ADVANCED_TO_WS2 requires:
    specialty_required != UNRESOLVED
    credential_level != UNRESOLVED
    facility_id is a valid UUID resolvable in facility registry
    shift_datetime_end > shift_datetime_start
```

---

## §11. Error Handling

| Failure | Detection method | Agent action | Human notification | Recovery path |
|---------|-----------------|--------------|-------------------|---------------|
| ServiceNow read API unavailable | HTTP 500/503 or timeout > 10s after 3 retries | Pause polling; write alert to coordinator dashboard | On-call coordinator via SMS | Retry polling every 60s; auto-resume when API responds; no messages dropped |
| Required field cannot be extracted (confidence < 0.50) | Per-field confidence score below threshold | Set field = UNRESOLVED; brief_status = NEEDS_COORDINATOR_INPUT; write HITLQueueItem | Coordinator sees item in HITL queue | Coordinator completes field; brief advances to WS2 |
| Agent extraction confidence globally low (all fields < 0.50) | All confidence scores below threshold | message_type = UNCLASSIFIABLE; write HITLQueueItem | On-call coordinator; 30-min SLA | Coordinator manually creates MatchingBrief from raw message text |
| Governance hard stop: WS2 advance attempted for incomplete brief | brief_status = NEEDS_COORDINATOR_INPUT AND WS2 trigger fired | Block WS2 trigger; log governance violation; alert supervisor | Supervisor notified with brief ID | Review audit log; resolve missing fields; re-trigger WS2 manually |
| Duplicate source_message_id on write | ServiceNow returns HTTP 409 | Skip write; log idempotency event; no alert | None (idempotent) | No recovery needed — original brief already exists |
| HITL SLA breached (30 min elapsed, item unresolved) | Scheduled job checks HITL item sla_deadline vs. now() | Set HITLQueueItem status = EXPIRED; send SMS to supervisor | Supervisor | Supervisor manually re-assigns; EXPIRED item can be re-opened by supervisor only |

---

## §12. Failure Modes

*Distinct from §11 (error handling). §11 covers system and integration failures — the agent crashes, the API is down. §12 covers wrong agent output — the agent runs successfully but produces an incorrect result with downstream consequences.*

---

> **Failure Mode [FM-A-1]: Misclassified message type advances as a standard shift request**
> **What bad output looks like:** A CANCELLATION or MODIFICATION message is classified as STANDARD_SHIFT_REQUEST because the prior-shift-ID lookup returns no match (prior brief was already CANCELLED in ServiceNow). A new MatchingBrief is created with the cancelled shift's parameters and enters the WS2 pipeline — a cancelled shift is actively matched and submitted.
> **Consequence:** Coordinator receives a shortlist for a shift the facility already withdrew. Submission is sent to the facility. Facility is confused; coordinator rework required; relationship friction.
> **Detection:** Daily reconciliation query: MatchingBriefs created within 24h where source facility also sent a CANCELLATION message for the same unit_type + shift_datetime_start window. Any match → flag for coordinator review. Latency: up to 24 hours.
> **Recovery path:** Coordinator cancels the erroneous MatchingBrief (status → CANCELLED); contacts facility to confirm no submission was sent; if submission reached facility, apologises and retracts.
> **Taxonomy:** Design gap — the spec's CANCELLATION rule requires prior_shift_id_present = true, but does not specify the lookup window or what to do when the prior brief is already CANCELLED in ServiceNow. Builder implementing the lookup against only OPEN briefs will miss this case silently.

---

> **Failure Mode [FM-A-2]: Systematic confidence miscalibration — LLM over-reports extraction confidence**
> **What bad output looks like:** The LLM extraction model consistently returns confidence scores ≥ 0.70 for all fields, even on ambiguous or malformed requests (e.g., a message that says "need a nurse, usual unit" with no specialty or datetime). Fields that should score < 0.50 and trigger UNRESOLVED are auto-accepted. Briefs with incorrect specialty and null-equivalent shift times advance to WS2 as READY_FOR_REVIEW.
> **Consequence:** WS2 receives malformed briefs; the candidate query runs against a garbage specialty_required, returning the wrong candidate pool. Coordinator receives a shortlist for the wrong role. If coordinator approves without noticing, a mismatched nurse is submitted — contributing to the 7% mismatch rate at machine speed.
> **Detection:** Weekly golden-set evaluation: 20 known-ambiguous historical messages with ground-truth field labels run through the extractor. If acceptance rate (fields scoring ≥ 0.70 on ambiguous messages) exceeds 40%, the threshold calibration is suspect. Owned by: FDE or QA lead. Alert path: if golden-set agreement with ground truth drops below 80% in any weekly run, freeze deployment and re-calibrate thresholds before the next release.
> **Recovery path:** Revert to previous model version or tighten the confidence gate thresholds (lower auto-accept from 0.70 to 0.85 for a fortnight); re-run golden-set evaluation; restore only when agreement is ≥ 80%.
> **Taxonomy:** Design gap — the spec defines the threshold values but does not specify a golden-set validation mechanism or a recalibration trigger. Without this, systematic over-confidence goes undetected until mismatch rate data surfaces it weeks later.

---

> **Failure Mode [FM-A-3]: Audit evidence incompleteness — HITLQueueItem written without gap details**
> **What bad output looks like:** An exception in the HITLQueueItem write code path causes `missing_fields[]` to be written as an empty array `[]` even when the brief has missing fields (e.g., due to a JSON serialisation bug that drops empty enum UNRESOLVED values). The coordinator opens the HITL item and sees: gap_type = MISSING_REQUIRED_FIELD, missing_fields = []. No indication of which field to fix.
> **Consequence:** Coordinator cannot resolve the item — they don't know what field is missing. Item sits in NEEDS_COORDINATOR_INPUT until it expires. The fill is missed. No exception is raised because the HITLQueueItem was written successfully (just with empty missing_fields).
> **Detection:** Daily ServiceNow query: HITLQueueItems with gap_type = MISSING_REQUIRED_FIELD AND missing_fields = [] created in the past 24 hours. Any result → alert on-call; this should never occur. Latency: up to 24 hours.
> **Recovery path:** Coordinator inspects the source MatchingBrief directly (via matching_brief_id foreign key) to identify UNRESOLVED fields; resolves manually; escalates the serialisation bug to engineering. The HITLQueueItem audit trail is incomplete and cannot be defended if challenged — reviewer must note that the coordinator's resolution was manual.
> **Taxonomy:** Builder misread — §3 entity definition specifies `missing_fields: array of strings, optional — populated when brief_status = NEEDS_COORDINATOR_INPUT`. A builder who serialises the MatchingBrief after setting fields to UNRESOLVED (rather than before) may produce an empty list. The spec is clear; the implementation is wrong.

---

> **Failure Mode [FM-A-4]: Stale facility registry — valid facility name resolves to wrong or deleted facility_id**
> **What bad output looks like:** A facility was renamed (e.g., "St. Mary's Medical Center" → "CommonSpirit Health – St. Mary's"). The fuzzy match still resolves the old name to the old facility_id (score = 0.82, above the 0.80 threshold). The MatchingBrief is created with the correct facility name from the request but the wrong facility_id. WS2 queries candidates against the wrong facility profile, DNR list, and proximity — submitting a nurse who may be on the new facility entity's DNR list.
> **Consequence:** Compliance risk: a nurse on the updated facility's DNR list is submitted because the old facility_id has a clean DNR record. Facility relationship damage. Potential regulatory incident if the DNR exclusion exists for a patient safety reason.
> **Detection:** Monthly facility registry audit: compare MedFlex's internal facility list against facilities that sent shift requests in the past 30 days. Any facility_name in inbound requests that does not match the current registry name (exact match, not fuzzy) → flag for registry update. Owned by: ops team. Additionally, any UNCLASSIFIABLE escalation that coordinators resolve by confirming "this is [known facility]" → trigger a registry update review.
> **Recovery path:** Ops team updates facility registry with new name and confirms facility_id mapping; agent re-processes any briefs created under old facility_id in the affected window.
> **Taxonomy:** Design gap — the spec does not define a facility registry update cadence or a stale-data detection mechanism. The integration contract (§9) specifies on-demand lookup but does not address registry freshness.

---

> **Failure Mode [FM-A-5]: Governance hard stop bypass — ADVANCED_TO_WS2 written with UNRESOLVED specialty**
> **What bad output looks like:** Because the enforcement mechanism for the READY_FOR_REVIEW → ADVANCED_TO_WS2 transition is procedure-dependent (§8 — the database has no CHECK constraint), a race condition or code path error allows a brief with specialty_required = UNRESOLVED to be written with status = ADVANCED_TO_WS2. WS2 receives the brief and queries the nurse database with an UNRESOLVED specialty — which either matches all specialties (if the DB query treats UNRESOLVED as a wildcard) or throws an unhandled error.
> **Consequence:** If the DB treats UNRESOLVED as wildcard: WS2 returns a shortlist of all available nurses regardless of specialty — coordinator is presented a nonsense shortlist for an ICU shift that includes CNA and LPN candidates. If they select without noticing: a non-ICU nurse is submitted. Compliance risk. If DB throws error: WS2 pipeline crashes; no fill; no coordinator alert (crash is silent if error handling is incomplete).
> **Detection:** Daily automated query: MatchingBriefs with status = ADVANCED_TO_WS2 AND specialty_required = 'UNRESOLVED' — count must be 0. Any non-zero result triggers an immediate governance alert to supervisor. The database-level CHECK constraint (§8 enforcement mechanism note) is the technical prevention; until it is deployed, this daily query is the detection backstop. Latency: up to 24 hours.
> **Recovery path:** Immediately cancel the affected MatchingBrief; any downstream PlacementSubmissions created from it must be reviewed and withdrawn if a nurse was submitted against the UNRESOLVED specialty. Engineering deploys the CHECK constraint as an emergency hotfix. Incident log entry required.
> **Taxonomy:** Design gap — the spec acknowledges the procedure-dependent enforcement risk in §8 but the mitigation (the CHECK constraint) is labelled as a pre-deployment prerequisite, not a monitoring requirement. Without the daily detection query, the bypass goes undetected until a facility reports a credential mismatch.

---

## §13. Audit and Governance

### Audit log schema

Every agent action MUST produce one log entry with the following fields:

```json
{
  "timestamp": "ISO 8601 with UTC timezone — e.g. 2026-05-13T14:22:05.123Z",
  "agent_id": "string — fixed identifier for this agent module, e.g. 'ws1-intake-v1'",
  "action": "enum [MESSAGE_RECEIVED, MESSAGE_CLASSIFIED, FIELD_EXTRACTED, CONFIDENCE_GATE_APPLIED, COMPLETENESS_GATE_APPLIED, BRIEF_WRITTEN, HITL_ITEM_WRITTEN, BRIEF_ADVANCED_TO_WS2, BRIEF_CANCELLED, GOVERNANCE_HARD_STOP_TRIGGERED]",
  "entity_type": "string — 'MatchingBrief' or 'HITLQueueItem'",
  "entity_id": "UUID — sys_id of the entity created or modified by this action",
  "source_message_id": "string — ServiceNow sys_id of the inbound message being processed",
  "input_summary": {
    "message_type_classified": "enum value or null",
    "fields_extracted": ["list of field names attempted"],
    "confidence_scores": {"field_name": 0.0},
    "fields_below_threshold": ["list of field names scoring < 0.50"]
  },
  "output_summary": {
    "brief_status_written": "enum value or null",
    "missing_fields_written": ["list or empty array"],
    "hitl_gap_type": "enum value or null"
  },
  "delegation_tier": "enum [AGENT_ALONE, AGENT_LOGS, AGENT_PROPOSES, HUMAN_DECIDES]",
  "human_id": "UUID or null — set if a coordinator was involved in this action",
  "confidence_score": "float 0.0–1.0 or null — overall extraction confidence for FIELD_EXTRACTED actions",
  "escalation_triggered": "boolean — true if a HITLQueueItem was written as a result of this action",
  "compliance_flags": "array of strings — list any hard-rule violations detected (e.g. 'GOVERNANCE_HARD_STOP: specialty_required=UNRESOLVED blocked WS2 advance')"
}
```

### Retention periods

| Log type | Retention |
|----------|-----------|
| Compliance logs (any action with compliance_flags non-empty, or GOVERNANCE_HARD_STOP_TRIGGERED) | 7 years — HIPAA minimum for business associate records |
| Operational logs (all other actions) | 90 days |
| HITL resolution audit trail (HITLQueueItem lifecycle) | 2 years — sufficient for coordinator performance review and incident reconstruction |

### HITL checkpoints

| Checkpoint | Trigger condition | Notified party | Required response | SLA | If SLA breached |
|------------|-------------------|----------------|-------------------|-----|-----------------|
| Missing required field | Any required field confidence < 0.50; brief_status = NEEDS_COORDINATOR_INPUT | On-call coordinator | Complete the missing field(s) in the HITL review UI | 30 minutes | HITLQueueItem → EXPIRED; supervisor SMS alert; brief remains blocked |
| Unclassifiable message | facility_id not resolvable OR message_type = UNCLASSIFIABLE | On-call coordinator | Manually classify message type and create or confirm MatchingBrief | 30 minutes | EXPIRED; supervisor alert; message held in dead-letter |
| Implicit urgency confirmation | shift_datetime_start − now() ≤ 4 hours; urgency = IMPLICIT_URGENT | On-call coordinator | Confirm or deny queue pre-emption | 10 minutes | Auto-advance to EXPLICIT_URGENT and pre-empt; action logged in compliance_flags |
| Governance hard stop (WS2 blocked) | ADVANCED_TO_WS2 attempted with UNRESOLVED fields | Supervisor (not coordinator) | Investigate and resolve missing fields; confirm WS2 re-trigger | 15 minutes | Engineering on-call alert; incident log opened |

### Compliance constraints

| Regulatory framework | Specific requirement for this agent |
|----------------------|-------------------------------------|
| HIPAA (45 CFR §164) | MatchingBrief records and audit logs containing nurse identifiers (nurse_id, facility_id, shift details) are PHI-adjacent business associate records. All ServiceNow writes must occur over TLS 1.2+. Audit logs must be retained for 7 years. Access to audit logs must be role-restricted to compliance and supervisory roles — not all coordinators. |
| State licensing law (5-state region) | The facility_placement_state field on MatchingBrief (to be added — see D4b §14 A-6) must be accurately extracted and propagated to WS2 for HR-3 gate. An incorrect state in the MatchingBrief produces a compliant-looking brief that WS2 cannot catch — it will query nurses for the wrong state licence. This agent is the first point at which state is determined; extraction errors here bypass all downstream compliance gates. |
| CMS Conditions of Participation | Credential-to-facility-type matching (HR-2) is a CMS requirement for hospitals receiving Medicare/Medicaid funding. The WS1 agent does not enforce HR-2 directly (that is WS2's gate), but if WS1 misclassifies specialty_required (e.g., "ICU experienced" → RN_GENERAL instead of RN_ICU), the HR-2 gate in WS2 checks against the wrong specialty and passes a non-compliant match. Specialty extraction accuracy is therefore a CMS compliance dependency, not just a UX concern. |

---

## §14. Spec Ambiguity Register

| Item | Type | Confidence | Description | Impact if unresolved | Resolution |
|------|------|------------|-------------|----------------------|------------|
| A-1 | Unknown | Low | ServiceNow instance URL and environment (prod/staging) not confirmed in scenario | Builder cannot write integration contracts; placeholder URL used | Client to confirm: ServiceNow instance name and whether a sandbox exists for dev/test |
| A-2 | Unknown | Low | ServiceNow table names for inbound messages, matching briefs, and HITL queue are not stated in scenario or discovery transcript — names above are assumed | Builder creates wrong table integrations; migration cost if names change | Client IT/ServiceNow admin to confirm table schema and API names before build sprint 1 |
| A-3 | Unknown | Medium | ServiceNow API rate limits not confirmed; 60 req/min used as conservative default | If actual limit is lower (e.g., 10 req/min), polling frequency must be reduced, increasing intake latency | Client to provide ServiceNow API rate limit documentation or sandbox test |
| A-4 | Design gap | Medium | No webhook from ServiceNow to agent confirmed; polling assumed — adds 0–10 second latency per message | For EXPLICIT_URGENT messages, polling latency may delay intake; webhook would reduce to near-zero | Ask client IT: does the ServiceNow instance support outbound webhooks/business rules? If yes, replace polling with event-driven trigger |
| A-5 | Spec ambiguity | Medium | Specialty taxonomy reference list not defined in scenario — RN_ICU, RN_ED etc. are assumed canonical values | Builder hard-codes wrong enum values; extraction normalisation fails for real message text | Client to provide the specialty labels and synonyms actually used by coordinators and facility contacts |
| A-6 | Unknown | Low | Per-field extraction confidence threshold (0.70 for auto-accept, 0.50 for flagged-accept) is a design assumption, not a validated calibration | Thresholds set too high → excessive HITL volume; too low → bad briefs advance to WS2 | Pre-deployment: run agent on 200 historical inbound messages (if available), measure precision/recall per threshold, calibrate before go-live |
