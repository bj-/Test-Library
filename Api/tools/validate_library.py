#!/usr/bin/env python3
"""Validate YAML checks, schema, taxonomy and profile references.

Usage: validate_library.py [library-root]
Exit code: 0 - no errors, 1 - errors found.
"""
from pathlib import Path
import sys

from library import (
    CHECK_STATUSES, iter_checks, load_json_schema, load_profiles, load_yaml, profile_key, setup_console,
)

try:
    from jsonschema import Draft202012Validator
except ImportError:
    Draft202012Validator = None

RUN_TAGS = {"smoke", "regression", "nightly", "release", "pr", "ci"}


def validate(root: Path):
    errors, warnings = [], []

    tags_doc = load_yaml(root / "taxonomy/tags.yaml")
    tags = {t for group in tags_doc["tag_groups"].values() for t in group}
    categories = set(load_yaml(root / "taxonomy/categories.yaml")["categories"])

    profiles, profile_errors = load_profiles(root)
    errors += profile_errors
    profile_validator = check_validator = None
    if Draft202012Validator:
        profile_validator = Draft202012Validator(load_json_schema(root, "execution-profile.schema.json"))
        check_validator = Draft202012Validator(load_json_schema(root, "check.schema.json"))

    for path, profile in profiles.values():
        if profile_validator:
            for e in profile_validator.iter_errors(profile):
                errors.append(f"{path}: schema {'/'.join(map(str, e.absolute_path))}: {e.message}")
        for t in (profile.get("include_tags") or []) + (profile.get("exclude_tags") or []):
            if t not in tags:
                errors.append(f"{path}: unknown tag {t}")

    checks, seen = [], set()
    for path, c in iter_checks(root, errors):
        cid = c.get("id", f"<missing-id in {path}>")
        checks.append(c)
        if cid in seen:
            errors.append(f"duplicate id: {cid} ({path})")
        seen.add(cid)
        if check_validator:
            for e in check_validator.iter_errors(c):
                errors.append(f"{cid}: schema {'/'.join(map(str, e.absolute_path))}: {e.message}")
        elif c.get("status") not in CHECK_STATUSES:
            errors.append(f"{cid}: status must be one of {', '.join(CHECK_STATUSES)}")
        if c.get("category") not in categories:
            errors.append(f"{cid}: unknown category {c.get('category')}")
        for t in c.get("tags", []):
            if t not in tags:
                errors.append(f"{cid}: unknown tag {t}")
        for p in c.get("profiles", []):
            entry = profiles.get(profile_key(p))
            if entry is None:
                errors.append(f"{cid}: unknown profile {p}")
            elif entry[1]["id"] != p:
                warnings.append(f"{cid}: profile '{p}' differs in case from id '{entry[1]['id']}'")
        listed = {profile_key(p) for p in c.get("profiles", [])}
        run_tags = {t for t in c.get("tags", []) if t in RUN_TAGS}
        if "profiles" in c and run_tags != listed:
            errors.append(f"{cid}: run tags {sorted(run_tags)} must mirror profiles {sorted(listed)}; run tools/assign_profiles.py")
        automation = c.get("automation", {})
        if c.get("status") == "approved" and "smoke" in listed and not (automation.get("level") == "full" and automation.get("deterministic") is True):
            errors.append(f"{cid}: Smoke requires automation.level=full and deterministic=true")
        if "costly" in c.get("tags", []) and listed & {"smoke", "pr", "ci"}:
            errors.append(f"{cid}: costly check must not be in Smoke/PR/CI")
        app = c.get("applicability", {})
        if not app.get("when"):
            errors.append(f"{cid}: applicability.when must not be empty")
        if "skip_when" not in app:
            errors.append(f"{cid}: applicability.skip_when must be present")
        if automation.get("level") == "full" and automation.get("deterministic") is not True:
            errors.append(f"{cid}: full automation requires deterministic=true")
        if c.get("kind") in RUN_TAGS:
            errors.append(f"{cid}: kind must not be a run tag")

    by_status = {s: sum(c.get("status") == s for c in checks) for s in CHECK_STATUSES}
    print(f"Checks: {len(checks)} | Unique IDs: {len(seen)} | Profiles: {len(profiles)}")
    print("Status: " + ", ".join(f"{s}={n}" for s, n in by_status.items()))
    print(f"JSON Schema validation: {'enabled' if Draft202012Validator else 'fallback; install jsonschema for full checks'}")
    print(f"Errors: {len(errors)} | Warnings: {len(warnings)}")
    for e in errors:
        print("ERROR:", e)
    for w in warnings:
        print("WARNING:", w)
    return 1 if errors else 0


def main(argv):
    setup_console()
    return validate(Path(argv[1] if len(argv) > 1 else "."))


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
