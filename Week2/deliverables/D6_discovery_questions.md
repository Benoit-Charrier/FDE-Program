# D6 — Discovery Questions for the Main Stakeholder
**Scenario:** Helix Workforce Software — Vendor Contract Clause Review

---

## 1. Stakeholder Context

**Amelia Forsythe — General Counsel, 12 years at Helix.** Amelia oversees the 5-person Legal & Commercial team, owns the vendor contract review process end-to-end, and is the named enforcer of the GC hard rule: no counteroffer may leave Legal's queue without a named lawyer's sign-off on the specific clauses being negotiated. Her primary concern about AI involvement is not AI error in general — it is the loss of lawyer accountability at the governance boundary. Twelve years of building a sign-off culture means her trust in any automation depends on whether the governance gate remains intact and auditable, not just on accuracy metrics. The secondary and near-term concern is the DPDI Act compliance gap: the playbook has been stale for 9 months, with Q1 updates not yet incorporated, and any agent that classifies DPA clauses before that update is a latent compliance liability. Her business pressure is real — the CRO is pushing to halve turnaround from 4–6 days — but she has already held the line on quality. An agent that trades legal risk for speed will not earn her sign-off. What will earn her trust: demonstrable accuracy on the standard path, an auditable HITL trail for every deviation, and hard architectural proof that no counteroffer can exit Legal without a named lawyer's approval token.

---

## 2. Questions Whose Answers Would Change the Design

---

### Category A: Policy/Knowledge Base Structure and Machine-Readability

> **Q1: Is the playbook a single SharePoint page with sections for each of the 7 clause types, or is it distributed across multiple documents, pages, or linked files?**
> **Category:** A
> **What I already infer from the scenario:** The playbook is on SharePoint (v3.4, 9 months stale). It covers 7 clause types. Beyond that, its structural organisation is not described.
> **If the answer is [single structured page with one section per clause type]:** RAG chunking is straightforward — one document, chunk by clause-type section. Retrieval drift risk is low. Index rebuild on version update is a single-document operation.
> **If the answer is [multiple documents or linked SharePoint pages — e.g., a master index linking to per-clause-type pages, or separate Word templates]:** Need a multi-document RAG with cross-document cross-reference handling. Higher risk of retrieving incomplete policy for a clause type (e.g., the IP section links to a separate IP principles document not included in the index). Retrieval architecture becomes a crawl-and-link problem, not a single-document index.
> **Why this matters more than a generic question:** The answer determines whether the RAG index is a solved engineering problem or an open architecture decision that must be resolved before any agent can produce reliable clause comparisons.

---

> **Q2: What is the formal process for updating the playbook — does Amelia approve every change before it is published, or can any team member edit the SharePoint page?**
> **Category:** A
> **What I already infer from the scenario:** Amelia annotated the playbook herself (Artefact 2.3 sticky note) and discussed DPDI updates with Sarah without completing them. This suggests updates are informal.
> **If the answer is [formal approval — Amelia or a named lawyer approves changes before the page goes live]:** Can instrument a SharePoint webhook on version publication: new version triggers RAG reindex AND requires the agent's configuration to be updated with the new playbook version number before it processes further DPA clauses. This is the deployment gate for DPA classification.
> **If the answer is [informal — anyone on the team can edit; no approval workflow]:** Intermediate edits can appear in the RAG index before they are authoritative. Must add a human approval gate between SharePoint edit and RAG reindex — otherwise the agent can classify against half-edited playbook content. Changes the index architecture from event-driven to gated.
> **Why this matters more than a generic question:** An informal update process means playbook integrity is not structurally enforced — the agent's accuracy depends on whoever last saved a draft, not on a reviewed position. This is a governance risk independent of model quality.

---

> **Q3: Are there vendor-specific playbook exceptions — positions that apply only to certain vendors or vendor categories (e.g., hyperscaler infrastructure vendors get different DPA terms, or known large-client procurement teams have pre-agreed positions)?**
> **Category:** A
> **What I already infer from the scenario:** The playbook describes standard positions. No vendor-specific exceptions are mentioned. Artefact 2.2 describes an operational exception (email-only redline delivery), not a policy exception.
> **If the answer is [yes — some vendors have pre-agreed exceptions recorded somewhere]:** Classification logic must be vendor-aware before applying playbook comparison. The agent must retrieve the vendor exception (if one exists) from wherever it is stored — Ironclad, a separate SharePoint list — before comparing against the standard playbook position. Adds a vendor-lookup dependency and exception handling path.
> **If the answer is [no — standard playbook position applies uniformly]:** Current design is sufficient. No vendor-exception lookup needed. Simplifies the retrieval architecture significantly.
> **Why this matters more than a generic question:** A vendor-exception that the agent doesn't know about produces a false-deviation flag — Tom spends review time on a "deviation" that was already agreed. At 300 contracts/quarter, even a 5% false-deviation rate (15 contracts) is meaningful HITL overhead.

---

### Category B: The Routing/Classification Logic — How It Actually Works Today

> **Q4: For qualitative clause types — IP ownership, indemnity scope, governing law — how does Tom currently decide whether a clause is standard, negotiable, or escalation-required? Does he match it against specific playbook language, or does he apply judgment about whether the intent is equivalent even if the wording differs?**
> **Category:** B
> **What I already infer from the scenario:** Tom performs first-pass classification across all 7 clause types. The playbook defines the positions. The distinction between standard and deviation is assumed to follow the playbook, but Tom is a paralegal — the degree to which he applies literal matching vs. interpretive judgment is not described.
> **If the answer is [literal match — Tom compares wording against specific playbook sections; equivalent intent in different words gets flagged as deviation]:** Can implement semantic similarity with a tight threshold (≥0.85 cosine similarity between extracted clause and playbook section). The agent's behaviour mirrors Tom's: similar wording to playbook → standard; different wording → deviation. Calibration against Tom's historical decisions is tractable.
> **If the answer is [intent judgment — Tom decides if the clause achieves the same commercial outcome even if wording differs]:** Semantic similarity alone is insufficient. Need a structured comparison prompt that asks the agent to reason about commercial intent, not just textual similarity. The confidence threshold must be higher, HITL triggers more frequent, and calibration harder because Tom's reasoning is implicit.
> **Why this matters more than a generic question:** This is the single most important question for confidence threshold design. A mismatch between the agent's matching logic and Tom's actual classification method is the primary source of false classifications — the failure mode with the highest downstream cost.

---

> **Q5: Of the ~30 escalation-required contracts per quarter, what are the most common triggers? Are they consistently one or two clause types, or is escalation spread across all 7 types unpredictably?**
> **Category:** B
> **What I already infer from the scenario:** 10% of 300 contracts are escalation-required. The scenario does not describe which clause types drive escalation most frequently.
> **If the answer is [concentrated — escalation is almost always DPA + IP ownership, rarely the others]:** Can apply higher confidence thresholds and more detailed prompting specifically to DPA and IP. Other clause types can use a lighter-weight comparison path. Threshold design is clause-type specific.
> **If the answer is [distributed — escalation occurs across all 7 clause types without a clear pattern]:** Must apply uniform high scrutiny to all 7 types. Cannot optimise by clause type. A higher baseline HITL rate is needed because uncertainty on any clause type is equally likely. The ≤35% HITL target becomes harder to hit with a uniform high threshold.
> **Why this matters more than a generic question:** Clause-type-specific threshold design is a significant optimisation opportunity. Without this information, the agent either applies uniform thresholds (accepting more false classifications) or applies uniformly high thresholds (accepting more HITL than needed). The answer enables or forecloses that optimisation.

---

> **Q6: When Tom currently routes a contract to WS2 or WS3, does he record why — the specific clause and the specific deviation — or is the routing decision recorded without a reasoning trail?**
> **Category:** B
> **What I already infer from the scenario:** Tom performs classification and routes. Artefact 2.1 shows Tom's annotations on a specific contract, which suggests he does annotate some decisions. Whether this is systematic is not stated.
> **If the answer is [yes — Tom documents reasoning per clause per routing decision, even informally in Ironclad notes or a spreadsheet]:** Tom's historical routing decisions are a usable calibration dataset. Can compare agent classifications against Tom's historical decisions to calibrate confidence thresholds before go-live. Reduces the cold-start accuracy problem.
> **If the answer is [no — Tom makes the decision but doesn't document reasoning; only the routing outcome is recorded]:** No structured calibration dataset available before go-live. Must start with conservative thresholds and calibrate on live production data (with HITL as the correction signal). Calibration cycle is slower. Go-live accuracy claims are based on assumptions, not measured baselines.
> **Why this matters more than a generic question:** The calibration strategy and the go-live accuracy confidence are entirely different depending on whether historical decisions are recoverable. This affects the honest claim we can make to Amelia about accuracy at launch.

---

### Category C: The Governance/Approval Rule — Exactly How It Works Operationally

> **Q7: When a named lawyer signs off on a counteroffer today, how is that sign-off recorded — is it an action in Ironclad, an email approval, a physical signature, or something else?**
> **Category:** C
> **What I already infer from the scenario:** The GC hard rule requires a named lawyer's sign-off. Ironclad is used as CLM. Whether sign-off is currently captured in Ironclad as a structured field action or via an adjacent channel (email thread, verbal confirmation) is not stated.
> **If the answer is [Ironclad — sign-off is recorded as a named field action or approval step within the case record]:** The approval token architecture uses Ironclad's native approval workflow. The agent's hard stop (never write a sign-off field) maps directly to a specific Ironclad field the agent's API credentials are denied write access to. Clean, auditable, and the governance gate is structurally enforced in the system.
> **If the answer is [email or verbal — sign-off is communicated outside Ironclad; someone manually updates Ironclad or it isn't recorded at all]:** Must build an email-to-Ironclad bridge or enforce a sign-off recording step as a new process requirement. The governance gate cannot be structurally enforced in the agent until the sign-off channel is formalised. This is a pre-deployment process gap, not a model design gap.
> **Why this matters more than a generic question:** The entire approval token architecture depends on this answer. If the sign-off channel is currently informal, the agent is being designed to enforce a governance rule that the current process does not structurally enforce — and that gap must be addressed before deployment, not assumed away.

---

> **Q8: Who can provide the named-lawyer sign-off — can any of the 3 commercial lawyers sign off on any clause type, or is sign-off authority scope-limited (e.g., only Amelia signs off on DPA clauses, only senior lawyers sign off on indemnity clauses)?**
> **Category:** C
> **What I already infer from the scenario:** The rule is "a named lawyer" — not "Amelia specifically." Three commercial lawyers are on the team. Whether authority is differentiated by clause type is not stated.
> **If the answer is [any named lawyer can sign off on any clause]:** Routing logic routes deviation packages to "named lawyer (any available)." Queue management is simple. The agent's routing decision for WS3 or WS4 cases does not need a lawyer-to-clause-type lookup.
> **If the answer is [sign-off authority is clause-type specific — certain clauses require a more senior reviewer or Amelia specifically]:** The agent must route each deviation package to the correct lawyer based on the deviated clause types. Requires a lawyer-to-clause-type authority mapping in agent configuration. If Amelia is the only lawyer who can sign off on DPA deviations, the ET-2 escalation path must route to Amelia directly, not to the next available lawyer.
> **Why this matters more than a generic question:** An incorrect routing to a lawyer without authority for a given clause type produces a sign-off that doesn't satisfy the GC hard rule — a compliance failure dressed as a process success. The authority mapping must be correct before deployment.

---

> **Q9: Does the sign-off apply at the contract level — one lawyer approves the whole counteroffer package — or at the clause level — each deviated clause receives individual sign-off?**
> **Category:** C
> **What I already infer from the scenario:** The GC hard rule specifies sign-off on "the specific clauses being negotiated" — suggesting clause-level intent. But operational practice may be contract-level package approval.
> **If the answer is [contract level — one approval covers the whole negotiation package]:** The approval token is a single field on the case record. The agent's ReviewDecision entity has one approval token per contract. Ironclad workflow is a single approval action.
> **If the answer is [clause level — each deviated clause requires independent sign-off]:** The ReviewDecision entity must support per-clause approval tokens. The Ironclad workflow must support multi-step sequential approvals. The agent's structured output must present each deviated clause as a distinct item awaiting individual approval — not a single package. Significantly increases implementation complexity and Ironclad workflow requirements.
> **Why this matters more than a generic question:** The approval workflow architecture in the entity model (ReviewDecision structure) and Ironclad integration depends entirely on whether this is one token or N tokens. Getting this wrong means building an approval system that the lawyers won't use.

---

### Category D: Exception Patterns and Edge Cases

> **Q10: What makes a clause escalation-required versus merely negotiable in practice? Is it the magnitude of deviation from playbook, the clause type, or something else — like the vendor's commercial profile, whether the clause is linked to a regulatory obligation, or whether the deviation touches a personally negotiated carve-out?**
> **Category:** D
> **What I already infer from the scenario:** The routing split is 70/20/10. Escalation-required contracts (~30/quarter) proceed to WS3 for senior lawyer review. What makes them escalation-required versus negotiable is not described beyond the implicit standard that paralegal redline is insufficient.
> **If the answer is [magnitude and type — specific numeric thresholds (e.g., liability cap below X% of playbook floor) or specific clause types always escalate]:** Can encode escalation rules as explicit thresholds per clause type. ET-5 (>50% numeric deviation) generalises. Classification logic is deterministic above the threshold.
> **If the answer is [context-dependent — escalation depends on the vendor's deal size, regulatory exposure, or relationship history not visible in the clause text alone]:** The agent cannot determine escalation-required status from clause text alone. Must incorporate Salesforce deal size, vendor risk category, or other external signals into the routing decision. Adds new data dependencies and makes the routing decision a multi-signal inference problem, not a single-source comparison.
> **Why this matters more than a generic question:** If escalation triggers require context outside the clause text, the current design — which routes based on classification confidence and deviation magnitude — is systematically incomplete. This determines whether the agent can ever produce a reliable escalation-required classification without human review.

---

> **Q11: How often do contracts arrive in a form that is not a standard Word document attached to an Outlook email — PDFs, SharePoint links, contracts uploaded directly into Ironclad, or non-English language documents?**
> **Category:** D
> **What I already infer from the scenario:** WS1 involves inbound vendor contracts. The scenario mentions Microsoft Word + Track Changes and Outlook, implying the standard intake path. Artefact 2.2 describes a vendor demanding Word attachment via email (implying email delivery is current standard). Non-Word or non-email formats are not described.
> **If the answer is [rare — <5% of contracts arrive in non-standard formats]:** The current design (agent halts on non-Word/non-Outlook intake; Tom handles manually) is an acceptable edge case. No separate handling path is needed; the exception handling branch is rarely triggered.
> **If the answer is [common — 10-20% of contracts arrive as PDFs, Ironclad uploads, or via vendor portal links]:** Must design a structured multi-format intake path: PDF OCR + section extraction, Ironclad direct-upload detection, portal polling. This is a significant integration scope expansion that is currently labelled "Human Takes Over." The intake monitoring architecture changes materially.
> **Why this matters more than a generic question:** At 300 contracts/quarter, a 15% non-standard rate is 45 contracts that cannot be processed by the agent's current intake design. If this is the reality, the "Human Takes Over" branch is not an edge case — it is a significant portion of the workload.

---

### Category E: Data and System Reality

> **Q12: Is Ironclad currently used to track all 300 contracts per quarter throughout their lifecycle, or are some contracts tracked in spreadsheets, email threads, or other tools — particularly lower-value or faster-turnaround contracts?**
> **Category:** E
> **What I already infer from the scenario:** Ironclad is a named confirmed system. Whether it is the system of record for 100% of contracts, or aspirationally used while some contracts are managed elsewhere, is not stated.
> **If the answer is [all 300 contracts are in Ironclad throughout their lifecycle]:** The agent's full bidirectional Ironclad integration design is valid from day one. Case record creation, field writes, and routing decision recording all target a single system.
> **If the answer is [partial adoption — some contracts are tracked outside Ironclad, particularly simple standard-path contracts that don't reach WS2/WS3]:** Must add a data normalisation step: identify which contracts are not in Ironclad on intake and provision records before processing. The 65% coverage target assumes Ironclad-resident cases — if standard-path contracts are the ones not in Ironclad, the coverage calculation changes entirely.
> **Why this matters more than a generic question:** A gap between nominal Ironclad adoption and actual usage directly undermines the measurability of every KPI in D4. If the case record system is incomplete, throughput, HITL rate, and turnaround metrics cannot be reliably measured.

---

> **Q13: Do vendor contracts always arrive as Word (.docx) attachments to Outlook emails, or does some meaningful fraction arrive as PDFs, scanned documents, or through a vendor self-service portal?**
> **Category:** E
> **What I already infer from the scenario:** Word + Track Changes is confirmed. Outlook is the named intake channel. Artefact 2.2 confirms one vendor demands Word attachment via email — implying email is standard intake, not that all formats are Word. PDF or scan frequency is unknown.
> **If the answer is [Word exclusively, always as email attachments]:** Parser design is a solved problem (python-docx or equivalent); no OCR layer needed.
> **If the answer is [a significant fraction arrive as PDFs or scanned documents]:** Must include an OCR and PDF extraction layer in the intake pipeline. Clause boundary detection on OCR output has meaningfully lower accuracy than on structured Word text; confidence thresholds may need to be recalibrated downward for PDF-source contracts. Increases false-absence and false-boundary risk.
> **Why this matters more than a generic question:** OCR errors compound into classification errors in a way that Word parsing errors don't. If PDF intake is significant, the accuracy target of ≥90% may require separate calibration per document type — or a lower initial coverage target for non-Word contracts.

---

> **Q14: Does Salesforce currently contain a procurement record for every inbound vendor contract before it reaches Legal's queue, or do some contracts arrive via email directly without a Salesforce-sourced procurement request?**
> **Category:** E
> **What I already infer from the scenario:** Salesforce is confirmed as the system where procurement requests arrive. But whether every vendor contract is pre-registered in Salesforce or whether some bypass the procurement channel and land in Outlook directly is not stated.
> **If the answer is [every contract has a prior Salesforce record]:** Can reliably use the Salesforce procurement ID as the foreign key when creating the Ironclad case record. Salesforce context (vendor name, deal value, procurement category) enriches the intake record.
> **If the answer is [some contracts arrive via direct email without a Salesforce record — e.g., unsolicited vendor proposals, renewal contracts, NDA requests]:** The intake agent must handle missing Salesforce context gracefully: create the Ironclad record with vendor name and filename as the only initial metadata; flag the case as "no Salesforce record — manual enrichment required." Salesforce-linked signals (e.g., deal value for escalation routing) are unavailable for these cases.
> **Why this matters more than a generic question:** If direct-email contracts are common and the agent assumes a Salesforce record always exists, intake processing fails silently for a class of contracts. The failure is invisible until someone notices a missing case in Ironclad.

---

### Category F: Organisational and Trust Context

> **Q15: What level of autonomous classification would you accept in production for the standard path — specifically, are you comfortable with the agent routing ~210 standard-path contracts per quarter to "accept" without Tom reviewing the classification, or would Tom need to spot-check every agent-classified contract for an initial period?**
> **Category:** F
> **What I already infer from the scenario:** CRO pressure to halve turnaround is real. Amelia has enforced sign-off discipline for 12 years. Whether her trust threshold allows fully autonomous standard-path routing or requires a supervised phase is not stated.
> **If the answer is [comfortable with fully autonomous standard path from day one, with notification-only oversight]:** Coverage target of ≥65% is achievable from the initial deployment. KPIs in D4 are valid as stated. Tom's WS1 time on standard contracts drops to intake acknowledgment only.
> **If the answer is [Tom spot-checks every agent classification for the first 6 months before approving any classification for commit]:** Phase 1 coverage target is effectively 0% (all classifications still require Tom's review). The KPI structure must include phase-dependent targets: Phase 1 = 100% HITL with accuracy measurement; Phase 2 = graduated handover above a measured accuracy threshold. The ≤35% HITL target is a Phase 2 target, not a Day 1 target. Deployment plan changes materially.
> **Why this matters more than a generic question:** The coverage and HITL rate KPIs are only meaningful if we know which oversight model Amelia will accept at launch. Building for 65% autonomous coverage and launching with 100% HITL oversight is misaligned at the design level.

---

> **Q16: The DPDI Act playbook update has been discussed since March but not completed. Is there a named owner and a realistic completion date, or is it currently unowned?**
> **Category:** F
> **What I already infer from the scenario:** Amelia has flagged the gap (Artefact 2.3 sticky note). Sarah was involved in discussions in March. The update is not complete. No owner or timeline is recorded.
> **If the answer is [named owner with a committed date within the deployment planning window]:** Can schedule the agent's DPA classification capability to activate on playbook update publication (deployment gate is on a predictable timeline). The mandatory DPA HITL flag (ET-2) is a transitional constraint, not a permanent one.
> **If the answer is [no owner; no committed date]:** The deployment gate for DPA classification is indefinite. Must redesign around this: either (a) deploy with the mandatory DPA HITL flag as a permanent feature until the update is completed (operationally acceptable but limits coverage target for DPA-containing contracts), or (b) delay full agent deployment pending playbook completion (affects the overall timeline). The DPA coverage exclusion must be reflected in the KPIs.
> **Why this matters more than a generic question:** This is a deployment-blocking dependency, not a nice-to-have. The D4 design explicitly states the DPDI update is a non-optional deployment gate. Without a resolution path, the agent either launches with a known compliance gap or cannot process DPA clauses at all. Amelia needs to understand this is on her critical path.

---

> **Q17: When Tom overrides the agent's classification, would you want that override recorded as a training/calibration signal for model improvement, or does creating that kind of correction log create a discoverability or liability concern for Legal?**
> **Category:** F
> **What I already infer from the scenario:** Tom's override decisions are the primary accuracy calibration mechanism in the current design (KPI measurement method in D4). Whether recording override reasoning creates any legal exposure is not considered in the current design.
> **If the answer is [overrides can be logged and used for calibration — no liability concern]:** Implement override logging as a structured field in the Ironclad case record: clause type, agent classification, Tom's override classification, Tom's brief rationale. Use as calibration signal to tune confidence thresholds quarterly. Accuracy improves over time as the calibration dataset grows.
> **If the answer is [override log creates discoverability risk — Legal is cautious about creating a written record of agent errors]:** Cannot use individual override records as calibration signals. Must rely on aggregate accuracy metrics (override rate per clause type per quarter) without preserving individual correction details. Anonymise or aggregate before use. Calibration cycle is slower and less precise. May also affect the admissibility of the audit log if a contract dispute arises.
> **Why this matters more than a generic question:** Legal teams routinely think carefully about creating records of professional mistakes. If the answer is "liability concern," the entire calibration architecture needs to be redesigned around anonymised aggregate metrics — a different engineering approach and a slower accuracy improvement path.

---

## 3. Questions Not Asked — and Why

> **Question not asked:** "How many contracts do you process per quarter?"
> **Why not:** Already stated in the scenario as ~300 per quarter. Asking this wastes a valuable minute of a 60-minute call and signals that we haven't read the brief — eroding Amelia's confidence in the assessment.

---

> **Question not asked:** "Are you concerned about AI making errors in legal documents?"
> **Why not:** No design fork. A "yes" and a "no" both lead to the same design: HITL gates on deviation-flagged cases, mandatory DPA escalation, and confidence thresholds. This is a concern statement dressed as a question. It conveys nothing we can act on.

---

> **Question not asked:** "What are your current turnaround times?"
> **Why not:** Already stated as 4–6 business days with CRO pressure to halve it. Asking this wastes call time and demonstrates we haven't internalised the scenario context Amelia expects us to have read.

---

> **Question not asked:** "What tools does your team use?"
> **Why not:** Ironclad, SharePoint, Salesforce, Outlook, and Word are confirmed in the scenario. A generic tool inventory question would produce a list we already have and would not change any design decision. The design-relevant questions are about the operational maturity of those named systems (Q12, Q13, Q14) — not about what the tools are.

---

> **Question not asked:** "Can you walk us through your entire contract review process from start to finish?"
> **Why not:** A broad SOP walkthrough at the start of a call produces the documented process, not the lived process. By this point in the assessment we have a detailed process model from D0B, D1, and D3. Asking Amelia to re-explain it demonstrates we haven't done our homework. The more valuable probe is to ask about specific deviations from what we already know (Q4, Q7, Q10) — not to re-collect information we already have.

---

## 4. Sequencing for a 60-Minute Discovery Call

| Time slot | Question(s) | Goal for this segment |
|-----------|------------|----------------------|
| 0–5 min | Context setting: explain we've read the brief, know the 300/quarter and 70/20/10 split; this call is about cognitive load and governance mechanics, not process overview | Establish that we're here to probe the decisions, not collect facts we already have; signal competence to earn Amelia's candour |
| 5–15 min | **Q15** (autonomy level Amelia accepts) + **Q5** (common escalation trigger patterns) | Broad funnel: establish where Amelia's trust threshold is, and which clause types she thinks of as highest risk — these two answers constrain everything else |
| 15–30 min | **Q4** (how classification judgment actually works — literal vs. intent) + **Q7** (how sign-off currently happens operationally) | Narrow funnel: the two most architecturally consequential questions; both probe lived vs. documented process in the classification and governance workflows |
| 30–45 min | **Q8** (sign-off authority scope by clause type) + **Q9** (sign-off at contract vs. clause level) + **Q10** (what makes escalation-required in practice) | Lived vs. documented probe: the governance rule is stated; this segment uncovers the operational mechanics that the documentation doesn't capture |
| 45–55 min | **Q16** (DPDI update ownership and timeline) + **Q2** (playbook update process and authority) + **Q13** (document format variety in practice) | Delegation signals: the three answers that most affect the deployment timeline and go-live readiness; surface blockers Amelia needs to act on |
| 55–60 min | Close: summarise the 2–3 design decisions that depend on Amelia's answers; confirm her interpretation of the GC hard rule; outline next steps (D7 specification, deployment gate conversation) | Leave Amelia with a clear picture of what our design depends on and where she needs to make decisions before we can finalise the spec |

---

## Summary — Main 3 Points

1. **The governance mechanics questions (Q7, Q8, Q9) are the most consequential and are currently under-specified.** How the sign-off is recorded (Ironclad vs. email), who can sign off on which clause types, and whether sign-off applies at the contract or clause level together determine the approval token architecture, the ReviewDecision entity design, and whether the GC hard rule can be structurally enforced in the system — or only aspirationally referenced in a prompt.

2. **The classification judgment question (Q4) is the primary source of confidence threshold design risk.** If Tom's classification decisions involve intent judgment rather than textual matching, the agent's semantic similarity approach may systematically diverge from Tom's actual reasoning. This divergence does not show up in any pre-deployment test — it shows up as unexplained override rate in production. Answering Q4 correctly is the difference between a calibrated threshold design and a threshold chosen by assumption.

3. **The DPDI Act update (Q16) is a deployment gate that currently has no owner and no date.** Unless this is resolved before the agent handles any DPA clause, the agent either ships with an unconditional DPA exclusion (limiting coverage and undermining the turnaround target) or ships with a known compliance gap. This is the highest-priority action item to surface in the discovery call — Amelia must leave knowing that the playbook update is on her critical path, not a background backlog item.
