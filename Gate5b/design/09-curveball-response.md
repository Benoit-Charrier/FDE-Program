# Deliverable 9 — Curveball Response
## Revised Delegation Design + Spec Amendments
**Gate 5b Final Exam · FinCEN Advisory FIN-2026-A-008**
**Submitted: 14:00 CET**

---

## 1. Does this kill the project?

No — the core pipeline (JtD-1 through JtD-5), delegation boundaries, and SAR recommendation
architecture are fully compliant with all 5 requirements; Requirements 4 and 5 require only
nomenclature fixes, Requirement 1 requires an audit log enhancement, and Requirements 2 and 3
add a new rescreening component that is architecturally independent of LACRA's alert-review
pipeline and is deliverable in Wave 2 within a modest budget supplement.

---

## 2. Requirement-by-requirement impact assessment

### Requirement 1 — Per-alert decision record
**Status:** Partially compliant. Gap requires fix.

Current audit log (spec Section 5.1) captures: `agent_version`, `disposition_recommendation`,
`confidence`, `data_sources_accessed`, `data_gaps`. The full case package JSON (retained
separately per Section 5.2) already contains `patterns_detected[].evidence[]`,
`watchlist_status.disconfirmation_evidence[]`, `disposition.supporting_transactions[]` — which
satisfies the "inputs consulted" and "surfaced patterns" elements.

**Gaps:**
1. The audit log does not explicitly include `patterns_detected`, `watchlist_status`, or
   `supporting_transactions` — the FinCEN examiner needs these in the **decision record**, not
   just the case package.
2. The analyst's accept/modify/override action and timestamp are not in the decision record.
   Spec Section 5.4 routes this to the case management system, which is correct operationally
   but must be explicitly linked back to the LACRA `audit_id` to form a single retrievable
   decision record.
3. `sdn_list_version` is not recorded — the examiner needs to know which sanctions list was
   current at case processing time.

**Spec amendments (Req 1):**

**AM-03:** Enhance audit log schema (Section 5.1). Add fields:
```json
{
  "patterns_detected_summary": [{"pattern_type": "string", "severity": "string"}],
  "watchlist_resolution": "NO_HIT | WATCHLIST_DISCONFIRMED | WATCHLIST_UNRESOLVED",
  "supporting_transactions": ["transaction_id"],
  "sdn_list_version": "string (date of SDN list file used)",
  "analyst_action": null,
  "analyst_action_timestamp_utc": null,
  "analyst_id": null
}
```
`analyst_action`, `analyst_action_timestamp_utc`, and `analyst_id` are written null at agent
processing time and updated by the case management system when the analyst acts. The audit
record is keyed by `audit_id` — the case management system must update by `audit_id` on
analyst sign-off. This creates the complete timestamped chain of custody in a single record.

**AM-04:** Add `sdn_list_version` to output schema (Section 4). Prototype: hardcoded to the
mock SDN file date. Production: queryable from OFAC list metadata.

---

### Requirement 2 — Updated sanctions screening within 24 hours
**Status:** Non-compliant. New component required.

LACRA is entirely pull-based (alert → pipeline → analyst queue). There is no mechanism to
rescreen open cases when a sanctions list is updated.

**Architecture addition — Sanctions Rescreening Service (SRS):**

This is a new component, independent of LACRA's core pipeline. It does not change JtD-1
through JtD-5.

```
OFAC/OFSI/EU list update event
        ↓
  SRS trigger (webhook or daily poll)
        ↓
  Query: all open alert cases (status = OPEN, not yet disposed)
        ↓
  For each open case: run JtD-4 disconfirmation logic
  against new SDN entries only
        ↓
  WATCHLIST_UNRESOLVED result → push to analyst queue
  with PRIORITY_RESCREEN flag + 24-hour timestamp
        ↓
  All customer KYC records: rescreen within 5 business days
  (separate batch job, not analyst-queue-gated)
```

LACRA's JtD-4 watchlist reconciliation logic is **reusable** by the SRS — the disconfirmation
rules and output vocabulary are the same. The SRS calls the same logic with the new SDN entry
as input.

**Data architecture requirements that must be baked into Wave 1 (LACRA output):**
- `alert_status` field on case package: `OPEN | DISPOSED | REOPENED` — required so SRS can
  query open cases. Set to `OPEN` at case package creation; updated to `DISPOSED` by case
  management system at analyst sign-off.
- `sdn_list_version` field (see AM-04) — required so SRS knows which cases were processed
  against an older list version.

**Prototype scope:** SRS is Wave 2. The `alert_status` and `sdn_list_version` fields are
baked into the prototype output schema.

---

### Requirement 3 — 90-day retroactive review on material SDN additions
**Status:** Non-compliant. New component required.

**Architecture addition — Retroactive Rescreening Batch Job:**

Triggered on material SDN addition event (distinct from list update). Independent of SRS.

```
SDN material addition (new entity added)
        ↓
  Batch job: query all disposed alerts from prior 90 days
        ↓
  For each disposed case: run JtD-4 disconfirmation logic
  against the new SDN entry only
        ↓
  Hit on previously-cleared case → set alert_status = REOPENED
  → push to analyst queue with RETROACTIVE_RESCREEN flag
  → log retroactive review record (required for FinCEN exam)
        ↓
  Complete within 10 business days; log completion
```

**Data architecture requirement (baked into Wave 1):** Disposition history must be queryable
by date range — the audit log already has `processed_at_utc` which supports this query.

**Prototype scope:** Retroactive review batch job is Wave 2.

---

### Requirement 4 — Span-level explainability on demand
**Status:** Largely compliant. Nomenclature fix only.

The existing output schema already provides span-level attribution:
- `patterns_detected[].evidence[]` — lists specific transactions by date/amount/channel
- `disposition.supporting_transactions[]` — lists transaction IDs driving the recommendation
- `disposition.reasoning` — names patterns, cites amounts, references watchlist resolution
- `watchlist_status.disconfirmation_evidence[]` — cites specific DOB/address/nationality factors

LACRA produces no aggregate "AML risk score" — every recommendation is evidence-grounded.
This satisfies the advisory's explicit standard by design.

**Spec amendment (Req 4):**

**AM-05:** Add one paragraph to Section 5 (Governance and Audit):

> "The full case package JSON — including `patterns_detected[].evidence[]`,
> `watchlist_status.disconfirmation_evidence[]`, `disposition.supporting_transactions[]`, and
> `disposition.reasoning` — constitutes the FIN-2026-A-008 Requirement 4 explainability
> record. On FinCEN examination, the case package JSON (retrievable by `audit_id`) provides
> the span-level attribution required. No additional explainability artifact is required."

---

### Requirement 5 — SAR-decision support boundary + 30-day clock
**Status:** Partially compliant. Nomenclature fix only.

LACRA cannot auto-file SARs (already the case — `ESCALATE_SAR` is a recommendation, not a
filing action). This part is compliant by design.

The gap: `generated_at_utc` is in the output schema and functions as the SAR clock T0, but
the spec never explicitly designates it as such. Without explicit designation, the institution
cannot demonstrate to FinCEN that the clock-start is architecturally enforced.

**Spec amendment (Req 5):**

**AM-06:** Add `sar_clock_start_utc` field to output schema (Section 4):
- For `ESCALATE_SAR` cases: `sar_clock_start_utc` = `generated_at_utc`
- For all other cases: `sar_clock_start_utc` = null

Add one sentence to Section 5 (Governance):
> "For cases where `disposition.recommendation = 'ESCALATE_SAR'`, `sar_clock_start_utc`
> designates the start of the 30-day FinCEN SAR-filing clock per FIN-2026-A-008 Requirement 5.
> The case management system must surface `sar_clock_start_utc` in the analyst queue view and
> alert at day 20 (10-day buffer for analyst review and SAR preparation)."

---

## 3. Delegation design — what changed

No change to the delegation archetypes or autonomy matrix. All five JtDs retain their
archetypes. All existing escalation triggers are unchanged.

One addition to escalation triggers:

| Trigger | Condition | Action |
|---|---|---|
| Sanctions list update (open case) | SRS detects WATCHLIST_UNRESOLVED on rescreen | Push to analyst queue with `PRIORITY_RESCREEN` flag; analyst reviews |
| Retroactive SDN hit | Previously-CLEAR case surfaces on retroactive rescreen | Reopen case; push to analyst queue with `RETROACTIVE_RESCREEN` flag |

Both new triggers route to analyst — consistent with the existing "agent proposes, human
approves" archetype for watchlist cases.

---

## 4. Economics impact

| New item | Wave | Build cost add | Annual run add |
|---|---|---|---|
| AM-03/04/05/06 (output + audit log field additions) | Wave 1 | +$10K | — |
| Alert status + SDN list version data architecture | Wave 1 | +$5K | — |
| Sanctions Rescreening Service (Req 2) | Wave 2 | +$30K | +$5K/yr |
| Retroactive Review Batch Job (Req 3) | Wave 2 | +$20K | +$2K/yr |
| Analyst action capture integration (case mgmt system) | Wave 2 | +$15K | — |
| **Total additions** | | **+$80K** | **+$7K/yr** |

Current approved build budget: $420K. Wave 1 additions ($15K) absorbed within existing
contingency. Wave 2 additions ($65K) require either: (a) $65K budget supplement, or (b)
reallocation from change management / training line ($30K) + minor scope deferral.

**Recommendation for Priya:** Approve Wave 1 additions immediately (within budget). Bring
Wave 2 $65K supplement to the board alongside the Wave 1 go-live ROI report. Wave 2 must
be live before the 90-day compliance deadline.

The ROI case is unchanged: $38.40/case saving, 8-month payback, $2.7M 3-year net. The
$65K Wave 2 add reduces 3-year net by $65K — immaterial.

---

## 5. What changes in the D#10 prototype

The prototype will demonstrate Requirement 1 and 5 compliance with the following additions
(all are output schema field additions — no pipeline logic change):

| Change | What to build |
|---|---|
| AM-03 (enhanced audit log) | Add `patterns_detected_summary`, `watchlist_resolution`, `supporting_transactions`, `sdn_list_version` to audit log output |
| AM-04 (`sdn_list_version`) | Add field to case package JSON; hardcode to mock SDN file date "2026-05-01" |
| AM-06 (`sar_clock_start_utc`) | Add field to case package JSON; set = `generated_at_utc` for ESCALATE_SAR, null otherwise |
| `alert_status` field | Add to case package JSON; hardcode to "OPEN" in prototype |

**Not in prototype (Wave 2):**
- Sanctions Rescreening Service
- Retroactive review batch job
- Analyst action feedback to audit record (requires case management system integration)

These are documented as known gaps (spec amendment note, Deliverable #11 if needed).

---

## 6. Summary of spec amendments

| ID | Section affected | Amendment |
|---|---|---|
| AM-01 | JtD-1a (scope detection) | Channel detection uses substring match `"remittance" in channel.lower()` (pre-build decision) |
| AM-02 | JtD-5 decision point 9 | "Both missing" = no data from any source; network file counts (pre-build decision) |
| AM-03 | Section 5.1 (audit log) | Enhanced schema with patterns summary, watchlist resolution, supporting transactions, analyst action fields, sdn_list_version |
| AM-04 | Section 4 (output schema) | Add `sdn_list_version` field |
| AM-05 | Section 5 (governance) | Designate full case package JSON as Req 4 FIN-2026-A-008 explainability record |
| AM-06 | Section 4 (output schema) + Section 5 | Add `sar_clock_start_utc` field; designate as 30-day SAR clock T0 for ESCALATE_SAR cases |
