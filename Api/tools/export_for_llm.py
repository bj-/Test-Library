"""Выгрузка для внешних LLM (web-интерфейс, без доступа к репозиторию) - всегда без закрытых частей (ADR 0008, 0009).

    python Api/tools/export_for_llm.py                         # вся библиотека (файлы из git) -> Api/build/export/test-library-<дата>.zip
    python Api/tools/export_for_llm.py --records INJ-SQL,INJ-REFLECTED-XSS   # только эти записи + порядок сбора значений
    python Api/tools/export_for_llm.py --group sg-token      # записи группы безопасности (ADR 0011), кроме sg-restricted
    python Api/tools/export_for_llm.py --task ../PostmanScripts/docs/tasks/attempt-limit.md   # задание + его файлы

Не попадает никогда: каталоги restricted/, словарь test-data/ (кроме README.md), .claude/, блоки
<!-- ai-restricted:begin/end --> (заменяются пометкой). Задание - Markdown с заголовком YAML `files:` - пути к файлам
и каталогам относительно каталога репозиториев (C:\\Git); первым в архиве лежит TASK.md.
"""
import argparse
import datetime
import re
import subprocess
import sys
import zipfile
from pathlib import Path

import yaml

LIB = Path(__file__).resolve().parents[2]          # Test-Library
GIT_ROOT = LIB.parent                              # C:\Git
OUT = LIB / "Api" / "build" / "export"
BLOCK = re.compile(r"<!-- ai-restricted:begin -->.*?(?:<!-- ai-restricted:end -->|\Z)", re.S)
HIDDEN = "[скрыто: ai-restricted - читает человек]"
TEXT = {".md", ".yaml", ".yml", ".json", ".py", ".js", ".txt", ".csv", ".ids", ".jsonl", ".toml", ".cmd", ".sh"}


def closed(rel):
    parts = [p.lower() for p in Path(rel).parts]
    if "restricted" in parts or ".claude" in parts or ".git" in parts or "__pycache__" in parts:
        return True
    if "test-data" in parts:
        return Path(rel).name != "README.md"
    return False


def tracked(repo, sub="."):
    out = subprocess.run(["git", "-C", str(repo), "ls-files", "-z", "--", sub], capture_output=True).stdout
    return [repo / p for p in out.decode("utf-8").split("\0") if p]


def content(path):
    data = path.read_bytes()
    if path.suffix.lower() in TEXT:
        return BLOCK.sub(HIDDEN, data.decode("utf-8", errors="replace")).encode("utf-8")
    return data


def files_under(p):
    p = p.resolve()
    if p.is_file():
        return [p]
    top = subprocess.run(["git", "-C", str(p), "rev-parse", "--show-toplevel"], capture_output=True, text=True).stdout.strip()
    return tracked(Path(top), str(p.relative_to(Path(top).resolve()))) if top else sorted(x for x in p.rglob("*") if x.is_file())


def write_zip(name, entries):
    OUT.mkdir(exist_ok=True)
    out = OUT / f"{name}-{datetime.date.today().isoformat()}.zip"
    n = skipped = 0
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for arc, src in entries:
            if closed(arc) or (isinstance(src, Path) and closed(src.relative_to(GIT_ROOT) if src.is_relative_to(GIT_ROOT) else src)):
                skipped += 1
                continue
            z.writestr(arc, src if isinstance(src, bytes) else content(src))
            n += 1
    print(f"файлов: {n}, закрытых пропущено: {skipped} -> {out}")
    return out


def export_library():
    write_zip("test-library", [(p.relative_to(GIT_ROOT).as_posix(), p) for p in tracked(LIB) if p.is_file()])


def export_records(ids):
    want, found, skipped = set(ids), [], set()
    for f in sorted((LIB / "Api" / "checks").rglob("*.yaml")):
        d = yaml.safe_load(f.read_text(encoding="utf-8")) or {}
        for r in (d.get("checks") if isinstance(d, dict) else d) or []:
            if isinstance(r, dict) and r.get("id") in want:
                if (r.get("automation") or {}).get("ai_generation", {}).get("restricted"):
                    print(f"{r['id']}: ai_generation.restricted - не выгружается (ADR 0008)")
                    skipped.add(r["id"])
                    continue
                found.append(r)
    missing = want - {r["id"] for r in found} - skipped
    if missing:
        print("не найдено: " + ", ".join(sorted(missing)))
    text = BLOCK.sub(HIDDEN, yaml.safe_dump({"checks": found}, allow_unicode=True, sort_keys=False, width=1000))
    extra = ["Test-Library/Process/test-data.md", "Test-Library/Api/test-data/README.md",
             "Test-Library/Api/schema/check.schema.json", "Test-Library/Api/taxonomy/test-data-index.yaml"]
    write_zip("records", [("records.yaml", text.encode("utf-8"))] + [(x, GIT_ROOT / x) for x in extra if (GIT_ROOT / x).exists()])


def export_task(task):
    task = task.resolve()
    text = task.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    files = (yaml.safe_load(m.group(1)) or {}).get("files", []) if m else []
    entries = [("TASK.md", task)]
    for f in files:
        src = GIT_ROOT / f
        if not src.exists():
            print(f"нет файла из заголовка задания: {f}")
            continue
        entries += [(p.relative_to(GIT_ROOT).as_posix(), p) for p in files_under(src)]
    write_zip(task.stem, entries)


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--records", help="ID записей через запятую")
    ap.add_argument("--task", type=Path, help="файл задания с заголовком files:")
    ap.add_argument("--group", help="группа безопасности из taxonomy/security-groups.yaml (ADR 0011)")
    a = ap.parse_args()
    if a.group:
        sys.path.insert(0, str(Path(__file__).parent))
        from security_groups import RESTRICTED, load_index
        if a.group == RESTRICTED:
            sys.exit(f"{RESTRICTED} не выгружается (ADR 0008)")
        ids = sorted(i for i, g in load_index().items() if g == a.group)
        if not ids:
            sys.exit(f"в группе {a.group} нет записей (или нет такой группы)")
        export_records(ids)
    elif a.task:
        export_task(a.task)
    elif a.records:
        export_records([x.strip() for x in a.records.split(",") if x.strip()])
    else:
        export_library()


if __name__ == "__main__":
    main()
