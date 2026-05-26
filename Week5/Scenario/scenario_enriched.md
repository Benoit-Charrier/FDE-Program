--

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
