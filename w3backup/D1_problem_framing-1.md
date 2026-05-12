# D1 — Problem Framing & Success Metrics
## MedFlex: Clinical Workforce Staffing Coordination

---

## 0. Executive summary

- MedFlex's 8 coordinators process ~960 shift-matching decisions per day entirely manually, producing a 4.2-hour average time-to-fill in a market where hospitals submit requests to multiple agencies simultaneously — the agency that responds first wins, meaning MedFlex systematically loses competitive placements to faster competitors before a coordinator can even begin matching.
- The current process cannot scale to the board's $200M revenue target because matching throughput is coupled to undocumented coordinator tacit knowledge: every placement decision depends on a mental model of individual nurse preferences and facility quirks that lives in coordinator heads, cannot be transferred, cannot be parallelised, and takes months to ramp in new hires — making a 14× revenue increase impossible with headcount-only growth.
- An agentic shift-matching system that autonomously processes intake, applies learned matching heuristics, and manages the confirmation loop will reduce average time-to-fill from 4.2 hours to under 1 hour, enabling the same coordinator team to supervise 3× current throughput within 8 weeks of deployment.

---

## 1. Table of contents

- [0. Executive summary](#0-executive-summary)
- [1. Table of contents](#1-table-of-contents)
- [2a. Problem statement — lived experience today](#2a-problem-statement--lived-experience-today)
- [2b. What is actually broken — root cause diagnosis](#2b-what-is-actually-broken--root-cause-diagnosis)
- [3. Why an AI agent — not traditional software, not RPA, not a process change](#3-why-an-ai-agent--not-traditional-software-not-rpa-not-a-process-change)
- [3b. What "10× without 10×-ing" requires architecturally](#3b-what-10-without-10ing-requires-architecturally)
- [4. What success looks like — by stakeholder](#4-what-success-looks-like--by-stakeholder)
- [5. Assumption log](#5-assumption-log)

---

## 2a. Problem statement — lived experience today

### 2a-i. MedFlex coordinators

Each of the 8 coordinators makes roughly 120 shift-matching decisions per day, every one of them manually. The process begins before matching even starts: shift requests arrive as unstructured free text inside ServiceNow, which means a coordinator must read, parse, and interpret every incoming request — inferring shift type, unit, required credentials, and timing from natural language before they can begin looking for a qualified nurse. Every minute spent parsing is a minute lost to the competitive window. Once matching begins, the coordinator is working from a mental model that is not in any system: knowledge of which nurse prefers certain facilities, which facilities are difficult to staff, which combinations of credentials and unit type tend to work — none of it is documented. This tacit knowledge is the coordinator's primary asset and also their primary constraint. When they multi-submit (the same nurse to multiple facilities simultaneously, which is standard practice under time pressure), they take on a withdrawal backlog: if more than one facility confirms before a rejection is processed, a coordinator must personally call to withdraw and manage the relationship friction. When a confirmed nurse does not show up, a coordinator learns about it via an unexpected hospital call — at shift start, after the remediation window has closed. The 12% no-show rate is not an abstract metric; it is 12 hospitals per 100 placements calling to say the nurse is not there, and a coordinator absorbing that call with no pre-shift warning system and no replacement already queued.

### 2a-ii. Hospitals

A hospital submitting a shift request to MedFlex is simultaneously submitting the same request to competing staffing agencies. They fill from the first qualified submission they receive. At MedFlex's current 4.2-hour average time-to-fill, the hospital has almost certainly received and evaluated submissions from faster competitors before a MedFlex coordinator has finished parsing the request. The facilities that stay with MedFlex do so for relationship reasons — nurse quality, reliability, account management — but those advantages erode when fill speed is consistently slower than alternatives. When a credential mismatch does reach the facility (the 7% rate), the hospital absorbs the operational consequence directly: the wrong-credentialed nurse either cannot be placed on the unit or triggers an internal credentialing review, creating an unplanned staffing gap and a compliance incident that may require documentation and escalation within the hospital's own processes. [Assumption: credential incidents require hospital-side documentation — not stated in scenario; see A-D1-3.] When a no-show occurs, the hospital calls MedFlex to report it — there is no proactive detection, and the staffing gap is already open at the time of the call. For a hospital depending on MedFlex for clinical coverage, a no-show without advance warning is a patient-safety adjacency risk, not just an inconvenience.

### 2a-iii. Nurses

A nurse receiving a placement notification from MedFlex gets an SMS or email and is considered confirmed unless they actively call to reject. If they miss the notification — a common scenario given that messages may arrive in a busy window — they are logged as having accepted a shift they did not knowingly agree to. The first they learn of the placement may be the day before the shift, if they happen to check their schedule, or at the shift itself when they either show up unexpectedly or do not appear and trigger a no-show. [Assumption: nurses experience missed-notification confirmations as a source of schedule conflicts and trust erosion with MedFlex — not directly stated in scenario; see A-D1-4.] The multi-submission model also creates a race condition from the nurse's perspective: a nurse who received and accepted a placement may later be withdrawn from it if a faster confirmation at a competing facility caused the coordinator to reallocate. The notification timing — typically 2–3 days in advance (DS-confirmed) — is adequate for simple planning but also leaves a 2–3 day window in which a better-paying opportunity at another hospital can appear. Travel nurses operate in a competitive market; when a higher-paying shift surfaces after they have passively "accepted" a MedFlex placement, some nurses take it — relying on the passive model's soft commitment to make the exit frictionless. From MedFlex's perspective this registers as a no-show; from the nurse's perspective it was a rational economic decision against a commitment they never explicitly made. Nurses with profile notes (facility restrictions, prior incidents, preference flags) may find themselves under- or over-offered if coordinator knowledge of those notes is not transferred consistently.

---

## 2b. What is actually broken — root cause diagnosis

> **Broken [B-1]: There is no machine-readable intake schema**
> **Symptom it produces:** Every shift fill begins with a manual text-parsing step. A coordinator reads free-text in ServiceNow, extracts the relevant parameters (shift type, unit, required credentials, timing, facility), and queues the request for matching — before any matching logic begins. This adds an irreducible manual delay to the front of every fill, and it cannot be delegated to a rules-based system because the text is unstructured.
> **Why it persists:** The prior chatbot failure established the ceiling on what MedFlex can ask hospitals to do differently. The lesson confirmed in discovery: requiring hospitals to submit via a structured form means asking them to change their behaviour for one of multiple agency relationships. Hospitals will not do it. The intake channel is not negotiable — MedFlex must accept unstructured input and process it on their side.
> **What fixing it would unlock:** If an agent can parse, classify, and structure intake in seconds upon receipt, the matching step can begin immediately. The intake-parsing bottleneck is removed from the critical path, and the time-to-fill clock starts counting from the moment a qualified nurse is submitted — not from the moment a coordinator reads the request.

> **Broken [B-2]: Matching quality is coupled to undocumented tacit knowledge**
> **Symptom it produces:** Each coordinator's matching decisions depend on a personal mental model of nurse preferences, facility quirks, DNR flags, and historical relationship context that exists nowhere in ServiceNow. A coordinator on leave cannot transfer their caseload without quality degradation. New coordinators take months to develop sufficient knowledge to make high-quality matches independently. At 8 coordinators for ~960 daily decisions, the knowledge is held by exactly 8 people, none of whom can be replaced quickly. The business model requires 14× revenue growth — which requires either 14× the coordinators (impossible given ramp time and cost) or externalising this knowledge into a system.
> **Why it persists:** Tacit knowledge has never been formally captured because it produces results at current scale. There is no incentive to document what already works until the scale constraint makes it unavoidable. The knowledge is also genuinely hard to elicit: coordinators may not be able to articulate their heuristics — they match by feel and pattern recognition developed over years, not by explicit rules.
> **What fixing it would unlock:** An agent that learns matching heuristics from historical placement data and outcome feedback can encode tacit knowledge in a queryable, scalable form. Coordinators transition from being the bottleneck (knowledge holders) to being exception handlers and quality reviewers — a model that can scale to any throughput without linear headcount growth.

> **Broken [B-3]: No-show drivers are invisible to MedFlex until shift start — and only one of the two is fixable by the agent**
> **Symptom it produces:** The 12% no-show rate has two confirmed root causes with different mechanics. **Cause 1 — notification failure:** a nurse who did not see the SMS/email is logged as confirmed; the passive model (silence = accepted) makes the commitment indistinguishable from genuine acceptance. **Cause 2 — wage competition:** a nurse consciously accepted a MedFlex placement but subsequently took a higher-paying shift elsewhere; the passive model's soft commitment made the exit frictionless. In both cases, no-shows are discovered exclusively via hospital call at shift start (DS-confirmed) — after the fill window has closed, the facility staffing gap is open, and pre-shift remediation is impossible.
> **Why it persists:** The passive model was adopted to minimise friction at acceptance — requiring explicit acknowledgement adds a step that may depress placement rates. The full cost of that choice (12% no-show rate; zero remediation window; hospital relationship damage) has never been traced back to the model design as a fixable failure point. The wage-competition cause has a separate structural driver: travel nurses operate in a competitive market where better-paying shifts appear in the same 2–3 day window that precedes most placements, and a passive commitment provides no contractual or social friction to leaving.
> **What fixing it would unlock:** These two causes require different interventions with different impact ceilings. **For notification-failure no-shows:** an active confirmation loop (explicit acknowledgement required within 24 hours of notification) converts this portion of no-shows into a detectable, actionable signal — nurses who do not respond trigger an automated re-fill before the shift window closes. **For wage-competition no-shows:** the confirmation loop cannot prevent a nurse from choosing better pay, but an agent monitoring pre-shift confirmation status can detect ambiguity earlier (e.g., a nurse who accepted but has not re-confirmed 24 hours out) and trigger a replacement queue proactively. The combined effect: no-shows stop being discovered at shift start. The split between the two causes is unquantified — the reduction in total no-show rate from these interventions cannot be precisely projected until the causes are disaggregated.

> **Broken [B-4]: Multi-submission race conditions are managed manually with no system-level controls**
> **Symptom it produces:** Coordinators submit the same nurse to multiple facilities simultaneously to hedge fill probability under time pressure. When multiple facilities confirm the same nurse before a withdrawal is processed, MedFlex must withdraw a confirmed placement and manage the facility relationship consequence. This introduces coordinator rework (manual withdrawal calls), relationship friction with the affected facility, and the risk of a failed placement that counted in a fill rate metric.
> **Why it persists:** Multi-submission is a rational response to two simultaneous pressures: competitive submission speed (B-1: no time to submit sequentially) and candidate scarcity (the best-qualified nurses are in high demand). The behaviour produces better fill rates than sequential submission despite the race condition risk. There is no system-level mechanism that automatically propagates a confirmation at one facility as a withdrawal at all others — the coordination is entirely manual.
> **What fixing it would unlock:** An agent that manages the full submission-and-withdrawal lifecycle atomically — confirm at one, immediately flag or withdraw from all others — eliminates the race condition without sacrificing fill probability. Facilities receive a definitive answer faster; nurses are not left in ambiguous multi-submitted state; coordinator rework from race-condition withdrawals is eliminated.

---

## 3. Why an AI agent — not traditional software, not RPA, not a process change

**Why not hire more coordinators:** The throughput constraint is not coordinator count — it is the speed and knowledge dependency of what each coordinator does. Doubling coordinator headcount doubles the tacit-knowledge problem and doubles the ramp time required to bring new coordinators to quality. Marcus Reyes stated the goal explicitly: "10x the business without 10x-ing the coordinators." Even if headcount scaling were desirable, achieving 14× revenue in 24 months is impossible given training ramp times — new coordinators take months to develop the matching knowledge required to work independently at quality. Headcount-only scaling also does not address the competitive speed problem: more coordinators matching slowly still lose placements to faster competitors.

**Why not RPA (robotic process automation):** RPA requires structured, deterministic inputs and rule-based logic. The core intake problem is unstructured free text — RPA cannot parse natural language, infer shift parameters, or handle variability in how different hospitals phrase their requests. The matching problem requires reasoning across multiple soft constraints simultaneously (nurse preference, facility reputation, tacit relationship history) — RPA can apply hard rules but cannot handle the exception-and-edge-case volume that accounts for a meaningful share of all matching decisions. RPA applied to the structured subset of the process would leave the hard cases — the ones most dependent on judgement — entirely manual.

**Why not a structured intake portal or rules-based matching engine:** Structured intake was the exact failure mode of the prior chatbot. Discovery confirmed the root cause: hospitals will not change their submission behaviour for one of multiple agency relationships. Any solution that requires hospitals to adopt a new intake form or portal replicates the same adoption failure. A rules-based matching engine was the prior recommendation engine failure — the root causes confirmed in discovery were (a) recommendations were not explainable, and coordinators could not trust output they could not verify; (b) coordinators perceived the system as a job threat and did not adopt it. A new rules-based engine addresses neither root cause: it still cannot match tacit-knowledge quality, it still produces outputs coordinators cannot audit, and it still positions the system as replacing coordinator judgment rather than augmenting it.

**Why not a process redesign with documentation and playbooks:** Knowledge externalisation through documentation projects is slow, incomplete, and never fully captures implicit judgment. Coordinators can articulate some of their heuristics but not all — the preference knowledge they hold was developed through hundreds of placements and is not fully recoverable through interviews and playbooks. Even a successful documentation project produces a static artefact that does not update as nurse preferences, facility relationships, and market conditions change. It also does not address intake parsing, confirmation loop management, or multi-submission race conditions.

**Why an AI agent:** The problem requires a system that can (a) parse unstructured natural language at intake with no hospital workflow change, (b) reason across multiple soft and hard constraints simultaneously to select a qualified nurse, (c) update its matching heuristics from placement outcome feedback so tacit knowledge is encoded and improves over time, (d) manage the confirmation loop proactively — not passively — to catch no-shows before the fill window closes, and (e) handle submission-and-withdrawal atomically to eliminate race conditions. These five capabilities are not independently sufficient — they must be integrated in a single decision-and-action loop. That is the AI agent design space. A system with explainable outputs and a visible human supervisor role addresses the prior failure modes directly.

---

## 3b. What "10× without 10×-ing" requires architecturally

The business targets in §4a are measurable outcomes. This section translates them into system-facing constraints — what the agent must be capable of for those outcomes to be achievable. These are not success metrics; they are build requirements.

**Constraint 1 — Intake-to-submission throughput: ≥3 cycles per minute during business hours**

At the 8-week target of 1,440 fills/day over an 8-hour primary work window, the system must complete intake-to-first-submission at ≥3 cycles per minute (1,440 ÷ 480 min). At the 24-month target of ~13,700/day, the rate rises to ~29 cycles per minute — physically impossible for a coordinator-reviewed workflow at every step. The architectural implication: coordinator involvement must be bounded to the exception rate, not total fill volume.

**Constraint 2 — First-submission latency: ≤15 minutes from intake receipt**

The <1 hour time-to-fill metric in §4a is a composite that includes matching, confirmation, and logistics. In the competitive placement market (DS-confirmed: hospitals award to the first qualified submission received), what determines win or loss is not fill time — it is first-submission time. A competitor who submits at 20 minutes wins the placement regardless of MedFlex's 58-minute result. The agent must complete intake parsing in <5 minutes and candidate selection and submission in <10 minutes of intake completion — total first-submission latency ≤15 minutes for standard fills. The 1-hour composite target is a client-facing SLA; the 15-minute first-submission target is the competitive survival requirement.

**Constraint 3 — Concurrent matching capacity: ≥8 threads at 8 weeks, scaling to ≥28 at 24 months**

Currently, 8 coordinators process ~120 matching decisions per day each, in parallel but sequentially within each coordinator's queue. At 1,440/day, the agent must support at minimum 8 simultaneous matching threads without one thread blocking another. At ~13,700/day, this scales to ~28 concurrent threads (13,700 ÷ 480 min ≈ 28.5 completions/min). At that concurrency, coordinator review of every match before submission is structurally impossible regardless of tool quality — the human review step becomes the bottleneck even if the agent is instant.

**Constraint 4 — Coordinator decoupling: the architectural test**

The three constraints above share a single structural implication: coordinator headcount must not be on the critical path for standard-fill throughput. A system where a coordinator approves every submission before it is sent is capped at 8 × 120 = 960 fills/day by coordinator cognitive capacity — regardless of agent speed. A system where coordinators supervise exceptions only can reach 1,440/day with the same team: if the agent handles 85% of fills autonomously and routes 15% to coordinators, the 8-week throughput target holds with 8 coordinators at ~135 exception reviews/day each (1,440 × 15% ÷ 8 ≈ 27 exceptions/coordinator — well within capacity). This is the architectural meaning of "10× without 10×-ing": the agent's autonomy rate, not coordinator headcount, is the throughput lever. Reaching 13,700/day requires an autonomy rate approaching 98% on standard fills, with coordinators managing a bounded exception queue — not reviewing volume.

---

## 4. What success looks like — by stakeholder

### 4a. Success for MedFlex

| Metric | Baseline (from scenario) | Target | How measured | Timeframe |
|--------|--------------------------|--------|--------------|-----------|
| Average time-to-fill | 4.2 hours | <1 hour | ServiceNow: case-creation timestamp to confirmed-placement timestamp, 30-day rolling average | 8 weeks post-deployment |
| Shift fills processed per day (total system throughput) | ~960 (derived: 8 coordinators × ~120 decisions — see A1 in scenario_context.md) | ≥1,440 (1.5× baseline) [A-D1-1] | ServiceNow: confirmed placements per calendar day, weekly average | 8 weeks post-deployment |
| Daily shift fills required to reach $200M revenue target | ~960/day at $14M revenue (derived) [A-D1-2] | ~13,700/day (derived: $200M ÷ ~$40 implied revenue/fill ÷ 365 days) [A-D1-2] | ServiceNow: confirmed placements per calendar day, annual average | 24 months (board target horizon) |
| Revenue per coordinator (annualised) | ~$1.75M (derived: $14M ÷ 8 coordinators) [A-D1-2] | ≥$12.5M per coordinator | Finance: annual gross revenue ÷ active coordinator headcount | 24 months (board target horizon) |
| Credential mismatch rate | 7% (stated) | ≤1% | Facility-reported credential mismatch incidents ÷ total confirmed placements, 30-day rolling | 8 weeks post-deployment |
| No-show rate | 12% composite (stated); notification-failure vs. wage-competition split unquantified [A-D1-4] | ≤8% composite; target to be refined once cause split is measured [A-D1-4] | Hospital-reported no-shows ÷ total confirmed placements, 30-day rolling; segmented by cause once active confirmation data exists | 8 weeks post-deployment |

### 4b. Success for the hospitals

| Metric | Baseline (from scenario or assumption) | Target | How measured | Timeframe |
|--------|----------------------------------------|--------|--------------|-----------|
| Time from shift request submission to first qualified nurse submitted to facility | ~4.2 hours (applying scenario time-to-fill as a proxy; does not distinguish first submission from final confirmation) [A-D1-3] | <1 hour | ServiceNow: request-received timestamp to nurse-submitted-to-facility timestamp, per placement | 8 weeks post-deployment |
| Credential mismatch incidents per 100 placements | ~7 per 100 placements (scenario mismatch rate applied to facility-facing experience) [A-D1-3] | <1 per 100 placements | Facility-reported mismatch incidents ÷ total placements × 100, monthly | 8 weeks post-deployment |
| No-show replacement response time (time from hospital no-show call to replacement nurse submitted) | Undefined — no proactive mechanism exists; current baseline is effectively unlimited [A-D1-4] | <2 hours from hospital notification | ServiceNow: no-show-reported timestamp to replacement-submitted timestamp, per incident | 8 weeks post-deployment |

### 4c. Success for the nurses

| Metric | Baseline (from scenario or assumption) | Target | How measured | Timeframe |
|--------|----------------------------------------|--------|--------------|-----------|
| Time from shift request intake to nurse notification of placement offer | Not stated in scenario; assumed ≥2 hours given 4.2-hour composite time-to-fill [A-D1-5] | <30 minutes from intake receipt | ServiceNow: intake-received timestamp to nurse-notification-sent timestamp, per placement | 8 weeks post-deployment |
| Confirmed-then-withdrawn placement rate (nurse confirmed at facility then removed due to race condition) | Not quantified; present due to multi-submission race condition [A-D1-6] | 0 confirmed-then-withdrawn placements per month | ServiceNow: placements with status sequence "confirmed → withdrawn" ÷ total confirmed placements, 30-day rolling | 8 weeks post-deployment |
| Active confirmation rate (explicit acknowledgement before shift, replacing passive silence-as-acceptance) | ~0% — currently all passive (DS-confirmed) | ≥90% explicit acknowledgement received before shift start | SMS/email confirmation system: explicit responses received ÷ total shift notifications sent, 30-day rolling | 8 weeks post-deployment |

---

## 5. Assumption log

> **Assumption [A-D1-1]:** A 1.5× throughput increase (960 → ≥1,440 fills per day) is achievable within 8 weeks if the agent handles ~30–40% of straightforward fills autonomously at initial deployment, with coordinators continuing to handle the remainder at current capacity. The 8-week target is an early-deployment milestone, not the ceiling — the longer-term goal (12+ months) is ≥3× (≥2,880/day) as the agent's automation rate increases toward ~70% of fills and coordinator throughput on the supervised portion improves with agent-assisted matching.
> **Why it matters:** This assumption underpins both the 8-week ROI case Marcus needs ("get my money back") and the longer-term capacity argument for the $200M revenue target. If the agent achieves <30% automation in the first 8 weeks, the 1.5× target is missed and the board's 24-month horizon comes into question.
> **If wrong:** If straightforward fills represent less than 30% of total volume (i.e., most fills require exception handling), the 8-week automation rate will be lower and the throughput target must be revised.
> **Confidence:** Medium — "straightforward fills" framing confirmed by Marcus in discovery; specific automation rate and proportion of straightforward fills not quantified in scenario.

> **Assumption [A-D1-2]:** The ~13,700 fills/day target is derived as follows: current revenue ($14M) ÷ current annual fills (~350,400: 960/day × 365) = ~$40 implied revenue per fill. $200M ÷ $40 ÷ 365 = ~13,700 fills/day. This assumes revenue per fill remains constant as MedFlex scales — the most conservative framing. Revenue per fill could increase (premium clients, better contract rates) or decrease (volume discounts), which would shift the required daily fill count proportionally. Even under the most optimistic scenario where revenue per fill doubles to $80, MedFlex still needs ~6,850 fills/day — 7× current capacity. Headcount-only scaling to 13,700/day would require ~114 coordinators at current productivity (13,700 ÷ 120), or ~57 coordinators if per-fill productivity doubles — neither is achievable in 24 months given training ramp times.
> **Why it matters:** This is the single most important number in the engagement. It makes the abstract $200M board target operational: MedFlex needs a system that can process 14× current daily fill volume with the same (or modestly larger) coordinator team. Every architectural decision flows from this constraint.
> **If wrong:** If revenue per fill increases significantly as MedFlex moves upmarket, the required fill count is lower — but the throughput challenge remains one that cannot be solved by headcount alone at any realistic revenue-per-fill assumption.
> **Confidence:** Medium — derived from two stated figures ($14M revenue; ~120 fills/coordinator/day); revenue-per-fill constancy is an assumption. The order of magnitude is robust even if the precise figure shifts.

> **Assumption [A-D1-3]:** The 7% mismatch rate and 4.2-hour time-to-fill are experienced by hospitals as the same metrics they use to evaluate MedFlex's performance relative to competing agencies. That is, the hospital uses fill speed and credential accuracy — not internal MedFlex metrics — to make agency preference decisions.
> **Why it matters:** If hospitals use different criteria (e.g., nurse quality scores, relationship tenure, rate competitiveness), the success metrics in 4b may not capture what would actually improve hospital retention and preference.
> **If wrong:** If hospitals weight nurse quality or pricing above fill speed, the time-to-fill reduction target is necessary but not sufficient for hospital success.
> **Confidence:** Medium — competitive submission dynamic confirmed in discovery (speed matters); relative weighting of speed vs. quality not directly resolved.

> **Assumption [A-D1-4]:** The 12% no-show rate has two confirmed root causes — notification-failure no-shows (nurse missed the passive SMS/email) and wage-competition no-shows (nurse accepted but took a higher-paying shift elsewhere) — but the split between them is not quantified. The composite ≤8% target in 4a assumes the active confirmation loop materially reduces notification-failure no-shows and that proactive pre-shift monitoring reduces wage-competition no-shows by enabling faster re-fills. The target will need to be revised once active confirmation data exists and causes can be disaggregated.
> **Why it matters:** If wage-competition is the dominant cause (e.g., >70% of the 12%), an active confirmation loop will move the composite rate only marginally. The agent's primary lever in that scenario is replacement speed — not confirmation design. Overstating the impact of a confirmation loop redesign would produce a false target and a missed success metric at 8 weeks.
> **If wrong:** If notification-failure is the dominant cause, the ≤8% target is conservative — the actual achievable reduction may be larger.
> **Confidence:** Low — both causes confirmed in discovery session; relative weighting not quantified.

> **Assumption [A-D1-5]:** The current time from intake receipt to nurse notification is at least 2 hours, given that the composite time-to-fill (4.2 hours) includes intake parsing, matching, and confirmation. The sub-30-minute target assumes agent-driven intake parsing is fast (<5 minutes) and agent-driven matching returns a candidate within 25 minutes of receipt.
> **Why it matters:** If matching itself (not intake) is the primary time driver, the notification time target requires solving the matching speed problem specifically — not just the intake parsing problem.
> **If wrong:** If coordinator matching for a standard fill already takes under 30 minutes and the 4.2-hour composite is driven by queue depth (volume of outstanding requests), the notification time target is already achievable and does not require agent-driven matching speed improvements.
> **Confidence:** Low — the 4.2-hour composite is not segmented by step in the scenario. Step-level timing was not resolved in discovery.

> **Assumption [A-D1-6]:** Nurses experience confirmed-then-withdrawn placements (due to multi-submission race conditions) as a source of schedule disruption and trust erosion, even if MedFlex's internal metrics do not track it as a nurse-facing failure. The 0 confirmed-then-withdrawn target requires the agent to handle withdrawal atomically — confirm at one facility, immediately remove from all others — before a nurse receives a confirmation she will later lose.
> **Why it matters:** If nurses experience frequent withdrawal-after-confirmation, they will reduce engagement with MedFlex placements over time. This is an adoption and retention risk that would compound with the job-security adoption risk already identified for coordinators.
> **If wrong:** If multi-submission withdrawal is transparent to nurses (they are not notified of the withdrawn submission, only the confirmed one), the nurse-facing metric is cosmetic — coordinators and facilities bear the consequence, not nurses.
> **Confidence:** Low — nurse-facing experience of multi-submission race conditions is not stated in the scenario. Raised as a concern, not a confirmed experience.
