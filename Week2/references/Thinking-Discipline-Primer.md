
## The one thing to internalise

That shifts the bar. You're judged on two things: the **quality of the artefacts** you produce (the deliverables list) **and the honesty of the reasoning** behind them. Every non-trivial claim in your problem statement, delegation analysis, agent spec, and validation design is either (a) tested through a coach role-play, (b) derived from something you can reasonably cite, or (c) assumed — and in that case, you say so, loudly, in writing.

**Hidden assumptions are the failure mode. Stated assumptions are discovery.** An assumption log at the top of your doc is not overhead; it is what turns a plausible-sounding spec into a reviewable one.

---

## How to show your thinking

For every non-trivial claim, use this shape:

> **Assumption:** [what you're taking as given]
> **Hypothesis:** If [X is true], then [Y will happen], because [reasoning].
> **How I'd test it:** [the coach session, prototype, or data probe that would confirm/refute]
> **Confidence:** low / medium / high — and why.

A reviewer should be able to scan your assumption log and immediately see where your reasoning is load-bearing.

---

## Cagan's four risks as a pressure-test lens

Cagan's four risks aren't the scoring spine of Gate 1 — the five deliverables are. But they're a useful lens for pressure-testing what you've produced before you hand it in.

- **Value risk** — does the customer actually care about this problem, and does the agent solve it in a way they'd pay for? Pressure-tests your *problem statement* and *success metrics*.
- **Usability risk** — can the people interacting with the agent (inputs, handoffs, escalations) figure out how to work with it? Pressure-tests your *delegation analysis* and *validation design*.
- **Feasibility risk** — is the spec precise enough that an AI coding agent can actually build from it? Pressure-tests your *agent specification*, and it's the risk your **closed build loop** is designed to attack directly.
- **Viability risk** — does it work for the business (compliance, procurement, handoffs with humans still in the loop)? Pressure-tests your *assumptions & unknowns* and your *delegation boundaries*.

You can't fully resolve any of these in Week 1 without real users. That's fine. The goal is to name which risks each artefact is attacking, and be explicit about what's still assumed.

---

## Where thinking-discipline shows up in each Gate 1 deliverable

- **Problem statement & success metrics** — every hedged claim is lifted into the assumption log with a hypothesis and a test. *Good:* a reviewer sees exactly where your confidence is load-bearing. *Bad:* prose that sounds confident but quietly rests on three untested premises.
- **Delegation analysis** — each boundary (fully agentic / agent-led / human-led / human only) is justified with *why*, not just *what*. *Good:* you've named what makes a task safe to delegate fully, and what tacit knowledge or accountability keeps a task human-led. *Bad:* arbitrary splits you couldn't defend against a coach's "why there?"
- **Agent specification** — precise enough that an AI coding agent wouldn't need to ask a clarifying question. Your closed build loop against Claude Code is how you test this directly. Every time the builder produces something unintended, you classify it: spec ambiguity (you own the fix), builder misread (the builder owns the fix), or unjustified addition (ask for rollback).
- **Validation design** — you've named what "working" looks like in testable terms and what the most likely failure modes are. *Good:* failure modes tied to specific decisions in the spec. *Bad:* "we'll write tests" without specifying what behaviour they'd defend.
- **Assumptions & unknowns** — at least 5 genuine unknowns, not filler. "I don't know" beats a plausible-sounding guess.

---

## Anti-patterns to catch yourself on

- Hand-waving verbs. "Handles claims triage, routes intelligently, manages exceptions" — with no inputs, outputs, or decision logic behind the verbs.
- Implicit state. References to a claim being "validated", "routed", "acknowledged" without defining what creates, invalidates, or checks that state.
- Integration hand-wave. "Integrates with CRM / policy admin / DMS" without naming endpoint, auth, request/response shape, timeout, retry, or fallback. (A named scope-out with a plan is fine — a silent omission is not.)
- Generic problem framing. A problem statement that could have been written without reading the scenario — no mention of the 300/day volume, the 22-minute handling time, the 18% routing error, the 31% SLA breach, the SOAP legacy, or the claimant perspective.
- Vanishing claimant. Framing the problem purely from the insurance company's efficiency perspective. The scenario distinguishes claimant from customer, and the claimant perspective is part of the problem.
- Filler assumptions. Assumptions lists that are platitudes ("We assume the client has good data") with no specific testable claim.
- Bluffing. Confident-sounding claims about systems, data, or constraints the scenario did not state — and the participant did not mark as an assumption. (If the scenario says SOAP endpoints and you design around REST, that is an assumption. Name it.)


---

## Self-check before Friday

- Is my assumption log visible, numbered, and honest about confidence?
- For each major claim across my five Gate 1 deliverables, can I point to either a test, a source, or an explicit assumption?
- Did I use my coach sessions to move specific hypotheses, not just to chat?
- Did I complete the closed build loop against Claude Code — and can I diagnose the gap between what I asked for and what got built?
- Would a reviewer be able to challenge my thinking because I've exposed it, rather than in spite of hiding it?

Four yeses is a strong Week 1. Five is rare and earned.
