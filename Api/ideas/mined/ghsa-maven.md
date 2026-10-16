# Кандидаты из баг-трекеров: партия `ghsa-maven`

Сгенерировано `tools/mining/cluster.py` из `build/mining/<batch>/batches/*.out.jsonl` и
`ideas/mined/ghsa-maven.review.yaml` — правки решений делаются в review-файле, затем пересборка.
План — `docs/BUG_MINING_PLAN.md`, шаги 6–7; применение — `tools/mining/apply_proofs.py`.

## Сводка

- Новых паттернов: 20 → идей: 10 (принять: 10, отклонить: 0, не решено: 0).
- Пруфы к существующим: 174 багов → 61 записей; новых шагов-вариантов: 96.

## Новые идеи

Принятые становятся записями `status: draft` с меткой `real-world-bug` и ссылкой на RWB.

| # | Решение | Запись / файл | Идея | Подтверждающие баги |
|---|---|---|---|---|
| 1 | accept | `SEC-INTERNAL-CONTROL-PARAMS` (RWB-0180)<br>`checks/security/api-hardening.yaml` | Заголовки запроса и параметры подключения (в том числе WebSocket) с именами внутренних управляющих параметров (запрос к хранилищу или поиску, операция, ID объекта, адрес исходящего запроса, DNS-сервер, ключи во внешней системе) не меняют внутреннюю операцию сервиса — выполняется настроенная | [GHSA-gcc7-c8mp-34qx](https://github.com/advisories/GHSA-gcc7-c8mp-34qx), [GHSA-4h4f-v54q-7pq8](https://github.com/advisories/GHSA-4h4f-v54q-7pq8), [GHSA-hcm8-x79p-wx2w](https://github.com/advisories/GHSA-hcm8-x79p-wx2w), [GHSA-64gv-6cq2-45jr](https://github.com/advisories/GHSA-64gv-6cq2-45jr), [GHSA-566h-v38h-3xp3](https://github.com/advisories/GHSA-566h-v38h-3xp3), [GHSA-rp9m-hfv5-pfvr](https://github.com/advisories/GHSA-rp9m-hfv5-pfvr), [GHSA-rcvm-6r79-cf4r](https://github.com/advisories/GHSA-rcvm-6r79-cf4r), [GHSA-hgg5-gp4c-gpcg](https://github.com/advisories/GHSA-hgg5-gp4c-gpcg) |
| 2 | accept | `INJ-USER-CODE-EXECUTION` (RWB-0181)<br>`checks/security/injection.yaml` | Пользовательский код (скрипт, выражение, алгоритм), который сервер принимает через API и исполняет, не получает доступа к классам и функциям вне разрешённого набора (запуск процессов, файловая система, сеть) | [GHSA-2g95-6x5q-xjwj](https://github.com/advisories/GHSA-2g95-6x5q-xjwj), [GHSA-vmwp-vh32-rj75](https://github.com/advisories/GHSA-vmwp-vh32-rj75), [GHSA-524g-x36v-9wm6](https://github.com/advisories/GHSA-524g-x36v-9wm6) |
| 3 | accept | `SEC-DISABLED-FEATURE-ENFORCED` (RWB-0182)<br>`checks/security/api-hardening.yaml` | Функция, отключённая настройкой, недоступна через все API и не попадает в токены (scope, claims), даже если у пользователя остались её данные | [GHSA-4q93-v92x-p89f](https://github.com/advisories/GHSA-4q93-v92x-p89f) |
| 4 | accept | `SEC-AUTHZ-PATH-RULE-PRECEDENCE` (RWB-0183)<br>`checks/security/access-control/SEC-AUTHZ-PATH-RULE-PRECEDENCE.yaml` | Правила доступа по путям применяются по наиболее точному совпадению независимо от порядка объявления — строгое правило подпути не перекрывается общим правилом | [GHSA-gcx9-497g-6cp6](https://github.com/advisories/GHSA-gcx9-497g-6cp6) |
| 5 | accept | `SEC-OPAQUE-ID-INTEGRITY` (RWB-0184)<br>`checks/security/api-hardening.yaml` | Непрозрачный идентификатор, который выдаёт сервер и из которого он выводит внутренние ресурсы, проверяется на подлинность — сфабрикованный клиентом ID отклоняется до распаковки и обращения к ресурсам | [GHSA-fp43-vj7g-pg92](https://github.com/advisories/GHSA-fp43-vj7g-pg92) |
| 6 | accept | `AUTH-CLIENT-ASSERTION-BINDING` (RWB-0185)<br>`checks/security/authentication-session.yaml` | Client assertion (private_key_jwt) принимается только с ключом того клиента, чей client_id в ней указан — клиент не аутентифицируется от имени другого | [GHSA-f2cx-463q-7m2c](https://github.com/advisories/GHSA-f2cx-463q-7m2c) |
| 7 | accept | `AUTH-ACCOUNT-STATE-ALL-SCHEMES` (RWB-0186)<br>`checks/security/authentication-session.yaml` | Отключённая, заблокированная или истёкшая учётка не аутентифицируется ни одной схемой (пароль, сертификат клиента, токен, ключ API) | [GHSA-6mfm-98wv-32wm](https://github.com/advisories/GHSA-6mfm-98wv-32wm) |
| 8 | accept | `AUTH-CLIENT-CERT-IDENTITY` (RWB-0187)<br>`checks/security/authentication-session.yaml` | Личность из сертификата клиента (CN, SAN) извлекается однозначно — нестандартно сформированное поле не даёт войти под именем другого пользователя | [GHSA-293q-567p-wmwq](https://github.com/advisories/GHSA-293q-567p-wmwq) |
| 9 | accept | `HARD-IP-ALLOWLIST` (RWB-0188)<br>`checks/security/api-hardening.yaml` | Ограничение доступа по списку адресов и подсетей работает на границах подсети для IPv4 и IPv6 — адреса вне разрешённой подсети получают отказ | [GHSA-3qp7-7mw8-wx86](https://github.com/advisories/GHSA-3qp7-7mw8-wx86) |
| 10 | accept | `HTTP-HTTP2-RESOURCE-LIMITS` (RWB-0189)<br>`checks/rest/http-protocol.yaml` | Параметры HTTP/2 со стороны клиента (окно управления потоком при медленном чтении тела, малый SETTINGS_MAX_HEADER_LIST_SIZE) не заставляют сервер буферизовать без предела или выполнять работу впустую | [GHSA-6m4x-pp6q-5jmm](https://github.com/advisories/GHSA-6m4x-pp6q-5jmm), [GHSA-563q-j3cm-6jxm](https://github.com/advisories/GHSA-563q-j3cm-6jxm) |

## Пруфы к существующим

Запись получает метку `real-world-bug` и `Real-world bug: RWB-NNNN`; статус не меняется. Для `extends`
текст варианта добавляется шагом (`steps[].action`, в `notes` — RWB). Неверное совпадение — ID бага в
`proofs.exclude`, вариант без нового шага — в `proofs.no_variant`.

### ASYNC-EVENT-PATH-SAME-RULES — Событийный путь применяет те же фильтры и границы доступа, что и плановый (RWB-0040, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-pw9q-pq7c-rfqw](https://github.com/advisories/GHSA-pw9q-pq7c-rfqw) | extends | Опубликовать в очередь сообщение с пользовательским заголовком, совпадающим с внутренним управляющим параметром (адрес исходящего запроса), и проверить, что он отброшен, как на HTTP-входе |

### ASYNC-WEBHOOK-URL-SSRF — URL вебхука не может указывать на внутренние адреса (RWB-0054, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-c556-q2mh-477v](https://github.com/advisories/GHSA-c556-q2mh-477v) | extends | Зарегистрировать URL уведомлений о событиях сессии на внешний адрес и проверить, что данные сессии туда не уходят |

### AUTH-CSRF — Изменяющие операции с cookie-аутентификацией защищены от CSRF (RWB-0190, багов: 9)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-2x9c-vp3g-hvv2](https://github.com/advisories/GHSA-2x9c-vp3g-hvv2) | covered | _только пруф_: Изменяющая операция доступна без CSRF-защиты |
| [GHSA-4j38-rw27-97gx](https://github.com/advisories/GHSA-4j38-rw27-97gx) | covered | _только пруф_: Изменяющая операция без защиты от CSRF |
| [GHSA-43m2-hcmm-qpm7](https://github.com/advisories/GHSA-43m2-hcmm-qpm7) | covered | _только пруф_: Изменяющая операция через GET без CSRF-защиты |
| [GHSA-429r-3j78-2pxm](https://github.com/advisories/GHSA-429r-3j78-2pxm) | covered | _только пруф_: Операция через GET без CSRF-защиты |
| [GHSA-6qc4-57v3-28rr](https://github.com/advisories/GHSA-6qc4-57v3-28rr) | covered | _только пруф_: Операция через GET без CSRF-защиты |
| [GHSA-w794-rwp2-jc9m](https://github.com/advisories/GHSA-w794-rwp2-jc9m) | covered | _только пруф_: Операция через GET без CSRF-защиты |
| [GHSA-fq56-wvv2-p8jf](https://github.com/advisories/GHSA-fq56-wvv2-p8jf) | covered | _только пруф_: Изменяющая операция через GET без CSRF-защиты |
| [GHSA-hj3h-r49w-34wh](https://github.com/advisories/GHSA-hj3h-r49w-34wh) | covered | _только пруф_: Изменяющая операция через GET без CSRF-защиты |
| [GHSA-rf8w-7c3g-7h3g](https://github.com/advisories/GHSA-rf8w-7c3g-7h3g) | covered | _только пруф_: Изменяющая операция через GET без CSRF-защиты |

### AUTH-OAUTH-REDIRECT-STATE — OAuth/OIDC flow проверяет redirect_uri, state и PKCE (RWB-0061, багов: 3)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-fxr3-gvm4-m8vc](https://github.com/advisories/GHSA-fxr3-gvm4-m8vc) | covered | _только пруф_: Проверка redirect_uri в OAuth-потоке |
| [GHSA-4v2w-2wqp-mc85](https://github.com/advisories/GHSA-4v2w-2wqp-mc85) | covered | _только пруф_: Проверка PKCE при обмене кода |
| [GHSA-4r8w-73jc-3m7q](https://github.com/advisories/GHSA-4r8w-73jc-3m7q) | extends | Отправить запрос авторизации с невалидным request_uri и незарегистрированным redirect_uri |

### AUTH-SESSION-FIXATION — Идентификатор сессии меняется после входа (RWB-0191, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-4hfh-6x8g-gwpp](https://github.com/advisories/GHSA-4hfh-6x8g-gwpp) | covered | _только пруф_: Ровно запись |

### AUTH-TOKEN-INTROSPECTION — Интроспекция токена возвращает актуальное состояние и те же claims, что в токене (RWB-0010, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-542g-m3fx-q86f](https://github.com/advisories/GHSA-542g-m3fx-q86f) | extends | Вызвать эндпоинт интроспекции без аутентификации клиента |

### AUTH-TOKEN-TYPE-CONFUSION — Refresh, ID или сервисный токен не принимается как access-токен (RWB-0192, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-cj8f-2fhf-826r](https://github.com/advisories/GHSA-cj8f-2fhf-826r) | extends | Предъявить как токен идентификатор записи другого типа из того же хранилища (регистрация, сессия), содержимое которой задал клиент, и проверить 401 |

### AUTH-USER-ENUMERATION — Ответы входа, регистрации и восстановления не раскрывают существование аккаунта (RWB-0193, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-5x25-c2rf-f2jx](https://github.com/advisories/GHSA-5x25-c2rf-f2jx) | extends | Выполнить вход для заблокированной, отключённой и несуществующей учёток и сравнить ответы |

### BIZ-WORKFLOW-STEP-SKIP — Нельзя пропустить обязательный шаг бизнес-процесса (RWB-0066, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-4gv3-mc9p-5wqc](https://github.com/advisories/GHSA-4gv3-mc9p-5wqc) | covered | _только пруф_: Пропуск обязательного шага подтверждения в потоке сброса |

### CONC-REQUEST-CONTEXT-ISOLATION — Параллельные запросы разных пользователей получают только свой контекст и свой ответ (RWB-0007, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-f4v5-65jj-pcr2](https://github.com/advisories/GHSA-f4v5-65jj-pcr2) | extends | Отправить по одному keep-alive соединению запрос с трейлерами и затем запрос без них и проверить, что второй не получил данных первого |

### ERR-INTERNAL-ERROR-SHAPE — Внутренняя ошибка сервера возвращается в общей модели без утечек (RWB-0068, багов: 3)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-hjg2-f45w-c566](https://github.com/advisories/GHSA-hjg2-f45w-c566) | covered | _только пруф_: Утечка стека во внутренней ошибке |
| [GHSA-42q5-xw42-xf9g](https://github.com/advisories/GHSA-42q5-xw42-xf9g) | covered | _только пруф_: Утечка стека во внутренней ошибке |
| [GHSA-p5mm-xwgq-whfr](https://github.com/advisories/GHSA-p5mm-xwgq-whfr) | covered | _только пруф_: Утечка внутренних деталей в ошибке — ровно запись |

### FILE-ARCHIVE-BOMB — Архивные и графические бомбы не исчерпывают ресурсы (RWB-0069, багов: 3)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-3w98-rrpr-fprr](https://github.com/advisories/GHSA-3w98-rrpr-fprr) | extends | Отправить JWT с заголовком zip=DEF и payload, распаковывающимся в сотни мегабайт, и проверить отказ по лимиту размера |
| [GHSA-gm45-99xc-r7wv](https://github.com/advisories/GHSA-gm45-99xc-r7wv) | extends | Отправить сжатые данные из тысяч минимальных пустых фреймов с максимальным размером блока и проверить, что время обработки пропорционально размеру входа |
| [GHSA-m69x-pw9p-7j3q](https://github.com/advisories/GHSA-m69x-pw9p-7j3q) | extends | Отправить deflate-бомбу в сжатом параметре запроса (SAMLRequest, SAMLResponse) |

### FILE-DOWNLOAD-AUTHZ — Скачивание файлов проверяет права и срок действия ссылок (RWB-0070, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-jr45-52cw-69h5](https://github.com/advisories/GHSA-jr45-52cw-69h5) | covered | _только пруф_: Скачивание чужого файла по ID |

### FILE-MALFORMED-STRUCTURE — Повреждённый файл при разборе метаданных даёт 4xx, а не падение процесса (RWB-0031, багов: 2)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-gq9c-wmrm-5hvr](https://github.com/advisories/GHSA-gq9c-wmrm-5hvr) | extends | Отправить JWT с заголовком zip=DEF и пустым или обрезанным сжатым payload и проверить, что ответ 4xx приходит за ограниченное время |
| [GHSA-gc95-3vw8-vg43](https://github.com/advisories/GHSA-gc95-3vw8-vg43) | extends | Загрузить документ с циклической цепочкой ссылок наследования (стиль A основан на B, B — на A) и вызвать его обработку |

### GQL-FIELD-LEVEL-AUTHZ — Авторизация применяется на уровне полей и вложенных резолверов (RWB-0194, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-phxq-526m-79px](https://github.com/advisories/GHSA-phxq-526m-79px) | covered | _только пруф_: Механизм внутренний; описанное следствие — пропуск авторизации резолвера |

### GRPC-STREAM-RESOURCE-LIMITS — Число одновременных стримов и их длительность ограничены (RWB-0195, багов: 2)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-9vwc-pc8p-253q](https://github.com/advisories/GHSA-9vwc-pc8p-253q) | extends | По HTTP/2 открыть потоков больше объявленного SETTINGS_MAX_CONCURRENT_STREAMS и проверить отказ REFUSED_STREAM или PROTOCOL_ERROR |
| [GHSA-5x3r-wrvg-rp6q](https://github.com/advisories/GHSA-5x3r-wrvg-rp6q) | covered | _только пруф_: Вариант для HTTP/2 уже добавлен по прошлой пачке |

### HARD-DEBUG-ENDPOINTS — Отладочные и служебные эндпоинты недоступны извне (RWB-0075, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-hpj9-grjp-7vc7](https://github.com/advisories/GHSA-hpj9-grjp-7vc7) | covered | _только пруф_: Служебные эндпоинты доступны извне без аутентификации |

### HARD-EXPENSIVE-OPERATION-LIMITS — Дорогие операции ограничены по ресурсам (RWB-0077, багов: 13)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-cxp5-3px4-pw24](https://github.com/advisories/GHSA-cxp5-3px4-pw24) | extends | Отправить коллекцию из N ссылок на объекты по ID, определяемые позже в обратном порядке, и сравнить время ответа для N и 2N |
| [GHSA-q4xh-88c3-wmh7](https://github.com/advisories/GHSA-q4xh-88c3-wmh7) | extends | Отправить в строковое поле длительности или даты компоненту из миллиона цифр и проверить, что отказ приходит быстро по лимиту длины |
| [GHSA-v74w-7mr3-4qg3](https://github.com/advisories/GHSA-v74w-7mr3-4qg3) | extends | Отправлять XML из повторяющихся «</» мелкими порциями без закрывающей «>» и проверить, что время обработки не растёт квадратично, а сервис отвечает другим клиентам |
| [GHSA-r7wm-3cxj-wff9](https://github.com/advisories/GHSA-r7wm-3cxj-wff9) | extends | Передать тело с числом из миллионов цифр потоково мелкими порциями без завершающего символа и проверить отказ по лимиту длины числа до конца передачи |
| [GHSA-w4cm-gvhj-cgw6](https://github.com/advisories/GHSA-w4cm-gvhj-cgw6) | extends | Передать JSON с одним длинным токеном очень мелкими порциями и сравнить время обработки для длины N и 2N |
| [GHSA-4899-mpch-38p3](https://github.com/advisories/GHSA-4899-mpch-38p3) | extends | Отправить бинарное сообщение (Binary HTTP) с заявленной длиной секции полей, не совпадающей с границами строк полей, и проверить, что разбор завершается ошибкой за ограниченное время |
| [GHSA-8cfx-wx3q-mh5q](https://github.com/advisories/GHSA-8cfx-wx3q-mh5q) | extends | _только пруф_: Тот же вариант, что у GHSA-4899-mpch-38p3 |
| [GHSA-6jqx-86gh-f27w](https://github.com/advisories/GHSA-6jqx-86gh-f27w) | extends | Отправить один кадр настроек соединения с сотнями тысяч уникальных параметров и проверить, что сервер его ограничивает |
| [GHSA-74xj-wh4w-vqxc](https://github.com/advisories/GHSA-74xj-wh4w-vqxc) | extends | Отправить заголовок baggage (или другой заголовок-список) с десятками тысяч элементов и проверить, что разбор ограничен лимитом |
| [GHSA-ghvc-7hp8-2g2v](https://github.com/advisories/GHSA-ghvc-7hp8-2g2v) | extends | Отправить multipart-сообщение с тысячами частей-вложений |
| [GHSA-5m4m-73w9-8433](https://github.com/advisories/GHSA-5m4m-73w9-8433) | covered | _только пруф_: Механизм не описан; запись проверяет описанное следствие |
| [GHSA-83f7-v6px-pp3h](https://github.com/advisories/GHSA-83f7-v6px-pp3h) | covered | _только пруф_: Механизм не описан; запись проверяет следствие |
| [GHSA-x23c-287f-qqv5](https://github.com/advisories/GHSA-x23c-287f-qqv5) | covered | _только пруф_: Механизм не описан; запись проверяет следствие |

### HARD-SHADOW-API-VERSIONS — Старые версии API и недокументированные маршруты не обходят защиту (RWB-0079, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-85g9-8j9g-p486](https://github.com/advisories/GHSA-85g9-8j9g-p486) | covered | _только пруф_: Альтернативная версия API без защиты — ровно запись |

### HARD-SLOW-CLIENT-LIMITS — Медленные и неполные запросы и непрочитанные ответы не накапливаются без ограничения (RWB-0024, багов: 8)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-cqgj-h8vf-4w59](https://github.com/advisories/GHSA-cqgj-h8vf-4w59) | extends | Подписаться на канал с подтверждением доставки, постоянно присылать одно и то же значение подтверждения и проверить, что очередь неподтверждённых сообщений ограничена |
| [GHSA-gq9p-f254-h286](https://github.com/advisories/GHSA-gq9p-f254-h286) | extends | По HTTP/2 отправить заголовок фрейма с длиной больше объявленного SETTINGS_MAX_FRAME_SIZE, передавая payload медленно, и проверить закрытие соединения с FRAME_SIZE_ERROR сразу после заголовка |
| [GHSA-8f3q-3jmv-7prw](https://github.com/advisories/GHSA-8f3q-3jmv-7prw) | extends | По HTTP/2 непрерывно слать PING и SETTINGS, не читая ответные ACK, и проверить, что сервер ограничивает очередь и закрывает соединение |
| [GHSA-q4f6-jm68-57ww](https://github.com/advisories/GHSA-q4f6-jm68-57ww) | extends | Отправить по одному соединению HTTP/1.1 поток конвейерных запросов, не читая ответы, и проверить, что сервер ограничивает очередь |
| [GHSA-hpcc-26xq-25fv](https://github.com/advisories/GHSA-hpcc-26xq-25fv) | extends | Отправить по HTTP/3 на многих потоках кадры зарезервированного типа с огромной заявленной длиной и частью данных и проверить, что память не растёт |
| [GHSA-q6cq-mhr2-jmr5](https://github.com/advisories/GHSA-q6cq-mhr2-jmr5) | extends | Отправить сигнатуру PROXY protocol v2 с недопустимым байтом версии и продолжать слать данные; проверить, что соединение закрывается |
| [GHSA-4grm-h2qv-h6w6](https://github.com/advisories/GHSA-4grm-h2qv-h6w6) | extends | Открыть по HTTP/3 много потоков со ссылками на неотправленные записи динамической таблицы QPACK и не досылать записи |
| [GHSA-x4gw-5cx5-pgmh](https://github.com/advisories/GHSA-x4gw-5cx5-pgmh) | extends | Отправить начало TLS ClientHello с большой заявленной длиной и не досылать остальное |

### HTTP-HEADER-SIZE-LIMIT — Слишком большие заголовки отклоняются контролируемо (RWB-0196, багов: 7)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-cp4q-fqw9-4hf6](https://github.com/advisories/GHSA-cp4q-fqw9-4hf6) | extends | По HTTP/2 отправить HEADERS без END_HEADERS и непрерывный поток CONTINUATION-фреймов и проверить разрыв по лимиту размера заголовков |
| [GHSA-hmq9-67w8-j5pw](https://github.com/advisories/GHSA-hmq9-67w8-j5pw) | extends | Отправить в бинарном представлении HTTP поле с заявленной длиной сверх лимита и проверить отказ до буферизации данных |
| [GHSA-mvh2-crg5-v77c](https://github.com/advisories/GHSA-mvh2-crg5-v77c) | extends | Отправить сжатый блок заголовков, раскрывающийся далеко за лимит, и проверить, что распаковка прекращается на лимите |
| [GHSA-vhch-2wf3-m8rp](https://github.com/advisories/GHSA-vhch-2wf3-m8rp) | extends | Отправить кадр STOMP с огромным числом коротких заголовков и проверить, что сервер его отклоняет |
| [GHSA-v3jc-474w-2wm6](https://github.com/advisories/GHSA-v3jc-474w-2wm6) | extends | Отправить по HTTP/2 крупный сжатый блок заголовков до подтверждения SETTINGS и проверить, что лимит уже действует |
| [GHSA-hf6x-8p5f-cgmf](https://github.com/advisories/GHSA-hf6x-8p5f-cgmf) | covered | _только пруф_: Лимит числа и размера заголовков |
| [GHSA-c2rx-5r8w-8xr2](https://github.com/advisories/GHSA-c2rx-5r8w-8xr2) | extends | Повторить отправку чрезмерных заголовков по HTTP/3 |

### HTTP-TRAILING-SLASH-CASE — Вариации пути (слэш в конце, регистр, двойной слэш) обрабатываются единообразно (RWB-0197, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-qcxp-gm7m-4j5v](https://github.com/advisories/GHSA-qcxp-gm7m-4j5v) | extends | Вызвать защищённый путь с закодированными %3B, %2F и %5C в сегментах без прав и проверить, что правило доступа по пути срабатывает |

### INJ-FILTER-EXPRESSION — Выражения фильтрации (OData, RSQL, JSONPath, GraphQL where) не позволяют выйти за ограничения (RWB-0082, багов: 3)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-c64q-hj4j-375f](https://github.com/advisories/GHSA-c64q-hj4j-375f) | extends | Отправить в шаблон LIKE поискового выражения значение с двойной кавычкой и фрагментом кода и проверить, что код не исполняется |
| [GHSA-cmwh-w62w-r2mf](https://github.com/advisories/GHSA-cmwh-w62w-r2mf) | extends | Отправить в значении фильтра спецсимволы языка запросов поискового хранилища (query string) |
| [GHSA-mwpv-rg79-863c](https://github.com/advisories/GHSA-mwpv-rg79-863c) | extends | Передать в ключе фильтра путь к полю, скрытому из ответа, и сравнить выборки при разных значениях |

### INJ-NOSQL — NoSQL-инъекция операторами запросов не исполняется (RWB-0084, багов: 2)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-q86m-qjpm-vqcw](https://github.com/advisories/GHSA-q86m-qjpm-vqcw) | extends | Отправить объект условий поиска, где имя ключа (а не значение) содержит синтаксис языка запросов графовой БД, и проверить отказ без изменения структуры запроса |
| [GHSA-hc43-m36c-8v33](https://github.com/advisories/GHSA-hc43-m36c-8v33) | extends | Отправить в параметр поиска строку, выходящую из экранирования regex, с метасимволами |

### INJ-OS-COMMAND — Инъекция команд ОС не исполняется (RWB-0085, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-x9f9-r4m8-9xc2](https://github.com/advisories/GHSA-x9f9-r4m8-9xc2) | extends | Создать пользовательский скрипт (триггер, процедуру), вызывающий запуск процесса ОС через стандартную библиотеку, и проверить, что песочница его запрещает |

### INJ-PATH-TRAVERSAL — Обход каталогов через параметры файлов и путей невозможен (RWB-0086, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-5g75-477j-2c2f](https://github.com/advisories/GHSA-5g75-477j-2c2f) | extends | Отправить request-target без ведущего слэша с сегментами ../ и проверить, что файл вне каталога не отдаётся |

### INJ-REDOS — Пользовательский ввод не вызывает катастрофический backtracking в regex (RWB-0088, багов: 4)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-p6pp-m3f8-5c89](https://github.com/advisories/GHSA-p6pp-m3f8-5c89) | extends | Отправить в числовое поле строку из десятков тысяч цифр, не совпадающую с шаблоном числа, и сравнить время ответа для длины N и 2N |
| [GHSA-7cmj-v6x8-frvv](https://github.com/advisories/GHSA-7cmj-v6x8-frvv) | extends | Передать собственное регулярное выражение с вложенными квантификаторами в функцию языка выражений (matches, replace) и проверить, что выполнение прекращается по тайм-ауту |
| [GHSA-fxj4-p9xp-37v5](https://github.com/advisories/GHSA-fxj4-p9xp-37v5) | extends | Повторить проверку ReDoS для каждой функции выражений с regex (matches, replaceMatches) и каждой версии API |
| [GHSA-659m-px2c-25wj](https://github.com/advisories/GHSA-659m-px2c-25wj) | covered | _только пруф_: ReDoS через ввод — ровно запись |

### INJ-SQL — SQL-инъекция во входных параметрах не исполняется (RWB-0089, багов: 3)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-mqjf-5f49-2fjh](https://github.com/advisories/GHSA-mqjf-5f49-2fjh) | extends | Отправить в аргумент функции выражения фильтра (например, jsonArrayContains) значение с одинарной кавычкой и SQL-фрагментом |
| [GHSA-cgfv-jrfp-2r7v](https://github.com/advisories/GHSA-cgfv-jrfp-2r7v) | extends | Сохранить SQL-синтаксис в имени объекта и вызвать операцию, использующую его позже (экспорт, отчёт), и проверить, что SQL не выполняется |
| [GHSA-2mfg-cc43-9pcj](https://github.com/advisories/GHSA-2mfg-cc43-9pcj) | extends | Отправить SQL-инъекцию в имени поля (ключе метаданных) фильтра; повторить со значением, оканчивающимся обратным слэшем |

### INJ-SSRF-PARAMETERS — Параметры с URL и хостами не дают доступа к внутренней сети (RWB-0090, багов: 9)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-vvgp-rfg2-7rr6](https://github.com/advisories/GHSA-vvgp-rfg2-7rr6) | extends | Отправить в поле типа IP-адреса имя хоста под контролем тестировщика и проверить по журналу DNS, что сервер не разрешает его при разборе |
| [GHSA-hgj6-7826-r7m5](https://github.com/advisories/GHSA-hgj6-7826-r7m5) | extends | _только пруф_: Тот же вариант, что у GHSA-vvgp-rfg2-7rr6 (DNS-запрос при разборе) |
| [GHSA-vqc2-c9jh-3jjv](https://github.com/advisories/GHSA-vqc2-c9jh-3jjv) | covered | _только пруф_: Параметр с URL, запрашиваемый сервером |
| [GHSA-r56g-q4p6-m3p6](https://github.com/advisories/GHSA-r56g-q4p6-m3p6) | extends | Создать и запустить сценарий, в шаблоне которого функция HTTP-запроса обращается к адресу облачных метаданных, и проверить отказ |
| [GHSA-68r5-9hpg-7qw9](https://github.com/advisories/GHSA-68r5-9hpg-7qw9) | covered | _только пруф_: Внутренние адреса и file:// уже в шагах записи |
| [GHSA-8w86-m9h8-hvqg](https://github.com/advisories/GHSA-8w86-m9h8-hvqg) | covered | _только пруф_: Внутренние адреса и file:// уже в шагах записи |
| [GHSA-x939-7fq5-v9v6](https://github.com/advisories/GHSA-x939-7fq5-v9v6) | covered | _только пруф_: Шаг записи «сервер прикладывает к исходящему вызову свои учётные данные» |
| [GHSA-whpp-xv3h-rwxf](https://github.com/advisories/GHSA-whpp-xv3h-rwxf) | extends | Указать внутренний адрес в заголовках адреса ответа (WS-Addressing ReplyTo, FaultTo) |
| [GHSA-7m2p-62gw-p8qq](https://github.com/advisories/GHSA-7m2p-62gw-p8qq) | extends | Передать URL, хост которого неоднозначен для разных парсеров |

### INJ-TEMPLATE-SSTI — Инъекция в серверные шаблоны не исполняется (RWB-0091, багов: 4)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-73mf-m39p-wpm9](https://github.com/advisories/GHSA-73mf-m39p-wpm9) | extends | Передать в аргумент шаблона конфигурации значение с переводом строки и новыми YAML-ключами и проверить, что структура итоговой конфигурации не меняется |
| [GHSA-3g44-3m7x-cgg2](https://github.com/advisories/GHSA-3g44-3m7x-cgg2) | extends | Создать объект с идентификатором (имя столбца, поля), содержащим синтаксис языка генерируемого кода, и вызвать операцию, компилирующую выражение с ним |
| [GHSA-9x82-rm84-c6x7](https://github.com/advisories/GHSA-9x82-rm84-c6x7) | covered | _только пруф_: Исполнение кода через серверный шаблон |
| [GHSA-9f52-rjqv-25qv](https://github.com/advisories/GHSA-9f52-rjqv-25qv) | extends | Передать в поле, вычисляемое как выражение в ограниченном контексте, вызов метода без аргументов |

### INJ-UNSAFE-DESERIALIZATION — Небезопасная десериализация пользовательских данных невозможна (RWB-0198, багов: 3)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-gx83-3vf8-gh7j](https://github.com/advisories/GHSA-gx83-3vf8-gh7j) | extends | Отправить в полиморфное поле с базовым типом Comparable идентификатор типа с именем произвольного класса, реализующего этот интерфейс |
| [GHSA-wg5r-wc3x-39vc](https://github.com/advisories/GHSA-wg5r-wc3x-39vc) | extends | Передать в поле запроса имя произвольного класса, не реализующего ожидаемый интерфейс, и проверить, что сервер не загружает его |
| [GHSA-72c8-3wwg-r59w](https://github.com/advisories/GHSA-72c8-3wwg-r59w) | extends | _только пруф_: Тот же вариант, что у GHSA-wg5r-wc3x-39vc: выбор класса по имени из запроса |

### INJ-XXE — Внешние сущности XML не обрабатываются (RWB-0199, багов: 2)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-x4r9-gmw3-hxww](https://github.com/advisories/GHSA-x4r9-gmw3-hxww) | covered | _только пруф_: Механизм обхода списка в бюллетене не описан — запись по следствию |
| [GHSA-2q27-6p2h-q6r3](https://github.com/advisories/GHSA-2q27-6p2h-q6r3) | extends | Вернуть с подконтрольного внешнего сервера XML-ответ с внешней сущностью и проверить, что сервис её не раскрывает |

### PAGE-SEARCH-SPECIAL-CHARS — Поиск со спецсимволами и wildcard не ломается и не расширяет выборку (RWB-0094, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-8r2h-xh92-gq57](https://github.com/advisories/GHSA-8r2h-xh92-gq57) | covered | _только пруф_: Wildcard в поиске расширяет выборку — ровно запись |

### RESIL-CIRCUIT-BREAKER — Circuit breaker размыкается и восстанавливается по политике (RWB-0200, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-2827-2mxx-j8pv](https://github.com/advisories/GHSA-2827-2mxx-j8pv) | extends | Отправить много уникальных сбойных запросов и проверить, что circuit breaker и повторы для других запросов работают |

### REST-AUTH-ERROR-NO-LEAK — Ошибки аутентификации без утечки (RWB-0201, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-fqjh-8322-vgrv](https://github.com/advisories/GHSA-fqjh-8322-vgrv) | covered | _только пруф_: Ошибка аутентификации раскрывает сведения о конфигурации |

### REST-CORS-POLICY — Политика CORS (RWB-0112, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-6cqp-g7gg-8hr5](https://github.com/advisories/GHSA-6cqp-g7gg-8hr5) | extends | Отправить запрос с Origin: null при неразрешённом null-origin и проверить, что он отклоняется |

### REST-MASS-ASSIGNMENT — Mass assignment защищённых полей (RWB-0121, багов: 8)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-5gvw-p9qm-jgwh](https://github.com/advisories/GHSA-5gvw-p9qm-jgwh) | extends | Отправить на публичный эндпоинт привилегированные поля, которые модель разворачивает из вложенного объекта на верхний уровень JSON, и проверить, что они не записаны |
| [GHSA-3pjw-73gf-8qr5](https://github.com/advisories/GHSA-3pjw-73gf-8qr5) | extends | Отправить защищённое поле под именем в стиле именования API (snake_case) и под исходным именем и проверить, что оно не записано |
| [GHSA-5hh8-q8hv-fr38](https://github.com/advisories/GHSA-5hh8-q8hv-fr38) | extends | Отправить на публичный эндпоинт привилегированное поле-коллекцию (список ролей, словарь прав) и проверить, что она не заполнена |
| [GHSA-rcqc-6cw3-h962](https://github.com/advisories/GHSA-rcqc-6cw3-h962) | extends | _только пруф_: Тот же вариант, что у GHSA-5gvw-p9qm-jgwh |
| [GHSA-mhm7-754m-9p8w](https://github.com/advisories/GHSA-mhm7-754m-9p8w) | extends | Отправить на публичный эндпоинт привилегированное полиморфное поле вместе с его внешним свойством-дискриминатором типа и проверить, что поле не записано |
| [GHSA-5jmj-h7xm-6q6v](https://github.com/advisories/GHSA-5jmj-h7xm-6q6v) | extends | Отправить защищённое поле с именем в другом регистре при регистронезависимом сопоставлении полей |
| [GHSA-cv39-x4c6-hhp2](https://github.com/advisories/GHSA-cv39-x4c6-hhp2) | extends | Отправить JSON Patch с многосегментным путём через поле, закрытое для записи |
| [GHSA-7fxc-486f-32q9](https://github.com/advisories/GHSA-7fxc-486f-32q9) | extends | Отправить защищённое поле в теле каждого поддерживаемого медиатипа (Collection+JSON, UBER) |

### REST-OPEN-REDIRECT — Валидация redirect URL (RWB-0125, багов: 7)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-pjp7-q6wp-97qx](https://github.com/advisories/GHSA-pjp7-q6wp-97qx) | covered | _только пруф_: Обход проверки redirect URL; конкретная форма URL в бюллетене не описана |
| [GHSA-3rqh-hch3-jhpc](https://github.com/advisories/GHSA-3rqh-hch3-jhpc) | extends | Передать URL возврата с сегментами ./ и ../ |
| [GHSA-463r-5m89-4xfr](https://github.com/advisories/GHSA-463r-5m89-4xfr) | extends | Передать URL возврата с табуляцией или переводом строки между // |
| [GHSA-92m7-4fpw-2wxm](https://github.com/advisories/GHSA-92m7-4fpw-2wxm) | covered | _только пруф_: Внешний URL в параметре возврата — ровно запись |
| [GHSA-x2r2-rvhq-2mqv](https://github.com/advisories/GHSA-x2r2-rvhq-2mqv) | extends | Подставить внешний URL в cookie сохранённого запроса и выполнить вход |
| [GHSA-h3qp-gqrc-q736](https://github.com/advisories/GHSA-h3qp-gqrc-q736) | extends | Запросить путь с префиксом redirect: и внешним URL |
| [GHSA-r8fj-rff6-f7h5](https://github.com/advisories/GHSA-r8fj-rff6-f7h5) | covered | _только пруф_: Внешний URL возврата после входа не проверяется |

### REST-READONLY-WRITEONLY — Поля readOnly/writeOnly (RWB-0129, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-9fxm-vc8v-hj55](https://github.com/advisories/GHSA-9fxm-vc8v-hj55) | covered | _только пруф_: readOnly-поле записывается из запроса |

### REST-SORT-INVALID-FIELD — Сортировка по неизвестному полю (RWB-0134, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-5vpf-xvv7-c8vh](https://github.com/advisories/GHSA-5vpf-xvv7-c8vh) | covered | _только пруф_: Механизм не описан; запись проверяет, что некорректная сортировка даёт 4xx |

### REST-SSRF-URL-FETCH — Контроль server-side URL fetch (RWB-0135, багов: 2)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-5hx7-j24v-rffj](https://github.com/advisories/GHSA-5hx7-j24v-rffj) | covered | _только пруф_: Классический server-side URL fetch по параметру |
| [GHSA-xm3x-9cfw-jhx4](https://github.com/advisories/GHSA-xm3x-9cfw-jhx4) | extends | Передать в параметр URL адрес на разрешённом хосте с произвольным путём и проверить, что без авторизации вызывающего сервер не отправляет туда служебный токен |

### SEC-AUTHN-MISSING — Protected operation rejects missing credentials (RWB-0143, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-p462-xxwx-pqf4](https://github.com/advisories/GHSA-p462-xxwx-pqf4) | covered | _только пруф_: Изменяющая операция без аутентификации |

### SEC-AUTHZ-FUNCTION — User without required permission cannot invoke operation (RWB-0146, багов: 21)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-9v77-j4xv-34gq](https://github.com/advisories/GHSA-9v77-j4xv-34gq) | covered | _только пруф_: Нет проверки права на служебную операцию; последствие — передача сохранённых кредов (ср. SEC-CONFUSED-DEPUTY) |
| [GHSA-rf99-f9j2-gv3f](https://github.com/advisories/GHSA-rf99-f9j2-gv3f) | extends | Под пользователем с правом отправки или чтения выполнить операцию с параметром, неявно меняющим настройку ресурса (тип маршрутизации адреса), и проверить отказ без права на изменение ресурса |
| [GHSA-cvw4-55pp-3hfq](https://github.com/advisories/GHSA-cvw4-55pp-3hfq) | covered | _только пруф_: Нет проверки права на административную операцию чтения |
| [GHSA-962x-ccwf-8x6p](https://github.com/advisories/GHSA-962x-ccwf-8x6p) | covered | _только пруф_: Пользователь без нужной привилегии вызывает административную операцию |
| [GHSA-48qw-824m-86pr](https://github.com/advisories/GHSA-48qw-824m-86pr) | extends | Повторить операцию на каждом поддерживаемом языке команд (SQL, скриптовые) под ролью только для чтения |
| [GHSA-vg6x-6pg9-6qwg](https://github.com/advisories/GHSA-vg6x-6pg9-6qwg) | extends | Повторить проверку права для каждой операции группы (все команды изменения схемы), а не только для одной |
| [GHSA-xj53-j257-hxvg](https://github.com/advisories/GHSA-xj53-j257-hxvg) | covered | _только пруф_: Пользователь без права записи выполняет запись |
| [GHSA-2xv8-gjwh-fv8p](https://github.com/advisories/GHSA-2xv8-gjwh-fv8p) | extends | Повторить операции над данными без прав через каждый альтернативный интерфейс к тем же данным (HTTP API хранилища, а не только SQL) |
| [GHSA-2r5w-jh6g-8hff](https://github.com/advisories/GHSA-2r5w-jh6g-8hff) | covered | _только пруф_: Операция без проверки права |
| [GHSA-xx59-jv36-5r44](https://github.com/advisories/GHSA-xx59-jv36-5r44) | covered | _только пруф_: Операция без проверки права |
| [GHSA-mpff-xhg4-vr45](https://github.com/advisories/GHSA-mpff-xhg4-vr45) | covered | _только пруф_: Операция без проверки нужного права |
| [GHSA-8263-qv4g-vfxr](https://github.com/advisories/GHSA-8263-qv4g-vfxr) | covered | _только пруф_: Вспомогательная операция без проверки права |
| [GHSA-p44q-fmwr-jqr7](https://github.com/advisories/GHSA-p44q-fmwr-jqr7) | covered | _только пруф_: Операция без проверки права |
| [GHSA-wjmq-rpqq-w4h9](https://github.com/advisories/GHSA-wjmq-rpqq-w4h9) | covered | _только пруф_: Операция без проверки права |
| [GHSA-hwvp-7xqv-8jx3](https://github.com/advisories/GHSA-hwvp-7xqv-8jx3) | covered | _только пруф_: Вспомогательная операция без проверки права |
| [GHSA-jhcq-6wqp-qcfx](https://github.com/advisories/GHSA-jhcq-6wqp-qcfx) | extends | Вызвать операцию под пользователем с глобальным правом того же типа, но без права на конкретный объект |
| [GHSA-g7c6-wxjf-8564](https://github.com/advisories/GHSA-g7c6-wxjf-8564) | covered | _только пруф_: Отсутствие проверки права на операцию — ровно запись |
| [GHSA-r2g5-993q-664g](https://github.com/advisories/GHSA-r2g5-993q-664g) | extends | Заменить родительскую группу, включив в неё объект, требующий дополнительной привилегии, под пользователем только с общим правом записи |
| [GHSA-qvj8-gwpm-4x49](https://github.com/advisories/GHSA-qvj8-gwpm-4x49) | extends | Отправить запрос проверки (dry-run) с предлагаемыми значениями под пользователем только с правом чтения |
| [GHSA-mw82-xcg6-gx79](https://github.com/advisories/GHSA-mw82-xcg6-gx79) | extends | Выполнить операцию над объектом под пользователем с правом на операцию, но без права чтения этого объекта |
| [GHSA-p2rj-mrmc-9w29](https://github.com/advisories/GHSA-p2rj-mrmc-9w29) | covered | _только пруф_: Операция чтения выполняется без проверки требуемой привилегии |

### SEC-AUTHZ-METHOD-MATRIX — Authorization is enforced for every method (RWB-0147, багов: 2)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-9jjc-fw8x-fmwx](https://github.com/advisories/GHSA-9jjc-fw8x-fmwx) | extends | Указать защищённую тему как тему завещания при подключении MQTT без права записи, оборвать соединение и проверить, что сообщение не опубликовано |
| [GHSA-h3x4-894j-xpx5](https://github.com/advisories/GHSA-h3x4-894j-xpx5) | extends | Повторить матрицу методов для ресурса, запрошенного до входа через форму, после возврата на него по завершении входа |

### SEC-BOLA-BULK — Bulk endpoint enforces ownership per item (RWB-0148, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-h3m5-97jq-qjrf](https://github.com/advisories/GHSA-h3m5-97jq-qjrf) | covered | _только пруф_: Массовая операция без проверки владения по каждому элементу — ровно запись |

### SEC-FAIL-CLOSED-INPUT — Неожиданный тип, пустое или отсутствующее поле проверки безопасности ведёт к отказу, а не к пропуску проверки (RWB-0006, багов: 5)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-8xjq-pr36-ccgf](https://github.com/advisories/GHSA-8xjq-pr36-ccgf) | covered | _только пруф_: Пустое поле проверки безопасности ведёт к пропуску проверки |
| [GHSA-h4pc-58cc-hc95](https://github.com/advisories/GHSA-h4pc-58cc-hc95) | extends | Запросить защищённый ресурс без подписи по каждому маршруту, где идентификатор ресурса стоит в другом сегменте пути, и проверить отказ |
| [GHSA-4w3q-qpfq-v992](https://github.com/advisories/GHSA-4w3q-qpfq-v992) | extends | Передать идентификатор защищённого ресурса в неканонической форме (пробел в конце, вариант с диакритикой, другой регистр) без учётных данных и проверить отказ |
| [GHSA-582q-v28r-7cxr](https://github.com/advisories/GHSA-582q-v28r-7cxr) | covered | _только пруф_: Отсутствующее поле приводит к пропуску проверки доступа |
| [GHSA-jrv5-8w28-4265](https://github.com/advisories/GHSA-jrv5-8w28-4265) | extends | Выполнить вход с существующим логином и пустым или null паролем |

### SEC-OWNERSHIP-DELETE — User cannot delete another owner’s resource (RWB-0149, багов: 3)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-j769-9gv9-65gr](https://github.com/advisories/GHSA-j769-9gv9-65gr) | covered | _только пруф_: Удаление чужого объекта (токена) по идентификатору |
| [GHSA-9284-fjc3-fmmj](https://github.com/advisories/GHSA-9284-fjc3-fmmj) | covered | _только пруф_: Удаление чужого ресурса по ID в пути |
| [GHSA-wh3w-v6gj-fqh2](https://github.com/advisories/GHSA-wh3w-v6gj-fqh2) | covered | _только пруф_: Удаление чужого объекта — ровно запись |

### SEC-OWNERSHIP-READ — User cannot read another owner’s resource (RWB-0150, багов: 6)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-jxpj-9j24-w337](https://github.com/advisories/GHSA-jxpj-9j24-w337) | covered | _только пруф_: Чтение чужого ресурса по ID |
| [GHSA-qpm9-h556-mwxm](https://github.com/advisories/GHSA-qpm9-h556-mwxm) | covered | _только пруф_: Чтение чужих ресурсов по ID и в списке |
| [GHSA-vvhj-w2jq-263q](https://github.com/advisories/GHSA-vvhj-w2jq-263q) | extends | Запросить сессии другого пользователя по его идентификатору через эндпоинт управления сессиями |
| [GHSA-wv7f-c794-82v6](https://github.com/advisories/GHSA-wv7f-c794-82v6) | covered | _только пруф_: Чтение объекта без прав — ровно запись |
| [GHSA-r989-cjhx-3v49](https://github.com/advisories/GHSA-r989-cjhx-3v49) | covered | _только пруф_: Чтение чужого объекта — ровно запись |
| [GHSA-g28p-6mcc-v4rv](https://github.com/advisories/GHSA-g28p-6mcc-v4rv) | covered | _только пруф_: Чтение чужих данных — ровно запись |

### SEC-OWNERSHIP-REFERENCE-INDIRECT — Indirect resource references preserve authorization (RWB-0151, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-694g-j8pj-cjj5](https://github.com/advisories/GHSA-694g-j8pj-cjj5) | covered | _только пруф_: Доступ к объекту через связь с родителем без прав — ровно запись |

### SEC-OWNERSHIP-UPDATE — User cannot modify another owner’s resource (RWB-0152, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-6h3c-r723-7fx3](https://github.com/advisories/GHSA-6h3c-r723-7fx3) | covered | _только пруф_: Изменение чужого ресурса по ID |

### SEC-ROLE-SELF-ASSIGN — User cannot grant self a higher role (RWB-0153, багов: 2)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-m9c2-85gv-8xr5](https://github.com/advisories/GHSA-m9c2-85gv-8xr5) | extends | Под учёткой с правом редактирования ресурса отправить его обновление с настройками доступа, дающими роль владельца другой своей учётке |
| [GHSA-45ph-gxxr-gwgw](https://github.com/advisories/GHSA-45ph-gxxr-gwgw) | extends | Выдать себе более высокое право через универсальный API редактирования данных объекта и проверить, что применяются те же проверки, что в основном пути |

### SEC-TENANT-READ — Tenant A cannot read tenant B data (RWB-0157, багов: 2)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-x8mg-6r4p-87pf](https://github.com/advisories/GHSA-x8mg-6r4p-87pf) | extends | Повторить доступ к чужой базе через все вспомогательные эндпоинты (пакетная запись, временные ряды, интеграции мониторинга), а не только через основной |
| [GHSA-xqr9-4wvv-gvch](https://github.com/advisories/GHSA-xqr9-4wvv-gvch) | covered | _только пруф_: Чтение данных другого арендатора по ID |

### SEC-TOKEN-EXPIRED — Expired access token is rejected (RWB-0161, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-mqwc-6qwc-v9gq](https://github.com/advisories/GHSA-mqwc-6qwc-v9gq) | covered | _только пруф_: Истёкший токен принимается; nbf — AUTH-JWT-TIME-CLAIMS |

### SEC-TOKEN-ISSUER — Token from untrusted issuer is rejected (RWB-0202, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-fpm2-m4qq-wghr](https://github.com/advisories/GHSA-fpm2-m4qq-wghr) | covered | _только пруф_: Токен от другого издателя принимается; аудитория — SEC-TOKEN-AUDIENCE |

### SEC-TOKEN-REVOKED — Revoked token cannot be reused (RWB-0203, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-v5g5-wwmp-jppw](https://github.com/advisories/GHSA-v5g5-wwmp-jppw) | extends | Отозвать refresh-токен, перезапустить сервис и повторить обмен этим токеном |

### SEC-TOKEN-SIGNATURE — Token with invalid signature is rejected (RWB-0204, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-qvc3-6q9x-95pj](https://github.com/advisories/GHSA-qvc3-6q9x-95pj) | extends | Отправить произвольную строку и неподписанный JWT на маршрут, защищённый без требований к ролям и разрешениям, и проверить 401 |

### SECURITY-AUTH-REQUIRED — Protected operation rejects unauthenticated requests (RWB-0162, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-c82x-f4xr-qv33](https://github.com/advisories/GHSA-c82x-f4xr-qv33) | covered | _только пруф_: Ровно запись |

### VAL-DEEP-NESTING — Чрезмерно вложенный JSON отклоняется без деградации сервиса (RWB-0165, багов: 3)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-65r4-943x-97jj](https://github.com/advisories/GHSA-65r4-943x-97jj) | extends | Отправить XML с глубокой вложенностью, где каждый элемент объявляет новый уникальный префикс пространства имён |
| [GHSA-cc4v-rvgp-2pf3](https://github.com/advisories/GHSA-cc4v-rvgp-2pf3) | covered | _только пруф_: Глубокая вложенность JSON |
| [GHSA-3wrr-7qpf-2prh](https://github.com/advisories/GHSA-3wrr-7qpf-2prh) | covered | _только пруф_: Чрезмерная вложенность JSON — ровно запись |

### VAL-MALFORMED-JSON — Синтаксически некорректный JSON отклоняется (RWB-0170, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-7hhh-6rmp-j9qf](https://github.com/advisories/GHSA-7hhh-6rmp-j9qf) | extends | Отправить тело с нераспознаваемым токеном длиной в миллионы символов и проверить, что ответ 4xx приходит быстро, а фрагмент токена в сообщении усечён |

### WS-MESSAGE-LIMITS — Размер и частота сообщений ограничены (RWB-0205, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-7ppr-r889-mcf2](https://github.com/advisories/GHSA-7ppr-r889-mcf2) | extends | Отправить сообщение из множества мелких кадров продолжения без FIN и проверить, что суммарный размер ограничен |

### WS-SUBSCRIPTION-AUTHZ — Подписки и сообщения авторизуются по каждому каналу (RWB-0179, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-fwww-cp23-7f5g](https://github.com/advisories/GHSA-fwww-cp23-7f5g) | covered | _только пруф_: Авторизация подписок по каждому каналу |

