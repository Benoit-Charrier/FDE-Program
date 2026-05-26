# Prompt: Deliverable D4-INT — Integration Specifications

> **These are Passes 2 and 7 in the master sequence defined in `prompt_D4_capability_specs.md`.** Run Pass 2 immediately after the capability preamble (Pass 1) and before Spec A (Pass 3). Run Pass 7 after all capability specs are approved (Passes 3–6).

## Sequence

| Pass | Scope | Run after | Output file |
|------|-------|-----------|-------------|
| 2 | Integration preamble: §1 system inventory, §2 gap analysis, §3 risk register | Capability preamble (Pass 1) | `Deliverables/D4_integration_preamble.md` |
| 7 | Integration contracts for both agents | All capability specs approved (Passes 3–6) | `Deliverables/D4_integration_specs.md` |

**Why the integration preamble runs before the capability specs:** The risk register (§3) determines whether the approval gate in the autonomy matrix is system-enforced or procedure-dependent. The capability spec authors (Passes 3 and 5) need this assessment before they can finalise §8.

---

## Pass 2: Integration Preamble

**Session prompt:** "Pass 2 — write the integration preamble: §1 system inventory, §2 gap analysis, §3 risk register. Output to `Deliverables/D4_integration_preamble.md`."

**Inputs for this pass:**
- `Deliverables/D4_preamble_capability_spec.md` §3 — the data and system requirements list; this is your starting inventory. Every system named there must have a corresponding row in §1 below.
- `Scenario/scenario_context.md` — named constraints and systems

Write these three sections in order.

---

### §1. System and data inventory

Using capability preamble §3 as the starting list, produce a complete inventory row for every system or data source required by either agent.

| System / Source | Data needed | Access type | Inferred availability | Gap / Risk | Priority | Pass 7 decision |
|-----------------|-------------|-------------|-----------------------|------------|----------|-----------------|

**Access types:** Read / Write / Read-Write / RAG / Event trigger  
**Inferred availability:** API likely available / API unknown / Manual or document-only / External service / Unknown  
**Priority:** Required (agent cannot function without it) / Important (degrades performance if absent) / Optional  
**Pass 7 decision:** Full contract / SCOPE-OUT / Omit

Include at minimum one row for each of the following:
1. Inbound work-item storage — where claims arrive and are stored
2. Primary reference or policy material — the decision framework, its format and location
3. Case or assignment management system — where triage or routing results are recorded
4. Approval / sign-off channel — how the designated approver's decision is captured with audit trail
5. Primary output target — where the agent's output artefact is stored or dispatched
6. Escalation routing system — how exception cases are queued and assigned to humans
7. Historical precedents or examples — prior accepted and rejected outputs, if available
8. Counterparty or entity registry — payer, provider, or other entities, if applicable

For systems named in `Scenario/scenario_context.md`: add the note *"Named in scenario — API specifics and integration maturity are assumptions beyond what is stated."*  
For systems not named in the scenario: add the note *"Not named in scenario — existence and API availability are assumed."*

**How the Pass 7 decision column works:**
- Required + API likely available → **Full contract** in Pass 7
- Required + API unknown → **SCOPE-OUT** in Pass 7; add an entry to the relevant capability spec §14
- Important or Optional → **Omit** from Pass 7 unless MVP scope requires it; note in capability spec §14

---

### §2. Gap analysis

For every system in §1 with "API unknown," "Manual or document-only," or "Unknown" inferred availability, produce a gap entry:

```
Gap G-[N]: [system / data source name]
What the agent cannot do without it: [specific task from D4a or D4b §4 that is blocked — name the Task ID]
Severity: Blocking (agent cannot launch) / Degrading (agent launches with reduced capability) / Low (workaround exists)
Mitigation options:
  1. [realistic option — manual workaround, alternative data source, phased approach]
  2. [realistic option]
  3. [realistic option]
Discovery action: [the specific question to ask the client to resolve this gap]
```

---

### §3. Integration risk register

For every system in §1, assess the integration risk.

| System | Risk type | Risk description | Likelihood (H/M/L) | Impact (H/M/L) | Mitigation |
|--------|-----------|------------------|--------------------|----------------|------------|

Assess all five risk types for each system. Not every system will carry every type — omit a type only if you can state why it does not apply.

**Risk types:**
- **Data quality risk** — is the reference material machine-readable, or is it a Word document or scan?
- **API availability risk** — does a documented API exist? Is there a rate limit? Is the API versioned?
- **Legal / compliance risk** — does agent access to this data create new regulatory exposure?
- **Audit trail risk** — can the agent's writes be logged in a way that satisfies audit requirements?
- **Sign-off integrity risk** — is the approval gate technically enforced by the system (workflow lock, required state transition that cannot be bypassed) or procedure-dependent (relies on the approver's discipline)? If procedure-dependent, name what prevents bypass under time pressure.

**The sign-off integrity risk entry is mandatory.** It must explicitly distinguish system-enforced from procedure-dependent enforcement. This is not a generic risk description — it must state concretely: what mechanism prevents an approver from skipping the review, and what happens if that mechanism is absent.

**This assessment feeds directly into D4a §8 and D4b §8 (autonomy matrix enforcement mechanism).** The capability spec authors must reference this entry before finalising those sections. If the approval gate is procedure-dependent, it must also appear as a governance risk in both specs' §12.

**Pass 2 acceptance criteria:**
- [ ] §1 inventory has at least 8 rows
- [ ] Every system named in capability preamble §3 has a corresponding row in §1
- [ ] Every system in §1 not named in `Scenario/scenario_context.md` is labelled as an assumption
- [ ] Pass 7 decision column populated for every row with rationale traceable to Priority + Inferred availability
- [ ] §2 gap analysis present for every §1 row with "API unknown," "Manual or document-only," or "Unknown" availability
- [ ] Every gap entry names a specific blocked Task ID from D4a or D4b §4
- [ ] Every gap entry has severity (Blocking / Degrading / Low), 3 mitigation options, and a discovery action
- [ ] §3 risk register includes a sign-off integrity entry for the approval / sign-off channel row
- [ ] Sign-off integrity entry explicitly states system-enforced vs. procedure-dependent — not a generic risk statement
- [ ] No risk register where every entry is rated Low — that is not analysis

---

## Pass 7: Integration Contracts (split into 6 sub-passes)

Pass 7 is split because 12 full contracts cannot be written in a single context window. Run sub-passes in order; each appends to `Deliverables/D4_integration_specs.md`. Do not skip ahead.

| Sub-pass | Systems covered | Output action |
|----------|-----------------|---------------|
| 7a | File scaffold + 4 SCOPE-OUT entries (S-06, S-08, S-13, S-15) + IC-S-10 (audit log) + IC-S-16 (config management) | **Create** file |
| 7b | IC-S-01 (clearinghouse inbound) + IC-S-12 (provider portal outbound) | Append |
| 7c | IC-S-02 (member eligibility) + IC-S-03 (code validation) + IC-S-05 (fee schedule) | Append |
| 7d | IC-S-04 (prior auth) + IC-S-14 (claims history) | Append |
| 7e | IC-S-09 (HITL exception management) + IC-S-11 (payment processing) | Append |
| 7f | IC-S-07 (claims management — most complex; both agents) | Append |

**Contract format applies to every full contract in every sub-pass.** Each full contract must include all ten sections:

1. **Integration purpose** — what the agent uses this system for; what it is NOT responsible for in this system; which agents use it (WS1 only / WS2 only / Both)
2. **System description** — assumed system name, base URL (DISCOVERY_REQUIRED), supported operations; note all names are assumptions unless stated in scenario
3. **Authentication & authorisation** — method (OAuth, API key, mTLS), where credentials are stored, token rotation policy, fallback if token is unavailable
4. **Endpoint contracts** — for each endpoint: HTTP method, URL pattern, required + optional fields with types, success + error response format, HTTP status code → agent action mapping, one worked example with real field values (NPI formats, claim amounts, date formats from scenario)
5. **Error handling & retry logic** — per HTTP status code and per timeout: retry (yes/no), max attempts (numeric), backoff strategy, escalation path if all retries fail
6. **Rate limits & throttling** — requests/min and requests/day (numeric); concurrent connection limit; behaviour when limit exceeded
7. **Data mapping** — internal entity field → external API field for every field exchanged; in both directions; note DISCOVERY_REQUIRED where field names are unconfirmed
8. **State synchronisation** — on-demand / cached with TTL (state the TTL in seconds) / webhook; specify which agent task triggers each call
9. **Failure modes & fallbacks** — fallback for: system down, unexpected response schema, rate limit exceeded. Each fallback must be one of: queue / escalate / fail-fast / graceful degrade. "Retry indefinitely" is not a fallback.
10. **Pre-deployment checklist** — the specific items that must be confirmed before this integration goes live (credentials provisioned, BAA signed, field names confirmed, etc.)

**SCOPE-OUT format:** For each SCOPE-OUT system, produce a single entry:
```
## IC-[S-NN] [System Name] — SCOPE-OUT
Gap reference: G-[N]
Why out of scope: [reason from integration preamble §1 Pass 7 decision]
What is needed before build can start: [specific discovery items]
Owner: [team responsible for resolving]
Stub behaviour during development: [how WS1/WS2 behaves in test if this system is absent]
Wave: [Wave 1 / Wave 2 / Post-MVP]
```

**Cross-agent contracts:** Where the same system is used by both WS1 and WS2, write one contract only. In §1 Integration Purpose and §7 Data Mapping, note agent-specific differences inline. Do not write two separate contracts for the same system.

---

## Pass 7a — File scaffold + SCOPE-OUT entries + IC-S-10 + IC-S-16

**Session prompt:** "Pass 7a — create `Deliverables/D4_integration_specs.md`. Write the document header, the 4 SCOPE-OUT entries (IC-S-06, IC-S-08, IC-S-13, IC-S-15), and two full contracts: IC-S-10 (audit log system) and IC-S-16 (configuration management). Use the contract format defined in this prompt."

**Inputs:** `Deliverables/D4_integration_preamble.md` §1–§3; `References/integration-spec-template.md`; `Deliverables/D4_preamble_capability_spec.md` §2 (entity definitions for AuditLogEntry and CalibrationRecord).

**Document header to write at top of file:**
```markdown
# D4 — Integration Specifications
## Greenfield Health Systems: Medical Claims Adjudication Transformation

> **Reading order:** This document is produced after all capability specs are approved. Read
> alongside `D4_integration_preamble.md` (system inventory, gap analysis, risk register) and
> `D4_preamble_capability_spec.md` (shared entity definitions). All system names, base URLs,
> and field names are DISCOVERY_REQUIRED unless confirmed in the scenario.

**Systems covered:** 12 full contracts + 4 SCOPE-OUT entries (S-01 through S-16).
**Pass sequence:** 7a (this pass) → 7b → 7c → 7d → 7e → 7f.
```

**IC-S-10 key contract details to include:**
- Used by: Both WS1 and WS2 (append-only write; no read access granted)
- Every ClaimRecord action produces exactly one AuditLogEntry before state transition writes
- ET-07 (audit log write failure): claim suspended with `incomplete_audit` flag; processing blocked until audit write confirmed
- Immutability must be technically enforced at storage layer; no UPDATE or DELETE permitted
- Required fields per write: `entry_id` (UUID), `claim_id`, `agent_id`, `action` (from §13 action enum in D4a/D4b), `timestamp` (ISO 8601 UTC), `input_summary`, `output_summary`, `latency_ms`
- 7-year retention minimum (clinical records; HIPAA)

**IC-S-16 key contract details to include:**
- Used by: Both WS1 (reads ROUTING CalibrationRecord) and WS2 (reads VERIFICATION CalibrationRecord)
- Agent reads once at startup; fails fast if CalibrationRecord is absent, unsigned, or fails validation
- Startup validation: state = SIGNED, cmo_signoff_date non-null, recall_achieved ≥ 0.995, holdout_set_size ≥ 500, call_site matches calling agent, classifier_version matches deployed classifier
- Two separate records required: one for call_site = ROUTING (WS1), one for call_site = VERIFICATION (WS2)
- CalibrationRecord.id is written into every ClinicalClassificationResult.calibration_record_id

**Pass 7a acceptance criteria:**
- [ ] File created with document header
- [ ] 4 SCOPE-OUT entries written: IC-S-06 (G-2), IC-S-08 (G-4 BLOCKING), IC-S-13 (G-5 Wave 2), IC-S-15 (G-6 degrading)
- [ ] Each SCOPE-OUT states: gap reference, why out of scope, what is needed before build, owner, stub behaviour, wave
- [ ] IC-S-10 full contract: all 10 sections; ET-07 failure mode explicit; immutability requirement stated; audit action enum referenced
- [ ] IC-S-16 full contract: all 10 sections; 6-field startup validation checklist; two CalibrationRecord call_sites distinguished
- [ ] Pass 7a ends with marker: `*Pass 7a complete. Pass 7b appends IC-S-01 and IC-S-12.*`

---

## Pass 7b — IC-S-01 (clearinghouse inbound) + IC-S-12 (provider portal outbound)

**Session prompt:** "Pass 7b — append IC-S-01 (clearinghouse / provider portal inbound) and IC-S-12 (provider portal / clearinghouse outbound) to `Deliverables/D4_integration_specs.md`."

**Inputs:** `Deliverables/D4_integration_preamble.md` §1 rows S-01 and S-12, §3 risk entries for S-01 and S-12; `Deliverables/D4a_capability_spec.md` §4 T-01 (intake) and T-10 (rejection notice); `References/integration-spec-template.md`.

**IC-S-01 key contract details:**
- Used by: WS1 only (intake trigger; T-01)
- Access type: Event trigger (push) or polling fallback (G-1); both paths must be specified
- WS1 receives normalised ClaimRecord from Intake Agent; S-01 is the upstream trigger, not a direct parse dependency
- Claim formats: EDI 837 (primary), PDF (secondary), portal structured form (tertiary)
- G-1 discovery action must appear in the pre-deployment checklist

**IC-S-12 key contract details:**
- Used by: WS1 only (rejection notice dispatch; T-10)
- Likely same clearinghouse partner as S-01 — note this relationship and confirm in discovery
- Output: machine-readable rejection_codes array (not free-text) + remittance advice
- Regulatory constraint: HIPAA EOB format requirements and state-specific timely notice requirements
- Delivery acknowledgement captured in AuditLogEntry; ET-09 on delivery failure

**Pass 7b acceptance criteria:**
- [ ] IC-S-01: both push trigger and polling fallback paths specified in §4 Endpoint Contracts
- [ ] IC-S-01: G-1 gap appears in §10 Pre-deployment Checklist
- [ ] IC-S-12: rejection_codes field is array type; free-text rejection reason is explicitly excluded
- [ ] IC-S-12: note whether same clearinghouse as S-01; confirm in discovery
- [ ] Both contracts: all 10 sections; worked examples with real field values
- [ ] Pass 7b ends with marker: `*Pass 7b complete. Pass 7c appends IC-S-02, IC-S-03, IC-S-05.*`

---

## Pass 7c — IC-S-02 (member eligibility) + IC-S-03 (code validation) + IC-S-05 (fee schedule)

**Session prompt:** "Pass 7c — append IC-S-02 (member eligibility), IC-S-03 (code validation reference), and IC-S-05 (fee schedule) to `Deliverables/D4_integration_specs.md`."

**Inputs:** `Deliverables/D4_integration_preamble.md` §1 rows S-02, S-03, S-05, §3 risk entries; `Deliverables/D4a_capability_spec.md` §4 T-02 (eligibility), T-04/T-05 (code validation), T-09 (fee schedule lookup); `References/integration-spec-template.md`.

**IC-S-02 key contract details:**
- Used by: WS1 only (T-02 and T-03); read-only; HIPAA PHI
- Real-time lookup: member_id + plan_id + date_of_service → active coverage status + discrepancy context
- Eligibility data lag risk (H/H per risk register): T-03 discrepancy resolution handles lag vs. true ineligibility; do not auto-deny on mismatch
- Timeout: 5s; one retry; ET-03 (HITL escalation) on persistent failure

**IC-S-03 key contract details:**
- Used by: WS1 only (T-04 ICD-10 validation, T-05 CPT validation); read-only
- Batch-loaded at startup (not real-time); pipeline startup version check required
- Annual update cycle: CMS ICD-10 (October), AMA CPT (January); stale reference triggers ET-06
- License confirmation (CMS and AMA) in pre-deployment checklist

**IC-S-05 key contract details:**
- Used by: WS1 only (T-09 payment calculation); read-only
- On-demand retrieval: provider_id + procedure_code + plan_id + modifier_codes → contracted_rate + cost_sharing_rules
- Fee schedule version check at startup; ET-06 on stale reference
- Commercially sensitive data: read-only scope only; no rate data logged in external systems

**Pass 7c acceptance criteria:**
- [ ] IC-S-02: eligibility data lag risk addressed in §9 Failure Modes (escalate, not auto-deny)
- [ ] IC-S-03: batch-load vs real-time distinction explicit; annual update cycle named in §10 checklist
- [ ] IC-S-05: modifier code array handling explicit in §7 Data Mapping
- [ ] All three: read-only access scope stated in §3 Authentication; no write access
- [ ] All three: all 10 sections; worked examples with real field values
- [ ] Pass 7c ends with marker: `*Pass 7c complete. Pass 7d appends IC-S-04 and IC-S-14.*`

---

## Pass 7d — IC-S-04 (prior auth) + IC-S-14 (claims history)

**Session prompt:** "Pass 7d — append IC-S-04 (prior authorisation system) and IC-S-14 (claims history database) to `Deliverables/D4_integration_specs.md`."

**Inputs:** `Deliverables/D4_integration_preamble.md` §1 rows S-04 and S-14, §3 risk entries; `Deliverables/D4a_capability_spec.md` §4 T-06/T-07 (prior auth); `Deliverables/D4b_capability_spec.md` §4 T-B-05 (claims history retrieval); `References/integration-spec-template.md`.

**IC-S-04 key contract details:**
- Used by: WS1 only (T-06 prior auth presence check, T-07 partial-match resolution); read-only
- Write access to prior auth system is explicitly excluded — state this in §3 and §10
- Partial match: authorised_units ≠ claimed_units triggers PRIOR_AUTH_UNIT_TOLERANCE_PCT evaluation (T-07); both fields required in response
- Timeout: 5s; one retry; ET-04 (HITL escalation) on persistent failure or absent record for procedure requiring auth
- PHI: minimum necessary access (member_id + procedure_code + service_date only)

**IC-S-14 key contract details:**
- Used by: WS2 only (T-B-05 claims history retrieval for physician review packet); read-only
- Query: member_id + diagnosis_code_range + lookback_period_days (configurable; default 365) → list of prior claims with status and dates
- May be a read view on S-07 (claims management platform) — note this relationship; single integration contract if confirmed
- Lookback period and diagnosis granularity are open assumptions (A-D4b-4 analogue); confirm before WS2 spec finalised
- Packet completeness: history absence reduces completeness_indicator score; physician notified via SCOPE-OUT flag

**Pass 7d acceptance criteria:**
- [ ] IC-S-04: write exclusion explicitly stated in §3 (no write API key or scope granted) and §10 checklist
- [ ] IC-S-04: partial-match logic (PRIOR_AUTH_UNIT_TOLERANCE_PCT) referenced in §7 Data Mapping
- [ ] IC-S-14: relationship to S-07 noted; single-contract path described if confirmed in discovery
- [ ] IC-S-14: lookback_period_days shown as configurable parameter in §4 Endpoint Contracts
- [ ] Both: all 10 sections; worked examples with real field values
- [ ] Pass 7d ends with marker: `*Pass 7d complete. Pass 7e appends IC-S-09 and IC-S-11.*`

---

## Pass 7e — IC-S-09 (HITL exception management) + IC-S-11 (payment processing)

**Session prompt:** "Pass 7e — append IC-S-09 (HITL exception management) and IC-S-11 (payment processing) to `Deliverables/D4_integration_specs.md`."

**Inputs:** `Deliverables/D4_integration_preamble.md` §1 rows S-09 and S-11, §3 risk entries; `Deliverables/D4a_capability_spec.md` §4 T-12 (escalation), T-09 (payment); `Deliverables/D4b_capability_spec.md` §4 T-B-09 (escalation); `References/integration-spec-template.md`.

**IC-S-09 key contract details:**
- Used by: Both WS1 (T-12 ET-series escalation writes) and WS2 (T-B-09 escalation writes); read-write
- May be a module of S-07 (claims management platform workflow engine) — confirm in discovery; if so, this contract is addendum to IC-S-07
- Write: EscalationPacket → exception processor queue; required fields: escalation_id, claim_id, escalation_reason (enum), required_resolution (enum options), sla_hours (numeric), assembled_by_agent, timestamp
- Read: resolution token → resolution_decision (enum), resolved_by, resolution_timestamp, claim_id
- Resolution_decision must be constrained enum (approve / reject / return_to_pipeline / request_info); free-text resolutions not accepted

**IC-S-11 key contract details:**
- Used by: WS1 only (T-09; ADMIN_CLEARED claims only); write-only push
- Agent writes to payment queue; disbursement is S-11's responsibility; agent does not confirm payment completion
- Pre-condition check in T-09: full upstream pipeline state validated before payment write (not just ClaimRecord.state = ADMIN_CLEARED)
- Payment instruction fields: claim_id, payment_amount (USD, 2 decimal places), provider_routing_id, remittance_codes array, approval_token_id, audit_log_entry_id
- Write-only scope: no read access to payment system; confirmation is asynchronous downstream

**Pass 7e acceptance criteria:**
- [ ] IC-S-09: S-07 module relationship noted; discovery action in §10 checklist
- [ ] IC-S-09: resolution_decision as constrained enum — free-text explicitly disallowed
- [ ] IC-S-09: agent-specific write payloads for WS1 vs WS2 distinguished in §7 Data Mapping
- [ ] IC-S-11: write-only scope stated in §3; no read access granted
- [ ] IC-S-11: T-09 pre-condition check (full pipeline state validation) referenced in §9 Failure Modes
- [ ] Both: all 10 sections; worked examples with real field values
- [ ] Pass 7e ends with marker: `*Pass 7e complete. Pass 7f appends IC-S-07.*`

---

## Pass 7f — IC-S-07 (claims management system)

**Session prompt:** "Pass 7f — append IC-S-07 (claims management system) to `Deliverables/D4_integration_specs.md`. This is the most complex contract; write it completely in one pass."

**Inputs:** `Deliverables/D4_integration_preamble.md` §1 row S-07, §3 risk entries (especially Sign-off Integrity entry and G-3 gap), §3 Sign-off Integrity Summary table; `Deliverables/D4a_capability_spec.md` §4 (all task IDs reading/writing ClaimRecord), §8 (autonomy matrix enforcement); `Deliverables/D4b_capability_spec.md` §4 (all task IDs reading/writing ClaimRecord), §8; `Deliverables/D4_preamble_capability_spec.md` §2 (full ClaimRecord entity and all 18 states); `References/integration-spec-template.md`.

**IC-S-07 key contract details:**

*Used by: Both WS1 and WS2 — read-write. This is the primary workflow state store.*

**Operations required (§4 Endpoint Contracts must cover all five):**

Operation A — ClaimRecord read:
`GET /claims/{claim_id}` → full ClaimRecord; used by T-01 (WS1 intake), T-B-01 (WS2 startup verification)

Operation B — ClaimRecord state transition write (the critical operation):
```
PATCH /claims/{claim_id}/state
{
  "from_state": "string — optimistic lock: system must reject if current state ≠ from_state",
  "to_state": "string — target state from defined state machine",
  "updated_by": "string — agent_id (agent-initiated) or human_id (HITL-initiated)",
  "audit_log_entry_id": "UUID — must exist in S-10 BEFORE this write is accepted"
}
```
Expected 409 response (G-3 desired system behaviour): `{ "error_code": "INVALID_STATE_TRANSITION", "current_state": "...", "requested_state": "..." }`

Operation C — ClaimRecord field write (non-state fields):
`PATCH /claims/{claim_id}/fields`; agent-writable fields only (list explicitly); state field NOT writable via this endpoint

Operation D — ClaimRecord query (WS1 T-01 batch intake):
`GET /claims?state=RECEIVED&limit=50&cursor=...` → paginated list for polling fallback (G-1 option 2)

Operation E — PhysicianReviewPacket write (WS2 T-B-07):
`POST /claims/{claim_id}/physician-packets` → packet_id; transitions claim to CLINICAL_PACKET_ASSEMBLY state

**Agent-writable fields (§7 Data Mapping — must enumerate explicitly):**
- WS1 writable: state, clinical_classification_id, rejection_codes, payment_amount, hitl_disposition, updated_by, updated_at
- WS2 writable: state (limited transitions), physician_packet_id, hitl_disposition, updated_by, updated_at
- Both agents: read all fields; no bulk delete; no schema modification

**G-3 gap and enforcement classification (§9 Failure Modes):**
- State machine enforcement is PROCEDURE-DEPENDENT until G-3 confirmed (D4a §8, D4b §8)
- If system returns 2xx for an invalid state transition (e.g., PENDING_PHYSICIAN_REVIEW → PAYMENT_CALCULATING), the agent must log a GOVERNANCE_HARD_STOP_TRIGGERED event and refuse to proceed
- Middleware guard (G-3 mitigation 2) must be in place before go-live if system-enforced is not confirmed
- Monthly audit: zero APPROVED ClaimRecords with no PhysicianReviewPacket in COMPLETE state (FM-A-5 detection)

**Pass 7f acceptance criteria:**
- [ ] All 5 operations covered in §4 with request/response schemas and status code mappings
- [ ] from_state optimistic locking field explained; 409 Conflict response and agent action defined
- [ ] Agent-writable fields enumerated for WS1 and WS2 separately in §7 Data Mapping; read-only fields named
- [ ] G-3 gap and procedure-dependent enforcement classification explicit in §9 Failure Modes
- [ ] GOVERNANCE_HARD_STOP_TRIGGERED action defined for invalid-state-transition 2xx response
- [ ] audit_log_entry_id pre-write requirement stated: S-10 write must precede S-07 state transition write
- [ ] All 10 sections; worked examples including a state transition request and a 409 Conflict response
- [ ] Pass 7f ends with marker: `*Pass 7 complete. All integration contracts delivered.*`

---

## Pass 7 composite acceptance criteria

Run after all six sub-passes are complete.

- [ ] Every Required + API likely available system from §1 has a full contract (IC-S-01, S-02, S-03, S-04, S-05, S-07, S-09, S-10, S-11, S-12, S-14, S-16)
- [ ] Every Required + API unknown system from §1 has a SCOPE-OUT entry (IC-S-06, S-08, S-13, S-15)
- [ ] Each full contract includes all 10 sections
- [ ] Every full contract includes a worked example with real field values — no placeholder values
- [ ] Every SCOPE-OUT states: gap reference, what is needed before build, owner, stub behaviour, wave
- [ ] Fallback for every system is one of: queue / escalate / fail-fast / graceful degrade
- [ ] Every system named as "Tool required" in D4a §4 or D4b §4 has a corresponding entry (full contract or SCOPE-OUT)
- [ ] G-3 sign-off integrity assessment in IC-S-07 is consistent with enforcement mechanism statement in D4a §8 and D4b §8
- [ ] No integration contract introduces a new agent capability not present in D4a or D4b

---

## Fail signals — do not produce output that contains these

- §1 inventory with fewer than 8 rows
- §1 missing any system named in capability preamble §3
- Gap analysis absent for any row with "API unknown," "Manual or document-only," or "Unknown" availability
- Gap entry that does not name a specific blocked Task ID
- §3 risk register absent or missing a sign-off integrity entry
- Sign-off integrity entry that does not distinguish system-enforced from procedure-dependent enforcement
- Risk register where every entry is rated Low
- Pass 7 decision column missing or not traceable to Priority + Inferred availability
- Full contract missing any of: authentication + credential storage, timeout value (numeric), retry per HTTP status code, rate limits (numeric), data mapping in both directions, fallback behaviour
- Fallback behaviour described as "retry indefinitely" or left unspecified
- Example request or response using placeholder values ("YOUR_VALUE," "[insert here]") — must use real field values from the scenario
- SCOPE-OUT with no resolution plan, no named owner, and no stub behaviour
- Any system named as "Tool required" in D4a or D4b that has no entry here
- Capability spec autonomy matrix enforcement mechanism inconsistent with §3 sign-off integrity assessment
- New agent capabilities introduced in the integration contracts that are not present in D4a or D4b
- Any section that uses "use best judgment," "handle appropriately," or "as needed"
