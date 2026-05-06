# D0A — Domain Research: Last-Mile Logistics / Regional Parcel Carrier — Customer Operations

**Domain:** Last-mile logistics / regional parcel carrier operations
**Produced:** 2026-05-06
**Status:** Draft — awaiting FDE review

> **Note on methodology:** Sections 1–5 are produced from domain knowledge prior to scenario analysis. This is a prior model, not a post-hoc analysis of the client. Client-specific deviations will surface in discovery and are captured in D0D.

---

## 0. Executive summary

- Customer operations in last-mile logistics consumes the most skilled human attention at the **exception triage point** — where a driver's unstructured field report must be matched to contract terms, customer history, and live route state to produce an actionable decision within minutes, while the driver sits parked.
- The dominant compliance constraint is the combination of **UK GDPR** (personal delivery data) and **Consumer Rights Act 2015** (credit/refund obligations), which together require a documented, auditable justification for every charge adjustment and create a hard delegation stop for credits above a formalised threshold.
- The highest-leverage agentic opportunity is **ETA inquiry and first-pass exception classification** (high volume, structured inputs, lookup-and-respond); the critical unknown is whether the billing system provides real-time API access — without it, billing disputes (the highest-value case type) can be triaged but not resolved autonomously.

---

## 0b. Table of contents

- [0. Executive summary](#0-executive-summary)
- [0b. Table of contents](#0b-table-of-contents)
- [1. Domain overview](#1-domain-overview)
  - [1a. What this domain does](#1a-what-this-domain-does)
  - [1b. Typical workflow](#1b-typical-workflow)
  - [1c. Common failure modes](#1c-common-failure-modes)
- [2. Regulatory and compliance context](#2-regulatory-and-compliance-context)
- [3. Cognitive work patterns typical to this domain](#3-cognitive-work-patterns-typical-to-this-domain)
  - [3a. Where skilled attention is typically consumed](#3a-where-skilled-attention-is-typically-consumed)
  - [3b. Lived vs. documented gaps typical to this domain](#3b-lived-vs-documented-gaps-typical-to-this-domain)
- [4. ATX dimension pre-assessment](#4-atx-dimension-pre-assessment)
- [5. Hypothesis questions for discovery](#5-hypothesis-questions-for-discovery)
- [6. Assumption log](#6-assumption-log)

---

## 1. Domain overview

### 1a. What this domain does

Regional parcel carriers operate a Customer Operations function whose core purpose is to manage the gap between what the delivery network promises and what actually happens at the point of delivery. Primary knowledge workers are: **dispatchers** (operational decision-makers who manage live route exceptions), **customer service agents** (inquiry and complaint handlers), and **billing clerks** (charge query resolution). Primary inputs are inbound customer contacts (calls, email, SMS), driver field reports (via app or phone), and system-generated alerts (missed scan, failed delivery attempt). Primary outputs are resolved CRM cases, driver instructions, credit or adjustment decisions, and escalation records. For a mid-size regional carrier serving 150–250 vehicles, customer operations handles 500–1,000 contacts per day across all channels, with strong daily and seasonal peaks tied to consumer delivery volumes.

### 1b. Typical workflow

*Domain-typical workflow — client deviations will surface in discovery.*

1. Trigger received: inbound contact (call, email, SMS) or driver-initiated report via app or phone. `[execution]`
2. Case created or retrieved in CRM; customer and order record pulled. `[execution]`
3. Case type classified: ETA inquiry / delivery exception / billing dispute / dispatch adjustment. `[judgment]`
4. Data retrieval: GPS/route status check, delivery scan history, invoice record, customer account history. `[execution]`
5. Decision or response: provide ETA estimate, issue instruction to driver, apply credit, or escalate to duty manager. `[judgment]`
6. Resolution logged in CRM; driver and/or customer notified. `[execution]`
7. Audit record created for any credit, adjustment, or formal refusal. `[verification]`
8. Escalation path (if case exceeds agent authority): duty manager or billing team review and sign-off. `[coordination]`

### 1c. Common failure modes

- **Data failure — billing and CRM not integrated in real time.** Billing records update on a batch cycle; agents make credit decisions against stale invoice data, leading to over- or under-adjustment and reconciliation errors.
- **Process failure — SOP references retired systems.** SOPs are updated infrequently; when systems are replaced, agents follow informal workarounds and the documented procedure becomes misleading.
- **Judgment failure — exception decisions made inconsistently.** When dispatcher discretion is the primary mechanism, similar cases get different outcomes depending on who handles them and how busy they are at the time.
- **Coordination failure — billing dispute routing loop.** Disputes arrive in customer ops but require billing team access to resolve; the handoff creates multi-day delays and customer drop-off between contacts.
- **Process failure — informal credit application without audit trail.** Under call pressure, agents apply small credits without formal approval or logging, creating compliance exposure that surfaces in audits.

---

## 2. Regulatory and compliance context

| Framework / Constraint | What it governs | Agent design implication |
|------------------------|----------------|--------------------------|
| UK GDPR / Data Protection Act 2018 | Personal data of delivery recipients: name, address, contact history, delivery records | Agent must not surface personal data to unauthorised parties; all data retrieval must be logged; right-of-access requests require traceable audit trail |
| Consumer Rights Act 2015 | Customer entitlements for damaged or undelivered goods: refund, repair, replacement | Agent credit decisions must align with CRA thresholds; credits above a defined amount must be human-approved to ensure legal defensibility |
| Consumer Contracts Regulations 2013 | Distance selling terms, delivery obligations, right of refusal | Agent-generated rejection or refusal decisions must be logged with justification and be overridable by a human |
| Financial conduct / invoice accuracy | Accuracy of billing records; credit note audit trail requirements | Any agent-issued or agent-recommended credit must generate a traceable record; informal override without audit trail is a compliance gap |
| Road transport / operator licensing | Driver hours compliance; route plan adherence | Dispatch adjustments that could breach driver hours must flag to a compliance-aware human before execution; agent cannot autonomously approve changes that affect hours |

---

## 3. Cognitive work patterns typical to this domain

### 3a. Where skilled attention is typically consumed

> **Cognitive hotspot CH-1: Exception triage — damaged or refused delivery**
> **Cognitive type:** Judgment + pattern recognition
> **Why it resists simple automation:** The agent must integrate an unstructured driver field report (often verbal, often incomplete) with customer contract terms, delivery history, consignment value, and live operational context (driver has n more drops, time is ticking). No two exceptions are identical, and the decision has immediate operational consequences that are difficult to reverse once the driver moves on.
> **What would make it delegatable:** Structured damage/refusal form submitted by the driver at point of exception; clear decision rules keyed to consignment value and customer tier; confidence-scored recommendation with HITL escalation above a threshold. High exception frequency with moderate determinism — a HITL co-pilot is achievable before full autonomy.

> **Cognitive hotspot CH-2: Billing dispute assessment and credit decision**
> **Cognitive type:** Synthesis + decision-making
> **Why it resists simple automation:** Requires cross-referencing invoice data, delivery outcome, customer account history, and credit policy — across systems that rarely share data in real time. The dispute often spans multiple contacts over days, requiring the agent to reconstruct context across a broken thread.
> **What would make it delegatable:** Real-time API access to billing system plus CRM; rules engine with confidence scoring; human approval gate for credits above a formal threshold. Without billing API access, the agent can triage and log but cannot close.

> **Cognitive hotspot CH-3: Dispatch adjustment under time pressure**
> **Cognitive type:** Decision-making (time-critical)
> **Why it resists simple automation:** Requires simultaneous awareness of current route state, driver capacity, traffic conditions, and customer priority — data spread across dispatch console, driver app, and GPS feed. Decisions must be made in minutes and have immediate consequences for downstream drops.
> **What would make it delegatable:** Structured optimisation inputs from an integrated dispatch console; clear priority rules for common scenarios (additional pickup, diversion, driver swap); HITL confirmation required for all adjustments. Fully agentic is not viable here without integrated data access and a defined priority hierarchy.

### 3b. Lived vs. documented gaps typical to this domain

> **Gap G-1: SOP references retired tools**
> **What SOP says vs. what typically happens:** The SOP specifies steps in systems that have been decommissioned or replaced; agents follow informal workarounds that exist only in tribal knowledge.
> **Why it exists:** System refresh cycles run ahead of documentation update cycles; there is no formal process for SOP version control triggered by system changes.
> **Agent design implication:** An agent built from the SOP alone would call wrong endpoints, reference unavailable fields, and fail on basic task execution. Discovery must identify the gap between documented and actual workflows before any agent is designed.

> **Gap G-2: Credit authority exercised informally**
> **What SOP says vs. what typically happens:** Credits are supposed to require documented approval above a threshold; in practice, agents apply small credits informally to close cases under call pressure, without logging or dual approval.
> **Why it exists:** Approval friction adds time agents do not have during peak periods; thresholds are often set at a level that is technically required but practically bypassed.
> **Agent design implication:** An agent built from the documented process would under-apply credits and generate customer escalations. An agent mirroring actual behaviour would apply credits without audit trail, creating compliance exposure. The threshold must be formally re-established as part of agent design, not inherited from informal practice.

> **Gap G-3: Exception decisions driven by dispatcher tacit knowledge**
> **What SOP says vs. what typically happens:** SOP provides a step-by-step procedure; experienced dispatchers pattern-match from memory — "this driver, this customer, this type of route" — in ways that are not codified.
> **Why it exists:** Exception frequency and variability exceeds what a deterministic SOP can cover; the tacit knowledge is faster and usually more accurate than the written procedure.
> **Agent design implication:** An agent trained from the SOP alone would produce lower-quality exception decisions than an experienced dispatcher. Effective agent design requires surfacing and encoding the tacit decision logic through structured discovery, not relying on the documented procedure.

---

## 4. ATX dimension pre-assessment

| ATX Dimension | Domain-typical signal | What to probe in discovery |
|---------------|----------------------|---------------------------|
| **Volume & Time** | High volume: 500–1,000 cases/day for a mid-size carrier. Wide time-per-case range: 2–5 min (ETA), 10–20 min (exceptions), 20–35 min (billing disputes). Strong daily and seasonal variation. | Actual volume by case type; average handle time from CRM; peak-to-trough ratio; staffing model |
| **Cognitive Nature** | Mixed: ETA inquiries are largely rule-bound (lookup-and-respond); exceptions and billing disputes are judgment-heavy with high exception rate and low decision determinism | What % of cases close without escalation? What does an agent decide vs. refer? Where does the most re-work occur? |
| **Data & Systems** | Typically fragmented: CRM, driver app, dispatch console, and billing system are rarely fully integrated. Billing is the most common integration gap — legacy systems with batch export only. | API availability on billing and dispatch systems; real-time vs. batch data; CRM as single source of truth vs. parallel tracking |
| **Risk & Compliance** | Moderate-to-high: credits and adjustments carry financial risk; personal delivery data is in scope for GDPR; audit trail obligations apply to credits and refusals; prior automation failures create stakeholder risk | Credit authority thresholds; audit log requirements; any regulatory incidents; what the COO considers non-negotiable |
| **Organisational** | Flat with informal escalation paths; dispatcher discretion high; billing typically handled by a separate function with its own access model | Who has credit authority and at what threshold? Who can override a dispatcher? How is driver compliance managed? What did prior automation attempts look like? |

**Most constraining dimension for agent design: Data & Systems.** Billing disputes are the highest-value case type — longest handling time, highest customer churn risk, and greatest financial exposure — yet billing systems in regional carriers are typically the least integrated with the rest of the stack. Batch-export-only architectures are common in legacy on-prem billing systems, and they mean an agent cannot query or modify billing records in real time. This creates a hard ceiling on autonomous dispute resolution regardless of how well the decision logic is designed. If this constraint is confirmed in discovery, it shapes the entire delegation architecture: billing becomes a triage-and-route problem, not an autonomous resolution problem, until the system integration is addressed.

---

## 5. Hypothesis questions for discovery

> **HQ-1: Does the billing system expose a real-time API, or is data available only through batch export?**
> **Hypothesis being tested:** Billing systems in regional carriers of this age and scale are commonly legacy on-prem with batch-export-only architecture — no real-time query or write capability.
> **If confirmed:** Billing dispute automation is constrained to triage and logging; the agent cannot close disputes autonomously. System integration becomes a prerequisite investment before full automation is viable.
> **If disconfirmed:** Billing disputes become viable for full agentic resolution with appropriate credit-authority thresholds.

> **HQ-2: What is the actual exception rate — what percentage of daily deliveries generate a customer operations case?**
> **Hypothesis being tested:** ~5–8% of deliveries generate an exception requiring human intervention; this is the primary driver of unplanned agent workload.
> **If confirmed:** Exception handling is the primary automation target by volume; designing the exception triage agent is the highest-ROI first scope.
> **If disconfirmed:** If the exception rate is lower, ETA inquiries dominate the volume picture and become the primary first-pass automation target.

> **HQ-3: Are exception decisions currently made from a codified decision tree, or is dispatcher discretion the primary mechanism?**
> **Hypothesis being tested:** Most dispatchers pattern-match from experience rather than following an enforced decision tree; the SOP exists but is not the actual decision driver.
> **If confirmed:** Agent needs HITL design for exceptions; fully autonomous exception resolution would produce inconsistent outcomes without encoding the tacit decision logic first.
> **If disconfirmed:** If a codified tree exists and is consistently followed, higher automation fidelity is achievable sooner.

> **HQ-4: What is the credit authority threshold — below what amount can an agent apply a credit without a human approval step?**
> **Hypothesis being tested:** This threshold exists informally (agents self-regulate based on experience) rather than as a formally stated, consistently enforced policy.
> **If confirmed:** The threshold must be formalised as part of agent design; the agent needs explicit enforcement and audit logging where the informal threshold has created compliance exposure.
> **If disconfirmed:** If a formal threshold exists and is consistently applied, the agent can be built to it directly without a policy design step.

> **HQ-5: Is the CRM the system of record for case resolution, or do agents maintain parallel tracking outside it?**
> **Hypothesis being tested:** For multi-day cases (billing disputes, complex exceptions), agents maintain informal tracking in email, spreadsheets, or personal notes because the CRM workflow is not well-suited to cases that span multiple contacts.
> **If confirmed:** Data quality work is a prerequisite; the agent cannot rely on CRM as a reliable single source of truth for dispute history.
> **If disconfirmed:** CRM is the authoritative input, simplifying integration scope significantly.

> **HQ-6: How do drivers submit exception reports — structured form fields, free-text message, or verbal call?**
> **Hypothesis being tested:** Driver input is primarily verbal or free-text via a messaging app, with low structure and high variability in what information is included.
> **If confirmed:** Agent needs NLP-based structured extraction before it can act on driver reports; input standardisation is a prerequisite for exception triage automation.
> **If disconfirmed:** If driver input is already structured (required form fields), exception triage becomes significantly more directly automatable.

> **HQ-7: Have there been regulatory incidents — customer complaints to an ombudsman, GDPR data subject requests, billing audit findings?**
> **Hypothesis being tested:** Informal credit application without audit trail creates compliance exposure; it has likely surfaced in an internal or external audit review.
> **If confirmed:** Compliance requirements will constrain agent autonomy on billing; human approval becomes mandatory at lower thresholds and audit logging becomes a non-negotiable design requirement.
> **If disconfirmed:** Lower current risk means more latitude for agent design, but the audit gap should still be closed proactively.

> **HQ-8: What does a dispatcher actually do during an 18-minute dispatch adjustment — what information do they pull, in what sequence, across how many systems?**
> **Hypothesis being tested:** Dispatchers run a mental checklist drawing on driver GPS, route state, customer priority, and vehicle capacity — data spread across 2–3 systems, none of which are integrated in real time.
> **If confirmed:** Agent needs multi-system integration to replicate this; Citrix-hosted or proprietary dispatch consoles may have limited programmatic access, which would block or significantly complicate automation.
> **If disconfirmed:** If dispatch adjustments are simpler and more data-contained than assumed, scope and technical complexity are lower.

> **HQ-9: Is there a formal escalation trigger for high-value consignments (e.g., above a defined threshold), and is it consistently followed in practice?**
> **Hypothesis being tested:** Escalation thresholds exist in the SOP but are inconsistently applied; under time pressure, dispatchers skip the escalation step for consignments that technically require it.
> **If confirmed:** Agent must enforce escalation thresholds mechanically, compensating for human under-escalation rather than mirroring current practice.
> **If disconfirmed:** If escalation is consistently followed, the agent can mirror current behaviour at this decision point.

> **HQ-10: What specifically broke in the two prior automation initiatives — was the failure technical (system integration), design (wrong scope), or adoption (people didn't use it)?**
> **Hypothesis being tested:** Prior failures were caused by brittle system integrations (the billing reconciliation RPA broke on schema changes) and/or over-promising automation coverage on judgment-heavy tasks (the customer chatbot couldn't handle exceptions).
> **If confirmed:** Scope this engagement conservatively; start with highest-structure tasks; treat brittle integrations as a first-class risk and name mitigation explicitly in the design.
> **If disconfirmed:** If failures were primarily adoption or change management failures, technical scope can be broader — but change management investment must be explicit in the plan and budget.

---

## 6. Assumption log

> **Assumption A-1:** Daily volume is approximately 500–1,000 customer operations contacts per day for a mid-size regional carrier.
> **Why it matters:** Drives ROI calculation, staffing displacement analysis, and agent capacity planning. Determines whether automation economics are compelling.
> **If wrong:** If volume is lower (e.g., <300/day), automation ROI may not justify investment at this stage. If higher (>1,200/day), urgency and scope both increase.
> **Confidence:** Medium
> **How to validate:** Request daily case volume by type from CRM reporting or call log extract; ask for peak vs. average ratio.

> **Assumption A-2:** Average handle time varies significantly by case type: ~2–5 min for ETA inquiries, ~10–20 min for delivery exceptions, ~20–35 min for billing disputes.
> **Why it matters:** Drives handle-time reduction calculations and prioritisation of automation scope. If billing disputes are shorter than assumed, they are lower priority; if ETA inquiries are longer, they are higher priority.
> **If wrong:** If billing disputes average less than 15 minutes, exceptions become the primary ROI driver. If ETA inquiries average more than 8 minutes, they represent a larger automation opportunity than this model assumes.
> **Confidence:** Medium
> **How to validate:** Request average handle time per case type from CRM or workforce management system; spot-check with a call listening session.

> **Assumption A-3:** The billing system is likely legacy on-prem with batch-export-only data availability — no real-time query or write API.
> **Why it matters:** Determines whether billing disputes can be resolved autonomously or only triaged and routed. If this assumption holds, it caps the agent's autonomy on the highest-value case type.
> **If wrong:** If a billing API is available, the full dispute resolution workflow becomes automatable with appropriate guardrails, changing the prioritisation model substantially.
> **Confidence:** Medium-high (batch-export architectures are prevalent in carriers of this age and scale; real-time billing APIs are more common in modern cloud-native systems)
> **How to validate:** Request system architecture overview; ask specifically whether billing data is accessible in real time or only via scheduled export.

> **Assumption A-4:** Dispatcher discretion is the primary decision mechanism for delivery exceptions — no enforced codified decision tree governs these decisions in practice.
> **Why it matters:** Determines delegation archetype. If rule-based: higher autonomy is viable. If discretion-based: HITL co-pilot is required and encoding tacit logic is a prerequisite step.
> **If wrong:** If a formal decision tree exists and is consistently followed, exception handling can be more fully automated sooner, without a knowledge-capture phase.
> **Confidence:** Medium-high (typical in carriers of this size; formal enforcement of exception decision trees is uncommon)
> **How to validate:** Ask dispatchers to walk through 2–3 recent exception decisions step by step; compare against any documented procedure.

> **Assumption A-5:** Prior automation failures involved at least one brittle system integration and/or over-scoped automation of judgment-heavy tasks — the failures were not purely adoption or change management.
> **Why it matters:** Shapes how conservatively the scope should be defined and which risks to name explicitly to the COO. If technical failure was the cause, conservative scoping and integration-first design are essential. If adoption was the cause, the technical scope can be broader but change management must be budgeted.
> **If wrong:** If failures were purely change management or user adoption (and the technical integrations worked), scope conservatism may be less necessary — but the change management lesson must be central to the engagement plan.
> **Confidence:** Low (no information yet on the actual failure modes; this is a domain-typical prior only)
> **How to validate:** Ask the COO directly: "What specifically broke — was it the technology, the scope, or how people responded to it?"
