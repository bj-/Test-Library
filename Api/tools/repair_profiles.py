#!/usr/bin/env python3
"""Normalize profile filenames/IDs and make profile references case-insensitive."""
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]
PROFILE_IDS = ("PR", "Smoke", "CI", "Regression", "Nightly", "Release")
PROFILE_DEFAULTS = {
    "PR": {"description": "Быстрая проверка на pull request.", "include_tags": ["smoke", "contract", "security", "positive"], "exclude_tags": ["nightly"], "max_priority": "P1", "selection": {"deterministic_only": True, "max_checks": 80}},
    "Smoke": {"description": "Минимальный набор критических путей.", "include_tags": ["smoke"], "exclude_tags": [], "max_priority": "P1", "selection": {"deterministic_only": True, "max_checks": 40}},
    "CI": {"description": "Средний набор для CI.", "include_tags": ["ci", "contract", "security", "validation", "error-handling"], "exclude_tags": [], "max_priority": "P2", "selection": {"deterministic_only": True, "max_checks": 300}},
    "Regression": {"description": "Широкий набор для проверки регрессий.", "include_tags": ["regression"], "exclude_tags": [], "max_priority": "P3", "selection": {"deterministic_only": False, "max_checks": None}},
    "Nightly": {"description": "Расширенный ночной прогон.", "include_tags": ["nightly", "regression", "compatibility", "resilience"], "exclude_tags": [], "max_priority": "P3", "selection": {"deterministic_only": False, "max_checks": None}},
    "Release": {"description": "Критические проверки перед релизом.", "include_tags": ["release", "security", "contract", "smoke"], "exclude_tags": [], "max_priority": "P1", "selection": {"deterministic_only": True, "max_checks": 200}},
}
def main():
    folder = ROOT / "profiles"
    folder.mkdir(exist_ok=True)
    existing = {}
    for path in folder.glob("*.yaml"):
        try:
            obj = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
            existing[str(obj.get("id") or path.stem).casefold()] = obj
        except Exception:
            pass
    for path in folder.glob("*.yaml"):
        path.unlink()
    for profile_id in PROFILE_IDS:
        obj = existing.get(profile_id.casefold(), PROFILE_DEFAULTS[profile_id])
        obj["id"] = profile_id
        (folder / f"{profile_id}.yaml").write_text(
            yaml.safe_dump(obj, allow_unicode=True, sort_keys=False), encoding="utf-8"
        )
    validator = ROOT / "tools" / "validate_library.py"
    text = validator.read_text(encoding="utf-8")
    text = text.replace(
        'profile_ids = {p.stem for p in (root / "profiles").glob("*.yaml")}',
        'profile_ids = {p.stem.casefold() for p in (root / "profiles").glob("*.yaml")}'
    )
    text = text.replace('if profile not in profile_ids:', 'if str(profile).casefold() not in profile_ids:')
    text = text.replace('if profile.get("id") != path.stem:', 'if str(profile.get("id", "")).casefold() != path.stem.casefold():')
    validator.write_text(text, encoding="utf-8")
    print("Профили нормализованы. Запусти: python tools/validate_library.py .")
if __name__ == "__main__":
    main()
