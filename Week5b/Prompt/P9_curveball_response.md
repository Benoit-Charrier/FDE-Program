# Prompt: P9 — Curveball Response

## Inputs

- All prior deliverables in `Deliverables/`
- The curveball statement (provided at 13:30)

## Your task

Produce the curveball response. You have 30 minutes. The goal is a targeted, specific adaptation — not a full redesign.

**Before running this prompt:** Read the curveball carefully. In one sentence, write down the assumption it invalidates. If you cannot name the assumption, re-read the curveball.

Output file: `Deliverables/09-curveball-response.md`

---

## Required structure

### 1. The assumption invalidated
One sentence: "The curveball invalidates [assumption A-N from the assumption log], which stated [what it stated]."

If the curveball introduces a wholly new constraint not previously assumed, state: "The curveball introduces a new constraint not present in the original design: [constraint]."

### 2. What changes

For each deliverable that needs amendment, state specifically what changes:

| Deliverable | What changes | What stays the same |
|-------------|-------------|---------------------|

Be precise — name sections, fields, thresholds, or escalation triggers, not just "the design changes."

### 3. Spec amendments

For each change to the capability spec, write a targeted amendment:

**Amendment [N] to §[X]:**
> Original: [the original text or decision]
> Amended: [the replacement]
> Reason: [why the curveball requires this change]

### 4. What does NOT change
Name explicitly what the curveball does not affect. This demonstrates scope discipline — you are not using the curveball as an excuse to redesign everything.

### 5. Build impact
Does the curveball affect the prototype scope?

- If yes: name the specific code change required (which function, which check, which state transition)
- If no: state why the build is unaffected

---

## Acceptance criteria

- [ ] §1 names a specific assumption — not "the design needs to change"
- [ ] §2 table is specific — section numbers, field names, threshold values
- [ ] §3 amendments are surgical — only what the curveball requires
- [ ] §4 explicitly states what is unchanged — not left empty
- [ ] §5 build impact gives a code-level answer if the prototype needs to change
- [ ] Total response is focused and decisive — composure and specificity are graded, not completeness of redesign
