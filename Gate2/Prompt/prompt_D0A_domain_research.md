# Prompt: Deliverable D0A — Domain Research
**Generic template — not scenario-specific. Run this before reading the scenario in detail.**

---

## Purpose

You are an FDE about to assess a business process in a domain you may not know. Before producing any ATX deliverable, you need a working model of the domain: how work typically flows, where judgment and compliance constraints live, and what agentic opportunities tend to emerge. This is a **budgeted orientation activity (~25 minutes)** — not a research project. Produce enough to listen intelligently during discovery and to avoid bluffing domain knowledge you do not have.

This deliverable feeds:
- **D0D** (discovery synthesis) — grounding the lived-process narrative in domain-typical patterns
- **D1** (cognitive load map) — pre-loading what pause points and judgment calls look like in this domain
- **D6** (discovery questions) — generating hypothesis questions before the stakeholder call
- **All assumption logs** — separating what you know about the domain from what the scenario tells you

Output file: `Deliverables/D0A_domain_research.md`

---

## Your task

You are given a domain and optionally a process area within that domain. Produce a structured domain research document using your training knowledge. Do not read the scenario before completing sections 1–5. You are building a prior, not a post-hoc analysis.

**Input:** `[DOMAIN]` — e.g., "legal contract review," "insurance claims processing," "clinical trial management," "logistics dispatch." Replace with the domain you have been given.

---

## Required structure

### 0. Executive summary
Three bullet points, written first. Each bullet is one sentence. Cover in order:
1. The domain's core workflow pattern and where skilled human attention is most typically consumed (the cognitive hotspot most common in this domain)
2. The most important compliance or governance constraint typical to this domain and how it shapes delegation boundaries
3. The highest-leverage hypothesis for agentic opportunity in this domain, and the single biggest unknown that would confirm or disconfirm it

This section must be self-contained — a reader who has not yet seen the scenario should understand the domain's cognitive shape, its governance constraint, and where the agent opportunity likely sits.

---

### 0b. Table of contents
List all sections by number and title as markdown anchor links, in order. Generate this after the full document is written — section titles must match exactly. Format each entry as `[N. Section title](#n-section-title)` using lowercase, hyphens for spaces, and no special characters in the anchor. Include subsections (e.g., 1a, 1b) indented under their parent.

Example format:
- [0. Executive summary](#0-executive-summary)
- [1. Domain overview](#1-domain-overview)
  - [1a. What this domain does](#1a-what-this-domain-does)

### 1. Domain overview

#### 1a. What this domain does
One paragraph. Describe:
- What the domain's core function is (what problem it exists to solve for the business)
- Who the primary knowledge workers are (roles, not org chart)
- What the primary inputs are (what arrives to trigger work) and what the primary outputs are (what leaves the team's queue)
- Typical volume and cadence (orders of magnitude — daily, weekly, hundreds, thousands)

#### 1b. Typical workflow
A numbered list of 5–8 steps describing how work typically flows in this domain — from trigger to close. For each step, note in brackets whether it is primarily: `[execution]`, `[judgment]`, `[coordination]`, or `[verification]`.

This is a domain-typical description, not this client's specific process. Label it explicitly: *"Domain-typical workflow — client deviations will surface in discovery."*

#### 1c. Common failure modes
List 3–5 things that typically go wrong in this domain. For each, note whether the failure is:
- **Process failure** (a step is missed or done wrong)
- **Data failure** (information is missing, stale, or inconsistent)
- **Judgment failure** (the wrong call is made at a decision point)
- **Coordination failure** (a handoff between people or systems breaks down)

---

### 2. Regulatory and compliance context

List the regulatory frameworks, compliance requirements, and governance constraints that typically apply to this domain. For each:

| Framework / Constraint | What it governs | Agent design implication |
|------------------------|----------------|--------------------------|
| | | |

**At minimum, address:**
- Any data protection or privacy regulation applicable to the data types this domain handles
- Any audit trail or sign-off requirement (who must approve what, and whether that approval must be recorded)
- Any sector-specific regulation that creates hard stops — decisions that cannot be delegated to an AI without human review

If this domain has no significant regulatory constraints, state that explicitly and explain why. Do not invent constraints.

---

### 3. Cognitive work patterns typical to this domain

#### 3a. Where skilled attention is typically consumed
List the 3–4 moments in the typical workflow where skilled human attention is most concentrated. For each:

> **Cognitive hotspot [CH-N]:** [the specific moment in the workflow]
> **Cognitive type:** decision-making / synthesis / pattern recognition / exception handling
> **Why it resists simple automation:** [the specific reason — ambiguity, regulatory sensitivity, exception rate, tacit knowledge]
> **What would make it delegatable:** [the condition under which an agent could handle this — codifiable rules, confidence threshold, human-in-the-loop design]

#### 3b. Lived vs. documented gaps typical to this domain
Describe 2–3 ways in which the real work in this domain commonly diverges from the documented process. These are domain-typical patterns — not claims about this specific client.

Format:
> **Gap [G-N]:** [the divergence — what the SOP says vs. what typically happens]
> **Why it exists:** [the structural reason — system limitation, exception frequency, informal knowledge]
> **Agent design implication:** [how this gap would affect an agent built from the SOP alone]

---

### 4. ATX dimension pre-assessment

For this domain, pre-assess each ATX dimension before seeing the client's specific scenario. This is your prior — you will update it against the scenario and discovery.

| ATX Dimension | Domain-typical signal | What to probe in discovery |
|---------------|----------------------|---------------------------|
| **Volume & Time** | [high / medium / low volume; typical time-per-case] | |
| **Cognitive Nature** | [primarily rule-bound / judgment-heavy / mixed] | |
| **Data & Systems** | [typically structured / unstructured / fragmented across systems] | |
| **Risk & Compliance** | [high stakes / reversible / regulated / audited] | |
| **Organisational** | [typical approval chains, handoffs, stakeholder dependencies] | |

Below the table: one paragraph identifying the ATX dimension you expect to be most constraining for agent design in this domain, and why.

---

### 5. Hypothesis questions for discovery

Generate at least 10 hypothesis questions to bring into the discovery call. These are questions whose answers would confirm or disconfirm your domain model — not generic discovery questions.

For each question, state the hypothesis it is testing:

> **HQ-[N]: [the question — concrete, not generic]**
> **Hypothesis being tested:** [what you currently believe about this domain that this question would confirm or challenge]
> **If confirmed:** [what it means for the agent design]
> **If disconfirmed:** [what changes]

Draw from all three pre-call preparation techniques from `references/discovery-questioning-patterns.md`:
- Domain standards and typical processes
- Compliance and regulatory frameworks
- ATX dimension mapping (Volume, Cognitive Nature, Data, Risk, Organisational)

---

### 6. Assumption log

Every claim you have made in sections 1–5 that is not universally true of all organisations in this domain must be logged here.

> **Assumption [A-N]:** [what you are taking as a domain-typical baseline]
> **Why it matters:** [which deliverable or design decision it affects]
> **If wrong:** [how the prior would need to be revised]
> **Confidence:** low / medium / high
> **How to validate:** [what question to ask or what artefact to request in discovery]

Minimum 4 assumptions. Every numeric estimate (volume, time-per-case, exception rate) must have an entry here.

---

## Time constraint

This deliverable should take ~25 minutes. If you find yourself researching beyond that, you are over-investing. The goal is a working model sufficient to listen intelligently in discovery — not a complete domain reference. Gaps are expected and will be filled by the scenario and stakeholder call. Name them in section 6 rather than papering over them.

---

## Acceptance criteria (all must pass)

- [ ] Sections 1–5 completed before the scenario is used as input (this is a prior, not a post-hoc analysis)
- [ ] Domain overview describes the cognitive shape of the work, not just the org chart
- [ ] Regulatory section addresses at minimum: data protection, audit trail requirements, and any hard delegation stops
- [ ] At least 3 cognitive hotspots with a "what would make it delegatable" signal for each
- [ ] At least 2 lived-vs-documented gaps with agent design implications
- [ ] ATX pre-assessment identifies the most constraining dimension with reasoning
- [ ] At least 10 hypothesis questions, each with a testable hypothesis and design fork
- [ ] At least 4 assumptions logged, including all numeric estimates
- [ ] Total length: 2–3 pages — this is orientation, not a report

## Fail signals — do not produce output that contains these

- Domain overview that describes the org chart without describing the cognitive work
- Regulatory section that lists frameworks without stating the agent design implication of each
- Cognitive hotspots described as "this is complex" without naming what makes it non-trivially delegatable
- Hypothesis questions with no hypothesis — questions that would generate interesting answers but not change the design
- Assumption log entries for universally true statements (e.g., "we assume humans are involved in this process")
- A document longer than 3 pages — if it is longer, it is a research report, not an orientation prior
