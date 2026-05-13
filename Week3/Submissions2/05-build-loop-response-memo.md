# Deliverable D5 — Build-Loop Response Memo
### MedFlex WS1 Intake Module — Agent A Diagnostic

*Source: `Deliverables/D4a_capability_spec_WS1_lean.md`, `Deliverables/D5B_build_loop_analysis.md`, `References/spec-ambiguity-vs-builder-mistakes.md`. Taxonomy applied per reference taxonomy decision tree.*

---

## 1. Signal Inventory

| Signal ID | What the build produced | What the spec required or intended | First-pass classification |
|-----------|------------------------|------------------------------------|--------------------------|
| S-1 | `StubExtractor` with 0.0 confidence for all fields — LLM extraction not implemented | WS1-T3: extract 8 structured fields from free text with per-field confidence scores | Legitimate unknown |
| S-2 | No implementation of confidence score generation mechanism | §6 Decision 2 requires per-field confidence score float 0.0–1.0 per extracted field | Legitimate unknown |
| S-3 | `FACILITY_FUZZY_THRESHOLD = 0.80` constant defined; algorithm not implemented | §9: "fuzzy match score < 0.80" — threshold specified, algorithm not | Spec gap |
| S-4 | `prior_shift_id_present: bool` caller-supplied flag; format of shift ID not parsed | §6 Decision 1: CANCELLATION/MODIFICATION rules require "references a prior shift ID" | Spec gap |
| S-5 | `"today"` keyword triggers EXPLICIT_URGENT on substring match | §6 Decision 3: keyword list includes "today" — matches "I'm writing today to request..." (false positive) | Spec gap |
| S-6 | Placeholder `_SPECIALTY_SYNONYMS` dict with 18 entries | §1: "normalise to canonical enum using specialty taxonomy reference (Static config)" — taxonomy not provided | Legitimate unknown |
| S-7 | `urgency` included in `REQUIRED_FIELDS` tuple for confidence gate | §6 Decision 2 lists 6 fields in FOR EACH loop — urgency absent; entity §3 lists urgency as required | **Builder misread** *(reclassified from "spec gap" after D7A validation — see §5)* |
| S-10 | `test_high_confidence_all_fields_accepted` includes `"urgency": 0.95` in fixture and asserts `len(accepted) == 7` | Spec (Decision 2) defines a 6-field gate; test validates 7-field behavior, masking the S-7 misread | Test problem |
| S-8 | `classify_message_type` split into two functions (`_full` variant for STANDARD upgrade) | Spec describes one decision tree for message type classification | Unjustified implementation choice |
| S-9 | MULTI_SHIFT_BLOCK detected by keyword only; shift count not parsed | §6 Decision 1: "shift count > 1 parseable" required for MULTI_SHIFT_BLOCK classification | Spec gap |

---

## 2. Classified Signal Responses

---

```
Signal S-1: LLM extraction backend not implemented — StubExtractor used.

Classification: Legitimate unknown surfaced correctly

Evidence:
- Spec: §4 WS1-T3 — task type "Reasoning," data required "Message text, specialty taxonomy," tool required "Specialty taxonomy config." The spec names the task and its inputs/outputs but does not name the model, the prompt, or the mechanism for generating per-field confidence scores.
- Build: Builder created StubExtractor returning 0.0 confidence for all fields, with a comment block explicitly naming the design gaps (model, prompt, confidence mechanism) and marking them as DG-1.
- Why Legitimate Unknown and not Spec Gap: A spec gap means the spec was ambiguous between two defensible interpretations. Here the spec is not ambiguous — it is simply silent on the implementation. The builder did not guess; they surfaced the gap and provided a safe stub. That is the correct response to a legitimate unknown.

Response:
You're right that the spec didn't address the extraction implementation. The correct behaviour is:
- Model: Claude claude-sonnet-4-6 via the Anthropic SDK (structured output mode)
- Prompt: A structured extraction prompt with the 8 required fields as the output schema, passed as a tool definition so field values are returned as typed JSON
- Confidence mechanism: Use the model's tool_use response — if a field is populated, confidence = 1.0; if the model leaves the field absent from the tool response, confidence = 0.0. A secondary calibration pass (re-ask the model "how confident are you in this extraction?") is deferred to v2 — too much latency for the 3-minute brief target (KPI baseline D4a §0).

I'm adding this to the spec now (see R-1 in §3). Please implement using the updated spec.

Ownership: Shared (FDE owns the gap; builder surfaced it correctly)
```

---

```
Signal S-2: Confidence score generation mechanism not specified.

Classification: Legitimate unknown surfaced correctly

Evidence:
- Spec: §6 Decision 2 requires "per-field extraction confidence, float 0.0–1.0" in confidence_scores. §5 REQ-A-1 references "extraction confidence for any required field < 0.70." The spec does not state how the confidence value is produced.
- Build: Builder flagged this in extractor.py: "How per-field confidence scores are generated (LLM logprobs? self-report? a separate calibration pass?) — DESIGN GAP [DG-1]."
- Why Legitimate Unknown and not Spec Gap: The spec prescribed a threshold and a gate; it was simply silent on the source of the score. Builder surfaced rather than guessed.

Response:
You're right that the spec didn't address this. The correct behaviour is: confidence score = 1.0 if the model's tool response includes the field with a non-null value; 0.0 if the field is absent from the tool response. This binary model is calibration-free and avoids the logprobs complexity. The 0.70 and 0.50 thresholds in the gate are meaningful only once calibration data is available — in v1, any field the model does not return gets confidence = 0.0 → UNRESOLVED → HITL. This is intentionally conservative. Threshold tuning is a post-deployment activity (D4a §14 A-6).

I'm adding this to the spec now (see R-2 in §3).

Ownership: Shared
```

---

```
Signal S-3: Fuzzy match algorithm not specified — threshold defined, no implementation.

Classification: Spec gap

Evidence:
- Spec: §9 Integration: ServiceNow Read — "Facility name does not match any entry in the registry (exact or fuzzy match score < 0.80)." Threshold 0.80 is specified. Algorithm is not.
- Build: Builder defined FACILITY_FUZZY_THRESHOLD = 0.80 with assumption comment A-D5B-1: "Algorithm not specified in spec. Using threshold value from spec (0.80) but algorithm is a design gap."
- Why Spec Gap and not Legitimate Unknown: The spec specifies a numeric threshold — this implies there is a single intended algorithm that produces a score in [0, 1] that the threshold applies to. The builder had to choose an algorithm to make the threshold meaningful. Two defensible interpretations: (A) string similarity (Jaro-Winkler or Levenshtein ratio), (B) embedding cosine similarity. The spec as written supports both — it is ambiguous, not merely silent.

Response:
I need to revise the spec because the original statement was ambiguous between (A) string similarity and (B) semantic embedding similarity. The correct behaviour is: use rapidfuzz library, WRatio scorer (weighted ratio combining partial match, token sort, and full ratio) — this handles abbreviations ("St. Mary's" vs "Saint Marys"), transpositions, and common facility name patterns better than Levenshtein alone. The 0.80 threshold applies to the WRatio score (0–100 normalised to 0.0–1.0 by dividing by 100). Embedding similarity is deferred to v2 — requires a vector store that is not in the current system inventory.

(See R-3 in §3.)

Ownership: FDE
```

---

```
Signal S-4: Prior shift ID format not specified — resolved as caller-supplied boolean.

Classification: Spec gap

Evidence:
- Spec: §6 Decision 1 — "CANCELLATION: IF text contains cancellation keywords AND references a prior shift ID." "Prior shift ID" is not defined: no format, no example, no lookup mechanism named.
- Build: Builder resolved this as `prior_shift_id_present: bool` — a caller-supplied flag — with comment: "Prior shift ID pattern assumed to follow ServiceNow sys_id format (alphanumeric, length 32) or #SN-NNNN. Spec says 'references a prior shift ID' without specifying the ID format."
- Why Spec Gap and not Builder Misread: The spec says "references a prior shift ID" — both interpretations (parse from text, or resolve via ServiceNow lookup) are defensible under that phrase. The builder chose the safer path (caller resolves) rather than guessing the format.

Response:
I need to revise the spec. The correct behaviour is: the agent does NOT parse the shift ID from the message text. Instead, after message type is classified as potentially CANCELLATION or MODIFICATION (keyword match), the agent queries ServiceNow for open MatchingBrief records with the same facility_id (extracted from the current message) created in the past 72 hours. If one or more exist, prior_shift_id_present = True. This approach does not require parsing a specific ID format from free text — it relies on the structured ServiceNow lookup.

(See R-4 in §3.)

Ownership: FDE
```

---

```
Signal S-5: "today" keyword triggers EXPLICIT_URGENT on any substring match — false positives on message metadata language.

Classification: Spec gap

Evidence:
- Spec: §6 Decision 3 — 'IF message text contains any of ["urgent", "ASAP", "immediately", "emergency", "same day", "today"] THEN urgency = EXPLICIT_URGENT.'
- Build: Builder implemented a case-insensitive substring match across the full message body. "I'm writing today to request a nurse for next Tuesday" → matches "today" → EXPLICIT_URGENT. This is unintended but matches the spec as written.
- Why Spec Gap and not Builder Misread: The spec literally lists "today" as a trigger keyword and specifies substring match logic. The builder's implementation is faithful to the spec as written. The false positive behaviour is a consequence of the spec's keyword list being insufficiently constrained — two readings: (A) "today" anywhere in text, (B) "today" modifying a temporal reference to the shift itself.

Response:
I need to revise the spec. The original keyword list was ambiguous about whether "today" must modify the shift date or can appear anywhere in the message. The correct behaviour is: "today" triggers EXPLICIT_URGENT only when it co-occurs within 10 tokens of a shift time reference (e.g., "today at 7pm", "tonight", "today's shift"). Standalone "today" with no adjacent shift reference does not trigger. Implementation: apply the keyword check only to the sentence(s) containing a time expression (parsed shift_datetime_start text span), not the full message body. If no time expression is found, "today" alone does not trigger.

(See R-5 in §3.)

Ownership: FDE
```

---

```
Signal S-6: Specialty synonym taxonomy provided as 18-entry placeholder.

Classification: Legitimate unknown surfaced correctly

Evidence:
- Spec: §1 in-scope — "normalise extracted specialty string to canonical enum value using specialty taxonomy reference (Static config, agent procedural memory)." §14 A-5 explicitly flags this: "Specialty taxonomy synonym list... the actual synonym mappings are not provided in the spec."
- Build: Builder provided `_SPECIALTY_SYNONYMS` dict with 18 entries and comment: "Must be replaced with the client-confirmed taxonomy before production." Builder did not pretend the placeholder was sufficient.
- Why Legitimate Unknown and not Spec Gap: The spec acknowledged the gap in §14 A-5. The builder surfaced it rather than inventing a complete taxonomy. This is the correct behaviour.

Response:
You're right that the spec didn't provide the taxonomy. The correct behaviour is: the taxonomy is provided by the client as a JSON config file. Action: request from Marcus Reyes (or his ops team) a list of the specialty labels and abbreviations coordinators actually use when describing shift requirements, mapped to the canonical enum values in the spec. Until that file is received, the placeholder stands and all non-obvious specialty strings will produce UNRESOLVED → HITL. This is acceptable for v1 if the HITL rate target (≤ 25% per D4a §0) is monitored — any specialty term not in the taxonomy will inflate the HITL rate.

I'm adding this as a pre-deployment prerequisite (see R-6 in §3).

Ownership: Shared
```

---

```
Signal S-7: urgency field added to confidence gate REQUIRED_FIELDS despite being absent from spec's Decision 2 field list.

Classification: Builder misread  ← reclassified from "spec gap" after D7A validation

Evidence:
- Spec (Decision 2 §6): "FOR EACH required_field IN [facility_id, unit_type, specialty_required,
  credential_level, shift_datetime_start, shift_datetime_end]" — 6 fields listed explicitly.
  Urgency is absent. Decision 2 is the authoritative spec section for the gate.
- Build: Builder added urgency as a 7th entry in REQUIRED_FIELDS, citing §3 (entity definition).
  Decision 2 names the gate fields precisely; adding a 7th field contradicts the spec as written.
- Why Builder Misread and not Spec Gap: A spec gap requires two defensible interpretations of the
  same text. Decision 2 is not ambiguous about which fields enter the gate — it names them. The
  builder followed the entity definition (§3) over the gate specification (§6 Decision 2), which
  is the authoritative section. When two sections conflict, the section that governs the specific
  behaviour (Decision 2 governs the gate) takes precedence. This was always the correct reading.
- Original misclassification: D5 classified this as a spec gap because §3 lists urgency as
  required and the builder's inference (required = gated) was described as defensible. D7A
  validation showed the practical consequence: every clean brief stalls with missing_fields=
  ["urgency"] because urgency has no LLM-extracted confidence score. The D7A S-1 failure is
  unambiguous — the builder contradicted Decision 2.

Response (builder correction — see §4):
The spec (Decision 2) names 6 gated fields. Urgency is not one of them. Remove urgency from
REQUIRED_FIELDS. R-7 (§3) is retained as a spec clarification to prevent the same misread in
future build loops — it is not the primary fix. The primary fix is the builder correction.

Ownership: Builder
```

---

```
Signal S-10: test_high_confidence_all_fields_accepted validates 7-field gate behavior.

Classification: Test problem

Evidence:
- Spec (Decision 2 §6): gate loop covers 6 fields — urgency is absent.
- Test (test_classifier.py line 145–154): fixture passes confidence_scores for all 7 fields
  including "urgency": 0.95, and asserts len(accepted) == 7.
- Build: builder implemented 7 fields (S-7 misread). Test was written to match the build,
  not the spec. Because the test included urgency with a valid score, urgency never appeared
  in missing_fields during the original 34-test run — the misread was masked.
- Why Test Problem and not Builder Misread: the code and test are consistent with each other;
  both are inconsistent with the spec. A builder misread fix (remove urgency from REQUIRED_FIELDS)
  will cause this test to fail, confirming the test expectation is wrong.

Response:
Fix the test after applying the S-7 builder correction. Change the fixture to 6 fields (remove
"urgency" from the scores dict) and change assert len(accepted) == 7 to assert len(accepted) == 6.
Do not re-prompt the builder for the test — fix the test directly.

Ownership: FDE (test was written to validate the builder's implementation, not the spec)
```

---

```
Signal S-8: Message type classification split into two functions (classify_message_type + classify_message_type_full).

Classification: Unjustified implementation choice

Evidence:
- Spec: §6 Decision 1 describes one decision tree for message type classification with a single set of inputs (text, facility_resolved, datetime_parseable, prior_shift_id_present) and one output (MessageType).
- Build: Builder split the function into classify_message_type (text + prior_shift_id only) and classify_message_type_full (adds facility_resolved and datetime_parseable) for "separation of concerns."
- Why Unjustified Addition and not Builder Misread: The split does not contradict the spec — the combined behaviour is equivalent to the spec's single decision tree. It is an architectural choice that the spec did not request. It is not wrong, but it introduces a public interface not in the spec.

Response:
This wasn't specified. Before deciding whether to keep it, we need to align: the two-function split is not wrong, but it creates two public entry points where the spec described one. If future callers use classify_message_type (the simpler variant) without the facility_resolved check, they will get UNCLASSIFIABLE for STANDARD_SHIFT_REQUEST messages — a silent failure. The safer approach is a single function with all four parameters. Either: (A) merge back into one function and keep the STANDARD upgrade logic internal, or (B) keep the split but make classify_message_type private (rename to _classify_message_type_text_only) so the public API matches the spec's single entry point. Option B is preferred — the internal decomposition is useful but should not be exposed as two public functions.

Ownership: Collaborative
```

---

```
Signal S-9: MULTI_SHIFT_BLOCK detected by keyword only — shift count not parsed.

Classification: Spec gap

Evidence:
- Spec: §6 Decision 1 — "ELSE IF text contains ["block", "multiple shifts", "recurring"] AND shift count > 1 parseable THEN MULTI_SHIFT_BLOCK."
- Build: Builder implemented keyword detection only; could not implement "shift count > 1 parseable" without the LLM extraction backend (Q-1). Comment in code: "Spec says 'shift count > 1 parseable' but does not specify how to count shifts. Using keyword heuristic only [assumption A-D5B-3]."
- Why Spec Gap and not Legitimate Unknown: The spec's "shift count > 1 parseable" condition implies a parsing step, but the spec is silent on HOW to parse a shift count from free text. A keyword heuristic and an LLM count extraction are both defensible implementations. The builder chose keyword-only; this is a valid interpretation of "parseable" (if keywords like "multiple" are present, the count is implicitly > 1). However, a message with "recurring nurse needed" (single recurring nurse, one shift at a time) would incorrectly classify as MULTI_SHIFT_BLOCK under the builder's interpretation.

Response:
I need to revise the spec. The original "shift count > 1 parseable" was ambiguous between (A) keyword heuristic implying multiple shifts and (B) numeric count explicitly extractable from text. The correct behaviour is: use the LLM extraction backend (once Q-1 is resolved) to extract an explicit shift count from the message. If an explicit count (e.g., "3 shifts," "Friday, Saturday, Sunday") is present and > 1, classify as MULTI_SHIFT_BLOCK. If only the keyword "recurring" is present with no explicit count, classify as STANDARD_SHIFT_REQUEST and add special_notes = "Recurring shift — coordinator should confirm frequency." "Recurring" alone does not confirm multiple discrete shifts.

(See R-8 in §3.)

Ownership: FDE
```

---

## 3. Spec Revision Log

```
Revision R-1 (for Signal S-1):
Section revised: D4a §4 Activity Catalog — WS1-T3 (Tool required column)
Original text: "Tool required: Specialty taxonomy config"
Revised text: "Tool required: Anthropic claude-sonnet-4-6 API (tool_use mode) + Specialty taxonomy config. Extraction prompt passes the 8 required fields as a tool definition; model returns typed JSON. Field absent from tool response = confidence 0.0. Field present = confidence 1.0 (binary confidence model, v1)."
What the revision prevents: Builder would implement any available model or a RAG retrieval instead of a structured tool_use call.
Category: Legitimate unknown — gap filled
```

```
Revision R-2 (for Signal S-2):
Section revised: D4a §6 Decision 2 — Confidence gate
Original text: "Confidence gate: Threshold = 0.70 for auto-accept; 0.50–0.69 for flagged-accept; < 0.50 → UNRESOLVED"
Revised text: "Confidence gate: Threshold = 0.70 for auto-accept; 0.50–0.69 for flagged-accept; < 0.50 → UNRESOLVED. Confidence score source (v1): binary — 1.0 if the Anthropic tool_use response includes the field with a non-null value; 0.0 if the field is absent from the tool response. Threshold tuning is a post-deployment activity after 200-brief calibration sample."
What the revision prevents: Builder implements logprobs-based confidence (requires model support not guaranteed) or a self-evaluation secondary call (doubles latency).
Category: Legitimate unknown — gap filled
```

```
Revision R-3 (for Signal S-3):
Section revised: D4a §2 Inputs table — facility_id validation rule
Original text: "Validation rule: Facility name extracted from text must resolve to a known facility_id; no match → UNCLASSIFIABLE flag"
Revised text: "Validation rule: Facility name extracted from text must resolve to a known facility_id using rapidfuzz WRatio scorer (score ≥ 80 on 0–100 scale). No match (score < 80) or multiple matches tied at score ≥ 80 → UNCLASSIFIABLE. Exact match (score = 100) bypasses fuzzy check."
What the revision prevents: Builder selects Levenshtein or embedding similarity, producing different match/no-match outcomes for the same facility name variants.
Category: Spec gap — ambiguity resolved
```

```
Revision R-4 (for Signal S-4):
Section revised: D4a §6 Decision 1 — CANCELLATION and MODIFICATION conditions
Original text: "IF text contains cancellation keywords AND references a prior shift ID THEN message_type = CANCELLATION"
Revised text: "IF text contains cancellation keywords AND (ServiceNow query returns ≥ 1 open MatchingBrief for the same resolved facility_id created within the past 72 hours) THEN message_type = CANCELLATION; attach the most recent matching brief_id as cancellation_target_id. If no prior brief found → message_type = UNCLASSIFIABLE with gap_type = UNCLASSIFIABLE_MESSAGE."
What the revision prevents: Builder parses free text for a shift ID using a regex that doesn't match the actual ServiceNow reference format.
Category: Spec gap — ambiguity resolved
```

```
Revision R-5 (for Signal S-5):
Section revised: D4a §6 Decision 3 — Urgency classification logic
Original text: 'IF message text contains any of ["urgent", "ASAP", "immediately", "emergency", "same day", "today"] THEN urgency = EXPLICIT_URGENT'
Revised text: 'IF message text contains any of ["urgent", "ASAP", "immediately", "emergency", "same day"] THEN urgency = EXPLICIT_URGENT. "today" triggers EXPLICIT_URGENT only when it appears in the same sentence as an extracted shift time reference (i.e., shift_datetime_start text span is in the same sentence as "today"). Standalone "today" with no adjacent time reference does not trigger. If no sentence-level time reference is parseable, evaluate "today" as: EXPLICIT_URGENT if shift_datetime_start = today's date, STANDARD otherwise.'
What the revision prevents: "I'm writing today to request a nurse for next Tuesday" classified as EXPLICIT_URGENT — queue jumping for a non-urgent request.
Category: Spec gap — ambiguity resolved
```

```
Revision R-6 (for Signal S-6):
Section revised: D4a Preamble §7 Pre-deployment prerequisite checklist (added item)
Original text: [item not present]
Revised text: "[ ] Specialty taxonomy config file — JSON file mapping client-used specialty terms and abbreviations to canonical enum values (RN_ICU, RN_ED, etc.). Confirmed by: MedFlex operations team. If unconfirmed: all non-obvious specialty strings produce UNRESOLVED → HITL; HITL rate target (≤ 25%) cannot be met. Blocker for production — not for integration testing."
What the revision prevents: Builder ships with placeholder taxonomy; production HITL rate exceeds target; coordinators lose trust in the extraction step.
Category: Legitimate unknown — gap filled
```

```
Revision R-7 (for Signal S-7):
Section revised: D4a §6 Decision 2 — REQUIRED_FIELDS list
Original text: "FOR EACH required_field IN [facility_id, unit_type, specialty_required, credential_level, shift_datetime_start, shift_datetime_end]:"
Revised text: "FOR EACH required_field IN [facility_id, unit_type, specialty_required, credential_level, shift_datetime_start, shift_datetime_end]: [gate logic]. NOTE: urgency is excluded from the confidence gate loop. It is set by classify_urgency() after extraction — a deterministic classifier that always produces a value (STANDARD as fallback). Urgency is required on the MatchingBrief entity but is never UNRESOLVED and never a confidence gate failure."
What the revision prevents: Future builder misreads the entity definition (§3) and adds urgency to the gate loop again.
Category: Spec clarification — prevents recurrence of builder misread S-7. Primary fix is the builder correction in §4, not this revision.
```

```
Revision R-8 (for Signal S-9):
Section revised: D4a §6 Decision 1 — MULTI_SHIFT_BLOCK condition
Original text: 'ELSE IF text contains ["block", "multiple shifts", "recurring"] AND shift count > 1 parseable THEN message_type = MULTI_SHIFT_BLOCK'
Revised text: 'ELSE IF text contains ["block", "multiple shifts"] AND the LLM extraction identifies an explicit count of discrete shift instances > 1 (e.g., "3 shifts", "Friday, Saturday, Sunday", "all weekend") THEN message_type = MULTI_SHIFT_BLOCK. "recurring" keyword alone, with no explicit count, classifies as STANDARD_SHIFT_REQUEST with special_notes = "Recurring shift — coordinator to confirm frequency." Shift count extraction is part of the LLM extraction pass (WS1-T3) — not a separate call.'
What the revision prevents: Single recurring placements classified as multi-shift blocks — wrong routing, wrong downstream workflow triggered.
Category: Spec gap — ambiguity resolved
```

---

## 4. Builder Correction Memos

*One builder misread identified (S-7). One test problem identified (S-10 — FDE fixes the test directly; no re-prompt needed).*

**For Signal S-7 (builder misread — re-prompt required):**

```
Re-prompt for Signal S-7:

The spec (§6 Decision 2) names exactly 6 fields in the confidence gate loop:
  [facility_id, unit_type, specialty_required, credential_level,
   shift_datetime_start, shift_datetime_end]

Urgency is not in this list. Your implementation adds it as a 7th entry in
REQUIRED_FIELDS (src/classifier.py):

  REQUIRED_FIELDS: tuple[str, ...] = (
      "facility_id", "unit_type", "specialty_required", "credential_level",
      "shift_datetime_start", "shift_datetime_end",
      "urgency",    ← this line contradicts Decision 2; remove it
  )

Because urgency is classified deterministically (not LLM-extracted), it never
appears in confidence_scores. The gate defaults its score to 0.0 → UNRESOLVED
→ missing_fields["urgency"] on every brief. Every clean brief stalls in HITL.

Please revise:
1. Remove "urgency" from REQUIRED_FIELDS in classifier.py
2. Urgency is assigned by classify_urgency() independently — it runs before the
   gate and is never gated. The entity requires it, but it is not an LLM field.
3. Do NOT update test_missing_score_treated_as_zero — that test is for LLM fields.
   The FDE will separately fix test_high_confidence_all_fields_accepted (S-10).
```

**For Signal S-8 (unjustified addition — collaborative):**

```
Collaborative request for Signal S-8:

This wasn't specified — the spec describes one entry point for message type 
classification, but you've implemented two (classify_message_type and 
classify_message_type_full). The decomposition is sensible internally, but 
exposing two public functions creates a risk: callers who use the simpler variant 
will get UNCLASSIFIABLE for all STANDARD_SHIFT_REQUEST messages silently.

Before deciding whether to keep it:
- Rename classify_message_type to _classify_message_type_text_only (private)
- Keep classify_message_type_full as the single public entry point
- Update all tests to call only the public function

This preserves your internal decomposition while matching the spec's interface.
```

---

## 5. Diagnostic Accuracy Self-Assessment

**Hardest classification call:**
"The hardest call in this fixture was Signal S-7. I initially read it as a builder misread because the spec's Decision 2 explicitly lists 6 fields and urgency is absent — the builder added a field the spec's loop didn't include. I then reclassified it as a spec gap, reasoning that the entity definition in §3 marks urgency as required, which I judged gave the builder a defensible basis for including it in the confidence gate. That reclassification was wrong. D7A validation confirmed the original instinct: every clean brief stalls with missing_fields=['urgency'] because urgency has no LLM-extracted confidence score — a consequence so severe it cannot be classified as 'acceptable variation.' The reclassification error was methodological: I applied the defensibility test ('could the builder read the spec this way?') without applying the downstream consequence test ('does this reading produce behaviour consistent with the spec's intent?'). A defensible reading that causes every brief to stall is not actually defensible — it breaks the system's core path. The correct classification sequence for a case like this is: (1) does the spec's authoritative section (Decision 2) name a specific list? Yes — 6 fields. (2) did the builder add to that list? Yes. (3) could the builder claim a basis elsewhere in the spec? Yes (§3). (4) does that alternate basis produce a working system? No. Step 4 is the tiebreaker — the §3 basis fails on first contact with a real brief. Builder misread."

**Closest miss:**
"The signal I came closest to misclassifying was S-5 (the 'today' keyword). The risk of error was that the builder faithfully implemented the spec's keyword list — 'today' is right there in the spec's IF condition — so it looked like a test problem (the test expects 'today' to be safe but the spec supports the builder's implementation). I avoided the error by reading the spec's intent: the spec's urgency section is titled 'classify urgency' and the surrounding context makes clear the keyword should indicate the shift is urgent, not that the message was written today. The keyword list was the spec's mistake, not the builder's implementation — confirmed by applying the 'was the builder's reading defensible' test: yes, substring match on 'today' is exactly what 'contains today' means."

**Pre-session prediction:**
"Before the build loop, I predicted the hardest part of build-loop diagnosis would be distinguishing legitimate unknowns from design gaps — whether the builder surfaced a question correctly vs. guessed and implemented something unspecified. Looking at this fixture, that prediction was partially accurate: S-1, S-2, and S-6 were all legitimate unknowns correctly surfaced, and none required reclassification. The harder calls were the spec gaps (S-3 through S-5, S-7, S-9) where the builder did implement something but the spec had two defensible readings — those required reading both the spec and the code closely before classifying."
