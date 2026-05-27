# Prompt: P2 — Cognitive Load Map + Delegation Suitability Matrix

## Methodology references

- `References/atx-concepts.md` — cognitive load zones, delegation archetypes, JtD decomposition framework
- `References/1-atx-assessment.md` — ATX four-phase methodology, micro-task scoring, interview guide
- `References/atx-agent-mapping.md` — mapping cognitive work to agent designs
- `References/atx-scoring.md` — scoring rubric for delegation suitability dimensions

## Inputs

- `Scenario/scenario_context.md` — §3 (process), §4 (work streams), §6 (compliance)
- `Deliverables/D0C_discovery.md` — §3 (primary bottleneck)
- `Deliverables/01-problem-framing.md` — §2 (root causes)

## Your task

Produce the combined cognitive assessment and delegation analysis. This is two ATX deliverables in one document: the Cognitive Load Map (Phase 2) and the Delegation Suitability Matrix (Phase 3).

Output file: `Deliverables/02-cognitive-delegation.md`

---

## Required structure

---

## Part A — Cognitive Load Map

### A0. Work stream selection
Select the 2 work streams from scenario_context.md §4 with the highest delegation potential AND the highest cognitive complexity. Justify your selection in 2–3 sentences before proceeding.

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

## Part B — Delegation Suitability Matrix

### B1. Delegation scoring summary
For each JtD, assign a delegation archetype and name the dimensions that drove it.

| JtD | Cognitive load | Input structure | Decision determinism | Exception freq | Risk | **Archetype** | **Driving dimensions** |
|-----|---------------|----------------|----------------------|----------------|------|---------------|------------------------|

**Archetypes:**
- **Fully agentic** — agent decides and acts alone; human reviews audit log only
- **Agent-assisted** — agent prepares and recommends; human approves before action
- **Human-led, agent-supported** — human decides; agent pre-fills, surfaces context, and logs
- **Human-only** — agent involvement would increase risk or violate compliance; no delegation

**Anti-patterns to avoid:**
- Do not assign "fully agentic" to any JtD with high exception frequency + high risk without explicit justification
- Do not assign "fully agentic" to any JtD where the domain compliance constraints (D0A §2) require human sign-off
- Do not assign "human-only" without naming the specific constraint that blocks delegation

### B2. Delegation boundary narrative
For the 2–3 JtDs where the archetype decision is most consequential (highest stakes or most debatable), write one paragraph each explaining:
- What the agent does and does not decide
- The specific condition that triggers escalation to human
- What would break if the boundary were moved in either direction

### B3. Hard HITL requirements
List any JtD where human-in-the-loop is non-negotiable based on domain compliance constraints from D0A §2 or stakeholder non-negotiables from scenario_context.md §2. These are not design choices — they are constraints.

---

## Acceptance criteria

- [ ] Work stream selection justified before decomposition begins
- [ ] Each JtD is a genuine cognitive contract — input, output, and decision type named
- [ ] All micro-tasks scored on all 5 dimensions — no blanks
- [ ] Breakpoints name a specific condition, not just "human reviews"
- [ ] No JtD assigned "fully agentic" with high risk + high exception frequency without written justification
- [ ] Hard HITL requirements (B3) trace to a named compliance constraint or stakeholder position — not a design preference
- [ ] Archetype assignments in B1 name the driving dimensions that determined the choice
