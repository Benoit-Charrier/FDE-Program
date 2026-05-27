# Prompt: P7 — Economics Sketch

## Methodology references

- `References/atx-economics.md` — digital labour economics, token cost modelling, ROI framework

## Inputs

- `Scenario/scenario_context.md` — §3 (volume, metrics), §2 (stakeholder concerns)
- `Deliverables/D2C_volume_value.md` — §3 (recommended agent scope + volume coverage)

## Your task

Produce an order-of-magnitude economics sketch. The goal is to confirm the business case closes before committing to the agent design — not to produce a full sensitivity analysis.

Output file: `Deliverables/07-economics.md`

---

## Required structure

### 0. One-line verdict
"The business case [closes / does not close] under conservative assumptions." One sentence with the primary ROI figure.

### 1. Baseline cost (current state)
Estimate the current cost of the work the recommended agent will handle.

| Cost component | Calculation | Annual cost |
|----------------|-------------|-------------|
| FTE cost for targeted tasks | [headcount × % time on target JtDs × fully-loaded cost] | |
| Error / rework cost | [if stated in scenario] | |
| SLA penalty or opportunity cost | [if stated] | |
| **Total baseline** | | |

Label every input that is not stated in the scenario as an assumption with confidence level.

### 2. Agent cost (future state)
Estimate the cost of running the agent at the scenario's stated volume.

| Cost component | Calculation | Annual cost |
|----------------|-------------|-------------|
| LLM token cost | [volume × tokens per claim × model price per token] | |
| Infrastructure / hosting | [assumption if not stated] | |
| Human review (HITL queue) | [escalation rate × reviewer cost per review] | |
| **Total agent cost** | | |

**Multi-model routing:** State which model handles which step and why.

| Step | Model | Rationale |
|------|-------|-----------|
| [e.g., classification] | [Haiku / Sonnet / Opus] | [cost vs. accuracy trade-off] |

Use current Anthropic public pricing. Show the per-unit cost calculation explicitly.

### 3. ROI summary

| | Baseline | Agent | Delta |
|-|----------|-------|-------|
| Annual cost | | | |
| Cost per unit processed | | | |
| Payback period | | | |

### 4. Conservative case
Rerun the ROI with the most pessimistic reasonable assumptions (lower automation rate, higher escalation rate, higher infrastructure cost). Does the business case still close?

> **Conservative assumption set:** [list 3 inputs changed and their pessimistic values]
> **Conservative ROI:** [result]
> **Verdict:** [still positive / marginal / does not close — and what would need to change]

### 5. Key economic risks
Two or three factors that could materially change the economics. For each:

> **Risk:** [what could go wrong] — **Impact:** [how it changes the numbers] — **Mitigation:** [what the design does to reduce this risk]

---

## Acceptance criteria

- [ ] §0 verdict states a number, not a direction
- [ ] §1 baseline calculation is explicit — shows the arithmetic, not just the result
- [ ] §2 token cost calculation shows: volume × tokens × price per token
- [ ] Multi-model routing is justified — not defaulted to one model for everything
- [ ] §4 conservative case uses different numbers from the base case, not just a disclaimer
- [ ] Every assumption labelled — no invented scenario facts presented as stated
