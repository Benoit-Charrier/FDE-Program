# Prompt: Deliverable 9 — Assumptions & Unknowns

## Scenario (read this first)
See `scenario\scenario_context.md` for the full scenario, work streams, tooling, and named-systems guidance. Do not invent numbers, systems, or constraints not present in the scenario. Every number you use must trace back to the scenario or be explicitly labelled as an assumption.

**Agent context:** Produce this document for the agent designed in D4. Pull the assumptions already logged across D0–D5 — do not repeat analysis, consolidate it. The value of this deliverable is honesty, not comprehensiveness: a plausible-sounding guess that turns out to be wrong mid-build is more expensive than an explicit "I don't know."

---

## Your task
Produce an Assumptions & Unknowns register. Be concise. Output file: `deliverables\D9_Assumptions_&_Unknowns.md`.

Read back through D0C (problem statement), D0D (discovery), D1 (cognitive load map), D2 (delegation suitability matrix), D3 (volume/value analysis), D4 (agent purpose document), and D5 (system/data inventory). Every assumption or unknown flagged in those deliverables must appear here. Then add any that are still missing.

---

## Required structure

### 0. Executive summary
Three bullet points, written first. Each bullet is one sentence. Cover in order:
1. The assumption the entire build rests on most — the one that, if wrong, would require redesigning the core architecture (name the specific assumption and what it drives)
2. The unknown with the highest pre-build urgency — what must be confirmed before a single line of spec is finalised, and who can answer it
3. The honest risk statement — what the build is most likely to get wrong, and whether the two resolution paths share enough structure to design for reversibility

This section must be self-contained — a reader who reads only this section should understand the load-bearing assumption, the most urgent open question, and the primary build risk.

### 0b. Table of contents
List all sections by number and title as markdown anchor links, in order. Generate this after the full document is written — section titles must match exactly. Format each entry as `[N. Section title](#n-section-title)` using lowercase and hyphens for spaces.

Example format:
- [0. Executive summary](#0-executive-summary)
- [0b. Table of contents](#0b-table-of-contents)
- [1. Consolidated assumption register](#1-consolidated-assumption-register)
- [2. Genuine unknowns](#2-genuine-unknowns)
- [3. Validation priority matrix](#3-validation-priority-matrix)
- [4. Top 3 unknowns — risk summary](#4-top-3-unknowns--risk-summary)

### 1. Consolidated assumption register

Pull every assumption already logged in D0C–D5. Consolidate duplicates. Use this format for each entry:

| ID | Assumption | Source deliverable | Category | Why it matters | If wrong | Confidence |
|----|-----------|-------------------|----------|----------------|----------|------------|
| A-1 | | D0 / D1 / D2 / D3 / D4 / D5 | data / systems / organisation / problem definition | | | low / medium / high |

**Categories:**
- **data** — assumptions about what data exists, its quality, its format, or its accessibility
- **systems** — assumptions about APIs, integrations, field schemas, or what a named system can actually do
- **organisation** — assumptions about how people work, who owns a process, what approval chains look like in practice
- **problem definition** — assumptions about the scope of the problem, what "success" means to the stakeholder, or what the agent is actually being asked to solve

Minimum 8 entries. If you cannot find 8 from D0–D5, that is a gap in the prior deliverables — note it and add the missing ones here.

---

### 2. Genuine unknowns

List at least 5 unknowns that are **not** resolvable by reading the scenario — things you genuinely do not know about the client's data, systems, organisation, or problem. An unknown is different from an assumption: an assumption is something you have taken as given; an unknown is something you have not yet taken a position on because you lack the information.

Use this format for each entry:

> **Unknown [U-N]: [the specific thing you do not know]**
> **Category:** data / systems / organisation / problem definition
> **Why it matters for the build:** [what design decision is blocked or at risk until this is resolved]
> **Consequence if unresolved:** [what gets built wrong — not "it might not work," but the specific failure mode]
> **How to validate:** [the specific question to ask, the specific document to request, or the specific test to run — name the person or system]
> **When to validate:** before build starts / before first production contract / can defer to v2

Do not write generic unknowns. "We don't know if the API works" is not an unknown — it is an untested assumption. "We don't know whether the system of record's primary classification field is a free-text string or a constrained enum, which determines whether the agent's output can be validated at write time or only post-hoc" is an unknown.

---

### 3. Validation priority matrix

Classify every assumption (from section 1) and every unknown (from section 2) into one of three tiers:

| Tier | Criteria | Items (IDs) |
|------|----------|-------------|
| **Must validate before build starts** | If wrong, the agent's core architecture changes — data model, delegation archetype, or primary integration point would need to be redesigned | |
| **Must validate before first production contract** | If wrong, the agent produces incorrect output in production but the architecture is still sound — a configuration or threshold change fixes it | |
| **Can defer to v2** | If wrong, the agent is suboptimal but not broken — the risk is inefficiency or a worse user experience, not incorrect routing decisions or compliance failures | |

At least 3 items in each tier. If everything falls into "can defer," that is a sign the unknowns are not genuine.

---

### 4. Top 3 unknowns — risk summary

Identify the 3 unknowns from section 2 that carry the highest build risk. For each, write 3–5 sentences covering:
- What you are building on the assumption that this unknown resolves a certain way
- What the build would look like if it resolves the other way
- Whether the two builds share enough structure that you can design for reversibility, or whether they diverge fundamentally

This section is the honest answer to: "what are you most likely to get wrong, and why?"

---

## Acceptance criteria (all must pass)

- [ ] At least 8 entries in the consolidated assumption register, sourced from D0–D5
- [ ] At least 5 genuine unknowns — each with a specific consequence and a specific validation method
- [ ] Every unknown is scenario-specific — no entry applies equally to all AI projects
- [ ] Validation priority matrix has at least 3 items in each tier
- [ ] Top 3 risk summary names what the build looks like under each resolution path — not just "it would be different"
- [ ] Unknowns are distinguishable from assumptions — the format enforces this
- [ ] No entry says "I don't know if it will work" without naming the specific thing that would or would not work

## Fail signals — do not produce output that contains these

- Assumptions that are self-evidently true and carry no risk if wrong (e.g., "we assume the process will generate some work items")
- Unknowns that are resolvable by reading the scenario — if the scenario tells you the answer, it is not an unknown
- "How to validate" entries that say "ask the stakeholder" without specifying what question to ask or what document to request
- All unknowns in the "can defer to v2" tier — if everything is low-stakes, the unknowns are not genuine
- A top-3 risk summary that describes risk in the abstract ("this could cause problems") rather than naming the specific failure mode and the specific part of the build it affects
- Fewer than 5 unknowns, or unknowns padded with obvious items to reach the count
