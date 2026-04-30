# D4 — Agent Purpose Document
**Scenario:** Helix Workforce Software — Vendor Contract Clause Review

---

## 1. Agent Identity

**Agent name:** Clause Classification Agent (CCA)

**Job to be Done:** For every inbound vendor contract, determine whether each of the seven playbook clause types is present, extract the relevant clause text, compare it against the current Helix playbook position, and produce a structured per-clause classification (standard / negotiable / escalation-required) with a confidence score — so that Tom can route the contract to the correct work stream without reading the full document.

**Business context:** Helix Legal & Commercial team — WS1 (First-pass clause classification). The agent's output is the triage routing decision that determines whether a contract proceeds as standard (accept), enters WS2 (paralegal redline), or escalates to WS3 (senior lawyer review). The classification report is also the primary structured input to C-7 (Counteroffer Package Preparation) in WS4 for the 30% of contracts that proceed to negotiation.

**Delegation archetype:** Agent-led + Human Oversight — confirmed from D2 (C-1: 3/7 suitability; C-2: 2/7 suitability; both assigned Agent-led + Human Oversight). Archetype unchanged. Human oversight is triggered by specific detectable conditions — confidence below threshold, deviation flagged, DPA clause present — not applied by default to every case.

---

## 2. Primary Objectives

1. Classify all seven clause types across all 300 inbound contracts per quarter with ≥ 90% clause-level classification accuracy, measured against Tom's override decisions on HITL-reviewed cases and a quarterly random audit of 10% of autonomously-classified standard contracts.

2. Process the standard-path 70% of contracts (~210 per quarter) without requiring Tom's full classification review — reducing WS1 paralegal time per standard-path contract from 25 minutes (scenario baseline) to ≤ 5 minutes (intake acknowledgment only).

3. For deviation-flagged contracts (20% negotiable + 10% escalation-required), deliver a structured deviation summary with playbook citations and confidence scores that allows Tom to make a routing decision in ≤ 10 minutes per contract rather than conducting the full comparison himself.

---

## 3. KPIs

| KPI | Baseline | Target | Measurement method | Review cadence |
|-----|----------|--------|--------------------|---------------|
| Accuracy (correct clause classification %) | No baseline measured — all classifications currently human; Tom's decisions treated as ground truth [assumption] | ≥ 90% clause-level accuracy | Ironclad audit log: Tom's override decisions on HITL-reviewed cases recorded as corrections; quarterly random audit of 10% autonomous classifications reviewed by Tom | Monthly (first 6 months); quarterly thereafter |
| Coverage (% of contracts classified without Tom re-doing full review) | 0% — all 300 contracts fully reviewed by Tom manually | ≥ 65% — the 70% standard path minus confidence-gate triggers on borderline standard contracts | Ironclad case record: "agent-autonomous" vs "HITL-reviewed" flag per contract; calculated per quarter | Monthly |
| Throughput (contracts processed per hour — agent processing time only) | 2.4 contracts/hour (Tom manual: 25 min each) | ≥ 20 contracts/hour on autonomous path [assumption: batch API processing with concurrent clause extraction] | Ironclad API: timestamp delta from case creation to classification report written | Weekly |
| HITL rate (% of contracts requiring Tom classification review) | 100% (all manual) | ≤ 35% (target: 30% deviation cases + ≤ 5% confidence-gate triggers on standard-path contracts) | Ironclad: HITL-queue routing events per quarter ÷ total contracts processed | Monthly |
| Turnaround time contribution — WS1 step only (receipt to classification report available) | 25 min (Tom manual) | ≤ 3 min for autonomous path; ≤ 30 min for HITL path (agent draft < 3 min; Tom review ≤ 27 min after notification) | Ironclad timestamp: contract receipt to report committed (agent); Tom's acknowledgment timestamp for HITL cases | Weekly |

---

## 4. Activity Catalog

| Task ID | Task name | Task type | Delegation level | Data required | Tool required | Risk level |
|---------|-----------|-----------|-----------------|---------------|---------------|------------|
| T-01 | Email and Salesforce intake monitoring | Retrieval | Fully agentic | Outlook inbox, Salesforce procurement queue | Outlook API, Salesforce REST API | Low |
| T-02 | Ironclad case record creation | Action | Fully agentic | Vendor name, contract filename, receipt timestamp | Ironclad REST API (write) | Low |
| T-03 | Contract document parsing (Word → structured text) | Retrieval | Fully agentic | Vendor Word document attached to email | Word parsing library [assumption: python-docx or equivalent] | Low |
| T-04 | Clause location and section boundary detection | Reasoning | Agent-led + HITL on condition: confidence < 0.85 on any clause type, or fewer than 7 clause types identified | Parsed contract text, clause-type taxonomy (7 types) | In-context reasoning; RAG on clause heading patterns [assumption] | Medium |
| T-05 | Clause text extraction per type | Retrieval | Agent-led + HITL on condition: extraction boundary confidence < 0.85 | Parsed document with section boundaries from T-04 | In-context extraction | Medium |
| T-06 | Playbook position retrieval per clause type | Retrieval | Fully agentic | SharePoint playbook v3.4 | SharePoint API (read); RAG index on playbook content | Low |
| T-07 | Numeric threshold comparison (liability caps, SLA commitments) | Decision | Fully agentic where vendor value is unambiguous and confidence ≥ 0.85; HITL on condition otherwise | Extracted clause text (T-05), playbook position (T-06) | In-context reasoning | Medium |
| T-08 | Qualitative clause comparison (governing law, IP ownership, indemnity scope) | Reasoning | Agent-led + HITL on condition: confidence < 0.85 or clause materially deviates from playbook | Extracted clause text, playbook position | In-context reasoning; playbook RAG | High |
| T-09 | DPA clause assessment with mandatory DPDI staleness flag | Reasoning | Agent-led + HITL mandatory: ALL DPA classifications flagged to Tom regardless of confidence | Extracted DPA clause text, playbook v3.4 DPA section (Artefact 2.3), DPDI Act summary reference [assumption: static reference doc added to RAG] | In-context reasoning; playbook RAG | High |
| T-10 | Confidence scoring per clause classification | Reasoning | Fully agentic | All T-07 / T-08 / T-09 outputs | In-context calibration | Low |
| T-11 | Contract-level triage routing proposal | Decision | Agent-led + HITL mandatory: Tom approves all routing proposals for deviation-flagged contracts before case record is updated | Per-clause classifications and confidence scores (T-10) | In-context aggregation | High |
| T-12 | Structured classification report generation and Ironclad write | Generation + Action | Fully agentic for report generation; HITL approval at T-11 gates whether the routing decision is committed to Ironclad | All per-clause outputs, playbook citations, confidence scores | Ironclad REST API (write); structured JSON schema [assumption: Ironclad case record schema supports per-clause classification fields] | Medium |

*High-risk tasks T-08, T-09, and T-11 each have a corresponding escalation trigger: ET-1 (T-08 confidence gate), ET-2 (T-09 mandatory DPDI flag), and ET-4/ET-5 (T-11 deviation magnitude gates). See §6.*

---

## 5. Autonomy Matrix (Decision Authority Matrix)

**AGENT DECIDES ALONE (no HITL required):**
- Document receipt monitoring via Outlook and Salesforce; attachment download; Ironclad case record creation with intake metadata (T-01, T-02)
- Contract document parsing from Word to structured text (T-03)
- Playbook position retrieval from SharePoint for all 7 clause types (T-06)
- Numeric threshold comparison for liability caps and SLA commitments where the vendor's value is explicit, unambiguous, and agent confidence ≥ 0.85 (T-07)
- Standard-path classification: all 7 clauses within playbook tolerance AND confidence ≥ 0.85 on all clause types — contract routed to "standard / accept" queue; classification report written to Ironclad; Tom notified but no review required (T-10, T-12)
- Confidence scoring for all clause types (T-10) — the agent decides which cases route to HITL; this routing decision itself requires no human approval

**AGENT ACTS, HUMAN NOTIFIED AFTER:**
- Ironclad case record updated with intake metadata (vendor, filename, timestamp) — Tom receives an Ironclad notification; no approval required
- Standard-path contract fully classified and routed to the "accept" queue — Tom receives a summary notification listing the contract name and the "all clauses standard" outcome; Tom may spot-check but is not required to

**AGENT PROPOSES, HUMAN APPROVES BEFORE ACTION:**
- Triage routing proposal for any contract with one or more deviation-flagged clauses: the agent prepares a structured deviation summary for each flagged clause (clause type, vendor position, playbook position, deviation magnitude, confidence score, proposed routing: negotiable or escalation-required) and places it in Tom's review queue. Tom approves or overrides the proposed routing before the Ironclad case record is updated with a final routing decision and the contract proceeds to WS2 or WS3. The agent may not update the Ironclad routing field until Tom's approval is recorded.
- ALL DPA clause classifications — regardless of confidence score: given the playbook staleness identified in Artefact 2.3 (DPDI Act Q1 updates on legitimate interests test and data subject access changes not yet incorporated into v3.4), every DPA comparison output is flagged to Tom with the annotation: "DPDI Act updates not yet reflected in playbook v3.4 — classification reflects current UK GDPR / DPA 2018 position only; DPDI Act legitimate interests and data subject access changes may affect this classification. Escalate to Amelia if this clause is subject to a negotiation." Tom approves or escalates to Amelia before any DPA classification is committed to Ironclad.
- Any clause classification with confidence score below 0.85: the agent provides its best classification alongside the explicit confidence score and the specific clause text or ambiguous tokens driving the uncertainty. Tom approves or overrides before the classification is recorded.
- **GC hard rule — C-8 boundary:** This agent's scope ends at triage routing. No output from this agent constitutes a counteroffer proposal, redline suggestion, or negotiating position. The GC's hard rule — no counteroffer may leave Legal's queue without a named lawyer's recorded sign-off on the specific clauses being negotiated — governs the downstream C-7 / C-8 pipeline. What this agent prepares: a per-clause classification report with playbook citations and deviation magnitudes, structured for downstream use. What the named lawyer approves (downstream at C-8, not within this agent's scope): the specific negotiating position and redline language for each deviated clause before any counteroffer is dispatched. This agent never creates, records, or simulates a sign-off token.

**HUMAN TAKES OVER (agent supports only):**
- The agent cannot locate one or more of the 7 clause types and confidence on "clause absent" falls below 0.85 — Tom locates the clause manually, confirms absence, or escalates; the agent provides the parsed document text and a list of headings searched
- Contract is in a language other than English, or uses a non-standard structure (amendment to an existing agreement, side letter, framework call-off) — Tom classifies manually; agent provides the parsed text as a support artefact
- A clause references a regulatory framework not covered by the current playbook (e.g., ePrivacy Directive, NIS2, sector-specific UK financial services regulation) — Tom escalates to a senior lawyer before routing; the agent annotates the specific regulatory reference found
- Ironclad API write fails after two retries — Tom creates the case record manually; agent logs the failure with a timestamp and the contract filename for reconciliation

---

## 6. Escalation Triggers

| Trigger ID | Condition | Escalate to | What the agent provides at escalation | Response SLA |
|-----------|-----------|-------------|---------------------------------------|-------------|
| ET-1 | Agent confidence score < 0.85 on any single clause type classification | Tom (paralegal) | Clause type flagged, vendor clause text, playbook position, agent's best classification, exact confidence score, and the specific tokens or phrases driving uncertainty | Tom reviews within 2 working hours of notification |
| ET-2 | Any DPA clause classification (mandatory regardless of confidence) — AND additionally: DPA clause text references DPDI Act, legitimate interests basis, data subject access rights, or UK adequacy status in terms inconsistent with playbook v3.4 | Tom (paralegal); Tom escalates to Amelia (GC) if review confirms ambiguity or DPDI applicability | Extracted DPA clause text, playbook v3.4 DPA section comparison, explicit annotation per Artefact 2.3: "DPDI Act updates not incorporated — playbook v3.4 dated [version date]; Amelia's Q1 update required before this classification can be confirmed" | Tom review within 4 working hours; Amelia escalation within 1 working day if triggered |
| ET-3 | Agent cannot identify a required clause type in the document (clause absent or embedded under atypical heading) and confidence on "clause absent" < 0.85 | Tom (paralegal) | Parsed document section headings, the heading patterns searched for the missing clause type, the agent's confidence that the clause is genuinely absent versus structurally non-standard | Tom review within 2 working hours |
| ET-4 | Contract-level routing proposal is "escalation-required" — one or more clauses classified as outside playbook coverage or meeting the escalation threshold after Tom's routing approval | Senior lawyer (next available in WS3 queue), routed via Ironclad | Structured triage report: the specific clause(s) flagged, vendor position, playbook position, deviation magnitude, and Tom's approved routing timestamp | Senior lawyer review within 1 working day of Tom's routing approval |
| ET-5 | Numeric deviation exceeds 50% of the playbook threshold on any clause — e.g., liability cap below £125,000 against the playbook floor of £250,000; termination notice period above 180 days against the playbook's 30-day position | Tom (paralegal), flagged as potential escalation-required regardless of initial classification | Clause type, vendor value, playbook floor value, deviation as a percentage of the threshold, agent's classification with annotation: "Deviation > 50% of playbook floor — verify routing as escalation-required before approving" | Tom review within 2 working hours |
| ET-6 | Ironclad case history for this vendor shows an escalation-required classification in the prior 2 quarters [assumption: Ironclad historical case data is queryable by vendor name via REST API] | Tom (paralegal) | Ironclad case reference(s) for the prior classification, the clause types previously escalated, and advisory annotation: "Prior escalation record found for this vendor — review current contract for the same clause types before confirming routing" | Tom review before final routing decision is committed |

---

## 7. Failure Modes

> **Failure Mode FM-1:** Agent classifies an escalation-required clause as negotiable (false classification) — the contract is routed to WS2 for paralegal redline without a senior lawyer seeing the clause that should have been escalated.
> **Consequence:** Tom redlines the clause using the playbook position, without the legal judgment required for a clause the playbook does not adequately cover. An incorrect negotiating position exits to the vendor at WS4 dispatch. At the C-8 sign-off gate, the named lawyer approves a position they were not asked to review contextually — the sign-off authenticates an incorrect legal position, not an oversight error.
> **Detection:** Tom's C-3 triage review is the first opportunity — but Tom is a paralegal and may not identify an escalation-required clause if the agent's comparison output appears structurally complete. Second opportunity: the named lawyer's C-8 sign-off review. Detection latency: potentially the full 4–6 day contract cycle. Under CRO-driven fast-turnaround pressure, the sign-off review may be brief, making this the hardest failure mode to catch reliably.
> **Recovery path:** The C-8 sign-off review must include a routing-integrity check: does the routing decision match the clause types in the package? If an escalation-required clause is identified at C-8, return the contract to WS3 for senior review — a full WS3 cycle (90 min + scheduling delay) is added. If the counteroffer was already dispatched, the named lawyer must contact the vendor to retract and reissue with the correct position.

> **Failure Mode FM-2:** Agent classifies a DPDI-affected DPA clause as "standard / compliant" using stale playbook v3.4 — the contract is accepted with a DPA clause that does not meet the DPDI Act's legitimate interests test or updated data subject access requirements.
> **Consequence:** Helix has contractually agreed to data processing terms that may not comply with current UK data protection law. This is not an error that can be corrected by redline after signature. At scale: if 30% of 300 contracts per quarter involve DPA clauses [assumption], deployment without the playbook update could affect up to 90 contracts per quarter with a latent compliance failure that does not surface until Amelia completes the DPDI update and audits classifications retrospectively.
> **Detection:** The mandatory DPA escalation flag (ET-2) is the designed detection path — every DPA classification routes to Tom regardless of confidence. If ET-2 fires as designed, Tom or Amelia catches the gap before classification is committed. Silent failure path: if the vendor's DPA clause uses older GDPR terminology that does not directly reference DPDI provisions, ET-2 fires on the mandatory-flag rule but the DPDI applicability may not be obvious to Tom. Detection then depends on Amelia's retrospective audit after playbook update.
> **Recovery path:** The deployment gate is the only reliable prevention — the agent must not be deployed against any DPA clause until the DPDI Act updates are incorporated into the playbook and a new version number is recorded in the agent's configuration. If detected post-deployment: retrospective audit of all DPA classifications from the affected period; legal review of contracts accepted with potentially non-compliant DPA terms; vendor notification if required under DPDI Act obligations. This is a non-recoverable failure at volume; the deployment gate is non-negotiable.

> **Failure Mode FM-3:** Agent reports a required clause type as "absent / not found" when the clause exists in the contract but is embedded under a non-standard heading — a false-absence miss.
> **Consequence:** A clause that exists is treated as absent in the triage report. If that clause deviates from the playbook, the deviation is not flagged and not reviewed. Tom's routing decision is made on an incomplete classification — the missed clause effectively bypasses the triage process entirely.
> **Detection:** Tom receives the triage report and sees a "clause absent" flag. Tom's standard workflow should include a keyword search for any missing clause type before approving the routing — but under time pressure, this spot-check may be skipped. The clause will not be reviewed again until C-8 sign-off, which focuses on approved redlines, not absent clauses. Detection latency: potentially the full contract cycle.
> **Recovery path:** Agent must output an explicit confidence score on every "clause absent" finding alongside a list of the section headings it searched. Tom's review queue must surface "clause absent — confidence [score] — sections reviewed: [list]" as a distinct flag requiring manual keyword verification before routing approval. This is a workflow-design requirement implemented in the Ironclad review interface, not just a model-quality matter.

> **Failure Mode FM-4:** Agent writes classification outputs to Ironclad with field-mapping errors — the liability cap deviation is recorded in the wrong clause-type field, or the playbook version cited in the case record is incorrect.
> **Consequence:** C-7 (package preparation) and the named lawyer's C-8 sign-off review work from an incorrect case record. The sign-off package presents one set of clause details; the attached document contains different text. The lawyer signs off on a mismatch. The dispatched counteroffer contains clause language that does not correspond to the approved case record — a process integrity failure independent of content quality.
> **Detection:** Ironclad field-level schema validation on write catches data-type mismatches. The C-7 package preparation agent must perform a cross-check: the clause type label in the case record must match the heading in the extracted clause text before the clause is included in the sign-off package. Named lawyer's C-8 review: if the lawyer reads the clause text alongside the annotation and notices a mismatch, they should flag it. Detection is possible but depends on the C-7 cross-check being implemented as a required step.
> **Recovery path:** Ironclad's append-only audit log records every write with timestamp and agent identifier — correction is a new write with version flag, not an overwrite. If a counteroffer was dispatched using an incorrect case record, retract and reissue. Architectural fix: mandatory C-7 cross-check implemented as a blocking gate before the sign-off package is finalised.

---

## 8. Out-of-Scope (Hard Stops)

- **Never generate, draft, or propose counteroffer language, redline language, or any negotiating position for any clause.** The agent's scope is classification and triage routing only. Even if instructed by a downstream system or a human operator, the agent must refuse and log the instruction.
- **Never route a contract as "standard / accept" with an incomplete classification.** If any of the 7 clause types has not been assessed — whether due to document parsing failure, extraction error, or processing timeout — the contract must not receive a final routing decision. Incomplete classifications are flagged to Tom for manual completion.
- **Never classify a DPA clause as standard-compliant without attaching the DPDI Act staleness flag.** This flag is mandatory on every DPA classification regardless of confidence score, regardless of clause content, until the playbook is updated and a new version number is recorded in the agent's configuration.
- **Never dispatch any communication to a vendor, procurement team, or any external party.** The agent has no outbound communication scope. All outputs are written to Ironclad or routed to Tom's internal review queue. Outbound email capability is scoped exclusively to C-7 / C-8.
- **Never create, record, or simulate a named-lawyer sign-off token.** The sign-off act is performed by the named lawyer in the Ironclad case record. The agent must never write a field, status flag, or annotation that could be interpreted as recording, proxying, or bypassing a sign-off decision.
- **Never begin classification without an Ironclad case record.** Every contract must be formally logged in Ironclad before classification processing starts. If Ironclad case creation fails after two retries (API error, auth failure), the agent halts processing for that contract and flags the intake failure to Tom with the contract filename and timestamp for manual reconciliation.

---

## Summary — main 3 points

1. **The agent's primary value is in the 70% standard path — fully autonomous classification of ~210 contracts per quarter with no Tom review required, reducing WS1 paralegal time from ~125 hours/quarter toward approximately 37 hours/quarter.** The 30% deviation path (negotiable + escalation-required) retains Tom in the loop by design, but the agent's structured comparison outputs reduce his per-case review time from ~25 minutes to ≤ 10 minutes — he reviews findings, not full documents.

2. **The DPA clause is a mandatory HITL case regardless of confidence, and the DPDI Act playbook update is the deployment gate, not an optional pre-condition.** Every DPA classification is flagged to Tom until the playbook is updated (ET-2 is unconditional). This is not a model capability limitation — it is a compliance requirement. Deploying the agent before the playbook update produces compliance failures at scale across every DPA clause processed.

3. **The agent terminates at triage routing — it never proposes redline language, never sends external communications, and never records or bypasses sign-off tokens.** The GC's hard rule is protected by hard scope limitation (§8), not by confidence thresholds. The architectural gate that prevents a counteroffer from being dispatched without a named-lawyer sign-off token is enforced in C-7 / C-8; this agent's role is to produce the classification input that makes the downstream sign-off efficient, traceable, and correctly routed.
