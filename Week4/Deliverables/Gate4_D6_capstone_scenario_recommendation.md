# Gate 4 — Capstone Scenario Recommendation

*Date: May 19, 2026*

---

## Recommendation: Option A — Healthcare Claims Processing

---

## Analysis

### Why A over B and C

**1. Domain momentum works in your favour**
Week 4 work (MedFlex, WS2 nurse-to-shift matching) is healthcare — coordinator economics, clinical delegation boundaries, credential gate logic. Claims processing is the same regulatory and human-oversight territory. Monday–Tuesday of Week 5 allows only 2 days to produce 11 design deliverables. Domain fluency is time. Options B and C require a cold start on the subject matter.

**2. The economic case is the strongest and most calculable**
22% → 85% auto-adjudication on 2,000 claims/day × 35 min/claim is a large, concrete denominator. The baseline cost per claim in processor time is calculable; the delta is unambiguous. A token economics model for this scenario follows the same structure as the MedFlex model already completed this week. Option B's ROI was explicitly challenged as "vague" by the CFO in the stakeholder exchange. Option C's economics depend on NPS improvement, which is harder to translate into a 3-year ROI model.

**3. The delegation architecture is forced and specific — ideal for the rubric**
The CMO/CFO tension in Option A resolves to exactly the distinction the rubric tests: *what should be agentic, what should stay human?*
- Clinical content classification = AI (free-text NLP, requires contextual reasoning — Sonnet-tier)
- Eligibility check, coding validation, completeness check = deterministic (Haiku-sufficient)

The 35%/65% physician-review split is already in the stakeholder exchanges, providing a concrete capability spec anchor. The delegation boundary is not invented — it was negotiated by the stakeholders themselves.

**4. The prototype arc covers all three required paths cleanly**

| Path | Description |
|------|-------------|
| **Happy path** | Administrative claim → completeness check (Haiku) → clinical content classifier (Sonnet) → non-clinical → auto-approved with audit record |
| **Failure-mode escalation** | Clinical content flagged → pre-filled review packet routed to physician HITL queue |
| **Edge case** | Classifier confidence below threshold → escalates with uncertainty flag; prevents silent misclassification |

All three are runnable against mock claim data (EDI 837 or simplified JSON). All three are completable in under 5 minutes of live demo.

**5. Curveball resilience**
The most likely curveball for Option A: *"The CMO just blocked all AI-assisted denial decisions."* The design already has a HITL architecture — the agent's delegation level shifts from auto-approve to accelerate-physician-queue. The agent does not disappear; it becomes a different kind of value (pre-filling context, reducing physician review time from 35 min to ~3 min per claim). The core architecture survives.

- Option B curveball (CISO pulls approval): kills the on-prem architecture and the entire deployment path.
- Option C curveball (CFPB bans automated refund decisions): hits the primary demo path directly.

---

### Why not Option B — Enterprise Procurement Intelligence

- The CFO in the exchange explicitly challenged the $2.5M ROI projection as "vague." Defending the economics will consume design time better spent building.
- The primary agentic capability (negotiation research briefing) sits closer to RAG + retrieval than autonomous decision-making. The automatic-fail criterion is "built a traditional rules engine instead of an agentic solution" — a briefing generator is close to that boundary.
- Knowledge capture from retiring employees does not demo well. There is no runnable agent interaction that is compelling in 5 minutes of live demo.
- The CISO security architecture (on-prem, encrypted, no cloud LLM) adds significant build complexity for a week-long prototype.

### Why not Option C — Multi-Channel Customer Resolution

Strong second choice. The delegation logic is clean (password resets → no HITL; refunds → HITL), the volume is concrete (4,500/day), and the stakeholder resolution is workable. Reasons Option A is stronger given Week 4 context:

- The CTO infrastructure constraint (Avaya 2010, 6-month rebuild) forces a two-track architecture narrative (platform migration + agent deployment) that complicates the design deliverables and the `CLAUDE.md`.
- Financial services CFPB/state banking compliance is an additional scope layer hard to cover honestly in 4 days of design.
- Six separate systems of record add integration complexity to the prototype that is not present in Option A.
- If financial services background from prior roles makes this domain familiar, Option C becomes competitive. Against this week's healthcare context, Option A has the edge.

---

## Summary

| Criterion | Option A | Option B | Option C |
|-----------|:--------:|:--------:|:--------:|
| Domain familiarity from Week 4 | High | Low | Medium |
| Economic case clarity | High | Low | Medium |
| Delegation boundary specificity | High | Medium | High |
| Prototype arc completeness | High | Low | High |
| Curveball resilience | High | Low | Medium |
| Build complexity | Medium | High | High |

**Pick Option A.** The domain advantage accelerates the compressed Mon–Tue design sprint, the economics are the most defensible, and the clinical/administrative delegation distinction is the clearest possible answer to the question the rubric is asking.
