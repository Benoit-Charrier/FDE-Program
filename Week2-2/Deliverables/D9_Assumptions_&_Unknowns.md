# D9 — Assumptions & Unknowns
**Agent:** Clause Classification Agent (CCA)
**Scenario:** Helix Workforce Software — Vendor Contract Clause Review

---

## 1. Consolidated Assumption Register

Pulled from D0A, D0B, D1, D2, D3, D4, and D5. Duplicates consolidated; source deliverable noted for each entry.

| ID | Assumption | Source | Category | Why it matters | If wrong | Confidence |
|----|-----------|--------|----------|----------------|----------|------------|
| A-01 | Current clause classification accuracy is approximately 85% — no measured baseline exists; inferred from the fact that borderline cases generate informal "will ask Sarah" escalations that are not tracked as errors | D0A [A1] | problem definition | Sets the baseline against which the ≥90% accuracy KPI is judged. If baseline is already 92%, the agent's accuracy target is modest. If baseline is 75%, the target is demanding. | The accuracy improvement narrative in the business case is calibrated incorrectly in either direction. | Low |
| A-02 | Inbound contract volume grows proportionally with Helix's 25% YoY revenue growth, reaching ~375 contracts/quarter within 12 months | D0A [A4] | organisation | Drives the capacity urgency case — the "≥400 contracts/quarter without headcount increase" target depends on this growth rate holding. | If enterprise deals are larger and fewer, volume growth lags revenue growth; the primary business justification shifts entirely to turnaround improvement, not throughput. | Medium |
| A-03 | Ironclad supports per-case timestamping at work-stream level (triage-open → classification-saved; contract-received → outbound-response) with sufficient granularity to measure the D0A time-based KPIs | D0A [A3] | systems | Four of the six D0A success metrics depend on Ironclad timestamps. Without this, measurement requires a separate instrumentation layer — additional build scope. | KPI measurement mechanism requires redesign; turnaround improvement cannot be demonstrated to the CRO without alternative data capture. | Medium |
| A-04 | The Helix playbook in SharePoint is structured as bullet-point criteria per clause type (consistent with Artefact 2.3) and can be directly indexed for RAG without a pre-processing reformatting step | D0B [U-2], D5 | data | Determines RAG pipeline complexity. A semi-structured bullet-point format can be chunked by clause type and indexed with standard embedding. A narrative Word document or multi-version fragmented playbook requires substantial pre-processing. | RAG pipeline scope increases significantly; retrieval quality may require additional validation; engineering timeline extends. | Medium — confirmed for the DPA section (Artefact 2.3) but not for all 7 clause type sections. |
| A-05 | Ironclad's case record schema can be extended with approximately 35 custom fields (5 per clause type × 7 clause types: match status, extracted text, playbook version, confidence score, deviation magnitude) to receive the agent's structured classification output | D4 T-12, D5 [G-4] | systems | T-12 cannot write classification outputs to Ironclad without confirmed custom fields. If the field schema cannot be extended, the agent's outputs have nowhere to land in the system of record, blocking the entire downstream C-7 package preparation pipeline. | Agent write layer must be redesigned around a secondary data store (SharePoint JSON file or external database) — higher engineering complexity, weaker audit trail, and no native Ironclad workflow integration. | Low — Ironclad supports custom fields as a platform capability but field availability for this tenant and the schema design have not been confirmed. |
| A-06 | A HITL notification channel — either Ironclad-native workflow task creation or a structured Outlook email to a dedicated legal inbox — is available and configurable before deployment | D5 [G-1] | systems | The entire HITL design depends on a confirmed delivery channel. Tom cannot review flagged cases if the agent has no reliable way to route an ET-1 through ET-6 payload to him. This is the most immediately blocking gap in D5. | Agent can classify but cannot deliver HITL payloads; the confidence-gate design is inoperable; every contract effectively routes autonomously even when it should not. | Low — mechanism not named in the scenario; both candidate implementations require configuration work before build can be finalised. |
| A-07 | A structured DPDI Act reference document summarising the Q1 legitimate interests test and data subject access changes will be produced by Amelia before deployment — either a 1–2 page internal briefing or the ICO's published guidance | D4 [ET-2], D5 [G-2] | data | Without this document, T-09 DPA assessment cannot detect specific DPDI applicability signals beyond keyword matching. ET-2 fires but the flag payload says "DPDI update pending" rather than identifying specific DPDI-affected provisions in the vendor's clause. The quality of Tom's and Amelia's review degrades materially. | DPA HITL flags are advisory rather than diagnostic; Amelia must review more cases herself to compensate for low-quality flagging; the compliance protection from ET-2 is present but weaker than designed. | Low — document does not exist (Artefact 2.3: "on a sticky note on Amelia's desk"). |
| A-08 | The clause heading patterns for the 7 clause types across the vendor population can be curated into a working taxonomy from 20–50 historical contracts before deployment, producing sufficient coverage to keep false-absence rates at acceptable levels | D5 [G-3] | data | T-04 clause location accuracy is a direct function of taxonomy coverage. If the vendor population's heading naming conventions are more diverse than a sample of 50 captures, false-absence rates (FM-3 in D4) will be higher than the design assumes — and Tom will receive more "clause not found" HITL items than expected. | HITL rate rises above the ≤35% target in early production; Tom's queue is heavier than projected; clause location accuracy requires a longer production warm-up period than estimated. | Low — no historical contracts have been reviewed; diversity of heading patterns is unknown. |
| A-09 | Borderline triage cases — where the negotiable/escalation boundary is genuinely ambiguous — represent approximately 5–10% of all contracts (above the 10% formal escalation rate but below a materially higher threshold) | D1 [MT5 footnote], D3 | problem definition | Drives the HITL rate projection. The 30% deviation path (20% negotiable + 10% escalation) already targets a ≤35% HITL rate. If borderline cases consistently require ET-1 or ET-5 flags in addition to the structural deviation flags, the HITL rate may structurally exceed 35% and the coverage KPI (≥65% autonomous) becomes unachievable. | HITL rate exceeds target; Tom's queue is materially heavier than projected; coverage KPI fails in the first quarter of production without a threshold recalibration. | Low — inferred from "borderline" language in Artefact 2.1; no data on frequency. |
| A-10 | The TCO payback period of approximately 17 months is based on a UK paralegal fully-loaded hourly rate of £75 and a commercial lawyer rate of £100 | D3 (TCO section) | problem definition | If actual rates are materially higher, the business case strengthens and payback shortens. If rates are lower, payback extends — though the 3-year ROI remains positive in either direction within a 30% variance band. | TCO analysis does not materially affect the build decision at plausible variance ranges; primarily affects the CFO-level business case presentation. | Low — no salary data in the scenario. |

---

## 2. Genuine Unknowns

Things not resolvable by reading the scenario. Each has a specific consequence if unresolved and a specific validation method.

---

> **Unknown [U-1]: Whether the Ironclad `routing_classification` field is a constrained enum or a free-text string — and which role types have write access to it**
> **Category:** systems
> **Why it matters for the build:** The agent writes `routing_classification` to Ironclad at T-12. If the field is a constrained enum (e.g., `STANDARD | NEGOTIABLE | ESCALATION_REQUIRED`), the write is validated at the API level — the agent cannot write an invalid value and the system rejects attempts to bypass the classification logic. If it is free-text, invalid values write silently and the classification logic must be enforced entirely in the agent's own code without system-level backstop. Additionally: if non-lawyer roles (including the agent) have write access to `lawyer_signoff_name` or `approval_token`, the GC's hard rule can be bypassed — an architectural risk that can only be confirmed by examining Ironclad's role-based access configuration.
> **Consequence if unresolved:** Build proceeds on the assumption that the field is constrained and that the agent's credentials do not have write access to signoff fields. If wrong at production: invalid routing values may be written silently; or the sign-off bypass risk is live and undetected until an audit.
> **How to validate:** Ask the Ironclad admin: "Show me the field type and role-permission configuration for `routing_classification`, `lawyer_signoff_name`, and `approval_token` in the contract record schema. Which roles can write each field?"
> **When to validate:** Before build starts

---

> **Unknown [U-2]: Whether Ironclad's current case record captures historical escalation data in a queryable form — by vendor name and escalation status — with consistent vendor name normalisation**
> **Category:** systems / data
> **Why it matters for the build:** ET-6 (vendor history escalation check) queries Ironclad for prior escalation-required cases for the same vendor. This requires: (a) historical case records exist in Ironclad with `routing_classification` populated, (b) the records are queryable by vendor name as a filter, and (c) vendor names are normalised consistently across cases. If Ironclad was adopted recently or contracts were managed in SharePoint/email before adoption, the historical data may be sparse or absent. If vendor names are inconsistently entered (free-text field with no normalisation), the ET-6 query produces false negatives regardless of fuzzy matching threshold.
> **Consequence if unresolved:** ET-6 is implemented but fires rarely due to data gaps; QF-1 (the vendor name variant quiet failure from D8) is more prevalent than estimated; the historical escalation advisory is a false-positive-safe but low-recall feature in production.
> **How to validate:** Ask the Ironclad admin: "Pull a list of contract records from the last two years with their vendor names and routing outcomes. How many have a routing_classification populated? Are vendor names free-text entry, or controlled by a vendor registry?" A sample of 20 records reveals data quality quickly.
> **When to validate:** Before build starts

---

> **Unknown [U-3]: Whether the named-lawyer sign-off on a counteroffer is currently captured in any auditable system record — and if not, what mechanism would create an `approval_token` before the CCA's downstream C-7 pipeline could execute dispatch**
> **Category:** systems / organisation
> **Why it matters for the build:** The CCA's hard stop HS-5 requires the agent to never simulate or record a sign-off token, and the downstream C-8 dispatch check requires `approval_token` to be non-null before any counteroffer leaves Legal's queue. The agent's data model assumes a named lawyer can set `approval_token` in Ironclad. If sign-off currently happens via an Outlook reply or verbal instruction with no Ironclad record, the `approval_token` field has no corresponding real-world mechanism — the field would always be null, and the hard stop would block every downstream dispatch indefinitely. In that scenario, the sign-off workflow itself must be redesigned (a lawyer clicks "Approve" in Ironclad to set the field) before the CCA goes live.
> **Consequence if unresolved:** The CCA's core governance constraint cannot be technically enforced. The hard stop design is sound, but the system has no mechanism for a lawyer to satisfy it. Deploying without this resolved means the sign-off gate is a policy rule, not a system constraint — precisely the gap the GC's hard rule was designed to close.
> **How to validate:** Ask Amelia: "If a counteroffer was sent to a vendor and six months later there was a dispute about who authorised that specific redline, where would I find the documented record of the approval?" If she cannot point to a specific Ironclad entry, the audit gap is confirmed and the approval mechanism must be built as part of the CCA deployment, not assumed.
> **When to validate:** Before build starts

---

> **Unknown [U-4]: What Tom's actual decision logic is for contracts with mixed clause-level results — specifically, whether one escalation-required clause escalates the entire contract or only the flagged clause proceeds to WS3 while others proceed to WS2**
> **Category:** problem definition
> **Why it matters for the build:** The CCA's `aggregate_routing_classification()` function must implement this logic. D4's precedence rule (ESCALATION_REQUIRED > NEGOTIABLE > STANDARD) assumes the most severe clause determines the contract-level routing — meaning one MAJOR_DEVIATION clause escalates the entire contract. If Tom's actual practice is "route only the flagged clause to WS3 and the rest to WS2 in parallel," the agent's routing output, its Ironclad field writes, and the downstream work stream handoff design are all wrong. The two implementations have different data models: one ReviewDecision per contract (D4/CLAUDE.md) versus one routing decision per flagged clause.
> **Consequence if unresolved:** The most prevalent failure mode is neither a crash nor a hard stop — it is the agent routing an entire contract to WS3 when Tom would have split it, creating unnecessary senior-lawyer review load. Less commonly: routing the whole contract to WS2 when it should have been split, causing a clause that should have gone to WS3 to be redlined by Tom instead.
> **How to validate:** Walk Tom through two or three past contracts with mixed clause-level results and ask him to narrate his routing decision. Ask specifically: "If a contract has four standard clauses, one negotiable deviation, and one that needs escalation — what do you route to WS3? Just the escalated clause, or the whole contract?"
> **When to validate:** Before build starts

---

> **Unknown [U-5]: Whether the playbook contains explicit numeric deviation thresholds for each of the 7 clause types — i.e., values that distinguish MINOR_DEVIATION from MAJOR_DEVIATION — or only position statements (the target) without a defined tolerance band**
> **Category:** data
> **Why it matters for the build:** The CLAUDE.md classification thresholds (COMPLIANT ≥ 0.85 similarity, MINOR_DEVIATION 0.60–0.84, MAJOR_DEVIATION < 0.60) are labelled as assumptions in CLAUDE.md §3 and in D4 §3. For numeric clause types (LIABILITY_CAP, SLA_COMMITMENTS), the playbook's Artefact 2.3 shows a floor value (£250,000 / 12 months) but does not show a "minor deviation" band (e.g., £125,001–£249,999) or a "major deviation" threshold (< £125,000). If these thresholds are absent, the agent cannot reliably distinguish MINOR_DEVIATION from MAJOR_DEVIATION on numeric clauses — it applies the semantic similarity fallback, which is less precise for numeric values. The entire routing split (20% negotiable vs. 10% escalation) depends on this threshold being codifiable.
> **Consequence if unresolved:** Build uses assumed numeric thresholds (50% of floor = major deviation, derived from Artefact 2.1 analysis). If the actual thresholds differ materially, the 20/10 routing split shifts — more contracts route to WS3 than expected (false escalation) or fewer route there (missed escalations). C-3's delegation archetype (Human-led + Agent Support) is justified precisely because these thresholds are currently tacit; if they are codified in the playbook, C-3 can move to Agent-led + Human Oversight without an architectural change.
> **How to validate:** Ask Amelia: "For each of the 7 clause types in the playbook, is there a documented threshold below which Tom should always escalate rather than redline? For the liability cap specifically — if a vendor proposes £100,000 instead of £250,000, is that automatically escalation-required or is it still negotiable?" Review the full playbook, not just the DPA section shown in Artefact 2.3.
> **When to validate:** Before build starts — if thresholds are codified, the CLAUDE.md classification rules can be updated before build and the agent's decision logic is more precise from day one.

---

## 3. Validation Priority Matrix

| Tier | Criteria | Items |
|------|----------|-------|
| **Must validate before build starts** | If wrong, the core architecture changes — data model, delegation archetype, integration point, or primary output target would need redesign | A-05 (Ironclad custom field schema), A-06 (HITL notification channel), U-1 (Ironclad field types and role permissions), U-3 (sign-off mechanism auditability), U-4 (Tom's mixed-result routing logic), U-5 (numeric deviation thresholds in playbook) |
| **Must validate before first production contract** | If wrong, the agent produces incorrect output in production but the architecture is sound — a configuration, threshold, or workflow change fixes it | A-04 (playbook machine-readable format), A-07 (DPDI Act reference document), A-08 (clause heading taxonomy coverage from historical contracts), U-2 (Ironclad historical escalation data quality) |
| **Can defer to v2** | If wrong, the agent is suboptimal or the business case framing shifts — not a compliance failure or a routing error | A-01 (baseline accuracy measurement), A-02 (volume growth rate), A-09 (borderline case frequency), A-10 (paralegal and lawyer hourly rates for TCO) |

**Tier 1 rationale:** A-05 and A-06 together block the entire write and HITL layers — without them, the agent has no place to record its outputs and no way to route flagged cases to Tom. U-3 determines whether the sign-off hard stop is technically enforceable or just a policy aspiration. U-4 determines the data model (one ReviewDecision per contract vs. per clause). U-5 determines whether the CLAUDE.md classification thresholds can be replaced with real numeric bands or must remain assumptions.

**Tier 2 rationale:** The architecture can be finalised without knowing the exact playbook format or DPDI document state — the RAG pipeline design can absorb format variation, and the DPA HITL flag works without the reference document (it just fires a lower-quality advisory). These affect output quality, not system viability.

**Tier 3 rationale:** Baseline accuracy, growth rate, and hourly rates affect how we report on success and how we frame the business case. None of them change what the agent does or how it is built.

---

## 4. Top 3 Unknowns — Risk Summary

---

**U-3 — Sign-off mechanism: does a machine-settable `approval_token` field exist in Ironclad?**

The CCA is being built on the assumption that a named lawyer can set an `approval_token` field in Ironclad, and that the agent reads this field before any downstream dispatch proceeds. Every line of code enforcing the GC's hard rule — HS-5, HS-8 in CLAUDE.md, the `assert_no_send_redline_without_approval_token()` hard stop, the `approval_token = null` invariant on ReviewDecision creation — assumes this mechanism exists.

If it resolves the other way — sign-off is currently an Outlook reply or a verbal instruction with no Ironclad record — two different builds are needed. Version A (current design): a sign-off token field is present or can be added; the agent reads it; the hard stop enforces a real constraint. Version B (no sign-off mechanism): the CCA deployment must include creating an Ironclad approval workflow as part of its scope — a lawyer-role "Approve" button that sets the field — before any downstream dispatch automation is viable. Version B is more scope and more organisational change than Version A.

The two builds share the agent's classification layer entirely. They diverge at the ReviewDecision model and the downstream C-7 integration. Designing Version A is faster; designing for Version A when Version B is the reality means rebuilding the C-7 dispatch integration and the ReviewDecision state machine after the first production deployment. This is the highest-consequence unknown in the build.

---

**A-05 — Ironclad per-clause classification field schema: can 35 custom fields be configured?**

The agent writes 5 structured fields per clause type × 7 clause types = 35 field writes per contract to Ironclad. The C-7 package preparation agent reads those same fields to assemble the sign-off package. The entire downstream pipeline depends on these fields existing.

If they can be configured (standard Ironclad customisation): the build proceeds as designed. If they cannot — either because the tenant licence does not support this level of customisation, or because adding 35 fields requires an Ironclad professional services engagement that is not budgeted or scheduled — the write layer must be redesigned around a secondary data store. The most viable alternative is a structured JSON blob written to a SharePoint document library, with the C-7 agent reading from SharePoint rather than Ironclad. This creates a secondary system of record that is not natively accessible via Ironclad's CLM workflows, weakens the audit trail, and increases integration complexity for every downstream agent in the programme.

The two builds are architecturally similar in the classification layer and diverge at T-12. The SharePoint fallback is buildable, but it adds an integration point and breaks the "Ironclad as single source of truth" design principle that the entire compounding infrastructure (D5 §6) relies on.

---

**A-06 — HITL notification channel: Ironclad workflow vs. Outlook email**

Every escalation trigger in the CCA requires routing a structured payload to Tom's review queue. The design assumes a reliable, auditable channel. Two candidate channels exist: Ironclad-native workflow task creation (preferred — native audit trail, status tracking, SLA visibility) and Outlook email to a dedicated legal inbox (simpler to build, harder to audit).

If Ironclad-native workflow is available and configurable: the CCA integrates with the existing CLM; Tom's review queue is an Ironclad task list; approval decisions are logged as Ironclad events with timestamps. The entire process — from ET trigger to Tom's approval — is visible in the same system as the contract record.

If only Outlook is available: the CCA sends a structured email to a shared inbox; Tom reviews by email; his approval is an email reply that may or may not be parsed back into Ironclad. The audit trail gap (D5 Risk Register: HITL via Outlook creates an audit gap between agent flag and Tom's approval) is live from day one. The D0B Unknown U-4 about whether sign-off decisions are currently auditable becomes compounded — not only is the sign-off mechanism unclear, but the HITL review mechanism also lacks an audit trail.

The two builds share the ET evaluation logic and the HITLPayload data model. They diverge at the delivery layer. Switching from Outlook to Ironclad-native after go-live requires rebuilding the HITL routing module and retroactively importing Outlook-based approvals into Ironclad. Design for the Ironclad path from the start; confirm availability in discovery.

---

## 5. Assumption Log

> **Assumption [A-L1]:** The aggregation rule — ESCALATION_REQUIRED overrides NEGOTIABLE overrides STANDARD — reflects Tom's actual contract-level routing practice, not just a defensible design choice. The playbook does not state this rule explicitly; it is inferred from the 10% escalation rate (if escalation-required contracts routed clause-by-clause, the denominator would be 2,100 clauses, not 300 contracts).
> **Why it matters:** The `aggregate_routing_classification()` function in `src/aggregator.py` implements this rule as a hard precedence. If Tom's actual practice is to route only the escalated clause rather than the entire contract, every multi-clause contract with one escalated and several standard clauses is over-escalated — senior lawyer time is consumed on cases where only one clause requires escalation.
> **If wrong:** HITL rate appears correct in aggregate (30% of contracts) but the nature of WS3 cases changes — more total clauses in WS3 with lower per-clause severity on average; senior lawyer capacity consumed by mixed contracts rather than pure escalation cases.
> **Confidence:** Low — this is the U-4 unknown above. Tom must be walked through a mixed-result contract before this assumption is locked in the data model.

> **Assumption [A-L2]:** The confidence threshold of 0.85 — the point above which the agent routes autonomously and below which ET-1 fires — is calibrated correctly for the actual distribution of clause classifications in the Helix vendor population. The 0.85 value is derived from D4 §3 KPIs and is marked as an assumption in CLAUDE.md §3.
> **Why it matters:** The autonomous coverage KPI (≥65%) depends on the threshold being set at a level where at least 65% of contracts pass without triggering ET-1. If the actual distribution of agent confidence scores for this vendor population clusters below 0.85 (because vendor drafting styles are more diverse than the model was designed for), the autonomous rate falls below 65% and the throughput case collapses.
> **If wrong:** In the short direction (threshold too high): HITL rate exceeds 35%; Tom is overwhelmed with low-value flags; coverage KPI fails; threshold must be recalibrated downward. In the tall direction (threshold too low): agent routes borderline cases autonomously; Tom's override rate rises above 10%; accuracy KPI fails; threshold must be recalibrated upward. Both failures are detectable within the first quarter via the monitoring checks defined in D8 §1.
> **Confidence:** Low — stated explicitly as an assumption in CLAUDE.md §3. Calibration data does not exist until the agent has run against a set of real Helix vendor contracts and Tom's overrides are measured.

---

## Summary — main 3 points

1. **Three assumptions are architectural, not analytical — A-05 (Ironclad custom fields), A-06 (HITL notification channel), and U-3 (sign-off mechanism) — and all three must be confirmed before build begins.** Each one controls a structural layer of the agent: the write layer, the HITL delivery layer, and the governance enforcement layer. Building any of them against an unconfirmed assumption means redesigning that layer post-facto when the assumption fails in integration testing.

2. **The DPDI Act deployment gate (A-07) is the only assumption whose failure is not recoverable at build time — it is a compliance risk that materialises in production on every DPA clause processed.** The playbook staleness is a confirmed fact; the DPDI reference document is a confirmed gap. Unlike the architectural assumptions above, this one cannot be fixed with a code change after go-live — it requires Amelia to produce content that does not currently exist. The deployment gate is non-negotiable.

3. **Four of the ten assumptions have "Low" confidence and sit in Tier 1 or Tier 2 of the validation matrix — meaning the build is proceeding with significant uncertainty in its most load-bearing design decisions.** This is not unusual for an early-stage agent design, but it means the discovery phase is genuinely load-bearing rather than confirmatory. The six questions that would resolve Tier 1 unknowns (field types in Ironclad, sign-off mechanism, Tom's routing logic, playbook threshold codification, HITL channel, custom field schema) can all be answered in two conversations: one with Amelia and one with the Ironclad admin.
