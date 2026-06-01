# Outbound Shipment Compliance Queue — Past 3 Business Days

Eight active outbound shipment files received from operations and awaiting Trade Compliance review.

| Shipment ID | Date received | Origin | Consignee | Consignee country | Product family | Stated end use | Freight forwarder |
|---|---|---|---|---|---|---|---|
| `SHP-2026-05-13-A1` | 2026-05-13 09:42 | Cleveland OH | Optikraft GmbH | Germany | Routine commodity sensors | Industrial automation OEM integration | Schenker AG |
| `SHP-2026-05-13-A2` | 2026-05-13 11:18 | Cleveland OH | Çelik Endüstri Ticaret AŞ | Türkiye | Specialty alloy (Inconel 718 rod stock) | Industrial-fan turbine repair (downstream end user: Aydın Power Plant per consignee statement) | Kuehne+Nagel |
| `SHP-2026-05-14-B1` | 2026-05-14 08:55 | Austin TX | Apex Star Pte Ltd | Singapore (re-export likely to PRC per freight docs) | Semiconductor process-control equipment subsystem | Customer-stated: "training laboratory equipment for technical college research" | DHL Global Forwarding |
| `SHP-2026-05-14-B2` | 2026-05-14 14:30 | Cleveland OH | Crown Electric Manufacturing Co Ltd | Hong Kong | Power transformer testing equipment | Customer-stated: "for affiliated power utility distribution division" | C.H. Robinson |
| `SHP-2026-05-14-B3` | 2026-05-14 16:45 | Austin TX | (consignee withheld in routing per ITAR shipment notation in COR system) | (per ITAR record: France) | Defense article — guidance subsystem component (per intake record) | (per ITAR record: foreign military sales support) | (per ITAR record: Designated forwarder) |
| `SHP-2026-05-15-C1` | 2026-05-15 10:22 | Dublin (Irish JV) — Re-export | EuroForge SE | Germany (EU re-export) | Specialty alloy (Hastelloy plate stock) | Pressure vessel manufacturing | DB Schenker Ireland |
| `SHP-2026-05-15-C2` | 2026-05-15 13:08 | Cleveland OH | Sundial Manufacturing LLC | United Arab Emirates | Industrial controller (prior shipments under expired license LIC-2024-X-2207) | Stated: "factory upgrade — replacement of failed control unit, same model as prior license" | Expeditors |
| `SHP-2026-05-15-C3` | 2026-05-15 15:33 | Cleveland OH | Global Maritime Logistics LLC (freight forwarder, no end consignee on shipment docs) | (forwarder origin: UAE; ultimate destination per latest forwarder email: "redirected to Lagos, Nigeria") | Industrial sensor package | (no end-user statement on file) | Global Maritime Logistics LLC (self) |

## Folder layout

```
mock-data/
├── shipment-queue/
│   ├── queue.md                              ← you are here
│   └── classifications-and-licenses-on-file.md   ← prior ECCN classifications + licenses
├── purchase-orders/                          ← PO PDFs (transcribed)
├── packing-lists/                            ← packing-list CSVs
├── end-user-statements/                      ← .txt end-user/end-use statements
├── freight-forwarder-emails/                 ← .eml threads
├── denied-parties-screening/                 ← .txt screening outputs
├── ECCN-references/                          ← CCL extract for relevant categories
└── prior-licenses/                           ← prior license documentation extracts
```

## Important

- The shipment queue intake data above is operations' first-touch routing, not a determination. Verify against the underlying documents.
- One shipment in the queue carries an ITAR notation indicating defense-controlled commodity — verify scope and route accordingly.
- One shipment claims a prior license that may no longer be current — verify license validity.
- One shipment has no end-user statement and a freight forwarder reporting a destination change mid-process — assess what that means.
- Customer + end-user PII is partially redacted in mock; the system you design must handle full data appropriately.
