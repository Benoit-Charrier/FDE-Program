

### Option A — Healthcare Claims Processing Transformation

A health insurance payer processes 2,000 claims/day with a team of 45 processors. Claims arrive from providers in multiple formats (EDI 837, PDFs, portal submissions). Each claim requires eligibility verification, coding validation, medical necessity review, and payment determination.

- **Current average processing time:** 35 minutes per claim
- **Auto-adjudication rate:** 22% (industry benchmark: 85%)
- **Denial appeal overturn rate:** 41% (indicating first-pass errors)

Design the agentic transformation: which parts of claims processing become agentic, at what delegation levels, with what economics?

## Stakeholder tensions

Each scenario includes **stakeholder tension** explored in `capstone-stakeholder-tensions.md` (also in this folder). Read the tensions for your chosen scenario when drafting your Gate 4 capstone proposal — they shape the **stakeholder alignment memo** (Deliverable #10).

---


### Build deliverable (Wed–Thu, submitted Virtual Thursday afternoon)

12. **Working prototype** — a runnable Claude Code project that implements your design. **Mock data is required** — the program has no client data; the prototype is a demonstration, not a production build. The prototype must include:
    - **One primary agentic flow** end-to-end
    - **One failure-mode escalation** that fires correctly
    - **At least one edge case** handled
    - **Tests covering all three paths**
    - **Demo script** showing how to run the three paths in sequence in under 5 minutes

**The prototype does not need to implement every flow in your design.** The skill being tested is *"your spec is buildable,"* not *"you can build everything in one week."* Cut scope honestly during the build if the happy path isn't working yet — a working happy path + working escalation + one edge case beats an ambitious half-built system.

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
