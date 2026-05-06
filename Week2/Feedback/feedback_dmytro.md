# Peer Feedback — Dmytro | Scenario 4: MiniBase Community Content Moderation

---

## Executive Summary

- **Overall calibration:** This submission is tracking toward a **Gate 2 pass**. The single most important reason is the exceptional assumption discipline and the precisely consistent agent scope boundary — both of which are the most common failure modes at this stage, and both are handled correctly here.
- **Most critical gap:** The V×V analysis renames the Value dimension "Non-Determinism Score," which creates a framing risk: for WS4 (IP Claims), the work's organizational value is partially about legal and commercial stakes, not only about non-determinism — renaming the axis risks under-articulating what actually drives the economic case, and may not match rubric terminology. Fix this before Friday.
- **Primary strength to preserve:** The Lived vs. Documented Process section in the CLM is the strongest demonstration of this skill in this cohort's submissions. Seven named deviations, each grounded in specific artefact evidence, with the cross-cultural communication point (#7) reaching a level of analytical depth that is rare. Carry this same evidence-first instinct into all future deliverables.

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Delegation-Archetype Calibration Comment](#delegation-archetype-calibration-comment)
3. [Lived-Work vs. Documented-Process Comment](#lived-work-vs-documented-process-comment)
4. [Gap 1 — V×V Axis Framing: "Non-Determinism" vs. "Value"](#gap-1--vv-axis-framing-non-determinism-vs-value)
5. [Gap 2 — KPI Measurement Disconnect: Completeness ≥95% Has No Operational Anchor](#gap-2--kpi-measurement-disconnect-completeness-95-has-no-operational-anchor)
6. [Gap 3 — WS3 Archetype Rationale Omits the Community-Trust Dimension](#gap-3--ws3-archetype-rationale-omits-the-community-trust-dimension)
7. [Gap 4 — Three TBD SLAs Leave Builders Without a Safe Default](#gap-4--three-tbd-slas-leave-builders-without-a-safe-default)
8. [Strengths](#strengths)
9. [One-Sentence Calibration Note](#one-sentence-calibration-note)

---

## Delegation-Archetype Calibration Comment

**This submission does not exhibit the "everything fully agentic" anti-pattern.** The matrix assigns four different archetypes across four work streams, and the zero fully-agentic assignments are explicitly justified rather than conservative by default:

- **WS1 (Human-led + Automation Support)** is the correct call and the call most participants get wrong. The reasoning — Decision Determinism = High means a rules engine outperforms an LLM here; the LLM adds hallucination risk at the exception routing step without adding value — is exactly the line of argument the rubric expects.
- **WS2 (Human-led + Agent Support)** is justified by five named driving dimensions, including the distinction between the preparation work (automatable) and the judgment core (steps 10–12, undelegatable). The asymmetric risk framing (Tom's stated FN/FP asymmetry) is correctly threaded from the JTBD through the archetype to the autonomy matrix.
- **WS4 (Human-only)** includes the ROI argument (3–5 cases/week, payback measured in years for even partial automation) in addition to the dimension analysis. That dual justification — dimension-based AND economic — is a sign of mature ATX reasoning.

The one calibration note: WS3 gets the same archetype as WS2 but with a thinner rationale. See Gap 3.

---

## Lived-Work vs. Documented-Process Comment

**The CLM clearly and consistently reflects what humans actually do, not what the SOP claims they do.** The Lived vs. Documented Process section identifies seven specific deviations from the written policy, each with artefact-grounded evidence:

- The shadow governance layer (Tom's private Google Sheet overriding the 14-page policy) is the core structural insight and is correctly named as the failure mode that would doom an agent built from the policy alone.
- The three-tier user model (Tier 1/2 in the Sheet, Tier 3 nowhere) is handled with appropriate nuance — the submission doesn't pretend the problem is solved; it names it as a MISSING data source and traces it through to the SDI, the APD failure modes, and the discovery questions.
- The cross-cultural interpretation point (#7) goes beyond what most participants surface from this scenario. The observation that UK, German, Australian, and Japanese moderators apply systematically different harshness thresholds with no structured calibration — and that this isn't acknowledged anywhere in the written policy — is the kind of lived-process insight that distinguishes strong ATX analysis.

One minor note: the CLM's WS4 step 4 score note states that "triage criteria live in Tom's head" and cites `stakeholders_quiz Q3` — correct — but doesn't name what a moderator observer would *see* in practice (i.e., Tom reading past email threads, cross-referencing his own memory of @sculpturedragon's prior claims). The micro-task description would be slightly stronger if it described what the observable inputs are, even when they're tacit.

---

## Gap 1 — V×V Axis Framing: "Non-Determinism" vs. "Value"

**What the submission does:** The V×V analysis labels the Y-axis "Non-Determinism Score" and scores WS1 as ND=1 and WS4 as ND=5. The scores are internally consistent and the work-stream selection is correct.

**Why this is a gap:** The ATX methodology frames the Y-axis as **Value** — capturing the organizational and economic difficulty of the work, including judgment complexity, regulatory sensitivity, and relationship stakes. Non-determinism is *one component* of value, but not all of it. For WS4 (IP Claims), the reason the work is hard to delegate is not only that decisions are non-deterministic — it's also that a wrong call carries legal and sponsor-relationship consequences that are organizationally costly in ways that go beyond the difficulty of the decision itself. Renaming the axis "Non-Determinism" obscures this economic dimension. It also risks rubric mismatch if assessors are checking for the standard V×V framing.

**Minimum-change fix:** Add one sentence to the V×V Scoring Notes section stating explicitly that "Non-Determinism Score is used here as the primary proxy for the Value dimension, reflecting the difficulty of encoding judgment; organizational risk and compliance stakes are treated as amplifiers of value rather than scored separately." Then confirm the terminology matches the rubric language in the Gate 2 materials. This is a 3-minute fix that removes the risk.

---

## Gap 2 — KPI Measurement Disconnect: Completeness ≥95% Has No Operational Anchor

**What the submission does:** The APD states the KPI "Context brief completeness ≥95%" measured by "% of briefs with no silently-omitted fields." The Implementation Specification defines a `brief_completeness_score` field (0–100) that scores eight data groups at 12.5 points each, with 0 only when a lookup was skipped entirely (not when it returned null/not-found).

**Why this is a gap:** The KPI as stated and the implementation-level measurement are disconnected. The KPI says "no silently-omitted fields," but the completeness score in the `ContextBrief` interface uses a different logic (group-level scoring, skipped vs. not-found distinction). An operator monitoring the ≥95% KPI doesn't know whether to watch `brief_completeness_score ≥ 95`, count briefs with `missing_fields.length = 0`, or use some other derived measure. This ambiguity means the KPI is not independently verifiable after deployment — which undermines it as a governance mechanism.

**Minimum-change fix:** Add one line to the KPI table's Measurement column: "A brief passes when `brief_completeness_score ≥ 95` AND `missing_fields` contains no skipped-lookup entries (distinguished from not-found entries by the scoring logic in the Implementation Specification)." This ties the high-level KPI to the specific implementation field and makes the target auditable.

---

## Gap 3 — WS3 Archetype Rationale Omits the Community-Trust Dimension

**What the submission does:** The WS3 archetype (Human-led + Agent Support) is justified with two rationale sections — "Driving dimensions" and "Driving dimensions that keep it Human-led rather than Agent-led." The second section focuses on Decision Determinism = Low and the communication drafting step.

**Why this is a gap:** The rationale correctly identifies *that* WS3 resists full delegation, but it doesn't articulate *what is different* about WS3 compared to WS2 at the same archetype level. The real differentiator is that a WS3 overturn is a public signal to the community about the reliability of the moderation system — a wrongly-upheld appeal (false-negative for the appellant) or a wrongly-overturned decision (false-positive for the community) both carry **community trust risk** that is qualitatively different from the content-decision risk in WS2. Tom's stated asymmetry doesn't map cleanly onto WS3 in the same way; the WS3 asymmetry is bi-directional (both types of error are visible and damaging). This dimension is implied but never named.

**Minimum-change fix:** Add one sentence to the WS3 rationale: "Unlike WS2, WS3 errors are bi-directional in community trust impact — a wrongly-upheld appeal is as damaging as a wrongly-overturned one; this makes automated decision-making at steps 8–9 inappropriate even at higher maturity, and is the reason WS3 does not have a clear upgrade path to Agent-led." This single sentence distinguishes WS3 from WS2 at the same archetype level and adds a future-state observation.

---

## Gap 4 — Three TBD SLAs Leave Builders Without a Safe Default

**What the submission does:** Three escalation triggers in the APD are correctly left as TBD, referencing Discovery Question Q1 for resolution. This is the right call per assumption discipline — inventing SLAs would produce a spec that looks complete but would fail operationally.

**Why this is still a gap:** The TBD entries specify what *will be* set once Q1 is answered, but don't specify what a builder should do if Q1 is never answered before go-live. Should the escalation trigger be disabled? Should a conservative default be applied (e.g., 60 minutes for moderator inaction)? Should the deployment be blocked? For a builder receiving this APD, the absence of a safe-default instruction means they will either invent a value (unsafe) or leave the trigger unimplemented (also unsafe). The APD has the right instinct (don't invent) but needs to give builders a fallback instruction.

**Minimum-change fix:** Add one line to each of the three TBD escalation triggers: "Builder instruction: if Q1 is not answered before go-live, treat this trigger as a **deployment blocker** — do not deploy the escalation module until an SLA value is confirmed by Tom." This is honest (it names the unresolved state), protective (it prevents builders from inventing values), and operationally clear.

---

## Strengths

**1. Assumption discipline is the standard for this cohort.** Twenty-one named assumptions (A-1 through A-21) in CLAUDE.md, each with confidence level, scenario source, and a specific test method naming the discovery question or validation event. The format is consistently applied across all deliverables — every `[Assumed]` tag in the APD traces back to a numbered assumption with explicit confidence. This is what the rubric means by "assumption discipline," and it's done right.

**2. The Lived vs. Documented Process section sets the bar for evidence-grounded CLM work.** Seven specific deviations from the written policy, each traceable to artefact evidence by number. The cross-cultural interpretation point (#7) — the observation that a UK moderator reading a German poster and a Japanese moderator reading the same post apply structurally different thresholds, and the policy doesn't acknowledge this anywhere — is the kind of latent-system insight that most participants in this exercise don't surface. It reaches the "shadow governance" level of the work. Carry this instinct forward.

**3. The agent scope boundary is consistently enforced across all deliverables.** The "no content decisions under any condition" principle appears in the APD Purpose Statement, Autonomy Matrix, CLAUDE.md Key Design Decisions, the DSM delegation boundaries, and the CLAUDE.md Build Loop Instructions. Every instance is consistent. This is not easy to achieve in a multi-deliverable submission and is the primary indicator that the participant understands why the boundary exists, not just that one exists.

---

## One-Sentence Calibration Note

This submission is tracking toward a **Gate 2 pass as currently drafted** — the structural methodology is sound, the anti-patterns are avoided, and the assumption discipline is strong; the three fixes above are presentation-level corrections, not methodological gaps.
