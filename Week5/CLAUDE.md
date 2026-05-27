# CLAUDE.md — FDE Gate 4 + Capstone Working Context
**Role:** Claude assists the FDE across all phases of the Week 5 capstone engagement for the Healthcare Claims Processing scenario (Option A — Greenfield Health Systems). Gate 4 is complete. The C12 prototype (WS1 administrative adjudication agent) is built, validated, and passing all tests. Active work is defense prep and any remaining Week 5 deliverables.

---

## Section 1: What This Project Is


**Chosen scenario:** Option A — Healthcare Claims Processing Transformation
**Client:** Greenfield Health Systems (health insurance payer)
**Engagement summary:** Agentic transformation of medical claims adjudication — automating the 65% administrative path and accelerating the 35% clinical path through HITL physician review with agent pre-filling.

**Single-source scenario:** `Scenario/scenario_context.md` — read this before producing any deliverable. Never invent numbers, systems, or constraints not present there. The raw scenario files are in `Scenario/scenario.md` and `Scenario/scenario_enriched.md`; `scenario_context.md` is the extracted, structured summary used by all prompt templates.

**Key constraint:** Every factual claim must trace back to `Scenario/scenario_context.md` or be explicitly labelled as an assumption with confidence level and test method.

**Claims Pack mock data:** `Capstone-A-Claims-Pack/` — 2,000 synthetic claims across 8 intake formats. This is the fixture dataset for design, testing, and demo. No real PHI; no answer key (build your own validation set).

| Format | Files | Share | Technical encoding | Intake complexity |
|--------|------:|------:|--------------------|-------------------|
| EDI 837P (professional) | 1,000 | 50% | X12: `*` separator, `~` terminator, `:` component | Parser; no LLM |
| EDI 837I (institutional) | 200 | 10% | Same X12 encoding | Parser; no LLM |
| Portal JSON | 400 | 20% | Pretty-printed JSON — cleanest shape | Near-zero |
| FHIR R4 Claim resource | 100 | 5% | FHIR R4 `Claim` resource shape | Structured; no LLM |
| CMS-1500 paper PDF | 200 | 10% | Single-page PDF — OCR required; `cms1500-ocr/` pre-extracted text provided | OCR already done in pack |
| Email (.eml) | 30 | 1.5% | RFC 5322; custom `X-Submitter-NPI` / `X-Submitter-TaxID` headers | LLM extraction |
| Fax cover sheet PDF | 30 | 1.5% | Single-page PDF with watermark | LLM extraction |
| Exception notes PDF | 40 | 2% | Typed notes, call logs, handwritten stickies — three style variants | LLM extraction — hardest |

**Prototype scope:** The C12 prototype covers **Tier 1 formats — EDI 837P + 837I + Portal JSON (80% of volume)**. Parsers for all three are built and validated against the full 1,600-file population; 1,493 parsed canonical files are cached in `prototype/normalized-tier1/`. CMS-1500 OCR (10%) is deferred — parser exists but 41% PARSE_FAILED rate makes it not production-ready. FHIR R4, email, fax, and exception notes (remaining 10%) are Tier 2/3 and handled by the Intake & Anomaly Agent (D3 Agent 1), scoped out of the prototype. State the deferred formats explicitly in the demo and defense — "silently excluding formats to report a flattering metric is the weakest possible move" (Claims Pack §Grading).

**False positive protection — the pack's primary warning:** *"The dangerous failure mode is silently approving claims that should have been denied."* Three layers guard this in the current design:
1. FM-A-5 hard stop — T-09 cannot execute unless `state == ADMIN_CLEARED`
2. Audit-first ordering — `payment_amount` never written without a `COMMITTED` audit entry
3. CalibrationRecord governance — CMO-certified threshold; borderline cases escalate to HITL

`test_governance_hard_stop` covers layer 1. Lead with this in the defense when asked about the most dangerous failure mode.

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


---

### Capstone pre-work

| # | Deliverable | Prompt | Output file | Status |
|---|-------------|--------|-------------|--------|
| D0A | Domain Research — Claims Processing | `Prompt/prompt_D0A_domain_research.md` | `Deliverables/D0A_domain_research_claims_processing.md` | ✓ Complete |
| D0B | Scenario Context (source of truth) | `Prompt/prompt_D0B_scenario_context.md` | `Scenario/scenario_context.md` | ✓ Complete |
| D0C | Discovery Synthesis | `Prompt/prompt_D0C_discovery.md` | `Deliverables/D0C_discovery.md` | ✓ Complete |
| D0D | Discovery Questions | `Prompt/prompt_D0D_discovery_questions.md` | `Deliverables/D0D_discovery_questions.md` | ⬜ Pending |

---

### Week 5 capstone deliverables

Official numbering and filename suggestions are from `Gate5a-Capstone-Participant-Pack.md` §3. "Our file" is the working file produced during the engagement; the Gate5a filename is the submission target.

| Gate5a # | Deliverable | Gate5a filename | Our file | Status |
|----------|-------------|-----------------|----------|--------|
| 1 | Problem Framing & Success Metrics | `01-problem-framing.md` | `Deliverables/D1_problem_framing.md` | ✓ Complete |
| 2 | Cognitive Load Map | `02-cognitive-load-map.md` | `Deliverables/D2A_cognitive_load_map.md` | ✓ Complete |
| 3 | Delegation Suitability Matrix | `03-delegation-matrix.md` | `Deliverables/D2B_delegation_suitability_matrix.md` + `Deliverables/D3_agentic_solution_architecture.md` | ✓ Complete |
| 4 | Agent Purpose Document(s) | `04-agent-purpose.md` | `Deliverables/D4_agent_purpose_document.md` | ✓ Complete |
| 5 | Architecture Decision Records (3+) | `05-adrs.md` | `Deliverables/05-adrs.md` (ADR-1, ADR-2, ADR-3 extracted from D3 §4) | ✓ Complete — standalone submission file; full architecture context remains in `D3_agentic_solution_architecture.md` |
| 6 | Two production-grade capability specifications | `06-capability-specs.md` | Preamble: `Deliverables/D4_preamble_capability_spec.md`; Spec A (WS1): `Deliverables/D4a_capability_spec.md`; Spec B (WS2): `Deliverables/D4b_capability_spec.md` | ✓ Complete — all spec gaps resolved |
| 7 | Integration specifications | `07-integration-specs.md` | Preamble: `Deliverables/D4_integration_preamble.md`; Contracts: `Deliverables/D4_integration_specs.md` | ✓ Complete |
| 8 | Token economics model with sensitivity analysis | `08-economics.md` | `Deliverables/D2D_token_economics_model.md` | ✓ Complete |
| 9 | Validation plan | `09-validation-plan.md` | `Deliverables/D7_validation_plan.md` | ✓ Complete |
| 10 | Stakeholder alignment memo | `10-stakeholder-memo.md` | `Deliverables/C10_stakeholder_alignment_memo.md` | ✓ Complete |
| 11 | CLAUDE.md and project configuration | `CLAUDE.md` | `CLAUDE.md` (this file) | ✓ In progress |
| 12 | Working prototype | `prototype/` | `prototype/` | ✓ Complete — 5/5 tests passing |

**Supporting deliverables (not Gate5a official, produced during engagement):**

| # | Deliverable | Output file | Status |
|---|-------------|-------------|--------|
| C9a | Validation Design Diagnosis | `Deliverables/D7A_validation_design_diagnosis.md` | ✓ Complete — all 3 scenarios PASS |
| C13 | Canonical Normalized Claim Record | `Deliverables/D4_canonical_claim_record.md` | ✓ Complete — §9 shows parse-only results (not WS1 routing): 1,493/1,600 Tier 1 files parse successfully (6.7% PARSE_FAILED, all missing diagnosis_codes); 1,493 canonical files cached in `prototype/normalized-tier1/`; CMS-1500 OCR deferred (41% PARSE_FAILED, see §9 deferral note) |
| C14 | Intake Agent Capability Spec | `Deliverables/D4c_capability_spec_intake_agent.md` | ✓ Complete — covers INT-JtD-1 (format detection + extraction), INT-JtD-2 (anomaly detection), 3-tier LLM routing, PARSE_FAILED escalation triggers, 5 open assumptions (A5–A9) |

**Capability spec execution passes (Gate5a deliverable #6):**

| Pass | Scope | Output file | Status |
|------|-------|-------------|--------|
| 1 | Preamble §1–§7 (shared foundation) | `Deliverables/D4_preamble_capability_spec.md` | ✓ Complete — all spec gaps resolved |
| 2 | Spec A §0–§14 (WS1: administrative screener) | `Deliverables/D4a_capability_spec.md` | ✓ Complete — all spec gaps resolved |
| 3 | Spec B §0–§14 (WS2: clinical classifier + HITL routing) | `Deliverables/D4b_capability_spec.md` | ✓ Complete — all spec gaps resolved |

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
- A2: Golden-set clinical-boundary case threshold set at 95% recall — no measured baseline. If wrong, QF-1 false-negative rate is miscalibrated. **Low confidence.** *Mini validation study (D7 §7) now informs golden-set composition: the 30-claim live classifier run showed zero dangerous misses (no LLM admin where manual=clinical) but 73% uncertain-labelling rate driven by CPT/ICD mismatch conflation. The golden set must include deliberate mismatch cases to surface this at calibration time — not just well-formed claims.*
- A4: CalibrationRecord revocation polling interval assumed 5 min. If wrong, agent may run against an invalidated record for longer than acceptable. **Low confidence.**

**Open Intake Agent assumptions (from D4c_capability_spec_intake_agent.md):**
- A5: CMS-1500 OCR text pre-extracted by clearinghouse before reaching Intake Agent; no OCR step needed in-agent. If wrong: must add Tesseract/cloud-OCR step, increasing Tier 2 complexity. **Medium confidence.**
- A6: OCR failure rate ~5% for CMS-1500 (claim → PARSE_FAILED). No measured baseline. Drives PARSE_FAILED queue staffing estimate. **Low confidence.**
- A7: Haiku extraction accuracy ≥ 95% for email and fax formats. If wrong: Tier 3 PARSE_FAILED rate rises; may need Sonnet fallback (10× cost) or human review queue. **Low confidence.**
- A8: Intake Agent processes claims synchronously at ~4 claims/min. 2,000 claims/day ÷ 8 hours = adequate. If throughput requirement rises, queue-worker pattern needed. **High confidence.**
- A9: `X-Submitter-NPI` header present in all email submissions. If absent: provider_npi defaults to "UNKNOWN_NPI" for all email claims, degrading code validity. **Medium confidence.**

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
| `Gate5a-Capstone-Participant-Pack.md` | **Canonical gate instructions** — deliverables, defense format, rubric, choreography |
| `Capstone-A-Claims-Pack/README.md` | Mock data pack — 2,000 synthetic claims across 8 intake formats; prototype fixture source |

---

## Section 6b: Gate5a Rubric (visible up front — use to guide all decisions)

**Source:** `Gate5a-Capstone-Participant-Pack.md` §6. This is the one gate where the full rubric is released at the start.

**Pass threshold: 78+ overall, with no individual criterion scoring below 60%.**

| Criterion | Weight | What it demands |
|-----------|-------:|-----------------|
| Solution is AI-native with justified delegation architecture | 15% | Agents making real decisions with justified delegation boundaries — not a rules engine |
| Specifications are production-grade (buildable by an AI coding agent) | 15% | Precise enough for Claude Code to build from with few/no clarifying questions |
| Economics model is credible and the business case closes | 15% | Realistic token costs, ROI positive under conservative assumptions, multi-model routing justified |
| Cognitive work assessment reflects lived process | 5% | Maps the actual work, not the org chart |
| Architecture decisions show sound judgment | 5% | ADRs with trade-off analysis and rejected alternatives |
| Stakeholder alignment shows professional judgment | 5% | Names real tensions (from `capstone-stakeholder-tensions.md`), defensible trade-off recommendation |
| Scope discipline | 5% | No silent scope creep or scope reduction; known gaps beat hidden gaps |
| Validation plan is comprehensive | 5% | Covers accuracy, edge cases, failure modes, compliance — not happy-path only |
| **Working prototype: correctness and faithfulness to spec** | **15%** | Runs on mock data; faithful to the spec; happy path + escalation + edge case all working |
| **Live demo quality** | **5%** | Running code, not narrated slides; under 5 minutes; three paths shown |
| Verbal defense quality (Q&A + curveball) | 10% | Composure and specificity on the curveball; honest about demo-vs-production gap |

**Automatic fail indicators (any one fails the gate regardless of total score):**
- Built a traditional rules engine instead of an agentic solution
- Failed to distinguish what should be agentic from what should stay human
- **Prototype does not run at all during the live demo**
- Narrated slides instead of demoing running code
- Validation is happy-path only with no failure-mode coverage

**Where we stand against the rubric:**
- AI-native + delegation: ✓ D3 autonomy matrix, ADRs, hard HITL stops documented
- Specifications production-grade: ✓ WS1 + WS2 specs complete; WS1 proven buildable by the C12 prototype; Intake Agent spec (D4c) added; canonical normalized claim record (D4_canonical_claim_record.md) derived from real Claims Pack data and adopted as the WS1 input contract
- Economics model: ✓ D2D complete with sensitivity analysis and multi-model routing
- Cognitive work assessment: ✓ D2A complete
- Architecture decisions: ✓ ADR-1, ADR-2, ADR-3 in D3 §4
- Stakeholder alignment: ✓ C10 complete
- Scope discipline: ✓ Tier 1 intake (EDI 837P/I + Portal JSON) built and empirically validated; CMS-1500 OCR deferred with documented rationale; WS2 and Wave 2+ explicitly deferred
- Validation plan: ✓ D7 complete — Pass 1 (5 scenario fixtures, all PASS) + Pass 2 (corpus validation: 6/6 assertions, 0 violations across 1,493 Tier 1 files) + §7 live classifier mini study (30-claim sample, 50% exact agreement, zero dangerous misses, key finding: classifier over-labels as uncertain on CPT/ICD mismatches — golden-set composition implication documented); D7A updated — §5 residual closed, §6 corpus diagnosis added
- Working prototype: ✓ 5/5 tests passing; happy path, escalation, governance hard stop all working; Pass 2 corpus run confirmed structural invariants hold at population scale
- Live demo quality: ⚠ Demo script needed — `run_claim.py` + `review_claim.py` are the tools
- Verbal defense: ⚠ Prep needed — key probe is "what would break this in production?"; live classifier mini study gives a concrete honest answer: classifier over-labels uncertain on CPT/ICD mismatches (73% uncertain rate on 30-claim sample), golden-set calibration is the production risk, confidence threshold correctly gates auto-approval even when label is imprecise

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
| `agents/ws1_agent.py` | Main pipeline: T-01 through T-09 state machine, FM-A-5 hard stop, audit-first ordering, all EscalationPacket fields spec-compliant. Uses `claim.get("payer_id", "UNKNOWN")` (canonical field name) |
| `agents/__init__.py` | Package init |
| `tools/calibration.py` | CalibrationRecord 6-field startup validation; `startup_validate()`, `CalibrationError` |
| `tools/clinical_classifier.py` | `classify_clinical_content()` — returns `{classification, confidence, reasoning}` |
| `tools/eligibility.py` | `check_eligibility()` |
| `tools/code_validity.py` | `check_code_validity()` |
| `tools/prior_auth.py` | `check_prior_auth()` |
| `tools/fee_schedule.py` | `get_payment_amount()` |
| `tools/__init__.py` | Package init |
| `tools/intake/edi_parser.py` | EDI X12 837P + 837I parser; `parse_edi_837(raw, source_file="") -> NormalizedClaimInput dict`; hard-required: claim_id, procedure_codes, diagnosis_codes |
| `tools/intake/portal_json_adapter.py` | Portal-JSON → NormalizedClaimInput; `adapt_portal_json(raw, source_file="") -> dict`; hard-required: submission_id, service_lines, diagnoses |
| `tools/intake/cms1500_ocr_parser.py` | CMS-1500 OCR text parser (pre-extracted); `parse_cms1500_ocr(raw, source_file="") -> dict`; **not production-ready** — 41% PARSE_FAILED on full population; deferred (see C13) |
| `tools/intake/__init__.py` | Package init |
| `tests/test_ws1_pipeline.py` | 5 tests — all passing |
| `fixtures/CLAIM-ADMIN-01.json` | Happy path / threshold boundary fixture (canonical schema: `provider_npi`, `payer_id`, `source_format`, `source_file`, `intake_warnings`) |
| `fixtures/CLAIM-CLINICAL-01.json` | Clinical routing fixture (canonical schema) |
| `fixtures/CLAIM-UNCERTAIN-01.json` | Uncertain classification fixture (canonical schema) |
| `fixtures/CLAIM-ELIG-01.json` | Eligibility discrepancy fixture (canonical schema) |
| `run_claim.py` | CLI: run a single claim through WS1; `--fixture CLAIM-ADMIN-01` (from fixtures/) or `--file path/to/any.json` (any NormalizedClaimInput file, e.g. from normalized-tier1/) |
| `review_claim.py` | CLI: review a saved escalation file |
| `run_batch.py` | Batch runner: feed Claims Pack directory or pre-normalized cache through WS1; `--live` for real classifier; `--save-normalized DIR` caches parsed NormalizedClaimInput JSON; detects `normalized-*` directories and skips parsing entirely |
| `normalized-tier1/` | **Pre-parsed canonical cache** — 1,493 NormalizedClaimInput JSON files (all Tier 1 parseable claims). Use `--dir normalized-tier1` with run_batch.py or `--file` with run_claim.py to test WS1 without re-running any parser. |
| `DEMO.md` | 5-minute demo script: 3 paths + format coverage Q&A answer |
| `escalations/` | Directory for saved escalation JSON files |

### Test status — 2026-05-26

All 5 tests passing:

| Test | What it covers |
|------|---------------|
| `test_happy_path` | S-1: CLAIM-ADMIN-01, confidence 0.91, all stubs nominal → `status=approved`, `payment_amount=85.0`, 6 COMMITTED audit entries |
| `test_hitl_escalation` | CLAIM-CLINICAL-01, clinical classification confidence 0.94 → `status=escalated`, physician HITL queue (ET-01) |
| `test_uncertain_classification` | CLAIM-UNCERTAIN-01, uncertain classification confidence 0.48 → `status=escalated`, physician HITL queue (ET-02); confirms audit trail includes all steps up to routing |
| `test_eligibility_stub_returns_discrepancy_for_sentinel` | Eligibility stub unit test — sentinel `member_id=GHS-MBR-INVALID` → `status=discrepancy` (stub wiring check, not a full pipeline path) |
| `test_governance_hard_stop` | S-3: FM-A-5 hard stop — state corrupted to ROUTING after ADMIN_CLEARED → ET-07 fires with `GOVERNANCE_VIOLATION`, `payment_amount` absent, `claim_state_at_escalation` preserved (not overwritten to PENDING_HITL_EXCEPTION) |

### Resolved spec gaps

| Gap | Description | Resolution | Applied to |
|-----|-------------|------------|------------|
| GAP-10 | REQ-A-6(c) contradicted §7 ET-07: spec said state → PENDING_HITL_EXCEPTION for governance violation, but diagnostic value is the incoming state | Leave state unchanged; `preserve_state=True` on governance-violation ET-07 call | `D4a_capability_spec.md` REQ-A-6, `ws1_agent.py` `_fire_et07` |
| GAP-14 | ET-07 `trigger_type` enum only had `AUDIT_FAILURE`; governance hard-stop needs a distinct type | Add `GOVERNANCE_VIOLATION` to `EscalationPacket.trigger_type` enum | `D4_preamble_capability_spec.md` enum, `D4a_capability_spec.md` outputs table + ET-07 action column |
| D7A residual | ET-07 `required_resolution` text said "Audit failure" even when `trigger_type = GOVERNANCE_VIOLATION`, giving exception processor contradictory signals | Split into two strings; `_fire_et07` selects by `trigger_type` | `D4a_capability_spec.md` §7 required_resolution table (two rows for ET-07), `ws1_agent.py` `_fire_et07` conditional |
| C13 field alignment | Prototype fixtures and adapters used `plan_id`, `provider_id`, `submission_format` — not aligned with canonical record derived from Claims Pack sampling | Rename: `plan_id` → `payer_id`, `provider_id` → `provider_npi`, `submission_format` → `source_format`; add `source_file` and `intake_warnings` fields; update `ws1_agent.py` to use `claim.get("payer_id", "UNKNOWN")`; update `D4a_capability_spec.md` §2 input contract and all decision logic references | All 4 fixtures, `edi_parser.py`, `portal_json_adapter.py`, `ws1_agent.py`, `D4a_capability_spec.md` |

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
