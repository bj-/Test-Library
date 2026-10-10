# Каталог проверок

Файл генерируется `python tools/build_catalog.py .` — не редактируйте вручную.

Всего проверок: **368** — approved: 320, draft: 32, needs_clarification: 16.
Протоколы: generic: 39, graphql: 191, grpc: 138, rest: 319, websocket: 59.

| Категория | Описание | Проверок |
|---|---|---:|
| [contract](#contract) | API contract and schema conformance | 25 |
| [resources](#resources) | Resource lifecycle and state transitions | 19 |
| [security](#security) | Authentication, authorization, and data isolation | 146 |
| [validation](#validation) | Input validation and normalization | 36 |
| [http-semantics](#http-semantics) | HTTP methods, headers, and status semantics | 13 |
| [errors](#errors) | Error response shape and consistency | 3 |
| [pagination](#pagination) | Pagination, filtering, and sorting | 13 |
| [idempotency](#idempotency) | Idempotent behavior and retry safety | 1 |
| [grpc-contract](#grpc-contract) | Protobuf and RPC contract conformance | 17 |
| [grpc-errors](#grpc-errors) | gRPC status and error details | 16 |
| [resilience](#resilience) | Timeouts, retries, dependency failures | 7 |
| [business-logic](#business-logic) | Domain rules, workflows, limits, and money | 11 |
| [concurrency](#concurrency) | Parallel requests, races, and lost updates | 6 |
| [observability](#observability) | Logs, audit trail, tracing, and health endpoints | 4 |
| [performance](#performance) | Latency, throughput, load, and resource usage | 6 |
| [compatibility](#compatibility) | Versioning, backward compatibility, and contract drift | 6 |
| [files](#files) | File upload, download, and binary content | 10 |
| [async](#async) | Webhooks, events, background jobs, and messaging | 8 |
| [graphql](#graphql) | GraphQL-specific query, schema, and abuse controls | 10 |
| [websocket](#websocket) | WebSocket connection, message, and subscription behavior | 7 |
| [privacy](#privacy) | Personal data handling, masking, consent, and erasure | 4 |

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
| `RES-BULK-LIMITS` | Массовые операции соблюдают лимиты и сообщают о каждом элементе | P2 | approved | rest, grpc, graphql | CI, Regression, Nightly |
| `RES-CREATE-RESPONSE-MATCHES-READ` | Ответ на создание и изменение совпадает с последующим чтением | P2 | approved | rest, grpc, graphql | CI, Regression, Nightly |
| `RES-LIST-REFLECTS-CHANGES` | Списки и счётчики отражают создание, изменение и удаление | P2 | approved | rest, grpc, graphql | CI, Regression, Nightly |
| `RES-READ-AFTER-WRITE` | Чтение после записи соответствует модели согласованности | P2 | approved | rest, grpc, graphql | Regression, Nightly |
| `RES-SOFT-DELETE-VISIBILITY` | Мягко удалённые ресурсы не видны в обычных операциях | P2 | approved | rest, grpc, graphql | CI, Regression, Nightly |
| `RES-TIMESTAMPS` | Метки времени создания и изменения ведут себя корректно | P2 | approved | rest, grpc, graphql | CI, Regression, Nightly |
| `RES-UNIQUENESS-NORMALIZATION` | Уникальность не обходится вариациями значения | P2 | approved | rest, grpc, graphql | CI, Regression, Nightly |
| `RES-UPDATE-MISSING` | Изменение несуществующего ресурса не создаёт его неявно | P2 | approved | rest, grpc, graphql | CI, Regression, Nightly |
| `RES-ARCHIVE-RESTORE` | Архивирование и восстановление сохраняют данные и связи | P3 | approved | rest, grpc, graphql | Regression, Nightly |

## security

Authentication, authorization, and data isolation

| ID | Проверка | P | Статус | Протоколы | Профили |
|---|---|---|---|---|---|
| `AUTH-CSRF` | Изменяющие операции с cookie-аутентификацией защищены от CSRF | P0 | approved | rest, graphql | PR, CI, Regression, Nightly, Release |
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
| `AUTH-API-KEY-LIFECYCLE` | API-ключи ограничены по правам, отзываются и не раскрываются | P1 | approved | rest, grpc, graphql, websocket | CI, Regression, Nightly, Release |
| `AUTH-BRUTE-FORCE-PROTECTION` | Перебор паролей ограничивается | P1 | approved | rest, graphql | Regression, Nightly |
| `AUTH-COOKIE-ATTRIBUTES` | Сессионные cookie имеют Secure, HttpOnly, SameSite и узкие Domain/Path | P1 | approved | rest, graphql | CI, Regression, Nightly, Release |
| `AUTH-JWT-HEADER-INJECTION` | Параметры kid, jku, x5u в заголовке JWT не позволяют подставить ключ | P1 | approved | rest, grpc, graphql, websocket | CI, Regression, Nightly, Release |
| `AUTH-OAUTH-REDIRECT-STATE` | OAuth/OIDC flow проверяет redirect_uri, state и PKCE | P1 | approved | rest, graphql | CI, Regression, Nightly, Release |
| `AUTH-OTP-BINDING` | Одноразовый код привязан к получателю и операции | P1 | approved | rest, graphql | CI, Regression, Nightly, Release |
| `AUTH-OTP-EXPIRY` | Одноразовый код перестаёт действовать после истечения срока | P1 | approved | rest, graphql | Regression, Nightly, Release |
| `AUTH-OTP-REUSE` | Одноразовый код нельзя использовать повторно и после выдачи нового | P1 | approved | rest, graphql | CI, Regression, Nightly, Release |
| `AUTH-OTP-SEND-LIMIT` | Частота отправки кодов ограничена (SMS bombing) | P1 | approved | rest, graphql | CI, Regression, Nightly, Release |
| `AUTH-PASSWORD-CHANGE-REVOKES` | Смена или сброс пароля завершает другие сессии | P1 | approved | rest, graphql | CI, Regression, Nightly, Release |
| `AUTH-SESSION-FIXATION` | Идентификатор сессии меняется после входа | P1 | approved | rest, graphql | CI, Regression, Nightly, Release |
| `AUTH-TOKEN-TYPE-CONFUSION` | Refresh, ID или сервисный токен не принимается как access-токен | P1 | approved | rest, grpc, graphql, websocket | CI, Regression, Nightly, Release |
| `AUTH-USER-ENUMERATION` | Ответы входа, регистрации и восстановления не раскрывают существование аккаунта | P1 | approved | rest, graphql | Regression, Nightly |
| `HARD-DEBUG-ENDPOINTS` | Отладочные и служебные эндпоинты недоступны извне | P1 | approved | rest, graphql | CI, Regression, Nightly, Release |
| `HARD-EXCESSIVE-DATA-EXPOSURE` | Ответы не содержат внутренних полей сверх контракта | P1 | approved | rest, grpc, graphql, websocket | CI, Regression, Nightly, Release |
| `HARD-EXPENSIVE-OPERATION-LIMITS` | Дорогие операции ограничены по ресурсам | P1 | approved | rest, grpc, graphql, websocket | Regression, Nightly |
| `HARD-HOST-HEADER` | Подмена Host и X-Forwarded-Host не влияет на ссылки и маршрутизацию | P1 | approved | rest, graphql | CI, Regression, Nightly, Release |
| `HARD-METHOD-OVERRIDE` | Заголовки переопределения метода не обходят авторизацию | P1 | approved | rest | CI, Regression, Nightly, Release |
| `HARD-SHADOW-API-VERSIONS` | Старые версии API и недокументированные маршруты не обходят защиту | P1 | approved | rest, graphql | CI, Regression, Nightly, Release |
| `HARD-TLS-ONLY` | API доступен только по TLS с актуальными настройками | P1 | approved | rest, grpc, graphql, websocket | CI, Regression, Nightly, Release |
| `INJ-FILTER-EXPRESSION` | Выражения фильтрации (OData, RSQL, JSONPath, GraphQL where) не позволяют выйти за ограничения | P1 | approved | rest, graphql | CI, Regression, Nightly, Release |
| `INJ-HEADER-CRLF` | CRLF в значениях не позволяет внедрять заголовки ответа | P1 | approved | rest | CI, Regression, Nightly, Release |
| `INJ-PROTOTYPE-POLLUTION` | Специальные ключи __proto__ и constructor не меняют поведение сервера | P1 | approved | rest, graphql | CI, Regression, Nightly, Release |
| `INJ-STORED-XSS` | Сохранённые данные с HTML/JS не создают XSS у потребителей API | P1 | approved | rest, graphql | CI, Regression, Nightly, Release |
| `INJ-TEMPLATE-SSTI` | Инъекция в серверные шаблоны не исполняется | P1 | approved | rest, grpc, graphql, websocket | CI, Regression, Nightly, Release |
| `INJ-UNSAFE-DESERIALIZATION` | Небезопасная десериализация пользовательских данных невозможна | P1 | approved | rest, grpc, graphql, websocket | CI, Regression, Nightly, Release |
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
| `SEC-AUTHN-MALFORMED` | Malformed credential is rejected | P1 | approved | rest, graphql, generic | CI, Regression, Nightly, Release |
| `SEC-AUTHZ-ASYNC-JOB` | Authorization is rechecked for asynchronous job access | P1 | approved | rest, graphql, generic | CI, Regression, Nightly, Release |
| `SEC-AUTHZ-ERROR-LEAK` | Authorization failures do not disclose protected data | P1 | approved | rest, graphql, generic | CI, Regression, Nightly, Release |
| `SEC-AUTHZ-METHOD-MATRIX` | Authorization is enforced for every method | P1 | approved | rest, graphql, generic | CI, Regression, Nightly, Release |
| `SEC-AUTHZ-REVOKE-ROLE` | Role revocation takes effect within policy window | P1 | approved | rest, graphql, generic | CI, Regression, Nightly, Release |
| `SEC-OWNERSHIP-REFERENCE-INDIRECT` | Indirect resource references preserve authorization | P1 | approved | rest, graphql, generic | CI, Regression, Nightly, Release |
| `SEC-ROLE-BULK-ADMIN` | Bulk admin actions require privilege for every target | P1 | approved | rest, graphql, generic | CI, Regression, Nightly, Release |
| `SEC-TOKEN-AUDIENCE` | Token for another audience is rejected | P1 | approved | rest, graphql, generic | CI, Regression, Nightly, Release |
| `SEC-TOKEN-REFRESH-REPLAY` | Refresh-token replay is rejected or rotated | P1 | approved | rest, graphql, generic | CI, Regression, Nightly, Release |
| `AUTH-JWT-TIME-CLAIMS` | Токены с nbf/iat в будущем и без exp обрабатываются по политике | P2 | approved | rest, grpc, graphql, websocket | CI, Regression, Nightly |
| `AUTH-PASSWORD-POLICY` | Политика паролей применяется на сервере | P2 | approved | rest, graphql | CI, Regression, Nightly |
| `AUTH-SESSION-TIMEOUT` | Сессия истекает после простоя и абсолютного срока | P2 | approved | rest, graphql | Regression, Nightly |
| `AUTH-TOKEN-IN-URL` | Учётные данные не передаются и не принимаются в URL | P2 | approved | rest, graphql | CI, Regression, Nightly |
| `HARD-BUSINESS-FLOW-AUTOMATION` | Чувствительные бизнес-потоки защищены от автоматизированного злоупотребления | P2 | approved | rest, grpc, graphql, websocket | Regression, Nightly |
| `HARD-CACHE-POISONING` | Неключевые заголовки не отравляют общий кэш | P2 | approved | rest, graphql | Regression, Nightly |
| `HARD-ID-PREDICTABILITY` | Предсказуемые идентификаторы не позволяют собрать данные перебором | P2 | approved | rest, grpc, graphql, websocket | CI, Regression, Nightly |
| `HARD-SENSITIVE-DATA-IN-URL` | Персональные данные и секреты не передаются в URL | P2 | approved | rest | CI, Regression, Nightly |
| `HARD-UNSAFE-API-CONSUMPTION` | Ответы сторонних API валидируются перед использованием | P2 | approved | rest, grpc, graphql, websocket | Regression, Nightly |
| `INJ-CSV-FORMULA` | Экспорт в CSV/XLSX нейтрализует формулы | P2 | approved | rest | CI, Regression, Nightly |
| `INJ-LOG-FORGING` | Пользовательские данные не позволяют подделывать записи журналов | P2 | approved | rest, grpc, graphql, websocket | Regression, Nightly |
| `INJ-REDOS` | Пользовательский ввод не вызывает катастрофический backtracking в regex | P2 | approved | rest, grpc, graphql, websocket | Regression, Nightly |
| `REST-CORS-POLICY` | Политика CORS | P2 | approved | rest | CI, Regression, Nightly |
| `REST-SECURITY-HEADERS` | Защитные HTTP-заголовки | P2 | approved | rest | CI, Regression, Nightly |
| `AUTH-CONCURRENT-SESSIONS` | Лимит одновременных сессий и устройств соблюдается | P3 | approved | rest, graphql | Regression, Nightly |
| `HARD-VERSION-DISCLOSURE` | Ответы не раскрывают версии ПО и инфраструктуры | P3 | approved | rest, graphql | Regression, Nightly |

## validation

Input validation and normalization

| ID | Проверка | P | Статус | Протоколы | Профили |
|---|---|---|---|---|---|
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
| `VAL-JSON-TOP-LEVEL-TYPE` | Неожиданный тип корня JSON отклоняется | P2 | approved | rest, graphql | CI, Regression, Nightly |
| `VAL-LARGE-COLLECTION-PAYLOAD` | Массив с очень большим числом элементов отклоняется или обрабатывается в пределах лимитов | P2 | approved | rest, grpc, graphql | CI, Regression, Nightly |
| `VAL-NESTED-OBJECT-ERRORS` | Ошибка во вложенном объекте указывает точный путь к полю | P2 | approved | rest, grpc, graphql | CI, Regression, Nightly |
| `VAL-QUERY-PARAM-POLLUTION` | Дублирующиеся query-параметры обрабатываются однозначно | P2 | approved | rest | CI, Regression, Nightly |
| `VAL-REGEX-PATTERN` | Поле с pattern принимает только совпадающие значения | P2 | approved | rest, graphql | CI, Regression, Nightly |
| `VAL-REQUIRED-HEADERS` | Обязательные и форматные заголовки валидируются | P2 | approved | rest | CI, Regression, Nightly |
| `VAL-WHITESPACE-HANDLING` | Пробелы по краям и строки из пробелов обрабатываются согласованно | P2 | approved | rest, grpc, graphql | CI, Regression, Nightly |
| `VAL-ALL-ERRORS-REPORTED` | Ошибки валидации нескольких полей возвращаются по контракту (все сразу или первая) | P3 | approved | rest, grpc, graphql | Regression, Nightly |
| `VAL-QUERY-ARRAY-FORMAT` | Массивы в query передаются в задокументированном формате | P3 | approved | rest | Regression, Nightly |

## http-semantics

HTTP methods, headers, and status semantics

| ID | Проверка | P | Статус | Протоколы | Профили |
|---|---|---|---|---|---|
| `HTTP-BODY-WITHOUT-CONTENT-TYPE` | Тело без Content-Type обрабатывается предсказуемо | P2 | approved | rest | CI, Regression, Nightly |
| `HTTP-HEADER-SIZE-LIMIT` | Слишком большие заголовки отклоняются контролируемо | P2 | approved | rest | CI, Regression, Nightly |
| `HTTP-REQUEST-SMUGGLING` | Противоречивые Content-Length и Transfer-Encoding не приводят к request smuggling | P2 | approved | rest | Regression, Nightly |
| `HTTP-UNKNOWN-ROUTE` | Неизвестный маршрут возвращает 404, а не 5xx или 200 | P2 | approved | rest | CI, Regression, Nightly |
| `REST-HEAD-GET-CONSISTENCY` | HEAD response is consistent with GET | P2 | approved | rest | CI, Regression, Nightly |
| `REST-METHOD-NOT-ALLOWED` | Unsupported HTTP method is rejected | P2 | approved | rest | CI, Regression, Nightly |
| `HTTP-ACCEPT-LANGUAGE` | Язык сообщений определяется Accept-Language с fallback | P3 | approved | rest, graphql | Regression, Nightly |
| `HTTP-BODY-ON-GET-DELETE` | Тело в GET/DELETE игнорируется или отклоняется по контракту | P3 | approved | rest | Regression, Nightly |
| `HTTP-COMPRESSION` | Сжатие ответа согласуется через Accept-Encoding | P3 | approved | rest | Regression, Nightly |
| `HTTP-OPTIONS-ALLOW` | OPTIONS возвращает согласованный список методов | P3 | approved | rest | Regression, Nightly |
| `HTTP-TRAILING-SLASH-CASE` | Вариации пути (слэш в конце, регистр, двойной слэш) обрабатываются единообразно | P3 | approved | rest | Regression, Nightly |
| `HTTP-URL-LENGTH-LIMIT` | Очень длинный URL отклоняется контролируемо | P3 | approved | rest | Regression, Nightly |
| `HTTP-VARY-HEADER` | Кэшируемые ответы содержат корректный Vary | P3 | approved | rest | Regression, Nightly |

## errors

Error response shape and consistency

| ID | Проверка | P | Статус | Протоколы | Профили |
|---|---|---|---|---|---|
| `ERR-INTERNAL-ERROR-SHAPE` | Внутренняя ошибка сервера возвращается в общей модели без утечек | P1 | approved | rest, grpc, graphql, websocket | CI, Regression, Nightly, Release |
| `ERR-STABLE-ERROR-CODES` | Машиночитаемые коды ошибок стабильны и задокументированы | P2 | approved | rest, grpc, graphql, websocket | CI, Regression, Nightly |
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
| `PAGE-SEARCH-SPECIAL-CHARS` | Поиск со спецсимволами и wildcard не ломается и не расширяет выборку | P2 | approved | rest, grpc, graphql | CI, Regression, Nightly |
| `PAGE-TOTAL-COUNT` | Общее число элементов согласовано с суммой страниц | P2 | approved | rest, grpc, graphql | CI, Regression, Nightly |
| `REST-FILTER-INVALID` | Невалидный фильтр | P2 | approved | rest | CI, Regression, Nightly |
| `REST-FILTER-SORT-COMPOSITION` | Filtering and sorting compose correctly | P2 | approved | rest, graphql | CI, Regression, Nightly |
| `REST-SORT-INVALID-FIELD` | Сортировка по неизвестному полю | P2 | approved | rest | CI, Regression, Nightly |
| `PAGE-SORT-NULLS-TIES` | Сортировка по полю с null и одинаковыми значениями детерминирована | P3 | approved | rest, grpc, graphql | Regression, Nightly |

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
| `RESIL-GRACEFUL-SHUTDOWN` | Перезапуск экземпляра не обрывает выполняющиеся запросы | P2 | approved | rest, grpc, graphql, websocket | Regression, Nightly |
| `RESIL-PARTIAL-DEGRADATION` | Отказ некритичной зависимости не ломает основной функционал | P2 | approved | rest, grpc, graphql, websocket | Regression, Nightly |
| `RESIL-CIRCUIT-BREAKER` | Circuit breaker размыкается и восстанавливается по политике | P3 | approved | rest, grpc, graphql, websocket | Regression, Nightly |

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
| `BIZ-CURRENCY-MISMATCH` | Смешение валют в операции обрабатывается явно | P2 | approved | rest, grpc, graphql | CI, Regression, Nightly |
| `BIZ-HIERARCHY-CYCLES` | Ссылка на себя и циклы в иерархии запрещены | P2 | approved | rest, grpc, graphql | CI, Regression, Nightly |
| `BIZ-SIDE-EFFECTS-ONCE` | Побочные эффекты (письма, push, события) выполняются ровно один раз | P2 | approved | rest, grpc, graphql | CI, Regression, Nightly |
| `BIZ-TIME-WINDOW` | Операции вне разрешённого временного окна отклоняются | P2 | approved | rest, grpc, graphql | CI, Regression, Nightly |

## concurrency

Parallel requests, races, and lost updates

| ID | Проверка | P | Статус | Протоколы | Профили |
|---|---|---|---|---|---|
| `CONC-COUNTER-INCREMENT` | Счётчики корректны при параллельных инкрементах | P1 | approved | rest, grpc, graphql | Regression, Nightly |
| `CONC-DOUBLE-SUBMIT` | Двойная отправка формы не создаёт дубликат операции | P1 | approved | rest, grpc, graphql | Regression, Nightly |
| `CONC-LOST-UPDATE` | Параллельные изменения не теряют друг друга молча | P1 | approved | rest, grpc, graphql | Regression, Nightly |
| `CONC-PARALLEL-CREATE-UNIQUE` | Параллельное создание с одним уникальным ключом создаёт один объект | P1 | approved | rest, grpc, graphql | Regression, Nightly |
| `CONC-STATE-TRANSITION-RACE` | Параллельные переходы состояния не нарушают автомат состояний | P1 | approved | rest, grpc, graphql | Regression, Nightly |
| `CONC-DELETE-VS-UPDATE` | Параллельные удаление и изменение не оставляют ресурс в противоречивом состоянии | P2 | approved | rest, grpc, graphql | Regression, Nightly |

## observability

Logs, audit trail, tracing, and health endpoints

| ID | Проверка | P | Статус | Протоколы | Профили |
|---|---|---|---|---|---|
| `OBS-NO-SECRETS-IN-LOGS` | Логи не содержат паролей, токенов и ПДн в открытом виде | P0 | approved | rest, grpc, graphql, websocket | Regression, Nightly |
| `OBS-AUDIT-TRAIL` | Чувствительные действия фиксируются в журнале аудита | P1 | approved | rest, grpc, graphql, websocket | CI, Regression, Nightly, Release |
| `OBS-HEALTH-ENDPOINTS` | Health-эндпоинты отражают состояние и не раскрывают детали | P2 | approved | rest, grpc, graphql, websocket | CI, Regression, Nightly |
| `OBS-TRACE-PROPAGATION` | Контекст трассировки принимается и передаётся дальше | P3 | approved | rest, grpc, graphql, websocket | Regression, Nightly |

## performance

Latency, throughput, load, and resource usage

| ID | Проверка | P | Статус | Протоколы | Профили |
|---|---|---|---|---|---|
| `PERF-DEEP-PAGINATION` | Глубокая пагинация и большие выборки не деградируют неприемлемо | P2 | approved | rest, grpc, graphql | Nightly |
| `PERF-LATENCY-BASELINE` | Задержка ключевых операций в пределах SLO при обычной нагрузке | P2 | approved | rest, grpc, graphql, websocket | Nightly |
| `PERF-LOAD-THROUGHPUT` | Сервис выдерживает целевую нагрузку | P2 | approved | rest, grpc, graphql, websocket | Nightly |
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
| `COMPAT-DEPRECATION-SIGNALS` | Устаревающие операции помечены Deprecation и Sunset | P3 | approved | rest, graphql | Regression, Nightly |

## files

File upload, download, and binary content

| ID | Проверка | P | Статус | Протоколы | Профили |
|---|---|---|---|---|---|
| `FILE-DOWNLOAD-AUTHZ` | Скачивание файлов проверяет права и срок действия ссылок | P0 | approved | rest | PR, CI, Regression, Nightly, Release |
| `FILE-UPLOAD-TYPE-VALIDATION` | Тип файла проверяется по содержимому, а не только по расширению | P0 | approved | rest | PR, CI, Regression, Nightly, Release |
| `FILE-ARCHIVE-BOMB` | Архивные и графические бомбы не исчерпывают ресурсы | P1 | approved | rest | Regression, Nightly |
| `FILE-FILENAME-SANITIZATION` | Имя загружаемого файла санитизируется | P1 | approved | rest | CI, Regression, Nightly, Release |
| `FILE-MALICIOUS-CONTENT` | Вредоносное содержимое обнаруживается или изолируется | P1 | approved | rest | CI, Regression, Nightly, Release |
| `FILE-UPLOAD-SIZE-LIMIT` | Лимит размера загружаемого файла соблюдается | P1 | approved | rest | CI, Regression, Nightly, Release |
| `FILE-DOWNLOAD-HEADERS` | Скачивание отдаёт корректные Content-Type, Content-Disposition и nosniff | P2 | approved | rest | CI, Regression, Nightly |
| `FILE-EMPTY-AND-MALFORMED-MULTIPART` | Пустой файл и некорректный multipart обрабатываются корректно | P2 | approved | rest | CI, Regression, Nightly |
| `FILE-METADATA-STRIP` | Метаданные изображений с ПДн удаляются | P3 | approved | rest | Regression, Nightly |
| `FILE-RANGE-REQUESTS` | Частичное скачивание через Range работает по контракту | P3 | approved | rest | Regression, Nightly |

## async

Webhooks, events, background jobs, and messaging

| ID | Проверка | P | Статус | Протоколы | Профили |
|---|---|---|---|---|---|
| `ASYNC-WEBHOOK-SIGNATURE` | Вебхуки подписаны, подпись проверяется, повтор отклоняется | P0 | approved | rest, graphql | PR, CI, Regression, Nightly, Release |
| `ASYNC-WEBHOOK-URL-SSRF` | URL вебхука не может указывать на внутренние адреса | P0 | approved | rest, graphql | PR, CI, Regression, Nightly, Release |
| `ASYNC-IDEMPOTENT-CONSUMER` | Повторная доставка события обрабатывается однократно | P1 | approved | rest, grpc, graphql, websocket | CI, Regression, Nightly, Release |
| `ASYNC-EVENT-ORDERING` | Нарушение порядка событий не портит состояние | P2 | approved | rest, grpc, graphql, websocket | Regression, Nightly |
| `ASYNC-JOB-LIFECYCLE` | Фоновая задача проходит статусы и отдаёт результат | P2 | approved | rest, grpc, graphql, websocket | CI, Regression, Nightly |
| `ASYNC-WEBHOOK-RETRY` | Неуспешная доставка вебхука повторяется с backoff и ограничением | P2 | approved | rest, graphql | Regression, Nightly |
| `ASYNC-DEAD-LETTER` | Необрабатываемые сообщения уходят в DLQ без блокировки очереди | P3 | approved | rest, grpc, graphql, websocket | Regression, Nightly |
| `ASYNC-JOB-CANCEL` | Отмена фоновой задачи останавливает её и не оставляет частичных эффектов | P3 | approved | rest, grpc, graphql, websocket | Regression, Nightly |

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
| `GQL-INTROSPECTION` | Introspection отключён или ограничен в продуктиве | P2 | approved | graphql | CI, Regression, Nightly |
| `GQL-PARTIAL-DATA` | Частичные результаты с ошибками соответствуют спецификации nullability | P2 | approved | graphql | CI, Regression, Nightly |
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
| `WS-RECONNECT-RESUME` | Переподключение восстанавливает подписки без потери и дублей сверх контракта | P3 | approved | websocket | Regression, Nightly |

## privacy

Personal data handling, masking, consent, and erasure

| ID | Проверка | P | Статус | Протоколы | Профили |
|---|---|---|---|---|---|
| `PRIV-CONSENT-ENFORCEMENT` | Обработка, требующая согласия, не выполняется без него | P1 | approved | rest, grpc, graphql, websocket | CI, Regression, Nightly, Release |
| `PRIV-DATA-MASKING` | Чувствительные данные маскируются в ответах по политике | P1 | approved | rest, grpc, graphql, websocket | CI, Regression, Nightly, Release |
| `PRIV-ERASURE` | Удаление персональных данных по запросу выполняется полностью | P2 | approved | rest, grpc, graphql, websocket | CI, Regression, Nightly |
| `PRIV-SELF-DATA-EXPORT` | Экспорт собственных данных содержит только данные пользователя | P3 | approved | rest, grpc, graphql, websocket | Regression, Nightly |
