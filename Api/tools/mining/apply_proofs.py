#!/usr/bin/env python3
"""Apply a reviewed mining batch: RWB entries in traceability/, tag + reference + variant steps in checks/.

Usage (from Api/):
  apply_proofs.py --batch pilot --dry-run       show what would change
  apply_proofs.py --batch pilot                 write traceability/real-world-bugs.yaml and checks/
  apply_proofs.py --batch pilot --proofs-only   only existing checks (new draft records are not written yet)

Plan and RWB IDs come from cluster.py (ideas/mined/<batch>.review.yaml). Records for accepted clusters are
written by Claude as `status: draft`; this script only checks they exist and adds the tag and reference.
Re-running is safe: present references, steps and bugs are skipped.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from assign_profiles import dump  # noqa: E402
from cluster import TRACE_FILE, build_plan  # noqa: E402
from library import setup_console  # noqa: E402

TAG = "real-world-bug"
TRACE_HEADER_END = "{}"


def ref(rwb: str) -> str:
    return f"Real-world bug: {rwb}"


def mark(check: dict, rwb: str) -> list[str]:
    changes = []
    if TAG not in check["tags"]:
        check["tags"].append(TAG)
        changes.append("метка")
    refs = check.setdefault("references", [])
    if ref(rwb) not in refs:
        refs.append(ref(rwb))
        changes.append(rwb)
    return changes


def add_step(check: dict, action: str, rwb: str, bug: str) -> bool:
    if any(s.get("action") == action for s in check["steps"]):
        return False
    check["steps"].append({"action": action, "notes": f"{ref(rwb)} ({bug})"})
    return True


def checks_by_file() -> dict[Path, list[dict]]:
    files = {}
    for f in sorted(Path("checks").rglob("*.yaml")):
        if "generated" not in f.parts:
            files[f] = (yaml.safe_load(f.read_text(encoding="utf-8")) or {}).get("checks") or []
    return files


def write_trace(plan: dict, entries: dict, dry: bool) -> int:
    trace = dict(plan["trace"])
    added = 0
    for rwb, (pattern, check_id, bug_ids) in entries.items():
        e = trace.setdefault(rwb, {"pattern": pattern, "checks": [], "batch": plan["batch"], "bugs": []})
        if check_id not in e["checks"]:
            e["checks"].append(check_id)
        urls = {b["url"] for b in e["bugs"]}
        for b in bug_ids:
            if plan["bugs"][b]["url"] not in urls:
                e["bugs"].append(plan["bugs"][b])
                added += 1
    if not dry:
        text = TRACE_FILE.read_text(encoding="utf-8")
        header = text[:text.rindex(TRACE_HEADER_END)] if text.rstrip().endswith(TRACE_HEADER_END) else \
            "".join(line for line in text.splitlines(keepends=True) if line.startswith("#"))
        body = yaml.dump(dict(sorted(trace.items())), allow_unicode=True, sort_keys=False, width=120)
        TRACE_FILE.write_text(header + body, encoding="utf-8")
    return added


def main() -> int:
    setup_console()
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--batch", default="pilot")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--proofs-only", action="store_true")
    args = ap.parse_args()
    errors: list[str] = []
    plan = build_plan(args.batch, errors)
    pending = [c["key"] for c in plan["clusters"] if c["decision"] == "pending"]
    if pending and not args.proofs_only:
        errors.append(f"не решены кластеры: {', '.join(pending)}")
    for e in errors:
        print("ОШИБКА:", e)
    if errors:
        return 1

    files = checks_by_file()
    where = {c["id"]: (f, c) for f, cs in files.items() for c in cs}
    touched, entries, log = set(), {}, []
    for cid, p in plan["proofs"].items():
        f, check = where[cid]
        changes = mark(check, p["rwb"])
        steps = sum(add_step(check, it["variant"], p["rwb"], it["bug"]) for it in p["items"] if it["variant"])
        if steps:
            changes.append(f"шагов +{steps}")
        if changes:
            touched.add(f)
            log.append(f"{cid}: {', '.join(changes)}")
        entries[p["rwb"]] = (p["title"], cid, [it["bug"] for it in p["items"]])
    missing = []
    for c in plan["clusters"]:
        if c["decision"] != "accept" or args.proofs_only:
            continue
        if c["check_id"] not in where:
            missing.append(f"{c['check_id']} ({c['file']})")
            continue
        f, check = where[c["check_id"]]
        if changes := mark(check, c["rwb"]):
            touched.add(f)
            log.append(f"{c['check_id']} (новая): {', '.join(changes)}")
        entries[c["rwb"]] = (c["idea"], c["check_id"], c["bugs"])
    if missing:
        print("ОШИБКА: нет записей для принятых кластеров (сначала написать draft или --proofs-only):")
        print("\n".join(f"  {m}" for m in missing))
        return 1

    added = write_trace(plan, entries, args.dry_run)
    if not args.dry_run:
        for f in touched:
            f.write_text(dump(files[f]), encoding="utf-8")
    print("\n".join(log))
    mode = "проверка (--dry-run)" if args.dry_run else "записано"
    print(f"{mode}: записей {len(log)}, файлов {len(touched)}, RWB {len(entries)}, багов в трассировку +{added}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
