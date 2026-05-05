# Stakeholder Presentation — Helix Workforce Software
## Vendor Contract Clause Review: Assessment Findings & Proposed Solution

---

## Slide 1: Title
**Type:** Title

**Helix Workforce Software**
**Vendor Contract Clause Review**

Assessment Findings & Proposed Solution

*[Date]*
*[Presenter name]*

**Speaker notes:**
I want to set expectations before we start: this is not a generic AI pitch. We've spent the last several weeks mapping how the Legal & Commercial team actually works — the volume, the bottlenecks, the governance rules — and what we're presenting today is a specific recommendation grounded in that analysis. We'll show you what we found, what we think should be built, and the decisions that only you can make before we can finalise the design.

---

## Slide 2: Agenda
**Type:** Section divider

1. The business problem — what we were asked to solve
2. What we found — where the work actually goes
3. What we recommend — the proposed solution
4. Decisions we need from you — open questions that change the design
5. Next steps — what happens before we can build

**Speaker notes:**
We'll move through five sections. The first two are findings — we'll earn the recommendation before we make it. The third is the recommendation itself, including where the system stops. The fourth is critical: there are five questions whose answers will materially change what we build. And the fifth is a concrete action list. I'll pause for questions throughout, but I've also reserved ten minutes at the end specifically for the decisions we need your input on.

---

## Slide 3: Why We Are Here — The Business Problem
**Type:** Content

- **125 hours of paralegal time per quarter** consumed by first-pass clause review — before any negotiation begins *(300 contracts × 25 min ÷ 60) [D3, scenario_context.md]*
- **4–6 day review cycle, with CRO pressure to halve it** — first-pass classification is the intake gate that everything else waits on [D1, D3]
- **Active compliance risk:** every Data Processing Agreement reviewed today is measured against a playbook that has not incorporated the DPDI Act's Q1 changes — 9 months stale [D4, scenario_context.md]

**The question this assessment set out to answer:** Can first-pass clause classification be reliably automated, with the named-lawyer sign-off requirement preserved and auditable — not assumed?

**Speaker notes:**
The 125-hour figure is worth pausing on. That's the equivalent of roughly three full working weeks every quarter that Tom spends reading contracts and comparing clause text against the playbook — before a single redline is drafted or a single lawyer is consulted. That's not wasted time, but it is time being spent on a task that follows a consistent enough pattern that a machine can do most of it. The compliance risk on the DPA clause is a separate issue, and it's not something we introduced — it exists in your process today, agent or no agent. We'll come back to it, because it has direct implications for what we can build and when.

---

## Slide 4: How the Work Actually Flows Today
**Type:** Content

```
Vendor contract (.docx, ~25 pages)
  ↓ via Outlook email
[WS1: First-pass clause classification]  — 300 contracts/quarter, ~25 min each
  │
  ├─ 70% standard → Accept as-is                       (~210 contracts)
  ├─ 20% deviation → [WS2: Paralegal redlining]         (~60 contracts, ~45 min each)
  └─ 10% escalation → [WS3: Senior lawyer review]       (~30 contracts, ~90 min each)
                                ↓
               [WS4: Counteroffer package + sign-off]   (~90 contracts, ~30 min each)
                                ↓
                         Vendor dispatch
```

**Most cognitive effort: WS1 — the classification step that determines every contract's path**

*[D1, scenario_context.md]*

**Speaker notes:**
What matters here is the architecture. WS1 is not just one of four work streams — it's the gate. Nothing moves to WS2, WS3, or WS4 until WS1 is done. At 25 minutes per contract across 300 contracts, that's where the time goes and where the turnaround delay originates. The 70/20/10 split is the other key fact: the majority of contracts are actually standard — they follow the playbook without deviation. The challenge is that you have to read every one of them to know which category they're in. That's the problem we're trying to solve.

---

## Slide 5: Where Time Goes — The Three Judgment Calls That Slow Everything Down
**Type:** Content

**1. Deciding whether a clause deviation is material enough to escalate**
Tom compares extracted clause language against playbook positions across 7 clause types. For qualitative clauses — IP ownership, indemnity scope — this requires judging whether the commercial intent is equivalent, even when the wording differs. Judgment call that varies case by case. *Automatable with structured oversight.* [D1]

**2. Locating the right clause when vendor documents use non-standard headings**
A clause titled "Commercial Exposure" may contain liability cap language. Tom recognises this through experience. Without a trained pattern library, an agent misses it entirely. *Skill-intensive; requires a curated knowledge base before automation is viable.* [D1, D5]

**3. Assessing DPA clauses against a compliance baseline that isn't current**
Tom reviews Data Processing Agreements against a playbook he knows is 9 months stale. He cannot flag DPDI Act gaps reliably without Amelia's completed update. *Every DPA review today carries latent compliance risk — agent or no agent.* [D1, D4]

**Speaker notes:**
These three moments are where the skilled attention actually goes. The first is the one we can automate most readily — it follows a pattern, even if that pattern isn't perfectly deterministic. The second is a knowledge gap we can fill by training the system on historical contract structures. The third is the one that keeps me up at night: it's not an AI problem, it's a data quality problem. An agent trained on the current playbook will produce the same compliance-risk classifications that Tom produces today — at scale. That's why the playbook update isn't optional background work. It's a deployment gate.

---

## Slide 6: What Can Be Delegated to an Agent — and What Cannot
**Type:** Content

| Agent-suitable | Human-anchored |
|---|---|
| Contract intake, routing, and case record creation — structured task, no judgment | **Named-lawyer counteroffer sign-off — GC rule: no counteroffer may leave Legal's queue without a named lawyer's approval recorded in Ironclad; non-negotiable hard stop** |
| Clause text extraction from vendor documents — pattern recognition against known structures | Senior lawyer review of unusual clauses outside the 7 playbook categories — no policy position exists for these |
| Standard clause comparison — matching extracted text against playbook positions | DPA clause review while playbook update is outstanding — mandatory human review on every DPA case until DPDI Act changes are incorporated |
| Exception flagging — when deviation magnitude exceeds defined thresholds, routing is deterministic | Redline drafting for qualitative clause types (IP, indemnity) — synthesis judgment; no templatable output |
| Counteroffer package assembly — compiling approved redlines into a structured sign-off package | |

*[D2, D4]*

**Speaker notes:**
The right column is not a negotiating position — it reflects the governance constraint you've already built into the process over 12 years. The GC hard rule is listed first because the architecture is designed around it: the system is built so the agent literally cannot dispatch a counteroffer without a named lawyer's approval token being present in the case record. It's not a warning — it's a hard architectural stop. The other items in the right column reflect genuine complexity limits: qualitative redline drafting requires legal synthesis that no classification system can reliably substitute for, and DPA review is human-mandatory until the playbook catches up.

---

## Slide 7: The Opportunity — Where Volume Meets Complexity
**Type:** Content

| | Low complexity (routine, pattern-based) | High complexity (judgment-intensive, varies case-by-case) |
|---|---|---|
| **High volume** | — | **★ WS1: Clause classification** — primary target |
| **Low volume** | — | WS2: Redlining · WS3: Escalations · WS4: Counteroffers |

**WS1 — primary agentic target:** score 12 out of 25 — the only work stream that combines sufficient volume with the type of judgment-based work that AI handles well [D3]

> **TCO directional finding:** ~£43,000 projected annual saving (WS1 + counteroffer package preparation). Estimated build cost: ~£60,000. Directional payback: ~17 months. *(All figures based on UK paralegal/lawyer rate assumptions — to be validated against actual rates; see D3 §8 for full derivation.)* [D3]

**Speaker notes:**
The key insight from this analysis is that WS2, WS3, and WS4 score high on complexity but low on volume — they're difficult cases, but there aren't enough of them to justify building a standalone automation. WS1 is the only work stream where the volume justifies the build cost and where the judgment pattern is consistent enough to replicate. A score of 12 out of 25 means "consider building, and validate the conditions before you commit to it" — it's not a slam dunk, it's a strong conditional case. The 17-month payback is directional, not a firm commitment: it assumes a UK paralegal rate and API token cost estimates that should be confirmed before signing off on a build budget.

---

## Slide 8: The Proposed Solution — What the Agent Does
**Type:** Content

**Agent name:** Clause Classification Agent (CCA) [D4]

- **Receives** every inbound vendor contract via Ironclad, reads the full document, and extracts the text for each of the 7 clause types the playbook covers
- **Compares** each extracted clause against the current Helix playbook position and assigns a classification: standard, deviation, or escalation-required — with a certainty level on each decision
- **Routes** standard-path contracts (those where all 7 clauses are within playbook tolerances and certainty is above threshold) for acceptance without requiring Tom's full review — cutting WS1 time from 25 minutes to under 5 minutes for those contracts
- **Prepares** a structured deviation summary for the ~30% of contracts where clauses fall outside playbook tolerances — Tom reviews the agent's findings, not the full document

**What it replaces:** the 125 hours/quarter Tom currently spends reading contracts end-to-end to perform initial clause comparisons
**What it produces:** a per-clause classification report, a routing decision, and a structured input to the counteroffer package pipeline [D4]

**Speaker notes:**
I want to be concrete about what "reduces Tom's time" actually means. For the 70% of contracts that are standard, Tom currently reads every page to confirm nothing deviates. With this agent, he receives a notification: "All 7 clauses within playbook tolerance, certainty above threshold — no action required unless you want to spot-check." For the 30% of contracts with deviations, Tom currently does the comparison himself. With this agent, he receives a structured summary: here is the clause, here is the playbook position, here is how far they diverge, here is the agent's proposed routing. He makes the routing decision; he doesn't redo the comparison. That's the value proposition.

---

## Slide 9: Where the Agent Stops — The Approval Boundary
**Type:** Content

| Agent decides alone | Agent proposes, human approves | Human only |
|---|---|---|
| Contract intake, case record creation, clause extraction | Any contract with one or more deviating clauses — Tom approves the routing before the case moves forward | **Named-lawyer counteroffer sign-off — GC rule: the agent cannot write, simulate, or bypass the approval token; the approval must be recorded by the lawyer in Ironclad before any counteroffer proceeds; enforced by system design, not by policy** |
| Standard-path classification with certainty ≥ 85% across all 7 clause types | All DPA clause assessments while the DPDI Act playbook update remains outstanding | Senior lawyer review of clause types outside the 7 playbook categories — no automation path exists for these |
| Routing standard contracts to the "accept" queue — Tom is notified but no review required | Any classification where the agent's certainty falls below 85% — Tom reviews the clause text and the agent's reasoning before the decision commits | — |

*[D4 §5, Deliverables/CLAUDE.md]*

**The approval gate is enforced at the database level: the agent's access credentials cannot write to the sign-off field. No instruction — from a downstream system or a human operator — can override this constraint.**

**Speaker notes:**
The phrase "enforced by design, not by policy" is the critical distinction here. Policy says "lawyers must sign off." Design means the database field that records the sign-off cannot be written by the agent — the agent's API credentials are denied write access to that field entirely. A counteroffer dispatch that depends on that field being non-empty cannot proceed without a lawyer physically taking an action in Ironclad. This is not a trust-the-AI question. It's an architecture question, and the answer is: the system cannot bypass this gate. That's what twelve years of sign-off culture looks like in code.

---

## Slide 10: Integration Readiness
**Type:** Content

| Integration | Status | What it means |
|---|---|---|
| **Ironclad CLM** (most critical) — REST API available; per-clause classification fields require custom configuration | **AMBER** | API exists and is confirmed. But the agent needs ~35 custom fields added to contract records (one set per clause type) before it can write its outputs. This must be scoped with the Ironclad admin before build begins. [D5 Gap G-4] |
| **HITL review channel** — no confirmed mechanism for routing flagged contracts to Tom | **RED — blocking** | The agent can classify, but without a confirmed review channel it cannot deliver flagged results to Tom. The entire oversight workflow is blocked until this is resolved. Options: Ironclad-native workflow, or Outlook shared inbox. [D5 Gap G-1] |
| **DPDI Act regulatory reference** — document not yet produced; playbook 9 months stale | **RED — deployment gate** | The agent cannot classify DPA clauses against the DPDI Act's Q1 changes until Amelia's update is completed and loaded into the knowledge base. All DPA clauses are mandatory human review until resolved. [D5 Gap G-2, D4 §8] |

**One confirmation needed before build can start:** Can Ironclad be configured with custom per-clause classification fields? Ironclad admin must confirm schema expandability.

*[D5]*

**Speaker notes:**
I want to be honest here: we have two blocking gaps and one deployment gate. This is not "we're ready to build." It is "we can start the build specification, but there are three things that must be resolved before we go live." The HITL channel is a design decision as much as a technical one — Tom needs to tell us how he wants to receive flagged contracts, because that determines whether we use Ironclad's workflow engine or Outlook. The Ironclad field schema is a confirmation, not a design question — the Ironclad admin either supports custom fields or they don't. The DPDI Act update is on your critical path, Amelia, and it currently has no owner and no date.

---

## Slide 11: What We Need From You — Five Questions That Change the Design
**Type:** Content

1. **How does Tom currently decide whether a clause deviation is serious enough to escalate?** Does he compare wording against specific playbook language, or judge whether the commercial intent is equivalent even if the wording differs? *(The answer determines how we design the comparison logic — and how accurate the agent can realistically be at launch.)* [D6 Q4]

2. **When a lawyer signs off on a counteroffer today, where does that approval live?** Is it a recorded action in Ironclad, an email, a verbal confirmation — or is it not formally recorded at all? *(If sign-off currently happens outside Ironclad, the approval gate architecture requires a process change before we can build it.)* [D6 Q7]

3. **Can any of the three commercial lawyers sign off on any clause type, or does authority vary by clause?** For example, is Amelia the only one who can approve a DPA deviation? *(If authority varies by clause type, the system must route each case to the correct lawyer — a different routing design.)* [D6 Q8]

4. **When a lawyer approves, does one sign-off cover the whole counteroffer package, or does each deviated clause need its own approval?** *(Contract-level approval is one field in the system. Clause-level approval is a much more complex approval workflow.)* [D6 Q9]

5. **The DPDI Act playbook update has been in discussion since March. Is there a named owner and a committed completion date?** *(This is a deployment gate: the agent cannot classify DPA clauses reliably without it. If it has no owner, the timeline for any DPA-clause handling is indefinite.)* [D6 Q16]

**Speaker notes:**
These five questions are ones we genuinely cannot answer from what we already know about your process — and each one has a direct impact on what we build. Q4 affects the confidence threshold design — getting it wrong means the agent systematically disagrees with Tom's classifications in a way that won't show up until we're in production. Q7, Q8, and Q9 together determine the entire approval token architecture: if sign-off is currently informal or outside Ironclad, we need to address that as a process gap before we can enforce it in the system. Q16 is the one I'd most like to resolve today, because it's blocking a specific part of the build and it's currently unowned.

---

## Slide 12: Discussion
**Type:** Discussion

**Three questions for your reaction:**

1. We've proposed that the agent handles the 70% of standard-path contracts fully autonomously — Tom receives a notification but doesn't review the classification unless he chooses to. Does that level of autonomy feel appropriate from day one, or would you want Tom to spot-check every agent classification for an initial period before the autonomous path goes live?

2. The system is designed so that no counteroffer can leave Legal's queue without a named lawyer's approval token recorded in Ironclad — that's an architectural rule, not a workflow suggestion. Does sign-off currently happen in Ironclad as a field action, or would formalising it there require a change to how the team currently works?

3. The DPDI Act playbook update is on the critical path for the agent handling DPA clauses. Who is the right person to own that update, and is a completion date achievable within the deployment planning window?

**Speaker notes:**
I've deliberately chosen these three because they represent tensions in the design that we can't resolve without your input. The first is about trust calibration — how much autonomous operation is Amelia comfortable with before there's a measured accuracy track record? The second is about whether the governance gate we've designed maps onto the current operational reality or requires a process change. The third is the practical blocker: without an owner and a date on the DPDI Act update, the DPA portion of the agent is indefinitely stalled, and that affects the coverage numbers we can commit to.

---

## Slide 13: Next Steps
**Type:** Content

| Action | Owner | Dependency | Target date |
|---|---|---|---|
| Confirm Ironclad custom field support: can the system be configured with ~35 per-clause classification fields across 7 clause types? | Ironclad admin | Ironclad admin access; field schema review | *[Placeholder]* |
| Name an owner and agree a target completion date for the DPDI Act playbook update — this is the deployment gate for DPA clause handling | Amelia (GC) | Internal decision | *[Placeholder]* |
| Confirm the HITL review channel: how should the agent deliver flagged contracts to Tom — Ironclad workflow, Outlook inbox, or a separate queue? | FDE team + Tom | Tom's workflow preference; Ironclad or Outlook API access | *[Placeholder]* |
| Provide 20–30 historical vendor contracts from Ironclad for clause heading pattern analysis — enables the agent to locate clauses reliably across varied document structures | Legal team | Access to Ironclad case archive | *[Placeholder]* |

*Actions 1 and 3 are blocking: build specification cannot be finalised without them. Action 2 is a deployment gate. Action 4 improves accuracy before go-live but does not block the build. [D5 G-1, G-2, G-3, G-4; D6 Q7, Q16]*

**Speaker notes:**
These four actions are all that stands between where we are today and a finalised build specification. Two of them — the Ironclad field confirmation and the HITL channel decision — are technical questions with a clear owner and a one-week resolution path. The DPDI update is the one that requires Amelia's decision about ownership and timeline; without it, we're committing to a build that excludes DPA clause automation indefinitely. The historical contracts request is the fastest path to improving the agent's clause location accuracy before launch — it's a one-time data exercise, not an ongoing commitment.

---

## Slide 14: Closing
**Type:** Closing

**Recommendation:** First-pass clause classification is a strong candidate for automation — with a projected 17-month payback, 125 hours of paralegal time recovered per quarter, and a design that preserves the named-lawyer sign-off requirement by architectural constraint, not policy assumption.

---

*[Contact details placeholder]*
*[Next meeting / follow-up date placeholder]*

**Speaker notes:**
To close: the case for building this agent is solid, conditional. The volume is there, the pattern is there, and the economics close. What makes this different from a generic AI implementation is the governance design — the sign-off gate is not a prompt or a policy, it's a system-level constraint that the agent cannot override. That's the answer to the accountability question. What we need from you today — or within the next week — are the five answers from slide 11. With those, we can finalise the specification and move to build. Without them, we're building assumptions into a design that should be built on facts.
