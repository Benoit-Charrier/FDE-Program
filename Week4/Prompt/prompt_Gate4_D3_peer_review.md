# Prompt: Gate 4 Deliverable 3 — Peer Review of a Capability Spec

## Inputs (read all of these before producing any output)

1. **Spec under review** — the capability spec file provided. Read it in full before assessing anything.
2. **Spec ambiguity vs. builder mistakes taxonomy** — `References/spec-ambiguity-vs-builder-mistakes.md`. Use this to classify every issue: spec gap, spec inconsistency, spec risk, builder misread, or test/environment issue.
3. **Production spec checklist** — `References/production-spec-checklist.md`. Use this as the completeness benchmark: the spec must pass this checklist for a builder to work from it without guessing.
4. **Integration spec template** — `References/integration-spec-template.md`. Use this to evaluate integration contracts: each contract must cover the 10 required sections. Flag missing sections as issues.

---

## Your task

Read the capability spec as both a **peer reviewer** (FDE lens: is this the right design?) and a **builder** (implementation lens: can I build this without ambiguity?).

Produce a structured peer review. The standard for "good review" is: real issues named against specific sentences or table rows, with concrete fixes. Generic feedback ("needs more detail", "unclear") is not acceptable — name the exact location and state exactly what is missing or wrong.

The anti-pattern to avoid: blocking everything. Find the one or two issues that would cause a builder to implement incorrect behaviour silently. Let things that are "different but defensible" pass.

---

## Required output structure

### Header

State:
- Spec name (as named in the file header)
- File reviewed (filename as provided)
- Status declared in the spec
- Spec creator (name provided at the end of the spec file)

---

### Overall assessment

Two to three sentences:
- Is this spec buildable as written?
- What is the single most important issue?
- Recommendation: accept / return with required fixes / escalate

---

### What can be built now

List the parts of the spec that are complete enough to implement immediately — specific sections, flows, or integration contracts where every required decision is made and every edge case is covered. Be precise: name the sections or flows, not just "most of the spec." This section comes first — start with the positive before raising issues.

---

### Issues requiring fixes

#### Blockers

Issues that must be fixed before the build starts. A blocker is any issue where:
- A builder following the spec exactly would implement wrong behaviour silently, OR
- A required decision has no answer anywhere in the spec and the builder cannot proceed without guessing

For each blocker:
- **ID**: B1, B2, …
- **Type**: from the spec-ambiguity-vs-builder-mistakes taxonomy
- **Location**: name the exact section, table row, or field where the issue appears
- **Finding**: what is wrong
- **If built as-is**: what a builder would implement as a result — the concrete wrong behaviour or guess they would produce
- **Fix**: the exact change needed — rewritten sentence, new table row, or new config parameter. Be specific enough that the spec author can apply the fix without interpretation.

#### Concerns

Real issues that do not block the build start but must be resolved before pilot or production. A concern is a design risk, an undefined edge case, or a missing configuration parameter that ops will need.

Same format as Blockers (ID: C1, C2, …).

---

### Acceptable differences

Items that look like issues but are not — defensible design choices, explicitly addressed gaps, or minor inconsistencies that do not affect builder behaviour. State what you noticed and why it passes. This section signals that you read the spec carefully, not that you ran out of issues to raise.

---

### Build readiness summary

Two tables — no severity column.

**Build now — no fixes required**

| Area | Spec sections |
|------|--------------|
| [complete area] | [section references] |

**Fix first — spec must be updated before builder proceeds**

| ID | Issue | Fix complexity |
|----|-------|----------------|
| B1 | [one-line description] | Trivial / Low / Medium |
| … | … | … |

---

### Attribution

> Spec reviewed: [spec file name]
> Spec creator: [name as provided at the end of the spec file]
> Reviewer: [your name]
