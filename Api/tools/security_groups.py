"""Группы проверок безопасности (ADR 0011): назначение, индекс, выборка.

    python tools/security_groups.py index              # пересобрать taxonomy/security-groups-index.yaml
    python tools/security_groups.py index --check      # индекс актуален? (validate_library.py вызывает сам)
    python tools/security_groups.py list sg-token      # записи группы: id, приоритет, заголовок
    python tools/security_groups.py list sg-token --ids   # только id через запятую (для export_for_llm --records)
    python tools/security_groups.py of AUTH-JWT-ALG-NONE INJ-SQL   # группа записей
    python tools/security_groups.py stats              # сколько записей в каждой группе

Правила - taxonomy/security-groups.yaml. Запись группы sg-restricted печатается только id (без заголовка).
"""
import argparse
import fnmatch
import sys
from pathlib import Path

import yaml

from library import PRIORITY_RANK, iter_checks, setup_console

ROOT = Path(__file__).resolve().parents[1]
RULES = ROOT / "taxonomy" / "security-groups.yaml"
INDEX = ROOT / "taxonomy" / "security-groups-index.yaml"
STOP = ROOT / "taxonomy" / "ai-stop-topics.yaml"
RESTRICTED = "sg-restricted"
HEADER = ("# Индекс групп безопасности (ADR 0011): группа -> записи. Собирается `python tools/security_groups.py index`,\n"
          "# вручную не править; правила - security-groups.yaml.\n")


def load_rules():
    return yaml.safe_load(RULES.read_text(encoding="utf-8"))


def in_scope(path, check):
    return "security" in path.relative_to(ROOT / "checks").parts or check.get("category") == "security" or "security" in (check.get("tags") or []) or bool(check.get("security_group"))


def stop_hit(check, topics):
    hay = " ".join([check["id"], check.get("title", ""), *map(str, check.get("tags") or [])])
    return any(w in hay for t in topics for w in t["match"])


def group_of(check, rules, topics):
    """Группа записи: явное поле -> restricted (флаг или стоп-тема) -> правила по порядку -> default."""
    if check.get("security_group"):
        return check["security_group"]
    if ((check.get("automation") or {}).get("ai_generation") or {}).get("restricted") or stop_hit(check, topics):
        return RESTRICTED
    tags = set(check.get("tags") or [])
    for r in rules["rules"]:
        if any(fnmatch.fnmatchcase(check["id"], p) for p in r.get("ids") or []) or tags & set(r.get("tags") or []):
            return r["group"]
    return rules["default"]


def compute():
    rules = load_rules()
    topics = yaml.safe_load(STOP.read_text(encoding="utf-8"))["topics"]
    known = {g["id"] for g in rules["groups"]}
    errors, out, checks = [], {g["id"]: [] for g in rules["groups"]}, {}
    for path, c in iter_checks(ROOT, errors):
        if not c.get("id") or not in_scope(path, c):
            continue
        g = group_of(c, rules, topics)
        if g not in known:
            errors.append(f"{c['id']}: неизвестная группа {g} (security-groups.yaml)")
            continue
        out[g].append(c["id"])
        checks[c["id"]] = c
    for g in out:
        out[g].sort()
    return out, checks, errors


def render(index):
    return HEADER + yaml.safe_dump(index, allow_unicode=True, sort_keys=False, width=1000)


def load_index(path=INDEX):
    """{id: группа} из индекса - для других инструментов (движок test-engine читает тот же файл)."""
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    return {i: g for g, ids in data.items() for i in ids or []}


def check_index():
    """Ошибки актуальности индекса (пустой список - актуален)."""
    index, _, errors = compute()
    if not INDEX.exists() or INDEX.read_text(encoding="utf-8") != render(index):
        errors.append(f"{INDEX.name} устарел - python tools/security_groups.py index")
    return errors


def main():
    setup_console()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("index")
    p.add_argument("--check", action="store_true")
    p = sub.add_parser("list")
    p.add_argument("group")
    p.add_argument("--ids", action="store_true")
    p = sub.add_parser("of")
    p.add_argument("ids", nargs="+")
    sub.add_parser("stats")
    a = ap.parse_args()

    if a.cmd == "index" and a.check:
        errors = check_index()
        for e in errors:
            print("ERROR:", e)
        print("актуален" if not errors else "")
        return 1 if errors else 0
    index, checks, errors = compute()
    for e in errors:
        print("ERROR:", e, file=sys.stderr)
    if a.cmd == "index":
        INDEX.write_text(render(index), encoding="utf-8")
        print(f"{INDEX.relative_to(ROOT).as_posix()}: " + ", ".join(f"{g} {len(v)}" for g, v in index.items()))
    elif a.cmd == "stats":
        rules = load_rules()
        ex = rules.get("executors") or {}
        for g in rules["groups"]:
            who = g.get("executor", "-")
            model = (ex.get(who) or {}).get("model")
            label = f"{who} ({model})" if model else who
            print(f"{g['id']:<14} {len(index[g['id']]):>4}  [{g['risk']}/{label}] {g['title']}")
        print(f"всего: {sum(map(len, index.values()))}")
    elif a.cmd == "of":
        inv = {i: g for g, ids in index.items() for i in ids}
        for i in a.ids:
            print(f"{i}: {inv.get(i, '- (нет в группах безопасности)')}")
    elif a.cmd == "list":
        if a.group not in index:
            sys.exit(f"нет группы {a.group}; группы: {', '.join(index)}")
        ids = sorted(index[a.group], key=lambda i: (PRIORITY_RANK.get(checks[i].get("priority"), 3), i))
        if a.ids:
            print(",".join(ids))
        else:
            for i in ids:
                c = checks[i]
                title = "" if a.group == RESTRICTED else c.get("title", "")
                print(f"{c.get('priority', '')}\t{i}\t{c.get('status', '')}\t{title}")
            print(f"записей: {len(ids)}", file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
