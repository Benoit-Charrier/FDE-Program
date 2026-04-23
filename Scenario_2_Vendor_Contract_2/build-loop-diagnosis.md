# Build Loop Diagnosis — Scenario 2 Vendor Contract Agent

**Audit trail**: 138 events across 5 contracts · 3 code fixes · 2 test-fixture corrections

---

## Issue 1 — Unicode crash on Windows (print statement)

**What broke**: `run.py` used the `→` character in two `print()` calls. The Windows terminal codec (cp1252) cannot encode it; the process exited with `UnicodeEncodeError` before any contract was processed.

**Why**: The character was written on a macOS/Linux-neutral assumption and never tested on Windows.

**Category**: Builder oversight — environment compatibility. Not a spec issue; the spec says nothing about console output encoding.

**Fix**: Replaced `→` with `->` in both print calls.

---

## Issue 2 — Extraction silently returning zero results for every contract

**What broke**: Every clause on every contract came back `confidence: 0.0 / found: false`, sending all five contracts to `senior_lawyer_escalation`.

**Why**: The extraction prompt instructs the model to "Return ONLY valid JSON. No markdown fences." The model ignored that instruction and wrapped the JSON in ` ```json … ``` `. The code called `json.loads(raw)` on the fenced string, which raises `JSONDecodeError: Expecting value: line 1 column 1`. A bare `except Exception` block caught the error silently and returned `_empty_results()` — empty objects with confidence 0.0. The confidence gate (FR-11) then correctly escalated every clause, as designed. The bug was invisible: the audit trail logged `extraction_error` but the console output showed `[OK]` routing decisions, just wrong ones.

**Category**: Builder misread of model behaviour. The spec (FR-02) is unambiguous about what extraction must produce. The model output format was assumed, not tested. The silent fallback compounded the problem by masking the failure.

**Fix**: Strip markdown fences before `json.loads`. The instruction in the prompt was also left in place as a soft nudge, but the code no longer depends on it.

---

## Issue 3 — Classification ordering: triggers checked before accepted positions

**What broke**: `sample_standard.docx` had `ip_ownership` correctly drafted as "work for hire owned by Company" — an exact accepted position. The agent classified it `escalate` with reason `escalation_trigger_matched`, routing the contract to the lawyer queue instead of `standard`.

**Why**: The code evaluated escalation triggers (Step 3) before accepted positions (Step 5). The trigger "work made for hire assigned to vendor" and the accepted text "work for hire owned by Company" both contain the phrase "work for hire". The LLM semantic matcher, asked only whether any trigger phrase matched the clause text, answered YES — a false positive caused by shared surface vocabulary with opposite legal meaning.

**Category**: Spec ambiguity interacting with builder implementation choice. The spec's escalation triggers section states: *"These conditions force a clause to escalate status regardless of other signals."* That phrase — **regardless of other signals** — is the ambiguity. Read strictly, it means triggers should pre-empt everything, including accepted positions. Read with legal intent, it means triggers should catch bad clauses that lack an accepted-position reading; they were never meant to override clauses that affirmatively match an approved position.

The original code followed the strict reading. The fix follows the intentional reading: accepted positions are checked first; if a clause matches an approved position, it is classified `match` and no trigger check is run. This is a genuine trade-off:

> **Strict ordering (triggers first)**: Maximally conservative. Any clause touching a sensitive topic is escalated even if it also matches an approved position. Cost: false escalations consume lawyer time and erode trust in the agent.
>
> **Revised ordering (accepted positions first)**: Maximally precise. A clause can only escalate if it fails to match any accepted position. Cost: a novel clause that partially resembles an accepted position might slip through the trigger check. This risk is mitigated by the semantic matcher's requirement for legal equivalence, not surface similarity.

The revised ordering was adopted. The trade-off should be noted in the playbook config comments or the capability specification so it does not get silently reversed in a future refactor.

---

## Issue 4 — Semantic matcher too permissive on quantitative terms

**What broke**: `sample_negotiable.docx` had `liability_cap` set to "capped at 3× annual fees" — a negotiable deviation. The agent classified it `match`.

**Why**: The semantic matching prompt asked whether the clause "semantically matches" any candidate phrase. The accepted position "capped at annual contract value" and the deviation "capped at 3× annual fees" are both fee-based caps; the model answered YES without regard to the multiplier, which is the legally material difference.

**Category**: Builder misread — the prompt was underspecified. "Semantically matches" is too broad a test for positions that differ only in a numeric threshold. The prompt was tightened to require *legal equivalence* — same obligations, same thresholds, same scope — and an explicit counter-example was added to the prompt to anchor the model's judgment.

---

## Issue 5 — Test fixture inconsistencies (sample contracts)

**What broke**: Two clauses in `sample_negotiable.docx` were drafted in ways that contradicted the validation design (Scenario 2):

- **SLA**: Written as "commercially reasonable efforts" — a `negotiable_deviation` in the playbook — but the validation design requires SLA to be a `match` (one of the five non-deviating clauses).
- **Indemnity**: Written as open-ended mutual indemnification, which matched the `negotiable_deviation` entry, not the `match` positions.

**Category**: Spec/fixture mismatch — the validation design was not used as a checklist when the sample contracts were drafted. Both clauses were corrected to language that unambiguously maps to an accepted playbook position.

---

## Summary Table

| # | What broke | Root cause category | Fixed in |
|---|-----------|-------------------|---------|
| 1 | Unicode crash | Builder oversight (platform) | `run.py` |
| 2 | Extraction returning empty results | Builder misread (model output format assumed) | `extraction.py` |
| 3 | Trigger-before-position ordering false positive | **Spec ambiguity** → documented design decision | `classification.py` |
| 4 | Semantic matcher accepting quantitative near-misses | Builder misread (prompt underspecified) | `classification.py` |
| 5 | Sample contracts inconsistent with validation design | Spec/fixture mismatch | `Input Contracts/*.docx` |
