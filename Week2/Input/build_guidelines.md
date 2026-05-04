# Build Instructions

When building using claude.md, create the build output in the `agent_build` folder.

## Workflow: Plan → Implement → Test

Every build session follows three phases in order. Do not skip ahead.

### 1. Plan

Before writing any code:

- Read `deliverables\CLAUDE.md` and the relevant deliverable (D4, D8) to understand the target behaviour
- Identify the specific capability or module being built this session — scope to one thing
- Write a short plan (3–10 bullet points) describing what you will build, what files you will create or modify, and what the acceptance test looks like
- Get explicit confirmation before proceeding to Implement

### 2. Implement

- Build output goes in `agent_build/`
- Source code in `agent_build/src/`
- Tests in `agent_build/tests/`
- Follow all constraints in `deliverables\CLAUDE.md` — delegation archetypes, hard stops, HITL triggers, and field names are not negotiable
- One logical change per commit — do not bundle unrelated changes
- Do not add error handling, fallbacks, or validation for scenarios that cannot happen
- Do not invent field names, thresholds, or system behaviours not in the spec; label anything not in the spec as an assumption

### 3. Test

- Run the full test suite after every change: `cd agent_build && pytest`
- All tests must pass before considering the session complete
- If a test fails, diagnose using the build-loop taxonomy from `references\spec-ambiguity-vs-builder-mistakes.md`:
  - **Spec ambiguity** — the spec is unclear; fix the spec first, then the code
  - **Builder misread** — the spec is clear but the code diverges; fix the code
  - **Design gap** — the spec is silent on a required behaviour; flag it, do not guess
  - **Acceptable variation** — the deviation is harmless; document and move on
- Do not mark a capability complete if any test is red or skipped

---

## Project Structure

```
agent_build/
├── src/          # Source code
├── tests/        # Test files
├── docs/         # Documentation
```

## Notes

- Every numeric threshold used in code must trace to `deliverables\CLAUDE.md`, a deliverable, or be labelled as an assumption in the code comment
- The closed build loop (draft → build → review → diagnose → fix → verify) is required for every non-trivial capability
