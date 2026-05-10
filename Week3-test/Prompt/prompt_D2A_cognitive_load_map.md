# Prompt: Deliverable 1 — Cognitive Load Map

## Scenario (read this first)
See `scenario\scenario_context.md` for the full scenario, work streams, tooling, and named-systems guidance. Do not invent numbers, systems, or constraints not present in the scenario. Every number you use must trace back to the scenario or be explicitly labelled as an assumption.

---

## Your task
Produce a Cognitive Load Map. Be concise. Output file: `deliverables\D2A_cognitive_load_map.md`.

This is Phase 2 of the ATX Assessment. Following the Phase 2 step-by-step from `references\1-ATX-Assessment.md`:

- **Step 1:** Map the lived process — walk through a real case, capture triggers, inputs, intermediate decisions, outputs, escalations, and where the worker pauses, consults, or makes a judgment call. Produce a lived process narrative per work stream.
- **Step 2:** Decompose into Jobs to be Done.
- **Step 3:** Map Cognitive Zones and Breakpoints.
- **Step 4:** Build the micro-task inventory.

Reference: `references\1-ATX-Assessment.md` Phase 2 and `references\atx-concepts.md`.

Choose the 2 work streams with the highest delegation potential AND the highest cognitive complexity. Justify your selection before proceeding.

---

## Required structure

### 0. Executive summary
Three bullet points, written first. Each bullet is one sentence. Cover in order:
1. Which two work streams were selected for decomposition and the shared reason they surfaced as the highest-priority (tie to delegation potential and cognitive complexity)
2. The most significant breakpoint found across the two maps — the moment where agent value and human judgment tension is highest
3. The cross-work-stream pattern most consequential for agent design (shared data dependency, reusable component, or compliance gate that applies to both)

This section must be self-contained — a reader who reads only this section should understand which work was decomposed, where the critical handoff lives, and what the design implication is.

### 0b. Table of contents
List all sections by number and title as markdown anchor links, in order. Generate this after the full document is written — section titles must match exactly. Format each entry as `[N. Section title](#n-section-title)` using lowercase and hyphens for spaces. Include subsections indented under their parent.

Example format:
- [0. Executive summary](#0-executive-summary)
- [0b. Table of contents](#0b-table-of-contents)
- [1. Work stream selection and rationale](#1-work-stream-selection-and-rationale)
- [2. Cognitive Load Map — Work Stream A](#2-cognitive-load-map--work-stream-a)
  - [2a. Lived process narrative (Step 1)](#2a-lived-process-narrative-step-1)
  - [2b. Jobs to be Done decomposition](#2b-jobs-to-be-done-decomposition)
  - [2c. Cognitive zones and breakpoints](#2c-cognitive-zones-and-breakpoints)
  - [2d. Micro-task inventory with dimension scores](#2d-micro-task-inventory-with-dimension-scores)
  - [2e. Process topology diagram](#2e-process-topology-diagram)
- [3. Cognitive Load Map — Work Stream B](#3-cognitive-load-map--work-stream-b)
- [4. Cross-work-stream observations](#4-cross-work-stream-observations)
- [5. Assumption log](#5-assumption-log)

### 1. Work stream selection and rationale
Name the 2 work streams you will decompose. In 3–5 sentences, explain why these two — not the others — offer the most insight for agent design. Your reasoning must reference delegation potential and cognitive complexity, not just "they seem important."

### 2. Cognitive Load Map — Work Stream A

#### 2a. Lived process narrative (Step 1)
One page maximum. Walk through a realistic single case in this work stream from trigger to output — describe **what actually happens**, not the idealised SOP.

Cover:
- What triggers this work stream and how the work arrives
- Where the worker pauses and consults something (system, colleague, document)
- Where they make a judgment call and what information they use
- Where back-and-forth happens (internally or externally) and with whom
- Where queues form or informal workarounds occur
- What informal knowledge is being applied that is not in any system

Flag explicitly where you are reconstructing from the scenario versus making a labelled assumption. This narrative is the foundation for the JtD decomposition — do not skip it or replace it with a bullet list of steps.

#### 2b. Jobs to be Done decomposition (step 2)
List 2–4 JtDs for this work stream in the table below. JtDs are cognitive contracts — outcome-focused, not task descriptions.

| JtD ID | Cognitive contract - what outcome must be produced?] | Trigger - what starts this job? | Actor - who currently does this?| Key decisions - what must be decided to complete it?| Key systems/data - what information is required?| Primary cognitive type | Expected output - what is produced?|
|--------|----------------------------------------|---------|-------|---------------|-----------------|----------------------|-----------------|
| WS-A-1 | | | | | | decision-making / execution / synthesis / communication / exception-handling | |
| WS-A-2 | | | | | | | |


#### 2c. Cognitive zones and breakpoints (step 3)
**Zones** — map this work stream as a sequence of cognitive zones:

| Zone ID | Zone name | Micro-tasks in zone | Dominant cognitive type | Data dependencies | Error tolerance - what is the cost of a mistake in this zone?|
|---------|-----------|---------------------|------------------------|-------------------|-----------------|
| Z-1 | | | probabilistic reasoning / deterministic execution / human sense-making | | |
| Z-2 | | | | | |

**Breakpoints** — moments where control must or should shift (minimum 3 per work stream):

| BP ID | Description of handoff | From - who/what currently controls | To - who/what should control after the breakpoint | Why this is a breakpoint - rule-to-judgment shift? human-to-system? compliance gate?| Agent opportunity or risk - does an agent create value or risk here? |
|-------|------------------------|------|----|--------------------------|--------------------------|
| BP-1 | | | | rule-to-judgment shift / human-to-system / compliance gate | |
| BP-2 | | | | | |
| BP-3 | | | | | |

#### 2d. Micro-task inventory with dimension scores (step 4)
For each micro-task within this work stream, complete the following table:

| Micro-task | Cognitive Load (H/M/L) How much reasoning, tacit knowledge, or disambiguation required | Input Structure (H/M/L) Are inputs structured, semi-structured, or unstructured? | Decision Determinism (H/M/L) Are outcomes predictable given inputs, or judgment-dependent? | Exception Frequency (H/M/L) How often do edge cases occur that break the standard path?| Turn-Taking Degree (H/M/L) How much back-and-forth with humans, systems, or both?| Latency Constraint (H/M/L) Is real-time response required, or is batch acceptable?| Compliance/Risk Sensitivity (H/M/L) What is the cost of an error? Regulated? Audited? | Tool/API Availability (H/M/L) Can the agent access the required data and systems? |
|------------|------------------------|-------------------------|------------------------------|------------------------------|---------------------------|---------------------------|--------------------------------------|-------------------------------|

Include at least 5 micro-tasks per work stream. Scores must be justified in footnotes — not asserted.

#### 2e. Process topology diagram
Use **two Mermaid flowcharts** (`flowchart TD`), each covering roughly half the work stream. Split at a natural phase boundary — for example, between the intake/comparison phases and the triage/routing phases. Label each diagram with its phase name (e.g., "Phase 1 — Ingestion & Classification", "Phase 2 — Triage & Routing"). Each diagram should contain no more than 6–8 nodes so it fits a screen without horizontal scrolling.

Zones are rounded rectangles `([...])`, breakpoints are diamonds `{...}`. Use style declarations to distinguish agent-owned zones (green: `fill:#d4edda,color:#155724,stroke:#155724`) from human-in-the-loop zones (amber: `fill:#fff3cd,color:#856404,stroke:#856404`). Always include an explicit `color:` value in every style declaration — without it, text renders grey and is unreadable against tinted backgrounds. Label each node with its ID and a short name — keep labels to one line, no `\n` or `<br/>` inside labels. Where Phase 1 ends at a node that Phase 2 continues from, repeat that node as the entry point of Phase 2 so the split is self-explanatory.

### 3. Cognitive Load Map — Work Stream B
Repeat sections 2a through 2e for the second work stream.

### 4. Cross-work-stream observations
After completing both maps, write 3–5 observations that apply across both. Focus on:
- Shared breakpoints that suggest reusable agent components
- Shared data sources that suggest shared context/retrieval design
- Patterns in where exception handling consumes disproportionate time


### 5. Assumption log
Use this format for every non-trivial claim:

> **Assumption [A1]:** [what you're taking as given]
> **Why it matters:** [what spec decision or metric it drives]
> **If wrong:** [what breaks]
> **Confidence:** low / medium / high

Minimum 2 assumptions in this section. More is better.

----
---

## Acceptance criteria (all must pass)

- [ ] Work stream selection is justified, not assumed
- [ ] Lived process narrative present for each selected work stream — describes actual work (pauses, consultations, informal knowledge, workarounds), not SOP steps
- [ ] At least 2 work streams fully decomposed
- [ ] JtDs are cognitive contracts (outcome-focused), not task descriptions
- [ ] Micro-task tables have at least 5 rows per work stream with justified scores
- [ ] Cognitive zones are distinguished by dominant cognitive type (probabilistic / deterministic / human sense-making)
- [ ] At least 3 breakpoints identified per work stream, with agent opportunity/risk noted
- [ ] Process topology diagram present for each work stream
- [ ] The primary governance/compliance constraint from the scenario reflected in at least one breakpoint
- [ ] No scores without justification in footnotes

## Fail signals — do not produce output that contains these

- Micro-task tables with all scores "H" or all "M" — that is not analysis
- Breakpoints described as "the human reviews the agent output" without specifying the condition that triggers the review
- JtDs that are tasks ("extract the document section") rather than cognitive contracts ("determine whether this input is compliant with policy and what the business exposure is if it is not")
- Zone definitions that group all work together as "review" — zones should separate qualitatively different cognitive activity
- Lived process narrative replaced by a bullet list of steps — it must describe the cognitive experience of the worker (pauses, judgment calls, informal consultations), not a process flow
- Lived process narrative that is SOP-level ("the reviewer checks the input against the policy") — name what the worker actually sees, decides, and does when the standard path doesn't apply
