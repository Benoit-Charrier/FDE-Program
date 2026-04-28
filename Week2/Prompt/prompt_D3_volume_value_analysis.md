# Prompt: Deliverable 3 — Volume × Value Analysis

## Scenario (read this first)
See `scenario\enriched_scenario.md`. Do not invent numbers, systems, or constraints not present there. Every number you use must trace back to the scenario or be explicitly labelled as an assumption.

**Scenario summary (for reference):**
- **Helix Workforce Software** — UK-based B2B SaaS (~480 employees, ARR £42M, 25% YoY growth); sells workforce-planning software to UK/EU enterprises
- Legal team (5-person): **Amelia Forsythe** (General Counsel, 12 years at Helix), 3 Commercial Lawyers (3–6 yrs experience), **Tom** (Paralegal)
- ~300 inbound vendor contracts per quarter; each 15–40 pages
- Playbook checklist: 7 clause types; playbook is 9 months stale — DPDI Act Q1 updates not yet incorporated
- 70% standard / 20% negotiable deviations / 10% senior-lawyer escalation
- Turnaround: 4–6 business days; CRO is pressuring Legal to halve turnaround to support enterprise sales targets
- GC hard rule: no counteroffer without named lawyer's sign-off on the specific clauses being negotiated
- Tooling: **Ironclad** (CLM, REST APIs), **Microsoft Word + Track Changes** + **SharePoint** (redlining & storage), **Salesforce** (sales pipeline), **Outlook** (vendor procurement), internal SharePoint playbook page

**The four work streams:**
1. First-pass clause classification (~300/quarter; ~25 min/case): triaging inbound contracts, classifying each major clause against the playbook
2. Standard-deviation redlining (~60/quarter; ~45 min/case): paralegal redlines negotiable deviations against playbook without escalation
3. Escalated clause review (~30/quarter; ~90 min/case): senior lawyer reviews unusual clauses, frames counteroffer position, drafts redline
4. Counteroffer drafting & sign-off (~90/quarter; ~30 min/case): drafting the response to procurement, named-lawyer sign-off, sending out

---

## Your task
Produce a Volume × Value Analysis. Output file: `deliverables\D3_volume_value_analysis.md`.

This is Phase 4 of the ATX Assessment. Plot all 4 work streams, identify where an agent creates value versus where it creates risk, identify the primary agentic target, and justify why it wins.

Reference: `input\1-ATX-Assessment.md` Phase 4 and `references\atx-scoring.md`.

---

## Required structure

### 1. Volume derivation
Before scoring, derive the per-work-stream volume from the scenario numbers. Show your arithmetic.

- 300 contracts/quarter → approximately how many per week?
- The enriched scenario gives per-work-stream volumes directly: first-pass ~300/quarter, redlining ~60/quarter, escalated review ~30/quarter, counteroffer drafting ~90/quarter. Cross-check these against the 70/20/10 split.
- For each work stream, how many "cases" per week does it handle?
- Flag any volume figures that require assumptions beyond what the scenario states, with explicit labelling.

### 2. Non-determinism scoring
For each work stream, score non-deterministic decision effort (1–5 scale from `references\atx-scoring.md`):

| Work Stream | Volume Score (1–5) | Non-Determinism Score (1–5) | Agentic Value Score (product) | Quadrant |
|-------------|-------------------|-----------------------------|-------------------------------|---------|

Score definitions (from `references\atx-scoring.md`):
- **Volume:** 5 = hundreds/day; 4 = 50–200/day; 3 = 10–50/day; 2 = several/day; 1 = weekly/monthly
- **Non-determinism:** 5 = synthesis + policy interpretation + contextual judgment; 4 = patterns + contextual adaptation + exception handling; 3 = rule-based core + exceptions needing reasoning; 2 = mostly deterministic; 1 = fully deterministic

Justify each score in a note below the table. Do not assert — cite the specific nature of the work.

### 3. Volume × Value grid (text representation)

Draw the 2×2 grid using ASCII text. Label each quadrant:
- Top-right: **Primary agentic targets** (high volume, high non-determinism)
- Top-left: **Rules / RPA, not agents** (high volume, low non-determinism)
- Bottom-right: **Select agentic use cases** (low volume, high non-determinism)
- Bottom-left: **Not worth automating**

Place each work stream in the appropriate quadrant. If two work streams fall in the same quadrant, note that explicitly.

```
High Non-Determinism |                    |                    |
(score 4-5)          |   [BOTTOM-RIGHT]   |   [TOP-RIGHT]      |
                     |                    |                    |
---------------------|--------------------|--------------------|
Low Non-Determinism  |                    |                    |
(score 1-2)          |   [BOTTOM-LEFT]    |   [TOP-LEFT]       |
                     |                    |                    |
                     |  Low Volume (1-2)  |  High Volume (3-5) |
```

### 4. Where an agent creates value — and where it creates risk
For each work stream, one paragraph:

> **Work Stream [N]: [name]**
> **Value created by agent:** [what would an agent accomplish that a human cannot do as efficiently?]
> **Risk created by agent:** [what could go wrong specifically in this work stream, and why?]
> **Net assessment:** [value > risk / risk > value / conditional on X]

The GC's hard rule must appear in the risk assessment of at least one work stream.

### 5. Suitability gate check
Run the suitability gate from `references\atx-scoring.md` on the top 2 agentic candidates (by Agentic Value Score):

| Factor | Work Stream A | Work Stream B |
|--------|--------------|--------------|
| Input Structure | H/M/L | H/M/L |
| Decision Determinism | H/M/L | H/M/L |
| Tool Coverage | H/M/L | H/M/L |
| Exception Rate | H/M/L | H/M/L |
| Compliance Risk | H/M/L | H/M/L |
| Gate Result | Pass / Conditional / Fail | Pass / Conditional / Fail |

### 6. Primary agentic target — selection and justification
Name the single work stream that is the primary agentic target. Justify in 4–6 sentences:
- Why this work stream wins on the Volume × Value grid
- Why it passes the suitability gate
- What specific business pain it addresses (tie to scenario numbers)
- What the feasibility case is (data availability, integration path, compliance manageability)
- What the single biggest risk to agentic success is in this work stream

### 7. Preliminary TCO sense-check
Using the scenario's numbers, run a high-level TCO estimate for the primary agentic target only. Show your arithmetic:

```
Baseline cost per case:
  Time per case: [from scenario]
  Assumption: fully loaded hourly cost = [£/$/€ — label as assumption]
  Baseline cost per case = [calculated]
  Cases per year = [derived from scenario]
  Annual baseline = [calculated]

Agent cost estimate:
  Estimated tokens per case: [estimate with rationale]
  Model: [name your assumption]
  Estimated token cost per case: [calculated]
  Estimated HITL rate: [% — tie to scenario's 20% or 10% escalation rates]
  HITL cost per case: [calculated]
  Estimated agent cost per case: [sum]
  Annual agent cost: [calculated]

Annual saving: [baseline - agent cost]
Estimated build cost: [label as assumption]
Payback period: [calculated]
```

All figures not in the scenario must be labelled as assumptions. The goal is directional — does the economics likely close?

---

## Acceptance criteria (all must pass)

- [ ] All 4 work streams appear on the grid
- [ ] Volume derivation shows arithmetic traced to scenario numbers
- [ ] Scores justified — not asserted
- [ ] Suitability gate run on the top 2 candidates
- [ ] Primary target named and justified with scenario-grounded reasoning
- [ ] Risk analysis present for every work stream (not just the primary target)
- [ ] GC hard rule reflected in risk analysis
- [ ] TCO sense-check present with all assumptions labelled
- [ ] Non-determinism scores differentiate the work streams (at least a 2-point range across all 4)

## Fail signals — do not produce output that contains these

- All four work streams in the same quadrant (that means the analysis didn't differentiate)
- Primary target selected based on intuition without Volume × Value evidence
- TCO estimate with no arithmetic shown
- Risk analysis that says "agents can make mistakes" without naming the specific mistake type and consequence in this scenario
- Volume numbers with no trace to the scenario's 300 contracts/quarter figure
