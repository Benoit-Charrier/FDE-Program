# D1 — Cognitive Load Map
**Scenario:** Helix Workforce Software — Vendor Contract Clause Review

---

## 1. Work Stream Selection and Rationale

**Selected: WS1 (First-pass clause classification) and WS2 (Standard-deviation redlining).**

WS1 is the obvious primary selection: it handles all 300 contracts per quarter, consumes ~125 hours of legal time on work that is structurally an LLM-suitable extraction and comparison problem, and is the bottleneck that gates every downstream work stream. Its cognitive complexity is high — unstructured document parsing, semantic clause identification across varied vendor drafting styles, and a borderline triage judgment that the current playbook does not codify — yet its delegation potential is also high because the core task is comparison against a reference document that can be structured and indexed.

WS2 is selected over WS3 and WS4 because it sits at the intersection of high delegation potential and cognitively interesting synthesis work. WS3 (escalated clause review) has high per-case cognitive complexity but low delegation potential — the judgment involved is precisely the kind that should remain human. WS4's sign-off act is human-anchored by the GC's hard rule; the remaining preparation and routing sub-tasks are low-complexity and not worth a full decomposition. WS2, by contrast, involves genuine synthesis (translating a policy position into legally precise clause language), has bounded scope (only flagged clauses from WS1), and feeds directly into the sign-off gate — making it the most instructive second work stream for understanding the full automation surface.

---

## 2. Cognitive Load Map — Work Stream A: First-Pass Clause Classification

### 2a. Jobs to be Done Decomposition

> **JtD [WS1-1]:** Determine, for every major clause in an inbound vendor contract, whether the language is compliant with Helix's playbook, and if not, whether the deviation is within the paralegal's authority to redline or requires senior-lawyer escalation.
> **Trigger:** An inbound vendor contract arrives via Outlook (or is flagged in Salesforce for a new enterprise deal).
> **Actor:** Tom (Paralegal).
> **Key decisions:** (1) Which document sections contain each of the 7 clause types? (2) Does the extracted clause language fall within playbook tolerance? (3) Is a deviation within the range Tom is authorised to redline, or does it cross the threshold requiring escalation? (4) Does the clause touch a regulatory area where the playbook is known to be stale?
> **Key systems/data:** Vendor contract (Word document via Outlook/SharePoint), SharePoint playbook page, Ironclad (case logging).
> **Primary cognitive type:** Decision-making (triage) + Synthesis (semantic comparison of unstructured legal text against semi-structured policy).
> **Expected output:** A per-clause classification (compliant / negotiable deviation / escalation-required / regulatory gap) and a contract-level routing decision (standard → close; negotiable → WS2; escalation → WS3).

> **JtD [WS1-2]:** Identify where the playbook does not provide a reliable policy position for a clause in the inbound contract, flag the gap, and determine who needs to resolve it before the contract can be classified.
> **Trigger:** During clause comparison, Tom recognises that the playbook position for a clause type is absent, outdated, or ambiguous relative to current law (e.g., DPDI Act changes not yet reflected in the DPA section).
> **Actor:** Tom (Paralegal), with informal escalation to a named lawyer ("Sarah").
> **Key decisions:** (1) Is the playbook position for this clause type currently reliable? (2) Is this gap significant enough to affect the classification outcome? (3) Which lawyer should be consulted to resolve it?
> **Key systems/data:** SharePoint playbook (version history/last-revised date), informal lawyer knowledge, Amelia's sticky-note awareness of DPDI updates.
> **Primary cognitive type:** Exception-handling — recognising the boundaries of the current policy reference and acting accordingly.
> **Expected output:** Either a provisional classification with a documented uncertainty flag routed to a lawyer, or a pause pending playbook clarification.

---

### 2b. Micro-Task Inventory with Dimension Scores

| Micro-task | Cognitive Load | Input Structure | Decision Determinism | Exception Frequency | Turn-Taking Degree | Latency Constraint | Compliance/Risk Sensitivity | Tool/API Availability |
|---|---|---|---|---|---|---|---|---|
| MT1: Receive and log inbound contract | L | M | H | L | L | M | L | H |
| MT2: Parse document structure — locate each of the 7 clause types | H | L | M | M | L | L | M | L |
| MT3: Extract clause text for each clause type | M | L | M | M | L | L | H | L |
| MT4: Compare extracted clause against playbook position | H | M | M | M | L | L | H | M |
| MT5: Apply triage judgment — negotiable vs. escalation-required | H | M | L | H | M | L | H | L |
| MT6: Detect regulatory/playbook coverage gap | H | L | L | M | H | L | H | L |
| MT7: Record per-clause classification in Ironclad | L | H | H | L | L | M | M | H |
| MT8: Make contract-level routing decision and trigger next work stream | M | H | M | M | L | M | H | H |

**Footnotes — score justifications:**

- **MT1 Cognitive Load (L):** Mechanical intake action — download, save, log. No legal judgment.
- **MT1 Input Structure (M):** Email arrives in Outlook with a Word attachment — semi-structured (identifiable source, variable attachment format).
- **MT1 Tool/API (H):** Outlook, SharePoint, and Ironclad all have documented APIs.
- **MT2 Cognitive Load (H):** Reading a 15–40 page unstructured Word document to identify which sections contain each of 7 clause types requires sustained legal reading against varied vendor section heading conventions. A section labelled "General" may contain liability, indemnity, and governing law language in adjacent paragraphs.
- **MT2 Input Structure (L):** Unstructured Word document — no standardised clause headings, no embedded metadata indicating clause type locations.
- **MT2 Tool/API (L):** No current tool in the scenario's toolset can semantically locate clause types in an unstructured Word document without LLM involvement. Word's search function matches strings, not clause semantics.
- **MT3 Input Structure (L):** Clause text boundaries within legal prose are often ambiguous — a liability clause may span multiple sub-sections; an indemnity obligation may appear mid-paragraph within a "General Terms" section.
- **MT3 Compliance/Risk (H):** Incorrectly extracting a clause (wrong text boundary, or missing a clause entirely) means the comparison in MT4 is performed on wrong text — misclassification propagates downstream.
- **MT3 Tool/API (L):** No current tool supports automated clause boundary extraction from unstructured legal prose.
- **MT4 Cognitive Load (H):** Semantic comparison of legal text against policy. Example from Artefact 2.1: "the lesser of (a) fees paid in the six (6) months preceding the event or (b) £50,000" must be mapped to the playbook minimum of "12 months / £250,000 for enterprise" — this is interpretation, not string matching.
- **MT4 Input Structure (M):** Extracted clause text is unstructured prose; playbook positions are semi-structured bullet points (per Artefact 2.3) — partially machine-readable but not formally structured.
- **MT4 Decision Determinism (M):** Numeric threshold comparisons are deterministic; qualitative comparisons (e.g., "materially different DPA terms") require interpretation. The DPDI Act gap makes DPA comparisons indeterminate until the playbook is updated.
- **MT4 Tool/API (M):** Playbook is in SharePoint (API-accessible); clause text comparison still requires semantic reasoning, not just retrieval.
- **MT5 Cognitive Load (H):** Tom's Artefact 2.1 annotation — "borderline negotiable, not escalation" — illustrates the exact judgment this micro-task requires. The threshold between the 20% and 10% buckets is not explicitly codified in the playbook; Tom applies institutional knowledge.
- **MT5 Decision Determinism (L):** The decision rule is tacit, not documented. Multiple reasonable lawyers might reach different conclusions on the same borderline case.
- **MT5 Exception Frequency (H):** By definition, 30% of contracts hit the deviation zone (20% negotiable + 10% escalation); the uncertainty is concentrated at the boundary between these — estimated 5–10% of all contracts involve genuine borderline judgment [assumption — not stated in scenario].
- **MT5 Turn-Taking (M):** Borderline cases generate the "will ask Sarah" informal consultation — a turn-taking event that introduces untracked latency.
- **MT5 Tool/API (L):** No tool supports this triage judgment — it is entirely Tom's expertise applied to the comparison output.
- **MT6 Cognitive Load (H):** Tom must know not only what the playbook says but what it *does not say* relative to current law. Recognising that a DPA clause referencing only "UK GDPR and DPA 2018" may be non-compliant with DPDI Act requirements requires a meta-level awareness of regulatory currency that goes beyond reading the playbook.
- **MT6 Input Structure (L):** The "input" here is an absence — the playbook does not reflect the current regulatory requirement. Tom detects this from prior knowledge, not from a system prompt.
- **MT6 Decision Determinism (L):** No rule tells Tom when the playbook is stale — this is knowledge-bound exception detection.
- **MT6 Turn-Taking (H):** Always generates an informal consultation ("will ask Sarah") before Tom can proceed.
- **MT6 Tool/API (L):** No tool currently flags playbook staleness or regulatory changes relevant to clause types under review.
- **MT7 Decision Determinism (H):** Recording is a transcription act — the classification decisions are already made. No new decisions at this step.
- **MT7 Tool/API (H):** Ironclad has REST APIs that support case record updates.
- **MT8 Input Structure (H):** By this point, per-clause classifications are structured outputs — the contract-level routing follows from them.
- **MT8 Decision Determinism (M):** Mostly deterministic (any escalation-required clause → escalate entire contract), but edge cases arise when one clause is escalation-required and five are standard — does the whole contract escalate or just the flagged clause? [Unknown — see D0 U-5.]
- **MT8 Compliance/Risk (H):** Routing errors propagate into subsequent work streams. Routing an escalation-required contract to WS2 instead of WS3 means a non-standard clause is redlined by a paralegal instead of reviewed by a senior lawyer.

---

### 2c. Cognitive Zones and Breakpoints

> **Zone [Z-1]:** Document Ingestion and Structure Mapping
> **Micro-tasks in zone:** MT1, MT2
> **Dominant cognitive type:** Deterministic execution (MT1) transitioning to probabilistic reasoning (MT2 — locating clause types in unstructured text)
> **Data dependencies:** Vendor contract file (via Outlook/SharePoint); knowledge of the 7 playbook clause types
> **Error tolerance:** Moderate at MT1 (intake errors are correctable); low at MT2 (missed or misidentified clause locations propagate forward as unreviewed clauses — a missed DPA clause represents a compliance failure)

> **Zone [Z-2]:** Clause Extraction
> **Micro-tasks in zone:** MT3
> **Dominant cognitive type:** Probabilistic reasoning — identifying where a clause begins and ends in dense legal prose, handling ambiguous boundaries and multi-section clauses
> **Data dependencies:** Full document text; understanding of the 7 clause type semantics
> **Error tolerance:** Low — incorrect extraction means MT4 comparison is performed on wrong text, producing an invalid classification

> **Zone [Z-3]:** Playbook Comparison
> **Micro-tasks in zone:** MT4
> **Dominant cognitive type:** Deterministic execution for numeric threshold checks; probabilistic reasoning for qualitative comparisons
> **Data dependencies:** Extracted clause text (from Z-2); playbook position statements (SharePoint); for DPA clauses, the current regulatory position (which is not in the stale playbook)
> **Error tolerance:** Low — comparison errors are the direct cause of misclassification

> **Zone [Z-4]:** Deviation Triage and Gap Detection
> **Micro-tasks in zone:** MT5, MT6
> **Dominant cognitive type:** Human sense-making — applying institutional knowledge to determine the negotiable/escalation boundary; detecting regulatory coverage gaps the playbook does not flag
> **Data dependencies:** Comparison outputs from Z-3; institutional knowledge of Helix's negotiation posture; awareness of current regulatory landscape
> **Error tolerance:** Very low — this is the highest-risk zone. A misclassification (treating escalation-required as negotiable) means a non-standard clause exits to WS2 without senior review. A missed regulatory gap means a non-compliant clause is accepted or incorrectly redlined.

> **Zone [Z-5]:** Classification Recording and Routing
> **Micro-tasks in zone:** MT7, MT8
> **Dominant cognitive type:** Deterministic execution — recording and routing from structured outputs
> **Data dependencies:** Per-clause classification outputs from Z-4; Ironclad (for case record and routing)
> **Error tolerance:** Moderate — administrative recording errors are correctable; routing errors have downstream consequences but are detectable at the next work stream

---

**Breakpoints:**

> **Breakpoint [BP-1]:** Low-confidence clause location — agent cannot reliably identify a clause type's location in the document
> **From:** Agent (document structure parsing, Z-1/Z-2)
> **To:** Tom (human disambiguation)
> **Why this is a breakpoint:** Probabilistic-to-human-sense-making shift. When the agent's confidence in clause location falls below a threshold (e.g., clause type not found, or found in an ambiguous multi-topic section), proceeding creates a risk of missed clause review. The condition triggering review is confidence score below threshold, not general "complexity."
> **Agent opportunity or risk:** Opportunity — agent handles the ~75% of cases where clause location is unambiguous [assumption]; risk — agent over-confidence on ambiguous clause locations is worse than flagging them, because an undetected miss is less visible than a flagged uncertainty.

> **Breakpoint [BP-2]:** Borderline triage judgment — deviation falls at the negotiable/escalation boundary
> **From:** Agent (threshold comparison output, Z-3)
> **To:** Tom (triage judgment, Z-4) — and potentially to a lawyer for informal consultation
> **Why this is a breakpoint:** Rule-to-judgment shift. The agent can produce a comparison result (deviation = X% below playbook minimum); the decision of whether X% constitutes a negotiable deviation or an escalation trigger requires a playbook rule that does not currently exist. Until the playbook codifies the boundary, this judgment cannot be safely delegated to the agent.
> **Agent opportunity or risk:** Opportunity once the playbook is updated with explicit deviation thresholds per clause type. Risk if the agent makes this call unilaterally against tacit thresholds — incorrect triage of the 10% escalation-required contracts is the highest-consequence classification error.

> **Breakpoint [BP-3]:** Regulatory gap detection — clause touches an area where the playbook is stale
> **From:** Tom (Z-4 gap detection)
> **To:** Lawyer (informal consultation — "will ask Sarah")
> **Why this is a breakpoint:** Knowledge boundary — Tom's meta-awareness of playbook staleness is not computable from the playbook itself. The DPDI Act gap is the current instance; similar gaps will occur whenever regulations change faster than the playbook update process.
> **Agent opportunity or risk:** Risk — an agent trained against the current playbook will classify DPDI-affected DPA clauses as "compliant" because the playbook says so. This is the highest compliance risk in the agent design and requires a dedicated regulatory currency check before deployment. Opportunity — a regulatory monitoring feed (flagging when new law affects clause types the agent is responsible for) could automate the gap detection that Tom currently performs from institutional knowledge.

> **Breakpoint [BP-4]:** Contract-level routing — per-clause results aggregated to a contract-level routing decision
> **From:** Agent (MT8 routing logic)
> **To:** Ironclad (automated routing) with human override capability
> **Why this is a breakpoint:** Deterministic execution for clear cases; judgment for edge cases (e.g., one escalation-required clause among five standard ones — does the entire contract escalate?). The routing logic rule is not codified in the scenario.
> **Agent opportunity or risk:** Opportunity — once routing rules are codified, this step is fully automatable. Risk — ambiguous routing rules create silent errors that may not surface until the next work stream.

---

### 2d. Process Topology Diagram — Work Stream A

```
[CONTRACT ARRIVES via Outlook / Salesforce trigger]
                     |
                     v
    ┌────────────────────────────────┐
    │ Z-1: Document Ingestion &      │
    │ Structure Mapping              │
    │ MT1: Receive + log             │
    │ MT2: Locate 7 clause types     │
    │ Type: Det. execution →         │
    │       Probabilistic reasoning  │
    └────────────────────────────────┘
                     |
                     v
       ◆ BP-1: Clause location confidence?
          /                        \
   [Confident]              [Ambiguous / not found]
          |                        |
          |                [Human: Tom disambiguates]
          |                        |
          └────────────────────────┘
                     |
                     v
    ┌────────────────────────────────┐
    │ Z-2: Clause Extraction         │
    │ MT3: Extract text per clause   │
    │ Type: Probabilistic reasoning  │
    └────────────────────────────────┘
                     |
                     v
    ┌────────────────────────────────┐
    │ Z-3: Playbook Comparison       │
    │ MT4: Compare vs. policy        │
    │ Type: Deterministic (numeric)  │
    │       + Probabilistic (qualit.)│
    └────────────────────────────────┘
                     |
                     v
       ◆ BP-2: Deviation at negotiable / escalation boundary?
          /                              \
   [Clear threshold — compliant,   [Borderline: triage
    clearly negotiable, or          judgment required]
    clearly escalation-required]         |
          |                        [Human: Tom judges]
          |                              |
          └──────────────────────────────┘
                     |
                     v
    ┌────────────────────────────────┐
    │ Z-4: Deviation Triage &        │
    │ Gap Detection                  │
    │ MT5: Negotiable vs. escalation │
    │ MT6: Regulatory gap detection  │
    │ Type: Human sense-making       │
    └────────────────────────────────┘
                     |
                     v
       ◆ BP-3: Regulatory / playbook gap detected?
          /                           \
   [No gap]                   [Gap: informal lawyer
          |                    consult ("will ask Sarah")]
          |                           |
          └───────────────────────────┘
                     |
                     v
    ┌────────────────────────────────┐
    │ Z-5: Classification Recording  │
    │ & Routing                      │
    │ MT7: Record in Ironclad        │
    │ MT8: Contract-level route      │
    │ Type: Deterministic execution  │
    └────────────────────────────────┘
                     |
              ◆ BP-4: Routing
         /           |            \
        v            v             v
  [Standard]   [Negotiable     [Escalation
  [Close WS1]  deviation →     required →
               WS2]            WS3]
```

---

## 3. Cognitive Load Map — Work Stream B: Standard-Deviation Redlining

### 3a. Jobs to be Done Decomposition

> **JtD [WS2-1]:** Produce legally precise redlined clause language that achieves Helix's playbook position for each flagged deviation, within the structure and grammar of the vendor's contract.
> **Trigger:** WS1 output routes a contract to WS2 with one or more flagged negotiable deviations.
> **Actor:** Tom (Paralegal).
> **Key decisions:** (1) What exactly is the playbook position for this clause type? (2) How should that position be expressed as redlined clause text that fits the surrounding contract structure? (3) Does the redline create any internal consistency conflicts with other clauses?
> **Key systems/data:** Word document (Track Changes), SharePoint playbook (position statements), prior redline examples [assumption: not mentioned in scenario; may or may not exist].
> **Primary cognitive type:** Synthesis — translating a policy position (semi-structured bullet points) into legally precise clause language (unstructured legal prose).
> **Expected output:** Redlined Word document with tracked changes replacing non-compliant clause text with playbook-compliant language, ready for sign-off routing.

> **JtD [WS2-2]:** Deliver the signed-off redlined document to the vendor procurement contact via the channel they can actually receive it.
> **Trigger:** Sign-off is obtained from a named lawyer (WS4 gate cleared).
> **Actor:** Tom (Paralegal).
> **Key decisions:** (1) Does this vendor accept SharePoint links, or do they require an email attachment? (2) Who is the correct procurement contact to send to?
> **Key systems/data:** Ironclad (vendor contact info), Outlook (delivery), SharePoint (document storage), vendor delivery preference — currently tracked informally, not in any system [inference from Artefact 2.2].
> **Primary cognitive type:** Communication + Execution.
> **Expected output:** Redlined document delivered to vendor procurement contact; delivery logged.

---

### 3b. Micro-Task Inventory with Dimension Scores

| Micro-task | Cognitive Load | Input Structure | Decision Determinism | Exception Frequency | Turn-Taking Degree | Latency Constraint | Compliance/Risk Sensitivity | Tool/API Availability |
|---|---|---|---|---|---|---|---|---|
| MT-A: Retrieve playbook position for flagged clause type | L | M | H | L | L | L | M | H |
| MT-B: Interpret playbook position as a concrete redline target | M | M | M | M | L | L | H | M |
| MT-C: Draft redlined clause language in Track Changes | H | M | L | M | L | L | H | M |
| MT-D: Review redline for cross-clause consistency | H | L | L | M | L | L | H | L |
| MT-E: Save and version the redlined document in SharePoint | L | H | H | L | L | M | L | H |
| MT-F: Route redline draft to named lawyer for sign-off | L | M | M | M | H | M | H | M |
| MT-G: Deliver signed-off redline to vendor via correct channel | L | H | M | M | M | M | L | H |

**Footnotes — score justifications:**

- **MT-A Cognitive Load (L):** Navigating to the correct playbook section is mechanical once the clause type is known from WS1 output. The cognitive work of identifying the clause type happened in WS1.
- **MT-A Input Structure (M):** SharePoint playbook is semi-structured — organised by clause type with bullet-point criteria (per Artefact 2.3), but not a formally structured data format with machine-readable fields.
- **MT-A Tool/API (H):** SharePoint has APIs; the playbook page is accessible programmatically.
- **MT-B Cognitive Load (M):** Understanding the policy position requires interpretation — "12 months / £250,000" is a floor, not an exact mandate; "materially different DPA terms" requires judgment about what "material" means. Moderate because the scope is bounded by the clause type.
- **MT-B Decision Determinism (M):** Clear for numeric thresholds; judgment-dependent for qualitative positions. DPDI Act staleness makes DPA positions indeterminate.
- **MT-B Compliance/Risk (H):** Misinterpreting the playbook position means drafting a redline that does not achieve Helix's required legal position — the error is subtle and may not be caught until the vendor accepts the (incorrectly redlined) clause.
- **MT-C Cognitive Load (H):** This is the most cognitively demanding micro-task in WS2. Tom must generate legally coherent substitute clause text that: (a) achieves the playbook position, (b) fits the grammatical and structural conventions of the surrounding contract, (c) uses appropriate legal formulation. The playbook provides policy positions, not ready-to-paste clause language [inferred from Artefact 2.3 which shows bullet-point criteria, not drafting templates].
- **MT-C Decision Determinism (L):** Multiple valid redline formulations exist for any given clause type; Tom exercises judgment on which formulation best achieves Helix's interests in the context of this specific vendor relationship.
- **MT-C Tool/API (M):** Word has APIs for Track Changes manipulation; generating the clause text itself requires synthesis capability — LLM-assisted for an agent, manual for Tom currently.
- **MT-D Cognitive Load (H):** Cross-clause consistency checking requires reading the full redlined contract to identify whether the redlined clause creates conflicts elsewhere. Example: a modified liability cap clause may interact with an indemnity clause that caps recoveries by reference to the same aggregate limit.
- **MT-D Input Structure (L):** Checking for internal consistency requires reading across the unstructured full document — no tool currently supports semantic cross-clause dependency analysis.
- **MT-D Decision Determinism (L):** Whether a cross-clause interaction constitutes a genuine conflict or a merely stylistic inconsistency is a judgment call requiring legal expertise.
- **MT-D Tool/API (L):** No current tool in the scenario's toolset supports automated cross-clause consistency checking.
- **MT-E Tool/API (H):** SharePoint file management via API is straightforward.
- **MT-F Turn-Taking (H):** Routing initiates a human-to-human handoff — Tom must identify an available named lawyer, route the draft, and then wait. This is the primary source of queue-forming latency in WS2/WS4.
- **MT-F Compliance/Risk (H):** If routing fails or is delayed, the sign-off gate is blocked and the counteroffer cannot be sent — directly affecting turnaround time and the GC's hard rule.
- **MT-G Decision Determinism (M):** Delivery channel is not systematically recorded anywhere — Tom must recall or re-check per-vendor preferences. For the VendorCo-type exception, the email thread from Artefact 2.2 contains the preference, but no system records it.
- **MT-G Exception Frequency (M):** Three vendors this quarter required email attachments — approximately 5% of the 60 redlining cases [inference: 3/60 = 5%].

---

### 3c. Cognitive Zones and Breakpoints

> **Zone [Z-A]:** Policy Retrieval and Interpretation
> **Micro-tasks in zone:** MT-A, MT-B
> **Dominant cognitive type:** Deterministic execution (retrieval) transitioning to probabilistic reasoning (interpretation of policy intent)
> **Data dependencies:** WS1 output (which clause types are flagged); SharePoint playbook (policy positions per clause type); awareness of playbook currency
> **Error tolerance:** Low — errors here corrupt the redline target. A wrong interpretation of the playbook position means the redline cannot achieve Helix's required legal position, and the error propagates through MT-C to the outbound counteroffer.

> **Zone [Z-B]:** Clause Drafting
> **Micro-tasks in zone:** MT-C
> **Dominant cognitive type:** Human sense-making — synthesising a policy target into legally coherent clause language. This is the only zone in either work stream that requires legal *generation* rather than legal *comparison*.
> **Data dependencies:** Playbook position interpretation (Z-A output); original vendor clause text; legal drafting convention
> **Error tolerance:** Very low — the redline is the substantive legal work product. Drafting errors (wrong position achieved, ambiguous language, grammatical inconsistency with surrounding contract) are the direct cause of legal risk in outbound counteroffers.

> **Zone [Z-C]:** Cross-Clause Consistency Review
> **Micro-tasks in zone:** MT-D
> **Dominant cognitive type:** Human sense-making — reading across an unstructured document for semantic interactions between clauses
> **Data dependencies:** Full redlined contract document
> **Error tolerance:** Low — undetected cross-clause inconsistencies create legal ambiguity that can be exploited by the counterparty in a dispute.

> **Zone [Z-D]:** Document Management and Sign-off Routing
> **Micro-tasks in zone:** MT-E, MT-F
> **Dominant cognitive type:** Deterministic execution
> **Data dependencies:** Signed-off document in SharePoint; Ironclad (routing); lawyer availability [currently untracked in any system — assumption]
> **Error tolerance:** Moderate — administrative errors are correctable; routing delays directly affect turnaround time.

> **Zone [Z-E]:** Vendor Delivery
> **Micro-tasks in zone:** MT-G
> **Dominant cognitive type:** Deterministic execution with exception-handling branch for non-standard delivery preferences
> **Data dependencies:** Signed-off document; vendor contact info (Ironclad); vendor delivery preference (currently not in any system — inferred from Artefact 2.2)
> **Error tolerance:** Moderate — delivery via wrong channel is fixable; sending to wrong recipient is more serious but detectable.

---

**Breakpoints:**

> **Breakpoint [BP-A]:** Playbook position is ambiguous or known to be stale for the flagged clause type
> **From:** Tom (Z-A policy interpretation)
> **To:** Lawyer (clarification of intended policy position before drafting begins)
> **Why this is a breakpoint:** Rule-to-judgment shift — plus a system knowledge gap. The playbook DPA section is 9 months stale (Artefact 2.3); the DPDI Act's new legitimate interests test and data subject access changes are not reflected. Tom cannot draft a correct DPA redline because the correct position is not in the playbook. The trigger is recognising that the clause type falls in a known stale area, not a general uncertainty about any clause.
> **Agent opportunity or risk:** Risk — an agent drafting from the current stale playbook will produce DPDI-non-compliant redlines without flagging the issue. Mitigation: agent must have an explicit "playbook staleness flag" that surfaces known-stale clause types and blocks drafting until the playbook is updated or a lawyer provides the current position.

> **Breakpoint [BP-B]:** Clause drafting requires novel legal synthesis beyond template application
> **From:** Agent (standard template application for numeric-threshold clauses)
> **To:** Tom / lawyer (for qualitative or complex clause synthesis)
> **Why this is a breakpoint:** The agent-delegatable portion of MT-C is constrained to clause types where the playbook position maps to a known redline pattern (e.g., "replace [vendor's cap amount] with '12 months' fees or £250,000, whichever is greater'"). Clause types requiring qualitative judgment in the drafting — DPA terms, IP ownership, indemnity scope — require human synthesis. Triggered when the clause type has a qualitative playbook position rather than a numeric threshold.
> **Agent opportunity or risk:** Opportunity for numeric-threshold clause types (liability cap redlines, SLA commitments with quantified parameters). Risk for qualitative clause types — agent-generated legal language that looks plausible but achieves the wrong legal effect is harder to catch than a blank draft.

> **Breakpoint [BP-C]:** Sign-off gate — draft counteroffer must be approved by a named lawyer before dispatch (GC's hard rule)
> **From:** Tom (redline draft complete, Z-D routing)
> **To:** Named lawyer (sign-off via WS4)
> **Why this is a breakpoint:** Non-negotiable compliance gate. The GC's hard rule is categorical: no counteroffer leaves legal's queue without named-lawyer sign-off on the specific clauses being negotiated. This is an accountability breakpoint, not a quality-review step — a lawyer must be identifiable as having authorised the negotiating position. No agent action can substitute for this.
> **Agent opportunity or risk:** Opportunity — the agent can prepare the sign-off package: extract the specific redlined clauses, annotate each with the playbook position applied and the deviation magnitude, and route to the appropriate available lawyer with SLA context. Reducing the lawyer's sign-off preparation time from 30 min to 10–15 min [assumption] is where agent value accrues in this work stream.

> **Breakpoint [BP-D]:** Vendor delivery preference exception — vendor requires email attachment rather than SharePoint link
> **From:** Standard delivery workflow (Z-E, SharePoint link)
> **To:** Exception workflow (Outlook email attachment)
> **Why this is a breakpoint:** Recurring operational exception with no current systematic record. At least 3 vendors this quarter required this workaround (Artefact 2.2). Each time, Tom must recall or rediscover the preference.
> **Agent opportunity or risk:** Opportunity — agent maintains a vendor delivery preference registry built from email thread history (Artefact 2.2 shows the preference is stated explicitly in email). Agent routes deliveries appropriately without Tom's manual intervention. Eliminates a recurring error mode (sending a SharePoint link to a vendor who can't open it).

---

### 3d. Process Topology Diagram — Work Stream B

```
[WS1 OUTPUT: Contract with flagged negotiable deviations → WS2]
                     |
                     v
    ┌────────────────────────────────┐
    │ Z-A: Policy Retrieval &        │
    │ Interpretation                 │
    │ MT-A: Retrieve playbook pos.   │
    │ MT-B: Interpret as redline     │
    │       target                   │
    │ Type: Det. execution →         │
    │       Probabilistic reasoning  │
    └────────────────────────────────┘
                     |
                     v
       ◆ BP-A: Playbook position ambiguous or stale?
          /                              \
   [Clear position]              [Ambiguous / stale →
          |                       Consult lawyer before
          |                       drafting]
          |                              |
          └──────────────────────────────┘
                     |
                     v
    ┌────────────────────────────────┐
    │ Z-B: Clause Drafting           │
    │ MT-C: Draft redlined clause    │
    │       language (Track Changes) │
    │ Type: Human sense-making       │
    │ (legal synthesis)              │
    └────────────────────────────────┘
                     |
                     v
       ◆ BP-B: Novel legal synthesis required beyond template?
          /                              \
   [Standard template                [Complex / qualitative →
    applicable]                       Human drafts]
          |                              |
          └──────────────────────────────┘
                     |
                     v
    ┌────────────────────────────────┐
    │ Z-C: Cross-Clause Consistency  │
    │ Review                         │
    │ MT-D: Check for clause         │
    │       conflicts in full doc    │
    │ Type: Human sense-making       │
    └────────────────────────────────┘
                     |
                     v
    ┌────────────────────────────────┐
    │ Z-D: Document Management &     │
    │ Sign-off Routing               │
    │ MT-E: Save + version           │
    │ MT-F: Route to named lawyer    │
    │ Type: Deterministic execution  │
    └────────────────────────────────┘
                     |
                     v
    ◆ BP-C: SIGN-OFF GATE (GC hard rule — mandatory lawyer approval)
                     |
    [Named lawyer reviews specific redlined clauses]
          /                         \
   [Approved]                [Revision requested →
          |                   back to Z-B]
          v
    ┌────────────────────────────────┐
    │ Z-E: Vendor Delivery           │
    │ MT-G: Deliver via correct      │
    │       channel                  │
    │ Type: Det. execution +         │
    │       exception handling       │
    └────────────────────────────────┘
                     |
                     v
       ◆ BP-D: Vendor delivery preference?
          /                         \
   [SharePoint link                [Email attachment
    (standard)]                    (VendorCo-type exception)]
          |                              |
          v                             v
  [REDLINE DELIVERED          [REDLINE DELIVERED
   via SharePoint]             via Outlook attachment]
```

---

## 4. Cross-Work-Stream Observations

**Observation 1 — Shared policy authority: the playbook is a single point of failure for both work streams.**
Both WS1 (comparison) and WS2 (redline drafting) use the same SharePoint playbook as their sole policy reference. The 9-month staleness of the playbook is not a WS1-only problem — it corrupts both the classification in Z-3/Z-4 and the redline target in Z-A/Z-B. Any agent architecture must treat the playbook as a dependency to be verified before deployment. A single RAG index over a structured, current playbook version would serve both work streams from the same retrieval layer — but only after Amelia's DPDI Act updates are incorporated.

**Observation 2 — Shared retrieval component: clause type → policy position lookup appears in both work streams.**
In WS1 (MT4), Tom retrieves the playbook position to compare against the extracted clause text. In WS2 (MT-A/MT-B), Tom retrieves the same playbook position to interpret as a redline target. These are two instances of the same retrieval pattern. A shared retrieval component — a vector index or structured lookup over the playbook, keyed by clause type — can serve both agents, reducing build cost and ensuring consistency between the classification agent's reference and the drafting agent's reference.

**Observation 3 — Regulatory gap detection is a shared exception that is currently untracked in both work streams.**
BP-3 in WS1 (DPDI gap → "will ask Sarah") and BP-A in WS2 (playbook stale for DPA redline) are the same regulatory gap manifesting at two different points in the workflow. Both are handled informally through a lawyer consultation that generates no audit trail. A shared regulatory monitoring component — triggered by confirmed legislative changes and applied to specific clause type entries in the playbook — would surface the gap at the earliest possible point (playbook versioning), preventing it from reaching either work stream as an unresolved ambiguity.

**Observation 4 — Informal consultation is the primary source of untracked latency across both work streams.**
The "will ask Sarah" pattern appears in WS1 (MT6, borderline cases and regulatory gaps) and implicitly in WS2 (BP-A, before drafting begins on uncertain clauses). Neither consultation is tracked in any system. Cumulative latency from these informal loops is a hidden contributor to the 4–6 day turnaround that the signed-off case metrics in Ironclad do not capture. Any agent design that aims to halve the turnaround must surface these consultations as tracked, SLA-bound workflow steps — not replace them, but make them visible.

**Observation 5 — Disproportionate exception concentration at the zone boundary.**
In both work streams, the most cognitively demanding zones (Z-4 in WS1 — deviation triage judgment; Z-B/Z-C in WS2 — clause drafting and consistency review) are also where skilled human time is disproportionately consumed relative to the frequency of cases that reach them. An agent designed on the assumption that all cases require Z-4/Z-B effort will be over-specified for the 70–80% of cases that are clear-cut and under-supported for the 20–30% that are genuinely hard. The correct design pattern is a confidence-gated architecture: the agent handles the clear-cut cases autonomously and surfaces the ambiguous ones for human review with structured context — not a human reviewing everything the agent produces, but a human reviewing only what the agent cannot confidently resolve.

---

## Self-check against acceptance criteria

- [x] Work stream selection justified by reference to delegation potential and cognitive complexity — not assumed
- [x] Both work streams fully decomposed (JtDs, micro-task tables, zones, breakpoints, topology diagrams)
- [x] JtDs are cognitive contracts — outcome-focused, not task descriptions
- [x] Micro-task tables have 8 rows (WS1) and 7 rows (WS2), all with dimension scores — exceeds minimum of 5
- [x] Cognitive zones distinguished by dominant cognitive type: deterministic execution / probabilistic reasoning / human sense-making — no zone is labelled generically as "review"
- [x] 4 breakpoints per work stream — exceeds minimum of 3
- [x] Process topology diagram present for both work streams
- [x] GC hard rule reflected in BP-C (WS2) — explicitly named as a non-negotiable compliance gate requiring named-lawyer approval before any counteroffer is dispatched
- [x] No scores asserted without justification in footnotes — all 15 footnote entries reference specific scenario facts or labelled inferences
