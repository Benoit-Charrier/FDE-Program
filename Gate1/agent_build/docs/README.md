# FNOL Processing Agent — Build Artefacts

## Running the console application

```bash
python agent_build/src/main.py \
  --input agent_build/data/sample_claim.json \
  --mock-policy agent_build/data/mock_policy.json \
  --mock-adjusters agent_build/data/mock_adjusters.json \
  --output-dir agent_build/output
```

The application writes two files to `--output-dir`:
- `report.html` — inline-CSS HTML processing report
- `claim_result.json` — final Claim record as JSON

## Rendering the workflow diagram

The diagram in `workflow.md` uses [Mermaid](https://mermaid.js.org/) syntax.

### Option 1 — Mermaid CLI (recommended)

```bash
npm install -g @mermaid-js/mermaid-cli
mmdc -i agent_build/docs/workflow.md -o agent_build/docs/workflow.png
```

### Option 2 — VS Code

Install the [Mermaid Preview](https://marketplace.visualstudio.com/items?itemName=bierner.markdown-mermaid) extension, then open `workflow.md` and use the Markdown preview panel.

### Option 3 — Online

Paste the Mermaid block into [mermaid.live](https://mermaid.live/) to preview and export.

## Data files

| File | Purpose |
|---|---|
| `data/sample_claim.json` | Example motor claim (EMAIL channel) |
| `data/mock_policy.json` | Mock policy record replacing the SOAP endpoint |
| `data/mock_adjusters.json` | Mock adjuster pool replacing the CRM REST query |

## Environment variables

Copy `.env` and set `ANTHROPIC_API_KEY` if extending the agent to use real LLM inference.

## No external dependencies

The console application runs on Python 3.8+ standard library only — no `pip install` required.
