# kong: сверка триажа багов без фикса с ручным эталоном

_2026-11-05, сессия «Выгрузка багов — сверка калибровки kong» (ad8c5ef0), Claude. ADR 0012, п. 6._

Эталон — [`nofix-review-kong.md`](nofix-review-kong.md) (ручная оценка 2026-10-23 по ~500 символам, 142 бага).
Триаж — `prompts/triage_abstract.md` (с п. 4 «Баги без исправления»), вслепую, пачки
`build/mining/kong/batches/b-03.out.jsonl` и `b-04.out.jsonl` (121 баг). Свод — скриптом
(эталон × `out.jsonl`), расхождения разобраны по тексту пачки, полному телу из `raw/kong.jsonl` и комментариям
issue на GitHub.

## Итог

- **Идея теста / не тест:** согласие 84,6 % (99 из 117 без Д), точность 87,5 %, полнота 87,5 %. После разбора
  расхождений триаж прав в 105 из 110 однозначных случаев (**95 %**); если все 7 спорных засчитать против триажа —
  105 из 117 (**90 %**). Цель ADR 0005 (85 %) выполнена.
- **Пруфы П:** 24 из 29 триаж отнёс к `api`; запись совпала с «Куда» полностью в 17 (71 %), близкая запись — в 7;
  выбор триажа не хуже эталона в 22 из 24 (92 %). Пять П триаж отбросил (см. расхождения).
- **Семейства:** слабо. Из 9 семейств эталона, у которых в пачках ≥ 2 бага, полностью собраны 2 (F3, F9),
  частично 1 (F1), разорваны 6. Попарная полнота — 17 из 51 пары (33 %). Лишних слияний против эталона — 2.
  Причина в основном одна: у багов с `extends`/`covered` ключ `family` не ставится.
- **Вывод:** триаж без фикса **можно запускать на остальных источниках**; правка промпта желательна (правила 1–3
  ниже), но не блокирует. Больше теряет не промпт, а `filter.py`: метка `stale` отсеяла 15 ценных багов из 21.
- **Спорно — решение bj:** 7 багов, плюс 3 вопроса политики (ниже).

## 1. Идея теста / не тест

Эталон: С, С+, П, Т, DB, UI → ценный; Н → не тест; Д (4 бага) — отдельно. Триаж: `verdict: api` или непустые
`ideas` → ценный.

| | Триаж: ценный | Триаж: не тест |
|---|---|---|
| **Эталон: ценный** | 63 | 9 |
| **Эталон: не тест** | 9 | 36 |

Д (6464, 6254, 6089, 5043): все четыре триаж отнёс к `api` с записью; у 6464 и 6254 запись совпала с эталоном,
у 6089 (`REST-OPTIONAL-EMPTY-VALUE` вместо `VAL-DEFERRED-FAILURE`) и 5043 (`AUTH-DUPLICATE-CREDENTIALS` вместо
`SEC-AUTHN-MALFORMED`) — близкая. Для Д это нормально: пруф к той же записи, что и у исправленного дубля.

## 2. Пруфы П

| Баг | Эталон «Куда» | Триаж | Совпадение | Кто точнее |
|---|---|---|---|---|
| 6578 | COMPAT-UPGRADE-STORED-DATA-STABLE | extends RESIL-TOKENS-SURVIVE-RESTART | близкая | эталон: дефект при обновлении версии, не при перезапуске |
| 6264 | VAL-SPECIAL-CHARACTERS | extends HTTP-UNRELATED-HEADERS-IGNORED | близкая | равно: управляющий символ в значении заголовка подходит к обеим |
| 6173 | COMPAT-BREAKING-CHANGE-DIFF | covered REST-PATCH-PARTIAL-UPDATE | близкая | триаж: ломается семантика PATCH; но `covered` спорно — лучше `extends` |
| 5907 | RESIL-CIRCUIT-BREAKER | new | нет | триаж: повтор на другую цель после 502 — не circuit breaker, записи нет |
| 4781 | RESIL-DEPENDENCY-DOWN | new | нет | триаж: восстановление после смены адресов (SRV), не «контролируемая ошибка» |
| 3964 | VAL-DEFERRED-FAILURE | extends COMPAT-UPGRADE-STORED-DATA-STABLE | близкая | триаж: условие — обновление версии |
| 3378 | REST-PAGINATION-BOUNDARIES | extends PAGE-CURSOR-TAMPERING | близкая | эталон: 500 вместо 400 на offset неверного типа — граница пагинации, не подделка курсора (направление) |

Полное совпадение — 13331, 11351, 8531, 8005, 7183, 6212, 5512, 5057, 4893, 4875, 4833, 4802, 4785, 4736, 4728,
4504, 3651. Отброшены триажем: 12805, 5094, 4232, 4213, 4145 (у 4145 есть идея DB — ценный, но без записи API).

## 3. Семейства

| F | В пачках | Ключи триажа | Итог |
|---|---|---|---|
| F1 | 3 из 6 (14043, 6236, 5217) | grpc-protocol-bridge ×2, route-setting-protocol-parity | частично; ещё 3 члена отсеяны фильтром |
| F2 | 4 | null ×2 (3426, 5967 — `covered`), json-empty-array-type, body-transform-fidelity | разорвано |
| F3 | 6 из 8 | config-change-propagation ×6 | **собрано** |
| F4 | 5 из 6 | null ×5 (2 `out_of_scope`, 3 с записью) | разорвано |
| F5 | 4 | deprecated-field-alias, body-transform-fidelity, null ×2 | разорвано |
| F6 | 4 из 5 | deployment-mode-parity, declarative-import-validation, config-accepted-runtime-fail, null | разорвано |
| F7 | 2 | config-accepted-runtime-fail, null | разорвано |
| F8 | 3 | все `out_of_scope` | разорвано (см. 3610 — на деле это F5) |
| F9 | 2 | upstream-tls-settings ×2 | **собрано** |
| F10–F12 | по 1 | — | не оценивается |

Лишние слияния против эталона: `body-transform-fidelity` (4880 из F2 + 4600 из F5) и
`config-accepted-runtime-fail` (13331 П + 12869 F7 + 5823 F6). Оба — другая ось (механизм «принято при записи —
падает при работе», «преобразование тела не теряет данных»), не ошибка; решение при кластеризации (шаг 6).
Новые группы триажа без пары в эталоне, разумные: `upgrade-stored-data` (6578, 6089, 4631, 3964), `cors-preflight`
(5512, 3651), `config-reload-state` (8531, 6464, 6359), `empty-credential-lookup` (5043, 4728); `stream-proxy-modes`
(9593, 7073) — см. спорные.

Вывод: `family` в нынешнем виде для багов без фикса почти бесполезен — семейства эталона придётся собирать на шаге 6
по `check_id` и тексту, как и сейчас делает `cluster.py`.

## 4. Расхождения «ценный / не тест»

| Баг | Эталон | Триаж | Кто прав | Почему |
|---|---|---|---|---|
| 12805 | П REQ-SPEC-NOT-IN-CONTRACT | oos/docs | эталон | Значения по умолчанию в документации расходятся с фактическими; подтверждено и исправлено (комментарии). Проверяемо по ответу сервера — категория `requirements`, а не ошибка документации |
| 9447 | С+ F4 | oos/insufficient-data | спорно | В теле только строка журнала; в комментариях — реальная гонка маршрутизатора, исправлена (PR 9480). По телу триаж прав, по сути — эталон |
| 6055 | С+ F4 | oos/memory | спорно | Рост памяти при 100 загрузках конфигурации через Admin API. По промпту `memory` — верно; воспроизводится запросами API — идея soak-проверки. Вопрос политики |
| 5801 | С+ F6 | oos/insufficient-data | спорно | «Странные ошибки» при дубле имени маршрута без БД — идея есть только в заголовке; та же идея уже есть у 6732 |
| 5212 | С+ F8 | oos/insufficient-data | триаж | Один текст ошибки, автор не ответил на вопросы; формат сертификата неизвестен — эталон достроил |
| 5094 | П OBS-METRICS-VALUE-RANGE | oos/insufficient-data | триаж | Только скриншоты, ждали автора; вероятная причина — пробы окружения |
| 4232 | П VAL-OPTIONAL-FIELDS-COMBINATIONS | oos/insufficient-data | эталон (класс) | Шаги воспроизведения — в конце тела, обрезанного до 4000 символов: токен с глобального эндпоинта на маршруте без `global_credentials` даёт 500 вместо 401. Идея эталона («маршрут без сервиса») неточна — верная: «токен, выданный для другого контекста, — 401, не 5xx» |
| 4213 | П AUTH-IDENTITY-ATTRIBUTES-ALL-SCHEMES | oos/framework-internal | эталон | Механизм внутренний, но внешнее следствие названо: лимит частоты по учётке ломается при части способов аутентификации |
| 3610 | С+ F8 | oos/insufficient-data | эталон (класс) | По комментариям мейнтейнера: загрузка через `multipart/form-data` не поддерживалась — «required field missing», через urlencoded работает. Ценная идея, но семейство — F5 (паритет форматов тела), не F8 |
| 9593 | Н | api new, stream-proxy-modes | спорно | TCP-прокси в режиме data plane рвёт соединение, шаги есть. Наблюдаемо, но не HTTP-API — вопрос охвата библиотеки |
| 7073 | Н | api new, stream-proxy-modes | спорно | То же: TCP-проксирование Postgres, TCP 500 |
| 6359 | Н | api extends RESIL-GRACEFUL-SHUTDOWN | триаж | Reload без БД ломает построение маршрутизатора; по п. 1 промпта (проявление после перезапуска) — `api`; только пруф, `variant: null` |
| 6186 | Н | api new | спорно | Запросы браузера не попадают в udp-log; мейнтейнер не воспроизвёл, версия — слишком большой UDP-пакет. Если так — идея «большие заголовки не теряют запись журнала» |
| 5748 | Н | api new | спорно | ~5 % TLS-рукопожатий с динамическим сертификатом — internal error, ARM. Идея «N рукопожатий подряд — все успешны» общая и дешёвая, но дефект платформенный |
| 5510 | Н | oos/other + DB | триаж | Идея DB «миграция данных идёт после схемных миграций, создающих её колонки» ценная; эталон непоследователен — 12978 и 6187 той же природы он отметил DB |
| 5042 | Н | api covered PERF-LOAD-THROUGHPUT | эталон | Самосборный образ arm64, «много запросов» без цифр — пруф без содержания |
| 4007 | Н | api covered VAL-JSON-TOP-LEVEL-TYPE | триаж | По трассировке видно: тело — число, а не объект → 500. Эталон по 500 символам до трассировки не дошёл |
| 3463 | Н | oos/other + DB | триаж | Идея «старт и работа при падении одного узла кластера БД, если кворум есть» — проверка устойчивости, ценная |

Счёт: эталон — 5 (12805, 4232, 4213, 3610, 5042), триаж — 6 (5212, 5094, 6359, 5510, 4007, 3463), спорно — 7.
Три из пяти ошибок триажа (4232, 3610, 9447) — не промпт, а вход: обрезанное тело и отсутствие комментариев.

## 5. Спорно — решение bj

1. **9593, 7073** — проксирование TCP-потоков (не HTTP): брать в библиотеку (`generic`) или `out_of_scope/other`?
2. **6055** — рост памяти при повторных операциях через API: `memory` (как сейчас в промпте) или идея soak-проверки
   категории `performance`?
3. **9447** — тело без данных, исправление в комментариях: считать ценным?
4. **5801** — идея только из заголовка (дубль имени в массовой загрузке без БД), уже есть у 6732: пруф или отказ?
5. **6186** — непонятный механизм (возможно, размер UDP-пакета): идея или отказ?
6. **5748** — платформенный (ARM) сбой TLS: брать общую идею «серия рукопожатий без ошибок»?
7. **Семейства из другой оси** (`config-accepted-runtime-fail`, `body-transform-fidelity`) — оставить как
   кандидаты для шага 6 или растащить по F6/F7 и F2/F5 эталона?

## 6. Отсеяны фильтром (21, в сверку не входят)

`filter.py`: метка `stale` (в `exclude_labels` по умолчанию) — 15, `manager` (kong) — 3, `question` в метке или заголовке — 3.

| Баг | Эталон | Причина отсева |
|---|---|---|
| 13339 | UI | kong-manager |
| 10757 | С+ F1 | stale |
| 9282 | Н | question |
| 8922 | UI | kong-manager |
| 8629 | С+ F6 | stale |
| 8527 | Н | stale |
| 8498 | П, UI REST-PATH-PARAM-ENCODING | kong-manager |
| 8151 | С+ F1 | stale |
| 8119 | П OBS-TRACE-PROPAGATION | stale |
| 8038 | П CONC-PARALLEL-INDEPENDENT | stale |
| 7920 | П RESOURCE-CREATE-READ | stale |
| 7541 | С+ F3 | stale |
| 7407 | С+ F4, F10 | stale |
| 6816 | Н | stale |
| 6808 | С+ F3 | stale |
| 6659 | Н | question (заголовок) |
| 6654 | Н | question |
| 6343 | Н | stale |
| 6066 | С+ F1 | stale |
| 5504 | П AUTH-OAUTH-REDIRECT-STATE | stale |
| 3790 | П AUTH-OAUTH-REDIRECT-STATE | stale |

Ценных по эталону — **15 из 21**: половина F1 (10757, 8151, 6066), F3 (7541, 6808), F4/F10 (7407), F6 (8629),
6 пруфов и 2 UI. Метка `stale` — отметка бота о бездействии, а не оценка бага; для багов без фикса она отсекает
в основном ценное. Предложение bj (не промпт): не применять `stale` к `closed-completed` или убрать её из
`exclude_labels` по умолчанию для источников с `allow_no_fix`. Решает человек — `sources.yaml` и `filter.py` здесь
не менялись.

## 7. Предложение по промпту (не применено, решает bj)

Правила для п. 4 «Баги без исправления» `prompts/triage_abstract.md`:

1. **Документация против поведения** (12805):
   > Расхождение документации с фактическим поведением или значениями по умолчанию, которое видно по ответу
   > сервера, — `api`, категория `requirements` (записи `REQ-*`). `docs` — только ошибки самой документации
   > (опечатки, ссылки, сайт), без проверяемого поведения.
2. **Внутренний механизм с названным следствием** (4213):
   > Если механизм внутренний, но в баге названо внешнее следствие (функция, лимит, ответ, плагин), это `api` по
   > этому следствию, а не `framework-internal`.
3. **Семейство не зависит от сопоставления** (F2, F4):
   > `family` ставится и у `extends`/`covered`: ключ — по матрице вариантов, не по записи. Перед выводом пачки
   > сверить ключи: один механизм — один ключ, без синонимов.

Не промпт, а вход пачки (решает bj): для `closed-completed` давать в пачку конец тела (раздел «Steps To
Reproduce») и первые комментарии мейнтейнера — так терялись 4232, 3610, 9447.

## 8. Можно ли запускать триаж без фикса на остальных источниках

Да. Решение «идея теста / не тест» — 90–95 % после разбора, выше цели 85 %; ошибки триажа в основном от неполного
входа, а не от правил. Выбор записи для пруфов — 92 %. Слабое место — семейства (33 % пар), их всё равно собирает
шаг 6. Перед запуском желательно решить вопрос с `stale` в фильтре (больше всего потерь), правки промпта 1–3 —
по желанию, при остановленных сессиях сбора.

## Приложение: все баги пачек

Совпадение: ✓ — одинаково «ценный / не тест», ✗ — расхождение, Д — дубль по эталону.

| Баг | Эталон | Куда | Триаж | match | family | ideas | |
|---|---|---|---|---|---|---|---|
| 14043 | С+ F1 | F1 | api | extends GRPC-JSON-TRANSCODING | grpc-protocol-bridge |  | ✓ |
| 13845 | С F11 | F11 | api | new | resource-name-lookup |  | ✓ |
| 13331 | П | VAL-DEFERRED-FAILURE | api | extends VAL-DEFERRED-FAILURE | config-accepted-runtime-fail |  | ✓ |
| 13301 | Н | — | oos/other | — |  |  | ✓ |
| 12978 | DB | DB-MIGRATION-STATE-TRACKED | oos/other | — |  | DB | ✓ |
| 12869 | С+ F7 | F7 | api | extends VAL-DEFERRED-FAILURE | config-accepted-runtime-fail |  | ✓ |
| 12805 | П | REQ-SPEC-NOT-IN-CONTRACT | oos/docs | — |  |  | ✗ |
| 12799 | С+ F2 | F2 | api | new | json-empty-array-type |  | ✓ |
| 11351 | П | RESIL-TOKENS-SURVIVE-RESTART | api | covered RESIL-TOKENS-SURVIVE-RESTART |  | DB | ✓ |
| 10758 | Н | — | oos/insufficient-data | — |  |  | ✓ |
| 9839 | Н | — | oos/other | — |  |  | ✓ |
| 9836 | Н | — | oos/other | — |  |  | ✓ |
| 9593 | Н | — | api | new | stream-proxy-modes |  | ✗ |
| 9447 | С+ F4 | F4 | oos/insufficient-data | — |  |  | ✗ |
| 9090 | Д / С+ F3 | F3 | api | extends RES-READ-AFTER-WRITE | config-change-propagation |  | ✓ |
| 8965 | Н | — | oos/perf-internal | — |  |  | ✓ |
| 8533 | Н | — | oos/build | — |  |  | ✓ |
| 8531 | П | RESIL-GRACEFUL-SHUTDOWN | api | extends RESIL-GRACEFUL-SHUTDOWN | config-reload-state |  | ✓ |
| 8005 | П | GRPC-JSON-TRANSCODING | api | extends GRPC-JSON-TRANSCODING | grpc-protocol-bridge |  | ✓ |
| 7406 | С+ F4 | F4 | api | extends RES-NOOP-UPDATE |  |  | ✓ |
| 7378 | С+ F3 | F3 | api | new | config-change-propagation |  | ✓ |
| 7183 | П | HARD-VERSION-DISCLOSURE | api | extends HARD-VERSION-DISCLOSURE |  |  | ✓ |
| 7073 | Н | — | api | new | stream-proxy-modes |  | ✗ |
| 6995 | Т | новая | api | extends HTTP-UNDERSCORE-HEADERS-PROXIED |  |  | ✓ |
| 6951 | DB | DB-MIGRATION-DATA-PRESERVED | oos/other | — |  | DB | ✓ |
| 6923 | С F12 | F12 | api | new |  |  | ✓ |
| 6827 | Н | — | oos/other | — |  |  | ✓ |
| 6813 | С+ F3 | F3 | api | extends RES-READ-AFTER-WRITE | config-change-propagation |  | ✓ |
| 6804 | Н | — | oos/usage | — |  |  | ✓ |
| 6793 | Н | — | oos/memory | — |  |  | ✓ |
| 6732 | С+ F6 | F6 / REST-DUPLICATE-UNIQUE-KEY | api | extends RES-BULK-SINGLE-VALIDATION-PARITY | declarative-import-validation | DB | ✓ |
| 6696 | Н | — | oos/other | — |  |  | ✓ |
| 6653 | Н | — | oos/other | — |  |  | ✓ |
| 6614 | Н | — | oos/other | — |  |  | ✓ |
| 6578 | П | COMPAT-UPGRADE-STORED-DATA-STABLE | api | extends RESIL-TOKENS-SURVIVE-RESTART | upgrade-stored-data |  | ✓ |
| 6573 | С+ F3 | F3 | api | extends RES-READ-AFTER-WRITE | config-change-propagation |  | ✓ |
| 6464 | Д | RESIL-TLS-CERT-RELOAD | api | extends RESIL-TLS-CERT-RELOAD | config-reload-state |  | Д |
| 6399 | Н | — | oos/usage | — |  |  | ✓ |
| 6362 | Н | — | oos/insufficient-data | — |  |  | ✓ |
| 6359 | Н | — | api | extends RESIL-GRACEFUL-SHUTDOWN | config-reload-state |  | ✗ |
| 6347 | Н | — | oos/insufficient-data | — |  |  | ✓ |
| 6302 | Н | — | oos/insufficient-data | — |  |  | ✓ |
| 6272 | С+ F5 | F5 / COMPAT-DEPRECATION-SIGNALS | api | new | deprecated-field-alias |  | ✓ |
| 6264 | П | VAL-SPECIAL-CHARACTERS | api | extends HTTP-UNRELATED-HEADERS-IGNORED |  |  | ✓ |
| 6254 | Д | OBS-HEALTH-ENDPOINTS | api | extends OBS-HEALTH-ENDPOINTS |  |  | Д |
| 6236 | С+ F1 | F1 | api | extends ASYNC-OUTBOUND-REQUEST-HEADERS | grpc-protocol-bridge |  | ✓ |
| 6212 | П (критично) | CONC-REQUEST-CONTEXT-ISOLATION | api | extends CONC-REQUEST-CONTEXT-ISOLATION |  |  | ✓ |
| 6199 | Н | — | oos/usage | — |  |  | ✓ |
| 6187 | DB | DB-MIGRATION-STATE-TRACKED | oos/other | — |  | DB | ✓ |
| 6186 | Н | — | api | new |  |  | ✗ |
| 6178 | Н | — | oos/perf-internal | — |  |  | ✓ |
| 6173 | П | COMPAT-BREAKING-CHANGE-DIFF | api | covered REST-PATCH-PARTIAL-UPDATE |  |  | ✓ |
| 6135 | Н | — | oos/build | — |  |  | ✓ |
| 6106 | Н | — | oos/usage | — |  |  | ✓ |
| 6089 | Д | VAL-DEFERRED-FAILURE | api | extends REST-OPTIONAL-EMPTY-VALUE | upgrade-stored-data | DB | Д |
| 6055 | С+ F4 | F4 | oos/memory | — |  |  | ✗ |
| 5967 | С+ F2 | F2 / REST-EMPTY-VALUES | api | covered REST-EMPTY-VALUES |  |  | ✓ |
| 5938 | Н | — | oos/framework-internal | — |  |  | ✓ |
| 5913 | Н | — | oos/usage | — |  |  | ✓ |
| 5907 | П | RESIL-CIRCUIT-BREAKER | api | new |  |  | ✓ |
| 5893 | С+ F5 | F5 | api | extends HTTP-BODY-WITHOUT-CONTENT-TYPE |  |  | ✓ |
| 5828 | Н | — | oos/usage | — |  |  | ✓ |
| 5823 | С+ F6 | F6 / VAL-DEFAULT-VALUES | api | extends VAL-DEFERRED-FAILURE | config-accepted-runtime-fail |  | ✓ |
| 5801 | С+ F6 | F6 | oos/insufficient-data | — |  |  | ✗ |
| 5791 | С+ F3 | F3 | api | extends RES-READ-AFTER-WRITE | config-change-propagation |  | ✓ |
| 5748 | Н | — | api | new |  |  | ✗ |
| 5645 | Н | — | oos/insufficient-data | — |  |  | ✓ |
| 5512 | П | REST-CORS-POLICY | api | extends REST-CORS-POLICY | cors-preflight |  | ✓ |
| 5510 | Н | — | oos/other | — |  | DB | ✗ |
| 5388 | Н | — | oos/build | — |  |  | ✓ |
| 5327 | DB | DB-SERVICE-ROLE-LEAST-PRIVILEGE | oos/other | — |  | DB | ✓ |
| 5313 | С+ F7 | F7 / REST-PATCH-PARTIAL-UPDATE | api | extends REST-PATCH-PARTIAL-UPDATE |  |  | ✓ |
| 5296 | С+ F10 | F10 | api | extends RES-CRUD-CYCLE | delete-recreate-same-key |  | ✓ |
| 5242 | Д, DB | — | api | extends COMPAT-UPGRADE-STORED-DATA-STABLE |  | DB | ✓ |
| 5217 | С+ F1 | F1 | api | new | route-setting-protocol-parity |  | ✓ |
| 5212 | С+ F8 | F8 | oos/insufficient-data | — |  |  | ✗ |
| 5135 | Н | — | oos/framework-internal | — |  |  | ✓ |
| 5112 | С F9 | F9 | api | new | upstream-tls-settings |  | ✓ |
| 5094 | П | OBS-METRICS-VALUE-RANGE | oos/insufficient-data | — |  |  | ✗ |
| 5069 | С+ F3 | F3 | api | extends RES-READ-AFTER-WRITE | config-change-propagation |  | ✓ |
| 5057 | П | OBS-LOG-ENTRY-INTEGRITY | api | extends OBS-LOG-ENTRY-INTEGRITY |  |  | ✓ |
| 5043 | Д | SEC-AUTHN-MALFORMED | api | extends AUTH-DUPLICATE-CREDENTIALS | empty-credential-lookup |  | Д |
| 5042 | Н | — | api | covered PERF-LOAD-THROUGHPUT |  |  | ✗ |
| 4986 | С+ F4, DB | F4 | api | extends CONC-PARALLEL-INDEPENDENT |  | DB | ✓ |
| 4975 | Н | — | oos/usage | — |  |  | ✓ |
| 4955 | С+ F9 | F9 | api | new | upstream-tls-settings |  | ✓ |
| 4893 | П | REST-PATCH-PARTIAL-UPDATE | api | extends REST-PATCH-PARTIAL-UPDATE |  |  | ✓ |
| 4883 | С+ F4 | F4 / PERF-METADATA-RELOAD-NO-BLOCK | api | extends PERF-METADATA-RELOAD-NO-BLOCK |  |  | ✓ |
| 4880 | С+ F2 | F2 | api | new | body-transform-fidelity |  | ✓ |
| 4875 | П | RES-REFERENTIAL-INTEGRITY | api | extends RES-REFERENTIAL-INTEGRITY |  | DB | ✓ |
| 4848 | Н | — | oos/framework-internal | — |  |  | ✓ |
| 4833 | П | HTTP-VERSION-PARITY | api | extends HTTP-VERSION-PARITY |  |  | ✓ |
| 4802 | П | REST-PUT-REPLACEMENT | api | covered REST-PUT-REPLACEMENT |  |  | ✓ |
| 4786 | Н | — | oos/framework-internal | — |  |  | ✓ |
| 4785 | П | OBS-SERVER-TIMING-ACCURATE | api | extends OBS-SERVER-TIMING-ACCURATE |  |  | ✓ |
| 4781 | П | RESIL-DEPENDENCY-DOWN | api | new |  |  | ✓ |
| 4736 | П | RESIL-GRACEFUL-SHUTDOWN | api | extends RESIL-GRACEFUL-SHUTDOWN |  |  | ✓ |
| 4728 | П (безопасность) | AUTH-DUPLICATE-CREDENTIALS | api | extends AUTH-DUPLICATE-CREDENTIALS | empty-credential-lookup |  | ✓ |
| 4631 | DB | DB-MIGRATION-DATA-PRESERVED | api | extends COMPAT-UPGRADE-STORED-DATA-STABLE | upgrade-stored-data | DB | ✓ |
| 4600 | С+ F5 | F5 | api | new | body-transform-fidelity |  | ✓ |
| 4542 | С+ F6 | F6 | api | extends AUTH-IMPORTED-PASSWORD-HASH | deployment-mode-parity |  | ✓ |
| 4504 | П | VAL-CASE-SENSITIVITY | api | extends VAL-CASE-SENSITIVITY |  |  | ✓ |
| 4471 | Н | — | oos/usage | — |  |  | ✓ |
| 4232 | П | VAL-OPTIONAL-FIELDS-COMBINATIONS | oos/insufficient-data | — |  |  | ✗ |
| 4213 | П | AUTH-IDENTITY-ATTRIBUTES-ALL-SCHEMES | oos/framework-internal | — |  |  | ✗ |
| 4145 | П, DB | DB-MIGRATION-CLEAN-INSTALL | oos/other | — |  | DB | ✓ |
| 4033 | Н | — | oos/other | — |  |  | ✓ |
| 4007 | Н | — | api | covered VAL-JSON-TOP-LEVEL-TYPE |  |  | ✗ |
| 3975 | Н | — | oos/other | — |  |  | ✓ |
| 3964 | П | VAL-DEFERRED-FAILURE | api | extends COMPAT-UPGRADE-STORED-DATA-STABLE | upgrade-stored-data |  | ✓ |
| 3924 | Н | — | oos/other | — |  |  | ✓ |
| 3911 | DB | DB-CASCADE-SCOPE | api | extends RES-DELETE-WITH-DEPENDENTS |  | DB | ✓ |
| 3823 | С+ F5 | F5 | api | extends REST-CONTENT-TYPE-JSON |  |  | ✓ |
| 3809 | Н | — | oos/other | — |  |  | ✓ |
| 3651 | П | REST-CORS-POLICY | api | extends REST-CORS-POLICY | cors-preflight |  | ✓ |
| 3610 | С+ F8 | F8 | oos/insufficient-data | — |  |  | ✗ |
| 3562 | Н | — | oos/other | — |  |  | ✓ |
| 3463 | Н | — | oos/other | — |  | DB | ✗ |
| 3426 | С+ F2 | F2 | api | covered REST-EMPTY-VALUES |  |  | ✓ |
| 3394 | Н | — | oos/other | — |  |  | ✓ |
| 3378 | П | REST-PAGINATION-BOUNDARIES | api | extends PAGE-CURSOR-TAMPERING |  |  | ✓ |
