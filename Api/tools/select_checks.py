#!/usr/bin/env python3
"""Select checks for an execution profile.

A check is a profile member when the profile is listed in its `profiles` field
(case-insensitive); checks without `profiles` fall back to matching `include_tags`.
Members are then filtered by status, `exclude_tags`, `max_priority` and
`deterministic_only`, ordered by priority and id, and truncated to `max_checks`.
"""
from pathlib import Path
import argparse
import json
import sys

from library import (
    CHECK_STATUSES, DEFAULT_SELECT_STATUSES, PRIORITY_RANK, iter_checks, load_profiles, profile_key, setup_console,
)


def exclusion_reason(check, key, profile, statuses):
    """Return (excluded_reason, None) or (None, included_reason)."""
    status = check.get("status", "<missing>")
    if status not in statuses:
        return f"status {status}", None
    tags = set(check.get("tags", []))
    if "profiles" in check:
        if key not in {profile_key(p) for p in check["profiles"]}:
            return "profile not listed in check.profiles", None
        included = "listed in check.profiles"
    else:
        matched = tags & set(profile.get("include_tags", []))
        if not matched:
            return "no include_tags match", None
        included = "include_tags: " + ", ".join(sorted(matched))
    excluded_tags = tags & set(profile.get("exclude_tags", []))
    if excluded_tags:
        return "exclude_tags: " + ", ".join(sorted(excluded_tags)), None
    priority = check.get("priority", "P3")
    if PRIORITY_RANK.get(priority, 3) > PRIORITY_RANK[profile["max_priority"]]:
        return f"priority {priority} > max_priority {profile['max_priority']}", None
    if profile["selection"]["deterministic_only"] and not check.get("automation", {}).get("deterministic", False):
        return "non-deterministic", None
    return None, included


def select(root: Path, profile_name: str, statuses):
    errors = []
    profiles, _ = load_profiles(root)
    key = profile_key(profile_name)
    if key not in profiles:
        known = ", ".join(sorted(doc["id"] for _, doc in profiles.values()))
        raise SystemExit(f"Unknown profile {profile_name}. Known: {known}")
    _, profile = profiles[key]

    selected, excluded = [], []
    for path, c in iter_checks(root, errors):
        item = {"id": c.get("id"), "priority": c.get("priority"), "title": c.get("title"),
                "status": c.get("status"), "file": path.relative_to(root).as_posix()}
        reason, included = exclusion_reason(c, key, profile, statuses)
        if reason:
            excluded.append({**item, "reason": reason})
        else:
            selected.append({**item, "reason": included})

    selected.sort(key=lambda x: (PRIORITY_RANK.get(x["priority"], 3), x["id"]))
    limit = profile["selection"].get("max_checks")
    truncated = 0
    if limit is not None and len(selected) > limit:
        truncated = len(selected) - limit
        excluded += [{**x, "reason": f"over max_checks={limit}"} for x in selected[limit:]]
        selected = selected[:limit]
    return {"profile": profile["id"], "statuses": list(statuses), "max_checks": limit,
            "selected_count": len(selected), "excluded_count": len(excluded), "truncated_by_max_checks": truncated,
            "selected": selected, "excluded": excluded, "errors": errors}


def main(argv=None):
    setup_console()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("root", help="library root (folder with checks/ and profiles/)")
    ap.add_argument("profile", help="profile id, case-insensitive, .yaml suffix optional")
    ap.add_argument("--status", default=",".join(DEFAULT_SELECT_STATUSES),
                    help=f"comma-separated statuses to include (default: approved; any of {', '.join(CHECK_STATUSES)})")
    ap.add_argument("--format", choices=("text", "json"), default="text")
    ap.add_argument("--explain", action="store_true", help="text mode: also list excluded checks with reasons")
    args = ap.parse_args(argv)

    statuses = [s.strip() for s in args.status.split(",") if s.strip()]
    unknown = [s for s in statuses if s not in CHECK_STATUSES]
    if unknown:
        ap.error(f"unknown status: {', '.join(unknown)}")

    result = select(Path(args.root), args.profile, statuses)
    if args.format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        for c in result["selected"]:
            print(f"{c['priority']}\t{c['id']}\t{c['title']}")
        if args.explain:
            for c in result["excluded"]:
                print(f"# excluded\t{c['id']}\t{c['reason']}")
    for e in result["errors"]:
        print("ERROR:", e, file=sys.stderr)
    print(f"Selected: {result['selected_count']} | Excluded: {result['excluded_count']}"
          f" | Truncated by max_checks: {result['truncated_by_max_checks']}", file=sys.stderr)
    return 1 if result["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
