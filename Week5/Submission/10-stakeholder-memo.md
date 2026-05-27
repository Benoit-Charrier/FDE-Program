# C10: Stakeholder Alignment Memo
**Engagement:** Greenfield Health Systems — Medical Claims Adjudication Transformation
**Prepared:** 2026-05-22

---

**TO:** Sarah Chen (CFO), Dr. Marcus Webb (CMO), James Liu (VP Operations)
**FROM:** Benoit Charrier, FDE
**DATE:** 2026-05-22
**RE:** Stakeholder Alignment — Agentic Claims Processing Transformation

---

## SITUATION SUMMARY

Greenfield Health Systems processes approximately 2,000 claims per day at an 8–9 day average cycle time — exceeding the 7-day contractual SLA threshold and incurring active financial penalties. The auto-adjudication rate of 22% sits 63 points below the 85% industry benchmark, not because the work is complex but because all claims enter the same full-manual workflow regardless of whether they require clinical judgment. A $400,000 budget has been committed for an agentic transformation. The core tension is not whether to automate — all three stakeholders agree that automation is necessary — but where the automation boundary sits: specifically, which claim types require physician review, and what "clinical content" means precisely enough to build a reliable classifier.

---

## STAKEHOLDER POSITIONS

**Sarah Chen (CFO):** The project is financially justified only if it achieves a 40% reduction in claims review headcount — 8 FTEs over 6 months. The financial case depends on the agent handling the majority of claim volume without physician involvement on each claim. The $400K budget is committed but fixed; material overruns require board approval.

**Dr. Marcus Webb (CMO):** A physician or advanced practice provider must review every claim with genuine clinical content before a coverage determination is made. This is not a design preference — it is a URAC/NCQA accreditation requirement, and his team will not certify any system that bypasses clinical review. He accepts agent-handled administrative checks (eligibility, coding, prior auth completeness) and estimates that approximately 30–35% of claims have genuine clinical content. He also requires that "clinical content" be formally defined before any routing automation is built or certified; without that definition, no classifier can be built or held accountable.

**James Liu (VP Operations):** Claims are averaging 9+ days, penalty exposure is active, and speed is needed now. The 7-day SLA threshold is a hard commercial commitment. A solution that brings cycle time below 7 days on the majority of claims — even if some claims remain on a physician review path — addresses the immediate penalty risk, provided the clinical review path does not itself become a bottleneck.

---

## THE CORE TENSION

The conflict is not between cost and quality — it is about where the routing boundary sits and whether it can be enforced reliably. Sarah Chen's cost model requires that the agent handle a substantial majority of claims autonomously. Dr. Marcus Webb's compliance requirement means that every claim with clinical content must receive physician review regardless of the agent's confidence level. James Liu's SLA requirement means that physician review, if it remains in the pipeline, must be faster than today's 35-minute-per-claim manual process.

These positions are compatible on one condition: that the clinical content classifier is reliable enough to concentrate physician review on a genuinely bounded clinical subset — and that pre-screened claims can be reviewed significantly faster than unscreened ones. The unresolved issue is the size of that subset. Dr. Webb's estimate of 30–35% has not been validated against historical claim data; this uncertainty is the primary risk to the economic model.

---

## PROPOSED RESOLUTION

**Wave 1 (Months 1–6):** Build and deploy the administrative adjudication agent for the estimated 65% of claims on the administrative path. The agent runs eligibility verification, coding validation, prior authorisation checks, and clinical content routing classification. Claims classified as administrative proceed to automated payment determination; claims classified as clinical route to the physician review queue.

Two preconditions must be satisfied before go-live:

1. **Clinical content definition.** A formal definition of "clinical content" must be produced as a joint design output with CMO sign-off. This definition is the input to the classifier and the baseline for certification. It is the critical-path item for Wave 1 and must be completed within the first 6 weeks of the design phase.
2. **Classifier calibration gate.** The clinical content classifier must achieve ≥99.5% recall on clinical claims in mock calibration testing — meaning it correctly identifies at least 995 out of every 1,000 clinical claims. This is a hard go-live gate. Below this threshold, clinical claims can reach the payment path without physician review, which constitutes a URAC/NCQA compliance event. CMO sign-off on calibration results is required before any production routing begins.

**Wave 2 (Months 7–12, conditional):** Deploy the clinical pre-screening agent for the 35% of claims on the clinical path. The agent assembles a pre-filled physician review packet — diagnosis codes, prior authorisation history, clinical notes summary — reducing physician review time from 35 minutes to approximately 3 minutes per claim. Wave 2 is conditional on confirmed programmatic API access to the clinical notes source system. This integration must be validated before Wave 2 build begins; if it is not technically feasible, Wave 2 cannot proceed as specified. Wave 1 generates its full financial return independently of Wave 2.

**Headcount:** The Wave 1 administrative agent displaces approximately 12 of the current 20-person claims processing staff. Seven retained staff handle exception review, oversight, and physician review coordination. This exceeds Sarah Chen's 8-FTE threshold while preserving the physician review capacity Dr. Webb requires.

**Cycle time:** Administrative-path claims target ≤5 days. Clinical-path claims target ≤7 days — within the SLA threshold — on the basis that agent pre-screening eliminates the document assembly time that currently extends physician review to 35 minutes per claim.

---

## RISKS AND MITIGATIONS

| Risk | Likelihood | Mitigation |
|------|-----------|------------|
| The 65%/35% routing split is a stakeholder estimate, not a validated baseline — if the clinical share is materially higher, physician queue volume grows and headcount reduction targets become harder to meet | Medium | Validate split against 90 days of historical claim data in the design phase before finalising headcount and economic model |
| Clinical content definition workshop takes longer than planned, delaying classifier build and go-live | Medium | Definition workshop is the first design-phase deliverable with a 6-week hard deadline; no classifier build begins without CMO sign-off |
| Wave 1 build estimate ($420K) exceeds committed budget ($400K) by 5% | Low | Defer provider rejection notice templating and analytics dashboard to Wave 2, targeting $400K Wave 1 scope; payback remains 6.9 months at the full $420K estimate |
| Wave 2 clinical notes API is not accessible as a programmatic integration | High (unconfirmed) | Wave 1 is financially self-sufficient; Wave 2 integration feasibility confirmed before any Wave 2 commitment is made; no Wave 2 budget allocated until API access is verified |

---

## SUCCESS CRITERIA

| Metric | Target | Measured by |
|--------|--------|-------------|
| Auto-adjudication rate — administrative path | ≥80% of administrative-path claims resolved without human intervention | Monthly claims report: claims without HITL ÷ total claims received |
| Cycle time — administrative path | ≤5 days (30-day rolling median) | Submission date to adjudication decision date |
| Cycle time — clinical path | ≤7 days (30-day rolling median) | Submission date to physician sign-off date |
| SLA penalty incurrence | Zero claims exceeding 7-day threshold | Legal/operations: adjudication date > submission date + 7 calendar days |
| Clinical classifier recall | ≥99.5% before go-live — CMO sign-off required | Mock calibration against labelled historical claims |
| Denial appeal overturn rate | ≤15% within 6 months of go-live | Overturned appeals ÷ total appeals filed |

---

## NEXT STEPS

| Action | Owner | By |
|--------|-------|----|
| Confirm API feasibility for eligibility, prior auth, fee schedule, and clinical notes source systems | James Liu / IT | Week 2 |
| Convene clinical content definition workshop | Dr. Webb + FDE | Week 3 |
| Deliver clinical content definition with CMO sign-off | Dr. Webb | Week 6 |
| Confirm Wave 1 build scope at $400K; identify scope items to defer if needed | Sarah Chen + FDE | Week 4 |
| Begin Wave 1 design phase | FDE | Week 1 |
| Confirm Wave 2 clinical notes API feasibility — go/no-go decision | James Liu / IT | Week 8 |

---

## AGREEMENT & SIGN-OFF

I have reviewed this memo and agree to the proposed approach:

&nbsp;

_____________________________ &nbsp;&nbsp; Date: ____________
Sarah Chen, CFO

&nbsp;

_____________________________ &nbsp;&nbsp; Date: ____________
Dr. Marcus Webb, Chief Medical Officer

&nbsp;

_____________________________ &nbsp;&nbsp; Date: ____________
James Liu, VP Operations

&nbsp;

_____________________________ &nbsp;&nbsp; Date: ____________
Benoit Charrier, FDE
