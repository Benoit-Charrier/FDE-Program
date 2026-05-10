# D2 — Delegation Suitability Matrix
**Helix Workforce Software — Vendor Contract Clause Review**
**Produced:** 2026-05-04 | **Status:** Draft — awaiting FDE approval

---

## 0. Executive Summary

- **Delegation architecture:** Of eight task clusters across four work streams, four are agent-led or agent-assisted (intake, clause comparison, redline drafting support, package preparation), two are human-anchored gates that the agent cannot cross (escalation threshold judgment and named-lawyer sign-off), one is Human Only with no agent role (legal analysis and position determination), and one is conditional on a pre-requisite not yet met (standard-deviation redlining depends on playbook format confirmation).
- **Most contested assignment:** C-3 (escalation threshold judgment) is assigned Human-led + Agent Support rather than Agent-led + Human Oversight because the escalation criteria are currently informal and undocumented — an agent given informal criteria will replicate Tom's unsanctioned judgment calls at scale; only once explicit, version-controlled escalation criteria exist does this cluster become a candidate for agent-led execution, and even then the borderline cases require a human confirmation step.
- **Primary governance constraint:** Amelia Forsythe's named-lawyer sign-off rule locks C-7 to Human Only regardless of agent accuracy — this is not a technical limitation but a governance accountability requirement that the architecture must enforce as a hard stop, meaning no agent action can move a counteroffer out of Legal's queue without a recorded human sign-off event in Ironclad.

---

## 0b. Table of Contents

1. Task Cluster Definition
2. Delegation Suitability Matrix
3. Delegation Archetype Assignment with Rationale
4. Delegation Architecture Summary
5. Delegation Boundary Defence
6. Assumption Log

---

## 1. Task Cluster Definition

| Cluster | Work Stream | Description |
|---|---|---|
| **C-1:** Contract intake and metadata logging | WS1 | Receive vendor contract from Outlook, extract counterparty/type/date, log in Ironclad and open for classification |
| **C-2:** Clause content comparison vs. playbook | WS1 | Read each clause in the vendor document, compare to the corresponding playbook position, identify match/deviation/flag and produce a structured deviation report |
| **C-3:** Escalation threshold judgment | WS1 | Given a flagged deviation, determine whether it falls within paralegal redline authority (→WS2) or requires senior-lawyer review (→WS3); currently governed by informal, undocumented criteria |
| **C-4:** Standard-deviation redlining | WS2 | Draft the redline clause language in Word Track Changes, translating the playbook position (and/or substitute language if available) into the vendor's document structure |
| **C-5:** Legal analysis and counteroffer position determination | WS3 | Interpret the legal effect of an unusual clause, assess commercial context, synthesise a counteroffer position and walk-away; the highest-judgment task in the pipeline |
| **C-6:** Agent-assisted redline drafting | WS3 | Generate a starting-point redline from the lawyer's stated position for the lawyer to review, refine, and approve; the agent drafts, the lawyer owns |
| **C-7:** Named-lawyer sign-off | WS4 | Named lawyer reviews the completed counteroffer against the specific clauses being negotiated and approves before it leaves Legal's queue; Amelia's hard rule |
| **C-8:** Counteroffer package preparation and routing | WS4 | Assemble the WS4 review package (structured summary of changed clauses, flagged items for lawyer attention), route to named lawyer's sign-off queue in Ironclad |

---

## 2. Delegation Suitability Matrix

| Task Cluster | Work Stream | Input Structure | Decision Determinism | Tool Coverage | Context Complexity | Exception Rate | Latency Constraint | Risk/Compliance | Suitability Score | Delegation Archetype |
|---|---|---|---|---|---|---|---|---|---|---|
| C-1: Intake and metadata logging | WS1 | M | H | M | L | L | L | L | 5/7 | Agent-led + Human Oversight |
| C-2: Clause comparison vs. playbook | WS1 | M | M | M | L | M | L | M | 2/7 | Agent-led + Human Oversight |
| C-3: Escalation threshold judgment | WS1 | L | L | M | M | H | L | H | 1/7 | Human-led + Agent Support |
| C-4: Standard-deviation redlining | WS2 | M | M | M | L | M | L | M | 2/7 | Agent-led + Human Oversight (Conditional) |
| C-5: Legal analysis and position determination | WS3 | L | L | L | H | H | L | H | 1/7 | Human Only |
| C-6: Agent-assisted redline drafting | WS3 | M | M | M | L | M | L | M | 2/7 | Human-led + Agent Support |
| C-7: Named-lawyer sign-off | WS4 | M | L | M | M | L | L | H | 2/7 | Human Only |
| C-8: Package preparation and routing | WS4 | M | H | M | L | L | L | L | 5/7 | Agent-led + Human Oversight |

**Scoring orientation:** For Input Structure, Decision Determinism, Tool Coverage — H = high suitability for delegation. For Context Complexity, Exception Rate, Latency Constraint, Risk/Compliance — L = high suitability for delegation. Suitability score = count of dimensions at high suitability out of 7.

**Score justification notes:**

*C-1:* Input Structure M — email is semi-structured but the Word attachment is unstructured; better than free-form text but not machine-readable without parsing. Tool Coverage M — Ironclad REST API is confirmed; Outlook integration path is not confirmed in the scenario [Assumption A-1]. Risk L — metadata logging is not compliance-sensitive; errors are correctable downstream. Five dimensions at high suitability makes this the joint-highest-scoring cluster.

*C-2:* Despite the low numeric score, the two suitability barriers (Input Structure M, Decision Determinism M) reflect the challenge for traditional automation tools, not for LLM-based agents — which are specifically designed for natural-language document comparison. The score reflects the framework's conservatism on unstructured input, which is appropriate for scoping but should not be read as "this task is hard for an LLM." Risk M — misclassification propagates to downstream work streams.

*C-3:* Input Structure L and Decision Determinism L are both driven by the same root cause: the escalation threshold criteria are informal and undocumented (Artefact 2.1 evidence). Exception Rate H — approximately 30% of all contracts require at least one escalation judgment, making this a frequent, not exceptional, task. Risk H — under-escalation (routing a WS3 case to WS2) is the primary error mode, with direct compliance and legal accountability consequences.

*C-4:* Suitability score matches C-2. The key uncertainty is playbook format (does it include substitute clause language?) which is not confirmed in the scenario [Assumption A-2]. If substitute language exists, Decision Determinism rises to H and the score becomes 3/7, strengthening the Agent-led case. Current assignment is conditional.

*C-5:* All three "positive" dimensions (Input Structure, Decision Determinism, Tool Coverage) are at L — legal interpretation requires tacit knowledge, deals are unique, and the commercial context sits largely outside any accessible structured system. Context Complexity H and Risk H compound this. 1/7 suitability score is the lowest in the matrix and reflects genuine Human Only territory.

*C-6:* Identical score to C-4 but different archetype. The difference: in C-4, the position is set by the playbook (less human involvement in the input); in C-6, the position is set by a lawyer's judgment (more human involvement, more verification needed). C-6's output must be treated as a first draft requiring professional review, not a recommendation with sampling review.

*C-7:* Exception Rate L and Latency L give a score of 2/7, but the governance constraint (Risk H, Amelia's hard rule) locks this to Human Only independently of the suitability score. Even if all other dimensions improved, the sign-off requirement means this is Human Only by design.

*C-8:* Joint-highest score with C-1 at 5/7. Decision Determinism H — once the redline exists, routing logic and package assembly are rule-bound. Risk L — package preparation errors are catchable at the sign-off review step. Note: the pure routing sub-task (updating Ironclad status and assigning to the sign-off queue) is a CLM workflow automation step, not an agent task; the agent's specific contribution is the structured review package (summary of changed clauses, flagged items for attention).

---

## 3. Delegation Archetype Assignment with Rationale

> **Cluster C-1 — Contract intake and metadata logging**
> **Archetype:** Agent-led + Human Oversight
> **Rationale:** Decision Determinism H (nothing to decide — log what is present) and Risk L (errors correctable) are the primary drivers. Tool Coverage M rather than H (Outlook integration unconfirmed) prevents a Fully Agentic assignment in this assessment; once the integration path is validated, this cluster could move to Fully Agentic.
> **Governance rule impact:** None — this cluster precedes any clause review and carries no compliance consequence.
> **Anti-pattern check:** Could a CLM workflow or RPA handle intake? Partially — structured email-header extraction is RPA territory, but the Word attachment must be parsed to extract contract type and counterparty details, and some contracts arrive with inconsistent email subjects or without metadata in the body. An agent that can read the attachment and the email together is better-suited than RPA for this mixed-format intake.

> **Cluster C-2 — Clause content comparison vs. playbook**
> **Archetype:** Agent-led + Human Oversight
> **Rationale:** Context Complexity L (comparison is mostly stateless; each clause assessed against the playbook independently) and Latency L (batch processing acceptable) support delegation. Input Structure M and Decision Determinism M reflect the natural-language input challenge — manageable for an LLM but not for traditional automation tools. The human oversight component is the reviewer's confirmation of the deviation report before routing decisions are made, not a clause-by-clause review.
> **Governance rule impact:** The stale DPA playbook (Artefact 2.3) creates a systematic compliance risk at this cluster: the agent will classify DPA clauses against the wrong standard until the playbook is updated. This does not change the archetype but adds a hard pre-condition: the DPA section of the playbook must be updated and version-stamped before the agent is deployed on DPA clauses.
> **Anti-pattern check:** Could static rules do this? No — the input is natural language with no structured schema. Could a keyword-search tool flag deviations? Partially for the most formulaic clauses (e.g., exact liability cap figures), but not for paraphrased or structurally equivalent formulations. An LLM with semantic understanding of clause content is required.

> **Cluster C-3 — Escalation threshold judgment**
> **Archetype:** Human-led + Agent Support
> **Rationale:** Decision Determinism L and Exception Rate H are the driving dimensions. The escalation criteria are currently informal (Artefact 2.1 confirms Tom makes calls not explicitly in the playbook). An agent that replicates informal criteria will produce systematic inconsistency at scale; assigning Agent-led at this stage would embed Tom's unsanctioned judgment into an automated system without governance review. The agent's role is to produce the deviation magnitude assessment and a suggested tier with confidence score; the human confirms or overrides the routing.
> **Governance rule impact:** Under-escalation risk (routing a WS3 case to WS2) would result in risky clauses receiving only paralegal-level treatment. Risk H drives the conservative archetype assignment. This cluster directly gates whether WS3 receives the cases it should.
> **Anti-pattern check:** Not a script — the threshold requires reading deviation magnitude and type against an implicit standard. Not fully agentic — the standard itself is not codified. Human-led + Agent Support is the correct answer until explicit escalation criteria are authored, validated, and version-controlled in the playbook.

> **Cluster C-4 — Standard-deviation redlining**
> **Archetype:** Agent-led + Human Oversight (Conditional)
> **Rationale:** Context Complexity L (the position is fully determined by the playbook; no deal context needed) and Latency L support delegation. Decision Determinism M reflects the drafting translation step — if the playbook contains substitute clause language (unknown — Assumption A-2), Decision Determinism rises to H and the archetype strengthens to confidently Agent-led. Without confirmed substitute language, the drafting step retains enough judgment to warrant human oversight of every output.
> **Governance rule impact:** The redline produced here proceeds to WS4 sign-off, which is the hard governance gate. Any drafting error in C-4 will be reviewed at C-7. The sign-off gate provides a backstop, but a systematic drafting error (e.g., incorrect standard substitute language) propagating to all counteroffers is a quality and reputational risk.
> **Anti-pattern check:** Not RPA — translating a position statement to contractual language in a variable-structure document requires natural language generation. Not a static template swap — clause structures and numbering vary by vendor. Agent is appropriate.

> **Cluster C-5 — Legal analysis and counteroffer position determination**
> **Archetype:** Human Only
> **Rationale:** Input Structure L (unusual clause in natural language; legal meaning is ambiguous by definition), Decision Determinism L (legal interpretation is context-specific and contested), Tool Coverage L (commercial context and negotiation history are largely inaccessible in structured systems), Context Complexity H (synthesis of legal risk + deal context + relationship history + institutional knowledge), and Risk H (wrong position creates legal liability or loses the deal) combine for the lowest suitability score in the matrix (1/7). No dimension is at high suitability except Latency L.
> **Governance rule impact:** Not applicable — this cluster is Human Only on capability grounds, not governance grounds. An agent cannot perform this work reliably even if governance permitted it.
> **Anti-pattern check:** Not applicable — this is explicitly not automatable in any form. An agent could supply reference material (relevant playbook sections, prior redlines for this counterparty) but cannot make the interpretive or positional judgment.

> **Cluster C-6 — Agent-assisted redline drafting**
> **Archetype:** Human-led + Agent Support
> **Rationale:** The position is set by a lawyer (C-5 output); the agent's task is to translate that position into a starting-point redline. Context Complexity L (the position is stated; no new context needed for drafting) supports delegation, but Risk M (poorly drafted language can introduce ambiguity) requires that every agent output is reviewed and approved by the lawyer before proceeding. The lawyer is not sampling the output — they are reading and approving every clause. This is support, not delegation.
> **Governance rule impact:** Not directly affected by Amelia's sign-off rule, but the redline produced here proceeds to C-7, where the sign-off gate applies. The agent's drafting quality directly affects the effort required at C-7.
> **Anti-pattern check:** Not a static template — while playbook substitute language (if it exists) could theoretically be copy-pasted, the adaptation to the vendor's specific document structure, clause numbering, and surrounding terms requires judgment. An LLM with the playbook and the vendor document can perform this adaptation; a template engine cannot.

> **Cluster C-7 — Named-lawyer sign-off**
> **Archetype:** Human Only
> **Rationale:** Amelia's hard rule ("no counteroffer may leave Legal's queue without a named lawyer's sign-off on the specific clauses being negotiated") is the overriding constraint, independent of suitability score. This is not a capability limitation — an agent could technically verify that a redline matches a playbook position. It is a governance accountability requirement: a named human must be legally and professionally responsible for every Helix negotiation position sent to a counterparty.
> **Governance rule impact:** This IS the primary governance constraint. C-7 is the architectural enforcement point of Amelia's rule. The design must ensure: (a) no counteroffer can be dispatched without a recorded sign-off event in Ironclad, (b) the sign-off is attributed to a named individual, and (c) the agent cannot trigger dispatch without a confirmed human approval record.
> **Anti-pattern check:** Could a CLM workflow rule implement the routing to the sign-off queue? Yes — the act of moving a completed redline to the named-lawyer approval queue is CLM workflow automation, not an agent task. The sign-off action itself is Human Only.

> **Cluster C-8 — Counteroffer package preparation and routing**
> **Archetype:** Agent-led + Human Oversight
> **Rationale:** Decision Determinism H (once the redline exists, what goes into the review package is rule-bound: changed clauses, playbook reference positions, flagged items) and Risk L (package preparation errors are visible to the reviewing lawyer and correctable before sign-off) support a high delegation level. Tool Coverage M (Ironclad routing confirmed; structured package generation from the redline document requires document parsing capability) prevents Fully Agentic assignment pending integration validation.
> **Governance rule impact:** This cluster feeds directly into C-7 (the sign-off gate). The agent's package preparation is specifically designed to make the human sign-off step faster and more reliable — not to bypass it. The architecture depends on C-8 producing a complete, accurate review package so that C-7's human attention is focused on the substance of the clauses.
> **Anti-pattern check:** The routing sub-task (updating Ironclad status and assigning to queue) is a CLM workflow automation task, not an agent task. The package preparation sub-task (parsing the redline, identifying changed clauses, generating a structured review summary) requires document understanding and is agent territory. These two sub-components should be implemented separately: CLM workflow rule for routing, agent for package generation.

---

## 4. Delegation Architecture Summary

The delegation architecture for this pipeline has three structural layers: an autonomous execution front-end, two human judgment gates, and an execution tail that returns to agent-led processing.

The **autonomous backbone** consists of C-1 (intake), C-2 (clause comparison), and C-8 (package preparation). These three clusters handle the volume-intensive, execution-oriented work at the start and end of the pipeline. Together they can run with agent-led + human oversight: the agent processes all 300 contracts through intake and classification, produces a structured deviation report reviewed by a human at the routing step, and later prepares the sign-off package once a redline is complete. C-4 (standard-deviation redlining) belongs in this group conditionally — it joins the autonomous backbone once playbook substitute language is confirmed and validated. The common characteristic of these clusters is that the agent does the work, and the human reviews the output rather than performing the primary task.

The **two human-anchored gates** are C-3 (escalation threshold judgment) and C-7 (named-lawyer sign-off). These are architecturally non-negotiable and must be treated as hard stops in any system design. C-3 is a judgment gate: Tom's current informal triage becomes a human-confirmed routing decision, with the agent providing a deviation report and a suggested tier but the human confirming the routing before any WS3 case is assigned. C-7 is a governance gate: no counteroffer leaves the queue without a named lawyer's sign-off, recorded in Ironclad, regardless of agent accuracy on the upstream steps. These two gates define the architecture's accountability structure — everything between them can be increasingly delegated; the gates themselves cannot.

C-5 (legal analysis and position determination) is the **Human Only core**: this is where experienced lawyers exercise the tacit knowledge and professional judgment that the rest of the architecture exists to support. The agent does not touch C-5. Its role in WS3 is limited to C-6 (drafting support) — generating a starting-point redline from the lawyer's stated position, reviewed and approved word-by-word before proceeding.

Two components are **not agent work**: the routing sub-task within C-8 (a CLM workflow automation, not an agent task) and C-7's sign-off dispatch mechanism (a governance record, not a capability gap). Building an agent for these components would add engineering complexity without adding value over what a well-configured CLM workflow rule can provide.

**Amelia's named-lawyer sign-off rule** is enforced at C-7, which is designated Human Only in the architecture. The technical implementation requires that Ironclad's dispatch workflow require a confirmed sign-off event (attributed to a named user) before any outbound counteroffer communication is permitted. The agent must not have the capability to trigger outbound dispatch — that action must be triggered only by the named lawyer's sign-off action in the CLM system.

---

## 5. Delegation Boundary Defence

> **Contested assignment: C-3 (Escalation threshold judgment) — assigned Human-led + Agent Support**
> **The counter-argument:** Once explicit escalation criteria are codified (e.g., "liability cap below 60% of playbook floor = WS3; DPA clauses with missing SCCs = WS3"), this decision becomes a rule-based classification that an agent can execute reliably — making Agent-led + Human Oversight the appropriate archetype. Tom's current informal judgment is not inherently superior; it is just tacit. Making it explicit doesn't make it harder, it makes it better. One could argue the conservative archetype assignment is deferring a solvable problem.
> **Why the assigned archetype is correct for this scenario:** The criteria are currently informal and unvalidated — codifying them is a distinct pre-deployment task that has not been done. Assigning Agent-led before that task is complete would have the agent replicating Tom's undocumented judgment at scale, with no governance record of how routing decisions were made. The Human-led + Agent Support assignment is correct for the current state of the scenario. Revision should happen when (a) explicit criteria are authored and reviewed by Amelia, and (b) the agent's routing accuracy on those criteria has been validated against a sample of real cases.
> **What would change the assignment:** Completion of a formal escalation criteria document, reviewed and approved by Amelia Forsythe, version-controlled in the playbook — followed by accuracy validation showing the agent correctly routes ≥95% of historical cases. At that point, Agent-led + Human Oversight with a low-confidence exception path becomes the appropriate archetype.

> **Contested assignment: C-2 (Clause comparison vs. playbook) — assigned Agent-led + Human Oversight**
> **The counter-argument:** With a 2/7 suitability score, this cluster might reasonably be assigned Human-led + Agent Support — the agent provides a deviation report as a reference tool, but the human performs the primary review. This is a more conservative position that acknowledges the unstructured input and the compliance consequence of misclassification.
> **Why the assigned archetype is correct for this scenario:** The 2/7 score reflects traditional automation limitations, not LLM limitations. An LLM reading a legal contract and comparing it to a playbook position is executing its core capability. The human oversight is specifically designed for what the framework requires: the human confirms the deviation report before routing decisions are made. This is structurally Agent-led (the agent does the primary work) with meaningful oversight (human reviews before routing), not Human-led (human does the primary work with agent reference). The key evidence: Tom currently spends ~25 min/case on this task; if the agent produces the deviation report in full and Tom reviews it in ~8 min, the work has been delegated to the agent. If Tom is still reading the full contract and using the agent report as a check, the work has not been delegated.
> **What would change the assignment:** If the agent's clause classification false-negative rate (missed deviations) is found to be above 5% in validation testing, the oversight model should be strengthened to Human-led + Agent Support with Tom performing a full first read on a sampled fraction of contracts. But this is a validation outcome, not a pre-deployment assumption.

---

## 6. Assumption Log

> **Assumption [A-1]:** Outlook-to-Ironclad intake is currently manual (Tom logs each contract from the email) rather than automated via Ironclad's email capture or an existing integration.
> **Why it matters:** If already automated, C-1 is partially solved and the agent scope starts at C-2. If manual, C-1 is the first agent contribution and the design must include Outlook monitoring and Ironclad write access as Day 1 integrations.
> **If wrong:** Agent scope adjusts; the Outlook integration component can be scoped down if existing automation covers intake.
> **Confidence:** Medium — the email-bypass pattern in Artefact 2.2 suggests manual handling is the norm for at least some contracts.

> **Assumption [A-2]:** The contract playbook (SharePoint "Position Statements v3.4") contains position statements per clause type but not standardised substitute clause language ready for insertion into vendor documents.
> **Why it matters:** If substitute language exists, C-4 (standard-deviation redlining) moves from Conditional Agent-led to Confirmed Agent-led, with Decision Determinism rising from M to H. If not, drafting requires the agent to generate language from a position statement, which requires more validation before deployment.
> **If wrong:** If substitute language is confirmed, C-4's archetype assignment strengthens and the scope of the WS2 agent component expands accordingly.
> **Confidence:** Low — playbook format is not described in the scenario beyond "position statements per clause type."

> **Assumption [A-3]:** Amelia's named-lawyer sign-off rule applies to all counteroffers regardless of risk tier or contract type — including low-value, standard-deviation cases from WS2 as well as complex escalated cases from WS3.
> **Why it matters:** If the rule only applies to WS3 escalated cases (and WS2 standard-deviation counteroffers can go out with paralegal sign-off), the WS4 sign-off bottleneck is smaller (~30/quarter) and the governance architecture changes.
> **If wrong:** The sign-off volume drops from ~90/quarter to ~30/quarter, reducing the C-7 bottleneck significantly. The archetype assignment for C-7 remains Human Only but the scale of the constraint changes.
> **Confidence:** Medium — the scenario states "no counteroffer may leave Legal's queue without a named lawyer's sign-off on the specific clauses being negotiated." "Specific clauses being negotiated" could imply WS3-only, but the plain reading applies to any negotiated counteroffer.

> **Assumption [A-4]:** The informal C-3 escalation criteria can be codified into a version-controlled document that covers the primary deviation types (liability cap magnitude, DPA deviation types, IP ownership formulations, SLA gap thresholds) with sufficient specificity to enable reliable agent classification of ≥90% of cases.
> **Why it matters:** If the escalation threshold is genuinely too contextual to codify (every case depends on deal value, counterparty, relationship history in ways that cannot be pre-specified), then C-3 may remain Human-led + Agent Support permanently rather than progressing to Agent-led.
> **If wrong:** C-3 stays Human-led + Agent Support indefinitely, and the agent's contribution to the routing step is advisory only. The architecture remains valid; the agent's autonomous scope does not expand to include routing decisions.
> **Confidence:** Medium — most legal escalation thresholds have a codifiable core (the clear cases) and a judgment residual (the borderline cases). The design can handle the residual through a "low-confidence → human confirms" pathway.
