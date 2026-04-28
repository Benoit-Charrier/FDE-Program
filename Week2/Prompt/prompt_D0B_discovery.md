# Prompt: Deliverable 0B — Discovery

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

**The four work streams in this process:**
1. First-pass clause classification (~300/quarter; ~25 min/case): triaging inbound contracts, classifying each major clause against the playbook
2. Standard-deviation redlining (~60/quarter; ~45 min/case): paralegal redlines negotiable deviations against playbook without escalation
3. Escalated clause review (~30/quarter; ~90 min/case): senior lawyer reviews unusual clauses, frames counteroffer position, drafts redline
4. Counteroffer drafting & sign-off (~90/quarter; ~30 min/case): drafting the response to procurement, named-lawyer sign-off, sending out

---

## Your task
Produce a Discovery document. Output file: `deliverables\D0B_discovery.md`.

This is Phase 1 of the ATX Assessment. The goal is to assess the process as it is **actually lived**, not as it is documented. Surface the cognitive workloads that consume the most skilled human time and carry the most operational friction.

Reference: `input\1-ATX-Assessment.md` Phase 1.

---

## Required structure

### 1. Lived process narrative
One to two pages. Walk through a realistic contract review cycle from the moment a vendor contract lands to the moment a counteroffer (or approval) leaves legal's queue. Describe **what actually happens**, not the idealised SOP.

- Where does the reviewer pause and consult something?
- Where do they make a judgment call?
- Where does back-and-forth happen (internally or externally)?
- Where do queues form?
- What informal knowledge is being applied?

Flag explicitly where you are reconstructing from the scenario versus where you are making a labelled assumption.

### 2. Points of Pain inventory
A structured table listing candidate processes with the following columns:

| Work Stream | Pain Description | Estimated Volume | Pain Level (H/M/L) | Key Data/Systems Involved | Candidate for Automation? |
|-------------|-----------------|------------------|--------------------|--------------------------|--------------------------|

Include at least one row for each of the four work streams listed above. Pain level must be justified in a note below the table, not asserted.

### 3. Cognitive workload hotspots
For each of the four work streams, identify the top 1–2 moments where skilled human attention is most consumed. Format:

> **Hotspot [WS-X-N]:** [work stream] — [specific moment]
> **What the human does:** [describe the cognitive act — decide, synthesise, interpret, judge?]
> **Why a machine can't trivially replace this today:** [specific reason]
> **Delegation signal:** [could this be structured enough for an agent? What would need to be true?]

### 4. Points of friction for procurement
One paragraph. Describe the downstream consequence of the 4–6 business day turnaround from procurement's perspective. This is the stakeholder pain that drives urgency. Tie to scenario facts.

### 5. Known unknowns
List at least 5 genuine unknowns — things you would need to discover in a real client engagement that are not answered by the scenario. Format:

> **Unknown [U-N]:** [what you don't know]
> **Why it matters for agent design:** [what decision it would change]
> **How to discover it:** [who to ask, what to look for]

---

## Acceptance criteria (all must pass)

- [ ] Lived process narrative describes actual work, not just the SOP-layer description from the scenario
- [ ] All four work streams appear in the Points of Pain table
- [ ] Pain levels are justified, not asserted
- [ ] Every number traces to the scenario or is labelled as an assumption
- [ ] At least 5 genuine unknowns in the format specified
- [ ] Hotspots include a delegation signal — not just "this is hard," but "here is what would make it delegatable"
- [ ] GC's hard rule (named-lawyer sign-off on specific clauses) is reflected in the analysis

## Fail signals — do not produce output that contains these

- SOP-level description masquerading as lived process
- Generic pain points not grounded in this specific scenario
- Fewer than 5 unknowns, or unknowns that are filler ("we don't know the exact number of clauses")
- Invented systems, tools, or org structures not in the scenario without labelling them as assumptions
- Confident claims about what the paralegal "always" does without flagging that this is an inference
