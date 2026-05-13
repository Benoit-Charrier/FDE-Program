# Deliverable D1 — Problem Framing & Success Metrics: MedFlex Clinical Workforce Staffing

*Source: `Scenario/scenario_context.md`, `Deliverables/D0C_discovery.md`. All numbers trace to scenario_context.md or are explicitly labelled as assumptions. DS-confirmed items reflect the mid-week discovery session with Marcus Reyes (CEO).*

---

## 0. Executive Summary

- **Core business problem:** At ~120 matching decisions per coordinator per day and a 4.2-hour average time-to-fill, MedFlex loses shift placements to faster competitors before a qualified nurse is ever submitted — the bottleneck is not data access (nurse matching data is in a structured database [DS-confirmed]) but the undocumented coordinator judgment layer and a passive confirmation model that produces a 12% no-show rate, both of which worsen linearly with volume.
- **Why the existing approach cannot scale:** The matching process depends on tacit, undocumented knowledge spread across 8 coordinators (8 different judgment approaches [DS-confirmed]) and a passive confirmation design where silence equals acceptance — neither can be solved by hiring more coordinators without directly contradicting the CEO's stated goal of reaching $200M revenue without proportional headcount growth.
- **The intervention:** A matching and confirmation orchestration agent that handles clean fills autonomously (structured credential and availability matching against the confirmed nurse database) and monitors shift confirmations proactively, targeting time-to-fill under 1 hour and no-show rate under 6%.

---

## 1. Table of Contents

- [0. Executive summary](#0-executive-summary)
- [1. Table of contents](#1-table-of-contents)
- [2a. Problem statement — lived experience today](#2a-problem-statement--lived-experience-today)
- [2b. What is actually broken — root cause diagnosis](#2b-what-is-actually-broken--root-cause-diagnosis)
- [3. "10x without 10x-ing" — decoded architectural requirements](#3-10x-without-10x-ing--decoded-architectural-requirements)
- [3b. Why an AI agent — not traditional software, not RPA, not a process change](#3b-why-an-ai-agent--not-traditional-software-not-rpa-not-a-process-change)
- [4. What success looks like — by stakeholder](#4-what-success-looks-like--by-stakeholder)
- [5. Assumption log](#5-assumption-log)

---

## 2a. Problem statement — lived experience today

**2a-i. MedFlex coordinators (the team doing the work)**

A coordinator's day is a continuous triage across 120+ decisions, each requiring a database query, a judgment call, and an outbound action — repeated without pause, in competition with other agencies responding to the same facility requests. The structured data exists (nurse profiles, credentials, availability [DS-confirmed]), but the edge cases — which nurse a facility actually prefers, which borderline-credential profile has been accepted before, which nurse is reliable enough for a short-notice shift — live only in coordinator memory, built over years. A newcomer coordinator is slower and makes worse calls than a veteran, not because the data isn't available but because the judgment layer takes time to build. At the same time, coordinators are managing a multi-submission race condition: the same nurse submitted to multiple facilities simultaneously, with manual withdrawal required on first confirmation, and relationship damage when two facilities confirm before withdrawal is processed. On top of this, a 12% no-show rate means roughly 115 failed placements every day — each one discovered by a hospital call at shift start, with no remediation window. The coordinator is the only detection mechanism, the only orchestration layer, and the only quality gate in a system operating at a volume that was not designed for.

**2a-ii. Hospitals (the facility customers)**

A hospital submitting a shift request to MedFlex simultaneously submits the same request to competing agencies — because experience has taught that no single agency can be relied on for speed [DS-confirmed]. From the facility's perspective, a 4.2-hour average response time [scenario] means paying a premium price for a relationship that routinely loses the race. When MedFlex does submit a nurse, 7% of the time the nurse does not meet the credential or preference requirements [scenario] — creating administrative burden, potential patient safety risk, and reputational erosion. When a nurse is confirmed but does not appear, the hospital discovers this only by calling MedFlex at or after shift start [DS-confirmed], with no advance warning and no replacement available. Each no-show is an unexpected staffing shortfall in a clinical environment where understaffing has direct patient care consequences. The hospital's experience is: slow on average, unreliable when it matters, and reactive when things go wrong.

**2a-iii. Nurses (the workers)**

A nurse working through MedFlex receives a shift notification via SMS or email and is expected to call in if they cannot attend — silence means accepted [DS-confirmed]. There is no explicit acknowledgement, no structured decline, and no confirmation that the nurse's record of what they agreed to matches what MedFlex logged. Notifications are sent 2–3 days in advance [DS-confirmed], which is workable for planned availability — but the 7% mismatch rate [scenario] means some nurses arrive at facilities for shifts that do not match their credentials or the facility's expectations, creating a wasted trip and a reputational incident. From the nurse's side, the process provides no confirmation receipt, no clear communication channel for questions before the shift, and no structured way to decline without making a phone call. In a market where nurses can and do take higher-paying competing offers [DS-confirmed], a process with this much friction and ambiguity — for a partner who cannot confirm faster than 4 hours — is not the preferred relationship. [assumption — D1-A1: nurse experience framed from scenario evidence; direct nurse satisfaction data not stated in scenario]

---

## 2b. What is actually broken — root cause diagnosis

> **Broken [B-1]:** The matching process is a non-codified human judgment bottleneck that scales only with headcount.
> **Symptom it produces:** 4.2-hour average time-to-fill against a 1-hour competitive requirement; lost placements to faster agencies; fill quality that varies by coordinator tenure; inability to grow placement volume without proportional coordinator hiring.
> **Why it persists:** The nurse database is structured and queryable [DS-confirmed], but facility preference data and matching heuristics are not — they live in coordinator heads, built through years of experience. Two prior AI attempts failed: the recommendation engine was rejected because coordinators could not verify its outputs and perceived it as a job threat [DS-confirmed]. The pattern is: data access is not the problem; trust in non-human judgment is.
> **What fixing it would unlock:** An agent that handles clean fills autonomously (credentials match, availability confirmed, no profile notes) would remove the majority of the 120/day volume from the coordinator's judgment queue, compressing time-to-fill for those cases to minutes rather than hours and freeing coordinator capacity for exception fills and relationship management.

> **Broken [B-2]:** The confirmation model produces no confirmation signal — it is a passive design that treats absence of response as consent.
> **Symptom it produces:** 12% no-show rate [scenario]; no-shows discovered exclusively by hospital call at or after shift start [DS-confirmed]; zero proactive detection window; zero re-fill capacity once the no-show is known.
> **Why it persists:** The passive model (SMS/email notification, silence = accepted) was the lowest-friction design at lower volume; requiring active acknowledgement from nurses imposes friction on a workforce that has competing offers. It has not been redesigned because each no-show is managed reactively as an individual incident rather than addressed as a structural design failure [assumption — D1-A2].
> **What fixing it would unlock:** An active confirmation loop — where the agent sends a structured confirmation request and monitors for explicit acknowledgement — would eliminate the notification-failure portion of the 12% no-show rate. Pre-shift status monitoring (agent flags unacknowledged placements X hours before shift start) would create a re-fill window that currently does not exist, converting a reactive crisis into a manageable exception.

> **Broken [B-3]:** Facility preference data is unstructured and locked in coordinator memory, making preference-based mismatch unpreventable by any automated system.
> **Symptom it produces:** A portion of the 7% mismatch rate [scenario] where nurses who meet hard credential requirements are rejected by facilities because of soft preference criteria (prior incidents, reputation, historical patterns) that are not in the database [DS-confirmed: 7% mismatch has dual causes — credential mismatch + hospital preference/reputation selection].
> **Why it persists:** Capturing facility preference data requires a deliberate data enrichment exercise that has never been prioritised; coordinators have compensated using memory, so the cost of the gap has been invisible until it produces a mismatch incident.
> **What fixing it would unlock:** Structured facility preference profiles would enable the agent to match on soft criteria, not just hard credentials — reducing the preference-based portion of the mismatch rate and enabling the agent to handle a larger share of fills autonomously without human review.

---

## 3. "10x without 10x-ing" — decoded architectural requirements

The CEO's framing is "10x the business without 10x-ing the coordinators" within 8 weeks, against a board-confirmed revenue target of $14M → $200M in 24 months [DS-confirmed]. That is a **~14× revenue growth** requirement. Translating this into numbers the architecture must satisfy:

**The capacity math:**

| Variable | Today | At $200M target |
|---|---|---|
| Annual revenue | $14M | $200M |
| Growth multiplier | — | ~14× |
| Coordinators | 8 | Tolerated max: ~16 (2× headcount growth [assumption D1-A10]) |
| Decisions/coordinator/day | 120 | Must increase substantially — see below |
| Total decisions/day (all coordinators) | ~960 | ~13,440 (14× volume [assumption D1-A11]) |
| Decisions that must be agent-handled | 0 | ~11,500/day (agent must absorb ~85% of volume for 2× headcount cap to hold) |

> **Assumption [D1-A10]:** "Without 10x-ing coordinators" is interpreted as a maximum of 2× headcount growth (8 → ≤16 coordinators). Marcus used "10x" rhetorically; the constraint is that headcount growth must be substantially sublinear relative to revenue growth, not that headcount is frozen. This interpretation gives the architecture a realistic coordinator capacity floor.
> **Confidence:** Medium — directional intent confirmed; specific headcount ceiling not stated.

> **Assumption [D1-A11]:** Revenue scales roughly proportionally with placement volume. At $14M with ~960 decisions/day, $200M implies ~13,440 decisions/day. This assumes revenue per placement is constant and that growth comes from volume, not from repricing.
> **Confidence:** Medium — revenue-per-placement data not in scenario; assumption may be tested in D7.

**Architectural requirements derived from the capacity math:**

| Requirement | Derived value | Rationale |
|---|---|---|
| **AR-1: Autonomous fill rate** | ≥85% of incoming shift requests resolved without coordinator decision | 16 coordinators × 120/day = 1,920 human decisions/day; remainder of 13,440 must be agent-handled |
| **AR-2: Agent concurrent decision throughput** | ≥28 decisions/minute sustained at peak (13,440/day ÷ 480 working minutes) | Agent must process requests as fast as they arrive; cannot queue behind a human response cycle |
| **AR-3: Time-to-first-submission (latency)** | <60 minutes from request arrival to qualified nurse submission sent to facility | Competitive survival requirement [DS-confirmed]; losing the race means losing the placement |
| **AR-4: HITL loop latency** | ≤15 minutes from agent escalation to coordinator acknowledgement | For exception fills that require human review, coordinator must respond within 15 minutes to keep total time-to-fill under 60 minutes |
| **AR-5: Clean-fill decision speed** | <2 minutes per autonomous decision (parse → query → score → submit) | 28 decisions/minute throughput at peak requires agent to resolve clean fills in sub-2-minute cycles |
| **AR-6: Pre-shift confirmation monitoring** | All active placements scanned ≥2 hours before shift start | No-show detection window currently zero [DS-confirmed]; 2-hour pre-shift window enables re-fill attempt |
| **AR-7: Per-coordinator output leverage** | Each coordinator's actions must produce ≥7× more confirmed placements than today | At 2× headcount (16 coordinators) handling 14× volume, per-coordinator leverage must be ~7×. Agent provides this by handling clean fills autonomously and routing only exceptions to the coordinator. |

**What these requirements rule out architecturally:**
- A single-agent serial pipeline cannot sustain 28 decisions/minute — requires concurrent, parallelised request handling
- A HITL design that requires coordinator approval on every decision cannot achieve <60-minute time-to-fill at scale — the agent must be authorised to submit clean fills without human pre-approval
- A system that processes intake sequentially (one request at a time) will queue behind volume at peak hours — intake parsing must be event-driven, not batch

---

## 3b. Why an AI agent — not traditional software, not RPA, not a process change

**Not hiring more coordinators:** The CEO's stated strategic goal is reaching $200M revenue without proportional headcount growth [DS-confirmed: "10x the business without 10x-ing the coordinators"]. Hiring is directly excluded as the scaling solution. It also does not address the passive confirmation model, the multi-submission race condition, or the tacit knowledge lock-in — it reproduces the same structural problems at higher cost.

**Not a new scheduling system or CRM:** MedFlex already has ServiceNow as its system of record and a structured nurse database [DS-confirmed]. The problem is not that data is inaccessible — it is that the matching judgment layer and the confirmation orchestration layer do not exist in any system. A new scheduling platform would still require a human to make the matching decision and would not change the passive confirmation design. Replacing ServiceNow would add integration risk and migration cost without addressing the root causes.

**Not RPA:** RPA can automate deterministic, rule-based sequences — reading a credential status from the nurse database is RPA-appropriate. But the bottleneck is not in the deterministic steps; it is in the judgment layer (which nurse to select when multiple candidates qualify, how to resolve edge cases) and in the adaptive confirmation loop (tracking acknowledgement status, re-routing unacknowledged placements, generating replacement workflows). These require reasoning about unstructured inputs, multi-step context across conversations, and real-time status monitoring — all beyond RPA's capability. Free-text intake parsing alone (all intake arrives as unstructured text [DS-confirmed]) is outside RPA scope.

**Not a process change alone:** A process redesign that mandates active nurse confirmation (phone call required, not SMS) would reduce no-shows but increase nurse friction and potentially hurt fill rates — and it does nothing for the WS2 matching bottleneck. A process change that requires coordinators to document their judgment heuristics would be slow and incomplete. Process changes that address one symptom in isolation do not address the structural throughput constraint at 120 decisions/coordinator/day. The required intervention is an orchestration layer that executes structured decisions at machine speed and routes exceptions to humans — which is the definition of an agent-led + HITL architecture.

**Why an agent is right for this specific problem:** The nurse matching problem has a large codifiable core (credentials, availability, proximity, hard rules) and a smaller judgment-dependent edge (facility preferences, exception handling). An agent can handle the codifiable core at scale and route the edge to humans — replicating the value of an experienced coordinator's structured query while preserving human oversight for the cases that require it. The confirmation orchestration problem is deterministic end-to-end (send → monitor → flag → re-route) and is a fit for agent-led execution without judgment requirements. Both problems are high-volume, the data infrastructure is confirmed as queryable [DS-confirmed], and both have clear HITL handoff points that address the adoption risk from prior failures.

---

## 4. What success looks like — by stakeholder

### 4a. Success for MedFlex

| Metric | Baseline (from scenario) | Target | How measured | Timeframe |
|--------|--------------------------|--------|--------------|-----------|
| Average time-to-fill | 4.2 hours [scenario] | <1 hour | Timestamp delta: request entry in ServiceNow → confirmed placement notification sent | 6 months post-deployment |
| Coordinator throughput | ~120 decisions/coordinator/day [scenario] | 240 decisions/coordinator/day [assumption — D1-A3] | Total confirmed placements / active coordinator-days, from ServiceNow placement records | 6 months post-deployment |
| No-show rate | 12% [scenario] | <6% [assumption — D1-A4: notification-failure portion is addressable; wage-competition portion is not] | (No-shows reported by hospitals / total confirmed placements) × 100, tracked monthly | 6 months post-deployment |
| Mismatch rate | 7% [scenario] | <3% [assumption — D1-A5] | (Facility-reported mismatches / total placements submitted) × 100, tracked monthly | 6 months post-deployment |
| Revenue capacity per 8-coordinator team | $14M/year run-rate [scenario] | Supports $200M trajectory [scenario board target] | Placement volume per coordinator per quarter, correlated to revenue | 24 months |

### 4b. Success for the hospitals

| Metric | Baseline (from scenario or assumption) | Target | How measured | Timeframe |
|--------|----------------------------------------|--------|--------------|-----------|
| Response time to shift request | 4.2 hours avg [scenario] | <1 hour | Time from hospital request submission to first qualified nurse submission confirmation received by facility | 6 months post-deployment |
| Credential mismatch rate | 7% [scenario] | <2% | Facility-reported credential or preference mismatches / total placements submitted, collected via post-placement facility confirmation | 6 months post-deployment |
| No-show rate at shift start | 12% [scenario] | <6% | Hospital-reported no-shows / total confirmed placements, reported monthly | 6 months post-deployment |
| Proactive pre-shift notification of potential no-show | 0% (all no-shows discovered by hospital call at shift start [DS-confirmed]) | >75% of unresolved placement risks flagged to facility >2 hours before shift start [assumption — D1-A6] | Count of proactive MedFlex alerts to facility / count of eventual no-shows, tracked by ServiceNow confirmation status log | 6 months post-deployment |

### 4c. Success for the nurses

| Metric | Baseline (from scenario or assumption) | Target | How measured | Timeframe |
|--------|----------------------------------------|--------|--------------|-----------|
| Time from shift opening to offer received | Unknown; inferred as proportional to 4.2h coordinator fill time [assumption — D1-A7] | <1 hour from request pickup to nurse notification | Timestamp delta: coordinator assignment → outbound nurse notification, from ServiceNow and communication log | 6 months post-deployment |
| Explicit confirmation rate | 0% — all confirmations are passive (silence = accepted [DS-confirmed]) | >90% of accepted placements carry an explicit nurse acknowledgement | Count of explicit acknowledge responses / total placement notifications sent, tracked via confirmation loop system | 6 months post-deployment |
| Shift information accuracy at point of arrival | 7% mismatch rate [scenario; nurse experiences same placement failures as facilities] | <2% | Nurse-reported shift discrepancies (wrong unit, rate, credential requirement) / total placements fulfilled, collected via post-shift feedback [assumption — D1-A8: feedback collection mechanism does not currently exist] | 6 months post-deployment |
| Last-minute MedFlex-initiated cancellations after nurse accepted | Unknown baseline [assumption — D1-A9] | <1% of confirmed placements cancelled by MedFlex within 24 hours of shift start | Count of MedFlex-side cancellations within 24h window / total confirmed placements, from ServiceNow records | 6 months post-deployment |

---

## 5. Assumption Log

> **Assumption [D1-A1]:** Nurse experience of the placement process (friction, communication quality, accuracy) is inferred from the scenario's structural evidence (passive confirmation model, 7% mismatch rate, 2–3 day notification window). Direct nurse satisfaction survey data or nurse-reported pain points are not stated in the scenario.
> **Why it matters:** Nurse success metrics in Section 4c must be validated through direct discovery with nurses or nurse-facing staff before being used as engagement KPIs. Using inferred baselines as contractual targets creates measurement risk.
> **If wrong:** If nurses are largely satisfied with the current process and the 12% no-show rate is predominantly wage-competition-driven (not notification-failure), the nurse-experience success metrics may not be the right adoption signal — coordinator adoption metrics become more important.
> **Confidence:** Medium.

> **Assumption [D1-A2]:** The passive confirmation model (silence = accepted) has not been redesigned because each no-show has been managed as an individual incident rather than recognised as a structural design failure. There is no stated evidence that MedFlex has previously attempted an active confirmation model and abandoned it.
> **Why it matters:** If a previous active confirmation attempt was tried and failed (e.g., nurses stopped responding entirely), there may be a nurse-behavior constraint that makes active confirmation design harder than assumed. This would change the WS4 agent design.
> **If wrong:** If nurse behaviour under an active confirmation model is unknown because the model has never been tested, the 6% no-show target may be achievable with a well-designed active loop — or it may be harder if wage-competition no-shows dominate.
> **Confidence:** Medium.

> **Assumption [D1-A3]:** With an agent handling clean fills autonomously, coordinator throughput can approximately double to 240 decisions/coordinator/day (from 120), as coordinators redirect time from routine database queries and outbound offer workflows to exception handling, relationship management, and oversight of agent outputs.
> **Why it matters:** Coordinator throughput is the mechanism by which $200M revenue becomes achievable without headcount growth. If the throughput multiplier is lower (e.g., 1.5x rather than 2x), the revenue case weakens and the headcount equation changes.
> **If wrong:** If clean fills are a minority of volume (below 40%), the throughput gain from automating them is smaller; the agent must handle exceptions earlier than planned for the throughput target to be met.
> **Confidence:** Low — this is a derived estimate, not a scenario-stated figure. Depends on the clean-fill percentage [D0C: U-2] and the HITL overhead per agent-assisted decision.

> **Assumption [D1-A4]:** The 12% no-show rate has two equal root causes: notification-failure (passive model) and wage competition. Targeting <6% is achievable by eliminating the notification-failure portion; the wage-competition portion (assumed ~6%) is not addressable by a confirmation loop redesign.
> **Why it matters:** The 6% target sets expectations for both MedFlex and hospital stakeholders. If the wage-competition portion is larger than 50%, the 6% target is unachievable through confirmation loop redesign alone — requiring a different intervention (pre-shift engagement, commitment incentives) or a revised target.
> **If wrong:** If wage competition is the dominant cause (>80% of no-shows), an active confirmation loop moves the metric by only 20% of 12% = <2.5 percentage points — and the target must be reset to approximately 10%.
> **Confidence:** Low-Medium — both causes are confirmed in discovery [DS-confirmed: scenario_context A3]; the split is not quantified.

> **Assumption [D1-A5]:** The 7% mismatch rate is reducible to <3% by enforcing the hard credential gate in the matching agent and completing a facility preference profile enrichment project. The residual 3% reflects preference-based mismatches that require structured facility profiles not yet available.
> **Why it matters:** The mismatch rate target is a quality and safety commitment to facilities. If the preference-based portion is larger than assumed, the agent's credential gate alone will not reach the target — facility profile enrichment must be scoped and resourced as a prerequisite.
> **If wrong:** If the entire 7% is hard credential mismatch (no preference-based component), the <3% target may be achievable without facility profile enrichment — a faster and simpler path to the target.
> **Confidence:** Medium — dual cause of mismatch is DS-confirmed; quantitative split is not stated.

> **Assumption [D1-A6]:** A proactive pre-shift notification to the facility (>75% of potential no-shows flagged >2 hours before shift start) is technically achievable via an active confirmation loop that monitors placement acknowledgement status and escalates unacknowledged placements before the shift window. The 2-hour threshold is selected to give the facility time to seek an alternative.
> **Why it matters:** This is the primary hospital-facing quality improvement — shifting the hospital experience from reactive discovery to proactive notification. If the agent cannot reliably detect unacknowledged placements early enough (e.g., because the nurse database does not capture confirmation timestamps), the proactive notification capability is not buildable in v1.
> **If wrong:** If nurses frequently acknowledge placements only in the final hours before a shift, a 2-hour threshold may not provide sufficient detection lead time and a longer window must be used — reducing the addressable portion of no-shows in the monitoring window.
> **Confidence:** Medium.

> **Assumption [D1-A7]:** Nurse notification timing is driven by the coordinator's fill cycle — a nurse typically receives their shift offer near the end of the 4.2-hour fill window, meaning advance notification is 2–3 days minus 4.2 hours of coordinator processing. With an agent compressing fill time to <1 hour, nurse advance notification effectively increases for the same request timing.
> **Why it matters:** Faster fills mean nurses get more lead time, which may improve acceptance rates and reduce wage-competition no-shows (nurses who have not yet committed to another shift are less likely to switch). This is a secondary benefit of the time-to-fill target.
> **If wrong:** If coordinators routinely batch shift offers at the end of the day regardless of when requests arrive, fill time compression does not improve nurse lead time.
> **Confidence:** Low — inferred from process structure; not stated in scenario.

> **Assumption [D1-A8]:** No nurse-facing feedback collection mechanism currently exists at MedFlex. Post-shift nurse feedback (on shift accuracy, communication quality, experience) is not captured systematically.
> **Why it matters:** Nurse success metrics in Section 4c require a feedback collection mechanism to measure. If this mechanism must be built, it is an additional scope item — not just an agentic capability but a data collection system.
> **If wrong:** If a feedback mechanism exists (e.g., post-shift SMS survey), nurse experience metrics can be baselined immediately and the 4c targets can be set against real data rather than assumptions.
> **Confidence:** Medium — no such mechanism is described in scenario_context.md; absence of mention implies absence.

> **Assumption [D1-A9]:** MedFlex-initiated cancellations (where MedFlex cancels a nurse's confirmed placement before the shift start) are rare but create significant nurse relationship damage — a nurse who has arranged childcare, transportation, or declined other work for a shift that MedFlex cancels is a churn risk. The baseline is unknown; the target of <1% is set as a table-stakes quality floor.
> **Why it matters:** If MedFlex-initiated cancellations are currently above 5%, the agent's multi-submission withdrawal logic (which eliminates double-bookings) will directly improve this metric — making it a trackable agent impact measure, not just a quality floor.
> **If wrong:** If MedFlex-initiated cancellations are already below 1% due to current coordinator discipline, this metric provides no differentiation signal for the agent's impact.
> **Confidence:** Low — not stated in scenario; included because it is a standard nurse-experience quality indicator in this domain.

----------------------------------------

# Deliverable D2 — Engagement Intake & Scope: MedFlex Clinical Workforce Staffing

*Source: `Scenario/scenario_context.md`, `Deliverables/D2A_cognitive_load_map.md`, `Deliverables/D2B_delegation_suitability_matrix.md`, `Deliverables/D2C_volume_value_analysis.md`, `Deliverables/D1_problem_framing.md`. All claims trace to scenario_context.md or are labelled as assumptions.*

---

## 0. Executive Summary

- **Why now:** The Series B has closed and Marcus Reyes is operating against a board-committed $200M revenue target within 24 months — ~14× growth [DS-confirmed] — at which point the manual matching process (8 coordinators, 120 decisions/day, 4.2-hour average fill) cannot sustain the volume; the 8-week CEO timeline is the signal that proof-of-concept must be visible before the growth ramp begins, not a full-system delivery deadline.
- **MVP scope:** The agent extracts structured matching briefs from free-text shift requests (WS1 NLP) and executes credential-compliant candidate queries against the nurse database, routing the shortlist to a coordinator for final selection (WS2); facility heuristics, exception fills, nurse renegotiation, credential verification, and confirmation automation (WS4, RPA — separate workstream) remain outside the AI MVP scope.
- **Critical risk:** Coordinator adoption — the prior recommendation engine failed because its outputs were unexplainable and coordinators perceived it as a job threat [DS-confirmed: A13]; the WS2 matching agent has the identical adoption vector and will fail quietly if the HITL design does not make coordinator judgment visible and valued from day one.

---

## 1. Table of Contents

- [0. Executive summary](#0-executive-summary)
- [1. Table of contents](#1-table-of-contents)
- [2. Business context](#2-business-context)
- [3. Stakeholder map](#3-stakeholder-map)
- [4. Constraints](#4-constraints)
  - [4a. Hard constraints](#4a-hard-constraints)
  - [4b. Soft constraints](#4b-soft-constraints)
- [5. Risk register](#5-risk-register)
- [6. MVP scope](#6-mvp-scope)
  - [6d. Wave sequencing](#6d-wave-sequencing)
  - [6a. In scope](#6a-in-scope)
  - [6b. Out of scope](#6b-out-of-scope)
  - [6c. MVP success condition](#6c-mvp-success-condition)
- [7. Assumption log](#7-assumption-log)

---

## 2. Business context

MedFlex's engagement context is shaped by three facts that D1's problem statement does not address. First, a Series B has just closed and Marcus Reyes is delivering against a board-committed $200M revenue target — this is not an internal efficiency initiative. The 8-week framing ("within 8 weeks") is the CEO signalling that he expects something observable in the near term: a live capability, a measurable metric, a pilot with real data. It is not a build-and-deploy deadline for a matching agent of this complexity. FDEs who respond by scoping a 6-month enterprise rollout will be cut. The scope must produce a measurable result at 8 weeks and frame the WS2 matching agent as the follow-on wave.

Second, two prior AI projects have already failed at MedFlex [DS-confirmed]. The chatbot failed because hospitals had to change their behaviour to use it — the integration requirement was on the wrong side. The recommendation engine failed because coordinators could not verify its outputs and perceived it as a threat to their roles. These are not ancient history; they are active organisational memory and the context within which this engagement is being evaluated. "AI at MedFlex" already has a connotation of wasted investment. The design must visibly differ from the recommendation engine in the specific dimension that killed it: explainability of outputs and preservation of human judgment in the selection step.

Third, the 8-week timeline creates acute scope discipline pressure that is political as much as technical. Every scope item that cannot produce a visible result inside 8 weeks is exposed to cancellation. The facility preference enrichment project, the nurse database API validation, and the coordinator HITL interface design each have dependencies that may not resolve in 8 weeks. The Wave 1 deliverable (WS4 active confirmation + WS1 NLP extraction in shadow mode) is the scope that is achievable and demonstrable within the window. WS2 matching is the 12-week follow-on — but must be framed to Marcus as the primary business-value wave that Wave 1 enables, not a deferral.

---

## 3. Stakeholder map

| Name / Role | What they need from this engagement | What they are worried about | Influence on success |
|-------------|-------------------------------------|-----------------------------|----------------------|
| **Marcus Reyes — CEO** | Observable proof in ≤8 weeks that the agent accelerates placement volume and that $200M is achievable without proportional hiring; a clear link between the agent's output and the revenue trajectory | A third failed AI project; a roadmap deck instead of a live result; engagement drift from the competitive speed target | High |
| **8 Coordinators — Staffing coordination team** | Tools that reduce the routine database query load without removing their judgment or their role from the placement process; a HITL interface that respects their expertise | That the agent replaces them; that they will be blamed when agent-recommended placements fail; that their tacit knowledge becomes irrelevant or is used to train a system that makes them redundant | **High — the engagement fails silently if they route around the agent** |
| **Compliance / legal team** | Assurance that every agent-generated submission has passed the credential gate (HR-1, HR-2, HR-3) and that no placement reaches a facility through the agent without a valid, current credential check | That a speed-optimised matching agent will treat their maintained credential data as optional and produce a patient safety or regulatory incident | Medium — blocks deployment if credential gate is not verifiably enforced |
| **Hospital relationship owner** [assumed role — see A-D2-2] | Faster response times, fewer no-shows, fewer mismatches; no change to how hospitals currently submit requests | That MedFlex's new tool will require hospitals to change their intake format or workflow (the prior chatbot failure was caused by exactly this) | Medium — hospital satisfaction drives revenue and contract renewal; relationship damage is the biggest downstream consequence of a failed deployment |
| **Nurse-facing relationship contact** [assumed role — see A-D2-3] | An active confirmation model that nurses find less ambiguous than the current passive design; fewer last-minute surprises about shift details | That the confirmation loop adds friction (required acknowledgement step) and reduces nurse acceptance rates, increasing the operational burden on coordinators | Low-Medium — nurse adoption of the active confirmation loop is a prerequisite for WS4 to reduce the no-show rate |

**At-risk stakeholder:** The 8 coordinators are the stakeholder most likely to cause the engagement to fail quietly — not visibly, not loudly, but through invisible workaround. The engagement's primary value metrics (time-to-fill, throughput, no-show rate) all require coordinators to actually route their work through the agent. The prior recommendation engine failed this exact way: technically deployed, coordinators continued working manually, the metric never moved. The risk is not open resistance, which Marcus can override. It is the slow reversion to manual querying alongside superficial use of the agent interface — a failure mode that looks like compliance and shows no signal until the 3-month review reveals no metric improvement. The HITL design must make coordinator judgment genuinely visible and recorded (agent presents, coordinator selects, coordinator's decision is logged), not cosmetically involved.

---

## 4. Constraints

### 4a. Hard constraints

> **Constraint [C-1]:** The engagement must produce an observable, measurable result within 8 weeks.
> **Source:** Marcus Reyes directly stated — "within 8 weeks" [scenario]
> **Agent design implication:** Wave 1 scope (WS4 active confirmation rule-based automation + WS1 NLP extraction in shadow mode) must be deployable and producing measurable output — no-show rate movement or extraction accuracy report — by week 8. WS2 matching agent enters Wave 2 and cannot be the 8-week deliverable; any plan that requires WS2 to go live inside 8 weeks is scope-unsafe.

> **Constraint [C-2]:** The credential gate (HR-1, HR-2, HR-3) must fire as a hard stop on every placement submission; the agent cannot surface or submit a nurse whose credential status does not pass the hard credential check in the nurse database.
> **Source:** Scenario [HR-1, HR-2, HR-3]; compliance team ownership DS-confirmed
> **Agent design implication:** Credential check is not a warning, advisory flag, or coordinator-bypassable soft gate. It is a blocking condition in the agent's shortlist generation step. The compliance team's credential database must be designated as the authoritative source and a data freshness SLA agreed before Wave 2 WS2 deployment, as a stale credential record that the agent passes is a patient safety event that cannot be attributed to the agent's logic.

> **Constraint [C-3]:** Nurse database API access must be validated before WS2 agent development begins.
> **Source:** Nurse database existence confirmed [DS-confirmed]; API capabilities, endpoints, and rate limits are not stated in the scenario or transcript [D0C: U-6]
> **Agent design implication:** WS2 cannot enter development until the database integration contract is confirmed. This is a Wave 2 blocker, not a parallel workstream. API design decisions — pagination, filtering capability, real-time vs. batch query, credential field schema — shape the entire matching pipeline architecture and cannot be assumed away.

> **Constraint [C-4]:** The agent must produce explainable, verifiable outputs; coordinators must be able to see and verify the basis for each matching decision without taking the agent's word.
> **Source:** Prior recommendation engine failure — root cause was inability to verify outputs [DS-confirmed: A13]
> **Agent design implication:** Every shortlist output must include the explicit credential basis for each candidate's inclusion (credential name, expiry, state match, HR-rule applied). Black-box scoring or unexplained rankings are architecturally excluded. The coordinator must be able to verify the agent's reasoning in under 60 seconds — this is a UX specification constraint, not a post-launch enhancement.

> **Constraint [C-5]:** WS3 (credential verification) is owned by the compliance team and is out of coordinator agent scope.
> **Source:** DS-confirmed scope correction — credential verification is performed by the compliance/legal team [scenario_context.md §4, WS3 correction]
> **Agent design implication:** The matching agent reads credential status (a query against the nurse database); it does not perform, replicate, or accelerate credential verification. Any credential gap discovered during matching must be routed to the compliance team via a defined escalation path. Automating the compliance team's verification workflow is a separate engagement requiring a separate discovery process.

### 4b. Soft constraints

- Marcus Reyes has low patience for over-qualified answers and rambling; the engagement lead must defend scope decisions with specific numbers and clean trade-offs [scenario: characterisation]. Prepare two-sentence answers to "why isn't this live in 8 weeks."
- Coordinators' tacit knowledge of facility preferences and nurse reliability is not in any system and cannot be accessed by the agent without a structured enrichment project that is outside 8-week scope [D2A: A2A3, A2A6]. The agent will not match on soft preferences in Wave 2 Phase 1; coordinators provide that judgment via HITL selection.
- No structured facility preference profiles exist [D0C: U-3]; WS1-JtD-3 (hard/soft credential ambiguity resolution) will remain HITL until profiles are built — this is a deliberate design choice, not a gap.
- The 5-state geography means credential logic must be state-aware (HR-3); agent rules are more complex than a single-state operation.
- Nurses are independent contractors in a competitive market; the active confirmation loop must be explicitly low-friction for nurses (single acknowledgement tap, clear shift details, not a form); friction that reduces acceptance rates is worse than the current passive model.
- MedFlex has no nurse feedback collection mechanism [D1: D1-A8]; nurse experience metrics cannot be baselined before deployment. Post-shift survey capability is an optional Wave 2 addition, not a Wave 1 dependency.

---

## 5. Risk register

> **Risk [R-1]:** Coordinators work around the agent — using the agent's output interface superficially while continuing to verify and select candidates manually, preserving their existing workflow rather than offloading it.
> **Category:** Adoption
> **Likelihood:** High — same root cause as the prior recommendation engine failure [DS-confirmed: A13]; coordinator perception that their role is threatened is confirmed, not resolved; the adoption vector is identical
> **Impact if it occurs:** Agent deployment produces no metric movement (time-to-fill and throughput unchanged); engagement fails to demonstrate ROI on coordinator capacity; Marcus loses confidence and the engagement is at risk of cancellation as a third failed AI project
> **Mitigation:** HITL-first phased deployment with transparent recording — in Wave 2 Phase 1, every coordinator action on an agent shortlist is logged; coordinators see that the agent provides credential verification and candidate retrieval (not their judgment), and they own the final selection; frame the agent as a tool that handles the database query so the coordinator can focus on the placement decision; measure and share coordinator agreement rate with agent's top-ranked candidate as a trust-building signal, not a performance metric

> **Risk [R-2]:** The nurse database contains stale credential records — a nurse whose real-world credential has expired is still flagged as valid because the compliance team's update cadence is slower than the agent's query interval.
> **Category:** Data
> **Likelihood:** Medium — compliance team update cadence is not stated and is an open unknown [D0C: U-1]; flagged as a prerequisite dependency before Wave 2
> **Impact if it occurs:** Agent submits a nurse whose credential appears valid in the database but has lapsed in reality — a patient safety event and a regulatory compliance violation; MedFlex's liability; HR-1 is violated by a data quality failure attributed to the agent's clearance decision
> **Mitigation:** Agree a data freshness SLA with the compliance team before Wave 2 WS2 deployment (maximum credential record age at time of query); add a staleness flag in the shortlist output (credential last updated >N days ago = HITL trigger, not just pass/fail); compliance team to confirm update cadence in Wave 2 prerequisites before agent is authorised to generate autonomous submissions

> **Risk [R-3]:** WS1 NLP extraction misclassifies specialty requirements at a rate that exceeds the current coordinator error rate, producing wrong matching briefs faster than the manual process.
> **Category:** Technical
> **Likelihood:** Medium — MedFlex's specialty lexicon is not documented [D2A: A-WS1-2]; NLP extraction on unstructured free text is sensitive to terminology coverage; cascade error path from WS1 to WS2 amplifies any extraction errors [D2A: Cross-stream Obs 1]
> **Impact if it occurs:** High-speed wrong answers: a higher volume of incorrectly specified briefs reaches WS2, increasing the mismatch rate rather than decreasing it; the agent is demonstrably worse than the manual baseline on the most visible quality metric
> **Mitigation:** Deploy WS1 in shadow mode before cutting over — agent runs extraction alongside coordinator extraction for 2 weeks; comparison is produced and reviewed; hard gate: WS1 must achieve ≥95% extraction accuracy on a validation set before WS2 autonomous querying begins; specialty taxonomy must be documented as a Wave 1 prerequisite before NLP prompting is calibrated

> **Risk [R-4]:** The 8-week timeline is interpreted by Marcus as full WS2 matching agent deployment in production — creating pressure to skip data validation and HITL design that are prerequisites for safe operation.
> **Category:** Timeline
> **Likelihood:** Medium — Marcus's phrasing is ambiguous; his time-pressure characterisation and prior AI project context suggest he may equate "8 weeks" with "live and replacing coordinator effort"
> **Impact if it occurs:** WS2 deployed before WS1 extraction quality is validated (cascade error path at full speed); WS2 deployed without coordinator trust-building phase (coordinators bypass agent); same failure mode as the recommendation engine, at production speed
> **Mitigation:** Define and align the 8-week deliverable explicitly with Marcus before development begins: 8 weeks = WS4 confirmation loop live + WS1 shadow mode running + WS2 integration spec and architecture reviewed and approved by MedFlex; frame WS4's measurable no-show rate improvement as the 8-week proof point; frame WS2 as the 12-week follow-on that delivers the $200M capacity case

> **Risk [R-5]:** Facility preference data is unavailable and the preference-based portion of the mismatch rate is unaddressable by the MVP agent, but the combined 7% mismatch rate is presented as the engagement's quality metric — creating an expectation gap.
> **Category:** Data
> **Likelihood:** High — absence of structured facility preference profiles is confirmed and cannot be resolved within Wave 1 or Wave 2 [D0C: U-3]; this is a current gap, not a future risk
> **Impact if it occurs:** Agent achieves credential mismatch reduction (hard gate enforced) but preference-based mismatches persist; facility-reported mismatch rate improves to ~4% rather than the D1 target of <3%; Marcus questions whether the agent is delivering the promised quality improvement
> **Mitigation:** Separate the mismatch rate into two trackable sub-metrics from day 1: (1) credential mismatch rate — agent-addressable, target <2% in 6 months; (2) preference-based mismatch rate — data-gap dependent, target TBD after facility profile enrichment project is scoped and resourced; anchor the MVP success condition to the credential mismatch sub-metric only; present the preference-based gap as a named follow-on project, not an agent limitation

---

## 6. MVP scope

### 6d. Wave sequencing

Three sequential phases with explicit deployment states and gates between them.

| Phase | Timing | WS1 | WS2 | Gate to next phase |
|-------|--------|-----|-----|--------------------|
| **Wave 1** | Weeks 1–8 | **Intake & Matching Agent — shadow mode**: extracts briefs in parallel with coordinator; output not fed to WS2 | Intake & Matching Agent development begins; spec and architecture approved; not deployed | WS1 achieves ≥95% extraction accuracy on validation set |
| **Wave 2 Phase 1** | ~Week 12 | **Intake & Matching Agent — live**: cuts over from shadow; feeds structured briefs to WS2 query | **Intake & Matching Agent — HITL mode**: generates ranked shortlist with credential citations → coordinator selects → agent submits on coordinator approval | Coordinator agreement rate ≥85% on agent top-ranked candidate + zero HR-1 violations over 4 consecutive weeks |
| **Wave 2 Phase 2** | Post-Phase 1 gate | Intake & Matching Agent — live | **Intake & Matching Agent — autonomous**: clean-fill submissions without coordinator pre-approval | — |

**Shadow mode (WS1):** Agent runs extraction in parallel with the coordinator; outputs are compared to validate accuracy. Agent does not feed WS2 until the validation gate is passed. Estimated shadow window: 2–4 weeks.

**HITL mode (WS2 Phase 1):** Agent generates a ranked shortlist of 2–5 qualified candidates with per-candidate credential citations. Coordinator reviews, selects, and approves before any submission is executed. No autonomous action in this phase.

**Separate workstream (not AI MVP):** WS4 active confirmation loop is rule-based automation (RPA) — no LLM reasoning required; delivered independently and does not gate or depend on WS1/WS2. See §6b.

**Never in scope (any phase):** Exception fill orchestration (WS2-JtD-3), standalone credential verification (WS3), hospital-facing intake, nurse renegotiation, facility preference enrichment. See §6b for exclusion rationale.

---

### 6a. In scope

- **WS1 — Shift request intake NLP extraction:** Classify inbound ServiceNow free-text messages as new shift request / modification / cancellation / other (WS1-JtD-1). Extract structured matching brief: specialty, credential level, shift datetime, unit type, facility location, urgency classification (WS1-JtD-2, WS1-JtD-4). Flag specialty ambiguities (hard vs. soft credential requirement) to coordinator HITL queue — agent does not apply a default; ambiguity is explicitly surfaced (WS1-JtD-3). Output a validated structured brief to the WS2 matching queue. Observable test: a brief either completes with all required fields populated, or it surfaces to the HITL queue with the specific ambiguity identified.
- **Coordinator HITL queue:** A single coordinator review interface that surfaces ambiguity flags from WS1 (hard/soft credential classification pending decision) and shortlist review requests from WS2 (candidate selection pending coordinator approval) — one view, per-item acknowledgement action, time-to-fill clock visible. Observable test: coordinator can resolve an ambiguity flag and return a resolved brief to the WS2 queue without leaving the interface.
- **WS2 — Candidate pool query and shortlist generation:** Query nurse database on credential match (HR-1, HR-2, HR-3), DNR exclusion (HR-4), availability, and proximity (WS2-JtD-2). Produce a ranked shortlist of 2–5 qualified candidates with explicit credential basis for each inclusion (credential name, expiry, state match, rules applied). Route shortlist to coordinator HITL queue for final candidate selection — coordinator approves before submission in Wave 2 Phase 1. Observable test: every shortlist includes per-candidate credential citations; no candidate appears on a shortlist who has a current HR-1/HR-2/HR-3 failure in the nurse database.
- **WS2 — Multi-submission tracking and withdrawal orchestration:** Log open submission per nurse per facility in ServiceNow (WS2-JtD-5). Monitor real-time submission statuses. On first confirmation received, automatically execute withdrawal from all other open submissions for that nurse. Flag simultaneous confirmation to coordinator for race condition resolution (WS2-JtD-6). Observable test: agent processes a simulated simultaneous confirmation without manual coordinator intervention on the withdrawal step.
- **Wave 1 shared infrastructure (prerequisite to Wave 2 WS2):** ServiceNow read/write connector, SMS/email notification gateway integration, placement status schema (confirms or creates the multi-submission status field), coordinator HITL queue — all built in Wave 1, reused in Wave 2.

### 6b. Out of scope

| What is excluded | Why it is excluded | When it could be added |
|------------------|--------------------|------------------------|
| Active confirmation loop and pre-shift monitoring (WS4-JtD-1, WS4-JtD-2) | Rule-based automation (RPA), not AI — confirmation dispatch and acknowledgement monitoring are deterministic, templated, event-triggered workflows; no LLM reasoning required at any step; including RPA in an AI MVP conflates two distinct delivery tracks and obscures what the engagement is demonstrating | Separate RPA / workflow automation workstream — can be scoped, built, and delivered independently; does not gate on WS1 or WS2 completing first |
| Facility preference profile enrichment | No structured facility preference data exists — every known facility heuristic is in coordinator memory, not in any system [D0C: U-3]; building profiles requires a dedicated data collection project (interview-based extraction, historical pattern mining) that cannot complete in the 8-week window | Phase 3 — after 6+ months of agent deployment generates structured signal on which coordinator overrides consistently reflect facility preferences; use override patterns to bootstrap profile construction |
| Exception fill orchestration — no suitable candidate found (WS2-JtD-4) | Exception fills require facility relationship negotiation (lower-credential candidate with facility approval, region-override candidates, unfillable escalation) that depends on facility-specific context not yet in any structured system; agent handling of exception fills without this data creates facility relationship risk; WS2-JtD-4 is Human Only in D2B | Phase 3 — after facility preference profiles are built and the agent has established a trust record on clean fills; agent can begin surfacing exception options only once coordinators trust its clean-fill judgment |
| Nurse renegotiation handling (WS4-JtD-3 — nurse withdraws or renegotiates post-acceptance) | Renegotiation involves rate approval authority, nurse relationship history, and alternative candidate lookup under time pressure — all requiring coordinator judgment; no structured rate approval workflow or renegotiation authority parameter is confirmed in the scenario [D2A: A2A5] | Post-Phase 2 once rate approval parameters are defined and documented and the agent has stable candidate lookup capability from WS2 |
| Standalone credential verification (WS3) | Credential verification is owned by the compliance/legal team, not coordinators — this work stream is explicitly out of coordinator automation scope [DS-confirmed]; automating it would require a separate engagement with the compliance team and their existing workflow tools | Separate engagement with the compliance/legal team if requested; out of scope for the coordinator-facing agent entirely |
| Hospital-facing intake automation | The prior chatbot failed specifically because it required hospitals to change their intake behavior [DS-confirmed]; until the coordinator-side process is stable and producing consistent output, adding a hospital-facing interface layer creates the same integration risk — hospitals submit via their existing channels; agent processes what arrives | Post-Phase 2 if hospital relationship owners request it and MedFlex's internal process has demonstrated 3+ months of stable output quality |
| Autonomous clean-fill submission without coordinator approval | In Wave 2 Phase 1, all agent shortlists require coordinator selection before submission — no autonomous submissions; the adoption constraint from prior recommendation engine failure [A13] means coordinators must experience the agent as a tool that amplifies their judgment before the autonomous submission step is activated | Wave 2 Phase 2 — after 4-week Phase 1 HITL deployment shows coordinator agreement rate ≥85% on agent top-ranked candidates and zero HR-1 violations in agent-generated shortlists |

### 6c. MVP success condition

The MVP is successful when, in the 30-day period beginning from Wave 2 Phase 1 go-live: (1) ≥70% of new shift requests processed through the WS1 NLP pipeline produce a complete structured matching brief that reaches the WS2 candidate query within 5 minutes of ServiceNow receipt, reducing WS1's contribution to the time-to-fill pipeline below 10 minutes for standard requests — supporting D1 AR-3 (<60 min time-to-first-submission); AND (2) zero HR-1 credential compliance failures are recorded in agent-generated shortlists for the duration of the 30-day window — establishing the compliance safety record required before autonomous submission (no coordinator pre-approval) is activated in Wave 2 Phase 2.

---

## 7. Assumption log

> **Assumption [A-D2-1]:** The 8-week deadline is interpreted as an observable, measurable MVP result — not full WS2 matching agent deployment in production. The 8-week deliverable is: WS4 confirmation loop live and reducing no-show detection time; WS1 NLP extraction in shadow mode and producing comparison data; WS2 integration spec and architecture reviewed and approved. WS2 autonomous matching goes live in Wave 2 (week 12+).
> **Why it matters:** If Marcus interprets 8 weeks as WS2 in production, scope must be renegotiated immediately — WS2 cannot be safely deployed without WS1 extraction validation (cascade error risk) and the coordinator trust-building phase (adoption risk).
> **If wrong:** If Marcus accepts trajectory evidence (pilot metrics, shadow mode results) rather than full production deployment, the MVP success condition is achievable within the 8-week window with the Wave 1 scope.
> **Confidence:** Medium — Marcus's characterisation (results-oriented, low patience) is stated [scenario]; specific definition of "8 weeks" is open.

> **Assumption [A-D2-2]:** No dedicated hospital relationship owner role exists at MedFlex — hospital account management is embedded in the coordinator function, not a separate named role. This is the assumed role in the stakeholder map; stakeholder is "Hospital relationship owner [assumed role]."
> **Why it matters:** If a dedicated hospital relationship owner exists, they must be consulted on the WS4 confirmation message design and on the WS1 extraction quality metrics — their account management priorities may differ from Marcus's throughput focus and should not be ignored.
> **If wrong:** If the coordinator team fully owns all hospital relationship work, no additional stakeholder management workstream is required for the WS4 confirmation loop design.
> **Confidence:** Medium — consistent with a 200-person agency without separately named relationship roles in the scenario; standard healthcare staffing structure may include a recruiter/account management split.

> **Assumption [A-D2-3]:** A nurse-facing relationship contact exists in some form — whether an onboarding recruiter, a nurse liaison within the coordinator team, or a compliance team member — but is not named in the scenario. This is the assumed role in the stakeholder map; stakeholder is "Nurse-facing relationship contact [assumed role]."
> **Why it matters:** The WS4 active confirmation loop is a nurse-facing communication model change. The person responsible for nurse relationships must review and approve the confirmation message design, acknowledgement deadline, and decline mechanism — or nurse acceptance rates risk dropping if the design adds friction without adding clarity.
> **If wrong:** If nurses are fully self-service (no relationship owner; all communication via portal/SMS) and acceptance rates are not managed through a dedicated contact, the confirmation loop design can be validated through pilot testing with a nurse cohort rather than stakeholder sign-off.
> **Confidence:** Low — role not named; standard healthcare staffing includes a recruiter or nurse liaison function.

> **Assumption [A-D2-4]:** ServiceNow API capabilities — specific endpoints, read/write permissions, module configuration, rate limits, and webhook/event-trigger availability — are sufficient to support the Wave 1 integrations (confirmation status field, structured brief write-back, HITL queue notifications). The specific API has not been validated [D0C: U-6].
> **Why it matters:** If ServiceNow API capabilities are more limited than assumed (e.g., read-only access in the coordinator module; rate limits preventing real-time status monitoring), Wave 1 integration scope must be redesigned and the timeline for Wave 2 slides. This is the most operationally material unknown for the 8-week delivery constraint.
> **If wrong:** If the API provides event-driven webhooks for placement status changes, the Wave 1 confirmation monitoring loop is simpler and the real-time withdrawal orchestration in WS2 is more reliable.
> **Confidence:** Low — ServiceNow confirmed as the working surface [DS-confirmed]; specific API capabilities are an open unknown [D0C: U-6].

> **Assumption [A-D2-5]:** The multi-submission placement status field in ServiceNow — tracking which facilities a given nurse has been submitted to simultaneously — does not currently exist as a queryable, real-time field; it is maintained manually by coordinators [D2A: A2A4]. Creating or confirming this field is a Wave 1 prerequisite for both WS4 monitoring and WS2 withdrawal orchestration.
> **Why it matters:** If this field does not exist, both WS4-JtD-2 (pre-shift monitoring via placement status) and WS2-JtD-6 (withdrawal orchestration on first confirmation) require a ServiceNow data schema change before the agent can be built. This is not an integration question but a data model prerequisite.
> **If wrong:** If ServiceNow already tracks multi-submission status per nurse in real time, the Wave 1 prerequisite is already met and the integration build is simpler.
> **Confidence:** Low — multi-submission behaviour is confirmed [DS-confirmed]; the system representation of it is not stated in the scenario or transcript.

--------------------------------------------------------------------

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
| WS1-JtD-2: Parameter extraction from unstructured request | Human-led + Agent Support | Partial (HITL) | Intake & Matching Agent | D2B 1/7: despite low score, LLM extraction from free text is the minimum required capability — no script or RPA alternative exists for unstructured intake [DS-confirmed]; agent drafts brief, coordinator validates hard/soft interpretation before brief enters WS2 |
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
A single Intake & Matching Agent handles WS1 extraction, WS2 matching, and WS3 credential check as sequential tool calls within one context window.

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

**Status:** Proposed

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
