# Scenario Context — MedFlex: Clinical Workforce Staffing Coordination

> *Source: `Scenario/scenario.md` (baseline) + discovery session transcript `Input/Mid-week_coach_peer checkpoint.docx` (updates labelled DS-*). This file is the single-source-of-truth scenario summary for use across all prompt templates.*

---

## 0b. Table of Contents

- [1. File header](#1-file-header)
- [2. The company](#2-the-company)
- [3. The team](#3-the-team)
- [4. The process](#4-the-process)
- [5. The work streams](#5-the-work-streams)
- [6. Tooling](#6-tooling)
- [8. Assumption log](#8-assumption-log)

---

## 1. File header

**MedFlex — Clinical Workforce Staffing Coordination**

> *Source: `Scenario/scenario.md` (baseline) + discovery session transcript (DS-* updates). This file is the single-source-of-truth scenario summary for use across all prompt templates.*

---

## 2. The company

**MedFlex** is a healthcare staffing agency with 200 employees, operating across a 5-state US region. Its business model is dual-sided: B2B with hospital systems (selling temporary clinical workforce placement) and B2C with travel nurses (providing shift opportunities).

**Revenue and growth target [DS-confirmed]:** Current revenue ~$14M. Board target: $200M within 24 months following the recently closed Series B. The engagement framing from CEO Marcus Reyes is "10x the business without 10x-ing the coordinators" within 8 weeks. The $14M → $200M target is a ~14× revenue growth requirement — confirmed in the discovery session.

---

## 3. The team

The process under assessment is owned by the staffing coordination function.

- **8 coordinators** — manually match nurses to shifts; individual names, roles beyond "coordinator," and tenure are not stated in the scenario. Coordinators carry high tacit knowledge about nurse preferences, facility quirks, and matching heuristics. This knowledge is not documented and represents a training cost and key-person risk [DS-confirmed].
- **Compliance / legal team [DS-confirmed]:** A separate team (distinct from coordinators) owns credential verification, licence checks, background checks, and training certifications. Coordinators do not perform this work — they read credential status from nurse profiles in ServiceNow. The compliance team updates those profiles. See Section 4 (WS3 correction) and corrected A5.
- **Marcus Reyes** — CEO; background in operations and growth, not engineering; recently closed Series B; characterised as confident, time-pressured, and results-oriented; cuts off rambling questions; respects FDEs who challenge framing with substance.

No other named individuals are stated in the scenario. Coordinator names, tenure, and individual experience levels are not provided.

---

## 4. The process

**Core process:** Clinical shift matching and confirmation — coordinating the placement of nurses into hospital shifts. Credential verification is a separate upstream process owned by the compliance/legal team, not part of the coordinator workflow.

**Volume:** ~120 shift-matching decisions per coordinator per day. (8 coordinators × ~120 = ~960 decisions per day — derived total, not a figure stated directly in the scenario.)

**Turnaround:**
- Current average time-to-fill: 4.2 hours
- Target time-to-fill: under 1 hour

**Performance indicators (stated):**
- Mismatch rate: 7% — **dual cause [DS-confirmed]:** (1) actual credential-to-request mismatch (nurse lacks required credential for the facility type); (2) hospital selects a nurse based on reputation or prior feedback rather than strict qualification match — the "match" fails the facility's preference criteria, not a regulatory credential check. The second cause is a market-dynamics failure, not an automation target. The split between the two causes is not quantified.
- No-show rate: 12%

**Intake channels:** Hospitals submit shift requests via email, portal, or phone. No dominant channel by volume is stated in the scenario baseline. **[DS-confirmed]** Shift requests arrive as **unstructured free text** within ServiceNow — coordinators read, parse, and act on natural-language requests. There is no structured intake form or machine-readable schema at the point of receipt.

**Competitive market dynamic [DS-confirmed]:** Hospitals submit shift requests to **multiple staffing agencies simultaneously**. The agency that submits a qualified nurse first wins the placement. Speed-to-first-submission is therefore the primary competitive differentiator — a coordinator who takes 4 hours to match and confirm loses the placement to a competitor who responds in 1 hour. This reframes the 4.2-hour → 1-hour target: it is not just an efficiency goal, it is a competitive survival requirement.

**Matching criteria (stated):** Credentials, proximity, availability, hospital preferences, nurse preferences — all applied manually by coordinators.

**Nurse database [DS-confirmed]:** The structured data required for matching (nurse profiles, credentials, availability, hospital preferences, nurse preferences, qualification requirements) is stored in a **structured database** — not free text, not spreadsheets. Marcus Reyes confirmed explicitly: "It's a database" when asked whether data was in spreadsheets or well-organized databases (transcript ~16:01). The database contains separate entities: nurse profile, nurse availability, hospital request/slot, and qualification requirements — "everything need to be matched" sits there, separately structured. This is distinct from the free-text intake channel (hospital shift requests arrive as unstructured text; nurse matching data is structured).

**Nurse onboarding [DS-confirmed]:** Before a nurse is available for matching, they go through an onboarding process: qualifications are shared, credentials are verified, and a profile is created in the database. This is a separate process owned by the compliance/legal team, not coordinators. Nurses can also be **offboarded from the database** — Marcus confirmed that nurses who no-show repeatedly can be removed from the roster (transcript ~37:07).

**Tacit knowledge qualification [DS-confirmed]:** The structured matching parameters (credentials, availability, proximity, hospital/nurse preferences) ARE captured in the database. What is not captured is the **judgment layer** coordinators apply on top of that structured data — facility-specific quirks, nurse relationship history, soft preferences not encoded in the profile, and heuristics built through years of experience. This is what varies across the 8 coordinators and creates training risk. The database gives the facts; experienced coordinators know what to do with edge cases the data does not resolve.

**Nurse availability [DS-confirmed]:** Nurses manage their own availability. This is not reported as a pain point; the availability signal exists and is accessible to coordinators.

**Confirmation model [DS-confirmed]:** Confirmation is **passive**. When a coordinator submits a nurse to a shift, the nurse receives an SMS or email notification. Silence is treated as acceptance — the nurse must actively call in to reject. This creates ambiguity: a nurse who did not see the notification is indistinguishable from one who accepted. This is a known contributor to the 12% no-show rate [assumption — see A3 update].

**Notification timing [DS-confirmed]:** Shift notifications are typically sent 2–3 days in advance of the shift. This window defines the available time for active confirmation loops and re-fill attempts.

**24-hour cancellation rule [DS-confirmed]:** Nurses must notify MedFlex within 24 hours of the shift if they cannot attend. Cancellations outside this window trigger the no-show process.

**No-show discovery [DS-confirmed]:** No-shows are discovered exclusively via hospital call — MedFlex has no proactive detection mechanism. A hospital calls MedFlex when the nurse does not appear. This means the no-show is discovered at or after shift start, not before — the window for remediation is effectively zero.

**Multi-submission behaviour [DS-confirmed]:** Coordinators submit the same nurse to multiple facilities or shifts simultaneously to increase fill probability. Upon receiving a confirmation from one facility, the coordinator manually withdraws the nurse from the remaining open submissions. If multiple facilities confirm the same nurse simultaneously (before withdrawal is processed), MedFlex must withdraw from the later confirmations and apologise to the affected facility. The downstream cost (facility relationship friction, coordinator rework) is not quantified but was raised as a concern in the discovery session [see A11].

**Tacit knowledge / training cost [DS-confirmed]:** Coordinator knowledge of nurse preferences, facility requirements, and matching heuristics is not documented. New coordinator ramp-up is slow. Marcus Reyes cited this as a concern — growth to $200M requires either dramatically more coordinators or externalising this knowledge into a system.

**Exception flag — nurse profile notes [DS-confirmed]:** Coordinator matching is largely rule-based unless a nurse profile contains specific notes. When notes are present (e.g., facility-specific restrictions, prior incidents, preferences), the coordinator must apply additional judgement. The presence of profile notes is the trigger for elevated human review at the matching step.

**Prior AI failures [DS-confirmed]:** Two prior failed projects:
1. **Chatbot (hospital-facing):** Rejected by hospital staff. Root cause confirmed in discovery: the chatbot did not integrate with hospital workflows and required hospitals to change their behaviour.
2. **Recommendation engine (coordinator-facing):** Nobody used it. Root cause confirmed in discovery: recommendations were not explainable — coordinators could not trust or verify them, so they ignored the output and continued working manually. A secondary contributing factor [DS-confirmed]: coordinators perceived the tool as a threat to their job security — if the system could replace their matching judgement, their role was at risk. This is a critical adoption constraint for any future agent design [see A13].

**Compliance verification — SCOPE CORRECTION [DS-confirmed]:** Credential verification (licence, background checks, training certifications) is performed by a **separate compliance/legal team**, not by coordinators. Coordinators read a pre-verified credential status from the nurse's profile in ServiceNow. The compliance team is responsible for keeping those profiles current. Credential latency (how quickly renewals appear in the system) was flagged in D0C as a risk — discovery session indicates this is managed by the compliance team and is **not a coordinator pain point**.

**Hard rules:**

> Note: HR-1 and HR-2 remain valid as process-level hard rules. Ownership is now corrected — credential verification is owned by the compliance team, not coordinators. HR-3 (state-aware credential logic) is owned by the compliance team. HR-4 (DNR lists) is a matching-level check that coordinators perform before generating shift offers. HR-5 (rest periods) remains an assumption.

| # | Rule | Basis | Actual owner | Assumption ref |
|---|------|-------|--------------|----------------|
| HR-1 | Credential verification (license, background, training certifications) must be completed before a placement is confirmed | Stated as a process step in the scenario; treated as a prerequisite, not optional | **Compliance/legal team** [DS-corrected] | A6 |
| HR-2 | Nurse credentials must match the required specialty and facility type | Implied by the scenario tracking mismatch rate as a KPI; a tracked failure mode implies an enforced rule | **Compliance/legal team + coordinator gate** [DS-corrected] | A7 |
| HR-3 | Placement state must be a first-class parameter in credential logic; 5-state operation means licence validity and scope of practice vary by state | Implied by 5-state geography and reliance on "state regulatory databases" (plural) | **Compliance/legal team** [DS-corrected] | A8 |
| HR-4 | Facility-specific Do Not Return (DNR) lists must be checked before a shift offer is generated | Standard contractual requirement in healthcare staffing; not explicitly stated in the scenario | Coordinator (at matching step) / MedFlex operations (assumed) | A9 |
| HR-5 | Mandatory rest periods between shifts must be enforced; a shift offer cannot be sent to a nurse who would violate minimum rest-interval rules | Governed by FLSA and state wage law; not stated in scenario | Federal / state labour law (assumed) | A10 |

---

## 5. The work streams

| # | Work stream | Volume / day | Time / case | Coordinator-owned? |
|---|-------------|--------------|-------------|-------------------|
| WS1 | Shift request intake (unstructured free text) | Not stated | Not stated | Yes |
| WS2 | Nurse-to-shift matching | ~120 decisions / coordinator / day (~960 total — derived) | Not stated per-case; composite avg time-to-fill: 4.2 hrs | Yes |
| WS3 | Compliance / credential verification | Not stated | Not stated | **No — separate compliance/legal team [DS-corrected]** |
| WS4 | Placement confirmation and coordination (passive model) | Not stated | Not stated | Yes |

**WS1 [DS-updated]:** Hospitals submit shift requests via email, portal, or phone. Requests arrive as **unstructured free text** in ServiceNow. Coordinator reads, interprets, and queues the request for matching. No structured intake schema exists at receipt.

**WS2:** Coordinator manually matches nurses to open shifts by querying the nurse database for matching parameters (credentials, availability, proximity, hospital preferences, nurse preferences — all structured, stored separately). The structured data is available; the coordinator's role is to interpret it, apply judgment on edge cases, and select the best match. This is the primary volume driver at ~120 decisions per coordinator per day. The judgment layer (facility quirks, soft preferences, heuristics) is undocumented and varies across coordinators [DS-confirmed]. Multi-submission (same nurse to multiple facilities) is a common coping strategy [DS-confirmed].

**WS3 [DS-corrected]:** Credential verification is performed by the **compliance/legal team**, not coordinators. Coordinators read a pre-verified credential status from nurse profiles in ServiceNow. This work stream is **out of scope for coordinator automation** — any agentic capability targeting credential verification must interface with the compliance team's process, not replace coordinator work. Re-scoped: coordinator involvement in WS3 is limited to reading and applying credential status, not verifying it.

**WS4 [DS-updated]:** Coordinator confirms placement with hospital and nurse. Confirmation uses a **passive model**: nurse receives SMS/email; silence = acceptance; nurse must call to reject. The 12% no-show rate is likely partially attributable to this model — nurses who did not see or act on the notification are treated as confirmed [assumption A3-updated]. Multi-submission race conditions contribute additional risk at this stage.

---

## 6. Tooling

- **ServiceNow [DS-confirmed]:** Central system of record for MedFlex. Shift requests are received as **free text** in ServiceNow (unstructured intake). Nurse profiles (including pre-verified credential status) are maintained in ServiceNow by the compliance team. Coordinators use ServiceNow as their primary working surface. Specific API capabilities, module configuration, and integration maturity are not stated — treat as assumptions in subsequent deliverables.
- **Nurse database [DS-confirmed]:** A structured database holds all matching-relevant nurse data: nurse profiles, credentials, availability, and qualification requirements. Hospital request data (slot, requirements) is stored as separate structured entities. Marcus confirmed this is a "database" (not spreadsheets or free text) when directly asked. This structured data is the query surface coordinators use for matching — it is distinct from the free-text intake channel. Whether this database is a ServiceNow module or a separate system connected to ServiceNow is **not stated** in the scenario or transcript — treat as an assumption requiring follow-up. The nurse database grows through onboarding (new nurses) and shrinks through offboarding (repeated no-shows or policy violations).
- **Email** — shift request intake channel from hospitals (also surfaces in ServiceNow)
- **Portal** — shift request intake channel (type and vendor not named in scenario)
- **Phone** — shift request intake channel from hospitals; implied for nurse outreach
- **SMS / email notifications [DS-confirmed]** — passive confirmation channel to nurses
- **State regulatory databases** — used by the compliance/legal team for manual compliance verification; specific databases not named; coordinator access not confirmed

> **Named systems note:** ServiceNow is now a confirmed named system [DS-confirmed]. A structured nurse database (containing profiles, credentials, availability, qualification requirements) is confirmed [DS-confirmed] but its technical identity is not — it may be a ServiceNow module or a separate connected system; this must be treated as an assumption. Email, portal, phone (as intake channels), SMS/email (as confirmation channels), and state regulatory databases (as a compliance verification source category) are also confirmed. No specific ATS, credential management system, or nurse scheduling platform is named beyond ServiceNow. Any additional system introduced in subsequent deliverables must be labelled as an assumption. Specific ServiceNow API capabilities, rate limits, and integration maturity are assumptions and must be labelled as such.

---

## 8. Assumption log

> **Assumption [A1]:** The ~960 total daily shift-matching decisions (8 coordinators × ~120) assumes all 8 coordinators are active on shift matching. The scenario states ~120 per coordinator but does not confirm whether all 8 are dedicated to matching or have additional responsibilities.
> **Why it matters:** Total throughput is the basis for the ROI case; if effective coordinator count on matching is lower, total daily volume is lower.
> **If wrong:** If fewer than 8 coordinators handle matching, total daily volume is lower and the throughput argument for automation weakens proportionally.
> **Confidence:** Medium.

> **Assumption [A2]:** The 4.2-hour average time-to-fill is a composite metric across all shift types and urgency levels. The scenario does not state whether this includes after-hours, same-day emergency, or planned fills, or whether it is segmented by any dimension.
> **Why it matters:** If time-to-fill varies significantly by shift type, the 1-hour target may be achievable for planned fills but not for complex or emergency cases — shaping which work streams are automatable in v1.
> **If wrong:** If 4.2 hours is already a segmented metric for a specific shift type, the automation target and success metric are more precisely bounded.
> **Confidence:** Medium.

> **Assumption [A3] [DS-updated]:** The 12% no-show rate has two confirmed root causes, not one: (1) **Notification-failure no-shows** — nurses who did not see or consciously act on the passive SMS/email confirmation and were logged as accepted; these are accidental, driven by the passive confirmation model design. (2) **Wage-competition no-shows** — nurses who accepted a MedFlex placement but subsequently took a higher-paying shift at another hospital and did not appear; these are deliberate, driven by competitive market dynamics in travel nursing. The split between the two causes is not quantified in the scenario or discovery session.
> **Why it matters:** The two causes require different interventions. Notification-failure no-shows are addressable by switching to an active confirmation model (explicit acknowledgement required). Wage-competition no-shows cannot be prevented by a confirmation loop — the nurse knowingly accepted and then left for better pay. For the wage-competition portion, the only agent-level mitigation is faster detection (monitoring pre-shift confirmation status) and faster replacement (triggering a re-fill before the shift window closes). Any no-show rate reduction target must be scoped to the addressable portion — overstating the impact of a confirmation loop redesign is a spec risk.
> **If wrong:** If wage competition is the dominant cause (say, >80% of no-shows), an active confirmation loop will move the metric only marginally — the primary lever becomes replacement speed, and the no-show rate target must be set accordingly.
> **Confidence:** Low-Medium (both causes confirmed in discovery; relative weighting not quantified).

> **Assumption [A4] [DS-updated]:** The 7% mismatch rate reflects placements that cleared MedFlex's internal process but failed at the facility due to credential mismatches — not errors detected and corrected internally before placement. Discovery session does not directly resolve this — the mismatch rate was not discussed in depth. Assumption stands.
> **Why it matters:** If mismatch is detected externally (facility-reported), the operational cost is a placement failure; if detected internally (rework before confirmation), the cost structure and agent design priority differ.
> **If wrong:** If the 7% includes internally caught errors, the credential-gate scope and success metric definition must be adjusted.
> **Confidence:** Low.

> **Assumption [A5] [DS-resolved — corrected]:** ~~Compliance verification is performed by the same 8 coordinators who do shift matching.~~ CORRECTED: Discovery session confirmed that credential verification is performed by a **separate compliance/legal team**, not coordinators. Coordinators only read pre-verified credential status from nurse profiles in ServiceNow. This resolves assumption A5 as a confirmed fact.
> **Why it matters:** The agent scope boundary between matching and credentialing is a handoff interface, not a within-role automation. Any capability targeting WS3 must be scoped as a compliance-team automation, not a coordinator automation.
> **Confidence:** High — confirmed in discovery session.

> **Assumption [A6] — supports HR-1 [DS-updated — ownership corrected]:** Credential verification is a hard prerequisite for placement confirmation, not a best-effort check that can be bypassed under time pressure. Owned by the compliance/legal team — the coordinator's role is to read status, not perform verification.
> **Why it matters:** The agent must respect the credential gate as a hard stop; it cannot generate placement offers for nurses with incomplete or expired credentials. Compliance team data quality in ServiceNow is now a critical dependency.
> **If wrong:** If the compliance team allows waivers, the agent must support a structured escalation and override flow.
> **Confidence:** High.

> **Assumption [A7] — supports HR-2 [DS-updated — ownership corrected]:** The 7% mismatch rate implies credential-to-facility-type matching is an enforced requirement. The compliance team maintains credential records; the coordinator (or agent) applies them at the matching step.
> **Why it matters:** The agent's credential gate logic depends on clean, up-to-date data in ServiceNow nurse profiles. If the compliance team's update cadence is slow, the gate is unreliable.
> **If wrong:** If mismatches are preference violations only (no regulatory consequence), the agent's credential gate can be advisory rather than blocking.
> **Confidence:** High.

> **Assumption [A8] — supports HR-3:** MedFlex's 5-state geography means nurse licence validity and scope of practice must be assessed against the state where the shift is located, not the nurse's home state. Owned by the compliance team. Coordinator (or agent) applies state-aware credential status read from ServiceNow.
> **Why it matters:** Placement state must be a first-class parameter in matching logic. Adds complexity to the data model and the matching gate.
> **If wrong:** If all 5 states are NLC participants and all nurses hold active compact licences, credential logic is simpler.
> **Confidence:** Medium.

> **Assumption [A9] — supports HR-4:** MedFlex's facility contracts include Do Not Return (DNR) provisions. Coordinators (or the agent) must check facility-specific DNR status before generating any shift offer.
> **Why it matters:** Offering a DNR nurse to a facility is a contract violation regardless of credential status. Hard exclusion.
> **If wrong:** If no DNR provisions exist, this check is unnecessary — reducing data requirements.
> **Confidence:** Medium.

> **Assumption [A10] — supports HR-5:** Federal FLSA and applicable state wage laws impose minimum rest periods between shifts. The agent must not offer a shift that would place a nurse in violation of their applicable rest-interval requirement.
> **Why it matters:** The agent needs shift history data per nurse and state-aware rest-interval rules.
> **If wrong:** If MedFlex operates only in states without strict scheduling laws and nurses are contractors not subject to FLSA rest rules, this check may not be legally required.
> **Confidence:** Medium.

> **Assumption [A11 — new, DS-sourced]:** Multi-submission (same nurse submitted to multiple facilities simultaneously) is a deliberate coordinator coping strategy, not a policy violation. It inflates apparent fill rate but creates double-booking risk and facility relationship friction.
> **Why it matters:** An agent that replicates multi-submission behaviour will inherit the race condition. An agent that prevents it may reduce fill rate in the short term. The correct agent behaviour (replicate, prevent, or flag) is an open design question.
> **If wrong:** If multi-submission is a policy violation that Marcus wants eliminated, the agent must enforce single-submission at the point of offer.
> **Confidence:** Medium — behaviour confirmed in discovery; policy status not explicitly addressed.

> **Assumption [A12 — new, DS-sourced]:** The revenue growth target ($14M → $200M in 24 months) implies the business model must scale at a rate that purely headcount-based growth cannot support. This is the underlying economic driver for automation — not cost reduction but revenue capacity.
> **Why it matters:** Success metrics for the engagement should include revenue capacity per coordinator, not just time-to-fill or fill rate reduction. An agent that reduces coordinator workload but does not unlock additional volume does not serve the board's target.
> **If wrong:** If the $200M target is achievable through geographic expansion or new contracts without volume automation, the urgency for coordinator workflow automation is lower.
> **Confidence:** High — confirmed directly by Marcus Reyes in discovery session.

> **Assumption [A13 — new, DS-sourced]:** Coordinator adoption of agentic tools is at risk due to job security concerns — not just usability. The failed recommendation engine was partly rejected because coordinators perceived it as threatening their role. An agent that is designed without a visible, valued human role risks the same fate regardless of technical quality.
> **Why it matters:** Agent design must preserve a meaningful coordinator role — at minimum, exception handling, escalation, and relationship management. The HITL model is not just a safety requirement; it is the adoption strategy. Framing the agent as a tool that amplifies coordinators (not replaces them) is a prerequisite for deployment success.
> **If wrong:** If Marcus is willing to override coordinator resistance and mandate adoption, the design constraint is removed — but the risk of sabotage, workarounds, and low-quality exception handling remains.
> **Confidence:** Medium-High — root cause of prior failure confirmed in discovery; current coordinator sentiment not directly measured.
