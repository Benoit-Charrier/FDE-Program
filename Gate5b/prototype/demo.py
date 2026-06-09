"""LACRA demo script — four-path demonstration.

Usage:
    python -m prototype.demo            # all four paths
    python -m prototype.demo --path 1   # single path (1–4)

Paths demonstrated:
    1  Primary flow      AML-1208  C-CON-9923441   Watchlist FP  → CLEAR
    2  SAR escalation    AML-1408  C-CON-6611442   Layering      → ESCALATE_SAR
    3  OOS routing       AML-1322  C-CON-5530118   Remittance    → ROUTE_OUT_OF_SCOPE
    4  Graceful degrade  synthetic C-CON-0000001   No data       → FURTHER_INFO_NEEDED
"""
import argparse
import json
import sys
from prototype.agent import run_lacra

# Force UTF-8 on Windows consoles so box-drawing and arrow characters render
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf_8"):
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

W = 70  # output width


def _bar(char="─"):
    return char * W


def _header(title: str, subtitle: str = "") -> None:
    print(f"\n┌{_bar()}┐")
    print(f"│  {title:<{W - 3}}│")
    if subtitle:
        print(f"│  {subtitle:<{W - 3}}│")
    print(f"└{_bar()}┘")


def _section(label: str, value: str) -> None:
    print(f"  {label:<22}{value}")


def _bullet(text: str, indent: int = 25) -> None:
    print(f"{' ' * indent}· {text}")


def _divider() -> None:
    print(f"  {_bar('·')}")


def print_case(path_num: int, label: str, subtitle: str, result: dict) -> None:
    _header(f"PATH {path_num} — {label}", subtitle)

    if "error" in result:
        print(f"  ERROR: {result['error']}")
        return

    scope = result.get("scope_classification", "—")
    disp = result.get("disposition", {})
    rec  = disp.get("recommendation", "—")
    conf = disp.get("confidence")

    _section("Scope:", scope)
    conf_str = f"  (confidence {conf:.2f})" if conf is not None else ""
    _section("Disposition:", f"{rec}{conf_str}")

    # Watchlist
    ws = result.get("watchlist_status")
    if ws:
        res = ws.get("resolution", "—")
        wconf = ws.get("confidence")
        wconf_str = f"  confidence={wconf:.2f}" if wconf is not None else ""
        _section("Watchlist:", f"{res}{wconf_str}")
        for ev in ws.get("disconfirmation_evidence", [])[:3]:
            _bullet(ev)

    # Patterns
    patterns = result.get("patterns_detected") or []
    for p in patterns:
        _section("Pattern:", f"{p['pattern_type']}  severity={p['severity']}")
        for ev in p.get("evidence", [])[:2]:
            _bullet(ev)

    # OOS routing
    routing = result.get("routing")
    if routing:
        _section("Route →", routing.get("destination", "—"))
        _bullet(routing.get("reason", ""))

    # SAR clock
    sar = result.get("sar_clock_start_utc")
    if sar:
        _section("SAR clock T0:", f"{sar}  (30-day FinCEN filing window)")

    # Data gaps
    gaps = result.get("data_gaps") or []
    if gaps:
        _section("Data gaps:", f"{len(gaps)} item(s)")
        for g in gaps[:4]:
            _bullet(g)
        if len(gaps) > 4:
            _bullet(f"… {len(gaps) - 4} more")

    # Narrative excerpt
    narrative = result.get("narrative")
    if narrative:
        _divider()
        excerpt = narrative[:280].rsplit(" ", 1)[0] + " …"
        wrapped = "\n  ".join(
            excerpt[i:i + W - 4] for i in range(0, len(excerpt), W - 4)
        )
        print(f"  Narrative:\n  {wrapped}")

    # Disposition reasoning (brief)
    reasoning = disp.get("reasoning", "")
    if reasoning and rec != "ROUTE_OUT_OF_SCOPE":
        _divider()
        excerpt = reasoning[:220].rsplit(" ", 1)[0] + " …"
        wrapped = "\n  ".join(
            excerpt[i:i + W - 4] for i in range(0, len(excerpt), W - 4)
        )
        print(f"  Reasoning:\n  {wrapped}")

    # Audit log
    audit = result.get("_audit_log", {})
    if audit:
        _divider()
        print(
            f"  Audit ID:  {audit.get('audit_id')}\n"
            f"  Duration:  {audit.get('processing_duration_ms')} ms"
        )


CASES = [
    (
        1,
        "Primary flow: watchlist false-positive → CLEAR",
        "Alert AML-1208 · C-CON-9923441 (Mohammed Khan, F-1 student, Wayne State)",
        dict(
            alert_id="CASE-2026-05-13-AML-1208",
            customer_id="C-CON-9923441",
            triggered_at_utc="2026-05-13T09:38:00Z",
        ),
    ),
    (
        2,
        "SAR escalation: layering across linked accounts → ESCALATE_SAR",
        "Alert AML-1408 · C-CON-6611442 (4 accounts, device dev-android-7011)",
        dict(
            alert_id="CASE-2026-05-15-AML-1408",
            customer_id="C-CON-6611442",
            triggered_at_utc="2026-05-15T02:55:00Z",
        ),
    ),
    (
        3,
        "OOS routing: remittance product → ROUTE_OUT_OF_SCOPE",
        "Alert AML-1322 · C-CON-5530118 (channel=cross-border-remittance, AM-01)",
        dict(
            alert_id="CASE-2026-05-14-AML-1322",
            customer_id="C-CON-5530118",
            triggered_at_utc="2026-05-14T18:08:00Z",
        ),
    ),
    (
        4,
        "Graceful degradation: no data → FURTHER_INFO_NEEDED",
        "Synthetic C-CON-0000001 (no files exist; all tool calls return None)",
        dict(
            alert_id="CASE-TEST-MISSING-DATA",
            customer_id="C-CON-0000001",
            triggered_at_utc="2026-05-15T00:00:00Z",
        ),
    ),
]


def _summary(results: list[tuple[int, str, dict]]) -> None:
    print(f"\n{'═' * W}")
    print(f"  {'PATH':<6}{'DISPOSITION':<28}{'SCOPE':<26}{'ms':>6}")
    print(f"  {'─' * 4}  {'─' * 24}  {'─' * 22}  {'─' * 6}")
    for num, label, result in results:
        if "error" in result:
            row_disp = f"ERROR: {result['error'][:22]}"
            row_scope = "—"
            row_ms = "—"
        else:
            row_disp = (result.get("disposition") or {}).get("recommendation", "—")
            row_scope = result.get("scope_classification", "—")
            row_ms = str((result.get("_audit_log") or {}).get("processing_duration_ms", "—"))
        print(f"  {num:<6}{row_disp:<28}{row_scope:<26}{row_ms:>6}")
    print(f"{'═' * W}\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="LACRA demo")
    parser.add_argument("--path", type=int, choices=[1, 2, 3, 4],
                        help="Run a single path (1–4); omit for all four")
    args = parser.parse_args()

    print(f"\n{'#' * W}")
    print(f"#{'LACRA — Lattice Pay AML Case Review Agent v1.0':^{W - 2}}#")
    print(f"#{'Prototype Demo  ·  Gate 5b Final Exam':^{W - 2}}#")
    print(f"{'#' * W}")

    to_run = [c for c in CASES if args.path is None or c[0] == args.path]

    collected: list[tuple[int, str, dict]] = []
    for num, label, subtitle, kwargs in to_run:
        result = run_lacra(**kwargs)
        print_case(num, label, subtitle, result)
        collected.append((num, label, result))

    if len(collected) > 1:
        print(f"\n  {'─' * W}")
        print("  SUMMARY")
        _summary(collected)
    else:
        print()


if __name__ == "__main__":
    main()
