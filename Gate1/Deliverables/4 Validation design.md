# Validation Design
## FNOL Processing Agent — Insurance Claims Automation

---

## 1. Validation strategy overview

Confirming the agent is right requires running structured test scenarios against known ground-truth outcomes — correct claim type, correct severity tier, correct adjuster specialty, correct delegation tier fired — and asserting that every output matches the expected value exactly. That confirms the happy path and known failure modes. Detecting that the agent is wrong when no one notices requires a different mechanism entirely: production monitoring that compares agent decisions against independent ground-truth signals that arrive after the fact. The primary quiet failure detection mechanism is **retrospective outcome comparison**: after a claim is processed, the adjuster's first recorded action (reserve value set, claim type confirmed, legal flag noted) is compared against the agent's original classification and routing decision. Systematic discrepancies between what the agent decided at FNOL intake and what the adjuster found on contact — claim value underestimated, specialty wrong, legal flag missed — are the signal that the agent is consistently wrong in a way that looks correct at processing time. This comparison runs as a nightly batch job against the prior 24 hours of routed claims, with alerts firing when discrepancy rates exceed defined thresholds. Without this retrospective signal, the agent can be completely wrong and every metric will look green.

---

## 2. Test scenarios

---

### Scenario 1: Standard Property Claim — Full Automation Path

```
Scenario 1: Standard property claim, end-to-end automation
Type: Happy Path

Description:
Tests the core automation path for a routine, low-complexity claim. Validates that
a standard property claim arrives, is processed entirely without human intervention,
and reaches COMPLETED within the 2-hour SLA. This is the baseline: if this fails,
nothing else is worth testing.

Preconditions:
- CRM is available and responding (HTTP 200 on health check)
- Policy admin system (mock) is available and returns a valid in-force policy record
- DMS is available
- Adjuster pool contains 3 PROPERTY adjusters with queue depths 1, 3, 6
- No active INTEGRATION_ERROR states in the system
- Email inbox polling is active

Input:
- source_channel: EMAIL
- raw_input: "I need to report a claim. My name is Sarah Chen. Policy number PR-87654321.
  On 12 January 2025 a burst pipe flooded my kitchen. Estimated repair cost from
  the plumber is around £4,500. Please can you process this urgently."
- Mock policy record:
    policy_id: PR-87654321
    policy_status: ACTIVE
    policy_start_date: 2023-06-01
    policy_end_date: 2026-06-01
    covered_perils: [PROPERTY_WATER_DAMAGE, PROPERTY_FIRE, PROPERTY_THEFT]
    exclusions: []
- Mock adjuster pool: [
    {adjuster_id: ADJ-101, specialty: PROPERTY, queue_depth: 1, is_available: true},
    {adjuster_id: ADJ-102, specialty: PROPERTY, queue_depth: 3, is_available: true},
    {adjuster_id: ADJ-103, specialty: PROPERTY, queue_depth: 6, is_available: true}
  ]

Expected agent behaviour (step by step):
1. ClaimRecord created (status = RECEIVED, external_reference = PR-XXXXXXXX,
   sla_deadline = created_at + 7200s)
2. DMS store initiated in parallel (document stored within 10s)
3. AcknowledgementRecord (RECEIPT) created and email sent to claimant within 300s of created_at;
   content includes external_reference and 2-hour SLA statement; no coverage language
4. Claim transitions RECEIVED → PARSING
5. NLP extraction: policy_id = PR-87654321, loss_date = 2025-01-12, claim_type_candidate = PROPERTY,
   estimated_loss_value = 4500, parse_confidence = 0.91 (above 0.70 threshold)
6. Claim transitions PARSING → PARSED
7. Claim transitions PARSED → TRIAGING
8. Classification: claim_type = PROPERTY, classification_confidence = 0.93 (above 0.85)
9. Severity scoring: severity_score = 38 (loss_value £4,500 < £10,000 AND no CRITICAL_EVENT
   flags); severity = LOW
10. Special handling flag scan: no fatality, legal, fraud, or vulnerable signals detected;
    special_handling_flags = []
11. Claim transitions TRIAGING → TRIAGED (no EscalationBriefing created)
12. Claim transitions TRIAGED → VALIDATING
13. Policy retrieval from mock: IN_FORCE, policy_start_date ≤ loss_date ≤ policy_end_date
14. Coverage match: PROPERTY_WATER_DAMAGE matches classified claim_type PROPERTY;
    coverage_match_confidence = 0.93 (above 0.85); exclusion_candidates = []
15. Claim transitions VALIDATING → COVERAGE_CONFIRMED (AGENT_LOG; no EscalationBriefing)
16. Claim transitions COVERAGE_CONFIRMED → ROUTING
17. Adjuster selection: specialty_required = PROPERTY; candidates = [ADJ-101(depth 1),
    ADJ-102(depth 3), ADJ-103(depth 6)]; selected = ADJ-101 (lowest queue_depth)
18. ClaimAssignment created: adjuster_id = ADJ-101, assignment_method = AGENT_ALGORITHM
19. CRM PATCH: Claim.status = ROUTED
20. Adjuster notification sent to ADJ-101 via CRM within 60s of assignment
21. AcknowledgementRecord (ROUTING_CONFIRMATION) created; email sent to claimant with
    adjuster name, contact details, and expected contact timeframe
22. Claim transitions ROUTED → ACKNOWLEDGED → COMPLETED
23. Total elapsed time from created_at to COMPLETED: < 180s (3 minutes)

Expected output:
- Claim.status = COMPLETED
- Claim.claim_type = PROPERTY
- Claim.severity = LOW
- Claim.coverage_status = COVERED
- Claim.sla_breached = false
- ClaimAssignment.adjuster_id = ADJ-101
- ClaimAssignment.assignment_method = AGENT_ALGORITHM
- AcknowledgementRecord count for this claim = 2 (RECEIPT + ROUTING_CONFIRMATION)
- AcknowledgementRecord[RECEIPT].sent_at ≤ Claim.created_at + 300s
- EscalationBriefing count for this claim = 0
- Audit log entry count ≥ 10 (one per named action in steps above)
- DMS document stored = 1

Pass criterion:
  Claim.status = COMPLETED
  AND ClaimAssignment.adjuster_specialty = PROPERTY
  AND AcknowledgementRecord[RECEIPT].sent_at ≤ Claim.created_at + 300s
  AND EscalationBriefing.count = 0
  AND total_elapsed_seconds < 180
  AND Claim.sla_breached = false

Fail criterion:
  Claim.status ≠ COMPLETED after 300s
  OR ClaimAssignment.adjuster_specialty ≠ PROPERTY
  OR AcknowledgementRecord[RECEIPT].sent_at > Claim.created_at + 300s
  OR EscalationBriefing.count > 0
  OR Claim.sla_breached = true

Quiet failure risk:
The agent selects adjuster ADJ-101 (PROPERTY specialty, queue depth 1) correctly.
But if the specialty mapping table has a data error and PROPERTY maps to GENERAL,
the agent assigns a GENERAL adjuster, the claim reaches COMPLETED, and all metrics
look correct. The claimant is acknowledged, the adjuster is notified — the error
only surfaces when the GENERAL adjuster contacts the claimant and lacks the
specialist knowledge to handle a water damage claim.

Detection mechanism: Nightly batch job compares ClaimAssignment.adjuster_specialty
against specialty_map[Claim.claim_type] for all claims assigned in the prior 24h.
Alert fires if specialty mismatch count > 5% of routed claims (15 claims on a 300/day
volume). This is independent of whether the claim reached COMPLETED.
```

---

### Scenario 2: Severity Threshold Boundary — Low/Medium vs High/Critical

```
Scenario 2: Severity threshold boundary — sub-case A (below) and sub-case B (above)
Type: Delegation Boundary

Description:
Tests that the severity threshold (severity_score = 60, corresponding to claim_value
≈ £10,000) fires the correct delegation tier on both sides of the boundary. Sub-case A
(score = 59) must produce AGENT_LOG with no escalation. Sub-case B (score = 61) must
produce AGENT_REVIEW with an EscalationBriefing. Both claims are otherwise identical.
This tests the boundary established in D2 tier 1.3/1.4 and the threshold flagged as
[TODO: D5-U1]. If the boundary is off by even one point, one class of high-value
claims will be silently under-escalated.

Preconditions:
- CRM available; policy admin mock available; same mock policy record for both sub-cases
- Mock policy: policy_id = MO-11223344, status = ACTIVE, covered_perils = [MOTOR_COLLISION]
- Adjuster pool: 2 MOTOR adjusters available, queue depths 2 and 4
- Severity scoring model configured with £10,000 threshold and score boundary at 60

--- Sub-case A: score below threshold ---

Input:
- source_channel: WEB_FORM
- policy_id: MO-11223344
- loss_date: 2025-02-03
- claim_type_candidate: MOTOR
- estimated_loss_value: £9,800
- loss_description: "Rear-end collision, significant boot and bumper damage"
- special_handling_flags candidate: none
- Severity model output for this input: severity_score = 59

Expected agent behaviour:
1. Parse and extract: parse_confidence = 0.94
2. Classify: claim_type = MOTOR, classification_confidence = 0.91
3. Severity: severity_score = 59; severity = MEDIUM (59 < 60 threshold)
4. Delegation tier 1.3 fires: AGENT_LOG
5. Claim transitions TRIAGING → TRIAGED
6. No EscalationBriefing created at triage stage

Expected output (Sub-case A):
- Claim.severity = MEDIUM
- Claim.status transitions through to TRIAGED without TRIAGE_PENDING_REVIEW
- EscalationBriefing.count at triage stage = 0
- Audit log contains entry: action_type = SEVERITY_ASSESSED, severity = MEDIUM,
  severity_score = 59, delegation_tier = AGENT_LOG

Pass criterion (Sub-case A):
  Claim.status = TRIAGED (not TRIAGE_PENDING_REVIEW)
  AND Claim.severity = MEDIUM
  AND EscalationBriefing.count = 0 at triage stage
  AND audit log entry severity_score = 59 AND delegation_tier = AGENT_LOG

Fail criterion (Sub-case A):
  Claim.status = TRIAGE_PENDING_REVIEW
  OR EscalationBriefing created at triage stage
  OR Claim.severity ∈ {HIGH, CRITICAL}

--- Sub-case B: score above threshold ---

Input:
- All fields identical to Sub-case A except:
- estimated_loss_value: £10,200
- Severity model output for this input: severity_score = 61

Expected agent behaviour:
1. Parse and extract: parse_confidence = 0.94
2. Classify: claim_type = MOTOR, classification_confidence = 0.91
3. Severity: severity_score = 61; severity = HIGH (61 ≥ 60 threshold)
4. Delegation tier 1.4 fires: AGENT_REVIEW
5. Claim transitions TRIAGING → TRIAGE_PENDING_REVIEW
6. EscalationBriefing created: escalation_reason = HIGH_SEVERITY,
   review_window_deadline = created_at + 1800s (30 min)
7. Specialist notified via CRM review queue within 30s

Expected output (Sub-case B):
- Claim.severity = HIGH
- Claim.status = TRIAGE_PENDING_REVIEW
- EscalationBriefing.count = 1 at triage stage
- EscalationBriefing.escalation_reason = HIGH_SEVERITY
- EscalationBriefing.review_window_deadline = claim.created_at + 1800s
- CRM review queue entry visible within 30s

Pass criterion (Sub-case B):
  Claim.status = TRIAGE_PENDING_REVIEW
  AND Claim.severity = HIGH
  AND EscalationBriefing.count = 1
  AND EscalationBriefing.review_window_deadline = claim.created_at + 1800s
  AND CRM review queue entry created within 30s

Fail criterion (Sub-case B):
  Claim.status = TRIAGED (bypassed TRIAGE_PENDING_REVIEW)
  OR EscalationBriefing.count = 0
  OR Claim.severity ∈ {LOW, MEDIUM}

Quiet failure risk:
The boundary test confirms the threshold fires correctly when the estimated_loss_value
is extracted accurately. The quiet failure is when the NLP extraction reads £10,200 as
£1,020 (misplaced decimal or comma parsing error). The agent scores severity_score = 32
(LOW), bypasses AGENT_REVIEW, and routes the £10,200 claim as a LOW-priority case.
The claim reaches COMPLETED. No specialist ever sees it at triage.

Detection mechanism: Nightly batch comparison of Claim.estimated_loss_value (extracted
at FNOL) against ClaimAssignment adjuster's first recorded reserve value in CRM.
Alert fires if extracted_value < 0.5 × adjuster_reserve_value for more than 3 claims
per day (indicating systematic extraction underestimation). This catches the pattern
before it compounds.
```

---

### Scenario 3: Ambiguous Coverage with Exclusion Candidate

```
Scenario 3: Coverage confidence in AGENT_REVIEW band with exclusion candidate present
Type: Edge Case

Description:
Tests the coverage validation path when the agent identifies a coverage match but
with low-to-medium confidence AND an exclusion candidate. Both conditions independently
trigger AGENT_REVIEW (D2 tier 2.4 and 2.5). This scenario verifies that either condition
alone is sufficient to trigger the review, and that the EscalationBriefing correctly
surfaces both the confidence score and the exclusion clause reference for the specialist.
A common failure mode is that exclusion detection fires correctly but the briefing note
omits the policy clause text — the specialist then confirms without actually reading
the clause.

Preconditions:
- Policy admin mock configured to return a policy with one candidate exclusion
- Mock policy:
    policy_id: PR-99887766
    policy_status: ACTIVE
    covered_perils: [PROPERTY_WATER_DAMAGE, PROPERTY_ACCIDENTAL_DAMAGE]
    exclusions: ["Clause 14.3: Damage arising from gradual deterioration or wear and tear"]
- Adjuster pool: 2 PROPERTY adjusters available
- Coverage model configured to return coverage_match_confidence = 0.72 for this
  claim/policy combination (in the 0.70–0.84 AGENT_REVIEW band)
- Exclusion detection model configured to flag Clause 14.3 with exclusion_confidence = 0.78

Input:
- source_channel: PHONE_TRANSCRIPT
- raw_input: "Transcript ref 20250220-4421. Claimant: David Okafor. Policy PR-99887766.
  Reporting damp and water staining on the living room ceiling. Has been there a while,
  noticed it getting worse over the past few months. Thinks it might be a slow leak from
  the bathroom above. Estimated repair cost approximately £3,800."
- loss_date: 2025-02-20
- estimated_loss_value: £3,800

Expected agent behaviour:
1. Parse: parse_confidence = 0.88; extracted claim_type_candidate = PROPERTY,
   loss_description = "gradual water ingress / ceiling damp from suspected slow leak"
2. Classify: claim_type = PROPERTY, classification_confidence = 0.89
3. Severity: severity_score = 36 (£3,800 < £10,000, no CRITICAL_EVENT); severity = LOW
4. Flag scan: no fatality, legal, fraud, or vulnerable signals; special_handling_flags = []
5. Transition TRIAGING → TRIAGED
6. Policy retrieval: IN_FORCE, policy_start_date ≤ loss_date ≤ policy_end_date
7. Coverage matching: coverage_match_confidence = 0.72 (in 0.70–0.84 band → AGENT_REVIEW)
8. Exclusion scan: Clause 14.3 identified as candidate exclusion;
   exclusion_confidence = 0.78; exclusion_candidates = ["Clause 14.3"]
9. Either condition alone triggers AGENT_REVIEW; both conditions present — single
   EscalationBriefing created with both signals surfaced
10. Claim transitions VALIDATING → COVERAGE_PENDING_REVIEW
11. EscalationBriefing created: escalation_reason = AMBIGUOUS_COVERAGE,
    escalation_detail includes: coverage_match_confidence = 0.72,
    exclusion_candidates = ["Clause 14.3: Damage arising from gradual deterioration
    or wear and tear"], full policy_snapshot, full claim_snapshot
12. Review window: review_window_deadline = created_at + 1800s
13. Specialist presented with: agent's coverage determination, policy clause text
    (Clause 14.3 verbatim), and claim narrative

Expected output:
- Claim.status = COVERAGE_PENDING_REVIEW
- Claim.coverage_match_confidence = 0.72
- Claim.exclusion_candidates = ["Clause 14.3"]
- EscalationBriefing.count = 1
- EscalationBriefing.escalation_detail contains policy_snapshot with Clause 14.3 text
- EscalationBriefing.escalation_detail contains coverage_match_confidence = 0.72
- EscalationBriefing.review_window_deadline = created_at + 1800s
- AcknowledgementRecord[RECEIPT] sent within 300s (fires independently of coverage state)
- No AcknowledgementRecord[ROUTING_CONFIRMATION] yet (routing not yet determined)

Pass criterion:
  Claim.status = COVERAGE_PENDING_REVIEW
  AND EscalationBriefing.count = 1
  AND EscalationBriefing.escalation_detail CONTAINS coverage_match_confidence = 0.72
  AND EscalationBriefing.escalation_detail CONTAINS "Clause 14.3"
  AND AcknowledgementRecord[RECEIPT].sent_at ≤ Claim.created_at + 300s
  AND AcknowledgementRecord[ROUTING_CONFIRMATION].count = 0

Fail criterion:
  Claim.status = COVERAGE_CONFIRMED (bypassed AGENT_REVIEW — agent over-confident)
  OR EscalationBriefing.escalation_detail DOES NOT CONTAIN exclusion clause text
    (specialist briefed without the evidence needed to make a decision)
  OR AcknowledgementRecord[RECEIPT] NOT sent within 300s
    (SLA-critical ACK blocked by coverage review state — must not happen)

Quiet failure risk:
The agent correctly triggers AGENT_REVIEW but the EscalationBriefing omits the
policy_snapshot or renders it as a raw policy_id reference rather than the actual
clause text. The specialist sees "exclusion candidate: Clause 14.3" but not the
clause wording. They confirm coverage without reading the clause. A "gradual
deterioration" exclusion that should have denied coverage is rubber-stamped.

Detection mechanism: Structured audit of EscalationBriefing records where
resolution = CONFIRMED and exclusion_candidates ≠ []. Sample 100% of these cases
for the first 30 days post-go-live; specialist confirms they reviewed clause text,
not just the reference. Long-term: if adjuster-recorded coverage dispute rate for
claims with exclusion candidates > 15%, trigger briefing content audit.
```

---

### Scenario 4: Policy Administration System Unavailable Mid-Processing

```
Scenario 4: SOAP policy admin system unavailable — all retries exhausted
Type: Failure Mode

Description:
Tests the INTEGRATION_ERROR path when the legacy policy administration system is
unavailable during coverage validation. This is the most likely production failure
given the system is described as "legacy." The critical assertions are: (1) the
receipt ACK was already sent before policy retrieval — it must not be withheld, (2)
the claim halts correctly at VALIDATING without proceeding to routing, (3) the
specialist is notified within 5 minutes, and (4) processing resumes correctly after
the system recovers. This scenario also tests that DMS storage is non-blocking —
a DMS failure at the same time must not compound the error.

Preconditions:
- CRM available
- Policy admin system mock configured to return HTTP 503 on all requests for this test run
- DMS available
- Adjuster pool available (not needed — routing should not be reached)
- Receipt ACK was queued successfully at claim receipt (pre-condition: email service available)

Input:
- source_channel: EMAIL
- raw_input: "Claim notification. Policy LI-55443322. Date of incident 15 March 2025.
  Liability claim — I was involved in a dispute with a neighbour causing property damage.
  Estimated damage £6,200."
- loss_date: 2025-03-15
- estimated_loss_value: £6,200
- Mock policy admin: configured to return HTTP 503 (Service Unavailable) on all requests
  for policy_id LI-55443322; all 3 retries (2s/4s/8s backoff) return 503

Expected agent behaviour:
1. ClaimRecord created (status = RECEIVED)
2. DMS store initiated
3. AcknowledgementRecord (RECEIPT) created and sent within 300s — fires before policy
   retrieval; must not be affected by SOAP failure
4. Parse: parse_confidence = 0.87; claim_type_candidate = LIABILITY
5. Classify: LIABILITY, confidence = 0.88
6. Severity: severity_score = 42; severity = MEDIUM; no flags
7. Transition TRIAGING → TRIAGED
8. Transition TRIAGED → VALIDATING
9. Policy retrieval attempt 1: HTTP 503 → wait 2s
10. Policy retrieval attempt 2: HTTP 503 → wait 4s
11. Policy retrieval attempt 3: HTTP 503 → wait 8s
12. All retries exhausted (total elapsed for retry cycle: 14s)
13. Claim transitions VALIDATING → INTEGRATION_ERROR
14. EscalationBriefing created: escalation_reason = INTEGRATION_ERROR,
    escalation_detail = "Policy admin system unavailable; 3 retries exhausted;
    policy_id = LI-55443322"
15. Specialist notified via CRM review queue within 5 minutes of INTEGRATION_ERROR
16. Processing halted — claim does NOT transition to COVERAGE_CONFIRMED or ROUTING
17. [Recovery] Specialist resolves issue; triggers manual policy lookup in CRM
18. Agent receives manual policy record; transitions INTEGRATION_ERROR → VALIDATING
19. Coverage validation proceeds with manually provided policy record
20. Claim continues to COMPLETED (assuming policy is in-force and coverage confirmed)

Expected output:
- Claim.status = INTEGRATION_ERROR (before recovery)
- AcknowledgementRecord[RECEIPT].sent_at ≤ Claim.created_at + 300s (unaffected by failure)
- EscalationBriefing.escalation_reason = INTEGRATION_ERROR
- EscalationBriefing created within 30s of INTEGRATION_ERROR transition
- Specialist notification visible in CRM review queue within 300s of INTEGRATION_ERROR
- No ClaimAssignment record exists (routing not attempted)
- No AcknowledgementRecord[ROUTING_CONFIRMATION] (not sent)
- Audit log entry: action_type = ERROR_LOGGED, error_type = INTEGRATION_ERROR,
  retry_count = 3, error_detail contains "HTTP 503"

Pass criterion:
  Claim.status = INTEGRATION_ERROR after retry exhaustion
  AND AcknowledgementRecord[RECEIPT].sent_at ≤ Claim.created_at + 300s
  AND ClaimAssignment.count = 0
  AND EscalationBriefing.escalation_reason = INTEGRATION_ERROR
  AND specialist CRM notification created within 300s of INTEGRATION_ERROR
  AND audit log retry_count = 3

Fail criterion:
  Claim.status = COVERAGE_CONFIRMED or ROUTED (processing continued past INTEGRATION_ERROR)
  OR AcknowledgementRecord[RECEIPT] NOT sent within 300s
  OR EscalationBriefing.count = 0
  OR specialist notification NOT created within 300s

Quiet failure risk:
After INTEGRATION_ERROR, the specialist manually enters the policy record via CRM.
If the specialist enters policy_status = IN_FORCE when the policy is actually LAPSED
(misread policy number, wrong policy retrieved), the agent validates coverage against
the wrong record. The claim proceeds to ROUTING and COMPLETED. The error is only
discovered when the adjuster contacts the claimant and the claimant has no valid
policy. At that point, a coverage decision has been implicitly communicated.

Detection mechanism: For all claims where ClaimAuditLog contains retrieval_method =
MANUAL, flag for mandatory specialist supervisor sign-off before the claim can
transition from INTEGRATION_ERROR back to VALIDATING. Alternatively: once the policy
admin system recovers, automated reconciliation of all manually-entered policy records
against the live system; alert if any discrepancy found. Either mechanism must run
before the 2-hour SLA window closes.
```

---

### Scenario 5: Under-Escalation at the Delegation Boundary — Extraction Value Error Causing Silent Severity Downgrade

```
Scenario 5: NLP extraction misreads claim value; HIGH claim processed as LOW
Type: Failure Mode / Delegation Boundary

Description:
Tests the most dangerous quiet failure mode for this agent: the NLP extraction
produces an estimated_loss_value that is significantly lower than the true value,
causing the severity scoring model to produce LOW instead of HIGH. The claim bypasses
AGENT_REVIEW entirely. It reaches COMPLETED. No specialist ever reviews it at triage.
The adjuster only discovers the true value when contacting the claimant. This is a
failure at the delegation boundary (the HIGH/CRITICAL threshold) that is undetectable
by the standard happy-path test suite, because from the pipeline's perspective
everything worked correctly — the agent processed the claim end-to-end as designed
for a LOW claim.

Preconditions:
- CRM, policy admin mock, DMS all available
- Mock policy: policy_id = MO-66554433, ACTIVE, covered_perils = [MOTOR_COLLISION]
- NLP extraction model in this test is configured to misparse "£14,000" as "£1,400"
  (simulating a comma/period locale parsing error: "14,000" read as "1.400" → £1,400)
- Adjuster pool: 2 MOTOR adjusters available

Input:
- source_channel: EMAIL
- raw_input: "Dear claims team, I'm writing about a serious collision on 4 April 2025.
  Policy ref MO-66554433. My car was written off — the repair estimate from the garage
  is £14,000 which is more than the car is worth. I also had to hire a replacement
  vehicle at £350. Please advise urgently."
- loss_date: 2025-04-04
- True estimated_loss_value in input: £14,000
- Extraction model output (defective): estimated_loss_value = £1,400

Expected agent behaviour (with extraction defect active):
1. Parse: parse_confidence = 0.89; extracted estimated_loss_value = £1,400 (WRONG)
2. Classify: claim_type = MOTOR, classification_confidence = 0.92
3. Severity scoring: severity_score = 14 (based on £1,400, well below £10,000 threshold)
4. Severity = LOW
5. Tier 1.3 fires: AGENT_LOG (no AGENT_REVIEW triggered — this is the failure)
6. Claim transitions TRIAGING → TRIAGED (no EscalationBriefing)
7. Coverage match: MOTOR_COLLISION covered; confidence = 0.91; no exclusions
8. Transition → COVERAGE_CONFIRMED
9. Routing: MOTOR adjuster selected (ADJ-201, queue depth 1)
10. Claim reaches COMPLETED
11. AcknowledgementRecord[RECEIPT] and [ROUTING_CONFIRMATION] both sent
12. Claim appears successful in all dashboard metrics

Expected output (with defect — this is what the agent DOES, not what it should do):
- Claim.status = COMPLETED
- Claim.severity = LOW
- Claim.estimated_loss_value = £1,400 (wrong)
- EscalationBriefing.count = 0
- All SLA metrics green
- No human specialist ever reviewed the triage decision

Pass criterion for this scenario (tests that the DETECTION mechanism fires):
  Nightly batch job runs comparing Claim.estimated_loss_value against
  ClaimAssignment adjuster's first recorded reserve value for this claim
  AND adjuster records reserve = £14,000 (or similar) within 48h of assignment
  AND discrepancy alert fires: extracted_value (£1,400) < 0.5 × adjuster_reserve (£14,000)
  AND alert is delivered to operations team

Fail criterion:
  Nightly batch comparison does NOT run for this claim
  OR adjuster reserve is recorded but discrepancy threshold check does not fire
  OR alert fires but is delivered to an unmonitored queue (alert acknowledged = false
     within 24h of firing)

Quiet failure risk:
This scenario IS the quiet failure. The detection mechanism (retrospective comparison
of extracted value against adjuster reserve) is the only signal. If the adjuster does
not set a reserve value within 48h of assignment (e.g., claim is sitting in their
queue unactioned), the discrepancy is never detected.

Detection mechanism (two layers):
Primary: Nightly batch — compare Claim.estimated_loss_value against adjuster reserve
  for all claims closed or updated in prior 24h; alert if extracted < 0.5 × reserve
  for > 3 claims/day.
Secondary: For any MOTOR or PROPERTY claim where Claim.estimated_loss_value < £2,000
  but adjuster does not set a reserve within 72h of assignment, flag for
  supervisor review — unactioned low-value claims assigned to motor specialists are
  a red flag for misclassified high-value claims.
```

---

## 3. Delegation boundary test

Scenario 2 above is the explicit delegation boundary test (`Type: Delegation Boundary`). It covers:

- **The boundary tested:** severity_score threshold between AGENT_LOG (score ≤ 59) and AGENT_REVIEW (score ≥ 60), which maps to the D2 tier 1.3 / 1.4 split
- **Sub-case A** (score = 59): must produce TRIAGED with no EscalationBriefing — confirms AGENT_LOG fires correctly below the threshold
- **Sub-case B** (score = 61): must produce TRIAGE_PENDING_REVIEW with EscalationBriefing — confirms AGENT_REVIEW fires correctly above the threshold
- **Why this boundary matters:** if the threshold is off by one point in the wrong direction, every claim in the £9,000–£11,000 range is either over-escalated (defeating the automation ROI) or under-escalated (high-value claims processed without specialist review)

Scenario 5 also tests a delegation boundary failure — specifically the case where the boundary threshold fires on corrupted input data, not on the correct input value. This is distinct from Scenario 2: Scenario 2 tests whether the threshold fires at the right value; Scenario 5 tests whether the threshold can be silently defeated by an upstream extraction error.

---

## 4. Quiet failure detection design

| Quiet failure mode | Why it would not be caught by standard tests | Detection mechanism |
|---|---|---|
| Agent routes claim to wrong adjuster specialty (e.g. PROPERTY claim assigned to GENERAL adjuster) | Standard tests confirm the claim reaches COMPLETED and the claimant is acknowledged. Routing accuracy is not verified post-assignment in the happy-path test. The COMPLETED state looks identical whether the specialty is correct or wrong. | Nightly batch: compare ClaimAssignment.adjuster_specialty against specialty_map[Claim.claim_type] for all claims assigned in the prior 24h. Alert fires if mismatch count > 5% of routed claims (threshold: 15 mismatches on a 300-claim day). Alert delivered to operations team via CRM. |
| NLP extraction systematically underestimates claim value for a specific input format (e.g. comma-formatted numbers: "14,000" parsed as "1,400") | Standard tests use manually crafted inputs with unambiguous value formats. Production inputs arrive from real claimants whose formatting varies by locale, channel, and literacy. A parsing defect on comma-formatted numbers would affect all such claims silently — each reaches COMPLETED with green metrics. | Nightly batch: compare Claim.estimated_loss_value (extracted at FNOL) against adjuster's first recorded reserve value for the same claim. Alert fires if extracted_value < 0.5 × adjuster_reserve for > 3 claims in any 24h window. This requires the CRM to expose the adjuster reserve field; flagged as dependency in D5. |
| Coverage confidence inflation — agent assigns coverage_match_confidence = 0.88 to a genuinely ambiguous claim, bypassing AGENT_REVIEW | Standard tests set coverage_match_confidence in the test fixture. In production, the confidence model runs on real policy language it may not have been trained on. A model that is systematically overconfident on certain policy clause types will never trigger AGENT_REVIEW, and all claims in that clause category will be auto-confirmed. The metric "coverage validation confidence distribution" looks healthy because high scores are recorded. | Track post-routing coverage dispute rate: % of COVERAGE_CONFIRMED (AGENT_LOG) claims where the adjuster subsequently records a coverage dispute or refers back to claims manager within 30 days of assignment. Alert fires if this rate exceeds 8% of AGENT_LOG coverage decisions over a rolling 30-day window. This retrospective signal catches systematic overconfidence that confidence score monitoring alone cannot detect. |
| Special handling flag missed for indirect or non-standard phrasing (e.g. "my wife's solicitor suggested I call" — LEGAL_REPRESENTATION not triggered by keyword match) | Standard tests inject claims with exact keyword matches from the defined keyword set. Production claimants paraphrase, hedge, and reference legal representation indirectly. A keyword-based detector has a hard boundary: if the phrase does not match the list, no flag. Tests only cover the listed keywords. | Monthly reconciliation: compare FNOL LEGAL_REPRESENTATION flag rate against rate at which adjusters subsequently record "claimant represented by solicitor" in CRM notes. Alert fires if adjuster-reported legal representation rate exceeds FNOL-detected rate by more than 3 percentage points over a rolling 30-day window. This gap is the false negative rate for the flag detector. |
| SLA breach prevention alert fires correctly but is delivered to an unmonitored queue or inbox | Standard tests confirm the SLA warning alert is sent (REQ-10 pass criterion). They do not test whether anyone receives or acts on it. If the alert destination (operations team CRM queue or email) is unmonitored outside business hours, 100% of out-of-hours at-risk claims breach SLA silently with green alert-sent metrics. | Monitor alert acknowledgement: for every SLA breach-prevention alert sent, check for acknowledgement (CRM queue "viewed" event or email open) within 15 minutes. If no acknowledgement within 15 minutes, escalate to secondary contact (on-call mobile number [TODO: D5-U9 — contact list not defined]). Track unacknowledged alert rate; alert fires if > 2 unacknowledged SLA warnings in any 24h window. |

---

## 5. Metrics to watch in production

| Metric | Measurement method | Alert threshold | Action if breached |
|---|---|---|---|
| Agent routing accuracy | Nightly batch: ClaimAssignment.adjuster_specialty vs specialty_map[Claim.claim_type] for all claims routed in prior 24h. Accuracy = matched / total routed. | < 95% accuracy (> 15 mismatches on 300-claim day) | Pause agent routing immediately; all routing switches to AGENT_SUPPORT (manual); investigate specialty mapping table and claim_type classification accuracy; resume only after root cause confirmed |
| SLA compliance rate | Daily: % of claims where AcknowledgementRecord[RECEIPT].sent_at ≤ Claim.sla_deadline for all claims closed on that calendar day. | < 90% on any calendar day (> 30 SLA breaches on 300-claim day) | Operations review same day; examine INTEGRATION_ERROR count, COVERAGE_DISPUTED backlog, and QUEUE_OVERFLOW duration for that day; report to client within 24h |
| Escalation rate (two-sided) | Daily: % of claims where EscalationBriefing.count ≥ 1, measured across all claims ingested that day. | < 10%: under-escalating (fewer than 30 escalations on 300-claim day). > 40%: over-escalating (more than 120 escalations) | < 10%: review confidence thresholds; sample 20 AGENT_LOG decisions for spot-check; risk of silent under-escalation. > 40%: review threshold calibration; check for model drift or input format changes; automation ROI at risk |
| Coverage validation confidence distribution | Daily: median and p10 of coverage_match_confidence across all claims that reached VALIDATING that day. | Median drops below 0.78 (from expected ~0.90) OR p10 drops below 0.60 | Investigate policy data quality; check if new policy types or clause formats were introduced; consider temporary lowering of AGENT_LOG threshold to 0.88 until cause identified |
| False negative escalation rate | Weekly: % of AGENT_LOG decisions (severity LOW/MEDIUM, no escalation) that were subsequently corrected by a specialist (claim_type changed OR severity upgraded OR coverage_status changed from COVERED). Measured from CRM audit trail. | > 5% of AGENT_LOG decisions corrected per week (> 105 corrections on 2,100 weekly AGENT_LOG decisions at 300/day) | Review scoring model accuracy; inspect corrected claims for patterns (specific claim types, channels, or value ranges over-represented); recalibrate confidence thresholds or severity model; do not accept > 5% correction rate as steady-state |
| Receipt ACK timeliness | Continuous: for every ClaimRecord, check AcknowledgementRecord[RECEIPT].sent_at ≤ Claim.created_at + 300s. Report as daily % in-time. | < 98% (> 6 ACKs late on 300-claim day) | Investigate email delivery pipeline; check CRM SEND_EMAIL operation latency; if systemic, switch to direct SMTP fallback for ACK send |
| Adjuster reassignment rate | Weekly: % of ClaimAssignments where superseded_at is set within 24h of created_at. | > 10% (> 210 reassignments/week on 2,100 weekly assignments) | Review specialty mapping accuracy; check adjuster availability data freshness in CRM; high reassignment rate indicates routing decisions based on stale adjuster pool data |
| Post-routing coverage dispute rate | Monthly rolling 30-day: % of COVERAGE_CONFIRMED (AGENT_LOG) claims where adjuster subsequently records coverage dispute in CRM within 30 days. | > 8% of AGENT_LOG coverage confirmations disputed | Investigate coverage confidence model; audit EscalationBriefing records for the disputed claims to identify what confidence score was assigned; likely indicates systematic model overconfidence on a specific coverage type |
