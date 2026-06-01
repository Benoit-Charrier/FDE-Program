# Active Loan Application Roster — Week of 2026-04-20

Eight residential mortgage applications currently in the underwriting queue at Meridian Home Lending. Files were received in the past 12 business days. Loan officers have done intake but underwriter review has not yet begun.

The index below is what an underwriter sees when opening the queue. **It does not pre-summarise document contents — that is the work.** Use it to navigate; do not assume the data inside the files matches what's named here.

| App ID | Borrower(s) | Product | Loan Amount | Purchase Price | Loan Officer Note |
|---|---|---|---|---|---|
| `APP-2026-0418-A` | Robert Sanderson | 30yr Fixed Conforming | $425,000 | $495,000 | clean salaried borrower; Tech Co employer |
| `APP-2026-0419-B` | Maria Delgado-Chen + David Chen | 30yr Fixed Jumbo | $612,000 | $745,000 | two-borrower file; income docs comingled |
| `APP-2026-0420-C` | Jasmine Beauchamp | 30yr Fixed Conforming | $315,000 | $368,000 | self-employed 1099; two years of returns required |
| `APP-2026-0421-D` | Anthony Marciano | FHA 30yr | $228,000 | $237,000 | FHA product — out of scope; flag and skip |
| `APP-2026-0422-E` | Yuki Tanaka | 30yr Fixed Conforming | $485,000 | $540,000 | borrower mis-labelled docs; 'paystub-final.pdf' is actually a bank statement |
| `APP-2026-0423-F` | Devon Washington-Pierce | 30yr Fixed Conforming | $392,000 | $455,000 | $31,400 deposit 42 days pre-application not documented as gift |
| `APP-2026-0424-G` | Priya Khanna | 30yr Fixed Jumbo | $548,000 | $625,000 | YTD pay stub income annualised does not match W-2 prior-year + raise letter |
| `APP-2026-0425-H` | Connor Yates + Brianna Yates | 30yr Fixed Conforming | $368,000 | $412,000 | co-borrowers; one salaried, one 1099; gift letter for closing costs |


## Folder layout

```
mock-data/
├── application-summary/
│   ├── index.md                              ← you are here
│   └── intake-notes.md                       ← loan officer intake-call notes
├── pay-stubs/                                ← PDF-style (markdown stub w/ embedded data)
├── w2s/                                      ← PDF-style
├── tax-returns/                              ← PDF-style (selected Schedule C / Schedule E pages)
├── bank-statements/                          ← CSV of last-60-day transactions
├── employer-emails/                          ← .eml threads (verification of employment)
├── id-docs/                                  ← OCR-style PDF (drivers license, passport extracts)
└── phone-clarifications/                     ← .vtt transcripts (processor → borrower)
```

## Important

- File names *may* misrepresent content. Trust file contents over filenames.
- Some artefacts are deliberately missing for some applications. That is the realistic shape — flag what's missing, design around it.
- Borrower PII (SSN, DOB, account numbers) is partially redacted in mock data. The system you design must handle full PII appropriately under Meridian's data-residency constraint.
