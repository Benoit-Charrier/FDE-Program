# Gate 2 — Participant Pack

**Gate:** Gate 2 (Week 2) — Cognitive Work Assessment & Agent Design
**Released:** Friday Week 2, 09:00 CET (scenario previously unseen).
**Timed exercise:** 3 hours, starts when you open this pack. Submissions close at 12:00 CET.
**Live clarification round:** ~10 minutes per participant, scheduled 15:30–17:30 CET; your specific slot is confirmed by your coach team. Format may be 1:1 or small-group of 3 — your coach team confirms.

Read this pack end-to-end before you start. The clock begins when you open it, not when you finish reading it — but reading the whole pack first will pay back more than the time it costs.

---

## 1. What Gate 2 is testing

Gate 2 tests whether you can apply ATX methodology to a real business process **in a domain you may not know** — assessing how cognitive work actually flows, decomposing it into Jobs to be Done and zones, scoring delegation suitability, and producing an agent design that is honest about what it knows and what it doesn't.

Three things distinguish Gate 2 from Gate 1:

- **The scenario is partial.** You have a one-page brief plus 5 sample artefacts (a voicemail, an email thread, an SMS exchange, an SOP fragment, a system catalogue). Together they describe how the work happens — not in full, but in enough texture that you can reason about it.
- **The domain may be unfamiliar.** That's intentional. A working FDE handles unfamiliar domains every engagement. Use AI to orient yourself; surface what you don't know as discovery questions and assumptions.
- **You will defend live.** A coach plays the Main Stakeholder for ~10 minutes after the timed window. They will be impatient, sceptical, and will answer some questions precisely, others vaguely or contradictorily. Your job is to ask questions whose answers would materially change your design — and to detect when you're being deflected.

---

## 2. How to run the 3 hours

A rough shape that has worked in test runs; adapt as you like.

- **0–25 min — AI-accelerated domain orientation.** Use Claude / Dial / Cursor to build working models of the relevant industry, the cognitive workflows you're about to map, the typical failure modes, and the system landscape. This is a budgeted activity, not procrastination.
- **25–55 min — Read the scenario brief and the 5 artefacts twice.** Note what's stated, what's implied, what's missing. List your unknowns before you start producing.
- **55–110 min — Cognitive Load Map (Deliverable 1) + Delegation Suitability Matrix (Deliverable 2).** These are the substantive ATX outputs.
- **110–140 min — Volume × Value Analysis (Deliverable 3) + Agent Purpose Document (Deliverable 4).** Identify which work stream wins; design the agent for it.
- **140–165 min — System/Data Inventory (Deliverable 5) + Discovery Questions (Deliverable 6).**
- **165–180 min — `CLAUDE.md` (Deliverable 7) + final pass.** Hunt for "everything is fully agentic" drift, undefined zones, integration vagueness, assumptions not marked as assumptions.

Near-pass is a fail. A delegation matrix that's 90% justified and 10% defaulted to "fully agentic" reads the same to a coach as a matrix that's 60% justified — because the parts that matter are the parts being assessed.

---

## 3. Scenario

> **Apex Distribution Ltd** — Birmingham, UK. Regional carrier serving the Midlands, South, and East England. 800 employees, 180 vehicles, ~3,500 deliveries/day across B2B and DTC parcels.
>
> Within the company, a **35-person "Customer Operations" function** handles four work streams that interlock and frequently cross-refer:
>
> - **Delivery exceptions** (~180/day): driver issues, refused deliveries, damages, missed delivery windows. Avg handling time 12 min/case. Dispatcher discretion drives most decisions.
> - **ETA inquiries** (~400/day): "where is my delivery?" Avg handling time 4 min/case. Mostly lookup-and-respond, with edge cases requiring driver call.
> - **Dispatch adjustments** (~90/day): mid-route changes — additional pickups, diversions, driver swaps. Avg handling time 18 min/case. Tight time pressure.
> - **Billing disputes** (~60/day): customer disputes a charge — fuel surcharge, redelivery fee, dimensional weight calculation. Avg handling time 28 min/case. Often crosses into the legacy billing system.
>
> **Tooling landscape:**
>
> - **Modern CRM** (Salesforce-based) — customer records, case history, communications. REST APIs available.
> - **Driver app** (in-house iOS/Android) — GPS, route, scan-on-delivery, driver-to-dispatch messaging.
> - **Dispatch console** (Java desktop, deployed via Citrix) — route planning, driver assignment, exception triage. Limited API surface.
> - **Legacy billing system ("Aurum Billing", on-prem Oracle, since 2008)** — invoicing, fuel surcharge calculation, customer credit handling. **Batch-file exports only**: daily 02:00–04:00 GMT to CSV; no real-time API; reconciliation file lags 24 hours behind invoice generation. Modifications to invoices require a manual ticket to the Aurum support team (typical turnaround 48 hours).
>
> **The COO, Sarah Whitmore**, was promoted internally 18 months ago after 5 years running the dispatch team. She wants to "put AI on this." She has watched two prior automation initiatives fail (a 2024 customer chatbot that customers hated; an RPA project for billing reconciliation that broke whenever Aurum's schema changed). Her CEO recently heard about a competitor saving £1.2M annualised on customer service using AI; he asked her to "look into it." She is sceptical of chatbots and sceptical of consultants, but open to something that actually works.
>
> **Design the agentic transformation of Customer Operations.**

That is the scenario. The 5 artefacts in Section 4 give you texture on how the work actually happens. If you need more than what is here, that is an assumption — name it as one in Deliverable 5.

---

## 4. Sample artefacts

### Artefact 1 — Driver voicemail to dispatch desk

*Wednesday, 14:37. Inbound to Birmingham dispatch line. Caller: Mark Petrov, route 042 (south-east cluster).*

> "Yeah, hi, it's Mark — Mark Petrov, route 042. Listen, I'm at the Cobham drop, the big one, the Stein-Allen account? They're saying they won't take it because the pallet's leaning, looks damaged on one corner, but to me it looks fine, it's just been on the lorry. The site manager isn't here, it's just the warehouse guy and he's new I think, he doesn't want to sign for it. I've got six more drops on this route. Do I — do I bring it back, do I leave it, what do you want me to do? I tried Sandra but her line was busy. Call me back, I'm parked up till you tell me. Cheers."

### Artefact 2 — Email thread, billing dispute

*Subject: RE: RE: RE: Disputed invoice INV-2026-04318. From customer (Hayes & Sons Ltd) to Apex billing@; 4 messages over 9 days.*

**Message 1 (customer → billing@, day 1, 09:14):**
> "Invoice INV-2026-04318 dated 14th. £340 fuel surcharge on a delivery that arrived damaged — pallet was unusable, we had to dispose of half the consignment. Please remove the surcharge and confirm credit. Thanks, Pete H."

**Message 2 (billing → customer, day 1, 16:48):**
> "Hi Pete, fuel surcharges are calculated automatically by route distance and aren't tied to delivery condition. For damage claims please contact Customer Operations on the number below, they handle goodwill credits. Regards, Aurum Billing Team."

**Message 3 (customer → billing@, day 4, 11:02):**
> "I called Customer Ops, was on hold for 22 minutes, got cut off. This is the second time you've billed full surcharge on a damaged consignment from us this quarter. Escalating — who is your manager?"

**Message 4 (Customer Ops agent → customer, day 6, 15:30):**
> "Hi Pete, sorry for the run-around. I've applied a £170 goodwill credit, you'll see it on your next statement. We're aware fuel surcharge can't be adjusted on individual invoices because of how Aurum works, so this is the best I can do. Sandra"

*Day 9: customer reply not yet shown in thread. Internal note (not visible to customer): no entry in the credits audit log for this £170; Sandra applied it via a manual override.*

### Artefact 3 — Customer ETA inquiry, SMS exchange

*Tuesday, 11:14. SMS thread between customer M.K. and Apex ETA inquiry line.*

> [11:14] **Customer:** Where is order #AX-771-3344?
> [11:16] **Apex agent:** Hi, let me check. Looks like it's out for delivery on route 028. ETA window is 13:00–17:00.
> [11:17] **Customer:** That's a 4 hour window, can you tell me anything more specific?
> [11:19] **Apex agent:** One moment, checking with dispatch.
> [11:24] **Apex agent:** Driver's last GPS ping was 10:48 in Watford. Best guess is your drop will be early afternoon, around 14:00–15:00. We don't have a tighter ETA than that — sorry.
> [11:25] **Customer:** OK, thanks.

### Artefact 4 — SOP fragment

*"Apex Customer Operations — Exception Handling SOP v2.3" (last revised October 2023). Excerpt from Section 4.*

> **4.2 Refused deliveries**
>
> When a recipient refuses a delivery, the driver should:
>
> 1. Note the reason for refusal on the **DispatchHub** tablet.
> 2. Confirm with **DispatchHub** whether to return-to-depot, hold, or re-attempt.
> 3. If the consignment is high-value (>£500), escalate to the Duty Manager via the dispatch console.
>
> **4.3 Damaged consignments**
>
> *[Section incomplete — "TBD pending review of insurance protocol" — no further content.]*
>
> **4.4 Unattended addresses**
>
> *[See Section 7.]*

*Footnote (added by the participant's coach in the artefact pack — not part of the SOP itself): DispatchHub was retired in October 2024 and replaced with the current Driver App. The SOP has not been updated since.*

### Artefact 5 — Aurum Billing batch export catalogue + sample exports

*Daily exports from Aurum Billing, written to `/exports/aurum/` between 02:00–04:00 GMT.*

```
APEX_BILL_DAILY_YYYYMMDD.csv          - invoices generated, T-1
APEX_FUEL_SURCH_YYYYMMDD.csv          - fuel surcharge line items, T-1
APEX_CREDITS_YYYYMMDD.csv             - manual credits applied, T-1
APEX_RECON_YYYYMMDD.csv               - reconciliation file, T-2 (24h lag)
APEX_DISPUTES_OPEN_YYYYMMDD.csv       - open disputes, T-1
APEX_AGED_RECEIVABLES_YYYYMMDD.csv    - aged receivables, weekly Friday
APEX_CUSTOMER_MASTER_YYYYMMDD.csv     - customer master extract, monthly first-of-month
```

**Sample exports for one weekday (2026-04-14):** open the `Gate2-Artefacts/` folder alongside this pack. Seven CSV files plus a brief README. These are illustrative excerpts showing the schema, real values, and cross-file consistency — not full daily volumes. Read them for the data shape, not for a full picture of Apex.

*No real-time API. No webhook from Aurum into other systems. Modifications to invoices require a manual ticket to the Aurum support team (typical turnaround 48 hours). Aurum schema changes happen ~quarterly without prior notice.*

---

## 5. Deliverables

Seven deliverables, all in one document. Any format that renders cleanly as text or markdown is fine. Length is not scored — precision is.

| # | Deliverable | Guidance |
|---|---|---|
| 1 | **Cognitive Load Map** | Decompose at least 2 of the 4 work streams into Jobs to be Done, micro-tasks, and cognitive dimensions. Map zones and breakpoints. The map must reflect *lived* work — what the artefacts and brief together imply — not what an SOP claims. |
| 2 | **Delegation Suitability Matrix** | Score each major task cluster on delegation dimensions; assign archetypes (fully agentic / agent-led with oversight / human-led with agent support / human-only) with rationale. Arbitrary assignments will be challenged. **"Everything is fully agentic" is the most-marked-down anti-pattern this week.** |
| 3 | **Volume × Value Analysis** | Plot the 4 work streams on volume × value axes. Identify the primary agentic target and justify why it wins. |
| 4 | **Agent Purpose Document** | For the highest-value opportunity: purpose, scope, KPIs, autonomy matrix, escalation triggers, failure modes. Precise enough that an AI coding agent could begin building from it. |
| 5 | **System/Data Inventory** | What the agent needs to access, what's available, what's missing, what's risky. The legacy billing system constraints are part of this — address them, don't hand-wave. Also state what assumptions you are making about systems the brief did not detail. |
| 6 | **Discovery questions for the Main Stakeholder** | Questions whose answers would *actually* change your design — not generic "tell me about your process" questions. **For a domain-naïve participant, this deliverable is the most direct signal of FDE judgment — invest accordingly.** |
| 7 | **`CLAUDE.md` for the project** | Demonstrates workflow discipline. See `../Reference/claude-md-examples-guide.md`. |

**Known gaps are better than hidden gaps.** If you do not have time to fully specify a part of your design, name it explicitly as a scope-out with a concrete plan to resolve. A senior FDE ships ATX outputs with known-and-labelled gaps under time pressure — silent omissions on delegation justification or system constraints do not earn the same read.

---

## 6. Live clarification round

After the timed exercise, each participant gets a ~10-minute clarification round with a coach playing the **Main Stakeholder** (Sarah Whitmore, COO).

Format may be **1:1 individual** or **small-group of 3 participants** — your coach team confirms the format ahead of the round.

Sarah will:

- Answer some questions precisely.
- Answer others vaguely ("I'd have to check," "It varies, honestly").
- Occasionally contradict an earlier answer if probed from a different angle.
- Sometimes redirect or counter-question rather than answer.
- **Not** volunteer information you didn't ask for.

Your job:

- Ask questions that would materially change your design.
- Detect evasion. Sarah is impatient and tends to answer plausibly even when she doesn't know — a strong participant catches her hedging and presses for honest uncertainty (e.g., "If you had to guess, what's a number you'd put on this — caveats fine?").
- Update cleanly. If a Sarah answer overturns one of your assumptions, name it and adjust on the spot.

This is a judgment test, not a presentation. Defending what you wrote is fine; refusing to update when challenged is not.

---

## 7. Evaluation criteria

This time evaluation rubric will not be shared.

---

## 8. What anti-patterns will cost you

Not exhaustive — but these are the failure modes coaches watch for closely.

**"Everything is fully agentic"**, **Documented-not-lived work**, **Bluffing domain knowledge.** , **Legacy system hand-wave.** T, **Generic discovery questions.**, **Vanishing dispatcher.** , **Filler assumptions.** 

---

## 9. Submission logistics

- **Format:** Markdown or plain text, one document containing all seven deliverables. Headings per deliverable (1 through 7) so the coach can navigate.
- **Filename:** `Gate2-<First Name>-<Last Name>.md`
- **Where to submit:** General Channel / Gate 2 Submissions Folder (link posted in Teams General channel at gate release).
- **Deadline:** 12:00 CET (3 hours from release at 09:00). Late submissions are flagged and handled separately as negotiated with the coach; partial submissions are accepted and scored on what is present.
- **Live round scheduling:** Your slot is on the shared afternoon schedule posted alongside this pack. Slots run between 15:30 and 17:30 CET.

If something goes wrong — tooling failure, system outage, lost work — contact your squad lead immediately. Do not rebuild silently past the deadline.

---

## 10. A final framing

You are not being asked to fix Customer Operations. You are being asked to produce an ATX-shaped assessment that makes the *real* work legible — honest about what's lived versus documented, defensible about which delegation archetypes the parts of the work fit, and explicit about what you don't yet know.

Near-pass is a fail. Write the assessment you would stand behind in front of Sarah after she's already burned by two failed projects.

Good luck.
