# Capstone Scenario Options & Format (Gate 5a)

> **What this file is.** The participant-facing reference for Week 5's Capstone (Gate 5a): the three scenario options you'll choose between in Week 4, the deliverable package you'll produce Mon–Thu of Week 5, and the 20-minute defense format Thursday afternoon.
>
> **What this file is NOT.** Not the Capstone rubric. The Capstone rubric (criteria, weights, scoring anchors, pass thresholds) is **released at the start of Virtual Monday Week 5**, alongside your chosen scenario's sealed pack. Until then, the deliverable expectations below are your canonical guidance. The Capstone rubric is the one program rubric participants DO see during the gate (sealed for all other gates) — see `../README.md` § *Rubrics — sealed until the gate begins* for the policy.
>
> **Why this file exists.** The v4.2 program doc (`FDE-Accelerated-Development-Program-v4.2.md`) is a coach-facing reference that contains rubrics for Gates 1–4 and the Final Exam which are sealed until each gate begins. Participants drafting the Gate 4 capstone proposal on Virtual Thursday of Week 4 need the scenario options without the rubric-leak path that reading the program doc would create. This file is the extracted participant-safe view.

---

## The three capstone scenario options (choose one)

You pick one of these three at Gate 4 (Friday Week 4) and get coach approval to proceed. The detailed **sealed scenario pack** for your chosen option — including stakeholder tensions, mock data context, operational specifics, and the rubric — is released at Virtual Monday Week 5.

### Option A — Healthcare Claims Processing Transformation

A health insurance payer processes 2,000 claims/day with a team of 45 processors. Claims arrive from providers in multiple formats (EDI 837, PDFs, portal submissions). Each claim requires eligibility verification, coding validation, medical necessity review, and payment determination.

- **Current average processing time:** 35 minutes per claim
- **Auto-adjudication rate:** 22% (industry benchmark: 85%)
- **Denial appeal overturn rate:** 41% (indicating first-pass errors)

Design the agentic transformation: which parts of claims processing become agentic, at what delegation levels, with what economics?

### Option B — Enterprise Procurement Intelligence

A manufacturing company (5,000 employees) spends $800M annually across 3,200 suppliers. Their procurement team (25 people) manually reviews contracts, tracks compliance, monitors supplier performance, and manages sourcing events.

- **Tribal-knowledge concentration:** 3 senior buyers approaching retirement
- **Knowledge location:** email threads + personal spreadsheets, not systems of record
- **Supplier coverage:** 3,200 suppliers across multiple categories

Design an agentic system that captures and operationalises this cognitive work before it walks out the door.

### Option C — Multi-Channel Customer Resolution

A financial services company handles 4,500 customer interactions daily across phone, email, chat, social media, and branch referrals. Issues range from simple balance inquiries to complex dispute resolution requiring regulatory compliance (CFPB, state banking regulations).

- **Current systems:** 6 different systems coordinated per interaction
- **Average handle time:** 18 minutes
- **First-contact resolution:** 34%

The Chief Customer Officer wants agentic resolution that handles the routine while routing the complex to specialists — with full audit trails for regulatory examination.

---

## Stakeholder tensions

Each scenario includes **stakeholder tension** explored in `capstone-stakeholder-tensions.md` (also in this folder). Read the tensions for your chosen scenario when drafting your Gate 4 capstone proposal — they shape the **stakeholder alignment memo** (Deliverable #10).

---

## Capstone schedule (Virtual Monday – Thursday Week 5)

| Day | Phase | Activity |
|---|---|---|
| **Monday** | Scenario release + design | Receive sealed scenario pack (incl. rubric). Begin design: problem framing, cognitive load map, delegation matrix, Agent Purpose Document, stakeholder alignment thinking. |
| **Tuesday** | Design completion | Finish the design package: capability specs, ADRs, economics, integration specs, validation plan, `CLAUDE.md`. Submit the design package by end of Tuesday. |
| **Wednesday** | Build phase starts | Begin building the prototype with Claude Code against the design. **Happy path first.** Wednesday afternoon mid-week checkpoint: coach reviews in-progress prototypes — *"is the agent actually doing something useful, or is it an if-else tree wearing a hat?"* |
| **Thursday morning** | Build completion + demo prep | Finish the prototype: failure-mode escalation working, at least one edge case handled, demo rehearsed end-to-end. |
| **Thursday afternoon** | **Capstone defense (20 min)** | 5-min live demo + 10-min coach Q&A + 5-min curveball. See defense format below. |
| **Friday** | *(Final Exam — separate gate, see `final-exam-rules.md`)* | — |

**Time budget note:** Design compresses to Mon–Tue because by this point in the program you've designed under pressure twice (Weeks 2 and 4) — you should move faster through design than your first ATX attempt. The build phase gets the most time because this is the first sustained exercise of "build what you yourself designed from nothing."

---

## Capstone deliverable package

### Design deliverables (Mon–Tue, submitted end of Virtual Tuesday)

1. **Problem framing & success metrics** — user, business, and operational perspectives
2. **Cognitive Load Map** for the primary work stream
3. **Delegation Suitability Matrix** with archetype assignments
4. **Agent Purpose Document(s)** with autonomy matrix
5. **Architecture Decision Records** (3+ ADRs, each with trade-off analysis)
6. **Two production-grade capability specifications**
7. **Integration specifications**
8. **Token economics model** with sensitivity analysis
9. **Validation plan**
10. **Stakeholder alignment memo** (defensible trade-off recommendation addressing the scenario's stakeholder tensions)
11. **`CLAUDE.md`** and project configuration

### Build deliverable (Wed–Thu, submitted Virtual Thursday afternoon)

12. **Working prototype** — a runnable Claude Code project that implements your design. **Mock data is required** — the program has no client data; the prototype is a demonstration, not a production build. The prototype must include:
    - **One primary agentic flow** end-to-end
    - **One failure-mode escalation** that fires correctly
    - **At least one edge case** handled
    - **Tests covering all three paths**
    - **Demo script** showing how to run the three paths in sequence in under 5 minutes

**The prototype does not need to implement every flow in your design.** The skill being tested is *"your spec is buildable,"* not *"you can build everything in one week."* Cut scope honestly during the build if the happy path isn't working yet — a working happy path + working escalation + one edge case beats an ambitious half-built system.

---

## Capstone defense (20 minutes, live demo-based)

| Time | Activity |
|---|---|
| **0:00–5:00** | **5-minute live demo** of the working prototype. Run the happy path, the failure-mode escalation, and the edge case in sequence, explaining what the agent is doing and why at each step. **This is a live demo, not a narrated slide deck.** |
| **5:00–15:00** | **10-minute coach Q&A** covering problem framing, delegation design, economics, spec quality, stakeholder management, and *"what would break this in production that the prototype doesn't show?"* |
| **15:00–20:00** | **5-minute curveball** — coach introduces a significant new constraint (regulatory ban, volume spike, deadline compression, PII flag, competitor parity, stakeholder reveal). Respond in real time, both verbally and by naming what in the prototype and/or design would need to change. Graded on composure and specificity, not on solving the curveball perfectly in 5 minutes. |

---

## Automatic-fail indicators (regardless of score)

The detailed rubric (criteria, weights, pass thresholds) is released Virtual Monday Week 5 alongside the sealed scenario pack. Independent of the numeric score, any of the following triggers an automatic fail:

- **Built a traditional rules engine instead of an agentic solution** — the core FDE test
- **Failed to distinguish what should be agentic from what should stay human** — delegation boundaries undefined or arbitrary
- **Prototype does not run at all during the live demo** (regardless of design quality)
- **Narrated slides instead of demoing running code** — the demo is a live demo by definition
- **Validation is happy-path only with no failure-mode coverage** — no honest validation
- **Build is unfaithful to your own design** — the prototype implements something the design did not describe, or silently omits something the design required, without an explicit amendment note

---

## Where the rubric is

The Capstone rubric is **released at the start of Virtual Monday Week 5** alongside your sealed scenario pack. The Capstone is the one program gate where the rubric is visible during the gate (sealed for all other gates) — the 4-day design+build format makes it operationally valuable to have the criteria in front of you as you work. See `../README.md` § *Rubrics — sealed until the gate begins* for the canonical rubric-visibility policy.
