# Week 5 — Capstone + Final Exam

## Where you are

This is the last week of the program. You've practised specification (Week 1), assessment and agent design (Week 2), engagement execution (Week 3), and economics/governance (Week 4). Week 5 asks you to do all of it on one problem — and then to do it again under maximum pressure on a fresh problem on Virtual Friday.

Week 5 has two parts:

- **Part 1 — Capstone (Virtual Monday–Thursday):** design and build a working prototype for the capstone scenario you chose and got approved at Gate 4 (Friday Week 4). Defend the prototype with a live demo Virtual Thursday afternoon.
- **Part 2 — Final Exam (Virtual Friday):** a solo 8-hour hybrid exercise on a completely new scenario. You design, receive a curveball at the 4.5-hour mark, adapt your design, and then build a working prototype from your own revised spec.

**Both the Capstone and the Final Exam produce working code**, not just documents. This is the first week of the program where "it runs" matters at gate level. The automatic-fail list for both includes "prototype doesn't run."

## Your goal this week

Execute the full FDE arc — assess, design, spec, build, validate, defend — on a sealed business problem with a working prototype at the end. Then prove you can do it again under pressure, solo, on a fresh scenario in 8 hours.

## Week 5 calendar

Week 5 starts on a **physical Tuesday or Wednesday** depending on how the schedule has absorbed the Week 4 holiday adjustment. Your coach team confirms the exact physical date for each virtual day in the **Teams General channel** at the start of the week.

---

# Part 1 — Capstone (Virtual Monday–Thursday)

> **Your canonical Capstone gate instructions are in `Gate5a-Capstone-Participant-Pack.md`** (this folder), released Virtual Monday alongside your sealed scenario pack. It carries the day-by-day choreography, the 12 deliverables with filename suggestions, the working-prototype requirement, the 20-minute defense format, and the full rubric (the one gate where you see it up front). The summary below orients you; the pack is the operational reference.

## What you'll do

| Virtual day, Week 5 | Main event |
|---|---|
| **Monday, Week 5** | **Detailed sealed scenario pack released** for your already-chosen capstone option (chosen and approved at Gate 4 Friday Week 4). Begin design work — supplementary materials including stakeholder tensions and mock data context arrive at Monday's start of week. |
| **Tuesday, Week 5** | Finish the design package — capability specs, ADRs, economics, stakeholder memo, `CLAUDE.md`. Submit the full design package by end of day |
| **Wednesday, Week 5** | Start building the prototype with Claude Code + mock data. Happy path first. **Afternoon:** per-squad coach checkpoint on in-progress prototypes |
| **Thursday, Week 5 (morning)** | Finish the prototype (failure escalation + edge case working end-to-end); rehearse your demo |
| **Thursday, Week 5 (afternoon)** | **20-minute Capstone defense** — 5-min live demo + 10-min Q&A + 5-min curveball (coaches run defenses in parallel) |
| **Friday, Week 5** | **Final Exam** (see Part 2 below) |

**Design compresses to Virtual Mon–Tue. Build gets Virtual Wed–Thu.** By this point in the program you've designed under pressure twice (Weeks 2 and 4) — you should move faster through design than you did on your first ATX attempt. The build phase gets the most time because this is the first sustained exercise in the program of "build what you yourself designed from nothing."

## Your three capstone scenario options

You chose one of these three options at Gate 4 (Friday Week 4) and got coach approval to proceed. The detailed sealed scenario pack for your chosen option — including stakeholder tensions, mock data context, and operational specifics — is released at Virtual Monday's start of week. Below is a recap of all three options for reference:

1. **Healthcare Claims Processing Transformation** — a health insurance payer processes 2,000 claims/day with 45 processors; auto-adjudication rate is 22% (industry benchmark is 85%); denial appeal overturn rate is 41%. Design the agentic transformation: which parts of claims processing become agentic, at what delegation levels, with what economics?
2. **Enterprise Procurement Intelligence** — a manufacturer spends $800M annually across 3,200 suppliers; tribal knowledge lives in 3 senior buyers who are approaching retirement and scattered across email threads and personal spreadsheets. Design an agentic system that captures and operationalises that cognitive work before it walks out the door.
3. **Multi-Channel Customer Resolution** — CloudServe Inc., a SaaS company, handles ~10,000 support tickets/month across chat, email, and phone. Design agentic resolution that auto-handles routine read-only requests, routes entitlement changes (refunds, cancellations) through a human-approval gate with full audit trails, and escalates the complex — while respecting a legacy-telephony constraint that keeps the phone channel out of scope until platform modernization.

Each scenario includes **stakeholder tension** (provided in supplementary materials) and requires a **stakeholder alignment memo** with a defensible trade-off recommendation.

## Capstone deliverables

**Design deliverables (Virtual Mon–Tue, submitted end of Virtual Tuesday):**

1. Problem framing & success metrics (user, business, and operational perspectives)
2. Cognitive Load Map for the primary work stream
3. Delegation Suitability Matrix with archetype assignments
4. Agent Purpose Document(s) with autonomy matrix
5. Architecture Decision Records (3+ ADRs)
6. Two production-grade capability specifications
7. Integration specifications
8. Token economics model with sensitivity analysis
9. Validation plan
10. Stakeholder alignment memo
11. `CLAUDE.md` and project configuration

**Build deliverable (Virtual Wed–Thu, submitted Virtual Thursday afternoon):**

12. **Working prototype** — a runnable Claude Code project implementing your design. **Mock data is required** — the program has no client data. The prototype must include:
    - **One primary agentic flow** end-to-end
    - **One failure-mode escalation** that fires correctly
    - **At least one edge case** handled
    - Tests covering all three paths
    - A demo script showing how to run the three paths in sequence in under 5 minutes

**The prototype does not need to implement every flow in your design.** The skill being tested is "your spec is buildable," not "you can build everything in one week."

## Capstone defense (20 minutes, live demo-based)

1. **5-minute live demo** of the working prototype. Run the happy path, the failure-mode escalation, and the edge case in sequence, explaining what the agent is doing at each step. **This is a live demo, not a narrated slide deck.** Narrating slides instead of demoing running code is marked down on live demo quality regardless of whether the prototype works.
2. **10-minute coach questions** on problem framing, delegation design, economics, spec quality, stakeholder management, and "what would break this in production that the prototype doesn't show?"
3. **5-minute curveball** — a coach introduces a significant new constraint (regulatory ban, volume spike, deadline compression, PII flag, stakeholder reveal, system constraint) and you must respond in real time, both verbally and by naming what in the prototype and/or design would need to change. Graded on composure and specificity, not on solving the curveball perfectly in 5 minutes.

**The full Capstone rubric (criteria, weights, and pass threshold) is shared at the start of Virtual Monday** so you can use it to guide design and build decisions through the week. Unlike Gates 1–4 (which keep the rubric sealed until the gate begins), the Capstone rubric is visible because the 4-day format makes it valuable to have the criteria in front of you as you work.

**Automatic fail indicators (regardless of score):**
- Built a traditional rules engine instead of an agentic solution
- Failed to distinguish what should be agentic from what should stay human
- **Prototype does not run at all during the live demo**
- Narrated slides instead of demoing running code
- Validation is happy-path only with no failure-mode coverage

---

# Part 2 — Final Exam (Virtual Friday, 8 hours solo)

## What it looks like

A completely new scenario, sealed until Virtual Friday morning. 8 hours solo, Claude Code required, mock data required, no peer interaction, no coach questions, Internet permitted for reference only.

The exam is split into three phases: you design for 4.5 hours, receive a curveball at the 4.5-hour mark and adapt for 30 minutes, then build a working prototype from your own revised spec for 3 hours.

## Exam schedule (CET)

| Time | Phase | Duration |
|---|---|---|
| 08:45–09:00 | Pre-exam: packet release *(not counted in 8-hour exam clock)* | 15 min |
| **09:00–13:30** | **Design phase** | **4h 30min** |
| **13:30–14:00** | **Curveball + adapt** | **30 min** |
| **14:00–17:00** | **Build phase** — includes self-assessment + submission in the final 15–30 min | **3 hours** |

**Total exam clock: 8 hours** (09:00–17:00).

## Spec amendments during the build are allowed

If you discover a gap in your own spec during the build phase, you can submit a supplementary **spec amendment note** alongside the build. The design criterion is scored against the final honest version of your spec — original + curveball adaptation + any build-phase amendments. **Specs and builds co-evolve honestly.** Naming a gap you discovered beats hiding it.

## Final Exam deliverables

**Design phase (submitted by 13:30):**
1. Discovery notes with problem framing and success metrics
2. Cognitive work assessment with delegation analysis
3. Agent Purpose Document with autonomy matrix and escalation triggers
4. Architecture Decision Record (at least 1)
5. Production-grade capability specification (the spec your prototype will be built from)
6. Validation plan
7. Economics sketch (baseline vs agent cost, order-of-magnitude ROI)
8. `CLAUDE.md` for the agent project

**Curveball response (submitted by 14:00):**
9. Revised delegation design + spec amendments — a targeted adaptation, not a full redesign

**Build phase (submitted by 17:00):**
10. **Working prototype** — runnable Claude Code project: 1 primary agentic flow + 1 failure-mode escalation + at least 1 edge case, built from your revised spec. **Mock data required.** Tests covering all three paths. Demo script.
11. **(Optional)** Supplementary spec amendment note — if the build exposed a gap your design missed

**Final submission (by 17:00):**
12. Self-assessment output — run your full package through the Standardised Self-Assessment Prompt and submit the output alongside

## Final Exam rubric

**The full Final Exam rubric (criteria, weights, and pass threshold) is shared at 09:00 CET on Virtual Friday morning, alongside the scenario packet.** Until then, focus on the deliverables list above and the guidance below.

What you need to know in advance: your **design and your build are both graded, and both must pass**. A design that is elegant but whose build doesn't run **fails**. A build that runs but comes from a shallow spec **also fails**. Both signals must be present.

**Automatic fail indicators (regardless of score):**
- Designed a traditional software solution instead of an agentic one
- Failed to distinguish what should be agentic from what should remain human
- Accepted a clearly out-of-scope feature despite contrary evidence
- Missed a mandatory compliance or regulatory requirement from the curveball
- Validation scenarios are all happy-path with no edge or failure coverage
- Produced a curveball response that would damage the client relationship
- **Working prototype does not run at all** (regardless of design quality)
- **Build is unfaithful to your own spec** — prototype silently implements something the spec did not describe, or silently omits something the spec required, without an amendment note explaining the gap

---

## What coaches are looking for across both parts of Week 5

- **Your prototype demonstrates agentic behaviour** — the agent is making decisions, handling escalations, managing delegation boundaries. Not a glorified if-else tree.
- **Your build is faithful to your spec.** No silent scope creep, no silent scope reduction. If you discover a spec gap during the build, an amendment note is honoured, not penalised.
- **You handle the curveball with composure and specificity.** Name the assumption it invalidates, adjust the relevant part of the design, don't panic or bluff.
- **You think on your feet in the defense.** Coach questions are designed to find the gap between demo and production. Name the gap honestly.
- **You know when to cut scope.** If your Virtual Wednesday checkpoint shows the happy path isn't working yet, cut the second edge case and make the fundamentals solid. A working happy path + working escalation + one edge case beats an ambitious half-built system.

## Multi-model experimentation (carried forward from Week 4)

Your capstone economic case and Final Exam economics sketch should reason about model selection, not default to Claude Opus. The three tools already in your kit give you multi-model exposure without changing your primary Claude Code build workflow:

- **Dial** (`https://chat.lab.epam.com/`) — EPAM's multi-provider chat gateway.
- **Cursor** (optional) — multi-model chat and agent support (Claude, GPT-4o, Gemini, others).
- **GitHub Copilot** (optional, via EPAM Leap) — multi-model selection in chat and agent modes.

Use them to validate which step in your agent's flow actually needs Opus versus Sonnet versus Haiku (or a cross-provider alternative). Naming a defensible routing decision in your economic model is stronger than assuming one model for everything.

## Final thought

Week 5 is the hardest test in this program. It is also the week where the work you've been doing for four weeks actually pays off — if the skill is there, Week 5 reveals it. If it isn't, Week 5 reveals that too. Both outcomes are valid, and both leave you knowing something about yourself and your craft that you did not know five weeks ago.

Whatever the result: thank you for doing the program.

## Week 5 Suggested Resource Library

Week 5 is the full FDE arc under time pressure — there is no new methodology to learn this week. Your resource library is everything you have already been using across Weeks 1–4, consolidated here so you don't have to hunt for any of it during the capstone or the final exam.

**Capstone-specific materials:**
- **Gate 5a Capstone Participant Pack** (canonical gate instructions, deliverables, defense format, rubric) — `Gate5a-Capstone-Participant-Pack.md`
- Capstone scenario options recap — `../Reference/capstone-scenario-options.md`
- Capstone stakeholder tensions — `../Reference/capstone-stakeholder-tensions.md`

**Final Exam rules:**
- `../Reference/final-exam-rules.md`

**Specification craft (carried forward from Weeks 1–3):**
- Production spec checklist — `../Reference/production-spec-checklist.md`
- Integration spec template — `../Reference/integration-spec-template.md`
- Spec ambiguity vs builder mistakes (build-loop diagnostic taxonomy) — `../Reference/spec-ambiguity-vs-builder-mistakes.md`
- CLAUDE.md examples and failure modes — `../Reference/claude-md-examples-guide.md`

**ATX Framework (carried forward from Weeks 2 and 4):**
- ATX Concepts Reference — `../Reference/atx/atx-concepts.md`
- ATX Business Assessment Reference — `../Reference/atx/atx-assessment.md`
- ATX Agent Mapping Reference — `../Reference/atx/atx-agent-mapping.md`
- ATX Scoring Reference — `../Reference/atx/atx-scoring.md`
- ATX Economics Reference — `../Reference/atx/atx-economics.md`
- Artificial Analysis — live model pricing and benchmark comparison across providers — https://artificialanalysis.ai/

**Discovery & stakeholder handling (carried forward from Weeks 2, 3, and 4):**
- Discovery questioning patterns — `../Reference/discovery-questioning-patterns.md`

**AI-native development and agent design (carried forward from Week 1 and Week 2):**
- Anthropic: Building Effective AI Agents — https://www.anthropic.com/research/building-effective-agents
- Anthropic: Effective Context Engineering for AI Agents — https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
- Anthropic: Writing Tools for Agents — https://www.anthropic.com/engineering/writing-tools-for-agents
- Anthropic: Claude Code documentation — https://code.claude.com/docs
- Simon Willison: Agentic Engineering Patterns — https://simonwillison.net/guides/agentic-engineering-patterns/

**FDE role (pre-reading — revisit if helpful):**
- `../../Sources/the-fde.md`
