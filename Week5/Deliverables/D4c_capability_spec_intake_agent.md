# D4c — Capability Specification: Intake & Anomaly Agent
## Greenfield Health Systems: Medical Claims Adjudication Transformation

*Inputs: `D4_canonical_claim_record.md` (output contract), `D4_preamble_capability_spec.md` (shared entities), `Capstone-A-Claims-Pack/README.md` (format inventory), direct Claims Pack sampling (all 8 format families).*

*Relationship to Gate5a deliverables: This spec is Wave 1 prerequisite infrastructure. It is deferred as a primary Gate5a capability spec target (see `D4_preamble_capability_spec.md §1` deferral rationale). It is produced here because the canonical normalized claim record (D4_canonical_claim_record.md) requires an explicit producing agent, and because the adapters in `prototype/tools/intake/` implement a subset of this spec.*

---

## §0. Agent Purpose

**Agent name:** Intake & Anomaly Agent (INTAKE)

**One-sentence purpose:** Accept claims arriving in any of the 8 intake formats, extract required fields, normalize them to the `NormalizedClaimInput` canonical record, and route the result to WS1's adjudication queue — or to `PARSE_FAILED` when extraction cannot recover required fields.

**What this agent does not do:**
- Does not make adjudication decisions (approve, deny, escalate for clinical reasons)
- Does not validate clinical appropriateness of diagnosis or procedure codes
- Does not hold claims for human review beyond what extraction failure requires
- Does not manage SLA timers (Queue & SLA Management Agent scope)

**Wave position:** Wave 1 — prerequisite infrastructure for WS1. WS1 cannot run without a normalized claim record; this agent produces it.

---

## §1. Jobs-to-be-Done

### INT-JtD-1: Format detection and extraction

**Trigger:** A claim file arrives in the intake queue.

**Inputs:** Raw file (EDI text, JSON, PDF text, .eml text)

**Output:** `NormalizedClaimInput` dict (see `D4_canonical_claim_record.md §2`)

**Autonomy:** Fully Agentic — no HITL gate. D2B score 3/7 (high input structure variance, but decision determinism is high once format is identified, no compliance constraint on the extraction decision itself). Parse failures route to PARSE_FAILED queue for human handling without agent review.

**Success criteria:**
- All HARD required fields populated (`claim_id`, `diagnosis_codes`, `procedure_codes`)
- All SOFT required fields populated or defaulted with warning
- `intake_warnings` list accurate and complete
- `source_format` correct

### INT-JtD-2: Anomaly detection and quality flagging

**Trigger:** Extraction complete; record passes HARD validation.

**Inputs:** Extracted `NormalizedClaimInput` dict

**Output:** `intake_warnings` list appended with anomaly flags; no field values changed

**Autonomy:** Fully Agentic — no HITL gate. D2B score 5/7. Pattern matching against known anomaly signatures.

**Anomaly checks (deterministic, no LLM):**
- `duplicate_claim_detected` — ClaimRecord lookup by (member_id, date_of_service, procedure_codes[0]); if a prior ClaimRecord with state ∉ {PARSE_FAILED, REJECTED} exists for the same tuple, append `duplicate_claim_detected` and set `resubmission_of = <prior_claim_id>`; WS1 inspects this flag during T-01 deduplication
- `resubmission_detected` — CLM frequency code 7 or 8 (EDI) or `resubmission_of` field non-null (portal-JSON)
- `billed_amount_zero` — billed_amount = 0.0 after default fill
- `quantities_length_mismatch` — lengths don't match before default fix
- `fhir_billable_period_reversed` — FHIR billablePeriod.start > billablePeriod.end
- `date_of_service_missing` — date_of_service = "unknown" after extraction
- `payer_id_is_name` — payer field is a text name, not a machine-readable ID

---

## §2. Format Detection

Format is determined from the file extension and header content. The agent applies the following rules in order:

| Priority | Rule | Assigned format |
|----------|------|----------------|
| 1 | File extension is `.edi` or `.x12`; content starts with `ISA*` | EDI (type determined from GS[8] transaction set) |
| 2 | EDI content and `GS[8]` contains `005010X222A1` | `EDI_837P` |
| 3 | EDI content and `GS[8]` contains `005010X223A2` | `EDI_837I` |
| 4 | File extension is `.json` and top-level key `resourceType == "Claim"` | `FHIR_R4` |
| 5 | File extension is `.json` and top-level key `submission_id` present | `PORTAL_FORM` |
| 6 | File extension is `.json` and neither of the above | Unknown — PARSE_FAILED |
| 7 | File extension is `.txt`; content contains "HEALTH INSURANCE CLAIM FORM" or "CMS-1500" | `CMS1500_PDF` |
| 8 | File extension is `.eml`; MIME type `message/rfc822` | `EMAIL_EML` |
| 9 | File extension is `.pdf`; content contains fax header patterns | `FAX_PDF` |
| 10 | File extension is `.pdf`; no fax header | `EXCEPTION_NOTES_PDF` |
| 11 | No rule matches | Unknown — PARSE_FAILED with warning `format_unrecognized` |

---

## §3. Extraction Tiers

### Tier 1 — Electronic structured (deterministic parser, no LLM)

**Formats:** EDI 837P, EDI 837I, Portal JSON, FHIR R4
**Volume:** ~85% of claims
**LLM cost:** $0

**EDI X12 extraction:**
- Element separator detected from ISA[3] character position (0-indexed position 3)
- Segment terminator detected from last character of stripped ISA segment
- Segments split on terminator; elements split on element separator
- Component values split on `:` separator
- Parsing rules per segment:
  - `GS`: element[8] → transaction_set (determines 837P vs 837I)
  - `CLM`: element[1] → claim_id; element[2] → billed_amount (float)
  - `NM1*85`: element[9] → provider_npi; element[3] → provider_name (for specialty heuristics)
  - `NM1*IL`: element[9] → member_id
  - `NM1*40`: element[9] → payer_id
  - `HI`: each element, if it contains `:`, split on `:` — if qualifier starts with `AB`, second component is a diagnosis code
  - `SV1`: element[1] split on `:` — second component is procedure code (strip `HC:` prefix); element[4] → unit quantity
  - `DTP*472`: element[3] → date_of_service (convert YYYYMMDD → YYYY-MM-DD)
  - `REF*G1` or `REF*F5`: element[2] → prior_auth_number
  - `CLM` element[4] component[0] → place_of_service

**Portal JSON extraction:** Field mapping per `D4_canonical_claim_record.md §3`.

**FHIR R4 extraction:**
- `id` → claim_id
- `patient.reference` strip "Patient/" prefix → member_id
- `provider.reference` strip "Practitioner/" prefix → provider_npi
- `provider.display` → text parse for specialty heuristics (same `_SPECIALTY_HINTS` table as EDI)
- `insurer.reference` strip "Organization/" prefix → payer_id
- `diagnosis[].diagnosisCodeableConcept.coding[0].code` → diagnosis_codes
- `item[].productOrService.coding[0].code` → procedure_codes
- `item[].quantity.value` → procedure_quantities
- `item[].servicedDate` min → date_of_service
- `total.value` → billed_amount
- `item[].modifier[].coding[0].code` → modifier_codes
- `billablePeriod.start > billablePeriod.end` → append `fhir_billable_period_reversed`

### Tier 2 — OCR text (deterministic parser on pre-OCR'd text, no LLM)

**Formats:** CMS-1500 OCR
**Volume:** ~10% of claims
**LLM cost:** $0 (OCR is pre-done by clearinghouse; only pattern matching required)
**OCR failure rate:** ~5% (assumption A6, low confidence — no measured baseline; see §8)

**CMS-1500 OCR extraction:**
The Claims Pack pre-extracts CMS-1500 forms to plain text in `cms1500-ocr/`. The agent parses this text using field number anchors:

| CMS-1500 field | Content | Extraction pattern |
|----------------|---------|-------------------|
| Field 1a | Member ID | After "1A. INSURED'S I.D. NUMBER" or "INSURED'S ID NUMBER" |
| Field 11 | Group number | After "11. INSURED'S GROUP OR FECA NUMBER" |
| Field 11c | Payer / insurance | After "11C." or "INSURANCE PLAN NAME"; sets `payer_id_is_name` warning |
| Field 21 | Diagnosis codes | ICD regex: `[A-Z][0-9]{2}[\\.][0-9A-Z]{0,4}` across 4 positions |
| Field 23 | Prior auth number | After "23." or "PRIOR AUTHORIZATION NUMBER" |
| Field 24A | Date of service | MMDDYYYY pattern; convert to YYYY-MM-DD |
| Field 24D | CPT codes | 5-digit numeric strings in service line area |
| Field 24G | Units | Numeric value after CPT code on same line |
| Field 26 | Claim ID | After "26." or "PATIENT'S ACCOUNT NO"; cleanup OCR artifacts ("CL -" → "CLM-") |
| Field 28 | Billed amount | Dollar amount after "28." or "TOTAL CHARGE" |
| Field 33 | Provider NPI | 10-digit string in "NPI" box; often empty in OCR |

OCR confidence scoring: if any of field 26, 21, or 24D fail to match expected format, append `ocr_confidence_low`.

### Tier 3 — Unstructured LLM extraction (one Haiku call per document)

**Formats:** Email .eml, Fax PDF, Exception Notes PDF
**Volume:** ~5% of claims (30 email + 30 fax + 40 exception notes = 100 / 2,000)
**LLM cost:** ~$0.0004 / claim (Haiku input ~500 tokens + output ~200 tokens)

**Email (.eml) pre-processing:**
- Parse MIME structure (multipart/alternative or plain text)
- Extract `X-Submitter-NPI` header → provider_npi (structured, no LLM needed)
- Extract `X-Submitter-TaxID` header → internal reference (not in NormalizedClaimInput)
- Extract plain text body (prefer text/plain over text/html)
- Pass body + NPI header to Haiku for field extraction

**Haiku prompt template (Email):**
```
You are extracting structured claim data from an insurance claim email.
Extract these fields from the email body text below.
Return a JSON object with exactly these keys (null if not found):
  claim_id, member_id, payer_id (plan name or ID),
  group_id, provider_specialty, date_of_service (YYYY-MM-DD),
  billed_amount (float), diagnosis_codes (list of ICD-10 strings),
  procedure_codes (list of 5-digit CPT strings), procedure_quantities (list of ints)

Email body:
{body_text}
```

**Haiku prompt template (Fax / Exception Notes):**
Same field set, body replaced with OCR-extracted text from the PDF.

**Post-LLM validation:** Apply same HARD and SOFT rules as Tier 1. If Haiku returns null for `diagnosis_codes` or `procedure_codes`, claim → PARSE_FAILED with `llm_extraction_failed_required_field`.

**LLM confidence guard — SOFT fields:** If the LLM response contains a malformed value for a SOFT field (e.g., negative billed_amount, non-10-digit provider_npi, malformed date_of_service), set the field to its normalization default and append `llm_extraction_low_confidence` to `intake_warnings`. Claim continues to WS1 with warning intact.

**LLM confidence guard — HARD fields:** If the LLM response contains a malformed or null value for a HARD required field (`diagnosis_codes`, `procedure_codes`, `claim_id`), do NOT set to default. Trigger PARSE_FAILED_LLM_REQUIRED_FIELD. The claim does not continue to WS1.

---

## §4. Normalization Rules

Applied after extraction, before validation, regardless of format:

1. All `diagnosis_codes` values → `.upper().strip()`
2. All `procedure_codes` values → strip leading `HC:`, `WK:`, or other X12 service type qualifiers; strip whitespace; result must be 4–5 characters
3. `provider_npi` → strip all non-numeric characters; if result is not 10 digits, set to "UNKNOWN_NPI" + warning `provider_npi_format_invalid`
4. `date_of_service`:
   - If YYYYMMDD (8 digits, EDI) → `YYYY-MM-DD`
   - If MMDDYYYY (CMS-1500) → `YYYY-MM-DD`
   - If already `YYYY-MM-DD` → no change
   - Otherwise → "unknown" + warning `date_of_service_missing`
5. `billed_amount` → cast to float; if cast fails → 0.0 + warning `billed_amount_zero`
6. `procedure_quantities` → ensure same length as `procedure_codes`; fill missing positions with 1; reset any value < 1 to 1
7. `claim_id` → `.strip()`; remove null bytes and control characters

---

## §5. Validation, Escalation Triggers, and Routing

### State transitions

| Transition | Trigger |
|-----------|---------|
| (new) → RECEIVED | File dequeued from intake queue |
| RECEIVED → PARSING | Agent begins format detection |
| PARSING → NORMALISED | All HARD required fields extracted and validated |
| PARSING → PARSE_FAILED | Any hard failure condition below |

Each state transition requires a COMMITTED `AuditLogEntry` with `action = CLAIM_STATE_TRANSITION` before the next processing step proceeds.

### Hard failures → PARSE_FAILED

| Trigger | Condition | ClaimRecord state |
|---------|-----------|-------------------|
| PARSE_FAILED_NO_CLAIM_ID | `claim_id` is null or empty after normalization | PARSE_FAILED |
| PARSE_FAILED_NO_DIAGNOSES | `len(diagnosis_codes) == 0` after extraction | PARSE_FAILED |
| PARSE_FAILED_NO_PROCEDURES | `len(procedure_codes) == 0` after extraction | PARSE_FAILED |
| PARSE_FAILED_FORMAT_UNKNOWN | Format detection found no matching rule | PARSE_FAILED |
| PARSE_FAILED_LLM_REQUIRED_FIELD | Haiku extraction returned null for a HARD required field | PARSE_FAILED |

PARSE_FAILED claims are written to the `parse_failed_queue`. **No EscalationPacket is produced** — the parse_failed_queue uses a separate `ParseFailedQueueMessage` schema:

| Field | Type | Content |
|-------|------|---------|
| `claim_id` | UUID | ClaimRecord.id |
| `source_file` | string | Original filename |
| `source_format` | string | Detected format enum value, or `UNKNOWN` |
| `failure_reason` | string | Trigger ID from table above (e.g., `PARSE_FAILED_NO_DIAGNOSES`) |
| `raw_content` | string | First 4,096 characters of raw file content |
| `extraction_output` | JSON object | Fields successfully extracted before failure (may be empty) |
| `queued_at` | ISO 8601 timestamp, UTC | When the message was enqueued |

On PARSE_FAILED, the Intake Agent:
1. Transitions `ClaimRecord.state`: PARSING → PARSE_FAILED.
2. Writes `AuditLogEntry`:
   - `action = CLAIM_PARSE_FAILED` (see §11)
   - `entity_type = "ClaimRecord"`, `entity_id = ClaimRecord.id`
   - `input_summary = { "source_file": source_file, "failure_reason": failure_reason, "source_format": source_format }`
   - `output_summary = { "previous_state": "PARSING", "new_state": "PARSE_FAILED" }`
   - `delegation_tier = AGENT_ALONE`
   - Transition `AuditLogEntry.state`: PENDING_WRITE → COMMITTED before step 3.
3. Writes `ParseFailedQueueMessage` to `parse_failed_queue`.

**SLA:** No SLA timer applies to `PARSE_FAILED` claims from the Intake Agent's perspective; operator review SLA is set by operations. `PARSE_FAILED` is a terminal ClaimRecord state — no pipeline retry. A human operator reviews parse_failed_queue messages; they are never routed to WS1.

**PARSE_FAILED rate targets:**
- Tier 1 (EDI): < 15% (observed ~9% for 837P, ~8.5% for 837I from Claims Pack sampling — missing diagnosis codes)
- Tier 2 (OCR): < 20% (OCR error compounding; 5% target for field-level failures)
- Tier 3 (LLM): < 5% (Haiku extraction; hard failures only)

### Successful extraction → NORMALISED

On success, the Intake Agent:
1. Creates a `ClaimRecord` row with `state = RECEIVED`; writes a COMMITTED `AuditLogEntry` (`action = CLAIM_STATE_TRANSITION`, `entity_type = "ClaimRecord"`, `entity_id = ClaimRecord.id`, `output_summary = { "previous_state": "RECEIVED", "new_state": "PARSING" }`, `delegation_tier = AGENT_ALONE`); transitions `ClaimRecord.state` to PARSING.
2. Transitions `ClaimRecord.state`: PARSING → NORMALISED.
3. Writes `AuditLogEntry`:
   - `action = CLAIM_NORMALISED` (see §11)
   - `entity_type = "ClaimRecord"`, `entity_id = ClaimRecord.id`
   - `input_summary = { "source_file": source_file, "intake_warnings": intake_warnings, "source_format": source_format }`
   - `output_summary = { "previous_state": "PARSING", "new_state": "NORMALISED" }`
   - `delegation_tier = AGENT_ALONE`
   - Transition `AuditLogEntry.state`: PENDING_WRITE → COMMITTED before step 4.
4. Writes `NormalizedClaimInput` dict to the normalised claim queue.

---

## §6. Output Contract Reference

The canonical output format is fully defined in `D4_canonical_claim_record.md`. This spec does not duplicate that definition; it specifies how to produce it.

Key constraint: the `NormalizedClaimInput` the Intake Agent emits is passed directly to `WS1.process_claim(claim: dict)` without transformation. If the Intake Agent emits a field name that WS1 does not access (e.g. `group_id`), that field is silently ignored by WS1. If WS1 accesses a field that the Intake Agent did not emit (e.g. `payer_id` missing from dict), WS1 must handle `KeyError` gracefully with `.get(field, default)`.

---

## §7. LLM Model Routing and Cost

| Format tier | Model | Tokens/claim | Cost/claim | Monthly cost (100 claims/day) |
|-------------|-------|-------------|-----------|-------------------------------|
| Tier 1 (EDI, Portal JSON, FHIR R4) | None | 0 | $0 | $0 |
| Tier 2 (CMS-1500 OCR) | None | 0 | $0 | $0 |
| Tier 3 (Email, Fax, Exception Notes) | Haiku 4.5 | ~700 in + ~200 out | ~$0.0004 | ~$1.20 |

Tier 3 volume: ~100 files/day × $0.0004 = $0.04/day = ~$14.60/year. Negligible relative to WS1 LLM costs.

Haiku is selected (not Sonnet) because:
- The extraction task is structured field-extraction from text, not clinical judgment
- Haiku has sufficient accuracy for well-structured email and typed notes
- Cost is 10× lower than Sonnet for this high-frequency, low-complexity task
- Sonnet is reserved for WS1 clinical content classification (non-trivial decision)

Exception: if Haiku extraction confidence is flagged as low (`llm_extraction_low_confidence`) for a SOFT field, the claim is still passed to WS1 with the warnings intact. WS1 does not re-invoke a higher-tier model — that is out of scope for the intake contract. The warning is surfaced in the physician review packet if the claim escalates. HARD field failures (null or malformed `diagnosis_codes`, `procedure_codes`, `claim_id`) always route to PARSE_FAILED and are never passed to WS1.

---

## §8. Open Assumptions

| ID | Assumption | Why it matters | Confidence |
|----|-----------|----------------|------------|
| A5 | OCR text in `cms1500-ocr/` was produced by the clearinghouse before reaching the Intake Agent. The agent does not need to run OCR itself. | If wrong: agent must add a PDF→text OCR step (Tesseract or cloud OCR), increasing complexity and Tier 2 failure rate | Medium — Claims Pack README implies pre-extraction, but production path is unconfirmed |
| A6 | OCR failure rate ~5% for CMS-1500 (claim → PARSE_FAILED). | Drives PARSE_FAILED queue staffing estimate. | Low — no measured baseline |
| A7 | Haiku extraction accuracy ≥ 95% for email and fax formats. | If wrong: Tier 3 PARSE_FAILED rate rises. Mitigation path is expanding PARSE_FAILED queue staffing, not adding a Sonnet fallback tier — Sonnet fallback is out of scope for Wave 1. | Low — no measured baseline; needs validation run |
| A8 | The Intake Agent processes claims synchronously — one file at a time in sequence. | If parallelism is required (throughput > 50 claims/min), the agent design needs a queue-worker pattern. 2,000 claims/day ÷ 8 hours = ~4 claims/min — synchronous is adequate. | High |
| A9 | `X-Submitter-NPI` header is present in all email submissions. | If absent: provider_npi defaults to "UNKNOWN_NPI" for all email claims, degrading code validity and billing audit quality. | Medium — observed in Claims Pack samples, but custom headers could be stripped by mail servers |
| A10 | CMS-1500 PARSE_FAILED rate in production will be materially lower than the 41% rate observed in Claims Pack sampling (empirically measured in `D4_canonical_claim_record.md §9`). The Claims Pack rate is driven by OCR quality on the synthetic dataset. | Drives PARSE_FAILED queue staffing for Tier 2 claims. If the production rate exceeds 30%, CMS-1500 should be escalated to a Tier 2b path with clearinghouse OCR pre-validation before intake. | Medium — Claims Pack rate is empirically measured but on synthetic data only |

---

## §9. Integration with WS1

The Intake Agent writes the `NormalizedClaimInput` to a normalised claim queue. WS1 reads from this queue. The interface is:

- **Queue:** normalised_claims_queue (FIFO, persistent)
- **Message schema:** `NormalizedClaimInput` as defined in `D4_canonical_claim_record.md §2`
- **Acknowledgement:** WS1 acknowledges each message after `process_claim()` completes (success or escalation); the Intake Agent does not retry acknowledged messages
- **PARSE_FAILED handling:** Routed to separate `parse_failed_queue`; WS1 never receives these

The Intake Agent does not wait for WS1 to complete processing. It emits the normalized record and moves to the next file.

---

## §11. Audit Log Schema

*Authoritative per-spec audit action enum for the Intake & Anomaly Agent. Referenced by `D4_preamble_capability_spec.md` AuditLogEntry.action field constraint — no action value outside this table is valid for records produced by this agent.*

| Action value | When written | delegation_tier |
|-------------|-------------|----------------|
| `CLAIM_RECEIVED` | ClaimRecord created with `state = RECEIVED` | AGENT_ALONE |
| `CLAIM_STATE_TRANSITION` | Any ClaimRecord.state transition (RECEIVED → PARSING; PARSING → NORMALISED; PARSING → PARSE_FAILED) | AGENT_ALONE |
| `CLAIM_NORMALISED` | PARSING → NORMALISED completed; NormalizedClaimInput written to normalised claim queue | AGENT_ALONE |
| `CLAIM_PARSE_FAILED` | PARSING → PARSE_FAILED completed; ParseFailedQueueMessage written to parse_failed_queue | AGENT_ALONE |
| `ANOMALY_FLAGS_APPENDED` | INT-JtD-2 completes with one or more flags appended to `intake_warnings` | AGENT_ALONE |

All Intake Agent audit records must use `agent_id` in format `INTAKE_AGENT:{version}:{instance_id}`.

---

## §10. Prototype Scope Note

The `prototype/tools/intake/` directory implements a subset of this spec:
- `edi_parser.py` implements Tier 1 EDI extraction for 837P and 837I
- `portal_json_adapter.py` implements Tier 1 portal-JSON extraction
- FHIR R4, CMS-1500 OCR, and Tier 3 LLM extraction are not implemented in the prototype

This is consistent with the prototype scope declaration: the prototype covers the portal-JSON path (20% of volume) plus the EDI path (60%) via the batch runner. The missing formats (FHIR R4, OCR, unstructured) are Intake Agent production build items. Their omission is explicitly disclosed in `prototype/DEMO.md §Format coverage`.
