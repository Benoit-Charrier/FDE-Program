# Prompt: Deliverable D7 — Validation Plan

## Scenario (read this first)
See `scenario\scenario_context.md` for the full scenario, work streams, tooling, and named-systems guidance. Do not invent numbers, systems, or constraints not present in the scenario. Every number you use must trace back to the scenario or be explicitly labelled as an assumption.

**Agent context:** Write the validation plan for the agents designed in D4 — the primary agentic targets identified in D3. The validation plan must be consistent with:
- D4's autonomy matrix and escalation triggers
- D2's delegation archetypes
- D5's build-loop response memo (known spec gaps, builder misreads, and legitimate unknowns that were surfaced)
- D5B's build-loop output (`Deliverables/D5B_build_loop_analysis.md`) — what was actually built, what questions the builder raised, what could not be built
- The hard stops and HITL triggers defined in CLAUDE.md

---

## Your task
Produce a Validation Plan. Be concise. Output file: `Deliverables/D7_validation_plan.md`.

Reference: `references\spec-ambiguity-vs-builder-mistakes.md` — use the failure taxonomy (spec ambiguity / builder misread / design gap / acceptable variation) to categorise every failure mode you identify.

---

## Required structure

### 0. Executive summary
Three bullet points, written first. Each bullet is one sentence. Cover in order:
1. The validation approach in one sentence — how correctness is confirmed on the autonomous path and how silent failure is detected (name the specific field or signal, not "monitoring")
2. The delegation boundary being stress-tested in S-3 — what the cheaper implementation would build and why that is wrong
3. The highest-risk quiet failure — the specific mechanism by which the agent produces wrong output with no exception raised, and what detects it

This section must be self-contained — a reader who reads only this section should understand how the agent proves it is right, where the hardest boundary test is, and what the most dangerous undetected failure looks like.

### 0b. Table of contents
List all sections by number and title as markdown anchor links, in order. Generate this after the full document is written — section titles must match exactly. Format each entry as `[N. Section title](#n-section-title)` using lowercase and hyphens for spaces.

Example format:
- [0. Executive summary](#0-executive-summary)
- [0b. Table of contents](#0b-table-of-contents)
- [1. Validation philosophy](#1-validation-philosophy)
- [2. Test scenarios](#2-test-scenarios)
- [3. Quiet failure catalogue](#3-quiet-failure-catalogue)
- [4. Build-loop diagnostic test](#4-build-loop-diagnostic-test)
- [5. Assumption log](#5-assumption-log)

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
| **Input** | Describe the specific document, record, or state the agent receives. Include numeric values (confidence scores, threshold values, field states, document metadata). Do not describe inputs generically — name the field values, thresholds, and condition that makes this case non-standard |
| **Expected agent behaviour** | Step-by-step: what does the agent do at each decision point? What does it write, enqueue, flag, or halt? |
| **Pass criteria** | Observable outputs that confirm correct behaviour — name the field, the value, the queue entry, the log line |
| **Failure signal** | What does wrong look like — not the exception, but the quiet wrong: what would be written, enqueued, or omitted that no one would notice without a specific check? |

The three scenarios must span:

1. **Happy path (S-1)** — the agent operates fully autonomously end-to-end. All conditions met, no HITL triggered, output committed to the system of record without human intervention. This test must also verify that the autonomous path is not broken by defensive coding added to handle edge cases.

2. **Edge case (S-2)** — a valid but non-standard input that sits exactly at a decision boundary: a confidence score at the threshold, a document at the anomaly size limit, a value that partially matches two categories, or an entity name at the fuzzy-match distance limit. The test must verify that the boundary is implemented as specified in CLAUDE.md — not as the cheapest available interpretation.

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

**Mechanism** means the specific condition that produced the wrong output — not "classification error," but the precise scenario (e.g., "entity name similarity score above fuzzy threshold, so the escalation trigger did not fire, but the entity was the same counterparty trading under a different registered name").

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
