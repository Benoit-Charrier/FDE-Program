# Final Exam Scenario — First Notice of Loss Intake at Cardinal Mutual Insurance

**FDE Accelerated Development Program v4.2 — Gate 5b Final Practical Exam**
**Released:** 08:45 CET, Virtual Friday Week 5 (the clock begins at 09:00).

---

## Engagement context

**Cardinal Mutual Insurance** is a mid-sized U.S. property & casualty carrier: ~$1.9B in net written premium, ~620,000 active policies across personal auto, homeowners, and small-business package lines, licensed in 24 states (concentration in the Southeast and Mountain West). HQ in Birmingham, AL.

You've been engaged as a Forward Deployed Engineer by Cardinal Mutual's VP of Claims, **Sarah Voss**. Her brief, captured from the kickoff call last week:

> "We take about 380 first-notice-of-loss intakes a day across our personal lines, more during weather events. Every FNOL is messy — a panicked phone call, an app submission that's half done, a broker emailing PDFs of police reports two days later, photos with no context. Our intake adjusters spend 25–40 minutes on each FNOL just figuring out what happened, what's covered, who else is involved, whether we need a field adjuster, and whether SIU should look at it. Cycle time from FNOL to first contact is creeping past 72 hours and it should be 24. Our combined ratio is sliding. Reggie (SIU Director) thinks we're missing fraud signal in the noise. Tom (VP Agency Relations) says our agents are losing patience because we ask the customer the same questions three times."
>
> "Our Claims Tech Pilot budget for this year is $375K for build + first-year run. I want a recommendation in 4 weeks. We want to use AI for first-pass triage — extract the facts, surface a coverage read, flag the SIU candidates, and route. We will NOT have AI making the coverage decision. The adjusters do that, with full context. But if AI can do the first 25 minutes of work in 25 seconds, I get my cycle time back and my adjusters get to focus on judgement."

## Your role and scope

Design and prototype an **agentic first-notice-of-loss triage system** for Cardinal Mutual's personal lines (auto + homeowners). The system must:

- Reduce the per-FNOL intake-adjuster handling time
- Produce a structured "FNOL package" for the human adjuster: extracted facts, coverage read with confidence, recommended routing (field adjuster vs desktop vs SIU referral vs additional information needed), surfaced anomalies

**What the system needs to do** (the cognitive work to be delegated):

1. **Ingest heterogeneous FNOL channels** — phone-call transcripts, app submissions, broker emails with PDF attachments, mailed-in claimant statements.
2. **Extract loss details** — what happened, when, where, who was involved, what damage, what other parties.
3. **Map to the right policy** — verify the reporting party against active policies; flag mid-policy lapse, recent endorsements, multi-policy households.
4. **Surface a coverage read** — based on extracted facts and policy form on file, what's likely covered, with what confidence, and where the underwriter judgement calls live.
5. **Surface anomaly and fraud signals** — for SIU consideration. The system does not declare fraud; it surfaces patterns for human review.
6. **Recommend routing** — field adjuster (e.g., total loss, large property), desktop adjuster (small auto), SIU (anomaly signals), or "info required" (missing critical fact).

**Scope guardrails** (from Sarah's kickoff and follow-up Slack):

- **Not delegated:** the coverage decision itself. Adjuster signs.
- **Not delegated:** any communication with the claimant or any other party. Adjuster or service rep handles.
- **Not delegated:** SIU referral acceptance. The system surfaces; SIU decides whether to investigate.
- **In scope:** personal auto + homeowners + condo. Personal umbrella where it sits on a covered auto/home loss.
- **Out of scope:** workers' comp claims (different operation, different licensure). Small-business package losses. Specialty lines.

## Stakeholder landscape

| Stakeholder | Their concern |
|---|---|
| **Sarah Voss** (VP Claims, executive sponsor) | Cycle time. Adjuster capacity. "I don't want to fire adjusters; I want to give them their lunches back." |
| **Marcus Holland** (CFO) | Combined ratio. Loss ratio. Reserve adequacy. Any architecture that systematically under-reserves at FNOL puts him at risk. |
| **Det. Reggie Vasquez** (SIU Director, ex-state insurance fraud bureau) | Fraud signal detection. Does not want AI making accusations. Wants the system to surface patterns and let SIU triage. "I lose half my actionable fraud cases in the FNOL noise. Help me see them, don't tell me what they are." |
| **Tom Mendez** (VP Agency Relations) | Independent-agent experience. Cardinal Mutual's distribution is broker-heavy; agents quit if claims is slow or asks the same question three times. |
| **Patricia Cho** (Chief Legal/Compliance Officer) | State-by-state regulatory variance (24 states, 24 sets of unfair-claims-practices acts). PII handling. Hard line: "Anything AI touches needs to be reproducible and explainable to a state DOI examiner." |
| **David Chen** (Senior Adjuster, 18 years at Cardinal Mutual, design partner) | Wants augmentation, not replacement. Has agreed to walk through edge cases. Skeptical of "AI scores" without reasoning. |

## The data you have

Sealed mock-data pack at `mock-data/`. Eight active FNOL intakes received in the past 5 days across:

- Clean auto fender-bender (straightforward routing)
- Homeowner water damage with coverage ambiguity
- Total-loss vehicle with anomaly signals (SIU candidate)
- One commercial-auto loss that mis-routed into the personal-lines queue (employee's work vehicle, commercial policy)
- One late-reported loss (loss occurred 18 days before report)
- Multi-vehicle accident with priority decision (which insurer leads)
- Photo set with metadata inconsistency
- Mid-policy lapse coverage question

Total ~35 files across the eight intakes. Format mix: phone-call transcripts (.vtt) from the FNOL line, app-submission JSON, broker emails (.eml) with PDF attachments (police reports, repair estimates, photo descriptions), mailed-in claimant statements (text), and policy/prior-claims extracts.

**This is messy real-shaped data.** Phone transcripts have crosstalk and corrections. App submissions have empty fields. Broker emails attach the wrong police report once. Engage with the mess.

## Success metrics (Sarah's framing)

| Metric | Baseline | Target |
|---|---:|---:|
| Per-FNOL intake-adjuster handling time | 32 min | ≤ 12 min |
| FNOL-to-first-contact cycle time | 71 hr | ≤ 24 hr |
| Coverage-decision reversal rate (adjuster overturns FNOL-routed disposition) | 14% | ≤ 8% |
| SIU referral precision (referrals that result in opened investigations) | 19% | ≥ 35% |
| Agent satisfaction (Net Promoter on claims intake) | -8 | ≥ +15 |
| Reproducibility of dispositions (re-run yields same disposition) | n/a | 100% across audit sample |

These are headline. Your design proposes the actual metrics you'd track operationally.

## Constraints

- **Claude Code is the required build tool.** Mock data is required for the prototype.
- **24-state regulatory variance.** PII handling must be defensible to a state DOI examiner. "Reproducible and explainable" is Patricia Cho's hard line.
- **8-hour clock** (09:00–17:00 CET). 4.5h design, 30-min curveball adaptation, 3h build incl. self-assessment + submission.
- **Solo.** No coach Q&A, no peer interaction. Claude Code is your only AI tool. Internet permitted for reference only.
- The **scoring rubric** is released at 09:00 sharp alongside this brief.

## What to read first

Start with `mock-data/intake-summary/queue.md` — the queue roster the FNOL adjuster sees. Then sample a few of the eight intakes across the channel mix.

You will receive a **curveball at 13:30 CET** that you will need to incorporate into your revised design before the build phase begins at 14:00. Plan for that.

---

*Sealed scenario — Final Exam, Gate 5b. Released 08:45 CET, Virtual Friday Week 5. Do not distribute or discuss with any person other than your proctor.*
