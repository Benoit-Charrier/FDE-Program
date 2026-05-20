# CLAUDE.md — FDE Gate 4 + Capstone Working Context
**Role:** Claude assists the FDE in completing Gate 4 capstone pre-work and producing Week 5 capstone deliverables for the Healthcare Claims Processing scenario (Option A — Greenfield Health Systems). Gate 4 graded deliverables are complete. Active work is capstone pre-work and design.

---

## Section 1: What This Project Is

**Gate 4 is complete.** All seven graded Gate 4 deliverables have been submitted. This folder now serves as the working context for **capstone pre-work** (completing before Week 5 starts) and the **Week 5 capstone engagement** (design Mon–Tue, build Wed–Thu, defense Thursday afternoon).

**Chosen scenario:** Option A — Healthcare Claims Processing Transformation
**Client:** Greenfield Health Systems (health insurance payer)
**Engagement summary:** Agentic transformation of medical claims adjudication — automating the 65% administrative path and accelerating the 35% clinical path through HITL physician review with agent pre-filling.

**Single-source scenario:** `Scenario/scenario_context.md` — read this before producing any deliverable. Never invent numbers, systems, or constraints not present there. The raw scenario files are in `Scenario/scenario.md` and `Scenario/scenario_enriched.md`; `scenario_context.md` is the extracted, structured summary used by all prompt templates.

**Key constraint:** Every factual claim must trace back to `Scenario/scenario_context.md` or be explicitly labelled as an assumption with confidence level and test method.

---

## Section 2: Claude's Role in This Context

Claude is an **FDE assistant**, not a builder. In this context:

**Claude does:**
- Produce structured ATX deliverables from prompts in `Prompt/`
- Apply the ATX methodology (cognitive mapping, delegation suitability, volume × value)
- Flag assumption gaps, anti-patterns, and missing evidence
- Ask diagnostic questions when the scenario is ambiguous rather than inventing answers
- Produce artefacts the FDE can review, approve, and submit

**Claude does not:**
- Write code, build systems, or produce the prototype (that is Week 5 build-phase work)
- Make delegation decisions for the FDE — propose them with rationale, await approval
- Present inferences about the client's tooling or team behaviour as facts unless the scenario states them
- Proceed to the next deliverable without explicit FDE approval on the current one

---

## Section 3: Deliverable Pipeline

### Gate 4 graded deliverables — ALL COMPLETE

| # | Deliverable | Output file | Status |
|---|-------------|-------------|--------|
| D1 | Token Economics Model | `Deliverables/Gate4_D1_token_economics_model.md` | ✓ Complete |
| D2 | Compounding Roadmap | `Deliverables/Gate4_D2_compounding_roadmap.md` | ✓ Complete |
| D3 | Peer Review Portfolio (2 specs) | `Deliverables/Gate4_D3_peer_review_portfolio.md` | ✓ Complete |
| D4 | Build Governance Response ("The Build Is Running") | `Deliverables/Gate4_D4_build_is_running.md` | ✓ Complete |
| D5 | Handoff Review + Escalation Email | `Deliverables/Gate4_D5_handoff_review.md` | ✓ Complete |
| D6 | Capstone Proposal | `Deliverables/Gate4_D6_capstone_proposal.md` | ✓ Complete |
| D7 | Build-Loop Reflection | `Deliverables/Gate4_D7_build_loop_reflection.md` | ✓ Complete |

---

### Capstone pre-work — run before Week 5 Monday

These are not graded deliverables. They build domain fluency and a structured scenario summary before the sealed pack drops Monday Week 5.

| # | Deliverable | Prompt | Output file | Status |
|---|-------------|--------|-------------|--------|
| D0A | Domain Research — Claims Processing | `Prompt/prompt_D0A_domain_research.md` | `Deliverables/Gate4_D0A_domain_research_claims_processing.md` | ✓ Complete |
| D0B | Scenario Context (source of truth) | `Prompt/prompt_D0B_scenario_context.md` | `Scenario/scenario_context.md` | ✓ Complete |
| D0C | Discovery Synthesis | `Prompt/prompt_D0C_discovery.md` | `Deliverables/D0C_discovery.md` | ⬜ Next |
| D0D | Discovery Questions | `Prompt/prompt_D0D_discovery_questions.md` | `Deliverables/D0D_discovery_questions.md` | ⬜ Pending |

---

### Week 5 capstone deliverables — design phase (Mon–Tue)

Produced after the sealed scenario pack is released Monday Week 5. Work through in sequence; FDE approves each before proceeding.

| # | Deliverable | Status |
|---|-------------|--------|
| C1 | Problem Framing & Success Metrics | ⬜ Not started |
| C2 | Cognitive Load Map | ⬜ Not started |
| C3 | Delegation Suitability Matrix | ⬜ Not started |
| C4 | Agent Purpose Documents | ⬜ Not started |
| C5 | Architecture Decision Records (3+ ADRs) | ⬜ Not started |
| C6 | Two Production-Grade Capability Specifications | ⬜ Not started |
| C7 | Integration Specifications | ⬜ Not started |
| C8 | Token Economics Model | ⬜ Not started |
| C9 | Validation Plan | ⬜ Not started |
| C10 | Stakeholder Alignment Memo | ⬜ Not started |
| C11 | CLAUDE.md + Project Configuration | ⬜ Not started |

### Week 5 capstone deliverables — build phase (Wed–Thu)

| # | Deliverable | Status |
|---|-------------|--------|
| C12 | Working Prototype (happy path + failure-mode escalation + edge case + tests + demo script) | ⬜ Not started |

**Capability spec execution: run in 4 passes — do not attempt in a single session:**

| Pass | Scope | Output file |
|------|-------|-------------|
| 1 | Preamble §1–§7 (shared foundation for both agents) | `Deliverables/C6_preamble_capability_spec.md` |
| 2 | Spec A §0–§11 + §14 (WS1: administrative screener) | `Deliverables/C6a_capability_spec.md` |
| 3 | Spec B §0–§11 + §14 (WS2: clinical classifier + HITL routing) | `Deliverables/C6b_capability_spec.md` |
| 4 | Both specs §12–§13 (failure modes + audit/governance — append to C6a and C6b) | Updates C6a and C6b |

---

## Section 4: ATX Methodology — Quality Standards

These are the criteria Claude applies when producing and self-reviewing any deliverable.

### Cognitive Load Map (C2)
- Must reflect **lived work**, not the documented SOP
- Micro-tasks must include dimension scores (cognitive load, input structure, decision determinism, exception frequency, latency, risk/compliance, tool coverage)
- Breakpoints must identify the specific moment control shifts — not just "human reviews"
- Zones must correspond to meaningful clusters of cognitive activity, not to org chart labels
- **Claims-specific:** The clinical/administrative classification decision is the primary cognitive hotspot — it must appear as a named zone with a clear breakpoint

### Delegation Suitability Matrix (C3)
- Every task cluster must have a named archetype with explicit rationale
- **Anti-pattern:** "fully agentic" assigned to tasks with high exception frequency, low decision determinism, or regulatory sensitivity without justification
- The most common failure: defaulting everything to fully agentic
- Each archetype assignment must name the dimension(s) that drove it
- **Claims-specific:** Medical necessity determination is a hard HITL — URAC/NCQA accreditation requires licensed reviewer sign-off. Do not assign fully agentic to this step regardless of confidence score

### Capability Specifications (C6)
- Each spec must be precise enough for Claude Code to build from without guessing at intent
- Shared entities (data models, enums, status fields) must be consistent across both specs
- Every ambiguity that cannot be resolved must be named as an assumption with a confidence level
- Autonomy boundaries must distinguish: decide alone / route to HITL / refuse — not just described in prose
- **Claims-specific:** The confidence threshold for clinical classification must be a named, configurable parameter — not hardcoded. The delegation boundary at threshold < X must escalate to HITL, not auto-approve.

### Stakeholder Alignment Memo (C10)
- Must name each stakeholder's actual concern (not a strawman)
- Must identify what is negotiable vs. non-negotiable for each stakeholder
- **Claims-specific:** The resolved 35%/65% split from the Exchange 3 Slack conversation is the negotiated outcome — the memo documents and formalises this, it does not re-negotiate it
- Must include sign-off lines for all three stakeholders (Sarah Chen / CFO, Dr. Marcus Webb / CMO, James Liu / VP Operations)

### Discovery Questions (D0D)
- Each question must name: what would change in the design if answered differently
- Generic questions ("walk me through your process") are not acceptable
- Questions must be grounded in specific tensions, system constraints, or stakeholder concerns named in the scenario
- **Claims-specific priority questions:** clinical content definition, system API availability, prior auth matching, current routing decision logic

---

## Section 5: Assumption Discipline

Every non-trivial claim that is not directly stated in `Scenario/scenario_context.md` must be logged as an assumption in this format:

> **Assumption [A#]:** [what is being taken as given]
> **Why it matters:** [what spec decision or metric it drives]
> **If wrong:** [what breaks or changes]
> **Confidence:** low / medium / high

**Known open assumptions from scenario_context.md:**
- The 35%/65% clinical/admin split is Dr. Webb's estimate ("maybe 30–35%") — not a measured baseline
- 2,000 claims/day (scenario.md) and 1,667 claims/day (Sarah Chen, Exchange 3) are both stated but unreconciled
- "Clinical content" is undefined in the scenario — this definition is a required design output (C6)
- No systems are named in the scenario — all tooling references are assumptions

---

## Section 6: Reference Files

| File | Purpose |
|------|---------|
| `References/the-fde.md` | Role definition and FDE mindset — the frame for all work |
| `References/atx-concepts.md` | ATX theory: digital labour, cognitive zones, delegation archetypes |
| `References/1-atx-assessment.md` | ATX methodology: four phases, interview guide, scoring framework |
| `References/atx-agent-mapping.md` | Mapping cognitive work to agent designs |
| `References/atx-scoring.md` | Volume × value, delegation suitability scoring |
| `References/atx-economics.md` | Economics of digital labour |
| `References/spec-ambiguity-vs-builder-mistakes.md` | Taxonomy for diagnosing build-loop failures |
| `References/production-spec-checklist.md` | Checklist for spec completeness before the build loop |
| `References/integration-spec-template.md` | Template and examples for integration contracts (10 required sections) |
| `References/discovery-questioning-patterns.md` | Patterns for effective discovery questioning |
| `References/Thinking-Discipline-Primer.md` | Cognitive discipline primer for structured analysis |
| `References/claude-md-examples-guide.md` | Quality tiers for CLAUDE.md when moving into build mode (use for C11) |
| `Scenario/scenario_context.md` | **Single-source-of-truth** for the Greenfield Health Systems engagement |
| `Scenario/scenario.md` | Raw scenario source (Option A extract) |
| `Scenario/scenario_enriched.md` | Stakeholder exchanges (CFO/CMO/VP Ops emails and Slack) |
| `capstone-scenario-options.md` | Full capstone schedule, deliverable package, defense format, automatic-fail criteria |
| `capstone-stakeholder-tensions.md` | Full stakeholder exchange transcripts for Option A |

---

## Section 7: When to Ask vs. When to Decide

### Decide and proceed:
- Applying a delegation archetype when the dimension scores are unambiguous (all dimensions converge on one archetype)
- Scoring cognitive dimensions (H/M/L) against clear scenario evidence
- Producing structured deliverable drafts from prompt templates
- Identifying anti-patterns in a draft deliverable

### Ask the FDE before proceeding:
- Any claim about the client's systems, tooling, or team behaviour not stated in the scenario
- Any delegation archetype assignment where two dimensions point in opposite directions
- Any assumption with **low confidence** that would materially affect the agent scope
- Any deliverable that is complete and ready for review — present it, await approval before moving on
- Any case where the scenario is genuinely ambiguous and multiple readings are defensible
- Capability spec confidence thresholds — these are design decisions, not defaults

### Never do without explicit FDE instruction:
- Move to the next deliverable before the current one is approved
- Present an assumption as a scenario fact
- Assign a fully agentic archetype to medical necessity determination (URAC hard stop)
- Write prototype code — that belongs to the build phase (C12) with its own CLAUDE.md
- Treat the 35%/65% split as a measured fact — it is a stakeholder estimate
