# D2B: Delegation Suitability Matrix
**Engagement:** Greenfield Health Systems — Medical Claims Adjudication Transformation
**Phase:** ATX Assessment Phase 3 — Delegation Qualification
**Prepared:** 2026-05-20
**Source of truth:** `Scenario/scenario_context.md`; informed by `Deliverables/D0C_discovery.md`, `Deliverables/D2A_cognitive_load_map.md`, `Deliverables/C1_problem_framing.md`

---

## 0. Executive Summary

- **Delegation architecture:** Of the 12 JtDs scored, 4 are assigned to the autonomous backbone (Fully Agentic) handling structured execution work; 4 are assigned Agent-led + Human Oversight governing administrative adjudication and clinical content classification; and the governance constraint imposed by URAC/NCQA accreditation enforces one hard Human Only assignment and two Human-led + Agent Support assignments — producing an architecture where agents handle the rule-bound throughput layer while humans retain ownership of every judgment that carries clinical, legal, or compliance consequence.
- **Most contested archetype assignment:** WS1-JtD-3 (payment determination, suitability score 4/7) is the strongest candidate for Fully Agentic in the engagement — the standard fee schedule path is deterministic, exception frequency is low, and this is the most structurally clean automation target — but it is assigned Agent-led + Human Oversight because contract exception rules are not confirmed to be encoded in accessible systems (Tool Coverage M; exception path has Tool Coverage L), and promoting this JtD to Fully Agentic before contract rules are confirmed encoded would create silent financial errors on a subset of claims.
- **Primary governance constraint:** WS2-JtD-3 (medical necessity determination) is Human Only — Dr. Marcus Webb's non-negotiable requirement (Exchange 2) that every claim with clinical content requires physician or advanced practice provider sign-off before finalisation is a URAC/NCQA accreditation condition that cannot be overridden by any classifier confidence level or agent accuracy metric; this constraint propagates upstream to WS1-JtD-2 and WS2-JtD-1, both of which must escalate to a HITL classification queue when classifier confidence falls below the configurable threshold, specifically to prevent the compliance violation of routing a clinical claim to the administrative payment path.

---

## 0b. Table of Contents

- [0. Executive summary](#0-executive-summary)
- [0b. Table of contents](#0b-table-of-contents)
- [1. JtD inventory](#1-jtd-inventory)
- [2. Delegation Suitability Matrix](#2-delegation-suitability-matrix)
- [3. Delegation archetype assignment with rationale](#3-delegation-archetype-assignment-with-rationale)
- [4. Delegation architecture summary](#4-delegation-architecture-summary)
- [5. Delegation boundary defence](#5-delegation-boundary-defence)
- [6. Assumption log](#6-assumption-log)

---

## 1. JtD Inventory

The following JtDs are taken directly from D2A §2b (WS1), §3b (WS2), and §5 (cross-cutting abbreviated work streams). No new JtDs are derived here.

### WS1 — Administrative Adjudication (D2A §2b)

| JtD ID | Work Stream | Cognitive contract |
|---|---|---|
| WS1-JtD-1 | WS1 | Determine whether a submitted claim is administratively valid — member eligible, codes correct and clinically plausible, prior authorisation present and matching — and produce a disposition: administratively complete / incomplete / pending provider response |
| WS1-JtD-2 | WS1 | Determine whether the validated claim contains clinical content requiring physician review, and route it to the correct downstream queue: administrative payment path or WS2 clinical review queue |
| WS1-JtD-3 | WS1 | Determine the correct payment amount for an administratively cleared claim — applying fee schedule, member cost-sharing, and duplicate check — and issue the payment approval decision |

### WS2 — Clinical Review (D2A §3b)

| JtD ID | Work Stream | Cognitive contract |
|---|---|---|
| WS2-JtD-1 | WS2 | Verify that a claim routed to clinical review was correctly classified as containing clinical content and that all required clinical context is present and accessible for physician review |
| WS2-JtD-2 | WS2 | Assemble the complete clinical context required for a physician to make a medical necessity determination without manual document hunting — producing a pre-filled review packet from diagnosis codes, prior auth history, clinical notes, and member history |
| WS2-JtD-3 | WS2 | Apply medical necessity criteria to the assembled clinical evidence and produce a signed physician determination (approve / deny / request additional information), with compliant documentation |

### Cross-Cutting Processes (D2A §5)

| JtD ID | Work Stream | Cognitive contract |
|---|---|---|
| INT-JtD-1 | Intake | Transform an inbound claim from its submission format (EDI 837, PDF, portal) into a structured record that WS1 processing can act on |
| INT-JtD-2 | Intake | Detect and flag intake anomalies — malformed submissions, missing required fields, duplicate or near-duplicate submissions — before processing begins |
| APP-JtD-1 | Appeals | Classify an inbound denial appeal by root cause — routing error, coding error, medical necessity error, or documentation gap — to guide the determination review |
| APP-JtD-2 | Appeals | Determine whether an original denial should be overturned in light of the appeal evidence and produce a final determination with documentation |
| QMG-JtD-1 | Queue Management | Ensure the processing queue is prioritised to avoid SLA breaches — escalating claims nearing the 7-day contractual penalty threshold before breach occurs |
| QMG-JtD-2 | Queue Management | Manage the pending-claims state — tracking claims awaiting provider response and re-queuing them promptly when documentation arrives |

---

## 2. Delegation Suitability Matrix

**Scoring key:**
- Input Structure, Decision Determinism, Tool Coverage: H = high suitability (1 pt each)
- Context Complexity, Exception Rate, Latency Constraint, Risk/Compliance: L = high suitability (1 pt each)
- Maximum score: 7/7
- *Risk/Compliance H independently gates against Fully Agentic regardless of total score; archetype assignment reflects both the suitability score and this constraint.*

| JtD | Work Stream | Input Structure | Decision Determinism | Tool Coverage | Context Complexity | Exception Rate | Latency Constraint | Risk/Compliance | Suitability Score | Delegation Archetype |
|---|---|---|---|---|---|---|---|---|---|---|
| WS1-JtD-1 | WS1 Admin | M | M | M | M | M | L ✓ | H | **1/7** | Agent-led + Human Oversight |
| WS1-JtD-2 | WS1 Admin | M | L | L | H | H | L ✓ | H | **1/7** | Agent-led + Human Oversight |
| WS1-JtD-3 | WS1 Admin | H ✓ | M | M | L ✓ | L ✓ | L ✓ | M | **4/7** | Agent-led + Human Oversight |
| WS2-JtD-1 | WS2 Clinical | H ✓ | M | M | M | M | L ✓ | H | **2/7** | Agent-led + Human Oversight |
| WS2-JtD-2 | WS2 Clinical | M | M | L | H | H | L ✓ | H | **1/7** | Agent-led + Human Oversight |
| WS2-JtD-3 | WS2 Clinical | M | L | M | H | H | L ✓ | H | **1/7** | **Human Only** |
| INT-JtD-1 | Intake | M | H ✓ | M | L ✓ | M | L ✓ | M | **3/7** | Fully Agentic |
| INT-JtD-2 | Intake | H ✓ | H ✓ | M | L ✓ | L ✓ | L ✓ | M | **5/7** | Fully Agentic |
| APP-JtD-1 | Appeals | M | M | M | H | H | L ✓ | H | **1/7** | Human-led + Agent Support |
| APP-JtD-2 | Appeals | M | M | M | H | H | M | H | **0/7** | Human-led + Agent Support |
| QMG-JtD-1 | Queue Mgmt | H ✓ | H ✓ | M | L ✓ | L ✓ | L ✓ | H | **5/7** | Fully Agentic |
| QMG-JtD-2 | Queue Mgmt | H ✓ | H ✓ | M | L ✓ | L ✓ | L ✓ | M | **5/7** | Fully Agentic |

---

**Dimension score justifications:**

**WS1-JtD-1 (administrative validation):** Input Structure M — structured claim data once normalised, but mixed intake formats create variability; Decision Determinism M — standard eligibility and prior auth lookups are deterministic (H), but coding plausibility judgment and prior auth partial match resolution are L, averaging to M; Tool Coverage M — eligibility, prior auth, and code lookup systems assumed available but unnamed (A-D0C-4), integration feasibility unconfirmed; Context Complexity M — three checks across multiple systems, bounded scope; Exception Rate M — coding plausibility and prior auth partial matches generate moderate exception volume per D2A (A-D2A-3, A-D2A-7); Latency Constraint L — 7-day SLA allows batch processing; Risk/Compliance H — errors in coding and prior auth are direct contributors to the 41% denial appeal overturn rate (scenario.md), and eligibility errors produce either wrongful denials or payment to ineligible claims. Score 1/7; assigned Agent-led + Human Oversight because the standard path is automatable but exception handling and the H risk dimension require a human backstop with authority to review flagged cases.

**WS1-JtD-2 (clinical content routing):** Input Structure M — diagnosis and procedure codes are structured; the classification signal is a pattern across structured inputs; Decision Determinism L — no formal clinical content criterion exists in the current process (scenario_context.md Assumption A-4); the classifier must be built and certified before this becomes codifiable; Tool Coverage L — no classifier tool exists today; the tool must be built as a prerequisite design output; Context Complexity H — the routing decision must synthesise diagnosis codes, procedure codes, and provider specialty as multi-factor inputs; Exception Rate H — without a formal criterion, every borderline case is an exception requiring HITL escalation; Latency Constraint L — batch processing acceptable within 7-day SLA; Risk/Compliance H — false negative (clinical claim routed as administrative) = URAC/NCQA compliance violation per Exchange 2. Score 1/7; assigned Agent-led + Human Oversight conditional on the clinical content criterion being formally defined and the classifier being certified by Dr. Webb's team. The 1/7 score reflects current-state prerequisites, not inherent impossibility.

**WS1-JtD-3 (payment determination):** Input Structure H — fee schedules and cost-sharing rules are structured tables with defined fields; Decision Determinism M — standard fee schedule path is deterministic (H); contract exception path requires informal institutional knowledge (L), averaging to M; Tool Coverage M — fee schedule system assumed available but unnamed; contract exception rules may reside in documents or email rather than in accessible data (A-D0C-6); Context Complexity L — standard path is straightforward fee schedule lookup with no complex context; Exception Rate L — contract exceptions are low-frequency in absolute volume per D2A (A-D2A-5, scored L in MT-WS1-10); Latency Constraint L — batch; Risk/Compliance M — payment errors are financially recoverable, not clinical compliance issues. Score 4/7; see contested assignment defence in Section 5.

**WS2-JtD-1 (clinical content verification):** Input Structure H — claim codes are structured; the claim has already been through WS1 normalisation; Decision Determinism M — in target state, a classifier with a configurable confidence threshold handles standard cases (M overall; not H because probabilistic); Tool Coverage M — shares the same classifier tool as WS1-JtD-2; once built, tool coverage improves; Context Complexity M — simpler than the original routing decision (claim has already passed administrative checks); Exception Rate M — low-confidence cases escalate to HITL; moderate exception rate expected; Latency Constraint L — claim is already in the physician queue; not real-time; Risk/Compliance H — routing error in either direction carries compliance or physician-time consequences. Score 2/7; assigned Agent-led + Human Oversight with the same classifier and confidence threshold design as WS1-JtD-2.

**WS2-JtD-2 (clinical context assembly):** Input Structure M — diagnosis and procedure codes are H; clinical documentation (physician notes, operative reports) is L/unstructured (D2A A-D2A-4); Decision Determinism M — structured retrieval is deterministic; handling missing or incomplete documentation requires judgment about whether to proceed or request more information; Tool Coverage L — clinical notes source system is unknown and unnamed (A-D0C-7); integration feasibility is the highest-risk unknown in the WS2 agent design; Context Complexity H — multi-source assembly from claim codes, prior auth history, clinical notes, and member history; Exception Rate H — clinical documentation is frequently incomplete, requiring provider follow-up (scored H for MT-WS2-2 in D2A); Latency Constraint L — physician reviews asynchronously; Risk/Compliance H — incomplete context assembly directly degrades physician determination quality; liability risk if physician makes a determination on insufficient evidence. Score 1/7; assigned Agent-led + Human Oversight because the agent's multi-source retrieval and synthesis capability at scale is the primary value proposition for WS2; the physician's review of the assembled packet provides the human oversight function; see contested assignment defence in Section 5.

**WS2-JtD-3 (medical necessity determination):** Input Structure M — medical necessity criteria are structured; clinical evidence includes unstructured notes; Decision Determinism L — highly judgment-dependent; clinical expertise required for application of criteria to ambiguous or borderline cases; Tool Coverage M — medical necessity criteria tool assumed available (A-D2A-9); Context Complexity H — requires synthesis of multi-source clinical evidence under potentially ambiguous conditions; Exception Rate H — unusual presentations, comorbidities, and incomplete documentation create a high proportion of non-standard cases; Latency Constraint L — physician reviews asynchronously; Risk/Compliance H — URAC/NCQA accreditation requirement; patient care and legal liability consequences. Score 1/7; assigned **Human Only** because Dr. Marcus Webb's non-negotiable governance requirement (Exchange 2) makes this a hard delegation stop regardless of classifier confidence or agent accuracy metrics. The Latency L point is the only suitability point, confirming this is not an automation target.

**INT-JtD-1 (intake normalisation):** Input Structure M — EDI 837 is H (structured); PDFs are L (unstructured); portal submissions are M; mixed intake pool; Decision Determinism H — parse-or-fail logic is fully deterministic for valid submissions; Tool Coverage M — EDI 837 parsing is a commodity capability; PDF extraction tooling exists but is unnamed; Context Complexity L — format transformation with no cognitive context; Exception Rate M — malformed PDFs and missing fields occur with moderate frequency (A-D2A-6); Latency Constraint L — intake processing is batch; Risk/Compliance M — intake errors propagate downstream but are detectable early.

**INT-JtD-2 (anomaly detection):** Input Structure H — claim submission fields are structured and machine-readable; Decision Determinism H — duplicate detection and format validation are deterministic rule-based checks; Tool Coverage M — standard duplication detection and format validation tools available; Context Complexity L — pattern matching against defined rules; no complex context; Exception Rate L — the majority of submissions are valid; near-duplicate detection for re-submissions adds some exception handling; Latency Constraint L — batch; Risk/Compliance M — intake errors propagate but not clinical compliance.

**APP-JtD-1 (appeal root cause classification):** Input Structure M — denial reason codes are structured; appeal documentation is semi-structured; Decision Determinism M — some root cause patterns follow clear signatures (e.g., wrong diagnosis code triggering denial); others require interpretation of the full claim context; Tool Coverage M — claim and denial records are accessible; Tool Coverage M overall; Context Complexity H — must understand both the original decision rationale and the appeal evidence together; Exception Rate H — the 41% overturn rate (scenario.md) implies high variability in what makes an appeal successful; Latency Constraint L — regulatory appeal timelines are days/weeks; Risk/Compliance H — regulatory timeliness requirements; patient access-to-care consequences.

**APP-JtD-2 (appeal determination):** Input Structure M — structured denial record + semi-structured appeal docs; Decision Determinism M — administrative appeals have clearer rules; clinical appeals require physician re-judgment; Tool Coverage M — records and medical necessity criteria tool available; Context Complexity H — requires understanding of original decision + appeal evidence + criteria application; Exception Rate H — each successful appeal is a deviation from the original decision; Latency Constraint M — regulatory timelines impose real time constraints (not real-time but not open-ended); Risk/Compliance H — regulatory; patient care; legal liability for incorrect denial maintenance. Score 0/7; note that clinical appeal determinations require physician involvement per the same URAC/NCQA constraint that governs WS2-JtD-3.

**QMG-JtD-1 (queue prioritisation):** Input Structure H — claim timestamps and SLA thresholds are structured numeric data; Decision Determinism H — the 7-day SLA threshold is a fixed contractual rule (scenario.md); priority scoring based on age-proximity to threshold is algorithmic; Tool Coverage M — claims management system is the required tool; unnamed but accessible; Context Complexity L — age-based priority queue with escalation logic; no complex context; Exception Rate L — the SLA rule is fixed; escalation follows predictable patterns; Latency Constraint L — periodic queue re-prioritisation, not real-time; Risk/Compliance H — SLA breaches carry active contractual penalties per Exchange 3. Score 5/7.

**QMG-JtD-2 (pending claims management):** Input Structure H — claim records and provider communication logs are structured; Decision Determinism H — state transitions are event-triggered (response received → re-queue; X days without response → escalate); Tool Coverage M — claims management system and communication logs; Context Complexity L — state machine: track state, re-queue when triggered; Exception Rate L — state transitions follow predictable patterns; Latency Constraint L — periodic polling acceptable; Risk/Compliance M — aged pending claims contribute to SLA breach but are not a clinical compliance issue. Score 5/7.

---

## 3. Delegation Archetype Assignment with Rationale

---

> **JtD WS1-JtD-1 — Administrative validation (eligibility, coding, prior auth)**
> **Archetype:** Agent-led + Human Oversight
> **Rationale:** Decision Determinism (M) reflects that the standard path for each check (eligibility lookup, code validity, prior auth presence) is deterministic and automatable at the JtD level; however, the coding plausibility judgment (L determinism at MT-WS1-5) and prior auth partial match resolution (L determinism at MT-WS1-7) are built into the JtD scope and require HITL escalation design. Risk/Compliance (H) — the 41% denial appeal overturn rate (scenario.md) is direct evidence that current manual execution of these checks produces systematic errors; agent-led execution with human oversight for flagged exceptions is more reliable than the current fully manual process, not less. The agent handles the standard path autonomously; processors review only flagged exceptions.
> **Governance rule impact:** No direct URAC/NCQA constraint applies to WS1-JtD-1 specifically. However, Risk H requires a HITL backstop for cases the agent cannot resolve within confidence bounds — errors here contribute to the downstream compliance problem.
> **Anti-pattern check:** Eligibility lookup (standard path) and prior auth presence check (standard path) ARE solvable with deterministic rules or RPA alone. These sub-tasks should be implemented as deterministic rules within the agent, not as LLM reasoning. The agent-level decision applies to the exception handling (discrepancy resolution, partial match tolerance, coding plausibility) that RPA cannot address. This JtD warrants an agent because the combination of structured rules AND judgment-requiring exceptions within a single processing unit creates the non-deterministic component that RPA cannot handle cleanly.

---

> **JtD WS1-JtD-2 — Clinical content routing classification**
> **Archetype:** Agent-led + Human Oversight
> **Rationale:** Tool Coverage (L) and Decision Determinism (L) are the two lowest-suitability dimensions and reflect a current-state gap, not a permanent impossibility: both resolve once the clinical content criterion is formally defined and the classifier is built and certified by Dr. Webb's team. The clinical content criterion definition is the prerequisite design output blocking this assignment; without it, the archetype defaults to Human Only (the current broken state where processors apply undocumented pattern recognition). Once the prerequisite is met, classifier-based routing with a configurable confidence threshold is the correct design: the agent handles high-confidence classifications autonomously; low-confidence cases escalate to a HITL classification queue; the confidence threshold is a named, configurable parameter certified by the CMO.
> **Governance rule impact:** The URAC/NCQA compliance constraint (WS2-JtD-3) propagates to this JtD: the classifier's false negative rate (clinical claim mis-classified as administrative) directly determines whether any claims bypass the required physician sign-off. The confidence threshold must be calibrated to near-zero false negative tolerance, accepting higher false positive rates (over-routing to WS2) as the safer error. This asymmetry must be built into the classifier design and the threshold certification process.
> **Anti-pattern check:** This is NOT solvable with static rules or RPA. The routing decision requires pattern recognition across multi-factor inputs (diagnosis codes, procedure codes, provider specialty, claim context) where the boundary between clinical and administrative is judgment-dependent. A rules engine could encode the most obvious cases; the remainder require a classifier. The agent is warranted.

---

> **JtD WS1-JtD-3 — Payment determination**
> **Archetype:** Agent-led + Human Oversight
> **Rationale:** Input Structure (H) and Exception Rate (L) are the strongest suitability signals: fee schedules are structured rate tables, and contract exceptions are low-frequency. The standard path for fee schedule application and cost-sharing calculation is deterministic and meets the Fully Agentic profile — this is the contested assignment (see Section 5). The assignment is held at Agent-led + Human Oversight because Tool Coverage (M) reflects unconfirmed access to contract exception rules (A-D0C-6): if contract exceptions reside in unstructured documents or email rather than in an accessible system, the agent cannot handle them and will produce silent errors on a subset of financially material claims. Promoting to Fully Agentic before contract rule encoding is confirmed would create undetected payment errors on contract edge cases.
> **Governance rule impact:** No URAC/NCQA constraint. Risk/Compliance (M) — payment errors are financially recoverable but contribute to provider relationship degradation. The archetype is conservative by design, not governance-mandated.
> **Anti-pattern check:** Standard fee schedule application IS solvable with deterministic rules. This component of WS1-JtD-3 should be implemented as a rules-based calculation within the agent, not LLM reasoning. The agent scope applies to: duplicate detection logic, cost-sharing calculation across plan types, and exception handling for contract carve-outs. Once contract rules are encoded and system integration confirmed, this JtD's standard path can be promoted to Fully Agentic.

---

> **JtD WS2-JtD-1 — Clinical content flag verification**
> **Archetype:** Agent-led + Human Oversight
> **Rationale:** Input Structure (H) — claim codes are already structured at WS2 entry — and Latency Constraint (L) are the suitability points. Decision Determinism (M) reflects that the same classifier built for WS1-JtD-2 applies here; once certified, high-confidence verifications are deterministic at the threshold boundary. The agent verifies the incoming routing classification, confirms contextual completeness, and escalates to HITL when confidence is below the threshold or when required documentation is flagged as unavailable. Risk/Compliance (H) applies in both error directions: a false negative (clinical claim passed without verification) = compliance violation; a false positive (administrative claim returned to WS2) = physician time waste.
> **Governance rule impact:** WS2-JtD-1 is the compliance gate that enforces the URAC/NCQA requirement at WS2 entry. It must be designed such that any claim with a classification confidence below the certified threshold cannot proceed to WS2-JtD-2 without human verification. This gate cannot be disabled by confidence threshold tuning alone — it must have a structural HITL path.
> **Anti-pattern check:** This is not solvable with a static rule. The verification task requires the same probabilistic classifier as WS1-JtD-2. A static rule (e.g., "if procedure code in list X, classify as clinical") would cover only pre-enumerated cases and cannot handle novel combinations — the same limitation that makes the current processor-based routing produce a 41% overturn rate.

---

> **JtD WS2-JtD-2 — Clinical context assembly (pre-filled review packet)**
> **Archetype:** Agent-led + Human Oversight
> **Rationale:** Tool Coverage (L) is the primary feasibility risk: the clinical notes source system is unknown (A-D0C-7), and system integration is a prerequisite to building this agent. The low suitability score (1/7) reflects this integration uncertainty and the high exception rate for missing documentation — not an inherent inability to delegate the work. The cognitive nature of this JtD (multi-source retrieval, organisation, and synthesis of structured and semi-structured data into a consistent review dossier) is precisely the work type where LLM agents add disproportionate value relative to manual assembly. Dr. Marcus Webb's 20 claims/hour target with agent pre-screening (Exchange 3) is a direct statement that this delegation is viable and material — the current physician throughput without pre-screening is substantially lower. The physician's review of the assembled packet as they make their WS2-JtD-3 determination provides the human oversight function.
> **Governance rule impact:** No direct URAC/NCQA constraint applies to context assembly itself. However, Risk/Compliance (H) applies because incomplete or incorrect context assembly directly degrades the quality of the physician's determination. The physician must be able to flag an insufficient packet and request additional assembly before making a determination — this physician-triggered exception path is the human oversight mechanism for this JtD.
> **Anti-pattern check:** Context assembly across multiple unnamed systems, involving clinical note retrieval and synthesis, cannot be solved with RPA. RPA can retrieve a structured record; it cannot synthesise a coherent clinical context from multiple partially unstructured sources and produce a readable pre-filled review dossier. The agent is warranted.

---

> **JtD WS2-JtD-3 — Medical necessity determination**
> **Archetype:** Human Only
> **Rationale:** Decision Determinism (L) — medical necessity determination requires clinical judgment against potentially ambiguous, incomplete, or contradictory evidence; no decision rule can substitute for a licensed clinician's synthesis; Risk/Compliance (H) — URAC/NCQA accreditation requires physician or advanced practice provider sign-off on every determination involving clinical content (Dr. Marcus Webb, Exchange 2); this is a regulatory compliance requirement with patient care and legal liability consequences. These two dimensions (L determinism + H compliance risk) are the "especially" conditions from the ATX Human Only assignment criteria.
> **Governance rule impact:** This is the hardest constraint in the engagement. Dr. Marcus Webb stated explicitly that his team will not certify any system that bypasses clinical review, and that no claim can be denied without CMO approval (Exchange 2). No confidence threshold, accuracy metric, or shadow-mode result changes this assignment. The agent's value in WS2 is entirely in the quality of the packet delivered to this gate — not in the determination made at it.
> **Anti-pattern check:** N/A — the question is not "could a script replace this?" but "is there any delegation path?" The answer is no: licensed clinical judgment under regulatory mandate is Human Only by governance constraint, not by task complexity alone.

---

> **JtD INT-JtD-1 — Claim intake normalisation**
> **Archetype:** Fully Agentic
> **Rationale:** Decision Determinism (H) — format transformation logic is fully deterministic: EDI 837 files are parsed by established standards; PDF and portal extraction follows defined field mapping rules; Context Complexity (L) — no cognitive context required; Latency Constraint (L) — batch processing. Exception Rate (M) reflects that malformed PDFs require more than simple rule-based handling — the agent must interpret partial extractions and return intelligible rejection notices to providers when the submission cannot be normalised. This exception handling provides the justification for an agent over pure RPA (see anti-pattern note).
> **Governance rule impact:** None — intake normalisation has no clinical compliance dimension.
> **Anti-pattern check:** Standard EDI 837 parsing IS solvable with a rules-based parser or RPA connector — an agent is not warranted for the structured-input path. The agent adds value specifically for: PDF extraction exception handling (partial fields, misaligned form layouts), provider rejection notice drafting (returning actionable error descriptions when a submission fails normalisation), and portal submission normalisation across potentially varying formats. These three capabilities require more than deterministic rules. If Greenfield subsequently confirms that PDF and portal submissions are already pre-normalised by a clearinghouse before reaching the processor queue, this JtD should be downgraded to a rules-based pipeline, not an agent.

---

> **JtD INT-JtD-2 — Intake anomaly detection**
> **Archetype:** Fully Agentic
> **Rationale:** Input Structure (H), Decision Determinism (H), Context Complexity (L), Exception Rate (L), and Latency Constraint (L) all score at high suitability — the strongest suitability profile in the engagement. Duplicate detection and format validation are deterministic rule-based checks. Near-duplicate detection (re-submissions with corrections, partial duplicates with different submission dates) adds a pattern-recognition component that benefits from LLM capability.
> **Governance rule impact:** None — anomaly detection has no clinical compliance dimension.
> **Anti-pattern check:** Basic duplicate detection and format validation ARE solvable with deterministic rules — these components should be implemented as rules within the agent, not as LLM reasoning calls. The agent scope applies specifically to: near-duplicate pattern recognition, anomalous volume or frequency patterns for a given provider (potential fraud signal), and returning intelligible rejection notices to providers. The agent is warranted for the pattern-recognition component. The deterministic checks should not consume LLM tokens.

---

> **JtD APP-JtD-1 — Appeal root cause classification**
> **Archetype:** Human-led + Agent Support
> **Rationale:** Context Complexity (H) — root cause classification requires synthesising the original claim decision and the appeal evidence together; Exception Rate (H) — the 41% overturn rate implies that appeals come in a wide variety of root cause types, many non-standard; Risk/Compliance (H) — regulatory timeliness requirements apply. The agent adds value by classifying the appeal root cause as a recommendation — surfacing the most probable error type and the supporting evidence — which the human reviewer confirms or overrides before proceeding. Decision Determinism (M) reflects that some root cause signatures (e.g., wrong code, missing prior auth) are pattern-recognisable; others require interpretation of the full case context.
> **Governance rule impact:** No URAC/NCQA constraint on root cause classification itself. However, if the classified root cause is "medical necessity error," the downstream determination (APP-JtD-2) may require physician re-review — the same governance constraint from WS2-JtD-3 applies to the clinical sub-type of appeals.
> **Anti-pattern check:** Appeal root cause classification across semi-structured documents requires more than a rules engine. Pattern matching on denial reason codes can surface obvious cases; interpreting the relationship between a denial reason and the appeal evidence requires LLM reasoning. The agent is warranted.

---

> **JtD APP-JtD-2 — Appeal determination**
> **Archetype:** Human-led + Agent Support
> **Rationale:** Decision Determinism (M) — administrative appeal determinations follow clearer rules (eligibility confirmed → overturn; code corrected → overturn); clinical appeal determinations require physician re-judgment (same L determinism as WS2-JtD-3); Risk/Compliance (H) — regulatory timeliness, patient care, legal liability. Score 0/7 reflects that all context-related dimensions score at Low suitability, and this JtD has the highest aggregate complexity in the engagement outside of WS2-JtD-3. The agent provides decision support: synthesising the relevant prior determination history, highlighting the specific evidence difference between the original claim and the appeal, and drafting a provisional determination for human review. The human reviewer confirms or overrides.
> **Governance rule impact:** For appeals involving clinical determinations, physician sign-off is required per the same URAC/NCQA constraint as WS2-JtD-3. The agent cannot make a clinical appeal determination; it can synthesise context and flag the clinical review requirement.
> **Anti-pattern check:** Appeal determination involves interpreting new evidence against prior decisions — this is not solvable with a static rule engine. The agent is warranted for the synthesis and drafting component, with human final decision authority.

---

> **JtD QMG-JtD-1 — Queue prioritisation for SLA**
> **Archetype:** Fully Agentic
> **Rationale:** Decision Determinism (H) — the 7-day SLA threshold is a fixed contractual rule (scenario.md); priority scoring based on claim age is algorithmic; Input Structure (H) — timestamps and threshold values are structured; Context Complexity (L), Exception Rate (L), and Latency Constraint (L) all score at high suitability. Risk/Compliance (H) reflects that SLA breaches carry active contractual penalties (Exchange 3) — this is the motivation for full automation, not a constraint against it. The agent continuously monitors queue age and re-prioritises in near-real-time without requiring human intervention for standard escalations.
> **Governance rule impact:** No URAC/NCQA constraint. The Fully Agentic assignment is appropriate because the decision rule is a hard contractual threshold — agent autonomy for this decision is risk-reducing, not risk-adding.
> **Anti-pattern check:** Basic SLA alerting with a fixed threshold IS solvable with a scripted rule or RPA. The agent adds value beyond a simple threshold alert by: (1) coordinating prioritisation across both WS1 async waits (missing prior auth) and WS2 async waits (missing clinical docs) in a single queue management layer; (2) drafting provider follow-up requests when a pending claim is approaching the threshold; (3) adapting prioritisation dynamically when new claims arrive that affect the entire queue's SLA risk profile. These capabilities require coordination logic beyond a threshold trigger.

---

> **JtD QMG-JtD-2 — Pending claims state management**
> **Archetype:** Fully Agentic
> **Rationale:** Decision Determinism (H) — state transitions are event-triggered (response received → re-queue; no response within X days → escalate and draft follow-up); Input Structure (H) — claim records and communication logs are structured; Context Complexity (L), Exception Rate (L), Latency Constraint (L) all score at high suitability. Risk/Compliance (M) — pending claim age-out contributes to SLA breach but is not a clinical compliance issue.
> **Governance rule impact:** None.
> **Anti-pattern check:** Core pending state tracking (response received / not received) IS solvable with a workflow script. The agent adds value by: drafting provider follow-up requests with the specific missing information required for each pending claim type (prior auth request vs. clinical documentation request); managing the follow-up conversation state; and feeding re-queued claims back into the priority queue with their age already accounted for. These functions benefit from an agent that can read the pending claim context and produce a tailored follow-up request. If Greenfield already has a workflow system that manages provider communications, this JtD should be integrated with that system rather than replacing it.

---

## 4. Delegation Architecture Summary

The delegation architecture for Greenfield Health Systems' claims adjudication transformation divides into three distinct layers. The first is an **autonomous backbone** that handles all structured execution work with no clinical judgment content: intake normalisation (INT-JtD-1), intake anomaly detection (INT-JtD-2), queue prioritisation (QMG-JtD-1), and pending claims state management (QMG-JtD-2). These four JtDs have suitability scores between 3/7 and 5/7, contain deterministic decision logic, and carry no URAC/NCQA compliance exposure. Two of them (INT-JtD-2, QMG-JtD-1, QMG-JtD-2) approach the Fully Agentic profile on multiple dimensions. Together, these JtDs form the platform infrastructure through which every claim passes, and their automation is a prerequisite for the higher-cognitive work streams to function at scale.

The second layer is the **agent-led adjudication core** — four JtDs assigned Agent-led + Human Oversight: WS1-JtD-1 (administrative validation), WS1-JtD-2 (clinical content routing), WS1-JtD-3 (payment determination), and WS2-JtD-1 (clinical content verification). This layer is where the primary volume × value opportunity lives: WS1-JtD-1 handles the full administrative validation sequence for ~2,000 claims/day (eligibility, coding, and prior auth checks apply to all incoming claims before the routing decision at step 8 — assumption A-2), and WS1-JtD-3 closes the administrative path for ~1,300 claims/day (the 65% admin-path subset after routing). WS1-JtD-2 and WS2-JtD-1 together implement the clinical content classifier — the single most consequential design decision in the architecture. These four JtDs share a common design pattern: the agent executes the standard path autonomously while a HITL escalation queue handles exceptions. The HITL queue for WS1-JtD-2 and WS2-JtD-1 is the compliance-critical path: it ensures no claim with uncertain clinical content bypasses the physician sign-off requirement.

The third structural element is the **clinical review boundary**, where the delegation scope is defined by the URAC/NCQA compliance constraint. WS2-JtD-2 (context assembly) is the final agent-executed JtD in the clinical path — the agent assembles the pre-filled review packet — but the physician's review of that packet is the oversight mechanism, and WS2-JtD-3 (medical necessity determination) is Human Only. This boundary is non-negotiable. The agent's entire value proposition in WS2 is concentrated in WS2-JtD-2: if context assembly is executed well, Dr. Webb's projected throughput of 20 claims/hour is achievable; if it is executed poorly (incomplete packets, wrong context), physician time is consumed with remediation rather than determination. The Human Only assignment at WS2-JtD-3 means the agent cannot replace or approximate the physician's judgment — it can only improve the conditions under which that judgment is made.

The two appeal JtDs (APP-JtD-1, APP-JtD-2) sit outside the primary adjudication pipeline in a **human-led support tier**. Both are assigned Human-led + Agent Support, reflecting that the appeal process involves the highest information integration complexity in the engagement (synthesising an original decision, new evidence, and applicable criteria in a single review) and that clinical appeal determinations are subject to the same URAC/NCQA physician sign-off requirement as WS2-JtD-3. The agent's role in appeals is to accelerate the human reviewer's work — classifying root cause, surfacing the relevant prior context, drafting provisional determination language — without making the determination itself.

The scenario's primary governance constraint (Dr. Marcus Webb's clinical review requirement, Exchange 2) is enforced structurally at three points in the architecture: WS2-JtD-3 (Human Only — the hard stop), WS1-JtD-2 and WS2-JtD-1 (Agent-led + Human Oversight with confidence threshold — the compliance-safe escalation path), and implicitly in APP-JtD-2 (Human-led + Agent Support for clinical appeal determinations). No JtD in the clinical path is assigned Fully Agentic. The architecture is designed so that an agent accuracy failure at WS1-JtD-2 escalates to HITL rather than producing a compliance violation — the classifier's false negative floor is a design parameter, not an operational risk accepted in production.

---

## 5. Delegation Boundary Defence

---

> **Contested assignment:** WS1-JtD-3 (payment determination) — assigned Agent-led + Human Oversight
> **The counter-argument:** The case for Fully Agentic is strong. WS1-JtD-3 has the highest suitability score of any JtD in the primary processing pipeline (4/7). Input Structure is H (structured fee schedule tables), Exception Rate is L (contract exceptions are rare per D2A A-D2A-5), and Latency is L. The standard fee schedule application and cost-sharing calculation path is genuinely deterministic — the industry benchmark of 85% auto-adjudication (scenario.md) is direct evidence that this step is fully automatable in a well-designed payer environment. Risk/Compliance is M (not H), which is the most permissive compliance profile of any WS1 or WS2 JtD. A reasonable architect would assign Fully Agentic here and trust the standard path.
> **Why the assigned archetype is correct for this scenario:** Tool Coverage is M, not H, because contract exception rules are assumed to be stored in documents or email rather than in accessible structured data (A-D0C-6 — a Low confidence assumption). If an agent applies the standard fee schedule to a claim that qualifies for a contractually negotiated exception rate, the error is financially material and may not be flagged by the agent — the agent produces a plausible-looking payment amount that is simply wrong. Unlike coding errors (which generate denials that trigger appeals), underpayment errors on contract exceptions may not generate an audit trail visible to either party until a contract reconciliation cycle. Agent-led + Human Oversight is the correct archetype for the period before contract rules are confirmed encoded in accessible systems. Once confirmed, promote to Fully Agentic on the confirmed-encoded path.
> **What would change the assignment:** Confirmation that all contract exception rules are encoded in a structured, API-accessible data source and that the fee schedule system has no undocumented rate exceptions for any payer or provider in scope. This can be confirmed through a system audit during discovery. If confirmed, WS1-JtD-3 is promoted to Fully Agentic with a HITL exception path only for claims flagged by the duplicate detection logic.

---

> **Contested assignment:** WS2-JtD-2 (clinical context assembly) — assigned Agent-led + Human Oversight
> **The counter-argument:** With a suitability score of 1/7 and four dimensions at Low suitability (Tool Coverage L, Context Complexity H, Exception Rate H, Risk/Compliance H), a strict application of the ATX dimension-count rule — Human Only for ≥3 Low suitability dimensions including risk/compliance — would assign this JtD to Human Only. The case: we don't know where clinical notes live (A-D0C-7), documentation is frequently incomplete (Exception Rate H scored at MT-WS2-2 in D2A), and incomplete context assembly directly degrades physician determination quality (Risk/Compliance H). Assigning Agent-led + Human Oversight before system integration is confirmed is architecturally premature.
> **Why the assigned archetype is correct for this scenario:** The Human Only archetype for WS2-JtD-2 is the current broken state — physicians manually assembling context from scratch is what produces the throughput bottleneck that Dr. Webb's 20 claims/hour estimate is designed to solve (Exchange 3). Human Only is not a conservative safe choice here; it is the perpetuation of the problem. The four Low suitability dimensions reflect implementation prerequisites (Tool Coverage L = system integration required) and operational design requirements (Exception Rate H = robust missing-documentation escalation path required; Risk H = packet completeness verification required), not fundamental impossibility. Decision Determinism (M — the "especially" dimension for Human Only) is not Low: structured retrieval logic is deterministic; only exception handling requires judgment. The archetype is conditional on system integration being confirmed feasible — if clinical notes cannot be retrieved programmatically, the archetype reverts to Human Only and the WS2 agent value proposition collapses. The integration feasibility question is Unknown U-5 from D0C, and it must be resolved in discovery before the capability specification is finalised.
> **What would change the assignment:** Discovery that clinical documentation (physician notes, operative reports) cannot be accessed programmatically — either because it exists only as physical faxes, because the EHR vendor has no accessible API, or because HIPAA / BAA constraints prevent programmatic access by the agent's runtime environment. Any of these conditions would make Agent-led + Human Oversight infeasible and revert WS2-JtD-2 to Human-led + Agent Support at best (agent can process documents provided to it, but cannot retrieve them) or Human Only if no access path exists.

---

## 6. Assumption Log

> **Assumption [A-D2B-1]:** The clinical content classifier (required for WS1-JtD-2 and WS2-JtD-1) can be built once a formal definition of "clinical content" is produced by Dr. Webb's team, and that definition will be precise enough to operationalise as classifier training criteria. The definition is the prerequisite design output blocking these two JtDs.
> **Why it matters:** Both WS1-JtD-2 and WS2-JtD-1 are assigned Agent-led + Human Oversight conditional on this prerequisite being met. If Dr. Webb's team cannot produce a definition that is precise enough to operationalise, both JtDs revert to Human Only — and the 65%/35% routing architecture that the entire economic case depends on cannot be implemented.
> **If wrong:** If the clinical content definition remains informal or context-dependent (e.g., "it depends on the physician's judgment about the case"), the classifier cannot be specified or built, and the administrative/clinical routing split must be implemented through processor judgment — preserving the inconsistency that produces the 41% overturn rate.
> **Confidence:** Medium — Sarah Chen's Exchange 3 explicitly requests a written definition, implying Dr. Webb's team can produce one; however, "clinical content" may be genuinely resistant to a precise, classifier-compatible definition depending on the range of claims Greenfield processes.

---

> **Assumption [A-D2B-2]:** The archetype assignments for WS1-JtD-1 (Agent-led + Human Oversight) and WS1-JtD-3 (Agent-led + Human Oversight) assume that the exception rates for coding plausibility and prior auth partial matches are manageable — roughly 10–20% of relevant claims — producing a HITL queue that is sized to the available processor team after headcount reduction. If exception rates are materially higher, the HITL queue may exceed the post-reduction processor capacity.
> **Why it matters:** The headcount model in the scenario projects reducing review staff from 20 to 7 (Exchange 3). If the WS1 HITL queue requires more than 7 processors to clear within SLA, the headcount reduction is not achievable at the designed exception rate, and the archetype assignments require revision upward (toward Fully Agentic, requiring lower exception rates) or the headcount model requires revision.
> **If wrong:** If coding plausibility exception rates are > 25%, the WS1 agent's HITL queue is a primary workflow rather than an exception path — more similar to Agent-led + Human Oversight with a large human component than to a predominantly agentic architecture. The economic model changes significantly.
> **Confidence:** Low — exception rates for both coding plausibility and prior auth partial matches are Unknown (U-4 in D0C); the 10–20% range is a design assumption, not a measured baseline.

---

> **Assumption [A-D2B-3]:** The Fully Agentic archetype assignments for QMG-JtD-1 and QMG-JtD-2 assume that queue prioritisation and pending claims state management are currently handled manually by processors alongside their adjudication work, and that there is no existing dedicated queue management system that already provides these functions.
> **Why it matters:** If Greenfield already has a queue management system (as part of their claims management platform), building these as agent capabilities may duplicate existing functionality rather than replace it. The integration design would differ: the agent coordinates with the existing system rather than owning the queue state.
> **If wrong:** If a queue management system already exists and is functioning, QMG-JtD-1 and QMG-JtD-2 may require agent enhancement of an existing tool (Human-led + Automation Support) rather than a new agent capability. The build scope and integration surface change, but the archetype may remain similar.
> **Confidence:** Low — no systems are named in the scenario (scenario_context.md Section 6); queue management capabilities are not described, which is consistent with their absence.

---

> **Assumption [A-D2B-4]:** The APP-JtD-1 and APP-JtD-2 assignments (Human-led + Agent Support) assume that appeal volume is manageable enough to warrant agent support but not a full agentic pipeline, and that the current appeal process has sufficient structure for an agent to add value without requiring the scenario evidence that is currently absent.
> **Why it matters:** The scenario provides only the 41% overturn rate as evidence for the appeals process. If appeal volume is high (e.g., > 200 appeals/day derived from the 41% rate × some denial volume unknown), the Human-led + Agent Support archetype may underinvest in automation for a process that is materially consuming staff time. A more complete picture of appeal volume and process structure — Unknown U-6 in D0C — is required before the appeal process archetype is finalised.
> **If wrong:** If appeal volume is high and the root cause structure is more codifiable than assumed, APP-JtD-1 could be promoted to Agent-led + Human Oversight and APP-JtD-2 (for administrative appeals only) could similarly be promoted. The clinical appeal sub-type remains Human Only regardless.
> **Confidence:** Low — appeal process detail is thin in the scenario; assignments are conservative pending discovery.
