# Deliverable D0D — Discovery Questions for Marcus Reyes, CEO, MedFlex

*Sources: `Scenario/scenario_context.md`, `Deliverables/D0A_domain_research.md`, `Deliverables/D0C_discovery.md`, `References/discovery-questioning-patterns.md`. No numbers or systems invented — all facts traced to source or labelled as assumptions.*

---

## 0. Executive Summary

- **Most design-critical unknown:** Whether the bottleneck on fill rate is coordinator bandwidth or candidate supply — if candidate supply is the constraint (not enough qualified available nurses), orchestration automation will not move fill rate regardless of execution quality, invalidating the primary ROI case and requiring a fundamentally different agent scope (outbound availability capture vs. inbound matching).
- **Governance question that must be resolved before any build decision:** The scenario states credential verification is performed before placement, but the 7% mismatch rate confirms it is not functioning as a hard gate — what actually happens when verification is incomplete under time pressure (bypass, waiver, escalation?) and where is that decision recorded, if anywhere, determines whether the agent can enforce the credential gate autonomously or must route every borderline case to HITL.
- **Most likely dealbreaker:** State regulatory database access — if credential verification requires manual lookup on individual state nursing board websites with no API, the agent cannot enforce the credential gate programmatically, blocking the compliance automation that is the entire justification for agent-led placement confirmation.

---

## 0b. Table of Contents

- [0. Executive summary](#0-executive-summary)
- [0b. Table of contents](#0b-table-of-contents)
- [1. Stakeholder context](#1-stakeholder-context)
- [2. Questions whose answers would change the design](#2-questions-whose-answers-would-change-the-design)
- [3. Questions you are not asking — and why](#3-questions-you-are-not-asking--and-why)
- [4. Sequencing for a 60-minute discovery call](#4-sequencing-for-a-60-minute-discovery-call)

---

## 1. Stakeholder Context

**Marcus Reyes** is CEO of MedFlex with a background in operations and growth, not engineering. He just closed a Series B and is under board pressure to demonstrate significant growth within 24 months. His framing — "10x the business without 10x-ing the coordinators" — signals that he sees coordinator capacity as the binding constraint on growth, but this framing has not been validated against the actual bottleneck data: it is possible the constraint is candidate supply or credential infrastructure, not coordinator headcount. Marcus has seen two AI projects fail already — a chatbot hospital staff rejected and a recommendation engine nobody used — which means he will require visible, measurable early results and will distrust an agent that produces wrong placements or requires significant behaviour change from his team without demonstrated value. His primary concern about AI involvement is almost certainly liability: a credential mismatch that reaches a hospital carries patient safety risk and contractual exposure, and any agent that introduces new mismatch risk — or that his coordinators route around — repeats the prior failure pattern. What would make him trust an agent is early proof that it reduces the metrics he is already tracking (time-to-fill, mismatch rate, no-show rate) without requiring him to defend a new risk profile to his board or his hospital clients.

---

## 2. Questions Whose Answers Would Change the Design

### Category A: Reference Material — Structure, Authority, and Machine-Readability

> **Q1: When a coordinator verifies a nurse's credentials, what exactly do they look up and where — do they access state nursing board websites directly, use a third-party licence verification service, or pull from an internal system that aggregates that data?**
> **Category:** A — Reference material
> **What D0A/D0C already established:** D0A identified that credential systems are often lagging records supplemented by coordinator memory (Gap G-1); D0C established U-1 as a key unknown — whether data has 24–72-hour latency or is real-time.
> **What remains open:** The access model — whether verification is API-queryable, manual web lookup, or an internal aggregated database — is not stated anywhere in the scenario. This is distinct from data currency; even a real-time database is useless if it requires manual browser navigation.
> **If the answer is [API or integrated verification service]:** Agent can enforce the credential gate programmatically at placement time — fully automated verification is in scope for v1.
> **If the answer is [manual state board website lookup]:** Agent cannot query credentials directly; integration requires either a third-party verification API (scoped as a new vendor dependency) or a human-in-the-loop at the verification step — fundamentally changing the compliance gate architecture.
> **Why this matters more than a generic question:** This is the single most constraining technical dependency in the agent design — if verification cannot be automated, the agent cannot make autonomous placement decisions, regardless of matching quality.

---

> **Q2: When a coordinator needs to check what credentials a facility requires for a specific unit — say, ICU vs. Med/Surg — where does that information live: in a system field, a document on a shared drive, or in their memory from prior experience with that facility?**
> **Category:** A — Reference material
> **What D0A/D0C already established:** D0A Gap G-3 identified that facility requirement profiles typically live in coordinator heads, not in system records; D0C U-3 flagged this as a key unknown requiring discovery.
> **What remains open:** Whether MedFlex has made any progress on structuring facility profiles, and whether there is a partial structured record that could be enriched vs. starting from zero.
> **If the answer is [structured system field, even if incomplete]:** Facility profile enrichment is an achievable data project within the engagement timeline — agent matching can begin with a known gap list.
> **If the answer is [primarily coordinator memory, no system record]:** Facility profile structuring is a prerequisite project before any matching automation is possible — this must be scoped as a dependency in D2 and may affect the 8-week delivery timeline.
> **Why this matters more than a generic question:** Matching automation without structured facility profiles will produce mismatches at the same rate as today — the 7% failure rate is partially attributable to this gap, and the agent will inherit it if profiles are not remediated.

---

### Category B: Core Decision Logic — How Matching Actually Works Today

> **Q3: When a shift goes unfilled — no placement confirmed — what is the most common reason: no available nurse with the right credentials, available nurses declining the offer, or your team not having time to work the shift before the window closes?**
> **Category:** B — Core decision logic
> **What D0A/D0C already established:** D0A A-5 (Low confidence) hypothesised that coordinator bandwidth is the primary bottleneck — but explicitly flagged this as unvalidated. D0C U-1 left this open as the central hypothesis of the engagement.
> **What remains open:** The actual bottleneck type is the foundational assumption behind the entire ROI case. D0A A-5 was explicitly Low confidence and the scenario does not answer it.
> **If the answer is [coordinator bandwidth — shifts go unfilled because the team can't reach enough nurses in time]:** Orchestration automation directly addresses the bottleneck; fill rate improvement is the primary success metric.
> **If the answer is [candidate supply — not enough qualified nurses available]:** Automation of the matching and coordination workflow will not improve fill rate; the agent must focus on expanding available nurse pool (outbound availability capture, proactive scheduling) — a different scope entirely.
> **Why this matters more than a generic question:** This is D0A's only Low-confidence assumption that fundamentally changes whether the proposed agent scope delivers any measurable ROI.

---

> **Q4: Walk me through the last shift fill where everything went smoothly — right nurse, first contact, no complications. What did the coordinator actually do, step by step, and how long did it take?**
> **Category:** B — Core decision logic
> **What D0A/D0C already established:** D0C established that clean fills are likely the majority of decisions and the primary automation target, but the actual steps and time per clean fill are not stated in the scenario.
> **What remains open:** Whether "clean" fills have hidden complexity (intermediate checks, informal facility relationship steps) that would surface as edge cases at scale — and the per-decision time, which determines the per-coordinator automation capacity gain.
> **If the answer is [truly simple — nurse lookup, one call, confirmed in under 10 minutes]:** Clean fill automation is high confidence; the agent ROI per clean fill is meaningful and the scope is well-defined.
> **If the answer is [apparently simple but with hidden steps — informal check with facility contact, rate negotiation, relationship note]:** Agent scope is larger than expected; "clean fill" requires a richer definition before automation can proceed without producing errors at those hidden steps.
> **Why this matters more than a generic question:** The agent's first autonomous capability must be clean fills — if clean fills are not actually clean, the first agent outputs will be wrong and will repeat the prior failure pattern.

---

> **Q5: When a nurse has most but not all of the credentials a facility requires — say, 7 of 8 — what does a coordinator actually do? Is there a rule for when to proceed vs. when to keep searching, or does it depend on the coordinator?**
> **Category:** B — Core decision logic
> **What D0A/D0C already established:** D0A CH-2 identified credential gap triage as a cognitive hotspot; D0C Hotspot WS3-1 established that waiver classification requires HITL. What is not known is whether there is any codified rule for the decision.
> **What remains open:** Whether the gap classification rule is consistent across coordinators or varies person-to-person — this determines whether the agent can be trained to classify gaps reliably or will always require HITL for borderline cases.
> **If the answer is [consistent rule — missing X type is always a hard stop, missing Y type can proceed if shift is > 48 hours away]:** Agent can enforce the rule; HITL is only needed for genuinely ambiguous cases.
> **If the answer is [varies by coordinator — each person has their own threshold]:** No stable rule to codify; agent classification will introduce inconsistency unless coordinators agree on a standard rule as part of the implementation — a change management dependency.
> **Why this matters more than a generic question:** Inconsistent gap classification rules produce the 7% mismatch rate; the agent can only fix this if it enforces a rule that doesn't currently exist consistently.

---

### Category C: Governance and Approval Constraint — Exactly How It Operates

> **Q6: When a coordinator completes credential verification before confirming a placement, where is that verification recorded — in your staffing system with a timestamp, in a separate document, or not systematically recorded?**
> **Category:** C — Governance and approval
> **What D0A/D0C already established:** D0C established that no audit trail system is stated in the scenario; the 7% mismatch rate implies verification is not functioning as a reliable gate.
> **What remains open:** Whether any audit trail currently exists — if it does, the agent can append to it; if it doesn't, the agent must create it, which requires coordinators to change their confirmation behaviour.
> **If the answer is [system record with timestamp and identity]:** Agent can read and write to the existing audit trail; compliance documentation is a feature extension, not a new infrastructure build.
> **If the answer is [not systematically recorded]:** Agent must introduce the audit trail as a new system behaviour; this is a change management dependency, not just a technical one — coordinators must accept that every verification action is now logged.
> **Why this matters more than a generic question:** JCAHO/CMS audit trail requirements (scenario_context hard rules HR-1) are assumed mandatory; if no trail exists today, the agent's audit trail is a compliance deliverable, not just a nice-to-have feature.

---

> **Q7: Has a placement ever gone forward without completed credential verification — either because of time pressure or because a coordinator was confident about the nurse? When that happens, what is the process?**
> **Category:** C — Governance and approval
> **What D0A/D0C already established:** D0C established that the 7% mismatch rate implies verification is being bypassed or abbreviated under volume pressure. D0A Gap G-1 identified this as a common pattern in the domain.
> **What remains open:** Whether bypass is an informal exception with tacit tolerance or an explicit override with documented accountability — this determines whether the agent's credential gate has a waiver path or is a true hard stop.
> **If the answer is [bypasses are rare and flagged — escalated to supervisor]:** The credential gate is a genuine organisational hard stop; the agent enforces it without an override path, consistent with Hard Rule HR-1.
> **If the answer is [bypasses happen under time pressure — coordinators proceed and catch up later]:** The credential gate has a tacit waiver culture that the agent must either enforce against (creating friction) or formalise (requiring explicit override with audit logging) — either way, change management is required before deployment.
> **Why this matters more than a generic question:** An agent that enforces a hard credential gate into an environment where bypass is culturally tolerated will either be routed around or create the same adoption failure as the prior recommendation engine.

---

> **Q8: When MedFlex places a nurse who turns out to have a credential gap — the 7% mismatch case — what actually happens? Who discovers it, what is the consequence for MedFlex, and who is held accountable internally?**
> **Category:** C — Governance and approval
> **What D0A/D0C already established:** D0C assumption A4 flagged uncertainty about whether the 7% is facility-reported failures or internally caught errors. D0A HQ-6 identified liability as a key question.
> **What remains open:** The severity of consequence is not stated in the scenario; this determines how aggressively the agent's credential gate must be enforced and how much false-negative risk (blocking a valid placement) is acceptable relative to false-positive risk (permitting an invalid one).
> **If the answer is [facility discovers it, contractual consequence, MedFlex bears liability]:** Credential gate is a non-negotiable hard stop — any false negative is unacceptable; the agent must err toward blocking over permitting in borderline cases.
> **If the answer is [corrected informally, no contractual consequence triggered to date]:** Risk tolerance is higher than assumed; the agent can use a confidence threshold with HITL escalation for borderline cases rather than a binary hard stop — reducing friction for coordinators.
> **Why this matters more than a generic question:** The severity of the 7% mismatch consequence determines whether the credential gate design is binary (block/permit) or probabilistic (confidence threshold + escalation).

---

### Category D: Exception Patterns and Escalation Triggers

> **Q9: Think about the last three no-shows you're aware of. What did those situations have in common — was it a specific shift type, time of day, how the placement was confirmed, or something else?**
> **Category:** D — Exception patterns
> **What D0A/D0C already established:** D0C assumption AD5 hypothesised that the 12% no-show rate is a confirmation loop failure; D0C U-6 identified the confirmation channel as unknown.
> **What remains open:** Whether no-shows cluster around a specific confirmation pattern (verbal only, late-night shifts, specific nurse profiles) — this determines whether structured confirmation orchestration will actually move the 12% metric or whether the root cause is elsewhere.
> **If the answer is [no-shows cluster around informal confirmation — verbal-only or SMS without explicit acknowledgment]:** Structured confirmation loop directly addresses the root cause; agent orchestration reduces no-show rate as a primary measurable outcome.
> **If the answer is [no-shows are personal emergencies or cancellations unrelated to confirmation method]:** Confirmation loop redesign will not move the 12% metric; the agent's value must be justified on fill rate and mismatch reduction alone, and no-show rate should not be a primary success metric.
> **Why this matters more than a generic question:** If no-show rate is not moveable by agent intervention, the success metric framework in D1 must be revised before the engagement proceeds.

---

> **Q10: When a shift is at risk of going unfilled — you've contacted several nurses and none have accepted — at what point does a coordinator escalate, and what does escalation look like in practice?**
> **Category:** D — Exception patterns
> **What D0A/D0C already established:** D0A HQ-8 hypothesised that escalation thresholds are inconsistent across coordinators. D0C U-7 flagged the escalation path as unstated in the scenario.
> **What remains open:** Whether an escalation protocol exists at all, and whether it involves a supervisor, a different coordinator, or direct facility notification.
> **If the answer is [defined threshold — after 3 contacts with no accept, escalate to supervisor]:** Agent can automate the contact-attempt loop and trigger escalation at a consistent threshold, removing coordinator judgment from the loop and improving consistency.
> **If the answer is [coordinator judgment — each person decides when to escalate]:** Agent must include an escalation trigger design that formalises a threshold; this is a process change, not just a feature, and requires buy-in from coordinators before deployment.
> **Why this matters more than a generic question:** Inconsistent escalation contributes to unfilled shifts — the agent's escalation trigger is one of its highest-value features if the current process is ad-hoc.

---

### Category E: Data and System Reality

> **Q11: When a nurse renews their licence or completes a certification, how quickly does that appear in your system — same day, next day, or longer? And who updates it — the nurse self-reports, a credentialing team updates it manually, or it comes from an external data feed?**
> **Category:** E — Data and system reality
> **What D0A/D0C already established:** D0A A-4 (Medium confidence) hypothesised 24–72-hour latency; D0C U-1 flagged credential data currency as the most consequential unknown for agent scope.
> **What remains open:** The actual latency and the update mechanism — these together determine whether the agent can use the credential system as a live gate or must treat it as a lagging record with uncertainty.
> **If the answer is [same-day, automated feed from state board or verification service]:** Agent can enforce the credential gate in real time; placement confirmation can be autonomous for standard credential checks.
> **If the answer is [manual update by credentialing team, 24–72-hour lag]:** Agent must treat credential status as potentially stale; placement confirmation must include a stale-data warning or route to HITL — reducing autonomy until data infrastructure is remediated. This also surfaces a remediation project as a prerequisite delivery dependency.
> **Why this matters more than a generic question:** Credential data currency is the binding constraint on how much autonomous authority the agent can hold at the placement confirmation step — the most consequential single data question in the design.

---

> **Q12: When a coordinator wants to know if a specific nurse is available for a shift, how do they find out — is availability recorded in a system they can query, or do they call or text the nurse directly?**
> **Category:** E — Data and system reality
> **What D0A/D0C already established:** D0C established that nurse communication channels are unstated; D0A A-3 (Medium) hypothesised SMS/phone dominance. Availability data structure is entirely unknown.
> **What remains open:** Whether availability is queryable programmatically or requires direct nurse contact — this determines whether the agent's candidate identification step can be a database query or must initiate nurse outreach to determine availability.
> **If the answer is [availability in system, updated by nurse via app or portal]:** Agent can generate a qualified shortlist before any nurse contact; coordination is offer-first, not availability-discovery-first. Faster and lower friction.
> **If the answer is [availability via direct contact only — call or text]:** Agent must initiate multi-nurse outreach to discover availability before it can identify candidates; the coordination flow is fundamentally different and the agent's first action is outbound contact, not query. Out-of-scope nurse app means this may require SMS orchestration.
> **Why this matters more than a generic question:** If availability is contact-only, the agent's primary value is in parallel outreach automation (contacting 10 nurses simultaneously vs. 1 at a time), not in smart shortlisting — a different design and a different capability spec.

---

> **Q13: Are there data sources your coordinators regularly use that are not in any system — things in spreadsheets, email threads, or in people's heads — that affect which nurse they choose for a shift?**
> **Category:** E — Data and system reality
> **What D0A/D0C already established:** D0C established that facility profiles and nurse preference data are assumed fragmented; D0A CH-1 identified tacit relationship knowledge as a key matching input.
> **What remains open:** The specific nature and volume of off-system data — is it occasional (one spreadsheet for specific facility preferences) or pervasive (every experienced coordinator maintains their own notes)?
> **If the answer is [occasional, bounded — a few facility preference notes in a shared doc]:** Off-system data can be ingested and structured as a one-time data project; the agent's knowledge base is completable.
> **If the answer is [pervasive — every coordinator maintains personal notes and the real matching knowledge is distributed across individuals]:** Institutional knowledge capture is a major prerequisite project; the agent cannot match at coordinator quality until this knowledge is externalised and structured, which may take months.
> **Why this matters more than a generic question:** Pervasive off-system data means the agent will initially underperform experienced coordinators — a trust risk if introduced without a knowledge-capture phase, and a direct repeat of the recommendation engine failure (nobody trusted its output).

---

### Category F: Organisational and Trust Context

> **Q14: The chatbot that hospital staff rejected and the recommendation engine nobody used — what specifically went wrong with each? Was it the output quality, the way adoption was handled, or the use case itself?**
> **Category:** F — Organisational and trust
> **What D0A/D0C already established:** D0C U-5 flagged this as a critical unknown with direct implications for adoption strategy. The scenario states the failures but gives no root cause.
> **What remains open:** Root cause is entirely unknown; without it, this engagement cannot design an adoption approach that avoids repeating the failure pattern.
> **If the answer is [adoption failure — tools deployed without coordinator or facility involvement in design]:** This engagement must involve coordinators and facility contacts in design validation before build; agent output must be visible and reviewable before any autonomous action is taken.
> **If the answer is [output quality failure — recommendations were wrong too often to trust]:** HITL phase before reducing oversight is mandatory; agent confidence thresholds must be conservative at launch; success requires demonstrably low error rate before expanding autonomy.
> **Why this matters more than a generic question:** Marcus will not fund a third AI failure. The single most important risk mitigation is understanding exactly what failed before, and this question cannot be answered from the scenario.

---

> **Q15: If this agent handles 60–70% of straightforward shift fills autonomously within 8 weeks, what do you see your 8 coordinators doing with the time that frees up — and have you already identified where you'd redeploy that capacity, or is that still open?**
> **Category:** F — Organisational and trust
> **What D0A/D0C already established:** The scenario establishes that Marcus's goal is "10x the business without 10x-ing the coordinators" — implying growth without headcount growth. What is not established is whether the freed capacity is mapped to a specific growth activity.
> **What remains open:** Whether role transition has been planned; coordinators who don't see a valued future role in a more automated operation may resist the agent or route around it even if Marcus supports it.
> **If the answer is [already planned — freed coordinators will focus on account growth, complex fills, client relationships]:** Role transition is scoped; the agent can be introduced as a productivity amplifier rather than a threat, reducing adoption risk.
> **If the answer is [not yet planned — haven't thought through the coordinator role in detail]:** Adoption risk is high; coordinators may resist or undermine the agent if they perceive it as a headcount reduction tool; role redesign must be addressed before deployment, not after.
> **Why this matters more than a generic question:** An agent that coordinators route around cannot sustain its performance metrics — and this is exactly what happened to the recommendation engine nobody used.

---

> **Q16: If the agent confirms a placement that later turns out to be a credential mismatch — a nurse placed at the wrong facility type — what would the consequence be for MedFlex and for you personally with that hospital?**
> **Category:** F — Organisational and trust
> **What D0A/D0C already established:** D0A HQ-6 identified liability as a key question; scenario_context Hard Rule HR-1 establishes the credential gate assumption. What is not known is the severity of consequence.
> **What remains open:** Marcus's personal risk tolerance at the placement confirmation step — this cannot be inferred from the scenario and determines how much autonomous authority the agent holds.
> **If the answer is [severe — contract review, liability clause triggered, hospital relationship at risk]:** Agent must operate with maximum caution at the confirmation step; false negatives (blocking valid placements) are preferable to false positives (permitting invalid ones); autonomy at confirmation is not viable in v1.
> **If the answer is [manageable — corrective process exists, hasn't triggered contractual consequence to date]:** A confidence threshold with HITL escalation for borderline cases is acceptable; agent can hold conditional autonomy at confirmation with defined escalation triggers.
> **Why this matters more than a generic question:** Marcus's risk tolerance at the most consequential decision point is the primary input to the autonomy matrix design — it cannot be assumed and must be stated explicitly by him.

---

> **Q17: What would the minimum visible human oversight step need to look like — for you, and for your coordinators — for you to feel comfortable letting the agent make placement decisions without a human reviewing every single one?**
> **Category:** F — Organisational and trust
> **What D0A/D0C already established:** The scenario establishes that Marcus has seen two AI failures and is results-oriented but cautious. No specific oversight preference is stated.
> **What remains open:** Whether Marcus's acceptable oversight model is exception-only (agent decides, human reviews only flagged cases), sampling-based (random review of a percentage), or metrics-based (trust by outcome, not by case review).
> **If the answer is [exception-only — review flagged cases only]:** Agent-led + Human Oversight archetype is viable; agent can operate autonomously with an alert system for borderline or high-risk decisions.
> **If the answer is [every decision reviewed, at least initially]:** Human-led + Agent Support is the appropriate archetype for v1; coordinator reviews and approves every agent recommendation before it becomes a confirmed placement — slower trust-building but politically safer given prior failures.
> **Why this matters more than a generic question:** The oversight model determines the HITL rate, which determines the agent's actual throughput contribution — a review-every-decision model at 960/day provides minimal efficiency gain and will not demonstrate the ROI Marcus needs for his board.

---

## 3. Questions You Are NOT Asking — and Why

> **Question not asked:** "How many employees does MedFlex have, and how many coordinators are on your team?"
> **Why not:** Already stated in the scenario — 200 employees, 8 coordinators. Asking confirmed facts wastes Marcus's time and signals the FDE hasn't prepared, which he will notice.

> **Question not asked:** "What are your biggest pain points with the current process?"
> **Why not:** No design fork — "tell me your pain points" produces a wish list, not a design constraint. Marcus cuts off rambling questions. The specific pain points (7% mismatch, 12% no-show, 4.2-hour fill time) are already in the scenario; what's needed is root cause and operational detail, not a general restatement of problems.

> **Question not asked:** "Are you concerned about AI making mistakes in placements?"
> **Why not:** This is a statement of concern dressed as a question with no design fork — it presupposes the answer and positions the FDE as seeking reassurance rather than designing a solution. Q16 addresses the same underlying concern with a specific design fork.

> **Question not asked:** "What is MedFlex's annual revenue or growth rate?"
> **Why not:** Not stated in the scenario; interesting for context but produces no design decision. The ROI case is driven by volume and time metrics (960/day, 4.2-hour fill time), not by revenue figures. Asking for financial data in a discovery call with a CEO who is time-pressured and operationally focused is likely to derail the conversation.

> **Question not asked:** "Have you considered a nurse mobile app to streamline confirmations?"
> **Why not:** The scenario explicitly states nurse mobile app is out of scope. Asking a question whose answer is already determined by the engagement scope wastes the call slot and may undermine Marcus's confidence in the FDE's preparation.

---

## 4. Sequencing for a 60-Minute Discovery Call

*Marcus is time-pressured and cuts off rambling. Every question must be delivered as a crisp single sentence. The call prioritises the three highest-stakes unknowns: bottleneck type (Q3), credential gate operation (Q7), and prior failure root cause (Q14).*

| Time slot | Question(s) | Goal for this segment |
|-----------|------------|----------------------|
| 0–5 min | Context setting — confirm Marcus's direct involvement in operations and which parts of the process he observes personally vs. delegates | Establish whether Marcus can answer operational questions directly or whether a follow-up session with a senior coordinator is required; calibrate question depth for the remaining 55 minutes |
| 5–15 min | Q3 (bottleneck type) and Q4 (clean fill walkthrough) | Validate or invalidate the core ROI hypothesis: is coordinator bandwidth the binding constraint on fill rate? If not, the proposed agent scope must change before any further deliverable is produced |
| 15–30 min | Q4 (continued — walk through a real clean fill), Q12 (nurse availability data), Q13 (off-system data) | Map the actual matching decision against the assumed clean-fill flow; identify data dependencies that could block the first agent capability; discover whether tacit knowledge is bounded or pervasive |
| 30–45 min | Q7 (credential gate bypass), Q8 (consequence of mismatch), Q11 (credential data currency) | Resolve the governance and compliance gate design: is the credential gate a genuine hard stop or a cultural soft stop? What is the actual consequence of the 7% mismatch? Can the agent enforce the gate programmatically? |
| 45–55 min | Q14 (prior AI failure root cause), Q16 (Marcus's risk tolerance at placement confirmation), Q17 (minimum oversight model) | Design the trust and oversight architecture: what failed before and why, what Marcus will accept as autonomous agent action, and what oversight level is politically viable for rollout |
| 55–60 min | Close: summarise the three design-critical open questions (bottleneck type, credential gate access, oversight model), confirm next steps (coordinator session for lived process, system access review) | Leave Marcus with a clear picture of what the FDE needs to resolve before architecture can be finalised; signal that the FDE is designing against real constraints, not producing a generic AI pitch |
