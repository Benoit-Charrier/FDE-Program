# 05 — Architecture Decision Records
## Greenfield Health Systems: Medical Claims Adjudication Transformation

*Three ADRs covering the principal design choices in the WS1 Administrative Adjudication Agent architecture. Full solution architecture context — workflow-to-agent mapping, agent designs, and autonomy matrix — is in `D3_agentic_solution_architecture.md`.*

*Source inputs: `Deliverables/D2A_cognitive_load_map.md`, `Deliverables/D2B_delegation_suitability_matrix.md`, `Deliverables/D2D_token_economics_model.md`, `Scenario/scenario_context.md`.*

---

## ADR-1: Delegation level of WS1-JtD-3 — payment determination

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

## ADR-2: Single shared clinical content classifier vs. separate classifiers per work stream

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
| Rules-based routing (no classifier) | Fully deterministic; no training data required; auditable enumeration of clinical triggers | Rejected: the current processor-based routing with undocumented heuristics already produces the 41% denial appeal overturn rate (scenario.md); a rules engine can enumerate known clinical patterns but cannot handle novel code combinations or multi-factor signal — the same limitation that makes processor inconsistency the root cause of the overturn problem |

**Consequences:**
- *Enables:* Single CMO certification event in Wave 1 covers both WS1 routing and WS2 verification; classifier improvements in Wave 1 calibration propagate to WS2 verification without re-certification; shared versioning means both agents always see the same classification output for the same input
- *Forecloses:* Cannot independently tune WS1 routing precision and WS2 verification recall as if they were separate design problems; if calibration reveals that optimal thresholds for the two use cases conflict, the architecture must support two separately configurable thresholds on the same underlying model — this must be designed into the classifier service interface from the start
- *Assumes:* The clinical content classification task for routing and the task for verification are the same problem solved once (A-D3-2); if the CMO team determines that routing and verification require fundamentally different criteria, this decision requires revisiting

**Revisit condition:**
Calibration data shows that the optimal confidence threshold for WS1 routing (minimising physician queue over-routing — false positives) materially conflicts with the optimal threshold for WS2 verification (minimising administrative payment path false negatives). At that point, the classifier service must expose two configurable threshold parameters rather than one shared value, and both configurations must be included in the CMO certification process.

---

## ADR-3: Single WS1 orchestrating agent vs. pipeline of micro-agents

**Status:** Proposed

**Context:**
WS1 involves 10 micro-tasks across 3 JtDs, mixing deterministic tool calls (eligibility lookup, code validation API, prior auth lookup, fee schedule calculation — no LLM tokens) with Sonnet LLM judgment calls (coding plausibility, eligibility discrepancy, prior auth partial match, clinical content routing, contract exception handling — ~2.15 average LLM calls per claim, D2D §3). These could be implemented as a single orchestrating agent that manages all micro-tasks, or as a pipeline of smaller agents — each specialising in a subset of the workflow (e.g., one agent for validation, one for routing, one for payment). Both patterns are deployed architectures in enterprise LLM systems.

**Decision:**
Implement WS1 as a single orchestrating agent that calls deterministic tools for the five structured micro-tasks and invokes Sonnet for the five judgment micro-tasks, rather than decomposing WS1 into multiple agents chained in a pipeline.

**Alternatives considered:**

| Alternative | Trade-offs | Why rejected |
|-------------|------------|--------------|
| Single WS1 orchestrating agent *(chosen)* | Simpler state management; single audit trail; single deployment unit; no inter-agent context passing overhead | *(chosen)* |
| Pipeline of micro-agents (one per JtD, three agents total) | Better separation of concerns per JtD; each agent independently testable; independent deployment of WS1-JtD-2 (routing) from WS1-JtD-1 (validation) | Rejected: WS1-JtD-1 through WS1-JtD-3 are serially dependent on a single claim record — the output of each step is the input to the next; no parallelism is possible or useful; chaining three agents produces inter-agent context-passing overhead (full claim record must be serialised and passed between agents) and complicates HITL state management (a HITL escalation at WS1-JtD-1 must pause the entire pipeline; a pipeline that pauses mid-chain requires recovery logic that a single agent handles naturally) |
| Rules engine with targeted LLM calls | Lowest token cost on the deterministic path; clearest audit trail for rule-based steps | Rejected as a standalone architecture: the deterministic steps within WS1 are already implemented as tool calls and code within the single agent (D2D §3); as a wholesale replacement, a rules engine cannot handle clinical plausibility assessment (MT-WS1-5, DD=L, no formal rule) or clinical content routing (MT-WS1-8, DD=L, no formal criterion) — the two highest-volume exception sources |

**Consequences:**
- *Enables:* Linear, auditable claim processing record; straightforward HITL state management (agent flags a breakpoint, pauses, human resolves, agent resumes from the same state); single deployment unit for Wave 1 delivery
- *Forecloses:* Independent scaling of individual processing stages (e.g., cannot scale the clinical content routing step in isolation from eligibility verification if one step becomes a throughput bottleneck); a change to any WS1 micro-task requires testing the full pipeline rather than just the affected stage
- *Assumes:* WS1 processing volume (1,300 claims/day) can be handled by a single-agent deployment with acceptable throughput within the 7-day SLA; no sub-minute latency requirement exists at the individual claim level (A-D3-3)

**Revisit condition:**
WS1 processing volume exceeds the single-agent throughput ceiling (to be established during capability specification load testing), or a sub-minute latency requirement emerges for a specific claim type (e.g., emergency service claims). At that point, WS1-JtD-2 (the Sonnet-heavy routing step) is the first candidate for extraction into a separate callable service.
