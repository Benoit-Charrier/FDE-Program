# Prompt: Deliverable 4 — Agent Purpose Document

## Scenario (read this first)
See `scenario\scenario_context.md` for the full scenario, work streams, tooling, and named-systems guidance. Do not invent numbers, systems, or constraints not present in the scenario. Every number you use must trace back to the scenario or be explicitly labelled as an assumption.

---

## Your task
Produce an Agent Purpose Document for the **highest-value agentic opportunity** identified in D3. Be concise. Output file: `deliverables\D4_agent_purpose_document.md`.

This document must be precise enough that an AI coding agent could begin development without asking a clarifying question about the agent's purpose, scope, KPIs, activity catalog, autonomy boundaries, or escalation logic.

Reference: `references\atx-agent-mapping.md`.

---

## Required structure

### 0. Executive summary
Three bullet points, written first. Each bullet is one sentence. Cover in order:
1. The agent's Job to be Done — what outcome it produces, for whom, and what it replaces in the current process (tie to a scenario number)
2. The autonomy boundary — what the agent decides alone versus what it cannot proceed without human approval (name the governance constraint explicitly)
3. The primary failure risk — the most consequential failure mode and how it is detected before it causes harm downstream

This section must be self-contained — a reader who reads only this section should understand what the agent does, where it stops, and what could go wrong.

### 0b. Table of contents
List all sections by number and title as markdown anchor links, in order. Generate this after the full document is written — section titles must match exactly. Format each entry as `[N. Section title](#n-section-title)` using lowercase and hyphens for spaces.

Example format:
- [0. Executive summary](#0-executive-summary)
- [0b. Table of contents](#0b-table-of-contents)
- [1. Agent identity](#1-agent-identity)
- [2. Primary objectives](#2-primary-objectives)
- [3. KPIs](#3-kpis)
- [4. Activity catalog](#4-activity-catalog)
- [5. Autonomy matrix (Decision Authority Matrix)](#5-autonomy-matrix-decision-authority-matrix)
- [6. Escalation triggers](#6-escalation-triggers)
- [7. Failure modes](#7-failure-modes)
- [8. Out-of-scope (hard stops)](#8-out-of-scope-hard-stops)

### 1. Agent identity
Provide:
- **Agent name:** [descriptive, not generic — should reflect the job it does]
- **Job to be Done:** [the cognitive contract — one sentence stating what outcome this agent produces for the business]
- **Business context:** [which team, which process step, which downstream handoff]
- **Delegation archetype:** [from D2 — name it and confirm it hasn't changed]

### 2. Primary objectives
State 2–3 objectives. Each must be measurable. No directional language ("improve", "reduce") — concrete targets only.

### 3. KPIs
Complete this table. Every metric must have a baseline from the scenario (or labelled assumption) and a specific numeric target.

| KPI | Baseline | Target | Measurement method | Review cadence |
|-----|----------|--------|--------------------|---------------|
| Accuracy (correct primary-task output %) | | | | |
| Coverage (% of cases handled without human escalation for this work stream) | | | | |
| Throughput (cases processed per hour) | | | | |
| HITL rate (% requiring human review within scope) | | | | |
| Turnaround time contribution (minutes per case for this work stream) | | | | |

All targets must be specific numbers. "How measured" must be concrete — name what system records the metric, not "track in a dashboard."

### 4. Activity catalog
Enumerate every micro-task the agent performs. One row per task:

| Task ID | Task name | Task type | Delegation level | Data required | Tool required | Risk level |
|---------|-----------|-----------|-----------------|---------------|---------------|------------|

**Task types:** Reasoning / Retrieval / Decision / Action / Generation
**Delegation levels:** Fully agentic / Agent-led + HITL on condition / Human-led + Agent support
**Risk levels:** Low / Medium / High

Include at least 8 tasks. Every task with risk level High must have a corresponding entry in the escalation triggers section (§6).

### 5. Autonomy matrix (Decision Authority Matrix)
Define the operational contract between the agent and the organisation. Use the four-tier format:

**AGENT DECIDES ALONE (no HITL required):**
- [list of specific decisions or actions, with any value/scope thresholds]

**AGENT ACTS, HUMAN NOTIFIED AFTER:**
- [list of specific decisions or actions]

**AGENT PROPOSES, HUMAN APPROVES BEFORE ACTION:**
- [list of specific decisions or actions — the scenario's primary approval gate belongs here]

**HUMAN TAKES OVER (agent supports only):**
- [list of specific triggers — be concrete; "complexity" is not a trigger]

The scenario's primary governance/compliance hard constraint (from scenario_context.md) must appear explicitly in the "AGENT PROPOSES, HUMAN APPROVES BEFORE ACTION" tier — with exact language about what the agent prepares and what the designated approver approves.

### 6. Escalation triggers
For each escalation condition, specify the trigger precisely and name the human role who receives it:

| Trigger ID | Condition | Escalate to | What the agent provides at escalation | Response SLA |
|-----------|-----------|-------------|---------------------------------------|-------------|

Minimum 5 escalation triggers. Conditions must be specific — not "agent is uncertain" but "confidence score below the defined threshold" or "input type is not among the scenario's defined categories."

### 7. Failure modes
For each failure mode, complete the following:

> **Failure Mode [FM-N]:** [what a bad output looks like]
> **Consequence:** [what breaks downstream — for the team receiving the output, for the dependent process, for the business]
> **Detection:** [how would this failure be caught? By whom? At what latency?]
> **Recovery path:** [what happens to put things right?]

Minimum 4 failure modes. At least one must address the consequences of a false classification (e.g., routing an escalation-required case as a standard case).

### 8. Out-of-scope (hard stops)
List things this agent must NEVER do, even if instructed:

- [specific forbidden action 1 — e.g., "never send a governance-gated output to an external party without the designated approver's token recorded in the case"]
- [minimum 4 entries]

---

## Acceptance criteria (all must pass)

- [ ] Job to be Done is a cognitive contract (outcome-focused), not a task description
- [ ] All KPI baselines trace to the scenario or are labelled assumptions
- [ ] All KPI targets are specific numbers, not directions
- [ ] Activity catalog has at least 8 tasks with all columns populated
- [ ] Autonomy matrix explicitly places the scenario's primary governance/compliance constraint in the "AGENT PROPOSES, HUMAN APPROVES BEFORE ACTION" tier
- [ ] Every High-risk task in the activity catalog has a corresponding escalation trigger
- [ ] At least 4 failure modes with detection and recovery paths
- [ ] Out-of-scope section present with at least 4 hard stops
- [ ] Document is precise enough that an AI coding agent would not need to ask a clarifying question about scope, KPIs, or escalation logic

## Fail signals — do not produce output that contains these

- KPIs with directional targets ("reduce review time") — all targets must be numbers
- Escalation triggers like "when the contract is complex" — name the specific detectable condition
- Failure modes with no detection mechanism ("someone notices the error")
- Autonomy matrix with no explicit placement of the scenario's primary governance constraint
- Activity catalog tasks with risk level High but no corresponding escalation trigger
- An agent that can trigger the governance-gated action without the required human approval (violates the scenario's primary hard constraint)
