# Prompt: Deliverable D2 — Engagement Intake & Scope

## Inputs (read all before writing)
- `Deliverables/D2A_cognitive_load_map.md` — micro-task breakdown, cognitive hotspots, breakpoints
- `Deliverables/D2B_delegation_suitability_matrix.md` — archetype assignments and dimension scores per JtD
- `Deliverables/D2C_volume_value_analysis.md` — prioritisation by volume × value, wave
- `scenario/scenario_context.md` — systems, constraints, stakeholders, governance requirements

See `scenario\scenario_context.md` for the full scenario, stakeholders, systems, and constraints. Do not invent numbers, people, or constraints not present in the scenario. Every claim must trace back to the scenario or be explicitly labelled as an assumption.

## Your task
Produce an engagement intake and scope document. Output file: `Deliverables\D2_engagement_intake_scope.md`.

---

## Required structure

### 0. Executive summary
Three bullet points, written first. Each bullet is one sentence. Cover in order:
1. Why this engagement is happening now — the business pressure and the specific trigger (tie to scenario evidence)
2. The MVP scope in one sentence — what the agent does, for whom, and what it does not do
3. The single constraint or risk most likely to determine whether this engagement succeeds or fails

### 1. Table of contents
Generate after the full document is written. Markdown anchor links, section titles must match exactly.

### 2. Business context
One paragraph. Explain:
- What MedFlex is trying to achieve and why the current approach cannot get them there
- What has already been tried and why it failed (the two prior AI projects are scenario evidence — name what they imply about organisational readiness)
- What the 8-week timeline signals about the CEO's tolerance for process and the risk that creates for scope discipline

This section must explain the *context* the engagement is operating inside — not restate the problem (that is D1's job).

### 3. Stakeholder map
Table format. For each named stakeholder in the scenario:

| Name / Role | What they need from this engagement | What they are worried about | Influence on success |
|-------------|-------------------------------------|-----------------------------|----------------------|
| | | | High / Medium / Low |

**Required entries:** at minimum the CEO, the operations lead or coordinator team, the hospital relationship owner (if named), and the nurse-facing contact (if named). If a stakeholder is not named in the scenario, label them as an assumed role and note the assumption.

Below the table: one short paragraph identifying the stakeholder whose buy-in is most at risk and why. This is not the most senior person — it is the person whose resistance or disengagement would most likely cause the engagement to fail quietly.

### 4. Constraints

Two sub-sections:

**4a. Hard constraints** — non-negotiable limits that the solution must operate within regardless of what would be technically ideal. For each:

> **Constraint [C-N]:** [what is fixed]
> **Source:** [scenario evidence or labelled assumption]
> **Agent design implication:** [what this rules out or requires]

Minimum 3 hard constraints. At minimum address: timeline, regulatory/compliance, and data availability.

**4b. Soft constraints** — preferences, political sensitivities, or organisational tendencies that should inform design but can be negotiated. List format, one line each. Label the source (scenario or assumption).

### 5. Risk register
For each risk, use this format:

> **Risk [R-N]:** [what could go wrong]
> **Category:** technical / adoption / compliance / timeline / data
> **Likelihood:** high / medium / low
> **Impact if it occurs:** [specific consequence for the engagement or the client]
> **Mitigation:** [what design or process choice reduces this risk]

Minimum 4 risks. Must include at least one adoption risk (the organisation rejects or works around the agent) and at least one data risk (the inputs the agent depends on are not as clean or available as assumed).

**Anti-pattern to avoid:** listing only technical risks. The most common engagement failure mode is adoption failure, not build failure.

### 6. MVP scope

**6a. In scope**
Bulleted list. Each item is a specific capability or workflow segment the agent handles in the first release. Each bullet must be testable — you should be able to observe whether the agent does or does not do this thing.

**6b. Out of scope**
Table format. Each exclusion must state why:

| What is excluded | Why it is excluded | When it could be added |
|------------------|--------------------|------------------------|

Minimum 4 exclusions. Do not use "not in scope" as a reason — name the actual reason (too risky for MVP, depends on data not yet available, requires integration not feasible in 8 weeks, etc.).

**6c. MVP success condition**
One paragraph. Complete this sentence: *"The MVP is successful when..."* The condition must be observable, time-bound, and agreed with the client. It must reference at least one metric from D1.

### 7. Assumption log
Use this format:

> **Assumption [A-N]:** [what you are taking as given]
> **Why it matters:** [which scope or constraint decision it drives]
> **If wrong:** [what changes in the engagement design]
> **Confidence:** low / medium / high

Minimum 3 assumptions. Every stakeholder listed as "assumed role" must have an entry here.

---

## Acceptance criteria (all must pass)

- [ ] Business context explains the *context* — not a restatement of the problem from D1
- [ ] Stakeholder map covers all named scenario stakeholders plus any assumed roles (labelled)
- [ ] At-risk stakeholder paragraph names a specific person/role with a specific reason — not "change management is hard"
- [ ] Hard constraints include timeline, regulatory/compliance, and data availability at minimum
- [ ] Risk register contains at least one adoption risk and one data risk
- [ ] Every out-of-scope exclusion states a concrete reason, not "not in scope"
- [ ] MVP success condition is observable, time-bound, and references a D1 metric
- [ ] Assumption log present with at least 3 entries

## Fail signals — do not produce output that contains these

- Stakeholder map that lists roles without naming what each person is worried about
- Risk register with only technical risks — adoption and data risks are required
- Out-of-scope table with "out of scope" or "not prioritised" as the reason column
- MVP success condition that is not observable ("the agent performs well" is not a condition)
- Business context that simply restates the problem statement — it must add context about organisational readiness, prior failure, and timeline pressure
- Constraints that are preferences dressed as hard stops, or hard stops buried in the soft constraints list
