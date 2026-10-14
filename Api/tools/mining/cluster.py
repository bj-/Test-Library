#!/usr/bin/env python3
"""Candidates of a mining batch for human review (step 6-7): ideas/mined/<batch>.review.yaml + results -> <batch>.md.

Usage (from Api/):
  cluster.py --batch pilot          check the review file against batch results, render ideas/mined/pilot.md

The review file holds the clustering of `new` patterns (written by Claude, step 6) and the human decisions
(step 7). Proofs to existing checks (`extends`/`covered`) are taken from build/mining/<batch>/batches/*.out.jsonl.
RWB IDs are assigned here deterministically; apply_proofs.py writes them to checks/ and traceability/.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from library import iter_checks, load_yaml, setup_console  # noqa: E402

MINING = Path("build/mining")
MINED = Path("ideas/mined")
TRACE_FILE = Path("traceability/real-world-bugs.yaml")
DECISIONS = {"accept", "reject", "pending"}
PRODUCTS = {
    "nestjs-nest": "NestJS", "express": "Express", "express-session": "express-session",
    "body-parser": "body-parser", "jshttp-cookie": "cookie", "keycloak": "Keycloak", "strapi": "Strapi",
    "directus": "Directus",
}
# Variant prefixes written by the matching step; the rest of the note becomes a test step.
VARIANT_PREFIX = re.compile(r"^(Добавить( вариант| вектор)?|Обратный вариант|Вариант( транспорта| с редиректом)?)\s*:\s*",
                            re.I)
NO_VARIANT = re.compile(r"^(Тот же|Ровно)", re.I)


def load_results(batch: str) -> list[dict]:
    base = MINING / batch / "batches"
    return [json.loads(line) for f in sorted(base.glob("*.out.jsonl"))
            for line in f.open(encoding="utf-8") if line.strip()]


def load_sources(batch: str) -> dict[str, dict]:
    return {r["id"]: r for r in map(json.loads, (MINING / batch / "filtered.jsonl").open(encoding="utf-8"))}


def variant_text(note: str) -> str | None:
    note = (note or "").strip()
    if not note or NO_VARIANT.match(note):
        return None
    text = VARIANT_PREFIX.sub("", note, count=1).strip()
    if text and "а" <= text[0] <= "я":  # Latin starts (data:, __proto__, glob) stay as is
        text = text[0].upper() + text[1:]
    return text or None


def bug_info(bug_id: str, src: dict, result: dict) -> dict:
    fix = (src.get("fix") or {})
    product = PRODUCTS.get(src["source"]) or ", ".join(src.get("packages") or []) or src["source"]
    info = {"url": src["url"]}
    if fix.get("prs") or fix.get("commits"):
        info["fix"] = (fix.get("prs") or fix.get("commits"))[0]
    info |= {"product": product, "closed": (src.get("closed") or "")[:10], "summary": result["reason"]}
    return info


def build_plan(batch: str, errors: list[str], drafts_written: bool = False) -> dict:
    """Clusters and proofs with RWB IDs. Existing RWB of a check (earlier batch) is reused.

    drafts_written: records of accepted clusters are already in checks/ (apply_proofs.py).
    """
    review = load_yaml(MINED / f"{batch}.review.yaml")
    results = {r["id"]: r for r in load_results(batch) if r["verdict"] == "api"}
    sources = load_sources(batch)
    checks = {c["id"]: c for _, c in iter_checks(Path("."), [])}
    trace = load_yaml(TRACE_FILE) if TRACE_FILE.exists() else {}
    by_check = {cid: rwb for rwb, e in trace.items() for cid in e.get("checks", [])}
    next_no = max([int(k.split("-")[1]) for k in trace] + [0]) + 1
    exclude = set((review.get("proofs") or {}).get("exclude") or [])
    no_variant = set((review.get("proofs") or {}).get("no_variant") or [])

    def rwb_for(check_id: str) -> str:
        nonlocal next_no
        if check_id not in by_check:
            by_check[check_id] = f"RWB-{next_no:04d}"
            next_no += 1
        return by_check[check_id]

    clusters, seen = [], set()
    for c in review.get("clusters") or []:
        key = c.get("key")
        if c.get("decision") not in DECISIONS:
            errors.append(f"кластер {key}: decision должен быть одним из {sorted(DECISIONS)}")
        for b in c.get("bugs") or []:
            if b not in results or results[b]["match"]["type"] != "new":
                errors.append(f"кластер {key}: {b} не new-паттерн партии")
            if b in seen:
                errors.append(f"кластер {key}: {b} уже в другом кластере")
            seen.add(b)
        if c.get("decision") == "accept":
            cid = c.get("check_id") or ""
            c = dict(c, rwb=rwb_for(cid))
            applied = f"Real-world bug: {c['rwb']}" in (checks.get(cid, {}).get("references") or [])
            if cid in checks and not (drafts_written or applied):
                errors.append(f"кластер {key}: {cid} уже есть в библиотеке — для дополнения это extends")
            if not c.get("file", "").startswith("checks/"):
                errors.append(f"кластер {key}: file должен быть в checks/")
        elif c.get("decision") == "reject" and not c.get("reason"):
            errors.append(f"кластер {key}: у reject нужна причина")
        clusters.append(c)
    for b in sorted(set(r for r, v in results.items() if v["match"]["type"] == "new") - seen):
        errors.append(f"new-паттерн {b} не попал ни в один кластер")

    proofs = defaultdict(list)
    for bug_id, r in results.items():
        m = r["match"]
        if m["type"] == "new" or bug_id in exclude:
            continue
        if m["check_id"] not in checks:
            errors.append(f"{bug_id}: запись {m['check_id']} не найдена в библиотеке")
            continue
        if m["type"] != "extends" or bug_id in no_variant:
            variant = None
        elif "variant" in m:  # prompt with a separate step field (after the pilot)
            variant = m["variant"]
        else:  # pilot: the step is cut out of the note
            variant = variant_text(m.get("note"))
        proofs[m["check_id"]].append({"bug": bug_id, "type": m["type"], "note": m.get("note") or "",
                                      "variant": variant})
    proofs = {cid: {"rwb": rwb_for(cid), "title": checks[cid]["title"], "items": items}
              for cid, items in sorted(proofs.items())}
    bugs = {b: bug_info(b, sources[b], results[b]) for b in results}
    return {"batch": batch, "clusters": clusters, "proofs": proofs, "bugs": bugs, "results": results,
            "trace": trace}


def link(bug_id: str, bugs: dict) -> str:
    return f"[{bug_id}]({bugs[bug_id]['url']})"


def render(plan: dict) -> str:
    bugs, clusters, proofs = plan["bugs"], plan["clusters"], plan["proofs"]
    accepted = [c for c in clusters if c["decision"] == "accept"]
    rejected = [c for c in clusters if c["decision"] == "reject"]
    n_items = sum(len(p["items"]) for p in proofs.values())
    n_var = sum(1 for p in proofs.values() for i in p["items"] if i["variant"])
    out = [
        f"# Кандидаты из баг-трекеров: партия `{plan['batch']}`",
        "",
        "Сгенерировано `tools/mining/cluster.py` из `build/mining/<batch>/batches/*.out.jsonl` и",
        f"`ideas/mined/{plan['batch']}.review.yaml` — правки решений делаются в review-файле, затем пересборка.",
        "План — `docs/BUG_MINING_PLAN.md`, шаги 6–7; применение — `tools/mining/apply_proofs.py`.",
        "",
        "## Сводка",
        "",
        f"- Новых паттернов: {sum(len(c['bugs']) for c in clusters)} → идей: {len(clusters)} "
        f"(принять: {len(accepted)}, отклонить: {len(rejected)}, "
        f"не решено: {len(clusters) - len(accepted) - len(rejected)}).",
        f"- Пруфы к существующим: {n_items} багов → {len(proofs)} записей; новых шагов-вариантов: {n_var}.",
        "",
        "## Новые идеи",
        "",
        "Принятые становятся записями `status: draft` с меткой `real-world-bug` и ссылкой на RWB.",
        "",
        "| # | Решение | Запись / файл | Идея | Подтверждающие баги |",
        "|---|---|---|---|---|",
    ]
    for i, c in enumerate(clusters, 1):
        refs = ", ".join(link(b, bugs) for b in c["bugs"])
        if c["decision"] == "accept":
            where = f"`{c['check_id']}` ({c['rwb']})<br>`{c['file']}`"
        elif c["decision"] == "reject":
            where = f"отклонено: {c['reason']}"
        else:
            where = "не решено"
        out.append(f"| {i} | {c['decision']} | {where} | {c['idea']} | {refs} |")
    out += [
        "",
        "## Пруфы к существующим",
        "",
        "Запись получает метку `real-world-bug` и `Real-world bug: RWB-NNNN`; статус не меняется. Для `extends`",
        "текст варианта добавляется шагом (`steps[].action`, в `notes` — RWB). Неверное совпадение — ID бага в",
        "`proofs.exclude`, вариант без нового шага — в `proofs.no_variant`.",
        "",
    ]
    for cid, p in proofs.items():
        out += [f"### {cid} — {p['title']} ({p['rwb']}, багов: {len(p['items'])})", "",
                "| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |", "|---|---|---|"]
        for it in p["items"]:
            text = it["variant"] or (f"_только пруф_: {it['note']}" if it["note"] else "_только пруф_")
            out.append(f"| {link(it['bug'], bugs)} | {it['type']} | {text.replace('|', '/')} |")
        out.append("")
    return "\n".join(out)


def main() -> int:
    setup_console()
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--batch", default="pilot")
    args = ap.parse_args()
    errors: list[str] = []
    plan = build_plan(args.batch, errors)
    for e in errors:
        print("ОШИБКА:", e)
    if errors:
        return 1
    path = MINED / f"{args.batch}.md"
    path.write_text(render(plan) + "\n", encoding="utf-8")
    accepted = sum(1 for c in plan["clusters"] if c["decision"] == "accept")
    print(f"кластеров {len(plan['clusters'])} (принять {accepted}), записей с пруфами {len(plan['proofs'])} -> {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
