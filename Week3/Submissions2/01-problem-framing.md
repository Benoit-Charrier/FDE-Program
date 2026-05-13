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
