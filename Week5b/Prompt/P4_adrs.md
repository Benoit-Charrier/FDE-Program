# Prompt: P4 — Architecture Decision Records

## Inputs

- `Deliverables/03-agent-purpose.md` — §3 (autonomy matrix), §4 (escalation triggers)
- `Deliverables/02-cognitive-delegation.md` — Part B (delegation boundaries)
- `Deliverables/07-economics.md` — §2 (multi-model routing)

## Your task

Produce 2–3 Architecture Decision Records for the most consequential design decisions made so far. ADRs are not post-hoc justification — they document the trade-off that was weighed and why an alternative was rejected.

Output file: `Deliverables/04-adrs.md`

---

## Required ADRs (produce all three)

**ADR-1: Delegation boundary** — Where is the agent/human boundary set, and why not further in either direction?

**ADR-2: Model selection and routing** — Which model(s) are used for which steps, and why not a single model for everything?

**ADR-3: A domain-specific architectural choice** — One decision specific to this scenario's constraints (e.g., audit trail design, escalation queue structure, confidence threshold governance, HITL packet design). Choose the decision with the highest stakes.

---

## Required structure for each ADR

```markdown
## ADR-[N]: [Decision title]

**Status:** Accepted
**Date:** [today's date]

### Context
[2–3 sentences: what situation made this decision necessary, what forces were in tension]

### Decision
[One sentence stating the decision made.]

### Rationale
[2–3 sentences: why this option was chosen over the alternatives — name the specific trade-off]

### Alternatives rejected

| Alternative | Why rejected |
|-------------|-------------|
| [Option A] | [specific reason — not "it was worse"] |
| [Option B] | [specific reason] |

### Consequences
**Positive:** [what this decision enables]
**Negative / trade-off accepted:** [what this decision costs or constrains]
**Risk if wrong:** [what breaks if the assumption behind this decision is incorrect]
```

---

## Acceptance criteria

- [ ] All three ADRs present
- [ ] Each ADR names at least 2 rejected alternatives with specific reasons — not "it was worse" or "too complex"
- [ ] ADR-1 delegation boundary traces to a compliance constraint or stakeholder position from the scenario
- [ ] ADR-2 model routing is consistent with P7 economics — the model choice is justified by cost + accuracy trade-off
- [ ] ADR-3 is specific to this scenario — not a generic architectural pattern
- [ ] Each ADR has a "risk if wrong" entry — what breaks if the assumption behind the decision is incorrect
