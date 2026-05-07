# Prompt: Deliverable D0C — Problem Statement and Success Metrics

## Scenario (read this first)
See `scenario\scenario_context.md` for the full scenario, work streams, tooling, and named-systems guidance. Do not invent numbers, systems, or constraints not present in the scenario. Every number you use must trace back to the scenario or be explicitly labelled as an assumption.

## Your task
Produce a problem statement and success metrics document. Output file: `Deliverables\D0C_problem_statement.md`.

---

## Required structure

### 0. Executive summary
Three bullet points, written first. Each bullet is one sentence. Cover in order:
1. The core business problem and its operational consequence (tie to a number from the scenario)
2. Why the existing approach cannot scale (name the structural constraint)
3. The agent intervention and the specific outcome it must achieve (name at least one target metric)

This section must be self-contained — a reader who reads only this section should understand the situation and the recommendation.

### 1. Table of contents
List all sections by number and title as markdown anchor links, in order. Generate this after the full document is written — section titles must match exactly. Format each entry as `[N. Section title](#n-section-title)` using lowercase and hyphens for spaces.

Example format:
- [0. Executive summary](#0-executive-summary)
- [1. Table of contents](#1-table-of-contents)
- [2a. Problem statement — team's perspective](#2a-problem-statement--teams-perspective)
- [2b. Problem statement — business perspective](#2b-problem-statement--business-perspective)

### 2a. Problem statement — team's perspective
One paragraph. What is the team's experience today — specifically the people doing the primary work described in scenario_context.md? What goes wrong for them and why does it matter? Tie to the turnaround targets and per-work-stream times from scenario_context.md.

### 2b. Problem statement — business perspective
One paragraph. What is the cost to the business today — operational, financial, reputational? Tie to the specific numbers from scenario_context.md: process volume per quarter, team size, per-work-stream times, turnaround targets, any stated growth trajectory, and any stated business pressure driving urgency.

### 3. Why an AI agent — not traditional software, not RPA, not a process change
Explicit paragraph. Name each alternative and say why it is not the right answer for this problem. This is required — not optional context.

### 4. Success metrics
Table format. At minimum:

| Metric | Baseline (from scenario) | Target | How measured | Timeframe |
|--------|--------------------------|--------|--------------|-----------|

Required metrics to include:
- Primary process turnaround time (baseline: from scenario_context.md)
- Time per case for the primary work stream (baseline: from scenario_context.md)
- Primary-task output accuracy (baseline: stated in scenario or label as assumption)
- Cases processed per period without headcount increase (baseline: from scenario_context.md)
- At least one downstream-stakeholder-facing metric relevant to this scenario's process

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

- [ ] Both perspectives (team AND business) are present and distinct
- [ ] Every metric has a numeric baseline sourced from the scenario or explicitly labelled as an assumption
- [ ] Every target is a specific number, not a direction
- [ ] "How measured" is concrete — names a system or mechanism, not "track in dashboard"
- [ ] Why-an-agent section names at least 2 alternatives and explains why each falls short for this specific scenario
- [ ] No generic business-speak ("improve efficiency", "reduce costs", "better experience") without a number attached
- [ ] Assumption log present with at least 2 entries in the required format

## Fail signals — do not produce output that contains these

- Metrics with no baseline or vague targets ("reduce turnaround significantly")
- Only one perspective (operational team or business, not both)
- Why-an-agent justification missing or asserted without reasoning specific to this scenario's process
- Confident claims about the organisation's systems or structure that are not in scenario_context.md and not flagged as assumptions
- Assumptions buried in prose rather than surfaced in the assumption log
