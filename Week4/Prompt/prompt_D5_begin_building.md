# Prompt: D5B — Begin Building (Closed Build Loop)

This prompt is run **twice** — once per agent, in sequence. Do not run both agents in the same session. Fix the spec between runs.

---

## Pass 1 — Agent A

Build the **first agent** described in `Deliverables/D4_capability_specs.md`.

1. Tell me what you can build confidently without asking any questions.
2. Tell me what you need to clarify before building the rest — list each question precisely, naming the spec section it relates to.
3. Build the one part you are confident about. Just enough so we can run the build_loop-response on some code snipet. Use the guidelines in `input/build_guidelines.md`.

Write all output (what was built, questions raised, what could not be built) to `Deliverables/D5B_build_loop_analysis.md` under a section headed **Agent A**.

**Stop here.** Before running Pass 2:
- Run `prompt_D5_build_loop_response.md` on the Agent A output to classify every signal
- Revise `Deliverables/D4_capability_specs.md` to address all spec gaps and legitimate unknowns surfaced in Agent A's build loop

---

## Pass 2 — Agent B

After the D5 build-loop response for Agent A is complete and D4 has been revised, build the **second agent** described in the updated `Deliverables/D4_capability_specs.md`.

1. Tell me what you can build confidently without asking any questions.
2. Tell me what you need to clarify before building the rest — list each question precisely, naming the spec section it relates to.
3. Build the parts you are confident about. Use the guidelines in `input/build_guidelines.md`.

Append all output to `Deliverables/D5B_build_loop_analysis.md` under a section headed **Agent B**.

Then run `prompt_D5_build_loop_response.md` again on the Agent B output to produce the final D5 diagnostic memo covering both agents.
