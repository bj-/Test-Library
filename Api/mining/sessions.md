# Масштабирование выгрузки багов: план и промпты сессий

_Составлено 2026-10-15 (bj, Claude). Решение о масштабировании — ADR [0005](../../docs/decisions/0005-bug-mining-pilot-go.md),
источники — `sources.yaml` (раздел «Масштабирование после пилота»), порядок шагов LLM — `README.md`._

## Условия на 2026-10-15 и 2026-10-16 (решение пользователя)

- Ограничения по недельному лимиту сняты: дневная норма из `budget.md` не действует, лимит можно израсходовать весь.
- Расход не считаем: при параллельных сессиях замеры `/usage` смешиваются. Строки в `budget.md` не пишем.
- Размер пачки — как раньше: до 80 багов, каждая пачка в свежей сессии.
- Сессии делятся так:
  - **одна внутренняя** — анализ, кластеры и ревью, вычитка draft, разбор inbox, git push;
  - **остальные — сессии сбора**: одна сессия работает только с одним источником.

## Как устроено

- **Партия = источник.** Данные источника лежат в `build/mining/<id>/`, пачки называются `b-01`, `b-02`, …
  `collect.py --batch <id>` собирает только этот источник.
- **Повторов нет.** `filter.py` отбрасывает баги, которые уже были в других партиях, в том числе в пилоте
  (причина «уже в другой партии»). Поэтому у keycloak, strapi и directus берётся только более старая история.
- **Нагрузка на серверы.** Почти все источники лежат на одном сервере — github.com (GHSA тоже), и токен у них общий.
  Поэтому пауза 1,5 с выдерживается между запросами **всех** процессов на машине вместе (`github_api.py`,
  файл `build/mining/.github-pace`). Для GitHub десять сессий сбора дают ту же нагрузку, что одна. Каждая из них
  при этом качает медленнее, но сбор — это минуты; основное время уходит на триаж, а он работает с диском, не с сетью.
- **Общая рабочая копия.** Все сессии работают в `C:\git\Test-Library`:
  - сессия сбора коммитит только файлы своей пачки (`commit_batch.py`, `git commit --only`) и делает одну попытку
    `push`;
  - `pull`, `stash`, `checkout` делает только внутренняя сессия.
- **Чего сессии сбора не трогают:** `docs/STATUS.md`, `budget.md`, `checks/`, `ideas/inbox.md`, промпт триажа.
  Идеи вне паттернов они записывают в `build/mining/<id>/ideas.md`, в inbox их переносит внутренняя сессия.

## Запуск

Одна команда — одна пачка: сессия обрабатывает её, коммитит и пишет, сколько багов осталось. Следующую пачку
лучше запускать в новой сессии, то есть той же командой ещё раз. В открытой сессии можно сделать `/clear` и
отправить тот же промпт. Скопировать и запустить в PowerShell:

```powershell
cd C:\git\Test-Library; claude -n "Выгрузка багов — <id>" --permission-mode auto "Выгрузка багов, источник <id>: обработай очередную пачку по Api/mining/sessions.md, раздел «Сессия сбора»."
```

Несколько источников сразу, по вкладке Windows Terminal на каждый:

```powershell
powershell -ExecutionPolicy Bypass -File C:\git\Test-Library\Api\mining\start-sessions.ps1 keycloak ghsa-pip ghsa-maven ghsa-go
powershell -ExecutionPolicy Bypass -File C:\git\Test-Library\Api\mining\start-sessions.ps1 -Internal
```

`-ExecutionPolicy Bypass` нужен потому, что на машине политика `Restricted` и `.ps1` напрямую не запускается.
Сессии открываются в режиме `auto` — как в текущей работе.

Отчёты: сессии сбора отчёты не пишут. Сводку по выгрузке за день делает внутренняя сессия в своём отчёте.

## Сессии сбора — список (по ожидаемой отдаче, сверху важнее)

Оценка: раз — сколько собрать; пачек — после фильтра. Для GHSA доля API в пилоте — 70–80 %, для продуктов — 30–50 %.

| # | Источник | Что | Собрать | Пачек ≈ | Промпт / команда |
|---|---|---|---|---|---|
| 1 | `keycloak` | история глубже пилота | 600 (−200 пилота) | 4–5 | `claude -n "Выгрузка багов — keycloak" --permission-mode auto "Выгрузка багов, источник keycloak: обработай очередную пачку по Api/mining/sessions.md, раздел «Сессия сбора»."` |
| 2 | `ghsa-pip` | GHSA, Python | 250 | 3 | `claude -n "Выгрузка багов — ghsa-pip" --permission-mode auto "Выгрузка багов, источник ghsa-pip: обработай очередную пачку по Api/mining/sessions.md, раздел «Сессия сбора»."` |
| 3 | `ghsa-maven` | GHSA, Java | 250 | 3 | `claude -n "Выгрузка багов — ghsa-maven" --permission-mode auto "Выгрузка багов, источник ghsa-maven: обработай очередную пачку по Api/mining/sessions.md, раздел «Сессия сбора»."` |
| 4 | `ghsa-go` | GHSA, Go | 250 | 3 | `claude -n "Выгрузка багов — ghsa-go" --permission-mode auto "Выгрузка багов, источник ghsa-go: обработай очередную пачку по Api/mining/sessions.md, раздел «Сессия сбора»."` |
| 5 | `directus` | история глубже пилота | 450 (−150) | 2–3 | `claude -n "Выгрузка багов — directus" --permission-mode auto "Выгрузка багов, источник directus: обработай очередную пачку по Api/mining/sessions.md, раздел «Сессия сбора»."` |
| 6 | `ghsa-composer` | GHSA, PHP | 200 | 2–3 | `claude -n "Выгрузка багов — ghsa-composer" --permission-mode auto "Выгрузка багов, источник ghsa-composer: обработай очередную пачку по Api/mining/sessions.md, раздел «Сессия сбора»."` |
| 7 | `ghsa-rubygems` | GHSA, Ruby | 200 | 2–3 | `claude -n "Выгрузка багов — ghsa-rubygems" --permission-mode auto "Выгрузка багов, источник ghsa-rubygems: обработай очередную пачку по Api/mining/sessions.md, раздел «Сессия сбора»."` |
| 8 | `ghsa-nuget` | GHSA, .NET | 150 | 2 | `claude -n "Выгрузка багов — ghsa-nuget" --permission-mode auto "Выгрузка багов, источник ghsa-nuget: обработай очередную пачку по Api/mining/sessions.md, раздел «Сессия сбора»."` |
| 9 | `kubernetes` | apiserver, api-machinery, auth | 200 | 2–3 | `claude -n "Выгрузка багов — kubernetes" --permission-mode auto "Выгрузка багов, источник kubernetes: обработай очередную пачку по Api/mining/sessions.md, раздел «Сессия сбора»."` |
| 10 | `hasura` | GraphQL Engine | 200 | 2 | `claude -n "Выгрузка багов — hasura" --permission-mode auto "Выгрузка багов, источник hasura: обработай очередную пачку по Api/mining/sessions.md, раздел «Сессия сбора»."` |
| 11 | `postgrest` | PostgREST (REST поверх PostgreSQL) | 150 | 2 | `claude -n "Выгрузка багов — postgrest" --permission-mode auto "Выгрузка багов, источник postgrest: обработай очередную пачку по Api/mining/sessions.md, раздел «Сессия сбора»."` |
| 12 | `strapi` | история глубже пилота | 450 (−150) | 1–2 | `claude -n "Выгрузка багов — strapi" --permission-mode auto "Выгрузка багов, источник strapi: обработай очередную пачку по Api/mining/sessions.md, раздел «Сессия сбора»."` |
| 13 | `supabase-auth` | Supabase Auth (GoTrue) | 120 | 1–2 | `claude -n "Выгрузка багов — supabase-auth" --permission-mode auto "Выгрузка багов, источник supabase-auth: обработай очередную пачку по Api/mining/sessions.md, раздел «Сессия сбора»."` |
| 14 | `kong` | API-шлюз | 150 | 2 | `claude -n "Выгрузка багов — kong" --permission-mode auto "Выгрузка багов, источник kong: обработай очередную пачку по Api/mining/sessions.md, раздел «Сессия сбора»."` |
| 15 | `apollo-server` | GraphQL | 120 | 1–2 | `claude -n "Выгрузка багов — apollo-server" --permission-mode auto "Выгрузка багов, источник apollo-server: обработай очередную пачку по Api/mining/sessions.md, раздел «Сессия сбора»."` |
| 16 | `graphql-js` | GraphQL | 100 | 1 | `claude -n "Выгрузка багов — graphql-js" --permission-mode auto "Выгрузка багов, источник graphql-js: обработай очередную пачку по Api/mining/sessions.md, раздел «Сессия сбора»."` |
| 17 | `grpc-go` | gRPC | 120 | 1–2 | `claude -n "Выгрузка багов — grpc-go" --permission-mode auto "Выгрузка багов, источник grpc-go: обработай очередную пачку по Api/mining/sessions.md, раздел «Сессия сбора»."` |
| 18 | `grpc-java` | gRPC | 120 | 1–2 | `claude -n "Выгрузка багов — grpc-java" --permission-mode auto "Выгрузка багов, источник grpc-java: обработай очередную пачку по Api/mining/sessions.md, раздел «Сессия сбора»."` |
| 19 | `grpc-node` | gRPC | 100 | 1 | `claude -n "Выгрузка багов — grpc-node" --permission-mode auto "Выгрузка багов, источник grpc-node: обработай очередную пачку по Api/mining/sessions.md, раздел «Сессия сбора»."` |
| 20 | `grpc-gateway` | gRPC ↔ REST | 100 | 1 | `claude -n "Выгрузка багов — grpc-gateway" --permission-mode auto "Выгрузка багов, источник grpc-gateway: обработай очередную пачку по Api/mining/sessions.md, раздел «Сессия сбора»."` |

Всего ≈ 4000 собранных → ≈ 2700 после фильтра → ≈ 35–40 пачек. По замерам пилота это ≈ 20–25 % недели.
Если лимит останется — ниже «Если останется лимит».

Перед каждой командой из таблицы — `cd C:\git\Test-Library;`.

Сколько сессий держать одновременно — решает человек. Удобно 4–6: каждая пачка занимает 15–30 минут,
и за выводом проще следить. Ограничений на одновременную работу источников нет.

## Сессия сбора — порядок для Claude

Источник `<id>` указан в промпте. Работа ведётся из `C:\git\Test-Library\Api`, с `PYTHONUTF8=1`.

1. **Не трогать git**, кроме шага 8: рабочая копия общая с другими сессиями, поэтому никаких `pull`, `stash`,
   `checkout`, `add .`. Не править `docs/STATUS.md`, `mining/budget.md`, `checks/`, `ideas/`,
   `mining/prompts/`, `mining/sources.yaml`. Если что-то из этого нужно поправить, написать человеку.
2. **Сбор, если его ещё не было.** В `build/mining/<id>/state.json` у источника нет `"done": true`, или нет
   `filtered.jsonl`, — выполнить по очереди, долгие команды в фоне:
   `python tools/mining/collect.py --batch <id>` → `python tools/mining/filter.py --batch <id>` →
   `python tools/mining/enrich.py --batch <id>`.
   - Код выхода 2 — остановка по лимиту GitHub: сказать человеку и закончить.
   - `collect.py` упал с «ни одна метка не подошла» — показать список меток человеку и закончить.
   - Вывод `filter.py` показать: сколько осталось и по каким причинам отброшено.
3. `python tools/mining/batch.py index` — справочник библиотеки: внутренняя сессия добавляет записи.
4. **Имя пачки** — следующее после последнего `build/mining/<id>/batches/b-NN.ids`; первая — `b-01`.
   Есть `b-NN.ids` без `b-NN.out.jsonl` — значит, прошлая сессия не закончила эту пачку: доделать её, `make` не
   запускать.
   Иначе `python tools/mining/batch.py make --batch <id> --name b-NN --n 80`. Если вышло 0 багов, источник исчерпан:
   сказать человеку и закончить.
5. **Триаж.** Прочитать `mining/prompts/triage_abstract.md`, `build/mining/library_index.txt`,
   `taxonomy/categories.yaml`, `taxonomy/tags.yaml` и файл пачки `build/mining/<id>/batches/b-NN.md`.
   - Файл пачки читать кусками по ~1300 строк. Ответы по каждому куску писать в отдельный файл в scratchpad,
     затем склеить в `batches/b-NN.out.jsonl`: UTF-8 без BOM, одна строка на баг, порядок как в пачке.
   - Идеи проверок, которые не вошли в паттерны, дописывать в `build/mining/<id>/ideas.md` с ID бага.
6. `python tools/mining/batch.py check --batch <id> --name b-NN` — должно быть N/N и 0 ошибок; ошибки исправить.
   Затем `python tools/mining/batch.py stats --batch <id>`.
7. Промпт не менять. Если триаж кажется неверным для целого класса багов, написать человеку.
8. `python tools/mining/commit_batch.py --batch <id> --name b-NN` — коммит только файлов пачки и попытка push.
9. **Итог одной строкой:** пачка, багов, API, new / extends / covered, сколько осталось. Затем либо
   «запусти ту же команду снова», либо «источник исчерпан».

Подводные камни Windows: в PowerShell `[IO.File]` берёт пути от каталога процесса — использовать только абсолютные
пути или Write; в heredoc обратные слэши портятся — `Path.as_posix()`.

## Внутренняя сессия

Промпт:

```powershell
cd C:\git\Test-Library; claude -n "Выгрузка багов — внутренняя" --permission-mode auto "Внутренняя сессия выгрузки багов: работай по Api/mining/sessions.md, раздел «Внутренняя сессия». Начни с пункта 1."
```

Задачи по порядку важности. Каждый пункт можно давать отдельной командой («сделай пункт 3»).

1. **Синхронизация.** `git pull --rebase --autostash` и `git push`: коммиты сессий сбора, которые не ушли сразу.
   Сводка по источникам — `batch.py stats --batch <id>` по каждому `build/mining/*/`, итог — строка «В работе»
   в `docs/STATUS.md` и запись в журнал. Повторять между остальными задачами, примерно раз в час.
2. **Точность пилота.** Когда человек скажет «разметку закончил», выполнить `accuracy.py score`. Итог записать
   в `REPORT.md`, в `STATUS.md` и в ADR 0005, идеи из комментариев перенести в inbox.
   - Есть раздел ниже 85 % — сообщить человеку до шагов 6–7 по новым источникам. Возможно, понадобится правка
     промпта и повторный триаж части пачек.
   - Промпт триажа меняется только при остановленных сессиях сбора.
3. **Шаги 6–7 по готовым источникам.** Источник готов, когда все пачки обработаны.
   - Сначала собрать идеи из `build/mining/<id>/ideas.md` в inbox.
   - Затем кластеры: `ideas/mined/<id>.review.yaml` → `cluster.py --batch <id>` → `ideas/mined/<id>.md`.
   - Ревью решений делает человек (ADR 0005, п. 5) — показать ему таблицу и дождаться ответа.
   - Затем записи draft, `apply_proofs.py --batch <id>`, `validate_library.py`, `build_catalog.py`.
   - Порядок: сначала источники с наибольшим числом `new`. Шаги 6–7 начинать только после пункта 2 —
     или раньше, если человек решит.
4. **Вычитка 50 draft-записей пилота:** перевести в `approved` или `needs_clarification`, переписать около 70
   шагов-вариантов, начинающихся с «Добавить …». Решения по спорным записям — человеку.
5. **Разбор `ideas/inbox.md`** (сейчас 46 идей): каждая идея — в `checks/` как draft или отказ с причиной.
6. **Метрики** по источникам — `evaluate.py --batch <id>`, раздел в `build/mining/<id>/REPORT.md`, итог по всем
   источникам — в `STATUS.md`: какие источники стоит копать дальше.
7. **Новые типы источников** (сборщика пока нет): GitLab (gitlab.com, issues GitLab CE), Jira (Apache:
   Kafka REST, Camel, CXF). Сначала план, затем `collect.py`.
8. **Дневной отчёт** — по команде человека: что собрано и обработано за день во всех сессиях.

## Если останется лимит

- NestJS и Express — только докачка новых закрытых багов (ADR 0005, п. 3); нужен режим «с даты» в `collect.py`.
- GHSA: `rust`, `pub`, `erlang`; GHSA npm — дальше пилота (`max_items` 200 → 500).
- Продукты-API: Supabase Storage, Ory Kratos и Hydra, Gitea (REST API), Mattermost (REST API).
- Если источник покажет высокую отдачу (идей на 100 собранных больше 6), стоит копать его глубже: увеличить
  `max_items` и обработать ещё пачки.
