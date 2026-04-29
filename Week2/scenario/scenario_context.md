# Scenario Context — Helix Workforce Software

*Full artefacts and background in `scenario\enriched_scenario.md`. This file is the single-source-of-truth scenario summary for use across all prompt templates.*

---

## The company

**Helix Workforce Software** — UK-based B2B SaaS (~480 employees, ARR £42M, 25% YoY growth); sells workforce-planning software to UK/EU enterprises (banks, retailers, NHS trusts). London + Bristol offices.

---

## The legal team

5-person Legal & Commercial team:
- **Amelia Forsythe** — General Counsel, 12 years at Helix
- 3 Commercial Lawyers (mid-level, 3–6 yrs experience)
- **Tom** — Paralegal

---

## The process

~300 inbound vendor contracts per quarter; each 15–40 pages. Playbook covers 7 clause types: liability caps, DPAs, termination clauses, IP ownership, SLA commitments, governing law, indemnity scope.

- **Triage split:** 70% standard (accept as-is) / 20% negotiable deviations (paralegal can redline) / 10% senior-lawyer escalation required
- **Turnaround:** 4–6 business days; CRO is pressuring Legal to halve turnaround to support enterprise sales targets
- **GC hard rule:** no counteroffer leaves Legal's queue without a named lawyer's sign-off on the specific clauses being negotiated
- **Playbook status:** 9 months stale — DPDI Act Q1 updates (legitimate interests test, data subject access changes) not yet incorporated

---

## The four work streams

| # | Work stream | Volume/quarter | Time/case |
|---|-------------|----------------|-----------|
| 1 | First-pass clause classification | ~300 | ~25 min |
| 2 | Standard-deviation redlining | ~60 | ~45 min |
| 3 | Escalated clause review | ~30 | ~90 min |
| 4 | Counteroffer drafting & sign-off | ~90 | ~30 min |

- **WS1:** Triaging inbound contracts, classifying each major clause against the playbook
- **WS2:** Paralegal redlines negotiable deviations against playbook without escalation
- **WS3:** Senior lawyer reviews unusual clauses, frames counteroffer position, drafts redline
- **WS4:** Drafting the response to procurement, named-lawyer sign-off, sending out

---

## Tooling

- **Ironclad** (CLM, modern SaaS, REST APIs)
- **Microsoft Word + Track Changes** (redlining) and **SharePoint** (storage and internal playbook page)
- **Salesforce** (sales pipeline; procurement requests arrive here)
- **Outlook** (vendor procurement teams send contracts here)

**Named systems note:** Ironclad, Microsoft Word + Track Changes, SharePoint, Salesforce, and Outlook are confirmed in the scenario — treat them as facts, not assumptions. Any additional system you introduce must be labelled as an assumption. Specific API capabilities, rate limits, and integration maturity beyond what is stated above are still assumptions and must be labelled as such.

---

## Key artefacts (from enriched scenario)

- **Artefact 2.1 — Tom's VendorCo annotations:** Liability cap below playbook minimum (6 months / £50k vs. playbook 12 months / £250k) — flagged for redline, not escalation. DPDI DPA uncertainty — "will ask Sarah." Termination clause (90-day vs. Helix 30-day) — accepted as routine.
- **Artefact 2.2 — Email-only redline requirement:** VendorCo procurement cannot accept SharePoint links; demands Word attachment via email. Third vendor this quarter with this constraint. Tom has flagged the pattern to Amelia.
- **Artefact 2.3 — Playbook DPA section (v3.4, 9 months old):** Standard UK GDPR / DPA 2018 position with sub-processor list, data residency (UK/EEA preferred), 72-hour breach notification, SCC fallback. Amelia's sticky note: *"DPDI Act updates landed Q1 — need to add new sections re: legitimate interests test and data subject access changes. Talked about this with Sarah in March, never got round to it. — A."*
