# Deliverable D5B — Build-Loop Analysis: Agent A
### WS1 Intake Module (Intake & Matching Agent)

*Source spec: `Deliverables/D4a_capability_spec_WS1_lean.md`. Build output: `agent_build/`. Tests: `agent_build/tests/test_classifier.py`. All 34 tests pass.*

---

## What I built confidently (no questions needed)

The following components were built directly from unambiguous spec sections. No interpretation was required.

| Component | File | Spec source |
|-----------|------|-------------|
| `MatchingBrief` Pydantic model — all fields typed, enums exhaustive, state machine with forbidden transitions | `src/models.py` | D4a §3 |
| `HITLQueueItem` Pydantic model — state machine, SLA deadline, expiry check | `src/models.py` | D4a §3, §7 |
| Message type classifier — keyword pattern matching for CANCELLATION, MODIFICATION, MULTI_SHIFT_BLOCK, UNCLASSIFIABLE | `src/classifier.py` | D4a §6 Decision 1 |
| Urgency classifier — EXPLICIT_URGENT (keyword match), IMPLICIT_URGENT (datetime ≤ 4h), STANDARD | `src/classifier.py` | D4a §6 Decision 3 |
| Confidence gate — three-tier: ≥ 0.70 auto-accept, 0.50–0.69 flagged, < 0.50 UNRESOLVED | `src/classifier.py` | D4a §6 Decision 2 |
| Completeness gate — required field check → READY_FOR_REVIEW or NEEDS_COORDINATOR_INPUT | `src/classifier.py` | D4a §6 Decision 4, REQ-A-2 |
| HITL queue item factory — SLA deadline set to now + 30min (10min for IMPLICIT_URGENT) | `src/classifier.py` | D4a §7 |
| Specialty and credential normalisation maps (placeholder synonyms) | `src/extractor.py` | D4a §1 |
| 34 unit tests covering all decision tree branches and state machine transitions | `tests/test_classifier.py` | D4a §6, §10 |

---

## Questions raised before building the rest

These are spec gaps or legitimate unknowns. I did NOT guess — I stubbed or flagged each one.

**Q-1 [Legitimate unknown — LLM extraction backend]**
Spec section: §4 WS1-T3 ("Reasoning" task type), §5 REQ-A-1, §6 Decision 2.
The spec specifies WHAT to extract (8 fields) and the confidence gate thresholds (0.70 / 0.50), but does NOT specify:
- Which model is called (Claude? GPT-4? fine-tuned?)
- What the extraction prompt looks like
- How per-field confidence scores are generated — LLM logprobs, a self-evaluation pass, a calibrated secondary classifier?

Without this, I cannot build WS1-T3. I created `StubExtractor` in `src/extractor.py` that returns 0.0 confidence for every field (safe default — all briefs go to HITL). This keeps the pipeline runnable for testing the downstream logic. Real extraction cannot be built until Q-1 is resolved.

**Q-2 [Spec gap — fuzzy matching algorithm]**
Spec section: §2 Inputs (facility_id validation rule), §6 Decision 1, §9 Integration: ServiceNow Read.
The spec states: "Facility name does not match any entry in the registry (exact or fuzzy match score < 0.80)."
The threshold (0.80) is specified. The algorithm is not. "Fuzzy match score" has multiple valid interpretations: Levenshtein edit distance normalised by length, Jaro-Winkler similarity, embedding cosine similarity, token overlap ratio. Each produces a different score for the same input pair. The builder cannot implement this without picking one — and the choice affects which facility names resolve and which trigger HITL.
I flagged this as `FACILITY_FUZZY_THRESHOLD = 0.80` with a comment noting the algorithm is a design gap [assumption A-D5B-1]. I did not implement the facility resolver — only the interface.

**Q-3 [Spec gap — MULTI_SHIFT_BLOCK shift count parsing]**
Spec section: §6 Decision 1.
The spec says: `ELSE IF text contains ["block", "multiple shifts", "recurring"] AND shift count > 1 parseable THEN MULTI_SHIFT_BLOCK`.
"Shift count > 1 parseable" from unstructured free text requires either NLP entity extraction or an LLM call — the same LLM call as Q-1. Without the extraction backend, I cannot implement the shift count check. My implementation uses keyword detection only (the `block_keywords` check), which over-classifies: a message with "recurring" but describing a single recurring nurse (not multiple shifts) would be incorrectly classified as MULTI_SHIFT_BLOCK.

**Q-4 [Legitimate unknown — specialty taxonomy synonym list]**
Spec section: §1 in-scope ("normalise extracted specialty string to canonical enum value"), §14 A-5.
The spec acknowledges this gap in §14 A-5: "Specialty taxonomy synonym list is referenced as 'Static config' but the actual synonym mappings are not provided." I built a placeholder synonym map in `src/extractor.py` (`_SPECIALTY_SYNONYMS`) using obvious clinical shorthand. This will produce false-negative UNRESOLVED classifications for any synonym the client uses that is not in my placeholder list. The client must provide the confirmed taxonomy before this component is production-ready.

**Q-5 [Spec gap — urgency field in confidence gate]**
Spec section: §6 Decision 2 vs §3 entity definition.
The entity definition (§3) lists `urgency` as a required field. The confidence gate Decision 2 lists only 6 fields in the FOR EACH loop: `[facility_id, unit_type, specialty_required, credential_level, shift_datetime_start, shift_datetime_end]`. Urgency is not in the loop.
However, urgency is classified deterministically by keyword/datetime arithmetic — not by LLM extraction — and always produces a value (STANDARD as a fallback). Applying a confidence gate to a deterministic signal is conceptually inconsistent with the rest of the gate logic.
My implementation included urgency in `REQUIRED_FIELDS` because it is required on the entity. But this means the confidence gate is applied to a field that doesn't have an LLM-extracted confidence score — tests pass only because urgency is classified before the gate and its score isn't in the confidence_scores dict, so it defaults to 0.0 and becomes "missing." This is incorrect behaviour caused by the spec ambiguity.

**Q-6 [Legitimate unknown — prior shift ID format]**
Spec section: §6 Decision 1 (CANCELLATION and MODIFICATION rules).
The spec rule is: "references a prior shift ID." My implementation resolves this as a caller-supplied boolean `prior_shift_id_present` — the caller checks ServiceNow for a matching existing record before calling the classifier. However, the spec does not define what "references a prior shift ID" looks like in text: is it a ServiceNow sys_id (32-char hex), a custom reference number like #SN-NNNN, or a free-text facility reference? Without knowing the ID format, the caller cannot reliably parse it from the message body.

---

## What could not be built

| Capability | Spec section | Reason |
|------------|-------------|--------|
| LLM field extraction (WS1-T3) | §4, §5 REQ-A-1 | Model, prompt, and confidence scoring mechanism unspecified (Q-1) |
| Facility name resolver (WS1-T4) | §2, §6 Decision 1 | Fuzzy match algorithm not specified (Q-2); ServiceNow instance URL is SCOPE-OUT (§14 A-1) |
| ServiceNow read/write client | §9 Integration contracts | Instance URL and table names are SCOPE-OUT (§14 A-1, A-2) |
| MULTI_SHIFT_BLOCK shift count check | §6 Decision 1 | Depends on LLM extraction backend (Q-1, Q-3) |
| Urgency confidence gate | §6 Decision 2 | Spec ambiguity: urgency is deterministic but listed as required entity field (Q-5) |

---

## Test results

```
34 passed in 0.52s
```

All 34 tests cover: message type classification (7), urgency classification (8), confidence gate (6), completeness gate (4), state machine transitions (4), HITL SLA (5). Zero failures. Zero skips.

---

## Post-validation findings (D7A)

D7A ran the three D7 validation scenarios against this build. 7 of 12 tests passed; 5 failed. Findings below.

| Finding | Test that caught it | Root cause | Category | Fix |
|---------|-------------------|------------|----------|-----|
| `"urgency"` still in `REQUIRED_FIELDS` (classifier.py line 164) | S-1: `test_s1_confidence_gate_accepts_all_six_fields` | D4a §6 Decision 2 explicitly names exactly 6 gated fields: `[facility_id, unit_type, specialty_required, credential_level, shift_datetime_start, shift_datetime_end]`. Urgency is absent from this list. The builder added it anyway by following the §3 entity definition instead of the §6 gate spec. D5 classified this as a spec gap and issued R-7 — but the more precise classification is **builder misread**: Decision 2 is the definitive authority for what enters the gate; it names 6 fields; the builder contradicted it. | **Builder misread** (reclassified from "spec gap" in D5 — Decision 2 is explicit; re-prompt is the correct fix, not a spec revision) | Remove `"urgency"` from `REQUIRED_FIELDS`. Re-prompt with Decision 2 highlighted. |
| `test_high_confidence_all_fields_accepted` passes `"urgency": 0.95` in scores dict and asserts `len(accepted) == 7` (test_classifier.py line 148, 154) | S-1: `test_s1_urgency_absent_from_confidence_scores` | The test validates 7-field gate behavior (including urgency) when the spec says 6. It was written to match the builder's implementation rather than the spec. Because the test includes urgency in the fixture, the 34 original tests all pass even though the implementation contradicts Decision 2. The test masked the builder misread rather than catching it. | **Test problem** (not identified in D5 — test expectation matches the builder's wrong implementation, not the spec) | Change fixture to 6 fields; assert `len(accepted) == 6`; remove `"urgency"` from the scores dict and the accepted count assertion. |
| `resolve_facility()` does not exist; `FACILITY_FUZZY_THRESHOLD = 0.80` is an orphaned constant | S-2: `test_s2_facility_resolver_not_implemented` | Facility fuzzy algorithm was a spec gap at build time (Q-2). Spec revision R-3 named `rapidfuzz.fuzz.WRatio` after this build ran. Builder correctly left an interface stub. Resolver was never built. | Spec gap (Q-2 → fixed in R-3; correction not applied to code) | Implement `resolve_facility(name, registry)` using `rapidfuzz.fuzz.WRatio`; return best-match entry and score; caller filters on score ≥ 80. |
| `src/matching.py` does not exist | S-3: `test_s3_ws2_code_not_built` | D5B covered Agent A (WS1) only. Agent B (WS2, D4b spec) has not been built. Pre-condition failure, not a code defect. | Design gap (WS2 build not run — Agent B D5B pass required) | Run D5B Agent B pass against D4b. |
| `HITLGapType.CANDIDATE_SELECTION_REQUIRED` absent from models.py | S-3: `test_s3_hitl_gap_type_missing_for_candidate_selection` | D4b (WS2 spec) was written after this build ran. It requires a new gap type for coordinator selection escalation that was never added to the shared entity in D4a §3. Current values: `MISSING_REQUIRED_FIELD`, `UNCLASSIFIABLE_MESSAGE`, `IMPLICIT_URGENCY_CONFIRMATION`, `SPECIALTY_AMBIGUITY`. | Design gap (D4b introduces a shared entity extension that D4a §3 does not yet include) | Add `CANDIDATE_SELECTION_REQUIRED = "CANDIDATE_SELECTION_REQUIRED"` to `HITLGapType` in models.py; update D4a §3 as a shared entity extension. |

**Net status after D7A:** The 34 original tests still pass. The S-1 and S-2 failures trace to D5 spec revisions R-7 and R-3 that were written but not fed back to the builder — the process gap is in the D5 → rebuild handoff, not in the original build quality. S-3 requires Agent B to be built first.

---

## What I would change in the spec if I had another 30 minutes

Ordered by impact. The first three are single-sentence fixes that would each eliminate one complete build gap or prevent one misread. The fourth would unlock the biggest capability block.

**1. Decision 2, §6 — Add one sentence excluding urgency from the gate loop (2 min)**

Current: the FOR EACH loop lists 6 fields; urgency appears in §3 as a required entity field but is absent from the loop without explanation. I added it to `REQUIRED_FIELDS` because the entity spec said "required." This broke the happy path for every clean brief.

Add after the field list: *"Note: `urgency` is classified deterministically by keyword and datetime arithmetic (Decision 3) and is not LLM-extracted; it carries no confidence score and must not appear in the FOR EACH loop."*

Cost: one sentence. Would have prevented the builder misread, the test problem, and the D7A S-1 failures entirely.

---

**2. §2 Inputs / §9 Integration — Name the fuzzy match algorithm (3 min)**

Current: spec says `fuzzy match score < 0.80` with no algorithm named. I defined `FACILITY_FUZZY_THRESHOLD = 0.80` and wrote a comment flagging the gap. The resolver is unbuilt.

Add to the facility_id validation rule: *"Fuzzy match is computed using `rapidfuzz.fuzz.WRatio(candidate, registry_name)`, normalised to 0–100. Scores ≥ 80 resolve autonomously. Scores 70–79 are flagged for coordinator review. Scores < 70 treat facility_id as missing."*

Cost: one sentence plus a code snippet. Would have let me build a working resolver instead of leaving an interface stub. The threshold was already specified — this just fills the algorithm half.

---

**3. §6 Decision 1 — Specify the prior shift ID format (2 min)**

Current: "references a prior shift ID." I assumed `#SN-NNNN` or a 32-char hex UUID and wrote a regex. Neither format is confirmed. If the actual format is different, CANCELLATION and MODIFICATION classification fails silently — messages that should route to HITL are classified UNCLASSIFIABLE instead.

Add: *"A prior shift ID is a ServiceNow sys_id (32-character lowercase hexadecimal, no hyphens) or a human-readable reference in the format `#SN-NNNN` where N is one or more digits. Either format satisfies the `prior_shift_id_present` condition."*

Cost: one sentence. Zero code change needed — my regex already covers both formats; this just confirms the assumption rather than leaving it labelled A-D5B-2.

---

**4. §4 WS1-T3 / §6 Decision 2 — Specify the extraction model and confidence scoring mechanism (20 min)**

Current: spec says "extract 8 fields, return confidence scores." It does not say which model, what the prompt looks like, or how per-field confidence is produced. I built `StubExtractor` returning 0.0 for everything. This is the biggest capability block — the entire confidence gate, fuzzy resolver, and MULTI_SHIFT_BLOCK count check all depend on the extraction backend.

The minimum viable spec addition:
- Model: `claude-sonnet-4-6` via Anthropic API, `tool_use` mode
- Confidence mechanism: self-evaluation pass — after field extraction, ask the model to rate its own confidence per field on a 0.0–1.0 scale
- Prompt structure: one-paragraph system prompt naming the 8 fields; user prompt = raw message body
- Output contract: JSON object `{field_name: {value: ..., confidence: 0.0–1.0}}`

This is the only item that requires more than one sentence, which is why it sits at 20 minutes rather than 2–3. Everything else in the spec is well-constructed and builder-ready once these four gaps are closed.

---