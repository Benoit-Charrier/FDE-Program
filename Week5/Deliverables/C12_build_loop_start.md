# C12 — Build Loop Start
## Greenfield Health Systems: WS1 Administrative Adjudication Agent
### Steps 1 and 2 — Spec completeness assessment before build

*Input specs: D4_preamble_capability_spec.md, D4a_capability_spec.md, D4_integration_preamble.md, D4_integration_specs.md*
*Step 3 (build) withheld pending FDE review of this completeness assessment.*

---

## Build Loop Output — Pass 1 (WS1)

---

## Step 1: What I can build confidently without asking any questions

All items below are fully specified — every decision is made, every edge case is covered, every integration contract (including stub behaviour for SCOPE-OUT systems) is defined. No assumptions are required to build these.

---

### Agent startup sequence (REQ-A-2, REQ-A-8, IC-S-16)

**Buildable components:**
- `GET /calibration-records?call_site=ROUTING&state=SIGNED` against S-16
- 6-field startup validation: state = SIGNED, cmo_signoff_date non-null, recall_achieved ≥ 0.995, holdout_set_size ≥ 500, call_site = ROUTING, classifier_version matches deployed binary
- Fail-fast on any validation failure — no graceful degrade; exit code 1; `STARTUP_CALIBRATION_CHECK_FAILED` written locally and to S-10 if reachable
- CLINICAL_CONTENT_CONFIDENCE_THRESHOLD set to `CalibrationRecord.threshold_value` on successful validation
- S-03 reference version check at startup (valid_through ≥ today)
- S-05 fee schedule version check (rate_valid_through ≥ today)
- S-07 health check before accepting first claim
- `STARTUP_CALIBRATION_CHECK_PASSED` audit event with `calibration_record_id`
- Cross-contamination guard: WS1 credential must not return VERIFICATION record (expect 403/404)

**All 5 fail-fast test cases are specified (REQ-A-2 acceptance criterion):** missing record, DRAFT state, recall_achieved = 0.990, holdout_set_size = 450, version mismatch.

---

### T-01 — Claim record intake and schema validation

**Buildable:** Full implementation.

- S-07 poll for `state = NORMALISED` records at `INTAKE_POLL_INTERVAL_SECONDS` (default 60s)
- Required-field validation: id, state, external_claim_id, member_id, provider_id, date_of_service, procedure_codes (≥1, 5-digit CPT format), diagnosis_codes (≥1, ICD-10 format), submission_format, created_at, plan_id
- date_of_service ≤ created_at date (future service date rejection)
- Duplicate detection: query S-07 for existing records with matching (external_claim_id, member_id, date_of_service, provider_id); duplicates → PENDING_HITL_EXCEPTION with trigger_type = DUPLICATE_DETECTED
- NORMALISED → ADMIN_VALIDATING state transition write (S-07 Operation B, optimistic locking with from_state)
- SCHEMA_VALIDATION_FAILED audit entry if any required field fails
- T-11 AuditLogEntry with action = CLAIM_INTAKE_VALIDATED written before state transition PATCH (audit-first ordering)

---

### T-02/T-03 + D-A-1 — Member eligibility verification and discrepancy resolution

**Buildable:** Full implementation (with one gap noted in Step 2, Q1 — but conservative safe path is fully specified).

- S-02 real-time lookup by (member_id, plan_id, date_of_service)
- 5 eligibility_status values handled: ACTIVE, INACTIVE, NOT_FOUND, PLAN_ID_MISMATCH, COVERAGE_GAP
- ACTIVE path: coverage_start_date ≤ date_of_service ≤ coverage_end_date → eligibility_result = CONFIRMED; AuditLogEntry action = ELIGIBILITY_CONFIRMED
- INACTIVE/COVERAGE_GAP path: check correction rule set; if matching rule found → CORRECTED (ELIGIBILITY_CORRECTED); if no matching rule → ET-03 (ELIGIBILITY_ESCALATED)
- API 5xx/timeout: retry once after 5 seconds; second failure → ET-03 with trigger_signal_values = {error_type: "API_UNAVAILABLE", member_id, plan_id, date_of_service}
- Null/unrecognised status → ET-03 with error: "NULL_OR_UNKNOWN_STATUS"
- ET-03 escalation: ClaimRecord.state → PENDING_HITL_EXCEPTION; EscalationPacket to S-09; response_sla_hours = 2
- Worked example: (GHS-MBR-0042891, GHS-PPO-2026, 2026-04-15) → ACTIVE → CONFIRMED (D-A-1 §6)

---

### T-04 + D-A-2 (part 1) — Code validity check

**Buildable:** Full implementation.

- Stale reference guard: if S-03.valid_through < today → log expired_reference; all T-04/T-05 calls route to ET-06 with trigger_signal_values = {expired_reference: "S-03", valid_through, today}; unaffected claims continue
- ICD-10 format validation: letter + 2–7 alphanumeric characters
- CPT format validation: exactly 5 digits
- Code membership check: each diagnosis_code ∈ S-03 valid ICD-10 set; each procedure_code ∈ S-03 valid CPT set
- invalid_codes list accumulation; if non-empty → ClaimRecord.state → REJECTED with rejection_codes populated (one INVALID_CODE entry per invalid code); T-12 assembles rejection notice to S-12
- AuditLogEntry action = CODE_VALIDITY_CHECKED
- All codes valid → pipeline advances to T-05

---

### T-05 + D-A-2 (part 2) — Coding plausibility assessment

**Buildable:** Full implementation with S-15 SCOPE-OUT stub (stub behaviour is the explicit current specification per IC-S-15).

- Structured plausibility table lookup: (procedure_codes[0], icd_chapter(diagnosis_codes[0]), provider_specialty)
- PLAUSIBLE in table → PLAUSIBLE; pipeline to T-06
- IMPLAUSIBLE in table → Haiku 4.5 call; if IMPLAUSIBLE AND confidence_score ≥ CODING_PLAUSIBILITY_CONFIDENCE_THRESHOLD (default 0.75) → ET-05; else PLAUSIBLE (log haiku result)
- Novel combination (not in table) → attempt S-15 vector retrieval (similarity ≥ 0.70)
  - S-15 SCOPE-OUT stub: retrieval returns empty; log RETRIEVAL_THRESHOLD_NOT_MET in compliance_flags; proceed as PLAUSIBLE on codes alone
  - If S-15 accessible: top-3 chunks; Haiku with context; same confidence gate
- CODING_PLAUSIBILITY_CONFIDENCE_THRESHOLD configurable (default 0.75)
- ET-05 routing_queue = CODING_SPECIALIST; response_sla_hours = 2
- Worked example: (59400, I25.10, Cardiology) → novel combination → Haiku IMPLAUSIBLE 0.91 → ET-05 (D-A-2 §6)

---

### T-06 + D-A-3 — Prior authorisation lookup

**Buildable:** Full implementation.

- S-04 read-only lookup by (member_id, procedure_codes, date_of_service) — write access explicitly excluded; confirm via integration test before deployment
- NOT_REQUIRED → auth_result = CONFIRMED; pipeline to T-08
- PRESENT_EXACT_MATCH with authorized_units = claimed_units → CONFIRMED
- API 5xx/timeout: retry once after 5 seconds; second failure → ET-04 with trigger_signal_values = {error_type: "API_UNAVAILABLE", procedure_codes, member_id, date_of_service}
- AuditLogEntry action = PRIOR_AUTH_CONFIRMED

---

### T-07 + D-A-3 — Prior auth partial-match tolerance resolution

**Buildable:** Full implementation (depends on claimed_units field — see Step 2 Q2).

- PRESENT_PARTIAL_MATCH: pct_excess = (claimed_units − authorized_units) / authorized_units
- pct_excess ≤ PRIOR_AUTH_UNIT_TOLERANCE_PCT (default 0.15) → TOLERANCE_APPROVED
  - AuditLogEntry: action = CLAIM_STATE_TRANSITION, delegation_tier = AGENT_LOGS, output_summary = {authorized_units, claimed_units, pct_excess, PRIOR_AUTH_UNIT_TOLERANCE_PCT}; include in daily tolerance batch accumulation
- pct_excess > PRIOR_AUTH_UNIT_TOLERANCE_PCT → ET-04
- NOT_FOUND → ET-04 with trigger_signal_values = {prior_auth_status: "NOT_FOUND", procedure_codes, member_id, date_of_service}
- EXPIRED → ET-04 with trigger_signal_values = {prior_auth_status: "EXPIRED", auth_record_id, expiry_date, date_of_service}
- Null/unrecognised → ET-04 with error: "NULL_OR_UNKNOWN_STATUS"
- PRIOR_AUTH_UNIT_TOLERANCE_PCT configurable (default 0.15); set by VP Operations
- AuditLogEntry actions = PRIOR_AUTH_TOLERANCE_APPLIED (tolerance case), PRIOR_AUTH_ESCALATED (ET-04)
- Worked example: authorized_units=20, claimed_units=22, pct_excess=0.10 ≤ 0.15 → TOLERANCE_APPROVED (D-A-3 §6)

---

### T-08 + D-A-4 — Clinical content routing classification

**Buildable:** Full implementation with S-15 SCOPE-OUT stub.

- Pre-condition checks (abort before any external call):
  - CalibrationRecord.state = SIGNED AND cmo_signoff_date non-null; else ET-07
  - ClaimRecord.state = ROUTING; else ET-07
- S-15 criteria retrieval: top-3 chunks (cosine ≥ 0.75, filtered by procedure_code_range and icd_chapter metadata)
  - S-15 SCOPE-OUT stub: criteria_chunks = []; log RETRIEVAL_THRESHOLD_NOT_MET in compliance_flags
- Sonnet 4.6 call with {diagnosis_codes, procedure_codes, provider_specialty, criteria_chunks}
- ClinicalClassificationResult creation: call_site = ROUTING, all required fields, threshold_applied = loaded threshold, threshold_met = computed
- 4 routing branches:
  1. ADMIN AND confidence ≥ threshold → ADMIN_CLEARED; AuditLogEntry compliance_flags = []; pipeline to T-09
  2. CLINICAL (any confidence) → PENDING_PHYSICIAN_REVIEW; ET-01; compliance_flags = ["URAC_NCQA_CLINICAL_GATE"]
  3. UNCERTAIN (any confidence) → PENDING_PHYSICIAN_REVIEW; ET-01; compliance_flags = ["URAC_NCQA_CLINICAL_GATE"]
  4. ADMIN AND confidence < threshold → PENDING_PHYSICIAN_REVIEW; ET-02; borderline_confidence_flag = true; compliance_flags = ["BORDERLINE_CONFIDENCE"]
- Link ClaimRecord.clinical_classification_id = ClinicalClassificationResult.id
- AuditLogEntry action = CLINICAL_CLASSIFICATION_COMPLETED with confidence_score; actions CLINICAL_ESCALATED_ET01, CLINICAL_ESCALATED_ET02 as applicable
- Worked examples: (93306, I25.10, Cardiology) → ADMIN 0.87 ≥ 0.70 → ADMIN_CLEARED; (27447, M17.11, Orthopedics) → CLINICAL 0.94 → PENDING_PHYSICIAN_REVIEW; (99214, J06.9, Internal Medicine) → ADMIN 0.61 < 0.70 → ET-02 (D-A-4 §6)

---

### T-09 + D-A-5 — Payment calculation with FM-A-5 hard stop

**Buildable:** Full implementation. This is the highest-confidence build target in the WS1 pipeline.

- **FM-A-5 governance hard stop — first operation of T-09, before any external call:**
  - IF ClaimRecord.state ≠ ADMIN_CLEARED: abort immediately; ET-07 with trigger_signal_values = {error: "GOVERNANCE_HARD_STOP_T09", actual_state, expected_state: "ADMIN_CLEARED", claim_id}; ClaimRecord state unchanged
  - Test: inject PENDING_PHYSICIAN_REVIEW claim → T-09 aborts within 100ms; no payment_amount written; ET-07 fires (REQ-A-6 acceptance criterion)
- S-05 fee schedule lookup by (provider_id, procedure_codes[0], plan_id, modifier_codes)
- Stale rate check: if rate_valid_through < today → ET-06 with {expired_reference: "S-05", rate_valid_through, today}
- No rate found → ET-06 with {error: "NO_RATE_FOUND", provider_id, procedure_codes, plan_id}
- contract_exception_flag = false → payment_amount = contracted_rate × (1 − cost_sharing_proportion), rounded half-up to 2 decimal places
- S-06 SCOPE-OUT path (all current T-10 calls) → contract_exception_flag = true, contract_exception_rate = null → ET-06 with {error: "CONTRACT_EXCEPTION_UNRESOLVED"}
- ClaimRecord.state → APPROVED; ClaimRecord.payment_amount = computed value
- S-11 payment instruction write with {ClaimRecord.id, payment_amount, provider_id, plan_id, audit_log_entry_id}
- AuditLogEntry: action = PAYMENT_APPROVED, delegation_tier = AGENT_LOGS, output_summary = {payment_amount, contracted_rate, cost_sharing_proportion, rate_version, audit_confirmation: true}
- Worked example: contracted_rate=312.50, cost_sharing_proportion=0.20 → payment_amount=250.00 (D-A-5 §6)

---

### T-10 + D-A-6 — Contract exception handling (SCOPE-OUT stub)

**Buildable:** Stub implementation — fully specified as current production behaviour.

- S-06 is SCOPE-OUT; all T-10 calls take first branch unconditionally:
  - contract_exception_flag = true; contract_exception_rate = null
  - ET-06 with trigger_signal_values = {error: "S06_SCOPE_OUT", provider_id, procedure_codes[0], payer_id, scope_out_reason: "S-06 API not confirmed accessible (G-2)"}
  - ClaimRecord.state → PENDING_HITL_EXCEPTION
- Post-G-2 logic is also fully specified (for when S-06 becomes available): exception record found + amendment_flag = false → apply rate; amendment_flag = true → ET-06; no record → standard path. This code can be written now (behind the stub branch).

---

### T-11 — Audit record generation (IC-S-10)

**Buildable:** Full implementation.

- Audit-first ordering enforced: S-10 POST → wait for `state = COMMITTED` response → then and only then issue S-07 state transition PATCH
- ET-07 fires on any S-10 400 response (missing required field) — no retry; claim suspended with incomplete_audit = true
- S-10 unavailability: queue locally (in-memory, max 50); retry every 10s; ops alert at 5 min sustained; no claim reaches terminal state
- Idempotency: 409 on duplicate entry_id → treat as COMMITTED; continue
- 401 credential: suspend all processing after one refresh attempt
- WS1 24-value action enum — all values mapped to pipeline steps above
- required fields: id (UUID, agent-generated), timestamp (ISO 8601 UTC ms-precision), agent_id (ws1-admin-adjudicator:{version}:{instance_id}), action (from enum), entity_type, entity_id, input_summary (min: entity_id, state_before, trigger_condition), output_summary (min: state_after, primary_output_value), delegation_tier, escalation_triggered, compliance_flags
- Conditional fields: human_id non-null when delegation_tier ∈ {HUMAN_DECIDES, AGENT_PROPOSES}; confidence_score non-null when action = CLINICAL_CLASSIFICATION_COMPLETED

---

### T-12 — Escalation packet assembly

**Buildable:** Full implementation including S-08 SCOPE-OUT stub.

- EscalationPacket entity fields: all defined in preamble §2
- routing_queue per trigger: ET-01/02 → PHYSICIAN_HITL (→ S-08 SCOPE-OUT stub); ET-03/04/06/07 → EXCEPTION_PROCESSOR (→ S-09); ET-05 → CODING_SPECIALIST (→ S-09)
- S-08 SCOPE-OUT stub: write EscalationPacket to S-07 with QUEUE_DELIVERY_FAILED flag; AuditLogEntry action = ESCALATION_DELIVERY_FAILED; ClaimRecord remains in PENDING_PHYSICIAN_REVIEW
- 60-second SLA for packet delivery (REQ-A-3 acceptance criterion a)
- trigger_signal_values must be machine-parseable JSON, no free-text — all trigger-specific signal objects are defined in §7
- pipeline_state_at_escalation: snapshot of all completed pipeline step outputs at time of trigger
- response_sla_hours: ET-01/02/06 = 4h; ET-03/04/05 = 2h; ET-07 = 1h (from §7 escalation trigger table)
- AuditLogEntry actions = ESCALATION_TRIGGERED, ESCALATION_DELIVERED, ESCALATION_DELIVERY_FAILED

---

### Integration contracts fully buildable (WS1)

| Contract | Status | Note |
|----------|--------|------|
| IC-S-10 Audit log | Build | Append-only; both agents; full 10-section contract |
| IC-S-16 Config management | Build | Read-only at startup; CalibrationRecord; 6-field validation |
| IC-S-01 Clearinghouse inbound | Build | WS1 reads S-07 for NORMALISED records; IC-S-01 specifies intake pipeline interface |
| IC-S-12 Provider portal outbound | Build | Rejection notice write; EDI 835 format; HIPAA EOB compliance |
| IC-S-02 Member eligibility | Build | Real-time read-only lookup; 5xx retry; ET-03 on persistent failure |
| IC-S-03 Code validation | Build | Batch-loaded at startup; version check; AMA CPT license required |
| IC-S-05 Fee schedule | Build | On-demand at T-09; contracted rate + cost sharing; ET-06 on miss |
| IC-S-04 Prior auth | Build | Read-only; write exclusion via integration test; ET-04 paths |
| IC-S-09 HITL exception management | Build | EscalationPacket write + resolution poll; constrained resolution enum |
| IC-S-11 Payment processing | Build | Write-only; 202 QUEUED terminal; FM-A-5 pre-condition enforced upstream |
| IC-S-07 Claims management | Build | Most complex; 5 operations; optimistic locking via from_state; audit-first ordering |

---

## Step 2: What I need to clarify before building the rest

Nine open questions. Six are spec gaps (not pre-documented). Three reference pre-documented gaps. Ordered by impact.

---

> *T-07, T-03, REQ-A-7 — ClaimRecord.claimed_units field*: D-A-3 references "claimed_units: integer (derived from ClaimRecord procedure code quantity field)" and REQ-A-7 requires logging `claimed_units` in AuditLogEntry.output_summary. The ClaimRecord entity in D4_preamble §2 has `procedure_codes: array of strings` but **no quantity field** — there is no `claimed_units`, `procedure_quantities`, or equivalent attribute anywhere in the entity definition. How are claimed units encoded in ClaimRecord? If unanswered, I would assume a parallel `procedure_quantities: array of integers` field corresponding positionally to `procedure_codes` — this is **risky** because if ClaimRecord is built without this field, REQ-A-7 cannot be satisfied and the T-07 tolerance calculation has no input. *(Not pre-documented — internal spec gap: entity definition and decision logic are inconsistent)*

---

> *IC-S-16 §4, D4a §3 — CalibrationRecord.call_site field missing from entity definition*: IC-S-16 specifies a `call_site` query parameter, returns it in the API response, and the startup validation field 5 says "call_site must match calling agent: ROUTING for WS1." But the CalibrationRecord entity definition in D4a §3 (lines 128–224) does not list `call_site` as an attribute. The two separate CalibrationRecords (ROUTING threshold 0.700, VERIFICATION threshold 0.850) are distinguished by call_site in the API — if this field is absent from the entity, the distinction cannot be stored or validated. If unanswered, I would assume `call_site: enum [ROUTING, VERIFICATION], required, immutable` must be added to CalibrationRecord — this is **safe** (the addition is unambiguous) but the entity definition needs the correction before the schema is built. *(Not pre-documented — omission from entity definition)*

---

> *T-03 — Eligibility correction rule set content*: D-A-1 references "eligibility correction rule set (internal): keyed by discrepancy_type; each rule has a match_condition (boolean expression) and a corrective_action (string)." No rules are defined anywhere in D4a, preamble, or integration preamble. Without rules, T-03's CORRECTED path (and ELIGIBILITY_CORRECTED audit action) cannot be exercised. If unanswered, I would assume an **empty rule set** — all non-ACTIVE eligibility cases escalate ET-03. This is **safe** (conservative default) but means the CORRECTED branch is dead code at build time until the ops team supplies rules. *(Not pre-documented as a gap number — the rule set is referenced but its content is a design output, not a system prerequisite)*

---

> *§8, IC-S-07 — G-3 state machine enforcement: architectural decision point*: D4a §8 explicitly defers: "procedure-dependent until confirmed, per D4_integration_preamble.md §3 sign-off integrity risk (G-3 discovery required)." Two build architectures are possible: (1) direct S-07 PATCH with agent-side REQ-A-6 pre-condition check only; (2) middleware guard (G-3 mitigation option 2) that validates all state transitions before forwarding to S-07. This is not a missing spec — it is an explicit deferred decision. If unanswered, I would implement option 1 (agent-side pre-condition, as REQ-A-6 requires) and add a `// G-3: replace with middleware guard if system enforcement not confirmed` marker at every state transition write — this is **safe** for build purposes but means the governance gate is procedure-dependent until G-3 discovery completes. *(Pre-documented: G-3)*

---

> *T-12, REQ-A-3 — EscalationPacket.required_resolution question text per trigger*: REQ-A-3 acceptance criterion (b) states "zero EscalationPackets with null trigger_signal_values or a required_resolution field containing free-text without enumerated options." The specific enumerated question text for each of ET-01 through ET-07 is not written anywhere in D4a or preamble §2. The format constraint (yes/no or enumerated options) is specified but the content is not. If unanswered, I would assume the following (propose for FDE approval):
> - ET-01/02: `"Route as: [CLINICAL_CONFIRMED / ADMIN_CONFIRMED / NEEDS_ADDITIONAL_INFO]"`
> - ET-03: `"Eligibility: [CONFIRM_ELIGIBLE / CONFIRM_INELIGIBLE / RETURN_TO_SUBMITTER]"`
> - ET-04: `"Prior auth: [APPROVE_WITH_EXCEPTION / REJECT / RETURN_TO_SUBMITTER]"`
> - ET-05: `"Coding: [CONFIRM_VALID / CONFIRM_IMPLAUSIBLE / RETURN_TO_SUBMITTER]"`
> - ET-06: `"Contract exception: [APPLY_EXCEPTION / USE_STANDARD_RATE / REJECT / RETURN_TO_SUBMITTER]"`
> - ET-07: `"Audit failure: [RECONSTRUCT_AND_CONTINUE / REJECT_CLAIM / ESCALATE_TO_COMPLIANCE]"`
>
> This is **risky** if the ops team has specific resolution language tied to downstream workflow steps in S-09. The question text must align with what the HITL exception processor interface expects as valid resolution_decision values. *(Not pre-documented — spec is silent on content, only on format)*

---

> *D-A-1, IC-S-02 — Eligibility data lag rule: last_verified_at field inconsistency*: IC-S-02 §4 specifies: "INACTIVE or COVERAGE_GAP with last_verified_at > 24h = data lag candidate; do NOT auto-deny; escalate ET-03." But the S-02 response schema in D4a §2 inputs table lists only: `eligibility_status`, `coverage_start_date`, `coverage_end_date`, `error_code` — `last_verified_at` is absent. D-A-1's logic branches do not reference `last_verified_at`. If unanswered, I would implement D-A-1 as written (all INACTIVE/COVERAGE_GAP → ET-03 regardless of lag) — this is **safe** (the data lag rule makes the ET-03 escalation more targeted, but omitting it only adds false escalations, not false approvals). The inconsistency should be resolved: either add `last_verified_at` to the D4a §2 S-02 response schema, or remove the lag rule from IC-S-02 §4. *(Not pre-documented — inconsistency between D4a §2 and IC-S-02 §4)*

---

> *REQ-A-7 — Daily tolerance batch report delivery mechanism*: REQ-A-7 says tolerance-approved claims "MUST be included in a daily batch summary report to the HITL exception team" but specifies no delivery mechanism — no target system, no format, no trigger time, no recipient endpoint. If unanswered, I would accumulate `CLAIM_STATE_TRANSITION` + `delegation_tier = AGENT_LOGS` + `action = PRIOR_AUTH_TOLERANCE_APPLIED` AuditLogEntry records (already required by REQ-A-7) and mark the active delivery as `DISCOVERY_REQUIRED` — this is **safe** because the audit trail is created regardless, and the report is a query on top of that data. The delivery mechanism needs to be confirmed (push to ops team dashboard, email digest, S-09 daily batch write, or other). *(Not pre-documented — delivery mechanism is a specification gap)*

---

> *D-A-6, IC-S-07 — payer_id derivation for T-10 contract exception lookup*: D-A-6 inputs include "payer_id: string (derived from plan configuration)" as a key field for the S-06 exception record lookup (provider_id + payer_id + procedure_code_range). ClaimRecord has `plan_id` but not `payer_id`. The derivation step (plan_id → payer_id) is not specified — no lookup table, no config entry, no IC-S-16 field. If unanswered, I would treat this as a configuration lookup at T-10 time (a plan-to-payer mapping table in agent config) — this is **safe for now** because T-10 is currently SCOPE-OUT (ET-06 fires unconditionally for all T-10 calls), so payer_id derivation does not affect Wave 1 behaviour. It must be resolved before S-06 goes live. *(Not pre-documented — derivation mechanism is absent from spec)*

---

> *IC-S-01, T-08 — provider_specialty field extraction from EDI 837*: ClaimRecord.provider_specialty is used by T-08 (D-A-4) as a classifier signal and is set at creation (immutable). IC-S-01 §7 data mapping table maps provider_npi → provider_id but does not show a mapping for provider_specialty from any EDI 837 segment. In EDI 837, the rendering provider's taxonomy code appears in the PRV segment (Loop 2310B); converting taxonomy code → specialty description requires a NUCC provider taxonomy reference table. This mapping step is not specified in the Intake Agent or WS1 specs. If unanswered, I would assume the Intake Agent handles taxonomy → specialty normalisation before writing to S-07 — this is **safe for WS1 build** (WS1 reads provider_specialty as already normalised) but is an Intake Agent spec gap that must be confirmed. *(Not pre-documented — Intake Agent spec is out of scope for this build pass; assumption is reasonable)*

---

## Summary for FDE review

**9 open questions found.** Ordered by build impact:

| # | Question | Impact | Pre-documented? | Safe to proceed with assumption? |
|---|---------|--------|-----------------|----------------------------------|
| Q2 | claimed_units missing from ClaimRecord entity | HIGH — T-07 tolerance arithmetic has no input; REQ-A-7 undeliverable | No | Risky — entity schema change required |
| Q9 (call_site) | CalibrationRecord.call_site missing from entity definition | HIGH — startup validation field 5 cannot be implemented | No | Safe — add the field |
| Q4 | required_resolution question text per ET trigger | MEDIUM — REQ-A-3 acceptance criterion (b) will fail if text doesn't match S-09 expectations | No | Risky — needs FDE approval of proposed text |
| Q1 | Eligibility correction rule set content | MEDIUM — T-03 CORRECTED branch is dead code | No | Safe — empty rule set is conservative |
| Q3 | G-3 state machine enforcement architecture | MEDIUM — governance gate strength depends on this | G-3 | Safe — agent-side check is required regardless |
| Q6 | last_verified_at inconsistency (D4a §2 vs IC-S-02 §4) | LOW — spec inconsistency; safe default exists | No | Safe — D-A-1 as written is conservative |
| Q5 | Daily tolerance batch report delivery | LOW — audit trail is created; delivery is a query on top | No | Safe — stub delivery as DISCOVERY_REQUIRED |
| Q7 | payer_id derivation for T-10 | LOW — T-10 is SCOPE-OUT; only matters post-G-2 | No | Safe — deferred to Wave 1.5 |
| Q8 | provider_specialty EDI 837 extraction | LOW — WS1 reads normalised value; Intake Agent gap | No | Safe — Intake Agent assumption |

**Blocking before Step 3 (recommend FDE decision):**
- Q2: Add `procedure_quantities: array of integers` to ClaimRecord entity, or specify an alternative encoding for claimed units.
- Q9: Add `call_site: enum [ROUTING, VERIFICATION]` to CalibrationRecord entity definition in D4a §3.
- Q4: Confirm or revise the proposed required_resolution question text for ET-01 through ET-07.

**Non-blocking (safe to proceed with stated assumptions):**
- Q1, Q3, Q5, Q6, Q7, Q8 — all have safe conservative defaults that do not create false approvals or compliance exposure.
