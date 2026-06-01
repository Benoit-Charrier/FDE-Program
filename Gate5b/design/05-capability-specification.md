# Deliverable 5 — Production-Grade Capability Specification
**Gate 5b Final Exam · Lattice Pay AML/KYC Case Review Agent (LACRA)**
**Version:** 1.0 — Design phase. Amendment notes will be appended during build phase.

---

## 1. Purpose and scope

LACRA accepts a case alert (alert_id + customer_id) and returns a structured case package
(JSON + embedded prose narrative) to the analyst queue within 60 seconds. LACRA executes
five Jobs to be Done (brief terminology):

1. **Ingest the alert and pull the case context**
2. **Synthesise the alert into a narrative**
3. **Surface patterns**
4. **Reconcile against watchlist screening**
5. **Recommend a disposition**

Not delegated to LACRA (brief scope guardrails):
- SAR filing decision — analyst signs
- Customer freeze decision — analyst recommends; supervisor approves (two-level chain)
- Sanctions screening positive confirmation — OFAC hit is not LACRA's call to declare
- Any communication with the customer or any other party
- Out-of-scope alerts (broker-dealer / remittance product) — routed, not analysed

---

## 2. Inputs

### 2.1 Primary input

```
{
  "alert_id": "string — format CASE-YYYY-MM-DD-AML-NNNN, required",
  "customer_id": "string — format C-CON-NNNNNNN or C-BIZ-NNNNNNN, required",
  "alert_type_code": "string — rule engine code, optional (agent derives if absent)",
  "triggered_at_utc": "ISO 8601 timestamp, required",
  "monetary_scope_usd": "decimal, optional",
  "analyst_queue_tag": "string enum [Standard | High], optional"
}
```

Validation: `alert_id` and `customer_id` are required. If either is absent, return
`{"error": "MISSING_REQUIRED_FIELD", "fields": ["alert_id" | "customer_id"]}` and halt.

### 2.2 Data sources (prototype: local files; production: internal APIs)

| Source | Tool | Prototype path | Required | Graceful-degrade behaviour |
|---|---|---|---|---|
| KYC profile | `read_kyc(customer_id)` | `mock-data/kyc-profiles/{customer_id}_kyc.json` | Yes | Note missing in `data_gaps`; continue |
| 90-day transaction history | `read_transactions(customer_id)` | `mock-data/transaction-history/{customer_id}_90day.csv` | Yes | Note missing; set `patterns_detected` to partial |
| Watchlist screening report | `read_watchlist(customer_id)` | `mock-data/watchlist-screenings/{customer_id}_*_screening.txt` | No | Set `watchlist_status.resolution = "NO_SCREENING_DATA"` |
| Counterparty/network data | `read_network(customer_id)` | `mock-data/counterparty-network/{customer_id}_linked_network.json` | No | Skip network analysis; note in `data_gaps` |
| Prior RFI email threads | `read_rfi_history(customer_id)` | `mock-data/customer-rfi-emails/{customer_id}_*.eml` | No | Note missing; continue |
| OFAC SDN reference extract | `read_sanctions_extract(sdn_entry_id)` | `mock-data/sanctions-list-extracts/OFAC_SDN_{name}.txt` | Conditional (only if watchlist hit present) | If absent, set `watchlist_status.resolution = "WATCHLIST_UNRESOLVED"` |
| Linked account KYC (layering) | `read_kyc(linked_customer_id)` × N | Same pattern | No | Note which linked accounts have no KYC |

---

## 3. Processing pipeline

The agent executes the five JtDs in order. Each JtD produces a structured output passed to
the next. If any JtD fails, the failure is logged and the pipeline continues with available
data (graceful degradation).

---

### JtD-1: Ingest the alert and pull the case context

**Delegation archetype:** Fully Agentic

#### 1a — Scope detection

**Input:** `alert_type_code` + transaction history (if available)
**Logic:**
- If alert involves transactions via the remittance product (`channel = "remittance"` in
  transaction CSV, or alert_type_code contains "REMIT"), classify as `OUT_OF_SCOPE_REMITTANCE`
- If alert_type_code indicates securities/broker-dealer activity, classify as
  `OUT_OF_SCOPE_BROKER_DEALER`
- Otherwise: `IN_SCOPE`

**Output:** `scope_classification` string

**On OUT_OF_SCOPE:** Immediately return:
```json
{
  "scope_classification": "OUT_OF_SCOPE_REMITTANCE",
  "routing": { "destination": "Cross-Border Remittance Review Team", "reason": "Alert involves Lattice Pay remittance product transactions" },
  "disposition": { "recommendation": "ROUTE_OUT_OF_SCOPE" }
}
```
Halt further processing.

**Edge case:** AML-1322 (C-CON-5530118) — cross-border transfers via remittance product.
Transaction CSV shows `channel = "remittance"` OR alert_type_code contains remittance indicator.
Must be routed, not analysed.

**Edge case:** Case where primary transactions are in-scope but one counterparty transaction
uses the remittance channel. Classify as `IN_SCOPE` but note the remittance-channel transaction
in `data_gaps` as "remittance channel transaction excluded from analysis; refer to remittance team."

#### 1b — Data retrieval (parallel tool calls)

Fetch all available data sources simultaneously:
- `read_kyc(customer_id)`
- `read_transactions(customer_id)`
- `read_watchlist(customer_id)`
- `read_network(customer_id)` — if network file exists for this customer_id
- `read_rfi_history(customer_id)`

For layering cases (network file present with linked accounts):
- For each `linked_customer_id` in the network file: `read_kyc(linked_customer_id)`
  (read the linked KYC files that are available; note missing ones in `data_gaps`)

Populate `data_gaps` list with every source that returned no data.

---

### JtD-2: Synthesise the alert into a narrative

**Delegation archetype:** Agent-led + Human Oversight

**Input:** All retrieved data from JtD-1
**Output:** `narrative` string, 150–400 words

The narrative must answer:
1. Who is the customer? (KYC summary: type, tier, tenure, occupation, funding sources)
2. What triggered the alert? (Triggering rule, key transactions cited by date+amount)
3. What is the 90-day transaction profile? (Volume, counterparties, patterns)
4. What prior history exists? (Prior alerts, prior RFI threads, prior dispositions)

The narrative must cite specific data: e.g., "Customer made 8 deposits in the $4,800–$4,950
range between May 7–12 (see transactions 2026-05-07 through 2026-05-12)" not "the customer
made several deposits."

---

### JtD-3: Surface patterns

**Delegation archetype:** Agent-led + Human Oversight

**Input:** Transaction history + network data + KYC from JtD-1
**Output:** `patterns_detected` array (zero or more items)

For each pattern detected, produce one entry with `pattern_type`, `description`, `evidence`
(list of transaction citations), and `severity`.

#### 3a. Structuring

**Rule:** ≥3 transactions in a 10-day window where:
- Each transaction amount is in the range [$4,000, $9,999] (under $10K CTR threshold), AND
- ≥2 of the transactions are in the range [$4,000, $5,000] (under $5K variant threshold), AND
- The aggregate of those transactions exceeds $10,000

**Evidence format:** List each qualifying transaction as `{date} ${amount} ({channel})`
**Severity:** HIGH if ≥5 qualifying transactions; MEDIUM if 3–4

#### 3b. Layering

**Rule:** Transaction graph (from network file) shows funds moving through ≥3 hops (accounts)
before exiting to an external beneficiary, where:
- ≥3 of the intermediate accounts share a device fingerprint or IP cluster, AND
- Accounts were opened within a 30-day window, AND
- Funds converge at a single external bank account

**Evidence format:** Hop chain — `{source_account} → {intermediate} → ... → {external_account}`,
with dollar amounts and timestamps for each hop
**Severity:** HIGH

#### 3c. Velocity anomaly

**Rule:** Current 30-day cross-border outbound volume is ≥10× the prior 12-month average
outbound per 30 days.

**Calculation:** prior_avg = total_cross_border_outbound_prior_12mo / 12;
current_30d = cross_border_outbound_in_current_30d;
ratio = current_30d / prior_avg (if prior_avg = 0, flag as "no prior cross-border history")
**Severity:** HIGH if ratio ≥ 10×; MEDIUM if 5–10×

#### 3d. Counterparty risk concentration

**Rule:** ≥70% of outbound transaction value in the 90-day window goes to a single counterparty
that is either: (a) on Lattice's elevated-risk merchant list, OR (b) an offshore financial
institution (routing number resolves to a Cayman, BVI, or other high-risk jurisdiction)

**Evidence format:** Counterparty name, % of outbound volume, dollar amount, jurisdiction
**Severity:** HIGH if offshore + ≥70%; MEDIUM if elevated-risk merchant list only

#### 3e. Thin KYC + volume mismatch

**Rule:** `kyc_verification_tier = 1` AND aggregate inbound in rolling 30 days exceeds
$25,000 (the Tier-1 limit)

**Evidence format:** KYC tier, aggregate inbound amount, limit, overage amount
**Severity:** HIGH

#### 3f. Multi-pattern convergence

If ≥2 patterns are detected simultaneously, add a synthetic entry:
`pattern_type: "MULTI_PATTERN_CONVERGENCE"` with description noting the co-occurring patterns.
Severity: HIGH.

---

### JtD-4: Reconcile against watchlist screening

**Delegation archetype:** Agent-led + Human Oversight (disconfirmation only)

**Input:** Watchlist screening report + OFAC SDN extract (if hit present) + KYC profile
**Output:** `watchlist_status` object

**If no hit in screening report:**
`{ "hit_present": false, "resolution": "NO_HIT", "confidence": 1.0 }`

**If hit present, apply disconfirmation criteria in order:**

1. **DOB check:** If customer DOB differs from SDN entry DOB by ≥5 years → strong
   disconfirmation factor. Note delta.
2. **Address check:** If customer address country differs from SDN entry known country →
   disconfirmation factor. Note mismatch.
3. **Nationality check:** If customer nationality/citizenship (from KYC) differs from SDN
   entry nationality → disconfirmation factor.
4. **Transaction profile coherence:** If customer transaction profile is consistent with
   stated occupation and expected volume (e.g., student stipend pattern) → disconfirmation
   factor.

**Disconfirmation rule:**
- ≥3 disconfirmation factors present → `WATCHLIST_DISCONFIRMED`, confidence = 0.9–1.0
- 2 disconfirmation factors present → `WATCHLIST_DISCONFIRMED`, confidence = 0.7–0.89;
  add uncertainty flag: "Analyst should verify [weakest factor]"
- 1 or 0 disconfirmation factors → `WATCHLIST_UNRESOLVED`; disposition must be
  `FURTHER_INFO_NEEDED` or `ESCALATE_SAR`; never `CLEAR`

**Hard constraint:** LACRA must never output `WATCHLIST_CONFIRMED`. Sanctions screening
positive confirmation is not delegated to the agent (brief scope guardrail). The output
vocabulary is: `{ "resolution": "NO_HIT" | "WATCHLIST_DISCONFIRMED" | "WATCHLIST_UNRESOLVED" }` only.

---

### JtD-5: Recommend a disposition

**Delegation archetype:** Human-led + Agent Support (agent produces recommendation; analyst decides and signs)

**Input:** Patterns detected (JtD-3) + watchlist status (JtD-4) + KYC + data gaps (JtD-1)
**Output:** `disposition` object (recommendation only — not a decision)

**Decision logic (evaluated in priority order):**

1. If `scope_classification` is OUT_OF_SCOPE → `ROUTE_OUT_OF_SCOPE` (handled in JtD-1)

2. If `watchlist_status.resolution = "WATCHLIST_UNRESOLVED"` → `FURTHER_INFO_NEEDED`
   (never clear a case with an unresolved watchlist hit)

3. If `pattern_type = "LAYERING"` OR `pattern_type = "MULTI_PATTERN_CONVERGENCE"` with
   severity HIGH → `ESCALATE_SAR`

4. If `pattern_type = "STRUCTURING"` with severity HIGH (≥5 qualifying transactions) →
   `ESCALATE_SAR`

5. If `pattern_type = "THIN_KYC"` with `kyc_verification_tier = 1` AND over limit →
   `ACCOUNT_FREEZE` recommendation. Note: freeze itself is not delegated — analyst
   recommends to supervisor; supervisor approves (two-level chain per brief scope guardrail).

6. If `pattern_type = "COUNTERPARTY_RISK"` with severity HIGH (offshore + ≥70%) →
   `ESCALATE_SAR`

7. If `pattern_type = "STRUCTURING"` with severity MEDIUM, OR `pattern_type =
   "COUNTERPARTY_RISK"` with severity MEDIUM → `CUSTOMER_RFI`

8. If no patterns detected AND `watchlist_status.resolution = "WATCHLIST_DISCONFIRMED"` AND
   no data gaps on critical fields → `CLEAR`

9. If data gaps are present on KYC or transaction history (both missing) → `FURTHER_INFO_NEEDED`

10. Default (patterns detected but insufficient for escalation threshold) → `CUSTOMER_RFI`

**Confidence scoring:**
- `CLEAR` with full data + ≥3 disconfirmation factors: 0.95
- `ESCALATE_SAR` with HIGH severity pattern: 0.85–0.95
- `CUSTOMER_RFI` with MEDIUM severity pattern: 0.65–0.80
- `FURTHER_INFO_NEEDED` any: 0.50
- Any case with data gaps: subtract 0.10 from confidence; add data gap to uncertainty_flags

**Reasoning field:** Must cite specific evidence. Minimum: name the pattern(s), cite 2+
specific transaction amounts/dates, reference watchlist resolution with evidence. Must not
reference outputs not produced by JtD-2 through JtD-4.

---

## 4. Output schema (full)

See ADR-003 for top-level schema. All fields are required in the output unless marked optional.

**Required fields in all outputs:**
- `case_id`, `customer_id`, `alert_id`, `generated_at_utc`, `agent_version`
- `scope_classification`
- `disposition` (always present; `ROUTE_OUT_OF_SCOPE` for out-of-scope cases)

**Required for in-scope cases only:**
- `narrative`, `patterns_detected`, `watchlist_status`, `data_gaps`

**Optional:**
- `routing` (only for out-of-scope cases)

---

## 5. Governance and audit

### 5.1 Audit log entry (written for every case processed)

```json
{
  "audit_id": "UUID",
  "case_id": "string",
  "customer_id": "string",
  "alert_id": "string",
  "processed_at_utc": "ISO 8601",
  "agent_version": "string",
  "disposition_recommendation": "string",
  "confidence": "decimal",
  "processing_duration_ms": "integer",
  "data_sources_accessed": ["string"],
  "data_gaps": ["string"]
}
```

The audit log entry contains NO raw PII (no customer name, DOB, address, account number).
The full case package JSON (which contains PII in the narrative) is stored separately in the
case management system under Lattice's standard data retention policy.

### 5.2 Retention

- Audit log entries: 7 years (BSA record-keeping requirement, 31 USC § 5318)
- Full case package JSON: retained per Lattice's internal data retention policy (minimum 5 years per BSA)
- Context window: not persisted; cleared after each case

### 5.3 Reproducibility

- All model calls use `temperature=0`
- System prompt is version-controlled; `agent_version` field in output references the exact system prompt version
- Given identical inputs and identical `agent_version`, the output must be identical
- Re-run test: feed the same alert twice; diff the output JSON; expect zero diff on all fields
  except `generated_at_utc` and `audit_id`

### 5.4 Human override

- Analyst may override any disposition recommendation; override is logged with analyst_id,
  reason, and timestamp in the case management system
- An overridden disposition is not a LACRA failure — it is expected and healthy
- Aggregate override rate by disposition type is a monitoring metric; high override rate on a
  specific disposition type triggers a spec review

---

## 6. Error handling

| Error condition | Agent behaviour |
|---|---|
| Data source unavailable (file not found / API timeout) | Log to `data_gaps`; continue pipeline with remaining data |
| Both KYC and transaction history missing | Return `disposition.recommendation = "FURTHER_INFO_NEEDED"`, `confidence = 0.3`; list both in `data_gaps` |
| Invalid input (missing required fields) | Return error JSON immediately; do not process |
| Model generation failure / timeout | Retry once with 5-second backoff; if second failure, return `{"error": "AGENT_PROCESSING_FAILURE", "case_id": "...", "retry_recommended": true}` |
| Linked account count > 10 in network file | Process first 10 linked accounts; note truncation in `data_gaps`; proceed |

---

## 7. Tool interfaces (prototype implementation)

### `read_kyc(customer_id: str) → dict | None`
Reads `mock-data/kyc-profiles/{customer_id}_kyc.json`. Returns parsed JSON or None if not found.

### `read_transactions(customer_id: str) → list[dict] | None`
Reads `mock-data/transaction-history/{customer_id}_90day.csv`. Returns list of row dicts or None.

### `read_watchlist(customer_id: str) → str | None`
Reads `mock-data/watchlist-screenings/{customer_id}_*_screening.txt` (glob). Returns file
content as string or None.

### `read_network(customer_id: str) → dict | None`
Reads `mock-data/counterparty-network/{customer_id}_linked_network.json`. Returns parsed JSON
or None.

### `read_rfi_history(customer_id: str) → str | None`
Reads `mock-data/customer-rfi-emails/{customer_id}_*.eml` (glob). Returns concatenated content
or None.

### `read_sanctions_extract(sdn_entry_name: str) → str | None`
Reads `mock-data/sanctions-list-extracts/OFAC_SDN_{sdn_entry_name}.txt`. Returns content or None.

---

## 8. Assumptions register

| ID | Assumption | Why it matters | If wrong | Status |
|---|---|---|---|---|
| A1 | Watchlist screening is pre-computed per case | Agent reads the report; does not call OFAC API | Must add OFAC API tool; PII constraint re-evaluated | Assumed — confirm with compliance team |
| A2 | Transaction CSV always has the 8-column schema (Date, Time_UTC, Direction, Type, Counterparty, Amount_USD, Channel, Balance_After) | Structuring and velocity pattern detection depend on column names | Parser must be made schema-flexible | Assumed from mock data |
| A3 | Linked account KYC files exist for primary account only; linked accounts may lack files | Agent must handle missing linked KYC gracefully | Layering cases may under-analyse | Confirmed from mock data (AML-1408 has 4 linked accounts but only 1 KYC file in mock set) |
| A4 | Temperature = 0 is sufficient for 100% reproducibility | FinCEN/audit requirement | Must implement deterministic output validation (diff-check on re-run) | Assumed — to be validated in build phase |
| A5 | Anthropic enterprise DPA constitutes safe harbour for PII processing | William Akoto's PII constraint | Must seek alternative in-perimeter model deployment | Assumed — confirm with legal/procurement |
| A6 | AML-1322 cross-border transfers are via the remittance product (channel = "remittance") | Scope detection in Step 1 | If channel is unmarked, agent may analyse instead of route | Verify with Engineering |
