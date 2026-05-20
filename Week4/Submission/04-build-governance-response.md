# Gate 4 — D4: Build Governance Response ("The Build Is Running")
**Scenario:** Customer Inquiry Resolution Agent — Pinnacle Financial Services
**Date:** 2026-05-19

---

## Classification Summary

| Signal | Classification | Fix Owner |
|--------|---------------|-----------|
| S-1: Dispute in Progress Loop | Builder Mistake | Builder |
| S-2: High-Risk Fraud Response Time | Spec Ambiguity | FDE |
| S-3: Identity Verification Surprise | Builder Mistake | Builder |
| S-4: Fraud Alert Escalation to Nowhere | Spec Ambiguity | FDE |
| S-5: Billing Dispute Closed Too Fast | Builder Mistake | Builder |
| S-6: Ambiguous Fraud Alert Definition | Spec Ambiguity | FDE |
| S-7: Respond Within 30 Seconds Paradox | Unjustified Builder Addition | Builder (collaborative) |
| S-8: Audit Trail Missing in Action | Spec Ambiguity | FDE |
| S-9: Billing API Response Format Test Fails | Test/Environment Issue | Test author |

---

## Signal 1: The "Dispute in Progress" Loop

**Classification: Builder Mistake**

**Reasoning:**

The spec is unambiguous: *"If a billing dispute has status ESCALATED_TO_HUMAN or PENDING_SPECIALIST_REVIEW, the agent must not create a second escalation."* The log confirms the same inquiry ID (`disp_4782`) is escalated twice within 7 minutes. The agent queried the dispute, found `duplicate_charge=true`, and escalated — twice — without ever checking the current status. There is no ambiguity in what the spec requires. The builder read the dispute-detection logic but did not implement the pre-check that guards against re-escalation.

**Correct Response:**

Direct builder correction. Do not rewrite the spec. Re-prompt the builder with the exact spec section highlighted:

> The spec says: *"If a billing dispute has status ESCALATED_TO_HUMAN or PENDING_SPECIALIST_REVIEW, the agent must not create a second escalation. It must tell the customer the existing escalation status, timestamp, and expected response window."*
>
> Your implementation creates a new escalation every time a dispute is detected, regardless of existing status. Please revise:
> 1. Before escalating, check `dispute.status` against `[ESCALATED_TO_HUMAN, PENDING_SPECIALIST_REVIEW]`
> 2. If status is already one of those: return a response with the existing escalation timestamp and the expected response window. Do not call `escalate_to_human`.
> 3. Only call `escalate_to_human` if dispute status is NOT already escalated.

---

## Signal 2: High-Risk Fraud Response Time

**Classification: Spec Ambiguity**

**Reasoning:**

The spec states *"High-risk fraud alerts must be reviewed by a compliance officer within 15 minutes of detection."* The agent correctly detects alerts in seconds and routes them to the compliance queue — that part is implemented per spec. The problem is that the spec establishes a 15-minute SLA but gives no instruction for what the agent should do to *enforce* that SLA if humans don't act in time. Should the agent send a pager alert? Escalate to a manager after 10 minutes? Notify a backup responder? The builder implemented "route to queue" (a defensible reading of "must be reviewed") but the spec is silent on the enforcement mechanism. The 43-minute average review time is a process failure, but it traces back to an FDE spec gap, not a build defect.

**Correct Response:**

Spec revision required. Add an explicit SLA enforcement mechanism:

> **Revised spec addition for §Fraud Alert Handling:**
> When a HIGH_RISK fraud alert is routed to the compliance queue, start a 10-minute countdown timer. If no compliance officer has accepted the alert within 10 minutes, the agent must:
> - Send an immediate PagerDuty alert to the on-call compliance officer
> - Escalate to the compliance team lead via SMS at 12 minutes
> - Log a `SLA_BREACH_IMMINENT` event with timestamp and alert ID
>
> This enforcement applies 24/7, including off-hours.

---

## Signal 3: The Identity Verification Surprise

**Classification: Builder Mistake**

**Reasoning:**

The spec says: *"For account inquiries, verify the customer's identity via security questions before disclosing any account data."* The agent skips this step entirely — it identifies the customer from the channel (email, phone, chat ID) and immediately discloses account data. Channel identification is not the same as identity verification via security questions. The spec is explicit: security questions are required before disclosure. The builder conflated "I know who called" with "I've verified who called." This is a direct contradiction of a clear spec requirement — there is nothing ambiguous about "verify via security questions before disclosing."

**Correct Response:**

Direct builder correction — high priority, security incident risk:

> The spec says: *"For account inquiries, verify the customer's identity via security questions before disclosing any account data."*
>
> Your implementation identifies the customer from channel metadata and immediately returns account data without running identity verification. This is a security violation.
>
> Please revise:
> 1. When an account inquiry arrives, do NOT retrieve or return any account data
> 2. First, run the identity verification flow: prompt the customer with security questions as defined in the identity verification module
> 3. Only if verification passes (customer answers correctly): retrieve and return the requested account data
> 4. If verification fails: do not disclose account data; offer to escalate to a human specialist

---

## Signal 4: Fraud Alert "Escalation" to Nowhere

**Classification: Spec Ambiguity**

**Reasoning:**

The spec says *"High-risk fraud alerts should be escalated to human review."* The agent did exactly that — the alert was sent to `fraud_review_queue`. The log confirms it. The spec's definition of "escalated to human review" was satisfied by routing to the queue; the spec gave no further instruction about what happens when that queue is unmonitored, what off-hours coverage requires, or whether the agent should verify the escalation is acknowledged. The builder implemented routing correctly. The operational gap (queue unstaffed, no pager) is real and dangerous — but it traces to a spec that defined the agent's action (route to queue) without defining the full operational context (24/7 monitoring, alerting, SLA on acknowledgement). This is the same root category as S-2: the spec stated a destination, not the enforcement.

**Correct Response:**

Spec revision required. Add off-hours escalation path:

> **Revised spec addition for §High-Risk Fraud Alert Handling:**
> The agent must escalate HIGH_RISK fraud alerts via two mechanisms:
> 1. Route alert to `fraud_review_queue` (existing)
> 2. Simultaneously send a PagerDuty notification to the on-call fraud analyst, 24/7
>
> The agent must not treat queue routing alone as a completed escalation. Escalation is complete only when the on-call analyst acknowledges the PagerDuty alert. If not acknowledged within 5 minutes, escalate to the fraud team lead.

---

## Signal 5: Billing Dispute Closed Too Fast

**Classification: Builder Mistake**

**Reasoning:**

The spec says: *"The agent should send a confirmation email to the customer's registered email address **immediately** after applying the credit."* The timeline shows: credit applied April 10 at 14:25, email sent April 12 at 09:03 — approximately 18+ hours later. The spec word "immediately" is clear in context: it means as part of the same dispute-resolution transaction, not queued for the following business day. The builder appears to have implemented the email send as a background job or scheduled delivery, not as a synchronous step in the resolution flow. The word "immediately" is not ambiguous; the builder chose a non-immediate delivery mechanism without spec authorization.

**Correct Response:**

Direct builder correction:

> The spec says the confirmation email must be sent *"immediately after applying the credit."*
>
> Your implementation sends the email the following morning (18+ hours after credit is applied). This is not "immediately."
>
> Please revise:
> 1. The email send must be a synchronous step in the dispute resolution sequence — called immediately after `apply_credit()` succeeds
> 2. The dispute must not be marked `RESOLVED` until the email is sent (or send is confirmed queued for near-immediate delivery with retry)
> 3. If email delivery fails, log the failure and alert operations — do not silently drop it
> 4. The correct sequence is: verify → communicate → apply credit → send email → mark resolved

---

## Signal 6: The Ambiguous "Fraud Alert" Definition

**Classification: Spec Ambiguity**

**Reasoning:**

The spec says *"route all fraud alerts to human review"* — the phrase "all fraud alerts" is ambiguous because it doesn't define what risk threshold constitutes an event worth calling a "fraud alert." The builder's 3-tier design (LOW_RISK: log-only; MEDIUM_RISK: standard queue; HIGH_RISK: compliance queue) is a reasonable, professionally sound implementation — but it contradicts a literal reading of "all." At the same time, a system that routes 100% of flagged transactions including low-confidence noise to human review would create queue overload. Both the literal reading ("all") and the practical reading ("high-risk only") are defensible. The spec writer used a shorthand phrase without defining its scope. The design disagreement between engineer and FDE is the diagnostic signal: two reasonable professionals read the same sentence differently.

**Correct Response:**

Spec revision required. Define escalation tiers explicitly:

> **Revised spec for §Fraud Alert Escalation Policy:**
> Fraud signals are categorised by risk score as follows:
> - **LOW_RISK** (risk_score < 40): Log event. No human escalation. Agent may take automated preventive action (e.g., flag transaction for monitoring).
> - **MEDIUM_RISK** (40 ≤ risk_score < 75): Route to standard fraud review queue. Human reviews within 2 hours. Agent holds associated transaction pending review.
> - **HIGH_RISK** (risk_score ≥ 75): Route to compliance queue with PagerDuty alert. Human reviews within 15 minutes. Agent immediately freezes associated account pending review.
>
> "All fraud alerts" in the original spec refers to MEDIUM_RISK and HIGH_RISK events only. LOW_RISK events are logged but do not require human escalation.

---

## Signal 7: The "Respond Within 30 Seconds" Paradox

**Classification: Unjustified Builder Addition**

**Reasoning:**

The spec sets a clear, explicit SLA: *"The agent must respond to customer inquiries within 30 seconds of receipt."* The builder added batching — collecting ~50 inquiries over up to 5 minutes before processing — with no spec authorisation. This is not a spec ambiguity about response time; it is the builder adding an optimisation (batch API calls to reduce costs) that directly and measurably violates the spec's most explicit performance requirement. P50 response time is 2 min 43 sec; P95 is 4 min 58 sec. The builder may have had good intentions (cost reduction) but this is an unjustified addition: behaviour the spec did not request that materially degrades a spec-required property. No spec negotiation is needed — the spec SLA is not the ambiguous part. The batching behaviour is what doesn't belong.

**Correct Response:**

Collaborative removal request — acknowledge the intent, but the behaviour must be removed or rearchitected:

> We noticed you added batching (collect ~50 inquiries, process after up to 5 minutes) to reduce API costs. The intent makes sense, but this change directly violates the spec SLA: *"The agent must respond to customer inquiries within 30 seconds of receipt."* P50 response time is now 2:43; P95 is 4:58. Both breach the SLA.
>
> Please remove the batching behaviour. Every inquiry must be processed individually and responded to within 30 seconds.
>
> If cost reduction is a real concern, let's discuss it: either (a) raise the tradeoff to the FDE/client for a formal SLA renegotiation, or (b) explore cost optimisations that don't break the response-time guarantee (e.g., smaller model for classification, larger model only for response generation). Either path requires explicit spec authorisation before implementation.

---

## Signal 8: Audit Trail Missing in Action

**Classification: Spec Ambiguity**

**Reasoning:**

The spec says: *"All inquiry handling and escalations must be logged in an audit trail for compliance review."* The builder implemented logging to an in-memory buffer — technically a log for the session duration. The phrase "audit trail for compliance review" implies durability in any financial services context, but the spec never stated the storage medium, retention period, query access requirements, or durability guarantee. An in-memory implementation that clears every 8 hours is clearly inadequate for "compliance review" (which requires records retrievable weeks or months later), but the gap exists in the spec, not just in the build. The builder did implement logging — just not to a durable store. The spec's failure was stating the destination ("audit trail") without constraining the properties that make it a real audit trail. Both the FDE and the builder share responsibility for this gap.

**Correct Response:**

Spec revision first, then builder correction:

> **Revised spec addition for §Audit Trail Requirements:**
> All inquiry handling events and escalation actions must be written to a persistent, queryable audit log with the following properties:
> - **Storage:** Written synchronously to a durable database (not in-memory cache) on every event
> - **Retention:** Minimum 7 years (regulatory requirement for financial services)
> - **Fields required per record:** inquiry_id, event_type, timestamp_utc, agent_action, outcome, operator_id (if human took action), customer_id (hashed)
> - **Query access:** Compliance team must be able to retrieve all events for a given inquiry_id via admin dashboard, within 5 minutes of request
> - **Restart durability:** Audit log must survive agent restarts, crashes, and redeployments without data loss

---

## Signal 9: The Billing API Response Format Test Fails

**Classification: Test/Environment Issue**

**Reasoning:**

The spec defines the v4 API response format. The agent implements v4 — confirmed by inspecting the actual staging response. The production billing service uses v4. The only thing still using v3 is the CI test fixture, which was missed when the billing API contract was migrated last month. The build is correct; the spec is correct; the production environment is correct. Only the test fixture is stale. This is the textbook test/environment issue: the test is checking for behaviour the spec doesn't require (v3 field names), not a defect in the agent.

**Correct Response:**

Fix the test fixture — do not change the agent code or the spec:

> CI is failing because the billing-system mock fixture (`test_billing_dispute_response_shape`) still expects the v3 contract:
> - `transaction_status`, `dispute_reference`, `credit_amount`, `credit_date`, `message`
>
> The real billing API, the spec, and the agent all use v4:
> - `status`, `dispute_id`, `amount_credited`, `effective_date`, `confirmation_message`
>
> Update the test mock fixture to return the v4 structure. Do not modify the agent implementation or the spec. After the fixture is updated, re-run CI — this should clear the block.

---

## Diagnostic Reflection

**Distribution:** 3 Builder Mistakes / 4 Spec Ambiguities / 1 Unjustified Builder Addition / 1 Test Issue

**Pattern worth noting:** Four of the nine signals (S-2, S-4, S-6, S-8) share a common root: the spec defined *what* should happen without defining *how* the system should enforce it. Signal 2 sets a SLA without enforcement. Signal 4 names a destination without off-hours coverage. Signal 6 names a scope without a risk boundary. Signal 8 names an obligation without a storage contract. This is a recurring FDE failure mode: treating a statement of intent as a complete specification. In financial services, operational context is load-bearing — "reviewed by a human" means nothing if the queue isn't monitored.

**Tone calibration notes applied:**
- Builder Mistakes (S-1, S-3, S-5): Direct, specific, cite the exact spec sentence, give the corrective action.
- Spec Ambiguities (S-2, S-4, S-6, S-8): Acknowledge the builder's defensible interpretation before naming the gap; own the fix as the FDE.
- Unjustified Builder Addition (S-7): Acknowledge the intent (cost reduction is legitimate); separate the intent from the unauthorised implementation; offer a path forward.
- Test Issue (S-9): No blame; just fix the fixture.
