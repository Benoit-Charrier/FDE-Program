# Deliverable 3 — Agent Purpose Document
## Autonomy Matrix & Escalation Triggers
**Gate 5b Final Exam · Lattice Pay AML/KYC Case Review**

---

## Agent Purpose Document

**Agent Name:** Lattice Pay AML Case Review Agent (LACRA)

**Job to be Done:**
Given a BSA/AML monitoring alert and associated case data, assemble a structured case package —
narrative, pattern analysis, watchlist status, and disposition recommendation — that enables an
AML analyst to make a fully documented judgment call in ≤18 minutes without retrieving data
from any system themselves.

**Business context:**
BSA/AML Compliance, Lattice Pay Inc. Consumer wallet + business account alert review pipeline.
Operates within the 7-day regulatory SLA for alert disposition. Reports to the analyst review
queue managed by the CCO organisation.

---

### Primary objectives

1. Reduce per-case analyst handling time from 58 min to ≤18 min by delivering a complete,
   citable, structured case package before the analyst opens the case.
2. Surface genuine suspicious patterns (structuring, layering, watchlist, counterparty risk)
   with sufficient evidence for the analyst to determine whether a SAR is warranted.
3. Disconfirm common-name watchlist false-positives with documented evidence so analysts
   do not spend 8 minutes manually reconciling names that differ by 21 birth years.
4. Detect and route out-of-scope cases (remittance product, broker-dealer) before analyst
   time is spent on them.
5. Produce reproducible dispositions: identical inputs must yield identical outputs.

---

### KPIs

| KPI | Target | Measurement |
|---|---|---|
| Analyst handling time per case | ≤ 18 min average | Time-tracked from package delivery to signed disposition |
| SAR-eligible detection precision | ≥ 75% | Agent recommends ESCALATE_SAR → analyst confirms SAR |
| SAR-eligible recall | ≥ 95% | Analyst files SAR → agent had recommended ESCALATE_SAR or ACCOUNT_FREEZE |
| Watchlist false-positive disconfirmation accuracy | ≥ 99% | Agent WATCHLIST_DISCONFIRMED → analyst agrees |
| Out-of-scope routing accuracy | 100% | Remittance/broker-dealer cases are routed, not analysed |
| Disposition reproducibility | 100% | Same inputs re-run → identical disposition + reasoning |
| Case package delivery time | ≤ 60 seconds | From alert ID received to case package returned |
| HITL escalation rate | ≤ 5% | Cases where agent cannot produce a disposition and returns FURTHER_INFO_NEEDED |

---

### Failure modes

| Failure | Consequence | Recovery |
|---|---|---|
| False negative on SAR-eligible case (agent clears a genuine SAR) | Regulatory exposure; SAR filed late or not at all | Recall ≥ 95% requirement; analyst reviews all CLEAR dispositions before signing; audit trail enables retrospective review |
| False positive OFAC confirmation (agent escalates a clear FP) | Analyst time wasted; customer churn risk if freeze follows | Agent never confirms OFAC positively; WATCHLIST_UNRESOLVED always escalates to analyst with evidence |
| Missing data for key field | Incomplete case package; analyst reverts to manual research | Agent outputs `data_gaps` list with each missing field; logs which systems returned no data; analyst fills manually for that case |
| Out-of-scope case processed instead of routed | Agent analyses remittance case using wrong rule set | Scope detection runs first, before any analysis; routing is the first decision gate |
| Reproducibility failure (re-run yields different disposition) | Audit integrity failure; FinCEN explainability broken | Temperature = 0 on all model calls; inputs are deterministic; system prompt is version-controlled |

---

### Delegation archetype

Per-JtD archetypes (from cognitive work assessment):

| JtD | Name | Archetype |
|---|---|---|
| JtD-1 | Ingest the alert and pull the case context | Fully Agentic |
| JtD-2 | Synthesise the alert into a narrative | Agent-led + Human Oversight |
| JtD-3 | Surface patterns | Agent-led + Human Oversight |
| JtD-4 | Reconcile against watchlist screening | Agent-led + Human Oversight (disconfirmation only) |
| JtD-5 | Recommend a disposition | Human-led + Agent Support |

**Overall system characterisation: Agent-led + Human Oversight** — the agent executes
JtD-1 through JtD-4 autonomously and supports JtD-5 with a recommendation. The analyst
reviews, challenges, and signs. The agent does not re-execute data assembly or pattern
detection; the analyst does not retrieve raw data.

Rationale: The cognitive work is high-volume, pattern-rich, and consistent enough for reliable
agentic execution. The stakes (SAR filing, OFAC determination, account freeze) require human
accountability and judgment. The per-JtD breakdown shows that full autonomy is appropriate
for retrieval (JtD-1) and narrows progressively toward human oversight as reasoning complexity
and compliance stakes increase (JtD-4, JtD-5).

---

### Escalation triggers

| Trigger | Condition | Action |
|---|---|---|
| Out-of-scope detection | Alert involves remittance product or broker-dealer activity | Immediately output `ROUTE_OUT_OF_SCOPE` with routing destination; halt analysis |
| Genuine OFAC match unresolvable | Watchlist hit cannot be disconfirmed with available data (DOB, address, nationality do not clearly diverge from SDN entry) | Output `WATCHLIST_UNRESOLVED`; disposition = `FURTHER_INFO_NEEDED`; flag for senior analyst |
| Layering pattern with ≥3 linked accounts | Network analysis shows multi-hop transfers consistent with layering (≥3 hops, funds converge to single external account) | Disposition = `ESCALATE_SAR`; flag as High priority |
| Confidence below threshold | Agent confidence score < 0.5 on disposition recommendation | Append explicit uncertainty flag; recommend analyst seek second opinion; do not suppress the package |
| Missing critical data | KYC profile unavailable AND transaction history unavailable (both missing for a linked account) | Disposition = `FURTHER_INFO_NEEDED`; list specific data needed; do not guess |
| SAR-eligible pattern detected | Structuring across ≥5 transactions below threshold, or layering, or counterparty + velocity + cross-border combined signal | Disposition = `ESCALATE_SAR`; confidence level attached |
| Tier limit breach | Customer at Tier-1 KYC with aggregate inbound exceeding $25K/30-day limit | Disposition = `ACCOUNT_FREEZE` recommendation; note limit breach with dollar amount; freeze itself requires analyst recommendation → supervisor approval (two-level chain) |

---

## Autonomy Matrix

### AGENT DECIDES ALONE (no HITL required)

- Alert intake: read alert, extract customer ID, alert ID, triggering rule
- Data retrieval: fetch KYC profile, transaction history, watchlist screening, counterparty network, prior case history for the primary customer ID
- Scope detection: classify alert as in-scope (consumer/business) or out-of-scope (remittance/broker-dealer)
- Narrative synthesis: produce plain-language description of what happened and why the rule fired
- Pattern detection: identify structuring intervals, velocity changes, layering hops, counterparty risk, geo risk
- Watchlist disconfirmation: output `WATCHLIST_DISCONFIRMED` when DOB + address + nationality evidence clearly diverges from SDN entry
- Draft disposition memo: generate memo text from case package

### AGENT ACTS, HUMAN NOTIFIED AFTER

- Case package delivery: write structured JSON case package to analyst queue (read: no action taken in external systems)
- Data gap logging: log which data sources returned no data for this case

### AGENT PROPOSES, HUMAN APPROVES BEFORE ACTION

- Disposition recommendation: agent outputs one of {CLEAR, ESCALATE_SAR, CUSTOMER_RFI, ACCOUNT_FREEZE, FURTHER_INFO_NEEDED} with reasoning and confidence; analyst signs
- Watchlist unresolved flag: agent surfaces WATCHLIST_UNRESOLVED; analyst makes the determination
- Out-of-scope routing: agent recommends routing destination; routing action taken by human

### HUMAN TAKES OVER (agent supports only)

- SAR filing decision: analyst signs; agent provides case package as supporting documentation only
- Customer freeze or wallet restriction: analyst recommends → supervisor approves (two-level chain); agent provides case package
- OFAC positive confirmation: NEVER agent's determination; agent surfaces evidence; analyst + legal counsel decide
- Any communication with the customer or any third party: human only

---

## Activity catalog

### JtD-1: Ingest the alert and pull the case context

| Task | Type | Delegation | Data required | Tool | Risk |
|---|---|---|---|---|---|
| Parse alert metadata | Retrieval | Fully agentic | Alert ID, customer ID, rule code | read_alert | Low |
| Detect scope / product line | Decision | Fully agentic | Alert type, channel | classify_scope | Low |
| Route out-of-scope case | Action | Agent flags / human routes | Scope classification | write_routing_flag | Low |
| Fetch KYC profile | Retrieval | Fully agentic | Customer ID | read_kyc | Low |
| Fetch 90-day transaction history | Retrieval | Fully agentic | Customer ID | read_transactions | Low |
| Fetch watchlist screening report | Retrieval | Fully agentic | Customer ID | read_watchlist | Low |
| Fetch counterparty network | Retrieval | Fully agentic | Customer ID | read_network | Low |
| Fetch prior RFI history | Retrieval | Fully agentic | Customer ID | read_rfi_history | Low |
| Fetch linked account KYC (×N) | Retrieval | Fully agentic | Linked IDs from network file | read_kyc (×N) | Low |
| Identify and log data gaps | Synthesis | Fully agentic | All retrieval results | None (in-context) | Low |

### JtD-2: Synthesise the alert into a narrative

| Task | Type | Delegation | Data required | Tool | Risk |
|---|---|---|---|---|---|
| Summarise KYC profile | Reasoning | Agent-led | KYC JSON | None (in-context) | Medium |
| Explain alert trigger with citations | Reasoning | Agent-led | Transaction history, alert metadata | None (in-context) | Medium |
| Characterise 90-day activity | Reasoning | Agent-led | Transaction history | None (in-context) | Medium |
| Integrate prior RFI history | Reasoning | Agent-led | Prior RFI thread | None (in-context) | Medium |

### JtD-3: Surface patterns

| Task | Type | Delegation | Data required | Tool | Risk |
|---|---|---|---|---|---|
| Detect structuring pattern | Reasoning | Agent-led | Transaction history | None (in-context) | High |
| Detect layering pattern | Reasoning | Agent-led | Network + transaction history | None (in-context) | High |
| Detect velocity anomaly | Reasoning | Agent-led | Transaction history + baseline | None (in-context) | High |
| Assess counterparty risk concentration | Reasoning | Agent-led | Transaction history, network | None (in-context) | High |
| Flag thin KYC + volume mismatch | Decision | Agent-led | KYC tier, inbound aggregate | None (in-context) | High |

### JtD-4: Reconcile against watchlist screening

| Task | Type | Delegation | Data required | Tool | Risk |
|---|---|---|---|---|---|
| Extract DOB / address / nationality factors | Retrieval | Agent-led | KYC, SDN extract | None (in-context) | High |
| Compare factors against SDN entry | Reasoning | Agent-led (disconfirm only) | KYC + SDN extract + screening report | None (in-context) | High |
| Assess transaction profile coherence | Reasoning | Agent-led | Transaction history, KYC occupation | None (in-context) | High |
| Output resolution + confidence | Decision | Agent-led (disconfirm only) | All above | None (in-context) | High |

### JtD-5: Recommend a disposition

| Task | Type | Delegation | Data required | Tool | Risk |
|---|---|---|---|---|---|
| Select disposition value | Decision | Agent proposes / analyst decides | Full case package | None (in-context) | High |
| Write rationale + span-citations | Generation | Agent drafts / analyst amends | Case package | None (in-context) | High |
| Generate case package JSON | Generation | Fully agentic | All above | write_case_package | Low |
| Analyst reviews and signs disposition | Decision | Human only | Case package | Case mgmt system | High |
| Supervisor approves freeze (if ACCOUNT_FREEZE) | Decision | Human only | Case package + analyst recommendation | Case mgmt system | High |
