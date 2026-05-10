# D0B — Problem Statement and Success Metrics
**Helix Workforce Software — Vendor Contract Clause Review**
**Produced:** 2026-05-04 | **Status:** Draft — awaiting FDE approval

---

## 0. Executive Summary

- **Core business problem:** Helix's Legal & Commercial team (5 people) takes 4–6 business days to return a vendor contract, a pace the CRO has identified as incompatible with enterprise sales targets at 25% YoY growth.
- **Why the existing approach cannot scale:** Every one of ~300 contracts per quarter must pass through a single paralegal (Tom Reilly) for first-pass clause classification — a ~25 min/case reading-and-comparison task that is mechanical in nature but requires unstructured document interpretation that neither the CLM, RPA, nor an additional hire can solve at acceptable unit cost.
- **The agent intervention:** An AI agent performing first-pass clause classification against the playbook would reduce WS1 time-per-case from ~25 min to ~8 min and enable the team to process ≥400 contracts per quarter without a headcount increase, bringing turnaround to ≤3 business days.

---

## 1. Table of Contents

1. Table of Contents
2. Problem Statement — Team's Perspective
3. Problem Statement — Business Perspective
4. Why an AI Agent — Not Traditional Software, Not RPA, Not a Process Change
5. Success Metrics
6. Assumption Log

---

## 2. Problem Statement — Team's Perspective

Tom Reilly, the team's sole paralegal, is the single throughput bottleneck for the entire 300-contract-per-quarter pipeline. WS1 (first-pass clause classification) consumes approximately 125 hours per quarter — ~10 hours per week — of his available time, and WS2 (standard-deviation redlining) adds another ~45 hours per quarter. The task in WS1 is structurally mechanical: read each clause, identify which playbook category it falls into, and flag deviations. Yet the task demands sustained close reading of 15–40-page documents, and the artefacts reveal that the escalation threshold between WS2 and WS3 is not cleanly rule-bound — Tom is making unsanctioned judgment calls (as in Artefact 2.1, where he decided a below-playbook liability cap was "borderline negotiable, not escalation") because no precise written threshold exists. Simultaneously, the playbook he is working against is stale: the DPA section has not been updated since the DPDI Act Q1 changes, meaning Tom is flagging DPA clauses against an outdated standard. The result is a team in which the person doing the most volume-sensitive work is also the person most exposed to compliance drift and judgment calls that exceed their formal authority — with no systematic mechanism to surface or correct either.

## 3. Problem Statement — Business Perspective

At Helix's current growth rate (25% YoY, ARR £42M), enterprise sales velocity depends on legal clearance of vendor contracts being a competitive differentiator, not a bottleneck. The current 4–6 business day turnaround is already unworkable by the CRO's assessment. At 300 contracts per quarter and 5 staff, the team's total contract review load is approximately 260 hours per quarter (WS1: 125 hrs, WS2: 45 hrs, WS3: 45 hrs, WS4: 45 hrs — see Assumption A1). If volume grows in line with the company's 25% YoY trajectory, the team will face ~375 contracts per quarter within one year — a 25% increase in load with no corresponding headcount increase planned. The structure of the work makes this a compounding problem: the first-pass classification step (WS1) is a prerequisite gate for every contract, so queue time at WS1 propagates downstream through WS2, WS3, and WS4. Adding headcount addresses the symptom at a unit cost of approximately £35–50k per additional paralegal (see Assumption A2) without eliminating the structural serial queuing that creates the turnaround delay. A 5-person team reviewing 300 contracts per quarter at 4–6 days per contract is also working at a risk level: one absence, one quarter-end spike, or one regulatory change (like the currently unincorporated DPDI Act updates) can create material legal exposure across a cohort of executed contracts.

---

## 4. Why an AI Agent — Not Traditional Software, Not RPA, Not a Process Change

**Not a CLM configuration fix:** Ironclad is already in place and used. The gap is not that Helix lacks a CLM — it is that first-pass clause classification requires reading and interpreting unstructured natural-language contract text and comparing it against a nuanced playbook. CLM rules engines can match structured metadata and trigger routing rules, but they cannot read a 40-page Word document received via email, identify a non-standard limitation of liability formulation, and classify it against a position statement. That task requires language understanding that is outside the capability class of CLM workflow configuration.

**Not RPA:** RPA requires structured, deterministic inputs. Vendor contracts arrive as Word documents via email (sometimes bypassing the CLM entirely, as confirmed in Artefact 2.2 — recurring for at least 3 vendors this quarter), contain varied clause numbering and drafting styles, and must be interpreted against a playbook stored as a SharePoint page of position statements. There is no structured form to scrape, no predictable field to read, and no rule that can be expressed as a click path. RPA would break on the first non-standard document layout.

**Not a process change alone:** The playbook could be updated (it needs to be — the DPA section is stale), and escalation thresholds could be codified more precisely. But even with a fully current, unambiguous playbook, a human still needs to read each contract clause-by-clause and compare it to the position. The bottleneck is the reading-and-comparison act itself, not the standard being applied. A process change removes the compliance drift risk; it does not remove the 125-hour-per-quarter WS1 labour burden.

**Not additional headcount:** Hiring a second paralegal addresses Tom's WS1 capacity in the short term. It does not reduce time-per-case, does not improve accuracy, does not address the stale playbook risk, and does not scale gracefully with growth. It adds a recurring cost (£35–50k/yr, Assumption A2) to solve a throughput problem that will recur the moment volume grows another 25%.

An AI agent that performs first-pass clause classification — reading the contract, mapping clauses to playbook categories, generating a structured deviation report for human review — is the correct intervention because it addresses the bottleneck at the point of maximum volume (WS1: 300 cases/quarter), keeps a human in the loop at the judgment and sign-off points (WS3, WS4) where Amelia's hard rule applies, and can incorporate playbook updates immediately upon revision, eliminating the compliance drift cycle.

---

## 5. Success Metrics

| Metric | Baseline (from scenario) | Target | How measured | Timeframe |
|---|---|---|---|---|
| Contract turnaround time (intake to counteroffer sent) | 4–6 business days | ≤3 business days | Timestamp delta between Ironclad intake record and outbound counteroffer sent (or Outlook send timestamp for email-channel deliveries) | 6 months post-deployment |
| WS1 time-per-case (first-pass clause classification) | ~25 min/case | ≤8 min/case (human review of agent classification report) | Time-tracked in Ironclad or manual log; sampled weekly across 20 contracts | 3 months post-deployment |
| WS1 clause classification accuracy | Not stated in scenario — see Assumption A3 | ≥95% correct clause categorisations (playbook match / deviation / escalation) | Weekly audit: lawyer reviews agent classification output for a random 10% sample and records corrections | 3 months post-deployment |
| Contracts processed per quarter without headcount increase | ~300/quarter (1 paralegal + 3 lawyers + GC) | ≥375/quarter (consistent with 25% YoY growth) | Contract count from Ironclad quarterly report | 12 months post-deployment |
| CRO-facing: % of contracts with counteroffer returned within 3 business days | Not stated; implied <50% given current 4–6 day average (see Assumption A4) | ≥80% of counteroffers returned within 3 business days | Ironclad or Outlook timestamp audit, reported monthly to CRO | 6 months post-deployment |

---

## 6. Assumption Log

> **Assumption [A1]:** Total quarterly labour of ~260 hours is computed from the work stream volumes and times stated in the enriched scenario (WS1: 300×25 min = 125 hrs; WS2: 60×45 min = 45 hrs; WS3: 30×90 min = 45 hrs; WS4: 90×30 min = 45 hrs). This is an arithmetic derivation from scenario facts, not an independently verified figure.
> **Why it matters:** The labour burden total underpins the economic case and the capacity-at-growth projection.
> **If wrong:** If work stream times or volumes differ materially from stated figures, the total labour estimate and the capacity headroom calculation both change.
> **Confidence:** Medium (volumes and times are stated as approximations in the scenario)

> **Assumption [A2]:** A replacement paralegal hire would cost approximately £35–50k per year (fully loaded). This figure is not stated in the scenario and is used only to compare the agent intervention against the headcount alternative.
> **Why it matters:** If wrong in either direction, it affects the comparative cost argument in Section 4.
> **If wrong:** If fully loaded cost is significantly lower (e.g., £25k), the headcount alternative becomes more competitive in the short term, weakening the agent ROI case.
> **Confidence:** Medium (UK paralegal market rate; not validated against Helix's actual compensation bands)
> **How to validate:** HR or finance confirmation of actual paralegal fully-loaded cost.

> **Assumption [A3]:** There is no stated baseline accuracy rate for Tom's first-pass clause classification. The 95% accuracy target in the success metrics is the minimum acceptable threshold for the agent to replace manual classification without increasing legal risk — it is not derived from a current measured error rate.
> **Why it matters:** The accuracy target determines whether the agent is fit for production use and at what review overhead. If current human accuracy is already <95%, the agent is being held to a higher standard than the baseline it replaces.
> **If wrong:** If human classification accuracy is measurably lower than 95% (which the artefacts suggest is possible — Tom made an unsanctioned judgment call in Artefact 2.1), the accuracy target may need to be reframed relative to current performance, not an absolute standard.
> **Confidence:** Low (no accuracy data in scenario)
> **How to validate:** Request a retrospective audit of a sample of Tom's classifications against Amelia's judgement in the discovery call.

> **Assumption [A4]:** The baseline for "% of counteroffers returned within 3 business days" is estimated as below 50%, inferred from the 4–6 business day average turnaround. If turnaround averages 4–6 days, the majority of contracts are not completing within 3 days.
> **Why it matters:** This metric is the primary CRO-facing indicator; setting the baseline too high would make the target appear trivially achievable.
> **If wrong:** If a significant fraction of contracts (e.g., simple NDAs) already complete in <3 days and the average is dragged up by complex cases, the target of ≥80% within 3 days may already be partially met, and the metric should be refined to track the tail (e.g., "% completed within 3 days for WS2+WS3 contracts").
> **Confidence:** Low (no distribution data in scenario; only average turnaround stated)
> **How to validate:** Ask Amelia for a breakdown of turnaround time by contract type/tier in discovery.
