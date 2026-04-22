from __future__ import annotations
from datetime import datetime, timezone
from dataclasses import dataclass
from typing import Optional
import audit
import approval as approval_module
from metrics import MetricsSummary

QUEUE_LABELS = {
    "standard": ("STANDARD", "#2d6a2d", "#e8f5e9"),
    "playbook_negotiable": ("PLAYBOOK NEGOTIABLE", "#7a5c00", "#fff8e1"),
    "senior_lawyer_escalation": ("ESCALATION", "#8b0000", "#fdecea"),
    "error": ("ERROR", "#555", "#f5f5f5"),
}

STATUS_LABELS = {
    "match": ("MATCH", "#2d6a2d", "#e8f5e9"),
    "negotiable_deviation": ("DEVIATION", "#7a5c00", "#fff8e1"),
    "escalate": ("ESCALATE", "#8b0000", "#fdecea"),
    "optional_clause_absent": ("OPTIONAL-ABSENT", "#666", "#f5f5f5"),
}


def generate(results: list[dict], errors: list[dict], metrics: MetricsSummary, output_path: str) -> None:
    html = _build_html(results, errors, metrics)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)


def _badge(label: str, color: str, bg: str) -> str:
    return (
        f'<span style="background:{bg};color:{color};border:1px solid {color};'
        f'padding:2px 8px;border-radius:4px;font-weight:bold;font-size:0.85em">{label}</span>'
    )


def _queue_badge(queue: str) -> str:
    label, color, bg = QUEUE_LABELS.get(queue, ("UNKNOWN", "#333", "#eee"))
    return _badge(label, color, bg)


def _status_badge(status: str) -> str:
    label, color, bg = STATUS_LABELS.get(status, ("UNKNOWN", "#333", "#eee"))
    return _badge(label, color, bg)


def _build_html(results: list[dict], errors: list[dict], metrics: MetricsSummary) -> str:
    now = datetime.now(timezone.utc).isoformat()
    total = len(results) + len(errors)

    queue_counts = {}
    for r in results:
        q = r.get("queue", "error")
        queue_counts[q] = queue_counts.get(q, 0) + 1

    summary_cards = _summary_cards(total, queue_counts, len(errors))
    metrics_table = _metrics_table(metrics)
    contract_rows = "".join(_contract_row(r, i) for i, r in enumerate(results))
    error_rows = "".join(_error_row(e) for e in errors)
    error_section = f"""
    <h2 style="margin-top:2rem">Ingestion Errors</h2>
    <table style="width:100%;border-collapse:collapse">
      <thead><tr>
        <th style="text-align:left;padding:8px;border-bottom:2px solid #ddd">File</th>
        <th style="text-align:left;padding:8px;border-bottom:2px solid #ddd">Reason</th>
      </tr></thead>
      <tbody>{error_rows}</tbody>
    </table>""" if errors else ""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Vendor Contract Review — Queue Report</title>
<style>
  body {{font-family:system-ui,sans-serif;margin:0;padding:1.5rem;background:#fafafa;color:#222}}
  h1 {{margin-bottom:.25rem}}
  .subtitle {{color:#666;margin-bottom:1.5rem;font-size:.9em}}
  .cards {{display:flex;gap:1rem;flex-wrap:wrap;margin-bottom:1.5rem}}
  .card {{background:#fff;border:1px solid #ddd;border-radius:6px;padding:1rem 1.5rem;min-width:120px}}
  .card-num {{font-size:2rem;font-weight:bold}}
  .card-label {{font-size:.8rem;color:#666;text-transform:uppercase}}
  table {{width:100%;border-collapse:collapse;background:#fff;border:1px solid #ddd;border-radius:6px;overflow:hidden}}
  th {{text-align:left;padding:10px 12px;background:#f0f0f0;border-bottom:2px solid #ddd;font-size:.85em;text-transform:uppercase}}
  td {{padding:10px 12px;border-bottom:1px solid #eee;vertical-align:top;font-size:.9em}}
  tr:last-child td {{border-bottom:none}}
  .detail-panel {{display:none;background:#f9f9f9;padding:1rem;border-top:1px solid #ddd}}
  .detail-panel.open {{display:block}}
  .tabs {{display:flex;gap:.5rem;margin-bottom:1rem;border-bottom:2px solid #ddd}}
  .tab-btn {{padding:6px 14px;border:none;background:none;cursor:pointer;font-size:.9em;border-bottom:2px solid transparent;margin-bottom:-2px}}
  .tab-btn.active {{border-bottom-color:#2255aa;color:#2255aa;font-weight:bold}}
  .tab-pane {{display:none}}
  .tab-pane.active {{display:block}}
  .redline-block {{background:#fff;border:1px solid #ddd;border-radius:4px;padding:.75rem;margin-bottom:.75rem}}
  .redline-label {{font-size:.8em;text-transform:uppercase;color:#888;margin-bottom:.25rem}}
  .original-text {{background:#fdecea;padding:.5rem;border-radius:3px;font-family:monospace;font-size:.82em;white-space:pre-wrap;margin-bottom:.5rem}}
  .proposed-text {{background:#e8f5e9;padding:.5rem;border-radius:3px;font-family:monospace;font-size:.82em;white-space:pre-wrap}}
  .citation {{font-size:.75em;color:#888;margin-top:.25rem}}
  .clause-text {{font-family:monospace;font-size:.8em;color:#444;max-width:360px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}}
  .expand-btn {{background:#2255aa;color:#fff;border:none;padding:4px 12px;border-radius:4px;cursor:pointer;font-size:.85em}}
  .audit-entry {{font-size:.8em;font-family:monospace;border-bottom:1px solid #eee;padding:4px 0}}
  .release-banner {{padding:.5rem 1rem;border-radius:4px;font-weight:bold;margin-bottom:1rem;font-size:.9em}}
  .release-blocked {{background:#fdecea;color:#8b0000;border:1px solid #8b0000}}
  .release-cleared {{background:#e8f5e9;color:#2d6a2d;border:1px solid #2d6a2d}}
  .approval-tag {{font-size:.8em;color:#2d6a2d;font-weight:bold}}
  .awaiting-tag {{font-size:.8em;color:#8b0000;font-weight:bold}}
</style>
</head>
<body>
<h1>Vendor Contract Review — Queue Report</h1>
<p class="subtitle">Generated: {now}</p>
{summary_cards}
{metrics_table}
<h2>Contracts</h2>
<table>
  <thead><tr>
    <th>File</th>
    <th>Queue</th>
    <th>Clauses</th>
    <th>Release</th>
    <th>Routing reason</th>
    <th></th>
  </tr></thead>
  <tbody>{contract_rows}</tbody>
</table>
{error_section}
<script>
function toggleDetail(id) {{
  var panel = document.getElementById('panel-' + id);
  panel.classList.toggle('open');
}}
function switchTab(contractId, tabName) {{
  var panes = document.querySelectorAll('.tab-pane[data-contract="' + contractId + '"]');
  var btns = document.querySelectorAll('.tab-btn[data-contract="' + contractId + '"]');
  panes.forEach(function(p) {{ p.classList.remove('active'); }});
  btns.forEach(function(b) {{ b.classList.remove('active'); }});
  document.getElementById('tab-' + contractId + '-' + tabName).classList.add('active');
  document.querySelector('.tab-btn[data-contract="' + contractId + '"][data-tab="' + tabName + '"]').classList.add('active');
}}
</script>
</body>
</html>"""


def _summary_cards(total: int, queue_counts: dict, error_count: int) -> str:
    standard = queue_counts.get("standard", 0)
    negotiable = queue_counts.get("playbook_negotiable", 0)
    escalation = queue_counts.get("senior_lawyer_escalation", 0)
    return f"""<div class="cards">
  <div class="card"><div class="card-num">{total}</div><div class="card-label">Total Contracts</div></div>
  <div class="card" style="border-color:#2d6a2d"><div class="card-num" style="color:#2d6a2d">{standard}</div><div class="card-label">Standard</div></div>
  <div class="card" style="border-color:#7a5c00"><div class="card-num" style="color:#7a5c00">{negotiable}</div><div class="card-label">Playbook Negotiable</div></div>
  <div class="card" style="border-color:#8b0000"><div class="card-num" style="color:#8b0000">{escalation}</div><div class="card-label">Escalation</div></div>
  <div class="card" style="border-color:#555"><div class="card-num" style="color:#555">{error_count}</div><div class="card-label">Errors</div></div>
</div>"""


def _metrics_table(m: MetricsSummary) -> str:
    if m.total_contracts == 0:
        return ""

    esc = f"{m.escalation_rate}%" if m.escalation_rate is not None else "—"
    override = f"{m.override_rate}%" if m.override_rate is not None else "0%"
    latency = f"{m.approval_latency_seconds}s" if m.approval_latency_seconds is not None else "—"

    turnaround_rows = "".join(
        f"<tr><td style='padding:6px 12px'>Mean turnaround — {q}</td><td style='padding:6px 12px'>{v}s</td></tr>"
        for q, v in m.mean_turnaround_by_queue.items()
    )
    dist_rows = "".join(
        f"<tr><td style='padding:6px 12px'>Route: {q}</td><td style='padding:6px 12px'>{v['count']} ({v['pct']}%)</td></tr>"
        for q, v in m.route_distribution.items()
    )

    return f"""<details style="margin-bottom:1.5rem">
  <summary style="cursor:pointer;font-weight:bold;font-size:1rem;margin-bottom:.5rem">Operational Metrics</summary>
  <table style="margin-top:.5rem;max-width:500px">
    <thead><tr><th>Metric</th><th>Value</th></tr></thead>
    <tbody>
      {dist_rows}
      <tr><td style='padding:6px 12px'>Escalation rate</td><td style='padding:6px 12px'>{esc}</td></tr>
      {turnaround_rows}
      <tr><td style='padding:6px 12px'>Override rate</td><td style='padding:6px 12px'>{override}</td></tr>
      <tr><td style='padding:6px 12px'>Approval latency</td><td style='padding:6px 12px'>{latency}</td></tr>
    </tbody>
  </table>
</details>"""


def _contract_row(r: dict, idx: int) -> str:
    cid = r["contract_id"]
    queue = r.get("queue", "error")
    matched = sum(1 for c in r.get("classifications", []) if c["status"] == "match")
    total_clauses = len(r.get("classifications", []))
    routing_reason = r.get("routing_reason", "")

    ap_state = approval_module.get_approval_state(cid)
    release_status = ap_state.get("release_status", "") if ap_state else ""
    release_cell = ""
    if release_status == "blocked":
        release_cell = _badge("BLOCKED", "#8b0000", "#fdecea")
    elif release_status == "cleared":
        release_cell = _badge("CLEARED", "#2d6a2d", "#e8f5e9")

    detail = _contract_detail(r, idx, ap_state)

    return f"""<tr>
  <td><strong>{cid}</strong></td>
  <td>{_queue_badge(queue)}</td>
  <td>{matched}/{total_clauses}</td>
  <td>{release_cell}</td>
  <td style="color:#555;font-size:.85em">{routing_reason}</td>
  <td><button class="expand-btn" onclick="toggleDetail({idx})">Details</button></td>
</tr>
<tr>
  <td colspan="6" style="padding:0">
    <div id="panel-{idx}" class="detail-panel">
      {detail}
    </div>
  </td>
</tr>"""


def _contract_detail(r: dict, idx: int, ap_state: dict) -> str:
    cid = r["contract_id"]
    tabs = _clause_tab(r, cid, idx) + _redlines_tab(r, cid, idx, ap_state) + _audit_tab(cid, idx)
    tab_btns = f"""<div class="tabs">
  <button class="tab-btn active" data-contract="{idx}" data-tab="clauses" onclick="switchTab('{idx}','clauses')">Clause Analysis</button>
  <button class="tab-btn" data-contract="{idx}" data-tab="redlines" onclick="switchTab('{idx}','redlines')">Redlines</button>
  <button class="tab-btn" data-contract="{idx}" data-tab="audit" onclick="switchTab('{idx}','audit')">Audit Trail</button>
</div>"""
    return tab_btns + tabs


def _clause_tab(r: dict, cid: str, idx: int) -> str:
    rows = ""
    for c in r.get("classifications", []):
        excerpt = (c["extracted_text"][:300] + "…") if len(c.get("extracted_text", "")) > 300 else c.get("extracted_text", "")
        conf = f"{c['confidence']:.2f}"
        rows += f"""<tr>
      <td>{c['family']}</td>
      <td>{_status_badge(c['status'])}</td>
      <td>{conf}</td>
      <td><code>{c['reason_code']}</code></td>
      <td class="clause-text" title="{c.get('extracted_text','')}">{excerpt}</td>
    </tr>"""
    return f"""<div id="tab-{idx}-clauses" class="tab-pane active" data-contract="{idx}">
  <table style="width:100%;border-collapse:collapse">
    <thead><tr>
      <th>Clause Family</th><th>Status</th><th>Confidence</th><th>Reason Code</th><th>Extracted Text</th>
    </tr></thead>
    <tbody>{rows}</tbody>
  </table>
</div>"""


def _redlines_tab(r: dict, cid: str, idx: int, ap_state: dict) -> str:
    redlines = r.get("redlines", [])
    if not redlines:
        content = "<p style='color:#666;font-size:.9em'>No redlines for this contract.</p>"
    else:
        release_status = ap_state.get("release_status", "blocked") if ap_state else "blocked"
        banner_class = "release-blocked" if release_status == "blocked" else "release-cleared"
        banner_text = "BLOCKED — awaiting named-lawyer sign-off" if release_status == "blocked" else "CLEARED — all clauses approved"
        content = f'<div class="release-banner {banner_class}">{banner_text}</div>'

        for rl in redlines:
            family = rl["family"]
            clause_ap = ap_state.get("clauses", {}).get(family, {}) if ap_state else {}
            if clause_ap.get("approved"):
                ap_html = f'<span class="approval-tag">✓ Approved by {clause_ap["lawyer_name"]} on {clause_ap["timestamp"]}</span>'
            else:
                ap_html = '<span class="awaiting-tag">⏳ Awaiting sign-off</span>'

            content += f"""<div class="redline-block">
  <strong>{family}</strong> {ap_html}
  <div class="redline-label" style="margin-top:.5rem">Original text</div>
  <div class="original-text">{rl['original_text']}</div>
  <div class="redline-label">Proposed replacement (from playbook)</div>
  <div class="proposed-text">{rl['proposed_text']}</div>
  <div class="citation">Playbook citation: {rl['playbook_citation']}</div>
</div>"""

    return f"""<div id="tab-{idx}-redlines" class="tab-pane" data-contract="{idx}">
  {content}
</div>"""


def _audit_tab(cid: str, idx: int) -> str:
    events = audit.query_by_contract(cid)
    if not events:
        entries = "<p style='color:#666;font-size:.9em'>No audit events recorded.</p>"
    else:
        entries = "".join(
            f'<div class="audit-entry">{e["timestamp"]} | <strong>{e["event_type"]}</strong></div>'
            for e in events
        )
    return f"""<div id="tab-{idx}-audit" class="tab-pane" data-contract="{idx}">
  <div style="max-height:300px;overflow-y:auto">{entries}</div>
</div>"""


def _error_row(e: dict) -> str:
    return f"<tr><td>{e['filename']}</td><td><code>{e['reason']}</code></td></tr>"
