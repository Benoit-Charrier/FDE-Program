# Scenario Context — Helix Workforce Software: Vendor Contract Clause Review

*Full artefacts and background in `scenario\enriched_scenario.md`. This file is the single-source-of-truth scenario summary for use across all prompt templates.*

---

## 0b. Table of contents

- [1. File header](#1-file-header)
- [2. The company](#2-the-company)
- [3. The team](#3-the-team)
- [4. The process](#4-the-process)
- [5. The work streams](#5-the-work-streams)
- [6. Tooling](#6-tooling)
- [7. Key artefacts](#7-key-artefacts)
- [8. Assumption log](#8-assumption-log)

---

## 1. File header

**Helix Workforce Software — Vendor Contract Clause Review**

*Full artefacts and background in `scenario\enriched_scenario.md`. This file is the single-source-of-truth scenario summary for use across all prompt templates.*

---

## 2. The company

**Helix Workforce Software** is a UK-based mid-size B2B SaaS company with approximately 480 employees, ARR of £42M, and 25% year-on-year growth. It operates from London and Bristol offices. Helix sells workforce-planning software to large UK and EU enterprises, including banks, retailers, and NHS trusts. Vendor contracts arrive at high volume from prospects and renewals because every customer's procurement team submits its own paper.

---

## 3. The team

**Legal & Commercial team** — 5 people:

- **Amelia Forsythe** — General Counsel, 12 years at Helix
- 3 Commercial Lawyers (mid-level, 3–6 years' experience; names not stated in scenario except Sarah, referenced informally in artefacts)
- **Tom** — Paralegal

---

## 4. The process

**Core process:** Inbound vendor contract review — ~300 contracts per quarter, each 15–40 pages.

**Governing document:** Internal negotiation playbook ("Position Statements v3.4"), hosted on SharePoint. Covers 7 clause types: liability caps, data processing addenda (DPAs), termination clauses, IP ownership, SLA commitments, governing law, indemnity scope. **Status: stale — last revised 9 months ago. DPDI Act Q1 updates (legitimate interests test, data subject access changes) have not been incorporated.**

**Triage / routing logic:**
- 70% standard — terms match playbook; accept as-is
- 20% negotiable deviations — paralegal can redline against playbook without escalation
- 10% escalation — unusual clauses requiring senior-lawyer review before any counteroffer goes out

**Turnaround target:** Current: 4–6 business days. Pressure: The CRO is pushing Legal to halve turnaround to support enterprise sales targets.

**Hard rule (non-negotiable):** No counteroffer may leave Legal's queue without a named lawyer's sign-off on the specific clauses being negotiated. Owned by **Amelia Forsythe**, General Counsel.

---

## 5. The work streams

| # | Work stream | Volume/quarter | Time/case |
|---|-------------|----------------|-----------|
| WS1 | First-pass clause classification | ~300 contracts | ~25 min |
| WS2 | Standard-deviation redlining | ~60 contracts | ~45 min |
| WS3 | Escalated clause review | ~30 contracts | ~90 min |
| WS4 | Counteroffer drafting & sign-off | ~90 contracts | ~30 min |

- **WS1:** Triaging an inbound contract and classifying each major clause against the 7-clause playbook.
- **WS2:** Redlining negotiable deviations against the playbook — performed by the paralegal without escalation.
- **WS3:** Senior lawyer reviews unusual clauses, frames a counteroffer position, and drafts the redline.
- **WS4:** Drafting the response to procurement, obtaining named-lawyer sign-off, and sending the counteroffer out.

---

## 6. Tooling

- **Ironclad** (CLM — contract lifecycle management, modern SaaS with REST APIs)
- **Microsoft Word + Track Changes** (where redlining is performed)
- **SharePoint** (document storage; hosts the playbook and contract files)
- **Salesforce** (sales pipeline; procurement requests for new contracts originate here)
- **Outlook** (vendor procurement teams submit their contracts via email)
- **Internal playbook SharePoint page** (position statements per clause type — "Position Statements v3.4")

> **Named systems note:** Ironclad, Microsoft Word, SharePoint, Salesforce, and Outlook are confirmed in the scenario — treat them as facts, not assumptions. Any additional system introduced in subsequent deliverables must be labelled as an assumption. Specific API capabilities, rate limits, and integration maturity beyond what is stated in the scenario are still assumptions and must be labelled as such.

---

## 7. Key artefacts

- **Artefact 2.1 — Inbound clause excerpt with paralegal annotations:** Tom's margin notes on a VendorCo MSA reveal three things about the lived process: (1) he applies judgment at the classification boundary — a liability cap below playbook minimum is assessed as "borderline negotiable, not escalation" without a codified rule distinguishing the two; (2) he recognises the DPA playbook is stale relative to DPDI Act updates and escalates informally to a colleague ("Will ask Sarah") rather than following a documented decision path; (3) routine clauses (e.g., 90-day termination on vendor paper) are accepted without consultation, suggesting a significant proportion of classification is deterministic.

- **Artefact 2.2 — Vendor procurement insists on email-only redline:** A VendorCo procurement email requires redlines to be sent as Word attachments rather than SharePoint links. Tom's internal forward to Amelia notes this is "the third vendor this quarter" with the same constraint, indicating a recurring workaround that bypasses the CLM's intended delivery mechanism and would affect any agent that assumes SharePoint-link delivery as standard.

- **Artefact 2.3 — Playbook DPA section with sticky note:** The printed playbook copy on Amelia's desk has a handwritten sticky note acknowledging that DPDI Act Q1 updates have not been incorporated into the playbook despite being discussed in March. This confirms the playbook staleness is known, unresolved, and affects the DPA clause type specifically — the most compliance-sensitive clause type in the set.

---

## 8. Assumption log

> **Assumption [A1]:** The volume figures (~300 / ~60 / ~30 / ~90 per quarter) are stated in the enriched scenario as approximate. They are treated as accurate for baseline calculations in subsequent deliverables.
> **Why it matters:** Drives volume scoring in D3 and TCO arithmetic.
> **If wrong:** Volume scores and payback period calculations would need revision; if actual volume is significantly lower, the economic case for automation weakens.
> **Confidence:** Medium

> **Assumption [A2]:** The time-per-case figures (25 / 45 / 90 / 30 min) are stated in the enriched scenario. They are taken as average active working time, not elapsed calendar time.
> **Why it matters:** Drives baseline cost-per-case in the TCO sense-check (D3) and KPI baselines (D4).
> **If wrong:** If figures include wait time or multi-tasking, the actual cognitive load per case may be lower, reducing the value of automation for time savings.
> **Confidence:** Medium

> **Assumption [A3]:** "Sarah" referenced in Artefact 2.1 is one of the three named Commercial Lawyers. The scenario does not give her full name or confirm her role explicitly.
> **Why it matters:** Escalation routing design in D4 assumes a named lawyer is reachable for informal DPA questions — if Sarah is a different role, the escalation path needs revision.
> **If wrong:** Escalation trigger design may misroute informal queries.
> **Confidence:** High (inference from context)

> **Assumption [A4]:** Ironclad's REST APIs are available for read and write access to case records, routing fields, and audit logs. The scenario names Ironclad and states it is a modern SaaS with REST APIs, but does not confirm specific endpoint availability or authentication requirements.
> **Why it matters:** Drives integration feasibility in D5. If the relevant endpoints do not exist or are behind enterprise licensing tiers, the integration design must change.
> **If wrong:** Core agent integration path (write classification output to Ironclad) would need a manual workaround or alternative system.
> **Confidence:** Medium
