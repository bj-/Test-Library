# Кандидаты из баг-трекеров: партия `hasura`

Сгенерировано `tools/mining/cluster.py` из `build/mining/<batch>/batches/*.out.jsonl` и
`ideas/mined/hasura.review.yaml` — правки решений делаются в review-файле, затем пересборка.
План — `docs/BUG_MINING_PLAN.md`, шаги 6–7; применение — `tools/mining/apply_proofs.py`.

## Сводка

- Новых паттернов: 16 → идей: 12 (принять: 10, отклонить: 2, не решено: 0).
- Пруфы к существующим: 12 багов → 9 записей; новых шагов-вариантов: 9.

## Новые идеи

Принятые становятся записями `status: draft` с меткой `real-world-bug` и ссылкой на RWB.

| # | Решение | Запись / файл | Идея | Подтверждающие баги |
|---|---|---|---|---|
| 1 | accept | `AUTH-JWT-VALID-ACCEPTED` (RWB-0206)<br>`checks/security/authentication-session.yaml` | Валидный токен принимается — подпись каждым поддерживаемым алгоритмом (включая EdDSA), JWKS с ключами неизвестного use рядом с ключом подписи, claims по настроенному пути (claims map) и значения по умолчанию; позитивная пара к AUTH-JWT-* и SEC-TOKEN-SIGNATURE | [hasura/graphql-engine#10774](https://github.com/hasura/graphql-engine/issues/10774), [hasura/graphql-engine#10733](https://github.com/hasura/graphql-engine/issues/10733), [hasura/graphql-engine#10243](https://github.com/hasura/graphql-engine/issues/10243) |
| 2 | accept | `GQL-REST-ENDPOINT-PARITY` (RWB-0207)<br>`checks/graphql/graphql.yaml` | Операция, опубликованная как REST-эндпоинт поверх GraphQL, выполняется так же, как исходный GraphQL-запрос — результат, побочные эффекты и контекст внешнего хука аутентификации (заголовки и тело) | [hasura/graphql-engine#10799](https://github.com/hasura/graphql-engine/issues/10799), [hasura/graphql-engine#10512](https://github.com/hasura/graphql-engine/issues/10512) |
| 3 | accept | `OBS-TELEMETRY-FORMAT` (RWB-0208)<br>`checks/common/observability.yaml` | Экспортируемая телеметрия (спаны, журналы OTLP) соответствует документированной структуре и семантическим соглашениям OpenTelemetry (span.kind CLIENT для обращений к БД и сервисам, поля записи журнала в body); нужен доступ к тестовому коллектору | [hasura/graphql-engine#10868](https://github.com/hasura/graphql-engine/issues/10868), [hasura/graphql-engine#10472](https://github.com/hasura/graphql-engine/issues/10472) |
| 4 | accept | `WS-SLOW-CONSUMER-NO-SILENT-LOSS` (RWB-0209)<br>`checks/websocket/websocket.yaml` | Медленный клиент подписки не теряет сообщения молча — при переполнении очереди отправки он получает все записи или явный сигнал о потере | [hasura/graphql-engine#10860](https://github.com/hasura/graphql-engine/issues/10860) |
| 5 | accept | `SEC-AUTHZ-RULE-READ-WRITE-PARITY` (RWB-0210)<br>`checks/security/access-control/SEC-AUTHZ-RULE-READ-WRITE-PARITY.yaml` | Условие прав по связанной записи (в том числе по вычисляемому полю) действует во вставке, изменении и удалении так же, как в чтении | [hasura/graphql-engine#10762](https://github.com/hasura/graphql-engine/issues/10762) |
| 6 | accept | `GQL-GATEWAY-ROUTING` (RWB-0211)<br>`checks/graphql/graphql.yaml` | В объединённой схеме нескольких источников (remote schemas, федерация) каждое поле направляется в свой upstream, даже если типы источников совпадают и различаются только префиксом | [hasura/graphql-engine#10717](https://github.com/hasura/graphql-engine/issues/10717) |
| 7 | accept | `REST-FILTER-RELATION-NO-DUPLICATES` (RWB-0212)<br>`checks/rest/pagination.yaml` | Фильтр по полю связанной коллекции (один-ко-многим, в том числе внутри _or/_and) возвращает каждую подходящую запись ровно один раз | [hasura/graphql-engine#10238](https://github.com/hasura/graphql-engine/issues/10238) |
| 8 | accept | `PAGE-SORT-MULTI-KEY-PRIORITY` (RWB-0213)<br>`checks/rest/pagination-extra.yaml` | Сортировка по нескольким ключам применяется в заданном клиентом порядке приоритета; смена порядка ключей меняет порядок результатов | [hasura/graphql-engine#10093](https://github.com/hasura/graphql-engine/issues/10093) |
| 9 | accept | `RES-CACHE-EXPLICIT-INVALIDATION` (RWB-0214)<br>`checks/common/resource-lifecycle.yaml` | Явный сброс кэша через API удаляет закэшированные ответы и сообщает их фактическое число; следующий запрос возвращает свежие данные | [hasura/graphql-engine#10055](https://github.com/hasura/graphql-engine/issues/10055) |
| 10 | accept | `RES-DB-OBJECT-NAMES` (RWB-0215)<br>`checks/common/resource-lifecycle.yaml` | API, построенный по схеме БД, читает и пишет объекты с именами в верхнем регистре, со спецсимволами и совпадающими со встроенными типами (таблицы, столбцы, пользовательские типы) | [hasura/graphql-engine#10314](https://github.com/hasura/graphql-engine/issues/10314) |
| 11 | reject | отклонено: Специфика конфигурации прав Hasura (несколько источников в метаданных); общая часть — задокументированная конфигурация прав работает — в SEC-AUTHZ-ROLE-POSITIVE-MATRIX | Правило доступа с условием по таблице другого источника принимается и применяется | [hasura/graphql-engine#10457](https://github.com/hasura/graphql-engine/issues/10457) |
| 12 | reject | отклонено: Внутренняя логика склейки схем Hasura (разбор defaultValue introspection при настройке ролей); тестом API продукта не воспроизводится без этой конфигурации | Значения по умолчанию входных полей из introspection удалённой схемы разбираются по типу поля | [hasura/graphql-engine#10759](https://github.com/hasura/graphql-engine/issues/10759) |

## Пруфы к существующим

Запись получает метку `real-world-bug` и `Real-world bug: RWB-NNNN`; статус не меняется. Для `extends`
текст варианта добавляется шагом (`steps[].action`, в `notes` — RWB). Неверное совпадение — ID бага в
`proofs.exclude`, вариант без нового шага — в `proofs.no_variant`.

### COMPAT-BREAKING-CHANGE-DIFF — Изменения контракта проверяются на обратную несовместимость (RWB-0216, багов: 2)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [hasura/graphql-engine#10867](https://github.com/hasura/graphql-engine/issues/10867) | extends | Обновить сервер до новой версии с неизменной конфигурацией и проверить, что он стартует без ошибок согласованности конфигурации |
| [hasura/graphql-engine#10864](https://github.com/hasura/graphql-engine/issues/10864) | extends | Снять схему API до и после обновления сервера при неизменной конфигурации и сравнить имена типов на несовместимые изменения |

### COMPAT-IMPLEMENTATION-MATCHES-CONTRACT — Реализация соответствует опубликованному контракту (RWB-0067, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [hasura/graphql-engine#10707](https://github.com/hasura/graphql-engine/issues/10707) | extends | Для каждого задокументированного флага запроса выполнить пример из документации с флагом и без него и проверить заявленное различие поведения |

### CONTRACT-PUBLISHED-SCHEMA-VALID — Опубликованные сервисом описания API валидны в заявленном диалекте (RWB-0049, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [hasura/graphql-engine#10560](https://github.com/hasura/graphql-engine/issues/10560) | extends | Выполнить полный запрос introspection и проверить ответ на соответствие мета-схеме GraphQL, включая non-null поля вроде isRepeatable |

### ERR-STATUS-MATCHES-EFFECT — Код ответа соответствует фактическому результату операции (RWB-0045, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [hasura/graphql-engine#10662](https://github.com/hasura/graphql-engine/issues/10662) | extends | Отправить изменение конфигурации при открытых WebSocket-подписках и сверить код ответа с фактически применённым изменением |

### GQL-FIELD-LEVEL-AUTHZ — Авторизация применяется на уровне полей и вложенных резолверов (RWB-0194, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [hasura/graphql-engine#10711](https://github.com/hasura/graphql-engine/issues/10711) | extends | Повторить проверку полевых и строковых ограничений для роли, которая наследует составную роль |

### OBS-HEALTH-ENDPOINTS — Health-эндпоинты отражают состояние и не раскрывают детали (RWB-0093, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [hasura/graphql-engine#10721](https://github.com/hasura/graphql-engine/issues/10721) | extends | Замерить время ответа liveness-эндпоинта под нагрузкой и во время перестроения конфигурации; ответ не должен зависеть от долгих проверок |

### RES-EXPORT-IMPORT-ROUNDTRIP — Данные, выгруженные API, принимаются им же обратно без изменений (RWB-0029, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [hasura/graphql-engine#10324](https://github.com/hasura/graphql-engine/issues/10324) | covered | _только пруф_: Ровно проверка «выгруженное принимается обратно без изменений» |

### REST-EMPTY-VALUES — Пустые объект, массив и строка (RWB-0115, багов: 3)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [hasura/graphql-engine#10322](https://github.com/hasura/graphql-engine/issues/10322) | extends | Отправить пустой массив в списковом аргументе пакетной операции и проверить, что ответ — пустой список объявленного типа |
| [hasura/graphql-engine#10239](https://github.com/hasura/graphql-engine/issues/10239) | extends | _только пруф_: Тот же вариант, что у hasura#10322 (пачка b-01): пустой массив ломает тип ответа; здесь только пруф |
| [hasura/graphql-engine#10135](https://github.com/hasura/graphql-engine/issues/10135) | extends | _только пруф_: Дубликат hasura#10239 и #10322 (b-01): тот же вариант с пустым массивом, только пруф |

### REST-NULL-VS-OMITTED — Null и отсутствующее поле (RWB-0122, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [hasura/graphql-engine#10013](https://github.com/hasura/graphql-engine/issues/10013) | extends | Отправить в теле GraphQL-запроса необязательные поля extensions, variables и operationName со значением null и проверить, что ответ такой же, как без этих полей |

