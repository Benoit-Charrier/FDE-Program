# Prompt: D0B — Scenario Context Extraction

## Your task

Read the sealed scenario packet (the materials provided at exam start) and extract all stated facts into `Scenario/scenario_context.md`. This file becomes the single source of truth for every subsequent prompt — all other prompts read from it, not from the raw scenario.

**Do not infer, extrapolate, or assume.** If a fact is not explicitly stated, mark the field as `[NOT STATED]`. Every gap you leave blank here will be surfaced as an assumption in later deliverables — that is correct behaviour.

Output file: `Scenario/scenario_context.md`

---

## Required structure for scenario_context.md

```markdown
# [Company Name] — [Domain]

*Extracted from sealed scenario packet. Single source of truth for all prompts.*

---

## 1. The company

**Name:** [company name]
**Industry / domain:** [what sector, what they do]
**Business model:** [how they operate — what they process, sell, or serve]
**Size / scale:** [headcount, revenue, volume — only if stated]
**Geography:** [if stated; otherwise NOT STATED]

---

## 2. The stakeholders

For each named stakeholder:

**[Name] — [Title]**
- Primary concern: [what they care about most]
- Non-negotiable position: [what they will not accept]
- Success looks like: [what winning means for them]

(List all named stakeholders from the scenario. Do not invent unnamed ones.)

---

## 3. The process

**Core process:** [what the primary work stream does — one sentence]
**Daily / monthly volume:** [stated volume figures; note inconsistencies if two figures are given]
**Current performance:** [baseline metrics — processing time, error rate, SLA, etc. — all stated figures]
**Current automation level:** [if stated]
**Industry benchmark:** [if stated]
**Cycle time / SLA:** [if stated]

---

## 4. The work streams

For each distinct work stream in the scenario:

**WS-[N]: [Name]**
- What it does: [one sentence]
- Who does it today: [role / team]
- Volume: [if stated]
- Key pain: [the stated problem with this stream]

---

## 5. Systems and tooling

List every system, tool, or platform named in the scenario. If no systems are named, write: "No systems named in scenario — all tooling is an assumption."

| System | Stated purpose | Integration notes |
|--------|---------------|-------------------|

---

## 6. Compliance and regulatory requirements

List every compliance requirement, regulatory constraint, or mandatory human-in-the-loop rule stated in the scenario. If none stated, write: "No compliance requirements explicitly stated."

---

## 7. Stakeholder tensions

Summarise the stated tensions between stakeholders. Use the exact exchange or quote from the scenario where available.

---

## 8. Key metrics (baseline)

| Metric | Value | Source |
|--------|-------|--------|

---

## 9. Open gaps (facts needed but not stated)

List facts that later prompts will need but that the scenario does not provide. These become low-confidence assumptions.
```

---

## Acceptance criteria

- [ ] Every section populated — no section left empty; gaps written as `[NOT STATED]`
- [ ] All stated numbers present in §3 and §8 with source citation (which part of the scenario)
- [ ] All named stakeholders in §2 with primary concern and non-negotiable position
- [ ] No invented facts — only what the scenario explicitly states
- [ ] Inconsistencies (e.g. two different volume figures) are noted, not resolved
- [ ] §9 lists at least 3 open gaps that will become assumptions in later deliverables
