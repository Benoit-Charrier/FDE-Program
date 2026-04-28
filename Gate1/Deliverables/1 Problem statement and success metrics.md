# Problem Statement and Success Metrics
## FNOL Processing Agent — Insurance Claims Automation

---

## 1. Problem statement — claimant perspective

When a claimant submits a first notice of loss — after a car accident, a flood, a theft — they are in a moment of disruption and need prompt confirmation that their insurer has received and is acting on their report. The current process guarantees acknowledgement within 2 hours, but breaches that guarantee for 1 in 3 claimants (31% SLA breach rate). On a 300-claim day, 93 people wait longer than 2 hours with no word — some considerably longer, since the breach rate tells us nothing about how far over the 2-hour mark those claims fall. For claimants, this is not an administrative inconvenience: it is uncertainty about whether a major financial event is being handled. The 18% routing error compounds this — a claim routed to the wrong adjuster must be re-routed before meaningful progress begins, adding further unacknowledged delay to claimants who have already been waiting.

---

## 2. Problem statement — business perspective

The claims team runs a structural capacity deficit. Processing 300 claims per day at 22 minutes per claim requires 6,600 minutes (110 hours) of specialist time per day. Twelve specialists, assuming 8-hour days, provide 5,760 minutes (96 hours) of capacity — a shortfall of 840 minutes (14 hours) per day. [A3] This arithmetic directly explains the 31% SLA breach: the team cannot physically handle peak volume within the 2-hour window. Beyond capacity, the 18% routing error rate — 54 mis-routed claims per day — creates rework that consumes specialist time that is already scarce, and degrades adjuster productivity by sending them claims outside their specialty. The combined effect is an operation that is expensive (12 FTEs on manual triage), slow (22 min/claim average), inaccurate (18% error on a step that could be automated), and unreliable (31% SLA breach). Without an automated first-line capability, the only paths to SLA compliance are headcount growth or volume reduction — neither of which the client has indicated is available. The client's stated design constraint is that any solution must retain human oversight for high-value or ambiguous claims — full automation is not the goal, but neither is the status quo. The target state is an operation where routine claims are handled end-to-end by the agent and specialists are reserved for the cases that genuinely require their judgment.

---

## 3. Why an AI agent — not traditional software, not RPA, not a process change

**Traditional rule-based software** cannot address this problem because FNOL inputs arrive as unstructured text from three channels: email, phone transcripts, and web forms. Rule-based systems require structured, predictable inputs. They can handle a structured web form with fixed fields, but cannot parse "my car was hit from behind at the junction near the office" and derive claim severity, coverage type, and adjuster routing from that narrative. Traditional software would cover at most one input channel and would still require specialists to handle email and phone transcript inputs — leaving the majority of the capacity problem unsolved.

**RPA** automates interactions with existing UIs by scripting clicks and keystrokes. It requires predictable screen layouts and structured data. Phone transcripts and emails are free-form; RPA cannot interpret semantic content or extract structured claim attributes from them. Even for structured web form inputs, RPA cannot perform the policy coverage validation step, which requires reading the policy record and applying judgment about whether the claimed event falls within coverage terms. RPA addresses data entry, not reasoning.

**Human process change** — optimising the existing manual workflow — fails on the capacity arithmetic alone. Even if a redesigned process reduced handling time by 25% (from 22 min to 16.5 min per claim), the team would need 4,950 minutes per day against 5,760 available, which clears the deficit with no buffer for volume spikes or absences. [A3] More fundamentally, process change does not address the structural mismatch: the problem is not that specialists are working inefficiently; it is that unstructured inputs require human interpretation for every claim, whether that takes 15 minutes or 25. Only removing human interpretation from the routine cases breaks the scaling constraint.

**An AI agent is the right answer** because: (1) the inputs are unstructured and require natural language understanding to classify and extract claim attributes — a capability only AI provides at the required speed and scale; (2) the decisions span multiple systems (claim text, policy record, adjuster availability) and must be synthesised in a single workflow — an agent can orchestrate this where a human must context-switch manually; (3) the client's stated requirement — full automation where appropriate, human oversight for ambiguous or high-value claims — is precisely the agent-with-delegation pattern; and (4) the volume (300/day) is high enough that even partial automation of routine cases closes the capacity deficit without headcount growth.

---

## 4. Success metrics

| Metric | Baseline (from scenario) | Target | How measured | Timeframe |
|--------|--------------------------|--------|--------------|-----------|
| SLA compliance rate | 69% (31% breach) | 95% | % of claims with claimant acknowledgement logged within 120 minutes of receipt; measured daily from CRM timestamp data | 90 days post go-live |
| Routing accuracy | 82% (18% error) | 96% | % of agent-routed claims accepted by the receiving adjuster without re-routing; measured weekly from CRM reassignment logs | 90 days post go-live |
| Average handling time — agentic claims | 22 min (manual baseline) | < 3 min | Elapsed time from claim receipt to routing decision logged in CRM, for claims processed without human escalation; measured per claim, reported as p50 and p95 | 90 days post go-live |
| Daily claim throughput without headcount increase | 300 claims/day with 12 FTEs | 300 claims/day with ≤ 12 FTEs | Total claims processed per day from CRM; FTE count from HR records; measured monthly | 90 days post go-live |
| Time to claimant acknowledgement | Not directly stated; implied ≤ 120 min with 31% breach [A5] | < 30 min for 90% of agent-handled claims | Time from claim receipt timestamp to acknowledgement sent timestamp in CRM; measured per claim, reported as p90 | 90 days post go-live |
| Escalation rate (agent to human) | Not applicable today (all human) | 15%–35% [A6] | % of claims where agent triggers AGENT_REVIEW or HUMAN_ONLY tier; measured weekly; alert if outside 15%–35% band | 90 days post go-live |

**Note on targets:** All targets above are proposed based on the stated business goals and industry reference points. [A1] None have been confirmed by the client. They must be validated before the success metrics are treated as contractual commitments.

---

## 5. Assumption log

> **Assumption [A1]:** All success metric targets (95% SLA compliance, 96% routing accuracy, < 3 min handling time, < 30 min acknowledgement) are proposed by the delivery team, not stated by the client.
> **Why it matters:** These targets drive the acceptance criteria in the capability specification and the pass/fail thresholds in the validation design. If the client has different targets, the spec thresholds change.
> **If wrong:** The system is built to the wrong bar — it may be over-engineered (if targets are lower) or under-scoped (if targets are higher, e.g. 99% SLA compliance requires different escalation logic).
> **Confidence:** Low — no client target confirmation in scenario.

> **Assumption [A2]:** The 18% routing error is caused primarily by misclassification of claim type or adjuster specialty, not by downstream constraints such as adjuster availability, geography, or workload balancing.
> **Why it matters:** If errors are classification-driven, an AI agent that correctly classifies claims will reduce them. If errors are capacity-driven (routed correctly but to an overloaded adjuster who passes it on), AI classification does not fix the problem — capacity management does.
> **If wrong:** The routing accuracy target is not achievable through classification improvement alone; the spec must include adjuster workload balancing logic, which is a significantly larger integration requirement.
> **Confidence:** Medium — misclassification is the most common driver of routing error in FNOL contexts, but this is not confirmed in the scenario.

> **Assumption [A3]:** Specialists work 8-hour days with no dedicated non-claim time (no meetings, training, or admin time factored in). The capacity calculation (12 × 8 × 60 = 5,760 min/day) assumes 100% productive utilisation.
> **Why it matters:** The capacity deficit (6,600 min needed vs 5,760 available) is the primary justification for why process change alone cannot close the SLA breach. If actual productive time per specialist is less than 8 hours, the deficit is larger, strengthening the case. If specialists have surge capacity or flexible hours, the deficit may be partially offset.
> **If wrong (productive time < 8h):** The capacity deficit is larger than calculated; the business case for automation is stronger.
> **If wrong (flexible capacity available):** The breach rate may be partially explainable by staffing patterns, not just volume — the agent may only need to cover peak periods, which changes the build scope.
> **Confidence:** Medium — 8-hour day is a standard assumption; actual productive utilisation is typically lower.

> **Assumption [A4]:** The 2-hour SLA clock starts at claim receipt (when the email, transcript, or web form arrives in the system) and covers the full cycle: triage, coverage validation, routing, and claimant acknowledgement.
> **Why it matters:** If the SLA clock starts later (e.g., when a specialist picks up the claim), the gap between receipt and pick-up is not measured, and the breach rate understates the true claimant wait time. This affects how we instrument the SLA metric and where the agent must insert itself in the workflow.
> **If wrong:** The measurement baseline is incorrect, and the 69% SLA compliance figure is not comparable to what the agent will produce under a different clock definition.
> **Confidence:** Medium — the scenario states the 2-hour requirement alongside the four steps, implying end-to-end coverage, but this is not explicit.

> **Assumption [A5]:** The current acknowledgement to the claimant is a manual step performed by a specialist, and it happens at or near the end of the 22-minute handling cycle — not as an automated first-contact response on receipt.
> **Why it matters:** If acknowledgement is already automated on receipt (e.g., an auto-reply email), the claimant-facing SLA is partially met regardless of the agent, and the 31% breach applies to something downstream (e.g., adjuster assignment confirmation). This changes which part of the process the agent must own to move the SLA metric.
> **If wrong:** The acknowledgement metric target (< 30 min for 90% of claims) is already being met today for the first-contact step, and the meaningful claimant metric is time to adjuster assignment — which requires a different measurement approach.
> **Confidence:** Low — the scenario does not state whether an automated acknowledgement exists.

> **Assumption [A6]:** Between 15% and 35% of claims will require human review or decision (AGENT_REVIEW or HUMAN_ONLY delegation tier). This band reflects the client's stated intent to automate "most" claims while retaining oversight for high-value or ambiguous cases.
> **Why it matters:** The escalation rate is a two-sided control: too low means the agent is under-escalating (potential quality risk); too high means the automation ROI is insufficient and FTE time is not freed as projected.
> **If wrong (escalation rate < 15%):** The agent may be under-escalating ambiguous claims, accepting low-confidence decisions that should go to a human. Silent quality risk.
> **If wrong (escalation rate > 35%):** The automation does not free enough specialist capacity to close the structural deficit; the business case weakens or additional automation scope is required.
> **Confidence:** Low — "most" is not quantified in the scenario; the 15%–35% band is a working hypothesis to be validated with the client.
