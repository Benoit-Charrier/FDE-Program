# D4A — Build Loop Clarification
**Helix Workforce Software — Contract Classifier Agent**
**Produced:** 2026-05-04 | **Status:** Draft — FDE review required before D4 revision

---

## Purpose

This document records the output of a simulated build loop against D4 (`D4_agent_purpose_document.md`). It identifies what a coding agent could build confidently from D4 as written, what clarifying questions it would ask, and what it cannot build without answers. Every question and every unbuilable component is a spec deficiency. The FDE uses this analysis to revise D4 before the actual build loop begins.

---

## 0. Table of Contents

- [1. What the builder builds confidently](#1-what-the-builder-builds-confidently)
- [2. Questions the builder asks before proceeding](#2-questions-the-builder-asks-before-proceeding)
- [3. What cannot be built without answers](#3-what-cannot-be-built-without-answers)
- [4. Spec deficiency diagnosis](#4-spec-deficiency-diagnosis)
- [5. D4 revision recommendations](#5-d4-revision-recommendations)

---

## 1. What the Builder Builds Confidently

These components have sufficient specification in D4 that a coding agent could implement them with no clarifying question.

### 1a. Ironclad intake case creation (T-3 scaffold)

D4 names the fields to write: counterparty, contract type, received date, delivery channel flag. Ironclad REST API is confirmed available. The builder can produce a function skeleton:

```python
def create_intake_case(counterparty: str, contract_type: str,
                       received_date: str, channel: str) -> str:
    """POST to Ironclad /cases; returns case_id. Auth via env var IRONCLAD_API_TOKEN."""
    ...
```

The function signature and expected output (a case ID returned for downstream use) are derivable from D4. The actual endpoint URL and field-name mapping are placeholder (`# TODO: confirm Ironclad field schema`).

### 1b. DOCX clause section extractor (T-4 scaffold)

Parsing a Word document into sections is unambiguous technically. The builder produces a parser that extracts text blocks grouped by heading hierarchy. D4 specifies the input (Word DOCX) and the desired output structure (identified clause sections). The clause-identification heuristic is ambiguous (see Q7 below), but the builder can implement a heading-based default and flag the assumption.

### 1c. DPA currency check logic (T-8)

The decision tree is fully specified: if `playbook_dpa_version_date < DPDI_ACT_EFFECTIVE_DATE`, all DPA classifications receive the "Unverified against current regulation" flag. The builder can implement this as:

```python
DPA_PLAYBOOK_DATE = "2025-08-01"          # scenario: playbook revised 9 months ago
DPDI_ACT_EFFECTIVE_DATE = "TODO"           # D4 Assumption A-5 — must be confirmed
DPA_CURRENT = DPA_PLAYBOOK_DATE >= DPDI_ACT_EFFECTIVE_DATE
```

The logic is buildable; `DPDI_ACT_EFFECTIVE_DATE` is a named constant placeholder requiring one answer (Q8).

### 1d. Confidence threshold constants (from Autonomy Matrix)

D4 §5 specifies two numeric thresholds: match confidence default 0.90, routing confidence default 0.80. The builder encodes these as configurable constants:

```python
MATCH_CONFIDENCE_THRESHOLD = 0.90
ROUTING_CONFIDENCE_THRESHOLD = 0.80
```

### 1e. Escalation trigger evaluation logic (ET-1, ET-4, ET-5)

Three triggers are unambiguously specified:
- **ET-1:** `routing_confidence < ROUTING_CONFIDENCE_THRESHOLD` → flag "Routing — Low Confidence" for Tom
- **ET-4:** `parse_completeness < 0.90` (>10% sections unextracted) → flag "Incomplete parse"
- **ET-5:** `matched_playbook_categories / total_clauses < 0.75` (>25% of clauses unmatched) → flag "Unclassifiable — playbook gap"

These are deterministic conditions with named thresholds; the builder can implement them immediately.

### 1f. Deviation report data schema (T-10 partial)

D4 §4 lists the report fields: clause text excerpt, playbook position, classification, confidence, flags. The builder produces a data class:

```python
@dataclass
class ClauseClassification:
    clause_id: str
    clause_excerpt: str
    playbook_position: str
    classification: Literal["MATCH", "DEVIATION_STANDARD", "DEVIATION_ESCALATION", "DPA_UNVERIFIED"]
    confidence: float
    flags: List[str]
```

The classification enum is derivable directly from T-7 in the activity catalog.

### 1g. Hard-stop enforcement in out-of-scope section

Five hard stops in D4 §8 are Boolean guards that the builder can implement as runtime assertions:
- No outbound external communication (agent has no email-send capability)
- No redline language generation (LLM system prompt prohibits redline output)
- No routing commit without `human_confirmed = True` in the Ironclad case record
- DPA currency flag cannot be suppressed
- No Salesforce data access (no Salesforce integration in scope)

---

## 2. Questions the Builder Asks Before Proceeding

These are the questions a coding agent would raise before being able to implement the remaining components. Each question is labelled with the task(s) it blocks.

---

**Q1 — Routing decision criteria: what drives WS2 vs. WS3 vs. No Redline Required?**

*Blocks: T-9 (routing tier assignment)*

D4 defines the three routing tiers and specifies that a routing recommendation is produced with a confidence score, but never specifies the decision logic. The autonomy matrix says the agent "generates a routing recommendation" but does not say: given a set of clause classifications and deviation magnitudes, how does the tier get assigned? The only concrete criterion is ET-3 (liability cap deviation above a threshold → WS3), but the threshold itself is "to be defined" (Assumption A-7) and covers only one of the seven playbook clause types.

For the builder to implement T-9, they need: for each of the seven clause types, what classification outcome (Match / Deviation-Standard / Deviation-Escalation) triggers which tier, and what is the aggregation rule when multiple clauses have conflicting signals?

---

**Q2 — Confidence scoring method: how is the per-clause confidence score derived?**

*Blocks: T-7, T-9, ET-1, MATCH threshold logic*

D4 references per-clause confidence scores and routing confidence scores throughout (D4 §3, §4, §5, §6) and specifies numeric thresholds (0.90 match, 0.80 routing). But it does not specify: Is the confidence score the LLM's raw token probability? A calibrated 0–1 value requested explicitly in the classification prompt? An ensemble of multiple classification attempts? Without knowing the scoring method, the builder cannot implement the classification prompt, cannot validate the threshold values, and cannot implement the escalation logic that depends on them.

---

**Q3 — Ironclad API: endpoint URL, field schema, authentication, request/response format**

*Blocks: T-3, T-11, ET-1 (human confirmation event write)*

D4 names "Ironclad REST API" as confirmed available but provides no: endpoint URL, authentication method (API token, OAuth, service account), field names for the case record, request format, response format, rate limits, or error handling. The production spec checklist §Integration Contracts requires all of these. As written, the builder can only create a placeholder function stub.

---

**Q4 — Outlook integration: mailbox address, authentication, email filter logic**

*Blocks: T-1, T-2 (contract intake monitoring)*

D4 §4 (T-1) assigns Outlook monitoring as a Fully Agentic task but D4 Assumption A-3 flags the integration feasibility as uncertain. The spec does not provide: the monitored mailbox address, the authentication mechanism (Microsoft Graph API, Exchange Web Services, or service account), or the filter criteria that distinguish a "vendor contract email" from other Legal & Commercial mail. Without a filter definition, the agent would either miss contracts or over-ingest non-contract emails.

---

**Q5 — SharePoint API: playbook URL, authentication, document format**

*Blocks: T-5 (playbook retrieval)*

D4 references "SharePoint 'Position Statements v3.4'" but provides no SharePoint URL, site/library path, authentication mechanism (Microsoft Graph API, SharePoint REST, service account), or document format. D4 Assumption A-4 notes the format and version metadata availability are unconfirmed. The builder cannot implement T-5 without a target URL and auth path.

---

**Q6 — Deviation report output format: what does the report written to Ironclad look like?**

*Blocks: T-10, T-11 (report generation and write)*

D4 §4 T-10 says "Generate structured deviation report (clause text excerpt, playbook position, classification, confidence, flags)" and T-11 says "Write deviation report to Ironclad case record." But the spec does not define: Is the report a JSON payload in an Ironclad field? A Word document attachment? A PDF? A combination? If JSON, what is the exact schema? If a document attachment, what template governs its structure? The builder has the content fields but not the output contract.

---

**Q7 — Clause section detection: how does T-4 identify clause sections in a contract?**

*Blocks: T-4 (document parsing), T-6 (per-clause comparison)*

Vendor contracts arrive with varied structure, numbering conventions, and drafting styles. D4 §4 T-4 says "identify clause sections" but does not specify the detection method. Three defensible approaches exist:
- Heading-based: text blocks following a heading that matches a pattern (`\d+\.`)
- Keyword-based: blocks containing trigger terms ("Limitation of Liability," "Data Processing," etc.)
- Semantic: LLM identifies clause type from surrounding text regardless of heading

Each produces different results on edge cases (e.g., a liability cap buried in an indemnity clause). Without a specified method, two builds from this spec would produce different clause lists from the same document.

---

**Q8 — DPDI Act effective date for T-8 DPA currency check**

*Blocks: T-8 (DPA currency check), ET-2 (DPA escalation trigger)*

D4 Assumption A-5 explicitly flags this as unknown. T-8 requires `DPDI_ACT_EFFECTIVE_DATE` as a concrete value (or a configurable constant with a specified source) to implement the version comparison. Without it, the DPA currency check always falls back to the "unverified" flag, which is a safe default but not the intended production behaviour.

---

**Q9 — Ironclad "Pending Human Review" queue: is this a workflow state, field value, or assignment rule?**

*Blocks: T-11 (case routing after report generation)*

D4 §4 T-11 says "move case to 'Pending Human Review' queue in Ironclad" but Ironclad's state model for a case (workflow states, approval steps, assignment queues) is not documented in D4. A builder cannot implement the routing transition without knowing: What is the Ironclad workflow event that triggers this transition? Is it a field write, a workflow step completion, or a case assignment to a specific user group?

---

## 3. What Cannot Be Built Without Answers

| Component | Blocked by | Status |
|---|---|---|
| T-1: Outlook inbox monitoring | Q4 (Outlook integration) | Cannot build |
| T-2: Email metadata + attachment extraction | Q4 (Outlook integration) | Cannot build |
| T-5: SharePoint playbook retrieval | Q5 (SharePoint integration) | Cannot build |
| T-9: Routing tier assignment logic | Q1 (routing criteria) | Cannot build core logic — can build output format only |
| T-11: Write to Ironclad + queue routing | Q3 (Ironclad schema), Q9 (queue model) | Cannot build |
| T-8 (production): DPA date-based currency check | Q8 (DPDI date) | Can build with placeholder constant; cannot deploy |
| T-7: Per-clause confidence scoring | Q2 (scoring method) | Can build classification enum; cannot build confidence assignment |
| T-4: Clause detection with specified method | Q7 (parsing heuristic) | Can build heading-based default; behaviour on edge cases undefined |

**Buildable immediately (T-3 scaffold, T-8 logic, T-10 schema, ET-1/ET-4/ET-5 triggers, hard-stop guards):** ~30% of the agent surface area.

**Blocked pending Q1–Q9 answers:** ~70% of the agent, including the two highest-value components (T-6/T-7 clause comparison and T-9 routing logic) and all integration adapters.

---

## 4. Spec Deficiency Diagnosis

Using the taxonomy from `references/spec-ambiguity-vs-builder-mistakes.md`:

| Question | Deficiency type | Diagnosis |
|---|---|---|
| Q1: Routing criteria | **Design Gap** | The spec covers routing outputs (the three tiers) but never specifies the routing decision logic. The builder built exactly what was asked for; the criteria simply aren't there. Fix: add them to the spec. |
| Q2: Confidence scoring method | **Design Gap** | Confidence scores are used throughout D4 as if they were a well-defined quantity, but the method of derivation was never specified. This is a production-obvious gap: the spec is silent on how to measure what it repeatedly references. Fix: add a confidence scoring definition. |
| Q3: Ironclad API schema | **Design Gap** | Integration contract fails §Integration Contracts checklist entirely: no endpoint, no auth, no request/response format, no error handling, no rate limits. The spec says "Ironclad REST API confirmed" — which is a statement of existence, not a contract. Fix: add an Ironclad integration contract to D4 or D5. |
| Q4: Outlook integration | **Spec Ambiguity** | D4 assigns T-1/T-2 as "Fully Agentic" while simultaneously flagging the integration as uncertain (Assumption A-3). These two statements are in tension: a task cannot be assigned Fully Agentic if the integration path is not confirmed. The builder gets conflicting signals. Fix: either confirm the integration path or designate a fallback (manual forwarding rule) as the Day 1 implementation, and update the task delegation level accordingly. |
| Q5: SharePoint API | **Design Gap** | Same as Q3: integration contract missing. SharePoint is listed as the playbook host; no access contract is provided. Fix: add SharePoint integration contract to D4 or D5. |
| Q6: Deviation report format | **Spec Ambiguity** | D4 §4 T-10 lists the content fields; D4 §4 T-11 says "write to Ironclad case record." The spec is precise about content but silent on format. A builder could reasonably produce a JSON payload, a Word attachment, or both. Two builds from this spec would produce different output formats. Fix: specify the output format schema. |
| Q7: Clause detection method | **Spec Ambiguity** | D4 describes the desired output (identified clause sections) but not the method. Three valid approaches exist; each produces different results on edge-case contracts. Fix: specify the primary detection method and the fallback. |
| Q8: DPDI Act date | **Design Gap** | D4 Assumption A-5 correctly flags this as unknown. It is a factual gap, not a design choice. Fix: supply the date (or a named configuration source from which it will be read at runtime). |
| Q9: Ironclad queue model | **Design Gap** | The spec describes a desired end state ("Pending Human Review queue") without describing the Ironclad mechanism that achieves it. A builder cannot implement a state transition without the state machine. Fix: document the Ironclad workflow step or add as a D5 discovery item. |

---

## 5. D4 Revision Recommendations

### Priority 1 — Blocks building the core classification logic

**R1: Add routing decision criteria to §5 (Autonomy Matrix) and §6 (Escalation Triggers)**

The routing tier assignment (T-9) is the agent's primary value-adding action. Without criteria, it cannot be implemented. D4 needs to specify, for each of the seven clause types:
- What classification outcome (Match / Deviation-Standard / Deviation-Escalation) triggers which tier
- The aggregation rule when a contract has mixed signals across clause types (e.g., three Matches and one Deviation-Escalation — is that WS2 or WS3?)
- The ET-3 liability cap threshold value (or a stated pre-deployment condition: "this threshold must be defined by Amelia before deployment")

If the criteria genuinely cannot be specified before deployment (because they depend on Tom and Amelia's input), D4 should state this explicitly and define the fallback behaviour: "until criteria are codified, all contracts with any Deviation-Escalation classification are routed WS3; contracts with Deviation-Standard only are routed WS2; contracts with Match only are No Redline Required."

**R2: Define the confidence scoring method in §4 (Activity Catalog) or a new §9 (Technical Definitions)**

Add a concise definition:
- How the score is produced (e.g., "the agent's classification prompt explicitly requests a confidence score as a float 0.0–1.0, where 1.0 = 'I am certain this is the correct classification and there is no ambiguous interpretation'; the agent is instructed to be conservative — scores above 0.90 are reserved for textbook examples")
- What the 0.90 match threshold and 0.80 routing threshold represent in plain English
- Whether scores are computed per-clause or at the case level

**R3: Define the deviation report output schema in §4 T-10**

Specify the exact output format: JSON schema with field names, types, and example. At minimum, define whether the report is delivered as a structured JSON payload written to an Ironclad custom field, a document attachment, or both. The clause-level `ClauseClassification` data class (field names from §1f above) is a valid starting point.

---

### Priority 2 — Blocks integration but can proceed with mocks

**R4: Add Ironclad integration contract (or move to D5 with explicit placeholder in D4)**

D4 §4 (T-3, T-11) and the escalation trigger mechanism all depend on Ironclad API specifics. Either:
- Add an Ironclad integration contract section to D4 (endpoint pattern, authentication via `IRONCLAD_API_TOKEN` env var, key field names for case metadata and deviation report)
- Or note explicitly in D4: "Ironclad integration contract is documented in D5 §[section]; build using the mock contract in D5 until the actual API is confirmed"

The current D4 says "Ironclad REST API confirmed" which is sufficient for stating intent but not for building.

**R5: Add SharePoint integration contract (or move to D5)**

Same pattern as R4: either add a SharePoint integration contract section or cross-reference D5.

**R6: Resolve the T-1/T-2 Outlook integration conflict**

T-1 and T-2 are currently designated Fully Agentic but D4 Assumption A-3 flags the integration as uncertain. The spec cannot simultaneously designate a task Fully Agentic and mark its prerequisite integration as uncertain. Choose one:
- **Option A:** Confirm that Microsoft Graph API access to the Legal & Commercial shared mailbox is available, and add it to the integration contract. T-1/T-2 remain Fully Agentic.
- **Option B:** Designate the Day 1 implementation as a manual forwarding rule (Tom forwards contract emails to a dedicated intake address that the agent monitors), reducing T-1 to "monitor a designated intake mailbox" with a simpler implementation path. Update the activity catalog delegation level from Fully Agentic to Agent-led + Human Oversight (Tom triggers the forwarding), with a note that this upgrades to Fully Agentic once Graph API access is confirmed.

---

### Priority 3 — Needed before production, can proceed with placeholders

**R7: Supply DPDI Act effective date or specify configuration source**

Add to D4 §4 T-8: "DPDI Act Q1 revisions effective date: [date — to be confirmed by Amelia; stored in config as `DPDI_ACT_EFFECTIVE_DATE`; until confirmed, default to 2025-01-01 as a conservative placeholder]." This lets the builder implement the check with a clearly-labelled placeholder rather than an open assumption.

**R8: Document the Ironclad "Pending Human Review" queue model**

Add a one-paragraph note to D4 §4 T-11 describing the expected Ironclad mechanism: "The Ironclad workflow step is expected to be a standard 'Review' stage in the contract workflow; the transition is triggered by a PATCH to the case's `workflow_stage` field (specific stage ID to be confirmed with Ironclad admin). Until confirmed, the builder implements a simulated state flag in a custom case field `agent_status = PENDING_REVIEW`."

---

## 6. Summary: D4 Production Readiness

| Checklist criterion (from production-spec-checklist.md) | D4 status |
|---|---|
| Every requirement has a testable acceptance criterion | Partial — KPIs are specific; routing logic has no test criterion |
| All ambiguous words defined | Partial — "confidence score" used 12+ times without definition |
| Integration contracts complete | Fail — Ironclad, SharePoint, Outlook all missing contracts |
| Entity/schema defined | Partial — deviation report fields listed but no schema |
| Delegation boundaries clear | Pass — autonomy matrix is well-specified for what it covers |
| Escalation triggers specific | Partial — ET-3 magnitude threshold is "to be defined" |
| Failure modes with detection and recovery | Pass |
| Assumptions registered | Pass — 7 assumptions with confidence levels |
| Governance/audit trail explicit | Partial — routing confirmation event specified; audit retention policy not stated |

**Overall: D4 is a strong foundation with three Priority 1 gaps that block the core build.** Addressing R1 (routing criteria), R2 (confidence scoring), and R3 (report schema) unblocks ~70% of the blocked surface area. The integration contracts (R4–R6) can be handled in D5 with explicit cross-referencing in D4.

**Recommended next action:** Revise D4 with R1–R3 before proceeding to the actual build loop. R4–R8 can be addressed in D5 (System/Data Inventory) or as D4 addenda, depending on whether the builder proceeds with mocks.
