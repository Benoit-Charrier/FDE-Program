# Prompt: Deliverable 4 — Validation Design

## Scenario (read this first)
See `scenario.md`. Validation must be grounded in this scenario's specifics — 300 claims/day, 2-hour SLA, 18% routing error, 31% SLA breach, three integration systems. Generic test cases that could apply to any agent are a fail signal.

Also read `Delegation analysis.md` (Deliverable 2) before writing this — at least one test scenario must specifically test a delegation boundary.

## Your task
Produce a validation design. Output file: `4 Validation design.md` in the `Gate1/Output/` folder.

---

## Required structure

### 1. Validation strategy overview
One paragraph. How do you know the agent is working correctly? Answer both questions:
- How do you confirm it is right?
- How do you detect it is wrong — specifically quiet failure (wrong and no one notices)?

Name the detection mechanism for quiet failure explicitly. "Run tests" is not an answer.

### 2. Test scenarios

Minimum 3 scenarios. Required coverage:
- One happy path
- One edge case
- One failure mode
- One delegation boundary test

For every scenario use this format:

```
Scenario [N]: [Name]
Type: [Happy Path / Edge Case / Failure Mode / Delegation Boundary]
Description: [What this scenario tests and why it matters]

Preconditions:
- [system state before the test runs]

Input:
- [exact input data — claim type, value, policy state, etc. Be specific, not generic]

Expected agent behaviour (step by step):
1. [step]
2. [step]
...

Expected output:
- [exact state changes, records created, notifications sent]

Pass criterion: [boolean statement — what must be true for this scenario to pass]
Fail criterion: [boolean statement — what must be true to flag a regression]

Quiet failure risk: [Does this scenario have a failure mode where the agent is wrong but the output looks correct? If yes, describe it and name the detection mechanism.]
```

### 3. Delegation boundary test (required — must be its own scenario or explicitly labelled within one)
This test must verify that the correct tier fires for a claim that sits at a boundary threshold. For example: a claim just below and just above an escalation threshold. Both must produce different, verifiable behaviours.

Explicitly label this scenario: `Type: Delegation Boundary`.

### 4. Quiet failure detection design
Quiet failure = the agent produces an output that looks correct but is wrong, and the error is not surfaced by any alert or test.

For this FNOL scenario, name at least 3 quiet failure modes:

| Quiet failure mode | Why it would not be caught by standard tests | Detection mechanism |
|--------------------|----------------------------------------------|---------------------|

Detection mechanisms must be specific — not "monitor the agent" but "compare agent routing decisions against adjuster specialist codes; alert if mismatch rate > 5% over rolling 24h window."

### 5. Metrics to watch in production
Table format:

| Metric | Measurement method | Alert threshold | Action if breached |
|--------|--------------------|-----------------|---------------------|

Required metrics:
- Agent routing accuracy (compare to correct routing ground truth)
- SLA compliance rate (% claims acknowledged within 2 hours)
- Escalation rate (% claims escalated to human — too low is also a problem)
- Coverage validation confidence distribution (flag if median confidence drops)
- False negative escalation rate (claims that should have escalated but didn't)

---

## Acceptance criteria (all must pass)

- [ ] At least 3 scenarios present covering happy path, edge case, failure mode
- [ ] At least 1 scenario explicitly labelled as Delegation Boundary test
- [ ] Every scenario has concrete inputs (not "a typical claim" — specific values)
- [ ] Every scenario has explicit pass AND fail criteria as boolean statements
- [ ] Quiet failure risk is addressed in every scenario (even if "none identified")
- [ ] Quiet failure detection design names at least 3 failure modes with specific detection mechanisms
- [ ] Production metrics table present with numeric alert thresholds
- [ ] Escalation rate has a two-sided alert (too low AND too high)

## Fail signals — do not produce output that contains these

- Test scenarios with no concrete input values ("a valid claim", "a high-value claim")
- Pass criteria that only confirm the happy path ("agent routes correctly") without testing failure
- No quiet failure detection — only testing that the agent succeeds
- "Monitor the agent" or "review logs" as the only detection mechanism
- Generic scenarios not tied to the FNOL domain or this scenario's specific numbers
- Missing delegation boundary test
- Escalation rate monitored only in one direction (only "too high" or only "too low")
