# D4a — Capability Spec: Intake Agent (WS4)

**Status: FINAL**

---

## Purpose

The Intake Agent monitors incoming hospital shift requests via email, parses unstructured request content into a structured shift requirement, writes the record to the CRM, and triggers the Shift Matching Agent (WS1). Its value is eliminating the manual copy-paste step coordinators perform today: receiving a multi-channel, unstructured request, extracting the required fields, and routing it into the matching pipeline without human intervention on the routine path.

---

## Scope

**In scope:**
- Inbound email parsing — new shift requests, cancellations, modifications, clarification responses
- CRM record creation and update
- Hospital acknowledgement email (conditional — see Configuration)
- Clarification request email when required fields are missing
- WS1 handoff trigger on intake completion
- Duplicate request detection

**Out of scope:**
- Phone intake — real-time phone channel requires transcription and CRM integration unconfirmed in MVP; coordinator-owned
- Portal intake — hospital portal submissions route directly into the CRM; no agent parsing required if portal produces structured records (confirm with Aaron)
- Urgent request priority routing — WS1 processes all requests on a single queue in MVP
- Cancellation completion — agent detects and flags; coordinator owns nurse notification and CRM finalisation (D3)
- Modification completion — agent detects and flags; coordinator owns review and update (D3)

---

## KPIs

These are process quality targets for WS4 specifically. The business KPIs (fill time, autonomous match rate) are owned by WS1; WS4 enables them.

| Metric | Target | Measured by |
|---|---|---|
| Intake parsing accuracy — complete requests | 100% of required fields correctly extracted | Phase 1 accuracy test — D7 |
| Acknowledgement latency | Hospital acknowledgement sent within 60 seconds of request receipt | Agent outbound email timestamp vs. inbound receipt timestamp |
| Incomplete record rate | 0% — agent must not write a CRM record with missing required fields; clarification loop must trigger before write | Phase 1 accuracy test — D7 |
| WS1 handoff integrity | WS1 picks up every completed intake record with all required fields intact; 0 field-schema mismatches | Phase 1 handoff integrity test — D7 |
| Clarification resolution rate | ≥ 80% of clarification requests result in a complete record before `CLARIFICATION_TIMEOUT_MINUTES` | Phase 2 pilot measurement |

---

## Autonomy Matrix

Grounded in CLM WS4: steps 5–10 are fully delegatable once parsing is complete. Step 4 (phone intake) is coordinator-owned and out of scope. Cancellation and modification handling are human-retained per D3.

Delegation levels: **AUTONOMOUS** = agent acts without coordinator review; **ESCALATED** = agent acts then routes to coordinator queue for follow-up; **HUMAN-RETAINED** = no agent action, coordinator owns entirely.

| Condition | Delegation level | Agent action | Human action |
|---|---|---|---|
| Complete, well-formed email request received | AUTONOMOUS | Parse all fields; write CRM record; set status `INTAKE_COMPLETE`; send acknowledgement (if in scope); trigger WS1 | None — routine path |
| Incomplete request (one or more required fields missing) | AUTONOMOUS | Send clarification email to hospital; set CRM status `CLARIFICATION_PENDING`; do not write incomplete record; do not trigger WS1 | None — agent handles clarification loop |
| Clarification response received; request now complete | AUTONOMOUS | Update CRM record with missing fields; set status `INTAKE_COMPLETE`; trigger WS1 | None |
| Clarification timeout exceeded (`CLARIFICATION_TIMEOUT_MINUTES` with no hospital response) | ESCALATED | Set CRM status `CLARIFICATION_TIMEOUT`; route to coordinator queue | Coordinator contacts hospital directly to obtain missing fields — SLA: 2 business hours |
| Hospital not found in CRM directory | ESCALATED | Set CRM status `UNKNOWN_HOSPITAL`; route to coordinator queue | Coordinator links inbound email to existing hospital record or creates a new one — SLA: 2 business hours |
| Ambiguous specialty description (non-standard language, e.g. "ICU-level cover") | AUTONOMOUS (MAPPED) / ESCALATED (UNMAPPABLE) | Select the CRM specialty code whose description has the highest semantic similarity to the input text; set `specialty_confidence = MAPPED`; write CRM record with confidence flag visible to coordinator; add non-blocking notification to coordinator queue flagging the mapped specialty and the original input text; trigger WS1 — WS1 surfaces partial match risk at shortlist stage. If no CRM specialty code reaches similarity above `SPECIALTY_MAPPING_THRESHOLD`, set `specialty_confidence = UNMAPPABLE`; route to coordinator queue; do not trigger WS1 | Coordinator reviews CRM flag and original input text; can correct the specialty before WS1 completes matching if the mapping is wrong — SLA: before WS1 shortlist is confirmed |
| Request identified as cancellation | ESCALATED | Set CRM status `CANCELLATION_PENDING`; route to coordinator queue | Coordinator notifies nurse if already contacted; finalises CRM record — SLA: 30 minutes (nurse may already be en route) |
| Request identified as modification to existing open record | ESCALATED | Set CRM status `MODIFICATION_PENDING`; route to coordinator queue | Coordinator reviews modification and updates matching parameters — SLA: 2 business hours |
| LLM returns `request_type = AMBIGUOUS` (agent cannot determine whether email is new request, cancellation, or modification) | ESCALATED | Set CRM status `TYPE_AMBIGUOUS`; route to coordinator queue with parsed fields and `ambiguity_notes` from LLM output; do not trigger WS1 | Coordinator determines request type and completes intake manually — SLA: 2 business hours |
| Email body exceeds 2,000-token ceiling | ESCALATED | Truncate body to first 2,000 tokens; do not attempt parsing; set CRM status `TYPE_AMBIGUOUS`; route to coordinator queue with note "email body exceeded parsing limit — manual intake required"; log `action_type = TRUNCATION_ESCALATED` to audit trail | Coordinator performs manual intake — SLA: 2 business hours |
| Duplicate request detected (same `hospital_id`, same `shift_date`, and the incoming request's `shift_start_time` is within ±30 minutes of an existing open record's `shift_start_time`, and the inbound email's `received_at` is within 60 minutes of the existing record's `created_at`) | AUTONOMOUS | Link second request to existing CRM record; do not create new; add note to CRM record flagging the duplicate submission; alert coordinator | None — alert is informational, no action required unless coordinator identifies false positive |
| Phone intake | HUMAN-RETAINED | No agent action | Coordinator takes call; manually creates CRM record |
| Hospital responds to clarification email via phone call instead of email reply | HUMAN-RETAINED | WS4 cannot receive or parse a phone response; `CLARIFICATION_PENDING` record remains open; coordinator is notified when the hospital calls | Coordinator takes the call; manually completes the missing fields in the CRM record; transitions status to `INTAKE_COMPLETE` to trigger WS1 — SLA: same as `CLARIFICATION_TIMEOUT` (2 business hours) |

### Escalation SLAs

| Queue item type | Coordinator SLA | Rationale |
|---|---|---|
| `CANCELLATION_PENDING` | 30 minutes | Nurse may already be en route; delay causes a live scheduling conflict |
| `UNKNOWN_HOSPITAL` | 2 business hours | New hospital onboarding required; does not block other requests |
| `UNMAPPABLE` specialty | 2 business hours | WS1 is blocked until specialty is resolved; affects fill time KPI |
| `CLARIFICATION_TIMEOUT` | 2 business hours | Hospital has already been unresponsive; coordinator follow-up resumes the loop |
| `MODIFICATION_PENDING` | 2 business hours | Existing match may be in progress; modification review is time-sensitive |
| `TYPE_AMBIGUOUS` | 2 business hours | Agent cannot determine intent; intake is stalled until resolved |
| `TYPE_AMBIGUOUS` (token ceiling) | 2 business hours | Email body exceeded 2,000-token ceiling; agent does not attempt parsing; coordinator queue item includes note "email body exceeded parsing limit — manual intake required" and `action_type = TRUNCATION_ESCALATED` in audit log |

SLA values are v1 defaults — to be confirmed with Kim in pilot design.

### Override Mechanism

Coordinators can correct agent-set field values via the CRM portal for any record where WS1 has not yet confirmed a match (`INTAKE_COMPLETE` before `CONFIRMED`):

- **Specialty correction:** Coordinator updates `specialty_required` and `specialty_confidence` directly in the CRM record. WS1 re-reads the corrected values before confirming.
- **Escalation clearance:** Coordinator resolves escalated items (e.g. links unknown hospital, corrects specialty) via the coordinator queue UI; CRM status is then transitioned to `INTAKE_COMPLETE` by the coordinator action, re-triggering WS1.
- **Post-confirmation corrections** are out of scope for WS4 — handled through the modification workflow.

### Audit Trail — WS4 Action Log

Every autonomous and escalated action WS4 takes must produce an audit log entry. Required fields per entry:

| Field | Type | Description |
|---|---|---|
| `log_id` | UUID v4 | Unique identifier for this log entry |
| `crm_request_id` | UUID v4 | FK to the CRM shift request record |
| `action_type` | enum | `RECORD_CREATED` \| `CLARIFICATION_SENT` \| `CLARIFICATION_RESPONSE_MATCHED` \| `RECORD_UPDATED` \| `STATUS_CHANGED` \| `WS1_TRIGGERED` \| `ESCALATED` \| `ACK_SENT` \| `DUPLICATE_DETECTED` \| `TRUNCATION_ESCALATED` |
| `from_status` | string \| null | CRM status before the action; null for new record creation |
| `to_status` | string | CRM status after the action |
| `fields_written` | string[] | List of field names written in this action (omits PHI — raw email body never logged) |
| `agent_id` | string | WS4 agent instance identifier |
| `timestamp` | datetime | ISO 8601 UTC |
| `error_detail` | string \| null | Populated only for failed actions; null on success |

Audit log is append-only. No deletion permitted. **Default retention: 6 years from record creation date** (HIPAA minimum for healthcare business records — 45 CFR §164.530(j)). Builder must implement automated deletion at 6-year mark unless Linda confirms a longer period is required before deployment. Retention configuration must be a parameter, not hardcoded.

---

## Cross-Feature Interactions

| Scenario | Behaviour |
|---|---|
| Cancellation received while clarification is pending on the same request | Agent cancels the clarification loop; sets CRM status to `CANCELLATION_PENDING`; routes to coordinator queue. The pending clarification email is superseded — coordinator does not need to follow up on it. |
| Modification received while clarification is pending on the same request | Agent cancels the clarification loop; sets CRM status to `MODIFICATION_PENDING`; routes to coordinator queue with both the original incomplete record and the modification email. Coordinator resolves both simultaneously. |
| Modification received while WS1 is already matching (CRM status `INTAKE_COMPLETE`) | Agent sets CRM status to `MODIFICATION_PENDING`; routes to coordinator queue. Agent does not attempt to halt WS1 directly — WS1 checks CRM status before confirming autonomously; if status is no longer `INTAKE_COMPLETE`, WS1 escalates to coordinator queue. |
| Duplicate request received while clarification is pending on the original | Agent links the duplicate to the existing `CLARIFICATION_PENDING` record; does not create a new clarification loop; notifies coordinator that a duplicate arrived. |
| Acknowledgement email send fails after CRM write succeeds | CRM write and WS1 trigger are not rolled back. Acknowledgement failure is logged; coordinator is notified to send a manual acknowledgement if required. The intake record is complete regardless of acknowledgement status. |

---

## Shared Glossary — WS4→WS1 Handoff Payload

This glossary defines the fields WS4 writes to the CRM shift request record and WS1 reads as its input. **D4b must not redefine these fields independently.** If a field name or type needs to change, it changes here and D4b is updated to match.

| Field | Type | Constraints | Required | Description |
|---|---|---|---|---|
| `crm_request_id` | string | UUID v4; immutable; max 36 chars | Required | Primary key for the CRM shift request record. All downstream reads and writes by WS1 reference this ID. Set by CRM on record creation; read-only after creation. |
| `hospital_id` | string | UUID v4; max 36 chars; must exist in CRM hospital directory | Required | CRM record ID for the hospital client. FK to hospital directory; referential integrity enforced by CRM. If lookup fails, status set to `UNKNOWN_HOSPITAL`. |
| `specialty_required` | string | Max 50 chars; must be a value from the CRM specialty vocabulary; UPPERCASE (e.g. `ICU`, `ER`, `MEDSURG`, `OR`) | Required | Standardised specialty code. WS4 maps non-standard descriptions to this vocabulary using cosine similarity over `SPECIALTY_EMBEDDING_MODEL` embeddings. Algorithm: embed the input specialty text and each CRM vocabulary label; compute cosine similarity; select the label with the highest score. If score ≥ `SPECIALTY_MAPPING_THRESHOLD` → `MAPPED`. If input already exactly matches a vocabulary label (case-insensitive) → `EXACT`. If highest score < `SPECIALTY_MAPPING_THRESHOLD` → `UNMAPPABLE`. |
| `specialty_confidence` | enum | `EXACT` \| `MAPPED` \| `UNMAPPABLE`; SCREAMING_SNAKE_CASE | Required | `EXACT` = input matched CRM vocabulary label exactly (case-insensitive string match, no embedding required); `MAPPED` = cosine similarity score ≥ `SPECIALTY_MAPPING_THRESHOLD` but not exact; `UNMAPPABLE` = highest cosine similarity score < `SPECIALTY_MAPPING_THRESHOLD`. WS1 treats `MAPPED` as partial match risk. |
| `shift_date` | date | ISO 8601 (YYYY-MM-DD); must be ≥ today's date (UTC) | Required | Date of the shift. |
| `shift_start_time` | time | ISO 8601 (HH:MM); 24h; timezone = facility local time; must be stored with UTC offset | Required | Shift start time in facility local time with UTC offset. |
| `shift_end_time` | time | ISO 8601 (HH:MM); 24h; timezone = facility local time; must be stored with UTC offset; must be > `shift_start_time` on the same date | Required | Shift end time. Shifts crossing midnight: `shift_end_time` is on the following date. |
| `facility_location` | string | Max 200 chars; CRM location ID (UUID v4) if lookup succeeds; free-text facility name/address string if lookup fails | Required | Facility location. Lookup sequence: (1) attempt CRM location directory lookup by `facility_name` extracted from email; (2) if match found, write the UUID and set `facility_location_resolved = true`; (3) if no match, write the raw `facility_name` string and set `facility_location_resolved = false`. WS1 uses `facility_state` for credential filtering — `facility_location` is informational for WS1 but required for coordinator context. |
| `facility_location_resolved` | boolean | `true` if `facility_location` contains a CRM location UUID; `false` if it contains a raw free-text string | Required | Disambiguates the type of `facility_location` at read time. WS1 and coordinators must not attempt to dereference `facility_location` as a UUID when this flag is `false`. |
| `facility_state` | string | Exactly 2 chars; uppercase US state code (e.g. `IL`, `NY`); must be a state MedFlex operates in | Required | US state the facility is in. WS1 uses this for state-specific credential requirements. |
| `nurse_preference_named` | string \| null | Max 100 chars; null if no preference; read-only after set | Optional | Full name of a specifically requested nurse. Null if no nurse preference stated. |
| `intake_channel` | enum | `EMAIL` \| `PORTAL`; SCREAMING_SNAKE_CASE | Required | Channel the request arrived through. |
| `intake_timestamp` | datetime | ISO 8601 UTC (YYYY-MM-DDTHH:MM:SSZ); immutable; set by WS4 at status transition to `INTAKE_COMPLETE` | Required | T0 for fill time KPI measurement (<1h target). |
| `max_availability_age` | integer | Hours; valid range 1–168 (1h–7 days); passed from `MAX_AVAILABILITY_AGE` env var at intake time | Required | Availability staleness threshold passed to WS1 so it applies the same value without reading WS4 config. |
| `created_at` | datetime | ISO 8601 UTC; immutable; set by CRM on record creation | System | CRM record creation timestamp. Read-only. |
| `updated_at` | datetime | ISO 8601 UTC; updated by CRM on every write | System | Last CRM record update timestamp. Read-only. |

**Record provenance:** The CRM shift request record does not include a `created_by` field — the CRM sets `created_at` and `updated_at` automatically. Record provenance (which agent instance or coordinator created the record) is tracked exclusively in the WS4 Action Log via the `agent_id` field on each `RECORD_CREATED` entry. This is sufficient for audit purposes; a separate entity-level `created_by` field is not required.

**WS1 trigger mechanism:** WS4 triggers WS1 by setting the CRM shift request status to `INTAKE_COMPLETE`. WS1 polls or subscribes to this status change. The handoff is CRM-mediated — no direct agent-to-agent call.

### CRM Request Status State Machine

All valid statuses and transitions. Transitions not listed here are invalid and must be rejected by the CRM.

| From status | Event | To status | Owner |
|---|---|---|---|
| *(new record)* | WS4 receives complete request | `INTAKE_COMPLETE` | WS4 |
| *(new record)* | WS4 receives incomplete request | `CLARIFICATION_PENDING` | WS4 |
| *(new record)* | WS4 cannot identify hospital | `UNKNOWN_HOSPITAL` | WS4 |
| *(new record)* | WS4 cannot map specialty | `UNMAPPABLE` | WS4 |
| *(new record)* | WS4 identifies cancellation | `CANCELLATION_PENDING` | WS4 |
| *(new record)* | WS4 identifies modification | `MODIFICATION_PENDING` | WS4 |
| *(new record)* | WS4 cannot determine request type | `TYPE_AMBIGUOUS` | WS4 |
| *(new record)* | Email body exceeds 2,000-token ceiling | `TYPE_AMBIGUOUS` | WS4 |
| `CLARIFICATION_PENDING` | Hospital responds with complete data | `INTAKE_COMPLETE` | WS4 |
| `CLARIFICATION_PENDING` | Hospital responds but data is still incomplete (one or more required fields remain null) | `CLARIFICATION_PENDING` | WS4 (new clarification email sent for remaining missing fields only; timeout clock resets to `CLARIFICATION_TIMEOUT_MINUTES` from the time of this response; no cap on clarification rounds in v1) |
| `CLARIFICATION_PENDING` | Timeout (`CLARIFICATION_TIMEOUT_MINUTES`) | `CLARIFICATION_TIMEOUT` | WS4 |
| `CLARIFICATION_PENDING` | Cancellation received | `CANCELLATION_PENDING` | WS4 |
| `CLARIFICATION_PENDING` | Modification received | `MODIFICATION_PENDING` | WS4 |
| `INTAKE_COMPLETE` | Modification received while WS1 matching | `MODIFICATION_PENDING` | WS4 |
| `UNKNOWN_HOSPITAL` | Coordinator resolves hospital identity | `INTAKE_COMPLETE` | Coordinator |
| `UNMAPPABLE` | Coordinator corrects specialty | `INTAKE_COMPLETE` | Coordinator |
| `CLARIFICATION_TIMEOUT` | Coordinator contacts hospital and resolves | `INTAKE_COMPLETE` | Coordinator |
| `CANCELLATION_PENDING` | Coordinator finalises cancellation | `CANCELLED` | Coordinator |
| `MODIFICATION_PENDING` | Coordinator reviews and updates | `INTAKE_COMPLETE` | Coordinator |
| `TYPE_AMBIGUOUS` | Coordinator determines request type | `INTAKE_COMPLETE` \| `CANCELLATION_PENDING` \| `MODIFICATION_PENDING` | Coordinator |
| `INTAKE_COMPLETE` | WS1 confirms match | `CONFIRMED` | WS1 |
| `INTAKE_COMPLETE` | WS1 exhausts shortlist | `ESCALATED` | WS1 |

---

## Integration Contracts

Each integration carries a named assumption. If the assumption proves wrong, the integration path changes as described.

Note on HTTP specifics: endpoint paths, authentication scheme, and exact field names below are provisional — Aaron must confirm all before implementation. Working default is REST/JSON. If the CRM uses a different protocol, this section is revised accordingly.

---

### Agent Startup Behavior

Execute the following steps in order on every agent start or restart before beginning the email polling loop:

1. **Load specialty vocabulary** — call `GET /specialties` (Contract 3). Cache all `{ code, label }` pairs in memory. Compute and cache embeddings for all labels using `SPECIALTY_EMBEDDING_MODEL`. If the call fails, abort startup and alert ops — the agent cannot perform specialty mapping without the vocabulary.
2. **Resume clarification timeouts** — query CRM for all records with status `CLARIFICATION_PENDING`: `GET /shift-requests?status=CLARIFICATION_PENDING`. For each record, compute remaining timeout as `CLARIFICATION_TIMEOUT_MINUTES` − elapsed minutes since `updated_at`. If elapsed ≥ `CLARIFICATION_TIMEOUT_MINUTES`, immediately transition that record to `CLARIFICATION_TIMEOUT` and route to coordinator queue. Otherwise, schedule the timeout timer for the remaining duration.
3. **Verify credentials** — confirm `EMAIL_PROVIDER_API_KEY`, `CRM_API_KEY`, and `LLM_API_KEY` are available from the secrets manager. If any credential is missing, abort startup and alert ops.
4. **Begin polling loop** — start polling for unread emails per Contract 1 at `EMAIL_POLL_INTERVAL_SECONDS` cadence.

**Crash recovery guarantee:** Because WS4 marks emails as read after processing (Contract 1) and because the duplicate detection logic covers the mark-as-read failure case, a restart after a crash does not produce duplicate CRM records. CLARIFICATION_PENDING timeouts are resumed from `updated_at`, not from zero — coordinators are not disadvantaged by a crash.

---

**Contract 1 — Email channel (inbound)**

- **Direction:** Read
- **Purpose:** Poll for incoming hospital shift request emails
- **Protocol:** Email provider REST API (Gmail API or Microsoft Graph — confirm provider with Aaron)
- **Poll interval:** Every 60 seconds (configurable via `EMAIL_POLL_INTERVAL_SECONDS` — add to Configuration if confirmed)
- **Request:** `GET /messages?filter=unread&folder=INTAKE_INBOX` — exact endpoint path TBD with Aaron
- **Authentication:** Bearer token via `EMAIL_PROVIDER_API_KEY`
- **Rate limit:** Gmail: 250 quota units/second (list = 5 units/call → ~50 polls/second headroom); Microsoft Graph: 10,000 requests/10 minutes. At 1 poll/minute, rate limits are not binding — monitor only if poll interval is reduced.
- **Expected response:** `200 OK` with list of message objects; each message contains `from`, `subject`, `body`, `received_at`, `message_id`
- **Timeout:** 10 seconds per poll request
- **Retry:** 3 attempts, exponential backoff (2s, 4s, 8s); on 3rd failure, alert ops and log missed poll window
- **Error handling:**

| HTTP status | Agent behaviour |
|---|---|
| `200` | Parse message list; process each unread message |
| `401` | Alert ops immediately — credential invalid or expired; pause polling |
| `429` | Honour `Retry-After` header; log rate limit hit |
| `5xx` | Retry with exponential backoff; alert ops if 3 consecutive failures |
| Timeout | Log timeout; retry immediately once; if second attempt times out, alert ops |

**Clarification response detection (mandatory pre-processing step — execute before treating any email as a new request):**

For every inbound email, before initiating a new intake, WS4 must check whether the email is a clarification response to an existing `CLARIFICATION_PENDING` record:

1. Extract `hospital_id` from the inbound email `from` address via CRM hospital directory lookup (Contract 3).
2. If lookup succeeds, query CRM for open `CLARIFICATION_PENDING` records with matching `hospital_id`: `GET /shift-requests?hospital_id={id}&status=CLARIFICATION_PENDING`.
3. Check `In-Reply-To` / `References` email headers against the `message_id` of the clarification email WS4 sent (stored in audit log with `action_type = CLARIFICATION_SENT`). If a header match is found, treat the email as a clarification response for that record — do not create a new intake.
4. If no thread header match but exactly one `CLARIFICATION_PENDING` record exists for the hospital, treat the email as a clarification response for that record and log the association decision.
5. If multiple `CLARIFICATION_PENDING` records exist for the hospital and no thread header match, route to coordinator queue with `action_type = ESCALATED` and note "multiple open clarification records — cannot determine which request this email resolves."
6. If no `CLARIFICATION_PENDING` record exists for the hospital, treat the email as a new intake request and proceed with full parsing.

**Audit log requirement:** Record the association decision (`CLARIFICATION_RESPONSE_MATCHED` or `NEW_INTAKE`) as an audit log entry before processing.

**Mark-as-read (idempotency gate — mandatory after processing each message):**

After processing a message (whether it results in a new CRM record, a clarification response, a duplicate link, or an escalation), WS4 must mark the email as read in the email provider to prevent re-processing on subsequent polls:

- **Request:** `PATCH /messages/{message_id}` — body: `{"read": true}`
- **When:** After the final CRM write or escalation for the message is confirmed (not before — if the agent crashes before marking as read, re-processing on restart is correct behaviour)
- **Failure handling:** If the mark-as-read call fails, log the failure with `message_id`; do not retry; ops alert. Coordinator manually marks as read if required. The CRM record is already written — the intake is not at risk; only re-processing risk exists.
- **Audit log:** Log `action_type = MESSAGE_PROCESSED` with `message_id` in the `fields_written` array on successful mark-as-read.

**Restart / re-processing safety:** Because WS4 marks messages as read immediately after processing, a restart picks up only unread messages — previously processed messages are not re-ingested. For messages where mark-as-read failed before crash, the duplicate detection logic (same `hospital_id`, `shift_date`, `shift_start_time`) prevents a duplicate CRM record from being created.

- **If CRM email integration is confirmed by Aaron** → this contract is removed; agent reads via CRM only (ADR-1 Option A)
- **Working default:** ADR-1 Option C (hybrid): direct email API + CRM write API

---

**Contract 2 — Internal CRM (write — shift request record)**

- **Direction:** Write
- **Purpose:** Create structured shift request record; update status; trigger WS1 handoff
- **Protocol:** REST/JSON
- **Base URL:** `CRM_API_BASE_URL`
- **Authentication:** Bearer token via `CRM_API_KEY`
- **Create record:** `POST /shift-requests` — body is the Shared Glossary payload (all required fields)
- **Update status:** `PATCH /shift-requests/{crm_request_id}` — body is `{"status": "<NEW_STATUS>"}`
- **Update fields:** `PATCH /shift-requests/{crm_request_id}` — body is the subset of fields being updated
- **Expected response:** `201 Created` (record creation) or `200 OK` (update); response body contains `crm_request_id` and `created_at`
- **Rate limit:** Confirm with Aaron — CRM API rate limits unknown. Working assumption: 60 write requests/minute. If MedFlex intake volume exceeds 1 request/second sustained, confirm higher tier with Aaron before deployment.
- **Timeout:** 5 seconds per request
- **Retry:** 3 attempts, exponential backoff (1s, 2s, 4s); on 3rd failure, queue record locally and alert ops — do not drop
- **Error handling:**

| HTTP status | Agent behaviour |
|---|---|
| `201` / `200` | Proceed; log action to audit trail |
| `400` | Log full request payload (minus PHI); alert ops — indicates spec field mismatch; do not retry |
| `401` | Alert ops immediately — credential invalid; pause CRM writes |
| `404` (on PATCH) | Log error; alert ops — `crm_request_id` not found; may indicate a race condition |
| `409` (duplicate) | Treat as duplicate detection; link records; alert coordinator |
| `429` | Honour `Retry-After`; queue write; retry when permitted |
| `5xx` | Queue locally; retry with backoff; alert ops if 3 consecutive failures |

- **Data mapping — email fields to Shared Glossary fields:**

| Source (parsed from email) | Shared Glossary field | Transformation |
|---|---|---|
| Specialty text (free text) | `specialty_required` | Semantic similarity mapping to CRM vocabulary; `specialty_confidence` set based on match score vs. `SPECIALTY_MAPPING_THRESHOLD` |
| Date expression (e.g. "next Tuesday") | `shift_date` | Resolved to `YYYY-MM-DD` relative to email `received_at` UTC date |
| Time expression (e.g. "07:00–19:00") | `shift_start_time`, `shift_end_time` | Parsed to `HH:MM`; stored with facility UTC offset |
| Hospital name or email domain | `hospital_id` | CRM hospital directory lookup; if no match → `UNKNOWN_HOSPITAL` |
| Facility name (from LLM parse) | `facility_location`, `facility_location_resolved` | CRM location directory lookup by facility name; if UUID match → write UUID + `resolved = true`; if no match → write raw string + `resolved = false` |
| State reference (e.g. "Chicago IL") | `facility_state` | Extracted 2-char state code; validated against MedFlex operating states |
| Nurse name if present | `nurse_preference_named` | Extracted as-is; null if absent |
| Email provider metadata | `intake_channel` | Always `EMAIL` for this integration |
| Intake completion time | `intake_timestamp` | Set to ISO 8601 UTC at status transition to `INTAKE_COMPLETE` |

- **Assumption:** CRM exposes a write API. Confidence: medium — not confirmed as CRM API specifically. Confirm with Aaron. If no CRM write API exists → intake automation value collapses; full architecture replanning required.
- **Assumption:** Hospital clients have a directory record in the CRM. Confidence: medium — implied by existing CRM lifecycle tracking; not directly confirmed. If directory does not exist, agent falls back to coordinator tagging.

---

**Contract 3 — Internal CRM (read — hospital directory and request lifecycle)**

- **Direction:** Read
- **Purpose:** Hospital lookup for record linking; duplicate detection; specialty vocabulary retrieval
- **Protocol:** REST/JSON
- **Hospital lookup:** `GET /hospitals?email_domain={domain}` or `GET /hospitals/{hospital_id}` — exact lookup key TBD with Aaron

  **Expected response (hospital lookup — `200 OK`):**
  ```json
  {
    "hospital_id": "string (UUID v4)",
    "name": "string",
    "email_domain": "string",
    "contact_email": "string | null",
    "location_ids": ["string (UUID v4)", "..."]
  }
  ```
  WS4 reads `hospital_id` from this response and writes it to the Shared Glossary field `hospital_id`. If `contact_email` is present and non-null, it is used as the clarification reply-to address (fallback for A-WS4-8). Full response schema TBD with Aaron — builder must treat unlisted fields as ignorable extras.

- **Existing request lookup (duplicate detection):** `GET /shift-requests?hospital_id={id}&shift_date={date}&status=INTAKE_COMPLETE,CLARIFICATION_PENDING,UNKNOWN_HOSPITAL,UNMAPPABLE,TYPE_AMBIGUOUS,MODIFICATION_PENDING` — returns all open records for deduplication check. **Open record definition:** any record where coordinator or WS1 action is still pending; `CANCELLED`, `CONFIRMED`, `ESCALATED` records are closed and excluded from duplicate detection.

  **Expected response (request lookup — `200 OK`):**
  ```json
  {
    "shift_requests": [
      {
        "crm_request_id": "string (UUID v4)",
        "hospital_id": "string (UUID v4)",
        "shift_date": "YYYY-MM-DD",
        "shift_start_time": "HH:MM",
        "status": "string",
        "created_at": "ISO 8601 UTC"
      }
    ]
  }
  ```

- **Specialty vocabulary lookup:** `GET /specialties` — returns the full list of CRM specialty vocabulary labels for embedding. WS4 fetches this on startup and caches the result (see Agent Startup Behavior). Refresh when cache TTL expires or on specialty mapping failure that seems vocabulary-related.

  **Expected response (specialty vocabulary — `200 OK`):**
  ```json
  {
    "specialties": [
      { "code": "ICU", "label": "Intensive Care Unit" },
      { "code": "ER", "label": "Emergency Room" },
      { "code": "MEDSURG", "label": "Medical-Surgical" },
      { "code": "OR", "label": "Operating Room" }
    ]
  }
  ```
  WS4 uses the `code` field as the `specialty_required` value written to the CRM record. The `label` field is embedded for semantic similarity matching. Full vocabulary list TBD with Aaron — builder must not hardcode specialty codes; always read from `GET /specialties` at startup.

- **Expected response (generic):** `200 OK` with record(s); `404` if no match
- **Rate limit:** Same as Contract 2 — confirm with Aaron. 3 read requests per intake (hospital lookup + duplicate check + optional specialty vocabulary — vocabulary is cached so only 1 cold-start call). Rate limits not expected to bind.
- **Timeout:** 5 seconds
- **Retry:** 2 attempts, exponential backoff (1s, 2s); on failure, route to coordinator queue rather than block intake
- **Error handling:**

| HTTP status | Agent behaviour |
|---|---|
| `200` | Use returned record |
| `404` | Hospital not found → set status `UNKNOWN_HOSPITAL`; escalate. Specialty not found → alert ops; do not attempt mapping with empty vocabulary |
| `5xx` | Retry once; on second failure, route to coordinator queue |

- **Assumption:** CRM has a request lifecycle status model with defined statuses. Exact status values unknown. Confirm status schema with Aaron before parsing logic is built.
- **Assumption:** CRM exposes a `GET /specialties` endpoint returning the complete specialty vocabulary. Confidence: low — not confirmed in discovery. If no endpoint exists, the specialty vocabulary must be provided as a configuration value (`SPECIALTY_VOCABULARY_JSON` env var containing the JSON array); confirm with Aaron which is available before implementation.

---

**Contract 4 — WS1 handoff (CRM-mediated)**

- **Direction:** Write (status change)
- **Purpose:** Trigger WS1 to begin shift matching
- **Mechanism:** `PATCH /shift-requests/{crm_request_id}` with `{"status": "INTAKE_COMPLETE"}` — no direct agent-to-agent call
- **WS1 trigger:** WS1 polls or subscribes to CRM status changes on `INTAKE_COMPLETE`; WS4 does not call WS1 directly
- **Payload:** All Shared Glossary fields must already be written to the CRM record before status is set to `INTAKE_COMPLETE`; WS1 reads from CRM on trigger
- **Required step order (mandatory — do not reorder):**
  1. Write all Shared Glossary fields to CRM record via Contract 2 `POST /shift-requests`
  2. Send acknowledgement email via Contract 5 (if `ACKNOWLEDGEMENT_SENDER_ADDRESS` is configured) — ACK failure does not block step 3; log failure and proceed
  3. Set CRM status to `INTAKE_COMPLETE` via Contract 4 `PATCH` — this is the WS1 trigger; executing this before step 1 is complete would trigger WS1 against an incomplete record
- **Error handling:** Same as Contract 2 PATCH error table above

---

**Contract 5 — Outbound email (acknowledgement and clarification)**

- **Direction:** Write
- **Purpose:** Send acknowledgement to hospital on intake completion; send clarification request when required fields are missing
- **Protocol:** Email provider send API (same provider as Contract 1 — Gmail API or Microsoft Graph)
- **Request:** `POST /messages/send` — body contains `to`, `subject`, `body`, `thread_id` (for replies)
- **Authentication:** Bearer token via `EMAIL_PROVIDER_API_KEY`
- **Rate limit:** Gmail: 100 send requests/100 seconds/user; Microsoft Graph: 10,000 requests/10 minutes. Maximum 2 outbound emails per intake (1 acknowledgement + 1 clarification). Rate limits are not expected to bind at MedFlex intake volume; monitor in pilot.
- **Timeout:** 10 seconds
- **Retry:** 2 attempts; on failure, log and notify coordinator — do not block CRM write or WS1 trigger
- **Acknowledgement scope:** Conditional — only sent if `ACKNOWLEDGEMENT_SENDER_ADDRESS` is configured and Kim confirms this is in v1 scope
- **Clarification email:** Reply to the originating hospital thread (`thread_id` from inbound message); hospital contact email is the `from` address of the original email
- **PHI constraint:** Outbound email body must contain only shift logistics fields (date, time, specialty, facility) — no patient names, no clinical context, no raw email content

**Email templates (exact content — not illustrative):**

*Acknowledgement email:*
```
Subject: Shift Request Received — [specialty_required], [shift_date], [facility_location]

We have received your shift request and are processing it now.

Request details:
  Specialty: [specialty_required]
  Date: [shift_date]
  Time: [shift_start_time] – [shift_end_time]
  Facility: [facility_location]

You will receive a confirmation once a nurse has been matched. If you need to make changes, reply to this email.
```

*Clarification email — one message listing all missing fields:*
```
Subject: Additional Information Needed — Shift Request [shift_date], [facility_location or "your facility"]

Thank you for your shift request. To complete your intake, please reply with the following:

[INCLUDE ONLY THE LINES FOR MISSING FIELDS:]
  • Specialty required (e.g. ICU, ER, MedSurg)
  • Shift date (YYYY-MM-DD)
  • Shift start time (HH:MM, 24-hour)
  • Shift end time (HH:MM, 24-hour)
  • Facility state (2-letter US state code, e.g. IL)

Once we have this information, we will process your request immediately.
```

Template substitution rules:
- `[specialty_required]` — use parsed value if `EXACT` or `MAPPED`; use "the specialty required" (literal) if `UNMAPPABLE` or not parsed
- `[shift_date]` — ISO 8601 date; if not parsed, use "the shift date" (literal)
- `[facility_location]` — use CRM location name if UUID resolved; otherwise use free-text value; if not parsed, use "your facility"
- Missing-fields list: include only the bullet for each field that failed extraction; omit fields that were successfully parsed
- No conditional logic beyond field presence — do not include patient names, clinical context, or any text from the original email body

- **Error handling:**

| HTTP status | Agent behaviour |
|---|---|
| `200` / `202` | Log sent; proceed |
| `400` | Log error; alert ops — indicates malformed request |
| `401` | Alert ops immediately — credential invalid |
| `5xx` | Retry once; on failure, log and notify coordinator for manual send |

---

**Contract 6 — LLM email parsing (OpenAI API)**

- **Direction:** Write (API call to OpenAI)
- **Purpose:** Extract structured shift request fields from unstructured inbound hospital email body; classify request type (new request / cancellation / modification)
- **Parsing endpoint:** OpenAI Chat Completions API — `POST https://api.openai.com/v1/chat/completions`; model: `PARSING_LLM_MODEL` (default: `gpt-4o-mini`)
- **Embedding endpoint:** OpenAI Embeddings API — `POST https://api.openai.com/v1/embeddings`; model: `SPECIALTY_EMBEDDING_MODEL` (default: `text-embedding-3-small`); used for specialty mapping only, not for email parsing
- **Authentication:** Bearer token via `LLM_API_KEY` (same key for both endpoints)
- **Rate limit:** OpenAI tier 1 default: 500 requests/minute, 200,000 tokens/minute. Monitor token usage in pilot; upgrade tier if intake volume requires.
- **Timeout:** 15 seconds
- **Retry:** 2 attempts on timeout or `5xx`; on third failure, route to coordinator queue — do not drop
- **Token ceiling:** If email body exceeds 2,000 tokens, truncate to first 2,000 tokens and flag for coordinator review (see Failure Modes)

**System prompt (exact — do not modify without re-testing):**
```
You are an intake parser for a healthcare staffing agency. Extract structured fields from the hospital email below.

Return a JSON object with exactly these fields. Use null for any field you cannot extract with confidence.

{
  "request_type": "NEW_REQUEST" | "CANCELLATION" | "MODIFICATION" | "AMBIGUOUS",
  "specialty_text": string | null,          // raw specialty description as written; do not normalise
  "shift_date": "YYYY-MM-DD" | null,        // resolve relative dates using received_at date provided
  "shift_start_time": "HH:MM" | null,       // 24-hour format
  "shift_end_time": "HH:MM" | null,         // 24-hour format
  "facility_name": string | null,           // facility name as written; do not look up
  "facility_state": "XX" | null,            // 2-letter US state code; null if not mentioned
  "nurse_preference": string | null,        // nurse name if specifically requested; null otherwise
  "ambiguity_notes": string | null          // brief note on any field you were uncertain about
}

Rules:
- received_at date is provided in the user message as ISO 8601 UTC. Resolve "today", "tomorrow", "next Tuesday" relative to this date.
- "Morning shift" = 07:00–15:00; "afternoon shift" = 15:00–23:00; "night shift" = 23:00–07:00 (next day). Use these defaults only if no explicit times are given.
- If the email is ambiguous between request types, set request_type to AMBIGUOUS and explain in ambiguity_notes.
- Never include patient names, case numbers, or clinical details in any field.
- Return only the JSON object — no commentary.
```

**User message format:**
```
received_at: {ISO 8601 UTC datetime}

{email body}
```

**Output JSON schema (required fields — build validation against this):**

| Field | Type | Null allowed | Notes |
|---|---|---|---|
| `request_type` | `NEW_REQUEST` \| `CANCELLATION` \| `MODIFICATION` \| `AMBIGUOUS` | No | Drives routing in Autonomy Matrix |
| `specialty_text` | string | Yes | Raw text — WS4 runs embedding mapping separately |
| `shift_date` | `YYYY-MM-DD` string | Yes | Builder must validate format and ≥ today |
| `shift_start_time` | `HH:MM` string | Yes | 24-hour; may use shift-name defaults (see prompt) |
| `shift_end_time` | `HH:MM` string | Yes | 24-hour; must be > start on same or next day |
| `facility_name` | string | Yes | Used for CRM hospital lookup (Contract 3) |
| `facility_state` | `XX` string | Yes | 2-char uppercase; validate against MedFlex operating states |
| `nurse_preference` | string | Yes | Null if absent |
| `ambiguity_notes` | string | Yes | Log to audit trail; do not write to CRM |

**Post-parse validation (WS4 owns — not LLM):**
- Any required Shared Glossary field still null after parsing → trigger clarification loop (Contract 5)
- `facility_state` not in MedFlex operating state list → escalate to coordinator queue
- `shift_date` < today UTC → reject; route to coordinator queue with note "shift date in the past"
- `shift_end_time` ≤ `shift_start_time` on same date and not a midnight-crossing pattern → route to coordinator queue with note "invalid shift window"

**Specialty mapping (separate from parsing LLM call):**
After extracting `specialty_text`, WS4 runs the embedding-based mapping step:
1. Embed `specialty_text` using `SPECIALTY_EMBEDDING_MODEL`
2. Embed all CRM specialty vocabulary labels (cache embeddings; refresh when vocabulary changes)
3. Compute cosine similarity between `specialty_text` embedding and each vocabulary label embedding
4. If `specialty_text` is a case-insensitive exact match to any vocabulary label → `specialty_confidence = EXACT`; set `specialty_required` to that label
5. If highest cosine similarity score ≥ `SPECIALTY_MAPPING_THRESHOLD` → `specialty_confidence = MAPPED`; set `specialty_required` to the highest-scoring label
6. If highest cosine similarity score < `SPECIALTY_MAPPING_THRESHOLD` → `specialty_confidence = UNMAPPABLE`; do not set `specialty_required`; route to coordinator queue

- **Error handling:**

| Response | Agent behaviour |
|---|---|
| Valid JSON, all required fields present | Proceed to post-parse validation |
| Valid JSON, required fields null | Trigger clarification loop for missing fields |
| Invalid JSON or missing `request_type` | Retry once with same prompt; on second failure, route to coordinator queue |
| `401` | Alert ops immediately — API key invalid |
| `429` | Honour `Retry-After`; queue email for retry; alert ops if queue exceeds 10 items |
| `5xx` or timeout | Retry twice; on third failure, route to coordinator queue; log full error |

---

## Escalation Triggers

| Trigger | Condition | Agent action | Coordinator action |
|---|---|---|---|
| Clarification timeout | Hospital has not responded within `CLARIFICATION_TIMEOUT_MINUTES` | Set CRM status `CLARIFICATION_TIMEOUT`; add to coordinator queue | Contact hospital directly to obtain missing fields |
| Unknown hospital | Inbound email cannot be matched to a CRM hospital record | Set CRM status `UNKNOWN_HOSPITAL`; add to coordinator queue | Link email to existing hospital or create new record |
| Cancellation received | Inbound email identified as a cancellation of an open shift request | Set CRM status `CANCELLATION_PENDING`; add to coordinator queue | Notify nurse if already contacted; finalise CRM |
| Modification received | Inbound email identified as a change to an existing open request | Set CRM status `MODIFICATION_PENDING`; add to coordinator queue | Review modification; update matching parameters |
| Ambiguous request type | Agent cannot determine whether email is new request, cancellation, or modification after parsing | Set CRM status `TYPE_AMBIGUOUS`; add to coordinator queue | Determine request type; complete intake manually |

---

## Coordinator Queue

**Technical definition:** The coordinator queue is implemented as a CRM filtered view — there is no separate queue system. WS4 routes to the coordinator queue by writing a structured CRM queue record and updating the shift request status; coordinators see all open items in their CRM dashboard filtered by `assignee = COORDINATOR_QUEUE`.

**Queue record:** When WS4 escalates, it creates a CRM queue record via `POST /coordinator-queue-items` — confirm endpoint with Aaron. Required fields:

| Field | Type | Description |
|---|---|---|
| `queue_item_id` | UUID v4 | Primary key |
| `crm_request_id` | UUID v4 | FK to the shift request record being escalated |
| `reason_code` | enum | `CANCELLATION_PENDING` \| `UNKNOWN_HOSPITAL` \| `UNMAPPABLE` \| `CLARIFICATION_TIMEOUT` \| `MODIFICATION_PENDING` \| `TYPE_AMBIGUOUS` \| `TRUNCATION_ESCALATED` \| `MULTI_CLARIFICATION_CONFLICT` — matches the CRM request status that triggered escalation |
| `note` | string | Human-readable context for the coordinator (e.g., "email body exceeded parsing limit — manual intake required"); max 500 chars |
| `sla_deadline` | datetime | ISO 8601 UTC; set to `created_at` + SLA from Escalation SLAs table |
| `created_at` | datetime | ISO 8601 UTC; set by CRM on creation |
| `resolved_at` | datetime \| null | Set by coordinator on resolution; null until resolved |

**Coordinator action to resolve:** Coordinator resolves via the CRM queue UI by updating the relevant shift request fields and transitioning the CRM request status to `INTAKE_COMPLETE` (or appropriate terminal status). The queue item `resolved_at` is set by the coordinator action. WS4 does not poll the coordinator queue — WS1 is re-triggered by the CRM status change, not by WS4.

**Fallback if CRM coordinator queue API is unavailable:** Log the queue item locally (same schema as above); alert ops; attempt resubmission every 60 seconds until the CRM API recovers. Do not drop escalation items.

**Assumption:** CRM exposes a coordinator queue write API at a `/coordinator-queue-items` endpoint. Confidence: medium — coordinator queue UI was referenced in discovery but API access not confirmed. Confirm endpoint and field schema with Aaron. If no API exists → WS4 sends an email alert to coordinator instead (lower fidelity; fallback only).

---

## Failure Modes

| Failure | Agent behaviour | Recovery |
|---|---|---|
| Email provider API unavailable | Alert ops immediately; do not silently miss inbound requests; retry per exponential backoff; log all missed poll windows | Ops investigates API status; coordinator manual intake fallback activates if downtime exceeds 5 minutes (D7 Phase 3 SPOF threshold) |
| CRM write API unavailable | Queue the structured record locally; alert ops; do not drop the request; retry when API recovers | Ops investigates; agent flushes queue on API recovery; no silent data loss |
| Acknowledgement email send failure | Log the failure; continue with CRM write and WS1 trigger; do not block intake on acknowledgement failure | Ops notified; manual acknowledgement sent by coordinator if required |
| Duplicate detection false positive | Log the suspected duplicate with both record IDs; route to coordinator queue for confirmation | Coordinator confirms whether duplicate or new request; clears the flag |
| CRM hospital directory lookup returns no match | Do not guess; set status `UNKNOWN_HOSPITAL`; route to coordinator queue | Coordinator resolves hospital identity before intake proceeds |

---

## Compliance

**PHI handling (D2 regulatory constraint — HIPAA):**

Inbound hospital emails may contain protected health information — patient details, case references, or clinical context embedded in a shift request. WS4 must not propagate PHI beyond the structured CRM record.

- The agent extracts and writes only the Shared Glossary fields to the CRM record. Raw email body content is not written to the CRM, not stored in logs, and not passed to WS1.
- If the agent cannot extract required fields without retaining raw content, it must route to the coordinator queue rather than attempt partial extraction. PHI routing triggers: (a) the LLM parse output contains a patient name in any field (e.g. `specialty_text = "ICU nurse for John Smith post-op"`); (b) the email body contains a case number, diagnosis code, or patient identifier embedded in the shift description; (c) the `ambiguity_notes` field from the LLM parse references patient-specific clinical details. In all three cases: do not write the field value to the CRM; set `specialty_confidence = UNMAPPABLE`; route to coordinator queue with a flag indicating PHI detected; log the flag (not the content) to the audit trail.
- Outbound emails (acknowledgement, clarification request) contain only shift logistics fields — no patient details, no clinical context.
- Confirm PHI handling requirements and log retention policy with Linda (compliance) and Aaron (log destination) before WS4 is deployed. Linda owns the HIPAA audit requirement; Aaron confirms the log infrastructure.

---

## Worked Examples

### Example 1 — Complete email request (routine path)

**Input:** Hospital email — "We need an ICU nurse for Thursday 15 May, 07:00–19:00, City General, Chicago IL. Preferred nurse: Sarah M. if available."

**Agent steps:**
1. Parse: specialty = `ICU` (exact), date = `2026-05-15`, start = `07:00`, end = `19:00`, facility = `City General`, state = `IL`, nurse preference = `Sarah M.`
2. Look up hospital in CRM by email domain → match found: `hospital_id = H-0042`
3. Write CRM record with all Shared Glossary fields; set status `INTAKE_COMPLETE`
4. Send acknowledgement email to hospital within 60 seconds
5. Set `intake_timestamp`; trigger WS1 via status change

**Pass criterion:** CRM record contains all required fields; `specialty_confidence = EXACT`; acknowledgement sent within 60s; WS1 picks up record immediately.

---

### Example 2 — Incomplete email (clarification loop)

**Input:** Hospital email — "Need a nurse for next Tuesday morning, St. Luke's."

**Note on shift-name defaults:** The system prompt resolves "morning shift" to 07:00–15:00 when no explicit times are given. "Morning" in this email is treated as a shift-name default — `shift_start_time = 07:00`, `shift_end_time = 15:00` are resolved. Specialty and facility state remain unknown.

**Missing fields:** specialty, facility state.

**Agent steps:**
1. Parse: date = `2026-05-19` (resolved from "next Tuesday"), start time = `07:00` (resolved from "morning" default), end time = `15:00` (resolved from "morning" default), facility = `St. Luke's`, specialty = unknown, facility state = unknown
2. Identify missing required fields: `specialty_required`, `facility_state`
3. Set CRM status `CLARIFICATION_PENDING`; do not write incomplete record
4. Send clarification email with bullets for `specialty_required` and `facility_state` only (times are resolved and omitted from the clarification request)
5. Await response

**On response received — complete:** update CRM record with all missing fields; set status `INTAKE_COMPLETE`; trigger WS1.

**On response received — still incomplete (e.g., hospital provides specialty but omits facility state):** send a second clarification email listing only the still-missing field(s); status remains `CLARIFICATION_PENDING`; timeout clock resets. No cap on clarification rounds in v1.

**On timeout (`CLARIFICATION_TIMEOUT_MINUTES` exceeded with no response):** set status `CLARIFICATION_TIMEOUT`; route to coordinator queue.

**Pass criterion:** No incomplete CRM record created before clarification is resolved; clarification email sent immediately; WS1 not triggered until all required fields are present; subsequent partial responses send a narrower clarification (only remaining missing fields) rather than repeating the full list.

---

### Example 3 — Cancellation received

**Input:** Hospital email — "Please cancel the ICU shift request we sent yesterday for City General, 15 May."

**Agent steps:**
1. Parse: request type = cancellation; match to existing CRM record by hospital, date, and facility
2. Set CRM status `CANCELLATION_PENDING`
3. Route to coordinator queue; do not autonomously notify nurse or finalise CRM

**Pass criterion:** Agent does not complete cancellation autonomously; coordinator receives queue item; CRM status is `CANCELLATION_PENDING`, not `CANCELLED` — coordinator finalises.

---

### Example 4 — Modification to existing request

**Input:** Hospital email — "Can you change the ICU shift on 15 May at City General to start at 09:00 instead of 07:00?"

**Agent steps:**
1. Parse: request type = modification; match to existing CRM record (`crm_request_id` identified)
2. Set CRM status `MODIFICATION_PENDING`
3. Route to coordinator queue; do not auto-update the shift time or re-trigger WS1

**Pass criterion:** Agent does not autonomously update the CRM record or restart the matching process; coordinator receives queue item and reviews the modification.

---

### Example 5 — UNMAPPABLE specialty

**Input:** Hospital email — "We need Level 3 perioperative cover, City General, 15 May, 07:00–19:00, IL."

**Agent steps:**
1. Parse: specialty = "Level 3 perioperative cover" (non-standard); date, times, facility, state = valid
2. Run semantic similarity match against CRM specialty vocabulary — highest score is `OR` at 0.61, below `SPECIALTY_MAPPING_THRESHOLD` (0.75)
3. Set `specialty_confidence = UNMAPPABLE`; do not write CRM record to `INTAKE_COMPLETE`
4. Set CRM status `UNMAPPABLE`; route to coordinator queue with original email text and similarity scores
5. Do not trigger WS1

**Pass criterion:** No `INTAKE_COMPLETE` record is created; WS1 is not triggered; coordinator receives queue item with original specialty text attached; coordinator can correct specialty and transition to `INTAKE_COMPLETE`.

---

### Race Conditions and Concurrency

The following concurrency scenarios must be handled deterministically. Builder note: the agent must not assume messages arrive in strict sequence.

| Scenario | Correct behaviour | Incorrect behaviour |
|---|---|---|
| Two emails for the same hospital/shift arrive within 60 seconds of each other | First email creates the CRM record; second email is detected as duplicate (same `hospital_id`, `shift_date`, `shift_start_time` within 30 minutes of first) and linked to first record — no second record created | Creating two separate CRM records for the same shift; triggering WS1 twice |
| Clarification response and cancellation arrive simultaneously (within same poll window) | Agent processes cancellation first (cancellation supersedes clarification); sets status `CANCELLATION_PENDING`; routes to coordinator queue | Processing clarification response first, creating `INTAKE_COMPLETE` record, then failing to cancel |
| Modification email arrives while WS1 is mid-match (CRM status = `INTAKE_COMPLETE`) | Set CRM status `MODIFICATION_PENDING`; route to coordinator queue; WS1 detects status change before confirming and escalates to coordinator | Agent ignoring the modification because WS1 already picked up the record |
| Email provider poll returns the same message ID twice (API deduplication failure) | Agent deduplicates by `message_id` before processing; second occurrence is silently dropped after first is processed | Processing the same email twice, creating two CRM records |

---

### Additional Edge Cases (Null, Boundary, Ambiguous)

| Scenario | Correct behaviour |
|---|---|
| Email body is empty or contains no extractable text (e.g. blank body, image-only email) | LLM parse returns all fields null; agent does not attempt clarification on an empty body (no information to work from); set status `TYPE_AMBIGUOUS`; route to coordinator queue with note "email body unreadable or empty" |
| Date expression is unresolvable (e.g. "sometime next week", "ASAP", no date mentioned) | LLM parse returns `shift_date = null`; agent triggers clarification loop — `shift_date` is a required field; clarification email includes "Shift date (YYYY-MM-DD)" bullet |
| `SPECIALTY_MAPPING_THRESHOLD` boundary test — cosine similarity score is exactly 0.75 (equal to threshold) | `specialty_confidence = MAPPED` — the condition is ≥ threshold; a score exactly at the boundary is a pass, not a fail |
| Inbound email `from` address matches multiple hospital records in CRM directory | Set status `UNKNOWN_HOSPITAL`; route to coordinator queue with note listing all matched hospital record IDs; coordinator selects the correct one |

---

## Configuration

Configurable parameters that must be set before deployment. All values are environment variables — no hard-coded constants in agent logic.

| Parameter | Type | Default | Description | Source |
|---|---|---|---|---|
| `EMAIL_PROVIDER_API_URL` | string | — | Inbound email API endpoint (Gmail or Outlook). Confirm provider and API access with Aaron. | D4a integration contracts |
| `EMAIL_PROVIDER_API_KEY` | secret | — | Authentication credential for email provider API. Injected via secrets manager — never logged. | D4a integration contracts |
| `CRM_API_BASE_URL` | string | — | Base URL for CRM write API. Must match the value set in D4b — shared across both agents. | D3; D4a integration contracts |
| `CRM_API_KEY` | secret | — | Authentication credential for CRM API. Same credential as D4b — injected via secrets manager, never logged. | D3; D4a integration contracts |
| `ACKNOWLEDGEMENT_SENDER_ADDRESS` | string | — | Outbound email address used for hospital intake acknowledgements. Only required if Kim confirms acknowledgements are in v1 scope. | D4a integration contracts |
| `CLARIFICATION_TIMEOUT_MINUTES` | integer (minutes) | 60 | Time agent waits for hospital response to a clarification request before escalating to coordinator queue. | D7 Phase 1 edge cases |
| `MAX_AVAILABILITY_AGE` | integer (hours) | 24 | Shared with D4b. Passed through the WS1 handoff payload so WS1 applies the same availability staleness threshold. | D7 Phase 1; D4b configuration |
| `SPECIALTY_MAPPING_THRESHOLD` | float (0–1) | 0.75 | Minimum cosine similarity score required to map a non-standard specialty description to a CRM specialty code. Below this threshold, `specialty_confidence` is set to `UNMAPPABLE` and the record is routed to the coordinator queue. Boundary: score = 0.75 exactly counts as `MAPPED` (≥ threshold). | Shared Glossary; Autonomy Matrix ambiguous specialty path |
| `SPECIALTY_EMBEDDING_MODEL` | string | `text-embedding-3-small` | OpenAI embedding model used to compute cosine similarity scores for specialty mapping. Both the input specialty text and the CRM vocabulary labels are embedded using this model. Change requires re-evaluating `SPECIALTY_MAPPING_THRESHOLD` against a representative sample of hospital emails. | Contract 6 (LLM specialty mapping) |
| `PARSING_LLM_MODEL` | string | `gpt-4o-mini` | OpenAI model used for email body parsing (field extraction). Changing to a different model may alter date/time resolution behaviour — revalidate Example 2 and Example 5 test cases. | Contract 6 (LLM email parsing) |
| `LLM_API_KEY` | secret | — | Authentication credential for OpenAI API (used by Contract 6 for both email parsing and specialty mapping). Injected via secrets manager — never logged. | Contract 6 |
| `LLM_COST_ALERT_MULTIPLIER` | float | 3.0 | Circuit breaker: if the token cost of a single LLM parse call exceeds this multiple of the rolling median parse cost, log and alert ops. Default 3.0× — indicates an unusually long email body or retry loop. Ops can lower threshold in pilot if median cost is stable. | Economics circuit breakers |
| `EMAIL_POLL_COST_BUDGET_USD_PER_HOUR` | float | 1.0 | Circuit breaker: if email API poll cost (calculated from provider pricing and poll count) exceeds this value per hour, alert ops and recommend increasing `EMAIL_POLL_INTERVAL_SECONDS`. Default $1.00/hour — a conservative ceiling at 1-poll/minute cadence; adjust based on actual provider pricing confirmed with Aaron. | Economics circuit breakers |
| `CRM_WRITE_FAILURE_RATE_THRESHOLD` | float (0–1) | 0.10 | Circuit breaker: if CRM write API call failure rate exceeds this value over a 5-minute window, pause intake processing and alert ops. Default 10%. | Economics circuit breakers |

**Notes:**
- `CRM_API_BASE_URL` and `CRM_API_KEY` are shared with D4b. Configure once via shared environment, not per-agent.
- `ACKNOWLEDGEMENT_SENDER_ADDRESS` is only required if Kim confirms hospital acknowledgements are in v1 scope. If not, this parameter and the outbound acknowledgement integration are removed.
- Secret parameters (`EMAIL_PROVIDER_API_KEY`, `CRM_API_KEY`) must not appear in logs, CRM fields, or audit records under any condition.

---

## Economics

WS4 value case: each coordinator currently spends ~30 minutes per intake request on manual email reading, field extraction, and CRM data entry (CLM WS4 micro-tasks 5–10). At ~7 FTE coordinators and the current intake volume, this is the highest-volume repeatable cognitive task in the business. WS4 eliminates this per-intake cost on the routine path.

**Per-request cost classification:**

| Operation | Cost type | Notes |
|---|---|---|
| Email API poll | API call — fixed per poll interval | Charged per request regardless of whether new emails are present; optimise poll interval to reduce idle API calls |
| LLM call — email parsing | Token cost — per email | Main variable cost. Email bodies are short (typically 50–200 words); estimated 500–1,500 tokens per parse (input + output). Budget: confirm with ops |
| LLM call — specialty mapping | Token cost — per email with non-standard specialty | Semantic similarity comparison against CRM vocabulary; additional token cost per ambiguous email. Frequency unknown until pilot data available |
| CRM write | API call — per record | Confirm CRM API pricing with Aaron (may be per-call or included in licence) |
| CRM read (hospital lookup, duplicate check) | API call — per request | Two reads per intake; confirm pricing |
| Outbound email (acknowledgement + clarification) | API call — per send | Two emails max per intake on normal path |

**Circuit breakers:**

- If LLM parse cost per email exceeds `LLM_COST_ALERT_MULTIPLIER` × rolling median parse cost, log and alert ops — indicates an unusually long email body or repeated retry; investigate before continuing
- If email API poll cost per hour exceeds `EMAIL_POLL_COST_BUDGET_USD_PER_HOUR`, alert ops and recommend increasing `EMAIL_POLL_INTERVAL_SECONDS`; ops approves change
- If CRM write API call failure rate exceeds `CRM_WRITE_FAILURE_RATE_THRESHOLD` over a 5-minute window, pause intake processing and alert ops — avoids queuing thousands of failed records

**Token budget (email parsing LLM call):**

- Input prompt: system prompt (static, ~300 tokens) + email body (variable, ~200 tokens typical) = ~500 tokens per call
- Output: structured JSON extraction (~200 tokens typical)
- Ceiling: if email body exceeds 2,000 tokens (unusual), truncate to first 2,000 tokens and flag for coordinator review — do not attempt parsing of very long emails autonomously
- Token budget values are estimates; calibrate against actual email samples in pilot

**Economics alignment with D1/D3:**

WS4 enables WS1 (the primary value driver — fill time and coordinator capacity). WS4's own cost must be below the value of coordinator time saved per intake. If average coordinator intake time is 30 minutes at coordinator loaded cost, and LLM + API cost per email parse is under $0.05 (estimate), WS4 has a 300:1 cost-benefit ratio on the routine path. Cost-per-intake data to be confirmed in pilot.

---

## Governance

**Human-in-the-loop SLAs:**

Coordinator queue items require a response within the SLAs defined in the Autonomy Matrix Escalation SLAs table. If no coordinator response is received within SLA:

- `CANCELLATION_PENDING` beyond 30 minutes: ops escalation — potential live scheduling conflict
- All other queue item types beyond 2 business hours: supervisor notification; item remains in queue

**HITL oversight during pilot:**

During the Wave 1 pilot (D7 Phase 1), coordinator reviews every completed `INTAKE_COMPLETE` record within 4 business hours to verify parsing accuracy. This is the accuracy measurement mechanism for the 100% parsing accuracy KPI. Review overhead is expected to be low on the routine path; the review requirement is reduced or removed when accuracy is confirmed at ≥ 95% over 50+ records.

**Accountability boundaries:**

| Decision | Owner | Accountability |
|---|---|---|
| Agent decides specialty mapping is `EXACT` or `MAPPED` | WS4 agent | If wrong specialty is confirmed → coordinator corrects before WS1 confirmation |
| Agent triggers WS1 on `INTAKE_COMPLETE` | WS4 agent | Coordinator can halt WS1 by updating CRM status to `MODIFICATION_PENDING` before confirmation |
| Agent sends clarification email to hospital | WS4 agent | Coordinator can review outgoing email content in audit log |
| Coordinator resolves escalated item | Coordinator | Coordinator owns the outcome once item is in their queue |

**Deployment approval:**

WS4 must not be deployed to production without:
1. Aaron confirming CRM API access and hospital directory existence
2. Kim confirming (or ruling out) acknowledgement emails in v1 scope
3. Linda signing off on PHI handling log retention policy
4. D7 Wave 0 prerequisite checks passing (availability consolidation complete, CRM status schema confirmed)
5. Kim confirming coordinator pilot buy-in: coordinators understand the escalation workflow, know how to act on coordinator queue items, and have agreed the SLAs before Wave 1 goes live — D2 Risk: coordinator resistance is High likelihood / High impact; deploying without this confirmation risks coordinators routing around the agent, which prevents the KPIs from moving regardless of technical correctness

---

## Assumptions Register

All assumptions that shape this spec. If any assumption is wrong, the listed impact describes what changes.

| ID | Claim | Confidence | Test via | Impact if wrong |
|---|---|---|---|---|
| A-WS4-1 | Email channel is not CRM-integrated — coordinators manually copy intake data from email into the CRM portal today; agent must read via direct email provider API | Medium — Marcus Reyes: *"I am not sure about that, to be honest."* (discovery session) | Aaron | If CRM email integration confirmed → email provider API (Contracts 1 and 5) removed; agent reads via CRM only (ADR-1 Option A) |
| A-WS4-2 | CRM exposes a write API for shift request record creation and status updates | Medium — Marcus: *"I think there is an API somewhere"*; not confirmed as CRM write API | Aaron | If no CRM write API → intake automation collapses; full architecture replanning required |
| A-WS4-3 | Hospital clients have a directory record in the CRM (name, location, email domain, contact details) | Medium — implied by existing CRM lifecycle tracking; not directly confirmed | Aaron | If no hospital directory → agent cannot link inbound emails to client records; `UNKNOWN_HOSPITAL` path becomes default for all new emails; coordinator tagging required |
| A-WS4-4 | CRM has a request lifecycle status model with defined status values | Medium — status model confirmed to exist in discovery; exact status names unknown | Aaron | If status values differ from spec → all state machine transitions require updating before deployment |
| A-WS4-5 | Email provider API (Gmail or Outlook) is accessible with API credentials obtainable before deployment | Unknown — provider not named in discovery | Aaron | If API access not available → email intake requires coordinator manual trigger; WS4 partial value only |
| A-WS4-6 | Coordinators do not currently send acknowledgement emails to hospitals on request receipt — this is a new design-target behaviour | Low — inferred from absence of mention in discovery | Kim | If Kim confirms acknowledgements are already standard → `ACKNOWLEDGEMENT_SENDER_ADDRESS` is a behaviour WS4 replaces (lower risk); if not in v1 scope → outbound acknowledgement integration removed |
| A-WS4-7 | Hospital portal submissions route directly into the CRM as structured records — no agent parsing required for portal channel | Medium — portal confirmed to exist; whether it produces structured CRM records not confirmed | Aaron | If portal does not produce structured records → agent must also parse portal submissions; `PORTAL` intake path requires additional parsing logic |
| A-WS4-8 | Hospital contact email for clarification replies is the `from` address of the inbound request or is in the CRM hospital directory | Medium — no explicit confirmation; standard email convention | Aaron / Kim | If neither source available → clarification email cannot be sent; route to coordinator queue |

---

## Open Questions Before Deployment

- Aaron: Email provider (Gmail / Outlook)? API access available? Does this change ADR-1 from Option C to Option A?
- Aaron: CRM write API confirmed? What is the request creation endpoint and the status update endpoint?
- Aaron: Hospital directory in CRM — does it exist? What is the lookup key (email domain, hospital name, phone number)?
- Aaron: Exact CRM request lifecycle status values — confirm the status codes for `INTAKE_COMPLETE`, `CLARIFICATION_PENDING`, `CANCELLATION_PENDING`, `MODIFICATION_PENDING`, `UNKNOWN_HOSPITAL`, `UNMAPPABLE`, `TYPE_AMBIGUOUS`, `CLARIFICATION_TIMEOUT`.
- Aaron: Does the hospital portal already produce structured CRM records? If yes, portal intake requires no agent parsing and the `PORTAL` intake path is simplified.
- Kim: Do coordinators currently send acknowledgement emails to hospitals on request receipt? Should the agent introduce this in v1?
