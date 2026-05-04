# Cognitive Map: Westbridge Family Medicine Patient Intake

## Executive Summary

**Context**: 6-physician family medicine practice, 4-person intake team, ~180 patients/day across two locations. Practice Manager Dana Velazquez (RN, 11 years tenure) faces physician complaints about intake misses — primarily expired prior authorizations discovered at visit time.

**Primary pain point**: Knowledge-intensive exception handling concentrated in Dana's head and Google Sheets, while front-desk team executes structured verification work that occasionally fails catastrophically when tacit rules aren't applied.

---

## Table of Contents

1. [Jobs to be Done (JtDs) Decomposition](#1-jobs-to-be-done-jtds-decomposition)
2. [Micro-Task Inventory with Cognitive Load Scores](#2-micro-task-inventory-with-cognitive-load-scores)
3. [Cognitive Topology: Zones and Critical Breakpoints](#3-cognitive-topology-zones-and-critical-breakpoints)
4. [Lived Process Narrative: What Really Happens vs. What the SOP Says](#4-lived-process-narrative-what-really-happens-vs-what-the-sop-says)
5. [Assumption Register (with Confidence Levels)](#5-assumption-register-with-confidence-levels)
6. [Delegation Archetype Assignment (Preliminary)](#6-delegation-archetype-assignment-preliminary)
7. [Key Cognitive Hotspots (Where Agents Create Disproportionate Value or Risk)](#7-key-cognitive-hotspots-where-agents-create-disproportionate-value-or-risk)
8. [Design-Changing Questions for Coach Role-Play](#8-design-changing-questions-for-coach-role-play-dana-velazquez)
9. [Summary: Where Agents Win vs. Where Humans Must Stay](#9-summary-where-agents-win-vs-where-humans-must-stay)
10. [Next Steps for FDE (You)](#10-next-steps-for-fde-you)

---

## 1. Jobs to be Done (JtDs) Decomposition

### JtD-1: Verify insurance eligibility for scheduled visit
**Trigger**: Patient scheduled appointment (typically 1-7 days before visit)  
**Actor**: Front-desk staff (rotates between locations)  
**Goal**: Confirm patient's insurance is active and visit type is covered  
**Key decisions**: 
- When to re-verify (last verification > 6 months? patient population? insurer?)
- How to handle verification failures (escalate, delay visit, convert to self-pay?)

**Key systems**: athenahealth (patient record), Availity (eligibility API)  
**Expected output**: Verification status in athenahealth; escalation to Dana if complex  
**Primary cognitive nature**: Execution with exception-pattern recognition

**Cognitive Zones**:
1. **Intent understanding** (LOW): Appointment type known, insurance on file
2. **Data retrieval** (MEDIUM): Pull from athenahealth → query Availity API
3. **Diagnosis** (HIGH for exceptions): ~30% fail auto-verify [A1], requiring interpretation of Availity response codes, patient history, prior verification dates
4. **Decision** (MEDIUM→HIGH): Accept verification / escalate / re-query with different parameters
5. **Documentation** (LOW): Update athenahealth verification status

**Breakpoints**:
- **Rule → Judgment**: When auto-verify fails (30% of cases [A1]) — High confidence this is where human pattern recognition begins
- **System → Human**: Availity API returns ambiguous code or timeout
- **Frontline → Dana**: Complex Medicaid managed care, discrepancy between Availity and patient card

**Lived vs. Documented work gap**: 
- **Documented**: "Verify insurance via Availity for all scheduled appointments"
- **Lived**: Dana's tacit rule (visible in Artefact 5.3): "Refresh verification if >6 months, especially for chronic patients on stable insurance" — front-desk doesn't consistently apply this [A3], causing billing failures

---

### JtD-2: Determine prior authorization status and chase pending PAs
**Trigger**: Scheduled procedure/imaging/referral visit approaching (typically 5-7 days before)  
**Actor**: Dana (primarily) with front-desk support for submission  
**Goal**: Ensure PA is approved before visit; avoid visit abort or patient frustration  
**Key decisions**: 
- When to submit PA (how far in advance?)
- When to chase (insurer-specific patterns vs. stated SLA)
- How to respond to denials (resubmit with additional docs? escalate? delay visit?)

**Key systems**: athenahealth (PA submission), insurer portals (varying), Dana's Google Sheet (chase tracker)  
**Expected output**: PA approved in time for visit; visit rescheduled if not  
**Primary cognitive nature**: Judgment-dependent execution with deep exception knowledge

**Cognitive Zones**:
1. **Intent understanding** (LOW): Procedure known, PA requirement clear
2. **Data retrieval** (MEDIUM→HIGH): Check athenahealth PA status, cross-reference with Google Sheet chase list, check insurer portal if necessary
3. **Diagnosis** (VERY HIGH): Interpret pending vs. denied vs. "silent pending" (insurer-specific); recognize denial patterns (e.g., Wellpath always denies colonoscopy first time, needs prior visit note)
4. **Decision** (VERY HIGH): When to chase (Humana: always 6 days, not 5; UnitedHealthcare Choice: 6-7 days; Aetna: sometimes fast, unpredictable)
5. **Action** (MEDIUM): Phone chase, resubmit with additional documentation, coordinate with physician for clinical justification
6. **Documentation** (MEDIUM): Update athenahealth and Google Sheet with status, notes, next chase date

**Breakpoints**:
- **Rule → Judgment**: Stated SLA (5 days) vs. Dana's learned SLA (insurer-specific: 6-7 days for some, fast-tracked for others) [A2]
- **System → Human**: Insurer portal doesn't update; requires phone call (unstructured)
- **Dana → Physician**: Denial requires additional clinical documentation
- **Frontline → Patient**: Visit must be rescheduled due to PA delay

**Lived vs. Documented work gap**: 
- **Documented**: "Submit PA per insurer requirements; follow up at day 5"
- **Lived**: Dana maintains insurer-specific chase timing in her head and Google Sheet (Artefact 5.1) [A7]. This is **pure institutional knowledge** — not in athenahealth, not in Availity, not documented anywhere formal. Example: "Wellpath always denies first time on colonoscopy — resubmit with August visit note" is a **learned workaround** [A4] preventing multi-week delays.

**Key assumption**: Dana's Google Sheet patterns are stable over time [A2] (MEDIUM confidence — insurers change policies, but slowly; patterns are validated over ~11 years of practice).

---

### JtD-3: Triage patient visit reason and flag clinical urgency
**Trigger**: Pre-visit questionnaire completion (day of visit or 1-2 days prior)  
**Actor**: Front-desk staff (initial review); Dana or physician (escalation for ambiguous cases)  
**Goal**: Classify visit as routine, urgent, or same-day; flag potential clinical red flags without making clinical judgments  
**Key decisions**: 
- Is stated reason consistent with scheduled visit type?
- Does reason suggest urgency requiring physician pre-notification?
- Should visit be converted to same-day or escalated?

**Key systems**: athenahealth (questionnaire module), phone intake for patients without portal  
**Expected output**: Visit reason documented; physician notified if urgent; visit type adjusted if necessary  
**Primary cognitive nature**: Pattern recognition with bright-line constraint (no clinical judgment)

**Cognitive Zones**:
1. **Intent understanding** (MEDIUM→HIGH): Interpret patient's stated reason (often ambiguous: "knee pain" vs. "knee pain, can't walk, started suddenly")
2. **Data retrieval** (LOW): Patient history, scheduled visit type
3. **Diagnosis** (HIGH): Does this cross into clinical territory? Is this "routine follow-up" or "new acute symptom"?
4. **Decision** (MEDIUM→HIGH): Accept as routine / flag for physician / escalate to same-day
5. **Communication** (MEDIUM): Notify physician if urgent; call patient if visit type needs to change
6. **Documentation** (LOW): Update athenahealth visit reason

**Breakpoints**:
- **Rule → Judgment**: Distinguishing administrative triage (safe for agent) from clinical triage (requires human)
- **Agent → Human escalation** (CRITICAL CONSTRAINT): Any ambiguity about clinical urgency must escalate to Dana or physician
- **Frontline → Physician**: Urgent symptoms flagged before patient arrives

**Lived vs. Documented work gap**: 
- **Documented**: "Review questionnaire; document visit reason"
- **Lived**: Implicit clinical judgment filtering — front-desk staff have learned over time when "chest pain" means "call physician now" vs. "routine cardiology follow-up for stable angina." This is **informal training** [A5], likely inconsistent across the 4-person team [A9].

**Key assumption**: Front-desk staff can reliably distinguish clinical urgency from administrative triage (LOW→MEDIUM confidence — Artefact 5.2 shows a PA status miss, suggesting attention/training gaps. Clinical triage errors would be more serious).

---

### JtD-4: Reconcile medications and flag allergy alerts
**Trigger**: Patient check-in (day of visit)  
**Actor**: Front-desk staff (initial reconciliation); physician (final review)  
**Goal**: Ensure athenahealth medication list matches patient's current regimen; flag new allergies or potential interactions  
**Key decisions**: 
- Is patient's stated medication list consistent with pharmacy records (DoseSpot)?
- Are there new medications not in athenahealth?
- Are there allergy conflicts with current medications?

**Key systems**: athenahealth (patient med list), DoseSpot (pharmacy reconciliation), patient verbal report  
**Expected output**: Updated medication list; allergy flags; physician notified of discrepancies  
**Primary cognitive nature**: Data reconciliation with exception escalation

**Cognitive Zones**:
1. **Intent understanding** (LOW): Patient states current medications (or confirms "no changes")
2. **Data retrieval** (MEDIUM): Pull athenahealth med list, DoseSpot pharmacy history
3. **Diagnosis** (MEDIUM→HIGH): Identify discrepancies (new meds, discontinued meds, dosage changes); interpret pharmacy fill dates vs. patient report
4. **Decision** (MEDIUM): Accept as reconciled / flag for physician review / escalate if allergy conflict
5. **Documentation** (MEDIUM): Update athenahealth med list, allergy list

**Breakpoints**:
- **System → Human**: DoseSpot shows recent fills not in athenahealth, but patient says "I stopped taking that"
- **Frontline → Physician**: New medication from another provider, or patient on OTC med not in system

**Lived vs. Documented work gap**: 
- **Documented**: "Reconcile medications using DoseSpot at check-in"
- **Lived**: **Unknown from artefacts** — we don't have visibility into where DoseSpot misses things (mentioned in scenario prompt) [A6]. This is a **critical elicitation target**.

**Key assumption**: DoseSpot integration with athenahealth is reliable for pharmacy-filled prescriptions [A6] (MEDIUM confidence — integration exists, but scope of "misses" is undefined). Non-pharmacy sources (OTC, supplements, other providers) likely require manual patient report.

---

## 2. Micro-Task Inventory with Cognitive Load Scores

| Micro-Task | JtD | Cognitive Load | Input Structure | Decision Determinism | Exception Freq | Turn-Taking | Latency | Compliance/Risk | Tool/API Availability |
|------------|-----|----------------|-----------------|---------------------|----------------|-------------|---------|----------------|---------------------|
| **Query Availity for insurance eligibility** | JtD-1 | L | H (structured API) | H | L | L (API call) | M (seconds) | H (billing impact) | H (REST API available) [A12] |
| **Interpret Availity failure codes** | JtD-1 | H | M (semi-structured error codes + patient context) | M | H (30% fail rate [A1]) | M (may need Dana) | M | H | M (API available; interpretation rules unclear) |
| **Determine if re-verification needed** | JtD-1 | H | L (last verified date in athenahealth) | L (tacit rule [A3]) | M | L | M | H | H (data available; rule is tacit) |
| **Submit PA to insurer** | JtD-2 | L | M (athenahealth form + clinical docs) | M | M | L (API or portal) | L (batch) | M | M (athenahealth API [A12]; insurer portals vary) |
| **Determine when to chase PA** | JtD-2 | VH | L (submission date + insurer + PA status) | L (insurer-specific learned pattern [A2]) | L | L | L | H (visit timing) | M (data in Google Sheet [A7]; not in athenahealth) |
| **Interpret PA denial reason** | JtD-2 | VH | L (denial code + insurer history) | L (pattern-based [A4]) | M | M (may need physician for docs) | M | H | L (denial codes exist; pattern knowledge is tacit) |
| **Resubmit PA with additional documentation** | JtD-2 | M | M (prior submission + new docs) | M | M | H (coordinate with physician) | M | H | M |
| **Parse patient visit reason from questionnaire** | JtD-3 | M | L (free text + structured fields) | M | M | L | M | H (clinical boundary [A13]) | H (athenahealth API [A12]) |
| **Determine if visit reason requires clinical escalation** | JtD-3 | VH | L (visit reason text + patient history) | L (judgment-dependent [A5]) | M | H (escalate to Dana/physician) | H (time-sensitive) | VH (clinical safety [A13]) | M (data available; decision boundary unclear) |
| **Pull pharmacy history from DoseSpot** | JtD-4 | L | H (structured API) | H | L | L | M | M | H (integrated with athenahealth [A12]) |
| **Identify med list discrepancies** | JtD-4 | M | M (athenahealth list + DoseSpot list + patient verbal) | M | M | M (ask patient to clarify) | M | H (clinical safety) | M (APIs available [A12]; reconciliation logic unclear [A6]) |
| **Flag allergy conflicts** | JtD-4 | M | H (structured allergy + med lists) | H | L | L | M | VH (clinical safety) | H (rule-based; available in athenahealth) |

**Scoring key**: H = High, M = Medium, L = Low, VH = Very High

---

## 3. Cognitive Topology: Zones and Critical Breakpoints

```
┌─────────────────────────────────────────────────────────────────┐
│                    INTAKE COGNITIVE FLOW                         │
└─────────────────────────────────────────────────────────────────┘

ZONE 1: PATIENT SCHEDULING (pre-intake)
├─ Trigger: Appointment scheduled in athenahealth
└─ Data state: Insurance on file, visit type known

     ↓ [Breakpoint: 1-7 days before visit]

ZONE 2: INSURANCE VERIFICATION (JtD-1)
├─ Auto-verify via Availity (70% success) ────────► LOW COGNITIVE LOAD
│
├─ BREAKPOINT: Availity failure (30% [A1]) ───────► HIGH COGNITIVE LOAD
│  ├─ Interpret error code (pattern recognition)
│  ├─ Check last verification date (tacit rule: >6mo = re-verify [A3])
│  ├─ Decision: Re-query / escalate to Dana / flag patient
│  └─ [If Medicaid managed care] → ESCALATE TO DANA
│
└─ BREAKPOINT: Verification stale (>6mo, chronic patient)
   └─ Missed by front-desk [A3] → billing failure (see Artefact 5.3)

     ↓ [Parallel track for subset of visits]

ZONE 3: PRIOR AUTHORIZATION MANAGEMENT (JtD-2)
├─ PA required (~25/day [A10]) → Dana's domain
│
├─ Submit PA (structured) ────────────────────────► LOW COGNITIVE LOAD
│
├─ BREAKPOINT: When to chase? ───────────────────► VERY HIGH COGNITIVE LOAD
│  ├─ Stated SLA (5 days) ≠ Lived SLA (insurer-specific [A2])
│  ├─ Dana's Google Sheet [A7]: Humana always 6d, UHC 6-7d, Aetna unpredictable
│  ├─ Decision: Chase now / wait / escalate
│  └─ This knowledge is NOT in athenahealth, Availity, or SOP [A11]
│
├─ BREAKPOINT: PA denial ─────────────────────────► VERY HIGH COGNITIVE LOAD
│  ├─ Interpret denial reason (pattern-based [A4])
│  ├─ Example: "Wellpath always denies colonoscopy first time — needs prior visit note" [A4]
│  ├─ Decision: Resubmit with docs / call insurer / coordinate with physician
│  └─ This is PURE INSTITUTIONAL KNOWLEDGE (11 years of pattern learning [A2, A4])
│
└─ BREAKPOINT: PA pending at visit time ──────────► OPERATIONAL FAILURE
   └─ Visit aborted, patient frustrated (see Artefact 5.2)

     ↓ [Day of visit or 1-2 days prior]

ZONE 4: VISIT REASON TRIAGE (JtD-3)
├─ Parse questionnaire (text + structured) ───────► MEDIUM COGNITIVE LOAD
│
├─ BREAKPOINT: Clinical urgency assessment ───────► VERY HIGH COGNITIVE LOAD
│  ├─ Distinguish "routine" from "urgent" without clinical judgment [A13]
│  ├─ CONSTRAINT: Must escalate ambiguity to Dana/physician
│  ├─ Decision: Accept as routine / flag physician / convert to same-day
│  └─ This is INFORMAL TRAINING (inconsistent across 4-person team [A5, A9])
│
└─ BREAKPOINT: Visit type mismatch
   └─ Patient expects MRI results, but PA still pending (see Artefact 5.2)

     ↓ [Day of visit: patient check-in]

ZONE 5: MEDICATION RECONCILIATION (JtD-4)
├─ Pull DoseSpot pharmacy history ────────────────► LOW COGNITIVE LOAD
│
├─ BREAKPOINT: Discrepancy between systems ───────► MEDIUM→HIGH COGNITIVE LOAD
│  ├─ DoseSpot shows fills, but patient says "I stopped taking that"
│  ├─ Patient reports OTC/supplement not in system [A6]
│  ├─ New med from another provider (not in DoseSpot [A6])
│  └─ Decision: Update athenahealth / flag physician / ask patient to clarify
│
├─ Flag allergy conflicts (rule-based) ───────────► LOW COGNITIVE LOAD
│
└─ BREAKPOINT: Physician discovers unreviewed med change at visit
   └─ Intake miss (mentioned in scenario brief; not detailed in artefacts [A8])

     ↓ [Visit occurs]

ZONE 6: POST-VISIT DOCUMENTATION & FEEDBACK
├─ Physician notes intake misses in chart (see Artefact 5.2)
└─ Dana investigates and updates tacit rules (not systematized)
```

---

## 4. Lived Process Narrative: What Really Happens vs. What the SOP Says

### The Documented Process (What the SOP Says)

Westbridge Family Medicine's documented intake process follows standard medical practice workflows:

1. **Insurance Verification**: "Verify all scheduled patients' insurance eligibility via Availity before visit"
2. **Prior Authorization**: "Submit PAs per insurer requirements; follow up at stated SLA (typically 5 days)"
3. **Visit Reason Review**: "Review pre-visit questionnaire; document visit reason in athenahealth"
4. **Medication Reconciliation**: "Reconcile patient medications using DoseSpot at check-in"

These documented steps assume:
- Systems provide all necessary information
- Stated SLAs are accurate
- Front-desk staff apply consistent procedures
- Exceptions are rare and handled through standard escalation

### The Lived Process (What Actually Happens)

The reality is significantly more complex, with critical work happening in the **gaps between documented steps**:

#### Gap 1: Dana's Invisible Re-Verification Rules [A3]

**Documented**: "Verify insurance via Availity for all scheduled appointments"

**Lived**: Dana has learned through painful experience that **insurance verification has an expiration date** [A3]. When a patient's insurance was last verified >6 months ago — especially for chronic patients with "stable" insurance — the verification status in athenahealth becomes unreliable. This rule exists **only in Dana's head**. Front-desk staff don't consistently apply it, leading to billing failures (Artefact 5.3: patient TJ received a $340 surprise bill because verification was 6+ months old, and the system pulled an outdated self-pay record from 2022).

**Real work**: Dana manually reviews verification dates for high-risk patients (chronic conditions, Medicaid managed care). When she catches it. When she has time. When the patient isn't already checked in.

**Why the gap exists**: athenahealth doesn't flag stale verifications. Availity doesn't proactively alert when eligibility is about to expire. Front-desk staff were never formally trained on the >6 month rule because **it's not written down anywhere** [A11].

---

#### Gap 2: Dana's Insurer-Specific Chase Timing Patterns [A2, A4, A7]

**Documented**: "Submit PA per insurer requirements; follow up at day 5"

**Lived**: **Stated SLAs are fiction**. Over 11 years, Dana has learned that each insurer has its own **actual** response timing, which bears little resemblance to their documented SLA:
- Humana: Always exactly 6 days, never 5 (Artefact 5.1)
- UnitedHealthcare Choice: 6-7 days, sometimes longer
- Aetna: Unpredictable — sometimes fast (3 days), sometimes slow (7+ days)
- Wellpath (Medicaid managed care): Always denies colonoscopy PAs the first time, requires prior visit note attached on resubmission (Artefact 5.1 footer: "never says so on the form")

Dana tracks these patterns in her **personal Google Sheet** [A7] — shared with front-desk, but maintained solely by her. Her "My target chase" column shows when she'll actually follow up, which is often 1-2 days later than the stated SLA. She adds notes like "Aetna fast this month, unusual" when insurers deviate from learned patterns.

**Real work**: Dana checks her Google Sheet daily, calculates chase timing based on submission date + insurer + her learned pattern (not the stated SLA), phones insurers at the right time, applies workarounds for known denial patterns (e.g., attaching prior visit note preemptively for Wellpath colonoscopies).

**Why the gap exists**: 
- Insurer portals rarely update in real-time; stated SLAs are aspirational, not actual
- Denial reasons are often vague; workarounds are discovered through trial-and-error over years
- Dana's patterns aren't documented in athenahealth or practice SOPs [A11] — they're **institutional knowledge locked in one person's head**
- When Dana is out sick or on vacation, PA chases either wait or front-desk guesses (Q4: "What happens to PA chases when you're on vacation?")

---

#### Gap 3: Front-Desk's Informal Clinical Triage [A5, A9]

**Documented**: "Review pre-visit questionnaire; document visit reason"

**Lived**: Front-desk staff make **implicit clinical judgments** when parsing patient-reported visit reasons [A5]. When a patient writes "chest pain," the front-desk needs to determine: Is this urgent (call physician now) or routine (scheduled cardiology follow-up)? When they write "feeling off," does that warrant escalation?

There is **no formal triage protocol** [A5]. Staff have learned through informal training — watching each other, getting corrected by Dana when they miss something, trial-and-error. Because the 4-person team rotates between two locations [A9], training is inconsistent. New hires learn by osmosis, not documentation.

**Real work**: Front-desk staff use pattern recognition based on:
- Patient's visit history ("this patient always says chest pain, they have stable angina")
- Appointment type (routine follow-up vs. new complaint vs. same-day request)
- Gut feeling about language urgency ("can't walk" vs. "some discomfort")

When uncertain, they escalate to Dana or flag the chart for physician review. But **where is the line between "administrative triage" (safe for front-desk) and "clinical triage" (requires nurse/physician)?** [A13] Dana hasn't explicitly defined it. Staff are making it up as they go.

**Why the gap exists**:
- Hard constraint: "No clinical judgment by the agent" [A13] implies front-desk shouldn't be making clinical judgments either, but **they are**
- Patient language is inherently ambiguous; structured questionnaires can't capture clinical urgency nuance
- Formalizing triage rules risks crossing into clinical territory (malpractice exposure [A15])

---

#### Gap 4: DoseSpot's Unknown Boundaries [A6]

**Documented**: "Reconcile medications using DoseSpot at check-in"

**Lived**: DoseSpot integration with athenahealth is reliable for **some** medication sources, but **not all** [A6]. The scenario states "DoseSpot misses things in real practice," but the artefacts don't specify what. Based on typical EHR integration gaps, likely misses include:
- Prescriptions filled at out-of-network pharmacies (patient traveling, using mail-order from different state)
- Over-the-counter medications and supplements (not tracked by pharmacy systems)
- Medication samples given by physicians (no pharmacy transaction)
- Prescriptions from other providers (specialists, urgent care, ER visits)

Front-desk staff **don't know what DoseSpot misses**, so they ask patients a generic "Are you taking any medications not listed here?" But patients:
- Forget to mention OTC meds ("that's not a real medication")
- Don't realize a new specialist prescribed something (it's not filled yet)
- Say "yes, same as before" without actually reviewing the list

**Real work**: Front-desk does a quick DoseSpot pull, asks patient "any changes?", documents patient's verbal response. If patient says "I stopped that blood pressure med," front-desk updates athenahealth. If patient says "no changes," front-desk moves on. **Discrepancies are discovered later** — often by the physician during the visit (Artefact 5.2 mentions "unreviewed medication change").

**Why the gap exists**:
- DoseSpot's integration scope is unclear [A6]; no one has explicitly mapped what it covers vs. what requires manual patient report
- Front-desk staff aren't trained pharmacists; they can't interpret fill dates, identify suspicious gaps, or probe for missing sources
- Patients are unreliable reporters of their own medication regimen

---

#### Gap 5: Post-Incident Learning Doesn't Scale [A11]

**Documented**: (No documented process for incorporating lessons learned)

**Lived**: When an intake miss occurs (visit abort, billing failure, unreviewed med change), the physician flags it in the chart (Artefact 5.2: Dr. Westbridge's note "please review with Dana"). Dana investigates, figures out what went wrong, **updates her mental model and maybe her Google Sheet** [A11]. But:
- She doesn't update practice SOPs (no formal SOP update process)
- She doesn't systematically train front-desk staff on the new pattern
- She doesn't build it into athenahealth workflows (no technical capability)

**Result**: Dana accumulates knowledge over 11 years, but it stays locked in her head and Google Sheet. Front-desk learns indirectly (when Dana corrects them). New hires start from scratch. **Institutional knowledge doesn't compound** [A11].

**Why the gap exists**: Small practice, limited resources, no dedicated operations/training role. Dana is both Practice Manager and de facto knowledge repository. No tools for systematizing tacit knowledge.

---

### Summary: The Cognitive Work Lives in the Exceptions

**What the SOPs describe**: Structured data flows through integrated systems (athenahealth → Availity → DoseSpot). Front-desk executes documented steps. Exceptions are rare.

**What actually happens**: 
- **70% of intake work is structured** and follows the documented process (successful Availity verifications, straightforward visit reasons, clean DoseSpot reconciliations)
- **30% of intake work is exception handling** [A1] that requires:
  - Dana's learned patterns (PA chase timing [A2], denial workarounds [A4], re-verification rules [A3])
  - Front-desk's informal judgment (visit triage [A5], patient language interpretation)
  - Manual reconciliation of system gaps (what DoseSpot misses [A6], what patients forget to mention)

**The cognitive work lives in the 30% exceptions** — interpreting Availity error codes, deciding when to chase a PA despite the stated SLA, distinguishing "chest pain" (urgent) from "chest pain" (routine), filling gaps in DoseSpot data. This is where **Dana's 11 years of institutional knowledge** [A2, A4] and **front-desk's pattern recognition** [A5] create value. It's also where the process breaks when Dana is unavailable [A11], front-desk is undertrained [A3, A9], or systems don't talk to each other [A6].

**This is what agents must address**: Not the structured 70% (already handled by athenahealth/Availity/DoseSpot APIs), but the **exception-handling 30%** where human judgment currently bridges system gaps, interprets ambiguity, and applies institutional knowledge that exists nowhere else.

---

## 5. Assumption Register (with Confidence Levels)

| # | Assumption | Confidence | Rationale | Impact if Wrong |
|---|------------|-----------|-----------|----------------|
| **A1** | 30% of insurance verifications fail auto-verify and require human interpretation | **MEDIUM** | Stated in scenario; aligns with typical Availity API failure rates for Medicaid managed care and lapsed policies | Under/overestimates exception volume; affects agent design and ROI |
| **A2** | Dana's insurer-specific PA chase timing patterns are stable over 6-12 month windows | **HIGH** ⬆️ | Coach validation: UHC changed 18 months ago; patterns stable but occasional policy changes; Dana tracks and adjusts | If insurers change SLAs frequently, Dana's Google Sheet becomes stale; agent can't rely on historical patterns |
| **A3** | Re-verification rule: >6mo + chronic patient (≥3 visits/year); plus sub-rules for Medicaid (every 3mo), Medicare Advantage (Q4), new insurance (next visit) | **VERY HIGH** ⬆️ | Validated explicitly via coach: >6mo + 3+ visits/year. Plus sub-rules: Medicaid every 3mo, Medicare Advantage in Q4, new insurance at next visit | If rule is more complex than validated, Wave 1 build time increases; if simpler, faster delivery |
| **A4** | PA denials follow learnable insurer-specific patterns (e.g., "Wellpath always denies colonoscopy first time") | **VERY HIGH** ⬆️ | Validated via coach: Wellpath colonoscopy 30-40 occurrences over 6 years, 100% consistent. "Standing rule in my head" | If denial reasons are actually unpredictable or policy-driven (not pattern-driven), agent can't learn shortcuts |
| **A5** | Visit reason triage by front-desk staff is inconsistent and relies on informal training | **HIGH** ⬆️ | Validated via coach: No written protocol; Dana trains verbally; keywords list provided (chest pain, SOB, severe, sudden, can't); false negative example (hypertensive crisis missed) | If formal triage rules exist (not provided in artefacts), less agent value in this JtD |
| **A6** | DoseSpot misses: (1) out-of-network pharmacies (10-15%), (2) other providers' prescriptions, (3) OTC meds, (4) supplements, (5) samples. Captures 70-80% of pharmacy fills, 0% of OTC/samples | **VERY HIGH** ⬆️⬆️ | Fully specified via coach: Dana estimates DoseSpot captures 70-80% of pharmacy fills, 0% of OTC/samples. Five categories of misses identified. | If DoseSpot is actually comprehensive, less agent value in reconciliation |
| **A7** | Dana's Google Sheet is the authoritative source for PA chase logic, not athenahealth or insurer portals | **VERY HIGH** ⬆️ | Confirmed via coach: Dana's personal tracking tool; front-desk doesn't use patterns from it; "living document" updated when patterns change | If insurer portals provide real-time status, Google Sheet is redundant; agent could query portals directly |
| **A8** | Physicians discover intake misses: 3 billing failures in Q4 from re-verification misses; "regular" medication/PA misses per month | **MEDIUM** ⬆️ | Validated via coach: 3 billing failures in Q4 from re-verification misses; unclear how many medication/PA misses per month, but "regular" per scenario | If miss rate is higher, greater urgency for automation; if lower, less ROI pressure |
| **A9** | Front-desk team rotates between two locations, creating knowledge fragmentation | **HIGH** ⬆️ | Confirmed via coach: 4-person team rotates between 2 locations; training doesn't stick; patterns locked in Dana's head | If rotation is rare, team knowledge is more stable; less need for systematization |
| **A10** | ~25 PAs/day is split unevenly by insurer (Medicaid managed care and UnitedHealthcare dominate volume) | **MEDIUM** | Not discussed in coach session; kept as stated in scenario | If PA volume is evenly distributed, insurer-specific pattern learning is less valuable |
| **A11** | Dana has no formal system for surfacing learned patterns to front-desk team beyond Google Sheet | **VERY HIGH** ⬆️ | Explicit via coach: "Patterns locked in my head"; front-desk doesn't know insurer-specific timing; no written SOPs for workarounds | If Dana has regular training sessions or documented SOPs, institutional knowledge is less concentrated in her |
| **A12** | athenahealth REST APIs support: (a) insurance verification status, (b) PA submission/status, (c) visit reason, (d) medication reconciliation | **HIGH** ⬆️ | Validated via coach: Dana mentions athenahealth subscription, Availity access, DoseSpot integrated; implies APIs exist (needs technical validation) | If APIs are limited or require custom development, tool integration cost is much higher |
| **A13** | Clinical judgment constraint: Front-desk can recognize keywords and escalate; cannot assess severity or decide disposition. "Recognition → escalate. Assessment → clinician." | **VERY HIGH** ⬆️ | Explicitly defined via coach: Front-desk can recognize keywords and escalate; cannot assess severity or decide disposition | If HIPAA permits broader access with audit, agent scope can expand (but risk increases) |
| **A14** | Dana's personal stake: Regional manager role in 5 years; success = replicable system for other practices; resume-building for operations leadership | **VERY HIGH** ⬆️⬆️⬆️ | Clarified via coach: Dana wants regional manager role in 5 years; success = replicable system that works for other practices | If Dana's goal is actually to reduce front-desk FTEs (cost-cutting), stakeholder alignment is different |
| **A15** | Malpractice insurance policy likely requires human review of all clinical flags; "AI can assist, but a human has to review and approve" | **MEDIUM** | Coach: Dana hasn't asked carrier yet, but expects human review required for anything clinical | If no malpractice constraints exist, agent can operate with less human oversight (higher autonomy) |

**Note**: Confidence levels updated post-coach role-play (2026-04-29). See `assumptions-update-post-coach.md` for detailed findings.

---

## 6. Delegation Archetype Assignment (Preliminary)

| JtD/Micro-Task | Archetype | Rationale |
|----------------|-----------|-----------|
| **Query Availity for insurance eligibility** | **Fully Agentic** | Structured API, deterministic, high volume (180/day), low risk for query itself |
| **Interpret Availity failure codes** | **Agent-led + Human Oversight** | Pattern-learnable (30% exception rate), but requires Dana's validation initially; escalation path for Medicaid managed care |
| **Determine re-verification timing** | **Agent-led + Human Oversight** | Tacit rule can be encoded (>6mo for chronic patients), but needs Dana to validate rule completeness |
| **Submit PA to insurer** | **Human-led + Automation Support** | Structured form-filling, but Dana currently owns relationships and knows insurer quirks; agent can prepare submission, Dana reviews/sends |
| **Determine when to chase PA** | **Agent-led + Human Oversight** | Insurer-specific patterns are learnable from Dana's Google Sheet; agent can recommend chase timing, Dana approves |
| **Interpret PA denial & resubmit** | **Human-led + Agent Support** | Agent can surface denial reason and suggest resubmission docs (e.g., "Wellpath colonoscopy: attach prior visit note"), Dana decides |
| **Parse visit reason from questionnaire** | **Fully Agentic** | NLP task, structured output (visit reason text), high volume (180/day) |
| **Determine if visit reason requires clinical escalation** | **Human Only** (initially) → **Agent-led + Human Oversight** (eventually) | CONSTRAINT: "clear human escalation path"; agent can flag potential urgency, Dana/physician makes final call; over time, agent learns escalation patterns |
| **Pull DoseSpot pharmacy history** | **Fully Agentic** | Structured API, deterministic |
| **Identify med list discrepancies** | **Agent-led + Human Oversight** | Pattern-learnable (DoseSpot vs. athenahealth vs. patient report), but requires physician review for clinical significance |
| **Flag allergy conflicts** | **Fully Agentic** | Rule-based, deterministic, high-consequence (must be 100% reliable) |

---

## 7. Key Cognitive Hotspots (Where Agents Create Disproportionate Value or Risk)

### Hotspot 1: Dana's Institutional Knowledge (PA Chase Timing & Denial Patterns)
**Where**: JtD-2 (Prior Authorization Management), Zone 3  
**Why it matters**: Dana has accumulated 11 years of insurer-specific pattern knowledge [A2, A4] that is:
- Not documented in athenahealth, Availity, or practice SOPs [A11]
- Not consistently shared with front-desk team (only via Google Sheet [A7])
- Critical for avoiding visit aborts and patient frustration (see Artefact 5.2: patient TJ's second visit abort)

**Value if delegated**: 
- Systematize Dana's knowledge → make it **available to all front-desk staff and future hires**
- Proactive PA chase timing → reduce visit aborts from ~3/quarter to near-zero
- Dana's time reclaimed from manual Google Sheet tracking (~1-2 hours/day) → focus on higher-value clinical operations

**Risk if delegated badly**: 
- Agent chases too early (wastes Dana's time on premature follow-up) or too late (visit abort, patient frustration)
- Agent applies wrong insurer pattern (e.g., treats Humana like Aetna [A2]) → operational failure
- Agent doesn't adapt when insurer changes SLA policy [A2] → stale knowledge

**Delegation design**: **Agent-led + Dana Oversight** during learning phase (3-6 months); **Fully Agentic** once patterns validated [A2]
- Agent ingests Dana's Google Sheet [A7] as training data
- Agent recommends chase timing; Dana approves/corrects
- Agent learns from Dana's corrections (reinforcement loop)
- Over time, Dana spot-checks rather than approves every case

---

### Hotspot 2: Insurance Re-Verification Rule Gap
**Where**: JtD-1 (Insurance Verification), Zone 2  
**Why it matters**: 
- Artefact 5.3 shows billing failure from stale verification (>6 months old, chronic patient)
- Front-desk team doesn't consistently apply Dana's tacit re-verification rule [A3]
- Cost: patient receives surprise $340 bill, 12 minutes of front-desk time to resolve, Aetna claim refile

**Value if delegated**: 
- Agent enforces re-verification rule automatically (>6 months, chronic patient, stable insurance) [A3]
- Prevents billing failures → reduces patient complaints and administrative rework
- Estimated volume: ~30-50 patients/month at risk [A10]: ~30% of 180 daily patients are chronic with stable insurance

**Risk if delegated badly**: 
- Agent over-verifies (queries Availity for every patient, even if verified yesterday) → API cost spike, front-desk time wasted
- Agent under-verifies (misses edge cases Dana knows: e.g., certain insurers require monthly verification for certain conditions [A3]) → billing failures continue

**Delegation design**: **Fully Agentic** with explicit rule encoding [A3]
- Agent checks last verification date in athenahealth [A12]
- If >6 months AND patient has ≥3 visits in past year (proxy for "chronic patient"), auto-trigger re-verification
- Dana validates rule logic in pilot phase (1 month)

---

### Hotspot 3: Visit Reason Triage (Clinical Boundary Enforcement)
**Where**: JtD-3 (Visit Reason Triage), Zone 4  
**Why it matters**: 
- CONSTRAINT: "No clinical judgment by the agent" [A13]
- CONSTRAINT: "Clear human escalation path for visit reason"
- Front-desk staff currently make implicit clinical judgments (informal training [A5])
- Risk: Agent either (a) misses urgent symptom → patient harm, or (b) over-escalates → Dana/physician alert fatigue

**Value if delegated**: 
- Standardize triage logic across 4-person team (currently inconsistent due to rotation [A9], training gaps [A5])
- Flag ambiguous cases for Dana/physician review → reduce informal clinical judgment by front-desk
- Free up physician time from non-urgent "just in case" escalations

**Risk if delegated badly**: 
- Agent makes clinical judgment (e.g., "chest pain + age 60 = cardiac, escalate immediately") → violates constraint [A13], malpractice risk [A15]
- Agent escalates everything ("chest pain" → always escalate) → alert fatigue, Dana ignores flags
- Agent misses true urgency (e.g., patient writes "feeling off" but means "chest pain") → patient harm

**Delegation design**: **Agent-led + Human Oversight** with bright-line rules
- Agent flags: (a) symptom keywords (chest pain, shortness of breath, bleeding, severe pain), (b) visit type mismatch (routine visit, but patient describes acute symptom), (c) ambiguous language ("not feeling well" without specifics)
- Agent does NOT assess severity or urgency — only surfaces cases requiring human review
- Dana/physician reviews all flagged cases before visit
- Over time, collect physician feedback on false positives/negatives → refine keyword list

---

### Hotspot 4: Medication Reconciliation (DoseSpot Integration Gaps)
**Where**: JtD-4 (Medication Reconciliation), Zone 5  
**Why it matters**: 
- Scenario states "DoseSpot misses things in real practice" [A6] — but artefacts don't specify what
- Physicians discover unreviewed medication changes at visit time (mentioned in brief [A8])
- Risk: Drug interactions, allergy conflicts, dosage errors

**Value if delegated**: 
- Agent identifies discrepancies between athenahealth, DoseSpot, and patient verbal report
- Agent flags: (a) new meds not in athenahealth, (b) discontinued meds still listed, (c) dosage changes, (d) OTC/supplements mentioned by patient [A6]
- Physician reviews flagged discrepancies before visit → reduces in-visit surprises

**Risk if delegated badly**: 
- Agent misinterprets patient verbal report (e.g., patient says "I stopped the blood pressure med" but means "I ran out, need refill")
- Agent misses DoseSpot integration gaps [A6] (e.g., fills from out-of-network pharmacies, samples from physician offices)
- Agent introduces new discrepancies by overwriting athenahealth with incorrect DoseSpot data

**Delegation design**: **Agent-led + Human Oversight** (physician must review before visit)
- Agent compares athenahealth med list [A12], DoseSpot fill history (past 6 months), and patient questionnaire response
- Agent flags discrepancies; does NOT auto-update athenahealth
- Physician reviews flagged list at visit start (30 seconds vs. 6 minutes of front-desk time)

**CRITICAL ELICITATION NEEDED**: What does DoseSpot actually miss [A6]? (out-of-network pharmacies? OTC meds? physician samples? other providers' prescriptions?)

---

## 8. Design-Changing Questions for Coach Role-Play (Dana Velazquez)

### Category A: Prior Authorization Chase Logic (Hotspot 1)

**Q1**: "Walk me through the last PA denial you handled. What was the insurer, what reason did they give, and what did you do to resolve it? How did you know to do that?"  
→ **Why this matters**: Tests whether Dana's denial response patterns are truly learnable or ad-hoc. If she says "I just called the insurer and figured it out," patterns are weaker than artefacts suggest.

**Q2**: "Your Google Sheet shows 'Wellpath always denies colonoscopy first time — needs prior visit note.' How did you discover that pattern? How many times did it happen before you realized it was consistent?"  
→ **Why this matters**: Validates pattern stability [A4] and Dana's confidence. If it's only happened twice, it's not a robust pattern. If it's 20+ times, agent can rely on it.

**Q3**: "Has an insurer ever changed their PA SLA or approval process in the last two years? How did you find out, and how long did it take you to adjust your chase timing?"  
→ **Why this matters**: Tests pattern decay rate [A2]. If insurers change policies quarterly, Dana's Google Sheet is constantly stale → agent needs real-time learning, not historical data.

**Q4**: "If you were on vacation for two weeks, what would happen to PA chases? Would the front-desk team handle them, or would they wait for you?"  
→ **Why this matters**: Reveals whether Dana's knowledge is actually transferable [A11] or if it's locked in her head. If front-desk waits, knowledge transfer is critical path for agent design.

**Q5**: "Which insurers are the most unpredictable for PA timing? Are there any where you just can't predict when they'll respond?"  
→ **Why this matters**: Identifies where agent will struggle [A2]. If Aetna is "unpredictable" (see Artefact 5.1: "Aetna fast this month, unusual"), agent may need to escalate those cases to Dana rather than recommend timing.

---

### Category B: Insurance Re-Verification Rules (Hotspot 2)

**Q6**: "The patient billing issue in October (TJ, $340 self-pay bill) — you said that's the third time this has happened. What do those three cases have in common? Same patient type, same insurer, same time gap?"  
→ **Why this matters**: Tests whether re-verification miss is systemic [A3] (learnable rule) or random (human error). If all three are >6 months + chronic patients, rule is clear. If they're unrelated, harder to prevent.

**Q7**: "Does Availity tell you when a patient's insurance is about to expire, or do you only find out when you try to verify and it fails?"  
→ **Why this matters**: If Availity provides proactive alerts [A12], agent can use those. If not, agent needs to infer from last verification date and patient history.

**Q8**: "Are there any patient populations where you always re-verify, even if it's been less than 6 months? For example, Medicaid patients, self-pay who recently got insurance, etc.?"  
→ **Why this matters**: Tests for edge cases beyond the >6 month rule [A3]. If Dana has sub-rules (e.g., "always re-verify Medicaid every 3 months because eligibility changes"), agent needs those encoded.

**Q9**: "When the front-desk team does re-verify, do they document why they did it in athenahealth? Or is it just 'verified on [date]' with no context?"  
→ **Why this matters**: If no context is logged, agent can't learn from front-desk actions. Logging "re-verified due to >6mo rule" creates training data.

---

### Category C: Visit Reason Triage (Hotspot 3)

**Q10**: "Can you give me an example of a visit reason that the front desk flagged as urgent, but turned out to be routine? And vice versa — something they marked routine that should have been escalated?"  
→ **Why this matters**: Calibrates false positive vs. false negative tolerance. If Dana says "I'd rather they over-escalate than miss something," agent design should favor sensitivity over specificity.

**Q11**: "What keywords or phrases in a patient's visit reason automatically make you think 'I need to tell the doctor before this visit'?"  
→ **Why this matters**: Directly elicits triage rules. If Dana lists specific terms (chest pain, bleeding, sudden onset, etc.), those become agent's escalation triggers.

**Q12**: "Has there ever been a visit where the patient's stated reason was completely different from what they actually needed? How did the front desk handle that?"  
→ **Why this matters**: Tests robustness of pre-visit triage. If patients often change their story at check-in, pre-visit agent triage is less valuable (need day-of triage instead).

**Q13**: "What does 'no clinical judgment' mean to you in practice? Where's the line between administrative triage and clinical triage?"  
→ **Why this matters**: Clarifies the hard constraint [A13]. If Dana's definition is fuzzy ("just use common sense"), agent needs very conservative escalation rules. If she has bright-line criteria, agent can be more autonomous.

---

### Category D: Medication Reconciliation (Hotspot 4)

**Q14**: "You mentioned DoseSpot misses things. What are the most common medication sources that DoseSpot doesn't capture? Other providers' prescriptions, OTC meds, supplements, something else?"  
→ **Why this matters**: Directly addresses [A6]. If DoseSpot misses out-of-network pharmacies, agent needs to prompt patient for "any meds filled elsewhere?" If it misses OTC, agent needs to ask about Tylenol, vitamins, etc.

**Q15**: "When a patient says 'I'm on the same medications as last time,' how often is that actually true vs. they forgot something changed?"  
→ **Why this matters**: Tests reliability of patient self-report. If patients are generally accurate, agent can trust their input. If not, agent needs to probe more ("Are you sure? DoseSpot shows a new prescription for...").

**Q16**: "Have there been cases where a medication discrepancy led to a clinical issue — like the doctor prescribed something that interacted with a med we didn't know about?"  
→ **Why this matters**: Establishes risk severity. If this has happened (or almost happened), medication reconciliation is high-priority for agent. If it's mostly administrative annoyance, lower priority.

**Q17**: "Does DoseSpot show medication fills from other states or other providers? Or only from pharmacies your practice typically uses?"  
→ **Why this matters**: Tests DoseSpot integration scope [A6]. If it's a narrow pharmacy network, agent needs to explicitly ask patients about other sources.

---

### Category E: Stakeholder Priorities & Constraints (Elicitation Targets from Scenario Prompt)

**Q18**: "What's your biggest frustration with the current intake process? If you could wave a magic wand and fix one thing, what would it be?"  
→ **Why this matters**: Reveals Dana's actual priority. If she says "PA chases," that's the primary agent target. If she says "front-desk makes too many mistakes," that's a different design (agent as QA layer).

**Q19**: "The senior physician asked you to 'look at this AI thing.' What do you think they're expecting? Fewer intake misses, cost savings, something else?"  
→ **Why this matters**: Aligns stakeholder expectations [A8]. If physician wants zero intake misses (unrealistic), need to reset expectations. If they want "better than current state," more achievable.

**Q20**: "Have you talked to your malpractice insurance carrier about using AI for intake? Do they have any requirements like 'a human must review every AI decision' or anything like that?"  
→ **Why this matters**: Directly addresses [A15]. If malpractice policy requires human review, agent must be **Agent-led + Human Oversight** (can't be Fully Agentic). If no constraints, broader design freedom.

**Q21**: "What patient populations don't fit the standard intake flow? For example, non-English speakers, patients without portal access, patients who always call instead of filling out forms?"  
→ **Why this matters**: Tests universality of agent design. If 20% of patients are "special cases," agent needs explicit handling for those (e.g., phone intake transcription, multilingual support).

**Q22**: "What's your role in 5 years? Are you planning to stay as Practice Manager, or move into a different role? What would success in this AI project mean for your career?"  
→ **Why this matters**: Directly addresses [A14] (Dana's personal stake). If she's grooming for a regional manager role, she wants a scalable solution (agent that works for multiple practices). If she's staying, she wants operational relief for her team.

**Q23**: "If this AI project works, what happens to the front-desk team? Are you expecting to reduce headcount, or redeploy them to other tasks?"  
→ **Why this matters**: Tests change management risk. If Dana says "we're understaffed, this will let us handle more patients with same team," low resistance. If she says "we'll probably let someone go," high resistance from front-desk.

**Q24**: "What's the practice's budget for new software or technology? Is there an annual IT spend, or would this need special approval?"  
→ **Why this matters**: Economic feasibility. If practice has zero IT budget beyond athenahealth subscription, need low-cost solution (token economics must be < $0.50/patient/day = ~$2,700/month for 180 patients/day [A10]).

---

## 9. Summary: Where Agents Win vs. Where Humans Must Stay

### Strong Agent Candidates (High Volume, Learnable Patterns, Low Clinical Risk)
1. **Insurance verification via Availity** (180/day, structured API, automatable except 30% exceptions)
2. **PA chase timing recommendations** (25/day, insurer-specific patterns, Dana's institutional knowledge is capturable)
3. **Re-verification rule enforcement** (30-50/month, clear rule: >6mo + chronic patient, prevents billing failures)
4. **Visit reason parsing** (180/day, NLP task, structured output)
5. **Medication discrepancy flagging** (180/day, cross-system reconciliation, physician reviews before visit)

### Human-Must-Stay (Clinical Judgment, High Consequence, Low Determinism)
1. **Visit reason clinical urgency assessment** (until bright-line triage rules validated by physician)
2. **PA denial negotiation with insurers** (relationship-dependent, unstructured phone calls)
3. **Final medication reconciliation decision** (physician must approve before prescribing)

### Hybrid (Agent Support, Human Decision)
1. **PA resubmission with additional docs** (agent suggests "attach prior visit note for Wellpath colonoscopy," Dana reviews/sends)
2. **Availity failure code interpretation** (agent learns patterns from Dana's corrections, escalates Medicaid managed care)

---

## 10. Next Steps for FDE (You)

**Post-Coach Update (2026-04-29)**: All 24 questions answered via coach role-play (see `coach-roleplay-answers.md`). Assumptions validated and confidence levels updated (see `assumptions-update-post-coach.md`).

### Wave Sequencing Update (Based on Coach Validation)

**CRITICAL FINDING from Q18**: Dana's #1 frustration is **PA timing misses that lead to visit aborts**, not insurance billing failures. This changes wave priority:

**REVISED Wave 1 (Start immediately): PA Chase Timing (JtD-2)**
- Dana explicitly said: "If I could fix one thing, it would be proactive PA chase timing that never misses a deadline"
- Prevents visit aborts (Artefact 5.2: patient TJ's frustration, Dr. Westbridge's complaint)
- Captures Dana's 11 years of institutional knowledge [A2, A4, A7] before she moves to regional role [A14]
- **Timeline**: 8-11 months (2 months build + 3-6 months learning phase)
- **Economics**: $20,897/year saving (Dana's time validated at 1-2 hours/day [Q18]) + visit abort prevention
- **Build cost**: $36,000
- **Payback**: 20.6 months (strategic justification: institutional knowledge capture)

**REVISED Wave 2: Insurance Re-Verification (JtD-1)**
- High ROI (171%), fast payback (4.4 months)
- Builds athenahealth + Availity integrations → reused in Wave 3
- **Wave 1 PA chase** doesn't build reusable integrations (Google Sheet is unique to JtD-2)
- Wave 2 can start while Wave 1 is in learning phase (6-month overlap)
- **Timeline**: 4 months
- **Economics**: $108,264/year saving, $40,000 build cost

**Wave 3: Medication Reconciliation (JtD-4)**
- Highest ROI (1,758%), fastest payback (0.6 months)
- Reuses athenahealth integration from Wave 2
- DoseSpot gaps now fully specified [A6] → agent prompts finalized
- **Timeline**: 4 months (starts Month 13, after Waves 1-2 complete)
- **Economics**: $557,464/year saving, $30,000 build cost

**Wave 4 (Optional, Deferred): Visit Reason Triage (JtD-3)**
- Clinical constraint [A13] validated: "Recognition → escalate. Assessment → clinician."
- Malpractice likely requires human review [A15]
- Prerequisites: Malpractice carrier approval, Waves 1-3 governance validated

### Immediate Next Steps for Implementation

1. ✅ **Assumptions validated** via coach role-play (completed)
2. ⏳ **Ingest Dana's Google Sheet** (Artefact 5.1 + full historical data)
3. ⏳ **Extract insurer-specific patterns** from Google Sheet:
   - Humana: 6 days (always, never 5)
   - UnitedHealthcare Choice: 7 days
   - Wellpath: 7 days + always denies colonoscopy first time (attach prior visit note preemptively)
   - Medicare: 4-5 days
   - BCBS PPO: 3 days
   - Aetna: Unpredictable (escalate to Dana)
4. ⏳ **Build Wave 1 agent architecture** (PA Chase Timing):
   - athenahealth API: Read PA submission date, status, procedure type
   - Agent logic: Calculate chase timing based on insurer + submission date + Dana's learned SLA
   - Output: "Chase now" / "Wait X days" / "Escalate to Dana" (Aetna)
5. ⏳ **Learning phase (3-6 months)**: Dana approves all chase recommendations, agent learns from corrections
6. ⏳ **Production transition**: Agent handles predictable insurers autonomously, Dana spot-checks Aetna + reviews denials

**Success criteria** (Wave 1):
- Zero visit aborts from PA timing misses (currently ~1/month)
- Dana's time reduced from 1.5-2 hours/day to ~15 min spot-checking
- Agent learns 15+ insurer-specific patterns from Dana's Google Sheet + corrections

---

**End of Cognitive Map**
