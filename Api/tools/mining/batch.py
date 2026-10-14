#!/usr/bin/env python3
"""Batches for LLM steps 3-5 of bug mining (run by Claude Code, prompt: mining/prompts/triage_abstract.md).

Usage (from Api/):
  batch.py index                              library index -> build/mining/library_index.txt
  batch.py make  --name cal-01 --n 20         next unprocessed records -> build/mining/<batch>/batches/<name>.md
  batch.py check --name cal-01                validate <name>.out.jsonl against the batch and taxonomy
  batch.py stats                              progress of the batch: processed, verdicts, match types
Options: --batch pilot (default).
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from library import iter_checks, load_yaml, setup_console  # noqa: E402

BODY_LIMIT = 1500
TESTS_LIMIT = 1200
OOS_CLASSES = {"build", "ui", "memory", "perf-internal", "docs", "framework-internal", "usage", "insufficient-data",
               "client-lib", "other"}
MATCH_TYPES = {"covered", "extends", "new"}
PROTOCOLS = {"rest", "grpc", "graphql", "websocket", "generic"}
MINING = Path("build/mining")


def library_ids() -> dict[str, dict]:
    return {c["id"]: c for _, c in iter_checks(Path("."), []) if not c["id"].startswith(("REAL-", "GEN-"))}


def cmd_index(_args) -> None:
    lines = [f"{c['id']} | {c['category']} | {c['title']}" for c in sorted(library_ids().values(), key=lambda c: c["id"])]
    MINING.mkdir(parents=True, exist_ok=True)
    (MINING / "library_index.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"{len(lines)} записей -> {MINING / 'library_index.txt'}")


def processed_ids(base: Path) -> set[str]:
    done = set()
    for f in (base / "batches").glob("*.out.jsonl"):
        done |= {json.loads(line)["id"] for line in f.open(encoding="utf-8") if line.strip()}
    for f in (base / "batches").glob("*.ids"):
        if not f.with_suffix(".out.jsonl").exists():
            done |= set(f.read_text(encoding="utf-8").split())  # issued, not yet answered
    return done


def cut(text: str, limit: int) -> str:
    return text if len(text) <= limit else text[:limit] + " …[обрезано]"


def cmd_make(args) -> None:
    base = MINING / args.batch
    (base / "batches").mkdir(parents=True, exist_ok=True)
    records = [json.loads(line) for line in (base / "filtered.jsonl").open(encoding="utf-8")]
    done = processed_ids(base)
    pending = [r for r in records if r["id"] not in done]
    # round-robin over sources, records with fix tests first
    by_source: dict[str, list] = {}
    for r in sorted(pending, key=lambda r: not r.get("fix_tests")):
        by_source.setdefault(r["source"], []).append(r)
    picked = []
    while len(picked) < args.n and any(by_source.values()):
        for queue in by_source.values():
            if queue and len(picked) < args.n:
                picked.append(queue.pop(0))

    out = [f"# Партия {args.name} ({len(picked)} багов)\n",
           "Инструкция — `mining/prompts/triage_abstract.md`, справочник — `build/mining/library_index.txt`.\n"]
    for r in picked:
        out.append(f"\n## {r['id']}\n")
        meta = f"source: {r['source']} | {r['kind']} | labels: {', '.join(r['labels'])} | fix: {r['fix_evidence']}"
        if r.get("packages"):
            meta += f" | packages: {', '.join(r['packages'])}"
        out.append(meta + f"\n\n**{r['title']}**\n\n{cut(r['body'], BODY_LIMIT)}\n")
        tests = "".join(f"\n--- {t['file']}\n{t['patch']}" for t in r.get("fix_tests") or [])
        if tests:
            out.append(f"\nТесты из фикса:\n```diff{cut(tests, TESTS_LIMIT)}\n```\n")
    (base / "batches" / f"{args.name}.md").write_text("".join(out), encoding="utf-8")
    (base / "batches" / f"{args.name}.ids").write_text("\n".join(r["id"] for r in picked) + "\n", encoding="utf-8")
    size = sum(len(s) for s in out)
    print(f"{len(picked)} багов, {size} символов -> {base / 'batches' / (args.name + '.md')}; осталось {len(pending) - len(picked)}")


def cmd_check(args) -> int:
    base = MINING / args.batch / "batches"
    ids = (base / f"{args.name}.ids").read_text(encoding="utf-8").split()
    tax = load_yaml(Path("taxonomy/categories.yaml"))["categories"]
    groups = load_yaml(Path("taxonomy/tags.yaml"))["tag_groups"]
    tags = set(groups["domain"]) | set(groups["quality"]) | set(groups["behavior"])
    known = library_ids()
    errors, seen = [], set()
    for n, line in enumerate((base / f"{args.name}.out.jsonl").open(encoding="utf-8"), 1):
        if not line.strip():
            continue
        r = json.loads(line)
        where = f"строка {n} ({r.get('id')})"
        seen.add(r.get("id"))
        if r.get("id") not in ids:
            errors.append(f"{where}: id не из партии")
        if r.get("verdict") == "out_of_scope":
            if r.get("oos_class") not in OOS_CLASSES:
                errors.append(f"{where}: oos_class {r.get('oos_class')!r}")
            continue
        if r.get("verdict") != "api":
            errors.append(f"{where}: verdict {r.get('verdict')!r}")
            continue
        p, m = r.get("pattern") or {}, r.get("match") or {}
        for key in ("title", "condition", "action", "expected", "actual", "expected_source"):
            if not p.get(key):
                errors.append(f"{where}: pattern.{key} пусто")
        if p.get("category") not in tax:
            errors.append(f"{where}: категория {p.get('category')!r}")
        if not set(p.get("protocol") or []) <= PROTOCOLS or not p.get("protocol"):
            errors.append(f"{where}: protocol {p.get('protocol')!r}")
        if bad := set(p.get("tags") or []) - tags:
            errors.append(f"{where}: метки вне таксономии {sorted(bad)}")
        if m.get("type") not in MATCH_TYPES:
            errors.append(f"{where}: match.type {m.get('type')!r}")
        elif m["type"] != "new" and m.get("check_id") not in known:
            errors.append(f"{where}: check_id {m.get('check_id')!r} нет в библиотеке")
        variant = m.get("variant")
        if "variant" in m and m.get("type") != "extends" and variant:
            errors.append(f"{where}: variant только у extends")
        if variant and variant.lower().startswith(("добавить", "вариант")):
            errors.append(f"{where}: variant — шаг в повелительной форме, без «Добавить …»")
    if missing := set(ids) - seen:
        errors.append(f"нет ответа для {len(missing)}: {sorted(missing)[:5]}")
    for e in errors:
        print(e)
    print(f"{args.name}: {len(seen)}/{len(ids)} ответов, ошибок {len(errors)}")
    return 1 if errors else 0


def cmd_stats(args) -> None:
    base = MINING / args.batch
    total = sum(1 for _ in (base / "filtered.jsonl").open(encoding="utf-8"))
    rows = [json.loads(line) for f in sorted((base / "batches").glob("*.out.jsonl"))
            for line in f.open(encoding="utf-8") if line.strip()]
    print(f"обработано {len(rows)}/{total}")
    print("verdict:", dict(Counter(r["verdict"] for r in rows)))
    print("вне области:", dict(Counter(r["oos_class"] for r in rows if r["verdict"] == "out_of_scope")))
    print("сопоставление:", dict(Counter(r["match"]["type"] for r in rows if r["verdict"] == "api")))
    print("категории:", dict(Counter(r["pattern"]["category"] for r in rows if r["verdict"] == "api")))


def main() -> int:
    setup_console()
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("cmd", choices=["index", "make", "check", "stats"])
    ap.add_argument("--batch", default="pilot")
    ap.add_argument("--name")
    ap.add_argument("--n", type=int, default=20)
    args = ap.parse_args()
    return {"index": cmd_index, "make": cmd_make, "check": cmd_check, "stats": cmd_stats}[args.cmd](args) or 0


if __name__ == "__main__":
    sys.exit(main())
