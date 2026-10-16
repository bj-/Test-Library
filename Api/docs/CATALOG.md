# Каталог проверок

Файл генерируется `python tools/build_catalog.py .` — не редактируйте вручную.

Всего проверок: **568** — approved: 467, draft: 85, needs_clarification: 16.
Протоколы: db: 20, generic: 117, graphql: 228, grpc: 149, rest: 420, websocket: 65.

| Категория | Описание | Проверок |
|---|---|---:|
| [contract](#contract) | API contract and schema conformance | 30 |
| [resources](#resources) | Resource lifecycle and state transitions | 34 |
| [security](#security) | Authentication, authorization, and data isolation | 226 |
| [validation](#validation) | Input validation and normalization | 42 |
| [http-semantics](#http-semantics) | HTTP methods, headers, and status semantics | 25 |
| [errors](#errors) | Error response shape and consistency | 4 |
| [pagination](#pagination) | Pagination, filtering, and sorting | 23 |
| [idempotency](#idempotency) | Idempotent behavior and retry safety | 1 |
| [grpc-contract](#grpc-contract) | Protobuf and RPC contract conformance | 17 |
| [grpc-errors](#grpc-errors) | gRPC status and error details | 16 |
| [resilience](#resilience) | Timeouts, retries, dependency failures | 10 |
| [business-logic](#business-logic) | Domain rules, workflows, limits, and money | 17 |
| [concurrency](#concurrency) | Parallel requests, races, and lost updates | 8 |
| [observability](#observability) | Logs, audit trail, tracing, and health endpoints | 12 |
| [performance](#performance) | Latency, throughput, load, and resource usage | 8 |
| [compatibility](#compatibility) | Versioning, backward compatibility, and contract drift | 8 |
| [files](#files) | File upload, download, and binary content | 17 |
| [async](#async) | Webhooks, events, background jobs, and messaging | 15 |
| [graphql](#graphql) | GraphQL-specific query, schema, and abuse controls | 14 |
| [websocket](#websocket) | WebSocket connection, message, and subscription behavior | 10 |
| [privacy](#privacy) | Personal data handling, masking, consent, and erasure | 6 |
| [requirements](#requirements) | Requirement transfer errors - spec vs contract vs implementation, unspecified behavior | 5 |
| [db](#db) | Database - schema and constraints, migrations, indexes and query plans, stored logic, data integrity, application queries | 20 |

## contract

API contract and schema conformance

| ID | Проверка | P | Статус | Протоколы | Профили |
|---|---|---|---|---|---|
| `REST-VALIDATION-ATOMICITY` | Атомарность ошибки валидации | P0 | approved | rest | PR, CI, Regression, Nightly, Release |
| `CONTRACT-REQUIRED-FIELDS` | Successful response contains required contract fields | P1 | approved | rest, grpc, graphql, generic | CI, Regression, Nightly, Release |
| `REST-API-VERSION-COMPATIBILITY` | Совместимость версий API | P1 | approved | rest | CI, Regression, Nightly, Release |
| `REST-BATCH-PARTIAL-FAILURE` | Частичный сбой batch | P1 | approved | rest | CI, Regression, Nightly, Release |
| `REST-CONTENT-TYPE-JSON` | Content-Type и JSON-формат | P1 | approved | rest | CI, Regression, Nightly, Release |
| `REST-ERROR-SCHEMA` | Стабильная схема ошибок | P1 | approved | rest | CI, Regression, Nightly, Release |
| `REST-ERROR-STATUS-BODY` | Согласованность статуса и тела ошибки | P1 | approved | rest | CI, Regression, Nightly, Release |
| `REST-IDEMPOTENCY-KEY` | Повтор с Idempotency-Key | P1 | approved | rest | CI, Regression, Nightly, Release |
| `REST-PATCH-PARTIAL-UPDATE` | Семантика PATCH | P1 | approved | rest | CI, Regression, Nightly, Release |
| `REST-PUT-REPLACEMENT` | Семантика PUT | P1 | approved | rest | CI, Regression, Nightly, Release |
| `REST-READONLY-WRITEONLY` | Поля readOnly/writeOnly | P1 | approved | rest | CI, Regression, Nightly, Release |
| `REST-STATUS-CODE-CONTRACT` | Статус ответа соответствует контракту | P1 | approved | rest | Smoke, PR, CI, Regression, Nightly, Release |
| `CONTRACT-FIELD-SELECTION` | Выбор полей возвращает ровно запрошенные поля с правильными значениями | P2 | approved | rest | CI, Regression, Nightly |
| `CONTRACT-PUBLISHED-SCHEMA-VALID` | Опубликованные сервисом описания API валидны в заявленном диалекте | P2 | approved | generic | CI, Regression, Nightly |
| `CONTRACT-UNKNOWN-FIELD-POLICY` | Unknown fields follow the documented contract policy | P2 | approved | rest, graphql, generic | CI, Regression, Nightly |
| `REST-204-NO-BODY` | Ответ 204 без тела | P2 | approved | rest | CI, Regression, Nightly |
| `REST-ACCEPT-NEGOTIATION` | Согласование Accept | P2 | approved | rest | CI, Regression, Nightly |
| `REST-ASYNC-202` | Асинхронное принятие задачи 202 | P2 | approved | rest | CI, Regression, Nightly |
| `REST-CACHE-CONDITIONAL-GET` | ETag/Last-Modified conditional GET | P2 | approved | rest | CI, Regression, Nightly |
| `REST-DELETE-REPEAT` | Повторное удаление | P2 | approved | rest | CI, Regression, Nightly |
| `REST-ERROR-RETRY-AFTER` | Retry-After при временной ошибке | P2 | approved | rest | CI, Regression, Nightly |
| `REST-PATH-PARAM-ENCODING` | Кодирование path-параметров | P2 | approved | rest | CI, Regression, Nightly |
| `REST-POST-LOCATION` | Location при создании | P2 | approved | rest | CI, Regression, Nightly |
| `REST-QUERY-ENCODING` | Кодирование query-параметров | P2 | approved | rest | CI, Regression, Nightly |
| `REST-RETRY-TRANSIENT-ERROR` | Retry после временной ошибки | P2 | approved | rest | CI, Regression, Nightly |
| `REST-TIMEOUT-BUDGET` | Таймаут и бюджет времени | P2 | approved | rest | CI, Regression, Nightly |
| `REST-UNKNOWN-FIELDS` | Политика неизвестных полей | P2 | approved | rest | CI, Regression, Nightly |
| `CONTRACT-RESPONSE-LINKS-RESOLVE` | URL в ответах открываются | P3 | draft | rest, graphql | Regression |
| `REST-CUSTOM-MEDIA-TYPE-EMPTY-RESULT` | Пустой результат в пользовательском медиатипе не вызывает внутреннюю ошибку | P3 | approved | rest | Regression, Nightly |
| `REST-NEGOTIATED-FORMAT-CONFORMANCE` | Ответ в согласованном формате соответствует спецификации формата | P3 | approved | rest | Regression, Nightly |

## resources

Resource lifecycle and state transitions

| ID | Проверка | P | Статус | Протоколы | Профили |
|---|---|---|---|---|---|
| `RES-CRUD-CYCLE` | Полный жизненный цикл ресурса: создание, чтение, изменение, удаление | P1 | approved | rest, grpc, graphql | CI, Regression, Nightly, Release |
| `RES-DELETE-WITH-DEPENDENTS` | Удаление ресурса с зависимыми объектами выполняется по правилам каскада | P1 | approved | rest, grpc, graphql | CI, Regression, Nightly, Release |
| `RES-IMMUTABLE-FIELDS` | Неизменяемые поля нельзя изменить после создания | P1 | approved | rest, grpc, graphql | CI, Regression, Nightly, Release |
| `RES-REFERENTIAL-INTEGRITY` | Ссылка на несуществующий или чужой связанный ресурс отклоняется | P1 | approved | rest, grpc, graphql | CI, Regression, Nightly, Release |
| `RES-SERVER-GENERATED-FIELDS` | Клиент не может задать серверные поля (id, createdAt, status, version) | P1 | approved | rest, grpc, graphql | CI, Regression, Nightly, Release |
| `RESOURCE-CREATE-READ` | Created resource can be read back | P1 | approved | rest, graphql, generic | Smoke, PR, CI, Regression, Nightly, Release |
| `RESOURCE-READ-MISSING` | Reading a missing resource returns a documented error | P1 | approved | rest, graphql, generic | CI, Regression, Nightly, Release |
| `REST-DECIMAL-PRECISION` | Точность decimal | P1 | approved | rest | CI, Regression, Nightly, Release |
| `REST-DUPLICATE-UNIQUE-KEY` | Дублирование уникального ключа | P1 | approved | rest | CI, Regression, Nightly, Release |
| `REST-STATE-TRANSITIONS` | Переходы состояния ресурса | P1 | approved | rest | CI, Regression, Nightly, Release |
| `RES-ALLOCATED-VALUE-RELEASE` | Выделенное из пула значение не выдаётся повторно, пока прежний владелец не удалён окончательно | P2 | approved | generic | Regression, Nightly |
| `RES-BULK-LIMITS` | Массовые операции соблюдают лимиты и сообщают о каждом элементе | P2 | approved | rest, grpc, graphql | CI, Regression, Nightly |
| `RES-BULK-SINGLE-VALIDATION-PARITY` | Массовая операция валидирует так же, как одиночная | P2 | approved | rest, graphql | CI, Regression, Nightly |
| `RES-CACHE-KEY-COMPLETENESS` | Серверный кэш различает ответы по всем значимым параметрам и по типу ресурса | P2 | approved | rest | CI, Regression, Nightly |
| `RES-CREATE-RESPONSE-MATCHES-READ` | Ответ на создание и изменение совпадает с последующим чтением | P2 | approved | rest, grpc, graphql | CI, Regression, Nightly |
| `RES-DB-OBJECT-NAMES` | API по схеме БД работает с объектами в любом регистре, со спецсимволами и зарезервированными именами | P2 | approved | generic | CI, Regression, Nightly |
| `RES-DRAFT-PUBLISH-FIDELITY` | Публикация черновика переносит все изменения и не ломает связи других объектов | P2 | approved | rest, graphql | CI, Regression, Nightly |
| `RES-LIST-REFLECTS-CHANGES` | Списки и счётчики отражают создание, изменение и удаление | P2 | approved | rest, grpc, graphql | CI, Regression, Nightly |
| `RES-READ-AFTER-WRITE` | Чтение после записи соответствует модели согласованности | P2 | approved | rest, grpc, graphql | Regression, Nightly |
| `RES-RELATIONS-SHARED-JUNCTION-ISOLATION` | Связи через общую связующую таблицу возвращают каждая только свои данные | P2 | approved | rest, graphql | CI, Regression, Nightly |
| `RES-SOFT-DELETE-VISIBILITY` | Мягко удалённые ресурсы не видны в обычных операциях | P2 | approved | rest, grpc, graphql | CI, Regression, Nightly |
| `RES-SYSTEM-OBJECT-PROTECTED` | Встроенные системные объекты защищены от удаления и изменения при любой конфигурации | P2 | approved | rest | CI, Regression, Nightly |
| `RES-TIMESTAMPS` | Метки времени создания и изменения ведут себя корректно | P2 | approved | rest, grpc, graphql | CI, Regression, Nightly |
| `RES-UNIQUENESS-NORMALIZATION` | Уникальность не обходится вариациями значения | P2 | approved | rest, grpc, graphql | CI, Regression, Nightly |
| `RES-UPDATE-MISSING` | Изменение несуществующего ресурса не создаёт его неявно | P2 | approved | rest, grpc, graphql | CI, Regression, Nightly |
| `RES-VALUE-ROUNDTRIP-EXACT` | Сохранённое значение возвращается так, как введено, кроме документированной нормализации | P2 | draft | generic | Regression, Nightly |
| `RES-ARCHIVE-RESTORE` | Архивирование и восстановление сохраняют данные и связи | P3 | approved | rest, grpc, graphql | Regression, Nightly |
| `RES-CACHE-EXPLICIT-INVALIDATION` | Явный сброс кэша через API удаляет закэшированные ответы | P3 | approved | generic | Regression, Nightly |
| `RES-EXPORT-IMPORT-ROUNDTRIP` | Данные, выгруженные API, принимаются им же обратно без изменений | P3 | approved | rest | Regression, Nightly |
| `RES-LARGE-RELATION-SET` | Тысячи связанных объектов не дают 5xx из-за лимитов СУБД на параметры запроса | P3 | approved | rest | Regression, Nightly |
| `RES-REFERENCE-DATA-COMPLETE` | Справочники через API полные, упорядочены по документации и управляются без релиза | P3 | draft | generic | Regression |
| `RES-RELATION-CONNECT-DISCONNECT-CONFLICT` | Подключение с позицией относительно отключаемой в том же запросе связи обрабатывается корректно | P3 | approved | rest, graphql | Regression, Nightly |
| `RES-RELATION-NULL-TARGET-ROWS` | Связь многие-ко-многим возвращает записи связующей таблицы с пустой ссылкой | P3 | approved | rest, graphql | Regression, Nightly |
| `RES-RELATION-ORDER-STABLE` | Изменение связанного ресурса не меняет ручной порядок связей у другой стороны | P3 | approved | rest | Regression, Nightly |

## security

Authentication, authorization, and data isolation

| ID | Проверка | P | Статус | Протоколы | Профили |
|---|---|---|---|---|---|
| `AUTH-CSRF` | Изменяющие операции с cookie-аутентификацией защищены от CSRF | P0 | approved | rest, graphql | PR, CI, Regression, Nightly, Release |
| `AUTH-EXTERNAL-IDP-UNVERIFIED-EMAIL` | Вход через внешний IdP не связывается с учёткой по неподтверждённому email | P0 | approved | rest, graphql | CI, Regression, Nightly, Release |
| `AUTH-JWT-ALG-CONFUSION` | Подмена алгоритма RS256 на HS256 с публичным ключом не принимается | P0 | approved | rest, grpc, graphql, websocket | PR, CI, Regression, Nightly, Release |
| `AUTH-JWT-ALG-NONE` | JWT с alg=none отклоняется | P0 | approved | rest, grpc, graphql, websocket | PR, CI, Regression, Nightly, Release |
| `AUTH-LOGOUT-INVALIDATES` | После выхода токен и сессия недействительны | P0 | approved | rest, grpc, graphql, websocket | PR, CI, Regression, Nightly, Release |
| `AUTH-MFA-STEP-UP` | Операции, требующие второго фактора, недоступны без него | P0 | approved | rest, grpc, graphql, websocket | PR, CI, Regression, Nightly, Release |
| `AUTH-OTP-ATTEMPT-LIMIT` | Количество попыток ввода одноразового кода ограничено | P0 | approved | rest, graphql | PR, CI, Regression, Nightly, Release |
| `AUTH-PASSWORD-RESET-TOKEN` | Токен сброса пароля одноразовый, ограничен по времени и привязан к пользователю | P0 | approved | rest, graphql | PR, CI, Regression, Nightly, Release |
| `INJ-NOSQL` | NoSQL-инъекция операторами запросов не исполняется | P0 | approved | rest, grpc, graphql, websocket | PR, CI, Regression, Nightly, Release |
| `INJ-OS-COMMAND` | Инъекция команд ОС не исполняется | P0 | approved | rest, grpc, graphql, websocket | CI, Regression, Nightly, Release |
| `INJ-PATH-TRAVERSAL` | Обход каталогов через параметры файлов и путей невозможен | P0 | approved | rest, grpc, graphql, websocket | PR, CI, Regression, Nightly, Release |
| `INJ-SQL` | SQL-инъекция во входных параметрах не исполняется | P0 | approved | rest, grpc, graphql, websocket | PR, CI, Regression, Nightly, Release |
| `INJ-SSRF-PARAMETERS` | Параметры с URL и хостами не дают доступа к внутренней сети | P0 | approved | rest, grpc, graphql, websocket | CI, Regression, Nightly, Release |
| `INJ-XXE` | Внешние сущности XML не обрабатываются | P0 | approved | rest | CI, Regression, Nightly, Release |
| `REST-AUTH-ERROR-NO-LEAK` | Ошибки аутентификации без утечки | P0 | approved | rest | Smoke, PR, CI, Regression, Nightly, Release |
| `REST-MASS-ASSIGNMENT` | Mass assignment защищённых полей | P0 | approved | rest | PR, CI, Regression, Nightly, Release |
| `REST-OBJECT-LEVEL-AUTHZ` | Object-level authorization | P0 | approved | rest | Smoke, PR, CI, Regression, Nightly, Release |
| `REST-SENSITIVE-DATA` | Отсутствие чувствительных данных в ответах | P0 | approved | rest | PR, CI, Regression, Nightly, Release |
| `REST-SSRF-URL-FETCH` | Контроль server-side URL fetch | P0 | approved | rest | PR, CI, Regression, Nightly, Release |
| `SEC-AUTHN-MISSING` | Protected operation rejects missing credentials | P0 | approved | rest, graphql, generic | Smoke, PR, CI, Regression, Nightly, Release |
| `SEC-AUTHZ-CACHE-ISOLATION` | Authorization context is respected by caches | P0 | approved | rest, graphql, generic | PR, CI, Regression, Nightly, Release |
| `SEC-AUTHZ-FUNCTION` | User without required permission cannot invoke operation | P0 | approved | rest, graphql, generic | PR, CI, Regression, Nightly, Release |
| `SEC-BOLA-BULK` | Bulk endpoint enforces ownership per item | P0 | approved | rest, graphql, generic | PR, CI, Regression, Nightly, Release |
| `SEC-HORIZONTAL-ESCALATION` | Peer user cannot access peer-only protected action | P0 | approved | rest, graphql, generic | PR, CI, Regression, Nightly, Release |
| `SEC-OWNERSHIP-DELETE` | User cannot delete another owner’s resource | P0 | approved | rest, graphql, generic | PR, CI, Regression, Nightly, Release |
| `SEC-OWNERSHIP-EXPORT` | Export/report endpoints enforce ownership and tenant boundaries | P0 | approved | rest, graphql, generic | PR, CI, Regression, Nightly, Release |
| `SEC-OWNERSHIP-READ` | User cannot read another owner’s resource | P0 | approved | rest, graphql, generic | Smoke, PR, CI, Regression, Nightly, Release |
| `SEC-OWNERSHIP-UPDATE` | User cannot modify another owner’s resource | P0 | approved | rest, graphql, generic | PR, CI, Regression, Nightly, Release |
| `SEC-ROLE-LOW-TO-HIGH` | Low-privilege role cannot perform privileged action | P0 | approved | rest, graphql, generic | PR, CI, Regression, Nightly, Release |
| `SEC-ROLE-MASS-ASSIGN` | Mass assignment cannot elevate privileges | P0 | approved | rest, graphql, generic | PR, CI, Regression, Nightly, Release |
| `SEC-ROLE-SELF-ASSIGN` | User cannot grant self a higher role | P0 | approved | rest, graphql, generic | PR, CI, Regression, Nightly, Release |
| `SEC-SCOPE-EXTRA-UNTRUSTED` | Client cannot add scopes by request parameter | P0 | approved | rest, graphql, generic | PR, CI, Regression, Nightly, Release |
| `SEC-SCOPE-MISSING` | Token without required scope is denied | P0 | approved | rest, graphql, generic | PR, CI, Regression, Nightly, Release |
| `SEC-TENANT-CREATE` | Client cannot assign resource to another tenant | P0 | approved | rest, graphql, generic | PR, CI, Regression, Nightly, Release |
| `SEC-TENANT-HEADER-SPOOF` | Untrusted tenant header cannot override identity context | P0 | approved | rest, graphql, generic | PR, CI, Regression, Nightly, Release |
| `SEC-TENANT-READ` | Tenant A cannot read tenant B data | P0 | approved | rest, graphql, generic | Smoke, PR, CI, Regression, Nightly, Release |
| `SEC-TENANT-SEARCH` | Tenant filter cannot be bypassed in list/search | P0 | approved | rest, graphql, generic | PR, CI, Regression, Nightly, Release |
| `SEC-TENANT-WRITE` | Tenant A cannot mutate tenant B data | P0 | approved | rest, graphql, generic | PR, CI, Regression, Nightly, Release |
| `SEC-TOKEN-EXPIRED` | Expired access token is rejected | P0 | approved | rest, graphql, generic | Smoke, PR, CI, Regression, Nightly, Release |
| `SEC-TOKEN-ISSUER` | Token from untrusted issuer is rejected | P0 | approved | rest, graphql, generic | PR, CI, Regression, Nightly, Release |
| `SEC-TOKEN-REVOKED` | Revoked token cannot be reused | P0 | approved | rest, graphql, generic | PR, CI, Regression, Nightly, Release |
| `SEC-TOKEN-SIGNATURE` | Token with invalid signature is rejected | P0 | approved | rest, graphql, generic | PR, CI, Regression, Nightly, Release |
| `SEC-VERTICAL-ESCALATION` | Lower role cannot invoke higher-role route via alternate method | P0 | approved | rest, graphql, generic | PR, CI, Regression, Nightly, Release |
| `SECURITY-AUTH-REQUIRED` | Protected operation rejects unauthenticated requests | P0 | approved | rest, grpc, graphql, generic | PR, CI, Regression, Nightly, Release |
| `SECURITY-AUTHZ-CROSS-USER` | User cannot access another user's resource | P0 | approved | rest, graphql, generic | PR, CI, Regression, Nightly, Release |
| `AUTH-ACCOUNT-STATE-ALL-SCHEMES` | Отключённая, заблокированная или истёкшая учётка не аутентифицируется ни одной схемой | P1 | approved | generic | CI, Regression, Nightly, Release |
| `AUTH-API-KEY-LIFECYCLE` | API-ключи ограничены по правам, отзываются и не раскрываются | P1 | approved | rest, grpc, graphql, websocket | CI, Regression, Nightly, Release |
| `AUTH-BRUTE-FORCE-PROTECTION` | Перебор паролей ограничивается | P1 | approved | rest, graphql | Regression, Nightly |
| `AUTH-CLIENT-ASSERTION-BINDING` | Client assertion принимается только с ключом клиента, указанного в ней | P1 | approved | generic | CI, Regression, Nightly, Release |
| `AUTH-COOKIE-ATTRIBUTES` | Сессионные cookie имеют Secure, HttpOnly, SameSite и узкие Domain/Path | P1 | approved | rest, graphql | CI, Regression, Nightly, Release |
| `AUTH-EXTERNAL-ID-EXACT-MATCH` | Внешний идентификатор субъекта сравнивается побайтно в паре издатель и subject | P1 | approved | generic | CI, Regression, Nightly, Release |
| `AUTH-JWT-HEADER-INJECTION` | Параметры kid, jku, x5u в заголовке JWT не позволяют подставить ключ | P1 | approved | rest, grpc, graphql, websocket | CI, Regression, Nightly, Release |
| `AUTH-NOSQL-OPERATOR-CREDENTIALS` | Операторы NoSQL в учётных данных входа отклоняются | P1 | draft | rest | Regression, Nightly |
| `AUTH-OAUTH-REDIRECT-STATE` | OAuth/OIDC flow проверяет redirect_uri, state и PKCE | P1 | approved | rest, graphql | CI, Regression, Nightly, Release |
| `AUTH-OTP-BINDING` | Одноразовый код привязан к получателю и операции | P1 | approved | rest, graphql | CI, Regression, Nightly, Release |
| `AUTH-OTP-EXPIRY` | Одноразовый код перестаёт действовать после истечения срока | P1 | approved | rest, graphql | Regression, Nightly, Release |
| `AUTH-OTP-REUSE` | Одноразовый код нельзя использовать повторно и после выдачи нового | P1 | approved | rest, graphql | CI, Regression, Nightly, Release |
| `AUTH-OTP-SEND-LIMIT` | Частота отправки кодов ограничена (SMS bombing) | P1 | approved | rest, graphql | CI, Regression, Nightly, Release |
| `AUTH-PASSWORD-CHANGE-REQUIRES-CURRENT` | Смена пароля требует верный текущий пароль | P1 | draft | rest | Regression, Nightly |
| `AUTH-PASSWORD-CHANGE-REVOKES` | Смена или сброс пароля завершает другие сессии | P1 | approved | rest, graphql | CI, Regression, Nightly, Release |
| `AUTH-PATH-NORMALIZATION-BYPASS` | Вариации пути защищённого маршрута не обходят аутентификацию | P1 | draft | rest | Regression, Nightly |
| `AUTH-PROTOCOL-SESSION-OWNER-BINDING` | Идентификатор протокольной сессии привязан к аутентифицированному владельцу | P1 | approved | rest, websocket | CI, Regression, Nightly, Release |
| `AUTH-SAML-ASSERTION-REPLAY` | Повторно предъявленное SAML-утверждение отклоняется | P1 | approved | generic | CI, Regression, Nightly, Release |
| `AUTH-SENSITIVE-CHANGE-REAUTH` | Изменение защиты учётки требует свежей аутентификации | P1 | draft | generic | Regression, Nightly |
| `AUTH-SESSION-FILTER-SCOPE` | Операции над сессиями ограничены сессиями своей учётки | P1 | draft | rest | Regression, Nightly |
| `AUTH-SESSION-FIXATION` | Идентификатор сессии меняется после входа | P1 | approved | rest, graphql | CI, Regression, Nightly, Release |
| `AUTH-SESSION-ID-NOT-EXPOSED` | Список сессий не раскрывает значение cookie сессии | P1 | draft | rest | Regression, Nightly |
| `AUTH-SESSION-VALUE-EXACT-MATCH` | Значение сессии сравнивается целиком и точно | P1 | draft | rest | Regression, Nightly |
| `AUTH-TOKEN-RESERVED-CLAIMS` | Пользовательские поля не переопределяют зарезервированные claims токена | P1 | approved | generic | CI, Regression, Nightly, Release |
| `AUTH-TOKEN-TYPE-CONFUSION` | Refresh, ID или сервисный токен не принимается как access-токен | P1 | approved | rest, grpc, graphql, websocket | CI, Regression, Nightly, Release |
| `AUTH-USER-ENUMERATION` | Ответы входа, регистрации и восстановления не раскрывают существование аккаунта | P1 | approved | rest, graphql | Regression, Nightly |
| `HARD-BACKUP-RESTORE-PROTECTED` | Восстановление из резервной копии не обходит защиту записи | P1 | approved | generic | CI, Regression, Nightly, Release |
| `HARD-DEBUG-ENDPOINTS` | Отладочные и служебные эндпоинты недоступны извне | P1 | approved | rest, graphql | CI, Regression, Nightly, Release |
| `HARD-ENVIRONMENT-ISOLATION` | Тестовый стенд не обращается к ресурсам production | P1 | draft | generic | Regression |
| `HARD-EXCESSIVE-DATA-EXPOSURE` | Ответы не содержат внутренних полей сверх контракта | P1 | approved | rest, grpc, graphql, websocket | CI, Regression, Nightly, Release |
| `HARD-EXPENSIVE-OPERATION-LIMITS` | Дорогие операции ограничены по ресурсам | P1 | approved | rest, grpc, graphql, websocket | Regression, Nightly |
| `HARD-HOST-HEADER` | Подмена Host и X-Forwarded-Host не влияет на ссылки и маршрутизацию | P1 | approved | rest, graphql | CI, Regression, Nightly, Release |
| `HARD-METHOD-OVERRIDE` | Заголовки переопределения метода не обходят авторизацию | P1 | approved | rest | CI, Regression, Nightly, Release |
| `HARD-OUTBOUND-CREDENTIALS-SCOPE` | Учётные данные своего сайта не уходят в исходящие запросы к другим хостам | P1 | approved | generic | CI, Regression, Nightly, Release |
| `HARD-SETUP-ENDPOINTS-PROTECTED` | Эндпоинты первоначальной настройки не позволяют захватить экземпляр | P1 | approved | generic | CI, Regression, Nightly, Release |
| `HARD-SHADOW-API-VERSIONS` | Старые версии API и недокументированные маршруты не обходят защиту | P1 | approved | rest, graphql | CI, Regression, Nightly, Release |
| `HARD-TLS-ONLY` | API доступен только по TLS с актуальными настройками | P1 | approved | rest, grpc, graphql, websocket | CI, Regression, Nightly, Release |
| `HARD-WILDCARD-DOMAIN-MATCH` | Шаблон домена с wildcard совпадает только с поддоменами указанного домена | P1 | approved | generic | CI, Regression, Nightly, Release |
| `INJ-ARCHIVE-ENTRY-NAME-EVAL` | Имена файлов внутри загруженного репозитория или архива не исполняются как код | P1 | approved | generic | CI, Regression, Nightly, Release |
| `INJ-DOWNSTREAM-BODY-INJECTION` | Значение поля не внедряет ключи в тело запроса к другой системе | P1 | draft | generic | Regression, Nightly |
| `INJ-FILTER-EXPRESSION` | Выражения фильтрации (OData, RSQL, JSONPath, GraphQL where) не позволяют выйти за ограничения | P1 | approved | rest, graphql | CI, Regression, Nightly, Release |
| `INJ-HEADER-CRLF` | CRLF в значениях не позволяет внедрять заголовки ответа | P1 | approved | rest | CI, Regression, Nightly, Release |
| `INJ-LLM-GENERATED-ACTIONS` | Код и вызовы инструментов, сгенерированные LLM по вводу пользователя, не выполняют опасных действий | P1 | approved | rest | Regression, Nightly |
| `INJ-PROTOTYPE-POLLUTION` | Специальные ключи __proto__ и constructor не меняют поведение сервера | P1 | approved | rest, graphql | CI, Regression, Nightly, Release |
| `INJ-RESERVED-PATH-WRITE` | Запись файлов через API не попадает в служебные каталоги | P1 | approved | generic | CI, Regression, Nightly, Release |
| `INJ-SCHEMA-IDENTIFIER-CODEGEN` | Идентификаторы пользовательской схемы не внедряют код и SQL при генерации кода и DDL | P1 | approved | generic | CI, Regression, Nightly, Release |
| `INJ-STORED-XSS` | Сохранённые данные с HTML/JS не создают XSS у потребителей API | P1 | approved | rest, graphql | CI, Regression, Nightly, Release |
| `INJ-TEMPLATE-SSTI` | Инъекция в серверные шаблоны не исполняется | P1 | approved | rest, grpc, graphql, websocket | CI, Regression, Nightly, Release |
| `INJ-UNSAFE-DESERIALIZATION` | Небезопасная десериализация пользовательских данных невозможна | P1 | approved | rest, grpc, graphql, websocket | CI, Regression, Nightly, Release |
| `INJ-USER-CODE-EXECUTION` | Пользовательский код, исполняемый сервером, не получает доступа к ОС, файлам и сети | P1 | approved | generic | CI, Regression, Nightly, Release |
| `INJ-USER-DATA-CALLABLE` | Данные пользователя не позволяют вызвать серверную функцию вне allowlist | P1 | approved | generic | CI, Regression, Nightly, Release |
| `REAL-BFF-ADMIN-API-AUDITCONTROLLER-GETENTRIES-OPERATION-ACCESS-PO` | Confirm operation-specific authentication and authorization policy | P1 | needs_clarification | rest | CI, Regression, Release |
| `REAL-BFF-ADMIN-API-AUTHCONTROLLER-CHANGEPASSWORD-MISSING-OR-INVAL` | Cookie-authenticated endpoint rejects missing/invalid session | P1 | draft | rest | Smoke, CI, Regression, Release |
| `REAL-BFF-ADMIN-API-AUTHCONTROLLER-CHANGEPASSWORD-ROLE-MODEL-UNRES` | Confirm minimum privilege policy for sensitive operation | P1 | needs_clarification | rest | CI, Regression, Release |
| `REAL-BFF-ADMIN-API-AUTHCONTROLLER-CHANGEPASSWORD-WRONG-CURRENT-PA` | Password change verifies current password | P1 | draft | rest | CI, Regression, Release |
| `REAL-BFF-ADMIN-API-AUTHCONTROLLER-DELETESESSION-CROSS-ACCOUNT-SES` | Session endpoint enforces session ownership | P1 | draft | rest | CI, Regression, Release |
| `REAL-BFF-ADMIN-API-AUTHCONTROLLER-DELETESESSION-MISSING-OR-INVALI` | Cookie-authenticated endpoint rejects missing/invalid session | P1 | draft | rest | Smoke, CI, Regression, Release |
| `REAL-BFF-ADMIN-API-AUTHCONTROLLER-DELETESESSION-ROLE-MODEL-UNRESO` | Confirm minimum privilege policy for sensitive operation | P1 | needs_clarification | rest | CI, Regression, Release |
| `REAL-BFF-ADMIN-API-AUTHCONTROLLER-GETSESSIONS-CROSS-ACCOUNT-SESSI` | Session endpoint enforces session ownership | P1 | draft | rest | CI, Regression, Release |
| `REAL-BFF-ADMIN-API-AUTHCONTROLLER-GETSESSIONS-MISSING-OR-INVALID` | Cookie-authenticated endpoint rejects missing/invalid session | P1 | draft | rest | Smoke, CI, Regression, Release |
| `REAL-BFF-ADMIN-API-AUTHCONTROLLER-LOGIN-INVALID-CREDENTIALS` | Login rejects invalid credentials | P1 | draft | rest | Smoke, CI, Regression, Release |
| `REAL-BFF-ADMIN-API-AUTHCONTROLLER-LOGOUT-MISSING-OR-INVALID-COOKI` | Cookie-authenticated endpoint rejects missing/invalid session | P1 | draft | rest | Smoke, CI, Regression, Release |
| `REAL-BFF-ADMIN-API-AUTHCONTROLLER-LOGOUT-ROLE-MODEL-UNRESOLVED` | Confirm minimum privilege policy for sensitive operation | P1 | needs_clarification | rest | CI, Regression, Release |
| `REAL-BFF-ADMIN-API-COMPONENTTYPESCONTROLLER-GETTYPES-OPERATION-AC` | Confirm operation-specific authentication and authorization policy | P1 | draft | rest | CI, Regression, Release |
| `REAL-BFF-ADMIN-API-CONTENTCONTROLLER-CREATEITEM-OPERATION-ACCESS` | Confirm operation-specific authentication and authorization policy | P1 | draft | rest | CI, Regression, Release |
| `REAL-BFF-ADMIN-API-CONTENTCONTROLLER-CREATEITEM-ROLE-MODEL-UNRESO` | Confirm minimum privilege policy for sensitive operation | P1 | needs_clarification | rest | CI, Regression, Release |
| `REAL-BFF-ADMIN-API-CONTENTCONTROLLER-GETITEMS-OPERATION-ACCESS-PO` | Confirm operation-specific authentication and authorization policy | P1 | needs_clarification | rest | CI, Regression, Release |
| `REAL-BFF-ADMIN-API-CONTENTCONTROLLER-GETSOURCES-OPERATION-ACCESS` | Confirm operation-specific authentication and authorization policy | P1 | draft | rest | CI, Regression, Release |
| `REAL-BFF-ADMIN-API-CONTENTCONTROLLER-REMOVEITEM-OPERATION-ACCESS` | Confirm operation-specific authentication and authorization policy | P1 | draft | rest | CI, Regression, Release |
| `REAL-BFF-ADMIN-API-CONTENTCONTROLLER-REMOVEITEM-ROLE-MODEL-UNRESO` | Confirm minimum privilege policy for sensitive operation | P1 | needs_clarification | rest | CI, Regression, Release |
| `REAL-BFF-ADMIN-API-CONTENTCONTROLLER-UPDATEITEM-OPERATION-ACCESS` | Confirm operation-specific authentication and authorization policy | P1 | draft | rest | CI, Regression, Release |
| `REAL-BFF-ADMIN-API-CONTENTCONTROLLER-UPDATEITEM-ROLE-MODEL-UNRESO` | Confirm minimum privilege policy for sensitive operation | P1 | needs_clarification | rest | CI, Regression, Release |
| `REAL-BFF-ADMIN-API-LAYOUTSCONTROLLER-ARCHIVE-OPERATION-ACCESS-POL` | Confirm operation-specific authentication and authorization policy | P1 | needs_clarification | rest | CI, Regression, Release |
| `REAL-BFF-ADMIN-API-LAYOUTSCONTROLLER-ARCHIVE-ROLE-MODEL-UNRESOLVE` | Confirm minimum privilege policy for sensitive operation | P1 | needs_clarification | rest | CI, Regression, Release |
| `REAL-BFF-ADMIN-API-LAYOUTSCONTROLLER-GETCURRENTVERSIONS-OPERATION` | Confirm operation-specific authentication and authorization policy | P1 | draft | rest | CI, Regression, Release |
| `REAL-BFF-ADMIN-API-LAYOUTSCONTROLLER-GETLANGUAGES-OPERATION-ACCES` | Confirm operation-specific authentication and authorization policy | P1 | draft | rest | CI, Regression, Release |
| `REAL-BFF-ADMIN-API-LAYOUTSCONTROLLER-GETNODES-OPERATION-ACCESS-PO` | Confirm operation-specific authentication and authorization policy | P1 | needs_clarification | rest | CI, Regression, Release |
| `REAL-BFF-ADMIN-API-LAYOUTSCONTROLLER-GETSCREEN-OPERATION-ACCESS-P` | Confirm operation-specific authentication and authorization policy | P1 | draft | rest | CI, Regression, Release |
| `REAL-BFF-ADMIN-API-LAYOUTSCONTROLLER-GETSCREENS-OPERATION-ACCESS` | Confirm operation-specific authentication and authorization policy | P1 | draft | rest | CI, Regression, Release |
| `REAL-BFF-ADMIN-API-LAYOUTSCONTROLLER-GETVERSIONS-OPERATION-ACCESS` | Confirm operation-specific authentication and authorization policy | P1 | draft | rest | CI, Regression, Release |
| `REAL-BFF-ADMIN-API-LAYOUTSCONTROLLER-PUBLISH-OPERATION-ACCESS-POL` | Confirm operation-specific authentication and authorization policy | P1 | needs_clarification | rest | CI, Regression, Release |
| `REAL-BFF-ADMIN-API-LAYOUTSCONTROLLER-PUBLISH-ROLE-MODEL-UNRESOLVE` | Confirm minimum privilege policy for sensitive operation | P1 | needs_clarification | rest | CI, Regression, Release |
| `REAL-BFF-ADMIN-API-LAYOUTSCONTROLLER-SAVETRANSLATION-OPERATION-AC` | Confirm operation-specific authentication and authorization policy | P1 | draft | rest | CI, Regression, Release |
| `REAL-BFF-ADMIN-API-LAYOUTSCONTROLLER-SAVETRANSLATION-ROLE-MODEL-U` | Confirm minimum privilege policy for sensitive operation | P1 | draft | rest | CI, Regression, Release |
| `REAL-BFF-ADMIN-API-LAYOUTSCONTROLLER-TOGGLELANGUAGE-OPERATION-ACC` | Confirm operation-specific authentication and authorization policy | P1 | draft | rest | CI, Regression, Release |
| `REAL-BFF-ADMIN-API-LAYOUTSCONTROLLER-TOGGLELANGUAGE-ROLE-MODEL-UN` | Confirm minimum privilege policy for sensitive operation | P1 | draft | rest | CI, Regression, Release |
| `REAL-BFF-ADMIN-API-LAYOUTSCONTROLLER-UPDATECOMPONENT-OPERATION-AC` | Confirm operation-specific authentication and authorization policy | P1 | draft | rest | CI, Regression, Release |
| `REAL-BFF-ADMIN-API-LAYOUTSCONTROLLER-UPDATECOMPONENT-ROLE-MODEL-U` | Confirm minimum privilege policy for sensitive operation | P1 | draft | rest | CI, Regression, Release |
| `REAL-BFF-ADMIN-API-LAYOUTSCONTROLLER-VALIDATE-OPERATION-ACCESS-PO` | Confirm operation-specific authentication and authorization policy | P1 | needs_clarification | rest | CI, Regression, Release |
| `REAL-BFF-ADMIN-API-LAYOUTSCONTROLLER-VALIDATE-ROLE-MODEL-UNRESOLV` | Confirm minimum privilege policy for sensitive operation | P1 | needs_clarification | rest | CI, Regression, Release |
| `REAL-MOBILE-CLIENT-API-ACCEPTDOCUMENTS-CROSS-PRINCIPAL-OR-STALE-R` | Document acceptance is bound to the correct principal and revision | P1 | draft | rest | CI, Regression, Release |
| `REAL-MOBILE-CLIENT-API-ACCEPTDOCUMENTS-GUEST-VS-AUTHENTICATED` | Guest and authenticated document access follow distinct policies | P1 | draft | rest | Smoke, CI, Regression, Release |
| `REAL-MOBILE-CLIENT-API-GETDOCUMENTSHISTORY-GUEST-VS-AUTHENTICATED` | Guest and authenticated document access follow distinct policies | P1 | draft | rest | CI, Regression, Release |
| `REAL-MOBILE-CLIENT-API-GETUNSIGNEDDOCUMENTS-GUEST-VS-AUTHENTICATE` | Guest and authenticated document access follow distinct policies | P1 | draft | rest | CI, Regression, Release |
| `REAL-MOBILE-CLIENT-API-LOGOUT-MISSING-EXPIRED-OR-REFRESH-TOKEN` | Logout requires a valid access token | P1 | draft | rest | Smoke, CI, Regression, Release |
| `REAL-MOBILE-CLIENT-API-ONSTART-ANONYMOUS-VS-API-KEY` | Startup endpoint matches the documented API-key policy | P1 | needs_clarification | rest | CI, Regression, Release |
| `REAL-MOBILE-CLIENT-API-REFRESH-EXPIRED-OR-INVALID-REFRESH-TOKEN` | Authentication endpoint rejects invalid credentials | P1 | draft | rest | Smoke, CI, Regression, Release |
| `REAL-MOBILE-CLIENT-API-SENDCODE-INVALID-API-KEY` | Authentication endpoint rejects invalid credentials | P1 | draft | rest | Smoke, CI, Regression, Release |
| `REAL-MOBILE-CLIENT-API-VERIFYCODE-INVALID-API-KEY` | Authentication endpoint rejects invalid credentials | P1 | draft | rest | Smoke, CI, Regression, Release |
| `REST-OPEN-REDIRECT` | Валидация redirect URL | P1 | approved | rest | CI, Regression, Nightly, Release |
| `REST-RATE-LIMIT` | Ограничение частоты запросов | P1 | approved | rest | CI, Regression, Nightly, Release |
| `REST-SENSITIVE-CACHE-CONTROL` | Кэширование чувствительных ответов | P1 | approved | rest | CI, Regression, Nightly, Release |
| `SEC-ALT-REPRESENTATION-ACCESS` | Закрытый ресурс недоступен ни через одно альтернативное представление | P1 | approved | rest, graphql | CI, Regression, Nightly, Release |
| `SEC-AUTHN-MALFORMED` | Malformed credential is rejected | P1 | approved | rest, graphql, generic | CI, Regression, Nightly, Release |
| `SEC-AUTHZ-ASYNC-JOB` | Authorization is rechecked for asynchronous job access | P1 | approved | rest, graphql, generic | CI, Regression, Nightly, Release |
| `SEC-AUTHZ-ERROR-LEAK` | Authorization failures do not disclose protected data | P1 | approved | rest, graphql, generic | CI, Regression, Nightly, Release |
| `SEC-AUTHZ-EXPLICIT-OVER-INHERITED` | Явное пониженное право на дочерний объект имеет приоритет над унаследованным | P1 | approved | generic | CI, Regression, Nightly, Release |
| `SEC-AUTHZ-METHOD-MATRIX` | Authorization is enforced for every method | P1 | approved | rest, graphql, generic | CI, Regression, Nightly, Release |
| `SEC-AUTHZ-RECREATED-IDENTITY` | Права и согласия не переходят к пересозданному пользователю с тем же логином | P1 | approved | rest | CI, Regression, Nightly, Release |
| `SEC-AUTHZ-REVOKE-ROLE` | Role revocation takes effect within policy window | P1 | approved | rest, graphql, generic | CI, Regression, Nightly, Release |
| `SEC-AUTHZ-ROLE-POSITIVE-MATRIX` | Разрешённая операция работает для каждой роли с правом, а не только для администратора | P1 | approved | generic | CI, Regression, Nightly, Release |
| `SEC-AUTHZ-RULE-READ-WRITE-PARITY` | Условие прав по связанной записи действует в записи так же, как в чтении | P1 | approved | rest, graphql | CI, Regression, Nightly, Release |
| `SEC-CONFUSED-DEPUTY` | Действия во внешней системе от имени пользователя выполняются только с его правами | P1 | approved | rest, generic | CI, Regression, Nightly, Release |
| `SEC-FAIL-CLOSED-INPUT` | Неожиданный тип, пустое или отсутствующее поле проверки безопасности ведёт к отказу, а не к пропуску проверки | P1 | approved | generic | CI, Regression, Nightly, Release |
| `SEC-IDENTITY-PROOF-OF-POSSESSION` | Заявленная клиентом идентичность без доказательства владения не даёт прав и льгот | P1 | approved | rest, generic | CI, Regression, Nightly, Release |
| `SEC-INTERNAL-CONTROL-PARAMS` | Заголовки и параметры подключения клиента не задают внутренние управляющие параметры операции | P1 | approved | rest, websocket | CI, Regression, Nightly, Release |
| `SEC-OWNERSHIP-REFERENCE-INDIRECT` | Indirect resource references preserve authorization | P1 | approved | rest, graphql, generic | CI, Regression, Nightly, Release |
| `SEC-POLICY-TEMPLATE-USER-DATA` | Данные пользователя, подставляемые в шаблон политики доступа, не работают как wildcard | P1 | approved | generic | CI, Regression, Nightly, Release |
| `SEC-PRINCIPAL-TYPE-CONFUSION` | Принципал одного типа не получает прав принципала другого типа с тем же числовым ID | P1 | draft | generic | Regression, Nightly |
| `SEC-READONLY-MODE-ENFORCED` | Режим только для чтения запрещает изменения любым запросом, а не по первому ключевому слову | P1 | approved | rest, graphql, generic | CI, Regression, Nightly, Release |
| `SEC-ROLE-BULK-ADMIN` | Bulk admin actions require privilege for every target | P1 | approved | rest, graphql, generic | CI, Regression, Nightly, Release |
| `SEC-TOKEN-AUDIENCE` | Token for another audience is rejected | P1 | approved | rest, graphql, generic | CI, Regression, Nightly, Release |
| `SEC-TOKEN-REFRESH-REPLAY` | Refresh-token replay is rejected or rotated | P1 | approved | rest, graphql, generic | CI, Regression, Nightly, Release |
| `AUTH-CLIENT-CERT-IDENTITY` | Личность из сертификата клиента извлекается однозначно | P2 | approved | generic | CI, Regression, Nightly |
| `AUTH-CREDENTIAL-CHANNEL-STRICT` | Учётные данные принимаются только по документированному каналу | P2 | draft | rest | Regression, Nightly |
| `AUTH-DUPLICATE-CREDENTIALS` | Повторяющиеся и пустые учётные данные не дают доступа | P2 | draft | rest | Regression, Nightly |
| `AUTH-GENERATED-SECRET-STRENGTH` | Сгенерированные сервером секреты имеют стойкость не ниже требуемой алгоритмом | P2 | approved | rest | CI, Regression, Nightly |
| `AUTH-IDENTITY-ATTRIBUTES-ALL-SCHEMES` | Атрибуты идентичности, которые даёт источник, сохраняются при любом способе аутентификации | P2 | approved | generic | CI, Regression, Nightly |
| `AUTH-IMPORTED-PASSWORD-HASH` | Пользователь, импортированный с хешем пароля поддерживаемого алгоритма, входит по исходному паролю | P2 | approved | generic | CI, Regression, Nightly |
| `AUTH-JWT-TIME-CLAIMS` | Токены с nbf/iat в будущем и без exp обрабатываются по политике | P2 | approved | rest, grpc, graphql, websocket | CI, Regression, Nightly |
| `AUTH-JWT-VALID-ACCEPTED` | Валидный токен принимается при всех поддерживаемых алгоритмах, наборах ключей и настройках claims | P2 | approved | generic | CI, Regression, Nightly |
| `AUTH-LOGIN-CROSS-ACCOUNT-COOKIE` | Вход другой учёткой с cookie действующей сессии обрабатывается по правилу | P2 | draft | rest | Regression, Nightly |
| `AUTH-LOGOUT-CLEARS-COOKIE` | Выход снимает cookie сессии на клиенте | P2 | approved | rest | CI, Regression, Nightly |
| `AUTH-LOGOUT-SCOPE` | Выход завершает только текущую сессию | P2 | draft | rest | Regression, Nightly |
| `AUTH-MFA-UNENROLLED-ERROR` | Ошибка шага второго фактора у пользователя без зарегистрированного фактора — обычная 4xx | P2 | approved | rest | CI, Regression, Nightly |
| `AUTH-OAUTH-PUBLIC-CLIENT-CONSENT` | Повторная авторизация публичного OAuth-клиента не выполняется без участия пользователя | P2 | approved | generic | CI, Regression, Nightly |
| `AUTH-PASSWORD-POLICY` | Политика паролей применяется на сервере | P2 | approved | rest, graphql | CI, Regression, Nightly |
| `AUTH-REFRESH-PRESERVES-SCOPE` | Refresh без параметра scope сохраняет scope исходной авторизации | P2 | approved | rest | CI, Regression, Nightly |
| `AUTH-SESSION-ID-ENTROPY` | Идентификатор сессии новый при каждом входе, уникален и непредсказуем | P2 | draft | rest | Regression, Nightly |
| `AUTH-SESSION-TIMEOUT` | Сессия истекает после простоя и абсолютного срока | P2 | approved | rest, graphql | Regression, Nightly |
| `AUTH-TOKEN-IN-URL` | Учётные данные не передаются и не принимаются в URL | P2 | approved | rest, graphql | CI, Regression, Nightly |
| `AUTH-TOKEN-INTROSPECTION` | Интроспекция токена возвращает актуальное состояние и те же claims, что в токене | P2 | approved | rest | CI, Regression, Nightly |
| `AUTH-TOKEN-SENDER-CONSTRAINED` | Обмен и обновление токена сохраняют привязку к отправителю (DPoP, mTLS) | P2 | approved | rest | CI, Regression, Nightly |
| `HARD-BUSINESS-FLOW-AUTOMATION` | Чувствительные бизнес-потоки защищены от автоматизированного злоупотребления | P2 | approved | rest, grpc, graphql, websocket | Regression, Nightly |
| `HARD-CACHE-POISONING` | Неключевые заголовки не отравляют общий кэш | P2 | approved | rest, graphql | Regression, Nightly |
| `HARD-CLIENT-IP-TRUSTED-PROXIES` | IP клиента определяется по цепочке доверенных прокси одинаково на всех маршрутах | P2 | approved | rest | CI, Regression, Nightly |
| `HARD-DENYLIST-EVERY-ENTRY` | Каждый элемент списка запрещённых значений отклоняется | P2 | approved | generic | CI, Regression, Nightly |
| `HARD-ID-PREDICTABILITY` | Предсказуемые идентификаторы не позволяют собрать данные перебором | P2 | approved | rest, grpc, graphql, websocket | CI, Regression, Nightly |
| `HARD-IP-ALLOWLIST` | Ограничение доступа по адресам и подсетям работает на границах для IPv4 и IPv6 | P2 | approved | generic | CI, Regression, Nightly |
| `HARD-NOT-IMPLEMENTED-INERT` | Операция, помеченная в контракте как нереализованная, не выполняется | P2 | draft | rest, graphql, grpc | Regression |
| `HARD-ROUTE-SHARED-BACKEND-ISOLATION` | Маршруты шлюза к одному бэкенду применяют каждый свои фильтры | P2 | approved | generic | CI, Regression, Nightly |
| `HARD-SENSITIVE-DATA-IN-URL` | Персональные данные и секреты не передаются в URL | P2 | approved | rest | CI, Regression, Nightly |
| `HARD-SLOW-CLIENT-LIMITS` | Медленные и неполные запросы и непрочитанные ответы не накапливаются без ограничения | P2 | approved | generic | Regression, Nightly |
| `HARD-UNSAFE-API-CONSUMPTION` | Ответы сторонних API валидируются перед использованием | P2 | approved | rest, grpc, graphql, websocket | Regression, Nightly |
| `INJ-CSV-FORMULA` | Экспорт в CSV/XLSX нейтрализует формулы | P2 | approved | rest | CI, Regression, Nightly |
| `INJ-LOG-FORGING` | Пользовательские данные не позволяют подделывать записи журналов | P2 | approved | rest, grpc, graphql, websocket | Regression, Nightly |
| `INJ-NULL-BYTE` | NUL-байт во входных данных отклоняется или не обрезает значение | P2 | draft | rest | Regression, Nightly |
| `INJ-REDOS` | Пользовательский ввод не вызывает катастрофический backtracking в regex | P2 | approved | rest, grpc, graphql, websocket | Regression, Nightly |
| `INJ-REFLECTED-XSS` | Параметры запроса не отражаются в HTML-ответе без экранирования | P2 | approved | rest | CI, Regression, Nightly |
| `REST-CORS-POLICY` | Политика CORS | P2 | approved | rest | CI, Regression, Nightly |
| `REST-SECURITY-HEADERS` | Защитные HTTP-заголовки | P2 | approved | rest | CI, Regression, Nightly |
| `SEC-AUTHN-SCHEMES-SUPPORTED` | Все задокументированные схемы Authorization принимаются на своих эндпоинтах | P2 | approved | rest | CI, Regression, Nightly |
| `SEC-AUTHZ-DYNAMIC-VARIABLES` | Динамические переменные в правилах доступа действуют как эквивалентные статические значения | P2 | approved | rest, graphql | CI, Regression, Nightly |
| `SEC-AUTHZ-LIST-CHECK-CONSISTENCY` | Перечисление субъектов и объектов с доступом согласовано с точечной проверкой | P2 | approved | generic | CI, Regression, Nightly |
| `SEC-AUTHZ-PATH-RULE-PRECEDENCE` | Правила доступа по путям применяются по наиболее точному совпадению, независимо от порядка объявления | P2 | approved | rest | CI, Regression, Nightly |
| `SEC-CHECK-ORDER` | Аутентификация и авторизация проверяются раньше разбора и валидации тела | P2 | draft | rest, graphql, grpc | Regression, Nightly |
| `SEC-CLONE-FIELD-PERMISSIONS` | Копирование ресурса соблюдает полевые права чтения и создания | P2 | approved | rest, graphql | CI, Regression, Nightly |
| `SEC-DISABLED-FEATURE-ENFORCED` | Отключённая настройкой функция недоступна через все API и не попадает в токены | P2 | approved | generic | CI, Regression, Nightly |
| `SEC-OPAQUE-ID-INTEGRITY` | Непрозрачный идентификатор, выданный сервером, проверяется на подлинность | P2 | approved | generic | CI, Regression, Nightly |
| `SEC-ROLE-ADMIN-SELF-TARGET` | Административная операция над собственной учёткой обрабатывается по политике без 5xx | P2 | approved | rest | CI, Regression, Nightly |
| `AUTH-BASIC-CREDENTIALS-SPECIAL-CHARS` | Basic-аутентификация принимает пароль с двоеточием, пробелами и UTF-8 | P3 | approved | rest | Regression, Nightly |
| `AUTH-CONCURRENT-SESSIONS` | Лимит одновременных сессий и устройств соблюдается | P3 | approved | rest, graphql | Regression, Nightly |
| `AUTH-CONTACT-CHANGE-PREVIOUS-VALUE` | Смена телефона или email на ранее использованный этим пользователем проходит подтверждение | P3 | approved | generic | Regression, Nightly |
| `AUTH-EXTERNAL-IDP-MISSING-ATTRIBUTES` | Вход через внешний IdP без необязательных атрибутов профиля обрабатывается по требованиям | P3 | approved | generic | Regression, Nightly |
| `AUTH-OAUTH-OUTBOUND-SCOPE` | Запрос авторизации к внешнему провайдеру содержит запрошенные scope без устаревших значений по умолчанию | P3 | approved | generic | Regression, Nightly |
| `AUTH-OAUTH-PAR` | Pushed Authorization Request действует как прямой запрос авторизации и не ограничивает длительность входа | P3 | approved | rest | Regression, Nightly |
| `AUTH-OAUTH-RESOURCE-INDICATOR` | Индикатор ресурса, не соответствующий аудитории клиента, даёт 400 invalid_target | P3 | approved | rest | Regression, Nightly |
| `AUTH-REVOKED-COOKIE-RELOGIN` | Вход с закрытой cookie сессии создаёт новую сессию | P3 | draft | rest | Regression, Nightly |
| `AUTH-SESSION-NOT-BEFORE-LOGIN` | Анонимный запрос не получает cookie сессии и не создаёт серверную сессию | P3 | approved | rest | Regression, Nightly |
| `AUTH-SESSION-SLIDING-RENEWAL` | Активность продлевает сессию по правилам скользящего срока | P3 | draft | rest | Regression, Nightly |
| `HARD-VERSION-DISCLOSURE` | Ответы не раскрывают версии ПО и инфраструктуры | P3 | approved | rest, graphql | Regression, Nightly |

## validation

Input validation and normalization

| ID | Проверка | P | Статус | Протоколы | Профили |
|---|---|---|---|---|---|
| `AUTH-LOGIN-IDENTIFIER-NORMALIZATION` | Логин (email, телефон) нормализуется одинаково при входе, создании и поиске | P1 | approved | rest, grpc, graphql | CI, Regression, Nightly, Release |
| `REST-DATE-TIME-TZ` | Дата, время и timezone | P1 | approved | rest | CI, Regression, Nightly, Release |
| `REST-ENUM-VALUES` | Допустимые и неизвестные enum | P1 | approved | rest | CI, Regression, Nightly, Release |
| `REST-NULL-VS-OMITTED` | Null и отсутствующее поле | P1 | approved | rest | CI, Regression, Nightly, Release |
| `REST-NUMERIC-BOUNDARIES` | Числовые границы | P1 | approved | rest | CI, Regression, Nightly, Release |
| `REST-REQUEST-SIZE-LIMIT` | Лимит размера тела | P1 | approved | rest | CI, Regression, Nightly, Release |
| `REST-REQUIRED-PARAM-MISSING` | Отсутствует обязательный параметр | P1 | approved | rest | CI, Regression, Nightly, Release |
| `REST-STRING-LENGTH-BOUNDARIES` | Границы длины строки | P1 | approved | rest | CI, Regression, Nightly, Release |
| `REST-TYPE-MISMATCH` | Несовпадение типа поля | P1 | approved | rest | CI, Regression, Nightly, Release |
| `REST-UNSUPPORTED-CONTENT-TYPE` | Неподдерживаемый Content-Type запроса | P1 | approved | rest | CI, Regression, Nightly, Release |
| `VAL-ARRAY-ITEMS-BOUNDARIES` | Границы массивов: minItems, maxItems, uniqueItems | P1 | approved | rest, grpc, graphql | CI, Regression, Nightly, Release |
| `VAL-DEEP-NESTING` | Чрезмерно вложенный JSON отклоняется без деградации сервиса | P1 | approved | rest, graphql | CI, Regression, Nightly, Release |
| `VAL-DEPENDENT-FIELDS` | Взаимозависимые поля валидируются совместно | P1 | approved | rest, grpc, graphql | CI, Regression, Nightly, Release |
| `VAL-MALFORMED-JSON` | Синтаксически некорректный JSON отклоняется | P1 | approved | rest, graphql | CI, Regression, Nightly, Release |
| `VAL-MONEY-AMOUNT` | Денежные суммы: знак, точность и валюта валидируются | P1 | approved | rest, grpc, graphql | CI, Regression, Nightly, Release |
| `VAL-NUMBER-REPRESENTATION` | Альтернативные записи чисел обрабатываются по контракту | P1 | approved | rest, grpc, graphql | CI, Regression, Nightly, Release |
| `VAL-PATH-ID-FORMAT` | Неверный формат идентификатора в пути не вызывает 5xx | P1 | approved | rest | CI, Regression, Nightly, Release |
| `VAL-RANGE-ORDER` | Начало диапазона не может быть позже конца | P1 | approved | rest, grpc, graphql | CI, Regression, Nightly, Release |
| `VAL-SPECIAL-CHARACTERS` | Спецсимволы, emoji и управляющие символы сохраняются или отклоняются корректно | P1 | approved | rest, grpc, graphql | CI, Regression, Nightly, Release |
| `VAL-STRING-FORMAT` | Форматы строк (email, uuid, uri, date, phone) проверяются | P1 | approved | rest, grpc, graphql | CI, Regression, Nightly, Release |
| `REST-EMPTY-VALUES` | Пустые объект, массив и строка | P2 | approved | rest | CI, Regression, Nightly |
| `REST-JSON-DUPLICATE-KEYS` | Дублирующиеся ключи JSON | P2 | approved | rest | CI, Regression, Nightly |
| `REST-OPTIONAL-EMPTY-VALUE` | Отсутствующий и пустой параметр | P2 | approved | rest | CI, Regression, Nightly |
| `REST-UNICODE-NORMALIZATION` | Unicode и нормализация | P2 | approved | rest | CI, Regression, Nightly |
| `VAL-BODY-ENCODING` | Тело в неверной кодировке или с BOM обрабатывается предсказуемо | P2 | approved | rest, graphql | CI, Regression, Nightly |
| `VAL-BOOLEAN-COERCION` | Неявное приведение типов для boolean не происходит | P2 | approved | rest, graphql | CI, Regression, Nightly |
| `VAL-CASE-SENSITIVITY` | Чувствительность к регистру идентификаторов, email и enum соответствует контракту | P2 | approved | rest, grpc, graphql | CI, Regression, Nightly |
| `VAL-DEFAULT-VALUES` | Опущенные необязательные поля получают задокументированные значения по умолчанию | P2 | approved | rest, grpc, graphql | CI, Regression, Nightly |
| `VAL-DEFERRED-FAILURE` | Принятые при записи данные не вызывают 5xx в зависимых операциях | P2 | approved | generic | CI, Regression, Nightly |
| `VAL-JSON-TOP-LEVEL-TYPE` | Неожиданный тип корня JSON отклоняется | P2 | approved | rest, graphql | CI, Regression, Nightly |
| `VAL-LARGE-COLLECTION-PAYLOAD` | Массив с очень большим числом элементов отклоняется или обрабатывается в пределах лимитов | P2 | approved | rest, grpc, graphql | CI, Regression, Nightly |
| `VAL-NESTED-OBJECT-ERRORS` | Ошибка во вложенном объекте указывает точный путь к полю | P2 | approved | rest, grpc, graphql | CI, Regression, Nightly |
| `VAL-OPTIONAL-FIELDS-COMBINATIONS` | Любая комбинация и порядок необязательных полей обрабатываются без падения | P2 | draft | rest, graphql, grpc | Regression, Nightly |
| `VAL-QUERY-PARAM-POLLUTION` | Дублирующиеся query-параметры обрабатываются однозначно | P2 | approved | rest | CI, Regression, Nightly |
| `VAL-REGEX-PATTERN` | Поле с pattern принимает только совпадающие значения | P2 | approved | rest, graphql | CI, Regression, Nightly |
| `VAL-REQUIRED-HEADERS` | Обязательные и форматные заголовки валидируются | P2 | approved | rest | CI, Regression, Nightly |
| `VAL-TIGHTENED-RULES-STORED-DATA` | Сохранённые до ужесточения валидации значения обрабатываются одинаково на всех путях записи | P2 | approved | rest, grpc, graphql | CI, Regression, Nightly |
| `VAL-WHITESPACE-HANDLING` | Пробелы по краям и строки из пробелов обрабатываются согласованно | P2 | approved | rest, grpc, graphql | CI, Regression, Nightly |
| `VAL-ALL-ERRORS-REPORTED` | Ошибки валидации нескольких полей возвращаются по контракту (все сразу или первая) | P3 | approved | rest, grpc, graphql | Regression, Nightly |
| `VAL-DYNAMIC-VARIABLES-TYPE` | Правило валидации с динамической переменной сравнивает значения по типу поля | P3 | approved | rest, graphql | Regression, Nightly |
| `VAL-QUERY-ARRAY-FORMAT` | Массивы в query передаются в задокументированном формате | P3 | approved | rest | Regression, Nightly |
| `VAL-UPLOADED-SCHEMA-FORMATS` | Загружаемая клиентом схема с документированными форматами принимается без ложных предупреждений | P3 | approved | rest, graphql | Regression, Nightly |

## http-semantics

HTTP methods, headers, and status semantics

| ID | Проверка | P | Статус | Протоколы | Профили |
|---|---|---|---|---|---|
| `HTTP-BODY-WITHOUT-CONTENT-TYPE` | Тело без Content-Type обрабатывается предсказуемо | P2 | approved | rest | CI, Regression, Nightly |
| `HTTP-HEADER-SIZE-LIMIT` | Слишком большие заголовки отклоняются контролируемо | P2 | approved | rest | CI, Regression, Nightly |
| `HTTP-PATH-PREFIX-SEGMENT-BOUNDARY` | Правило по префиксу пути соблюдает границу сегмента | P2 | approved | rest | CI, Regression, Nightly |
| `HTTP-REQUEST-SMUGGLING` | Противоречивые Content-Length и Transfer-Encoding не приводят к request smuggling | P2 | approved | rest | Regression, Nightly |
| `HTTP-RESPONSE-FRAMING-HEADERS` | Ответ не содержит одновременно Content-Length и Transfer-Encoding | P2 | approved | rest | CI, Regression, Nightly |
| `HTTP-UNKNOWN-ROUTE` | Неизвестный маршрут возвращает 404, а не 5xx или 200 | P2 | approved | rest | CI, Regression, Nightly |
| `REST-HEAD-GET-CONSISTENCY` | HEAD response is consistent with GET | P2 | approved | rest | CI, Regression, Nightly |
| `REST-METHOD-NOT-ALLOWED` | Unsupported HTTP method is rejected | P2 | approved | rest | CI, Regression, Nightly |
| `HTTP-ABSOLUTE-URL-BASE-PATH` | Абсолютные URL, которые формирует сервер, учитывают публичный адрес и базовый путь | P3 | approved | rest | Regression, Nightly |
| `HTTP-ACCEPT-LANGUAGE` | Язык сообщений определяется Accept-Language с fallback | P3 | approved | rest, graphql | Regression, Nightly |
| `HTTP-BODY-ON-GET-DELETE` | Тело в GET/DELETE игнорируется или отклоняется по контракту | P3 | approved | rest | Regression, Nightly |
| `HTTP-CACHEABLE-RESPONSE-CACHE-CONTROL` | Кэшируемый ответ содержит Cache-Control по итоговой политике | P3 | approved | rest, graphql | Regression, Nightly |
| `HTTP-COMPRESSION` | Сжатие ответа согласуется через Accept-Encoding | P3 | approved | rest | Regression, Nightly |
| `HTTP-HEADER-REPEATED-LINES-ACCEPTED` | Сотни повторяющихся строк одного заголовка в пределах лимита размера принимаются одинаково по HTTP/1.1 и HTTP/2 | P3 | approved | rest, grpc | Regression, Nightly |
| `HTTP-HTTP2-RESOURCE-LIMITS` | Параметры HTTP/2 со стороны клиента не заставляют сервер буферизовать и работать без предела | P3 | approved | rest, grpc | Regression, Nightly |
| `HTTP-OPTIONS-ALLOW` | OPTIONS возвращает согласованный список методов | P3 | approved | rest | Regression, Nightly |
| `HTTP-PREFERENCE-APPLIED-ACCURATE` | Preference-Applied перечисляет ровно применённые предпочтения | P3 | approved | rest | Regression, Nightly |
| `HTTP-REDIRECT-ENDPOINT-PARITY` | Вызов через перенаправляющий адрес работает как прямой вызов | P3 | draft | rest | Regression |
| `HTTP-RESPONSE-MODE-HEADER-PARITY` | Настроенные заголовки ответа присутствуют во всех режимах обработки ответа | P3 | approved | rest | Regression, Nightly |
| `HTTP-ROUTE-PROTOCOL-CONDITION` | Условие маршрута для одного протокола не блокирует маршрут по другому разрешённому протоколу | P3 | approved | rest, grpc | Regression, Nightly |
| `HTTP-TRAILING-SLASH-CASE` | Вариации пути (слэш в конце, регистр, двойной слэш) обрабатываются единообразно | P3 | approved | rest | Regression, Nightly |
| `HTTP-URL-LENGTH-LIMIT` | Очень длинный URL отклоняется контролируемо | P3 | approved | rest | Regression, Nightly |
| `HTTP-VARY-HEADER` | Кэшируемые ответы содержат корректный Vary | P3 | approved | rest | Regression, Nightly |
| `HTTP-VERSION-PARITY` | Запросы по HTTP/2 и с предложением Upgrade h2c обслуживаются так же, как по HTTP/1.1 | P3 | approved | rest | Regression, Nightly |
| `HTTP-WWW-AUTHENTICATE-SYNTAX` | Заголовок WWW-Authenticate в ответе 401 соответствует синтаксису RFC | P3 | approved | rest | Regression, Nightly |

## errors

Error response shape and consistency

| ID | Проверка | P | Статус | Протоколы | Профили |
|---|---|---|---|---|---|
| `ERR-INTERNAL-ERROR-SHAPE` | Внутренняя ошибка сервера возвращается в общей модели без утечек | P1 | approved | rest, grpc, graphql, websocket | CI, Regression, Nightly, Release |
| `ERR-STABLE-ERROR-CODES` | Машиночитаемые коды ошибок стабильны и задокументированы | P2 | approved | rest, grpc, graphql, websocket | CI, Regression, Nightly |
| `ERR-STATUS-MATCHES-EFFECT` | Код ответа соответствует фактическому результату операции | P2 | approved | rest, grpc, graphql | CI, Regression, Nightly |
| `REST-CORRELATION-ID` | Correlation ID | P3 | approved | rest | Regression, Nightly |

## pagination

Pagination, filtering, and sorting

| ID | Проверка | P | Статус | Протоколы | Профили |
|---|---|---|---|---|---|
| `PAGE-CURSOR-TAMPERING` | Подделанный или чужой курсор пагинации не раскрывает данные | P1 | approved | rest, grpc, graphql | CI, Regression, Nightly, Release |
| `REST-FILTER-SORT-PAGINATION` | Комбинация filter/sort/pagination | P1 | approved | rest | CI, Regression, Nightly, Release |
| `REST-PAGINATION-BOUNDARIES` | Pagination handles boundary values correctly | P1 | approved | rest, graphql | CI, Regression, Nightly, Release |
| `REST-PAGINATION-LIMITS` | Границы размера страницы | P1 | approved | rest | CI, Regression, Nightly, Release |
| `REST-PAGINATION-STABLE-ORDER` | Стабильный порядок пагинации | P1 | approved | rest | CI, Regression, Nightly, Release |
| `PAGE-BEYOND-LAST` | Запрос страницы за последней возвращает пустой результат без ошибки | P2 | approved | rest, grpc, graphql | CI, Regression, Nightly |
| `PAGE-CONCURRENT-MODIFICATION` | Изменения коллекции во время обхода не приводят к дублям и пропускам сверх контракта | P2 | approved | rest, grpc, graphql | Regression, Nightly |
| `PAGE-NEXT-LINK-VALID` | Ссылка next ведёт на ту же коллекцию, сохраняет фильтры и работает | P2 | approved | rest | CI, Regression, Nightly |
| `PAGE-SEARCH-SPECIAL-CHARS` | Поиск со спецсимволами и wildcard не ломается и не расширяет выборку | P2 | approved | rest, grpc, graphql | CI, Regression, Nightly |
| `PAGE-SORT-FIELD-TYPE-MATRIX` | Сортировка по каждому полю учитывает его тип, локаль и направление | P2 | draft | rest, graphql | Regression, Nightly |
| `PAGE-TOTAL-COUNT` | Общее число элементов согласовано с суммой страниц | P2 | approved | rest, grpc, graphql | CI, Regression, Nightly |
| `REST-ALIASED-EMBED-FILTER-INDEPENDENCE` | Вложения одного ресурса под разными алиасами фильтруются независимо | P2 | approved | rest, graphql | CI, Regression, Nightly |
| `REST-FILTER-INVALID` | Невалидный фильтр | P2 | approved | rest | CI, Regression, Nightly |
| `REST-FILTER-OPERATION-PARITY` | Один фильтр даёт согласованный результат в списке, агрегации и вложенной выборке | P2 | approved | rest, graphql | CI, Regression, Nightly |
| `REST-FILTER-OPERATOR-TYPE-MATRIX` | Каждый оператор фильтра работает для каждого допустимого типа поля и возвращает ровно подходящие записи | P2 | approved | rest, graphql | CI, Regression, Nightly |
| `REST-FILTER-RELATION-NO-DUPLICATES` | Фильтр по полю связанной коллекции возвращает каждую запись один раз | P2 | approved | rest, graphql | CI, Regression, Nightly |
| `REST-FILTER-SORT-COMPOSITION` | Filtering and sorting compose correctly | P2 | approved | rest, graphql | CI, Regression, Nightly |
| `REST-FILTER-UNSELECTED-FIELD` | Фильтр по полю, не входящему в выбор полей, работает | P2 | approved | rest, graphql | CI, Regression, Nightly |
| `REST-SORT-INVALID-FIELD` | Сортировка по неизвестному полю | P2 | approved | rest | CI, Regression, Nightly |
| `PAGE-SORT-MULTI-KEY-PRIORITY` | Сортировка по нескольким ключам соблюдает заданный клиентом порядок приоритета | P3 | approved | rest, graphql | Regression, Nightly |
| `PAGE-SORT-NULLS-TIES` | Сортировка по полю с null и одинаковыми значениями детерминирована | P3 | approved | rest, grpc, graphql | Regression, Nightly |
| `REST-FILTER-EQUIVALENT-FORMS` | Логически эквивалентные формы фильтра дают одинаковый ответ | P3 | approved | rest, graphql | Regression, Nightly |
| `REST-FILTER-NAME-COLLISION` | Фильтр по полю с именем вложенного ресурса применяется к полю | P3 | approved | rest | Regression, Nightly |

## idempotency

Idempotent behavior and retry safety

| ID | Проверка | P | Статус | Протоколы | Профили |
|---|---|---|---|---|---|
| `REST-IDEMPOTENCY-RETRY` | Retry does not duplicate an idempotent operation's effect | P1 | approved | rest | CI, Regression, Nightly, Release |

## grpc-contract

Protobuf and RPC contract conformance

| ID | Проверка | P | Статус | Протоколы | Профили |
|---|---|---|---|---|---|
| `GRPC-PROTO-BREAKING` | Изменения proto не ломают совместимость wire и JSON | P0 | approved | grpc | PR, CI, Regression, Nightly, Release |
| `GRPC-FIELD-PRESENCE` | Значение по умолчанию отличается от неустановленного поля, где это важно | P1 | approved | grpc | CI, Regression, Nightly, Release |
| `GRPC-MAX-MESSAGE-SIZE` | Сообщения больше лимита отклоняются RESOURCE_EXHAUSTED | P1 | approved | grpc | CI, Regression, Nightly, Release |
| `GRPC-REQUEST-VALIDATION` | Invalid gRPC request is rejected predictably | P1 | approved | grpc | CI, Regression, Nightly, Release |
| `GRPC-SERVER-STREAM-COMPLETE` | Серверный стрим отдаёт все элементы по порядку и завершается OK | P1 | approved | grpc | CI, Regression, Nightly, Release |
| `GRPC-STREAM-TERMINATION` | Streaming RPC terminates correctly | P1 | approved | grpc | Regression, Nightly |
| `GRPC-CLIENT-STREAM-PARTIAL-FAILURE` | Ошибка в середине клиентского стрима обрабатывается по контракту | P2 | approved | grpc | CI, Regression, Nightly |
| `GRPC-ENUM-UNKNOWN-VALUE` | Неизвестное и нулевое значение enum обрабатывается явно | P2 | approved | grpc | CI, Regression, Nightly |
| `GRPC-HEALTH-PROTOCOL` | Стандартный health-протокол gRPC реализован корректно | P2 | approved | grpc | CI, Regression, Nightly |
| `GRPC-JSON-TRANSCODING` | HTTP/JSON транскодирование соответствует proto-аннотациям | P2 | approved | grpc, rest | CI, Regression, Nightly |
| `GRPC-ONEOF` | Поля oneof валидируются и не установлены одновременно | P2 | approved | grpc | CI, Regression, Nightly |
| `GRPC-REFLECTION-EXPOSURE` | Server reflection отключён или защищён в продуктиве | P2 | approved | grpc | CI, Regression, Nightly |
| `GRPC-REPEATED-BOUNDARIES` | Repeated и map поля: пусто, много элементов, дубликаты ключей | P2 | approved | grpc | CI, Regression, Nightly |
| `GRPC-UNKNOWN-FIELDS` | Неизвестные поля сообщения обрабатываются по политике совместимости | P2 | approved | grpc | CI, Regression, Nightly |
| `GRPC-WELL-KNOWN-TYPES` | Timestamp, Duration и другие well-known types валидируются по диапазонам | P2 | approved | grpc | CI, Regression, Nightly |
| `GRPC-BIDI-FLOW-CONTROL` | Двунаправленный стрим соблюдает flow control при медленном клиенте | P3 | approved | grpc | Regression, Nightly |
| `GRPC-COMPRESSION` | Сжатие сообщений согласуется и неподдерживаемое отклоняется | P3 | approved | grpc | Regression, Nightly |

## grpc-errors

gRPC status and error details

| ID | Проверка | P | Статус | Протоколы | Профили |
|---|---|---|---|---|---|
| `GRPC-METADATA-AUTH-MISSING` | Каждый RPC сервиса требует аутентификационные метаданные | P0 | approved | grpc | PR, CI, Regression, Nightly, Release |
| `GRPC-UNAUTHENTICATED-VS-PERMISSION-DENIED` | Отсутствие аутентификации и отсутствие прав различаются по статусу | P0 | approved | grpc | PR, CI, Regression, Nightly, Release |
| `GRPC-DEADLINE-EXCEEDED` | Превышение дедлайна возвращает DEADLINE_EXCEEDED без побочных эффектов сверх контракта | P1 | approved | grpc | CI, Regression, Nightly, Release |
| `GRPC-NOT-FOUND-ALREADY-EXISTS` | Отсутствующий и дублирующийся ресурс дают NOT_FOUND и ALREADY_EXISTS | P1 | approved | grpc | CI, Regression, Nightly, Release |
| `GRPC-STATUS-MAPPING` | RPC errors use documented gRPC status codes | P1 | approved | grpc | CI, Regression, Nightly, Release |
| `GRPC-STREAM-AUTH-EXPIRY` | Длительный стрим учитывает истечение и отзыв токена | P1 | approved | grpc | CI, Regression, Nightly, Release |
| `GRPC-TLS-MTLS` | Транспорт защищён TLS, при mTLS клиентский сертификат обязателен | P1 | approved | grpc | CI, Regression, Nightly, Release |
| `GRPC-CANCELLATION` | Отмена клиентом прекращает обработку на сервере | P2 | approved | grpc | Regression, Nightly |
| `GRPC-DEADLINE-PROPAGATION` | Дедлайн передаётся в нижележащие вызовы | P2 | approved | grpc | Regression, Nightly |
| `GRPC-ERROR-DETAILS` | Ошибки содержат структурированные детали google.rpc.Status | P2 | approved | grpc | CI, Regression, Nightly |
| `GRPC-METADATA-MALFORMED` | Некорректные и чрезмерные метаданные отклоняются | P2 | approved | grpc | CI, Regression, Nightly |
| `GRPC-RESOURCE-EXHAUSTED` | Превышение квот возвращает RESOURCE_EXHAUSTED с RetryInfo | P2 | approved | grpc | CI, Regression, Nightly |
| `GRPC-RETRY-POLICY` | Автоматические повторы применяются только к безопасным методам и статусам | P2 | approved | grpc | Regression, Nightly |
| `GRPC-STREAM-RESOURCE-LIMITS` | Число одновременных стримов и их длительность ограничены | P2 | approved | grpc | Regression, Nightly |
| `GRPC-KEEPALIVE-POLICY` | Агрессивные keepalive-пинги клиента ограничиваются | P3 | approved | grpc | Regression, Nightly |
| `GRPC-PRECONDITION-ABORTED` | FAILED_PRECONDITION и ABORTED используются согласно семантике повтора | P3 | approved | grpc | Regression, Nightly |

## resilience

Timeouts, retries, dependency failures

| ID | Проверка | P | Статус | Протоколы | Профили |
|---|---|---|---|---|---|
| `RESIL-DEPENDENCY-DOWN` | Недоступность зависимости даёт контролируемую ошибку | P1 | approved | rest, grpc, graphql, websocket | Regression, Nightly |
| `REST-CONCURRENT-UPDATE` | Конкурентное обновление | P1 | approved | rest | CI, Regression, Nightly, Release |
| `REST-ETAG-IF-MATCH` | Условное обновление If-Match | P1 | approved | rest | CI, Regression, Nightly, Release |
| `RESIL-BROKER-DOWN` | Недоступность брокера сообщений не теряет события | P2 | approved | rest, grpc, graphql, websocket | Regression, Nightly |
| `RESIL-DEPENDENCY-TLS-RECOVERY` | Проверка доступности внешнего бэкенда проверяет его сертификат и восстанавливается без перезапуска | P2 | approved | generic | CI, Regression, Nightly |
| `RESIL-GRACEFUL-SHUTDOWN` | Перезапуск экземпляра не обрывает выполняющиеся запросы | P2 | approved | rest, grpc, graphql, websocket | Regression, Nightly |
| `RESIL-PARTIAL-DEGRADATION` | Отказ некритичной зависимости не ломает основной функционал | P2 | approved | rest, grpc, graphql, websocket | Regression, Nightly |
| `RESIL-CIRCUIT-BREAKER` | Circuit breaker размыкается и восстанавливается по политике | P3 | approved | rest, grpc, graphql, websocket | Regression, Nightly |
| `RESIL-ENCRYPTION-KEY-ROTATION` | Нерасшифровываемое после смены ключа значение не ломает чтение и сохранение остальных данных | P3 | approved | rest | Regression, Nightly |
| `RESIL-TLS-CERT-RELOAD` | Сервер подхватывает заменённый TLS-сертификат без перезапуска | P3 | approved | generic | Regression, Nightly |

## business-logic

Domain rules, workflows, limits, and money

| ID | Проверка | P | Статус | Протоколы | Профили |
|---|---|---|---|---|---|
| `BIZ-CLIENT-PRICE-TAMPERING` | Цена, скидка и итог рассчитываются на сервере | P0 | approved | rest, grpc, graphql | PR, CI, Regression, Nightly, Release |
| `BIZ-DOUBLE-SPEND` | Параллельные списания не приводят к двойной трате | P0 | approved | rest, grpc, graphql | Regression, Nightly |
| `BIZ-NEGATIVE-QUANTITY` | Отрицательные и нулевые количества и суммы не дают выгоды | P0 | approved | rest, grpc, graphql | PR, CI, Regression, Nightly, Release |
| `BIZ-WORKFLOW-STEP-SKIP` | Нельзя пропустить обязательный шаг бизнес-процесса | P0 | approved | rest, grpc, graphql | PR, CI, Regression, Nightly, Release |
| `BIZ-LIMITS-QUOTAS` | Лимиты и квоты соблюдаются на границе и не обходятся параллельно | P1 | approved | rest, grpc, graphql | CI, Regression, Nightly, Release |
| `BIZ-ONE-TIME-BENEFIT-REUSE` | Одноразовые промокоды, бонусы и приглашения нельзя использовать повторно | P1 | approved | rest, grpc, graphql | CI, Regression, Nightly, Release |
| `BIZ-ROUNDING` | Округление денежных величин корректно и не накапливает ошибку | P1 | approved | rest, grpc, graphql | CI, Regression, Nightly, Release |
| `BIZ-CONFIG-SCOPE-PRECEDENCE` | Настройка более узкого уровня имеет приоритет над глобальной | P2 | approved | generic | CI, Regression, Nightly |
| `BIZ-CURRENCY-MISMATCH` | Смешение валют в операции обрабатывается явно | P2 | approved | rest, grpc, graphql | CI, Regression, Nightly |
| `BIZ-DIVISION-BY-ZERO` | Входы с нулём в знаменателе не дают 500 и нечисловых значений | P2 | draft | generic | Regression, Nightly |
| `BIZ-EMAIL-LINK-CROSS-SESSION` | Ссылка-действие из письма работает в другой сессии и после перезапуска сервиса | P2 | approved | rest | CI, Regression, Nightly |
| `BIZ-EMAIL-NOTIFICATION-DELIVERY` | Письма уходят нужному адресату с верными ссылками и без внедрения заголовков | P2 | draft | generic | Regression, Nightly |
| `BIZ-FLAG-EFFECT-MATRIX` | Каждый флаг сущности влияет на поведение так, как описано | P2 | draft | generic | Regression, Nightly |
| `BIZ-HIERARCHY-CYCLES` | Ссылка на себя и циклы в иерархии запрещены | P2 | approved | rest, grpc, graphql | CI, Regression, Nightly |
| `BIZ-SIDE-EFFECTS-ONCE` | Побочные эффекты (письма, push, события) выполняются ровно один раз | P2 | approved | rest, grpc, graphql | CI, Regression, Nightly |
| `BIZ-TIME-WINDOW` | Операции вне разрешённого временного окна отклоняются | P2 | approved | rest, grpc, graphql | CI, Regression, Nightly |
| `BIZ-AMBIGUOUS-ADDRESS` | Неоднозначный почтовый адрес не выбирается молча по первому совпадению | P3 | draft | generic | Regression |

## concurrency

Parallel requests, races, and lost updates

| ID | Проверка | P | Статус | Протоколы | Профили |
|---|---|---|---|---|---|
| `CONC-COUNTER-INCREMENT` | Счётчики корректны при параллельных инкрементах | P1 | approved | rest, grpc, graphql | Regression, Nightly |
| `CONC-DOUBLE-SUBMIT` | Двойная отправка формы не создаёт дубликат операции | P1 | approved | rest, grpc, graphql | Regression, Nightly |
| `CONC-LOST-UPDATE` | Параллельные изменения не теряют друг друга молча | P1 | approved | rest, grpc, graphql | Regression, Nightly |
| `CONC-PARALLEL-CREATE-UNIQUE` | Параллельное создание с одним уникальным ключом создаёт один объект | P1 | approved | rest, grpc, graphql | Regression, Nightly |
| `CONC-REQUEST-CONTEXT-ISOLATION` | Параллельные запросы разных пользователей получают только свой контекст и свой ответ | P1 | approved | generic | Regression, Nightly |
| `CONC-STATE-TRANSITION-RACE` | Параллельные переходы состояния не нарушают автомат состояний | P1 | approved | rest, grpc, graphql | Regression, Nightly |
| `CONC-DELETE-VS-UPDATE` | Параллельные удаление и изменение не оставляют ресурс в противоречивом состоянии | P2 | approved | rest, grpc, graphql | Regression, Nightly |
| `CONC-PARALLEL-INDEPENDENT` | Параллельные независимые запросы одной операции выполняются без 5xx | P2 | approved | generic | Regression, Nightly |

## observability

Logs, audit trail, tracing, and health endpoints

| ID | Проверка | P | Статус | Протоколы | Профили |
|---|---|---|---|---|---|
| `OBS-NO-SECRETS-IN-LOGS` | Логи не содержат паролей, токенов и ПДн в открытом виде | P0 | approved | rest, grpc, graphql, websocket | Regression, Nightly |
| `OBS-AUDIT-TRAIL` | Чувствительные действия фиксируются в журнале аудита | P1 | approved | rest, grpc, graphql, websocket | CI, Regression, Nightly, Release |
| `OBS-HEALTH-ENDPOINTS` | Health-эндпоинты отражают состояние и не раскрывают детали | P2 | approved | rest, grpc, graphql, websocket | CI, Regression, Nightly |
| `OBS-METRICS-LABEL-CARDINALITY` | Значения из запроса не создают неограниченно новых серий метрик | P2 | approved | generic | CI, Nightly |
| `OBS-BUILD-VERSION-TRACEABLE` | Версия сборки доступна для трассировки на тестовых стендах и скрыта в production | P3 | draft | generic | Regression |
| `OBS-CONFIG-ENDPOINT-ACCURATE` | Служебный эндпоинт конфигурации показывает фактические значения | P3 | approved | generic | Regression, Nightly |
| `OBS-LOG-ENTRY-INTEGRITY` | Записи журнала при всплеске параллельных запросов не склеиваются | P3 | approved | generic | Regression, Nightly |
| `OBS-METRICS-VALUE-RANGE` | Gauge-метрики с известными границами остаются в них после сбоев и восстановления | P3 | approved | generic | Regression, Nightly |
| `OBS-REQUEST-LOG-ALL-ATTEMPTS` | Журнал запроса с повторами содержит каждую попытку, включая последнюю | P3 | approved | generic | Regression, Nightly |
| `OBS-SERVER-TIMING-ACCURATE` | Server-Timing отражает фактическую длительность этапов | P3 | approved | rest | Regression, Nightly |
| `OBS-TELEMETRY-FORMAT` | Экспортируемая телеметрия соответствует документированной структуре и соглашениям OpenTelemetry | P3 | approved | generic | Regression, Nightly |
| `OBS-TRACE-PROPAGATION` | Контекст трассировки принимается и передаётся дальше | P3 | approved | rest, grpc, graphql, websocket | Regression, Nightly |

## performance

Latency, throughput, load, and resource usage

| ID | Проверка | P | Статус | Протоколы | Профили |
|---|---|---|---|---|---|
| `PERF-DEEP-PAGINATION` | Глубокая пагинация и большие выборки не деградируют неприемлемо | P2 | approved | rest, grpc, graphql | Nightly |
| `PERF-LATENCY-BASELINE` | Задержка ключевых операций в пределах SLO при обычной нагрузке | P2 | approved | rest, grpc, graphql, websocket | Nightly |
| `PERF-LOAD-THROUGHPUT` | Сервис выдерживает целевую нагрузку | P2 | approved | rest, grpc, graphql, websocket | Nightly |
| `PERF-METADATA-RELOAD-NO-BLOCK` | Перезагрузка кэша метаданных не блокирует обслуживание запросов надолго | P3 | approved | generic | Nightly |
| `PERF-NO-UNNEEDED-DEPENDENCY-CALLS` | Внешняя зависимость вызывается только когда её результат нужен | P3 | approved | generic | Nightly |
| `PERF-PAYLOAD-SIZE` | Размер ответов разумен и не растёт неограниченно | P3 | approved | rest, grpc, graphql, websocket | Nightly |
| `PERF-SOAK` | Длительная нагрузка не вызывает утечек и деградации | P3 | approved | rest, grpc, graphql, websocket | Nightly |
| `PERF-SPIKE` | Резкий всплеск нагрузки обрабатывается деградацией, а не отказом | P3 | approved | rest, grpc, graphql, websocket | Nightly |

## compatibility

Versioning, backward compatibility, and contract drift

| ID | Проверка | P | Статус | Протоколы | Профили |
|---|---|---|---|---|---|
| `COMPAT-BREAKING-CHANGE-DIFF` | Изменения контракта проверяются на обратную несовместимость | P0 | approved | rest, grpc, graphql, websocket | PR, CI, Regression, Nightly, Release |
| `COMPAT-ADDITIVE-CHANGE` | Добавление полей не ломает существующих клиентов | P1 | approved | rest, grpc, graphql, websocket | CI, Regression, Nightly, Release |
| `COMPAT-IMPLEMENTATION-MATCHES-CONTRACT` | Реализация соответствует опубликованному контракту | P1 | approved | rest, grpc, graphql, websocket | CI, Regression, Nightly, Release |
| `COMPAT-DEFAULT-VERSION` | Запрос без указания версии обслуживается задокументированной версией | P2 | approved | rest, graphql | CI, Regression, Nightly |
| `COMPAT-ENUM-EXTENSION` | Добавление значения enum не ломает клиентов | P2 | approved | rest, grpc, graphql, websocket | CI, Regression, Nightly |
| `COMPAT-UPGRADE-STORED-DATA-STABLE` | Обновление сервера не меняет сохранённые объекты и не запускает побочных действий | P2 | approved | generic | CI, Regression, Nightly |
| `COMPAT-DEPRECATION-SIGNALS` | Устаревающие операции помечены Deprecation и Sunset | P3 | approved | rest, graphql | Regression, Nightly |
| `COMPAT-MIXED-VERSION-WRITE-STABILITY` | Экземпляры разных версий при поэтапном обновлении не перезаписывают общий объект по кругу | P3 | approved | generic | Regression, Nightly |

## files

File upload, download, and binary content

| ID | Проверка | P | Статус | Протоколы | Профили |
|---|---|---|---|---|---|
| `FILE-DOWNLOAD-AUTHZ` | Скачивание файлов проверяет права и срок действия ссылок | P0 | approved | rest | PR, CI, Regression, Nightly, Release |
| `FILE-UPLOAD-TYPE-VALIDATION` | Тип файла проверяется по содержимому, а не только по расширению | P0 | approved | rest | PR, CI, Regression, Nightly, Release |
| `FILE-ARCHIVE-BOMB` | Архивные и графические бомбы не исчерпывают ресурсы | P1 | approved | rest | Regression, Nightly |
| `FILE-FILENAME-SANITIZATION` | Имя загружаемого файла санитизируется | P1 | approved | rest | CI, Regression, Nightly, Release |
| `FILE-MALICIOUS-CONTENT` | Вредоносное содержимое обнаруживается или изолируется | P1 | approved | rest | CI, Regression, Nightly, Release |
| `FILE-UPLOAD-KEY-COLLISION` | Загрузка не перезаписывает чужой файл с тем же именем или ключом хранилища | P1 | approved | rest | CI, Regression, Nightly, Release |
| `FILE-UPLOAD-SIZE-LIMIT` | Лимит размера загружаемого файла соблюдается | P1 | approved | rest | CI, Regression, Nightly, Release |
| `FILE-DOWNLOAD-HEADERS` | Скачивание отдаёт корректные Content-Type, Content-Disposition и nosniff | P2 | approved | rest | CI, Regression, Nightly |
| `FILE-EMPTY-AND-MALFORMED-MULTIPART` | Пустой файл и некорректный multipart обрабатываются корректно | P2 | approved | rest | CI, Regression, Nightly |
| `FILE-MALFORMED-STRUCTURE` | Повреждённый файл при разборе метаданных даёт 4xx, а не падение процесса | P2 | approved | rest | CI, Regression, Nightly |
| `FILE-ROUNDTRIP-EXACT` | Загруженный файл скачивается байт в байт | P2 | draft | rest | Regression, Nightly |
| `FILE-ABORTED-UPLOAD-CLEANUP` | Прерванная загрузка не оставляет данных в хранилище и не учитывается в квоте | P3 | approved | rest | Regression, Nightly |
| `FILE-METADATA-STRIP` | Метаданные изображений с ПДн удаляются | P3 | approved | rest | Regression, Nightly |
| `FILE-MULTIPART-METADATA-SAVED` | Метаданные из полей multipart сохраняются вместе с файлом | P3 | approved | rest | Regression, Nightly |
| `FILE-RANGE-REQUESTS` | Частичное скачивание через Range работает по контракту | P3 | approved | rest | Regression, Nightly |
| `FILE-TRANSFORM-LIMITS` | Лимит трансформации файла пропускает допустимые комбинации и отклоняет превышение | P3 | approved | rest | Regression, Nightly |
| `FILE-TRANSFORM-STORAGE-PARITY` | Трансформации файла работают на каждом поддерживаемом хранилище | P3 | approved | rest | Regression, Nightly |

## async

Webhooks, events, background jobs, and messaging

| ID | Проверка | P | Статус | Протоколы | Профили |
|---|---|---|---|---|---|
| `ASYNC-WEBHOOK-SIGNATURE` | Вебхуки подписаны, подпись проверяется, повтор отклоняется | P0 | approved | rest, graphql | PR, CI, Regression, Nightly, Release |
| `ASYNC-WEBHOOK-URL-SSRF` | URL вебхука не может указывать на внутренние адреса | P0 | approved | rest, graphql | PR, CI, Regression, Nightly, Release |
| `ASYNC-EVENT-PATH-SAME-RULES` | Событийный путь применяет те же фильтры и границы доступа, что и плановый | P1 | approved | rest, generic | CI, Regression, Nightly, Release |
| `ASYNC-IDEMPOTENT-CONSUMER` | Повторная доставка события обрабатывается однократно | P1 | approved | rest, grpc, graphql, websocket | CI, Regression, Nightly, Release |
| `ASYNC-EVENT-ORDERING` | Нарушение порядка событий не портит состояние | P2 | approved | rest, grpc, graphql, websocket | Regression, Nightly |
| `ASYNC-JOB-LIFECYCLE` | Фоновая задача проходит статусы и отдаёт результат | P2 | approved | rest, grpc, graphql, websocket | CI, Regression, Nightly |
| `ASYNC-MESSAGE-VALIDATION` | Входящие сообщения брокера валидируются по схеме так же, как HTTP-запросы | P2 | approved | generic | CI, Regression, Nightly |
| `ASYNC-RPC-ERROR-PROPAGATION` | Ошибка обработчика в схеме запрос-ответ через брокер возвращается вызывающему | P2 | approved | generic | CI, Regression, Nightly |
| `ASYNC-SSE-STREAM` | Потоковый ответ SSE работает для всех методов и отдаёт text/event-stream | P2 | approved | rest | CI, Regression, Nightly |
| `ASYNC-WEBHOOK-RETRY` | Неуспешная доставка вебхука повторяется с backoff и ограничением | P2 | approved | rest, graphql | Regression, Nightly |
| `ASYNC-DEAD-LETTER` | Необрабатываемые сообщения уходят в DLQ без блокировки очереди | P3 | approved | rest, grpc, graphql, websocket | Regression, Nightly |
| `ASYNC-JOB-CANCEL` | Отмена фоновой задачи останавливает её и не оставляет частичных эффектов | P3 | approved | rest, grpc, graphql, websocket | Regression, Nightly |
| `ASYNC-OUTBOUND-REQUEST-HEADERS` | Исходящий запрос сервера содержит корректный Host, в том числе с нестандартным портом | P3 | approved | generic | Regression, Nightly |
| `ASYNC-SCHEDULE-DST-TRANSITION` | Расписание на несуществующее или повторяющееся местное время срабатывает по правилу | P3 | draft | generic | Nightly |
| `ASYNC-SCHEDULE-LONG-UPTIME` | Задача по расписанию срабатывает и после длительной непрерывной работы процесса | P3 | approved | generic | Regression, Nightly |

## graphql

GraphQL-specific query, schema, and abuse controls

| ID | Проверка | P | Статус | Протоколы | Профили |
|---|---|---|---|---|---|
| `GQL-FIELD-LEVEL-AUTHZ` | Авторизация применяется на уровне полей и вложенных резолверов | P0 | approved | graphql | PR, CI, Regression, Nightly, Release |
| `GQL-ALIAS-BATCH-ABUSE` | Алиасы и batch-запросы не обходят rate limit | P1 | approved | graphql | CI, Regression, Nightly, Release |
| `GQL-COMPLEXITY-LIMIT` | Стоимость запроса ограничена (поля, списки, first/last) | P1 | approved | graphql | CI, Regression, Nightly, Release |
| `GQL-CSRF-GET-MUTATION` | Мутации не выполняются через GET и простые Content-Type | P1 | approved | graphql | CI, Regression, Nightly, Release |
| `GQL-DEPTH-LIMIT` | Глубина запроса ограничена | P1 | approved | graphql | CI, Regression, Nightly, Release |
| `GQL-INPUT-VALIDATION` | Входные типы и переменные валидируются | P1 | approved | graphql | CI, Regression, Nightly, Release |
| `GQL-ERRORS-NO-LEAK` | Ошибки GraphQL не раскрывают внутренние детали | P2 | approved | graphql | CI, Regression, Nightly |
| `GQL-GATEWAY-ROUTING` | В объединённой схеме каждое поле направляется в свой upstream | P2 | approved | graphql | CI, Regression, Nightly |
| `GQL-INTROSPECTION` | Introspection отключён или ограничен в продуктиве | P2 | approved | graphql | CI, Regression, Nightly |
| `GQL-PARTIAL-DATA` | Частичные результаты с ошибками соответствуют спецификации nullability | P2 | approved | graphql | CI, Regression, Nightly |
| `GQL-REST-ENDPOINT-PARITY` | Операция, опубликованная как REST-эндпоинт, выполняется так же, как исходный GraphQL-запрос | P2 | approved | graphql, rest | CI, Regression, Nightly |
| `GQL-EQUIVALENT-SELECTION-FORMS` | Эквивалентные формы выбора полей GraphQL дают одинаковые данные | P3 | approved | graphql | Regression, Nightly |
| `GQL-ERROR-EXTENSIONS-SHAPE` | Поля extensions ошибки GraphQL не дублируются во вложенных объектах | P3 | approved | graphql | Regression, Nightly |
| `GQL-FIELD-SUGGESTIONS` | Подсказки «Did you mean» не раскрывают схему при закрытом introspection | P3 | approved | graphql | Regression, Nightly |

## websocket

WebSocket connection, message, and subscription behavior

| ID | Проверка | P | Статус | Протоколы | Профили |
|---|---|---|---|---|---|
| `WS-HANDSHAKE-AUTH` | Установление соединения требует аутентификации | P0 | approved | websocket | PR, CI, Regression, Nightly, Release |
| `WS-SUBSCRIPTION-AUTHZ` | Подписки и сообщения авторизуются по каждому каналу | P0 | approved | websocket | PR, CI, Regression, Nightly, Release |
| `WS-ORIGIN-CHECK` | Проверка Origin защищает от cross-site WebSocket hijacking | P1 | approved | websocket | CI, Regression, Nightly, Release |
| `WS-TOKEN-EXPIRY` | Истечение или отзыв токена учитывается в открытом соединении | P1 | approved | websocket | CI, Regression, Nightly, Release |
| `WS-MALFORMED-MESSAGE` | Некорректные сообщения не рвут соединение без ответа | P2 | approved | websocket | CI, Regression, Nightly |
| `WS-MESSAGE-LIMITS` | Размер и частота сообщений ограничены | P2 | approved | websocket | CI, Regression, Nightly |
| `WS-SLOW-CONSUMER-NO-SILENT-LOSS` | Медленный клиент подписки не теряет сообщения молча | P2 | approved | websocket, graphql | Regression, Nightly |
| `WS-SUBSCRIPTION-EVENTS-DELIVERED` | Подписка получает события создания, изменения и удаления | P2 | approved | websocket, graphql | CI, Regression, Nightly |
| `WS-MULTIPLE-ENDPOINTS-INDEPENDENT` | Несколько WebSocket-эндпоинтов на разных путях работают независимо | P3 | approved | websocket | Regression, Nightly |
| `WS-RECONNECT-RESUME` | Переподключение восстанавливает подписки без потери и дублей сверх контракта | P3 | approved | websocket | Regression, Nightly |

## privacy

Personal data handling, masking, consent, and erasure

| ID | Проверка | P | Статус | Протоколы | Профили |
|---|---|---|---|---|---|
| `PRIV-CONSENT-ENFORCEMENT` | Обработка, требующая согласия, не выполняется без него | P1 | approved | rest, grpc, graphql, websocket | CI, Regression, Nightly, Release |
| `PRIV-DATA-MASKING` | Чувствительные данные маскируются в ответах по политике | P1 | approved | rest, grpc, graphql, websocket | CI, Regression, Nightly, Release |
| `PRIV-RESPONSE-FOREIGN-DATA` | Ответ не содержит фрагментов данных других запросов и памяти процесса | P1 | approved | rest, generic | Regression, Nightly |
| `PRIV-ERASURE` | Удаление персональных данных по запросу выполняется полностью | P2 | approved | rest, grpc, graphql, websocket | CI, Regression, Nightly |
| `PRIV-IMPORT-URL-CREDENTIALS-NOT-STORED` | Учётные данные из URL источника импорта не сохраняются после завершения импорта | P2 | approved | generic | CI, Regression, Nightly |
| `PRIV-SELF-DATA-EXPORT` | Экспорт собственных данных содержит только данные пользователя | P3 | approved | rest, grpc, graphql, websocket | Regression, Nightly |

## requirements

Requirement transfer errors - spec vs contract vs implementation, unspecified behavior

| ID | Проверка | P | Статус | Протоколы | Профили |
|---|---|---|---|---|---|
| `REQ-CONTRACT-CONTRADICTS-SPEC` | Поведение по контракту не противоречит ТЗ | P1 | approved | generic | CI, Regression, Nightly, Release |
| `REQ-SPEC-NOT-IN-CONTRACT` | Требование ТЗ не потеряно по пути в контракт и реализацию | P1 | approved | generic | CI, Regression, Nightly, Release |
| `REQ-CONTRACT-SELF-CONSISTENCY` | Контракт не противоречит сам себе и своей прежней версии | P2 | approved | rest, grpc, graphql | CI, Regression, Nightly |
| `REQ-CROSS-CLIENT-CONSISTENCY` | Одно правило продукта одинаково в API разных клиентов | P2 | approved | generic | CI, Regression, Nightly |
| `REQ-UNSPECIFIED-BEHAVIOR-PROBE` | Неописанное поведение выясняется тестом и сравнивается со стандартом и здравым смыслом | P2 | approved | rest, grpc, graphql, websocket | CI, Regression, Nightly |

## db

Database - schema and constraints, migrations, indexes and query plans, stored logic, data integrity, application queries

| ID | Проверка | P | Статус | Протоколы | Профили |
|---|---|---|---|---|---|
| `DB-ACCESS-SCOPE-IN-QUERY` | Граница доступа задаётся в самом запросе к БД | P1 | draft | db | Regression |
| `DB-API-DATA-MATCH` | После операции API в БД изменены ровно ожидаемые строки с ожидаемыми значениями | P1 | draft | db | Regression |
| `DB-DYNAMIC-SQL-PARAMETERIZED` | Значения и идентификаторы из ввода и из БД попадают в SQL параметрами или по allowlist | P1 | draft | db | Regression |
| `DB-KEYS-AND-CONSTRAINTS` | Ключи и ограничения защищают целостность независимо от приложения | P1 | draft | db | Regression |
| `DB-ROLES-AND-PRIVILEGES` | Роли БД приложения имеют минимальные права, переключение ролей безопасно | P1 | draft | db | Regression |
| `DB-SENSITIVE-DATA-PROTECTED` | Чувствительные данные хранятся защищённо | P1 | draft | db | Regression |
| `DB-COLLATION-COMPARISON` | Сравнение строк в БД соответствует назначению колонки | P2 | draft | db | Regression |
| `DB-IDENTIFIER-QUOTING` | Имена объектов БД экранируются во всех служебных и генерируемых запросах | P2 | draft | db | Regression |
| `DB-IMPORT-CONSISTENCY` | Импорт не оставляет частичного состояния вне документированной политики | P2 | draft | db | Regression |
| `DB-METADATA-CACHE-FRESH` | Кэш метаданных схемы в сервисе актуален после изменений БД | P2 | draft | db | Regression |
| `DB-MIGRATIONS-SAFE` | Миграции схемы применяются предсказуемо и не портят данные | P2 | draft | db | Regression |
| `DB-QUERY-INDEX-USAGE` | Запросы приложения используют подходящие индексы на реалистичном объёме | P2 | draft | db | Regression |
| `DB-SCHEMA-MATCHES-SPEC` | Схема БД совпадает со спецификацией и контрактом API | P2 | draft | db | Regression |
| `DB-STORED-ROUTINES` | Хранимые процедуры и функции установлены и работают по спецификации | P2 | draft | db | Regression |
| `DB-TRIGGERS` | Триггеры срабатывают ровно на нужные события и изолированы | P2 | draft | db | Regression |
| `DB-TYPED-COMPARISONS` | Значения сравниваются и приводятся в типе колонки | P2 | draft | db | Regression |
| `DB-CATALOG-INTROSPECTION` | Чтение каталога схемы корректно и укладывается во время на больших схемах | P3 | draft | db | Regression |
| `DB-CONNECTION-HANDLING` | Соединения с БД управляются предсказуемо | P3 | draft | db | Regression |
| `DB-DEFAULT-PRECEDENCE` | Значения по умолчанию применяются по правилам СУБД при любом способе вставки | P3 | draft | db | Regression |
| `DB-GENERATED-SQL-SHAPE` | Генерируемый SQL не выполняет лишней работы | P3 | draft | db | Regression |
