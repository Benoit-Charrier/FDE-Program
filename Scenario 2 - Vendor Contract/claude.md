# Claude Build Brief - Scenario 2 Vendor Contract Review Agent

## Goal

Build an implementation-ready MVP of the Inbound Vendor Contract Review Agent defined in [3 Capability specification.md](3%20Capability%20specification.md).

The MVP must automate first-pass contract review against a structured legal playbook, produce clause-level outputs, route contracts to the right queue, and enforce the non-negotiable control that no negotiated outbound package can be released without named lawyer sign-off.

## Source Of Truth

Treat [3 Capability specification.md](3%20Capability%20specification.md) as the primary requirements document.

Use supporting context from:

- [1 Problem statement and success metrics.md](1%20Problem%20statement%20and%20success%20metrics.md)
- [2 Delegation analysis.md](2%20Delegation%20analysis.md)
- [4 Validation design.md](4%20Validation%20design.md)
- [5 Assumptions & unknowns.md](5%20Assumptions%20%26%20unknowns.md)

If any conflict appears, follow the capability specification first and log unresolved conflicts as explicit assumptions.

## What To Build

Implement a service with these end-to-end behaviors:

1. Ingest PDF and DOCX contracts up to 40 pages.
2. Extract these clause families with page references and confidence: liability, DPA, termination, IP ownership, SLA, governing law, indemnity.
3. Compare extracted clauses against a structured playbook.
4. Classify each clause as `match`, `negotiable_deviation`, or `escalate`.
5. Produce contract-level routing decision: `standard`, `playbook_negotiable`, or `senior_lawyer_escalation`.
6. Generate draft redlines only from approved fallback language.
7. Never generate novel fallback language when no approved fallback exists.
8. Block outbound release for any negotiated package until named lawyer sign-off exists for each changed clause.
9. Log all key actions and decisions for auditability.
10. Expose operational metrics for turnaround, route distribution, override rate, and escalation rate.

## Required Deliverables From Claude

Create all of the following in the repository:

1. Architecture document (`docs/architecture.md`) covering modules, data flow, and control boundaries.
2. Data contracts (`docs/data-contracts.md`) with JSON schemas for inputs, extracted clauses, routing decisions, redline proposals, approvals, and audit events.
3. Policy/playbook schema and sample (`config/playbook.schema.json`, `config/playbook.sample.json`).
4. Implemented code for ingestion, extraction pipeline, rules engine, redline generator, routing, approval gate, and audit logging.
5. API or CLI interface for running contract analysis and recording approvals.
6. Test suite with at least:
   - Happy path (standard contract)
   - Edge case (playbook-negotiable deviations)
   - Failure mode (low confidence + attempted release without sign-off)
7. Validation report (`docs/validation-report.md`) mapping test outcomes to [4 Validation design.md](4%20Validation%20design.md).
8. Runbook (`README.md`) with setup, execution, and example commands.

## Decision Rules To Encode

Implement these rules explicitly in code, not only in prompt text:

1. If required clause missing or confidence below threshold, escalate.
2. If all target clauses match approved playbook positions, route `standard`.
3. If deviations exist and all map to approved fallback language with no escalation rule triggered, route `playbook_negotiable`.
4. If any must-escalate trigger fires, or clause is novel, route `senior_lawyer_escalation`.
5. If negotiated language exists, release is blocked until clause-level named lawyer approvals are recorded.

## Escalation Triggers (Must Be Configurable)

- Uncapped liability or non-approved cap structure
- Missing/non-compliant DPA
- IP ownership transfer from company standard
- Over-broad indemnity scope
- Governing law outside approved jurisdictions
- Low extraction confidence
- Missing mandatory clause family
- Clause type absent from playbook
- Conflicting clause signals preventing safe routing

## Non-Functional Requirements

1. Deterministic rule execution for routing and release gating.
2. Full audit trail for extraction, classification, routing, redline suggestion, overrides, and approvals.
3. Config-driven policies and thresholds; no hardcoded legal values in business logic.
4. Safe failure behavior: when uncertain, escalate rather than auto-approve.
5. Reproducible local test run with one command.

## Acceptance Criteria

The build is acceptable only if all are true:

1. All 10 minimum functional requirements in [3 Capability specification.md](3%20Capability%20specification.md) are implemented and demonstrable.
2. The three validation scenarios from [4 Validation design.md](4%20Validation%20design.md) pass with evidence.
3. Attempted outbound release without required lawyer sign-off fails every time.
4. No redline is produced from invented language outside approved playbook entries.
5. Test artifacts clearly show classification, routing, and escalation reasons.

## Implementation Guidance

- Start with a rules-first architecture; LLM extraction can be used, but final routing and release control must be rule-enforced.
- Keep legal policy externalized in config so legal ops can update tolerances without code changes.
- Prefer modular components:
  - `ingestion`
  - `clause_extraction`
  - `playbook_matching`
  - `redline_generation`
  - `routing`
  - `approval_gate`
  - `audit`
  - `metrics`
- Create synthetic fixtures representing standard, negotiable, and escalation contracts for deterministic testing.

## Working Agreement

When implementing:

1. Do not skip unresolved requirements; document gaps under `Known Limitations` with explicit rationale.
2. If assumptions are required, list them in `docs/assumptions-log.md` and map each to [5 Assumptions & unknowns.md](5%20Assumptions%20%26%20unknowns.md).
3. Keep humans in control of policy and final legal approval at all times.
