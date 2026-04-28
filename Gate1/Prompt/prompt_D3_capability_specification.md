# Prompt: Deliverable 3 — Capability Specification

## Scenario (read this first)
See `scenario.md`. Three systems are in scope: modern CRM (REST APIs), legacy policy administration system (SOAP endpoints), document management system. No AI infrastructure exists today. Do not invent systems. Every integration contract must reference one of these three or be flagged as an assumption.

## Your task
Produce a capability specification precise enough that an AI coding agent could start building without asking clarifying questions. Output file: `3 Capability specification.md` in the `Gate1/Output/` folder.

Also produce (as part of the build artefacts in `agent_build/`):
- A console application that demonstrates the agent's core workflow
- An HTML report that summarises the analysis output
- A workflow diagram (input → agent tasks → human review → output)

---

## Required structure

### 1. Purpose and scope
- One-paragraph purpose statement
- Explicit in-scope list (bullet points)
- Explicit out-of-scope list (bullet points) — what the agent will NOT do

### 2. Inputs and outputs

**Inputs table:**

| Input | Source system | Format | Required/Optional | Validation rule |
|-------|---------------|--------|-------------------|-----------------|

**Outputs table:**

| Output | Target system / recipient | Format | Trigger condition |
|--------|---------------------------|--------|-------------------|

### 3. Entity definitions
For every entity the agent creates, reads, updates, or deletes:

```
Entity: [Name]
Attributes:
- [field]: [type], [required/optional], [constraints], [immutability]
State machine:
- [STATE_A] → [STATE_B]: [transition condition]
- [STATE_A] → [STATE_C]: [transition condition]
Constraints:
- [business rule as a boolean statement]
```

Required entities: Claim, ClaimAssignment, AdjusterQueue, AcknowledgementRecord. Add others if the spec requires them.

### 4. Requirements (6–10 minimum)
Number each requirement. For every requirement:

```
REQ-[N]: [Requirement title]
Description: [What the system must do]
Acceptance criterion: [Testable statement — measurable, specific]
Delegation tier: [from Deliverable 2]
Error handling: [What happens when this requirement cannot be met]
```

Use MUST for mandatory behaviour. No SHALL, SHOULD, MAY without explicit scoping.

### 5. Decision logic
For every branching decision in the agent:

```
Decision: [Name]
Input: [what data the agent reads to make this decision]
Logic:
  IF [condition with numeric/boolean threshold] THEN [action]
  ELSE IF [condition] THEN [action]
  ELSE [default action]
Output: [what is produced or changed]
Delegation tier: [AGENT_ONLY / AGENT_LOG / AGENT_REVIEW / AGENT_SUPPORT / HUMAN_ONLY]
```

Required decisions: severity triage, coverage validation, adjuster routing, escalation trigger.

### 6. Escalation triggers
Table format:

| Trigger condition | Threshold | Action | Notified party | SLA | If SLA breached |
|-------------------|-----------|--------|----------------|-----|-----------------|

All thresholds must be numeric or boolean.

### 7. Integration contracts
For each of the three systems (CRM, policy admin, DMS), provide a full contract:

```
Integration: [System name]
Purpose: [what the agent uses this system for]
Protocol: REST / SOAP / other
Base URL / endpoint: [URL pattern or placeholder — flag as [ASSUMED] if not in scenario]
Authentication: [method and credential storage location]
Operations:
  [OPERATION_NAME]:
    Request: [exact fields, types, required/optional]
    Response (success): [exact fields]
    Response (error): [error codes and meanings]
    Timeout: [ms or seconds — numeric]
    Retry: [conditions, max attempts, backoff strategy]
    Rate limit: [requests/min or flag as [UNKNOWN]]
    Fallback: [what the agent does if this system is unavailable]
Data mapping: [internal field] → [external field] for each operation
```

If the SOAP contract for the legacy system is not fully specifiable from the scenario, write: `[SCOPE-OUT: SOAP contract for policy admin system not specifiable from scenario. Resolution: client to provide WSDL before build. Build should stub this integration with a configurable mock.]`

### 8. State model
Draw the full claim lifecycle as a state machine:

```
States: [list all states in SCREAMING_SNAKE_CASE]
Transitions:
  [STATE_A] → [STATE_B]: [condition]
  [STATE_A] → [STATE_C]: [condition]
Terminal states: [list]
Invalid transitions: [list at least 3 — what can never happen]
```

### 9. Error handling
For each failure category:

| Failure | Detection | Agent action | Human notification | Recovery |
|---------|-----------|--------------|---------------------|----------|

Required failure categories: integration unavailable, coverage data missing, confidence below threshold, SLA about to breach, duplicate claim detected.

### 10. Audit and governance
- What is logged for every agent action (fields, not just "log it")
- Retention period per log type
- Compliance constraints applicable (flag any that are assumed, not confirmed)
- HITL checkpoints with SLAs

---

## Acceptance criteria (all must pass)

- [ ] Every requirement has a testable acceptance criterion with a numeric measure
- [ ] No modal verbs without scope (no "should", "may", "could" — use "must", "will", "can")
- [ ] All entities have full data models with state machines
- [ ] All decision logic has numeric/boolean thresholds — no fuzzy language
- [ ] All three integrations have full contracts (or explicit [SCOPE-OUT] with resolution plan)
- [ ] State machine is complete: every state has at least one valid exit transition listed
- [ ] Every error/failure mode has an explicit recovery path
- [ ] Audit log specifies fields, not just "log the action"
- [ ] Escalation triggers are all numeric or boolean
- [ ] Console app, HTML report, and workflow diagram are specified as build artefacts

## Fail signals — do not produce output that contains these

- Requirements without acceptance criteria
- "Handle appropriately", "use best judgment", "as needed"
- Integration contracts missing any of: timeout, retry, fallback
- Entity definitions with no state machine
- Decision logic with qualitative thresholds ("if the claim is complex")
- Audit trail specified as "log important actions"
- Missing [SCOPE-OUT] for the legacy SOAP system (silent omission fails)
- Open [TODO] items that are not tracked in Deliverable 5
