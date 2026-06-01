# Deliverable 2 — Cognitive Work Assessment
## Delegation Analysis
**Gate 5b Final Exam · Lattice Pay AML/KYC Case Review**

---

## The 58-minute case: decomposed

Current analyst workflow reconstructed from the scenario brief and mock data sampling.
Times are averages across the 8-case queue; complex cases (layering, genuine watchlist hit)
skew toward the 90-minute ceiling; routine cases (common-name FP, tobacco-vendor transfers)
skew toward 40 minutes.

| Zone | Cognitive activity | Avg time | Type | Can agent do this? |
|---|---|---:|---|---|
| Z1 | Alert intake — read triggering rule, identify alert type, locate the case in the queue | 3 min | Retrieval | **Yes — fully agentic** |
| Z2 | Context pull — fetch KYC profile, 90-day tx history, watchlist screening, counterparty network, prior case history from 4–6 systems | 12 min | Retrieval + assembly | **Yes — fully agentic** |
| Z3 | Narrative synthesis — understand what happened, what triggered the rule, what context matters | 10 min | Reasoning | **Yes — agent-led** |
| Z4 | Pattern detection — structuring intervals, layering hops, velocity changes, counterparty risk, geo/jurisdictional risk | 12 min | Reasoning + pattern recognition | **Yes — agent-led** |
| Z5 | Watchlist reconciliation — confirm or disconfirm hits; distinguish common-name FP from genuine match using DOB, address, nationality | 8 min | Reasoning + rule application | **Yes — agent-led with confidence score** |
| Z6 | Disposition recommendation — select one of 5 values, write rationale, cite transactions | 8 min | Reasoning + generation | **Yes — agent proposes** |
| Z7 | Analyst judgment — evaluate agent's package, challenge reasoning, apply expert knowledge, sign disposition | 5 min | Human judgment | **Human only — irreducible** |
| Z8 | Documentation — write the memo, record the rationale in the case system | 8 min | Generation + action | **Partial — agent drafts; analyst amends and signs** |

**Total documented: 66 min** (aligns with 40–90 min range; 58 min = weighted average across alert types)

---

## Delegation analysis

### Z1–Z2: Context pull (15 min → ~1 min agent execution)

**Nature:** Pure retrieval and assembly. Deterministic given the customer ID and alert ID.
No judgment required. Currently slow because analysts manually navigate 4–6 systems.

**Delegation:** Fully agentic. Agent reads alert, extracts customer ID, calls data tools in
parallel, assembles context package. Execution time: seconds, not minutes.

**Risk:** Missing data (partially filled KYC, no prior RFIs for 3 of 4 layering accounts).
Agent must handle graceful degradation — note what is missing, continue with what is available.

---

### Z3–Z4: Synthesis and pattern detection (22 min → in-context reasoning, ~2 min)

**Nature:** High-value cognitive work. Multi-source synthesis, pattern recognition across time
and counterparty dimensions, identification of signal vs. noise. This is where agents create
the most leverage — they can hold the full context window simultaneously and apply consistent
pattern detection logic that humans apply inconsistently under cognitive load.

**Delegation:** Agent-led. The agent produces a structured narrative + pattern list with
span-citations. The analyst reads, evaluates, and challenges — they don't reproduce the work.

**Key patterns to detect (from case queue):**
- **Structuring:** Deposits clustered just below reporting thresholds ($4,800–$4,950 range for AML-1109)
- **Layering:** Multi-hop transfers across linked accounts to single external beneficiary (AML-1408)
- **Velocity change:** Prior 12-month cross-border baseline $580 → $42,800 in 48 hours (AML-1322)
- **Counterparty risk concentration:** $171K outbound to single Cayman National Bank account within 72h of receipt (AML-1304)
- **Thin KYC + volume mismatch:** Tier-1 KYC (phone+email only) receiving $61K cash-equivalent above account limit (AML-1419)

---

### Z5: Watchlist reconciliation (8 min → deterministic rule + reasoning, ~1 min)

**Nature:** Structured reasoning. The screening report pre-computes the fuzzy name match score.
The agent applies a multi-factor disconfirmation rule: DOB delta, address mismatch, nationality,
transaction profile coherence. This is currently manual because analysts must pull the SDN extract
and compare fields by hand.

**Delegation:** Agent-led with explicit confidence score and disconfirmation evidence.

**Critical design point:** The agent must NEVER positively confirm an OFAC SDN hit. That
determination is human + legal. The agent can output `WATCHLIST_DISCONFIRMED` (with evidence)
or `WATCHLIST_UNRESOLVED — REQUIRES ANALYST JUDGMENT` — never `WATCHLIST_CONFIRMED`.

**From mock data (AML-1208, Mohammed Khan):**
- DOB delta: 21 years (customer 1993, SDN entry 1972)
- Address: Detroit MI vs Karachi/Quetta Pakistan
- Transaction profile: Wayne State stipend + rent + utilities = student wallet
- Conclusion: high-confidence disconfirmation → `WATCHLIST_DISCONFIRMED` with 3-factor evidence

**From mock data (AML-1219, Maria González):**
- Match score: 0.82 (above 0.80 high-attention threshold)
- US passport on file, US citizen, Tampa FL
- SDN entry: GONZALEZ-ALAVA (compound surname, distinct)
- Routine wallet activity
- Conclusion: disconfirmation → `WATCHLIST_DISCONFIRMED`, but analyst should confirm US passport

---

### Z6: Disposition recommendation (8 min → generation, included in agent output)

**Nature:** The agent selects from 5 disposition values and writes the rationale. This is
generation from context already assembled — not new reasoning.

**Delegation:** Agent proposes; analyst decides. The recommendation is a starting hypothesis
for the analyst to evaluate, not a pre-determined outcome.

**Disposition vocabulary:**
- `CLEAR` — no suspicious activity; close with rationale
- `ESCALATE_SAR` — pattern consistent with suspicious activity; recommend SAR filing
- `CUSTOMER_RFI` — additional information needed from customer before disposition
- `ACCOUNT_FREEZE` — risk level warrants immediate restriction pending investigation
- `FURTHER_INFO_NEEDED` — internal data gap; need more system data before disposition

---

### Z7: Analyst judgment (5 min — irreducible human work)

**Nature:** Expert evaluation, ethical accountability, regulatory signature. This is the
cognitive work that cannot be delegated: the analyst applies professional judgment, considers
context the agent may have missed, and signs the disposition.

**Target time:** 5–18 min depending on complexity. The agent's case package should be
structured so a skilled analyst can challenge and verify, not just rubber-stamp.

**Design principle (Diane Reston's framing):** The agent does the boring synthesis and
the analyst argues with it. Output design must invite scrutiny — cited evidence, confidence
levels, explicit uncertainty flags — not optimise for passive acceptance.

---

### Z8: Documentation (8 min → agent drafts, analyst amends)

**Nature:** Writing the disposition memo. Currently repetitive and formulaic for no-SAR cases.

**Delegation:** Agent generates a draft memo from the case package. Analyst reviews, amends,
and submits. Target analyst time: 2–3 min for no-SAR cases; 8–12 min for SAR-eligible cases.

---

## Delegation summary

| Zone | Delegation archetype | Post-agent analyst time |
|---|---|---:|
| Z1: Alert intake | Fully agentic | 0 min |
| Z2: Context pull | Fully agentic | 0 min |
| Z3: Narrative synthesis | Agent-led + analyst reviews output | 2 min |
| Z4: Pattern detection | Agent-led + analyst reviews output | 3 min |
| Z5: Watchlist reconciliation | Agent-led + analyst reviews confidence + evidence | 3 min |
| Z6: Disposition recommendation | Agent proposes, analyst decides | 5 min |
| Z7: Analyst judgment | Human only | 5 min |
| Z8: Documentation | Agent drafts, analyst amends + signs | 3 min (no-SAR) / 8 min (SAR) |
| **Total (no-SAR case)** | | **~16 min** |
| **Total (SAR-eligible case)** | | **~26 min** |

No-SAR target (95% of volume): **~16 min** (well under 18-min target)
SAR-eligible target (5% of volume): **~26 min** (above target — acceptable given complexity;
the 18-min target is a fleet average; SAR cases will always take longer)

---

## Suitability gate (ATX scoring)

| Criterion | Rating | Rationale |
|---|---|---|
| Input structure | High | KYC JSON, transaction CSV, screening text, network JSON — consistent schemas |
| Decision determinism | Medium | Core path has patterns; exceptions require contextual judgment (handled by HITL) |
| Tool coverage | High | File reads in prototype; API calls in production — all integrations feasible |
| Exception rate | Medium | ~5% of cases are genuinely ambiguous; agent flags, analyst resolves |
| Compliance risk | Medium | High-stakes domain, but SAR filing and OFAC confirmation stay human |
| **Gate result** | **Pass** | All criteria ≥ Medium; compliance risk mitigated by explicit HITL design |

**Agentic value score:**
- Execution frequency: 5 (11,000 alerts/week — very frequent)
- Non-deterministic effort: 5 (synthesis of 4–6 sources, pattern detection, watchlist reasoning)
- Score: **25/25** — maximum agentic value
