## Your goal this week

Assess a business process as it is actually lived (not as it is documented), map its cognitive work using ATX, determine the delegation architecture, and produce an agent design precise enough to begin development.

## Scenario (read this first)
See `scenario.md`and 'enriched_scenario.md'. Do not invent numbers, systems, or constraints not present there. Every number you use must trace back to the scenario or be explicitly labelled an assumption.

## These are the deliverables to produce:

Be concise

A. **A problem statement and success metrics** frame the problem from the employee's perspective and business perspectives. Define measurable outcomes that justify the investment. Reference the scenario's specific numbers (not generic business-speak). Write in File "A Problem statement and success metrics.md".

B. **Discovery**
Assess a business process as it is actually lived, how work actually happens (not as it is documented)
- use \input\1-ATX-Assessment.md Phase 1 
- Read \references\discovery-questioning-patterns.md for more information

1. **Cognitive Load Map** 
    — decompose at least 2 of the 4 work streams into Jobs to be Done, micro-tasks, and cognitive dimensions. Map zones and breakpoints.
    - Use \input\1-ATX-Assessment.md Phase 2
    - Read \references\Atx-concepts.md for more information

2. **Delegation Suitability Matrix** 
    — score each major task cluster on delegation dimensions
    - assign delegation archetypes (fully agentic, agent-led with oversight, human-led with agent support, human-only) with rationale
    - determine the delegation architecture
    - Use \input\1-ATX-Assessment.md Phase 3

3. **Volume × Value Analysis** 
    — plot the 4 work streams
    - Identify where an agent creates value versus where it creates risk
    - identify the primary agentic target and justify why it wins
    - Use \input\1-ATX-Assessment.md Phase 4
    - Use \references\atx-scoring.md

4. **Agent Purpose Document** 
    — for the highest-value opportunity: 
        - produce an agent design, that fits real business reality, precise enough to begin development. 
        - Design agent with purpose, scope, KPIs, activity catalog, autonomy matrix, system/data requirements, escalation triggers, failure modes
    - Use \references\atx-agent-mapping.md
    
5. **System/Data Inventory** 
    — what the agent needs to access, what's available, what's missing, what's risky
    - Use \references\atx-agent-mapping.md

6. **Discovery questions for the Main Stakeholder** 
    — questions whose answers would *actually* change your design, not generic discovery questions
    - use references\discovery-questioning-patterns.md

7. **`CLAUDE.md` for the project** 
    - create a claude.md file, precise enough to begin development
    — demonstrates workflow discipline

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
