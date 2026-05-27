# Prompt: P6 — Validation Plan

## Inputs

- `Deliverables/05-capability-spec.md` — §10 (test scenarios), §11 (ambiguity register)
- `Deliverables/03-agent-purpose.md` — §4 (escalation triggers)
- `Deliverables/D0A_domain_research.md` — §4 (known failure modes)

## Your task

Produce the validation plan. Cover accuracy, failure modes, compliance, and the gap between prototype and production.

Output file: `Deliverables/06-validation-plan.md`

---

## Required structure

### 1. Validation scope
Two sentences: what is being validated and what is explicitly out of scope for the prototype validation.

### 2. Test scenarios (3 required)

For each scenario from the capability spec §10:

**Scenario [N]: [name]**
- Fixture: [describe the input — key field values]
- Pipeline path: [what steps execute]
- Pass conditions: [specific, checkable — field names and expected values]
- Fail signal: [what output indicates failure]

### 3. Failure mode coverage

Map each domain failure mode from D0A §4 to a test scenario or a named reason it is not covered:

| Failure mode | Covered by | How |
|-------------|-----------|-----|
| [from D0A] | Scenario N / Not covered | [test mechanism or reason for gap] |

### 4. The dangerous failure mode
Name the single most dangerous failure mode for this domain — the one where the agent approves something it should have escalated. State explicitly:
- What output field or condition would reveal this failure
- What design mechanism prevents it (reference the spec — e.g., FM-A-5 hard stop, confidence threshold)
- What test covers it

### 5. Prototype vs production gap
What does the prototype not validate that a production deployment would require? For each gap:

> **Gap:** [what is not tested] — **Risk:** [consequence if this gap exists in production] — **Production validation action:** [what would need to happen before go-live]

Minimum 2 gaps.

### 6. Acceptance criteria for the prototype
A checklist the FDE can run before the demo:

- [ ] All 3 test scenarios pass with correct output fields
- [ ] The dangerous failure mode test (S-3 or equivalent) passes
- [ ] No `[output value field]` appears in any escalated output
- [ ] Audit trail is present and all entries are COMMITTED in approved outputs
- [ ] [Add 1–2 domain-specific checks relevant to the scenario's compliance requirements]

---

## Acceptance criteria

- [ ] §2 has all 3 test scenarios with checkable pass conditions (field names + expected values)
- [ ] §3 maps every domain failure mode from D0A — none silently ignored
- [ ] §4 names the dangerous failure mode and the design mechanism that prevents it
- [ ] §5 has at least 2 prototype vs production gaps
- [ ] §6 checklist is runnable — no vague items like "verify it works"
