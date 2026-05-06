# Volume × Value Analysis — MiniBase Community Moderation

## V×V Grid

| Work Stream | Volume Score (1–5) | Non-Determinism Score (1–5) | V×V | Quadrant |
|---|---|---|---|---|
| WS1 — Routine Spam / Clear Violations | 5 | 1 | 5 | Automate (rules engine) |
| WS2 — Grey-Zone Case Review | 4 | 5 | 20 | Primary agentic target |
| WS3 — User Dispute Appeals | 3 | 3 | 9 | Agent-assisted |
| WS4 — IP Claim Resolution | 1 | 5 | 5 | Human-only |

## Scoring Notes

**WS1 — Volume 5, Non-Determinism 1**
~1,080 cases/day (72% of queue). Every decision is a Boolean check against enumerable criteria — spam pattern match, sub-forum placement, exception list lookup. Decision Determinism = High across all 9 micro-tasks. Non-Determinism = 1 by definition: when a rule applies, the outcome is fixed. High volume + deterministic rules → rules engine, not an agent. LLM adds cost and variance without adding value here.

**WS2 — Volume 4, Non-Determinism 5**
~360 cases/day (24% of queue). Every case is, by definition, outside WS1's rule set. Decision Determinism = Low for 9 of 14 micro-tasks. The moderator must synthesise sub-forum norms, cultural context, account tier, Discord precedent, and asymmetric risk weighting to reach a decision — no single data source determines the outcome. This is the textbook LLM-agent use case: high volume + high non-determinism + multi-source synthesis required.

**WS3 — Volume 3, Non-Determinism 3**
~60 cases/day (4% of queue). Policy check and case retrieval are structured (Medium DD), but the final uphold/overturn decision drops to Low DD and the communication layer adds relationship sensitivity. Mixed profile: the structured portion benefits from agent support; the judgment core does not. V×V = 9 — worth building agent support but not the primary target.

**WS4 — Volume 1, Non-Determinism 5**
~3–5 cases/week. Highest non-determinism in the system (tacit claimant credibility knowledge, legal register judgment, irreversible content takedown) but lowest volume by a wide margin. Low volume + high non-determinism → human-only. Even scoping WS4 automation to the mechanical steps only (steps 1–3 and 9–10: email receipt logging, Sheet lookup, Gallery content retrieval, action application, correspondence archiving), recoverable time is ~5 min/case × 4 cases/week = **~20 minutes/week**. The build required to get there — Gallery Rails API integration, email ingestion pipeline, Tom's Sheet read access, structured logging — is non-trivial (see System/Data Inventory for availability ratings). At 20 recoverable WS4 minutes/week, the payback horizon on even a minimal build is measured in years. ROI does not justify the investment.

---

## Primary Agentic Target: WS2 — Grey-Zone Case Review

**V×V score: 20** — well above the ≥15 threshold for a strong agentic candidate.

WS2 wins over alternatives for three reasons:

**1. Volume justifies the build.** At 360 cases/day, the moderator team spends ~30 hours/day on grey-zone work alone (360 × 5 min). This is the single largest time sink on the team and the one driving the capacity crisis. Even a 40% reduction in per-case preparation time returns ~12 hours/day to the team.

**2. The non-determinism is the right kind for an agent.** WS2 requires multi-source synthesis (thread context, account tier, sub-forum norms, Discord precedent, cultural context) before any judgment can be made. This context assembly is high-effort, low-judgment work — exactly where an LLM agent adds value without needing to make the decision itself. The judgment core (steps 10–12) remains human; the agent removes the preparation burden that currently consumes most of the 5-minute case time.

**3. WS1 is the wrong target despite higher volume.** WS1 scores V×V = 5 because Non-Determinism = 1. A rules engine handles WS1 faster, cheaper, and more reliably than an LLM agent. Building an agent for WS1 would be a misuse of the technology — and would expose the sponsor exception routing (steps 4–5, High C/R) to the hallucination risk that a rules engine eliminates by design.

**Why not WS3?** V×V = 9 is a secondary candidate. The structured portion of WS3 (policy retrieval, case context assembly) overlaps with WS2 agent capabilities — the same context-assembly agent built for WS2 likely handles WS3 preparation with minimal additional scope. WS3 is a compounding opportunity once WS2 is built, not a separate primary target.

---

## Quadrant Map

```
Non-Determinism
5 │         WS4 (5)        WS2 (20) ← PRIMARY TARGET
  │
3 │                        WS3 (9)
  │
1 │         WS1 (5)
  └─────────────────────────────────
            Low vol        High vol     Volume
            (1–2)          (4–5)
```

WS2 sits in the high-volume + high non-determinism quadrant — the only quadrant where an LLM agent is both justified and value-generating.

---

## Economics

### Step 1 — Baseline Cost Model

WS2 is the primary agentic target; this model covers grey-zone case review only.

```
Time per case:        5 minutes (0.083 hours) — confirmed in scenario brief
Fully loaded hourly:  £70/hour [Assumed: medium confidence — UK community manager;
                      range £50–120; no salary data in brief]
Cost per case:        0.083 × £70 = £5.83
Annual volume:        360 cases/day × 250 working days = 90,000 cases/year
Annual baseline cost: 90,000 × £5.83 = £524,700/year
```

**Indirect costs (material for this scenario):**
- **Sponsor relationship cost** — the 2024 incident (one mishandled sponsor case → founder call) demonstrates that even a single false negative carries relationship and revenue risk disproportionate to case volume. This is not modelled as a £ figure [Assumed: low confidence — no sponsor revenue data in brief] but is the primary driver of the 100% Tier 1/2 accuracy KPI.
- **Queue cost** — moderator team is at 47 hours/day capacity; overflow forces either delayed decisions or volunteer burnout. No SLA breach penalty is quantified in the brief.

---

### Step 2 — Token Economics Model

Agent: WS2 Grey-Zone Context Agent. Model: `claude-haiku-4-5-20251001`.

**Token consumption per case [Assumed: medium confidence — estimated from APD scope; not measured]:**

| Component | Tokens | Notes |
|---|---|---|
| System prompts (2) | ~600 input | Reporter signal assessment + rationale generation prompts; stable, cache-eligible |
| Flagged post + thread context (20 posts) | ~3,000 input | Variable; capped at 20 posts |
| Account tier data + sub-forum norm | ~300 input | Short structured lookups |
| Reporter comments | ~500 input | Variable; 1–10 reporters |
| LLM output (2 calls) | ~600 output | Signal quality sentence + rationale template |
| **Total per case** | **~4,400 input / ~600 output** | |

**Cost per case (Haiku pricing ~$0.80/1M input, $4/1M output):**

```
Input:  4,400 / 1,000,000 × $0.80  = $0.0035
Output:   600 / 1,000,000 × $4.00  = $0.0024
Token cost per case:                  $0.006  (~£0.005)
```

| Cost component | Per case | Notes |
|---|---|---|
| Token cost | £0.005 | Haiku tier; estimate |
| Tool call cost (Discourse + Sheet + Stripe API) | £0.003 | [Assumed: low confidence — ~5 API calls × ~£0.0006 avg] |
| Infrastructure | £0.001 | Negligible at prototype scale |
| HITL cost | £0.38 | 15% escalation rate × 3 min review × £70/hr reviewer |
| **Total agent cost per case** | **£0.39** | HITL dominates |

**Unit saving:** £5.83 − £0.39 = **£5.44/case (93% reduction)**

Token cost is negligible; HITL cost dominates. The business case is primarily a function of the escalation rate, not token pricing.

---

### Step 3 — ROI Business Case

```
Annual saving:        90,000 cases × £5.44 = £489,600/year

Build cost [Assumed: medium confidence — single agent, 3–4 integrations]:
  Assessment + design:     £5,000
  Development:            £20,000
  Integration + testing:  £10,000
  Change management:       £3,000
  Total build cost:       £38,000

Annual maintenance:   £6,000 (15% of build cost) [Assumed: medium confidence]

Year 1 net:           £489,600 − £38,000 − £6,000 = £445,600
Payback period:       £38,000 / £489,600 × 12 = ~1 month
3-year net value:     (£489,600 × 3) − £38,000 − (£6,000 × 3) = £1,412,800
```

**Financial Sensitivity Table**

| Scenario | Token cost | HITL rate | Agent cost/case | Annual saving | Payback |
|---|---|---|---|---|---|
| Conservative | +50% | 25% | £0.66 | £464,850/yr | ~1 month |
| Base case | Current | 15% | £0.39 | £489,600/yr | ~1 month |
| Optimistic | −30% | 8% | £0.22 | £505,890/yr | ~1 month |

The payback period is robust across all scenarios because HITL cost (not token cost) dominates agent cost, and the baseline is large. Even at a 25% HITL rate and inflated token prices, the business case holds comfortably. The only scenario that would materially change the case: HITL rate exceeds ~85%, which would require the agent to be nearly useless — contradicted by the APD scope.

---

### Step 4 — Self-Financing Roadmap

The V×V analysis identified WS3 (User Dispute Appeals) as a compounding opportunity — the same Discourse integration, Sheet lookup, and context-assembly capability built for WS2 covers WS3 preparation work.

```
Wave 1 — WS2 Grey-Zone Context Agent (months 0–4):
  Build cost:       £38,000
  Annual saving:    £489,600
  Payback:          ~1 month
  Platform assets built: Discourse API integration, Google Sheet lookup,
                         Stripe tier check, context-assembly pipeline,
                         audit log, escalation routing

Wave 2 — WS3 Appeal Context Agent (months 4–8):
  Reused from Wave 1: Discourse integration, Sheet lookup, audit log
  Estimated build cost reduction: £12,000–15,000 (shared integration setup)
  Reduced build cost: ~£20,000–25,000
  Additional annual saving: ~60 cases/day × 250 days × £4/case saved [Assumed] = £60,000/yr

Cumulative 3-year value (WS2 + WS3):
  Total investment:  £38,000 + £25,000 + (£6,000 + £4,000) × 3 = £93,000
  Total saving:      £489,600 × 3 + £60,000 × 2.5 = £1,618,800
  Net 3-year value:  £1,525,800
```

Wave 1 pays back in ~1 month and funds Wave 2 entirely from savings. The platform assets built for WS2 cut WS3 build cost by ~35–40%, which is the compounding thesis in practice.
