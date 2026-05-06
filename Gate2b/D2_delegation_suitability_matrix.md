# D2 — Delegation Suitability Matrix: Apex Distribution Ltd — Customer Operations

**Produced:** 2026-05-06
**Status:** Draft — awaiting FDE review

---

## 0. Executive summary

- Across eight scored task clusters, two are Fully Agentic (ETA standard lookup and compliant credit execution), three are Human-led + Agent Support (ETA edge-case, exception classification, dispute intake), one is Human-led + Automation Support (dispatch adjustment, system-constrained), and two are Human Only — the split is governed not by task volume but by the presence or absence of a codified decision rule and the availability of a write-capable system integration.
- The most contested assignment is exception intake and classification (C-3), which scores 0/7 on the suitability matrix due to unstructured inputs and hard real-time latency, yet warrants Human-led + Agent Support rather than Human Only because the agent's speed advantage in structured extraction and its mechanical enforcement of the £500 escalation threshold are exactly what this work stream needs — the score reflects a difficult environment, not a useless intervention.
- The scenario's primary governance constraints — Aurum's batch-only architecture with no real-time write API, the mandatory APPROVER_ID and AUDIT_REF requirement for credit records, and the £500 Duty Manager escalation rule — land in three distinct clusters: they lock credit determination (C-7) to Human Only until a write pathway is established, enforce the audit-compliant credit execution cluster (C-8) as a non-negotiable compliance gate before any credit record is written, and require the exception classification cluster (C-3) to route all >£500 cases to a human duty manager before disposition is attempted.

---

## 0b. Table of contents

- [0. Executive summary](#0-executive-summary)
- [0b. Table of contents](#0b-table-of-contents)
- [1. Task cluster definition](#1-task-cluster-definition)
- [2. Delegation Suitability Matrix](#2-delegation-suitability-matrix)
- [3. Delegation archetype assignment with rationale](#3-delegation-archetype-assignment-with-rationale)
- [4. Delegation architecture summary](#4-delegation-architecture-summary)
- [5. Delegation boundary defence](#5-delegation-boundary-defence)
- [6. Assumption log](#6-assumption-log)

---

## 1. Task cluster definition

| Cluster | Work Stream | Description |
|---------|-------------|-------------|
| C-1: ETA Standard Inquiry Resolution | WS2 — ETA Inquiries | Customer requests delivery status; agent retrieves route window from CRM and Driver App and responds; no dispatch consultation required |
| C-2: ETA Edge-Case Estimate | WS2 — ETA Inquiries | Customer pushes for a tighter estimate than the standard window; GPS data is stale; dispatch consultation is required to produce a useful answer |
| C-3: Exception Intake, Classification, and Escalation Routing | WS1 — Delivery Exceptions | Agent receives unstructured driver message, extracts key facts, classifies exception type, checks consignment value against the £500 escalation threshold, and routes to Duty Manager or dispatcher |
| C-4: Exception Disposition Decision | WS1 — Delivery Exceptions | Dispatcher determines the correct instruction for the driver (return-to-depot, hold, reattempt, conditional accept) for damage and refusal exceptions where no documented procedure exists |
| C-5: Dispatch Adjustment Assessment and Execution | WS3 — Dispatch Adjustments | Dispatcher receives a mid-route change request, assembles route state from dispatch console and Driver App, makes the adjustment decision, and communicates it to the driver |
| C-6: Billing Dispute Intake and Charge Validity Assessment | WS4 — Billing Disputes | Agent receives customer dispute, retrieves invoice and surcharge data from Aurum batch exports, classifies dispute type, and assesses whether the disputed charge is valid |
| C-7: Credit Amount Determination | WS4 — Billing Disputes | Agent determines the appropriate goodwill credit amount to apply given that invoice line-item correction is not possible in real time; no credit policy currently exists |
| C-8: Audit-Compliant Credit Record Execution | WS4 — Billing Disputes | Agent writes the credit record with APPROVER_ID, AUDIT_REF, CREDIT_AMT, and REASON_CODE populated; ensures the audit trail is complete before the credit is issued to the customer |

---

## 2. Delegation Suitability Matrix

| Task Cluster | Work Stream | Input Structure | Decision Determinism | Tool Coverage | Context Complexity | Exception Rate | Latency Constraint | Risk/Compliance | Suitability Score | Delegation Archetype |
|---|---|---|---|---|---|---|---|---|---|---|
| C-1: ETA Standard Resolution | WS2 | H | H | H | L | L | M | L | 6/7 | Fully Agentic |
| C-2: ETA Edge-Case Estimate | WS2 | M | M | M | M | M | M | L | 1/7 | Human-led + Agent Support |
| C-3: Exception Intake, Classification, Escalation | WS1 | L | M | M | M | M | H | M | 0/7 | Human-led + Agent Support |
| C-4: Exception Disposition Decision | WS1 | L | L | L | H | H | H | H | 0/7 | Human Only |
| C-5: Dispatch Adjustment | WS3 | M | L | L | H | M | H | M | 0/7 | Human-led + Automation Support |
| C-6: Dispute Intake and Validity Assessment | WS4 | M | M | M | M | M | L | M | 1/7 | Human-led + Agent Support |
| C-7: Credit Amount Determination | WS4 | L | L | L | H | H | L | H | 1/7 | Human Only |
| C-8: Audit-Compliant Credit Execution | WS4 | H | H | M | L | L | L | H | 5/7 | Fully Agentic (below threshold) / Agent-led + Human Oversight (above threshold) |

**Scoring note — dimension values represent delegation suitability signals:**
H = High; M = Medium; L = Low. Suitability score counts: Input Structure (H=1), Decision Determinism (H=1), Tool Coverage (H=1), Context Complexity (L=1), Exception Rate (L=1), Latency Constraint (L=1), Risk/Compliance (L=1). Maximum score: 7.

**Dimension justification notes:**

*C-1:* Input structure H — customer requests are structured (order ID or name provided); Decision Determinism H — route window lookup is deterministic given order record; Tool Coverage H — CRM REST API and Driver App both confirmed available; Context Complexity L — single order, no multi-system synthesis; Exception Rate L — standard inquiries require no judgment [A-1]; Latency M — customer expects response within minutes but not driver-urgent; Risk L — an incorrect ETA estimate is a service issue, not a compliance event.

*C-2:* All middle-ground. Input structure M — customer request clear but GPS data state uncertain (26-min lag observed in Artefact 3); Decision Determinism M — estimate requires judgment about GPS data quality; Tool Coverage M — tools available but GPS freshness limits decision quality; Context Complexity M — requires route + movement rate reasoning; Exception Rate M — this is the exception path; Latency M; Risk L — poor estimate is a service issue.

*C-3:* Input Structure L — driver messages are unstructured voice/free text (Artefact 1); Decision Determinism M — classification taxonomy is mostly deterministic but ambiguous inputs occur (combined damage + refusal); Tool Coverage M — CRM available, NLP capability needed but not in place, escalation routing via dispatch console has limited API; Context Complexity M — customer history + consignment value synthesis; Exception Rate M — combined exception types occur; Latency H — driver parked, real-time required (Artefact 1); Risk M — misclassification causes rework; escalation miss is a compliance concern.

*C-4:* All adverse. Input Structure L — inputs are the dispatcher's assembled judgment, no structured form; Decision Determinism L — SOP Section 4.3 is blank, pure tacit knowledge (Artefact 4); Tool Coverage L — no system supports this decision; Context Complexity H — driver report + customer history + consignment value + route impact + customer relationship all relevant; Exception Rate H — every damaged consignment presents unique context; Latency H — driver parked; Risk H — wrong disposition = financial exposure + route disruption + reputational risk with key accounts.

*C-5:* Input Structure M — some structure (Driver App message or CRM request) but route state is fragmented across systems; Decision Determinism L — requires judgment on route state, customer priority, driver capacity simultaneously; Tool Coverage L — dispatch console via Citrix has limited API surface, no confirmed write access (scenario); Context Complexity H — multi-system synthesis under time pressure; Exception Rate M — not all adjustments are equally complex; Latency H — time-critical; Risk M — wrong adjustment cascades to downstream drops; driver hours compliance risk.

*C-6:* Input Structure M — customer email semi-structured, invoice/dispute data structured (Aurum CSV schema confirmed); Decision Determinism M — surcharge validity is rule-based for clear-cut cases; damage-linked disputes require judgment; Tool Coverage M — CRM available, Aurum batch accessible, no real-time billing query; Context Complexity M — invoice + delivery outcome + account history required; Exception Rate M — damage-linked disputes are the majority of open disputes (APEX_DISPUTES_OPEN); Latency L — same-day response expected, not minute-by-minute; Risk M — validity assessment drives credit decision; error has financial consequence.

*C-7:* Input Structure L — no credit policy document exists; decision rests on informal norms (Artefact 2: 50% applied without rationale); Decision Determinism L — different agents produce different amounts for identical disputes; Tool Coverage L — no system or policy supports this decision; Context Complexity H — customer history, dispute history, account value, precedent all relevant; Exception Rate H — every dispute requiring a goodwill credit reaches this step with no rule to apply; Latency L — not time-critical; Risk H — under-credit drives churn, over-credit is a financial loss, non-compliant application is an audit exposure.

*C-8:* Input Structure H — APEX_CREDITS schema is fully defined (CREDIT_ID, INVOICE_NO, CUSTOMER_ID, CREDIT_AMT, REASON_CODE, APPROVER_ID, AUDIT_REF, APPLIED_DT); Decision Determinism H — given credit amount, record creation is deterministic; Tool Coverage M — CRM write confirmed, Aurum write access uncertain [A-2]; Context Complexity L — all required fields are known before execution; Exception Rate L — execution errors are rare; Latency L — not time-critical; Risk H — APPROVER_ID and AUDIT_REF are mandatory compliance fields; non-compliant application is the active gap identified in Artefact 2.

---

## 3. Delegation archetype assignment with rationale

> **Cluster C-1 — ETA Standard Inquiry Resolution**
> **Archetype:** Fully Agentic
> **Rationale:** Input Structure (H) and Decision Determinism (H) converge on a lookup-and-respond pattern with no judgment required for standard cases. Tool Coverage (H) is confirmed via CRM REST API and Driver App. Risk (L) means an incorrect response is a service issue, not a compliance event, making this safe for full delegation. Suitability score 6/7.
> **Governance rule impact:** None — this cluster has no financial, regulatory, or escalation trigger.
> **Anti-pattern check:** The standard ETA lookup is close to solvable by a simple API integration (CRM order query → Driver App route check → templated response). An AI agent is justified over a script because: (1) customer messages arrive in natural language requiring parsing; (2) the edge case path (C-2) requires contextual judgment that a script cannot handle; (3) a unified agent handles both C-1 and C-2 more efficiently than a script plus a separate human triage layer.

> **Cluster C-2 — ETA Edge-Case Estimate**
> **Archetype:** Human-led + Agent Support
> **Rationale:** Decision Determinism (M) — the GPS data has observable latency (~26 min in Artefact 3); producing a useful estimate requires inference about movement rate, not just data lookup. Tool Coverage (M) — the necessary data exists but its freshness is uncertain. The agent adds value by: retrieving and presenting the last GPS ping with its timestamp, calculating the implied travel time since the ping, and flagging whether the data is fresh enough to give a reliable estimate. The human (dispatcher) then decides whether to call the route driver or respond with a caveat. Suitability score 1/7.
> **Governance rule impact:** None — providing an estimate carries no compliance trigger.
> **Anti-pattern check:** A script could retrieve the last GPS ping, but it could not assess whether the data is stale enough to require a dispatch call, nor compose a contextually appropriate customer response for the edge case. An agent is warranted here; a script would either always call dispatch (wasteful) or never call dispatch (poor customer experience).

> **Cluster C-3 — Exception Intake, Classification, and Escalation Routing**
> **Archetype:** Human-led + Agent Support
> **Rationale:** Input Structure (L) — driver messages are unstructured voice/free text (Artefact 1) — is the primary limiting dimension, combined with Latency Constraint (H) — driver parked, real-time response required. These two dimensions make fully autonomous handling non-viable. However, the agent adds irreplaceable value at two specific points: (1) structured extraction from unstructured input at speed the human cannot match under multi-tasking conditions; (2) mechanical enforcement of the £500 Duty Manager escalation threshold, which D0D flagged as inconsistently applied. The human validates the extracted classification before any disposition is attempted. Suitability score 0/7 reflects a difficult environment, not a zero-value intervention.
> **Governance rule impact:** The £500 escalation rule (SOP Section 4.2) is embedded here as a non-negotiable compliance gate. The agent must enforce this threshold mechanically — regardless of whether the dispatcher would have applied it — before any disposition path is opened.
> **Anti-pattern check:** A script with keyword matching could attempt classification, but would fail on ambiguous inputs (Artefact 1: damage + refusal combined in a single voicemail) and would have no awareness of context (customer tier, prior case history). An agent with NLP capability is warranted; keyword matching is not sufficient.

> **Cluster C-4 — Exception Disposition Decision**
> **Archetype:** Human Only
> **Rationale:** Decision Determinism (L) — SOP Section 4.3 is explicitly incomplete; no documented procedure exists for damaged consignments — is the determining dimension. Tool Coverage (L) — no system provides decision support for this judgment — confirms there is nothing for an agent to execute against. Risk (H) — wrong disposition for a high-value consignment creates financial exposure and route disruption — makes this a hard stop for autonomous delegation. Unlike C-3 where the agent adds value in preparation, here the core cognitive act (what do I do with this consignment?) cannot be supported by an agent without a decision matrix that does not yet exist. Suitability score 0/7.
> **Governance rule impact:** The £500 escalation rule means that for the subset of cases that have already been routed to the Duty Manager (via C-3), the disposition decision is not made by the regular dispatcher at all — it is a Duty Manager judgment. The agent's scope ends at routing; it has no role in the disposition decision itself.
> **Anti-pattern check:** N/A — Human Only archetypes do not require an anti-pattern check. The prerequisite for changing this archetype is a documented decision matrix for at least the top 3 exception types (damage, refusal, unattended address with high-value consignment). Once that exists, this cluster can be reclassified as Human-led + Agent Support.

> **Cluster C-5 — Dispatch Adjustment Assessment and Execution**
> **Archetype:** Human-led + Automation Support
> **Rationale:** Tool Coverage (L) — the dispatch console runs via Citrix with a stated limited API surface, and write access is unconfirmed — is the binding constraint. Even if the cognitive work were fully delegatable, the agent cannot act on the dispatch console without a confirmed programmatic interface. Decision Determinism (L) — multi-system context synthesis under time pressure — confirms the cognitive challenge. The appropriate archetype is Human-led + Automation Support rather than Human-led + Agent Support because the automation scope is narrowly limited to structured data retrieval (CRM case context, GPS from Driver App); the agent cannot extend into the dispatch console without integration work that is out of scope for an initial deployment. Suitability score 0/7.
> **Governance rule impact:** Driver hours compliance is a constraint: dispatch adjustments that affect driver hours must not be executed without a compliance check. Until the dispatch console API surface is confirmed, this constraint cannot be mechanically enforced — it remains a human responsibility.
> **Anti-pattern check:** A script that reads Driver App GPS and formats a current route state summary would cover a portion of the agent's value here. This cluster is the one in the portfolio where an agent is the least clearly warranted over simpler automation — structured data retrieval and formatting is closer to a static integration than an agentic capability. The agent is appropriate only if it is also handling intake classification across work streams (the shared NLP component from D1 Cross-Observation 4).

> **Cluster C-6 — Billing Dispute Intake and Charge Validity Assessment**
> **Archetype:** Human-led + Agent Support
> **Rationale:** Tool Coverage (M) — CRM REST API confirmed; Aurum batch export accessible; but no real-time billing query is possible — sets the upper bound on agent capability. Decision Determinism (M) — fuel surcharge validity for clear delivery cases is rule-based (agent can handle); damage-linked dispute validity requires judgment (human validates) — creates a natural human-agent split within the cluster. The agent handles: case creation, Aurum batch data retrieval, dispute type classification, and rule-based validity verdicts for clear-cut cases. The human handles: validity judgment for ambiguous damage-linked cases. Suitability score 1/7 reflects the mixed determinism and Aurum data latency constraint.
> **Governance rule impact:** Aurum batch-only (T-1 data, no real-time API) means the agent is always working from yesterday's data. This is a structural constraint, not a design choice — the agent must communicate data staleness to the human reviewer when presenting a validity assessment.
> **Anti-pattern check:** The structured retrieval and classification steps within this cluster are close to script-level automation (Aurum CSV read + CRM lookup + taxonomy mapping). An agent is warranted because: (1) dispute intake arrives in natural language; (2) the rule-based vs. judgment-required split within the cluster needs contextual awareness to navigate correctly.

> **Cluster C-7 — Credit Amount Determination**
> **Archetype:** Human Only
> **Rationale:** Decision Determinism (L) — no credit policy exists; Sandra applied 50% of the disputed amount in Artefact 2 without stated rationale; different agents produce different amounts for identical disputes — is the determining dimension. Tool Coverage (L) — no system or policy document provides a rule for the agent to apply — confirms there is nothing to delegate to. Risk (H) — under-credit drives customer churn; over-credit is a financial loss; non-compliant application is the active audit gap from Artefact 2 — makes this a hard stop. Suitability score 1/7 (the one point comes from Latency L — this decision is not time-critical).
> **Governance rule impact:** This is the cluster where the Aurum batch-only constraint and the absent credit policy converge. Even if a policy were defined, the agent cannot close a credit autonomously without confirmed write access to the APEX_CREDITS pathway. Until both prerequisites are met (credit policy defined; write pathway confirmed), this cluster must remain Human Only.
> **Anti-pattern check:** N/A — Human Only. The prerequisite for changing this archetype: (1) a documented credit policy with explicit thresholds and reason codes; (2) confirmed write pathway for APEX_CREDITS. Once both exist, this cluster can become Agent-led + Human Oversight above threshold.

> **Cluster C-8 — Audit-Compliant Credit Record Execution**
> **Archetype:** Fully Agentic (below threshold) / Agent-led + Human Oversight (above threshold)
> **Rationale:** Input Structure (H) — APEX_CREDITS schema is fully defined with all required fields; Decision Determinism (H) — given credit amount and reason code, record creation is deterministic — make execution the most delegatable cluster in the billing dispute path. Context Complexity (L) — all required fields are known before execution begins — means the agent is not synthesising anything new; it is writing a record. The split archetype reflects the governance constraint: for credits below the approval threshold, the agent writes the record and the case closes; for credits above the threshold, the agent prepares the record and routes for human sign-off before writing. Risk (H) — the compliance gap in Artefact 2 is the active problem this cluster is designed to fix — means the agent must be held to a higher standard than the current human practice, not a lower one. Suitability score 5/7.
> **Governance rule impact:** APPROVER_ID and AUDIT_REF are non-negotiable required fields. The agent must enforce these mechanically — it must not write a credit record with empty or system-placeholder values in these fields. Above-threshold credits require a named human approver ID, not a system ID.
> **Anti-pattern check:** Credit record creation with structured fields is close to a script-level automation. An agent is warranted here specifically because it must also: (1) receive the output from C-7 (human credit decision) and translate it into a compliant record; (2) route for approval when the amount exceeds the threshold; (3) manage the async wait for approval before writing; (4) notify the customer after the record is written. This multi-step flow with approval routing and async handling requires more than a script.

---

## 4. Delegation architecture summary

The delegation architecture for Apex Customer Operations organises into four layers: an autonomous backbone for high-volume structured work, an agent-supported zone for judgment-adjacent preparation, two human-only gates where policy gaps make autonomous delegation non-viable, and one system-constrained cluster that cannot be automated in its current technical state.

**The autonomous backbone** consists of C-1 (ETA standard inquiry resolution) and C-8 (audit-compliant credit execution below threshold). These two clusters are the clearest immediate automation targets. C-1 handles the highest-volume work stream (400 cases/day, 4 min/case) with fully structured inputs and confirmed tooling — the agent can handle end-to-end without human intervention for standard cases, freeing approximately 1,600 agent-minutes per day. C-8 closes the active compliance gap in billing: once the credit amount is determined by a human (C-7), the agent creates the formal record with all required audit fields populated — replacing the informal bypass that currently leaves credits without APPROVER_ID or AUDIT_REF entries in the APEX_CREDITS export.

**The agent-supported zone** consists of C-2 (ETA edge-case estimate), C-3 (exception intake/classification/routing), and C-6 (billing dispute intake/validity). In all three clusters, the agent handles structured retrieval, pattern recognition, and rule-based checks — reducing the time a human must spend assembling context before making a judgment. In C-3, the agent's mechanical enforcement of the £500 escalation threshold is arguably the highest-compliance-value contribution in the entire architecture: it converts an inconsistently applied SOP rule into a guaranteed gate. The human's role in these clusters is validation and judgment, not data assembly — changing the cognitive experience from "reconstruct from scratch" to "review a structured summary and decide."

**The two human-only gates** are C-4 (exception disposition decision) and C-7 (credit amount determination). These are not permanent Human Only designations — they are policy gaps masquerading as capability limits. C-4 requires a documented decision matrix for at least the top three exception types before an agent can support the disposition decision; C-7 requires a formal credit policy with explicit thresholds and reason codes. Neither of these is a long-horizon infrastructure project — both are policy design tasks that the FDE should flag as prerequisites for Phase 2 agent capability, not as future-state aspirations. Until these prerequisites are met, the agent scope boundary is drawn at C-3 (routing) and C-6 (intake/validity) respectively — the agent prepares, the human decides.

**The system-constrained cluster** is C-5 (dispatch adjustment). This is the one cluster in the portfolio where the binding constraint is not cognitive but technical: the dispatch console runs via Citrix with a limited API surface, and no confirmed programmatic write access exists. Even if the cognitive work were fully delegatable, the agent cannot act on the dispatch console without integration work that is out of scope for an initial deployment. The appropriate near-term design is lightweight automation support — a structured data-retrieval component that pre-populates the dispatcher's decision summary — rather than any form of agent-led execution. This cluster should be revisited after the dispatch console API surface is confirmed.

**Where the primary governance constraints are enforced in the architecture:** The Aurum batch-only constraint (no real-time write API) locks C-7 to Human Only and limits C-6 to agent-supported validity assessment. The mandatory APPROVER_ID/AUDIT_REF requirement is enforced in C-8 as a mechanical gate before any credit record is written. The £500 Duty Manager escalation rule is enforced in C-3 as the first decision point after classification — the agent routes to the Duty Manager before the dispatcher can attempt a disposition, not after. All three are non-negotiable: they cannot be relaxed by agent design choices or business-case pressure.

---

## 5. Delegation boundary defence

> **Contested assignment: C-3 — Exception Intake, Classification, and Escalation Routing — assigned Human-led + Agent Support**
> **The counter-argument:** The suitability score is 0/7 — the worst possible score. A reasonable reader might argue this should be Human Only: the inputs are unstructured, the latency is hard real-time, the risk of a misclassified exception routing to the wrong procedure is non-trivial, and the agent has no confirmed NLP tool available. Every dimension argues against delegation.
> **Why the assigned archetype is correct for this scenario:** The score reflects the difficulty of the task environment, not the value of the intervention. The agent's two contributions here — structured extraction from unstructured input at machine speed, and mechanical enforcement of the escalation threshold — are valuable precisely because the environment is difficult. A dispatcher under simultaneous call pressure currently has to: (1) listen to a voicemail, (2) extract facts, (3) open the CRM, (4) check the consignment value, (5) decide whether to escalate, all while other work is arriving. The agent does steps 1–5 in seconds and presents a structured summary. The human still validates the classification (the judgment step). This is not "the agent is replacing human judgment" — it is "the agent is removing the preparation burden so the human judgment step starts from a better position." Human Only would mean throwing away the preparation value; that is not justified by the score.
> **What would change the assignment:** If the Driver App does not permit the agent to receive and parse driver messages (i.e., there is no API or integration point that would allow the agent to access inbound driver communications), the agent has no input to work from and the cluster reverts to Human Only. Confirmation of Driver App integration capability is the critical discovery question for this cluster.

> **Contested assignment: C-8 — Audit-Compliant Credit Execution — assigned Fully Agentic (below threshold)**
> **The counter-argument:** Risk/Compliance is H — the APPROVER_ID and AUDIT_REF requirements are active compliance gaps, not theoretical concerns (Artefact 2 shows a credit applied with no audit log entry). A reasonable reader might argue this should be Agent-led + Human Oversight for all credits, not just above-threshold ones, given that the current process has already demonstrated non-compliance. Assigning Fully Agentic to a cluster with an active compliance gap looks like over-confidence.
> **Why the assigned archetype is correct for this scenario:** The compliance gap in Artefact 2 exists precisely because a human bypassed the formal process under pressure. The agent does not face the same pressure — it will not shortcut the APPROVER_ID and AUDIT_REF fields because they are mandatory fields in its execution logic, not optional steps that can be skipped when busy. The agent is more reliable at enforcing the formal path than the human currently is, which is why Fully Agentic for below-threshold credits is correct: the agent's mechanical compliance is the feature, not a risk. The risk of over-confidence would apply if the agent were likely to make novel errors that a human would catch — but credit record creation from structured inputs with defined fields is not that kind of task. The residual risk is in Aurum write access, which is why this has a governance rule impact note and why the assumption is flagged in the assumption log.
> **What would change the assignment:** If the confirmed Aurum write pathway requires a human to review before submission (i.e., if the Aurum ticket process is the only write path and every ticket requires human approval), then below-threshold credits also require human sign-off and the archetype becomes Agent-led + Human Oversight for all credits. The Fully Agentic assignment depends on confirming a programmatic write path that does not route through the manual Aurum ticket process.

---

## 6. Assumption log

> **Assumption A-1:** Approximately 70% of ETA inquiries (C-1) are standard lookups that resolve with no dispatch consultation — the remaining ~30% require the edge-case path (C-2).
> **Why it matters:** Drives the volume estimate for the C-1 autonomous backbone. If the edge-case proportion is higher, the Fully Agentic scope is smaller and more cases require human involvement.
> **If wrong:** If edge-case inquiries are >50% of volume, the ETA work stream as a whole scores closer to Human-led + Agent Support, and the autonomous ETA claim in the architecture summary needs to be moderated.
> **Confidence:** Low — the scenario provides no breakdown; Artefact 3 shows one edge-case inquiry but this is not representative of population. Validate by pulling CRM case data and classifying ETA cases by whether a dispatch consultation was made.

> **Assumption A-2:** The agent can write to the APEX_CREDITS export pathway programmatically — either directly via a confirmed write API or via a CRM-to-Aurum integration layer — without requiring a manual Aurum support ticket for every credit record.
> **Why it matters:** If this assumption is wrong, C-8 (Fully Agentic) cannot be delivered as designed. Every credit write would require the manual 48-hour Aurum ticket process, which defeats the purpose of automating credit execution.
> **If wrong:** C-8 reverts to Agent-led + Human Oversight at best: the agent prepares the credit record for human review, and the human submits the Aurum ticket. The compliance gap is partially closed (the agent enforces field completeness before the ticket is submitted) but the 48-hour turnaround remains.
> **Confidence:** Low — the scenario states "batch-file exports only" and "no real-time API"; it is unclear whether this applies equally to write operations. This is a critical technical discovery question.

> **Assumption A-3:** The Driver App exposes an integration point that allows the agent to receive inbound driver messages programmatically — not just read a log, but receive and parse messages in near-real-time.
> **Why it matters:** C-3's Human-led + Agent Support archetype depends on the agent having access to driver messages. If the Driver App does not expose a message API, the agent cannot perform the structured extraction step that makes the archetype viable.
> **If wrong:** C-3 reverts to Human Only: there is no agent input to work from, and the structured extraction value proposition disappears.
> **Confidence:** Medium — the Driver App is described as in-house iOS/Android with driver-to-dispatch messaging; in-house apps typically expose internal APIs. Confirming the API surface is a critical technical discovery question.

> **Assumption A-4:** A formal credit policy with explicit thresholds and reason codes can be produced by Apex (e.g., COO + finance sign-off) within the assessment or early build phase, making C-7's Human Only designation a temporary state rather than a permanent constraint.
> **Why it matters:** If Apex cannot or will not formalise a credit policy, C-7 remains Human Only indefinitely and the billing dispute agent is permanently limited to intake + validity assessment — it can never close a case autonomously.
> **If wrong:** If the COO or finance team refuses to define a credit policy (e.g., for liability reasons), the agent design for WS4 must explicitly scope out autonomous credit decisions and frame this as a human-assisted triage tool only.
> **Confidence:** Medium — formalising a credit policy is standard practice for a business of this size and is not a technically complex task; the scenario provides no reason to believe it cannot be done. Validate by confirming with the COO in the stakeholder session.
