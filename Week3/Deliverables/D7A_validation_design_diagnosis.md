# Deliverable D7A — Validation Design Diagnosis

*Source: D7 scenarios run against `agent_build/` code (D5B Agent A build). Test file: `agent_build/tests/test_d7_scenarios.py`. 12 tests collected: 7 passed, 5 failed.*

---

## 0b. Table of Contents

- [0b. Table of contents](#0b-table-of-contents)
- [1. Run summary](#1-run-summary)
- [2. S-1 diagnosis — urgency in confidence gate (R-7 not applied)](#2-s-1-diagnosis--urgency-in-confidence-gate-r-7-not-applied)
- [3. S-2 diagnosis — facility resolver not built (R-3 not applied)](#3-s-2-diagnosis--facility-resolver-not-built-r-3-not-applied)
- [4. S-3 diagnosis — WS2 not built; gap type missing from model](#4-s-3-diagnosis--ws2-not-built-gap-type-missing-from-model)
- [5. What this means for the build loop](#5-what-this-means-for-the-build-loop)

---

## 1. Run Summary

```
12 tests collected — 7 passed, 5 failed

PASSED  S-1: message classifies as STANDARD_SHIFT_REQUEST
PASSED  S-1: urgency classifies as STANDARD (deterministic)
PASSED  S-1: brief completeness gate reaches READY_FOR_REVIEW
PASSED  S-1: state machine allows transition to ADVANCED_TO_WS2
PASSED  S-2: FACILITY_FUZZY_THRESHOLD constant = 0.80 (correct)
PASSED  S-2: downstream STANDARD_SHIFT_REQUEST when facility_resolved=True (caller-supplied)
PASSED  S-2: downstream UNCLASSIFIABLE when facility_resolved=False (caller-supplied)

FAILED  S-1: confidence gate returns missing_fields=['urgency']  ← R-7 not applied
FAILED  S-1: 'urgency' present in missing_fields instead of absent   ← same root cause
FAILED  S-2: resolve_facility() does not exist in src/classifier.py  ← R-3 not applied
FAILED  S-3: src/matching.py does not exist (WS2 not built)
FAILED  S-3: HITLGapType.CANDIDATE_SELECTION_REQUIRED missing from models.py
```

---

## 2. S-1 Diagnosis — Urgency in Confidence Gate (R-7 Not Applied)

**What broke:** `apply_confidence_gate` returns `missing_fields = ['urgency']` even when all six intended gated fields are provided with scores ≥ 0.70. The brief cannot reach `READY_FOR_REVIEW` cleanly through the confidence gate path because `urgency` scores 0.0 (absent from `confidence_scores`) and is treated as UNRESOLVED.

**Where:** `src/classifier.py` line 157–165, `REQUIRED_FIELDS` tuple:

```python
REQUIRED_FIELDS: tuple[str, ...] = (
    "facility_id",
    "unit_type",
    "specialty_required",
    "credential_level",
    "shift_datetime_start",
    "shift_datetime_end",
    "urgency",        # ← this line must be removed
)
```

**Why:** D5B signal S-7 identified that `urgency` was included in `REQUIRED_FIELDS` even though urgency is classified deterministically by datetime arithmetic — not via LLM extraction — and therefore has no entry in `confidence_scores`. The D5 build-loop response memo classified this as a spec gap (not a builder misread) and issued spec revision R-7: remove `urgency` from `REQUIRED_FIELDS`. R-7 was written as a spec fix but the builder was never re-prompted to apply it. The code was not updated.

**Category: Spec ambiguity** — the original D4a spec listed `urgency` as a required entity field (§3) while Decision 2's confidence gate loop omitted it, creating an ambiguous signal about whether urgency should be gate-checked. The ambiguity was correctly identified in D5B and resolved in R-7. The failure at D7A is not a new defect in the code — the code faithfully implements the original ambiguous spec. The fix requires re-prompting the builder with R-7 explicitly applied.

**Fix:** Remove `"urgency"` from `REQUIRED_FIELDS` in `classifier.py`. One line. Re-run 34 existing tests to confirm no regression (completeness gate in `evaluate_completeness` correctly excludes urgency already — that path is unaffected).

---

## 3. S-2 Diagnosis — Facility Resolver Not Built (R-3 Not Applied)

**What broke:** `resolve_facility()` does not exist in `src/classifier.py`. The S-2 WRatio=80 boundary test cannot run at all. The `FACILITY_FUZZY_THRESHOLD = 0.80` constant is present but is an orphaned value — nothing in the codebase calls it.

**Why:** D5B Q-2 identified the fuzzy matching algorithm as a spec gap: the spec stated the threshold (0.80) but not the algorithm (`ratio`? `partial_ratio`? `token_sort_ratio`?). The builder left the constant and an interface comment but did not implement the resolver. The D5 build-loop response memo issued spec revision R-3: use `rapidfuzz.fuzz.WRatio`, threshold ≥ 80/100. R-3 was written after the build ran. The builder never received R-3 and was never re-prompted.

**What partially works:** The downstream path is intact. `classify_message_type_full` accepts `facility_resolved: bool` as a caller-supplied argument. When the caller passes `True` (simulating WRatio ≥ 80), the function correctly returns `STANDARD_SHIFT_REQUEST`. When the caller passes `False` (simulating WRatio < 80), it returns `UNCLASSIFIABLE`. The routing logic is correct; only the resolver that produces the boolean is missing.

**Category: Spec gap** — the spec was silent on which algorithm to use. R-3 filled the gap. The builder correctly stubbed the interface and did not guess. The failure is that R-3 was never applied to the code. This is not a builder misread; it is a build-loop process gap: the FDE issued two spec revisions (R-3 and R-7) in D5 but the build was not re-run with the updated spec.

**Fix:** Implement `resolve_facility(name: str, registry: list[str]) -> tuple[str | None, float]` in `src/classifier.py` using `rapidfuzz.fuzz.WRatio`. Return the best-match registry entry and score; caller filters on score ≥ 80. Requires `rapidfuzz` in `requirements.txt` (confirm it is already listed or add it).

---

## 4. S-3 Diagnosis — WS2 Not Built; Gap Type Missing from Model

**What broke (two distinct failures):**

**4a. `src/matching.py` does not exist.** `generate_shortlist()` and `create_placement_submission()` — the two functions S-3 tests — are not present anywhere in the build. `ModuleNotFoundError: No module named 'src.matching'`.

**Why:** D5B ran only for Agent A (WS1 intake spec D4a). The Agent B D5B pass (WS2 matching spec D4b) has not been run. The matching module was never built. S-3 cannot be tested against a non-existent module.

**Category: Design gap** — D4b was written and is a complete spec, but the build loop was not run against it. This is not a spec ambiguity or a builder error — no builder has touched D4b yet. The gap is that D7 validation was run before Agent B was built. S-3 is correctly designed; it is a pre-condition failure.

---

**4b. `HITLGapType.CANDIDATE_SELECTION_REQUIRED` is absent from `models.py`.** Current values: `MISSING_REQUIRED_FIELD`, `UNCLASSIFIABLE_MESSAGE`, `IMPLICIT_URGENCY_CONFIRMATION`, `SPECIALTY_AMBIGUITY`. The S-3 HITL item requires `CANDIDATE_SELECTION_REQUIRED` — which the test confirms does not exist.

**Why:** `models.py` was built against D4a (WS1 spec). D4b (WS2 spec) introduces new escalation types — specifically the candidate selection HITL that routes to coordinator review. Since D4b was written after D5B ran, the builder has never seen D4b's escalation requirements. The `HITLGapType` enum covers only WS1 gap types.

**Category: Design gap** — D4a §3 defines `HITLGapType` with four values scoped to WS1 intake. D4b's requirement for `CANDIDATE_SELECTION_REQUIRED` is a new value that belongs in the shared entity definition but was never written into D4a §3. When Agent B builds against D4b, this gap will surface again unless `models.py` is updated first. The fix requires adding `CANDIDATE_SELECTION_REQUIRED` to `HITLGapType` in `models.py` and cross-referencing it in D4a §3 as a shared entity extension.

---

## 5. What This Means for the Build Loop

Three actions are required before the D7 scenarios can all pass:

| # | Action | Scenario unblocked | Category |
|---|--------|--------------------|----------|
| 1 | Remove `"urgency"` from `REQUIRED_FIELDS` in `classifier.py` (R-7) | S-1 fully passes | Spec ambiguity — apply issued correction |
| 2 | Implement `resolve_facility()` with `rapidfuzz.fuzz.WRatio` in `classifier.py` (R-3) | S-2 WRatio boundary testable | Spec gap — apply issued correction |
| 3 | Run D5B Agent B pass against D4b; add `CANDIDATE_SELECTION_REQUIRED` to `HITLGapType` in `models.py` | S-3 testable | Design gap — WS2 build not run |

Action 1 is a one-line fix that unblocks S-1 immediately. Actions 2 and 3 require the Agent B build loop, which is the natural next step in the pipeline (D5B Agent B pass). The two D5 spec revisions (R-3 for facility fuzzy algorithm, R-7 for urgency gate) were correctly issued but were not fed back to a builder — the process gap is in the D5 → build re-run handoff, not in the spec quality.
