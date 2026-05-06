# D5 — System/Data Inventory: Apex Billing Dispute Resolution Agent

**Produced:** 2026-05-06
**Status:** Draft — awaiting FDE review
**Agent:** Apex Billing Dispute Resolution Agent (BDRA), WS4 Billing Disputes

---

## 0. Executive summary

- The Salesforce-based CRM is the most critical integration: it provides the inbound dispute case queue, customer account history, and delivery outcome evidence that the agent needs to initiate any case — if the CRM REST API is unavailable or the agent's service account lacks case-queue read access, the agent cannot receive any inbound dispute and the entire pipeline is blocked before T-001 executes.
- The most significant gap in this inventory is the APEX_CREDITS write path: the scenario confirms Aurum Billing has no real-time API and all invoice modifications require a manual 48-hour ticket to the Aurum support team, but whether a programmatic write path to the credit ledger can be established outside that manual ticket process is unknown (D4 Assumption A-5, confidence: Low) — if no write path exists, C-8 (Fully Agentic credit execution) cannot be delivered, the audit trail compliance KPI cannot be system-enforced, and the primary governance hard stop degrades from system-enforced to procedure-dependent.
- The Aurum CSV ingestion layer, once built with schema-change detection, is the highest-compounding integration: it provides the invoice, disputes, and reconciliation data pipeline that both the BDRA and any future WS1 Delivery Exception Agent or accounts-receivable reconciliation agent would share, meaning the first build amortises across at least two subsequent agents.

---

## 0b. Table of contents

- [0. Executive summary](#0-executive-summary)
- [0b. Table of contents](#0b-table-of-contents)
- [1. Data and system requirements (from agent design)](#1-data-and-system-requirements-from-agent-design)
- [2. System and data inventory table](#2-system-and-data-inventory-table)
- [3. Gap analysis](#3-gap-analysis)
- [4. Risk register](#4-risk-register)
- [5. Context engineering design](#5-context-engineering-design)
  - [5b. Pre-deployment prerequisite checklist](#5b-pre-deployment-prerequisite-checklist)
- [6. Compounding opportunities](#6-compounding-opportunities)

---

## 1. Data and system requirements (from agent design)

Requirements derived directly from the D4 activity catalog (T-001 through T-014). No requirements are invented independently.

### Input data

| Data required | Derived from task | Granularity | Latency requirement |
|---|---|---|---|
| Inbound dispute contact text (customer email / call transcription) | T-001: Parse inbound dispute contact | Case-level; full text including invoice reference and description of charge disputed | Real-time — agent triggers on case arrival in CRM queue |
| Customer ID and invoice number extracted from contact | T-001 output / T-002 input | Record-level field | Derived at intake; no external latency |
| Invoice headers and fuel surcharge line items | T-003: Retrieve invoice data from Aurum T-1 batch | Invoice-level; individual line items including AMT_FUEL_SURCH, AMT_REDELIV, DIM_WEIGHT fields | Batch-loaded — available daily after 02:00–04:00 GMT; T-1 lag (yesterday's invoices only) |
| Open disputes history by customer ID | T-004: Retrieve APEX_DISPUTES_OPEN | Customer-level; all open disputes, type, assigned agent | Batch-loaded daily; T-1 lag |
| Reconciliation file with DISPUTE_OPEN flags | T-014: Detect data-stale condition | Invoice-level; DISPUTE_OPEN flag per invoice | Batch-loaded daily; T-2 lag (two days behind invoice generation) |
| Customer account status (active / inactive / collections / payment plan) | Autonomy matrix — Human Takes Over condition | Customer-level; account status field | Batch-loaded monthly (first of month); up to 30-day staleness |
| Delivery outcome data from CRM case history | T-007: Charge validity assessment | Case-level; delivery confirmation, scan-on-delivery result, driver notes | On-demand retrieval from CRM REST API; current at time of query |

### Reference data

| Data required | Derived from task | Granularity | Latency requirement |
|---|---|---|---|
| Formal credit policy: REASON_CODE taxonomy, approval thresholds, dispute-type validity rules | T-005 (classification), T-007 (validity), T-009 (recommendation) | Clause-level; structured rules with explicit thresholds | On-demand retrieval from policy registry; versioned; updated only on COO-approved revision |
| Aurum export schema definitions | T-003, T-004, T-014 (CSV parsing) | Column-level; field names, types, nullable flags, schema version | Loaded at ingestion time; schema-change detection required (quarterly changes without notice — scenario) |
| Historical labelled calibration cases | Pre-deployment confidence threshold validation (D4 §3 KPI note) | Case-level; 150 minimum; independently labelled by 2 senior billing agents | One-time pre-deployment retrieval; archived post-calibration |

### Output targets

| Output | Derived from task | System written to | Write mechanism |
|---|---|---|---|
| New CRM case or updated case record | T-002 (create/retrieve), T-013 (update, close) | CRM (Salesforce) | CRM REST API: POST (new case), PUT (update fields, status) |
| Agent-generated case summary and evidence attachments | T-013 | CRM case record | CRM REST API — attachment or custom case field write |
| Credit record | T-011 | APEX_CREDITS (Aurum) | **Unknown — see Gap G-1** |
| Customer resolution notification | T-012 | CRM outbound messaging / email | CRM outbound messaging API (assumed available via CRM REST; API specifics are assumptions) |

### Approval/governance channels

| Channel required | Derived from task | Mechanism | Enforcement type |
|---|---|---|---|
| APPROVER_ID capture — named human approver must explicitly confirm credit amount and record before APEX_CREDITS write is triggered | T-010 (route to approver), T-011 (write blocked without APPROVER_ID) | CRM workflow state engine: case held in PENDING_APPROVAL until authenticated human action transitions to APPROVED; APPROVER_ID populated from authenticated user token | **System-enforced — required design constraint; see Risk R-3 for bypass risk if this is not achievable** |
| Audit trail for approver action: identity, timestamp, CREDIT_AMT confirmed, AUDIT_REF (CRM case ID) | T-011, FM-3 | CRM case log and APEX_CREDITS record (APPROVER_ID + AUDIT_REF + APPLIED_DT fields) | System-enforced (CRM audit log) + batch-verifiable (daily APEX_CREDITS scan) |

---

## 2. System and data inventory table

| System/Source | Data needed | Access type | Inferred availability | Gap/Risk | Priority |
|---|---|---|---|---|---|
| **Salesforce-based CRM — case queue** | Inbound dispute contacts; customer ID; case history; delivery outcome; agent assignment | Read-Write + Event trigger | API likely available — REST APIs confirmed in scenario_context.md; specific endpoints and rate limits are assumptions beyond what is stated | Trigger mechanism (webhook vs. polling) not confirmed; service account permissions not confirmed | Required |
| **Salesforce-based CRM — outbound messaging** | Customer notification after case resolution; case status communications | Write | API likely available — CRM REST APIs confirmed; outbound messaging capability assumed via Salesforce standard email/SMS features | Salesforce email-to-case or messaging configuration not confirmed — assumption | Required |
| **Salesforce-based CRM — workflow state engine** | PENDING_APPROVAL → APPROVED workflow state transition; APPROVER_ID field writeable only by authenticated human token | Read-Write (state transitions) | API unknown — REST API confirmed but Salesforce Approval Process or Flow configuration is not confirmed in scenario | If Salesforce is configured in basic CRM mode without Approval Processes, governance gate cannot be system-enforced without configuration work | Required |
| **Aurum Billing — APEX_BILL_DAILY CSV** | Invoice headers, surcharge line items (AMT_FUEL_SURCH, AMT_REDELIV, DIM_WEIGHT), invoice date | Read (batch file, daily 02:00–04:00 GMT) | Manual/document-only — batch CSV confirmed in scenario; no real-time API. Named in scenario_context.md — API specifics and integration maturity are assumptions beyond what is stated | T-1 lag; schema changes ~quarterly without notice; same-day invoice not available (triggers T-014 / ET-004) | Required |
| **Aurum Billing — APEX_DISPUTES_OPEN CSV** | Open disputes by customer ID; dispute type (FUEL_SURCH_DAMAGE, DIM_WEIGHT, etc.); ASSIGNED_TO; STATUS | Read (batch file, daily) | Manual/document-only — batch CSV confirmed; schema confirmed via artefact. Named in scenario_context.md | T-1 lag; schema change risk | Required |
| **Aurum Billing — APEX_CREDITS write path** | Write: CREDIT_AMT, APPROVER_ID, REASON_CODE, AUDIT_REF (CRM case ID), APPLIED_DT | Write | **Unknown** — batch exports only confirmed; write path existence not confirmed. Named in scenario_context.md — the specific question of whether a programmatic write path exists is explicitly flagged as an open gap (D4 A-5, confidence: Low) | **G-1 — Blocking.** Without a programmatic write path, C-8 cannot be delivered; handle-time target and audit trail enforcement are at risk | Required |
| **Aurum Billing — APEX_CUSTOMER_MASTER CSV** | Customer account status (active/inactive/collections/payment plan) | Read (batch file, monthly — first of month) | Manual/document-only — batch CSV confirmed; monthly cadence confirmed. Named in scenario_context.md | Up to 30-day staleness in account status; status change between export dates not visible to agent | Important |
| **Aurum Billing — APEX_RECON CSV** | T-2 reconciliation data; DISPUTE_OPEN flags per invoice | Read (batch file, daily — T-2 lag) | Manual/document-only — batch CSV confirmed in scenario. Named in scenario_context.md | T-2 lag; useful for confirming dispute status but not for same-day or T-1 decisions | Important |
| **Credit policy registry** | Formal credit policy document: REASON_CODE taxonomy, approval thresholds, dispute-type validity rules; version number; COO approval date | RAG (retrieval-augmented generation) + Read | **Unknown — does not currently exist as a formal document.** Not named in scenario — existence and API availability are assumptions. D4 A-6 flags this as a deployment prerequisite | **G-2 — Blocking.** Agent cannot generate credit recommendations without this; ET-006 threshold cannot be set | Required |
| **Historical calibration case set** | 150+ labelled historical billing dispute cases with final verdicts and credit amounts; labelled by 2 senior billing agents | Read (one-time, pre-deployment) | Unknown — CRM case archive likely contains historical cases; whether they are labelled with final verdicts is unknown. Not named in scenario — existence and labelling quality are assumptions | **G-4 — Blocking for first deployment.** Without this, confidence threshold validation cannot be completed | Required (pre-deployment) |
| **SOP v2.3 — Apex Customer Operations Exception Handling SOP** | Procedural reference for non-standard cases — if usable | Read (document) | Manual/document-only — SOP confirmed in scenario as stale; references DispatchHub (retired Oct 2024); Section 4.3 incomplete. Named in scenario_context.md | **G-5 — Degrading.** SOP cannot be used as reference material in current form; must be updated or explicitly excluded from corpus | Low (excluded in current form) |

---

## 3. Gap analysis

> **Gap G-1:** APEX_CREDITS programmatic write path
> **What the agent cannot do without it:** T-011 (Write audit-compliant credit record to APEX_CREDITS once APPROVER_ID is confirmed) — the agent cannot execute the credit record write; C-8 (Fully Agentic credit execution) cannot be delivered. Without a system-writeable credit path, the agent can prepare a complete credit record but cannot submit it; the human approver must then submit a manual Aurum support ticket (48-hour turnaround). The handle-time reduction target (28 min → ≤10 min) is partially but not fully achievable. The audit trail compliance KPI (100% APPROVER_ID in APEX_CREDITS) depends on the write path populating APPROVER_ID correctly — if the write is manual, the compliance gap from Artefact 2 persists.
> **Severity:** Blocking — agent can launch in a reduced scope (intake, validity assessment, recommendation preparation) but the primary efficiency and compliance gains are not fully deliverable.
> **Mitigation options:**
> 1. Confirm with Aurum vendor and Apex IT whether Aurum's Oracle database exposes a controlled write path for the CREDITS table (direct JDBC insert under a service account with restricted permissions) — this would bypass the manual ticket without requiring a full API.
> 2. Build a CRM-to-Aurum integration layer that auto-submits an Aurum support ticket with pre-populated credit record fields after approval is confirmed in CRM — the 48-hour turnaround remains but the manual effort is eliminated and the audit trail is captured in CRM at approval time, not at Aurum write time.
> 3. Scope agent to record preparation and approval capture only; the designated approver submits the Aurum ticket manually using the agent's pre-populated record. Accept the 48-hour execution delay as a deployment constraint, with full write-path integration planned for Phase 2.
> **Discovery action:** Ask Apex IT and/or the Aurum vendor: "Does Aurum Billing expose any write interface — direct database, structured import, or controlled API — that does not require a manual support ticket for credit record creation? Has this been attempted previously?"

---

> **Gap G-2:** Credit policy registry
> **What the agent cannot do without it:** T-009 (Generate structured credit recommendation package) is blocked — the agent cannot generate a credit recommendation without policy-defined REASON_CODEs, approval thresholds, and validity rules. T-011 is also blocked (no REASON_CODE to write). ET-006 (high-value escalation threshold) cannot be configured. Hard Stop §8.3 explicitly prohibits the agent from operationalising the informal 50% heuristic from Artefact 2 as a substitute for a formal policy.
> **Severity:** Blocking — the agent cannot generate or route credit recommendations without this; scope is limited to intake, triage, and evidence assembly.
> **Mitigation options:**
> 1. Engage COO to commission a formal policy document before deployment; frame it as a two-page structured document with explicit numerical rules (e.g., "Fuel surcharge disputes: if calculation error confirmed by invoice data, full credit; if partial evidence, 50% credit — both subject to approval threshold [T]").
> 2. Use the informal 50% practice observed in Artefact 2 as a starting point but document it explicitly with COO written approval — minimum viable policy that enables deployment, with full policy review scheduled for 90 days post-deployment.
> 3. Deploy agent in intake-and-triage-only scope (no credit recommendation); use the 60-day period to build evidence for what the policy should contain; draft policy based on observed dispute outcomes from the agent's structured case records.
> **Discovery action:** "Has a formal credit policy for billing disputes been documented anywhere — in a finance policy manual, email thread, or management agreement? If not, who is the owner and what is the timeline for producing one before agent deployment?"

---

> **Gap G-3:** CRM workflow state engine (Salesforce Approval Process / Flow)
> **What the agent cannot do without it:** T-010 (Route to approver and await APPROVER_ID) — the system-enforced approval gate requires a CRM workflow state that can only advance via an authenticated human action. Without this, the APPROVER_ID capture is procedure-dependent: the approver must manually populate the field, which — as Artefact 2 demonstrates — is the exact behaviour that produced the compliance gap (Sandra's credit with no audit log entry). The governance hard stop in §8 cannot be technically guaranteed without a system-enforced gate.
> **Severity:** Blocking for governance enforcement. The agent can technically launch without this, but the primary compliance guarantee degrades from system-enforced to procedure-dependent — equivalent to the current informal state.
> **Mitigation options:**
> 1. Configure a Salesforce Approval Process with the designated approver role and APPROVER_ID requirement — standard Salesforce feature, no custom development required; configuration by a Salesforce administrator.
> 2. Build a custom Salesforce Flow that creates an approval task, captures the approver's authenticated confirmation, and writes the APPROVER_ID field before releasing the case to the next stage.
> 3. Use a separate lightweight workflow tool (e.g., a dedicated approval queue in an existing ticketing system) to capture approvals — less desirable because the APPROVER_ID capture is then in a separate system from the CRM case record, creating a reconciliation dependency.
> **Discovery action:** "Is Salesforce configured with Approval Processes or Flow? Does a Salesforce administrator have the capacity to configure an Approval Process for the billing dispute workflow? What Salesforce edition is Apex running?"

---

> **Gap G-4:** Historical calibration case set
> **What the agent cannot do without it:** Pre-deployment confidence threshold validation (D4 §3 KPI note) — without 150 labelled cases, the 0.85 confidence threshold cannot be validated against domain-specific data; the agent cannot deploy with a calibrated threshold and must either use an uncalibrated default (risk: unknown precision) or apply 100% HITL until live cases accumulate.
> **Severity:** Blocking for first deployment on schedule; not blocking for build.
> **Mitigation options:**
> 1. Source from APEX_DISPUTES_OPEN historical exports and CRM case archive; have two senior billing agents (e.g., Sandra W. + one peer) independently label final verdicts for 150 cases; build the calibration set over 2–3 weeks before deployment.
> 2. Use a smaller calibration set (50–80 cases) with wider confidence intervals and document the lower statistical power explicitly; accept a longer post-deployment monitoring period as compensation.
> 3. Deploy with 100% HITL for the first 30 days; use live reviewed cases as the calibration set; set the confidence threshold retrospectively based on the first 150 live cases. Advantage: calibration uses current case distribution.
> **Discovery action:** "How many closed billing dispute cases are accessible in the CRM archive with final resolution outcomes? Are the resolution verdicts and credit amounts recorded in structured fields or only in free-text notes?"

---

> **Gap G-5:** SOP v2.3 current status
> **What the agent cannot do without it:** Procedural guidance for out-of-taxonomy cases. This is not a hard blocker — the agent's taxonomy (fuel surcharge, redelivery fee, dimensional weight) covers the confirmed dispute types from the scenario artefacts, and ET-002 escalation handles unknown types. However, the human agent receiving the ET-002 escalation also has no current SOP to follow; the gap is equally present in the human process.
> **Severity:** Degrading — agent can operate, but edge case handling is undocumented for humans and agent alike.
> **Mitigation options:**
> 1. Update SOP v2.3 before deployment — specifically update Section 4.3 (damaged consignments, currently "TBD") and replace all DispatchHub references with Driver App equivalents; this is a prerequisite for the human reviewers receiving ET-002 escalations.
> 2. Exclude SOP v2.3 from the agent's reference corpus entirely; rely on the credit policy registry as the sole policy reference for WS4; document the WS4 dispute taxonomy (fuel surcharge, redelivery fee, dimensional weight) as the operative SOP for billing disputes.
> 3. Accept the gap for now and document in the assumption log; raise with COO in the stakeholder session as a process hygiene item that affects both the human team and the agent.
> **Discovery action:** "Is SOP v2.3 currently being updated? Who owns the update and what is the timeline? Is there a separate billing-specific procedure document that supersedes Section 4 for WS4 cases?"

---

## 4. Risk register

| System | Risk type | Risk description | Likelihood (H/M/L) | Impact (H/M/L) | Mitigation |
|---|---|---|---|---|---|
| Aurum Billing — APEX_CREDITS write path | API availability risk | No real-time write API confirmed. Invoice modifications require a manual 48-hour Aurum support ticket. Whether a programmatic write path can be established is unknown. Prior RPA initiative broke on Aurum schema changes — confirms integration fragility. | H | H | Confirm with Aurum vendor and Apex IT in discovery before committing to C-8 scope; plan three fallback levels (direct DB write / pre-populated ticket automation / manual-submit with agent-prepared record) |
| Aurum Billing — all CSV exports | Data quality risk | Schema changes occur "approximately quarterly without prior notice" (scenario) — confirmed cause of the prior RPA failure. A schema change mid-deployment breaks the agent's CSV parsing logic silently: the agent continues to run but reads incorrect field values, producing invalid validity verdicts with no immediate error signal. | H | H | Build schema version detection into CSV ingestion layer (header hash check at each batch load); alert to operations lead on any schema change; define fallback to 100% HITL for all cases until schema updated and re-tested |
| Aurum Billing — APEX_CREDITS write path | **Governance enforcement mechanism risk** | **System-enforced vs. procedure-dependent:** If the APEX_CREDITS write path requires a CSV submission or manual ticket, the APPROVER_ID field is populated by whoever submits the file — which could be the agent itself writing a system-generated string. The governance hard stop (agent never writes a credit without a named human APPROVER_ID) can only be technically guaranteed if the write path enforces it: i.e., the APPROVER_ID field is populated via an authenticated workflow action, not a file field the agent controls. If the write path is file-based or manual, the control is **procedure-dependent**: it relies on the designated approver's discipline to provide their real name/ID, not on a system that prevents a system ID from being accepted. This is the machine-speed version of the exact failure documented in Artefact 2. **Policy-only enforcement risk rating: High.** System-enforced enforcement risk rating: Low (if correctly implemented). | H (that write path is not system-enforceable) | H | Design requirement: APPROVER_ID must be captured in the CRM workflow (system-enforced) before the write action is triggered; the write API call must be issued by the CRM workflow engine using the CRM-captured APPROVER_ID, not by the agent from its own context. The agent must never have direct write-field access to APPROVER_ID. Confirm this architecture with Apex IT before build begins. |
| CRM (Salesforce) — workflow state engine | API availability risk | CRM REST APIs are confirmed, but Salesforce Approval Process or Flow configuration is not confirmed. If Salesforce is deployed in a basic CRM-only configuration, workflow state enforcement requires configuration work that must be scoped and scheduled before build. | M | H | Confirm Salesforce edition and existing workflow configuration in discovery; estimate configuration effort; include as a prerequisite in the pre-deployment checklist |
| CRM (Salesforce) — inbound case data | Data quality risk | Inbound dispute contacts arrive as unstructured text (email or phone transcription). T-001 extraction depends on the customer including a recognisable invoice number. If the customer omits the invoice reference, T-003 cannot execute and the entire retrieval chain is blocked. | M | M | T-001 must include an explicit confidence check for required fields (customer ID, invoice number); if invoice reference is absent or ambiguous, agent must send a structured acknowledgement requesting the missing reference before proceeding — not escalate to a human for this step |
| Credit policy registry | Data quality risk | Policy does not currently exist as a formal machine-readable document. When produced, if written in ambiguous natural language (e.g., "partial credit at manager discretion"), RAG retrieval will return this clause for ambiguous cases and the agent's confidence score will correctly reflect genuine ambiguity — producing systematic low-confidence verdicts and high HITL volume. | H | H | Policy must be written with explicit numerical rules and taxonomy codes; the FDE should review policy format before build begins; policy owner should confirm structured format is achievable |
| Credit policy registry | Legal/compliance risk | If the credit policy document contains proprietary pricing logic, contractual rate schedules, or information under legal privilege, indexing it in an LLM retrieval store creates a data security exposure — especially if the retrieval store is hosted externally or accessed by a cloud API. | M | M | Review policy document for sensitive content before ingestion; store retrieval index in an access-controlled environment; exclude confidential pricing schedules from the retrieval corpus; rely on structured taxonomy codes (REASON_CODE values) rather than full pricing text |
| APEX_CREDITS export | Audit trail risk | APEX_CREDITS data is available only via daily batch export. If the agent writes a credit record and the batch export fails or is delayed overnight, the daily compliance scan cannot confirm the record until the next export. A write that fails silently (FM-5 / ET-008 scenario) will produce no APEX_CREDITS record at all — the gap is not detectable until the next batch run. | M | H | Maintain a write confirmation log in CRM (case-level: "credit record write confirmed at [timestamp]") cross-referenced against the daily APEX_CREDITS export; any case with a CRM write-confirmed flag but no corresponding APEX_CREDITS record in the next export triggers an immediate ET-008 alert |
| APEX_CUSTOMER_MASTER CSV | Data quality risk | Account status data is exported monthly (first of month) — up to 30 days stale. A customer account moved to collections or under a formal payment plan between export dates will be treated by the agent as an active standard account, and a credit recommendation may be generated for an account that should be escalated. | M | M | Flag APEX_CUSTOMER_MASTER data with its export date in the agent's context; if the export date is >15 days old and the case has any financial risk indicators (high credit amount, repeat disputes), escalate to human agent with "customer status may be stale — verify before proceeding" flag |
| SOP v2.3 | Data quality risk | SOP is confirmed stale; references DispatchHub (retired Oct 2024); Section 4.3 (damaged consignments) is explicitly "TBD." If ingested as reference material, the agent will retrieve procedure text referencing a non-existent system and incomplete policy for the highest-judgment case type. | H | M | Exclude SOP v2.3 from agent reference corpus entirely; do not ingest; confirm exclusion in pre-deployment checklist |

---

## 5. Context engineering design

### Memory architecture

| Memory type | Content | Storage mechanism | Lifecycle |
|---|---|---|---|
| In-context (short-term) | Active case data: customer contact text, extracted fields (customer ID, invoice number, dispute description), retrieved invoice data (APEX_BILL_DAILY fields), open dispute history (APEX_DISPUTES_OPEN), validity reasoning chain and confidence scores, credit recommendation draft, workflow state (PENDING_APPROVAL / APPROVED), approver token | Assembled at case intake (T-001); updated as each task completes; passed as structured context to each reasoning step | Active for a single case lifecycle; committed to CRM case record at T-013 (case closure); not retained in agent memory after closure |
| Semantic (long-term, retrieval) | Credit policy document: REASON_CODE taxonomy, dispute-type validity rules, approval thresholds — chunked at clause boundaries and tagged with dispute_type metadata. Aurum CSV schema definitions: column names, types, schema version hash. Historical calibration cases: 150 labelled disputes with final verdicts (pre-deployment; periodically augmented) | Vector index with metadata filters (dispute_type, schema_version, policy_version); hosted in access-controlled environment | Policy corpus: versioned; old version purged from index on each COO-approved revision; effective date and version tag on each chunk. Schema definitions: updated on schema-change detection alert. Calibration cases: updated quarterly or after each threshold retuning event |
| Procedural (static instructions) | Agent operating instructions: task execution order (T-001 → T-002 → T-003 → T-004 → T-005 → T-006 → T-007 → T-008 → T-009 → T-010; T-011 blocked until APPROVED state), confidence threshold value (current: 0.85), escalation trigger conditions (ET-001 through ET-008), hard stop rules (§8 of D4), HITL routing conditions | System prompt / instruction set; stored in version-controlled policy register | Updated only by operations lead with explicit COO sign-off; each change logged with effective date and trigger condition; threshold changes additionally logged per D4 §3 recalibration protocol |

### Retrieval strategy

**What triggers a retrieval call:**

1. **T-005 (Dispute type classification):** When the parsed dispute contact is ambiguous between two standard types (e.g., a damaged delivery that also has a fuel surcharge claim), the agent retrieves the REASON_CODE taxonomy chunk to confirm which classification applies.
2. **T-007 (Charge validity assessment):** After dispute type is confirmed, the agent retrieves the policy clause for that dispute type (e.g., "fuel surcharge validity: confirm against AMT_FUEL_SURCH in APEX_BILL_DAILY; if calculation error confirmed, verdict = invalid charge") to drive the structured validity rule-check.
3. **T-009 (Credit recommendation package):** The agent retrieves the full policy section for the confirmed dispute type, including the REASON_CODE value and the approval threshold table, to populate the recommendation package for the human approver.
4. **Aurum CSV parsing (T-003, T-004, T-014):** At each batch file ingestion, the agent retrieves the stored schema definition for the relevant CSV type and compares against the current file header hash; a mismatch triggers a schema-change alert before any data is read.

**Retrieval target:**

- Policy document: Top-K clause chunks where K = 3–5, filtered by dispute_type metadata tag that matches the T-005 classification output — the dispute type filter is applied before retrieval to prevent cross-type clause confusion (see risk below).
- Aurum CSV data: Structured exact-match lookup (not RAG) — invoice number → row in APEX_BILL_DAILY; customer ID → rows in APEX_DISPUTES_OPEN.
- CRM case history: CRM REST API query (not RAG) — customer ID → case history records; structured JSON response parsed directly.

**Retrieval quality evaluation:**

The core risk is a false-positive policy clause match: the retrieval returns a clause that appears similar to the dispute context but is for the wrong dispute type (e.g., redelivery fee clause retrieved for a fuel surcharge case). This would produce a validity verdict grounded in the wrong policy rules — a legally material error.

Evaluation approach:
- **Chunk-level:** Each retrieved chunk is attached to the CRM case record with its chunk ID, policy section reference, and similarity score. Human reviewers in the weekly audit can inspect which clause drove each verdict and flag cross-type mismatches.
- **Dispute-type filter enforcement:** Retrieval is constrained to chunks tagged with the dispute_type confirmed in T-005. The filter must execute before the similarity search — not as a post-filter on results. If T-005 returns low confidence on the dispute type, retrieval must not proceed until the type is confirmed by the human reviewer (ET-001 escalation).
- **Audit signal:** If weekly audit reviews reveal that the same incorrect clause is being retrieved for a specific dispute pattern, the policy document must be restructured to create clearer separation between clause text for different dispute types.
- **Automated check:** If the retrieved clause's dispute_type tag does not match the case's classified dispute type, the agent must flag a retrieval confidence warning rather than proceeding silently.

**Retrieval cost management:**

- Chunking strategy: Policy document split at clause boundaries (numbered rules and sub-rules), not at fixed token counts. Each chunk tagged with: dispute_type, section_number, effective_date, policy_version. Expected corpus: ~10–50 pages (small domain document); no cost pressure.
- Caching: Full policy document loaded into session cache on agent startup; not re-retrieved on each case. Cache invalidated only on policy version increment (logged by operations lead).
- Index rebuild trigger: Policy version change only — not on daily schedule. Aurum schema definition index updated on schema-change alert only.

### Key context engineering risks

1. **Policy language ambiguity producing systematic low-confidence verdicts:** If the credit policy (which does not yet exist) is written in natural language with discretionary terms ("at manager's discretion," "reasonable credit"), the RAG retrieval will return these clauses for ambiguous cases and the agent's confidence score will correctly reflect genuine ambiguity — routing a disproportionate share of cases to HITL and negating the handle-time reduction target. The policy must be written with explicit numerical rules and enumerated conditions for each dispute type.

2. **Multi-version policy confusion in retrieval index:** If the policy is revised and the old version is not purged from the vector index before the new version is ingested, the agent may retrieve clauses from both versions simultaneously for a single query. The retrieved chunks will carry different policy version tags, producing a contradictory reasoning context. Strict lifecycle enforcement — old version purged before new version ingested, with a brief blackout period where policy retrieval escalates to HITL — is required.

3. **Aurum schema drift causing silent misparse:** The Aurum CSV schema changes approximately quarterly without prior notice. If the schema changes and the ingestion layer does not detect it, the agent continues parsing with the old schema — reading wrong field values (e.g., reading AMT_REDELIV as AMT_FUEL_SURCH because columns shifted). The agent produces a validity assessment based on incorrect data, with full apparent confidence. A schema hash check at each ingestion is the only reliable defence; without it, this failure is undetectable until a human reviewer spots a nonsensical verdict.

---

## 5b. Pre-deployment prerequisite checklist

- [ ] **Credit policy document format:** The formal credit policy must exist as a machine-readable structured text document (not an image, scan, or non-extractable PDF); every clause must contain explicit numerical rules and named REASON_CODE values — no discretionary language — **Confirmed by:** COO-designated policy owner (finance or operations lead) — **If unconfirmed:** Agent cannot generate credit recommendations; T-009 and T-011 are blocked; scope is limited to intake, validity assessment, and data assembly

- [ ] **Credit policy version control:** The policy must have a version number, effective date, and documented COO approval signature; these fields must be machine-readable in the policy registry so the agent can confirm it is operating on the current approved version — **Confirmed by:** Operations lead — **If unconfirmed:** Agent may operate on an unapproved draft policy; any credit recommendation generated under an unapproved policy is non-compliant; audit exposure

- [ ] **APEX_CREDITS programmatic write path:** A programmatic write path to APEX_CREDITS is confirmed operational (direct DB, controlled API, or auto-ticket integration) and tested end-to-end with the CRM approval state machine; write does not require a 48-hour manual Aurum support ticket — **Confirmed by:** Apex IT / Aurum vendor — **If unconfirmed:** C-8 (Fully Agentic credit execution) cannot be delivered; APEX_CREDITS write scope must be reduced to record preparation only; handle-time improvement target is partially at risk; credit audit trail KPI is at risk

- [ ] **CRM workflow state engine (Salesforce Approval Process / Flow):** A Salesforce Approval Process or equivalent workflow state machine is configured such that: (a) the case enters PENDING_APPROVAL when the agent submits a credit recommendation; (b) only an authenticated human user action transitions the case to APPROVED; (c) the APPROVER_ID field is populated from the authenticated user token and is not writeable by the agent's service account — **Confirmed by:** Salesforce administrator — **If unconfirmed:** The primary governance gate is procedure-dependent rather than system-enforced; the compliance guarantee from Artefact 2 is not technically delivered

- [ ] **CRM inbound trigger mechanism:** The agent's intake path (CRM case queue trigger, or inbound email webhook that creates a CRM case) is confirmed operational and has been approved by Apex IT security; the agent's service account has case-queue read access and case-create/update write access — **Confirmed by:** Apex IT security — **If unconfirmed:** Agent cannot receive inbound disputes; the pipeline does not start

- [ ] **Approval/audit trail queryability:** APEX_CREDITS APPROVER_ID and AUDIT_REF fields are populated by the credit write path with the values provided by the CRM workflow state machine; these fields are readable in the daily APEX_CREDITS batch export; a daily compliance scan against null or system-placeholder APPROVER_ID values can be run from the export — **Confirmed by:** Operations lead + Apex IT — **If unconfirmed:** Daily compliance audit (audit trail KPI) cannot be automated; the compliance gap from Artefact 2 is not closed

- [ ] **Historical calibration set availability:** A minimum of 150 historical billing dispute cases with documented final resolution outcomes (verdict + credit amount) are accessible from the CRM case archive or APEX_DISPUTES_OPEN historical exports; two senior billing agents are available to independently label them over a 2–3 week period before deployment — **Confirmed by:** COO + senior billing agents (Sandra W. equivalent) — **If unconfirmed:** Pre-deployment confidence threshold validation cannot be completed; agent must deploy with an uncalibrated threshold (high risk: precision unknown) or with 100% HITL as the safe fallback

- [ ] **SOP v2.3 exclusion confirmed:** SOP v2.3 is explicitly excluded from the agent's reference corpus; a documented escalation path exists for the human reviewer receiving ET-002 (unknown dispute type) escalations — either an updated SOP section or a named senior agent responsible for unknown types — **Confirmed by:** Operations lead — **If unconfirmed:** Agent may inadvertently reference stale SOP content if it is present in a shared document store; ET-002 escalation has no defined human resolution path

---

## 6. Compounding opportunities

| Integration built | Future agent that could reuse it | Reuse mechanism |
|---|---|---|
| Aurum CSV ingestion layer (APEX_BILL_DAILY, APEX_DISPUTES_OPEN, APEX_RECON, APEX_CUSTOMER_MASTER) with schema-change detection and daily batch scheduling | WS1 Delivery Exception Agent (D3: Conditional priority target) | Delivery exceptions involving billing charges (fuel surcharge disputes arising from damaged consignments — confirmed pattern in APEX_DISPUTES_OPEN: FUEL_SURCH_DAMAGE type) require the same invoice and dispute history data; the CSV ingestion layer is reused without rebuild; schema-change detection protects both agents |
| Aurum CSV ingestion layer | Accounts receivable reconciliation agent (future) | APEX_RECON and APEX_BILL_DAILY are the primary inputs for AR reconciliation; the ingestion layer with schema-drift detection is the platform component; a reconciliation agent is a direct extension — the same infrastructure, a different analytical task |
| CRM REST API integration (case read/write, case status management, outbound messaging) | WS2 ETA Inquiry Agent (D3: highest Volume × Value score — primary secondary target) | ETA inquiry cases are managed in the same CRM instance; case creation, status update, and customer notification are structurally identical; the CRM integration layer is fully reusable |
| CRM workflow state engine (PENDING_APPROVAL → APPROVED, system-enforced APPROVER_ID gate) | Any future agent in this domain requiring HITL approval for a compliance-sensitive or irreversible action | The approval workflow pattern (system-enforced human gate with authenticated user token) is domain-agnostic; once configured in Salesforce, it can be cloned for future agent designs requiring a governance gate — the investment is amortised across the WS4 agent and every subsequent agent that needs a HITL checkpoint |
| Credit policy RAG retrieval corpus and versioned policy index | Future billing policy compliance monitoring agent or credit audit agent | The versioned, clause-tagged policy corpus is the reference layer for any billing-related agent; a compliance monitoring agent reading APEX_CREDITS against the same policy index would share the corpus without duplication; policy maintenance overhead is shared across both agents |
