# Кандидаты из баг-трекеров: партия `pilot`

Сгенерировано `tools/mining/cluster.py` из `build/mining/<batch>/batches/*.out.jsonl` и
`ideas/mined/pilot.review.yaml` — правки решений делаются в review-файле, затем пересборка.
План — `docs/BUG_MINING_PLAN.md`, шаги 6–7; применение — `tools/mining/apply_proofs.py`.

## Сводка

- Новых паттернов: 73 → идей: 53 (принять: 50, отклонить: 3, не решено: 0).
- Пруфы к существующим: 287 багов → 129 записей; новых шагов-вариантов: 255.

## Новые идеи

Принятые становятся записями `status: draft` с меткой `real-world-bug` и ссылкой на RWB.

| # | Решение | Запись / файл | Идея | Подтверждающие баги |
|---|---|---|---|---|
| 1 | accept | `REST-FILTER-OPERATOR-TYPE-MATRIX` (RWB-0001)<br>`checks/rest/pagination.yaml` | Матрица «оператор фильтра × тип поля»; допустимые операторы принимаются для типа и подтипов, результат совпадает с эталонным отбором по полному списку | [directus/directus#28303](https://github.com/directus/directus/issues/28303), [directus/directus#28256](https://github.com/directus/directus/issues/28256) |
| 2 | accept | `REST-FILTER-EQUIVALENT-FORMS` (RWB-0002)<br>`checks/rest/pagination.yaml` | Логически эквивалентные фильтры (плоская форма, вложенные $and/$or) дают одинаковый ответ | [strapi/strapi#27235](https://github.com/strapi/strapi/issues/27235) |
| 3 | accept | `VAL-DEFERRED-FAILURE` (RWB-0003)<br>`checks/rest/input-validation.yaml` | Данные, принятые при записи, не вызывают 5xx в зависимых операциях (чтение, поиск, экспорт, политика) | [keycloak/keycloak#53456](https://github.com/keycloak/keycloak/issues/53456) |
| 4 | accept | `SEC-AUTHZ-ROLE-POSITIVE-MATRIX` (RWB-0004)<br>`checks/security/access-control/SEC-AUTHZ-ROLE-POSITIVE-MATRIX.yaml` | Разрешённая операция работает для каждой роли с правом, а не только для администратора (позитивная матрица прав) | [directus/directus#28285](https://github.com/directus/directus/issues/28285) |
| 5 | accept | `SEC-ROLE-ADMIN-SELF-TARGET` (RWB-0005)<br>`checks/security/access-control/SEC-ROLE-ADMIN-SELF-TARGET.yaml` | Делегированный администратор над собственной учёткой — явное разрешение или 403 по политике, без 5xx | [keycloak/keycloak#50136](https://github.com/keycloak/keycloak/issues/50136) |
| 6 | accept | `SEC-FAIL-CLOSED-INPUT` (RWB-0006)<br>`checks/security/api-hardening.yaml` | Неожиданный тип, пустое или отсутствующее поле, участвующее в проверке безопасности, приводит к отказу, а не к пропуску проверки (fail-closed) | [keycloak/keycloak#53140](https://github.com/keycloak/keycloak/issues/53140), [keycloak/keycloak#50719](https://github.com/keycloak/keycloak/issues/50719) |
| 7 | accept | `CONC-REQUEST-CONTEXT-ISOLATION` (RWB-0007)<br>`checks/common/concurrency.yaml` | Параллельные запросы разных пользователей получают только свой контекст и свой ответ (в том числе через общий канал к нижележащему сервису) | [nestjs/nest#17007](https://github.com/nestjs/nest/issues/17007), [nestjs/nest#16989](https://github.com/nestjs/nest/issues/16989), [nestjs/nest#505](https://github.com/nestjs/nest/issues/505) |
| 8 | accept | `CONC-PARALLEL-INDEPENDENT` (RWB-0008)<br>`checks/common/concurrency.yaml` | Параллельные независимые запросы одной операции выполняются без 5xx (общая кэшированная конфигурация) | [keycloak/keycloak#50286](https://github.com/keycloak/keycloak/issues/50286) |
| 9 | accept | `PRIV-RESPONSE-FOREIGN-DATA` (RWB-0009)<br>`checks/security/privacy.yaml` | Ответ не содержит фрагментов данных других запросов и памяти процесса (общие буферы сериализации) | [GHSA-j22f-vq7h-c4qm](https://github.com/advisories/GHSA-j22f-vq7h-c4qm) |
| 10 | accept | `AUTH-TOKEN-INTROSPECTION` (RWB-0010)<br>`checks/security/authentication-session.yaml` | Интроспекция (RFC 7662) — active true для действующих токенов каждого типа с теми же claims, false для отозванных и истёкших | [keycloak/keycloak#53029](https://github.com/keycloak/keycloak/issues/53029), [keycloak/keycloak#51552](https://github.com/keycloak/keycloak/issues/51552) |
| 11 | accept | `AUTH-SESSION-NOT-BEFORE-LOGIN` (RWB-0011)<br>`checks/security/authentication-session.yaml` | Анонимный запрос без входа не получает cookie сессии и не создаёт серверную сессию | [expressjs/session#239](https://github.com/expressjs/session/issues/239) |
| 12 | accept | `FILE-TRANSFORM-LIMITS` (RWB-0012)<br>`checks/rest/files.yaml` | Лимит трансформации файла на лету (размер, формат) не отклоняет допустимые комбинации и отклоняет превышение, в том числе на промежуточном шаге | [directus/directus#28103](https://github.com/directus/directus/issues/28103) |
| 13 | accept | `HTTP-VERSION-PARITY` (RWB-0013)<br>`checks/rest/http-protocol.yaml` | Запросы по HTTP/2 и с предложением Upgrade h2c обслуживаются так же, как по HTTP/1.1; соединение не сбрасывается, процесс не падает | [expressjs/express#6580](https://github.com/expressjs/express/issues/6580), [expressjs/express#5678](https://github.com/expressjs/express/issues/5678) |
| 14 | accept | `GQL-EQUIVALENT-SELECTION-FORMS` (RWB-0014)<br>`checks/graphql/graphql.yaml` | Прямой выбор, inline- и именованные фрагменты, алиасы, вложенные аргументы в запросе по id и в списке дают одинаковые данные | [directus/directus#28060](https://github.com/directus/directus/issues/28060), [directus/directus#27772](https://github.com/directus/directus/issues/27772), [directus/directus#26232](https://github.com/directus/directus/issues/26232) |
| 15 | accept | `RES-DRAFT-PUBLISH-FIDELITY` (RWB-0015)<br>`checks/common/resource-lifecycle.yaml` | Публикация черновика переносит все изменения (включая связи и их порядок), не удаляет объект из связей других и работает между типами с разными режимами | [strapi/strapi#26786](https://github.com/strapi/strapi/issues/26786), [strapi/strapi#26473](https://github.com/strapi/strapi/issues/26473), [strapi/strapi#26804](https://github.com/strapi/strapi/issues/26804) |
| 16 | accept | `RES-RELATION-ORDER-STABLE` (RWB-0016)<br>`checks/common/resource-lifecycle.yaml` | Изменение связанного ресурса не меняет ручной порядок связей у другой стороны | [strapi/strapi#26615](https://github.com/strapi/strapi/issues/26615) |
| 17 | accept | `BIZ-EMAIL-LINK-CROSS-SESSION` (RWB-0017)<br>`checks/common/business-logic.yaml` | Ссылка-действие из письма работает в другом браузере/сессии и после перезапуска сервиса (или понятная ошибка, но не 5xx), во всех вариантах настройки потока | [keycloak/keycloak#52604](https://github.com/keycloak/keycloak/issues/52604), [keycloak/keycloak#51088](https://github.com/keycloak/keycloak/issues/51088) |
| 18 | accept | `AUTH-REFRESH-PRESERVES-SCOPE` (RWB-0018)<br>`checks/security/authentication-session.yaml` | Refresh без параметра scope сохраняет scope исходной авторизации (RFC 6749 §6) | [keycloak/keycloak#52574](https://github.com/keycloak/keycloak/issues/52574) |
| 19 | accept | `AUTH-MFA-UNENROLLED-ERROR` (RWB-0019)<br>`checks/security/authentication-session.yaml` | Ошибка шага второго фактора у пользователя без зарегистрированного фактора — обычная 4xx, как у пользователя с фактором, без 5xx | [keycloak/keycloak#52464](https://github.com/keycloak/keycloak/issues/52464) |
| 20 | reject | отклонено: Специфично для конфигурации мапперов Keycloak; общая часть (claims выпускаемого токена) — в AUTH-TOKEN-RESERVED-CLAIMS | Claim из маппера атрибута сохраняется в токене при нестандартном значении | [keycloak/keycloak#52087](https://github.com/keycloak/keycloak/issues/52087) |
| 21 | accept | `AUTH-OAUTH-PAR` (RWB-0020)<br>`checks/security/authentication-session.yaml` | PAR (RFC 9126) — параметры через request_uri действуют как в прямом запросе; срок request_uri ограничивает погашение, а не длительность входа | [keycloak/keycloak#51761](https://github.com/keycloak/keycloak/issues/51761), [keycloak/keycloak#49255](https://github.com/keycloak/keycloak/issues/49255) |
| 22 | reject | отклонено: Kerberos/SPNEGO вне нашего стека и типовых API; вернуться, если появится продукт с Negotiate | SPNEGO с взаимной аутентификацией возвращает ответный токен в WWW-Authenticate | [keycloak/keycloak#51559](https://github.com/keycloak/keycloak/issues/51559) |
| 23 | accept | `RESIL-ENCRYPTION-KEY-ROTATION` (RWB-0021)<br>`checks/common/resilience.yaml` | Значение, которое не удаётся расшифровать после смены ключа, не ломает чтение и сохранение остальных данных | [directus/directus#26734](https://github.com/directus/directus/issues/26734) |
| 24 | accept | `RES-LARGE-RELATION-SET` (RWB-0022)<br>`checks/common/resource-lifecycle.yaml` | Тысячи связанных объектов не дают 5xx из-за лимитов СУБД на параметры запроса (2100 MSSQL, 1000 в IN Oracle) | [keycloak/keycloak#51510](https://github.com/keycloak/keycloak/issues/51510) |
| 25 | accept | `RES-CACHE-KEY-COMPLETENESS` (RWB-0023)<br>`checks/common/resource-lifecycle.yaml` | Серверный кэш различает ответы по всем значимым параметрам запроса и по типу ресурса при одинаковых id | [nestjs/nest#13058](https://github.com/nestjs/nest/issues/13058), [directus/directus#26929](https://github.com/directus/directus/issues/26929) |
| 26 | reject | отклонено: Специфично для флагов функций Keycloak; разбор scope в целом покрыт SEC-SCOPE-* | Параметризованные scope принимаются при любой комбинации включённых функций | [keycloak/keycloak#51437](https://github.com/keycloak/keycloak/issues/51437) |
| 27 | accept | `HARD-SLOW-CLIENT-LIMITS` (RWB-0024)<br>`checks/security/api-hardening.yaml` | Незавершённые сообщения (slowloris) и непрочитанные ответы не накапливаются без ограничения; таймауты, лимит соединений, backpressure | [GHSA-96h4-vgxj-gvm2](https://github.com/advisories/GHSA-96h4-vgxj-gvm2) |
| 28 | accept | `SEC-AUTHZ-RECREATED-IDENTITY` (RWB-0025)<br>`checks/security/access-control/SEC-AUTHZ-RECREATED-IDENTITY.yaml` | Права и согласия не переходят к пересозданному пользователю с тем же логином; привязка к неизменяемому id | [keycloak/keycloak#51398](https://github.com/keycloak/keycloak/issues/51398) |
| 29 | accept | `CONTRACT-FIELD-SELECTION` (RWB-0026)<br>`checks/common/contract.yaml` | Выбор полей (fields, sparse fieldsets) возвращает ровно запрошенные поля с правильными значениями, включая ключ и вложенные связи | [directus/directus#26596](https://github.com/directus/directus/issues/26596) |
| 30 | accept | `HTTP-ABSOLUTE-URL-BASE-PATH` (RWB-0027)<br>`checks/rest/http-protocol.yaml` | Абсолютные URL, которые формирует сервер (Location, callback, ссылки в письмах), учитывают публичный базовый путь | [directus/directus#26236](https://github.com/directus/directus/issues/26236) |
| 31 | accept | `SEC-READONLY-MODE-ENFORCED` (RWB-0028)<br>`checks/security/api-hardening.yaml` | Режим «только чтение» для пользовательских запросов (SQL, GraphQL) запрещает любые изменения, а не проверяет первое ключевое слово | [GHSA-mwwr-p57h-56pf](https://github.com/advisories/GHSA-mwwr-p57h-56pf), [GHSA-5648-rgj9-v224](https://github.com/advisories/GHSA-5648-rgj9-v224) |
| 32 | accept | `RES-EXPORT-IMPORT-ROUNDTRIP` (RWB-0029)<br>`checks/common/resource-lifecycle.yaml` | Данные и снапшоты, выгруженные API, принимаются им же обратно без изменений (round-trip) | [directus/directus#26235](https://github.com/directus/directus/issues/26235) |
| 33 | accept | `HARD-CLIENT-IP-TRUSTED-PROXIES` (RWB-0030)<br>`checks/security/api-hardening.yaml` | IP клиента определяется по X-Forwarded-For с учётом числа доверенных прокси, одинаково на всех маршрутах и модулях | [expressjs/express#2569](https://github.com/expressjs/express/issues/2569), [expressjs/express#2550](https://github.com/expressjs/express/issues/2550) |
| 34 | accept | `FILE-MALFORMED-STRUCTURE` (RWB-0031)<br>`checks/rest/files.yaml` | Повреждённый файл (некорректные размеры блоков) при разборе метаданных даёт 4xx, а не падение процесса | [GHSA-8j4c-6x6g-rq3j](https://github.com/advisories/GHSA-8j4c-6x6g-rq3j) |
| 35 | accept | `ASYNC-RPC-ERROR-PROPAGATION` (RWB-0032)<br>`checks/common/async-integration.yaml` | Ошибка обработчика в схеме запрос-ответ через брокер возвращается вызывающему в документированном формате, а не таймаутом | [nestjs/nest#10113](https://github.com/nestjs/nest/issues/10113) |
| 36 | accept | `ASYNC-MESSAGE-VALIDATION` (RWB-0033)<br>`checks/common/async-integration.yaml` | Входящие сообщения брокера валидируются по схеме так же, как HTTP-запросы | [nestjs/nest#5974](https://github.com/nestjs/nest/issues/5974) |
| 37 | accept | `AUTH-GENERATED-SECRET-STRENGTH` (RWB-0034)<br>`checks/security/authentication-session.yaml` | Сгенерированные сервером секреты (HMAC-ключи, секреты клиентов) имеют энтропию не ниже требуемой алгоритмом | [keycloak/keycloak#49793](https://github.com/keycloak/keycloak/issues/49793) |
| 38 | accept | `RES-SYSTEM-OBJECT-PROTECTED` (RWB-0035)<br>`checks/common/resource-lifecycle.yaml` | Встроенные (системные) объекты защищены от удаления и изменения при любой конфигурации, понятной ошибкой одинаково во всех версиях API | [keycloak/keycloak#50796](https://github.com/keycloak/keycloak/issues/50796), [keycloak/keycloak#49674](https://github.com/keycloak/keycloak/issues/49674) |
| 39 | accept | `SEC-AUTHN-SCHEMES-SUPPORTED` (RWB-0036)<br>`checks/security/access-control/SEC-AUTHN-SCHEMES-SUPPORTED.yaml` | Все задокументированные схемы Authorization принимаются на своих эндпоинтах; неподдерживаемые — 401 с WWW-Authenticate | [keycloak/keycloak#49611](https://github.com/keycloak/keycloak/issues/49611) |
| 40 | accept | `FILE-UPLOAD-KEY-COLLISION` (RWB-0037)<br>`checks/rest/files.yaml` | Загрузка не перезаписывает чужой файл с тем же именем или ключом хранилища | [GHSA-7vg8-29qx-jgj8](https://github.com/advisories/GHSA-7vg8-29qx-jgj8) |
| 41 | accept | `AUTH-TOKEN-RESERVED-CLAIMS` (RWB-0038)<br>`checks/security/authentication-session.yaml` | Пользовательские поля профиля не переопределяют зарезервированные claims токена (sub, iss, aud, exp, roles) | [GHSA-66wr-7vmr-p5jq](https://github.com/advisories/GHSA-66wr-7vmr-p5jq) |
| 42 | accept | `AUTH-OAUTH-RESOURCE-INDICATOR` (RWB-0039)<br>`checks/security/authentication-session.yaml` | Индикатор ресурса (RFC 8707), не соответствующий аудитории клиента, даёт 400 invalid_target | [keycloak/keycloak#49077](https://github.com/keycloak/keycloak/issues/49077) |
| 43 | accept | `ASYNC-EVENT-PATH-SAME-RULES` (RWB-0040)<br>`checks/common/async-integration.yaml` | Событийный путь (вебхук, событие) применяет те же фильтры и границы доступа, что и плановая синхронизация | [GHSA-c36c-cf6r-ghgj](https://github.com/advisories/GHSA-c36c-cf6r-ghgj), [GHSA-gp6m-x9vw-5c5x](https://github.com/advisories/GHSA-gp6m-x9vw-5c5x) |
| 44 | accept | `AUTH-EXTERNAL-IDP-UNVERIFIED-EMAIL` (RWB-0041)<br>`checks/security/authentication-session.yaml` | Вход через внешний IdP не связывается с существующей учёткой по неподтверждённому email (email_verified=false или нет признака) | [GHSA-xm5q-p7w3-x6cp](https://github.com/advisories/GHSA-xm5q-p7w3-x6cp), [GHSA-826h-28h9-65hg](https://github.com/advisories/GHSA-826h-28h9-65hg), [GHSA-6j36-r6pr-59x4](https://github.com/advisories/GHSA-6j36-r6pr-59x4) |
| 45 | accept | `SEC-IDENTITY-PROOF-OF-POSSESSION` (RWB-0042)<br>`checks/security/access-control/SEC-IDENTITY-PROOF-OF-POSSESSION.yaml` | Заявленная клиентом идентичность (кошелёк, DID, account id) без доказательства владения не даёт прав и льгот | [GHSA-jg6q-3qfh-r9f8](https://github.com/advisories/GHSA-jg6q-3qfh-r9f8) |
| 46 | accept | `SEC-CONFUSED-DEPUTY` (RWB-0043)<br>`checks/security/access-control/SEC-CONFUSED-DEPUTY.yaml` | Действия во внешней системе от имени пользователя — только с его правами; нет отката на сервисные учётные данные, прокси к стороннему API пропускает только нужные операции | [GHSA-29gx-h2m3-xw44](https://github.com/advisories/GHSA-29gx-h2m3-xw44), [GHSA-r9v2-gg2j-22q5](https://github.com/advisories/GHSA-r9v2-gg2j-22q5) |
| 47 | accept | `AUTH-TOKEN-SENDER-CONSTRAINED` (RWB-0044)<br>`checks/security/authentication-session.yaml` | Обмен и обновление токена сохраняют привязку к отправителю (DPoP, mTLS) или требуют доказательство владения ключом | [keycloak/keycloak#50963](https://github.com/keycloak/keycloak/issues/50963) |
| 48 | accept | `ERR-STATUS-MATCHES-EFFECT` (RWB-0045)<br>`checks/common/errors.yaml` | Код ответа соответствует фактическому результату; при 5xx — состояние не изменено (или явное сообщение о частичном выполнении) | [keycloak/keycloak#48904](https://github.com/keycloak/keycloak/issues/48904) |
| 49 | accept | `INJ-LLM-GENERATED-ACTIONS` (RWB-0046)<br>`checks/security/injection.yaml` | Код и вызовы инструментов, сгенерированные LLM по вводу пользователя, не выполняют исходящих запросов и опасных операций (prompt injection) | [GHSA-w7x8-q2gp-5cgg](https://github.com/advisories/GHSA-w7x8-q2gp-5cgg) |
| 50 | accept | `SEC-CLONE-FIELD-PERMISSIONS` (RWB-0047)<br>`checks/security/access-control/SEC-CLONE-FIELD-PERMISSIONS.yaml` | Копирование/клонирование ресурса соблюдает полевые права чтения и создания; отключённое дублирование недоступно | [GHSA-vc4h-q48j-5hcx](https://github.com/advisories/GHSA-vc4h-q48j-5hcx) |
| 51 | accept | `FILE-ABORTED-UPLOAD-CLEANUP` (RWB-0048)<br>`checks/rest/files.yaml` | Прерванная загрузка не оставляет данных в хранилище и не учитывается в квоте | [GHSA-3pph-fpjx-jg34](https://github.com/advisories/GHSA-3pph-fpjx-jg34) |
| 52 | accept | `CONTRACT-PUBLISHED-SCHEMA-VALID` (RWB-0049)<br>`checks/common/contract.yaml` | Опубликованные сервисом описания (OpenAPI, JSON Schema, MCP tools, SDL) валидны в заявленном диалекте и проходят строгий валидатор | [strapi/strapi#27395](https://github.com/strapi/strapi/issues/27395) |
| 53 | accept | `ASYNC-SSE-STREAM` (RWB-0050)<br>`checks/common/async-integration.yaml` | Потоковый ответ SSE работает для всех методов (включая POST с телом), отдаёт text/event-stream и события до закрытия клиентом | [nestjs/nest#17098](https://github.com/nestjs/nest/issues/17098) |

## Пруфы к существующим

Запись получает метку `real-world-bug` и `Real-world bug: RWB-NNNN`; статус не меняется. Для `extends`
текст варианта добавляется шагом (`steps[].action`, в `notes` — RWB). Неверное совпадение — ID бага в
`proofs.exclude`, вариант без нового шага — в `proofs.no_variant`.

### ASYNC-DEAD-LETTER — Необрабатываемые сообщения уходят в DLQ без блокировки очереди (RWB-0051, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [nestjs/nest#10091](https://github.com/nestjs/nest/issues/10091) | extends | Различение повторяемых и неповторяемых ошибок — бизнес-ошибка не должна повторяться |

### ASYNC-JOB-LIFECYCLE — Фоновая задача проходит статусы и отдаёт результат (RWB-0052, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [strapi/strapi#26579](https://github.com/strapi/strapi/issues/26579) | extends | Задача падает на ограничении данных — проверить детализацию причины в статусе и судьбу частичного результата |

### ASYNC-WEBHOOK-SIGNATURE — Вебхуки подписаны, подпись проверяется, повтор отклоняется (RWB-0053, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [nestjs/nest#14543](https://github.com/nestjs/nest/issues/14543) | extends | Добавить сторону приёма: подпись по сырым байтам при неканоническом форматировании JSON |

### ASYNC-WEBHOOK-URL-SSRF — URL вебхука не может указывать на внутренние адреса (RWB-0054, багов: 3)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-q567-cr4x-96w4](https://github.com/advisories/GHSA-q567-cr4x-96w4) | covered | _только пруф_: Ровно эта проверка; пруф к существующей записи |
| [GHSA-xxv7-2vv3-h682](https://github.com/advisories/GHSA-xxv7-2vv3-h682) | covered | _только пруф_: Ровно эта проверка |
| [GHSA-354h-gmhv-mr9c](https://github.com/advisories/GHSA-354h-gmhv-mr9c) | covered | _только пруф_: Ровно эта проверка |

### AUTH-API-KEY-LIFECYCLE — API-ключи ограничены по правам, отзываются и не раскрываются (RWB-0055, багов: 3)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [keycloak/keycloak#50855](https://github.com/keycloak/keycloak/issues/50855) | extends | Секрет клиента OAuth после ротации и отключения функции — старый не должен работать |
| [GHSA-238x-w2j9-gwwr](https://github.com/advisories/GHSA-238x-w2j9-gwwr) | extends | Ключ как поле документа пользователя в обычных чтениях и списках |
| [GHSA-2q76-m6w6-qgc6](https://github.com/advisories/GHSA-2q76-m6w6-qgc6) | extends | Создание/отзыв ключа для чужой учётной записи (владение ключом) |

### AUTH-BRUTE-FORCE-PROTECTION — Перебор паролей ограничивается (RWB-0056, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [keycloak/keycloak#49960](https://github.com/keycloak/keycloak/issues/49960) | extends | refresh токена или SSO по cookie из существующей сессии не должен сбрасывать блокировку |

### AUTH-COOKIE-ATTRIBUTES — Сессионные cookie имеют Secure, HttpOnly, SameSite и узкие Domain/Path (RWB-0057, багов: 2)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [jshttp/cookie#103](https://github.com/jshttp/cookie/issues/103) | extends | Добавить синтаксическую корректность Max-Age/Expires, в том числе при больших и нулевых сроках |
| [strapi/strapi#26723](https://github.com/strapi/strapi/issues/26723) | extends | Добавить Max-Age/Expires по настройке на всех cookie аутентификации, включая обновление токена |

### AUTH-LOGIN-IDENTIFIER-NORMALIZATION — Логин (email, телефон) нормализуется одинаково при входе, создании и поиске (RWB-0058, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [keycloak/keycloak#53138](https://github.com/keycloak/keycloak/issues/53138) | extends | Одинаковая нормализация не только при входе, но и в проверках согласия и прав |

### AUTH-LOGOUT-INVALIDATES — После выхода токен и сессия недействительны (RWB-0059, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [keycloak/keycloak#50629](https://github.com/keycloak/keycloak/issues/50629) | extends | Выход после отзыва согласия — отзыв refresh-токена не должен падать, сессия завершается |

### AUTH-MFA-STEP-UP — Операции, требующие второго фактора, недоступны без него (RWB-0060, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [directus/directus#28152](https://github.com/directus/directus/issues/28152) | extends | Добавить сохранение требования MFA после refresh и при наследовании ролей |

### AUTH-OAUTH-REDIRECT-STATE — OAuth/OIDC flow проверяет redirect_uri, state и PKCE (RWB-0061, багов: 2)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [directus/directus#26237](https://github.com/directus/directus/issues/26237) | extends | Позитивный вариант: адрес из allowlist должен приниматься (регрессия ложного отказа), в т. ч. после обновления |
| [keycloak/keycloak#49456](https://github.com/keycloak/keycloak/issues/49456) | extends | Клиенты, зарегистрированные динамически/через метаданные, — те же ограничения redirect_uri |

### AUTH-PASSWORD-POLICY — Политика паролей применяется на сервере (RWB-0062, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [keycloak/keycloak#51674](https://github.com/keycloak/keycloak/issues/51674) | extends | Режим с ограниченным криптопровайдером (FIPS), пароль короче его внутреннего минимума — ошибка политики, а не 5xx; проверить все пути (смена, сброс, обязательное обновление) |

### AUTH-SESSION-TIMEOUT — Сессия истекает после простоя и абсолютного срока (RWB-0063, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [expressjs/session#340](https://github.com/expressjs/session/issues/340) | extends | Добавить проверку продления при активности (в inbox №21 — AUTH-SESSION-SLIDING-RENEWAL) |

### BIZ-ONE-TIME-BENEFIT-REUSE — Одноразовые промокоды, бонусы и приглашения нельзя использовать повторно (RWB-0064, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [directus/directus#26699](https://github.com/directus/directus/issues/26699) | extends | Добавить приглашение, ставшее недействительным из-за активации пользователя другим путём; проверять код и текст ошибки |

### BIZ-SIDE-EFFECTS-ONCE — Побочные эффекты (письма, push, события) выполняются ровно один раз (RWB-0065, багов: 2)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [strapi/strapi#26610](https://github.com/strapi/strapi/issues/26610) | extends | Добавить сравнение одиночного и массового удаления по числу побочных эффектов |
| [nestjs/nest#2557](https://github.com/nestjs/nest/issues/2557) | extends | Обработчик WebSocket-события, зарегистрированный дважды (наследование) |

### BIZ-WORKFLOW-STEP-SKIP — Нельзя пропустить обязательный шаг бизнес-процесса (RWB-0066, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-35jj-42hp-8gmq](https://github.com/advisories/GHSA-35jj-42hp-8gmq) | extends | Пропуск шага согласования через другой канал продолжения с токеном, выданным для иного шага |

### COMPAT-IMPLEMENTATION-MATCHES-CONTRACT — Реализация соответствует опубликованному контракту (RWB-0067, багов: 6)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [directus/directus#27039](https://github.com/directus/directus/issues/27039) | extends | Производные контракты (схемы MCP-инструментов, SDK) против контракта API |
| [directus/directus#27762](https://github.com/directus/directus/issues/27762) | extends | Описанные параметры без эффекта — проверить влияние каждого документированного параметра |
| [directus/directus#27761](https://github.com/directus/directus/issues/27761) | extends | Реализованные маршруты, отсутствующие в контракте (включая публичные без аутентификации) |
| [expressjs/express#2495](https://github.com/expressjs/express/issues/2495) | extends | Маршруты-префиксы перехватывают более длинные пути — проверить, что ответ от нужной операции |
| [keycloak/keycloak#49730](https://github.com/keycloak/keycloak/issues/49730) | extends | Документ discovery/метаданных как контракт — сверять объявленные возможности с фактическими |
| [keycloak/keycloak#52378](https://github.com/keycloak/keycloak/issues/52378) | covered | _только пруф_: Строгая валидация ответа по опубликованной схеме ловит расхождение |

### ERR-INTERNAL-ERROR-SHAPE — Внутренняя ошибка сервера возвращается в общей модели без утечек (RWB-0068, багов: 2)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [nestjs/nest#17695](https://github.com/nestjs/nest/issues/17695) | extends | Ошибка зависимости со своим кодом не меняет статус ответа клиенту |
| [nestjs/nest#373](https://github.com/nestjs/nest/issues/373) | extends | Ошибка, возникшая асинхронно в обработчике, — ответ приходит без зависания и в общей модели |

### FILE-ARCHIVE-BOMB — Архивные и графические бомбы не исчерпывают ресурсы (RWB-0069, багов: 3)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-f94x-6692-553q](https://github.com/advisories/GHSA-f94x-6692-553q) | extends | Добавить медиафайлы с искажёнными размерами блоков (бесконечный цикл разбора), не только архивы и изображения |
| [GHSA-c6fg-446q-cg94](https://github.com/advisories/GHSA-c6fg-446q-cg94) | extends | Заявленный в заголовке ZIP размер занижен — лимит должен считаться по фактическому выходу |
| [GHSA-8238-w5pm-2374](https://github.com/advisories/GHSA-8238-w5pm-2374) | extends | Не бомба, а испорченные сжатые данные — проверять живость сервиса после ответа |

### FILE-DOWNLOAD-AUTHZ — Скачивание файлов проверяет права и срок действия ссылок (RWB-0070, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-rg9r-hr7g-5gc2](https://github.com/advisories/GHSA-rg9r-hr7g-5gc2) | extends | Манипуляция путём в URL статического контента (traversal, кодирование) приводит к файлу другой сущности, а права проверены по сущности из исходного пути; прогонять на внешнем хранилище |

### FILE-EMPTY-AND-MALFORMED-MULTIPART — Пустой файл и некорректный multipart обрабатываются корректно (RWB-0071, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [expressjs/express#6406](https://github.com/expressjs/express/issues/6406) | covered | _только пруф_ |

### FILE-MALICIOUS-CONTENT — Вредоносное содержимое обнаруживается или изолируется (RWB-0072, багов: 2)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-788w-68h3-cvxp](https://github.com/advisories/GHSA-788w-68h3-cvxp) | extends | Файл получает сам сервер по ссылке пользователя (превью, закладка), а не загружает клиент |
| [GHSA-jj74-hc2q-xrvm](https://github.com/advisories/GHSA-jj74-hc2q-xrvm) | extends | Пакеты расширений (темы, плагины) — путь за каталог и исполнение файлов данных; связано с INJ-PATH-TRAVERSAL |

### FILE-UPLOAD-TYPE-VALIDATION — Тип файла проверяется по содержимому, а не только по расширению (RWB-0073, багов: 2)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [directus/directus#27784](https://github.com/directus/directus/issues/27784) | extends | Согласованность проверки на альтернативных путях загрузки (TUS, импорт по URL) |
| [nestjs/nest#437](https://github.com/nestjs/nest/issues/437) | covered | _только пруф_ |

### GRPC-STREAM-TERMINATION — Streaming RPC terminates correctly (RWB-0074, багов: 2)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [nestjs/nest#13360](https://github.com/nestjs/nest/issues/13360) | extends | Исключение в обработчике стрима — клиент получает ошибку, сервис после этого доступен |
| [nestjs/nest#13187](https://github.com/nestjs/nest/issues/13187) | extends | Исключение обработчика до первого сообщения — итоговый статус не OK |

### HARD-DEBUG-ENDPOINTS — Отладочные и служебные эндпоинты недоступны извне (RWB-0075, багов: 2)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-jmg2-rcxh-w8q3](https://github.com/advisories/GHSA-jmg2-rcxh-w8q3) | extends | Служебный сервер доступен по сети (0.0.0.0) и с wildcard CORS — проверить доступность не с loopback и ответ на preflight с чужим Origin |
| [GHSA-rqx4-3f6q-3x2v](https://github.com/advisories/GHSA-rqx4-3f6q-3x2v) | covered | _только пруф_: Тот же вариант, что из GHSA-jmg2-rcxh-w8q3 (служебный API, сетевой доступ, CORS *) |

### HARD-EXCESSIVE-DATA-EXPOSURE — Ответы не содержат внутренних полей сверх контракта (RWB-0076, багов: 3)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [keycloak/keycloak#51137](https://github.com/keycloak/keycloak/issues/51137) | extends | Вариант для токенов: состав claims по политике проверить для каждого типа grant, а не только основного |
| [GHSA-g2v8-7jhw-pp8p](https://github.com/advisories/GHSA-g2v8-7jhw-pp8p) | extends | Ответы о фоновых задачах (статус, шаги, журнал) — без секретов контекста выполнения |
| [GHSA-xgv3-crq2-6f69](https://github.com/advisories/GHSA-xgv3-crq2-6f69) | extends | Ответы auth-эндпоинтов (refresh, reset, verify), обходящие общую фильтрацию полей |

### HARD-EXPENSIVE-OPERATION-LIMITS — Дорогие операции ограничены по ресурсам (RWB-0077, багов: 4)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-ff3f-86qr-9cv3](https://github.com/advisories/GHSA-ff3f-86qr-9cv3) | extends | Усиление памяти при разборе URL (числовые ключи параметров) |
| [GHSA-477h-4r7f-fvrx](https://github.com/advisories/GHSA-477h-4r7f-fvrx) | extends | Сверхдлинный пароль на auth-эндпоинтах (в том числе для несуществующего пользователя) |
| [GHSA-rj75-hqrm-r3gf](https://github.com/advisories/GHSA-rj75-hqrm-r3gf) | extends | Алгоритмическая сложность парсеров ввода — плоский вход с большим числом элементов при нулевой вложенности |
| [GHSA-r3ph-w7gj-g6xm](https://github.com/advisories/GHSA-r3ph-w7gj-g6xm) | extends | YAML с алиасами и merge-ключами (включая пустые отображения) — стоимость разбора ограничена |

### HARD-HOST-HEADER — Подмена Host и X-Forwarded-Host не влияет на ссылки и маршрутизацию (RWB-0078, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-fm8p-53ww-hf6w](https://github.com/advisories/GHSA-fm8p-53ww-hf6w) | extends | Сервис без аутентификации — Host проверяется по allowlist; совпадения Origin с Host недостаточно |

### HARD-SHADOW-API-VERSIONS — Старые версии API и недокументированные маршруты не обходят защиту (RWB-0079, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-r9ph-3637-55px](https://github.com/advisories/GHSA-r9ph-3637-55px) | extends | Устаревший маршрут доверяет описанию сущности из тела запроса - сравнить объём выдачи с актуальной операцией при подменённых атрибутах |

### HARD-UNSAFE-API-CONSUMPTION — Ответы сторонних API валидируются перед использованием (RWB-0080, багов: 3)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-542g-h47m-68v8](https://github.com/advisories/GHSA-542g-h47m-68v8) | extends | Добавить сбои на уровне соединения и протокола у внешнего узла (обрыв, не тот протокол) — не только некорректные ответы |
| [GHSA-c475-qrg2-pj4r](https://github.com/advisories/GHSA-c475-qrg2-pj4r) | extends | Тяжёлый для разбора ответ внешнего сервера (ReDoS/квадратичный парсер), а не только неверные данные |
| [GHSA-3xpg-4rpp-hhhm](https://github.com/advisories/GHSA-3xpg-4rpp-hhhm) | extends | Компрессионная бомба в ответе внешнего сервиса |

### HTTP-COMPRESSION — Сжатие ответа согласуется через Accept-Encoding (RWB-0081, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [expressjs/session#72](https://github.com/expressjs/session/issues/72) | extends | Добавить сжатие одновременно с установкой cookie сессии и проверку живости сервиса |

### INJ-FILTER-EXPRESSION — Выражения фильтрации (OData, RSQL, JSONPath, GraphQL where) не позволяют выйти за ограничения (RWB-0082, багов: 6)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-v6q3-xqxm-6f5v](https://github.com/advisories/GHSA-v6q3-xqxm-6f5v) | extends | Добавить фильтр по скрытым полям как оракул подбора секрета (без инъекции синтаксиса) |
| [GHSA-5x6v-p487-7qh2](https://github.com/advisories/GHSA-5x6v-p487-7qh2) | extends | Добавить синтаксис поисковых движков (RediSearch TAG/TEXT) и фильтры векторных хранилищ в RAG |
| [GHSA-9q4r-4842-93vw](https://github.com/advisories/GHSA-9q4r-4842-93vw) | extends | Пользовательский SQL-подобный DSL — инъекция через позиции идентификаторов (имена функций) с обходом фильтра тенанта |
| [GHSA-pj7x-6wpf-pgvp](https://github.com/advisories/GHSA-pj7x-6wpf-pgvp) | extends | Сегменты пути к вложенным полям JSON в фильтре, а не только значения |
| [GHSA-fpww-c55p-cjv6](https://github.com/advisories/GHSA-fpww-c55p-cjv6) | extends | Фильтр по скрытым полям через полиморфные связи как оракул подбора |
| [GHSA-xf65-r35x-wmmv](https://github.com/advisories/GHSA-xf65-r35x-wmmv) | extends | Параметр логического оператора (filterOperator=OR) в комбинации с обязательным серверным фильтром видимости/арендатора |

### INJ-LOG-FORGING — Пользовательские данные не позволяют подделывать записи журналов (RWB-0083, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [keycloak/keycloak#52103](https://github.com/keycloak/keycloak/issues/52103) | covered | _только пруф_: Ровно подделка записей лога через пользовательский ввод |

### INJ-NOSQL — NoSQL-инъекция операторами запросов не исполняется (RWB-0084, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-m6rx-h84q-8r95](https://github.com/advisories/GHSA-m6rx-h84q-8r95) | covered | _только пруф_ |

### INJ-OS-COMMAND — Инъекция команд ОС не исполняется (RWB-0085, багов: 3)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-hf57-cqmx-p4gr](https://github.com/advisories/GHSA-hf57-cqmx-p4gr) | extends | Без метасимволов оболочки — интерпретатор и флаг выполнения кода в разрешённых аргументах execFile |
| [GHSA-8w7q-29mw-gf5c](https://github.com/advisories/GHSA-8w7q-29mw-gf5c) | extends | Конфигурация серверного генератора/сборщика из пользовательских данных (allowlist ключей) |
| [GHSA-pqg4-j6r4-53mv](https://github.com/advisories/GHSA-pqg4-j6r4-53mv) | extends | Символы конца строки (включая U+2028/2029) в связке с # в аргументах, экранируемых библиотекой |

### INJ-PATH-TRAVERSAL — Обход каталогов через параметры файлов и путей невозможен (RWB-0086, багов: 2)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-f7v3-xhm6-w245](https://github.com/advisories/GHSA-f7v3-xhm6-w245) | extends | Директивы включения (include/snippets) в загружаемой разметке и её конфигурации |
| [GHSA-9gfj-28hw-jchp](https://github.com/advisories/GHSA-9gfj-28hw-jchp) | extends | Целевой путь переименования/перемещения (newPath) и соответствие операции требуемому праву (rename = delete) |

### INJ-PROTOTYPE-POLLUTION — Специальные ключи __proto__ и constructor не меняют поведение сервера (RWB-0087, багов: 11)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [directus/directus#28209](https://github.com/directus/directus/issues/28209) | extends | Добавить GraphQL-алиасы __proto__ (не только ключи JSON-тела) |
| [GHSA-7mx3-vvmw-hjmv](https://github.com/advisories/GHSA-7mx3-vvmw-hjmv) | extends | Добавить алиасы GraphQL как источник специальных ключей при слиянии ответов подграфов |
| [GHSA-gcgf-fh7c-8gf2](https://github.com/advisories/GHSA-gcgf-fh7c-8gf2) | extends | Подмена прототипа одного объекта запроса (без глобального загрязнения) и 5xx на ключе constructor в словарях |
| [GHSA-2mhw-wcx5-v3xj](https://github.com/advisories/GHSA-2mhw-wcx5-v3xj) | extends | Добавить пути через унаследованные методы (toString, valueOf, hasOwnProperty) в PATCH-операциях, в обход блок-листа |
| [GHSA-8hq7-ggx2-cc6m](https://github.com/advisories/GHSA-8hq7-ggx2-cc6m) | extends | Бинарные форматы сериализации (MessagePack, CBOR), не только JSON |
| [GHSA-97rh-rhh2-7vjv](https://github.com/advisories/GHSA-97rh-rhh2-7vjv) | extends | Публичные операции начальной настройки (first-register), доступные без аутентификации |
| [GHSA-r488-j9vj-wx3q](https://github.com/advisories/GHSA-r488-j9vj-wx3q) | covered | _только пруф_ |
| [GHSA-qf28-8hc6-vwrp](https://github.com/advisories/GHSA-qf28-8hc6-vwrp) | extends | Эндпоинты импорта (CSV/JSON с точечными путями в заголовках колонок) |
| [GHSA-mjw6-4jj6-33hc](https://github.com/advisories/GHSA-mjw6-4jj6-33hc) | covered | _только пруф_: Ровно эта проверка; применять и к эндпоинтам с потоковым разбором |
| [GHSA-325j-mg25-8q58](https://github.com/advisories/GHSA-325j-mg25-8q58) | extends | __proto__ в значении поля, которое сервер использует как ключ (type/id JSON:API, included), а не в имени ключа |
| [GHSA-679f-58pq-4v2c](https://github.com/advisories/GHSA-679f-58pq-4v2c) | extends | Отложенное (second-order) загрязнение из ранее сохранённых имён; ограничения только в UI проверять прямым запросом к API |

### INJ-REDOS — Пользовательский ввод не вызывает катастрофический backtracking в regex (RWB-0088, багов: 16)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-9m4w-fmjw-fvjq](https://github.com/advisories/GHSA-9m4w-fmjw-fvjq) | covered | _только пруф_ |
| [GHSA-fwh9-qg68-vxp4](https://github.com/advisories/GHSA-fwh9-qg68-vxp4) | covered | _только пруф_ |
| [GHSA-c29m-xwm3-cm6r](https://github.com/advisories/GHSA-c29m-xwm3-cm6r) | extends | data: URL и другие нестандартные схемы в параметрах с URL; заодно — ограничение допустимых схем |
| [GHSA-mghh-pgcx-3jjj](https://github.com/advisories/GHSA-mghh-pgcx-3jjj) | extends | Патологический хост в Location редиректа при server-side загрузке URL |
| [GHSA-6h2x-m376-mqjq](https://github.com/advisories/GHSA-6h2x-m376-mqjq) | extends | Поля даты/времени с длинной дробной частью секунд |
| [GHSA-jx63-h26r-8cph](https://github.com/advisories/GHSA-jx63-h26r-8cph) | extends | Пользователь задаёт сам шаблон (pathFilters), а не только данные под серверный regex |
| [GHSA-68jq-fhch-4xq4](https://github.com/advisories/GHSA-68jq-fhch-4xq4) | extends | Заголовки запроса (User-Agent), разбираемые до маршрутизации, — в том числе на несуществующих путях |
| [GHSA-2g7p-5934-q4w7](https://github.com/advisories/GHSA-2g7p-5934-q4w7) | extends | Заголовок Content-Type multipart и параметр boundary |
| [GHSA-gjj5-9665-rwrc](https://github.com/advisories/GHSA-gjj5-9665-rwrc) | extends | ReDoS при анализе содержимого файла (заголовок SVG/изображения), в том числе скачанного по URL, а не только в полях запроса |
| [GHSA-prgh-xp8r-p3m5](https://github.com/advisories/GHSA-prgh-xp8r-p3m5) | extends | email-адреса и почтовые заголовки (комментарии RFC 5322, длинные строки без '@') — квадратичный парсер, а не только regex |
| [GHSA-q2hr-2g5m-vwhr](https://github.com/advisories/GHSA-q2hr-2g5m-vwhr) | extends | glob/brace-шаблоны в параметрах поиска — квадратичное раскрытие, а не regex |
| [GHSA-v53p-9fqp-m79j](https://github.com/advisories/GHSA-v53p-9fqp-m79j) | extends | _только пруф_: Тот же вариант, что GHSA-prgh-xp8r-p3m5: email-адреса — добавить формы без '@' и с '@' на краю |
| [GHSA-253c-mchw-3w2r](https://github.com/advisories/GHSA-253c-mchw-3w2r) | extends | Рендеринг Markdown/разметки пользователя (автоссылки) — квадратичный разбор, а не regex |
| [GHSA-f67j-2jqw-jpq7](https://github.com/advisories/GHSA-f67j-2jqw-jpq7) | extends | Незавершённая HTML-разметка в контенте с серверным разбором — зависание парсера, не regex |
| [GHSA-9rgm-9g3h-6x36](https://github.com/advisories/GHSA-9rgm-9g3h-6x36) | extends | Сверхлинейный разбор сериализованного формата (индексы вне границ), не только регулярные выражения |
| [GHSA-jgm3-qmp2-c4p7](https://github.com/advisories/GHSA-jgm3-qmp2-c4p7) | extends | Оператор фильтра, принимающий сырой regex от клиента; проверять на каждом драйвере БД/окружении |

### INJ-SQL — SQL-инъекция во входных параметрах не исполняется (RWB-0089, багов: 5)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-r3rv-jm3r-62q2](https://github.com/advisories/GHSA-r3rv-jm3r-62q2) | extends | Добавить нагрузки, рассчитанные на экранирование обратным слэшем (\\'), — ломаются при режиме удвоения кавычек |
| [GHSA-v6pj-gxxw-phfw](https://github.com/advisories/GHSA-v6pj-gxxw-phfw) | extends | Инъекция в имени поля (ключе JSON), а не в значении; связано с REST-MASS-ASSIGNMENT |
| [GHSA-r223-96jv-q533](https://github.com/advisories/GHSA-r223-96jv-q533) | extends | Инъекция в имени поля сортировки (ORDER BY не параметризуется); связано с REST-SORT-INVALID-FIELD |
| [GHSA-v49j-62m6-pgrr](https://github.com/advisories/GHSA-v49j-62m6-pgrr) | extends | Имена полей, операторы и join-параметры динамических фильтров (зависит от адаптера БД) |
| [GHSA-wmw4-mw6x-6vfm](https://github.com/advisories/GHSA-wmw4-mw6x-6vfm) | extends | Инъекция в имена параметров/полей фильтра, а не только в значения |

### INJ-SSRF-PARAMETERS — Параметры с URL и хостами не дают доступа к внутренней сети (RWB-0090, багов: 11)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-q8hw-4fvp-9rwv](https://github.com/advisories/GHSA-q8hw-4fvp-9rwv) | extends | URL спрятан в base64/JSON сегменте пути; слепой SSRF с побочным каналом через статус ответа |
| [GHSA-2h44-8472-frjj](https://github.com/advisories/GHSA-2h44-8472-frjj) | extends | Адрес задаётся заголовком запроса, сервер прикладывает к исходящему вызову свои учётные данные |
| [GHSA-q38j-6vcm-2f5m](https://github.com/advisories/GHSA-q38j-6vcm-2f5m) | extends | URL приходит не из параметра запроса, а из конфигурации в пользовательском источнике (манифест, репозиторий) |
| [GHSA-g734-fhp4-7mfp](https://github.com/advisories/GHSA-g734-fhp4-7mfp) | extends | Параметр базового URL сторонней интеграции - проверять не только доступ к внутренней сети, но и утечку серверного токена интеграции на подконтрольный внешний адрес |
| [keycloak/keycloak#52167](https://github.com/keycloak/keycloak/issues/52167) | extends | Хост/адрес проверяется по allowlist уже на эндпоинте регистрации (запись), а не только там, где его потом используют |
| [GHSA-pcmq-25r3-5w9v](https://github.com/advisories/GHSA-pcmq-25r3-5w9v) | extends | allowlist типов/схем источника должен применяться и при фоновой обработке, и для ссылок, найденных внутри принятого источника |
| [GHSA-xvq9-wjp8-hwqf](https://github.com/advisories/GHSA-xvq9-wjp8-hwqf) | extends | Код языка/локали, подставляемый в шаблон URL серверной загрузки |
| [GHSA-6mwv-4mrm-5p3m](https://github.com/advisories/GHSA-6mwv-4mrm-5p3m) | extends | Фрагмент хоста (регион, поддомен) из параметра — символы '#', ':', '/', '@' и утечка пересылаемых учётных данных |
| [GHSA-798p-78g2-v556](https://github.com/advisories/GHSA-798p-78g2-v556) | extends | Доменное имя, резолвящееся во внутренний/метаданных адрес (wildcard-DNS), — не только IP-литералы |
| [GHSA-65h7-9wrw-629c](https://github.com/advisories/GHSA-65h7-9wrw-629c) | extends | Вложенные ссылки в загружаемых документах ($ref) и записи IPv4-mapped IPv6, DNS-имена, редиректы |
| [GHSA-f6mr-pjwc-34m4](https://github.com/advisories/GHSA-f6mr-pjwc-34m4) | extends | Расхождение парсеров URL — Unicode-пробелы (U+00A0, U+FEFF) перед // превращают относительный путь в внешний хост |

### INJ-TEMPLATE-SSTI — Инъекция в серверные шаблоны не исполняется (RWB-0091, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-8r5x-fm3f-whwj](https://github.com/advisories/GHSA-8r5x-fm3f-whwj) | extends | Добавить подмену типа: объект вместо строки шаблона |

### OBS-AUDIT-TRAIL — Чувствительные действия фиксируются в журнале аудита (RWB-0092, багов: 3)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [keycloak/keycloak#52568](https://github.com/keycloak/keycloak/issues/52568) | extends | Добавить отказы на всех ветках проверок выдачи токена, а не только успешные действия |
| [keycloak/keycloak#52257](https://github.com/keycloak/keycloak/issues/52257) | extends | Несколько событий в одном запросе — проверить, что тип и детали каждого не перезаписаны |
| [directus/directus#26242](https://github.com/directus/directus/issues/26242) | extends | Добавить матрицу ролей (включая администратора тенанта) и путей загрузки при проверке инициатора в событиях |

### OBS-HEALTH-ENDPOINTS — Health-эндпоинты отражают состояние и не раскрывают детали (RWB-0093, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [nestjs/nest#11442](https://github.com/nestjs/nest/issues/11442) | extends | Доступность health без аутентификации при глобальном префиксе/версии и что исключение не расширяется на соседние маршруты |

### PAGE-SEARCH-SPECIAL-CHARS — Поиск со спецсимволами и wildcard не ломается и не расширяет выборку (RWB-0094, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [keycloak/keycloak#50228](https://github.com/keycloak/keycloak/issues/50228) | extends | Добавить значения с обратным слэшем в конце и незакрытыми экранированными кавычками в синтаксисе key:value |

### PAGE-TOTAL-COUNT — Общее число элементов согласовано с суммой страниц (RWB-0095, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [directus/directus#26768](https://github.com/directus/directus/issues/26768) | extends | Число записей больше лимита по умолчанию, агрегат количества через GraphQL и REST совпадает с реальным |

### PERF-LATENCY-BASELINE — Задержка ключевых операций в пределах SLO при обычной нагрузке (RWB-0096, багов: 2)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [keycloak/keycloak#51554](https://github.com/keycloak/keycloak/issues/51554) | extends | Добавить замер задержки при росте объёма данных (тенанты, роли) и сравнение с предыдущей версией — ловит регрессии сложности |
| [keycloak/keycloak#51531](https://github.com/keycloak/keycloak/issues/51531) | extends | Добавить замер при росте числа ролей; проверять все варианты эндпоинта (realm и client) — фикс одного не гарантирует другой |

### PERF-PAYLOAD-SIZE — Размер ответов разумен и не растёт неограниченно (RWB-0097, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [strapi/strapi#27393](https://github.com/strapi/strapi/issues/27393) | extends | Добавить списки с крупными объектами и сортировкой (500 от СУБД) |

### PRIV-DATA-MASKING — Чувствительные данные маскируются в ответах по политике (RWB-0098, багов: 2)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [keycloak/keycloak#52792](https://github.com/keycloak/keycloak/issues/52792) | extends | Добавить обратную сторону: избыточное маскирование несекретных полей и read-modify-write с маской |
| [GHSA-p795-mqf2-36mf](https://github.com/advisories/GHSA-p795-mqf2-36mf) | extends | Обойти все пути получения одного и того же чувствительного объекта (и эквивалентные пользовательские типы) и сравнить маскирование |

### REQ-CROSS-CLIENT-CONSISTENCY — Одно правило продукта одинаково в API разных клиентов (RWB-0099, багов: 5)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [strapi/strapi#27447](https://github.com/strapi/strapi/issues/27447) | extends | Одна сущность через разные эндпоинты и протоколы, сравнение полей и связей |
| [keycloak/keycloak#53117](https://github.com/keycloak/keycloak/issues/53117) | extends | Добавить сравнение одной сущности в разных версиях API |
| [directus/directus#26703](https://github.com/directus/directus/issues/26703) | extends | Добавить сравнение REST и GraphQL одного продукта на агрегатах с группировкой по функциям |
| [directus/directus#27844](https://github.com/directus/directus/issues/27844) | extends | Разные транспорты одного API (REST и WebSocket) — валидация параметров должна совпадать |
| [keycloak/keycloak#49457](https://github.com/keycloak/keycloak/issues/49457) | extends | Разные пути создания одного объекта (админ-API, регистрация, метаданные) — одинаковые политики |

### RES-BULK-LIMITS — Массовые операции соблюдают лимиты и сообщают о каждом элементе (RWB-0100, багов: 3)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [directus/directus#27863](https://github.com/directus/directus/issues/27863) | extends | Добавить дубликаты и несуществующие ID в массовой операции и сравнение поведения ролей |
| [directus/directus#27514](https://github.com/directus/directus/issues/27514) | extends | Пустой список ключей не означает «все записи» |
| [directus/directus#26754](https://github.com/directus/directus/issues/26754) | extends | Добавить пустой список в массовой операции и сравнение ответа для разных ролей |

### RES-CREATE-RESPONSE-MATCHES-READ — Ответ на создание и изменение совпадает с последующим чтением (RWB-0101, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [strapi/strapi#26606](https://github.com/strapi/strapi/issues/26606) | extends | Поле-связь, заданное альтернативным идентификатором, на нестандартном эндпоинте ресурса — 200 без применения |

### RES-DELETE-WITH-DEPENDENTS — Удаление ресурса с зависимыми объектами выполняется по правилам каскада (RWB-0102, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [keycloak/keycloak#51589](https://github.com/keycloak/keycloak/issues/51589) | extends | Добавить проверку зависимых операций после удаления (выдача токена, вычисление прав), в том числе при закэшированной конфигурации |

### RES-IMMUTABLE-FIELDS — Неизменяемые поля нельзя изменить после создания (RWB-0103, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [directus/directus#28131](https://github.com/directus/directus/issues/28131) | extends | Добавить служебные поля синглтона настроек |

### RES-REFERENTIAL-INTEGRITY — Ссылка на несуществующий или чужой связанный ресурс отклоняется (RWB-0104, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [keycloak/keycloak#50178](https://github.com/keycloak/keycloak/issues/50178) | extends | Обе ссылки существуют, но не связаны между собой; интерфейс ограничивает выбор, API — нет (см. REQ-CROSS-CLIENT-CONSISTENCY) |

### RES-SERVER-GENERATED-FIELDS — Клиент не может задать серверные поля (id, createdAt, status, version) (RWB-0105, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [directus/directus#28207](https://github.com/directus/directus/issues/28207) | extends | Добавить путь загрузки файла (multipart) и повторную внутреннюю запись |

### RES-TIMESTAMPS — Метки времени создания и изменения ведут себя корректно (RWB-0106, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [directus/directus#28042](https://github.com/directus/directus/issues/28042) | extends | Добавить проверку меток времени для всех альтернативных путей создания (resumable-загрузка и др.) |

### RESIL-DEPENDENCY-DOWN — Недоступность зависимости даёт контролируемую ошибку (RWB-0107, багов: 7)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [strapi/strapi#27374](https://github.com/strapi/strapi/issues/27374) | extends | Добавить проверку живости сервиса сразу после отказа зависимости |
| [directus/directus#27412](https://github.com/directus/directus/issues/27412) | extends | Ошибка зависимости не маппится в 403/404 (ложный отказ в доступе) |
| [keycloak/keycloak#51352](https://github.com/keycloak/keycloak/issues/51352) | extends | Зависимость отключена в конфигурации (а не упала) — контролируемая ошибка |
| [keycloak/keycloak#51268](https://github.com/keycloak/keycloak/issues/51268) | extends | Явно проверять, что при недоступном хранилище списки не возвращают 200 с пустыми данными |
| [nestjs/nest#10681](https://github.com/nestjs/nest/issues/10681) | extends | Отказ зависимости после отправки заголовков потокового ответа — проверить живость сервиса после |
| [nestjs/nest#9363](https://github.com/nestjs/nest/issues/9363) | extends | Добавить фазу восстановления: после возврата зависимости сервис переподключается без своего перезапуска |
| [nestjs/nest#288](https://github.com/nestjs/nest/issues/288) | covered | _только пруф_: Ровно недоступность зависимости |

### RESIL-GRACEFUL-SHUTDOWN — Перезапуск экземпляра не обрывает выполняющиеся запросы (RWB-0108, багов: 2)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [directus/directus#27961](https://github.com/directus/directus/issues/27961) | extends | Добавить негрейсфул остановку (SIGKILL, OOM) с удерживаемой распределённой блокировкой |
| [nestjs/nest#13910](https://github.com/nestjs/nest/issues/13910) | extends | Долгие соединения разных типов не блокируют остановку |

### RESIL-PARTIAL-DEGRADATION — Отказ некритичной зависимости не ломает основной функционал (RWB-0109, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [strapi/strapi#27245](https://github.com/strapi/strapi/issues/27245) | extends | Добавить отключённый модуль/фичу лицензии и проверку всех операций CRUD, а не только create |

### REST-ASYNC-202 — Асинхронное принятие задачи 202 (RWB-0110, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [directus/directus#27854](https://github.com/directus/directus/issues/27854) | extends | Добавить загрузку большого тела через прокси: ответ 202 только после приёма тела, задача завершается |

### REST-CACHE-CONDITIONAL-GET — ETag/Last-Modified conditional GET (RWB-0111, багов: 3)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [expressjs/express#7365](https://github.com/expressjs/express/issues/7365) | extends | HEAD и QUERY с If-None-Match дают 304 так же, как GET |
| [expressjs/express#2749](https://github.com/expressjs/express/issues/2749) | extends | Проверить набор заголовков в 304 (Trailer, заголовки тела) |
| [expressjs/express#2667](https://github.com/expressjs/express/issues/2667) | extends | Коллизия ETag у разных тел одинаковой длины |

### REST-CORS-POLICY — Политика CORS (RWB-0112, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [nestjs/nest#3939](https://github.com/nestjs/nest/issues/3939) | covered | _только пруф_: Ровно эта проверка; регрессия после обновления |

### REST-DATE-TIME-TZ — Дата, время и timezone (RWB-0113, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [directus/directus#28254](https://github.com/directus/directus/issues/28254) | extends | Добавить даты на границе года и функции над датами в фильтре и сортировке |

### REST-DUPLICATE-UNIQUE-KEY — Дублирование уникального ключа (RWB-0114, багов: 2)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [directus/directus#27986](https://github.com/directus/directus/issues/27986) | extends | Добавить ложный конфликт: обновление с собственными значениями уникального (составного) ключа |
| [directus/directus#26997](https://github.com/directus/directus/issues/26997) | extends | Обновление со своим же уникальным значением и корректный код при конфликте |

### REST-EMPTY-VALUES — Пустые объект, массив и строка (RWB-0115, багов: 2)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [expressjs/express#5959](https://github.com/expressjs/express/issues/5959) | extends | Полностью пустое тело при JSON Content-Type |
| [keycloak/keycloak#50039](https://github.com/keycloak/keycloak/issues/50039) | extends | Пустые и пробельные строки как элементы массива; неверный статус 409 вместо 400 |

### REST-ENUM-VALUES — Допустимые и неизвестные enum (RWB-0116, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [keycloak/keycloak#50362](https://github.com/keycloak/keycloak/issues/50362) | extends | Неподдерживаемое значение внутри списка — отклонить запрос или отбросить элемент, по документации |

### REST-ERROR-SCHEMA — Стабильная схема ошибок (RWB-0117, багов: 2)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [nestjs/nest#4319](https://github.com/nestjs/nest/issues/4319) | extends | Регрессия схемы ошибок после обновления фреймворка — снимок ошибок до/после |
| [nestjs/nest#431](https://github.com/nestjs/nest/issues/431) | extends | Ошибки промежуточных слоёв (middleware, guard, прокси) — та же схема, что у ошибок обработчика |

### REST-FILTER-SORT-COMPOSITION — Filtering and sorting compose correctly (RWB-0118, багов: 2)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [strapi/strapi#26746](https://github.com/strapi/strapi/issues/26746) | extends | Добавить сортировку по вычисляемым полям при фильтре по связи (DISTINCT) и проверку на разных СУБД |
| [strapi/strapi#26359](https://github.com/strapi/strapi/issues/26359) | extends | Сортировка на уровне раскрываемой связи вместе с сортировкой верхнего уровня |

### REST-FILTER-SORT-PAGINATION — Комбинация filter/sort/pagination (RWB-0119, багов: 4)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [strapi/strapi#26577](https://github.com/strapi/strapi/issues/26577) | extends | Пустые значения sort и ручной порядок связей при пагинации |
| [strapi/strapi#26550](https://github.com/strapi/strapi/issues/26550) | extends | _только пруф_: Тот же вариант, что strapi#26577 (пустой sort), для связей во вложенных компонентах |
| [strapi/strapi#26465](https://github.com/strapi/strapi/issues/26465) | extends | _только пруф_: Тот же корень, что strapi#26577/26550 (пустой sort): вариант для повторяемых вложенных компонентов |
| [strapi/strapi#26426](https://github.com/strapi/strapi/issues/26426) | extends | Исходный баг серии strapi#26577/26550/26465 — пруф к тому же варианту |

### REST-HEAD-GET-CONSISTENCY — HEAD response is consistent with GET (RWB-0120, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [nestjs/nest#14016](https://github.com/nestjs/nest/issues/14016) | covered | _только пруф_: Ровно эта проверка |

### REST-MASS-ASSIGNMENT — Mass assignment защищённых полей (RWB-0121, багов: 4)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [keycloak/keycloak#52488](https://github.com/keycloak/keycloak/issues/52488) | extends | Добавить служебные флаги защиты, снятие которых отключает другие проверки |
| [GHSA-4ww4-68q3-h7g5](https://github.com/advisories/GHSA-4ww4-68q3-h7g5) | extends | Добавить варианты: точечные пути и операторы хранилища, обход полевых прав на конкретном бэкенде хранения |
| [GHSA-fx49-4h83-wjv9](https://github.com/advisories/GHSA-fx49-4h83-wjv9) | extends | Учётные поля (password) в общем эндпоинте изменения пользователя при полевом запрете |
| [GHSA-vmjq-hvgq-2wv4](https://github.com/advisories/GHSA-vmjq-hvgq-2wv4) | extends | Глобальные флаги безопасности в объекте настроек и проверка последствий для доступа |

### REST-NULL-VS-OMITTED — Null и отсутствующее поле (RWB-0122, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [keycloak/keycloak#51527](https://github.com/keycloak/keycloak/issues/51527) | extends | Явный null для секрета/служебного поля в PATCH запускает побочную операцию (перегенерацию) - проверить, что она идёт через те же правила, что и штатная операция |

### REST-NUMERIC-BOUNDARIES — Числовые границы (RWB-0123, багов: 2)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [keycloak/keycloak#52491](https://github.com/keycloak/keycloak/issues/52491) | extends | Добавить переполнение в арифметике времени (метка времени + длительность) для параметров срока |
| [directus/directus#26448](https://github.com/directus/directus/issues/26448) | extends | Добавить числа больше 2^53 и с высокой точностью в полях с правилами валидации |

### REST-OBJECT-LEVEL-AUTHZ — Object-level authorization (RWB-0124, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-g7fw-3gjp-g5hf](https://github.com/advisories/GHSA-g7fw-3gjp-g5hf) | extends | Добавить параметр цели в действиях бота/агента (каналы, комнаты) и проверку каждого действия чтения метаданных |

### REST-OPEN-REDIRECT — Валидация redirect URL (RWB-0125, багов: 4)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [expressjs/express#6614](https://github.com/expressjs/express/issues/6614) | extends | Добавить опасные схемы (javascript:, data:) |
| [keycloak/keycloak#51712](https://github.com/keycloak/keycloak/issues/51712) | extends | Параметры внутри redirect URI и кодированные имена параметров (регрессия от защитного фикса) |
| [GHSA-2m6q-8v3h-jqww](https://github.com/advisories/GHSA-2m6q-8v3h-jqww) | extends | Редирект на внутренний маршрут, где пользовательское значение — сегмент пути; проверить scheme-relative '//host' |
| [GHSA-w84c-53h3-mc2g](https://github.com/advisories/GHSA-w84c-53h3-mc2g) | covered | _только пруф_: Ровно эта проверка |

### REST-PAGINATION-LIMITS — Границы размера страницы (RWB-0126, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [keycloak/keycloak#52033](https://github.com/keycloak/keycloak/issues/52033) | extends | Проверка целостности тела (обрезанный JSON при статусе 200) при огромном max |

### REST-PATCH-PARTIAL-UPDATE — Семантика PATCH (RWB-0127, багов: 2)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [directus/directus#27877](https://github.com/directus/directus/issues/27877) | extends | Добавить удаление вложенного свойства в diff/patch, которое не должно трактоваться как удаление объекта |
| [keycloak/keycloak#51213](https://github.com/keycloak/keycloak/issues/51213) | extends | null удаляет поле, PUT без поля очищает его; проверять фактическое применение для атрибутов безопасности |

### REST-POST-LOCATION — Location при создании (RWB-0128, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [expressjs/express#5602](https://github.com/expressjs/express/issues/5602) | extends | Добавить вариант с IDN-доменом и не-ASCII путём в Location |

### REST-READONLY-WRITEONLY — Поля readOnly/writeOnly (RWB-0129, багов: 3)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [keycloak/keycloak#52173](https://github.com/keycloak/keycloak/issues/52173) | extends | Вычисляемые значения внутри свободной карты атрибутов и round-trip GET→PUT |
| [keycloak/keycloak#49272](https://github.com/keycloak/keycloak/issues/49272) | extends | Отсутствие read-only поля в запросе на изменение не должно давать ошибку |
| [keycloak/keycloak#48868](https://github.com/keycloak/keycloak/issues/48868) | extends | Обновление ресурса без writeOnly-секрета (тело из GET, где секрет не отдаётся) сохраняет прежний секрет; проверить аутентификацией по нему, в том числе на мигрированных данных |

### REST-REQUEST-SIZE-LIMIT — Лимит размера тела (RWB-0130, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [nestjs/nest#14734](https://github.com/nestjs/nest/issues/14734) | extends | Добавить сочетание лимитов по маршрутам: особый лимит не ломает разбор тела на других |

### REST-REQUIRED-PARAM-MISSING — Отсутствует обязательный параметр (RWB-0131, багов: 2)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [keycloak/keycloak#52076](https://github.com/keycloak/keycloak/issues/52076) | extends | Отсутствуют все поля сразу - пустой POST и GET на URL действия формы; ответ должен быть валидационным, а не общей ошибкой |
| [nestjs/nest#5688](https://github.com/nestjs/nest/issues/5688) | extends | Прогон по всем эндпоинтам, включая сгенерированные/унаследованные, где валидация может быть молча отключена |

### REST-SECURITY-HEADERS — Защитные HTTP-заголовки (RWB-0132, багов: 3)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [nestjs/nest#13401](https://github.com/nestjs/nest/issues/13401) | extends | Проверять наличие заголовков и других следов глобальных middleware на всех группах маршрутов, включая исключённые из глобального префикса и служебные |
| [nestjs/nest#13093](https://github.com/nestjs/nest/issues/13093) | extends | Проверять заголовки и другие следы middleware во всех версиях API (вместе с вариантом про исключения из глобального префикса) |
| [nestjs/nest#972](https://github.com/nestjs/nest/issues/972) | extends | Регистрация middleware шаблоном на все маршруты и под альтернативным HTTP-сервером |

### REST-SENSITIVE-DATA — Отсутствие чувствительных данных в ответах (RWB-0133, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [keycloak/keycloak#52197](https://github.com/keycloak/keycloak/issues/52197) | extends | Маскирование секрета зависит от роли и должно совпадать между версиями API |

### REST-SORT-INVALID-FIELD — Сортировка по неизвестному полю (RWB-0134, багов: 2)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-53vv-xm9f-mm82](https://github.com/advisories/GHSA-53vv-xm9f-mm82) | extends | Добавить сортировку по существующему, но скрытому полю как оракул, включая алиасы, суффиксы и составные выражения |
| [GHSA-9g87-32v6-3c2r](https://github.com/advisories/GHSA-9g87-32v6-3c2r) | extends | Сортировка по существующему, но закрытому полевыми правами полю — отклонять как неизвестное |

### REST-SSRF-URL-FETCH — Контроль server-side URL fetch (RWB-0135, багов: 13)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-322m-ff4g-9vx9](https://github.com/advisories/GHSA-322m-ff4g-9vx9) | extends | Добавить DNS rebinding (TOCTOU) |
| [GHSA-r7f2-6fj8-6fg2](https://github.com/advisories/GHSA-r7f2-6fj8-6fg2) | extends | Добавить переходные IPv6 и сокращённую запись IPv4 |
| [GHSA-4233-jc72-56c5](https://github.com/advisories/GHSA-4233-jc72-56c5) | extends | Обход allow-list — разрешённый хост в пути/query/поддомене |
| [GHSA-r4gj-5m52-g5wh](https://github.com/advisories/GHSA-r4gj-5m52-g5wh) | extends | Добавить вариант с редиректом: внешний URL отвечает 3xx на внутренний адрес; проверка не должна ограничиваться исходным URL |
| [GHSA-3pq3-5fj3-cg6v](https://github.com/advisories/GHSA-3pq3-5fj3-cg6v) | extends | Добавить вариант транспорта: цель с HTTP/2 и имя, разрешающееся во внутренний адрес — защита не должна зависеть от версии протокола |
| [GHSA-cjq9-62q9-8jv4](https://github.com/advisories/GHSA-cjq9-62q9-8jv4) | extends | Хост из allowlist с DNS на внутренний адрес (DNS rebinding) — проверять IP после резолва |
| [GHSA-pj5h-5q6c-3pfx](https://github.com/advisories/GHSA-pj5h-5q6c-3pfx) | extends | Утечка учётных данных пользователя в исходящий запрос и повторная проверка адреса при редиректе |
| [GHSA-qgvj-qcf8-xq73](https://github.com/advisories/GHSA-qgvj-qcf8-xq73) | extends | URL из директив внутри содержимого, разрешаемых сервером с его учётными данными, — ограничение тем же источником |
| [GHSA-m62c-5q34-f3cf](https://github.com/advisories/GHSA-m62c-5q34-f3cf) | extends | Обход allowlist префиксом пути без границы сегмента в прокси с учётными данными сервера |
| [GHSA-rpw4-54j3-4h4q](https://github.com/advisories/GHSA-rpw4-54j3-4h4q) | extends | link-local IPv6 вне fe80::/64 (весь fe80::/10) |
| [GHSA-2vr4-cq9g-pvrc](https://github.com/advisories/GHSA-2vr4-cq9g-pvrc) | extends | NAT64 local-use 64:ff9b:1::/48 (в дополнение к ::ffff:0:0/96 и 64:ff9b::/96) |
| [GHSA-cmhj-wh2f-9cgx](https://github.com/advisories/GHSA-cmhj-wh2f-9cgx) | extends | _только пруф_: Тот же вариант, что в прежних партиях: DNS rebinding — проверка в момент подключения; здесь через вложение image_url в LLM-запросе |
| [GHSA-q5wm-mgqx-fv2f](https://github.com/advisories/GHSA-q5wm-mgqx-fv2f) | extends | Исходящие запросы с учётными данными сервера — назначение ограничено origin интеграции, и после редиректа тоже |

### REST-STATUS-CODE-CONTRACT — Статус ответа соответствует контракту (RWB-0136, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [nestjs/nest#2360](https://github.com/nestjs/nest/issues/2360) | extends | Эндпоинты-перенаправления — проверять код 3xx и Location, без автоматического следования редиректам |

### REST-STRING-LENGTH-BOUNDARIES — Границы длины строки (RWB-0137, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [keycloak/keycloak#50903](https://github.com/keycloak/keycloak/issues/50903) | extends | Поле логина без лимита длины на неаутентифицированном эндпоинте — усиление записи в логи |

### REST-TYPE-MISMATCH — Несовпадение типа поля (RWB-0138, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-48qf-xh34-q73r](https://github.com/advisories/GHSA-48qf-xh34-q73r) | extends | Массивоподобный объект ({length: N}) или строка на месте вложенного массива; проверить прочитанное значение |

### REST-UNKNOWN-FIELDS — Политика неизвестных полей (RWB-0139, багов: 2)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [nestjs/nest#8066](https://github.com/nestjs/nest/issues/8066) | extends | При политике «отбросить неизвестные» проверить, что объявленные вложенные объекты и их поля сохраняются (сравнить отправленное и прочитанное) |
| [nestjs/nest#417](https://github.com/nestjs/nest/issues/417) | covered | _только пруф_: Ровно политика неизвестных полей |

### REST-UNSUPPORTED-CONTENT-TYPE — Неподдерживаемый Content-Type запроса (RWB-0140, багов: 2)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [nestjs/nest#15022](https://github.com/nestjs/nest/issues/15022) | extends | Добавить синтаксически неверный media type и проверку схемы тела ошибки, а не только статуса |
| [keycloak/keycloak#49964](https://github.com/keycloak/keycloak/issues/49964) | extends | Синтаксически некорректный (а не просто неподдерживаемый) Content-Type и пустое значение |

### REST-VALIDATION-ATOMICITY — Атомарность ошибки валидации (RWB-0141, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [strapi/strapi#26674](https://github.com/strapi/strapi/issues/26674) | extends | Добавить проверку после сохранения файла (тип, размер > 2 ГиБ): ошибка не должна оставлять ресурс |

### SEC-AUTHN-MALFORMED — Malformed credential is rejected (RWB-0142, багов: 3)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [jshttp/cookie#35](https://github.com/jshttp/cookie/issues/35) | extends | Добавить синтаксически битый и пустой заголовок Cookie и вариант для WebSocket-рукопожатия |
| [keycloak/keycloak#50791](https://github.com/keycloak/keycloak/issues/50791) | extends | Basic без части с паролем или с пустым секретом |
| [keycloak/keycloak#49969](https://github.com/keycloak/keycloak/issues/49969) | extends | Добавить варианты заголовка JWT без alg, с alg=null и пустым объектом (не только alg=none из AUTH-JWT-ALG-NONE) |

### SEC-AUTHN-MISSING — Protected operation rejects missing credentials (RWB-0143, багов: 4)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-6wjp-v33h-5cvq](https://github.com/advisories/GHSA-6wjp-v33h-5cvq) | covered | _только пруф_: CORS — REST-CORS-POLICY |
| [GHSA-472h-9c5j-prrr](https://github.com/advisories/GHSA-472h-9c5j-prrr) | extends | Защищённый путь под публичным префиксом — правила по самому длинному совпадению |
| [GHSA-59h8-w5q6-mfmp](https://github.com/advisories/GHSA-59h8-w5q6-mfmp) | extends | Маршруты совместимости со старыми клиентами и ingest-эндпоинты (стримы, события) — проверять так же, как основные; вместе с предсказуемыми ID |
| [GHSA-x5c9-v98j-722r](https://github.com/advisories/GHSA-x5c9-v98j-722r) | extends | Проверка без учётных данных через каждый путь развёртывания (прокси, балансировщик) — исключения для loopback/внутренних адресов не должны срабатывать на внешний трафик |

### SEC-AUTHZ-ASYNC-JOB — Authorization is rechecked for asynchronous job access (RWB-0144, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-7hfw-grcm-cqm6](https://github.com/advisories/GHSA-7hfw-grcm-cqm6) | extends | Эндпоинт списка задач, а не только чтение отдельной задачи |

### SEC-AUTHZ-CACHE-ISOLATION — Authorization context is respected by caches (RWB-0145, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-2jfj-6hjv-fm6j](https://github.com/advisories/GHSA-2jfj-6hjv-fm6j) | extends | Set-Cookie в кэшируемом ответе — проверять двумя пользователями через общий кэш |

### SEC-AUTHZ-FUNCTION — User without required permission cannot invoke operation (RWB-0146, багов: 3)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [keycloak/keycloak#52753](https://github.com/keycloak/keycloak/issues/52753) | extends | Добавить позитивную сторону матрицы прав: минимальная достаточная роль получает полный ответ, вложенные коллекции не отфильтровываются молча при 200; сравнивать с ответом полной учётки и прежней версией |
| [nestjs/nest#879](https://github.com/nestjs/nest/issues/879) | extends | Маршруты из базовых/общих обработчиков — проверять каждый отдельно, а не по одному представителю |
| [GHSA-88h9-xgvx-hvf2](https://github.com/advisories/GHSA-88h9-xgvx-hvf2) | extends | Имена методов/маршрутов с общим префиксом и разным регистром при правилах по имени |

### SEC-AUTHZ-METHOD-MATRIX — Authorization is enforced for every method (RWB-0147, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-pp95-gc86-jq6q](https://github.com/advisories/GHSA-pp95-gc86-jq6q) | extends | action-обработчик формы (POST) на маршруте с защищённым GET |

### SEC-BOLA-BULK — Bulk endpoint enforces ownership per item (RWB-0148, багов: 2)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [directus/directus#28161](https://github.com/directus/directus/issues/28161) | extends | Добавить аутентификацию массового варианта (не только владение по элементам) |
| [GHSA-5ffh-6f9q-5hhr](https://github.com/advisories/GHSA-5ffh-6f9q-5hhr) | extends | Операции порядка/сортировки и привязки со списком ID в теле при проверке прав по родителю из пути; сверять все «соседние» операции одного ресурса |

### SEC-OWNERSHIP-DELETE — User cannot delete another owner’s resource (RWB-0149, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-x3mg-q38v-m562](https://github.com/advisories/GHSA-x3mg-q38v-m562) | covered | _только пруф_: Ровно проверка удаления чужого ресурса |

### SEC-OWNERSHIP-READ — User cannot read another owner’s resource (RWB-0150, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-8xcj-9hfr-fh9j](https://github.com/advisories/GHSA-8xcj-9hfr-fh9j) | extends | Косвенное чтение через clone/copy/duplicate — права проверяются и на источник, а не только на место назначения |

### SEC-OWNERSHIP-REFERENCE-INDIRECT — Indirect resource references preserve authorization (RWB-0151, багов: 6)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-6q6j-f24j-p477](https://github.com/advisories/GHSA-6q6j-f24j-p477) | extends | Добавить ссылку на скрытый объект при создании, после которой ответ раскрывает его фрагмент (snippet) |
| [keycloak/keycloak#51061](https://github.com/keycloak/keycloak/issues/51061) | extends | Косвенная ссылка через параметр scope в запросе токена — данные цели раскрываются в claims |
| [GHSA-4qpv-39hg-f7fx](https://github.com/advisories/GHSA-4qpv-39hg-f7fx) | extends | Вспомогательный эндпоинт с параметрами collection+id вызывает внутренний API без проверки доступа |
| [GHSA-7c34-32v3-j575](https://github.com/advisories/GHSA-7c34-32v3-j575) | extends | Раскрытие связи и фильтр по полям связанной коллекции с условными правами чтения |
| [GHSA-72h8-wp98-7hch](https://github.com/advisories/GHSA-72h8-wp98-7hch) | extends | Несоответствие родителя в пути и фактического владельца вложенного объекта (projectId из пути игнорируется); плюс права, проверяемые в обработчике, а не на маршруте — проверять каждую такую операцию пользователем без права |
| [GHSA-pq6c-vh67-xpm3](https://github.com/advisories/GHSA-pq6c-vh67-xpm3) | extends | Ссылка на секрет/учётные данные по ID в конфигурации, которую сервер использует при отправке наружу |

### SEC-OWNERSHIP-UPDATE — User cannot modify another owner’s resource (RWB-0152, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-f7hx-52q9-hcrf](https://github.com/advisories/GHSA-f7hx-52q9-hcrf) | extends | Вспомогательные операции (reorder/move), меняющие поля документа в обход основного update |

### SEC-ROLE-SELF-ASSIGN — User cannot grant self a higher role (RWB-0153, багов: 2)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-4pvx-fwjj-8gpc](https://github.com/advisories/GHSA-4pvx-fwjj-8gpc) | extends | Добавить назначение своей и более высокой роли другим пользователям, а не только себе |
| [GHSA-p96c-xwx8-3cqj](https://github.com/advisories/GHSA-p96c-xwx8-3cqj) | extends | Самоназначение членства в арендаторах (поле массива), а не роли |

### SEC-SCOPE-EXTRA-UNTRUSTED — Client cannot add scopes by request parameter (RWB-0154, багов: 3)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [keycloak/keycloak#52785](https://github.com/keycloak/keycloak/issues/52785) | extends | Добавить проверку по всем grant-типам, включая device flow, и единообразие ошибки invalid_scope |
| [keycloak/keycloak#49952](https://github.com/keycloak/keycloak/issues/49952) | extends | Позитивный вариант для token exchange: разрешённый scope выдаётся, неразрешённый — нет |
| [keycloak/keycloak#49388](https://github.com/keycloak/keycloak/issues/49388) | extends | Согласованность проверки scope между grant type (позитивная и негативная сторона) |

### SEC-SCOPE-MISSING — Token without required scope is denied (RWB-0155, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-cq7v-rfgc-5c7v](https://github.com/advisories/GHSA-cq7v-rfgc-5c7v) | extends | Токен без нужного scope не получает доступ через промежуточный сервис, вызывающий целевой от своего имени (ограничения при делегировании) |

### SEC-TENANT-CREATE — Client cannot assign resource to another tenant (RWB-0156, багов: 2)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-qxpp-qjg8-x4jv](https://github.com/advisories/GHSA-qxpp-qjg8-x4jv) | extends | Целевой контейнер в производных операциях (replay, clone, move), а не только в create |
| [GHSA-xhm9-gwgw-3q2q](https://github.com/advisories/GHSA-xhm9-gwgw-3q2q) | covered | _только пруф_ |

### SEC-TENANT-READ — Tenant A cannot read tenant B data (RWB-0157, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-cqr2-h44g-v75v](https://github.com/advisories/GHSA-cqr2-h44g-v75v) | extends | Глобальное функциональное право (управление ролями) не заменяет проверку доступа к конкретному проекту/арендатору из параметра |

### SEC-TENANT-SEARCH — Tenant filter cannot be bypassed in list/search (RWB-0158, багов: 2)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-9325-vq29-gp3v](https://github.com/advisories/GHSA-9325-vq29-gp3v) | extends | Не только граница tenant, но и запрет по типу данных/политике в поиске; прогонять на каждом поддерживаемом поисковом бэкенде |
| [GHSA-65xw-2v52-jhxc](https://github.com/advisories/GHSA-65xw-2v52-jhxc) | extends | Служебные/вспомогательные списки (активные, запущенные) и broadcast push-событий — тот же фильтр доступа, что у основного списка |

### SEC-TENANT-WRITE — Tenant A cannot mutate tenant B data (RWB-0159, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-4672-hwv6-gq62](https://github.com/advisories/GHSA-4672-hwv6-gq62) | extends | Окружения внутри проекта как граница изоляции; действия-команды (cancel) против чтения |

### SEC-TOKEN-AUDIENCE — Token for another audience is rejected (RWB-0160, багов: 3)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-g74q-6g2f-874x](https://github.com/advisories/GHSA-g74q-6g2f-874x) | extends | Аудитория/приложение для проверки берётся из параметра запроса — должна браться из конфигурации сервиса |
| [GHSA-cw9w-vv67-hf73](https://github.com/advisories/GHSA-cw9w-vv67-hf73) | extends | Смена resource/audience при refresh — refresh-токен привязан к исходному ресурсу |
| [GHSA-q333-f498-w2x7](https://github.com/advisories/GHSA-q333-f498-w2x7) | covered | _только пруф_ |

### SEC-TOKEN-EXPIRED — Expired access token is rejected (RWB-0161, багов: 3)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-x937-hj6v-793p](https://github.com/advisories/GHSA-x937-hj6v-793p) | extends | Токен без iat, использованный до истечения (прогретый кэш проверки), повторно после exp |
| [GHSA-687g-22h4-j4w4](https://github.com/advisories/GHSA-687g-22h4-j4w4) | covered | _только пруф_: nbf в будущем — AUTH-JWT-TIME-CLAIMS |
| [keycloak/keycloak#49909](https://github.com/keycloak/keycloak/issues/49909) | covered | _только пруф_: Применять ко всем эндпоинтам, включая служебные (регистрация клиентов) |

### SECURITY-AUTH-REQUIRED — Protected operation rejects unauthenticated requests (RWB-0162, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [nestjs/nest#718](https://github.com/nestjs/nest/issues/718) | extends | Глобальный префикс и привязка middleware к контроллеру — проверять маршруты в опубликованном виде |

### VAL-ARRAY-ITEMS-BOUNDARIES — Границы массивов: minItems, maxItems, uniqueItems (RWB-0163, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [keycloak/keycloak#52776](https://github.com/keycloak/keycloak/issues/52776) | extends | Добавить обязательный массив с пустыми элементами среди непустых |

### VAL-CASE-SENSITIVITY — Чувствительность к регистру идентификаторов, email и enum соответствует контракту (RWB-0164, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-hmp2-4m7g-22cv](https://github.com/advisories/GHSA-hmp2-4m7g-22cv) | extends | Сравнение имён в правилах авторизации (allow/deny-list) расходится с исполнителем по регистру — обход ограничения |

### VAL-DEEP-NESTING — Чрезмерно вложенный JSON отклоняется без деградации сервиса (RWB-0165, багов: 2)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-qhr7-859c-m2p7](https://github.com/advisories/GHSA-qhr7-859c-m2p7) | extends | Вложенность не только в JSON, но и в строковых шаблонах (glob/brace, выражения) |
| [GHSA-6j4f-fj2g-mc7p](https://github.com/advisories/GHSA-6j4f-fj2g-mc7p) | extends | _только пруф_: Тот же вариант, что GHSA-qhr7-859c-m2p7: шаблоны с множеством групп/альтернатив, а не только вложенность |

### VAL-DEFAULT-VALUES — Опущенные необязательные поля получают задокументированные значения по умолчанию (RWB-0166, багов: 3)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [nestjs/nest#12818](https://github.com/nestjs/nest/issues/12818) | extends | Добавить boolean-параметры query: отсутствует, пустое значение; сравнение до и после обновления зависимостей |
| [keycloak/keycloak#50882](https://github.com/keycloak/keycloak/issues/50882) | extends | Явное указание значения, совпадающего с умолчанием, — дедупликация, а не 5xx |
| [keycloak/keycloak#50807](https://github.com/keycloak/keycloak/issues/50807) | extends | Наличие необязательного поля отключает применение умолчаний к связанному набору |

### VAL-DEPENDENT-FIELDS — Взаимозависимые поля валидируются совместно (RWB-0167, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [strapi/strapi#27421](https://github.com/strapi/strapi/issues/27421) | extends | Добавить вариант взаимоисключающих полей с проверкой, что часть операции не отброшена молча |

### VAL-JSON-TOP-LEVEL-TYPE — Неожиданный тип корня JSON отклоняется (RWB-0168, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [keycloak/keycloak#52798](https://github.com/keycloak/keycloak/issues/52798) | extends | Явно включить литерал null и пустое тело с Content-Type JSON |

### VAL-LARGE-COLLECTION-PAYLOAD — Массив с очень большим числом элементов отклоняется или обрабатывается в пределах лимитов (RWB-0169, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-jp82-f5mq-hwhp](https://github.com/advisories/GHSA-jp82-f5mq-hwhp) | extends | Объявленная длина без самих данных (маленький запрос — большое выделение) |

### VAL-MALFORMED-JSON — Синтаксически некорректный JSON отклоняется (RWB-0170, багов: 2)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [expressjs/body-parser#119](https://github.com/expressjs/body-parser/issues/119) | extends | Добавить сравнение разных видов невалидного JSON между собой |
| [nestjs/nest#422](https://github.com/nestjs/nest/issues/422) | extends | Проверять не только 400, но и что тело — в общей схеме ошибки без стека (ошибка парсера вне фильтров приложения) |

### VAL-NESTED-OBJECT-ERRORS — Ошибка во вложенном объекте указывает точный путь к полю (RWB-0171, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [nestjs/nest#4418](https://github.com/nestjs/nest/issues/4418) | covered | _только пруф_: Ровно эта проверка |

### VAL-QUERY-ARRAY-FORMAT — Массивы в query передаются в задокументированном формате (RWB-0172, багов: 4)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [expressjs/express#7178](https://github.com/expressjs/express/issues/7178) | extends | Один элемент, закодированные скобки, запрос через прокси стенда |
| [expressjs/express#7147](https://github.com/expressjs/express/issues/7147) | extends | Добавить границу числа элементов (20/21 и больше) |
| [nestjs/nest#14486](https://github.com/nestjs/nest/issues/14486) | extends | bracket-нотация a[]= и регрессия разбора после обновления парсера query |
| [expressjs/express#5688](https://github.com/expressjs/express/issues/5688) | extends | Добавить границу числа элементов и максимального индекса (20/21) и разреженные индексы |

### VAL-QUERY-PARAM-POLLUTION — Дублирующиеся query-параметры обрабатываются однозначно (RWB-0173, багов: 2)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [expressjs/body-parser#687](https://github.com/expressjs/body-parser/issues/687) | extends | Добавить вариант для urlencoded-тела (не только query) и регрессию между версиями |
| [expressjs/express#6966](https://github.com/expressjs/express/issues/6966) | extends | _только пруф_: Тот же паттерн, что body-parser#687 (cal-01) |

### VAL-SPECIAL-CHARACTERS — Спецсимволы, emoji и управляющие символы сохраняются или отклоняются корректно (RWB-0174, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [nestjs/nest#1734](https://github.com/nestjs/nest/issues/1734) | extends | Многобайтовые символы в протоколах с префиксом длины — проверять целостность и следующие сообщения потока |

### VAL-STRING-FORMAT — Форматы строк (email, uuid, uri, date, phone) проверяются (RWB-0175, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-h3mg-xc3c-68pw](https://github.com/advisories/GHSA-h3mg-xc3c-68pw) | extends | Проверка формата на экстремально длинном значении — время, память и отсутствие 5xx |

### VAL-WHITESPACE-HANDLING — Пробелы по краям и строки из пробелов обрабатываются согласованно (RWB-0176, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [directus/directus#28037](https://github.com/directus/directus/issues/28037) | extends | Добавить обход проверки зарезервированного префикса пробелами и несогласованность create/delete |

### WS-HANDSHAKE-AUTH — Установление соединения требует аутентификации (RWB-0177, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-gg6r-gp4c-89hp](https://github.com/advisories/GHSA-gg6r-gp4c-89hp) | extends | Служебные namespace и секреты по умолчанию |

### WS-MALFORMED-MESSAGE — Некорректные сообщения не рвут соединение без ответа (RWB-0178, багов: 2)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [nestjs/nest#3127](https://github.com/nestjs/nest/issues/3127) | extends | Синтаксически корректное сообщение с невалидной по схеме нагрузкой |
| [nestjs/nest#683](https://github.com/nestjs/nest/issues/683) | covered | _только пруф_ |

### WS-SUBSCRIPTION-AUTHZ — Подписки и сообщения авторизуются по каждому каналу (RWB-0179, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-89vx-jh4q-vg3w](https://github.com/advisories/GHSA-89vx-jh4q-vg3w) | extends | Перебор всех типов действий протокола (включая пакетные PATCH_MULTI и аналоги) — действие без явного правила должно запрещаться |

