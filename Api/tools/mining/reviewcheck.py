#!/usr/bin/env python3
"""Cross-review pack for new ideas of a mining batch (step 7): a self-contained Markdown task for another LLM.

Usage (from Api/):
  reviewcheck.py --batch kubernetes            the task with Claude's proposals (the same input the human reviews)
  reviewcheck.py --batch kubernetes --blind    without Claude's decisions, IDs and files — an independent review

Writes ideas/mined/<batch>.reviewcheck.md: the task, the library principles, every cluster of `new` patterns with
the source text of its bugs, and the index of all library records (to spot duplicates). The model does the same
review as the human (decision, ID, file, overlap); its answer is saved next to it (<batch>.reviewcheck.answer-N.md)
and compared with the human decisions in <batch>.review.yaml.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from cluster import MINED, iter_checks, load_results, load_sources, load_yaml  # noqa: E402
from library import setup_console  # noqa: E402

README = Path("README.md")
MODEL = "Claude Opus 5.5 (`claude-opus-5-5`)"
BODY_LIMIT = 2500

TASK = """## Задание для модели

Ты — ревьюер библиотеки шаблонов API-тестов. Из реальных закрытых багов открытого проекта выделены паттерны,
для которых в библиотеке нет подходящей записи (`new`). Паттерны склеены в идеи (кластеры). Для каждой идеи реши,
становится ли она новой записью библиотеки. Суди по первоисточнику бага, а не по пересказу, и по индексу библиотеки
в конце файла.

Для каждой идеи ответь:

1. **Решение** — `accept` (новая запись) или `reject` (с причиной). Причины отказа, которые уже применялись:
   специфика конфигурации или внутренней логики одного продукта, не воспроизводимая тестом API другого продукта;
   идея уже покрыта существующей записью (назови её ID — тогда это пруф к ней, а не новая запись);
   слишком общая, чтобы стать шагом теста.
2. **Пересечение** — ID существующих записей, с которыми идея пересекается или дублирует их, и предложение:
   новая запись, шаг-вариант в существующей (`extends` к ID) или объединение с другой идеей этого списка.
3. **ID и файл** — подходят ли (ID: префикс файла, суть проверки, латиница и дефисы); если нет — твой вариант.
4. **Формулировка** — обобщена ли идея до проверки любого API (а не продукта из бага), верно ли направление
   (позитивная / негативная), нужны ли особые условия (инструменты, доступ к БД, к файлам стенда, две версии сервиса).
5. **Почему** — одна-две строки; при сомнении — цитата из бага.

Отдельно (после таблицы): идеи, которые стоит разбить на несколько записей или склеить, и паттерны, которые, по-твоему,
вообще не про API.
"""

ANSWER = """Формат ответа — одна таблица на все идеи:

| # | Решение | Пересечение (ID) и что сделать | ID и файл | Формулировка / условия | Почему |
|---|---|---|---|---|---|
| 1 | accept/reject | — / extends ID / объединить с №N | ok / свой вариант | ok / замечание | ... |

В конце — 2–3 строки общего вывода: систематические ошибки кластеризации, если есть.
"""


def principles() -> str:
    m = re.search(r"## Принципы\n(.*?)(?=\n## )", README.read_text(encoding="utf-8"), re.S)
    return m.group(1).strip() if m else ""


def build(batch: str, blind: bool) -> tuple[str, int]:
    review = load_yaml(MINED / f"{batch}.review.yaml")
    sources = load_sources(batch)
    results = {r["id"]: r for r in load_results(batch)}
    mode = ("без решений Claude — независимое ревью" if blind
            else f"с предложениями модели {MODEL} — то же, что видит человек на ревью")
    out = ["# Перекрёстное ревью новых идей выгрузки багов", "",
           f"Партия `{batch}`, идей: {len(review['clusters'])}; вариант пакета — {mode}.",
           "Этот файл целиком отдаётся другой LLM. Ответ модели вставить в чат внутренней сессии.", "",
           TASK, "Принципы библиотеки (из README):", "", principles(), "", ANSWER]
    for n, c in enumerate(review["clusters"], 1):
        out += [f"## Идея {n}. {c['idea']}", ""]
        if not blind:
            target = (f"`{c['check_id']}` в `{c['file']}`" if c["decision"] == "accept"
                      else f"причина: {c.get('reason') or '—'}")
            out += [f"- **Предложение Claude:** `{c['decision']}` — {target}", ""]
        for bug in c["bugs"]:
            src, r = sources[bug], results[bug]
            p = r["pattern"]
            body = re.sub(r"\n{3,}", "\n\n", (src.get("body") or "").strip())
            if len(body) > BODY_LIMIT:
                body = body[:BODY_LIMIT] + " …[обрезано]"
            out += [f"### {bug} — {src['title']}", "", f"Ссылка: {src['url']}", "",
                    f"- **Паттерн:** {p['title']}", f"- **Условие:** {p['condition']}",
                    f"- **Действие:** {p['action']}", f"- **Ожидание:** {p['expected']}",
                    f"- **Источник ожидания:** {p.get('expected_source') or '—'}",
                    f"- **Почему не подошла ближайшая запись:** {r['match'].get('note') or '—'}", "",
                    "Первоисточник:", "", "````text", body, "````", ""]
    n = len(review["clusters"])
    for t in (review.get("proofs") or {}).get("retarget") or []:
        n += 1
        src, r = sources[t["bug"]], results[t["bug"]]
        body = re.sub(r"\n{3,}", "\n\n", (src.get("body") or "").strip())[:BODY_LIMIT]
        out += [f"## Идея {n}. {r['pattern']['title']}", ""]
        if not blind:
            out += [f"- **Предложение Claude:** не новая запись, а шаг-вариант к `{t['check_id']}`: {t['variant']}", ""]
        out += [f"### {t['bug']} — {src['title']}", "", f"Ссылка: {src['url']}", "",
                f"- **Действие:** {r['pattern']['action']}", f"- **Ожидание:** {r['pattern']['expected']}", "",
                "Первоисточник:", "", "````text", body, "````", ""]
    index = sorted((c["id"], c.get("category", ""), c.get("title", "")) for _, c in iter_checks(Path("."), []))
    out += ["## Индекс библиотеки", "", f"Все записи ({len(index)}): ID | категория | заголовок.", "", "```text"]
    out += [" | ".join(row) for row in index]
    out += ["```"]
    return "\n".join(out) + "\n", n


def main() -> int:
    setup_console()
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--batch", required=True)
    ap.add_argument("--blind", action="store_true", help="не показывать решения, ID и файлы Claude")
    ap.add_argument("--out", help="файл пакета; по умолчанию ideas/mined/<batch>.reviewcheck[.blind].md")
    args = ap.parse_args()
    text, n = build(args.batch, args.blind)
    name = f"{args.batch}.reviewcheck{'.blind' if args.blind else ''}.md"
    path = Path(args.out) if args.out else MINED / name
    path.write_text(text, encoding="utf-8")
    print(f"{path}: идей {n}, символов {len(text)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
