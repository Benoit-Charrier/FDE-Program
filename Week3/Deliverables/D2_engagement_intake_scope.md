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
