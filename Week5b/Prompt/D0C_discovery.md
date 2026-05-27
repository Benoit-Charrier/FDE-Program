# Prompt: D0C — Discovery Synthesis

## Methodology references

- `References/1-atx-assessment.md` — Phase 1: Discovery (Points of Pain inventory, interview guide, candidate process identification)

## Inputs

- `Scenario/scenario_context.md` — all sections
- `Deliverables/D0A_domain_research.md` — domain constraints and failure modes

## Your task

Synthesise the scenario facts and domain knowledge into a concise discovery brief. This is not a summary of the two inputs — it is the FDE's working interpretation of the situation: what is actually broken, what the domain constraints mean for this specific design, and what must be resolved before the design can proceed.

Output file: `Deliverables/D0C_discovery.md`

---

## Required structure

### 1. Situation in one paragraph
What is the client's actual problem, stated precisely. Include the most consequential number from the scenario. End with the structural reason the current approach cannot solve it.

### 2. Points of Pain inventory
List every candidate process from the scenario where skilled human time is consumed at scale, there is operational friction, or the cost-per-task is high. This is the raw candidate list for P2 and D2C — do not pre-filter.

| Process | Rough volume | Pain level (H/M/L) | Data / system context | Delegation candidate? |
|---------|-------------|--------------------|-----------------------|----------------------|
| [process name] | [from scenario — cases/day or %] | H/M/L | [inputs, systems touched, data type] | Yes / Partial / No |

Minimum 4 entries. Volume and pain level must reference specific scenario figures or be labelled as assumptions.

### 3. What the domain constraints mean for this design
Cross-reference D0A §2 (regulatory constraints) against the scenario. For each constraint that applies:

> **[Constraint]:** Given [scenario fact], this means [specific design implication — e.g., a hard HITL requirement, a mandatory audit trail, a data residency constraint].

Skip constraints from D0A that do not apply to this scenario.

### 4. The primary cognitive bottleneck
Name the single task in the current process that is simultaneously: (a) high-volume, (b) cognitively demanding, and (c) most exposed to the domain's known failure modes. This is the candidate for the highest-value agent intervention.

### 5. The highest-risk assumption
The one assumption that, if wrong, would most materially change the agent scope or delegation design. State it explicitly with confidence level and what would need to be true for the design to hold.

### 6. Questions the design must answer before the capability spec
List 3–5 specific design questions that remain open after reading the scenario and domain research. For each:

> **Q[N]:** [the question] — **What changes if answered differently:** [the design decision it drives]

---

## Acceptance criteria

- [ ] §1 names the structural failure, not just symptoms
- [ ] §2 has at least 4 candidate processes; volume figures reference scenario or are labelled as assumptions
- [ ] §3 references specific scenario facts, not generic domain constraints
- [ ] §4 names one specific task — not a work stream or process area
- [ ] §5 highest-risk assumption has a stated confidence level (low / medium / high)
- [ ] §6 questions are specific — "what is the API for X?" not "what systems do they use?"
- [ ] Nothing invented about the scenario — all claims trace to scenario_context.md or D0A
