# Prompt: Deliverable D1 — Problem Framing & Success Metrics

## Scenario (read this first)
See `scenario\scenario_context.md` for the full scenario, work streams, tooling, and named-systems guidance. Do not invent numbers, systems, or constraints not present in the scenario. Every number you use must trace back to the scenario or be explicitly labelled as an assumption.

## Your task
Produce a problem framing and success metrics document. Output file: `Deliverables\D1_problem_framing.md`.

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
- [2a. Problem statement — lived experience today](#2a-problem-statement--lived-experience-today)

### 2a. Problem statement — lived experience today

Three separate paragraphs, one per party. Each describes what the current situation feels like and costs from that party's point of view — not from MedFlex's internal metrics.

**2a-i. MedFlex coordinators (the team doing the work)**
What is the coordinator's day-to-day experience? What breaks, what is manual, what creates stress or error risk? Tie to turnaround targets and per-work-stream times from scenario_context.md.

**2a-ii. Hospitals (the facility customers)**
What does a hospital experience when MedFlex's process is slow, unreliable, or produces compliance gaps? Name the operational consequence for the facility — staffing shortfalls, credential incidents, last-minute surprises. Tie to any scenario evidence; label gaps as assumptions.

**2a-iii. Nurses (the workers)**
What does a nurse experience when the placement process is friction-heavy, slow to confirm, or produces errors (wrong unit, wrong rate, last-minute cancellation)? Tie to any scenario evidence; label gaps as assumptions.

### 2b. What is actually broken — root cause diagnosis
This is not a restatement of symptoms. Identify the structural failure(s) underneath the surface problems. For each:

> **Broken [B-N]:** [name the failure — what the process cannot do reliably and why]
> **Symptom it produces:** [what people experience as a result]
> **Why it persists:** [the structural reason it hasn't been fixed — system constraint, incentive, data gap, or process design flaw]
> **What fixing it would unlock:** [the specific improvement that becomes possible once this root cause is addressed]

Minimum 2 entries. Do not list problems that are symptoms of each other as separate broken items — trace to the actual root.

### 3. Why an AI agent — not traditional software, not RPA, not a process change
Explicit paragraph. Name each alternative and say why it is not the right answer for this problem. This is required — not optional context.

### 4. What success looks like — by stakeholder

Success must be defined separately for each party affected by the intervention. Generic metrics that apply to "the business" are not sufficient. Produce three sub-sections:

#### 4a. Success for MedFlex
What does the business win if the agent works? Table format:

| Metric | Baseline (from scenario) | Target | How measured | Timeframe |
|--------|--------------------------|--------|--------------|-----------|

Required: at minimum one operational metric (throughput, turnaround time), one financial or capacity metric (revenue, headcount leverage), and one quality or risk metric (fill rate, compliance incidents). All baselines must trace to scenario_context.md or be labelled as assumptions.

#### 4b. Success for the hospitals
What does a hospital (the facility customer) experience differently when the agent is working well? These are not internal MedFlex metrics — they are outcomes the hospital would use to judge whether the relationship is working. Table format:

| Metric | Baseline (from scenario or assumption) | Target | How measured | Timeframe |
|--------|----------------------------------------|--------|--------------|-----------|

Required: at minimum one reliability metric (fill rate, response time), one compliance metric (credential accuracy, incident rate), and one relationship/experience metric. Label any baseline not in the scenario as an assumption.

#### 4c. Success for the nurses
What does a nurse (the worker) experience differently? These are outcomes the nurse would use to judge whether working through MedFlex is worth it. Table format:

| Metric | Baseline (from scenario or assumption) | Target | How measured | Timeframe |
|--------|----------------------------------------|--------|--------------|-----------|

Required: at minimum one friction metric (time to receive offer, confirmation speed), one reliability metric (last-minute cancellations, shift accuracy), and one experience metric. Label any baseline not in the scenario as an assumption.

**All targets must be specific numbers, not ranges or directional statements ("improve" is not a target).**

### 5. Assumption log
Use this format for every non-trivial claim:

> **Assumption [A1]:** [what you're taking as given]
> **Why it matters:** [what spec decision or metric it drives]
> **If wrong:** [what breaks]
> **Confidence:** low / medium / high

Minimum 2 assumptions in this section. More is better.

---

## Acceptance criteria (all must pass)

- [ ] Section 2a covers all three parties — MedFlex coordinators, hospitals, and nurses — as distinct paragraphs with distinct problems
- [ ] Root cause diagnosis (2c) identifies structural failures, not just symptoms — each entry traces to a root cause with a "why it persists" explanation
- [ ] Success metrics are defined separately for MedFlex, hospitals, and nurses (4a, 4b, 4c)
- [ ] Each stakeholder success section contains at least 3 metrics covering distinct dimensions (not three versions of the same metric)
- [ ] Every metric has a numeric baseline sourced from the scenario or explicitly labelled as an assumption
- [ ] Every target is a specific number, not a direction
- [ ] "How measured" is concrete — names a system or mechanism, not "track in dashboard"
- [ ] Why-an-agent section names at least 2 alternatives and explains why each falls short for this specific scenario
- [ ] No generic business-speak ("improve efficiency", "reduce costs", "better experience") without a number attached
- [ ] Assumption log present with at least 2 entries in the required format

## Fail signals — do not produce output that contains these

- Metrics with no baseline or vague targets ("reduce turnaround significantly")
- Only one or two stakeholder perspectives in section 4 — all three (MedFlex, hospitals, nurses) are required
- Section 2a written only from the coordinator's perspective — hospital and nurse paragraphs missing or collapsed into MedFlex's viewpoint
- Root cause section (2c) that lists symptoms rather than structural failures — "coordinators are overwhelmed" is a symptom, not a root cause
- Hospital and nurse success metrics that are just restatements of MedFlex internal metrics from the facility's or nurse's point of view
- Why-an-agent justification missing or asserted without reasoning specific to this scenario's process
- Confident claims about the organisation's systems or structure that are not in scenario_context.md and not flagged as assumptions
- Assumptions buried in prose rather than surfaced in the assumption log
