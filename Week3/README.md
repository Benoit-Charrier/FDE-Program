# Week 3 — End-to-End AI-Native Engagement

## Where you are

Weeks 1 and 2 practised the two halves of FDE work in isolation: write a buildable spec for an agentic solution (Week 1) and assess a business to design the right agent (Week 2). Week 3 puts them together into a full engagement arc — messy discovery, production-grade specification, build-loop correction, and stakeholder management, all on the same problem.

Week 3 is also the first time you'll be asked to diagnose an actual build output a (simulated) builder produced against a partial spec. You'll read the code, classify what went wrong, and write the corrective response in the right tone for each category.

## Your goal this week

Execute a complete FDE engagement from messy discovery through agentic solution design, production-grade specification, build-loop correction, and stakeholder management. The solution you design must be **AI-native** — not traditional software with AI features bolted on, but a system where agents are the primary mechanism for delivering value.

## By Friday, you must demonstrate that you can:

- **Navigate a realistic discovery process** with incomplete and contradictory information
- **Design an agentic solution that addresses the real business problem** — not just the stated request
- Produce specifications precise enough for an AI coding agent to build from
- **Diagnose build-loop failures** — is it a spec gap, a builder misread, an unjustified builder addition, or a test/environment issue?
- Handle **client pushback and scope pressure** professionally
- Write **Architecture Decision Records** with explicit trade-off analysis
- **Run the closed loop on your own spec under exam conditions** — diagnose what your spec produced honestly, even when the build is broken

## Week 3 calendar

Week 3 has more structure than Weeks 1–2 because the engagement simulation requires coordinated timing. The standing weekly rhythm applies — your coach team confirms the exact physical date for each virtual day in the **Teams General channel** at the start of the week, including any holiday-driven calendar shifts.

| Virtual day, Week 3 | Main event |
|---|---|
| **Monday, Week 3** | Coach-led week orientation (1h); self-directed preparation begins — read the build-loop diagnostic taxonomy end-to-end and audit your Week 2 specs for ambiguities |
| **Tuesday, Week 3** | Continue self-directed prep; production-spec-checklist audit of any draft spec you've started |
| **Wednesday, Week 3 (by 09:00 CET)** | Submit your one-line classification prediction to the critique pool *(see "Required preparation" below)* |
| **Wednesday, Week 3 (morning, 90 min)** | **Whole-cohort coach-led build-review walkthrough** — live diagnosis of a fresh worked build output (the **Coffee Subscription Credit Handler** fixture). You see the diagnostic move modelled on a complete fixture before you apply it solo. |
| **Wednesday, Week 3 (afternoon)** | Self-directed build-loop exercise on a *different* fixture — the **Cascade Public Libraries Hold Queue** fixture (`W3D3-BuildLoop-Exercise.md`), released at the end of the morning session. Submit to your squad lead by Wednesday EOD. |
| **Thursday, Week 3 (09:00 CET)** | **Gate 3 scenario released** — open `Gate3-Participant-Pack.md` (MedFlex healthcare staffing engagement). Read it end-to-end before the discovery call. |
| **Thursday, Week 3 (morning, 09:30–10:30 CET)** | **Live discovery session** — your squad conducts a 60-minute simulated client discovery call (a coach plays the stakeholder; all 10 squads run in parallel) |
| **Thursday, Week 3 (afternoon)** | Specification work based on what you learned in discovery |
| **Thursday, Week 3 (EOD, by 23:59 CET)** | **Submit your interim engagement design** to your squad lead — whatever you've drafted of Deliverables #1 (problem framing), #2 (intake & scope), #3 (architecture + ADRs). Rough is fine. **Not graded** — it's the input to your Friday-morning client feedback. |
| **Friday, Week 3 (09:00 CET)** | **Receive personalised client feedback** — a Marcus Reyes (CEO) email pushing back on your specific interim design (timeline pressure + scope/architecture pushback + a stakeholder or operational complication). The pushback is tailored to your work, not a generic memo. |
| **Friday, Week 3 (09:00–13:30)** | **Untimed preparation window.** Process Marcus's pushback. Plan how you'll incorporate the response into Deliverable #6. Refine your D#1–D#3 thinking. You are *not* yet writing the gate — this is preparation. |
| **Friday, Week 3 (13:30–17:00 CET)** | **Timed Gate 3 exercise (3.5 hours)** — produce all 9 deliverables under exam conditions. Final, polished, complete. **Submission closes at 17:00 sharp** (single markdown folder). |
| **Friday, Week 3 (17:50–19:00 CET)** | **10-minute verbal defense** with coach (5-min stagger). Coach probes one architectural decision + one acknowledged weakness from your submission. Specific slot confirmed by your coach. |
| **Following Monday (Week 4)** | Gate 3 results |

**How Friday actually flows.** This is where participants most often misread the schedule, so read it twice:

- **Friday morning (09:00–13:30) is preparation, not the gate.** You receive Marcus's personalised pushback memo at 09:00 and have ~4.5 hours to think through how to incorporate the response. You are *not* yet writing your Gate 3 deliverables. Use this window to read Marcus closely, decide which pushback points you'll concede with concrete alternatives vs hold scope on, and refine your D#1–D#3 thinking against the discovery + pushback evidence.
- **Friday afternoon (13:30–17:00) is the timed gate.** All 9 deliverables — including finalised D#1–D#3 (revised against Marcus), D#4 capability specs, D#5 build-loop response on the Cascade fixture, D#6 client-feedback response, D#7 validation plan, D#8 reflection, D#9 self-spec build-loop reflection — are produced under exam conditions. **Submission closes at 17:00 sharp.** Not EOD. Anything not in the package at 17:00 is not graded.
- **Friday 17:50–19:00 is the verbal defense.** 10 minutes per participant with your coach (5-min stagger). Coach picks one architectural decision and one weakness from your submission and probes both. Coaches run defenses sequentially across their 12–15 participants — your specific slot is confirmed by your coach.

**Note on the Friday rhythm:** Week 3 has no peer cross-review window. The engagement simulation runs Thursday–Friday back-to-back and there is no realistic slot for cross-squad review without breaking the simulation's timing. Assessment for Gate 3 is: self-assessment → coach review → live verbal defense.

## The Wednesday morning build-review walkthrough

The Wednesday morning session is the most important calibration moment of Week 3. Your coach projects a complete fixture — a spec plus the build output a (simulated) builder produced against it — and walks the cohort through diagnosis of each signal live:

- Is this a **spec gap** (you own the fix — spec revision)?
- Is this a **builder misread** (the builder owns the fix — direct correction)?
- Is this an **unjustified implementation choice** (collaborative removal request)?
- Is this a **test/environment issue** (diagnostic fix)?
- Or is this a **legitimate unknown the builder surfaced correctly** (acknowledge + revise + confirm)?

You'll see each category diagnosed live, with the canonical response pattern modelled, before applying the same move solo that afternoon on a different fixture. The Wednesday morning fixture (Coffee Subscription Credit Handler — coach-led) and the afternoon fixture (Cascade Public Libraries Hold Queue — solo) are deliberately different problems in different domains so the walkthrough never spoils the afternoon exercise. The afternoon fixture is released at the end of the morning session in `W3D3-BuildLoop-Exercise.md`.

### Required preparation before Wednesday 09:00 CET

The walkthrough does not teach the taxonomy. It demonstrates it. Three things are required before the session — participants who arrive without them will not be able to follow the session at the speed it runs.

1. **Read `../Reference/spec-ambiguity-vs-builder-mistakes.md` end-to-end**, including the FDE Response Protocol (tone, format, and category per response type). This is the vocabulary the coach uses throughout the session.
2. **Audit your own Week 2 or Week 3 draft spec for at least one requirement you suspect is ambiguous.** Bring a one-sentence private note: which requirement, why you suspect it, what a builder might misread. Not submitted — its purpose is to prime you to recognise ambiguity in your own work, not just in the walkthrough fixture.
3. **Submit a one-line classification prediction to the critique pool by 09:00 CET:** complete the sentence *"The hardest part of build-loop diagnosis for me will be ___."* This lets the coach weight the session toward the cohort's declared weak points. Non-submission is flagged but not blocking.

## The Thursday live discovery session

Thursday morning, all 10 squads run a 60-minute simulated client discovery session in parallel. A coach (or designated squad lead) plays a named stakeholder from the engagement scenario. You ask discovery questions; they answer some precisely, some vaguely, some contradictorily. Your job is to extract what you need to design the right solution — and to notice when you're being told something that doesn't add up.

This session is the one time in Week 3 when you directly practise the skill that Week 4's Monday discovery rehearsal and the Week 5 capstone defense both test further.

## Gate 3 — what you'll hand in

The full release packet — scenario, deliverables, timing, verbal defense format — is in `Gate3-Participant-Pack.md`, opened Thursday 09:00 CET. The summary below previews what's coming so you can plan ahead during Monday and Tuesday prep; **the pack itself is the canonical reference once it's released.**

The scenario is a healthcare staffing agency (**MedFlex**, 200 employees) that wants to "10x the business without 10x-ing the coordinators." The CEO is impatient and has seen two failed AI projects already (a chatbot and a recommendation engine that nobody used). He wants results in 8 weeks.

You have **3.5 hours** on Friday afternoon to produce **9 deliverables**:

1. **Problem framing & success metrics** — what is actually broken, and what does success look like for MedFlex, for the hospitals, and for the nurses? Measurable.
2. **Engagement intake & scope** — business context, stakeholder map, constraints, risks, MVP scope, what's **out** of scope and why
3. **Agentic solution architecture** — which parts of the workflow become agentic and at what delegation level? Include **at least 2 ADRs** with trade-off analysis
4. **Two production-grade capability specifications** — precise enough for Claude Code to build from; shared entities consistent across both
5. **Build-loop response memo** — references the Wednesday Cascade Public Libraries fixture you diagnosed earlier in the week (different domain from MedFlex; same diagnostic move). What did the build get wrong, what did your spec leave unclear, what must change?
6. **Client feedback response** — the CEO pushed back on scope and timeline during the week; how do you respond professionally?
7. **Validation plan** — how do you know the agentic system works? What do you test before production?
8. **Reflection document** — what would you do differently? What did you learn about your own process?
9. **Self-spec build-loop reflection (1 page)** — take one of your two capability specs from Deliverable #4, run it through Claude Code under exam conditions, and submit a 1-page reflection on what it built, what it asked, and what you'd change in the spec. **Graded on diagnosis honesty, not code correctness** — a spec that produced a broken build but was diagnosed honestly scores higher than a spec that produced working code by accident.

**When you work on what.**

- **Wednesday afternoon (solo build-loop fixture):** Cascade Public Libraries Hold Queue fixture diagnosed and submitted to your squad lead. This is *not* a Gate 3 deliverable, but the substance feeds **D#5** when you write it Friday.
- **Thursday morning (09:30–10:30, discovery role-play):** input gathering for **D#1**, **D#2**, **D#3**. No writing yet.
- **Thursday afternoon:** rough drafts of **D#1** (problem framing), **D#2** (intake & scope), **D#3** (architecture + ADRs), based on what you got from discovery + the scenario pack.
- **Thursday 23:59 — interim submission:** rough drafts of **D#1**, **D#2**, **D#3** submitted to your squad lead. Not graded. Input to the Marcus pushback generator overnight.
- **Friday 09:00–13:30 — untimed preparation:** read Marcus's personalised pushback. Refine your **D#1**/**D#3** thinking against it. Plan your **D#6** response strategy (which pushback points you'll concede with concrete alternatives, which you'll hold scope on, which need a re-frame). No deliverable is finalised in this window.
- **Friday 13:30–17:00 — timed gate (3.5h):** finalise everything. Revise **D#1–D#3** against Marcus and the day's clearer thinking. Produce **D#4** (two capability specs — the heaviest single deliverable; expect this to consume the largest share of the 3.5h). Write **D#5** (build-loop response memo against your Wednesday Cascade diagnosis). Write **D#6** (client feedback response, addressing each Marcus pushback point concretely). Produce **D#7** (validation plan), **D#8** (reflection), **D#9** (self-spec build-loop reflection — take ONE of your two D#4 specs, run it through Claude Code under exam conditions, write a 1-page reflection on what it built and what you'd change).
- **Friday 17:00 — submission cutoff:** single markdown folder containing all 9 deliverables.

After submission, you do a **10-minute verbal defense**. A coach picks one architectural decision and one weakness in your work and asks you to defend the decision with trade-off reasoning and acknowledge the weakness honestly. Coaches also probe: *"The CEO's two failed AI projects — how is yours different?"* and *"What kills this in production?"*

The detailed scoring rubric is held by your coach and not shared with participants from Week 3 onward — see the explanation in §7 of `Gate3-Participant-Pack.md`.

## What coaches are looking for

- Your solution is **genuinely AI-native** — agents are the mechanism, not a feature label on a traditional matching algorithm
- Your **build-loop diagnosis is correct** — you classify signals accurately and write the right corrective response in the right tone for each category
- Your **problem framing addresses the real problem**, not the stated request. *"10x without 10x-ing"* is not a technical requirement — figure out what it actually demands of the architecture.
- Your **Self-spec build-loop reflection is honest.** A spec that produced a broken build but was diagnosed precisely and honestly scores higher than a spec that produced working code by accident. Coaches read this deliverable for diagnosis quality, not build-output correctness.
- Your **client feedback response holds boundary without alienating.** The CEO will push on scope and timeline; caving and stonewalling are both failure modes.
- Your **specifications enable near-autonomous build.** An AI coding agent should not need to guess at intent. Where ambiguity is unavoidable, the spec names it as an assumption with a confidence level.

## Common Week 3 failure modes to avoid

- **AI-as-a-feature on a traditional matching algorithm.** Your architecture is a deterministic matcher with an LLM call sprinkled on top. Coaches will ask: *"Show me the agent decision in your design — the specific point where reasoning over context determines an outcome that a rule-based system couldn't reach."*
- **Build-loop diagnostic stops at first impression.** Most missed classifications come from naming the surface signal (e.g., "the test is wrong") without reading the spec alongside the code (e.g., the test reflects a real gap in the spec's expiry semantics). The walkthrough on Wednesday is built specifically to expose this second-order failure mode.
- **Client feedback is appeased, not addressed.** "Yes CEO, we'll deliver in 6 weeks" is not a response — it's a capitulation that breaks at week 4. Gate 3 rewards scope discipline and honest replanning, not optimism.
- **Self-spec reflection that defends the spec instead of diagnosing it.** A reflection that says "Claude Code mostly got it right, just needs minor polish" when Claude Code clearly missed the point is read as bluffing. Honest diagnosis ("Claude Code built X because my spec failed to distinguish Y from Z; I'd add a worked example for case A") scores higher than defensive reading.
- **No ADR trade-off analysis.** ADRs that read as justifications ("We chose X because it is the right choice") without naming alternatives considered, the consequences of each, and why the decision could later be revisited are read as decision theatre.

## Week 3 Suggested Resource Library

These are starting points, not assignments. Navigate them based on what you need to achieve the week's objective.

**Build-Loop & Spec Quality:**
- Production spec checklist — `../Reference/production-spec-checklist.md`
- Spec ambiguity vs builder mistakes — `../Reference/spec-ambiguity-vs-builder-mistakes.md` *(read end-to-end before Wednesday)*
- Kent Beck: Augmented Coding — https://tidyfirst.substack.com/p/augmented-coding-beyond-the-vibes

**Architecture Decisions:**
- ADR overview and templates — https://adr.github.io/
- ADR examples — https://github.com/joelparkerhenderson/architecture-decision-record
- AWS: ADR Best Practices — https://aws.amazon.com/blogs/architecture/master-architecture-decision-records-adrs-best-practices-for-effective-decision-making/

**AI Governance (as it affects FDE decisions):**
- NIST AI Risk Management Framework — https://www.nist.gov/itl/ai-risk-management-framework
- Microsoft: Responsible AI Principles — https://learn.microsoft.com/en-us/training/modules/embrace-responsible-ai-principles-practices/
- Google: Responsible AI Practices — https://ai.google/responsibility/responsible-ai-practices/

**Specification craft (in-folder):**
- Integration spec template — `../Reference/integration-spec-template.md`
- Discovery questioning patterns — `../Reference/discovery-questioning-patterns.md` *(carried forward from Week 2; revisit before Thursday's discovery session)*

**Carried forward from Week 2:**
- ATX framework references (`references/atx-*.md`) — your Cognitive Load Map and Delegation Matrix work in Gate 3 still uses ATX vocabulary even though Gate 3 is engagement-led, not ATX-led
