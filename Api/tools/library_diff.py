"""База подбора проектов и сравнение с библиотекой (ADR 0016), без git.

    python tools/library_diff.py init <каталог-проекта-тестов> <модуль>   # docs/modules/<модуль>/library-baseline.yaml
    python tools/library_diff.py diff <baseline> [--library PATH]       # новые, изменённые (с текстом новых шагов), ставшие approved, удалённые, pending
    python tools/library_diff.py compact <baseline> --track functional|security   # без решения (pending и новые): id, title, category, tags, protocols, applicability
    python tools/library_diff.py needed <baseline> [--track T] [--group G]   # записи needed: что осталось сгенерировать
    python tools/library_diff.py full ID,ID                             # полный текст записей (закрытые отказывает)
    python tools/library_diff.py apply <baseline> <decisions.yaml>      # {ID: {decision, reason}}; removed - окончательное удаление записи из базы
    python tools/library_diff.py sync <каталог-проекта-тестов> <модуль>   # после генерации: needed с тестами -> applied (вызывает генератор)

База: module, library_version, selected_at, records: {ID: {decision, track, status, hash, steps, reason}}.
decision: applied | needed (применима, тестов нет; reason обязателен) | not_applicable (reason обязателен) | human (sg-restricted и ai_generation.restricted, не перезаписывается) | pending.
--library: manifest.yaml (в том числе из выгрузки) или каталог библиотеки; по умолчанию - эта библиотека (манифест, иначе
расчёт по каталогу). Содержимое закрытых записей инструмент не выводит.
"""
import argparse
import datetime
import json
import re
import sys
from pathlib import Path

import yaml

from library import setup_console
from library_manifest import MANIFEST, ROOT, build_manifest, closed_ids, load_checks, parse, record_hash, step_hashes

DECISIONS = ("applied", "needed", "not_applicable", "pending")
LIB_LINE = re.compile(r"Библиотека:[ \t]*([^\n]*)")
ID_TOKEN = re.compile(r"[A-Z0-9][A-Za-z0-9_.-]*")
OWN_PROTOCOLS = {"rest", "generic"}


def security_track() -> set:
    from security_groups import compute
    index, _, _ = compute()
    return {i for ids in index.values() for i in ids}


def applied_ids(collection: Path, known: set) -> set:
    """ID из строк «Библиотека: ...» файлов коллекции (только известные библиотеке)."""
    out = set()
    for f in collection.rglob("*.yaml"):
        for line in LIB_LINE.findall(f.read_text(encoding="utf-8", errors="replace")):
            out |= {t for t in ID_TOKEN.findall(line) if t in known}
    return out


def dump_baseline(path: Path, data: dict):
    lines = ["# База подбора (ADR 0016): решения по записям библиотеки. Меняется только при подборе (library_diff.py apply).",
             f"module: {data['module']}", f'library_version: "{data["library_version"]}"', f'selected_at: "{data["selected_at"]}"',
             "records:"]
    for i, e in sorted(data["records"].items()):
        lines.append(f'  "{i}":')
        lines.append(f"    decision: {e['decision']}")
        lines.append(f"    track: {e['track']}")
        lines.append(f"    status: {e['status']}")
        lines.append(f'    hash: "{e["hash"]}"')
        lines.append("    steps: [" + ", ".join(f'"{h}"' for h in e["steps"]) + "]")
        if e.get("reason"):
            lines.append(f"    reason: {json.dumps(str(e['reason']), ensure_ascii=False)}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def load_baseline(path) -> dict:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))


def library_manifest(spec=None) -> dict:
    """Манифест: файл manifest.yaml, или каталог (манифест из него, иначе расчёт по checks/), или эта библиотека."""
    if spec:
        p = Path(spec)
        if p.is_file():
            return parse(p.read_text(encoding="utf-8"))
        if (p / "manifest.yaml").exists():
            return parse((p / "manifest.yaml").read_text(encoding="utf-8"))
        if (p / "checks").is_dir():
            return build_manifest(p)
        sys.exit(f"--library: нет манифеста и каталога checks в {p}")
    if MANIFEST.exists():
        return parse(MANIFEST.read_text(encoding="utf-8"))
    return build_manifest()


def cmd_init(project: Path, module: str):
    collection = project / "postman" / "collections" / module
    if not collection.is_dir():
        sys.exit(f"нет коллекции {collection}")
    pairs, errors = load_checks()
    if errors:
        sys.exit("ошибки библиотеки: " + "; ".join(errors[:3]))
    manifest = build_manifest(pairs=pairs)
    closed, sec = closed_ids(pairs), security_track()
    applied = applied_ids(collection, {c["id"] for _, c in pairs})
    records = {}
    for path, c in pairs:
        i = c["id"]
        parts = path.relative_to(ROOT / "checks").parts
        protocols = set(c.get("protocols") or [])
        entry = {"track": "security" if i in sec else "functional", "status": str(c.get("status")),
                 "hash": record_hash(c), "steps": step_hashes(c)}
        if i in closed:
            entry.update(decision="human", reason="закрытая запись (sg-restricted или ai_generation.restricted)")
        elif i in applied:
            entry.update(decision="applied")
        elif parts[0] in ("ui", "db"):
            entry.update(decision="not_applicable", reason=f"каталог {parts[0]}: проверки не API")
        elif protocols and not protocols & OWN_PROTOCOLS:
            entry.update(decision="not_applicable", reason="протоколы: " + ", ".join(sorted(protocols)))
        else:
            entry["decision"] = "pending"
        records[i] = entry
    target = project / "docs" / "modules" / module / "library-baseline.yaml"
    dump_baseline(target, {"module": module, "library_version": manifest["version"],
                           "selected_at": datetime.date.today().isoformat(), "records": records})
    print(f"{target}: версия {manifest['version']}, записей {len(records)}")
    count(records)


def count(records: dict):
    from collections import Counter
    print("decision: " + ", ".join(f"{k} {v}" for k, v in sorted(Counter(e["decision"] for e in records.values()).items())))
    print("track: " + ", ".join(f"{k} {v}" for k, v in sorted(Counter(e["track"] for e in records.values()).items())))


def open_checks() -> dict:
    """Открытые записи этой библиотеки по ID: для текста новых шагов; закрытых здесь нет."""
    pairs, _ = load_checks()
    closed = closed_ids(pairs)
    return {c["id"]: c for _, c in pairs if c["id"] not in closed}


def change_details(check, old_steps: list) -> list:
    """Что показать об изменённой записи: новые шаги; пусто - текст недоступен (закрытая запись или только манифест)."""
    if not check:
        return []
    added = [s for h, s in zip(step_hashes(check), check.get("steps") or []) if h not in old_steps]
    if not added:
        return [f"    шаги те же: изменены expected, preconditions или applicability - library_diff.py full {check['id']}"]
    return ["    + " + (s if isinstance(s, str) else json.dumps(s, ensure_ascii=False)) for s in added]


def cmd_diff(baseline: Path, library=None):
    base = load_baseline(baseline)
    man = library_manifest(library)
    lib, recs = man["records"], base["records"]
    partial = man.get("scope") == "partial"
    checks = open_checks() if library is None else {}
    new = sorted(i for i in lib if i not in recs)
    changed, approved = [], []
    for i, e in sorted(recs.items()):
        c = lib.get(i)
        if not c:
            continue
        if c["hash"] != e["hash"]:
            add, rem = len(set(c["steps"]) - set(e["steps"])), len(set(e["steps"]) - set(c["steps"]))
            changed.append("\n  ".join([f"{i} [{e['decision']}] шагов: +{add} -{rem}", *change_details(checks.get(i), e["steps"])]))
        if e["status"] != "approved" and c["status"] == "approved":
            approved.append(i)
    missing = sorted(i for i in recs if i not in lib)
    pending = sorted(i for i, e in recs.items() if e["decision"] == "pending" and e["status"] == "approved" and i in lib)
    print(f"база: {base['module']}, версия {base['library_version']} ({base['selected_at']}); библиотека: {man['version']} (scope {man['scope']})")
    print(f"новые ({len(new)}): " + ", ".join(new))
    print(f"изменённые ({len(changed)}):" + "".join(f"\n  {x}" for x in changed))
    print(f"ставшие approved ({len(approved)}): " + ", ".join(approved))
    if partial:
        print(f"нет в поставке ({len(missing)}; в поставке пропущено записей: {man.get('omitted', '?')}): не считаются удалёнными")
    else:
        note = f" (в поставке пропущено закрытых: {man['omitted']})" if man.get("omitted") else ""
        print(f"удалённые ({len(missing)}){note}: " + ", ".join(missing))
    print(f"pending approved ({len(pending)})")
    print(f"нужны тесты, needed ({sum(e['decision'] == 'needed' for e in recs.values())})")


def cmd_compact(baseline: Path, track: str):
    recs = load_baseline(baseline)["records"]
    pairs, _ = load_checks()
    closed, sec = closed_ids(pairs), security_track()
    n = 0
    for _, c in pairs:
        i = c["id"]
        e = recs.get(i) or {"decision": "pending", "track": "security" if i in sec else "functional"}   # новая запись библиотеки
        if e["decision"] != "pending" or e["track"] != track or c.get("status") != "approved" or i in closed:
            continue
        app = c.get("applicability") or {}
        print(f"{i} | {c.get('title', '')} | {c.get('category')} | tags: {', '.join(map(str, c.get('tags') or []))} | "
              f"protocols: {', '.join(c.get('protocols') or [])}\n  when: {app.get('when')} | skip_when: {app.get('skip_when')}")
        n += 1
    print(f"pending {track}: {n}", file=sys.stderr)


def cmd_needed(baseline: Path, track=None, group=None):
    from collections import Counter
    from security_groups import compute
    index, _, _ = compute()
    if group and group not in index:
        sys.exit(f"нет группы {group}: {', '.join(sorted(index))}")
    group_of = {i: g for g, ids in index.items() for i in ids}
    rows = [(i, e["track"], group_of.get(i, "-"), e.get("reason", "")) for i, e in sorted(load_baseline(baseline)["records"].items())
            if e["decision"] == "needed" and track in (None, e["track"]) and group in (None, group_of.get(i))]
    for row in rows:
        print(" | ".join(row))
    print(f"needed: {len(rows)}; по группам: " + ", ".join(f"{g} {n}" for g, n in sorted(Counter(r[2] for r in rows).items())))


def cmd_sync(project: Path, module: str):
    """После генерации: needed, по которым появились тесты, -> applied. Версию подбора не меняет: новые решения не приняты."""
    baseline = project / "docs" / "modules" / module / "library-baseline.yaml"
    if not baseline.exists():
        print(f"база подбора: нет {baseline} - первый подбор: library_diff.py init")
        return
    base = load_baseline(baseline)
    recs = base["records"]
    tested = applied_ids(project / "postman" / "collections" / module, set(recs))
    moved = sorted(i for i, e in recs.items() if e["decision"] == "needed" and i in tested)
    for i in moved:
        recs[i]["decision"] = "applied"
        recs[i].pop("reason", None)
    if moved:
        dump_baseline(baseline, base)
    lost = sorted(i for i, e in recs.items() if e["decision"] == "applied" and i not in tested)
    current = library_manifest()["version"]
    print(f"база подбора: needed -> applied {len(moved)}, needed осталось {sum(e['decision'] == 'needed' for e in recs.values())}")
    if lost:
        print(f"ВНИМАНИЕ: applied без тестов в коллекции ({len(lost)}): " + ", ".join(lost))
    if base["library_version"] != current:
        print(f"ВНИМАНИЕ: база подбора {base['library_version']} отстаёт от библиотеки {current} - library_diff.py diff")


def cmd_full(ids):
    pairs, _ = load_checks()
    closed = closed_ids(pairs)
    by_id = {c["id"]: c for _, c in pairs}
    rc = 0
    for i in [x.strip() for x in ids.split(",") if x.strip()]:
        if i in closed:
            print(f"{i}: закрытая запись - полный текст не выдаётся")
            rc = 1
        elif i not in by_id:
            print(f"{i}: нет в библиотеке")
            rc = 1
        else:
            print(yaml.safe_dump(by_id[i], allow_unicode=True, sort_keys=False, width=1000) + "---")
    return rc


def cmd_apply(baseline: Path, decisions_file: Path):
    base = load_baseline(baseline)
    decisions = yaml.safe_load(decisions_file.read_text(encoding="utf-8")) or {}
    pairs, _ = load_checks()
    manifest = build_manifest(pairs=pairs)
    lib = manifest["records"]
    sec = security_track()
    recs, errors, skipped = base["records"], [], []
    for i, d in decisions.items():
        d = d or {}
        if d.get("decision") == "removed":     # окончательное удаление записи: убирает её из базы
            if i in lib or i not in recs:
                errors.append(f"{i}: removed - только для записи базы, которой нет в библиотеке")
            elif not str(d.get("reason") or "").strip():
                errors.append(f"{i}: removed без причины")
        elif i not in lib:
            errors.append(f"{i}: нет в библиотеке")
        elif d.get("decision") not in DECISIONS:
            errors.append(f"{i}: decision должен быть один из {', '.join(DECISIONS)}")
        elif d["decision"] in ("needed", "not_applicable") and not str(d.get("reason") or "").strip():
            errors.append(f"{i}: {d['decision']} без причины")
    if errors:
        for e in errors:
            print("ERROR:", e)
        return 1
    for i, e in lib.items():       # новые записи библиотеки попадают в базу (pending), чтобы не потеряться
        if i not in recs:
            recs[i] = {"decision": "pending", "track": "security" if i in sec else "functional",
                       "status": e["status"], "hash": e["hash"], "steps": e["steps"]}
    for i, d in decisions.items():
        cur, e = recs[i], lib.get(i)
        if cur["decision"] == "human":
            skipped.append(i)
            continue
        if d["decision"] == "removed":
            del recs[i]
            continue
        cur.update(decision=d["decision"], status=e["status"], hash=e["hash"], steps=e["steps"])
        if d.get("reason"):
            cur["reason"] = d["reason"]
        else:
            cur.pop("reason", None)
    base["library_version"], base["selected_at"] = manifest["version"], datetime.date.today().isoformat()
    dump_baseline(baseline, base)
    print(f"применено решений: {len(decisions) - len(skipped)}, human не перезаписано: {len(skipped)}; версия {manifest['version']}")
    count(recs)
    return 0


def main():
    setup_console()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("init")
    p.add_argument("project", type=Path)
    p.add_argument("module")
    p = sub.add_parser("diff")
    p.add_argument("baseline", type=Path)
    p.add_argument("--library")
    p = sub.add_parser("compact")
    p.add_argument("baseline", type=Path)
    p.add_argument("--track", choices=("functional", "security"), required=True)
    p = sub.add_parser("needed")
    p.add_argument("baseline", type=Path)
    p.add_argument("--track", choices=("functional", "security"))
    p.add_argument("--group")
    p = sub.add_parser("sync")
    p.add_argument("project", type=Path)
    p.add_argument("module")
    p = sub.add_parser("full")
    p.add_argument("ids")
    p = sub.add_parser("apply")
    p.add_argument("baseline", type=Path)
    p.add_argument("decisions", type=Path)
    a = ap.parse_args()
    if a.cmd == "init":
        cmd_init(a.project, a.module)
    elif a.cmd == "diff":
        cmd_diff(a.baseline, a.library)
    elif a.cmd == "compact":
        cmd_compact(a.baseline, a.track)
    elif a.cmd == "needed":
        cmd_needed(a.baseline, a.track, a.group)
    elif a.cmd == "sync":
        cmd_sync(a.project, a.module)
    elif a.cmd == "full":
        return cmd_full(a.ids)
    else:
        return cmd_apply(a.baseline, a.decisions)
    return 0


if __name__ == "__main__":
    sys.exit(main())
