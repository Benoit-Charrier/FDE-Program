# Prompt: D0 — Generate Scenario Context

## Purpose of this step

This is the first step in the ATX assessment workflow. Before any deliverable (D0A through D7) can be produced, you must generate `scenario\scenario_context.md` — a structured, single-source-of-truth summary of the scenario.

Every subsequent prompt references this file instead of embedding the scenario. The goal is to generate it once and reuse it across all deliverables. Any change to the scenario (e.g., enriched artefacts, corrections) only needs to be made here.

**Read `scenario\scenario.md` (and `scenario\enriched_scenario.md` if it exists) as your source material.** Do not invent numbers, systems, or constraints not present in those files. Every number must trace back to the source or be explicitly labelled as an assumption.

---

## Your task

Generate `scenario\scenario_context.md`. This file will be read at the start of every subsequent prompt. It must be accurate, complete, and structured so that any prompt template can extract the facts it needs without reading the full scenario file.

---

## Required structure

### 1. File header

One-line title naming the company and process domain. One italicised line pointing back to the source files, e.g.:

> *Full artefacts and background in `scenario\enriched_scenario.md`. This file is the single-source-of-truth scenario summary for use across all prompt templates.*

---

### 2. The company

One paragraph. Include:
- Full company name (bold)
- Size (headcount, revenue/ARR if stated, growth rate if stated)
- Business model and what it sells
- Market/customer segment
- Geography or offices if stated

---

### 3. The team

The team that owns the process being assessed. Include:
- Team name and headcount
- Each named individual: name (bold), role, years at company or experience level
- Generic roles and their count if named individuals are not given for all

---

### 4. The process

The core process under assessment. Include:
- What the process handles (volume, cadence, typical unit size)
- Any policy or compliance document that governs it (name it, state its current status — is it stale, under revision?)
- Triage or routing logic (percentage splits, who handles each tier)
- Turnaround targets and any stated performance pressure
- Any hard rules or non-negotiable constraints (name who owns each rule)

---

### 5. The work streams

A markdown table with one row per work stream:

| # | Work stream | Volume/quarter | Time/case |
|---|-------------|----------------|-----------|

Followed by a bullet list: `**WS[N]:**` and one sentence describing what the work stream involves.

---

### 6. Tooling

A bullet list of every system named in the scenario with a brief role description in parentheses.

Then this note, worded precisely:

> **Named systems note:** [List every system named in the scenario here] are confirmed in the scenario — treat them as facts, not assumptions. Any additional system you introduce must be labelled as an assumption. Specific API capabilities, rate limits, and integration maturity beyond what is stated in the scenario are still assumptions and must be labelled as such.

If no systems are named in the scenario, write: "No systems are explicitly named in the scenario. All tooling references in subsequent deliverables are assumptions and must be labelled as such."

---

### 7. Key artefacts

*Include this section only if the scenario contains sample artefacts, excerpts, emails, or annotated documents that reveal how the process actually works in practice.*

For each artefact, one bullet:
- `**Artefact [N] — [descriptive title]:**` followed by a 2–3 sentence summary of what the artefact shows. Focus on what it reveals about the **lived process** versus the documented SOP — workarounds, informal decisions, compliance gaps, or constraints not captured in the formal process description.

If no artefacts are present, omit this section entirely.

---

### 8. Assumption log
Use this format for every non-trivial claim:

> **Assumption [A1]:** [what you're taking as given]
> **Why it matters:** [what spec decision or metric it drives]
> **If wrong:** [what breaks]
> **Confidence:** low / medium / high

Minimum 2 assumptions in this section. More is better.

----
## Quality requirements

- Every number in the file must be directly quoted from or traceable to the source scenario files
- If a scenario fact is ambiguous or could be interpreted multiple ways, state the most conservative reading and label it as an interpretation
- Do not introduce additional context, examples, or elaborations beyond what is in the source material
- Named individuals should be quoted exactly as written in the scenario (spelling, title)
- The file must be self-contained: a reader who has not read the original scenario should be able to answer any factual question about the company, team, process, work streams, and tooling from this file alone

---


## Acceptance criteria

- [ ] File header present with pointer to source files
- [ ] Company section complete (name, size, model, market)
- [ ] Team section lists every named individual with role and tenure/experience
- [ ] Process section captures volume, policy status, triage split, turnaround, and all hard rules
- [ ] Work streams table present with volume and time/case for every work stream stated in the scenario
- [ ] Tooling section present with named-systems note
- [ ] Named systems note distinguishes confirmed-in-scenario systems from anything additional
- [ ] Artefacts section present if and only if the scenario contains sample artefacts
- [ ] No invented numbers, systems, or constraints

## Fail signals — do not produce output that contains these

- Numbers not traceable to the source scenario (e.g., computed averages presented as scenario facts)
- Systems listed as confirmed that are not explicitly named in the scenario source files
- Named-systems note absent or omitted
- Artefacts section present but summarising artefacts that don't exist in the source
- Work streams table missing time/case or volume for any work stream that the scenario provides
- Hard rules stated without naming who owns them
