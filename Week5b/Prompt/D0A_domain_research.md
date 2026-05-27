# Prompt: D0A — Domain Research

## Methodology references

- `References/atx-concepts.md` — digital labour taxonomy and what makes work delegable

## Inputs

- `Scenario/scenario_context.md` — read §1 (company) and §3 (process) to identify the industry and domain

## Your task

Produce a lean domain research brief for the scenario's industry. The goal is to give the FDE enough domain knowledge to make sound delegation decisions and avoid naive assumptions in later deliverables.

**Focus on what matters for agent design:** regulatory constraints, compliance requirements, data sensitivity, industry benchmarks, and known failure modes. Do not produce a general industry overview.

Output file: `Deliverables/D0A_domain_research.md`

---

## Required structure

### 1. Domain summary
Two sentences: what this industry does and what makes it operationally complex from an automation standpoint.

### 2. Key regulatory and compliance constraints
What rules govern automation, data handling, human-in-the-loop requirements, or audit trails in this domain? For each constraint:

> **[Constraint name / regulation]:** [what it requires] — **Impact on agent design:** [what this means for delegation boundaries or escalation triggers]

Minimum 3 constraints if applicable to the domain. If none apply, state why.

### 3. Industry benchmarks
What does "good" look like operationally in this domain? Include benchmark metrics relevant to the scenario's stated performance gaps.

| Metric | Industry benchmark | Why it matters for this design |
|--------|-------------------|-------------------------------|

### 4. Known automation failure modes
What has gone wrong when automation has been applied in this domain before? What are the dangerous failure modes specific to this industry?

For each:
> **Failure mode:** [what breaks] — **Why it is dangerous:** [consequence] — **Design implication:** [what the agent must guard against]

Minimum 2 entries.

### 5. Data sensitivity and handling constraints
What categories of data does this domain handle? What restrictions apply (PII, PHI, financial data, etc.)?

### 6. Domain-specific terminology
A brief glossary of 5–10 terms the FDE needs to use correctly in deliverables. Incorrect terminology in specs causes builder errors.

---

## Acceptance criteria

- [ ] §2 names at least 3 real regulatory constraints relevant to the domain (or explicitly states none apply)
- [ ] §3 benchmarks are industry-standard figures, not invented
- [ ] §4 failure modes are specific to this domain — not generic "AI can be wrong"
- [ ] §6 glossary terms are precise enough to appear in a capability spec without ambiguity
- [ ] Nothing invented about the specific scenario company — this is domain knowledge, not scenario facts
