# Final Exam Scenario — Adverse Event Triage at Helix Therapeutics

**FDE Accelerated Development Program v4.2 — Gate 5b Final Practical Exam**
**Released:** 08:45 CET, Virtual Friday Week 5 (the clock begins at 09:00).

---

## Engagement context

**Helix Therapeutics, Inc.** is a mid-sized U.S. pharmaceutical company with three marketed products and seven pipeline assets. ~1,200 employees, ~$680M annual revenue, HQ in Cambridge MA. Marketed products: **Solivian** (chronic kidney disease, approved 2021), **Tezarimab** (multiple sclerosis, approved 2023), **Phaedora** (treatment-resistant depression, approved 2024).

You've been engaged as a Forward Deployed Engineer by Helix's Chief Medical Officer, **Dr. Maeve Carmichael**. Her brief from the kickoff:

> "Pharmacovigilance is the unglamorous backbone of every pharmaceutical company. We receive ~6,000 adverse event reports per year across our three marketed products — from physicians, patients, social media monitoring, our clinical trial sites, and the medical literature. Every single one must be triaged for seriousness, expectedness, and reportability — to FDA within 15 calendar days for serious-unexpected, periodic reporting for everything else, with parallel reporting to EMA, MHRA, and ~30 other regulators where we're marketed. Our case processing specialists average 75 minutes per case, and we have a backlog. The 15-day clock starts the moment any Helix employee or contractor receives the report, not when we open it."
>
> "Our PV Platform initiative has $510K budgeted for AI-assisted intake triage build + first-year run. We need the AI to do the unglamorous synthesis — extract patient + drug + adverse event from heterogeneous formats, classify seriousness per ICH E2A criteria, surface the expectedness question against the product reference safety profile, and recommend reportability. We are not asking AI to make the reportability decision. That's our medical safety officer's call. But if AI can do the synthesis and the classification recommendation in 5 minutes instead of 60, the safety officer can focus on the medical assessment."

## Your role and scope

Design and prototype an **agentic adverse event triage system** for Helix's marketed-product pharmacovigilance program. The system must reduce per-case handling time and produce a structured "AE case package" for the medical safety officer: extracted patient + drug + AE narrative + seriousness classification recommendation + expectedness signal + reportability recommendation, with reasoning and span-level citations.

**What the system needs to do** (the cognitive work to be delegated):

1. **Ingest heterogeneous AE reports** — HCP report forms (PDF, fax, email), patient direct reports (web form, phone), social-media monitoring extracts, clinical-trial-site reports (MedDRA-coded), literature alerts.
2. **Extract structured information** — patient demographics (age, sex, weight, race when reported), suspect drug + dose + indication, AE description + onset + outcome + temporal relationship, concomitant medications, medical history.
3. **Classify seriousness per ICH E2A** — death; life-threatening; hospitalisation (initial or prolonged); persistent or significant disability/incapacity; congenital anomaly/birth defect; "other medically important condition."
4. **Surface the expectedness signal** — against the product reference safety profile (Company Core Safety Information / Reference Safety Information).
5. **Recommend reportability** — 15-day expedited (serious-unexpected per FDA), periodic only, or non-reportable per definitions. Recommendation, with reasoning. Medical safety officer signs.

**Scope guardrails** (from Dr. Carmichael):

- **Not delegated:** the reportability decision. Medical safety officer signs.
- **Not delegated:** causality assessment final determination. The system surfaces a temporal/biological-plausibility signal; the safety officer makes the call.
- **Not delegated:** any communication with the reporter, the patient, or regulators.
- **Not delegated:** SAE follow-up information requests.
- **In scope:** adverse events for the three marketed products (Solivian, Tezarimab, Phaedora).
- **Out of scope:** medical device complaints (Helix's combination-product injectables route to a separate device complaint team and tooling). Clinical trial AEs for pipeline assets (separate sponsor obligations, separate group). Quality complaints with no AE component.

## Stakeholder landscape

| Stakeholder | Their concern |
|---|---|
| **Dr. Maeve Carmichael** (CMO, executive sponsor) | Patient safety. 15-day FDA clock compliance. Career consequence of late SAE reporting. |
| **Dr. Anil Iyer** (Senior Safety Physician, design partner) | Has done case processing for 15 years. "I do not want AI to write my medical assessment. I want AI to do the boring synthesis so I can write the assessment." |
| **Carolina Núñez-Reyes** (VP Regulatory Affairs) | Global reportability variance. "What's reportable to FDA in 15 days is not the same as what's reportable to PMDA. Be careful." |
| **Theo Lonergan** (Head of Drug Safety Operations) | Throughput. Backlog. Case processor capacity. "We are hiring case processors. I'd rather not." |
| **Greta Schäffer** (Chief Compliance Officer) | Inspection readiness. Audit trail. "Every reportability call needs to be defensible to an FDA inspector with the underlying evidence on demand." |
| **Dr. Hadi Mansour** (External pharmacovigilance audit consultant — former FDA reviewer) | Will not approve a black-box. Wants explicit audit trail. Has stated: "AI in pharmacovigilance is acceptable when it accelerates human safety physicians and is transparent. It is not acceptable when it makes the medical assessment." |

## The data you have

Sealed mock-data pack at `mock-data/`. Eight active AE reports received in the past 7 calendar days across:

- A serious-unexpected HCP report on Tezarimab (clear 15-day reportable, baseline)
- A patient-direct report on Phaedora with a non-medical narrative requiring extraction
- A social-media monitoring extract referencing Solivian + an AE with patient identifier challenges
- A clinical-trial-site report from a Solivian Phase 4 commitment study
- A medical device complaint that mis-routed to the AE intake (out-of-scope)
- A literature-published case series naming Tezarimab
- A fatal AE report on Phaedora with concomitant-medication causality complexity
- A non-serious expected AE on Solivian (the type of case that should triage quickly)

Total ~22 files. Format mix: HCP report PDF transcripts, patient web-form submissions (JSON), patient phone transcripts (.vtt), social-media monitoring extracts (JSON with conversation thread), clinical-trial-site MedDRA-coded reports, literature reference text, prior-case retrieval extracts.

**Engage with the heterogeneity. The reports are messy.**

## Success metrics (Maeve's framing)

| Metric | Baseline | Target |
|---|---:|---:|
| Per-case processing time (intake-to-triage-complete) | 75 min | ≤ 20 min |
| 15-day clock compliance (SAE reportability decided + filed within 15 calendar days from first receipt) | 92% | 99.5% |
| Seriousness classification accuracy vs safety physician adjudication (audit sample) | n/a baseline | ≥ 96% |
| Expectedness signal precision (cases flagged unexpected that are unexpected per RSI) | n/a baseline | ≥ 85% |
| Reportability recommendation precision (recommendations safety officer accepts as-is) | n/a baseline | ≥ 88% |
| Per-case audit-trail completeness (machine-generated for inspector retrieval) | 0% (manual today) | 100% |

## Constraints

- **Claude Code is the required build tool.** Mock data is required for the prototype.
- **Patient PII handling** — case identifiers + any genetic/sensitive data require defensible handling. Architectural constraint.
- **8-hour clock** (09:00–17:00 CET). 4.5h design, 30-min curveball adaptation, 3h build incl. self-assessment + submission.
- **Solo.** No coach Q&A, no peer interaction. Claude Code is your only AI tool. Internet permitted for reference only (regulatory text, MedDRA lookups, ICH E2A reference).
- The **scoring rubric** is released at 09:00 sharp alongside this brief.

## What to read first

Start with `mock-data/intake-queue/queue.md` — the case roster the intake specialist sees. Then `mock-data/product-information/` for the three Helix marketed products' reference safety profiles. Then sample a few cases across the format mix.

You will receive a **curveball at 13:30 CET** that you will need to incorporate into your revised design before the build phase begins at 14:00. Plan for that.

---

*Sealed scenario — Final Exam, Gate 5b. Released 08:45 CET, Virtual Friday Week 5. Do not distribute or discuss with any person other than your proctor.*
