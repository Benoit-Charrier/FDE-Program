# Build Loop Diagnosis
## FNOL Processing Agent — Gate 1 Validation Run

**Run date:** 2026-04-27  
**Agent version:** fnol-agent-v1.0.0  
**Test suite:** D4 Validation Design — 5 scenarios (6 sub-cases)  
**Final results:** 24 pass / 5 fail / 5 informational

---

## Summary

Four separate failures surfaced during the test run. Two were fixed during the loop; one is an open design gap requiring client input before it can be resolved; one is a deliberate infrastructure gap outside the Phase 1 console scope. Each is classified below using the taxonomy from `spec-ambiguity-vs-builder-mistakes.md`.

---

## Finding 1 — Coverage status check does not gate routing

**Category: Builder Misread (Category 2)**

**What broke:** The original `run()` function always proceeded to Step 7 (adjuster routing) regardless of the coverage validation outcome. When Scenario 3 produced `coverage_status = UNCERTAIN`, the code set that status correctly, then immediately overwrote it with `"ROUTING"` and assigned an adjuster. The claim reached `COMPLETED` with an unresolved coverage dispute — a dangerous incorrect outcome.

**Why:** The spec is unambiguous. D2 defines Step 3's input as `"ClaimRecord (COVERAGE_CONFIRMED)"`, and D3 REQ-6 states: `"Routing is triggered by transition to COVERAGE_CONFIRMED."` The code executed routing unconditionally, ignoring the pre-condition entirely.

**Classification: builder misread.** The spec explicitly names `COVERAGE_CONFIRMED` as the routing trigger. A sentence in D2 directly refutes the original implementation. There is no defensible interpretation of D2 that permits routing a `COVERAGE_DISPUTED` claim to an adjuster.

**Fix applied:** Added a coverage gate in `run()`: Step 7 only executes when `coverage_status == "COVERED"`. All other coverage states log a SKIPPED outcome and leave `assigned_adjuster_id = None`.

---

## Finding 2 — Exclusion candidates filtered too narrowly (silent data loss)

**Category: Builder Misread (Category 2)**

**What broke:** The exclusion candidate check in `step_validate_coverage()` was:

```python
exclusion_candidates = [e for e in exclusions if claim_type.lower() in e.lower()]
```

Scenario 3's exclusion clause, `"Clause 14.3: Damage arising from gradual deterioration or wear and tear"`, does not contain the word `"property"`, so it was silently dropped. The specialist would have received no exclusion signal — the exact failure mode D4 Scenario 3 was designed to catch.

**Why:** D2 tier 2.5 says: `"Apply coverage exclusions check — AGENT_REVIEW if exclusion_candidates ≥ 1."` It does not say only surface exclusions that mention the claim type by name. Policy exclusion clauses are written in legal language and do not use the claim type enum as a keyword. The filtering logic was a builder assumption with no basis in the spec.

**Classification: builder misread.** The spec required surfacing exclusions for specialist review. The code silently discarded them. This contradicts an explicit requirement, not an ambiguous one.

**Fix applied:** Changed to `list(exclusions)` — all policy exclusions are candidate flags for specialist review.

---

## Finding 3 — PROPERTY keyword classifier misses standard vocabulary (Scenario 3)

**Category: Builder Misread (Category 2)**

**What broke:** Scenario 3's claim — "damp and water staining on the living room ceiling... a slow leak from the bathroom above" — produced `claim_type = OTHER`. The classifier returned OTHER because none of the PROPERTY keywords matched. `claim_type = OTHER` then produced `coverage_match_confidence = 0.40` (no coverage match), which triggered `COVERAGE_DISPUTED` rather than `COVERAGE_PENDING_REVIEW`. Two downstream checks cascaded from one upstream misclassification.

**Why:** The PROPERTY keyword list omitted standard water damage vocabulary. "damp", "leak", "ceiling", "pipe" are unambiguously property domain terms, but were not in the initial list. The spec (D3 §4.3) says the classifier should handle all claim types including property water damage. The keyword set was too narrow to implement that requirement.

**Classification: builder misread.** The spec was clear that PROPERTY classification must work for water damage claims. The keyword list simply didn't cover the vocabulary. No spec ambiguity — it was an incomplete implementation.

**Fix applied:** Added `"damp"`, `"leak"`, `"leaking"`, `"ceiling"`, `"pipe"`, `"plumbing"`, `"wall damage"` to the PROPERTY keyword list.

---

## Finding 4 — Severity model has no sub-bracket at £10,000 (Scenario 2B)

**Category: Design Gap (Category 4)**

**What broke:** Scenario 2B (£10,200 motor claim) produced `severity = MEDIUM, score = 50` — identical to Scenario 2A (£9,800). The D4 pass criterion requires `severity = HIGH, score ≥ 60` for the £10,200 case. The test failed. The D2 boundary between tier 1.3 (AGENT_LOG) and tier 1.4 (AGENT_REVIEW) sits at `severity_score = 60`, which corresponds to a claim value around £10,000. The current scoring uses a single bracket for the entire £5,000–£15,000 range, assigning score 45 to every claim in that band regardless of where within it the value falls.

**Why:** D3 §4.4 specifies a severity scoring formula with value-based bands and a threshold at £10,000 for AGENT_REVIEW. The formula as written cannot produce a score of 59 for £9,800 and 61 for £10,200 using a single bracket — it would require a sub-bracket split at £10,000. The spec did not define the sub-bracket explicitly, and the builder implemented a simpler set of bands that cannot differentiate values within the same bracket.

**Classification: design gap.** The spec stated the desired outcome (threshold at score 60 / £10k) but did not provide a scoring formula precise enough to produce that outcome. The builder built a valid severity scoring model; it just doesn't produce the exact boundary the spec intended. D5-U1 already flags this: *"Severity scoring thresholds are assumed (£5k, £10k, £50k) — require validation with client against historical claims data before production."*

**Fix NOT applied.** Changing the severity thresholds before client validation would be premature. The existing model is internally consistent; the boundary is a calibration decision. This goes back to the client as a question requiring historical data.

**Spec update needed:** D3 §4.4 should specify the scoring formula as a lookup table with explicit value sub-brackets, e.g.:

```
< £1,000    → score 10
£1,000–£4,999   → score 25
£5,000–£9,999   → score 45
£10,000–£14,999 → score 65   ← sub-bracket needed to cross the 60 threshold
£15,000–£49,999 → score 75
≥ £50,000   → score 80
```

Until D5-U1 is resolved, the D4 Scenario 2B test is expected to fail.

---

## Finding 5 — Quiet failure detection mechanism not implemented (Scenario 5)

**Category: Design Gap (Category 4)**

**What broke:** Scenario 5's two detection assertions failed:
- *Primary: nightly batch job compares extracted value against adjuster reserve* — NOT IMPLEMENTED
- *Secondary: flag unactioned low-value MOTOR/PROPERTY claims for supervisor review* — NOT IMPLEMENTED

The quiet failure *behavior* was correctly confirmed: the agent processed a £1,400 claim (defective extraction simulating a £14,000 true value) end-to-end as LOW severity, reached COMPLETED with no escalation, and produced green metrics — exactly the silent failure D4 was designed to expose. But the detection mechanism that would catch this pattern in production does not exist in the console build.

**Why:** The console application was scoped in D3 §11 as a synchronous single-claim processing pipeline. The nightly batch job is a post-processing monitoring component that requires CRM integration with adjuster reserve fields — a dependency flagged in D5 as out of scope for Phase 1. The spec (D4) correctly identified the detection requirement; it simply wasn't within the Phase 1 build boundary.

**Classification: design gap.** The batch comparison job is obviously necessary for production safety; D4 specified it; D3 did not include it as a build deliverable. The gap is in scope definition, not in the builder's execution.

**No fix applied.** This is a Phase 2 CRM integration dependency. The console build verifies that the quiet failure *can* happen — which is the meaningful Phase 1 finding.

---

## Classification ordering mismatch — documented design decision

The diagnosis template flags this issue specifically. It manifested in Finding 1 and deserves an explicit note.

**The mismatch:** D2 defines a strict ordering: coverage validation trigger → check result → gate routing position. The trigger (coverage confirmation) must precede the position assignment (adjuster ID). The original code evaluated the trigger correctly but did not let the result gate the position — routing always ran. The check fired; the position was assigned anyway.

**Why it matters:** An agent that checks a trigger but ignores its output is functionally equivalent to an agent that doesn't check it at all. In this case, a `COVERAGE_DISPUTED` claim would have been routed to an adjuster and reached `COMPLETED`. From all monitoring dashboards it would look like a successful automated claim. The error would only surface when the adjuster contacted the claimant and discovered no valid coverage decision had been made.

**Why this is now a documented decision, not a silent deviation:** The routing gate (`coverage_status == "COVERED"` check before Step 7) is now in the code and its rationale is documented here. Future builds from this codebase know that routing is intentionally conditional on coverage confirmation, not a default that falls through. The ordering is no longer an implementation detail — it is a stated constraint. Any future refactor that changes this ordering now has a diagnosis note explaining exactly what breaks if it does.

---

## Changes made to the codebase in this loop

| File | Change | Reason |
|---|---|---|
| `agent_build/src/main.py` | Added `coverage_status == "COVERED"` gate before Step 7 | Finding 1 (builder misread) |
| `agent_build/src/main.py` | Changed exclusion_candidates to `list(exclusions)` | Finding 2 (builder misread) |
| `agent_build/src/main.py` | Added `simulate_unavailable` flag support + INTEGRATION_ERROR early exit | Scenario 4 test coverage |
| `agent_build/src/main.py` | Added `steps_result.json` output | Test runner dependency |
| `agent_build/src/main.py` | Added "damp", "leak", "ceiling", "pipe", "plumbing", "wall damage" to PROPERTY keywords | Finding 3 (builder misread) |
| `agent_build/data/scenarios/` | 15 new test data files for 5 scenarios | Test suite input data |
| `agent_build/src/test_runner.py` | New file — runs all 5 D4 scenarios, evaluates pass/fail | Test execution |

---

## Open items after this loop

| Item | Status | Owner |
|---|---|---|
| D5-U1: Severity scoring thresholds — validate £10k sub-bracket with client | Blocked on client data | FDE → Client |
| Nightly batch job (extracted value vs adjuster reserve) | Out of scope Phase 1 | Phase 2 planning |
| Secondary detection mechanism (unactioned low-value claims) | Out of scope Phase 1 | Phase 2 planning |
| PROPERTY keyword list — confirm completeness with domain expert | Partially addressed; may need further expansion | FDE review |
