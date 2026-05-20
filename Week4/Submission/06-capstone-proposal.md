# Gate 4 — D6: Capstone Proposal
**Scenario: Option A — Healthcare Claims Processing Transformation**
**Client: Greenfield Health Systems**
**Submitted by: Benoit Charrier, FDE**
**Date: 2026-05-20**

---

## 1. Problem Framing

Greenfield Health Systems processes ~50,000 medical claims per month (≈2,000/day) with a team of 45 processors. Claims arrive from providers in three formats — EDI 837, PDFs, and portal submissions — each requiring eligibility verification, coding validation, medical necessity review, and payment determination.

Current state:
- **Average cycle time:** 8–9 days (payer SLA threshold is 7 days; contractual penalties are live)
- **Auto-adjudication rate:** 22% (industry benchmark: 85%)
- **Denial appeal overturn rate:** 41% — indicating systematic first-pass errors, not edge-case mistakes
- **Average processing time per claim:** 35 minutes, most of it spent on work that is verifiable against structured data sources

The core problem is not that humans are slow — it is that humans are doing deterministic work. Eligibility checks, coding validation, prior auth completeness checks, and format verification are rule-governed lookups with fixed correct answers. Physicians are doing this alongside genuinely clinical judgment tasks. The result: the wrong work is expensive, and the right work (clinical review of complex claims) is crowded out.

Stakeholder alignment has already resolved the key tension. CFO Sarah Chen requires cost reduction (40% headcount reduction, $400K budget). CMO Dr. Marcus Webb requires physician review of every claim with clinical content. VP Operations James Liu requires cycle time below the 7-day penalty threshold. The resolution, negotiated in the stakeholder exchange, is:

- **65% of claims** are administrative (billing, coding, prior auth completeness) → agentic path, no physician required
- **35% of claims** have genuine clinical content → physician HITL, but with agent pre-screening reducing review time from 35 min to ~3 min per claim

This means the design question is already answered at the delegation boundary. The build question is whether the clinical content classifier can reliably make that 65%/35% split.

---

## 2. Success Metrics

**Operational targets (by end of Week 5 build):**

| Metric | Baseline | Target |
|--------|----------|--------|
| Auto-adjudication rate | 22% | ≥ 80% of administrative-path claims |
| Cycle time — admin path | 8–9 days | 4–5 days |
| Cycle time — clinical path | 8–9 days | 6–7 days |
| Physician review time per claim | 35 min | ≤ 5 min (pre-filled context) |
| First-pass error rate | 41% appeal overturn | ≤ 15% |

**Prototype-specific targets (demo-ready by Thursday):**

| Path | Definition of done |
|------|--------------------|
| Happy path | Administrative claim → all deterministic checks pass → auto-approved with audit record; end-to-end in < 30 seconds |
| Failure-mode escalation | Clinical content flagged → pre-filled physician review packet (diagnosis codes, prior auth history, clinical notes summary) generated and routed to HITL queue |
| Edge case | Classifier confidence below threshold → escalated with uncertainty flag; no silent auto-approval |

---

## 3. Intended Approach

**Two-agent pipeline with orchestrator routing:**

**Agent A — Administrative Screener (Haiku-tier)**
Runs first on every claim. Deterministic rule-following: eligibility check against member database, coding validation (ICD-10 / CPT lookup), prior auth completeness, format verification (EDI 837 field population). Pass/fail decision. If any check fails: reject with specific failure code (not a generic error). If all pass: hand off to classifier.

**Agent B — Clinical Content Classifier (Sonnet-tier)**
NLP classification: does this claim contain clinical content requiring physician judgment? Inputs: diagnosis codes, procedure codes, clinical notes, medical necessity rationale. Output: `CLINICAL` | `ADMINISTRATIVE` + confidence score (0.0–1.0).

**Routing logic:**
- `ADMINISTRATIVE` + confidence ≥ 0.85 → auto-approve, write audit record
- `CLINICAL` (any confidence) → generate pre-filled physician review packet, route to HITL queue
- Any result + confidence < 0.85 → escalate with uncertainty flag; do not auto-approve

**HITL queue design:** Physician receives a pre-filled packet (not the raw claim file) containing: extracted diagnosis codes, flagged clinical terms, prior auth history, and a 3-bullet summary of the clinical question. Target: physician decision time ≤ 5 minutes per claim.

**Mock data:** Simplified JSON claim objects covering: a routine billing claim (admin path), a physical therapy pre-auth with clinical notes (clinical path), and a claim with ambiguous diagnosis coding (edge case / low-confidence).

**CLAUDE.md scope:** Administrative Screener + Clinical Content Classifier + orchestrator routing. Physician queue interface is out of scope for the prototype — simulated as a log write.

---

## 4. Why This Is Hard Enough

The difficulty is not the deterministic checks — those are straightforward tool calls. The difficulty is in three places:

**The classification boundary is probabilistic, not deterministic.** The classifier must make a judgment call about clinical content in free-text fields and ICD codes that can be ambiguous. A hardcoded rules engine cannot do this. The boundary between "routine billing" and "clinical content" is exactly the kind of contextual reasoning that requires a language model — and that can fail.

**The cost of a false negative is asymmetric.** A false positive (clinical claim flagged as admin) floods the physician queue — operationally bad but recoverable. A false negative (clinical claim auto-approved without physician review) bypasses required oversight — a patient safety risk and a regulatory exposure. The spec must handle classifier uncertainty explicitly, with a confidence threshold that errs toward escalation. Designing that threshold correctly, and testing it against adversarial cases, is a real spec and validation problem.

**The HITL design is not just routing — it is cognitive load reduction.** "Route to physician" is not a HITL design. The spec must define what information the pre-filled packet contains, in what format, and in what sequence — so that a physician spending 5 minutes on a pre-screened claim makes a better decision than one spending 35 minutes reading the raw file. That requires understanding what physicians actually need to make a denial/approval decision, which is the ATX delegation design skill being tested.

---

## 5. What I Expect to Learn

**Primary question:** Can the clinical content classifier achieve sufficient precision/recall to run the 65%/35% split reliably on realistic claim data, or does the confidence threshold need to be set so conservatively that it collapses toward 80%+ physician review?

**Secondary questions:**
- What does a pre-filled physician review packet need to contain to genuinely reduce review time from 35 min to 5 min? What information is load-bearing vs. noise?
- How do I write a capability spec that makes the confidence threshold a configurable parameter — one that a compliance team could adjust after pilot without requiring a rebuild?
- What are the failure modes the happy-path prototype does not surface? (Specifically: what happens when an EDI 837 field is malformed, or when clinical notes are absent from a claim that has clinical diagnosis codes?)

**Anticipated curveball:** The CMO blocks auto-approval entirely — all claims require physician sign-off. The architecture survives this: the agent shifts from auto-approve to accelerate-physician-queue. The value proposition changes from "65% straight-through processing" to "35-min → 5-min physician review across 100% of claims." The core build (screening, classification, pre-filling) is the same; only the routing output changes. I will prepare this response explicitly for the defense.

---

## Scenario Selection Rationale (one paragraph)

Option A over B and C: domain fluency from Week 4 healthcare work (MedFlex, WS2 nurse-to-shift matching) eliminates a cold-start risk in a 4-day sprint. The 35%/65% delegation split is not invented — it was negotiated by the stakeholders, which means the hardest design decision has a client-anchored answer. Option B's economics were explicitly challenged as vague by the CFO in the stakeholder exchange. Option C requires a two-track narrative (Avaya 2010 platform rebuild + agent deployment) that adds scope without adding learning value, and its most likely curveball (CFPB bans automated refund decisions) hits the primary demo path directly.
