from __future__ import annotations

import argparse
import html
import json
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean


REPO_ROOT = Path(__file__).resolve().parents[1]


def percentile(values: list[float], p: int) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = max(0, min(len(ordered) - 1, round((p / 100) * len(ordered) + 0.5) - 1))
    return ordered[index]


def load_records(path: Path) -> list[dict]:
    records: list[dict] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(record, dict):
            records.append(record)
    return records


def render(records: list[dict]) -> str:
    received = [r for r in records if r.get("event") == "request_received"]
    responses = [r for r in records if r.get("event") == "response_sent"]
    failures = [r for r in records if r.get("event") == "request_failed"]
    latencies = [float(r.get("latency_ms", 0)) for r in responses]
    total_requests = len(received) or len(responses) + len(failures)
    error_rate = len(failures) / total_requests * 100 if total_requests else 0.0
    costs = [float(r.get("cost_usd", 0)) for r in responses]
    tokens_in = sum(int(r.get("tokens_in", 0)) for r in responses)
    tokens_out = sum(int(r.get("tokens_out", 0)) for r in responses)
    quality = [float(r.get("quality_score", 0)) for r in responses]
    error_types: dict[str, int] = {}
    for failure in failures:
        key = str(failure.get("error_type", "unknown"))
        error_types[key] = error_types.get(key, 0) + 1

    p50, p95, p99 = (percentile(latencies, p) for p in (50, 95, 99))
    generated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    breakdown = ", ".join(f"{html.escape(k)}: {v}" for k, v in error_types.items()) or "No errors"
    latency_max = max(3000.0, p99, 1.0)

    return f"""<!doctype html>
<html lang="vi"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Day 13 AI Observability</title>
<style>
:root{{--bg:#08111f;--panel:#111d2f;--text:#edf4ff;--muted:#9db0c9;--line:#2a3c55;--ok:#55d6a7;--warn:#ffca68;--accent:#6da8ff}}
*{{box-sizing:border-box}} body{{margin:0;background:var(--bg);color:var(--text);font:15px/1.45 system-ui,sans-serif}}
main{{max-width:1200px;margin:auto;padding:28px}} header{{display:flex;justify-content:space-between;gap:20px;align-items:end;margin-bottom:20px}}
h1{{margin:0;font-size:28px}} .meta{{color:var(--muted);text-align:right}} .grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}}
section{{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:18px;min-height:190px}}
h2{{font-size:16px;margin:0 0 14px}} .value{{font-size:34px;font-weight:700}} .unit,.note{{color:var(--muted)}}
.threshold{{margin-top:14px;padding-top:10px;border-top:1px solid var(--line);color:var(--ok)}}
.bars{{display:grid;gap:9px;margin-top:14px}} .bar{{display:grid;grid-template-columns:38px 1fr 68px;gap:9px;align-items:center}}
.track{{height:9px;background:#20314a;border-radius:9px;overflow:hidden}} .fill{{height:100%;background:var(--accent)}}
.split{{display:flex;gap:28px;align-items:end}} .warn{{color:var(--warn)}}
@media(max-width:850px){{.grid{{grid-template-columns:1fr 1fr}}}} @media(max-width:560px){{.grid{{grid-template-columns:1fr}} header{{display:block}} .meta{{text-align:left;margin-top:8px}}}}
</style></head><body><main>
<header><div><h1>Day 13 AI Observability</h1><div class="note">Operational dashboard · 6 technical signal groups</div></div><div class="meta">Window: last 60 minutes<br>Generated: {generated}</div></header>
<div class="grid">
<section><h2>Latency percentiles</h2><div class="bars">
<div class="bar"><span>P50</span><div class="track"><div class="fill" style="width:{p50/latency_max*100:.1f}%"></div></div><b>{p50:.0f} ms</b></div>
<div class="bar"><span>P95</span><div class="track"><div class="fill" style="width:{p95/latency_max*100:.1f}%"></div></div><b>{p95:.0f} ms</b></div>
<div class="bar"><span>P99</span><div class="track"><div class="fill" style="width:{p99/latency_max*100:.1f}%"></div></div><b>{p99:.0f} ms</b></div></div><div class="threshold">SLO: P95 <= 3000 ms</div></section>
<section><h2>Request traffic</h2><div class="value">{total_requests}</div><div class="unit">requests / 60 minutes</div><div class="threshold">Guide: >= 1 request/minute</div></section>
<section><h2>Error rate and breakdown</h2><div class="value">{error_rate:.2f}%</div><div class="unit">{breakdown}</div><div class="threshold">SLO: error rate <= 2%</div></section>
<section><h2>Cost over time</h2><div class="value">${sum(costs):.4f}</div><div class="unit">Average ${mean(costs) if costs else 0:.4f} / response</div><div class="threshold">Budget: total <= USD 2.50</div></section>
<section><h2>Input and output tokens</h2><div class="split"><div><div class="value">{tokens_in}</div><div class="unit">input</div></div><div><div class="value">{tokens_out}</div><div class="unit">output</div></div></div><div class="threshold">Guide: total <= 50,000 tokens</div></section>
<section><h2>Quality proxy</h2><div class="value">{mean(quality) if quality else 0:.2f}</div><div class="unit">mean score (0–1)</div><div class="threshold">SLO: average >= 0.75</div></section>
</div></main></body></html>"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Render the CP2 dashboard evidence from JSONL logs")
    parser.add_argument("--logs", type=Path, default=REPO_ROOT / "data" / "logs.jsonl")
    parser.add_argument("--output", type=Path, default=REPO_ROOT / "submission" / "evidence" / "cp2-dashboard.html")
    args = parser.parse_args()
    if not args.logs.exists():
        parser.error(f"log file not found: {args.logs}")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(render(load_records(args.logs)), encoding="utf-8")
    print(f"Dashboard written to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
