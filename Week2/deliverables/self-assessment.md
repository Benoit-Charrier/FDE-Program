# Self-Assessment — Benoit Charrier, Week 2
**Reviewer**: Benoit Charrier (self)
**Date**: 2026-04-30
**Scenario**: Scenario 2 — Helix Workforce Software Vendor Contract Clause Review

---

## Specific Gaps

### Gap 1 — D2 assigns C-2 a single archetype but D4 T-07 and T-08 operate at different delegation levels

**Where**: `D2_delegation_suitability_matrix.md`, Cluster C-2 (Clause Extraction & Playbook Comparison) — scored 2/7, assigned "Agent-led + Human Oversight"; `D4_agent_purpose_document.md`, Activity Catalog T-07 and T-08.

**The problem**: D4 subdivides C-2 into two tasks with materially different delegation levels. T-07 (Numeric threshold comparison) is "Fully agentic where vendor value is unambiguous and confidence ≥ 0.85." T-08 (Qualitative clause comparison) is "Agent-led + HITL on condition: confidence < 0.85 or clause materially deviates." In the standard path, numeric comparisons (liability caps, SLA commitments) route fully autonomously — no human oversight step occurs unless confidence falls below threshold. D2's cluster label "Agent-led + Human Oversight" accurately describes T-08 but understates T-07's autonomy in normal operation. A coding agent reading D2's delegation matrix would apply the same oversight model to both tasks, and might introduce unnecessary HITL gates on numeric comparisons that should route autonomously.

The mismatch also weakens the D2 suitability argument: C-2 is scored 2/7 because of judgment requirements and external dependency, but numeric threshold comparison (T-07) scores differently on most of those dimensions than qualitative comparison (T-08). The cluster-level score is defensible but the reasoning is aggregated in a way that blurs the delegation split the build actually implements.

**Minimum fix**: Add a note to the C-2 archetype row: *"Within C-2: T-07 (numeric) is Fully Agentic in the standard confidence path — no oversight step occurs on unambiguous numeric comparisons above the playbook floor where confidence ≥ 0.85. T-08 (qualitative) is Agent-led + Human Oversight. The cluster label reflects T-08's higher judgment load; the coding agent must not apply T-08's HITL conditions to T-07."* This closes the delegation level ambiguity before it reaches the build.

---

### Gap 2 — The routing precedence rule (ESCALATION_REQUIRED > NEGOTIABLE > STANDARD) is not stated in D4

**Where**: `D4_agent_purpose_document.md`, Section 5 Autonomy Matrix — "AGENT PROPOSES, HUMAN APPROVES BEFORE ACTION"; `CLAUDE.md` Section 3 (Contract-Level Routing Classification), Precedence rule.

**The problem**: D4's autonomy matrix states that the agent prepares a "triage routing proposal for any contract with one or more deviation-flagged clauses" and places it in Tom's queue. It does not state how the contract-level routing classification is derived from the seven clause-level results — specifically, it does not state that a single MAJOR_DEVIATION clause makes the entire contract ESCALATION_REQUIRED regardless of other clauses. The most-severe-wins rule exists in CLAUDE.md §3 ("ESCALATION_REQUIRED overrides NEGOTIABLE, which overrides STANDARD. A single MAJOR_DEVIATION clause makes the entire contract ESCALATION_REQUIRED.") and in D9 Assumption A-L1 (where it is labelled Low confidence with a caveat about Tom's actual practice).

The Build Loop Analysis shows the coding agent was given both D4 and CLAUDE.md simultaneously, so it correctly implemented the aggregation rule. But D4 as a standalone spec is underspecified: a coding agent reading only D4 cannot derive the most-severe-wins logic — it could implement averaging, majority vote, or clause-by-clause routing and still satisfy D4's stated behaviour. The precedence rule is load-bearing architecture; it belongs in D4, not only in CLAUDE.md.

The downstream risk is compounded by D9 A-L1 flagging it as an assumption with Low confidence, meaning there is acknowledged uncertainty about whether this reflects Tom's actual practice. If the assumption resolves differently (Tom routes only the escalated clause, not the entire contract), the data model changes — one ReviewDecision per contract versus one per flagged clause. That architectural fork is downstream of D4 not stating the rule explicitly.

**Minimum fix**: Add one sentence to D4 §5 under "AGENT PROPOSES, HUMAN APPROVES": *"Contract-level routing classification is determined by the most severe clause-level result: a single MAJOR_DEVIATION or REQUIRES_SENIOR_REVIEW clause makes the entire contract ESCALATION_REQUIRED regardless of other clause classifications. This is the `aggregate_routing_classification()` rule; validate Tom's actual mixed-contract practice before locking the data model (see D9 A-L1, U-4)."*

---

### Gap 3 — D8 has no test scenario for FM-1 (the routing precedence failure under the most consequential failure mode)

**Where**: `D8_Validation_Design.md`, Sections 2–4 — three test scenarios (S-1, S-2, S-3) and one build-loop diagnostic test; `D4_agent_purpose_document.md`, Section 7 Failure Modes — FM-1.

**The problem**: FM-1 (agent classifies an escalation-required clause as negotiable) is explicitly called "the hardest failure mode to catch reliably" in D4 §7. The consequence is a major deviation clause entering WS2 paralegal redline without senior lawyer review, potentially producing an incorrect negotiating position. Despite this characterisation, D8's three test scenarios cover: the happy path (S-1, all COMPLIANT → STANDARD autonomous), the threshold boundary (S-2, confidence exactly 0.85 → no ET-1), and the DPA mandatory HITL (S-3, COMPLIANT high-confidence DPA → still HITL). None of the scenarios tests the routing precedence under mixed clause conditions.

A cheaper implementation could pass all three current tests while incorrectly implementing the aggregation: for example, routing a contract with six COMPLIANT clauses and one MAJOR_DEVIATION to NEGOTIABLE (averaging, or "one clause doesn't override the whole contract") — every existing test would still pass because none of them set up a MAJOR_DEVIATION input and assert ESCALATION_REQUIRED as the contract-level output.

The gap is structurally symmetric to Gap 2 in Alexandra Rendon's feedback (anti-assertion missing for the Aetna escalation case) but with higher consequence: a miscategorised liability cap deviation entering WS2 has direct commercial and legal exposure.

**Minimum fix**: Add to D8 §2:

```
### S-4 — Single MAJOR_DEVIATION clause forces contract-level ESCALATION_REQUIRED

| Field | Content |
|-------|---------|
| Type | Routing precedence / FM-1 boundary |
| Delegation boundary tested | aggregate_routing_classification() — the most-severe-wins rule. |
| Input | 7 clause results: LIABILITY_CAP MAJOR_DEVIATION confidence 0.77 (£80,000 vendor vs £250,000 floor — deviation 68%, above the 50% ET-5 threshold); remaining 6 clauses COMPLIANT confidence 0.87–0.93. |
| Expected behaviour | routing_classification = ESCALATION_REQUIRED. Contract enters AWAITING_APPROVAL. Tom receives ET-5 payload for the liability cap deviation. |
| Pass criteria | routing_classification == "ESCALATION_REQUIRED". contract.status == AWAITING_APPROVAL. ReviewDecision.decision_type == ESCALATE. NOT routing_classification == "NEGOTIABLE". |
| Failure signal | If aggregate_routing_classification() returns NEGOTIABLE (e.g., majority-wins or averaging), the contract enters WS2 redline instead of WS3. FM-1 has occurred. Tom never sees the £80,000 liability exposure. |
```

Also add to D8 §4 (Build-Loop Diagnostic Test): a Python test asserting `routing_classification == ESCALATION_REQUIRED` and `routing_classification != NEGOTIABLE` when any input ClauseReview has `MAJOR_DEVIATION`.

---

## Delegation-Archetype Calibration

This submission does not default to fully agentic. The three-layer architecture in D2 — autonomous backbone (C-1, C-2, C-7), human-anchored judgment (C-3, C-4, C-5), non-negotiable gates (C-6, C-8) — is genuine differentiation backed by suitability scores. C-3 (Deviation Triage) at 1/7 with Human-led + Agent Support is the right call: the decision requires senior lawyer judgment on negotiating position, and the anti-pattern check in D2 names why rules-based routing would fail (tacit deviation thresholds, regulatory exposure). C-8 (Counteroffer Dispatch Governance) as Human Only is the correct assignment given the GC hard rule.

One calibration concern worth naming: C-7 (Counteroffer Package Preparation) is assigned Fully Agentic, but D4's delegation for T-12 (structured classification report and Ironclad write) is "Fully agentic for report generation; HITL approval at T-11 gates whether the routing decision is committed." C-7's Fully Agentic assignment is downstream of the T-11 approval gate — it works correctly because it inherits a gated input, but D2 doesn't make this dependency explicit. A reviewer reading D2 alone might ask why C-7 (package assembly, a complex task) is Fully Agentic while C-2 (comparison, more mechanical) is Agent-led + Human Oversight. The dependency on T-11's approval gate is the answer, but it's not in D2.

---

## Lived-Work vs. Documented-Process

D1's lived process narrative for WS1 and WS2 is the strongest element of the cognitive load map. The "will ask Sarah" informal consultation chain is the kind of untracked latency that distinguishes genuine work practice analysis from SOP description. Identifying that this escalation is not captured in Ironclad — that it lives in email threads and corridor conversations — directly motivates the ET-1/ET-4/ET-6 escalation design, which routes those informal consultations through a structured HITL queue. That connection from observation to design is the correct methodology.

The explicit choice not to decompose WS3 and WS4 is a good design decision that is clearly justified: the CCA's scope ends at triage routing, and WS3/WS4 cognitive load is out of scope for this agent. Noting this as intentional rather than an omission is the right discipline.

One observation: D1 identifies the informal sign-off mechanism (lawyer approvals happen via Outlook reply with no Ironclad record) as a lived-process gap, and D9 U-3 escalates this into the highest-consequence unknown. But D1 doesn't trace the consequence of this gap forward to the CCA's design — the fact that the `approval_token` field relies on a mechanism that may not currently exist is a design-stakes implication that could be stated at the D1 stage, not only at D9. The gap is resolved correctly in D9, but the chain from lived-work observation to design risk is only fully closed at the final deliverable.

---

## Strength to Preserve

**The ET-2 unconditional DPA HITL design is the standout architectural decision in the submission.** The insight is specific: confidence gating does not protect against playbook staleness because a high-confidence classification against a stale playbook is confidently wrong, not uncertainly wrong. The solution — HITL mandatory regardless of confidence, with a hard deployment gate until the playbook is updated — correctly identifies that this is a compliance requirement, not a model capability limitation. S-3 in D8 validates it by constructing the cheaper wrong implementation (confidence gate covering all clause types, DPA at 0.95 routes autonomously) and explaining exactly why it fails. The build-loop diagnostic test in D8 §4 closes the loop by showing the test already exists in the suite and explicitly naming what would break if the unconditional trigger were weakened.

Preserve this pattern: identify the failure mode first, construct the cheaper wrong implementation that a coding agent would reasonably produce, then design the test that catches that specific implementation. This is not just thorough testing — it is delegation boundary defence made operational.

---

## Gate 2 Calibration

This submission is tracking toward a Gate 2 pass — the delegation boundaries are defensible, the lived-work analysis is genuine, and ET-2 is the best-reasoned single architectural decision in the batch — but Gap 2 (routing precedence rule absent from D4) needs to be resolved before the spec would be safe to hand to a coding agent without CLAUDE.md, and Gap 3 (no FM-1 test scenario) leaves the hardest-to-catch failure mode without a build-level safeguard.
