"""Словарь тестовых значений по ссылке (ADR 0009): значения - в test-data/dict/, в записях и тестах - только ID.

    python tools/test_data.py next-id SQLI [N]  # зарезервировать N следующих ID класса (печатает ID)
    python tools/test_data.py ingest            # inbox/*.yaml -> dict/<КЛАСС>.yaml, индекс; дубли значений -> ссылки
    python tools/test_data.py merge OLD NEW     # убрать OLD из словаря, ссылки на него в записях -> NEW
    python tools/test_data.py index             # пересобрать публичный индекс taxonomy/test-data-index.yaml
    python tools/test_data.py check             # ссылки TD-* в записях библиотеки есть в индексе
    python tools/test_data.py env               # окружение Postman со значениями -> test-data/build/ (для человека)
    python tools/test_data.py html              # страница «ID -> значение» для человека -> test-data/build/index.html

Значения ни одна команда не печатает: в консоль - только ID и счётчики (вывод читает ассистент).
Формат записи словаря и порядок работы - test-data/README.md, Process/test-data.md.
"""
import argparse
import base64
import datetime
import hashlib
import html
import json
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]                # Api/
TD = ROOT / "test-data"
DICT, INBOX, BUILD = TD / "dict", TD / "inbox", TD / "build"
INDEX = ROOT / "taxonomy" / "test-data-index.yaml"
ID_RE = re.compile(r"^TD-([A-Z][A-Z0-9]*)-(\d{4})$")
REF_RE = re.compile(r"\bTD-[A-Z][A-Z0-9]*-\d{4}\b|\bTDS-[A-Z][A-Z0-9-]*\b")   # значение или набор
FIELDS = ("id", "value", "encoding", "set", "title", "records", "source", "added")


def load_list(path):
    data = yaml.safe_load(path.read_text(encoding="utf-8")) if path.exists() else None
    return data or []


def dump_list(path, items):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(items, allow_unicode=True, sort_keys=False, width=1000), encoding="utf-8")


def raw_value(e):
    """Значение как строка для запроса: encoding base64 - для двоичных и чувствительных к пробелам значений."""
    v = str(e.get("value", ""))
    return base64.b64decode(v).decode("utf-8", errors="surrogateescape") if e.get("encoding") == "base64" else v


def load_dict():
    out = {}
    for f in sorted(DICT.glob("*.yaml")):
        for e in load_list(f):
            out[e["id"]] = e
    return out


def load_index():
    d = yaml.safe_load(INDEX.read_text(encoding="utf-8")) if INDEX.exists() else None
    return d or {"values": {}, "sets": {}, "reserved": []}


def write_index(entries, reserved):
    values, sets = {}, {}
    for i in sorted(entries):
        e = entries[i]
        v = raw_value(e)
        values[i] = {"title": e.get("title", ""), "set": e.get("set"), "records": e.get("records") or [],
                     "length": len(v), "sha256": hashlib.sha256(v.encode("utf-8", "surrogateescape")).hexdigest()[:12]}
        values[i] = {k: x for k, x in values[i].items() if x not in (None, [])}
        if e.get("set"):
            sets.setdefault(e["set"], []).append(i)
    head = ("# Публичный индекс словаря тестовых значений (ADR 0009) - без значений, читать можно всем.\n"
            "# Генерируется: python tools/test_data.py index | ingest | next-id. Руками не править.\n")
    body = yaml.safe_dump({"values": values, "sets": sets, "reserved": sorted(set(reserved) - set(values))},
                          allow_unicode=True, sort_keys=False, width=1000)
    INDEX.write_text(head + body, encoding="utf-8")


def cmd_next_id(cls, n):
    if not re.fullmatch(r"[A-Z][A-Z0-9]*", cls):
        sys.exit("класс - латиница в верхнем регистре и цифры, например SQLI, XSS, PATH, JWT")
    idx = load_index()
    taken = set(idx.get("values") or {}) | set(idx.get("reserved") or [])
    nums = [int(m.group(2)) for m in map(ID_RE.match, taken) if m and m.group(1) == cls]
    new = [f"TD-{cls}-{k:04d}" for k in range(max(nums, default=0) + 1, max(nums, default=0) + 1 + n)]
    idx["reserved"] = sorted(set(idx.get("reserved") or []) | set(new))
    write_index(load_dict(), idx["reserved"])
    print("\n".join(new))


def relink(old, new):
    """Ссылки на значение-дубль в записях библиотеки -> на существующий ID."""
    n = 0
    for f in (ROOT / "checks").rglob("*.yaml"):
        t = f.read_text(encoding="utf-8")
        t2 = re.sub(rf"\b{re.escape(old)}\b", new, t)
        if t2 != t:
            f.write_text(t2, encoding="utf-8")
            n += 1
    return n


def cmd_ingest():
    entries = load_dict()
    by_value = {raw_value(e): i for i, e in entries.items()}
    idx = load_index()
    reserved = set(idx.get("reserved") or [])
    added, dupes, errors = [], [], []
    for f in sorted(INBOX.glob("*.yaml")):
        try:
            batch = load_list(f)
        except yaml.YAMLError as ex:
            errors.append(f"{f.name}: не YAML ({ex.__class__.__name__}) - файл оставлен")
            continue
        bad = False
        for e in batch:
            i = str(e.get("id", ""))
            if not ID_RE.match(i) or "value" not in e:
                errors.append(f"{f.name}: запись без id вида TD-<КЛАСС>-NNNN или без value ({i or '?'})")
                bad = True
                continue
            v = raw_value(e)
            if v in by_value:
                if by_value[v] != i:
                    dupes.append((i, by_value[v], relink(i, by_value[v])))
                continue
            if i in entries:
                errors.append(f"{f.name}: {i} уже занят другим значением - нужен новый ID (next-id)")
                bad = True
                continue
            e = {k: e[k] for k in FIELDS if k in e}
            e.setdefault("added", datetime.date.today().isoformat())
            entries[i] = e
            by_value[v] = i
            cls = ID_RE.match(i).group(1)
            dump_list(DICT / f"{cls}.yaml", sorted((x for x in entries.values() if ID_RE.match(x["id"]).group(1) == cls),
                                                   key=lambda x: x["id"]))
            added.append(i)
        if not bad:
            f.unlink()
    write_index(entries, reserved)
    print(f"добавлено: {len(added)}" + (f" - {' '.join(added)}" if added else ""))
    for new, old, files in dupes:
        print(f"дубль значения: {new} = {old}, ссылки заменены в {files} файлах записей")
    for e in errors:
        print("ошибка: " + e)
    return 1 if errors else 0


def cmd_merge(old, new):
    entries = load_dict()
    if old not in entries or new not in entries:
        sys.exit(f"нет в словаре: {old if old not in entries else new}")
    cls = ID_RE.match(old).group(1)
    dump_list(DICT / f"{cls}.yaml", [e for e in load_list(DICT / f"{cls}.yaml") if e["id"] != old])
    rec = sorted(set(entries[new].get("records") or []) | set(entries[old].get("records") or []))
    if rec:
        ncls = ID_RE.match(new).group(1)
        items = load_list(DICT / f"{ncls}.yaml")
        for e in items:
            if e["id"] == new:
                e["records"] = rec
        dump_list(DICT / f"{ncls}.yaml", items)
    del entries[old]
    write_index(load_dict(), load_index().get("reserved") or [])
    print(f"{old} -> {new}, ссылки заменены в {relink(old, new)} файлах записей")


def cmd_check():
    idx = load_index()
    known = set(idx.get("values") or {}) | set(idx.get("sets") or {})
    missing = {}
    for f in (ROOT / "checks").rglob("*.yaml"):
        for ref in REF_RE.findall(f.read_text(encoding="utf-8")):
            if ref not in known:
                missing.setdefault(ref, set()).add(f.relative_to(ROOT).as_posix())
    for ref, files in sorted(missing.items()):
        print(f"нет в словаре: {ref} - {', '.join(sorted(files))}")
    print(f"ссылок без значения: {len(missing)}")
    return 1 if missing else 0


def cmd_env():
    entries = load_dict()
    vals = [{"key": i, "value": raw_value(e), "enabled": True} for i, e in sorted(entries.items())]
    sets = {}
    for i, e in entries.items():
        if e.get("set"):
            sets.setdefault(e["set"], []).append(i)
    vals += [{"key": s, "value": json.dumps(sorted(ids)), "enabled": True} for s, ids in sorted(sets.items())]
    BUILD.mkdir(parents=True, exist_ok=True)
    out = BUILD / "test-data.postman_environment.json"
    out.write_text(json.dumps({"name": "test-data", "values": vals}, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"значений: {len(entries)}, наборов: {len(sets)} -> {out}")


def cmd_html():
    entries = load_dict()
    rows = "".join(f"<tr id='{i}'><td>{i}</td><td>{html.escape(e.get('set') or '')}</td><td>{html.escape(e.get('title', ''))}"
                   f"</td><td><code>{html.escape(raw_value(e))}</code></td><td>{html.escape(', '.join(e.get('records') or []))}"
                   f"</td></tr>" for i, e in sorted(entries.items()))
    BUILD.mkdir(parents=True, exist_ok=True)
    out = BUILD / "index.html"
    out.write_text("<!doctype html><meta charset='utf-8'><title>Тестовые значения</title>"
                   "<style>body{font:14px sans-serif}td{border:1px solid #ccc;padding:4px;vertical-align:top}"
                   "code{white-space:pre-wrap;word-break:break-all}</style><h1>Тестовые значения (ADR 0009)</h1>"
                   "<table><tr><th>ID</th><th>Набор</th><th>Назначение</th><th>Значение</th><th>Записи</th></tr>"
                   f"{rows}</table>", encoding="utf-8")
    print(f"значений: {len(entries)} -> {out}")


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("next-id")
    p.add_argument("cls")
    p.add_argument("n", nargs="?", type=int, default=1)
    p = sub.add_parser("merge")
    p.add_argument("old")
    p.add_argument("new")
    for c in ("ingest", "index", "check", "env", "html"):
        sub.add_parser(c)
    a = ap.parse_args()
    if a.cmd == "next-id":
        return cmd_next_id(a.cls, a.n)
    if a.cmd == "merge":
        return cmd_merge(a.old, a.new)
    if a.cmd == "index":
        return write_index(load_dict(), load_index().get("reserved") or [])
    return {"ingest": cmd_ingest, "check": cmd_check, "env": cmd_env, "html": cmd_html}[a.cmd]()


if __name__ == "__main__":
    sys.exit(main() or 0)
