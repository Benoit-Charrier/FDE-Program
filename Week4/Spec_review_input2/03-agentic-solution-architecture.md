# Agentic Solution Architecture — MedFlex Shift Matching

> Deliverable for ATX Phase 3: Delegation Qualification.
> Input: `specs/cognitive-load-map.md` (6 JtDs, 20 micro-tasks).
> Assumption IDs reference `specs/assumptions.md`; new assumptions A19–A20 added in this session.

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Delegation Qualification Framework](#2-delegation-qualification-framework)
3. [Delegation Suitability Matrix](#3-delegation-suitability-matrix)
   - 3.1 [JtD-1 — Shift Intake Parsing](#31-jtd-1--shift-intake-parsing)
   - 3.2 [JtD-2 — Candidate Search & Evaluation](#32-jtd-2--candidate-search--evaluation)
   - 3.3 [JtD-3 — Match Selection](#33-jtd-3--match-selection)
   - 3.4 [JtD-4 — Submission](#34-jtd-4--submission)
   - 3.5 [JtD-5 — Confirmation & Conflict Resolution](#35-jtd-5--confirmation--conflict-resolution)
   - 3.6 [JtD-6 — No-Show Management](#36-jtd-6--no-show-management)
4. [Archetype Summary](#4-archetype-summary)
5. [Trade-off Analysis](#5-trade-off-analysis)
6. [Architecture Implications](#6-architecture-implications)

---

## 1. Executive Summary

The MedFlex coordinator workflow decomposes into six JtDs with meaningfully different delegation profiles. Three findings shape the MVP architecture:

**Finding 1 — JtD-2 and JtD-4 are unconditionally agentic.** Candidate search and submission are deterministic, structured, and fully API-accessible. Automating them removes the operational bulk of coordinator time and the primary source of fill-time latency — independently of whether the ranker performs well.

**Finding 2 — JtD-3 (Match Selection) is the highest-value, hardest delegation target.** Two dimensions score Low (decision determinism, context complexity) because the ranking logic is undocumented and tacit (A18). MVP design must be Agent-led + Human Oversight (coordinator approves the ranker shortlist at BP4), with a clear upgrade path to Fully Agentic as labeled outcome data accumulates (A19). Skipping the HITL guard in MVP would risk a third AI failure (C2, R1).

**Finding 3 — Exception paths are not MVP delegation targets.** JtD-5 conflict resolution and JtD-6 no-show management score multiple Low dimensions simultaneously (input structure, tool coverage, risk). These tasks require human judgment by design; agent value here is data surfacing and structured intake, not autonomous action.

**Critical path to <1h fill time**: Automating JtD-1 (parsing) + JtD-2 (search) removes the queue accumulation and search delay that drives 4.2h fills. JtD-3 HITL at BP4 adds only ~2 minutes. Fill time target is achievable with three JtDs automated and one HITL gate — not requiring full autonomy.

**6-week board demo milestone** *[Rev. 2026-05-13 — CEO Pushback]*: The 6-week delivery scope includes JtD-1 through JtD-4 and JtD-5a (MT-5.1/5.2). Feature 5 (proactive Shift Confirmation Notifier) is the only item deferred to Wave 2. The rule-based ranker (T4) enables JtD-1 and JtD-3 to develop in parallel by locking the parser output schema at end of week 1 — the ranker data model builds against this locked interface, not a completed parser. JtD-3 and JtD-4 share the ServiceNow write API credential (A11-write): both are gated on a single provisioning event by end of week 3.

---

## 2. Delegation Qualification Framework

Suitability is scored per JtD on seven dimensions. Scores reflect delegation readiness, not task importance.

| Dimension | High suitability | Low suitability |
|---|---|---|
| **Input structure** | Structured, machine-readable | Unstructured, ambiguous, requires interpretation |
| **Decision determinism** | Clear rules, predictable outputs | Judgment-dependent, contextual, implicit |
| **Tool coverage** | APIs available or buildable | Inaccessible, black-box, or manual |
| **Context complexity** | State can be made explicit | Requires institutional knowledge or relationship history |
| **Exception rate** | Rare, predictable exceptions | Frequent, unpredictable edge cases |
| **Latency constraint** | Batch or async acceptable | Real-time, sub-second response required |
| **Risk/compliance** | Reversible, low consequence | Irreversible, regulated, high-consequence |

**Archetype thresholds** (from ATX Phase 3):
- **Human Only**: ≥3 Low dimensions, especially risk/compliance and decision determinism
- **Human-led + Automation Support**: deterministic sub-tasks automated; judgment stays human
- **Human-led + Agent Support**: agent synthesizes and recommends; human decides
- **Agent-led + Human Oversight**: agent acts; human reviews or approves high-stakes outputs
- **Fully Agentic**: all dimensions Medium or High; volume justifies full delegation

---

## 3. Delegation Suitability Matrix

---

### 3.1 JtD-1 — Shift Intake Parsing

**Micro-tasks**: MT-1.1 (queue triage), MT-1.2 (specialty/schedule parse), MT-1.3 (credential extraction), MT-1.4 (confidence routing)

| Dimension | Score | Rationale |
|---|:---:|---|
| Input structure | L | Free-text hospital requests with no schema; inconsistent formats across email, portal, and phone transcriptions |
| Decision determinism | M | Specialty and credential code mapping follows domain rules (largely teachable); ambiguous requests require hospital clarification |
| Tool coverage | M | ServiceNow webhook/polling is buildable (A11); LLM parsing is feasible at ≥85% accuracy (A10); confidence-threshold routing requires new build |
| Context complexity | M | Domain vocabulary (specialty shorthand, credential names) is encodable in system prompt; no deep institutional knowledge required |
| Exception rate | M | ~15% of parses expected below confidence threshold (A10); non-standard or incomplete requests require escalation (BP1) |
| Latency constraint | M | LLM processing in 2–5 seconds is acceptable for <1h target; sub-second not required |
| Risk/compliance | M | Parse errors propagate to credential mismatches downstream (currently 7%); moderate consequence; recoverable via BP1 human review |

**Archetype**: **Agent-led + Human Oversight**

**Rationale**: The LLM parser runs autonomously on all inbound requests. High-confidence parses proceed to JtD-2 automatically (BP2). Low-confidence parses route to the human review queue (BP1) — coordinator clarifies with hospital and corrects. The only human action is exception resolution, not routine parsing. This directly attacks the first manual step driving fill-time latency (A16: ~35% of coordinator active work).

**Anti-pattern check**: Not a candidate for static rules or RPA. The free-text format (confirmed in discovery: "free text, free text") requires non-deterministic NLP. Templated intake forms would improve accuracy but require hospital behavior change — excluded from MVP scope.

**Parser output schema lock** *[Rev. 2026-05-13 — CEO Pushback]*: The parser JSON output contract (fields: shift_request_id, specialty_code, datetime_start, datetime_end, location_id, credentials[], confidence_score) must be frozen at end of week 1. JtD-2 (candidate search) and JtD-3 (ranker) build against this schema as a stable interface — parallel development in weeks 1–2 requires the schema to be fixed before ranker data model work begins. Schema changes after week 1 break the ranker integration contract and are a named project risk.

---

### 3.2 JtD-2 — Candidate Search & Evaluation

**Micro-tasks**: MT-2.1 (specialty query), MT-2.2 (availability filter), MT-2.3 (credential expiry), MT-2.4 (proximity scoring), MT-2.5 (hospital preference lookup)

| Dimension | Score | Rationale |
|---|:---:|---|
| Input structure | H | Structured requirement object from JtD-1; nurse profiles contain structured credential fields, availability windows, and location data |
| Decision determinism | H | MT-2.1–2.4 are binary or algorithmic filters; credential expiry is a structured date comparison; proximity is a distance calculation |
| Tool coverage | M | ServiceNow nurse database requires API build (A11); proximity requires geocoding API (low build effort); hospital preference is partially structured (A12) |
| Context complexity | M | MT-2.5 hospital preference history has data gaps (A12: completeness unconfirmed); missing preference records require fallback logic, not judgment |
| Exception rate | M | Stale availability records (~15–20%, A17) cause false positives — candidate appears available but cannot attend; agent must handle gracefully |
| Latency constraint | M | Structured DB query + proximity calculation completes in <5 seconds; not sub-second |
| Risk/compliance | M | MT-2.3 (credential expiry) carries compliance significance; but it is fully deterministic — expiry date is a structured field on the nurse card (confirmed in discovery) |

**Archetype**: **Fully Agentic**

**Rationale**: MT-2.1 through MT-2.4 are deterministic filters with no judgment required. MT-2.5 is a structured lookup with a fallback (if preference data is missing, fall back to MT-2.4 proximity ranking). The combination of six M/H suitability scores and high volume (~184 fills/day requiring ~5 candidate evaluations each = ~920 filter operations/day, A2, A4) makes full automation both safe and economically mandatory. The stale availability issue (A17) is handled via re-queue logic when a candidate fails an availability confirmation — not a reason to add human oversight.

**Anti-pattern check**: MT-2.1–2.4 could theoretically be implemented as a simple SQL query + rules engine without an agent. However, coordinating across five data sources (credential DB, availability, proximity, hospital preference history), handling missing/stale records, and producing a ranked pool with per-candidate confidence flags benefits from an orchestrating agent that can branch on intermediate results.

---

### 3.3 JtD-3 — Match Selection

**Micro-tasks**: MT-3.1 (multi-factor ranking), MT-3.2 (tacit knowledge application), MT-3.4 (submit vs. escalate decision)

| Dimension | Score | Rationale |
|---|:---:|---|
| Input structure | M | Structured candidate pool as input; but ranking criteria are undocumented and vary across 8 coordinators |
| Decision determinism | L | Ranking weights are undocumented; MT-3.2 (tacit knowledge) is entirely unencoded; "feeling" cannot be extracted from coordinator behavior without labeled training data (A18) |
| Tool coverage | L | No API encodes senior coordinator pattern recognition; historical outcome data needed to train a ranking model (A19) — completeness unconfirmed |
| Context complexity | L | Senior coordinators' 10-year institutional knowledge (A18) — hospital specialization, nurse relationship history, competitive timing — is the core decision asset; entirely absent from current systems |
| Exception rate | M | Borderline and escalation cases estimated at 10–20% of total matches (MT-3.4 routing) |
| Latency constraint | M | Ranker scoring in seconds is acceptable; coordinator review at BP4 adds ~2 minutes |
| Risk/compliance | M | Wrong selection = reputational risk + potential relationship damage (no direct financial consequence confirmed); reversible via hospital rejection |

**Archetype (MVP)**: **Agent-led + Human Oversight**

**Archetype (Phase 2, post-training)**: **Fully Agentic** (progressive as ranker accuracy increases)

**Rationale**: Three suitability dimensions score Low (decision determinism, tool coverage, context complexity), disqualifying Fully Agentic for MVP. The agent provides a scored and ranked shortlist of 1–3 candidates with explanation; the coordinator reviews at BP4 and approves or edits before submission. This is the natural HITL boundary identified in the cognitive load map.

The upgrade path is data-driven: as the ranker accumulates labeled selections + outcomes (A19), model accuracy improves and the confidence threshold for auto-submit can be progressively lowered. Marcus explicitly delegated the HITL decision to FDE expertise (A13), and both of his stated concerns — matching accuracy and coordinator adoption — are directly addressed by starting with human oversight.

**Anti-pattern check**: Not a candidate for static RPA. The tacit knowledge in MT-3.2 (A18) is the primary source of senior coordinator speed advantage; fully replicating it in Phase 2 requires ML, not rules. The MVP rule-based ranker is an explicit, time-bounded choice — it captures the deterministic dimensions of ranking (credential compliance, availability confidence, proximity, preference history weight per A25) and produces a credible shortlist for coordinator review. It does not learn and will plateau at a fixed accuracy ceiling. The ML upgrade in Phase 2 is a qualitatively different capability — it replaces the scoring function with a learned model trained on coordinator decisions and submission outcomes (A19), not merely an incremental accuracy improvement on the same algorithm.

**MVP implementation note** *[Rev. 2026-05-13 — CEO Pushback]*: The MVP ranker is deterministic and does not require agent orchestration for the scoring step itself — it is a weighted formula (A25). It is included in the unified agentic pipeline (not as a standalone script) to share the event-driven architecture, audit trail, and ServiceNow integration layer with JtD-1, JtD-2, and JtD-4. The label "Agent-led + Human Oversight" describes the delegation pattern (agent ranks, coordinator approves at BP4), not the technical implementation of the scoring function.

---

### 3.4 JtD-4 — Submission

**Micro-tasks**: MT-4.1 (format, submit & log)

| Dimension | Score | Rationale |
|---|:---:|---|
| Input structure | H | Structured approved-candidate object from JtD-3; templated hospital-facing submission format |
| Decision determinism | H | Pure execution; no judgment; format → submit → log |
| Tool coverage | M | ServiceNow write API required (A11); standard licensed capability; requires provisioning |
| Context complexity | H | No institutional knowledge required; deterministic mapping to submission template |
| Exception rate | L | Rare failures (API error, duplicate submission); handled by standard retry/error logging |
| Latency constraint | M | Seconds acceptable after coordinator approval event at BP4 |
| Risk/compliance | M | Submission is the revenue-generating action; errors are recoverable (submission can be retracted before hospital confirms); not regulated |

**Archetype**: **Fully Agentic**

**Rationale**: Six of seven dimensions score M or H. MT-4.1 is the clearest fully-agentic candidate in the workflow. After coordinator approval at BP4, submission fires automatically with a full event audit trail (parse → rank → review → submission timestamps), enabling precise M1 measurement.

**Anti-pattern check**: This is structurally an RPA task (format + API call). It is included as an agent step rather than a standalone script to maintain a unified event-driven architecture and shared audit trail with JtD-1–3. A separate submission script would fragment observability and make re-entry (BP5 rejection cycle, BP6 emergency re-fill) harder to coordinate.

---

### 3.5 JtD-5 — Confirmation & Conflict Resolution

JtD-5 has two structurally different sub-tasks that warrant separate archetype assignments.

#### Sub-task A — Monitoring & Notification (MT-5.1, MT-5.2)

| Dimension | Score | Rationale |
|---|:---:|---|
| Input structure | H | Binary hospital response (accepted/rejected); notification is templated |
| Decision determinism | H | Accepted → notify nurse; rejected → return to JtD-3 (BP5); no judgment |
| Tool coverage | M | ServiceNow polling/webhook buildable; notification system exists (A14) |
| Context complexity | H | No institutional knowledge required; event-driven routing |
| Exception rate | M | Hospital non-response requires follow-up; rejection triggers re-rank cycle |
| Latency constraint | M | Response polling on short intervals (minutes) is sufficient |
| Risk/compliance | M | Notification accuracy matters for nurse trust; recoverable errors |

**Archetype (MT-5.1/5.2)**: **Fully Agentic**

#### Sub-task B — Decline & Multi-Agency Conflict (MT-5.3, MT-5.4)

| Dimension | Score | Rationale |
|---|:---:|---|
| Input structure | L | Nurse decline requires inbound phone call (no API); multi-agency conflict discovered reactively (no cross-agency visibility) |
| Decision determinism | L | Conflict resolution depends on timing, nurse relationships, and competitive dynamics; no rule set applies |
| Tool coverage | L | No cross-agency coordination API exists; nurse decline has no structured inbound channel (A14 low confidence); conflict detected post-facto |
| Context complexity | L | Requires knowledge of competitive landscape, nurse relationship history, and shift urgency — all unencoded |
| Exception rate | M | ~12% no-show rate includes conflict-driven subset (A9: ~60% of no-shows attributable to passive model + competitive poaching) |
| Latency constraint | L | Time-sensitive — shift window may be closing; sub-hour recovery required |
| Risk/compliance | H | Hospital relationship and patient care continuity at risk; partially irreversible once shift window closes |

**Archetype (MT-5.3/5.4)**: **Human-led + Agent Support**
- Agent surfaces relevant data on trigger: nurse's prior no-show history, available replacement candidates (re-entry to JtD-2), shift timeline status, competing submissions in-flight (A20)
- Human coordinator makes the conflict resolution decision and initiates replacement if needed

**Overall JtD-5 Archetype**: **Human-led + Agent Support** (with fully-agentic sub-path for routine monitoring)

**Rationale**: Sub-task B has three Low-scoring dimensions including risk/compliance and two infrastructure gaps (no decline API, no cross-agency visibility) that cannot be resolved within the 8-week engagement. Attempting to automate MT-5.3/5.4 would require building capabilities that do not exist (inbound structured nurse response, cross-agency deconfliction) and introduce high-consequence errors in low-headroom situations. The safe design is an agent that arms the coordinator with structured data and candidate alternatives, not one that acts autonomously under conflict conditions.

**Wave 1 scope boundary** *[Rev. 2026-05-13 — CEO Pushback]*: MT-5.1 (hospital response monitoring) and MT-5.2 (initial nurse placement notification) are in the 6-week MVP. Proactive T-48h/T-24h nurse confirmation — Feature 5 (Shift Confirmation Notifier) — is deferred to Wave 2. Feature 5 depends on U4 (whether the notification infrastructure supports bidirectional response capture, not just one-way notifications), which is unresolved within the 6-week window. No-show reduction (M4) is tracked in Wave 1 through MT-5.1/5.2 outcome logging; the M4 intervention (Feature 5) is Wave 2.

---

### 3.6 JtD-6 — No-Show Management

**Micro-tasks**: MT-6.1 (reactive intake), MT-6.2 (profile update + offboard threshold), MT-6.4 (emergency re-fill)

| Dimension | Score | Rationale |
|---|:---:|---|
| Input structure | L | Hospital reports no-show via inbound phone call; no structured API for intake |
| Decision determinism | M | Profile update rule is partially defined ("too many no-shows → offboard"); MT-6.2 is automatable if threshold is encoded; MT-6.4 re-entry to JtD-1–4 follows a known pattern |
| Tool coverage | M | ServiceNow profile write via API feasible (A11); MT-6.4 re-entry re-uses JtD-1–4 agent pipeline; no automation for MT-6.1 phone intake |
| Context complexity | M | Offboard threshold is informal (confirmed in discovery: "we offboard them if we see it happening too often") — encodable once threshold is defined |
| Exception rate | M | ~12% no-show rate; subset involves concurrent competitive conflicts (A9, A20) |
| Latency constraint | L | Emergency re-fill is time-critical — shift window may have <2 hours remaining |
| Risk/compliance | H | Patient care continuity; hospital relationship; repeated no-shows have commercial consequences (discount given to at least one client, per discovery) |
| | | |

**Archetype**: **Human-led + Automation Support**

**Rationale**: MT-6.1 cannot be automated — it is triggered by an inbound hospital phone call with no structured API. The coordinator receives the call, logs the incident, and the agent takes over for the downstream structured work: MT-6.2 (profile update, check offboard threshold) and MT-6.4 (priority re-entry to the JtD-1–4 pipeline with urgency flag and reduced candidate pool).

The two Low-scoring dimensions (input structure, latency constraint) combined with High risk/compliance preclude anything beyond automation support for this JtD. The emergency re-fill is the highest-stress task in the workflow (MT-6.4: CL:H, TT:H, LC:H) and executes under time constraints that reduce the coordinator's ability to catch agent errors — a further reason for human-in-the-loop throughout.

**Anti-pattern check**: MT-6.2 threshold enforcement is a candidate for simple rules once the offboard threshold is numerically defined. No agent is needed for that specific sub-step; it is included here because it sits within a broader exception-handling JtD where context switching between sub-tasks benefits from orchestration.

---

## 4. Archetype Summary

| JtD | Name | MVP Archetype | Phase 2 Target | Primary Constraint |
|---|---|---|---|---|
| JtD-1 | Shift Intake Parsing | Agent-led + Human Oversight | Agent-led + Human Oversight (stable) | Free-text input structure (L); 15% exception rate |
| JtD-2 | Candidate Search & Evaluation | Fully Agentic | Fully Agentic | Stale availability data (A17); API provisioning (A11) |
| JtD-3 | Match Selection | Agent-led + Human Oversight | Fully Agentic (progressive) | Unencoded tacit knowledge (A18); training data dependency (A19) |
| JtD-4 | Submission | Fully Agentic | Fully Agentic | ServiceNow write API (A11) |
| JtD-5 | Confirmation & Conflict Resolution | Human-led + Agent Support | Human-led + Agent Support (stable for conflict path) | No decline API; no cross-agency visibility; high-consequence errors |
| JtD-6 | No-Show Management | Human-led + Automation Support | Human-led + Automation Support (stable) | Phone intake; emergency time constraints; High risk/compliance |

**Throughput impact by archetype**:
- Fully Agentic JtDs (JtD-2, JtD-4, MT-5.1/5.2): These run without coordinator action; the throughput ceiling is system capacity, not human capacity.
- Agent-led + Human Oversight JtDs (JtD-1 for exceptions, JtD-3): Coordinator action is required only for the review step; time per match drops from ~20 min (A1) to ~2 min at BP4.
- Human-led JtDs (JtD-5 conflicts, JtD-6): Coordinator load is unchanged but is scoped to genuine exception cases, freeing capacity for the high-volume standard path.

---

## 5. Trade-off Analysis

### T1 — JtD-3 MVP HITL vs. Fully Agentic at Launch

**Option A (Selected): Agent-led + Human Oversight**
- Coordinator reviews ranked shortlist at BP4; adds ~2 min per match
- Preserves coordinator trust and job role in MVP (addresses C2, R1)
- Captures coordinator approval decisions as training signal for ranker improvement (A19)
- Risk: Throughput multiplier is smaller (~10× per coordinator vs. theoretical ~50×+ fully agentic)

**Option B (Deferred): Fully Agentic from day 1**
- Eliminates coordinator review step; maximum throughput immediately
- Risk: Third AI failure — Marcus explicitly cited accuracy and coordinator adoption as the two red flags (A13); no training data at launch means ranker accuracy is below coordinator level initially
- Risk: Reputational errors with hospitals are not recoverable within the engagement window
- **Decision: Option A. The 2-minute overhead per match is acceptable given the failure risk of Option B.**

### T2 — JtD-1 Parsing: LLM vs. Structured Intake Overlay

**Option A (Selected): LLM parser on existing free-text input**
- Hospital behavior unchanged; no new submission channel required
- Risk: Accuracy ceiling determined by input ambiguity; sub-85% accuracy requires higher human review rate
- Contingency: If accuracy is below threshold after pilot, propose structured intake template for high-volume hospital partners (out of MVP scope, see `specs/2-engagement-intake-and-scope-definition.md`)

**Option B (Deferred): Structured intake form replacing free text**
- Higher parser accuracy; simpler downstream processing
- Risk: Requires hospitals to change submission behavior; may require commercial negotiation; estimated 2–3 weeks additional MVP timeline
- **Decision: Option A for MVP. Option B as Phase 2 enhancement for high-volume hospital partners.**

### T3 — JtD-2 Stale Availability (A17): Speed vs. Accuracy

**Option A (Selected): Trust availability records; handle staleness reactively**
- Agent queries availability as displayed; re-queues candidate on contact failure
- Faster candidate pool generation; minor re-work when stale record surfaces
- Risk: 15–20% of records may be stale (A17); false positives in candidate pool

**Option B: Freshness check before including candidate in pool**
- Agent pings nurse for availability confirmation before shortlisting
- Lower false-positive rate; increases nurse-facing notification volume
- Risk: Adds latency to candidate pool generation; degrades fill-time metric
- **Decision: Option A. Stale availability is a recoverable failure; latency is not.**

### T4 — JtD-3 Ranker Cold-Start: Rule-Based vs. ML

**Option A (Selected): Rule-based ranker with deterministic scoring at launch** *[Rev. 2026-05-13 — CEO Pushback]*
- **Time independence**: Implementable in 1–2 weeks — no training data pipeline required. A 6-week board demo cannot wait for the 3+ months of live coordinator decisions needed to train A19. The rule-based ranker runs on structured ServiceNow data that exists today.
- **Data independence**: Not blocked by A19 (labeled training data availability) — which is unconfirmed at engagement start. A rules-only ranker runs on day 1 of production while the labeled feedback corpus accumulates.
- Scores on: credential match score, availability confidence, proximity, preference history weight (A25)
- Lower accuracy than a trained ML model; no personalization for hospital-specific implicit preferences; fixed accuracy ceiling
- Provides immediate value and begins accumulating the labeled coordinator decisions that will train the Phase 2 model

**Option B: ML ranker at launch**
- Higher accuracy potential; can replicate tacit knowledge (A18) if training data is sufficient and structurally correct
- Risk: Dependent on A19 (labeled data availability) — if data is insufficient or unstructured, launch is blocked or accuracy is unpredictably poor
- Risk: Training pipeline adds 3–4 weeks minimum (data cleaning, model training, evaluation, deployment) — incompatible with 6-week window
- **Decision: Option A at launch (rule-based), with ML upgrade in Phase 2 once A19 is validated and ~3 months of labeled data is accumulated.**

**Why the ML upgrade is a qualitative leap, not an incremental improvement** *[Rev. 2026-05-13 — CEO Pushback]*: The rule-based ranker applies explicit, static weights (A25) to structured signals. The ML ranker replaces the scoring function entirely with a model that learns implicit patterns — hospital-specific coordinator behaviors, nurse-hospital relationship signals, seasonal demand patterns — that are not encodable as rules. Phase 2 is not "tune the weights on the same algorithm"; it is a different technical architecture (learned model vs. deterministic formula) targeting the tacit knowledge gap (A18) that the rule-based ranker deliberately does not address.

---

## 6. Architecture Implications

Four structural implications follow from the delegation assignments above:

**1. BP2 is the pipeline gate**: The shift intake parser (JtD-1) produces the structured object that enables all downstream automation. If the parser fails or routes to human review, JtD-2 through JtD-4 cannot proceed for that request. Parser reliability and confidence-threshold calibration are the most critical operational parameters in the system — not the ranker. The parser output schema must be locked at end of week 1 to enable parallel JtD-3 ranker development (see Section 3.1 schema lock constraint). *[Rev. 2026-05-13 — CEO Pushback]*

**2. BP4 is the designed HITL boundary for MVP**: All fully-agentic downstream work (submission, notification, hospital response monitoring) depends on a single coordinator approval action. This design concentrates human labor at one point, maximizes automation above and below it, and provides a clean audit trail. The boundary is designed to move: as JtD-3 ranker accuracy improves, the confidence threshold for auto-approval can be raised progressively without re-architecting the pipeline.

**3. JtD-3 requires a labeled feedback loop from day 1**: The rule-based ranker selected for MVP (T4) must log coordinator approval/edit decisions and submission outcomes to build the training corpus (A19). This is not optional — without the feedback loop, the upgrade path to ML ranking in Phase 2 is blocked. The coordinator review interface (MVP Feature 3) must capture: ranked shortlist presented, coordinator's final selection, whether coordinator edited the ranking, and submission outcome.

**4. Exception paths must be isolated from the standard pipeline**: JtD-5 conflict resolution and JtD-6 no-show management both involve partial re-entry to JtD-1–4 (BP5 rejection cycle, BP6 emergency re-fill). These re-entry paths must operate on a priority queue that does not block or delay standard in-flight requests. A shared queue without priority routing would cause exception handling to increase queue depth for new requests — compounding the latency problem the system is designed to solve.

**5. ServiceNow write API is a shared go/no-go gate for JtD-3 and JtD-4** *[Rev. 2026-05-13 — CEO Pushback]*: The coordinator review interface (Feature 3, JtD-3 approval event) and automated submission (Feature 4, JtD-4) both require ServiceNow write API credentials (A11-write). This is a single dependency with a shared provisioning event — not two sequential dependencies. If write credentials are not available by end of week 3, Features 3 and 4 are blocked simultaneously. The write credential is a distinct, higher-privilege request from the read credential (A11-read) needed by JtD-1 and JtD-2. Both must be requested from the ServiceNow admin contact explicitly and separately.

---

*See `specs/assumptions.md` for all assumptions referenced in this document (A1–A20).*
