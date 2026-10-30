#!/usr/bin/env python3
"""Build docs/CATALOG.md: every check grouped by category with priority, status, protocols and profiles.

Usage: build_catalog.py [library-root] [--check]
  --check  do not write; exit 1 if docs/CATALOG.md is out of date.
"""
from collections import Counter, defaultdict
from pathlib import Path
import argparse

from library import CHECK_STATUSES, PRIORITY_RANK, iter_checks, load_yaml, setup_console


def build(root: Path):
    errors = []
    checks = [c for _, c in iter_checks(root, errors)]
    categories = load_yaml(root / "taxonomy/categories.yaml")["categories"]
    by_cat = defaultdict(list)
    for c in checks:
        by_cat[c.get("category")].append(c)

    status = Counter(c.get("status") for c in checks)
    protocols = Counter(p for c in checks for p in c.get("protocols", []))
    lines = ["# Каталог проверок", "",
             "Файл генерируется `python tools/build_catalog.py .` — не редактируйте вручную.", "",
             f"Всего проверок: **{len(checks)}** — " + ", ".join(f"{s}: {status.get(s, 0)}" for s in CHECK_STATUSES) + ".",
             "Протоколы: " + ", ".join(f"{p}: {n}" for p, n in sorted(protocols.items())) + ".", "",
             "| Категория | Описание | Проверок |", "|---|---|---:|"]
    for cat in categories:
        if by_cat.get(cat):
            lines.append(f"| [{cat}](#{cat}) | {categories[cat]} | {len(by_cat[cat])} |")
    for cat in categories:
        items = sorted(by_cat.get(cat, []), key=lambda c: (PRIORITY_RANK.get(c.get("priority"), 3), c.get("id")))
        if not items:
            continue
        lines += ["", f"## {cat}", "", categories[cat], "",
                  "| ID | Проверка | P | Статус | Протоколы | Профили |", "|---|---|---|---|---|---|"]
        for c in items:
            title = str(c.get("title", "")).replace("|", "\\|")
            lines.append(f"| `{c['id']}` | {title} | {c.get('priority')} | {c.get('status')} | "
                         f"{', '.join(c.get('protocols', []))} | {', '.join(c.get('profiles', []))} |")
    return "\n".join(lines) + "\n", errors


def main(argv=None):
    setup_console()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("root", nargs="?", default=".")
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args(argv)
    root = Path(args.root)
    text, errors = build(root)
    for e in errors:
        print("ERROR:", e)
    target = root / "docs" / "CATALOG.md"
    current = target.read_text(encoding="utf-8") if target.exists() else None
    if args.check:
        print("CATALOG.md is up to date" if current == text else "CATALOG.md is out of date")
        return 1 if errors or current != text else 0
    if current != text:
        target.write_text(text, encoding="utf-8", newline="\n")
    print(f"Written: {target.relative_to(root).as_posix()}")
    if root.resolve() == Path(__file__).resolve().parents[1]:   # манифест версии (ADR 0016)
        from library_manifest import write_manifest
        print(f"Written: manifest.yaml ({write_manifest()['version']})")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
