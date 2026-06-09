# Deliverable 11 — Supplementary Spec Amendment Note
## Build-Phase Gaps and Revised Spec Language
**Gate 5b Final Exam · Build phase (14:00–17:00 CET)**

This note documents spec gaps discovered during prototype implementation (AM-07 through AM-11)
and one correction to a curveball amendment (AM-06 correction). All are silent-divergence
risks without this note. The original spec (D05) and curveball amendments (D09) remain
unchanged; this document extends them.

---

## AM-06 Correction — SAR clock T0 field

**Affected:** D09 Section 5 (prototype change table) and Section 6 (amendment summary).

D09 specified: `sar_clock_start_utc = generated_at_utc` for ESCALATE_SAR cases.

**Correction:** The prototype implementation sets `sar_clock_start_utc = triggered_at_utc`
(the alert trigger timestamp from the input, not the agent's `generated_at_utc`).

**Why it matters:** FinCEN's 30-day SAR-filing clock begins when the institution **detects**
the suspicious activity — i.e., when the alert fires — not when the agent processes it. Cases
can sit in queue for hours or days before LACRA runs. Using `generated_at_utc` would
systematically undercount elapsed days and potentially mask overdue SARs in the analyst queue.

**Revised spec language (D05 Section 4 output schema):**
> "`sar_clock_start_utc`: ISO 8601 UTC timestamp. For `ESCALATE_SAR` cases, set to the
> `triggered_at_utc` value from the alert input — the timestamp at which the alert was
> originally detected. For all other cases, null. Using the alert-trigger timestamp ensures the
> 30-day FinCEN SAR-filing clock is measured from detection, not from agent processing time."

---

## AM-07 — Linked account KYC retrieval loop not implemented

**Affected:** D05 Section 3.2 (JtD-2, data ingestion for network cases).

The spec implies that for network-analysis cases, KYC profiles for each linked account should
be fetched via `read_kyc(linked_account_id)`. The prototype does not implement this loop —
the network file (`C-CON-6611442_linked_network.json`) is self-contained and includes all
relevant account attributes inline, so the prototype produces correct output without the loop.

**Gap:** If a production network file contains account IDs but not full KYC attributes, the
agent will proceed with partial data and may miss risk signals on linked entities.

**Revised spec language (D05 Section 3.2, JtD-2):**
> "For network-analysis cases where `read_network()` returns a non-null result, the agent must
> attempt `read_kyc()` for each account in the network's `accounts[]` list (up to 10 accounts
> per AM-08 cap). KYC results for linked accounts are appended to the data context. If
> `read_kyc()` returns null for a linked account, record the missing account ID in `data_gaps[]`
> and continue."

**Prototype status:** Not implemented. Network file is self-contained for all current mock
cases. Production Wave 1 must implement the loop.

---

## AM-08 — Transaction row truncation and network account cap not enforced

**Affected:** D05 Section 3.2 (data ingestion guards).

The spec references a 500-row cap on transaction history and a 10-account cap on network files
to prevent prompt-context overflow. Neither guard is implemented in the prototype.

**Gap:** No current mock file exceeds either limit, so tests pass. Production files from
high-volume business accounts (e.g., C-BIZ-4408821 with 50+ transactions/month) could exceed
500 rows within 90 days. Exceeding the context limit would cause the API call to fail or
silently truncate data.

**Revised spec language (D05 Section 3.2):**
> "Before passing transaction history to the model context, truncate to the 500 most recent
> rows (sorted descending by transaction date). If truncation occurs, record
> `'Transaction history truncated to 500 most recent rows (total: N)'` in `data_gaps[]`.
> Before passing network data, cap the `accounts[]` list to the 10 highest-degree nodes.
> These guards must be applied in the data ingestion stage, before the API call."

**Prototype status:** Guards absent. No mock file exceeds limits. Production Wave 1 must add
pre-processing step.

---

## AM-09 — `monetary_scope_usd` and `analyst_queue_tag` accepted but unused

**Affected:** D05 Section 2.1 (input schema).

The spec defines `monetary_scope_usd` and `analyst_queue_tag` as optional input fields but
does not specify how the agent should use them. The prototype accepts them without error but
passes them through to the model context without any routing logic.

**Gap:** `analyst_queue_tag = "High"` is intended to signal priority routing, but the
prototype never reads or acts on this field.

**Revised spec language (D05 Section 2.1 and Section 3.5, JtD-5):**
> "`analyst_queue_tag`: If `'High'`, the agent must set `disposition.priority = 'HIGH'` in
> the output regardless of pattern severity. This field represents a pre-classification signal
> from the alert-generation system that the case warrants expedited analyst review. The agent
> should not override or second-guess this tag.
>
> `monetary_scope_usd`: Include in the narrative summary and `_audit_log.monetary_scope_usd`
> for case package completeness. Does not alter pattern detection logic."

**Prototype status:** Both fields silently unused. Production Wave 1 must implement the
priority routing for `analyst_queue_tag`.

---

## AM-10 — Velocity anomaly uses 90-day extract as 12-month proxy

**Affected:** D05 Section 3.3 (JtD-3c, velocity anomaly detection).

The spec requires comparison of current-month inbound volume against a 12-month prior average.
The prototype only has access to a 90-day transaction extract. The proxy used:
`prior_60d_total / 2` as an estimated monthly baseline for the prior period.

**Additional guard not in original spec:** If `prior_60d_total = 0` (no transactions in the
prior 60-day window), the agent flags `"No prior baseline: velocity anomaly cannot be
computed"` at MEDIUM severity rather than dividing by zero or silently skipping the check.
Guard: `current_30d_total > 0` is required before evaluation — a current period of zero
inbound activity does not trigger velocity anomaly.

**Revised spec language (D05 Section 3.3, JtD-3c):**
> "Velocity anomaly check requires a 12-month prior average. Where only a 90-day extract is
> available, substitute `prior_60d_total / 2` as the estimated monthly baseline (days 31–90
> of the extract). If `prior_60d_total = 0`, record `'No prior baseline available: velocity
> anomaly indeterminate'` in `data_gaps[]` and flag MEDIUM severity. Do not evaluate velocity
> anomaly if `current_30d_total = 0`. Production must extend to a 12-month data source."

**Prototype status:** Proxy implemented with guard. Produces correct results on all mock data.

---

## AM-11 — Mixed remittance scope detection uses direction-based rule

**Affected:** D05 Section 3.1 (JtD-1a, scope classification) and AM-01 (channel substring
match).

The original spec (AM-01) routes any case where the channel contains `"remittance"` to
`OUT_OF_SCOPE`. The curveball scenario (C-CON-5530118) has only OUTBOUND remittance-channel
transactions, so the original rule produced the correct result.

**Gap discovered during build:** A customer with both INBOUND and OUTBOUND remittance-channel
transactions (e.g., a worker receiving remittances from overseas while also sending them) would
be incorrectly routed entirely OOS under the original rule, losing AML coverage on the
in-scope INBOUND transactions.

**Revised rule:**

| Transaction direction | Channel contains "remittance" | Routing |
|---|---|---|
| OUTBOUND | Yes | `OUT_OF_SCOPE` — route to remittance team |
| INBOUND | Yes | `IN_SCOPE` — flag `data_gaps: "Inbound remittance-channel transactions: cross-border remittance team should be notified"` |
| Mixed (both) | Yes | `IN_SCOPE` — process INBOUND only; OUTBOUND transactions excluded from pattern analysis; `data_gaps` note added |

**Revised spec language (D05 Section 3.1, JtD-1a):**
> "Remittance channel check: if any OUTBOUND transaction has a channel containing
> `'remittance'` (case-insensitive), classify the case `OUT_OF_SCOPE` with routing destination
> `cross-border-remittance`. If INBOUND-only remittance-channel transactions are present,
> classify `IN_SCOPE`, add a `data_gaps` note that the remittance team should be informed of
> the inbound activity, and exclude remittance-channel transactions from pattern detection.
> This direction-based rule prevents mixed-profile customers from being entirely removed from
> AML scrutiny due to incidental remittance-channel INBOUND activity."

**Prototype status:** Direction-based rule implemented. C-CON-5530118 (OUTBOUND only) still
routes OOS correctly. Mixed-profile case now routes IN_SCOPE with data gap note.

---

## Summary table

| ID | Category | Affected spec section | Prototype status | Production action |
|---|---|---|---|---|
| AM-06 correction | Compliance field semantics | D05 §4 output schema | `triggered_at_utc` (correct) | D09 text must be updated |
| AM-07 | Missing feature — linked KYC loop | D05 §3.2 JtD-2 | Not implemented | Wave 1 required |
| AM-08 | Missing guard — data truncation | D05 §3.2 ingestion | Not implemented | Wave 1 required |
| AM-09 | Undefined field behaviour — queue tag | D05 §2.1 input schema | Silently unused | Wave 1 required |
| AM-10 | Rule substitution — velocity proxy | D05 §3.3 JtD-3c | Proxy with guard | Production: 12-month source |
| AM-11 | Rule correction — mixed remittance | D05 §3.1 JtD-1a | Direction-based rule | Correct as-built |

**AM-07, AM-08, AM-09** are prototype-only gaps that do not affect test correctness (mock
data is self-contained and within limits). All three are Wave 1 production requirements.

**AM-10, AM-11** are rule refinements where the prototype implements the correct production
behaviour. The spec needed updating to match.

**AM-06 correction** is a FinCEN compliance correctness fix. The prototype is correct;
the D09 amendment text was imprecise.
