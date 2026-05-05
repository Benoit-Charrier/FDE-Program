# D6 — Discovery Questions
**Helix Workforce Software — Contract Classifier Agent**
**Produced:** 2026-05-04 | **Stakeholder:** Amelia Forsythe, General Counsel | **Status:** Draft — awaiting FDE approval

---

## 0. Executive Summary

- **Most design-critical unknown:** Whether Tom can articulate the 3–5 signals that drive his WS2 vs. WS3 routing decision — if he can, those signals become the codified escalation criteria that unlock the agent's routing logic from its conservative over-escalation default; if he cannot, the pre-deployment criteria workshop is longer and the initial deployment must use a restricted scope.
- **Governance question that must be resolved before any build decision:** What the named-lawyer sign-off action looks like in the Ironclad system — specifically whether it is a recorded system event with an attributed user and timestamp, or whether it currently happens outside Ironclad (email, verbal) and therefore has no technical enforcement point that the agent's hard stop can bind to.
- **Most likely dealbreaker:** Whether Ironclad allows a custom field to store the agent's deviation report JSON payload — if Ironclad's configuration is locked and no custom fields can be added, the agent's output has no system of record in the CLM, and either a separate database must be introduced or the entire integration architecture changes.

---

## 0b. Table of Contents

- [0. Executive Summary](#0-executive-summary)
- [0b. Table of Contents](#0b-table-of-contents)
- [1. Stakeholder Context](#1-stakeholder-context)
- [2. Questions Whose Answers Would Change the Design](#2-questions-whose-answers-would-change-the-design)
- [3. Questions Not Asked — and Why](#3-questions-not-asked--and-why)
- [4. Sequencing for a 60-Minute Discovery Call](#4-sequencing-for-a-60-minute-discovery-call)

---

## 1. Stakeholder Context

Amelia Forsythe has been General Counsel at Helix for 12 years — long enough to have built the governance framework the team operates within, including the named-lawyer sign-off rule that is the architectural non-negotiable for this agent. Her primary pressure right now is not operational efficiency for its own sake: the CRO is framing the 4–6 day turnaround as incompatible with enterprise sales velocity, which means Legal is being asked to change at a pace set by a commercial function rather than at Amelia's preferred cadence. Her concern about AI involvement will not be abstract ("AI makes mistakes") — it will be specific to accountability: if an agent misclassifies a clause and a commercially disadvantageous counteroffer goes out under a named lawyer's sign-off, where does the professional and legal responsibility land? The DPA section being stale (Artefact 2.3) under her watch, and Tom's informal escalation judgment call (Artefact 2.1) going undetected until this assessment, tell us that Amelia's oversight of WS1 is currently thin. She is likely aware that the current process has compliance gaps, which may make her more receptive to a structured agent design than a GC with a tightly controlled process — but her trust threshold for the agent's output will be anchored to whether she can inspect, override, and audit every material decision the agent contributes to.

---

## 2. Questions Whose Answers Would Change the Design

---

### Category A: Reference Material — Structure, Authority, and Machine-Readability

---

> **Q1: Is "Position Statements v3.4" stored in SharePoint as a Word document, an HTML SharePoint page, or a PDF — and is the text directly extractable, or are any sections embedded as images or tables that would not survive text extraction?**
> **Category:** A — Reference material
> **What I already infer from the scenario:** The playbook exists, is hosted on SharePoint, is titled "Position Statements v3.4," was last revised 9 months ago, and has a known-stale DPA section. I do not know the file format or whether it is machine-readable.
> **If the answer is [Word doc or HTML with extractable text]:** The SharePoint integration (T-5) is straightforward — retrieve the document, extract text per section, load into cache. The retrieval architecture is as designed in D5 §5.
> **If the answer is [PDF with embedded tables, or any section as an image]:** T-5 is blocked for those sections; an OCR pre-processing pipeline is required, or those sections must be manually converted to plain text as a pre-deployment prerequisite. Changes the D5 Gap G-2 mitigation from "straightforward API retrieval" to "format conversion work item before build."
> **Why this matters more than a generic question:** The entire clause comparison pipeline (T-6, T-7) depends on the playbook being text-readable by the agent; a single section stored as an image would silently disable classification for that clause type.

---

> **Q2: When the DPA section update is done — who actually writes it, how is it version-controlled in SharePoint, and how will downstream consumers (including Tom) know the version has changed?**
> **Category:** A — Reference material
> **What I already infer from the scenario:** The DPA section has not been updated since the DPDI Act Q1 revisions; Amelia discussed it with Sarah in March; it has not been actioned. I do not know whether Amelia writes the playbook herself, whether there is a version-numbering convention in SharePoint, or how Tom is notified of changes.
> **If the answer is [Amelia or Sarah writes it directly in SharePoint; version number increments in the document title; Tom is notified by email]:** The agent can implement a playbook version hash check at startup (D5 §5 context engineering risk 3); when the hash changes, the agent pauses and prompts revalidation. Straightforward.
> **If the answer is [Ad hoc — updates are made without a structured versioning process; Tom finds out when he notices a change]:** The agent cannot rely on version metadata to detect playbook updates. A more robust mechanism is needed: either the agent operator must manually trigger revalidation after any SharePoint edit, or a Change Notification API subscription (Microsoft Graph) must be implemented to detect edits. This adds engineering complexity and a new integration dependency.
> **Why this matters more than a generic question:** The DPA update is imminent and the agent cannot be safely deployed on DPA clauses until it is complete; how the update propagates determines whether the agent will silently continue using stale content after the update or will correctly detect the change.

---

> **Q3: Does the playbook include substitute clause language — ready-to-insert redline text for standard deviations — or does it only state the position (what Helix wants, not how to phrase it in contractual language)?**
> **Category:** A — Reference material
> **What I already infer from the scenario:** The playbook is described as "position statements" — the name implies positional guidance rather than substitute language, but does not confirm the absence of drafting templates. This was flagged as Assumption A-2 in D2.
> **If the answer is [yes, substitute clause language exists for at least the most common deviation types]:** D2 C-4 (standard-deviation redlining) moves from Conditional Agent-led to Confirmed Agent-led; Decision Determinism rises from M to H; the WS2 agent's scope expands and the build case for a second agent strengthens significantly.
> **If the answer is [no, position statements only — no substitute language]:** The WS2 agent (C-4) must generate redline language from a position statement, which requires lawyer review of every draft output and limits the delegation archetype to Human-led + Agent Support. The current assessment is correct; no design change needed for the Contract Classifier Agent specifically, but the roadmap for WS2 is much longer.
> **Why this matters more than a generic question:** The answer bifurcates the entire WS2 agent roadmap — substitute language means a 3-month build; position-statements-only means a much more complex generation problem requiring deeper legal review at every step.

---

### Category B: Core Decision Logic — How the Primary Classification or Routing Actually Works Today

---

> **Q4: When Tom is looking at a flagged clause and deciding between WS2 (he handles it) and WS3 (it needs a lawyer) — what are the 3 to 5 specific signals he is actually checking, in the order he checks them?**
> **Category:** B — Core decision logic
> **What I already infer from the scenario:** Tom makes this decision informally and the criteria are undocumented (Artefact 2.1 — he classified a £50k liability cap deviation as "borderline negotiable, not escalation"). I do not know what signals he uses beyond that one data point.
> **If the answer is [Tom can articulate 3–5 specific, concrete signals — e.g., "if the liability cap is below £100k I escalate; if it's just missing the standard SLA language I handle it myself"]:** Those signals become the escalation criteria document. D4 §5 routing decision criteria can be populated with specific, testable rules. The conservative default in T-9 is replaced with explicit logic. This is the fastest path to production-quality routing.
> **If the answer is [Tom cannot articulate the signals clearly — "it depends on the contract, I use my judgment"]:** The escalation criteria document requires more work: a workshop with real cases, possibly with Sarah to triangulate. The conservative default remains active for longer. The agent's initial deployment is restricted to NRR confirmation only until criteria are codified.
> **Why this matters more than a generic question:** This is the most design-critical question in the document — the routing criteria document is the single biggest pre-deployment prerequisite for the agent, and Amelia's answer determines how long it will take to produce it.

---

> **Q5: Of the roughly 70% of contracts that end up as No Redline Required — does Tom read the full contract before reaching that conclusion, or does he have heuristics that let him confirm NRR without reading every clause?**
> **Category:** B — Core decision logic
> **What I already infer from the scenario:** Tom spends ~25 min per case on WS1. The 70% NRR cases presumably take less time than the 30% with deviations, but the scenario gives a single average time across all cases. I do not know how Tom approaches NRR confirmation.
> **If the answer is [Tom has heuristics — e.g., "if it's from Vendor X on their standard paper, it's always NRR; I scan the liability and DPA sections only"]:** These heuristics should be built into the agent's pre-classification triage as a confidence booster. The ~25 min baseline may be inflated by the absence of such a triage step; actual time for NRR confirmation with the heuristic may already be < 8 min. Design implication: add a "vendor-level prior" signal to T-9 routing if historical data is available.
> **If the answer is [Tom reads the full contract for every case regardless of expected outcome]:** The 25 min baseline is genuine reading time, not a heuristic shortcut. The agent's value is straightforwardly replacing full reading with a structured report. No additional pre-triage signal needed in the design.
> **Why this matters more than a generic question:** If Tom has vendor-level heuristics that are currently invisible, not incorporating them into the agent would produce a system that performs worse than Tom on those vendor relationships and erodes his trust.

---

> **Q6: In the ~10% of cases that escalate to WS3 — what is the most common reason a clause is "unusual" enough to require senior-lawyer review? Is it primarily magnitude (the deviation is too large), type (certain clause categories always escalate regardless of size), novelty (formulation we have not seen before), or a combination?**
> **Category:** B — Core decision logic
> **What I already infer from the scenario:** 10% of 300 = ~30 cases/quarter escalate. Artefact 2.1 shows a magnitude-driven borderline (liability cap value). I do not know whether most escalations are magnitude-driven, type-driven, or novelty-driven.
> **If the answer is [primarily magnitude and type — most WS3 cases are recognisable patterns just beyond a threshold]:** The agent can handle the majority of WS3 classification deterministically: compare magnitude against a floor, check clause type against a WS3-mandatory list. The residual "true novelty" cases are a small fraction that the conservative default handles safely.
> **If the answer is [primarily novelty — most WS3 cases involve clause formulations the team has not seen before]:** The agent's T-7 DEVIATION_ESCALATION classification must rely heavily on the low-confidence path (confidence < 0.85 → escalate), not on deterministic threshold rules. The routing logic becomes more conservative and the HITL escalation rate rises. The agent's primary value in WS1 shifts from accurate routing to fast report generation, with Tom doing more routing confirmation than initially estimated.
> **Why this matters more than a generic question:** The answer sets the expected HITL rate for routing confirmations and determines whether the 20% target in D4 §3 is achievable or needs to be revised upward before build.

---

### Category C: Governance and Approval Constraint — Exactly How It Operates

---

> **Q7: When a named lawyer signs off on a counteroffer today, what does that action look like in the system? Is it a specific workflow step in Ironclad that creates a logged event with the lawyer's name and a timestamp — or does it currently happen outside Ironclad (e.g., email approval, verbal sign-off, lawyer sends the document directly)?**
> **Category:** C — Governance and approval constraint
> **What I already infer from the scenario:** The hard rule exists ("no counteroffer may leave Legal's queue without a named lawyer's sign-off") and Amelia owns it. The scenario does not describe the mechanical implementation of the sign-off step in Ironclad or otherwise.
> **If the answer is [Ironclad workflow step — the counteroffer cannot advance to dispatch without a named lawyer's approval action in the CLM, logged with identity and timestamp]:** The governance gate is technically enforceable at the system level. The agent's hard stop (D4 §8) can be implemented by ensuring the agent's API token does not have the ability to trigger the workflow step that currently requires a human click. Strong design position.
> **If the answer is [outside Ironclad — email, verbal, or the lawyer reviews a Word document and tells Tom to send]:** There is no current technical enforcement point. The agent cannot bind its hard stop to a system event that does not exist. Before deployment, the sign-off must be formalised as a recorded system action in Ironclad; the agent build is partially gated on this process change, which requires Amelia's sponsorship and Ironclad admin time.
> **Why this matters more than a generic question:** This is the single governance question that determines whether the hard constraint is architecturally enforceable in the current system state or requires a process change as a pre-build prerequisite.

---

> **Q8: Has the named-lawyer sign-off rule ever been bypassed in practice — for example, a lawyer verbally approving a counteroffer that Tom then sent without a recorded sign-off, or a contract going out during a period when Amelia was the only available approver and was unavailable?**
> **Category:** C — Governance and approval constraint
> **What I already infer from the scenario:** The rule is stated as absolute ("no counteroffer may leave Legal's queue without a named lawyer's sign-off") and Amelia owns it personally. I do not know if it has ever been informally waived.
> **If the answer is [no — the rule has never been bypassed; the team treats it as genuinely non-negotiable]:** The current policy discipline is strong. The agent's hard stop aligns with existing culture. The primary risk is technical (the enforcement mechanism), not cultural.
> **If the answer is [yes — there have been exceptions under pressure, especially at quarter-end]:** The governance risk is both cultural and technical. The agent's hard stop must be more robustly enforced at the system level (not just policy-dependent) because the team's culture already tolerates informal waiver. D4 FM-2 (under-escalation) has a compounding risk: the agent misroutes AND the sign-off pressure at quarter-end creates a second bypass opportunity. The design must include a circuit-breaker: if routing confirmation is pending for more than N hours, escalate to Amelia directly rather than allowing the case to time out into a default state.
> **Why this matters more than a generic question:** If the rule has been waived before, the agent's governance architecture must be designed to be bypass-resistant — not just well-intentioned — because the same pressure that caused prior bypasses will be applied to the agent-assisted process.

---

> **Q9: Is Amelia's named-lawyer sign-off rule the same for WS2 (standard deviations) as for WS3 (escalated clauses) — or is there a tier where a commercial lawyer's sign-off suffices for WS2 and only Amelia herself signs off on WS3?**
> **Category:** C — Governance and approval constraint
> **What I already infer from the scenario:** The rule states "named lawyer's sign-off" — which implies any named lawyer, not specifically Amelia. The scenario does not clarify whether WS2 and WS3 have different approval authority tiers.
> **If the answer is [any named lawyer for both WS2 and WS3 — one sign-off tier]:** The current design is correct. C-7 is Human Only for all counteroffers regardless of tier; the agent's routing confirmation gate (C-3) does not need to distinguish sign-off authority levels.
> **If the answer is [commercial lawyer for WS2; Amelia personally for WS3]:** The routing confirmation gate must capture tier-specific sign-off routing: WS2 cases go to a commercial lawyer's approval queue; WS3 cases go to Amelia's queue. The Ironclad workflow must have two distinct approval queues. If Amelia is the sole WS3 approver, her capacity is the WS3 bottleneck — at 30 cases/quarter, that is roughly 1.5 cases/week requiring Amelia's personal review, which is likely manageable but must be confirmed.
> **Why this matters more than a generic question:** Tier-specific sign-off authority changes the Ironclad workflow configuration, the routing trigger in T-11, and the accountability structure for D4 FM-2 (under-escalation consequences differ depending on whether a WS3 case that was mis-routed to WS2 received only a commercial lawyer's sign-off or Amelia's).

---

### Category D: Exception Patterns and Escalation Triggers

---

> **Q10: Looking at Artefact 2.1 — the case where Tom classified a £50k liability cap (vs. the playbook floor of £250k) as "borderline negotiable, not escalation" — if you had reviewed that case at the time, would you have agreed with Tom's routing, or would you have escalated it to WS3?**
> **Category:** D — Exception patterns and escalation triggers
> **What I already infer from the scenario:** Tom made an informal judgment call that the deviation was "borderline negotiable." The scenario flags this as evidence that escalation criteria are undocumented. I do not know whether Amelia would agree or disagree with Tom's call.
> **If the answer is [I would have agreed — a £50k cap from a small vendor in a low-risk deal context is negotiable without senior review]:** Tom's judgment is calibrated approximately correctly, and the conservative default (any cap below £250k → WS3) in D4 §5 will over-escalate. The escalation criteria document should capture deal-value context as a modifier (lower escalation threshold for low-contract-value deals), which requires access to Salesforce deal data — currently out of scope. Design implication: either bring Salesforce deal value into scope (complexity increase) or accept controlled over-escalation on small deals.
> **If the answer is [I would have escalated it — a cap 80% below the playbook floor is always WS3 regardless of deal context]:** Tom's informal judgment was wrong, and the conservative default is correct. The escalation criteria document is straightforward: any liability cap below the playbook floor → WS3. No deal-context modifier needed. Design is confirmed as-is.
> **Why this matters more than a generic question:** This specific case is the primary evidence for under-escalation risk (FM-2 in D4); Amelia's answer either confirms or challenges the severity of that risk and determines whether deal value must enter the routing logic.

---

> **Q11: Are there recurring clause types or vendor behaviours that Tom and the team recognise immediately as "this will always escalate" — patterns that appear regularly enough to be worth codifying but have never been formally added to the playbook?**
> **Category:** D — Exception patterns and escalation triggers
> **What I already infer from the scenario:** The 10% escalation rate is described as contracts with "unusual clauses requiring senior-lawyer review." The scenario does not describe what "unusual" looks like in practice. Tom's informal handling suggests some patterns exist that are not playbook-codified.
> **If the answer is [yes — Tom and the lawyers can name 3–5 patterns: e.g., "any contract that modifies IP ownership of work-for-hire deliverables always goes to WS3; any contract with a mutual NDA that restricts Helix's sales territory goes to WS3"]:** These patterns become immediate entries in the escalation criteria document. They reduce the "novelty-driven" fraction of WS3 cases and increase the fraction that the agent can classify deterministically. The initial deployment can target these patterns first.
> **If the answer is [no — each escalation is genuinely unique and no patterns have been observed]:** The WS3 classification problem is harder than assumed. The agent's conservative default (confidence < 0.85 → DEVIATION_ESCALATION) is the primary mechanism and the HITL rate will be higher in the initial deployment. A retrospective analysis of historical Ironclad cases (if available) may surface patterns that are not visible to Tom consciously.
> **Why this matters more than a generic question:** Naming 3–5 recurring patterns in this call immediately reduces the escalation criteria workshop from a blank-sheet exercise to a confirmation exercise, cutting preparation time before deployment.

---

> **Q12: When a WS3 case is completed — does the team record what the unusual clause was, why it was escalated, and what the final counteroffer position was? And if so, is that record searchable by future reviewers handling similar cases?**
> **Category:** D — Exception patterns and escalation triggers
> **What I already infer from the scenario:** Ironclad is used as the CLM but the scenario does not describe what case fields or notes exist for completed escalations. The enriched scenario does not mention any case history or precedent access mechanism.
> **If the answer is [yes — the reasoning and outcome are recorded in structured Ironclad case fields, searchable by clause type and counterparty]:** Historical WS3 records are a high-value reference dataset. The agent can use them to calibrate the DEVIATION_ESCALATION confidence threshold against real outcomes and to surface precedents when a similar clause type appears ("in prior case [ID], this formulation was escalated and the final position was X"). This changes the retrieval architecture: in addition to playbook retrieval (T-5), the agent performs a precedent lookup from Ironclad history (new T-5b task not currently in scope).
> **If the answer is [no — escalation reasoning is in email threads or lawyer notes not systematically captured; there is no queryable case history]:** Historical calibration data is not available. The agent's routing accuracy must be validated on a prospective sample, not a historical one. The precedent-lookup capability is not feasible at launch; it becomes a future enhancement pending a data collection phase.
> **Why this matters more than a generic question:** Available historical case data changes both the validation timeline (weeks vs. months) and whether a precedent-retrieval capability is in scope for v1.

---

### Category E: Data and System Reality

---

> **Q13: For contracts that arrive by email and bypass Ironclad's standard intake — does Tom eventually create an Ironclad case record for all of them, or are some of those contracts processed and executed without ever appearing in Ironclad?**
> **Category:** E — Data and system reality
> **What I already infer from the scenario:** Artefact 2.2 confirms email bypass as a recurring pattern (at least 3 vendors per quarter). Tom's note to Amelia treats it as an operational exception but does not confirm whether Ironclad records are eventually created for those cases.
> **If the answer is [Tom always creates an Ironclad record eventually, even for email-bypass cases]:** Ironclad is the authoritative record for all 300 cases/quarter. The agent's coverage metric (cases processed / total cases) is auditable entirely through Ironclad logs. The email-bypass flag in the intake record (D4 §5) captures the exception without creating a data gap.
> **If the answer is [some email-bypass contracts are never logged in Ironclad — processed and executed entirely via email and Word documents]:** The baseline volume (300/quarter) may be under-counted, and the agent's coverage metric will systematically miss a fraction of contracts. More critically, those contracts are being executed without any CLM oversight, which is both a compliance risk and a scope question: should the agent's intake monitoring extend to Tom's personal inbox (higher complexity) or should Amelia require all vendors to use the standard channel before the agent is deployed?
> **Why this matters more than a generic question:** If a material fraction of contracts never reach Ironclad, the agent's coverage KPI (D4 §3) is measuring the wrong denominator, and the compliance risk is larger than the scenario currently implies.

---

> **Q14: Can the Ironclad admin create a custom field on vendor contract case records to store a JSON payload of approximately 10–15KB — and how long does a typical Ironclad configuration change like this take to approve and deploy at Helix?**
> **Category:** E — Data and system reality
> **What I already infer from the scenario:** Ironclad REST APIs are confirmed available. The specific data model (whether custom fields exist, their types and size limits) is not described. This was flagged as Assumption A-8 in D4 and Gap G-3 in D5.
> **If the answer is [yes, custom fields are available; changes take 1–2 weeks with admin approval]:** The deviation report schema (D4 §4b) can be stored directly in the CLM as designed. The Ironclad integration is straightforward.
> **If the answer is [no — Ironclad configuration is locked, changes require vendor involvement, or JSON fields of that size are not supported]:** The deviation report must be stored externally (separate database or document attachment). This adds an infrastructure component not currently in scope — a storage layer outside Ironclad — and changes the routing confirmation gate design: Tom's confirmation click must span two systems (Ironclad for routing + external storage for the report). Significant architecture change.
> **Why this matters more than a generic question:** This is the most concrete buildability-blocking question in Category E — the deviation report storage architecture is the centrepiece of the integration design, and a locked Ironclad configuration would require adding a database as a new system dependency.

---

> **Q15: Is there a record anywhere — in Ironclad, in email, or in a shared folder — of Tom's past first-pass classifications that could be used to calibrate the agent's routing logic before the live system is deployed?**
> **Category:** E — Data and system reality
> **What I already infer from the scenario:** Ironclad is used for case management but the scenario does not describe what historical data is stored per case. The scenario's artefacts (2.1, 2.2, 2.3) are incident-level records, not systematic classification logs.
> **If the answer is [yes — Ironclad case records include which clauses were flagged and how they were routed, going back at least 2–3 quarters]:** 600–900 cases of historical data are available. The agent's routing accuracy can be validated against this ground truth before go-live. The validation phase may be shortened from months to weeks.
> **If the answer is [no — Ironclad captures intake and outcome but not mid-process classification detail; Tom's WS1 work is not systematically logged]:** No historical calibration dataset exists. The validation approach (D0B success metric: weekly 10% audit) must be prospective — collect 3–4 weeks of production data, audit it, then tune. This means a longer validation period and a wider initial deployment restriction.
> **Why this matters more than a generic question:** The presence or absence of historical classification data directly sets the validation timeline, which is the primary factor in the time-to-production estimate.

---

### Category F: Organisational and Trust Context

---

> **Q16: If the agent produces a deviation report that misses a material clause deviation — and that case proceeds through WS2, gets a lawyer's sign-off, and the counteroffer is sent — where does the accountability for that outcome sit? Does it rest with the signing lawyer (who approved the counteroffer), with Tom (who confirmed the agent's routing), or does it come back to you as GC?**
> **Category:** F — Organisational and trust context
> **What I already infer from the scenario:** The named-lawyer sign-off rule exists precisely to ensure a named individual is accountable for each counteroffer. I do not know how Amelia interprets that accountability in an agent-assisted context.
> **If the answer is [with the signing lawyer — the sign-off is the accountability event regardless of what tools were used to produce the counteroffer]:** The current sign-off gate architecture is sufficient. The agent is a tool; the lawyer is accountable for what they sign. The oversight design does not need additional layers beyond the existing sign-off gate.
> **If the answer is [with me as GC, because I authorised the deployment — any systematic agent error becomes a governance failure at my level]:** Amelia will require additional protective layers before deploying: potentially a higher sampling rate in the accuracy audit, a soft-launch period with a more conservative autonomous scope, or a formal policy statement on agent-assisted review signed by all team members. The initial deployment may need to be structured as a shadow deployment (agent classifies but Tom still performs the first-pass read in parallel) before any autonomous WS1 classification goes live.
> **Why this matters more than a generic question:** Amelia's answer determines the initial deployment model — shadow vs. live — and the oversight intensity in the first 3 months.

---

> **Q17: What is the minimum visible human oversight step that would make this deployment politically acceptable to you personally — and to any external auditor (e.g., a client's procurement team or a regulator) who might review how Helix's contract review process works?**
> **Category:** F — Organisational and trust context
> **What I already infer from the scenario:** Amelia owns the governance framework and the hard constraint. I do not know whether she has a view on what "sufficient" oversight looks like for an AI-assisted process, or whether external audit requirements (e.g., from NHS trust procurement standards) place demands on the process documentation.
> **If the answer is [Tom's routing confirmation in Ironclad is sufficient — he reads the report, confirms or corrects, and that's the human in the loop]:** The current design is correct. No additional oversight layers needed. The weekly 10% audit by a lawyer is the accuracy monitoring mechanism.
> **If the answer is [a named lawyer must review and counter-sign every deviation report before it is used for routing, not just Tom]:** The HITL model changes: Tom confirms routing, and a lawyer spot-checks the deviation report (not just at sign-off, but earlier in the process). This doubles the human touch points and erodes the WS1 time-per-case improvement. The agent's primary value shifts from "autonomous WS1" to "structured assistant that makes Tom and the lawyers faster" — a Human-led + Agent Support archetype for the whole pipeline, not just C-3. The D2 archetype assignments would need revision.
> **Why this matters more than a generic question:** The answer determines the actual operational model at deployment — autonomous report generation with Tom's confirmation (as designed), or report generation requiring additional lawyer review before routing — and directly sets the WS1 time-per-case achievable KPI.

---

## 3. Questions Not Asked — and Why

> **Question not asked:** "How many contracts does your team process per quarter?"
> **Why not:** This is stated in the scenario: approximately 300 contracts per quarter, with a 70/20/10 triage split. Asking confirms we have not read the briefing material, which wastes Amelia's time and damages credibility.

---

> **Question not asked:** "What systems does your team currently use for contract management?"
> **Why not:** The scenario explicitly names Ironclad, SharePoint, Outlook, Word, and Salesforce. A question about tooling that the scenario already answers has no design fork — no matter what Amelia says, the answer is already known.

---

> **Question not asked:** "Have you considered the risks of AI making mistakes in legal documents?"
> **Why not:** This is a concern statement dressed as a question. It has no design fork — both "yes I have" and "no I haven't" lead to the same design response. More importantly, Amelia will have considered this; the question implies she has not, which is condescending and likely to create friction at the start of the relationship.

---

> **Question not asked:** "Can you walk us through your end-to-end contract review process from intake to execution?"
> **Why not:** The scenario provides a detailed process description across four work streams with volumes and times. A broad process walkthrough produces information we already have; it consumes 20–30 minutes of the call that should be spent on the specific unknowns that would change the design. If anything is unclear in the process, narrow questions (like Q5 and Q6 above) are more efficient than a broad funnel.

---

> **Question not asked:** "What would success look like for this project from your perspective?"
> **Why not:** The scenario already provides explicit success metrics: ≤3 business day turnaround, ≥375 contracts/quarter, ≥95% accuracy. Asking Amelia to re-state what the CRO has already put in writing adds no design information. If her definition of success diverges materially from the documented metrics, that is a governance conversation, not a discovery question — and should be surfaced as a stakeholder alignment issue rather than buried in the discovery call.

---

## 4. Sequencing for a 60-Minute Discovery Call

| Time slot | Question(s) | Goal for this segment |
|---|---|---|
| 0–5 min | Context setting — confirm Amelia's ownership of WS1 process governance vs. what she delegates to Tom and the lawyers day-to-day | Establish whether Amelia has direct visibility into Tom's WS1 decisions or whether she is relying on Tom's judgment without systematic oversight — this primes the conversation for Q10 (the Artefact 2.1 judgment call) |
| 5–15 min | **Q5** (does Tom read every contract for NRR?) + **Q6** (what makes a clause escalation-worthy: magnitude, type, or novelty?) | Understand the real cognitive structure of WS1 before asking Amelia to comment on Tom's behaviour — get a baseline picture of what the first-pass triage actually involves so the later questions land with evidence, not abstraction |
| 15–30 min | **Q4** (what are Tom's 3–5 routing signals?) — use one real case as the anchor; if possible, reference the VendorCo MSA from Artefact 2.1 | Produce the raw material for the escalation criteria document in the call itself — Amelia thinking through one real case out loud often surfaces more criteria than direct questioning; if she cannot articulate criteria, this session defines the workshop scope |
| 30–45 min | **Q10** (Amelia's view on the £50k liability cap routing from Artefact 2.1) + **Q8** (has the sign-off rule ever been bypassed?) + **Q7** (what does the sign-off action look like in Ironclad?) | Resolve the two most consequential governance unknowns: whether Tom's informal judgment is calibrated to Amelia's standard (determines whether conservative default over-escalates), and whether the hard constraint has a technical enforcement point or is currently policy-only |
| 45–55 min | **Q14** (Ironclad custom field feasibility) + **Q3** (substitute clause language in playbook) + **Q2** (DPA update timeline and versioning) | Confirm or block the three most critical buildability assumptions — these answers determine whether Day 1 build can begin immediately or requires prerequisite work items (Ironclad config change, playbook reformatting, DPA section update) |
| 55–60 min | **Q16** (where does accountability sit for a missed deviation?) + close with next steps: schedule escalation criteria workshop, identify Ironclad admin contact, confirm DPA update owner and target date | Surface Amelia's accountability framing before closing — the answer shapes the initial deployment model (shadow vs. live), and closing with a concrete next-steps list (criteria workshop, Ironclad admin contact, DPA update target) gives the FDE actionable outcomes from the call |