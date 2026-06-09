# Deliverable 12 — Self-Assessment
**Gate 5b Final Exam · Lattice Pay AML/KYC Case Review Agent (LACRA)**
**Evaluated against:** design deliverables 1–9, prototype (`prototype/agent.py`, `tests.py`, `demo.py`)
**Test status at time of assessment:** T1–T13 all pass (13/13)

---

## 1. DELEGATION

**Are the human/agent boundaries justified? Could someone else clearly understand who does what?**

Yes — the boundaries are the strongest part of this package. The line is drawn consistently
across four independent locations:

1. `CLAUDE.md` guardrails ("NOT delegated — analyst/supervisor only")
2. Spec §1 "Not delegated to LACRA" section
3. Spec §3 JtD delegation archetypes (Fully Agentic → Agent-led + Human Oversight →
   Human-led + Agent Support, in that order across the 5 JtDs)
4. System prompt decision rules (ACCOUNT_FREEZE note: "freeze itself requires analyst →
   supervisor two-level approval")

The irreducible 10-minute analyst residual in JtD-5 is correctly justified: the agent
produces a *recommendation* with reasoning and confidence; the analyst decides and signs.
SAR filing, account freeze, and OFAC positive confirmation are all held back for documented
reasons (legal liability, two-level chain, compliance guardrail). These exclusions are not
arbitrary — each maps to a specific brief constraint.

**One gap:** When `watchlist_status.resolution = WATCHLIST_UNRESOLVED`, the spec says the
agent returns `FURTHER_INFO_NEEDED`, but doesn't specify who handles the resolution path
(analyst? compliance officer? escalation queue?). This is a production workflow gap, not a
prototype failure — acceptable at this stage.

**Overall: Clear. A new team member reading the spec would not confuse agent and analyst
responsibilities.**

---

## 2. AMBIGUITY

**Identify every statement that could be interpreted two ways.**

Four active ambiguities found; two previously identified have been resolved. Ranked by impact:

**Resolved:**

**A1 — Velocity anomaly: 90-day CSV vs. 12-month calculation** (§3 JtD-3c) — *resolved via AM-10*
The spec specified `prior_avg = total_cross_border_outbound_prior_12mo / 12` but the only
data available is a 90-day extract. AM-10 documents the substitution explicitly: `prior_avg =
total_cross_border_outbound_prior_60d / 2`, with a guard requiring `current_30d > $0` before
any evaluation. If `prior_60d = $0`, the rule notes "no prior cross-border baseline" in evidence
without creating a pattern entry. The system prompt enforces this. Production must still extend
to a 12-month data source; AM-10 documents the gap and the interim rule.

**A5 — Mixed remittance/in-scope case** (§1a second edge case) — *resolved via AM-11*
Spec described a case where primary transactions are in-scope but some use the remittance channel.
AM-11 implements direction-based logic: any OUTBOUND remittance transaction → OOS (customer is
using the product); inbound-only remittance → IN_SCOPE with a data_gaps note. This matches spec
intent and is exercised by T3 (pure OOS path intact).

**Active:**

**A2 — Rolling vs. fixed structuring window** (§3 JtD-3a) — *medium impact*
"≥3 transactions in a 10-day window" does not specify rolling or fixed-calendar. Rolling is
the correct AML interpretation; fixed would miss structuring straddling a boundary. The system
prompt delegates this to the model, which correctly uses rolling windows in T7. Spec is still
ambiguous — a production build should add explicit language.

**A3 — Watchlist confidence when hit_present = false** (§4) — *medium impact*
Schema says `"confidence: required if hit_present = true"` — implying omitted for NO_HIT.
But the JtD-4 logic example returns `"confidence": 1.0` for NO_HIT. Inconsistent. The prototype
follows the example (1.0), which is the correct behavior; the schema comment should be corrected.

**A4 — "Strong disconfirmation factor" label** (§3 JtD-4, DOB check) — *low impact*
Spec says DOB delta ≥5 years is a "strong disconfirmation factor" but counts it as one factor
toward the threshold like any other. The word "strong" is inconsistent with the flat counting
rule. A builder would correctly implement it as one factor; the language is just misleading.

**A6 — `triggered_at_utc` validation gap** (§2.1 vs. §6) — *low impact*
Input schema says `triggered_at_utc` is required, but `run_lacra()` only validates `alert_id`
and `customer_id`. If absent, `sar_clock_start_utc` would be `None` for SAR cases. Low risk for
prototype (callers always provide it); must be fixed and documented before production.

---

## 3. BUILDABILITY

**Could an AI coding agent build this without asking clarifying questions?**

Largely yes. The spec is concrete enough that the core paths (scope detection, pattern
detection, watchlist reconciliation, disposition decision tree) can be built without
clarification. The tool interfaces have complete Python type signatures and file path
patterns. The output schema is fully typed.

**Questions a builder would still ask:**

1. "Is the structuring window rolling or fixed-calendar?" (A2 — no answer in spec; builder
   would likely guess rolling, which is correct)

2. "Should I validate `triggered_at_utc` as required?" (A6 — inconsistency between schema
   and validation block)

3. "For the linked account KYC loop (AM-07 deferred) — should I write a stub that logs the
   skip, or omit the loop entirely?" The amendment note says "prototype omits this loop" but
   doesn't specify what the production Wave 1 build should do.

**Verdict:** 3 clarifying questions out of a 9-section spec and 5-JtD pipeline — high
buildability. The core paths are unambiguous. All gaps are edge cases or production-hardening
items that don't block a working prototype.

---

## 4. FAITHFULNESS

**Does the prototype implement what the spec describes? Where they differ, is there an amendment note?**

**Implemented faithfully (critical paths):**
- JtD-1a scope detection: `"remittance" in channel.lower()` substring match (AM-01) ✓
- JtD-1a mixed-remittance: direction-based rule, outbound → OOS, inbound-only → IN_SCOPE + note (AM-11) ✓
- JtD-1b data retrieval with per-source graceful degradation ✓
- JtD-2 narrative: four required questions, specific transaction citations required ✓
- JtD-3a–3e: all five pattern rules with correct thresholds ✓
- JtD-3c velocity guard: `current_30d > $0` required; `prior_60d / 2` proxy; zero-baseline noted (AM-10) ✓
- JtD-3f: MULTI_PATTERN_CONVERGENCE inherits highest constituent severity ✓
- JtD-4: four disconfirmation factors, threshold rules (≥3 → DISCONFIRMED conf 0.90+) ✓
- JtD-4 NO_SCREENING_DATA: absent watchlist = NO_SCREENING_DATA, not NO_HIT ✓
- JtD-4 output template: all four resolution values in JSON schema and HARD CONSTRAINT ✓
- JtD-5: 9-priority decision tree in exact spec order ✓
- AM-04 `sdn_list_version` = "2026-05-01" ✓
- AM-06 `sar_clock_start_utc` = `triggered_at_utc` for ESCALATE_SAR ✓
- AM-06 `alert_status` = "OPEN" ✓
- AM-03 enhanced audit log schema (6 additional fields) ✓
- Input validation (MISSING_REQUIRED_FIELD), retry logic (once, 5-sec backoff) ✓
- `temperature=0`, `model="claude-sonnet-4-6"`, `agent_version="LACRA-1.0"` ✓

**Divergences with amendment notes (acceptable):**
- AM-07: Linked account KYC loop not implemented; relies on network file being self-contained ✓
- AM-08: Transaction row truncation (500 rows) and network account cap (10) not enforced in
  prototype; no mock file exceeds limits; required for production ✓
- AM-09: `monetary_scope_usd` and `analyst_queue_tag` accepted but unused ✓
- AM-10: Velocity rule uses 90-day proxy for 12-month spec calculation; documented ✓
- AM-11: Mixed-remittance direction-based rule; extends spec §1a intent; documented ✓

**Residual divergences without amendment notes:**

**R3 — `triggered_at_utc` not validated**
Spec §2.1 says required; `run_lacra()` only validates `alert_id` and `customer_id`. No
amendment note. Low risk for prototype; must be fixed before production.

**Overall faithfulness: Strong across all 8 tested paths. One minor residual divergence (R3)
does not affect any tested path and carries low production risk.**

---

## 5. ECONOMICS

**Does the implicit cost model make sense? Are you automating the right things?**

**Automating the right things:** Yes.

The 58-minute case decomposition maps directly to the automation strategy:
- JtD-1 (data assembly, 15 min) → 100% automated. Pure I/O with no judgment component.
  Automating this is unambiguously correct.
- JtD-2 (narrative, 10 min) → 90% automated. The 2-minute residual is analyst
  comprehension — healthy.
- JtD-3 (pattern detection, 12 min) → 88% automated. The 3-minute residual is analyst
  verification of evidence. Correct — the analyst should spot-check the hop chain.
- JtD-4 (watchlist reconciliation, 8 min) → 63% automated. The 3-minute residual for
  watchlist factor verification is appropriate given OFAC consequences.
- JtD-5 (disposition recommendation, 13 min) → 23% automated. The 10-minute residual is
  irreducible analyst judgment and sign-off. Removing this would shift legal and regulatory
  liability to the agent — the correct design choice.

**Cost arithmetic is correct:**
- Token cost per case ($0.054) is accurate for claude-sonnet-4-6 at $3/$15 per 1M tokens
  with 8K input + 2K output.
- Annual model cost ($3,602 at 66,703 cases) is 0.1% of the baseline $3.72M headcount cost.
  Model cost is economically irrelevant — analyst time dominates.
- $420K build estimate is detailed and plausible for the scope described.

**Primary economic claim (Scenario B) is honest:** Throughput triples (3.2×) at same
headcount; cycle time drops from 6.2 days to ~1.9 days (meeting the 2.5-day target). This
is the operationally honest case — no mass layoffs assumed, just queue clearance. Priya Rao's
stated concern (regulatory SLA risk from 6.2-day cycle) is directly addressed.

**One remaining concern:** AM-10 documents the 90-day proxy for the velocity anomaly
calculation, but the economics don't model the cost of extending the transaction data pipeline
to 12-month history. If velocity anomaly is a significant detection signal at scale, a data
pipeline extension would be a Wave 1 budget item. This should be surfaced in the Wave 1
planning conversation, not treated as a free assumption.

**Overall: Sound. Conservative assumptions, honest about non-quantified value, sensitivity
analysis covers the range of realistic outcomes.**

---

## 6. VALIDATION

**Are the failure modes covered? How will you know if this worked?**

**Test coverage — 13 paths, all passing:**

| Test | Customer | Path | Disposition | Data source |
|---|---|---|---|---|
| T1 | C-CON-9923441 | Watchlist FP Mohammed Khan → CLEAR | `CLEAR` | Real mock |
| T2 | C-CON-6611442 | Layering across 4 linked accounts | `ESCALATE_SAR` | Real mock |
| T3 | C-CON-5530118 | OOS remittance routing | `ROUTE_OUT_OF_SCOPE` | Real mock |
| T4 | C-CON-0000001 | No data, synthetic customer | `FURTHER_INFO_NEEDED` | Synthetic |
| T5 | C-CON-9923441 | Reproducibility (T1 re-run) | Identical decision fields | Real mock |
| T6 | C-TEST-T6 | Thin-KYC tier-1 aggregate breach | `ACCOUNT_FREEZE` | Synthetic |
| T7 | C-TEST-T7 | Structuring MEDIUM (3 transactions) | `CUSTOMER_RFI` | Synthetic |
| T8 | C-TEST-T8 | Watchlist UNRESOLVED (1 factor) | `FURTHER_INFO_NEEDED` | Synthetic |
| T9 | C-CON-7714290 | Structuring HIGH, owner-operator trucker | `ESCALATE_SAR` | Real mock |
| T10 | C-CON-3318822 | Counterparty risk, vape shop, prior RFI | `CUSTOMER_RFI` | Real mock |
| T11 | C-CON-2207715 | Watchlist FP Gonzalez/Alava, Tampa nurse | `CLEAR` | Real mock |
| T12 | C-BIZ-4408821 | Cayman offshore wire-outs, 100% concentration | `ESCALATE_SAR` | Real mock |
| T13 | C-CON-7720338 | Thin-KYC + structuring HIGH, MPC HIGH | `ESCALATE_SAR` | Real mock |

All 8 real mock customers from the queue are exercised. T4 (no-data graceful degradation)
and T6–T8 (isolated disposition paths) use synthetic data via `unittest.mock.patch`.

**Critical failure mode coverage:**
- False negative on genuine SAR (clear a layering case) → T2 catches this ✓
- False positive on watchlist (escalate a common-name FP) → T1, T11 catch this ✓
- Agent processes out-of-scope case → T3 catches this ✓
- Agent crashes on missing data → T4 catches this ✓
- Non-reproducible output → T5 catches this ✓
- Agent misclassifies thin-KYC breach as lower-priority → T6 catches this ✓
- Agent over-escalates MEDIUM structuring → T7 catches this ✓
- Agent clears an unresolved watchlist hit → T8 catches this ✓
- Agent misses structuring on cash-deposit pattern despite prior no-SAR → T9 catches this ✓
- Agent escalates routine counterparty activity when RFI explanation is on file → T10 catches this ✓
- Agent misses offshore wire-out counterparty risk on shell LLC → T12 catches this ✓
- Agent misses co-occurring thin-KYC + structuring on new P2P-funded account → T13 catches this ✓

**T5 scope is correct:** Reproducibility is validated on structural decision fields
(`scope_classification`, `disposition.recommendation`, `watchlist_status.resolution`,
`pattern_type`/`severity` per pattern). Prose fields (`narrative`, `reasoning`) are
excluded — minor character-level variation at temperature=0 is acceptable per spec §5.3
and FinCEN requirements (reproducibility is about decisions, not verbatim prose).

**T10 assertion design note:** C-CON-3318822's pattern detection is marginal (the model
produces COUNTERPARTY_RISK LOW or MPC LOW across runs, depending on how it reads the
elevated-risk merchant alert trigger vs. the RFI explanation). The test asserts only the
disposition (`CUSTOMER_RFI`) and the negative (no STRUCTURING), not the specific pattern
type — this is correct for a case where the signal is genuinely ambiguous.

**Untested paths (acceptable gaps):**
- Broker-dealer OOS routing — spec covers it; not tested
- Input validation error (missing `alert_id`) — not tested

**Production validation plan (spec §6 monitoring):** Concrete and measurable — monthly recall
tracking, precision tracking, override rate monitoring, reproducibility audit sample. These
tie directly back to Dr. Rao's KPIs (≥95% recall, ≥75% precision). This is the right level
of specificity for a production deployment decision.

---

## 7. SCORE

**Rating: 92 / 100**

**Rationale:**

This is a production-grade design with strong internal consistency, a complete amendment
register, and 8-path test coverage across all five disposition types. The score reflects
the package as it stands after a build-phase audit that identified and resolved its own gaps.

**What earns the high score:**
- Delegation boundaries are precise and documented in 4 independent locations — no
  ambiguity about what the agent does.
- The spec is concrete enough to build from without clarifying questions on the core paths.
- Amendment register (AM-01 through AM-11) is explicit about every divergence with
  rationale — no silent omissions. Three divergences were fixed during build (3f severity,
  NO_SCREENING_DATA, sar_clock source); four more were identified via self-assessment and
  resolved (AM-10 velocity proxy, output template, AM-11 mixed-remittance, T6/T7/T8 tests).
- Economics is honest: Scenario B (throughput gain, same headcount) is the primary claim,
  not the theoretical ceiling of Scenario A.
- All 8 test cases pass with correct assertions for structural fields, not just smoke tests.
- Two previously unimplemented spec requirements (velocity proxy, mixed-remittance) are now
  both implemented and documented, not silently deferred.

**What holds it below 95:**

1. **`triggered_at_utc` validation gap (A6/R3).** Listed as required in §2.1; not validated
   in `run_lacra()`; no amendment note. If absent, `sar_clock_start_utc` would be `None`
   for SAR cases despite spec requiring it. Low risk for prototype (callers always provide it),
   but this is a spec-to-code inconsistency that a production hardening pass must close.
   Minus 2 points.

2. **Structuring window ambiguity unresolved in spec (A2).** The spec does not say "rolling"
   vs. "fixed-calendar" window. The model uses rolling (correct AML interpretation), but the
   spec should say so explicitly. A builder following the spec literally could go either way.
   Minus 2 points.

3. **12-month velocity data pipeline not modeled in economics.** AM-10 correctly documents the
   90-day proxy and flags the production requirement, but the economics sketch doesn't include
   a line item for the data pipeline extension. A Wave 1 plan built from this package would
   discover a budget item that isn't in the ROI model. Minus 1 point.

4. **Watchlist confidence schema inconsistency (A3).** Schema says confidence is omitted when
   `hit_present = false`; logic example shows 1.0. Prototype follows the example (correct
   behavior), but the spec has contradictory guidance. Minus 1 point.

**Final: 92/100 — Strong pass. The package meets production-grade standards for the scope
claimed. Deductions are all minor production-hardening and spec-clarification items; none
affect any tested decision path. A Wave 1 handoff from this package requires: (1) add
`triggered_at_utc` validation with an amendment note, (2) confirm 12-month transaction data
pipeline availability or budget it, (3) clarify rolling-window language in the spec.**
