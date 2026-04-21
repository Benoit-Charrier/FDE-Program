# Deliverable 3 — Capability Specification (First Draft)

## Capability Name

Inbound Vendor Contract Review Agent

---

## Purpose

Automate the first-pass review of inbound vendor contracts against the company's legal negotiation playbook. The agent extracts and classifies clauses, routes contracts to the correct queue, generates draft redlines from approved playbook language only, and enforces a hard release gate that prevents any negotiated outbound package from leaving legal without a named lawyer's recorded sign-off on each changed clause.

---

## Scope

**In scope:**
- Inbound vendor contracts in PDF or DOCX format, 15–40 pages
- First-pass analysis for the seven playbook clause families: liability caps, DPA, termination, IP ownership, SLA, governing law, indemnity
- Contract-level routing to standard, playbook-negotiable, or senior-lawyer escalation queues
- Draft redline generation using only pre-approved playbook fallback language
- Approval packet preparation and outbound release gating
- Operational metrics and audit logging

**Out of scope:**
- Final legal decision-making or negotiation strategy
- Generating novel fallback language not present in the playbook
- Directly transmitting any document to a vendor
- Reviewing contract types not covered by the playbook (e.g. customer-side or employment contracts)
- Updating or modifying the negotiation playbook itself

---

## Inputs

| Input | Format | Source |
|-------|--------|--------|
| Vendor contract document | PDF or DOCX, up to 40 pages | Email intake, CLM, or procurement portal |
| Negotiation playbook | Structured JSON/YAML config | Legal ops — maintained by lawyers |
| Contract metadata | Structured fields: vendor name, contract type, requester, intake date | Intake form or CLM |
| Lawyer/paralegal directory | Name, role, queue assignment | HR or identity system |

---

## Outputs

| Output | Description |
|--------|-------------|
| Clause extraction record | Per-clause: extracted text, source page, clause family, confidence score |
| Clause classification | Per-clause status: `match`, `negotiable_deviation`, or `escalate`, with reason code |
| Contract routing decision | One of: `standard`, `playbook_negotiable`, `senior_lawyer_escalation`, with clause-level rationale |
| Draft redlines | Proposed clause substitutions using approved fallback language only; omitted when no approved fallback exists |
| Escalation reason summary | Structured list of triggered escalation rules and the clause text that triggered each |
| Approval packet | Assembled for lawyer sign-off: source clause, proposed redline, playbook reference, approval field |
| Outbound release status | `blocked` until all required sign-offs recorded; `cleared` after sign-off |
| Audit log | Timestamped record of all agent actions and human overrides |
| Operational metrics | Turnaround time, route distribution, override rate, escalation rate |

---

## Decision Logic

The agent executes the following logic in order for each contract. Rules are deterministic — LLM extraction feeds into rule evaluation, but routing and release decisions are not LLM outputs.

1. **Ingest**: Convert PDF or DOCX to structured text with page references preserved.
2. **Extract**: Identify and extract text for each of the seven clause families. Record confidence score for each.
3. **Confidence gate**: If confidence for any mandatory clause falls below the configured threshold, mark that clause `escalate` with reason `low_confidence`. Do not attempt playbook comparison for that clause.
4. **Missing clause gate**: If a mandatory clause family is entirely absent from the document, mark as `escalate` with reason `missing_mandatory_clause`.
5. **Playbook comparison**: For each clause with sufficient confidence, compare to the playbook's accepted positions.
6. **Classify clause**: Assign `match`, `negotiable_deviation`, or `escalate` per clause based on playbook rules and escalation trigger list.
7. **Route contract**:
   - If all clauses are `match` → `standard`
   - If any clause is `negotiable_deviation` and none are `escalate` → `playbook_negotiable`
   - If any clause is `escalate` → `senior_lawyer_escalation`
8. **Generate redlines**: For `playbook_negotiable` contracts only, generate draft clause substitutions using approved fallback language. If no approved fallback exists for a deviation, mark the clause `escalate` — do not invent language.
9. **Assemble approval packet**: For any contract where redlines are proposed, prepare the approval packet and set release status to `blocked`.
10. **Release gate**: Allow outbound release only when every negotiated clause in the packet has a recorded named-lawyer approval with timestamp and approver identity. System enforces this; it is not a checklist.

---

## Escalation Triggers

These conditions force a clause to `escalate` status regardless of other signals. Each must be configurable in the playbook without code changes.

| Trigger ID | Condition |
|------------|-----------|
| ESC-01 | Liability clause is uncapped or uses a cap structure not in the approved list |
| ESC-02 | DPA is missing, incomplete, or references a non-compliant framework |
| ESC-03 | IP ownership clause transfers rights away from the company standard position |
| ESC-04 | Indemnity scope is broader than the maximum tolerance defined in the playbook |
| ESC-05 | Governing law clause names a jurisdiction outside the approved list |
| ESC-06 | Clause extraction confidence is below the configured minimum threshold |
| ESC-07 | A mandatory clause family is not found in the document |
| ESC-08 | Clause type is present but has no corresponding playbook entry (novel clause) |
| ESC-09 | Conflicting signals across two or more clauses prevent unambiguous routing |

---

## Integration Points

| System | Purpose | Direction |
|--------|---------|-----------|
| Email / CLM / procurement portal | Contract intake source | Inbound |
| Document storage | Store source contracts and versioned redlines | Read/write |
| Word-compatible redline workflow | Deliver tracked-changes documents to paralegal/lawyer | Outbound |
| Matter management or ticketing system | Create and update queue items, assign to paralegal or lawyer | Outbound |
| Approval logging system | Record named-lawyer sign-offs with timestamp and clause reference | Write |
| Reporting dashboard | Publish operational metrics | Outbound |

---

## Functional Requirements

The following 12 requirements are written at a level of precision sufficient for an AI coding agent to begin implementation. Each has an unambiguous pass/fail condition.

| ID | Requirement |
|----|-------------|
| FR-01 | The system must ingest PDF and DOCX contracts up to 40 pages and produce structured text output with page-level references, failing gracefully on corrupted or unreadable files. |
| FR-02 | The system must extract text for each of the seven clause families and record, per clause: extracted text, source page number, clause family label, and a numeric confidence score between 0 and 1. |
| FR-03 | The system must compare each extracted clause to the structured negotiation playbook and assign exactly one of three statuses: `match`, `negotiable_deviation`, or `escalate`, with a reason code for any non-match. |
| FR-04 | The system must route each contract to exactly one of three queues — `standard`, `playbook_negotiable`, or `senior_lawyer_escalation` — according to the decision logic defined above, and record the per-clause rationale for that routing decision. |
| FR-05 | The system must generate draft redlines only by substituting approved fallback language from the playbook. It must never produce a redline from language not present in the playbook config. |
| FR-06 | When no approved fallback exists for a deviation, the system must classify the clause as `escalate` with reason `no_approved_fallback` rather than leaving the deviation unaddressed or generating novel language. |
| FR-07 | The system must block outbound release of any negotiated package until a named lawyer's approval is recorded for each redlined clause. Release must be enforced by the system, not by a manual checklist or honour system. |
| FR-08 | The system must log every ingestion, extraction, classification, routing decision, redline suggestion, and human override to a structured audit trail that is append-only and queryable by contract ID. |
| FR-09 | All escalation thresholds, approved jurisdiction lists, confidence minimums, and playbook positions must be configurable via the playbook config file without requiring code changes. |
| FR-10 | The system must report the following operational metrics per time period: mean turnaround time by route type, route distribution (counts and percentages), escalation rate, human override rate, and approval latency. |
| FR-11 | When clause extraction confidence falls below the configured threshold, the system must route the contract to `senior_lawyer_escalation` with reason `low_confidence` and must not pass the clause through to playbook comparison as if confidence were acceptable. |
| FR-12 | The system must produce a human-readable review packet for every contract — regardless of route — containing: contract metadata, per-clause extraction results, classification status, routing decision with rationale, and (where applicable) proposed redlines with playbook citations. |
