# Prompt: Stakeholder Presentation Deck

**Generic template — synthesises D1–D6 into a stakeholder-facing slide deck.**

---

## Scenario (read this first)
See `scenario\scenario_context.md` for the full scenario, work streams, tooling, and named-systems guidance. Do not invent numbers, systems, or constraints not present in the scenario or the deliverables. Every claim must trace back to a deliverable.

---

## Purpose

This prompt produces a stakeholder presentation deck that communicates assessment findings, the proposed agent solution, open questions requiring stakeholder input, and next steps — in language a senior business stakeholder can act on without reading the full ATX deliverables.

**Audience:** The primary stakeholder identified in `scenario_context.md` and their immediate team. Not a technical audience. They care about: business outcomes, risk, what changes for their team, and what decisions they need to make.

**Tone:** Direct, evidence-based, no jargon. Each slide earns its place. If a slide cannot be summarised in one sentence, it is doing too much.

**Input deliverables to read before writing:**
- `Deliverables/D1_cognitive_load_map.md` — where the cognitive work lives today
- `Deliverables/D2_delegation_suitability_matrix.md` — what can and cannot be delegated
- `Deliverables/D3_volume_value_analysis.md` — the business case and primary target
- `Deliverables/D4_agent_purpose_document.md` — what the agent does and where it stops
- `Deliverables/D5_system_data_inventory.md` — integration readiness
- `Deliverables/D6_discovery_questions.md` — open questions that require stakeholder input

**Output file:** `Deliverables/Stakeholder_Presentation.md`

---

## Your task

Produce a structured slide deck in markdown. Each slide is a clearly delimited section. Include speaker notes for every slide — one paragraph, written as what the presenter would say, not a repeat of the slide content. The deck must stand alone: a reader who has not seen the deliverables should be able to follow the argument from problem to recommendation to next steps.

Do not produce a summary of the deliverables. Produce a narrative arc: here is the problem, here is what we found, here is what we recommend, here are the decisions we need from you.

---

## Required structure

Use this format for every slide:

```
---
## Slide [N]: [Title]
**Type:** [Title / Section divider / Content / Discussion / Closing]

[Slide content — bullet points, table, or diagram as appropriate. Maximum 5 bullets per content slide. No full sentences in bullets — headline style only.]

**Speaker notes:**
[One paragraph. What the presenter says to bring the slide to life — context, emphasis, the one thing the audience must take away. Written in first person.]
```

---

### Slide sequence

Produce exactly the following slides in order:

**Section 1 — Opening**

**Slide 1: Title**
Company name, process domain, meeting purpose ("Assessment Findings & Proposed Solution"), date placeholder, presenter name placeholder.

**Slide 2: Agenda**
Five agenda items matching the five sections of this deck. One line each.

**Slide 3: Why we are here — the business problem**
The core operational problem in two or three bullets. Tie every bullet to a number from `scenario_context.md` or `D3`. No generic statements. End with the one question this assessment set out to answer.

---

**Section 2 — What we found**

**Slide 4: How the work actually flows today**
A simplified process flow showing the main work streams, volumes, and time-per-case from `D1` and `scenario_context.md`. Use a text-based flow (→ arrows) if a diagram is needed — no Mermaid on this slide (not all presentation tools render it). Highlight where the most cognitive load sits.

**Slide 5: Where time goes — the cognitive hotspots**
Two or three hotspots from `D1`. For each: the moment, why it consumes skilled attention, and whether it is automatable. Frame for a business audience: not "non-deterministic reasoning" but "judgment calls that vary case by case."

**Slide 6: What can be delegated to an agent — and what cannot**
A simple two-column view: agent-suitable vs. human-anchored, drawn from `D2`'s delegation architecture summary. Include the primary governance constraint as a named non-negotiable in the human-anchored column. One sentence of rationale per row. Maximum 6 rows.

**Slide 7: The opportunity — where volume meets complexity**
The Volume × Value quadrant from `D3`. Label each work stream. Identify the primary agentic target. State its Agentic Value Score and what it means in plain language. Include the TCO directional finding (payback period or annual saving estimate) as a single callout.

---

**Section 3 — What we recommend**

**Slide 8: The proposed agent — what it does**
Three to four bullets describing the agent's Job to be Done, drawn from `D4` section 1 and section 2. Plain language — no technical architecture. What does it replace? What does it produce? Who benefits?

**Slide 9: Where the agent stops — the autonomy boundary**
A three-row table: Agent decides alone / Agent proposes, human approves / Human only. Drawn directly from `D4`'s autonomy matrix. The primary governance constraint must appear explicitly in the "human approves" row with its exact condition. This slide must make clear that the hard rule is enforced by design, not by policy.

**Slide 10: Integration readiness**
A three-item summary from `D5`: (1) the most critical integration and its status, (2) the biggest gap and what it means for the timeline, (3) the one confirmation needed before build can start. Frame as "green / amber / red" readiness per item if evidence supports it — do not invent a RAG status not supported by `D5`.

---

**Section 4 — Questions we need your input on**

**Slide 11: What we need from you — top questions**
The five most design-critical questions from `D6`, reformatted for a stakeholder audience. For each question: one line for the question, one line for why the answer changes the design. No category labels, no design-fork format — plain conversational questions a GC or COO would recognise as meaningful. Do not include questions already answered by the scenario.

**Slide 12: Discussion**
Type: Discussion. One open prompt per agenda item that surfaced an unresolved tension. Invite the stakeholder to react. Maximum three prompts.

---

**Section 5 — Next steps**

**Slide 13: Next steps**
A four-row table: Action / Owner / Dependency / Target date (placeholder). Actions must be concrete — not "continue the assessment" but "confirm Ironclad API access" or "validate the triage split against Q1 actuals." Drawn from `D5` gaps and `D6` questions. Owner should be either "FDE team" or the stakeholder's role — no invented names.

**Slide 14: Closing**
One-sentence summary of the recommendation. Contact / next meeting placeholder.

---

## Acceptance criteria (all must pass)

- [ ] Every factual claim traces to a named deliverable or `scenario_context.md` — no invented numbers or findings
- [ ] Speaker notes present for every slide and add context not visible on the slide
- [ ] Slide 6 (delegation) includes the primary governance constraint as a named non-negotiable
- [ ] Slide 9 (autonomy boundary) places the governance constraint in the "human approves" tier explicitly
- [ ] Slide 11 (questions) contains only questions not already answered by the scenario
- [ ] Slide 13 (next steps) actions are specific and traceable to `D5` or `D6`
- [ ] No jargon: "non-deterministic," "cognitive zone," "delegation archetype," "ATX" must not appear in any slide content (speaker notes may use them if needed for presenter context)
- [ ] Deck tells a complete narrative arc: problem → finding → recommendation → decision needed → next step
- [ ] Total slide count: exactly 14

## Fail signals — do not produce output that contains these

- Slides that summarise a deliverable section by section rather than building a narrative
- Speaker notes that repeat the slide bullets verbatim
- Volume or time figures not traceable to the scenario or deliverables
- A governance constraint presented as "best practice" rather than a named rule from the scenario
- Next steps that are vague ("explore options", "gather more information")
- Questions on slide 11 that the stakeholder could answer by reading `scenario_context.md` — they already know their own process
- Generic AI-risk language ("the agent might make mistakes") without naming the specific failure mode from `D4`
