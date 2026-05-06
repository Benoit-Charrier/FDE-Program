# Gate 2 — Artefact 5 sample exports

Sample contents from `/exports/aurum/` — one weekday's batch run (2026-04-14, except where the file's natural cadence dictates a different date per the catalogue in §4 of `../Gate2-Participant-Pack.md`).

These are illustrative excerpts, not full daily volumes. Real exports run hundreds of rows per file. Use these to reason about schema shape, cross-file consistency, and the constraints the legacy billing system imposes on agentic design.

## Files

| File | Cadence | Notes |
|---|---|---|
| `APEX_BILL_DAILY_20260414.csv` | T-1 daily | Invoice header data |
| `APEX_FUEL_SURCH_20260414.csv` | T-1 daily | Surcharge line items linked to invoices via INVOICE_NO |
| `APEX_CREDITS_20260414.csv` | T-1 daily | Manual credits with APPROVER_ID and AUDIT_REF |
| `APEX_RECON_20260413.csv` | T-2 daily | Reconciliation against received payments — note the 24h additional lag vs invoice generation |
| `APEX_DISPUTES_OPEN_20260414.csv` | T-1 daily | Open dispute snapshot — point-in-time, not transactional |
| `APEX_AGED_RECEIVABLES_20260410.csv` | Weekly Friday | Customer ageing buckets — most recent Friday before exercise date |
| `APEX_CUSTOMER_MASTER_20260401.csv` | Monthly 1st-of-month | Reference data — note last refresh date relative to your exercise date |

The catalogue in §4 of the participant pack lists the same files. These exports are CSV-only — no real-time API, no webhook from Aurum into other systems. Modifications to invoices require a manual ticket to the Aurum support team. Schema changes happen ~quarterly without prior notice.
