#!/usr/bin/env python3
"""Cross-check pack for proofs (extends/covered) of a mining batch: a self-contained Markdown task for another LLM.

Usage (from Api/):
  proofcheck.py --batch ghsa-maven --checks HARD-EXPENSIVE-OPERATION-LIMITS,INJ-SSRF-PARAMETERS,REST-MASS-ASSIGNMENT

Writes ideas/mined/<batch>.proofcheck.md: the task, the matching rules from the triage prompt, each record (YAML) and
every bug of the batch matched to it with its source text. The file goes to 2–3 other models as is; their answers
are saved next to it (<batch>.proofcheck.answer-N.md), Claude's own verdict — <batch>.proofcheck.claude.yaml
(separately, so it does not bias the models). Changes are made only where both models object (decision of bj,
2026-10-16): wrong match -> proofs.exclude, unsupported variant -> proofs.no_variant in <batch>.review.yaml.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from cluster import MINED, iter_checks, load_results, load_sources  # noqa: E402
from library import setup_console  # noqa: E402

PROMPT = Path("mining/prompts/triage_abstract.md")
MODEL = "Claude Opus 5.5 (`claude-opus-5-5`)"
BODY_LIMIT = 2000
FIELDS = ("id", "title", "preconditions", "steps", "expected", "applicability")

TASK = """## Задание для модели

Ты проверяешь качество сопоставления реальных багов с записями библиотеки шаблонов API-тестов.
Для каждой записи ниже даны её текст (YAML) и список багов, которые другая модель к ней привязала, с первоисточником.
Для каждого бага ответь по первоисточнику, а не по пересказу:

1. **Привязка** — `ok` (запись проверяет именно тот механизм, что сломан в баге), `doubt` (близко, но спорно) или `wrong`
   (механизм другой; укажи, какая проверка подошла бы — словами или ID, если видишь подходящую среди записей ниже).
2. **Тип** — `covered` верно, только если существующие шаги записи уже ловят этот баг; иначе должен быть `extends`.
3. **Вариант** (для `extends`) — `ok` (новый, полезный и следует из бага), `dup` (уже есть в шагах записи),
   `invented` (деталей нет в баге — додумано), `vague` (слишком общий, нельзя выполнить как шаг теста).
4. **Почему** — одна строка, с цитатой из бага, если спорно.
"""

ANSWER = """Формат ответа — одна таблица на все записи:

| # | Баг | Привязка | Тип верен? | Вариант | Почему |
|---|---|---|---|---|---|
| P1 | GHSA-... | ok/doubt/wrong | да/нет | ok/dup/invented/vague/— | ... |

В конце — 2–3 строки общего вывода: систематические ошибки, если есть.
"""


def matching_rules() -> str:
    m = re.search(r"3\. \*\*Сопоставление\*\*.*?(?=\n4\. )", PROMPT.read_text(encoding="utf-8"), re.S)
    return m.group(0).strip() if m else ""


def build(batch: str, ids: list[str]) -> tuple[str, int]:
    sources = load_sources(batch)
    results = load_results(batch)
    checks = {c["id"]: c for _, c in iter_checks(Path("."), []) if c.get("id") in ids}
    missing = [i for i in ids if i not in checks]
    if missing:
        raise SystemExit("ОШИБКА: нет записей " + ", ".join(missing))
    out = ["# Перекрёстная проверка пруфов выгрузки багов", "",
           f"Партия `{batch}`, записей: {len(ids)}. Сопоставление сделала модель {MODEL}.",
           "Этот файл целиком отдаётся другой LLM. Ответ модели вставить в чат внутренней сессии.", "",
           TASK, "Правила, по которым делалось сопоставление (из промпта):", "", "```", matching_rules(), "```", "",
           ANSWER]
    n = 0
    for cid in ids:
        rec = {k: checks[cid][k] for k in FIELDS if k in checks[cid]}
        out += [f"## Запись {cid}", "", "```yaml",
                yaml.safe_dump(rec, allow_unicode=True, sort_keys=False, width=110).strip(), "```", ""]
        for r in results:
            if r["verdict"] != "api" or r["match"].get("check_id") != cid:
                continue
            n += 1
            src, m = sources[r["id"]], r["match"]
            body = re.sub(r"\n{3,}", "\n\n", (src.get("body") or "").strip())
            if len(body) > BODY_LIMIT:
                body = body[:BODY_LIMIT] + " …[обрезано]"
            out += [f"### P{n}. {r['id']} — {src['title']}", "", f"Ссылка: {src['url']}", "",
                    f"- **Решение модели:** `{m['type']}`", f"- **Заметка:** {m.get('note') or '—'}",
                    f"- **Вариант (новый шаг):** {m.get('variant') or '—'}",
                    f"- **Паттерн бага:** {r['pattern']['title']}", "", "Первоисточник:", "", "````text", body, "````", ""]
    return "\n".join(out) + "\n", n


def main() -> int:
    setup_console()
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--batch", required=True)
    ap.add_argument("--checks", required=True, help="ID записей через запятую (2–3 записи с разными механизмами)")
    ap.add_argument("--out", help="файл пакета; по умолчанию ideas/mined/<batch>.proofcheck.md")
    args = ap.parse_args()
    ids = [i.strip() for i in args.checks.split(",") if i.strip()]
    text, n = build(args.batch, ids)
    path = Path(args.out) if args.out else MINED / f"{args.batch}.proofcheck.md"
    path.write_text(text, encoding="utf-8")
    print(f"{path}: записей {len(ids)}, пруфов {n}, символов {len(text)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
