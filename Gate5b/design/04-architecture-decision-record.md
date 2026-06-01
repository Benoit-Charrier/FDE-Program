# Deliverable 4 — Architecture Decision Records
**Gate 5b Final Exam · Lattice Pay AML/KYC Case Review**

---

## ADR-001: Single agent vs. multi-agent pipeline

**Date:** 2026-06-01
**Status:** Accepted

### Context

The AML case review workflow has five distinct cognitive zones: context retrieval, narrative
synthesis, pattern detection, watchlist reconciliation, and disposition generation. Each zone
has different data dependencies, reasoning complexity, and failure modes. Two architectural
options exist: (1) a single monolithic agent that performs all zones in sequence, or (2) a
pipeline of specialist sub-agents coordinated by an orchestrator.

### Decision

**Single orchestrator with inline specialist prompting** — the orchestrator agent executes all
five cognitive zones sequentially using tool calls for data retrieval and structured sub-prompts
for each reasoning zone. No separate agent processes; one LLM call chain per case.

### Rationale

- **Volume and latency:** 11,000 alerts/week requires sub-60-second case package generation.
  Multi-agent coordination (spawning sub-agents, aggregating results) adds latency and
  complexity without corresponding accuracy benefit for this use case.
- **Context coherence:** Each reasoning zone benefits from having the full prior context
  (KYC + transactions + watchlist + network) available simultaneously. A monolithic context
  window with all retrieved data is superior to siloed sub-agents that must pass state between
  themselves for this type of synthesis task.
- **Reproducibility:** Single-agent execution with temperature=0 is simpler to reproduce
  deterministically than a multi-agent graph where small coordination variances compound.
- **Prototype scope:** A clean single-agent pipeline is buildable in the 3-hour build window;
  a multi-agent orchestration framework is not.

### Tradeoffs accepted

- The full context window per case will be large (~15K–20K tokens). This is an accepted cost
  given the token economics (see ADR-003 and Economics sketch).
- Future evolution toward specialist sub-agents (e.g., a dedicated network analysis agent for
  complex layering cases) is structurally possible — the tool interface is designed to be
  extractable.

### Rejected alternative

**Multi-agent pipeline** (orchestrator + KYC agent + transaction agent + watchlist agent):
adds inter-agent communication overhead, context serialisation cost, and coordination failure
modes without improving accuracy for the synthesis task at hand. Appropriate for Wave 2 when
alert volume justifies dedicated specialist routing.

---

## ADR-002: Model selection

**Date:** 2026-06-01
**Status:** Accepted

### Context

Model selection affects: accuracy of pattern detection, cost per case, latency, and — critically
for Lattice Pay — reproducibility and explainability. Three tiers are available: frontier
(Claude Opus), mid-tier (Claude Sonnet), and fast (Claude Haiku).

### Decision

**Claude Sonnet (claude-sonnet-4-6) for all reasoning zones.** No model routing or fallback to
a cheaper model for any case type in the prototype.

### Rationale

- **Accuracy requirement:** SAR recall ≥ 95% demands high-quality multi-step reasoning over
  mixed-format data (JSON + CSV + text in a single context window). Haiku's reasoning quality
  is insufficient for the pattern detection and watchlist reconciliation zones.
- **Cost:** At mid-tier pricing (~$3/$15 per 1M input/output tokens), a 20K-token case
  costs ~$0.09 in model cost — well within economics (see Economics sketch).
- **Reproducibility:** Sonnet at temperature=0 produces highly stable outputs. Confirmed
  sufficient for FinCEN explainability requirements.
- **Frontier not required:** Opus would add ~5× cost (~$0.45/case) for marginal reasoning
  improvement. The pattern types in this domain (structuring intervals, layering hops, DOB
  delta) are well within Sonnet's reliable reasoning range.
- **PII constraint satisfied:** Claude API (Anthropic) is contractually safe-harboured for
  enterprise PII processing — satisfies William Akoto's constraint given appropriate DPA.

### Tradeoffs accepted

- Sonnet is more expensive than Haiku. At 572K cases/year, model cost is ~$52K/year —
  acceptable vs. $3.72M baseline human cost.
- If Anthropic changes Sonnet pricing or model behaviour significantly, re-evaluation is
  required. Token economics must be re-run annually (see Economics governance section).

### Rejected alternative

**Haiku for retrieval zones + Sonnet for reasoning zones:** model routing reduces cost ~30%
but adds coordination complexity and a potential consistency failure if the cheap model
misformats retrieved data for the reasoning model. Not worth the complexity in the prototype;
revisit in Wave 2.

---

## ADR-003: Output format — structured JSON case package + prose narrative

**Date:** 2026-06-01
**Status:** Accepted

### Context

The case package must serve two consumers: (1) the analyst reviewing it in a UI, who needs
prose they can read quickly and challenge, and (2) the case management system, which needs
structured fields for logging, audit, and reproducibility.

### Decision

**Dual output:** The agent produces a structured JSON case package (machine-readable, loggable,
reproducible) that includes an embedded `narrative` field containing human-readable prose.
Both are returned in a single response.

### Schema (top-level)

```json
{
  "case_id": "string",
  "customer_id": "string",
  "alert_id": "string",
  "generated_at_utc": "ISO 8601",
  "agent_version": "string",
  "scope_classification": "IN_SCOPE | OUT_OF_SCOPE_REMITTANCE | OUT_OF_SCOPE_BROKER_DEALER",
  "narrative": "string (prose summary, 150–400 words)",
  "patterns_detected": [
    {
      "pattern_type": "STRUCTURING | LAYERING | VELOCITY_ANOMALY | COUNTERPARTY_RISK | WATCHLIST | THIN_KYC | OTHER",
      "description": "string",
      "evidence": ["transaction_id or field citation"],
      "severity": "LOW | MEDIUM | HIGH"
    }
  ],
  "watchlist_status": {
    "hit_present": true | false,
    "resolution": "WATCHLIST_DISCONFIRMED | WATCHLIST_UNRESOLVED | NO_HIT",
    "disconfirmation_evidence": ["string"],
    "confidence": 0.0–1.0
  },
  "disposition": {
    "recommendation": "CLEAR | ESCALATE_SAR | CUSTOMER_RFI | ACCOUNT_FREEZE | FURTHER_INFO_NEEDED",
    "reasoning": "string",
    "confidence": 0.0–1.0,
    "supporting_transactions": ["transaction_id"],
    "uncertainty_flags": ["string"]
  },
  "data_gaps": ["string"],
  "routing": null | { "destination": "string", "reason": "string" }
}
```

### Rationale

- JSON schema enables deterministic comparison for reproducibility testing
- Embedded narrative allows analyst UI to display human-readable output without extra generation
- `evidence` and `supporting_transactions` fields make every claim citable — satisfies FinCEN explainability
- `data_gaps` field is explicit rather than silent — analyst knows what's missing
- `uncertainty_flags` field invites scrutiny (Diane Reston's "argue with it" requirement)
- `agent_version` field enables audit trail reconstruction

---

## ADR-004: PII handling — in-memory only, no persistence of raw customer data

**Date:** 2026-06-01
**Status:** Accepted

### Context

William Akoto's constraint: no raw customer data to third-party APIs without contractual
safe harbour. The agent processes PII (names, addresses, DOBs, account numbers, transaction
data) from Lattice's internal systems.

### Decision

1. **Model API:** Use Anthropic Claude API only. Anthropic's enterprise DPA constitutes the
   required safe harbour for PII processed by the model. Raw customer data is transmitted to
   the Anthropic API only during active case processing; it is not stored by Anthropic beyond
   the API call lifecycle under the enterprise DPA.
2. **Prototype:** All data is processed from local mock files. No external API calls in the
   prototype.
3. **Production:** Data retrieval tools call internal Lattice APIs only. The agent orchestrator
   runs inside Lattice's infrastructure perimeter.
4. **Logging:** Case packages logged to the internal audit store contain `customer_id` and
   `alert_id` as identifiers; they do not contain raw PII fields (name, DOB, address) in the
   audit log — only the case package JSON with citations to transaction IDs.
5. **Context window:** PII is present in the model's context window during processing and
   nowhere else. Context is not cached across cases.

### Rationale

Minimises PII surface area while enabling the agent to reason over customer data for the
duration of the case. Satisfies William Akoto's constraint by treating Anthropic's enterprise
DPA as the safe harbour instrument.

### Tradeoffs accepted

- Anthropic API dependency for PII processing. If Lattice moves to a fully on-premise model
  in the future, this ADR must be revisited.
- No cross-case context caching means each case re-processes KYC data from scratch. This is
  the correct choice for both privacy and reproducibility.
