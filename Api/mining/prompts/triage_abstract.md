# Промпт: триаж, абстракция и сопоставление (шаги 3–5 за один проход)

Выполняет Claude Code над файлом партии `build/mining/<batch>/batches/<name>.md`. Справочники:
`build/mining/library_index.txt` (существующие записи библиотеки) и `taxonomy/` (категории и метки).
Результат — `build/mining/<batch>/batches/<name>.out.jsonl`, одна строка JSON на каждый баг партии,
проверка — `python tools/mining/batch.py check --name <name>`.

## Задача по каждому багу

1. **Триаж.** Это дефект поведения, который можно обнаружить black-box запросами к API (REST, gRPC, GraphQL,
   WebSocket) или по ответу сервера? Если нет — `verdict: out_of_scope` и класс:
   `build` (сборка, зависимости, типы, упаковка), `ui` (интерфейс, вёрстка), `memory` (утечки, рост ресурсов),
   `perf-internal` (деградация без внешнего проявления в одном запросе), `docs` (документация, сайт),
   `other` (внутренняя логика, CLI, миграции, не баг, мало данных). Плюс `reason` — одна фраза.
2. **Абстракция** (только для `api`). Паттерн без привязки к продукту, по-русски:
   - `title` — суть в одной строке, как заголовок проверки;
   - `condition` — при каком условии/данных проявляется;
   - `action` — что сделать в тесте (запрос, последовательность);
   - `expected` — что должно быть; `actual` — что ломалось в реальном баге;
   - `protocol` — список из `rest`, `grpc`, `graphql`, `websocket`, `generic`;
   - `category` — одна из `taxonomy/categories.yaml`; `tags` — из группы `domain`/`quality` `taxonomy/tags.yaml`;
   - `owasp` — категория OWASP API Security Top 10:2023 (`API1`…`API10`) или `null`; `cwe` — список номеров;
   - `expected_source` — откуда ожидание: RFC/стандарт с номером, OWASP, практика, здравый смысл.
   Ожидание не додумывать сверх бага и источника. Мало данных — `verdict: out_of_scope`, класс `other`.
3. **Сопоставление** (только для `api`) с `library_index.txt`:
   - `covered` — существующая запись проверяет ровно это; `check_id` — её ID;
   - `extends` — запись есть, но баг показывает неучтённый вариант; `check_id` и `note` — какой вариант добавить;
   - `new` — подходящей записи нет; `check_id: null`, `note` — почему не подходит ближайшая.

## Формат строки

```json
{"id": "owner/repo#123", "verdict": "api", "oos_class": null, "reason": "…",
 "pattern": {"title": "…", "condition": "…", "action": "…", "expected": "…", "actual": "…",
             "protocol": ["rest"], "category": "validation", "tags": ["validation"],
             "owasp": null, "cwe": [], "expected_source": "RFC 9110 §8.3"},
 "match": {"type": "new", "check_id": null, "note": "…"}}
```

Для `out_of_scope`: `pattern` и `match` — `null`.
