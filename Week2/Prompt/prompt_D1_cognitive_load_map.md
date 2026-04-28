# Prompt: Deliverable 1 — Cognitive Load Map

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
Produce a Cognitive Load Map. Output file: `deliverables\D1_cognitive_load_map.md`.

This is Phase 2 of the ATX Assessment. Decompose **at least 2 of the 4 work streams** into Jobs to be Done, micro-tasks, and cognitive dimensions. Map cognitive zones and breakpoints.

Reference: `input\1-ATX-Assessment.md` Phase 2 and `references\atx-concepts.md`.

Choose the 2 work streams with the highest delegation potential AND the highest cognitive complexity. Justify your selection before proceeding.

---

## Required structure

### 1. Work stream selection and rationale
Name the 2 work streams you will decompose. In 3–5 sentences, explain why these two — not the others — offer the most insight for agent design. Your reasoning must reference delegation potential and cognitive complexity, not just "they seem important."

### 2. Cognitive Load Map — Work Stream A

#### 2a. Jobs to be Done decomposition
List 2–4 JtDs for this work stream. For each:

> **JtD [WS-A-N]:** [the cognitive contract — what outcome must be produced?]
> **Trigger:** [what starts this job?]
> **Actor:** [who currently does this?]
> **Key decisions:** [what must be decided to complete it?]
> **Key systems/data:** [what information is required?]
> **Primary cognitive type:** decision-making / execution / synthesis / communication / exception-handling
> **Expected output:** [what is produced?]

#### 2b. Micro-task inventory with dimension scores
For each micro-task within this work stream, complete the following table:

| Micro-task | Cognitive Load (H/M/L) | Input Structure (H/M/L) | Decision Determinism (H/M/L) | Exception Frequency (H/M/L) | Turn-Taking Degree (H/M/L) | Latency Constraint (H/M/L) | Compliance/Risk Sensitivity (H/M/L) | Tool/API Availability (H/M/L) |
|------------|------------------------|-------------------------|------------------------------|------------------------------|---------------------------|---------------------------|--------------------------------------|-------------------------------|

Include at least 5 micro-tasks per work stream. Scores must be justified in footnotes — not asserted.

#### 2c. Cognitive zones and breakpoints
Map this work stream as a sequence of cognitive zones. For each zone:

> **Zone [Z-N]:** [zone name, e.g. "Intent classification", "Data retrieval", "Deviation judgment"]
> **Micro-tasks in zone:** [list]
> **Dominant cognitive type:** [probabilistic reasoning / deterministic execution / human sense-making]
> **Data dependencies:** [what must be available?]
> **Error tolerance:** [what is the cost of a mistake in this zone?]

Then identify breakpoints — moments where control must or should shift:

> **Breakpoint [BP-N]:** [description of the handoff]
> **From:** [who/what currently controls]
> **To:** [who/what should control after the breakpoint]
> **Why this is a breakpoint:** [rule-to-judgment shift? human-to-system? compliance gate?]
> **Agent opportunity or risk:** [does an agent create value or risk here?]

#### 2d. Process topology diagram (text)
Draw a linear or branching flow showing zones → breakpoints → zones. Use ASCII or structured text. Label each zone and breakpoint with its ID.

### 3. Cognitive Load Map — Work Stream B
Repeat sections 2a through 2d for the second work stream.

### 4. Cross-work-stream observations
After completing both maps, write 3–5 observations that apply across both. Focus on:
- Shared breakpoints that suggest reusable agent components
- Shared data sources that suggest shared context/retrieval design
- Patterns in where exception handling consumes disproportionate time

---

## Acceptance criteria (all must pass)

- [ ] Work stream selection is justified, not assumed
- [ ] At least 2 work streams fully decomposed
- [ ] JtDs are cognitive contracts (outcome-focused), not task descriptions
- [ ] Micro-task tables have at least 5 rows per work stream with justified scores
- [ ] Cognitive zones are distinguished by dominant cognitive type (probabilistic / deterministic / human sense-making)
- [ ] At least 3 breakpoints identified per work stream, with agent opportunity/risk noted
- [ ] Process topology diagram present for each work stream
- [ ] GC hard rule reflected in at least one breakpoint (sign-off gate)
- [ ] No scores without justification in footnotes

## Fail signals — do not produce output that contains these

- Micro-task tables with all scores "H" or all "M" — that is not analysis
- Breakpoints described as "the human reviews the agent output" without specifying the condition that triggers the review
- JtDs that are tasks ("extract clause text") rather than cognitive contracts ("determine whether this liability cap is compliant with the playbook and what the business exposure is if it is not")
- Zone definitions that group all work together as "review" — zones should separate qualitatively different cognitive activity
