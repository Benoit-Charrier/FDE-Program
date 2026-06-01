# AE Intake Queue — Past 7 Calendar Days

Eight active adverse event reports received via mixed channels. Not yet triaged. **The 15-day FDA reporting clock began at the moment of first receipt by any Helix employee or contractor.**

| Case ID | Channel | Received | Suspect product | Patient identifier (intake) | Reporter | Intake-clock day |
|---|---|---|---|---|---|---:|
| `AE-2026-05-09-001` | HCP fax/PDF | 2026-05-09 14:22 ET | Tezarimab | "Female, mid-50s" | Dr. Renée Ostroff, MD | Day 7 |
| `AE-2026-05-10-002` | Patient web form | 2026-05-10 09:18 ET | Phaedora | "Marcus T., 38, M" | Patient (self) | Day 6 |
| `AE-2026-05-11-003` | Social-media monitoring | 2026-05-11 11:55 ET | Solivian | (handle-only, unspecified) | Public Twitter / X post | Day 5 |
| `AE-2026-05-12-004` | Clinical-trial site report | 2026-05-12 08:30 ET | Solivian | Subject ID SOL-PROT-007-T48-0911 | Site PI, Phase 4 commitment study SOL-PROT-007 | Day 4 |
| `AE-2026-05-13-005` | HCP email | 2026-05-13 16:18 ET | (device complaint mislabeled) | (device serial number only) | Pharmacist | Day 3 |
| `AE-2026-05-14-006` | Literature alert | 2026-05-14 10:08 ET | Tezarimab (cited) | Multiple patients in published case series | Authors (peer-reviewed journal) | Day 2 |
| `AE-2026-05-15-007` | HCP phone | 2026-05-15 13:45 ET | Phaedora (suspect) | Patient deceased; family provided info | Treating psychiatrist Dr. Tomé | Day 1 |
| `AE-2026-05-15-008` | Patient phone | 2026-05-15 15:22 ET | Solivian | "Maria, 67" | Patient (self) | Day 1 |

## Folder layout

```
mock-data/
├── intake-queue/
│   ├── queue.md                              ← you are here
│   └── intake-clock-protocol.md              ← Helix's PV team protocol for the 15-day clock
├── hcp-reports/                              ← HCP report PDFs (transcribed)
├── patient-reports/                          ← patient web-form (JSON) + patient phone (.vtt)
├── social-media-monitoring/                  ← .json extracts from monitoring vendor
├── clinical-trial-site-reports/              ← MedDRA-coded site reports
├── product-information/                      ← reference safety profiles for the 3 marketed products
├── literature-references/                    ← extracted text from published case series
└── prior-cases/                              ← prior AE retrieval extracts
```

## Important

- The 15-day reporting clock starts at the moment of first receipt by ANY Helix employee or contractor — including the social-media monitoring vendor (Helix contractor) on the day they pushed the alert.
- Some reports are missing critical identifiers (handle-only, "Maria, 67"). The system must distinguish between "minimally identifiable patient" (acceptable for ICSR) and "no identifiable patient" (not acceptable).
- One report is a medical device complaint with no AE component — must route away from the AE pipeline.
- One report is a literature case series referencing multiple patients — different obligations apply (literature surveillance vs spontaneous report).
- Patient identifier information is partially redacted in mock; the system you design must handle full PII appropriately.
