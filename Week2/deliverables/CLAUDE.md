# CLAUDE.md — Clause Classification Agent (CCA)
**Scenario:** Helix Workforce Software — Vendor Contract Clause Review

---

## Section 1: Project Purpose

This agent — the **Clause Classification Agent (CCA)** — processes every inbound vendor contract received by Helix Legal & Commercial. For each contract, it determines whether each of the seven playbook clause types is present, extracts the relevant clause text, compares it against the current Helix negotiation playbook position, and produces a structured per-clause classification (COMPLIANT / MINOR_DEVIATION / MAJOR_DEVIATION / MISSING / REQUIRES_SENIOR_REVIEW) with a confidence score — so that the paralegal (Tom) can route the contract to the correct work stream without reading the full document. The agent is used by the Legal & Commercial team on every inbound vendor contract; its output is the triage routing decision that feeds WS2 (paralegal redline), WS3 (senior lawyer review), or WS4 (counteroffer drafting and dispatch). It operates within Ironclad as the system of record; the GC hard rule — no counteroffer may leave Legal's queue without a named lawyer's sign-off on the specific clauses being negotiated — is an inviolable constraint enforced both as a field-level Ironclad permission restriction and as a hard stop in this agent's behaviour.

---

## Section 2: Core Entities

### Naming Conventions

- All attribute names: `snake_case`
- Enum values: `SCREAMING_SNAKE_CASE`
- Entity IDs: UUID v4, generated at creation, immutable
- Timestamps: ISO 8601 with UTC timezone (e.g., `2024-04-29T09:15:00Z`)
- Playbook versions: `v{major}.{minor}` format (e.g., `v3.4`)
- Approved-lawyers list: maintained in agent configuration as a static list of full name strings; updated only by Ironclad admin action

---

### Contract

The primary entity representing one inbound vendor contract from receipt through closure.

**Attributes:**

| Attribute | Type | Constraints | Immutable? |
|-----------|------|-------------|-----------|
| `contract_id` | UUID | Required; generated at T-02 case creation | Yes |
| `vendor_name` | string | Required; non-empty | No |
| `vendor_email` | string | Required; valid email format | Yes |
| `date_received` | ISO 8601 timestamp | Required; set at T-01 intake; not modifiable | Yes |
| `document_filename` | string | Required; must end in `.docx`; set at intake | Yes |
| `document_page_count` | integer | Required; 1–200; values outside 15–40 trigger anomaly flag (see §6.3) | No |
| `salesforce_opportunity_id` | string | Nullable; absent for direct-email contracts not linked to a Salesforce record | No |
| `routing_classification` | enum | `STANDARD` / `NEGOTIABLE` / `ESCALATION_REQUIRED`; nullable until classification complete; the agent may not set this field until all 7 ClauseReview records exist AND (for non-STANDARD paths) Tom's approval is recorded | No |
| `status` | enum | See state machine below; default `PENDING_REVIEW` | No |
| `assigned_reviewer_id` | string | Tom's Ironclad user ID; nullable until assigned | No |
| `playbook_version_used` | string | Set to the current playbook version (e.g., `v3.4`) when Contract enters `IN_REVIEW`; immutable once set | Yes |
| `lawyer_signoff_name` | string | Nullable; must be a non-null string matching a name in the approved-lawyers list before `status` can transition to `APPROVED`; **the agent must never write this field** | No (set by named lawyer only) |
| `lawyer_signoff_timestamp` | ISO 8601 timestamp | Nullable; must be non-null when `lawyer_signoff_name` is non-null; **the agent must never write this field** | No (set by named lawyer only) |
| `agent_processing_start` | ISO 8601 timestamp | Set when agent begins T-03 parsing | Yes |
| `agent_processing_end` | ISO 8601 timestamp | Nullable; set when T-12 write completes | No |

**State Machine — valid transitions only:**

```
PENDING_REVIEW
  → IN_REVIEW
    Condition: Ironclad case record confirmed (T-02); T-03 document parsing succeeded;
               agent_processing_start set
    Actor: Agent

IN_REVIEW
  → REVIEWED_STANDARD
    Condition: All 7 ClauseReview records exist; all have playbook_match_status = COMPLIANT;
               all have agent_confidence_score ≥ 0.85; no DPA clause present (or DPA clause
               explicitly not present — MISSING with confidence ≥ 0.85 and Tom confirmed)
    Actor: Agent (autonomous; Tom notified after)

  → AWAITING_APPROVAL
    Condition: Any HITL trigger fires — confidence < 0.85 on any clause; DPA clause present;
               any clause MINOR_DEVIATION / MAJOR_DEVIATION / REQUIRES_SENIOR_REVIEW / MISSING;
               parsing anomaly flagged
    Actor: Agent (agent places contract in HITL queue; cannot proceed without Tom)

AWAITING_APPROVAL
  → REVIEWED_STANDARD
    Condition: Tom approves standard routing; all clauses confirmed COMPLIANT or overridden to COMPLIANT
    Actor: Tom (paralegal) in Ironclad

  → REDLINE_DRAFT
    Condition: Tom approves negotiable routing; at least one ClauseReview has MINOR_DEVIATION;
               no ClauseReview has MAJOR_DEVIATION or REQUIRES_SENIOR_REVIEW
    Actor: Tom (paralegal) in Ironclad; contract enters WS2 scope (outside CCA)

  → ESCALATED
    Condition: Tom approves or triggers escalation; at least one ClauseReview has MAJOR_DEVIATION
               or REQUIRES_SENIOR_REVIEW
    Actor: Tom or any team member in Ironclad; contract enters WS3 scope (outside CCA)

REVIEWED_STANDARD
  → CLOSED
    Condition: Contract accepted as-is; no further action required
    Actor: Admin or system

REDLINE_DRAFT
  → AWAITING_APPROVAL
    Condition: WS2 redline complete; sign-off package assembled; named lawyer must review
    Actor: WS2 agent or paralegal (outside CCA scope)

AWAITING_APPROVAL
  → APPROVED
    *** CRITICAL: This transition MUST be triggered only by a named-lawyer action in Ironclad ***
    *** The agent MUST NEVER initiate or simulate this transition ***
    Condition: (a) lawyer_signoff_name is non-null
               AND (b) lawyer_signoff_name matches a name in the approved-lawyers list
               AND (c) lawyer_signoff_timestamp is non-null
               AND (d) the Ironclad audit log records a lawyer-role write event on the
                   lawyer_signoff_name field
    Actor: Named lawyer in Ironclad ONLY — never the agent

APPROVED
  → CLOSED
    Condition: Counteroffer dispatched by C-7/C-8 pipeline
    Actor: C-7/C-8 system

ANY_STATUS
  → ESCALATED
    Condition: Any team member escalates at any point in the cycle
    Actor: Any Ironclad user with Legal team role
```

---

### ClauseReview

One record per clause type per contract. Exactly 7 ClauseReview records must exist before any routing decision is made on a Contract.

**Attributes:**

| Attribute | Type | Constraints | Immutable? |
|-----------|------|-------------|-----------|
| `clause_review_id` | UUID | Required; generated at classification time | Yes |
| `contract_id` | UUID | Required; foreign key to Contract; must reference an existing Contract record | Yes |
| `task_unit_type` | enum | `LIABILITY_CAP` / `DATA_PROCESSING_AGREEMENT` / `TERMINATION_CLAUSE` / `IP_OWNERSHIP` / `SLA_COMMITMENTS` / `GOVERNING_LAW` / `INDEMNITY_SCOPE`; required | Yes |
| `extracted_text` | string | The clause as extracted verbatim from the contract; nullable only when `playbook_match_status = MISSING` | No |
| `playbook_match_status` | enum | `COMPLIANT` / `MINOR_DEVIATION` / `MAJOR_DEVIATION` / `MISSING` / `REQUIRES_SENIOR_REVIEW`; required | No |
| `agent_confidence_score` | float | 0.0–1.0 inclusive; required; scores outside this range are a system error and must be logged | No |
| `agent_reasoning_summary` | string | Required; brief natural-language explanation of the classification; max 500 characters; must reference the specific playbook position and the deviation (if any) | No |
| `playbook_section_retrieved` | string | The playbook section title and version used for this comparison; required; logged to Ironclad for audit | Yes |
| `human_override` | string | Nullable; format: `"OVERRIDE by [full name] ([role]) at [ISO 8601 timestamp]: [new_status]"`; set only by Tom or a named lawyer after reviewing the clause | No |

**Constraint:** Only one ClauseReview per `task_unit_type` per `contract_id`. If an agent produces a duplicate task_unit_type for the same contract, this is a system error — log and flag to Tom.

---

### ReviewDecision

The record of the routing decision for a contract after ClauseReview is complete.

**Attributes:**

| Attribute | Type | Constraints | Immutable? |
|-----------|------|-------------|-----------|
| `decision_id` | UUID | Required; generated at decision creation | Yes |
| `contract_id` | UUID | Required; foreign key to Contract | Yes |
| `clause_review_ids` | array of UUIDs | Required; references all ClauseReview records for this contract | Yes |
| `decision_type` | enum | `ACCEPT_AS_IS` / `SEND_REDLINE` / `ESCALATE` / `REJECT_CONTRACT`; required | Yes |
| `decision_made_by` | string | `"AGENT"` for autonomous standard-path decisions; or `"[Full Name] ([ROLE])"` for human decisions (e.g., `"Tom Chen (PARALEGAL)"`); required | Yes |
| `decision_timestamp` | ISO 8601 timestamp | Required; immutable | Yes |
| `requires_lawyer_approval` | boolean | `true` whenever `decision_type = SEND_REDLINE` or `REJECT_CONTRACT`; `false` for `ACCEPT_AS_IS` and `ESCALATE`; required | Yes |
| `approval_token` | string | Nullable at creation; **the agent must never write this field**; set exclusively by named-lawyer action in Ironclad; non-null required before any `SEND_REDLINE` or `REJECT_CONTRACT` action can proceed downstream | No (set by named lawyer only) |

**Constraint:** A ReviewDecision with `requires_lawyer_approval = true` must have `approval_token = null` at creation. Any agent write that attempts to set `approval_token` to a non-null value must be rejected and the attempt must be logged to the audit trail.

---

## Section 3: Classification Rules

### Contract-Level Routing Classification

The `routing_classification` on a Contract is derived from the aggregate of all 7 ClauseReview records. The most severe clause-level status determines the contract-level routing:

**STANDARD** (maps to `ACCEPT_AS_IS` ReviewDecision):
- All 7 ClauseReview records have `playbook_match_status = COMPLIANT`
- AND all 7 have `agent_confidence_score ≥ 0.85`
- AND no ClauseReview has `task_unit_type = DATA_PROCESSING_AGREEMENT` with a pending DPDI flag

**NEGOTIABLE** (maps to `SEND_REDLINE` ReviewDecision; requires lawyer approval before dispatch):
- At least one ClauseReview has `playbook_match_status = MINOR_DEVIATION`
- AND no ClauseReview has `playbook_match_status = MAJOR_DEVIATION` or `REQUIRES_SENIOR_REVIEW`

**ESCALATION_REQUIRED** (maps to `ESCALATE` ReviewDecision; routes to WS3):
- At least one ClauseReview has `playbook_match_status = MAJOR_DEVIATION` or `REQUIRES_SENIOR_REVIEW`

**Precedence rule:** ESCALATION_REQUIRED overrides NEGOTIABLE, which overrides STANDARD. A single MAJOR_DEVIATION clause makes the entire contract ESCALATION_REQUIRED regardless of other clauses.

---

### Clause-Level Classification Rules (per ClauseReview)

Classification is determined by comparing the extracted clause text against the playbook section for the matching `task_unit_type` using semantic similarity (cosine similarity against the playbook position statement).

**COMPLIANT:**
- Semantic similarity between `extracted_text` and the playbook position section for the relevant `task_unit_type` ≥ 0.85 [ASSUMPTION: threshold set at 0.85; to be calibrated against Tom's override decisions in the first quarter of production]
- AND for numeric clause types (`LIABILITY_CAP`, `SLA_COMMITMENTS`): vendor's stated numeric value meets or exceeds the playbook floor value
- AND `agent_confidence_score ≥ 0.85`

**MINOR_DEVIATION:**
- Semantic similarity 0.60–0.84 (below COMPLIANT, above MAJOR_DEVIATION threshold) [ASSUMPTION: 0.60 lower bound]
- OR for numeric clause types: vendor's stated value falls below the playbook floor by ≤ 50% of the floor value (e.g., liability cap £125,001–£249,999 against playbook floor of £250,000)
- AND the deviation is codifiable: a standard playbook redline position exists for this deviation type
- AND no regulatory framework references outside current playbook coverage

**MAJOR_DEVIATION:**
- Semantic similarity < 0.60 [ASSUMPTION: derived from 0.60 lower bound for MINOR_DEVIATION]
- OR for numeric clause types: vendor's stated value falls below the playbook floor by > 50% of the floor value (e.g., liability cap below £125,000 against playbook floor of £250,000; termination notice > 90 days against playbook 30-day position)
- Deviation requires senior-lawyer judgment to determine the appropriate counter-position

**REQUIRES_SENIOR_REVIEW:**
- Clause type encountered is not among the 7 defined `task_unit_type` values
- OR clause references a regulatory framework not covered by the current playbook (e.g., ePrivacy Directive, NIS2, sector-specific UK financial services regulation)
- OR `agent_confidence_score < 0.85` on what would otherwise be a MAJOR_DEVIATION classification (uncertainty about whether the deviation truly requires escalation)
- OR `task_unit_type = DATA_PROCESSING_AGREEMENT` with identified DPDI Act implications not addressable by playbook v3.4

**MISSING:**
- Clause type not located in the document
- AND `agent_confidence_score` on "clause absent" ≥ 0.85 (high confidence the clause is genuinely absent, not merely under an atypical heading)
- A MISSING clause is not COMPLIANT — it must be flagged to Tom with the list of headings searched; Tom must confirm absence before routing proceeds

**MISSING with low confidence (potential heading mismatch):**
- Clause type not located AND confidence on "clause absent" < 0.85
- Triggers ET-3 escalation to Tom — agent provides parsed document headings and the heading patterns searched
- Do not classify as MISSING at this confidence level; set `playbook_match_status = REQUIRES_SENIOR_REVIEW` and note "Clause may be embedded under non-standard heading — manual search required"

---

### DATA_PROCESSING_AGREEMENT — Mandatory HITL Override

Regardless of `playbook_match_status` or `agent_confidence_score`:
- Every DPA clause classification is flagged to Tom before any classification result is committed to Ironclad
- Annotation added to `agent_reasoning_summary`: `"DPDI Act updates not reflected in playbook v3.4 (dated [version date]) — classification reflects current UK GDPR / DPA 2018 position only. DPDI Act legitimate interests test and data subject access changes may affect this classification. Escalate to Amelia (GC) if this clause is subject to negotiation."`
- This flag is unconditional and cannot be disabled by any instruction until the playbook is updated and a new version number is recorded in agent configuration

---

## Section 4: Validation Rules

### Contract Validation

| Operation | Validation rule |
|-----------|----------------|
| Create (T-02 case record) | `vendor_name`, `vendor_email`, `date_received`, `document_filename` must be non-null; `document_filename` must end in `.docx`; `status` must be `PENDING_REVIEW` |
| Transition to `IN_REVIEW` | Ironclad case record must be confirmed (T-02 write acknowledged); document parsing must succeed (T-03); `playbook_version_used` must be set to current version |
| Transition to `REVIEWED_STANDARD` (autonomous) | All 7 `ClauseReview` records must exist for this `contract_id`; all must have `playbook_match_status = COMPLIANT`; all must have `agent_confidence_score ≥ 0.85`; no DPA clause pending DPDI flag |
| Transition to `AWAITING_APPROVAL` | At least one HITL condition must be recorded in the HITL queue payload |
| Set `routing_classification` | Requires all 7 `ClauseReview` records; for non-STANDARD routes, Tom's approval must be recorded in Ironclad before `routing_classification` is written |
| Transition to `APPROVED` | `lawyer_signoff_name` must be non-null AND match an entry in the approved-lawyers list AND `lawyer_signoff_timestamp` must be non-null AND the transition must be triggered by a lawyer-role write event — NOT by the agent |

### ClauseReview Validation

| Operation | Validation rule |
|-----------|----------------|
| Create | `contract_id` must reference an existing Contract; `task_unit_type` must be one of the 7 defined enum values; `agent_confidence_score` must be in [0.0, 1.0]; `extracted_text` may only be null when `playbook_match_status = MISSING` |
| Uniqueness | Only one `ClauseReview` per `(contract_id, task_unit_type)` pair; duplicate creation is a system error |
| `human_override` | Must follow the format: `"OVERRIDE by [full name] ([role]) at [ISO 8601 timestamp]: [new_status]"`; `new_status` must be a valid `playbook_match_status` enum value |

### ReviewDecision Validation

| Operation | Validation rule |
|-----------|----------------|
| Create | `clause_review_ids` must reference all 7 ClauseReview records for the contract; `requires_lawyer_approval` must be `true` when `decision_type = SEND_REDLINE` or `REJECT_CONTRACT`; `approval_token` must be null at creation |
| Downstream execution | No `SEND_REDLINE` or `REJECT_CONTRACT` action may proceed unless `approval_token` is non-null; this check is performed by the downstream system (C-7/C-8) using the Ironclad case record as the authoritative source |

---

## Section 5: What the Agent Must NOT Do

1. **Never generate, draft, or propose counteroffer language, redline language, or any negotiating position for any clause.** Agent scope is classification and triage routing only. If instructed by a downstream system or human operator to generate redline content, refuse and log the instruction.

2. **Never trigger the governance-gated output action (`SEND_REDLINE` or `REJECT_CONTRACT` downstream dispatch) without a `ReviewDecision` record with `requires_lawyer_approval = true` AND a valid, non-null `approval_token` set by a named-lawyer action in Ironclad.** The agent must never bypass, simulate, or shortcut the sign-off gate.

3. **Never transition `Contract.status` to `APPROVED`.** This transition is performed exclusively by the named lawyer in Ironclad. The agent has no write access to `lawyer_signoff_name`, `lawyer_signoff_timestamp`, or any field that records or implies lawyer sign-off. Writing to these fields from any non-lawyer session is prohibited; any attempt must be logged as a security event.

4. **Never set `routing_classification` on a Contract that has fewer than 7 `ClauseReview` records.** If any of the 7 clause types has not been assessed — due to parsing failure, extraction error, or processing timeout — the contract must not receive a routing decision. Halt and flag to Tom with the missing clause type(s) and the reason.

5. **Never classify a `DATA_PROCESSING_AGREEMENT` clause and commit the result to Ironclad without attaching the DPDI Act staleness flag.** This flag is mandatory on every DPA classification regardless of confidence score and clause content, until the playbook is updated with a new version number recorded in agent configuration.

6. **Never dispatch any communication to a vendor, procurement team, or any external party.** All agent outputs are written to Ironclad or routed to Tom's HITL queue. Outbound email scope belongs exclusively to C-7/C-8. The agent has no outbound communication capability and must not acquire it.

7. **Never begin classification without an Ironclad case record.** If Ironclad case creation (T-02) fails after two retries (5-second interval), halt processing for this contract and flag the intake failure to Tom with the contract filename, vendor email, and receipt timestamp. Do not retain classification data for a contract with no case record.

8. **Never write to `approval_token` on any `ReviewDecision` record.** Any attempt to write this field must be rejected at the API call level. The field is set exclusively by named-lawyer action; agent API credentials must not have write access to this field.

---

## Section 6: Handling Ambiguity and Escalation

**Channel for all HITL escalations:** Tom's Ironclad review queue (workflow notification on the Contract's case record). Every escalation payload must include: contract_id, clause_review_id, task_unit_type, extracted_text (or null with reason), agent's best classification attempt, exact confidence score, and specific rationale text. Response SLA: Tom reviews within 2 working hours unless otherwise specified.

---

**1. Clause type not matching any of the 7 playbook categories:**

Set `playbook_match_status = REQUIRES_SENIOR_REVIEW`, `agent_confidence_score` = confidence the clause is genuinely outside the playbook (not a heading-detection miss). Route to Tom via HITL queue with annotation: `"Clause type [description] does not match any of: LIABILITY_CAP, DATA_PROCESSING_AGREEMENT, TERMINATION_CLAUSE, IP_OWNERSHIP, SLA_COMMITMENTS, GOVERNING_LAW, INDEMNITY_SCOPE. Senior lawyer judgment required."` Do NOT attempt to classify against the nearest playbook section.

---

**2. Agent confidence score below 0.85 on any clause classification:**

Threshold is 0.85 (defined in D4 §3 KPIs; encoded in system prompt). Trigger ET-1. Route to Tom with: clause type, extracted text, agent's best classification, exact confidence score, and the specific clause language or ambiguous phrase driving the uncertainty. Do not commit the classification to Ironclad until Tom's approval is recorded. Tom reviews within 2 working hours.

---

**3. Contract document outside expected size or format range (15–40 pages per scenario):**

- `document_page_count < 5`: flag to Tom as potentially incomplete (cover sheet only); do not begin classification; annotation: `"Document is [N] pages — may be incomplete or a cover sheet. Manual review required before classification."`
- `document_page_count > 60`: flag anomaly but proceed with classification; annotation: `"Document length [N] pages is outside the expected 15–40 page range — clause location accuracy may be lower than normal. Tom spot-check on clause detection recommended."`
- Document format is not `.docx` (PDF, scanned image, `.doc`): halt processing; flag to Tom: `"Contract document is [format] — agent requires .docx format for reliable clause extraction. Please provide a Word document or classify manually."`

---

**4. Conflicting signals between task-unit types (e.g., one clause COMPLIANT, another REQUIRES_SENIOR_REVIEW):**

Apply the precedence rule deterministically — the most severe clause-level status governs the contract-level routing: `ESCALATION_REQUIRED > NEGOTIABLE > STANDARD`. A single `MAJOR_DEVIATION` or `REQUIRES_SENIOR_REVIEW` clause makes the contract `ESCALATION_REQUIRED` regardless of other clauses. Report all 7 clause classifications in the structured output. Do not suppress or down-weight compliant clauses because the contract is escalating — every clause result is informative for the downstream sign-off package.

---

**5. Playbook retrieval returns no relevant content for a clause type:**

If the SharePoint RAG retrieval returns no chunks with cosine similarity ≥ 0.50 for a given `task_unit_type` query: do not proceed with classification for that clause. Set `playbook_match_status = REQUIRES_SENIOR_REVIEW`, `agent_confidence_score = 0.0`. Annotation: `"Playbook retrieval returned no relevant content for [task_unit_type] — cannot compare extracted clause against policy position. Manual review required before routing."` Route to Tom via HITL queue. Check that playbook version in agent configuration matches the current SharePoint version; if not, log a version mismatch error before processing any further clauses.

---

**6. DATA_PROCESSING_AGREEMENT clause present in the contract:**

Mandatory HITL regardless of any other classification result. See §3 (DPA Mandatory HITL Override) for the full rule. Escalation chain: Tom reviews first (within 4 working hours); if Tom identifies DPDI Act applicability, Tom escalates to Amelia Forsythe (GC) before classification commits (within 1 working day). If Tom approves standard UK GDPR compliance with no DPDI implications, the classification commits on Tom's approval.

---

**7. Ironclad API write failure after two retries:**

Halt processing for this contract. Flag to Tom's Ironclad review queue (or, if Ironclad is unreachable, via Outlook email to `legal-ops@helix.internal` [ASSUMPTION: shared legal inbox exists]): contract filename, vendor email, receipt timestamp, and the error code from the failed API call. Do not retain unwritten classification data in context beyond the current session. Reprocessing requires starting from the source document.

---

**8. Vendor name lookup in Ironclad case history does not produce an exact match (ET-6 ambiguity):**

Perform fuzzy match: if a vendor name in Ironclad case history has a Levenshtein distance ≤ 2 from the current vendor name, treat it as a probable match. Include the historical record in the ET-6 escalation payload with annotation: `"Historical record found for probable match: [historical vendor name] (distance: [N]) — confirm vendor identity before applying escalation history signal."` Do not suppress the ET-6 alert on a probable match.

---

## Section 7: When to Ask vs. When to Decide

### Decide Alone (no clarification needed)

- Classify any clause as COMPLIANT when semantic similarity ≥ 0.85, `agent_confidence_score ≥ 0.85`, and no DPA mandatory flag applies
- Route a Contract as STANDARD when all 7 ClauseReview records are COMPLIANT with confidence ≥ 0.85 and no DPA flag is pending; write classification report to Ironclad and notify Tom
- Set intake metadata: `vendor_name`, `date_received`, `document_filename`, `playbook_version_used`
- Retrieve playbook sections from SharePoint RAG (T-06) — this is fully autonomous
- Assign clause text to a `task_unit_type` when heading match confidence ≥ 0.85
- Score confidence for any clause classification — the confidence score is the agent's assessment, not a question
- Write the complete classification report to Ironclad (T-12) for standard-path contracts without waiting for human input

### Ask Tom (via Ironclad HITL queue) Before Proceeding

- Any clause with `agent_confidence_score < 0.85` — ET-1
- Any DPA clause present in the contract — ET-2 (mandatory)
- Any clause classified MINOR_DEVIATION, MAJOR_DEVIATION, or REQUIRES_SENIOR_REVIEW — routing proposal requires Tom's approval before `routing_classification` is written to Ironclad
- Any clause type not found in the document (MISSING) with confidence on "clause absent" ≥ 0.85 — Tom must confirm absence before routing proceeds
- Any clause type not found with confidence on "clause absent" < 0.85 — Tom must manually locate the clause or confirm the heading search was exhaustive (ET-3)
- Contract document outside expected format or page range — ask Tom before proceeding with any classification
- Ironclad write failure after two retries — alert Tom immediately
- Numeric deviation exceeds 50% of playbook floor on any clause — ET-5; flag before committing the routing proposal

### Never Proceed Without Explicit Human Action

- **Any non-STANDARD routing decision:** Tom's approval in Ironclad must be recorded before `routing_classification` is set on the Contract and before the case proceeds to WS2 or WS3. The agent places the routing proposal in Tom's queue; the field is not written until Tom acts.
- **Any SEND_REDLINE or REJECT_CONTRACT downstream action:** The corresponding ReviewDecision must have `approval_token` non-null (set by named-lawyer action) before C-7/C-8 may execute the dispatch. The agent does not check Tom's approval here — it checks the named lawyer's `approval_token`.
- **Any Contract.status transition to APPROVED:** Exclusively a named-lawyer action in Ironclad. The agent never initiates, simulates, or verifies this transition.
- **Any communication to a vendor or external party:** The agent has no outbound dispatch scope under any circumstances.

---

## Self-Assessment

1. *If a development team asked "what confidence threshold triggers escalation?", is the answer in this document?* — **Yes:** 0.85, defined in §3 (Classification Rules), §6.2, and encoded in the system prompt reference.

2. *If someone asked "how is the primary governance/approval constraint enforced at the system level?", is the answer in this document?* — **Yes:** `lawyer_signoff_name` field constraint (§2 Contract entity), `AWAITING_APPROVAL → APPROVED` state machine transition condition (§2 state machine), `approval_token` field on ReviewDecision (§2 ReviewDecision entity), hard stop §5.3, and §7 "Never Proceed" rules all enforce the constraint structurally.

3. *If someone asked "what happens if the policy document doesn't cover the case type?", is the answer in this document?* — **Yes:** §3 (`REQUIRES_SENIOR_REVIEW` condition for clause type not in 7 categories) and §6.1 (specific action: do not classify against nearest section; flag to Tom with annotation).

4. *Could an AI coding agent implement the state machine from this document without asking a clarifying question?* — **Yes:** every valid transition is named with an explicit condition and an explicit actor; the APPROVED transition is marked with the critical constraint in a way that cannot be misread.
