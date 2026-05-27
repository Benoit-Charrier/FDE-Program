# C4 — Agent Purpose Document: WS1 Administrative Claims Adjudication Agent
**Engagement:** Greenfield Health Systems — Medical Claims Adjudication Transformation
**Prepared:** 2026-05-23
**Source of truth:** `Scenario/scenario_context.md`; informed by `Deliverables/D2B_delegation_suitability_matrix.md`

---

## 0. Executive Summary

- **Purpose:** The WS1 agent adjudicates the estimated 65% of Greenfield Health Systems medical claims (~1,300/day) that contain no genuine clinical content — running each through a 10-step eligibility, coding, prior auth, and payment pipeline — replacing the current 35-minute full-manual review workflow for administrative claims and producing an approved, rejected, or structured escalation output with a complete, defence-ready audit record.
- **Autonomy boundary:** The agent decides alone on claims where the clinical content classifier returns `admin` at or above the configured confidence threshold, all eligibility, coding, and prior auth checks pass, and the payment calculation falls within confirmed contract terms; any claim where the classifier returns `clinical` or `uncertain` — at any confidence level — is placed in a `pending_physician_review` queue state that the payment step cannot read from until a CMO-authorised clinical reviewer records an approval token, satisfying the URAC/NCQA accreditation requirement for physician sign-off on every claim with clinical implications.
- **Primary failure risk:** The most consequential failure is a false negative from the clinical content classifier — a claim with genuine clinical content classified as `admin` and auto-approved without physician review — which constitutes a URAC/NCQA compliance event and triggers agent suspension; this failure is mitigated by a pre-deployment recall gate (≥99.5% on a CMO-labelled holdout set, not model self-reported scores), a monthly audit of 5% of auto-approved claims by a clinical reviewer, and a threshold recalibration protocol that requires CMO sign-off before restoring full auto-approval.

---

## 0b. Table of Contents

- [0. Executive summary](#0-executive-summary)
- [0b. Table of contents](#0b-table-of-contents)
- [1. Agent identity](#1-agent-identity)
- [2. Primary objectives](#2-primary-objectives)
- [3. KPIs](#3-kpis)
- [4. Activity catalog](#4-activity-catalog)
- [5. Autonomy matrix (Decision Authority Matrix)](#5-autonomy-matrix-decision-authority-matrix)
- [6. Escalation triggers](#6-escalation-triggers)
- [7. Failure modes](#7-failure-modes)
- [8. Out-of-scope (hard stops)](#8-out-of-scope-hard-stops)

---

## 1. Agent Identity

- **Agent name:** WS1 Administrative Claims Adjudication Agent
- **Cognitive contract:** Adjudicate every claim that contains no genuine clinical content — producing an approved or rejected payment determination with a defensible audit record — so that physician time is reserved exclusively for claims requiring clinical judgment.
- **Business context:** Operates within the claims processing team (45 processors total). Receives structured claim records from the INT intake agent. Produces three output types: (a) approved claims routed to payment processing, (b) rejected claims returned to the provider resubmission queue with specific, actionable error codes, and (c) escalation packets routed to either the HITL exception processor queue or the physician HITL queue. Clinical-classified outputs route to WS2. Owned operationally by VP Operations (James Liu); the clinical routing boundary is governed by CMO (Dr. Marcus Webb).
- **Decision authority pattern:** Agent-led with conditional human oversight. The agent executes autonomously across the administrative path; human review is triggered only when specific detectable conditions are met — confidence below threshold, eligibility discrepancy, coding implausibility, prior auth mismatch beyond tolerance, or any classification returning `clinical` or `uncertain`. The URAC/NCQA clinical routing boundary is a hard system-enforced stop, not a soft policy.

---

## 2. Primary Objectives

1. Auto-adjudicate ≥80% of administrative-path claims (estimated ~1,300/day) without human escalation, measured as claims reaching `approved` or `rejected` status without entering any HITL queue.
2. Achieve ≤5-day end-to-end cycle time for all administrative-path claims, measured from claim receipt to payment determination, eliminating the contractual SLA penalty exposure currently incurred on claims exceeding 7 days.
3. Achieve ≥99.5% recall on clinical claims before go-live — confirmed against a CMO-labelled holdout set, not model self-reported scores — so that no claim with genuine clinical content reaches the payment path without physician review.

---

## 3. KPIs

| KPI | Baseline | Target | Measurement method | Review cadence |
|-----|----------|--------|--------------------|---------------|
| Clinical classifier recall (% of clinical claims correctly routed to physician queue) | Not measured — all claims currently manual | ≥99.5% — hard go-live gate | Labelled holdout set (≥500 claims, CMO clinical team labelling) pre-deployment; monthly audit of 5% random sample of auto-approved claims post-deployment, reviewed by CMO-authorised clinical reviewer, recorded in audit log | Pre-deployment: once before go-live. Post-deployment: monthly |
| Auto-adjudication rate (% of admin-path claims reaching approved/rejected without HITL) | 22% across all claim types (scenario.md) — baseline for admin path alone is not stated separately [Assumption A-5] | ≥80% of administrative-path claims | Count of claims reaching terminal status without entering any HITL queue ÷ total admin-path claims processed, recorded in the claims management system | Weekly |
| HITL rate (% of admin-path claims requiring exception processor review) | 100% — all claims currently manual (scenario.md) | ≤20% of administrative-path claims | Count of claims entering HITL exception queue ÷ total admin-path claims, excluding physician queue escalations (tracked separately) | Weekly |
| Cycle time — admin path (calendar days from receipt to payment determination) | 8 days average; 9+ days per VP Operations (Exchange 3) | ≤5 days | Timestamp delta from claim receipt to `approved` or `rejected` status in claims management system | Daily; SLA breach alert at day 4 |
| Throughput (claims processed per agent-hour) | ~1.7 claims/hour per processor (35 min/claim × 1 processor; scenario.md) | ≥120 claims/hour (agent execution, excluding HITL wait time) [Assumption: agent pipeline execution is sub-30 seconds per claim] | Claims processed ÷ agent-hours logged, recorded in execution metrics | Daily |

**Confidence threshold validation — pre-deployment requirement:**

The clinical classifier confidence threshold (`CLINICAL_CONTENT_CONFIDENCE_THRESHOLD`, default 0.70) must not be set based on the model's self-reported confidence scores alone. Before deployment:

1. The CMO clinical team labels a holdout set of ≥500 historical claims as `admin` or `clinical`.
2. The classifier is run against the holdout set across a range of threshold values (0.50 to 0.90 in 0.05 increments).
3. The threshold value is set at the lowest value that achieves ≥99.5% recall on the holdout set, prioritising recall over precision (false positives flood the physician queue but are recoverable; false negatives are a compliance event).
4. The calibration result — threshold value, recall, precision, holdout set size, labelling date, CMO reviewer name — is recorded as a signed configuration artefact before go-live. The agent will not load a threshold value that lacks this artefact.

**Post-deployment miscalibration feedback loop:**

If the monthly 5% audit reveals auto-approved claims that a clinical reviewer classifies as containing clinical content:
1. The classifier's threshold is immediately lowered by 0.05 and held pending recalibration.
2. The prior 30 days of auto-approved claims are queued for expedited clinical review.
3. A full recalibration is run against an updated labelled set within 5 business days.
4. CMO sign-off is required before restoring the original threshold.

---

## 4. Activity Catalog

| Task ID | Task name | Task type | Delegation level | Data required | Tool required | Risk level |
|---------|-----------|-----------|-----------------|---------------|---------------|------------|
| T-01 | Claim format parsing and canonical record extraction | Retrieval | Fully agentic | EDI 837 / PDF / portal submission | Rule-based format parser | Low |
| T-02 | Member eligibility verification | Retrieval | Fully agentic | Member ID, plan ID, date of service | Eligibility API (read-only) | Medium |
| T-03 | Eligibility discrepancy resolution | Reasoning | Agent-led + HITL on condition | Eligibility API response, member record, claim date of service | Sonnet 4.6, eligibility API | Medium |
| T-04 | Procedure and diagnosis code validity check | Retrieval + Decision | Fully agentic | ICD-10/CPT codes, code pairing rules table | Code validation table lookup | Low |
| T-05 | Coding plausibility assessment | Reasoning | Agent-led + HITL on condition | Diagnosis codes, procedure codes, provider specialty | Sonnet 4.6, coding reference table | Medium |
| T-06 | Prior authorisation lookup | Retrieval | Fully agentic | Member ID, procedure code, service date | Prior auth API (read-only) | Medium |
| T-07 | Prior auth partial-match resolution | Reasoning + Decision | Agent-led + HITL on condition | Prior auth record, claimed units, authorised units, `PRIOR_AUTH_UNIT_TOLERANCE_PCT` | Sonnet 4.6 + arithmetic | Medium |
| T-08 | Clinical content routing classification | Decision | Agent-led + HITL on condition | Diagnosis codes, procedure codes, provider specialty, `CLINICAL_CONTENT_CONFIDENCE_THRESHOLD` | Sonnet 4.6 | **High** |
| T-09 | Payment calculation | Retrieval + Decision | Fully agentic | Fee schedule, member cost-sharing rules, modifier codes, contract terms | Rate table lookup | Medium |
| T-10 | Contract exception handling | Reasoning | Agent-led + HITL on condition | Contract terms document store, claim data, exception conditions | Sonnet 4.6, contract document store | **High** |
| T-11 | Audit record generation | Generation | Fully agentic | All pipeline step outputs, confidence scores, matched references, timestamps, escalation reason if applicable | Audit logger (append-only) | Medium |
| T-12 | Escalation packet assembly | Generation | Fully agentic | Pipeline outputs to point of escalation, trigger type, specific failure reason, all signal values | Escalation formatter | Medium |

**High-risk task cross-reference:** T-08 → ET-01, ET-02. T-10 → ET-06.

---

## 5. Autonomy Matrix (Decision Authority Matrix)

**AGENT DECIDES ALONE (no HITL required):**
- Auto-approve claims where: clinical content classifier returns `admin` with confidence ≥ `CLINICAL_CONTENT_CONFIDENCE_THRESHOLD`; member eligibility confirmed with no discrepancy; all procedure and diagnosis codes are valid and plausible; prior auth is present and matches claimed units within `PRIOR_AUTH_UNIT_TOLERANCE_PCT`; payment calculation falls within fee schedule with no contract exception.
- Auto-reject claims where: member is ineligible on date of service with no correctable discrepancy; a required procedure code is absent from the fee schedule and no applicable contract exception exists; required prior auth is absent with no matching approval.
- Generate and append audit record to all terminal decisions.
- Route approved claims to payment processing queue.
- Route rejected claims to provider resubmission queue with a specific, machine-readable error code.

**AGENT ACTS, HUMAN NOTIFIED AFTER:**
- Apply prior auth partial-match approval when claimed units differ from authorised units by ≤ `PRIOR_AUTH_UNIT_TOLERANCE_PCT` (default 15%) — logged to audit record; reported in daily operations batch summary to HITL exception team.
- Apply eligibility discrepancy resolution when a discrepancy is deterministically correctable by rule (e.g., transposed date-of-birth digits matching a known correction pattern) — action logged; exception report generated weekly for ops review.

**AGENT PROPOSES, HUMAN APPROVES BEFORE ACTION:**
- **Clinical routing — primary URAC/NCQA governance gate:** Any claim where the clinical content classifier (T-08) returns `clinical` or `uncertain` — at any confidence level — is placed in `pending_physician_review` queue state. The agent assembles an escalation packet containing: classification result, confidence score, all three input signals (diagnosis code, procedure code, provider specialty), full reasoning chain, and complete claim record to that point. A CMO-authorised physician or advanced practice provider must review the packet and record a signed approval token before the claim record transitions to `physician_reviewed` state.
  - **Enforcement mechanism:** System-enforced workflow state transition. The payment calculation step (T-09) reads only from claims in `admin_cleared` state. Claims in `pending_physician_review` state are not readable by T-09. No code path exists for T-09 to execute on a `pending_physician_review` claim. The constraint is not procedure-dependent.
- Exception-queue escalations (eligibility discrepancy beyond rule-correction, coding plausibility below threshold, prior auth mismatch beyond tolerance): agent assembles escalation packet with specific trigger type and all signal values; HITL exception processor reviews and issues a disposition before the claim re-enters or exits the pipeline.

**HUMAN TAKES OVER (agent supports only):**
- Any claim classified as `uncertain` where physician review produces additional questions that cannot be resolved from the existing claim data — the claim enters a `pending_additional_information` state; the agent provides all assembled context but takes no further action.
- Any claim whose submission format cannot be parsed into the canonical record structure (malformed submission with no correctable rule) — the agent returns a specific parse-failure error code; intake correction is a human responsibility.
- Any claim where the contract exception handler (T-10) references a contract clause flagged as outside the pre-deployment validated reference set — the agent suspends the claim with an `unverified_reference` flag; a contract owner resolves the reference question before processing resumes.
- Any claim where the audit record is incomplete at the point of terminal decision — the claim is suspended with an `incomplete_audit` flag; HITL exception processor completes the record before the decision is issued.

---

## 6. Escalation Triggers

| Trigger ID | Condition | Escalate to | What the agent provides at escalation | Response SLA |
|-----------|-----------|-------------|---------------------------------------|-------------|
| ET-01 | Clinical content classifier (T-08) returns `clinical` or `uncertain` at any confidence level | Physician HITL queue (CMO-authorised clinical reviewer) | Classification result (`clinical` / `uncertain`), confidence score, all three input signals (diagnosis code, procedure code, provider specialty), full Sonnet 4.6 reasoning chain, complete claim record to point of escalation | 4 hours (within 7-day SLA window) |
| ET-02 | Clinical content classifier (T-08) returns `admin` but confidence score is below `CLINICAL_CONTENT_CONFIDENCE_THRESHOLD` | Physician HITL queue (CMO-authorised clinical reviewer) | Classification result (`admin`) with confidence value, threshold value at time of classification, all three signal values, reasoning chain, flag indicating borderline confidence | 4 hours |
| ET-03 | Member eligibility check (T-02) returns a discrepancy that cannot be resolved by a deterministic correction rule (member ID not found, active coverage gap on date of service, plan ID mismatch without known alias) | HITL exception processor | Eligibility API response, member ID, claim date of service, specific discrepancy type and error code | 2 hours |
| ET-04 | Prior auth lookup (T-06 / T-07) returns a mismatch where claimed units exceed authorised units by more than `PRIOR_AUTH_UNIT_TOLERANCE_PCT`, or where no prior auth record exists for a procedure requiring one | HITL exception processor | Prior auth record (or absence), claimed units, authorised units, percentage difference, procedure code, `PRIOR_AUTH_UNIT_TOLERANCE_PCT` value at time of escalation | 2 hours |
| ET-05 | Coding plausibility assessment (T-05) produces a Sonnet 4.6 confidence score below the coding plausibility threshold, or flags a procedure-diagnosis pairing as implausible against the coding reference | HITL coding specialist | Procedure codes, diagnosis codes, provider specialty, Sonnet 4.6 output with reasoning chain, relevant code pairing rule reference | 2 hours |
| ET-06 | Contract exception handler (T-10) references a contract clause that is either (a) not present in the pre-deployment validated contract reference set, or (b) flagged as having a known amendment pending validation | HITL exception processor + contract owner | Claim data, referenced contract clause identifier, flag type (`not_in_validated_set` / `pending_amendment`), request for manual resolution | 4 hours |
| ET-07 | Audit record generation (T-11) fails or produces a record with any required field absent (step output, confidence score, matched reference, timestamp, decision rationale) | HITL exception processor | Partial audit record, list of missing fields by field name, claim ID, pipeline step at which failure occurred | 1 hour |

---

## 7. Failure Modes

> **Failure Mode [FM-1]: False negative — clinical claim classified as `admin` and auto-approved without physician review**
> **Consequence:** A claim with genuine clinical content reaches payment determination without physician sign-off. This is a URAC/NCQA compliance event. Downstream: incorrect payment issued to provider; compliance record shows an unapproved clinical determination; the agent is suspended pending investigation regardless of volume or financial impact. Recovery costs include clinical re-review of all auto-approved claims in the affected period.
> **Detection:** Monthly audit of 5% random sample of auto-approved claims by a CMO-authorised clinical reviewer, with results recorded in the audit log. Audited recall is computed monthly; a single confirmed false negative in an audit cohort triggers the full threshold recalibration protocol. Detection latency: up to 30 days post-error if the false negative is not in the audit sample; immediate if flagged by a provider appeal.
> **Recovery path:** (1) Suspend auto-approval for all claims with classifier confidence below 0.85 pending investigation. (2) Expedite clinical review of all auto-approved claims in the prior 30 days. (3) Issue corrected determinations where required. (4) Run full recalibration against an updated labelled set. (5) CMO sign-off required before restoring auto-approval at any threshold.

---

> **Failure Mode [FM-2]: Systematic confidence miscalibration — classifier consistently returns high confidence on borderline claims**
> **Consequence:** The classifier returns confidence ≥ `CLINICAL_CONTENT_CONFIDENCE_THRESHOLD` on claims that are genuinely near the clinical/administrative boundary. The threshold gate fires correctly in the technical sense — no ET-02 escalation is triggered — but the underlying classification is systematically incorrect for a class of borderline claims. This failure mode is invisible to per-claim audit and can persist for weeks before manifesting as a pattern in the monthly audit cohort.
> **Detection:** Monthly audit cohort analysis: if ≥2% of audited auto-approved claims are reclassified as clinical by the auditing reviewer, a miscalibration investigation is triggered regardless of whether any individual claim was flagged at processing time. The audit must include a deliberate over-representation of borderline claim types (procedure codes with high plausibility variance, mixed-specialty provider submissions).
> **Recovery path:** (1) Lower `CLINICAL_CONTENT_CONFIDENCE_THRESHOLD` by 0.05 immediately, routing borderline cases to ET-02 pending recalibration. (2) Pull full prior-period auto-approved claims for clinical review, prioritising claim types matching the miscalibrated pattern. (3) Re-run calibration against an updated holdout set with expanded borderline representation. (4) If the model's confidence outputs are found to be structurally miscalibrated (e.g., consistently returning 0.85+ on all claims regardless of signal ambiguity), escalate to system prompt redesign before restoring any threshold. (5) Document revised threshold and calibration record; CMO sign-off required before go-live restoration.

---

> **Failure Mode [FM-3]: Audit record incompleteness — agent produces a determination the designated approver cannot defend if challenged**
> **Consequence:** A claim is approved or rejected, but the audit record is missing one or more required fields (step output, confidence score, matched code reference, reasoning chain, timestamp, or decision rationale). The HITL reviewer or physician who received the escalation packet has no defensible basis for the determination. If a claim is audited, appealed, or subject to a regulatory review, the absence of a complete audit record constitutes a documentation failure with compliance exposure.
> **Detection:** T-11 (audit record generation) validates the presence of all required fields before writing the record. If any field is absent, T-11 triggers ET-07 and the claim is suspended with an `incomplete_audit` flag. This detection is synchronous — an incomplete audit record cannot exist without triggering ET-07 at the time of generation.
> **Recovery path:** HITL exception processor reconstructs the missing fields from available pipeline step outputs and system logs. If reconstruction is not possible (e.g., the LLM reasoning chain was not captured at execution time), the claim is re-run through the affected pipeline step(s) with audit logging enabled. The determination is not issued until a complete audit record is confirmed. The `incomplete_audit` event is logged as a system quality incident for root cause analysis.
> **Required fields for an audit-defensible record:** claim ID, submission timestamp, each step ID with its input values and output, confidence scores for all LLM calls, matched code references or API response identifiers, the clinical content classifier's three signal values and reasoning chain, the classification result, the decision rationale (approve / reject / escalate with specific trigger), the approved-by field (agent ID or reviewer name and approval token), and the decision timestamp.

---

> **Failure Mode [FM-4]: Prior auth tolerance over-approval — claims with authorised unit counts materially exceeded are auto-approved**
> **Consequence:** The agent applies `PRIOR_AUTH_UNIT_TOLERANCE_PCT` to a claim where the actual unit excess is financially material, approving a payment amount that exceeds the authorised scope. Downstream: over-payment to provider; CFO financial controls flag the discrepancy after payment is issued; recovery requires a provider credit memo or recoupment process.
> **Detection:** Post-payment financial reconciliation compares approved claim amounts against prior auth authorised amounts. Discrepancies above a dollar threshold trigger a flag in the payment processing system. Detection latency: 1–5 business days post-payment. The monthly HITL exception summary also surfaces prior auth partial-match approvals for ops review.
> **Recovery path:** Identify the specific `PRIOR_AUTH_UNIT_TOLERANCE_PCT` value that produced the over-approval. If the approved excess falls within the configured tolerance, the tolerance value is reviewed for appropriateness and potentially tightened. If the approved excess exceeds the tolerance (indicating a calculation error in T-07), the claim is clawed back for re-adjudication. The provider is notified of the corrected determination.

---

> **Failure Mode [FM-5]: Stale reference data — agent validates claims against an outdated fee schedule, code pairing table, or prior auth rule set**
> **Consequence:** Claims are approved or rejected against codes or rates that are no longer current. Downstream: incorrect payment amounts issued (over- or under-payment), or valid claims rejected with incorrect error codes, causing unnecessary provider resubmissions and queue volume.
> **Detection:** The pre-deployment reference validation checklist requires all reference data sources (fee schedule, code pairing table, prior auth rule set) to have a version identifier and an expiry date. At pipeline startup, T-04, T-05, and T-09 verify that all loaded reference data is within its validity window. If any reference source is past its expiry date, the pipeline logs an `expired_reference` warning and routes affected claims to ET-06 (using the `not_in_validated_set` flag type). Detection at startup is synchronous; mid-cycle expiry is detected at the next pipeline execution.
> **Recovery path:** Reference data owner (VP Operations / IT) refreshes the expired reference set and commits a new validated version with an updated expiry date. The agent is restarted against the updated reference set. Claims processed against the stale reference are re-adjudicated if the reference change affects their determination. The reference update is logged as a configuration change event.

---

> **Failure Mode [FM-6]: Malformed or unrecognised claim format producing a silently incomplete canonical record**
> **Consequence:** The format parser (T-01) successfully produces a canonical record but silently omits one or more required fields because the source format is non-standard or corrupted. Downstream pipeline steps receive an incomplete record and produce a determination against missing data — for example, a coding plausibility assessment run on a claim with no provider specialty field, or a clinical classification run without a diagnosis code. The determination is incorrect but the pipeline does not flag the incompleteness.
> **Detection:** T-01 validates the canonical record against a required-fields schema immediately after extraction. Any record with a missing required field triggers a parse-failure rejection with a specific error code returned to the provider. A schema validation step is also run at the entry point of T-08 (clinical classification) as a secondary check, since this step's output is the highest-consequence decision in the pipeline.
> **Recovery path:** The claim is rejected with a specific, actionable error code identifying the missing field. The provider corrects and resubmits. The parse-failure event is logged for volume monitoring — a spike in parse failures from a specific provider or submission format triggers an intake format investigation by the ops team.

---

## 8. Out-of-Scope (Hard Stops)

- **Never issue a payment determination on a claim in `pending_physician_review` state.** The payment calculation step (T-09) is architecturally blocked from executing against this queue state. This constraint cannot be overridden by configuration, by a high classifier confidence score, by claim volume pressure, or by a runtime instruction. Any code path that would allow T-09 to execute on a `pending_physician_review` claim is a critical defect.

- **Never write to, modify, or delete member records, eligibility data, prior auth records, or fee schedule data.** The agent reads these systems via API only. Write access is not granted to any data source. If a discrepancy is identified that appears to require a data correction, the agent escalates with an `eligibility_discrepancy` flag; the correction is made by the data-owning team and the claim is resubmitted.

- **Never deploy or operate with a clinical content confidence threshold that lacks a signed calibration record.** The `CLINICAL_CONTENT_CONFIDENCE_THRESHOLD` value must have a corresponding calibration artefact documenting: the holdout set size, the labelling reviewer, the recall achieved at the deployed threshold, and the CMO sign-off date. The agent must not load a threshold value that lacks this record.

- **Never classify a claim against a reference section — fee schedule, code pairing rule, prior auth criterion, or contract clause — that is not present in the pre-deployment validated reference set or that is flagged as having a pending amendment.** If the required reference is absent or out of date, the agent must trigger ET-06 with an `unverified_reference` flag rather than applying a potentially stale standard.

- **Never send claim data, member data, or payment determinations to any external party** (provider, clearinghouse, downstream payer, analytics platform) directly. The agent writes only to internal queue states and the append-only audit log. All external communications are the responsibility of downstream systems with their own access controls.
