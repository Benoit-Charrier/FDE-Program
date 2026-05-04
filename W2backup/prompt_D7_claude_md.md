# Prompt: Deliverable 7 — CLAUDE.md for the Project

## Scenario (read this first)
See `scenario\scenario_context.md` for the full scenario, work streams, tooling, and named-systems guidance. Do not invent numbers, systems, or constraints not present in the scenario. Every number you use must trace back to the scenario or be explicitly labelled as an assumption.

**Agent context:** Write the CLAUDE.md for the agent designed in D4 — the primary agentic target identified in D3. The CLAUDE.md must be consistent with D4's activity catalog, autonomy matrix, and escalation triggers. Reference the named tooling from `scenario\scenario_context.md` when specifying system integrations.

---

## Your task
Produce a CLAUDE.md for the primary agentic target identified in D4. Output file: `deliverables\CLAUDE.md`.

This file is the agent's project constitution. It must be precise enough that an AI coding agent begins development without needing to ask a clarifying question about the agent's purpose, the entities it works with, the rules it follows, or what to do in ambiguous situations.

Reference: `references\claude-md-examples-guide.md` — aim for Tier 3 (Strong). Use that reference to self-assess before submitting.

---

## Required structure

### Section 0: Table of contents
List all sections by number and title, in order. Generate this after the full document is written — section titles must match exactly.

### Section 1: Project Purpose
Two to three sentences. What is this agent? What outcome does it produce? Who uses it and in what context? This should match D4's Job to be Done exactly.

### Section 2: Core Entities
Define every entity the agent works with. For each entity:
- All attributes with types, constraints, and whether they are immutable
- Valid state machine (if the entity has a lifecycle — e.g., a Contract or a ClauseReview has states)
- Naming conventions (snake_case, enums in SCREAMING_SNAKE_CASE, etc.)

**Required entities (at minimum):**

#### Contract
Attributes to define:
- Unique identifier
- Vendor/counterparty name
- Date received
- Primary case document size (state the valid range from scenario_context.md if provided, otherwise label as assumption)
- Routing classification: derive the categories and any stated distribution from scenario_context.md
- Status: `PENDING_REVIEW` / `IN_REVIEW` / `REVIEWED_STANDARD` / `REDLINE_DRAFT` / `AWAITING_APPROVAL` / `APPROVED` / `ESCALATED` / `CLOSED`
- Assigned reviewer (lawyer or paralegal ID, nullable until assigned)
- Lawyer sign-off name (required before status can move to `APPROVED`; the GC's hard rule)
- Lawyer sign-off timestamp

State machine: define every valid transition between Contract statuses. Include the condition that triggers each transition. The transition from `AWAITING_APPROVAL` → `APPROVED` must require `lawyer_signoff_name` to be non-null and must be triggered only by a named lawyer action — never by the agent acting alone.

#### ClauseReview
Attributes to define:
- Contract ID (foreign key)
- Task-unit type (derive the categories from scenario_context.md — the policy-defined types the agent classifies against)
- Extracted text (the clause as found in the contract)
- Playbook match status: `COMPLIANT` / `MINOR_DEVIATION` / `MAJOR_DEVIATION` / `MISSING` / `REQUIRES_SENIOR_REVIEW`
- Agent confidence score (float 0.0–1.0)
- Agent reasoning summary (brief explanation of the classification)
- Human override (nullable — if a lawyer overrides the agent classification, record it here)

#### ReviewDecision
The record of what happens after clause review:
- Decision type: `ACCEPT_AS_IS` / `SEND_REDLINE` / `ESCALATE` / `REJECT_CONTRACT`
- Clause review IDs affected
- Decision made by: agent or named human (with role)
- Requires lawyer approval: boolean (true whenever decision type is `SEND_REDLINE` or `REJECT_CONTRACT`)
- Approval token: the mechanism by which lawyer sign-off is cryptographically or audit-trail recorded

### Section 3: Classification Rules
Define the classification logic precisely:

- What makes a case `STANDARD` (or equivalent routing category)? (all policy-defined task-unit types assessed; all `COMPLIANT` → `STANDARD`)
- What makes a case `NEGOTIABLE`? (at least one task unit `MINOR_DEVIATION`, none `REQUIRES_SENIOR_REVIEW`)
- What makes a case `ESCALATION_REQUIRED`? (at least one task unit `MAJOR_DEVIATION` or `REQUIRES_SENIOR_REVIEW`)

For each clause type, define what `COMPLIANT`, `MINOR_DEVIATION`, `MAJOR_DEVIATION`, and `REQUIRES_SENIOR_REVIEW` means in terms of the playbook. Since the scenario does not provide playbook specifics, state the rule as a retrieval instruction: "compliance is determined by comparing the extracted content against the policy/playbook section for [task-unit type] using semantic similarity with threshold X; any match below threshold triggers MINOR_DEVIATION."

State explicitly: what threshold triggers `MAJOR_DEVIATION` vs. `MINOR_DEVIATION`? (This is a key design decision — state it as an assumption if not derivable from the scenario.)

State explicitly: what triggers `REQUIRES_SENIOR_REVIEW`? (Name the conditions, not just "complex clauses.")

### Section 4: Validation Rules
For each entity and each operation (create, update, transition):
- List the validation rules as acceptance criteria
- Be specific: "lawyer_signoff_name must be a non-null string matching a name in the approved-lawyers list before Contract.status can transition to APPROVED"

### Section 5: What the Agent Must NOT Do
Hard stops — the agent must refuse these even if instructed:

- Never trigger the governance-gated output action (as defined in D4's out-of-scope section) without a ReviewDecision record with `requires_lawyer_approval = true` AND a valid `approval_token` from the designated approver
- [Add at least 4 more hard stops derived from D4's out-of-scope section]

### Section 6: Handling Ambiguity and Escalation
For each ambiguous condition the agent will encounter, specify exactly what it does:

1. **Clause type not matching any of the 7 playbook categories:** [specific action]
2. **Agent confidence score below threshold:** [specific threshold; specific action]
3. **Primary case document outside the expected size or format range** (use the range from scenario_context.md if stated): [specific action]
4. **Conflicting signals between task-unit types** (e.g., one assessment supports accept while another requires escalation): [specific action]
5. **Playbook retrieval returns no relevant content:** [specific action]
6. [Add at least 2 more scenario-specific conditions]

### Section 7: When to Ask vs. When to Decide
**Decide alone (no clarification needed):**
- [list of decisions — specific, not generic]

**Ask the lawyer/paralegal before proceeding:**
- [list of conditions — specific, not generic]

**Never proceed without explicit human action:**
- [list — the sign-off gate and anything else irreversible]

---

## Acceptance criteria (all must pass)

- [ ] Matches Tier 3 from `references\claude-md-examples-guide.md` (check self-assessment below)
- [ ] All three core entities defined with full attributes, types, and state machines
- [ ] Classification rules are specific enough to implement (not "use your judgment")
- [ ] Validation rules include the lawyer sign-off constraint with exact language
- [ ] Hard stops section present with at least 5 entries
- [ ] Ambiguity handling has at least 6 specific conditions with specific responses
- [ ] "When to ask vs. when to decide" is explicit — no ambiguity about when the agent acts alone
- [ ] No section that says "use best judgment" — every ambiguous case must have a defined resolution
- [ ] Contract state machine includes all valid transitions with conditions

## Self-assessment (complete before submitting)
After drafting the CLAUDE.md, answer these questions. If any answer reveals a gap, fix it:

1. If a development team asked "what confidence threshold triggers escalation?", is the answer in this document?
2. If someone asked "how is the primary governance/approval constraint enforced at the system level?", is the answer in this document?
3. If someone asked "what happens if the policy document doesn't cover the case type?", is the answer in this document?
4. Could an AI coding agent implement the state machine from this document without asking a clarifying question?

## Fail signals — do not produce output that contains these

- Generic instructions like "ensure data consistency" without specifying what data and what consistency rules
- The governance/approval rule described in prose only — it must appear in both the entity definition (as a field constraint) and the state machine (as a transition condition)
- Ambiguity handling section that says "escalate to human" without naming which human, in what channel, with what information
- Hard stops missing the primary one: no governance-gated output action without the required approval token (derive the specific action from D4)
- A state machine where the agent can transition a case to `APPROVED` without the designated approver's sign-off
