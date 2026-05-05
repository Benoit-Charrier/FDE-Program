# D0 — Discovery
**Scenario:** Helix Workforce Software — Vendor Contract Clause Review

---

## 1. Lived Process Narrative

*Reconstruction note: the sequence below is derived from the four work streams, their volumes and times, and the three artefacts in the enriched scenario. Where I reconstruct beyond those sources I label the inference explicitly.*

**Day 0 — A contract lands**

A vendor's procurement team emails their standard MSA to Tom (the paralegal) via Outlook. This is the most common intake path. Separately, when a new enterprise deal is progressing in Salesforce, the sales rep flags that a contract has arrived, and Tom is the person who connects the Salesforce opportunity to the inbound document. There is no described handoff protocol — *[INFERENCE: Tom monitors both Outlook and Salesforce for incoming contracts and decides when to begin review based on his own prioritisation; there is no described automated intake logging].*

Tom downloads the Word document and saves it to SharePoint. Whether and when he creates a case in Ironclad at this stage is not described — *[INFERENCE: some CLM setup step happens before formal review begins, but the scenario does not confirm when or by whom].*

**Day 1 — First-pass clause classification (~25 min/case, all 300/quarter)**

Tom opens the Word document and the SharePoint playbook page side by side. He works through the contract section by section, hunting for each of the 7 clause types: liability cap, DPA, termination, IP, SLA, governing law, indemnity. Vendor contracts do not use standardised section headings — what Helix calls "Limitation of Liability" may appear as "Aggregate Damages Cap," "Maximum Exposure," or buried within a "General Provisions" section. Tom identifies these through a combination of scanning headings and reading language to determine what type of clause it is. *[INFERENCE: this is not described explicitly in the scenario but is a necessary consequence of reviewing 15–40 page unstructured Word documents from hundreds of different vendors.]*

For each clause Tom finds, he compares it against the playbook position and makes a margin note — as shown in Artefact 2.1 — capturing both his classification and his reasoning. Three distinct outcomes emerge at the clause level:

1. **Routine accept**: the clause is within playbook tolerance and Helix's standard position is to accept it. Example from Artefact 2.1: VendorCo's 90-day termination-for-convenience clause — Tom notes "Ours is 30 days for our paper, 90 for theirs. Routine — accept." No further action.

2. **Negotiable deviation — redline**: the clause is below playbook minimum but within the range Tom is authorised to redline without escalation. Example from Artefact 2.1: VendorCo's liability cap at 6 months / £50,000 versus the playbook minimum of 12 months / £250,000 for enterprise — Tom notes "FLAG — but the term is borderline negotiable, not escalation. Will redline to playbook position."

3. **Uncertain — informal escalation**: the clause touches an area where Tom knows the playbook is stale or where he cannot confidently classify. The DPDI Act example in Artefact 2.1 is the clearest signal: the DPA clause nominally references UK GDPR and DPA 2018, but Tom notes "DPDI updates aren't reflected — playbook is stale on this. Honestly not sure if this needs escalation. Will ask Sarah." This is a third path that does not appear in the documented 70/20/10 framework. Tom routes informally to one of the commercial lawyers ("Sarah") rather than escalating through a formal channel. *[SCENARIO FACT: the "will ask Sarah" note is explicit in Artefact 2.1.]* The existence of this informal loop means the actual escalation rate is higher than 10% at the consultation stage — it just does not all become formal escalated clause review.

At the end of first-pass, Tom has a contract-level classification: standard (accept as-is), negotiable (he will redline), or escalation-required (needs a senior lawyer). *[INFERENCE: the decision logic for contract-level classification from clause-level results — e.g., what happens if 5 clauses are standard and 1 requires escalation — is not described in the scenario and is a genuine unknown.]*

**Redlining (~45 min/case, ~60/quarter)**

For contracts classified as having negotiable deviations, Tom opens the Word document, enables Track Changes, navigates to the flagged clauses, and replaces the vendor's language with Helix's playbook position. The playbook provides position statements (e.g., "12 months / £250,000 for enterprise liability cap") but does not necessarily provide pre-written substitute clause language — *[INFERENCE: Artefact 2.3 shows the playbook as bullet-pointed position criteria, not ready-to-paste legal text, suggesting Tom synthesises the clause language himself.]*

After drafting the redline, the contract enters the counteroffer drafting and sign-off work stream. The redlined Word document is not sent directly to the vendor by Tom — sign-off from a named lawyer is required first (see Work Stream 4 below).

A recurring operational friction arises here: some vendors cannot accept SharePoint links (at least 3 this quarter per Artefact 2.2). When VendorCo's Linda Carrington requests "please return the redlined Word doc as an attachment to this thread," Tom must manually re-attach the document via Outlook rather than sharing a SharePoint link. This workaround is not in any SOP — Tom treats it as a pragmatic adaptation and flags it to Amelia as an FYI, not as a process exception requiring escalation.

**Escalated clause review (~90 min/case, ~30/quarter)**

Contracts with clauses classified as requiring senior review are routed to one of the three commercial lawyers. *[INFERENCE: the routing mechanism — Ironclad task assignment, Outlook email, or informal message — is not described in the scenario and is a genuine unknown.]* The lawyer reviews the flagged clauses in the context of the full agreement, applies their legal expertise, and determines:

- What is the specific legal risk to Helix in this clause?
- What is Helix's preferred position and minimum acceptable outcome?
- Is this clause so non-standard that Amelia should be consulted before a position is framed?

The lawyer then drafts the redlined counteroffer position, producing a marked-up Word document. *[INFERENCE: lawyers may draw on prior deal precedent or comparable clause language from earlier contracts, but no structured precedent library is mentioned in the scenario. If such a library exists in SharePoint, its structure and completeness are unknown.]* The lawyer's draft then also feeds into the counteroffer drafting and sign-off work stream.

**Counteroffer drafting & sign-off (~30 min/case, ~90/quarter)**

The 90 cases in this work stream represent the aggregate of Tom's 60 redlined contracts and the 30 escalated-lawyer redlines — all require sign-off before the counteroffer leaves legal's queue. This is Amelia's hard rule: no counteroffer leaves without a named lawyer's sign-off on the specific clauses being negotiated. *[SCENARIO FACT.]*

A named lawyer reviews the draft redline — specifically the flagged clauses — approves the negotiating position, and authorises the counteroffer to be sent. For Tom's redlined cases, this means a lawyer who did not draft the redline must still review and sign off. For escalated cases, the drafting lawyer presumably self-approves, or a second lawyer confirms. *[INFERENCE: the sign-off mechanism — whether it is a digital approval in Ironclad, an email reply, or an oral instruction to Tom — is not described in the scenario.]*

Once signed off, the counteroffer is sent to the vendor — via SharePoint link for most vendors, via Outlook email attachment for those who cannot handle SharePoint links. The case is then closed or enters a negotiation round-trip if the vendor responds with counter-redlines.

**Where queues form**

- *At Tom's desk*: all 300 first-pass cases pass through a single person. Tom is not described as having a backup. Any absence or concurrent surge creates a backlog.
- *At the informal consultation loop*: when Tom writes "will ask Sarah," he stops and waits for a response from a lawyer who has their own queue. This waiting time is not tracked anywhere.
- *At the sign-off gate*: 90 counteroffers per quarter require a named-lawyer approval step. Lawyer availability — they are also handling escalated reviews, client matters, and Amelia's requests — determines throughput here. When lawyers are busy, this gate is the primary cause of the 4–6 day turnaround.

**Informal knowledge being applied**

- Tom knows from experience which deviation magnitudes Helix routinely accepts in negotiation, even when this is not codified in the playbook (e.g., accepting 90-day termination).
- Tom knows vendor-specific quirks that are not in any system (e.g., VendorCo's email-only requirement).
- Amelia's DPDI Act update (Artefact 2.3) exists on a printed sticky note on her desk, not in the digital playbook — meaning the most current regulatory knowledge is physically inaccessible to anyone reviewing contracts from their desk.
- "Sarah" is the informal escalation point for borderline regulatory questions — a role not described in any documented process.

---

## 2. Points of Pain Inventory

| Work Stream | Pain Description | Estimated Volume | Pain Level | Key Data/Systems Involved | Candidate for Automation? |
|---|---|---|---|---|---|
| WS1: First-pass clause classification | Single person (Tom) processes all 300 contracts manually against a 9-month-stale playbook; DPDI uncertainty creates untracked informal escalations; no backup when Tom is unavailable | 300/quarter (~25 min each = ~125 hrs/quarter) | **H** | Outlook (intake), SharePoint (playbook), Word (contract document), Ironclad (case record) | Yes — high-volume, pattern-matching against a reference document |
| WS2: Standard-deviation redlining | Redline drafting requires synthesis of playbook position into clause language; delivery friction for vendors requiring email attachments (3+ this quarter); playbook staleness creates ambiguity in what "standard" redline position is | 60/quarter (~45 min each = ~45 hrs/quarter) | **M** | Word (Track Changes), SharePoint (playbook + storage), Outlook (email-only delivery workaround) | Partial — clause language generation can be agent-assisted; vendor-delivery workaround can be automated |
| WS3: Escalated clause review | Senior lawyer time (90 min/case) consumed by reviewing unusual clauses; no described precedent library to accelerate research; informal consultation with Amelia for the most novel issues adds untracked latency | 30/quarter (~90 min each = ~45 hrs/quarter) | **H** (per-case cost) | Word, SharePoint (playbook), Ironclad; precedent library — existence unconfirmed | Limited — judgment-intensive; agent can reduce prep time but not substitute lawyer analysis |
| WS4: Counteroffer drafting & sign-off | Named-lawyer sign-off is a hard gate on every outbound counteroffer; sign-off mechanism is undescribed (no evidence of instrumented approval workflow); 90 cases/quarter queue behind lawyer availability; email-attachment workaround for some vendors adds manual steps | 90/quarter (~30 min each = ~45 hrs/quarter) | **M** | Ironclad (case management), Outlook (outbound delivery), Word (final document) | Partial — preparation and routing can be automated; sign-off act must remain human |

**Pain level justifications:**

- **WS1 (H):** Rated high because: (a) it is the bottleneck for all downstream work streams — nothing moves until Tom completes first-pass; (b) all volume (300 contracts) passes through one person; (c) the playbook staleness means informal judgement calls are made on live contracts where policy is ambiguous; (d) the untracked "will ask Sarah" escalation path represents hidden latency that the SOP does not account for.
- **WS2 (M):** Rated medium because the scope of each case is defined before redlining begins (Tom has already flagged which clauses need redlining), making the task more bounded than first-pass. The email-attachment workaround is friction but is currently managed. The primary remaining uncertainty is playbook currency for the DPA clauses.
- **WS3 (H per-case):** Rated high on per-case cost (senior lawyer time at £[assumption] per hour × 90 min = significant cost per case), but the volume is low (30/quarter). The impact is concentrated: if the three commercial lawyers are simultaneously carrying escalated cases alongside client work, the queue at WS3 drives WS4 delays.
- **WS4 (M):** Rated medium because the drafting component is downstream of the hard work (WS2 or WS3 already produced the redline), but the sign-off gate's lack of instrumentation means there is no SLA visibility on how long counteroffers wait for approval before going out.

---

## 3. Cognitive Workload Hotspots

> **Hotspot [WS1-1]:** First-pass clause classification — identifying and classifying clause types across unstructured vendor documents
> **What the human does:** Tom reads an unstructured 15–40 page Word document, identifies which sections correspond to each of the 7 playbook clause types despite varied headings and formatting, extracts the relevant language, and compares it against the playbook position to determine: compliant / negotiable deviation / escalation-required.
> **Why a machine can't trivially replace this today:** Clause boundaries in vendor contracts are not standardised. A section called "General Provisions" may contain liability, indemnity, and governing law language in adjacent paragraphs. Semantic understanding of legal text is required to identify and isolate the relevant clause content before any comparison to the playbook can happen. Rule-based systems and keyword matchers fail on the breadth of variation across 300 vendor drafting styles per quarter.
> **Delegation signal:** This becomes delegatable when: (a) an LLM-based extraction layer can reliably identify and isolate clause-type candidates across the document (not just by heading, but by semantic content); (b) playbook comparison thresholds are made explicit and machine-readable (e.g., "liability cap compliant = ≥12 months AND ≥£250k for enterprise"); (c) confidence-scored outputs route low-confidence extractions to human review. The extraction task is structurally an LLM extraction + retrieval-augmented comparison problem — well within current capability.

> **Hotspot [WS1-2]:** First-pass clause classification — borderline triage judgment (negotiable vs. escalation-required)
> **What the human does:** When a clause deviates from the playbook, Tom must decide whether the deviation is within the range he can redline (20% bucket) or requires a senior lawyer (10% bucket). Artefact 2.1 shows this judgment call explicitly: "Cap is below playbook minimum. FLAG — but the term is borderline negotiable, not escalation." He also faces a third category the SOP does not document: "uncertain due to regulatory gap — ask informally."
> **Why a machine can't trivially replace this today:** The threshold between "negotiable" and "escalation-required" is not codified in the playbook as written. Tom applies institutional knowledge about what Helix will and won't accept in negotiation, combined with informal knowledge from prior escalations. The DPDI Act gap makes this worse: for DPA clauses, Tom doesn't know if the current playbook position is even valid, making automated comparison against a stale reference actively misleading.
> **Delegation signal:** Becomes delegatable if: (a) the playbook is updated with explicit deviation thresholds for each clause type (not just positions, but "below threshold X = negotiate; below threshold Y = escalate"); (b) regulatory gaps like the DPDI Act are resolved by updating the playbook before the agent is deployed; (c) the agent uses a confidence-scored output to surface borderline cases for human triage rather than classifying them unilaterally.

> **Hotspot [WS2-1]:** Standard-deviation redlining — synthesising playbook position into redlined clause language
> **What the human does:** Tom knows Helix wants a 12-month / £250k liability cap. He must draft replacement clause language that achieves that position within the structure of the vendor's existing contract — matching the grammatical form, numbering, and legal precision of the surrounding document. The playbook gives positions, not pre-written substitute clauses.
> **Why a machine can't trivially replace this today:** Generating legally precise clause language that (a) achieves the playbook position, (b) fits the surrounding contract structure, and (c) is formulated to hold up in a dispute, requires legal synthesis beyond template filling. The playbook in Artefact 2.3 shows position bullet points, not ready-to-insert redline text.
> **Delegation signal:** Becomes delegatable if: (a) the playbook is extended to include standard redline substitute language for each clause type and deviation scenario (not just policy positions); (b) the agent is tasked with retrieving and applying standard redline language, with a human reviewing fit — rather than generating novel clause text from scratch; (c) a lawyer reviews agent-drafted redlines before sign-off anyway (which the existing WS4 gate already provides).

> **Hotspot [WS3-1]:** Escalated clause review — framing a negotiation position for a non-standard clause
> **What the human does:** A senior lawyer reads an unusual clause that Tom could not classify against the playbook. The lawyer must: (a) understand what legal risk the clause creates for Helix; (b) determine what position Helix should take; (c) assess how hard to push in negotiation given the vendor relationship and deal context; (d) draft the redlined counteroffer position with appropriate legal language.
> **Why a machine can't trivially replace this today:** This requires synthesis of legal risk analysis, institutional risk appetite, negotiation strategy, and deal-specific context (which Helix almost never knows the full picture of from the contract text alone — context lives in Salesforce and in the lawyer's head). The clause is unusual by definition — it does not match the playbook, so retrieval-augmented comparison is of limited help.
> **Delegation signal:** Partially delegatable: an agent could retrieve comparable precedents from prior escalated decisions and draft a position memo (risk summary + proposed position) as input to the lawyer's review — reducing 90 min to perhaps 30–40 min of net lawyer time. Full delegation is not appropriate. This requires a structured precedent library to exist first.

> **Hotspot [WS4-1]:** Counteroffer drafting & sign-off — named-lawyer approval of specific negotiated clauses before dispatch
> **What the human does:** A named lawyer reviews the specific clauses being negotiated in the draft counteroffer, confirms the redline position is within acceptable parameters, and formally authorises the counteroffer to leave Helix's queue. This is simultaneously a legal analysis act and an accountability act — someone with professional standing is putting their name on a negotiating position.
> **Why a machine can't trivially replace this today:** The GC's hard rule is categorical: this is not a complexity threshold but an accountability requirement. Legal liability can flow from the contents of a counteroffer; Amelia has determined that a named lawyer must be accountable for that position. The rule's rationale likely connects to professional indemnity, regulatory requirements, and internal risk governance — not purely to accuracy concerns that an agent could solve.
> **Delegation signal:** The sign-off act must remain human. The delegatable adjacent work is: (a) preparing the sign-off package (summarising which clauses are under negotiation, the redlined positions, and any notes from WS2 or WS3); (b) routing it to the right lawyer with SLA awareness; (c) capturing the approval in a system of record with an audit trail. An agent handling preparation and routing reduces the 30-min case time without touching the approval decision itself.

---

## 4. Points of Friction for Procurement

From the perspective of external vendor procurement teams, Helix's 4–6 business day turnaround means that a vendor who submits their MSA on Monday morning will not receive a redlined response until Thursday or the following Monday — at best. As Artefact 2.2 shows, VendorCo's procurement team has its own internal 5-business-day target for in-house review once they receive a redline response. This means the total round-trip for a single negotiation cycle — Helix receives → Helix responds → vendor reviews → vendor responds — approaches two calendar weeks per cycle, before any second-round negotiation begins. For enterprise software procurement at a company like Helix, where deals involve banks, retailers, and NHS trusts with their own governance timelines, this creates compounding delays: each additional round-trip adds another two weeks to a process that is already on the critical path for deal close. From the CRO's internal perspective, enterprise sales targets are directly dependent on deal velocity; each day a contract sits in legal's queue is a day the sales team cannot advance to signature. With ~300 contracts per quarter and the CRO explicitly demanding Legal halve the turnaround, the arithmetic is clear: the current 4–6 day cycle needs to reach ≤2–3 days, which cannot happen without removing the first-pass classification bottleneck.

---

## 5. Known Unknowns

> **Unknown [U-1]:** How is Ironclad actually used in the current intake and review workflow?
> **Why it matters for agent design:** Ironclad is the named CLM with REST APIs. If it is the system of record for contract lifecycle — with contracts logged on intake, work stream stages tracked, and approvals recorded there — it is the natural integration target for an agent. If Ironclad is sparsely used (contracts tracked in SharePoint or managed via email threads), the integration architecture must compensate with a more complex data model, and the clean timestamping needed for turnaround measurement (as in D0A's metrics) may not exist yet.
> **How to discover:** Ask Tom to walk through a real contract intake from first email receipt to Ironclad entry — what does he actually open, what does he type, and at what point in the process? Ask to see the Ironclad case view for one recent contract.

> **Unknown [U-2]:** What is the machine-readable structure of the playbook?
> **Why it matters for agent design:** The playbook is the agent's primary reference authority. Artefact 2.3 shows one section (DPA) as structured bullet-point criteria. If the full playbook is similarly structured — clause type → position criteria → standard redline language — it can be directly indexed for retrieval-augmented comparison. If it is narrative prose, a Word document with embedded commentary, or split across multiple versions and sticky notes, the RAG architecture becomes significantly more complex and the risk of retrieval errors increases.
> **How to discover:** Ask to see the full playbook as Tom uses it day-to-day (the live SharePoint version, not a curated export). Ask: "when you check a DPA clause, do you click to a specific section, or do you search for it?" Ask Amelia: "what is the authoritative version of the playbook — the SharePoint page, the printed copy on your desk, or somewhere else?"

> **Unknown [U-3]:** How are escalations currently routed and tracked?
> **Why it matters for agent design:** The agent's escalation trigger logic must integrate with real routing infrastructure. If escalations today happen via Outlook email to a specific lawyer, the agent needs to generate a structured escalation email (or an Ironclad task). If there is no tracking system and escalations are informal, the agent design must either integrate with an existing tool or propose a new mechanism — which increases implementation scope and organisational change.
> **How to discover:** Ask Tom: "when you decide a contract needs escalation to a senior lawyer, what do you do next — exactly? Show me the last escalation you made." Ask to see the escalation queue as it exists right now.

> **Unknown [U-4]:** What is the operational mechanism for named-lawyer sign-off, and is it currently auditable?
> **Why it matters for agent design:** The GC's hard rule requires named-lawyer sign-off, but the agent design must implement this as a system constraint — not just a policy. If sign-off currently happens via an unlogged Outlook reply or verbal authorisation, building the agent around this mechanism creates audit trail risk. The design may need to introduce a formal approval token (e.g., a lawyer clicking "Approve" in Ironclad) rather than simply preserving the current informal mechanism.
> **How to discover:** Ask Amelia: "if a counteroffer was sent to a vendor and six months later there was a dispute about what was agreed, where would I find the documented record of who authorised that specific redline?" If she cannot point to a specific system entry, the audit trail gap is confirmed.

> **Unknown [U-5]:** What is Tom's actual decision logic for the contract-level 70/20/10 classification?
> **Why it matters for agent design:** The agent must replicate (or improve on) Tom's classification logic. If a contract has one escalation-required clause and five standard clauses, is the entire contract escalated, or only the flagged clause? The answer determines whether the agent produces a contract-level classification or a clause-level classification — and these are architecturally different outputs with different downstream consequences for work stream routing.
> **How to discover:** Walk Tom through two or three past contracts — one clearly standard, one with mixed clause-level results — and ask him to narrate his classification decision at each step. Ask: "if a contract has four standard clauses and one that needs escalation, what do you do?"

> **Unknown [U-6]:** Do contract complexity and structure vary materially by counterparty type or intake source?
> **Why it matters for agent design:** Helix's customers include banks, retailers, and NHS trusts. Bank procurement paper is typically more complex and more prescriptive than a technology vendor's standard MSA. If contracts from different counterparty types require qualitatively different classification logic, a single agent model may perform well on the modal case (standard SaaS MSA) but poorly on outlier types. The agent's confidence scoring and escalation triggers may need to be calibrated separately by contract type.
> **How to discover:** Ask Tom: "in your experience, are contracts from NHS trusts significantly different from those from banks or tech vendors? Are there types you see infrequently that are always harder to classify?" Ask Amelia which counterparty types generate the most escalations.

> **Unknown [U-7]:** Who owns the playbook, and what is the process for updating it?
> **Why it matters for agent design:** An agent's classification accuracy is bounded by the currency of its policy reference. Amelia's sticky note (Artefact 2.3) confirms the DPDI Act updates have been on the radar since at least March but not incorporated. If the playbook update process is ad hoc — a GC and one lawyer discuss it informally, "never get round to it" — the agent may classify DPA clauses as compliant against outdated policy, creating a compliance risk that is harder to detect than the human's current uncertainty (which at least surfaces as a "will ask Sarah" flag).
> **How to discover:** Ask Amelia: "who is accountable for keeping the playbook current? What would trigger an update outside of a regulatory change? How would we know when the playbook is authoritative again?" Ask to see if there is a version history or review cadence documented anywhere.

---

## Self-check against acceptance criteria

- [x] Lived process narrative describes actual work (queues, informal escalations, shortcuts, workarounds) not SOP-layer description
- [x] All four work streams appear in the Points of Pain table
- [x] Pain levels justified in notes below the table — not asserted
- [x] Every number traces to the scenario (300/quarter, 25 min, 60/quarter, 45 min, 30/quarter, 90 min, 90/quarter, 30 min, 4–6 days) or is labelled as inference/assumption
- [x] 7 genuine unknowns in the required format (exceeds minimum of 5)
- [x] Every hotspot includes a delegation signal — specific condition that would make it delegatable, not just "this is hard"
- [x] GC's hard rule (named-lawyer sign-off on specific clauses) appears in WS4 pain, WS4-1 hotspot, and U-4 unknown
