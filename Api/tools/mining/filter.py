#!/usr/bin/env python3
"""Step 2 of bug mining: filter raw records without LLM -> build/mining/<batch>/filtered.jsonl.

Usage: filter.py [--batch pilot] [--allow-no-fix] [--sources mining/sources.yaml]
Run from Api/. Keeps fixed bugs only (merged PR or fixing commit; advisories are kept as published;
sources with allow_no_fix also keep issues closed as COMPLETED, marked fix_evidence: closed-completed),
drops records of other batches, excluded labels, feature/question titles and per-source exclude_title (framework internals, build) —
except records already answered by an LLM batch, so re-filtering never orphans results; dedups by id, cleans and truncates bodies.
Prints drop reasons per source; the same numbers go to filter_stats.json.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from batch import processed_ids  # noqa: E402
from library import load_yaml, setup_console  # noqa: E402

TITLE_DROP = re.compile(r"(?i)^\s*(\[(feature|feat|question|docs?|rfc|proposal)\b|feature request|question\b|"
                        r"\[?enhancement|docs?:|chore|ci:|build:)")
HTML_COMMENT = re.compile(r"<!--.*?-->", re.S)
IMAGE = re.compile(r"!\[[^\]]*\]\([^)]*\)|<img[^>]*>", re.I)
BLANKS = re.compile(r"\n{3,}")


def clean_body(text: str, limit: int) -> str:
    text = BLANKS.sub("\n\n", IMAGE.sub("[image]", HTML_COMMENT.sub("", text or ""))).strip()
    if len(text) > limit:
        text = text[:limit] + f"\n…[обрезано, всего {len(text)} символов]"
    return text


def folded(pattern: str) -> str:
    """A regex from a folded YAML scalar (>-): line breaks become spaces, which must not stick to alternatives."""
    return re.sub(r"\s*\|\s*", "|", " ".join(pattern.split()))


def main() -> int:
    setup_console()
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--batch", default="pilot")
    ap.add_argument("--allow-no-fix", action="store_true", help="оставлять закрытые COMPLETED без PR/коммита")
    ap.add_argument("--sources", default="mining/sources.yaml")
    args = ap.parse_args()

    cfg = load_yaml(Path(args.sources))
    defaults = cfg["defaults"]
    by_id = {s["id"]: s for s in cfg["sources"]}
    base = Path("build/mining") / args.batch
    seen, kept = set(), []
    answered = {json.loads(line)["id"] for f in (base / "batches").glob("*.out.jsonl")
                for line in f.open(encoding="utf-8") if line.strip()}
    other = set()  # issued or answered in other batches (a deeper pass over a pilot source)
    for d in Path("build/mining").glob("*/batches"):
        if d.parent != base:
            other |= processed_ids(d.parent)
    stats: dict[str, Counter] = defaultdict(Counter)

    for raw in sorted((base / "raw").glob("*.jsonl")):
        for line in raw.open(encoding="utf-8"):
            r = json.loads(line)
            src = by_id.get(r["source"], {})
            st = stats[r["source"]]
            st["raw"] += 1
            exc = [re.compile(folded(p)) for p in (defaults.get("exclude_labels"), src.get("exclude_labels")) if p]
            reason = None
            if r["id"] in seen:
                reason = "дубль"
            elif r["id"] in other:
                reason = "уже в другой партии"
            elif r["kind"] == "issue" and r["state_reason"] in ("NOT_PLANNED", "DUPLICATE"):
                reason = f"закрыт как {r['state_reason'].lower().replace('_', ' ')}"
            elif (r["kind"] == "issue" and not (r["fix"]["prs"] or r["fix"]["commits"])
                  and not (args.allow_no_fix or src.get("allow_no_fix"))):
                reason = "нет PR/коммита с исправлением"
            elif any(e.search(lb) for e in exc for lb in r["labels"]):
                reason = "исключающая метка"
            elif TITLE_DROP.search(r["title"]):
                reason = "заголовок: фича/вопрос/доки"
            elif (src.get("exclude_title") and r["id"] not in answered
                  and re.search(folded(src["exclude_title"]), r["title"])):
                reason = "заголовок: внутренности фреймворка/сборка"
            if reason:
                st["drop: " + reason] += 1
                continue
            seen.add(r["id"])
            r["fix_evidence"] = ("published" if r["kind"] == "advisory" else "pr" if r["fix"]["prs"]
                                 else "commit" if r["fix"]["commits"] else "closed-completed")
            r["body"] = clean_body(r["body"], src.get("body_max_chars", defaults.get("body_max_chars", 4000)))
            kept.append(r)
            st["kept"] += 1

    with (base / "filtered.jsonl").open("w", encoding="utf-8") as f:
        for r in kept:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    (base / "filter_stats.json").write_text(
        json.dumps({k: dict(v) for k, v in stats.items()}, ensure_ascii=False, indent=1), encoding="utf-8")

    for source, st in stats.items():
        drops = ", ".join(f"{k[6:]} {v}" for k, v in st.items() if k.startswith("drop: "))
        print(f"{source:16} raw {st['raw']:4}  оставлено {st['kept']:4}  {drops}")
    print(f"Итого оставлено: {len(kept)} -> {base / 'filtered.jsonl'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
