# Deliverable 1 — Discovery Notes
## Problem Framing & Success Metrics
**Gate 5b Final Exam · Lattice Pay AML/KYC Case Review**

---

## Engagement summary

Lattice Pay's BSA/AML compliance team is structurally under-resourced relative to alert volume.
31 analysts process ~11,000 alerts per week. At a measured 58-minute average per case, the team
has theoretical capacity for ~1,280 cases per week — a ~8.6× gap between alert volume and
throughput. The team bridges this gap through prioritisation, but it creates a 6.2-day median
cycle time and a long tail of aging alerts that represent direct regulatory exposure (7-day SLA).

The root cause is not analyst skill — it is structural: 95% of analyst time is consumed by data
gathering and synthesis (pulling KYC, transaction history, watchlist hits, counterparty networks,
prior cases from disparate systems, then writing it into a coherent narrative). This is
high-volume, repeatable cognitive assembly work. The remaining 5% — the judgment call and the
SAR/no-SAR determination — is the irreducible human work and is currently squeezed by the 95%.

**The ask:** delegate the synthesis to an agent. Free the analyst to spend their 58 minutes on
18 minutes of judgment.

---

## Problem framing

### The job that needs to be done

An AML analyst reviewing an alert must answer one question:

> *Given everything I know about this customer, their transactions, their counterparties, and
> any watchlist exposure — does this alert represent suspicious activity that requires further
> action, or can I close it?*

Answering that question requires assembling information from 4–6 systems, interpreting patterns
across time and counterparty networks, and producing a documented rationale. The agent handles
the assembly and pattern interpretation. The analyst handles the question.

### What "messy" means in practice

From data sampling:
- KYC profiles are partially filled (ITIN-only, missing occupation, tier-1 verification)
- Watchlist hits are almost always common-name false-positives requiring manual disconfirmation
- Transaction histories contain genuine and decoy signals (Mohammed Khan: textbook student wallet triggering an OFAC alert on name alone)
- Counterparty networks span 4 linked accounts with a single shared device fingerprint (layering case — definitionally suspicious)
- Prior RFI history is load-bearing context: account limit lifted after customer complaint → then $61K cash-equivalent inflow (thin KYC case — risk escalates)
- One case (AML-1322) touches the cross-border remittance product line — out-of-scope for this agent; routing is a required behaviour

The agent must be robust to missing fields, imperfect name matches, multi-entity cases, and
boundary conditions that require scope routing rather than analysis.

---

## Stakeholder alignment notes

| Stakeholder | Key requirement | Design implication |
|---|---|---|
| Dr. Priya Rao (CCO) | Explainability on demand to FinCEN/state regulator | Every recommendation must cite specific transactions + reasoning chain. Reproducibility = 100%. |
| Joaquín Velasco (CEO) | Reduce false-positive cycle time; cut wallet-freeze churn | Agent must disconfirm common-name watchlist hits confidently and quickly |
| Mona Karunaratne (CRO) | Model risk management; third-party risk | Architecture must keep PII inside Lattice; model selection must be documented |
| William Akoto (Engineering) | PII stays inside Lattice infrastructure | No raw customer data to third-party APIs without safe harbour |
| Diane Reston (Lead analyst) | Augmentation, not replacement. "Let me argue with it." | Output must be structured, citable, and arguable — not a summary to rubber-stamp |
| Tomáš Brejcha (FinCEN examiner) | No black box; reproducible dispositions | Chain-of-thought reasoning logged with every case; re-run produces identical output |

---

## Scope boundaries (from scenario-brief)

**In scope:**
- Consumer wallet alerts
- Business account alerts
- Structuring, layering, watchlist, counterparty, high-velocity, and thin-KYC alert types

**Out of scope — agent must route, not analyse:**
- Cross-border remittance product-specific alerts (separate team) → agent detects and flags for routing
- Broker-dealer / securities-related alerts (FINRA jurisdiction) → not expected in Lattice Pay alert queue

**Not delegated to agent — analyst/supervisor only:**
- SAR filing decision
- Customer freeze or wallet restriction decision
- OFAC positive confirmation (a genuine SDN hit is not the agent's determination)
- Any communication with the customer or third parties

---

## Success metrics (Priya Rao's framing)

| Metric | Baseline | Target | How measured |
|---|---:|---:|---|
| Per-case analyst handling time | 58 min | ≤ 18 min | Time-tracked per disposition from case-package delivery to analyst sign-off |
| Alert-to-disposition median cycle | 6.2 days | ≤ 2.5 days | Timestamp: alert trigger → final disposition recorded |
| False-positive close rate | 95% | Operational (not a target to reduce) | Monitor for regression |
| SAR-eligible detection precision | n/a | ≥ 75% | Agent recommends ESCALATE_SAR → analyst confirms SAR filed |
| SAR-eligible recall | n/a | ≥ 95% | Analyst files SAR → retrospective check: did agent recommend SAR or escalate? |
| Disposition reproducibility | n/a | 100% | Re-run same case with same inputs → identical disposition + reasoning |

---

## Key constraints

1. **Budget:** $420K for AI-assisted case review build + first-year run (per Dr. Rao)
2. **PII constraint:** No raw customer data to third-party APIs without contractual safe harbour (William Akoto)
3. **Regulatory explainability:** Every disposition must be reproducible and traceable on demand (FinCEN / state regulator)
4. **Analyst autonomy:** The agent recommends; the analyst decides. The agent must produce output that invites scrutiny, not output designed to be accepted passively.
5. **Timeline:** 4-week recommendation window for Dr. Rao; prototype required for credibility

---

## Open questions / assumptions flagged

| ID | Assumption | Risk if wrong | Validation required |
|---|---|---|---|
| A1 | KYC, transaction, watchlist, and network data are accessible via internal API (not file extract only) | Agent cannot be production-ready without API access; prototype uses mock files | Confirm with William Akoto |
| A2 | Watchlist screening is pre-computed at alert time (screening report exists per case) | If not, agent must call OFAC API directly — PII constraint applies | Confirm with compliance team |
| A3 | Prior alert history per customer is queryable by customer ID | Critical for layering and thin-KYC cases where prior RFI is load-bearing | Confirm with Engineering |
| A4 | The remittance product alert queue is genuinely separate (different system, different team) | AML-1322 suggests boundary is fuzzy in practice | Confirm routing protocol with Dr. Rao |
| A5 | 31 analysts remain the review team; no headcount change planned | Economics model depends on human cost being fixed | Confirm with Dr. Rao / HR |
