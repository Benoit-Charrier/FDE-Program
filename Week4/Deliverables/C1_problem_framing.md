# C1: Problem Framing & Success Metrics
**Engagement:** Greenfield Health Systems — Medical Claims Adjudication Transformation
**Phase:** ATX Assessment — Problem Framing
**Prepared:** 2026-05-20
**Source of truth:** `Scenario/scenario_context.md`; informed by `Deliverables/D0C_discovery.md`

---

## 0. Executive Summary

- **Core business problem:** Greenfield's medical claims adjudication operates at 22% auto-adjudication — against an 85% industry benchmark (scenario.md) — because its manual workflow does not differentiate between rule-bound administrative decisions and judgment-requiring clinical decisions, forcing all 2,000 claims/day through the same full-manual process and producing a cycle time of 8–9 days that already exceeds the 7-day SLA penalty threshold (Exchange 3).
- **Why the existing approach cannot scale:** The structural constraint is the absence of a clinical content classifier — without a formal, codified definition of what constitutes a clinical claim, processors route claims to physician review using undocumented pattern recognition, making accurate high-volume triage structurally impossible and producing the 41% denial appeal overturn rate (scenario.md) that signals systematic first-pass errors.
- **The agent intervention:** A two-agent system — an administrative adjudication agent handling the 65% of claims with no clinical content and a clinical pre-screening agent assembling physician review context for the 35% with clinical content — must achieve ≥85% auto-adjudication, reduce cycle time to ≤5 days for administrative claims and ≤7 days for clinical claims, and reduce the denial appeal overturn rate to ≤15% within 12 months of go-live.

---

## 1. Table of Contents

- [0. Executive summary](#0-executive-summary)
- [1. Table of contents](#1-table-of-contents)
- [2a. Problem statement — lived experience today](#2a-problem-statement--lived-experience-today)
- [2b. What is actually broken — root cause diagnosis](#2b-what-is-actually-broken--root-cause-diagnosis)
- [3. Why an AI agent — not traditional software, not RPA, not a process change](#3-why-an-ai-agent--not-traditional-software-not-rpa-not-a-process-change)
- [4. What success looks like — by stakeholder](#4-what-success-looks-like--by-stakeholder)
- [5. Assumption log](#5-assumption-log)

---

## 2a. Problem statement — lived experience today

### 2a-i. Claims processors and clinical reviewers (the team doing the work)

A claims processor at Greenfield starts each day facing a queue of claims that the current system cannot process at the rate they arrive. At the current 78% manual processing rate (100% minus the 22% auto-adjudication rate, scenario.md) against ~2,000 claims/day, the team is managing roughly 1,560 claims/day requiring full manual handling. At 35 minutes per claim (scenario.md), that represents approximately 54,600 person-minutes of manual adjudication work daily — against a 45-person team capacity of approximately 21,600 person-minutes per day (45 × 8 hrs × 60 min). The daily incoming workload is roughly 2.5 times what the team can process in a single day, which is exactly what produces the 8–9 day cycle time and the SLA penalty exposure James Liu escalated in Exchange 3.

The processor's experience is one of volume pressure applied to cognitively mixed work. Every claim requires: an eligibility verification requiring a system cross-reference, a coding validation that mixes rules lookup with clinical plausibility judgment, a prior auth completeness check requiring a manual reconciliation between two likely-separate systems, and — critically — an undocumented routing decision about whether the claim contains clinical content. This routing decision is the most consequential step in the process and the one with the least support: there is no formal criterion, no classifier, and no training document that defines what "clinical content" means. Processors apply personal pattern recognition, which varies across the team.

Physician reviewers experience a different version of the same problem. For every claim that reaches them, they must first gather clinical context from scratch — assembling diagnosis codes, procedure history, prior authorisation records, and clinical notes from sources that are not pre-organised for their review. This context-assembly phase is information retrieval work, not clinical judgment, yet it consumes physician time before any medical reasoning begins. Dr. Marcus Webb's estimate of 20 claims per hour achievable with agent pre-screening (Exchange 3) implies that the current throughput without pre-screening is substantially lower — physicians are spending a disproportionate fraction of their review time on data gathering, not decision-making.

### 2a-ii. Healthcare providers (hospitals, physician groups — the submitting parties)

*Note: provider experience is not directly described in scenario_context.md. The following paragraph is derived from the scenario's performance metrics and standard payer-provider dynamics. Each inference is flagged as assumption A-C1-4 through A-C1-6 in Section 5.*

A hospital billing department or physician group submitting claims to Greenfield currently waits an average of 8–9 days for an adjudication decision (scenario.md, Exchange 3) — already past the 7-day SLA threshold that even Greenfield's own payer contracts enforce. For the 41% of denied claims that are eventually overturned on appeal (scenario.md), the provider's experience is worse: the initial denial triggers appeal work — compiling additional documentation, writing appeal letters, resubmitting — and the provider waits further for appeal resolution before receiving payment. Each overturn represents a claim that was correctly submitted, incorrectly denied, and then corrected only through the provider bearing the cost of the appeal process (assumption A-C1-4). Providers with high claim volume absorb this as a structural overhead: dedicated denial management staff, delayed cash flow on legitimate receivables, and a relationship with Greenfield characterised by unpredictability. Providers cannot distinguish between a denial that reflects a genuine coverage gap and a denial that will be overturned — because with a 41% overturn rate, the denial itself is not a reliable signal of coverage status (assumption A-C1-5).

### 2a-iii. Health plan members (patients — the people whose care is affected)

*Note: member experience is not directly described in scenario_context.md. The following paragraph is derived from the 41% denial overturn rate and the 8–9 day cycle time. Inferences are flagged as assumption A-C1-7 in Section 5.*

A health plan member whose claim is denied receives a denial notice after 8–9 days. For the 41% of denials that are incorrect (scenario.md — denial appeal overturn rate), the member has two paths: appeal the decision, or accept it. A member who appeals must navigate a process that takes additional weeks, may require documentation they don't know how to gather, and may involve coordination between their provider and the payer that the member does not control. A member who accepts the denial without appealing may be paying out-of-pocket for care their plan should have covered — because the denial was incorrect but was never challenged. This is the most consequential downstream effect of a 41% overturn rate: the overturn rate measures only the appeals that were filed and won, not the incorrect denials that were never appealed (assumption A-C1-7). For members facing elective procedures or ongoing treatment requiring prior authorisation, a 9-day adjudication cycle can delay care if treatment decisions depend on confirmed coverage status — particularly for procedures where providers will not schedule without confirmed approval (assumption A-C1-7).

---

## 2b. What is actually broken — root cause diagnosis

> **Broken [B-1]:** The claims adjudication process has no mechanism to distinguish rule-bound decisions from judgment-requiring decisions before work begins — every claim enters the same full-manual workflow regardless of complexity.
> **Symptom it produces:** 22% auto-adjudication rate against an 85% industry benchmark (scenario.md); 1,560 claims/day requiring full manual processing; daily workload 2.5× team capacity (derived); 8–9 day cycle time; active SLA penalty incurrence (Exchange 3).
> **Why it persists:** Differentiating administrative from clinical claims requires a formal clinical content classifier, which requires a cross-functional definition of "clinical content" agreed between the CMO (Dr. Webb) and Operations (James Liu). That definition has not been produced — Sarah Chen's Exchange 3 request makes this explicit. Without the definition, the triage that would enable selective automation cannot be built. The undifferentiated manual workflow continues because the prerequisite governance decision (defining clinical content) has not been made.
> **What fixing it unlocks:** Once the clinical content boundary is defined and a classifier is built, 65% of claims (administrative path, Exchange 3 negotiated target) can be processed by an agent with no physician involvement; physician capacity is concentrated on the 35% of claims that actually require clinical judgment; the daily processing volume becomes manageable at a significantly reduced FTE base; cycle time targets (4–5 days admin, 6–7 days clinical, Exchange 3) become achievable.

---

> **Broken [B-2]:** The first-pass routing and adjudication decisions that determine physician review and denial outcomes are made without a formal decision criterion, producing inconsistent and error-prone outputs at scale.
> **Symptom it produces:** 41% denial appeal overturn rate (scenario.md) — meaning roughly 4 in 10 appealed denial decisions were incorrect at first pass; providers bear the appeal burden; members bear access-to-care consequences; Greenfield incurs rework cost on every overturned denial.
> **Why it persists:** The routing decision (clinical vs. administrative) is made by processors using personal pattern recognition because no documented clinical flagging criterion exists. The medical necessity determination downstream is made by physicians who are assembling context manually rather than reviewing pre-structured evidence — which means the quality of the physician determination is constrained by whatever context the physician managed to gather. Neither decision point has a formal quality check or feedback loop that would surface systematic errors back to the processors making routing calls. The 41% overturn rate is the lagging indicator; by the time it appears in reporting, thousands of incorrect first-pass decisions have already been made.
> **What fixing it unlocks:** A formal clinical content classifier reduces routing errors at source. An agent-generated pre-filled review packet ensures physicians make determinations against complete, consistently structured evidence. Both interventions directly reduce the upstream cause of overturns — not the overturns themselves, but the information gaps and inconsistent routing that produce them.

---

## 3. Why an AI agent — not traditional software, not RPA, not a process change

**A rules engine or deterministic auto-adjudication expansion (RPA)** is the right answer for a subset of what is broken — specifically, eligibility verification on the standard path and fee schedule application for non-exception claims. These steps are binary, rule-bound, and do not require judgment: a member was eligible or not; a fee schedule entry applies or it doesn't. An RPA solution for these steps is not only viable but preferable to an agent for cost and predictability reasons, and D0C identifies eligibility verification's standard path as an explicit RPA candidate. However, RPA cannot address the two root causes identified in 2b. A rules engine cannot classify clinical content — the routing decision requires pattern recognition across semi-structured diagnosis and procedure code combinations where the boundary between clinical and administrative is judgment-dependent and currently undefined. A rules engine cannot detect coding plausibility edge cases where a code is technically valid but contextually implausible. A rules engine cannot assemble a pre-filled physician review packet from multi-source clinical documentation — that requires dynamic retrieval and synthesis, not rule execution. The 41% overturn rate is not a rules compliance failure; it is a classification accuracy failure. RPA does not fix it.

**A workflow tool or case management system upgrade** optimises queue management, task routing, and process visibility — it does not reduce the cognitive work inside each claim. The bottleneck at Greenfield is not that claims are slow to route between processors; it is that each claim requires 35 minutes of manual adjudication work once it arrives with a processor (scenario.md). A case management system that routes a claim faster to a processor does not reduce the time that processor spends on eligibility lookup, coding validation, prior auth reconciliation, or the undocumented routing decision. The auto-adjudication rate stays at 22%. The cycle time does not fall below the SLA threshold. The denial overturn rate is unchanged. A workflow upgrade is a process visibility improvement; it does not substitute for the cognitive labour that is causing the capacity problem.

**Hiring more processors or reviewers** directly contradicts the financial case and the CFO mandate. Sarah Chen's Exchange 1 email establishes a non-negotiable 40% headcount reduction as the condition under which the $400K implementation budget is justified. More importantly, adding processors does not fix the structural accuracy problem: more processors applying the same undocumented routing criteria produce more claims at the same 41% overturn rate — at higher cost. The daily workload math (54,600 person-minutes needed vs. 21,600 available at current team size) implies that maintaining current throughput without automation would require approximately 2.5× the current team — roughly 112 processors — at a labour cost the $400K budget cannot support and a headcount trajectory the CFO will not approve. Hiring is not a solution to an accuracy problem, and it is not viable as a capacity solution at the required scale.

The agent case is grounded in what RPA and process tools cannot do: classify semi-structured inputs into a routing decision, detect judgment-requiring anomalies in coding, and synthesise multi-source clinical context into a structured pre-read. These are the specific tasks where the cost of human attention is highest and where the structural failures in 2b are concentrated.

---

## 4. What success looks like — by stakeholder

### 4a. Success for Greenfield Health Systems

*Planning volume: 2,000 claims/day (operative assumption — see A-C1-1). All baselines sourced from scenario_context.md unless labelled.*

| Metric | Baseline | Target | How measured | Timeframe |
|---|---|---|---|---|
| Auto-adjudication rate (throughput) | 22% (scenario.md) | 85% | Claims management system audit log: count of claims resolved without human intervention ÷ total claims received, 30-day rolling | 12 months post-go-live |
| Administrative path cycle time | 8–9 days blended average (scenario.md: 8 days average; Exchange 3: currently 9+ days) | ≤5 days | Claims management system: submission date to adjudication decision date for WS1 claims, 30-day rolling median | 6 months post-go-live |
| Clinical path cycle time | 8–9 days blended average | ≤7 days | Claims management system: submission date to physician sign-off date for WS2 claims, 30-day rolling median | 6 months post-go-live |
| Average human processing time per claim — WS2 clinical path (physician review) | 35 min/claim overall average across all claim types (scenario.md); per-path breakdown not stated — 35 min is the only baseline available | ≤3 min/claim physician review time with agent pre-screening (derived from Dr. Marcus Webb's 20 claims/hour estimate with pre-screening, Exchange 3) | Claims management system time-tracking: physician queue open-time to signed determination per WS2 claim, 30-day rolling average | 12 months post-go-live |
| Claims review FTE headcount | 20 review staff (CFO email Exchange 1; James Liu Exchange 3 — note: inconsistency between 8 FTE reduction per CFO and 13 FTE reduction per James Liu; see A-C1-2) | 7 review staff (James Liu, Exchange 3) | HR headcount record for claims review role classification | 6 months post-go-live |
| Denial appeal overturn rate (quality) | 41% (scenario.md) | ≤15% | Appeals management system: count of overturned appeal decisions ÷ total appeals filed, 90-day rolling | 12 months post-go-live |
| SLA penalty incidence | Penalties currently live — claims running 9+ days (Exchange 3) | 0 claims exceeding 7-day threshold | Claims management system: count of claims with adjudication decision date > submission date + 7 calendar days, 30-day rolling | 6 months post-go-live |
| Claims processing error rate | ~1.2% (scenario_enriched.md) | ≤1.0% | Quality assurance audit sample: 200 randomly selected adjudicated claims per month, error rate by independent reviewer | 12 months post-go-live |

### 4b. Success for healthcare providers

*Baselines not in scenario_context.md are labelled as assumptions. Provider-facing metrics are derived from Greenfield's adjudication performance, as the scenario provides no direct provider data.*

| Metric | Baseline | Target | How measured |Timeframe |
|---|---|---|---|---|
| Days to adjudication decision / payment clearance (timeliness) | ~8–9 days for adjudication decision (scenario.md, Exchange 3); payment processing lag on top of this is unknown (assumption A-C1-4) | ≤7 days from claim submission to adjudication decision | Provider remittance data: submission timestamp to remittance advice date, 30-day rolling median | 6 months post-go-live |
| Incorrect denial rate — proportion of denials subsequently overturned (accuracy) | Baseline: 41% of filed appeals overturned (scenario.md); proportion of all denials that are incorrect is unknown — 41% overturn rate applies only to appealed claims (assumption A-C1-5) | Denial appeal overturn rate ≤15% of filed appeals | Appeals management system: overturned decisions ÷ appeals filed, 90-day rolling | 12 months post-go-live |
| Denial reason specificity (transparency) | Unknown — denial reason quality not described in scenario (assumption A-C1-6) | 100% of denial notices include a specific, actionable reason code with no generic uncodified rejections | Audit of 100 consecutive denial notices per quarter: % containing a specific reason code from the standard denial reason code set | 6 months post-go-live |
| Appeal resolution time | Unknown baseline (assumption A-C1-6) | ≤30 days from appeal submission to final decision | Appeals management system: appeal submission date to final determination date, 90-day rolling median | 12 months post-go-live |

### 4c. Success for health plan members

*Baselines not in scenario_context.md are labelled as assumptions. Member-facing metrics are derived from the adjudication performance metrics available in the scenario.*

| Metric | Baseline | Target | How measured | Timeframe |
|---|---|---|---|---|
| Days to coverage decision (timeliness) | 8–9 days (scenario.md, Exchange 3) | ≤7 days from claim submission to member notification | Claims management system: submission date to member notification date, 30-day rolling median | 6 months post-go-live |
| Denial appeal overturn rate — proxy for wrongful denial rate (accuracy) | 41% of filed appeals overturned (scenario.md) | ≤15% of filed appeals overturned | Appeals management system: overturned decisions ÷ appeals filed, 90-day rolling | 12 months post-go-live |
| Claims requiring appeal to obtain correct coverage outcome (access-to-care) | Unknown — the scenario provides only the overturn rate for appealed claims; total denied volume and appeal filing rate are not stated (assumption A-C1-7); current rate is derived as: if 41% of all appeals are overturned, and assuming a non-trivial proportion of denied claims are appealed, the proportion of all claims requiring appeal for correct resolution is material | ≤5% of all adjudicated claims require a member appeal to obtain the correct coverage outcome | Claims management system: total appeal-overturned decisions ÷ total adjudicated claims, 90-day rolling | 12 months post-go-live |

---

## 5. Assumption Log

> **Assumption [A-C1-1]:** 2,000 claims/day is used as the operative planning volume. Both 2,000/day (scenario.md) and 1,667/day (Sarah Chen, Exchange 3) are stated directly in the scenario and are not reconciled. 2,000/day is used as the conservative (higher) planning number per scenario_context.md Section 8.
> **Why it matters:** Volume is the denominator for all throughput, economic, and capacity metrics. The 17% difference between the two figures affects target FTE requirements, token cost model, and payback period.
> **If wrong:** If the operative volume is 1,667/day, all volume-dependent metrics scale down proportionally. All Greenfield targets in Section 4a remain valid but the absolute capacity headroom increases slightly.
> **Confidence:** Medium — both figures are stated in the scenario; the discrepancy is unresolved.

---

> **Assumption [A-C1-2]:** The 35%/65% clinical/administrative routing split is a stakeholder-negotiated estimate, not a measured baseline. Dr. Marcus Webb's language in Exchange 3 was "honestly? maybe 30–35%." The 65% administrative path is the target design, not a confirmed empirical figure.
> **Why it matters:** If the true clinical content rate is higher than 35%, the HITL physician queue receives more claims than the 20 claims/hour throughput target can absorb, and the cycle time targets in Section 4a become unachievable without additional physician capacity. The headcount model (20 → 7 review staff) also depends on this split.
> **If wrong:** A higher clinical rate (e.g., 50%) requires either more physician capacity or a more precise classifier. The FTE reduction and cycle time targets change materially.
> **Confidence:** Low — Dr. Webb's estimate was explicitly hedged; it has not been validated against claims data.

---

> **Assumption [A-C1-3]:** The ≤15% denial appeal overturn rate target is derived from industry benchmarks for well-functioning commercial health plan auto-adjudication environments. It is not stated in scenario_context.md.
> **Why it matters:** This target is the primary quality success metric for Greenfield (Section 4a), providers (Section 4b), and members (Section 4c). The target level determines whether the agent's classification accuracy is sufficient to certify the system.
> **If wrong:** If Greenfield's payer contracts or accreditation requirements specify a different overturn rate threshold, the classifier accuracy requirement changes accordingly.
> **Confidence:** Medium — consistent with commercial healthcare payer benchmarks; must be confirmed with Dr. Webb and Sarah Chen as part of stakeholder alignment.

---

> **Assumption [A-C1-4]:** Provider cash flow is materially affected by the current 8–9 day adjudication cycle and the denial-and-appeal cycle for the 41% overturn rate. Providers bear overhead costs for denial management work on incorrect denials. These impacts are standard in payer-provider dynamics and are inferred from the scenario's performance metrics, not stated directly.
> **Why it matters:** Provider success metrics in Section 4b are grounded in this assumption. If providers have contractual structures that insulate them from payment timing (e.g., capitated arrangements), some of these metrics lose relevance.
> **If wrong:** Provider-facing success metrics may need to be reframed around different outcomes (e.g., claim acceptance rate on first submission rather than payment cycle time) depending on provider contract structures.
> **Confidence:** Low — not stated in scenario; derived from standard payer-provider dynamics.

---

> **Assumption [A-C1-5]:** Providers cannot reliably distinguish between denials that will be overturned on appeal and denials that reflect genuine coverage gaps, because the 41% overturn rate is not visible to them at the individual claim level. Providers treat all denials as potentially incorrect until reviewed, adding appeal-filing overhead to their operations.
> **Why it matters:** This assumption drives the "denial reason specificity" provider metric in Section 4b. If providers already have sufficient visibility to triage denials accurately, the transparency metric is lower priority.
> **If wrong:** If Greenfield provides rich denial reason codes today that allow providers to quickly identify clearly correct denials, the transparency gap is less severe than assumed.
> **Confidence:** Low — not stated in scenario; derived from the 41% overturn rate as evidence of a provider-visible quality problem.

---

> **Assumption [A-C1-6]:** Denial reason quality and appeal resolution time are not described in scenario_context.md. Both are treated as unknown baselines in Section 4b. Targets (100% specific reason codes; ≤30 days appeal resolution) are derived from standard commercial health plan quality standards.
> **Why it matters:** These metrics define the provider experience improvement the agent system must produce. If baseline denial reason quality is already high, the transparency metric is already partially met.
> **If wrong:** If baseline denial reason codes are already specific and actionable, the agent does not need to improve on this dimension and the metric target is achievable at current state.
> **Confidence:** Low — inferred from the 41% overturn rate as indirect evidence that denial quality has problems; not directly stated.

---

> **Assumption [A-C1-7]:** A material proportion of health plan members who receive an incorrect denial do not file appeals — they either pay out-of-pocket or forgo the care. The 41% overturn rate represents only appealed-and-overturned decisions; the total rate of incorrect denials (including those not appealed) is higher.
> **Why it matters:** The member access-to-care metric (≤5% of claims requiring appeal for correct resolution) is grounded in this assumption. If members routinely appeal incorrect denials, the metric is tracking the correct population. If members do not appeal, the metric undercounts the access-to-care impact.
> **If wrong:** If members reliably appeal incorrect denials, the 41% overturn rate is a more complete picture of incorrect denial volume, and the member access-to-care impact is contained within the appeal population.
> **Confidence:** Low — not stated in scenario; derived from standard health insurance access-to-care research patterns.
