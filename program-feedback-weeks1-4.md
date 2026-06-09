# Overall Feedback — FDE Program, Weeks 1–5

## Summary

The FDE program is substantive, well-conceived, and covers genuine professional territory. The frameworks, the E2E arc, and the live sessions (discovery, build review, spec review, capstone proposal review) are the strongest elements. Over five weeks, a good amount of new knowledge was acquired and the investment was worthwhile. However, given the 100% time commitment, significantly more could have been learned. The recurring friction across all five weeks traces back to a small number of fixable root causes: **a learning design that does not match the difficulty of the material, an absence of structured feedback on deliverables, and a persistent pattern of unclear communication.** With targeted improvements in these three areas, this program has the potential to be genuinely exceptional.

---

## What Worked — Consistent Across Weeks

- **Live interactive sessions** (discovery practice, build reviews, spec reviews, capstone proposal review, mid-week coach sessions) were consistently the highest-value moments. Participants could test semi-formed understanding against a coach and get calibrated quickly.
- **The ATX framework and token economics model** are genuinely powerful tools. Once participants find their footing, the output becomes more deterministic and the justifications clearer — as visible in the Week 3 cohort convergence on categorizations.
- **The timed gate format** creates productive pressure and simulates real deployment conditions. The capstone proposal review felt closest to actual client work.
- **The E2E arc across the five weeks** pays off in Week 5 when design, build, and validation come together. Participants who prepared through the capability specification by end of Week 4 saw real continuity.
- **The program team's dedication** — running this alongside regular responsibilities — was noted and appreciated throughout.

---

## Recurring Issues — Five-Week Pattern

**1. Learning design gap: the content requires instruction, not just documentation**

Every week surfaced the same theme: participants read, re-read, and applied the material, but still lacked confidence that their outputs were correct. This is a signal that the material exceeds the threshold where self-directed reading alone is sufficient. The ATX assessment, the spec structure, the build/validation loop, and the tooling setup all need at least one live session each — not to replace reading, but to handle the questions that reading cannot answer. Effective learning environments combine clear goals, moderate challenge, immediate feedback, and deliberate repetition. The program currently has challenge but is light on the other three.

**2. Absence of concrete submission feedback**

Across all five weeks, participants received no structured feedback on what was good and what should be improved in their individual submissions. This is the single largest gap in making learning stick. Anonymized examples of strong and weak deliverables, and returning peer/spec reviews to their authors with discussion time, would close most of this gap at low cost.

**3. Instruction clarity and timing**

Instructions were described as confusing in every week. Friday packages surfaced requirements that were not in Monday packages. Scenario releases came too close to live sessions to allow proper preparation. In Week 5, the exam packet arrived 1 hour and 15 minutes late with no explanation, apology, or timeline adjustment communicated — and the curveball package was dropped into a folder at 13:30 with no Teams message. At the end of the final day, there was no communication about the end of the program, no indication of when results would be shared, and no update on the two follow-up events planned for the following days. Taken together across five weeks, this forms a clear pattern rather than isolated incidents.

If VUCA is an intentional design choice, it should be applied only where it serves a learning objective — on the AI/agentic material itself, which is already genuinely ambiguous. Adding VUCA to the logistics of the program is unnecessary friction that costs learning time, erodes trust, and at its most acute (a 75-minute silent delay on exam day) comes across as disrespectful to participants' time.

**4. ATX framework: inconsistent terminology, unclear scoring**

Terms (workstream, JtD, task, zone, use case, candidate, process) are used interchangeably across documents. Scoring rubrics have edge cases that produce non-deterministic results. Volume's definition (frequency vs. time) is ambiguous. Phase 2 applies to 2 workstreams while Phase 4 ranks all 4. These are not quibbles — they produce divergent outputs from equally careful participants and undermine trust in the framework. A single live Q&A session dedicated to ATX, with worked examples, would address most of this.

**5. Build-to-spec pipeline: unclear entry and exit criteria**

What belongs in a spec, what can be validated before building vs. after, when to use the ambiguity guide vs. the validation design, and how to catch builder mistakes without being a developer — these questions were open at Week 2 and were still present in Week 5. The build loop needs its own session with a concrete worked example from brief to spec to build to test.

**6. Scope alignment: deliverable expectations not shared in advance**

During the Week 5 mid-week review, participants and the coach had materially different expectations for the prototype scope — an agentic solution demonstrating AI capability versus an end-to-end solution including a customer-facing UX. Both are valid deliverables; the issue is that the expectation was not established in writing before the work began. In client-facing work, a misalignment of this kind at review time is costly. The program should model the practice it teaches: define the acceptance criteria before the build, not at the review.

**7. Final exam purpose: assessment vs. new learning**

The Week 5 final exam felt redundant to participants who had completed significant design work during the week. It was unclear whether the intent was to teach something new or to assess skills under tighter time constraints. The exam did demonstrate something valuable — that Claude can generate a full design through to a capability specification in a single pass in under 10 minutes — but that finding was incidental rather than deliberate. Clarifying the exam's pedagogical purpose in advance would help participants engage with it more productively.

**8. Tooling and infrastructure**

Budget depletion, profile confusion (Codemie/EPAM/personal), API key setup, VS Code + GitHub + Claude Code onboarding — these are Week 1 problems that consumed time in later weeks. Pre-requisite technical setup guidance before the program starts, and a dedicated session in Week 1, would eliminate this class of friction entirely.

---

## Strategic Question

The program asks a single participant to cover requirements elicitation, agentic architecture, capability specification, build, and validation — skills that in practice are distributed across BA, architect, developer, and QA roles. The relevant question is not whether this is theoretically possible with AI assistance, but whether it produces trustworthy production-grade output for a paying client. A team-based model — with the FDE role as architect/orchestrator rather than solo practitioner — may be more realistic for actual deployment. This could be worth an explicit discussion in the program, and the exam format could evolve to reflect it.

---

## Highest-Leverage Changes

1. **Add four live sessions**: ATX framework, spec structure and build loop, validation design, tooling setup. Require pre-reading; use session time for questions and worked examples.
2. **Return submission feedback**: Concrete, structured, individual feedback each week — or at minimum anonymized cohort examples of strong and weak submissions.
3. **Establish communication standards**: Acknowledge delays, communicate timeline changes, close the program formally. Model the professionalism the program teaches.
4. **Define deliverable scope in writing before each build phase**: Coach and participant expectations aligned on paper before the work starts, not discovered at the review.
5. **Clarify the exam's purpose**: Is it a learning experience or an assessment? Both are legitimate — but participants deserve to know which one they are in.
