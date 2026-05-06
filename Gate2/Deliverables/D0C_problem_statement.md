# D0C — Problem Statement and Success Metrics: Apex Distribution Ltd

**Produced:** 2026-05-06
**Status:** Draft — awaiting FDE review

---

## 0. Executive summary

- A 35-person Customer Operations team is absorbing approximately 730 cases per day — spanning delivery exceptions, ETA inquiries, dispatch adjustments, and billing disputes — without formal SLAs, with a stale SOP that references a retired system, and with a billing constraint that prevents invoice corrections in under 48 hours; the result is visible in the scenario: a repeat customer in a 9-day dispute thread, a 22-minute hold incident, and a credit applied with no audit trail entry.
- The existing approach cannot scale because the binding constraint is not headcount but system architecture: Aurum Billing offers no real-time API and requires a manual 48-hour ticket for every invoice modification, meaning that regardless of how many agents work the queue, billing dispute resolution speed is structurally capped — and every prior automation attempt that touched billing broke when Aurum's schema changed quarterly.
- An AI agent that handles ETA inquiries autonomously and provides structured triage and HITL co-pilot support for exceptions and billing disputes must achieve a measurable reduction in agent handle time of at least 50% on ETA inquiries and reduce billing dispute first-response time from the observed 9-day baseline to same business day — without requiring real-time Aurum API access and without replicating the informal credit-bypass that currently produces audit trail gaps.

---

## 1. Table of contents

- [0. Executive summary](#0-executive-summary)
- [1. Table of contents](#1-table-of-contents)
- [2a. Problem statement — team's perspective](#2a-problem-statement--teams-perspective)
- [2b. Problem statement — business perspective](#2b-problem-statement--business-perspective)
- [3. Why an AI agent — not traditional software, not RPA, not a process change](#3-why-an-ai-agent--not-traditional-software-not-rpa-not-a-process-change)
- [4. Success metrics](#4-success-metrics)
- [5. Assumption log](#5-assumption-log)

---

## 2a. Problem statement — team's perspective

The Customer Operations team handles four interlocking work streams that arrive in an uncoordinated mix throughout the working day. Agents receive unstructured inputs — driver voicemails, customer email threads, inbound calls — and must retrieve context from multiple systems (CRM, Driver App, dispatch console, and Aurum Billing) that do not share data in real time before they can make any decision. For the highest-volume work stream, ETA inquiries (~400/day at 4 min/case), the information exists but requires a manual lookup across systems; for every non-routine ETA, a separate call to dispatch adds further latency. For delivery exceptions (~180/day at 12 min/case), there is no codified decision procedure for damaged consignments — Section 4.3 of the SOP is explicitly marked incomplete — so each agent makes a discretionary call. For billing disputes (~60/day at 28 min/case), agents cannot correct the underlying invoice; the only tool available is a goodwill credit, and the informal mechanism for applying it bypasses the audit trail that the billing system formally requires. The team operates with a SOP that references a system retired eighteen months ago, with no updated documentation, and with no formal performance targets against which to measure their own work. The result is not underperformance by individuals — it is a team working hard inside a set of structural constraints that make consistent, defensible, timely resolution impossible regardless of individual effort.

---

## 2b. Problem statement — business perspective

At the volumes stated in the scenario (~730 cases/day across a 35-person team), Customer Operations is consuming a significant share of its capacity on work that is either structurally lookup-and-respond (ETA inquiries: 400/day × 4 min = 1,600 agent-minutes/day) or structurally bottlenecked by a system constraint that no amount of additional headcount can resolve (billing disputes: capped at 48-hour turnaround per invoice modification regardless of team size). The competitor benchmark cited by the CEO — £1.2M annualised saving on customer service via AI — has created an explicit board-level expectation that Sarah Whitmore must respond to. Two prior automation initiatives have failed, exposing the business to reputational risk with the COO and reducing stakeholder confidence in any new initiative. The billing dispute evidence (a repeat customer, C-04451, holding 3 open disputes simultaneously — including one open since 28 February 2026) suggests that unresolved disputes are not isolated incidents but a systemic pattern that affects customer retention. A goodwill credit applied without an audit trail entry (Artefact 2) represents a financial control gap: credits are being issued without approval records, which creates exposure in any regulatory or audit review. The business case for intervention is not primarily about headcount reduction; it is about restoring service reliability on a high-volume, time-sensitive process while closing the compliance gap before it becomes a formal finding.

---

## 3. Why an AI agent — not traditional software, not RPA, not a process change

**Traditional software (rule-based automation or workflow tooling):** ETA inquiries — the most structured work stream — could in principle be handled by a simple API integration between the CRM and the Driver App. But delivery exceptions arrive as unstructured voice and text (driver voicemails, customer emails), require contextual judgment (damaged consignment with an incomplete SOP, a driver waiting with 6 more drops), and vary in ways that a rule-based system cannot enumerate. Billing disputes require cross-referencing invoice data, delivery history, and customer account standing across systems with no shared real-time state. Traditional software handles variation by routing it to humans as exceptions; the exception rate here is the norm, not the edge case.

**RPA (Robotic Process Automation):** Already attempted for billing reconciliation and already failed. The stated failure mode — the RPA broke whenever Aurum's schema changed, which happens approximately quarterly without prior notice — is not a deployment failure; it is a structural incompatibility between RPA's screen-scraping / fixed-field dependency and a system that does not offer a stable interface. Rebuilding the same approach on the same system would produce the same result. RPA also cannot handle the unstructured inputs that drive exceptions and disputes.

**A customer-facing chatbot:** Already attempted in 2024 and rejected by customers. The failure aligns with a known pattern: rule-based or retrieval-only chatbots fail when the customer's query requires judgment, context, or action — and at Apex, the majority of contacts (exceptions, disputes, dispatch adjustments) require all three. A chatbot that can only answer ETA inquiries is handling 55% of volume (400/730) and deflecting the harder cases back to already-stretched agents.

**Process redesign alone:** The SOP could be updated and the informal credit process could be formalised, but neither change addresses the structural bottleneck: billing modifications still require a 48-hour manual Aurum ticket regardless of how well the process is documented. A tighter escalation procedure does not increase throughput. Process change is a necessary companion to agent design — it is not a substitute for it.

**An AI agent is the right intervention** because: (1) it can handle unstructured inputs (driver messages, customer emails) and extract structured signals from them; (2) it can operate as a HITL co-pilot for judgment-heavy cases without requiring full autonomy; (3) it can enforce audit trail compliance mechanically, closing the credit-logging gap without relying on agent discipline under pressure; (4) it can be designed to be resilient to Aurum schema changes by operating at the batch-export layer (reading CSV exports) rather than integrating directly into Aurum — the same constraint that broke RPA becomes a design parameter, not a blocker.

---

## 4. Success metrics

| Metric | Baseline (source) | Target | How measured | Timeframe |
|--------|-------------------|--------|--------------|-----------|
| ETA inquiry handle time (per case) | 4 min/case (scenario) | 1 min/case | CRM case duration field, sampled weekly | 90 days post-deployment |
| Billing dispute first-response time | 9 days observed in Artefact 2 (single data point — see A-1) | Same business day acknowledgement (≤4 hours) | CRM case open date vs. first outbound contact timestamp | 90 days post-deployment |
| Credit audit trail compliance rate | Unknown — Artefact 2 shows at least one credit applied with no audit log entry (see A-2) | 100% of agent-issued credits have an APEX_CREDITS entry with APPROVER_ID and AUDIT_REF populated | APEX_CREDITS_YYYYMMDD.csv row count vs. CRM credit actions, reconciled daily | 30 days post-deployment |
| ETA inquiries handled per day without headcount increase | ~400/day handled by human agents (scenario) | 400/day handled by agent autonomously, human agent queue <50 escalations/day | CRM case volume by type and by resolution path (agent vs. human) | 90 days post-deployment |
| Repeat dispute rate for key accounts | C-04451 holds 3 simultaneous open disputes (APEX_DISPUTES export, 2026-04-14) — pattern unconfirmed at population level (see A-3) | <1 open dispute per account at any point in time for accounts with >£5k/month billing | APEX_DISPUTES_OPEN export, weekly count of accounts with >1 open dispute | 180 days post-deployment |
| Delivery exception decision time | 12 min/case average (scenario) | 6 min/case average (agent pre-populates case with structured summary; dispatcher decides) | CRM case duration for exception case type | 90 days post-deployment |

---

## 5. Assumption log

> **Assumption A-1:** The 9-day billing dispute resolution observed in Artefact 2 (Hayes & Sons Ltd) is representative of a systemic pattern, not an outlier case.
> **Why it matters:** Drives the baseline for the billing dispute turnaround metric. If the average is 3–4 days, the target and the improvement story both change.
> **If wrong:** If most billing disputes resolve within 2–3 days, the turnaround improvement is less dramatic and a different metric (credit accuracy, repeat dispute rate) should be the primary success indicator.
> **Confidence:** Medium — the APEX_DISPUTES export shows disputes open for 30+ days (D-2026-00318 opened 28 Feb 2026) alongside faster cases, suggesting high variance rather than a consistent baseline. Validate by pulling average age of open disputes from APEX_DISPUTES across a rolling 90-day period.

> **Assumption A-2:** The credit audit trail compliance rate is materially below 100% — the Artefact 2 example (credit applied with no APEX_CREDITS entry) reflects an ongoing pattern of informal credit application, not a one-off incident.
> **Why it matters:** Sets the compliance baseline for the audit trail metric. If most credits are already logged correctly and Artefact 2 is an outlier, the compliance target is already nearly met and does not justify design complexity.
> **If wrong:** If the APEX_CREDITS export captures >95% of credits issued in practice, the audit trail gap is smaller than assumed and the agent's audit enforcement role is less critical.
> **Confidence:** Medium — the internal note in Artefact 2 is explicit ("no entry in the credits audit log for this £170"), and the informal credit behaviour described aligns with the domain-typical gap identified in D0A. Validate by reconciling CRM credit action count vs. APEX_CREDITS row count over a 30-day sample.

> **Assumption A-3:** The repeat dispute pattern visible for C-04451 (Hayes & Sons, 3 simultaneous open disputes) is representative of a broader pattern of unresolved disputes accumulating on key accounts, not a single-account anomaly.
> **Why it matters:** Drives the downstream stakeholder metric (repeat dispute rate). If C-04451 is an outlier, this metric is irrelevant to most customers and a different stakeholder-facing measure should be chosen.
> **If wrong:** If repeat disputes are concentrated in 1–2 accounts and rare elsewhere, the metric should be reframed as average dispute age or customer escalation rate.
> **Confidence:** Low — the sample data covers 6 open disputes across 5 customers; insufficient to confirm or disconfirm at population level. Validate by pulling APEX_DISPUTES across a full 90-day period and counting accounts with >1 dispute per quarter.

> **Assumption A-4:** The total daily handle-time load (~7,060 agent-minutes/day, derived from scenario volumes × per-case times) is absorbed within the 35-person team's available capacity without consistent overtime or queue backlog. If this is wrong and the team is already backlogged, baseline performance is worse than stated and the improvement targets should be recalibrated upward.
> **Why it matters:** Determines whether the scenario volumes represent a manageable steady-state or an already-stressed team operating above capacity. Affects the framing of agent ROI — relief of strain vs. capacity creation.
> **If wrong:** If the team is regularly operating in backlog, the baseline case-age metrics will be longer than handle-time estimates suggest, and the business case for agent deployment is stronger.
> **Confidence:** Medium — ~7,060 agent-minutes/day across 35 agents = ~202 min/agent/day of direct case-handling time, which is plausible as a fraction of a working day without being backlog-inducing. But the 22-minute hold time in Artefact 2 suggests at least some queue pressure at peak. Validate by asking the COO or team lead whether the team consistently clears the daily queue.
