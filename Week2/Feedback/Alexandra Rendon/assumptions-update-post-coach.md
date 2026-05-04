# Assumptions Update Post-Coach Role-Play

**Date**: 2026-04-29  
**Source**: Coach role-play interview with Dana Velazquez (simulated)  
**Impact**: Major update to confidence levels and wave sequencing

---

## Confidence Level Changes

| Assumption | Pre-Coach Confidence | Post-Coach Confidence | Change | Evidence from Dana |
|-----------|---------------------|----------------------|--------|-------------------|
| **[A1]** 30% insurance verifications fail auto-verify | MEDIUM | **MEDIUM** (unchanged) | No new data | Not discussed; kept as industry standard |
| **[A2]** PA patterns stable 6-12 months | MEDIUM | **HIGH** | ⬆️ Increased | UHC example: changed 18 months ago; patterns stable but occasional policy changes; Dana tracks and adjusts |
| **[A3]** Re-verification rule: >6mo + chronic patient | HIGH | **VERY HIGH** | ⬆️ Increased | Validated explicitly: >6mo + 3+ visits/year. Plus sub-rules: Medicaid every 3mo, Medicare Advantage in Q4, new insurance at next visit |
| **[A4]** PA denial patterns learnable | MEDIUM→HIGH | **VERY HIGH** | ⬆️ Increased | Wellpath colonoscopy: 30-40 occurrences over 6 years, 100% consistent. "Standing rule in my head" |
| **[A5]** Visit triage inconsistent (informal training) | MEDIUM | **HIGH** | ⬆️ Increased | No written protocol; Dana trains verbally; keywords list provided (chest pain, SOB, severe, sudden, can't); false negative example (hypertensive crisis missed) |
| **[A6]** DoseSpot misses med sources | LOW→MEDIUM | **VERY HIGH** | ⬆️⬆️ Increased | Fully specified: 1) Out-of-network pharmacies (10-15%), 2) Other providers' prescriptions, 3) OTC meds, 4) Supplements, 5) Samples. Dana estimates DoseSpot captures 70-80% of pharmacy fills, 0% of OTC/samples |
| **[A7]** Google Sheet is authoritative PA tracking | HIGH | **VERY HIGH** | ⬆️ Increased | Confirmed: Dana's personal tracking tool; front-desk doesn't use patterns from it; "living document" updated when patterns change |
| **[A8]** Intake miss rate ~3-5/month | LOW | **MEDIUM** | ⬆️ Increased | 3 billing failures in Q4 from re-verification misses; unclear how many medication/PA misses per month, but "regular" per scenario |
| **[A9]** Front-desk rotation creates inconsistency | MEDIUM | **HIGH** | ⬆️ Increased | Confirmed: 4-person team rotates between 2 locations; training doesn't stick; patterns locked in Dana's head |
| **[A10]** PA volume ~25/day | MEDIUM | **MEDIUM** (unchanged) | No new data | Not discussed; kept as stated in scenario |
| **[A11]** No formal knowledge transfer system | MEDIUM→HIGH | **VERY HIGH** | ⬆️ Increased | Explicit: "Patterns locked in my head"; front-desk doesn't know insurer-specific timing; no written SOPs for workarounds |
| **[A12]** athenahealth/Availity/DoseSpot APIs available | MEDIUM | **HIGH** | ⬆️ Increased | Dana mentions athenahealth subscription, Availity access, DoseSpot integrated; implies APIs exist (needs technical validation) |
| **[A13]** Clinical judgment constraint | HIGH | **VERY HIGH** | ⬆️ Increased | Dana explicitly defined: Front-desk can recognize keywords and escalate; cannot assess severity or decide disposition. "Recognition → escalate. Assessment → clinician." |
| **[A14]** Dana's personal stake | VERY LOW | **VERY HIGH** | ⬆️⬆️⬆️ Increased | Clarified: Dana wants regional manager role in 5 years; success = replicable system that works for other practices; resume-building for operations leadership |
| **[A15]** Malpractice constraints | MEDIUM | **MEDIUM** (unchanged) | No change | Dana hasn't asked carrier yet, but expects human review required for anything clinical; "AI can assist, but a human has to review and approve" |

---

## Major Findings from Coach Interview

### Finding 1: PA Chase Timing is Dana's #1 Frustration (Q18)

**Quote**: "That's easy: **the PA timing misses that lead to visit aborts**. When a patient shows up for a procedure or an imaging scan, expecting to get it done, and then we tell them, 'Sorry, the prior auth is still pending, we have to reschedule' — that's the worst."

**Impact**: 
- **Changes wave sequencing priority**
- Previous assumption: Insurance re-verification (billing failures) was highest pain point
- **Dana's actual priority**: PA chase timing (visit aborts, patient frustration, physician complaints)
- **Wave 1 should be PA chase timing, not insurance re-verification**

**Validation**:
- Artefact 5.2 (patient TJ's visit abort) directly aligns with Dana's stated frustration
- Dr. Westbridge's complaint about "three PA misses in Q4" was the trigger for AI exploration
- **Dana explicitly says**: "If I could fix one thing, it would be proactive PA chase timing that never misses a deadline"

---

### Finding 2: Dana's Time Spent on PAs Validates TCO Estimate (Q18)

**Quote**: "I'm tracking PA chases manually in my Google Sheet... I check my Google Sheet every morning, I eyeball the submission dates, I calculate the target chase day in my head based on the insurer, and I make phone calls."

**Impact**:
- Phase 4 estimated Dana spends 1.5-2 hours/day on PA chases
- Dana confirms this is accurate: "1-2 hours/day on PA chase work"
- **Baseline cost validated**: $20,625/year (conservative; likely higher)
- **ROI for JtD-2 (PA chase)** remains accurate

---

### Finding 3: DoseSpot Gaps Fully Specified (Q14, Q17)

**Quote**: "DoseSpot is pretty good at capturing prescriptions filled at major pharmacy chains — CVS, Walgreens, Rite Aid... But here's what it misses..."

**Specified gaps** [A6]:
1. **Out-of-network pharmacies (10-15% of patients)**: Mail-order, independent pharmacies, out-of-state fills, non-networked chains
2. **Other providers' prescriptions**: Specialists, ER, urgent care — DoseSpot shows fill but not prescriber/reason
3. **OTC medications**: Aspirin, ibuprofen, allergy meds, supplements (huge interaction risk for warfarin patients)
4. **Medication samples**: Specialists give samples, no pharmacy fill → DoseSpot never sees it
5. **Stopped medications**: DoseSpot shows old fills, patient stopped but never told anyone

**Dana's estimate**: DoseSpot captures **70-80% of pharmacy fills, 0% of OTC/samples**

**Impact on JtD-4 (Medication Reconciliation)**:
- Agent must explicitly prompt for missing sources: "Any meds filled at other pharmacies? Any OTC meds like aspirin, ibuprofen, allergy meds? Any vitamins or supplements? Any samples from specialists?"
- Build time increases by ~1 week for additional prompting logic
- **ROI still strong** (1,758% Year 1 ROI remains valid)

---

### Finding 4: Re-Verification Rule Has Sub-Rules (Q8)

**Dana's explicit rules** [A3]:
1. **Standard patients**: Re-verify if >6 months AND ≥3 visits/year (chronic patient proxy)
2. **Medicaid managed care**: Re-verify every 3 months (eligibility changes frequently)
3. **New insurance**: Re-verify at next visit regardless of timing (self-pay → insured, or employer switch)
4. **Medicare Advantage in Q4**: Always re-verify during open enrollment (Oct-Dec)

**Impact on JtD-1 (Insurance Verification)**:
- Agent needs conditional logic for patient population detection
- More complex than simple ">6 months" rule, but still deterministic
- **Build time unchanged** (logic is straightforward once encoded)

---

### Finding 5: Dana Wants Replicable System for Regional Role (Q22)

**Quote**: "I'd love to move into a regional manager role... Success in this AI project means building a system that's replicable. Not just for Westbridge, but for other practices."

**Impact on design**:
- Dana is highly motivated stakeholder (career advancement tied to project success) [A14]
- She wants **scalable solution**, not one-off for Westbridge
- Willing to invest time (3-6 months learning phase for PA chase) because it's resume-building
- **Organizational readiness**: HIGH (Dana will champion the project internally)

**Validation for Wave 2 (PA Chase)**: Dana's willingness to teach agent her patterns for 3-6 months is now **confirmed**, not assumed

---

### Finding 6: No Headcount Reduction Planned (Q23)

**Quote**: "Redeploy, not reduce. We're not letting anyone go. Honestly, we're already short-staffed."

**Impact on change management**:
- **Low resistance from front-desk** (not threatened by job loss)
- Front-desk time freed up for patient-facing work (proactive outreach, same-day slots, patient experience)
- Practice may grow (7th doctor, 3rd location) → AI enables growth without proportional headcount increase

**Organizational readiness**: HIGH (team will see AI as relief, not threat)

---

### Finding 7: Budget Threshold Identified (Q24)

**Quote**: "If it's under $5,000, I can usually get it approved... If it's $5,000-$20,000, I'd need to present a business case... If it's over $20,000, we'd probably need a partners meeting."

**Dana's ROI logic**: "If it's saving us 15+ hours a week... that's at least $1,500/week = $6,000/month in labor savings. So if the AI costs less than $6,000/month, it pays for itself."

**Impact on build cost**:
- Phase 4 estimated build costs: $30K-$40K per wave (one-time)
- Ongoing costs: Token + infrastructure = ~$1,000-$5,000/month (all 3 JtDs combined)
- **Budget gate**: If ongoing cost <$6,000/month, Dana can approve with ROI case
- **One-time build cost $30-40K**: Needs business case presentation to senior physician, likely approved given $100K+ annual savings

---

### Finding 8: Malpractice Likely Requires HITL (Q20)

**Quote**: "Our malpractice carrier is pretty conservative... I imagine they'd have similar requirements for AI... a human has to review and approve, especially for anything patient-facing or anything that could affect care."

**Impact on delegation archetypes**:
- **Fully Agentic** may be blocked for all JtDs by malpractice policy [A15]
- Conservative assumption: All agents require **Human Oversight** (at least spot-checks)
- **JtD-1 (Insurance Verification)**: Agent-led + Dana spot-checks (already designed this way)
- **JtD-2 (PA Chase)**: Agent-led + Dana spot-checks for unpredictable insurers (already designed this way)
- **JtD-3 (Visit Triage)**: Human-led + Agent Support (already designed this way)
- **JtD-4 (Medication Reconciliation)**: Agent-led + Physician reviews flags (already designed this way)

**Good news**: Our Phase 3 delegation archetypes already assumed human oversight, so **no design changes needed**

---

## Revised Wave Sequencing (Based on Dana's Priority)

### Original Sequencing (Phase 3 & 4):
1. **Wave 1**: Insurance Re-Verification (quick win, self-funding)
2. **Wave 2**: PA Chase Timing (strategic value)
3. **Wave 3**: Medication Reconciliation (highest ROI)

### **REVISED Sequencing (Based on Q18 - Dana's Top Frustration)**:

#### Wave 1: PA Chase Timing (Dana's #1 Priority)
**Why first**: 
- Dana explicitly said this is her biggest frustration: "If I could fix one thing, it would be proactive PA chase timing"
- Prevents visit aborts (Artefact 5.2: patient TJ's frustration, Dr. Westbridge's complaint)
- **Stakeholder alignment**: This is what Dr. Westbridge asked Dana to address
- Dana's 11 years of institutional knowledge [A2, A4, A7] must be captured before she moves to regional role [A14]

**Economics**:
- Annual saving: $20,897/year (Dana's time) + visit abort prevention (unquantified but significant)
- Build cost: $36,000
- Payback: 20.6 months
- **Strategic justification**: Highest stakeholder priority + institutional knowledge capture

**Timeline**: 8-11 months (2 months build + 3-6 months learning phase)

---

#### Wave 2: Insurance Re-Verification (Quick Win)
**Why second**:
- High ROI (171%), fast payback (4.4 months)
- Clear rules [A3]: >6mo + chronic patient, plus sub-rules for Medicaid, Medicare Advantage
- Builds athenahealth + Availity integrations → reused in Wave 3
- **Wave 1 PA chase** doesn't build reusable integrations (Google Sheet is unique to JtD-2)
- Wave 2 can start while Wave 1 is in learning phase (6-month overlap)

**Economics**:
- Annual saving: $108,264/year
- Build cost: $40,000
- Payback: 4.4 months
- Year 1 ROI: 171%

**Timeline**: 4 months (can start Month 5, during Wave 1 learning phase)

---

#### Wave 3: Medication Reconciliation (Highest ROI)
**Why third**:
- Highest ROI (1,758%), fastest payback (0.6 months)
- Reuses athenahealth integration from Wave 2
- DoseSpot gaps now fully specified [A6] → agent prompts finalized
- Physician time savings (16.5 hours/day freed up)

**Economics**:
- Annual saving: $557,464/year
- Build cost: $30,000 (reduced via Wave 2 integration reuse)
- Payback: 0.6 months
- Year 1 ROI: 1,758%

**Timeline**: 4 months (starts Month 13, after Waves 1-2 complete)

---

#### Wave 4 (Optional, Deferred): Visit Reason Triage
**Why deferred**:
- Clinical constraint [A13] validated: "Recognition → escalate. Assessment → clinician."
- Malpractice likely requires human review [A15]
- Lower priority than other JtDs (Dana didn't mention it as top frustration)

**Prerequisites**: Malpractice carrier approval, Waves 1-3 governance validated

---

## Implementation Recommendation

### Start with Wave 1: PA Chase Timing

**Immediate next steps**:
1. ✅ Assumptions validated via coach role-play (this document)
2. ⏳ **Ingest Dana's Google Sheet** (Artefact 5.1 + full historical data)
3. ⏳ **Extract insurer-specific patterns** from Google Sheet:
   - Humana: 6 days
   - UnitedHealthcare Choice: 7 days
   - Wellpath: 7 days + always denies colonoscopy first time (attach prior visit note)
   - Medicare: 4-5 days
   - BCBS PPO: 3 days
   - Aetna: Unpredictable (escalate to Dana)
4. ⏳ **Build agent architecture**:
   - athenahealth API: Read PA submission date, status, procedure type
   - Agent logic: Calculate chase timing based on insurer + submission date + Dana's learned SLA
   - Output: "Chase now" / "Wait X days" / "Escalate to Dana" (Aetna)
5. ⏳ **Learning phase (3-6 months)**: Dana approves all chase recommendations, agent learns from corrections
6. ⏳ **Production transition**: Agent handles predictable insurers autonomously, Dana spot-checks Aetna + reviews denials

**Success criteria**:
- Zero visit aborts from PA timing misses (currently ~1/month)
- Dana's time reduced from 1.5-2 hours/day to ~15 min spot-checking
- Agent learns 15+ insurer-specific patterns from Dana's Google Sheet + corrections

**Timeline**: 
- Months 1-2: Build + integration
- Months 3-8: Learning phase (Dana teaches patterns, agent recommends, Dana approves/corrects)
- Month 9+: Production (agent autonomous for predictable insurers, Dana spot-checks Aetna)

---

**End of Assumptions Update**
