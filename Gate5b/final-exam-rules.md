# FDE Accelerated Development Program v4.2
## Final Practical Exam — Exam Day Rules & Schedule

**Date:** Friday of Week 5
**Time:** 09:00–17:00 (8-hour exam clock; 08:45 packet release is setup, not counted)
**Type:** Solo practical **design + build** deployment gate

---

## Exam Overview

This is a **previously unseen scenario** that you will design and build alone. This exam is not a test of your coding speed — it is a test of your ability to think *and* build like a Forward Deployed Engineer.

**The core expectation:** You will design an agentic solution and then build a working prototype of it. The right answer involves architecting how AI agents will do the work — not how you will write traditional software — and then proving the spec you wrote is actually buildable.

This is the only gate that tests design *and* build fluency simultaneously, on a fresh scenario, solo. **Both your design and your build are graded, and both must pass.** A design that is elegant but whose build doesn't run fails. A build that runs but came from a shallow spec also fails.

You are evaluated on your judgment about what to automate, how to delegate human and agentic work, how to specify systems that reduce ambiguity and enable autonomous execution, and whether the prototype you build is faithful to the spec you designed.

---

## Allowed Tools

**Claude Code (REQUIRED)**
- CodeMie CLI or personal license.
- Your primary design, reasoning, and build partner. This is how FDEs work.

**`CLAUDE.md` (Expected)**
- Part of your professional FDE workflow.
- You may reference general patterns, but all patterns must be freshly configured for this exam scenario — no boilerplate copy-paste.

**Internet Access**
- Permitted for **reference only**: documentation, API references, framework specifications, standards lookups.
- Not permitted for crowdsourcing solutions or consulting external contacts.

**Plain editors / IDEs**
- A plain text editor or IDE may be used for editing and running code.
- **Any AI / agent / autocomplete features must be disabled.** Claude Code is the only permitted AI tool (see Prohibited).

---

## Prohibited

**Communication**
- No contact with peers, Squad Leads, coaches, or any external person.
- No Slack, email, messaging, phone calls, or video calls during the exam.
- Violation = automatic fail.

**AI Tools**
- **Claude Code only.** No ChatGPT, Gemini, Copilot, Cursor AI features, or any other LLM interface or AI coding assistant.
- Violation = automatic fail.

**Collaborative Tools**
- No shared documents, spreadsheets, or collaborative platforms.
- No version control pushed to shared repositories during the exam. Work locally only.

**Pre-Prepared Materials**
- All deliverables must be created during the exam.
- `CLAUDE.md` may reference general patterns but must be instantiated for this specific scenario.
- Templates brought from outside = automatic fail.

---

## Exam Schedule

The exam is three phases: design, then a mid-exam curveball you adapt to, then build. You design from the scenario, receive new information at the 4.5-hour mark, adapt your design, then build a working prototype from your own revised spec.

| Time | Phase | Duration | Activity |
|------|-------|----------|----------|
| 08:45–09:00 | **Pre-exam setup** *(not counted in the 8-hour clock)* | 15 min | Receive exam packet; read the scenario. The clock begins at 09:00. |
| **09:00–13:30** | **Design phase** | **4h 30min** | Full FDE design arc: discovery notes, cognitive work assessment, Agent Purpose Document, production-grade capability specification, ADR, economics sketch, validation plan, assumptions, `CLAUDE.md`. **Submit the design package at 13:30.** |
| **13:30–14:00** | **Curveball + adapt** | **30 min** | New information arrives. Revise delegation boundaries, failure modes, or scope as the curveball demands — a targeted adaptation, not a full rewrite. **Submit revised design notes at 14:00.** |
| **14:00–17:00** | **Build phase** (includes self-assessment + submission in the final segment) | **3 hours** | Implement the agent with Claude Code + mock data: one primary agentic flow, one failure-mode escalation, at least one edge case. Build from your own revised design. Tests covering all three paths. Demo script. Spec amendments discovered during the build are permitted (see below). **In the final 15–30 minutes, run the full package through the Standardised Self-Assessment Prompt and submit by 17:00.** |

**Total exam clock: 8 hours (09:00–17:00).** Time budgeting is part of the test — participants who spend all three build hours coding and leave nothing for self-assessment and submission hand in an incomplete package.

### Specs and builds co-evolve

If you discover a gap in your own spec during the build phase, you may submit a supplementary **spec amendment note** alongside the build. The design is graded against its *final honest version* — original + curveball adaptation + any build-phase amendments. **Naming a gap you discovered beats hiding it.** A prototype that silently diverges from your spec with no amendment note is a faithfulness failure (see Automatic Fail Indicators).

---

## Submission Requirements

All deliverables are files in a single project folder. Submit the following (11 required + 1 optional = 12):

**Design phase (by 13:30):**
1. Discovery notes with problem framing and success metrics
2. Cognitive work assessment with delegation analysis
3. Agent Purpose Document with autonomy matrix and escalation triggers
4. Architecture Decision Record (at least 1)
5. Production-grade capability specification (the spec your prototype will be built from)
6. Validation plan
7. Economics sketch (baseline vs agent cost, order-of-magnitude ROI)
8. `CLAUDE.md` for the agent project

**Curveball response (by 14:00):**
9. Revised delegation design + spec amendments — a targeted adaptation with explicit reasoning, not a full redesign

**Build phase (by 17:00):**
10. **Working prototype** — a runnable Claude Code project implementing one primary agentic flow, one failure-mode escalation, and at least one edge case, built from Deliverable #5 (and any amendments). **Mock data required.** Tests covering all three paths. Demo script.
11. **(Optional)** Supplementary spec amendment note — any spec gaps discovered during the build, with the revised spec language.

**Final submission (by 17:00):**
12. Self-assessment output — your full package run through the Standardised Self-Assessment Prompt, submitted alongside.

---

## Standardised Self-Assessment Prompt

In the final 15–30 minutes of the build phase, assess your own package using this prompt in Claude Code, and submit the output as Deliverable #12:

```
Review this [specification / agent design / prototype] as a senior FDE would.
Evaluate against these criteria:

1. DELEGATION: Are the human/agent boundaries justified?
   Could someone else clearly understand who does what?

2. AMBIGUITY: Identify every statement that could be interpreted two ways.
   What would cause a builder to ask a clarifying question?

3. BUILDABILITY: Could an AI coding agent build this without asking
   clarifying questions? What's missing?

4. FAITHFULNESS: Does the prototype implement what the spec describes —
   no silent additions, no silent omissions? Where they differ, is there
   an amendment note?

5. ECONOMICS: Does the implicit cost model make sense?
   Are you automating the right things?

6. VALIDATION: Are the failure modes covered?
   How will you know if this worked?

7. SCORE: Rate this deliverable 1–100 with specific rationale.
   Be rigorous. A near-pass is a fail.
```

Use it rigorously — it trains your eye to spot the gaps examiners will find.

---

## Scoring & Pass Criteria

**The full rubric — criteria, weights, and pass threshold — is released at 09:00 CET on Virtual Friday morning, alongside the scenario packet.** Until then, work to the deliverables list above and the guidance here.

What you need to know in advance:

- **Your design and your build are both graded, and both must pass.** The rubric is split between design and build. An elegant design with a dead build fails; a working build from a shallow spec fails. Both signals must be present.
- The design is scored against the **final honest version** — original + curveball adaptation + build-phase amendments.

**Automatic fail indicators (any one fails the exam regardless of score):**

*Conduct:*
1. Communication with another person during the exam
2. Use of any prohibited AI tool (any LLM/AI assistant other than Claude Code) or collaborative platform
3. Pre-prepared deliverables submitted as exam work
4. Submission after 17:00 without a documented technical emergency
5. Failure to submit all required deliverables

*Quality (also disclosed in the Week 5 participant README):*
6. Designed a traditional software solution instead of an agentic one
7. Failed to distinguish what should be agentic from what should remain human
8. Accepted a clearly out-of-scope feature despite contrary evidence
9. Missed a mandatory compliance or regulatory requirement introduced by the curveball
10. Validation scenarios are all happy-path with no edge or failure coverage
11. A curveball response that would damage the client relationship
12. **Working prototype does not run at all** (regardless of design quality)
13. **Build is unfaithful to your own spec** — the prototype silently implements something the spec did not describe, or silently omits something it required, with no amendment note explaining the gap

---

## Misconduct Policy

These rules are non-negotiable:

- **Communication during the exam** = automatic fail. You are solo.
- **Use of prohibited tools** = automatic fail. Claude Code is sufficient.
- **Pre-prepared work** = automatic fail. Everything is created during exam hours.

If you have extenuating circumstances before the exam begins, notify the program coordinator. Once the exam starts, the rules apply uniformly.

---

## Practical Notes

**Breaks**
- Take breaks as needed. The 8-hour clock does not stop.
- Manage your energy. This is a marathon, not a sprint. Hydration and food permitted.

**Technical Difficulties**
- If Claude Code or your tools have issues, document the problem with timestamps and continue working.
- Technical difficulties are handled case-by-case after submission. Document what happened.

**Quality Over Completeness**
- A strong partial submission beats a weak complete one. A working happy path + working escalation + one edge case, built from a clear spec, beats an ambitious half-built system.
- Examiners reward clarity, rigor, justified design decisions, and a prototype faithful to the spec over checking every box.

**Time Management**
- The phase boundaries are firm submission points (13:30 design, 14:00 curveball response, 17:00 final). Within each phase, pace yourself.
- The build phase is only 3 hours — scope your prototype to what you can actually make run. Cut the second edge case before you cut the happy path.
- Reserve the final 15–30 minutes for self-assessment and submission. This is not optional; it is part of the graded package.

---

## You Are Ready

You have learned how to think *and* build like an FDE. This exam is an opportunity to demonstrate that under pressure. Trust your training, lean on Claude Code as your partner, write specifications that would make a senior engineer confident in autonomous execution — and then prove the spec was buildable by building it.

**Start at 09:00. Good luck.**
