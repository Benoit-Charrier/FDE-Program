# Greenfield Health Systems — Healthcare Claims Processing

*Full artefacts and background in `Scenario/scenario_enriched.md` and `Scenario/scenario.md`. This file is the single-source-of-truth scenario summary for use across all prompt templates.*

---

## 0b. Table of Contents

- [1. File header](#1-file-header)
- [2. The company](#2-the-company)
- [3. The team](#3-the-team)
- [4. The process](#4-the-process)
- [5. The work streams](#5-the-work-streams)
- [6. Tooling](#6-tooling)
- [7. Key artefacts](#7-key-artefacts)
- [8. Assumption log](#8-assumption-log)

---

## 1. File header

**Greenfield Health Systems — Medical Claims Adjudication**

*Full artefacts and background in `Scenario/scenario_enriched.md` and `Scenario/scenario.md`. This file is the single-source-of-truth scenario summary for use across all prompt templates.*

---

## 2. The company

**Greenfield Health Systems** is a health insurance payer that adjudicates medical claims submitted by healthcare providers on behalf of its plan members. Business model: health plan/payer operations — the company processes provider-submitted claims, determines coverage and medical necessity, and issues payment or denial decisions. No revenue, ARR, or market segment is explicitly stated in the scenario. No geographic information is stated.

---

## 3. The team

**Claims processing team — 45 processors total.**

Named stakeholders (executives, not processors):

- **Sarah Chen** — CFO. Primary KPI: cost reduction; FTE savings improve margin. Owns the financial case and headcount plan. Budget authority: $400K allocated for AI agent implementation.
- **Dr. Marcus Webb** — Chief Medical Officer (CMO). Clinical decisions are his domain. Non-negotiable position: physician or advanced practice provider must review every claim with clinical implications before finalisation; CMO team will not certify a system that bypasses clinical review.
- **James Liu** — VP Operations. Facing contractual SLA penalties from payers for claims exceeding 7 days. Primary driver: speed; needs claims cleared below the penalty threshold.

> **Note:** The Slack exchange (Exchange 3) includes one message attributed to "James Chen" — this appears to be a scenario inconsistency; based on context the speaker is James Liu.

No named individuals are given for the processor team. Generic roles implied: claims processors (adjudication), clinical reviewers (medical necessity), coding specialists (not explicitly named but implied by coding validation step).

---

## 4. The process

**Core process:** Medical claims adjudication — receipt through payment or denial.

**Volume:** ~50,000 claims per month (stated in `scenario_enriched.md`); 2,000 claims/day (stated in `scenario.md`).

> *Inconsistency: scenario.md states 2,000 claims/day; Sarah Chen states "We have 1,667 claims/day" directly in Exchange 3. Both are stated figures in the scenario — neither is derived here. The two numbers are not reconciled in the source material. For conservatism, 2,000/day is used as the planning number unless a deliverable depends on the distinction, in which case both figures are presented.*

**Current average processing time:** 35 minutes per claim (scenario.md).
**Current cycle time (end-to-end):** 8 days average (scenario_enriched.md); currently running 9+ days per VP Operations (Exchange 3).
**Current auto-adjudication rate:** 22% (industry benchmark: 85%) (scenario.md).
**Current denial appeal overturn rate:** 41% — described in scenario as "indicating first-pass errors" (scenario.md).
**Current error rate:** ~1.2% (scenario_enriched.md).

**SLA constraint:** Payers impose contractual penalties for claims exceeding 7 days. VP Operations is currently absorbing penalty costs. This is a hard deadline owned by **James Liu / VP Operations**.

**Compliance constraint:** CMO **Dr. Marcus Webb** holds a non-negotiable requirement: no claim with clinical content may be denied or finalised without physician or advanced practice provider review. CMO team will not certify any system that bypasses clinical review. This is a hard delegation stop owned by **Dr. Marcus Webb / CMO**.

**Budget:** $400K allocated for AI agent implementation (owned by **Sarah Chen / CFO**). Financial case requires headcount reduction to pencil out.

**Negotiated routing split (from stakeholder exchanges):**
- **65% of claims** — administrative path (billing, coding, prior auth completeness): agent-approved, no physician required.
- **35% of claims** — clinical path (claims with genuine clinical content): physician review required; agent pre-screens and routes with pre-filled context.

> *This split is a stakeholder-negotiated figure from Exchange 3, not a measured baseline. Dr. Webb's estimate: "Maybe 30–35% of claims have genuine clinical content." Treated as a design target, not a confirmed empirical fact.*

**Headcount targets (from stakeholder exchanges):**
- CFO target: 40% reduction in claims review staff = 8 FTEs over 6 months (Exchange 1).
- James Liu's resolution calculation: reduce claims review staff from 20 to 7, retaining clinical oversight (Exchange 3).

> *Inconsistency flagged: The CFO email states "40% reduction = 8 FTEs," implying a review staff of 20. James Liu's Slack message proposes "20 to 7" = 13 FTE reduction, which exceeds 40% of 20. These figures are not reconciled in the scenario. The 20-person review staff figure is consistent across both references. The reduction target (8 FTEs vs. 13 FTEs) is inconsistent and is flagged as an assumption requiring clarification.*

**Physician throughput with agent pre-screening:** ~20 claims per hour (Dr. Marcus Webb, Exchange 3). Without pre-screening: current manual review is included in the 35 min/claim average.

**Cycle time targets (from Exchange 3):**
- Administrative (agent-approved) path: 4–5 days.
- Clinical (physician review) path: 6–7 days.
- Both targets clear the 7-day SLA penalty threshold.

**Claim formats accepted:** EDI 837, PDFs, portal submissions (scenario.md).

**Required steps per claim (scenario.md):** eligibility verification, coding validation, medical necessity review, payment determination.

---

## 5. The Work Streams

The scenario does not label discrete work streams by name. The following two work streams are derived from the negotiated routing split in the stakeholder exchanges and the four required processing steps in scenario.md.

| # | Work stream | Volume/day | Time/case |
|---|-------------|------------|-----------|
| WS1 | Administrative adjudication (eligibility, coding validation, prior auth completeness, payment determination — no clinical content) | ~1,300 claims/day (65% × 2,000) | Not stated separately; included in 35 min/claim overall average |
| WS2 | Clinical review (claims with clinical content — agent pre-screens, physician reviews and finalises) | ~700 claims/day (35% × 2,000) | ~3 min/claim with agent pre-screening (derived: 20 claims/hour ÷ 60 min = 3 min; stated by Dr. Webb in Exchange 3) |

> **Volume derivation note:** WS1 and WS2 volumes are derived from the 65%/35% split applied to the 2,000 claims/day figure. Neither volume is stated directly in the scenario. The 3 min/claim for WS2 is derived from Dr. Webb's "20 claims/hour" with pre-screening; this is a target state figure, not a current state figure. The overall 35 min/claim is the current state across all claim types.

- **WS1:** Agent-led administrative adjudication — format validation, eligibility verification, coding accuracy checks, prior auth completeness, and payment determination for claims with no clinical content. Decision output: auto-approve with audit record, or reject with specific failure code returned to provider.
- **WS2:** Physician-reviewed clinical adjudication — agent classifies claim as containing clinical content, generates a pre-filled review packet (diagnosis codes, prior auth history, clinical notes summary), routes to physician HITL queue. Physician makes the final determination. Decision output: approve, deny, or request additional information.

---

## 6. Tooling

No specific systems are named in the scenario source files (`scenario.md` and `scenario_enriched.md`).

> **Named systems note:** No systems are explicitly named in the scenario. All tooling references in subsequent deliverables are assumptions and must be labelled as such. Specific claims management platforms, clearinghouses, eligibility databases, prior authorisation systems, and coding validation tools are not confirmed in the scenario. Any system named in a deliverable must be identified as an assumption with a confidence level and validation method.

---

## 7. Key Artefacts

**Artefact 1 — CFO email to CMO re: Claims Processing Automation — Headcount Plan (2026-04-08):**
Sarah Chen proposes a 40% headcount reduction (8 FTEs over 6 months) as non-negotiable for the financial case, asserting the agent should handle ~70% of claims. The email reveals that the financial case is driven by a board-level margin pressure and that headcount transition planning has already been initiated with HR — the CFO is treating the headcount reduction as committed before the architecture is designed.

**Artefact 2 — CMO reply to CFO (2026-04-08):**
Dr. Marcus Webb draws a clear delegation boundary: agent handles administrative checks (eligibility, prior auth completeness, coding accuracy); a physician reviews every claim with clinical implications before finalisation. He explicitly states his team will not certify a system that bypasses clinical review, and no claim can be denied without CMO approval. This is the hardest constraint in the scenario — it is non-negotiable and compliance-linked.

**Artefact 3 — Slack exchange: Operations, CFO, CMO (undated, follows 2026-04-08 emails):**
James Liu escalates the SLA crisis (claims at 9+ days, penalties live) and forces a resolution conversation. The exchange produces the key design outcome: Dr. Webb estimates 30–35% of claims have genuine clinical content; James Liu calculates that a 35%/65% split would reduce review staff from 20 to 7 while preserving clinical oversight; Sarah Chen conditionally accepts pending a written definition of "clinical flagging" criteria; James Liu establishes cycle time targets (4–5 days admin, 6–7 days clinical). This exchange is the primary source for the delegation architecture and the headcount model.

---

## 8. Assumption Log

> **Assumption [A-1]:** 2,000 claims/day is used as the operative planning volume. Both 2,000/day (scenario.md) and 1,667/day (Sarah Chen, Exchange 3) are stated directly in the scenario and are not reconciled. Neither is designated as the canonical figure.
> **Why it matters:** Volume is the denominator for all economic calculations (headcount savings, processing time delta, token cost model). The 17% difference between the two figures affects ROI, payback period, and staffing model materially.
> **If wrong:** If the true daily volume is 1,667, all volume-dependent metrics scale down proportionally. This must be confirmed before the token economics model is finalised.
> **Confidence:** Medium — both figures are stated in the scenario; the discrepancy is unresolved.

> **Assumption [A-2]:** The 35%/65% clinical/administrative split is a design target based on Dr. Webb's estimate, not a measured baseline from claims data.
> **Why it matters:** If the true clinical content rate is higher than 35%, physician review volume exceeds what the HITL queue can absorb at the throughput Dr. Webb cited (20 claims/hour), and the cycle time targets are not achievable without additional clinical reviewers.
> **If wrong:** A higher clinical rate (e.g., 50%) requires either more physician capacity or a more precise classifier to push the boundary lower. The economic model changes significantly.
> **Confidence:** Low — Dr. Webb's language was "honestly? maybe 30–35%" — an estimate, not a measurement.

> **Assumption [A-3]:** The "reduce staff from 20 to 7" figure in Exchange 3 refers to claims review staff specifically (the subset of the 45-person team), not the total team headcount.
> **Why it matters:** Total headcount reduction is the primary economic metric. If "20" is the full relevant team, the reduction is 13 FTEs. If "45" is the full team and "20" is a subset, different roles are affected.
> **If wrong:** If the reduction target applies to a different subset, the headcount savings model and payback period calculation change.
> **Confidence:** Medium — the CFO email says "40% of claims review staff = 8 FTEs" implying a 20-person review team; the "20 to 7" in the Slack is consistent with that denominator but the reduction magnitude differs (8 vs. 13 FTEs). The inconsistency is unresolved in the scenario.

> **Assumption [A-4]:** "Clinical content" — the classification criterion that determines routing — is not formally defined in the scenario. The design must produce this definition as a spec artifact.
> **Why it matters:** The clinical content classifier cannot be built without a precise definition of what constitutes "clinical content." Sarah Chen explicitly requested this in Exchange 3: "Draft the requirements for what 'clinical flagging' means." This is an open design question, not a resolved scenario fact.
> **If wrong:** N/A — this is a gap, not an assumption. The definition must be produced in the capability spec.
> **Confidence:** N/A — flagged as a required design output.

> **Assumption [A-5]:** The 35-minute average processing time applies to the current state across all claim types. Post-automation, administrative claims will process faster (agent execution) and clinical claims will process at ~3 min physician review time (Dr. Webb's estimate with pre-screening). The 35-minute figure is not decomposed by claim type in the scenario.
> **Why it matters:** The token economics model requires a current-state baseline cost per claim. If the 35-minute average is skewed by clinical claims taking much longer and administrative claims taking much less, the per-type economics differ from a flat average.
> **If wrong:** If administrative claims currently take less than 35 minutes, the time-savings delta for WS1 automation is smaller than the flat average implies.
> **Confidence:** Low — the scenario provides only the overall average; no per-type breakdown is given.
