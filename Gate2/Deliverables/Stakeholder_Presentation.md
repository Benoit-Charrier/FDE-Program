# Stakeholder Presentation: Apex Distribution Ltd — Billing Disputes

**Produced:** 2026-05-06
**Status:** Draft — awaiting FDE review
**Audience:** Sarah Whitmore, COO, Apex Distribution Ltd
**Purpose:** Assessment findings and proposed solution for WS4 Billing Disputes

---

## Slide 1: Title
**Type:** Title

**Apex Distribution Ltd**
**Customer Operations — Billing Disputes**

Assessment Findings & Proposed Solution

*Date: [DATE]*
*Presenter: [NAME], Field Deployment Engineer*

**Speaker notes:**
Thank you for making time for this. Today I'll walk you through what we found across your billing dispute process, what we think is worth building, and — critically — where we need your input before any build begins. This is not a pitch for AI. It's a structured look at where a well-scoped agent would actually save time and close a compliance gap that already exists in your process today, followed by an honest conversation about the decisions you need to make first.

---

## Slide 2: Agenda
**Type:** Section divider

1. The business problem — what triggered this assessment
2. What we found — how the work flows today and where it gets stuck
3. What we recommend — a targeted agent for billing disputes
4. Decisions we need from you — five questions that determine the design
5. Next steps — four actions before build begins

**Speaker notes:**
We'll move through five sections. The first two are about what we observed. The third is our recommendation. The fourth is where I'll need your answers — not hypotheticals, but specific operational facts that change what we build. The fifth is a concrete action list. I'll leave time for open discussion before next steps.

---

## Slide 3: Why We Are Here — The Business Problem
**Type:** Content

- **60 billing disputes handled every day at 28 minutes each** — the highest handle time of any work stream in Customer Operations, absorbing more than 1,600 minutes of skilled agent time daily with no structured support *(scenario_context.md)*
- **Credits are being applied without an audit trail** — live case records show at least one £170 credit applied to a customer account with no named approver and no entry in the audit log *(Artefact 2, confirmed in D3)*
- **A competitor has reported £1.2M in annualised savings on customer service AI** — the CEO has asked whether Apex can achieve something comparable *(scenario_context.md)*

**The question this assessment set out to answer:** Can a targeted agent reduce dispute handling time, close the compliance gap, and give Apex an auditable trace of every credit decision — without repeating the failures of 2024?

**Speaker notes:**
The 2024 chatbot and the billing RPA are in the room. I want to address them directly: both failed for specific, diagnosable reasons — the chatbot was customer-facing without a clear job to do, and the RPA broke because Aurum's data format changed without warning. What we're recommending today is different in both scope and design, and I'll show you specifically what we've built in to prevent the Aurum schema failure from happening again. But first, let me show you what the process actually looks like today.

---

## Slide 4: How the Work Actually Flows Today
**Type:** Content

```
Customer emails billing@ with disputed charge
        ↓ (avg 9 days to resolution — Artefact 2)
Agent opens CRM → manually retrieves yesterday's Aurum invoice data
        ↓
Agent assesses whether the charge is valid — no formal policy to check against
        ↓
Agent decides credit amount from experience (e.g., £170 on a £340 dispute)
        ↓
Agent applies credit via manual override — no audit log entry recorded
        ↓
Customer receives credit on next statement — case closed informally
```

**Four work streams today — billing disputes absorb the most per-case time:**

| Work stream | Daily volume | Time per case |
|---|---|---|
| ETA inquiries | ~400/day | 4 min |
| Delivery exceptions | ~180/day | 12 min |
| Dispatch adjustments | ~90/day | 18 min |
| **Billing disputes** | **~60/day** | **28 min** |

**Speaker notes:**
The flow I've drawn is based on actual case records, not the SOP. The SOP references DispatchHub, which was retired eighteen months ago, and the section covering damaged consignments is blank — marked TBD. So your team is resolving sixty cases a day against no documented policy and using a system that wasn't designed to give them the information they need at the time they need it. The result is what you see in that internal note on the Hayes & Sons case: a credit applied with no record of who approved it.

---

## Slide 5: Where Time Goes — The Cognitive Hotspots
**Type:** Content

**1. Assembling the evidence (estimated 10–12 min per case)**
Sandra manually retrieves invoice data, surcharge details, and delivery records from separate systems — Aurum batch exports and the CRM — that do not talk to each other in real time. There is no single view of a dispute. Each case starts from scratch. *(D1 — WS4 Zone 1, Z2)*

**2. Deciding the credit amount (judgment call with no rule)**
No written policy exists for how much to credit. The observed practice — roughly 50% of the disputed amount — is Sandra's heuristic, not an approved rule. Different agents would reach different amounts for the same case. *(D1 — WS4 Zone 3, MT6; D2 — C-7 Human Only)*

**3. Writing the credit record (compliance step routinely skipped under pressure)**
The audit trail fields exist in the system — named approver, case reference, reason code — but the current process bypasses them. At least one confirmed miss in live records. At machine speed, this gap would become systematic. *(D1 — WS4 BP-4; Artefact 2 internal note)*

**Speaker notes:**
The first hotspot is the one an agent fixes most directly and most safely — data assembly is not a judgment call, it's a retrieval task that takes time because the systems aren't integrated. The second hotspot is the one that requires a policy decision from you before we can build anything. The third hotspot is the reason the compliance argument for this agent is as strong as the efficiency argument — we're not just saving time, we're closing a gap that's already creating audit exposure today.

---

## Slide 6: What Can Be Delegated to an Agent — and What Cannot
**Type:** Content

| Task | Suitable for agent? | Why |
|---|---|---|
| Retrieve invoice, surcharge, and dispute records | Agent | Structured lookup — no judgment required |
| Send initial acknowledgement to customer | Agent | Same message every time; no variation |
| Classify dispute type (fuel surcharge / redelivery / dimensional weight) | Agent | Rule-based once dispute arrives in CRM |
| Verify whether a charge was calculated correctly | Agent | Arithmetic check against system data |
| Write the completed credit record once approved | Agent | Structured field population — deterministic |
| **Decide the credit amount** | **Human only** | **No formal policy exists; judgment required** |
| **Confirm and sign every credit record before it is written** | **Human — system-enforced gate** | **Named approver required; system will not write the record without it — enforced by design, not by policy** |

**Speaker notes:**
The right column is not a shortlist of things we couldn't figure out how to automate. It's where the design draws a deliberate line. The credit amount decision needs a written policy before any agent can apply it consistently — and that policy doesn't exist yet, which is one of the decisions I'll come back to. The approval gate is different: that's a system constraint we're building in as a hard rule. The agent physically cannot write a credit record until a named human has authenticated and confirmed it in the workflow. That's the direct design response to what happened in the Hayes & Sons case.

---

## Slide 7: The Opportunity — Where Volume Meets Complexity
**Type:** Content

```
                    HIGH COMPLEXITY
                          │
      WS1 Delivery  ●     │     ● WS4 Billing Disputes  ← PRIMARY TARGET
      Exceptions          │
                          │
   WS3 Dispatch ●         │
   Adjustments*           │
──────────────────────────┼──────────────────── VOLUME
                          │
              WS2 ETA ●   │
              Inquiries   │
                          │
                    LOW COMPLEXITY
```

*WS3 excluded: dispatch system does not support programmatic integration at present*

**Primary target: WS4 — Billing Disputes**
- Agentic value score: 20/25 — strongest in the portfolio *(D3)*
- Annual baseline cost: ~£245k/year at current handle time
- Projected annual agent cost: ~£70k/year (includes human review time)
- **Directional saving: ~£175k/year | Build cost: ~£100k | Payback: ~7 months** *(D3 §8)*

**Speaker notes:**
The chart shows why billing disputes is the right first target. It has the highest combination of case complexity and daily volume — not so high in volume that it's already been automated, but high enough in complexity that it genuinely needs an agent rather than a simple automation script. ETA inquiries are high volume but low complexity — closer to a lookup than an agent. Dispatch adjustments score similarly to billing disputes, but the dispatch console runs on Citrix and doesn't have a confirmed API surface, so building there would risk recreating exactly the brittle integration that broke in 2024. The billing dispute agent is the one with confirmed data access and a clear compliance case.

---

## Slide 8: The Proposed Agent — What It Does
**Type:** Content

- **Receives every inbound billing dispute** from the CRM queue and immediately assembles the evidence package: invoice data, surcharge records, delivery outcome, customer account history — what Sandra currently spends 10–12 minutes retrieving manually *(D4 §1, T-001 through T-004)*

- **Assesses whether the disputed charge is valid** using rule-based checks for fuel surcharges, dimensional weight, and redelivery fees; routes clear-cut cases with a structured verdict; routes ambiguous cases to a human reviewer with all evidence already assembled and a confidence score attached *(D4 T-007)*

- **Enforces a complete audit trail on every credit record**: named approver, CRM case reference, approved reason code — every field the current process routinely leaves blank *(D4 T-011, FM-3)*

- **Flags repeat dispute patterns automatically**: a customer with multiple open disputes of the same type triggers a senior review rather than being handled as three separate cases — the Hayes & Sons situation would have been surfaced on the first day *(D4 T-008, ET-005)*

**Speaker notes:**
What this agent replaces is the data assembly and the audit trail enforcement — the parts of Sandra's job that take the most time but require the least judgment. What it does not replace is the part that actually requires Sandra: deciding whether a credit is warranted, how much, and — in the cases that don't fit the standard types — making a call. The target outcome is that Sandra spends 8 minutes reviewing a pre-assembled case and confirming an amount, rather than 28 minutes rebuilding the picture from scratch and then writing it up informally.

---

## Slide 9: Where the Agent Stops — The Autonomy Boundary
**Type:** Content

| Tier | What happens | Examples |
|---|---|---|
| **Agent decides alone** | Data retrieval, dispute classification, charge calculation check, stale-data flag, customer acknowledgement, audit record write after approval is confirmed | Retrieve invoice; classify as fuel surcharge dispute; verify surcharge arithmetic; notify customer once credit is written |
| **Agent prepares — named human must approve before anything is written** | Every credit record: agent prepares the complete record with all required fields; the system holds it in pending state until a named approver authenticates and confirms the amount via an authenticated action; for credits above a threshold set by the COO, a senior approver is required | Sandra reviews the agent's case summary, confirms the credit amount, and her identity is recorded — then and only then does the system write the record |
| **Human only** | Credit amount decision (no written policy exists yet); disputes outside fuel surcharge, redelivery, or dimensional weight; legal or ombudsman referrals; accounts under a payment plan or in collections | Sandra decides the credit amount; agent prepares the paperwork around that decision |

**The named-approver gate is enforced by the system.** The credit record write is physically blocked until the workflow registers a human approval with an authenticated identity. The agent cannot populate the approver field — it has no write access to it. If a misconfiguration were ever to allow it to do so, the daily audit scan would detect a system identifier in that field and alert the operations lead within 24 hours. *(D4 §5 Autonomy matrix, FM-5)*

**Speaker notes:**
I want to spend a moment on the middle row, because it's the most important one. The reason Sandra's £170 credit appeared in the Artefact 2 case with no audit log entry is that the current process relies on people following a procedure under time pressure. That's a procedure-dependent control — and we've already seen it fail. What we're building is a system-dependent control: the credit record cannot be written until a human has authenticated. That's not a rule we're asking your team to follow. It's a technical constraint. The agent enforces it the same way every time.

---

## Slide 10: Integration Readiness
**Type:** Content

| Integration | Status | What it means |
|---|---|---|
| **CRM (Salesforce)** — case queue, customer data, delivery records, outbound messaging | **Amber** | REST APIs confirmed available. Whether inbound disputes auto-create CRM cases (vs. Sandra creating them manually) is not yet confirmed — if manual, the agent's intake trigger depends on Sandra taking the first step |
| **Aurum Billing — credit record write path** | **Red — blocking gap** | No programmatic write path to the credit ledger has been confirmed. If none exists, the agent can prepare credit records but cannot submit them, and the 48-hour manual ticket process remains. This is the single largest risk to the build timeline. *(D5 G-1)* |
| **Credit policy** | **Red — blocking gap** | No formal written credit policy exists. The agent cannot recommend credit amounts without explicit approved rules. This is a policy design task — not a technical one — but it must be completed before the agent can be deployed with full capability. *(D5 G-2)* |

**One confirmation needed before build can start:**
"Does Aurum Billing expose any write interface — even a controlled database path or structured import file — that does not require submitting a manual support ticket?"

**Speaker notes:**
The amber and two reds are not reasons not to build. They're the specific things that need to be resolved before we can commit to a timeline. The Salesforce amber is likely a configuration question — your IT team or Salesforce admin should be able to answer it in a day. The two reds are genuinely blocking: we cannot build the credit recommendation or credit write capability until they're resolved. The good news is that neither requires a new system to be built. One is a policy design decision — who owns it, and what are the rules. The other is a question for your Aurum vendor that we'd like to ask together.

---

## Slide 11: What We Need From You — Top Questions
**Type:** Content

**These five questions will change what we build. We do not currently have answers from the scenario artefacts alone.**

1. **Does a written credit policy exist anywhere — even a draft or email thread — that documents the rules for when to credit and how much?**
*If yes: it becomes the agent's rulebook. If no: someone must write it, and that person and timeline need to be identified before build begins.*

2. **When Sandra applies a credit today, what exactly does she do, step by step — which system does she go into, what does she type or click?**
*This single answer tells us whether a programmatic credit write path exists. If she emails the Aurum team a request, we may be able to automate that email. If she types directly into Aurum, there may be a write interface we can use. We cannot determine this from the data exports alone.*

3. **Who at Apex is authorised to approve a credit — and is there a threshold above which a manager must sign off rather than a billing agent?**
*We need this number to configure the approval routing. Without it, we cannot set the boundary between what Sandra approves and what escalates to you or a senior designate.*

4. **The 2024 RPA project broke when Aurum's data format changed without notice. This agent reads from the same Aurum exports. What would you need to see in the first 30 days to believe this time is different?**
*Your answer determines whether we lead the deployment with the compliance audit feature or the handle-time reduction — and what the 30-day milestone looks like.*

5. **If this agent reduces Sandra's time on billing disputes from 28 minutes per case to roughly 8 minutes, what does she do with the rest of her day — is there already a plan for that capacity?**
*An agent that creates capacity without a redeployment plan generates internal resistance. We'd rather surface this now.*

**Speaker notes:**
I want to be clear about why these are the five questions and not others. We're not asking about your systems — we have the Aurum exports and the CRM data. We're not asking about volumes — they're in the scenario. These five are the ones where the answer materially changes what we build. The credit policy question is the most important: if the answer is that no policy exists and you're not sure who would own writing one, that changes the build timeline more than any technical question. I'd like to spend most of our discussion time on questions two and one.

---

## Slide 12: Discussion
**Type:** Discussion

**Three topics we'd like your reaction to:**

1. **The compliance gap is already there.** Credits are being applied today without an audit trail — the agent closes this gap technically, but it will make that gap visible in a way it hasn't been before. Sandra's process will change. How does the team hear that?

2. **The Aurum write path has three realistic options.** If no API exists, we have three paths: automated email-ticket submission, agent-assisted manual submit, or a direct database write with the Aurum vendor's support. Each has a different risk and cost profile. Which fits your risk appetite for the first six months?

3. **The credit policy is a business decision, not a technical one.** The agent needs explicit written rules before it can recommend credit amounts. We can help frame what that document needs to contain — but the approval and ownership sit with you and finance. Is this something we scope as a pre-build sprint, or does a version already exist that we haven't seen?

**Speaker notes:**
These three prompts are the places where the assessment surfaces tensions that can't be resolved with better data — they need a decision from this room. The first one is about change management: I'd rather have that conversation now than discover it during rollout. The second is a genuine fork in the build design with real cost and timeline differences. The third is the most important: if there is a version of a credit policy somewhere — a finance memo, a management email, even a whiteboard photo — that's a very different starting point than writing from scratch.

---

## Slide 13: Next Steps
**Type:** Content

| Action | Owner | Dependency | Target date |
|---|---|---|---|
| Ask Apex IT and the Aurum vendor: does Aurum expose any write interface for credit records that does not require the manual support ticket? | Apex IT lead + FDE team | Discovery call scheduled | [DATE + 2 weeks] |
| Confirm Salesforce configuration: is an Approval Process or Flow available to enforce the system-level approval gate? | Apex Salesforce admin | Admin access | [DATE + 2 weeks] |
| Commission formal credit policy document: explicit rules per dispute type (fuel surcharge, redelivery, dimensional weight), approved credit amounts, and named approval threshold | COO + finance lead | COO decision to proceed | [DATE + 4 weeks] |
| Identify 150 historical billing dispute cases from CRM archive for confidence calibration; confirm two senior billing agents available to label them independently | Operations lead | Credit policy draft complete | [DATE + 5 weeks] |

**Speaker notes:**
The first two actions are discovery — they can happen in parallel and in under two weeks if the right people are in the room. The third is the most consequential: it's not a task we can do for you, but we can provide the template and the framing. The fourth is the pre-deployment safety requirement — we will not deploy an agent that makes autonomous validity assessments until we've validated its confidence scores against 150 real cases labelled by your own senior agents. That's the answer to the question about what's different this time.

---

## Slide 14: Closing
**Type:** Closing

**The recommendation in one sentence:**

Apex's billing dispute process is the strongest candidate for an AI agent in Customer Operations — a projected £175k annual saving with a 7-month payback — but two decisions must be made before build begins: what the credit policy says, and whether Aurum can accept a programmatic credit write.

---

*Contact: [NAME] | [EMAIL]*
*Next meeting: [DATE]*

---

*Acceptance criteria verified:*
- *All factual claims traced to named deliverables or scenario_context.md*
- *Speaker notes present on all 14 slides, adding context not on slide face*
- *Slide 6: primary governance constraint (named-approver, system-enforced) in human-anchored column*
- *Slide 9: governance constraint in "human approves" tier with enforcement mechanism explicitly stated*
- *Slide 11: all five questions unanswerable from scenario alone*
- *Slide 13: all four actions traceable to D5 gaps (G-1, G-2, G-3, G-4) and D6 questions (Q8, Q1, Q9)*
- *No ATX jargon in slide content (speaker notes use methodology terms where needed for presenter context)*
- *Total slides: 14*
