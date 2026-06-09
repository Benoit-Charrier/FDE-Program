# Deliverable 6 — Validation Plan
**Gate 5b Final Exam · Lattice Pay AML/KYC Case Review Agent (LACRA)**

---

## Overview

Three test paths are required per the exam rules: (1) primary agentic flow (happy path),
(2) failure-mode escalation, (3) edge case. This plan covers all three plus two additional
scenarios for robustness. Each test specifies concrete inputs, expected outputs, and
pass/fail criteria.

---

## Test 1 — Primary flow: Common-name watchlist false-positive (AML-1208)

**Purpose:** Validate the end-to-end happy path — alert ingested, data retrieved, narrative
produced, watchlist false-positive correctly disconfirmed, clean disposition returned.

**Input:**
```json
{
  "alert_id": "CASE-2026-05-13-AML-1208",
  "customer_id": "C-CON-9923441",
  "triggered_at_utc": "2026-05-13T09:38:00Z"
}
```

**Data available:** KYC (tier-3, Pakistani passport, F-1 student), 90-day tx history (stipend
ACH + utility bills + P2P to roommate), watchlist screening (hit on KHAN Muhammad, score 0.74),
OFAC SDN extract (DOB 1972, Karachi Pakistan, SDGT).

**Expected output:**
- `scope_classification`: `IN_SCOPE`
- `narrative`: references Wayne State stipend, bill payments, P2P transfers to identified
  counterparties; characterises as student wallet
- `patterns_detected`: empty array (no structuring, no layering, no velocity anomaly)
- `watchlist_status.resolution`: `WATCHLIST_DISCONFIRMED`
- `watchlist_status.disconfirmation_evidence`: must include all three of:
  1. DOB delta ≥ 21 years (1993 vs 1972)
  2. Address mismatch (Detroit MI vs Karachi Pakistan)
  3. Transaction profile consistent with F-1 student
- `watchlist_status.confidence`: ≥ 0.9
- `disposition.recommendation`: `CLEAR`
- `disposition.confidence`: ≥ 0.90
- `data_gaps`: empty or minimal

**Pass criteria:**
- `disposition.recommendation = "CLEAR"` ✓
- `watchlist_status.resolution = "WATCHLIST_DISCONFIRMED"` ✓
- All three disconfirmation evidence items present ✓
- `narrative` cites at least two specific transactions with amounts ✓
- `sar_clock_start_utc` is null (no SAR clock for CLEAR cases — AM-06) ✓
- Processing completes within 60 seconds ✓

**Fail criteria:**
- Any output of `ESCALATE_SAR` or `ACCOUNT_FREEZE` = automatic fail (false positive, customer harm)
- `WATCHLIST_UNRESOLVED` without uncertainty flag = spec violation
- Narrative contains no specific transaction citations = quality fail

---

## Test 2 — Failure-mode escalation: Layering across linked accounts (AML-1408)

**Purpose:** Validate the escalation path — layering pattern detected, high-confidence
ESCALATE_SAR recommendation returned with full evidence chain.

**Input:**
```json
{
  "alert_id": "CASE-2026-05-15-AML-1408",
  "customer_id": "C-CON-6611442",
  "triggered_at_utc": "2026-05-15T02:55:00Z"
}
```

**Data available:** Network file (4 linked accounts, shared device fingerprint dev-android-7011,
all opened March 2026, transfer chain → Eastside FCU → Tyrone Ostrander Personal); KYC for
primary account only; transaction summary in network file.

**Expected output:**
- `scope_classification`: `IN_SCOPE`
- `patterns_detected`: must include at minimum:
  - `LAYERING` with severity HIGH, evidence showing the hop chain
    (6611442 → 6611445 → 6611448 → 6611449 → Acct_5511720)
  - `MULTI_PATTERN_CONVERGENCE` is acceptable if additional patterns noted
- `patterns_detected[LAYERING].evidence`: must cite at least the 4-hop chain with amounts
- `disposition.recommendation`: `ESCALATE_SAR`
- `disposition.confidence`: ≥ 0.85
- `disposition.reasoning`: must reference shared device fingerprint, account opening dates,
  and external convergence point
- `data_gaps`: must list the 3 linked accounts with no KYC files
  (C-CON-6611445, C-CON-6611448, C-CON-6611449)

**Pass criteria:**
- `disposition.recommendation = "ESCALATE_SAR"` ✓
- Layering pattern with severity HIGH present in `patterns_detected` ✓
- Hop chain cited in evidence (all 4 accounts + external endpoint) ✓
- `data_gaps` lists the 3 missing linked KYC files (graceful degradation) ✓
- `disposition.reasoning` references shared device fingerprint ✓
- `sar_clock_start_utc` is set to `triggered_at_utc` value (30-day FinCEN SAR-filing clock — AM-06) ✓

**Fail criteria:**
- `disposition.recommendation = "CLEAR"` or `"CUSTOMER_RFI"` = SAR recall failure
- Layering pattern absent from `patterns_detected` = pattern detection failure
- Missing `data_gaps` entry for linked accounts = spec faithfulness failure

---

## Test 3 — Edge case: Out-of-scope routing (AML-1322)

**Purpose:** Validate that a cross-border remittance alert is detected as out-of-scope and
routed before analysis begins. Agent must not analyse a case it is not authorised to assess.

**Input:**
```json
{
  "alert_id": "CASE-2026-05-14-AML-1322",
  "customer_id": "C-CON-5530118",
  "triggered_at_utc": "2026-05-14T18:08:00Z"
}
```

**Data available:** Transaction history showing cross-border transfers via remittance product
(channel = `"cross-border-remittance"` in CSV — AM-01: scope detection uses substring match
`"remittance" in channel.lower()`, not exact equality).

**Expected output:**
```json
{
  "scope_classification": "OUT_OF_SCOPE_REMITTANCE",
  "routing": {
    "destination": "Cross-Border Remittance Review Team",
    "reason": "Alert involves Lattice Pay remittance product transactions"
  },
  "disposition": { "recommendation": "ROUTE_OUT_OF_SCOPE" },
  "narrative": null,
  "patterns_detected": null
}
```

**Pass criteria:**
- `scope_classification = "OUT_OF_SCOPE_REMITTANCE"` ✓
- `disposition.recommendation = "ROUTE_OUT_OF_SCOPE"` ✓
- `routing.destination` references the remittance team ✓
- No narrative, no pattern detection, no watchlist check performed ✓
- Processing halts at JtD-1 scope detection zone (no further tool calls) ✓

**Fail criteria:**
- Any `patterns_detected` array or narrative generated = spec violation (agent processed
  out-of-scope case instead of routing)
- `disposition.recommendation` ≠ `ROUTE_OUT_OF_SCOPE` = automatic scope boundary failure

---

## Test 4 — Edge case: Missing data graceful degradation

**Purpose:** Validate that the agent handles a case where both KYC and transaction history
are completely absent — no files exist for the customer — and returns `FURTHER_INFO_NEEDED`
without crashing.

**Input:**
```json
{
  "alert_id": "CASE-TEST-MISSING-DATA",
  "customer_id": "C-CON-0000001",
  "triggered_at_utc": "2026-05-15T00:00:00Z"
}
```

*(Synthetic customer ID — no files exist for `C-CON-0000001` in any mock-data directory.
No temporary file deletion required; the fixture is self-contained and deterministic.)*

**Data available:** None — all tool calls return `None`. KYC absent, transaction history
absent, watchlist screening absent, network file absent, RFI history absent.

**Expected output:**
- `disposition.recommendation`: `FURTHER_INFO_NEEDED`
- `data_gaps`: ≥2 items (KYC profile absent + transaction history absent at minimum)
- No `"error"` key in the response

**Pass criteria:**
- `disposition.recommendation = "FURTHER_INFO_NEEDED"` ✓
- `data_gaps` has ≥2 items ✓
- No `"error"` key in response (agent degrades gracefully, does not crash) ✓

**Fail criteria:**
- Agent crashes or returns `{"error": ...}` = graceful degradation failure
- `disposition.recommendation = "CLEAR"` with no data = spec faithfulness failure

---

## Test 5 — Reproducibility

**Purpose:** Validate that identical inputs produce identical outputs on re-run (100%
reproducibility requirement for FinCEN audit).

**Method:** Run Test 1 (AML-1208) twice in sequence. Capture both output JSONs.
Diff the two outputs.

**Pass criteria:**
- `scope_classification` identical across both runs ✓
- `disposition.recommendation` identical ✓
- `watchlist_status.resolution` identical ✓
- All `pattern_type` and `severity` values identical ✓
- Fields legitimately excluded from comparison (vary by design): `generated_at_utc`,
  `sar_clock_start_utc`, `_audit_log`

**Fail criteria:**
- `disposition.recommendation` differs between runs = reproducibility failure
- `watchlist_status.resolution` differs between runs = reproducibility failure
- Any `pattern_type` or `severity` differs between runs = reproducibility failure

*Note: `disposition.reasoning` and `narrative` prose may have minor character-level
variation at the API level even at temperature=0 — this is acceptable. Reproducibility
is defined over structural decision fields, not verbatim prose.*

---

## Test coverage matrix

| Test | Alert type | Expected disposition | Validates |
|---|---|---|---|
| T1 | Watchlist FP (student wallet) | `CLEAR` | Happy path, watchlist disconfirmation |
| T2 | Layering (4 linked accounts) | `ESCALATE_SAR` | Failure escalation, network analysis |
| T3 | Remittance boundary | `ROUTE_OUT_OF_SCOPE` | Scope detection, out-of-scope routing |
| T4 | No data at all (synthetic C-CON-0000001) | `FURTHER_INFO_NEEDED` | Graceful degradation, data gaps |
| T5 | Same as T1 (re-run) | Identical to T1 | Reproducibility (FinCEN requirement) |

---

## Failure mode coverage

| Failure mode | Covered by | Expected behaviour |
|---|---|---|
| False negative on genuine SAR (clear a layering case) | T2 | ESCALATE_SAR required |
| False positive on watchlist (escalate a common-name FP) | T1 | CLEAR required |
| Out-of-scope case processed | T3 | ROUTE_OUT_OF_SCOPE, halt analysis |
| Missing data causes crash | T4 | FURTHER_INFO_NEEDED, graceful degrade |
| Non-reproducible output | T5 | Identical outputs on re-run |
| OFAC positive confirmation by agent | T1 (implicit) | WATCHLIST_DISCONFIRMED only — never CONFIRMED |

---

## Production validation (post-prototype)

Once in production, the following ongoing validation applies:

1. **Monthly retrospective:** For every case where LACRA recommended `CLEAR` and a SAR was
   subsequently filed (analyst override), classify as recall failure. Track recall rate vs ≥95% target.
2. **Precision tracking:** For every `ESCALATE_SAR` recommendation, track whether analyst
   confirmed SAR. Track precision rate vs ≥75% target.
3. **Override rate monitoring:** High override rate on any disposition type triggers a spec review.
4. **Reproducibility audit sample:** Monthly: re-run 10 randomly selected closed cases through
   LACRA; confirm output matches the original case package.
