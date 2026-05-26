# Gate 5a — Capstone Participant Pack (Design + Build)

**Gate:** Gate 5a (Week 5, Virtual Monday–Thursday) — the full FDE arc on one sealed problem, ending in a working prototype you defend live.
**Pack release:** Virtual Monday Week 5, start of week — released alongside the sealed scenario pack for the capstone option you chose and got approved at Gate 4. Read this pack end-to-end before you start designing.
**Design phase:** Virtual Monday–Tuesday. Design package (Deliverables #1–#11) due **end of Virtual Tuesday**.
**Build phase:** Virtual Wednesday–Thursday morning. Working prototype (Deliverable #12) due **Virtual Thursday afternoon**, before your defense slot.
**Capstone defense:** Virtual Thursday afternoon — **20 minutes per participant** (5-min live demo + 10-min coach Q&A + 5-min graded curveball). Coaches run defenses in parallel; your coach team confirms your slot.

> **The big shift this week:** Weeks 1–4 graded *documents*. Gate 5a grades *running code*. This is the first gate where "it runs" matters — the automatic-fail list below includes "prototype doesn't run at all." Your design has to survive contact with a real build.

---

## 1. What Gate 5a is testing

Weeks 1–4 tested the pieces: scope and spec an engagement (Week 1), assess and design agents (Week 2), execute and defend a build (Week 3), reason about economics and govern quality (Week 4). The Capstone asks you to do **all of it on one problem, end to end, and then prove the spec you wrote is actually buildable by building it.**

The question shifts from *"can you write a buildable spec?"* to:

- Can you design an **AI-native** solution — agents making real decisions, with justified delegation boundaries — not a rules engine wearing an AI label?
- Can you produce **production-grade specifications** that an AI coding agent can build from with few or no clarifying questions?
- Can you **build a working prototype** of your own design with Claude Code and mock data — happy path, a failure-mode escalation, and at least one edge case, all running?
- Can you **defend the gap between demo and production** honestly, and adapt your design on your feet when a curveball lands?

What distinguishes Gate 5a from earlier gates:

- **Four days, design then build.** Design compresses to Mon–Tue (you've run the design arc twice already — Weeks 2 and 4); the build gets Wed–Thu because it's the first sustained "build what you yourself designed from nothing" exercise in the program.
- **A working prototype is graded.** 20% of the rubric is the prototype (correctness + live demo). A prototype that doesn't run is an automatic fail regardless of how good the design is.
- **The curveball is graded.** Unlike Gate 4's 2-minute *rehearsal*, the Capstone's 5-minute curveball counts.
- **The rubric is visible.** Gate 5a is the one gate where you get the full rubric up front (released Monday) — the 4-day format makes it valuable to design and build against the criteria. See §6.

---

## 2. The week's choreography

> **If you're on the v4.2-Accel overlay:** your Week 5 calendar may differ — follow your overlay's `Participants/Week5/README.md` for the canonical Accel timing. The deliverables (§3), the working-prototype requirement (§4), the defense format (§5), and the scoring logic (§6) below all apply to you unchanged; only the day-by-day timing may shift.

| Virtual day | What | Who |
|---|---|---|
| **Monday** | Sealed scenario pack released for your chosen option (A/B/C). Capstone **rubric shared** (§6). Supplementary materials — stakeholder tensions + mock-data context — arrive. **Begin design.** | You + coach team |
| **Tuesday** | Finish the design package — capability specs, ADRs, economics, stakeholder memo, `CLAUDE.md`. **Submit Deliverables #1–#11 by end of Virtual Tuesday.** | You (solo) |
| **Wednesday (morning)** | **Build starts.** Build the prototype with Claude Code + mock data. **Happy path first.** | You (solo) |
| **Wednesday (afternoon)** | **Per-squad coach prototype checkpoint (30–45 min).** Coach reviews in-progress prototypes live — *"is the agent doing something useful, or is it an if-else tree wearing a hat?"* Not graded. | Coach + your squad |
| **Thursday (morning)** | Finish the prototype: failure-mode escalation working, at least one edge case handled, demo rehearsed end-to-end. | You (solo) |
| **Thursday (afternoon)** | **20-minute Capstone defense** — live demo + Q&A + graded curveball. Submit the prototype before your slot. | You + coach |
| **Friday** | **Final Exam (Gate 5b)** — separate 8-hour solo gate. See `../Reference/final-exam-rules.md`. | You (solo) |

**Why the Wednesday checkpoint matters — and what it isn't.** It is a *coach-visibility* moment, not a graded one. Bring whatever runs. The coach is checking one thing: is the prototype demonstrating *agentic* behaviour, or has it drifted into procedural rules-engine code? If your happy path isn't working by Wednesday afternoon, that's the signal to **cut scope** — a working happy path + working escalation + one edge case beats an ambitious half-built system. Cutting the second edge case Wednesday is the right call, not a failure.

**Note on the week's start day:** Week 5 starts on a physical Tuesday or Wednesday depending on how the schedule absorbed the Week 4 holiday shift. Your coach team confirms the exact physical date for each Virtual day in Teams General at the start of the week.

---

## 3. The deliverable package (12 deliverables)

Submit as a single project folder. Markdown for the design deliverables; a runnable Claude Code project for the prototype.

### Design deliverables (#1–#11) — due end of Virtual Tuesday

| # | Deliverable | Filename suggestion | What strong looks like |
|---|---|---|---|
| 1 | **Problem framing & success metrics** | `01-problem-framing.md` | User, business, and operational perspectives. Success metrics are numeric and measurable (turnaround, completeness, escalation precision, cost-per-case) — not adjectives. |
| 2 | **Cognitive Load Map** | `02-cognitive-load-map.md` | The primary work stream's zones, breakpoints, and micro-tasks — reflecting the *lived* process, not the org chart. |
| 3 | **Delegation Suitability Matrix** | `03-delegation-matrix.md` | Each task assigned an archetype; agent-vs-human boundaries specific and defensible. Names the decisions the agent *makes*, not just steps it executes. |
| 4 | **Agent Purpose Document(s)** | `04-agent-purpose.md` | Purpose, scope, autonomy matrix, escalation triggers. Would survive scrutiny from a builder. |
| 5 | **Architecture Decision Records (3+)** | `05-adrs.md` | Each ADR has trade-off analysis with rejected alternatives, not just an asserted choice. |
| 6 | **Two production-grade capability specifications** | `06-capability-specs.md` | Buildable by an AI coding agent with few/no clarifying questions. Your prototype (Deliverable #12) is the evidence these specs are buildable. |
| 7 | **Integration specifications** | `07-integration-specs.md` | Systems, data contracts, auth, failure handling for the integration points your flow touches (mocked for the prototype). |
| 8 | **Token economics model with sensitivity analysis** | `08-economics.md` | Realistic token costs from public pricing; ROI positive under conservative assumptions; multi-model routing justified (Haiku/Sonnet/Opus — see §8). |
| 9 | **Validation plan** | `09-validation-plan.md` | Covers accuracy, cost, edge cases, failure modes, compliance — not happy-path only. |
| 10 | **Stakeholder alignment memo** | `10-stakeholder-memo.md` | Names the real tension in your scenario (see `../Reference/capstone-stakeholder-tensions.md`) and proposes a defensible trade-off. Don't sidestep or strawman a stakeholder. |
| 11 | **`CLAUDE.md` and project configuration** | `CLAUDE.md` | The project config your prototype build runs against — instantiated for this scenario, not boilerplate. |

### Build deliverable (#12) — due Virtual Thursday afternoon

| # | Deliverable | Location | What strong looks like |
|---|---|---|---|
| 12 | **Working prototype** | `prototype/` (runnable Claude Code project) | See §4. One primary agentic flow + one failure-mode escalation + one edge case, all running on **mock data**, with tests covering all three paths and a demo script that runs them in sequence in under 5 minutes. |

**The prototype does not need to implement every flow in your design.** The skill being tested is *"your spec is buildable,"* not *"you can build everything in one week."* Cut scope honestly during the build if the happy path isn't working yet.

**Known gaps beat hidden gaps.** If the build exposes a gap your design missed, name it — a spec amendment note alongside the prototype is honoured, not penalised. A prototype that silently diverges from your spec is a faithfulness failure (see §6 automatic-fails).

---

## 3.1 Design phase vs build phase

| Phase | Days | Submitted | What it is |
|---|---|---|---|
| **Design** | Mon–Tue | End of Virtual Tuesday | Deliverables #1–#11. This is the spec your build runs against. |
| **Build** | Wed–Thu morning | Virtual Thursday afternoon, before your defense | Deliverable #12 — the working prototype, built from your own design. |

The design submission is the spec of record. The Wednesday checkpoint reads your in-progress build against it. The final grade reads your Thursday prototype + the design package + your live defense together. **Faithfulness between the two is graded** — no silent scope creep, no silent scope reduction.

---

## 4. The working prototype (Deliverable #12) — what "it runs" means

The prototype is a **demonstration that your spec is buildable**, not a production system. It must include, all running on mock data:

1. **One primary agentic flow, end-to-end.** The agent makes the load-bearing decision your design centres on — routing, judging, classifying, resolving — not just executing a fixed procedure.
2. **One failure-mode escalation that fires correctly.** A reachable code path where the agent decides *"I can't handle this — escalate to a human"* and does so. It must actually fire in the demo, not be aspirational.
3. **At least one edge case handled.** A non-happy-path input the design anticipated, handled as designed.
4. **Tests covering all three paths** — happy path, escalation, edge case.
5. **A demo script** that runs the three paths in sequence in **under 5 minutes**, so the coach can watch the whole thing live.

**Mock data is required** — the program has no client data, and you generate or use the mock data in your scenario pack. **The prototype must be genuinely agentic.** A traditional rules engine with an AI label is an automatic fail (§6), even if it runs cleanly.

---

## 5. The 20-minute capstone defense

Thursday afternoon, individual slots, run in parallel across coaches.

| Time | Activity |
|---|---|
| 0:00–5:00 | **Live demo (5 min).** Run the happy path, the failure-mode escalation, and the edge case in sequence, explaining what the agent is doing and why at each step. **This is a live demo, not a narrated slide deck.** Narrating slides instead of running code is marked down on demo quality regardless of whether the prototype works — and counts toward the automatic-fail. |
| 5:00–15:00 | **Coach Q&A (10 min).** Expect questions on problem framing, delegation design, economics, spec quality, stakeholder management, and the key probe: *"what would break this in production that the prototype doesn't show?"* Name the demo-vs-production gap honestly — that scores higher than pretending the prototype is production-ready. |
| 15:00–20:00 | **Curveball (5 min) — GRADED.** The coach introduces a significant new constraint (a regulatory ban, a volume spike, a deadline compression, a PII flag, a competitor-parity demand, a stakeholder reveal). You respond in real time — both verbally and by naming what in the prototype and/or design would have to change. Graded on **composure and specificity**, not on solving it perfectly in 5 minutes. |

**This curveball counts.** Gate 4 gave you a 2-minute *rehearsal* of this format precisely so it would be familiar here, where it's graded. The response shape that works: (a) name the assumption the constraint breaks, (b) name the part of the design/prototype that adapts, (c) name the new trade-off. Five minutes isn't enough to redesign — it's enough to show you can think clearly about your own system under pressure.

---

## 6. Scoring — the rubric, and the fact that you can see it

Gate 5a is **the one gate in the program where you get the full rubric up front.** It is released at the start of Virtual Monday so you can design and build against it. (Gates 1–4 keep the rubric sealed; the Final Exam rubric is sealed until Friday 09:00.) The criteria, weights, and pass threshold are reproduced here for your reference.

**Pass: 78+ overall, with no criterion scoring below 60%.**

| Criterion | Weight |
|---|---:|
| Solution is AI-native with justified delegation architecture | 15% |
| Specifications are production-grade (buildable by an AI coding agent) | 15% |
| Economics model is credible and the business case closes | 15% |
| Cognitive work assessment reflects lived process, not documentation | 5% |
| Architecture decisions show sound judgment | 5% |
| Stakeholder alignment shows professional judgment | 5% |
| Scope discipline | 5% |
| Validation plan is comprehensive | 5% |
| **Working prototype: correctness and faithfulness to spec** | **15%** |
| **Live demo quality** | **5%** |
| Verbal defense quality (Q&A + curveball) | 10% |

**Automatic fail indicators (any one fails the gate regardless of score):**

- Built a traditional rules engine instead of an agentic solution
- Failed to distinguish what should be agentic from what should stay human
- **Prototype doesn't run at all** during the live demo
- Narrated slides instead of demoing running code
- Validation is happy-path only with no failure-mode coverage

Use the rubric the way you'd use a client's acceptance criteria: as a checklist of what "done and defensible" looks like, not as something to game. The 20% on the prototype + the agentic automatic-fail are the program's way of saying: a beautiful design that doesn't build, or that builds into procedural code, is not the FDE skill.

---

## 7. How to run the four days

A rough shape that has worked; adapt as you like.

- **Monday — design, half 1.** Read the sealed scenario pack and the stakeholder tensions end-to-end before writing anything. Then: problem framing + success metrics (#1), cognitive load map (#2), delegation matrix (#3). Decide your *one primary agentic flow* now — it's what you'll build Wed–Thu, so choose something bounded.
- **Tuesday — design, half 2.** Agent Purpose Doc (#4), ADRs (#5), the two capability specs (#6) — write these as if a builder you'll never meet has to build from them, because tomorrow that builder is Claude Code. Then integration specs (#7), economics (#8), validation plan (#9), stakeholder memo (#10), `CLAUDE.md` (#11). **Submit the design package by end of day.**
- **Wednesday morning — build the happy path.** Stand up the project against your `CLAUDE.md`. Get the one primary agentic flow running on mock data before you touch anything else. Resist building breadth — depth on the happy path first.
- **Wednesday afternoon — checkpoint.** Bring what runs. Take the coach's one-minimum-change steer. If the happy path isn't working, cut scope here.
- **Thursday morning — escalation + edge case + tests + demo.** Make the failure-mode escalation actually fire. Handle one edge case. Write tests for all three paths. Write and rehearse the under-5-minute demo script. If you discover a spec gap, write the amendment note.
- **Thursday afternoon — defend.** Demo live, answer honestly, take the curveball with composure.

**The thing not to skimp on is the running prototype.** A polished design package cannot rescue a prototype that doesn't run — that's an automatic fail. A working happy path + working escalation + one edge case, faithful to a clear spec, is the spine of a passing gate.

---

## 8. Multi-model experimentation note (carried from Week 4)

Your economics model (#8) should reason about *when* to use which model, not default to Opus. Tools that expose multiple models without changing your primary Claude Code build workflow:

- **Dial** (`https://chat.lab.epam.com/`) — EPAM's multi-provider chat gateway.
- **Cursor** (optional) — multi-model chat/agent support.
- **GitHub Copilot** (optional, via EPAM Leap) — multi-model selection.

Use them to validate which step in your agent's flow actually needs Opus versus Sonnet versus Haiku (or a cross-provider alternative). A defensible routing decision — "classification runs on Haiku, the high-stakes determination on Sonnet, nothing needs Opus" with the cost delta named — is a stronger economic case than assuming one model for everything. **(Note: the Final Exam on Friday is Claude Code only — these multi-model tools are for capstone economics reasoning, not for the exam build.)**

---

## 9. Cross-references

| File | Use |
|---|---|
| `README.md` | Week 5 calendar and broader framing (both gates) |
| `Capstone-A-Claims-Pack/README.md` | Sealed scenario pack + mock data — Option A (Healthcare Claims) |
| `Capstone-B-Procurement-Pack/README.md` | Sealed scenario pack + mock data — Option B (Enterprise Procurement) |
| `Capstone-C-CustomerResolution-Pack/README.md` | Sealed scenario pack + mock data — Option C (Multi-Channel Customer Resolution) |
| `../Reference/capstone-scenario-options.md` | The three options recap + deliverable package + defense format |
| `../Reference/capstone-stakeholder-tensions.md` | The stakeholder conflict per scenario — the basis for your alignment memo (#10) |
| `../Reference/final-exam-rules.md` | Friday's Final Exam (Gate 5b) rules — read before Friday |
| `../Reference/production-spec-checklist.md` | Cross-check your capability specs (#6) for buildability |
| `../Reference/integration-spec-template.md` | Template for your integration specs (#7) |
| `../Reference/claude-md-examples-guide.md` | `CLAUDE.md` examples and failure modes (#11) |
| `../Reference/atx/atx-economics.md` | ATX economics framework for the economics model (#8) |

---

*Released Virtual Monday Week 5, alongside your chosen scenario's sealed pack. The Capstone rubric (§6) is shared the same morning — the one gate where you see it up front.*
