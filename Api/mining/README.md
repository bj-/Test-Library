# Выгрузка багов из открытых трекеров

План — `docs/BUG_MINING_PLAN.md`, решение — ADR 0004 (`../docs/decisions/0004-bug-tracker-mining.md`).

## Подготовка

Нужен токен GitHub (только чтение публичных данных): `gh auth login` или переменная `GITHUB_TOKEN`
(fine-grained токен без доступа к репозиториям — достаточно публичного чтения). Токен в git не попадает.

## Запуск (из `Api/`)

В Git Bash кириллица в выводе может отображаться как `\u...` — задайте `PYTHONUTF8=1`.

```bash
python tools/mining/collect.py --batch pilot              # шаг 1: сбор в build/mining/pilot/raw/
python tools/mining/collect.py --batch pilot --source keycloak   # только один источник
python tools/mining/filter.py  --batch pilot              # шаг 2: фильтр -> filtered.jsonl
python tools/mining/enrich.py  --batch pilot              # шаг 2b: тесты из фикс-PR
```

Все шаги возобновляемы: прерванный запуск продолжается с места остановки (`state.json`, `pr_tests.json`).
Код выхода 2 — остановка по лимиту API, запустить позже.

## Бережная нагрузка на источники

Параметры — `politeness` в `sources.yaml`:

- запросы только последовательные, пауза между ними не меньше `min_interval_s`;
- последние 20 % лимита GitHub не расходуются: сборщик ждёт сброса, а если ждать дольше `max_wait_s` — останавливается;
- `Retry-After` и сброс лимита соблюдаются; вторичный лимит (403/429) и 5xx — нарастающая пауза и повтор;
- ничего не скачивается повторно: кэш и курсоры по каждому источнику;
- `User-Agent` указывает на проект;
- тексты issue в git не попадают: `build/mining/` в `.gitignore`, кроме `REPORT.md` партии.
