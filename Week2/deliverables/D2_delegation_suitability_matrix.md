# D2 — Delegation Suitability Matrix
**Scenario:** Helix Workforce Software — Vendor Contract Clause Review

---

## 1. Task Cluster Definition

Eight clusters are defined across all four work streams, derived from the JtDs and micro-task groups in D1. WS3 and WS4 clusters are inferred from the scenario's per-work-stream descriptions; internal micro-task structure is labelled as assumption where not stated.

| Cluster | Work stream | Description |
|---------|-------------|-------------|
| C-1: Document intake & clause location | WS1 | Receive inbound contract via Outlook, log in Ironclad, locate each of the 7 clause types within the unstructured document |
| C-2: Clause extraction & playbook comparison | WS1 | Extract clause text per type and compare semantically against the SharePoint playbook position statements |
| C-3: Deviation triage & routing judgment | WS1 | Classify each deviation as standard / negotiable / escalation-required and produce a contract-level routing decision |
| C-4: Redline drafting | WS2 | Retrieve the playbook position for each flagged clause and draft tracked-changes replacement language in the vendor's Word document |
| C-5: Cross-clause consistency review | WS2 | Check the redlined document for semantic interactions between the modified clause and the rest of the contract |
| C-6: Escalated clause review & position framing | WS3 | Senior lawyer reviews clauses outside playbook coverage, frames the counteroffer position, and drafts the redline [task structure assumed from 90 min/case and senior-lawyer involvement] |
| C-7: Counteroffer package preparation | WS4 | Compile the sign-off package (specific redlined clauses, playbook annotations, deviation magnitude) and draft the procurement response communication |
| C-8: Named-lawyer sign-off on specific clauses | WS4 | Named lawyer reviews and approves each redlined clause before the counteroffer is dispatched — the GC hard rule enforcement point |

---

## 2. Delegation Suitability Matrix

**Scoring note:** Input structure, decision determinism, tool coverage rated H = high suitability (favourable). Context complexity, exception rate, latency constraint, risk/compliance rated L = high suitability (favourable). Score = count of favourable conditions out of 7.

| Task Cluster | WS | Input Structure | Decision Determinism | Tool Coverage | Context Complexity | Exception Rate | Latency Constraint | Risk/Compliance | Suitability Score | Delegation Archetype |
|---|---|---|---|---|---|---|---|---|---|---|
| C-1: Document intake & clause location | WS1 | M | M | H | L | M | L | M | 3/7 | Agent-led + Human Oversight |
| C-2: Clause extraction & playbook comparison | WS1 | L | M | H | M | M | L | H | 2/7 | Agent-led + Human Oversight |
| C-3: Deviation triage & routing judgment | WS1 | M | L | M | H | H | L | H | 1/7 | Human-led + Agent Support |
| C-4: Redline drafting | WS2 | L | L | M | H | M | L | H | 1/7 | Human-led + Agent Support |
| C-5: Cross-clause consistency review | WS2 | L | L | M | H | M | L | H | 1/7 | Human-led + Agent Support |
| C-6: Escalated clause review & position framing | WS3 | L | L | M | H | H | L | H | 1/7 | Human Only |
| C-7: Counteroffer package preparation | WS4 | H | M | H | M | L | L | M | 4/7 | Agent-led + Human Oversight |
| C-8: Named-lawyer sign-off on specific clauses | WS4 | H | L | M | H | L | L | H | 2/7 | Human Only |

**Scoring notes per cluster:**

- **C-1 (3/7):** Tool coverage is High — Outlook, SharePoint, and Ironclad all have APIs; Word parsing libraries exist. Context complexity is Low — the task is bounded by 7 known clause types requiring no institutional knowledge. Latency is Low — async processing is acceptable. Input structure and decision determinism score Medium because clause *location* in unstructured prose is probabilistic, not deterministic. Risk scores Medium because intake errors are correctable, but missed clause locations propagate downstream.
- **C-2 (2/7):** Tool coverage is High — SharePoint playbook is API-accessible; LLM-based semantic comparison is buildable. Latency is Low — batch processing acceptable for contract review. Input structure is Low because clause text is unstructured legal prose. Decision determinism is Medium (numeric thresholds are deterministic; qualitative comparisons are not). Risk is High — misclassification at this stage is the direct cause of incorrect downstream routing and potential compliance failure.
- **C-3 (1/7):** Only latency is favourable. Decision determinism is Low — the boundary between the 20% negotiable and 10% escalation buckets is tacitly held by Tom, not codified in the playbook. Context complexity is High — requires institutional knowledge of Helix's negotiating posture and regulatory currency. Exception rate is High — borderline cases are this cluster's defining work. Risk is High — routing an escalation-required contract to WS2 is the single most consequential misclassification in the process.
- **C-4 (1/7):** Only latency is favourable. Input structure is Low — drafting requires generating unstructured legal prose from semi-structured policy positions. Decision determinism is Low — multiple valid clause formulations exist; judgment required on which best serves Helix's interest in context. Context complexity is High — legal drafting convention, contract grammar, and current regulatory position all participate. Risk is High — an incorrect redline sends a non-compliant legal position in the outbound counteroffer.
- **C-5 (1/7):** Same profile as C-4 but with Tool coverage additionally penalised — no current tool supports semantic cross-clause dependency analysis. The only favourable dimension is Latency. Input structure is Low (full unstructured contract document). Decision determinism is Low (conflict versus stylistic inconsistency = legal judgment). Risk is High — undetected cross-clause conflicts create legal ambiguity.
- **C-6 (1/7):** All dimensions are at low suitability except latency. Input structure is Low — unusual clauses are unusual precisely because they do not fit known patterns. Decision determinism is Low — senior lawyer is exercising judgment on novel clause types with no playbook coverage. Context complexity is High — requires full commercial law expertise, understanding of Helix's business relationships, and current regulatory awareness. Exception rate is High — this cluster is entirely composed of exceptions. Risk is High — errors here propagate directly into negotiation positions on the most sensitive clauses.
- **C-7 (4/7):** Highest suitability score. Input structure is High — by the time WS4 is reached, the redlined clauses and vendor contact data are structured records in Ironclad. Tool coverage is High — Ironclad REST APIs, Outlook, and Word APIs are all available. Exception rate is Low — once redlines are approved, package assembly is routine. Latency is Low. Decision determinism and context complexity score Medium due to some judgment on communication framing and vendor relationship context.
- **C-8 (2/7):** Input structure is High (structured sign-off package); exception rate and latency are Low. However, decision determinism is Low — sign-off is a legal judgment act, not a rules-check. Context complexity is High — requires the named lawyer's full expertise. Risk is High — this is the GC's non-negotiable compliance gate; the cost of bypassing it is not a recoverable error.

---

## 3. Delegation Archetype Assignment with Rationale

> **Cluster C-1 — Document Intake & Clause Location**
> **Archetype:** Agent-led + Human Oversight
> **Rationale:** Tool coverage (H) and context complexity (L) together make this the most immediately automatable cluster in WS1. The intake and logging steps are deterministic; the clause location step is probabilistic but tractable for an LLM operating on 7 known clause types. Human oversight is warranted specifically because a missed clause location (a false negative) creates an unreviewed clause downstream — a low-frequency but high-consequence failure mode. Oversight trigger: agent confidence below threshold for any clause type, or fewer than 7 clause types identified.
> **GC rule impact:** Not applicable. This cluster has no counteroffer dependency.
> **Anti-pattern check:** The intake/logging sub-task (MT1) *is* solvable by RPA — structured file receipt, renaming, SharePoint upload, Ironclad case creation. The clause location sub-task (MT2) is not — it requires semantic understanding of document structure, not string matching. Warranted to build as agent rather than RPA precisely because of MT2.

> **Cluster C-2 — Clause Extraction & Playbook Comparison**
> **Archetype:** Agent-led + Human Oversight
> **Rationale:** Tool coverage (H) enables the agent to access both the contract text and the SharePoint playbook; batch latency (L) removes real-time pressure. The agent can handle numeric threshold comparisons autonomously — Artefact 2.1 shows this is a lookup-and-compare task for liability caps. The unstructured input (L) and high compliance risk (H) require a confidence-gated design where the agent only produces autonomous outputs for cases where its comparison confidence exceeds a defined threshold. Cases below threshold, and all qualitative comparisons (DPA terms, indemnity scope), are flagged for Tom's review rather than resolved by the agent.
> **GC rule impact:** Not applicable at this stage. The GC rule gates the downstream counteroffer, not the classification.
> **Anti-pattern check:** Not solvable by static rules or RPA — the semantic comparison of unstructured legal prose against semi-structured policy requires reasoning over language, not pattern matching. An LLM agent is the correct tool.

> **Cluster C-3 — Deviation Triage & Routing Judgment**
> **Archetype:** Human-led + Agent Support
> **Rationale:** Decision determinism (L) and context complexity (H) are the two blocking dimensions. The 20%/10% boundary is tacit institutional knowledge held by Tom — it is not codified in the playbook. An agent cannot safely make this routing decision because the threshold between "negotiable" and "escalation-required" has no documented rule. Exception rate (H) compounds this: the uncertain cases are concentrated precisely at this boundary. The agent's role is to provide structured comparison outputs and a confidence score; Tom makes the routing call on all deviation cases. This archetype becomes upgradeable to Agent-led + Human Oversight if and when the playbook is updated with explicit, per-clause-type deviation thresholds.
> **GC rule impact:** Indirectly — correct triage is a precondition for the sign-off gate to operate correctly. If C-3 routes an escalation-required contract to WS2, it bypasses the senior-lawyer review that would otherwise precede sign-off. Correct triage protects the integrity of C-8.
> **Anti-pattern check:** Not solvable by static rules — the threshold requires judgment. Not solvable by RPA — RPA requires deterministic rules. An agent providing comparison context to a human triage decision is the appropriate design.

> **Cluster C-4 — Redline Drafting**
> **Archetype:** Human-led + Agent Support
> **Rationale:** Decision determinism (L) and context complexity (H) block full delegation. The playbook provides policy positions (e.g., "12 months / £250,000"), not ready-to-paste clause language — Tom must generate substitute text that fits the vendor's contract grammar. For numeric-threshold clause types (liability cap, SLA commitments), an agent can generate a candidate redline for Tom to review and accept. For qualitative clause types (DPA terms, IP ownership, indemnity scope), the agent's role is limited to surfacing the playbook position and relevant prior redline examples [assumption: prior examples may or may not exist] — Tom drafts the language. Risk (H) makes human review of every agent-generated redline mandatory before any clause proceeds to sign-off.
> **GC rule impact:** All agent-generated redlines feed into C-8 (sign-off). The GC rule does not change the archetype here but confirms that human review at C-4 is a prerequisite for the C-8 gate to be meaningful.
> **Anti-pattern check:** Not solvable by a script or template — the variety of vendor contract structures means no static template reliably produces grammatically consistent redlined language. LLM-based generation with human review is warranted.

> **Cluster C-5 — Cross-Clause Consistency Review**
> **Archetype:** Human-led + Agent Support
> **Rationale:** Tool coverage (M) — no current tool supports semantic cross-clause analysis, but an LLM agent can read the full document and flag potential interactions. The critical constraint is decision determinism (L): whether a cross-clause interaction constitutes a genuine legal conflict or a cosmetic inconsistency requires legal expertise. The agent's contribution is surface-area reduction — it identifies candidate interaction pairs for Tom to review rather than requiring Tom to read the entire 15–40 page document. Context complexity (H) and risk (H) confirm that the agent flags, the human decides.
> **GC rule impact:** Not directly applicable. Cross-clause consistency errors are a quality risk that should be caught before the sign-off package is prepared, but the GC rule does not specifically address this step.
> **Anti-pattern check:** Not solvable by RPA or static rules — it requires reading unstructured contract prose for semantic dependencies. Agent-assisted analysis is the minimum viable approach.

> **Cluster C-6 — Escalated Clause Review & Position Framing**
> **Archetype:** Human Only
> **Rationale:** Five of the seven suitability dimensions are at low suitability. Decision determinism (L) is disqualifying on its own — the senior lawyer is exercising legal judgment on clause types the playbook explicitly does not cover. Context complexity (H) is equally disqualifying — the position framing requires full awareness of Helix's current business relationships, risk appetite, and regulatory posture, none of which is capturable in a structured system. Exception rate (H) means every case in this cluster is definitionally an edge case. This is not work where an agent reduces effort; it is work that defines why a senior lawyer is employed.
> **GC rule impact:** Not directly applicable — the GC rule governs the downstream sign-off. But Amelia's rule exists precisely because of the kind of legal judgment this cluster represents; relaxing the sign-off rule would be especially dangerous for clauses that went through this cluster.
> **Anti-pattern check:** Definitively not solvable by script, RPA, or agent. This cluster is the reference case for Human Only.

> **Cluster C-7 — Counteroffer Package Preparation**
> **Archetype:** Agent-led + Human Oversight
> **Rationale:** This is the highest-suitability cluster in the matrix (4/7). Input structure (H) is the key enabler — by WS4, the redlined clauses, playbook positions applied, deviation magnitudes, and vendor contact data are all structured records in Ironclad, available via REST API. Tool coverage (H) confirms all required systems are API-accessible. Exception rate (L) reflects that package assembly is routine once redlines are approved. Human oversight is required because the package is the direct input to C-8 — any error in package preparation (wrong clause version, missing annotation) would cause the named lawyer to approve incorrect content. Oversight trigger: agent flags any mismatch between the redlined clause version in the package and the Ironclad case record.
> **GC rule impact:** Package preparation is the precondition for the C-8 sign-off gate. The agent prepares the package; the lawyer approves it. The GC rule is satisfied by C-8, not C-7 — but C-7 must be correct for C-8 to be meaningful.
> **Anti-pattern check:** Package assembly from structured records could in principle be handled by a script. The agent adds value specifically through: (1) drafting the human-readable procurement response communication contextualised to the specific vendor relationship, and (2) flagging vendor delivery preference exceptions (Artefact 2.2 pattern). These require reasoning, not rules. Warranted.

> **Cluster C-8 — Named-Lawyer Sign-off on Specific Clauses**
> **Archetype:** Human Only
> **Rationale:** Decision determinism (L) and risk (H) are both disqualifying. Sign-off is a legal judgment act — the named lawyer is verifying that the redlined clause achieves Helix's intended negotiating position, not just that it matches a template. Context complexity (H) reflects that this judgment draws on the full expertise of a named individual. This is not an oversight step that could theoretically be reduced — it is the accountability mechanism that makes the GC's rule enforceable. The agent's role is limited to preparing the package and routing it efficiently; it cannot participate in the approval act itself.
> **GC rule impact:** This cluster *is* the GC rule. It exists in Human Only precisely because Amelia's non-negotiable requirement is that a named lawyer's identity is attached to the specific clauses being approved. No agent action can substitute for or record this accountability in a legally meaningful way.
> **Anti-pattern check:** Not applicable — Human Only means the question of automation does not arise. The dispatch sub-task (sending the signed-off document) is Fully Agentic once the sign-off is recorded in Ironclad, but dispatch is subordinate to sign-off, not a substitute for it.

---

## 4. Delegation Architecture Summary

The overall delegation architecture for Helix's vendor contract review process has a clear three-layer structure: an **autonomous processing backbone** in WS1 and WS4, a **human-anchored judgment layer** in WS1's triage zone and WS2's drafting zone, and two **non-negotiable human gates** in WS3 and WS4.

The autonomous backbone consists of C-1, C-2, and C-7. These three clusters together process every one of the 300 contracts per quarter — receiving them, extracting and comparing clause text, and assembling the sign-off packages. C-1 and C-2 are the highest-volume work in the process (all 300 contracts pass through both) and the tasks where an LLM agent creates the most throughput value. C-7 sits at the other end of the pipeline, preparing the structured packages that make the sign-off gate efficient. All three operate under human oversight — a confidence threshold gate in C-2, a package integrity check in C-7 — but the default path is agent-executed, with human intervention triggered by specific conditions rather than by default.

The human-anchored judgment layer consists of C-3, C-4, and C-5. These are the three clusters where the agent supports but does not lead. C-3 (triage) is the most critical of these: it is the routing decision that determines which work stream a contract proceeds to, and therefore the integrity of the entire pipeline depends on it being correct. The agent provides Tom with structured comparison outputs and confidence scores; Tom makes the triage call. C-4 (redline drafting) uses the agent as a generation tool for numeric-threshold clauses, with Tom reviewing and adapting the output — and drafting directly for qualitative clauses. C-5 (cross-clause review) uses the agent to flag candidate interaction pairs, reducing Tom's reading surface without replacing his legal judgment. This layer is deliberately kept human-led because the playbook is not yet in a state that would support higher delegation — the DPDI Act gap, the undocumented triage thresholds, and the absence of a clause-drafting template library all need to be resolved before any of these clusters can move up the autonomy scale.

The non-negotiable human gates are C-6 and C-8. C-6 (escalated clause review) is where the 10% of contracts that fall outside playbook coverage go for senior-lawyer judgment; no agent involvement is appropriate here, and the architecture does not attempt it. C-8 (named-lawyer sign-off) is where the GC's hard rule is enforced: no counteroffer leaves the queue without a named lawyer's identity attached to the specific clauses being approved. The agent can route the package, annotate it, and execute dispatch once the sign-off is recorded — but the sign-off act itself is non-negotiable Human Only. This gate applies to all contracts that reach WS4, including those that passed through the agent-led portions of WS1 and WS2.

The architecture is designed to compound. C-1 and C-2's shared playbook retrieval layer can be extended to serve WS2's redline drafting agent without rebuilding the retrieval infrastructure. C-7's structured sign-off package feeds directly into C-8 in a form the lawyer can review efficiently — reducing the 30 min/case WS4 time rather than eliminating it. The system is designed so that improvements to the playbook (DPDI Act updates, codified triage thresholds, numeric redline templates) automatically increase the delegation ceiling at C-3 and C-4 without requiring architectural changes.

---

## 5. Delegation Boundary Defence

> **Contested assignment:** C-2 — Clause Extraction & Playbook Comparison — assigned Agent-led + Human Oversight
> **The counter-argument:** The suitability score is 2/7 — lower than the 3/7 of C-1, which shares the same archetype. The unstructured input and high compliance risk together suggest Human-led + Agent Support would be safer: the agent produces extraction outputs for Tom to review, rather than acting autonomously by default.
> **Why the assigned archetype is correct for this scenario:** The volume argument is decisive — 300 contracts per quarter means approximately 23 per week, and each involves extracting 7 clause types and comparing each against the playbook. If Tom must review every agent extraction before it proceeds, the throughput gain collapses. The confidence-gated design provides the safety: the agent acts autonomously only where its extraction confidence exceeds a threshold, and flags all low-confidence extractions and all qualitative comparisons for Tom's review. The numeric comparisons (liability caps, SLA commitments) are deterministic once extraction is correct — these represent the majority of deviations encountered. Human-led would correctly handle the DPDI-gap edge cases but would waste Tom's time on the 70% of contracts where the agent's comparison is reliable.
> **What would change the assignment:** If the false-positive rate on numeric comparisons in testing exceeded 5% [assumption: acceptable error rate], or if Amelia required human review of all agent outputs regardless of confidence — either condition would push the archetype to Human-led + Agent Support.

> **Contested assignment:** C-3 — Deviation Triage & Routing Judgment — assigned Human-led + Agent Support
> **The counter-argument:** Once the playbook is updated with explicit, per-clause-type deviation thresholds, the triage decision for numeric-threshold clauses becomes deterministic. A reasonable designer might argue that C-3 should be pre-assigned Agent-led + Human Oversight in anticipation of that update, with the human oversight gate covering the residual qualitative cases.
> **Why the assigned archetype is correct for this scenario:** The assignment must reflect the scenario as it exists now, not after a hypothetical playbook update. The playbook is currently 9 months stale. The DPDI Act gap means Tom cannot even reliably triage DPA clauses, let alone an agent. The "will ask Sarah" informal path — an untracked third routing channel — exists precisely because the triage rules are insufficient. Assigning Agent-led + Human Oversight today would build an agent that mimics Tom's tacit knowledge rather than replacing it with codified rules. That is a fragile design that would require retraining every time the implicit threshold shifts. The correct sequence is: update playbook → codify thresholds → pilot Agent-led + Human Oversight for numeric-threshold cases → extend to qualitative cases if quality holds.
> **What would change the assignment:** Playbook updated with explicit deviation thresholds per clause type for at least 5 of the 7 clause types, validated against at least one quarter of historical routing decisions. That is the minimum evidence base for upgrading this archetype.

---

## Summary — main 3 points

1. **The autonomous backbone is C-1, C-2, and C-7 — these three clusters cover all 300 contracts and represent the primary throughput opportunity.** Both C-1 and C-2 score Agent-led + Human Oversight on the strength of tool availability and batch latency, despite unstructured inputs; confidence gating manages the compliance risk without defaulting to human review of every case.

2. **The GC's hard rule creates a non-negotiable Human Only gate at C-8 that the architecture is designed around, not against.** The agent's highest value in WS4 is preparing the sign-off package efficiently (C-7), which reduces the lawyer's approval time rather than attempting to replace the approval act. The sign-off gate is the accountability mechanism — making it faster is the design goal, not removing it.

3. **The playbook is the binding constraint on the delegation ceiling across three clusters (C-3, C-4, and the DPA exception in C-2).** Before the DPDI Act updates are incorporated and explicit triage thresholds are codified, C-3 cannot safely move from Human-led to Agent-led, and C-4 cannot generate DPA redlines without human drafting. The agent architecture is ready to compound as the playbook matures; the playbook is not yet ready for the agent architecture.
