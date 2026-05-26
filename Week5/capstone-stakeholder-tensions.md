# Capstone Stakeholder Tensions: Week 5
## FDE Accelerated Development Program v4.0

### Introduction

Each capstone scenario presents a real-world stakeholder conflict. Your role as the FDE: navigate competing priorities, gather requirements from conflicting perspectives, and produce a **stakeholder alignment memo** that acknowledges the tensions, proposes a path forward, and gets buy-in from all parties.

You will receive email and Slack exchanges between executives with contradictory goals. Your job is to:

1. Identify the underlying concerns of each stakeholder
2. Clarify what's negotiable vs. non-negotiable
3. Propose a phased approach or compromise that addresses the real risks
4. Get signatures on a memo that commits all parties

**Time limit for this exercise:** 2 hours to analyze exchanges, write alignment memo, and socialize it.

---

## Option A: Healthcare Claims Processing

### Scenario Overview

Greenfield Health Systems processes ~50,000 medical claims per month via manual review. Cycle time: 8 days average. Errors: ~1.2%. Goal: Deploy an AI claims agent to accelerate processing and reduce errors.

### Key Stakeholders

- **CFO (Sarah Chen):** Cost reduction is her primary KPI. Every FTE saved improves margin.
- **Chief Medical Officer (Dr. Marcus Webb):** Clinical decisions are his domain. AI must not replace human judgment on claim denials or clinical questions.
- **VP Operations (James Liu):** Facing SLA penalties from payers for claims >7 days. Needs speed to avoid fines.

---

### Email / Slack Exchanges

#### Exchange 1: CFO → CMO (Email)

```
To: Dr. Webb
From: Sarah Chen (CFO)
Date: 2026-04-08
Subject: Claims Processing Automation — Headcount Plan

Marcus,

We've budgeted $400K for the AI agent implementation. The financial case depends on a 40% reduction in claims review staff — that's 8 FTEs over 6 months. Without that headcount reduction, this project doesn't pencil out. Our margin is under pressure, and I need to show the board we're getting serious about productivity.

The agent should handle ~70% of straightforward claims (routine billing reviews, prior auth checks). Our compliance team says 70% of volume is low-complexity. That means our staff goes from processing 100% to reviewing edge cases and appeals.

I'm scheduling a meeting with HR to start the transition planning. I'd rather we're aligned, but this is non-negotiable from a financial perspective.

Sarah
```

#### Exchange 2: CMO → CFO (Email Response)

```
To: Sarah Chen
From: Dr. Marcus Webb (Chief Medical Officer)
Date: 2026-04-08
Subject: RE: Claims Processing Automation — Headcount Plan

Sarah,

I appreciate the business pressure, but I have a fundamental concern: I can't delegate clinical judgment to a machine, even if it's "only" for 70% of claims. A "routine" claim can hide clinical complexity. Denying a claim for diagnostic imaging or a specialist consult affects patient care. I need a physician or advanced practice provider reviewing every claim with clinical implications.

Here's what I can live with:
- The agent handles administrative checks (eligibility, prior auth completeness, coding accuracy).
- A physician still reviews every claim that has clinical content before it's finalized.
- We can reduce admin staff, but not clinical review staff.

I get that you need cost savings, but not at the expense of patient safety or physician responsibility. And my team will not certify a system that bypasses clinical review, which means no claim can be denied without our approval.

Marcus
```

#### Exchange 3: Operations → CFO + CMO (Slack)

```
James Liu: Sarah, Marcus—we've got a problem. Our claims are sitting in queue for 9+ days now. Payers are threatening contractual penalties, and I'm absorbing the cost. We need to move fast.

Sarah Chen: That's exactly why we need the agent. Claims should drop to 3-4 days with automation.

James Liu: Agreed. But here's the tension: if we still run every claim through physician review, we're not actually reducing cycle time, just changing who does the work.

Dr. Marcus Webb: That's not quite right, James. The agent can do the upfront work (check if prior auth is in the file, verify coding accuracy). Then it routes clear cases to a faster-path approval, and complex ones to me. That's faster than today, where my team has to touch everything.

James Liu: OK, I hear you. But you need to commit to SLAs. If Marcus's team becomes a bottleneck, this fails. How fast can you turn around a routed claim?

Dr. Marcus Webb: My team can review ~20 claims per hour if they're pre-screened by the agent. That's faster than today's manual process where we read the whole file from scratch.

Sarah Chen: If Marcus's team reviews 20/hour and they work 8 hours a day, that's 160 claims/day per person. We have 1,667 claims/day. That's 10-11 physicians needed for clinical review. That defeats my headcount reduction goal.

James Liu: [pause]

Dr. Marcus Webb: Maybe we need to reframe what "clinical review" means. If the agent is really good at flagging claims with clinical content, and my team only touches those, maybe the volume is smaller than 70%.

Sarah Chen: What percentage would you actually need to touch?

Dr. Marcus Webb: Honestly? Maybe 30-35% of claims have genuine clinical content. The rest are billing and admin.

James Chen: If it's 35% physician review and 65% agent approval (with admin checks), we could reduce staff from 20 to 7, and you still get clinical oversight. That's a case I can take to the board.

Dr. Marcus Webb: That works for me, as long as the agent's clinical flagging is accurate and I'm not drowning in reviews.

James Liu: And if the agent-reviewed claims are solid, our cycle time drops to 4-5 days on the pre-approved path and 6-7 days on the clinical review path. That clears the penalty threshold.

Sarah Chen: Draft the requirements for what "clinical flagging" means. I want to see it on paper before I commit budget, but this seems worth exploring.
```

---

## Option B: Enterprise Procurement Intelligence

### Scenario Overview

MidCorp Inc. has 5 senior procurement leaders who make all supplier negotiation decisions. They spend ~40% of their time on research (supplier history, market rates, competitive intelligence). Goal: Deploy an AI procurement agent that generates negotiation briefings, finds cost optimization opportunities, and handles routine supplier communications.

Two of the five procurement leaders are retiring in 8 months. Recruitment for experienced procurement staff is slow. The system needs to be operational before they leave, or deal flow gets disrupted.

### Key Stakeholders

- **CPO (Chief Procurement Officer, Lisa Huang):** Timeline is critical. She has 8 months to get the system live before staff leaves. Any delay jeopardizes the transition.
- **CISO (Chief Information Security Officer, Rajesh Patel):** Procurement data (supplier terms, negotiation strategy, pricing history) is sensitive. He's worried about AI systems processing confidential M&A data and negotiation positions.
- **CFO (Robert Kim):** Questioning the ROI. "We've done this for 20 years without AI. Why now?" Wants proof before investing heavily.

---

### Email / Slack Exchanges

#### Exchange 1: CPO → CISO + CFO (Email)

```
To: Rajesh, Robert
From: Lisa Huang (CPO)
Date: 2026-04-08
Subject: Procurement AI Initiative — Timeline and Budget Request

Rajesh, Robert—

I need your alignment on a procurement intelligence agent initiative. Here's the urgency: Tom and Patricia retire in 8 months. They handle $120M in supplier relationships. If we lose that institutional knowledge without a transition plan, we're in trouble.

The agent would:
1. Analyze supplier data and market intelligence to brief negotiators
2. Flag cost savings opportunities in existing contracts
3. Automate routine communications (RFQ follow-ups, supplier inquiries)

Budget: $350K over 6 months. ROI: $2.5M in year 1 through cost avoidance and contract optimization. Payback period: 2 months.

Timeline: Live system by month 7, giving us 1 month to train on the system before Tom and Patricia leave.

Rajesh—I know you'll have security concerns. But we're talking about our own procurement data, not customer data. Standard confidentiality agreements apply. I think this is manageable.

Robert—This is about continuity and risk, not just efficiency. If we don't transition that knowledge, we'll lose negotiating power and spend money on rushed supplier searches.

I'd like to kick off design next week.

Lisa
```

#### Exchange 2: CISO → CPO (Email Response)

```
To: Lisa Huang
From: Rajesh Patel (CISO)
Date: 2026-04-09
Subject: RE: Procurement AI Initiative — Security and Data Concerns

Lisa,

I appreciate the business case, but I have serious reservations. Here's what keeps me up at night:

The agent would process:
- Supplier contract terms (confidential to the supplier)
- Our negotiation strategy and fallback positions
- Margin data and cost structures
- Competitive intelligence (what we know about other buyers' deals)
- M&A pipeline intelligence (if suppliers are consolidating, expanding, or divesting)

If this data is processed by an AI system, where does it go? Is it logged? Cached? Used for training? I've read enough about LLM data retention to be worried. One supplier figures out we shared their terms with an AI system, and we have a contract violation and a legal problem.

I'm not saying no. But I need to see:
1. Data handling and retention policy (what data the agent can access, where it's stored, who can audit it)
2. Encryption and access control specs
3. Third-party audit or compliance sign-off
4. A contractual framework for supplier data confidentiality

This isn't paranoia—this is responsible stewardship of sensitive business data. I'm happy to work on it, but I can't greenlight a system that touches procurement data without a serious security architecture first.

I'd estimate that security design adds 4-6 weeks to the timeline. That cuts into your 8-month window.

Rajesh
```

#### Exchange 3: CFO → CPO + CISO (Email)

```
To: Lisa, Rajesh
From: Robert Kim (CFO)
Date: 2026-04-09
Subject: RE: Procurement AI Initiative — ROI Challenge

Lisa, Rajesh—

I appreciate the proactive thinking, Lisa, but I need to push back on the financial case. You're projecting $2.5M in savings. From where?

You say the agent "flags cost savings." That's vague. In 20 years, our procurement team has already found the obvious cost savings. What new savings does an AI agent find that humans miss?

You say "automate routine communications." RFQ follow-ups take maybe 5 hours a week per person. That's real, but that's not $2.5M. Where's the big number coming from?

I'm concerned this is a "because AI" project rather than a "because we have a real problem" project. Our margins are fine. Our supplier relationships are stable. We've never lost a deal because we were slow on RFQ turnaround.

What I do support: a tool to help your team transition knowledge from Tom and Patricia before they leave. But that's a 3-month knowledge capture effort, not a $350K AI system.

Show me the actual cost savings model—not optimistic projections, but where AI specifically moves the needle. Then I'll listen.

Robert
```

#### Exchange 4: CPO → CFO (Slack)

```
Lisa Huang: Robert, I get the skepticism. Let me be more specific.

Last year we negotiated 47 supplier contracts. On 12 of them (25%), we accepted the first offer or minor variation. Analysis shows we likely left $3-5M on the table by not deeper research.

For example: One supplier quoted us $2.2M/year for logistics services. Our team didn't have time to research their market position and alternative vendors. We signed. A competitor later told us they negotiated the same service for $1.8M with a vendor we didn't consider.

The agent would:
1. Automatically pull public financial data, market reports, alternative vendor info for every RFQ
2. Flag if the bid seems high relative to market comparables
3. Brief the negotiator with that context before they accept a quote

That's not magic, but it's better research in less time. If we prevent even ONE $500K miss per year, the system pays for itself.

Robert Kim: That's more specific. Still seems optimistic, but I hear the logic. What about Rajesh's security concerns? Those are real.

Lisa Huang: They are. But I don't think they're a blocker if we architect correctly. We're not sending proprietary data to a cloud LLM. We're deploying an on-prem agent with encrypted access to our own databases. Supplier terms stay in our database; the agent queries, analyzes, and returns briefings. No data leaves our network.

That's more expensive and complex than a cloud solution, but Rajesh gets his controls, and we get the capabilities.

Robert Kim: OK. That changes the calculus. Let's talk security architecture. And let's be more conservative on the financial case—call it $1.5M ROI rather than $2.5M. If Rajesh can design it securely in 4-6 weeks, and you can build in 6-8 weeks, you're looking at a 12-14 week timeline. That's tight against your 8-month window, but doable.

Lisa Huang: Tight but doable. Let's set up a working group.

Robert Kim: I'll green light budget if the security architecture holds up. But no surprises. If Rajesh says it's a security risk, we pause.

Rajesh Patel: Fair. I'll work with the team on threat modeling and see if on-prem architecture closes the gaps. No promises yet.
```

---

## Option C: Multi-Channel Customer Resolution

### Scenario Overview

CloudServe Inc. operates a customer support center handling ~10,000 tickets/month across chat, email, and phone. Current process: Frontline agents triage, escalate to specialists, specialists resolve. Cycle time: 3-5 days. NPS: 6.2 (needs to be >7.0 for competitive positioning).

The company is considering an AI resolution agent that handles ~60% of issues end-to-end (resets, refunds, account updates, billing questions) without human intervention. Goal: improve NPS and reduce resolution time.

### Key Stakeholders

- **Chief Customer Officer (Amanda Torres):** NPS is her KPI. She's convinced that faster resolution and 24/7 AI availability will improve NPS. Wants aggressive AI deployment to "own the outcome."
- **Chief Compliance Officer (Jennifer Park):** Concerned that AI-driven decisions on refunds, account modifications, or service termination could trigger customer complaints that escalate to regulatory inquiry or litigation. Wants human approval for anything affecting customer entitlements.
- **CTO (David Okonkwo):** The existing telephony system is outdated (built in 2010, barely supported). He wants to rebuild it with modern infrastructure. AI agent is a nice feature, but only if it's built on the new stack. Current tech stack can't support AI integration safely.

---

### Email / Slack Exchanges

#### Exchange 1: CCO → CCC + CTO (Email)

```
To: Jennifer, David
From: Amanda Torres (Chief Customer Officer)
Date: 2026-04-08
Subject: Customer Resolution AI — Deploy Within 60 Days

Jennifer, David—

Our NPS has been stuck at 6.2 for two quarters. Competitors are at 7.5+. We need to move. I'm proposing an AI resolution agent for our support platform.

The agent would handle:
- Password resets and account access issues (28% of volume)
- Billing questions and invoice clarification (18% of volume)
- Refund and return requests (12% of volume)
- Service cancellations and downgrades (8% of volume)

That's ~66% of our ticket volume. Most of these are repetitive, low-risk decisions. The agent can resolve them in seconds via chat. 24/7 availability. No wait times.

Impact: Resolution time drops from 3-5 days to <5 minutes for 2/3 of customers. That moves the needle on NPS.

I want this live in 60 days. Let's do this.

Amanda
```

#### Exchange 2: CCC → CCO (Email Response)

```
To: Amanda Torres
From: Jennifer Park (Chief Compliance Officer)
Date: 2026-04-08
Subject: RE: Customer Resolution AI — Compliance and Risk

Amanda,

I hear the urgency on NPS, and I'm not opposed to the agent in principle. But I have a fundamental concern: the decisions you listed—refunds, cancellations, account modifications—affect customer entitlements. If the agent makes a wrong decision, the customer might pursue a chargeback, dispute, or complaint to a regulator.

For example:
- An agent refunds $500 due to a misunderstanding. Customer disputes the refund after fact, claiming they never authorized it. We might be on the hook for the charge back fee.
- An agent cancels a customer's service due to an account issue, and the cancellation affects their business. They claim we acted without due process and escalate to the state attorney general. Now we're in an inquiry.

I'm not saying AI can't help. But I need a human-in-the-loop for any decision that affects customer entitlements. That means:
- AI can suggest a refund; a human approves it.
- AI can flag a cancellation request; a human confirms before execution.

This slows things down compared to your 60-day aggressive timeline, but it keeps us out of compliance trouble.

I need sign-off from Legal on the AI decision logic before this goes live.

Jennifer
```

#### Exchange 3: CTO → CCO + CCC (Email)

```
To: Amanda, Jennifer
From: David Okonkwo (CTO)
Date: 2026-04-09
Subject: RE: Customer Resolution AI — Technical Architecture

Amanda, Jennifer—

I want to be supportive, but I need to be honest: our telephony system is a blocker. We're still running Avaya systems from 2010 with custom integrations to our support platform. An AI agent needs modern APIs, real-time message queuing, and cloud-native infrastructure.

We can't integrate an AI agent into the current stack safely. Any attempt will introduce architectural debt and instability.

I've been planning a platform modernization for 18 months. Estimated timeline: 6 months. Budget: $800K. New stack: cloud-native, containerized, modern APIs, built for integrations.

Here's what I propose:
1. We modernize the platform (6 months)
2. Then we integrate the AI agent into the new platform (4-6 weeks)
3. Go-live: month 7

That's 7 months, not 60 days. But it's sustainable and doesn't put us on a technical landmine.

I can't support deploying an AI agent on our current infrastructure in 60 days. It will break, and you'll all be in a war room at 2 AM on a Saturday.

Amanda, I get that you want speed. But I can't sign off on a design that puts the company at risk.

David
```

#### Exchange 4: CCO → CCC + CTO (Slack)

```
Amanda Torres: David, 7 months is too slow. NPS is a competitive issue now. We need to show momentum.

Jennifer Park: Amanda, I get the business pressure, but David's right about the infrastructure risk. A fast-deployed system that breaks is worse than a slower system that works reliably.

David Okonkwo: What if we compromise? We could deploy the agent on a dedicated, modern infrastructure (not integrated into the old system yet). It handles chat and email only—not phone, which requires the telephony integration. That's about 60% of our tickets, and it avoids the Avaya dependency.

We could pilot that in 8-10 weeks on the new infrastructure while the platform modernization runs in parallel. The modern infrastructure is good practice anyway.

Amanda Torres: I like it. Chat and email are 60% of volume, mostly the low-risk stuff. Refunds and cancellations come through those channels more than phone. We get NPS impact without waiting for full platform migration.

Jennifer Park: But who approves refunds and cancellations on the chat/email path? If we're doing human-in-the-loop, the SLA advantage goes away.

David Okonkwo: Not entirely. The agent can handle 100% of password resets and billing questions with no approval needed (those are read-only). For refunds, the agent escalates to a human, but with context pre-filled. Human approval takes 30 seconds instead of 5 minutes to read the whole ticket. That's still faster.

Jennifer Park: That's acceptable. And the human review protects us from compliance risk.

Amanda Torres: OK, let's scope this: Chat + email AI agent for password resets, billing questions, and escalation with pre-filled context for refunds/cancellations. Modern infrastructure. 8-10 week timeline. David owns the infrastructure, Jennifer owns the approval process design, I own the customer experience brief.

David Okonkwo: Agreed. But no surprises on timeline. If the infrastructure work is slow, we push the agent timeline, not the other way around.

Amanda Torres: Deal. Let's draft a memo to the exec team and move forward.
```

---

## Your Capstone Assignment

You have received these three scenarios. Pick ONE to work with (or your instructor will assign it).

**Your deliverable:** A **Stakeholder Alignment Memo** that:

1. **Names the conflict** — What are the executives actually disagreeing about?
2. **Restates each position** — Show each stakeholder you understand their real concern, not a strawman.
3. **Identifies the negotiables** — What can move? What can't?
4. **Proposes a path forward** — Describe a phased approach, compromise, or decision that addresses the underlying risks/needs.
5. **Gets buy-in** — Include sign-off lines for all stakeholders indicating they agree to move forward.

**Length:** ~1,000-1,200 words  
**Audience:** Executives and project leadership  
**Tone:** Professional, direct, respectful of constraints, forward-looking  

**Memo template:**

```
TO: [All Stakeholders]
FROM: [Your name], FDE
DATE: [Today]
RE: Stakeholder Alignment — [Project Name]

SITUATION SUMMARY:
[1 paragraph restating the business context and the core tension]

STAKEHOLDER POSITIONS:
[For each stakeholder, restate their position and underlying concern in 1-2 sentences]

THE CORE TENSION:
[What is actually in conflict? Is it timeline vs. risk? Cost vs. oversight? Technical feasibility vs. business need?]

PROPOSED RESOLUTION:
[Your recommendation. Include phased timeline, compromises, decision points, and accountability]

RISKS AND MITIGATIONS:
[What could go wrong with your proposal? How will you manage it?]

SUCCESS CRITERIA:
[How will we know this is working? What metrics or checkpoints?]

NEXT STEPS:
[Who does what, by when?]

---
AGREEMENT & SIGN-OFF:

I have reviewed this memo and agree to the proposed approach:

_____________________ Date: ______
[Stakeholder 1]

_____________________ Date: ______
[Stakeholder 2]

_____________________ Date: ______
[Stakeholder 3]

_____________________ Date: ______
[FDE]
```

**Evaluation criteria:**
- Do you understand each stakeholder's actual concern?
- Is your proposal realistic and achievable?
- Does it address the tensions or sidestep them?
- Would real executives sign this?
- Is it clear what happens next?

**Begin with your chosen scenario. You have 2 hours.**
