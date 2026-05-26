# Prompt: Deliverable 2 — Delegation Suitability Matrix

## Scenario (read this first)
See `scenario\scenario_context.md` for the full scenario, work streams, tooling, and named-systems guidance. Do not invent numbers, systems, or constraints not present in the scenario. Every number you use must trace back to the scenario or be explicitly labelled as an assumption.

---

## Your task
Produce a Delegation Suitability Matrix. Be concise. Output file: `deliverables\D2B_delegation_suitability_matrix.md`.

This is Phase 3 of the ATX Assessment. Score each major task cluster on delegation suitability dimensions, assign delegation archetypes with rationale, and determine the overall delegation architecture.

Reference: `references\1-ATX-Assessment.md` Phase 3.

---

## Required structure

### 0. Executive summary
Three bullet points, written first. Each bullet is one sentence. Cover in order:
1. The delegation architecture in one sentence — how many clusters are fully/agent-led vs. human-anchored, and what governs the split
2. The most contested archetype assignment — which cluster sits closest to the boundary between two archetypes and what tips it one way
3. Where the scenario's primary governance constraint lands in the architecture — which specific cluster(s) it locks to human control and why that is non-negotiable

This section must be self-contained — a reader who reads only this section should understand the overall delegation shape, the hardest call made, and where the hard rule is enforced.

### 0b. Table of contents
List all sections by number and title as markdown anchor links, in order. Generate this after the full document is written — section titles must match exactly. Format each entry as `[N. Section title](#n-section-title)` using lowercase and hyphens for spaces.

Example format:
- [0. Executive summary](#0-executive-summary)
- [0b. Table of contents](#0b-table-of-contents)
- [1. Task cluster definition](#1-task-cluster-definition)
- [2. Delegation Suitability Matrix](#2-delegation-suitability-matrix)
- [3. Delegation archetype assignment with rationale](#3-delegation-archetype-assignment-with-rationale)
- [4. Delegation architecture summary](#4-delegation-architecture-summary)
- [5. Delegation boundary defence](#5-delegation-boundary-defence)
- [6. Assumption log](#6-assumption-log)

### 1. JtD inventory
Before scoring, list the JtDs you will score. Use the JtDs from D2A directly: §2b and §3b for the two fully mapped work streams; Do not derive new JtDs here — if a work stream has no JtDs in D2A, return to D2A and complete §5 before proceeding. List each JtD with a one-sentence description of its cognitive contract and which work stream it belongs to.

### 2. Delegation Suitability Matrix

One table covering all JtDs:

| JtD | Work Stream | Input Structure (H/M/L) | Decision Determinism (H/M/L) | Tool Coverage (H/M/L) | Context Complexity (H/M/L) | Exception Rate (H/M/L) | Latency Constraint (H/M/L) | Risk/Compliance (H/M/L) | Suitability Score | Delegation Archetype |
|-----|-------------|------------------------|------------------------------|----------------------|---------------------------|------------------------|---------------------------|------------------------|-------------------|----------------------|

**Suitability score**: count the number of dimensions at High suitability (for input structure, decision determinism, tool coverage — higher = better; for context complexity, exception rate, latency constraint, risk/compliance — lower = better). Express as a score out of 7.

**Scoring notes:** Below the table, add a brief justification (2–4 sentences) for each JtD's archetype assignment. Do not assert; justify.

### 3. Delegation archetype assignment with rationale

For each JtD, state its archetype and defend it. Use this format:

> **JtD [J-N] — [name]**
> **Archetype:** [Human Only / Human-led + Automation Support / Human-led + Agent Support / Agent-led + Human Oversight / Fully Agentic]
> **Rationale:** [cite the specific dimensions that drove this assignment — at least 2 dimensions with their scores]
> **Governance rule impact (if applicable):** [does the scenario's primary hard constraint change the archetype? If so, how?]
> **Anti-pattern check:** [could this be solved with static rules, RPA, or a simple script? If yes, do not assign an agentic archetype]

### 4. Delegation architecture summary

After completing all cluster assignments, step back and describe the overall delegation architecture as a system:

- Which JtDs form the **autonomous backbone** (fully agentic or agent-led with oversight)?
- Which JtDs are the **human-anchored gates** that the agent cannot cross without approval?
- Which JtDs are **not worth automating** and why?
- Where is the scenario's primary hard constraint enforced in the architecture? Name the exact JtD(s) and archetype(s) that implement it.

Write this as a coherent 3–5 paragraph narrative, not as a list.

### 5. Delegation boundary defence

Pick the 2 most debatable archetype assignments (where a reasonable person might argue for a different archetype). For each:

> **Contested assignment:** [JtD name] — assigned [archetype]
> **The counter-argument:** [why someone might assign a more or less autonomous archetype]
> **Why the assigned archetype is correct for this scenario:** [specific reasoning tied to scenario facts]
> **What would change the assignment:** [conditions under which you would revise it]

### 6. Assumption log
Use this format for every non-trivial claim:

> **Assumption [A1]:** [what you're taking as given]
> **Why it matters:** [what spec decision or metric it drives]
> **If wrong:** [what breaks]
> **Confidence:** low / medium / high

Minimum 2 assumptions in this section. More is better.

---

## Acceptance criteria (all must pass)

- [ ] All work streams from scenario_context.md represented in the matrix
- [ ] At least 2 JtDs scored per work stream (minimum 8 JtDs total)
- [ ] Every archetype assignment has a written rationale citing at least 2 dimensions
- [ ] The scenario's primary hard constraint is explicitly reflected in the architecture
- [ ] Anti-pattern check performed for every cluster (no agent assigned to purely deterministic work)
- [ ] Delegation architecture summary describes the system as a whole, not just each cluster independently
- [ ] Two contested assignments defended in the format specified
- [ ] Suitability scores consistent with archetype assignments (a cluster with suitability score 2/7 should not be "fully agentic")

## Fail signals — do not produce output that contains these

- Assigning "agent-led" archetype to a JtD that requires the judgment expertise the scenario marks as Human Only, without explaining how the governance constraint is satisfied
- All JtDs assigned the same archetype (that means you haven't differentiated)
- Anti-pattern check missing — if you can't confirm "this is not solvable by a script," you haven't done the analysis
- Rationale that says "this is complex, therefore human-only" without naming which specific suitability dimensions are Low
- Architecture summary that is just a list of archetypes restated, not a description of how they work together
- JtDs for the two work streams not in D2A invented without grounding in the scenario — derive them from the scenario's stated volume, decision types, and system touchpoints
