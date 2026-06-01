# Final Exam Scenario — AML / KYC Case Review at Lattice Pay

**FDE Accelerated Development Program v4.2 — Gate 5b Final Practical Exam**
**Released:** 08:45 CET, Virtual Friday Week 5 (the clock begins at 09:00).

---

## Engagement context

**Lattice Pay, Inc.** is a U.S.-chartered fintech offering consumer wallet, P2P transfers, business accounts, and a cross-border remittance product. ~4.8 million active consumer wallets, ~38,000 business accounts, ~$22B in annual transaction volume. HQ in Austin, TX. Bank-charter holder (FDIC member) since 2024 following a 5-year fintech-with-sponsor-bank period.

You've been engaged as a Forward Deployed Engineer by Lattice Pay's Chief Compliance Officer, **Dr. Priya Anjali Rao**. Her brief, captured from the kickoff:

> "Our BSA/AML monitoring system generates about 11,000 alerts a week. Our review team is 31 analysts. They are drowning. Each case takes 40–90 minutes to review depending on complexity — pulling the KYC profile, the transaction history, the network of counterparties, watchlist hits, prior cases, and writing a disposition memo. We have a 7-day SLA on alerts and we're at 6.2 days median with a long tail. Our false-positive rate is around 95% — industry average — but that means our analysts are spending 40 minutes on cases that close as 'no SAR.' The cases that DO need SAR filings, we're sometimes catching late, which is regulatory exposure we cannot have. And the CEO is on me about customer experience — when we freeze a wallet for investigation, the customer churn after we unfreeze is brutal."
>
> "Our Compliance Platform budget for this year includes $420K for AI-assisted case review build + first-year run. I need a recommendation in 4 weeks. We are not asking AI to file SARs. We are asking AI to do the 40-minute synthesis work so my analysts can do the judgement work, document the rationale defensibly, and move on. FinCEN and our state regulator are watching this space. Whatever we build must be explainable on a moment's notice to either of them."

## Your role and scope

Design and prototype an **agentic AML / KYC case review system** for Lattice Pay's consumer and business alerts. The system must reduce per-case analyst handling time and produce a structured "case package" for the analyst: synthesised KYC + transaction + network + watchlist + prior-cases view with surfaced patterns and a recommended disposition (clear, escalate to SAR, customer-RFI, account-freeze, or further-information-needed).

**What the system needs to do** (the cognitive work to be delegated):

1. **Ingest the alert and pull the case context** — the triggering transaction(s), the KYC profile of the customer, the last 90 days of transaction history, network of counterparties, watchlist hits, prior alert history.
2. **Synthesise the alert into a narrative** — what happened, what triggered the rule, what context the analyst needs.
3. **Surface patterns** — structuring across multiple transactions, layering through related accounts, sudden change in transaction profile, counterparty risk concentration, geographic/jurisdictional risk.
4. **Reconcile against watchlist screening** — confirm or disconfirm hits (name-based hits often false-positive on common names).
5. **Recommend a disposition** — with reasoning, span-citations to the underlying transactions, and a confidence level for the analyst to validate.

**Scope guardrails:**

- **Not delegated:** the SAR filing decision. Analyst signs.
- **Not delegated:** the customer freeze decision. Analyst recommends; supervisor approves.
- **Not delegated:** sanctions screening positive confirmation (an OFAC list hit is not the agent's call to declare).
- **Not delegated:** any communication with the customer or any other party.
- **In scope:** consumer wallet + business-account alerts.
- **Out of scope:** broker-dealer or securities-related alerts (different operation, different rule set, FINRA jurisdiction). Cross-border remittance product-specific alerts (separate, dedicated team and tooling).

## Stakeholder landscape

| Stakeholder | Their concern |
|---|---|
| **Dr. Priya Rao** (CCO, executive sponsor) | BSA/AML regulatory exposure. SAR timing. SLA on alerts. "Whatever we build is explainable on demand." |
| **Joaquín Velasco** (CEO) | False-positive rate. Customer churn after wallet freezes. Customer experience cost of investigations. |
| **Mona Karunaratne** (Chief Risk Officer) | Risk appetite. Model risk management. Third-party risk if any vendor model is used. |
| **William Akoto** (Head of Engineering) | PII handling. Borrower-data-stays-inside-Lattice constraint (no raw customer data to third-party APIs unless contractually safe-harboured). Build approach. |
| **Diane Reston** (Senior AML Analyst, 11 years at Lattice/sponsor-bank, design partner) | Wants augmentation, not replacement. "I do not want to spend my life agreeing with an AI summary. I want it to do the boring synthesis and let me argue with it." |
| **Tomáš Brejcha** (External FinCEN Examiner — relationship contact) | Will not approve a black-box. Reproducibility of dispositions. Explainability of model contributions. |

## The data you have

Sealed mock-data pack at `mock-data/`. Eight active AML/KYC review cases generated by the monitoring system in the past 5 business days across:

- Routine structuring-pattern alert that closes as no-SAR (clean baseline)
- Network analysis with one suspicious counterparty
- Watchlist false-positive (common-name OFAC hit)
- Watchlist genuine hit needing escalation
- High-velocity merchant-payments pattern (small-business account)
- Sudden onset of large cross-border transfers (touches the out-of-scope remittance line)
- Apparent layering pattern across linked accounts
- High-aggregate cash-equivalent activity with thin KYC

Total ~26 files across the eight cases. Format mix: KYC profiles (JSON), transaction-history extracts (CSV), watchlist-screening outputs (text reports), network-relationship data (JSON adjacency lists), customer-RFI email threads (.eml), and sanctions-list reference extracts.

**This is messy real-shaped data.** KYC fields are partially filled. Names match imperfectly to watchlists. Transaction patterns include genuine and decoy signals. Engage with the mess.

## Success metrics (Priya's framing)

| Metric | Baseline | Target |
|---|---:|---:|
| Per-case analyst handling time | 58 min | ≤ 18 min |
| Alert-to-disposition median cycle time | 6.2 days | ≤ 2.5 days |
| False-positive close rate (analyst confirms no-SAR) | 95% | (operational, not target) |
| SAR-eligible detection precision (cases agent recommends SAR vs analyst confirms) | n/a (baseline) | ≥ 75% |
| SAR-eligible recall (cases analyst files SAR that agent recommended SAR or escalate) | n/a | ≥ 95% |
| Reproducibility of disposition recommendation (re-run yields same disposition) | n/a | 100% across audit sample |

## Constraints

- **Claude Code is the required build tool.** Mock data is required for the prototype.
- **PII / customer data stays inside Lattice's infrastructure** unless safe-harboured. Architectural constraint per William.
- **8-hour clock** (09:00–17:00 CET). 4.5h design, 30-min curveball adaptation, 3h build incl. self-assessment + submission.
- **Solo.** No coach Q&A, no peer interaction. Claude Code is your only AI tool. Internet permitted for reference only.
- The **scoring rubric** is released at 09:00 sharp alongside this brief.

## What to read first

Start with `mock-data/case-queue/queue.md` — the alert queue the analyst sees. Then sample a few of the eight cases across the alert types.

You will receive a **curveball at 13:30 CET** that you will need to incorporate into your revised design before the build phase begins at 14:00. Plan for that.

---

*Sealed scenario — Final Exam, Gate 5b. Released 08:45 CET, Virtual Friday Week 5. Do not distribute or discuss with any person other than your proctor.*
