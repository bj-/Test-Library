#!/usr/bin/env python3
"""Step 2b of bug mining: add test diffs of fixing PRs to filtered records.

Usage: enrich.py [--batch pilot] [--sources mining/sources.yaml]
Run from Api/. For each GitHub issue in filtered.jsonl with merged PRs fetches the PR file list once
(cache: pr_tests.json), keeps test files and their patches (truncated) in `fix_tests`.
Resumable via the cache; requests are sequential and paced.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from library import load_yaml, setup_console  # noqa: E402
from github_api import GitHub, StopCollection  # noqa: E402

TEST_FILE = re.compile(r"(?i)(^|/)(tests?|spec|__tests__|testsuite|e2e|integration)(/|$)|[._-](test|spec)\.[a-z]+$|Test\.java$")
PR_URL = re.compile(r"github\.com/([^/]+/[^/]+)/pull/(\d+)")
PATCH_LIMIT = 3000
MAX_PRS_PER_ISSUE = 2


def main() -> int:
    setup_console()
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--batch", default="pilot")
    ap.add_argument("--sources", default="mining/sources.yaml")
    args = ap.parse_args()

    cfg = load_yaml(Path(args.sources))
    base = Path("build/mining") / args.batch
    cache_path = base / "pr_tests.json"
    cache = json.loads(cache_path.read_text(encoding="utf-8")) if cache_path.exists() else {}
    records = [json.loads(line) for line in (base / "filtered.jsonl").open(encoding="utf-8")]
    gh = GitHub(cfg["politeness"])
    stopped = None

    try:
        for r in records:
            for url in r["fix"]["prs"][:MAX_PRS_PER_ISSUE]:
                m = PR_URL.search(url)
                if not m or url in cache:
                    continue
                files = list(gh.paginate(f"/repos/{m.group(1)}/pulls/{m.group(2)}/files?per_page=100"))
                tests, budget = [], PATCH_LIMIT
                for fl in files:
                    if not TEST_FILE.search(fl["filename"]):
                        continue
                    patch = (fl.get("patch") or "")[:max(budget, 0)]
                    budget -= len(patch)
                    tests.append({"file": fl["filename"], "patch": patch})
                cache[url] = {"files": len(files), "tests": tests}
                if len(cache) % 20 == 0:
                    cache_path.write_text(json.dumps(cache, ensure_ascii=False), encoding="utf-8")
    except StopCollection as e:
        stopped = e
    cache_path.write_text(json.dumps(cache, ensure_ascii=False), encoding="utf-8")

    with_tests = 0
    with (base / "filtered.jsonl").open("w", encoding="utf-8") as f:
        for r in records:
            r["fix_tests"] = [t for url in r["fix"]["prs"][:MAX_PRS_PER_ISSUE] for t in cache.get(url, {}).get("tests", [])]
            with_tests += bool(r["fix_tests"])
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"PR в кэше: {len(cache)}, записей с тестами из фикса: {with_tests}/{len(records)}, запросов: {gh.requests}")
    if stopped:
        print(f"Остановка: {stopped}")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
