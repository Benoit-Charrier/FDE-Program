# Apex Distribution Ltd — Customer Operations: ATX Scenario Context

*Full scenario and artefacts in `Scenario/Scenario.md` and `Scenario/Gate2-Artefacts/`. This file is the single-source-of-truth scenario summary for use across all prompt templates.*

---

## Table of contents

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

**Apex Distribution Ltd — Agentic Transformation Assessment of Customer Operations**

*Full artefacts and background in `Scenario/Scenario.md` and `Scenario/Gate2-Artefacts/`. This file is the single-source-of-truth scenario summary for use across all prompt templates.*

---

## 2. The company

**Apex Distribution Ltd** is a regional parcel carrier headquartered in Birmingham, UK. The company employs 800 people, operates 180 vehicles, and handles approximately 3,500 deliveries per day across a network covering the Midlands, South, and East England. Its business model is B2B and direct-to-consumer (DTC) parcel delivery. No revenue, ARR, or growth rate figures are stated in the scenario.

---

## 3. The team

**Team:** Customer Operations — 35 people.

Named individuals:

- **Sarah Whitmore** — COO. Promoted internally 18 months ago after 5 years running the dispatch team. Commissioned this assessment following a CEO request prompted by a competitor saving £1.2M annualised on customer service using AI. Sceptical of chatbots and of consultants; open to something that demonstrably works.
- **Sandra W.** — Customer Operations agent. Handles billing disputes and delivery exceptions. Appears in Artefact 2 (email thread) and in the open disputes export (assigned to 3 of 6 open disputes including all FUEL_SURCH_DAMAGE cases).
- **Tom J.** — Customer Operations agent. Appears in the open disputes export assigned to DIM_WEIGHT dispute types.

Generic roles: the remaining 32 team members are not individually named. The scenario describes four work streams handled by the 35-person team; no headcount split per work stream is stated.

---

## 4. The process

**Core process:** Customer Operations handles four interlocking work streams — delivery exceptions, ETA inquiries, dispatch adjustments, and billing disputes — totalling approximately 730 cases per day across the team of 35.

**Governing policy:** "Apex Customer Operations — Exception Handling SOP v2.3" (last revised October 2023). **Status: stale.** The SOP references DispatchHub, which was retired in October 2024 and replaced with the current Driver App. The SOP has not been updated since. Section 4.3 (Damaged consignments) is explicitly incomplete — marked "TBD pending review of insurance protocol" with no further content.

**Triage / routing logic:** Not formally stated in the scenario. From the artefacts, exception decisions are driven by dispatcher discretion (Artefact 1: driver waits for a call-back from dispatch to determine how to proceed). Billing disputes are assigned to named agents (Artefact 5: disputes carry an ASSIGNED_TO field). No percentage splits or tier routing rules are stated.

**Turnaround targets:** No formal SLA or turnaround target is stated in the scenario for any work stream. The billing dispute artefact (Artefact 2) spans 9 days with a 22-minute on-hold incident, suggesting no enforced response SLA is currently operating.

**Hard rules and constraints:**

- **Billing system modification rule (owned by Aurum Billing / Aurum support team):** Modifications to invoices require a manual ticket to the Aurum support team. Typical turnaround: 48 hours. This is a non-negotiable constraint imposed by the external system.
- **Batch data constraint (owned by Aurum Billing):** No real-time API. Data exports run daily 02:00–04:00 GMT to CSV. Reconciliation file lags 24 hours behind invoice generation. Schema changes happen approximately quarterly without prior notice.
- **High-value consignment escalation rule (owned by Customer Operations SOP):** SOP Section 4.2 states consignments valued above £500 must be escalated to the Duty Manager via the dispatch console. Consistency of application is not confirmed — this is a documented rule, not a confirmed operational practice.
- **Prior automation failure context:** Two prior initiatives have failed: a 2024 customer chatbot (customer rejection) and an RPA project for billing reconciliation (broke on Aurum schema changes). The COO is aware of both failures and they constrain stakeholder appetite for any new automation initiative.

---

## 5. The work streams

| # | Work stream | Volume (daily, as stated) | Time/case |
|---|-------------|--------------------------|-----------|
| WS1 | Delivery exceptions | ~180/day | Avg 12 min/case |
| WS2 | ETA inquiries | ~400/day | Avg 4 min/case |
| WS3 | Dispatch adjustments | ~90/day | Avg 18 min/case |
| WS4 | Billing disputes | ~60/day | Avg 28 min/case |

- **WS1 — Delivery exceptions:** Driver issues, refused deliveries, damages, and missed delivery windows requiring dispatcher intervention; decisions are currently discretion-driven with dispatcher call-back as the primary mechanism.
- **WS2 — ETA inquiries:** "Where is my delivery?" inquiries; primarily lookup-and-respond against route and GPS data, with edge cases requiring a direct call to the driver for a tighter estimate.
- **WS3 — Dispatch adjustments:** Mid-route changes including additional pickups, diversions, and driver swaps; handled under time pressure with decisions affecting downstream drops on the same route.
- **WS4 — Billing disputes:** Customer disputes over charges (fuel surcharges, redelivery fees, dimensional weight calculations); resolution is constrained by the Aurum batch-only architecture and the 48-hour manual ticket turnaround for invoice modifications.

---

## 6. Tooling

- **Salesforce-based CRM** — customer records, case history, customer communications. REST APIs confirmed as available.
- **Driver App (in-house, iOS/Android)** — GPS location, route data, scan-on-delivery, driver-to-dispatch messaging. Replaced DispatchHub in October 2024.
- **Dispatch console (Java desktop, deployed via Citrix)** — route planning, driver assignment, exception triage. Limited API surface (the scenario states "limited API surface" — specific capabilities are not defined).
- **Aurum Billing (on-prem Oracle, in production since 2008)** — invoicing, fuel surcharge calculation, customer credit handling. Batch-file exports only: seven CSV file types, daily 02:00–04:00 GMT (except aged receivables: weekly Friday; customer master: monthly first-of-month). No real-time API. No webhook. Reconciliation file lags 24 hours behind invoice generation. Invoice modifications require a manual ticket to the Aurum support team (typical turnaround 48 hours). Schema changes occur approximately quarterly without prior notice.

> **Named systems note:** Salesforce-based CRM, Driver App (in-house iOS/Android), Dispatch console (Java/Citrix), and Aurum Billing (on-prem Oracle) are confirmed in the scenario — treat them as facts, not assumptions. Any additional system introduced in subsequent deliverables must be labelled as an assumption. Specific API capabilities, rate limits, and integration maturity beyond what is stated in the scenario (e.g., the exact endpoints available on the CRM REST API, the specific data fields exposed by the Driver App, or the internal schema of the dispatch console) are assumptions and must be labelled as such.

---

## 7. Key artefacts

- **Artefact 1 — Driver voicemail, delivery exception (Mark Petrov, route 042, 14:37):** A driver phones dispatch from a refused/disputed delivery at the Stein-Allen account (Cobham drop), asking whether to return-to-depot, leave the consignment, or wait. He has six more drops on the route and is parked waiting for a call-back. This reveals that exception decisions are dispatcher-discretion-driven and communicated verbally in real time; the driver cannot proceed without human instruction; and there is no structured intake mechanism — the exception arrives as an unstructured voicemail.

- **Artefact 2 — Billing dispute email thread (Hayes & Sons Ltd, INV-2026-04318, 9 days):** A customer disputes a £340 fuel surcharge on a damaged delivery. The thread spans 9 days, includes a 22-minute on-hold incident, and is resolved with a £170 goodwill credit applied by Sandra via manual override. An internal note states there is no entry in the credits audit log for this credit. This reveals three constraints: (1) the billing system cannot adjust individual fuel surcharge line items — Aurum calculates them automatically; (2) credits are applied informally, bypassing the audit trail that the APEX_CREDITS export schema formally supports; (3) the "best Sandra can do" is a partial goodwill credit, not a correct invoice adjustment.

- **Artefact 3 — ETA inquiry SMS exchange (order AX-771-3344, Tuesday 11:14):** A customer asks for delivery status; the agent retrieves route and GPS data, provides a 4-hour window, then checks with dispatch for a tighter estimate (5-minute gap between messages). This reveals that ETA inquiries are largely lookup-and-respond but the last-GPS-ping data (10:48 in Watford at 11:14) is already 26 minutes stale at the time of the response, and achieving a tighter estimate requires a human dispatch consultation step.

- **Artefact 4 — SOP fragment (v2.3, October 2023):** Section 4.3 (Damaged consignments) is explicitly incomplete — "TBD pending review of insurance protocol." The SOP references DispatchHub (retired October 2024 and replaced by the Driver App) and has not been updated since. This reveals a critical gap: the highest-judgment exception type (damaged consignments) has no documented procedure, and the SOP references a system that no longer exists — meaning any agent built from the documented process would be built on a broken foundation.

- **Artefact 5 — Aurum batch export catalogue and sample CSVs:** Seven CSV file types with defined schema. The APEX_CREDITS export includes APPROVER_ID and AUDIT_REF columns, confirming the schema formally supports an audit trail — but Artefact 2 shows that informal credits bypass this schema entirely. The APEX_DISPUTES_OPEN export shows customer C-04451 (Hayes & Sons) with 3 open disputes, all assigned to Sandra W., all of type FUEL_SURCH_DAMAGE — suggesting a repeat-disputer pattern that is not being resolved systematically. The APEX_RECON export shows a 24-hour additional lag vs. invoice data, and flags open disputes as DISPUTE_OPEN in the reconciliation file.

---

## 8. Assumption log

> **Assumption A-1:** The ~730 daily cases (180 + 400 + 90 + 60) represent the full scope of Customer Operations workload. No other work streams are implied by the scenario.
> **Why it matters:** Scopes the automation opportunity and ROI model. If additional work streams exist, the total addressable volume is higher.
> **If wrong:** If there are additional work streams not listed (e.g., complaints escalation, proactive outreach), the agent scope would need to expand.
> **Confidence:** Medium — the scenario explicitly states "four work streams" but may not capture informal or overflow work.

> **Assumption A-2:** The 35-person Customer Operations team handles all four work streams without a formal headcount split per work stream.
> **Why it matters:** Affects staffing displacement estimates and any capacity modelling in D3.
> **If wrong:** If the team is formally partitioned (e.g., a dedicated billing team of 8), automation ROI calculations and delegation scope would need to reflect that split.
> **Confidence:** Medium — the scenario describes the team as handling "four work streams that interlock and frequently cross-refer," implying a shared pool, but does not confirm this.

> **Assumption A-3:** Sandra's £170 goodwill credit (Artefact 2) was applied outside the formal credits process — not captured in APEX_CREDITS_20260414.csv — meaning the audit gap is active and ongoing, not historical.
> **Why it matters:** If the audit gap is confirmed as ongoing, it is a compliance risk that must be addressed in the agent design (the agent cannot inherit this behaviour). If it was a one-off, the risk is lower.
> **If wrong:** If Sandra's credit does appear in a later credits export under a different date or reference, the audit trail gap may be narrower than the artefact suggests.
> **Confidence:** Medium — the internal note states "no entry in the credits audit log for this £170," which is unambiguous, but the sample data covers only one day.

> **Assumption A-4:** "Limited API surface" on the dispatch console (Java/Citrix) means programmatic read/write access to dispatch data is not reliably available without custom integration work.
> **Why it matters:** Determines whether dispatch adjustment automation is technically feasible within the assessment scope, or whether it requires a system integration investment as a prerequisite.
> **If wrong:** If the dispatch console exposes more API surface than the scenario implies (e.g., undocumented REST endpoints), dispatch adjustment automation becomes more directly achievable.
> **Confidence:** Medium — "limited API surface" is stated in the scenario; what "limited" means in practice must be confirmed in discovery.
