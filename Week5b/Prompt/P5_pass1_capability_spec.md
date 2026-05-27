# Prompt: P5 Pass 1 — Capability Specification §0–§6

**This is Pass 1 of 1 capability spec, 2 passes total.** Pass 1 produces §0–§6. Pass 2 (P5_pass2) appends §7–§11 to the same file.

## Methodology references

- `References/production-spec-checklist.md` — completeness checklist before the build loop
- `References/spec-ambiguity-vs-builder-mistakes.md` — taxonomy for diagnosing under-specified decisions

## Inputs

- `Scenario/scenario_context.md` — §5 (systems), §6 (compliance)
- `Deliverables/03-agent-purpose.md` — all sections
- `Deliverables/02-cognitive-delegation.md` — Part A (micro-task inventory), Part B (delegation matrix)
- `Deliverables/04-adrs.md` — all ADRs

## Your task

Produce §0–§6 of the production-grade capability specification. This spec must be buildable by an AI coding agent with few or no clarifying questions.

Output file: `Deliverables/05-capability-spec.md` (create new — Pass 2 will append)

---

## Required structure

### §0. Agent identity and KPIs

| Field | Value |
|-------|-------|
| Agent name | |
| Version | |
| Spec status | Draft |
| Primary model | |
| Confidence threshold (configurable) | [named parameter — e.g., `CLASSIFICATION_CONFIDENCE_THRESHOLD = 0.70`] |

**KPIs this agent is responsible for:**

| KPI | Baseline | Target | How measured |
|-----|----------|--------|--------------|

### §1. Purpose and scope

**Purpose:** [one paragraph — what problem this agent solves, for whom, and at what scale]

**In scope:** [bulleted list — what the agent processes and decides]

**Out of scope:** [bulleted list — what the agent explicitly does not handle; reference D2C exclusions]

### §2. Inputs and outputs

**Input contract — NormalizedInput schema:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| [field_name] | [type] | Yes/No | [what it contains] |

All required fields must be present. If any required field is missing, the agent must reject the input and return a structured error — never process a partial input silently.

**Output contract — two shapes:**

Shape 1 — Approved/completed:
```json
{
  "id": "string",
  "status": "approved",
  [key output fields]
}
```

Shape 2 — Escalated:
```json
{
  "id": "string",
  "status": "escalated",
  "escalation_trigger_id": "ET-XX",
  "routing_queue": "string",
  "escalation_reason": "string",
  [context fields for HITL reviewer]
}
```

**Rule: `payment_amount` (or equivalent final-output value field) must never appear in an escalated output.**

### §3. Entity definitions

For each core entity the agent creates or modifies, define:

**[EntityName]**
- Attributes: [field: type — description]
- State machine: [valid states and transitions — use → notation]
- Invariants: [rules that must always be true]

Include at minimum: the primary record entity (ClaimRecord, OrderRecord, etc.), the audit log entry, and the escalation packet.

### §4. Activity catalog

List every distinct action the agent takes, numbered as T-01, T-02, etc.

| ID | Name | Input | Output | Real or stub | Failure mode |
|----|------|-------|--------|--------------|-------------|

Mark each as **Real** (actual LLM call or integration) or **Stub** (hardcoded for prototype).

### §5. Functional requirements

For each capability, state requirements in this format:

> **REQ-[N]:** [what the agent must do — imperative, testable]
> **Trigger:** [what causes this requirement to activate]
> **Success condition:** [how to verify it passed]
> **Failure condition:** [what triggers an escalation or error]

Group by capability area. Minimum 5 requirements.

### §6. Decision logic

For each decision the agent makes autonomously (Decide alone in the autonomy matrix), specify:

**Decision: [name]**

```
IF [condition using named fields and thresholds]
THEN [action — name the next state or output]
ELSE IF [condition]
THEN [action]
ELSE [default action — escalate or abort]
```

All thresholds must be named configurable parameters (e.g., `CONFIDENCE_THRESHOLD`), never hardcoded literals.

---

## Acceptance criteria

- [ ] §0 confidence threshold is a named configurable parameter, not a hardcoded value
- [ ] §2 input contract lists all required fields; missing-field handling is specified
- [ ] §2 output contract has two shapes — approved and escalated — with explicit rule about what must not appear in escalated output
- [ ] §3 entity state machines show all valid transitions — no implicit states
- [ ] §4 activity catalog marks every action as Real or Stub
- [ ] §5 requirements are imperative and testable — not descriptive ("the agent processes claims")
- [ ] §6 decision logic uses named parameters, not literal values
- [ ] Nothing in this spec contradicts ADRs from P4
