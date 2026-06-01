# FNOL Queue — Past 5 Business Days

Eight first-notice-of-loss intakes received via mixed channels and not yet triaged by an intake adjuster. Adjusters work from this queue.

The queue note below is what the originating channel (phone CSR, app, broker) wrote at intake. It is loose first-touch text — treat as background, not verified facts.

| FNOL ID | Channel | Date received | Reporting party | Loss type (rough) | Channel intake note |
|---|---|---|---|---|---|
| `FNL-2026-0511-01` | Phone | 2026-05-11 09:42 | Insured | Auto — rear-end | "Customer called, rear-ended at red light on 280 at exit 19. No injuries he said. He's at autozone now. Says he wants enterprise rental." |
| `FNL-2026-0512-02` | App | 2026-05-12 21:18 | Insured | Homeowner — water | "App submission. Photos of basement, drywall, says HVAC contractor identified split copper line. Asking about ALE." |
| `FNL-2026-0513-03` | Broker email | 2026-05-13 11:30 | Broker, on behalf | Auto — total loss | "Broker forwarded customer email — single-car loss, driver says deer, vehicle off the road in a culvert in rural county. Claims total. Police report attached." |
| `FNL-2026-0513-04` | App | 2026-05-13 14:55 | Insured (work cell number) | Auto — backing into property | "App submission — customer says he backed his work truck into a parking-lot bollard at his employer's lot. Damage to truck and bollard." |
| `FNL-2026-0514-05` | Phone | 2026-05-14 16:08 | Insured (spouse) | Auto — multi-vehicle accident | "Spouse called for insured. 3-car accident on I-65. Insured was lead car, struck from behind by middle car, who was struck from behind by trailing car. Spouse asking about who pays. Insured still at hospital." |
| `FNL-2026-0515-06` | Mail | 2026-05-15 13:11 | Insured | Homeowner — theft | "Mailed in. Handwritten statement, photos of empty jewelry boxes and a broken window. Says they were on vacation 2026-04-22 to 2026-04-28, discovered on return. Did not call us at the time — said they were dealing with police." |
| `FNL-2026-0515-07` | Phone | 2026-05-15 15:33 | Insured | Auto — windshield | "Customer says rock chip on highway. Wants to use glass coverage." |
| `FNL-2026-0516-08` | Broker email | 2026-05-16 10:24 | Broker, on behalf | Auto — total loss + fire | "Broker forwarded customer email. Vehicle 'caught fire' in parking lot of customer's apartment complex Monday evening, total loss. Customer asking about timing of payment." |

## Folder layout

```
mock-data/
├── intake-summary/
│   ├── queue.md                              ← you are here
│   └── policy-system-extract.md              ← what the policy system shows for each reporting party
├── phone-fnol-transcripts/                   ← .vtt FNOL line transcripts
├── app-submissions/                          ← JSON from mobile-app FNOL flow
├── broker-emails/                            ← .eml with PDF attachments
├── police-reports/                           ← .txt mock police-report content
├── photo-metadata/                           ← text representation of EXIF + content notes
├── claimant-statements/                      ← .txt mailed-in or attached statements
└── prior-claims-history/                     ← extracted prior-claims summaries for each insured
```

## Important

- Channel-intake notes (the table above) are first-touch chatter, not verified. Trust the underlying artefacts.
- Some intakes are missing critical artefacts (no police report, no photos, no policy match). Detect and flag — don't assume.
- Some intakes belong to a different operation (workers' comp) and were mis-routed here. Detect and route away.
- Some intakes show anomaly signals that warrant SIU consideration. Surface, don't accuse.
- Policy / PII data in `policy-system-extract.md` and `prior-claims-history/` is partially redacted in mock; the system you design must handle full PII appropriately.
