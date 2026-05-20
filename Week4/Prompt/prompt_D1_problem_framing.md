# Prompt: Deliverable C1 — Problem Framing & Success Metrics

## Scenario (read this first)
See `Scenario/scenario_context.md` for the full scenario, work streams, tooling, and named-systems guidance. Do not invent numbers, systems, or constraints not present in the scenario. Every number you use must trace back to `scenario_context.md` or be explicitly labelled as an assumption.

Read `Deliverables/D0C_discovery.md` before producing this deliverable.

## Your task
Produce a problem framing and success metrics document. Output file: `Deliverables/C1_problem_framing.md`.

Frame the claims processing transformation in terms of what each affected party experiences today and what they need the agent to change. Decode the operational targets (22% → 85% auto-adjudication, 8-day → 4–7 day cycle time, 41% denial overturn rate) into architectural requirements and measurable success metrics for Greenfield Health Systems, healthcare providers, and health plan members.

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

Three separate paragraphs, one per party. Each describes what the current situation feels like and costs from that party's point of view — not from Greenfield's internal metrics.

**2a-i. Claims processors and clinical reviewers (the team doing the work)**
What is the processor's and reviewer's day-to-day experience? What is manual, repetitive, or produces error risk? What does a physician reviewer experience when they must read full claim files from scratch for every claim? Tie to processing time, cycle time, and staffing figures from `scenario_context.md`.

**2a-ii. Healthcare providers (hospitals, physician groups — the submitting parties)**
What does a provider experience when the payer's adjudication is slow, opaque, or produces incorrect denials? Name the operational consequence — delayed reimbursement, denial management overhead, appeal burden, cash flow impact. Tie to any scenario evidence; label gaps as assumptions.

**2a-iii. Health plan members (patients — the people whose care is affected)**
What does a health plan member experience when a claims decision is slow, wrongly denied, or overturned only on appeal? Name the access-to-care consequence — delayed treatment, out-of-pocket exposure, confusion about coverage. Tie to the 41% denial overturn rate from `scenario_context.md`; label gaps as assumptions.

### 2b. What is actually broken — root cause diagnosis
This is not a restatement of symptoms. Identify the structural failure(s) underneath the surface problems. For each:

> **Broken [B-N]:** [name the failure — what the process cannot do reliably and why]
> **Symptom it produces:** [what people experience as a result]
> **Why it persists:** [the structural reason it hasn't been fixed — system constraint, incentive, data gap, or process design flaw]
> **What fixing it would unlock:** [the specific improvement that becomes possible once this root cause is addressed]

Minimum 2 entries. Do not list problems that are symptoms of each other as separate broken items — trace to the actual root. The 41% denial overturn rate and the 22% auto-adjudication rate are symptoms; name what structural failure produces them.

### 3. Why an AI agent — not traditional software, not RPA, not a process change
Explicit paragraph. Name each alternative and say why it is not the right answer for this specific problem. This is required — not optional context.

Required alternatives to address:
- A rules engine / deterministic auto-adjudication expansion (RPA)
- A workflow tool / case management system upgrade
- Hiring more processors or reviewers

For each: explain specifically why it fails to address the structural root cause identified in 2b, using evidence from this scenario.

### 4. What success looks like — by stakeholder

Success must be defined separately for each party affected by the intervention. Generic metrics that apply to "the business" are not sufficient. Produce three sub-sections:

#### 4a. Success for Greenfield Health Systems
What does the business win if the agent works? Table format:

| Metric | Baseline (from scenario) | Target | How measured | Timeframe |
|--------|--------------------------|--------|--------------|-----------|

Required: at minimum one throughput metric (auto-adjudication rate, claims processed per day), one financial or capacity metric (headcount, cost per claim), and one quality metric (denial overturn rate, error rate). All baselines must trace to `scenario_context.md` or be labelled as assumptions.

**Note on volume inconsistency:** `scenario_context.md` contains two stated daily volume figures (2,000/day from scenario.md; 1,667/day from Sarah Chen in Exchange 3). Use 2,000/day as the planning number; label it as the operative assumption.

#### 4b. Success for healthcare providers
What does a provider (hospital, physician group) experience differently when the agent is working well? These are not Greenfield internal metrics — they are outcomes the provider would use to judge whether adjudication quality has improved. Table format:

| Metric | Baseline (from scenario or assumption) | Target | How measured | Timeframe |
|--------|----------------------------------------|--------|--------------|-----------|

Required: at minimum one payment timeliness metric (cycle time, days-to-payment), one accuracy metric (denial rate, incorrect denial rate), and one transparency metric (denial reason quality, appeal resolution time). Label any baseline not in the scenario as an assumption.

#### 4c. Success for health plan members
What does a member experience differently? These are outcomes the member would use to judge whether coverage decisions are fair, timely, and correctly made. Table format:

| Metric | Baseline (from scenario or assumption) | Target | How measured | Timeframe |
|--------|----------------------------------------|--------|--------------|-----------|

Required: at minimum one timeliness metric (days to coverage decision), one accuracy metric (wrongful denial rate or appeal overturn rate), and one access-to-care metric. Label any baseline not in the scenario as an assumption. The 41% denial appeal overturn rate from `scenario_context.md` is the primary baseline for accuracy.

**All targets must be specific numbers, not ranges or directional statements ("improve" is not a target).**

### 5. Assumption log
Use this format for every non-trivial claim:

> **Assumption [A1]:** [what you're taking as given]
> **Why it matters:** [what spec decision or metric it drives]
> **If wrong:** [what breaks]
> **Confidence:** low / medium / high

Minimum 2 assumptions in this section. The volume discrepancy (2,000 vs. 1,667 claims/day) and the 35%/65% clinical/admin split (estimate, not measured) must both appear here.

---

## Acceptance criteria (all must pass)

- [ ] Section 2a covers all three parties — claims processors/reviewers, healthcare providers, and health plan members — as distinct paragraphs with distinct problems
- [ ] Root cause diagnosis (2b) identifies structural failures, not just symptoms — each entry traces to a root cause with a "why it persists" explanation
- [ ] The 41% denial overturn rate is used as evidence of a structural failure, not just cited as a metric
- [ ] Success metrics are defined separately for Greenfield, providers, and members (4a, 4b, 4c)
- [ ] Each stakeholder success section contains at least 3 metrics covering distinct dimensions
- [ ] Every metric has a numeric baseline sourced from `scenario_context.md` or explicitly labelled as an assumption
- [ ] Every target is a specific number, not a direction
- [ ] "How measured" is concrete — names a system or mechanism, not "track in dashboard"
- [ ] Why-an-agent section explicitly addresses rules engine/RPA, workflow tooling, and hiring as alternatives
- [ ] No generic business-speak ("improve efficiency", "reduce costs", "better experience") without a number attached
- [ ] Volume inconsistency (2,000 vs. 1,667/day) is acknowledged and a planning number is declared
- [ ] Assumption log present with at least 2 entries including the split estimate and volume discrepancy

## Fail signals — do not produce output that contains these

- Metrics with no baseline or vague targets ("reduce turnaround significantly")
- Only one or two stakeholder perspectives in section 4 — all three (Greenfield, providers, members) are required
- Section 2a written only from Greenfield's internal perspective — provider and member paragraphs missing or collapsed into the business viewpoint
- Root cause section that lists symptoms rather than structural failures — "processors are overwhelmed" is a symptom, not a root cause
- Provider and member success metrics that are just restatements of Greenfield's internal metrics from the other party's point of view
- Why-an-agent justification that dismisses RPA without acknowledging that deterministic checks (eligibility, coding validation) genuinely are RPA-appropriate — the agent's value is in classification and pre-filling, not in replacing every step
- Confident claims about provider or member experience not in `scenario_context.md` and not flagged as assumptions
- The 35%/65% split presented as a measured fact rather than a stakeholder estimate
- Assumptions buried in prose rather than surfaced in the assumption log
