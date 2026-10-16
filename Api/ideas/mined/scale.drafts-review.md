# Вычитка draft-записей масштабирования (внутренняя сессия, п. 4)

_Claude, 2026-10-16. Статус `approved` ставит только человек (`docs/BUG_MINING_PLAN.md`): здесь — рекомендация, решение bj._

Draft в библиотеке — 122; из выгрузки багов — 90 (ниже). Остальные 32 (`REAL-BFF-*`, `REAL-MOBILE-*`) — кандидаты из
реальных контрактов (`checks/generated/`, свой процесс), сюда не входят.

Все записи прошли ревью идей: ghsa-maven и hasura — ревью bj, остальные — перекрёстное ревью ChatGPT и Qwen по правилу
сверки (`mining/README.md`, шаги 6–7, п. 7), расхождения — решение bj. Автоматические проверки (шаги-действия, источник
ожидания, условия стенда для partial/manual, обрывки списков, кластер в review-файле) — без замечаний после правок: в
INJ-SCHEMA-IDENTIFIER-CODEGEN и HARD-SETUP-ENDPOINTS-PROTECTED добавлены условия стенда.

Рекомендация: **все 90 — `approved`**. Если ценность спорных (ниже) вызывает сомнения — оставить их в draft.

## Принятые при несогласии хотя бы одной модели

| Запись | Партия | Возражение |
|---|---|---|
| OBS-CONFIG-ENDPOINT-ACCURATE | kubernetes | модели 1–2 (ChatGPT) — reject: эндпоинт «не для машинного разбора»; принято по решению bj |
| HTTP-PATH-PREFIX-SEGMENT-BOUNDARY | ghsa-rubygems | Qwen — reject как инфраструктура (Rack::Static) |
| INJ-REFLECTED-XSS | ghsa-rubygems | Qwen — reject как UI; ограничено эндпоинтами с HTML-ответом |
| ASYNC-SCHEDULE-LONG-UPTIME | directus | Qwen — reject как soak-тест |
| FILE-TRANSFORM-STORAGE-PARITY | directus | Qwen — reject как матрица конфигурации продукта; сужено до трансформаций |
| HTTP-RESPONSE-MODE-HEADER-PARITY | kong | ChatGPT — reject: жизненный цикл плагинов Kong |
| AUTH-CONTACT-CHANGE-PREVIOUS-VALUE | supabase-auth | Qwen — reject: слишком специфично |
| RES-RELATION-CONNECT-DISCONNECT-CONFLICT | strapi | Qwen — покрыто RES-RELATION-ORDER-STABLE |
| REST-FILTER-NAME-COLLISION | postgrest | Qwen — синтаксис PostgREST |
| OBS-LOG-ENTRY-INTEGRITY | postgrest | ChatGPT и Qwen — reject: не API; принято по решению bj (доступ к журналу) |

## Все записи

| # | Запись | Партия | Ревью | Приоритет | Автоматизация | Заголовок |
|---|---|---|---|---|---|---|
| 1 | SEC-INTERNAL-CONTROL-PARAMS | ghsa-maven | ревью bj | P1 | partial | Заголовки и параметры подключения клиента не задают внутренние управляющие параметры операции |
| 2 | INJ-USER-CODE-EXECUTION | ghsa-maven | ревью bj | P1 | partial | Пользовательский код, исполняемый сервером, не получает доступа к ОС, файлам и сети |
| 3 | SEC-DISABLED-FEATURE-ENFORCED | ghsa-maven | ревью bj | P2 | full | Отключённая настройкой функция недоступна через все API и не попадает в токены |
| 4 | SEC-AUTHZ-PATH-RULE-PRECEDENCE | ghsa-maven | ревью bj | P2 | full | Правила доступа по путям применяются по наиболее точному совпадению, независимо от порядка объявления |
| 5 | SEC-OPAQUE-ID-INTEGRITY | ghsa-maven | ревью bj | P2 | full | Непрозрачный идентификатор, выданный сервером, проверяется на подлинность |
| 6 | AUTH-CLIENT-ASSERTION-BINDING | ghsa-maven | ревью bj | P1 | full | Client assertion принимается только с ключом клиента, указанного в ней |
| 7 | AUTH-ACCOUNT-STATE-ALL-SCHEMES | ghsa-maven | ревью bj | P1 | full | Отключённая, заблокированная или истёкшая учётка не аутентифицируется ни одной схемой |
| 8 | AUTH-CLIENT-CERT-IDENTITY | ghsa-maven | ревью bj | P2 | partial | Личность из сертификата клиента извлекается однозначно |
| 9 | HARD-IP-ALLOWLIST | ghsa-maven | ревью bj | P2 | partial | Ограничение доступа по адресам и подсетям работает на границах для IPv4 и IPv6 |
| 10 | HTTP-HTTP2-RESOURCE-LIMITS | ghsa-maven | ревью bj | P3 | partial | Параметры HTTP/2 со стороны клиента не заставляют сервер буферизовать и работать без предела |
| 11 | AUTH-JWT-VALID-ACCEPTED | hasura | ревью bj | P2 | full | Валидный токен принимается при всех поддерживаемых алгоритмах, наборах ключей и настройках claims |
| 12 | GQL-REST-ENDPOINT-PARITY | hasura | ревью bj | P2 | full | Операция, опубликованная как REST-эндпоинт, выполняется так же, как исходный GraphQL-запрос |
| 13 | OBS-TELEMETRY-FORMAT | hasura | ревью bj | P3 | partial | Экспортируемая телеметрия соответствует документированной структуре и соглашениям OpenTelemetry |
| 14 | WS-SLOW-CONSUMER-NO-SILENT-LOSS | hasura | ревью bj | P2 | partial | Медленный клиент подписки не теряет сообщения молча |
| 15 | SEC-AUTHZ-RULE-READ-WRITE-PARITY | hasura | ревью bj | P1 | full | Условие прав по связанной записи действует в записи так же, как в чтении |
| 16 | GQL-GATEWAY-ROUTING | hasura | ревью bj | P2 | full | В объединённой схеме каждое поле направляется в свой upstream |
| 17 | REST-FILTER-RELATION-NO-DUPLICATES | hasura | ревью bj | P2 | full | Фильтр по полю связанной коллекции возвращает каждую запись один раз |
| 18 | PAGE-SORT-MULTI-KEY-PRIORITY | hasura | ревью bj | P3 | full | Сортировка по нескольким ключам соблюдает заданный клиентом порядок приоритета |
| 19 | RES-CACHE-EXPLICIT-INVALIDATION | hasura | ревью bj | P3 | full | Явный сброс кэша через API удаляет закэшированные ответы |
| 20 | RES-DB-OBJECT-NAMES | hasura | ревью bj | P2 | full | API по схеме БД работает с объектами в любом регистре, со спецсимволами и зарезервированными именами |
| 21 | HTTP-HEADER-REPEATED-LINES-ACCEPTED | kubernetes | ChatGPT + Qwen | P3 | full | Сотни повторяющихся строк одного заголовка в пределах лимита размера принимаются одинаково по HTTP/1.1 и HTTP/2 |
| 22 | RESIL-DEPENDENCY-TLS-RECOVERY | kubernetes | ChatGPT + Qwen | P2 | partial | Проверка доступности внешнего бэкенда проверяет его сертификат и восстанавливается без перезапуска |
| 23 | RESIL-TLS-CERT-RELOAD | kubernetes | ChatGPT + Qwen | P3 | partial | Сервер подхватывает заменённый TLS-сертификат без перезапуска |
| 24 | COMPAT-UPGRADE-STORED-DATA-STABLE | kubernetes | ChatGPT + Qwen | P2 | partial | Обновление сервера не меняет сохранённые объекты и не запускает побочных действий |
| 25 | COMPAT-MIXED-VERSION-WRITE-STABILITY | kubernetes | ChatGPT + Qwen | P3 | partial | Экземпляры разных версий при поэтапном обновлении не перезаписывают общий объект по кругу |
| 26 | VAL-UPLOADED-SCHEMA-FORMATS | kubernetes | ChatGPT + Qwen | P3 | full | Загружаемая клиентом схема с документированными форматами принимается без ложных предупреждений |
| 27 | OBS-CONFIG-ENDPOINT-ACCURATE | kubernetes | ChatGPT + Qwen ⚠ | P3 | partial | Служебный эндпоинт конфигурации показывает фактические значения |
| 28 | PERF-NO-UNNEEDED-DEPENDENCY-CALLS | kubernetes | ChatGPT + Qwen | P3 | full | Внешняя зависимость вызывается только когда её результат нужен |
| 29 | VAL-TIGHTENED-RULES-STORED-DATA | kubernetes | ChatGPT + Qwen | P2 | full | Сохранённые до ужесточения валидации значения обрабатываются одинаково на всех путях записи |
| 30 | AUTH-IDENTITY-ATTRIBUTES-ALL-SCHEMES | kubernetes | ChatGPT + Qwen | P2 | full | Атрибуты идентичности, которые даёт источник, сохраняются при любом способе аутентификации |
| 31 | RES-ALLOCATED-VALUE-RELEASE | kubernetes | ChatGPT + Qwen | P2 | partial | Выделенное из пула значение не выдаётся повторно, пока прежний владелец не удалён окончательно |
| 32 | SEC-ALT-REPRESENTATION-ACCESS | ghsa-rubygems | ChatGPT + Qwen | P1 | full | Закрытый ресурс недоступен ни через одно альтернативное представление |
| 33 | INJ-ARCHIVE-ENTRY-NAME-EVAL | ghsa-rubygems | ChatGPT + Qwen | P1 | full | Имена файлов внутри загруженного репозитория или архива не исполняются как код |
| 34 | AUTH-PROTOCOL-SESSION-OWNER-BINDING | ghsa-rubygems | ChatGPT + Qwen | P1 | full | Идентификатор протокольной сессии привязан к аутентифицированному владельцу |
| 35 | AUTH-OAUTH-PUBLIC-CLIENT-CONSENT | ghsa-rubygems | ChatGPT + Qwen | P2 | full | Повторная авторизация публичного OAuth-клиента не выполняется без участия пользователя |
| 36 | HTTP-PATH-PREFIX-SEGMENT-BOUNDARY | ghsa-rubygems | ChatGPT + Qwen ⚠ | P2 | full | Правило по префиксу пути соблюдает границу сегмента |
| 37 | INJ-REFLECTED-XSS | ghsa-rubygems | ChatGPT + Qwen ⚠ | P2 | full | Параметры запроса не отражаются в HTML-ответе без экранирования |
| 38 | PRIV-IMPORT-URL-CREDENTIALS-NOT-STORED | ghsa-rubygems | ChatGPT + Qwen | P2 | full | Учётные данные из URL источника импорта не сохраняются после завершения импорта |
| 39 | REST-FILTER-OPERATION-PARITY | directus | ChatGPT + Qwen | P2 | full | Один фильтр даёт согласованный результат в списке, агрегации и вложенной выборке |
| 40 | SEC-AUTHZ-DYNAMIC-VARIABLES | directus | ChatGPT + Qwen | P2 | full | Динамические переменные в правилах доступа действуют как эквивалентные статические значения |
| 41 | VAL-DYNAMIC-VARIABLES-TYPE | directus | ChatGPT + Qwen | P3 | full | Правило валидации с динамической переменной сравнивает значения по типу поля |
| 42 | ASYNC-SCHEDULE-LONG-UPTIME | directus | ChatGPT + Qwen ⚠ | P3 | partial | Задача по расписанию срабатывает и после длительной непрерывной работы процесса |
| 43 | WS-SUBSCRIPTION-EVENTS-DELIVERED | directus | ChatGPT + Qwen | P2 | full | Подписка получает события создания, изменения и удаления |
| 44 | FILE-MULTIPART-METADATA-SAVED | directus | ChatGPT + Qwen | P3 | full | Метаданные из полей multipart сохраняются вместе с файлом |
| 45 | RES-RELATION-NULL-TARGET-ROWS | directus | ChatGPT + Qwen | P3 | full | Связь многие-ко-многим возвращает записи связующей таблицы с пустой ссылкой |
| 46 | RES-RELATIONS-SHARED-JUNCTION-ISOLATION | directus | ChatGPT + Qwen | P2 | full | Связи через общую связующую таблицу возвращают каждая только свои данные |
| 47 | AUTH-EXTERNAL-IDP-MISSING-ATTRIBUTES | directus | ChatGPT + Qwen | P3 | full | Вход через внешний IdP без необязательных атрибутов профиля обрабатывается по требованиям |
| 48 | FILE-TRANSFORM-STORAGE-PARITY | directus | ChatGPT + Qwen ⚠ | P3 | partial | Трансформации файла работают на каждом поддерживаемом хранилище |
| 49 | WS-MULTIPLE-ENDPOINTS-INDEPENDENT | directus | ChatGPT + Qwen | P3 | full | Несколько WebSocket-эндпоинтов на разных путях работают независимо |
| 50 | HTTP-WWW-AUTHENTICATE-SYNTAX | kong | ChatGPT + Qwen | P3 | full | Заголовок WWW-Authenticate в ответе 401 соответствует синтаксису RFC |
| 51 | ASYNC-OUTBOUND-REQUEST-HEADERS | kong | ChatGPT + Qwen | P3 | full | Исходящий запрос сервера содержит корректный Host, в том числе с нестандартным портом |
| 52 | HTTP-RESPONSE-MODE-HEADER-PARITY | kong | ChatGPT + Qwen ⚠ | P3 | full | Настроенные заголовки ответа присутствуют во всех режимах обработки ответа |
| 53 | BIZ-CONFIG-SCOPE-PRECEDENCE | kong | ChatGPT + Qwen | P2 | full | Настройка более узкого уровня имеет приоритет над глобальной |
| 54 | PAGE-NEXT-LINK-VALID | kong | ChatGPT + Qwen | P2 | full | Ссылка next ведёт на ту же коллекцию, сохраняет фильтры и работает |
| 55 | HARD-WILDCARD-DOMAIN-MATCH | kong | ChatGPT + Qwen | P1 | full | Шаблон домена с wildcard совпадает только с поддоменами указанного домена |
| 56 | OBS-REQUEST-LOG-ALL-ATTEMPTS | kong | ChatGPT + Qwen | P3 | partial | Журнал запроса с повторами содержит каждую попытку, включая последнюю |
| 57 | HTTP-ROUTE-PROTOCOL-CONDITION | kong | ChatGPT + Qwen | P3 | full | Условие маршрута для одного протокола не блокирует маршрут по другому разрешённому протоколу |
| 58 | HTTP-RESPONSE-FRAMING-HEADERS | kong | ChatGPT + Qwen | P2 | full | Ответ не содержит одновременно Content-Length и Transfer-Encoding |
| 59 | AUTH-BASIC-CREDENTIALS-SPECIAL-CHARS | kong | ChatGPT + Qwen | P3 | full | Basic-аутентификация принимает пароль с двоеточием, пробелами и UTF-8 |
| 60 | OBS-METRICS-LABEL-CARDINALITY | ghsa-go | ChatGPT + Qwen | P2 | full | Значения из запроса не создают неограниченно новых серий метрик |
| 61 | SEC-POLICY-TEMPLATE-USER-DATA | ghsa-go | ChatGPT + Qwen | P1 | full | Данные пользователя, подставляемые в шаблон политики доступа, не работают как wildcard |
| 62 | HARD-DENYLIST-EVERY-ENTRY | ghsa-go | ChatGPT + Qwen | P2 | full | Каждый элемент списка запрещённых значений отклоняется |
| 63 | INJ-RESERVED-PATH-WRITE | ghsa-go | ChatGPT + Qwen | P1 | full | Запись файлов через API не попадает в служебные каталоги |
| 64 | HARD-ROUTE-SHARED-BACKEND-ISOLATION | ghsa-go | ChatGPT + Qwen | P2 | full | Маршруты шлюза к одному бэкенду применяют каждый свои фильтры |
| 65 | SEC-AUTHZ-EXPLICIT-OVER-INHERITED | ghsa-go | ChatGPT + Qwen | P1 | full | Явное пониженное право на дочерний объект имеет приоритет над унаследованным |
| 66 | HARD-BACKUP-RESTORE-PROTECTED | ghsa-go | ChatGPT + Qwen | P1 | full | Восстановление из резервной копии не обходит защиту записи |
| 67 | SEC-AUTHZ-LIST-CHECK-CONSISTENCY | ghsa-go | ChatGPT + Qwen | P2 | full | Перечисление субъектов и объектов с доступом согласовано с точечной проверкой |
| 68 | HARD-SETUP-ENDPOINTS-PROTECTED | ghsa-go | ChatGPT + Qwen | P1 | partial | Эндпоинты первоначальной настройки не позволяют захватить экземпляр |
| 69 | INJ-SCHEMA-IDENTIFIER-CODEGEN | ghsa-composer | ChatGPT + Qwen | P1 | partial | Идентификаторы пользовательской схемы не внедряют код и SQL при генерации кода и DDL |
| 70 | INJ-USER-DATA-CALLABLE | ghsa-composer | ChatGPT + Qwen | P1 | full | Данные пользователя не позволяют вызвать серверную функцию вне allowlist |
| 71 | HARD-OUTBOUND-CREDENTIALS-SCOPE | ghsa-composer | ChatGPT + Qwen | P1 | full | Учётные данные своего сайта не уходят в исходящие запросы к другим хостам |
| 72 | AUTH-EXTERNAL-ID-EXACT-MATCH | ghsa-composer | ChatGPT + Qwen | P1 | full | Внешний идентификатор субъекта сравнивается побайтно в паре издатель и subject |
| 73 | AUTH-OAUTH-OUTBOUND-SCOPE | supabase-auth | ChatGPT + Qwen | P3 | full | Запрос авторизации к внешнему провайдеру содержит запрошенные scope без устаревших значений по умолчанию |
| 74 | AUTH-IMPORTED-PASSWORD-HASH | supabase-auth | ChatGPT + Qwen | P2 | full | Пользователь, импортированный с хешем пароля поддерживаемого алгоритма, входит по исходному паролю |
| 75 | AUTH-CONTACT-CHANGE-PREVIOUS-VALUE | supabase-auth | ChatGPT + Qwen ⚠ | P3 | full | Смена телефона или email на ранее использованный этим пользователем проходит подтверждение |
| 76 | GQL-ERROR-EXTENSIONS-SHAPE | apollo-server | ChatGPT + Qwen | P3 | full | Поля extensions ошибки GraphQL не дублируются во вложенных объектах |
| 77 | HTTP-CACHEABLE-RESPONSE-CACHE-CONTROL | apollo-server | ChatGPT + Qwen | P3 | full | Кэшируемый ответ содержит Cache-Control по итоговой политике |
| 78 | RES-RELATION-CONNECT-DISCONNECT-CONFLICT | strapi | ChatGPT + Qwen ⚠ | P3 | full | Подключение с позицией относительно отключаемой в том же запросе связи обрабатывается корректно |
| 79 | RES-BULK-SINGLE-VALIDATION-PARITY | strapi | ChatGPT + Qwen | P2 | full | Массовая операция валидирует так же, как одиночная |
| 80 | AUTH-SAML-ASSERTION-REPLAY | ghsa-nuget | ChatGPT + Qwen | P1 | full | Повторно предъявленное SAML-утверждение отклоняется |
| 81 | OBS-METRICS-VALUE-RANGE | postgrest | ChatGPT + Qwen | P3 | partial | Gauge-метрики с известными границами остаются в них после сбоев и восстановления |
| 82 | OBS-SERVER-TIMING-ACCURATE | postgrest | ChatGPT + Qwen | P3 | partial | Server-Timing отражает фактическую длительность этапов |
| 83 | REST-ALIASED-EMBED-FILTER-INDEPENDENCE | postgrest | ChatGPT + Qwen | P2 | full | Вложения одного ресурса под разными алиасами фильтруются независимо |
| 84 | REST-FILTER-UNSELECTED-FIELD | postgrest | ChatGPT + Qwen | P2 | full | Фильтр по полю, не входящему в выбор полей, работает |
| 85 | REST-FILTER-NAME-COLLISION | postgrest | ChatGPT + Qwen ⚠ | P3 | full | Фильтр по полю с именем вложенного ресурса применяется к полю |
| 86 | REST-NEGOTIATED-FORMAT-CONFORMANCE | postgrest | ChatGPT + Qwen | P3 | full | Ответ в согласованном формате соответствует спецификации формата |
| 87 | REST-CUSTOM-MEDIA-TYPE-EMPTY-RESULT | postgrest | ChatGPT + Qwen | P3 | full | Пустой результат в пользовательском медиатипе не вызывает внутреннюю ошибку |
| 88 | HTTP-PREFERENCE-APPLIED-ACCURATE | postgrest | ChatGPT + Qwen | P3 | full | Preference-Applied перечисляет ровно применённые предпочтения |
| 89 | OBS-LOG-ENTRY-INTEGRITY | postgrest | ChatGPT + Qwen ⚠ | P3 | partial | Записи журнала при всплеске параллельных запросов не склеиваются |
| 90 | PERF-METADATA-RELOAD-NO-BLOCK | postgrest | ChatGPT + Qwen | P3 | partial | Перезагрузка кэша метаданных не блокирует обслуживание запросов надолго |
