# Final Exam Scenario — Residential Mortgage Document Review at Meridian Home Lending

**FDE Accelerated Development Program v4.2 — Gate 5b Final Practical Exam**
**Released:** 08:45 CET, Virtual Friday Week 5 (the clock begins at 09:00).

---

## Engagement context

**Meridian Home Lending** is a mid-sized U.S. residential mortgage originator: ~$8B in annual originations, ~22,000 loans per year across conforming, jumbo, and FHA/VA product lines. Headquartered in Charlotte; licensed in 38 states.

You've been engaged as a Forward Deployed Engineer by Meridian's Chief Operating Officer, **Lena Okafor**. Her brief, summarised from the kickoff call:

> "Our underwriters are drowning. Every loan application arrives as a 'document package' — sometimes 30 PDFs, sometimes 60. Pay stubs, W-2s, tax returns, bank statements, IDs, employer letters, gift letters, divorce decrees, you name it. The underwriter spends 90 minutes per file just figuring out what's there, what's missing, and whether the numbers tie out. Then another 45 minutes deciding whether the borrower has the income, the assets, and the credit profile to clear our guidelines. We're processing 60 files per day with 28 underwriters and our backlog is 17 days. Senior underwriters are starting to leave. We've heard about AI doc review. We want it. But our compliance team is paranoid — fair-lending is our nightmare scenario."
>
> "I need a recommendation in 4 weeks. We've got a Document Review Pilot budget of $400K for build + first-year run. If you can come back with a credible agentic approach that we can defend to our Board and our regulators, we go. If not, we keep hiring underwriters."

## Your role and scope

Design and prototype an **agentic system for residential mortgage document review** at Meridian. The system must reduce the per-file underwriting handling time and surface a credible recommendation (or escalation) for each loan file, while keeping a human underwriter in the loop where loan-decisioning judgement is required.

**What the system needs to do** (the cognitive work to be delegated):

1. **Triage the incoming document package** — what borrower is this, what loan product, what's present, what's missing, what's misfiled?
2. **Extract and reconcile income evidence** — pay stubs + W-2s + tax returns + employer verification need to tell a consistent income story; flag the inconsistencies.
3. **Extract and reconcile asset evidence** — bank statements + gift letters + investment statements need to support down-payment + reserves; flag suspicious patterns (e.g., large unexplained deposits 60 days pre-application).
4. **Surface the underwriter-decision-relevant signals** — DTI estimate, LTV estimate, derogatory-credit indicators, residual income, manual-review triggers.
5. **Produce a structured underwriter package** for the human to review — what the agent saw, where confidence is high vs uncertain, what escalations the agent recommends.

**Scope guardrails** (from Lena's kickoff and follow-up Slack):

- **Not delegated:** the actual loan approval / denial decision. Human underwriter signs.
- **Not delegated:** any communication with the borrower. Underwriter or processor handles all borrower outreach.
- **In scope:** conforming + jumbo loan files. FHA/VA files route to a separate workflow — flag and skip.
- **Out of scope:** investor loans, commercial loans, rehab/construction loans.

## Stakeholder landscape

| Stakeholder | Their concern |
|---|---|
| **Lena Okafor** (COO, executive sponsor) | Throughput, cost, defensibility to the Board. "Don't make me explain a fair-lending finding to our regulators." |
| **Ravi Patel** (Chief Risk Officer) | Fair-lending exposure (ECOA, HMDA, CFPB attention to AI underwriting). Reproducibility of decisions. Audit trail. |
| **Kim Esposito** (VP Underwriting) | Her team's jobs. Will not endorse anything that auto-approves loans. Believes the senior judgement on borderline files is the value the team brings. Wants the system to support her seniors, not replace them. |
| **Marcus Reed** (CTO) | Integration footprint. Wants Claude Code-style build, sceptical of black-box vendor solutions. Hard line: borrower PII does not leave Meridian's infrastructure (state-by-state data-residency variance). |
| **Tara Lin** (Senior Underwriter, informal leader) | Skeptical of "AI promises." Wants to see specific examples of how the agent handles edge cases she'd flag manually. Has agreed to be the design partner. |

## The data you have

Sealed mock-data pack at `mock-data/` (released alongside this brief). Eight active loan applications from the past two weeks, sampled across:

- Salaried W-2 borrowers (cleanest)
- Self-employed / 1099 borrowers (income reconciliation harder)
- Co-borrower applications (two-person packages, joint or separate)
- One file with deliberately mis-named documents
- One file with an indicator of suspicious deposit pattern
- One file that should route to FHA workflow (you flag, you don't process)

Total ~30 files across the eight applications. Format mix: PDFs (pay stubs, W-2s, tax returns, IDs), CSV (bank statement transactions), `.eml` (employer verification emails), `.vtt` (transcripts of borrower clarification calls captured by processors).

**This is messy mock data.** Some documents are mis-named, some have OCR-like noise, some have inconsistent income figures across sources. That is the realistic shape of underwriting input — engage with the mess, don't assume it away.

## Success metrics (Lena's framing)

| Metric | Baseline | Target |
|---|---:|---:|
| Per-file underwriter handling time | 135 min | ≤ 60 min (with agent assist) |
| Files processed per underwriter per day | 2.1 | ≥ 4.5 |
| Re-work rate (files returned for additional documentation) | 28% | ≤ 18% |
| Underwriter-reported confidence at decision time | 6.1/10 | ≥ 7.5/10 |
| Fair-lending audit-trail completeness | (manual today) | 100% machine-generated |

These are the *headline* metrics. Your design should propose the actual operational and economic metrics you'd track, with reasoning.

## Constraints

- **Claude Code is the required build tool.** Mock data is required for the prototype.
- **Borrower PII stays inside Meridian's infrastructure.** Any model call that includes raw borrower data must be justifiable on that constraint.
- **8-hour clock** (09:00–17:00 CET). 4.5h design, 30-min curveball adaptation, 3h build incl. self-assessment + submission.
- **Solo.** No coach Q&A, no peer interaction. Claude Code is your only AI tool. Internet permitted for reference only (rate tables, regulatory text, documentation).
- The **scoring rubric** is released at 09:00 sharp alongside this brief.

## What to read first

Start with `mock-data/application-summary/index.md` — a one-page roster of the eight applications, their loan product, their borrower count, and which input artefacts are present. Then sample two or three of the applications across the format mix before designing.

You will receive a **curveball at 13:30 CET** that you will need to incorporate into your revised design before the build phase begins at 14:00. Plan for that.

---

*Sealed scenario — Final Exam, Gate 5b. Released 08:45 CET, Virtual Friday Week 5. Do not distribute or discuss with any person other than your proctor.*
