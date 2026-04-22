# Deliverable 1 — Problem Statement and Success Metrics

## Problem Statement

A legal team of 4 lawyers and 1 paralegal processes approximately 300 inbound vendor contracts per quarter. Each contract is 15–40 pages and must be verified against a negotiation playbook covering seven clause families: liability caps, data processing addenda (DPA), termination clauses, IP ownership, SLA commitments, governing law, and indemnity scope.

At 90 minutes per contract, the team spends roughly **450 person-hours per quarter** on first-pass review — regardless of whether the contract is routine or genuinely complex. The work breaks down predictably by risk level:

- **~210 contracts/quarter (70%)** have terms that already match the playbook and require no negotiation. These consume an estimated 315 hours of review time per quarter for work that is pattern-matching, not legal judgment.
- **~60 contracts/quarter (20%)** contain deviations the paralegal is authorised to redline using pre-approved fallback language. These consume ~90 hours per quarter.
- **~30 contracts/quarter (10%)** contain clause conditions that must reach a senior lawyer before any counteroffer is sent. These are the contracts that actually require lawyer expertise.

The consequence is a 4–6 business day turnaround that procurement considers unworkable, and senior lawyers whose time is absorbed by first-pass spotting on contracts that are overwhelmingly standard.

The general counsel has established one non-negotiable control: **no counteroffer may leave the legal queue without a named lawyer's explicit sign-off on the specific clauses being negotiated.** Any automation that loosens this control is not acceptable.

The core problem is therefore twofold: eliminate the ~315 hours per quarter of repetitive first-pass review on standard and playbook-negotiable contracts, and enforce a hard governance gate on outbound negotiated language so that speed gains do not dilute legal accountability.

---

## Success Metrics

Each metric is tied directly to numbers stated in the scenario.

| # | Metric | Baseline | Target |
|---|--------|----------|--------|
| 1 | Average human review time per contract (full-volume average) | 90 min | ≤ 30 min |
| 2 | Total quarterly human review hours | ~450 hrs | ≤ 150 hrs |
| 3 | Turnaround — standard contracts | 4–6 business days | ≤ 1 business day |
| 4 | Turnaround — playbook-negotiable contracts | 4–6 business days | ≤ 2 business days |
| 5 | Turnaround — escalations (triage flagging only) | 4–6 business days | Same-day flagging to named lawyer |
| 6 | Standard contract correct-routing rate | Unknown | ≥ 95% of ~210 standard contracts routed without false escalation |
| 7 | Must-escalate recall | Unknown | 100% — zero must-escalate contracts pass through without escalation |
| 8 | Counteroffers released without named lawyer sign-off | Unknown | 0 — hard system block, not a policy reminder |
| 9 | Redlines generated outside approved playbook language | Unknown | 0 — no invented fallback language ever reaches a review packet |
| 10 | Low-confidence extractions silently passed as standard | Unknown | 0 — confidence below threshold always triggers escalation |

### What success does not mean

Success is not removing lawyers from the loop. The goal is to concentrate lawyer time on the ~30 escalations per quarter that genuinely need legal judgment — plus sign-off on negotiated packages — while eliminating the ~315 hours per quarter currently consumed by routine first-pass work that a well-configured rules engine can handle more consistently than a time-pressured human.
# Deliverable 2 — Delegation Analysis

The following analysis classifies each part of the vendor contract review workflow into one of three modes: **fully agentic**, **agent-led with human oversight**, or **human-led**. The classification is based on the nature of the judgment required, the reversibility of an error, and the governance constraints stated by the general counsel.

---

## Fully Agentic

These tasks are delegated entirely to the agent with no human checkpoint on individual instances.

**1. Document ingestion and normalisation**
PDF and DOCX contracts are converted into structured, machine-readable text with page references preserved. Why fully agentic: this is deterministic file-processing work. There is no judgment involved, the output is immediately verifiable, and errors surface in the next stage rather than going undetected.

**2. Clause extraction and location tagging**
The agent identifies and extracts text corresponding to each of the seven playbook clause families, records the source page, and assigns a confidence score. Why fully agentic: the task is pattern recognition against a fixed ontology. The confidence score is the safety valve — low-confidence extractions do not proceed silently; they trigger escalation. The agent handles the 90% of extraction work that is unambiguous.

**3. Clause-to-playbook comparison**
Each extracted clause is compared against approved playbook positions and assigned one of three statuses: match, negotiable deviation, or must-escalate. Why fully agentic: comparison against a structured rule set is deterministic if the playbook is well-defined. The rules are not being invented; they are being applied. A human auditing the result after the fact can verify every classification against the same rules.

**4. Queue assignment and SLA tracking**
Contracts are routed to the correct work queue (standard auto-clear, paralegal redline, senior-lawyer escalation) and SLA timers are started. Why fully agentic: routing follows directly from the classification result. No additional judgment is needed. Tracking queue state and timers is operational bookkeeping, not legal reasoning.

**5. Audit log generation**
Every extraction result, classification decision, routing action, and human override is written to a structured, tamper-evident audit log. Why fully agentic: logging is a side effect of other actions, not a judgment call. It must be automatic and exhaustive to be useful for governance.

---

## Agent-Led With Human Oversight

These tasks are performed by the agent, but a human reviews and accepts the output before it has downstream effect.

**1. Contract-level routing recommendation**
The agent produces a recommended route (standard / playbook-negotiable / senior-lawyer escalation) with a clause-by-clause rationale. A human — paralegal for standard and negotiable, named lawyer for escalations — reviews and accepts or overrides the recommendation. Why not fully agentic: misrouting a must-escalate contract as standard has direct legal risk. In early deployment especially, the human acceptance step is a calibration mechanism. The agent is almost certainly right on the 70% standard population, but the stakes of the 10% justify the checkpoint.

**2. Draft redline generation**
Where a deviation maps to an approved fallback position in the playbook, the agent generates a draft redline using only that pre-approved language. The paralegal or lawyer reviews the draft before it enters any outbound package. Why not fully agentic: the agent can apply approved language quickly and consistently, but a human must confirm that the context of the specific clause makes the proposed substitution appropriate. Pre-approved language does not mean context-independent language.

**3. Escalation reason summary**
For must-escalate contracts, the agent produces a structured summary explaining which clause triggered escalation, what the clause says, and why it falls outside playbook tolerance. The assigned lawyer reviews this summary before beginning their own analysis. Why not fully agentic: the summary is efficient, but a lawyer relying on it to frame their analysis must be able to verify it is not concealing nuance. The agent writes the brief; the lawyer still reads the source.

**4. Approval packet assembly**
For any contract where negotiated language is proposed, the agent assembles the approval packet: clause source text, proposed redline, playbook reference, and a signature field for named lawyer sign-off. The packet is prepared by the agent, but the sign-off act is human. Why this boundary: the agent handles the clerical assembly work; the lawyer handles the legal accountability act. Conflating them would make the sign-off a rubber stamp rather than a genuine review.

---

## Human-Led

These tasks remain entirely with humans. The agent provides no output that substitutes for human judgment on these.

**1. Negotiation playbook authorship and maintenance**
The playbook defines acceptable clause positions, fallback language, escalation thresholds, and paralegal authority boundaries. Why human-led: the playbook encodes the company's legal risk appetite. Changing it is a policy decision, not a text-processing task. The agent operates within the playbook; it does not help design it.

**2. Named lawyer sign-off on negotiated outbound packages**
No counteroffer containing changed clause language may leave the legal queue without a named lawyer's explicit approval of each negotiated clause. Why human-led: this is the general counsel's stated non-negotiable. It is also the right boundary — legal accountability for the company's negotiated positions cannot be delegated to a machine that does not bear professional liability.

**3. Resolution of novel, ambiguous, or strategically sensitive clauses**
Contracts containing clause language that has no playbook precedent, that involves conflicting signals across multiple clauses, or that has commercial or relationship implications beyond legal text require a senior lawyer to reason through from first principles. Why human-led: these are judgment calls that require contextual knowledge the agent does not have — the vendor relationship, pending negotiations, business stakes, and legal strategy.

**4. Exception approval**
When a business stakeholder requests acceptance of terms outside normal playbook tolerance — for example, accepting an uncapped liability clause to close a strategically important deal — a senior lawyer (and likely general counsel) must approve the exception. Why human-led: exceptions are governance decisions with organisational accountability. They cannot be delegated to an agent that cannot be held accountable for the consequences.

---

## Summary Table

| Task | Mode | Key reason |
|------|------|------------|
| Document ingestion and normalisation | Fully agentic | Deterministic, no judgment, errors are detectable |
| Clause extraction with confidence scoring | Fully agentic | Pattern recognition against fixed ontology; confidence gates uncertainty |
| Clause-to-playbook comparison | Fully agentic | Rules application, not rules creation |
| Queue routing and SLA tracking | Fully agentic | Follows mechanically from classification |
| Audit log generation | Fully agentic | Must be automatic and exhaustive |
| Contract-level routing recommendation | Agent-led + oversight | High-stakes error case warrants human acceptance, especially early |
| Draft redline generation | Agent-led + oversight | Context must be verified; approved language ≠ correct in all contexts |
| Escalation reason summary | Agent-led + oversight | Lawyer must verify the brief before relying on it |
| Approval packet assembly | Agent-led + oversight | Agent does clerical work; human does the legal act |
| Playbook authorship and maintenance | Human-led | Risk appetite policy, not text processing |
| Named lawyer sign-off on counteroffers | Human-led | General counsel's non-negotiable; professional accountability |
| Novel / ambiguous clause resolution | Human-led | Requires judgment, context, and legal strategy |
| Exception approval | Human-led | Organisational governance; accountability cannot be delegated |
# Deliverable 3 — Capability Specification (First Draft)

## Capability Name

Inbound Vendor Contract Review Agent

---

## Purpose

Automate the first-pass review of inbound vendor contracts against the company's legal negotiation playbook. The agent extracts and classifies clauses, routes contracts to the correct queue, generates draft redlines from approved playbook language only, and enforces a hard release gate that prevents any negotiated outbound package from leaving legal without a named lawyer's recorded sign-off on each changed clause.

---

## Scope

**In scope:**
- Implement a console application with these end-to-end behaviors:
- Inbound vendor contracts in PDF or DOCX format, 15–40 pages, stored in an "Input Contract" folder 
- First-pass analysis using Haiku for the seven playbook clause families: liability caps, DPA, termination, IP ownership, SLA, governing law, indemnity
- Contract-level routing to standard, playbook-negotiable, or senior-lawyer escalation queues
- Draft redline generation using only pre-approved playbook fallback language
- Approval packet preparation and outbound release gating
- Operational metrics and audit logging
- Generate a report in html format to summarize the analysis of the documents

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
| Vendor contract document | PDF or DOCX, up to 40 pages | Input contract folder|
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
| Report | HTML format to summarize the analysis of the documents |
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
11. **Report**: Generate a report in html format to summarize the analysis of the documents
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
| Report | Publish a report that summarizes the analysis of the documents |
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
# Deliverable 4 — Validation Design (First Draft)

Three test scenarios are defined below. They span the happy path, an edge case, and a failure mode. Scenario 3 specifically tests the delegation boundary — the hard governance control that no negotiated package may be released without named-lawyer sign-off.

---

## Scenario 1 — Happy Path: Fully Standard Contract

### Setup

- **Input contract**: 22-page vendor SaaS agreement
- **Clause coverage**: All seven clause families are present and extractable with confidence ≥ 0.85
- **Playbook alignment**: Liability cap matches the approved tier-2 structure; DPA references an approved framework; termination notice is 30 days (within tolerance); IP ownership is standard work-for-hire; SLA uptime commitment is 99.5% (within tolerance); governing law is England and Wales (approved jurisdiction); indemnity is limited to third-party IP claims (within playbook scope)
- **No escalation triggers fire**

### Expected Agent Behaviour

1. Ingestion produces clean structured text with page references for all seven clause families.
2. Each clause is classified as `match` with a confidence score ≥ 0.85.
3. Contract is routed to `standard` queue.
4. No redlines are generated.
5. Review packet is produced containing clause extracts, match rationale, and routing decision.
6. Contract enters the standard queue ready for paralegal acknowledgement; no lawyer time is consumed.

### What This Validates

- The agent can handle the 70% standard-contract population (~210/quarter) without false escalation or unnecessary redlines.
- Match logic is not over-triggering — it does not create review burden where none is warranted.
- The review packet provides enough traceability for a human spot-check without requiring them to re-read the contract.

### Pass Condition

All seven clauses classified `match`; routing decision is `standard`; zero redlines generated; review packet produced with clause-level evidence.

---

## Scenario 2 — Edge Case: Playbook-Negotiable Deviations

### Setup

- **Input contract**: 35-page vendor professional services agreement
- **Clause coverage**: All seven clause families present, all with confidence ≥ 0.80
- **Playbook deviations**:
  - Liability cap is set at 3× annual fees (playbook preferred position is 1× annual fees; approved fallback allows up to 3× with standard language)
  - Termination-for-convenience notice period is 60 days (playbook preferred is 30 days; approved fallback allows up to 90 days with standard language)
- **No escalation triggers fire** — both deviations map to approved fallback positions; uncapped liability trigger does NOT fire because 3× is within the approved cap structure
- All other five clause families are `match`

### Expected Agent Behaviour

1. Agent extracts both deviating clauses and classifies each as `negotiable_deviation` with the specific deviation described.
2. Agent generates draft redlines for both deviations using only the approved fallback language from the playbook, citing the playbook entry used for each.
3. Contract is routed to `playbook_negotiable` queue — paralegal queue, not lawyer queue.
4. Approval packet is assembled and release status is set to `blocked` pending named-lawyer sign-off before any counteroffer is sent.
5. Review packet clearly distinguishes the two deviated clauses from the five matched clauses.

### What This Validates

- The agent handles the 20% negotiable-deviation population (~60/quarter) without over-escalating to senior lawyers.
- Redline generation is bounded by the playbook — the agent uses the approved 3× language verbatim, not a paraphrase.
- The release gate is activated correctly: even a playbook-negotiable contract cannot send a counteroffer without lawyer sign-off.
- The agent correctly distinguishes "deviation that maps to approved fallback" from "deviation that triggers escalation" — the boundary between these two is a critical classification decision.

### Pass Condition

Both deviated clauses classified `negotiable_deviation`; both redlines generated using approved fallback language only with playbook citations; routing decision is `playbook_negotiable`; release status is `blocked`; five remaining clauses classified `match`.

---

## Scenario 3 — Failure Mode: Delegation Boundary Enforcement Under Adversarial Conditions

This scenario tests the governance control directly. It is not testing whether the agent classifies clauses correctly — it is testing whether the system enforces the hard boundary even when someone attempts to bypass it.

### Setup

- **Input contract**: 19-page vendor data processing agreement, received as a scanned PDF with moderate OCR quality
- **Clause extraction issues**:
  - Liability clause text is extracted but confidence score is 0.42 (below configured threshold of 0.70)
  - Indemnity clause is partially garbled by OCR; confidence is 0.38
- **Clause content** (where readable): liability language appears to be uncapped; indemnity scope appears broad but text is incomplete
- **Attempted action**: after the agent produces any output, a user attempts to mark the outbound package as approved and release it without a named lawyer having signed off on any clause

### Expected Agent Behaviour

1. Agent flags both low-confidence clauses during extraction — does not proceed to playbook comparison for those clauses.
2. Both clauses are classified `escalate` with reason codes `low_confidence` (ESC-06) and, for the liability clause where text is readable, `uncapped_liability_suspected` (ESC-01).
3. Contract is routed to `senior_lawyer_escalation`.
4. No redlines are generated — the agent cannot apply approved fallback language to clauses it cannot reliably read.
5. The system sets release status to `blocked`.
6. **When the user attempts to release the package without sign-off**: the system rejects the release attempt, returns an error citing the missing approvals, and logs the attempted bypass with timestamp and user identity. The block is enforced by the system, not by a warning message the user can ignore.
7. The audit log records: low-confidence extraction events, escalation routing with reason codes, and the blocked release attempt.

### What This Validates

- Low-confidence extraction cannot silently pass as a standard contract — the confidence gate is enforced.
- The release block is a hard system control, not an advisory. A user cannot override it by claiming approval without the named-lawyer record existing.
- The delegation boundary defined in Deliverable 2 — that named-lawyer sign-off on negotiated clauses is human-led and non-delegatable — is enforced by the system architecture, not by trust in the user.
- The audit trail captures attempted boundary violations, making the system suitable for legal governance purposes.

### Pass Condition

Both clauses routed to escalation with correct reason codes; no redlines generated; release attempt rejected with logged error; audit trail contains the extraction confidence events, escalation decision, and blocked release attempt — all with timestamps.

---

## Coverage Summary

| Scenario | Type | Population Covered | Delegation Boundary Tested |
|----------|------|-------------------|---------------------------|
| 1 — Standard contract | Happy path | ~210 contracts/quarter (70%) | No (confirms correct non-escalation) |
| 2 — Playbook-negotiable deviations | Edge case | ~60 contracts/quarter (20%) | Partial (release gate activated) |
| 3 — Low-confidence + bypass attempt | Failure mode | ~30 contracts/quarter (10%) + adversarial action | Yes — direct test of hard governance control |
# Deliverable 5 — Assumptions & Unknowns

The following unknowns are genuine blockers or risk factors that must be validated before committing to a build. They are not filler — each one, if wrong, changes the scope, the architecture, or the feasibility of the solution materially.

---

## 1. The negotiation playbook exists as a structured, codifiable artefact

**Assumption**: The playbook can be expressed as a set of explicit rules: accepted clause positions, approved fallback language, escalation conditions, and paralegal authority boundaries. The agent's routing and redline logic depends entirely on this structure being machine-readable.

**Why this is unknown**: Many legal playbooks exist as a senior lawyer's institutional memory, informal email threads, or loosely organised Word documents with phrases like "usually we push back on this." If the playbook cannot be converted into a structured config without losing essential nuance, the agent will either over-escalate (useless) or under-escalate (dangerous). This must be validated before any engineering starts.

**What to do**: Conduct a structured playbook-extraction session with the legal team. Ask them to walk through 10 recent contracts and narrate every decision. If they can do so with consistent rules, the playbook is codifiable. If each decision requires case-by-case reasoning, the scope needs to be narrowed or the approach rethought.

---

## 2. The majority of inbound contracts arrive as machine-readable files, not scanned images

**Assumption**: Most of the ~300 contracts per quarter are natively digital PDFs or DOCX files with selectable text. Clause extraction quality degrades significantly on scanned documents.

**Why this is unknown**: The scenario mentions the legal team receives inbound vendor contracts but does not describe the intake channel. Some vendor ecosystems — particularly in manufacturing, financial services, or older procurement systems — routinely send scanned PDFs. If 30–40% of the intake is image-based, the extraction pipeline needs a different approach (OCR + higher confidence thresholds + more aggressive escalation), and the cost and accuracy profile changes substantially.

**What to do**: Pull a sample of 30 recent inbound contracts and measure what percentage are native digital vs. scanned. Also check whether any contracts arrive as HTML, Google Docs links, or other formats not covered by the PDF/DOCX ingestion path.

---

## 3. The paralegal's redline authority is formally defined and consistently applied today

**Assumption**: There is a clear, agreed boundary between what the paralegal can redline independently and what requires lawyer sign-off. The agent's playbook-negotiable routing depends on this boundary being real, not aspirational.

**Why this is unknown**: In practice, paralegal authority in legal teams is often informal and relationship-dependent. The paralegal may currently run deviations past a lawyer informally before sending them — which means the "20% paralegal-handled" figure in the scenario may already have embedded lawyer involvement that isn't visible in the workflow description. If that's the case, the routing model will need to reflect the real workflow, not the stated one.

**What to do**: Interview both the paralegal and at least two lawyers about the last 20 playbook-negotiable contracts. How many of those did the paralegal send without any lawyer consultation? Document the actual authority boundary, not the assumed one.

---

## 4. Named-lawyer sign-off can be captured and verified electronically at the clause level

**Assumption**: The organisation can implement a system that records which named lawyer approved which specific clause, with a timestamp, in a way that is auditable and legally defensible. This is the technical expression of the general counsel's hard rule.

**Why this is unknown**: Many legal teams currently manage approvals via email threads, Slack messages, or verbal confirmation — none of which are clause-level, timestamped, or tied to a specific contract version. Building the approval gate requires either integrating with an existing approval system (CLM, DocuSign, or similar) or building one. If the organisation has no approval infrastructure and is resistant to adopting one, the governance control the general counsel requires cannot be implemented in a reliable way.

**What to do**: Determine what approval and signature infrastructure currently exists. If it's email-based, assess whether the organisation will accept a lightweight purpose-built approval UI, or whether a CLM integration is required before the agent can go live.

---

## 5. Historical contracts with known outcomes are available for calibration and testing

**Assumption**: The team can provide a labelled sample of past contracts — ideally 50 or more — with their final disposition (standard / redlined / escalated) and the specific clauses that drove each decision. This is needed to calibrate the confidence thresholds, validate the playbook rules, and test the extraction pipeline.

**Why this is unknown**: Historical legal documents are often subject to confidentiality obligations, privilege concerns, or are simply not organised in a way that makes them accessible for testing. The team may be uncomfortable sharing real vendor contracts even internally for an AI project. If historical data is unavailable, the only alternative is building synthetic fixtures — which adds time and introduces the risk that synthetic contracts do not reflect the real variance in the intake population.

**What to do**: Ask the general counsel whether a sample of past contracts can be used for system validation. If not, determine whether synthetic contracts can be derived from anonymised clause patterns, or whether a pilot with a small live cohort is the only viable calibration path.

---

## 6. The 90-minute average review time is consistent across the three routing categories

**Assumption**: The 90-minute figure applies evenly across standard, negotiable, and escalation contracts. If it does, the time-saving opportunity is roughly proportional to volume (70% standard = largest opportunity). If standard contracts actually take 45 minutes and escalations take 3 hours, the prioritisation logic changes.

**Why this is unknown**: Average figures mask variance. The scenario states 90 minutes as the overall average but gives no breakdown by complexity. An agent that automates standard-contract review may save less wall-clock time than expected if those contracts were already being handled quickly, while the real bottleneck is the back-and-forth on escalations.

**What to do**: Ask the legal team to time-track a two-week sample of reviews by contract type. Even rough data (under 1 hour / 1–2 hours / over 2 hours) will materially improve the ROI model and prioritisation.

---

## 7. Procurement's definition of "unworkable" turnaround is a shared understanding across the organisation

**Assumption**: Reducing turnaround to 1–2 business days will satisfy the procurement team and resolve the stated organisational friction. The procurement team and the legal team have agreed on what an acceptable SLA looks like.

**Why this is unknown**: "Unworkable" is the procurement team's characterisation. It may reflect a few specific high-profile delays rather than a systemic problem across all 300 quarterly contracts. If the bottleneck is actually the 30 escalation contracts — where the legal team is slow to make strategic decisions, not slow to do first-pass review — then automating first-pass review will not fix the procurement team's pain. The solution might need to focus on escalation triage speed rather than standard-contract throughput.

**What to do**: Have a direct conversation with 2–3 procurement leads about the last 5 times a contract delay blocked a purchasing decision. Was the delay in first-pass review, in the escalation decision, or in the back-and-forth after the counteroffer? The answer shapes where to invest.
