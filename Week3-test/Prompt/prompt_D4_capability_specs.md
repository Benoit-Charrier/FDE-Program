# Prompt: Deliverable D4 — Two Production-Grade Capability Specifications

## Inputs (read all before writing)
- `Deliverables/D3_agentic_solution_architecture.md` — which agents were designed, their scope, autonomy matrix, governance hard stops, and ADR decisions. **Select the two agents from D3 that appear in the autonomy matrix.** Do not invent agents not present there.
- `Deliverables/D2A_cognitive_load_map.md` — micro-tasks and workflow steps that each agent covers; use for decision logic and entity state machines
- `Deliverables/D2_engagement_intake_scope.md` — MVP scope boundary, hard constraints, and out-of-scope exclusions; do not specify capabilities excluded there
- `scenario/scenario_context.md` — systems, stakeholders, compliance requirements, and named constraints

**Reference standards (apply throughout — do not produce output that would fail these):**
- `references/integration-spec-template.md` — mandatory format for every integration contract in section 9
- `references/claude-md-examples-guide.md` — Tier 3 entity precision standard; every entity must meet this bar
- `references/production-spec-checklist.md` — quality gate; self-audit against all criteria before finalising
- `references/spec-ambiguity-vs-builder-mistakes.md` — proactively classify every ambiguity you leave in the spec; no silent gaps

## Your task
Produce two production-grade capability specifications — one per agent selected from D3. Output file: `Deliverables/D4_capability_specs.md`.

Each spec must be **precise enough for Claude Code to build from without asking a clarifying question** about the agent's purpose, scope, entities, decision logic, integration contracts, or escalation triggers. Where something cannot be specified from the scenario, classify it explicitly using the spec-ambiguity-vs-builder taxonomy (see section 14).

**Shared entity requirement:** If both agents use the same entity (e.g., Nurse, Shift, Placement, CredentialRecord), define it once in a shared section and reference it from both specs. Shared entities must be identical across both specs — no silent divergence in field names, types, enums, or state machines.

---

## Document structure

The document has two parts: a **Preamble** (written once, covering both agents) and the **Per-agent specifications** (Spec A and Spec B). The preamble establishes the shared foundation — entities, system landscape, integration readiness — that both specs draw from. Do not repeat preamble content inside individual specs; reference it by section.

---

## Preamble (written once — covers both agents)

### Preamble §1: Agent selection

State which two agents from D3 you are specifying, why these two (reference D3 priority ordering or autonomy matrix), and which agents from D3 are explicitly deferred (not specified here).

### Preamble §2: Shared entity definitions

Define every entity used by more than one agent. Follow the Tier 3 standard from `references/claude-md-examples-guide.md` exactly: attributes with types and constraints, state machine with all valid transitions, validation rules with acceptance criteria, naming conventions. Label clearly as shared. Per-agent specs reference these by name — they do not redefine them.

### Preamble §3: Data and system requirements

Before assessing available systems, derive what the agents collectively need from their activity catalogs. Group requirements into four categories:

- **Input data** — what each agent reads to do its work; name the source and required latency (real-time lookup / batch-loaded / on-demand retrieval)
- **Reference data** — policy documents, playbooks, or reference materials the agents consult; note format (structured, text-extractable, image/scan-based)
- **Output targets** — systems the agents write to, or queues they push results into
- **Approval / governance channels** — how each agent's designated approver sign-off is captured and made auditable

For each requirement, state: what data is needed, at what granularity, and at what latency.

### Preamble §4: System and data inventory

For every system or data source required by either agent:

| System / Source | Data needed | Access type | Inferred availability | Gap / Risk | Priority |
|-----------------|-------------|-------------|-----------------------|------------|----------|

**Access types:** Read / Write / Read-Write / RAG / Event trigger
**Inferred availability:** API likely available / API unknown / Manual or document-only / External service / Unknown
**Priority:** Required (agent cannot function without it) / Important (degrades performance if absent) / Optional (nice to have)

Include a row for each of the following at minimum:
1. Inbound work-item storage (where cases or shifts arrive and are stored)
2. Primary reference or policy material (the decision framework — its format and location)
3. Case or assignment management system (where triage or routing results are recorded)
4. Approval / sign-off channel (how the designated approver's decision is captured with audit trail)
5. Primary output target (where the agent's output artefact is stored or dispatched)
6. Escalation routing system (how exception cases are queued and assigned to humans)
7. Historical precedents or examples (prior accepted and rejected outputs — if available)
8. Counterparty or entity registry (background on nurses, facilities, or other entities — if applicable)

For systems named in `scenario/scenario_context.md`, add the note: *"Named in scenario — API specifics and integration maturity are assumptions beyond what is stated."* For any system you introduce that is not named in the scenario, add: *"Not named in scenario — existence and API availability are assumed."*

**How this table drives §9:** Every row in this table maps to a decision in the per-agent integration contracts:
- **Required + API likely available** → write a full integration contract in §9
- **Required + API unknown** → write a `[SCOPE-OUT]` in §9 and add an entry in §14
- **Important or Optional** → note in §14; omit from §9 unless MVP scope requires it

### Preamble §5: Gap analysis

For every system in the inventory with "API unknown," "Manual or document-only," or "Unknown" availability:

> **Gap [G-N]:** [system / data source name]
> **What the agent cannot do without it:** [specific task from the activity catalog that is blocked — name the Task ID from §4]
> **Severity:** Blocking (agent cannot launch) / Degrading (agent launches with reduced capability) / Low (workaround exists)
> **Mitigation options:** [2–3 realistic options — manual workaround, alternative data source, phased approach]
> **Discovery action:** [the specific question to ask the client to resolve this gap]

### Preamble §6: Integration risk register

For every system in the inventory, assess the integration risk:

| System | Risk type | Risk description | Likelihood (H/M/L) | Impact (H/M/L) | Mitigation |
|--------|-----------|------------------|--------------------|----------------|------------|

Risk types to consider:
- **Data quality risk** — is the reference material machine-readable, or is it a Word document or scan?
- **API availability risk** — does a documented API exist? Is there a rate limit?
- **Legal / compliance risk** — does agent access to this data create new regulatory exposure?
- **Audit trail risk** — can the agent's writes be logged in a way that satisfies audit requirements?
- **Sign-off integrity risk** — is the approval technically enforced by the system (workflow lock, required state transition), or is it a procedural agreement that relies on the approver's discipline? If procedure-dependent, name what prevents bypass under time pressure.

The sign-off integrity risk must appear in this register. The entry must explicitly distinguish system-enforced from procedure-dependent enforcement — these carry different build requirements and risk profiles.

### Preamble §7: Context engineering design

Design the shared information architecture for both agents:

**Memory architecture:**

| Memory type | Content | Storage mechanism | Lifecycle |
|-------------|---------|-------------------|-----------|
| In-context (short-term) | | | |
| Semantic (long-term, retrieval) | | | |
| Procedural (static instructions) | | | |

**Retrieval strategy:**
- What triggers a retrieval call? (give specific examples tied to Task IDs from §4)
- What is the retrieval target? (top-K chunks, exact section, structured record?)
- How is retrieval quality evaluated? (false-positive matches can have downstream compliance consequences — address this explicitly)
- How are retrieval costs managed? (chunking strategy, caching, index structure)

**Pre-deployment prerequisite checklist:**

Before build begins, the following must be confirmed:

- [ ] **Reference material format** — machine-readable (structured / text-extractable) vs. image or scan-based; if any section is image-based, OCR preprocessing is a prerequisite — **Confirmed by:** [role] — **If unconfirmed:** [what is blocked]
- [ ] **Reference material version control** — machine-readable "last updated" timestamp or revision history queryable by the agent — **Confirmed by:** — **If unconfirmed:**
- [ ] **Primary write-target system** — API write access confirmed for custom fields and workflow state transitions required by the agent design — **Confirmed by:** — **If unconfirmed:**
- [ ] **Inbound trigger mechanism** — intake path (API, event, manual upload) confirmed and approved by relevant IT security stakeholders — **Confirmed by:** — **If unconfirmed:**
- [ ] **Approval / audit trail** — designated approver sign-off is logged with identity and timestamp in a queryable system — **Confirmed by:** — **If unconfirmed:**
- [ ] **Known-stale reference sections** — any sections identified as out of date must be updated or explicitly excluded from agent scope with a defined fallback — **Confirmed by:** — **If unconfirmed:**

Add additional rows for any system in the inventory rated Required + API unknown.

---

## Required structure for EACH specification

Repeat this structure twice — once per agent. Label each spec clearly: **Spec A: [Agent Name]** and **Spec B: [Agent Name]**.

### 0. Agent identity
Taken from the D3 architecture. Provide:
- **Agent name:** [from D3 — do not rename]
- **Job to be Done:** [one sentence — what outcome this agent produces, for whom, what it replaces]
- **D3 reference:** [which agent block in D3 this maps to]
- **Delegation archetype:** [from D3B — name it; confirm it is consistent with D3's autonomy matrix]
- **KPIs:** table with baseline (from scenario or labelled assumption) and numeric target

| KPI | Baseline | Target | How measured | Review cadence |
|-----|----------|--------|--------------|----------------|
| Accuracy (% of outputs correct) | | | | |
| Coverage (% of cases handled without escalation) | | | | |
| Throughput (cases per hour/day) | | | | |
| HITL rate (% routed to human review) | | | | |

All KPI targets must be specific numbers — not "improve" or "reduce." If any KPI uses a confidence threshold, also specify: (a) how that threshold will be validated before deployment (not assumed from model self-reporting) and (b) what the recalibration path is if post-deployment audit data reveals the threshold is miscalibrated.

- **Governance hard stop:** [restate the non-negotiable constraint from D3's autonomy matrix — the one that cannot be automated under any circumstances]

### 1. Purpose and scope

**Purpose statement:** One paragraph. What problem this agent solves, for which users, and what it explicitly does not do.

**In scope:** Bulleted list. Each item is a specific, testable capability — a builder must be able to tell from the item alone whether or not to implement it. If you cannot tell, it is not specific enough.

**Out of scope:** Bulleted list with a reason for each exclusion. Use the same format as D2 section 6b — name the reason (deferred, data dependency, regulatory hard stop, outside MVP). Never use "not in scope" as a reason.

### 2. Inputs and outputs

**Inputs table:**

| Input | Source system | Format | Required / Optional | Validation rule |
|-------|---------------|--------|---------------------|-----------------|

**Outputs table:**

| Output | Target system / recipient | Format | Trigger condition |
|--------|---------------------------|--------|-------------------|

Every input must name a source system. Every output must name a target. If a system is unknown, write `[UNKNOWN — see section 14]` and log it in the ambiguity register.

### 3. Entity definitions

For every entity this agent creates, reads, updates, or deletes that is not already defined in the shared entity block, define it here using the Tier 3 standard:

```
Entity: [Name]

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

If the entity is defined in the shared block, write: *"See shared entity definition — [Entity Name]."* Do not redefine.

### 4. Activity catalog

Enumerate every micro-task the agent performs. One row per task. Include at least 8 tasks.

| Task ID | Task name | Task type | Delegation level | Data required | Tool required | Risk level |
|---------|-----------|-----------|-----------------|---------------|---------------|------------|

**Task types:** Reasoning / Retrieval / Decision / Action / Generation
**Delegation levels:** Fully agentic / Agent-led + HITL on condition / Human-led + Agent support
**Risk levels:** Low / Medium / High

Every task with risk level **High** must have a corresponding entry in the escalation triggers section (§7). Every task with a **Tool required** entry must have a corresponding integration contract in section 9.

This catalog is the bridge between the agent's job (section 0) and the requirements (section 5) — it enumerates what is built before specifying how it must behave.

### 5. Requirements

Number each requirement REQ-[SpecLetter]-[N] (e.g., REQ-A-1, REQ-B-3). Minimum 6 per spec.

```
REQ-[X]-[N]: [Requirement title]
Description: [What the agent MUST do — use MUST, not should/may/could]
Acceptance criterion: [Testable, measurable statement — includes a numeric threshold or boolean condition]
Delegation tier: [AGENT_ALONE / AGENT_LOGS / AGENT_PROPOSES / HUMAN_DECIDES — from D3 autonomy matrix]
Error handling: [What happens when this requirement cannot be met — name the failure path]
```

**Requirement coverage checklist — all six must be present across the 6+ requirements:**
- [ ] At least one covering the agent's primary action (the core job it does)
- [ ] At least one covering credential or compliance verification (if applicable to this agent)
- [ ] At least one covering escalation to HITL
- [ ] At least one covering audit logging
- [ ] At least one covering failure or unavailability of a required integration
- [ ] At least one covering the governance hard stop from section 0

### 6. Decision logic

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
Confidence gate: [if agent confidence < X%, what happens — numeric threshold required; no threshold without a named action below it]
```

**Anti-pattern:** "If the nurse is a good match" — not a decision rule. Every condition must be evaluable by code without human judgment. If it requires judgment, it belongs in the HITL path, not the decision logic.

### 7. Escalation triggers

| Trigger condition | Threshold | Action | Notified party | SLA | If SLA breached |
|-------------------|-----------|--------|----------------|-----|-----------------|

All thresholds must be numeric or boolean. SLAs must be time-bounded in minutes or hours — not days or "when needed." The "If SLA breached" column must contain a concrete action for every row.

### 8. Autonomy matrix

The operational contract between the agent and the organisation. Consolidates the delegation tiers from section 5 into a single authoritative reference for the builder. Every agent action must appear in exactly one tier.

**AGENT DECIDES ALONE (no HITL required):**
- [list specific decisions or actions, with any value/scope thresholds]

**AGENT ACTS, HUMAN NOTIFIED AFTER:**
- [list specific decisions or actions]

**AGENT PROPOSES, HUMAN APPROVES BEFORE ACTION:**
- [list specific decisions or actions — the governance hard stop from section 0 belongs here, with exact language on what the agent prepares and what the approver authorises]

**HUMAN TAKES OVER (agent supports only):**
- [list specific triggers — "complexity" is not a trigger; name the detectable condition]

**Enforcement mechanism:** For the primary approval gate, state explicitly: is the agent **technically blocked** from proceeding without a recorded approval token (system-enforced workflow state transition), or does the constraint rely on the designated approver following procedure (procedure-dependent)? If procedure-dependent, name it as a governance risk in section 12 (failure modes). This must be consistent with the sign-off integrity risk assessment in Preamble §6.

### 9. Integration contracts

Use the inventory table (Preamble §4) and gap analysis (Preamble §5) to determine what appears here:
- **Required + API likely available** → write a full contract below
- **Required + API unknown** → write a `[SCOPE-OUT]` below and add an entry in §14
- **Important or Optional** → note in §14; omit unless MVP scope requires it

For every system with a full contract, produce it using the structure from `references/integration-spec-template.md`. Each contract must include all of the following:

1. **Integration purpose** — what the agent uses this system for; what it is NOT responsible for in this system
2. **System description** — name, provider, base URL, supported operations
3. **Authentication & Authorization** — method (OAuth, API key, mTLS), where credentials are stored, token rotation policy, fallback if token is unavailable
4. **Endpoint contracts** — for each endpoint: HTTP method, URL pattern, request format (required/optional fields with types), response format (success and error), example request, example response, HTTP status code → agent action mapping
5. **Error handling & retry logic** — retry decision per HTTP status code (2xx/3xx/4xx/5xx) and per timeout: retry? max attempts? backoff strategy? escalation if all retries fail?
6. **Rate limits & throttling** — requests/min, requests/day, concurrent requests (all numeric)
7. **Data mapping** — internal field → external field, both directions, for every field exchanged
8. **State synchronization** — how the agent keeps data current (on-demand, cached with TTL, webhook)
9. **Failure modes & fallbacks** — what the agent does if this system is down, returns unexpected data, or exceeds rate limits; fallback must be one of: queue / escalate / fail-fast / graceful degrade
10. **Monitoring & logging** — what is logged per call (fields, not just "log calls"); alert thresholds

Every `[SCOPE-OUT]` must state: what is needed before build, who provides it, and what the stub behaviour is.

### 10. State model

The full lifecycle of the agent's primary output entity as a state machine:

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

### 11. Error handling

| Failure | Detection method | Agent action | Human notification | Recovery path |
|---------|-----------------|--------------|-------------------|---------------|

Required failure categories — all six must appear:
- Integration unavailable (primary external system down)
- Required data missing or malformed
- Agent confidence below threshold
- Governance hard stop triggered
- Duplicate or conflicting record detected
- SLA breach imminent

Every row must name a detection method — not just "an error occurs."

### 12. Failure modes

**Distinct from section 11 (error handling).** Error handling covers system and integration failures. Failure modes cover **wrong agent output** — cases where the agent runs successfully but produces an incorrect or incomplete result with downstream consequences.

For each failure mode:

> **Failure Mode [FM-[SpecLetter]-N]:** [what a bad output looks like — concrete, not "the agent makes an error"]
> **Consequence:** [what breaks downstream — for the team receiving the output, for the dependent process, for the business]
> **Detection:** [how this failure would be caught; by whom; at what latency after the fact]
> **Recovery path:** [what happens to put things right — including who is responsible]

Minimum 5 failure modes per spec. Required types — all must be present:

- At least one addressing **false routing / wrong delegation** — the agent routes a case that required escalation as a standard case; name the downstream consequence
- At least one addressing **systematic confidence miscalibration** — confidence scores are consistently wrong in one direction, causing high-confidence incorrect outputs to pass the threshold; the recovery path must include a threshold retuning mechanism, not just "re-run the audit"
- At least one addressing **audit evidence incompleteness** — the agent produces an output the designated approver cannot defend if challenged; specify what the output must contain to be audit-defensible (reasoning chain, matched criteria, confidence score) and what the approver should do if they receive an incomplete record
- At least one addressing **stale data input** — the agent acts on data (credential status, facility requirement profile, nurse availability) that was current when retrieved but has since changed
- At least one addressing **governance hard stop bypass** — the condition under which the hard stop from section 0 could be circumvented (accidentally or under pressure) and how it would be detected

### 13. Audit and governance

**Audit log schema** — every agent action must produce a log entry. Specify fields with types, not just "log the action":

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

**Retention:** state retention period per log type:
- Compliance logs: [period]
- Operational logs: [period]
- Audit trail: [period]

**HITL checkpoints:** for each checkpoint, specify all five fields:

| Checkpoint | Trigger condition | Notified party | Required response | SLA | If SLA breached |
|------------|-------------------|----------------|-------------------|-----|-----------------|

**Compliance constraints:** list every regulatory framework from D0A section 2 that applies to this agent's actions. For each framework, state the specific requirement it creates for this agent — not just the framework name.

### 14. Spec ambiguity register

Before submitting, classify every gap or assumption in the spec using the taxonomy from `references/spec-ambiguity-vs-builder-mistakes.md`:

| Item | Type | Description | Impact if unresolved | Resolution |
|------|------|-------------|----------------------|------------|
| [A-N] | Spec ambiguity / Design gap / Unknown | [what is unclear or missing] | [what a builder would guess wrong] | [what is needed to resolve — client question, API doc, assumption] |

Every `[UNKNOWN]` and `[SCOPE-OUT]` marker in the spec must have a corresponding entry here. Every Required + API unknown row from Preamble §4 must have a corresponding entry here. Minimum 3 entries per spec.

---

## Acceptance criteria (all must pass before finalising)

Run the full `references/production-spec-checklist.md` against both specs. Additionally:

**Preamble — system and data assessment:**
- [ ] Data and system requirements (§3) derived from both agents' activity catalogs — not invented independently
- [ ] Inventory table (§4) has at least 8 rows; every system with a Tool required entry in either §4 (activity catalog) is present
- [ ] Every system not named in `scenario/scenario_context.md` is labelled as an assumption
- [ ] Gap analysis (§5) present for every inventory row with "API unknown," "Manual or document-only," or "Unknown" availability; each gap has severity (Blocking/Degrading/Low), 2–3 mitigation options, and a discovery action
- [ ] Risk register (§6) includes a sign-off integrity risk entry that explicitly distinguishes system-enforced from procedure-dependent enforcement
- [ ] No risk register with all entries rated Low
- [ ] Context engineering design (§7) addresses retrieval quality evaluation — not just retrieval mechanism
- [ ] Pre-deployment checklist (§7) has at least 6 entries; each names what is confirmed, who confirms it, and what is blocked if unconfirmed
- [ ] §9 Integration contracts decision (full contract vs. [SCOPE-OUT] vs. omit) traces to the inventory table for every integration

**Cross-spec consistency:**
- [ ] Agent selection traces to D3 priority ordering or autonomy matrix — not asserted
- [ ] Both agents are named in D3's autonomy matrix — no invented agents
- [ ] Every entity used by more than one agent is defined exactly once in the shared block; no field name, type, enum value, or state machine transition diverges across specs

**§0 Agent identity:**
- [ ] Governance hard stop matches D3 autonomy matrix — not paraphrased
- [ ] All KPI baselines trace to scenario or labelled as assumptions
- [ ] All KPI targets are specific numbers — not "improve" or "reduce"
- [ ] Governance hard stop also appears as a REQ in §5
- [ ] If any KPI or escalation trigger uses a confidence threshold: pre-deployment validation method named (not "LLM self-reports") and post-deployment recalibration path stated

**§1 Purpose and scope:**
- [ ] Every in-scope item is testable — describes a specific capability a builder can implement
- [ ] Every out-of-scope item names an explicit reason: deferred / data dependency / regulatory hard stop / outside MVP

**§2 Inputs and outputs:**
- [ ] Every input names a source system
- [ ] Every output names a target system or recipient
- [ ] Every [UNKNOWN] source or target is logged in §14

**§3 Entity definitions:**
- [ ] Every entity (shared and agent-specific) meets Tier 3 standard: primary key (UUID, immutable), all attributes typed and constrained, timestamp fields (created_at, updated_at, ISO 8601 UTC), relationships with cascade behaviour
- [ ] State machine is complete: every state has at least one valid exit transition; terminal states are listed; no state is unreachable
- [ ] All enum values are SCREAMING_SNAKE_CASE and exhaustive — no "other" bucket
- [ ] Every string field has a max length; every numeric field has units and range
- [ ] No contradictory rules within the same entity definition
- [ ] Foreign keys specify cascade behaviour: cascade / restrict / set null

**§4 Activity catalog:**
- [ ] At least 8 tasks per spec with all five columns populated (type, delegation level, data, tool, risk)
- [ ] Every High-risk task has a corresponding escalation trigger in §7
- [ ] Every task with a Tool required entry has a corresponding integration contract in §9

**§5 Requirements:**
- [ ] Minimum 6 requirements per spec
- [ ] Every requirement uses MUST — no "should," "may," "could"
- [ ] Every requirement has a testable acceptance criterion with a numeric threshold or boolean condition
- [ ] Requirement coverage checklist satisfied: all six categories present — primary action, credential/compliance verification, escalation to HITL, audit logging, integration failure, governance hard stop

**§6 Decision logic:**
- [ ] Every IF condition is evaluable by code — no qualitative thresholds
- [ ] Every decision has an explicit ELSE default — no "handle appropriately"
- [ ] Every decision that uses a confidence score has a numeric threshold and a named action for below-threshold cases

**§7 Escalation triggers:**
- [ ] All trigger conditions are numeric or boolean
- [ ] All SLAs are time-bounded in minutes or hours
- [ ] "If SLA breached" column populated with a concrete action for every row
- [ ] Every High-risk task from §4 has a corresponding row

**§8 Autonomy matrix:**
- [ ] Four-tier matrix present; every agent action appears in exactly one tier
- [ ] Governance hard stop from §0 placed in "AGENT PROPOSES, HUMAN APPROVES" tier with exact language on what the agent prepares and what the approver authorises
- [ ] Enforcement mechanism stated and consistent with Preamble §6 sign-off integrity assessment

**§9 Integration contracts:**
- [ ] Every Required + API likely available system from Preamble §4 has a full contract
- [ ] Every Required + API unknown system from Preamble §4 has a [SCOPE-OUT] with resolution plan
- [ ] Each full contract includes all ten required sections: purpose; authentication + credential storage; request format with required/optional fields; response format (success and error); timeout (numeric); retry per HTTP status code and timeout; rate limits (numeric); data mapping both directions; fallback behaviour named; per-call logging fields

**§10 State model:**
- [ ] All states in SCREAMING_SNAKE_CASE
- [ ] Initial state and all terminal states explicitly named
- [ ] At least 3 invalid transitions listed with FORBIDDEN and reason
- [ ] Guard conditions specified for any transition that requires a pre-condition

**§11 Error handling:**
- [ ] All 6 required failure categories present
- [ ] Every row has a detection method named

**§12 Failure modes:**
- [ ] At least 5 failure modes per spec; all five required types present
- [ ] Confidence miscalibration failure mode includes a threshold retuning mechanism
- [ ] Audit evidence incompleteness failure mode names what a complete output must contain and what the approver does if they receive an incomplete record
- [ ] Every failure mode has consequence, detection, and recovery path
- [ ] Section is clearly distinct from §11 — wrong outputs only

**§13 Audit and governance:**
- [ ] Audit log schema lists every field with type
- [ ] Retention period stated per log type
- [ ] Every HITL checkpoint specifies all five fields: trigger, notified party, required response, SLA, breach action
- [ ] Every applicable compliance framework from D0A §2 listed with the specific requirement it creates for this agent

**§14 Ambiguity register:**
- [ ] Minimum 3 entries per spec
- [ ] Every [UNKNOWN] and [SCOPE-OUT] marker has a corresponding entry
- [ ] Every Required + API unknown row from Preamble §4 has a corresponding entry
- [ ] Every entry names impact if unresolved and a resolution path

**Spec precision (cross-cutting):**
- [ ] No modal verbs: MUST throughout; no "should," "may," "could"
- [ ] No fuzzy decision conditions: every IF condition evaluable by code
- [ ] No silent integration omissions: every system gap is a [SCOPE-OUT] with a resolution plan
- [ ] Production spec checklist self-assessment completed; both specs pass all criteria

---

## Fail signals — do not produce output that contains these

- Agents not present in D3's architecture — if you invent a third agent, you have not read D3
- Inventory table absent or with fewer than 8 rows — integration contract decisions made without an assessed foundation
- Gap analysis absent for any inventory row with unknown or manual-only availability
- Risk register with no sign-off integrity entry, or an entry that does not distinguish system-enforced from procedure-dependent enforcement
- Risk register with all entries rated Low — that is not analysis
- Pre-deployment checklist absent or with fewer than 6 entries
- §9 Integration contract decisions not traceable to the inventory table — contracts written or omitted without a stated rationale
- Activity catalog missing or with fewer than 8 tasks
- KPI targets with directional language ("reduce," "improve") — every target must be a specific number
- Confidence threshold without a pre-deployment validation method
- Entity definitions without a complete state machine: no initial state, missing terminal states, or states with no valid exit
- Enum values that are not SCREAMING_SNAKE_CASE or that include an "other" category
- Escalation triggers with qualitative conditions or SLAs without a time unit
- "If SLA breached" column empty for any row
- Autonomy matrix missing the enforcement mechanism distinction, or enforcement assessment inconsistent with Preamble §6
- Integration contracts missing any of: authentication + credential storage, timeout, retry per status code, rate limit, data mapping, fallback behaviour
- State model missing initial state, terminal states, or invalid transitions
- Audit log schema that lists categories without field names and types
- HITL checkpoints without SLAs or breach actions
- Compliance framework listed by name only — must state the specific requirement it creates
- Failure modes that duplicate error handling (integration down, timeout)
- Confidence miscalibration failure mode with no retuning mechanism
- Governance hard stop bypass failure mode missing
- Shared entities defined differently in Spec A and Spec B
- Requirements without testable acceptance criteria or with "should / may / could"
- Decision logic with qualitative conditions or missing ELSE clause
- Ambiguity register missing or with fewer than 3 entries per spec
- Any section that says "use best judgment," "handle appropriately," or "as needed"
