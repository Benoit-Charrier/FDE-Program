 ## Your goal this week

Given an ambiguous business problem, decompose it into a solution where the core mechanism is an AI agent. Produce a specification precise enough for an AI coding agent (Claude Code) to build from. Use AI iteratively to test, refine, and verify that spec.

You must demonstrate that you can:
- Frame a business problem from both user and business perspectives, with measurable success criteria
- Determine that the right solution is an AI agent — not traditional software, not RPA, not a human process change
- Produce a specification in a format an AI coding agent can execute against
- Use AI iteratively: prompt → assess output → refine → re-prompt until the spec converges on quality
- Identify what you don't know, what you're assuming, and what questions remain for the client

These are the deliverables to produce:

1. **A problem statement and success metrics** frame the problem from the claimant's perspective and business perspectives. Define measurable outcomes that justify the investment. Reference the scenario's specific numbers (not generic business-speak). File name "1 Problem statement and success metrics.md".
2. **A delegation analysis** for each part of FNOL processing, name which parts of the work become fully agentic, agent-led with human oversight, human-led with agent support, or human only — and **why**. Justify each boundary. The "why" is the skill being tested. File name "2 Delegation analysis.md".
3. **A first-draft capability specification** for the agentic part: purpose, scope, inputs/outputs, entities defined, decision logic with concrete thresholds, escalation triggers, integration contracts explicit (endpoint / auth / request / response / timeout / retry / fallback), state model (state machines named), error handling. Target 6–10 requirements minimum. Precise enough that an AI coding agent could start building from it. Output also should include a console application, a report in html format to summarize the analysis, a workflow diagram with input, output, agent tasks, human review.  File name "3 Capability specification.md"
4. **A first-draft validation design** with at least 3 scenarios spanning happy path, edge case, and failure mode — including at least one failure scenario that tests the delegation boundary itself. how do you know the agent is working? How do detect the agent is wrong — not just confirm it is right, What do you test? What does failure look like  — not just obvious failure, but quiet failure (the agent is wrong and no one notices)? File name "4 Validation Design.md" 
5. **An honest assumptions & unknowns section** — at least 5 genuine, scenerio-relevant unknowns, not filler. What are you assuming about the client's data, systems, organisation or the problem itself? What must be validated with the client before building? File name " 5 Assumptions & unknows.md"

Known gaps are better than hidden gaps. If you do not have time to fully specify a part of the contract (e.g., the exact SOAP request/response shape for the legacy policy system), name it explicitly as a scope-out with a concrete plan to resolve. A senior FDE ships specs with known-and-labelled gaps under time pressure — silent omissions on integration contracts do not earn the same read.
---

## What coaches are looking for

Three things more than anything else:

1. **Delegation boundaries are defensible, not arbitrary.** If you can't explain why a specific task is fully agentic versus human-overseen, you haven't done the thinking yet.
2. **The spec is precise enough that an AI coding agent wouldn't need to ask a clarifying question.** The critique session and your own closed build loop are both designed to teach you what this feels like. Use them.
3. **Assumptions and unknowns are honest.** "I don't know" beats a plausible-sounding guess. At least 5 genuine unknowns, not filler.

## The closed build loop (required)

1. Draft a spec for one feature or capability
2. Hand it to Claude Code — let it build
3. Review the output; identify at least one gap between what you asked for and what got built
4. Diagnose the gap: is it a **spec ambiguity** (you own the fix), a **builder misread** (the builder owns the fix), or an **unjustified builder addition** (ask for rollback)?
5. Apply the fix to the root cause
6. Re-run and verify the fix actually closed the gap

## Where to find more

- **Specification quality reference:** `production-spec-checklist.md`
- **Build-loop diagnostic taxonomy (used in your closed build loop and the Wednesday critique session):** `spec-ambiguity-vs-builder-mistakes.md`
- **CLAUDE.md examples:** `claude-md-examples-guide.md`
- **Thinking discipline** `Thinking-Discipline-Primer.md`
