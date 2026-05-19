# Prompt: Gate 4 D7 — Build-Loop Reflection

## What this deliverable is

Gate 4 D7 is a build-loop reflection on a peer's spec. It has two parts:

1. **Signal classification** — apply the 5-category taxonomy to every signal the build loop produced against Dmytro's intake spec. Same rigour as a D5 diagnostic memo: every signal classified, every classification defended, every spec gap given revised text.

2. **Peer review vs. build loop comparison** — compare the signals the build loop surfaced against the findings in your D3 peer review of the same spec. What did the peer review catch that the build loop didn't? What did the build loop surface that the peer review missed? What does that tell you about the relative value of each method?

This is not a narrative of what went wrong. The classification is structured and evidenced; the comparison is honest and specific.

---

## Inputs (read all before writing)

- `references/spec-ambiguity-vs-builder-mistakes.md` — the taxonomy, diagnostic decision tree, and response templates. The response templates define the exact format and tone for each category. Do not invent your own format.
- Dmytro's intake spec (`Spec_review_input1/04a-capability-spec-intake-Dmytro.md`) — the spec the build loop ran against
- The D7 build loop output (`Deliverables/Gate4_D7_build_loop_reflection.md`, section **Build Loop Output**) — what was built, questions raised, what could not be built; this is the raw material for the signal inventory in §1
- Your D3 peer review of this spec (`Deliverables/Gate4_D3_peer_review_portfolio.md`, Spec 1 section) — the findings from the peer review that the build loop should be compared against

**Read the taxonomy end-to-end before classifying a single signal.** The most common failure is naming the surface signal ("the test is wrong") without reading the spec alongside the code to determine whether the test reflects a real gap in the spec's semantics.

---

## The 5 categories

| Category | Signal pattern | Fix owner | Response tone |
|----------|---------------|-----------|---------------|
| **Spec gap** | Build matches the spec as written but not as intended — two valid interpretations existed and the builder chose the wrong one | FDE owns | "I need to revise the spec because the original statement was ambiguous between interpretation A and interpretation B. The correct behaviour is..." |
| **Builder misread** | Build contradicts an explicit, unambiguous statement in the spec | Builder owns | "The spec says [exact quote]. Your implementation does [what it does]. This is a direct contradiction. Please revise to [specific fix]." |
| **Unjustified implementation choice** | Builder added something the spec did not request — not a contradiction, but an unauthorised addition | Collaborative | "This wasn't specified. Before deciding whether to keep it, we need to align: either remove it to stay within spec scope, or if there's a reason for it, let's discuss before committing." Never accusatory — you're not saying the builder was wrong, you're saying the scope boundary wasn't respected. |
| **Test/environment issue** | The build matches the spec; the test expectation is wrong or the environment is misconfigured | Test author owns | "The spec says [X]. The code correctly implements [X]. The test expects [Y], which contradicts the spec. Fix the test, not the code." |
| **Legitimate unknown surfaced correctly** | The spec was silent on something that matters; the builder correctly identified the gap and surfaced it rather than guessing | Shared — acknowledge + revise + confirm | "You're right that the spec didn't address this. The correct behaviour is [X]. I'm adding this to the spec now. Please implement [specific instruction]." |

**The hardest calls:**
- **Spec gap vs. builder misread:** Ask — was the builder's interpretation *defensible* under the spec as written? If yes, it is a spec gap (you own it). If no, it is a builder misread.
- **Design gap vs. legitimate unknown surfaced:** Did the builder implement a guess, or did they surface the question? If they guessed, it is a design gap (spec gap). If they flagged it, it is a legitimate unknown.
- **Unjustified addition vs. builder misread:** A misread contradicts what the spec says. An unjustified addition adds something the spec is silent about. Different tone, different ownership.

---

## Required structure

Output file: append to `Deliverables/Gate4_D7_build_loop_reflection.md` after the **Build Loop Output** section

### 1. Signal inventory

List every discrepancy or notable behaviour you identified in the build output. One row per signal.

| Signal ID | What the build produced | What the spec required or intended | First-pass classification |
|-----------|------------------------|------------------------------------|--------------------------|

Include everything — do not filter before classifying. Signals you initially misread are valuable learning data.

### 2. Classified signal responses

For each signal, produce a structured block. Use the response templates from `references/spec-ambiguity-vs-builder-mistakes.md` — do not paraphrase them into vague prose.

```
Signal [S-N]: [one-sentence description of the discrepancy]

Classification: [one of the 5 categories]

Evidence:
- Spec: [exact quote or section reference that makes this classification defensible]
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

Section revised: [which spec section]
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
"[exact quote]"

Your implementation [does / does not do X]. This directly contradicts the spec.

Please revise:
1. [specific instruction 1]
2. [specific instruction 2]
```

Do not include re-prompts for spec gaps — re-prompting the builder for your own ambiguity is a graded failure mode.

### 5. Peer review vs. build loop comparison (D7 deliverable)

This is the core of D7. Compare the signals from the build loop against the findings from the D3 peer review of the same spec. Be specific — name each finding by its ID (B1–B5, C1–C3 from the peer review; S-N from the build loop).

**What the build loop caught that the peer review also caught**

For each overlapping finding: name the peer review ID, the build loop signal, and one sentence on why both methods converge on this issue. Convergence signals high-confidence blockers.

**What the peer review caught that the build loop missed**

For each peer review finding (B1–B5, C1–C3) that did not surface as a build loop signal: state why the build loop would not surface it. Is it a logic error only visible at spec-reading level? A missing config parameter that a builder would hardcode silently? A cross-contract inconsistency only visible when reading the full spec rather than building one component?

**What the build loop surfaced that the peer review missed**

For each build loop signal not present in the peer review: state what it is and why the peer reviewer would have missed it. Is it an environment-specific issue? An implementation choice the spec leaves open that only becomes visible when you commit to code?

**One-paragraph honest assessment**

Answer directly: which method caught the issues most likely to cause silent wrong behaviour in production — the peer review or the build loop? What does this fixture tell you about the limits of each method, and what would a complete spec-validation process look like that uses both?

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
- [ ] Section 5 comparison references every D3 peer review finding by ID (B1–B5, C1–C3) — no finding unaccounted for
- [ ] Section 5 comparison references every build loop signal — no signal left out of the comparison
- [ ] The one-paragraph assessment takes a position: it names which method is better for which category of issue, not "both methods are complementary"

## Fail signals — do not produce output that contains these

- Classifying a signal without reading the spec section it relates to — surface-level diagnosis fails
- "The builder got it wrong" for a spec that was genuinely ambiguous — if the builder's reading was defensible, you own the fix
- Re-prompting the builder for a spec gap — the builder cannot correct for your ambiguity
- Spec revision that says "add more detail" or "be clearer about X" without providing the actual revised text
- Treating every signal as a builder misread — a fixture with no spec gaps is not a realistic or honest diagnosis
- Treating every signal as a spec gap — a fixture with no builder errors is also not realistic
- Conflating unjustified addition with builder misread — different ownership and different tone; getting this wrong produces an accusatory response for something that may be a reasonable suggestion
- Classifying a legitimate unknown as a spec gap — the distinction matters: spec gap means ambiguity existed; legitimate unknown means the spec was simply silent; the corrective response is different
- Missing signals that are present in the build output — an incomplete signal inventory means some build failures would go uncorrected
- Section 5 that lists peer review findings without explaining why each one did or did not surface in the build loop — the comparison requires a reason, not just a match/no-match
- A one-paragraph assessment that concludes "both methods are complementary" without naming which is better for silent-failure detection — that is the specific question; answer it
