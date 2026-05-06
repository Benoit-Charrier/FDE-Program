# D4A — Build Loop Analysis: Apex Billing Dispute Resolution Agent

**Produced:** 2026-05-06
**Status:** Draft — awaiting FDE review
**Source spec:** `Deliverables/D4_agent_purpose_document.md`
**Build guidelines:** `input/build_guidelines.md`
**Built to:** `agent_build/`

---

## 0. Build loop summary

| Category | Count |
|---|---|
| Modules built and tested | 6 |
| Spec gaps that blocked build | 5 (Q-4, Q-5, Q-6, Q-7, Q-8) |
| Questions for FDE before next build session | 8 |
| Tasks that cannot be built without spec revision | 4 (T-001, T-007, T-009, T-010/T-011) |

**Diagnosis:** The spec is strong on governance structure (confidence routing, audit scanning, repeat pattern detection) but silent on the core reasoning logic. T-007 (charge validity assessment) — the central intelligence task of the agent — has zero defined rules. T-001 (NLP intake) has no channel specification. T-009/T-010/T-011 (credit recommendation + write path) are blocked by two confirmed unknowns from D5: the APEX_CREDITS write path mechanism (D5 G-1) and the CRM workflow state engine configuration (D5 G-3).

---

## 1. What was built (confident modules)

All modules built in `agent_build/src/`. All tests in `agent_build/tests/`. Schemas sourced from Gate2-Artefacts CSV headers (2026-04-13/14).

### Module 1: `aurum_ingestion.py` — Aurum CSV ingestion with schema-drift detection

**Spec source:** D4 §4 T-003, T-004, T-014; scenario_context.md §6 (quarterly schema changes; prior RPA failure root cause)

Built: `load_csv(file_type, path)` — validates the header row against the canonical schema before reading any data. Raises `SchemaChangeAlert` on schema drift, halting processing and switching to 100% HITL. Canonical schemas derived from artefact headers; four file types registered: APEX_BILL_DAILY, APEX_DISPUTES_OPEN, APEX_CREDITS, APEX_RECON.

Tests: schema match (pass), schema change (SchemaChangeAlert raised), unknown file type (ValueError).

### Module 2: `staleness_checker.py` — T-014 data-stale detection

**Spec source:** D4 §4 T-014; D4 §8 Hard Stop 5

Built: `is_invoice_stale(invoice_dt, batch_export_dt)` — returns True if the invoice is not in the T-1 batch (same-day or future-dated invoice). Deterministic; no external data required.

Tests: same-day (stale), prior-day (not stale), future-dated (stale), two-days-old (not stale).

### Module 3: `dispute_classifier.py` — T-005 dispute type classification (structured path only)

**Spec source:** D4 §4 T-005; D4 §8 Hard Stop 2; APEX_DISPUTES_OPEN artefact (confirmed DISPUTE_TYPE values)

Built: `classify_from_structured_field(dispute_type_value)` — classifies against the confirmed taxonomy (FUEL_SURCH_DAMAGE, DIM_WEIGHT, REDELIVERY_FEE); returns confidence 1.0 for known types, 0.0 + UNKNOWN for anything outside the taxonomy (triggers ET-002). Case-insensitive.

**Not built:** `classify_from_contact_text()` — spec gap (see Q-5). The function exists but raises `NotImplementedError` to make the gap visible.

Tests: each known type (confidence 1.0), unknown type (UNKNOWN + confidence 0.0), case insensitivity, NotImplementedError from contact-text path.

### Module 4: `pattern_detector.py` — T-008 repeat dispute pattern detection

**Spec source:** D4 §4 T-008; D4 §6 ET-005; D4 §8 Hard Stop 6

Built: `detect_repeat_pattern(customer_id, dispute_type, all_open_disputes)` — counts open disputes (PENDING_CLAIM or AWAITING_CUST status) for the given customer and type; returns `has_repeat_pattern=True` if count ≥ 2. RESOLVED disputes explicitly excluded. Test data derived from APEX_DISPUTES_OPEN artefact (Hayes & Sons C-04451 has 2 open FUEL_SURCH_DAMAGE disputes — confirmed pattern).

Tests: Hayes & Sons detected (repeat_count=2), single dispute (no pattern), different customer (no pattern), RESOLVED excluded.

### Module 5: `constraint_check.py` — T-006 Aurum real-time constraint

**Spec source:** D4 §4 T-006; scenario_context.md §6

Built: `aurum_realtime_correction_possible()` — always returns False. Exists so the constraint is explicit and testable rather than an implicit assumption embedded in workflow logic.

Tests: single test — always False.

### Module 6: `audit_scanner.py` — FM-3/FM-5 daily APEX_CREDITS compliance scan

**Spec source:** D4 §7 FM-3 (audit evidence incompleteness), FM-5 (approval gate bypass); D4 §3 KPI (audit trail compliance)

Built: `scan_credits(records)` — scans APEX_CREDITS records for four violation types:
- `NULL_APPROVER_ID` — APPROVER_ID is empty
- `SYSTEM_APPROVER_ID` — APPROVER_ID matches BDRA-SYSTEM-* or AUTO-* pattern (FM-5 detection)
- `MISSING_AUDIT_REF` — AUDIT_REF is empty
- `UNKNOWN_REASON_CODE` — REASON_CODE not in {FUEL_RECALC, GOODWILL, INV_CORR}

Returns `AuditScanResult` with violation list and compliance rate.

**Spec note:** REASON_CODE taxonomy {FUEL_RECALC, GOODWILL, INV_CORR} is inferred from the artefact sample, not formally defined in D4. See Q-5.

Tests: valid record (no violations), null APPROVER_ID, BDRA-SYSTEM-01 (FM-5), AUTO-* (FM-5), missing AUDIT_REF, unknown REASON_CODE, empty scan (100% compliance), partial compliance rate.

### Module 7: `confidence_router.py` — confidence threshold routing

**Spec source:** D4 §3 KPI (0.85 threshold); D4 §5 Autonomy matrix

Built: `route_by_confidence(confidence_score, current_threshold=0.85)` — routes to AUTONOMOUS or HITL. Threshold is a parameter, not a constant, to support post-deployment recalibration without code deployment (D4 §3 recalibration protocol: threshold raised to 0.90 if precision < 90% in rolling 7-day window). Raises ValueError for out-of-range scores.

Tests: at-threshold (autonomous), above (autonomous), below (HITL), zero (HITL), custom threshold (0.90), out-of-range (ValueError).

---

## 2. Questions asked — spec deficiencies

Each question names what was blocked and what the answer would change.

---

**Q-1: APEX_CREDITS write path mechanism**

**Task blocked:** T-011 (write audit-compliant credit record to APEX_CREDITS)

**What the build hit:** The scenario confirms Aurum has no real-time API and invoice modifications require a 48-hour manual Aurum support ticket. D4 Assumption A-5 (confidence: Low) and D5 Gap G-1 flag this as unresolved. No write interface can be coded without knowing the mechanism.

**What changes if answered:**
- If a direct DB write or controlled API exists: T-011 can be built as a programmatic API call; C-8 (Fully Agentic credit execution) is deliverable.
- If the only path is a pre-populated auto-ticket submission: T-011 becomes a ticket-generation module; APPROVER_ID must be captured before ticket submission; 48-hour turnaround remains; handle-time target partially at risk.
- If no write path exists: agent scope is limited to record preparation; the human must submit the Aurum ticket manually; T-011 is not automated.

**Spec action required:** Confirm with Apex IT and Aurum vendor before next build session.

---

**Q-2: CRM workflow state engine — Salesforce Approval Process / Flow configuration**

**Task blocked:** T-010 (route to approver and await APPROVER_ID); the system-enforced governance gate

**What the build hit:** D4 §5 specifies the approval gate as system-enforced via CRM workflow state. This requires Salesforce Approval Process or Flow to be configured. REST APIs are confirmed but the workflow state capability is not. Without knowing the API call pattern for the PENDING_APPROVAL → APPROVED transition, the T-010 module cannot be built.

**What changes if answered:**
- If Salesforce Approval Process is configured: T-010 is a CRM API call to submit for approval; APPROVER_ID is populated by Salesforce from the authenticated approver's user token; governance gate is system-enforced.
- If Salesforce is in basic CRM mode with no Approval Process: configuration work is required before T-010 can be built; governance gate is currently procedure-dependent (D5 G-3).
- If a different tool handles approvals: T-010 must integrate with that tool instead; APPROVER_ID reconciliation between tools adds a compliance risk.

**Spec action required:** Confirm Salesforce edition and Approval Process configuration with Apex IT.

---

**Q-3: Inbound trigger mechanism — how does the agent receive new dispute cases?**

**Task blocked:** T-001 (parse inbound dispute contact) — the entry point is undefined

**What the build hit:** D4 §1 states the agent "receives disputes from the CRM case queue" but does not specify how disputes arrive in that queue or how the agent is triggered. Three possible mechanisms exist: (a) Salesforce Outbound Message / webhook pushes a notification when a new case is created; (b) the agent polls the CRM case queue via REST API on a schedule; (c) an email parser creates CRM cases from inbound customer email. The trigger architecture determines module design.

**What changes if answered:**
- Webhook: T-001 is an event handler triggered by a Salesforce Outbound Message; near-real-time response.
- Polling: T-001 is a scheduled job querying for cases in a given status; response latency depends on poll interval; must avoid duplicate processing.
- Email parser: T-001 must parse raw email before any CRM case exists; creates its own CRM case via T-002 after parsing.

**Spec action required:** Confirm intake channel with Apex IT and CRM administrator.

---

**Q-4: T-001 multi-invoice disambiguation — what happens when a customer contact references more than one invoice number?**

**Task blocked:** T-001 (parse inbound dispute contact) → T-003 (retrieve invoice data)

**What the build hit:** APEX_BILL_DAILY artefact shows customer C-04451 (Hayes & Sons) has two invoices on the same date (INV-2026-04318: £340 fuel surcharge; INV-2026-04320: £132 fuel surcharge). A customer email disputing "my April invoice" is ambiguous. The spec does not define disambiguation logic: does the agent extract all referenced invoice numbers? Does it escalate when more than one is found? Does it use the APEX_DISPUTES_OPEN INVOICE_NO to resolve the reference?

**What changes if answered:**
- If agent extracts all invoice numbers and processes each as a separate dispute: T-001 produces a list; T-003 is called once per invoice; the case may cover multiple invoices.
- If the agent escalates when >1 invoice is identified: ET-001 fires with a "multiple invoice references — clarify" flag; one-for-one intake is preserved.
- If APEX_DISPUTES_OPEN is the authoritative source and the dispute already has an INVOICE_NO: T-001 defers to T-004 for invoice identification, not NLP extraction.

**Spec action required:** Add a disambiguation rule to D4 §4 T-001 description.

---

**Q-5: T-007 charge validity assessment — what are the rules?**

**Task blocked:** T-007 (assess charge validity) — the core reasoning task

**What the build hit:** D4 §4 T-007 states "rule-based verdict for clear cases; confidence-scored for ambiguous" but provides zero rules. No spec section defines what makes a fuel surcharge valid or invalid. The scenario artefact (Hayes & Sons, INV-2026-04318, £340 fuel surcharge on a damaged delivery) shows the domain — the charge exists and was disputed — but provides no rule for whether the charge is valid under Apex's policy. Without rules, the "rule-based" path in T-007 cannot be built.

**What changes if answered:**
- If validity is determined by comparing the charged rate to a schedule in the credit policy: T-007 retrieves the rate schedule and performs an arithmetic comparison; confidence is high for calculation errors, lower for ambiguous damage claims.
- If validity depends on delivery outcome (damaged = automatically invalid fuel surcharge): T-007 queries CRM for the delivery outcome field value; confidence is high when the field is populated, low when it is not.
- If validity is always ambiguous and the rule-based path is only for edge cases (e.g., duplicate billing): the 0.85 threshold will rarely be reached and the HITL rate will be high.

**Spec action required:** Define the validity rules for each dispute type (FUEL_SURCH_DAMAGE, DIM_WEIGHT, REDELIVERY_FEE) in D4 §4 T-007 before the next build session. This is the highest-priority spec gap.

---

**Q-6: Approval threshold value (ET-006)**

**Task blocked:** T-009 / T-010 routing logic — high-value escalation to COO-designated approver

**What the build hit:** D4 §6 ET-006 states "credit recommendation amount exceeds approval threshold [ASSUMPTION A-6: threshold TBD]." The threshold is unknown. The module that routes a credit recommendation to either the standard approver or the COO-designated senior approver cannot be built without this value.

**What changes if answered:**
- Any specific threshold (e.g., £200): routing logic is a simple comparison; fully buildable.
- Multiple tiers (e.g., <£100 standard, £100–£500 senior, >£500 COO): routing has three branches; each requires a different approver identity lookup.
- No threshold until policy is formalised: T-010 routing must default to routing all cases to standard approver; ET-006 is effectively disabled until the policy is confirmed.

**Spec action required:** COO must define the approval threshold before deployment (D4 §9 A-6). This is a prerequisite, not a build decision.

---

**Q-7: Full REASON_CODE taxonomy**

**Task blocked:** T-009 (credit recommendation — REASON_CODE mapping); `audit_scanner.py` KNOWN_REASON_CODES constant

**What the build hit:** The APEX_CREDITS artefact shows three REASON_CODE values: FUEL_RECALC, GOODWILL, INV_CORR. The scanner uses these as the canonical set. But D4 §7 FM-3 mentions "FUEL_RECALC, GOODWILL, INV_CORR, or other formally defined code" — implying the set may be incomplete. If the credit policy introduces new codes (e.g., DIM_RECALC, REDELIV_WAIVE), the audit scanner will flag them as violations. The policy registry must define the canonical set before deployment.

**What changes if answered:**
- If {FUEL_RECALC, GOODWILL, INV_CORR} is the complete set: no change required; current scanner is correct.
- If additional codes exist: update KNOWN_REASON_CODES in `audit_scanner.py`; update T-009 REASON_CODE mapping logic.

**Spec action required:** Define the complete REASON_CODE taxonomy in the credit policy document (D4 §9 A-6 prerequisite).

---

**Q-8: APEX_CUSTOMER_MASTER schema and account status field values**

**Task blocked:** Autonomy matrix — Human Takes Over condition based on account status

**What the build hit:** D4 §5 Autonomy matrix references "the customer's account has been flagged as inactive, in collections, or under a formal payment plan in the APEX_CUSTOMER_MASTER export." The APEX_CUSTOMER_MASTER CSV is not present in the Gate2-Artefacts; its schema and account status field values are unknown. A module that checks account status before proceeding cannot be built without knowing the field name and the set of status values that trigger escalation.

**What changes if answered:**
- If the field is ACCOUNT_STATUS with values {ACTIVE, INACTIVE, COLLECTIONS, PAYMENT_PLAN}: the check is a simple lookup; fully buildable.
- If the schema differs: the check must be adapted to the actual field name and values.

**Spec action required:** Obtain the APEX_CUSTOMER_MASTER schema from Apex IT or the Aurum vendor and add it to the canonical schemas in `aurum_ingestion.py`.

---

## 3. What could not be built — blocked modules

| Task | Reason blocked | Spec action required |
|---|---|---|
| T-001: NLP intake parser (contact text extraction) | No intake channel specified (Q-3); no extraction field list; no disambiguation logic for multi-invoice contacts (Q-4) | Add intake channel and extraction field spec to D4 §4 T-001 |
| T-007: Charge validity assessment | Zero validity rules defined for any dispute type (Q-5) — highest-priority spec gap | Define rules per dispute type in D4 §4 T-007; this is the core intelligence task and it has no spec |
| T-009: Credit recommendation package | Credit policy does not exist (D4 A-6); REASON_CODE→credit_amount mapping undefined (Q-7); approval threshold TBD (Q-6) | Formalise credit policy before build |
| T-010 / T-011: Approval workflow + APEX_CREDITS write | CRM workflow state API unknown (Q-2); APEX_CREDITS write path mechanism unknown (Q-1) | Confirm both with Apex IT before build |
| T-012: Customer notification | CRM outbound messaging API spec unknown; notification templates not defined | Confirm CRM messaging capability and define templates |
| Account status check (Autonomy matrix) | APEX_CUSTOMER_MASTER schema unknown (Q-8) | Obtain schema from Apex IT |

---

## 4. Spec deficiency diagnosis

Each question and each blocked module is a spec deficiency. Classified by type (per `references/spec-ambiguity-vs-builder-mistakes.md` taxonomy):

| Deficiency | Type | Priority |
|---|---|---|
| T-007: No validity rules for any dispute type | **Design gap** — spec is silent on required behaviour | Critical — highest priority; the agent cannot do its primary job without this |
| Q-1: APEX_CREDITS write path unknown | **Design gap** — spec assumes a write path exists (D4 A-5) without defining it | Critical — blocks credit execution and audit trail enforcement |
| Q-2: CRM workflow state engine unconfirmed | **Design gap** — spec requires system-enforced approval gate but the mechanism is unconfirmed | Critical — governance hard stop degrades to procedure-only without this |
| Q-3: Inbound trigger mechanism | **Design gap** — spec states agent "receives disputes from CRM case queue" without defining the trigger | High — agent cannot start without this |
| Q-4: Multi-invoice disambiguation | **Spec ambiguity** — the spec is silent on a case the artefact data confirms is real | High — Hayes & Sons has 2 invoices on the same day; this case will occur |
| Q-5: NLP classification rules (T-005 contact text path) | **Design gap** — spec mentions NLP extraction without defining rules | High — structured path covers cases already in APEX_DISPUTES_OPEN; NLP path needed for new inbound contacts |
| Q-6: Approval threshold value | **Design gap** — explicitly TBD; COO must define before deployment | Medium — blocks ET-006 routing but not core intake or validity path |
| Q-7: Full REASON_CODE taxonomy | **Spec ambiguity** — artefact shows 3 codes; spec implies more may exist | Medium — audit scanner may generate false positive violations if new codes are introduced |
| Q-8: APEX_CUSTOMER_MASTER schema | **Design gap** — field names and status values not in any artefact | Medium — blocks account status check but not core billing dispute path |

---

## 5. Recommended D4 revisions before next build session

1. **Add T-007 validity rules section** — for each dispute type, define: (a) what constitutes a clear-cut valid charge; (b) what constitutes a clear-cut invalid charge; (c) what makes a case ambiguous (triggers confidence < 0.85). This is the most important addition. Example structure: "FUEL_SURCH_DAMAGE: charge is invalid if delivery outcome in CRM = DAMAGED_REFUSED and the fuel surcharge calculation matches the Aurum rate schedule; charge is ambiguous if delivery outcome is missing or CRM delivery field is not populated."

2. **Add T-001 intake specification** — confirm the intake channel and add disambiguation logic for multi-invoice contacts. Minimum viable: "if multiple invoice numbers are extracted, create one case per invoice" or "if ambiguous, escalate with 'multiple invoice references' flag."

3. **Add T-010 workflow state API note** — confirm whether Salesforce Approval Process is available and document the API call pattern for PENDING_APPROVAL → APPROVED transition. If not available, document the configuration requirement as a pre-build prerequisite.

4. **Update A-5 from Low confidence to Confirmed/Blocked** — the APEX_CREDITS write path must be resolved before D4 can be considered build-ready. It is currently the highest-consequence low-confidence assumption in the spec.

5. **Define REASON_CODE taxonomy** — even informally, confirm whether {FUEL_RECALC, GOODWILL, INV_CORR} is complete or whether additional codes are expected from the credit policy.
