# D6 — Discovery Questions: Apex Billing Dispute Resolution Agent

**Produced:** 2026-05-06
**Status:** Draft — awaiting FDE review
**Primary stakeholder:** Sarah Whitmore, COO, Apex Distribution Ltd
**In scope:** WS4 Billing Disputes (BDRA agent design); cross-references D4 revision 1 §10 outstanding gaps

---

## 0. Executive summary

- The most design-critical unknown is whether a formal credit policy exists — or can be produced before deployment — that defines validity rules for each dispute type and a credit amount for each outcome: without it, T-007 (validity assessment) and T-009 (credit recommendation) cannot be built, and the agent's primary value proposition is blocked entirely regardless of how well every other integration works.
- The governance question that must be resolved before any build decision is made is exactly how Sandra applies a credit today — what specific system action she takes and whether any authenticated step records her identity before the credit lands in APEX_CREDITS — because Artefact 2 confirms credits can reach APEX_CREDITS without an APPROVER_ID, meaning the governance constraint may be technically unenforceable in the current system configuration.
- The question most likely to reveal a dealbreaker is whether Aurum Billing has any programmatic write path for credit records that does not require the 48-hour manual support ticket — because if no such path exists and none can be established, the agent cannot execute credits autonomously, the audit trail compliance KPI cannot be technically enforced at write-time, and C-8 scope must be reduced to record preparation only before build begins.

---

## 0b. Table of contents

- [0. Executive summary](#0-executive-summary)
- [0b. Table of contents](#0b-table-of-contents)
- [1. Stakeholder context](#1-stakeholder-context)
- [2. Questions whose answers would change the design](#2-questions-whose-answers-would-change-the-design)
  - [Category A: Reference material](#category-a-reference-material--structure-authority-and-machine-readability)
  - [Category B: Core decision logic](#category-b-core-decision-logic--how-billing-dispute-resolution-actually-works-today)
  - [Category C: Governance and approval constraint](#category-c-governance-and-approval-constraint--exactly-how-it-operates)
  - [Category D: Exception patterns and escalation triggers](#category-d-exception-patterns-and-escalation-triggers)
  - [Category E: Data and system reality](#category-e-data-and-system-reality)
  - [Category F: Organisational and trust context](#category-f-organisational-and-trust-context)
- [3. Questions you are NOT asking — and why](#3-questions-you-are-not-asking--and-why)
- [4. Sequencing for a 60-minute discovery call](#4-sequencing-for-a-60-minute-discovery-call)

---

## 1. Stakeholder context

Sarah Whitmore is COO of Apex Distribution Ltd, promoted internally 18 months ago after five years running the dispatch team. She commissioned this ATX assessment in direct response to a CEO request triggered by a competitor's reported £1.2M annualised saving on customer service AI. She is sceptical of consultants and of chatbots — specifically, Apex ran a customer-facing chatbot in 2024 that customers rejected, and a separate RPA project targeting billing reconciliation that broke on an Aurum schema change. Both failures are in Sarah's recent memory. Her scepticism is not generic; it is specific to two concrete failure modes: automation that the end customer rejects, and automation that breaks silently on a system it does not control. What she cares about most in WS4 is not speed — it is correctness and compliance. The billing dispute process is exposed to financial control risk (credits applied without audit trail entries, confirmed in Artefact 2), and Sarah's primary concern about AI involvement is that automation amplifies this gap at machine speed: if the agent does what Sandra has been doing informally, it does it sixty times a day with no audit trail. Her trust threshold is therefore not "does it work?" but "can I audit what it did, and can I stop it when it goes wrong?" She would distrust an agent that makes credit decisions she cannot review, challenge, or trace — and she would trust one where every credit decision has a named approver, a CRM case record, and an audit log entry that she can pull on demand.

---

## 2. Questions whose answers would change the design

### Category A: Reference material — structure, authority, and machine-readability

---

> **Q1: Does a formal, documented credit policy for billing disputes exist anywhere at Apex — and if so, where does it live and who owns it?**
> **Category:** A — Reference material
> **What I already infer from the scenario:** The SOP (v2.3, Oct 2023) is stale and Section 4.3 (damaged consignments) is explicitly incomplete. No formal credit policy is referenced in any artefact. The observed resolution in Artefact 2 is a GOODWILL credit of £170 on a £340 fuel surcharge — suggesting a 50% partial credit heuristic — but this is one case with no confirmation it reflects written policy.
> **If the answer is "yes, there is a documented policy":** The policy is the primary retrieval corpus for T-007 and T-009. The next question becomes its format (structured rules vs. narrative) and whether it is version-controlled. If it contains explicit rules for each dispute type (fuel surcharge, redelivery fee, dimensional weight), T-007 can be largely built from it.
> **If the answer is "no, it's informal — we just use judgement":** The credit policy must be produced before agent deployment (D4 §8 Hard Stop 3). This becomes a project prerequisite, not a build input. The follow-up is: who would own writing it, and what is the realistic timeline? If Sarah cannot commit to a formal policy before deployment, the agent scope must be limited to intake, data assembly, and evidence preparation — with no credit recommendation capability.
> **Why this matters more than a generic question:** The existence and format of the credit policy is a binary gating condition for the agent's credit recommendation module — not a design parameter, a prerequisite.

---

> **Q2: The SOP (v2.3, October 2023) references DispatchHub, which was retired eighteen months ago. Has anyone been assigned to update it, and is there a timeline?**
> **Category:** A — Reference material
> **What I already infer from the scenario:** The SOP is confirmed stale; Section 4.3 is explicitly "TBD pending review of insurance protocol." DispatchHub was replaced by the Driver App in October 2024. The SOP has not been updated.
> **If the answer is "yes, an update is in progress / planned within 90 days":** The updated SOP could form a secondary reference document for the agent — particularly Section 4.3 if it covers the damaged consignment procedure that drives most FUEL_SURCH_DAMAGE disputes. This reduces reliance on the credit policy as the sole reference source.
> **If the answer is "no, nobody owns it":** The SOP must be explicitly excluded from the agent's retrieval corpus (D5 §5b checklist item). Escalation path for out-of-taxonomy disputes (ET-002) depends on the human reviewer having a current procedure; without an updated SOP, ET-002 has no documented resolution path on the human side either — a gap that exists regardless of the agent.
> **Why this matters more than a generic question:** The SOP's usability as agent reference material is a deployment prerequisite; knowing whether an update is coming determines whether we design around it or exclude it entirely.

---

> **Q3: When Sandra verifies whether a fuel surcharge charge is correct, does she check it against a rate schedule — and if so, where does that rate schedule live?**
> **Category:** A — Reference material
> **What I already infer from the scenario:** Aurum calculates fuel surcharges automatically (Artefact 2). Sandra cannot adjust individual fuel surcharge line items. The artefact shows AMT_FUEL_SURCH = £340 on INV-2026-04318, but no rate schedule is referenced in any artefact or the scenario.
> **If the answer is "yes, there's a rate table in [system/document]":** Step 1 of the FUEL_SURCH_DAMAGE validity check (calculation verification) can be built. The agent retrieves the rate and compares — producing HIGH-confidence autonomous verdicts for calculation errors without requiring HITL. This is the most impactful improvement to T-007 autonomy rate.
> **If the answer is "no — Aurum calculates it and we trust it unless the customer pushes back":** Calculation verification is not possible. All FUEL_SURCH_DAMAGE cases go directly to Step 2 (delivery context check), keeping confidence below 0.85 for damaged-delivery cases and maintaining HITL for the majority of this dispute type. T-007 autonomous rate for FUEL_SURCH_DAMAGE will be low.
> **Why this matters more than a generic question:** The rate schedule is the primary data source for the rule-based path in T-007 — its accessibility or absence determines whether the largest dispute type has an autonomous verdict path at all.

---

### Category B: Core decision logic — how billing dispute resolution actually works today

---

> **Q4: Walk me through your most recently resolved FUEL_SURCH_DAMAGE dispute — not what the SOP says, what actually happened. What did you look at first, what made you decide on the credit amount, and what did you do in the system to apply it?**
> **Category:** B — Core decision logic
> **What I already infer from the scenario:** From Artefact 2: Sandra resolved a £340 fuel surcharge dispute for Hayes & Sons with a £170 GOODWILL credit after a 9-day exchange. The billing system cannot adjust fuel surcharge line items. Sandra applied the credit via "manual override." There is no audit log entry for this credit. The process involves CRM communication and some form of Aurum interaction.
> **If the answer reveals a consistent rule ("I check [specific field] and if [condition], I apply a 50% credit"):** This is a codifiable decision rule — the highest-value input to T-007. The rule can be formalised as the interim credit policy (confirmed with COO sign-off) and operationalised in the agent immediately.
> **If the answer reveals tacit judgement ("it depends on the customer, how long they've been with us, how the driver handled it"):** The decision logic is context-dependent and relationship-driven — not readily codifiable. T-007 confidence for this type will be lower; HITL rate for FUEL_SURCH_DAMAGE will be higher. The agent's value in this case is evidence assembly and audit record, not verdict determination.
> **Why this matters more than a generic question:** This is the primary route to discovering the actual validity rule for the highest-volume dispute type — one real case trace extracts more design signal than any general question about policy.

---

> **Q5: For DIM_WEIGHT disputes — what evidence would convince you that a dimensional weight charge is wrong? If a customer disputes it, what do you check to decide whether to credit them?**
> **Category:** B — Core decision logic
> **What I already infer from the scenario:** APEX_DISPUTES_OPEN shows D-2026-00339 (Aldgate Logistics, DISPUTE_AMT = £88.00, DIM_WEIGHT type, assigned to Tom J.). APEX_BILL_DAILY shows no dedicated DIM_WEIGHT field — the charge appears embedded in AMT_GROSS. The dimensional weight formula and tolerance are not specified in any scenario document.
> **If the answer is "we check the declared dimensions against Aurum's calculation — if there's a discrepancy, we credit":** The check is computational — buildable as a Step 1 rule-based check in T-007 once the formula is confirmed. Autonomous verdict for calculation errors is achievable.
> **If the answer is "we ask the customer for their package dimensions, check against what the driver scanned, and use our judgement":** The check requires Driver App scan data and a cross-reference step — deterministic only if scan data is available and consistent. High data-unavailability rate means HITL for most DIM_WEIGHT cases.
> **Why this matters more than a generic question:** This question simultaneously surfaces the formula (Q-V5), the data source (Q-V4), and the evidence standard — three unknowns that all feed into the DIM_WEIGHT branch of T-007.

---

> **Q6: Across all billing dispute types, roughly what proportion result in no credit at all — the customer's claim is reviewed and upheld as a valid charge?**
> **Category:** B — Core decision logic
> **What I already infer from the scenario:** APEX_DISPUTES_OPEN shows mostly PENDING_CLAIM or AWAITING_CUST statuses — no confirmed rate of claims upheld vs. credited. Artefact 2 shows a credit was issued but does not say whether this was representative. APEX_CREDITS artefact shows 4 credits in one day across 6 open disputes.
> **If the answer is "very few — we almost always offer some credit":** The agent's primary job is generating the correct credit amount and the audit trail, not making binary valid/invalid determinations. T-007 confidence thresholds should be tuned toward recommending credit with varying amounts rather than binary verdicts.
> **If the answer is "a significant portion — maybe 30-40% — we uphold the charge":** The validity assessment is meaningfully binary. The agent must produce high-quality invalid verdicts as well as valid ones. The calibration set must include sufficient "no credit" cases to validate the 0.85 threshold on both sides of the verdict.
> **Why this matters more than a generic question:** The base rate of "no credit" outcomes directly determines the class balance required in the calibration set (D4 §3) and whether the HITL rate target of ≤60% is achievable within 90 days.

---

> **Q7: When Sandra decides on a credit amount — for example, the £170 on a £340 fuel surcharge — is that based on a documented rule, a team norm, or purely her judgement in the moment?**
> **Category:** B — Core decision logic
> **What I already infer from the scenario:** Artefact 2 shows a £170 credit on a £340 disputed amount — exactly 50%. Whether this reflects a formal rule, a team norm, or coincidence is not stated. No formal credit policy document is referenced anywhere in the scenario.
> **If the answer is "there's an informal norm — we typically offer 50% for goodwill":** This is the minimum viable policy that can be formalised quickly. The COO signs off on a written version; it becomes the agent's credit policy for GOODWILL cases immediately. Deployment timeline compresses.
> **If the answer is "it's entirely Sandra's call — it depends on how angry the customer is, how long they've been with us":** No fixed rule exists. The credit policy must be built from scratch. Deployment timeline extends by the time required to draft, review, and COO-approve a formal policy — potentially 4–8 weeks.
> **Why this matters more than a generic question:** Whether an informal norm exists determines the time and effort required to produce the formal credit policy that is a hard prerequisite for T-009 (D4 §8 Hard Stop 3).

---

### Category C: Governance and approval constraint — exactly how it operates

---

> **Q8: When Sandra applies a goodwill credit today, what exactly does she do, step by step? Which system does she go into, what does she type or click, and who — if anyone — reviews or confirms it before it goes through?**
> **Category:** C — Governance and approval constraint
> **What I already infer from the scenario:** Artefact 2 says Sandra applied a £170 credit via "manual override." An internal note states there is no entry in the credits audit log. The APEX_CREDITS schema has APPROVER_ID and AUDIT_REF fields. The scenario states invoice modifications require a manual ticket to the Aurum support team (48-hour turnaround). It is not confirmed whether Sandra's "manual override" uses this ticket process or a different mechanism.
> **If the answer is "she emails the Aurum support team with the credit details — they apply it and return a confirmation":** The existing write path is a manual email ticket process. A programmatic integration could auto-submit the ticket with pre-populated fields, eliminating the manual drafting step. APPROVER_ID capture must happen in CRM before ticket submission since Aurum provides no authenticated approval mechanism.
> **If the answer is "she types directly into Aurum through a form or interface":** Aurum has a write interface Sandra can access — potentially exploitable for a direct programmatic write path. This is the highest-value answer; it means T-011 may be buildable without a workaround. Follow-up: does that interface have field-level access control (could it enforce APPROVER_ID)?
> **Why this matters more than a generic question:** The exact mechanics of Sandra's credit application is the only way to confirm or rule out the APEX_CREDITS programmatic write path (D4 A-5, D5 G-1) — the highest-consequence unknown in the entire build.

---

> **Q9: Who, at Apex, is authorised to approve a credit — and does the level of approval depend on the credit amount? Is there a threshold above which a manager must sign off?**
> **Category:** C — Governance and approval constraint
> **What I already infer from the scenario:** APEX_CREDITS artefact shows two distinct APPROVER_IDs: U-0042 and U-0089 — suggesting at least two different approvers exist. Artefact 2 shows Sandra applied a credit without any confirmed approval step. The SOP does not specify an approval hierarchy for credits. D4 A-6 flags the approval threshold as TBD.
> **If the answer is "any billing agent can approve credits below £X; above £X it needs a manager":** The approval threshold (ET-006 in D4) can be configured. Two approval tiers are buildable. The CRM workflow must route to different approver queues based on CREDIT_AMT.
> **If the answer is "there's no formal threshold — Sandra just applies what she thinks is right":** No approval hierarchy currently exists. Formalising one is a prerequisite for the agent design. Sarah must define the threshold before deployment. The agent cannot route to a "senior approver" if no such role is formally designated.
> **Why this matters more than a generic question:** The approval threshold value is the only missing parameter in ET-006 (D4 §6) — without it, high-value credit routing cannot be configured.

---

> **Q10: Has it ever happened, under time pressure or when the approver was unavailable, that a credit was applied without the normal review step? If so, what was the team's response?**
> **Category:** C — Governance and approval constraint
> **What I already infer from the scenario:** Artefact 2 confirms at least one credit was applied without an audit log entry. The internal note flags this as a known gap. Whether this is a one-off or a pattern is not stated (D4 A-3 rates this as "medium confidence — one confirmed miss; population rate unknown").
> **If the answer is "it happens occasionally when Sandra is under pressure — nobody follows up":** The audit bypass is a cultural norm, not an exception. This changes the governance design: a soft procedural control will be bypassed again. The system-enforced approval gate (CRM workflow locking the write until APPROVER_ID is confirmed) is not a nice-to-have — it is the only defence. Sarah must understand that the agent is designed to close this gap at the system level, not rely on procedural discipline that has already demonstrably failed.
> **If the answer is "Artefact 2 is the only time — we flagged it and it won't happen again":** The bypass was an exception that has been addressed. The governance gap risk is lower than assumed. The system-enforced gate is still required by design, but the calibration of urgency in the stakeholder conversation changes.
> **Why this matters more than a generic question:** The cultural frequency of audit bypasses determines whether the CRM workflow enforcement gate is politically sensitive (Sarah may not want to surface how often it has happened) or straightforwardly welcome — which affects how to frame the agent's compliance KPI.

---

### Category D: Exception patterns and escalation triggers

---

> **Q11: You have a customer — I won't name them — with three open fuel surcharge damage disputes simultaneously, the oldest dating back to late February. Is this known, and what's the current plan for that account?**
> **Category:** D — Exception patterns and escalation triggers
> **What I already infer from the scenario:** APEX_DISPUTES_OPEN shows customer C-04451 (Hayes & Sons Ltd) with three open FUEL_SURCH_DAMAGE disputes (D-2026-00342, D-2026-00337, D-2026-00318) spanning 14 February to 15 April 2026, all assigned to Sandra W. The pattern has not been escalated or flagged in any artefact.
> **If the answer is "no — we didn't know this was building up":** The repeat dispute pattern is invisible in the current process — Sandra handles each dispute individually without a systemic view. This confirms ET-005 (repeat pattern escalation) is a net-new capability the agent introduces, and it has immediate value. The Hayes & Sons case becomes the primary demonstration case for the COO.
> **If the answer is "yes — we know, and there's an ongoing commercial conversation with that account":** The escalation path for repeat disputers exists informally (via account management, not billing). The agent's ET-005 must route to whoever owns the commercial conversation, not just the senior billing agent. The routing target for ET-005 needs to be confirmed.
> **Why this matters more than a generic question:** The answer determines whether ET-005 is a new capability or a formalisation of an existing one — and whether the routing target is billing-team-internal or requires a cross-team handoff.

---

> **Q12: What proportion of billing disputes fall outside the three standard categories — fuel surcharges, dimensional weight, and redelivery fees? What do the non-standard ones tend to be about?**
> **Category:** D — Exception patterns and escalation triggers
> **What I already infer from the scenario:** APEX_DISPUTES_OPEN artefact shows only FUEL_SURCH_DAMAGE, DIM_WEIGHT, and REDELIVERY_FEE dispute types across the sample. D4 §8 Hard Stop 2 requires ET-002 for any type outside this taxonomy. The full population rate of out-of-taxonomy disputes is unknown.
> **If the answer is "less than 5% — nearly everything is one of those three":** The taxonomy is effectively complete. ET-002 is a low-frequency safety net. The HITL rate for out-of-taxonomy cases is a small proportion of total volume. The agent's primary value is in the three defined types.
> **If the answer is "10-20% or more — we get insurance claims, contract disputes, late delivery penalties":** The defined taxonomy covers only a fraction of real dispute volume. The agent's scope statement needs revision — either expand the taxonomy (which requires additional validity rules) or clarify that a significant fraction of WS4 volume falls outside the BDRA's scope from day one. The handle-time improvement and TCO calculations from D3 must be rebaselined.
> **Why this matters more than a generic question:** This directly determines the agent's coverage rate — the percentage of WS4 cases it can handle vs. the percentage it must immediately escalate via ET-002.

---

> **Q13: When a redelivery fee is disputed and the original delivery failed because of something Apex did — wrong address used, driver error — is the fee waived as a matter of course, or does it go through the same review process?**
> **Category:** D — Exception patterns and escalation triggers
> **What I already infer from the scenario:** APEX_DISPUTES_OPEN shows one REDELIVERY_FEE dispute (D-2026-00337, Hayes & Sons, £60.00, AWAITING_CUST). The scenario does not state Apex's policy on Apex-fault redeliveries. The distinction between Apex-fault and recipient-fault is the primary design fork for the REDELIVERY_FEE branch of T-007.
> **If the answer is "yes — if it's our fault, we always waive it, no approval needed":** REDELIVERY_FEE Apex-fault cases become a HIGH-confidence autonomous verdict (confidence 0.92). The agent checks the Driver App fault record, confirms Apex-fault, and generates an automatic waiver recommendation. HITL rate for this sub-type drops to near zero.
> **If the answer is "even if it's our fault, it still goes through the approval process":** The fault determination does not change the approval requirement, only the expected outcome. T-007 confidence for Apex-fault cases remains in the HITL zone (~0.70). The agent flags the Apex-fault context for the human reviewer but cannot autonomously recommend a waiver.
> **Why this matters more than a generic question:** This single policy answer determines whether the Apex-fault REDELIVERY_FEE sub-type achieves autonomous resolution — a direct change to the HITL rate target.

---

### Category E: Data and system reality

---

> **Q14: When a driver delivers a consignment and the customer reports it damaged, what gets recorded in the CRM or the Driver App at the time of delivery — is there a structured field for the delivery condition, and how consistently do drivers fill it in?**
> **Category:** E — Data and system reality
> **What I already infer from the scenario:** The Driver App replaced DispatchHub in October 2024 and supports scan-on-delivery and driver-to-dispatch messaging (scenario_context.md §6). Whether a structured delivery condition field exists (DAMAGED / DELIVERED_OK / REFUSED) is not stated. Artefact 1 (driver voicemail) suggests verbal communication is still the norm for exceptions — the driver phoned dispatch rather than recording a structured exception in the app.
> **If the answer is "yes — the Driver App has a structured delivery outcome field and drivers fill it in consistently":** Step 2 of the FUEL_SURCH_DAMAGE validity check (delivery context) is buildable. The agent queries the CRM for the delivery outcome, finds DAMAGED, and uses it as evidence in the validity verdict. Confidence for damage-confirmed cases rises. The field name and population rate are the follow-up questions.
> **If the answer is "no — drivers call it in verbally, or it's in free-text notes":** Structured delivery outcome data is unavailable. Step 2 of T-007 for FUEL_SURCH_DAMAGE returns UNVERIFIABLE for most cases, keeping HITL rates high for the most common dispute type. The agent's evidence package includes the delivery case notes but cannot assign a structured damage verdict.
> **Why this matters more than a generic question:** The delivery outcome field is the primary evidence input for FUEL_SURCH_DAMAGE validity assessment — its availability and consistency is the single biggest lever on the autonomous verdict rate for the most common dispute type.

---

> **Q15: When you look up a customer's account before deciding whether to offer a credit, is there anything you check beyond the current invoice and dispute — for example, their payment history, their account tier, or their standing with the commercial team?**
> **Category:** E — Data and system reality
> **What I already infer from the scenario:** APEX_CUSTOMER_MASTER is referenced in the agent's autonomy matrix for inactive/collections/payment plan account status. The agent's CUSTOMER_MASTER check is monthly (export cadence). The specific fields and account status values in APEX_CUSTOMER_MASTER are not provided in any artefact (D4 revision 1 Q-BUILD-8).
> **If the answer is "yes — we check whether they're in arrears, whether they're a key account, whether there are any commercial flags":** The agent must integrate APEX_CUSTOMER_MASTER data and potentially CRM account tier fields. The monthly export frequency may be too stale for high-risk-account decisions; a more frequent check or a CRM account flag may be required. This also determines whether the "Human Takes Over" condition in the autonomy matrix (inactive/collections/payment plan) covers the real set of risky account states.
> **If the answer is "no — we just look at the dispute on its own merits":** Account-level context does not factor into billing dispute decisions at Apex. The APEX_CUSTOMER_MASTER check in the autonomy matrix is a governance safeguard (prevent credits to accounts in collections), not a decision input. The design is simplified — monthly staleness is acceptable for a safety check, not a primary input.
> **Why this matters more than a generic question:** The answer determines the APEX_CUSTOMER_MASTER integration scope and whether the monthly export cadence is acceptable or needs supplementation.

---

> **Q16: When a customer contacts you about a billing dispute — what channel do they use? Is it primarily email, phone, or the CRM portal? And when it arrives, does it land directly in a CRM case queue or does someone have to manually create the case?**
> **Category:** E — Data and system reality
> **What I already infer from the scenario:** Artefact 2 is an email thread between Hayes & Sons and Sandra — suggesting at least some disputes arrive by email. The scenario confirms a Salesforce-based CRM with REST APIs but does not specify the intake mechanism. Whether inbound emails automatically create CRM cases or require manual case creation is not stated.
> **If the answer is "email is primary and it auto-creates CRM cases via email-to-case":** The agent's inbound trigger is a CRM case creation event (webhook or queue poll). T-001 processes structured CRM case text. Invoice number extraction works on whatever the customer put in the email subject or body. The intake path is well-defined.
> **If the answer is "email is primary but Sandra manually creates the CRM case after reading it":** The agent must be triggered from the manual CRM case creation event — it cannot read raw inbound email. Sandra's manual case creation step must be preserved in the workflow; the agent fires after it. Alternatively, email-to-case configuration is a prerequisite for automated intake.
> **Why this matters more than a generic question:** The intake channel determines the agent's trigger mechanism (T-001 architecture) and whether a Salesforce email-to-case configuration is a prerequisite or the work is already done.

---

### Category F: Organisational and trust context

---

> **Q17: The 2024 RPA project for billing reconciliation broke when Aurum's schema changed. This new agent reads from the same Aurum exports. What would you need to see in the first 30 days to believe this time is different?**
> **Category:** F — Organisational and trust context
> **What I already infer from the scenario:** The RPA failure is confirmed; the COO is aware of it. The scenario states Aurum schema changes "approximately quarterly without prior notice." The new agent design includes schema-change detection (D4A build loop — `aurum_ingestion.py` raises SchemaChangeAlert on header mismatch, halting processing and switching to 100% HITL). Sarah's trust is not generic — it is specifically conditioned on the Aurum schema fragility she has already experienced.
> **If the answer is "I want to see it handle a schema change gracefully — not just stop, but tell us what changed and keep working on what it can":** The schema-change alert design is exactly right; the question is whether the fallback to 100% HITL is acceptable or whether partial graceful degradation is expected (e.g., agent continues processing non-Aurum fields while flagging the schema gap). This would change the SchemaChangeAlert handling in the ingestion layer.
> **If the answer is "I want to see the audit trail working perfectly before I care about anything else":** Sarah's threshold is the compliance fix, not the efficiency gain. The deployment order should be: audit trail compliance first (daily APEX_CREDITS scan operational, APPROVER_ID gate enforced), then efficiency improvement. Phasing the deployment around compliance before automation is the right trust-building sequence.
> **Why this matters more than a generic question:** Sarah's specific trust condition shapes the deployment phasing — whether we lead with efficiency (handle time) or compliance (audit trail) in the first 30-day milestone.

---

> **Q18: If this agent reduces the time your billing team spends assembling dispute evidence from roughly 28 minutes per case to 8–10 minutes, what does Sandra do with the rest of her time? Is there already a plan for where that capacity goes?**
> **Category:** F — Organisational and trust context
> **What I already infer from the scenario:** Sandra currently handles billing disputes and delivery exceptions (scenario_context.md: "handles billing disputes and delivery exceptions"). With 60 billing disputes/day at 28 min/case, Sandra and colleagues spend approximately 1,680 minutes/day on this work stream. The scenario does not state a headcount split or indicate whether capacity freed by automation has been discussed.
> **If the answer is "yes — we have more WS1 exception cases than Sandra can handle; she'd move to that":** The redeployment is already identified and valued. The ROI case for the agent is strengthened beyond the billing dispute saving — it frees capacity for a higher-value work stream. Stakeholder resistance from the billing team is lower because no job is being eliminated, only rebalanced.
> **If the answer is "honestly, we haven't thought about it — I just assumed we'd save money":** The labor impact has not been planned. This is an organisational design gap that Sarah needs to address before deployment. An agent that frees 18 minutes per case × 60 cases/day = ~1,080 agent-minutes/day but has no plan for the freed capacity will either generate internal resistance (Sandra feels displaced) or the savings will be absorbed by slack, not redeployed. The FDE should raise this explicitly: the efficiency gain has two failure modes — the team resists the agent, or the savings evaporate.
> **Why this matters more than a generic question:** An unplanned labor transition is one of the most common reasons an agent succeeds technically but fails organisationally — this question surfaces that risk before build starts.

---

## 3. Questions you are NOT asking — and why

> **Question not asked:** "Can you walk me through your current billing dispute process from start to finish?"
> **Why not:** We already have the lived process reconstructed from Artefacts 2 and 5 — the email thread, the credit ledger, and the open disputes export. Asking for a process walkthrough would signal we haven't read the artefacts, waste the stakeholder's time confirming what we already know, and produce a documented process answer rather than the lived-process specifics we actually need. Our questions are deliberately targeted at the gaps the artefacts leave open.

---

> **Question not asked:** "What systems does your team use for billing disputes?"
> **Why not:** The scenario names all four systems (Salesforce CRM, Aurum Billing, Driver App, Dispatch console) and their integration constraints. Asking this would confirm facts we already have, signal insufficient preparation to Sarah, and consume question budget that should go toward the operational unknowns (how those systems are actually used in practice).

---

> **Question not asked:** "How many billing disputes does your team handle per day?"
> **Why not:** Already stated in the scenario: approximately 60 disputes/day at an average of 28 minutes per case. Asking about volume confirms a number we already have. The question has no design fork for our purposes — we are not scoping the agent to a fraction of WS4 volume based on the answer.

---

> **Question not asked:** "Have you considered using AI before?"
> **Why not:** We know the answer — two prior initiatives (2024 customer chatbot, RPA billing reconciliation) both failed. Asking "have you considered AI" would be condescending to a COO who commissioned this assessment. What we need to know is not whether AI has been tried, but specifically what the trust conditions are following those failures — which Q17 addresses directly and concretely.

---

> **Question not asked:** "Is your team comfortable with AI making decisions?"
> **Why not:** This question has no design fork — "yes" and "no" lead to essentially the same agent design, because the governance hard constraints in D4 are non-negotiable regardless of team comfort level. It also invites a generic sentiment response rather than operational specifics. The organisational trust question (Q17, Q18) is framed around specific conditions (prior failure lessons, labor transition plan), not comfort level in the abstract.

---

## 4. Sequencing for a 60-minute discovery call

The call uses the broad → narrow → probe funnel from `references/discovery-questioning-patterns.md`. The primary interviewee is Sarah Whitmore (COO). Questions marked † would benefit from a follow-up with Sandra W. or Apex IT if Sarah cannot answer them directly.

| Time slot | Question(s) | Goal for this segment |
|---|---|---|
| 0–5 min | Context setting | Establish that this is a lived-process conversation, not a system audit. Confirm Sarah is the right person for governance and policy questions; identify whether Sandra should join for process mechanics questions. Ask roughly what fraction of Sarah's attention WS4 billing disputes consume vs. the other three work streams. |
| 5–15 min | **Q4** (FUEL_SURCH_DAMAGE real case walkthrough), **Q7** (credit amount rule vs. judgement) | Determine whether the credit policy is a codifiable rule or tacit judgement — the binary that gates the entire T-009 capability. One real case trace extracts more than ten general questions. |
| 15–30 min | **Q8** (exact mechanics of credit application — what Sandra does in which system) †, **Q3** (fuel surcharge rate schedule location) | Confirm or rule out the APEX_CREDITS programmatic write path (the highest-consequence unknown in the build). Establish whether Step 1 of T-007 (calculation verification) is buildable. If Sarah cannot answer Q8, note it as a confirmed follow-up with Sandra or Apex IT. |
| 30–45 min | **Q1** (credit policy existence and format), **Q10** (audit trail bypass frequency and awareness), **Q11** (Hayes & Sons repeat pattern — is it known?) | Establish the credit policy gap as a design prerequisite, not a nice-to-have. Surface the compliance exposure at the population level. The Hayes & Sons case is the concrete example that makes the audit trail gap visible to Sarah without requiring her to defend Sandra's individual behaviour. |
| 45–55 min | **Q9** (approval hierarchy and threshold), **Q17** (trust conditions after prior RPA failure), **Q18** (role impact — Sandra's freed capacity) | Determine ET-006 threshold and approval routing. Establish the deployment phasing Sarah would trust (compliance-first vs. efficiency-first). Surface the labor transition gap if it exists — this is where organisational resistance to the agent is most likely to originate. |
| 55–60 min | **Q16** (intake channel and CRM case creation) †, **Q13** (redelivery fee Apex-fault policy), close and next steps | Confirm the intake trigger architecture (T-001 design). Confirm or eliminate the highest-leverage autonomy upgrade in T-007 (Apex-fault redelivery waiver). Summarise the top three items needed from Sarah before build begins: (1) credit policy document, (2) confirmation of Aurum write path, (3) approval threshold value. |

**Post-call follow-up required (not appropriate for the 60-minute session with Sarah):**
- **Q14** (Driver App delivery condition field — population rate) — Sandra W. or Driver App technical owner
- **Q15** (APEX_CUSTOMER_MASTER fields and account status values) — Apex IT
- **Q5** (DIM_WEIGHT evidence standard and formula) — Sandra W. or Tom J.
- **Q12** (non-standard dispute type rate) — Sandra W. (she sees the full distribution)
- **Q2** (SOP ownership and update timeline) — whoever Sarah identifies as the SOP owner
