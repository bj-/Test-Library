#!/usr/bin/env python3
"""Cross-review pack for draft records: a self-contained Markdown task for another LLM.

Usage (from Api/):
  draftcheck.py --layer api|db|ui            drafts from the inbox review of that layer (references 'inbox №N')
  draftcheck.py --ids A,B,C --name custom    any records by ID

Writes ideas/draftcheck/<name>.md: the task, the library principles, each record as YAML with the inbox ideas it came
from, and the index of all library records (to spot duplicates). The model reviews each record (approve / fix /
merge / reject); its answer is saved next to it (<name>.answer-N.md). Decisions follow the reconciliation rule of
mining/README.md (steps 6–7, item 7): where the models agree with Claude, or Claude agrees after re-evaluation, the
decision is taken; otherwise the human decides. Status `approved` is set by the human only.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from library import iter_checks, setup_console  # noqa: E402

OUT = Path("ideas/draftcheck")
README = Path("README.md")
INBOX = Path("ideas/inbox.md")
SPLIT = re.compile(r"(?<!\\)\|")
FIELDS = ("id", "title", "category", "protocols", "kind", "priority", "preconditions", "steps", "expected",
          "applicability", "automation", "references")
LAYERS = {"api": lambda c: not c["id"].startswith(("DB-", "UI-")),
          "db": lambda c: c["id"].startswith("DB-"),
          "ui": lambda c: c["id"].startswith("UI-")}

TASK = """## Задание для модели

Ты — ревьюер библиотеки шаблонов тестов (API, UI, БД). Ниже — черновые записи (`status: draft`), которые другая модель
написала по идеям из входящего списка. Для каждой записи суди по её тексту, исходным идеям и индексу библиотеки.

Для каждой записи ответь:

1. **Решение** — `approve` (можно утверждать как есть), `fix` (утверждать после правки — какой именно),
   `merge` (дублирует или почти дублирует запись из индекса — с какой и как объединить), `reject` (не проверка, слишком
   общая или продуктовая — почему).
2. **Шаги и ожидание** — исполнимы ли шаги как действия теста; проверяемо ли ожидание; не подогнано ли ожидание под одно
   поведение там, где источник допускает варианты (тогда — «по документации»).
3. **Применимость и условия** — верны ли протоколы и `when` / `skip_when`; указаны ли нужные доступы и инструменты.
4. **Почему** — одна-две строки.

Исходные идеи — мнение одного автора; если запись теряет или искажает смысл идеи, отметь это.
"""

ANSWER = """Формат ответа — одна таблица на все записи:

| # | ID | Решение | Что исправить / с чем объединить | Почему |
|---|---|---|---|---|
| 1 | AUTH-… | approve/fix/merge/reject | … | … |

В конце — 2–3 строки общего вывода: систематические ошибки, если есть.
"""


def principles() -> str:
    m = re.search(r"## Принципы\n(.*?)(?=\n## )", README.read_text(encoding="utf-8"), re.S)
    return m.group(1).strip() if m else ""


def inbox_ideas() -> dict[int, str]:
    out = {}
    for line in INBOX.read_text(encoding="utf-8").split("\n"):
        if re.match(r"^\| \d+ ", line):
            c = [x.strip() for x in SPLIT.split(line)]
            out[int(c[1])] = c[3]
    return out


def refs_of(check: dict) -> list[int]:
    text = yaml.safe_dump(check, allow_unicode=True)
    return sorted({int(n) for n in re.findall(r"inbox №(\d+)", text)} |
                  {int(n) for m in re.findall(r"inbox (№\d+(?:, №\d+)*)", text) for n in re.findall(r"\d+", m)})


def build(name: str, checks: list[dict]) -> str:
    ideas = inbox_ideas()
    out = ["# Перекрёстная проверка черновых записей библиотеки", "",
           f"Пакет `{name}`, записей: {len(checks)}. Записи и разбор входящих идей сделала модель Claude Opus 5.5.",
           "Этот файл целиком отдаётся другой LLM. Ответ модели вставить в чат внутренней сессии.", "",
           TASK, "Принципы библиотеки (из README):", "", principles(), "", ANSWER]
    for n, c in enumerate(checks, 1):
        rec = {k: c[k] for k in FIELDS if k in c}
        out += [f"## {n}. {c['id']}", "", "```yaml",
                yaml.safe_dump(rec, allow_unicode=True, sort_keys=False, width=110).strip(), "```", ""]
        src = refs_of(c)
        if src:
            out += ["Исходные идеи (inbox):", ""] + [f"- №{i}: {ideas.get(i, '—')}" for i in src] + [""]
    own = {c["id"] for c in checks}
    index = sorted((c["id"], c.get("category", ""), c.get("title", "")) for _, c in iter_checks(Path("."), [])
                   if not c["id"].startswith("REAL-") and c["id"] not in own)
    out += ["## Индекс библиотеки", "",
            f"Остальные записи ({len(index)}): ID | категория | заголовок. Записи этого пакета в индекс не входят.", "",
            "```text"]
    out += [" | ".join(row) for row in index] + ["```"]
    return "\n".join(out) + "\n"


def main() -> int:
    setup_console()
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--layer", choices=sorted(LAYERS))
    g.add_argument("--ids", help="ID записей через запятую")
    ap.add_argument("--name", help="имя пакета; по умолчанию inbox-<layer>")
    args = ap.parse_args()
    allc = [c for _, c in iter_checks(Path("."), [])]
    if args.layer:
        checks = [c for c in allc if c.get("status") == "draft" and not c["id"].startswith("REAL-")
                  and LAYERS[args.layer](c) and refs_of(c)]
        name = args.name or f"inbox-{args.layer}"
    else:
        ids = [i.strip() for i in args.ids.split(",") if i.strip()]
        by = {c["id"]: c for c in allc}
        missing = [i for i in ids if i not in by]
        if missing:
            raise SystemExit("ОШИБКА: нет записей " + ", ".join(missing))
        checks = [by[i] for i in ids]
        name = args.name or "custom"
    OUT.mkdir(parents=True, exist_ok=True)
    text = build(name, checks)
    path = OUT / f"{name}.md"
    path.write_text(text, encoding="utf-8")
    print(f"{path}: записей {len(checks)}, символов {len(text)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
