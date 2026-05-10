# Prompt: Deliverable 3 — Volume × Value Analysis

## Scenario (read this first)
See `scenario\scenario_context.md` for the full scenario, work streams, tooling, and named-systems guidance. Do not invent numbers, systems, or constraints not present in the scenario. Every number you use must trace back to the scenario or be explicitly labelled as an assumption.

---

## Your task
Produce a Volume × Value Analysis. Be concise. Output file: `deliverables\D2C_volume_value_analysis.md`.

This is Phase 4 of the ATX Assessment. Plot all 4 work streams, identify where an agent creates value versus where it creates risk, identify the primary agentic target, and justify why it wins.

Reference: `references\1-ATX-Assessment.md` Phase 4 and `references\atx-scoring.md`.

---

## Required structure

### 0. Executive summary
Three bullet points, written first. Each bullet is one sentence. Cover in order:
1. The primary agentic target — name it, give its Agentic Value Score, and state the one-line business case (tie to a scenario number)
2. The work stream that looks automatable but isn't — name it and the specific dimension or constraint that disqualifies it from the top spot
3. Whether the economics close — state the directional TCO finding (payback period or annual saving estimate) and the single biggest assumption it rests on

This section must be self-contained — a reader who reads only this section should know what to build first, what not to build, and whether the business case holds.

### 0b. Table of contents
List all sections by number and title as markdown anchor links, in order. Generate this after the full document is written — section titles must match exactly. Format each entry as `[N. Section title](#n-section-title)` using lowercase and hyphens for spaces.

Example format:
- [0. Executive summary](#0-executive-summary)
- [0b. Table of contents](#0b-table-of-contents)
- [1. Suitability pre-screening (ATX Step 1)](#1-suitability-pre-screening-atx-step-1)
- [2. Volume derivation](#2-volume-derivation)
- [3. Non-determinism scoring](#3-non-determinism-scoring)
- [4. Volume × Value grid (Mermaid quadrantChart)](#4-volume--value-grid-mermaid-quadrantchart)
- [5. Where an agent creates value — and where it creates risk](#5-where-an-agent-creates-value--and-where-it-creates-risk)
- [6. Suitability gate check](#6-suitability-gate-check)
- [7. Primary agentic target — selection and justification](#7-primary-agentic-target--selection-and-justification)
- [8. Preliminary TCO sense-check](#8-preliminary-tco-sense-check)

### 1. Suitability pre-screening (ATX Step 1)

Before scoring volume or value, apply the four suitability criteria from `references\atx-scoring.md` Step 1 to all four work streams. Produce a table:

| Work stream | Solvable by rules/RPA only? | Tacit judgment with no structure? | Critical integrations unavailable? | Compliance risk with no viable HITL? | Pre-screen result |
|-------------|---|---|---|---|---|

For each work stream, state the pre-screen result (Pass / Conditional pass / Conditional — not yet delegatable / Fail — Human Only) and a one-sentence rationale. Note which work streams proceed to the volume × value analysis. Work streams that fail the gate may still appear on the grid for diagnostic completeness, but must be labelled as excluded from the agentic candidate set.

### 2. Volume derivation
Before scoring, derive the per-work-stream volume from the scenario numbers. Show your arithmetic.

- Use the total process volume from scenario_context.md → approximately how many per week?
- Use the per-work-stream volumes from scenario_context.md directly. Cross-check them against any routing split or distribution stated in the scenario.
- For each work stream, how many "cases" per week does it handle?
- Flag any volume figures that require assumptions beyond what the scenario states, with explicit labelling.

### 3. Non-determinism scoring
For each work stream, score both dimensions using the exact scales from `references\atx-scoring.md` Step 2. Agentic Value Score = Volume × Non-Determinism (1–25 scale).

| Work Stream | Volume Score (1–5) | Non-Determinism Score (1–5) | Agentic Value Score (product) | Quadrant |
|-------------|-------------------|-----------------------------|-------------------------------|---------|

**Execution Frequency (Volume) scale:**

| Score | Threshold |
|-------|-----------|
| 5 | Very frequent: hundreds+ per day or continuous stream |
| 4 | Frequent: 50–200 per day |
| 3 | Regular: 10–50 per day, or high volume per week |
| 2 | Moderate: several per day or high volume per month |
| 1 | Infrequent: weekly or monthly |

**Non-Deterministic Decision Effort scale:**

| Score | Threshold |
|-------|-----------|
| 5 | High reasoning: requires synthesis of multiple data sources, policy interpretation, contextual judgment |
| 4 | Significant reasoning: follows patterns but requires contextual adaptation and exception handling |
| 3 | Mixed: core path is rule-based but exceptions and edge cases require reasoning |
| 2 | Mostly deterministic: small reasoning component around structured rules |
| 1 | Fully deterministic: pure rules/logic, no reasoning required |

**Agentic Value Score calculation — do this for every work stream:**
1. Assign a Volume Score (1–5) using the Execution Frequency scale above. Cite the weekly case volume derived in §2.
2. Assign a Non-Determinism Score (1–5) using the Non-Deterministic Decision Effort scale above. Cite the specific decision types present in that work stream.
3. Multiply: Agentic Value Score = Volume Score × Non-Determinism Score.
4. Enter the product in the table column "Agentic Value Score (product)".
5. Interpret the score against the thresholds below and record the candidate status.

**Agentic candidate thresholds:**
- Score ≥ 15: Strong agentic candidate
- Score 8–14: Consider agentic, validate with TCO
- Score < 8: Use rule-based automation or do not automate

Justify each score in a note below the table. Do not assert — cite the specific nature of the work. Scores must differentiate across all 4 work streams (minimum 2-point range on Non-Determinism).

### 4. Volume × Value grid (Mermaid quadrantChart)

Render the grid as a Mermaid `quadrantChart`. Map each work stream's scores to normalised coordinates using:

```
x = (Non-Determinism Score - 1) / 4
y = (Volume Score - 1) / 4
```

Output the following block, replacing the placeholder coordinates with the values calculated above:

```mermaid
quadrantChart
    title Volume x Value Analysis
    x-axis Low Non-Determinism --> High Non-Determinism
    y-axis Low Volume --> High Volume
    quadrant-1 Primary agentic targets
    quadrant-2 Rules / RPA only
    quadrant-3 Not worth automating
    quadrant-4 Select agentic use cases
    Work Stream A: [x, y]
    Work Stream B: [x, y]
    Work Stream C: [x, y]
    Work Stream D: [x, y]
```

**Mermaid quadrantChart rendering rules — apply before finalising coordinates:**

1. **No axis-edge values.** Coordinates must be strictly between 0 and 1 exclusive. Never use 0.0, 0.00, 1.0, or 1.00 on either axis — Mermaid throws a lexical error.
2. **Avoid y=0.50.** The horizontal quadrant divider sits exactly at y=0.50. Any point plotted at y=0.50 will have its label printed on top of the quadrant label text, making both unreadable. Keep all points ≥0.08 away from y=0.50 (i.e., use y≤0.42 or y≥0.58).
3. **ASCII characters in the title only.** Replace `×` with `x`, `—` with `-`, and `→` with `-->` in the chart title line. Special Unicode characters cause a lexical error.
4. **Offset colliding points.** If two work streams share the same formula coordinates, offset one by at least 0.08 on either axis to keep labels visually distinct.
5. **Record formula coordinates in text, use adjusted coordinates in the diagram.** State the raw formula result (e.g., `y = (3-1)/4 = 0.50`) in the narrative below the chart for traceability, then use the adjusted rendering coordinate (e.g., `0.58`) in the actual Mermaid code block.

If two work streams share the same scores, offset one coordinate by at least 0.08 to keep points visually distinct, and note the collision below the chart.

### 5. Where an agent creates value — and where it creates risk
For each work stream, one paragraph:

> **Work Stream [N]: [name]**
> **Value created by agent:** [what would an agent accomplish that a human cannot do as efficiently?]
> **Risk created by agent:** [what could go wrong specifically in this work stream, and why?]
> **Net assessment:** [value > risk / risk > value / conditional on X]

The scenario's primary governance constraint must appear in the risk assessment of at least one work stream.

### 6. Suitability gate check
Run the suitability gate from `references\atx-scoring.md` on the top 2 agentic candidates (by Agentic Value Score):

| Factor | Work Stream A | Work Stream B |
|--------|--------------|--------------|
| Input Structure | H/M/L | H/M/L |
| Decision Determinism | H/M/L | H/M/L |
| Tool Coverage | H/M/L | H/M/L |
| Exception Rate | H/M/L | H/M/L |
| Compliance Risk | H/M/L | H/M/L |
| Gate Result | Pass / Conditional / Fail | Pass / Conditional / Fail |

### 7. Primary agentic target — selection and justification
Name the single work stream that is the primary agentic target. Justify in 4–6 sentences:
- Why this work stream wins on the Volume × Value grid
- Why it passes the suitability gate
- What specific business pain it addresses (tie to scenario numbers)
- What the feasibility case is (data availability, integration path, compliance manageability)
- What the single biggest risk to agentic success is in this work stream

### 8. Preliminary TCO sense-check
Using the scenario's numbers, run a high-level TCO estimate for the primary agentic target only. Show your arithmetic:

```
Baseline cost per case:
  Time per case: [from scenario]
  Assumption: fully loaded hourly cost = [£/$/€ — label as assumption]
  Baseline cost per case = [calculated]
  Cases per year = [derived from scenario]
  Annual baseline = [calculated]

Agent cost estimate:
  Estimated tokens per case: [estimate with rationale]
  Model: [name your assumption]
  Estimated token cost per case: [calculated]
  Estimated HITL rate: [% — tie to scenario's stated escalation or routing rates]
  HITL cost per case: [calculated]
  Estimated agent cost per case: [sum]
  Annual agent cost: [calculated]

Annual saving: [baseline - agent cost]
Estimated build cost: [label as assumption]
Payback period: [calculated]
```

All figures not in the scenario must be labelled as assumptions. The goal is directional — does the economics likely close?

---

## Acceptance criteria (all must pass)

- [ ] Suitability pre-screening present as §1 with a table covering all 4 work streams against the four ATX Step 1 criteria; pre-screen result stated for each
- [ ] All 4 work streams appear on the grid
- [ ] Volume derivation shows arithmetic traced to scenario numbers
- [ ] Scores justified — not asserted
- [ ] Suitability gate run on the top 2 candidates
- [ ] Primary target named and justified with scenario-grounded reasoning
- [ ] Risk analysis present for every work stream (not just the primary target)
- [ ] The scenario's primary governance constraint reflected in risk analysis
- [ ] TCO sense-check present with all assumptions labelled
- [ ] Non-determinism scores differentiate the work streams (at least a 2-point range across all 4)

## Fail signals — do not produce output that contains these

- All four work streams in the same quadrant (that means the analysis didn't differentiate)
- Primary target selected based on intuition without Volume × Value evidence
- TCO estimate with no arithmetic shown
- Risk analysis that says "agents can make mistakes" without naming the specific mistake type and consequence in this scenario
- Volume numbers with no trace to the scenario's stated volume figures
