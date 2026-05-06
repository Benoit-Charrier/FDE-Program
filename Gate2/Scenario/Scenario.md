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
