# Prompt: Deliverable 6 — Discovery Questions for the Main Stakeholder

## Scenario (read this first)
See `scenario\scenario_context.md` for the full scenario, work streams, tooling, and named-systems guidance. Do not invent numbers, systems, or constraints not present in the scenario. Every number you use must trace back to the scenario or be explicitly labelled as an assumption.
---

## Your task
Produce a set of discovery questions for the main stakeholder identified in scenario_context.md. Be concise. Summarize the main 3 points at the end. Output file: `deliverables\D6_discovery_questions.md`.

These must be questions whose answers would **actually change your agent design** — not generic discovery questions, not questions whose answers you can already infer from the scenario, and not questions that demonstrate you haven't thought through the design yet.

Before writing a question, ask yourself: "If the answer is X, what changes in my design? If the answer is Y, what changes?" If both answers lead to the same design, the question is not useful.

Reference: `references\discovery-questioning-patterns.md`.

---

## Required structure

### 1. Stakeholder context
One paragraph. The main stakeholder is identified in scenario_context.md — read their role, tenure, and the team they oversee from there. What does this stakeholder care about most in the context of this process? What is their primary concern about AI involvement (grounded in the hard constraints and compliance gaps stated in the scenario, not in generic AI risk)? What would make them trust or distrust an agent? Draw on what the scenario states: any unresolved compliance issues, any non-negotiable governance rules, any stated business pressure.

This paragraph informs the framing and sequencing of your questions — do not skip it.

### 2. Questions whose answers would change the design

Produce at least 15 questions grouped into the following categories. For each question, include the "design fork" — what different answer X versus answer Y would change in your agent design.

Use this format for every question:

> **Q[N]: [the question — concrete, specific, not leading]**
> **Category:** [category name]
> **What I already infer from the scenario:** [what you can already deduce — so you're not asking about it]
> **If the answer is [X]:** [what changes in the design]
> **If the answer is [Y]:** [what changes in the design]
> **Why this matters more than a generic question:** [1 sentence]

**Required categories (at least 2 questions per category):**

#### Category A: Policy/knowledge base structure and machine-readability
The scenario references a policy or knowledge document (see scenario_context.md) but may not describe its format, versioning, or authority. Questions here would change how you design the agent's knowledge base and retrieval system.

#### Category B: The routing/classification logic — how it actually works today
The scenario gives you the routing split (from scenario_context.md) but may not describe how reviewers actually reach those classifications in practice. Questions here would change the agent's decision logic and confidence threshold design.

#### Category C: The governance/approval rule — exactly how it works operationally
The scenario's primary governance or approval constraint (from scenario_context.md) is stated but may be operationally vague. Questions here would change the autonomy matrix and the approval workflow design.

#### Category D: Exception patterns and edge cases
The scenario implies ~10% escalation but doesn't describe what makes a clause escalation-worthy versus merely negotiable. Questions here would change the agent's escalation trigger design.

#### Category E: Data and system reality
The scenario names specific systems (see scenario_context.md) but not the operational reality — API maturity, integration constraints, data quality, access model. Questions here would change your gap analysis and integration architecture.

#### Category F: Organisational and trust context
The scenario may state the stakeholder's comfort level with automation alongside non-negotiable governance constraints and unresolved compliance gaps (see scenario_context.md). Questions here would change the HITL rate, rollout approach, oversight design, and how you sequence automation against compliance risk.

### 3. Questions you are NOT asking — and why
List 5 questions that a less disciplined analyst might ask, and explain why you are not asking them:

> **Question not asked:** [the generic or low-value question]
> **Why not:** [either it's already answered by the scenario, or it's not decision-relevant, or it's too early to ask, or it would waste the GC's time]

This section demonstrates that your question list is curated, not exhaustive.

### 4. Sequencing for a 60-minute discovery call
Using the 60-minute call structure from `references\discovery-questioning-patterns.md`, sequence your top 10 questions into a call plan:

| Time slot | Question(s) | Goal for this segment |
|-----------|------------|----------------------|
| 0–5 min | Context setting | |
| 5–15 min | Broad funnel | |
| 15–30 min | Narrow funnel (lived process) | |
| 30–45 min | Lived vs. documented probe | |
| 45–55 min | Delegation signals | |
| 55–60 min | Close | |

---

## Acceptance criteria (all must pass)

- [ ] At least 15 questions total
- [ ] Every question has a design fork (if X, then [design change]; if Y, then [design change])
- [ ] No question whose answer is already determinable from the scenario (these are wasted questions)
- [ ] At least 2 questions per required category
- [ ] "Questions not asked" section present with at least 5 entries and reasoning
- [ ] Call sequencing plan present
- [ ] At least one question directly probes how the primary governance/approval rule works operationally (not just confirms that it exists)
- [ ] At least one question targets how the playbook is currently maintained and versioned (this affects RAG design fundamentally)

## Fail signals — do not produce output that contains these

- Questions that confirm scenario facts already given (e.g., confirming process volumes or team sizes already stated in scenario_context.md) — you already know this
- Questions with no design fork ("Can you tell us more about your process?")
- Generic questions from a discovery template that don't reference this scenario's specifics
- Questions that are really statements of concern dressed as questions ("Have you considered the risk of AI making mistakes?")
- Fewer than 15 questions, or questions padded with obvious/low-value content to reach the count
