# Prompt: P8 — CLAUDE.md (Build-Phase Configuration)

## Methodology references

- `References/claude-md-examples-guide.md` — quality tiers for CLAUDE.md; Tier 3 build config requirements

## Inputs

- `Deliverables/05-capability-spec.md` — all sections (this is the spec the build runs against)
- `Deliverables/03-agent-purpose.md` — §3 (autonomy matrix), §4 (escalation triggers)

## Your task

Produce the `CLAUDE.md` for the prototype build. This is a Tier 3 build config — it must be precise enough for Claude Code to build the prototype with few or no clarifying questions.

Output file: `CLAUDE.md` (project root)

---

## Required structure

### 1. What this prototype does
Two sentences: what it processes, what it decides, what it outputs.

### 2. Entry point
`process_[entity](input: dict) -> dict` — name the function and its signature.

### 3. Input schema
Every field the entry function expects. Table format:

| Field | Type | Required | Notes |
|-------|------|----------|-------|

### 4. State machine
All valid states and transitions. Use → notation. Include the governance hard stop transition.

### 5. Key invariants — never break without explicit instruction

List each in this format:
> **[Invariant name]:** [what must always be true — precise enough to check in code]

Required invariants:
- Audit-first ordering (output value written only after audit entry is COMMITTED)
- Governance hard stop (first check in the output step)
- From-state guard on every state transition
- Startup validation (agent refuses to process if calibration/config check fails at startup)

### 6. Escalation triggers
For each ET, one line:
> **ET-[N]:** [condition] → queue: [queue name], trigger_type: [type]

### 7. Tools — real vs stub

| Tool | Status | Notes |
|------|--------|-------|
| [LLM classifier / main AI call] | Real — live API call | Reads `ANTHROPIC_API_KEY` |
| [other tools] | Stub | [what it always returns] |

### 8. What Claude must never do without explicit FDE instruction

- [Governance hard stop specific item]
- [Audit-first ordering specific item]
- Add a state transition not in §4
- Hardcode any threshold — always read from `config.py`
- Write the output value field before the audit entry is COMMITTED

### 9. When to ask vs decide

**Decide and proceed:**
- Fixing a failing test by reading the spec and correcting the code
- Adding a fixture that follows the input schema

**Ask before proceeding:**
- Any change to the governance hard stop logic
- Any change to the state machine transitions
- Any change to audit-first ordering

---

## Acceptance criteria

- [ ] §3 input schema matches §2 of the capability spec exactly
- [ ] §4 state machine is complete — all states from the capability spec §9 are present
- [ ] §5 names all four required invariants with precise, code-checkable descriptions
- [ ] §7 marks exactly one tool as Real (the LLM call) and names which env var it reads
- [ ] §8 "never do" list includes the governance hard stop and audit-first ordering as specific items
- [ ] Nothing in CLAUDE.md contradicts the capability spec
