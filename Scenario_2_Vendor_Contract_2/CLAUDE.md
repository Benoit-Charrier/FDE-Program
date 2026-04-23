# Claude Build Brief — Full Build: Inbound Vendor Contract Review Agent

## Goal

Build a **console application** that is a complete, working implementation of the Inbound Vendor Contract Review Agent covering all 12 functional requirements (FR-01 through FR-12).

The application runs from the terminal. Given a folder of vendor contracts, it ingests each file, extracts the seven playbook clause families, classifies each clause, routes contracts to the correct queue, generates draft redlines from approved playbook language only, enforces a hard release gate requiring named-lawyer sign-off before any negotiated package can be released, logs all actions to an audit trail, and produces a **single HTML report** summarising the full analysis. The HTML report is the primary human-facing output of every analysis run.

---

## Source of Truth

[3 Capability specification.md](3%20Capability%20specification.md) is the primary requirements document.
Supporting context: [1 Problem statement and success metrics.md](1%20Problem%20statement%20and%20success%20metrics.md), [2 Delegation analysis.md](2%20Delegation%20analysis.md), [4 Validation design.md](4%20Validation%20design.md), [5 Assumptions %26 unknowns.md](5%20Assumptions%20%26%20unknowns.md).

Any conflict between this file and the spec resolves in favour of this file. Document unresolved conflicts in `docs/assumptions-log.md`.

---

## Requirements Coverage

| ID | Requirement summary | Module |
|----|--------------------|---------| 
| FR-01 | Ingest PDF/DOCX up to 40 pages, structured text with page refs, graceful errors | `ingestion.py` |
| FR-02 | Extract 7 clause families — text, page, confidence score | `extraction.py` |
| FR-03 | Compare clauses to playbook → `match` / `negotiable_deviation` / `escalate` + reason code | `classification.py` |
| FR-04 | Route contract to `standard` / `playbook_negotiable` / `senior_lawyer_escalation` with rationale | `routing.py` |
| FR-05 | Generate redlines from approved playbook fallback language only | `redlines.py` |
| FR-06 | When no approved fallback exists, escalate — never invent language | `redlines.py` + `classification.py` |
| FR-07 | Block outbound release until named-lawyer sign-off recorded per negotiated clause | `approval.py` + `release.py` |
| FR-08 | Append-only audit log of every action and human override | `audit.py` |
| FR-09 | All thresholds, jurisdictions, and playbook positions configurable via `config/playbook.json` — no legal values in code | `classification.py` reads config |
| FR-10 | Metrics: turnaround by queue, route distribution, escalation rate, override rate, approval latency | `metrics.py` |
| FR-11 | Confidence below threshold → `senior_lawyer_escalation`, not silent pass | `classification.py` |
| FR-12 | Human-readable review packet per contract: metadata, clause results, routing, redlines | `report.py` (HTML) |

---

## Architecture

### System Overview

The system is a **console application** — no GUI, no web server. All interaction happens in the terminal. The HTML report is a generated output file, not an interactive interface.

Three CLI commands cover the full workflow:

1. **`python run.py`** — Analyse all contracts in the input folder, write results to `data/`, generate the HTML report. This is the main command users run.
2. **`python approve.py`** — Record a named-lawyer approval for a specific clause in a specific contract. Prints confirmation to the console.
3. **`python release.py`** — Attempt outbound release of a contract's negotiated package; prints `[CLEARED]` or `[BLOCKED]` to the console and enforces the approval gate.

No web server. No database. State is stored as JSON files in `data/`. The HTML report (`report.html`) is regenerated on every `run.py` call and is the sole output artifact presented to legal reviewers.

### Data Flow

```
Input contract/
    └── [PDF/DOCX files]
         │
         ▼
    ingestion.py       → Page objects (text + page number)
         │
         ▼
    extraction.py      → ClauseResult × 7 (text, page, confidence, found)
         │
         ▼
    classification.py  → ClauseClassification × 7 (+ status, reason_code, rationale)
         │
         ├──[playbook_negotiable]──▶ redlines.py → RedlineProposal × N
         │
         ▼
    routing.py         → RoutingDecision (queue, rationale)
         │
         ▼
    audit.py           → data/audit.jsonl  (every step logged)
    data/              → data/analysis_results.json (persisted per contract)
         │
         ▼
    report.py          → report.html
```

Approval flow (separate CLI):
```
approve.py  →  approval.py  →  data/approvals.json  →  audit.py
release.py  →  approval.py  →  checks data/approvals.json  →  CLEARED or BLOCKED
```

---

## Module Specifications

### `ingestion.py`

**Input**: file path (str)
**Output**: `IngestionResult` — either a list of `Page(page_number: int, text: str)` or an `IngestionError(filename, reason)`

Rules:
- PDF: use `pdfplumber`. Extract text page by page. Preserve page numbers (1-based).
- DOCX: use `python-docx`. No native page breaks — approximate page number using word-count heuristic: every 350 words = 1 new page, starting at page 1.
- If the file is corrupted, password-protected, or raises any exception during parsing → return `IngestionError` with `reason = "parse_error"`. Do not raise.
- If the document exceeds 40 pages → return `IngestionError` with `reason = "exceeds_page_limit"`.
- Other file extensions → not called; the CLI skips them upstream.
- Log every ingestion attempt and outcome to `audit.py` with event type `ingestion`.

---

### `extraction.py`

**Input**: list of `Page` objects, contract metadata
**Output**: list of 7 `ClauseResult` objects

Rules:
- Use the Claude API with model `claude-haiku-4-5-20251001` and `temperature=0`.
- Send the full document text in a single prompt. Use prompt caching (`cache_control: {"type": "ephemeral"}`) on the document text block to reduce cost on re-runs.
- The prompt must instruct the model to:
  - Return exactly one JSON object per clause family.
  - Extract verbatim text — no paraphrasing, no summarising.
  - Return an empty string `""` for `extracted_text` if the clause is not found — never hallucinate.
  - Return a float 0.0–1.0 for `confidence` reflecting how certain it is the extracted text actually corresponds to the clause family.
- Parse the model's JSON response into 7 `ClauseResult` objects:
  - `family`: `liability_cap` | `dpa` | `termination` | `ip_ownership` | `sla` | `governing_law` | `indemnity`
  - `extracted_text`: str
  - `source_page`: int or `null`
  - `confidence`: float
  - `found`: bool (`false` if `extracted_text` is empty)
- If the model call fails (API error, malformed JSON) → return 7 `ClauseResult` objects all with `found=false`, `confidence=0.0`, and log the error to audit with event type `extraction_error`.
- Log successful extraction to audit with event type `extraction`.

---

### `classification.py`

**Input**: list of `ClauseResult` objects, loaded playbook config
**Output**: list of `ClauseClassification` objects (extends `ClauseResult` with `status`, `reason_code`, `rationale`)

Classification logic applied in this order per clause:

1. **Confidence gate** (FR-11): if `confidence < playbook.min_confidence_threshold` → `escalate`, `reason_code = "low_confidence"`. Stop. Do not proceed to playbook comparison.
2. **Missing clause gate**: if `found == false` and playbook marks this family `required: true` → `escalate`, `reason_code = "missing_mandatory_clause"`. Stop.
3. **Missing optional clause**: if `found == false` and `required: false` → `match`, `reason_code = "optional_clause_absent"`. (No escalation for absent optional clauses.)
4. **Jurisdiction check** (governing_law only): if the jurisdiction named in the text is not in `accepted_jurisdictions` → `escalate`, `reason_code = "unapproved_jurisdiction"`. If jurisdiction is accepted → `match`, `reason_code = "playbook_match"`. Stop.
5. **Accepted position check**: semantic similarity against `accepted_positions`. If match → `match`, `reason_code = "playbook_match"`. **This step runs before escalation triggers.** A clause that matches an accepted position is not evaluated against triggers — doing so causes false escalations when clause text shares surface vocabulary with a trigger phrase but is legally compliant (e.g. "work for hire owned by company" matching a trigger aimed at vendor-assigned IP).
6. **Escalation trigger check**: semantic similarity via Haiku API (`temperature=0`) against `escalation_triggers`. Only reached if step 5 found no accepted position. If match → `escalate`, `reason_code = "escalation_trigger_matched"`.
7. **Negotiable deviation check**: semantic similarity against `negotiable_deviations`. If match → `negotiable_deviation`, `reason_code = "approved_fallback_available"`.
8. **No playbook entry**: none of the above matched → `escalate`, `reason_code = "no_playbook_entry"`.

The classification outcome is determined by these rules. The LLM is used only for semantic similarity evaluation in steps 4, 6, and 7 — it does not directly decide the status.

Log classification results to audit with event type `classification`.

---

### `routing.py`

**Input**: list of `ClauseClassification` objects
**Output**: `RoutingDecision(queue, clause_rationale, routing_reason)`

Routing rules (deterministic, in order):
1. If **any** clause has `status == "escalate"` → `queue = "senior_lawyer_escalation"`.
2. Else if **any** clause has `status == "negotiable_deviation"` → `queue = "playbook_negotiable"`.
3. Else → `queue = "standard"`.

`clause_rationale` = list of `{family, status, reason_code, rationale}` for all 7 clauses.
`routing_reason` = one sentence explaining the queue choice, citing the specific trigger clause(s).

The routing decision is written to the audit log and the analysis results immediately — there is no human acceptance step. Routing is a deterministic code decision, not a recommendation. Legal ops may spot-check routing decisions on a sample basis during calibration; that is a monitoring activity external to the system.

Log routing decision to audit with event type `routing`.

---

### `redlines.py`

**Input**: list of `ClauseClassification` objects, loaded playbook config
**Output**: list of `RedlineProposal` objects — only for `playbook_negotiable` contracts

Called only when `routing.queue == "playbook_negotiable"`.

For each clause with `status == "negotiable_deviation"`:
- Look up `negotiable_deviations` in the playbook for that clause family.
- The fallback text is the matching entry from `negotiable_deviations` (the same entry that drove the classification).
- Return `RedlineProposal(family, original_text, proposed_text, playbook_citation)` where `playbook_citation` is the playbook entry key/path used.
- **Never generate or paraphrase fallback text.** Use only exact strings from the playbook config.

FR-06 enforcement: if a clause is `negotiable_deviation` but no `negotiable_deviations` entry was matched (this should not happen given correct classification, but must be guarded) → reclassify the clause as `escalate` with `reason_code = "no_approved_fallback"` and re-run routing. Do not produce a redline.

Log each redline proposal to audit with event type `redline_generated`.

---

### `approval.py`

Manages the approval state for negotiated packages. All state is persisted in `data/approvals.json`.

**Schema for `data/approvals.json`**:
```json
{
  "<contract_id>": {
    "release_status": "blocked" | "cleared",
    "clauses": {
      "<family>": {
        "approved": true | false,
        "lawyer_name": "Full Name",
        "timestamp": "ISO 8601"
      }
    }
  }
}
```

`contract_id` = filename (without path).

**Functions exposed**:
- `initialise_approval_packet(contract_id, redline_families)` — called by `run.py` after redlines are generated; creates entry with all families set to `approved: false`.
- `record_approval(contract_id, clause_family, lawyer_name)` — records approval with current timestamp. Validates that `contract_id` exists and `clause_family` is in the packet.
- `check_release(contract_id)` → returns `("cleared", [])` if all clauses approved, or `("blocked", [list of unapproved families])`.
- `set_release_status(contract_id, status)` — updates `release_status` field.

Log every approval record and release status change to audit.

---

### `audit.py`

Append-only audit log at `data/audit.jsonl`. One JSON object per line.

**Event schema**:
```json
{
  "timestamp": "ISO 8601",
  "contract_id": "filename.pdf",
  "event_type": "ingestion | extraction | extraction_error | classification | routing | redline_generated | approval_recorded | release_attempted | release_blocked | release_cleared | override",
  "payload": {}
}
```

**Rules**:
- `log_event(contract_id, event_type, payload)` opens the file in append mode, writes one line, closes. Never rewrites existing lines.
- `query_by_contract(contract_id)` reads all lines and returns those matching the contract_id — used by report generation.
- If `data/audit.jsonl` does not exist, create it on first write.

---

### `metrics.py`

**Input**: `data/analysis_results.json`, `data/approvals.json`, `data/audit.jsonl`
**Output**: `MetricsSummary` object consumed by `report.py`

Computes:
- **Route distribution**: count and percentage per queue across all analysed contracts.
- **Escalation rate**: `senior_lawyer_escalation` count / total contracts.
- **Mean turnaround**: for each queue, mean elapsed time between ingestion log event and routing log event (in seconds). Derived from audit log timestamps.
- **Override rate**: count of `override` audit events / total contracts. (An override is when a user re-routes a contract manually — recorded via `approve.py --override`; leave at 0 if no overrides exist yet.)
- **Approval latency**: mean elapsed time between `redline_generated` and `approval_recorded` events per contract, averaged across all approved contracts.

All time calculations come from audit log timestamps. If no data exists for a metric, return `null` rather than 0 to distinguish "not measured yet" from "zero."

---

### `report.py`

**Input**: list of analysis results, approval state, metrics summary
**Output**: single self-contained HTML file (inline CSS + vanilla JS, no external dependencies)

#### HTML Report Sections

**1. Header**
- Title: "Vendor Contract Review — Queue Report"
- Run timestamp (ISO 8601)

**2. Summary Dashboard**
- Cards showing: Total contracts | Standard | Playbook Negotiable | Escalation | Errors
- Metrics table: Escalation rate | Mean turnaround per queue | Approval latency | Override rate

**3. Contract Table**
One row per contract:
- Filename
- Queue badge: `STANDARD` (green), `PLAYBOOK NEGOTIABLE` (amber), `ESCALATION` (red), `ERROR` (grey)
- Clauses matched / total checked
- Release status (only shown for `playbook_negotiable`): `BLOCKED` (red) | `CLEARED` (green)
- Routing reason (one sentence)
- [Expand] button

**4. Contract Detail Panel** (expanded per contract)

Tab 1 — **Clause Analysis**: table with one row per clause family:
- Clause family name
- Status badge: `MATCH` (green) | `DEVIATION` (amber) | `ESCALATE` (red) | `MISSING` (grey) | `OPTIONAL-ABSENT` (light grey)
- Confidence score
- Reason code
- Extracted text (first 300 chars, truncated with ellipsis)

Tab 2 — **Redlines** (only for `playbook_negotiable`):
- Per redlined clause: original text block, proposed replacement text block, playbook citation
- Approval status per clause: `APPROVED by [Name] on [date]` (green) | `AWAITING SIGN-OFF` (red)
- Overall release status banner

Tab 3 — **Audit Trail**: chronological list of all audit events for this contract.

**5. Error Section**
Ingestion errors listed with filename and reason.

#### Visual Design
- Responsive layout, readable at 1080p
- Monospace font for extracted clause text and redline blocks
- Colour badges must also carry text labels (not colour-only)
- Vanilla JS for expand/collapse and tab switching — no frameworks

---

## CLI Entry Points

### `run.py` — Main analysis pipeline

```
python run.py --input "Input contract" --output report.html
```

- Scan `Input contract/` for `.pdf` and `.docx` files. Skip other extensions silently.
- For each file: ingest → extract → classify → route → (if playbook_negotiable) generate redlines → initialise approval packet → persist results to `data/analysis_results.json` → log all steps.
- Print one status line per contract to stdout: `[OK] filename.pdf → standard` or `[ERR] filename.pdf → parse_error`.
- After all contracts: compute metrics → generate HTML report → print output path.
- Check for `ANTHROPIC_API_KEY` at startup; exit with code 1 and a clear message if missing.

---

### `approve.py` — Record named-lawyer sign-off

```
python approve.py --contract "filename.pdf" --clause liability_cap --lawyer "Jane Smith"
```

- Validates that `filename.pdf` exists in `data/analysis_results.json`.
- Validates that `liability_cap` is in the approval packet for that contract (i.e. it was redlined).
- Records approval with timestamp to `data/approvals.json`.
- Logs to audit with event type `approval_recorded`.
- Prints: `[APPROVED] liability_cap in filename.pdf — signed off by Jane Smith at <timestamp>`.
- If all clauses for the contract are now approved, automatically calls `set_release_status(contract_id, "cleared")` and prints: `[CLEARED] filename.pdf — all clauses approved, package may be released`.

---

### `release.py` — Attempt outbound release

```
python release.py --contract "filename.pdf"
```

- Calls `check_release(contract_id)`.
- If `cleared`: logs `release_cleared` to audit, prints `[CLEARED] filename.pdf — approved for release`.
- If `blocked`: logs `release_blocked` to audit (including the attempted user action), prints `[BLOCKED] filename.pdf — missing approvals for: [clause list]`. **Does not release.** Does not offer a workaround.
- The block is enforced by code logic, not by a warning the user can ignore.

---

## Playbook Config

File: `config/playbook.json`. No legal values hardcoded anywhere in Python modules (FR-09).

### Full Schema

```json
{
  "min_confidence_threshold": 0.70,
  "clause_families": {
    "liability_cap": {
      "required": true,
      "escalation_triggers": [
        "uncapped liability",
        "no limitation of liability",
        "unlimited liability"
      ],
      "accepted_positions": [
        "limited to fees paid in the preceding 12 months",
        "capped at annual contract value",
        "limited to direct damages not exceeding"
      ],
      "negotiable_deviations": [
        "capped at 3x annual fees",
        "limited to direct damages not exceeding 2x",
        "capped at total fees paid"
      ]
    },
    "dpa": {
      "required": true,
      "escalation_triggers": [
        "no data processing agreement",
        "transfers data outside",
        "no standard contractual clauses"
      ],
      "accepted_positions": [
        "data processing agreement attached",
        "GDPR compliant",
        "standard contractual clauses"
      ],
      "negotiable_deviations": []
    },
    "termination": {
      "required": true,
      "escalation_triggers": [
        "no termination for convenience",
        "irrevocable"
      ],
      "accepted_positions": [
        "30 days written notice",
        "either party may terminate on 30 days"
      ],
      "negotiable_deviations": [
        "60 days written notice",
        "45 days written notice",
        "90 days written notice"
      ]
    },
    "ip_ownership": {
      "required": true,
      "escalation_triggers": [
        "assigns all intellectual property",
        "transfers ownership of",
        "work made for hire assigned to vendor"
      ],
      "accepted_positions": [
        "each party retains ownership of pre-existing IP",
        "company retains ownership of deliverables",
        "work for hire owned by company"
      ],
      "negotiable_deviations": []
    },
    "sla": {
      "required": false,
      "escalation_triggers": [],
      "accepted_positions": [
        "99.9% uptime",
        "99.5% uptime",
        "99% uptime"
      ],
      "negotiable_deviations": [
        "98.5% uptime",
        "commercially reasonable efforts"
      ]
    },
    "governing_law": {
      "required": true,
      "escalation_triggers": [],
      "accepted_jurisdictions": [
        "England and Wales",
        "New York",
        "Delaware",
        "California"
      ],
      "negotiable_deviations": []
    },
    "indemnity": {
      "required": true,
      "escalation_triggers": [
        "indemnify and hold harmless for any and all claims",
        "broad indemnification",
        "unlimited indemnity"
      ],
      "accepted_positions": [
        "indemnify for third-party IP infringement claims only",
        "limited to gross negligence or wilful misconduct",
        "mutual indemnification for IP claims"
      ],
      "negotiable_deviations": [
        "indemnify for gross negligence",
        "mutual indemnification"
      ]
    }
  }
}
```

Legal ops updates this file. No code change is required to adjust thresholds, add jurisdictions, or add fallback positions.

---

## Project Layout

```
Scenario_2_Vendor_Contract_2/
├── CLAUDE.md
├── run.py                         ← analyse all contracts, generate report
├── approve.py                     ← record named-lawyer clause approval
├── release.py                     ← attempt outbound release (enforces gate)
├── ingestion.py                   ← FR-01
├── extraction.py                  ← FR-02 (uses Haiku)
├── classification.py              ← FR-03, FR-06, FR-09, FR-11
├── routing.py                     ← FR-04
├── redlines.py                    ← FR-05, FR-06
├── approval.py                    ← FR-07 state management
├── audit.py                       ← FR-08
├── metrics.py                     ← FR-10
├── report.py                      ← FR-12 + HTML output
├── config/
│   └── playbook.json              ← FR-09: all legal policy values
├── data/                          ← runtime state (add to .gitignore)
│   ├── analysis_results.json
│   ├── approvals.json
│   └── audit.jsonl
├── Input contract/                ← drop contracts here
│   ├── sample_standard.docx
│   ├── sample_negotiable.docx
│   ├── sample_escalation.docx
│   └── sample_novel_clause.docx
├── requirements.txt
├── .env.example
└── README.md
```

---

## Test Fixtures

Create three valid DOCX fixture files in `Input contract/`:

**`sample_standard.docx`** — All 7 clauses present, all match `accepted_positions`:
- Liability: "limited to fees paid in the preceding 12 months"
- DPA: "data processing agreement attached and GDPR compliant"
- Termination: "either party may terminate on 30 days written notice"
- IP: "each party retains ownership of pre-existing IP"
- SLA: "vendor commits to 99.5% uptime"
- Governing law: "this agreement is governed by the laws of England and Wales"
- Indemnity: "vendor shall indemnify for third-party IP infringement claims only"

**`sample_negotiable.docx`** — Two deviations mapping to `negotiable_deviations`, no escalation triggers:
- Liability: "capped at 3x annual fees" (deviation — approved fallback exists)
- Termination: "60 days written notice" (deviation — approved fallback exists)
- All other 5 clauses match accepted positions

**`sample_escalation.docx`** — Two escalation conditions:
- Liability: "vendor's liability shall be unlimited" (triggers ESC-01)
- DPA: intentionally absent (triggers ESC-07 missing_mandatory_clause)
- All other 5 clauses match accepted positions

**`sample_novel_clause.docx`** — One novel clause with no playbook entry (ESC-08), all others match:
- Liability: "each party's liability is limited to the amount recoverable under its insurance policy in force at the time of the claim" (no accepted position, trigger, or deviation matches → `no_playbook_entry`)
- All other 6 clauses match accepted positions

This fixture covers Validation Design Scenario 4: a clause that is present and extractable with high confidence but falls outside the entire playbook. It validates the safe-failure fallback of last resort at step 8 of the classification logic.

---

## Dependencies

Pin all versions in `requirements.txt`.

```
anthropic>=0.40.0
pdfplumber>=0.11.0
python-docx>=1.1.0
python-dotenv>=1.0.0
```

No web frameworks. No databases. No external services beyond the Claude API.

---

## Environment

- `ANTHROPIC_API_KEY` read from environment or `.env` file.
- If missing at startup of any CLI command → print clear error and exit with code 1.
- Provide `.env.example` with `ANTHROPIC_API_KEY=your_key_here`.

---

## Acceptance Criteria

The build is complete when all of the following pass:

**FR-01–FR-04 (pipeline)**
1. `python run.py --input "Input contract" --output report.html` completes without unhandled exceptions.
2. `sample_standard.docx` → queue `standard` in the report.
3. `sample_negotiable.docx` → queue `playbook_negotiable`; two deviation clauses visible with redline proposals in the report; release status shows `BLOCKED`.
4. `sample_escalation.docx` → queue `senior_lawyer_escalation`; escalation reason codes visible; no redlines generated.

**FR-05–FR-06 (redlines)**
5. Redlines for `sample_negotiable.docx` contain exact playbook fallback strings, not paraphrases. Confirm by comparing report output to `config/playbook.json` `negotiable_deviations` entries.
6. Adding a contract with a deviation that has no `negotiable_deviations` entry results in `escalate` with `reason_code = "no_approved_fallback"`, not a generated redline.

**FR-07 (release gate)**
7. `python release.py --contract "sample_negotiable.docx"` prints `[BLOCKED]` before approvals are recorded.
8. `python approve.py --contract "sample_negotiable.docx" --clause liability_cap --lawyer "Jane Smith"` succeeds and updates `data/approvals.json`.
9. `python release.py --contract "sample_negotiable.docx"` still prints `[BLOCKED]` after only one of two clauses is approved.
10. After approving both clauses, `python release.py` prints `[CLEARED]`.

**FR-08 (audit)**
11. `data/audit.jsonl` exists after running the pipeline. It contains at least one event per stage (ingestion, extraction, classification, routing, redline_generated) for each processed contract.
12. Running `release.py` on a blocked contract adds a `release_blocked` event to the log with the user's attempted action.

**FR-09 (configurable)**
13. Changing `min_confidence_threshold` in `config/playbook.json` from 0.70 to 0.99 and re-running causes `sample_standard.docx` to route to `senior_lawyer_escalation` (all clauses fail confidence gate). No code change required.

**FR-10 (metrics)**
14. The HTML report summary dashboard shows route distribution counts and percentages that match the three fixture results.

**FR-11 (confidence gate)**
15. When a clause confidence is below `min_confidence_threshold`, the audit log shows `reason_code = "low_confidence"` and the contract routes to escalation — not to `standard` or `playbook_negotiable`.

**FR-12 (review packet)**
16. Every contract — regardless of queue — has an expandable detail panel in the HTML report showing all 7 clause families with their extracted text, status, and rationale.

**ESC-08 (no playbook entry — novel clause)**
17. `sample_novel_clause.docx` → `liability_cap` classified `escalate` with `reason_code = "no_playbook_entry"`; routing decision is `senior_lawyer_escalation`; zero redlines generated; audit log contains the classification event with the extracted liability clause text and reason code. This confirms the safe-failure fallback (classification step 8) fires correctly on novel language that passes extraction but matches nothing in the playbook.

---

## Implementation Rules

1. **Rules own routing and release decisions.** The LLM (Haiku) is used for extraction and semantic similarity only. The code, not the LLM, determines `status`, `queue`, and `release_status`.
2. **No hardcoded legal values.** Every threshold, jurisdiction, trigger phrase, and fallback string lives in `config/playbook.json`.
3. **Safe failure default.** When uncertain — low confidence, API error, missing clause, no playbook match — escalate, do not approve silently.
4. **Audit log is write-only during analysis.** Never delete or rewrite audit lines. Append only.
5. **Redline source traceability.** Every `RedlineProposal` must carry `playbook_citation` pointing to the exact config key used — so a lawyer can verify where the proposed language came from.
6. **No partial implementations.** If a requirement cannot be fully met, document the gap in `README.md` under "Known Limitations" with explicit rationale. Do not implement a stub that silently skips the requirement.
