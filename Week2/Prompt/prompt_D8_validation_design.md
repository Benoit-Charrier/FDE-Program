# Prompt: Deliverable 8 — Validation Design

## Scenario (read this first)
See `scenario\scenario_context.md` for the full scenario, work streams, tooling, and named-systems guidance. Do not invent numbers, systems, or constraints not present in the scenario. Every number you use must trace back to the scenario or be explicitly labelled as an assumption.

**Agent context:** Write the validation design for the agent designed in D4 — the primary agentic target identified in D3. The validation design must be consistent with D4's autonomy matrix and escalation triggers, D2's delegation archetypes, D5's known system gaps, and the hard stops and HITL triggers defined in CLAUDE.md.

---

## Your task
Produce a Validation Design. Be concise. Output file: `deliverables\D8_Validation_Design.md`.

Reference: `references\spec-ambiguity-vs-builder-mistakes.md` — use the failure taxonomy (spec ambiguity / builder misread / design gap / acceptable variation) to categorise every failure mode you identify.

---

## Required structure

### 1. Validation philosophy
One paragraph maximum. Answer two questions — both must be answered explicitly:
- How do you confirm the agent is right on the cases it handles?
- How do you detect the agent is wrong — especially when it fails silently, with no exception raised and no human immediately notified?

Do not write generic statements about "monitoring" or "logging." Name the specific field, the specific threshold, the specific person or queue that receives the alert, and the SLA for response.

---

### 2. Test scenarios

Produce exactly three scenarios. Each must use the following structure:

| Field | Content |
|-------|---------|
| **Scenario ID** | S-1 / S-2 / S-3 |
| **Name** | A specific descriptive name — not "happy path" or "failure mode" |
| **Type** | Happy path / Edge case / Failure mode |
| **Delegation boundary tested** | Name the specific archetype assignment from D2 being stressed — the claim that this task is fully agentic, or this trigger pushes to HITL, or this action is human-only |
| **Input** | Describe the specific document, record, or state the agent receives. Include numeric values (clause cap amounts, confidence scores, vendor history, document page count). Do not say "a contract with a minor deviation" — say what the deviation is and what the playbook floor is |
| **Expected agent behaviour** | Step-by-step: what does the agent do at each decision point? What does it write, enqueue, flag, or halt? |
| **Pass criteria** | Observable outputs that confirm correct behaviour — name the field, the value, the queue entry, the log line |
| **Failure signal** | What does wrong look like — not the exception, but the quiet wrong: what would be written, enqueued, or omitted that no one would notice without a specific check? |

The three scenarios must span:

1. **Happy path (S-1)** — the agent operates fully autonomously end-to-end. All conditions met, no HITL triggered, output committed to the system of record without human intervention. This test must also verify that the autonomous path is not broken by defensive coding added to handle edge cases.

2. **Edge case (S-2)** — a valid but non-standard input that sits exactly at a decision boundary: a confidence score at the threshold, a document at the anomaly size limit, a clause that partially matches two playbook categories, or a vendor name at the fuzzy-match distance limit. The test must verify that the boundary is implemented as specified in CLAUDE.md — not as the cheapest available interpretation.

3. **Delegation boundary failure (S-3)** — this scenario must be designed so that a coding agent reading only the spec could reasonably implement the step as fully agentic (the cheapest option), when the correct implementation is agent-led with oversight or human-only. Describe explicitly: (a) what the coding agent would build if it defaulted to the cheaper archetype, (b) why that implementation is wrong, and (c) why the test fails if the cheaper implementation was built.

---

### 3. Quiet failure catalogue

List at least 4 failure modes where the agent produces output, no exception is raised, and no human is immediately alerted — but the output is wrong.

| QF ID | Mechanism | What was written (or not written) | Why no one notices immediately | Detection check | Taxonomy category |
|-------|-----------|-----------------------------------|-------------------------------|-----------------|-------------------|
| QF-1 | | | | | spec ambiguity / builder misread / design gap / acceptable variation |
| QF-2 | | | | | |
| QF-3 | | | | | |
| QF-4 | | | | | |

**Mechanism** means the specific condition that produced the wrong output — not "classification error," but the precise scenario (e.g., "vendor name Levenshtein distance = 3, above fuzzy threshold, so ET-6 did not fire, but the vendor was the same entity trading under a subsidiary name").

**Detection check** must name a concrete action: a field audit on a named field, a review of override rates against a threshold, a downstream system rejection, or a periodic spot-check by a named person on a named schedule.

**Taxonomy category** uses the four categories from `references\spec-ambiguity-vs-builder-mistakes.md`. The category tells you where the fix belongs: in the spec, in a re-prompt, in a new test, or in a note that the variation is acceptable.

---

### 4. Build-loop diagnostic test

Write one concrete test — expressed as pytest-style pseudocode — that would detect if the coding agent defaulted to the wrong delegation archetype for the boundary tested in S-3.

The test must include:
- **Fixture:** the exact input record or document state (field names and values)
- **Assertion:** the specific field value, queue entry, or absence of write that proves the correct archetype was implemented
- **Anti-assertion:** what the cheaper implementation would produce instead — so the failure mode is unambiguous
- **Taxonomy classification:** is this test catching a spec ambiguity, a builder misread, or a design gap? State which and why.

---

### 5. Assumption log

Use this format for every non-trivial claim:

> **Assumption [A1]:** [what you are taking as given]
> **Why it matters:** [what test outcome or detection check it drives]
> **If wrong:** [what breaks — which test passes when it should fail, or which quiet failure goes undetected]
> **Confidence:** low / medium / high

Minimum 2 assumptions. Label any numeric threshold not derivable from the scenario as an assumption here.

---

## Acceptance criteria (all must pass)

- [ ] Validation philosophy answers both questions (confirm right AND detect wrong) with specific fields, thresholds, people, and SLAs
- [ ] Three scenarios present: happy path, edge case, delegation boundary failure
- [ ] S-3 describes explicitly what the cheaper implementation would build and why the test fails for it
- [ ] Quiet failure catalogue has at least 4 entries with mechanism (not label), detection check (not generic "monitor"), and taxonomy category
- [ ] Build-loop diagnostic test has a fixture, assertion, anti-assertion, and taxonomy classification
- [ ] Every numeric value traces to the scenario, D4, D5, or CLAUDE.md — or is labelled as an assumption
- [ ] Taxonomy categories from `spec-ambiguity-vs-builder-mistakes.md` used correctly throughout

## Fail signals — do not produce output that contains these

- Scenarios named "happy path," "edge case," or "failure mode" without a specific descriptive name encoding what is being tested
- Pass criteria that describe behaviour in prose without naming a specific field, value, or queue entry
- Quiet failure entries where the mechanism is "classification error" or "wrong output" — name the specific condition that caused it
- Detection checks that say "monitor logs" or "review periodically" without naming who, what field, what threshold, and what schedule
- A delegation boundary failure scenario (S-3) that does not describe what the cheaper implementation would produce
- Taxonomy categories applied without a one-sentence justification for the categorisation
