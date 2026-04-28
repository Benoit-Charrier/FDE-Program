# Prompt: Deliverable 2 — Delegation Analysis

## Scenario (read this first)
See `scenario.md`. The FNOL process has four named steps: triage by severity, validate against policy coverage, route to adjuster, acknowledge to claimant. Every delegation decision must be grounded in one of these steps or a sub-step you identify. Do not invent steps not present in the scenario.

## Your task
Produce a delegation analysis. Output file: `2 Delegation analysis.md` in the `/deliverables/` folder.

---

## Required structure

### 1. FNOL process decomposition
Break the four named steps into sub-tasks. For each sub-task, name it explicitly. This is the input to the delegation table.

### 2. Delegation table
For each sub-task, fill in all columns:

| Sub-task | Delegation tier | Rationale | Threshold / condition | Escalation path |
|----------|-----------------|-----------|-----------------------|-----------------|

**Delegation tiers (use exactly these labels):**
- `AGENT_ONLY` — agent decides and acts; no human review required
- `AGENT_LOG` — agent decides and acts; every decision is logged for audit
- `AGENT_REVIEW` — agent acts; human can review and veto within a defined window
- `AGENT_SUPPORT` — human decides; agent gathers information and presents options
- `HUMAN_ONLY` — human decides and acts; agent has no role

**Rationale must answer:** What makes this task safe (or unsafe) to delegate? Name the specific property — reversibility, consequence of error, ambiguity of input, regulatory requirement, tacit knowledge required, etc.

**Threshold / condition must be numeric or boolean.** No fuzzy language. Examples:
- `claim_value > £50,000`
- `coverage_match_confidence < 0.85`
- `claimant_sentiment = DISTRESSED AND claim_type = FATALITY`

If you cannot define a threshold yet, write `[TODO: define threshold]` and add it to the Assumptions log in Deliverable 5.

### 3. Delegation boundary justification
For each AGENT_ONLY and HUMAN_ONLY boundary, write one paragraph justifying *why* that boundary sits where it does — not what the task is, but why the line is drawn there. A coach will ask "why there and not one step further?" You must have an answer.

### 4. Override and audit requirements
For every tier that is not HUMAN_ONLY:
- Can a human override the agent's decision? Yes/No
- If yes: how is the override triggered, and how is it logged?
- What must be in the audit trail for this decision?

### 5. Assumption log (delegation-specific)
Use the standard format:

> **Assumption [D1]:** [what you're taking as given about the delegation boundary]
> **Why it matters:** [what breaks if the boundary is wrong]
> **If wrong:** [consequence — regulatory, operational, or trust-related]
> **Confidence:** low / medium / high

Minimum 2 delegation-specific assumptions.

---

## Acceptance criteria (all must pass)

- [ ] Every sub-task in the FNOL process has a tier assigned
- [ ] Every tier label is one of the five defined above (no invented labels)
- [ ] Every AGENT_ONLY or HUMAN_ONLY boundary has a written justification paragraph
- [ ] Every threshold is numeric or boolean — no "if the claim seems complex"
- [ ] Every [TODO] threshold is tracked in the assumption log
- [ ] Override mechanism is documented for every non-HUMAN_ONLY tier
- [ ] At least one boundary is defended with a regulatory or reversibility argument, not just convenience

## Fail signals — do not produce output that contains these

- Boundaries justified only by "the agent should use judgment"
- Fuzzy thresholds ("high-value claims", "complex cases", "if uncertain")
- Missing rationale — a table row with tier and no why
- Delegation tiers invented outside the five defined above
- No HUMAN_ONLY tasks (everything automated is a red flag for this scenario)
- No AGENT_ONLY tasks (excessive caution that defeats the business case)
- Override mechanism absent for any tier that is not HUMAN_ONLY
