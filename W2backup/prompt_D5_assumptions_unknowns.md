# Prompt: Deliverable 5 — Assumptions & Unknowns

## Scenario (read this first)
See `scenario.md`. Every assumption must be specific to this scenario. The scenario explicitly states: no appendix, no SOW, no sample claim data. Anything you needed but didn't have is an assumption or unknown. This deliverable is where you surface all of them — including every [TODO] and [ASSUMED] marker from Deliverable 3.

Also read `Delegation analysis.md` and `Capability specification.md` before writing this — all [TODO] items and [SCOPE-OUT] labels from those deliverables must appear here.

## Your task
Produce an assumptions and unknowns document. Output file: `5 Assumptions and unknowns.md` in the `Gate1/Output/` folder.

---

## Required structure

### 1. How to read this document
One short paragraph explaining how this log is used: assumptions that turn out to be wrong become scope changes or spec failures; unknowns left unresolved before build start are risks.

### 2. Assumptions register
Minimum 5 entries. Each must be specific to this FNOL scenario — not generic AI project assumptions.

Use this format for every entry:

```
[A-N] [Assumption title]
Statement: [What you are taking as given]
Domain: [Data / Systems / Organisation / Process / Regulatory]
Why it matters: [Which spec decision or metric this assumption drives]
If wrong: [What breaks — be specific about consequence]
Status: [ASSUMED / KNOWN / FLAGGED_FOR_VALIDATION]
Validation question: [The exact question to ask the client to confirm or refute this]
Confidence: low / medium / high
```

Required domains to cover (at least one entry per domain):
- **Data:** What do you assume about the quality, structure, or completeness of claim inputs?
- **Systems:** What do you assume about the CRM APIs, the SOAP endpoints, or the DMS?
- **Organisation:** What do you assume about adjuster capacity, specialist coverage, or team structure?
- **Process:** What do you assume about the current FNOL workflow that isn't stated in the scenario?
- **Regulatory:** What compliance constraints are you assuming apply — and are any confirmed?

### 3. Open unknowns
Things you cannot even assume — genuine blanks that must be answered before build.

Use this format:

```
[U-N] [Unknown title]
What we don't know: [The specific gap]
Why it blocks build: [What cannot be specified without this information]
Who can answer: [Role at the client — not a name, a role]
How to resolve: [Discovery activity — workshop, API audit, document review, etc.]
Priority: [BLOCKER / HIGH / MEDIUM] — BLOCKER means build cannot start without this
```

Minimum 3 open unknowns. At least 1 must be a BLOCKER.

### 4. Scope-outs
Any integration contract or requirement that was explicitly deferred in Deliverable 3 must appear here with a resolution plan.

Use this format:

```
[S-N] [Scope-out title]
What was deferred: [The specific item]
From: [Which section of Capability Specification]
Resolution plan: [Concrete step — e.g., "client to provide WSDL; mock stub in build until received"]
Owner: [who resolves this — FDE, client, or joint]
Deadline: [before what milestone this must be resolved]
```

### 5. Risk summary table
Consolidate the highest-risk items across all four categories:

| ID | Summary | If unresolved | Priority | Owner |
|----|---------|---------------|----------|-------|

---

## Acceptance criteria (all must pass)

- [ ] At least 5 assumptions present, each with all required fields
- [ ] All five domains covered (Data, Systems, Organisation, Process, Regulatory)
- [ ] At least 3 open unknowns present, at least 1 labelled BLOCKER
- [ ] Every [TODO] from Deliverable 3 is resolved or tracked here as an unknown
- [ ] Every [SCOPE-OUT] from Deliverable 3 appears in the Scope-outs section
- [ ] Every assumption has a validation question written in the form of a question to the client
- [ ] "If wrong" consequence is specific (not "things could go wrong")
- [ ] Risk summary table present

## Fail signals — do not produce output that contains these

- Generic assumptions not tied to this scenario ("AI systems can fail", "change management is hard")
- Assumptions without validation questions — an assumption with no way to test it is just a gap
- "If wrong: project risk increases" — non-specific consequences
- Missing coverage of any of the five required domains
- No BLOCKER unknowns (if everything is resolvable, the analysis is too optimistic)
- [TODO] or [SCOPE-OUT] items from Deliverable 3 that do not appear here
- Assumptions that are actually facts from the scenario (the 300 claims/day figure is not an assumption — it is given)
