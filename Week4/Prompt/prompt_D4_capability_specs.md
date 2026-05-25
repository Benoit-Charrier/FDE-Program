# Prompt: Deliverable D4 — Two Production-Grade Capability Specifications

> **Integration specifications are a companion deliverable.** The integration preamble (system inventory, gap analysis, risk register) and per-agent integration contracts are produced using `prompt_D4_integration_specs.md`. Run those passes at the points indicated in the master sequence below. The capability specs reference external systems by name — full contracts are not produced here.

---

## Master sequence — 9 passes across two prompt files

Run one pass per session. FDE approves each pass before starting the next.

| Pass | Prompt file | Scope | Output file |
|------|-------------|-------|-------------|
| 1 | This file | Capability preamble: §1 agent selection, §2 shared entities, §3 data requirements, §4 context engineering | `Deliverables/D4_preamble_capability_spec.md` |
| 2 | `prompt_D4_integration_specs.md` | Integration preamble: §1 system inventory, §2 gap analysis, §3 risk register | `Deliverables/D4_integration_preamble.md` |
| 3a | This file | Spec A §0–§4 (agent identity, purpose/scope, inputs/outputs, entity definitions, activity catalog) | `Deliverables/D4a_capability_spec.md` |
| 3b | This file | Spec A §5–§8 (requirements, decision logic, escalation triggers, autonomy matrix) | Append to `Deliverables/D4a_capability_spec.md` |
| 4 | This file | Spec A §10–§14 (state model through ambiguity register) | Append to `Deliverables/D4a_capability_spec.md` |
| 5a | This file | Spec B §0–§4 (same shape as Pass 3a) | `Deliverables/D4b_capability_spec.md` |
| 5b | This file | Spec B §5–§8 (same shape as Pass 3b) | Append to `Deliverables/D4b_capability_spec.md` |
| 6 | This file | Spec B §10–§14 (same shape as Pass 4) | Append to `Deliverables/D4b_capability_spec.md` |
| 7 | `prompt_D4_integration_specs.md` | Integration contracts for both agents | `Deliverables/D4_integration_specs.md` |

**Why Pass 2 runs before Pass 3:** The integration preamble risk register (§3) determines whether the approval gate in the autonomy matrix (Spec A and B §8) is system-enforced or procedure-dependent. Write the integration preamble first so §8 can reference it — not forward-reference a document that does not yet exist.

**Why Pass 3 is split into 3a and 3b:** §0–§4 (identity, scope, I/O, entities, activity catalog) are structural inventory sections. §5–§8 (requirements, decision logic, escalation triggers, autonomy matrix) are logic and governance sections that require more reasoning depth. Splitting keeps each session focused and reviewable.

**§12 and §13 are required inputs for the validation plan deliverable. Do not skip or defer them.**

---

## Shared inputs — read all before starting any pass

- `Deliverables/D3_agentic_solution_architecture.md` — which agents were designed, their scope, autonomy matrix, governance hard stops, and ADR decisions. **Select the two agents from D3 that appear in the autonomy matrix. Do not invent agents not present there.**
- `Deliverables/D4_agent_purpose_document.md` — agent job-to-be-done statements, delegation archetypes, and governance constraints; use for §0 agent identity and §8 autonomy matrix
- `Deliverables/D2A_cognitive_load_map.md` — micro-tasks and workflow steps that each agent covers; use for decision logic and entity state machines
- `Deliverables/D2B_delegation_suitability_matrix.md` — archetype assignments and dimension scores per task cluster; use for §4 delegation levels, §5 requirement tiers, and §8 autonomy matrix entries
- `Deliverables/D2C_volume_value_analysis.md` — volume and value scores per task; use for §0 KPI baselines and §4 risk levels
- `Scenario/scenario_context.md` — systems, stakeholders, compliance requirements, and named constraints

**Reference standards — apply throughout:**
- `References/claude-md-examples-guide.md` — Tier 3 entity precision standard; every entity must meet this bar
- `References/production-spec-checklist.md` — quality gate; self-audit before finalising each pass
- `References/spec-ambiguity-vs-builder-mistakes.md` — ambiguity taxonomy; use when classifying §14 entries

---

## Four bars for production-grade output

A spec that fails any one of these is not production-grade.

1. **Precise enough for Claude Code to build from without guessing at intent.** Every decision has a code-evaluable condition — no "good match," no "appropriate." Every entity has typed fields, constraints, and a complete state machine. If a builder would need to ask a clarifying question to implement any section, the spec is not strong.
2. **One glossary, not two.** Every entity used by both specs is defined once in the preamble. Field names, types, enum values, and state machine transitions are identical across both specs — no silent divergence.
3. **Worked examples for edge cases.** Every branching decision in §6 includes a concrete worked example showing input values, which branch fires, and the exact output or state change.
4. **Every assumption named with a confidence level.** Every inference or design choice not directly stated in the scenario must appear in §14 with a confidence level (Low / Medium / High) and the impact if wrong. Silent assumptions are spec defects.

---

## Pass 1: Capability Preamble

**Session prompt:** "Pass 1 — write the capability preamble only: §1 through §4. Output to `Deliverables/D4_preamble_capability_spec.md`."

**Inputs for this pass:** D3 architecture, D2A cognitive load map, D2B delegation matrix, `Scenario/scenario_context.md`

Write these four sections in order.

---

### §1. Agent selection

State which two agents from D3 you are specifying and why (reference D3 priority ordering or autonomy matrix). Name which agents from D3 are explicitly deferred and why they are not specified here.

---

### §2. Shared entity definitions

Define every entity used by more than one agent. Use the Tier 3 standard from `References/claude-md-examples-guide.md` exactly. Label each entity as SHARED. Per-agent specs reference these by name — they do not redefine them.

```
Entity: [Name]
Scope: SHARED

Attributes:
- id: UUID, primary key, immutable, generated on creation
- [field]: [type], [required/optional], [constraints], [immutability rule]
- [enum fields]: enum [LIST_ALL_VALUES_IN_SCREAMING_SNAKE_CASE], exhaustive — no "other" bucket
- [string fields]: string, max [N] characters
- [numeric fields]: [type], [units], range [min–max]
- created_at: ISO 8601 timestamp, UTC, set on creation, immutable
- updated_at: ISO 8601 timestamp, UTC, updated on any modification
- created_by: UUID, reference to actor who created it, immutable
- updated_by: UUID, reference to actor who last modified it

Relationships:
- [field]: [type], foreign key to [Entity], [cardinality], on delete: [cascade / restrict / set null]

State machine:
- Initial state: [STATE]
- [STATE_A] → [STATE_B]: [transition condition — exact trigger]
- [STATE_A] → [STATE_C]: [transition condition]
- Terminal states: [STATE_X], [STATE_Y] — no valid exit

Invalid transitions (list at least 3):
- [STATE_X] → [STATE_Y]: FORBIDDEN — [reason]

Validation rules:
- [rule as a boolean statement with acceptance criterion]

Naming conventions:
- [table name, field naming pattern, enum format]
```

---

### §3. Data and system requirements

Derive what the agents collectively need from their activity catalogs. Group into four categories:

- **Input data** — what each agent reads to do its work; name the source and required latency (real-time lookup / batch-loaded / on-demand retrieval)
- **Reference data** — policy documents, playbooks, or reference materials the agents consult; note format (structured / text-extractable / image or scan-based)
- **Output targets** — systems the agents write to, or queues they push results into
- **Approval / governance channels** — how each agent's designated approver sign-off is captured and made auditable

For each requirement: what data is needed, at what granularity, at what latency.

> **Note:** This section is the starting inventory for the integration preamble (Pass 2). Name every system or data source here — Pass 2 builds its §1 system inventory from this list.

---

### §4. Context engineering design

Design the shared information architecture for both agents.

**Memory architecture:**

| Memory type | Content | Storage mechanism | Lifecycle |
|-------------|---------|-------------------|-----------|
| In-context (short-term) | | | |
| Semantic (long-term, retrieval) | | | |
| Procedural (static instructions) | | | |

**Retrieval strategy:**
- What triggers a retrieval call? (give specific examples tied to Task IDs from each agent's §4 activity catalog)
- What is the retrieval target? (top-K chunks, exact section, structured record?)
- How is retrieval quality evaluated? (false-positive matches can have downstream compliance consequences — address this explicitly)
- How are retrieval costs managed? (chunking strategy, caching, index structure)

**Pre-deployment prerequisite checklist:**

| # | What must be confirmed | Confirmed by | If unconfirmed |
|---|------------------------|--------------|----------------|
| 1 | Reference material format — machine-readable vs. image/scan-based; if any section is image-based, OCR preprocessing is a prerequisite | [role] | [what is blocked] |
| 2 | Reference material version control — machine-readable "last updated" timestamp queryable by the agent | | |
| 3 | Primary write-target system — API write access confirmed for custom fields and workflow state transitions required by the agent design | | |
| 4 | Inbound trigger mechanism — intake path (API, event, manual upload) confirmed and approved by IT security | | |
| 5 | Approval / audit trail — designated approver sign-off logged with identity and timestamp in a queryable system | | |
| 6 | Known-stale reference sections — any sections identified as out of date updated or explicitly excluded with a defined fallback | | |

Add rows for any system in §3 with unknown API availability.

**Pass 1 acceptance criteria:**
- [ ] Both agents in §1 trace to D3 autonomy matrix — not asserted
- [ ] Agents deferred in §1 named with a reason
- [ ] Every shared entity in §2 meets Tier 3 standard: typed fields with constraints, complete state machine, validation rules, naming conventions
- [ ] State machine for every shared entity: initial state named, all terminal states listed, at least 3 invalid transitions with FORBIDDEN and reason
- [ ] All enum values SCREAMING_SNAKE_CASE and exhaustive — no "other" bucket
- [ ] §3 requirements derived from both agents' activity catalogs — not invented independently
- [ ] Every system in §3 traceable to an activity or I/O requirement; systems not named in `Scenario/scenario_context.md` labelled as assumptions
- [ ] §4 pre-deployment checklist has at least 6 rows; each names what is confirmed, who confirms it, and what is blocked if unconfirmed
- [ ] §4 retrieval quality evaluation addressed explicitly — not just retrieval mechanism

---

## Pass 3a: Spec A §0–§4

**Session prompt:** "Pass 3a — write Spec A (WS1) §0 through §4. Reference the preamble by section; do not redefine shared entities. Output to `Deliverables/D4a_capability_spec.md`."

**Inputs for this pass:** `D4_preamble_capability_spec.md` (Pass 1), `D4_integration_preamble.md` (Pass 2), D3 architecture, D2A cognitive load map, `Scenario/scenario_context.md`

Write these five sections in order.

---

### §0. Agent identity

- **Agent name:** [from D3 — do not rename]
- **Job to be Done:** [one sentence — what outcome this agent produces, for whom, and what it replaces]
- **D3 reference:** [which agent block in D3 this maps to]
- **Delegation archetype:** [from D3 — name it; confirm it is consistent with D3's autonomy matrix]
- **KPIs:**

| KPI | Baseline | Target | How measured | Review cadence |
|-----|----------|--------|--------------|----------------|
| Accuracy (% of outputs correct) | | | | |
| Coverage (% of cases handled without escalation) | | | | |
| Throughput (cases per hour/day) | | | | |
| HITL rate (% routed to human review) | | | | |

All KPI targets must be specific numbers — not "improve" or "reduce." If any KPI uses a confidence threshold, also state: (a) how that threshold will be validated before deployment — not assumed from model self-reporting — and (b) the recalibration path if post-deployment audit reveals miscalibration.

- **Governance hard stop:** [restate the non-negotiable constraint from D3's autonomy matrix — the one that cannot be automated under any circumstances. Exact language — do not paraphrase.]

---

### §1. Purpose and scope

**Purpose statement:** One paragraph. What problem this agent solves, for which users, and what it explicitly does not do.

**In scope:** Bulleted list. Each item is a specific, testable capability — a builder must be able to tell from the item alone whether or not to implement it.

**Out of scope:** Bulleted list. Each exclusion names its reason: deferred / data dependency / regulatory hard stop / outside MVP. Never write "not in scope" as a reason.

---

### §2. Inputs and outputs

**Inputs table:**

| Input | Source system | Format | Required / Optional | Validation rule |
|-------|---------------|--------|---------------------|-----------------|

**Outputs table:**

| Output | Target system / recipient | Format | Trigger condition |
|--------|---------------------------|--------|-------------------|

Every input must name a source system. Every output must name a target system or recipient. Unknown sources or targets: write `[UNKNOWN — see §14]` and log an entry in the §14 ambiguity register. Full integration contracts for named systems are produced in Pass 7.

---

### §3. Entity definitions

For every entity this agent creates, reads, updates, or deletes that is **not** already defined in the preamble shared entity block, define it here using the same Tier 3 format from Pass 1 §2.

If the entity is defined in the shared block, write: *"See shared entity definition — [Entity Name]."* Do not redefine.

---

### §4. Activity catalog

Enumerate every micro-task the agent performs. Minimum 8 tasks. All columns must be populated.

| Task ID | Task name | Task type | Delegation level | Data required | Tool required | Risk level |
|---------|-----------|-----------|-----------------|---------------|---------------|------------|

**Task types:** Reasoning / Retrieval / Decision / Action / Generation  
**Delegation levels:** Fully agentic / Agent-led + HITL on condition / Human-led + Agent support  
**Risk levels:** Low / Medium / High

Every High-risk task must have a corresponding escalation trigger in §7. Every "Tool required" entry names a system from preamble §3 — full contracts are produced in Pass 7.

**Pass 3a acceptance criteria:**
- [ ] Agent name unchanged from D3
- [ ] All KPI baselines trace to scenario or labelled as assumptions; all targets are specific numbers
- [ ] Confidence threshold: pre-deployment validation method named (not "LLM self-reports"); recalibration path stated
- [ ] Governance hard stop matches D3 autonomy matrix — exact language, not paraphrased
- [ ] Every in-scope item testable; every out-of-scope item names an explicit reason
- [ ] Every input names a source system; every output names a target; every [UNKNOWN] logged with a §14 placeholder note
- [ ] No shared entity redefined — referenced by name only; per-agent entities (e.g., CalibrationRecord) defined at Tier 3 standard
- [ ] At least 8 tasks in §4 with all columns populated
- [ ] Every "Tool required" entry names a system from preamble §3

---

## Pass 3b: Spec A §5–§8

**Session prompt:** "Pass 3b — write Spec A (WS1) §5 through §8 and append to `Deliverables/D4a_capability_spec.md`."

**Inputs for this pass:** `D4a_capability_spec.md` (Pass 3a — read in full before writing), `D4_preamble_capability_spec.md`, `D4_integration_preamble.md`, `Scenario/scenario_context.md`

Write these four sections in order and append to the existing file.

---

### §5. Requirements

Number REQ-A-N. Minimum 6 requirements.

```
REQ-A-[N]: [Requirement title]
Description: [What the agent MUST do — use MUST, not should/may/could]
Acceptance criterion: [Testable, measurable — numeric threshold or boolean condition]
Delegation tier: [AGENT_ALONE / AGENT_LOGS / AGENT_PROPOSES / HUMAN_DECIDES]
Error handling: [What happens when this requirement cannot be met — name the failure path]
```

All six coverage categories must be present across the requirements:
- [ ] Agent's primary action (core job it does)
- [ ] Credential or compliance verification
- [ ] Escalation to HITL
- [ ] Audit logging
- [ ] Failure or unavailability of a required integration
- [ ] Governance hard stop from §0

---

### §6. Decision logic

For every branching decision the agent makes:

```
Decision: [Name]
Input: [what data the agent reads to make this decision]
Logic:
  IF [condition — numeric or boolean, no fuzzy language] THEN [action]
  ELSE IF [condition] THEN [action]
  ELSE [default action — must be explicit; no "handle appropriately"]
Output: [what is produced or changed as a result]
Delegation tier: [AGENT_ALONE / AGENT_LOGS / AGENT_PROPOSES / HUMAN_DECIDES]
Confidence gate: [if confidence < X%, what happens — numeric threshold required; no threshold without a named action below it]
Worked example:
  Input values: [concrete values — use real entities from the scenario where possible]
  Branch taken: [which IF condition fires and why]
  Output: [exact state change, queue item written, or action produced]
```

Every condition must be evaluable by code without human judgment. Every decision must have an explicit ELSE — no "handle appropriately." If a condition requires judgment, it belongs in the HITL path.

---

### §7. Escalation triggers

| Trigger condition | Threshold | Action | Notified party | SLA | If SLA breached |
|-------------------|-----------|--------|----------------|-----|-----------------|

All thresholds must be numeric or boolean. All SLAs must be time-bounded in minutes or hours — not days or "when needed." "If SLA breached" must contain a concrete action for every row. Every High-risk task from §4 must have a corresponding row here.

---

### §8. Autonomy matrix

The operational contract between the agent and the organisation. Every agent action must appear in exactly one tier.

**AGENT DECIDES ALONE (no HITL required):**
- [list specific decisions or actions, with any value/scope thresholds]

**AGENT ACTS, HUMAN NOTIFIED AFTER:**
- [list specific decisions or actions]

**AGENT PROPOSES, HUMAN APPROVES BEFORE ACTION:**
- [list specific decisions or actions — the governance hard stop from §0 belongs here, with exact language on what the agent prepares and what the approver authorises]

**HUMAN TAKES OVER (agent supports only):**
- [list specific triggers — name the detectable condition, not "complexity"]

**Enforcement mechanism:** State explicitly whether the primary approval gate is **technically blocking** (system-enforced workflow state transition — the agent cannot proceed without a recorded approval token) or **procedure-dependent** (the constraint relies on the approver following procedure). Cross-reference `D4_integration_preamble.md` §3 sign-off integrity risk entry. If procedure-dependent, note it as a governance risk to be addressed in §12.

**Pass 3b acceptance criteria:**
- [ ] Governance hard stop from §0 also appears as a REQ in §5
- [ ] Minimum 6 requirements; all use MUST; all have testable acceptance criteria with numeric threshold or boolean condition; all six coverage categories present
- [ ] Every IF condition evaluable by code; every decision has an explicit ELSE; every confidence gate has a numeric threshold and a named action for below-threshold cases
- [ ] All escalation thresholds numeric or boolean; all SLAs in minutes or hours; "If SLA breached" populated for every row
- [ ] Every High-risk task from §4 has a corresponding escalation trigger in §7
- [ ] Enforcement mechanism statement in §8 references `D4_integration_preamble.md` §3 sign-off integrity risk

---

## Pass 4: Spec A §10–§14

**Session prompt:** "Pass 4 — write Spec A (WS1) §10 through §14 and append to `Deliverables/D4a_capability_spec.md`."

**Inputs for this pass:** `D4a_capability_spec.md` (Pass 3 — read the full spec before writing), `D4_preamble_capability_spec.md`, `Scenario/scenario_context.md`

Write these five sections in order.

---

### §10. State model

The full lifecycle of the agent's primary output entity as a state machine.

```
States: [list all states in SCREAMING_SNAKE_CASE]
Initial state: [which state an entity enters on creation]
Terminal states: [which states have no valid exit — list all]

Transitions:
  [STATE_A] → [STATE_B]: [exact trigger condition]
  [STATE_A] → [STATE_C]: [exact trigger condition]

Invalid transitions (list at least 3):
  [STATE_X] → [STATE_Y]: FORBIDDEN — [reason]

Guard conditions:
  Transition [A → B] requires: [pre-condition that must be true before transition is allowed]
```

---

### §11. Error handling

| Failure | Detection method | Agent action | Human notification | Recovery path |
|---------|-----------------|--------------|-------------------|---------------|

All six failure categories must be present:
- Integration unavailable (primary external system down)
- Required data missing or malformed
- Agent confidence below threshold
- Governance hard stop triggered
- Duplicate or conflicting record detected
- SLA breach imminent

Every row must name a detection method — not just "an error occurs."

---

### §12. Failure modes

**Distinct from §11.** Error handling covers system and integration failures. Failure modes cover **wrong agent output** — cases where the agent runs successfully but produces an incorrect or incomplete result with downstream consequences. Do not duplicate §11 content here.

```
Failure Mode FM-A-[N]: [what a bad output looks like — concrete, not "the agent makes an error"]
Consequence: [what breaks downstream — for the team receiving the output, for the dependent process, for the business]
Detection: [how this failure would be caught; by whom; at what latency after the fact]
Recovery path: [what happens to put things right — including who is responsible]
```

Minimum 5 failure modes. All five required types must be present:
- **False routing / wrong delegation** — the agent routes a case that required escalation as a standard case; name the downstream consequence
- **Systematic confidence miscalibration** — confidence scores consistently wrong in one direction, causing high-confidence incorrect outputs to pass the threshold; the recovery path must include a threshold retuning mechanism, not just "re-run the audit"
- **Audit evidence incompleteness** — the agent produces an output the designated approver cannot defend if challenged; specify what a complete output must contain (reasoning chain, matched criteria, confidence score) and what the approver must do if they receive an incomplete record
- **Stale data input** — the agent acts on data that was current when retrieved but has since changed
- **Governance hard stop bypass** — the condition under which the hard stop from §0 could be circumvented accidentally or under time pressure, and how it would be detected

---

### §13. Audit and governance

**Audit log schema** — every agent action must produce a log entry with these typed fields:

```json
{
  "timestamp": "ISO 8601 with timezone",
  "agent_id": "string",
  "action": "enum [list all possible values]",
  "entity_type": "string",
  "entity_id": "UUID",
  "input_summary": "object — key fields used to make the decision",
  "output_summary": "object — what changed",
  "delegation_tier": "enum [AGENT_ALONE / AGENT_LOGS / AGENT_PROPOSES / HUMAN_DECIDES]",
  "human_id": "UUID or null — set if a human was involved",
  "confidence_score": "float 0–1 or null",
  "escalation_triggered": "boolean",
  "compliance_flags": "array of strings"
}
```

**Retention:** State the retention period per log type:
- Compliance logs: [period]
- Operational logs: [period]
- Audit trail: [period]

**HITL checkpoints:** For each checkpoint, all five fields must be populated:

| Checkpoint | Trigger condition | Notified party | Required response | SLA | If SLA breached |
|------------|-------------------|----------------|-------------------|-----|-----------------|

**Compliance constraints:** List every regulatory framework from the domain research deliverable that applies to this agent's actions. For each framework, state the specific requirement it creates for this agent — not just the framework name.

---

### §14. Spec ambiguity register

Classify every gap, assumption, or unknown in the spec using the taxonomy from `References/spec-ambiguity-vs-builder-mistakes.md`.

| Item | Type | Confidence | Description | Impact if unresolved | Resolution |
|------|------|------------|-------------|----------------------|------------|
| A-[N] | Spec ambiguity / Design gap / Unknown | Low / Medium / High | [what is unclear or missing] | [what a builder would guess wrong] | [client question / API doc / assumption] |

Every `[UNKNOWN]` marker in the spec must have a corresponding row here. Minimum 3 entries.

**Pass 4 acceptance criteria:**
- [ ] All states in §10 in SCREAMING_SNAKE_CASE; initial state and all terminal states explicitly named; at least 3 invalid transitions with FORBIDDEN and reason; guard conditions specified for any transition that requires a pre-condition
- [ ] All 6 failure categories present in §11; every row has a named detection method
- [ ] At least 5 failure modes in §12; all five required types present; §12 contains only wrong-output failures — no integration failures
- [ ] Confidence miscalibration failure mode includes a threshold retuning mechanism
- [ ] Audit evidence incompleteness failure mode names what a complete output must contain and what the approver does if they receive an incomplete record
- [ ] Governance hard stop bypass failure mode present
- [ ] Audit log schema in §13 lists every field with its type
- [ ] Retention period stated per log type
- [ ] Every HITL checkpoint specifies all five fields: trigger, notified party, required response, SLA, breach action
- [ ] Every applicable compliance framework listed with the specific requirement it creates for this agent
- [ ] Minimum 3 entries in §14; every [UNKNOWN] marker has a row; every entry names impact if unresolved and a resolution path

---

## Pass 5a: Spec B §0–§4

**Session prompt:** "Pass 5a — write Spec B (WS2) §0 through §4. Reference the preamble by section; do not redefine shared entities. Output to `Deliverables/D4b_capability_spec.md`."

**Inputs for this pass:** Same as Pass 3a. Also read `D4a_capability_spec.md` in full before writing — every shared entity field name, type, and enum value must be identical across both specs.

Write §0 through §4 in order. Follow exactly the same section structure as Pass 3a. All Pass 3a acceptance criteria apply, with requirement numbers REQ-B-N.

**Additional cross-spec consistency checks for Pass 5a:**
- [ ] Every entity used by both Spec A and Spec B is referenced from the preamble shared entity block — not redefined here
- [ ] All enum values that appear in both specs use identical SCREAMING_SNAKE_CASE names — no silent renaming
- [ ] Any state transition that appears in both specs is identical in trigger condition and outcome

---

## Pass 5b: Spec B §5–§8

**Session prompt:** "Pass 5b — write Spec B (WS2) §5 through §8 and append to `Deliverables/D4b_capability_spec.md`."

**Inputs for this pass:** Same as Pass 3b. Also read `D4a_capability_spec.md` §5–§8 to verify cross-spec consistency — identical enum values, consistent enforcement mechanism statement.

Write §5 through §8 in order and append. Follow exactly the same section structure as Pass 3b. All Pass 3b acceptance criteria apply.

**Additional cross-spec consistency checks for Pass 5b:**
- [ ] Autonomy matrix enforcement mechanism in Spec B is consistent with the same assessment in Spec A §8

---

## Pass 6: Spec B §10–§14

**Session prompt:** "Pass 6 — write Spec B (WS2) §10 through §14 and append to `Deliverables/D4b_capability_spec.md`."

**Inputs for this pass:** Same as Pass 4. Also read `D4a_capability_spec.md` §12–§13 to verify Spec B failure modes and audit sections are distinct — not duplicates of Spec A.

Write §10 through §14 in order. Follow exactly the same section structure as Pass 4. All Pass 4 acceptance criteria apply, with failure mode numbers FM-B-N and ambiguity register items B-N.

---

## Cross-spec consistency — verify before starting Pass 7

Before starting the integration contracts (Pass 7), confirm:
- [ ] Every entity used by more than one agent is defined exactly once in the preamble; no field name, type, enum value, or state machine transition diverges between D4a and D4b
- [ ] Both agents are present in D3's autonomy matrix — no invented agents
- [ ] Agent names in D4a and D4b are unchanged from D3
- [ ] The enforcement mechanism statement in D4a §8 and D4b §8 both reference `D4_integration_preamble.md` §3 and are mutually consistent

---

## Fail signals — do not produce output that contains these

- Agents not present in D3 — if you invent a third agent, you have not read D3
- Activity catalog with fewer than 8 tasks per spec
- KPI targets with directional language ("reduce," "improve") — every target must be a specific number
- Confidence threshold without a pre-deployment validation method named (not "LLM self-reports")
- Entity definitions without a complete state machine — no initial state, missing terminal states, or states with no valid exit
- Enum values not in SCREAMING_SNAKE_CASE or that include an "other" category
- Escalation triggers with qualitative conditions or SLAs without a time unit
- "If SLA breached" column empty for any row
- Autonomy matrix missing the system-enforced vs. procedure-dependent distinction
- State model missing initial state, terminal states, or invalid transitions
- Audit log schema that lists categories without field names and types
- HITL checkpoints without SLAs or breach actions
- Compliance framework listed by name only — must state the specific requirement it creates for this agent
- §12 failure modes that duplicate §11 error handling (integration down, timeout)
- Confidence miscalibration failure mode with no retuning mechanism
- Governance hard stop bypass failure mode missing
- Shared entities defined differently in D4a and D4b
- Requirements with "should / may / could" or without testable acceptance criteria
- Decision logic with qualitative conditions or a missing ELSE clause
- Ambiguity register with fewer than 3 entries per spec
- Any section that uses "use best judgment," "handle appropriately," or "as needed"
- Integration contracts written in this deliverable — these belong in `prompt_D4_integration_specs.md`
