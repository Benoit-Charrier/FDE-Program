# Phase 3: Delegation Qualification — Westbridge Family Medicine Patient Intake

**Date**: 2026-04-28  
**Based on**: `scenario5-cognitive-map.md` (Iteration 001.1)  
**Methodology**: ATX Assessment Phase 3 (atx-assessment.md)

---

## Executive Summary

This document scores each Job to be Done (JtD) from the cognitive map across 7 delegation suitability dimensions, assigns delegation archetypes, and identifies which tasks are suitable for agentic automation vs. those requiring human judgment.

**Key Finding**: 2 of 4 JtDs are strong agentic candidates (insurance verification, PA chase timing), 1 requires hybrid approach (medication reconciliation), and 1 must remain human-led with conservative agent support (visit reason triage) due to clinical judgment constraint.

---

## Table of Contents

1. [Delegation Suitability Matrix](#delegation-suitability-matrix)
   - [JtD-1: Verify Insurance Eligibility for Scheduled Visit](#jtd-1-verify-insurance-eligibility-for-scheduled-visit)
   - [JtD-2: Determine Prior Authorization Status and Chase Pending PAs](#jtd-2-determine-prior-authorization-status-and-chase-pending-pas)
   - [JtD-3: Triage Patient Visit Reason and Flag Clinical Urgency](#jtd-3-triage-patient-visit-reason-and-flag-clinical-urgency)
   - [JtD-4: Reconcile Medications and Flag Allergy Alerts](#jtd-4-reconcile-medications-and-flag-allergy-alerts)
2. [Delegation Archetype Summary](#delegation-archetype-summary)
3. [Anti-Pattern Analysis: Could Any of These Be Rules/RPA Instead?](#anti-pattern-analysis-could-any-of-these-be-rulesrpa-instead)
4. [Critical Dependencies for Delegation Design](#critical-dependencies-for-delegation-design)
5. [Recommended Delegation Sequencing (Waves)](#recommended-delegation-sequencing-waves)
   - [Wave 1: High Suitability, Clear Rules (Quick Wins)](#wave-1-high-suitability-clear-rules-quick-wins)
   - [Wave 2: High Value, Institutional Knowledge Capture (Strategic)](#wave-2-high-value-institutional-knowledge-capture-strategic)
   - [Wave 3: High Volume, Human Backstop (Moderate Complexity)](#wave-3-high-volume-human-backstop-moderate-complexity)
   - [Wave 4 (Optional): High Risk, Conservative Design (Long-term)](#wave-4-optional-high-risk-conservative-design-long-term)
6. [Output Artifacts (Phase 3 Complete)](#output-artifacts-phase-3-complete)
7. [Next Steps (Proceeding to Phase 4)](#next-steps-proceeding-to-phase-4)

---

## Delegation Suitability Matrix

### JtD-1: Verify Insurance Eligibility for Scheduled Visit

| Dimension | Score | Rationale | Evidence |
|-----------|-------|-----------|----------|
| **Input structure** | **HIGH** | Patient ID, insurance info, appointment date all in athenahealth (structured). Availity API accepts structured queries. | Scenario states athenahealth has REST APIs [A12]; Availity is separate REST-API tool |
| **Decision determinism** | **MEDIUM** | 70% of verifications succeed automatically (deterministic API call). 30% require interpretation of error codes and application of Dana's tacit re-verification rule [A1, A3]. | Artefact 5.3 shows billing failure from missed re-verification rule; rule is clear once encoded (>6 months + chronic patient) |
| **Tool coverage** | **HIGH** | athenahealth API for patient data, Availity API for eligibility checks. Both REST APIs available [A12]. | Scenario explicitly states "REST APIs" for athenahealth; Availity is standard in healthcare |
| **Context complexity** | **MEDIUM** | Dana has tacit re-verification rule [A3]: >6 months for chronic patients on stable insurance. Once encoded, context is explicit. Front-desk doesn't consistently apply it, causing failures. | Artefact 5.3: "Patient verification refresh window > 6 months caused billing miss... Dana said this is the third time" [A3] |
| **Exception rate** | **MEDIUM** | 30% fail auto-verify [A1], requiring human interpretation. Medicaid managed care especially complex. | Cognitive map states "~30% fail auto-verify" based on typical Availity rates for complex insurance |
| **Latency constraint** | **HIGH** (low constraint) | Verification happens 1-7 days before visit. Batch processing acceptable. No real-time requirement. | Cognitive map JtD-1 trigger: "Patient scheduled appointment (typically 1-7 days before visit)" |
| **Risk/compliance** | **MEDIUM** | Billing impact if wrong (patient gets surprise bill), but reversible via claim refile. HIPAA-compliant (administrative data only). No clinical risk. | Artefact 5.3: Patient received $340 surprise bill, took 12 min to resolve. Reversible but painful. |

**Suitability Summary**: 4 High, 3 Medium, 0 Low  
**Archetype**: **Agent-led + Human Oversight** (initially) → **Fully Agentic** (once re-verification rule validated)

**Rationale**:
- High volume (180/day), structured inputs, deterministic API calls → strong agentic candidate
- 30% exception rate [A1] requires agent to learn error code patterns (not pure rules)
- Dana's re-verification rule [A3] needs validation and encoding, then can be fully automated
- Initial phase: agent flags re-verification cases for Dana review; learns from corrections
- Production phase: agent auto-triggers re-verification for >6 month + chronic patient cases

**Anti-pattern check**: ✅ PASS — 30% exception rate requires pattern recognition, not static rules. Re-verification logic has conditional complexity (chronic patient identification). Agent justified.

---

### JtD-2: Determine Prior Authorization Status and Chase Pending PAs

| Dimension | Score | Rationale | Evidence |
|-----------|-------|-----------|----------|
| **Input structure** | **MEDIUM** | PA submission data in athenahealth (structured), but Dana's chase timing patterns live in Google Sheet and her head [A7]. Insurer portal responses vary (semi-structured). | Artefact 5.1: Dana's Google Sheet tracks submission date, insurer, status, target chase date. Not in athenahealth. |
| **Decision determinism** | **LOW** | Chase timing is insurer-specific and learned through 11 years of pattern observation [A2]. "Stated SLA (5 days) ≠ Lived SLA (Humana: always 6d, UHC: 6-7d, Aetna: unpredictable)". Denial response patterns vary by insurer [A4]. | Artefact 5.1: "Humana always exactly 6 days; never 5", "Wellpath always denies colonoscopy first time — needs prior visit note" [A4]. This is institutional knowledge, not documented rules. |
| **Tool coverage** | **MEDIUM** | athenahealth API for PA submission/status [A12]. Insurer portals vary (some have APIs, some are web-only). Dana's Google Sheet [A7] provides historical pattern data for training. | Scenario states athenahealth has REST APIs; insurer portals are fragmented (not standardized) |
| **Context complexity** | **HIGH** (requires institutional knowledge) | Dana's patterns are pure institutional knowledge [A2, A4] — not in athenahealth, Availity, or SOPs [A11]. Example: "Wellpath colonoscopy denial — attach prior visit note" is learned workaround preventing multi-week delays. | Artefact 5.1 footer: "Wellpath colonoscopy denial pattern — they want the prior visit note attached, never says so on the form. Standing rule: include with submission, save the resubmit cycle." |
| **Exception rate** | **MEDIUM** | ~40% of PAs denied or delayed beyond stated SLA (inferred from Artefact 5.1: 3 of 5 samples show deviations from standard SLA or denials). Each insurer has unique patterns. | Artefact 5.1: 3 of 5 PAs show non-standard handling (Wellpath denial, UHC delayed, Aetna fast/unpredictable) |
| **Latency constraint** | **HIGH** (low constraint) | PAs submitted 5-7 days before procedure. Chase timing is days, not hours. Async acceptable. | Cognitive map JtD-2: "Scheduled procedure/imaging/referral visit approaching (typically 5-7 days before)" |
| **Risk/compliance** | **HIGH** (high consequence, but reversible) | PA miss causes visit abort, patient frustration, physician complaint (Artefact 5.2: patient TJ's second visit abort). But recoverable via rescheduling. No patient harm, but operational failure. | Artefact 5.2: "Visit aborted at exam-room check; rescheduled for 04.11... Patient frustrated — 'this is the second time this has happened to me.'" Senior physician asked Dana to address. |

**Suitability Summary**: 2 High, 3 Medium, 1 Low (Decision determinism), 1 High-consequence (Risk)  
**Archetype**: **Agent-led + Human Oversight** (learning phase, 3-6 months) → **Fully Agentic** (production, once patterns validated and stable)

**Rationale**:
- **Highest-value unlock**: Dana's 11 years of insurer-specific patterns [A2, A4] not systematized. Single point of failure.
- Decision determinism is LOW because patterns are learned, not rule-based — but this is exactly where agents add value (pattern learning from historical data + Dana's corrections)
- Context complexity is HIGH (institutional knowledge locked in Dana's head [A11]), but capturable: Dana's Google Sheet [A7] provides training data; agent learns from her corrections
- Volume is moderate (~25/day), but operational impact is high (visit aborts directly motivated senior physician to request AI solution)
- **Learning phase design**: Agent ingests Dana's Google Sheet, recommends chase timing, Dana approves/corrects. Agent learns insurer-specific patterns through reinforcement.
- **Production phase design**: Agent auto-recommends chase timing; Dana spot-checks high-stakes cases (e.g., Aetna unpredictable insurers). Agent flags when insurer behavior deviates from learned pattern (e.g., Humana suddenly approves in 5 days instead of 6).

**Anti-pattern check**: ✅ PASS — Cannot be solved with static rules (each insurer has unique, learned patterns). Cannot be RPA (requires reasoning about timing, denial patterns, historical behavior). Agent justified for pattern learning + institutional knowledge capture.

---

### JtD-3: Triage Patient Visit Reason and Flag Clinical Urgency

| Dimension | Score | Rationale | Evidence |
|-----------|-------|-----------|----------|
| **Input structure** | **MEDIUM** | Visit reason from questionnaire: mix of free text and structured fields. Patient writes "knee pain" or "knee pain, can't walk, started suddenly" — requires NLP interpretation. | Cognitive map Zone 4: "Parse questionnaire (text + structured)" — semi-structured patient input |
| **Decision determinism** | **LOW** | Distinguishing "routine" from "urgent" without making clinical judgment is inherently fuzzy [A5]. Hard constraint [A13]: "No clinical judgment by the agent". Front-desk currently uses informal training [A5], inconsistent across 4-person team [A9]. | Scenario constraint: "No clinical judgment by the agent" [A13]. Cognitive map: "This is INFORMAL TRAINING (inconsistent across 4-person team [A5, A9])" |
| **Tool coverage** | **HIGH** | athenahealth API for visit reason, patient history [A12]. Data is accessible. | Scenario states athenahealth has REST APIs [A12] |
| **Context complexity** | **HIGH** (clinical boundary is fuzzy) | Where is the line between "administrative triage" (agent-safe) and "clinical triage" (human-only)? Dana's definition unknown [Q13]. Front-desk makes implicit clinical judgments today [A5]. | Cognitive map Hotspot 3: "Front-desk staff currently make implicit clinical judgments (informal training [A5])" + Q13: "What does 'no clinical judgment' mean to you in practice?" |
| **Exception rate** | **HIGH** | Patient language is ambiguous. "Feeling off" might mean "chest pain". "Knee pain" might be urgent trauma or routine follow-up. Every visit reason requires judgment call about escalation. | Cognitive map: "patient writes 'feeling off' but means 'chest pain'" — high ambiguity in patient self-reporting |
| **Latency constraint** | **MEDIUM** | Questionnaire completed 1-2 days before visit or day-of. Some urgency (same-day conversion), but not real-time. | Cognitive map JtD-3: "Pre-visit questionnaire completion (day of visit or 1-2 days prior)" |
| **Risk/compliance** | **VERY HIGH** (patient safety) | Missing urgent symptom → patient harm. Over-escalating → alert fatigue, Dana/physician ignores flags (also risky). Malpractice insurance may require human review [A15]. | Cognitive map Hotspot 3: "Agent either (a) misses urgent symptom → patient harm, or (b) over-escalates → Dana/physician alert fatigue" + [A15]: malpractice constraints unknown |

**Suitability Summary**: 2 High, 2 Medium, 2 Low (Decision determinism, Context complexity), 1 Very High risk  
**Archetype**: **Human-led + Agent Support** (conservative design; agent flags ambiguity, human decides)

**Rationale**:
- **Clinical boundary constraint [A13] is hard blocker**: Agent cannot make clinical judgments. This is non-negotiable per scenario.
- Decision determinism is LOW because "routine vs. urgent" is judgment-dependent, and Dana's definition of the boundary is unclear [Q13]
- Risk is VERY HIGH: patient safety + malpractice exposure [A15]
- **Conservative design required**: Agent parses visit reason (NLP), flags keyword-based urgency triggers (chest pain, bleeding, sudden onset, severe pain), and **always escalates ambiguous cases** to Dana/physician
- Agent does NOT assess severity or make urgency decisions — only surfaces cases requiring human review
- Over time, agent learns from physician feedback on false positives/negatives, but **human always makes final call**
- **Value**: Standardizes triage logic across 4-person front-desk team (currently inconsistent [A9]); reduces informal clinical judgments by front-desk

**Anti-pattern check**: ⚠️ CAUTION — Could this be keyword list + escalation rules (not an agent)? Possibly, but:
- Patient language is highly variable (NLP required, not keyword matching)
- Escalation logic needs to learn from physician feedback (reduce false positives without increasing false negatives)
- Agent provides value in adapting to practice's specific escalation patterns over time
- **Verdict**: Agent justified IF designed conservatively with human-in-loop for all ambiguous cases. Not for full autonomy.

---

### JtD-4: Reconcile Medications and Flag Allergy Alerts

| Dimension | Score | Rationale | Evidence |
|-----------|-------|-----------|----------|
| **Input structure** | **MEDIUM** | athenahealth med list (structured), DoseSpot pharmacy history (structured), patient verbal report (unstructured). Three data sources must be reconciled. | Cognitive map: "athenahealth list + DoseSpot list + patient verbal" — mix of structured and unstructured |
| **Decision determinism** | **MEDIUM** | Identifying discrepancies is partly deterministic (list comparison), but interpreting discrepancies requires judgment. Patient says "I stopped that" — does it mean discontinued or ran out? DoseSpot misses things [A6] (scope unknown). | Cognitive map Hotspot 4: "Agent misinterprets patient verbal report (e.g., patient says 'I stopped the blood pressure med' but means 'I ran out, need refill')" |
| **Tool coverage** | **HIGH** | athenahealth API [A12], DoseSpot integrated with athenahealth (structured API). Patient verbal report via questionnaire. | Scenario: "DoseSpot (pharmacy / medication reconciliation, integrated with athenahealth)" + athenahealth REST APIs [A12] |
| **Context complexity** | **HIGH** (unknown DoseSpot gaps) | Scenario states "DoseSpot misses things in real practice" [A6], but artefacts don't specify what. Likely: out-of-network pharmacies, OTC meds, physician samples, other providers' prescriptions. Until [A6] validated, scope is unclear. | Cognitive map Hotspot 4: "What does DoseSpot actually miss [A6]? (out-of-network pharmacies? OTC meds? physician samples? other providers' prescriptions?)" — CRITICAL ELICITATION NEEDED |
| **Exception rate** | **MEDIUM** | Physicians "regularly discover" unreviewed medication changes at visit time [A8] (frequency unknown). Suggests exceptions are common, but not quantified. | Scenario brief: "Physicians regularly discover at the visit that something was missed in intake — most commonly an expired prior auth or an unreviewed medication change." [A8] frequency unknown |
| **Latency constraint** | **HIGH** (low constraint) | Reconciliation happens at patient check-in (day of visit). Takes ~6 minutes/case currently. Batch acceptable; physician reviews before exam. | Cognitive map JtD-4: "Patient check-in (day of visit)" — not time-critical |
| **Risk/compliance** | **HIGH** (patient safety, but with backstop) | Drug interactions, allergy conflicts, dosage errors → patient harm. BUT: Physician reviews before prescribing (human backstop). Agent flags discrepancies; does NOT auto-update athenahealth. | Cognitive map: "Physician reviews flagged discrepancies before visit → reduces in-visit surprises" + "Agent flags discrepancies; does NOT auto-update athenahealth" |

**Suitability Summary**: 3 High, 3 Medium, 0 Low, 1 High risk (but with human backstop)  
**Archetype**: **Agent-led + Human Oversight** (physician reviews flagged discrepancies before visit)

**Rationale**:
- Agent compares three data sources (athenahealth, DoseSpot, patient questionnaire), flags discrepancies for physician review
- **Does NOT auto-update** athenahealth med list (risk mitigation: physician makes final decision)
- Agent flags: (a) new meds not in athenahealth, (b) discontinued meds still listed, (c) dosage changes, (d) DoseSpot fills patient didn't mention, (e) patient-reported OTC/supplements not captured [A6]
- Allergy conflict flagging is deterministic (rule-based, high-consequence) → can be Fully Agentic for this sub-task
- **Value**: Reduces physician time from 6 minutes of manual reconciliation to 30 seconds of reviewing flagged list. Front-desk time freed up for other tasks.
- **Critical dependency [A6]**: Must validate what DoseSpot misses (Q14, Q17) before finalizing scope. If DoseSpot only covers in-network pharmacies, agent must explicitly prompt patient: "Any medications filled at other pharmacies? Any over-the-counter medications or supplements?"

**Anti-pattern check**: ✅ PASS — Reconciliation across three data sources (two structured, one unstructured) requires reasoning about discrepancies, not just list diff. Patient language interpretation requires NLP. Agent justified.

---

## Delegation Archetype Summary

| JtD | Archetype | Autonomy Level | Human Role | Rationale |
|-----|-----------|---------------|-----------|-----------|
| **JtD-1: Insurance Verification** | **Agent-led + Human Oversight** → **Fully Agentic** | HIGH (learning phase) → VERY HIGH (production) | Dana reviews re-verification triggers initially; spot-checks in production | High volume (180/day), structured APIs, clear re-verification rule once encoded [A3] |
| **JtD-2: PA Chase Timing** | **Agent-led + Human Oversight** → **Fully Agentic** | MEDIUM (learning phase, 3-6 months) → HIGH (production) | Dana approves chase recommendations initially; teaches insurer patterns; spot-checks unpredictable insurers in production | Highest-value unlock: Dana's institutional knowledge [A2, A4, A7]. Patterns learnable from Google Sheet + corrections. |
| **JtD-3: Visit Reason Triage** | **Human-led + Agent Support** | LOW (agent assists, human decides) | Dana/physician reviews all flagged cases; agent only surfaces ambiguity, never assesses urgency | Clinical judgment constraint [A13] + very high risk (patient safety). Agent cannot cross clinical boundary. |
| **JtD-4: Medication Reconciliation** | **Agent-led + Human Oversight** | MEDIUM (agent flags, physician reviews) | Physician reviews flagged discrepancies before visit; makes final decision on med list updates | Three-source reconciliation (athenahealth, DoseSpot [A6], patient verbal). High risk, but backstop via physician review. |

---

## Anti-Pattern Analysis: Could Any of These Be Rules/RPA Instead?

### JtD-1: Insurance Verification
**Could it be static rules?** No.
- 30% exception rate [A1] requires interpreting Availity error codes in context of patient history
- Re-verification rule [A3] has conditional logic (chronic patient identification requires pattern recognition: ≥3 visits in past year)
- **Agent justified** for exception handling + adaptive re-verification logic

### JtD-2: PA Chase Timing
**Could it be static rules?** No.
- Insurer-specific patterns are learned over 11 years [A2], not documented rules
- "Humana always 6 days, not 5" is empirical pattern, not API-provided SLA
- Denial patterns [A4] ("Wellpath needs prior visit note") are workarounds, not official requirements
- **Agent justified** for institutional knowledge capture + pattern learning

### JtD-3: Visit Reason Triage
**Could it be keyword list + escalation rules?** Partially, but agent adds value.
- Patient language is highly variable ("feeling off" vs. "chest pain" vs. "not feeling well")
- NLP required to normalize and interpret free text
- Agent learns from physician feedback to calibrate false positive/negative rate
- **Agent justified** for adaptive escalation + NLP interpretation, BUT must be conservative (human-led)

### JtD-4: Medication Reconciliation
**Could it be list diff + manual review?** Partially, but agent adds value.
- Reconciling three sources (two structured, one unstructured) requires interpretation
- Patient verbal report needs NLP ("I stopped that" is ambiguous)
- Identifying what DoseSpot misses [A6] requires reasoning about data source coverage gaps
- **Agent justified** for multi-source reconciliation + discrepancy interpretation

**Conclusion**: All 4 JtDs pass anti-pattern check. None can be solved with static rules or simple RPA. All require reasoning, pattern recognition, or NLP interpretation.

---

## Critical Dependencies for Delegation Design

### Dependency 1: Validate Dana's Re-Verification Rule [A3]
**Affects**: JtD-1 delegation archetype (Fully Agentic feasibility)  
**Questions**: Q6, Q8, Q9  
**Risk if not validated**: Agent over-verifies (API cost spike) or under-verifies (billing failures continue)  
**Next step**: Coach role-play to confirm: "All three billing failures were >6 months + chronic patients, same pattern?"

### Dependency 2: Confirm PA Pattern Stability [A2]
**Affects**: JtD-2 delegation archetype (Fully Agentic timeline)  
**Questions**: Q3, Q5  
**Risk if not validated**: Dana's Google Sheet patterns are stale; agent applies outdated timing  
**Next step**: Coach role-play: "Has an insurer changed their SLA in last 2 years? How did you adapt?"

### Dependency 3: Define Clinical Judgment Boundary [A13]
**Affects**: JtD-3 delegation archetype (Human-led vs. Agent-led)  
**Questions**: Q10, Q11, Q13  
**Risk if not validated**: Agent crosses into clinical territory (malpractice risk) or over-escalates (alert fatigue)  
**Next step**: Coach role-play: "What does 'no clinical judgment' mean in practice? Where's the line?"

### Dependency 4: Identify DoseSpot Integration Gaps [A6]
**Affects**: JtD-4 delegation scope (what to reconcile)  
**Questions**: Q14, Q15, Q17  
**Risk if not validated**: Agent misses medication sources DoseSpot doesn't cover; scope is incomplete  
**Next step**: Coach role-play: "What does DoseSpot actually miss? Out-of-network pharmacies? OTC? Samples?"

### Dependency 5: Validate Malpractice Insurance Constraints [A15]
**Affects**: All JtDs (especially JtD-3); determines if Fully Agentic is even allowed  
**Questions**: Q20  
**Risk if not validated**: Agent design violates malpractice policy; practice exposed to liability  
**Next step**: Coach role-play: "Have you talked to malpractice carrier about AI? Any requirements like human review?"

---

## Recommended Delegation Sequencing (Waves)

**POST-COACH UPDATE (2026-04-29)**: Wave sequencing revised based on Dana's Q18 answer: **PA timing misses are her #1 frustration**, not billing failures. Wave 1/Wave 2 swapped.

---

### Wave 1: High Value, Institutional Knowledge Capture (Strategic Priority)
**Target**: JtD-2 (PA Chase Timing) — Dana's insurer-specific patterns  
**Archetype**: Agent-led + Human Oversight (3-6 month learning phase) → Fully Agentic (production)  
**Rationale**:
- **Dana's #1 priority** (Q18): "If I could fix one thing, it would be proactive PA chase timing that never misses a deadline"
- Prevents visit aborts (Artefact 5.2: patient TJ's second abort; Dr. Westbridge's complaint)
- **Captures Dana's 11 years of institutional knowledge** [A2: HIGH confidence ⬆️, A4: VERY HIGH ⬆️, A7: VERY HIGH ⬆️] before she moves to regional role [A14: VERY HIGH ⬆️⬆️⬆️]
- Scalable to front-desk team + future hires (knowledge transfer)
- **Validated via coach**: Dana's PA time 1-2 hours/day (Q18), willing to teach patterns for 3-6 months (career-building)
- **Timeline**: 2 months build (Google Sheet ingestion, pattern extraction) → 3-6 months learning (Dana teaches patterns) → production

**Success metrics**:
- Zero visit aborts from PA timing misses (currently ~1/month, inferred from Artefact 5.2)
- Agent learns 15+ insurer-specific patterns (Humana 6d, UHC 7d, Wellpath denial workaround [A4: VERY HIGH ⬆️], etc.)
- Dana's time reduced from ~1-2 hours/day PA chases to ~15 minutes spot-checking

---

### Wave 2: High Suitability, Clear Rules (Self-Funding)
**Target**: JtD-1 (Insurance Verification) — re-verification rule enforcement  
**Archetype**: Fully Agentic (after 1-month validation)  
**Rationale**:
- High ROI (171%), fast payback (4.4 months)
- Clear rule validated [A3: VERY HIGH ⬆️]: >6mo + chronic patient (≥3 visits/year), plus sub-rules for Medicaid (every 3mo), Medicare Advantage (Q4), new insurance (next visit)
- Prevents billing failures (Artefact 5.3: $340 surprise bills)
- Builds athenahealth + Availity integrations → reused in Wave 3
- **Wave 1 PA chase** doesn't build reusable integrations (Google Sheet is unique to JtD-2)
- Wave 2 can start while Wave 1 is in learning phase (6-month overlap)
- **Timeline**: 1 month validation → 2 months build → 1 month pilot → production

**Success metrics**:
- Zero billing failures from stale verification (currently 3/quarter, validated via Q6)
- 30-50 proactive re-verifications/month
- $0 API cost increase (re-verify only when needed, not all patients)

---

### Wave 3: High Volume, Human Backstop (Highest ROI)
**Target**: JtD-4 (Medication Reconciliation) — three-source discrepancy flagging  
**Archetype**: Agent-led + Human Oversight (physician reviews flagged discrepancies)  
**Rationale**:
- **Highest ROI** (1,758% Year 1, 0.6-month payback)
- High volume (180/day), immediate physician time savings
- Risk mitigated by physician review before prescribing (backstop)
- **[A6] DoseSpot gaps now fully specified** (VERY HIGH confidence ⬆️⬆️): (1) out-of-network pharmacies (10-15%), (2) other providers' prescriptions, (3) OTC meds, (4) supplements, (5) samples. Dana estimates 70-80% pharmacy fills captured, 0% OTC/samples.
- Agent must explicitly prompt for missing sources: "Any meds filled at other pharmacies? Any OTC meds like aspirin, ibuprofen, allergy meds? Any vitamins or supplements? Any samples from specialists?"
- Reuses athenahealth integration from Wave 2
- **Timeline**: 2 months build (includes additional prompting logic for [A6] gaps) → 1 month pilot → production

**Success metrics**:
- Physician review time reduced from 6 min/patient to 30 sec (flagged list only)
- Zero unreviewed med changes discovered at visit time (currently "regular" [A8: MEDIUM ⬆️])
- Front-desk time freed up (~5 min/patient × 180 = 900 min/day = 15 hours/day across team)

---

### Wave 4 (Optional): High Risk, Conservative Design (Long-term)
**Target**: JtD-3 (Visit Reason Triage) — keyword-based urgency flagging  
**Archetype**: Human-led + Agent Support (conservative escalation)  
**Rationale**:
- **Clinical boundary constraint validated** [A13: VERY HIGH ⬆️]: "Recognition → escalate. Assessment → clinician." Front-desk can recognize keywords (chest pain, SOB, severe, sudden, can't) and escalate; cannot assess severity or decide disposition.
- **Malpractice risk** [A15: MEDIUM]: Dana expects human review required for anything clinical ("AI can assist, but a human has to review and approve")
- **Triage inconsistency confirmed** [A5: HIGH ⬆️]: No written protocol; Dana trains verbally; false negative example (hypertensive crisis missed)
- Lower immediate ROI (no documented failures in artefacts, but risk is high)
- **Timeline**: Defer until Waves 1-3 validated governance/monitoring for high-risk use cases; reassess based on malpractice carrier approval

**Success metrics** (if pursued):
- Standardized triage across 4-person team (reduce inconsistency [A9: HIGH ⬆️])
- Zero missed urgent symptoms (maintain current safety level, improve consistency)
- Physician alert fatigue: <5% false positive rate on escalations

---

## Output Artifacts (Phase 3 Complete)

✅ **Delegation Suitability Matrix**: 4 JtDs scored across 7 dimensions  
✅ **Archetype Assignment**: 2 Agent-led (→ Fully Agentic), 1 Agent-led (perpetual oversight), 1 Human-led  
✅ **Anti-Pattern Check**: All 4 JtDs justified for agents (none can be static rules/RPA)  
✅ **Critical Dependencies**: 5 assumptions validated via coach role-play (2026-04-29)  
✅ **Recommended Sequencing**: 3-wave implementation — **REVISED** based on Dana's Q18 answer:
   - **Wave 1**: PA Chase Timing (Dana's #1 priority)
   - **Wave 2**: Insurance Re-Verification (self-funding, builds reusable integrations)
   - **Wave 3**: Medication Reconciliation (highest ROI, reuses Wave 2 integrations)
   - **Wave 4** (optional): Visit Reason Triage (deferred, clinical risk)

---

## Next Steps (Phase 3 → Phase 4 Complete)

✅ **Phase 3 complete** (Delegation Qualification)  
✅ **Critical assumptions validated** via coach role-play (see `coach-roleplay-answers.md`)  
✅ **Confidence levels updated** (see `assumptions-update-post-coach.md`)  
✅ **Phase 4 complete** (Candidate Prioritization - see `scenario5-phase4-prioritization.md`)  
✅ **Wave sequencing updated** based on Dana's priority (Q18: PA timing is #1 frustration)

**Next: Implementation** (Wave 1 - PA Chase Timing)
1. Ingest Dana's Google Sheet (Artefact 5.1 + historical data)
2. Extract insurer-specific patterns (Humana 6d, UHC 7d, Wellpath denial workaround, etc.)
3. Build agent architecture (athenahealth API + chase timing logic + escalation rules)
4. Learning phase: Dana teaches patterns for 3-6 months, agent learns from corrections
5. Production transition: Agent autonomous for predictable insurers, Dana spot-checks Aetna

**Iteration tracking**: See `build-loop/iteration-003.md` for coach validation details.

---

**End of Phase 3: Delegation Qualification**
