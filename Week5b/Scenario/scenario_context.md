# Lattice Pay, Inc. — AML / KYC Case Review

*Extracted from sealed scenario packet. Single source of truth for all prompts.*

---

## 1. The company

**Name:** Lattice Pay, Inc.
**Industry / domain:** U.S.-chartered fintech — consumer wallet, P2P transfers, business accounts, and cross-border remittance
**Business model:** Consumer-facing payments platform offering wallet, P2P, business accounts, and cross-border remittance; bank-charter holder (FDIC member) since 2024, following a 5-year fintech-with-sponsor-bank period
**Size / scale:** ~4.8 million active consumer wallets; ~38,000 business accounts; ~$22B annual transaction volume; 31 AML analysts (team size stated; total headcount NOT STATED)
**Geography:** HQ in Austin, TX. State(s) of licensure NOT STATED beyond FDIC membership.

---

## 2. The stakeholders

**Dr. Priya Anjali Rao — CCO (Chief Compliance Officer), executive sponsor**
- Primary concern: BSA/AML regulatory exposure; SAR timing; SLA on alerts; explainability to FinCEN and state regulator on demand
- Non-negotiable position: AI must not file SARs — analyst signs. Whatever is built must be explainable on a moment's notice to FinCEN and state regulator.
- Success looks like: AI does the 40-minute synthesis work; analysts do the judgement work; rationale is documented defensibly; FinCEN can examine any disposition on demand

**Joaquín Velasco — CEO**
- Primary concern: False-positive rate; customer churn after wallet freezes; customer experience cost of investigations
- Non-negotiable position: NOT STATED explicitly
- Success looks like: Reduced false-positive rate; less customer churn from unnecessary wallet freezes

**Mona Karunaratne — Chief Risk Officer**
- Primary concern: Risk appetite; model risk management; third-party risk if any vendor model is used
- Non-negotiable position: NOT STATED explicitly
- Success looks like: Model risk is managed; third-party risk is acceptable

**William Akoto — Head of Engineering**
- Primary concern: PII handling; architectural constraint that no raw customer data leaves Lattice's infrastructure unless contractually safe-harboured; build approach
- Non-negotiable position: Raw customer data must not go to third-party APIs unless contractually safe-harboured
- Success looks like: Architecture is defensible; PII stays inside Lattice

**Diane Reston — Senior AML Analyst (11 years at Lattice/sponsor-bank), design partner**
- Primary concern: Augmentation, not replacement. "I do not want to spend my life agreeing with an AI summary. I want it to do the boring synthesis and let me argue with it."
- Non-negotiable position: System must not replace analyst judgement
- Success looks like: AI handles boring synthesis; analyst handles judgement; she can challenge the AI's reasoning

**Tomáš Brejcha — External FinCEN Examiner (relationship contact)**
- Primary concern: Reproducibility of dispositions; explainability of model contributions
- Non-negotiable position: Will not approve a black-box
- Success looks like: Dispositions are reproducible and explainable to a FinCEN examiner on demand

---

## 3. The process

**Core process:** BSA/AML alert triage — an analyst receives a monitoring-system alert, pulls the KYC profile, transaction history, counterparty network, watchlist hits, and prior cases, then writes a disposition memo recommending an action.
**Daily / monthly volume:** ~11,000 alerts per week (stated in Priya's brief). [Daily figure NOT STATED; no monthly figure stated.]
**Current performance:**
- Per-case review time: 40–90 minutes depending on complexity (Priya's brief)
- Per-case review time (median): 58 minutes (metrics table)
- Alert-to-disposition median cycle time: 6.2 days with a long tail (Priya's brief + metrics table)
- Alert SLA: 7 days (Priya's brief)
- False-positive rate: ~95% (stated as "industry average" by Priya)
**Current automation level:** NOT STATED — process described as analyst-performed (implied manual)
**Industry benchmark:** 95% false-positive rate cited as "industry average" for AML alerts
**Cycle time / SLA:** 7-day SLA; currently at 6.2 days median (marginal compliance)

---

## 4. The work streams

**WS-1: Alert Intake and Case Context Pull**
- What it does: Ingest the monitoring-system alert; retrieve the triggering transaction(s), KYC profile, last 90 days of transaction history, network of counterparties, watchlist hits, and prior alert history
- Who does it today: AML analyst (manual)
- Volume: All ~11,000 alerts/week
- Key pain: The pull step alone is a significant portion of the 40–90 min per case; messy, multi-source data with partially filled KYC fields

**WS-2: Alert Narrative Synthesis**
- What it does: Synthesise the alert context into a human-readable narrative — what happened, what triggered the rule, what context the analyst needs to make a judgement
- Who does it today: AML analyst (manual memo writing)
- Volume: All ~11,000 alerts/week
- Key pain: Repetitive synthesis consuming analyst capacity on cases that close as no-SAR (95% false-positive rate)

**WS-3: Pattern Surfacing**
- What it does: Identify structuring across multiple transactions, layering through related accounts, sudden change in transaction profile, counterparty risk concentration, geographic/jurisdictional risk
- Who does it today: AML analyst (manual)
- Volume: All cases; patterns may or may not be present
- Key pain: SAR-eligible cases are being caught late; patterns are getting lost in the noise of 11,000 weekly alerts

**WS-4: Watchlist Screening Reconciliation**
- What it does: Confirm or disconfirm watchlist hits — name-based OFAC/sanctions hits are often false-positives on common names; agent surfaces reasoning but does not declare a positive confirmation
- Who does it today: AML analyst (manual)
- Volume: Subset of cases with watchlist hits
- Key pain: High false-positive rate on name-based hits consumes analyst time; genuine hits risk being delayed

**WS-5: Disposition Recommendation and Documentation**
- What it does: Recommend one of five dispositions (clear, escalate to SAR, customer-RFI, account-freeze, further-information-needed) with reasoning, span-citations to underlying transactions, and a confidence level
- Who does it today: AML analyst writes the disposition memo; analyst signs
- Volume: All ~11,000 alerts/week
- Key pain: 40 min per case on cases that close as no-SAR; FinCEN requires the reasoning to be explainable and reproducible on demand

---

## 5. Systems and tooling

| System | Stated purpose | Integration notes |
|--------|---------------|-------------------|
| BSA/AML monitoring system | Generates ~11,000 alerts/week | Product name NOT STATED; no integration details stated |
| Mock-data pack (`mock-data/`) | Sealed exam data — 8 cases, ~26 files | KYC profiles (JSON), transaction history (CSV), watchlist outputs (text), network data (JSON adjacency lists), customer-RFI emails (.eml), sanctions-list reference extracts |

No other systems named in scenario. KYC platform, case management system, and watchlist screening tooling are all UNNAMED — all integration assumptions will be stated explicitly in later deliverables.

---

## 6. Compliance and regulatory requirements

1. **BSA/AML (Bank Secrecy Act / Anti-Money Laundering)** — core regulatory obligation; 7-day SLA on alert review stated
2. **SAR filing (FinCEN)** — Suspicious Activity Reports must be filed; AI is explicitly prohibited from making the SAR filing decision; analyst signs. FinCEN SAR filing deadline NOT STATED in scenario (regulatory baseline: 30 days from detection of suspicious activity).
3. **OFAC sanctions screening** — positive confirmation of an OFAC list hit is not the agent's call to declare; agent surfaces the match, analyst confirms
4. **FinCEN oversight** — "FinCEN and our state regulator are watching this space"; dispositions must be explainable to FinCEN examiner on demand
5. **State regulator** — named but NOT IDENTIFIED; state of licensure not specified
6. **Customer freeze** — AI cannot make the freeze decision; analyst recommends, supervisor approves
7. **PII / customer data residency** — raw customer data must not leave Lattice's infrastructure unless contractually safe-harboured (hard constraint from William Akoto)
8. **FDIC membership** — bank-charter holder since 2024; federal banking regulation applies
9. **Reproducibility** — 100% across audit sample is a stated target; all dispositions must be re-runnable with the same outcome
10. **Out-of-scope: FINRA jurisdiction** — broker-dealer/securities-related alerts are explicitly out of scope (different rule set)

---

## 7. Stakeholder tensions

**Priya (CCO) vs. Joaquín (CEO):**
Priya is focused on regulatory exposure and SAR timing — missing a SAR is her nightmare. Joaquín is focused on customer experience and false-positive rate — unnecessary wallet freezes cause "brutal" customer churn. These goals can conflict: erring towards more escalations (SAR/freeze) improves regulatory safety but worsens customer experience.

**Priya (CCO) / Tomáš Brejcha (FinCEN) vs. AI capability:**
Both Priya and Brejcha require full explainability and reproducibility. Brejcha "will not approve a black-box." This is an architectural constraint that limits the use of opaque vendor models and requires span-level citation of evidence in every disposition.

**Diane (Analyst) vs. AI system:**
Diane explicitly does not want to spend her time "agreeing with an AI summary" — she wants the system to do synthesis so she can argue with it. The risk is an over-confident AI that presents conclusions rather than evidence, which would make Diane's role feel like rubber-stamping.

**William (Engineering) / Mona (CRO) vs. capability:**
William's PII constraint (no raw data to third-party APIs) and Mona's third-party risk concern together mean any external model usage requires contractual safe-harbours or self-hosted infrastructure. This constrains the choice of AI model and hosting architecture.

---

## 8. Key metrics (baseline)

| Metric | Value | Source |
|--------|-------|--------|
| Weekly alert volume | ~11,000 | Priya's brief |
| Review team size | 31 analysts | Priya's brief |
| Per-case review time (range) | 40–90 minutes | Priya's brief |
| Per-case review time (median) | 58 minutes | Success metrics table |
| Alert-to-disposition median cycle time | 6.2 days | Priya's brief + metrics table |
| Alert SLA | 7 days | Priya's brief |
| False-positive rate | ~95% | Priya's brief (stated as "industry average") |
| Budget (build + first-year run) | $420K | Priya's brief |
| Target: per-case analyst handling time | ≤ 18 minutes | Success metrics table |
| Target: alert-to-disposition cycle time | ≤ 2.5 days | Success metrics table |
| Target: SAR-eligible detection precision | ≥ 75% | Success metrics table |
| Target: SAR-eligible recall | ≥ 95% | Success metrics table |
| Target: disposition reproducibility | 100% across audit sample | Success metrics table |
| False-positive close rate (target) | NOT STATED (listed as "operational, not target") | Success metrics table |

---

## 9. Open gaps (facts needed but not stated)

1. **Alert management / case management platform** — no named platform; integration approach is an assumption. Will need to assume a queue + case API or flat-file handoff.

2. **SAR filing deadline** — scenario says SAR-eligible cases are "sometimes caught late" but does not state the FinCEN SAR filing deadline. The regulatory baseline (30 days from detection, or 60 days from first-awareness) will be treated as an assumption with HIGH confidence based on BSA/AML regulation.

3. **Watchlist screening tooling** — no named OFAC/FinCEN screening platform. How the agent connects to live lists vs. static reference extracts is an assumption.

4. **KYC source system** — KYC profiles are provided as JSON in the mock data, but the production source system is unnamed. Integration pattern is an assumption.

5. **Per-analyst throughput capacity** — 31 analysts for ~11,000/week implies ~355 cases/analyst/week (~71/day at a 5-day week). At 58 min/case this implies 68 hours/analyst/week — clearly unsustainable. The actual capacity constraint (how many cases per analyst per day are expected) is NOT STATED.

6. **Disposition taxonomy completeness** — five dispositions are named (clear, escalate to SAR, customer-RFI, account-freeze, further-information-needed). Whether this list is exhaustive is NOT STATED.

7. **State regulator identity** — "our state regulator" is mentioned but not named. Texas Department of Banking is assumed based on Austin, TX HQ, but NOT CONFIRMED.

8. **Customer churn figure** — Joaquín calls post-freeze churn "brutal" but no quantitative figure is stated. Will be treated as a metric Lattice tracks but did not share.

9. **Audit trail retention period** — FinCEN requires BSA record retention; the scenario does not specify the required retention window (5 years is the regulatory baseline — will be assumed).

10. **Cross-border remittance boundary** — the scenario places cross-border remittance alerts out of scope for this system but notes one of the 8 mock cases "touches the out-of-scope remittance line." The exact routing rule for these edge cases is not defined beyond "flag and separate."
