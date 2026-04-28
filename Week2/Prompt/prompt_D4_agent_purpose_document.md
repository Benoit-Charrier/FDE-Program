# Prompt: Deliverable 4 — Agent Purpose Document

## Scenario (read this first)
See `scenario\enriched_scenario.md`. Do not invent numbers, systems, or constraints not present there. Every number you use must trace back to the scenario or be explicitly labelled as an assumption.

**Scenario summary (for reference):**
- **Helix Workforce Software** — UK-based B2B SaaS (~480 employees, ARR £42M, 25% YoY growth); sells workforce-planning software to UK/EU enterprises
- Legal team (5-person): **Amelia Forsythe** (General Counsel, 12 years at Helix), 3 Commercial Lawyers (3–6 yrs experience), **Tom** (Paralegal)
- ~300 inbound vendor contracts per quarter; each 15–40 pages
- Playbook checklist: liability caps, DPAs, termination clauses, IP ownership, SLA commitments, governing law, indemnity scope (7 clause types); playbook is 9 months stale — DPDI Act Q1 updates not yet incorporated
- 70% standard / 20% negotiable deviations (paralegal can redline) / 10% senior-lawyer escalation
- Turnaround: 4–6 business days; CRO is pressuring Legal to halve turnaround to support enterprise sales targets
- GC hard rule: no counteroffer leaves legal's queue without a named lawyer's sign-off on the specific clauses being negotiated
- Tooling: **Ironclad** (CLM, REST APIs), **Microsoft Word + Track Changes** + **SharePoint** (redlining & storage), **Salesforce** (sales pipeline), **Outlook** (vendor procurement), internal SharePoint playbook page

---

## Your task
Produce an Agent Purpose Document for the **highest-value agentic opportunity** identified in D3. Output file: `deliverables\D4_agent_purpose_document.md`.

This document must be precise enough that an AI coding agent could begin development without asking a clarifying question about the agent's purpose, scope, KPIs, activity catalog, autonomy boundaries, or escalation logic.

Reference: `references\atx-agent-mapping.md`.

---

## Required structure

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
| Accuracy (correct clause classification %) | | | | |
| Coverage (% of cases handled without human escalation for this work stream) | | | | |
| Throughput (contracts processed per hour) | | | | |
| HITL rate (% requiring human review within scope) | | | | |
| Turnaround time contribution (minutes per contract for this work stream) | | | | |

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
- [list of specific decisions or actions — the counteroffer sign-off gate belongs here]

**HUMAN TAKES OVER (agent supports only):**
- [list of specific triggers — be concrete; "complexity" is not a trigger]

The GC's hard rule (named-lawyer sign-off on specific clauses being negotiated) must appear explicitly in the "AGENT PROPOSES, HUMAN APPROVES BEFORE ACTION" tier with exact language about what the agent prepares and what the lawyer approves.

### 6. Escalation triggers
For each escalation condition, specify the trigger precisely and name the human role who receives it:

| Trigger ID | Condition | Escalate to | What the agent provides at escalation | Response SLA |
|-----------|-----------|-------------|---------------------------------------|-------------|

Minimum 5 escalation triggers. Conditions must be specific — not "agent is uncertain" but "confidence score below 0.85 on clause classification" or "clause type is not among the 7 playbook categories."

### 7. Failure modes
For each failure mode, complete the following:

> **Failure Mode [FM-N]:** [what a bad output looks like]
> **Consequence:** [what breaks downstream — for the legal team, for procurement, for the business]
> **Detection:** [how would this failure be caught? By whom? At what latency?]
> **Recovery path:** [what happens to put things right?]

Minimum 4 failure modes. At least one must address the consequences of a false classification (e.g., classifying a 10% escalation-required contract as standard).

### 8. Out-of-scope (hard stops)
List things this agent must NEVER do, even if instructed:

- [specific forbidden action 1 — e.g., "never send a redline or counteroffer to a vendor without a named lawyer's approval token in the case record"]
- [minimum 4 entries]

---

## Acceptance criteria (all must pass)

- [ ] Job to be Done is a cognitive contract (outcome-focused), not a task description
- [ ] All KPI baselines trace to the scenario or are labelled assumptions
- [ ] All KPI targets are specific numbers, not directions
- [ ] Activity catalog has at least 8 tasks with all columns populated
- [ ] Autonomy matrix explicitly places the GC sign-off rule in the "AGENT PROPOSES, HUMAN APPROVES" tier
- [ ] Every High-risk task in the activity catalog has a corresponding escalation trigger
- [ ] At least 4 failure modes with detection and recovery paths
- [ ] Out-of-scope section present with at least 4 hard stops
- [ ] Document is precise enough that an AI coding agent would not need to ask a clarifying question about scope, KPIs, or escalation logic

## Fail signals — do not produce output that contains these

- KPIs with directional targets ("reduce review time") — all targets must be numbers
- Escalation triggers like "when the contract is complex" — name the specific detectable condition
- Failure modes with no detection mechanism ("someone notices the error")
- Autonomy matrix with no explicit placement of the GC sign-off rule
- Activity catalog tasks with risk level High but no corresponding escalation trigger
- An agent that can send a counteroffer to a vendor without lawyer approval (violates GC rule — this is the hardest hard stop)
