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

## Масштабирование: параллельные сессии

После пилота партия равна источнику: данные лежат в `build/mining/<id>/`, пачки называются `b-NN`, одна сессия
Claude работает с одним источником. План, список промптов и запуск — [`sessions.md`](sessions.md). Отличия от
пилота:

- `collect.py --batch <id>` собирает только этот источник;
- `filter.py` отбрасывает баги других партий;
- пауза между запросами к GitHub общая для всех процессов на машине;
- коммит пачки — `commit_batch.py`, только её файлы.

Раздел ниже — порядок пилота (`--batch pilot`, пачки `p-NN`).

## Очередная LLM-партия (шаги 3–5) — порядок для Claude

Запускать в свежей сессии из `C:\Git\Test-Library` (расход растёт с длиной разговора). Человек присылает `/usage`
до начала и после конца партии.

1. `git pull --rebase`; прочитать `docs/STATUS.md` и `Api/mining/budget.md`.
2. **Размер партии.** Норма — до 500 багов в день на все машины (`budget.md`, «Текущая норма»). Сложить «Багов»
   по строкам с сегодняшней датой; остаток = 500 − сумма. Ноль или меньше — партию не начинать, сказать человеку.
   Одна партия — не больше 80 багов (остаток меньше — весь остаток): длинная сессия дороже на баг, поэтому за день —
   несколько партий, каждая в свежей сессии.
   Нет `/usage` «до» — попросить его до начала работы.
3. **Имя** — следующее после последнего `build/mining/pilot/batches/p-NN.ids` (`p-02` → `p-03`).
4. Из `Api/`, с `PYTHONUTF8=1`: `python tools/mining/batch.py make --name p-NN --n <размер>`.
   Нет `build/mining/pilot/filtered.jsonl` — сначала `collect.py`, `filter.py`, `enrich.py` (раздел «Запуск»);
   нет `build/mining/library_index.txt` — `batch.py index`.
5. Прочитать `mining/prompts/triage_abstract.md`, `build/mining/library_index.txt`, `taxonomy/categories.yaml`,
   `taxonomy/tags.yaml` и файл партии `build/mining/pilot/batches/p-NN.md`. Файл большой (80 багов ≈ 5000 строк) —
   читать кусками по ~1300 строк, ответы по каждому куску писать в отдельный файл в scratchpad, затем склеить в
   `batches/p-NN.out.jsonl` (UTF-8 без BOM, одна строка на баг, порядок как в партии).
6. `batch.py check --name p-NN` (должно быть N/N, ошибок 0), показать `batch.py stats`.
7. `budget.md` — строка партии: дата, машина, `p-NN`, багов, «неделя до»; «после» и расход — по `/usage` после.
   `docs/STATUS.md` — строка «В работе» (обработано X/696, итоги new/extends/covered) и запись в журнале.
8. Коммит: `batches/p-NN.ids`, `batches/p-NN.out.jsonl`, `budget.md`, `docs/STATUS.md`; `git push` — без отдельного
   подтверждения (решение пользователя, 2026-10-13). Остальное из `build/mining/` в git не попадает.

Подводные камни (Windows): в PowerShell `[IO.File]` берёт пути от каталога процесса, а не от `cd` — только
абсолютные пути или Edit/Write; `git push` может вернуть код 255 при успехе — проверять `git rev-parse HEAD origin/main`.

## Кластеры и ревью (шаги 6–7)

1. **Кластеризация (Claude).** `new`-паттерны склеиваются в идеи в `ideas/mined/<batch>.review.yaml`: ключ,
   баги, идея, предложение `accept` (ID и файл новой записи) или `reject` (причина).
2. `python tools/mining/cluster.py --batch <batch>` — проверка review-файла (каждый `new` ровно в одном кластере,
   ID не занят) и сборка `ideas/mined/<batch>.md`: новые идеи и «Пруфы к существующим» с номерами `RWB-*`.
3. **Ревью (человек)** по `<batch>.md`; правки — в review-файле: `decision`, `check_id`, `file` кластера,
   неверное совпадение пруфа — ID бага в `proofs.exclude`, вариант без нового шага — в `proofs.no_variant`.
   Затем снова `cluster.py`.
4. `python tools/mining/apply_proofs.py --batch <batch> --dry-run`, затем без `--dry-run`: записи с пруфами
   получают метку `real-world-bug`, `Real-world bug: RWB-NNNN` и шаги-варианты (`extends`), трассировка —
   в `traceability/real-world-bugs.yaml`. Записи принятых кластеров пишет Claude (`status: draft`) до запуска;
   без них — `--proofs-only`. Повторный запуск безопасен.
5. `validate_library.py`, `build_catalog.py`.
6. **Перекрёстная проверка пруфов** (по решению человека; он пруфы сам не проверяет): `python tools/mining/proofcheck.py
   --batch <batch> --checks A,B,C` — пакет `ideas/mined/<batch>.proofcheck.md` для 2–3 других LLM; вердикт Claude —
   отдельно в `<batch>.proofcheck.claude.yaml`, ответы моделей — `<batch>.proofcheck.answer-N.md`. Правка — только
   там, где замечание у обеих моделей (`proofs.exclude`, `proofs.no_variant`), до `apply_proofs.py`. Образец — ghsa-maven.

## Бережная нагрузка на источники

Параметры — `politeness` в `sources.yaml`:

- запросы только последовательные, пауза между ними не меньше `min_interval_s`;
- последние 20 % лимита GitHub не расходуются: сборщик ждёт сброса, а если ждать дольше `max_wait_s` — останавливается;
- `Retry-After` и сброс лимита соблюдаются; вторичный лимит (403/429) и 5xx — нарастающая пауза и повтор;
- ничего не скачивается повторно: кэш и курсоры по каждому источнику;
- `User-Agent` указывает на проект;
- тексты issue в git не попадают: `build/mining/` в `.gitignore`, кроме `REPORT.md` партии.
