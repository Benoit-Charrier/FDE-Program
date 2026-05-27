# Prompt: D2C — Volume × Value Analysis

## Methodology references

- `References/atx-scoring.md` — Volume × Value scoring formula and priority matrix

## Inputs

- `Scenario/scenario_context.md` — §3 (volume, metrics), §4 (work streams)
- `Deliverables/02-cognitive-delegation.md` — Part B (delegation archetypes per JtD)

## Your task

Score each JtD from the delegation matrix on volume and value to identify the highest-ROI automation target. This output directly informs which agent to build (P3) and the economics model (P7).

Output file: `Deliverables/D2C_volume_value.md`

---

## Required structure

### 0. Scoring methodology
State the scoring approach in 2–3 sentences. Volume and value are each scored 1–5. Combined score = Volume × Value (max 25). Higher score = higher-priority automation candidate.

**Volume scoring guide (1–5):**
- 5: Runs on every case / every day; high frequency
- 3: Runs on most cases; moderate frequency
- 1: Rare; exception path only

**Value scoring guide (1–5):**
- 5: High financial impact OR regulatory risk OR significant time saving per occurrence
- 3: Moderate impact — meaningful but not critical
- 1: Low individual impact; value comes only from accumulation

### 1. Volume × Value matrix

| JtD | Description | Volume (1–5) | Volume rationale | Value (1–5) | Value rationale | Score (V×V) | Current archetype |
|-----|-------------|-------------|------------------|-------------|-----------------|-------------|-------------------|

### 2. Top automation candidates
Rank the top 3 JtDs by score. For each:

> **[Rank N] — JtD-[X]: [name]** (score: [N])
> Why high volume: [specific reason from scenario]
> Why high value: [specific reason — financial, risk, or time]
> Current archetype: [from Part B of P2]
> Recommended delegation shift: [what changes if automated — e.g., "fully agentic" for the high-confidence path, "agent-assisted" for the edge case path]

### 3. Agent scope recommendation
Based on the top candidates, name the single agent scope that captures the most value for the build:

> **Recommended agent:** [name and one-sentence scope]
> **Why this scope:** [highest V×V score + feasible given delegation archetype]
> **What it excludes:** [JtDs left out and why — out of scope, too risky, or requires a second wave]
> **Volume it covers:** [% of total daily / monthly volume this agent handles]

---

## Acceptance criteria

- [ ] All JtDs from P2 Part B appear in the matrix — none skipped
- [ ] Volume and value rationales reference specific scenario figures or label assumptions
- [ ] Top 3 candidates have written justification beyond the score
- [ ] §3 names a single recommended agent scope with explicit exclusions
- [ ] Volume coverage stated as a percentage of total stated volume
