## Scenario 2 (enriched) — Vendor Contract Clause Review

*Original brief in `README-Participants-Week1-Scenarios.md` § Scenario 2.*

### The company

**Helix Workforce Software** — UK-based mid-size B2B SaaS (London + Bristol offices, ~480 employees, ARR £42M, growing 25% YoY). Sells workforce-planning software to large UK and EU enterprises (banks, retailers, NHS trusts). Vendor contracts arrive at high volume from prospects and renewals because every customer's procurement team has its own paper.

### The function

5-person Legal & Commercial team: General Counsel, 3 Commercial Lawyers (mid-level, 3–6 yrs), 1 Paralegal (Tom).

### The four work streams

- **First-pass clause classification** (~300 contracts/quarter; ~25 min/case). Triaging an inbound contract, classifying each major clause against the playbook (liability cap / DPA / termination / IP / SLA / governing law / indemnity).
- **Standard-deviation redlining** (~60/quarter; ~45 min/case). Negotiable deviations the paralegal can redline against the playbook without escalation.
- **Escalated clause review** (~30/quarter; ~90 min/case). A senior lawyer reviews unusual clauses, frames a counteroffer position, drafts the redline.
- **Counteroffer drafting & sign-off** (~90/quarter; ~30 min/case). Drafting the response to procurement, named-lawyer sign-off, sending out.

### Tooling sketch

- **Ironclad** (CLM, modern SaaS, REST APIs)
- **Microsoft Word + Track Changes** (where redlining happens) and **SharePoint** (storage)
- **Salesforce** (sales pipeline; procurement requests for new contracts come in here)
- **Outlook** (vendor procurement teams send their paper here)
- **Internal "playbook" SharePoint page** (position statements per clause type)

### Stakeholder

**Amelia Forsythe**, General Counsel, 12 years at Helix. Hard rule: no counteroffer leaves Legal's queue without a named lawyer's sign-off on the specific clauses being negotiated. The CRO is pressuring Legal to halve contract turnaround (currently 4–6 days) to support enterprise sales targets.

### What you're expected to elicit through the week

Bring questions to your coach (role-playing Amelia) about:

- Why the named-lawyer-sign-off rule exists, and what specifically would break if it were relaxed.
- What recent regulatory changes (e.g., DPDI Act updates) are or aren't reflected in the playbook.
- How the paralegal actually triages cases day-to-day vs how the playbook describes triage.
- Where in the workflow shortcuts already exist that aren't in the SOP.
- What Amelia fears about AI-driven contract review — what specific failure mode would damage her position.

### Sample artefacts

#### Artefact 2.1 — Inbound clause excerpt with paralegal annotations

*Excerpts from a vendor MSA inbound from VendorCo Ltd (sales-tools procurement). Tom's margin notes captured during first-pass review.*

**Section 7.3 — Limitation of Liability**

> "Notwithstanding any other provision of this Agreement, neither party shall be liable to the other for any indirect, incidental, consequential, special, or punitive damages, regardless of the form of action, whether in contract, tort, or otherwise, even if advised of the possibility of such damages. The total aggregate liability of either party arising from this Agreement shall not exceed the lesser of (a) the fees paid by Customer in the six (6) months preceding the event giving rise to liability or (b) £50,000."

*[Tom's margin note: "Cap is below playbook minimum (12 months / £250k for enterprise). FLAG — but the term is borderline negotiable, not escalation. Will redline to playbook position."]*

**Section 11.2 — Data Processing Addendum**

> "The parties acknowledge that Customer's data may be processed in jurisdictions outside the United Kingdom. Vendor agrees to comply with applicable data protection laws including the UK GDPR and the Data Protection Act 2018."

*[Tom's margin note: "DPDI updates aren't reflected — playbook is stale on this. Honestly not sure if this needs escalation. Will ask Sarah."]*

**Section 14.1 — Termination for Convenience**

> "Either party may terminate this Agreement upon ninety (90) days' written notice without cause."

*[Tom's margin note: "Ours is 30 days for our paper, 90 for theirs. Routine — accept."]*

#### Artefact 2.2 — Vendor procurement insists on email-only redline

*Subject: VendorCo MSA — please return all redlines via this thread, our system can't accept SharePoint links.*

**Linda Carrington (VendorCo Procurement) → Tom Reilly (Helix Legal), Day 1:**
> "Hi Tom — sorry but our procurement workflow tool only accepts attachments via email. Please return the redlined Word doc as an attachment to this thread; do not send a SharePoint link as I won't be able to open it. We aim to turn around in-house review within 5 business days. Linda."

**Tom internal forwarding to Amelia, Day 1:**
> "FYI — VendorCo can't take our SharePoint link. I'll attach the redline directly. This is the third vendor this quarter who has the same issue; just flagging. Tom."

#### Artefact 2.3 — Playbook DPA section with sticky note

*From SharePoint > Legal > Contract Playbook > "Position Statements v3.4" (last revised 9 months ago).*

> **Section 12 — Data Processing Addendum (DPA)**
>
> **Position:** "We accept the standard UK GDPR / Data Protection Act 2018 DPA template provided in Annex C of this playbook. Vendors proposing materially different DPA terms should be redirected to Annex C; if they refuse, escalate to GC.
>
> **Standard clauses to verify:**
> - Sub-processor list disclosure
> - Data residency (UK/EEA preferred)
> - Breach notification SLA (≤72 hours)
> - SCC fallback clause for data leaving the UK"

*[Sticky note attached on the printed copy on Amelia's desk: "DPDI Act updates landed Q1 — need to add new sections re: legitimate interests test and data subject access changes. Talked about this with Sarah in March, never got round to it. — A."]*
