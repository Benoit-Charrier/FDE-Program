# Prompt: P2c — Agent Landscape

**This is Pass 3 of the cognitive assessment (3 passes + combine). Read 02a and 02b in full before writing — every JtD from A2 must appear in §C1.**

## Methodology references

- `References/atx-agent-mapping.md` — mapping cognitive work to agent designs, agent design summary format

## Inputs

- `Deliverables/02a-cognitive-load-map.md` — all JtDs (A2) — determines which tasks exist
- `Deliverables/02b-delegation-matrix.md` — archetype assignments (B1) — determines which tasks are agentic and at what level
- `Deliverables/D0A_domain_research.md` — §2 (regulatory constraints) — drives governance constraints per agent
- `Scenario/scenario_context.md` — §4 (work streams) — names and bounds the work areas

## Your task

Produce the agent landscape: map every JtD to a named agent, summarise each agent's design in one block, and identify the non-agentic residual. This is the full architectural picture before zooming into one agent in P3.

Output file: `Deliverables/02c-agent-landscape.md`

---

## Required structure

### C1. Workflow-to-agent mapping

Map every JtD from 02a A2 to a named agent. No JtD may be left unmapped.

| JtD | Delegation archetype (from 02b) | Agentic? | Agent assigned | Justification (1 sentence — the dimension that drove the assignment) |
|-----|---------------------------------|:--------:|----------------|----------------------------------------------------------------------|

Below the table, in one paragraph: name the **AI-native moment** — the single task in this architecture where an agent does something a rules engine structurally cannot. Name the task, why a rule cannot handle it, and what the agent does instead.

### C2. Agent design summary

For each named agent from §C1, one block:

> **Agent [N]: [Name]**
> **JtDs covered:** [list from §C1]
> **Tools required:** [list — APIs, parsers, classifiers, reference tables]
> **Context required:** [what the agent must have in scope to act — input record, history, criteria]
> **Escalation triggers:** [conditions that route to HITL — name each with a rough rate if stated in scenario]
> **Governance constraint:** [the one compliance or stakeholder rule that bounds this agent's authority — or "None" if fully agentic with no compliance dimension]

### C3. Non-agentic residual

For each JtD assigned Human-only or Human-led in 02b B1:

> **[JtD name] — stays human because:** [the specific constraint — regulatory, compliance, or stakeholder non-negotiable from D0A §2 or scenario_context §2] — **Agent role:** [what the agent does to support this step without taking the decision] — **Future delegation path:** [condition under which this could be revisited, or "No path" if regulatory ceiling]

---

## Acceptance criteria

- [ ] Every JtD from 02a A2 appears in §C1 — none unmapped
- [ ] AI-native moment names a specific task and explains why a rule engine cannot handle it
- [ ] Each agent block in §C2 has all 5 fields — no blanks
- [ ] Governance constraint in §C2 references a named constraint from D0A §2 or scenario_context, not a design preference
- [ ] §C3 covers every Human-only or Human-led JtD from 02b B3
