# Prompt: Deliverable 5 — System/Data Inventory

## Scenario (read this first)
See `scenario\scenario_context.md` for the full scenario, work streams, tooling, and named-systems guidance. Do not invent numbers, systems, or constraints not present in the scenario. Every number you use must trace back to the scenario or be explicitly labelled as an assumption.

---

## Your task
Produce a System/Data Inventory. Be concise. Output file: `deliverables\D5_system_data_inventory.md`.

This inventory defines what the agent (from D4) needs to access, what is available, what is missing, and what is risky. It is the integration specification that a development team will use to assess buildability and plan their integration work.

Reference: `references\atx-agent-mapping.md` — System and Data Inventory section.

---

## Required structure

### 0. Executive summary
Three bullet points, written first. Each bullet is one sentence. Cover in order:
1. The integration that is most critical to the agent functioning at all — name the system, the data it provides, and what blocks if it is unavailable
2. The most significant gap or risk in the inventory — the system or data source whose availability is unknown or whose integration has the highest consequence if it fails
3. The compounding opportunity — the integration that, once built, reduces the cost of the next agent in this domain most

This section must be self-contained — a reader who reads only this section should understand what must be confirmed before build starts, what the biggest integration risk is, and what the long-term platform value is.

### 0b. Table of contents
List all sections by number and title as markdown anchor links, in order. Generate this after the full document is written — section titles must match exactly. Format each entry as `[N. Section title](#n-section-title)` using lowercase and hyphens for spaces. Include subsections indented under their parent.

Example format:
- [0. Executive summary](#0-executive-summary)
- [0b. Table of contents](#0b-table-of-contents)
- [1. Data and system requirements (from agent design)](#1-data-and-system-requirements-from-agent-design)
- [2. System and data inventory table](#2-system-and-data-inventory-table)
- [3. Gap analysis](#3-gap-analysis)
- [4. Risk register](#4-risk-register)
- [5. Context engineering design](#5-context-engineering-design)
  - [5b. Pre-deployment prerequisite checklist](#5b-pre-deployment-prerequisite-checklist)
- [6. Compounding opportunities](#6-compounding-opportunities)

### 1. Data and system requirements (from agent design)
Before listing available systems, derive the requirements from the agent's activity catalog (D4). What data and systems does the agent need to complete each task type?

Group requirements into categories:
- **Input data** (what the agent reads to do its work)
- **Reference data** (policy documents, playbooks, reference materials the agent consults)
- **Output targets** (systems the agent writes to, or queues it pushes results into)
- **Approval/governance channels** (how the designated approver's sign-off is captured and audited)

For each requirement, state: what data is needed, at what granularity, and at what latency (real-time lookup vs. batch-loaded vs. on-demand retrieval).

### 2. System and data inventory table
For each system or data source required:

| System/Source | Data needed | Access type | Inferred availability | Gap/Risk | Priority |
|--------------|-------------|-------------|----------------------|----------|---------|

**Access types:** Read / Write / Read-Write / RAG (retrieval-augmented generation) / Event trigger
**Inferred availability:** API likely available / API unknown / Manual/document-only / External service / Unknown
**Priority:** Required (agent cannot function without it) / Important (degrades performance if absent) / Optional (nice to have)

Include a row for each of the following (at minimum):
1. Inbound document/case storage (where work items arrive and are stored)
2. Reference policy or playbook (the primary decision framework — its format and location)
3. Case classification/case management (where triage or routing results are recorded)
4. Approval/sign-off channel (how the designated approver's approval is captured with audit trail)
5. Output tooling (where the agent's primary output artefact is produced or stored)
6. Escalation routing system (how exception cases are queued and assigned)
7. Historical precedents or examples (prior accepted and rejected outputs — if available)
8. Counterparty or entity registry (background on the external party involved — if applicable)

For systems named in scenario_context.md, note: "Named in scenario_context.md — API specifics and integration maturity are assumptions beyond what is stated." For any additional systems you introduce, note: "Not named in scenario — existence and API availability are assumptions."

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
- **Sign-off integrity risk** (can the approval mechanism be bypassed — accidental or intentional?)
- **Governance enforcement mechanism risk** (is the approval technically enforced by the system — workflow lock, write-block, required state transition — or is it a procedural agreement that relies on the designated approver's discipline? If policy-only, what prevents a bypass under time pressure?)

The governance/approval integrity risk (protecting the scenario's primary hard constraint in the system design) must appear in this register. The entry must distinguish between system-enforced and procedure-dependent enforcement — these carry different risk profiles.

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
- How is retrieval quality evaluated? (false positive matches can have downstream compliance or business consequences — address this)
- How are retrieval costs managed? (chunking strategy, caching, index structure)

#### Key context engineering risks
List 2–3 risks specific to this agent's context design (e.g., "reference policy language may be ambiguous — multiple valid interpretations of the same category").

### 5b. Pre-deployment prerequisite checklist

Before build begins, the following must be confirmed. List each item as:
- [ ] **[System or data item]:** [what specifically must be confirmed] — **Confirmed by:** [who confirms] — **If unconfirmed:** [what is blocked]

Required entries (at minimum):
1. Reference material format — machine-readable (structured/text-extractable) vs. image or scan-based; if any section is image-based, OCR preprocessing is a prerequisite
2. Reference material version control — is there a machine-readable "last updated" timestamp or revision history queryable by the agent?
3. Primary write-target system — API write access confirmed for custom fields and workflow state transitions required by the agent design
4. Inbound trigger mechanism — intake path (email, API, manual upload) confirmed and approved by any relevant IT security stakeholder
5. Approval/audit trail — designated approver sign-off is logged with identity and timestamp in a queryable system; not just visible but retrievable
6. Known-stale reference sections — any sections identified as out of date before deployment must either be updated or explicitly excluded from agent scope with a defined fallback behaviour

---

### 6. Compounding opportunities
Which integrations built for this agent could be reused by future agents in this team or this organisation?

| Integration built | Future agent that could reuse it | Reuse mechanism |
|------------------|----------------------------------|-----------------|

---

## Acceptance criteria (all must pass)

- [ ] Data and system requirements derived from the agent's activity catalog, not invented independently
- [ ] At least 8 system/data sources in the inventory table
- [ ] Every system that is not named in the scenario is labelled as an assumption
- [ ] Gap analysis present for every system with "unknown" or "manual-only" availability
- [ ] Risk register includes sign-off integrity risk
- [ ] Risk register distinguishes system-enforced approval mechanisms from policy-only ones; if policy-only, the bypass risk is explicitly rated
- [ ] Pre-deployment checklist present with at least 6 entries; each names what is confirmed, who confirms it, and what is blocked if unconfirmed
- [ ] Context engineering design addresses retrieval quality evaluation (not just retrieval mechanism)
- [ ] Compounding opportunities section present
- [ ] All gaps rated for severity (Blocking / Degrading / Low) with mitigation options

## Fail signals — do not produce output that contains these

- Systems not confirmed in scenario_context.md stated as facts without labelling them as assumptions
- A gap analysis that says "this data may not be available" without a mitigation option
- Context engineering design that only describes what is retrieved, not how quality is evaluated
- Governance/approval integrity risk absent from the risk register
- Risk register that lists sign-off integrity risk without assessing whether it is system-enforced or procedure-only
- Risk register with all risks rated Low — that is not analysis
- Pre-deployment checklist absent — gaps named without specifying what must be confirmed before build begins
