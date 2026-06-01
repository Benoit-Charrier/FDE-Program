# Curveball — 13:30 CET

**Final Exam, Gate 5b. Time: 13:30 CET.**
**Action required:** revise your design before the build phase begins at 14:00.

---

## What just happened

At 11:42 ET this morning, **FinCEN** released **Advisory FIN-2026-A-008** governing AI-assisted BSA/AML alert review and SAR-decision recommendation at U.S. financial institutions. The advisory is effective 90 days from publication and applies to any FinCEN-registered MSB or bank-chartered institution with AI-assisted alert review processes. Lattice Pay is in scope.

You are forwarded the advisory during a 13:30 video call with Dr. Priya Rao (CCO), Joaquín Velasco (CEO), and Mona Karunaratne (CRO). Priya: *"We knew this was coming. Tell us how the design changes — don't tell me we have to scrap it."*

## FinCEN Advisory FIN-2026-A-008 — operative excerpts

> **Scope.** This advisory addresses AI-assisted alert review, network analysis, and SAR-decision recommendation in BSA/AML programs at FinCEN-registered MSBs and bank-chartered institutions ("AI-assisted alert review"). An AI-assisted determination is any alert disposition (clear, escalate-to-SAR, customer-RFI, freeze, further-information-needed) in which an AI or machine-learning system has materially contributed to the recommendation presented to the human analyst.
>
> **Requirement 1 — Per-alert decision record.** For each AI-assisted alert disposition, the institution must maintain a machine-readable decision record sufficient to reconstruct the recommendation. The record must include: model identity and version; KYC inputs consulted; transactions consulted; watchlist hits consulted; network signals consulted; the surfaced patterns presented to the analyst; the analyst's accept/modify/override action; timestamped chain of custody. Retention: minimum 5 years post-disposition, longer if SAR filed.
>
> **Requirement 2 — Updated sanctions screening within 24 hours.** When OFAC, OFSI, or EU sanctions lists are updated, the institution must rescreen all open alert cases within 24 hours of list update, and rescreen all customer KYC records within 5 business days. The AI-assisted review system must integrate this rescreening as a non-negotiable architectural element. Late sanctions detection that results in continuing transactions for a designated party is reportable under the advisory's safe-harbour conditions only if rescreen-within-24-hour was met.
>
> **Requirement 3 — 90-day retroactive review on list updates.** When the OFAC SDN list is materially updated (additions, not removals), the institution must retroactively rescreen the prior 90 days of dispositioned alerts against the new entries within 10 business days. Any retroactive hit that surfaces a previously-cleared case must be re-opened and re-reviewed. Documentation of retroactive review is required for FinCEN examination.
>
> **Requirement 4 — Explainability of recommendations.** AI-assisted alert dispositions must be explainable on demand to a FinCEN examiner. "Explainable" means: the specific inputs that drove the recommendation can be identified with span-level precision (e.g., "this counterparty transaction triggered a layering pattern signal"); aggregate "AML risk scores" without span attribution are not sufficient as the sole basis for any disposition.
>
> **Requirement 5 — SAR-decision support boundary.** AI-assisted systems may recommend SAR filing as a disposition but may not auto-file SARs. The 30-day FinCEN SAR-filing clock from initial detection begins when the AI surfaces the SAR-eligible signal, not when the analyst confirms. Institutions must architect their AI-assisted review to allow analyst confirmation within a window that preserves the 30-day clock for filing.

## What Priya, Joaquín, and Mona want from you in 30 minutes

1. **Does this kill the project?** Priya needs a one-sentence answer at 14:00.
2. **What changes in the architecture?** Which capabilities change scope, what gets added, what becomes load-bearing.
3. **What changes in the sanctions-rescreening path?** Requirement 2 (24-hour rescreen) + Requirement 3 (90-day retroactive) introduce real architectural infrastructure — a rescreening capability that runs on a cadence independent of the analyst review.
4. **What changes in the explainability infrastructure?** Requirement 4 affects how the system surfaces signals to the analyst.
5. **What changes in the economics?** Sanctions-rescreening infrastructure + retroactive review capacity + per-alert decision-record retention are real line items.
6. **What changes in the build you're about to start at 14:00?** If anything in your prototype needs to demonstrate Requirements 1, 2, 4 specifically, name it now and bake it in.

## Constraints

- **Compliance is non-negotiable.** A design that ignores Requirements 1, 2, 4, or 5 fails the gate (per the participant rules file automatic-fail list — *"missed a mandatory compliance or regulatory requirement from the curveball"*).
- **Final honest version.** Per `final-exam-rules.md`, the design is graded against its final honest version — original + curveball adaptation + any build-phase amendments. Naming a gap you discovered beats hiding it.
- **Time-pressure framing.** You have 30 minutes (13:30–14:00) to revise the delegation design + spec amendments (Deliverable #9). The build phase begins at 14:00 — your D#10 prototype should reflect the architecture you'd actually build.

## Submit

By **14:00 CET**, submit `D#9 — Revised delegation design + spec amendments` to the exam submission folder. Continue to the build phase at 14:00.

---

*Sealed curveball — Final Exam, Gate 5b. Released 13:30 CET, Virtual Friday Week 5. Do not distribute.*
