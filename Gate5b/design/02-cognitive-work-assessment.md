# Deliverable 2 — Cognitive Work Assessment
## Delegation Analysis
**Gate 5b Final Exam · Lattice Pay AML/KYC Case Review**

ATX hierarchy: Work stream → JtD → Zone → Micro-task

---

## Phase 1 output — Work stream identified

**Work stream: BSA/AML Alert Review**

Points of pain (from Dr. Rao's brief + mock data sampling):
- 11,000 alerts/week; 31 analysts; 8.6× gap between alert volume and throughput capacity
- 58-minute average case handling time dominated by data assembly and synthesis (not judgment)
- 95% false-positive rate: most analyst time spent closing cases that should close quickly
- 6.2-day median cycle time; 7-day regulatory SLA; SAR-eligible cases sometimes caught late
- Watchlist hits are almost entirely common-name false-positives — but each requires 8 min of manual cross-referencing
- One alert type (cross-border remittance) is systematically misrouted — touches an out-of-scope product line

**Candidate process selected:** AML Alert Case Review
**Rationale for agentic candidacy:** High volume, high non-determinism, data-assembly dominated, repeatable pattern types, human judgment required only at disposition sign-off

---

## Phase 2 — Cognitive Load Map

### JtD decomposition

The work stream contains **five Jobs to be Done**, named directly from the brief's definition of the cognitive work to be delegated:

| JtD | Cognitive contract | Trigger | Actor (current) | Output |
|---|---|---|---|---|
| **JtD-1** | Ingest the alert and pull the case context | Alert fires in monitoring system | Analyst | Scope classification + complete assembled case data (KYC, tx history, network, watchlist, prior history) |
| **JtD-2** | Synthesise the alert into a narrative | Case context assembled | Analyst | Plain-language account of what happened, what triggered the rule, what context the analyst needs |
| **JtD-3** | Surface patterns | Narrative complete | Analyst | Pattern inventory with type, evidence, and severity |
| **JtD-4** | Reconcile against watchlist screening | Watchlist hit present in screening report | Analyst | Watchlist resolution (disconfirmed / unresolved) with evidence |
| **JtD-5** | Recommend a disposition | Patterns surfaced + watchlist reconciled | Analyst | Signed disposition with reasoning, span-citations, and confidence level |

---

### JtD-1: Ingest the alert and pull the case context

**Cognitive contract:** Given an alert in the queue, determine whether it is in scope, and if so retrieve all data required to understand the customer and their activity — KYC profile, last 90 days of transaction history, network of counterparties, watchlist hits, prior alert history — and identify what is missing.

**Key decisions:** In-scope (consumer/business) vs. out-of-scope (remittance, broker-dealer)? Which data sources are relevant? What gaps exist?

**Zones within JtD-1:**

| Zone | Micro-tasks | Cognitive type |
|---|---|---|
| Z1a — Alert parsing | Read alert metadata: alert_id, customer_id, triggering rule, monetary scope, timestamp | Retrieval |
| Z1b — Scope detection | Identify whether alert involves remittance product channel or broker-dealer activity | Decision |
| Z1c — Routing (out-of-scope only) | Route to correct team and halt; do not proceed to JtD-2 | Action |
| Z1d — Primary data retrieval | Fetch KYC, 90-day transaction history, watchlist screening for primary customer | Retrieval |
| Z1e — Extended data retrieval | Fetch counterparty network, prior RFI emails, OFAC SDN extract (if hit present) | Retrieval |
| Z1f — Linked account retrieval | For layering cases: fetch KYC and transaction data for each linked account ID in network file | Retrieval |
| Z1g — Gap identification | Log which data sources returned no data; assess completeness | Synthesis |

**Cognitive breakpoints:**
- After Z1b: out-of-scope → route and exit; in-scope → continue
- After Z1g: if both KYC and transaction history are missing → disposition = FURTHER_INFO_NEEDED; do not proceed to JtD-2

**Micro-task inventory:**

| Micro-task | Cog Load | Input Structure | Decision Determinism | Exception Freq | Turn-Taking | Latency | Compliance Risk | Tool Availability |
|---|---|---|---|---|---|---|---|---|
| Read alert metadata | L | H | H | L | L | L | L | H |
| Detect scope / product line | L | M | H | M | L | L | M | M |
| Route out-of-scope | L | H | H | L | L | L | H | H |
| Fetch KYC profile | L | H | H | L | L | L | M | H |
| Fetch 90-day transaction history | L | H | H | L | L | L | M | H |
| Fetch watchlist screening report | L | H | H | L | L | L | H | H |
| Fetch counterparty network | L | M | H | M | L | L | M | M |
| Fetch prior RFI thread | L | M | H | M | L | L | M | M |
| Fetch linked account KYC (×N) | L | H | H | M | L | L | M | M |
| Identify and log data gaps | M | M | M | M | L | L | M | H |

---

### JtD-2: Synthesise the alert into a narrative

**Cognitive contract:** Given the assembled case context, produce a coherent plain-language account of what happened, what triggered the rule, and what the analyst needs to know — drawing on KYC profile, transaction history, prior RFI history, and alert metadata.

**Key decisions:** What is the customer's profile? What does the 90-day activity look like? What prior history is load-bearing?

**Zones within JtD-2:**

| Zone | Micro-tasks | Cognitive type |
|---|---|---|
| Z2a — Customer profile summary | Synthesise KYC: account type, verification tier, tenure, occupation, funding sources, expected volume | Synthesis |
| Z2b — Alert trigger account | Explain what triggered the rule with specific transaction citations (dates, amounts, counterparties) | Synthesis |
| Z2c — Activity profile | Characterise the 90-day transaction profile: volume, cadence, counterparty mix, channel mix | Synthesis |
| Z2d — Prior history integration | Incorporate prior alerts, prior RFI threads, prior dispositions as context | Synthesis |

**Cognitive breakpoint:** After Z2d: narrative is the shared foundation for JtD-3, JtD-4, and JtD-5. All downstream reasoning draws from it.

**Micro-task inventory:**

| Micro-task | Cog Load | Input Structure | Decision Determinism | Exception Freq | Turn-Taking | Latency | Compliance Risk | Tool Availability |
|---|---|---|---|---|---|---|---|---|
| Summarise KYC profile | M | H | M | L | L | L | M | H |
| Explain alert trigger with citations | H | M | L | M | L | L | H | H |
| Characterise 90-day activity | H | M | L | M | L | L | M | H |
| Integrate prior history | M | M | M | M | L | L | M | H |

---

### JtD-3: Surface patterns

**Cognitive contract:** Given the assembled context and narrative, identify patterns in the transaction data consistent with money laundering — structuring across multiple transactions, layering through related accounts, sudden change in transaction profile, counterparty risk concentration, geographic/jurisdictional risk — and assign severity.

**Key decisions:** Which patterns are present? How strong is the evidence? What severity?

**Zones within JtD-3:**

| Zone | Micro-tasks | Cognitive type |
|---|---|---|
| Z3a — Structuring detection | Identify deposits clustered below CTR thresholds ($10K / $5K) across a time window | Pattern recognition |
| Z3b — Layering detection | Analyse counterparty network for multi-hop transfer chains converging at a single external account | Pattern recognition |
| Z3c — Velocity anomaly | Compare current cross-border or aggregate volume to prior-period baseline; flag sudden change | Pattern recognition |
| Z3d — Counterparty risk concentration | Assess concentration of outbound value to elevated-risk merchant list or offshore financial institutions | Pattern recognition |
| Z3e — Thin KYC / volume mismatch | Check KYC verification tier against inbound aggregate; flag tier limit breaches | Rule application |
| Z3f — Multi-pattern convergence | If ≥2 patterns detected: synthesise a MULTI_PATTERN_CONVERGENCE flag | Synthesis |

**Cognitive breakpoints:**
- Z3a–Z3e are independent of each other and can run in parallel
- After Z3f: pattern inventory feeds JtD-5 disposition logic

**Micro-task inventory:**

| Micro-task | Cog Load | Input Structure | Decision Determinism | Exception Freq | Turn-Taking | Latency | Compliance Risk | Tool Availability |
|---|---|---|---|---|---|---|---|---|
| Detect structuring pattern | M | H | M | M | L | L | H | H |
| Detect layering pattern | H | M | L | H | L | L | H | M |
| Detect velocity anomaly | M | H | H | M | L | L | H | H |
| Assess counterparty risk concentration | M | M | M | M | L | L | H | M |
| Flag thin KYC + volume mismatch | L | H | H | L | L | L | H | H |
| Synthesise multi-pattern convergence | M | H | M | M | L | L | H | H |

---

### JtD-4: Reconcile against watchlist screening

**Cognitive contract:** Given a watchlist hit in the screening report, determine — using KYC profile, SDN extract, and transaction profile — whether the hit represents genuine OFAC exposure or a false positive on a common name.

**Trigger:** Conditional — only fires when a watchlist hit is present in the screening report.

**Key decisions:** Does the customer's DOB, address, nationality, and transaction profile diverge sufficiently from the SDN entry to disconfirm the hit?

**Zones within JtD-4:**

| Zone | Micro-tasks | Cognitive type |
|---|---|---|
| Z4a — Factor extraction | Extract from KYC: DOB, address country, nationality/citizenship; extract from SDN: same fields | Retrieval |
| Z4b — Factor comparison | Compare each factor: DOB delta, address country match, nationality match | Reasoning |
| Z4c — Transaction coherence check | Assess whether transaction profile is consistent with stated occupation and expected volume | Reasoning |
| Z4d — Resolution determination | Apply disconfirmation rule: count factors; assign resolution (DISCONFIRMED / UNRESOLVED) and confidence | Decision |

**Cognitive breakpoint:** After Z4d. If WATCHLIST_UNRESOLVED → JtD-5 disposition must be FURTHER_INFO_NEEDED or ESCALATE_SAR; CLEAR is blocked.

**Hard constraint:** Positive confirmation of an OFAC SDN hit is never the agent's determination. Output vocabulary is WATCHLIST_DISCONFIRMED or WATCHLIST_UNRESOLVED only.

**Micro-task inventory:**

| Micro-task | Cog Load | Input Structure | Decision Determinism | Exception Freq | Turn-Taking | Latency | Compliance Risk | Tool Availability |
|---|---|---|---|---|---|---|---|---|
| Extract DOB / address / nationality | L | H | H | L | L | L | H | H |
| Compare DOB delta | L | H | H | L | L | L | H | H |
| Compare address / nationality | L | H | H | L | L | L | H | H |
| Assess transaction profile coherence | M | M | M | M | L | L | H | H |
| Determine resolution + confidence | M | M | M | M | L | L | H | H |

---

### JtD-5: Recommend a disposition

**Cognitive contract:** Given the pattern inventory, watchlist resolution, and case context, select the appropriate disposition value, write a rationale with span-citations to the underlying transactions, attach a confidence level, and deliver the recommendation to the analyst for validation and sign-off.

**Key decisions:** Which disposition value is correct? Is the rationale defensible to a FinCEN examiner? (Analyst makes the final call — agent proposes.)

**Zones within JtD-5:**

| Zone | Micro-tasks | Cognitive type |
|---|---|---|
| Z5a — Disposition selection | Apply decision logic to patterns + watchlist status; select one of 5 values; assign confidence | Decision |
| Z5b — Rationale and citation | Write rationale citing specific transactions, pattern evidence, and watchlist resolution | Generation |
| Z5c — Analyst review | Analyst reads case package, evaluates recommendation, applies expert judgment | Human judgment |
| Z5d — Analyst sign-off | Analyst confirms or overrides disposition; submits to case management system | Human action |

**Cognitive breakpoints:**
- Z5a–Z5b: agent proposes (recommendation + draft rationale + confidence level)
- Z5c–Z5d: **human only — irreducible** — analyst accountability and regulatory signature

**Hard constraints (from brief — never delegated to agent):**
- **SAR filing decision:** agent recommends ESCALATE_SAR; the SAR itself is drafted, reviewed, and signed by the analyst. The filing act is entirely outside LACRA's scope.
- **Customer freeze decision:** agent recommends ACCOUNT_FREEZE; analyst recommends to supervisor; supervisor approves. Two-level approval chain — neither level is delegated to the agent.
- **Any communication with the customer or any other party:** LACRA produces no outbound communication of any kind. Customer RFI emails, freeze notices, and SAR-related correspondence are human-initiated only.

**Micro-task inventory:**

| Micro-task | Cog Load | Input Structure | Decision Determinism | Exception Freq | Turn-Taking | Latency | Compliance Risk | Tool Availability |
|---|---|---|---|---|---|---|---|---|
| Select disposition value (agent) | M | H | M | M | L | L | H | H |
| Write rationale + span-citations (agent) | H | M | L | M | L | L | H | H |
| Analyst reviews case package | H | M | L | H | M | M | H | n/a |
| Analyst signs disposition / escalates SAR | H | L | L | M | L | L | H | H |
| Supervisor approves freeze (if ACCOUNT_FREEZE) | H | L | L | L | M | L | H | n/a |

---

## Phase 3 — Delegation qualification

### Delegation suitability matrix

| JtD | Input Structure | Decision Determinism | Tool Coverage | Exception Rate | Compliance Risk | Archetype |
|---|---|---|---|---|---|---|
| JtD-1: Ingest + pull context | High | High | High | Low–Medium | Medium | **Fully Agentic** |
| JtD-2: Synthesise narrative | Medium | Low | High | Medium | Medium | **Agent-led + Human Oversight** |
| JtD-3: Surface patterns | Medium–High | Medium | High | Medium | High | **Agent-led + Human Oversight** |
| JtD-4: Reconcile watchlist | High | Medium | High | Low | High | **Agent-led + Human Oversight** (disconfirmation only) |
| JtD-5: Recommend disposition | Medium | Medium | High | Medium | High | **Human-led + Agent Support** (Z5a–Z5b agent; Z5c–Z5d human; supervisor approval required for ACCOUNT_FREEZE) |

---

## Phase 4 — Volume × Value positioning

| Candidate | Volume (cases/week) | Non-determinism score | Agentic value (V×ND) | Wave |
|---|---|---|---|---|
| AML Alert Case Review (JtD-1 through JtD-5) | 11,000 | 5/5 | **25/25** | Wave 1 |

Top-right quadrant (high volume + high non-determinism): primary agentic target.

---

## Time decomposition (58 min → 18 min target)

| JtD | Current analyst time | Agent execution time | Residual analyst time |
|---|---:|---:|---:|
| JtD-1: Ingest + pull context | 15 min | <1 min | 0 min |
| JtD-2: Synthesise narrative | 10 min | ~20 sec | 2 min (read + verify) |
| JtD-3: Surface patterns | 12 min | ~20 sec | 3 min (review evidence) |
| JtD-4: Reconcile watchlist | 8 min | ~10 sec | 3 min (verify factors) |
| JtD-5: Recommend disposition | 13 min | ~20 sec (draft) | 10 min (judgment + sign) |
| **Total** | **58 min** | **<3 min** | **~18 min** |

No-SAR case (95% of volume): ~16 min (below 18-min target)
SAR-eligible case (5% of volume): ~26 min (accepted; fleet average still meets ≤18 min)
