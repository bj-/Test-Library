"""Перенос подробностей записей с ограничением генерации ассистентом в Api/restricted/ (ADR 0008).

    python tools/restrict_records.py --dry-run        # какие записи будут перенесены (только id)
    python tools/restrict_records.py                  # перенести
    python tools/restrict_records.py --restore ID     # вернуть подробности записи в checks/ (снятие ограничения)
    python tools/restrict_records.py --check          # у каждой restricted-записи есть файл подробностей
    python tools/restrict_records.py --suggest        # кандидаты под флаг по taxonomy/ai-stop-topics.yaml (только id)
    python tools/restrict_records.py --flag ID ...    # поставить restricted (решение человека), затем перенос

Для записи с `automation.ai_generation.restricted: true` поля description, preconditions, steps, expected уходят в
`Api/restricted/<ID>.md` (YAML-блок - восстанавливается `--restore`), в записи остаются заглушки со ссылкой и
`ai_generation.details`. Каталог restricted/ ассистенту (LLM) не читать: запрет в .claude/settings.json, правило
в CLAUDE.md. Скрипт содержимое не печатает - только id и счётчики.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml

from library import setup_console

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "restricted"
MOVED = ("description", "preconditions", "steps", "expected")
FENCE = "```yaml"


def stub(cid):
    ref = f"restricted/{cid}.md"
    note = f"Подробности - Api/{ref} (только для человека, ассистенту не читать; ADR 0008)."
    return ref, {"description": note, "preconditions": [note], "steps": [{"action": note}], "expected": [note]}


def blocks(text):
    """Записи файла checks/: (id, начало, конец) по строкам `- id: ` в начале строки."""
    starts = [(m.group(1), m.start()) for m in re.finditer(r"^- id: *(\S+)\s*$", text, re.M)]
    return [(cid, s, starts[i + 1][1] if i + 1 < len(starts) else len(text)) for i, (cid, s) in enumerate(starts)]


def dump(rec):
    return yaml.safe_dump([rec], allow_unicode=True, sort_keys=False, width=120, default_flow_style=False)


def details_md(cid, title, moved):
    return (f"# {cid}. {title}\n\n"
            "> Только для человека. Ассистенту (LLM) этот файл не читать и не пересказывать - ADR Test-Library 0008.\n"
            "> Вернуть в запись: `python tools/restrict_records.py --restore " + cid + "`.\n\n"
            + FENCE + "\n" + yaml.safe_dump(moved, allow_unicode=True, sort_keys=False, width=120) + "```\n")


def process(path, dry, restore=None):
    text = path.read_text(encoding="utf-8")
    out, pos, done = [], 0, []
    for cid, s, e in blocks(text):
        rec = yaml.safe_load(text[s:e])[0]
        g = (rec.get("automation") or {}).get("ai_generation") or {}
        if restore:
            if cid != restore or not g.get("details"):
                continue
            src = ROOT / g["details"]
            body = src.read_text(encoding="utf-8")
            moved = yaml.safe_load(body[body.index(FENCE) + len(FENCE):body.rindex("```")])
            rec.update(moved)
            g.pop("details", None)
        else:
            if not g.get("restricted") or g.get("details"):
                continue
            ref, placeholders = stub(cid)
            moved = {k: rec[k] for k in MOVED if k in rec}
            if not dry:
                OUT.mkdir(exist_ok=True)
                (OUT / f"{cid}.md").write_text(details_md(cid, rec.get("title", ""), moved), encoding="utf-8")
            for k in MOVED:
                if k in rec:
                    rec[k] = placeholders[k]
            g["details"] = ref
        out += [text[pos:s], dump(rec)]
        pos = e
        done.append(cid)
    if done and not dry:
        path.write_text("".join(out) + text[pos:], encoding="utf-8")
    return done


def all_checks():
    for path in sorted((ROOT / "checks").glob("**/*.yaml")):
        for c in (yaml.safe_load(path.read_text(encoding="utf-8")) or {}).get("checks") or []:
            yield path, c


def stop_topics():
    return yaml.safe_load((ROOT / "taxonomy" / "ai-stop-topics.yaml").read_text(encoding="utf-8"))


def suggest():
    """Кандидаты: совпадение слов-признаков стоп-темы в id, заголовке или метках; печатаются только id и тема."""
    st, n = stop_topics(), 0
    for _, c in all_checks():
        if ((c.get("automation") or {}).get("ai_generation") or {}).get("restricted"):
            continue
        hay = " ".join([c["id"], c.get("title", ""), *map(str, c.get("tags") or [])])
        hits = [t["id"] for t in st["topics"] if any(w in hay for w in t["match"])]
        if hits:
            print(f"{c['id']}: {', '.join(hits)}")
            n += 1
    print(f"кандидатов: {n} - решение о флаге за человеком: --flag ID ...")
    return 0


def flag(ids, today):
    reason = " ".join(stop_topics()["reason"].split())
    left = set(ids)
    for path in sorted((ROOT / "checks").glob("**/*.yaml")):
        text = path.read_text(encoding="utf-8")
        out, pos = [], 0
        for cid, s, e in blocks(text):
            if cid not in left:
                continue
            rec = yaml.safe_load(text[s:e])[0]
            rec.setdefault("automation", {})["ai_generation"] = dict(
                {"restricted": True, "reason": reason, "noted": f"{today}, restrict_records.py --flag"},
                **{k: v for k, v in ((rec["automation"].get("ai_generation")) or {}).items() if k != "restricted"})
            out += [text[pos:s], dump(rec)]
            pos = e
            left.discard(cid)
            print(f"{path.relative_to(ROOT).as_posix()}: {cid} - restricted")
        if out:
            path.write_text("".join(out) + text[pos:], encoding="utf-8")
    if left:
        print("не найдены: " + ", ".join(sorted(left)))
    return 1 if left else 0


def check():
    bad = []
    for path in sorted((ROOT / "checks").glob("**/*.yaml")):
        for c in (yaml.safe_load(path.read_text(encoding="utf-8")) or {}).get("checks") or []:
            g = (c.get("automation") or {}).get("ai_generation") or {}
            if g.get("restricted") and not (g.get("details") and (ROOT / g["details"]).exists()):
                bad.append(c["id"])
    print(f"restricted без файла подробностей: {len(bad)}" + (": " + ", ".join(bad) if bad else ""))
    return 1 if bad else 0


def main():
    setup_console()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--restore", metavar="ID")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--suggest", action="store_true")
    ap.add_argument("--flag", nargs="+", metavar="ID")
    a = ap.parse_args()
    if a.check:
        return check()
    if a.suggest:
        return suggest()
    if a.flag:
        import datetime
        return flag(a.flag, datetime.date.today().isoformat())
    total = []
    for path in sorted((ROOT / "checks").glob("**/*.yaml")):
        done = process(path, a.dry_run, a.restore)
        if done:
            print(f"{path.relative_to(ROOT).as_posix()}: {', '.join(done)}")
            total += done
    verb = "вернуть" if a.restore else "перенести"
    print(f"{'план' if a.dry_run else 'готово'}: {verb} {len(total)} записей")
    if a.restore and total:
        print(f"файл {OUT.name}/{a.restore}.md оставлен: удалить вручную после снятия ограничения (restricted: false)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
