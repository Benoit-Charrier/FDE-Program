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
