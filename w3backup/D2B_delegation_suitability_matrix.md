# D2B — Delegation Suitability Matrix
## MedFlex: Clinical Workforce Staffing Coordination

---

## 0. Executive summary

- Across 15 JtDs spanning four work streams, the delegation architecture is split: 4 JtDs are fully agentic (mechanical execution of deterministic state transitions), 6 are agent-led with human oversight (agent executes, human reviews at boundaries), 4 are human-led with agent support (agent surfaces signal, human decides), and 1 is human only — governed principally by the degree of tacit knowledge dependency and compliance risk at each decision point.
- The most contested assignment is WS1-J2 (extract shift parameters from free text), which scores 0/7 on the suitability rubric yet is assigned Agent-led + Human Oversight because the rubric is calibrated for rule-based automation and undersells LLM-specific capability for unstructured text — the assignment is justified by the agent's core strength, not by the dimension scores alone.
- The scenario's primary governance constraint (HR-1/HR-2: credential verification as a hard prerequisite for placement) lands in WS2-J1 (hard filtering) and WS3-J1 (credential status gate), both assigned Agent-led + Human Oversight — meaning the agent enforces the credential gate consistently and faster than a coordinator under time pressure, but the human remains the final authority on borderline cases, which is non-negotiable given the 7% mismatch rate and the regulatory exposure a compliance bypass creates.

---

## 0b. Table of contents

- [0. Executive summary](#0-executive-summary)
- [0b. Table of contents](#0b-table-of-contents)
- [1. JtD inventory](#1-jtd-inventory)
- [2. Delegation Suitability Matrix](#2-delegation-suitability-matrix)
- [3. Delegation archetype assignment with rationale](#3-delegation-archetype-assignment-with-rationale)
- [4. Delegation architecture summary](#4-delegation-architecture-summary)
- [5. Delegation boundary defence](#5-delegation-boundary-defence)
- [6. Assumption log](#6-assumption-log)

---

## 1. JtD inventory

JtDs carried forward from D2A §2b, §3b, and §5.

| JtD ID | Work stream | Cognitive contract — one sentence |
|--------|-------------|-----------------------------------|
| WS1-J1 | WS1: Shift request intake | Determine whether a new ServiceNow case is an actionable shift request and classify it accordingly |
| WS1-J2 | WS1: Shift request intake | Extract all parameters needed to run a matching search from a free-text shift request |
| WS1-J3 | WS1: Shift request intake | Resolve ambiguities and fill gaps in the request that prevent it from proceeding to matching |
| WS1-J4 | WS1: Shift request intake | Validate extracted parameters against known facility data and confirm the request is serviceable |
| WS1-J5 | WS1: Shift request intake | Assign urgency and queue priority so the matching step is sequenced correctly relative to other open requests |
| WS2-J1 | WS2: Nurse-to-shift matching | Determine the set of nurses who clear all hard gates (credentials, availability, DNR, rest periods) |
| WS2-J2 | WS2: Nurse-to-shift matching | Rank the eligible candidate set by likelihood of successful placement using soft preference knowledge |
| WS2-J3 | WS2: Nurse-to-shift matching | Determine the optimal multi-submission strategy given competitive pressure, candidate availability, and race-condition risk |
| WS2-J4 | WS2: Nurse-to-shift matching | Handle exceptions that prevent standard matching from completing (partial credentials, zero candidates, DNR conflicts) |
| WS2-J5 | WS2: Nurse-to-shift matching | Execute submissions and manage the withdrawal lifecycle to prevent double-booking |
| WS3-J1 | WS3: Compliance / credential verification (coordinator scope) | Determine whether the credential status shown in ServiceNow for a given nurse is current and sufficient for the required shift |
| WS3-J2 | WS3: Compliance / credential verification (coordinator scope) | Flag and escalate cases where credential latency may be blocking a serviceable placement |
| WS4-J1 | WS4: Placement confirmation and coordination | Ensure every submitted nurse has received and acknowledged placement notification within the confirmation window, and trigger re-fill if not |
| WS4-J2 | WS4: Placement confirmation and coordination | Manage the withdrawal lifecycle for multi-submitted nurses — confirm at one facility, withdraw from all others |
| WS4-J3 | WS4: Placement confirmation and coordination | Detect and respond to no-show risk signals before shift start, and trigger replacement workflow when needed |

---

## 2. Delegation Suitability Matrix

**Scoring convention:** Suitability score counts how many of the 7 dimensions favour delegation. For Input Structure, Decision Determinism, Tool Coverage: H = favourable (score 1). For Context Complexity, Exception Rate, Latency Constraint, Risk/Compliance: L = favourable (score 1). M and H scores on the second group, and M and L scores on the first group, score 0.

| JtD | Work Stream | Input Structure | Decision Determinism | Tool Coverage | Context Complexity | Exception Rate | Latency Constraint | Risk/Compliance | Suitability Score | Delegation Archetype |
|-----|-------------|-----------------|---------------------|---------------|-------------------|----------------|-------------------|----------------|-------------------|----------------------|
| WS1-J1 | WS1 | M | H | H | L | L | M | L | 5/7 | Fully Agentic |
| WS1-J2 | WS1 | L | L | L | H | H | M | M | 0/7 | Agent-led + Human Oversight† |
| WS1-J3 | WS1 | L | L | M | H | H | H | M | 0/7 | Human-led + Agent Support |
| WS1-J4 | WS1 | H | H | M | L | M | M | M | 3/7 | Agent-led + Human Oversight |
| WS1-J5 | WS1 | M | M | H | L | M | M | L | 3/7 | Agent-led + Human Oversight |
| WS2-J1 | WS2 | H | H | H | L | M | H | H | 4/7 | Agent-led + Human Oversight |
| WS2-J2 | WS2 | L | L | L | H | H | H | M | 0/7 | Human-led + Agent Support |
| WS2-J3 | WS2 | M | L | M | H | H | H | M | 0/7 | Human-led + Agent Support |
| WS2-J4 | WS2 | L | L | L | H | H | H | H | 0/7 | Human Only |
| WS2-J5 | WS2 | H | H | H | L | M | H | M | 4/7 | Fully Agentic |
| WS3-J1 | WS3 | H | H | H | L | M | M | H | 4/7 | Agent-led + Human Oversight |
| WS3-J2 | WS3 | H | M | H | L | M | M | H | 3/7 | Agent-led + Human Oversight |
| WS4-J1 | WS4 | H | H | H | L | M | M | M | 4/7 | Fully Agentic |
| WS4-J2 | WS4 | H | H | H | L | H | H | M | 4/7 | Agent-led + Human Oversight |
| WS4-J3 | WS4 | M | L | M | H | H | H | M | 0/7 | Human-led + Agent Support |

*† WS1-J2 scores 0/7 but is assigned Agent-led + Human Oversight — see §3 rationale and §5 defence.*

**Scoring notes by JtD:**

**WS1-J1:** High suitability on 5 of 7 dimensions. Classification is binary, tool coverage is high, risk is low, exceptions are rare. Standard path is fully automatable; misclassified edge cases are correctable before downstream harm.

**WS1-J2:** The rubric penalises unstructured inputs and low decision determinism, producing a 0/7 score. This score is accurate for rule-based automation (RPA, scripts) but not for LLMs, which are specifically designed for unstructured text interpretation. The archetype exception is justified by agent capability, not by dimension scores. Low-confidence extractions must be flagged for human review — this is the oversight mechanism.

**WS1-J3:** Clarification outreach requires human judgment about ambiguity threshold, relationship management with the hospital, and interpretation of partial responses. The agent can draft outreach messages and track response state, but cannot decide autonomously what constitutes "sufficient" clarification.

**WS1-J4:** Mostly deterministic lookups (facility record exists or not; credential requirement known or not). Tool coverage scores M because the facility-unit-credential mapping is partially tacit — once encoded in a knowledge base, this upgrades to Fully Agentic.

**WS1-J5:** Urgency assignment could be made rule-based (shifts within 48 hours = high; 48–96 = medium; >96 = normal). Until those rules are formally defined, coordinator judgment remains necessary — hence Agent-led + Human Oversight rather than Fully Agentic.

**WS2-J1:** High suitability on structure and determinism dimensions; penalised by RC=H (compliance sensitivity). The agent executing hard gates consistently is better than a human who may skip them under time pressure — the RC=H score is a reason for the agent to do this more reliably, not a reason to leave it human. Human oversight applies at the margin (borderline credential freshness, borderline rest period calculations).

**WS2-J2:** The lowest suitability JtD in the workflow — tacit knowledge dominates, no system holds the required data. The prior recommendation engine failure makes a fully agentic assignment untenable at launch. Agent provides scored candidates with explanations; coordinator makes the final call. Upgradeable as outcome data accumulates.

**WS2-J3:** Multi-submission strategy cannot be agent-led without a defined policy. No policy currently exists. Agent can execute the decided strategy and flag race-condition risk, but cannot decide how many nurses to submit without a rule to apply.

**WS2-J4:** All seven dimensions point against automation. Exception handling is where compliance risk is highest, where tacit knowledge is most concentrated, and where the diversity of exception types makes a deterministic resolution path impossible. Human Only is the correct assignment — but the agent should detect and route exceptions with a structured summary to reduce coordinator context-switching time.

**WS2-J5:** Submission execution is mechanical once the matching decision is made. The agent can execute submissions, monitor confirmation events, and trigger withdrawals atomically. The high latency constraint (must be fast) is the reason for automation, not a reason against it — though the rubric scores it as unfavourable.

**WS3-J1:** Deterministic credential gate — the most directly compliance-critical JtD in the coordinator-scope work. Agent reads verified status and applies as a hard stop; human reviews cases where the status timestamp raises freshness concerns.

**WS3-J2:** Latency detection (how old is this credential update?) is algorithmic. The escalation priority judgment (worth holding the placement?) warrants human involvement — hence Agent-led + Human Oversight rather than Fully Agentic.

**WS4-J1:** Confirmation tracking is a pure state machine — notify, await, confirm or timeout, trigger re-fill. Fully automatable. The re-fill trigger connects directly to the matching agent (WS2), making this a closed-loop capability.

**WS4-J2:** The withdrawal trigger is deterministic, but simultaneous confirmations (race condition) require a human to decide which placement to honour. Agent handles the standard case autonomously; human handles the race-condition exception.

**WS4-J3:** No-show signal detection is partially automatable (monitoring pre-shift confirmation state), but the interpretation of non-response is genuinely ambiguous — a nurse who hasn't confirmed may be a wage-competition no-show or may simply not have seen the message yet. Human judgment required to decide when to escalate vs. wait.

---

## 3. Delegation archetype assignment with rationale

> **WS1-J1 — Classify incoming case as shift request**
> **Archetype:** Fully Agentic
> **Rationale:** Decision Determinism is H (binary classification), Tool Coverage is H (ServiceNow accessible), Context Complexity is L, Exception Rate is L, Risk/Compliance is L. Five of seven dimensions favour automation with no governance constraint applying.
> **Governance rule impact:** None — classification precedes any compliance-gated decision.
> **Anti-pattern check:** A keyword filter (RPA/script) could handle obvious cases but would fail on ambiguous cases (e.g., a hospital emailing about an amendment to an existing placement, not a new request). LLM-based classification handles the long tail without a rule for every variant.

> **WS1-J2 — Extract shift parameters from free text**
> **Archetype:** Agent-led + Human Oversight
> **Rationale:** Input Structure is L (free text, no schema) and Decision Determinism is L (multiple valid interpretations possible) — these scores would suggest Human Only if the rubric applied to rule-based automation. The exception is that LLMs are specifically designed for this task. The oversight mechanism is explicit: the agent flags low-confidence extractions (ambiguous facility name, inferred credential shorthand, relative date references) for coordinator review before the case proceeds to matching. The agent handles the majority; the coordinator handles the flagged minority.
> **Governance rule impact:** Extraction errors at this stage propagate to the 7% mismatch rate. The oversight requirement is therefore materially important, not cosmetic.
> **Anti-pattern check:** Cannot be solved by a script — free text with no schema requires language understanding, not pattern matching.

> **WS1-J3 — Resolve ambiguities and initiate clarification outreach**
> **Archetype:** Human-led + Agent Support
> **Rationale:** Decision Determinism is L (no rule governs when ambiguity requires outreach vs. inference) and Context Complexity is H (each ambiguity is different and requires contextual judgment). The agent's role is to detect the ambiguity, draft the clarification message, and track response state — but the coordinator decides whether to send and reviews the response. Automating the decision to initiate outreach risks either over-contacting hospitals (damaging the relationship) or under-contacting (proceeding with a wrong interpretation).
> **Governance rule impact:** None directly, but errors in this JtD propagate to credential mismatches downstream.
> **Anti-pattern check:** Cannot be solved by a script — ambiguity detection requires language understanding; relationship management requires human judgment.

> **WS1-J4 — Validate extracted parameters against known facility data**
> **Archetype:** Agent-led + Human Oversight
> **Rationale:** Input Structure is H (facility records are structured in ServiceNow) and Decision Determinism is H (facility exists or not; credential requirements mapped or not). Tool Coverage scores M because the facility-unit-credential mapping is partially tacit and not yet fully encoded in ServiceNow. Human oversight applies specifically to cases where the credential requirement mapping is absent from the system — the agent flags these for coordinator resolution.
> **Governance rule impact:** Directly supports HR-2 (credential-to-facility-type matching). Accurate parameter validation is a pre-condition for the credential gate in WS2-J1.
> **Anti-pattern check:** Mostly solvable by a lookup script once the facility-unit-credential mapping is encoded. The agent adds value in handling partial matches and fuzzy facility name resolution.

> **WS1-J5 — Assign urgency and queue priority**
> **Archetype:** Agent-led + Human Oversight (upgradeable to Fully Agentic once urgency rules are defined)
> **Rationale:** Tool Coverage is H (ServiceNow queue management accessible) and Risk/Compliance is L. Decision Determinism scores M because no formal urgency policy currently exists — coordinators apply personal judgment. Once a policy is defined (e.g., shifts within 48 hours = high priority), the decision becomes fully deterministic and this JtD upgrades to Fully Agentic.
> **Governance rule impact:** None directly.
> **Anti-pattern check:** Fully solvable by a script once the urgency rules are defined — the agent adds no intelligence here, only consistency.

> **WS2-J1 — Hard filtering (credentials, availability, DNR, rest periods)**
> **Archetype:** Agent-led + Human Oversight
> **Rationale:** Input Structure is H (structured nurse profiles), Decision Determinism is H (binary gates), and Tool Coverage is H (ServiceNow accessible). The suitability score of 4/7 is penalised by Risk/Compliance=H and Latency Constraint=H — but both of these are arguments for agent automation, not against it. Consistent credential gate enforcement by an agent is safer than a coordinator who may skip the check under time pressure. Human oversight applies at the margin: credential records with stale timestamps or borderline rest-period calculations are surfaced for coordinator review rather than auto-passed or auto-blocked.
> **Governance rule impact:** This JtD is the primary enforcement point for HR-1 (credential verification as a hard prerequisite) and HR-2 (credential-to-facility-type match). The agent must not pass a nurse who fails either gate without explicit human override.
> **Anti-pattern check:** For individual gate checks in isolation, a script suffices. The agent adds value by applying all gates together, handling borderline cases, and surfacing data-quality issues (stale credential timestamps, missing DNR records).

> **WS2-J2 — Soft ranking using tacit preference/fit knowledge**
> **Archetype:** Human-led + Agent Support
> **Rationale:** All three pro-automation dimensions score against this JtD: Input Structure is L (tacit knowledge, not in any system), Decision Determinism is L (two coordinators would rank differently), and Tool Coverage is L (no queryable preference data). Context Complexity is H (multi-dimensional assessment). This is the JtD most directly responsible for the prior recommendation engine failure — coordinators could not trust rankings they could not verify, and perceived the tool as a job threat. The agent's role at launch is to surface quantifiable signals (historical fill rate with this facility, nurse response rate, last confirmed placement at this unit) with explicit attribution — not to rank autonomously. The coordinator retains final authority.
> **Governance rule impact:** Indirectly supports HR-2 by helping coordinators select appropriately credentialed nurses, but soft ranking itself is not a compliance gate.
> **Anti-pattern check:** Cannot be solved by a script — the required data is currently tacit; the ranking itself involves probabilistic inference, not rule application.

> **WS2-J3 — Multi-submission strategy**
> **Archetype:** Human-led + Agent Support
> **Rationale:** Decision Determinism is L (no policy exists; coordinator decides case-by-case) and Context Complexity is H (juggling multiple nurses across multiple facilities with race-condition risk). The agent can execute the strategy once decided and can flag when a nurse is already submitted elsewhere — but the strategic decision (how many, in what order) requires a policy that does not currently exist. If Marcus defines a policy, this JtD upgrades to Agent-led + Human Oversight.
> **Governance rule impact:** Multi-submission decisions drive the race conditions that create double-booking incidents. Defining a policy here is a prerequisite for agent autonomy.
> **Anti-pattern check:** Cannot be solved by a script — the optimal strategy depends on contextual factors (competitive window, nurse quality, facility strictness) that vary per case.

> **WS2-J4 — Exception handling (partial credentials, zero candidates, DNR conflicts)**
> **Archetype:** Human Only
> **Rationale:** All seven dimensions score against automation: Input Structure=L, Decision Determinism=L, Tool Coverage=L, Context Complexity=H, Exception Rate=H, Latency Constraint=H, Risk/Compliance=H. This is the highest compliance-risk JtD in the entire workflow — it is where partial credential placements are weighed, where zero-candidate scenarios require escalation or boundary-pushing decisions, and where DNR conflicts must be resolved without a clear rule. The diversity of exception types (no two are the same) makes a deterministic resolution path impossible.
> **Governance rule impact:** Directly relevant to HR-1 and HR-2 — the most common exceptions involve credential questions. A Human Only assignment here is the compliance constraint made explicit in the architecture.
> **Anti-pattern check:** Not applicable — this JtD cannot be solved by any automated system at this stage. The agent's contribution is exception detection and structured routing to the coordinator, not resolution.

> **WS2-J5 — Execute submissions and manage withdrawal lifecycle**
> **Archetype:** Fully Agentic
> **Rationale:** Input Structure is H (structured ServiceNow operations), Decision Determinism is H (once the matching decision is made: submit these nurses, withdraw on confirmation), and Tool Coverage is H (ServiceNow accessible). Context Complexity is L — this is mechanical execution of a decided action, not a judgment task. The high Latency Constraint score (H) is the primary reason for full automation: withdrawal must be immediate when a confirmation arrives to prevent double-booking; human-in-the-loop withdrawal creates the race condition MedFlex currently experiences.
> **Governance rule impact:** None — this is execution, not decision-making. All compliance gates were enforced in WS2-J1.
> **Anti-pattern check:** The standard submission path is executable by a script with ServiceNow API access. The agent adds value in handling simultaneous confirmation events (race condition detection and routing) and in monitoring the full submission lifecycle across multiple concurrent cases.

> **WS3-J1 — Determine whether credential status is current and sufficient (coordinator scope)**
> **Archetype:** Agent-led + Human Oversight
> **Rationale:** Input Structure is H (structured nurse profiles), Decision Determinism is H (verified/not verified is binary), and Tool Coverage is H (ServiceNow accessible). Risk/Compliance is H — the agent must enforce the credential gate consistently, and any borderline case (e.g., a renewal that updated yesterday but the compliance team hasn't reviewed it yet) requires human review before the agent auto-passes a nurse.
> **Governance rule impact:** This JtD enforces HR-1 (credential verification prerequisite) at the coordinator-workflow level. The compliance team's data quality in ServiceNow is a critical dependency — if the data is stale, the agent's gate enforcement is only as good as the compliance team's update cadence.
> **Anti-pattern check:** Solvable by a script for standard cases. The agent adds value in detecting and surfacing staleness signals (e.g., flagging credentials with update timestamps older than a configurable threshold).

> **WS3-J2 — Flag and escalate credential latency cases**
> **Archetype:** Agent-led + Human Oversight
> **Rationale:** Input Structure is H (timestamp comparison is structured) and Tool Coverage is H. Decision Determinism scores M because the escalation priority question ("should I hold this placement pending the update?") depends on fill urgency and the compliance team's expected update timeline — not a fully deterministic calculation. Human oversight at the escalation decision is appropriate.
> **Governance rule impact:** Indirectly supports HR-1 — surfaces cases where the credential gate might be bypassed due to data latency.
> **Anti-pattern check:** Latency detection is scriptable (flag records older than N days). Escalation prioritisation requires agent judgment or human decision.

> **WS4-J1 — Ensure placement notification acknowledged; trigger re-fill if not**
> **Archetype:** Fully Agentic
> **Rationale:** Input Structure is H (confirmation state is binary), Decision Determinism is H (confirmed = proceed; timeout = trigger re-fill), and Tool Coverage is H. Context Complexity is L (state machine: notify → await → confirm/timeout). This is the core active confirmation loop that addresses B-3 (passive confirmation root cause from D1). The agent replaces the passive silence-as-acceptance model with an explicit acknowledgement requirement, monitors state, and triggers re-fill automatically when the window closes without response.
> **Governance rule impact:** None directly — but this JtD addresses the structural root cause of the 12% no-show rate.
> **Anti-pattern check:** Solvable by a script or workflow automation for the standard confirm/timeout path. The re-fill trigger connects to the matching agent (WS2), making the full loop an integrated agent capability rather than a standalone script.

> **WS4-J2 — Manage withdrawal lifecycle for multi-submitted nurses**
> **Archetype:** Agent-led + Human Oversight
> **Rationale:** Input Structure is H (confirmation events are structured), Decision Determinism is H (confirm at A → withdraw from all others), and Tool Coverage is H. Exception Rate is H — simultaneous confirmations occur regularly and require a human to decide which placement to honour. Standard withdrawals are Fully Agentic; race-condition conflicts route to a human with a structured summary of both confirmations.
> **Governance rule impact:** None directly — but resolving the multi-submission race condition (B-4 from D1) is a facility relationship and coordinator-workload issue.
> **Anti-pattern check:** Standard withdrawal is scriptable. Race-condition conflict resolution requires human judgment about which facility relationship to prioritise — not scriptable.

> **WS4-J3 — Detect and respond to no-show risk signals**
> **Archetype:** Human-led + Agent Support
> **Rationale:** Decision Determinism is L (non-response is ambiguous — could be a technical miss or a wage-competition departure) and Context Complexity is H (distinguishing notification failure from deliberate no-show requires context the agent may not have). The agent's role is to surface the risk signal (nurse has not confirmed with X hours to shift start) and present replacement options; the coordinator decides whether to escalate or wait. This JtD addresses the wage-competition component of the no-show problem — where the agent cannot prevent the behaviour but can reduce the detection-to-response lag.
> **Governance rule impact:** None directly. But WS4-J3 is the last opportunity to prevent a no-show from becoming a shift-start surprise for the hospital.
> **Anti-pattern check:** Detection (monitoring pre-shift confirmation state) is scriptable. The response decision (escalate now vs. wait) requires human judgment about the specific nurse and shift context.

---

## 4. Delegation architecture summary

The delegation architecture for MedFlex's coordinator workflow has three layers, and the layer boundaries are determined by two orthogonal forces: data structure (can the agent access what it needs?) and judgment type (is the decision rule-based or experience-dependent?).

The **autonomous backbone** consists of four JtDs that the agent executes without coordinator action: case classification (WS1-J1), submission execution and withdrawal management (WS2-J5), placement notification and re-fill triggering (WS4-J1), and — for the standard withdrawal path — multi-submission lifecycle management (WS4-J2). These four JtDs share a common profile: structured inputs, deterministic decision logic, and mechanical execution where speed matters more than judgment. Together they form the latency-sensitive spine of the process — the parts that currently lose MedFlex competitive placements because humans cannot execute fast enough. An agent running these four JtDs autonomously directly addresses B-1 (intake bottleneck), B-4 (multi-submission race condition), and the mechanical component of B-3 (passive confirmation → no proactive re-fill).

The **agent-led with oversight** layer — six JtDs — covers work that is mostly deterministic but requires a human backstop at the margin. Hard filtering (WS2-J1) is the most compliance-critical entry in this layer: the agent enforces the credential gate consistently and surfaces borderline cases (stale credential timestamps, edge-case rest-period calculations) for coordinator review. Credential status validation (WS3-J1) operates identically. Parameter validation (WS1-J4), urgency assignment (WS1-J5), credential latency flagging (WS3-J2), and the withdrawal race-condition path within WS4-J2 all fit the same pattern: the agent handles the standard path; the human handles the exception. This layer is where the primary hard constraint (HR-1, HR-2) is operationally enforced — the agent runs the gate, the human owns the decision when the gate produces an uncertain result.

The **human-led with agent support** layer covers four JtDs where the agent provides decision support but the human retains authority: free-text parameter extraction (WS1-J2), clarification outreach (WS1-J3), soft ranking (WS2-J2), multi-submission strategy (WS2-J3), and no-show risk response (WS4-J3). These JtDs share the property that either the required data is tacit (soft ranking), the decision threshold is unresolved (multi-submission policy, clarification threshold), or the input is genuinely ambiguous (no-show signal interpretation). WS1-J2 is the notable outlier in this layer — its suitability score is 0/7 but it is not Human-led; the LLM's unstructured-text capability makes it Agent-led + Human Oversight for the majority of cases, with Human-led reserved for the ambiguous minority. This layer is where the prior recommendation engine failure is directly addressed: every JtD in this layer produces an explainable agent output (extracted parameters with confidence scores, candidate scores with attributions, risk flags with evidence) that the coordinator can verify and override without having to trust a black box.

**WS2-J4 (exception handling) is the single Human Only JtD** — and this is non-negotiable. It is the only JtD where all seven dimensions score against automation, where compliance risk is highest, and where the diversity of exception types (partial credentials, zero candidates, DNR conflicts) makes a deterministic resolution path impossible. The agent's contribution here is limited to detection and structured routing: it identifies that an exception has occurred, classifies the exception type, and presents the coordinator with a structured summary of the situation and available options. The coordinator resolves it. This boundary is where the hard constraint (HR-1, HR-2) is most visibly defended — exceptions in matching are precisely the cases where credential compliance is most likely to be compromised under time pressure, and human oversight is the compliance architecture's last line of defence.

---

## 5. Delegation boundary defence

> **Contested assignment: WS1-J2 — Extract shift parameters from free text — assigned Agent-led + Human Oversight**
> **The counter-argument:** The suitability score is 0/7. Input Structure is L, Decision Determinism is L, Tool Coverage is L — every pro-automation dimension scores unfavourably. A strict reading of the matrix says Human Only.
> **Why the assigned archetype is correct for this scenario:** The scoring rubric was calibrated for rule-based automation where low input structure genuinely means unsolvable-by-machine. For an LLM, unstructured text is the primary use case — extracting structured parameters from natural language hospital requests is exactly what these models do reliably at scale. The rubric understates LLM capability for this specific task. The oversight mechanism is precise: the agent flags low-confidence extractions (ambiguous facility names, inferred credential shorthand, relative date references) for coordinator review. This is not a cosmetic HITL layer — it is targeted oversight at the specific failure mode (extraction ambiguity) while the majority of standard requests are processed autonomously.
> **What would change the assignment:** If a significant proportion of hospital requests are so idiosyncratic or ambiguous that the agent's low-confidence flag rate is >50%, the effective labour savings are marginal and the archetype should be reconsidered. The assignment stands if the agent handles ≥70% of requests without triggering the oversight flag.

> **Contested assignment: WS2-J4 — Exception handling (partial credentials, zero candidates) — assigned Human Only**
> **The counter-argument:** Exceptions are frequent (Exception Rate=H) and time-sensitive (Latency Constraint=H) — both argue for automation to reduce coordinator burden. A more aggressive architecture might assign Agent-led + Human Oversight, reasoning that the agent can diagnose the exception type and propose resolution options, reducing the cognitive work even if the final decision remains human.
> **Why the assigned archetype is correct for this scenario:** The compliance risk at this JtD is too high for the agent to have even a decision-proposal role at launch. Partial credential placements and zero-candidate escalations are where the 7% mismatch rate and regulatory exposure are most concentrated. The prior recommendation engine failed in part because coordinators could not audit the agent's reasoning — if the agent proposes a resolution to a partial-credential exception and the coordinator accepts without fully understanding the rationale, MedFlex has an autonomous compliance decision dressed up as human oversight. The Human Only assignment forces the coordinator to reason through the exception from first principles. The agent's contribution (exception detection + structured routing) is already specified and is meaningful without extending into decision support.
> **What would change the assignment:** Two conditions would justify upgrading to Human-led + Agent Support: (1) a formal partial-credential policy that converts partial-credential decisions into rule-based judgments, and (2) at least 6 months of exception logs showing consistent resolution patterns that the agent can learn from. Neither exists at launch.

---

## 6. Assumption log

> **Assumption [A-D2B-1]:** The facility-unit-credential mapping can be encoded as a queryable knowledge base within the engagement timeline, making WS1-J4 and the credential-matching components of WS2-J1 upgradeable from Agent-led + Human Oversight to a more autonomous state. If this encoding is not completed before the agent is deployed, both JtDs will depend on coordinator tacit knowledge for a larger share of cases than projected.
> **Why it matters:** The facility-unit-credential mapping is the shared data dependency identified as the highest-leverage encoding target in D2A. If it remains tacit, the intake agent's extraction confidence is lower and the matching agent's hard-filter gate is incomplete.
> **If wrong:** If the mapping cannot be encoded systematically (e.g., too many facility-specific exceptions with no consistent logic), both WS1-J4 and the credential component of WS2-J1 remain more dependent on human oversight than the archetype assignments suggest.
> **Confidence:** Medium — Marcus confirmed the tacit knowledge problem; encoding feasibility is not confirmed.

> **Assumption [A-D2B-2]:** A multi-submission policy will be defined before WS2-J3 is deployed. The current Human-led + Agent Support assignment for WS2-J3 is contingent on the policy being absent; once a policy exists, the archetype upgrades to Agent-led + Human Oversight.
> **Why it matters:** Multi-submission strategy directly governs the race-condition frequency (B-4 root cause from D1). Without a policy, the agent cannot act autonomously and the race condition persists under agent-assisted operations as it does today.
> **If wrong:** If Marcus declines to define a multi-submission policy (prefers to leave it to coordinator judgment indefinitely), WS2-J3 remains Human-led + Agent Support and the race condition is only partially mitigated.
> **Confidence:** Medium — Marcus has not been asked directly about a multi-submission policy. This is an open design question that should be raised in the next stakeholder touchpoint.

> **Assumption [A-D2B-3]:** The agent's soft-ranking output in WS2-J2 is explainable — each candidate score includes attributed evidence (e.g., "fill rate at this facility: 94%, last shift: 3 weeks ago, response rate: 88%") visible to the coordinator before they accept the ranking. Without explainability, the Human-led + Agent Support archetype collapses to Human Only as coordinators disengage from agent output, replicating the prior recommendation engine failure.
> **Why it matters:** Explainability is the adoption prerequisite identified from the prior failure root cause. If the agent cannot surface its reasoning, coordinator adoption will fail regardless of the technical quality of the ranking.
> **If wrong:** If the agent's ranking signals are not attributable to queryable data (e.g., the ranking emerges from a black-box model), the archetype must be downgraded to Human Only until explainability is achieved.
> **Confidence:** High — explainability as a design requirement is confirmed by the prior failure analysis; implementing it is a spec constraint, not an assumption.

> **Assumption [A-D2B-4]:** The DNR list for each facility is accessible as a structured, queryable data source within ServiceNow or a system the agent can query at matching time. If it is maintained in unstructured documents or email threads, the DNR check component of WS2-J1 cannot be performed by the agent and must remain human-dependent.
> **Why it matters:** A DNR check that the agent cannot perform leaves a contract-violation risk (HR-4) unmitigated at the automated matching layer.
> **If wrong:** If DNR lists are not queryable, WS2-J1 degrades from Agent-led + Human Oversight to Human-led + Agent Support for the DNR component specifically, and a data migration is required before full autonomy is achievable.
> **Confidence:** Low — DNR list accessibility in ServiceNow is assumed but not confirmed in the scenario or discovery session.
