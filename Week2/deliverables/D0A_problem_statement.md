# D0A — Problem Statement and Success Metrics
**Scenario:** Helix Workforce Software — Vendor Contract Clause Review

---

## 1. Problem Statement — Legal Team's Perspective

Tom (the paralegal) and the three commercial lawyers begin every vendor contract review by manually opening a 15–40 page Word document from Outlook or Ironclad, then cross-referencing each of the 7 clause types against a SharePoint playbook page that has not been updated in 9 months. First-pass classification alone takes ~25 minutes per contract — a task that is largely pattern-matching against known policy positions, but requires enough legal literacy that it cannot be delegated outside the team. Tom regularly hits decision uncertainty at the boundary between "negotiable deviation" and "escalation required": the DPDI Act updates that landed in Q1 are not in the playbook, so DPA clauses that might trigger new requirements go to Amelia informally rather than through a defined triage path. Recurring logistics failures add friction with no legal value — at least 3 vendors this quarter cannot accept SharePoint links, forcing Tom to re-attach redlined Word documents via Outlook as a manual workaround. At 300 contracts per quarter, first-pass classification alone consumes approximately 125 hours of legal time per quarter — time that leaves commercial lawyers with less capacity for the judgment-intensive escalated review and counteroffer work they were hired to do. The 4–6 business day turnaround is not a failure of effort; it is the arithmetic consequence of a 5-person team doing manually what a structured agent could handle faster and more consistently.

---

## 2. Problem Statement — Business Perspective

Helix Workforce Software is growing at 25% YoY with an enterprise sales motion that depends on processing ~300 vendor contracts per quarter. Each contract sits in legal's queue for 4–6 business days before procurement receives a response — a timeline the CRO considers incompatible with enterprise sales cycles where stalled procurement signals a troubled deal. Across the four work streams, the 5-person legal team spends approximately 260 hours per quarter on contract review: ~125 hrs on first-pass classification, ~45 hrs on paralegal redlining, ~45 hrs on escalated clause review, and ~45 hrs on counteroffer drafting and sign-off. At 25% YoY growth, Helix should expect ~375 contracts per quarter next year with no corresponding headcount increase planned — meaning turnaround degrades further unless throughput per person improves. The cost is not only operational: enterprise procurement teams interpret a 4–6 day legal response as a signal of process immaturity, and recurring manual workarounds (email-attachment redlines, informal playbook consultations) confirm that impression. The CRO's pressure to halve turnaround without adding headcount can only be met by reducing time-per-case on the high-volume, lower-judgment work streams — which the existing team cannot do alone.

---

## 3. Why an AI Agent — Not Traditional Software, Not RPA, Not a Process Change

**Traditional rules-based software** cannot solve this problem because clause classification requires semantic interpretation, not string matching. A liability cap clause stating "the lesser of (a) fees paid in the six months preceding the event or (b) £50,000" must be compared against the playbook's enterprise threshold of 12 months / £250,000 by understanding what the clause means in context — not by detecting a specific phrase. Traditional software can detect exact or near-exact matches but cannot handle the range of vendor-specific drafting styles across 300 different procurement teams. It also cannot reason about policy gaps, such as whether a DPA clause fails to address the DPDI Act's new legitimate interests test when the playbook itself does not yet reflect that requirement.

**RPA (Robotic Process Automation)** fails for structurally the same reason: RPA automates deterministic UI interactions on structured data. Each inbound contract is an unstructured 15–40 page Word document with different section numbering, layout, and terminology. RPA cannot read an unstructured document, identify which section contains the indemnity clause versus the SLA commitment, extract the relevant language, and assess whether it constitutes a minor or major deviation from policy. It also cannot flag novel regulatory exposure that the existing playbook does not cover.

**A process change alone** — redistribution of tasks, tighter SOPs, or lateral hires — cannot close the gap. Helix's 25% YoY growth means the problem compounds: a process optimised for 300 contracts per quarter will fail at 375. The GC's hard rule further constrains redistribution, since no counteroffer can leave the queue without named-lawyer sign-off on specific clauses — which means the judgment-intensive steps cannot be simplified away. The only structurally sound path is an AI agent that performs semantic clause extraction and playbook comparison at machine speed on the high-volume, lower-judgment work stream (first-pass classification), with human oversight reserved for the decision points the scenario already designates: negotiable deviations, escalation calls, and sign-off before any counteroffer leaves the queue.

---

## 4. Success Metrics

| Metric | Baseline (from scenario) | Target | How measured | Timeframe |
|--------|--------------------------|--------|--------------|-----------|
| Contract turnaround time (business days from receipt to counteroffer/approval sent) | 4–6 business days | ≤3 business days | Ironclad: contract-received timestamp → outbound response timestamp, per case | After 2 quarters in production |
| First-pass classification time per contract (min/case) | ~25 min/case | ≤6 min/case | Ironclad case time-log: triage-open → classification-saved timestamp | After 1 quarter in production |
| Clause classification accuracy (% of agent classifications confirmed without lawyer override) | Not stated in scenario — see **[A1]** | ≥95% of clause classifications accepted without human override | Ironclad: lawyer override events per 100 clauses reviewed, measured over rolling 4-week window | After 1 quarter in production |
| Contracts processed per quarter without headcount increase | 300/quarter with 5-person team | ≥400/quarter with same team | Ironclad volume report vs. legal team headcount at quarter close | After 2 quarters in production |
| Time from contract receipt to first outbound response to vendor | Not stated in scenario — see **[A2]** | ≤1 business day | Ironclad/Outlook: contract received → first outbound email to vendor procurement contact | After 1 quarter in production |
| Legal team hours consumed by first-pass classification per quarter | ~125 hrs/quarter (300 cases × 25 min) | ≤40 hrs/quarter | Ironclad time-log aggregated by work stream per quarter | After 2 quarters in production |

---

## 5. Assumption Log

> **Assumption [A1]:** Current clause classification accuracy (lawyer agreement rate with Tom's first-pass assessments) is approximately 85%.
> **Why it matters:** Sets the baseline for the accuracy KPI. If baseline accuracy is already 95%+, the agent needs to match a higher bar and the accuracy improvement case weakens. If it's below 85%, there is a stronger argument that the agent replaces a currently unreliable step.
> **If wrong:** The accuracy target (≥95%) may be set relative to the wrong baseline — either too easy or too demanding.
> **Confidence:** low — no accuracy data appears in the scenario; this figure is inferred from the fact that escalation-worthy contracts are manually identified and occasionally misclassified (Tom's DPDI uncertainty in Artefact 2.1).

> **Assumption [A2]:** Time from contract receipt to first vendor response is currently 2–3 business days within the 4–6 day total turnaround cycle (i.e., the first half of the cycle covers internal review and routing; the second half covers drafting and sign-off).
> **Why it matters:** Drives the procurement-facing turnaround metric. If the bottleneck is earlier in the cycle (e.g., contracts sit unlogged for 2 days before first-pass begins), the agent intervention point and the target both shift.
> **If wrong:** The ≤1 business day first-response target may be unachievable even with an agent if upstream intake delay is the dominant constraint.
> **Confidence:** medium — the scenario gives total turnaround (4–6 days) and Artefact 2.2 shows same-day forwarding by Tom, suggesting intake is fast and the delay is in review.

> **Assumption [A3]:** Helix's instance of Ironclad (the CLM) supports time-logging and case-lifecycle timestamping at sufficient granularity to measure the "How measured" column targets above.
> **Why it matters:** If Ironclad does not log per-case open/close timestamps for each work stream, the measurement mechanism for 4 of the 6 metrics breaks and a separate instrumentation layer would need to be built.
> **If wrong:** Measurement plan requires rework; targets may be unverifiable without additional tooling investment.
> **Confidence:** medium — Ironclad is a modern SaaS CLM with REST APIs (stated in scenario); time-tracking granularity at work-stream level is a common feature but not confirmed.

> **Assumption [A4]:** Helix's vendor contract volume will continue to grow proportionally with the company's 25% YoY growth rate, reaching ~375 contracts/quarter in the next year.
> **Why it matters:** Drives the capacity headroom case for the agent. The "≥400 contracts/quarter without headcount increase" target is only meaningful if the volume growth assumption holds.
> **If wrong:** If contract volume is decoupled from ARR growth (e.g., because enterprise deals are larger and fewer), the capacity urgency case is weaker, and the primary business justification shifts to turnaround time rather than throughput.
> **Confidence:** medium — the assumption is directionally reasonable given the business model and growth rate, but contract volume is not explicitly projected in the scenario.

---

## Self-check against acceptance criteria

- [x] Both perspectives (legal team AND business/procurement) present and distinct
- [x] Every metric has a numeric baseline sourced from scenario, or explicitly labelled as assumption [A1]/[A2]
- [x] Every target is a specific number (≤3 days, ≤6 min, ≥95%, ≥400, ≤1 day, ≤40 hrs)
- [x] "How measured" names a specific system and event (Ironclad timestamps, lawyer override events, Outlook timestamps)
- [x] Why-an-agent section names 3 alternatives and explains why each fails for clause review specifically
- [x] No directional language without a number attached
- [x] Assumption log has 4 entries in the required format
