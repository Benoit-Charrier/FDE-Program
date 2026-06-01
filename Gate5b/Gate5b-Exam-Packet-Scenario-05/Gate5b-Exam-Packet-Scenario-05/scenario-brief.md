# Final Exam Scenario — Export Control Review at Ferrum Industrial Group

**FDE Accelerated Development Program v4.2 — Gate 5b Final Practical Exam**
**Released:** 08:45 CET, Virtual Friday Week 5 (the clock begins at 09:00).

---

## Engagement context

**Ferrum Industrial Group** is a U.S. manufacturer of precision industrial sensors, controls, and specialty alloys serving aerospace, energy, semiconductor, and defense markets. ~3,400 employees, ~$1.4B annual revenue, HQ in Cleveland OH, manufacturing in OH / TX / and through a JV in Ireland. Exports to ~40 countries.

You've been engaged as a Forward Deployed Engineer by Ferrum's VP of Trade Compliance, **Greer Aldecombe** (reporting to General Counsel). Her brief:

> "We process about 1,400 outbound shipment files per week through our Export Compliance Operations team. Every shipment needs an ECCN classification check, a denied-parties screening on consignee + end-user + freight forwarder + any visible downstream parties, and an end-use review. License determination if applicable. The vast majority are routine commodity-grade — go through fast. A meaningful subset are technology-controlled with real export-license implications. And a small but consequential subset are problematic — a denied-party hit, a dual-use technology going to a jurisdiction that just changed, an end-user statement that doesn't ring true. Our 16 trade compliance analysts spend 20 to 60 minutes per shipment file. We're at 4.3 days median cycle time, which means we're holding $40M of shipped revenue at any given moment in compliance hold. And one missed denied-party hit is a 20-year prison risk for whoever signed off."
>
> "Trade Compliance Platform budget this year is $445K for AI-assisted shipment review build + first-year run. I am not asking AI to make the license-determination call. I'm asking AI to do the synthesis work — parse the shipment documents, propose an ECCN, run the denied-parties screening, surface end-use red flags, and recommend a disposition for the analyst. The analyst signs."

## Your role and scope

Design and prototype an **agentic export-controls shipment review system** for Ferrum's outbound shipments. The system must reduce per-shipment analyst handling time and produce a structured "shipment review package": ECCN classification recommendation, denied-parties screening results with disposition reasoning, end-use red-flag surface, recommended disposition (release / hold-for-license / hold-for-clarification / deny / out-of-scope).

**What the system needs to do** (the cognitive work to be delegated):

1. **Ingest the shipment file** — purchase order, packing list, commercial invoice, end-user statement, freight forwarder communications, any prior license/exception documentation.
2. **Propose an ECCN classification** — matching product description against the Export Administration Regulations (EAR) Commerce Control List, with reasoning per the relevant CCL category, against any prior classifications on file for the same product.
3. **Run denied-parties screening** — consignee, end-user, freight forwarder, and any visible downstream parties against OFAC SDN list, BIS Entity List, BIS Unverified List, State DDTL, and Ferrum's internal blocked list.
4. **Surface end-use red flags** — diversion-risk patterns, end-use statements that don't align with the product, jurisdiction-of-installation vs jurisdiction-of-consignee mismatches.
5. **Recommend disposition** — release / hold-for-license / hold-for-clarification / deny / route-out-of-scope, with reasoning and span-level citations to the underlying shipment documents.

**Scope guardrails** (from Greer):

- **Not delegated:** the license-determination decision. Analyst signs.
- **Not delegated:** the deny decision. Analyst recommends; Compliance Counsel approves.
- **Not delegated:** denied-parties positive confirmation. The system surfaces matches; an analyst confirms hit-vs-false-positive with reasoning.
- **Not delegated:** any communication with the customer, consignee, freight forwarder, or any government body.
- **In scope:** commercial exports from U.S. facilities (OH, TX). Re-exports from the Irish JV where Ferrum has signed-off control.
- **Out of scope:** ITAR-controlled (defense article) shipments — separate license process under State DDTC, separate team. Munitions List items. Encryption-only software shipments (separate BIS encryption-review workflow).

## Stakeholder landscape

| Stakeholder | Their concern |
|---|---|
| **Greer Aldecombe** (VP Trade Compliance, executive sponsor) | Cycle time. Defensibility to BIS. Denied-parties screening completeness. |
| **Jordan Pellegrini** (CFO) | $40M shipped revenue on compliance hold at any moment. Penalty exposure if wrong. |
| **Ravi Sundaram** (General Counsel, Greer's boss) | "Anything AI touches must be defensible to a BIS examiner." Personal risk attribution if the company signs off a denied-party shipment. |
| **Anders Bredsdorff** (VP Commercial, semiconductor BU) | Customer relationships. Loses deals when shipments sit in compliance for a week. |
| **Marisol Vega-Cantarella** (Senior Trade Compliance Analyst, 12 years at Ferrum, design partner) | Wants augmentation. "I am tired of looking at the same shipment from the same customer to the same end user for the 200th time. I want AI to do that one. Save my time for the hard cases." |
| **Special Agent Tyrese Walls** (External BIS examiner — relationship contact for Ferrum's voluntary self-disclosure history) | Will not approve a black-box. Reproducibility of classification and screening decisions. |

## The data you have

Sealed mock-data pack at `mock-data/`. Eight active outbound shipment files received in the past 3 business days across:

- Routine commodity-grade sensor shipment to a long-standing European customer (clean baseline)
- Specialty alloy shipment to a new consignee in Türkiye with a downstream end user not previously documented
- A semiconductor-equipment-component shipment to a Singaporean broker with a stated end use that doesn't ring true
- A denied-parties hit on the consignee (BIS Entity List)
- A shipment that includes an ITAR-controlled item incorrectly routed through the commercial export queue (out-of-scope)
- A re-export from the Irish JV with EU consignee documentation in German
- A shipment with a stale prior license (license expired)
- A shipment to a freight-forwarder whose ultimate destination changed mid-process

Total ~22 files. Format mix: purchase order PDFs, packing-list CSVs, end-user statements (.txt), freight forwarder emails (.eml), denied-parties screening outputs (text reports), ECCN reference extracts, prior license extracts.

## Success metrics (Greer's framing)

| Metric | Baseline | Target |
|---|---:|---:|
| Per-shipment analyst handling time | 38 min | ≤ 10 min |
| Compliance-hold cycle time (median) | 4.3 days | ≤ 1.5 days |
| ECCN classification recommendation precision (analyst accepts as-is) | n/a | ≥ 90% |
| Denied-parties screening recall (system surfaces every hit a human would catch) | n/a | 100% |
| Per-shipment audit-trail completeness (machine-generated for BIS examination) | partial today | 100% |
| Reproducibility of disposition recommendations | n/a | 100% across audit sample |

## Constraints

- **Claude Code is the required build tool.** Mock data is required for the prototype.
- **Customer + end-user data handling** — defensible to BIS examiner. Architectural constraint.
- **8-hour clock** (09:00–17:00 CET). 4.5h design, 30-min curveball adaptation, 3h build incl. self-assessment + submission.
- **Solo.** No coach Q&A, no peer interaction. Claude Code is your only AI tool. Internet permitted for reference only (EAR, BIS guidance, CCL).
- The **scoring rubric** is released at 09:00 sharp alongside this brief.

## What to read first

Start with `mock-data/shipment-queue/queue.md` — the shipment file roster. Then sample a few across the destination + product-type mix.

You will receive a **curveball at 13:30 CET** that you will need to incorporate into your revised design before the build phase begins at 14:00. Plan for that.

---

*Sealed scenario — Final Exam, Gate 5b. Released 08:45 CET, Virtual Friday Week 5. Do not distribute or discuss with any person other than your proctor.*
