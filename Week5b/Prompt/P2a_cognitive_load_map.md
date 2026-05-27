# Prompt: P2a — Cognitive Load Map

**This is Pass 1 of the cognitive assessment (2 passes + combine). Pass 2 (P2b) produces the delegation matrix from this output.**

## Methodology references

- `References/atx-concepts.md` — cognitive load zones, JtD decomposition framework, breakpoints
- `References/1-atx-assessment.md` — Phase 2: Cognitive Load Mapping (micro-task scoring, lived process, zone/breakpoint method)
- `References/atx-agent-mapping.md` — mapping cognitive work to agent designs

## Inputs

- `Scenario/scenario_context.md` — §3 (process), §4 (work streams), §6 (compliance)
- `Deliverables/D0C_discovery.md` — §2 (Points of Pain inventory), §4 (primary cognitive bottleneck)
- `Deliverables/01-problem-framing.md` — §2 (root causes)

## Your task

Produce the Cognitive Load Map (ATX Phase 2). Decompose the highest-priority candidate processes from the Points of Pain inventory into cognitive zones, JtDs, and scored micro-tasks.

**Start from lived work, not documented SOPs.** Name where the worker pauses, checks a reference, makes a judgment call, or handles an exception — these are the cognitive hotspots.

Output file: `Deliverables/02a-cognitive-load-map.md`

---

## Required structure

### A0. Work stream selection
Select the 2 work streams from D0C §2 with the highest delegation potential AND the highest cognitive complexity. Justify your selection in 2–3 sentences before proceeding.

### A1. Lived process narrative (one per work stream)
For each selected work stream: walk through a real case from trigger to completion. Name where the worker pauses, consults, makes a judgment call, or handles an exception. This is the lived process — not the documented SOP.

### A2. Jobs to be Done decomposition
For each work stream, decompose into JtDs (atomic units of delegation). Each JtD is a cognitive contract: "Given [input], produce [output], making [decision type]."

Format:
> **JtD-[N]:** [name] — Given [input], [produce/decide/route/validate] [output]. Decision type: [lookup / classification / judgment / compliance check / escalation].

### A3. Micro-task inventory
For each JtD, list the micro-tasks and score on 5 dimensions:

| Micro-task | Cognitive load (H/M/L) | Input structure (H/M/L) | Decision determinism (H/M/L) | Exception frequency (H/M/L) | Risk / compliance (H/M/L) |
|------------|----------------------|------------------------|------------------------------|----------------------------|--------------------------|

**Scoring guide:**
- Cognitive load: H = requires expertise or judgment; L = lookup or rule-following
- Input structure: H = structured/predictable; L = unstructured/variable (note: high structure = easier to automate)
- Decision determinism: H = rule-based with clear criteria; L = judgment-dependent
- Exception frequency: H = exceptions are common; L = exceptions are rare
- Risk / compliance: H = error has regulatory or safety consequence; L = error is recoverable

### A4. Cognitive zones and breakpoints
For each work stream, group micro-tasks into cognitive zones and name the breakpoints — the specific moments where control must shift between agent and human.

> **Zone [N]: [name]** — [micro-tasks in this zone] — Cognitive type: [pattern recognition / rule application / judgment / compliance gate]
> **Breakpoint before Zone [N]:** [what triggers the shift — not "human reviews" but the specific condition]

---

## Acceptance criteria

- [ ] Work stream selection justified before decomposition begins — references specific D0C §2 entries
- [ ] Each JtD is a genuine cognitive contract — input, output, and decision type all named
- [ ] All micro-tasks scored on all 5 dimensions — no blanks
- [ ] Breakpoints name a specific condition, not just "human reviews"
- [ ] Lived process narrative names real pauses, judgment calls, or exception moments — not an SOP restatement
