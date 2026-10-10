"""Shared helpers for library tools: loading YAML, checks and execution profiles.

Profiles are identified by the `id` inside the file and compared case-insensitively.
Results therefore do not depend on filesystem case sensitivity (Windows/Linux) or on
how git recorded a case-only rename of a profile file (core.ignorecase=true).
"""
from __future__ import annotations

import sys
from pathlib import Path

import yaml

PRIORITY_RANK = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}
CHECK_STATUSES = ("approved", "draft", "needs_clarification")
DEFAULT_SELECT_STATUSES = ("approved",)


def setup_console() -> None:
    """Never crash on characters the console/pipe code page cannot encode (cp866/cp1251)."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(errors="backslashreplace")
        except AttributeError:
            pass


def load_yaml(path: Path):
    with Path(path).open(encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def load_json_schema(root: Path, name: str):
    import json
    return json.loads((Path(root) / "schema" / name).read_text(encoding="utf-8"))


def profile_key(name) -> str:
    """Canonical comparison key for a profile name: case-insensitive, optional .yaml suffix."""
    key = str(name).strip()
    if key.casefold().endswith(".yaml"):
        key = key[:-5]
    return key.casefold()


def _sorted_files(folder: Path, pattern: str):
    # Explicit casefold ordering: Path ordering differs between Windows and POSIX.
    return sorted(folder.glob(pattern), key=lambda p: p.as_posix().casefold())


def load_profiles(root: Path):
    """Return ({profile_key: (path, doc)}, errors)."""
    profiles, errors = {}, []
    for path in _sorted_files(Path(root) / "profiles", "*.yaml"):
        try:
            doc = load_yaml(path)
        except Exception as e:
            errors.append(f"{path}: YAML error: {e}")
            continue
        pid = doc.get("id") if isinstance(doc, dict) else None
        if not isinstance(pid, str) or not pid.strip():
            errors.append(f"{path}: profile id is missing")
            continue
        key = profile_key(pid)
        if key != profile_key(path.stem):
            errors.append(f"{path}: id '{pid}' must match file name (case-insensitive)")
        if key in profiles:
            errors.append(f"{path}: duplicate profile id '{pid}' (also in {profiles[key][0]})")
            continue
        profiles[key] = (path, doc)
    return profiles, errors


def iter_checks(root: Path, errors: list):
    """Yield (path, check) for every check in checks/**; structural problems go to errors."""
    for path in _sorted_files(Path(root) / "checks", "**/*.yaml"):
        try:
            doc = load_yaml(path)
        except Exception as e:
            errors.append(f"{path}: YAML error: {e}")
            continue
        if not isinstance(doc, dict) or not isinstance(doc.get("checks"), list):
            errors.append(f"{path}: missing checks list")
            continue
        for check in doc["checks"]:
            if not isinstance(check, dict):
                errors.append(f"{path}: check entry must be a mapping")
                continue
            yield path, check
