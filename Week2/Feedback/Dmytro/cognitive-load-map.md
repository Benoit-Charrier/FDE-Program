# Cognitive Load Map — MiniBase Community Moderation

## Work Streams Overview

| # | Work Stream | Volume | Time/case | Queue share |
|---|---|---|---|---|
| WS1 | Routine spam / clear violations | ~1,080/day | ~30 sec | 72% |
| WS2 | Grey-zone case review | ~360/day | ~5 min | 24% |
| WS3 | User dispute appeals | ~60/day | ~8 min | 4% |
| WS4 | IP claim resolution | ~3–5/wk | ~30 min | Separate channel |

Total moderator effort ≈ 47 hours/day across 10-person team (2 paid, 8 volunteer). Team is at capacity.

*All four work streams are fully mapped (JTBD + micro-tasks + dimension scores + cognitive zones + breakpoints).*

---

## WS1 — Routine Spam / Clear Violations (Human-led + Automation Support)

### JTBD — Cognitive Contract

| Field | Content |
|---|---|
| **Trigger** | Flag arrives in moderation queue via user report, automated detection, or moderator sampling |
| **Actor** | Volunteer moderator (or agent) |
| **Goal** | Classify the flagged post and execute the correct action before queue volume compounds |
| **Key decisions** | (1) Does the post match a known spam/violation pattern? (2) Is the user account in the exceptions list (Tom's Google Sheet)? (3) Is sub-forum placement incorrect? |
| **Key systems** | Discourse REST API (flag queue, post content, user account history, reporter comments); Tom's Google Sheet (exception accounts — confirmed sponsors e.g. @vortex_minis; special users e.g. @sculpturedragon; **note:** established commercial members with informal latitude are NOT in the Sheet — detection fallback is Stripe payment tier or mod recognition) |
| **Expected output** | Action applied (removed / no-action) + flag closed + action logged in Discourse; OR case pushed to WS2 queue if no pattern match |
| **Classification** | **Rule-bound execution** — all decisions are Boolean checks against enumerable criteria; no contextual judgment required once exception accounts are pre-loaded |

### Micro-tasks

1. Receive flag notification from Discourse queue
2. Open flagged post; read all reporter comments
3. Check user account age and prior violation history in Discourse
4. Check user handle against exception list in Tom's Google Sheet (confirmed sponsors e.g. @vortex_minis; special users e.g. @sculpturedragon) — note: established commercial members with informal latitude are NOT in the Sheet; no structured source for this third tier [Assumed: confidence medium — Q5]
5. If exception match → push to WS2 immediately; do not evaluate content
6. Read post content against spam / off-topic / miscategorisation criteria
7. Confirm sub-forum placement (is it in the correct sub-forum?)
8. Decide: remove / no-action / escalate to WS2
9. Log action in Discourse + close flag

*Artefact evidence: steps 4–5 derived from Artefact 4.3 (Tom's tracker, @vortex_minis rule). Steps 6–7 match Artefact 4.2 (Aki and Klaus's sub-forum placement check on @greenwingmolar).*

### 8-Dimension Scores (per micro-task)

| # | Micro-task | Cognitive Load | Input Structure | Decision Determinism | Exception Frequency | Turn-Taking | Latency | Compliance / Risk | Tool Availability |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Receive flag notification from queue | Low | High | High | Low | Low | Low | Low | High |
| 2 | Open post + read all reporter comments | Low | High | High | Low | Low | Low | Low | High |
| 3 | Check account age + prior violation history | Low | High | High | Low | Low | Low | Low | High |
| 4 | Check exception list in Tom's Sheet (Tier 1/2) | Low | Medium | High | Low | Low | Low | **High** | Medium |
| 5 | Route to WS2 if exception match | Low | High | High | Low | Low | Low | **High** | High |
| 6 | Read content vs. spam / off-topic criteria | Low | Medium | High | Low | Low | Low | Low | High |
| 7 | Confirm sub-forum placement | Low | High | High | Low | Low | Low | Low | High |
| 8 | Decide: remove / no-action / escalate | Low | High | High | Low | Low | Low | Low | High |
| 9 | Log action + close flag | Low | High | High | Low | Low | Low | Low | High |

**Score notes:**
- Steps 1–3 and 6–9: all Low/High — fully rule-bound retrieval and execution; high delegation suitability throughout
- Step 4: Input Structure = Medium because Tom's Sheet is semi-structured (Google Sheet, not a proper database); Compliance/Risk = High because missing a sponsor account here is the 2024 incident risk; Tool Availability = Medium because Google Sheets API requires a separate integration from Discourse
- Step 5: Compliance/Risk = High because routing a sponsor to the wrong queue is the highest-consequence error in WS1; everything else is deterministic once step 4 fires

### Cognitive Zones

```
Retrieval (1–3) → Exception Screen (4–5) → Classification (6–7) → Decision (8) → Documentation (9)
```

### Breakpoints

- No known spam/violation pattern match → escalate to WS2 queue (do not leave in WS1 backlog)
- Exception account match at step 4 → push to WS2 immediately; content analysis does not run

---

## WS2 — Grey-Zone Case Review (Human-led + Agent Support)

### JTBD — Cognitive Contract

| Field | Content |
|---|---|
| **Trigger** | Post escalated from WS1 (no pattern match), OR high-reporter-count flag (>3 distinct users) arrives directly in grey-zone queue |
| **Actor** | Volunteer moderator (primary decision); Senior Moderator (second opinion when sub-forum norm is disputed); Tom (mandatory for special-account cases) |
| **Goal** | Produce a defensible, documented decision by correctly assembling and applying sub-forum norms, user tier, cultural context, and case precedent — without requiring Tom to reverse the decision |
| **Key decisions** | (1) Is this account a confirmed sponsor or special user (Tom's Sheet) → route to Tom immediately? (2) Is this account an established commercial member with informal community-standing latitude (not in Sheet; unstructured) → handle with elevated caution? (3) Which sub-forum norm set applies? (4) Does cultural/regional context shift the interpretation threshold? (5) What Discord precedent matches this case? (6) Weigh false-negative risk (existential) vs. false-positive risk (survivable) → final action: no-action / soft-warn / remove / escalate |
| **Key systems** | Discourse (post content, thread context, reporter count, user account history); Tom's Google Sheet (exception accounts + sub-forum norms); Discord #mod-decisions (informal precedent cases); Stripe (user payment tier — sponsor detection fallback) |
| **Expected output** | Decision + full rationale logged in Discourse + flag closed; OR escalation package sent to Tom with context brief attached |
| **Classification** | **Exception-bound judgment** — every case is, by definition, outside WS1's rule set; requires multi-source synthesis and implicit norm knowledge; cannot be reduced to rules without losing the cases that carry the most risk |

### Micro-tasks

1. Open flagged post; read full thread context — not just the flagged message
2. Check user account handle against Tom's Google Sheet — three-tier check:
   - **Tier 1 (confirmed sponsor):** e.g. @vortex_minis → route to Tom immediately; stop
   - **Tier 2 (special user):** e.g. @sculpturedragon → route to Tom immediately; stop
   - **Tier 3 (established commercial member, informal latitude):** NOT in Sheet; recognisable by Stripe commercial tier or mod institutional knowledge — no structured lookup; flag for elevated caution [Assumed: confidence medium — stakeholders_quiz Q5]
3. **If Tier 1 or Tier 2 match → assemble escalation package and route to Tom; stop all further analysis**
4. Identify which sub-forum the post is in; retrieve its specific norm set from Tom's tracker (Painters: "no critique without invitation"; Historical: permissive on charged imagery; Japanese painters: soft-warn before removal)
5. Assess cultural/regional context — is the harshness threshold different for this community segment?
6. Count reporter comments and read each for signal quality (4 reports from distinct users carries more weight than 1)
7. Check original poster's response to the flagged content — did OP accept the feedback? (Artefact 4.1: @knightmodeller_v2's "thanks, that's actually really useful" changes the read)
8. Search Discord #mod-decisions for precedent cases matching this pattern (same sub-forum + same type of report)
9. Assess viral risk: is the post gaining rapid engagement since being flagged?
10. Weigh false-negative risk vs. false-positive risk for this specific case — apply Tom's asymmetry (FN existential, FP survivable)
11. Draft decision rationale: outcome + the specific norms/signals that drove it
12. Decide: no-action / soft-warn / remove / escalate to Tom
13. Log decision + full rationale in Discourse + close flag
14. *[If sub-forum norm is ambiguous]* Post to #mod-decisions for second opinion before closing

*Artefact evidence: steps 4–5 from Artefact 4.3 (Tom's tracker rows for Painters/Historical/Japanese subs). Steps 6–7 from Artefact 4.1 (greenwingmolar case — OP's reply changes the read). Steps 8 and 14 from Artefact 4.2 (Aki/Klaus Discord exchange). Step 3 from stakeholders_quiz Q1 (2024 sponsor incident).*

### 8-Dimension Scores (per micro-task)

| # | Micro-task | Cognitive Load | Input Structure | Decision Determinism | Exception Frequency | Turn-Taking | Latency | Compliance / Risk | Tool Availability |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Open post + read full thread context | Medium | Low | Low | Medium | Low | Low | Medium | High |
| 2 | Three-tier exception check (Sheet + Stripe + knowledge) | Medium | Low | Medium | Low | Low | Low | **High** | Low |
| 3 | Route to Tom if Tier 1/2 match | Low | High | High | Low | Low | Low | **High** | High |
| 4 | Identify sub-forum + retrieve norm set | Medium | Low | Medium | Medium | Low | Low | Medium | Low |
| 5 | Assess cultural/regional context | **High** | Low | Low | Medium | Low | Low | Medium | Low |
| 6 | Count + assess reporter comments for signal | Medium | Medium | Medium | Medium | Low | Low | Medium | High |
| 7 | Check OP's response to flagged content | Medium | Medium | Low | Medium | Low | Low | Medium | High |
| 8 | Search Discord #mod-decisions for precedent | **High** | Low | Low | **High** | Low | Low | **High** | Low |
| 9 | Assess viral risk | Medium | Medium | Medium | Medium | Low | **High** | **High** | Medium |
| 10 | Weigh false-negative vs false-positive risk | **High** | Low | Low | **High** | Low | Low | **High** | Low |
| 11 | Draft decision rationale | **High** | Low | Low | **High** | Low | Low | Medium | Low |
| 12 | Decide: no-action / soft-warn / remove / escalate | **High** | Low | Low | **High** | Low | Medium | **High** | Low |
| 13 | Log decision + rationale + close flag | Low | High | High | Low | Low | Low | Low | High |
| 14 | [If ambiguous] Post to #mod-decisions + await consensus | Medium | Low | Low | **High** | **High** | Medium | **High** | Low |

**Score notes:**
- Steps 2–3: Compliance/Risk = High — sponsor miss is the 2024 incident; Tool Availability = Low on step 2 because Tier 3 accounts have no structured source
- Steps 4–5: Tool Availability = Low — sub-forum norms not in any queryable system; step 5 is the highest pure-judgment step in the context assembly zone: the moderator must infer the cultural origin of both the poster and the reporters, assess whether the tone crosses a threshold for that community segment, and do this with no structured data — Discourse user profiles do not expose region; the moderator works from username patterns, post history, and sub-forum context alone. A UK moderator reading a German poster's blunt critique applies a different threshold than Aki reading the same post in the Japanese sub. No tool can encode this; no policy document defines it
- Step 8: Tool Availability = Low — Discord has no moderation search API; moderator must manually scroll channel history
- Step 9: Latency = High — only step in WS2 where real-time response may be required (viral risk window)
- Steps 10–12: Cognitive Load = High, Decision Determinism = Low, Compliance/Risk = High — the three-step judgment core; highest cognitive demand and risk in the work stream; Tool Availability = Low across all three
- Step 14: Turn-Taking = High — asynchronous Discord thread; moderator must wait for peer responses with no defined SLA

### Cognitive Zones

```
Exception Screen (1–3) → Context Assembly (4–7) → Precedent Search (8) → Risk Assessment (9) → Judgment (10–12) → Documentation (13)
```

*Step 14 (Discord consensus) is a conditional branch out of Judgment — triggered when sub-forum norm is ambiguous; loops back into Judgment once consensus is reached.*

### Breakpoints

- User account is Tier 1 (confirmed sponsor) or Tier 2 (special user) in Tom's tracker → immediate Tom personal review; do not run any content analysis
- User account is Tier 3 (established commercial member, informal latitude) → continue analysis but apply elevated caution; no removal without Senior Moderator sign-off [Assumed: confidence medium — stakeholders_quiz Q5]
- Sub-forum norm is ambiguous AND reporter count > 3 distinct users → Discord consensus required before closing
- Post is gaining rapid engagement (viral signal) → immediate Tom escalation
- Reporter count = 0 (moderator-initiated flag) → higher burden of evidence required before any removal action
- Case open in #mod-decisions for > [TBD minutes — no SLA currently defined] without resolution → escalate to Senior Moderator; do not allow indefinite debate [stakeholders_quiz Q4: failure mode — volunteers debate too long instead of escalating]
- Decision is overturn of a previous moderation action → treat as WS3 (appeal), not WS2

---

## WS3 — User Dispute Appeals (Human-led + Agent Support)

### JTBD — Cognitive Contract

| Field | Content |
|---|---|
| **Trigger** | User submits appeal of a prior moderation action via Discourse appeal mechanism or email; OR Tom discovers at appeal stage that a WS2 case was inconsistently closed by a volunteer (stakeholders_quiz Q4: failure mode — one mod closes what another would have escalated) |
| **Actor** | Senior Moderator (primary); Tom (when original action was Tom's, or original case touched a sponsor/special account) |
| **Goal** | Determine whether the original moderation decision was within policy and communicate the outcome to the appellant — upholding or overturning with a clear rationale |
| **Key decisions** | (1) Was the original action within policy bounds? (2) Does the appellant's new information or argument change the assessment? (3) Uphold or overturn? (4) If overturn — what corrective action and communication? |
| **Key systems** | Discourse (original post, prior moderation log, user account history); global 14-page policy; Tom's Google Sheet (if original case involved a special account) |
| **Expected output** | Appeal decision logged in Discourse + user notified of outcome + moderation record updated if overturned |
| **Classification** | **Rule-bound review + communication** — checking a prior action against policy is mostly deterministic; the communication layer (explaining a reversal to a community member) adds a relationship and tone dimension that resists full delegation |

### Micro-tasks

1. Receive appeal via Discourse appeal mechanism or email
2. Retrieve original moderation action + full case context from Discourse log
3. Check whether original case involved a special account (Tom's Sheet)
4. If original action was Tom's or involves special account → route to Tom; stop
5. Read appellant's argument in full
6. Check appellant's claim against the 14-page global policy
7. Assess whether original decision was within policy bounds
8. If appellant presents new information → reassess original decision against it
9. Decide: uphold or overturn
10. If overturn → determine corrective action (restore post, rescind warning, etc.)
11. Draft communication to appellant explaining outcome and rationale
12. Apply corrective action in Discourse if overturning
13. Log appeal decision + outcome in Discourse moderation record

*Artefact evidence: steps 3–4 from Artefact 4.3 (Tom's tracker — special accounts route to Tom personally). Step 11 grounds the communication dimension of the archetype — explaining a reversal to a community member requires tone judgment not present in WS1/WS2.*

### 8-Dimension Scores (per micro-task)

| # | Micro-task | Cognitive Load | Input Structure | Decision Determinism | Exception Frequency | Turn-Taking | Latency | Compliance / Risk | Tool Availability |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Receive appeal | Low | High | High | Low | Low | Low | Low | High |
| 2 | Retrieve original action + case context | Low | High | High | Low | Low | Low | Low | High |
| 3 | Check for special account (Tom's Sheet) | Low | Medium | High | Low | Low | Low | **High** | Medium |
| 4 | Route to Tom if special account / Tom's original action | Low | High | High | Low | Low | Low | **High** | High |
| 5 | Read appellant's argument | Medium | Low | Low | Medium | Low | Low | Medium | High |
| 6 | Check claim against global policy | Medium | Medium | Medium | Medium | Low | Low | Medium | High |
| 7 | Assess whether original decision was within policy | Medium | Medium | Medium | Medium | Low | Low | Medium | High |
| 8 | Reassess if new information changes assessment | **High** | Low | Low | **High** | Low | Low | Medium | High |
| 9 | Decide: uphold or overturn | **High** | Low | Low | **High** | Low | Low | **High** | Low |
| 10 | Determine corrective action if overturning | Medium | Low | Medium | Medium | Low | Low | Medium | High |
| 11 | Draft communication to appellant | **High** | Low | Low | Medium | Low | Low | Medium | Low |
| 12 | Apply corrective action in Discourse | Low | High | High | Low | Low | Low | Medium | High |
| 13 | Log appeal decision in moderation record | Low | High | High | Low | Low | Low | Low | High |

**Score notes:**
- Steps 1–4: retrieval and routing — fully automatable; step 3 Compliance/Risk = High for the same reason as WS1/WS2 (sponsor miss risk)
- Steps 5–7: policy check — structured enough for agent support (retrieve policy, surface relevant clauses); Decision Determinism drops to Medium because policy coverage is incomplete for edge cases
- Steps 8–9: reassessment and final decision — Cognitive Load = High, Decision Determinism = Low; the agent cannot make this call; it can surface prior context but the judgment is the Senior Moderator's
- Step 11: communication drafting — Cognitive Load = High because tone of a reversal communication is relationship-sensitive; Tool Availability = Low because no drafting tool exists; agent could draft but human must review

### Cognitive Zones

```
Retrieval (1–2) → Exception Screen (3–4) → Policy Review (5–7) → Judgment (8–9) → Resolution (10–11) → Execution & Documentation (12–13)
```

### Breakpoints

- Original action was Tom's personally → Tom reviews the appeal
- Original case involved a sponsor or special-account user → Tom
- Overturn decision → Senior Moderator sign-off required before communication sent to user

---

## WS4 — IP Claim Resolution (Human-only)

### JTBD — Cognitive Contract

| Field | Content |
|---|---|
| **Trigger** | Email received from an external sculptor or manufacturer asserting copyright or trademark violation over user-uploaded content |
| **Actor** | Tom (personal review by default; @sculpturedragon is always Tom per tracker) |
| **Goal** | Assess claim credibility and merit, determine the platform's response, and protect MiniBase from legal exposure while managing claimant relationships |
| **Key decisions** | (1) Is the claimant in Tom's tracker with prior claim history? (2) Is the claim substantive or retaliatory? (3) Content action: takedown / dispute / no-action? (4) Response tone: informal acknowledgement vs. formal legal language? |
| **Key systems** | Email (inbound claim + correspondence archive); in-house Gallery Rails app (content under dispute); Tom's Google Sheet (claimant history — e.g. @sculpturedragon full-review rule, @vintage_kitbasher watch flag); **no structured tool for claim credibility assessment — triage criteria live in Tom's head** [stakeholders_quiz Q3: medium confidence; confirm whether criteria will be documented post-deployment]; potentially external legal counsel |
| **Expected output** | Decision logged + claimant email response sent + content action applied (or explicitly justified non-action) + legal correspondence archived |
| **Classification** | **Knowledge-bound judgment** — claimant credibility, history of retaliatory reports, and appropriate legal register are tacit knowledge; irreversibility of a content takedown and relationship stakes with known sculptors make this human-only |

### Micro-tasks

1. Receive claim email; log receipt
2. Check claimant name/handle against Tom's Google Sheet (prior claim history, @sculpturedragon rule, @vintage_kitbasher watch flag)
3. Locate disputed content in Gallery Rails app
4. Assess claimant credibility: known sculptor with plausible claim, or retaliatory history?
5. Assess claim merit: does the content plausibly infringe the stated IP?
6. Determine platform response: takedown / dispute / no-action
7. Determine response tone: informal acknowledgement vs. formal legal language
8. Draft email response to claimant
9. Apply content action in Gallery if required (takedown)
10. Log decision + archive full correspondence

*Artefact evidence: steps 2 and 4 from Artefact 4.3 (Tom's tracker — @sculpturedragon full review, @vintage_kitbasher cautious). Step 4 from stakeholders_quiz Q3 (triage criteria live in Tom's head; no structured tool).*

### 8-Dimension Scores (per micro-task)

| # | Micro-task | Cognitive Load | Input Structure | Decision Determinism | Exception Frequency | Turn-Taking | Latency | Compliance / Risk | Tool Availability |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Receive claim email + log receipt | Low | Medium | High | Low | Low | Low | Low | High |
| 2 | Check claimant against Tom's Sheet | Medium | Medium | High | Low | Low | Low | **High** | Medium |
| 3 | Locate disputed content in Gallery | Low | High | High | Low | Low | Low | Low | Medium |
| 4 | Assess claimant credibility | **High** | Low | Low | **High** | Low | Low | **High** | Low |
| 5 | Assess claim merit | **High** | Low | Low | **High** | Low | Low | **High** | Low |
| 6 | Determine platform response | **High** | Low | Low | **High** | Low | Low | **High** | Low |
| 7 | Determine response tone | **High** | Low | Low | **High** | Low | Low | **High** | Low |
| 8 | Draft email response | **High** | Low | Low | **High** | Low | Low | **High** | Low |
| 9 | Apply content action in Gallery | Low | High | High | Low | Low | Low | **High** | Medium |
| 10 | Log decision + archive correspondence | Low | High | High | Low | Low | Low | **High** | High |

**Score notes:**
- Steps 1–3: mechanical retrieval; steps 1 and 3 are automatable; step 2 Compliance/Risk = High (claimant routing error = legal exposure)
- Steps 4–8: the judgment core — Cognitive Load = High, Decision Determinism = Low, Exception Frequency = High, Compliance/Risk = High across all five; Tool Availability = Low because no structured credibility tool exists (stakeholders_quiz Q3); this cluster is what makes WS4 Human-only
- Steps 9–10: execution and logging — automatable once Tom has decided; Compliance/Risk = High on step 9 because takedown is irreversible

### Cognitive Zones

```
Retrieval (1–3) → Assessment (4–5) → Decision (6–7) → Communication (8) → Execution & Documentation (9–10)
```

### Breakpoints

- Claimant is @sculpturedragon → Tom personal review; non-negotiable per 2024 incident
- Claimant is @vintage_kitbasher → standard escalation, no fast-track; retaliatory reports history (Artefact 4.3)
- Takedown decision → Tom must approve; no volunteer or agent can action a takedown

---

## Lived vs. Documented Process

The 14-page global policy describes a uniform moderation process applied consistently by the volunteer team. The lived process differs in seven material ways:

**1. Shadow governance layer.** Tom's private Google Sheet contains sponsor exceptions, special-account routing rules, and sub-forum norms that override the written policy. Volunteers do not have access. Any moderation decision touching these accounts is implicitly governed by rules that don't exist in the documented policy. An agent built from the policy alone will be built for an imaginary organisation.

**2. Sub-forum norms are informal and undocumented.** The Painters sub's "no critique without invitation," the Historical sub's permissiveness on charged imagery, and the Japanese painters sub's soft-warn threshold all live in Tom's tracker and volunteer institutional memory. Artefact 4.2 shows these norms being applied in real time — Aki citing the Painters sub norm, Klaus confirming the thread context makes it an invited critique — without consulting any written source.

**3. Precedent is built in Discord, not in Discourse.** When mods are uncertain, they negotiate in #mod-decisions and close the flag. These precedents are the de-facto case law for grey-zone decisions, but they are unstructured, unsearchable, and invisible to any new volunteer or automated system.

**4. Tom is the single point of failure for commercial relationships.** The 2024 sponsor incident created a personal review rule that routes all sponsor-related content decisions to Tom. This is not in the policy, not documented anywhere except Tom's tracker, and creates a bottleneck that grows with platform volume. Any delegation design that doesn't explicitly handle this routing rule will reproduce the failure mode.

**5. Three user tiers exist but only one is structured.** The volunteer team effectively operates with three user categories — confirmed sponsors (Tom's Sheet), established commercial members with informal community-standing latitude (not in any system), and standard users — but only the first tier is machine-readable. The middle tier is recognised through mod institutional memory or Stripe payment data, which doesn't map cleanly to "sponsor" status. This means an agent doing an exception screen will miss Tier 3 accounts entirely unless a structured source is created. [stakeholders_quiz Q5: medium confidence]

**6. No formal escalation trigger exists for Discord consensus deadlocks.** When mods disagree in #mod-decisions, the informal rule is "if not sure, ask." There is no time limit, no defined escalation path if consensus isn't reached, and no mechanism to prevent a case from being closed inconsistently by one volunteer while another would have escalated. Tom only learns about these inconsistencies when the affected user files an appeal. [stakeholders_quiz Q4: medium confidence]

**7. Regional communication norms create a systematic interpretation problem that the policy does not acknowledge.** The MiniBase user base spans US, UK, Germany, Australia, and Japan. The volunteer moderator team mirrors the same distribution. What reads as harassment in UK English may be normal directness in German communication; what reads as acceptable bluntness in Australian English may read as aggression to a Japanese member; English-language critiques in the Japanese painters sub carry a harshness premium not present in the original intent. The 14-page policy is written in a single cultural register and applies a single harshness threshold. The lived process requires every grey-zone moderator to silently perform cross-cultural tone interpretation on every case — with no guidance, no structured user region data, and no consistent calibration across the volunteer team. The Japanese sub case is the only one Tom has formally acknowledged (stakeholders_quiz Q2); the rest are invisible in the documented process and inconsistently handled across moderators.
