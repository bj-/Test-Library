# Кандидаты из баг-трекеров: партия `postgrest`

Сгенерировано `tools/mining/cluster.py` из `build/mining/<batch>/batches/*.out.jsonl` и
`ideas/mined/postgrest.review.yaml` — правки решений делаются в review-файле, затем пересборка.
План — `docs/BUG_MINING_PLAN.md`, шаги 6–7; применение — `tools/mining/apply_proofs.py`.

## Сводка

- Новых паттернов: 16 → идей: 15 (принять: 10, отклонить: 5, не решено: 0).
- Пруфы к существующим: 57 багов → 27 записей; новых шагов-вариантов: 53.

## Новые идеи

Принятые становятся записями `status: draft` с меткой `real-world-bug` и ссылкой на RWB.

| # | Решение | Запись / файл | Идея | Подтверждающие баги |
|---|---|---|---|---|
| 1 | accept | `OBS-METRICS-VALUE-RANGE` (RWB-0325)<br>`checks/common/observability.yaml` | Gauge-метрики с известными границами остаются в них и согласуются с фактическим состоянием после сбоев и восстановления — например, доступные соединения в пределах от 0 до размера пула при обрывах и переподключениях к БД | [PostgREST/postgrest#4622](https://github.com/PostgREST/postgrest/issues/4622) |
| 2 | accept | `OBS-SERVER-TIMING-ACCURATE` (RWB-0326)<br>`checks/common/observability.yaml` | Заголовок Server-Timing отражает фактическую длительность этапов — значения в документированных единицах (миллисекунды) и согласуются с независимым измерением в пределах допуска при запросе с известной задержкой; точного равенства суммы этапов общему времени не требуется | [PostgREST/postgrest#4522](https://github.com/PostgREST/postgrest/issues/4522) |
| 3 | accept | `REST-ALIASED-EMBED-FILTER-INDEPENDENCE` (RWB-0327)<br>`checks/rest/pagination.yaml` | Один связанный ресурс, вложенный в ответ несколько раз под разными алиасами со своими фильтрами (REST-вложения, алиасы GraphQL), фильтруется независимо — каждое вложение совпадает с отдельным запросом с его фильтром | [PostgREST/postgrest#4075](https://github.com/PostgREST/postgrest/issues/4075) |
| 4 | accept | `REST-FILTER-UNSELECTED-FIELD` (RWB-0328)<br>`checks/rest/pagination.yaml` | Фильтр по полю, не входящему в выбор полей (select, fields, sparse fieldsets), работает для любых источников — таблица, представление, результат функции — и для простого, логического и вложенного фильтра; ответ содержит только выбранные поля | [PostgREST/postgrest#3965](https://github.com/PostgREST/postgrest/issues/3965) |
| 5 | accept | `REST-FILTER-NAME-COLLISION` (RWB-0329)<br>`checks/rest/pagination.yaml` | Фильтр по полю, имя которого совпадает с именем вложенного (встраиваемого) ресурса или связи, применяется к значению поля — совпадение имён не меняет смысл фильтра и не даёт ошибку | [PostgREST/postgrest#2862](https://github.com/PostgREST/postgrest/issues/2862), [PostgREST/postgrest#2588](https://github.com/PostgREST/postgrest/issues/2588) |
| 6 | reject | отклонено: Специфика конфигурации PostgREST из самой БД (in-db config); идея сохранена в inbox как DB (№317); общая часть — обновление не меняет поведение — в COMPAT-UPGRADE-STORED-DATA-STABLE | Настройки, хранящиеся в БД, применяются при старте ко всем видам ресурсов | [PostgREST/postgrest#3660](https://github.com/PostgREST/postgrest/issues/3660) |
| 7 | reject | отклонено: Специфика PostgreSQL (SET у функции, search_path) — проверка уровня БД, а не API; идея — в inbox как DB (SECURITY DEFINER и фиксированный search_path) | Настройки, заданные на уровне функции (SET search_path), не меняют окружение остальной части запроса | [PostgREST/postgrest#3242](https://github.com/PostgREST/postgrest/issues/3242) |
| 8 | reject | отклонено: Специфика переключения ролей PostgreSQL (SET ROLE и параметры суперпользователя) — проверка уровня БД; идея — в inbox как DB | Настройки роли подключения не ломают запросы пользователей с меньшими правами | [PostgREST/postgrest#2896](https://github.com/PostgREST/postgrest/issues/2896) |
| 9 | reject | отклонено: Специфика API, построенного по функциям PostgreSQL (перегрузка по типу аргумента); идея — в inbox как DB (№315) | Перегруженные функции разрешаются по типу аргумента во всех местах использования | [PostgREST/postgrest#2963](https://github.com/PostgREST/postgrest/issues/2963) |
| 10 | reject | отклонено: Специфика API, построенного по функциям PostgreSQL (record, setof record, составные типы); идея — в inbox как DB (№316) | Функции с любым поддерживаемым видом возвращаемого значения вызываются через API | [PostgREST/postgrest#2881](https://github.com/PostgREST/postgrest/issues/2881) |
| 11 | accept | `REST-NEGOTIATED-FORMAT-CONFORMANCE` (RWB-0330)<br>`checks/rest/http-protocol.yaml` | Ответ в согласованном формате (GeoJSON, CSV, NDJSON) соответствует спецификации этого формата — для GeoJSON структура FeatureCollection и Feature и расположение членов по RFC 7946; пара к REST-ACCEPT-NEGOTIATION | [PostgREST/postgrest#2699](https://github.com/PostgREST/postgrest/issues/2699) |
| 12 | accept | `REST-CUSTOM-MEDIA-TYPE-EMPTY-RESULT` (RWB-0331)<br>`checks/rest/http-protocol.yaml` | Пустой результат или null в поддерживаемом пользовательском медиатипе (бинарный формат, свой обработчик) обрабатывается документированным образом — пустое тело того же Content-Type или документированный статус — без 5xx и внутренней ошибки | [PostgREST/postgrest#3126](https://github.com/PostgREST/postgrest/issues/3126) |
| 13 | accept | `HTTP-PREFERENCE-APPLIED-ACCURATE` (RWB-0332)<br>`checks/rest/http-protocol.yaml` | Заголовок Preference-Applied перечисляет ровно применённые предпочтения из Prefer (return, count, handling, tx и др.) — нет неприменённых, в том числе в ответе с ошибкой (RFC 7240) | [PostgREST/postgrest#2939](https://github.com/PostgREST/postgrest/issues/2939) |
| 14 | accept | `OBS-LOG-ENTRY-INTEGRITY` (RWB-0333)<br>`checks/common/observability.yaml` | Записи журнала при всплеске параллельных запросов не склеиваются и не разрываются — каждая запись отдельной строкой с собственной меткой времени, структурированный журнал разбирается построчно; нужен доступ к журналу | [PostgREST/postgrest#5234](https://github.com/PostgREST/postgrest/issues/5234) |
| 15 | accept | `PERF-METADATA-RELOAD-NO-BLOCK` (RWB-0334)<br>`checks/common/performance.yaml` | Перезагрузка кэша метаданных (схема, конфигурация, маршруты) на большом объёме не блокирует обслуживание запросов надолго — запросы идут по старому состоянию или с короткой задержкой в пределах SLO | [PostgREST/postgrest#4360](https://github.com/PostgREST/postgrest/issues/4360) |

## Пруфы к существующим

Запись получает метку `real-world-bug` и `Real-world bug: RWB-NNNN`; статус не меняется. Для `extends`
текст варианта добавляется шагом (`steps[].action`, в `notes` — RWB). Неверное совпадение — ID бага в
`proofs.exclude`, вариант без нового шага — в `proofs.no_variant`.

### AUTH-JWT-VALID-ACCEPTED — Валидный токен принимается при всех поддерживаемых алгоритмах, наборах ключей и настройках claims (RWB-0206, багов: 2)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [PostgREST/postgrest#4039](https://github.com/PostgREST/postgrest/issues/4039) | extends | Передать роль в claim по настроенному пути с индексом массива — массив из одного элемента, из нескольких элементов и строка; роль определяется одинаково, неподходящее значение даёт 401, а не тихий переход к анонимной роли |
| [PostgREST/postgrest#5212](https://github.com/PostgREST/postgrest/issues/5212) | extends | Отправить запрос со свежим токеном после длительного простоя сервера и проверить, что токен принимается |

### CONTRACT-FIELD-SELECTION — Выбор полей возвращает ровно запрошенные поля с правильными значениями (RWB-0026, багов: 4)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [PostgREST/postgrest#3887](https://github.com/PostgREST/postgrest/issues/3887) | extends | Запросить вложение со спредом и пустым списком полей и сравнить ответ с ответом на обычное пустое вложение |
| [PostgREST/postgrest#3093](https://github.com/PostgREST/postgrest/issues/3093) | extends | Запросить вложенные пустые вложения с фильтром по ним и проверить, что фильтр применён, а пустые вложения не попали в ответ |
| [PostgREST/postgrest#2565](https://github.com/PostgREST/postgrest/issues/2565) | extends | Запросить у результата функции только встроенную связь многие-ко-многим без собственных колонок и проверить успешный ответ |
| [PostgREST/postgrest#3160](https://github.com/PostgREST/postgrest/issues/3160) | extends | Запросить пользовательский формат ответа вместе с выбором части колонок или вычисляемых колонок и проверить, что формат применяется |

### CONTRACT-PUBLISHED-SCHEMA-VALID — Опубликованные сервисом описания API валидны в заявленном диалекте (RWB-0049, багов: 3)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [PostgREST/postgrest#4641](https://github.com/PostgREST/postgrest/issues/4641) | covered | _только пруф_: Запись проверяет валидность опубликованного описания в заявленном диалекте |
| [PostgREST/postgrest#4292](https://github.com/PostgREST/postgrest/issues/4292) | covered | _только пруф_: Запись проверяет валидность опубликованного описания |
| [PostgREST/postgrest#2619](https://github.com/PostgREST/postgrest/issues/2619) | extends | Создать представление над таблицей со связью, имя которого по алфавиту раньше таблицы, и проверить, что описание внешнего ключа в опубликованной схеме указывает на исходную таблицу |

### HTTP-OPTIONS-ALLOW — OPTIONS возвращает согласованный список методов (RWB-0335, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [PostgREST/postgrest#2821](https://github.com/PostgREST/postgrest/issues/2821) | extends | Отправить OPTIONS с Accept: application/json и другими поддерживаемыми медиатипами и проверить 200 с Allow |

### HTTP-UNKNOWN-ROUTE — Неизвестный маршрут возвращает 404, а не 5xx или 200 (RWB-0336, багов: 2)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [PostgREST/postgrest#4463](https://github.com/PostgREST/postgrest/issues/4463) | extends | Запросить несуществующий ресурс при десятках тысяч существующих и проверить, что приходит быстрый 404, а не обрыв соединения |
| [PostgREST/postgrest#3602](https://github.com/PostgREST/postgrest/issues/3602) | extends | Запросить несуществующий ресурс с параметром вложения связанных ресурсов и проверить 404, а не 400 |

### OBS-HEALTH-ENDPOINTS — Health-эндпоинты отражают состояние и не раскрывают детали (RWB-0093, багов: 3)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [PostgREST/postgrest#3330](https://github.com/PostgREST/postgrest/issues/3330) | extends | Опрашивать эндпоинт готовности во время долгой загрузки кэша метаданных и проверить 503 до её завершения |
| [PostgREST/postgrest#5096](https://github.com/PostgREST/postgrest/issues/5096) | extends | _только пруф_: Тот же сценарий, что у #5012 этой пачки — пруф |
| [PostgREST/postgrest#5012](https://github.com/PostgREST/postgrest/issues/5012) | extends | Запросить health-эндпоинт с тайм-аутом клиента и проверить, что ответ или отказ соединения приходит за ограниченное время |

### PAGE-BEYOND-LAST — Запрос страницы за последней возвращает пустой результат без ошибки (RWB-0337, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [PostgREST/postgrest#4455](https://github.com/PostgREST/postgrest/issues/4455) | extends | Запросить смещение больше числа записей с запросом точного общего счётчика и проверить статус, Content-Range и Content-Length ответа |

### PAGE-TOTAL-COUNT — Общее число элементов согласовано с суммой страниц (RWB-0095, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [PostgREST/postgrest#2846](https://github.com/PostgREST/postgrest/issues/2846) | extends | Запросить общий счётчик вместе с фильтром по наличию вложенного ресурса (is null, not is null) и проверить данные и Content-Range |

### RES-BULK-LIMITS — Массовые операции соблюдают лимиты и сообщают о каждом элементе (RWB-0100, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [PostgREST/postgrest#4100](https://github.com/PostgREST/postgrest/issues/4100) | extends | Вызвать процедуру, возвращающую void или скаляр и меняющую больше строк, чем разрешено строгим ограничением, и проверить отказ с откатом |

### RES-CACHE-EXPLICIT-INVALIDATION — Явный сброс кэша через API удаляет закэшированные ответы (RWB-0214, багов: 2)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [PostgREST/postgrest#2791](https://github.com/PostgREST/postgrest/issues/2791) | extends | Послать второй запрос на сброс кэша во время обработки первого, после ещё одного изменения, и проверить, что ответы отражают последнее состояние |
| [PostgREST/postgrest#2620](https://github.com/PostgREST/postgrest/issues/2620) | extends | Изменить тип колонки пересозданием таблицы, послать сигнал сброса кэша и проверить, что фильтр по колонке работает с новым типом |

### RES-CREATE-RESPONSE-MATCHES-READ — Ответ на создание и изменение совпадает с последующим чтением (RWB-0101, багов: 2)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [PostgREST/postgrest#3707](https://github.com/PostgREST/postgrest/issues/3707) | extends | Изменить записи по фильтру на изменяемое поле с возвратом представления и проверить, что в ответе все изменённые записи |
| [PostgREST/postgrest#3013](https://github.com/PostgREST/postgrest/issues/3013) | extends | Изменить и удалить записи с возвратом представления и сортировкой основного и вложенного ресурса и сравнить порядок с GET |

### RESIL-DEPENDENCY-DOWN — Недоступность зависимости даёт контролируемую ошибку (RWB-0107, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [PostgREST/postgrest#3673](https://github.com/PostgREST/postgrest/issues/3673) | extends | Вызвать на реплике конфликт запроса с восстановлением и проверить, что запрос завершается ошибкой, а не повторяется бесконечно |

### RESIL-PARTIAL-DEGRADATION — Отказ некритичной зависимости не ломает основной функционал (RWB-0109, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [PostgREST/postgrest#4873](https://github.com/PostgREST/postgrest/issues/4873) | extends | Прервать по тайм-ауту перезагрузку кэша схемы и проверить, что запросы обслуживаются по прежнему кэшу |

### REST-ACCEPT-NEGOTIATION — Согласование Accept (RWB-0280, багов: 5)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [PostgREST/postgrest#3373](https://github.com/PostgREST/postgrest/issues/3373) | extends | Запросить коллекцию из нескольких строк с Accept одиночного объекта и проверить, что ошибка 406 приходит с одним Content-Type application/json |
| [PostgREST/postgrest#3124](https://github.com/PostgREST/postgrest/issues/3124) | extends | Запросить ресурс с Accept каждого пользовательского медиатипа, для которого определён обработчик (в том числе в другой схеме), и проверить 200 с этим Content-Type |
| [PostgREST/postgrest#3089](https://github.com/PostgREST/postgrest/issues/3089) | extends | Запросить ресурс с Accept длинного медиатипа с точками и дефисами (application/vnd.openxmlformats-officedocument.wordprocessingml.document) и с Accept */*, проверить Content-Type |
| [PostgREST/postgrest#3498](https://github.com/PostgREST/postgrest/issues/3498) | extends | Отправить Accept с параметром медиатипа в кавычках, содержащим «;», «,» и экранированные кавычки, и проверить корректный разбор |
| [PostgREST/postgrest#3478](https://github.com/PostgREST/postgrest/issues/3478) | extends | Отправить Accept с типом в другом регистре (Application/JSON) и проверить, что он принимается как application/json |

### REST-CONTENT-TYPE-JSON — Content-Type и JSON-формат (RWB-0338, багов: 3)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [PostgREST/postgrest#4271](https://github.com/PostgREST/postgrest/issues/4271) | extends | Запросить служебный эндпоинт метрик и проверить Content-Type text/plain формата Prometheus |
| [PostgREST/postgrest#4030](https://github.com/PostgREST/postgrest/issues/4030) | extends | Отправить тело с Content-Type application/json; charset=utf-8 и с нераспознанным параметром медиатипа и проверить, что запрос принят |
| [PostgREST/postgrest#2915](https://github.com/PostgREST/postgrest/issues/2915) | extends | Переопределить Content-Type ответа из обработчика и проверить, что в ответе один заголовок Content-Type с новым значением |

### REST-ERROR-SCHEMA — Стабильная схема ошибок (RWB-0117, багов: 2)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [PostgREST/postgrest#3906](https://github.com/PostgREST/postgrest/issues/3906) | extends | Запросить многоуровневый несуществующий путь и отключённое описание API и проверить код и сообщение ошибки в теле 404 |
| [PostgREST/postgrest#3697](https://github.com/PostgREST/postgrest/issues/3697) | extends | Отправить вставку и upsert в несуществующий ресурс и проверить код и сообщение в теле ответа |

### REST-ERROR-STATUS-BODY — Согласованность статуса и тела ошибки (RWB-0339, багов: 5)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [PostgREST/postgrest#3257](https://github.com/PostgREST/postgrest/issues/3257) | extends | Вызвать операцию, превышающую лимит временных файлов БД, и проверить 500 без Retry-After, а не 503 |
| [PostgREST/postgrest#3256](https://github.com/PostgREST/postgrest/issues/3256) | extends | Запросить представление с бесконечной рекурсией в определении и проверить 500, а не 400 |
| [PostgREST/postgrest#3255](https://github.com/PostgREST/postgrest/issues/3255) | extends | Вызвать небольшую вставку, приводящую к рекурсии триггера на сервере, и проверить 500, а не 413 |
| [PostgREST/postgrest#3205](https://github.com/PostgREST/postgrest/issues/3205) | extends | _только пруф_: Тот же вариант, что у бага #3256 этой партии: серверная ошибка определения объекта отдаётся как 4xx |
| [PostgREST/postgrest#2569](https://github.com/PostgREST/postgrest/issues/2569) | extends | Запросить встраивание несуществующей связи и проверить, что подсказка в ошибке описывает выполненный поиск, а не предлагает перезагрузить кэш |

### REST-FILTER-EQUIVALENT-FORMS — Логически эквивалентные формы фильтра дают одинаковый ответ (RWB-0002, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [PostgREST/postgrest#2705](https://github.com/PostgREST/postgrest/issues/2705) | extends | Отправить PATCH/DELETE с ограничением через заголовок Range вместо limit/offset, с order и без него, и сравнить с ответами для limit/offset |

### REST-FILTER-OPERATOR-TYPE-MATRIX — Каждый оператор фильтра работает для каждого допустимого типа поля и возвращает ровно подходящие записи (RWB-0001, багов: 3)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [PostgREST/postgrest#4135](https://github.com/PostgREST/postgrest/issues/4135) | extends | Применить операторы фильтра к колонкам доменных типов (в том числе домена над доменом) и сравнить результат с колонкой базового типа |
| [PostgREST/postgrest#2929](https://github.com/PostgREST/postgrest/issues/2929) | extends | Отфильтровать и отсортировать результат функции по полю составного типа через оператор пути |
| [PostgREST/postgrest#2800](https://github.com/PostgREST/postgrest/issues/2800) | extends | Отфильтровать родительские записи по «связь не null» при связанной записи с null в части полей и проверить, что такие записи возвращаются, а «связь is null» отдаёт только записи без связи |

### REST-FILTER-SORT-PAGINATION — Комбинация filter/sort/pagination (RWB-0119, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [PostgREST/postgrest#4109](https://github.com/PostgREST/postgrest/issues/4109) | extends | Запросить сортировку с явным порядком null (nullslast, nullsfirst) вместе с limit и offset, в том числе для вложенного ресурса |

### REST-STRING-LENGTH-BOUNDARIES — Границы длины строки (RWB-0137, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [PostgREST/postgrest#2861](https://github.com/PostgREST/postgrest/issues/2861) | extends | Вставить и изменить значение максимальной длины в колонки char(n) и bit(n) и проверить, что оно принято |

### SEC-AUTHN-MALFORMED — Malformed credential is rejected (RWB-0142, багов: 2)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [PostgREST/postgrest#3926](https://github.com/PostgREST/postgrest/issues/3926) | extends | Отправить Authorization: Bearer с пустым значением токена и проверить 401 без выполнения операции |
| [PostgREST/postgrest#3601](https://github.com/PostgREST/postgrest/issues/3601) | extends | Отправить подписанный токен с ролью, которой нет на сервере, и проверить 401 |

### SEC-AUTHZ-ERROR-LEAK — Authorization failures do not disclose protected data (RWB-0340, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [PostgREST/postgrest#4675](https://github.com/PostgREST/postgrest/issues/4675) | extends | Запросить несуществующие ресурсы с именами, далёкими от существующих, и проверить, что подсказка не называет ресурсы, недоступные пользователю |

### SEC-TOKEN-SIGNATURE — Token with invalid signature is rejected (RWB-0204, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [PostgREST/postgrest#4014](https://github.com/PostgREST/postgrest/issues/4014) | extends | Сменить ключ подписи токенов перезагрузкой конфигурации и повторить запрос с ранее принятым токеном |

### VAL-CASE-SENSITIVITY — Чувствительность к регистру идентификаторов, email и enum соответствует контракту (RWB-0164, багов: 4)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [PostgREST/postgrest#5158](https://github.com/PostgREST/postgrest/issues/5158) | extends | Настроить сервис на схему с именем в смешанном регистре и выполнить запрос к корневому ресурсу и к таблице этой схемы |
| [PostgREST/postgrest#4955](https://github.com/PostgREST/postgrest/issues/4955) | extends | Задать роли БД настройку со значением в смешанном регистре (work_mem = '256MB') и выполнить запрос к API от этой роли |
| [PostgREST/postgrest#4678](https://github.com/PostgREST/postgrest/issues/4678) | extends | Подключить сервис к БД под ролью с именем в смешанном регистре и выполнить запросы, переключающие роль |
| [PostgREST/postgrest#3712](https://github.com/PostgREST/postgrest/issues/3712) | extends | Выполнить массовый upsert с подстановкой default в таблицу с именем в смешанном регистре и автогенерируемым ключом |

### VAL-DEFAULT-VALUES — Опущенные необязательные поля получают задокументированные значения по умолчанию (RWB-0166, багов: 3)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [PostgREST/postgrest#3706](https://github.com/PostgREST/postgrest/issues/3706) | extends | Вставить запись без поля доменного типа, у колонки которого свой default, и проверить, что применён default колонки, а не домена |
| [PostgREST/postgrest#2840](https://github.com/PostgREST/postgrest/issues/2840) | extends | Вставить запись без поля доменного типа с default и NOT NULL и проверить, что применён default домена |
| [PostgREST/postgrest#2756](https://github.com/PostgREST/postgrest/issues/2756) | extends | Отправить вставку с подстановкой значений по умолчанию, в списке колонок которой есть вычисляемая колонка, и проверить вычисление значения или понятную ошибку 4xx |

### VAL-SPECIAL-CHARACTERS — Спецсимволы, emoji и управляющие символы сохраняются или отклоняются корректно (RWB-0174, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [PostgREST/postgrest#3054](https://github.com/PostgREST/postgrest/issues/3054) | extends | Выбрать и отфильтровать по JSON-пути с ключами, содержащими спецсимволы (@, !, #, $, %, &) |

