# Prompt: P5 Pass 2 — Capability Specification §7–§11

**This is Pass 2 of 1 capability spec.** Append §7–§11 to `Deliverables/05-capability-spec.md`. Do not rewrite §0–§6.

## Methodology references

- `References/production-spec-checklist.md` — completeness checklist before the build loop
- `References/spec-ambiguity-vs-builder-mistakes.md` — taxonomy for diagnosing under-specified decisions

## Inputs

- `Deliverables/05-capability-spec.md` — read §2–§6 before writing; §7–§11 must be consistent
- `Deliverables/03-agent-purpose.md` — §3 (autonomy matrix), §4 (escalation triggers)
- `Deliverables/02-cognitive-delegation.md` — Part B §B3 (hard HITL requirements)

## Your task

Append §7–§11 to the capability spec. These sections cover governance, testing, and the assumption register.

Append to: `Deliverables/05-capability-spec.md`

---

## Required structure (append after §6)

### §7. Escalation trigger definitions

For each escalation trigger defined in P3 §4:

| Trigger ID | Condition (precise) | Routing queue | Required HITL action | Required resolution options |
|------------|--------------------|--------------|--------------------|---------------------------|

Each trigger must have:
- A precise condition using named fields from §2 input contract or §3 entity definitions
- A named routing queue (e.g., `PHYSICIAN_HITL`, `EXCEPTION_PROCESSOR`)
- Required resolution options the HITL reviewer must choose from

**ET-[last] — Governance hard stop:** Define one escalation trigger that fires if the agent is invoked in an invalid state. This trigger must:
- Be the first operation of the payment/output step
- Preserve the incoming state (not overwrite it)
- Route to an exception processor with `trigger_type: GOVERNANCE_VIOLATION`

### §8. Autonomy matrix

| Capability | Condition | Mode | Agent action | Human action |
|------------|-----------|------|-------------|--------------|

**Mode values:** `DECIDE_ALONE` / `ROUTE_TO_HITL` / `REFUSE`

Every hard HITL requirement from P2 Part B §B3 must appear as `ROUTE_TO_HITL` or `REFUSE` here — no exceptions.

### §9. State model

**Valid states:** [list all states from §3 entity state machines]

**Valid transitions table:**

| From state | To state | Trigger | Guard condition |
|------------|----------|---------|----------------|

**Invariants:**
- [State X] can only be reached from [State Y] — never from [State Z]
- [Final output field] must never be written before state reaches [State N]
- Audit entry must be COMMITTED before any state transition that writes output

### §10. Test scenarios

Define 3 test scenarios the builder must implement:

**S-1: Happy path**
- Input: [describe the nominal case — all checks pass, agent approves]
- Expected output: `status: approved`, [key output fields present], [audit trail requirements]

**S-2: Failure-mode escalation**
- Input: [describe the case that triggers the primary escalation]
- Expected output: `status: escalated`, correct `escalation_trigger_id`, `[output value field]` absent

**S-3: Governance hard stop**
- Input: [describe the state corruption or invalid invocation scenario]
- Expected output: `status: escalated`, `trigger_type: GOVERNANCE_VIOLATION`, output value absent, incoming state preserved

### §11. Spec ambiguity register

For every design decision that required an assumption (because the scenario does not specify it), register it here:

| ID | Type | Confidence | Description | Impact if wrong | Resolution |
|----|------|-----------|-------------|----------------|-----------|

**Types:** `Open assumption` / `Design gap` / `Deferred decision`
**Confidence:** Low / Medium / High

Minimum 3 entries. Every low-confidence assumption must have a named resolution owner and action.

---

## Acceptance criteria

- [ ] §7 every escalation trigger has a precise condition using named fields — no prose descriptions
- [ ] §7 governance hard stop trigger is defined and preserves incoming state
- [ ] §8 autonomy matrix is consistent with §7 escalation triggers — every ROUTE_TO_HITL in §8 has a corresponding ET-N in §7
- [ ] §9 state model shows every valid transition; no implicit transitions
- [ ] §9 audit-first invariant explicitly stated
- [ ] §10 S-3 governance hard stop test scenario is present and tests state preservation
- [ ] §11 has at least 3 entries; low-confidence items have resolution owners
- [ ] Nothing in §7–§11 contradicts §2–§6 from Pass 1
