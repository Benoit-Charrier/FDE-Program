# D0A — Domain Research: Legal Contract Review
**Produced:** 2026-05-04 | **Domain:** Legal Contract Review | **Status:** Prior (pre-scenario)

---

## 0. Executive Summary

- **Cognitive hotspot:** The highest concentration of skilled human attention in legal contract review falls at the clause-level risk assessment step — where a reviewer must simultaneously apply the organisation's playbook, weigh relationship context, and judge whether a deviation is acceptable or escalation-worthy; this judgment is high-stakes, often tacit, and not fully captured in any written policy.
- **Governance constraint:** Attorney-client privilege and professional responsibility rules (e.g., ABA Model Rules 5.3 and 1.1) require that AI use in legal work remain under competent attorney supervision, creating a hard delegation stop: any output that constitutes legal advice or a final risk determination must have an identifiable human reviewer accountable for it.
- **Agentic opportunity and key unknown:** The highest-leverage opportunity is contract intake, classification, and structured risk flagging — tasks where the agent surfaces issues for human decision rather than making them; the single biggest unknown is whether the organisation operates from a codified contract playbook, because a mature playbook converts clause-level review from judgment work to pattern-matching, dramatically expanding the delegatable surface.

---

## 0b. Table of Contents

1. Domain Overview
   - 1a. What this domain does
   - 1b. Typical workflow
   - 1c. Common failure modes
2. Regulatory and Compliance Context
3. Cognitive Work Patterns
   - 3a. Where skilled attention is typically consumed
   - 3b. Lived vs. documented gaps
4. ATX Dimension Pre-Assessment
5. Hypothesis Questions for Discovery
6. Assumption Log

---

## 1. Domain Overview

### 1a. What This Domain Does

Legal contract review exists to protect an organisation from unfavourable or legally unacceptable obligations before it executes a binding agreement. The primary knowledge workers are in-house counsel, contract managers, paralegals, and (in law firm contexts) associates and partners. Work arrives as contract documents — NDAs, MSAs, SOWs, procurement agreements, employment contracts, licensing agreements — typically via email, CLM (contract lifecycle management) systems, or procurement portals. What leaves the team's queue is either a redlined document (requesting changes), an approval decision (clean to sign), an escalation (to senior counsel or business leadership), or a rejection. In-house legal teams at mid-size organisations typically handle 20–100 contracts per week; large enterprise teams or law firm practices may process hundreds. Many contracts are time-sensitive, with business stakeholders expecting turnaround in 24–72 hours.

### 1b. Typical Workflow

*Domain-typical workflow — client deviations will surface in discovery.*

1. **Contract receipt and intake** — Contract arrives (email, portal, CLM system); reviewer logs it and records metadata (counterparty, type, business owner, value, deadline). `[execution]`
2. **Classification and triage** — Reviewer classifies the contract type and assigns priority based on business urgency, contract value, and risk profile. Determines who should review it and whether a playbook applies. `[judgment]`
3. **Initial risk scan** — Reviewer reads the contract at speed to identify non-standard clauses, missing standard provisions, and red-flag terms (unlimited liability, IP ownership, data processing terms, termination rights). `[judgment]`
4. **Clause-level review and redlining** — Reviewer works through the contract systematically, marking up unacceptable clauses and proposing alternatives from the playbook or drafting new language. `[judgment]`
5. **Internal stakeholder check** — Reviewer consults with the business owner (procurement, sales, HR, finance) to confirm commercial intent and flag where legal risk intersects with business priorities. `[coordination]`
6. **Escalation routing** — If issues exceed the reviewer's delegation authority — high financial exposure, novel legal questions, regulatory sensitivity — the contract is escalated to senior counsel or an approval committee. `[judgment]` / `[coordination]`
7. **Negotiation cycle** — Redlined contract is returned to counterparty; responses received and assessed; further rounds of negotiation may occur. `[coordination]` / `[judgment]`
8. **Final approval and execution** — Once terms are agreed, the contract is routed for signature through the appropriate authority chain. Executed contract is stored in a repository with metadata. `[verification]` / `[execution]`

### 1c. Common Failure Modes

- **Non-standard clause slippage** — A risky clause (e.g., uncapped liability, problematic IP assignment) passes through undetected under time pressure or because the reviewer focused on higher-priority issues. `Judgment failure`
- **Inconsistent playbook application** — Different reviewers apply the same playbook clause differently, creating inconsistent negotiation positions that counterparties exploit. `Process failure`
- **Version and document control errors** — A stale redline version is signed rather than the final agreed version; or tracked changes are accepted in bulk without review. `Data failure`
- **Approval bottleneck** — A contract requiring senior sign-off sits in a queue because the escalation path is unclear or the approver is unavailable, causing the business to miss a deadline. `Coordination failure`
- **Relationship context ignored** — A reviewer applies the standard playbook to a long-standing strategic partner where precedent or side agreements allow for deviation; the counterparty rejects and escalates. `Judgment failure`

---

## 2. Regulatory and Compliance Context

| Framework / Constraint | What it governs | Agent design implication |
|---|---|---|
| **ABA Model Rules 1.1 (Competence) & 5.3 (Supervision of Non-Lawyers)** | Attorneys must maintain competence when using technology; must supervise non-lawyer (including AI) work products | Any agent output that informs or constitutes legal advice must have an identifiable supervising attorney; agent cannot be the final decision-maker on legal risk determinations |
| **GDPR / UK GDPR / CCPA (data protection)** | Contracts involving personal data must contain appropriate data processing terms (DPAs, SCCs); the contract review process itself may handle personal data about counterparties | Agent must be scoped to avoid storing or processing personal data beyond what is necessary; DPA clause review is a candidate for structured agent work if playbook is mature |
| **SOX (Sarbanes-Oxley) — for public companies** | Material contracts must be identified, reviewed, and disclosed; controls over contract approval must be documented and auditable | Agent must produce an audit trail of every review action; escalation decisions must be logged with rationale to support internal audit |
| **HIPAA — for healthcare-adjacent contracts** | Business Associate Agreements (BAAs) required for vendors accessing protected health information; terms are tightly regulated | BAA review is a structured, high-stakes sub-domain; agent can flag missing or non-compliant BAA terms but human must verify adequacy |
| **E-Signature regulations (ESIGN, eIDAS)** | Governing validity of electronic signatures; certain contract types may require wet signatures | Agent should flag contract types where e-signature validity is uncertain (e.g., real estate, some regulated industries) |
| **Attorney-Client Privilege** | Legal advice and legal risk assessments in contracts are privileged communications | Agent-generated risk assessments sent to non-lawyers without attorney review may inadvertently waive privilege; agent must operate within a workflow that preserves the privilege chain |
| **Export Control (ITAR/EAR) — for relevant sectors** | Contracts in defence, aerospace, dual-use technology must comply with export licensing requirements | Agent must flag contracts in regulated sectors for mandatory specialist review; cannot independently assess export control compliance |

---

## 3. Cognitive Work Patterns

### 3a. Where Skilled Attention Is Typically Consumed

> **Cognitive hotspot [CH-1]:** Clause-level risk assessment and redlining
> **Cognitive type:** Pattern recognition + judgment
> **Why it resists simple automation:** The reviewer must simultaneously apply the organisation's standard position (playbook), assess the commercial context of this specific deal, weigh the counterparty relationship, and judge whether a deviation from playbook is commercially acceptable or a hard stop. A clause that is unacceptable in a vendor contract may be acceptable in a strategic partnership. The rule is context-dependent in ways that require tacit knowledge about the organisation's risk appetite and relationship history.
> **What would make it delegatable:** A mature, comprehensive contract playbook that codifies the organisation's position on each clause type, combined with a structured flagging system where the agent identifies clause deviations and the human decides whether to accept, reject, or negotiate. The agent handles detection; the human handles the disposition decision.

> **Cognitive hotspot [CH-2]:** Triage and prioritisation
> **Cognitive type:** Pattern recognition + decision-making
> **Why it resists simple automation:** Priority is set by a combination of business urgency (stakeholder pressure), contract value, risk profile, and operational capacity — factors that are not all present in the document itself. An experienced reviewer incorporates informal signals (who the requestor is, what deal this supports, what else is in the queue) that are not structured data.
> **What would make it delegatable:** If the organisation has structured intake metadata (contract type, counterparty tier, deal value, requested sign date), an agent could score and route contracts by priority with human override. High-quality intake data is the prerequisite.

> **Cognitive hotspot [CH-3]:** Escalation judgment
> **Cognitive type:** Decision-making
> **Why it resists simple automation:** The decision to escalate requires the reviewer to assess whether an issue is within their delegated authority, whether precedent exists, and whether the business stakeholder has accepted the risk elsewhere. These are partially codified (delegation matrices exist) but the hard cases — where a clause is unusual but the deal is strategically important — require judgment that exceeds the delegation matrix.
> **What would make it delegatable:** Explicit, well-maintained delegation thresholds (financial value, clause category, counterparty type) would make most escalation routing rule-bound. An agent could handle ~70% of escalation routing if the matrix is codified; the remainder would surface as "uncertain — human decides."

> **Cognitive hotspot [CH-4]:** Negotiation position setting
> **Cognitive type:** Synthesis + judgment
> **Why it resists simple automation:** Setting a negotiation position requires understanding the counterparty's likely motivation, the organisation's leverage, deal history, and acceptable fallback positions — all of which involve contextual knowledge that is mostly not in structured systems.
> **What would make it delegatable:** Narrow automation is possible for standard positions on standard clause types. A playbook-trained agent can surface "our standard fallback for IP assignment is X; our walk-away position is Y" but the human must decide whether to use it given the context.

### 3b. Lived vs. Documented Gaps

> **Gap [G-1]:** The contract playbook is selectively applied
> **Why it exists:** Experienced reviewers deviate from playbooks based on relationship context, deal priority, and informal knowledge of what counterparties will and will not accept. A long-standing strategic partner's standard terms may be known to be acceptable even if they deviate from the playbook because a side agreement or past precedent governs.
> **Agent design implication:** An agent built purely against the written playbook will flag deviations that experienced reviewers would silently accept. This generates false positives and erodes trust. The agent must either incorporate a known-exceptions registry or route all playbook deviations to human review rather than treating them as hard stops.

> **Gap [G-2]:** Volume spikes produce informal triage shortcuts
> **Why it exists:** When contract volume exceeds reviewer capacity — end of quarter, M&A activity, large procurement cycles — reviewers informally deprioritise certain contract types (e.g., low-value NDAs, renewal agreements with standard terms) rather than processing them with full rigor. This is not documented.
> **Agent design implication:** An agent that applies uniform review rigor to all contracts is solving a different problem than the one humans are actually solving. The design must accommodate tiered review modes (light-touch vs. full review) if it is to match the lived workflow.

> **Gap [G-3]:** Negotiation history lives in email threads and people's memories, not CLM systems
> **Why it exists:** CLM systems record executed agreements, but negotiation context — why a clause was accepted, what was traded off, what the counterparty's red lines are — lives in email threads and reviewers' institutional memory. When a reviewer leaves, this context is lost.
> **Agent design implication:** An agent that needs negotiation context to inform redline decisions will find it largely inaccessible in structured systems. This is both a gap to surface in discovery and a potential high-value capability (agent-assisted negotiation memory) if the organisation is open to capturing this data.

---

## 4. ATX Dimension Pre-Assessment

| ATX Dimension | Domain-typical signal | What to probe in discovery |
|---|---|---|
| **Volume & Time** | Medium to high volume; 20–300+ contracts/week depending on org type; time-per-contract varies widely (15 min for standard NDA; 4–8 hrs for complex MSA); significant time pressure from business stakeholders | Actual weekly volume by contract type; average review time by type; backlog size and SLA adherence; who absorbs overflow |
| **Cognitive Nature** | Mixed: standard form contracts and NDA review is largely rule-bound; complex commercial agreements are judgment-heavy; the same organisation often has both | What percentage of volume is standard vs. complex? Is there a playbook? How mature and complete is it? Where do reviewers most often deviate or escalate? |
| **Data & Systems** | Mixed structured/unstructured: contract documents are unstructured; CLM metadata is structured but often incomplete; negotiation context is largely unstructured (email) | What CLM or intake system is in use? How complete is the metadata? Is there a playbook, and in what format? Where does negotiation history live? |
| **Risk & Compliance** | High stakes and highly regulated: errors create legal liability, financial exposure, regulatory non-compliance; privileged communications constraint shapes AI deployment; audit trail requirements are non-negotiable | What are the consequences of a missed clause? What is the escalation and approval authority structure? Are there regulated sectors (healthcare, defence, financial services) that add additional constraints? Is there an audit trail requirement? |
| **Organisational** | Multi-stakeholder: legal, business units, procurement, finance, external counsel; approval chains vary by contract value and type; handoffs between legal and business are frequent friction points | Who are the stakeholders in the review process? Where do handoffs break down? Who has signature authority at what threshold? Is there a shared service model or federated legal team? |

**Most constraining dimension:** Risk & Compliance is likely the binding constraint on agent design in this domain. Not because the work is uniquely complex, but because the professional responsibility framework creates a hard requirement that no AI output constitutes an unsupervised legal determination. Every agent design must thread through this constraint: the agent can detect, classify, flag, draft, and route — but it cannot be the final accountable voice on legal risk without an identified human attorney in the chain. This constraint does not prevent meaningful automation; it defines the architecture (HITL at the determination point, not at every step).

---

## 5. Hypothesis Questions for Discovery

> **HQ-1: Does the organisation operate from a written contract playbook, and how complete is it?**
> **Hypothesis being tested:** The existence and completeness of a playbook is the primary determinant of how much clause-level review can be converted from judgment work to pattern-matching work. I believe most in-house teams have playbooks but they are incomplete (covering 60–80% of clause types) and inconsistently maintained.
> **If confirmed (incomplete playbook):** Agent scope must be limited to intake, classification, and flagging of known high-risk clause categories; full-clause review requires human. Playbook completion is a pre-condition for expanding agent scope.
> **If disconfirmed (mature, comprehensive playbook):** Agent can be scoped to perform structured clause comparison against the playbook, generating a deviation report for human review — significantly higher delegation potential.

> **HQ-2: What percentage of contracts received are standard form vs. negotiated from scratch?**
> **Hypothesis being tested:** Standard form contracts (NDAs, template MSAs, renewal agreements) represent the high-volume, lower-judgment end of the workload and are the most obvious agentic opportunity. I believe most in-house teams spend disproportionate time on standard form contracts simply because of volume.
> **If confirmed:** Standard form contracts are the right initial agent target — high volume, lower judgment, meaningful time savings.
> **If disconfirmed (most volume is bespoke/negotiated):** The easy automation path is narrower; agent must have more sophisticated clause analysis capability to deliver value.

> **HQ-3: How is review work currently assigned and tracked — through a CLM, email, or informal coordination?**
> **Hypothesis being tested:** Many in-house teams manage contract queues through email and shared drives rather than mature CLM systems. If true, intake and routing are the first friction point — and agent value may begin before the review step.
> **If confirmed (email/informal):** Significant value in intake automation (classification, metadata extraction, routing); but data quality risk is high for agent-assisted review.
> **If disconfirmed (CLM in use):** CLM integration is the agent's primary data source; probe for API access and data completeness.

> **HQ-4: What is the escalation rate — what percentage of contracts require senior counsel or committee review?**
> **Hypothesis being tested:** I believe escalation rates are high in organisations without mature delegation matrices (15–30% of contracts), and that many escalations are driven by ambiguity about authority rather than genuine complexity.
> **If confirmed (high escalation rate, ambiguous criteria):** Escalation routing automation is a high-value target — a well-designed agent routing layer could significantly reduce unnecessary escalations.
> **If disconfirmed (low escalation rate, clear delegation matrix):** Escalation routing is already working; agent value lies elsewhere.

> **HQ-5: Are there specific contract types that reviewers treat as lower-risk and process with less rigor (informal triage)?**
> **Hypothesis being tested:** I believe high-volume, low-value contracts (mutual NDAs, standard vendor renewals) are reviewed with significantly less rigor than the documented process suggests — and that this informal triage is not captured anywhere.
> **If confirmed:** The agent design must accommodate a tiered review model; a single-mode agent applied uniformly will not match the lived workflow and will be rejected as creating more work.
> **If disconfirmed (uniform rigor applied to all contracts):** The organisation may have a compliance or audit driver imposing uniform review; this is a constraint that limits tiering options.

> **HQ-6: Where does negotiation history and counterparty context currently live?**
> **Hypothesis being tested:** I believe this context is largely in email threads and individuals' memories rather than structured systems — representing both a risk (knowledge loss on attrition) and an agent opportunity (if the organisation is willing to invest in capturing it).
> **If confirmed:** Negotiation memory capture is a high-value secondary opportunity; but the agent design for clause review must account for this context gap — it cannot rely on counterparty history it cannot access.
> **If disconfirmed (CLM captures negotiation history):** Agent can incorporate counterparty history into clause-level recommendations, increasing the delegation surface.

> **HQ-7: What is the current SLA for contract turnaround, and how often is it missed?**
> **Hypothesis being tested:** Most in-house legal teams operate under informal or inconsistently enforced SLAs; turnaround pressure is real but not well-measured. If missed SLAs are a business pain point, speed is a more compelling agent value proposition than quality.
> **If confirmed (SLAs missed, business frustrated):** Agent value proposition is latency reduction; prioritise intake and routing automation to reduce queue time.
> **If disconfirmed (SLAs consistently met):** Speed is not the primary pain; probe for quality or consistency issues as the value driver.

> **HQ-8: Is there an audit trail requirement — does every review decision need to be logged with a named reviewer?**
> **Hypothesis being tested:** SOX-compliant and highly regulated organisations have mandatory audit trail requirements; others do not. This constraint shapes whether an agent can take any actions autonomously or must always operate in an advisory/HITL mode.
> **If confirmed (mandatory audit trail with named reviewers):** Agent must operate in an advisory role; every disposition decision must be attributed to a named human. Fully agentic execution is not available for any step.
> **If disconfirmed (no mandatory audit trail):** Greater autonomy is available for low-risk contract types; agent can execute on standard-form, low-value contracts with post-hoc review.

> **HQ-9: Has the organisation previously attempted to automate any part of the contract review process, and what happened?**
> **Hypothesis being tested:** Prior automation attempts (contract analytics tools, AI review platforms) that failed or were abandoned often failed because of playbook immaturity, data quality, or reviewer distrust — not because the task is unautomatable. Understanding prior failures is diagnostic.
> **If confirmed (prior failures):** Probe specifically for the failure mode — playbook gaps, false positive rate, reviewer rejection, or technical issues. The agent design must address the same failure mode.
> **If disconfirmed (no prior automation):** The organisation is starting from scratch; no legacy trust/distrust dynamic to manage, but no baseline data on failure rates either.

> **HQ-10: Who is accountable when a contract with an undetected risky clause is executed?**
> **Hypothesis being tested:** Accountability structures shape risk tolerance for agent delegation. If an individual attorney is personally accountable for every executed contract, they will be reluctant to delegate to an agent. If accountability sits at the team or function level, delegation tolerance is higher.
> **If confirmed (individual attorney accountability):** HITL is non-negotiable at the approval step; agent must be positioned as a productivity tool for the attorney, not a replacement for attorney judgment.
> **If disconfirmed (team/function accountability, approval committee model):** Higher delegation tolerance; agent may be able to handle standard-form contracts end-to-end within defined parameters.

> **HQ-11: What happens when contract volume spikes — who absorbs the overflow and how?**
> **Hypothesis being tested:** Volume spikes (end of quarter, M&A activity) are a known pain point in legal teams. How overflow is handled reveals both the true capacity constraint and what "good enough" looks like under pressure — which is the real delegation target.
> **If confirmed (overflow handled by triage shortcuts or external counsel):** Agent value is in handling the lower-complexity overflow volume, freeing reviewers for complex work.
> **If disconfirmed (team scales well with volume):** Capacity is not the pain point; probe for consistency or quality as the driver.

> **HQ-12: Are there contract types where the organisation almost never negotiates (take-it-or-leave-it)?**
> **Hypothesis being tested:** Many organisations have contracts they sign with minimal review because the counterparty will not negotiate (e.g., SaaS platform agreements, utility contracts, insurance). These are still reviewed for acceptability but negotiation is not the goal. This sub-domain may have different automation characteristics.
> **If confirmed:** Take-it-or-leave-it review is a distinct workflow — agent can assess acceptability against a threshold and recommend sign/reject without generating a redline. High automation potential.
> **If disconfirmed:** All contracts are negotiated; the full redline workflow applies across the board.

---

## 6. Assumption Log

> **Assumption [A-1]:** The organisation processes 20–300 contracts per week.
> **Why it matters:** Volume drives the economic case for agent automation and determines whether throughput or quality is the primary value driver.
> **If wrong:** If volume is very low (<10/week), the ROI case for agentic tooling is weak and the assessment should focus on quality and consistency rather than throughput. If volume is very high (500+/week), the prioritisation logic and triage design become much more important.
> **Confidence:** Medium
> **How to validate:** Ask directly: "How many contracts does your team review per week, and does that vary significantly by time of year?"

> **Assumption [A-2]:** Average review time ranges from 15 minutes (standard NDA) to 4–8 hours (complex MSA or enterprise agreement).
> **Why it matters:** Time-per-contract drives the cognitive load map and determines which contract types offer the most leverage for agent-assisted review. It also calibrates the FTE hours at stake.
> **If wrong:** If all contracts take roughly the same time regardless of type, the type-based triage model is less useful. If complex contracts take much longer (12+ hours), the agent value in complex review may be higher than assumed.
> **Confidence:** Medium
> **How to validate:** Ask: "For a standard NDA vs. a complex vendor MSA, roughly how much time do you spend per contract? Does that include negotiation rounds?"

> **Assumption [A-3]:** The organisation has a contract playbook, but it is incomplete or inconsistently maintained.
> **Why it matters:** Playbook maturity is the primary determinant of how much clause-level review can be delegated to an agent. This assumption drives the initial scoping of the agent (intake and flagging vs. full clause comparison).
> **If wrong:** If no playbook exists, the agent scope is limited to intake, routing, and high-risk-clause flagging using general legal standards. If the playbook is comprehensive and current, the delegation surface is much larger.
> **Confidence:** Medium
> **How to validate:** Ask: "Do you have a contract playbook? When was it last updated? What percentage of the clause types you encounter does it cover?"

> **Assumption [A-4]:** Negotiation history and counterparty context is not reliably captured in structured systems — it lives primarily in email and individual memory.
> **Why it matters:** An agent that needs counterparty history for context will find it inaccessible. This shapes whether negotiation-informed clause review is in scope for the agent.
> **If wrong:** If a mature CLM with negotiation history exists, the agent can incorporate counterparty context into recommendations, expanding the delegation surface.
> **Confidence:** Medium-high (this is common across in-house teams)
> **How to validate:** Ask: "If I wanted to understand how you've handled a specific clause type with a counterparty in the past, where would I find that information?"

> **Assumption [A-5]:** The escalation rate is 15–30% of all contracts, with a significant portion driven by ambiguity about delegation authority rather than genuine legal complexity.
> **Why it matters:** If escalation rates are high and driven by ambiguity, escalation routing is a high-value agent target. If escalation is low and well-managed, the value is elsewhere.
> **If wrong:** If escalation rates are very low (<5%), the organisation has clear delegation authority and the routing problem is already solved. If escalation rates are very high (>40%), it may indicate systemic understaffing or a very conservative risk culture that limits delegation to agents.
> **Confidence:** Low (this varies significantly by organisation)
> **How to validate:** Ask: "Roughly what percentage of contracts require escalation to senior counsel or a committee? What typically drives an escalation?"

> **Assumption [A-6]:** The primary professional responsibility constraint (attorney supervision of AI) applies to this organisation — i.e., licensed attorneys are involved in the review process and their professional obligations govern AI tool use.
> **Why it matters:** If the review function is handled by a non-law-firm in-house team where attorneys are not directly accountable for outputs (e.g., a procurement team doing commercial review without legal sign-off), the professional responsibility constraint may be weaker or absent, changing the delegation architecture.
> **If wrong:** If no licensed attorneys are in the loop, the professional responsibility constraint does not apply in the same way. Different governance constraints (internal policy, commercial risk appetite) would govern instead.
> **Confidence:** Medium (most contract review of this type involves attorneys, but not universally)
> **How to validate:** Ask: "Who is accountable when a contract is executed — is it a licensed attorney who signs off, or a business function?"
