# D4 — Canonical Normalized Claim Record
## Greenfield Health Systems: Intake Agent Output Contract

*Schema derived from: representative sampling of 2–3 files per Claims Pack format family (all 8 formats). Parse success/failure rates in §9 are empirically validated against the full Tier 1 population: 1,000 EDI 837P + 200 EDI 837I + 400 Portal JSON files (1,600 total). Tier 2 and Tier 3 format rates (CMS-1500 OCR, FHIR R4, email, fax, exception notes) are sample-only estimates.*

*This document is the architectural contract between the Intake Agent and WS1 (Administrative Adjudication Agent). Both agents are bound by this contract: the Intake Agent produces it, WS1 consumes it. Neither may deviate from it without a versioned contract change reviewed by both agent owners.*

---

## §1. Rationale for a Separate Canonical Record

WS1 operates on a normalized claim record. By the time a claim reaches WS1, the Intake Agent has already extracted it from whichever of the 8 intake formats it arrived in. WS1 sees the same normalized structure regardless of source format — this is the architectural isolation that allows WS1 adjudication logic to be tested independently of format parsing.

The canonical record is **not** the same as `ClaimRecord` in `D4_preamble_capability_spec.md §2`. `ClaimRecord` is the database entity with state, SLA, and audit relationships. The canonical normalized record is the **intake output payload** — the flat dict/JSON that the Intake Agent writes and WS1 reads at the start of each pipeline invocation. The two are related: the canonical record fields map 1:1 onto the creation-time fields of `ClaimRecord`. The distinction matters because:

- The canonical record is a wire format (Python dict / JSON payload), not a database row
- It exists from the moment extraction completes until WS1 consumes it
- It carries source tracking metadata (`source_format`, `source_file`, `intake_warnings`) that `ClaimRecord` does not need to persist after creation

---

## §2. Entity: NormalizedClaimInput

```
Entity: NormalizedClaimInput
Version: 1.0
Owner: Intake Agent (producer), WS1 (consumer)
Format: flat JSON object / Python dict

HARD REQUIRED — extraction fails, claim → PARSE_FAILED if absent:
  claim_id             str       Unique claim identifier from the source document.
                                 Max 64 chars. Must be non-empty after whitespace strip.
  diagnosis_codes      list[str] ICD-10 codes. Min 1 element. Each element must match
                                 the pattern: letter + 2–7 alphanumeric chars (e.g. "E11.9",
                                 "M54.5", "Z00.00"). Codes are upper-cased on normalization.
  procedure_codes      list[str] CPT or HCPCS codes. Min 1 element. For CPT: 5-digit numeric
                                 string (e.g. "99213"). For HCPCS Level II: letter + 4 digits.
                                 Extracted without modifiers (modifiers go in modifier_codes).

SOFT REQUIRED — missing triggers intake_warning entry, default applied, pipeline continues:
  member_id            str       Insurance member ID. Default: "UNKNOWN_MEMBER".
                                 Max 32 chars.
  provider_npi         str       Rendering provider NPI (10-digit numeric string per CMS).
                                 Default: "UNKNOWN_NPI". Max 10 chars.
  provider_specialty   str       Provider specialty label. Default: "Unknown".
                                 Derived from: structured field (portal-JSON), name heuristics
                                 (EDI), FHIR provider.display (text parse), or LLM extraction.
                                 Max 128 chars.
  date_of_service      str       Service date, ISO 8601 format YYYY-MM-DD.
                                 For multi-line claims: earliest line item date.
                                 Default: "unknown".
  procedure_quantities list[int] Unit count per procedure line. Position-aligned with
                                 procedure_codes: procedure_quantities[i] is the unit count for
                                 procedure_codes[i]. Each value ≥ 1.
                                 Default: [1] × len(procedure_codes).
                                 Array length must equal procedure_codes length.
  billed_amount        float     Total billed amount in USD. Default: 0.0. Min: 0.0.

OPTIONAL — populated when available in the source format, null otherwise:
  payer_id             str|null  Payer / insurance plan identifier. Null if not extractable.
                                 Note: email and CMS-1500 OCR may yield a plan name, not a
                                 machine-readable ID. When a name is extracted (not an ID),
                                 the value is stored and "payer_id_is_name" added to
                                 intake_warnings. Null if neither name nor ID available.
  group_id             str|null  Insurance group or plan identifier. Available in: portal-JSON
                                 (insurance.group_id), CMS-1500 OCR (field 11), email (body
                                 "Group:" field). Not available in: EDI 837P/837I, FHIR R4.
  place_of_service     str|null  CMS place-of-service code (2-digit string). Available in:
                                 EDI 837I (CLM element 5 component 1), CMS-1500 OCR (field
                                 24B), portal-JSON (service_lines[].place_of_service if
                                 present). Not in FHIR R4 core Claim resource.
  modifier_codes       list[str] CPT modifier codes (2-character alphanumeric). Available in:
                                 EDI SV1 or SV2 modifier elements, portal-JSON, FHIR item.modifier.
                                 Default: [].
  prior_auth_number    str|null  Prior authorization reference number. Available in: EDI REF
                                 segment with qualifier G1 or F5, portal-JSON
                                 (service_lines[].prior_auth_number if present). Null if absent.
  resubmission_of      str|null  Original claim ID this submission corrects. Available in: EDI
                                 CLM element 19 (frequency code 7 or 8), portal-JSON
                                 (resubmission_of if present). Null if not a resubmission.

SOURCE TRACKING — always present, set by Intake Agent, never null:
  source_format        str       Format of the source document. Enum:
                                   EDI_837P        — X12 837 Professional
                                   EDI_837I        — X12 837 Institutional
                                   PORTAL_FORM     — Portal JSON (nested submitter/patient/
                                                     insurance/service_lines/diagnoses shape)
                                   FHIR_R4         — FHIR R4 Claim resource
                                   CMS1500_OCR     — CMS-1500 paper form, OCR-extracted text
                                   EMAIL           — RFC 5322 .eml with X-Submitter-NPI header
                                   FAX             — Fax cover sheet PDF
                                   EXCEPTION_NOTES — Exception notes PDF (typed, handwritten,
                                                     call logs)
  source_file          str       Original filename from the intake queue.
                                 e.g. "CLM-2026-1000001.edi", "CLM-2026-0000001.json"
  intake_warnings      list[str] Quality issues detected during extraction. Empty list if none.
                                 Standardized warning strings (see §4).
```

---

## §3. Format-to-Field Extraction Map

This table shows the extraction source for each field in each format. "LLM" means one Haiku call per document is required; "Parser" means deterministic rule-based extraction.

| Field | EDI 837P | EDI 837I | Portal JSON | FHIR R4 | CMS-1500 OCR | Email .eml | Fax / Exception |
|-------|----------|----------|-------------|---------|--------------|------------|-----------------|
| **claim_id** | CLM[1] | CLM[1] | `submission_id` | `id` | Field 26 (OCR) | Body: "Claim reference:" | LLM |
| **member_id** | NM1\*IL[9] | NM1\*IL[9] | `insurance.member_id` | `patient.reference` strip "Patient/" | Field 1a (OCR) | Body: "Member ID:" | LLM |
| **provider_npi** | NM1\*85[9] | NM1\*85[9] (may be empty) | `submitter.npi` | `provider.reference` strip "Practitioner/" | Field 33 NPI box (OCR, often empty) | `X-Submitter-NPI` header | LLM |
| **provider_specialty** | Name heuristics on NM1\*85[3] | "Hospital/Institutional" (institutional always) | `submitter.specialty` | Text parse on `provider.display` (e.g. "Sophia Reyes, MD") | Field 31 or 17 (OCR) | Body: "Specialty:" | LLM |
| **date_of_service** | DTP\*472[3] → YYYY-MM-DD | DTP\*472[3] → YYYY-MM-DD | min(`service_lines[].date_of_service`) | min(`item[].servicedDate`) | Field 24A (OCR, MMDDYYYY) | Body: service date | LLM |
| **diagnosis_codes** | HI segments with AB-prefix qualifiers (ABK, ABF) | HI segments with AB-prefix qualifiers | `[d.code for d in diagnoses]` | `diagnosis[].diagnosisCodeableConcept.coding[0].code` | Field 21 (OCR, up to 12 codes) | Body: ICD code patterns | LLM |
| **procedure_codes** | SV1[1] component after "HC:" | SV1[1] or SV2[1] component after "HC:" | `[sl.cpt_code for sl in service_lines]` | `item[].productOrService.coding[0].code` | Field 24D (OCR, 5-digit CPT) | Body: "CPT XXXXX" patterns | LLM |
| **procedure_quantities** | SV1[4] (units) | SV1[4] or SV2[4] | `[sl.units for sl in service_lines]` | `item[].quantity.value` | Field 24G (OCR) | Body: "N unit(s)" | LLM |
| **billed_amount** | CLM[2] | CLM[2] | `total_charge_amount` | `total.value` | Field 28 (OCR, dollar amount) | Body: total or per-line sum | LLM |
| **payer_id** | NM1\*40[9] | NM1\*40[9] | `insurance.payer_id` | `insurer.reference` strip "Organization/" | Field 11c (payer name, not ID — warns) | Body: "Plan:" (name — warns) | LLM |
| **group_id** | Not available | Not available | `insurance.group_id` | Not in core Claim | Field 11 (OCR) | Body: "Group:" | LLM |
| **place_of_service** | CLM[4][0] (POS in CLM compound) | CLM[4][0] or BHT facility | Not standard | Not in core R4 | Field 24B (OCR) | Not standard | LLM |
| **modifier_codes** | SV1 elements [5]–[8] | SV1/SV2 modifier elements | `service_lines[].modifiers` (if present) | `item[].modifier[].coding[0].code` | Field 24D suffix (OCR) | Rare | LLM |
| **prior_auth_number** | REF\*G1 or REF\*F5[2] | REF\*G1 or REF\*F5[2] | `service_lines[].prior_auth_number` (if present) | `item[].careTeamSequence` (indirect) | Field 23 (OCR) | Rare | LLM |
| **source_format** | "EDI_837P" (from GS[8] 005010X222A1) | "EDI_837I" (from GS[8] 005010X223A2) | "PORTAL_FORM" | "FHIR_R4" | "CMS1500_OCR" | "EMAIL" | "FAX" / "EXCEPTION_NOTES" |
| **source_file** | Filename | Filename | Filename | Filename | Filename | Filename | Filename |

---

## §4. Standardized intake_warnings Strings

| Warning key | Trigger condition | Impact |
|-------------|-------------------|--------|
| `member_id_missing` | No member ID extractable | Default applied; eligibility check will fail |
| `provider_npi_missing` | No NPI in source document | Default applied; code validity may fail |
| `provider_npi_empty_segment` | NPI segment present but value empty (EDI 837I institutional) | Common for hospital billing; default applied |
| `provider_specialty_unknown` | No specialty extractable or derivable | Default "Unknown"; classifier loses one signal |
| `date_of_service_missing` | No service date extractable | Default applied; downstream date validation will flag |
| `payer_id_is_name` | Payer field contains a plain-text name, not a machine ID (email, CMS-1500) | payer_id stored as name string; eligibility lookup may fail |
| `diagnosis_codes_none` | Zero ICD codes extracted — hard failure | Claim → PARSE_FAILED |
| `procedure_codes_none` | Zero CPT codes extracted — hard failure | Claim → PARSE_FAILED |
| `ocr_confidence_low` | CMS-1500 OCR confidence score below 0.80 | Extracted fields may have OCR errors; verify against billed amount |
| `ocr_field_unparseable` | Specific OCR field could not be parsed (e.g. field 26 claim ID garbled) | Named field set to null or default |
| `quantities_length_mismatch` | procedure_quantities length ≠ procedure_codes length | Quantities reset to [1] × len(codes) |
| `billed_amount_zero` | billed_amount extracted as 0.0 or not found | Default applied; downstream payment calculation will flag |
| `fhir_billable_period_reversed` | FHIR billablePeriod.start > billablePeriod.end (data quality) | Logged; date_of_service derived from item-level dates instead |
| `llm_extraction_low_confidence` | LLM extraction (Haiku) returned confidence < 0.70 | Fields marked as uncertain; claim may need human review |
| `resubmission_detected` | CLM frequency code 7 or 8 in EDI; resubmission_of populated | WS1 duplicate check should treat as correction, not duplicate |

---

## §5. Validation Rules (Intake Agent enforces before emitting)

These are applied by the Intake Agent before writing the NormalizedClaimInput. A claim that fails a HARD rule is routed to PARSE_FAILED state. A claim that fails a SOFT rule gets a warning appended and a default applied.

**HARD rules (PARSE_FAILED if violated):**
- `claim_id` is non-null and non-empty after whitespace strip
- `len(diagnosis_codes) >= 1`
- `len(procedure_codes) >= 1`
- `len(procedure_codes) == len(procedure_quantities)` after default-fill

**SOFT rules (warning + default if violated):**
- `member_id` non-null and non-empty → default "UNKNOWN_MEMBER" + warning `member_id_missing`
- `provider_npi` non-null and non-empty → default "UNKNOWN_NPI" + warning `provider_npi_missing`
- `date_of_service` is a valid YYYY-MM-DD → default "unknown" + warning `date_of_service_missing`
- `billed_amount >= 0.0` → default 0.0 + warning `billed_amount_zero`
- `procedure_quantities[i] >= 1` for all i → reset element to 1

**Format rules (applied to code values):**
- All `diagnosis_codes` values upper-cased
- All `procedure_codes` values stripped of leading service type qualifiers (e.g. "HC:" prefix from EDI SV1)
- `provider_npi` stripped of non-numeric characters before storing (OCR noise)
- `date_of_service` converted from YYYYMMDD (EDI) or MMDDYYYY (OCR field 24A) to YYYY-MM-DD

---

## §6. Mapping to ClaimRecord (D4_preamble_capability_spec.md §2)

On intake, the Intake Agent creates a `ClaimRecord` database row. The canonical fields map as follows:

| NormalizedClaimInput field | ClaimRecord field | Notes |
|---------------------------|-------------------|-------|
| `claim_id` | `external_claim_id` | ClaimRecord generates its own `id` (UUID) as PK |
| `member_id` | `member_id` | Direct map |
| `provider_npi` | `provider_id` | ClaimRecord uses `provider_id` as the column name; value is the NPI |
| `provider_specialty` | `provider_specialty` | Direct map |
| `date_of_service` | `date_of_service` | Direct map |
| `diagnosis_codes` | `diagnosis_codes` | Direct map |
| `procedure_codes` | `procedure_codes` | Direct map |
| `procedure_quantities` | `procedure_quantities` | Direct map |
| `modifier_codes` | `modifier_codes` | Direct map |
| `billed_amount` | `billed_amount` | Direct map |
| `payer_id` | — | Not persisted in ClaimRecord; used only by WS1 eligibility and audit |
| `group_id` | — | Not persisted in ClaimRecord; used only for eligibility lookup |
| `place_of_service` | — | Not in current ClaimRecord; add if prior auth lookup requires it |
| `source_format` | `submission_format` | ClaimRecord enum needs updating — see §7 |
| `source_file`, `intake_warnings` | — | Not persisted in ClaimRecord; Intake Agent logs these to AuditLogEntry |

---

## §7. Required Updates to ClaimRecord (D4_preamble_capability_spec.md §2)

The `submission_format` enum in `ClaimRecord` currently reads:
```
[EDI_837, PDF, PORTAL]
```
This is too coarse — it conflates EDI 837P and 837I, and collapses all PDF types into one. Replace with the 8-value enum from `NormalizedClaimInput.source_format`:
```
[EDI_837P, EDI_837I, PORTAL_FORM, FHIR_R4, CMS1500_OCR, EMAIL, FAX, EXCEPTION_NOTES]
```
This change is backward-compatible for WS1 (WS1 does not branch on `submission_format` — it uses the already-normalized fields). WS2 and the Queue & SLA Management Agent are also unaffected. The Queue agent does not route by format; SLA deadlines are format-agnostic.

---

## §8. WS1 Process_Claim() Input Contract

When WS1's `process_claim(claim: dict)` is called, the dict it receives is the `NormalizedClaimInput` payload (passed through directly from the Intake Agent output, no transformation). WS1 accesses the following fields:

| WS1 access pattern | Field | Required by WS1 |
|-------------------|-------|-----------------|
| `claim["claim_id"]` | `claim_id` | Hard required |
| `claim["member_id"]` | `member_id` | Hard required (eligibility lookup) |
| `claim["payer_id"]` | `payer_id` | Used in audit entries and eligibility trigger; null-safe |
| `claim["procedure_codes"]` | `procedure_codes` | Hard required (code validity, classifier) |
| `claim["diagnosis_codes"]` | `diagnosis_codes` | Hard required (code validity, classifier) |
| `claim["provider_specialty"]` | `provider_specialty` | Used by classifier as signal; null-safe |
| `claim["procedure_quantities"]` | `procedure_quantities` | Used by prior-auth tolerance check (T-07) |
| `claim["billed_amount"]` | `billed_amount` | Used by payment calculation (T-09) |

WS1 does **not** access: `provider_npi`, `group_id`, `place_of_service`, `modifier_codes`, `prior_auth_number`, `source_format`, `source_file`, `intake_warnings`. These are available for future tool calls but are not part of the current WS1 pipeline.

---

## §9. Known Data Quality Patterns (from Claims Pack population run)

This section records what the **parser** produces — parse success vs. PARSE_FAILED — for each format. WS1 routing outcomes (approved/escalated) are downstream of the parser and belong in WS1 test reports, not here.

**Tier 1 full-population parse results** (empirical — 2026-05-26):

| Format | n | Parse success | PARSE_FAILED |
|--------|--:|--------------|--------------|
| EDI 837P | 1,000 | **936 (93.6%)** | **64 (6.4%)** |
| EDI 837I | 200 | **183 (91.5%)** | **17 (8.5%)** |
| Portal JSON | 400 | **374 (93.5%)** | **26 (6.5%)** |
| **Total Tier 1** | **1,600** | **1,493 (93.3%)** | **107 (6.7%)** |

All 107 PARSE_FAILED events share one root cause: missing `diagnosis_codes`. No `claim_id` or `procedure_codes` failures were observed in Tier 1.

**Canonical cache — no need to re-run the parser for WS1 testing:**

The 1,493 successfully parsed claims are saved as NormalizedClaimInput JSON in `prototype/normalized-tier1/`. These files are the direct output of the intake parsers and can be fed straight into WS1 without re-parsing the raw EDI/JSON source files.

```
# Run a single cached claim through WS1:
python run_claim.py --file normalized-tier1/CLM-2026-1000001.json

# Run all 1,493 cached claims through WS1 (heuristic classifier):
python run_batch.py --dir normalized-tier1 --limit 0

# Run a live-classifier sample against the cache (costs ~$0.004/claim):
python run_batch.py --dir normalized-tier1 --limit 50 --live
```

The batch runner detects the `normalized` format from the directory name and skips the parse step entirely — `process_claim()` receives the cached dict directly.

**Per-format data quality patterns:**

| Format | Pattern | Empirical frequency | Handling |
|--------|---------|---------------------|---------|
| EDI 837I | `NM1*85` segment has empty NPI element (`NM1*85*2*...*****XX*~`) | Multiple files (sample only) | `provider_npi_empty_segment` warning; default "UNKNOWN_NPI" |
| EDI 837P | No HI segment with AB-prefix qualifiers (diagnosis codes missing) | **6.4%** (64/1,000 — full population) | PARSE_FAILED |
| EDI 837I | No HI segment with AB-prefix qualifiers (diagnosis codes missing) | **8.5%** (17/200 — full population) | PARSE_FAILED |
| Portal JSON | `diagnoses` array is empty | **6.5%** (26/400 — full population) | PARSE_FAILED |
| FHIR R4 | `billablePeriod.start > billablePeriod.end` | Observed in CLM-2026-1001805 (sample only) | `fhir_billable_period_reversed` warning; use item-level dates |
| CMS-1500 OCR | Claim ID garbled (e.g. "CLM" → "CL -" OCR error) | Observed in CLM-2026-1001601 (sample only) | `ocr_field_unparseable` warning; attempt cleanup |
| CMS-1500 OCR | Procedure code garbled (e.g. "97110" → "9 110") | Observed (sample only) | `ocr_field_unparseable` warning; flag for human review |
| Email .eml | `X-Submitter-TaxID` header empty with call-to-action text | Observed in CLM-2026-1001903 (sample only) | Warning in `intake_warnings`; TaxID not part of NormalizedClaimInput |
| Email .eml | Payer field is plan name, not ID | All email samples | `payer_id_is_name` warning; stored as string |

---

### CMS-1500 OCR — Batch Findings and Deferral Decision

A deterministic regex parser (`tools/intake/cms1500_ocr_parser.py`) was built and run against all 200 pre-extracted CMS-1500 OCR text files in the Claims Pack. After two rounds of fixes addressing the most common failure patterns, the PARSE_FAILED rate remained at **41% (82/200)**.

**OCR noise patterns observed (beyond the 3-file sample):**

| Pattern | Example | Effect |
|---------|---------|--------|
| Field label digit dropped | `"24."` → `" 2. SERVICE LINE"` | Service section anchor fails — no procedure codes extracted |
| Letter/digit substitution in keywords | `"SERVICE"` → `"5ERVICE"` | Anchor regex misses the section |
| Dropped character in field keyword | `"ACCOUNT"` → `"ACCONT"` | Claim ID regex fails; fallback uses filename |
| Truncated date (1-digit day) | `"2026-04-0"` | Date normalisation returns None; `date_of_service_missing` warning |
| Missing second hyphen in date | `"2026-0412"` | Requires explicit 4-digit-without-separator branch |
| Service lines merged with header | Column header and first data row on same line | Row regex skips the line entirely |
| Diagnosis section anchor missing | Field 21 label absent or unrecognisable | `diagnosis_codes` empty → PARSE_FAILED |

**Root cause of 82 PARSE_FAILED events:** All are missing `diagnosis_codes` (Field 21 section unrecognisable) or `procedure_codes` (Field 24 section unrecognisable) — the two hard-required fields. The extreme label noise means the regex anchors that reliably anchor against EDI and portal-JSON cannot anchor reliably against CMS-1500 OCR text.

**Decision: CMS-1500 OCR parsing is deferred from prototype scope.**

The parser file exists (`tools/intake/cms1500_ocr_parser.py`) and handles ~59% of files correctly. It is not production-ready. Bringing it to acceptable quality (target: <10% PARSE_FAILED) would require one of:

- A significantly more fault-tolerant layout-aware parser (positional matching instead of label anchoring)
- Tier 3 LLM extraction (Haiku or Sonnet) as a fallback for files where the regex parser fails

Neither is in scope for the Week 5 prototype.

**Impact on coverage:** The prototype empirically covers Tier 1 formats (EDI 837P + EDI 837I + Portal JSON = 1,600 files, ~80% of the 2,000-claim pack). CMS-1500 OCR (200 files, ~10%) is deferred. This is consistent with the stated prototype scope in CLAUDE.md and DEMO.md — scope discipline requires naming this gap explicitly rather than reporting a flattering metric from the 59% that do parse.
