# Prompt: P3 — Agent Purpose Document

## Inputs

- `Scenario/scenario_context.md` — §2 (stakeholders), §6 (compliance)
- `Deliverables/02-cognitive-delegation.md` — Part B (delegation archetypes, hard HITL requirements), Part C (agent design summary for the selected agent)
- `Deliverables/D2C_volume_value.md` — §3 (recommended agent scope)
- `Deliverables/07-economics.md` — §2 (multi-model routing)

## Your task

Produce the Agent Purpose Document for the single agent recommended in D2C §3.

Output file: `Deliverables/03-agent-purpose.md`

---

## Required structure

### 0. Agent identity

| Field | Value |
|-------|-------|
| Agent name | [short, descriptive — e.g., "WS1 Administrative Adjudication Agent"] |
| Version | v1.0 |
| Scope | [one sentence — what it processes, what it decides, what volume it covers] |
| Wave | Wave 1 (prototype scope) |
| Primary model | [from P7 multi-model routing] |

### 1. Job to be Done
One paragraph. Complete this sentence: "This agent exists so that [who] no longer has to [what cognitive work], and instead [does what instead / gets what result]."

Then name what the agent does NOT do — the scope boundary that keeps the design honest.

### 2. Capability profile
For each JtD in scope, state what the agent does:

| JtD | What the agent does | What triggers escalation | Delegation archetype |
|-----|--------------------|--------------------------|--------------------|

### 3. Autonomy matrix
For each capability, name the three modes:

| Capability | Decide alone | Route to HITL | Refuse / abort |
|------------|-------------|---------------|----------------|

**Decide alone:** the agent acts without human input. Name the condition.
**Route to HITL:** the agent prepares a packet and stops. Name the trigger condition.
**Refuse / abort:** the agent will not proceed under any circumstances. Name the hard stop.

Every hard stop must trace to a named compliance constraint (D0A §2) or a stakeholder non-negotiable (scenario_context.md §2).

### 4. Escalation triggers
For each escalation type, define:

| Trigger ID | Condition | What the agent sends to HITL | Required human action |
|------------|-----------|-----------------------------|-----------------------|

### 5. What this agent does not do
Explicit scope exclusions. For each excluded capability:

> **Out of scope: [capability]** — Reason: [compliance constraint / wave 2 deferral / dependency not yet built] — What handles it instead: [human / future agent / existing system]

### 6. Open assumptions
Any assumption about the agent's operating environment that, if wrong, would change the design.

> **Assumption [A-N]:** [what is assumed] — **If wrong:** [what changes] — **Confidence:** low / medium / high

---

## Acceptance criteria

- [ ] §1 names what the agent does NOT do as explicitly as what it does
- [ ] §3 autonomy matrix has all three modes for every capability — no blanks
- [ ] Every hard stop in §3 traces to a named compliance constraint or stakeholder position
- [ ] §4 escalation triggers are conditions, not states — "confidence < threshold" not "uncertain classification"
- [ ] §5 scope exclusions give a reason and name what handles the excluded work instead
- [ ] Agent scope is consistent with D2C §3 recommendation — no silent expansion
