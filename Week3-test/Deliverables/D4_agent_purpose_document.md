# D4 — Agent Purpose Document
**Helix Workforce Software — Vendor Contract Clause Review**
**Produced:** 2026-05-04 | **Revised:** 2026-05-04 (D4A build loop — R1/R2/R3 applied) | **Status:** Draft — awaiting FDE approval

---

## 0. Executive Summary

- **Job to be Done:** The Contract Classifier Agent converts inbound vendor contracts into structured clause deviation reports against the Helix negotiation playbook, reducing Tom Reilly's WS1 time-per-case from ~25 min to ≤8 min human review and enabling the team to process ≥375 contracts per quarter without additional headcount (D0B success metrics).
- **Autonomy boundary:** The agent classifies and reports independently but may not commit a routing decision (WS2 standard-deviation / WS3 escalation / No Redline Required) without a human confirmation event recorded in Ironclad — protecting the downstream integrity of Amelia Forsythe's governance rule that no counteroffer may leave Legal's queue without named-lawyer sign-off on the specific clauses being negotiated.
- **Primary failure risk:** The agent mis-routes a WS3-tier clause as WS2, allowing a clause requiring senior-lawyer review to receive only paralegal treatment — undetected until the sign-off stage or, in the worst case, post-dispatch; detected by weekly 10% audit of routing decisions against lawyer retrospective classification.

---

## 0b. Table of Contents

- [0. Executive Summary](#0-executive-summary)
- [0b. Table of Contents](#0b-table-of-contents)
- [1. Agent Identity](#1-agent-identity)
- [2. Primary Objectives](#2-primary-objectives)
- [3. KPIs](#3-kpis)
- [4. Activity Catalog](#4-activity-catalog)
- [4b. Technical Definitions](#4b-technical-definitions)
- [5. Autonomy Matrix](#5-autonomy-matrix)
- [6. Escalation Triggers](#6-escalation-triggers)
- [7. Failure Modes](#7-failure-modes)
- [8. Out-of-Scope (Hard Stops)](#8-out-of-scope-hard-stops)
- [9. Assumption Log](#9-assumption-log)

---

## 1. Agent Identity

- **Agent name:** Contract Classifier Agent
- **Job to be Done:** Given an inbound vendor contract received by the Helix Legal & Commercial team, produce a structured clause deviation report identifying every clause that departs from the Helix negotiation playbook, with a routing tier recommendation and confidence score, so that Tom Reilly can confirm the routing in ≤8 minutes rather than performing the full 25-minute first-pass read.
- **Business context:** Legal & Commercial team (5 staff); replaces WS1 (first-pass clause classification), which is the prerequisite gate for all 300 contracts per quarter. Downstream handoffs: confirmed routing to WS2 (standard-deviation redlining by Tom) or WS3 (escalated clause review by a commercial lawyer), or confirmation of No Redline Required (passed directly to WS4 for sign-off). The agent's output is the primary input to every downstream work stream.
- **Delegation archetype:** Agent-led + Human Oversight — the agent performs the primary classification work; Tom Reilly reviews the deviation report and confirms the routing tier before the case is formally assigned. Applies to C-1 (intake) and C-2 (clause comparison) from D2. The routing confirmation step (C-3) operates as Agent Proposes / Human Approves due to the informal and undocumented state of the current escalation criteria (Artefact 2.1, D2 C-3 rationale).

---

## 2. Primary Objectives

1. Process 100% of inbound vendor contracts through first-pass clause classification and produce a deviation report in Ironclad, maintaining a clause categorisation accuracy of ≥95% (correct match / deviation / escalation flag per clause) across all playbook categories except DPA until the playbook DPA section is updated.
2. Reduce WS1 human time-per-case to ≤8 minutes by producing a structured, clause-by-clause deviation report that enables Tom to confirm or correct classifications without re-reading the source document.
3. Enable the Legal & Commercial team to process ≥375 contracts per quarter (consistent with Helix's 25% YoY growth projection) within the existing 5-person headcount by eliminating the 125 hours/quarter of paralegal reading time currently consumed by WS1 (D0B, Section 3).

---

## 3. KPIs

| KPI | Baseline | Target | Measurement method | Review cadence |
|-----|----------|--------|--------------------|---------------|
| Accuracy (% of clauses correctly categorised as Match / Deviation-Standard / Deviation-Escalation) | Not measured — no baseline exists [Assumption A-1] | ≥95% correct categorisations across all clause types in scope | Weekly audit: a lawyer reviews agent classification output for a random 10% sample of cases and records corrections clause-by-clause in Ironclad; error rate computed as (incorrect categorisations / total clauses reviewed) | Weekly for first 3 months post-deployment; monthly thereafter |
| Coverage (% of cases processed end-to-end by the agent without failure requiring manual restart) | 0% — no agent currently operates on WS1 | ≥90% of all inbound cases reaching "Pending Human Review" status in Ironclad without an agent error event | Ironclad case log: count of cases with status "Pending Human Review" vs. total intake events per week; error events logged automatically by agent | Weekly |
| Throughput (human time per case for WS1) | ~25 min/case (Tom reading + classifying full contract) | ≤8 min/case (Tom reviewing and confirming agent deviation report) | Time-tracked in Ironclad between "case opened for review" and "routing confirmed" events; sampled across 20 contracts per week per D0B measurement protocol | Weekly (sampled, 20 contracts/week) |
| HITL escalation rate (% of cases where agent flags low confidence and requests human adjudication before report is finalised) | N/A — no agent | ≤20% of cases receiving a confidence-below-threshold flag on routing tier or individual clause [Assumption A-2] | Ironclad case log: count of "confidence flag" events vs. total cases per week | Weekly |
| Turnaround time contribution — WS1 stage (calendar time from contract receipt to routing confirmed) | Not isolated — overall turnaround is 4–6 business days | ≤0.5 business days (agent classification + human confirmation) | Ironclad timestamp delta between intake record creation and routing-confirmed event | Weekly |

---

## 4. Activity Catalog

| Task ID | Task name | Task type | Delegation level | Data required | Tool required | Risk level |
|---------|-----------|-----------|-----------------|---------------|---------------|------------|
| T-1 | Monitor Outlook inbox for inbound vendor contract emails | Retrieval | Fully agentic | Outlook mailbox access (Legal & Commercial monitored inbox) | Outlook API [Assumption A-3] | Low |
| T-2 | Extract email metadata and Word attachment | Retrieval | Fully agentic | Email header, body, attachment | Outlook API | Low |
| T-3 | Log intake case in Ironclad with counterparty name, contract type, received date, and delivery channel flag | Action | Fully agentic | Extracted metadata from T-2 | Ironclad REST API | Low |
| T-4 | Parse contract document structure and identify clause sections | Reasoning | Fully agentic | Word document (DOCX) | Document parser + LLM | Low |
| T-5 | Retrieve current active playbook version from SharePoint | Retrieval | Fully agentic | SharePoint path to "Position Statements v3.4"; playbook version timestamp | SharePoint API [Assumption A-4] | Low |
| T-6 | Compare each identified clause against the corresponding playbook position | Reasoning | Agent-led + HITL on condition | Parsed clause text + relevant playbook section + playbook version metadata | LLM | Medium |
| T-7 | Classify each clause as Match / Deviation-Standard / Deviation-Escalation / DPA-Unverified | Decision | Agent-led + HITL on condition | T-6 comparison output + per-clause confidence score | LLM | High |
| T-8 | Apply DPA currency check — attach "unverified against current regulation" flag to all DPA clause classifications when playbook DPA section predates the DPDI Act Q1 revisions | Decision | Human-led + Agent support | Playbook version timestamp vs. DPDI Act effective date [Assumption A-5] | SharePoint API + LLM | High |
| T-9 | Assign routing tier recommendation (No Redline Required / WS2 / WS3) with aggregate confidence score and deviation magnitude summary | Decision | Agent-led + HITL on condition | All T-7/T-8 clause classifications + confidence distribution | LLM | High |
| T-10 | Generate structured deviation report (clause-by-clause: clause text excerpt, playbook position, classification, confidence, flags) | Generation | Fully agentic | All T-7/T-8/T-9 outputs | LLM | Medium |
| T-11 | Write deviation report to Ironclad case record and move case to "Pending Human Review" queue | Action | Fully agentic | Completed deviation report (T-10) + routing tier suggestion (T-9) | Ironclad REST API | Low |

---

## 4b. Technical Definitions

### Confidence Scoring

Per-clause confidence scores are **prompt-elicited float values (0.0–1.0)** produced by the LLM as part of each clause classification output. The classification prompt instructs the LLM:

> "Assign a confidence score between 0.0 and 1.0 alongside your classification. Score 0.90 or above only when the clause text unambiguously and materially matches or departs from the exact playbook position with no reasonable alternative interpretation. Score 0.75–0.89 when the classification is probably correct but a reasonable reader could defend a different interpretation. Score below 0.75 when you could plausibly defend two different classifications and are not confident which is correct."

**Three operational thresholds:**

| Threshold | Value | Meaning |
|---|---|---|
| Match acceptance | ≥ 0.90 | Agent records MATCH autonomously; no HITL required |
| Routing acceptance | ≥ 0.80 | Agent routing recommendation proceeds to human confirmation without additional escalation flag |
| Low-confidence escalation | < 0.75 (per-clause) | Individual clause escalated to Tom for manual adjudication before the classification is recorded |

**Routing confidence** = the minimum per-clause confidence score across all DEVIATION_STANDARD and DEVIATION_ESCALATION classifications in the case. Example: if a contract has five deviations with scores [0.92, 0.88, 0.85, 0.79, 0.95], the routing confidence is 0.79 — below the 0.80 routing acceptance threshold, triggering ET-1.

**Calibration:** Confidence scores are LLM-self-reported and are not independently calibrated in v1. The weekly 10% audit tracks cases where Tom overrides a high-confidence agent classification (score ≥ 0.85 and Tom disagrees), which is the signal used to detect systematic overconfidence and retune prompting instructions.

---

### Deviation Report Schema

The deviation report (T-10) is output as a JSON payload written to the Ironclad case's `agent_deviation_report` custom field [Assumption A-8: this field name must be confirmed with Ironclad admin before deployment].

```json
{
  "case_id": "string — Ironclad case identifier",
  "generated_at": "ISO 8601 timestamp (UTC)",
  "contract_metadata": {
    "counterparty": "string",
    "contract_type": "string",
    "received_date": "ISO 8601 date",
    "delivery_channel": "IRONCLAD | EMAIL_BYPASS"
  },
  "playbook_version": "string — version label from SharePoint document properties",
  "dpa_currency_verified": "boolean — true only if playbook DPA section post-dates DPDI Act effective date",
  "clause_classifications": [
    {
      "clause_id": "string — heading-derived (e.g. 'Section 8.2') or agent-assigned sequential ID",
      "clause_type": "liability_cap | dpa | termination | ip | sla | governing_law | indemnity | unrecognized",
      "clause_excerpt": "string — first 300 characters of clause text",
      "playbook_position_summary": "string — one-sentence summary of the applicable playbook position",
      "classification": "MATCH | DEVIATION_STANDARD | DEVIATION_ESCALATION | DPA_UNVERIFIED",
      "confidence": "float 0.0–1.0",
      "flags": ["string — e.g. 'DPA_CURRENCY_UNVERIFIED', 'LIABILITY_CAP_BELOW_FLOOR', 'LOW_CONFIDENCE'"],
      "determination_source": "AGENT | HUMAN — set to HUMAN when Tom has adjudicated this clause manually"
    }
  ],
  "routing_recommendation": "NO_REDLINE_REQUIRED | WS2 | WS3",
  "routing_confidence": "float 0.0–1.0 — minimum per-clause confidence across all deviation classifications",
  "routing_rationale": "string — one sentence stating the primary driver of the routing recommendation",
  "escalation_flags": ["string — active escalation trigger IDs, e.g. 'ET-1', 'ET-2', 'ET-3'"]
}
```

---

## 5. Autonomy Matrix

**AGENT DECIDES ALONE (no HITL required):**
- Extract and log contract intake metadata (counterparty name, contract type, received date, delivery channel) in Ironclad for every inbound contract
- Parse document structure and identify clause sections
- Retrieve the current active playbook version from SharePoint at the start of each case
- Classify a clause as "Match — No Action Required" when clause text is materially identical to the playbook position and per-clause confidence score is ≥ the configurable match threshold (default: 0.90)
- Generate the structured deviation report and write it to the Ironclad case record
- Move a completed case to the "Pending Human Review" queue in Ironclad

**AGENT ACTS, HUMAN NOTIFIED AFTER:**
- Log a new intake case in Ironclad even when the contract arrives via email-bypass channel (not through the standard Ironclad intake route — Artefact 2.2 pattern); Tom is notified of the bypass flag so the case can be manually reconciled if needed
- Classify a clause as "Deviation — Standard" (within WS2 authority) when: (a) deviation type matches a defined negotiable category, (b) per-clause confidence score is ≥ the configurable deviation threshold, and (c) no DPA currency flag applies; Tom is notified via the deviation report but no confirmation event is required for the classification itself (confirmation is required only for the routing decision — see below)

**AGENT PROPOSES, HUMAN APPROVES BEFORE ACTION:**
- **Routing tier assignment (No Redline Required / WS2 / WS3):** the agent generates a routing recommendation with confidence score and deviation magnitude summary; Tom Reilly (or a designated reviewer) must record a routing confirmation event in Ironclad before the case is formally assigned to a work stream. This is the primary control point protecting the downstream integrity of Amelia Forsythe's governance rule — no counteroffer may leave Legal's queue without named-lawyer sign-off on the specific clauses being negotiated (scenario Section 4). A mis-routed WS3 case treated as WS2 would deliver a high-risk clause through paralegal treatment and could present a non-compliant counteroffer at the sign-off gate.
- **Any clause classification against the DPA playbook section:** the agent proposes a DPA classification but must attach a "DPA — unverified against current regulation" flag to every DPA classification until a revised, version-stamped DPA section is available in the playbook (Artefact 2.3); Tom or Amelia must confirm any WS2 routing decision on a contract with flagged DPA clauses before the case proceeds
- **Any clause where per-clause confidence score falls below the configurable low-confidence threshold (default: 0.75):** the agent presents the clause text, the nearest matching playbook position, and the confidence score to Tom for manual adjudication; the classification is recorded as "Human-determined" in the deviation report, not as an agent classification

**HUMAN TAKES OVER (agent supports only):**
- Contract arrives in a language other than English — agent logs the intake case and flags it as out-of-scope for classification; Tom receives the original document for manual triage
- Contract type does not map to any of the seven defined playbook categories (liability cap, DPA, termination, IP, SLA, governing law, indemnity) — agent logs intake and flags as "Unclassifiable — playbook gap"; Tom escalates to a commercial lawyer for manual triage
- Document parsing returns a clause extraction completeness score below the minimum threshold (>10% of document sections unextracted by the parser) — agent logs the case as "Incomplete parse" in Ironclad and suspends classification; Tom processes the case manually
- Three or more routing tier decisions for a specific counterparty have been manually overridden by Tom within the current quarter — the agent is flagged for routing threshold recalibration before further cases from that counterparty are processed autonomously [Assumption A-6]

---

### Routing Decision Criteria

The routing tier recommendation (T-9) is determined by applying the following steps in order. The most restrictive single-clause outcome governs the entire case.

**Step 1 — WS3 automatic triggers (any one present → WS3 recommendation):**
- Any clause classified DEVIATION_ESCALATION in any clause type
- Liability cap clause with the stated cap value below the playbook minimum floor (£250k per scenario — conservative default active until Amelia codifies a percentage-based threshold, see Assumption A-7)
- IP ownership clause with any classification other than MATCH (IP ownership changes are treated as automatic WS3 until precise IP escalation criteria are co-developed with Amelia and version-controlled in the playbook)
- DPA clause with DPA_UNVERIFIED flag and Tom's confirmation action set to "Escalate"
- Routing confidence below 0.80 on a case that contains any DEVIATION_STANDARD or DEVIATION_ESCALATION classification — routing tier suspended; ET-1 fires; Tom determines tier manually

**Step 2 — WS2 (if no WS3 trigger fires):**
- At least one clause classified DEVIATION_STANDARD, no WS3 triggers present, routing confidence ≥ 0.80

**Step 3 — No Redline Required (if no WS3 or WS2 trigger fires):**
- All clause classifications are MATCH, no unresolved DPA_UNVERIFIED flags, routing confidence ≥ 0.80

**Pre-deployment prerequisite:** The per-clause-type criteria for DEVIATION_STANDARD vs. DEVIATION_ESCALATION within each of the seven playbook categories must be co-developed with Amelia Forsythe and version-controlled in the playbook before the agent is deployed in production. Until that document exists, the conservative default applies: any clause the LLM cannot classify as standard-deviation with confidence ≥ 0.85 is treated as DEVIATION_ESCALATION.

---

## 6. Escalation Triggers

| Trigger ID | Condition | Escalate to | What the agent provides at escalation | Response SLA |
|-----------|-----------|-------------|---------------------------------------|-------------|
| ET-1 | Aggregate routing tier confidence score falls below the configurable routing threshold (default: 0.80) after all clause classifications are complete | Tom Reilly | Deviation report with all clause classifications, per-clause confidence scores, and a "Routing — Low Confidence" flag; routing tier is listed as "Recommended — requires human confirmation" with no default assignment | Next business day (before case proceeds to WS2 or WS3) |
| ET-2 | One or more DPA clauses detected in the contract and the playbook DPA section version timestamp predates the DPDI Act Q1 revisions [Assumption A-5] | Tom Reilly + Amelia Forsythe | Deviation report with DPA clause(s) flagged as "Unverified against current regulation — DPA playbook section not updated post-DPDI Act"; all DPA classifications carry the flag; routing decision on DPA clauses suspended until human confirmation | Same business day |
| ET-3 | Liability cap clause detected with deviation magnitude exceeding [threshold to be defined in playbook update: preliminary estimate ≥ 60% below the playbook minimum floor, e.g., <£100k vs. playbook floor of £250k — Assumption A-7] | Tom Reilly; auto-routing suggestion set to WS3 regardless of aggregate confidence score | Deviation report with liability cap clause highlighted, deviation magnitude expressed in £ and as % below playbook floor, routing suggestion locked to WS3 | Tom confirms within next business day; case held from WS2 assignment until confirmed |
| ET-4 | Document parsing failure: clause extraction completeness below minimum threshold (>10% of document sections unextracted) | Tom Reilly | Incomplete deviation report with a "Parser failure — sections unextracted" flag, list of unextracted section identifiers, and raw document attached for manual review | Same business day; Tom manually processes or re-submits the document |
| ET-5 | Contract type not among the seven defined playbook categories — no matching category found for more than 25% of identified clauses | Tom Reilly | Intake case record with "Unclassifiable — playbook gap" flag, list of unmatched clause identifiers, and the original document attached | Tom escalates to a commercial lawyer within next business day |
| ET-6 | Three or more routing decisions for a specific counterparty have been manually overridden by Tom in the current quarter | Tom Reilly + agent recalibration queue [Assumption A-6] | Ironclad flag "Systematic routing misalignment — [Counterparty] — recalibration required"; cases from that counterparty are paused for autonomous routing pending threshold review | Tom reviews within 5 business days; agent resumes autonomous routing only after explicit clearance |

---

## 7. Failure Modes

> **Failure Mode FM-1: Silent false negative — missed deviation**
> **What it looks like:** The agent classifies a non-playbook clause as "Match — No Action Required" and the deviation does not appear in the deviation report.
> **Consequence:** Tom reviews and confirms the report without seeing the deviation. The case is routed to No Redline Required or WS2. The clause proceeds through the pipeline untouched. Depending on the deviation type, this may result in a contract with a below-standard clause being executed — legal and commercial exposure. In the worst case (a missed DPA deviation), it creates a regulatory compliance gap.
> **Detection:** Weekly 10% audit by a lawyer comparing agent classification output to a human re-read; error captured as "missed deviation" in audit log. Latency: up to 1 week for audited cases; non-audited cases may not surface until downstream review or contract execution.
> **Recovery path:** The case is reopened in Ironclad, the clause is manually reclassified, and the routing decision is corrected. If the contract has already proceeded to WS4 sign-off, the lawyer at sign-off is responsible for catching the deviation — this is why the sign-off gate (C-7) exists. If the contract is already executed, Amelia is notified for legal risk assessment.

> **Failure Mode FM-2: Under-escalation — WS3-tier clause routed to WS2**
> **What it looks like:** The agent assigns a routing recommendation of WS2 (standard-deviation redlining) to a case containing a clause that, under correct interpretation, requires senior-lawyer review (WS3). Tom confirms the WS2 routing without identifying the error. The clause receives paralegal treatment.
> **Consequence:** A high-risk clause (unusual formulation, significant liability exposure, or novel legal construct) is redlined by Tom rather than reviewed by a lawyer. The redline may be technically incorrect or commercially disadvantageous. The resulting counteroffer proceeds to WS4 sign-off, where the lawyer may or may not catch the clause depending on review depth. This is the WS1 failure mode most directly connected to the scenario's governance risk — it replicates at scale the informal judgment call Tom made in Artefact 2.1 (classifying a £50k liability cap deviation as "borderline negotiable" rather than escalating).
> **Detection:** Weekly 10% audit; WS4 sign-off review if a lawyer conducts a deep read; post-execution contract review. Latency: potentially days if the case moves quickly through WS2 and WS4.
> **Recovery path:** If caught before sign-off: case is paused, re-routed to WS3, lawyer reviews and issues a corrected counteroffer. If caught after sign-off: Amelia is notified for assessment of whether the sent counteroffer constitutes a material legal exposure; commercial lawyer manages the renegotiation if required.

> **Failure Mode FM-3: DPA compliance drift — classification against stale playbook standard**
> **What it looks like:** The agent classifies a DPA clause as "Match" or "Deviation — Standard" against the current playbook DPA section, which does not reflect DPDI Act Q1 revisions (Artefact 2.3). The deviation report carries no flag because the agent's comparison is internally consistent with the (stale) playbook.
> **Consequence:** Helix may execute contracts with DPA clauses that comply with the old standard but not the current regulatory requirement. This is a latent compliance risk that accumulates across all DPA-containing contracts processed before the playbook is updated. Risk is highest for contracts with NHS trusts or other regulated-sector counterparties where DPA standards are actively audited.
> **Detection:** The DPA currency check (T-8) is specifically designed to prevent this by flagging all DPA classifications when the playbook version is pre-DPDI-Act. This failure mode occurs if T-8 is bypassed or if the version check logic is misconfigured. The weekly 10% audit covers DPA clauses; Amelia or a lawyer reviewing DPA content would notice the discrepancy.
> **Recovery path:** The playbook DPA section is updated and version-stamped (prerequisite that should have been completed before agent deployment on DPA clauses). All DPA-containing contracts processed during the stale period are identified via Ironclad logs and reviewed by Amelia for exposure assessment.

> **Failure Mode FM-4: Outlook bypass — contract processed outside the agent's monitored channel**
> **What it looks like:** A vendor submits a contract directly to Tom's personal Outlook inbox (or via a non-monitored email address), bypassing the Legal & Commercial team inbox that the agent monitors. The agent never receives the contract; Tom processes it manually without generating an Ironclad case record through the agent workflow.
> **Consequence:** The contract bypasses the agent classification entirely. Tom performs a full manual WS1 review. No structured deviation report is generated. The contract may not be logged in Ironclad at all — replicating the email-bypass pattern from Artefact 2.2 (confirmed as a recurring exception for at least 3 vendors per quarter). At scale, systematic bypass by specific vendors erodes the agent's coverage metric and creates a parallel untracked process.
> **Detection:** Weekly volume check: if Ironclad case count is materially below the expected 23 cases/week, Tom investigates for bypass contracts. Proactive measure: Tom adds a processing rule to forward non-monitored-inbox contracts to the monitored inbox; Amelia communicates the monitored address to vendors with recurring bypass behaviour.
> **Recovery path:** Tom manually creates the Ironclad case record and flags it as "Email bypass — manual intake." The contract is processed manually for that case. If the vendor is identified as a systematic bypasser, Amelia's team notifies the vendor's procurement contact of the required submission channel.

---

## 8. Out-of-Scope (Hard Stops)

The Contract Classifier Agent must **never** do the following, regardless of instruction or apparent efficiency gain:

- **Never send any communication to an external vendor, counterparty, or party outside the Helix Legal & Commercial team.** The agent's output is a deviation report written to Ironclad for internal review only. Only a named member of the Legal & Commercial team may initiate outbound communications.
- **Never write, propose, or generate redline language in a vendor contract document.** The agent's scope ends at clause classification and deviation reporting. Redline drafting belongs to WS2 (C-4) and WS3 (C-6) and requires a separate human-authorised workflow. An agent producing redline language without explicit human instruction for that purpose is operating outside its sanctioned scope.
- **Never commit a routing decision (WS2 / WS3 / No Redline Required) to Ironclad as a confirmed assignment without a recorded human confirmation event.** The routing tier may be populated as a recommendation in the deviation report, but the Ironclad field that triggers work stream assignment must be written only by the human confirmation action, not by the agent.
- **Never classify a DPA clause as a confirmed match or standard deviation when the active playbook DPA section carries a version timestamp predating the DPDI Act Q1 revisions.** All DPA classifications in this state must carry the "Unverified against current regulation" flag; the agent must not suppress or override this flag based on apparent clause quality or comparison confidence.
- **Never access Salesforce CRM data, deal value, commercial relationship history, or sales pipeline information.** Clause classification is a pure legal-document-to-playbook comparison. Commercial context belongs to WS3 legal analysis (C-5), which is Human Only. Introducing deal-value awareness into the classification step would conflate legal compliance assessment with commercial negotiation strategy — a combination that is outside the agent's sanctioned cognitive scope and Amelia's accountability framework.

---

## 9. Assumption Log

> **Assumption [A-1]:** There is no measured baseline for Tom Reilly's current WS1 clause classification accuracy. The ≥95% accuracy target is the minimum acceptable threshold for agent deployment without increasing legal risk, not a figure derived from a measured human error rate.
> **Why it matters:** If Tom's current accuracy is already below 95% (suggested by Artefact 2.1, where he made an unsanctioned judgment call), the agent is being held to a higher standard than the process it replaces. The audit design may need to establish the human baseline first.
> **If wrong:** The accuracy target may need to be reframed relative to current human performance. If the agent matches Tom's accuracy and human accuracy is <95%, the target becomes "match or beat Tom" rather than "achieve 95%."
> **Confidence:** Low

> **Assumption [A-2]:** The 20% HITL escalation rate target reflects an expectation that approximately 60 cases per quarter (20% of 300) will require a confidence-flag escalation under the current state of the playbook and escalation criteria. This is a design assumption, not a derived figure.
> **Why it matters:** If the actual low-confidence rate is higher (e.g., 40%), the agent is adding less time saving than expected — Tom confirms more cases individually.
> **If wrong:** The HITL rate target is adjusted after the first quarter of production operation based on observed confidence distribution. If consistently above 30%, the confidence threshold or the playbook specificity needs review.
> **Confidence:** Low

> **Assumption [A-3]:** An Outlook API integration is technically feasible for monitoring the Legal & Commercial team's contract intake inbox and extracting email body and Word attachments. Specific API capabilities, authentication model, and rate limits are not confirmed in the scenario.
> **Why it matters:** If Outlook integration requires IT security approval or is blocked by enterprise email policies, the intake monitoring component (T-1, T-2) may need to be replaced with a manual forwarding rule or a Shared Mailbox approach.
> **If wrong:** Intake (C-1) must be redesigned; the agent starts at T-4 (document parsing) rather than T-1, with Tom manually uploading contracts to Ironclad as an initial step.
> **Confidence:** Medium

> **Assumption [A-4]:** The SharePoint "Position Statements v3.4" playbook is accessible via SharePoint API in a machine-readable format (not an embedded image or scanned PDF). Version metadata (last-revised date) is available as a document property.
> **Why it matters:** If the playbook is stored as a non-parseable format, T-5 (playbook retrieval) must use a pre-indexed or manually maintained copy, adding a maintenance overhead and a version drift risk.
> **If wrong:** The playbook must be converted to a structured, machine-readable format as a pre-deployment prerequisite. Version tracking becomes a manual process until SharePoint metadata is confirmed accessible.
> **Confidence:** Medium

> **Assumption [A-5]:** The DPDI Act Q1 revisions took effect before the scenario date (2026-05-04) and the playbook DPA section has not been updated since the Act came into force. The specific effective date of the revisions is not stated in the scenario.
> **Why it matters:** The DPA currency check logic (T-8, ET-2) depends on comparing the playbook version timestamp against a known regulatory effective date. If the effective date is ambiguous, the currency check cannot be automated reliably.
> **If wrong:** The DPA currency check must use a human-maintained flag ("DPA section current: Yes/No") in Ironclad or SharePoint rather than an automated timestamp comparison. This adds a manual maintenance step but does not change the agent's classification logic.
> **Confidence:** Medium

> **Assumption [A-6]:** An Ironclad-based mechanism for tracking per-counterparty routing override counts is technically feasible — either via existing CLM reporting or a lightweight custom field. The specific implementation path is not confirmed in the scenario.
> **Why it matters:** ET-6 (systematic routing misalignment detection) depends on this tracking. Without it, recurring routing errors for specific counterparties will not be detected systematically.
> **If wrong:** ET-6 becomes a manual monitoring task: Tom tracks override frequency for counterparties informally. The agent recalibration pathway remains valid but loses its automated trigger.
> **Confidence:** Low

> **Assumption [A-8]:** The Ironclad case record contains a custom field named `agent_deviation_report` that can store a JSON payload of arbitrary size. The field name and type are not confirmed in the scenario.
> **Why it matters:** The deviation report schema (§4b) depends on a writable structured field in the Ironclad case record. If no such field exists, the report must be stored as a document attachment instead, which changes the T-11 implementation and makes downstream query/audit of report contents harder.
> **If wrong:** The integration contract for T-11 changes: replace the JSON field write with a document attachment upload to the Ironclad case. The report schema remains the same; only the delivery mechanism changes.
> **Confidence:** Low — the scenario confirms Ironclad REST APIs are available but does not describe the case data model.

> **Assumption [A-7]:** The specific numerical threshold for the liability cap escalation trigger (ET-3) has not been codified in the playbook. The preliminary estimate (deviation ≥60% below playbook floor, e.g., <£100k vs. £250k minimum) is derived from Artefact 2.1, where Tom informally classified a £50k cap (80% below playbook floor) as "borderline negotiable" rather than WS3. The actual threshold must be defined and version-controlled by Amelia before the agent applies it.
> **Why it matters:** If the threshold is set incorrectly (too high or too low), the agent will systematically over- or under-escalate liability cap cases. This is the same calibration problem that Tom's informal judgment creates — except at machine speed.
> **If wrong:** Amelia defines the threshold as part of the playbook update pre-deployment prerequisite. Until defined, ET-3 should use a conservative default (any liability cap deviation below the playbook floor triggers WS3 routing suggestion) rather than a percentage-based magnitude threshold.
> **Confidence:** Low
