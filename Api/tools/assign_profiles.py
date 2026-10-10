#!/usr/bin/env python3
"""Assign execution profiles to approved checks by policy and keep run tags in sync.

Policy for status=approved (draft/needs_clarification keep their profiles):
  Smoke      - manual choice: kept if already listed (requires deterministic + full automation)
  PR         - Smoke, plus P0 deterministic full-automation checks that are not costly
  CI         - P0-P2, deterministic, not manual, not costly
  Release    - P0-P1, deterministic, not manual (costly allowed)
  Regression - everything except kind=performance
  Nightly    - everything
Run tags in `tags` (smoke, pr, ci, ...) are rewritten to mirror `profiles` for every check.
Files are re-serialized in one canonical YAML layout.

Usage: assign_profiles.py [library-root] [--check]
  --check  do not write; exit 1 if any file would change (for CI).
"""
from pathlib import Path
import argparse

import yaml

from library import PRIORITY_RANK, iter_checks, load_profiles, profile_key, setup_console

PROFILE_ORDER = ("Smoke", "PR", "CI", "Regression", "Nightly", "Release")
RUN_TAGS = {"smoke", "pr", "ci", "regression", "nightly", "release"}
KEY_ORDER = ("id", "status", "title", "description", "category", "protocols", "kind", "priority", "tags",
             "preconditions", "steps", "expected", "applicability", "automation", "profiles", "risk", "references")


class _Dumper(yaml.SafeDumper):
    def ignore_aliases(self, data):
        return True


def policy_profiles(check):
    existing = {profile_key(p) for p in check.get("profiles", [])}
    if check.get("status") != "approved":
        return [p for p in PROFILE_ORDER if profile_key(p) in existing]
    rank = PRIORITY_RANK.get(check.get("priority"), 3)
    automation = check.get("automation", {})
    deterministic = automation.get("deterministic") is True
    level = automation.get("level")
    costly = "costly" in check.get("tags", [])
    smoke = "smoke" in existing and deterministic and level == "full"
    chosen = {
        "Smoke": smoke,
        "PR": smoke or (rank == 0 and deterministic and level == "full" and not costly),
        "CI": rank <= 2 and deterministic and level != "manual" and not costly,
        "Release": rank <= 1 and deterministic and level != "manual",
        "Regression": check.get("kind") != "performance",
        "Nightly": True,
    }
    return [p for p in PROFILE_ORDER if chosen[p]]


def normalize(check):
    profiles = policy_profiles(check)
    tags = [t for t in check.get("tags", []) if t not in RUN_TAGS] + [p.lower() for p in profiles]
    check = {**check, "tags": list(dict.fromkeys(tags)), "profiles": profiles}
    ordered = {k: check[k] for k in KEY_ORDER if k in check}
    ordered.update({k: v for k, v in check.items() if k not in ordered})
    return ordered


def dump(checks):
    return yaml.dump({"checks": checks}, Dumper=_Dumper, allow_unicode=True, sort_keys=False, width=120)


def main(argv=None):
    setup_console()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("root", nargs="?", default=".")
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args(argv)
    root = Path(args.root)

    profiles, errors = load_profiles(root)
    missing = [p for p in PROFILE_ORDER if profile_key(p) not in profiles]
    if missing:
        errors.append(f"profiles/ lacks: {', '.join(missing)}")
    by_file = {}
    for path, check in iter_checks(root, errors):
        by_file.setdefault(path, []).append(check)
    if errors:
        for e in errors:
            print("ERROR:", e)
        return 1

    changed = []
    for path, checks in by_file.items():
        text = dump([normalize(c) for c in checks])
        if path.read_text(encoding="utf-8") != text:
            changed.append(path)
            if not args.check:
                path.write_text(text, encoding="utf-8", newline="\n")
    verb = "would change" if args.check else "updated"
    for p in changed:
        print(f"{verb}: {p.relative_to(root).as_posix()}")
    print(f"Files: {len(by_file)} | {verb}: {len(changed)}")
    return 1 if args.check and changed else 0


if __name__ == "__main__":
    raise SystemExit(main())
