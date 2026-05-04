# Phase 4: Candidate Prioritization — Westbridge Family Medicine Patient Intake

**Date**: 2026-04-29  
**Based on**: Phase 3 Delegation Qualification + ATX Scoring Methodology  
**Status**: **PROVISIONAL** (depends on unvalidated assumptions marked with [A#])

---

## Executive Summary

This document scores 4 JtDs on Volume × Value dimensions, assesses economic viability through TCO analysis, validates feasibility across 6 factors, and confirms implementation wave sequencing from Phase 3.

**Key Finding**: JtD-1 (insurance re-verification) and JtD-2 (PA chase timing) both score ≥15 on Agentic Value (Volume × Non-Determinism), pass economic gate (positive Year 1 ROI), and are ready for Wave 1-2 implementation. JtD-4 (medication reconciliation) scores 12 (marginal), depends on [A6] validation. JtD-3 (visit triage) scores 12 but deferred to Wave 4 due to clinical risk.

---

## Table of Contents

1. [Step 1: Suitability Gating (Validation)](#step-1-suitability-gating-validation)
2. [Step 2: Volume × Value Scoring](#step-2-volume--value-scoring)
3. [Step 3: Total Cost of Ownership (TCO) Assessment](#step-3-total-cost-of-ownership-tco-assessment)
4. [Step 4: Feasibility Scoring Matrix](#step-4-feasibility-scoring-matrix)
5. [Step 5: Strategic Sequencing Validation](#step-5-strategic-sequencing-validation)
6. [Prioritized Candidate Shortlist](#prioritized-candidate-shortlist)
7. [Implementation Roadmap](#implementation-roadmap)
8. [Assumption Dependencies & Update Protocol](#assumption-dependencies--update-protocol)

---

## Step 1: Suitability Gating (Validation)

Per ATX scoring methodology: *"Before scoring volume or value, confirm the use case passes the suitability gate."*

**Pass criteria**: At least Medium suitability on Input Structure, Decision Determinism, and Tool Coverage; no hard blocks on Risk/Compliance.

| JtD | Input Structure | Decision Determinism | Tool Coverage | Risk/Compliance | Gate Result |
|-----|----------------|---------------------|---------------|----------------|-------------|
| **JtD-1: Insurance Verification** | HIGH | MEDIUM | HIGH | MEDIUM (reversible) | ✅ **PASS** |
| **JtD-2: PA Chase Timing** | MEDIUM | LOW (patterns [A2]) | MEDIUM [A12] | HIGH (visit abort, reversible) | ✅ **PASS** (LOW determinism acceptable; patterns learnable) |
| **JtD-3: Visit Reason Triage** | MEDIUM | LOW (judgment [A5]) | HIGH | **VERY HIGH** (patient safety [A13]) | ⚠️ **CONDITIONAL** (clinical constraint; human-led only) |
| **JtD-4: Medication Reconciliation** | MEDIUM | MEDIUM | HIGH [A12] | HIGH (backstop via physician) | ✅ **PASS** (risk mitigated by human review) |

**Gate analysis**:
- **JtD-1, JtD-2, JtD-4**: Pass suitability gate; proceed to Volume × Value scoring
- **JtD-3**: Conditional pass; clinical constraint [A13] limits autonomy to Human-led + Agent Support

**Anti-pattern validation** (from Phase 3): All 4 JtDs require reasoning/pattern learning/NLP; none can be solved with static rules or RPA → agents justified.

---

## Step 2: Volume × Value Scoring

### Scoring Methodology (from atx-scoring.md)

**Execution Frequency (Volume)**: 1-5 scale
- 5: Very frequent (hundreds+ per day or continuous)
- 4: Frequent (50-200 per day)
- 3: Regular (10-50 per day, or high volume per week)
- 2: Moderate (several per day or high volume per month)
- 1: Infrequent (weekly or monthly)

**Non-Deterministic Decision Effort (Value driver)**: 1-5 scale
- 5: High reasoning (synthesis, policy interpretation, contextual judgment)
- 4: Significant reasoning (pattern-based, contextual adaptation, exception handling)
- 3: Mixed (core is rule-based, exceptions require reasoning)
- 2: Mostly deterministic (small reasoning around structured rules)
- 1: Fully deterministic (pure rules/logic)

**Agentic Value Score = Volume × Non-Determinism** (1-25 scale)
- Score ≥15: Strong agentic candidate
- Score 8-14: Consider agentic, validate with TCO
- Score <8: Use rule-based automation or don't automate

---

### JtD-1: Verify Insurance Eligibility for Scheduled Visit

**Execution Frequency**: **5** (Very frequent)
- 180 patients/day across both locations
- Verification happens 1-7 days before each visit
- **Volume estimate**: 180/day × 365 days = **65,700 cases/year**
- **Confidence**: HIGH (stated in scenario)

**Non-Deterministic Decision Effort**: **3** (Mixed)
- 70% of verifications are deterministic API calls (Availity query → success/failure)
- 30% fail auto-verify [A1] → require interpretation of error codes in context of patient history
- Re-verification timing decision requires applying Dana's tacit rule [A3]: >6 months + chronic patient → re-verify
- **Reasoning required**: Error code interpretation, chronic patient identification (pattern recognition: ≥3 visits/year), Medicaid managed care escalation
- **Confidence**: MEDIUM (30% exception rate [A1] is typical but not validated)

**Agentic Value Score**: **5 × 3 = 15** → **Strong agentic candidate**

---

### JtD-2: Determine Prior Authorization Status and Chase Pending PAs

**Execution Frequency**: **3** (Regular)
- ~25 PAs/day requiring submission/chase (stated in scenario)
- Dana's primary workload; front-desk only handles structured submission
- **Volume estimate**: 25/day × 250 workdays = **6,250 cases/year** [A10]
- **Confidence**: MEDIUM (scenario states ~25/day; Artefact 5.1 shows 5 samples, but not full volume distribution)

**Non-Deterministic Decision Effort**: **5** (High reasoning)
- Chase timing requires synthesis of: submission date + insurer + stated SLA + Dana's learned actual SLA [A2]
- Denial interpretation requires: denial code + insurer history + learned workaround patterns [A4]
- Example reasoning: "Wellpath always denies colonoscopy first time — preemptively attach prior visit note" (Artefact 5.1) is contextual judgment based on 11 years of pattern observation
- **Institutional knowledge capture**: Dana's Google Sheet [A7] contains patterns not in any system
- **Reasoning required**: Pattern matching, temporal reasoning (when to chase), workaround application, physician coordination for resubmission docs
- **Confidence**: HIGH (Artefact 5.1 explicitly shows non-deterministic patterns)

**Agentic Value Score**: **3 × 5 = 15** → **Strong agentic candidate**

---

### JtD-3: Triage Patient Visit Reason and Flag Clinical Urgency

**Execution Frequency**: **5** (Very frequent)
- 180 patients/day complete pre-visit questionnaires
- Visit reason triage happens for every patient
- **Volume estimate**: 180/day × 365 days = **65,700 cases/year**
- **Confidence**: HIGH (stated in scenario)

**Non-Deterministic Decision Effort**: **4** (Significant reasoning)
- Patient language is highly variable and ambiguous ("feeling off" vs. "chest pain" vs. "knee pain, can't walk")
- Requires NLP interpretation + pattern recognition (is "chest pain" urgent or routine cardiology follow-up?)
- Contextual adaptation based on patient history, appointment type, symptom language
- **BUT**: Clinical judgment constraint [A13] limits agent to keyword flagging + escalation, not urgency assessment
- **Reasoning required**: NLP parsing, ambiguity detection, keyword-based urgency flagging, escalation logic learning (reduce false positives via physician feedback)
- **Confidence**: MEDIUM (informal training [A5] suggests complexity, but no documented triage errors in artefacts)

**Agentic Value Score**: **5 × 4 = 20** → **Strong agentic candidate** (by volume/reasoning alone)

**BUT**: Clinical constraint [A13] + VERY HIGH risk (patient safety) **downgrades to Human-led + Agent Support** (deferred to Wave 4)

---

### JtD-4: Reconcile Medications and Flag Allergy Alerts

**Execution Frequency**: **5** (Very frequent)
- 180 patients/day at check-in
- Medication reconciliation happens for every visit
- **Volume estimate**: 180/day × 365 days = **65,700 cases/year**
- **Confidence**: HIGH (stated in scenario)

**Non-Deterministic Decision Effort**: **2-3** (Mostly deterministic → Mixed)
- Comparing athenahealth med list vs. DoseSpot fill history vs. patient verbal report is partly deterministic (list diff)
- **BUT**: Interpreting discrepancies requires reasoning:
  - Patient says "I stopped that" — discontinued or ran out and needs refill?
  - DoseSpot shows fill patient didn't mention — missed by patient or not taking it?
  - Identifying what DoseSpot misses [A6] (out-of-network pharmacies, OTC, samples, other providers) requires gap analysis
- Allergy conflict flagging is fully deterministic (rule-based)
- **Reasoning required**: Discrepancy interpretation, patient language NLP, gap source identification
- **Score**: **2.5** (round to **3** for mixed deterministic/reasoning)
- **Confidence**: LOW→MEDIUM ([A6] DoseSpot scope unknown; affects reasoning complexity)

**Agentic Value Score**: **5 × 2.5 = 12.5** → Round to **12** (Consider agentic, validate with TCO)

---

### Volume × Value Summary Table

| JtD | Volume Score | Non-Determinism Score | Agentic Value | Candidacy | Notes |
|-----|-------------|----------------------|---------------|-----------|-------|
| **JtD-1: Insurance Verification** | 5 | 3 | **15** | ✅ Strong | High volume, 30% exceptions [A1] |
| **JtD-2: PA Chase Timing** | 3 | 5 | **15** | ✅ Strong | Institutional knowledge [A2, A4, A7] |
| **JtD-3: Visit Reason Triage** | 5 | 4 | **20** | ⚠️ Strong (but clinical constraint) | Deferred to Wave 4 [A13] |
| **JtD-4: Medication Reconciliation** | 5 | 2.5 | **12** | ⚠️ Marginal | Validate TCO; depends on [A6] scope |

---

### Volume × Value Quadrant (Visual Prioritization)

```
Non-Deterministic Decision Effort (Value Driver)
            ↑
         5  │             │
            │  JtD-2 (15) │
            │      ●      │     JtD-3 (20)
         4  │             │         ●
            │             │
            ├─────────────┼─────────────────────┐
         3  │             │                     │
            │             │              JtD-1 (15)
            │             │                 ●   │
         2  │             │         JtD-4 (12)  │
            │             │            ●        │
         1  │             │                     │
            │             │                     │
         0  └─────────────┴─────────────────────┘──→
            0      1      2      3      4      5
                  Execution Frequency (Volume)
```

**Quadrant Positions:**
- **JtD-2 (PA Chase)**: Volume=3, Non-Determinism=5, Score=15 (Top-Left)
- **JtD-3 (Visit Triage)**: Volume=5, Non-Determinism=4, Score=20 (Top-Right)
- **JtD-1 (Insurance)**: Volume=5, Non-Determinism=3, Score=15 (Top-Right)
- **JtD-4 (Med Recon)**: Volume=5, Non-Determinism=2.5, Score=12 (Bottom-Right)

**QUADRANT INTERPRETATION:**

**TOP-LEFT (Low Volume, High Non-Determinism)**
- **JtD-2 (PA Chase)**: Volume=3, Non-Determinism=5, Score=15
- **Rationale**: Institutional knowledge capture [A2, A4, A7]
- **Strategy**: Agent learns patterns from expert over 3-6 months

**TOP-RIGHT (High Volume, High Non-Determinism) — PRIMARY AGENTIC ZONE**
- **JtD-3 (Visit Triage)**: Volume=5, Non-Determinism=4, Score=20
- **JtD-1 (Insurance)**: Volume=5, Non-Determinism=3, Score=15
- **Rationale**: High volume justifies automation; non-determinism requires agent reasoning (not static rules)
- **Strategy**: Agent-led with human oversight (JtD-3 deferred due to clinical constraint [A13]; JtD-1 proceeds to Wave 2)

**BOTTOM-RIGHT (High Volume, Low Non-Determinism)**
- **JtD-4 (Med Recon)**: Volume=5, Non-Determinism=2.5, Score=12
- **Rationale**: High volume, but mostly deterministic (list comparison)
- **Strategy**: Agent flags discrepancies; physician reviews (human backstop for clinical safety)
- **Note**: Borderline for agentic (score=12); justified by TCO (1,758% ROI) and physician time savings

**BOTTOM-LEFT (Low Volume, Low Non-Determinism) — NOT AGENTIC**
- No JtDs in this quadrant
- **Strategy**: If JtDs fell here, use static rules/RPA instead of agents

**Priority zones** (from atx-assessment.md):
- **Top right** (high volume, high non-determinism): JtD-3 (20), JtD-1 (15) → primary agentic targets
- **Top left** (medium volume, high non-determinism): JtD-2 (15) → institutional knowledge capture
- **Bottom right** (high volume, low-medium non-determinism): JtD-4 (12) → validate TCO before proceeding

**Key insight**: JtD-2 scores same as JtD-1 (both 15) despite lower volume (3 vs 5) because non-determinism is higher (5 vs 3). This validates Phase 3 finding: **JtD-2 is strategic value unlock** (institutional knowledge capture) even though volume is lower.

---

## Step 3: Total Cost of Ownership (TCO) Assessment

### Baseline Assumptions (Provisional)

**Fully loaded hourly cost**:
- Front-desk staff: **$35/hour** (includes salary + benefits + overhead)
  - **Assumption basis**: US mid-Atlantic suburban practice; typical medical front-desk range $22-28/hour base salary × 1.4 for benefits/overhead
  - **Confidence**: MEDIUM (not validated with Dana; industry standard)
- Dana (RN, Practice Manager): **$55/hour**
  - **Assumption basis**: RN with 11 years tenure + management responsibilities; typical range $45-65/hour fully loaded
  - **Confidence**: MEDIUM (not validated; industry standard)

**Model selection** (provisional): **Claude 3.5 Sonnet**
- Input tokens: $3/million
- Output tokens: $15/million
- **Rationale**: Balance of cost vs. capability for healthcare intake (requires accuracy, not fastest model)
- **Alternative**: Claude 3 Haiku ($0.25/$1.25 per million) for simple verifications; Opus 4.6 for complex PA denials

---

### JtD-1: Insurance Verification — TCO Analysis

#### Baseline Cost (Human)

**Current process** (from cognitive map):
- 70% auto-verify successfully: ~2 min front-desk time (check athenahealth, query Availity, update status)
- 30% fail auto-verify [A1]: ~5 min front-desk time (interpret error code, check patient history, escalate to Dana if complex)
- Re-verification cases (currently missed [A3]): ~0 min (not being caught → billing failures)

**Weighted average time per case**: (0.7 × 2 min) + (0.3 × 5 min) = 1.4 + 1.5 = **2.9 min = 0.048 hours**

**Annual baseline cost**:
```
65,700 cases/year × 0.048 hours × $35/hour = $110,376/year
```

**Plus**: Billing failure resolution cost (Artefact 5.3: patient TJ's $340 surprise bill took 12 min to resolve)
- Estimated 3 billing failures/quarter from missed re-verification [A3] = 12/year
- 12 cases/year × 0.2 hours × $35/hour = **$84/year** (minor, but patient satisfaction impact)

**Total baseline**: **$110,460/year**

---

#### Agent Cost Model

**Token consumption estimate** (per case):
- Input: Patient ID, insurance info, last verification date, appointment type, patient visit history (≥3 visits/year for chronic patient detection) = **~1,200 tokens**
- Output: Verification status, re-verification recommendation, escalation flag if complex = **~300 tokens**
- **Total**: 1,500 tokens/case

**Token cost per case**: (1,200 × $3/1M) + (300 × $15/1M) = $0.0036 + $0.0045 = **$0.0081**

**Tool calls per case**:
- athenahealth API: Read patient record, insurance info, visit history (2 calls)
- Availity API: Eligibility verification (1 call)
- athenahealth API: Update verification status (1 write)
- **Total**: 4 API calls × $0.001/call (estimated) = **$0.004**

**Infrastructure cost**: Minimal (hosted platform) = **$0.001/case**

**HITL cost** (Human-in-the-Loop):
- Learning phase (1 month): Dana reviews 100% of re-verification triggers → 30-50 cases/month × 1 min review = **$35-60/month** → amortize over year = **$5/year per case negligible**
- Production phase: Dana spot-checks 5% of re-verifications → 5% × 30 cases/month × 1 min × $55/hour = **$14/month = $168/year**
- Exception escalations (Medicaid managed care): 5% of 30% failures = 1.5% of total → 1,000 cases/year × 2 min × $35/hour = **$1,167/year**

**Total agent cost per case**: $0.0081 + $0.004 + $0.001 = **$0.0131**

**Annual agent cost** (65,700 cases): $0.0131 × 65,700 = **$861** + $168 (Dana spot-checks) + $1,167 (escalations) = **$2,196/year**

---

#### ROI Calculation

**Annual saving**: $110,460 - $2,196 = **$108,264/year**

**Build cost estimate**:
- Agent development: 2 weeks (re-verification logic, Availity error code patterns, chronic patient detection) = $15,000
- athenahealth + Availity integration: 2 weeks (assuming APIs available [A12]) = $15,000
- Testing + Dana validation: 1 month = $10,000
- **Total build**: **$40,000**

**Payback period**: $40,000 / $108,264 = **4.4 months**

**Year 1 ROI**: ($108,264 - $40,000) / $40,000 × 100% = **171%**

**3-year ROI**: (($108,264 × 3) - $40,000) / $40,000 × 100% = **713%**

✅ **Economic gate: PASS** (Year 1 ROI > 0%, payback < 12 months)

---

### JtD-2: PA Chase Timing — TCO Analysis

#### Baseline Cost (Human)

**Current process** (from cognitive map lived process narrative):
- Dana manually checks Google Sheet daily, calculates chase timing based on learned patterns [A2: HIGH ⬆️], phones insurers, applies denial workarounds [A4: VERY HIGH ⬆️]
- **Validated time** (Q18): Dana confirms **1-2 hours/day** on PA chase work: "I check my Google Sheet every morning, I eyeball the submission dates, I calculate the target chase day in my head based on the insurer, and I make phone calls."
- **Conservative estimate**: 1.5 hours/day × 250 workdays = **375 hours/year**

**Annual baseline cost**:
```
375 hours/year × $55/hour = $20,625/year
```

**Plus**: Visit abort operational cost (Artefact 5.2: patient TJ's visit aborted, rescheduled)
- Estimated ~1 visit abort/month from PA timing miss [A8] = 12/year
- Physician time wasted: 12 × 15 min × $150/hour = **$4,500/year**
- Patient satisfaction impact: Not quantified, but senior physician complaint suggests significant

**Total baseline**: **$25,125/year** (conservative; likely higher if Dana's actual time is >1.5 hours/day)

---

#### Agent Cost Model

**Token consumption estimate** (per case):
- Input: PA submission date, insurer, procedure type, patient info, Dana's Google Sheet pattern for this insurer [A7], athenahealth PA status = **~2,000 tokens**
- Output: Chase recommendation (chase now / wait X days / escalate), denial interpretation if applicable, resubmission doc suggestion = **~500 tokens**
- **Total**: 2,500 tokens/case

**Token cost per case**: (2,000 × $3/1M) + (500 × $15/1M) = $0.006 + $0.0075 = **$0.0135**

**Tool calls per case**:
- athenahealth API: Read PA status, submission date (1 call)
- Dana's Google Sheet ingestion (pattern lookup): Amortized over all cases = negligible
- athenahealth API: Update PA status with agent recommendation (1 write)
- **Total**: 2 API calls = **$0.002**

**Infrastructure cost**: **$0.001/case**

**HITL cost**:
- Learning phase (3-6 months): Dana approves 100% of chase recommendations → 25/day × 2 min × $55/hour × 150 days = **$6,875** (amortized over 3 years = $2,292/year)
- Production phase: Dana spot-checks unpredictable insurers (Aetna) + reviews all denials → 20% of cases × 2 min × $55/hour = **$1,833/year**

**Total agent cost per case**: $0.0135 + $0.002 + $0.001 = **$0.0165**

**Annual agent cost** (6,250 cases): $0.0165 × 6,250 = **$103** + $1,833 (Dana oversight) + $2,292 (learning amortized) = **$4,228/year**

---

#### ROI Calculation

**Annual saving**: $25,125 - $4,228 = **$20,897/year**

**Build cost estimate**:
- Agent development: 2 months (Google Sheet ingestion [A7], insurer pattern learning, denial interpretation, reinforcement from Dana's corrections) = $30,000
- athenahealth integration: 1 week (reuse from JtD-1) = $3,000
- Google Sheet API integration: 1 week = $3,000
- Dana training/validation: 3-6 months (concurrent with learning phase; included in HITL cost)
- **Total build**: **$36,000**

**Payback period**: $36,000 / $20,897 = **20.6 months** (fails Year 1 ROI gate, but passes 18-month payback)

**Year 1 ROI**: ($20,897 - $36,000) / $36,000 × 100% = **-42%** (negative Year 1)

**3-year ROI**: (($20,897 × 3) - $36,000) / $36,000 × 100% = **74%**

⚠️ **Economic gate: CONDITIONAL PASS** (payback 20.6 months; exceeds 18-month threshold but within 2-year window)

**Strategic justification**:
- **Institutional knowledge capture** [A2, A4, A7]: Dana's 11 years of patterns systematized → scales to front-desk team + future hires
- **Business continuity**: Eliminates single point of failure (Dana on vacation)
- **Prevents visit aborts**: Physician satisfaction + patient retention value not quantified
- **Compounding asset**: PA chase patterns reusable if practice expands or adds locations

**Recommendation**: Proceed as Wave 2 (strategic value), but **validate Dana's actual PA time [Q18]** — if >2 hours/day, ROI improves significantly.

---

### JtD-4: Medication Reconciliation — TCO Analysis

#### Baseline Cost (Human)

**Current process** (from cognitive map):
- Front-desk: Pull DoseSpot, ask patient "any changes?", document verbal response = **~6 min/patient** (scenario states this)
- Physician: Manual reconciliation during visit when front-desk misses discrepancies (unquantified frequency [A8])

**Annual baseline cost** (front-desk only):
```
65,700 cases/year × 0.1 hours × $35/hour = $229,950/year
```

**Physician time saved** (if agent reduces in-visit reconciliation from 6 min to 30 sec review of flagged list):
```
65,700 cases × 5.5 min saved × $150/hour = $902,025/year
```

**BUT**: This assumes physician currently does full 6-min reconciliation for every patient, which is unlikely. More realistic: physician reviews flagged discrepancies only (current process: front-desk does initial recon, physician catches what's missed).

**Conservative estimate**: Physician saves 2 min/patient on average (reviewing pre-flagged list vs. manual questioning)
```
65,700 cases × 2 min × $150/hour = $328,500/year
```

**Total baseline** (conservative): $229,950 + $328,500 = **$558,450/year**

---

#### Agent Cost Model

**Token consumption estimate** (per case):
- Input: athenahealth med list, DoseSpot fill history (past 6 months), patient questionnaire response, allergy list = **~2,000 tokens**
- Output: Flagged discrepancies (new meds, discontinued meds, dosage changes, allergy conflicts), suggested questions for physician = **~400 tokens**
- **Total**: 2,400 tokens/case

**Token cost per case**: (2,000 × $3/1M) + (400 × $15/1M) = $0.006 + $0.006 = **$0.012**

**Tool calls per case**:
- athenahealth API: Read med list, allergy list (1 call)
- DoseSpot API: Read fill history (1 call) [A12]
- Patient questionnaire: Read verbal report (already in athenahealth)
- **Total**: 2 API calls = **$0.002**

**Infrastructure cost**: **$0.001/case**

**HITL cost**:
- **100% physician review** (perpetual): Agent flags discrepancies; physician reviews before prescribing = **$0** additional (physician was already reviewing, just faster)
- Exception: If agent misses discrepancy, physician catches during prescribing (backstop) = **$0** additional cost (same as current process)

**Total agent cost per case**: $0.012 + $0.002 + $0.001 = **$0.015**

**Annual agent cost** (65,700 cases): $0.015 × 65,700 = **$986/year**

---

#### ROI Calculation

**Annual saving**: $558,450 - $986 = **$557,464/year** (conservative; could be higher if physician saves >2 min/patient)

**Build cost estimate**:
- Agent development: 3 weeks (three-source reconciliation, discrepancy interpretation, gap source prompts [A6]) = $15,000
- athenahealth integration: Reuse from JtD-1 = $0
- DoseSpot API integration: 1 week [A12] = $5,000
- Testing + physician validation: 1 month = $10,000
- **Total build**: **$30,000**

**Payback period**: $30,000 / $557,464 = **0.6 months** (!!!)

**Year 1 ROI**: ($557,464 - $30,000) / $30,000 × 100% = **1,758%** (!!)

**3-year ROI**: (($557,464 × 3) - $30,000) / $30,000 × 100% = **5,474%**

✅ **Economic gate: STRONG PASS** (highest ROI of all JtDs)

**BUT**: **[CRITICAL ASSUMPTION DEPENDENCY - A6]** — This ROI assumes:
1. Physician currently spends significant time on manual reconciliation (conservative 2 min/patient)
2. Agent successfully identifies discrepancies DoseSpot misses [A6]
3. Physician time savings are realized (not absorbed by other tasks)

**Recommendation**: Wave 3 priority, BUT **must validate [A6] DoseSpot scope first** (Q14, Q17). If DoseSpot only covers in-network pharmacies, agent must explicitly prompt for out-of-network fills, OTC, samples → adds scope but doesn't change ROI materially.

---

### JtD-3: Visit Reason Triage — TCO Analysis (Deferred)

**Not analyzed for Wave 1-3**: Clinical constraint [A13] + VERY HIGH risk (patient safety) + malpractice constraints unknown [A15] → deferred to Wave 4 pending coach validation (Q13, Q20).

**Preliminary volume/value**: Agentic Value Score = 20 (highest), but risk gates override economic analysis.

---

### TCO Summary Table

| JtD | Annual Baseline | Annual Agent Cost | Annual Saving | Build Cost | Payback | Year 1 ROI | 3-Year ROI | Gate Result |
|-----|----------------|-------------------|--------------|-----------|---------|-----------|-----------|-------------|
| **JtD-1: Insurance Verification** | $110,460 | $2,196 | $108,264 | $40,000 | 4.4 mo | **171%** | **713%** | ✅ PASS |
| **JtD-2: PA Chase Timing** | $25,125 | $4,228 | $20,897 | $36,000 | 20.6 mo | -42% | **74%** | ⚠️ CONDITIONAL (strategic) |
| **JtD-4: Medication Reconciliation** | $558,450 | $986 | $557,464 | $30,000 | 0.6 mo | **1,758%** | **5,474%** | ✅ STRONG PASS |
| **JtD-3: Visit Reason Triage** | _Not analyzed_ | _Not analyzed_ | _Not analyzed_ | _Deferred_ | _Deferred_ | _Deferred_ | _Deferred_ | ⚠️ DEFERRED (risk) |

**Economic rank** (by Year 1 ROI):
1. **JtD-4**: 1,758% ROI, 0.6-month payback → **Highest financial return**
2. **JtD-1**: 171% ROI, 4.4-month payback → **Quick win**
3. **JtD-2**: -42% Year 1 ROI, 20.6-month payback → **Strategic value** (institutional knowledge)

---

## Step 4: Feasibility Scoring Matrix

Score each JtD on 6 factors (1-5 scale, 5 = most feasible):

### JtD-1: Insurance Verification

| Factor | Score | Rationale | Confidence |
|--------|-------|-----------|-----------|
| **Data availability** | **5** | athenahealth patient record, insurance info, visit history all accessible via API [A12]. Availity API for eligibility checks. | HIGH |
| **System integration feasibility** | **4** | athenahealth REST APIs stated in scenario [A12]. Availity is standard healthcare integration. Potential complexity: error code interpretation patterns not documented. | MEDIUM (assume APIs available; integration effort typical) |
| **Compliance risk** | **5** | Administrative data only (no clinical judgment). HIPAA-compliant via standard EHR access. Reversible (billing failures can be corrected). | HIGH |
| **Context stability** | **4** | Re-verification rule [A3] is stable once validated. Availity error codes may change, but rarely. Insurance verification logic is industry-standard. | MEDIUM→HIGH ([A3] needs validation; assume stable) |
| **Organizational readiness** | **4** | Front-desk team comfortable with Availity/athenahealth already. Dana available for 1-month validation. Low HITL overhead (spot-checks only). | MEDIUM (assume Dana's availability; not validated) |
| **TCO viability** | **5** | Year 1 ROI 171%, payback 4.4 months. Economics strongly favor automation. | HIGH |

**Average feasibility**: (5+4+5+4+4+5)/6 = **4.5 / 5** → **Very High Feasibility**

---

### JtD-2: PA Chase Timing

| Factor | Score | Rationale | Confidence |
|--------|-------|-----------|-----------|
| **Data availability** | **4** | athenahealth PA submission/status accessible [A12]. Dana's Google Sheet [A7] provides historical pattern data. Insurer portal responses vary (some APIs, some web-only). | MEDIUM ([A12] assume athenahealth APIs available; Google Sheet accessible) |
| **System integration feasibility** | **3** | athenahealth REST APIs [A12]. Google Sheets API straightforward. Insurer portals fragmented (not standardized). Agent needs to ingest Dana's Google Sheet patterns, then learn via reinforcement (Dana's corrections during 3-6 month learning phase). | MEDIUM (athenahealth + Google Sheet feasible; insurer portal variability adds complexity) |
| **Compliance risk** | **4** | Administrative PA management (no clinical decisions). HIPAA-compliant via athenahealth access. Risk: visit abort if chase timing wrong (reversible via rescheduling, but patient satisfaction impact). | MEDIUM→HIGH (reversible but operationally impactful; senior physician complaint in Artefact 5.2) |
| **Context stability** | **3** | Dana's patterns stable over 6-12 months [A2] (MEDIUM confidence). Risk: insurer policy changes (Q3: "Has an insurer changed their SLA in last 2 years?"). Agent must detect pattern deviation. | MEDIUM ([A2] needs validation; assume patterns relatively stable but require monitoring) |
| **Organizational readiness** | **3** | Requires Dana's active participation for 3-6 months (teaching patterns, correcting agent recommendations). Dana's availability and willingness critical [Q22: career goals]. Front-desk benefit: PA knowledge scales to team. | MEDIUM (assume Dana's buy-in; not validated) |
| **TCO viability** | **3** | Year 1 ROI -42% (negative), payback 20.6 months. Economics marginal unless Dana's actual time >2 hours/day [Q18]. Strategic value (institutional knowledge) justifies despite marginal economics. | MEDIUM (conditional pass; strategic justification; needs [Q18] validation) |

**Average feasibility**: (4+3+4+3+3+3)/6 = **3.3 / 5** → **Medium Feasibility**

**Critical dependencies**: [A2] pattern stability, [Q18] Dana's actual PA time, [Q22] Dana's willingness to teach patterns for 3-6 months

---

### JtD-4: Medication Reconciliation

| Factor | Score | Rationale | Confidence |
|--------|-------|-----------|-----------|
| **Data availability** | **4** | athenahealth med list, allergy list accessible [A12]. DoseSpot pharmacy history integrated with athenahealth. Patient questionnaire responses in athenahealth. **BUT**: DoseSpot scope unknown [A6] — what it misses affects completeness. | MEDIUM ([A12] assume APIs available; [A6] scope unknown) |
| **System integration feasibility** | **5** | athenahealth REST APIs [A12]. DoseSpot integration already exists (scenario states "integrated with athenahealth"). Patient questionnaire already in athenahealth workflow. Agent doesn't need new systems, only API access. | HIGH (reuses JtD-1 athenahealth integration; DoseSpot already integrated) |
| **Compliance risk** | **4** | High-consequence if wrong (drug interactions, allergy conflicts), BUT mitigated by **physician review before prescribing** (human backstop). Agent flags discrepancies; does NOT auto-update med list. HIPAA-compliant via athenahealth access. | HIGH (risk mitigated by design; physician always makes final decision) |
| **Context stability** | **4** | Medication reconciliation logic stable (compare three sources, flag discrepancies). DoseSpot integration scope may change if practice adds new pharmacies or DoseSpot expands coverage [A6], but core logic remains. | MEDIUM→HIGH ([A6] scope needs validation; assume relatively stable) |
| **Organizational readiness** | **5** | Physician reviews flagged list (already part of visit workflow). No new HITL burden (physician was already doing manual reconciliation, just faster now). Front-desk time freed up for other tasks. | HIGH (minimal change management; physician time savings motivate adoption) |
| **TCO viability** | **5** | Year 1 ROI 1,758%, payback 0.6 months. **Strongest economics of all JtDs**. | HIGH (ROI assumes physician saves 2 min/patient; conservative estimate) |

**Average feasibility**: (4+5+4+4+5+5)/6 = **4.5 / 5** → **Very High Feasibility**

**Critical dependency**: [A6] DoseSpot scope — must validate what it misses (Q14, Q17) before finalizing agent prompt design

---

### JtD-3: Visit Reason Triage (Deferred)

| Factor | Score | Rationale | Confidence |
|--------|-------|-----------|-----------|
| **Data availability** | **5** | Visit reason from questionnaire, patient history in athenahealth [A12]. All data accessible. | HIGH |
| **System integration feasibility** | **5** | athenahealth REST APIs [A12]. Reuses JtD-1 integration. NLP parsing straightforward. | HIGH |
| **Compliance risk** | **2** | **VERY HIGH risk** (patient safety [A13]). Malpractice constraints unknown [A15]. Clinical judgment boundary unclear (Q13). Missing urgent symptom → patient harm. Over-escalating → alert fatigue (also risky). | LOW (risk gates block despite high feasibility on other dimensions) |
| **Context stability** | **3** | Patient language variability high. Escalation logic can learn from physician feedback, but clinical boundary [A13] is moving target (depends on Dana's definition, Q13). | MEDIUM ([A13] needs clarification; [A15] malpractice constraints unknown) |
| **Organizational readiness** | **3** | Requires Dana/physician to review 100% of agent flags (Human-led design). Alert fatigue risk if false positive rate too high. Physician tolerance for AI triage unknown [A15]. | MEDIUM (assume conservative design acceptable; needs validation) |
| **TCO viability** | **Not scored** | Deferred; economics not analyzed due to risk gates | N/A |

**Average feasibility**: (5+5+2+3+3)/5 = **3.6 / 5** → **Medium Feasibility** (but **compliance risk (2) blocks** regardless of overall score)

**Critical dependencies**: [A13] clinical boundary definition (Q13), [A15] malpractice constraints (Q20), [A5] front-desk triage error rate (unknown)

**Recommendation**: Defer to Wave 4; proceed only after [A13] and [A15] validated via coach

---

### Feasibility Summary Table

| JtD | Data | Integration | Compliance | Stability | Org Readiness | TCO | **Average** | **Feasibility** |
|-----|------|------------|-----------|-----------|--------------|-----|------------|----------------|
| **JtD-1: Insurance Verification** | 5 | 4 | 5 | 4 | 4 | 5 | **4.5** | ✅ Very High |
| **JtD-4: Medication Reconciliation** | 4 | 5 | 4 | 4 | 5 | 5 | **4.5** | ✅ Very High |
| **JtD-2: PA Chase Timing** | 4 | 3 | 4 | 3 | 3 | 3 | **3.3** | ⚠️ Medium (strategic) |
| **JtD-3: Visit Reason Triage** | 5 | 5 | **2** | 3 | 3 | _N/A_ | **3.6** | ⚠️ Deferred (risk) |

**Key finding**: JtD-4 (medication reconciliation) scores **highest on both TCO (1,758% ROI) and feasibility (4.5)**, yet Phase 3 sequenced it as Wave 3 (not Wave 1). Why?

**Reason**: JtD-4 depends on [A6] DoseSpot scope validation (Q14, Q17), which requires coach elicitation first. JtD-1 has no critical unknowns → can proceed immediately.

**Revised sequencing consideration**: If [A6] is validated quickly (coach answers Q14/Q17 in next session), **swap Wave 1 and Wave 3** → JtD-4 first (highest ROI), then JtD-1.

---

## Step 4.5: Use Case Scoring Templates (Summary)

Complete scoring templates for all 4 JtDs following the atx-scoring.md format:

### JtD-1: Insurance Verification — Use Case Scoring Template

```
Use Case: Insurance Eligibility Verification for Scheduled Visits
Process: Patient Intake / Front-Desk Operations
Volume: 180 patients/day (65,700 cases/year)

Suitability gate:
  Input structure: HIGH (structured API: patient ID, insurance info, appointment date in athenahealth)
  Decision determinism: MEDIUM (70% deterministic API calls; 30% require error code interpretation [A1])
  Tool coverage: HIGH (athenahealth + Availity REST APIs available [A12])
  Exception rate: MEDIUM (30% fail auto-verify [A1])
  Compliance risk: MEDIUM (administrative data only; billing impact if wrong, but reversible)
  Gate result: PASS

Scoring:
  Execution frequency score: 5 (Very frequent: 180/day)
  Non-deterministic effort score: 3 (Mixed: 70% rules, 30% pattern recognition)
  Agentic value score: 15 (Strong agentic candidate)

Economics:
  Avg time per case (human): 0.048 hours (2.9 min weighted avg: 70% × 2 min + 30% × 5 min)
  Cases per year: 65,700
  Fully loaded hourly cost: $35/hour (front-desk staff)
  Annual baseline cost: $110,460

  Estimated tokens per case: 1,200 input + 300 output = 1,500 total
  Model: Claude 3.5 Sonnet ($3/M input, $15/M output)
  Estimated token cost per case: $0.0081
  Tool calls per case: 4 (athenahealth read × 2, Availity query × 1, athenahealth write × 1) = $0.004
  Infrastructure cost per case: $0.001
  HITL rate: 5% (Dana spot-checks re-verification triggers in production)
  Estimated agent cost per case: $0.0131
  Annual agent cost: $2,196 (includes $168 Dana spot-checks + $1,167 escalations)

  Annual saving: $108,264
  Estimated build cost: $40,000 (2 months build + integration + testing)
  Payback period: 4.4 months
  Year 1 ROI: 171%
  3-Year ROI: 713%

Sequencing:
  Wave: 2 (REVISED from Wave 1; moved to Wave 2 based on stakeholder priority [Q18])
  Key integrations built: athenahealth REST API, Availity API (both reused in Wave 3)
  Dependencies: [A3] re-verification rule validation (VALIDATED: >6mo + ≥3 visits/year, plus sub-rules)
  Can start: Month 5 (during Wave 1 learning phase; 6-month overlap)

Delegation archetype: Agent-led + Human Oversight → Fully Agentic (after 1-month validation)
Recommended next step: Proceed to Wave 2 build (Month 5); validate athenahealth/Availity API documentation
```

---

### JtD-2: PA Chase Timing — Use Case Scoring Template

```
Use Case: Prior Authorization Chase Timing and Denial Management
Process: Clinical Operations / Practice Manager (Dana)
Volume: 25 PAs/day requiring submission/chase (6,250 cases/year [A10])

Suitability gate:
  Input structure: MEDIUM (PA data in athenahealth structured; Dana's Google Sheet semi-structured [A7]; insurer portals vary)
  Decision determinism: LOW (insurer-specific patterns learned over 11 years [A2, A4]; not rule-based)
  Tool coverage: MEDIUM (athenahealth API [A12], Google Sheets API available; insurer portals fragmented)
  Exception rate: MEDIUM (~40% of PAs denied or delayed beyond stated SLA; each insurer has unique patterns)
  Compliance risk: HIGH (visit abort if timing wrong, but reversible via rescheduling; operational impact)
  Gate result: PASS (LOW determinism acceptable; patterns learnable from Dana's institutional knowledge)

Scoring:
  Execution frequency score: 3 (Regular: 25/day)
  Non-deterministic effort score: 5 (High reasoning: institutional knowledge capture [A2, A4, A7])
  Agentic value score: 15 (Strong agentic candidate)

Economics:
  Avg time per case (human): 1.5 hours/day ÷ 25 cases = 0.06 hours/case (Dana manually tracks Google Sheet, calculates timing, phones insurers)
  Cases per year: 6,250
  Fully loaded hourly cost: $55/hour (Dana, RN Practice Manager)
  Annual baseline cost: $20,625 (VALIDATED via Q18: Dana confirms 1-2 hours/day on PA chase work)

  Estimated tokens per case: 2,000 input + 500 output = 2,500 total
  Model: Claude 3.5 Sonnet
  Estimated token cost per case: $0.0135
  Tool calls per case: 2 (athenahealth PA status read × 1, athenahealth update × 1) = $0.002
  Infrastructure cost per case: $0.001
  HITL rate: 100% during learning (3-6 months); 20% in production (Dana spot-checks unpredictable insurers like Aetna)
  Learning phase HITL: $6,875 over 6 months (amortized: $2,292/year over 3 years)
  Production HITL: $1,833/year
  Estimated agent cost per case: $0.0165
  Annual agent cost: $4,228 (includes learning amortized + production oversight)

  Annual saving: $20,897
  Estimated build cost: $36,000 (2 months build: Google Sheet ingestion, pattern extraction, reinforcement learning)
  Payback period: 20.6 months
  Year 1 ROI: -42% (negative; strategic justification)
  3-Year ROI: 74%

Sequencing:
  Wave: 1 (PROMOTED from Wave 2; stakeholder priority [Q18] overrides economic ranking)
  Key integrations built: Google Sheets API, athenahealth PA status (unique to JtD-2; not reused)
  Dependencies: [A2] PA pattern stability (VALIDATED: HIGH), [A4] denial patterns learnable (VALIDATED: VERY HIGH), [A7] Google Sheet authoritative (VALIDATED: VERY HIGH), [A14] Dana's willingness to teach 3-6 months (VALIDATED: VERY HIGH)
  Strategic justification: Dana's #1 frustration (Q18); captures 11-year institutional knowledge before Dana moves to regional role; prevents visit aborts (Dr. Westbridge's triggering concern)

Delegation archetype: Agent-led + Human Oversight (3-6 month learning) → Fully Agentic for predictable insurers (Dana spot-checks Aetna)
Recommended next step: START Wave 1 build immediately; ingest Dana's Google Sheet, extract insurer patterns, design learning phase workflow
```

---

### JtD-4: Medication Reconciliation — Use Case Scoring Template

```
Use Case: Medication Reconciliation and Allergy Conflict Flagging
Process: Patient Intake (Front-Desk) + Physician Review
Volume: 180 patients/day at check-in (65,700 cases/year)

Suitability gate:
  Input structure: MEDIUM (athenahealth med list structured; DoseSpot structured; patient verbal report unstructured)
  Decision determinism: MEDIUM (list comparison partly deterministic; discrepancy interpretation requires reasoning)
  Tool coverage: HIGH (athenahealth API [A12], DoseSpot integrated with athenahealth, patient questionnaire accessible)
  Exception rate: MEDIUM (physicians "regularly" discover unreviewed med changes [A8]; frequency unquantified)
  Compliance risk: HIGH (drug interactions/allergy conflicts risk, BUT mitigated by physician review before prescribing)
  Gate result: PASS (risk mitigated by human backstop; agent flags, physician decides)

Scoring:
  Execution frequency score: 5 (Very frequent: 180/day)
  Non-deterministic effort score: 2.5 (Mostly deterministic with reasoning for discrepancies)
  Agentic value score: 12 (Marginal; validate TCO before proceeding)

Economics:
  Avg time per case (human): 
    - Front-desk: 0.1 hours (6 min: DoseSpot pull, patient verbal confirmation, documentation)
    - Physician: 0.033 hours (2 min saved: reviewing pre-flagged list vs. manual questioning)
  Cases per year: 65,700
  Fully loaded hourly cost: $35/hour (front-desk), $150/hour (physician)
  Annual baseline cost: 
    - Front-desk: $229,950
    - Physician time saved: $328,500 (conservative estimate: 2 min/patient)
    - Total: $558,450

  Estimated tokens per case: 2,000 input + 400 output = 2,400 total
  Model: Claude 3.5 Sonnet
  Estimated token cost per case: $0.012
  Tool calls per case: 2 (athenahealth med/allergy list × 1, DoseSpot fill history × 1) = $0.002
  Infrastructure cost per case: $0.001
  HITL rate: 100% perpetual (physician reviews all flagged discrepancies; agent does NOT auto-update)
  HITL cost: $0 additional (physician was already reviewing, just faster now)
  Estimated agent cost per case: $0.015
  Annual agent cost: $986

  Annual saving: $557,464 (conservative; assumes physician saves 2 min/patient on avg)
  Estimated build cost: $30,000 (reduced from $40K via Wave 2 athenahealth reuse; +1 week for [A6] prompting logic)
  Payback period: 0.6 months
  Year 1 ROI: 1,758% (highest of all JtDs)
  3-Year ROI: 5,474%

Sequencing:
  Wave: 3 (starts Month 13, after Waves 1-2 complete)
  Key integrations built: Reuses athenahealth + Availity from Wave 2; DoseSpot API integration
  Dependencies: [A6] DoseSpot gaps specification (VALIDATED: VERY HIGH; 5 categories specified: out-of-network 10-15%, other providers, OTC, supplements, samples; 70-80% capture rate)
  Agent prompt design: Must explicitly prompt for 5 categories of DoseSpot misses

Delegation archetype: Agent-led + Human Oversight (perpetual; physician reviews flagged discrepancies before prescribing)
Recommended next step: Proceed to Wave 3 build (Month 13); design prompts for [A6] DoseSpot gaps; integrate with Wave 2 athenahealth
```

---

### JtD-3: Visit Reason Triage — Use Case Scoring Template

```
Use Case: Patient Visit Reason Triage and Clinical Urgency Flagging
Process: Patient Intake / Front-Desk Operations
Volume: 180 patients/day complete pre-visit questionnaires (65,700 cases/year)

Suitability gate:
  Input structure: MEDIUM (visit reason from questionnaire: mix of free text and structured fields; patient language highly variable)
  Decision determinism: LOW (distinguishing "routine" from "urgent" without clinical judgment [A13] is inherently fuzzy)
  Tool coverage: HIGH (athenahealth API for visit reason, patient history [A12])
  Exception rate: HIGH (patient language ambiguous; every visit reason requires judgment call about escalation)
  Compliance risk: VERY HIGH (patient safety risk; missing urgent symptom → patient harm; over-escalating → alert fatigue)
  Gate result: CONDITIONAL (clinical constraint [A13] + VERY HIGH risk block full autonomy; Human-led design required)

Scoring:
  Execution frequency score: 5 (Very frequent: 180/day)
  Non-deterministic effort score: 4 (Significant reasoning: NLP interpretation + pattern recognition)
  Agentic value score: 20 (Strongest by volume × non-determinism)

Economics:
  NOT ANALYZED (risk gates block; Wave 4 deferred)
  
  Rationale for deferral:
    - Clinical boundary constraint [A13] VALIDATED: "Recognition → escalate. Assessment → clinician." Front-desk can recognize keywords (chest pain, SOB, severe, sudden, can't); cannot assess severity
    - Malpractice constraints [A15] PARTIALLY VALIDATED: Dana expects human review required for anything clinical
    - Triage inconsistency [A5] VALIDATED: No written protocol; Dana trains verbally; false negative example (hypertensive crisis missed)

Sequencing:
  Wave: 4 (optional; deferred pending malpractice carrier approval and Waves 1-3 governance validation)
  Key integrations built: Reuses athenahealth from Wave 2; NLP visit reason parsing
  Dependencies: [A13] clinical boundary clarified (VALIDATED), [A15] malpractice carrier approval required (PENDING), Waves 1-3 establish governance/monitoring for high-risk use cases
  Prerequisites for Wave 4: Malpractice carrier explicitly approves AI-assisted triage with human review; Waves 1-3 validate HITL protocols

Delegation archetype: Human-led + Agent Support (conservative design; agent flags keywords/ambiguity, Dana/physician reviews 100%)
Recommended next step: DEFER until malpractice approval obtained; do NOT proceed to build without explicit risk mitigation plan
```

---

## Step 5: Strategic Sequencing Validation

**POST-COACH UPDATE (2026-04-29)**: Wave sequencing **REVISED** based on Dana's Q18 answer. Dana's #1 frustration is **PA timing misses that lead to visit aborts**, not billing failures. This changes stakeholder priority → Wave 1/Wave 2 swapped.

### Sequencing Criteria (from atx-scoring.md)

| Criterion | Weight | JtD-2 (PA Chase) | JtD-1 (Insurance) | JtD-4 (Med Recon) | JtD-3 (Triage) |
|-----------|--------|------------------|-------------------|-------------------|----------------|
| **Stakeholder priority** | **VERY HIGH** ⬆️ | ✅ Dana's #1 (Q18) | ⚠️ Back-office | ✅ Physician time | _Deferred_ |
| **Self-financing ROI** | High | ⚠️ -42% Year 1 (strategic) | ✅ 171% Year 1 | ✅ 1,758% Year 1 | _Deferred_ |
| **Integration reusability** | High | ⚠️ Google Sheet (unique to JtD-2) | ✅ athenahealth + Availity (reused in JtD-4) | ✅ Reuses athenahealth from JtD-1 | ✅ Reuses athenahealth |
| **Low compliance risk** | Medium | ✅ Administrative (reversible) | ✅ Administrative only | ✅ Risk mitigated (physician backstop) | ❌ VERY HIGH (patient safety) |
| **Data readiness** | Medium | ✅ Google Sheet [A7: VERY HIGH ⬆️] accessible | ✅ All accessible [A12: HIGH ⬆️] | ✅ [A6: VERY HIGH ⬆️⬆️] now specified | ✅ All data accessible |
| **Organizational readiness** | Medium | ✅ Dana willing to teach 3-6mo [A14: VERY HIGH ⬆️⬆️⬆️] | ✅ Low HITL overhead | ✅ Physician time savings motivate | ⚠️ Requires 100% physician review |
| **Strategic visibility** | High | ✅ Visit abort prevention (Dr. Westbridge complaint) | ⚠️ Billing failure prevention (back-office) | ✅ Physician time savings (high visibility) | _Deferred_ |

**Key finding from coach validation (Q18)**: "What's your biggest frustration? **That's easy: the PA timing misses that lead to visit aborts**. When a patient shows up for a procedure or an imaging scan, expecting to get it done, and then we tell them, 'Sorry, the prior auth is still pending, we have to reschedule' — that's the worst. If I could fix one thing, it would be proactive PA chase timing that never misses a deadline."

---

### REVISED Wave 1: JtD-2 (PA Chase Timing) — **Dana's #1 Priority**

**Original Phase 3 rationale**: Strategic value (institutional knowledge capture), scales to team, prevents visit aborts → assigned Wave 2

**REVISED rationale (post-coach)**: **Stakeholder priority overrides economic ranking**. Dana explicitly identified PA timing misses as her #1 frustration (Q18). This was the trigger for Dr. Westbridge asking Dana to explore AI (Artefact 5.2: patient TJ's second visit abort → physician complaint).

**Phase 4 validation (post-coach)**:
- ✅ **Stakeholder priority**: Dana's #1 (Q18); Dr. Westbridge's triggering concern (Artefact 5.2)
- ✅ **Validated baseline**: Dana's PA time 1-2 hours/day confirmed (Q18); Year 1 ROI still negative (-42%) but strategic value justifies
- ✅ **Institutional knowledge urgency**: Dana wants regional manager role in 5 years [A14: VERY HIGH ⬆️⬆️⬆️]; must capture her 11-year patterns [A2: HIGH ⬆️, A4: VERY HIGH ⬆️] before she moves
- ✅ **Organizational readiness**: Dana willing to teach patterns 3-6 months (career-building: "success = replicable system for other practices")
- ✅ **Data readiness**: Google Sheet [A7: VERY HIGH ⬆️] accessible; patterns stable 6-12 months [A2: HIGH ⬆️]
- ⚠️ **Integration reusability**: Google Sheet API unique to JtD-2 (not reused), but doesn't block other waves

**Strategic justification**:
1. **Alignment with stakeholder priority**: Dana said this is her #1 frustration → starting here builds trust, momentum
2. **Business continuity**: Captures Dana's institutional knowledge [A2, A4, A7] before she moves to regional role [A14] → eliminates single point of failure
3. **Prevents visit aborts**: Directly addresses Dr. Westbridge's triggering concern (Artefact 5.2: patient TJ's frustration)
4. **Scalable knowledge**: PA patterns systematized → front-desk team + future hires can handle chases

**Conclusion**: ✅ **PROMOTED to Wave 1** (from Wave 2) — stakeholder priority + institutional knowledge urgency override marginal Year 1 economics

**Success metrics**:
- Zero visit aborts from PA timing misses (currently ~1/month inferred from Artefact 5.2)
- Agent learns 15+ insurer-specific patterns (Humana 6d, UHC 7d [A2: HIGH ⬆️], Wellpath denial workaround [A4: VERY HIGH ⬆️], etc.)
- Dana's time reduced from 1-2 hours/day (validated Q18) to ~15 min spot-checking

**Timeline**: 8-11 months (2 months build + 3-6 months learning phase + 2-3 months production transition)

---

### REVISED Wave 2: JtD-1 (Insurance Re-Verification) — **Self-Funding**

**Original Phase 3 rationale**: Quick win, clear rule, high volume, immediate ROI → assigned Wave 1

**REVISED rationale (post-coach)**: Moved to Wave 2 to prioritize Dana's #1 frustration (PA chase). Still strong candidate: high ROI (171%), fast payback (4.4 months), builds reusable integrations for Wave 3.

**Phase 4 validation (post-coach)**:
- ✅ Self-financing ROI: 171% Year 1, payback 4.4 months
- ✅ Integration reusability: athenahealth + Availity → **reused in Wave 3** (medication reconciliation)
- ✅ Low compliance risk: Administrative only, reversible
- ✅ Data readiness: All accessible [A12: HIGH ⬆️]
- ✅ Organizational readiness: Low HITL (Dana spot-checks), front-desk already uses Availity
- ✅ **Re-verification rule validated** [A3: VERY HIGH ⬆️]: >6mo + chronic patient (≥3 visits/year), plus sub-rules (Medicaid every 3mo, Medicare Advantage in Q4, new insurance at next visit)

**Why Wave 2 (not Wave 1)**:
1. **Stakeholder priority**: Dana's #1 is PA chase (Q18), not billing failures (though both are important)
2. **Integration sequencing**: Wave 1 (PA chase) doesn't build reusable integrations → Wave 2 can start during Wave 1 learning phase (6-month overlap)
3. **Still self-funding**: $108K annual savings funds Wave 1 build cost retrospectively

**Conclusion**: ✅ **MOVED to Wave 2** (from Wave 1) — stakeholder priority drives sequencing, but economics remain strong

**Success metrics**:
- Zero billing failures from stale verification (currently 3/quarter, validated Q6)
- 30-50 proactive re-verifications/month
- $0 API cost increase (re-verify only when needed)

**Timeline**: 4 months (can start Month 5, during Wave 1 learning phase)

---

### Wave 3 Validation: JtD-4 (Medication Reconciliation) — **Highest ROI**

**Phase 3 rationale**: High volume, immediate physician time savings, depends on [A6] DoseSpot scope validation

**Phase 4 validation (post-coach)**:
- ✅ Self-financing ROI: **1,758% Year 1** (highest of all JtDs), payback 0.6 months
- ✅ Integration reusability: Reuses athenahealth from Wave 2 (insurance verification), DoseSpot already integrated
- ✅ Low compliance risk: Risk mitigated by physician review (human backstop)
- ✅ **Data readiness**: [A6: VERY HIGH ⬆️⬆️] **DoseSpot gaps now fully specified** (Q14, Q17 validated):
  1. Out-of-network pharmacies (10-15%): Mail-order, independent, out-of-state, non-networked chains
  2. Other providers' prescriptions: Specialists, ER, urgent care — DoseSpot shows fill but not prescriber/reason
  3. OTC medications: Aspirin, ibuprofen, allergy meds, supplements (interaction risk for warfarin patients)
  4. Medication samples: Specialists give samples, no pharmacy fill → DoseSpot never sees it
  5. Stopped medications: DoseSpot shows old fills, patient stopped but never told anyone
  - **Dana's estimate** (Q14): DoseSpot captures 70-80% of pharmacy fills, 0% of OTC/samples
- ✅ Organizational readiness: Physician time savings motivate adoption, no new HITL burden
- ✅ Strategic visibility: Physician time savings (16.5 hours/day freed up across 180 patients)

**Agent prompt design (based on validated [A6] gaps)**:
- Agent must explicitly prompt for missing sources:
  - "Any medications filled at other pharmacies (mail-order, independent, out-of-state)?"
  - "Any over-the-counter medications like aspirin, ibuprofen, allergy meds?"
  - "Any vitamins or supplements?"
  - "Any medication samples from specialists?"
  - "Any prescriptions from other providers (specialists, urgent care, ER)?"
- Build time increases by ~1 week for additional prompting logic (from 3 weeks to 4 weeks)
- **ROI still strong** (1,758% Year 1 ROI remains valid; conservative physician time savings assumption)

**Conclusion**: ✅ **Confirmed as Wave 3** — [A6] now validated, agent scope finalized. Reuses Wave 2 athenahealth + Availity integrations.

**Success metrics**:
- Physician review time reduced from 6 min to 30 sec per patient
- Zero unreviewed med changes discovered at visit (currently "regular" [A8: MEDIUM ⬆️])
- Front-desk time freed: 15 hours/day across team (900 min/day × $35/hour = $525/day savings)

**Timeline**: 4 months (starts Month 13, after Waves 1-2 complete)

---

### Wave 4 Validation: JtD-3 (Visit Reason Triage)

**Phase 3 rationale**: Clinical boundary constraint [A13] + VERY HIGH risk (patient safety) → defer pending [A13] and [A15] validation

**Phase 4 validation (post-coach)**:
- ❌ Compliance risk: **VERY HIGH** (patient safety); malpractice constraints validated [A15: MEDIUM] → Dana expects human review required
- ⚠️ Organizational readiness: Requires 100% physician review (Human-led design); alert fatigue risk
- ❓ Self-financing ROI: Not analyzed (risk gates block)
- ✅ **Clinical boundary clarified** [A13: VERY HIGH ⬆️]: "Recognition → escalate. Assessment → clinician." Front-desk can recognize keywords (chest pain, SOB, severe, sudden, can't) and escalate; cannot assess severity or decide disposition.
- ✅ **Triage inconsistency validated** [A5: HIGH ⬆️]: No written protocol; Dana trains verbally; false negative example (hypertensive crisis missed)

**Conclusion**: ✅ **Confirmed as Wave 4 (deferred)** — proceed only after:
1. ✅ [A13] clinical boundary clarified (Q13 validated: "Recognition → escalate")
2. ⚠️ [A15] malpractice carrier approval required (Q20 validated: Dana expects human review for clinical decisions)
3. ⏳ Waves 1-3 validated governance, testing, monitoring infrastructure for high-risk use cases

**Success metrics** (if pursued):
- Standardized triage across 4-person team (reduce inconsistency [A9: HIGH ⬆️])
- Zero missed urgent symptoms (maintain current safety level, improve consistency)
- <5% false positive rate on escalations (prevent alert fatigue)

---

### Wave Structure Summary (REVISED post-coach)

| Wave | JtD | Timeline | Build Cost | Year 1 ROI | Payback | Rationale |
|------|-----|----------|-----------|-----------|---------|-----------|
| **1** | **PA Chase Timing** | 8-11 months | $36,000 | -42% (strategic) | 20.6 mo | **Dana's #1 priority** (Q18); institutional knowledge capture [A2: HIGH ⬆️, A4: VERY HIGH ⬆️, A7: VERY HIGH ⬆️]; prevents visit aborts (Dr. Westbridge's triggering concern); captures patterns before Dana moves to regional role [A14: VERY HIGH ⬆️⬆️⬆️] |
| **2** | **Insurance Re-Verification** | 4 months (can start Month 5, during Wave 1 learning) | $40,000 | **171%** | 4.4 mo | Self-funding; builds athenahealth + Availity integrations reused in Wave 3; re-verification rule validated [A3: VERY HIGH ⬆️] |
| **3** | **Medication Reconciliation** | 4 months (starts Month 13) | $30,000 | **1,758%** | 0.6 mo | Highest ROI; [A6: VERY HIGH ⬆️⬆️] DoseSpot gaps now specified; reuses Wave 2 athenahealth integration; physician time savings |
| **4** | **Visit Reason Triage** (optional) | TBD (deferred) | TBD | TBD | TBD | Clinical constraint [A13: VERY HIGH ⬆️] validated; malpractice requires human review [A15: MEDIUM]; deferred until Waves 1-3 validate governance |

**Compounding thesis** (from atx-concepts.md):
- Wave 2 builds athenahealth + Availity integrations → **Wave 3 reuses**, reducing build cost from estimated $40,000 to $30,000 (integration already exists)
- Wave 1 establishes governance, testing, monitoring (Dana's 3-6 month learning phase validates HITL protocols) → **Waves 2-3 inherit**, reducing marginal validation cost
- By Wave 3, practice has 2 agents in production → **platform infrastructure amortized**, lowering future agent development cost

**Key change (post-coach)**: **Stakeholder priority overrides economic ranking**. Dana's Q18 answer ("PA timing misses are my biggest frustration") + Dr. Westbridge's triggering concern (Artefact 5.2) + Dana's career timeline [A14] justify starting with PA Chase despite negative Year 1 ROI.

---

## Prioritized Candidate Shortlist

### Ranked by Combined Score (REVISED post-coach)

**POST-COACH UPDATE**: Wave sequencing revised based on validated stakeholder priority (Q18). Dana's #1 frustration overrides pure economic ranking.

| Rank | JtD | Agentic Value | Feasibility | Year 1 ROI | Payback | Combined Priority | Recommended Wave |
|------|-----|--------------|------------|-----------|---------|------------------|-----------------|
| **1** | **PA Chase Timing (JtD-2)** | 15 (Strong) | 3.3 (Medium) | -42% (strategic) | 20.6 mo | ✅ **Stakeholder priority** (Q18: Dana's #1) | **Wave 1** ⬆️ |
| **2** | **Insurance Re-Verification (JtD-1)** | 15 (Strong) | 4.5 (Very High) | 171% | 4.4 mo | ✅ **Self-funding** | **Wave 2** ⬇️ |
| **3** | **Medication Reconciliation (JtD-4)** | 12 (Marginal) | 4.5 (Very High) | **1,758%** | 0.6 mo | ✅ **Highest ROI** ([A6: VERY HIGH ⬆️⬆️] validated) | **Wave 3** |
| **4** | **Visit Reason Triage (JtD-3)** | 20 (Strongest) | 3.6 (Medium, but risk blocks) | _Deferred_ | _Deferred_ | ⚠️ **Deferred** (risk gates) | **Wave 4** (optional) |

### Final Sequencing Recommendation (REVISED post-coach)

**Wave 1 (Months 1-11): PA Chase Timing**
- **Why first**: **Dana's #1 frustration** (Q18); Dr. Westbridge's triggering concern (Artefact 5.2: visit aborts); captures Dana's institutional knowledge [A2: HIGH ⬆️, A4: VERY HIGH ⬆️, A7: VERY HIGH ⬆️] before she moves to regional role [A14: VERY HIGH ⬆️⬆️⬆️]
- **Success criteria**: Zero visit aborts, agent learns 15+ insurer patterns, Dana's time reduced from 1-2 hours/day (validated Q18) to ~15 min
- **Timeline**: 2 months build + 3-6 months learning phase + 2-3 months production transition

**Wave 2 (Months 5-8): Insurance Re-Verification**
- **Why second**: Self-funding (171% ROI), builds athenahealth + Availity integrations reused in Wave 3, re-verification rule validated [A3: VERY HIGH ⬆️]
- **Can start during Wave 1 learning phase** (6-month overlap): Wave 1 learning doesn't block Wave 2 build
- **Success criteria**: Zero billing failures, 30-50 re-verifications/month, $108K annual savings
- **Timeline**: 4 months (starts Month 5)

**Wave 3 (Months 13-16): Medication Reconciliation**
- **Why third**: Highest ROI (1,758%), reuses Wave 2 athenahealth integration, [A6: VERY HIGH ⬆️⬆️] DoseSpot gaps now specified (Q14)
- **Success criteria**: Physician time 6 min → 30 sec per patient, zero unreviewed med changes, $557K annual savings
- **Timeline**: 4 months (starts Month 13, after Waves 1-2 complete)

**Wave 4 (Optional, TBD): Visit Reason Triage**
- **Why deferred**: Clinical constraint [A13: VERY HIGH ⬆️] validated, malpractice requires human review [A15: MEDIUM], deferred until Waves 1-3 validate governance
- **Prerequisites**: Malpractice carrier approval; Waves 1-3 establish governance/monitoring for high-risk use cases

---

## Implementation Roadmap (REVISED post-coach)

### Year 1: Stakeholder Priority + Self-Funding (Waves 1-2)

**POST-COACH UPDATE**: Wave sequencing revised. Wave 1 starts with PA Chase Timing (Dana's #1 priority), Wave 2 overlaps during Wave 1 learning phase.

**Q1-Q4 (Months 1-11): Wave 1 — PA Chase Timing**
- Months 1-2: Build (Google Sheet ingestion [A7: VERY HIGH ⬆️], insurer pattern extraction, chase timing logic, escalation rules)
- Month 3: Integration (athenahealth API [A12: HIGH ⬆️], Google Sheets API)
- Months 4-9 (or 4-11): Learning phase (Dana teaches patterns, agent recommends chase timing, Dana approves/corrects)
  - Agent learns insurer-specific patterns: Humana 6d, UHC 7d [A2: HIGH ⬆️], Wellpath denial workaround [A4: VERY HIGH ⬆️], Aetna unpredictable
  - Reinforcement: Agent adjusts patterns based on Dana's corrections
  - Dana's time investment: 1-2 hours/day (validated Q18) → 2 min/case review × 25 PAs/day = 50 min/day
- Month 10-11: Production transition (Dana spot-checks unpredictable insurers, agent handles predictable ones autonomously)
- **Deliverables**: Agent-led PA chase timing (→ Fully Agentic for predictable insurers), Dana's institutional knowledge systematized [A2, A4, A7], Google Sheet pattern codified
- **Economics**: $36K build cost, $10K Year 1 savings (partial year, Months 10-11), **net cost Year 1** = -$26K (strategic investment)
- **Strategic value**: Prevents visit aborts (Dr. Westbridge's triggering concern), captures Dana's knowledge before regional role transition [A14: VERY HIGH ⬆️⬆️⬆️]

**Q2-Q3 (Months 5-8): Wave 2 — Insurance Re-Verification** (overlaps with Wave 1 learning phase)
- Month 5: Build (re-verification logic [A3: VERY HIGH ⬆️], Availity error patterns, chronic patient detection)
- Month 6: Integration (athenahealth + Availity APIs [A12: HIGH ⬆️])
- Month 7: Testing + Dana validation (1-month pilot, 100% review of re-verification triggers)
- Month 8: Production rollout (spot-checks only, 5% Dana review)
- **Deliverables**: Fully agentic re-verification, athenahealth + Availity integrations (reusable in Wave 3)
- **Economics**: $40K build cost, $54K Year 1 savings (Months 8-12 = 5 months), **net profit Year 1** = $14K
- **Cumulative Year 1**: Wave 1 (-$26K) + Wave 2 (+$14K) = **-$12K net** (strategic investment in Wave 1, partially offset by Wave 2 self-funding)

---

### Year 2: Compounding Returns (Wave 3)

**Q1 (Months 13-16): Wave 3 — Medication Reconciliation**
- **Prerequisite**: ✅ [A6: VERY HIGH ⬆️⬆️] DoseSpot gaps validated (Q14, Q17) → agent prompt finalized
- Month 13: Build (three-source reconciliation, discrepancy interpretation, gap source prompts [A6])
  - Agent prompts for 5 categories of DoseSpot misses: out-of-network pharmacies, other providers' prescriptions, OTC meds, supplements, samples
  - Build time: 4 weeks (includes 1 week additional prompting logic)
- Month 14: Integration (**reuses athenahealth + Availity from Wave 2**, DoseSpot API [A12: HIGH ⬆️])
- Month 15: Testing + physician validation (1-month pilot, 100% physician review of flagged discrepancies)
- Month 16: Production rollout (perpetual physician review; agent flags, physician decides)
- **Deliverables**: Agent-led medication reconciliation + Human Oversight (perpetual)
- **Economics**: $30K build cost (reduced via Wave 2 athenahealth reuse), $557K annual savings → **$527K net profit**
- **Cumulative economics** (Waves 1-3 through Month 24):
  - Year 1 (partial): Wave 1 (-$26K) + Wave 2 (+$14K) = -$12K
  - Year 2 (full): Wave 1 (+$21K) + Wave 2 (+$108K) + Wave 3 ($557K × 8/12 months = +$371K) = +$500K
  - **Cumulative savings by end of Month 24**: **+$488K**

**Q2-Q4 (Months 20-24): Platform Optimization**
- Model routing: Use Claude Haiku for simple verifications (JtD-1), Sonnet for PA chase (JtD-2), Sonnet for med recon (JtD-4) → optimize token economics
- Caching: Implement prompt caching for repeated context (Dana's PA patterns, re-verification rules) → reduce token cost 10-20%
- Monitoring: Real-time agent performance dashboard (exception rates, HITL escalations, cost per case, accuracy metrics)
- Governance: Formalize HITL escalation protocols, audit logging, patient consent workflow (HIPAA compliance)

---

### Year 3: AI-Native Operations (Optional Wave 4 + Multi-Agent Workflows)

**Q1 (Months 25-28, if [A13] and [A15] validated): Wave 4 — Visit Reason Triage**
- **Prerequisites**: 
  - [A13] clinical boundary clarified via coach (Q13) → bright-line triage rules established
  - [A15] malpractice constraints validated (Q20) → agent design complies with policy
  - Waves 1-3 governance/monitoring validated for high-risk use cases
- Month 25: Build (NLP visit reason parsing, keyword-based urgency flagging, escalation logic)
- Month 26: Integration (**reuses athenahealth from Wave 1**)
- Month 27: Conservative pilot (agent flags 100% of ambiguous cases → Dana/physician reviews all)
- Month 28: Calibration (collect physician feedback on false positives/negatives → refine keyword list)
- **Deliverables**: Human-led + Agent Support (conservative escalation; agent assists, human decides)
- **Economics**: TBD (depends on front-desk triage error rate [A5] and physician time savings from standardized triage)

**Q2-Q4 (Months 29-36): Multi-Agent Coordination**
- **Agent-to-agent workflows**: JtD-1 (insurance verification) flags re-verification case → triggers JtD-4 (med reconciliation) to check if patient's med changes align with insurance change (e.g., switched from commercial to Medicare → different drug formulary)
- **Coordinated PA + Med Recon**: JtD-2 (PA chase) identifies procedure requiring PA → triggers JtD-4 to flag if patient's current meds interact with procedure (e.g., blood thinner before surgery)
- **Platform-level cost optimization**: Agent orchestration layer routes cases to cheapest sufficient model (Haiku for simple, Sonnet for complex, Opus for edge cases requiring maximum reasoning)

---

## Assumption Dependencies & Update Protocol

### Critical Assumptions — POST-COACH VALIDATION STATUS (2026-04-29)

| Assumption | Status | Affects | Validated Answer | Impact on Design |
|-----------|--------|---------|------------------|------------------|
| **[A3]** Re-verification rule | ✅ **VALIDATED** (VERY HIGH ⬆️) | Wave 2 (Insurance) scope | Q6, Q8, Q9: >6mo + chronic patient (≥3 visits/year), plus sub-rules (Medicaid every 3mo, Medicare Advantage Q4, new insurance at next visit) | Agent scope finalized; rule is deterministic once encoded |
| **[A6]** DoseSpot gaps | ✅ **VALIDATED** (VERY HIGH ⬆️⬆️) | Wave 3 (Med Recon) scope | Q14, Q17: 5 categories of misses specified (out-of-network 10-15%, other providers, OTC, supplements, samples). Dana estimates 70-80% pharmacy fills, 0% OTC/samples. | Agent prompts finalized; build time +1 week for additional prompting logic; ROI unchanged |
| **[A2]** PA pattern stability | ✅ **VALIDATED** (HIGH ⬆️) | Wave 1 (PA Chase) design | Q3: UHC changed 18 months ago; patterns stable 6-12 months but occasional policy changes; Dana tracks and adjusts | Agent must detect pattern deviation; learning phase 3-6 months validated |
| **[A4]** PA denial patterns learnable | ✅ **VALIDATED** (VERY HIGH ⬆️) | Wave 1 (PA Chase) design | Q2: Wellpath colonoscopy 30-40 occurrences over 6 years, 100% consistent. "Standing rule in my head" | Agent can reliably learn denial workarounds from Dana's Google Sheet + corrections |
| **[Q18]** Dana's actual PA time | ✅ **VALIDATED** | Wave 1 (PA Chase) ROI | Q18: Dana confirms 1-2 hours/day: "I check my Google Sheet every morning, I eyeball the submission dates, I calculate the target chase day in my head based on the insurer, and I make phone calls." | Baseline cost validated at $20,625/year; Year 1 ROI remains -42% (strategic justification stands) |
| **[A14]** Dana's personal stake | ✅ **VALIDATED** (VERY HIGH ⬆️⬆️⬆️) | Wave 1 priority, Dana's willingness | Q22: Dana wants regional manager role in 5 years; success = replicable system for other practices; resume-building for operations leadership | Dana highly motivated; willing to teach patterns 3-6 months; captures knowledge before role transition |
| **[A13]** Clinical judgment boundary | ✅ **VALIDATED** (VERY HIGH ⬆️) | Wave 4 (Visit Triage) design | Q13: "Recognition → escalate. Assessment → clinician." Front-desk can recognize keywords (chest pain, SOB, severe, sudden, can't); cannot assess severity or decide disposition. | Agent scope constrained to keyword flagging + escalation; Human-led design required |
| **[A15]** Malpractice constraints | ⚠️ **PARTIALLY VALIDATED** (MEDIUM) | All JtDs autonomy level | Q20: Dana hasn't asked carrier yet, but expects human review required for anything clinical; "AI can assist, but a human has to review and approve" | Conservative design assumption: Human Oversight required for all JtDs; "Fully Agentic" OK for administrative only (insurance, PA chase once learned) |
| **[A12]** API availability | ⚠️ **INFERRED** (HIGH ⬆️) | All waves integration | Dana mentions athenahealth subscription, Availity access, DoseSpot integrated; implies APIs exist (needs technical validation) | Assume APIs available; validate during Wave 1 build Month 1 |

### Update Protocol — POST-COACH COMPLETION (2026-04-29)

✅ **Coach validation completed**. All critical assumptions validated via coach role-play (see `coach-roleplay-answers.md`).

**Updates applied**:

1. ✅ **Step 2: Volume × Value Scoring**
   - [Q18] validated Dana's PA time at 1-2 hours/day → JtD-2 baseline cost confirmed at $20,625/year
   - [A6] DoseSpot gaps fully specified (5 categories) → JtD-4 Non-Determinism score remains 2.5 (discrepancy interpretation still needed, but scope clear)

2. ✅ **Step 3: TCO Assessment**
   - JtD-2 (PA Chase): Dana's time validated (Q18), baseline unchanged
   - JtD-4 (Med Recon): [A6] adds 1 week build time (from 3 weeks to 4 weeks), build cost remains $30K

3. ✅ **Step 4: Feasibility Scoring**
   - [A2] PA patterns stable 6-12 months (HIGH ⬆️) → JtD-2 "Context stability" remains 3
   - [A15] malpractice expects human review → design already assumes Human Oversight; no downgrade needed

4. ✅ **Step 5: Strategic Sequencing**
   - **MAJOR CHANGE**: Dana's Q18 answer ("PA timing misses are my biggest frustration") → **Wave 1/Wave 2 swapped**
   - JtD-2 (PA Chase) promoted to Wave 1 (stakeholder priority overrides economics)
   - JtD-1 (Insurance) moved to Wave 2 (can start during Wave 1 learning phase)
   - [A6] validated → JtD-4 (Med Recon) scope finalized; Wave 3 confirmed

5. ✅ **Prioritized Candidate Shortlist**
   - Re-ranked with JtD-2 as #1 (stakeholder priority)
   - Wave assignments updated: PA Chase (Wave 1), Insurance (Wave 2), Med Recon (Wave 3)

**Iteration tracking**: All updates documented in `build-loop/iteration-003.md`.

---

## Next Steps

**Pre-Implementation (Completed)**:
1. ✅ Complete Phase 4 candidate prioritization (this document)
2. ✅ **Coach role-play: All 24 questions** (see `coach-roleplay-answers.md`) → validated critical assumptions [A6], [Q18], [A15], [A2], [A3], [A4], [A14], [A13]
3. ✅ Update Phase 4 TCO and feasibility scores based on coach answers (completed 2026-04-29)
4. ✅ **Wave sequencing revised**: PA Chase Timing promoted to Wave 1 based on stakeholder priority (Q18)

**Wave 1 Build (PA Chase Timing) — Ready to Proceed**:
5. ⏳ **Ingest Dana's Google Sheet** (Artefact 5.1 + full historical data)
6. ⏳ **Extract insurer-specific patterns** from Google Sheet:
   - Humana: 6 days (always, never 5)
   - UnitedHealthcare Choice: 7 days
   - Wellpath: 7 days + always denies colonoscopy first time (attach prior visit note preemptively)
   - Medicare: 4-5 days
   - BCBS PPO: 3 days
   - Aetna: Unpredictable (escalate to Dana)
7. ⏳ **athenahealth API documentation review** → validate [A12: HIGH ⬆️] (APIs available, rate limits, authentication requirements)
8. ⏳ Agent architecture design (orchestration, tool interfaces, guardrails, HITL escalation protocols)
9. ⏳ Development environment setup (Claude API, athenahealth sandbox, Google Sheets API)
10. ⏳ Build PA chase logic (chase timing calculation, insurer pattern matching, escalation rules)
11. ⏳ Integration testing (athenahealth ↔ Google Sheet ↔ agent)
12. ⏳ **Dana learning phase** (3-6 months): Dana approves all chase recommendations, agent learns from corrections
13. ⏳ Production transition: Agent handles predictable insurers autonomously, Dana spot-checks Aetna

---

**End of Phase 4: Candidate Prioritization**

**Status**: PROVISIONAL — depends on coach validation of [A6], [Q18], [A15], [A2], [A12]
