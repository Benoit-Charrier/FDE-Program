# Peer Feedback — Alexandra Rendon, Week 2
**Reviewer**: Benoit Charrier  
**Date**: 2026-04-30  
**Scenario**: Scenario 5 — Westbridge Family Medicine Patient Intake

---

## Specific Gaps

### Gap 1 — The autonomy matrix conflates "recommendation without pre-approval" with "fully agentic"

**Where**: `scenario5-agent-mapping-pa-chase.md`, Section 3 Autonomy Matrix — "AGENT DECIDES ALONE: Production-Phase Chase Recommendations."

**The problem**: The agent never executes a PA chase — Dana always places the call or sends the portal message. "Fully agentic" conventionally means the agent completes the end-to-end process without a human step. What you've actually designed is: agent autonomously decides when to recommend, Dana autonomously decides whether to act on it (no approval workflow in production). That is "Fully Agentic recommendation generation + Human executes." These are not the same thing.

A coding agent reading "AGENT DECIDES ALONE" on chase recommendations might build an automated outreach pathway to insurer portals (technically possible from athenahealth) rather than a dashboard notification to Dana. Nothing in the current spec explicitly closes that door.

**Minimum fix**: Add one line to the production-phase section: *"'Fully Agentic' here refers to recommendation generation only. Execution (phone call, portal message) remains human-only in all phases. Coding agent must not implement direct insurer contact."* This prevents a delegation boundary failure that your own S-3 test scenario (from a hypothetical D8) would catch.

---

### Gap 2 — The build test suite has no anti-assertion for the Aetna escalation

**Where**: `BUILD_SUMMARY.md`, Test Suite / `tests/test_agent.py`; `scenario5-agent-mapping-pa-chase.md`, Section 1 Escalation Triggers.

**The problem**: The test confirms PA-004 (Aetna) produces `action=ESCALATE`. It does not confirm that `chase_date` is `None`. A cheaper implementation could pass your current test by producing `{action: ESCALATE, chase_date: 2026-05-02, confidence: low}` — the escalation flag is set, but a chase date is still calculated and might be rendered in Dana's dashboard. Over time that "informational" chase date drifts into being acted on.

The escalation trigger for Aetna in your spec says "no stable pattern available" — so producing a chase_date at all would be architecturally wrong, not just suboptimal.

**Minimum fix**: Add to the Aetna test case:
```python
assert rec.action == ActionType.ESCALATE
assert rec.chase_date is None  # anti-assertion: no date produced for unpredictable insurer
assert rec.confidence == ConfidenceLevel.LOW or rec.confidence is None
```
Also add the same anti-assertion for the "unknown insurer" case (PA-008, Cigna).

---

### Gap 3 — The "allergy conflict flagging" micro-task has inconsistent cognitive load scoring

**Where**: `scenario5-cognitive-map.md`, Section 2 Micro-Task Inventory — row "Flag allergy conflicts."

**The problem**: The table scores this task as Cognitive Load: **M** (Medium), Decision Determinism: **H** (High), then Section 6 assigns it "Fully Agentic" with the rationale "rule-based, deterministic, high-consequence (must be 100% reliable)." A medium cognitive load under the ATX framework would normally push toward Agent-led + Human Oversight. The Fully Agentic assignment is correct — allergy matching is deterministic rule-evaluation — but the cognitive load score doesn't support it. The mismatch will be confusing to anyone reading the delegation assignment against the scoring table.

**Minimum fix**: Change "Flag allergy conflicts" cognitive load from M to L in the micro-task table. Add a note: *"LOW cognitive load for agent (deterministic rule evaluation); HIGH clinical consequence requires a reliable rule implementation, not HITL."* This also removes a signal that could make a coach or reviewer question why the boundary is where it is.

---

### Gap 4 — Wave 1 ROI is presented as -42% Year 1 without a breakeven scenario

**Where**: `scenario5-phase4-prioritization.md`, Step 3 TCO — JtD-2 ROI Calculation.

**The problem**: The -42% Year 1 ROI is an honest number, but the "strategic justification" for proceeding is primarily qualitative (institutional knowledge capture, Dana's career timeline). The document does not show what Dana's PA time would need to be for the economics to pass Year 1 — a credible executive sponsor will ask this. Given the formula `$20,897/year / $36,000 build cost = 20.6 months payback`, a Dana time of 2.5 hours/day (not 1.5 hours) would yield `$34,375/year`, dropping payback to ~12.5 months and Year 1 ROI to near break-even.

The validated number is "1-2 hours/day" (Q18). If she routinely runs 2 hours rather than 1.5, the economics already improve significantly. Not showing this range weakens the business case for Wave 1 at a stakeholder review.

**Minimum fix**: Add one paragraph to the Wave 1 strategic justification: *"Sensitivity: if Dana's PA time averages 2 hours/day (upper bound of Q18 range), annual saving increases to $27,500, payback drops to 15.6 months, Year 1 ROI = -24%. At 2.5 hours/day (scenario where visit-abort coordination is included), payback = 12.5 months, Year 1 ROI near break-even."*

---

## Delegation-Archetype Calibration

This submission does not default to "fully agentic." It is one of the stronger examples of genuine archetype differentiation I've seen.

JtD-3 (visit reason triage) being held at **Human-led + Agent Support** is the right call, and the justification is crisp: [A13] draws an explicit line between recognition (agent-safe) and severity assessment (clinician-only). That line was not invented — it was elicited in the coach role-play (Q13: "Recognition → escalate. Assessment → clinician."). This is the correct methodology.

JtD-2's phased archetype (Agent-led + Human Oversight → Fully Agentic for predictable insurers) is well-reasoned, and the anti-pattern check in Phase 3 (Section 3) explicitly addresses whether a rule-based system would suffice instead — and argues correctly that it would not. The only gap is the "fully agentic" labeling issue noted in Gap 1 above.

One calibration concern: JtD-4 (medication reconciliation) is assigned **Agent-led + Human Oversight (perpetual)** with the physician always reviewing flagged discrepancies. This is correct, but the CLAUDE.md for the project doesn't make this a hard constraint the way ET-2 is a hard constraint in a well-designed CLAUDE.md. It's mentioned in the agent mapping but not as a non-negotiable guardrail. A coding agent building the Write operation to athenahealth's med list field would have no explicit spec-level prohibition to stop it.

---

## Lived-Work vs. Documented-Process

Section 4 (Lived Process Narrative) is the strongest section of the submission. The five gaps between SOP and lived reality are specific, evidence-backed, and structurally important to the agent design.

The best example is Gap 2 (Dana's insurer-specific chase timing). The contrast between "follow up at stated SLA (5 days)" and "Humana always exactly 6 days; never 5" backed by Artefact 5.1 is exactly what ATX cognitive mapping is for. The observation that this pattern "lives in Dana's head and Google Sheet, not in athenahealth, not in any SOP" directly drives the institutional knowledge capture argument for Wave 1.

Gap 5 (post-incident learning doesn't scale) is a useful observation but doesn't connect to an agent design decision — it's a diagnosis without a prescription. If this knowledge institutionalization failure motivates anything, it should motivate the HITL feedback loop design more explicitly. Consider noting that the agent's correction-learning pipeline (pattern library updates → Dana approval) is precisely the mechanism that replaces Dana's informal learning loop.

The medication reconciliation section (Gap 4) acknowledges upfront: *"Unknown from artefacts — we don't have visibility into where DoseSpot misses things."* This is appropriately honest, and the subsequent coach validation ([A6], Q14/Q17) fully resolved it. The discipline of flagging the unknown before filling it is the right pattern.

---

## Strength to Preserve

**The coach role-play integration is the standout element of this submission.** Not just that it was done, but how it was used: 24 specific questions, documented answers (`coach-roleplay-answers.md`), confidence levels updated with directional indicators (HIGH ⬆️, VERY HIGH ⬆️⬆️⬆️), and — most importantly — the wave sequencing was revised based on what was learned (Q18 answer swapped Waves 1 and 2). That last step is the one most participants skip: they do the discovery, they log it, but they don't let it change the design.

Preserve this format: assumption tagged to a question, confidence level before and after, update to the design decision it affects. This is what "honest assumptions and unknowns" looks like in practice.

---

## Gate 2 Calibration

This submission is tracking toward a Gate 2 pass — the delegation boundaries are defensible, the lived-work analysis is genuine, and the assumptions register is evidence-backed rather than filler — but Gap 1 (the "fully agentic" labeling issue) needs to be resolved before the spec would be precise enough to hand to a coding agent without causing a delegation boundary failure.
