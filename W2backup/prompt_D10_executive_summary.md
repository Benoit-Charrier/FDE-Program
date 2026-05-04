# Prompt: Executive Summary — ATX Assessment Synthesis

## Inputs (read these first, in order)
The following deliverables are your only sources. Do not re-read the scenario or invent new analysis. Synthesise what is already there.

| Deliverable | What to extract |
|-------------|----------------|
| `deliverables\D0B_discovery.md` | Points of Pain inventory |
| `deliverables\D1_cognitive_load_map.md` | Cognitive Load Map — top micro-tasks and hotspots |
| `deliverables\D2_delegation_suitability_matrix.md` | Delegation Suitability Matrix — archetype assignments and scores |
| `deliverables\D3_volume_value_analysis.md` | Volume × Value grid and primary agentic candidate |
| `deliverables\D4_agent_purpose_document.md` | Prioritised candidate — agent identity, objectives, KPIs |
| `deliverables\D6_discovery_questions.md` | Top 5 questions that would change the design |

---

## Your task
Produce a concise executive summary of the ATX assessment. This document is for a senior business stakeholder — not a developer. No implementation detail, no methodology explanation. Only findings, what they mean, and what needs to be resolved before building.

Output file: `deliverables\executive_summary.md`

Be concise.

---

## Required structure

### 0. Executive summary
Three bullet points, written first. Each bullet is one sentence. Draw only from the six input deliverables — no new analysis. Cover in order:
1. The primary agentic recommendation — what to build, what business pain it eliminates, and the headline economic case (tie to a number from D3)
2. The most consequential delegation boundary — which task cluster is the hardest governance call and what the design does to enforce it
3. The single biggest open question before build can start — what is unresolved, what it risks if it stays unresolved, and which of the five design-impact questions from D6 it maps to

This section must be self-contained — a senior stakeholder who reads only this section should know what is recommended, where the governance line is drawn, and what must be confirmed before committing to build.

### 0b. Table of contents
List all sections by number and title, in order. Generate this after the full document is written — section titles must match exactly.

### 1. Points of Pain

Draw from D0B. Present as a condensed table — one row per work stream, maximum two rows for cross-cutting pain. Drop the discovery-process scaffolding; keep only findings.

| Work Stream | Core Pain | Volume | Pain Level | Automation Candidate? |
|-------------|-----------|--------|------------|----------------------|

Below the table: one sentence per H-rated pain explaining the business consequence of leaving it unaddressed.

---

### 2. Cognitive Load Map — where skilled attention is consumed

Draw from D1. Do not reproduce the full micro-task table. Present the top 3–4 hotspots only — the moments where the most skilled human attention is consumed and where the gap between documented and lived process is largest.

Format for each hotspot:

> **[Work stream] — [specific moment]**
> What the human does: [decision / synthesis / judgment — one line]
> Why it matters for agent design: [what this means for how the agent must be scoped or constrained — one line]

---

### 3. Delegation Suitability Matrix — what can be delegated and what cannot

Draw from D2. Present as a summary table — one row per task cluster, archetype assignment, and one-word rationale. Do not reproduce suitability scores.

| Task Cluster | Delegation Archetype | Key reason |
|--------------|---------------------|-----------|

Below the table: call out the one or two clusters where the archetype assignment is most consequential — where getting it wrong would produce either an over-automated agent (autonomy where judgment is needed) or an under-automated design (HITL where none is needed). Explain the consequence in one sentence each.

---

### 4. Volume × Value Grid

Draw from D3. Reproduce the Mermaid quadrantChart exactly as it appears in D3 — do not recalculate or redraw it.

Below the chart: a two-sentence interpretation — which work stream is the primary agentic target and why it wins the quadrant analysis over the alternatives.

---

### 5. Prioritised Candidate Shortlist

Draw from D3 (TCO sense-check) and D4 (agent identity and KPIs). Present as a ranked table.

| Rank | Candidate | Agentic Value Score | Payback Period | Primary blocker before build |
|------|-----------|--------------------|-----------------|-----------------------------|

For the top candidate only, add a three-sentence business case:
- What pain it eliminates (tie to a scenario number)
- What the economic case is (payback period from D3 TCO, labelled as an estimate)
- What the primary governance or compliance constraint is and how the design addresses it

---

### 6. Five questions that would change the design

Draw from D6. Select the 5 questions with the highest design impact — the ones where different answers would produce materially different architectures, autonomy levels, or deployment gates. Do not include the full design-fork text from D6. Condense each to two lines.

| # | Question | If unresolved, this blocks or risks: |
|---|----------|--------------------------------------|
| 1 | | |
| 2 | | |
| 3 | | |
| 4 | | |
| 5 | | |

---

## Acceptance criteria (all must pass)

- [ ] All six sections present
- [ ] No new analysis introduced — every claim traces to one of the six input deliverables
- [ ] Points of Pain table covers every work stream from D0B
- [ ] Cognitive Load hotspots are drawn from D1, not re-inferred from the scenario
- [ ] Delegation archetype table matches D2's assignments — no silent upgrades or downgrades
- [ ] Volume × Value chart is reproduced from D3, not redrawn
- [ ] Prioritised candidate shortlist ranks are consistent with D3's Agentic Value Scores
- [ ] Five questions are drawn from D6 and selected on design-impact, not question number
- [ ] The primary governance or compliance constraint appears in both §5 (business case) and §6 (questions)
- [ ] Total length: fits on 2–3 pages; this is a briefing document, not a report

## Fail signals — do not produce output that contains these

- New analysis not present in D1–D6 (the executive summary synthesises; it does not discover)
- Delegation archetypes that differ from D2 without noting the discrepancy
- A Volume × Value chart that differs from D3's chart
- Questions in §6 that are generic ("What is your timeline?") rather than drawn from D6's design-fork analysis
- A business case in §5 that omits the governance or compliance constraint
- Section length that reproduces the source deliverable rather than condensing it
