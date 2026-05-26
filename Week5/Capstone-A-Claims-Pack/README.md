# Capstone Option A — Healthcare Claims Pack (Participant Edition)

**Pack version:** v2.0 (2026-04-27)
**Scenario:** Capstone Option A — Healthcare Claims Processing Transformation
**Purpose:** A simulated single-day intake of 2,000 healthcare claims, mixed across the realistic format and quality distribution a mid-sized payer would actually see, **delivered in their real on-the-wire formats** (EDI X12, FHIR R4 JSON, RFC 5322 `.eml`, PDF). This is the **fixture data** you use to design, test, and demo your agentic claim-processing solution during the Capstone week.

> ⚠️ **All data is synthetic.** No real PHI. Names, dates of birth, member IDs, NPIs, tax IDs, addresses, and phone numbers are randomly generated and do not correspond to real people or providers. Do not treat any value in this pack as a real-world identifier.

> 🔒 **There is no answer key in this folder.** Coaches hold a separate ground-truth oracle for grading. Your job is to design your *own* detection and validation logic and evaluate your agent against it — see "Grading & validation" below.

---

## Why this pack exists

Capstone Option A is built around the scenario:

> *A health insurance payer processes 2,000 claims/day with 45 processors. Auto-adjudication rate is 22% (industry benchmark: 85%). Denial appeal overturn rate is 41%.*

Your job during the Capstone is to design (and partially build) an agentic transformation that lifts the auto-adjudication rate, cuts denial-overturn rework, and handles the multi-format intake stream without fragile glue code. Without realistic fixture data, every solution looks plausible on paper. With this pack, you can:

- run a real agent against realistic intake and measure the auto-adjudication rate it actually achieves against *your own* validation set;
- see whether your design holds up across formats (EDI, FHIR, scanned-PDF CMS-1500, email, fax, exception notes), or only handles the easy case;
- demo the *messy reality* of claims intake to a stakeholder who thinks it's "just a JSON pipeline".

This pack is **not** a benchmark suite. It's a representative day of work. Treat it like one.

---

## What's in the pack

| Folder | Format | File ext | Count | Notes |
|---|---|---|---:|---|
| `edi-837p/` | EDI X12 837P (Professional) | `.edi` | 1,000 | 50% — the bulk-volume electronic format. Real X12 segment encoding (`*` element separator, `~` segment terminator, `:` component separator). |
| `edi-837i/` | EDI X12 837I (Institutional) | `.edi` | 200 | 10% — hospital / inpatient claims. Same X12 encoding as 837P. |
| `portal-json/` | Provider-portal JSON | `.json` | 400 | 20% — clean shape, smaller submitters. Pretty-printed JSON. |
| `fhir-r4-json/` | FHIR R4 `Claim` resource | `.json` | 100 | 5% — modern providers / value-based payers. Conforms to the FHIR R4 `Claim` resource shape. |
| `cms1500-paper/` | Scanned paper CMS-1500 | `.pdf` | 200 | 10% — single-page PDFs of filled-in CMS-1500 forms. **You must run OCR** to extract structured data; this models real paper-claim intake. |
| `email/` | Provider email submissions | `.eml` | 30 | 1.5% — RFC 5322 `.eml` files with proper From/To/Date/Subject/Message-ID headers, custom `X-Submitter-NPI`/`X-Submitter-TaxID` headers, and a mix of plain-text-only and `multipart/alternative` (plain + HTML) bodies. |
| `fax/` | Faxed cover sheets | `.pdf` | 30 | 1.5% — single-page PDFs styled as fax cover sheets, with watermark. |
| `exception-notes/` | Internal processor notes | `.pdf` | 40 | 2% — single-page PDFs in three style variants: typed processor notes, phone-call logs, and "sticky-note" handwritten annotations. |
| **Total** | | | **2,000** | |

> 🎲 **Your pack is one fresh non-deterministic draw.** The claims, identifiers, and dollar amounts in your copy are unique to your draw — the format mix and quality distribution match the scenario, but the specific claims do not match anyone else's pack. (Coaches regenerate packs from a generator they hold; you don't need it.)

The intake is a realistic *mix*: a large majority of claims are auto-adjudicatable or fixable by routine review, a meaningful slice needs human judgment (appeal candidates), and a smaller slice carries a legitimate denial reason. **Part of the exercise is discovering that distribution yourself** — your agent has to detect issues (missing modifiers, OCR truncation, out-of-network, invalid CPT, coverage-date problems, duplicates, and so on) rather than being handed a list of them.

---

## How to use this pack

1. **Start with one format.** Don't try to ingest all eight on day one. Most teams pick `portal-json/` (cleanest shape) or `edi-837p/` (highest volume) to bootstrap.
2. **Define your own ground truth as you go.** Since there is no answer key in this folder, build a small hand-labelled validation set (a few dozen claims you've adjudicated yourself, by hand) and measure your agent against it. Your validation design is itself a graded deliverable (Capstone Deliverable #9).
3. **Auto-adjudicate the truly-clean claims first** — if you can't handle the obviously-clean claims with high accuracy, fixing the messier ones is meaningless.
4. **Tackle the fixable-by-review claims second.** This is where the operational lift lives. Design your agent's tool calls around concrete repair operations (extract NPI, look up member, append a modifier, re-OCR a field) rather than a single "fix it" prompt.
5. **Reserve the judgment-call claims for human-in-the-loop design.** For appeal candidates and ambiguous cases, the right answer is usually "escalate with a clear summary," not "approve" or "deny."
6. **Don't try to handle `email/`, `fax/`, and `exception-notes/` early.** They are the messy long-tail; agents that handle them well are doing a separate job (information extraction — email parsing, PDF/OCR) on top of the core adjudication job.

---

## Grading & validation

There is **no `master-index.csv` or answer key in this folder.** Coaches hold a separate ground-truth oracle and grade your agent's output against it after you submit.

What this means for you:

- **Build your own validation design.** Hand-label a representative sample, define your accuracy and false-positive metrics, and report your agent's performance honestly against your own labels. A clear, honest validation plan beats an inflated metric every time.
- **Watch your false positives.** The dangerous failure mode is *silently approving claims that should have been denied* (non-covered, before coverage-effective-date, duplicate-of-paid, invalid CPT). A high "auto-adjudication rate" that comes from approving claims that should be denied is worse than a lower, honest rate.
- **Be explicit about coverage.** If your solution doesn't yet handle a format, say so. Silently excluding formats to report a flattering metric is the weakest possible move in the defense.

---

## Sample file pointers

For quick orientation, open one file per format. Because each pack is a fresh draw, exact filenames vary — pick any file in each folder:

- EDI 837P: `edi-837p/` (any `.edi` file — open in a text editor)
- EDI 837I: `edi-837i/` (any `.edi` file)
- Provider portal JSON: `portal-json/` (any `.json` file — pretty-printed)
- FHIR R4 `Claim`: `fhir-r4-json/` (any `.json` file — FHIR R4 resource shape)
- CMS-1500 paper: `cms1500-paper/` (any `.pdf` — open in a PDF viewer; you must run OCR to extract structured data)
- Email submission: `email/` (any `.eml` — open in any mail client; ~50% are `multipart/alternative` plain+HTML, the rest plain-text only)
- Fax cover sheet: `fax/` (any `.pdf` — single-page with watermark)
- Exception note: `exception-notes/` (any `.pdf` — typed processor note, phone-call log, or "sticky-note" handwritten transcription)

---

## What the pack is *not*

- **Not real PHI.** All identifiers are synthetic. Member IDs follow real-payer formatting conventions but are randomly generated.
- **Not a fully spec-compliant EDI 837 transaction.** The EDI files use realistic segment naming and field ordering, sufficient for parser exercises and round-tripping. They are not certified for production submission.
- **Not exhaustive of every possible claim issue.** The pack covers the most common operational issues a payer sees. Real payers see hundreds of edge cases that are out of scope here.
- **Not replayable as a "stream."** Intake timestamps are clustered for plausibility but the pack is delivered as a static folder of files, not a live feed. If you want to demo a streaming agent, synthesize the stream from this static pack.
- **Not a benchmark.** There is no leaderboard, no canonical score. Your agent design is the deliverable; this pack is the test bed.

---

## File manifest

```
./
├── README.md                      # This file
├── edi-837p/         ( 1,000 .edi files)
├── edi-837i/         (   200 .edi files)
├── portal-json/      (   400 .json files)
├── fhir-r4-json/     (   100 .json files)
├── cms1500-paper/    (   200 .pdf  files — single-page CMS-1500 forms)
├── cms1500-ocr/      (   OCR-extracted text for the paper claims)
├── email/            (    30 .eml  files — RFC 5322 with custom X-headers)
├── fax/              (    30 .pdf  files — fax cover sheets, watermarked)
├── fax-email/        (   faxed-as-email variants)
└── exception-notes/  (    40 .pdf  files — three style variants)
```

*The ground-truth oracle, answer-distribution stats, and the pack generator are held by coaches (not in this folder). Evaluate your agent against your own validation design.*
