# Prompt: Deliverable D0D — Discovery (Generic Template)

## Scenario (read this first)
See `scenario\scenario_context.md` for the full scenario, work streams, tooling, and named-systems guidance. Do not invent numbers, systems, or constraints not present in the scenario. Every number you use must trace back to the scenario or be explicitly labelled as an assumption.

---

## Your task
Produce a Discovery document. Be concise. Output file: `deliverables\D0C_discovery.md`.

This is Phase 1 of the ATX Assessment. The goal is to assess the process as it is **actually lived**, not as it is documented. Surface the cognitive workloads that consume the most skilled human time and carry the most operational friction.

Reference: `input\1-ATX-Assessment.md` Phase 1 and `references\discovery-questioning-patterns.md`.

---

## Required structure

### 0. Executive summary
Three bullet points, written first. Each bullet is one sentence. Cover in order:
1. The primary cognitive workload finding — which work stream consumes the most skilled human time and why (tie to a number from the scenario)
2. The most critical lived-vs-documented gap — the most significant workaround or compliance friction the team is actually experiencing
3. The highest-signal delegation opportunity — which work stream shows the strongest case for agent intervention and what makes it delegatable

This section must be self-contained — a reader who reads only this section should understand where the real work lives, what is broken, and where the agent opportunity is.

### 0b. Table of contents
List all sections by number and title as markdown anchor links, in order. Generate this after the full document is written — section titles must match exactly. Format each entry as `[N. Section title](#n-section-title)` using lowercase and hyphens for spaces.

Example format:
- [0. Executive summary](#0-executive-summary)
- [0b. Table of contents](#0b-table-of-contents)
- [1. Lived process narrative](#1-lived-process-narrative)

### 1. Lived process narrative
One to two pages. Walk through a realistic process cycle from the trigger event (how work arrives) to the final output (what leaves the team's queue), as described in scenario_context.md. Describe **what actually happens**, not the idealised SOP.

As you write, identify and flag:
- **Pause points** — where the worker stops to think, consult, or verify before proceeding
- **Judgment calls** — where the rule is complex, context-dependent, or exception-prone
- **Coordination work** — where someone is shepherding information across tools, people, or systems
- **Workarounds** — where the system doesn't match the real work and the human compensates manually
- **Async waits** — where someone is blocked on input from another person or system

Flag explicitly where you are reconstructing from the scenario versus where you are making a labelled assumption.

### 2. Points of Pain inventory
A structured table covering all work streams in scenario_context.md. Include at least one row per work stream and additional rows for cross-cutting pain that spans work streams.

| Work Stream | Pain Description | Volume (per week/month) | Pain Level (H/M/L) | Lived-vs-Documented Gap | Key Data/Systems Involved | Delegation Signal | Candidate for Automation? |
|-------------|-----------------|-------------------------|--------------------|------------------------|--------------------------|-------------------|--------------------------|

Pain level must be justified in a note below the table, not asserted. Every volume figure must trace to the scenario or be labelled as an assumption.

### 3. ATX discovery dimensions — assessment per work stream
For each work stream, assess across the five ATX dimensions. Draw evidence directly from scenario_context.md — do not invent.

| Work Stream | Volume & Time | Cognitive Nature | Data & Systems | Risk & Compliance | Organisational |
|-------------|--------------|-----------------|---------------|-------------------|---------------|

For each cell: one to two specific observations grounded in the scenario. Where the scenario is silent, write "Unknown — requires discovery."

### 4. Cognitive workload hotspots
For each work stream, identify the top 1–2 moments where skilled human attention is most consumed. Format:

> **Hotspot [WS-X-N]:** [work stream] — [specific moment]
> **What the human does:** [describe the cognitive act — decide, synthesise, interpret, judge]
> **Why a machine can't trivially replace this today:** [specific reason grounded in the scenario]
> **Delegation signal:** [codifiable? exception rate? what would need to be true for an agent to handle this?]

### 5. Known unknowns
List at least 5 genuine unknowns — things you would need to discover in a real client engagement that are not answered by the scenario. Format:

> **Unknown [U-N]:** [what you don't know]
> **Why it matters for agent design:** [what decision it would change]
> **How to discover it:** [who to ask, what to look for]

### 6. Assumption log
Use this format for every non-trivial claim not directly supported by the scenario:

> **Assumption [A-N]:** [what you're taking as given]
> **Why it matters:** [what spec decision or metric it drives]
> **If wrong:** [what breaks]
> **Confidence:** Low / Medium / High

Minimum 2 assumptions. More is better.

---

## Acceptance criteria (all must pass)

- [ ] Lived process narrative describes actual work, not just the SOP-layer description from the scenario
- [ ] Points of Pain table covers every work stream in scenario_context.md
- [ ] Pain levels are justified in a note below the table, not asserted
- [ ] Every number traces to the scenario or is labelled as an assumption
- [ ] ATX dimensions table includes at least one observation per cell grounded in the scenario; unknowns are marked explicitly
- [ ] Hotspots include a delegation signal — not just "this is hard," but "here is what would make it delegatable"
- [ ] At least 5 genuine unknowns in the format specified
- [ ] The primary governance or compliance constraint from scenario_context.md is reflected in the analysis
- [ ] At least one work stream identified where a static rule or RPA would suffice — and an agent is not warranted

## Fail signals — do not produce output that contains these

- SOP-level description masquerading as lived process
- Generic pain points not grounded in this specific scenario
- ATX dimension assessment with no scenario evidence cited ("unknown" is fine; generic assertion is not)
- Fewer than 5 unknowns, or unknowns that are filler ("we don't know the exact volume breakdown by sub-type")
- Invented systems, tools, or org structures not in the scenario without labelling them as assumptions
- Confident claims about what team members "always" do without flagging that this is an inference
- All work streams scored the same pain level
