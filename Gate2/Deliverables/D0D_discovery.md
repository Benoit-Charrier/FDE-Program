# D0D — Discovery Synthesis: Apex Distribution Ltd — Customer Operations

**Produced:** 2026-05-06
**Status:** Draft — awaiting FDE review

---

## 0. Executive summary

- Delivery exceptions (~180/day at 12 min/case) consume the most skilled human time per unit and carry the highest operational friction: the SOP's damaged-consignment section is explicitly incomplete, every decision is discretion-driven, and the driver is physically parked waiting for a call-back — meaning the cost of a slow response is borne by the entire downstream route, not just the one case.
- The most critical lived-vs-documented gap is the informal credit mechanism: Aurum Billing cannot adjust individual invoice line items in real time, so agents apply goodwill credits as a workaround, bypassing the formal audit trail the billing system schema requires — creating a compliance exposure that is invisible in the daily CSV exports.
- ETA inquiries (~400/day at 4 min/case) show the strongest delegation signal: the underlying task is a structured lookup-and-respond against CRM and Driver App data, the inputs are already digital, the CRM exposes REST APIs, and the only judgment required is a confidence-weighted estimate from GPS data — a well-defined problem that an agent can handle with low error risk and immediate volume impact.

---

## 0b. Table of contents

- [0. Executive summary](#0-executive-summary)
- [0b. Table of contents](#0b-table-of-contents)
- [1. Lived process narrative](#1-lived-process-narrative)
- [2. Points of pain inventory](#2-points-of-pain-inventory)
- [3. ATX discovery dimensions — assessment per work stream](#3-atx-discovery-dimensions--assessment-per-work-stream)
- [4. Cognitive workload hotspots](#4-cognitive-workload-hotspots)
- [5. Known unknowns](#5-known-unknowns)
- [6. Assumption log](#6-assumption-log)

---

## 1. Lived process narrative

*The following reconstructs the actual lived process from the scenario artefacts. Where the scenario provides direct evidence (artefacts, explicit statements), it is cited. Where inference fills a gap, it is labelled as [INFERENCE].*

### How work arrives

Work does not arrive as a clean queue. A dispatcher's morning begins with a mix already in motion: inbound calls from drivers on the road, an email thread from a customer who escalated yesterday, an SMS inquiry that came in at 07:50, and a queue of cases in the CRM from the prior day that were not fully closed. The scenario does not state how cases are distributed across the 35-person team; the assumption is a shared queue with some informal assignment by type or familiarity [INFERENCE — see A-1 in assumption log].

**Trigger sources confirmed by the scenario:**
- Driver phone call / voicemail to the dispatch desk (Artefact 1)
- Customer email to billing@ or customer ops (Artefact 2)
- Customer SMS to the ETA inquiry line (Artefact 3)
- [INFERENCE] Inbound calls are also implied by the 22-minute hold time in Artefact 2

### ETA inquiry path (400/day, 4 min/case)

A customer contacts the ETA inquiry line — by SMS, call, or email — asking where their delivery is. The agent opens the CRM, retrieves the order record, and cross-references the Driver App for the route and GPS data. For a standard inquiry, the agent provides the assigned delivery window (e.g., 13:00–17:00) and closes the case.

For an edge case — where the customer asks for a tighter estimate — the agent checks the driver's last GPS ping. The GPS data has latency: in Artefact 3, the last recorded ping at the time of the 11:14 inquiry was from 10:48, meaning the agent is giving an estimate based on 26-minute-old location data [scenario evidence: Artefact 3]. The agent then calls or messages dispatch to get a human assessment of likely ETA, waits for a response (a 5-minute gap in Artefact 3), and relays the estimate to the customer. The "edge case" here is not rare — any customer who pushes back on a 4-hour window triggers the dispatch consultation step.

**Pause point:** the agent pauses to evaluate whether the GPS data is fresh enough to give a useful estimate, or whether a dispatch call is necessary.
**Workaround:** the GPS ping latency means the agent must apply a mental model of "how far could this driver have travelled in 26 minutes" to produce an estimate — a judgment step that a lookup alone cannot eliminate.
**Async wait:** the 5-minute gap waiting for dispatch response is dead time that extends average handle time.

### Delivery exception path (180/day, 12 min/case)

A driver encounters an exception — damage claim, refused delivery, missed window, unattended address — and contacts the dispatch desk. In Artefact 1, this arrives as an unstructured voicemail. The driver is parked, has six more drops on the route, and is waiting for a call-back before he can proceed.

The dispatcher receives the voicemail [INFERENCE: the dispatcher listens to or reads the message, then retrieves the case in the CRM to confirm customer details and consignment value]. There is no codified decision procedure for damaged consignments — SOP Section 4.3 is marked "TBD pending review of insurance protocol" [scenario evidence: Artefact 4]. The dispatcher draws on experience: is this customer one who would accept a conditional delivery? Is the pallet damage likely to be cosmetic or structural? Is the site manager reachable? For high-value consignments (>£500), the SOP requires escalation to the Duty Manager via the dispatch console [scenario evidence: SOP Section 4.2] — but whether this threshold is consistently applied is not confirmed [INFERENCE].

The dispatcher calls or messages the driver back with an instruction. The driver proceeds or returns to depot. The dispatcher logs the outcome in the CRM [INFERENCE — the scenario implies CRM is the case management system but does not confirm every exception generates a CRM entry].

**Pause point:** the dispatcher pauses before calling the driver back — evaluating whether to return-to-depot, hold, or reattempt, without a complete procedure to follow for the damage scenario.
**Judgment call:** the core decision (what do I do with this consignment?) is made by the dispatcher based on tacit knowledge, not a rule table.
**Coordination work:** the dispatcher must reach the driver by call or app message, wait for acknowledgement, and confirm the instruction was understood — all while other exceptions and ETA inquiries are arriving.
**Workaround:** in the absence of a damage assessment protocol, the dispatcher substitutes personal judgment for policy — consistently across experienced staff, inconsistently across the full team.

### Dispatch adjustment path (90/day, 18 min/case)

A mid-route change is required — a new pickup added, a diversion needed, a driver swap. The dispatcher must assess the current state of the affected route: driver location (Driver App), remaining drops and their sequence (dispatch console), time constraints, and the impact on customer commitments. The dispatch console is a Java desktop application deployed via Citrix [scenario evidence] with a stated limited API surface — meaning the dispatcher is likely working through a graphical interface, not a programmatic integration [INFERENCE].

The dispatcher makes the adjustment, communicates it to the driver via the Driver App messaging system, and logs the change. Time pressure is named explicitly in the scenario as a characteristic of this work stream. The 18-minute average handle time reflects the multi-system coordination burden — assembling a decision from fragmented, non-integrated data sources [INFERENCE based on scenario system description].

**Pause point:** the dispatcher pauses to mentally construct a picture of the route state across at least two systems before making an adjustment.
**Judgment call:** prioritising downstream drops — which customer can absorb a delay vs. which cannot — requires contextual knowledge that is not encoded in the dispatch console.
**Coordination work:** communicating the adjustment to the driver and confirming receipt adds time that is not pure decision-making.

### Billing dispute path (60/day, 28 min/case)

A customer disputes a charge on their invoice. They contact billing@ or customer operations. The agent retrieves the invoice from — but Aurum Billing is batch-only; the agent is looking at yesterday's data at best, and reconciliation data lags 24 hours further still [scenario evidence: Artefact 5]. The agent cannot query Aurum in real time [scenario evidence].

The agent identifies that the disputed charge (e.g., a fuel surcharge) cannot be removed or adjusted on the individual invoice — Aurum calculates fuel surcharges automatically and invoice modifications require a manual ticket to the Aurum support team with a 48-hour turnaround [scenario evidence]. The agent cannot close the dispute by correcting the invoice. The only tool available is a goodwill credit.

The agent applies a goodwill credit — but, as Artefact 2 shows, this is done via manual override without generating an entry in the APEX_CREDITS audit log. The credits export schema formally supports APPROVER_ID and AUDIT_REF fields [scenario evidence: APEX_CREDITS CSV], but the informal application bypasses this. The customer does not receive a corrected invoice; they receive a credit on their next statement. Depending on when in the billing cycle this falls, the credit may not appear for weeks [INFERENCE].

**Async wait:** the agent is blocked on the 48-hour Aurum ticket for any formal invoice correction — and has no mechanism to accelerate this.
**Workaround:** the goodwill credit is the structural workaround for a system that cannot perform the correct action (invoice line-item correction). The workaround generates a compliance gap.
**Pause point:** the agent must decide whether the dispute warrants a credit, at what amount, and whether to escalate — without a formal policy on credit thresholds [INFERENCE — no threshold stated in scenario].
**Coordination failure:** Artefact 2 shows the customer was bounced from billing@ to customer ops and back, waiting 9 days for a partial resolution.

---

## 2. Points of pain inventory

| Work Stream | Pain Description | Volume (derived — see note) | Pain Level | Lived-vs-Documented Gap | Key Data/Systems Involved | Delegation Signal | Candidate for Automation? |
|-------------|-----------------|----------------------------|------------|------------------------|--------------------------|-------------------|--------------------------|
| WS2 — ETA inquiries | GPS data is 20–30 min stale at time of response; 4-hour windows dissatisfy customers; edge cases require dispatch consultation, extending handle time | ~2,000/week | M | SOP does not address GPS latency or the dispatch-consultation step; agents improvise the tighter-estimate path | CRM (REST API available), Driver App (GPS) | High — structured lookup, digital inputs, codifiable rules, REST APIs available | Yes — strong candidate for autonomous agent handling; static API integration insufficient for edge-case estimates |
| WS1 — Delivery exceptions | No SOP for damaged consignments; all decisions are dispatcher-discretion; driver parked waiting increases route-wide cost of every delay | ~900/week | H | SOP Section 4.3 incomplete; SOP references DispatchHub (retired Oct 2024); real process is phone/app call-back | CRM, Driver App (unstructured messages), Dispatch console | Medium — HITL co-pilot viable; fully autonomous not viable without damage assessment protocol | Yes — agent as structured intake + decision-support; not autonomous close |
| WS3 — Dispatch adjustments | Multi-system context synthesis under time pressure; Citrix dispatch console limits programmatic access; decision has cascade effect on downstream drops | ~450/week | H | No documented escalation procedure for complex adjustments; SOP does not cover mid-route scenarios in detail | Dispatch console (Citrix, limited API), Driver App | Low-medium — high time pressure and operational consequence; HITL required; system access constraint limits agent scope | Partial — structured intake and recommendation; final decision must stay with dispatcher |
| WS4 — Billing disputes | Cannot adjust invoice line items in real time; 48h Aurum ticket for any formal correction; informal credit bypasses audit trail; customer bounced between teams | ~300/week | H | Formal process requires APPROVER_ID and AUDIT_REF; actual practice bypasses both; SOP does not address billing system constraints | Aurum Billing (batch-only), CRM | Medium — triage, policy lookup, and credit recommendation viable; autonomous credit application not viable above a defined threshold | Yes — agent handles triage, policy check, audit-compliant credit recommendation; human approves above threshold |
| Cross-cutting — SOP staleness | SOP references retired system (DispatchHub); damage section incomplete; agents operate on informal knowledge not captured anywhere | All work streams | H | SOP v2.3 (Oct 2023) vs. Driver App deployment (Oct 2024); 18-month gap | SOP document, Driver App | N/A — this is a prerequisite gap, not a delegatable task; must be resolved before agent can be built from documented process | No — requires process documentation work before automation |
| Cross-cutting — Audit trail gap | Credits applied informally; APEX_CREDITS schema supports audit trail but informal application bypasses it; compliance exposure exists | ~300 dispute cases/week (disputes as proxy) | H | Credits export schema has APPROVER_ID/AUDIT_REF; Artefact 2 shows credit with no log entry | Aurum Billing (APEX_CREDITS export), CRM | N/A — this is a compliance gap; agent design must enforce the correct path, not replicate the workaround | Prerequisite design constraint — agent must generate compliant credit records, not inherit the bypass |

**Pain level justification:**
- **WS2 ETA — Medium:** High volume but the task is largely tractable; the pain is inefficiency, not compliance risk or operational failure. The customer experience is suboptimal (4-hour window, stale GPS) but the work closes cleanly.
- **WS1 Exceptions — High:** Incomplete SOP for the primary exception type (damage), dispatcher discretion as the sole decision mechanism, and driver downtime cascading to the full route make this operationally costly per case even at 12 min average.
- **WS3 Dispatch adjustments — High:** Systemic latency from multi-system coordination, time pressure, and operational cascade risk. Lower volume (90/day) reduces aggregate daily burden but per-case risk is high.
- **WS4 Billing disputes — High:** Longest handle time (28 min), systemic billing constraint (48h), active compliance gap (informal credits), and repeat-disputer pattern (C-04451 holds 3 simultaneous open disputes). Highest per-case cost and highest compliance risk.

---

## 3. ATX discovery dimensions — assessment per work stream

| Work Stream | Volume & Time | Cognitive Nature | Data & Systems | Risk & Compliance | Organisational |
|-------------|--------------|-----------------|---------------|-------------------|---------------|
| **WS2 — ETA inquiries** | 400/day, 4 min/case; ~1,600 agent-min/day; highest volume work stream by case count | Primarily rule-bound: lookup-and-respond; judgment only at edge (tighter estimate requires GPS interpretation + dispatch consult) | CRM (REST APIs confirmed); Driver App (GPS); GPS data has observable latency (~26 min in Artefact 3) | Low — providing an estimate carries no financial or regulatory consequence; error is a poor customer experience, not a compliance event | Single agent handles; dispatch consultation required for edge cases; no formal escalation path |
| **WS1 — Delivery exceptions** | 180/day, 12 min/case; ~2,160 agent-min/day; highest per-case cognitive cost | Judgment-heavy: no codified procedure for damaged consignments; dispatcher discretion primary; SOP explicitly incomplete for damage type | Driver App (unstructured messages from driver); CRM; Dispatch console (Citrix, limited API); inputs are primarily unstructured text/voice | Medium-high: >£500 consignment requires Duty Manager escalation per SOP; insurance protocol review incomplete; high-value damage decisions carry financial and reputational risk | Dispatcher discretion primary; Duty Manager escalation for >£500 (SOP); consistency of escalation compliance unknown — requires discovery |
| **WS3 — Dispatch adjustments** | 90/day, 18 min/case; ~1,620 agent-min/day; lowest volume but highest per-case coordination burden | Decision-making under time pressure: requires simultaneous awareness of route state, driver capacity, and customer priority across 2–3 systems | Dispatch console (Citrix, limited API surface — specific capabilities unstated); Driver App (GPS, messaging) | Medium: driver hours compliance is a constraint; cascade effect on downstream drops; Unknown — requires discovery whether any formal approval is needed for route changes | Unknown — requires discovery: who has authority to approve dispatch adjustments? Is there an escalation path for complex changes? |
| **WS4 — Billing disputes** | 60/day, 28 min/case; ~1,680 agent-min/day; highest per-case handle time; longest resolution cycle | Synthesis + decision-making: cross-reference invoice, delivery outcome, customer history, credit policy; judgment on credit amount | Aurum Billing (batch-only, T-1 invoices, T-2 reconciliation, 48h modification ticket); CRM; no real-time integration between systems | High: APEX_CREDITS schema requires APPROVER_ID and AUDIT_REF; Artefact 2 shows active bypass of audit trail; financial control gap; repeat-disputer pattern in open disputes data | Billing@ and Customer Ops are separate entry points (Artefact 2 shows customer bounced between them); no clear ownership boundary stated in scenario; credit authority threshold unknown — requires discovery |

---

## 4. Cognitive workload hotspots

> **Hotspot WS2-1: ETA inquiries — converting stale GPS data into a useful customer estimate**
> **What the human does:** Interprets a GPS timestamp and location, applies a mental model of route progress and traffic conditions, and decides whether the data is fresh enough to give a reliable estimate or whether a dispatch call is necessary.
> **Why a machine can't trivially replace this today:** The GPS data has observable latency (~26 min in the artefact); a rule-based system that simply reports the last ping location would provide a stale answer. Producing a useful estimate requires reasoning about movement rate, route sequence, and confidence — a small but real inference step.
> **Delegation signal:** Medium-high. The inference is bounded: route distance, average speeds, and GPS refresh rates are knowable. An agent with access to route data and Driver App GPS could produce a confidence-weighted estimate. The key condition: GPS refresh rate and Driver App API access must be confirmed. If the Driver App exposes a real-time GPS endpoint (not just a logged ping), this becomes highly automatable.

> **Hotspot WS1-1: Delivery exceptions — deciding the disposition of a refused or damaged consignment**
> **What the human does:** Synthesises an unstructured driver report (voicemail or app message) with CRM customer history, consignment value, and operational context (driver's remaining drops, time of day, site manager availability), then produces an actionable instruction: return-to-depot, hold, reattempt, or conditional acceptance.
> **Why a machine can't trivially replace this today:** The decision procedure for damaged consignments does not exist in documented form (SOP Section 4.3 is blank). The inputs are unstructured. The consequences are immediate and hard to reverse (driver acts on the instruction and moves on). No confidence threshold exists because no decision logic has been formalised.
> **Delegation signal:** HITL co-pilot is the realistic target before full autonomy. Conditions needed: (1) structured intake form for driver exceptions (replaces unstructured voicemail); (2) a documented decision matrix for at least the top 3 exception types; (3) human approval for all cases above a consignment value threshold. The agent pre-populates the case, presents a recommended disposition, and a dispatcher approves in under 2 minutes rather than reconstructing from scratch in 12.

> **Hotspot WS1-2: Delivery exceptions — applying the >£500 Duty Manager escalation rule consistently**
> **What the human does:** Estimates consignment value from available data and decides whether to escalate to the Duty Manager before giving the driver an instruction.
> **Why a machine can't trivially replace this today:** The scenario does not confirm that consignment value is a field readily queryable from the CRM or Driver App at the point of exception. If the value is embedded in the order record, retrieval is straightforward; if it requires a separate billing lookup, the agent faces the same latency constraints as billing disputes.
> **Delegation signal:** High for the threshold-check itself if consignment value is accessible in the CRM. This is a rule-table decision (value > £500 → escalate) that an agent can apply mechanically and consistently — removing the current inconsistency risk.

> **Hotspot WS4-1: Billing disputes — determining the appropriate credit amount when invoice correction is impossible**
> **What the human does:** Accepts that the invoice cannot be corrected in real time, determines what goodwill credit is appropriate (partial? full? proportional to the dispute amount?), decides whether to apply it now or wait for Aurum ticket resolution, and judges whether the credit should be formal (through proper channels) or informal (manual override).
> **Why a machine can't trivially replace this today:** There is no stated credit policy: the scenario shows Sandra applying £170 against a £340 dispute with no stated rule for why 50% was chosen. Without a codified credit policy, the agent has no rule table to apply. The informal bypass of the audit trail is the human workaround for a process that is too slow to satisfy customers — an agent that enforces the formal path will appear slower unless the underlying process constraint (48h Aurum ticket) is also addressed.
> **Delegation signal:** Medium. Prerequisite: a formal credit policy with stated thresholds must exist before an agent can be built to enforce it. Once that policy exists, the agent can: (a) retrieve the dispute details from APEX_DISPUTES, (b) apply the policy, (c) generate a formal credit record with APPROVER_ID and AUDIT_REF, and (d) route for human sign-off above threshold. The constraint is policy definition, not technical capability.

> **Hotspot WS3-1: Dispatch adjustments — assembling a decision from fragmented, non-integrated data sources**
> **What the human does:** Simultaneously queries the dispatch console for route state, checks the Driver App for current GPS, and mentally constructs a picture of what the adjusted route would look like — timing, sequence, driver capacity — before making the change.
> **Why a machine can't trivially replace this today:** The dispatch console has a "limited API surface" and runs via Citrix — programmatic integration may not be feasible without significant platform work. Without the ability to read and write to the dispatch console programmatically, an agent cannot substitute for the dispatcher's manual data assembly.
> **Delegation signal:** Low in current state, pending technical discovery. The key unknown is what the dispatch console API surface actually covers. If read-only route data is accessible, an agent could pre-populate a decision summary for the dispatcher's review. Write capability (making the actual route change) is a separate and likely more constrained question.

---

## 5. Known unknowns

> **Unknown U-1: What is the actual credit authority threshold — below what amount can an agent apply a credit without human approval, and does a formal policy exist or only informal norms?**
> **Why it matters for agent design:** Without a formal credit threshold, the agent has no rule to enforce. The delegation archetype for billing disputes (autonomous below threshold vs. always HITL) depends entirely on whether this threshold exists and at what level.
> **How to discover it:** Ask the COO and a billing agent separately: "Is there a defined amount below which you can apply a credit without getting approval?" Compare answers. If they differ, the threshold is informal and must be formalised as part of agent design.

> **Unknown U-2: What API surface does the Driver App actually expose — specifically, is GPS location available in real time or only as a logged ping, and what is the refresh rate?**
> **Why it matters for agent design:** The quality of ETA estimates the agent can produce depends directly on GPS data freshness. A 26-minute GPS lag (Artefact 3) means the agent must reason probabilistically; a near-real-time feed changes the estimate from inference to lookup. This also affects exception handling — the agent's ability to locate the driver and confirm route context depends on data freshness.
> **How to discover it:** Request the Driver App technical documentation or API spec. Alternatively, ask a dispatcher: "When you check the Driver App during an exception, how old is the GPS location typically?"

> **Unknown U-3: Does the dispatch console expose any programmatic read or write API, and is it accessible outside the Citrix session?**
> **Why it matters for agent design:** If the dispatch console has no accessible API, dispatch adjustment automation is limited to structured intake and recommendation — the agent cannot read route state or write changes programmatically. This would constrain WS3 to a HITL support tool rather than any form of autonomous execution.
> **How to discover it:** Ask the IT team: "Does the dispatch console have a REST or SOAP API, or any integration endpoint outside the Citrix session?" Also ask what changed when DispatchHub was retired — was any integration work done at that point?

> **Unknown U-4: What is the actual headcount split across the four work streams — are agents dedicated to work types or do they handle all four?**
> **Why it matters for agent design:** If the team is partitioned (e.g., a dedicated billing team), the agent scope, training data, and deployment model would be different for each partition. If agents handle all four work streams interchangeably, a single agent with multi-domain capability is the right design.
> **How to discover it:** Ask the team lead: "On a typical day, do individual agents handle all four work types or do people specialise?" Also observe the CRM assignment pattern — do individual agent IDs appear across all four case types or predominantly one?

> **Unknown U-5: What does the escalation path for >£500 delivery exceptions actually look like in practice — is the Duty Manager consistently reachable, and how often is the threshold bypassed?**
> **Why it matters for agent design:** The agent must enforce escalation thresholds mechanically. But if the current escalation path is frequently bypassed because the Duty Manager is unavailable or the threshold is poorly understood, building the agent to strictly enforce it will surface a process problem — the agent will create cases it cannot close, or it will be perceived as slowing down experienced dispatchers.
> **How to discover it:** Ask a dispatcher: "When you get an exception with a consignment above £500, what do you actually do? How often does that reach the Duty Manager?" Pull CRM data to check how many exception cases have an escalation flag vs. total cases in the >£500 implied range.

> **Unknown U-6: Are billing disputes and delivery exceptions tracked as separate CRM case types with distinct workflows, or do they land in a shared queue and get manually routed?**
> **Why it matters for agent design:** If cases are already typed at intake, the agent can apply work-stream-specific logic immediately. If all inbound contacts land in a shared queue and routing is manual, case classification becomes a first-step agent task — and the quality of that classification directly determines downstream handling quality.
> **How to discover it:** Ask to see a live CRM view of the incoming case queue. Ask: "When a new case comes in, is it already tagged by type or does an agent classify it?"

---

## 6. Assumption log

> **Assumption A-1:** Cases are distributed across the 35-person team from a shared queue, with some informal specialisation (e.g., Sandra W. primarily handles billing disputes based on the APEX_DISPUTES export showing her assigned to 3 of 6 open disputes).
> **Why it matters:** Affects how agent deployment is scoped — a shared-queue model supports a single agent across all work streams; a partitioned team suggests separate agent deployments or capability streams.
> **If wrong:** If the team is formally partitioned, the agent scope, access model, and change management plan each need to be designed per sub-team.
> **Confidence:** Medium — the scenario describes four work streams that "interlock and frequently cross-refer," implying shared handling, but the APEX_DISPUTES export shows consistent assignment patterns.

> **Assumption A-2:** The weekly volumes stated in the Points of Pain table are derived by multiplying the scenario's daily volumes by 5 working days. This is an approximation; actual volumes likely vary by day of week (higher on Mondays following weekend deliveries) and season.
> **Why it matters:** Weekly/monthly volume is used in ROI and capacity modelling. If the 5-day assumption is wrong (e.g., Apex operates 6 days, or volume spikes on specific days), the workload estimate changes.
> **If wrong:** Validate against actual CRM case volume reports covering a 4-week rolling period.
> **Confidence:** Medium — 5-day working week is the standard assumption for a UK carrier; Apex's actual operating pattern is not stated.

> **Assumption A-3:** The Artefact 2 example — credit applied with no audit log entry — represents a pattern, not a one-off. The informal credit bypass is a team-wide behaviour, not Sandra's individual deviation.
> **Why it matters:** If it is a team-wide pattern, the compliance gap is systemic and must be addressed at design level (the agent enforces the formal path). If it is an individual deviation, a lighter-touch intervention (training, reminders) might suffice.
> **If wrong:** If audit trail compliance is actually high and Artefact 2 is an outlier, the compliance metric in D0C overstates the problem and the agent's enforcement role is less critical.
> **Confidence:** Medium — domain-typical pattern (D0A identified this as a common lived/documented gap); one artefact is insufficient to confirm at population level.

> **Assumption A-4:** The "limited API surface" of the dispatch console means that programmatic read/write integration for WS3 is not currently feasible without platform or middleware investment — placing dispatch adjustment automation out of scope for an initial agent deployment.
> **Why it matters:** If this assumption holds, WS3 is scoped as structured intake + recommendation only, not autonomous execution. If the dispatch console has more API surface than stated, the scope and ROI for WS3 expand.
> **If wrong:** Any confirmed API endpoint on the dispatch console opens the possibility of automated route-change execution, changing the delegation archetype for WS3 from "human decision, agent support" to "agent recommendation, human confirm."
> **Confidence:** Medium — "limited API surface" is stated in the scenario; exact limitations unknown until technical discovery.
