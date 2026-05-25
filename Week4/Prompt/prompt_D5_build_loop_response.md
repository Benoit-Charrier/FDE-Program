# Prompt: Capstone C12 — Build-Loop Reflection

## What this deliverable is

C12 build-loop reflection has two parts:

1. **Signal classification** — apply the 5-category taxonomy to every signal the build loop produced against the D4a (WS1) and D4b (WS2) capability specs. Every signal classified, every classification defended, every spec gap given revised text.

2. **Gap register validation** — compare the signals the build loop surfaced against the pre-documented gaps in `Deliverables/D4_integration_preamble.md` (G-1 through G-6). Did the build loop confirm expected gaps, surface new gaps, or reveal that documented gaps behaved differently than anticipated?

This is not a narrative of what went wrong. The classification is structured and evidenced; the comparison is honest and specific.

---

## Inputs (read all before writing)

- `References/spec-ambiguity-vs-builder-mistakes.md` — the taxonomy, diagnostic decision tree, and response templates. The response templates define the exact format and tone for each category. Do not invent your own format.
- `Deliverables/D4_preamble_capability_spec.md` — shared entity definitions; ground truth for all shared type references (ClaimRecord, AuditLogEntry, CalibrationRecord, EscalationPacket, ResolutionRecord)
- `Deliverables/D4a_capability_spec.md` — WS1 spec built against; primary reference for classifying WS1 signals
- `Deliverables/D4b_capability_spec.md` — WS2 spec; reference for any WS2 signals if WS2 build was attempted
- `Deliverables/D4_integration_preamble.md` — gap register (G-1 through G-6), risk register; the pre-documented known gaps against which the build loop is validated
- `Deliverables/D4_integration_specs.md` — integration contracts for all 16 systems; reference for classifying integration-layer signals and confirming stub behaviour for SCOPE-OUT entries
- `Deliverables/C12_build_loop_start.md` (section **Build Loop Output — Pass 1 (WS1)**) — what was built, questions raised, what could not be built; the raw material for the signal inventory in §1

**Read the taxonomy end-to-end before classifying a single signal.** The most common failure is naming the surface signal ("the integration call failed") without reading the spec alongside the code to determine whether the failure reflects a real gap in the spec's semantics.

---

## The 5 categories

| Category | Signal pattern | Fix owner | Response tone |
|----------|---------------|-----------|---------------|
| **Spec gap** | Build matches the spec as written but not as intended — two valid interpretations existed and the builder chose the wrong one | FDE owns | "I need to revise the spec because the original statement was ambiguous between interpretation A and interpretation B. The correct behaviour is..." |
| **Builder misread** | Build contradicts an explicit, unambiguous statement in the spec | Builder owns | "The spec says [exact quote]. Your implementation does [what it does]. This is a direct contradiction. Please revise to [specific fix]." |
| **Unjustified implementation choice** | Builder added something the spec did not request — not a contradiction, but an unauthorised addition | Collaborative | "This wasn't specified. Before deciding whether to keep it, we need to align: either remove it to stay within spec scope, or if there's a reason for it, let's discuss before committing." Never accusatory. |
| **Test/environment issue** | The build matches the spec; the test expectation is wrong or the environment is misconfigured | Test author owns | "The spec says [X]. The code correctly implements [X]. The test expects [Y], which contradicts the spec. Fix the test, not the code." |
| **Legitimate unknown surfaced correctly** | The spec was silent on something that matters; the builder correctly identified the gap and surfaced it rather than guessing | Shared — acknowledge + revise + confirm | "You're right that the spec didn't address this. The correct behaviour is [X]. I'm adding this to the spec now. Please implement [specific instruction]." |

**The hardest calls:**
- **Spec gap vs. builder misread:** Ask — was the builder's interpretation *defensible* under the spec as written? If yes, it is a spec gap (you own it). If no, it is a builder misread.
- **Design gap vs. legitimate unknown surfaced:** Did the builder implement a guess, or did they surface the question? If they guessed, it is a design gap (spec gap). If they flagged it, it is a legitimate unknown.
- **Unjustified addition vs. builder misread:** A misread contradicts what the spec says. An unjustified addition adds something the spec is silent about. Different tone, different ownership.
- **FM-A-5 / FM-B-5 omission:** These are explicit, unambiguous hard-stop requirements in D4a §11 and D4b §11. A builder who omits them has misread the spec — this is a builder misread, not a spec gap.

---

## Required structure

Output file: append to `Deliverables/C12_build_loop_start.md` after the **Build Loop Output — Pass 1 (WS1)** section

### 1. Signal inventory

List every discrepancy or notable behaviour you identified in the build output. One row per signal.

| Signal ID | What the build produced | What the spec required or intended | First-pass classification |
|-----------|------------------------|------------------------------------|--------------------------|

Include everything — do not filter before classifying. Signals you initially misread are valuable learning data.

### 2. Classified signal responses

For each signal, produce a structured block. Use the response templates from `References/spec-ambiguity-vs-builder-mistakes.md` — do not paraphrase them into vague prose.

```
Signal [S-N]: [one-sentence description of the discrepancy]

Classification: [one of the 5 categories]

Evidence:
- Spec: [exact quote or section reference from D4a/D4b/D4_preamble/D4_integration_specs]
- Build: [what the builder produced that triggered this signal]
- Why this classification and not [the closest alternative]: [one sentence — this is the diagnostic work]

Response:
[The corrective action written in the tone prescribed for this category.
For spec gap / legitimate unknown: write the revised spec text.
For builder misread: write the re-prompt message.
For unjustified addition: write the collaborative removal request.
For test issue: write the test fix instruction.]

Ownership: [FDE / Builder / Collaborative / Test author]
```

### 3. Spec revision log

For every signal classified as **spec gap** or **legitimate unknown surfaced correctly**, record the spec change:

```
Revision [R-N] (for Signal [S-N]):

Section revised: [D4a / D4b / D4_preamble / D4_integration_specs + specific section number]
Original text: "[exact original wording]"
Revised text: "[exact revised wording]"
What the revision prevents: [one sentence — name the specific build failure this wording would have avoided]
Category: [Spec gap — ambiguity resolved / Legitimate unknown — gap filled]
```

### 4. Builder correction memos

For every signal classified as **builder misread**, write the re-prompt as a direct message to the builder:

```
Re-prompt for Signal [S-N]:

The spec states:
"[exact quote from D4a/D4b/D4_preamble/D4_integration_specs]"

Your implementation [does / does not do X]. This directly contradicts the spec.

Please revise:
1. [specific instruction 1]
2. [specific instruction 2]
```

Do not include re-prompts for spec gaps — re-prompting the builder for your own ambiguity is a graded failure mode.

### 5. Gap register validation

Compare the signals from this build loop against the pre-documented gaps in `Deliverables/D4_integration_preamble.md` (G-1 through G-6) and the SCOPE-OUT entries in `Deliverables/D4_integration_specs.md`.

**Gaps confirmed by the build loop**

For each pre-documented gap (G-1 through G-6) or SCOPE-OUT entry that surfaced as a build signal: name the gap ID, the corresponding build loop signal ID, and one sentence on what the build loop revealed that the static gap analysis did not capture.

**New gaps surfaced by the build loop**

For each build loop signal not present in the gap register: state what it is, why it was not visible at spec-reading level, and whether it should be added to D4_integration_preamble.md as a new gap entry (G-7+) or classified as a spec gap owned by the FDE.

**Pre-documented gaps NOT confirmed by the build loop**

For each G-N gap (G-1 through G-6) that did not surface as a build loop signal: state why. Is the gap in a SCOPE-OUT path the builder correctly stubbed? Is it a Wave 2 concern that does not affect the happy path? Is it a discovery gap the builder handled with a `DISCOVERY_REQUIRED` placeholder?

**One-paragraph honest assessment**

Answer directly: which category of gap poses the higher production risk — gaps the build loop confirmed, or gaps the build loop missed entirely? What does the ratio of confirmed vs. missed gaps tell you about the completeness of the pre-build gap analysis, and what additional analysis step would reduce the residual risk most?

---

## Acceptance criteria (all must pass)

- [ ] Every signal identified in the build output has a classified response — no signal left as "unclear"
- [ ] Every classification cites the specific spec section or build output that makes it defensible — no assertions without evidence
- [ ] The "Why this classification and not X" line is present for every signal — the diagnostic work is visible, not implied
- [ ] Response tone matches the category exactly: spec gaps use first-person revision language; builder misreads use direct correction; unjustified additions use collaborative framing; test issues fix the test not the code
- [ ] Every spec gap and legitimate unknown has a revised spec text in Section 3 — not "I would clarify this" but the actual revised wording
- [ ] Every builder misread has a direct re-prompt in Section 4 — specific, citing the spec, stating the exact fix
- [ ] No re-prompt written for a spec gap — the builder cannot fix your ambiguity
- [ ] Signal inventory is exhaustive — signals are not pre-filtered before classification
- [ ] Section 5 references every pre-documented gap (G-1 through G-6) by ID — no gap unaccounted for
- [ ] Section 5 accounts for every build loop signal — no signal left out of the gap register validation
- [ ] The one-paragraph assessment takes a position: names which gap category (confirmed vs. missed) poses the higher production risk — not "all gaps matter equally"

## Fail signals — do not produce output that contains these

- Classifying a signal without reading the spec section it relates to — surface-level diagnosis fails
- "The builder got it wrong" for a spec that was genuinely ambiguous — if the builder's reading was defensible, you own the fix
- Re-prompting the builder for a spec gap — the builder cannot correct for your ambiguity
- Spec revision that says "add more detail" or "be clearer about X" without providing the actual revised text
- Treating every signal as a builder misread — a fixture with no spec gaps is not a realistic or honest diagnosis
- Treating every signal as a spec gap — a fixture with no builder errors is also not realistic
- Conflating unjustified addition with builder misread — different ownership and different tone
- Classifying a legitimate unknown as a spec gap — spec gap means ambiguity existed; legitimate unknown means the spec was simply silent; the corrective response is different
- Missing signals that are present in the build output — an incomplete signal inventory means some build failures would go uncorrected
- Classifying FM-A-5 or FM-B-5 omission as a spec gap — both hard stops are explicit and unambiguous in D4a §11 and D4b §11; omission is a builder misread
- Section 5 that lists pre-documented gaps without explaining why each one did or did not surface — the comparison requires a reason, not just a match/no-match
- A one-paragraph assessment that concludes "confirmed and missed gaps are equally important" — the question asks which poses the higher production risk; answer it
