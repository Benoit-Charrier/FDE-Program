# D0C — Discovery Synthesis
**Helix Workforce Software — Vendor Contract Clause Review**
**Produced:** 2026-05-04 | **Status:** Draft — awaiting FDE approval

---

## 0. Executive Summary

- **Primary cognitive workload:** WS1 (first-pass clause classification) consumes approximately 125 hours per quarter through a single paralegal (Tom Reilly), making it the highest-volume cognitive bottleneck in the pipeline — but the artefacts confirm the work is not purely mechanical: Tom is making informal escalation judgment calls that the playbook does not explicitly authorise, meaning the real cognitive load is higher and less consistent than the work stream description implies.
- **Most critical lived-vs-documented gap:** The contract playbook (Position Statements v3.4) is known-stale on the DPA section following Q1 DPDI Act updates, and Tom is actively classifying DPA clauses against an outdated standard — a compliance gap that is not a temporary oversight but a sustained, acknowledged risk that Amelia has not yet scheduled to remediate.
- **Highest-signal delegation opportunity:** WS1 first-pass clause classification is the strongest agent target — it is the volume gate for the entire pipeline (~23 contracts/week, ~25 min each), the task is primarily playbook comparison (a pattern-matching task for an LLM), and the artefacts reveal the primary obstacle is not complexity but the absence of explicit escalation criteria; once those criteria are codified, the classification task becomes delegatable with a structured human-in-the-loop at the escalation threshold.

---

## 0b. Table of Contents

1. Lived Process Narrative
2. Points of Pain Inventory
3. ATX Discovery Dimensions — Assessment per Work Stream
4. Cognitive Workload Hotspots
5. Known Unknowns
6. Assumption Log

---

## 1. Lived Process Narrative

*Reconstructed from scenario_context.md and scenario artefacts. Inferences are labelled.*

**How work arrives.** A vendor's procurement team sends their paper via email to Outlook — the scenario confirms this is the primary intake channel, with Salesforce as a secondary trigger for new-prospect contracts. The CLM (Ironclad) is the system of record, but intake begins in email, not Ironclad. Whether Tom manually logs each contract into Ironclad upon receipt or whether there is an automated intake step is unknown — labelled as **Unknown [U-1]** below.

**WS1: First-pass clause classification.** Tom opens the vendor's Word document and reads through 15–40 pages, mapping each major clause to the playbook categories: liability cap, DPA, termination, IP, SLA, governing law, indemnity. The playbook lives on a SharePoint page ("Position Statements v3.4"). He reads clause-by-clause and annotates his assessment in the margin or in a tracking document.

*[PAUSE POINT]* At the liability cap clause, Tom must decide whether a deviation constitutes a routine redline (WS2, within his authority) or an escalation (WS3). Artefact 2.1 shows him encountering a £50k cap against a £250k playbook minimum and deciding independently that it is "borderline negotiable, not escalation." The playbook does not appear to define this threshold explicitly — Tom is exercising informal judgment about magnitude and negotiability. This is not a documented step; it is a judgment call the process relies on without naming it as such.

*[JUDGMENT CALL]* At the DPA clause, Tom checks against playbook section 12 — but the playbook has not been updated for Q1 DPDI Act changes (Artefact 2.3). Tom knows the standard is potentially stale ("DPDI updates aren't reflected — playbook is stale on this") and does not know whether this uncertainty warrants escalation. His response is informal peer consultation: "Will ask Sarah." There is no formal trigger, no escalation protocol, and no documentation of the question or its answer. This is a coordination workaround substituting for a governance gap.

*[WORKAROUND]* Sarah is one of the three commercial lawyers on the team. This ad hoc consultation path — Tom to Sarah — is not part of the documented escalation process (which routes unusual clauses to "senior-lawyer review"). Whether this is effectively the same thing or an informal bypass of the formal route is unclear.

After completing the first pass, the contract is routed:
- **70% (~210/quarter):** Standard terms — playbook match. These presumably proceed to execution without redline. *[Assumption: the team's SOP has a mechanism for clearing these; the scenario does not describe it explicitly.]*
- **20% (~60/quarter):** Negotiable deviations → WS2 (Tom redlines).
- **10% (~30/quarter):** Unusual clauses → WS3 (senior lawyer review).

**WS2: Standard-deviation redlining.** Tom drafts the redline in Word using Track Changes, working from the playbook position. This is more mechanical than WS1 — the position is already determined — but requires translating a position statement into precise contractual language. Whether the playbook provides standard substitute clause language or only position statements is not stated in the scenario; this affects how delegatable this drafting task is. *[Unknown — see U-2.]*

*[COORDINATION WORK / WORKAROUND]* When the redlined document is ready to send, Tom must check the vendor's delivery preference. Artefact 2.2 confirms at least three vendors this quarter cannot accept SharePoint links and require Word attachments via email. This creates a manual routing decision that bypasses Ironclad and SharePoint, generating a parallel delivery channel that is not reflected in the CLM audit trail. Tom has flagged this to Amelia; no systemic fix is in place.

**WS3: Escalated clause review.** A senior lawyer (routing not specified in scenario — presumably by availability or subject matter ownership) takes the escalated contract and spends ~90 min reviewing the unusual clause(s), interpreting the legal risk, framing a counteroffer position, and drafting the redline. This is the highest-judgment step in the process. The lawyer must hold simultaneously: the playbook's standard position, the deal's commercial context, the counterparty's likely response, and any regulatory considerations. *[ASYNC WAIT]* During escalated review, the contract sits in a queue waiting for lawyer availability — a key contributor to the 4–6 day turnaround.

**WS4: Counteroffer drafting and sign-off.** Once a redline exists (from WS2 or WS3), a lawyer drafts the outbound response to the vendor's procurement team and routes it for named-lawyer sign-off before it leaves the queue. Amelia's hard rule — no counteroffer may go out without a named lawyer's sign-off on the specific clauses being negotiated — is a non-negotiable governance constraint, the rationale for which is not stated in the scenario. *[ASYNC WAIT]* The counteroffer waits in the sign-off queue until a named lawyer reviews and approves. At ~90 counteroffers per quarter (~7/week), this creates a recurring approval queue that compounds the turnaround delay.

*[WORKAROUND]* At the delivery step, the email-vs-SharePoint routing decision from WS2 reappears: some vendors require attachment-via-email, bypassing the standard SharePoint link workflow and creating a manual coordination step for each affected vendor.

The cumulative result of serial queues — WS1 backlog, then WS3 availability wait, then WS4 sign-off queue — is a 4–6 day turnaround that the CRO considers incompatible with enterprise sales targets. The bottleneck is not any single step; it is the compounding of queue wait times across the pipeline.

---

## 2. Points of Pain Inventory

| Work Stream | Pain Description | Volume (per week) | Pain Level | Lived-vs-Documented Gap | Key Data/Systems | Delegation Signal | Candidate for Automation? |
|---|---|---|---|---|---|---|---|
| WS1 — First-pass clause classification | Tom is the sole throughput gate for all 300 contracts/quarter; informal escalation judgment calls exceed his documented authority; DPA review against stale playbook creates compliance exposure | ~23/week | **H** | Tom makes unsanctioned escalation calls (Artefact 2.1); peer-consults Sarah for DPDI ambiguity outside formal escalation path (Artefact 2.1) | Ironclad, Outlook (intake), SharePoint (playbook) | High — pattern-matching task against a codified standard; primary blocker is absent explicit escalation criteria, not task complexity | **Yes** — primary agent target; requires playbook update and escalation criteria codification as pre-conditions |
| WS2 — Standard-deviation redlining | Redline drafting is mechanical but depends on WS1 classification accuracy; email-only delivery for some vendors bypasses CLM and creates manual coordination | ~4.6/week | **M** | Email-delivery bypass of SharePoint/Ironclad is a recurring exception (~3 cases/quarter confirmed), not an edge case (Artefact 2.2) | Word/Track Changes, SharePoint, Ironclad, Outlook | Medium — delegatable if playbook includes standard substitute language; if positions-only, drafting requires more judgment | **Conditional** — delegatable at high confidence if playbook has substitute clauses; requires discovery to confirm |
| WS3 — Escalated clause review | Low volume but highest judgment per case (~90 min); risk of under-escalation from WS1 informal triage; lawyer availability creates queue wait | ~2.3/week | **M** | Escalation routing is not systematically documented; ad hoc Tom → Sarah consultation path exists outside the formal escalation process | Word/Track Changes, SharePoint (playbook + precedent — assumption) | Low for decision-making; Medium for drafting support — agent can draft from playbook position; lawyer must evaluate | **Partial** — agent-supported drafting (Human-led + Agent Support); decision-making stays human |
| WS4 — Counteroffer drafting and sign-off | Named-lawyer sign-off is a hard governance constraint creating a recurring approval queue (~7 counteroffers/week); email-vs-SharePoint routing adds manual coordination | ~6.9/week | **M** | Email delivery bypass recurs (Artefact 2.2); sign-off rule's rationale is undocumented — may have more flexibility than stated if the rationale is policy rather than regulation | Word/Track Changes, Outlook, Ironclad | Low for sign-off (non-delegatable by rule); Medium for preparation and routing (could be workflow-automated) | **Partial** — sign-off stays human; routing and package preparation could use CLM workflow rules (not an agent) |
| Cross-cutting — Stale playbook compliance risk | DPA section not updated since Q1 DPDI Act changes; team operating against outdated standard across WS1, WS2, and WS3; Amelia is aware but remediation not scheduled | All WS1/2/3 volume | **H** | Documented standard (playbook) diverges from current regulatory reality; informal knowledge of the gap (Tom's margin note, Amelia's sticky note) exists but is not acted on | SharePoint (playbook) | This is a pre-condition, not a delegation target — any agent must operate against a current playbook | **No** — playbook update is required before agent deployment; this is a governance remediation task |
| Cross-cutting — CLM bypass via email | Some vendors require Word attachment delivery via email, bypassing Ironclad/SharePoint; creates parallel untracked channel; Tom flags this as recurring | ~0.2–0.5/week (est. — 3 confirmed this quarter, assumption) | **L** | The documented workflow assumes SharePoint link delivery; email attachment delivery is undocumented and creates audit trail gaps | Outlook, Ironclad | Medium — agent could handle email intake and delivery, potentially eliminating the bypass | **Yes** — agent-managed email handling could normalise this channel, but requires discovery on volume |

**Pain level justifications:**
- **WS1 = High:** 125 hrs/quarter throughput bottleneck for all 300 contracts; informal judgment calls exceed documented authority; active compliance gap from stale DPA standard. Combining highest volume, active governance risk, and informal process drift makes this the most critical pain point.
- **WS2 = Medium:** Volume is significant (45 hrs/quarter) and the email bypass creates an audit gap, but the work is more rule-bound and the judgment load is lower than WS1. The pain is real but is downstream of the WS1 bottleneck — fixing WS1 relieves much of WS2's pressure.
- **WS3 = Medium:** Low volume (45 hrs/quarter) but high judgment and highest per-case risk. Pain is concentrated in lawyer availability and queue wait, not in the nature of the task itself.
- **WS4 = Medium:** High frequency (~7/week) and a hard governance constraint, but the sign-off task itself is not cognitively burdensome — it is organisationally constrained. The pain is friction and queue time, not complexity.
- **Cross-cutting stale playbook = High:** Compliance risk is not proportional to the hours it occupies; a single missed DPDI clause in an executed contract can have material consequences.

---

## 3. ATX Discovery Dimensions — Assessment per Work Stream

| Work Stream | Volume & Time | Cognitive Nature | Data & Systems | Risk & Compliance | Organisational |
|---|---|---|---|---|---|
| **WS1** | 300/quarter, ~25 min/case = ~125 hrs/quarter; highest volume of any stream; ~23 cases/week for a single person (Tom) | Mixed: primarily pattern-matching (clause vs. playbook) but with informal judgment at the escalation threshold; artefact confirms unsanctioned judgment calls occur routinely | Unstructured input (Word/PDF via email); structured reference (playbook on SharePoint); Ironclad for record-keeping; DPA playbook section is known-stale | Active compliance gap: DPA review against stale Q1 standard; under-escalation risk from informal triage; no audit of classification accuracy | Single-person throughput gate (Tom); ad hoc consultation path to Sarah for ambiguous cases; no documented quality control on classification output |
| **WS2** | 60/quarter, ~45 min/case = ~45 hrs/quarter; ~4.6/week | Largely rule-bound: position is set by playbook; drafting precision required but creative judgment is low; exception = when playbook position is ambiguous or the substitute language doesn't fit the counterparty's structure | Word/Track Changes for redlining; playbook on SharePoint; Ironclad; Outlook for email-channel delivery (recurring bypass) | Lower than WS1/3: within paralegal authority; but misclassification from WS1 propagates risk here — a WS2 contract that should have been WS3 gets a lightweight redline | Within Tom's authority; no escalation needed for standard deviations; email delivery bypass creates informal coordination step with Amelia (flagging only, not approval) |
| **WS3** | 30/quarter, ~90 min/case = ~45 hrs/quarter; ~2.3/week | Judgment-heavy: unusual clause interpretation, counteroffer framing, legal drafting; tacit knowledge of deal context, counterparty history required; highest cognitive load per case | Word/Track Changes; SharePoint; possibly prior contract versions or negotiation history — Unknown — requires discovery | Highest per-case risk: senior lawyer accountability; hard stop before counteroffer; regulatory and commercial exposure if framing is wrong | Routing to specific lawyer not documented; dependency on lawyer availability creates queue; under-escalation from WS1 means some WS3 work may be arriving as WS2 |
| **WS4** | ~90/quarter, ~30 min/case = ~45 hrs/quarter; ~6.9/week | Mixed: drafting component requires precision; sign-off is a verification task (not judgment about the legal position, which was made in WS3); hard rule makes the sign-off non-discretionary | Word/Track Changes; Outlook (for email-channel counteroffers); Ironclad for record | Non-negotiable governance constraint: named-lawyer sign-off before counteroffer exits; rationale not stated in scenario — Unknown — requires discovery on whether this is regulatory or policy | Amelia's rule creates dependency on named lawyer availability; email-vs-SharePoint routing creates ad hoc manual step; no documented process for which lawyer signs off on which contracts |

---

## 4. Cognitive Workload Hotspots

> **Hotspot [WS1-1]:** First-pass clause classification — escalation threshold judgment
> **What the human does:** Tom reads a non-standard clause and makes a binary decision: is this a WS2 redline (within his authority) or a WS3 escalation (requires a lawyer)? In Artefact 2.1, he makes this call on a clause where the deviation is significant (£50k vs. £250k playbook floor) based on his personal assessment that the term is "borderline negotiable."
> **Why a machine can't trivially replace this today:** The escalation threshold is not written down in the playbook as a rule. The playbook defines positions (what Helix wants) but not triage logic (when a deviation is too large to handle at paralegal level). Any classifier — rule-based or AI — needs explicit criteria to make this determination reliably.
> **Delegation signal:** If explicit escalation criteria were codified (e.g., liability cap deviations >X% of playbook floor = escalation; DPA terms deviating from Annex C = escalation), this becomes a classifiable decision. An LLM-based agent with these criteria and a calibrated confidence threshold (route to human when confidence < threshold) could handle the majority of cases. The human-in-the-loop at the borderline cases would be a designed feature, not a fallback.

> **Hotspot [WS1-2]:** DPA adequacy assessment under stale playbook
> **What the human does:** Tom compares the vendor's DPA clause to the playbook standard — but knows the playbook hasn't been updated for DPDI Act Q1 changes. He has to decide whether the uncertainty warrants escalation, and resolves it by informally asking a lawyer colleague rather than applying a rule.
> **Why a machine can't trivially replace this today:** The agent's ground truth is the playbook. If the playbook is stale, the agent classifies DPA deviations against the wrong standard — and, critically, cannot flag its own uncertainty about playbook currency the way Tom can. Tom's metacognitive awareness of the gap (he wrote the margin note) is itself a form of quality control that the process would lose if classification were fully automated against the current stale document.
> **Delegation signal:** Playbook update is a hard pre-condition. Once the DPA section is current and the agent can compare against a known-current standard, DPA clause comparison becomes highly delegatable — it is a structured matching task with well-defined acceptance criteria. The agent should also be designed to flag its own playbook version and surface staleness warnings if the playbook has not been updated within a defined period.

> **Hotspot [WS3-1]:** Escalated clause review — counteroffer position framing
> **What the human does:** A senior lawyer reads an unusual clause, interprets it in the context of the specific deal and counterparty, decides what Helix's negotiation position should be (not just what the playbook says, but what is commercially viable given this deal), and drafts precise legal language for the redline.
> **Why a machine can't trivially replace this today:** This requires synthesis of playbook position + deal context + counterparty relationship + legal judgment about what language will hold in court and what will be acceptable in negotiation. The playbook tells the lawyer what Helix wants; the lawyer decides what Helix can realistically get and frames it in language that achieves the goal. This contextual, tacit synthesis is not derivable from structured data alone.
> **Delegation signal:** Low for the decision and framing; medium for the drafting. An agent could draft a starting-point redline from the playbook position for the lawyer to review and modify — reducing 90 min to perhaps 45 min — but cannot replace the lawyer's judgment about position. Archetype: Human-led + Agent Support.

> **Hotspot [WS4-1]:** Named-lawyer sign-off
> **What the human does:** A named lawyer reviews the drafted counteroffer — specifically the redlined clauses — and signs off before it is sent to the vendor. This is the governance checkpoint that Amelia's hard rule enforces.
> **Why a machine can't trivially replace this today:** This is not a technical limitation but a governance constraint. The rule exists to maintain a named human accountable for every Helix legal position sent externally. Even a perfect agent output cannot satisfy this requirement, because the rule is about human accountability, not about classification accuracy.
> **Delegation signal:** None for the sign-off act itself — this is a permanent HITL by design. Agent value at WS4 is in preparation: assembling the review package, flagging what changed from the previous round, highlighting the specific clauses requiring sign-off attention, and routing to the right lawyer. These preparation tasks are fully delegatable and would reduce the per-case time below the current ~30 min estimate.

> **Hotspot [WS2-1]:** Standard-deviation redline drafting
> **What the human does:** Tom maps the deviation to the playbook position and writes the specific redline clause language in Word. This requires translating a position statement ("we require 12 months / £250k liability cap") into precise contractual language that fits the structure and numbering of the vendor's document.
> **Why a machine can't trivially replace this today:** The translation from position to contract language requires understanding the vendor's document structure and the specific phrasing that will replace the non-standard clause. If the playbook only contains position statements (not substitute language), this is a drafting judgment task; if it contains standard substitute clauses, it becomes a copy-and-adapt task that is close to deterministic.
> **Delegation signal:** Contingent on playbook format. If substitute clause language exists in the playbook, this is a high-confidence agent task (copy substitute clause, adapt numbering/cross-references, flag for human review). If position-only, the agent can produce a draft redline from the position statement but human review of the language is necessary. This is the key unknown for WS2 delegation scope.

---

## 5. Known Unknowns

> **Unknown [U-1]:** How does a vendor contract get from Outlook (intake) to Ironclad (system of record) — is there an automated ingestion step, or does Tom log it manually?
> **Why it matters for agent design:** If intake is manual (Tom copies metadata from email to Ironclad), an agent could automate this step and create a clean record before classification begins. If already automated, that step is solved and the agent starts at the classification task. The intake method also affects whether the agent can be triggered by an Ironclad workflow event or must monitor an Outlook mailbox.
> **How to discover it:** Ask Tom to walk through what happens in the first five minutes after a contract email arrives. Ask Amelia whether Ironclad generates an intake ticket automatically or manually.

> **Unknown [U-2]:** Does the contract playbook include standard substitute clause language, or only position statements?
> **Why it matters for agent design:** This is the primary determinant of WS2 delegation scope. Position-only playbook → agent needs to draft language (harder, requires human review of output). Playbook with substitute clauses → agent performs a document-editing task (easier, higher accuracy, tighter human review requirement).
> **How to discover it:** Ask to see a sample playbook entry for a specific clause type (e.g., liability cap). If the entry contains only a position ("we require X"), drafting is not pre-populated. If it contains a template redline ("replace with the following language: ..."), drafting is pre-populated.

> **Unknown [U-3]:** Why does Amelia's named-lawyer sign-off rule exist — is it a regulatory requirement, a professional responsibility obligation, or an internal policy response to a past incident?
> **Why it matters for agent design:** If it is a regulatory or professional responsibility requirement, the HITL is permanent and non-negotiable regardless of agent accuracy. If it is an internal policy, there may be flexibility in how it is implemented (e.g., async batch review vs. synchronous approval per contract). The rationale also affects whether the rule applies equally to all contract types or whether low-risk contracts (e.g., mutual NDAs) could be signed off in a lighter-touch way.
> **How to discover it:** Ask Amelia directly: "Can you tell me what drove the sign-off rule — was there a specific incident, or is it a compliance requirement?" and "If an agent were to draft the counteroffer with 95%+ accuracy, what would need to be true for you to consider modifying how sign-off works?"

> **Unknown [U-4]:** What percentage of contracts arrive through email-only channels (bypassing SharePoint/Ironclad) per quarter, and is there a pattern by counterparty type or industry?
> **Why it matters for agent design:** If the email bypass is confirmed at >20% of contracts, the agent must treat email delivery as a primary channel, not an exception handler. If concentrated in a specific counterparty type (e.g., large enterprise procurement systems with attachment-only workflows), the agent can flag these at intake and route them through a dedicated email-delivery path.
> **How to discover it:** Ask Tom: "You mentioned this is the third vendor this quarter who needs email attachment delivery — can you estimate the total over the past year? Is there a pattern in the types of companies?" Review Ironclad records for contracts without a SharePoint link in the delivery log.

> **Unknown [U-5]:** Has Helix experienced any legal or commercial consequence from a missed, misclassified, or incorrectly redlined contract clause?
> **Why it matters for agent design:** Past failures reveal the actual error modes that matter, calibrate the risk tolerance for agent delegation, and identify the specific clause types or triage decisions where HITL review is most critical. A single past incident of, e.g., an uncapped liability clause being accepted as standard would change the design of WS1's escalation logic for liability clauses.
> **How to discover it:** Ask Amelia: "Has there been an instance where a clause issue that should have been caught in review created a problem downstream — commercially, legally, or with a counterparty?" Review any post-mortems or legal counsel correspondence if accessible.

> **Unknown [U-6]:** Does contract volume spike at any predictable point in the year (quarter-end, renewal cycles, procurement seasons)?
> **Why it matters for agent design:** A flat-volume assumption produces a different agent design than a spike-volume one. If volume doubles at quarter-end, the agent must handle peak load (potentially 2× weekly volume) without degrading accuracy or creating a new queue. This affects infrastructure sizing and the design of the human-review capacity alongside the agent.
> **How to discover it:** Ask Tom or Amelia: "Is the volume of contracts roughly steady through the year, or are there periods when it spikes significantly? What causes the spikes?"

> **Unknown [U-7]:** How are WS3 escalated contracts routed — by availability, by subject matter expertise, or by some other rule?
> **Why it matters for agent design:** If routing is informal (whoever is available), the agent's routing logic can be simple (route to next available lawyer in the queue). If routing reflects subject matter ownership (e.g., Sarah handles IP clauses, lawyer X handles SLA/service terms), the agent needs to classify the escalation reason and route to the appropriate person. Incorrect routing to the wrong lawyer would create re-work.
> **How to discover it:** Ask the team: "When Tom escalates a contract to WS3, who does it go to — is there a rule, or does it depend on who's available?" Ask Amelia whether the three commercial lawyers have subject matter specialisms.

---

## 6. Assumption Log

> **Assumption [A-1]:** The 70%/20%/10% triage split is applied at WS1 classification and reflects a stable distribution. The 70% standard-match contracts do not require a redline and are processed to execution without further legal review beyond the first-pass classification.
> **Why it matters:** If the 70% standard-match contracts require any additional step before execution (e.g., a brief lawyer review or a pro forma sign-off), the WS4 volume estimate and the turnaround model are both incorrect.
> **If wrong:** The total pipeline load and the queue dynamics change; in particular, if all 300 contracts require some WS4 sign-off step, the sign-off bottleneck is significantly more severe.
> **Confidence:** Medium — the scenario implies standard-match contracts proceed without redline, but does not explicitly confirm they bypass WS4.

> **Assumption [A-2]:** The informal Tom → Sarah consultation path for ambiguous cases (evidenced by Artefact 2.1) occurs at the WS1 stage and is not tracked in Ironclad or any system of record.
> **Why it matters:** If these consultations are tracked, there may be a dataset of ambiguous cases and their resolutions that could be used to train or calibrate escalation criteria for the agent. If untracked, this institutional knowledge is lost and would need to be elicited through interviews.
> **If wrong:** A tracked consultation log would be a high-value input to the agent design — it captures exactly the borderline cases and how experienced lawyers resolve them.
> **Confidence:** High (informal margin notes and verbal consultations are structurally unlikely to be logged in a CLM).

> **Assumption [A-3]:** Weekly volume figures (~23/week for WS1, ~4.6/week for WS2, ~2.3/week for WS3, ~6.9/week for WS4) are computed assuming 13 working weeks per quarter. These are averages and do not reflect intra-quarter variation.
> **Why it matters:** If volume spikes (quarter-end, renewal seasons), the average-based load estimates understate peak demand. Agent design calibrated to average volume will underperform at peak.
> **If wrong:** If volume is significantly spikier than flat, the agent design needs explicit peak-load handling and the human review capacity must scale alongside it.
> **Confidence:** Medium (13-week quarter is standard; spike pattern is Unknown [U-6]).

> **Assumption [A-4]:** The CLM bypass described in Artefact 2.2 (email attachment delivery for vendors who cannot accept SharePoint links) affects a material but minority fraction of contracts — estimated at 3–5 per quarter based on Tom's note ("third vendor this quarter"). This is treated as a recurring exception that the agent design must accommodate rather than an edge case that can be ignored.
> **Why it matters:** If the bypass fraction is higher than estimated (e.g., 20%+), it becomes a primary delivery channel and must be a first-class feature of the agent design, not an exception handler.
> **If wrong (higher fraction):** The agent must natively support email attachment delivery for outbound counteroffers, with full audit trail logging, rather than treating it as a fallback.
> **Confidence:** Low — the "third vendor this quarter" data point is a lower bound, not a complete count.
