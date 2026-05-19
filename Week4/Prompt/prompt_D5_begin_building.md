# Prompt: Gate 4 D7 — Begin Building (Dmytro's Intake Spec)

This prompt is run **once**. The spec under build is Dmytro's intake agent spec. The output feeds directly into `prompt_D5_build_loop_response.md`, which produces the final D7 deliverable.

---

## The build task

Build the agent described in `Spec_review_input1/04a-capability-spec-intake-Dmytro.md`.

Read the spec in full before writing a single line of code. Use the guidelines in `Input/build_guidelines.md`.

Then produce three outputs in sequence:

**1. What I can build confidently without asking any questions**

List the parts of the spec that are complete enough to implement immediately — specific sections, flows, or integration contracts where every decision is made and every edge case is covered. Be precise: name the sections, not just "most of the spec."

**2. What I need to clarify before building the rest**

List each open question precisely. For each:
- Name the spec section it relates to
- State exactly what is ambiguous or missing
- State what assumption you would make if forced to proceed, and whether that assumption is safe or risky

Format:
> *[Section name]*: [Exact question]. If unanswered, I would assume [X] — this is [safe / risky] because [reason].

**3. Build the part you are most confident about**

Build the single component or integration contract you rated most complete. Enough code to demonstrate a real implementation choice — not scaffolding. Name what you chose to build and why (most complete, fewest open questions).

---

## Output

Write everything — what was built, questions raised, what could not be built and why — to `Deliverables/Gate4_D7_build_loop_reflection.md` under a section headed **Build Loop Output**.

Then run `prompt_D5_build_loop_response.md` on this output.
