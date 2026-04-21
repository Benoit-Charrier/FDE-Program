# Deliverable 1 — Problem Statement and Success Metrics

## Problem Statement

A legal team of 4 lawyers and 1 paralegal processes approximately 300 inbound vendor contracts per quarter. Each contract is 15–40 pages and must be verified against a negotiation playbook covering seven clause families: liability caps, data processing addenda (DPA), termination clauses, IP ownership, SLA commitments, governing law, and indemnity scope.

At 90 minutes per contract, the team spends roughly **450 person-hours per quarter** on first-pass review — regardless of whether the contract is routine or genuinely complex. The work breaks down predictably by risk level:

- **~210 contracts/quarter (70%)** have terms that already match the playbook and require no negotiation. These consume an estimated 315 hours of review time per quarter for work that is pattern-matching, not legal judgment.
- **~60 contracts/quarter (20%)** contain deviations the paralegal is authorised to redline using pre-approved fallback language. These consume ~90 hours per quarter.
- **~30 contracts/quarter (10%)** contain clause conditions that must reach a senior lawyer before any counteroffer is sent. These are the contracts that actually require lawyer expertise.

The consequence is a 4–6 business day turnaround that procurement considers unworkable, and senior lawyers whose time is absorbed by first-pass spotting on contracts that are overwhelmingly standard.

The general counsel has established one non-negotiable control: **no counteroffer may leave the legal queue without a named lawyer's explicit sign-off on the specific clauses being negotiated.** Any automation that loosens this control is not acceptable.

The core problem is therefore twofold: eliminate the ~315 hours per quarter of repetitive first-pass review on standard and playbook-negotiable contracts, and enforce a hard governance gate on outbound negotiated language so that speed gains do not dilute legal accountability.

---

## Success Metrics

Each metric is tied directly to numbers stated in the scenario.

| # | Metric | Baseline | Target |
|---|--------|----------|--------|
| 1 | Average human review time per contract (full-volume average) | 90 min | ≤ 30 min |
| 2 | Total quarterly human review hours | ~450 hrs | ≤ 150 hrs |
| 3 | Turnaround — standard contracts | 4–6 business days | ≤ 1 business day |
| 4 | Turnaround — playbook-negotiable contracts | 4–6 business days | ≤ 2 business days |
| 5 | Turnaround — escalations (triage flagging only) | 4–6 business days | Same-day flagging to named lawyer |
| 6 | Standard contract correct-routing rate | Unknown | ≥ 95% of ~210 standard contracts routed without false escalation |
| 7 | Must-escalate recall | Unknown | 100% — zero must-escalate contracts pass through without escalation |
| 8 | Counteroffers released without named lawyer sign-off | Unknown | 0 — hard system block, not a policy reminder |
| 9 | Redlines generated outside approved playbook language | Unknown | 0 — no invented fallback language ever reaches a review packet |
| 10 | Low-confidence extractions silently passed as standard | Unknown | 0 — confidence below threshold always triggers escalation |

### What success does not mean

Success is not removing lawyers from the loop. The goal is to concentrate lawyer time on the ~30 escalations per quarter that genuinely need legal judgment — plus sign-off on negotiated packages — while eliminating the ~315 hours per quarter currently consumed by routine first-pass work that a well-configured rules engine can handle more consistently than a time-pressured human.
