# Agent Purpose Document — WS2 Grey-Zone Moderation Context Agent

**Primary agentic target:** WS2 — Grey-Zone Case Review (V×V = 20)

---

## Purpose Statement

Assemble the full structured context brief a moderator needs to make a defensible grey-zone decision — thread context, account tier, sub-forum norm, reporter signal, Discord precedent, and viral risk — so the moderator applies judgment to organised evidence rather than scattered, manually-gathered inputs.

---

## Scope

**In scope:**
- Read Discourse flagged post and full thread context
- Check user account handle against Tom's Google Sheet (Tier 1/2 classification)
- Check Stripe payment tier as Tier 3 fallback signal (commercial account not in Sheet) [Assumed: low confidence — a Discourse user ID → Stripe customer ID mapping exists or can be created; not confirmed in any scenario source — test via DQ#N]
- Retrieve sub-forum norm from structured norm source [Assumed: medium confidence — Tom will export sub-forum norms from his private tracker into a structured queryable source before go-live; confirmed norms exist (stakeholders_quiz Q2) but no structured source currently exists — test via DQ#N]
- Count and assess reporter comments for signal quality
- Check original poster's response to flagged content
- Search indexed Discord #mod-decisions channel for precedent cases matching sub-forum + report type
- Calculate viral risk indicator (engagement velocity in trailing 30-minute window)
- Draft decision rationale template populated with assembled evidence
- Deliver complete structured context brief to moderator review queue

**Out of scope:**
- Making any content decision (remove / no-action / soft-warn)
- Closing a flag in Discourse
- Communicating with users, reporters, or the original poster
- Screening for Tier 3 accounts without a structured data source
- Applying a sub-forum norm not found in the structured norm source
- Assessing cultural or regional context (no structured data; requires moderator judgment)
- Weighing false-negative vs. false-positive risk (Tom's asymmetry; human-only)
- Any action on Tier 1 or Tier 2 accounts beyond immediate routing to Tom

---

## KPIs

| KPI | Target | Measurement |
|---|---|---|
| Context brief completeness | ≥95% of briefs have all available data fields populated before reaching moderator | % of briefs with no silently-omitted fields |
| Tier 1/2 escalation accuracy | 100% — zero sponsor or special-account misses acceptable | % of Tier 1/2 accounts correctly identified and routed to Tom before content analysis runs |
| Moderator time-per-case | ≤3 min average (baseline: 5 min) — ≥40% reduction | Median time from brief delivery to moderator decision |
| Escalation rate (incomplete brief) | ≤15% of cases flagged for manual assembly due to missing data | % of cases where agent cannot complete the brief and hands off unfinished |

---

## Autonomy Matrix

| Decision / Action | Authority | Condition |
|---|---|---|
| Read post + thread context from Discourse | Agent alone | Always |
| Check account against Tom's Sheet | Agent alone | Always |
| Route case to Tom | Agent alone | `account_tier = 1` OR `account_tier = 2` in Tom's Sheet |
| Retrieve sub-forum norm | Agent alone | `sub_forum_id` has a matching entry in structured norm source |
| Flag account as Tier 3 (elevated caution) | Agent flags, human notified in brief | Stripe payment tier = commercial AND account NOT in Tom's Sheet |
| Calculate and surface viral risk indicator | Agent alone | `engagement_velocity` measured over trailing 30-minute window |
| Escalate for viral risk | Agent alone | `viral_risk_flag = TRUE` → immediate Tom escalation; no brief assembly delay |
| Search Discord for precedent | Agent alone | Discord index integration is available; result surfaced in brief whether found or not |
| Draft decision rationale | Agent proposes, moderator approves | Always — agent populates template with evidence; moderator edits and decides |
| Content decision (remove / no-action / soft-warn) | Human (moderator) takes over | Always — agent may not make this call under any condition |
| Close flag in Discourse | Human (moderator) takes over | Always — agent may not close a flag |
| Discord consensus request | Human (moderator) takes over | `sub_forum_norm_conflict = TRUE` OR norm not found in structured source AND `reporter_count > 3` |

---

## Escalation Triggers

- **Tier 1 account match** (confirmed sponsor in Tom's Sheet): route to Tom immediately; no content analysis runs; SLA: instant on flag receipt
- **Tier 2 account match** (special user in Tom's Sheet): route to Tom immediately; no content analysis runs; SLA: instant on flag receipt
- **Viral risk flag = TRUE** (`engagement_velocity` exceeds configured threshold in trailing 30-minute window): route to Tom immediately; SLA: instant; do not wait for brief assembly
- **Sub-forum norm not found AND reporter count > 3**: flag for Senior Moderator before decision; SLA: [TBD — no current SLA; see Discovery Question Q1]
- **Brief assembly incomplete after [TBD minutes]** (data source unavailable): escalate to Senior Moderator with partial brief and explicit gap list; SLA: [TBD; see Discovery Question Q2]
- **Case open in moderator queue for > [TBD minutes] without decision**: escalate to Senior Moderator (addresses stakeholders_quiz Q4 failure mode — no current time-based trigger exists)
- **Stripe API unavailable AND account not in Tom's Sheet AND account has commercial-pattern indicators**: flag for human Tier 3 check before any content decision; SLA: before flag is closed

---

## Failure Modes

**1. Tier 1/2 account missing from Tom's Sheet (Sheet not updated after new sponsor onboarding)**
- Bad output: agent processes as standard case; context brief reaches volunteer moderator
- Consequence: volunteer moderator makes content decision on sponsor content; 2024 incident pattern repeated
- Recovery: agent must surface "account not found in Sheet" as an explicit brief flag when account exhibits commercial-pattern indicators (Stripe tier, posting frequency, post content); Tom must establish Sheet update cadence as part of deployment agreement

**2. Sub-forum norm not in structured source**
- Bad output: agent applies global policy threshold; norm-mismatch not visible in brief
- Consequence: wrong norm applied; community trust damage (e.g. Painters sub critique removed without "no critique without invitation" check)
- Recovery: agent must explicitly state "sub-forum norm not found — global policy threshold applied" in every brief where this occurs; moderator must manually consult Tom's tracker; this gap blocks full accuracy until structured norm source is created

**3. Discord #mod-decisions integration unavailable**
- Bad output: precedent step silently skipped; brief shows no precedent data
- Consequence: moderator makes decision without precedent context; inconsistent outcomes across cases
- Recovery: agent must explicitly flag "Discord precedent unavailable — manual check required" rather than silently omitting; do not mark brief as complete when this step was skipped

**4. Viral risk threshold miscalibrated (set too high or too low)**
- Bad output: viral posts not flagged in time (threshold too high) or routine posts escalate to Tom unnecessarily (threshold too low)
- Consequence: community damage if viral post handled by volunteer, or Tom overloaded by false escalations
- Recovery: `viral_risk_threshold` must be a named, configurable parameter (env var); Tom must confirm the value before go-live; default must be absent (agent rejects processing if unset)

**5. Tier 3 account (established commercial member) not detected**
- Bad output: account treated as standard user; brief contains no elevated-caution flag
- Consequence: content decision made without the caution warranted by community standing; potential community trust damage
- Recovery: agent must surface Stripe commercial tier flag in every brief where the account is not in Tom's Sheet but has commercial-tier Stripe payment; moderator must apply Tier 3 caution manually when flag is present; this is a known partial mitigation — Stripe tier does not map cleanly to community standing [stakeholders_quiz Q5]

---

## Governance

**Audit log fields (per case):**

| Field | Type | Notes |
|---|---|---|
| `case_id` | string | Discourse flag ID |
| `agent_run_id` | UUID | Unique per brief assembly run |
| `timestamp_brief_assembled` | UTC ISO 8601 | When brief was delivered to moderator queue |
| `account_tier_assigned` | enum: 1 / 2 / 3 / standard | Tier as determined by agent |
| `tier_source` | enum: sheet / stripe / unknown | Data source used for tier assignment |
| `sub_forum_norm_found` | boolean | Whether a structured norm entry was found |
| `viral_risk_flag` | boolean | Whether viral risk threshold was exceeded |
| `discord_precedent_found` | boolean | Whether a matching precedent was indexed |
| `brief_completeness_score` | integer 0–100 | % of data fields populated |
| `escalation_triggered` | boolean | Whether an auto-escalation fired |
| `escalation_target` | enum: tom / senior_mod / none | Named role escalated to |
| `moderator_id` | string | ID of moderator who reviewed the brief |
| `final_decision` | enum: no-action / soft-warn / remove / escalate | Moderator's decision |
| `decision_timestamp` | UTC ISO 8601 | When moderator closed the case |

**Data retention:**
- Standard cases: 90 days (aligned with Discourse moderation log retention)
- Cases involving Tier 1/2 accounts: indefinite (legal and relationship risk)
- Cases that resulted in a WS3 appeal: retained until appeal is closed + 90 days

**HITL oversight:**
- Tom reviews a random 5% sample of closed WS2 cases weekly to calibrate context brief quality and catch systematic gaps
- Any WS2 case that generates a WS3 appeal is automatically flagged for Tom review — assesses whether the agent brief contributed to the wrong decision
- Viral risk threshold reviewed monthly by Tom for the first 3 months post-deployment; quarterly thereafter

**Audit log persistence:** append one JSONL record per case to the file at `AUDIT_LOG_PATH` (defaults to `./audit.jsonl`). Write after the brief is delivered or escalation fires — not before. Non-fatal on write failure: log the error and continue processing.

---

## Implementation Specification

### Trigger / Invocation

Invoked by the WS1 automation rules engine via webhook — not directly by Discourse. [A-9]

- WS1 runs Boolean checks on `flag_created` events → routes grey-zone cases to `POST /webhook/ws2-flag`
- Validate `X-WS1-Secret` request header against `WS1_WEBHOOK_SECRET` env var; return HTTP 401 if missing or mismatched
- Server listens on `PORT` env var (default: 3000)
- **Deployment prerequisite:** WS1 automation must be operational before this agent is deployed (OI-8)

### WS1 Webhook Payload Schema

```typescript
interface WS1FlagPayload {
  flag_id: string;        // Discourse flag ID → ContextBrief.case_id
  post_id: string;        // Discourse post ID of the flagged content
  topic_id: string;       // Discourse topic/thread ID
  sub_forum: string;      // Sub-forum identifier (e.g. 'painters', 'historical', 'japanese')
  poster_handle: string;  // Account handle of the post author
  reporter_count: number; // Number of distinct users who flagged this post
  flag_type: string;      // Discourse flag category (e.g. 'inappropriate', 'spam', 'other')
  routed_at: string;      // UTC ISO 8601 — when WS1 handed off to WS2
}
```

Validate all required fields on receipt. Return HTTP 400 if any are missing. [A-14]

### LLM Usage

Three assembly steps require LLM calls — all others are deterministic:

| Step | LLM | Input | Output |
|---|---|---|---|
| Reporter signal quality assessment | Yes | Reporter comment texts | `quality_assessment` string |
| Discord precedent matching | Stub (GAP-3) | — | `{ found: false, cases: [] }` always |
| Decision rationale template generation | Yes | All assembled brief fields | `decision_rationale_template` markdown string |

Model: `claude-haiku-4-5-20251001` via Anthropic SDK (`@anthropic-ai/sdk`).

### LLM System Prompts

**Reporter signal quality assessment:**
```
You are a moderation assistant. Given a list of reporter comments from users who flagged a post, assess the overall signal quality: are these reports substantive and specific, or vague and potentially retaliatory? Return a single concise sentence (max 30 words) summarising the signal quality. Do not make a moderation recommendation.
```

**Decision rationale template generation:**
```
You are a moderation assistant. Given the structured context brief below, populate the decision rationale template with the assembled evidence. Fill in all placeholders using only the data provided — do not infer, assume, or add information not present in the brief. Leave the Decision checkboxes unchecked and the Rationale line blank for the moderator to complete.
```

### Google Sheet Column Schema

[A-16] Row 1 is a header row — skip on read. Match on `handle` (case-insensitive). Unreachable = not-found, surface in `missing_fields`.

| Column | Header | Type | Notes |
|---|---|---|---|
| A | `handle` | string | Discourse account handle |
| B | `tier` | number | `1` = sponsor; `2` = special user |
| C | `notes` | string | Free-text; surfaced in brief, not used in routing |

### Viral Risk Formula

[A-15] Engagement velocity = count of engagement events on the flagged post in the trailing 30-minute window:

```
engagement_velocity = new_replies + new_reactions + new_flags
```

Source: Discourse API (`GET /t/{topic_id}.json` for replies; `GET /posts/{post_id}.json` for reactions and flag count). Compare against `VIRAL_RISK_THRESHOLD` to set `viral_risk.flag`.

### Thread Context Depth

Fetch the last **20 posts** preceding the flagged post from the parent topic. If the thread has fewer than 20 posts, fetch all. If the flagged post is the first post, `thread_context` is an empty array.

### Brief Completeness Score

Eight equal-weight data groups (12.5 points each). A group scores 0 only when its lookup was **skipped entirely** — not when it returned null or not-found:

| # | Group | Fields | Populated when |
|---|---|---|---|
| 1 | Post content | `post.content` | Non-empty string |
| 2 | Thread context | `post.thread_context` | Array fetched (empty is valid) |
| 3 | Account tier | `account.tier`, `account.tier_source` | Tier determined from any source |
| 4 | Sub-forum norm | `sub_forum_norm.found` | Lookup attempted |
| 5 | Reporter signals | `reporter_signals.quality_assessment` | Non-empty LLM output |
| 6 | OP response | `op_response.responded` | Boolean set |
| 7 | Precedents | `precedents.found` | Stub return counts |
| 8 | Viral risk | `viral_risk.flag`, `viral_risk.engagement_velocity` | Calculation completed |

Add skipped group field names to `missing_fields`.

### Context Brief Output Format

[A-8] Primary output delivered to the moderator review queue:

```typescript
interface ContextBrief {
  case_id: string;
  assembled_at: string;                 // UTC ISO 8601

  post: {
    content: string;                    // flagged post text
    thread_context: string[];           // up to 20 preceding posts
    sub_forum: string;
  };

  account: {
    handle: string;
    tier: 1 | 2 | 3 | 'standard';
    tier_source: 'sheet' | 'stripe' | 'unknown';
    elevated_caution: boolean;          // true for Tier 1/2/3
  };

  sub_forum_norm: {
    found: boolean;
    norm_text: string | null;
    fallback_applied: boolean;          // true when global policy used
  };

  reporter_signals: {
    count: number;
    quality_assessment: string;
  };

  op_response: {
    responded: boolean;
    response_text: string | null;
  };

  precedents: {
    found: boolean;
    cases: Array<{ summary: string; decision: string; date: string }>;
  };

  viral_risk: {
    flag: boolean;
    engagement_velocity: number;
    threshold_used: number;             // value of VIRAL_RISK_THRESHOLD
  };

  escalation_flags: Array<{
    trigger: string;                    // e.g. 'TIER_1_MATCH', 'VIRAL_RISK'
    target: 'tom' | 'senior_mod';
    fired_at: string;                   // UTC ISO 8601
  }>;

  brief_completeness_score: number;     // 0–100
  missing_fields: string[];

  decision_rationale_template: string;  // pre-populated markdown for moderator
}
```

**Decision rationale template structure:** [A-11]

```markdown
## Case [case_id] — Decision Required

**Account:** [handle] | Tier: [tier] ([tier_source]) | Elevated caution: [yes/no]
**Sub-forum:** [sub_forum] | Norm: [norm_text / "Global policy applied — norm not found"]
**Reporters:** [count] | Signal: [quality_assessment]
**OP response:** [yes/no] — [response_text if present]
**Precedent:** [found/not found] — [case summaries if found]
**Viral risk:** [flag] | Velocity: [engagement_velocity] vs threshold [threshold_used]

### Decision
- [ ] No action
- [ ] Soft warn
- [ ] Remove
- [ ] Escalate to Tom

**Rationale:** [moderator completes this line before closing the case]
```

### Brief Delivery Mechanism

POST `ContextBrief` JSON to `MODERATOR_QUEUE_ENDPOINT` on assembly completion. [A-10]

Stub behaviour: if endpoint is unreachable, log to stdout with prefix `[BRIEF_STUB]`. Do not silently drop the brief.

### Tier 1/2 Escalation Delivery

On Tier 1/2 match, POST immediately to `TOM_ESCALATION_ENDPOINT` — before any content analysis. [A-12]

Payload: `{ case_id, account_handle, account_tier, tier_source, escalation_trigger, fired_at }`. No `ContextBrief` assembled for these cases.

Stub behaviour: if endpoint unreachable, log `[ESCALATION_STUB]`. Do not fall back to content analysis — treat as hard failure and halt processing for that case.

### Brief Assembly Timeout

If assembly exceeds `BRIEF_ASSEMBLY_TIMEOUT_MS` (default: 30 000 ms), deliver partial brief immediately with `missing_fields` populated, `brief_completeness_score` reflecting assembled fields only, and an `ASSEMBLY_TIMEOUT` entry in `escalation_flags`.
