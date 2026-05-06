# Discovery Questions — MiniBase Community Moderation

Questions whose answers would change a specific design decision. Every question traces to a TBD, [Assumed] tag, or MISSING item in deliverables 1–5. Questions that wouldn't change the design regardless of answer have been removed.

---

> **Q1: What is the acceptable time limit for a case sitting in the WS2 moderator queue without a decision — and who is responsible when that limit is breached?**
> **Affects:** APD Escalation Triggers — three TBD SLAs: (a) Discord consensus deadlock timeout, (b) brief assembly timeout, (c) moderator inaction timeout. CLM WS2 Breakpoints (stakeholders_quiz Q4: no SLA currently defined).
> **If answer is a defined time limit (e.g. 30 min):** all three APD escalation triggers can be set to numeric values and are fully buildable. Senior Moderator becomes a named, operational role with a queue.
> **If answer is "we don't want a time limit":** escalation trigger cannot be automated; the stakeholders_quiz Q4 failure mode (volunteers debate indefinitely, Tom finds out at appeal stage) is preserved by design. The agent can surface case age as a signal in the brief, but cannot auto-escalate. This is an explicit design choice that must be documented.

---

> **Q2: Does a structured mapping between Discourse user IDs and Stripe customer IDs exist — or can one be created before go-live?**
> **Affects:** APD Scope (Tier 3 detection assumption, low confidence); SDI GAP-2 (quality blocker for Tier 3 detection).
> **If yes (mapping exists or can be built):** Stripe tier lookup is buildable in v1; agent brief includes a reliable Tier 3 commercial flag for all non-Sheet accounts. SDI GAP-2 closes.
> **If no:** Stripe tier lookup is removed from v1 scope; APD Tier 3 detection degrades to "moderator recognises the account" — the undocumented process the agent was meant to surface. The APD failure mode #5 handling remains as the permanent mitigation. A structured Tier 3 source becomes a post-go-live requirement if the community trust risk from missed Tier 3 accounts is unacceptable to Tom.

---

> **Q3: The sub-forum norms you've built up over time — Painters, Historical, Japanese painters sub — are clearly load-bearing for moderation quality. How do you see those being made available to the system, and is that something you'd want in place from day one?**
> **Affects:** APD Scope (sub-forum norm retrieval assumption, medium confidence); SDI GAP-1 (quality blocker for norm-sensitive sub-forums); CLM WS2 step 4 Tool Availability = Low.
> **If available from day one:** norm-aware triage is a v1 capability. The structured source must cover at minimum the three confirmed sub-forums. Agent brief quality for norm-sensitive cases reaches full design intent.
> **If not available at launch:** agent flags "norm not found — global policy applied" on all norm-sensitive cases at launch — the most common source of community trust damage in the grey-zone queue. SDI GAP-1 remains a quality blocker until resolved. Follow-up: are there other sub-forums with divergent norms beyond the three we've identified?

---

> **Q4: When you're assessing an IP claim, you clearly have a feel for which claimants are credible and which aren't — @sculpturedragon versus @vintage_kitbasher being a good example. Is that judgment something you'd want to try to write down at some point, even informally, or does it feel too context-dependent to capture?**
> **Affects:** CLM WS4 JTBD Key systems (stakeholders_quiz Q3: medium confidence); DSM WS4 Human-only archetype assignment; SDI (no structured credibility tool noted).
> **If yes (willing to document, even informally):** WS4 archetype can be revisited once heuristics are formalised. A structured credibility guide is the minimum required before any partial automation of WS4 steps 4–6. Long-term opportunity, not a v1 item.
> **If no (too context-dependent to capture):** WS4 remains Human-only. The platform's IP claim capacity stays tied to Tom's personal availability, which becomes a risk as claim volume grows.

---

> **Q5: When a new sponsor comes on board, how does their account get added to your tracking sheet — is that part of the onboarding process, or something you catch up on separately?**
> **Affects:** APD Failure Mode #1 (Sheet staleness = 2024 incident risk); SDI Tom's Google Sheet row (staleness risk noted); CLM WS1 step 4 Compliance/Risk = High.
> **If it's part of onboarding (account added before the sponsor starts posting):** staleness risk is low; the agent can rely on the Sheet with a short cache refresh cycle. The 2024 incident risk is structurally mitigated.
> **If it's caught up on separately:** the agent needs a safety net — flagging accounts that show commercial signals but aren't in the Sheet yet, for Tom to review before any automated action. Without this, the system reproduces the 2024 incident at higher volume.

---

> **Q6: For the long-standing community members who've become small commercial operators — the ones who get a bit more latitude informally — is there anywhere that list currently lives, even informally? And if not, is that something you'd want to maintain going forward?**
> **Affects:** CLM WS1 step 4 and WS2 step 2 (Tier 3 not in any structured source, [Assumed: medium confidence — stakeholders_quiz Q5]); DSM WS2 delegation boundary (agent cannot screen for Tier 3 without structured data); APD failure mode #5.
> **If a list already exists (in any form):** confirm the source, access method, and ownership. Tier 3 detection may be buildable in v1 with minimal new infrastructure — this significantly upgrades brief quality for commercial-member cases.
> **If no list exists and Tom is willing to maintain one:** Tier 3 detection becomes reliable once the list is created and kept current. The three-tier model becomes fully machine-readable. Highest-value data infrastructure investment for the moderation system.
> **If no list exists and Tom is not willing to maintain one:** the agent permanently relies on Stripe tier as an imperfect proxy. Moderators apply Tier 3 caution manually when the commercial flag is present. The gap between documented and lived process in this area remains unresolved.
