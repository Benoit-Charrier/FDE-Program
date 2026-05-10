# Prompt: Deliverable D3 — Agentic Solution Architecture

## Inputs (read all before writing)
- `Deliverables/D2A_cognitive_load_map.md` — micro-task breakdown, cognitive hotspots, breakpoints
- `Deliverables/D2B_delegation_suitability_matrix.md` — archetype assignments and dimension scores per JtD
- `Deliverables/D2C_volume_value_analysis.md` — prioritisation by volume × value
- `Deliverables/D2_engagement_intake_scope.md` - MVP scope
- `scenario/scenario_context.md` — systems, constraints, stakeholders, governance requirements

Do not produce an architecture that is inconsistent with the delegation archetypes in D2B or the priority ordering in D2C. Every design decision must trace to one of these inputs or be flagged as an assumption.

## Your task
Produce an agentic solution architecture document. Output file: `Deliverables/D3_agentic_solution_architecture.md`.

This document answers two questions: **which parts of the workflow become agentic and at what delegation level**, and **why those design decisions were made over the alternatives**. It is not a technical specification — that is D4's job. It is an architectural design with justified trade-offs.

**AI-native requirement:** The architecture must use agents as the primary mechanism for delivering value — not a deterministic workflow engine with an LLM call sprinkled in. The document must identify at least one point where agent reasoning over context produces an outcome a rule-based system could not reliably reach.

---

## Required structure

### 0. Executive summary
Three bullet points, written first. Each bullet is one sentence:
1. The primary agentic target — which workflow segment, at what delegation level, and what it replaces
2. The central architectural decision and the alternative that was rejected
3. The condition most likely to constrain the architecture in production (not a generic risk — name the specific constraint from scenario or D2B)

### 1. Table of contents
Generate after the full document is written. Markdown anchor links, exact section title matches.

### 2. Workflow-to-agent mapping

Table format. For each JtD from D2B, state:

| JtD (from D2B) | Delegation archetype (from D2B) | Agentic? | Agent / role assigned | Justification |
|----------------|---------------------------------|----------|-----------------------|---------------|

- **Agentic?** — Yes / Partial (HITL) / No (stays human)
- **Justification** — cite the specific D2B dimension scores or D2C priority that drove the decision; do not assert without evidence
- Every "No" must name the reason from D2B (which dimension blocked delegation) — not just "too complex"

Below the table: one paragraph identifying the **AI-native moment** — the specific point in the workflow where agent reasoning over context determines an outcome that a rule-based system could not reach. If no such moment exists, the architecture is not AI-native and must be redesigned before proceeding.

### 3. Agent design summary

For each agent in the architecture, produce a compact purpose block:

> **Agent [N]: [name]**
> **Job to be done:** [the cognitive contract — what outcome does this agent produce?]
> **Workflow segments covered:** [which JtDs from section 2]
> **Tools required:** [what the agent must be able to call or write to]
> **Context required:** [what data the agent must see to do its job]
> **Escalation triggers:** [the specific conditions that route to HITL or human takeover]
> **Governance constraint:** [the non-negotiable hard stop from the scenario — if none applies, state that explicitly]

Minimum 1 agent, maximum justified by the workflow. Do not create agents for the sake of modularity — each agent must have a distinct job.

### 4. Autonomy matrix

Table showing the full authority map across all agents. Every action the architecture takes must appear in exactly one cell:

| Action | Agent decides alone | Agent acts, human notified | Agent proposes, human approves | Human takes over |
|--------|--------------------|-----------------------------|-------------------------------|-----------------|

Below the table: identify the **hardest boundary** — the action that sits closest to the line between "agent proposes, human approves" and "human takes over," and explain why it sits where it does. This is the boundary the client will push on most during the verbal defense.

### 5. Architecture Decision Records

Include at least 2 ADRs. Each ADR must follow this exact structure:

---
**ADR-[N]: [decision title — a noun phrase naming the decision, not the outcome]**

**Status:** Proposed

**Context:**
What situation made this decision necessary? Name the specific workflow constraint, data condition, compliance requirement, or stakeholder concern that forced a choice. One short paragraph.

**Decision:**
What was chosen. One sentence, direct.

**Alternatives considered:**

| Alternative | Trade-offs | Why rejected |
|-------------|------------|--------------|
| [Option A — the chosen path] | [what it costs; what it enables] | *(chosen)* |
| [Option B] | [what it costs; what it enables] | [specific reason it was not chosen] |
| [Option C if applicable] | [what it costs; what it enables] | [specific reason] |

**Consequences:**
- *Enables:* [what this decision makes possible or easier]
- *Forecloses:* [what this decision makes harder or impossible later]
- *Assumes:* [what must be true for this decision to hold — flag as assumption if not in scenario]

**Revisit condition:**
[The specific circumstance that would cause this decision to be reconsidered — not "if requirements change"]

---

**ADR content requirements:**
- At least one ADR must address **delegation level** — a decision about whether a specific workflow segment is fully agentic, HITL, or human-led
- At least one ADR must address **architecture pattern** — orchestration vs. parallel agents, synchronous vs. async, tool choice, or integration approach
- The rejected alternatives must be real options, not strawmen. If the only reason to reject an alternative is "it's worse," the ADR has not done its work
- "We chose X because it is the right choice" is not a consequence — name what X forecloses

### 6. Non-agentic residual

Bulleted list. For each workflow segment that stays human-led (from section 2):

> **[JtD]** — stays human because: [the specific D2B dimension that blocked delegation, e.g., "exception frequency H, decision determinism L"]. Agent role: [what the agent does to support the human in this segment, if anything]. Future delegation path: [the condition under which this could become agentic — or "no clear path" if none exists].

This section is not a failure list. A well-designed architecture has non-agentic residual. The question is whether it is the *right* residual.

### 7. Assumption log

> **Assumption [A-N]:** [what is being taken as given]
> **Source:** D3A / D3B / D3C / scenario / inferred
> **Why it matters:** [which architectural decision it enables or constrains]
> **If wrong:** [what changes in the architecture]
> **Confidence:** low / medium / high

Minimum 3 assumptions. Every ADR "Assumes" line must have a corresponding entry here.

---

## Acceptance criteria (all must pass)

- [ ] Every JtD from D2B appears in section 2 — nothing is silently dropped
- [ ] Every "agentic" assignment in section 2 traces to a D2B archetype or D2C priority score — not asserted
- [ ] Every "no" in section 2 names the blocking D2B dimension — not just "too complex" or "too risky"
- [ ] AI-native moment is explicitly named in section 2 — if it cannot be named, the architecture is not AI-native
- [ ] Each agent purpose block includes governance constraint — even if the answer is "none applies"
- [ ] Autonomy matrix covers every action the architecture takes — no gaps
- [ ] Hardest boundary is named and justified in section 4
- [ ] At least 2 ADRs, each with alternatives table and consequences block
- [ ] One ADR addresses delegation level; one addresses architecture pattern
- [ ] ADR rejected alternatives are real options with genuine trade-offs — not strawmen
- [ ] Non-agentic residual explains future delegation path (or explicitly states "no clear path")
- [ ] Assumption log has at least 3 entries; every ADR "Assumes" line is covered

## Fail signals — do not produce output that contains these

- JtDs from D2B missing from section 2 without explanation
- "Fully agentic" assigned to a segment that D2B scored as exception-heavy or regulation-sensitive, without naming and justifying the override
- ADR alternatives that exist only to be dismissed — real trade-offs must be visible
- ADR consequences that only describe benefits — every decision forecloses something
- An autonomy matrix with no "human takes over" row — every production architecture has hard stops
- Architecture that is a deterministic matcher or rule engine with an LLM wrapper, with no point where agent reasoning over context produces a distinctly different outcome
- Non-agentic residual section that reads as an apology — explain why it is the right boundary, not why it couldn't be automated
