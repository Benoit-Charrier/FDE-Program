# Week5b — Final Exam Prompt System

**Purpose:** Generic prompts for the Part 2 Final Exam (Virtual Friday). 8-hour solo exercise on a sealed scenario. Design phase is 4.5 hours; curveball + adapt is 30 minutes; build is 3 hours.

Each prompt runs in under 5 minutes of model output time. FDE reviews and approves before running the next.

---

## Pre-exam (15 min — before the clock starts, 08:45–09:00)

1. Read the sealed scenario packet fully
2. Note key numbers, stakeholder names, and stated constraints — you will extract these via D0B once the clock starts

---

## Design phase run order (09:00–13:30)

| Step | Prompt | Output file | Why here | Slot |
|------|--------|-------------|----------|------|
| D0B | `Prompt/D0B_scenario_context.md` | `Scenario/scenario_context.md` | Extract sealed packet into structured source-of-truth — all prompts read from this | 09:00–09:20 |
| D0A | `Prompt/D0A_domain_research.md` | `Deliverables/D0A_domain_research.md` | Understand the industry domain before framing the problem | 09:20–09:40 |
| D0C | `Prompt/D0C_discovery.md` | `Deliverables/D0C_discovery.md` | Synthesise D0A + D0B into discovery findings that inform problem framing | 09:40–09:55 |
| P1 | `Prompt/P1_problem_framing.md` | `Deliverables/01-problem-framing.md` | Problem framing + success metrics per stakeholder | 09:55–10:25 |
| P2a | `Prompt/P2a_cognitive_load_map.md` | `Deliverables/02a-cognitive-load-map.md` | Cognitive load map — JtDs, micro-task scores, zones, breakpoints | 10:25–11:05 |
| P2b | `Prompt/P2b_delegation_matrix.md` | `Deliverables/02b-delegation-matrix.md` | Delegation matrix — archetype assignments, boundary narrative, hard HITL | 11:05–11:35 |
| P2c | `Prompt/P2c_agent_landscape.md` | `Deliverables/02c-agent-landscape.md` | Agent landscape — JtD-to-agent mapping, agent design summaries, non-agentic residual, AI-native moment | 11:35–11:55 |
| P2d | `Prompt/P2d_combine.md` | `Deliverables/02-cognitive-delegation.md` | Combine P2a + P2b + P2c into single deliverable (no new analysis) | 11:55–12:00 |
| D2C | `Prompt/D2C_volume_value.md` | `Deliverables/D2C_volume_value.md` | Volume × value scoring — identifies highest-ROI automation target | 12:00–12:20 |
| P7 | `Prompt/P7_economics_sketch.md` | `Deliverables/07-economics.md` | Economics sketch — closes the business case before committing to agent scope | 12:20–12:40 |
| P3 | `Prompt/P3_agent_purpose.md` | `Deliverables/03-agent-purpose.md` | Agent purpose — now informed by D2C + P7 + P2c; agent selection is justified | 12:40–13:00 |
| P4 | `Prompt/P4_adrs.md` | `Deliverables/04-adrs.md` | 2–3 ADRs with rejected alternatives | 13:00–13:12 |
| P5 pass 1 | `Prompt/P5_pass1_capability_spec.md` | `Deliverables/05-capability-spec.md` | One spec — §0–§6: identity, I/O, entities, activity catalog, requirements, decision logic | 13:12–13:22 |
| P5 pass 2 | `Prompt/P5_pass2_capability_spec.md` | append `05-capability-spec.md` | One spec — §7–§11: escalation triggers, autonomy matrix, state model, test scenarios, assumptions | 13:22–13:28 |
| P6 | `Prompt/P6_validation_plan.md` | `Deliverables/06-validation-plan.md` | 3 test scenarios (happy path, failure mode, edge case) | 13:28–13:30 |
| P8 | `Prompt/P8_claude_md.md` | `CLAUDE.md` | Build-phase config — generated last so it reflects the final spec | after P6 if time |

**Submit design package by 13:30.**

> **If running behind:** P8 is the most droppable — you can write the build CLAUDE.md at the start of the build phase instead. P6 is the next droppable. P5 passes 1 and 2 are the least droppable — the capability spec is the highest-weighted design criterion and the foundation of the build. P2c (combine) is 2 minutes; never skip it even when rushed.

---

## Curveball + adapt (13:30–14:00)

1. Read the curveball carefully — name the assumption it invalidates before writing anything
2. Run `Prompt/P9_curveball_response.md`
3. Output: `Deliverables/09-curveball-response.md`
4. Submit by 14:00

---

## Build phase (14:00–17:00)

Build from `05-capability-spec.md` (amended by curveball response if relevant). Same pattern as the capstone:
- One primary agentic flow end-to-end
- One failure-mode escalation that fires correctly
- At least one edge case
- Tests covering all three paths
- `prototype/DEMO.md` — demo script showing three paths in under 5 minutes

**Submit by 17:00. Include self-assessment output.**

---

## Key rules

- `Scenario/scenario_context.md` is the single source of truth — every factual claim must trace back to it or be labelled as an assumption with confidence level
- Never invent stakeholder names, system names, or metrics not stated in the scenario
- If the scenario is ambiguous, label it as an assumption — do not invent
- Prototype must run — automatic fail if it doesn't
- Build must be faithful to the spec — silent scope creep or silent scope reduction both fail
- If you find a spec gap during the build, submit a spec amendment note — naming it is honoured, hiding it fails

---

## File map

```
Week5b/
  README.md
  CLAUDE.md                                  ← generated by P8
  Scenario/
    scenario_context.md                      ← populated by D0B
  Prompt/
    D0B_scenario_context.md
    D0A_domain_research.md                   ← reads References/atx-concepts.md
    D0C_discovery.md                         ← reads References/1-atx-assessment.md (Phase 1)
    P1_problem_framing.md
    P2a_cognitive_load_map.md                ← reads atx-concepts, 1-atx-assessment, atx-agent-mapping
    P2b_delegation_matrix.md                 ← reads atx-scoring, atx-agent-mapping; reads 02a output
    P2c_agent_landscape.md                   ← reads atx-agent-mapping; reads 02a + 02b outputs
    P2d_combine.md                           ← combines 02a + 02b + 02c into final 02-cognitive-delegation.md
    D2C_volume_value.md                      ← reads References/atx-scoring.md
    P7_economics_sketch.md                   ← reads References/atx-economics.md
    P3_agent_purpose.md
    P4_adrs.md
    P5_pass1_capability_spec.md              ← §0–§6; reads production-spec-checklist, spec-ambiguity-vs-builder-mistakes
    P5_pass2_capability_spec.md              ← §7–§11 appended to same file; same references
    P6_validation_plan.md
    P8_claude_md.md                          ← reads References/claude-md-examples-guide.md
    P9_curveball_response.md
  References/                                ← key ATX methodology files (self-contained)
    atx-concepts.md
    1-atx-assessment.md
    atx-agent-mapping.md
    atx-scoring.md
    atx-economics.md
    production-spec-checklist.md
    spec-ambiguity-vs-builder-mistakes.md
    claude-md-examples-guide.md
  Deliverables/
    D0A_domain_research.md
    D0C_discovery.md
    D2C_volume_value.md
    01-problem-framing.md
    02a-cognitive-load-map.md               ← intermediate (P2a output)
    02b-delegation-matrix.md                ← intermediate (P2b output)
    02c-agent-landscape.md                  ← intermediate (P2c output)
    02-cognitive-delegation.md              ← final combined (P2d output)
    03-agent-purpose.md
    04-adrs.md
    05-capability-spec.md                    ← single spec, two passes
    06-validation-plan.md
    07-economics.md
    09-curveball-response.md
  prototype/                                 ← build phase output
```
