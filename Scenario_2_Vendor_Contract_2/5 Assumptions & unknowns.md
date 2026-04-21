# Deliverable 5 — Assumptions & Unknowns

The following unknowns are genuine blockers or risk factors that must be validated before committing to a build. They are not filler — each one, if wrong, changes the scope, the architecture, or the feasibility of the solution materially.

---

## 1. The negotiation playbook exists as a structured, codifiable artefact

**Assumption**: The playbook can be expressed as a set of explicit rules: accepted clause positions, approved fallback language, escalation conditions, and paralegal authority boundaries. The agent's routing and redline logic depends entirely on this structure being machine-readable.

**Why this is unknown**: Many legal playbooks exist as a senior lawyer's institutional memory, informal email threads, or loosely organised Word documents with phrases like "usually we push back on this." If the playbook cannot be converted into a structured config without losing essential nuance, the agent will either over-escalate (useless) or under-escalate (dangerous). This must be validated before any engineering starts.

**What to do**: Conduct a structured playbook-extraction session with the legal team. Ask them to walk through 10 recent contracts and narrate every decision. If they can do so with consistent rules, the playbook is codifiable. If each decision requires case-by-case reasoning, the scope needs to be narrowed or the approach rethought.

---

## 2. The majority of inbound contracts arrive as machine-readable files, not scanned images

**Assumption**: Most of the ~300 contracts per quarter are natively digital PDFs or DOCX files with selectable text. Clause extraction quality degrades significantly on scanned documents.

**Why this is unknown**: The scenario mentions the legal team receives inbound vendor contracts but does not describe the intake channel. Some vendor ecosystems — particularly in manufacturing, financial services, or older procurement systems — routinely send scanned PDFs. If 30–40% of the intake is image-based, the extraction pipeline needs a different approach (OCR + higher confidence thresholds + more aggressive escalation), and the cost and accuracy profile changes substantially.

**What to do**: Pull a sample of 30 recent inbound contracts and measure what percentage are native digital vs. scanned. Also check whether any contracts arrive as HTML, Google Docs links, or other formats not covered by the PDF/DOCX ingestion path.

---

## 3. The paralegal's redline authority is formally defined and consistently applied today

**Assumption**: There is a clear, agreed boundary between what the paralegal can redline independently and what requires lawyer sign-off. The agent's playbook-negotiable routing depends on this boundary being real, not aspirational.

**Why this is unknown**: In practice, paralegal authority in legal teams is often informal and relationship-dependent. The paralegal may currently run deviations past a lawyer informally before sending them — which means the "20% paralegal-handled" figure in the scenario may already have embedded lawyer involvement that isn't visible in the workflow description. If that's the case, the routing model will need to reflect the real workflow, not the stated one.

**What to do**: Interview both the paralegal and at least two lawyers about the last 20 playbook-negotiable contracts. How many of those did the paralegal send without any lawyer consultation? Document the actual authority boundary, not the assumed one.

---

## 4. Named-lawyer sign-off can be captured and verified electronically at the clause level

**Assumption**: The organisation can implement a system that records which named lawyer approved which specific clause, with a timestamp, in a way that is auditable and legally defensible. This is the technical expression of the general counsel's hard rule.

**Why this is unknown**: Many legal teams currently manage approvals via email threads, Slack messages, or verbal confirmation — none of which are clause-level, timestamped, or tied to a specific contract version. Building the approval gate requires either integrating with an existing approval system (CLM, DocuSign, or similar) or building one. If the organisation has no approval infrastructure and is resistant to adopting one, the governance control the general counsel requires cannot be implemented in a reliable way.

**What to do**: Determine what approval and signature infrastructure currently exists. If it's email-based, assess whether the organisation will accept a lightweight purpose-built approval UI, or whether a CLM integration is required before the agent can go live.

---

## 5. Historical contracts with known outcomes are available for calibration and testing

**Assumption**: The team can provide a labelled sample of past contracts — ideally 50 or more — with their final disposition (standard / redlined / escalated) and the specific clauses that drove each decision. This is needed to calibrate the confidence thresholds, validate the playbook rules, and test the extraction pipeline.

**Why this is unknown**: Historical legal documents are often subject to confidentiality obligations, privilege concerns, or are simply not organised in a way that makes them accessible for testing. The team may be uncomfortable sharing real vendor contracts even internally for an AI project. If historical data is unavailable, the only alternative is building synthetic fixtures — which adds time and introduces the risk that synthetic contracts do not reflect the real variance in the intake population.

**What to do**: Ask the general counsel whether a sample of past contracts can be used for system validation. If not, determine whether synthetic contracts can be derived from anonymised clause patterns, or whether a pilot with a small live cohort is the only viable calibration path.

---

## 6. The 90-minute average review time is consistent across the three routing categories

**Assumption**: The 90-minute figure applies evenly across standard, negotiable, and escalation contracts. If it does, the time-saving opportunity is roughly proportional to volume (70% standard = largest opportunity). If standard contracts actually take 45 minutes and escalations take 3 hours, the prioritisation logic changes.

**Why this is unknown**: Average figures mask variance. The scenario states 90 minutes as the overall average but gives no breakdown by complexity. An agent that automates standard-contract review may save less wall-clock time than expected if those contracts were already being handled quickly, while the real bottleneck is the back-and-forth on escalations.

**What to do**: Ask the legal team to time-track a two-week sample of reviews by contract type. Even rough data (under 1 hour / 1–2 hours / over 2 hours) will materially improve the ROI model and prioritisation.

---

## 7. Procurement's definition of "unworkable" turnaround is a shared understanding across the organisation

**Assumption**: Reducing turnaround to 1–2 business days will satisfy the procurement team and resolve the stated organisational friction. The procurement team and the legal team have agreed on what an acceptable SLA looks like.

**Why this is unknown**: "Unworkable" is the procurement team's characterisation. It may reflect a few specific high-profile delays rather than a systemic problem across all 300 quarterly contracts. If the bottleneck is actually the 30 escalation contracts — where the legal team is slow to make strategic decisions, not slow to do first-pass review — then automating first-pass review will not fix the procurement team's pain. The solution might need to focus on escalation triage speed rather than standard-contract throughput.

**What to do**: Have a direct conversation with 2–3 procurement leads about the last 5 times a contract delay blocked a purchasing decision. Was the delay in first-pass review, in the escalation decision, or in the back-and-forth after the counteroffer? The answer shapes where to invest.
