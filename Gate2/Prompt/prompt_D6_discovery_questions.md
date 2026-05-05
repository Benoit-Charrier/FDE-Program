# Prompt: Discovery Questions for the Main Stakeholder (Generic Template)

## Scenario (read this first)
See `scenario\scenario_context.md` for the full scenario, work streams, tooling, and named-systems guidance. Do not invent numbers, systems, or constraints not present in the scenario. Every number you use must trace back to the scenario or be explicitly labelled as an assumption.

---

## Your task
Produce a set of discovery questions for the main stakeholder identified in scenario_context.md. Be concise. Output file: `deliverables\D6_discovery_questions.md`.

These must be questions whose answers would **actually change your agent design** — not generic discovery questions, not questions whose answers you can already infer from the scenario, and not questions that demonstrate you haven't thought through the design yet.

**Before writing each question, apply this test:**
> "If the answer is X, what changes in my design? If the answer is Y, what changes?"
> If both answers lead to the same design, the question is not useful. Do not write it.

Reference: `references\discovery-questioning-patterns.md`.

---

## Required structure

### 0. Executive summary
Three bullet points, written first. Each bullet is one sentence. Cover in order:
1. The single most design-critical unknown — the question whose answer would most change the agent's scope, autonomy boundary, or architecture (name the specific design decision it affects)
2. The governance question that must be resolved before any build decision is made — what about the primary hard constraint is still operationally unclear from the scenario alone
3. The question most likely to reveal a dealbreaker — the system or data access assumption that, if wrong, blocks the agent entirely

This section must be self-contained — a reader who reads only this section should understand what the FDE most needs to learn, why the governance constraint is still open, and where the highest buildability risk sits.

### 0b. Table of contents
List all sections by number and title as markdown anchor links, in order. Generate this after the full document is written — section titles must match exactly. Format each entry as `[N. Section title](#n-section-title)` using lowercase and hyphens for spaces.

Example format:
- [0. Executive summary](#0-executive-summary)
- [0b. Table of contents](#0b-table-of-contents)
- [1. Stakeholder context](#1-stakeholder-context)
- [2. Questions whose answers would change the design](#2-questions-whose-answers-would-change-the-design)
- [3. Questions you are NOT asking — and why](#3-questions-you-are-not-asking--and-why)
- [4. Sequencing for a 60-minute discovery call](#4-sequencing-for-a-60-minute-discovery-call)

### 1. Stakeholder context
One paragraph. The main stakeholder is identified in scenario_context.md — read their role, tenure, and the team they oversee from there.

Address all three of the following:
- What does this stakeholder care about most in the context of this process? (draw from stated business pressures in the scenario, not generic priorities)
- What is their primary concern about AI involvement? (grounded in the hard constraints and compliance gaps stated in the scenario — not generic AI risk)
- What would make them trust or distrust an agent? (draw on any non-negotiable governance rules and unresolved compliance issues stated in the scenario)

This paragraph informs the framing and sequencing of your questions — do not skip it.

---

### 2. Questions whose answers would change the design

Produce at least 15 questions grouped into the six categories below. For each question, include the design fork — what different answers would change in your agent design.

**Format for every question:**

> **Q[N]: [the question — concrete, specific, not leading]**
> **Category:** [category letter and name]
> **What I already infer from the scenario:** [what you can already deduce so you are not asking about it]
> **If the answer is [X]:** [what changes in the design]
> **If the answer is [Y]:** [what changes in the design]
> **Why this matters more than a generic question:** [1 sentence tying it to a specific design decision]

---

**Required categories (at least 2 questions per category):**

#### Category A: Reference material — structure, authority, and machine-readability
The scenario references a policy document, playbook, knowledge base, or ruleset (identified in scenario_context.md) but may not describe its format, versioning, update cadence, or who owns it. Questions here would change how you design the agent's knowledge retrieval, how often it must be refreshed, and how much you can trust a static snapshot.

*Ask about:* format (structured vs narrative), versioning, who updates it and when, whether there are known gaps or out-of-date sections, whether it lives in a machine-readable system or in documents.

#### Category B: Core decision logic — how the primary classification or routing actually works today
The scenario tells you the outcome split (e.g., X% routed one way, Y% another) but may not describe the reasoning that produces those splits in practice. Questions here would change the agent's decision logic, confidence threshold design, and what signals drive the primary classification.

*Ask about:* the criteria used in borderline cases, what information the reviewer checks before deciding, how consistent the decision is across reviewers, whether the logic is written down or tacit, what percentage of cases are genuinely ambiguous.

#### Category C: Governance and approval constraint — exactly how it operates
The scenario's primary governance or approval constraint (identified in scenario_context.md) is stated but may be operationally vague — who triggers it, how it is recorded, what the audit trail looks like. Questions here would change the autonomy matrix, the HITL workflow design, and whether the constraint is technically enforceable or just a policy statement.

*Ask about:* who performs the approval and in what system, whether approval decisions are logged with timestamps and identity, what happens if the approval step is skipped, whether the constraint has ever been bypassed under pressure.

#### Category D: Exception patterns and escalation triggers
The scenario implies a minority of cases require escalation or senior review but may not describe what makes those cases different. Questions here would change the agent's escalation trigger design, confidence gate thresholds, and the failure modes you need to protect against.

*Ask about:* what the last three escalated cases had in common, what signals a reviewer uses to recognise an edge case before fully processing it, whether there are known exception types that recur regularly, what happens when an exception is missed.

#### Category E: Data and system reality
The scenario names specific systems (identified in scenario_context.md) but not the operational reality — API maturity, data quality, access model, integration gaps. Questions here would change your gap analysis, integration architecture, and which parts of the design are blocked until system access is confirmed.

*Ask about:* whether the systems named have APIs or require screen-scraping, where data is incomplete or inconsistent, whether any relevant data lives outside the named systems (spreadsheets, email, someone's head), which system is considered the authoritative source when they disagree.

#### Category F: Organisational and trust context
The scenario may state the stakeholder's comfort level with automation. Questions here would change the HITL rate, rollout approach, oversight design, and how you sequence automation against compliance risk or political constraints.

*Ask about:* what a failed or wrong agent output would mean for this stakeholder personally, whether there is a recent incident that has made the team cautious, what the minimum visible human oversight step would be to make the deployment politically acceptable, whether the team would want to see agent outputs before or after a decision is made.

---

### 3. Questions you are NOT asking — and why

List 5 questions that a less disciplined analyst might ask, and explain why you are not asking them:

> **Question not asked:** [the generic or low-value question]
> **Why not:** [either it is already answered by the scenario / it has no design fork / it is too early to ask / it would waste the stakeholder's time]

This section demonstrates that your question list is curated, not exhaustive.

---

### 4. Sequencing for a 60-minute discovery call

Using the 60-minute call structure from `references\discovery-questioning-patterns.md`, sequence your top 10 questions into a call plan. Column "Goal for this segment" must describe what decision or unknown you are trying to resolve — not just the category name.

| Time slot | Question(s) | Goal for this segment |
|-----------|------------|----------------------|
| 0–5 min | Context setting | Establish rapport; confirm scope of their role and which parts of the process they own directly |
| 5–15 min | Broad funnel | |
| 15–30 min | Narrow funnel — one real case, walked through | |
| 30–45 min | Lived vs. documented probe | |
| 45–55 min | Delegation signals — codifiability, risk, trust | |
| 55–60 min | Close and next steps | |

---

## Acceptance criteria (all must pass)

- [ ] At least 15 questions total
- [ ] Every question has a design fork — if X, then [specific design change]; if Y, then [specific design change]
- [ ] No question whose answer is already determinable from the scenario (these are wasted questions — you already know the answer)
- [ ] At least 2 questions per required category
- [ ] "Questions not asked" section present with at least 5 entries and reasoning
- [ ] Call sequencing plan present; "Goal for this segment" column is specific to the design decision being resolved, not just a category label
- [ ] At least one question directly probes how the primary governance/approval constraint works operationally — not just confirms that it exists
- [ ] At least one question targets how the reference material (playbook/policy/ruleset) is maintained and versioned — this affects retrieval design fundamentally

## Fail signals — do not produce output that contains these

- Questions that confirm scenario facts already given (volumes, team sizes, system names already stated in scenario_context.md) — you already know this
- Questions with no design fork ("Can you tell us more about your process?")
- Generic questions from a discovery template that do not reference the specific constraints, gaps, or governance rules in this scenario
- Questions that are really statements of concern dressed as questions ("Have you considered the risk of AI making mistakes?")
- Fewer than 15 questions, or questions padded with obvious or low-value content to reach the count
- Questions where X and Y answers lead to the same design — these waste the stakeholder's time
