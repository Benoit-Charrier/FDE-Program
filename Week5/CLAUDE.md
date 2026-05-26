# CLAUDE.md — FDE Gate 4 + Capstone Working Context
**Role:** Claude assists the FDE across all phases of the Week 5 capstone engagement for the Healthcare Claims Processing scenario (Option A — Greenfield Health Systems). Gate 4 is complete. The C12 prototype (WS1 administrative adjudication agent) is built, validated, and passing all tests. Active work is defense prep and any remaining Week 5 deliverables.

---

## Section 1: What This Project Is

**Gate 4 is complete.** All seven graded Gate 4 deliverables have been submitted. The Week 5 capstone engagement (design Mon–Tue, build Wed–Thu, defense Thursday afternoon) is in the build/validation phase.

**Chosen scenario:** Option A — Healthcare Claims Processing Transformation
**Client:** Greenfield Health Systems (health insurance payer)
**Engagement summary:** Agentic transformation of medical claims adjudication — automating the 65% administrative path and accelerating the 35% clinical path through HITL physician review with agent pre-filling.

**Single-source scenario:** `Scenario/scenario_context.md` — read this before producing any deliverable. Never invent numbers, systems, or constraints not present there. The raw scenario files are in `Scenario/scenario.md` and `Scenario/scenario_enriched.md`; `scenario_context.md` is the extracted, structured summary used by all prompt templates.

**Key constraint:** Every factual claim must trace back to `Scenario/scenario_context.md` or be explicitly labelled as an assumption with confidence level and test method.

---

## Section 2: Claude's Role in This Context

Claude operates as both **FDE assistant** and **prototype builder** in this context.

**Claude does:**
- Produce structured ATX deliverables from prompts in `Prompt/`
- Apply the ATX methodology (cognitive mapping, delegation suitability, volume × value)
- Flag assumption gaps, anti-patterns, and missing evidence
- Ask diagnostic questions when the scenario is ambiguous rather than inventing answers
- Produce artefacts the FDE can review, approve, and submit
- Build and iterate on the C12 prototype in `prototype/` (build phase is active)
- Run pytest, read test output, diagnose and fix failures

**Claude does not:**
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

### Capstone pre-work

| # | Deliverable | Prompt | Output file | Status |
|---|-------------|--------|-------------|--------|
| D0A | Domain Research — Claims Processing | `Prompt/prompt_D0A_domain_research.md` | `Deliverables/D0A_domain_research_claims_processing.md` | ✓ Complete |
| D0B | Scenario Context (source of truth) | `Prompt/prompt_D0B_scenario_context.md` | `Scenario/scenario_context.md` | ✓ Complete |
| D0C | Discovery Synthesis | `Prompt/prompt_D0C_discovery.md` | `Deliverables/D0C_discovery.md` | ⬜ Pending |
| D0D | Discovery Questions | `Prompt/prompt_D0D_discovery_questions.md` | `Deliverables/D0D_discovery_questions.md` | ⬜ Pending |

---

### Week 5 capstone deliverables

| # | Deliverable | Output file | Status |
|---|-------------|-------------|--------|
| C1 | Problem Framing & Success Metrics | `Deliverables/D1_problem_framing.md` | ✓ Complete |
| C2 | Cognitive Load Map | — | ⬜ Not started |
| C3 | Delegation Suitability Matrix | `Deliverables/D3_agentic_solution_architecture.md` | ✓ Complete |
| C4 | Agent Purpose Documents | `Deliverables/D4_agent_purpose_document.md` | ✓ Complete |
| C4a | Preamble Capability Spec (§1–§7, shared) | `Deliverables/D4_preamble_capability_spec.md` | ✓ Complete — all spec gaps resolved |
| C6a | WS1 Capability Spec (§0–§14, administrative screener) | `Deliverables/D4a_capability_spec.md` | ✓ Complete — all spec gaps resolved |
| C6b | WS2 Capability Spec (clinical classifier + HITL routing) | — | ⬜ Not started |
| C7 | Integration Specifications | `Prompt/prompt_D4_integration_specs.md` | ⬜ Prompt ready, output not started |
| C8 | Token Economics Model | `Deliverables/D2D_token_economics_model.md` | ✓ Complete |
| C9 | Validation Plan | `Deliverables/D7_validation_plan.md` | ✓ Complete |
| C9a | Validation Design Diagnosis | `Deliverables/D7A_validation_design_diagnosis.md` | ✓ Complete — all 3 scenarios PASS |
| C10 | Stakeholder Alignment Memo | — | ⬜ Not started |
| C11 | CLAUDE.md + Project Configuration | `CLAUDE.md` (this file) | ✓ In progress |
| C12 | Working Prototype — WS1 agent | `prototype/` | ✓ Complete — 5/5 tests passing |

**Capability spec execution passes completed:**

| Pass | Scope | Output file | Status |
|------|-------|-------------|--------|
| 1 | Preamble §1–§7 (shared foundation) | `Deliverables/D4_preamble_capability_spec.md` | ✓ Complete |
| 2 | Spec A §0–§14 (WS1: administrative screener) | `Deliverables/D4a_capability_spec.md` | ✓ Complete |
| 3 | Spec B §0–§14 (WS2: clinical classifier + HITL routing) | — | ⬜ Not started |

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

### Capability Specifications (C4a/C6a/C6b)
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

**Open prototype assumptions requiring CMO input (from D7_validation_plan.md):**
- A2: Golden-set clinical-boundary case threshold set at 95% recall — no measured baseline. If wrong, QF-1 false-negative rate is miscalibrated. **Low confidence.**
- A4: CalibrationRecord revocation polling interval assumed 5 min. If wrong, agent may run against an invalidated record for longer than acceptable. **Low confidence.**

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
- Running and fixing tests in the prototype build loop

### Ask the FDE before proceeding:
- Any claim about the client's systems, tooling, or team behaviour not stated in the scenario
- Any delegation archetype assignment where two dimensions point in opposite directions
- Any assumption with **low confidence** that would materially affect the agent scope
- Any deliverable that is complete and ready for review — present it, await approval before moving on
- Any case where the scenario is genuinely ambiguous and multiple readings are defensible
- Capability spec confidence thresholds — these are design decisions, not defaults
- Any prototype change that touches the FM-A-5 hard stop logic, audit-first ordering, or state machine transitions — these are governance boundaries

### Never do without explicit FDE instruction:
- Move to the next deliverable before the current one is approved
- Present an assumption as a scenario fact
- Assign a fully agentic archetype to medical necessity determination (URAC hard stop)
- Treat the 35%/65% split as a measured fact — it is a stakeholder estimate

---

## Section 8: Prototype Build State

### File inventory — `prototype/`

| File | Purpose |
|------|---------|
| `config.py` | `CLINICAL_CONTENT_CONFIDENCE_THRESHOLD = 0.70`, `CLASSIFIER_VERSION = "sonnet-4-6:ws1-routing:v1"` |
| `requirements.txt` | Python dependencies |
| `agents/ws1_agent.py` | Main pipeline: T-01 through T-09 state machine, FM-A-5 hard stop, audit-first ordering, all EscalationPacket fields spec-compliant |
| `agents/__init__.py` | Package init |
| `tools/calibration.py` | CalibrationRecord 6-field startup validation; `startup_validate()`, `CalibrationError` |
| `tools/clinical_classifier.py` | `classify_clinical_content()` — returns `{classification, confidence, reasoning}` |
| `tools/eligibility.py` | `check_eligibility()` |
| `tools/code_validity.py` | `check_code_validity()` |
| `tools/prior_auth.py` | `check_prior_auth()` |
| `tools/fee_schedule.py` | `get_payment_amount()` |
| `tools/__init__.py` | Package init |
| `tests/test_ws1_pipeline.py` | 5 tests — all passing |
| `fixtures/CLAIM-ADMIN-01.json` | Happy path / threshold boundary fixture |
| `fixtures/CLAIM-CLINICAL-01.json` | Clinical routing fixture |
| `fixtures/CLAIM-UNCERTAIN-01.json` | Uncertain classification fixture |
| `fixtures/CLAIM-ELIG-01.json` | Eligibility discrepancy fixture |
| `run_claim.py` | CLI: run a single claim through the pipeline |
| `review_claim.py` | CLI: review a saved escalation file |
| `escalations/` | Directory for saved escalation JSON files |

### Test status — 2026-05-25

All 5 tests passing:

| Test | What it covers |
|------|---------------|
| `test_happy_path` | S-1: CLAIM-ADMIN-01, confidence 0.91, all stubs nominal → `status=approved`, `payment_amount=85.0`, 6 COMMITTED audit entries |
| `test_uncertain_classification` | ET-01/ET-02 routing → `status=escalated`, physician HITL queue |
| `test_eligibility_discrepancy` | ET-03 escalation → `status=escalated`, exception processor queue |
| `test_confidence_at_threshold` | S-2: confidence exactly 0.70 → `>=` operator confirmed inclusive, `status=approved` |
| `test_governance_hard_stop` | S-3: FM-A-5 hard stop — state corrupted to ROUTING after ADMIN_CLEARED → ET-07 fires with `GOVERNANCE_VIOLATION`, `payment_amount` absent, `claim_state_at_escalation` preserved (not overwritten to PENDING_HITL_EXCEPTION) |

### Resolved spec gaps

| Gap | Description | Resolution | Applied to |
|-----|-------------|------------|------------|
| GAP-10 | REQ-A-6(c) contradicted §7 ET-07: spec said state → PENDING_HITL_EXCEPTION for governance violation, but diagnostic value is the incoming state | Leave state unchanged; `preserve_state=True` on governance-violation ET-07 call | `D4a_capability_spec.md` REQ-A-6, `ws1_agent.py` `_fire_et07` |
| GAP-14 | ET-07 `trigger_type` enum only had `AUDIT_FAILURE`; governance hard-stop needs a distinct type | Add `GOVERNANCE_VIOLATION` to `EscalationPacket.trigger_type` enum | `D4_preamble_capability_spec.md` enum, `D4a_capability_spec.md` outputs table + ET-07 action column |
| D7A residual | ET-07 `required_resolution` text said "Audit failure" even when `trigger_type = GOVERNANCE_VIOLATION`, giving exception processor contradictory signals | Split into two strings; `_fire_et07` selects by `trigger_type` | `D4a_capability_spec.md` §7 required_resolution table (two rows for ET-07), `ws1_agent.py` `_fire_et07` conditional |

### Key invariants (do not break without FDE sign-off)

- **Audit-first ordering**: `AuditEntry.committed` must be `True` before any `ctx.transition()` to a post-payment state. If audit write fails, ET-07 fires and `payment_amount` is NOT written.
- **FM-A-5 hard stop**: First operation of T-09 is `ctx.state != "ADMIN_CLEARED"` check. If it fails, `_fire_et07(..., trigger_type="GOVERNANCE_VIOLATION", preserve_state=True)` is returned immediately — `get_payment_amount()` is never called.
- **`from_state` on every transition**: `ctx.transition(to_state, from_state=expected)` raises `ConflictError` (409) if state diverged. Production S-07 PATCH carries the same guard.
- **Startup validation**: `process_claim()` raises `RuntimeError` if `_STARTUP_ERROR` is set (CalibrationRecord failed 6-field check at import time).
- **`calibration_record_id` in approved output**: Governance chain from payment decision back to CMO-signed CalibrationRecord must be traceable in every approved response.

### Open items for production deployment

| Item | Category | What needs to happen |
|------|----------|---------------------|
| QF-2 | Integration contract gap | `GOVERNANCE_VIOLATION` EscalationPacket routed through S-09 — integration contract must explicitly list this `trigger_type` as a valid payload. Risk: S-09 silently drops unknown enum values. Needs S-09 contract update before production. |
| A2 | Open assumption | Golden-set clinical-boundary recall threshold (95%) needs CMO sign-off against measured baseline before CalibrationRecord can be issued for production. |
| A4 | Open assumption | CalibrationRecord revocation polling interval (assumed 5 min) needs operations agreement before production deploy. |
