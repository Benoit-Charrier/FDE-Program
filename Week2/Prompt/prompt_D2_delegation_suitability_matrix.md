# Prompt: Deliverable 2 — Delegation Suitability Matrix

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

**The four work streams:**
1. First-pass clause classification (~300/quarter; ~25 min/case): triaging inbound contracts, classifying each major clause against the playbook
2. Standard-deviation redlining (~60/quarter; ~45 min/case): paralegal redlines negotiable deviations against playbook without escalation
3. Escalated clause review (~30/quarter; ~90 min/case): senior lawyer reviews unusual clauses, frames counteroffer position, drafts redline
4. Counteroffer drafting & sign-off (~90/quarter; ~30 min/case): drafting the response to procurement, named-lawyer sign-off, sending out

---

## Your task
Produce a Delegation Suitability Matrix. Output file: `deliverables\D2_delegation_suitability_matrix.md`.

This is Phase 3 of the ATX Assessment. Score each major task cluster on delegation suitability dimensions, assign delegation archetypes with rationale, and determine the overall delegation architecture.

Reference: `input\1-ATX-Assessment.md` Phase 3.

---

## Required structure

### 1. Task cluster definition
Before scoring, define the task clusters you will score. These may be the JtDs from D1 or aggregated micro-task groups. List each cluster with a one-sentence description and which work stream it belongs to. Aim for 6–10 clusters total across all four work streams.

### 2. Delegation Suitability Matrix

One table covering all task clusters:

| Task Cluster | Work Stream | Input Structure (H/M/L) | Decision Determinism (H/M/L) | Tool Coverage (H/M/L) | Context Complexity (H/M/L) | Exception Rate (H/M/L) | Latency Constraint (H/M/L) | Risk/Compliance (H/M/L) | Suitability Score | Delegation Archetype |
|-------------|-------------|------------------------|------------------------------|----------------------|---------------------------|------------------------|---------------------------|------------------------|-------------------|----------------------|

**Suitability score**: count the number of dimensions at High suitability (for input structure, decision determinism, tool coverage — higher = better; for context complexity, exception rate, latency constraint, risk/compliance — lower = better). Express as a score out of 7.

**Scoring notes:** Below the table, add a brief justification (2–4 sentences) for each cluster's archetype assignment. Do not assert; justify.

### 3. Delegation archetype assignment with rationale

For each task cluster, state its archetype and defend it. Use this format:

> **Cluster [C-N] — [name]**
> **Archetype:** [Human Only / Human-led + Automation Support / Human-led + Agent Support / Agent-led + Human Oversight / Fully Agentic]
> **Rationale:** [cite the specific dimensions that drove this assignment — at least 2 dimensions with their scores]
> **GC rule impact (if applicable):** [does the GC's sign-off requirement change the archetype? If so, how?]
> **Anti-pattern check:** [could this be solved with static rules, RPA, or a simple script? If yes, do not assign an agentic archetype]

### 4. Delegation architecture summary

After completing all cluster assignments, step back and describe the overall delegation architecture as a system:

- Which clusters form the **autonomous backbone** (fully agentic or agent-led with oversight)?
- Which clusters are the **human-anchored gates** that the agent cannot cross without approval?
- Which clusters are **not worth automating** and why?
- Where is the GC's hard rule enforced in the architecture? Name the exact cluster(s) and archetype(s) that implement it.

Write this as a coherent 3–5 paragraph narrative, not as a list.

### 5. Delegation boundary defence

Pick the 2 most debatable archetype assignments (where a reasonable person might argue for a different archetype). For each:

> **Contested assignment:** [cluster name] — assigned [archetype]
> **The counter-argument:** [why someone might assign a more or less autonomous archetype]
> **Why the assigned archetype is correct for this scenario:** [specific reasoning tied to scenario facts]
> **What would change the assignment:** [conditions under which you would revise it]

---

## Acceptance criteria (all must pass)

- [ ] All four work streams represented in the matrix
- [ ] At least 6 task clusters scored
- [ ] Every archetype assignment has a written rationale citing at least 2 dimensions
- [ ] GC hard rule (sign-off on specific clauses) is explicitly reflected in the architecture
- [ ] Anti-pattern check performed for every cluster (no agent assigned to purely deterministic work)
- [ ] Delegation architecture summary describes the system as a whole, not just each cluster independently
- [ ] Two contested assignments defended in the format specified
- [ ] Suitability scores consistent with archetype assignments (a cluster with suitability score 2/7 should not be "fully agentic")

## Fail signals — do not produce output that contains these

- Assigning "agent-led" archetype to work requiring senior-lawyer judgment without explaining how the GC rule is satisfied
- All clusters assigned the same archetype (that means you haven't differentiated)
- Anti-pattern check missing — if you can't confirm "this is not solvable by a script," you haven't done the analysis
- Rationale that says "this is complex, therefore human-only" without naming which specific suitability dimensions are Low
- Architecture summary that is just a list of archetypes restated, not a description of how they work together
