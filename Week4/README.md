# Week 4 — Economics, Governance & Platform Strategy

## Where you are

Weeks 1–3 were about individual engagements — one problem, one solution, one week at a time. Week 4 zooms out. You're now thinking *across* multiple engagements: building the economic case for why an agentic solution is worth the investment, governing the quality of work across a portfolio, and designing a platform strategy where each agent you build makes the next one cheaper.

Week 4 also introduces two structured exercises you haven't seen before: **"The Build Is Running"** (classifying 9 live build signals from an active engagement) and **"The Handoff"** (reviewing a partner team's spec and deciding whether to accept or block). Both are real FDE-in-the-field moves that you'll encounter in actual engagements.

## Your goal this week

Think across multiple engagements. Build the economic case that makes agentic transformation real. Design a platform strategy where each agent makes the next one cheaper. Govern quality across a portfolio of FDE work.

## By Friday, you must demonstrate that you can:

- Build a **credible token economics model** for an agentic use case
- Construct a business case a **CFO** would take seriously (baseline cost, agent cost, ROI, payback period, sensitivity analysis)
- Design a **compounding roadmap** where platform assets accumulate across waves
- Review and improve other FDEs' specifications with **specific, actionable** feedback
- **Distinguish spec issue from build issue from test issue** across multiple engagements
- Develop and defend a **capstone proposal** that is ambitious but achievable

## Week 4 calendar

Week 4 starts on  **Monday**. Your squad coach(es) confirms the exact physical date for each team+coach event in the **Teams General channel** or squad chat at the start of the week.

| Week 4 | Main event |
| --- | --- |
| **Monday, Week 4** | **Extended 90-minute coach orientation.** **Part 1 (60 min):** standard week orientation. **Part 2 (30 min):** live **discovery questioning rehearsal** — the coach plays a stakeholder from a practice scenario and you practise asking questions whose answers would actually change your design. This is rehearsal for the Gate 4 live round, not grading. |
| **Tuesday, Week 4** | Work on the peer review portfolio (reviewing 2 specs from Week 3); start the token economics model |
| **Wednesday, Week 4** | Compounding roadmap; "The Build Is Running" 9-signal classification exercise. **Afternoon:** per-squad coach checkpoint |
| **Thursday, Week 4** | "The Handoff" partner spec review + escalation email; finalise your capstone proposal |
| **Friday, Week 4 (afternoon)** | Gate 4 timed exercise (4 hours) + **14-minute capstone approval defense** (includes a 2-minute curveball rehearsal) |
| **Following Monday (Week 5)** | Gate 4 results |



**Note:** Week 4 has no Friday peer cross-review. Peer review *is* the graded deliverable this week (#3 below), so there's no recursion.

## The Monday discovery rehearsal

The 30-minute discovery rehearsal on Monday is the one time in Week 4 you practise the live clarification skill in a low-stakes setting. A coach plays a stakeholder from a practice scenario (**not** the Gate 4 scenario — the rehearsal doesn't leak the gate). The coach answers some questions precisely, some vaguely, and some contradictorily, and pushes back on framing you jump to too quickly.


Your job in the 15 minutes of role-play is not to "win" the conversation — it is to ask questions whose answers would actually change your design, notice when you're being told something that doesn't add up, and follow up on evasion without being accusatory. The coach debriefs for 10 minutes, naming specific discovery patterns from `../Reference/discovery-questioning-patterns.md` and commenting on what the cohort caught and what it missed.

## The "Build Is Running" exercise

You open the scenario file (`the-build-is-running-scenario.md`) and receive 9 live build signals from a simulated engagement. The file isn't available before Wednesday — there's no Tuesday pre-read. Each signal is a real build event — a failing test, an odd file the builder added, a runtime error, a stale test fixture — and each belongs to one of the four categories you learned in Week 3:

- Spec ambiguity (you own the fix — spec revision)
- Builder misread (the builder owns the fix — direct correction)
- Unjustified builder addition (collaborative removal request)
- Test/environment issue (diagnostic fix to the test, not the build)

Your job is to classify each signal and write the right governance response in the right tone. This is a 3.5-hour exercise, intentionally long. Don't rush it.

## The Thursday "Handoff" exercise

You inherit a specification from a partner team. You have to decide what to do: accept it, ask for specific changes, or escalate the whole thing. Then you draft the escalation email (or the accept response) in the tone you would actually send to a partner team lead you want to keep working with. The exercise tests your ability to triage — **the anti-pattern to avoid is "block everything" just as much as "approve everything."** Find the one thing that actually blocks production; let the things that are "different but fine" pass.

## Gate 4 — what you'll hand in

The full release packet — deliverables, timing, defense format, capstone-approval gate logic, and the suggested 4-hour cadence — is in `Gate4-Participant-Pack.md`, opened Friday 12:30 CET when the timed exercise begins. The summary below previews what's coming so you can plan ahead during Monday–Thursday prep; **the pack itself is the canonical reference once it's released.**

You have **4 hours** on Virtual Friday afternoon to produce **7 deliverables**:

1. **Token economics model** — for one of the Weeks 1–3 scenarios: baseline human cost, agent cost per case (tokens + tools + HITL), annual saving, build cost, payback period, sensitivity analysis
2. **Compounding roadmap** — 3-wave implementation plan showing how platform assets (integrations, governance, retrieval pipelines) built in Wave 1 reduce Wave 2–3 costs. Include an integration reuse matrix.
3. **Peer review portfolio** — your reviews of 2 specifications from Week 3. Real issues with concrete fixes, not vague feedback.
4. **Build governance response ("The Build Is Running")** — classify 9 signals and write the correct response to each
5. **Handoff review + escalation email** — review a partner team's spec, identify blocker/concern/acceptable difference, draft a professional escalation
6. **Capstone proposal** — full proposal including problem framing, success metrics, intended approach, why it's hard enough, what you expect to learn
7. **Build-loop reflection on a peer spec (1 page)** — take ONE of the two peer specs you reviewed in Deliverable #3, run it through Claude Code under exam conditions, and submit a 1-page honest comparison: what did the build reveal vs what did your peer review catch? What did your peer review miss? What were your **false positives**?

After submission, you do a **14-minute capstone approval defense**:

- **5-minute pitch** of your capstone proposal
- **7-minute coach challenge** on scope, difficulty, economic viability, and primary risks
- **2-minute curveball rehearsal (not graded)** — a coach introduces one new constraint that invalidates one specific assumption in your design (e.g. *"a regulator just banned automated decisions in this category"* or *"the client's volume just tripled"*) and you have 2 minutes to explain how your design adapts. This is explicit practice before Week 5, where curveballs are graded.

The detailed scoring rubric is held by your coach and not shared with participants from Week 3 onward — see the explanation in §7 of `../Week3/Gate3-Participant-Pack.md`. The deliverable expectations above and the verbal defense format are the canonical guidance for what good work looks like.

## What coaches are looking for

- Your **economics model is credible under stress.** Token costs are realistic; the sensitivity analysis shows the business case still holds under conservative assumptions.
- Your **peer reviews are specific and actionable.** "Looks good, minor issues" is not acceptable. Real issues named against specific sentences, with concrete fixes.
- You **classify build signals correctly and use the right response tone for each.** The most common failure mode is applying the same tone to every signal.
- Your **capstone proposal is ambitious but achievable.** Not bloated, not trivially simple, and bounded enough to design, build, and demo in 4 days with mock data next week.
- In the **build-loop reflection on a peer spec**, you are honest about what your peer review missed. Naming a missed issue scores higher than hiding it.

## Multi-model experimentation (Weeks 4–5)

Your economic case should reason about *when* to use which model, not just Claude Opus by default. Participants already have several tools that expose multiple models without changing the primary build workflow:

- **Dial** (`https://chat.lab.epam.com/`) — EPAM's multi-provider chat gateway.
- **Cursor** (optional) — multi-model chat and agent support (Claude, GPT-4o, Gemini, others) via its own subscription.
- **GitHub Copilot** (optional, via EPAM Leap) — multi-model selection in chat and agent modes.

Use any of these to pressure-test prompts across Claude Haiku / Sonnet / Opus and cross-provider alternatives. A 10× cost delta between Haiku and Opus on a step that works fine on Haiku is a real unit-economics finding — and the kind of analysis a client expects you to have done.

## Week 4 Suggested Resource Library

These are starting points, not assignments. Navigate them based on what you need to achieve the week's objective.

**Economics & Business Case:**
- ATX Economics Reference — `../Reference/atx/atx-economics.md` — token economics, cost modelling, ROI, self-financing roadmaps
- ATX Scoring Reference — `../Reference/atx/atx-scoring.md` — Volume × Value, TCO assessment, strategic sequencing
- Artificial Analysis — live model pricing and benchmark comparison across providers — https://artificialanalysis.ai/

**Platform & Architecture Thinking:**
- Anthropic: Building Effective AI Agents (revisit with a platform lens) — https://www.anthropic.com/research/building-effective-agents
- Donella Meadows: Leverage Points (revisit: which leverage points correspond to FDE activities?) — https://donellameadows.org/archives/leverage-points-places-to-intervene-in-a-system/
- Martin Fowler: Software Architecture Guide — https://martinfowler.com/architecture/

**Quality Governance:**
- "The Build Is Running" scenario — `the-build-is-running-scenario.md`
- "The Handoff" partner spec — `the-handoff-partner-spec.md`

**Carried forward from earlier weeks:**
- Discovery questioning patterns — `../Reference/discovery-questioning-patterns.md`
- Spec ambiguity vs builder mistakes — `../Reference/spec-ambiguity-vs-builder-mistakes.md`
- Production spec checklist — `../Reference/production-spec-checklist.md`
