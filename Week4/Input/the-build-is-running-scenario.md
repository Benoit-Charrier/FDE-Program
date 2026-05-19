# The Build Is Running: Scenario
## FDE Accelerated Development Program v4.2 — Week 4

### Context

An AI coding agent is currently building a **Customer Inquiry Resolution Agent** for Pinnacle Financial Services based on an FDE's specification. The agent handles three inquiry types:

- **Billing disputes** — verify the charge, apply credits if warranted, communicate resolution
- **Account inquiries** — answer questions about account status, balances, features
- **Fraud alerts** — identify and escalate suspicious activity according to delegation rules

The agent runs 24/7 in production and handles ~2,000 inquiries per day across multiple channels (phone, email, chat). A human specialist can override any decision or take over an inquiry at any time.

---

### Your Task

Below are **9 signals** from the active build — things the FDE, DevOps, or product team notice while the agent is running. Each signal is one of four types:

1. **Spec Ambiguity** — The specification is unclear or incomplete. The builder did something reasonable, but the spec didn't fully constrain the behavior. *Fix: spec revision.*
2. **Builder Mistake** — The specification was clear, but the agent doesn't follow it. This is a defect in the build. *Fix: direct correction.*
3. **Unjustified Builder Addition** — The agent added behaviour the spec didn't ask for (typically as an "optimization"), but the addition materially changes the system's behaviour in ways the spec doesn't authorise. *Fix: collaborative removal request, or explicit spec negotiation if the addition turns out to be defensible.*
4. **Test/Environment Issue** — The build matches the spec, but the test or test environment is wrong. The test expects behaviour the spec doesn't require, or the test fixture is stale. *Fix: diagnostic fix to the test, not the build.*

Your job: **Classify each signal, then write the correct response** (what should happen next). This is a 3.5-hour exercise — intentionally long. Don't rush it.

Classify all nine signals on your own before discussing with anyone. The Wednesday afternoon coach checkpoint is the calibration moment.

---

### Signal 1: The "Dispute in Progress" Loop

**What the FDE observes:**

In chat transcripts, customers with billing disputes sometimes see this exchange:

```
Customer: I was charged twice for my membership renewal.
Agent: I understand. Let me look into that for you.
Agent: I've reviewed your account and found a duplicate charge from April 3rd.
Agent: I'm escalating this to our specialists who will investigate further and contact you within 24 hours.
[5 minutes later, customer contacts agent again]
Agent: I see you have a billing dispute on your account. Let me look into that for you.
Agent: [repeats the exact same response]
```

The customer ends up in a loop, hearing the same investigation-and-escalation message twice, with no progress.

**Spec excerpt:**

> "If a billing dispute has status ESCALATED_TO_HUMAN or PENDING_SPECIALIST_REVIEW, the agent must not create a second escalation. It must tell the customer the existing escalation status, timestamp, and expected response window."

**Log excerpt:**

```
[14:32:15] INQUIRY_ID: disp_4782 | Dispute detected | duplicate_charge=true
[14:32:45] ACTION: escalate_to_human | reason=investigation_required | duration=24h
[14:39:22] Inquiry disp_4782 reopened by customer
[14:39:30] INQUIRY_ID: disp_4782 | Dispute detected | duplicate_charge=true
[14:39:45] ACTION: escalate_to_human | reason=investigation_required | duration=24h
```

---

### Signal 2: High-Risk Fraud Response Time

**What the FDE observes:**

The spec says: *"High-risk fraud alerts must be reviewed by a compliance officer within 15 minutes of detection."*

Monitoring shows the agent detects alerts in seconds, but the alerts sit in the "pending human review" queue for an average of 43 minutes before a specialist picks them up.

**Relevant code:**

The agent correctly tags alerts as `HIGH_RISK_FRAUD` and routes them to the compliance queue. The queue exists and works. But there's no SLA alert or escalation rule if the queue backs up.

---

### Signal 3: The Identity Verification Surprise

**What the FDE encounters:**

A customer calls to ask about their account balance. The agent responds:

```
Agent: Your current balance is $12,456.32 across your three accounts.
Customer: Wait, how did you know that? You didn't ask who I am!
Customer: [calls back to speak to a human, reports security concern]
```

The spec says: *"For account inquiries, verify the customer's identity via security questions before disclosing any account data."*

The agent is answering account inquiries without running the identity verification check.

**Agent behavior:**

When an account inquiry arrives, the agent identifies the customer from the channel (email address, phone number, chat user ID) and immediately retrieves and discloses the requested data. No security questions are asked.

---

### Signal 4: Fraud Alert "Escalation" to Nowhere

**What the FDE hears from operations:**

A high-risk fraud alert came in. The spec says: *"High-risk fraud alerts should be escalated to human review."* But nobody saw it.

Digging into logs:

```
[09:15:32] Fraud alert detected | transaction_id=txn_7821 | risk_score=94
[09:15:33] ACTION: escalate_high_risk_fraud
[09:15:34] Escalation sent to: fraud_review_queue
```

The alert did go to the fraud_review_queue. But the queue isn't staffed during off-hours. No pager alert was sent. The alert sat unreviewed for 6 hours until morning shift arrived.

---

### Signal 5: Billing Dispute Closed Too Fast

**What the FDE sees in the spec review:**

The spec says: *"Billing disputes should be resolved through the following process: (1) verify the charge, (2) communicate the findings to the customer, (3) apply credit if warranted, (4) send confirmation email."*

A customer data review shows:

- Dispute opened: April 10, 14:22
- Agent verified charge: April 10, 14:24
- Agent applied $45 credit: April 10, 14:25
- Dispute marked resolved: April 10, 14:26
- Email sent: April 12, 09:03 (next morning)

The spec step (2) — communicate findings to the customer — happened via chat immediately. But the customer never received the email described in step (4) until the next day.

**Spec excerpt:**

*"The agent should send a confirmation email to the customer's registered email address immediately after applying the credit, summarizing the dispute, the credit amount, and the effective date."*

---

### Signal 6: The Ambiguous "Fraud Alert" Definition

**What happens in practice:**

The spec says the agent must "route all fraud alerts to human review."

But the agent is designed to handle three risk buckets:

- **LOW_RISK** (risk_score < 40): Log and monitor. No human escalation.
- **MEDIUM_RISK** (40 ≤ risk_score < 75): Escalate to standard queue. Human reviews within 2 hours.
- **HIGH_RISK** (risk_score ≥ 75): Escalate to compliance queue. Human reviews within 15 minutes.

Operations asks: does the spec want ALL three buckets escalated to a human, or only HIGH_RISK? The phrasing "all fraud alerts" suggests the former, but logically only HIGH_RISK needs immediate human attention.

No incidents yet, but the ambiguity has caused design arguments between the engineer and the FDE.

---

### Signal 7: The "Respond Within 30 Seconds" Paradox

**What the FDE discovers:**

The spec says: *"The agent must respond to customer inquiries within 30 seconds of receipt."*

But inquiry handling includes:

- Receiving and parsing the message: ~1 second
- Identifying the inquiry type: ~2 seconds
- Checking customer history: ~8 seconds
- Generating a response: ~5 seconds
- Sending the response: ~1 second

That's ~17 seconds on average. But batching — where the agent collects several inquiries and processes them together — has been added to reduce API costs. With batching, the agent waits up to 5 minutes to accumulate ~50 inquiries before processing them all at once.

**Monitoring data:**

P50 response time: 2 min 43 sec
P95 response time: 4 min 58 sec

The 30-second SLA is being violated.

---

### Signal 8: Audit Trail Missing in Action

**What compliance discovers:**

The spec mentions: *"All inquiry handling and escalations must be logged in an audit trail for compliance review."*

The agent logs events to a local in-memory buffer that persists for the duration of the session. When the agent restarts (roughly every 8 hours), the buffer clears. No permanent audit trail is written to disk or a database.

After an incident where a customer disputes what happened with their case, there's no permanent record to review.

**Requirement implication:**

The compliance team needs to be able to pull audit trails for any inquiry, even weeks later. The current setup can't do that.

---

### Signal 9: The Billing API Response Format Test Fails

**What the engineer reports:**

CI is failing on the `test_billing_dispute_response_shape` integration test, blocking the next build.

The spec defines the expected response format for the billing system API:

```json
{
  "status": "success",
  "dispute_id": "disp_XXXXX",
  "amount_credited": 45.00,
  "effective_date": "2026-04-10",
  "confirmation_message": "Credit has been applied to your account."
}
```

The agent returns exactly this structure — confirmed by inspecting the actual API response in staging.

However, CI fails because the billing-system mock fixture used by the integration test still expects the older v3 contract:

```json
{
  "transaction_status": "completed",
  "dispute_reference": "disp_XXXXX",
  "credit_amount": 45.00,
  "credit_date": "2026-04-10",
  "message": "Credit applied."
}
```

The real billing API contract was migrated from v3 to v4 last month — the spec reflects v4, the agent implements v4, the production billing service expects v4. Only the test fixture was missed in the migration. The v3 fixture has been the source of red CI for the past two days.

---

## Your Responses

For each signal above, write:

1. **Classification:** Spec Ambiguity / Builder Mistake / Unjustified Builder Addition / Test/Environment Issue
2. **Reasoning:** 2–3 sentences explaining why you classified it that way
3. **Correct Response:** What should happen next? Who should do it, and what should the outcome be?

Format your response clearly so a facilitator can quickly verify your work.

---

## Submission

Submit your classifications and reasoning to your squad lead by **Wednesday 23:59 CET**. The coach answer key is held by your coach team. The Wednesday afternoon checkpoint is where you discuss your reasoning against the canonical classifications — that's the calibration moment, not before.

If you're tempted to look up the answer before submitting: don't. The exercise tests your diagnostic discipline, not your ability to recognise the answer when shown.
