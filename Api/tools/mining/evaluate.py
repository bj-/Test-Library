#!/usr/bin/env python3
"""Evaluation of a mining batch (stage 7 of docs/BUG_MINING_PLAN.md): metrics by source + accuracy sample.

Usage (from Api/):
  evaluate.py --batch pilot      metrics -> stdout (Markdown, for REPORT.md)

The manual accuracy sample (sample()) is built into Excel by accuracy.py.

Metrics: idea yield per 100 collected bugs, API share, proofs, accepted on review, proof coverage by category,
out-of-scope bin. Cost is taken from mining/budget.md by hand: /usage has no machine-readable form.
"""
from __future__ import annotations

import argparse
import json
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from cluster import MINED, MINING, load_results, load_sources  # noqa: E402
from library import iter_checks, load_yaml, setup_console  # noqa: E402

SAMPLE_TRIAGE = 50
SAMPLE_MATCH = 30
SEED = 7


def per_source(batch: str) -> tuple[dict, dict]:
    sources = load_sources(batch)
    raw = {f.stem: sum(1 for _ in f.open(encoding="utf-8")) for f in (MINING / batch / "raw").glob("*.jsonl")}
    review = load_yaml(MINED / f"{batch}.review.yaml")
    lead = {c["bugs"][0]: c["decision"] for c in review.get("clusters") or []}
    stats = defaultdict(Counter)
    for r in load_results(batch):
        s = stats[sources[r["id"]]["source"]]
        s["filtered"] += 1
        if r["verdict"] != "api":
            s["oos"] += 1
            continue
        s["api"] += 1
        s[r["match"]["type"]] += 1
        if lead.get(r["id"]) == "accept":
            s["ideas"] += 1
    return raw, stats


def pct(a: int, b: int) -> str:
    return f"{100 * a / b:.1f}" if b else "—"


def metrics(batch: str) -> str:
    raw, stats = per_source(batch)
    out = ["| Источник | Собрано | После фильтра | API | Доля API, % | new | extends | covered | Идей принято |"
           " Идей на 100 собранных | Пруфов на 100 собранных |", "|---|---|---|---|---|---|---|---|---|---|---|"]
    total = Counter()
    for src, s in sorted(stats.items(), key=lambda x: -x[1]["ideas"] * 1000 / max(raw.get(x[0], 1), 1)):
        n = raw.get(src, 0)
        total.update(s)
        total["raw"] += n
        out.append(f"| {src} | {n} | {s['filtered']} | {s['api']} | {pct(s['api'], s['filtered'])} | {s['new']} |"
                   f" {s['extends']} | {s['covered']} | {s['ideas']} | {pct(s['ideas'], n)} |"
                   f" {pct(s['extends'] + s['covered'], n)} |")
    t = total
    out.append(f"| **Итого** | {t['raw']} | {t['filtered']} | {t['api']} | {pct(t['api'], t['filtered'])} | {t['new']} |"
               f" {t['extends']} | {t['covered']} | {t['ideas']} | {pct(t['ideas'], t['raw'])} |"
               f" {pct(t['extends'] + t['covered'], t['raw'])} |")

    review = load_yaml(MINED / f"{batch}.review.yaml")
    decisions = Counter(c["decision"] for c in review.get("clusters") or [])
    out += ["", f"Ревью: идей {sum(decisions.values())}, принято {decisions['accept']}, отклонено {decisions['reject']}"
            f" — доля принятых {pct(decisions['accept'], sum(decisions.values()))} %.", ""]

    oos = Counter(r["oos_class"] for r in load_results(batch) if r["verdict"] == "out_of_scope")
    out += ["Корзина вне области: " + ", ".join(f"`{k}` {v}" for k, v in oos.most_common()) + ".", ""]

    tot, proof, draft = Counter(), Counter(), Counter()
    for _, c in iter_checks(Path("."), []):
        if c["id"].startswith(("REAL-", "GEN-")):
            continue
        tot[c["category"]] += 1
        if "real-world-bug" in c.get("tags", []):
            proof[c["category"]] += 1
            draft[c["category"]] += c.get("status") == "draft"
    out += ["| Категория | Записей | С пруфами | Доля, % | Из них новых draft |", "|---|---|---|---|---|"]
    for k in sorted(tot, key=lambda k: (proof[k] / tot[k], -tot[k])):
        out.append(f"| {k} | {tot[k]} | {proof[k]} | {pct(proof[k], tot[k])} | {draft[k]} |")
    out.append(f"| **Итого** | {sum(tot.values())} | {sum(proof.values())} |"
               f" {pct(sum(proof.values()), sum(tot.values()))} | {sum(draft.values())} |")
    return "\n".join(out)


def sample(batch: str) -> tuple[list[dict], list[dict]]:
    """Accuracy sample (stable, seed SEED): half api / half out_of_scope for triage, extends+covered for matching."""
    results = load_results(batch)
    rnd = random.Random(SEED)
    api = [r for r in results if r["verdict"] == "api"]
    oos = [r for r in results if r["verdict"] == "out_of_scope"]
    triage = rnd.sample(api, SAMPLE_TRIAGE // 2) + rnd.sample(oos, SAMPLE_TRIAGE // 2)
    matched = rnd.sample([r for r in api if r["match"]["type"] != "new"], SAMPLE_MATCH)
    return triage, matched


def main() -> int:
    setup_console()
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--batch", default="pilot")
    args = ap.parse_args()
    print(metrics(args.batch))
    return 0


if __name__ == "__main__":
    sys.exit(main())
