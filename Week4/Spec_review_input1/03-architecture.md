# D3 — Agentic Solution Architecture

**Status: FINAL**

---

## Solution Overview

MedFlex's core bottleneck is coordinator cognitive capacity, not market demand. 8 coordinators performing ~960 shift-matching decisions per day across fragmented data sources is the ceiling on revenue growth. Removing that ceiling requires agents that act — not assistants that suggest. The architecture is designed against three D1 KPIs: fill time 4.2h → < 1h, ≥ 70% of routine matches confirmed autonomously by end of pilot, and 100% of partial matches disclosed explicitly from day one.

The MVP architecture is two LLM agents delivered sequentially. A scheduled automation script and a third agent are roadmap items for subsequent phases.

- **Intake Agent (WS4):** Reads incoming hospital shift requests from email, parses unstructured content into structured shift requirements, and writes records into the CRM. Prerequisite for the Matching Agent — structured input is required before matching can be automated.
- **Shift Matching Agent (WS1):** Receives structured shift requirements and reasons over credentials, availability, and prior placement history (as a fit signal) to produce a ranked shortlist. For routine matches meeting confidence criteria, confirms autonomously. For non-routine matches, surfaces the shortlist to the coordinator for confirmation. Structured preference inference is post-MVP — the feedback loop required to learn and apply explicit preferences does not exist today (D1).
- **Credential Compliance Automation (WS2, roadmap):** Scheduled script that monitors nurse credential expiry dates against state regulatory databases and flags lapses before they reach the matching pool. Not an LLM agent — the decision is binary and deterministic. The value is closing the undetected-lapse window that currently exists between quarterly manual checks.
- **No-Show Response Agent (WS3, roadmap):** Emergency re-match agent that triggers when a nurse no-show is detected at shift start. Reuses Matching Agent capability under time pressure. Depends on the Matching Agent being operational and coordinator trust established.

**Where agent reasoning determines outcomes a rule-based system cannot reach:**

In WS1, the matching decision requires simultaneous reasoning over credentials (structured), availability (fragmented, unreliable), and prior placement history (partially structured). A rule-based system can filter by credentials and availability. It cannot infer fit from prior placement patterns or recognise that a nurse who was a poor fit for a facility type last quarter is a poor fit again — even if all credentials check out. That contextual inference is the agent's mechanism. It is what distinguishes this from the failed recommendation engine Marcus described: that system applied rules and produced wrong results; this agent reasons over context. Structured preference inference is out of scope for MVP — the feedback loop to learn and apply explicit preferences does not exist today (D1).

In WS4, the value is narrower but still requires LLM capability: hospital shift requests arrive as unstructured natural language across email and messages. A regex parser handles clean templates; it fails on the edge cases that create manual coordinator work. The agent handles ambiguity in language and maps it to structured fields — the exact gap a rule-based parser cannot close.

---

## Agent Map

| Work stream | Type | Archetype | Agent does | Human retains |
|---|---|---|---|---|
| WS4 — Intake | LLM agent | Agent-led + Human Oversight | Parse email requests into structured CRM records; send email clarification requests for incomplete intakes; send hospital acknowledgement (conditional — pending Kim confirmation that this is in v1 scope); trigger WS1 handoff | Phone clarification calls for incomplete requests; phone intake (MVP); cancellation handling |
| WS1 — Shift Matching | LLM agent | Agent-led + Human Oversight | Reason over credentials + availability → ranked shortlist; explicit partial match flag in CRM record and hospital confirmation when no exact credential match exists; autonomous confirmation for routine matches; HIPAA-compliant audit log entry per decision; CRM escalation status update when shortlist exhausted | Coordinator picks up escalated requests from CRM queue |
| WS2 — Credential Compliance *(roadmap)* | Scheduled automation script | Human-led + Automation Support | Out of scope for MVP — current quarterly manual compliance process continues; automation deferred to subsequent phase | Compliance team owns credential monitoring in MVP |
| WS3 — No-Show Response *(roadmap)* | LLM agent | Agent-led + Human Oversight | Out of scope for MVP — coordinator fire drill process continues; agent deferred until Matching Agent is operational and coordinator trust established | Coordinator runs fire drill in MVP |

---

## Implementation Waves

**Wave 0 — Foundation (prerequisite, not a separate delivery)**
Nurse availability data consolidation into a single queryable source. CRM API and email integration confirmed with Aaron. Without this, WS1 matching accuracy cannot be guaranteed and WS4 CRM write is unbuildable. This is not a separate agent — it is the data infrastructure that enables Waves 1 and 2.

**Wave 1 — WS4 Intake Agent (prerequisite for WS1)**
Parse incoming hospital shift requests from email into structured CRM records. Removes the manual copy-paste step coordinators perform today. Hard prerequisite for WS1 — the matching agent cannot operate without structured input. Delivers visible coordinator time savings from day one.

**Wave 2 — WS1 Shift Matching Agent (primary value delivery)**
The primary KPI mover. Agent reasons over credentials and availability, proposes a ranked shortlist of top-N nurses (`NURSE_SHORTLIST_SIZE`), and initiates nurse contact within 5 minutes of shortlist generation — the D1 nurse KPI. Contact is initiated across the shortlist in parallel, not sequentially; sequential outreach cannot meet the fill time target at the volume MedFlex operates. When no exact credential match exists, the agent explicitly flags the partial match status in the CRM record and in the hospital confirmation — this is the Layer 3 mismatch improvement committed at MVP (D1). Escalates to coordinator queue via CRM status update when shortlist is exhausted. Fill time and autonomous match rate KPI movement begins here.

**Wave 3 — WS2 Credential Compliance Automation (data quality roadmap)**
Scheduled automation script that monitors nurse credential expiry against state regulatory databases and flags lapses before they reach the matching pool. Closes the quarterly detection gap that currently allows lapsed credentials to persist in WS1's candidate pool. Depends on state regulatory DB API confirmation (pending Aaron). Current manual compliance process continues until Wave 3.

**Wave 4 — WS3 No-Show Response Agent (operational resilience roadmap)**
No-show fire drill automation. Reuses WS1 matching capability under emergency conditions. Adds pre-shift nurse engagement monitoring to reduce competitor double-booking no-shows (confirmed discovery). Requires WS1 operational and coordinator trust established before deployment.

---

## System Flow

```
Hospital (external)
     │ shift request (email / phone)
     ▼
[Email Provider API]
     │ raw inbound email
     ▼
┌─────────────────────┐
│   Intake Agent      │──── acknowledgement email ────► Hospital
│   (WS4)             │
└─────────────────────┘
     │ structured shift record (CRM write)
     ▼
  [CRM]
     │ shift requirement record
     ▼
┌──────────────────────────┐◄── credential data (CRM)
│  Shift Matching Agent    │◄── availability data (CRM portal / coord spreadsheet / phone updates)
│  (WS1)                   │◄── placement history (CRM, partial)
└──────────────────────────┘
     │                 │                    │
     │ nurse contact   │ CRM status update  │ shortlist exhausted: escalation flag
     ▼                 ▼                    ▼
   Nurse             [CRM]         Coordinator queue (CRM)
     │                                      │
     │ acceptance                           ▼
     ▼                               Coordinator (exception handling)
[Shift Matching Agent]
     │ confirmation email ────► Hospital
     │ CRM status update ────► [CRM]
```

**Phone intake (MVP):** Coordinator-owned. Parsed manually into CRM; email channel is the automation target.
**Wave 0 prerequisite:** Nurse availability data must be consolidated into a single queryable source before WS1 matching accuracy can be guaranteed. This is not shown as an agent — it is the data infrastructure that enables Waves 1 and 2.
**HIPAA compliance requirement (D2 constraint):** Every WS1 match decision must produce a full audit log entry — timestamp, actor, data accessed, decision made, and CRM fields changed. PII fields must not be written to external log targets; audit records reference CRM record IDs only. This is a non-negotiable architectural requirement, not a post-build addition. Linda (compliance) owns the HIPAA audit requirement; confirm audit log destination and retention policy with Aaron and Linda before WS1 integration is built.
**Hospital confirmation acknowledgement [open item]:** The confirmation email arrow above is currently designed as a one-way notification. Whether hospitals explicitly acknowledge or accept the match — creating a pre-shift detection window for wrong confirmations — was not confirmed in discovery. If hospitals reliably acknowledge, a wrong autonomous confirmation is detectable before the shift and coordinator intervention is possible. If they do not, detection falls back to the post-shift satisfaction survey — the only mismatch signal that exists today (D2 confirmed: no real-time mismatch detection mechanism exists). The post-shift survey is lagging by shift duration plus survey return time; a wrong autonomous confirmation discovered this way cannot be corrected before the shift occurs. This must be confirmed with Kim before the autonomous confirmation failure path is finalised and before graduation to autonomous mode is approved.

---

## Why This Is AI-Native, Not AI-Featured

The defining question for an AI-native architecture is where agent reasoning determines an outcome a rule-based system cannot reach. There are two such points in this design.

**WS1 — the matching decision:** The agent must simultaneously reason over credentials (structured), availability (fragmented across three sources), and prior placement history (partially structured) to produce a fit inference. A rule-based system can filter by credentials and binary availability. It cannot infer fit from prior placement patterns or recognise that a nurse who was a poor match for a facility type last quarter is likely a poor match again — even if all credentials check out. That contextual inference is the agent mechanism. It is what the failed recommendation engine could not do: that system applied rules and produced wrong shortlists; this agent reasons over context. Structured preference inference — learning and applying explicit hospital and nurse preferences — is post-MVP; the feedback loop required does not exist today (D1).

**WS4 — intake parsing:** Narrower but still requires LLM capability. Hospital shift requests arrive as unstructured natural language in email. A regex parser handles clean templates and fails on edge cases — partial information, non-standard phrasing, ambiguous specialty descriptions — exactly the edge cases that currently create manual coordinator work. The agent maps ambiguous language to structured CRM fields. That gap is not closeable by a rule-based parser.

**WS3 — no-show response *(roadmap)*:** Reuses WS1 matching reasoning under emergency conditions. When a nurse no-show is detected at shift start, the agent must re-match against remaining availability and contact a replacement under time pressure. The reasoning requirement is identical to WS1 — contextual inference over credentials, availability, and fit — which is why the mechanism is the same. LLM capability is appropriate here for the same reasons as WS1.

**Where agent reasoning is not the mechanism:** WS2 (credential compliance) is a scheduled automation script. The decision — credential current or lapsed — is binary and deterministic. No LLM reasoning is needed or appropriate. Including an LLM here would be AI-as-a-feature, not AI-as-the-mechanism.

---

## How This Is Different From the Two Failed Projects

Marcus named two prior failures in discovery. They are not incidental context — they define the failure modes this architecture must avoid.

**Failure 1 — The chatbot:** Document retrieval with no inference. *"It was just referencing across docs and trying to find an answer... no inference that was really happening."* (Marcus Reyes, discovery session) The chatbot retrieved; it did not reason. Coordinators found no value in a system that surfaced documents they could look up themselves. The WS4 Intake Agent does not retrieve — it parses unstructured input and maps it to structured output, a task the chatbot mechanism could not perform.

**Failure 2 — The recommendation engine:** Rule application without nuance. *"The recommendations were mostly off despite we have spent quite some time to add some details to it."* (Marcus Reyes, discovery session) The engine ranked nurses by applying explicit rules. When the rules were incomplete or the matching criteria were tacit and unwritten, it produced wrong shortlists. The WS1 Matching Agent does not apply rules — it reasons over context. The distinction is concrete: the recommendation engine could not weight preferences against availability constraints or infer fit from placement history patterns. The Matching Agent can.

**The architectural implication:** Both failures share a root cause — the system mechanism did not match the task's actual reasoning requirements. This architecture is built against that failure: the agent mechanism (contextual inference) is used only where the task requires it; deterministic automation is used where the decision is binary. The Matching Agent is not a smarter rule engine. It is a different kind of system.

---

## ADR-1 — Primary Integration Path for Intake and Matching Agents

**Status: PENDING — decision requires IT confirmation of CRM API and email integration**

### Problem statement

The Intake Agent (WS4) must read incoming shift requests from email and write structured requirements into the CRM. The Matching Agent (WS1) must read those requirements and write match outcomes back. The integration path determines build complexity, failure modes, and the dependency chain for all downstream agents. This decision must be locked before D4a and D4b specs are finalised; an incorrect integration assumption produces an unbuildable spec.

The ambiguity comes directly from discovery: Marcus confirmed the internal system is a web portal with a request lifecycle, but when asked whether it integrates with email he said *"I am not sure about that, to be honest."* (Marcus Reyes, discovery session) API access was referenced as *"I think there is an API somewhere. I don't know where it is."* (Marcus Reyes, discovery session) Both route to Aaron in IT for confirmation.

### Options considered

**Option A — CRM-native integration**
Agents read and write the CRM via its own API; email intake is handled through the CRM's built-in email integration.
- Requires: CRM exposes an API AND CRM has email integration (both unconfirmed)
- Consequences: single integration point; simplest build; no separate email provider API needed
- Risk: if email is not CRM-integrated, Option A collapses to Option C at build time — late-stage integration rework

**Option B — Email-first integration**
Agent reads email directly via email provider API (Gmail or Outlook); parses intake independently; writes structured output to CRM via a separate CRM write API.
- Requires: email provider API access AND CRM write API (both pending IT confirmation)
- Consequences: two independent integration points; email APIs are well-documented and stable; agent owns the parsing layer fully
- Risk: higher initial build complexity; requires IT coordination on email provider access

**Option C — Hybrid (email-direct + CRM write API, no CRM email integration)**
Agent reads email via email provider API; CRM exposes a write API but has no email integration. Two integrations required by design.
- Requires: email provider API + CRM write API (same as Option B)
- Consequences: most likely to reflect real infrastructure given Marcus's uncertainty about CRM email integration; designing for this avoids a false assumption that breaks at build time; phone intake channel remains coordinator-handled in MVP regardless of option
- Risk: most complex of the three

### Chosen option

**Decision pending IT confirmation (Aaron).**

Working default: **Option C (Hybrid)**. Most defensible given uncertainty about CRM email integration. Designing for Option C means the build does not break if IT confirms no CRM email integration. If Aaron confirms full CRM email integration, the email provider integration layer is removed — a simplification, not a rework.

### Revisability

- If Aaron confirms CRM email integration → move to Option A; remove email provider API from D4a spec
- If CRM has no API at all → full architecture replanning required; WS4 and WS1 agent scopes change materially

---

## ADR-2 — WS1 Autonomy Model: Agent-Confirms vs. Agent-Proposes in MVP

### Problem statement

Marcus's explicit requirement is that the agent removes coordinator tasks rather than assists them: *"Something that involves them all the time is quite futile for us."* (Marcus Reyes, discovery session) The strongest interpretation of this is a fully autonomous matching agent that confirms nurses without coordinator review. However, two constraints push back against full autonomy in MVP: fragmented availability data (no single source of truth — accuracy cannot be guaranteed at launch) and unknown coordinator tolerance for agent-autonomous decisions. Choosing the wrong autonomy model in MVP either fails Marcus's requirement (too conservative) or destroys coordinator trust early and makes the pilot unrecoverable (too aggressive).

### Options considered

**Option A — Agent-confirms (fully autonomous for routine matches)**
Agent confirms nurse to hospital and updates CRM without coordinator review for matches meeting a defined confidence threshold. Coordinator is notified post-confirmation, not pre-confirmation.
- Requires: availability data consolidated and reliable; confidence scoring model validated on historical data; coordinator trust established
- Consequences: directly meets Marcus's stated expectation; maximum fill time reduction; coordinators are freed from routine decision load
- Risk: if data quality is lower than assumed at launch, the agent makes confident wrong matches. A wrong autonomous match that a coordinator would have caught erodes trust faster than no automation at all. Recovery from a failed pilot is harder than a phased ramp.

**Option B — Agent-proposes, coordinator confirms (human-in-the-loop)**
Agent produces a ranked shortlist with reasoning; coordinator confirms the top match or selects an alternative. Agent handles data retrieval, ranking, and communication scaffolding; coordinator retains the final decision.
- Requires: CRM integration to surface the shortlist to coordinator; coordinator review workflow
- Consequences: lower fill time reduction than Option A (coordinator confirmation adds latency); higher safety margin; builds coordinator trust before autonomy is expanded; coordinator can observe and calibrate agent behaviour
- Risk: does not deliver Marcus's stated vision in MVP; risks being labelled "just a better tool, not an agent" if coordinator time savings are not visible

**Option C — Graduated autonomy (Option B at launch, ramp to Option A)**
Launch with Option B. Define explicit graduation criteria (match accuracy ≥X%, coordinator override rate ≤Y%, availability data quality confirmed). Autonomy expands to Option A when criteria are met — without a new build cycle.
- Requires: graduation criteria agreed with Marcus and coordinators before launch; accuracy tracking instrumented from day one
- Consequences: mitigates the risk of early trust failure; gives coordinators visibility into agent behaviour before control is removed; creates a concrete milestone Marcus can track; autonomy expansion is a setting change, not a redeployment
- Risk: graduation criteria must be negotiated and agreed — if criteria are set too conservatively, the agent stays in proposal mode indefinitely

### Chosen option

**Option C — Graduated autonomy.**

The data gaps at MVP launch (availability fragmentation, unvalidated confidence model, unknown coordinator tolerance) make full autonomy from day one a trust risk that outweighs the fill time benefit. Option B alone risks failing Marcus's stated requirement. Option C is the only path that is honest about both constraints: it delivers visible coordinator time savings from day one, names a concrete graduation milestone, and does not require a rebuild to reach full autonomy.

The graduation criteria — match accuracy threshold, coordinator override rate, and availability data quality confirmation — must be agreed with Marcus and Kim before the pilot begins. These criteria are the measurable progress signal Marcus asked for.

### Revisability

- If Kim confirms coordinator resistance is low and availability data consolidation completes before launch → reconsider accelerating to Option A sooner
- If graduation criteria are not met within pilot window → extend Option B; do not force autonomy expansion on a deadline

---

## ADR-3 — WS2 Credential Compliance Automation: MVP vs. Roadmap

### Problem statement

The Matching Agent's credential filtering is only as accurate as the credential data in the CRM. Without credential compliance automation, the quarterly compliance gap remains open: a nurse's credential can lapse between quarterly checks and persist undetected in the matching pool. The Matching Agent will match against this stale data with full confidence. Including WS2 in MVP closes this gap at launch but extends the timeline, adds build complexity, and introduces a dependency on the state regulatory database API — which is unconfirmed at this stage. Excluding WS2 means shipping WS1 with a known credential accuracy limitation.

### Options considered

**Option A — Include WS2 in MVP (WS4 + WS1 + WS2)**
Build the credential compliance automation script alongside the two agents within the 8-week window.
- Requires: state regulatory DB API confirmed (currently low confidence); compliance team workflow confirmed with Linda; builds in parallel with WS4 and WS1
- Consequences: WS1 launches with clean credential data; mismatch rate improvement from credential accuracy visible from day one; stronger "why this is different" claim to Marcus
- Risk: 8-week window is tight for three work streams; state regulatory DB API unconfirmed (pending Aaron) — if Aaron cannot confirm the API, WS2 build stalls and risks blocking the MVP timeline

**Option B — Exclude WS2, roadmap for Wave 3**
Deliver WS4 + WS1 only. Current quarterly manual compliance process continues. WS2 ships as a Wave 3 data quality improvement.
- Requires: nothing additional beyond MVP scope
- Consequences: WS1 launches with current credential data quality; quarterly lapse gap remains open until Wave 3; credential-related mismatch rate improvement is deferred; WS1 fills faster but not necessarily more accurately on credentials
- Risk: Marcus may challenge why the credential problem is not addressed if the 7% mismatch rate is part of the value claim; must be communicated as a phased improvement, not an oversight

### Chosen option

**Option B — WS2 is a roadmap item (Wave 3).**

The 8-week window is the binding constraint. WS4 and WS1 together are the primary KPI movers (fill time, revenue). Adding WS2 introduces an unconfirmed state regulatory DB API dependency (pending Aaron) that could stall the entire MVP timeline if access cannot be confirmed. The current compliance process is known and functional — relying on it in MVP is a risk-managed decision, not a quality failure. WS2 ships in Wave 3 and improves the Matching Agent's credential accuracy as a measurable second-phase outcome.

The credential accuracy limitation must be communicated to Marcus explicitly: the Matching Agent matches on credentials that are current as of the last quarterly compliance check. Lapse detection between cycles remains manual until Wave 3.

### Revisability

- If Aaron confirms state regulatory DB API before the build starts and timeline allows → reconsider pulling WS2 into MVP as a parallel track
- If credential-related mismatch rate proves higher than expected after WS1 launch → accelerate Wave 3 ahead of schedule
