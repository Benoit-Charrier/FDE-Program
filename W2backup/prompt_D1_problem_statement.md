# Prompt: Deliverable 1 — Problem Statement and Success Metrics

## Scenario (read this first)
See `scenario.md`. Do not invent numbers, systems, or constraints not present there. Every number you use must trace back to the scenario or be explicitly labelled an assumption.

## Your task
Produce a problem statement and success metrics document. Output file: `1 Problem statement and success metrics.md` in the `\deliverables\` folder.

---

## Required structure

### 1. Problem statement — claimant perspective
One paragraph. What is the claimant's experience today? What goes wrong for them and why does it matter? Tie to the 2-hour SLA and the 31% breach rate.

### 2. Problem statement — business perspective
One paragraph. What is the cost to the business today — operational, financial, reputational? Tie to the specific numbers: 300 claims/day, 12 specialists, 22 min/claim, 18% routing error, 31% SLA breach.

### 3. Why an AI agent — not traditional software, not RPA, not a process change
Explicit paragraph. Name each alternative and say why it is not the right answer for this problem. This is required — not optional context.

### 4. Success metrics
Table format. At minimum:

| Metric | Baseline (from scenario) | Target | How measured | Timeframe |
|--------|--------------------------|--------|--------------|-----------|

Required metrics to include:
- SLA compliance rate (baseline: 69%, i.e. 31% breach)
- Routing accuracy (baseline: 82%, i.e. 18% error)
- Average handling time per claim (baseline: 22 min)
- Claims processed per day without headcount increase (baseline: 300 with 12 FTEs)
- At least one claimant-facing metric (e.g. acknowledgement time)

All targets must be specific numbers, not ranges or directional statements ("improve" is not a target).

### 5. Assumption log
Use this format for every non-trivial claim:

> **Assumption [A1]:** [what you're taking as given]
> **Why it matters:** [what spec decision or metric it drives]
> **If wrong:** [what breaks]
> **Confidence:** low / medium / high

Minimum 2 assumptions in this section. More is better.

---

## Acceptance criteria (all must pass)

- [ ] Both perspectives (claimant AND business) are present and distinct
- [ ] Every metric has a numeric baseline sourced from the scenario
- [ ] Every target is a specific number, not a direction
- [ ] "How measured" is concrete — not "track in dashboard"
- [ ] Why-an-agent section names at least 2 alternatives and explains why each falls short
- [ ] No generic business-speak ("improve efficiency", "reduce costs", "better experience") without a number attached
- [ ] Assumption log present with at least 2 entries in the required format

## Fail signals — do not produce output that contains these

- Metrics with no baseline or vague targets ("reduce SLA breaches significantly")
- Only one perspective (business or claimant, not both)
- Why-an-agent justification missing or asserted without reasoning
- Confident claims about the client's systems or organisation that are not in the scenario and not flagged as assumptions
- Assumptions buried in prose rather than surfaced in the assumption log
