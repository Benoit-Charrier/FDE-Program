# Deliverable D2B — Delegation Suitability Matrix: MedFlex Clinical Workforce Staffing

*Source: `Scenario/scenario_context.md`, `Deliverables/D2A_cognitive_load_map.md`, `Deliverables/D0C_discovery.md`. All JtDs derived directly from D2A §2b, §3b, and §5. All numbers trace to scenario_context.md or are labelled as assumptions.*

---

## 0. Executive Summary

- **Delegation architecture:** Of 16 JtDs scored across 4 work streams, 8 are assigned agentic archetypes (fully agentic or agent-led + human oversight) forming an autonomous backbone that executes structured data operations, monitoring, and deterministic workflows at machine speed; 4 are Human Only gates that preserve coordinator judgment where no structured tool exists — specifically, soft credential ambiguity resolution (WS1-JtD-3), optimal candidate selection via tacit facility knowledge (WS2-JtD-3), and exception-path decisions with no governed escalation route (WS2-JtD-4, WS4-JtD-3).
- **Most contested archetype:** WS2-JtD-2 (candidate pool identification from nurse database) is assigned Fully Agentic despite High Risk/Compliance sensitivity; the tipping factor is that the credential rules are deterministic and the agent applies them more consistently than any individual coordinator — the governance constraint is enforced by data quality (compliance team's profile maintenance) rather than by human review at the query step; the assignment holds only while the data freshness dependency is met [A-D2B-1].
- **Primary governance constraint:** HR-1 (credential verification as hard stop before placement) is enforced at three levels — Fully Agentic at the database read layer (WS2-JtD-2, WS3-JtD-1), Human Only at the borderline-credential exception layer (WS2-JtD-3, WS3-JtD-2), and out-of-scope at the compliance team's profile maintenance layer; the constraint is non-negotiable at every layer and no archetype assignment overrides it.

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

JtDs are listed exactly as defined in D2A. No new JtDs are introduced here.

### WS1: Shift request intake (fully mapped in D2A §3b)

| JtD ID | Cognitive contract (one sentence) |
|--------|-----------------------------------|
| WS1-JtD-1 | Classify inbound ServiceNow message as new shift request, modification, cancellation, or other — and route to the correct workflow |
| WS1-JtD-2 | Extract structured matching parameters from unstructured shift request text, producing a matching brief WS2 can execute against |
| WS1-JtD-3 | Resolve whether a specialty requirement is a hard credential gate or a preference, clarifying with the facility or applying a judgment-based default |
| WS1-JtD-4 | Assign urgency classification (same-day vs. planned) and insert request at the correct priority position in the coordinator queue |

### WS2: Nurse-to-shift matching (fully mapped in D2A §2b)

| JtD ID | Cognitive contract (one sentence) |
|--------|-----------------------------------|
| WS2-JtD-1 | Verify the matching brief is sufficiently specified to begin database querying — or flag it for resolution before proceeding |
| WS2-JtD-2 | Identify a qualified candidate pool from the nurse database by applying credential, availability, proximity, and hard exclusion rules |
| WS2-JtD-3 | Select the optimal candidate from the qualified shortlist by applying institutional knowledge, facility heuristics, and profile notes not in the database |
| WS2-JtD-4 | Resolve the exception when no candidate passes the first-pass shortlist — escalate, expand search, or flag as unfillable |
| WS2-JtD-5 | Submit the selected nurse to the facility and manage simultaneous multi-submission state tracking across all open shifts |
| WS2-JtD-6 | Process the first confirmation received and execute withdrawal from all remaining open submissions for the same nurse before a race condition fires |

### WS3: Compliance / credential verification — coordinator scope only (abbreviated in D2A §5)

| JtD ID | Cognitive contract (one sentence) |
|--------|-----------------------------------|
| WS3-JtD-1 | Confirm that the selected nurse's credential status in the database is valid for the required specialty and placement state before proceeding to submission |
| WS3-JtD-2 | Determine whether a borderline or expiring credential status requires escalation to the compliance team before the fill proceeds |

### WS4: Placement confirmation and coordination (abbreviated in D2A §5)

| JtD ID | Cognitive contract (one sentence) |
|--------|-----------------------------------|
| WS4-JtD-1 | Send a structured shift confirmation request to the nurse and record the outbound timestamp in the placement record |
| WS4-JtD-2 | Monitor placement acknowledgement status and generate a pre-shift escalation alert when a placement remains unacknowledged past the configured threshold |
| WS4-JtD-3 | Resolve nurse withdrawal or post-acceptance renegotiation — deciding whether to accommodate, negotiate, or initiate a replacement fill |
| WS4-JtD-4 | Detect and respond to a confirmed no-show — manage facility communication and initiate a compressed replacement fill cycle if the window allows |

---

## 2. Delegation Suitability Matrix

Scoring key: **Input Structure, Decision Determinism, Tool Coverage** — H = high suitability; **Context Complexity, Exception Rate, Latency Constraint, Risk/Compliance** — L = high suitability. Suitability score = count of dimensions at high suitability (max 7).

| JtD | Work Stream | Input Structure | Decision Determinism | Tool Coverage | Context Complexity | Exception Rate | Latency Constraint | Risk/Compliance | Score | Archetype |
|-----|-------------|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|---|
| WS1-JtD-1: Message classification | WS1 | L | M | H | L | M | H | L | 3/7 | Human-led + Agent Support |
| WS1-JtD-2: Parameter extraction | WS1 | L | M | H | M | M | H | M | 1/7 | Human-led + Agent Support |
| WS1-JtD-3: Credential ambiguity resolution | WS1 | L | L | L | H | M | H | H | 0/7 | Human Only |
| WS1-JtD-4: Urgency classification | WS1 | M | M | H | L | L | H | L | 4/7 | Agent-led + Human Oversight |
| WS2-JtD-1: Brief completeness check | WS2 | M | M | H | L | M | H | M | 2/7 | Agent-led + Human Oversight |
| WS2-JtD-2: Candidate pool identification | WS2 | H | H | H | L | L | H | H | 5/7 | Fully Agentic |
| WS2-JtD-3: Optimal candidate selection | WS2 | L | L | L | H | H | H | H | 0/7 | Human Only |
| WS2-JtD-4: Exception / no-candidate resolution | WS2 | L | L | M | H | H | H | H | 0/7 | Human Only |
| WS2-JtD-5: Submission + multi-submission tracking | WS2 | H | H | H | L | M | H | L | 5/7 | Agent-led + Human Oversight |
| WS2-JtD-6: Confirmation withdrawal execution | WS2 | H | H | H | L | M | H | M | 4/7 | Agent-led + Human Oversight |
| WS3-JtD-1: Credential status verification | WS3 | H | H | H | L | L | H | H | 5/7 | Fully Agentic |
| WS3-JtD-2: Credential gap escalation | WS3 | M | M | M | M | L | H | H | 1/7 | Human-led + Agent Support |
| WS4-JtD-1: Confirmation dispatch | WS4 | H | H | H | L | L | M | L | 7/7 | Fully Agentic |
| WS4-JtD-2: Acknowledgement monitoring | WS4 | H | H | M | L | L | H | M | 4/7 | Agent-led + Human Oversight |
| WS4-JtD-3: Nurse withdrawal / renegotiation | WS4 | L | L | L | H | M | H | M | 0/7 | Human Only |
| WS4-JtD-4: No-show response | WS4 | L | L | M | H | M | H | M | 0/7 | Human-led + Agent Support |

**Score notes:**

- **Latency Constraint:** All MedFlex work streams operate under competitive or time-critical latency [DS-confirmed]. H latency is scored as low suitability per rubric; however, agent speed is an *argument for* delegation in this context — the latency constraint penalises human execution, not agent execution. This scoring artefact is noted but does not change archetype assignments.
- **Tool Coverage for WS1-JtD-2:** Scored H because LLM extraction capability is the proposed agent toolchain; the low Input Structure score captures that the task requires NLP reasoning, not that tooling is unavailable.
- **Risk/Compliance for WS2-JtD-2:** Scored H (low suitability) because credential errors are patient safety events. Archetype remains Fully Agentic because the rules are deterministic and agent application is more consistent than human; the compliance risk is managed by data quality, not by adding human review at this step.

---

## 3. Delegation Archetype Assignment with Rationale

> **WS1-JtD-1 — Message classification and routing**
> **Archetype:** Human-led + Agent Support
> **Rationale:** Tool Coverage H (ServiceNow accessible, LLM classification capable) and Context Complexity L (single-message classification) support agent assistance. Input Structure L (free text) and Exception Rate M (non-standard combined messages) mean the agent's classification cannot be trusted without human oversight for ambiguous cases. Standard messages can be auto-routed; non-standard messages surface a classification question to the coordinator before routing.
> **Governance rule impact:** None — misclassification at this step is correctable before credential or matching decisions are made.
> **Anti-pattern check:** A rules-based keyword classifier could handle the deterministic majority (standard facility template recognised → new shift), but would fail on combined-type messages. An agent outperforms a script here, confirming agentic archetype is warranted over RPA.

> **WS1-JtD-2 — Parameter extraction from unstructured request**
> **Archetype:** Human-led + Agent Support
> **Rationale:** Input Structure L (unstructured free text) and Decision Determinism M (hard/soft ambiguity is a real pattern per A-WS1-2) produce a score of 1/7. Despite the low score, this is an LLM-native task — precisely because the input is unstructured, this task cannot be assigned to a lower archetype (RPA/script cannot parse free text). The agent drafts the structured brief; the coordinator validates the specialty requirement interpretation before the brief is passed to WS2. Risk/Compliance M: extraction errors cascade to the mismatch rate.
> **Governance rule impact:** The cascade error path identified in D2A (Observation 1) makes coordinator validation of the hard/soft interpretation a prerequisite for clean-fill automation in WS2. Until facility preference profiles are structured [D0C: U-3], coordinator sign-off on each extracted brief is the error firewall.
> **Anti-pattern check:** Cannot be done by RPA or script — free text is confirmed as the intake baseline [DS-confirmed]. An LLM agent is the minimum required capability; this confirms the agentic archetype is correct rather than over-engineered.

> **WS1-JtD-3 — Credential requirement ambiguity resolution**
> **Archetype:** Human Only
> **Rationale:** Score 0/7 — all 7 dimensions point away from delegation. Decision Determinism L: no governing rule exists for hard-vs-soft interpretation [A-WS1-2]. Tool Coverage L: no structured facility preference profiles exist to query [D0C: U-3]. Context Complexity H: the correct interpretation requires facility relationship history that lives in coordinator memory. Risk/Compliance H: wrong interpretation propagates through WS2 and surfaces as a facility-reported mismatch.
> **Governance rule impact:** This JtD is the origin point for the preference-based portion of the 7% mismatch rate [DS-confirmed: dual causes]. Assigning any autonomous archetype here without structured facility profiles would accelerate wrong answers at machine speed.
> **Anti-pattern check:** Cannot be done by script, RPA, or agent without facility profiles. Upgrade condition: once facility preference profiles are structured and confirmed accurate, this JtD becomes Human-led + Agent Support.

> **WS1-JtD-4 — Urgency classification and queue assignment**
> **Archetype:** Agent-led + Human Oversight
> **Rationale:** Tool Coverage H, Context Complexity L, Exception Rate L, Risk/Compliance L produce a score of 4/7. Explicit urgency signals (stated deadline, same-day language) are deterministic — the agent classifies and queues without human input. Implicit urgency (shift datetime proximity without an explicit label) requires datetime inference which is technically within agent scope. Human oversight is appropriate for the edge case where urgency classification drives queue pre-emption with ambiguous signal.
> **Governance rule impact:** None directly — urgency errors produce fill delays, not compliance events.
> **Anti-pattern check:** Explicit urgency classification is solvable by a simple rule (datetime < threshold → urgent). The agent adds value over a script at the implicit urgency inference case and by integrating with the broader queue state. Agent-led is warranted over pure automation.

> **WS2-JtD-1 — Brief completeness check before matching**
> **Archetype:** Agent-led + Human Oversight
> **Rationale:** Tool Coverage H (brief completeness check against defined schema is queryable) and Context Complexity L (schema validation, not deep reasoning) provide the foundation. Decision Determinism M reflects that "is this brief complete?" has a deterministic core (required fields present/absent) but a judgment edge (is the specialty term usable or needs resolution?). The agent validates the brief and passes clean ones directly to WS2-JtD-2; incomplete or ambiguous briefs are routed to coordinator with a specific flag on what is missing.
> **Governance rule impact:** This JtD is the WS1→WS2 handoff gate. Cascade errors identified in D2A Observation 1 are caught here — incomplete briefs do not enter the matching pipeline.
> **Anti-pattern check:** Could be a static schema validator for the required-fields check. The judgment edge (ambiguous specialty term vs. truly missing) requires agent-level reasoning; agent is warranted.

> **WS2-JtD-2 — Candidate pool identification from nurse database**
> **Archetype:** Fully Agentic
> **Rationale:** Input Structure H, Decision Determinism H, Tool Coverage H, Context Complexity L, Exception Rate L produce a score of 5/7. Credential check (HR-1, HR-2, HR-3), DNR exclusion (HR-4), placement state validation, availability filter, and proximity filter are all hard rules applied against a confirmed structured database [DS-confirmed]. The agent executes these rules more consistently than any individual coordinator. Risk/Compliance H is present but does not override the archetype: the agent enforces the rules that ARE the compliance mechanism. Error risk is in data quality (compliance team's update cadence), not in agent judgment.
> **Governance rule impact:** HR-1, HR-2, HR-3 are enforced deterministically by the agent at this step. This is the most direct implementation of the primary hard constraint in the architecture. The agent never clears a credential-invalid candidate — this is non-negotiable behaviour.
> **Anti-pattern check:** The structured query + rule filter could be implemented as RPA against a static database. The agent adds value over RPA through real-time event-driven execution, integration with the multi-submission state, and DNR list cross-reference that may require dynamic lookup. Fully Agentic is appropriate; a simpler implementation would also be acceptable if the above integrations are handled separately.

> **WS2-JtD-3 — Optimal candidate selection via institutional knowledge**
> **Archetype:** Human Only
> **Rationale:** Score 0/7 — Decision Determinism L (judgment-dependent), Tool Coverage L (facility heuristics unstructured and not in any system [DS-confirmed]), Context Complexity H (facility relationship history, nurse reliability history, soft preferences), Exception Rate H (this JtD IS the exception-handling layer). This is the hardest HITL gate in the engagement and the one most at risk of being under-scoped. The agent presents the ranked shortlist from WS2-JtD-2 to the coordinator; the coordinator makes the final selection. The agent role at this step is display and surfacing, not decision-making.
> **Governance rule impact:** Assigning any autonomous archetype here without structured facility profiles would produce facility-preference mismatches at machine speed — replicating the failed recommendation engine pattern [DS-confirmed: A13]. Human Only is the adoption-safe assignment.
> **Anti-pattern check:** Cannot be done by script or RPA (no structured facility preferences to query). Cannot be done by agent without structured facility profiles. Upgrade condition: when facility preference profiles are structured, enriched, and validated over a HITL training period, this JtD may become Human-led + Agent Support.

> **WS2-JtD-4 — Exception path: no suitable candidate in first-pass shortlist**
> **Archetype:** Human Only
> **Rationale:** Score 0/7 — Input Structure L, Decision Determinism L (multiple possible resolution paths with no governing rule: expanded search, facility waiver request, unfillable flag), Context Complexity H (requires facility urgency assessment, waiver history, competitive context), Risk/Compliance H (submitting a below-threshold candidate without human sign-off is a compliance event). The agent surfaces the exception and presents available paths; the coordinator owns the resolution decision.
> **Governance rule impact:** Submitting a candidate who does not meet HR-1 or HR-2 on an exception basis requires explicit human authorisation — this is the override gate. No agent should be able to submit a credential-deficient candidate autonomously.
> **Anti-pattern check:** Not solvable by script or RPA. Human Only is correct; no upgrade condition until an explicit waiver workflow is defined and implemented.

> **WS2-JtD-5 — Submission and multi-submission state tracking**
> **Archetype:** Agent-led + Human Oversight
> **Rationale:** Input Structure H, Decision Determinism H (submission is a mechanical act; withdrawal trigger is deterministic: first confirmation received), Tool Coverage H (ServiceNow confirmed [DS-confirmed]), Context Complexity L produce a score of 5/7. Submission and withdrawal orchestration are fully automatable once the candidate is selected by the coordinator. The simultaneous confirmation race condition (two facilities confirm before withdrawal is processed) requires a human to determine which facility to honour — this exception keeps the archetype at Agent-led + Human Oversight rather than Fully Agentic.
> **Governance rule impact:** None directly — submission itself carries no compliance consequence provided the candidate passed WS2-JtD-2 and WS2-JtD-3.
> **Anti-pattern check:** Single-submission orchestration could be RPA. Multi-submission state tracking across concurrent placements requires event-driven monitoring that is beyond static RPA. Agent is warranted.

> **WS2-JtD-6 — First confirmation received: withdrawal execution**
> **Archetype:** Agent-led + Human Oversight
> **Rationale:** Input Structure H, Decision Determinism H (withdrawal trigger = first confirmation received), Tool Coverage H produce a score of 4/7. For the single-confirmation case, this is fully deterministic — agent monitors, detects first confirmation, fires withdrawal workflow, updates placement record. Human oversight activates only on simultaneous confirmation: two facilities confirm before withdrawal is processed, requiring the coordinator to decide which confirmation to honour and manage the apology workflow with the other facility.
> **Governance rule impact:** None — withdrawal is a relationship management action, not a compliance event.
> **Anti-pattern check:** Single-confirmation withdrawal could be done with a trigger rule. Simultaneous confirmation detection and smart race-condition handling requires agent-level state management. Agent is warranted over script.

> **WS3-JtD-1 — Credential status verification before submission**
> **Archetype:** Fully Agentic
> **Rationale:** Input Structure H, Decision Determinism H, Tool Coverage H, Context Complexity L, Exception Rate L produce a score of 5/7. Credential status is structured, pre-verified by the compliance team, and stored in the nurse database [DS-confirmed]. The check is binary: valid for required specialty and placement state → proceed; invalid → block and flag. Risk/Compliance H is present but — as with WS2-JtD-2 — the agent enforces the compliance rule more consistently than a human. The compliance risk is managed by the data source, not by adding human review at this check.
> **Governance rule impact:** This is the second implementation point of HR-1. It runs as a final gate before submission is executed at WS2-JtD-5 — ensuring no submission bypasses the credential check due to a gap between when WS2-JtD-2 ran and when the submission fires.
> **Anti-pattern check:** Could be implemented as a simple database lookup with a boolean result. An agent performs this as a tool call within the broader matching workflow; no separate agent is needed — it is a step within the matching agent's execution.

> **WS3-JtD-2 — Credential gap escalation to compliance team**
> **Archetype:** Human-led + Agent Support
> **Rationale:** Score 1/7 — Exception Rate L is the only high-suitability dimension. Input Structure M, Decision Determinism M (hard stop vs. timing question vs. waiver path = interpretation), Tool Coverage M (database accessible; compliance escalation channel is informal [A2A2]), Risk/Compliance H. The agent surfaces the credential gap with renewal timeline and gap severity; the coordinator decides whether to block, hold, or escalate to the compliance team. The coordinator owns the escalation decision because no formal governance path exists for borderline credentials.
> **Governance rule impact:** This is the exception gate for HR-1/HR-2. The agent cannot clear a borderline credential independently — only a human with compliance team access can authorise a hold-and-proceed.
> **Anti-pattern check:** A simple date comparison (credential expires within N days → flag) is RPA-appropriate for the detection step. The escalation decision itself requires judgment. Agent is warranted for the combined detection + escalation routing workflow; a script handles the detection only.

> **WS4-JtD-1 — Confirmation dispatch to nurse**
> **Archetype:** Fully Agentic
> **Rationale:** Score 7/7 — all dimensions at high suitability. Placement record is structured [DS-confirmed]; outbound notification via SMS/email is confirmed [DS-confirmed]; no judgment required; exception rate is negligible; latency constraint is M (2–3 days in advance, not real-time); risk is low (worst case = notification not received, which is the current baseline). This is the most automatable JtD in the engagement and the clearest entry point for initial deployment.
> **Governance rule impact:** None. This JtD is a process redesign (passive → active confirmation) as much as an automation — the value is in switching from no structured outbound to a confirmed, timestamped structured request.
> **Anti-pattern check:** This could be implemented as scheduled RPA (trigger on placement record created → send message). An agent is appropriate here for consistency with the broader confirmation monitoring workflow rather than a separate RPA process.

> **WS4-JtD-2 — Acknowledgement monitoring and pre-shift escalation**
> **Archetype:** Agent-led + Human Oversight
> **Rationale:** Input Structure H, Decision Determinism H (escalation trigger is rule-based: time-to-shift < threshold AND no acknowledgement), Context Complexity L, Exception Rate L produce a score of 4/7. Tool Coverage M (placement status field and confirmation timestamp must exist in ServiceNow — confirmed as structured but specific field availability is an assumption [A2A4]). Monitoring and escalation trigger are fully deterministic; the coordinator decides what to do when the escalation fires (attempt nurse contact, begin replacement fill, inform facility). Human oversight is at the escalation-response layer, not at the monitoring layer.
> **Governance rule impact:** None directly — this JtD creates the re-fill window that currently does not exist. It is the primary structural remedy for the notification-failure portion of the 12% no-show rate.
> **Anti-pattern check:** Monitoring could be a scheduled job (check placement status every N hours, compare to shift time). An agent is warranted for event-driven response and integration with the replacement fill workflow when escalation fires.

> **WS4-JtD-3 — Nurse withdrawal / renegotiation resolution**
> **Archetype:** Human Only
> **Rationale:** Score 0/7 — all dimensions point to human ownership. Input Structure L (inbound phone call), Decision Determinism L (accommodate vs. negotiate vs. replace = relationship judgment), Tool Coverage L (nurse relationship history and facility urgency tier not in any structured system [A2A6]), Context Complexity H, Risk/Compliance M (wrong accommodation decision = preventable no-show or relationship loss). The coordinator owns the call; the agent provides support (surface replacement candidates from the database in parallel) but does not own or influence the conversation.
> **Governance rule impact:** None — this is a relationship management decision, not a compliance event.
> **Anti-pattern check:** Not solvable by script or RPA. Human Only is correct; agent support is the appropriate upgrade (agent queries replacement pool during call, displays alternatives to coordinator in real time).

> **WS4-JtD-4 — No-show detection and response**
> **Archetype:** Human-led + Agent Support
> **Rationale:** Score 0/7 — Input Structure L (hospital call, unstructured), Decision Determinism L (facility communication tone and replacement decision = judgment), Context Complexity H (crisis management: apologise, assess replacement options, manage open queue simultaneously). Score of 0/7 would suggest Human Only; however, the agent provides immediate and distinct value here that changes the coordinator's capability: the agent simultaneously initiates a compressed WS2 replacement query while the coordinator is on the call with the facility, surfacing replacement options before the coordinator finishes the apology. This is agent-as-parallel-processor, not agent-as-decision-maker. Archetype is Human-led + Agent Support rather than Human Only.
> **Governance rule impact:** Replacement fill must still clear the full credential gate (WS2-JtD-2, WS3-JtD-1) under compressed conditions. The agent must not short-circuit credential checks in "fill fast" mode — HR-1 applies regardless of time pressure.
> **Anti-pattern check:** Not solvable by script or RPA. Human-led with agent support is the correct assignment; agent cannot own this JtD.

---

## 4. Delegation Architecture Summary

The MedFlex delegation architecture is a **two-layer pipeline** with a clear autonomous backbone and a set of human-anchored judgment gates that cannot be bypassed without facility profile data that does not yet exist.

**The autonomous backbone** runs from intake to submission. WS4-JtD-1 (confirmation dispatch, 7/7) and WS2-JtD-2 (candidate pool identification, 5/7) are the cleanest fully agentic targets — the first because the task is entirely mechanical, the second because the rules are deterministic and the data is structured. These two JtDs, combined with WS3-JtD-1 (credential status check, 5/7), WS1-JtD-4 (urgency classification), and the monitoring and withdrawal orchestration in WS4-JtD-2 and WS2-JtD-5/6, define the agent's unassisted operating zone. In this zone the agent works at machine speed, applies hard rules consistently, and hands off structured outputs to coordinators — compressing the pipeline from request receipt to qualified shortlist from 4.2 hours to minutes.

**The human-anchored gates** are not a weakness of the architecture — they are its safety design. WS1-JtD-3 (credential ambiguity resolution), WS2-JtD-3 (optimal candidate selection), and WS2-JtD-4 (exception path) are Human Only because no structured facility preference data exists to support agent judgment [D0C: U-3]. A coordinator who reviews a shortlist produced by WS2-JtD-2 and selects a final candidate using WS2-JtD-3 is exercising exactly the tacit knowledge the recommendation engine failure showed cannot be bypassed. These gates are not temporary scaffolding — they are permanent until facility profiles are structured, validated, and confirmed as reliable input to agent decision-making.

**JtDs not worth automating independently** are WS1-JtD-3, WS2-JtD-3, and WS2-JtD-4: all three require judgment with no structured tooling available. Additionally, WS3-JtD-1 is so simple (a binary database read + rule check) that it is not a separate agent — it is a tool call within the matching agent. Treating it as a standalone automation project would add overhead without proportional value.

**The primary hard constraint (HR-1)** is enforced at three distinct points in the architecture: at WS2-JtD-2 (agent queries confirmed credential status and filters the shortlist), at WS3-JtD-1 (agent re-checks credential status immediately before submission fires), and at WS2-JtD-4 (human owns all exception-path decisions involving below-threshold candidates). No agent action results in a submission without credential status being confirmed valid by a database read. The compliance team's data freshness SLA is therefore a critical operational dependency for the entire autonomous backbone — a stale credential record that permits an uncredentialed submission is a data quality failure, not an agent design failure.

The architecture enables the throughput arithmetic in D1: by handling ~85% of fills autonomously (clean fills: standard credentials, no profile notes, available nurse, clear intake), the 8 coordinators are freed to focus on the 15% requiring judgment — which at 14× revenue volume is still substantial work, but work that requires the judgment they are uniquely positioned to apply.

---

## 5. Delegation Boundary Defence

> **Contested assignment:** WS2-JtD-2 (Candidate pool identification) — assigned **Fully Agentic**
> **The counter-argument:** Risk/Compliance is H (credential non-compliance is a patient safety and regulatory event). A reasonable reviewer might argue that any JtD with patient safety consequences should require human sign-off before the shortlist is generated — assigning Human-led + Agent Support instead.
> **Why the assigned archetype is correct for this scenario:** The credential gate is a binary rule applied against a pre-verified database. The compliance team owns and maintains the credential records [DS-confirmed]; the agent reads a field and applies a filter. Adding human review at this step would not improve compliance outcomes — it would introduce human inconsistency into what is currently a deterministic check. The seven coordinators applying this check manually today produce a 7% mismatch rate; the agent applying it consistently produces no mismatch on the credential dimension. The safety risk is in data quality (stale records), not in the agent's rule application. Human review belongs at WS2-JtD-3 (final candidate selection), not at the query-and-filter step.
> **What would change the assignment:** Evidence that the compliance team's database update cadence produces systematic staleness above a threshold (say, >5% of credentials stale at any time) — at that point, a "credential status uncertain" routing path should be added to the agent design, and the archetype would become Agent-led + Human Oversight for the uncertain subset.

> **Contested assignment:** WS1-JtD-4 (Urgency classification and queue assignment) — assigned **Agent-led + Human Oversight**
> **The counter-argument:** With a score of 4/7, explicit urgency classification is nearly fully deterministic; a reasonable reviewer might argue this should be Fully Agentic since the "implicit urgency" edge case (inferring urgency from datetime proximity) is technically within agent scope and the risk of misclassification is low (wrong priority = delay, not a compliance event).
> **Why the assigned archetype is correct for this scenario:** The 14× revenue growth target [DS-confirmed] means same-day fill windows are the highest competitive priority in the portfolio. A misclassified same-day shift — queued as planned because the implicit urgency signal was not recognised — means MedFlex misses the fill window and loses the placement to a competitor. At volume, implicit urgency errors compound. Human Oversight ensures that when the agent's datetime inference is uncertain, a coordinator confirms before the queue pre-emption fires. The cost of the oversight (a coordinator confirmation click) is low; the cost of a missed same-day urgency classification at competitive fill rates is high.
> **What would change the assignment:** If analysis of shift request data shows that implicit urgency cases (no explicit urgency label, urgency inferred from datetime) represent less than 3% of all requests and the agent's datetime inference accuracy is validated above 98%, this JtD upgrades to Fully Agentic.

---

## 6. Assumption Log

> **Assumption [A-D2B-1]:** The Fully Agentic archetype for WS2-JtD-2 (candidate pool identification) holds only while the compliance team's nurse database update cadence is sufficiently current that credential status reads are reliable. If credential data is systematically stale (>5% of active credentials outdated at any time), the archetype must be downgraded to Agent-led + Human Oversight with a "credential status uncertain" routing path.
> **Why it matters:** The autonomous backbone depends on WS2-JtD-2 producing a correctly filtered shortlist. If the underlying data is unreliable, fully agentic execution produces high-speed false positives on the credential gate.
> **If wrong:** If compliance team update cadence is poor, an additional "credential age check" gate must be designed into the agent — adding a HITL escalation for credentials updated more than X days ago.
> **Confidence:** Medium — compliance team is confirmed as a separate function [DS-confirmed]; update cadence SLA is unknown [D0C: U-1].

> **Assumption [A-D2B-2]:** The Human Only archetype for WS2-JtD-3 (optimal candidate selection) is a phase 1 assignment, not a permanent designation. Once structured facility preference profiles are built and validated, this JtD upgrades to Human-led + Agent Support — the agent proposes a ranked selection with facility preference context; the coordinator confirms or overrides.
> **Why it matters:** WS2-JtD-3 is the single JtD that caps the agent's autonomous fill rate. If it remains Human Only indefinitely, the agent handles only the database query (WS2-JtD-2) and the coordinator still makes every selection decision — the throughput gain is real but partial. The facility profile enrichment project is therefore a prerequisite for the full throughput target, not a nice-to-have.
> **If wrong:** If facility preference data turns out to be encodable faster than expected (e.g., coordinators can annotate facility profiles in ServiceNow during a structured interview session), phase 2 upgrade to Human-led + Agent Support can begin within weeks rather than months.
> **Confidence:** High — facility preferences are confirmed as unstructured/tacit [DS-confirmed]; enrichment is a known prerequisite for full delegation.

> **Assumption [A-D2B-3]:** WS4-JtD-4 (no-show response) is assigned Human-led + Agent Support on the basis that the agent provides parallel replacement candidate surfacing while the coordinator manages the facility call. This assumes the agent can initiate a compressed WS2 cycle (credential check, availability filter, shortlist generation) in under 2 minutes — quickly enough to be useful during an active phone call.
> **Why it matters:** If the agent's compressed WS2 cycle takes longer than the coordinator's call, the parallel processing benefit disappears and the JtD reverts to Human Only.
> **If wrong:** If the WS2 query takes 5+ minutes (due to database latency or API rate limits), the agent cannot provide useful replacement options during the call and the archetype reverts to Human Only for this JtD.
> **Confidence:** Medium — database query speed is confirmed as fast for the structured case [DS-confirmed: nurse matching data is structured]; API rate limits and integration latency are assumptions [D0C: U-6].

> **Assumption [A-D2B-4]:** The 85% autonomous fill rate derived in D1 (AR-1) requires clean-fill percentage above 70% of total shift volume. This assumption is carried from D0C [AD2] where clean fills are estimated at 50–70%. If the actual clean-fill percentage is below 50%, the autonomous backbone as designed handles less than 85% of fills, and the throughput target in D1 [AR-1] must be revised.
> **Why it matters:** The delegation architecture is calibrated on the assumption that the majority of fills are clean. If exceptions dominate, WS2-JtD-3 and WS2-JtD-4 (both Human Only) handle the majority of volume and the throughput gain is smaller.
> **If wrong:** If clean fills are only 40%, the architecture still delivers value (faster clean fills, better no-show detection) but the coordinator leverage target (7× per D1 AR-7) requires reassessment.
> **Confidence:** Low — not stated in scenario; must be validated by coordinator sampling [D0C: U-2].
