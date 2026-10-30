"""Манифест библиотеки (ADR 0016): версия и хеши записей и шагов, без git.

    python tools/library_manifest.py --write    # пересобрать Api/manifest.yaml
    python tools/library_manifest.py --check    # манифест актуален? (validate_library.py вызывает сам)

Хеш записи - sha256 (12 символов) от канонического JSON разобранного YAML полей steps, expected, preconditions,
applicability; форматирование, CRLF, описание и теги на хеш не влияют. Версия: <YYYY.MM.DD>-<6 символов хеша статусов
и хешей всех записей>. Хеш библиотеки не изменился - дата остаётся из существующего манифеста (сборка идемпотентна).
Закрытые записи (automation.ai_generation.restricted, sg-restricted) в манифесте библиотеки есть только хешем;
в манифест выгрузки не попадают.
"""
import argparse
import datetime
import hashlib
import json
import sys
from pathlib import Path

import yaml

from library import iter_checks, setup_console

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "manifest.yaml"
HASHED = ("steps", "expected", "preconditions", "applicability")
HEADER = ("# Манифест библиотеки (ADR 0016): версия, хеши записей и шагов. Собирается `python tools/library_manifest.py --write`\n"
          "# (и build_catalog.py), вручную не править.\n")


def canon(obj) -> str:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str)


def digest(obj) -> str:
    return hashlib.sha256(canon(obj).encode("utf-8")).hexdigest()[:12]


def record_hash(check: dict) -> str:
    return digest({k: check.get(k) for k in HASHED})


def step_hashes(check: dict) -> list:
    return [digest(s) for s in check.get("steps") or []]


def is_restricted(check: dict) -> bool:
    return bool(((check.get("automation") or {}).get("ai_generation") or {}).get("restricted"))


def closed_ids(checks=None) -> set:
    """ID закрытых записей: флаг restricted или группа sg-restricted."""
    from security_groups import RESTRICTED, compute
    index, _, _ = compute()
    out = set(index.get(RESTRICTED, []))
    errors = []
    for _, c in (checks if checks is not None else iter_checks(ROOT, errors)):
        if c.get("id") and is_restricted(c):
            out.add(c["id"])
    return out


def load_checks(root: Path = ROOT):
    errors = []
    pairs = [(p, c) for p, c in iter_checks(root, errors) if c.get("id")]
    return pairs, errors


def library_hash(entries: dict) -> str:
    return digest(sorted([i, e["status"], e["hash"]] for i, e in entries.items()))


def build_manifest(root: Path = ROOT, include=None, exclude=None, scope="full", date=None, pairs=None) -> dict:
    """Манифест. include/exclude - множества ID (выгрузка); версия считается по всей библиотеке."""
    pairs = pairs if pairs is not None else load_checks(root)[0]
    full = {c["id"]: {"status": str(c.get("status")), "hash": record_hash(c), "steps": step_hashes(c)} for _, c in pairs}
    lib_hash = library_hash(full)
    existing = None
    if root == ROOT and MANIFEST.exists():
        existing = yaml.safe_load(MANIFEST.read_text(encoding="utf-8")) or {}
    day = date or (existing["version"].split("-")[0] if existing and existing.get("library_hash") == lib_hash
                   else datetime.date.today().strftime("%Y.%m.%d"))
    keep = {i: e for i, e in full.items() if (include is None or i in include) and i not in (exclude or ())}
    return {"version": f"{day}-{lib_hash[:6]}", "library_hash": lib_hash, "scope": scope,
            "omitted": len(full) - len(keep), "records": dict(sorted(keep.items()))}


def render(m: dict) -> str:
    lines = [HEADER.rstrip("\n"), f'version: "{m["version"]}"', f'library_hash: "{m["library_hash"]}"',
             f"scope: {m['scope']}", f"omitted: {m['omitted']}", f"records_total: {len(m['records'])}", "records:"]
    for i, e in m["records"].items():
        steps = ", ".join(f'"{h}"' for h in e["steps"])
        lines += [f'  "{i}":', f"    status: {e['status']}", f'    hash: "{e["hash"]}"', f"    steps: [{steps}]"]
    return "\n".join(lines) + "\n"


def parse(text: str) -> dict:
    return yaml.safe_load(text) or {}


def check_manifest() -> list:
    """Ошибки актуальности Api/manifest.yaml (пустой список - актуален)."""
    if not MANIFEST.exists():
        return [f"{MANIFEST.name} отсутствует - python tools/library_manifest.py --write"]
    want = render(build_manifest())
    if MANIFEST.read_text(encoding="utf-8").replace("\r\n", "\n") != want:
        return [f"{MANIFEST.name} устарел - python tools/library_manifest.py --write"]
    return []


def write_manifest() -> dict:
    m = build_manifest()
    text = render(m)
    if not MANIFEST.exists() or MANIFEST.read_text(encoding="utf-8").replace("\r\n", "\n") != text:
        MANIFEST.write_text(text, encoding="utf-8", newline="\n")
    return m


def main():
    setup_console()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--write", action="store_true")
    g.add_argument("--check", action="store_true")
    a = ap.parse_args()
    if a.write:
        m = write_manifest()
        print(f"{MANIFEST.relative_to(ROOT).as_posix()}: версия {m['version']}, записей {len(m['records'])}")
        return 0
    errors = check_manifest()
    for e in errors:
        print("ERROR:", e)
    print("актуален" if not errors else "")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
