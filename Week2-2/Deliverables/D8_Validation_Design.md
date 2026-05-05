# D8 — Validation Design
**Agent:** Clause Classification Agent (CCA)
**Scenario:** Helix Workforce Software — Vendor Contract Clause Review

---

## 1. Validation Philosophy

The CCA is correct when two conditions hold simultaneously: its clause classifications match what Tom or a senior lawyer would have decided, and every case where governance rules applied or confidence was uncertain was escalated rather than processed autonomously. Confirming it is right requires measuring Tom's override rate on HITL-reviewed ClauseReview records (logged in the Ironclad `human_override` field per ClauseReview) and running a quarterly random audit in which Tom reviews 10% of autonomously-routed STANDARD contracts — target ≤ 10% override rate on audited cases. Detecting that it is wrong requires a different set of checks: a weekly automated comparison of the confidence score distribution per clause type against the prior 4-week baseline (a shift signals model behaviour change or input population change); Tom's per-clause-type override rate tracked quarterly as a calibration signal (overrides concentrated on one clause type signal systematic misclassification); and a mandatory post-quarter random audit of the 10% of cases that did NOT trigger HITL, reviewed by Tom within 5 working days of quarter end and logged in Ironclad. The last check is the only one that catches confident-but-wrong autonomous routing — the failure mode that produces no exception, no queue item, and no immediate human review.

---

## 2. Test Scenarios

---

### S-1 — All-compliant no-DPA contract routes to STANDARD without Tom review

| Field | Content |
|-------|---------|
| **Type** | Happy path |
| **Delegation boundary tested** | C-1 + C-2 assigned Agent-led + Human Oversight (D2). The claim: when all 7 clause types are assessed, all COMPLIANT, all confidence ≥ 0.85, and no DPA clause is present, the agent routes STANDARD and writes to Ironclad without requiring Tom's approval. Tom is notified but takes no action. |
| **Input** | Vendor: SimpleIT Ltd. 18-page IT services agreement. Clause outputs from T-04/T-05: LIABILITY_CAP: "Vendor liability capped at £300,000 or 12 months fees, whichever greater" — £300,000 > playbook floor of £250,000 → COMPLIANT, confidence 0.92. TERMINATION_CLAUSE: "30 days written notice for convenience" — matches playbook 30-day position → COMPLIANT, confidence 0.91. IP_OWNERSHIP: "All deliverables IP vests in Helix on creation" → COMPLIANT, confidence 0.93. SLA_COMMITMENTS: "99.5% uptime; 4-hour critical P1 response" — meets playbook minimums → COMPLIANT, confidence 0.90. GOVERNING_LAW: "English law; English courts exclusive jurisdiction" → COMPLIANT, confidence 0.95. INDEMNITY_SCOPE: "Vendor indemnifies Helix against third-party IP infringement from vendor deliverables" → COMPLIANT, confidence 0.88. DATA_PROCESSING_AGREEMENT: not located in document — no "data processing", "GDPR", "personal data" headings or keywords found anywhere; absence confidence 0.92. ET-3 does not fire (0.92 ≥ 0.85 threshold). |
| **Expected agent behaviour** | T-01: email received, attachment extracted. T-02: Ironclad case created (IRONCLAD-{n}), contract.status = PENDING_REVIEW. T-03: document parsed, 18 pages — within 15–40 range, no anomaly flag. T-04/T-05: 6 clauses located and extracted; DPA not located, absence_confidence = 0.92. T-06–T-10: 6 COMPLIANT classifications written; DPA written as MISSING, confidence 0.92. Hard stop HS-4 passes (all 7 TaskUnitType records exist, including MISSING). No ET-1 (all confidence ≥ 0.85). No ET-2 (DPA clause absent — ET-2 fires on a present DPA clause, not an absent one). No ET-3 (absence confidence ≥ 0.85). No ET-4/ET-5/ET-6. aggregate_routing_classification() → STANDARD. T-12: contract.status transitions IN_REVIEW → REVIEWED_STANDARD. routing_classification = STANDARD written to Ironclad. ReviewDecision written: decision_type = ACCEPT_AS_IS, decision_made_by = "AGENT", approval_token = null. Tom receives Ironclad summary notification; no review task created. |
| **Pass criteria** | Ironclad case record: `routing_classification = "STANDARD"`. `contract.status = REVIEWED_STANDARD`. 7 ClauseReview records written (6 × COMPLIANT, 1 × MISSING for DPA, all confidence ≥ 0.85). Zero items in Tom's HITL queue for this contract_id. ReviewDecision.decision_type = ACCEPT_AS_IS. ReviewDecision.approval_token = null. No ET-1 through ET-6 fired. Ironclad case record logs playbook_version_used = "v3.4". |
| **Failure signal** | If a later defensive addition broadened ET-1 to "confidence < 0.90" (instead of < 0.85), the INDEMNITY_SCOPE clause at 0.88 would trigger HITL unnecessarily — the autonomous path breaks, Tom receives a queue item he shouldn't, and the throughput KPI (≤ 35% HITL rate) degrades silently. No exception is raised; the test simply shows HITL triggered = True on a contract that should route cleanly. |

---

### S-2 — Liability cap confidence exactly at threshold does not trigger ET-1

| Field | Content |
|-------|---------|
| **Type** | Edge case |
| **Delegation boundary tested** | C-2 (Clause Extraction & Playbook Comparison) — Agent-led + Human Oversight. The boundary condition: confidence ≥ 0.85 → autonomous; confidence < 0.85 → ET-1. The claim is that 0.85 is inclusive on the autonomous side. |
| **Input** | Vendor: MidtechCo Ltd. 22-page software licence. LIABILITY_CAP: "Our aggregate liability shall not exceed £275,000 or 12 months fees, whichever is greater" — £275,000 > £250,000 floor → COMPLIANT. Agent confidence score = 0.85 exactly (the numeric comparison is unambiguous; the 0.85 reflects borderline extraction confidence on the "12 months fees" sub-clause). All other 6 clauses COMPLIANT, confidence ranging 0.87–0.94. No DPA clause present (DPA = MISSING, absence confidence 0.91). |
| **Expected agent behaviour** | ET-1 evaluation: `agent_confidence_score < CONFIDENCE_THRESHOLD` → `0.85 < 0.85` → False. ET-1 does NOT fire for LIABILITY_CAP. All other clauses clear their confidence checks. No HITL triggered. aggregate_routing_classification() → STANDARD. Contract routes autonomously. |
| **Pass criteria** | Zero ET-1 items in HITL queue. `contract.status = REVIEWED_STANDARD`. `routing_classification = "STANDARD"`. The LIABILITY_CAP ClauseReview record has `agent_confidence_score = 0.85` and `playbook_match_status = COMPLIANT`. |
| **Failure signal** | If ET-1 is implemented as `agent_confidence_score <= CONFIDENCE_THRESHOLD` (wrong operator) or `agent_confidence_score < 0.86` (off-by-one threshold), confidence = 0.85 fires ET-1. The contract goes to Tom's HITL queue with a flag that reads "confidence 0.85 below threshold" — incorrect, because 0.85 is at threshold. Tom reviews it, approves the COMPLIANT classification, and the contract routes STANDARD. No exception is raised. The wrong-operator failure is silent: HITL rate increases by approximately 5% of contracts (those with confidence scores exactly at 0.85), measurable only in quarterly HITL rate reporting. |

---

### S-3 — DPA clause COMPLIANT at high confidence still routes to HITL, not autonomously

| Field | Content |
|-------|---------|
| **Type** | Failure mode / delegation boundary |
| **Delegation boundary tested** | T-09 (DPA clause assessment) is assigned "Agent-led + HITL mandatory: ALL DPA classifications flagged to Tom regardless of confidence" (D4 Activity Catalog). C-3 deviation triage is Human-led + Agent Support. The boundary claim: ET-2 fires unconditionally for any present DPA clause, even when confidence is 0.95 and playbook_match_status is COMPLIANT. No confidence check applies. |
| **What a coding agent building the cheaper option would produce** | A coding agent reading the general HITL rule from D4 §5 Autonomy Matrix ("HITL on condition: confidence < 0.85") would implement a single confidence gate covering all clause types. For a DPA clause with COMPLIANT classification and confidence 0.95, the condition `0.95 < 0.85` evaluates to False → ET-2 does not fire → HITL not triggered → contract routes as STANDARD → routing_classification = STANDARD committed to Ironclad autonomously. Tom never reviews the DPA clause. |
| **Why that implementation is wrong** | The DPDI Act Q1 updates are not incorporated into playbook v3.4 (confirmed in D4 §6 ET-2 and D5 Gap G-2). A COMPLIANT classification at confidence 0.95 is a correct comparison against a stale playbook — it means the vendor's DPA clause matches the current v3.4 position, which may itself not reflect current UK law. The risk is not classification uncertainty (hence high confidence), it is playbook staleness. Confidence gating does not protect against this because confidence scores the agent's certainty about the comparison, not the playbook's regulatory currency. |
| **Input** | Vendor: DataSystems Ltd. 28-page data processing and services agreement. DPA clause extracted: "Processor shall process personal data only on documented instructions from controller; implement appropriate technical and organisational measures per Article 32 GDPR; notify controller within 72 hours of becoming aware of a personal data breach; maintain records of processing activities per Article 30 GDPR." Playbook v3.4 comparison → COMPLIANT with current UK GDPR / DPA 2018 position. Agent confidence: 0.95. All other 6 clauses: COMPLIANT, confidence 0.87–0.93. |
| **Expected agent behaviour** | T-09 DPA assessment: DPA clause present (extracted_text not null). ET-2 evaluation: `task_unit_type == DATA_PROCESSING_AGREEMENT` → True. ET-2 fires unconditionally. HITL queue receives ET-2 payload: contract_id, ironclad_case_id, trigger_id = "ET-2", DPA clause text, playbook comparison, confidence 0.95, annotation "DPDI Act updates not reflected in playbook v3.4 — classification reflects UK GDPR / DPA 2018 only." contract.status transitions to AWAITING_APPROVAL. routing_classification NOT written to Ironclad until Tom approves. |
| **Pass criteria** | `run.hitl_required == True`. One ET-2 item in HITL queue with trigger_id = "ET-2". `contract.status = AWAITING_APPROVAL`. `contract.routing_classification` is null or not yet committed (Tom has not yet approved). DPA ClauseReview.agent_reasoning_summary contains "DPDI Act updates not reflected in playbook v3.4". |
| **Failure signal (cheaper implementation)** | `run.hitl_required == False`. Zero ET-2 items in HITL queue. `contract.status = REVIEWED_STANDARD`. `routing_classification = "STANDARD"` committed to Ironclad. Tom receives a summary notification (not a review task). Helix has autonomously accepted a DPA clause that has not been reviewed against DPDI Act provisions. No exception is raised. The failure is detectable only by an Ironclad audit of STANDARD-routed contracts containing a DPA clause — a check that does not happen by default unless explicitly scheduled. |

---

## 3. Quiet Failure Catalogue

| QF ID | Mechanism | What was written (or not written) | Why no one notices immediately | Detection check | Taxonomy category |
|-------|-----------|-----------------------------------|-------------------------------|-----------------|-------------------|
| QF-1 | Vendor name in new contract is "Acme Limited"; Ironclad case history contains "Acme Ltd". Levenshtein distance = 4, above the fuzzy match threshold of 2 (D4 §6 ET-6 assumption). ET-6 does not fire. Prior escalation history for this vendor — a MAJOR_DEVIATION on IP_OWNERSHIP six months ago — is not surfaced. | 6 ClauseReview records written, all COMPLIANT; contract routes STANDARD. No ET-6 payload in HITL queue. Ironclad case record has no advisory annotation linking to the prior escalation. | Tom is not asked to review the contract. The CRO-driven time pressure means Tom does not independently check Ironclad history for every STANDARD-path contract. The missed advisory is an omission, not a wrong field value — Ironclad's case record is internally consistent. | Quarterly audit: compare all STANDARD-routed contracts against Ironclad vendor history by exact-match AND fuzzy-match (distance ≤ 4). Flag any contract where a near-match vendor has a prior ESCALATION_REQUIRED case not surfaced by ET-6 during processing. | **Spec ambiguity** — the fuzzy threshold of 2 is labelled as an assumption in D4 §6 ET-6, not a specified value from the scenario. A different threshold would produce different ET-6 firing behaviour. Fix: specify the fuzzy threshold explicitly in CLAUDE.md and validate it against the first quarter's vendor name data. |
| QF-2 | Playbook RAG retrieval for SLA_COMMITMENTS returns the GOVERNING_LAW playbook section (cosine similarity was borderline; wrong chunk ranked first). Agent compares vendor's SLA uptime clause against the governing law section. The comparison produces a low-confidence output (confidence 0.61) and ET-1 fires. Tom reviews the flag, sees a confusing comparison, overrides with his own classification. The override is recorded correctly. | ClauseReview for SLA_COMMITMENTS written with Tom's override. The underlying retrieval failure is not logged — only the resulting low confidence score is visible in Ironclad. | Tom attributes the low confidence to the clause being ambiguous, not to the retrieval producing the wrong playbook section. He overrides it and moves on. The root cause (wrong playbook section retrieved) is masked by the ET-1 HITL process working correctly on the symptom. Over time, HITL rate for SLA_COMMITMENTS climbs above baseline without an obvious cause. | Monitor HITL rate per clause type weekly. A sustained increase in ET-1 triggers on a specific clause type (e.g., SLA_COMMITMENTS rate rises from 5% to 20%) signals a retrieval quality issue, not a model quality issue. Confirmation: log the playbook section title retrieved alongside the confidence score in every ClauseReview record. A mismatch between the retrieved section title and the task_unit_type is a retrieval error, not a classification error. | **Design gap** — the spec (D5 §5, retrieval quality evaluation) specifies checking that the retrieved chunk contains the operative numeric threshold, but does not require logging the retrieved section title to Ironclad. Without that log field, retrieval errors are invisible. Fix: add playbook_section_retrieved logging as a required field in ClauseReview (already present in CLAUDE.md entity definition — verify it is populated in T-12). |
| QF-3 | Agent consistently assigns confidence scores of 0.85–0.87 to borderline LIABILITY_CAP and INDEMNITY_SCOPE classifications — just above the 0.85 HITL gate. The underlying classification is uncertain (true confidence is closer to 0.75–0.80) but the agent's calibration is optimistic for these two clause types. 15% of these borderline cases are actually MINOR_DEVIATION or worse, but they route as STANDARD without Tom's review. At 300 contracts/quarter × 7 clauses, 2,100 classifications are produced; if 10% of those are borderline (210 clauses) and 15% of those are miscategorised (31 clauses), approximately 31 misclassified clauses per quarter route autonomously. | 31 ClauseReview records per quarter written with `playbook_match_status = COMPLIANT` and `agent_confidence_score ∈ [0.85, 0.87]` where the correct classification is MINOR_DEVIATION. These records are internally consistent and pass all schema validation. Ironclad shows a clean STANDARD-path contract for the affected vendors. | Tom is not notified. The classification looks right. The error surfaces only when a vendor later claims a contractual position that Helix accepted — e.g., a liability cap of £225,000 that the agent classified as COMPLIANT (£250,000 floor) due to extraction ambiguity on the "whichever is greater" qualifier. At that point, the contract is signed; Ironclad shows a STANDARD-path contract; the miscategorisation is buried in a ClauseReview record from the prior quarter. | Quarterly random audit: Tom reviews 10% of STANDARD-path contracts (≈21 contracts/quarter, ≈147 clauses). Any override in this audit is a confirmed miscategorisation. Track override rate per clause type. If override rate exceeds 10% of audited clauses on any single type, recalibrate the confidence scoring for that type. The KPI (≥ 90% accuracy) is only measurable through this audit — it is not visible in real-time. | **Design gap** — the spec defines the accuracy KPI and the audit method (D4 §3) but does not specify a real-time monitoring mechanism that would surface calibration drift between quarterly audits. Fix: add a confidence distribution dashboard (mean and variance per clause type, updated weekly) with an alert threshold. A drop in mean confidence ≥ 0.05 on any clause type within a 4-week window triggers a recalibration review before the next quarter's audit. |
| QF-4 | A DPA clause references the vendor's "legitimate interests basis for processing under applicable data protection law." ET-2 fires correctly; Tom receives the HITL payload with the DPDI Act staleness annotation. Tom reads the annotation, marks the task as reviewed in Ironclad, and approves the STANDARD routing for the DPA clause. Tom's review was valid procedurally — the annotation was read, the task was acknowledged — but Tom did not identify the phrase "legitimate interests basis" as a potential DPDI Act applicability signal requiring Amelia's review. The DPDI Act updates the legitimate interests test in ways not reflected in playbook v3.4 (D4 §6 ET-2; D5 Risk Register). | DPA ClauseReview written with Tom's approval recorded (`human_override = "OVERRIDE by Tom Chen (PARALEGAL) at [timestamp]: COMPLIANT"`). Contract routes STANDARD. Ironclad audit log shows ET-2 fired and Tom approved — process was followed. | No exception is raised. The HITL process completed correctly. Tom's approval is logged. The failure is that the trigger for Amelia escalation (DPA clause references a DPDI Act applicability signal) was not identified by Tom during his review. This is not detectable in the Ironclad case record because the process worked as designed — the gap is that the process relied on Tom recognising a technical legal trigger he may not have the expertise to identify. | Amelia to conduct a retrospective review of all DPA HITL cases approved by Tom (not escalated to her) in the first two quarters post-deployment. Any contract where the DPA clause contains "legitimate interests", "data subject access rights", or "UK adequacy" language and was not escalated to Amelia is a candidate false-negative. This is a manual audit, not a system check. Structural fix: agent adds keyword-triggered sub-flag within ET-2 payload — "⚠ DPDI applicability signal detected: [matched phrase] — escalate to Amelia before approving." | **Design gap** — the ET-2 payload (D4 §6) specifies the DPDI staleness annotation but does not define which specific clause language patterns should trigger automatic Amelia escalation (versus Tom-only review). The spec leaves this distinction to Tom's judgment, which is unreliable for technical regulatory signals. Fix: add a keyword list to ET-2 evaluation (legitimate interests, data subject access, UK adequacy, DPDI, legitimate interest assessment) that produces a sub-flag in the HITL payload marking the case as Amelia-escalation-required. |

---

## 4. Build-Loop Diagnostic Test

**Scenario tested:** S-3 — DPA mandatory HITL regardless of confidence and compliance.

**Taxonomy classification:** Spec ambiguity. The general HITL rule in D4 §5 states "HITL on condition: confidence < 0.85." The DPA exception in D4 T-09 states "HITL mandatory: ALL DPA classifications." A coding agent implementing the general rule from §5 without reading T-09's delegation level would produce the cheaper implementation. Both interpretations are derivable from D4 — the exception requires reading T-09 specifically, not just the autonomy matrix summary.

```python
def test_dpa_compliant_high_confidence_still_triggers_et2_hitl(minimal_docx):
    """
    Fixture: contract with DPA clause present (extracted_text not null),
    classified COMPLIANT by StubClauseClassifier, confidence 0.95.
    
    Delegation boundary: T-09 = "HITL mandatory regardless of confidence" (D4 Activity Catalog).
    
    Cheaper implementation produces (wrong):
        run.hitl_required == False
        len([p for p in hitl.all_items() if p.trigger_id == "ET-2"]) == 0
        run.contract.status == ContractStatus.REVIEWED_STANDARD
    
    Correct implementation produces:
        run.hitl_required == True
        len([p for p in hitl.all_items() if p.trigger_id == "ET-2"]) == 1
        run.contract.status == ContractStatus.AWAITING_APPROVAL
    """
    # StubClauseClassifier defaults: COMPLIANT, confidence 0.90 for all types
    # minimal_docx fixture includes a DPA clause section — DPA extracted_text is not null
    orch, _, hitl = make_orchestrator()
    run = orch.process_contract(make_contract(), minimal_docx)

    # Primary assertion: ET-2 fired
    et2_payloads = [p for p in hitl.all_items() if p.trigger_id == "ET-2"]
    assert len(et2_payloads) == 1, (
        "ET-2 must fire exactly once for a contract with a DPA clause, "
        "regardless of confidence or playbook_match_status"
    )

    # Secondary assertion: contract did not route autonomously
    assert run.hitl_required is True
    assert run.contract.status == ContractStatus.AWAITING_APPROVAL, (
        "Contract must not reach REVIEWED_STANDARD while DPA clause is pending Tom review"
    )

    # Anti-assertion: cheaper implementation fingerprint
    # If this fails, the cheaper implementation was built:
    #   run.hitl_required is False AND et2_payloads is empty
    # This is not asserted here — it would pass if the wrong implementation was built.
    # The positive assertions above catch it.

    # DPDI annotation present in DPA ClauseReview reasoning
    dpa_review = next(r for r in run.clause_reviews if r.task_unit_type == TaskUnitType.DATA_PROCESSING_AGREEMENT)
    assert "DPDI Act updates not reflected" in dpa_review.agent_reasoning_summary
```

**This test is already in the test suite as `test_dpa_clause_always_triggers_hitl` in `tests/test_orchestrator.py:146`.** It passes in the current build. If the ET-2 unconditional trigger in `src/escalation.py` is refactored to a confidence-gated check, this test fails — surfacing the regression before it reaches production.

---

## 5. Assumption Log

> **Assumption [A1]:** The agent's standard path — all 7 clauses COMPLIANT, confidence ≥ 0.85, no DPA clause present — results in fully autonomous routing with no Tom review required. Tom receives a summary notification only.
> **Why it matters:** S-1 is built on this assumption. If the actual requirement is "Tom must confirm every routing decision including STANDARD," then S-1's pass criterion (zero HITL queue items) is wrong and the happy path does not exist.
> **If wrong:** Every contract requires Tom action regardless of confidence or compliance → HITL rate = 100% → throughput KPI (≤ 35% HITL rate) is unachievable by design → the business case collapses.
> **Confidence:** Medium — D4 §5 Autonomy Matrix says "Tom notified but no review required" for the standard path; CLAUDE.md §7 says "Tom must confirm absence" for MISSING clauses. The two statements are in tension for a contract where DPA is MISSING with high absence confidence. Resolve in discovery before build.

> **Assumption [A2]:** The 0.85 confidence threshold is inclusive on the autonomous side (`confidence >= 0.85` routes autonomously; `confidence < 0.85` triggers ET-1). The operator is ≥, not >.
> **Why it matters:** S-2 tests this boundary condition exactly. An off-by-one implementation (using >) would route confidence = 0.85 to HITL unnecessarily, inflating HITL rate and causing real contracts to receive unnecessary human review.
> **If wrong:** The HITL rate increases for borderline-confidence clauses; Tom's queue receives false-positive flags; KPI drift is small but persistent and goes unnoticed until quarterly reporting.
> **Confidence:** High — CLAUDE.md §3 states "confidence ≥ 0.85" as the COMPLIANT condition; D4 §3 states "confidence ≥ 0.85" as the HITL threshold. Both documents use ≥. Implemented as `<` in `src/config.py CONFIDENCE_THRESHOLD = 0.85` and tested in `test_escalation.py::TestET1ConfidenceThreshold::test_does_not_fire_at_threshold`.

> **Assumption [A3]:** ET-6 vendor history match uses Levenshtein distance ≤ 2 as the fuzzy threshold (D4 §6 ET-6 labels this as an assumption). Values of "Acme Ltd" vs "Acme Limited" (distance 4) are treated as non-matches.
> **Why it matters:** QF-1 is the quiet failure that results from this threshold being too tight. If the real vendor population has many subsidiary/shortened name variants at distance 3–5, ET-6 fires less than expected and the historical escalation signal is systematically suppressed.
> **If wrong:** ET-6 has low recall; prior escalation history for vendors with name variants is missed consistently; the quiet failure in QF-1 is more prevalent than the 5% estimate.
> **Confidence:** Low — the threshold value is an assumption. Validate against the first quarter's vendor name data before fixing it in production configuration.

---

## Summary — main 3 points

1. **The DPA mandatory HITL boundary (S-3) is the highest-risk delegation boundary in the build.** It is the one place where a coding agent implementing the general confidence gate would produce a silently wrong result — routing a DPDI-affected DPA clause autonomously because confidence is high and compliance looks correct against a stale playbook. The `test_dpa_clause_always_triggers_hitl` test in the current suite already catches this; it must not be removed or weakened.

2. **Three of the four quiet failures are design gaps, not misreads — they require spec additions, not re-prompts.** QF-2 needs a retrieved section title logged in ClauseReview; QF-3 needs a real-time confidence distribution monitor between quarterly audits; QF-4 needs a keyword-triggered Amelia sub-flag within the ET-2 payload. All three are detectable in principle but not detectable in the current design without those additions.

3. **The quarterly random audit of STANDARD-path contracts is the only check that catches confident-but-wrong autonomous routing.** No real-time mechanism surfaces a misclassification that passed the 0.85 confidence gate. The KPI (≥ 90% accuracy) is only measurable through that audit — it must be scheduled, resourced (Tom's time), and its results fed back into confidence recalibration.
