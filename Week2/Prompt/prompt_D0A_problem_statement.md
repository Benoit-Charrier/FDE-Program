# Prompt: Deliverable 1 — Problem Statement and Success Metrics

## Scenario (read this first)
See `scenario\scenario_context.md` for the full scenario, work streams, tooling, and named-systems guidance. Do not invent numbers, systems, or constraints not present in the scenario. Every number you use must trace back to the scenario or be explicitly labelled as an assumption.

## Your task
Produce a problem statement and success metrics document. Be concise. Summarize the main 3 points at the end. Output file: `deliverables\D0A_problem_statement.md`.

---

## Required structure

### 1. Problem statement — legal team's perspective
One paragraph. What is the legal team's experience today — specifically the paralegal and lawyers doing first-pass and redline work? What goes wrong for them and why does it matter? Tie to the 4–6 business day turnaround and the specific per-work-stream times in the scenario.

### 2. Problem statement — business perspective
One paragraph. What is the cost to the business today — operational, financial, reputational? Tie to the specific numbers: 300 contracts/quarter, 5-person legal team, first-pass at ~25 min/case, turnaround at 4–6 business days, CRO pressure, and Helix's 25% YoY growth trajectory.

### 3. Why an AI agent — not traditional software, not RPA, not a process change
Explicit paragraph. Name each alternative and say why it is not the right answer for this problem. This is required — not optional context.

### 4. Success metrics
Table format. At minimum:

| Metric | Baseline (from scenario) | Target | How measured | Timeframe |
|--------|--------------------------|--------|--------------|-----------|

Required metrics to include:
- Contract turnaround time (baseline: 4–6 business days)
- First-pass classification time per contract (baseline: ~25 min/case)
- Clause classification accuracy (baseline: not stated in scenario — label as assumption)
- Contracts processed per quarter without headcount increase (baseline: 300 with 5-person team)
- At least one procurement-facing metric (e.g., time from contract receipt to first response to vendor)

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

- [ ] Both perspectives (legal team AND business/procurement) are present and distinct
- [ ] Every metric has a numeric baseline sourced from the scenario or explicitly labelled as an assumption
- [ ] Every target is a specific number, not a direction
- [ ] "How measured" is concrete — names a system or mechanism, not "track in dashboard"
- [ ] Why-an-agent section names at least 2 alternatives and explains why each falls short for this specific scenario
- [ ] No generic business-speak ("improve efficiency", "reduce costs", "better experience") without a number attached
- [ ] Assumption log present with at least 2 entries in the required format

## Fail signals — do not produce output that contains these

- Metrics with no baseline or vague targets ("reduce turnaround significantly")
- Only one perspective (legal team or business, not both)
- Why-an-agent justification missing or asserted without reasoning specific to contract clause review
- Confident claims about Helix's systems or organisation that are not in the scenario and not flagged as assumptions
- Assumptions buried in prose rather than surfaced in the assumption log
- Numbers from a different scenario (e.g., claims processing figures — this is a contract review scenario)
