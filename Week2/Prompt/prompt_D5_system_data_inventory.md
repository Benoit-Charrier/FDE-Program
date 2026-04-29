# Prompt: Deliverable 5 — System/Data Inventory

## Scenario (read this first)
See `scenario\scenario_context.md` for the full scenario, work streams, tooling, and named-systems guidance. Do not invent numbers, systems, or constraints not present in the scenario. Every number you use must trace back to the scenario or be explicitly labelled as an assumption.
---

## Your task
Produce a System/Data Inventory. Be concise. Summarize the main 3 points at the end.Output file: `deliverables\D5_system_data_inventory.md`.

This inventory defines what the agent (from D4) needs to access, what is available, what is missing, and what is risky. It is the integration specification that a development team will use to assess buildability and plan their integration work.

Reference: `references\atx-agent-mapping.md` — System and Data Inventory section.

---

## Required structure

### 1. Data and system requirements (from agent design)
Before listing available systems, derive the requirements from the agent's activity catalog (D4). What data and systems does the agent need to complete each task type?

Group requirements into categories:
- **Input data** (what the agent reads to do its work)
- **Reference data** (policy documents, playbooks, precedent clauses the agent consults)
- **Output targets** (systems the agent writes to, or queues it pushes results into)
- **Approval/governance channels** (how lawyer sign-off is captured and audited)

For each requirement, state: what data is needed, at what granularity, and at what latency (real-time lookup vs. batch-loaded vs. on-demand retrieval).

### 2. System and data inventory table
For each system or data source required:

| System/Source | Data needed | Access type | Inferred availability | Gap/Risk | Priority |
|--------------|-------------|-------------|----------------------|----------|---------|

**Access types:** Read / Write / Read-Write / RAG (retrieval-augmented generation) / Event trigger
**Inferred availability:** API likely available / API unknown / Manual/document-only / External service / Unknown
**Priority:** Required (agent cannot function without it) / Important (degrades performance if absent) / Optional (nice to have)

Include a row for each of the following (at minimum):
1. Inbound contract document storage (where contracts arrive and are stored)
2. Negotiation playbook (the 7-clause checklist — its format and location)
3. Contract classification/case management (where triage results are recorded)
4. Lawyer approval/sign-off channel (how named-lawyer approval is captured with audit trail)
5. Redline/markup tooling (where the paralegal's or agent's redlines are produced)
6. Escalation routing system (how the 10% escalation cases are queued and assigned)
7. Historical contract precedents (prior accepted and rejected clause language — if available)
8. Vendor/counterparty registry (background on the vendor submitting the contract)

For systems named in the enriched scenario (Ironclad, SharePoint, Salesforce, Outlook, Word), note: "Named in the enriched scenario — API specifics and integration maturity are assumptions beyond what is stated." For any additional systems you introduce, note: "Not named in scenario — existence and API availability are assumptions."

### 3. Gap analysis
For each gap (system with unknown or unavailable access):

> **Gap [G-N]:** [system/data name]
> **What the agent cannot do without it:** [specific task from the activity catalog that is blocked]
> **Severity:** Blocking (agent cannot launch) / Degrading (agent can launch with reduced capability) / Low (workaround exists)
> **Mitigation options:** [list 2–3 realistic options — manual workaround, alternative data source, phased approach]
> **Discovery action:** [what question to ask the client to resolve this gap]

### 4. Risk register
For each system or data source, assess the integration risk:

| System | Risk type | Risk description | Likelihood (H/M/L) | Impact (H/M/L) | Mitigation |
|--------|-----------|-----------------|-------------------|----------------|------------|

Risk types to consider:
- **Data quality risk** (is the playbook in a machine-readable format, or is it a Word document?)
- **API availability risk** (does an API exist? Is it documented? Is there a rate limit?)
- **Legal/compliance risk** (does the agent's access to contract data create new GDPR or privilege exposure?)
- **Audit trail risk** (can the agent's actions be logged in a way that satisfies legal's audit requirements?)
- **Sign-off integrity risk** (can the lawyer approval mechanism be bypassed — accidental or intentional?)

The sign-off integrity risk (protecting the GC's hard rule in the system) must appear in this register.

### 5. Context engineering design
Design the agent's information architecture:

#### Memory architecture
| Memory type | Content | Storage mechanism | Lifecycle |
|-------------|---------|------------------|-----------|
| In-context (short-term) | | | |
| Semantic (long-term, retrieval) | | | |
| Procedural (static instructions) | | | |

#### Retrieval strategy
- What triggers a retrieval call? (give specific examples from the activity catalog)
- What is the retrieval target? (top-K clause chunks? exact playbook section? structured record?)
- How is retrieval quality evaluated? (false positive clause matches have legal consequences — address this)
- How are retrieval costs managed? (chunking strategy, caching, index structure)

#### Key context engineering risks
List 2–3 risks specific to this agent's context design (e.g., "playbook language may be ambiguous — multiple valid interpretations of the same clause type").

### 6. Compounding opportunities
Which integrations built for this agent could be reused by future agents in this legal team or this company?

| Integration built | Future agent that could reuse it | Reuse mechanism |
|------------------|----------------------------------|-----------------|

---

## Acceptance criteria (all must pass)

- [ ] Data and system requirements derived from the agent's activity catalog, not invented independently
- [ ] At least 8 system/data sources in the inventory table
- [ ] Every system that is not named in the scenario is labelled as an assumption
- [ ] Gap analysis present for every system with "unknown" or "manual-only" availability
- [ ] Risk register includes sign-off integrity risk
- [ ] Context engineering design addresses retrieval quality evaluation (not just retrieval mechanism)
- [ ] Compounding opportunities section present
- [ ] All gaps rated for severity (Blocking / Degrading / Low) with mitigation options

## Fail signals — do not produce output that contains these

- Systems not in the scenario (DocuSign, Slack, etc.) stated as facts without labelling them as assumptions — Ironclad, SharePoint, Salesforce, Outlook, and Word are confirmed in the enriched scenario; anything else is an assumption
- A gap analysis that says "this data may not be available" without a mitigation option
- Context engineering design that only describes what is retrieved, not how quality is evaluated
- Sign-off integrity risk absent from the risk register (this is the highest-consequence risk in this scenario)
- Risk register with all risks rated Low — that is not analysis
