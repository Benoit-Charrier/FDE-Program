# Deliverable D3 — Agentic Solution Architecture: MedFlex Clinical Workforce Staffing

*Source: `Deliverables/D2A_cognitive_load_map.md`, `Deliverables/D2B_delegation_suitability_matrix.md`, `Deliverables/D2C_volume_value_analysis.md`, `Deliverables/D2_engagement_intake_scope.md`, `Scenario/scenario_context.md`. All design decisions trace to D2B archetype assignments, D2C priority scores, or are flagged as assumptions.*

---

## 0. Executive Summary

- **Primary agentic target:** WS2 nurse-to-shift matching backbone — specifically WS2-JtD-2 (candidate pool identification, Fully Agentic, D2B score 5/7) running as the core of the Intake & Matching Agent — replaces the coordinator's manual database-query-to-shortlist cycle, compressing the 4.2-hour average time-to-fill to under 60 minutes for 85% of fills; the coordinator retains final candidate selection (WS2-JtD-3, Human Only) as the governance and adoption anchor.
- **Central architectural decision:** A single orchestration agent (Intake & Matching Agent) handles the WS1 extraction → WS2 matching → WS3 credential check pipeline as sequential tool calls within one context window, rather than a multi-agent pipeline with inter-agent message passing — rejected because WS1's hard/soft credential classification must be available as context during WS2's database query, and fragmented agent contexts break that dependency.
- **Primary production constraint:** WS2-JtD-3 (optimal candidate selection) is Human Only because no structured facility preference profiles exist [D0C: U-3] — this is the single gate that prevents the architecture from reaching the 85% autonomous fill target until facility profiles are built, validated, and confirmed as reliable agent inputs; without them, the autonomous backbone stalls at shortlist generation and the coordinator makes every selection.

---

## 1. Table of Contents

- [0. Executive summary](#0-executive-summary)
- [1. Table of contents](#1-table-of-contents)
- [2. Workflow-to-agent mapping](#2-workflow-to-agent-mapping)
- [3. Agent design summary](#3-agent-design-summary)
- [4. Autonomy matrix](#4-autonomy-matrix)
- [5. Architecture decision records](#5-architecture-decision-records)
- [6. Non-agentic residual](#6-non-agentic-residual)
- [7. Assumption log](#7-assumption-log)

---

## 2. Workflow-to-agent mapping

| JtD (from D2B) | Delegation archetype (D2B) | Agentic? | Agent / role assigned | Justification |
|---|---|---|---|---|
| WS1-JtD-1: Message classification and routing | Human-led + Agent Support | Partial (HITL) | Intake & Matching Agent | D2B 3/7: Tool Coverage H enables auto-routing for standard facility templates; Input Structure L and Exception Rate M require HITL for non-standard or combined-type messages; misclassification is recoverable, so partial delegation is safe |
| WS1-JtD-2: Parameter extraction from unstructured request | Human-led + Agent Support | Partial (HITL) | Intake & Matching Agent | D2B 1/7: despite low score, LLM extraction from free text is the minimum required capability — no script or RPA alternative exists for unstructured intake [DS-confirmed]; agent extracts high-confidence fields (datetime, facility name via lookup, urgency signal) and pre-populates structured brief in HITL queue; coordinator completes remaining fields (specialty, credential level, unit type) in under 90 seconds — brief completion mode, not shadow mode; brief enters WS2 with all fields populated |
| WS1-JtD-3: Credential requirement ambiguity resolution | Human Only | No | Coordinator | D2B 0/7: Decision Determinism L (no governing rule exists [A-WS1-2]); Tool Coverage L (no facility preference profiles [D0C: U-3]); Risk H (wrong interpretation propagates to WS2 mismatch rate); blocking dimension: Tool Coverage L — no data to support agent judgment |
| WS1-JtD-4: Urgency classification and queue assignment | Agent-led + Human Oversight | Partial (HITL) | Intake & Matching Agent | D2B 4/7: explicit urgency is fully deterministic; implicit urgency (inferred from datetime proximity) requires agent-level datetime inference; human oversight preserved for edge case where pre-emption is triggered with ambiguous signal; same-day fill loss is high-cost at competitive fill rates [DS-confirmed] |
| WS2-JtD-1: Brief completeness check before matching | Agent-led + Human Oversight | Partial (HITL) | Intake & Matching Agent | D2B 2/7: schema validation (fields present/absent) is deterministic and agent-executed; judgment edge (ambiguous specialty term vs. missing field) requires HITL routing; this is the WS1→WS2 cascade error firewall [D2A: Obs 1] |
| WS2-JtD-2: Candidate pool identification from nurse database | Fully Agentic | Yes | Intake & Matching Agent | D2B 5/7: Input Structure H, Decision Determinism H, Tool Coverage H, Context Complexity L, Exception Rate L; credential rules (HR-1, HR-2, HR-3, HR-4) are deterministic and applied more consistently by agent than coordinators; D2C AV Score 20 — primary agentic target |
| WS2-JtD-3: Optimal candidate selection via institutional knowledge | Human Only | No | Coordinator | D2B 0/7: Decision Determinism L, Tool Coverage L (facility heuristics tacit and unstructured [DS-confirmed]), Context Complexity H, Exception Rate H; blocking dimensions: Tool Coverage L + Decision Determinism L — no structured facility preference data exists to support agent judgment; assigning any autonomous archetype here replicates the recommendation engine failure [A13] |
| WS2-JtD-4: Exception / no-candidate resolution | Human Only | No | Coordinator | D2B 0/7: Decision Determinism L, Input Structure L, Context Complexity H, Risk H; blocking dimension: Decision Determinism L — multiple resolution paths (expanded search, facility waiver, unfillable flag) with no governing rule; submitting a below-threshold candidate without human sign-off is a compliance event |
| WS2-JtD-5: Submission and multi-submission state tracking | Agent-led + Human Oversight | Partial (HITL) | Intake & Matching Agent | D2B 5/7: Input Structure H, Decision Determinism H, Tool Coverage H; submission is mechanical once coordinator selects candidate; simultaneous confirmation race condition (two facilities confirm before withdrawal) requires human to honour one and manage the apology — preserves HITL for that exception |
| WS2-JtD-6: First confirmation received — withdrawal execution | Agent-led + Human Oversight | Partial (HITL) | Intake & Matching Agent | D2B 4/7: single-confirmation withdrawal is fully deterministic (first confirmation → execute withdrawal); simultaneous confirmation requires HITL for relationship management decision; agent handles standard path autonomously |
| WS3-JtD-1: Credential status verification before submission | Fully Agentic | Yes | Intake & Matching Agent (tool call) | D2B 5/7: Input Structure H, Decision Determinism H, Tool Coverage H; binary database read + rule check; implemented as a tool call within the matching agent's submission step — not a standalone agent; provides final HR-1 gate before submission fires |
| WS3-JtD-2: Credential gap escalation to compliance team | Human-led + Agent Support | Partial (HITL) | Intake & Matching Agent + Coordinator | D2B 1/7: agent detects expiry proximity and surfaces gap to coordinator (date comparison is deterministic); escalation decision (block / hold / escalate to compliance team) requires coordinator judgment — no formal governance path exists for borderline credentials [A2A2] |
| WS4-JtD-1: Confirmation dispatch to nurse | Fully Agentic | No (RPA) | Rule-based automation | D2B 7/7: all dimensions at high suitability; placement record structured [DS-confirmed], SMS/email gateway confirmed [DS-confirmed]; no judgment or LLM reasoning required — deterministic, templated, event-triggered workflow; highest-confidence automation in the engagement but not an AI capability; delivered as separate RPA workstream |
| WS4-JtD-2: Acknowledgement monitoring and pre-shift escalation | Agent-led + Human Oversight | No (RPA, HITL escalation) | Rule-based automation | D2B 4/7: monitoring and escalation trigger are fully deterministic (time-to-shift < threshold AND no acknowledgement → write to HITL queue); no LLM reasoning required — scheduled polling with conditional record write; Tool Coverage M reflects placement status field assumption [A2A4]; coordinator decides what to do when escalation fires |
| WS4-JtD-3: Nurse withdrawal / renegotiation resolution | Human Only | No | Coordinator | D2B 0/7: Input Structure L (inbound phone call), Decision Determinism L (accommodate vs. negotiate vs. replace = relationship judgment), Tool Coverage L; blocking dimension: Decision Determinism L — no structured rate approval workflow or nurse relationship data exists to support agent judgment [A2A5, A2A6]; agent provides parallel replacement query but does not influence the conversation |
| WS4-JtD-4: No-show detection and response | Human-led + Agent Support | Partial (HITL) | Intake & Matching Agent (parallel replacement query) | D2B 0/7 but Human-led + Agent Support assigned: agent value is as parallel processor — agent simultaneously initiates compressed WS2 replacement query while coordinator manages facility call; coordinator owns all communication and replacement selection; agent-as-parallel-processor does not require autonomous decision authority |

**AI-native moment:** The Intake & Matching Agent produces an outcome that no rule-based system could reliably reach at WS2-JtD-2 during nurse profile note interpretation. When the agent generates a candidate shortlist, it must read free-text profile notes on shortlisted candidates (e.g., "historically reliable at Facility X but two late arrivals at Facility Y in Q3") and classify each note as: a hard blocking signal (remove from shortlist), a soft risk signal (include but flag for coordinator attention in WS2-JtD-3 HITL review), or a neutral informational record (include without flag). A rule-based SQL query or keyword filter cannot perform this classification — it cannot distinguish "declined three shifts at this facility" (blocking for this specific placement) from "prefers day shifts" (informational) from "prior incident resolved" (context-dependent, may or may not block). The agent reasons over the note content in the context of the specific facility, shift type, and urgency level and makes a consistent, explainable classification — providing the coordinator a shortlist where each candidate's note relevance is pre-adjudicated, not just raw note text. This AI-native step is what makes the shortlist genuinely useful rather than a filtered database dump that the coordinator must still read in full to apply the same judgment.

---

## 3. Agent design summary

> **Agent 1: Intake & Matching Agent**
> **Job to be done:** Convert a raw inbound shift request into a ranked, credential-verified candidate shortlist with submission executed on coordinator approval — and manage multi-submission state and withdrawal orchestration across all open shifts.
> **Workflow segments covered:** WS1-JtD-1, WS1-JtD-2, WS1-JtD-4, WS2-JtD-1, WS2-JtD-2, WS2-JtD-5, WS2-JtD-6; WS3-JtD-1 (embedded tool call); WS3-JtD-2 (detection step); WS4-JtD-4 (parallel replacement query on no-show trigger)
> **Tools required:**
> - ServiceNow read: inbound message queue, facility history (if available), existing placement records
> - ServiceNow write: structured matching brief, HITL queue items, placement record status updates, submission record creation
> - Nurse database query API: credential status, availability, proximity, profile notes [access unconfirmed — A-D3-1]
> - DNR list lookup: facility-specific exclusions [A-D3-2]
> - SMS/email notification gateway: outbound submission notification to nurse (post-confirmation)
> - HITL queue write: ambiguity flags (WS1-JtD-3), shortlist review requests (WS2-JtD-3), exception escalations (WS2-JtD-4)
>
> **Context required:** Full inbound message text; specialty taxonomy reference (for NLP extraction calibration); nurse database record for each shortlisted candidate (credentials, availability, profile notes); existing open placement records for the same nurse (multi-submission state); coordinator HITL queue state (active review items and time-to-fill clocks)
> **Escalation triggers:**
> - Specialty requirement is ambiguous (hard vs. soft) → flag to WS1-JtD-3 HITL queue
> - Required fields missing after extraction → flag to WS2-JtD-1 HITL with specific missing fields identified
> - Profile note on shortlisted candidate classified as "risk signal" → include candidate but flag for WS2-JtD-3 coordinator review
> - No candidate passes first-pass shortlist → route to WS2-JtD-4 HITL with available exception options surfaced
> - Simultaneous confirmation received before withdrawal completes → pause withdrawal, route to coordinator for race condition resolution
> - Credential expiry within N days detected → surface gap with renewal timeline to WS3-JtD-2 HITL
>
> **Governance constraint:** HR-1 (credential verification as hard stop) is enforced at two points within this agent: (1) WS2-JtD-2 query filters all candidates whose credential status does not pass specialty + state match; (2) WS3-JtD-1 re-checks credential status immediately before WS2-JtD-5 submission executes. No submission can bypass either gate. The agent must never produce a shortlist or execute a submission for a candidate flagged invalid in the nurse database.

---

> **WS4 — Confirmation & Monitoring Workflow (rule-based automation, not an AI agent)**
> **Job to be done:** Send structured confirmation requests to nurses at placement confirmation and monitor acknowledgement status; escalate unacknowledged placements to the coordinator HITL queue before the shift window closes.
> **Workflow segments covered:** WS4-JtD-1, WS4-JtD-2
> **Implementation:** Scheduled polling job + event-driven trigger — no LLM invocation at any step; logic is fully deterministic (if placement confirmed AND no acknowledgement AND time-to-shift < threshold → write to HITL queue). Delivered as a separate RPA workstream, not as part of the Intake & Matching Agent.
> **Integrations required:**
> - ServiceNow read: active placement records (nurse contact, shift datetime, confirmation status, outbound notification timestamp)
> - ServiceNow write: confirmation outbound timestamp, acknowledgement response record, escalation status
> - SMS/email notification gateway: outbound structured confirmation request; acknowledgement capture (inbound response or link-click)
> - HITL queue write: pre-shift escalation alert with shift details and nurse contact
>
> **Trigger to AI agent:** On explicit nurse decline or confirmed no-show, the workflow fires a trigger to the Intake & Matching Agent to initiate a parallel replacement candidate query (WS4-JtD-4) — this is the only handoff point between WS4 and the AI agent.
> **Governance note:** HR-5 (mandatory rest periods) is checked by the Intake & Matching Agent when it processes the replacement query trigger — not by this workflow.

---

## 4. Autonomy matrix

| Action | Agent decides alone | Agent acts, human notified | Agent proposes, human approves | Human takes over |
|--------|--------------------|-----------------------------|-------------------------------|-----------------|
| Classify inbound message as standard type (recognised facility template) | ✓ | | | |
| Classify inbound message — ambiguous or non-standard type | | | ✓ coordinator confirms type | |
| Extract structured matching brief from free text | | | ✓ coordinator validates hard/soft interpretation | |
| Classify urgency — explicit signal (stated deadline, same-day language) | ✓ | | | |
| Classify urgency — implicit (inferred from datetime proximity, no label) | | | ✓ coordinator confirms pre-emption | |
| Validate brief completeness (required fields present/absent) | ✓ | | | |
| Route incomplete brief to HITL with specific gap identified | | ✓ | | |
| Query nurse database: credential match (HR-1, HR-2, HR-3) | ✓ | | | |
| Apply DNR exclusion check (HR-4) | ✓ | | | |
| Apply availability and proximity filters | ✓ | | | |
| Interpret nurse profile notes (classify as blocking / risk-signal / neutral) | ✓ | | | |
| Present ranked shortlist with credential citations to coordinator queue | | ✓ | | |
| Select final candidate from shortlist | | | | ✓ coordinator owns |
| Resolve exception when no candidate passes first-pass shortlist | | | | ✓ coordinator owns |
| Re-check credential status immediately before submission (WS3-JtD-1) | ✓ | | | |
| Execute submission to facility (Wave 2 Phase 1 — HITL approval required) | | | ✓ coordinator approves each submission | |
| Execute submission to facility (Wave 2 Phase 2 — autonomous clean fills) | | ✓ | | |
| Log open submission and update multi-submission state | ✓ | | | |
| Execute withdrawal from remaining open submissions — single confirmation | | ✓ | | |
| Execute withdrawal — simultaneous confirmation (race condition) | | | ✓ coordinator selects which facility to honour | |
| Detect and flag credential expiry proximity | | ✓ | | |
| Decide whether to block, hold, or escalate borderline credential to compliance team | | | | ✓ coordinator owns |
| Send active confirmation request to nurse *(rule-based automation)* | ✓ | | | |
| Monitor placement acknowledgement status *(rule-based automation)* | ✓ | | | |
| Escalate unacknowledged placement to HITL queue ≥2 hours before shift start *(rule-based automation)* | | ✓ | | |
| Resolve nurse withdrawal or post-acceptance renegotiation | | | | ✓ coordinator owns |
| Initiate parallel replacement candidate query on no-show escalation | | ✓ (triggers Intake & Matching Agent) | | |
| Manage facility communication on confirmed no-show | | | | ✓ coordinator owns |
| Approve replacement submission after no-show | | | | ✓ coordinator owns |

**Hardest boundary:** The submission execution step (Wave 2 Phase 1: "Agent proposes, human approves" → Phase 2: "Agent acts, human notified") sits closest to the line between HITL and autonomous operation and is the boundary that Marcus will push on hardest during the verbal defense. In Wave 2 Phase 1, every submission requires coordinator approval before execution — the agent has selected the candidate (via its structured query) but the coordinator clicks to confirm before the outbound offer goes to the facility. The argument for moving this to "Agent acts, human notified" (Phase 2) is compelling on throughput grounds: at 960+ decisions/day, requiring a coordinator click on every clean fill consumes the coordinator capacity the agent was supposed to free. The argument for keeping it at "Agent proposes, human approves" in Phase 1 is adoption: the prior recommendation engine failed not because the technology was wrong but because coordinators could not verify the outputs and felt their judgment was being replaced [DS-confirmed: A13]. A Phase 1 that requires the coordinator's click but shows them the credential basis for each shortlist candidate is a trust-building exercise — each approved clean fill builds the coordinator's confidence in the agent's credential logic, and coordinator agreement rate above 85% over 4 weeks is the gate that unlocks Phase 2 autonomous submission. The boundary is here because the transition from HITL to autonomous requires evidence of trust, not just technical capability.

---

## 5. Architecture Decision Records

---
**ADR-1: Delegation level for WS2-JtD-3 (optimal candidate selection)**

**Status:** Proposed

**Context:**
WS2-JtD-3 is the final selection step in the matching pipeline — the coordinator reviews the agent-produced shortlist (from WS2-JtD-2) and selects the candidate to submit. D2B scores this JtD 0/7 with Human Only archetype on all three blocking dimensions: Decision Determinism L (selection among qualified candidates requires facility heuristics not in any system), Tool Coverage L (no structured facility preference profiles exist [D0C: U-3]), and Context Complexity H (facility relationship history lives in coordinator memory [DS-confirmed]). The prior recommendation engine failed at exactly this step — coordinators could not verify the engine's recommendation and felt their judgment was being overridden [DS-confirmed: A13]. The question is whether any autonomous archetype is appropriate in the architecture's initial wave, given that some automation is needed to demonstrate throughput improvement.

**Decision:**
WS2-JtD-3 is Human Only in Wave 2 Phase 1; the agent presents a ranked shortlist with explicit credential citations and profile note flags, and the coordinator selects the final candidate.

**Alternatives considered:**

| Alternative | Trade-offs | Why rejected |
|-------------|------------|--------------|
| Human Only — agent presents shortlist, coordinator selects (chosen) | Cost: coordinator selection adds 30 seconds per clean fill and cannot be parallelised; throughput gain from WS2-JtD-2 is partially offset. Enables: coordinator trust in agent outputs is built through visible, verifiable shortlists; adoption risk from A13 is managed; compliance safety record begins accumulating | *(chosen)* |
| Agent-led + Human Oversight — agent selects, coordinator can override | Cost: requires facility preference profiles or confidence scoring model to rank beyond credential match; neither exists. Enables: full throughput if coordinators accept agent selections. Rejected: replicates the recommendation engine pattern — agent recommends, coordinator cannot verify the recommendation basis, adoption fails quietly; no facility profiles to drive ranking logic beyond credential match |
| Fully agentic for high-confidence cases (e.g., single qualifying candidate) | Cost: requires a "confidence" heuristic to define "high-confidence" — how many qualifying candidates, no profile notes, no prior exceptions. Enables: removes human from the truly trivial cases. Rejected: even single-candidate fills require coordinator to confirm the agent didn't miss a profile note or facility restriction; the legal and relationship liability of an autonomous single-candidate submission without human review is not justified at this stage of trust-building |

**Consequences:**
- *Enables:* Adoption safety — coordinators remain in the selection loop; each selection builds the trust foundation for Phase 2 autonomous submission; compliance liability stays with human judgment at the critical moment
- *Forecloses:* Full throughput at Phase 1; the 85% autonomous fill rate target (D1 AR-1) is not achievable in Phase 1 — the agent handles all database querying but every selection requires a coordinator click; Phase 2 autonomous submission (clean fills only) is the mechanism that closes this gap
- *Assumes:* A "clean fill" is one where WS2-JtD-2 produces a shortlist with no profile-note risk signals, no simultaneous-submission conflicts, and a clear top-ranked candidate — and that this category comprises ≥70% of fills [D0C: U-2; A-D2B-4]

**Revisit condition:**
When coordinator agreement rate on the agent's top-ranked candidate exceeds 85% over a sustained 4-week period AND no HR-1 violations have been recorded in agent-generated shortlists during that period — the Phase 2 autonomous submission gate is met and clean-fill submissions no longer require coordinator pre-approval. At that point, WS2-JtD-3 upgrades to Agent-led + Human Oversight for clean fills.

---

**ADR-2: Architecture pattern — single orchestration agent vs. multi-agent pipeline for WS1→WS2→WS3**

**Status:** Proposed

**Context:**
The WS1 extraction, WS2 matching, and WS3 credential check form a sequential pipeline where each stage's output is the next stage's primary input. The key dependency is that the hard/soft credential classification determined in WS1 (or resolved by the HITL coordinator in WS1-JtD-3) must be present and consistent when WS2-JtD-2 constructs its database query — a strict filter (certified required) produces a different candidate pool than a preference filter (certified preferred). A multi-agent design with separate Intake Agent and Matching Agent communicating via message-passing must serialize the credential classification result across an inter-agent boundary. The question is whether that boundary introduces fragmentation risk that exceeds its modular benefits.

**Decision:**
A single Intake & Matching Agent handles WS1 extraction, WS2 matching, and WS3 credential check as sequential tool calls within one context window. The WS1→WS2 handoff uses a **stable brief schema as the interface contract** — WS2 is always built to consume this schema regardless of whether WS1-lite (week-6 pilot), Wave 1 WS1 (brief completion mode), or Wave 2 WS1 (full pipeline) produced it. This decouples WS2 development from WS1 completion: WS2 can be built and piloted before WS1 reaches full pipeline coverage, because the schema is the contract, not who filled it in.

**Alternatives considered:**

| Alternative | Trade-offs | Why rejected |
|-------------|------------|--------------|
| Single orchestration agent with tool calls (chosen) | Cost: larger context window per invocation (WS1 text + WS2 query state + shortlist + profile notes); no clean modularity boundary between intake and matching logic. Enables: WS1 hard/soft classification is present in WS2 query construction without serialization; profile note interpretation can reference intake context; HITL queue items carry the full fill context | *(chosen)* |
| Separate Intake Agent + Matching Agent with message passing | Cost: inter-agent handoff must serialize the structured brief including hard/soft classification decision; if classification was a HITL resolution, the coordinator's reasoning may not be fully represented in the structured message. Enables: independent scaling and deployment of intake vs. matching; cleaner observability boundary. Rejected: the cascade error path [D2A: Obs 1] means the handoff boundary is exactly where errors propagate silently; a serialized brief that loses context about *why* a specialty was classified hard vs. soft means the Matching Agent cannot flag anomalies that the Intake Agent had flagged as uncertain |
| Microagents per JtD (one agent per job-to-be-done) | Cost: 10+ agent instantiations per fill cycle; coordination and state management overhead dominates compute cost; debugging a failure at WS2-JtD-2 requires tracing across multiple agent logs. Enables: maximum observability per micro-step; independent replacement of any JtD. Rejected: most JtDs in WS1 and WS2 are tool calls (structured DB query, field extraction, record write), not cognitive contracts requiring independent agent reasoning; the overhead of agent orchestration for tool-call-level operations is unjustified; JtDs that are genuinely complex (WS2-JtD-3, WS2-JtD-4) are Human Only and do not benefit from a microagent wrapper |

**Consequences:**
- *Enables:* Context continuity across the WS1→WS2 pipeline; the agent can reference the original request text when interpreting profile notes ("this profile note about Facility X is relevant because the intake request came from Facility X"); full fill context is visible in one agent trace for debugging
- *Forecloses:* Independent scaling of intake vs. matching workloads — if intake volume spikes (many new requests arriving) while matching backlog clears, a single agent architecture must handle both simultaneously rather than scaling the intake layer independently; this may require parallelised agent invocations rather than a single queue-processing loop
- *Assumes:* The context window required per fill (intake text + brief + shortlist + profile notes) remains manageable within the chosen model's context limit; estimated at 3,000–5,000 tokens per fill at current volume [A-D3-3]

**Revisit condition:**
If WS1 intake volume exceeds WS2 matching capacity by more than 3× during peak hours (sustained intake spike that builds a queue the single agent cannot process within the <60-minute latency constraint), the architecture should be split: WS1 extraction runs as a separate lightweight agent with cheaper model, outputs to a structured brief queue, and the Matching Agent pulls from that queue. The split point is latency degradation, not volume alone.

---

**ADR-3: Wave sequencing — confirmation automation before matching automation**

**Status:** Revised — revisit condition triggered

**Context:**
D2C Wave assignment places WS4 (active confirmation loop) and WS1 (NLP extraction) in Wave 1 and WS2 (matching agent) in Wave 2. The business case's primary value driver is WS2 — it is the throughput bottleneck and the revenue capacity unlock. The question is whether deploying WS4 and WS1 first genuinely enables WS2, or whether it is a delay that pushes the business-case deliverable out by 4–6 weeks unnecessarily.

**Decision:**
WS4 active confirmation loop and WS1 NLP extraction deploy in Wave 1; WS2 matching agent deploys in Wave 2 after WS1 extraction quality is validated and coordinator trust is established.

**Alternatives considered:**

| Alternative | Trade-offs | Why rejected |
|-------------|------------|--------------|
| WS4 first (Wave 1), WS2 in Wave 2 after WS1 validation (chosen) | Cost: WS2 business case (time-to-fill improvement, revenue capacity) is delayed by the Wave 1 deployment period (~8–12 weeks); Marcus sees throughput improvement later. Enables: WS1 extraction quality validated before WS2 depends on it (cascade error path prevented); coordinator trust built through WS4's visible, low-threat operational improvement before the adoption-risk WS2 agent deploys; 8-week checkpoint shows observable metric (no-show rate improvement) | *(chosen)* |
| WS2 and WS4 parallel deployment in Wave 1 | Cost: WS2 deploys before WS1 extraction is validated — cascade error path active at full speed from day one; coordinator trust-building is skipped — same vector as recommendation engine failure [A13]; WS1-JtD-3 HITL queue floods from raw free-text intake overwhelming coordinators simultaneously with the new matching interface. Enables: earlier WS2 throughput improvement for Marcus. Rejected: the two prerequisites for WS2 safety (WS1 quality gate and coordinator adoption trust) cannot be compressed into simultaneous deployment without creating a high probability of replicating the prior AI failure |
| WS2 deployed first as primary business-case driver | Cost: WS2 depends on WS1 producing clean structured briefs — deploying WS2 without WS1 means coordinators manually produce briefs, negating half the pipeline compression; adoption risk from prior recommendation engine failure is at maximum without a prior positive AI deployment experience at MedFlex. Enables: fastest route to the time-to-fill metric if coordinators adopt immediately. Rejected: coordinator adoption of a matching recommendation agent at a company with two prior AI failures is not a safe assumption; the WS4 deployment is the fastest route to building the adoption evidence that WS2 requires |

**Consequences:**
- *Enables:* Wave 1 provides measurable proof at the 8-week checkpoint (no-show rate movement, WS1 extraction comparison data); builds the ServiceNow connector and HITL queue infrastructure that Wave 2 reuses without rebuilding; coordinator adoption track record before the higher-risk WS2 agent deploys
- *Forecloses:* Early WS2 throughput improvement; the 4.2-hour time-to-fill metric does not improve until Wave 2; Marcus cannot see the primary revenue-capacity business case demonstrated until week 12+; requires managing Marcus's expectations at the 8-week checkpoint against a no-show rate metric rather than the time-to-fill metric
- *Assumes:* WS1 extraction quality can be validated within the Wave 1 window (8–12 weeks) using shadow-mode comparison against coordinator extraction [A-D3-4]; coordinator trust is measurable through WS4's adoption (confirmation acknowledgement rate improving, no coordinator workarounds) before WS2 deploys

**Revisit condition:**
If Marcus explicitly confirms at the engagement kickoff that a no-show rate improvement at 8 weeks is an insufficient proof point and insists on time-to-fill demonstration, the wave sequencing must be renegotiated — the mitigation would be to scope Wave 1 to a WS2 pilot on a narrow sub-segment (e.g., one facility, one specialty type) in parallel with WS4, accepting the adoption risk for that sub-segment while building the broader trust foundation.

**Revision (triggered — see D6 P1 response):**
Marcus's P1 pushback ("my board update is in 6 weeks; WS2 goes live at week 12") meets this condition verbatim. Wave sequencing is revised as follows:

| Phase | Timing | Change from original |
|-------|--------|----------------------|
| Wave 1 | Weeks 1–8 | WS1 in **brief completion mode** (replaces shadow mode) — coordinator actively completes partially-filled forms from day 1 of week 9; HITL queue live for coordinators; shared infrastructure built |
| **Narrow WS2 pilot** | **Week 6** | **New** — 1 facility, 1 specialty, 2 coordinators; WS1-lite produces stable brief schema; Intake & Matching Agent generates real shortlist; coordinator selects in HITL queue |
| Wave 2 Phase 1 | ~Week 12 | Unchanged — full WS2 HITL rollout to all 8 coordinators; WS1 cuts over to full pipeline |
| Wave 2 Phase 2 | Post-Phase 1 gate | Unchanged — autonomous clean-fill submissions |

**WS1-lite:** A constrained version of WS1 scoped to the week-6 pilot — extracts shift datetime, facility name (matched against a known facility lookup), and urgency signal. The remaining fields (specialty, credential level, unit type) are surfaced to the coordinator as a structured form to complete in under 90 seconds.

**Stable brief schema as interface contract:** WS2 is built to the stable structured brief schema from day 1. WS1-lite produces that schema. Wave 1 full WS1 produces that same schema with higher extraction coverage. Wave 2 WS1 produces that same schema autonomously. WS2 is never rewritten — the interface contract is fixed from week 6; only the producer side (WS1) evolves.

**Risk accepted:** API validation for a single facility must complete by week 4. Minimal HITL interface (shortlist view, approve button, time-to-fill clock) must be ready by week 5. The credential gate (WS3-JtD-1) is non-negotiable and active on day 1 of the pilot.

---

## 6. Non-agentic residual

> **WS1-JtD-3 — Credential requirement ambiguity resolution** — stays human because: Tool Coverage L (no structured facility preference profiles exist — the data the agent would need to resolve the ambiguity is missing [D0C: U-3]); Decision Determinism L (no governing policy for hard/soft interpretation exists [A-WS1-2]).
> **Agent role:** The Intake & Matching Agent flags the ambiguous specialty term with the specific phrase, the facility name, and both interpretation options (strict vs. preference); the coordinator resolves with a single selection in the HITL queue.
> **Future delegation path:** Once structured facility preference profiles are built (documenting each facility's standard interpretation for ambiguous specialty terms), this JtD upgrades to Human-led + Agent Support — the agent checks the profile before flagging, and flags only cases the profile does not resolve. The data enrichment project is the prerequisite, not the agent design.

> **WS2-JtD-3 — Optimal candidate selection via institutional knowledge** — stays human because: Tool Coverage L (facility heuristics, nurse reliability history, and soft preferences are in coordinator memory, not in any structured system [DS-confirmed]); Decision Determinism L (selection among equally-qualified candidates is judgment, not rules); this is the most consequential non-agentic gate in the architecture — assigning any autonomous archetype here without structured data replicates the recommendation engine failure [A13].
> **Agent role:** The agent presents a ranked shortlist with per-candidate credential citations, profile note classifications (blocking / risk-signal / neutral), and prior-submission history where available; the coordinator selects from this structured view rather than from raw data.
> **Future delegation path:** When facility preference profiles are structured, enriched with coordinator-annotated edge cases, and validated over a HITL training period (≥3 months, ≥500 selections with coordinator override rate <15%), this JtD upgrades to Human-led + Agent Support. This is the highest-value upgrade in the entire engagement; the facility profile enrichment project should begin in Wave 1 as a parallel data work stream, not deferred until Wave 2 is deployed.

> **WS2-JtD-4 — Exception / no-candidate resolution** — stays human because: Decision Determinism L (expanded search vs. facility waiver request vs. unfillable flag — no governing rule distinguishes when each is appropriate); Risk/Compliance H (submitting a below-threshold candidate without explicit human authorisation is a compliance event; the exception path is by definition outside the deterministic rules).
> **Agent role:** When no candidate passes first-pass shortlist, the agent surfaces: (1) an expanded search result with the relaxed filter applied, labelled with which constraint was relaxed; (2) the facility contact details for a waiver request; (3) an unfillable flag option. The coordinator selects among these options.
> **Future delegation path:** No clear path unless a formal exception workflow is defined — specifically, a structured set of rules for when MedFlex can submit a lower-credential candidate with explicit facility approval, and an API-accessible waiver request mechanism. Without these, the exception path remains Human Only.

> **WS4-JtD-3 — Nurse withdrawal / renegotiation resolution** — stays human because: Input Structure L (inbound phone call); Decision Determinism L (accommodate vs. negotiate vs. replace requires facility urgency tier, nurse relationship history, and rate approval authority — none of which are in any structured system [A2A5, A2A6]); this is a relationship management decision, not a process execution step.
> **Agent role:** While the coordinator is managing the renegotiation call, the Intake & Matching Agent is triggered to surface replacement candidates from the nurse database (same as WS4-JtD-4 parallel query) — the coordinator has a replacement shortlist ready if the renegotiation fails, without waiting for the call to conclude.
> **Future delegation path:** Partial — if nurse relationship preference data and rate approval parameters are structured, the agent could handle simple renegotiation cases (standard rate request within authorised range, standard unit swap) via a structured response menu. Full automation of this JtD is unlikely given the relationship sensitivity.

---

## 7. Assumption log

> **Assumption [A-D3-1]:** The nurse database exposes a queryable API that the Intake & Matching Agent can call with structured filter parameters (credential type, availability date range, proximity threshold, placement state) and receive a structured result set. The database is confirmed as structured [DS-confirmed]; the API interface — endpoint, authentication, rate limits, pagination, and response schema — is unconfirmed [D0C: U-6].
> **Source:** D2A DS-confirmed (database structured), D0C U-6 (API unconfirmed)
> **Why it matters:** The entire WS2-JtD-2 (Fully Agentic, D2B 5/7) depends on this API existing with queryable parameters. If only a read-all API exists (no filtering), the agent must load all nurse records and filter in-memory — manageable at current database size but a scaling risk at 14× volume.
> **If wrong:** If the nurse database is not API-accessible (e.g., a legacy SQL database requiring direct connection) or requires a separate integration build, Wave 2 development requires an integration sprint before agent development begins — impacting timeline.
> **Confidence:** Low — database confirmed as structured; API interface is the outstanding prerequisite.

> **Assumption [A-D3-2]:** A DNR (Do Not Return) list per facility exists as a queryable data structure in ServiceNow or the nurse database, accessible to the Intake & Matching Agent at WS2-JtD-2 execution time. DNR provisions are assumed as standard in MedFlex's facility contracts [scenario_context: A9]; the data representation is not confirmed.
> **Source:** Scenario_context A9 (HR-4 assumed as standard practice); D0C (not confirmed)
> **Why it matters:** HR-4 (DNR check before shift offer) is a non-negotiable hard exclusion in the matching pipeline. If DNR data is maintained only in coordinator-side notes or email threads rather than a structured, queryable field, the agent cannot enforce HR-4 — requiring the coordinator to manually verify DNR status, which defeats the purpose of the automated credential gate.
> **If wrong:** If no structured DNR list exists, a DNR data structuring project becomes a Wave 2 prerequisite before the Intake & Matching Agent can be certified as credential-safe for deployment.
> **Confidence:** Low — contractual requirement assumed; database representation unconfirmed.

> **Assumption [A-D3-3]:** The context window required per fill cycle for the single-agent orchestration architecture is approximately 3,000–5,000 tokens (intake message + structured brief + shortlist of 2–5 candidates with credentials + profile notes). This is within the context budget of a capable but cost-efficient model class (Claude Haiku equivalent) without requiring extended context or chunking.
> **Source:** Inferred from D2C A-D2C-5 (token estimate for WS2 matching agent ~2,500 tokens); adjusted upward for WS1 extraction text and profile notes
> **Why it matters:** ADR-2 chose the single-agent architecture on the basis of context continuity; if the actual context window requirement per fill is significantly higher (e.g., 20,000 tokens for facilities with extensive history or nurses with lengthy profile notes), the cost-efficient model tier may be insufficient and the architecture requires a different model or chunking strategy.
> **If wrong:** If extended nurse profile notes or long facility history contexts are common, the single-agent design may need to chunk profile notes before passing them to the matching agent — introducing a secondary NLP step that somewhat compromises the context continuity advantage of ADR-2.
> **Confidence:** Low — preliminary token estimate; requires profiling against real data.

> **Assumption [A-D3-4]:** WS1 NLP extraction can be validated against coordinator extraction within the Wave 1 window by running shadow mode (agent extracts alongside coordinator for the same intake messages) for 2–4 weeks on a representative sample of shift request types. Extraction accuracy of ≥95% on the validation sample is achievable within this window with prompt calibration against MedFlex's specialty taxonomy.
> **Source:** ADR-3 "Assumes" line; D2C A-D2C-6
> **Why it matters:** ADR-3 gates Wave 2 WS2 deployment on WS1 extraction quality validation. If 2–4 weeks of shadow mode is insufficient to validate extraction (e.g., because MedFlex's shift request volume is too low to produce a statistically representative sample), the Wave 2 gate cannot be cleared and the timeline for matching agent deployment extends.
> **If wrong:** If MedFlex's specialty terminology is highly variable (multiple informal names for the same credential, facility-specific shorthand not in any published taxonomy), prompt calibration requires an extended discovery sprint — documenting the taxonomy from coordinator knowledge before calibration can begin, adding 4–6 weeks to Wave 1.
> **Confidence:** Low-Medium — free-text intake confirmed as the baseline [DS-confirmed]; taxonomy documentation status is unknown.

> **Assumption [A-D3-5]:** The coordinator HITL queue (single unified review interface for WS1 ambiguity flags and WS2 shortlist reviews) is technically buildable as a ServiceNow module or lightweight web interface that writes back to ServiceNow records. The HITL queue must: display the time-to-fill clock, show the credential basis for each shortlist candidate, and capture the coordinator's selection as a recorded decision — all within a single view.
> **Source:** D2 §6a (in scope); D2B delegation boundary defence; inferred from ServiceNow as confirmed working surface [DS-confirmed]
> **Why it matters:** The HITL queue is the primary adoption lever for the WS2 matching agent — if it is poorly designed (slow, requires context switching, does not show the credential basis), coordinators will route around it and the agent fails for the same reason as the recommendation engine. The queue must be designed by a UX sprint with actual coordinators before Wave 2 deployment.
> **If wrong:** If ServiceNow's module capabilities cannot support the HITL queue design (e.g., cannot display custom views with time clocks and structured credential tables), the queue must be built as a separate web interface with ServiceNow write-back — adding integration scope to Wave 1.
> **Confidence:** Medium — ServiceNow is the confirmed working surface [DS-confirmed]; module configuration capabilities are an assumption.
