# D4 — Agent Purpose Document: Apex Billing Dispute Resolution Agent

**Produced:** 2026-05-06
**Status:** Revised 2026-05-06 — D4 revision 1 (D4A build loop: T-001 disambiguation and §4b T-007 rule framework added; A-5 status updated)

---

## 0. Executive summary

- The agent's Job to be Done is to convert an inbound billing dispute from an unstructured customer contact into a structured, evidence-backed credit recommendation with a complete audit record — enabling a human approver to close the dispute in ≤8 minutes instead of the current 28 minutes (scenario: 60 disputes/day × 28 min/case = 1,680 agent-minutes/day absorbed today without a single compliant audit trail entry).
- The agent decides alone on dispute intake, invoice retrieval, dispute classification (when confidence ≥ 0.85), and data-stale flagging; it cannot write any credit record to APEX_CREDITS until a named human APPROVER_ID is recorded in the workflow state — this gate is system-enforced, not procedure-dependent, and is the direct response to the compliance gap confirmed in Artefact 2 (Sandra's £170 credit with no audit log entry).
- The primary failure risk is systematic confidence miscalibration: the agent consistently classifying ambiguous charge validity cases as high-confidence and routing them to autonomous resolution, causing incorrect validity verdicts to accumulate at scale without triggering the HITL threshold — detected via a weekly precision audit against a human reviewer sample, with a defined threshold retuning mechanism triggered if precision drops below 90% in any rolling 7-day window.

---

## 0b. Table of contents

- [0. Executive summary](#0-executive-summary)
- [0b. Table of contents](#0b-table-of-contents)
- [1. Agent identity](#1-agent-identity)
- [2. Primary objectives](#2-primary-objectives)
- [3. KPIs](#3-kpis)
- [4. Activity catalog](#4-activity-catalog)
- [4b. T-007 validity assessment rule framework](#4b-t-007-validity-assessment-rule-framework)
- [5. Autonomy matrix](#5-autonomy-matrix)
- [6. Escalation triggers](#6-escalation-triggers)
- [7. Failure modes](#7-failure-modes)
- [8. Out-of-scope hard stops](#8-out-of-scope-hard-stops)
- [9. Assumption log](#9-assumption-log)

---

## 1. Agent identity

- **Agent name:** Apex Billing Dispute Resolution Agent (BDRA)
- **Job to be Done:** Convert every inbound billing dispute into a structured, evidence-backed credit recommendation with a completed, audit-compliant credit record — enabling a human approver to close the case in ≤8 minutes by eliminating the data-assembly burden and enforcing the audit trail that the current process consistently bypasses.
- **Business context:** Operates within the Apex Customer Operations team, handling WS4 (Billing Disputes, ~60 cases/day). Receives disputes from the CRM case queue. Handoffs downstream: (1) to the designated human approver for credit amount confirmation and APPROVER_ID assignment; (2) to APEX_CREDITS write path for the compliant credit record; (3) to CRM outbound messaging for customer notification.
- **Delegation archetype:** Mixed — Human-led + Agent Support for C-6 (dispute intake and charge validity assessment); Fully Agentic below approval threshold for C-8 (audit-compliant credit record execution once APPROVER_ID is provided). Confirmed from D2; no change. Credit amount determination (C-7) remains Human Only until a formal credit policy is defined and approved — this is a prerequisite, not a design choice.

---

## 2. Primary objectives

1. **Handle-time target:** Reduce average agent handle time for billing disputes from 28 min/case to ≤10 min/case (human reviewer time only, measured from case assignment to case closure) within 90 days of deployment across at least 80% of cases.

2. **Audit trail compliance target:** Achieve 100% of credit records written to APEX_CREDITS containing non-null, named APPROVER_ID and AUDIT_REF values within 30 days of deployment — zero credits written via manual override that bypass the APPROVER_ID requirement.

3. **First-response SLA target:** 90% of inbound disputes receive an agent-generated case summary (intake + invoice retrieval + dispute classification) within 4 hours of the dispute contact timestamp, within 60 days of deployment.

---

## 3. KPIs

| KPI | Baseline | Target | Measurement method | Review cadence |
|-----|----------|--------|--------------------|---------------|
| Validity assessment accuracy (% of agent verdicts confirmed correct by human reviewer) | Unknown — no accuracy baseline exists; human verdicts are not currently recorded systematically [A-1] | ≥92% confirmed correct across a rolling 200-case sample | Weekly audit: random sample of 20 cases reviewed by a designated senior billing agent; verdict compared to agent's classification; discrepancies logged in CRM audit field | Weekly |
| Audit trail compliance rate (% of credit records with non-null APPROVER_ID and AUDIT_REF) | Below 100% — Artefact 2 confirms at least one credit applied with no audit log entry; population rate unknown [A-2] | 100% within 30 days of deployment | Daily: APEX_CREDITS export scanned for null or system-placeholder APPROVER_ID/AUDIT_REF values; count of non-compliant records reported to COO | Daily for first 30 days; weekly thereafter |
| First-response time (hours from dispute intake timestamp to agent case summary delivered to human reviewer queue) | Observed: 9-day resolution cycle in Artefact 2 (single case; no population baseline) [A-3] | ≤4 hours for 90% of cases within 60 days | CRM case log: timestamp of dispute intake event vs. timestamp of "agent summary ready" status; exported from CRM reporting API | Weekly |
| HITL rate for validity assessment (% of cases escalated to human reviewer before verdict is finalised) | 100% (all validity assessment is currently human, no agent) [A-4] | ≤60% within 90 days — meaning ≥40% of cases resolved as clear-cut by agent autonomously without human validity review | CRM case type split: "agent-resolved validity" vs. "escalated to human reviewer" count per week; exported from CRM reporting API | Weekly |
| Average handle time per case (human reviewer minutes from case receipt to case closure) | 28 min/case (scenario) | ≤10 min/case within 90 days for cases where agent completed intake + validity assessment | CRM case duration field (assignment timestamp to closure timestamp), filtered to cases with agent-completed summary; sampled weekly | Weekly |

**Confidence threshold validation (applies to validity assessment accuracy KPI and HITL routing):**

The agent uses a confidence score to route validity verdicts: ≥0.85 → autonomous verdict; <0.85 → escalated to human reviewer.

*Pre-deployment validation:* Before deployment, a calibration set of 150 historical disputes (sourced from APEX_DISPUTES_OPEN export history and CRM case archive) will be labelled by two senior billing agents independently. The agent's confidence scores on this set will be compared to human labels. The 0.85 threshold will be adopted only if it achieves ≥90% precision (correct verdicts among high-confidence outputs) on the calibration set. If precision is below 90%, the threshold is raised to the level at which precision reaches 90%, or HITL is applied to all cases until calibration improves. The threshold is not derived from the model's self-reported calibration — it is validated against human labels on domain-specific historical data.

*Post-deployment recalibration trigger:* Weekly precision audit (see Validity assessment accuracy KPI). If rolling 7-day precision falls below 90%, the threshold is immediately raised by 0.05 (i.e., to 0.90) and held there until two consecutive weeks of ≥90% precision are achieved. Threshold changes are logged with the effective date, trigger condition, and new value in a policy version control register maintained by the COO's designated operations lead.

---

## 4. Activity catalog

| Task ID | Task name | Task type | Delegation level | Data required | Tool required | Risk level |
|---------|-----------|-----------|-----------------|---------------|---------------|------------|
| T-001 | Parse inbound dispute contact and extract structured fields | Reasoning | Agent-led + HITL on condition (confidence <0.85 on key field extraction) | Customer email/call text, customer ID | CRM inbound queue API; NLP extraction | Low |
| T-002 | Create or retrieve CRM case linked to dispute | Action | Fully agentic | Customer ID, invoice number extracted from T-001 | CRM REST API (POST/GET case) | Low |
| T-003 | Retrieve invoice and surcharge data from Aurum T-1 batch export | Retrieval | Fully agentic | Invoice number, date range | Aurum CSV file path read access | Low |
| T-004 | Retrieve open disputes history from APEX_DISPUTES_OPEN export | Retrieval | Fully agentic | Customer ID | Aurum APEX_DISPUTES_OPEN CSV read | Low |
| T-005 | Classify dispute type (fuel surcharge / redelivery fee / dimensional weight / other) | Reasoning | Agent-led + HITL on condition (type = "other" → escalate) | Parsed contact text, invoice line items | Internal classification; Aurum CSV | Medium |
| T-006 | Apply Aurum constraint check: confirm invoice line-item correction is not possible in real time | Decision | Fully agentic | Hardcoded constraint rule; no external data required | None — constraint is universal | Low |
| T-007 | Assess charge validity: rule-based verdict for clear cases; confidence-scored for ambiguous | Decision | Agent-led + HITL on condition (confidence <0.85) | Invoice data, surcharge line items, delivery outcome from CRM, customer account history | CRM REST API; Aurum CSV | **High** |
| T-008 | Detect repeat dispute pattern: flag if customer has ≥2 open disputes of same type | Reasoning | Agent-led + HITL on condition (pattern detected → escalate) | APEX_DISPUTES_OPEN data for customer ID | Aurum CSV read | **High** |
| T-009 | Generate structured credit recommendation package for human approver | Generation | Agent-led + HITL on condition (all credit recommendations require human approval) | Validity verdict, dispute type, invoice amount, REASON_CODE mapped from credit policy | Policy registry (version-controlled); CRM case | **High** |
| T-010 | Route credit recommendation to designated approver and await APPROVER_ID | Action | Agent-led + HITL — mandatory human step; agent blocked from proceeding without approval token | Credit recommendation package; designated approver identity | CRM workflow state engine; approval notification | **High** |
| T-011 | Write audit-compliant credit record to APEX_CREDITS once APPROVER_ID is confirmed | Action | Fully agentic (below threshold); Agent-led + HITL (above threshold — second approval required) | CREDIT_AMT (from human approval), APPROVER_ID (from human), REASON_CODE, AUDIT_REF (= CRM case ID), APPLIED_DT | APEX_CREDITS write path [A-5]; confirmation receipt required | **High** |
| T-012 | Notify customer of resolution and expected credit timeline | Generation | Fully agentic | Resolved case details, credit amount, expected statement date | CRM outbound messaging API | Medium |
| T-013 | Update CRM case status to closed; log agent-generated summary and all retrieved evidence | Action | Fully agentic | Case outcome, all retrieved and generated data | CRM REST API | Low |
| T-014 | Flag data-stale condition when invoice is not in T-1 batch (same-day dispute) | Action | Fully agentic | Invoice date vs. T-1 export date | Aurum CSV header timestamp | Medium |

**High-risk tasks requiring escalation trigger entries (T-007, T-008, T-009, T-010, T-011):** All confirmed with corresponding entries in §6.

**T-001 multi-invoice disambiguation rule (added revision 1):**
When the customer contact or CRM intake record references more than one invoice number, the agent applies the following precedence:
1. If the contact contains exactly one recognisable invoice reference (format: INV-YYYY-NNNNN) → use that invoice number; proceed to T-003.
2. If no invoice number is extractable from the contact AND exactly one open dispute for this customer exists in APEX_DISPUTES_OPEN → use that dispute's INVOICE_NO as the authoritative reference.
3. If the contact contains multiple invoice numbers with no single-match resolution → create one CRM case per invoice number and process each as a separate dispute instance.
4. If no invoice number can be extracted and no existing open dispute is found → send a structured acknowledgement requesting the invoice reference; do not proceed to T-003 until the invoice number is confirmed. Log the case as PENDING_INTAKE in CRM.

*Discovery note (for D6):* The reliability of invoice reference extraction depends on the inbound channel (email vs. phone transcription vs. CRM portal). Rule 1 is robust for email; transcriptions may require lower-confidence handling. Confirm the primary inbound channel with Apex IT — see D6 question on intake channel (Q-BUILD-3 from Build_loop_analysis.md).

---

## 4b. T-007 validity assessment rule framework

**Added:** D4 revision 1, 2026-05-06 (D4A build loop — highest-priority spec gap)

T-007 produces a validity verdict using a two-step rule-based check for each dispute type before falling back to a confidence-scored assessment. The rule-based path targets HIGH confidence (≥ 0.90); the fallback path produces verdicts in the 0.50–0.89 range. All HITL thresholds apply as specified in §3 (default 0.85).

**Pre-conditions for all dispute types (checks must complete before T-007 runs):**
- T-014 must confirm the invoice is in the T-1 batch. If stale: do not proceed; escalate per ET-004.
- T-008 must confirm no repeat pattern (≥2 open disputes, same type) exists. If pattern detected: do not proceed to verdict; escalate per ET-005.
- T-006 constraint check confirms real-time invoice correction is not possible (universal; hardcoded).

---

### FUEL_SURCH_DAMAGE

**Context:** Customer disputes a fuel surcharge applied to an invoice involving a damaged delivery. Aurum calculates fuel surcharges automatically (Artefact 2: "the billing system cannot adjust individual fuel surcharge line items"). The observed resolution in Artefact 2 is a GOODWILL credit (~50% of disputed amount), not a FUEL_RECALC — confirming the standard path is a discretionary partial credit, not a calculation correction. This means true calculation errors (Aurum formula bugs) are expected to be rare; most FUEL_SURCH_DAMAGE cases are policy disputes, not arithmetic disputes.

**Step 1 — Fuel surcharge calculation verification:**
Retrieve `AMT_FUEL_SURCH` from the invoice in APEX_BILL_DAILY. Compare to the expected surcharge using Apex's fuel surcharge rate schedule (if available in the policy registry).
- If rate schedule is available AND `AMT_FUEL_SURCH` ≠ expected → verdict: **CALCULATION_ERROR — charge invalid** | confidence: 0.92 | REASON_CODE: FUEL_RECALC
- If `AMT_FUEL_SURCH` = expected, or rate schedule is unavailable → proceed to Step 2

> **[REQUIRES CUSTOMER INPUT — Q-V2, for D6]:** Where is Apex's fuel surcharge rate schedule documented? Is it accessible to the agent (policy registry, CRM field, Aurum configuration parameter)? Without it, calculation verification is not possible and all FUEL_SURCH_DAMAGE cases proceed to Step 2.

**Step 2 — Delivery damage context check:**
Retrieve delivery outcome from the CRM case record (field populated by Driver App scan-on-delivery or dispatcher notes at exception resolution).
- If no delivery outcome field is recorded in CRM → verdict: **UNVERIFIABLE** | confidence: 0.45 | route: HITL
- If delivery outcome = NOT_DAMAGED or DELIVERED_CONFIRMED → verdict: **CHARGE_VALID — damage not confirmed in system** | confidence: 0.80 | route: HITL (below threshold; human reviewer confirms before closing)
- If delivery outcome = DAMAGED, REFUSED_DAMAGE, or equivalent → verdict: **DAMAGE_CONFIRMED — policy determination required** | confidence: 0.60 | route: HITL

> **[REQUIRES CUSTOMER INPUT — Q-V1, for D6]:** When a damage claim is confirmed in the CRM/Driver App record, does Apex policy: (a) automatically waive the fuel surcharge in full? (b) apply a standard partial credit (e.g., 50% of AMT_FUEL_SURCH)? (c) require manager discretion? This answer determines whether the DAMAGE_CONFIRMED verdict can become a HIGH-confidence autonomous verdict or must always route to HITL.

> **[REQUIRES CUSTOMER INPUT — Q-V3, for D6]:** What CRM field captures the delivery outcome (e.g., DAMAGED / DELIVERED_OK / REFUSED)? How consistently is this field populated by drivers across all routes? Low population rate means Step 2 returns UNVERIFIABLE frequently, keeping HITL rates high.

*Interim baseline (not to be operationalised without policy approval — D4 §8 Hard Stop 3):* Artefact 2 shows Sandra applying a GOODWILL credit of ~50% of the disputed fuel surcharge. This is recorded as a baseline for the policy formalisation conversation (D6 Q-V1), not as an agent rule.

---

### DIM_WEIGHT

**Context:** Customer disputes a dimensional weight charge. Dimensional weight is calculated as (L × W × H) ÷ dimensional factor × per-unit rate. A calculation error is verifiable if package dimensions and the formula are available.

**Step 1 — Dimensional weight calculation verification:**
Retrieve the DIM_WEIGHT charge amount from the invoice. Compare to the expected dimensional weight charge using Apex's formula.

> **[REQUIRES CUSTOMER INPUT — Q-V4, for D6]:** Does APEX_BILL_DAILY contain a dedicated dimensional weight charge field, or is it embedded in AMT_NET? The current artefact shows DISPUTE_AMT = £88.00 for a DIM_WEIGHT dispute but no dedicated DIM_WEIGHT field is visible in the bill daily schema. Confirm the field name.

> **[REQUIRES CUSTOMER INPUT — Q-V5, for D6]:** What dimensional weight formula does Apex use? Specifically: what dimensional factor (divisor) and per-unit rate? Without this, calculation verification cannot be built.

If formula and dimension data are available:
- If calculated DIM_WEIGHT charge ≠ charged amount (outside ±£1.00 tolerance) → verdict: **CALCULATION_ERROR — charge invalid** | confidence: 0.92 | REASON_CODE: INV_CORR
- If calculated DIM_WEIGHT charge = charged amount → verdict: **CHARGE_VALID — calculation confirmed correct** | confidence: 0.90 | route: Autonomous (if customer claims wrong dimensions, route to Step 2)

**Step 2 — Package specification conflict (triggered only if customer disputes the declared dimensions):**
Retrieve Driver App scan data or shipper-declared dimension records from CRM.
- If Driver App dimension record matches invoice → verdict: **CHARGE_VALID — dimensions confirmed by scan** | confidence: 0.88 | route: HITL (near-threshold; human confirms)
- If Driver App data is unavailable or conflicts with invoice → verdict: **AMBIGUOUS — dimension evidence conflicting** | confidence: 0.55 | route: HITL

---

### REDELIVERY_FEE

**Context:** Customer disputes a fee charged for a redelivery attempt. A redelivery fee is only valid if a redelivery was actually attempted and recorded in the system.

**Step 1 — Service confirmation (was a redelivery attempted?):**
Retrieve delivery history for the invoice from CRM case records and Driver App delivery scan events.
- If no redelivery attempt is recorded in CRM or Driver App for this invoice → verdict: **CHARGE_INVALID — no redelivery attempt on record** | confidence: 0.92 | REASON_CODE: INV_CORR
- If redelivery attempt is confirmed → proceed to Step 2

**Step 2 — Reason for initial delivery failure:**
Retrieve the reason for the initial delivery failure from CRM case notes or Driver App exception log.
- If reason = Apex-fault (driver error, wrong address used, incorrect depot assignment, Apex system error) → verdict: **CHARGE_DISPUTE — initial failure was Apex-fault** | confidence: 0.70 | route: HITL

> **[REQUIRES CUSTOMER INPUT — Q-V6, for D6]:** Does Apex waive redelivery fees when the initial delivery failure was caused by an Apex error? If yes, this becomes a HIGH-confidence autonomous verdict (confidence raised to 0.92; REASON_CODE: GOODWILL or INV_CORR). If subject to manager discretion, it remains HITL.

- If reason = Recipient-fault (not home, refused access, incorrect delivery address provided by customer, access restrictions not communicated) → verdict: **CHARGE_VALID — redelivery required due to recipient action** | confidence: 0.82 | route: HITL (near-threshold; human confirms)
- If reason is not recorded in CRM → verdict: **AMBIGUOUS — failure reason not documented** | confidence: 0.50 | route: HITL

---

### Confidence score assignment summary

| Band | Route | Typical scenario |
|---|---|---|
| 0.90–1.00 | Autonomous | Confirmed calculation error (arithmetic check); or charge confirmed valid by matching records from two system sources |
| 0.80–0.89 | HITL | Strong evidence for validity/invalidity but one ambiguous factor; human reviewer confirms |
| 0.50–0.79 | HITL | Evidence present but conflicting or incomplete; human assesses with agent-prepared evidence package |
| < 0.50 | HITL | Insufficient evidence to form a verdict; human assesses from scratch; agent provides only the structured evidence package |

---

### Customer discovery questions reserved for D6

The following questions cannot be answered from the scenario alone. Each would materially change the agent's autonomy level for the relevant dispute type — in some cases moving cases from HITL to autonomous.

| Question ID | Question | Design impact if answered |
|---|---|---|
| Q-V1 | When a damaged delivery is confirmed in CRM/Driver App, does Apex policy waive the fuel surcharge in full, partially, or at discretion? | Full or standard-partial waiver → FUEL_SURCH_DAMAGE DAMAGE_CONFIRMED becomes HIGH-confidence autonomous; HITL rate drops for this type |
| Q-V2 | Where is Apex's fuel surcharge rate schedule documented and is it accessible to the agent? | If accessible → Step 1 calculation check is buildable; enables autonomous CALCULATION_ERROR verdicts |
| Q-V3 | What CRM field captures delivery outcome and how consistently is it populated by drivers? | Low population rate means Step 2 UNVERIFIABLE is frequent; high population rate enables higher confidence scores |
| Q-V4 | Does APEX_BILL_DAILY contain a dedicated DIM_WEIGHT charge field or is it embedded in AMT_NET? | Required to build DIM_WEIGHT calculation verification step |
| Q-V5 | What is Apex's dimensional weight formula (dimensional factor and per-unit rate)? | Required to build DIM_WEIGHT calculation verification step |
| Q-V6 | Does Apex waive redelivery fees when the initial failure was Apex's fault? | If yes → REDELIVERY_FEE Apex-fault cases become HIGH-confidence autonomous (confidence: 0.92) |

---

## 5. Autonomy matrix

**AGENT DECIDES ALONE (no HITL required):**
- Parse inbound dispute contact and extract structured fields (when extraction confidence ≥ 0.85 on all required fields)
- Create or retrieve CRM case for inbound dispute
- Retrieve invoice, surcharge, and dispute history data from Aurum T-1 batch exports
- Apply the Aurum constraint check (invoice line-item correction not possible in real time — this constraint is universal and requires no judgment)
- Classify dispute type as fuel surcharge, redelivery fee, or dimensional weight when classification confidence ≥ 0.85
- Detect and flag a repeat dispute pattern (≥2 open disputes, same customer, same type) as an escalation signal — does not close or act on the pattern itself
- Flag a case as data-stale when the relevant invoice is not in the current T-1 batch
- Send standard acknowledgement to customer within 4 hours of intake ("Your dispute is being reviewed — you will receive a response within [X] business days")
- Update CRM case fields with retrieved data, agent-generated summary, and confidence scores
- Write credit record to APEX_CREDITS after APPROVER_ID and human-confirmed CREDIT_AMT are present in workflow state and write confirmation is received

**AGENT ACTS, HUMAN NOTIFIED AFTER:**
- Create a new CRM case for an inbound dispute where no existing case is found (human notified via CRM case assignment notification within 15 minutes)
- Attach Aurum batch export data as supporting evidence to the case record
- Log data-stale flag to CRM case and notify assigned billing agent (automated notification only; agent does not proceed to validity assessment until data is confirmed available)

**AGENT PROPOSES, HUMAN APPROVES BEFORE ACTION:**
- **Credit record write [PRIMARY GOVERNANCE GATE]:** The agent prepares a complete credit record containing CREDIT_AMT (proposed by human during approval), REASON_CODE (from policy), and a pre-populated AUDIT_REF (= CRM case ID). The record is not written to APEX_CREDITS until: (a) the designated approver has provided their named APPROVER_ID via an authenticated CRM workflow action, and (b) the CREDIT_AMT has been explicitly confirmed by the approver. The APEX_CREDITS write is system-blocked if APPROVER_ID is null or equals a system-generated placeholder — this is a workflow state enforcement, not a procedural expectation. See enforcement mechanism note below.
- Validity verdict for ambiguous cases (confidence < 0.85): agent presents its reasoning, the supporting invoice evidence, and the confidence score to the human reviewer; the reviewer confirms or overrides before the case proceeds to credit recommendation
- Any credit recommendation above the approval threshold [ASSUMPTION A-6: threshold value TBD by COO/finance prior to deployment; flagged as prerequisite item]: agent prepares the full recommendation package; a COO-designated senior approver must confirm before any credit record is written

**HUMAN TAKES OVER (agent supports only):**
- The disputed charge involves a physical damage claim requiring assessment of driver photos, delivery condition report, or third-party damage evidence not available in any integrated system
- The customer explicitly requests escalation to a named senior manager or the COO
- The dispute references a formal legal notice, regulatory complaint, or ombudsman referral
- The dispute type is not in the defined taxonomy (fuel surcharge, redelivery fee, dimensional weight) — classified as "unknown dispute type" and handed to a senior billing agent with the agent's partial intake summary
- The same invoice has been disputed and credited more than twice — agent provides full dispute history; human senior agent determines whether a root cause correction is needed
- The customer's account has been flagged as inactive, in collections, or under a formal payment plan in the APEX_CUSTOMER_MASTER export

**Enforcement mechanism — primary approval gate:**
The credit record write gate is **system-enforced via workflow state**: the CRM workflow engine holds the case in "PENDING_APPROVAL" state until a human agent performs an authenticated approval action (API call with user token + CREDIT_AMT input). The APPROVER_ID field is populated only by the authenticated token — the agent has no write permission to this field. The APEX_CREDITS write API call is issued only by the workflow engine after the state transitions to "APPROVED," never by the agent directly. If the system were to allow the agent to write the APPROVER_ID field — e.g., due to a permissions misconfiguration — this would become a procedure-dependent control rather than a system-enforced one, and would represent a governance risk that must be logged and remediated. This is confirmed in FM-5 below.

---

## 6. Escalation triggers

| Trigger ID | Condition | Escalate to | What the agent provides at escalation | Response SLA |
|---|---|---|---|---|
| ET-001 | Validity assessment confidence score < 0.85 for any field in the verdict output | Assigned billing agent (human reviewer) | Case summary with invoice data, surcharge calculation evidence, preliminary verdict with confidence score, and specific reason confidence is below threshold (which evidence field is ambiguous) | 2 business hours |
| ET-002 | Dispute type classification returns "other" — input does not match fuel surcharge, redelivery fee, or dimensional weight taxonomy | Senior billing agent | Customer contact text, invoice data, "unknown dispute type" flag, and a list of the three standard types with the agent's confidence scores for each | 4 business hours |
| ET-003 | Customer contact includes explicit reference to legal action, regulatory complaint, ombudsman referral, or formal written notice | COO or designated legal contact | Full case history including all prior contacts, all prior dispute resolutions for this customer ID, and a verbatim extract of the relevant language from the customer's message | Immediate — same business day |
| ET-004 | Invoice not found in current T-1 Aurum batch export (same-day invoice, data not yet available) | Assigned billing agent | Customer contact, CRM case ID, invoice number, and "T-1 data unavailable" flag with the T-1 export timestamp | 4 business hours |
| ET-005 | Repeat dispute pattern: customer has ≥2 open disputes of the same dispute type in APEX_DISPUTES_OPEN at time of intake | Senior billing agent (or equivalent of Sandra W. role) | Dispute history table (all open and recently closed disputes for this customer), account summary from APEX_CUSTOMER_MASTER, repeat pattern flag | 1 business day |
| ET-006 | Credit recommendation amount exceeds approval threshold [ASSUMPTION A-6: threshold TBD] | COO-designated senior approver | Full credit recommendation package: validity verdict with evidence, proposed CREDIT_AMT, REASON_CODE, AUDIT_REF (CRM case ID), and a summary of the case history | 1 business day |
| ET-007 | APPROVER_ID not provided within 24 hours of credit recommendation routing (case remains in PENDING_APPROVAL state) | Senior billing agent (escalation owner) | Reminder notification with case summary, outstanding approval action required, and case age from intake | Immediate — triggers escalation notification; human must act within 4 business hours |
| ET-008 | APEX_CREDITS write confirmation not received within 60 minutes of APPROVED workflow state transition | Operations lead | Case ID, approved credit record content, write attempt log, error status | Immediate |

---

## 7. Failure modes

> **Failure Mode FM-1: False validity verdict — valid charge classified as invalid (false negative)**
> **What a bad output looks like:** The agent classifies a correctly calculated fuel surcharge as invalid (e.g., confusing a damage-complaint context with a calculation-error context), generates a credit recommendation for a charge the customer actually owes, and the human approver confirms the credit without scrutinising the validity verdict.
> **Consequence:** Apex issues an unwarranted credit. Financial loss at the individual case level (~£100–£350 per dispute based on APEX_DISPUTES_OPEN amounts). At scale, if systematic: the agent erodes Apex's billing accuracy and trains customers that disputing a charge reliably produces a credit regardless of merit.
> **Detection:** Weekly precision audit (20-case sample reviewed by designated senior billing agent). Systematic detection: if credit issuance rate for any dispute type exceeds the prior 30-day rolling average by >25% in a given week, an automated alert is generated to the COO's operations lead. Typical detection latency: 7–14 days for systematic errors; individual errors may take longer if the human approver does not document their rationale.
> **Recovery path:** For individual confirmed false positives: annotate the CRM case with the correct verdict, log the credit as a known-overpayment in the APEX_CREDITS record, and initiate a credit adjustment ticket with the Aurum team if the account balance requires correction. For systematic errors: trigger FM-2 threshold retuning protocol; re-audit all cases from the preceding week where the same dispute type was classified as invalid at high confidence.

> **Failure Mode FM-2: Systematic confidence miscalibration — high-confidence verdicts are frequently wrong**
> **What a bad output looks like:** The agent consistently assigns confidence scores ≥ 0.85 to validity verdicts that are incorrect — routing cases that should have been escalated to human review directly to the autonomous path. The human reviewer never sees these cases; errors accumulate. No individual case triggers an alert because each appears as a single correct-looking verdict.
> **Consequence:** The weekly precision audit detects the pattern only after 7–14 days of incorrect autonomous resolution. Depending on case volume, 40–80 incorrect verdicts may have been generated before detection. If credits have already been written (via approved-but-wrong credit amounts), financial exposure accumulates.
> **Detection:** Weekly precision audit: if rolling 7-day precision of high-confidence (≥0.85) verdicts falls below 90%, automated alert is generated. Threshold: 2 consecutive weekly audits with precision < 90% triggers mandatory threshold retuning. Threshold retuning process: the confidence threshold is raised by 0.05 increments until two consecutive weekly audits achieve ≥90% precision; if raising to 0.95 does not restore precision, HITL is applied to 100% of validity assessments until root cause is diagnosed.
> **Recovery path:** Immediately raise threshold to 0.90 and notify the COO's operations lead. Re-audit all cases from the preceding 14 days where high-confidence verdicts were applied autonomously; human reviewer validates each. For confirmed incorrect verdicts: apply FM-1 recovery path per case. Document the miscalibration event, new threshold, and recovery date in the policy version control register. Investigate whether the miscalibration is dispute-type-specific (e.g., only affects dimensional weight disputes) and apply type-specific threshold overrides if warranted.

> **Failure Mode FM-3: Audit evidence incompleteness — credit record lacks defensible reasoning chain**
> **What a bad output looks like:** The agent writes a credit record to APEX_CREDITS with APPROVER_ID and CREDIT_AMT populated but AUDIT_REF is a system-generated placeholder (e.g., "AUTO-BDRA-XXXX") rather than the CRM case ID, or the REASON_CODE is a generic fallback ("GOODWILL") without a specific sub-category. The credit record cannot be traced to a specific dispute, specific evidence review, or specific approval action.
> **Consequence:** During an internal or external audit, the credit record cannot be defended — the approver cannot demonstrate what they approved, what evidence they reviewed, or why the credit amount was chosen. This is the exact compliance exposure documented in Artefact 2 (Sandra's £170 credit with no audit log entry). At audit-findings level: financial control failure finding; regulatory risk if the audit is part of a formal compliance review.
> **Detection:** Daily automated scan of APEX_CREDITS export: flag any record where AUDIT_REF does not match a known CRM case ID, REASON_CODE is not a defined taxonomy value, or APPROVER_ID is a non-human system identifier. Alert to operations lead. Detection latency: ≤24 hours (next daily export).
> **What the output must contain to be audit-defensible:** Each credit record must include: (a) AUDIT_REF = CRM case ID (not a system placeholder); (b) APPROVER_ID = named human approver's authenticated user ID; (c) REASON_CODE = approved taxonomy value (FUEL_RECALC, GOODWILL, INV_CORR, or other formally defined code); (d) CRM case record must contain the agent's validity assessment with confidence score, the Aurum invoice data retrieved, and the approver's confirmation action timestamp. If any of these is absent, the approver must not accept the credit record and must return the case to the agent for re-preparation. The approver should reject any credit recommendation that does not include a navigable link to the CRM case with full supporting evidence.
> **Recovery path:** For each flagged record: create a correction case in CRM linking the incomplete APEX_CREDITS record to its originating dispute (if identifiable). Notify the original approver to review and re-sign with a corrected AUDIT_REF. If the originating case cannot be identified, log as an irreconcilable credit and escalate to the COO for review. Fix the AUDIT_REF generation logic in the agent before the next deployment cycle.

> **Failure Mode FM-4: Stale data validity verdict — agent assesses dispute using the wrong invoice**
> **What a bad output looks like:** A same-day dispute arrives for invoice INV-2026-05100. The T-1 batch does not contain this invoice. However, the same customer (C-04451) has an older invoice (INV-2026-04318) in the batch. The agent retrieves the older invoice, does not flag the mismatch, and produces a validity verdict based on the wrong invoice data.
> **Consequence:** The agent's validity assessment is entirely incorrect — it is assessing the wrong charge. If the human reviewer does not notice the invoice date mismatch, an incorrect credit recommendation flows to approval and a credit is issued against the wrong dispute.
> **Detection:** The agent must log the invoice date retrieved against the dispute date stated in the customer contact. If the retrieved invoice date is > 1 business day older than the dispute contact date, the agent must flag "invoice date mismatch — validate manually" and escalate per ET-004. This check must run before any validity assessment is generated. Detection is immediate if the check is implemented; the failure mode occurs only if the check is absent or bypassed.
> **Recovery path:** If a mismatch-flagged case was somehow resolved without human review: invalidate the credit record if it has been written, initiate an Aurum correction ticket if needed, re-open the case for correct assessment with the correct invoice once the T-1 batch catches up (typically next business day, 02:00–04:00 GMT window).

> **Failure Mode FM-5: Approval gate bypass — APPROVER_ID field writeable by agent due to permissions misconfiguration**
> **What a bad output looks like:** A permissions misconfiguration in the CRM workflow engine allows the agent to populate the APPROVER_ID field with a system-generated identifier (e.g., "BDRA-SYSTEM-01"). Credits are written to APEX_CREDITS with a system ID in the APPROVER_ID field, bypassing the human approval requirement entirely.
> **Consequence:** The primary governance constraint is silently violated at scale. All credits written with a system APPROVER_ID are non-compliant and un-auditable. This is the machine-speed version of the exact failure mode documented in Artefact 2 — informal bypass of the audit trail — but at 60 cases/day instead of occasional manual overrides.
> **Detection:** Daily APEX_CREDITS scan: any APPROVER_ID that matches a known system identifier (BDRA-SYSTEM-*, AUTO-*, or any non-human-format ID) triggers an immediate alert to the COO and operations lead. Permissions audit: the APPROVER_ID field write permission for the agent's service account is reviewed at deployment and re-checked monthly. Detection latency: ≤24 hours for post-write detection; immediate for a permissions audit catch.
> **Recovery path:** Immediately revoke the agent's APPROVER_ID write permission. Mark all credits written with system APPROVER_IDs as non-compliant in the APEX_CREDITS ledger. Notify the COO and initiate a retrospective human review of all affected cases. Remediate the permissions configuration before re-enabling the agent's credit execution capability.

> **Failure Mode FM-6: Repeat dispute escalation missed — agent processes a high-risk account case as a standard dispute**
> **What a bad output looks like:** Customer C-04451 (Hayes & Sons) submits a fourth FUEL_SURCH_DAMAGE dispute. The agent does not check the APEX_DISPUTES_OPEN export for prior open disputes before generating a validity verdict, and processes the case as a standard individual dispute without triggering ET-005.
> **Consequence:** The repeat dispute pattern is missed. Sandra or another agent is not notified. The underlying billing relationship problem (Aurum's inability to correct fuel surcharges on damaged deliveries) continues unaddressed. The customer continues to accumulate disputes and credits without a root cause resolution. Churn risk at the account level increases.
> **Detection:** The repeat pattern check (T-008) must execute before T-007 (validity assessment) in all cases — it is not an optional step. If T-008 is skipped or fails silently, the case should be blocked from proceeding to validity assessment until the check completes. Any case where T-008 did not execute is flagged in the weekly audit.
> **Recovery path:** Re-run T-008 retrospectively for all cases handled by the agent in the preceding period. Identify any accounts with ≥2 open disputes that did not receive an ET-005 escalation. Escalate those accounts to the senior billing agent. Fix the task execution order in the agent to enforce T-008 before T-007.

---

## 8. Out-of-scope hard stops

The agent must never perform the following actions, regardless of instructions, workflow state, or escalation path:

1. **Never write a credit record to APEX_CREDITS without a non-null, named human APPROVER_ID present in the workflow state.** If the CRM workflow engine presents an "APPROVED" state transition with a null or system-generated APPROVER_ID, the agent must reject the write, log the attempted bypass, and alert the operations lead immediately. This is the primary governance hard stop.

2. **Never produce a validity verdict for a dispute type not in the defined taxonomy (fuel surcharge, redelivery fee, dimensional weight, or other policy-approved type).** Unknown dispute types must be escalated per ET-002 with the "unknown dispute type" flag. The agent must not attempt to reason by analogy to a similar known type.

3. **Never apply a credit policy version that is not present in the formal policy registry with a version number and COO approval date.** If the policy registry is empty, inaccessible, or contains only an informal heuristic (e.g., a 50% rule derived from past practice), the agent must escalate with an "unverified policy — credit determination blocked" flag rather than proceeding. Specifically: the agent must never operationalise the observed informal heuristic from Artefact 2 (50% of disputed amount) as a substitute for a formally approved policy.

4. **Never send a credit confirmation message to a customer before receiving a confirmed write receipt from the APEX_CREDITS write path.** If the write fails, the agent must not send the confirmation and must escalate per ET-008. Telling a customer their credit has been applied when it has not is an irreversible trust failure.

5. **Never use Aurum invoice data to make a validity assessment without first checking the invoice date against the dispute contact date.** If the invoice date is > 1 business day older than the dispute contact date, the agent must flag the mismatch and escalate per ET-004 before generating any validity verdict. The data-stale check is not optional.

6. **Never close a case for a customer with ≥2 open disputes of the same type without triggering ET-005 and receiving confirmation that the senior billing agent has acknowledged the escalation.** The agent must not autonomously resolve cases that indicate a systemic account-level billing problem, regardless of the individual case validity verdict's confidence score.

---

## 9. Assumption log

> **Assumption A-1:** No systematic accuracy baseline exists for human validity assessments — individual billing agents do not currently record their reasoning or confidence in the CRM case record.
> **Why it matters:** The accuracy KPI baseline must be established empirically during the calibration phase rather than read from existing data. This affects the pre-deployment timeline.
> **If wrong:** If CRM case records contain structured decision rationale (unlikely given the informal process described in D0D), the baseline can be derived from historical data, shortening the calibration phase.
> **Confidence:** High — the scenario describes informal practice without documentation.

> **Assumption A-2:** The audit trail compliance rate is materially below 100% at the population level, consistent with the single confirmed miss in Artefact 2 and the domain-typical gap identified in D0A.
> **Why it matters:** Sets the baseline for the audit trail KPI. If most credits are already logged correctly, the KPI target is already nearly met.
> **If wrong:** If APEX_CREDITS already captures >95% of credits correctly and Artefact 2 is an outlier, the compliance improvement is smaller than the KPI implies.
> **Confidence:** Medium — one confirmed miss; population rate unknown.

> **Assumption A-3:** The 9-day resolution cycle observed in Artefact 2 (Hayes & Sons) is representative of a broader pattern, not an outlier.
> **Why it matters:** Sets the first-response time baseline. If average resolution is 2–3 days, the improvement claim is smaller.
> **If wrong:** Pull 90-day CRM case age distribution for WS4 disputes before finalising baseline.
> **Confidence:** Medium — APEX_DISPUTES_OPEN shows disputes open for 30+ days alongside newer cases, suggesting high variance rather than a consistent short-resolution baseline.

> **Assumption A-4:** Current HITL rate for validity assessment is 100% (fully human), giving the agent a meaningful reduction target of ≤60%.
> **Why it matters:** If some structured automation already exists (e.g., a CRM macro that pre-fills invoice data), the baseline HITL rate may already be below 100%, changing the improvement claim.
> **If wrong:** Measure actual current HITL rate during pilot deployment before committing to the 60% target.
> **Confidence:** High — the scenario describes no structured automation in the billing dispute path.

> **Assumption A-5:** A programmatic write path to APEX_CREDITS exists (or can be established) that does not require the manual Aurum support ticket process — enabling the agent to write credit records after approval without the 48-hour Aurum turnaround.
> **Why it matters:** If no write path exists and every credit still requires a manual Aurum ticket, C-8 (Fully Agentic credit execution) cannot be delivered; the agent can only prepare records for manual submission. This would change the handle-time reduction from 28 min to ~8 min to a smaller improvement.
> **If wrong:** The credit execution scope narrows to record preparation only; the 48-hour Aurum turnaround remains; TCO saving falls by approximately 30%.
> **Confidence:** Low — **STATUS: BLOCKING GAP (confirmed D5 G-1, revision 1).** "Batch-file exports only" and "no real-time API" are confirmed constraints. The D4A build loop confirmed T-011 cannot be built without resolving this. Three fallback options exist (direct DB write / pre-populated auto-ticket / manual-submit with agent-prepared record — see D5 §3 G-1). Must be resolved with Apex IT and Aurum vendor before build proceeds to T-011. This is the highest-consequence unresolved assumption in the spec.

> **Assumption A-6:** A formal credit policy with explicit threshold values (below which the standard approver can approve; above which a COO-designated approver is required) will be defined and approved before agent deployment.
> **Why it matters:** Without a credit policy, the credit amount determination step (C-7) cannot be handed off to the agent's recommendation logic, and the approval threshold for ET-006 cannot be set. The agent's credit recommendation capability is blocked entirely.
> **If wrong:** If the policy is not defined before deployment, the agent scope is limited to intake, validity assessment, and audit record preparation — it cannot generate a credit recommendation. The handle-time target of ≤10 min/case may still be achievable for the triage and data assembly portion, but the full case closure efficiency gain is not.
> **Confidence:** Medium — formalising a credit policy is a standard business task; no scenario evidence suggests it would be blocked. Confirm with COO in stakeholder session.

---

## 10. Revision log

| Revision | Date | Author | Changes |
|---|---|---|---|
| 0 (original) | 2026-05-06 | FDE assessment | Initial D4 draft produced from D3 analysis |
| 1 | 2026-05-06 | FDE assessment (D4A build loop) | Added T-001 multi-invoice disambiguation rule; added §4b T-007 validity assessment rule framework (structural rules for all three dispute types with confidence assignments and outstanding customer discovery questions Q-V1 through Q-V6); updated A-5 status to BLOCKING GAP per D5 G-1 confirmation |

### Remaining spec gaps requiring customer discovery (D6)

The following items could not be resolved from the scenario or artefacts alone. Each is a question for the D6 stakeholder session.

| Gap ID | System/area | Question | What changes in the design |
|---|---|---|---|
| Q-BUILD-1 | Aurum Billing | Does a programmatic write path to APEX_CREDITS exist that does not require the 48-hour manual support ticket? | Determines whether T-011 (Fully Agentic credit execution) can be built; without it, scope is limited to record preparation |
| Q-BUILD-2 | CRM / Salesforce | Is Salesforce configured with Approval Processes or Flow? Can the PENDING_APPROVAL → APPROVED transition be enforced via an authenticated API action? | Determines whether the governance gate is system-enforced (as required) or degrades to procedure-dependent |
| Q-BUILD-3 | CRM / intake | What is the primary intake channel for billing disputes — email, inbound CRM portal, phone, or a combination? | Determines T-001 trigger mechanism and extraction reliability |
| Q-BUILD-6 | Credit policy | What credit amount threshold determines whether the standard approver or a COO-designated senior approver is required? | Required to configure ET-006 routing logic |
| Q-BUILD-8 | Aurum Billing | What fields and account status values does the APEX_CUSTOMER_MASTER export contain? | Required to build account status check in the Autonomy matrix Human Takes Over condition |
| Q-V1 | Credit policy | When a damage claim is confirmed, does Apex waive fuel surcharges in full, at 50%, or at discretion? | Determines whether FUEL_SURCH_DAMAGE DAMAGE_CONFIRMED becomes an autonomous verdict or always requires HITL |
| Q-V2 | Aurum / policy | Where is Apex's fuel surcharge rate schedule documented and is it machine-readable? | Required to build Step 1 calculation verification for FUEL_SURCH_DAMAGE |
| Q-V3 | CRM / Driver App | What field captures delivery outcome and how consistently is it populated? | Determines confidence levels for FUEL_SURCH_DAMAGE Step 2 and REDELIVERY_FEE Step 1 |
| Q-V4 | Aurum Billing | Does APEX_BILL_DAILY contain a dedicated DIM_WEIGHT charge field or is it embedded in AMT_NET? | Required to build DIM_WEIGHT calculation verification |
| Q-V5 | Credit policy / ops | What is Apex's dimensional weight formula (factor and rate)? | Required to build DIM_WEIGHT calculation verification |
| Q-V6 | Credit policy / ops | Does Apex waive redelivery fees when the initial failure was Apex's fault? | Determines whether REDELIVERY_FEE Apex-fault cases become autonomous verdicts |
