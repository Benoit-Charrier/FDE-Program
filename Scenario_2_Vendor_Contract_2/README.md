# Introduction
I built the 5 deliverables in 5 .md files
"1 Problem statement and success metrics.md"
"2 Delegation analysis.md"
"3 Capability specification.md"
"4 Validation design.md"
"5 Assumptions & unknowns.md"

I concatenated these these files in critique-pool-KTB-3-410.md for the submission so you can review this

I  built "\Output\workflow-diagram.html" to show the workflow in a user friendly html format so you can take a look at this too

I built a Claude.md file to ask Claude Code to build the app
How to run the app and the output is further below

I ran a couple of tests, did some fixes and built "built-loop-diagnostic" to show the kind of errors and fixes

I also ran a validation against the primer and made some fixes

Of course all of this with Claude code, I didn't write one single line in these files (well except a couple because it was quicker than asking Claude code)

# Inbound Vendor Contract Review Agent

Console application that automates first-pass review of vendor contracts against a legal negotiation playbook, enforces named-lawyer sign-off on negotiated outbound packages, and generates an HTML queue report.

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

## Create sample fixtures

```bash
python create_fixtures.py
```

This generates three DOCX test contracts in `Input Contracts/`.

## Run analysis

```bash
python run.py
# or specify paths:
python run.py --input "Input Contracts" --output "Output/report.html"
```

Opens `Output/report.html` in a browser to see the queue report.

## Record lawyer sign-off

```bash
python approve.py --contract "sample_negotiable.docx" --clause liability_cap --lawyer "Jane Smith"
python approve.py --contract "sample_negotiable.docx" --clause sla --lawyer "Jane Smith"
```

## Attempt outbound release

```bash
python release.py --contract "sample_negotiable.docx"
# [BLOCKED] until all clauses are approved
# [CLEARED] once all clauses have named-lawyer sign-off
```

Re-run `python run.py` after approvals to refresh the HTML report with updated release status.

## Project structure

```
run.py               — main analysis pipeline
approve.py           — record named-lawyer clause approval
release.py           — enforce outbound release gate
ingestion.py         — FR-01: PDF/DOCX ingestion
extraction.py        — FR-02: clause extraction via Claude Haiku
classification.py    — FR-03, FR-09, FR-11: playbook matching
routing.py           — FR-04: queue assignment
redlines.py          — FR-05, FR-06: redline generation
approval.py          — FR-07: approval state management
audit.py             — FR-08: append-only audit log
metrics.py           — FR-10: operational metrics
report.py            — FR-12: HTML report generation
config/playbook.json — all legal policy values (edit here, no code changes needed)
data/                — runtime state (audit.jsonl, analysis_results.json, approvals.json)
Input Contracts/     — drop contracts here
Output/              — report.html written here
```

## Playbook configuration

Edit `config/playbook.json` to update thresholds, approved jurisdictions, escalation triggers, accepted positions, or negotiable deviations. No code change required (FR-09).

## Known Limitations

- Approval workflow is CLI-only; no email notifications or integrated CLM.
- Metrics require re-running `run.py` to refresh; no live dashboard.
- DOCX page numbers are approximated by word count (350 words/page).
