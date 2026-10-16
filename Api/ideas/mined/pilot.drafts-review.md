# Вычитка 50 draft-записей пилота (внутренняя сессия, п. 4)

_Claude, 2026-10-16. Статус `approved` ставит только человек (`docs/BUG_MINING_PLAN.md`): здесь — рекомендация, решение bj._

Критерии: шаги исполнимы как действие теста; ожидание проверяемо и следует из источника; источник указан;
применимость (`when` / `skip_when`) ясна; запись не привязана к одному продукту (продуктовые детали — только в шагах-вариантах).

Сделано до решения (на тексте, без смены статуса):

- 72 шага-варианта «Добавить …» в 56 записях переписаны в форму действия (коммит `2ebb3ec`);
- обрывки списков, разрезанных по запятой генератором пилота, склеены в 13 записях библиотеки (5 из них — эти draft);
- ERR-STATUS-MATCHES-EFFECT: ожидание «Успех — 2xx.» заменено на «2xx — только когда изменение фактически применено…»;
- HARD-SLOW-CLIENT-LIMITS: предусловие об инструментах (TCP, TLS, HTTP/2, HTTP/3) — транспортные шаги без них пропускаются.

Рекомендация: **все 50 — `approved`**. Ниже — замечания, которые не мешают переводу, но стоит знать.

| # | Запись | Приоритет | Рекомендация | Замечание |
|---|---|---|---|---|
| 1 | REST-FILTER-OPERATOR-TYPE-MATRIX | P2 | approved | Часть шагов — PostgreSQL (доменные типы, составные типы); применимы только к API поверх СУБД |
| 2 | REST-FILTER-EQUIVALENT-FORMS | P3 | approved | Шаг с Range в PATCH/DELETE — эквивалентные формы ограничения, а не фильтра; оставить |
| 3 | VAL-DEFERRED-FAILURE | P2 | approved | Склеены when и ссылка; шаги-варианты разнородны (политики, маршруты), ожидание «нет 5xx» их покрывает |
| 4 | SEC-AUTHZ-ROLE-POSITIVE-MATRIX | P1 | approved | — |
| 5 | SEC-ROLE-ADMIN-SELF-TARGET | P2 | approved | Ожидание по документированной политике; молчит политика — needs_clarification на уровне теста, не записи |
| 6 | SEC-FAIL-CLOSED-INPUT | P1 | approved | 13 шагов — крупная запись; при генерации полезно отбирать варианты по применимости |
| 7 | CONC-REQUEST-CONTEXT-ISOLATION | P1 | approved | — |
| 8 | CONC-PARALLEL-INDEPENDENT | P2 | approved | — |
| 9 | PRIV-RESPONSE-FOREIGN-DATA | P1 | approved | Шаг с MNG — только для сервисов, разбирающих изображения |
| 10 | AUTH-TOKEN-INTROSPECTION | P2 | approved | — |
| 11 | AUTH-SESSION-NOT-BEFORE-LOGIN | P3 | approved | Склеен skip_when |
| 12 | FILE-TRANSFORM-LIMITS | P3 | approved | — |
| 13 | HTTP-VERSION-PARITY | P3 | approved | — |
| 14 | GQL-EQUIVALENT-SELECTION-FORMS | P3 | approved | — |
| 15 | RES-DRAFT-PUBLISH-FIDELITY | P2 | approved | — |
| 16 | RES-RELATION-ORDER-STABLE | P3 | approved | — |
| 17 | BIZ-EMAIL-LINK-CROSS-SESSION | P2 | approved | Без исходной сессии допустимы оба исхода (выполнено или понятная ошибка) — кроме 5xx |
| 18 | AUTH-REFRESH-PRESERVES-SCOPE | P2 | approved | — |
| 19 | AUTH-MFA-UNENROLLED-ERROR | P2 | approved | — |
| 20 | AUTH-OAUTH-PAR | P3 | approved | Склеена ссылка RFC 9126 |
| 21 | RESIL-ENCRYPTION-KEY-ROTATION | P3 | approved | Ручная (manual) — нужен доступ к ключам стенда |
| 22 | RES-LARGE-RELATION-SET | P3 | approved | — |
| 23 | RES-CACHE-KEY-COMPLETENESS | P2 | approved | — |
| 24 | HARD-SLOW-CLIENT-LIMITS | P2 | approved | Добавлено предусловие об инструментах; 15 шагов, большая часть транспортные |
| 25 | SEC-AUTHZ-RECREATED-IDENTITY | P1 | approved | — |
| 26 | CONTRACT-FIELD-SELECTION | P2 | approved | Часть шагов — PostgREST-синтаксис (спреды, вложения), применимы к API со вложениями |
| 27 | HTTP-ABSOLUTE-URL-BASE-PATH | P3 | approved | — |
| 28 | SEC-READONLY-MODE-ENFORCED | P1 | approved | — |
| 29 | RES-EXPORT-IMPORT-ROUNDTRIP | P3 | approved | Много шагов про снимки схемы (Directus); применимы к API с экспортом схемы |
| 30 | HARD-CLIENT-IP-TRUSTED-PROXIES | P2 | approved | — |
| 31 | FILE-MALFORMED-STRUCTURE | P2 | approved | Шаги по форматам (MIFF, PCD, MNG) — только если сервис разбирает эти форматы |
| 32 | ASYNC-RPC-ERROR-PROPAGATION | P2 | approved | — |
| 33 | ASYNC-MESSAGE-VALIDATION | P2 | approved | — |
| 34 | AUTH-GENERATED-SECRET-STRENGTH | P2 | approved | Оценка энтропии по выборке — приблизительная; ожидание по длине и алфавиту проверяемо |
| 35 | RES-SYSTEM-OBJECT-PROTECTED | P2 | approved | — |
| 36 | SEC-AUTHN-SCHEMES-SUPPORTED | P2 | approved | Шаг про refresh в httpOnly cookie — способ передачи учётных данных, подходит |
| 37 | FILE-UPLOAD-KEY-COLLISION | P1 | approved | — |
| 38 | AUTH-TOKEN-RESERVED-CLAIMS | P1 | approved | — |
| 39 | AUTH-OAUTH-RESOURCE-INDICATOR | P3 | approved | — |
| 40 | ASYNC-EVENT-PATH-SAME-RULES | P1 | approved | — |
| 41 | AUTH-EXTERNAL-IDP-UNVERIFIED-EMAIL | P0 | approved | Склеена ссылка OIDC; единственная P0 среди draft — приоритет оправдан (захват учётки) |
| 42 | SEC-IDENTITY-PROOF-OF-POSSESSION | P1 | approved | — |
| 43 | SEC-CONFUSED-DEPUTY | P1 | approved | — |
| 44 | AUTH-TOKEN-SENDER-CONSTRAINED | P2 | approved | — |
| 45 | ERR-STATUS-MATCHES-EFFECT | P2 | approved | Ожидание успеха уточнено |
| 46 | INJ-LLM-GENERATED-ACTIONS | P1 | approved | Результат LLM недетерминирован — automation partial уже стоит |
| 47 | SEC-CLONE-FIELD-PERMISSIONS | P2 | approved | — |
| 48 | FILE-ABORTED-UPLOAD-CLEANUP | P3 | approved | — |
| 49 | CONTRACT-PUBLISHED-SCHEMA-VALID | P2 | approved | Шаг с представлением над таблицей — PostgREST; применим к API по схеме БД |
| 50 | ASYNC-SSE-STREAM | P2 | approved | — |

Остальные draft (≈ 120, из масштабирования 2026-10-15…16) прошли перекрёстное ревью идей другими LLM (`*.reviewcheck.answer-*.md`);
их вычитка — отдельной задачей.
