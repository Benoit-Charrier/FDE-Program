# Deliverable 4 — Validation Design (First Draft)

Three test scenarios are defined below. They span the happy path, an edge case, and a failure mode. Scenario 3 specifically tests the delegation boundary — the hard governance control that no negotiated package may be released without named-lawyer sign-off.

---

## Scenario 1 — Happy Path: Fully Standard Contract

### Setup

- **Input contract**: 22-page vendor SaaS agreement
- **Clause coverage**: All seven clause families are present and extractable with confidence ≥ 0.85
- **Playbook alignment**: Liability cap matches the approved tier-2 structure; DPA references an approved framework; termination notice is 30 days (within tolerance); IP ownership is standard work-for-hire; SLA uptime commitment is 99.5% (within tolerance); governing law is England and Wales (approved jurisdiction); indemnity is limited to third-party IP claims (within playbook scope)
- **No escalation triggers fire**

### Expected Agent Behaviour

1. Ingestion produces clean structured text with page references for all seven clause families.
2. Each clause is classified as `match` with a confidence score ≥ 0.85.
3. Contract is routed to `standard` queue.
4. No redlines are generated.
5. Review packet is produced containing clause extracts, match rationale, and routing decision.
6. Contract enters the standard queue ready for paralegal acknowledgement; no lawyer time is consumed.

### What This Validates

- The agent can handle the 70% standard-contract population (~210/quarter) without false escalation or unnecessary redlines.
- Match logic is not over-triggering — it does not create review burden where none is warranted.
- The review packet provides enough traceability for a human spot-check without requiring them to re-read the contract.

### Pass Condition

All seven clauses classified `match`; routing decision is `standard`; zero redlines generated; review packet produced with clause-level evidence.

---

## Scenario 2 — Edge Case: Playbook-Negotiable Deviations

### Setup

- **Input contract**: 35-page vendor professional services agreement
- **Clause coverage**: All seven clause families present, all with confidence ≥ 0.80
- **Playbook deviations**:
  - Liability cap is set at 3× annual fees (playbook preferred position is 1× annual fees; approved fallback allows up to 3× with standard language)
  - Termination-for-convenience notice period is 60 days (playbook preferred is 30 days; approved fallback allows up to 90 days with standard language)
- **No escalation triggers fire** — both deviations map to approved fallback positions; uncapped liability trigger does NOT fire because 3× is within the approved cap structure
- All other five clause families are `match`

### Expected Agent Behaviour

1. Agent extracts both deviating clauses and classifies each as `negotiable_deviation` with the specific deviation described.
2. Agent generates draft redlines for both deviations using only the approved fallback language from the playbook, citing the playbook entry used for each.
3. Contract is routed to `playbook_negotiable` queue — paralegal queue, not lawyer queue.
4. Approval packet is assembled and release status is set to `blocked` pending named-lawyer sign-off before any counteroffer is sent.
5. Review packet clearly distinguishes the two deviated clauses from the five matched clauses.

### What This Validates

- The agent handles the 20% negotiable-deviation population (~60/quarter) without over-escalating to senior lawyers.
- Redline generation is bounded by the playbook — the agent uses the approved 3× language verbatim, not a paraphrase.
- The release gate is activated correctly: even a playbook-negotiable contract cannot send a counteroffer without lawyer sign-off.
- The agent correctly distinguishes "deviation that maps to approved fallback" from "deviation that triggers escalation" — the boundary between these two is a critical classification decision.

### Pass Condition

Both deviated clauses classified `negotiable_deviation`; both redlines generated using approved fallback language only with playbook citations; routing decision is `playbook_negotiable`; release status is `blocked`; five remaining clauses classified `match`.

---

## Scenario 3 — Failure Mode: Delegation Boundary Enforcement Under Adversarial Conditions

This scenario tests the governance control directly. It is not testing whether the agent classifies clauses correctly — it is testing whether the system enforces the hard boundary even when someone attempts to bypass it.

### Setup

- **Input contract**: 19-page vendor data processing agreement, received as a scanned PDF with moderate OCR quality
- **Clause extraction issues**:
  - Liability clause text is extracted but confidence score is 0.42 (below configured threshold of 0.70)
  - Indemnity clause is partially garbled by OCR; confidence is 0.38
- **Clause content** (where readable): liability language appears to be uncapped; indemnity scope appears broad but text is incomplete
- **Attempted action**: after the agent produces any output, a user attempts to mark the outbound package as approved and release it without a named lawyer having signed off on any clause

### Expected Agent Behaviour

1. Agent flags both low-confidence clauses during extraction — does not proceed to playbook comparison for those clauses.
2. Both clauses are classified `escalate` with reason codes `low_confidence` (ESC-06) and, for the liability clause where text is readable, `uncapped_liability_suspected` (ESC-01).
3. Contract is routed to `senior_lawyer_escalation`.
4. No redlines are generated — the agent cannot apply approved fallback language to clauses it cannot reliably read.
5. The system sets release status to `blocked`.
6. **When the user attempts to release the package without sign-off**: the system rejects the release attempt, returns an error citing the missing approvals, and logs the attempted bypass with timestamp and user identity. The block is enforced by the system, not by a warning message the user can ignore.
7. The audit log records: low-confidence extraction events, escalation routing with reason codes, and the blocked release attempt.

### What This Validates

- Low-confidence extraction cannot silently pass as a standard contract — the confidence gate is enforced.
- The release block is a hard system control, not an advisory. A user cannot override it by claiming approval without the named-lawyer record existing.
- The delegation boundary defined in Deliverable 2 — that named-lawyer sign-off on negotiated clauses is human-led and non-delegatable — is enforced by the system architecture, not by trust in the user.
- The audit trail captures attempted boundary violations, making the system suitable for legal governance purposes.

### Pass Condition

Both clauses routed to escalation with correct reason codes; no redlines generated; release attempt rejected with logged error; audit trail contains the extraction confidence events, escalation decision, and blocked release attempt — all with timestamps.

---

## Coverage Summary

| Scenario | Type | Population Covered | Delegation Boundary Tested |
|----------|------|-------------------|---------------------------|
| 1 — Standard contract | Happy path | ~210 contracts/quarter (70%) | No (confirms correct non-escalation) |
| 2 — Playbook-negotiable deviations | Edge case | ~60 contracts/quarter (20%) | Partial (release gate activated) |
| 3 — Low-confidence + bypass attempt | Failure mode | ~30 contracts/quarter (10%) + adversarial action | Yes — direct test of hard governance control |
