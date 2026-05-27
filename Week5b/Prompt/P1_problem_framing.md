# Prompt: P1 — Problem Framing & Success Metrics

## Inputs

- `Scenario/scenario_context.md` — all sections
- `Deliverables/D0C_discovery.md` — especially §1 (situation) and §3 (primary bottleneck)

## Your task

Produce the problem framing and success metrics document.

Output file: `Deliverables/01-problem-framing.md`

---

## Required structure

### 0. Executive summary
Three bullet points. Each is one sentence:
1. The core business problem and its operational consequence — tie to a number from the scenario
2. Why the existing approach cannot scale — name the structural constraint
3. The agent intervention and the specific outcome it must achieve — name at least one target metric

### 1. Problem statement — lived experience today
Three separate paragraphs, one per affected party. Each describes what the current situation feels like and costs from that party's point of view.

**Party 1: The operations team (the people doing the work today)**
What is their day-to-day experience? What is manual, repetitive, or error-prone? Tie to processing time, volume, and staffing figures from scenario_context.md.

**Party 2: The external party submitting work or requesting service**
What do they experience when the process is slow, opaque, or produces incorrect outputs? Name the operational consequence — delayed payment, incorrect decisions, appeal burden. Tie to scenario evidence; label gaps as assumptions.

**Party 3: The end recipient or affected party**
What does the person ultimately affected experience when decisions are slow or wrong? Name the downstream consequence. Tie to scenario metrics; label gaps as assumptions.

### 2. Root cause diagnosis
For each structural failure:

> **Broken [B-N]:** [name the failure — what the process cannot do reliably and why]
> **Symptom it produces:** [what people experience]
> **Why it persists:** [structural reason — system constraint, incentive, data gap, or process design flaw]
> **What fixing it unlocks:** [the specific improvement that becomes possible]

Minimum 2 entries. Trace to root cause, not symptoms.

### 3. Why an AI agent — not traditional software
One paragraph each on why the following alternatives are insufficient for this specific problem:
- A rules engine or deterministic automation (RPA)
- A workflow tool or case management upgrade
- Hiring more people

For each: explain why it fails to address the structural root cause identified in §2.

### 4. Success metrics by stakeholder
One table per party (matching the three parties in §1).

| Metric | Baseline (from scenario or assumption) | Target | How measured | Timeframe |
|--------|---------------------------------------|--------|--------------|-----------|

Each table needs at minimum: one throughput metric, one quality metric, one cost or capacity metric. Every baseline must trace to scenario_context.md or be labelled as an assumption. Every target must be a specific number.

### 5. Assumption log

> **Assumption [A-N]:** [what is being taken as given]
> **Why it matters:** [what design decision it drives]
> **If wrong:** [what breaks]
> **Confidence:** low / medium / high

Minimum 3 entries. Include the most consequential open gap from D0C §4.

---

## Acceptance criteria

- [ ] §1 covers all three parties as distinct paragraphs with distinct problems
- [ ] §2 identifies structural failures, not symptoms — each entry has a "why it persists"
- [ ] §3 explicitly addresses rules engine, workflow tooling, and hiring as alternatives
- [ ] §4 has three separate stakeholder tables with numeric baselines and specific targets
- [ ] No metric has a vague target ("improve", "reduce significantly")
- [ ] Every baseline traces to scenario_context.md or is labelled as an assumption
- [ ] §5 has at least 3 assumptions with confidence levels
