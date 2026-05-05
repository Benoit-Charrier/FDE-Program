# Helix Workforce Software — Vendor Contract Clause Review

*Full artefacts and background in `scenario/enriched_scenario.md`. This file is the single-source-of-truth scenario summary for use across all prompt templates.*

---

## 2. The Company

**Helix Workforce Software** is a UK-based, mid-size B2B SaaS company headquartered in London with a second office in Bristol. The company has approximately 480 employees, ARR of £42M, and is growing at 25% year-on-year. It sells workforce-planning software to large UK and EU enterprises, including banks, retailers, and NHS trusts. Because every customer's procurement team uses its own paper, vendor contracts arrive at high volume from both new prospects and renewals.

---

## 3. The Team

The **Legal & Commercial team** is 5 people:

- **Amelia Forsythe** — General Counsel; 12 years at Helix. Owns the named-lawyer sign-off rule (see Section 4). Point of escalation for all senior clause review.
- **3 Commercial Lawyers** — mid-level; 3–6 years' experience each. One is referred to by first name in the scenario artefacts as **Sarah**; the other two are unnamed.
- **Tom Reilly** — Paralegal. Handles first-pass clause classification and executes standard-deviation redlines within playbook authority. Identified in artefacts by full name.

---

## 4. The Process

The Legal & Commercial team reviews approximately **300 inbound vendor contracts per quarter**. Each contract is 15–40 pages and must be assessed against the company's negotiation playbook covering: liability caps, data processing addenda (DPAs), termination clauses, IP ownership, SLA commitments, governing law, and indemnity scope.

**Triage split (stated in scenario):**
- **70%** (~210/quarter) — standard terms matching the playbook; no redline required
- **20%** (~60/quarter) — negotiable deviations the paralegal can redline without escalation
- **10%** (~30/quarter) — unusual clauses requiring senior-lawyer review before any counteroffer is issued

**Turnaround target:** 4–6 business days. The procurement team (represented by the CRO) considers this unworkable and is pressuring Legal to halve it to support enterprise sales targets.

**Playbook:** Internal SharePoint page titled "Position Statements v3.4", last revised 9 months ago. The DPA section is known-stale: DPDI Act updates that landed Q1 have not been incorporated. Amelia is aware and has not yet scheduled the revision.

**Hard rules:**
- **No counteroffer may leave Legal's queue without a named lawyer's sign-off on the specific clauses being negotiated.** — owned by **Amelia Forsythe**, General Counsel. The rationale for this rule is not stated in the scenario and is flagged as a key discovery question.

---

## 5. The Work Streams

| # | Work stream | Volume/quarter | Time/case |
|---|---|---|---|
| WS1 | First-pass clause classification | ~300 | ~25 min |
| WS2 | Standard-deviation redlining | ~60 | ~45 min |
| WS3 | Escalated clause review | ~30 | ~90 min |
| WS4 | Counteroffer drafting & sign-off | ~90 | ~30 min |

- **WS1:** Triaging an inbound contract, classifying each major clause against the playbook (liability cap / DPA / termination / IP / SLA / governing law / indemnity). Performed by the paralegal (Tom Reilly).
- **WS2:** Redlining negotiable deviations against the playbook without escalation. Within the paralegal's authority. Approximately the 20% of contracts with standard deviations.
- **WS3:** Senior lawyer reviews unusual clauses, frames a counteroffer position, and drafts the redline. Required for the 10% escalation tier.
- **WS4:** Drafting the response to the vendor's procurement team, obtaining named-lawyer sign-off, and sending the counteroffer out. Volume (~90/quarter) corresponds to the combined WS2 and WS3 outputs that require a counteroffer.

---

## 6. Tooling

- **Ironclad** (CLM system; modern SaaS; REST APIs available)
- **Microsoft Word + Track Changes** (where redlining happens)
- **SharePoint** (document storage; also hosts the contract playbook)
- **Salesforce** (sales pipeline; procurement requests for new contracts originate here)
- **Outlook** (primary channel through which vendor procurement teams submit their paper; also used for counteroffer delivery when vendors cannot accept SharePoint links)

> **Named systems note:** Ironclad, Microsoft Word, SharePoint, Salesforce, and Outlook are confirmed in the scenario — treat them as facts, not assumptions. Any additional system introduced in subsequent deliverables must be labelled as an assumption. Specific API capabilities (beyond "REST APIs available" for Ironclad), rate limits, and integration maturity beyond what is stated in the scenario are still assumptions and must be labelled as such.

---

## 7. Key Artefacts

- **Artefact 1 — Inbound clause excerpt with paralegal annotations (Artefact 2.1):** Tom Reilly's margin notes on a VendorCo MSA reveal that triage and escalation boundaries are exercised with personal judgment, not strict rule-following. Tom independently decided a below-playbook liability cap (£50k vs. playbook minimum £250k) was "borderline negotiable, not escalation" — a call the playbook does not explicitly authorise. He also flagged DPDI uncertainty on the DPA section and noted he would ask Sarah rather than apply a rule, indicating that the escalation threshold is informally negotiated between team members rather than definitively documented.

- **Artefact 2 — Email: vendor insists on email-only redline delivery (Artefact 2.2):** VendorCo's procurement workflow cannot accept SharePoint links; Tom must email Word attachments instead. Tom's internal note to Amelia identifies this as the third such case in the quarter, confirming it is a recurring exception rather than an edge case. This means the actual counteroffer delivery workflow partially bypasses the CLM (Ironclad) and SharePoint-based process, creating a parallel email channel for a material fraction of contracts.

- **Artefact 3 — Playbook DPA section with Amelia's sticky note (Artefact 2.3):** The playbook's DPA section (Position Statements v3.4, revised 9 months ago) does not reflect DPDI Act Q1 updates. Amelia's handwritten sticky note confirms she is aware, that the update was discussed with Sarah in March, and that it has not been actioned. The playbook is therefore known-stale at the section most likely to be affected by recent UK regulatory change, and the team is operating against an outdated compliance standard for DPA clause review.

---

## 8. Assumption Log

> **Assumption [A1]:** The average review time of 90 minutes per contract stated in the original scenario brief (Scenario.md) refers to the all-in average across all work streams, not a per-work-stream figure. The enriched scenario provides disaggregated times per work stream (25 / 45 / 90 / 30 min), which do not arithmetically reconcile to a single 90-minute average across 300 contracts without additional weighting. The enriched scenario is treated as the more authoritative source; the 90 min figure from the base scenario is noted but not used as a primary metric in subsequent deliverables.
> **Why it matters:** Time-per-case drives the volume × value analysis and the economic case for agent assistance.
> **If wrong:** If 90 minutes is the correct per-contract figure (not the disaggregated figures), the labour burden estimate would be significantly higher and the ROI case stronger.
> **Confidence:** Medium

> **Assumption [A2]:** The WS4 volume of ~90/quarter represents the combined output of WS2 (~60) and WS3 (~30) — i.e., every contract that receives a redline also receives a formal counteroffer. The scenario does not explicitly state whether all redlined contracts proceed to counteroffer or whether some are resolved informally.
> **Why it matters:** If a significant number of redlines are resolved without a formal counteroffer (e.g., verbal agreement, withdrawn contracts), the actual WS4 volume and the sign-off bottleneck may be smaller than assumed.
> **If wrong:** WS4 volume and the named-lawyer sign-off bottleneck would need to be re-scoped.
> **Confidence:** Medium

> **Assumption [A3]:** The 70%/20%/10% triage split is a stable, approximate distribution and not a precise or audited figure. It is used as stated but may reflect Tom's perception rather than a measured rate.
> **Why it matters:** The split determines which work stream receives the most volume and therefore which is the highest-leverage agent target.
> **If wrong:** If the escalation rate (currently 10%) is higher in practice, the senior lawyer workload is larger and the agent design must handle a greater fraction of edge cases.
> **Confidence:** Medium

> **Assumption [A4]:** "Sarah" — mentioned in Artefact 2.1 — is one of the three unnamed Commercial Lawyers on the team. Her surname is not stated in the scenario.
> **Why it matters:** Relevant only for accurately attributing roles in the team section; does not affect process or agent design.
> **If wrong:** Sarah could be an external counsel or a person in another function. If so, the informal escalation path (Tom → Sarah) crosses a team boundary, which would have coordination implications.
> **Confidence:** High (contextually clear from the artefact that she is a lawyer on the same team)
