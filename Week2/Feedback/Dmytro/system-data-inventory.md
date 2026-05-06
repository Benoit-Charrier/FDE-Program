# System / Data Inventory — MiniBase Community Moderation Agent

Primary agent: WS2 Grey-Zone Context Agent. Where a system is also required by WS1 automation or WS3 agent support, it is marked **shared** — these are compounding opportunities where a single integration serves multiple work streams.

---

## Inventory

| System / Source | Data needed | Access type | Availability | Gap / Risk |
|---|---|---|---|---|
| **Discourse REST API** | Flagged post content; full thread context; reporter comments + count; user account age; prior violation history; engagement activity (reactions, replies) | REST API read + flag management write | High | Engagement velocity calculation (viral risk) may require polling activity endpoints rather than a native stream — latency risk for real-time viral detection. **Shared**: WS1 automation, WS3 agent support. |
| **Tom's Google Sheet — account tiers** | Tier 1 (confirmed sponsor) and Tier 2 (special user) account handles + routing rules | Google Sheets API read-only | Medium | (1) Sheet is not a database — no schema enforcement, no webhook on update; agent reads a snapshot, not live state. (2) Staleness risk: new sponsors onboarded without updating Sheet reproduce the 2024 incident. (3) No Tier 3 accounts in Sheet — Tier 3 is a MISSING data source (see Critical Gaps). **Shared**: WS1 automation, WS3 agent support. |
| **Stripe API — payment tier** | Commercial account status for a given user (Tier 3 fallback detection) | REST API read-only | Medium | **Critical dependency: Discourse user ID → Stripe customer ID mapping does not exist as a confirmed structured source.** Without this mapping, Stripe tier cannot be retrieved for a given moderator-identified user. See Critical Gaps. |
| **Sub-forum norm source** | Per-sub-forum content norms: Painters ("no critique without invitation"), Historical (permissive on charged imagery), Japanese painters sub (soft-warn before removal); any additional sub-forum norms in Tom's tracker | Structured read (database, config file, or Sheet) | MISSING | Currently lives in Tom's private tracker. No queryable source exists. Agent cannot apply norm-aware triage without this. **Deployment blocker** — see Critical Gaps. |
| **Discord #mod-decisions channel — precedent index** | Prior moderation decisions indexed by sub-forum + report type, searchable by case pattern | Discord API read + semantic search index | Low | Discord API can retrieve messages but has no semantic search. Precedent lookup requires a separate indexing pipeline (e.g. periodic export + vector index). Without it, agent must flag "precedent unavailable" explicitly in every brief. Not a deployment blocker but significantly limits brief quality. |
| **Engagement velocity calculator** | Post engagement rate over trailing 30-minute window (reactions + replies delta) for viral risk signal | Derived from Discourse activity API or webhook stream | Medium | Real-time 30-minute rolling window requires either a streaming webhook or a polling interval ≤5 min. Native Discourse API is request/response — a lightweight polling service or webhook listener is needed. `VIRAL_RISK_THRESHOLD` must be a named env var confirmed by Tom before deployment. |
| **Global 14-page moderation policy** | Policy text for WS3 policy-check step (compounding use) | Static document read | High | Policy is a static document — no API needed. Must be re-ingested whenever policy is updated. Version tracking required (agent must operate on a known policy version). **Shared**: WS3 agent support. |

---

## Critical Gaps

### GAP-1: Sub-forum norm structured source — MISSING — **Quality blocker for norm-sensitive sub-forums**

**What the APD requires:** agent retrieves the applicable sub-forum norm for the flagged post's sub-forum before assembling the context brief.

**Current state:** norms live in Tom's private tracker (described in stakeholders_quiz Q2). No structured, queryable source exists. The three confirmed norms (Painters, Historical, Japanese sub) are known, but the full set is unknown.

**What it would take to create:**
1. Tom exports all sub-forum norm entries from his tracker into a structured format (minimum: sub-forum ID → norm text → action threshold)
2. Source is stored in a queryable location (a dedicated Sheet tab, config file, or lightweight database table)
3. Agent reads from this source on each case; human-maintained update process established

**Impact if not resolved before deployment:** agent flags "norm not found — global policy applied" on every norm-sensitive case, degrading brief quality for Painters, Historical, and Japanese painters sub-forums. V1 deployment is possible — the APD failure mode #2 handles the absence explicitly — but brief quality for norm-sensitive cases will be materially lower until resolved. **Quality blocker for norm-sensitive sub-forums, not a hard deployment blocker.**

---

### GAP-2: Discourse → Stripe user identity mapping — MISSING or unknown — **Quality blocker for Tier 3 detection**

**What the APD requires:** for accounts not in Tom's Sheet, agent checks Stripe payment tier as a Tier 3 (established commercial member) fallback signal.

**Current state:** it is unknown whether a Discourse user ID → Stripe customer ID mapping exists. MiniBase uses Stripe for payments, but the link between a community account and a Stripe customer record is not confirmed as a structured, accessible data source.

**What it would take to create:**
- If the mapping exists (e.g. in a user database table or via shared email): confirm the join key and expose a read endpoint
- If no mapping exists: either build a registration-time link or scope Tier 3 detection out of v1 and rely solely on moderator institutional knowledge

**Impact if not resolved before deployment:** Tier 3 detection falls back to "moderator recognises the account" — which is exactly the undocumented process the agent was meant to surface. Agent brief will include a Stripe flag field populated as "unknown" for all non-Sheet accounts, requiring moderator to apply Tier 3 caution manually. V1 deployment is possible with this degradation — the APD failure mode #5 handles the absence explicitly. **Quality blocker for Tier 3 detection, not a hard deployment blocker.**

---

### GAP-3: Discord precedent index — Low availability — **Not a deployment blocker; limits brief quality**

**What the APD requires:** agent searches Discord #mod-decisions for precedent cases matching the current case's sub-forum and report type.

**Current state:** Discord API can retrieve raw messages but has no semantic search. A full precedent lookup would require scrolling the channel history manually — not feasible for an agent at 360 cases/day.

**What it would take to create:**
- Periodic export of #mod-decisions messages (daily or on new post)
- Embedding + vector index (e.g. pgvector, Pinecone, or equivalent)
- Similarity search on sub-forum + report pattern at brief assembly time

**Impact if not resolved before deployment:** agent flags "Discord precedent unavailable — manual check required" in every brief. Moderator preparation time savings are reduced but not eliminated — context assembly for all other fields still delivers value. Precedent indexing is a post-go-live enhancement, not a requirement for initial deployment.

---

## Environment Variables

All variables required unless marked optional. Agent must refuse to start if a required variable is unset.

| Variable | Required | Notes |
|---|---|---|
| `DISCOURSE_BASE_URL` | Yes | Base URL of the MiniBase Discourse instance |
| `DISCOURSE_API_KEY` | Yes | Discourse API key with moderator read access |
| `DISCOURSE_API_USERNAME` | Yes | Discourse username for API authentication |
| `GOOGLE_SHEET_ID` | Yes | ID of Tom's Google Sheet (Tier 1/2 list) |
| `GOOGLE_SERVICE_ACCOUNT_CREDENTIALS` | Yes | JSON string; Google service account with Sheet read access |
| `STRIPE_API_KEY` | Yes (stub if OI-4 unresolved) | Stripe restricted key with customer read access |
| `ANTHROPIC_API_KEY` | Yes | Anthropic API key for LLM assembly steps |
| `VIRAL_RISK_THRESHOLD` | Yes — no default | Agent rejects processing if unset (see OI-6) |
| `MODERATOR_QUEUE_ENDPOINT` | Yes (stub) | URL to POST completed `ContextBrief` to (see A-10) |
| `TOM_ESCALATION_ENDPOINT` | Yes (stub) | URL to POST Tier 1/2 and viral risk escalations to (see A-12) |
| `WS1_WEBHOOK_SECRET` | Yes | Shared secret validating inbound WS1 requests via `X-WS1-Secret` header |
| `AUDIT_LOG_PATH` | No | JSONL audit log path; defaults to `./audit.jsonl` |
| `BRIEF_ASSEMBLY_TIMEOUT_MS` | No | Assembly timeout in ms; defaults to 30000 |
| `PORT` | No | HTTP server port; defaults to 3000 |

---

## Compounding Opportunities

The following systems are shared across work streams — a single integration serves multiple agents:

| System | Used by | Compounding value |
|---|---|---|
| Discourse REST API | WS1 automation + WS2 agent + WS3 agent support | One API integration + auth setup serves all three work streams |
| Tom's Google Sheet (account tiers) | WS1 automation + WS2 agent + WS3 agent support | Exception routing logic built once, reused across all three |
| Global policy document | WS2 agent (sub-forum norm context) + WS3 agent support (policy check) | Same document ingestion pipeline serves both |

Building WS2 agent first establishes the Discourse integration and Sheet lookup that WS1 automation and WS3 agent support both depend on. WS1 and WS3 are lower-cost increments once WS2 integration is live.
