# Delegation Suitability Matrix — MiniBase Community Moderation

Aggregates dimension scores from the Cognitive Load Map across all four work streams. Archetype assignments are drawn directly from CLM per-micro-task scores; rationale references specific step clusters.

---

## Aggregate Dimension Scores

Scores reflect the dominant pattern across all micro-tasks in each work stream. Where a small cluster of steps scores materially higher (the peak risk cluster), both values are shown — dominant / peak — because the peak cluster often drives the archetype assignment even when the majority of steps score low.

| Work Stream | Cognitive Load | Input Structure | Decision Determinism | Exception Frequency | Turn-Taking | Latency | Compliance / Risk | Tool Availability |
|---|---|---|---|---|---|---|---|---|
| WS1 — Routine Spam | Low | High | High | Low | Low | Low | Low / **High** (steps 4–5) | High / Medium (step 4) |
| WS2 — Grey-Zone Review | High | Low | Low | High | Low / **High** (step 14) | Low / **High** (step 9) | **High** | Low |
| WS3 — Dispute Appeals | Medium | Medium | Medium | Medium | Low | Low | Medium / **High** (steps 3–4, 9) | High / Low (steps 9, 11) |
| WS4 — IP Claims | **High** (steps 4–8) | Low | Low (steps 4–8) | **High** (steps 4–8) | Low | Low | **High** | Low (steps 4–8) |

---

## WS1 — Routine Spam / Clear Violations

**Archetype: Human-led + Automation Support**

**Rationale:** All 9 micro-tasks score Low Cognitive Load and High Decision Determinism — every decision is a Boolean check against enumerable criteria. High volume (1,080/day) makes automation viable and valuable, but the exception routing logic (steps 4–5) carries High Compliance/Risk, ruling out a fully autonomous LLM agent. A rules engine + API integration is more reliable and cheaper than an LLM for deterministic rule application; the LLM adds noise without adding value here.

**Driving dimensions:**
- Decision Determinism = High across all steps → rules engine, not an agent
- Exception Frequency = Low → exception path is narrow and well-defined
- Tool Availability = High (Discourse API) → automation is technically straightforward
- Compliance/Risk = High at steps 4–5 (exception screen) → sponsor miss is the 2024 incident risk; this step requires the automation to be verified, not just deployed

**Delegation boundary:**

| Layer | What it may do | What it may NOT do |
|---|---|---|
| Automation | Ingest flag from Discourse queue; check account history; check exception list; apply spam/off-topic rule; close flag + log action | Take any action on a Tier 1 (sponsor) or Tier 2 (special user) account; make any removal decision without a matched rule |
| Human (moderator) | Override automation decision; review edge cases flagged as no-match | — |
| Escalation | Any case without a rule match → WS2 queue; any Tier 1/2 account match → Tom | — |

---

## WS2 — Grey-Zone Case Review

**Archetype: Human-led + Agent Support**

**Rationale:** Exception-bound judgment work where every case is, by definition, outside the rule set. Steps 10–12 form the judgment core (High Cognitive Load + Low Decision Determinism + High Compliance/Risk + Low Tool Availability) — these steps are undelegatable. However, six earlier steps (context assembly, precedent search, reporter analysis) are high-effort, low-judgment work the agent can handle. The agent reduces the moderator's preparation burden; the moderator retains all decision authority.

**Driving dimensions:**
- Cognitive Load = High at judgment core (steps 10–12) → undelegatable
- Decision Determinism = Low across the majority of steps → judgment cannot be encoded
- Compliance/Risk = High at 7 of 14 steps → wrong decision risk is existential (Tom's stated asymmetry)
- Tool Availability = Low for sub-forum norms, Discord precedent, and cultural context → agent cannot query these without new structured data sources
- Exception Frequency = High at steps 8, 10–12, 14 → these are the cases with the highest stakes

**Delegation boundary:**

| Layer | What it may do | What it may NOT do |
|---|---|---|
| Agent | Check user account against Tom's Sheet (Tier 1/2); retrieve sub-forum norm from structured source (if created); pull thread context and reporter history; surface Discord #mod-decisions precedents; flag viral risk indicator; draft decision rationale for moderator review | Screen for Tier 3 accounts (no structured data); apply a sub-forum norm it cannot find in a structured source; make a content decision; close a flag; communicate with users |
| Human (moderator) | Assess cultural/regional context; weigh false-negative vs. false-positive risk; decide action; review + edit rationale | — |
| Human (Tom) | All Tier 1 and Tier 2 account cases without exception; any viral escalation | — |

---

## WS3 — User Dispute Appeals

**Archetype: Human-led + Agent Support**

**Rationale:** Policy check and case retrieval are structured enough for agent assistance, but the final decision (uphold/overturn, steps 8–9) requires Senior Moderator judgment — Decision Determinism drops to Low and Compliance/Risk peaks to High at exactly these steps. Communication drafting (step 11) adds a relationship and tone dimension that resists full delegation. Volume (60/day) is lower than WS2, but the irreversibility of an overturn decision and the community trust stakes justify keeping final authority with a named human role.

**Driving dimensions:**
- Decision Determinism = Low at steps 8–9 (reassessment + overturn decision) → judgment core
- Compliance/Risk = High at steps 3–4 (special account routing) and step 9 (overturn) → same sponsor-miss risk as WS1/WS2 for the routing steps; community trust risk for the overturn
- Tool Availability = High for most steps (Discourse stores all original case data) → agent support is technically feasible for retrieval and policy check
- Turn-Taking = Low throughout → no coordination bottleneck; agent can work ahead of the moderator

**Driving dimensions that keep it Human-led rather than Agent-led:**
- Steps 8–9 are the core value of the work stream (the decision itself) and score Low DD + High C/R simultaneously — the agent cannot take this call
- Step 11 (communication drafting) is relationship-sensitive; agent may draft but human must approve before sending

**Delegation boundary:**

| Layer | What it may do | What it may NOT do |
|---|---|---|
| Agent | Retrieve original case + moderation log; check for special account in Tom's Sheet; surface relevant policy clauses; surface prior decisions on similar cases; draft appeal response for human review | Check original case involved Tom's original action (needs Tom-self-identification); decide uphold/overturn; send communication to appellant; apply content changes in Discourse |
| Human (Senior Moderator) | Read and assess appellant's argument; make uphold/overturn decision; review and approve drafted communication | — |
| Human (Tom) | All appeals where original action was Tom's, or original case involved a sponsor/special account | — |

---

## WS4 — IP Claim Resolution

**Archetype: Human-only**

**Rationale:** Steps 4–8 form a five-step judgment core where every dimension that blocks delegation scores at maximum simultaneously: High Cognitive Load, Low Decision Determinism, High Exception Frequency, High Compliance/Risk, Low Tool Availability. Claimant credibility is tacit knowledge (lives in Tom's head; Q3 confirms no structured tool will exist in the near term). A content takedown is irreversible. The claimant relationship carries legal and commercial stakes. Volume is 3–5 cases per week — too low to justify the infrastructure investment required to even partially delegate. Steps 1–3 and 9–10 are automatable in isolation but are not worth isolating given the volume.

**Driving dimensions:**
- Cognitive Load = High at steps 4–8 → tacit knowledge work
- Decision Determinism = Low at steps 4–8 → no enumerable criteria; triage criteria live in Tom's head
- Compliance/Risk = High at 8 of 10 steps → content takedown is irreversible; legal exposure; sponsor relationship risk
- Tool Availability = Low at steps 4–8 → no structured credibility tool; no claim-merit assessment system
- Volume = 3–5/week → ROI does not justify partial delegation build

**Delegation boundary:**

| Layer | What it may do | What it may NOT do |
|---|---|---|
| Automation (long-term) | Log receipt of claim email; check claimant name against Tom's Sheet for prior history flag; locate disputed content in Gallery Rails | Assess claimant credibility; assess claim merit; determine response; draft legal correspondence; apply takedown |
| Human (Tom) | All steps 4–10 without exception | — |

**Blocker for any future delegation upgrade:** Q3 (stakeholders_quiz) flags that triage criteria live in Tom's head and it is unclear whether they will be documented. Until at least a structured credibility heuristic exists and is formalised, no agent can triage WS4 cases. This is a named data gap in the System/Data Inventory.

---

## Anti-Pattern Check

Four work streams, four different archetypes:
- Human-led + Automation Support (WS1)
- Human-led + Agent Support (WS2, WS3)
- Human-only (WS4)

No work stream assigned Fully Agentic or Agent-led + Human Oversight. This is correct, not conservative: the exception routing in WS1 carries Compliance/Risk = High (sponsor miss risk), the judgment core in WS2 is five steps deep with no queryable data, WS3's decision is irreversible, and WS4 is entirely tacit. The primary agentic target is WS2 — the agent support layer there is the highest-value opportunity in the system.

Zero Fully Agentic assignments ≠ anti-pattern in this scenario. Tom's stated asymmetry ("absorb a lot of false positives to avoid one viral false negative") makes any fully autonomous action on content decisions inappropriate at current maturity. The correct progression is: automate WS1 → build agent support for WS2 → establish trust data → revisit WS2 archetype upgrade.
