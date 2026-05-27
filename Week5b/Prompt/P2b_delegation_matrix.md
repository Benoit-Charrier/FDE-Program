# Prompt: P2b — Delegation Suitability Matrix

**This is Pass 2 of the cognitive assessment. Read `02a-cognitive-load-map.md` in full before writing — every JtD from A2 must appear in the matrix.**

## Methodology references

- `References/atx-scoring.md` — delegation suitability scoring rubric, archetype assignment criteria
- `References/atx-agent-mapping.md` — mapping cognitive work to agent designs, anti-pattern check

## Inputs

- `Deliverables/02a-cognitive-load-map.md` — all JtDs (A2) and micro-task scores (A3) — primary input
- `Deliverables/D0A_domain_research.md` — §2 (regulatory constraints) — drives hard HITL requirements
- `Scenario/scenario_context.md` — §2 (stakeholder non-negotiables) — drives hard HITL requirements

## Your task

Produce the Delegation Suitability Matrix (ATX Phase 3). Assign a delegation archetype to every JtD from the cognitive load map, name the dimensions that drove the assignment, and identify the hard HITL requirements that are not design choices.

Output file: `Deliverables/02b-delegation-matrix.md`

---

## Required structure

### B1. Delegation scoring summary
For each JtD from 02a-cognitive-load-map.md A2, assign a delegation archetype and name the dimensions that drove it.

| JtD | Cognitive load | Input structure | Decision determinism | Exception freq | Risk | **Archetype** | **Driving dimensions** |
|-----|---------------|----------------|----------------------|----------------|------|---------------|------------------------|

**Archetypes:**
- **Fully agentic** — agent decides and acts alone; human reviews audit log only
- **Agent-assisted** — agent prepares and recommends; human approves before action
- **Human-led, agent-supported** — human decides; agent pre-fills, surfaces context, and logs
- **Human-only** — agent involvement would increase risk or violate compliance; no delegation

**Anti-patterns to avoid:**
- Do not assign "fully agentic" to any JtD with high exception frequency + high risk without explicit written justification
- Do not assign "fully agentic" to any JtD where the domain compliance constraints (D0A §2) require human sign-off
- Do not assign "human-only" without naming the specific constraint that blocks delegation

### B2. Delegation boundary narrative
For the 2–3 JtDs where the archetype decision is most consequential (highest stakes or most debatable), write one paragraph each explaining:
- What the agent does and does not decide
- The specific condition that triggers escalation to human
- What would break if the boundary were moved in either direction

### B3. Hard HITL requirements
List any JtD where human-in-the-loop is non-negotiable based on domain compliance constraints from D0A §2 or stakeholder non-negotiables from scenario_context.md §2. These are not design choices — they are constraints.

For each:
> **[JtD name]:** [the constraint that makes HITL mandatory] — **Source:** [D0A regulation name / stakeholder quote]

---

## Acceptance criteria

- [ ] Every JtD from 02a A2 appears in the B1 matrix — none skipped
- [ ] Archetype assignments name the driving dimensions — not just a label
- [ ] No "fully agentic" with high risk + high exception frequency without written justification in B2
- [ ] Hard HITL requirements (B3) trace to a named compliance constraint or stakeholder position — not a design preference
- [ ] B2 boundary narratives name the specific escalation condition — not "human reviews if uncertain"
