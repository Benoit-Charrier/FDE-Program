# Enriched Practice Scenarios — Week 1 Pool, Re-Usable for Week 2 ATX Practice

These scenarios extend the 7-scenario pool defined in `README-Participants-Week1-Scenarios.md` with Week 2-grade texture: named companies, multi-stream decomposition, volumes and handling times, tooling sketches, and named stakeholders. Each scenario can support a Cognitive Load Map, Delegation Suitability Matrix, Volume × Value analysis, Agent Purpose Document, and System/Data Inventory.

---

## A note on what this document contains — and what it deliberately doesn't

The brief below is your **starting context**. Like a real client engagement, the named stakeholder knows things this document doesn't tell you. **Eliciting what's not in the brief is the Week 2 skill.** This document gives you enough to start; it deliberately does not give you everything you need to finish.

Each scenario also includes **3 sample artefacts** — fragments of how the work actually happens (calls, emails, system extracts, sticky-note margins). They exist so your "lived work" claims are grounded in evidence rather than narration. Mine them.

### How elicitation actually happens during Week 2

Coaches cannot run 1:1 30-minute role-play sessions with every participant for every scenario — that would be ~6+ hours per coach for one round of one scenario. Elicitation is therefore multi-channel:

1. **AI as your primary stakeholder proxy.** Feed the scenario brief below into Claude / Dial / Cursor with a prompt like: *"You are [stakeholder name]. Role-play in character given **only** the information in this brief. Do not volunteer information you weren't asked about. Hedge or change topic if a question would force you to invent. Push back on generic questions."* This is your unlimited practice surface. The AI's hedging, non-answers, and generic deflections are real elicitation pressure — they're how a partial-information stakeholder behaves under questioning. Sharpen your questions until the AI gives you signal.

2. **Coach during the Wednesday squad mid-week checkpoint** (~30–45 min per squad). Your coach plays the stakeholder for the squad. Each participant gets to ask 1–2 questions; the squad listens to all questions. Bring questions you could not crack with the AI alone. The coach has access to deeper context than the brief reveals — they reveal it selectively in response to sharp questions.

3. **Coach office hours** (shared, ~1 hour per week). Borderline cases and design-impacting unknowns. Office hours are scarce; don't burn them on questions answerable by AI.

The scarce coach resource (channels 2 and 3) reveals what the AI can't — the deeper layer of stakeholder context that lives in coach-only material. **Use AI for breadth; use coach time for depth on questions that surface from your AI practice.**

If you find yourself producing a Cognitive Load Map purely from the brief without referencing artefacts or elicited material from any channel, you are skipping the work.

---

## What Gate 2 signals these scenarios practice

Gate 2 grades seven deliverables. These enriched scenarios give you practice surface for five of them directly, and for two judgment signals that determine pass/fail at the margin.

| Gate 2 deliverable / signal | How these scenarios support practice |
|---|---|
| Cognitive Load Map | Work-stream decomposition + artefacts give you raw material to decompose. |
| Delegation Suitability Matrix | Lived-vs-documented tensions in the artefacts force defensible delegation reasoning. |
| Volume × Value Analysis | Volumes and handling times in the brief give you the V × V data. |
| Agent Purpose Document | Stakeholder context + system constraints shape the agent's purpose and autonomy boundaries. |
| System/Data Inventory | Tooling sketch + artefact-level system references (filenames, batch windows, manual workarounds) give the inventory's substance. |
| **Discovery Questions (#6)** | The "What you're expected to elicit" list in each scenario is the **seed** for your Discovery Questions deliverable. Your job is to shape those seeds into questions whose answers would *materially change your design* — that's the Gate 2 quality bar, not restating the seeds. |
| **Assumptions discipline** | The brief and artefacts are partial by design. Every inference you make — about volumes the brief doesn't state, stakeholder priorities not yet surfaced through coach role-play, system behaviours implied by an artefact — is an assumption. **Mark each as one, with explicit confidence levels.** Unmarked inferences read as bluffing. |
| CLAUDE.md | Workflow-level, not scenario-specific. See `claude-md-examples-guide.md`. |

Discovery Question quality and Assumption honesty are two of the seven Gate 2 rubric criteria — and the two where domain-naïve participants most often distinguish themselves. But they are **two of seven, not the whole rubric.** The Gate 2 rubric also weights the **professional quality of your deliverables** (clarity, organisation, readability) and **evidence of effective AI use across the week** (your CLAUDE.md, your build-loop diagnosis, your iterative refinement, the trail of how you got from blank page to submission). Strong work across all dimensions wins the gate; over-investing in two of them while neglecting the others doesn't compensate.

---

## Scenario 1 (enriched) — HR Onboarding Coordination

*Original brief in `README-Participants-Week1-Scenarios.md` § Scenario 1.*

### The company

**Aldridge & Sykes** — Manchester-headquartered regional professional services firm (UK). 1,200 employees across audit, tax, and consulting; offices in Manchester, Leeds, Birmingham, and a small Dublin team. ~85% FTE, ~15% contractors / secondments / rehires. 220+ hires/year, with strong growth in the consulting division.

### The function

3-person HR Ops team supporting all hires across the firm: an HR Ops Lead and 2 HR Coordinators.

### The four work streams

- **New-hire system & access setup** (~190/yr; effective handling ~3 hrs/case spread across 2 weeks). Workday record creation, IT requests, badge ordering, payroll setup, building access.
- **Compliance training assignment & tracking** (~220/yr; ~45 min/case for assignment plus chasing). Choosing the right LMS path based on role, country (UK vs Republic of Ireland), prior employment certifications.
- **Buddy matching & welcome cadence** (~220/yr; ~30 min initial + ~60 min across the first 30 days). Buddy assignment, 30-day check-in scheduling, welcome materials, manager handoff.
- **Edge-case resolution** (~30–50/yr; ~4 hrs/case but unpredictable). Late right-to-work checks (Home Office share-code / passport verification), expired visa work permits, missing reference checks, contractor-to-FTE conversions, rehires with frozen records.

### Tooling sketch

- **Workday** (core HR, modern, REST APIs available)
- **ServiceNow** (IT requests, robust auto-routing)
- **Saba LMS** (compliance training, no API)
- **SharePoint** (onboarding doc library)
- **Outlook** (most stakeholder communication)

### Stakeholder

**Priya Aggarwal**, HR Ops Lead. Recently asked by the CFO to "look at AI options" after onboarding delays surfaced as a complaint from the consulting division.

### What you're expected to elicit through the week

You do not have the full picture. Use your elicitation channels (AI proxy primarily; coach at squad checkpoint / office hours for what AI can't crack) to surface:

- What automation has been tried at Aldridge & Sykes before, and what happened?
- How does the team's actual practice differ from the documented onboarding SOP?
- What tools does Priya rely on that aren't in the system list above?
- What does she fear about an AI-driven approach?
- Where do contractors, secondments, and rehires fit in real practice — not just on paper?

### Sample artefacts

#### Artefact 1.1 — Email thread, delayed laptop

*Subject: RE: RE: RE: New consultant Tom Reeves — Day 5 with no laptop. Between Mike Tehrani (Consulting Director's PA) and Priya Aggarwal (HR Ops Lead). 5 messages over 5 days.*

**Day 1, 09:14 — Mike → Priya:**
> "Morning Priya — Tom Reeves started Monday, the senior consulting hire from the Deloitte poach. He's been here three days and hasn't received his laptop. Anyone in your team handling this? Mike."

**Day 1, 16:48 — Priya → Mike:**
> "Sorry Mike — checking now. ServiceNow ticket #INC-44102 is open, sitting with IT for hardware allocation. Will chase. P."

**Day 3, 11:02 — Mike → Priya:**
> "Hi Priya, status? It's Wednesday now, Tom's on a loaner from reception that security need back tomorrow. The director is not happy."

**Day 3, 15:30 — Priya → Mike:**
> "Reset the ticket priority and pinged IT directly. ServiceNow ETA tomorrow. Apologies for the delay — the consulting laptop spec changed last quarter and the auto-routing didn't pick it up."

**Day 5, 08:45 — Mike → Priya:**
> "Still nothing. The director has emailed the CFO. Please escalate."

#### Artefact 1.2 — Master Tracker excerpt

*Selected row from Priya's "Onboarding Master Tracker" (Excel, OneDrive). Some hidden columns un-hidden for this excerpt.*

| Hire | Start | Type | Workday status | Visible status | (hidden) Notes | (hidden) Risk flag | (hidden) Buddy override |
|---|---|---|---|---|---|---|---|
| Tom Reeves | 14.10 | FTE | Active | Pending IT — laptop | Director's hire from Deloitte; sensitive about onboarding speed | Amber — laptop ETA missed | Paired with Sarah J (peer level), not Anna (rule says senior pair) |
| Maria Costa | 14.10 | Contractor → FTE Q1 | Active (FTE record only) | On track | Originally contractor June; FTE conversion record didn't pull contractor compliance history | Green | Default rule |
| James O'Connor | 21.10 | Returning hire | Pending Workday reactivation | On hold | Was contractor 2022; old record frozen, IT thinks duplicate | Red — start delayed | n/a until live |

*Workday is the "system of record" but Priya updates the tracker first and refreshes Workday end-of-week.*

#### Artefact 1.3 — Compliance Training Routing Flowchart fragment

*From SharePoint > HR Ops > Onboarding > "Compliance Training Routing v4.2" (last revised October 2023).*

```
[Hire Type?] → [FTE]                    → Path A (Standard FTE Pack)
            → [Contractor]              → Path B (Reduced — see below)
            → [Secondment]              → Path C (Client-specific)

[Path B — Contractor]
  ├─ Role code = CONS-A,B,C  → assign 6-module compliance pack
  ├─ Role code = CONS-D       → assign 4-module compliance pack
  └─ Role code = TEMP-EXT     → no assignment (out of scope)
```

*Footnote pencilled on the printed copy on Priya's desk: "TEMP-EXT retired 2024-Q1 — these now route as CONS-D. Update flowchart sometime."*

---

## Scenario 2 (enriched) — Vendor Contract Clause Review

*Original brief in `README-Participants-Week1-Scenarios.md` § Scenario 2.*

### The company

**Helix Workforce Software** — UK-based mid-size B2B SaaS (London + Bristol offices, ~480 employees, ARR £42M, growing 25% YoY). Sells workforce-planning software to large UK and EU enterprises (banks, retailers, NHS trusts). Vendor contracts arrive at high volume from prospects and renewals because every customer's procurement team has its own paper.

### The function

5-person Legal & Commercial team: General Counsel, 3 Commercial Lawyers (mid-level, 3–6 yrs), 1 Paralegal (Tom).

### The four work streams

- **First-pass clause classification** (~300 contracts/quarter; ~25 min/case). Triaging an inbound contract, classifying each major clause against the playbook (liability cap / DPA / termination / IP / SLA / governing law / indemnity).
- **Standard-deviation redlining** (~60/quarter; ~45 min/case). Negotiable deviations the paralegal can redline against the playbook without escalation.
- **Escalated clause review** (~30/quarter; ~90 min/case). A senior lawyer reviews unusual clauses, frames a counteroffer position, drafts the redline.
- **Counteroffer drafting & sign-off** (~90/quarter; ~30 min/case). Drafting the response to procurement, named-lawyer sign-off, sending out.

### Tooling sketch

- **Ironclad** (CLM, modern SaaS, REST APIs)
- **Microsoft Word + Track Changes** (where redlining happens) and **SharePoint** (storage)
- **Salesforce** (sales pipeline; procurement requests for new contracts come in here)
- **Outlook** (vendor procurement teams send their paper here)
- **Internal "playbook" SharePoint page** (position statements per clause type)

### Stakeholder

**Amelia Forsythe**, General Counsel, 12 years at Helix. Hard rule: no counteroffer leaves Legal's queue without a named lawyer's sign-off on the specific clauses being negotiated. The CRO is pressuring Legal to halve contract turnaround (currently 4–6 days) to support enterprise sales targets.

### What you're expected to elicit through the week

Use your elicitation channels (AI proxy primarily; coach at squad checkpoint / office hours for what AI can't crack) to surface:

- Why the named-lawyer-sign-off rule exists, and what specifically would break if it were relaxed.
- What recent regulatory changes (e.g., DPDI Act updates) are or aren't reflected in the playbook.
- How the paralegal actually triages cases day-to-day vs how the playbook describes triage.
- Where in the workflow shortcuts already exist that aren't in the SOP.
- What Amelia fears about AI-driven contract review — what specific failure mode would damage her position.

### Sample artefacts

#### Artefact 2.1 — Inbound clause excerpt with paralegal annotations

*Excerpts from a vendor MSA inbound from VendorCo Ltd (sales-tools procurement). Tom's margin notes captured during first-pass review.*

**Section 7.3 — Limitation of Liability**

> "Notwithstanding any other provision of this Agreement, neither party shall be liable to the other for any indirect, incidental, consequential, special, or punitive damages, regardless of the form of action, whether in contract, tort, or otherwise, even if advised of the possibility of such damages. The total aggregate liability of either party arising from this Agreement shall not exceed the lesser of (a) the fees paid by Customer in the six (6) months preceding the event giving rise to liability or (b) £50,000."

*[Tom's margin note: "Cap is below playbook minimum (12 months / £250k for enterprise). FLAG — but the term is borderline negotiable, not escalation. Will redline to playbook position."]*

**Section 11.2 — Data Processing Addendum**

> "The parties acknowledge that Customer's data may be processed in jurisdictions outside the United Kingdom. Vendor agrees to comply with applicable data protection laws including the UK GDPR and the Data Protection Act 2018."

*[Tom's margin note: "DPDI updates aren't reflected — playbook is stale on this. Honestly not sure if this needs escalation. Will ask Sarah."]*

**Section 14.1 — Termination for Convenience**

> "Either party may terminate this Agreement upon ninety (90) days' written notice without cause."

*[Tom's margin note: "Ours is 30 days for our paper, 90 for theirs. Routine — accept."]*

#### Artefact 2.2 — Vendor procurement insists on email-only redline

*Subject: VendorCo MSA — please return all redlines via this thread, our system can't accept SharePoint links.*

**Linda Carrington (VendorCo Procurement) → Tom Reilly (Helix Legal), Day 1:**
> "Hi Tom — sorry but our procurement workflow tool only accepts attachments via email. Please return the redlined Word doc as an attachment to this thread; do not send a SharePoint link as I won't be able to open it. We aim to turn around in-house review within 5 business days. Linda."

**Tom internal forwarding to Amelia, Day 1:**
> "FYI — VendorCo can't take our SharePoint link. I'll attach the redline directly. This is the third vendor this quarter who has the same issue; just flagging. Tom."

#### Artefact 2.3 — Playbook DPA section with sticky note

*From SharePoint > Legal > Contract Playbook > "Position Statements v3.4" (last revised 9 months ago).*

> **Section 12 — Data Processing Addendum (DPA)**
>
> **Position:** "We accept the standard UK GDPR / Data Protection Act 2018 DPA template provided in Annex C of this playbook. Vendors proposing materially different DPA terms should be redirected to Annex C; if they refuse, escalate to GC.
>
> **Standard clauses to verify:**
> - Sub-processor list disclosure
> - Data residency (UK/EEA preferred)
> - Breach notification SLA (≤72 hours)
> - SCC fallback clause for data leaving the UK"

*[Sticky note attached on the printed copy on Amelia's desk: "DPDI Act updates landed Q1 — need to add new sections re: legitimate interests test and data subject access changes. Talked about this with Sarah in March, never got round to it. — A."]*

---

## Scenario 3 (enriched) — Retail Returns Disposition

*Original brief in `README-Participants-Week1-Scenarios.md` § Scenario 3.*

### The company

**Heron Apparel** — UK-headquartered mid-size apparel retailer (Reading HQ). 60 stores across UK, Republic of Ireland, and the Netherlands, plus a direct online channel. ~£280M annual revenue, growing 8% YoY but with margin compression from rising return rates.

### The function

Central returns facility (Reading, single location, two shifts). 12 returns processors handle everything that comes back to the warehouse. **Lara Bekova** is the VP Operations who owns the function.

### The four work streams

- **Reason-code classification** (~4,500/wk inbound; ~3 min/item). Look at the return + customer's stated reason; classify into 5 codes (defective / didn't fit / changed mind / wrong item / suspected fraud).
- **Condition inspection** (~4,500/wk; ~2 min/item). Visual inspection: tags, signs of wear, damage.
- **Disposition routing** (~4,500/wk; ~1.5 min/item). Restock as new / discount to outlet / refurbish / donate / destroy.
- **Suspected-fraud workup** (~150/wk current — 40% of suspected-fraud cases caught; ~225/wk target; ~15 min/case). Cross-reference customer history, look at order patterns, decide whether to flag for the customer service team.

### Tooling sketch

- **NetSuite** (ERP + WMS, modern, REST APIs)
- **Shopify Plus** (online channel, REST APIs)
- **In-house "ReturnsPanel"** (Java backend, AWS, custom web app — what processors actually use at the bench)
- **Stripe Radar** (payment fraud signals, referenced manually for fraud workup)
- **SharePoint + Excel** (disposition policy docs)

### Stakeholder

**Lara Bekova**, VP Operations, 18 months in the role. Under direct margin pressure from the CFO (4% returns-cost recovery target over 12 months). Receptive to a phased AI approach with measurable savings per phase.

### What you're expected to elicit through the week

Use your elicitation channels (AI proxy primarily; coach at squad checkpoint / office hours for what AI can't crack) to surface:

- What automation projects have been tried at Heron, and what was learned from each?
- Where do processors apply tribal-knowledge overrides that aren't in the disposition policy?
- How does the suspected-fraud routing actually work in practice vs how the policy describes it?
- What constraints govern "destroy" disposition decisions — are there charity or sustainability angles?
- What would a phase-one AI deployment have to demonstrate before Lara would commit to phase two?

### Sample artefacts

#### Artefact 3.1 — ReturnsPanel processor session note

*Free-text "notes" field captured by processor Sam W. on a single returned item. Item arrived warehouse 14.10, processed 16.10.*

> "Item: Marsh Bay knit jumper, navy, M. Customer reason: defective. Order #SO-44712.
>
> Inspected: tag still on, no obvious damage. Marsh Bay always have seam issues at the shoulder so I checked there — yes, slight pull on the left shoulder where it joins the sleeve. Not visible at first glance. Customer right to return.
>
> Disposition: outlet (not new restock — Marsh Bay seam is structural, will reappear after one wash even if fixed). Have flagged customer's account in my fraud sheet — second Marsh Bay return from this customer in 6 weeks. Not fraud yet but watching.
>
> Sam"

#### Artefact 3.2 — Customer service ticket, disputed disposition

*Ticket #CST-9931, submitted via Heron's web form 21.10.*

> **Subject: Refund denied unfairly**
>
> "I returned a Heron Apparel coat (order SO-39988, returned 14.10) within the 30-day window. Tags attached. Used once. The disposition email today says 'restock denied due to condition; partial refund applied (£42 of £85 paid).' I was not informed there was a condition issue at point of return. I'd like to know specifically what the issue was and dispute the partial refund.
>
> J. Patel"

*[Internal flag attached by Heron Customer Service: "Processor was Sam W. — disposition note mentions 'slight wear on inner lining, hard to spot' but customer was not notified of the inspection finding before partial refund was applied. Lara, please advise — full refund and move on, or stand by Sam's call? Third one like this in two weeks."]*

#### Artefact 3.3 — Disposition policy with sticky note

*From SharePoint > Operations > Returns > "Disposition Policy v2.1" (last updated 18 months ago, March).*

> **Section 4 — Suspected Fraud Workup**
>
> "When a returns processor identifies a suspected-fraud case, route to the Fraud Review Queue (NetSuite custom queue 'FRAUD_PENDING'). The Fraud Review team will:
> 1. Cross-reference customer order history and prior returns
> 2. Apply the Fraud Screening Matrix (Appendix C)
> 3. Decide within 3 business days: confirm fraud, dismiss, or request more evidence."

*[Sticky note attached to the policy binder in Lara's office, in her handwriting: "Fraud Review team is one part-timer (Maya, Tue/Thu). 3-day SLA is fiction — actually 7–10 days. Matrix in Appendix C is from 2022, missing newer fraud patterns (multi-account same delivery address, etc.). Needs full revisit but no slack to do it. — L, June."]*

---

## Scenario 4 (enriched) — Community Content Moderation

*Original brief in `README-Participants-Week1-Scenarios.md` § Scenario 4.*

### The platform

**MiniBase** — UK-incorporated tabletop-miniature hobbyist community platform (~180K active users, mostly UK / Western Europe / North America, with smaller bases in Japan and Australia). 12K posts/day across 14 sub-forums plus a gallery section. Revenue ~£1.4M/yr from premium memberships, gallery commissions, and sponsored content from miniature manufacturers.

### The function

Hybrid moderation team: 8 volunteer moderators (US, UK, Germany, Australia, Japan — covering time zones) + 2 paid staff (the Community Manager and a Senior Moderator).

### The four work streams (queue + IP)

Of the ~12K daily posts, the community is largely self-regulating — most pass without any moderator attention. About **12.5% of posts (~1,500/day) enter the moderation queue** via user flags, automated detection, or moderator sampling.

- **Routine spam / clear-violation removal** (~1,080/day; ~30 sec/case; ~72% of the queue). Obvious spam, off-topic, miscategorised posts.
- **Grey-zone case review** (~360/day; ~5 min/case; ~24% of the queue, matching the original brief's "3% of all posts sit in genuine grey zones"). Hobbyist critique that reads harsh, commercial posts from long-standing community members, regional cultural-reference disputes, ambiguous self-promotion.
- **User dispute appeals** (~60/day; ~8 min/case; ~4% of the queue, fed by prior moderation actions).
- **IP-claim resolution** (~3–5/wk; ~30 min/case + escalation). Separate inbound channel — sculptors claiming copyright over user uploads, manufacturers asserting trademark on miniature designs.

*Total moderator effort ≈ 47 hours/day across the 10-person team; the team is at capacity.*

### Tooling sketch

- **Discourse** (forum platform, self-hosted on AWS, REST APIs)
- **In-house gallery** (Rails app, custom; limited API surface)
- **Stripe** (premium memberships and gallery commissions)
- **Discord** (volunteer moderator coordination)
- **Google Sheets** (Community Manager's tracker)
- **Email** (IP-claim correspondence; legal record-keeping)

### Stakeholder

**Tomasz "Tom" Włodarczyk**, Community Manager (paid, Warsaw-based, ex-volunteer moderator promoted). Brief from the founder: "False positives are survivable; one viral false negative is existential."

### What you're expected to elicit through the week

Use your elicitation channels (AI proxy primarily; coach at squad checkpoint / office hours for what AI can't crack) to surface:

- What previous moderation incidents have shaped Tom's risk tolerance?
- Where do sub-forum-specific norms diverge from the global 14-page policy?
- How are IP claims actually triaged in practice — by whom, against what criteria?
- Where do volunteer moderators disagree, and what happens when they do?
- What sponsorship / commercial dynamics constrain content decisions in ways the policy doesn't acknowledge?

### Sample artefacts

#### Artefact 4.1 — A grey-zone post

*Post in the "Painting Critique" sub-forum, 18.10. Reported by 4 users; queued for moderator review.*

**Original post by user @greenwingmolar in critique thread "Help me figure out what's wrong with my Imperial Knight":**
> "Honestly mate, your highlights are gone, your edges are blurry, the freehand is wonky, and the basing looks like you used cat litter without thinking about colour. The OSL is the only thing saving this from being a beginner Reddit post. If you're entering this in Golden Demon you'll get DQ'd at the table. Fix the highlights first, then come back."

**Reactions on the post:**
- 12 ❤️
- 6 😐
- 4 reported as "harsh / harassment" (the trigger for moderator review)

*Original poster (@knightmodeller_v2) replied 90 minutes later: "thanks, that's actually really useful. cat litter ouch lol. will redo highlights."*

#### Artefact 4.2 — Discord thread between volunteer mods

*From the "#mod-decisions" channel on the MiniBase volunteer-mod Discord. Aki (Japan, painters sub) and Klaus (Germany, historical sub).*

> **Aki:** This @greenwingmolar critique post — 4 reports. Within painters norm or harassment?
>
> **Klaus:** I'd call it normal critique. The OP literally asked for help. The tone is sharp but the content is feedback.
>
> **Aki:** Yeah but the painters sub has the "no critique without invitation" thing — but this is a critique thread so invitation is implicit. I think it's fine, want a second opinion before I close the report.
>
> **Klaus:** That "no critique without invitation" is painters-sub-specific. Thread title is literally "help me figure out what's wrong" so OP invited it.
>
> **Aki:** OK closing as no action. Tom said before to be careful about harshness reports though, the 2024 thing.
>
> **Klaus:** That was the sponsor incident. Different. OP isn't a high-profile sculptor and the reply shows they took it well.
>
> **Aki:** Closing. Logging in Discourse as "no action — invited critique within sub norms."

#### Artefact 4.3 — Tom's "moderation patterns" Google Sheet

*Selected rows. Shared with the senior moderator only; not in the volunteer Discord.*

| User / topic | Pattern | Action default | Notes |
|---|---|---|---|
| @sculpturedragon | Established sculptor; recurring IP claims about user uploads | Tom personally reviews every IP claim from this account | After 2024 incident, full review every time |
| @vortex_minis | Sponsor account; commercial-content posts | Tom personally reviews; do not auto-flag as commercial-spam | THE 2024 SPONSOR — never get this wrong |
| Painters sub | "No critique without invitation" | Apply norm; flag posts that critique uninvited | Not in global policy; sub-forum-specific |
| Historical sub | More permissive on historically-charged imagery | Don't apply global "controversial imagery" rule strictly | Flag to Tom if uncertain |
| Japanese painters sub | English-language critiques sometimes read harsher than intended | Soft-warning before any removal action | Aki has flagged this; we're learning |
| @vintage_kitbasher | IP claims credibility unclear; small sculptor | Standard escalation, no fast-track | Watch for retaliatory reports |

---

## Scenario 5 (enriched) — Small-Clinic Patient Intake

*Original brief in `README-Participants-Week1-Scenarios.md` § Scenario 5.*

### The practice

**Westbridge Family Medicine** — 6-physician family medicine practice (US, mid-Atlantic suburb). Two locations 12 miles apart. ~180 patients/day across both sites: routine visits, chronic-disease management, urgent same-day appointments, pre-procedure screenings.

### The function

4-person front-desk intake team supporting both locations (typically 2 at each site, with cross-site rotation when one location is short-staffed). **Dana Velazquez**, RN-trained Practice Manager, oversees the function.

### The four work streams (per visit)

- **Insurance verification** (~180/day; ~3 min/case automated + ~5 min/case for the ~30% that fail auto-verify). Especially complex for self-pay or Medicaid managed-care patients.
- **Prior-authorisation check** (~25/day; ~12 min/case). For scheduled procedures, imaging, specialty referrals.
- **Pre-visit questionnaire & visit-reason triage** (~180/day; ~4 min/case). Routine vs urgent vs same-day classification.
- **Medication reconciliation & allergy-flag review** (~180/day; ~6 min/case). Pharmacy history review, allergy alerts, change flagging.

### Tooling sketch

- **athenahealth** (EHR, modern SaaS, REST APIs)
- **Availity** (insurance eligibility, separate REST-API tool)
- **DoseSpot** (pharmacy / medication reconciliation, integrated with athenahealth)
- **Phone + paper intake forms** (for patients without portal accounts)
- **Google Sheets** (Dana's PA chase list and flagged-patient tracker)

### Stakeholder

**Dana Velazquez**, Practice Manager, RN by background, 11 years at Westbridge. The senior physician has discovered three intake misses in the last quarter (all expired prior auths) and has asked her to "look at this AI thing the medical society keeps emailing about."

### Hard constraints (preserved from the original brief)

1. No clinical judgment by the agent.
2. Any contact with the stated visit reason must preserve a clear human escalation path.
3. HIPAA and state medical-records compliance is non-negotiable.

### What you're expected to elicit through the week

Use your elicitation channels (AI proxy primarily; coach at squad checkpoint / office hours for what AI can't crack) to surface:

- What happens when prior authorisations fail, and how does Dana actually chase them?
- Where does DoseSpot's medication reconciliation miss things in real practice?
- Which patient populations don't fit the standard intake flow, and how is the team accommodating them today?
- What HIPAA / malpractice insurance constraints govern AI usage at the practice?
- What's Dana's personal stake in this — what is she planning for beyond this project?

### Sample artefacts

#### Artefact 5.1 — Dana's PA chase list

*Selected rows from Dana's "PA chase list" Google Sheet. Shared with the front desk only.*

| Patient | Procedure | Insurer | Submitted | Standard SLA | My target chase | Status | Notes |
|---|---|---|---|---|---|---|---|
| MR (DOB 1962-03-14) | Cardiac stress test | Aetna | 18.10 | 5 days | Chase 23.10 | Approved 22.10 | Aetna fast this month, unusual |
| TJ (DOB 1989-07-22) | MRI right knee | UnitedHealthcare Choice | 16.10 | 5 days | Chase 22.10 | Pending | UHC Choice is always 6 days, sometimes 7; visit on 28.10 |
| RB (DOB 1955-11-02) | Colonoscopy | Medicaid Managed Care (Wellpath) | 11.10 | 5 days | Chase day 7 (18.10) | Denied — needs prior visit doc | Wellpath always denies first time on this — resubmit with the August visit note |
| KS (DOB 1976-04-09) | Specialty referral (rheum) | BCBS PPO | 14.10 | 3 days | Chase 19.10 | Approved 16.10 | Standard |
| DP (DOB 1944-12-01) | Cardiac echo | Medicare Advantage (Humana) | 19.10 | 5 days | Chase 26.10 | Pending | Humana always exactly 6 days; never 5 |

*[Footer note in Dana's hand: "Wellpath colonoscopy denial pattern — they want the prior visit note attached, never says so on the form. Standing rule: include with submission, save the resubmit cycle."]*

#### Artefact 5.2 — Physician portal note

*Note attached to patient TJ's chart by Dr. Westbridge after the visit on 28.10.*

> "Visit reason was MRI follow-up for right knee. Patient arrived expecting results review. PA for the MRI was still pending at visit time — see athenahealth ticker. Front desk did not flag this at check-in.
>
> Visit aborted at exam-room check; rescheduled for 04.11 once PA confirmed. Patient frustrated — 'this is the second time this has happened to me.' Please review with Dana.
>
> JW"

#### Artefact 5.3 — Patient phone call about a bill

*Phone call notes captured by front-desk staff (paraphrased; full call ~7 minutes).*

> Patient called about a bill received 22.10 for visit on 12.08 — $340 listed as 'self-pay portion, insurance not on file at date of service.'
>
> Patient (TJ): "I've been on Aetna for three years and I gave you my card every time. Why is this insurance-not-on-file?"
>
> Looked into athenahealth. Patient was actually verified as Aetna at the August visit, but the verification is dated 22.05 (last verified) and somehow when the claim was submitted, the system pulled the older record showing self-pay from 2022.
>
> Resolved: refiled the claim with the Aetna info; refund pending. Took 12 minutes including hold time with billing.
>
> *Front-desk note added to chart: "Patient verification refresh window > 6 months caused billing miss. We don't refresh for chronic patients on stable insurance — Dana said this is the third time. Need to discuss."*

---

## Scenario 6 (enriched) — Academic Journal Desk-Review Triage

*Original brief in `README-Participants-Week1-Scenarios.md` § Scenario 6.*

### The journal

**Journal of Applied Statistics in Industry (JASI)** — UK-based mid-tier academic journal, published quarterly, owned by a small Edinburgh-based academic-society publisher. ~1,400 manuscript submissions/year, ~25% accepted (after desk and peer review). Reputation respectable but viability hinges on protecting the peer-reviewer pool from low-quality work.

### The function

Editorial team:

- **Prof. Eleanor Whittaker**, Editor-in-Chief, university-employed, 20% time on this role (4 years in seat).
- 3 Associate Editors (each ~10–15% time, owning a topic area).
- 1 part-time Editorial Assistant (publisher-paid, 0.4 FTE) handling logistics.

### The four work streams (within desk-review)

- **Initial scope/fit screening** (~1,400/yr; ~10 min/case).
- **Methodology adequacy check** (~1,400/yr; ~25 min/case).
- **Novelty assessment** (~1,400/yr; ~20 min/case).
- **Plagiarism + writing-quality screen** (~1,400/yr; ~10 min/case). iThenticate run + readability check.

Of these, ~770 (55%) get desk-rejected; ~630 (45%) move to peer review.

### Tooling sketch

- **ScholarOne Manuscripts** (manuscript management, REST APIs available via publisher IT)
- **iThenticate** (plagiarism detection, integrated)
- **Crossref** (metadata + reference verification, APIs available)
- **In-house "AE Tracker" Excel** (Eleanor's spreadsheet, AE workload balancing)
- **Email + Slack** (informal editorial discussion)

### Stakeholder

**Prof. Eleanor Whittaker**, Editor-in-Chief. Brief from the publisher's editorial board: "Speed matters, but reputation matters more. Your peer reviewers are your scarcest resource."

### What you're expected to elicit through the week

Use your elicitation channels (AI proxy primarily; coach at squad checkpoint / office hours for what AI can't crack) to surface:

- Which prior journal incidents shape Eleanor's risk tolerance, and which failure mode is she more anxious about — false-reject or false-accept?
- How does the desk-review timing actually work in practice, and where does it bunch?
- Where do AEs reassign work informally that the documented workflow doesn't capture?
- How is novelty actually assessed, and where does Crossref under-perform?
- What appeals does Eleanor receive from authors, and how does she respond?

### Sample artefacts

#### Artefact 6.1 — iThenticate similarity report

*iThenticate similarity report for manuscript JASI-2026-0788 ("Bayesian shrinkage estimators in panel data with unbalanced clusters"). Submitted 14.10 by Dr. Patel et al.*

> **Overall similarity: 22%**
>
> Top matches:
> - **18%** — *Patel, R., & Hayashi, T. (2024). "Shrinkage in unbalanced panels: a simulation study." Journal of Statistical Computation and Simulation.* (the same authors' prior published work)
> - **2%** — *Wu, L. (2019). "Hierarchical priors in panel models." Journal of Econometrics.*
> - **2%** — Standard methodology boilerplate (unattributed)
>
> *iThenticate flag: above 15% threshold. Recommend desk-review.*

*[Eleanor's margin note in the editorial system: "18% to authors' own 2024 paper. Legitimate self-citation; this is the standard 'methodology section recap' you see in follow-up papers. Override to send forward. The other 4% is fine."]*

#### Artefact 6.2 — AE Tracker workload imbalance

*Selected columns from Eleanor's "AE Tracker" Excel — current load as of week 42.*

| AE | Topic area | Active assignments | Decisions overdue (>4 wks) | Notes |
|---|---|---|---|---|
| Dr. Mehta | Bayesian methods | 11 | 2 | "Carrying load — said yes to extra last quarter, can't redirect more" |
| Dr. Lehmann | Applied econometrics | 4 | 0 | Light load this quarter; sabbatical ending |
| Dr. Park | Biostatistics | 9 | 1 | Standard load |

*[Eleanor's note at the bottom: "Reassigned 4 of Mehta's recent 'Bayesian-methods' submissions to Lehmann because Mehta was drowning. Not strictly Lehmann's topic but he's competent for them. Don't tell anyone."]*

#### Artefact 6.3 — Slack gut-check thread

*From the JASI editors' Slack workspace, #editorial channel.*

> **Mehta:** Eleanor, can I get a gut check on JASI-2026-0801? Methodology is technically clean, but the "novel contribution" claim is essentially restating the 2022 Wu result with a slightly different prior. I'd say desk-reject for novelty but I'm not 100% — borderline.
>
> **Eleanor:** Send me the abstract.
>
> **Mehta:** [link]
>
> **Eleanor:** I see what you mean. The "novel" prior is a parameterised Wu — maybe 5% novelty contribution at most. But Wu's paper was at JASI's competitor; if we desk-reject, are we comfortable with the optics?
>
> **Mehta:** Not really. But "we should accept because of optics" isn't a great reason either.
>
> **Eleanor:** No — desk-reject is right on substance. Use the standard novelty-threshold language. I'll personally rewrite the rejection letter so it doesn't sound like we're blocking the line of work, just that this specific paper doesn't add enough.
>
> **Mehta:** Thanks.

---

## Scenario 7 (enriched) — Municipal Building Permit Screening

*Original brief in `README-Participants-Week1-Scenarios.md` § Scenario 7.*

### The city

**City of Brookfield** — US Mid-Atlantic suburb (~95K population). Mix of established residential (1930s–1960s housing stock with historic-district overlay), modern subdivisions, and small-scale infill development pressure. Permit volume up 35% over 5 years.

### The function

Building Department under City Public Works:

- **Marcus Trent**, Building Department Director (9 years).
- 18 plan reviewers (residential, commercial, structural specialists).
- 3 senior plans examiners (variances, historic district, unusual structures).
- 2 administrative staff handling intake and applicant communications.

### The four work streams

- **Intake & documentation completeness** (~5,800/yr; ~12 min/case).
- **Standard code compliance review** (~3,800/yr — the 65% routine; ~75 min/case). IBC + state amendments + ~40 pages of local amendments across zoning, fire, energy, accessibility.
- **Correctable-deficiency kickbacks** (~1,450/yr — the 25%; ~45 min/case to identify + write up).
- **Senior plans-examiner escalations** (~580/yr — the 10%; ~3.5 hrs/case). Variances, historic-district, unusual structural designs.

### Tooling sketch

- **Accela Civic Platform** (permit-management, modern, REST APIs)
- **GIS layers** (city GIS — zoning, flood, historic district, APIs available)
- **City SharePoint + scanned drawing archive** (some still on microfiche)
- **Bluebeam Revu** (markup software — what reviewers actually use)
- **Email** (most applicant communication)

### Hard constraint (preserved from the original brief)

**No permit decision — approval, rejection, or kickback — may be made without a named human plan reviewer attached to the record.** This is a City Council mandate and is non-negotiable.

### Stakeholder

**Marcus Trent**, Building Department Director. Under personal political pressure: the 19-day average time-to-first-review is a Council issue, and one Council member is publicly calling for outsourcing plan review to a private firm.

### What you're expected to elicit through the week

Use your elicitation channels (AI proxy primarily; coach at squad checkpoint / office hours for what AI can't crack) to surface:

- What previous process-improvement or automation pilots have been tried, and what happened?
- Where do reviewers' code interpretations diverge in ways the documentation doesn't capture?
- Which parts of the workflow live in email vs Accela vs Bluebeam vs reviewers' heads?
- What's Marcus's personal political risk profile — what failure mode would end his role?
- How does the GIS check actually fit into routine reviews vs how the SOP describes it?

### Sample artefacts

#### Artefact 7.1 — Returned-with-comments email (kickback)

*Email from plan reviewer Carlos Diaz to applicant architect Sarah O'Brien, 18.10. CC: City permit-intake@ (which routes to a generic inbox, not Accela).*

> "Hi Sarah,
>
> Reviewed the permit application for 1442 Linden Ave. Six items needing correction before I can move this forward:
>
> 1. Stair stringer dimensions on Sheet A-3.2 don't match the framing detail on S-2.1 — need consistent
> 2. Energy code: U-factor for the new windows on the south elevation shown as 0.32, but state amendment requires 0.30 max
> 3. Accessibility ramp slope calculated at 1:11.8 — code allows 1:12 max, this is over (just barely but over)
> 4. Smoke detector locations missing from the bedroom additions on the second floor
> 5. Lot setback diagram appears to use the older 1978 boundary — check current GIS, this lot was re-platted 2018
> 6. Structural drawings reference 2018 IBC; we're now on 2021 IBC + Brookfield amendments. Update references.
>
> Resubmit when ready.
>
> P.S. — I noticed the historic-district overlay edge runs through your front yard setback. You probably want Mariela to look at that before resubmitting; she has the historic-district experience in our office.
>
> Carlos D.
> Senior Plan Reviewer, City of Brookfield"

*[Note from Marcus, attached separately to the file: "Carlos's kickback didn't make it into Accela — he typed 'see email' in the comments field. Third time this month from Carlos. Need to discuss."]*

#### Artefact 7.2 — Marcus's "issues log" Excel

*Selected rows from Marcus's personal "Plan Review Inconsistencies" Excel — unshared, on his C: drive.*

| Issue | Reviewers diverge | Cases observed | Root cause | Status |
|---|---|---|---|---|
| Energy code U-factor for additions: state amendment vs. IECC 2021 | Carlos, James apply state amendment (0.30); Reagan, Patel apply IECC 2021 (0.32) | 14 in last quarter | State amendment issued mid-2024, not all reviewers caught the update | NEED TO RESOLVE — keep flagging |
| Setback measurement from face of structure vs. face of foundation | Mariela measures from foundation; rest from structure | 6 cases | Old-school habit from Mariela's previous city | DECISION: confirmed Mariela is correct per current code; rest of team needs retraining |
| Garage as habitable vs. accessory for ADU compliance | Reagan, James treat as accessory; Patel as habitable | 5 cases this year | 2023 zoning amendment ambiguity | NEEDS LEGAL REVIEW; not resolved |

*[Marcus's note at the bottom: "Haven't formalised any of these because each one creates extra retraining work and I don't have the slack. They keep biting us though. Council member's 'inconsistency' complaint is partly about exactly this — he's heard from developers who got conflicting comments on similar projects."]*

#### Artefact 7.3 — Council member email

*Forwarded by the City Manager to Marcus. Original from Council Member Doris Aldrich, 11.10.*

> "Subject: Building Department turnaround — discussion at next session
>
> City Manager,
>
> I've heard now from three different builder-association members in two weeks about building department review times. The common complaint is the 19-day average, but a more specific concern is **inconsistency**: builders submitting similar projects to similar reviewers are getting different kinds of kickbacks.
>
> I'd like the next session to include a discussion of: (a) compression of average review time, (b) outsourcing options for routine permits — there are private firms advertising 5-day turnaround, (c) whether the inconsistency is a training issue, a code-amendment issue, or a staffing issue.
>
> Marcus should be ready to speak to all three at the public session 25.10.
>
> Doris."

---

## Closing note

If you reach Thursday's peer review with a Cognitive Load Map, Delegation Suitability Matrix, and Agent Purpose Document built only from this document — without coach-elicited material in your Assumptions log — you have skipped the central skill the week is testing. Use your coach.
