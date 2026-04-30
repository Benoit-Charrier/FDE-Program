# Helix Negotiation Playbook — v3.4
# Last updated: [STALE — DPDI Act Q1 updates NOT yet incorporated]
# Owner: Amelia Forsythe (GC)
#
# IMPORTANT: This version does not reflect the DPDI Act Q1 updates
# (legitimate interests test, data subject access changes).
# All DPA clause classifications against this playbook must be flagged
# to Tom for review. Amelia to update before agent deployment against DPA clauses.

---

## LIABILITY_CAP

**Standard Position:**
Vendor liability to Helix must be capped at no less than 12 months of fees paid
under the agreement or £250,000, whichever is greater.

**COMPLIANT:** Liability cap ≥ £250,000 OR ≥ 12 months of contract value.
**MINOR_DEVIATION:** Liability cap is between £125,001 and £249,999, or between 6 and 11 months of fees. Acceptable with redline to raise to standard floor.
**MAJOR_DEVIATION:** Liability cap is below £125,000 (>50% below floor) or below 6 months of fees. Requires senior lawyer review before negotiation.

Carve-outs: mutual unlimited liability for fraud, death/personal injury, and data protection breaches is standard; do not accept one-sided unlimited liability for Helix only.

---

## DATA_PROCESSING_AGREEMENT

**Standard Position (UK GDPR / DPA 2018 — v3.4):**
- Controller/processor delineation must be clear; Helix is typically controller.
- Sub-processor list must be provided and approved in writing before engagement.
- Data residency: UK/EEA preferred; adequacy decision required for third-country transfers; SCC fallback acceptable with Annex.
- Breach notification: 72-hour notification to Helix; 24-hour internal SLA.
- Data retention and deletion: confirm deletion within 30 days of contract end.
- Data subject access: vendor must cooperate with DSAR requests within 5 business days.

**COMPLIANT:** All the above elements present and consistent with UK GDPR / DPA 2018.
**MINOR_DEVIATION:** One element missing or slightly out of position (e.g., 48-hour breach notification vs. 72-hour; UK/EEA only data residency without SCC fallback). Paralegal can redline.
**MAJOR_DEVIATION:** Controller/processor relationship inverted; no sub-processor list; no data residency restriction; no breach notification clause. Senior lawyer required.

**[NOTE — DPDI ACT GAP]:** DPDI Act Q1 updates (legitimate interests test changes, data subject access changes) are NOT reflected in this version. All DPA classifications must be flagged to Tom until Amelia updates this section.

---

## TERMINATION_CLAUSE

**Standard Position:**
- Either party may terminate for convenience with 30 days' written notice.
- Immediate termination for material breach; 14-day cure period for non-material breach.
- Auto-renewal: maximum 12-month auto-renewal with 60-day opt-out window.

**COMPLIANT:** Termination notice ≤ 30 days for convenience; cure period present; auto-renewal ≤ 12 months.
**MINOR_DEVIATION:** Termination notice 31–90 days, or auto-renewal 13–24 months, or cure period 15–30 days. Paralegal can redline to standard position.
**MAJOR_DEVIATION:** Termination notice > 90 days, or perpetual auto-renewal with no opt-out, or no termination for convenience right. Senior lawyer required.

---

## IP_OWNERSHIP

**Standard Position:**
- All pre-existing IP remains with the originating party (background IP).
- Work product created solely by vendor for Helix under this agreement: Helix owns it.
- Joint development: joint ownership with licensing rights for each party.
- No assignment of Helix's IP to vendor under any circumstance.
- Source code escrow required for software deliverables.

**COMPLIANT:** Background IP protected; Helix owns bespoke deliverables; no Helix IP assigned to vendor.
**MINOR_DEVIATION:** Work product ownership ambiguous (e.g., "vendor grants licence" instead of "assigns ownership"). Paralegal can redline to assignment language.
**MAJOR_DEVIATION:** Vendor claims ownership of work product; Helix IP assigned or licensed exclusively to vendor; no escrow for software. Senior lawyer required.
**REQUIRES_SENIOR_REVIEW:** Joint IP development without clearly defined licensing terms; open-source licensing implications for Helix's proprietary software.

---

## SLA_COMMITMENTS

**Standard Position:**
- System uptime: ≥ 99.5% monthly (excluding scheduled maintenance with 48h notice).
- Critical issue response: < 4 hours; critical resolution: < 24 hours.
- Standard issue response: < 1 business day; resolution: < 5 business days.
- Service credits: ≥ 10% monthly fee for each 0.5% below uptime SLA; vendor may not cap total credits below 15% of monthly fees.

**COMPLIANT:** Uptime ≥ 99.5%; response times at or below standard; service credits ≥ 10% per 0.5% downtime.
**MINOR_DEVIATION:** Uptime 99.0%–99.4%, or response time up to 8 hours for critical, or service credits 5%–9%. Paralegal can redline.
**MAJOR_DEVIATION:** Uptime < 99.0%, or no SLA at all, or service credits < 5% or capped below 10% of monthly fees. Senior lawyer required.

---

## GOVERNING_LAW

**Standard Position:**
- English law governs the agreement.
- Disputes: English courts have exclusive jurisdiction (High Court of Justice, England & Wales).
- ADR: 30-day good-faith negotiation before litigation; optional mediation clause acceptable.

**COMPLIANT:** English law; English courts exclusive jurisdiction.
**MINOR_DEVIATION:** English law with non-exclusive jurisdiction, or English law with mandatory arbitration under LCIA or ICC rules. Paralegal can redline to exclusive jurisdiction.
**MAJOR_DEVIATION:** Non-English governing law (e.g., New York law, Delaware law, EU member state law). Senior lawyer required to assess enforceability impact.
**REQUIRES_SENIOR_REVIEW:** Conflict of laws provisions; international arbitration with seat outside England; governing law of a jurisdiction with data localisation requirements.

---

## INDEMNITY_SCOPE

**Standard Position:**
- Mutual indemnification for: (a) third-party IP infringement claims arising from vendor's deliverables; (b) vendor's gross negligence or wilful misconduct; (c) vendor's data protection breaches.
- Helix indemnifies vendor only for: (a) use of Helix-supplied materials in violation of vendor's instructions; (b) Helix's own gross negligence.
- Indemnity cap: aligned with the liability cap (12 months fees or £250,000, whichever greater).
- No uncapped indemnity obligations on Helix without senior lawyer sign-off.

**COMPLIANT:** Mutual indemnity as above; cap aligned with liability cap; no one-sided uncapped obligations.
**MINOR_DEVIATION:** Indemnity scope slightly broader than standard (e.g., includes ordinary negligence rather than gross negligence). Paralegal can redline to gross negligence threshold.
**MAJOR_DEVIATION:** One-sided uncapped indemnity obligations on Helix; indemnity for Helix covering vendor's IP decisions; indemnity cap below liability cap. Senior lawyer required.
