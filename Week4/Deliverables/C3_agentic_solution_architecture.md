# D3 — Agentic Solution Architecture
## Greenfield Health Systems: Medical Claims Adjudication Transformation

*Source inputs: `Deliverables/D2A_cognitive_load_map.md`, `Deliverables/D2B_delegation_suitability_matrix.md`, `Deliverables/D2C_volume_value_analysis.md`, `Deliverables/C1_token_economics_model.md`, `Scenario/scenario_context.md`. Every design decision traces to one of these inputs or is flagged as an assumption.*

---

## 0. Executive Summary

- **Primary agentic target:** WS1 — Administrative Adjudication at Agent-led + Human Oversight delegation, covering 1,300 claims/day on the administrative path — replacing processor-driven manual adjudication running at a 5.7× daily capacity deficit against the 20-person review staff that produces active SLA penalties and a 9+ day cycle time against a 7-day contractual threshold (Exchange 3).
- **Central architectural decision:** A single shared clinical content classifier component called by both the WS1 agent (routing) and WS2 agent (verification), rejecting separate per-work-stream classifiers because separate classifiers would create routing inconsistency at the WS1/WS2 boundary and require Dr. Webb's team to certify the clinical content definition twice — the highest-effort governance activity in the engagement.
- **Condition most likely to constrain production:** The clinical content classifier's confidence threshold is a single configurable parameter that determines both the URAC/NCQA false-negative exposure (CMO requires near-zero tolerance for clinical claims bypassing physician review, Exchange 2) and the HITL queue size (CFO and VP Ops require ≤25% HITL rate to close the economic case, C1 §10) — these two pressures operate in opposite directions on the same dial, and the threshold value cannot be resolved without calibration data from a production-like mock run before go-live.

---

## 0b. Table of Contents

- [0. Executive summary](#0-executive-summary)
- [1. Workflow-to-agent mapping](#1-workflow-to-agent-mapping)
- [2. Agent design summary](#2-agent-design-summary)
- [3. Autonomy matrix](#3-autonomy-matrix)
- [4. Architecture Decision Records](#4-architecture-decision-records)
- [5. Non-agentic residual](#5-non-agentic-residual)
- [6. Assumption log](#6-assumption-log)

---

## 1. Workflow-to-Agent Mapping

*All 12 JtDs from D2B §1 are mapped. Archetype column is taken directly from D2B §2; no re-scoring is performed here.*

| JtD | Delegation archetype (D2B) | Agentic? | Agent / role assigned | Justification |
|-----|---------------------------|:--------:|-----------------------|---------------|
| **WS1-JtD-1:** Administrative validation (eligibility, coding, prior auth) | Agent-led + Human Oversight | Yes — partial HITL | WS1 Administrative Adjudication Agent | D2B score 1/7; Decision Determinism M — standard eligibility and prior auth lookups are deterministic but coding plausibility (MT-WS1-5, DD=L) and prior auth partial match (MT-WS1-7, DD=L) require HITL escalation; Risk H — 41% overturn rate (scenario.md) is direct evidence of current manual error; D2C Wave 1 primary target |
| **WS1-JtD-2:** Clinical content routing classification | Agent-led + Human Oversight | Yes — partial HITL | WS1 Administrative Adjudication Agent (shared clinical content classifier) | D2B score 1/7; Tool Coverage L (classifier must be built), Decision Determinism L (no formal criterion exists — scenario_context.md A-4); conditional on CMO-certified classifier; confidence threshold is the HITL gate; D2C Wave 1 prerequisite dependency |
| **WS1-JtD-3:** Payment determination and approval | Agent-led + Human Oversight | Yes — partial HITL | WS1 Administrative Adjudication Agent | D2B score 4/7 — strongest in the primary pipeline; Input Structure H, Exception Rate L, Risk M; held at Agent-led (not Fully Agentic) because Tool Coverage M — contract exception rules unconfirmed in accessible systems (D2B §5, A-D0C-6); see ADR-1 |
| **WS2-JtD-1:** Clinical content flag verification | Agent-led + Human Oversight | Yes — partial HITL | Clinical Review Support Agent | D2B score 2/7; Input Structure H; reuses shared classifier component from WS1; confidence threshold gates HITL verification before WS2-JtD-2 proceeds; structural compliance gate at WS2 entry |
| **WS2-JtD-2:** Clinical context assembly (pre-filled review packet) | Agent-led + Human Oversight | Yes — partial HITL | Clinical Review Support Agent | D2B score 1/7; Tool Coverage L (clinical notes source system unknown — A-D0C-7); conditional on integration feasibility (D2C Wave 2 hard blocker); physician review of assembled packet = human oversight mechanism; D2C Wave 2 |
| **WS2-JtD-3:** Medical necessity determination | Human Only | No — stays human | Physician / licensed provider (always) | D2B score 1/7; Decision Determinism L + Risk H = URAC/NCQA accreditation requirement (Dr. Marcus Webb, Exchange 2); no agent confidence level or accuracy metric changes this assignment; see §5 |
| **INT-JtD-1:** Claim intake normalisation | Fully Agentic | Yes — autonomous | Intake & Anomaly Agent | D2B score 3/7; Decision Determinism H, Context Complexity L, Latency L; EDI 837 parsing is commodity; agent adds value for PDF exception handling and provider rejection notice drafting; D2C Wave 1 prerequisite infrastructure |
| **INT-JtD-2:** Intake anomaly detection | Fully Agentic | Yes — autonomous | Intake & Anomaly Agent | D2B score 5/7 — strongest structural suitability profile in the engagement; Input Structure H, Decision Determinism H, Exception Rate L, Context Complexity L; duplicate detection and format validation are deterministic; near-duplicate pattern recognition benefits from agent reasoning |
| **APP-JtD-1:** Appeal root cause classification | Human-led + Agent Support | Partial — agent supports | Appeals Support Agent (Wave 3) | D2B score 1/7; Context Complexity H, Exception Rate H (41% overturn rate — scenario.md), Risk H; agent classifies root cause as recommendation; human reviewer confirms or overrides; D2C Wave 3 — deferred until WS1 steady-state quality data available |
| **APP-JtD-2:** Appeal determination | Human-led + Agent Support | Partial — agent supports | Appeals Support Agent (Wave 3) | D2B score 0/7; highest aggregate complexity; agent synthesises prior context and drafts provisional determination; human makes final decision; clinical appeal sub-type requires physician review per same URAC/NCQA constraint as WS2-JtD-3; D2C Wave 3 |
| **QMG-JtD-1:** Queue prioritisation for SLA | Fully Agentic | Yes — autonomous | Queue & SLA Management Agent | D2B score 5/7; Decision Determinism H (7-day threshold is a contractual rule — scenario.md), Input Structure H, Exception Rate L; SLA threshold is a hard contractual rule; full automation is risk-reducing here, not risk-adding |
| **QMG-JtD-2:** Pending claims state management | Fully Agentic | Yes — autonomous | Queue & SLA Management Agent | D2B score 5/7; state-machine transitions are event-triggered; Input Structure H; manages both WS1 async waits (missing prior auth) and WS2 async waits (missing clinical docs) in a single queue layer |

---

**AI-native moment:** The architecture's AI-native moment occurs at **WS1-JtD-2 (clinical content routing, MT-WS1-8)**. The current process relies on undocumented processor pattern recognition across diagnosis codes, procedure codes, and provider specialty simultaneously — a task for which no formal criterion exists and no rule engine can be specified (scenario_context.md Assumption A-4). A rules engine can encode pre-enumerated code combinations as "clinical" or "administrative," but it cannot handle novel combinations, and it cannot reason over the interaction between all three inputs at once. The agent classifier does what no rule engine can: it treats "cardiologist billing for a gynecological procedure under a cardiac diagnosis code" as implausible not because any single code is on a flagged list, but because the combination as a whole — read in context — is inconsistent with standard clinical practice. This multi-factor contextual pattern recognition is the structural cause of the 41% denial appeal overturn rate in the current process (scenario.md): processors applying different personal heuristics to the same borderline claim make different routing decisions; the agent produces a consistent, auditable classification with a confidence score at every claim. The agent does not merely speed up the routing decision — it produces a different quality of outcome than the current manual process, which is why classifier accuracy is the load-bearing design constraint, not token count or latency.

---

## 2. Agent Design Summary

---

> **Agent 1: Intake & Anomaly Agent**
> **Job to be done:** Transform inbound claim submissions (EDI 837, PDF, portal) into structured canonical claim records, and detect anomalies (malformed submissions, duplicates) before WS1 processing begins — ensuring downstream agents receive consistent, validated input.
> **Workflow segments covered:** INT-JtD-1 (intake normalisation), INT-JtD-2 (anomaly detection)
> **Tools required:** EDI 837 parser, PDF extraction library (OCR + structured field extraction), portal submission normaliser, duplicate detection rules engine, submission history record access
> **Context required:** Inbound claim submission (EDI, PDF, or portal format); submission history for duplicate detection (member ID + service date + procedure code match window)
> **Escalation triggers:** Submission cannot be normalised (missing required fields after extraction, unrecognisable format) → return to provider with specific actionable error message; suspected duplicate (near-match with prior submission within X days) → HITL human review before rejecting, to prevent valid re-submissions being discarded
> **Governance constraint:** None — intake normalisation has no clinical compliance dimension. If Greenfield subsequently confirms that all PDF and portal submissions arrive pre-normalised via a clearinghouse, this agent's scope reduces to anomaly detection only.

---

> **Agent 2: WS1 Administrative Adjudication Agent**
> **Job to be done:** Take a normalised claim record through the complete administrative adjudication pipeline — eligibility verification, coding validation, prior auth check, clinical content routing classification, and payment determination — producing a final disposition: auto-approved with payment amount, rejected with specific failure codes, routed to WS2 clinical queue, or escalated to HITL for exception resolution.
> **Workflow segments covered:** WS1-JtD-1 (administrative validation), WS1-JtD-2 (clinical content routing), WS1-JtD-3 (payment determination)
> **Tools required:** Member eligibility API (binary lookup + discrepancy context), ICD-10/CPT code validation API / reference table, prior auth system API (presence + record retrieval), fee schedule API (rate lookup + cost-sharing calculation), shared clinical content classifier (called as a service; see ADR-2), fee schedule contract exception lookup (structured system — required condition for WS1-JtD-3 promotion; currently unconfirmed)
> **Context required:** Canonical claim record (from Intake Agent); member eligibility record; prior auth record; fee schedule excerpt for this procedure-provider combination; clinical content criterion (must be formally defined and classifier-encoded before go-live); contract exception rules (must be in accessible structured system for WS1-JtD-3 standard path)
> **Escalation triggers:** BP-WS1-1 (eligibility discrepancy detected, ~5% of claims) → HITL exception review; BP-WS1-2 (coding plausibility flag, ~15%) → HITL exception review; BP-WS1-3 (prior auth partial match, ~8%) → HITL tolerance review; BP-WS1-4 (clinical content classifier confidence below configured threshold, ~10%) → HITL routing verification before claim proceeds to either path; BP-WS1-5 (contract exception flag on fee schedule, ~2%) → HITL payment review
> **Governance constraint:** The clinical content classifier (WS1-JtD-2) must be certified by Dr. Marcus Webb's team before any production routing. Classifier false-negative rate (clinical claim mis-classified as administrative) is the compliance-critical metric — a false negative routes a clinical claim to the administrative payment path without physician review, constituting a URAC/NCQA accreditation violation (Exchange 2). This certification is a hard go-live gate, not a post-launch calibration activity.

---

> **Agent 3: Clinical Review Support Agent**
> **Job to be done:** Verify that claims arriving in the clinical review queue were correctly classified as clinical, and assemble a complete pre-filled review packet — diagnosis codes, prior auth history, clinical notes summary, member history — so physicians can make a medical necessity determination without manual document hunting.
> **Workflow segments covered:** WS2-JtD-1 (clinical content flag verification), WS2-JtD-2 (clinical context assembly)
> **Tools required:** Shared clinical content classifier (verification call — same component as WS1-JtD-2), clinical notes source system API (hard prerequisite — system unknown, A-D0C-7), prior auth system API (reused from WS1 integration), member eligibility and history API (reused from WS1 integration), medical necessity criteria reference (InterQual/Milliman or proprietary — A-D2A-9), physician review queue interface (HITL delivery endpoint)
> **Context required:** Incoming claim with routing classification and confidence score; clinical notes from treating provider; prior auth history for this member and procedure type; member's prior claims history relevant to this diagnosis; applicable medical necessity criteria section for this procedure type
> **Escalation triggers:** BP-WS2-1 (classifier confidence below threshold for routing verification) → HITL routing review before proceeding to context assembly; BP-WS2-2 (required clinical documentation not retrievable — missing notes, fax-only records, incomplete prior auth) → flag to physician with completeness indicator and pre-draft information request for provider outreach; physician flags assembled packet as insufficient → draft additional information request, pend claim in SLA-monitored state
> **Governance constraint:** This agent cannot produce, approximate, or pre-fill a medical necessity determination. The pre-filled review packet is an input to the physician's judgment, not a pre-decided answer. Packet completeness must be explicitly surfaced to the physician as a confidence indicator before WS2-JtD-3 begins — a physician making a determination on an incomplete packet without knowing it is incomplete violates the quality standard this agent exists to support. If clinical notes cannot be retrieved programmatically, this agent reverts to Human-led + Agent Support at best and the WS2 economic case collapses.

---

> **Agent 4: Queue & SLA Management Agent**
> **Job to be done:** Continuously monitor the claims processing queue to prevent SLA breaches, prioritise claims approaching the 7-day contractual penalty threshold, and manage the state of all claims pending provider response — re-queuing them promptly when documentation arrives and escalating when providers are unresponsive.
> **Workflow segments covered:** QMG-JtD-1 (SLA queue prioritisation), QMG-JtD-2 (pending claims state management)
> **Tools required:** Claims queue (read + write access), claim timestamp and age data, submission timestamp and SLA countdown, provider communication interface (for follow-up drafting), pending claims state record
> **Context required:** All claims in queue with submission timestamps and current processing state; pending claims awaiting provider response with last-contact date; 7-day SLA threshold and penalty structure (scenario.md)
> **Escalation triggers:** Claim approaching 7-day threshold with no pending state resolution → escalate to human coordinator with drafted provider follow-up; provider has not responded to prior auth request within X days → human-initiated escalation path (threshold value X is a configurable design parameter); re-queued claim arrives but documentation is incomplete → flag for HITL completeness review rather than silent re-queue
> **Governance constraint:** None — queue management has no clinical compliance dimension. The 7-day SLA threshold is a contractual rule (scenario.md Exchange 3), not a governance process. Fully Agentic assignment is appropriate because automation here is risk-reducing: the current manual queue management is what allows claims to exceed the 7-day threshold and incur penalties (James Liu, Exchange 3).

---

> **Agent 5: Appeals Support Agent** *(Wave 3 — not built until WS1 is in steady state)*
> **Job to be done:** Classify an inbound denial appeal by root cause and assemble the relevant prior context for the human reviewer, so the reviewer can determine whether to overturn the original denial without rebuilding the evidence record from scratch.
> **Workflow segments covered:** APP-JtD-1 (appeal root cause classification), APP-JtD-2 (appeal determination support)
> **Tools required:** Denial record access, original claim record (reuses WS1 integration), appeal documentation system (system unknown — A-D2C-2), denial reason code reference, medical necessity criteria tool (for clinical appeal sub-type classification)
> **Context required:** Original claim decision and reason codes; appeal submission documentation; applicable criteria for the procedure type (if clinical sub-type)
> **Escalation triggers:** Root cause classified as medical necessity error → flag for mandatory physician review before determination (URAC/NCQA extends to clinical appeals); determination is all cases — agent proposes; human reviewer always approves before determination is issued
> **Governance constraint:** For any appeal involving a medical necessity determination (clinical sub-type), the same URAC/NCQA physician sign-off requirement that governs WS2-JtD-3 applies here. The agent cannot make a clinical appeal determination; it can synthesise context and flag the physician review requirement. Wave 3 build should not begin until WS1 steady-state data confirms the residual appeal volume and root-cause distribution (D2C §10).

---

## 3. Autonomy Matrix

*Every action the architecture takes appears in exactly one cell. Actions that do not yet exist (Wave 2 and Wave 3 components) are included to show the complete authority map.*

| Action | Agent decides alone | Agent acts, human notified | Agent proposes, human approves | Human takes over |
|--------|:------------------:|:---------------------------:|:------------------------------:|:---------------:|
| EDI 837 parsing and normalisation (standard path) | ✓ | | | |
| PDF field extraction (well-formed submission) | ✓ | | | |
| Duplicate submission detection | ✓ | | | |
| Malformed submission — provider rejection notice | | ✓ | | |
| Near-duplicate submission (possible valid re-submission) | | | ✓ | |
| Claims queue reprioritisation by SLA age | ✓ | | | |
| Provider follow-up draft for pending claim approaching threshold | | | ✓ | |
| Member eligibility lookup (standard path — binary result) | ✓ | | | |
| Eligibility discrepancy resolution (data lag vs. genuine gap) | | | ✓ | |
| Code validity check (standard crosswalk rules) | ✓ | | | |
| Coding plausibility assessment (multi-factor pattern recognition) | | | ✓ | |
| Prior auth lookup (present / not present) | ✓ | | | |
| Prior auth partial match tolerance resolution | | | ✓ | |
| Clinical content routing — high-confidence classification | ✓ | | | |
| Clinical content routing — below confidence threshold | | | | ✓ |
| Fee schedule calculation (standard path — rate table lookup + arithmetic) | ✓ | | | |
| Fee schedule contract exception handling | | | ✓ | |
| Payment approval — standard administrative claim | | ✓ | | |
| Clinical content flag verification — high-confidence | ✓ | | | |
| Clinical content flag verification — below threshold | | | | ✓ |
| Clinical documentation retrieval (all documentation present) | ✓ | | | |
| Clinical documentation retrieval — incomplete, missing notes | | ✓ | | |
| Pre-filled review packet delivery to physician queue | | ✓ | | |
| Additional information request — physician-triggered | | | ✓ | |
| Medical necessity determination (approve / deny / pend) | | | | ✓ (physician) |
| Determination documentation and reason coding | ✓ | | | |
| Denial notice generation (compliant format) | | | ✓ | |
| Appeal root cause classification | | | ✓ | |
| Appeal determination — administrative sub-type | | | ✓ | |
| Appeal determination — clinical sub-type | | | | ✓ (physician) |
| HITL exception queue escalation when unresolvable | | | | ✓ |

---

**Hardest boundary:** The action that sits closest to the line is **clinical content routing at the confidence threshold boundary** — specifically, the transition between "agent decides alone" (above threshold: agent routes to administrative or clinical path autonomously) and "human takes over" (below threshold: human reviews the routing before the claim proceeds to either path). This is the boundary the client will push on most during the verbal defense because the threshold value is a single configurable parameter under opposing pressure from two stakeholders: Dr. Marcus Webb requires near-zero false-negative tolerance (meaning a conservative threshold that sends more borderline cases to HITL, protecting URAC/NCQA compliance) while Sarah Chen and James Liu require a HITL rate at or below 25% to make the economic case hold (C1 §10). The architecture establishes the structural boundary — below threshold = human takes over — but the threshold value itself cannot be set without calibration data. The defense question will be: "who has authority to set the threshold?" The answer must be: the CMO certifies the threshold; the CFO accepts the economic implications of that certification; the threshold is not negotiable from the outside of that process.

---

## 4. Architecture Decision Records

---

**ADR-1: Delegation level of WS1-JtD-3 — payment determination**

**Status:** Proposed

**Context:**
WS1-JtD-3 has the highest suitability score of any JtD in the primary processing pipeline (4/7 per D2B §2). Input Structure is H (fee schedules are structured rate tables), Exception Rate is L (contract exceptions are low-frequency per D2A A-D2A-5), and Risk/Compliance is M — the most permissive compliance profile of any WS1 or WS2 JtD. The industry benchmark of 85% auto-adjudication (scenario.md) is direct evidence that payment determination is automatable at scale in a well-configured payer environment. Assigning Fully Agentic here would reduce HITL queue volume and align the architecture with the industry benchmark target.

**Decision:**
Hold WS1-JtD-3 at Agent-led + Human Oversight until discovery confirms all contract exception rules are encoded in a structured, API-accessible data system.

**Alternatives considered:**

| Alternative | Trade-offs | Why rejected |
|-------------|------------|--------------|
| Agent-led + Human Oversight *(chosen)* | Adds HITL overhead for ~2% of claims (BP-WS1-5); prevents full auto-adjudication rate until contract rules are confirmed encoded | *(chosen)* |
| Fully Agentic | Reduces HITL volume; achieves maximum auto-adjudication rate; consistent with the 85% industry benchmark | Rejected: if contract exceptions reside in documents/email (A-D0C-6) rather than an accessible system, the agent produces plausible-looking incorrect payment amounts on a subset of financially material claims with no visible error signal — underpayment errors on negotiated contract rates may not surface until a contract reconciliation cycle, bypassing the appeals mechanism that catches other errors |
| Human-led + Agent Support | Eliminates financial risk on contract exceptions; agent calculates, processor approves all | Rejected: over-conservative given the 4/7 suitability profile; Input Structure H and Exception Rate L confirm the standard path is automatable; requiring processor approval of every payment approval would preserve most of the manual overhead WS1 automation is designed to eliminate |

**Consequences:**
- *Enables:* Safe go-live without pre-encoding all contract exceptions; HITL reviewer catches exception-path errors before payment is issued; the standard-path (95%+ of payment determinations) is still fully automated
- *Forecloses:* The 85% industry auto-adjudication benchmark cannot be fully achieved until contract exceptions are confirmed encoded; the WS1 HITL queue will remain slightly larger than the theoretical minimum for as long as Tool Coverage is M
- *Assumes:* Contract exception rules exist in some form and can eventually be encoded in structured data (A-D3-1); if they exist only in individual employees' memory, WS1-JtD-3 may never reach the Fully Agentic archetype

**Revisit condition:**
Discovery audit confirms all contract exception rules for in-scope providers and payers are encoded in a structured, API-accessible data source and no undocumented rate exceptions exist. At that point, WS1-JtD-3 standard path is promoted to Fully Agentic; HITL remains only for duplicate flags (BP-WS1-5 is eliminated as a breakpoint).

---

**ADR-2: Single shared clinical content classifier vs. separate classifiers per work stream**

**Status:** Proposed

**Context:**
Both WS1-JtD-2 (routing a claim to the administrative or clinical path) and WS2-JtD-1 (verifying that a claim arriving in the clinical queue was correctly classified) require a clinical content classification decision against the same underlying criterion. These two uses could be served by a single shared classifier component or by two independently designed classifiers — one optimised for WS1 routing precision, one for WS2 verification recall. The clinical content criterion definition is the prerequisite design output that blocks both JtDs (D2A §4, A-D2B-1), and Dr. Marcus Webb's CMO certification of that criterion is the highest-effort governance activity in the engagement.

**Decision:**
Build a single shared clinical content classifier component, called by both the WS1 agent (routing) and the WS2 agent (verification), with configurable confidence thresholds for each call site.

**Alternatives considered:**

| Alternative | Trade-offs | Why rejected |
|-------------|------------|--------------|
| Single shared classifier with configurable thresholds *(chosen)* | One training dataset; one CMO certification event; one maintenance workflow; possible tension between WS1 precision and WS2 recall requirements at a shared threshold | *(chosen)* |
| Separate classifiers per work stream | Each classifier optimised for its use case independently; can evolve separately | Rejected: creates routing inconsistency at the WS1/WS2 boundary — if WS1 routes a claim as administrative and WS2 classifies the same claim as clinical, there is no defined resolution path, the claim bounces between queues, and the compliance record is ambiguous; additionally doubles the CMO certification effort (the clinical content definition process must be repeated for each classifier) and introduces maintenance divergence over time |
| Rules-based routing (no classifier) | Fully deterministic; no training data required; auditable enumeration of clinical triggers | Rejected: the current processor-based routing with undocumented heuristics already produces the 41% overturn rate (scenario.md); a rules engine can enumerate known clinical patterns but cannot handle novel code combinations or multi-factor signal — the same limitation that makes processor inconsistency the root cause of the overturn problem; this option also fails the AI-native requirement (see §1) |

**Consequences:**
- *Enables:* Single CMO certification event in Wave 1 covers both WS1 routing and WS2 verification; classifier improvements in Wave 1 calibration propagate to WS2 verification without re-certification; shared versioning means both agents always see the same classification output for the same input
- *Forecloses:* Cannot independently tune WS1 routing precision and WS2 verification recall as if they were separate design problems; if calibration reveals that optimal thresholds for the two use cases conflict, the architecture must support two separately configurable thresholds on the same underlying model — this must be designed into the classifier service interface from the start
- *Assumes:* The clinical content classification task for routing and the task for verification are the same problem solved once (A-D3-2); if the CMO team determines that routing and verification require fundamentally different criteria, this decision requires revisiting

**Revisit condition:**
Calibration data shows that the optimal confidence threshold for WS1 routing (minimising physician queue over-routing — false positives) materially conflicts with the optimal threshold for WS2 verification (minimising administrative payment path false negatives). At that point, the classifier service must expose two configurable threshold parameters rather than one shared value, and both configurations must be included in the CMO certification process.

---

**ADR-3: Single WS1 orchestrating agent vs. pipeline of micro-agents**

**Status:** Proposed

**Context:**
WS1 involves 10 micro-tasks across 3 JtDs, mixing deterministic tool calls (eligibility lookup, code validation API, prior auth lookup, fee schedule calculation — no LLM tokens) with Sonnet LLM judgment calls (coding plausibility, eligibility discrepancy, prior auth partial match, clinical content routing, contract exception handling — ~2.15 average LLM calls per claim, C1 §3). These could be implemented as a single orchestrating agent that manages all micro-tasks, or as a pipeline of smaller agents — each specialising in a subset of the workflow (e.g., one agent for validation, one for routing, one for payment). Both patterns are deployed architectures in enterprise LLM systems.

**Decision:**
Implement WS1 as a single orchestrating agent that calls deterministic tools for the five structured micro-tasks and invokes Sonnet for the five judgment micro-tasks, rather than decomposing WS1 into multiple agents chained in a pipeline.

**Alternatives considered:**

| Alternative | Trade-offs | Why rejected |
|-------------|------------|--------------|
| Single WS1 orchestrating agent *(chosen)* | Simpler state management; single audit trail; single deployment unit; no inter-agent context passing overhead | *(chosen)* |
| Pipeline of micro-agents (one per JtD, three agents total) | Better separation of concerns per JtD; each agent independently testable; independent deployment of WS1-JtD-2 (routing) from WS1-JtD-1 (validation) | Rejected: WS1-JtD-1 through WS1-JtD-3 are serially dependent on a single claim record — the output of each step is the input to the next; no parallelism is possible or useful; chaining three agents produces inter-agent context-passing overhead (full claim record must be serialised and passed between agents) and complicates HITL state management (a HITL escalation at WS1-JtD-1 must pause the entire pipeline; a pipeline that pauses mid-chain requires recovery logic that a single agent handles naturally) |
| Rules engine with targeted LLM calls | Lowest token cost on the deterministic path; clearest audit trail for rule-based steps | Rejected as a standalone architecture: the deterministic steps within WS1 are already implemented as tool calls and code within the single agent (C1 §3 architecture); this option's valid elements are absorbed into the recommended architecture's design. As a wholesale replacement, a rules engine cannot handle clinical plausibility assessment (MT-WS1-5, DD=L, no formal rule) or clinical content routing (MT-WS1-8, DD=L, no formal criterion) — the two highest-volume exception sources |

**Consequences:**
- *Enables:* Linear, auditable claim processing record; straightforward HITL state management (agent flags a breakpoint, pauses, human resolves, agent resumes from the same state); single deployment unit for Wave 1 delivery
- *Forecloses:* Independent scaling of individual processing stages (e.g., cannot scale the clinical content routing step in isolation from eligibility verification if one step becomes a throughput bottleneck); a change to any WS1 micro-task requires testing the full pipeline rather than just the affected stage
- *Assumes:* WS1 processing volume (1,300 claims/day) can be handled by a single-agent deployment with acceptable throughput within the 7-day SLA; no sub-minute latency requirement exists at the individual claim level (A-D3-3)

**Revisit condition:**
WS1 processing volume exceeds the single-agent throughput ceiling (to be established during capability specification load testing), or a sub-minute latency requirement emerges for a specific claim type (e.g., emergency service claims). At that point, WS1-JtD-2 (the Sonnet-heavy routing step) is the first candidate for extraction into a separate callable service.

---

## 5. Non-Agentic Residual

> **WS2-JtD-3 — Medical necessity determination — stays human because:** Decision Determinism L + Risk/Compliance H produce the URAC/NCQA accreditation condition that Dr. Marcus Webb named as non-negotiable (Exchange 2): every claim with clinical content requires physician or advanced practice provider sign-off before finalisation; his team will not certify any system that bypasses this review. This is not a limitation of available LLM capability — it is a regulatory compliance requirement with patient care and legal liability consequences, enforced by a named stakeholder with explicit veto authority. The agent's entire WS2 value proposition is in the quality of the pre-filled packet delivered to this gate, not in what happens at the gate. **Agent role:** The Clinical Review Support Agent assembles the complete clinical context (WS2-JtD-2) and delivers it to the physician queue; the Queue & SLA Management Agent ensures the physician's queue is prioritised by claim age; the WS1 agent's classifier reduces the volume arriving at this gate to only the 35% of claims with genuine clinical content. **Future delegation path:** No clear path; URAC/NCQA accreditation is the ceiling, not a target to design around. If accreditation standards change — or if Greenfield operates in a jurisdiction with different requirements — this assignment requires re-evaluation with Dr. Webb's team. Do not design toward this boundary.

---

> **APP-JtD-1 / APP-JtD-2 — Denial appeals (administrative and clinical) — human-led because:** Context Complexity H, Exception Rate H (41% overturn rate — scenario.md), and Risk/Compliance H on both JtDs place these firmly in Human-led + Agent Support. For administrative appeals (APP-JtD-2 administrative sub-type), Decision Determinism M and a defined review outcome make agent support meaningful; the agent synthesises prior context and proposes a determination. For clinical appeals (APP-JtD-2 clinical sub-type), the same URAC/NCQA physician sign-off requirement that governs WS2-JtD-3 applies — a clinical appeal determination is a new clinical determination, not an administrative review. **Agent role:** Wave 3 Appeals Support Agent classifies root cause, surfaces relevant prior context, and drafts a provisional determination for the administrative sub-type. It flags clinical sub-types for physician routing. **Future delegation path:** If WS1 quality improvement significantly reduces the appeal volume and narrows the root cause distribution to a smaller, more pattern-consistent set of cases, APP-JtD-1 could be promoted to Agent-led + Human Oversight for the administrative sub-type. The clinical sub-type has no delegation path (same URAC constraint as WS2-JtD-3). This evaluation should happen 90 days post-WS1 go-live when the residual appeal pattern is measurable (D2C §10).

---

> **WS2-JtD-2 — Clinical context assembly — conditionally agentic, currently blocked:** This JtD is assigned Agent-led + Human Oversight in D2B, but its Wave 2 build is blocked by an unresolved prerequisite: the clinical notes source system is unknown (A-D0C-7), and without a programmatic API to retrieve clinical documentation, the pre-filled review packet cannot be assembled by the agent. If discovery reveals that clinical notes are inaccessible programmatically (fax-only, EHR vendor API restrictions, HIPAA/BAA constraints on programmatic access), this JtD reverts to Human-led + Agent Support at best — the physician manually retrieves documents, and the agent processes whatever is provided. The architecture documents this as a conditional assignment, not a confirmed one. It is the right boundary for the engagement's ambitions; it is not yet confirmed as achievable. **Agent role (if integration confirmed):** See §2, Agent 3. **Agent role (if integration blocked):** Physician assembles clinical documentation manually; agent assists with prior auth history synthesis and structured note-taking only. **Future delegation path to full delegation:** Requires clinical notes source system API access confirmed in Wave 1 discovery.

---

## 6. Assumption Log

> **Assumption [A-D3-1]:** Contract exception rules for WS1-JtD-3 exist in some form and can eventually be encoded in a structured, accessible data system, even if that encoding is not complete at go-live.
> **Source:** Inferred from D2B §5 (contested assignment defence for WS1-JtD-3) and D2A A-D2A-5.
> **Why it matters:** The ADR-1 decision to hold WS1-JtD-3 at Agent-led + Human Oversight is a temporary assignment, not a permanent one. If contract exceptions cannot be encoded (because they are informal, ad hoc, or undocumented), WS1-JtD-3 must remain at Agent-led + HITL indefinitely and the 85% auto-adjudication benchmark target cannot be reached.
> **If wrong:** If contract exceptions exist only in employees' institutional knowledge with no documentation, a pre-encoding effort (structured data entry project) becomes a prerequisite before WS1-JtD-3 can be promoted — changing the Wave 1 build scope.
> **Confidence:** Low — contract exception storage is unknown (A-D0C-6); assumption is consistent with standard payer operations but unconfirmed.

---

> **Assumption [A-D3-2]:** The clinical content classification task for WS1 routing and WS2 verification is the same underlying decision, solvable with a single trained model at two configurable confidence thresholds — the routing and verification use cases do not require fundamentally different criteria or training datasets.
> **Source:** Inferred from D2A §4 cross-work-stream observation 1 (shared classifier component) and D2B §3 (WS1-JtD-2 and WS2-JtD-1 both reference the same undefined clinical content criterion).
> **Why it matters:** ADR-2's single-classifier architecture depends on this assumption. If WS1 routing (minimise over-routing to physician queue) and WS2 verification (minimise under-routing of clinical claims) require different feature signals or different training label definitions, one model serving both uses will produce systematic errors in one or both directions.
> **If wrong:** If the two use cases require materially different classifiers, the architecture must deploy two separately certified models — doubling CMO certification effort and eliminating the primary benefit of ADR-2's chosen path.
> **Confidence:** Medium — supported by D2A's cross-work-stream observation that both JtDs depend on the same clinical content definition; the assumption holds if that definition is precise enough to operationalise as a single classifier training specification.

---

> **Assumption [A-D3-3]:** WS1 processing volume (1,300 claims/day) can be handled by a single orchestrating agent deployment with acceptable throughput and no sub-minute latency requirement at the individual claim level.
> **Source:** Inferred from scenario_context.md §4 (7-day SLA threshold with batch processing acceptable) and D2B §3 (Latency Constraint scored L for all WS1 JtDs).
> **Why it matters:** ADR-3's single-agent architecture is justified in part by the absence of sub-minute latency requirements. If a specific claim type (emergency services, same-day care) requires real-time adjudication, the single-agent design must be revisited before that claim type is in scope.
> **If wrong:** If throughput requirements exceed what a single agent can serve (to be established during load testing), or if a latency requirement emerges for a specific claim subtype, WS1-JtD-2 (the Sonnet-heavy judgment step) should be extracted as a callable service first — it is the most independent step in the pipeline and the most computationally intensive per claim.
> **Confidence:** Medium — Latency L scoring is consistent across all WS1 JtDs in D2A; no real-time adjudication requirement is stated in the scenario; the 7-day SLA is orders of magnitude above any LLM inference latency.

---

> **Assumption [A-D3-4]:** The HITL escalation queue for WS1 (estimated at ~25% of WS1 claims = ~325 HITL events/day) can be managed by the post-reduction team of 7 reviewers alongside WS2 clinical support, producing a sustainable operations model within James Liu's target (Exchange 3).
> **Source:** Derived from D2C §8 HITL rate model (25% aggregate) applied to WS1 volume (1,300/day) and James Liu's 20→7 reviewer target (Exchange 3).
> **Why it matters:** The entire headcount reduction case (CFO target: 8 FTE reduction, Exchange 1; James Liu target: 20→7, Exchange 3) assumes that 7 reviewers can handle both WS1 HITL exceptions and WS2 clinical co-ordination. If HITL rates are higher than 25%, the residual team is understaffed and either cycle time relapses or the headcount target must be revised.
> **If wrong:** If HITL rates run at 35% (conservative scenario in C1 §10), the daily HITL event volume rises to ~455/day — requiring approximately 11 FTEs at the C1 time model — more than James Liu's 7-reviewer target. The architecture remains structurally sound; the headcount model requires revision.
> **Confidence:** Low — HITL rate is the load-bearing assumption in both the economics model (C1) and the staffing model; it is a design target, not a measured baseline.
