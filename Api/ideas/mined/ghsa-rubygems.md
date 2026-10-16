# Кандидаты из баг-трекеров: партия `ghsa-rubygems`

Сгенерировано `tools/mining/cluster.py` из `build/mining/<batch>/batches/*.out.jsonl` и
`ideas/mined/ghsa-rubygems.review.yaml` — правки решений делаются в review-файле, затем пересборка.
План — `docs/BUG_MINING_PLAN.md`, шаги 6–7; применение — `tools/mining/apply_proofs.py`.

## Сводка

- Новых паттернов: 11 → идей: 7 (принять: 7, отклонить: 0, не решено: 0).
- Пруфы к существующим: 154 багов → 55 записей; новых шагов-вариантов: 97.

## Новые идеи

Принятые становятся записями `status: draft` с меткой `real-world-bug` и ссылкой на RWB.

| # | Решение | Запись / файл | Идея | Подтверждающие баги |
|---|---|---|---|---|
| 1 | accept | `SEC-ALT-REPRESENTATION-ACCESS` (RWB-0231)<br>`checks/security/access-control/SEC-ALT-REPRESENTATION-ACCESS.yaml` | Закрытый ресурс (неопубликованный, приватный, защищённый паролем доступа) недоступен ни через одно альтернативное представление — встраивание (embed), превью, дерево и вложенные списки, ленты, поиск, метаданные; правила доступа и публикации такие же, как у основного маршрута | [GHSA-qcj6-vxwx-4rqv](https://github.com/advisories/GHSA-qcj6-vxwx-4rqv), [GHSA-mqq5-j7w8-2hgh](https://github.com/advisories/GHSA-mqq5-j7w8-2hgh), [GHSA-5jm7-g527-m694](https://github.com/advisories/GHSA-5jm7-g527-m694) |
| 2 | accept | `INJ-ARCHIVE-ENTRY-NAME-EVAL` (RWB-0232)<br>`checks/security/injection.yaml` | Имена файлов внутри загруженного пользователем содержимого (git-репозиторий, архив, пакет) с переводом строки, кавычками и выражениями кода (#{...}, ${...}, $(...)) при перечислении и обработке остаются текстом и не исполняются; отличие от FILE-FILENAME-SANITIZATION — имена внутри содержимого, а не имя загружаемого файла | [GHSA-pphf-gfrm-v32r](https://github.com/advisories/GHSA-pphf-gfrm-v32r), [GHSA-pfpr-3463-c6jh](https://github.com/advisories/GHSA-pfpr-3463-c6jh) |
| 3 | accept | `AUTH-PROTOCOL-SESSION-OWNER-BINDING` (RWB-0233)<br>`checks/security/authentication-session.yaml` | Идентификатор протокольной сессии (Mcp-Session-Id, ID потока SSE, ID сессии в пути) привязан к аутентифицированному владельцу — чужой ID с другой учёткой или без неё даёт 403/404, существующий поток владельца не перехватывается и не переключается | [GHSA-5p9g-j988-pcwv](https://github.com/advisories/GHSA-5p9g-j988-pcwv), [GHSA-qvqr-5cv7-wh35](https://github.com/advisories/GHSA-qvqr-5cv7-wh35) |
| 4 | accept | `AUTH-OAUTH-PUBLIC-CLIENT-CONSENT` (RWB-0234)<br>`checks/security/authentication-session.yaml` | Для публичного OAuth-клиента (без секрета) повторный запрос авторизации показывает экран согласия, а не выдаёт код автоматически по прошлому одобрению — иначе любой, кто знает client_id и разрешённый redirect_uri, получает код без участия пользователя (RFC 8252 §8.6) | [GHSA-7w2c-w47h-789w](https://github.com/advisories/GHSA-7w2c-w47h-789w) |
| 5 | accept | `HTTP-PATH-PREFIX-SEGMENT-BOUNDARY` (RWB-0235)<br>`checks/rest/http-protocol.yaml` | Правило по префиксу пути (статика /css, /js, исключения из аутентификации, маршрутизация прокси) соблюдает границу сегмента — /css-config.env, /cssbackup.sql, /js.env не попадают под правило /css/, /js/ | [GHSA-h2jq-g4cq-5ppq](https://github.com/advisories/GHSA-h2jq-g4cq-5ppq) |
| 6 | accept | `INJ-REFLECTED-XSS` (RWB-0236)<br>`checks/security/injection.yaml` | Параметры запроса (фильтр, поиск, сообщения об ошибке) не отражаются в HTML-ответе без экранирования по контексту; Content-Type соответствует содержимому; пара к INJ-STORED-XSS | [GHSA-cmh9-rx85-xj38](https://github.com/advisories/GHSA-cmh9-rx85-xj38) |
| 7 | accept | `PRIV-IMPORT-URL-CREDENTIALS-NOT-STORED` (RWB-0237)<br>`checks/security/privacy.yaml` | Учётные данные из URL источника импорта или зеркалирования (https://user:token@host/...) после завершения импорта не сохраняются и не возвращаются в параметрах объекта (адрес источника, настройки зеркала, журнал задачи) | [GHSA-mmmm-chjf-jmvw](https://github.com/advisories/GHSA-mmmm-chjf-jmvw) |

## Пруфы к существующим

Запись получает метку `real-world-bug` и `Real-world bug: RWB-NNNN`; статус не меняется. Для `extends`
текст варианта добавляется шагом (`steps[].action`, в `notes` — RWB). Неверное совпадение — ID бага в
`proofs.exclude`, вариант без нового шага — в `proofs.no_variant`.

### ASYNC-WEBHOOK-URL-SSRF — URL вебхука не может указывать на внутренние адреса (RWB-0054, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-2g9c-vf8h-prxx](https://github.com/advisories/GHSA-2g9c-vf8h-prxx) | extends | Создать push-подписку с endpoint на произвольный и на внутренний хост и проверить, что принимаются только адреса разрешённых push-сервисов |

### AUTH-CSRF — Изменяющие операции с cookie-аутентификацией защищены от CSRF (RWB-0190, багов: 6)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-f3qm-vfc3-jg6v](https://github.com/advisories/GHSA-f3qm-vfc3-jg6v) | extends | Отправить без CSRF-токена запросы к служебным эндпоинтам (предпросмотр, рендер), для которых защита могла быть отключена |
| [GHSA-wqw3-p83g-r24v](https://github.com/advisories/GHSA-wqw3-p83g-r24v) | covered | _только пруф_: Классический CSRF |
| [GHSA-p4xx-w6fr-c4w9](https://github.com/advisories/GHSA-p4xx-w6fr-c4w9) | covered | _только пруф_: Классический CSRF |
| [GHSA-cc8c-26rj-v2vx](https://github.com/advisories/GHSA-cc8c-26rj-v2vx) | covered | _только пруф_: Механизм перехвата кода не описан; описанное следствие — отсутствие CSRF-защиты |
| [GHSA-8639-qx56-r428](https://github.com/advisories/GHSA-8639-qx56-r428) | extends | Выполнить изменяющую операцию методом GET без CSRF-токена (переход по ссылке) и проверить, что состояние не изменилось |
| [GHSA-mcvq-7xjq-46x6](https://github.com/advisories/GHSA-mcvq-7xjq-46x6) | covered | _только пруф_: Ровно то, что проверяет запись |

### AUTH-EXTERNAL-IDP-UNVERIFIED-EMAIL — Вход через внешний IdP не связывается с учёткой по неподтверждённому email (RWB-0041, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-5g66-628f-7cvj](https://github.com/advisories/GHSA-5g66-628f-7cvj) | covered | _только пруф_: Ровно сценарий записи |

### AUTH-LOGOUT-INVALIDATES — После выхода токен и сессия недействительны (RWB-0059, багов: 3)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-4cx3-3c38-j9vv](https://github.com/advisories/GHSA-4cx3-3c38-j9vv) | covered | _только пруф_: После выхода сессия недействительна — ровно проверка записи |
| [GHSA-9j94-67jr-4cqj](https://github.com/advisories/GHSA-9j94-67jr-4cqj) | extends | Выполнить выход параллельно с долгим запросом в той же сессии и после завершения обоих повторить запрос со старой cookie |
| [GHSA-vpfw-47h7-xj4g](https://github.com/advisories/GHSA-vpfw-47h7-xj4g) | extends | _только пруф_: Тот же вариант, что у GHSA-9j94-67jr-4cqj в этой партии |

### AUTH-PASSWORD-CHANGE-REVOKES — Смена или сброс пароля завершает другие сессии (RWB-0238, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-438x-2p9v-g8h9](https://github.com/advisories/GHSA-438x-2p9v-g8h9) | extends | Сменить пароль пользователя от имени администратора и выполнить запрос в ранее открытой сессии пользователя |

### AUTH-SESSION-TIMEOUT — Сессия истекает после простоя и абсолютного срока (RWB-0063, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-52jp-gj8w-j6xh](https://github.com/advisories/GHSA-52jp-gj8w-j6xh) | extends | Создать множество сессий без закрытия и проверить, что простаивающие удаляются по таймауту |

### CONC-REQUEST-CONTEXT-ISOLATION — Параллельные запросы разных пользователей получают только свой контекст и свой ответ (RWB-0007, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-356j-hg45-x525](https://github.com/advisories/GHSA-356j-hg45-x525) | covered | _только пруф_: Смешение контекста параллельных запросов разных пользователей — ровно проверка записи |

### ERR-INTERNAL-ERROR-SHAPE — Внутренняя ошибка сервера возвращается в общей модели без утечек (RWB-0068, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-vf99-xw26-86g5](https://github.com/advisories/GHSA-vf99-xw26-86g5) | extends | Вызвать ошибку СУБД в операции, выполняющей запрос пользователя (EXPLAIN), и проверить, что текст ошибки не содержит значений из данных |

### FILE-ARCHIVE-BOMB — Архивные и графические бомбы не исчерпывают ресурсы (RWB-0069, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-92rq-c8cf-prrq](https://github.com/advisories/GHSA-92rq-c8cf-prrq) | extends | Отправить сжатое сообщение протокола (SAMLRequest/SAMLResponse deflate), которое после распаковки превышает лимит размера |

### FILE-DOWNLOAD-AUTHZ — Скачивание файлов проверяет права и срок действия ссылок (RWB-0070, багов: 2)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-3mvf-82qp-8qh5](https://github.com/advisories/GHSA-3mvf-82qp-8qh5) | extends | Получить подписанную ссылку на чувствительный файл, выйти и запросить её без сессии; проверить, что доступ запрещён или срок ссылки — минуты |
| [GHSA-767h-63j4-5226](https://github.com/advisories/GHSA-767h-63j4-5226) | extends | Скачать собственный файл через защищённый эндпоинт и повторить запрос по URL из Location без сессии |

### FILE-EMPTY-AND-MALFORMED-MULTIPART — Пустой файл и некорректный multipart обрабатываются корректно (RWB-0071, багов: 2)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-wpv5-97wm-hp9c](https://github.com/advisories/GHSA-wpv5-97wm-hp9c) | extends | Отправить multipart-часть, блок заголовков которой не завершается пустой строкой и занимает мегабайты |
| [GHSA-p543-xpfm-54cp](https://github.com/advisories/GHSA-p543-xpfm-54cp) | extends | Отправить multipart с преамбулой в сотни мегабайт перед первой границей |

### FILE-RANGE-REQUESTS — Частичное скачивание через Range работает по контракту (RWB-0239, багов: 3)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-x8cg-fq8g-mxfx](https://github.com/advisories/GHSA-x8cg-fq8g-mxfx) | extends | Отправить Range с тысячами перекрывающихся диапазонов 0-0 и проверить, что ответ — 416 или 200 без multipart |
| [GHSA-p9fm-f462-ggrg](https://github.com/advisories/GHSA-p9fm-f462-ggrg) | extends | _только пруф_: Тот же вариант, что GHSA-x8cg-fq8g-mxfx в этой партии |
| [GHSA-xj5v-6v4g-jfw6](https://github.com/advisories/GHSA-xj5v-6v4g-jfw6) | extends | Отправить специально построенный Range и проверить, что размер ответа не превышает размер ресурса многократно |

### FILE-UPLOAD-KEY-COLLISION — Загрузка не перезаписывает чужой файл с тем же именем или ключом хранилища (RWB-0037, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-3cx6-j9j4-54mp](https://github.com/advisories/GHSA-3cx6-j9j4-54mp) | extends | Создать серию приватных экспортов разными пользователями и проверить, что каждый скачивает только свой файл |

### FILE-UPLOAD-SIZE-LIMIT — Лимит размера загружаемого файла соблюдается (RWB-0240, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-8vqr-qjwx-82mw](https://github.com/advisories/GHSA-8vqr-qjwx-82mw) | extends | Отправить загрузку multipart chunked-кодированием без Content-Length сверх лимита |

### GQL-COMPLEXITY-LIMIT — Стоимость запроса ограничена (поля, списки, first/last) (RWB-0241, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-3h96-34p3-xm76](https://github.com/advisories/GHSA-3h96-34p3-xm76) | extends | Отправить запрос с огромным числом комментариев и проверить, что срабатывает лимит токенов |

### GQL-FIELD-LEVEL-AUTHZ — Авторизация применяется на уровне полей и вложенных резолверов (RWB-0194, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-ghmh-q25g-gxxx](https://github.com/advisories/GHSA-ghmh-q25g-gxxx) | covered | _только пруф_: Авторизация на уровне полей и резолверов — ровно проверка записи |

### GRPC-METADATA-MALFORMED — Некорректные и чрезмерные метаданные отклоняются (RWB-0242, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-496j-2rq6-j6cc](https://github.com/advisories/GHSA-496j-2rq6-j6cc) | extends | Отправить метаданные цепочкой HEADERS и множества CONTINUATION-кадров суммарно сверх лимита, а также целые HPACK с длинной цепочкой ведущих нулей |

### HARD-CLIENT-IP-TRUSTED-PROXIES — IP клиента определяется по цепочке доверенных прокси одинаково на всех маршрутах (RWB-0030, багов: 2)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-ffp2-8p2h-4m5j](https://github.com/advisories/GHSA-ffp2-8p2h-4m5j) | covered | _только пруф_: IP клиента по цепочке доверенных прокси — ровно этот механизм |
| [GHSA-9hf4-67fc-4vf4](https://github.com/advisories/GHSA-9hf4-67fc-4vf4) | extends | Отправить X-Forwarded_For и X-Forwarded_Proto (с подчёркиванием) вместе с заголовками прокси и проверить, что значения прокси не перезаписаны |

### HARD-EXCESSIVE-DATA-EXPOSURE — Ответы не содержат внутренних полей сверх контракта (RWB-0076, багов: 2)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-f25h-3mj6-4jpg](https://github.com/advisories/GHSA-f25h-3mj6-4jpg) | extends | Запросить ресурс в альтернативных форматах через расширение пути (.xml, .json) и сравнить набор полей с основным ответом |
| [GHSA-4xq9-vw89-p5cx](https://github.com/advisories/GHSA-4xq9-vw89-p5cx) | extends | _только пруф_: Тот же вариант, что у GHSA-f25h-3mj6-4jpg этой пачки |

### HARD-EXPENSIVE-OPERATION-LIMITS — Дорогие операции ограничены по ресурсам (RWB-0077, багов: 18)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-gh9q-2xrm-x6qv](https://github.com/advisories/GHSA-gh9q-2xrm-x6qv) | extends | Отправить заголовок Cookie предельного размера с множеством разделителей и пустых пар и сравнить время ответа с обычным |
| [GHSA-2x79-gwq3-vxxm](https://github.com/advisories/GHSA-2x79-gwq3-vxxm) | extends | Отправить JSON с буквой i/I на месте вложенного значения и проверить быстрый ответ |
| [GHSA-v569-hp3g-36wr](https://github.com/advisories/GHSA-v569-hp3g-36wr) | extends | Отправить Accept-Encoding с тысячами значений * и сравнить время ответа с обычным |
| [GHSA-v6x5-cg8r-vv6x](https://github.com/advisories/GHSA-v6x5-cg8r-vv6x) | extends | Отправить multipart с множеством частей, у которых длинные параметры с плотными обратными слэшами |
| [GHSA-625h-95r8-8xpm](https://github.com/advisories/GHSA-625h-95r8-8xpm) | extends | Отправить query с числом параметров сверх лимита, разделёнными ';' вместо '&' |
| [GHSA-c2f4-jgmc-q2r5](https://github.com/advisories/GHSA-c2f4-jgmc-q2r5) | extends | Отправить XML с патологическими последовательностями (повторные XML-декларации, тысячи пробелов, '<', '>]', ']>', '>' в атрибутах) и сравнить время разбора с обычным документом того же размера |
| [GHSA-gjh7-p2fx-99vx](https://github.com/advisories/GHSA-gjh7-p2fx-99vx) | covered | _только пруф_: Плоский вход с большим числом элементов уже есть в шагах записи |
| [GHSA-2m96-52r3-2f3g](https://github.com/advisories/GHSA-2m96-52r3-2f3g) | extends | Отправить в поле расписания (текстом или cron) строку длиной десятки тысяч символов |
| [GHSA-5866-49gr-22v4](https://github.com/advisories/GHSA-5866-49gr-22v4) | extends | Отправить XML с множеством вложенных расширений внутренних сущностей (billion laughs) |
| [GHSA-r55c-59qm-vjw6](https://github.com/advisories/GHSA-r55c-59qm-vjw6) | extends | _только пруф_: Тот же вариант, что у GHSA-c2f4-jgmc-q2r5 в этой партии |
| [GHSA-4xqq-m2hx-25v8](https://github.com/advisories/GHSA-4xqq-m2hx-25v8) | extends | _только пруф_: Тот же вариант, что у GHSA-c2f4-jgmc-q2r5 в этой партии |
| [GHSA-8c8q-2xw3-j869](https://github.com/advisories/GHSA-8c8q-2xw3-j869) | extends | Передать огромное значение параметра, задающего число повторов или итераций обработки |
| [GHSA-vg3r-rm7w-2xgh](https://github.com/advisories/GHSA-vg3r-rm7w-2xgh) | extends | _только пруф_: Тот же вариант, что у GHSA-c2f4-jgmc-q2r5 в этой партии |
| [GHSA-3px7-jm2p-6h2c](https://github.com/advisories/GHSA-3px7-jm2p-6h2c) | extends | Передать закодированный идентификатор (hashid) длиной до лимита URL веб-сервера и замерить время ответа |
| [GHSA-3h57-hmj3-gj3p](https://github.com/advisories/GHSA-3h57-hmj3-gj3p) | extends | Отправить multipart с десятками тысяч нефайловых частей и проверить, что лимит считает все части, а не только файлы |
| [GHSA-636f-xm5j-pj9m](https://github.com/advisories/GHSA-636f-xm5j-pj9m) | extends | Отправить в поле с серверным рендерингом Markdown большой патологический документ и сравнить время с обычным документом того же размера |
| [GHSA-4qw4-jpp4-8gvp](https://github.com/advisories/GHSA-4qw4-jpp4-8gvp) | extends | Отправить в поле с Markdown длинный текст из множества фрагментов, похожих на автоссылки, и сравнить время рендера с текстом вдвое короче |
| [GHSA-v6j3-7jrw-hq2p](https://github.com/advisories/GHSA-v6j3-7jrw-hq2p) | extends | Отправить форму с большим числом параметров, имена которых дают коллизии хэша, и проверить время ответа и лимит числа параметров |

### HARD-SLOW-CLIENT-LIMITS — Медленные и неполные запросы и непрочитанные ответы не накапливаются без ограничения (RWB-0024, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-qpgp-93vx-g8v8](https://github.com/advisories/GHSA-qpgp-93vx-g8v8) | extends | Отправить при включённом PROXY protocol поток байтов без CRLF и проверить закрытие соединения |

### HTTP-HEADER-SIZE-LIMIT — Слишком большие заголовки отклоняются контролируемо (RWB-0196, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-8j3g-f24p-4mpw](https://github.com/advisories/GHSA-8j3g-f24p-4mpw) | extends | Отправить при рукопожатии WebSocket непрерывный поток заголовков без завершения и проверить закрытие по лимиту |

### HTTP-URL-LENGTH-LIMIT — Очень длинный URL отклоняется контролируемо (RWB-0243, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-m875-3xf6-mf78](https://github.com/advisories/GHSA-m875-3xf6-mf78) | extends | Отправить URL максимальной допустимой длины и проверить, что сервер не отражает его в заголовках ответа без ограничения размера |

### INJ-FILTER-EXPRESSION — Выражения фильтрации (OData, RSQL, JSONPath, GraphQL where) не позволяют выйти за ограничения (RWB-0082, багов: 3)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-x485-rhg3-cqr4](https://github.com/advisories/GHSA-x485-rhg3-cqr4) | extends | Передать в ключе параметра поиска имя служебного метода (instance_eval, send) вместо имени поля или оператора |
| [GHSA-97vm-c39p-jr86](https://github.com/advisories/GHSA-97vm-c39p-jr86) | extends | _только пруф_: Тот же вариант, что у GHSA-x485-rhg3-cqr4 в этой партии |
| [GHSA-jm79-9pm4-vrw9](https://github.com/advisories/GHSA-jm79-9pm4-vrw9) | covered | _только пруф_: Выход выражения фильтрации за ограничения по полям связей |

### INJ-OS-COMMAND — Инъекция команд ОС не исполняется (RWB-0085, багов: 7)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-vp3w-52v9-q57f](https://github.com/advisories/GHSA-vp3w-52v9-q57f) | extends | Сохранить через API настройку с метасимволами оболочки и запустить операцию, которая использует эту настройку в командной строке |
| [GHSA-9fh3-j99m-f4v7](https://github.com/advisories/GHSA-9fh3-j99m-f4v7) | covered | _только пруф_: Инъекция команд ОС через параметр — ровно проверка записи |
| [GHSA-88cv-mj24-8w3q](https://github.com/advisories/GHSA-88cv-mj24-8w3q) | extends | Загрузить файл, в поле метаданных которого метасимволы оболочки, и вызвать операцию распаковки или перечисления содержимого |
| [GHSA-hfcp-477w-3wjw](https://github.com/advisories/GHSA-hfcp-477w-3wjw) | covered | _только пруф_: Классическая инъекция метасимволов оболочки в значение поля |
| [GHSA-6qjf-g333-pv38](https://github.com/advisories/GHSA-6qjf-g333-pv38) | extends | Подставить метасимволы оболочки в имя файла, который сервер обрабатывает фоновой задачей |
| [GHSA-qpqw-mc85-qvm9](https://github.com/advisories/GHSA-qpqw-mc85-qvm9) | covered | _только пруф_: Запись проверяет метасимволы оболочки в аргументах |
| [GHSA-4fvg-pwv7-v54g](https://github.com/advisories/GHSA-4fvg-pwv7-v54g) | extends | Загрузить файл, в имени которого метасимволы оболочки, на эндпоинт, обрабатывающий файл внешней утилитой |

### INJ-PATH-TRAVERSAL — Обход каталогов через параметры файлов и путей невозможен (RWB-0086, багов: 3)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-2xmw-f8j8-wfxc](https://github.com/advisories/GHSA-2xmw-f8j8-wfxc) | extends | Передать в параметре языка или локали значение с ../ и абсолютным путём и проверить, что применяется язык по умолчанию |
| [GHSA-44hj-4m45-frj3](https://github.com/advisories/GHSA-44hj-4m45-frj3) | extends | Отправить данные, поле которых подставляется в шаблон пути выходного файла, с ../ в этом поле |
| [GHSA-cp65-5m9r-vc2c](https://github.com/advisories/GHSA-cp65-5m9r-vc2c) | covered | _только пруф_: Классический обход каталогов через параметр файла |

### INJ-REDOS — Пользовательский ввод не вызывает катастрофический backtracking в regex (RWB-0088, багов: 30)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-mhwm-jh88-3gjf](https://github.com/advisories/GHSA-mhwm-jh88-3gjf) | extends | Отправить в поле, которое сервер экранирует как HTML, длинный повтор незакрытых тегов '<A ' |
| [GHSA-c4rq-3m3g-8wgx](https://github.com/advisories/GHSA-c4rq-3m3g-8wgx) | extends | Передать в параметр, который используется как CSS-селектор, незакрытую строку в кавычках и длинную цепочку hex-экранирований |
| [GHSA-h27x-rffw-24p4](https://github.com/advisories/GHSA-h27x-rffw-24p4) | extends | Отправить URI с длинной цепочкой разделителей под маршрут, заданный URI-шаблоном с explode-модификатором |
| [GHSA-cg4j-q9v8-6v38](https://github.com/advisories/GHSA-cg4j-q9v8-6v38) | extends | Отправить в числовое поле, которое сервер выводит с разделителями разрядов, строку из десятков тысяч цифр |
| [GHSA-mr3q-g2mv-mr4q](https://github.com/advisories/GHSA-mr3q-g2mv-mr4q) | extends | Отправить длинное патологическое значение в If-Match и If-None-Match к ресурсу, который отдаёт ETag |
| [GHSA-47m2-26rw-j2jw](https://github.com/advisories/GHSA-47m2-26rw-j2jw) | extends | Отправить multipart-часть с длинным патологическим заголовком Content-Disposition |
| [GHSA-2rxp-v6pw-ch6m](https://github.com/advisories/GHSA-2rxp-v6pw-ch6m) | extends | Отправить XML с числовой ссылкой на символ (&#…x…;) из тысяч цифр |
| [GHSA-h47h-mwp9-c6q6](https://github.com/advisories/GHSA-h47h-mwp9-c6q6) | covered | _только пруф_: Детали нагрузки в баге нет — общая проверка записи |
| [GHSA-wwhv-wxv9-rpgw](https://github.com/advisories/GHSA-wwhv-wxv9-rpgw) | covered | _только пруф_: Разбор разметки пользователя уже есть в шагах записи |
| [GHSA-vfg9-r3fq-jvx4](https://github.com/advisories/GHSA-vfg9-r3fq-jvx4) | extends | Отправить длинное патологическое значение в заголовке Authorization (схема Token) к защищённому эндпоинту |
| [GHSA-x76w-6vjr-8xgj](https://github.com/advisories/GHSA-x76w-6vjr-8xgj) | extends | Отправить параметры с длинными патологическими именами, которые сервер фильтрует перед записью в лог |
| [GHSA-cj83-2ww7-mvq7](https://github.com/advisories/GHSA-cj83-2ww7-mvq7) | extends | Отправить длинные патологические значения в Accept-Encoding и Accept-Language |
| [GHSA-22f2-v57c-j9cx](https://github.com/advisories/GHSA-22f2-v57c-j9cx) | covered | _только пруф_: Заголовок Content-Type уже есть в шагах записи |
| [GHSA-54rr-7fvw-6x8f](https://github.com/advisories/GHSA-54rr-7fvw-6x8f) | extends | Отправить длинное патологическое значение в заголовке Forwarded |
| [GHSA-jjhx-jhvp-74wq](https://github.com/advisories/GHSA-jjhx-jhvp-74wq) | extends | _только пруф_: Заголовки согласования Accept-* — вариант у GHSA-cj83-2ww7-mvq7 этой партии |
| [GHSA-hww2-5g85-429m](https://github.com/advisories/GHSA-hww2-5g85-429m) | covered | _только пруф_: Уязвимые паттерны url уже в шагах записи |
| [GHSA-qcm3-vfq5-wfr2](https://github.com/advisories/GHSA-qcm3-vfq5-wfr2) | covered | _только пруф_: Рендеринг разметки пользователя уже в шагах записи |
| [GHSA-fg7x-g82r-94qc](https://github.com/advisories/GHSA-fg7x-g82r-94qc) | covered | _только пруф_: Поля даты/времени уже в шагах записи |
| [GHSA-hv5j-3h9f-99c2](https://github.com/advisories/GHSA-hv5j-3h9f-99c2) | covered | _только пруф_: Уязвимые паттерны url уже в шагах записи |
| [GHSA-93pm-5p5f-3ghx](https://github.com/advisories/GHSA-93pm-5p5f-3ghx) | extends | _только пруф_: Тот же вариант, что у GHSA-47m2-26rw-j2jw в этой партии |
| [GHSA-p84v-45xj-wwqj](https://github.com/advisories/GHSA-p84v-45xj-wwqj) | extends | Отправить запрос с cookie и длинным патологическим X-Forwarded-Host |
| [GHSA-j6gc-792m-qgm2](https://github.com/advisories/GHSA-j6gc-792m-qgm2) | covered | _только пруф_: Механизм входа не описан — общая проверка записи |
| [GHSA-8xww-x3g3-6jcv](https://github.com/advisories/GHSA-8xww-x3g3-6jcv) | extends | Отправить длинный специально построенный заголовок If-None-Match и замерить время ответа |
| [GHSA-65f5-mfpf-vfhj](https://github.com/advisories/GHSA-65f5-mfpf-vfhj) | extends | Отправить на эндпоинт скачивания длинный специально построенный заголовок Range и замерить время ответа |
| [GHSA-rqv2-275x-2jq5](https://github.com/advisories/GHSA-rqv2-275x-2jq5) | extends | Отправить multipart с длинными атрибутами Content-Disposition частей, содержащими управляющие символы, и замерить время ответа |
| [GHSA-23c2-gwp5-pxw9](https://github.com/advisories/GHSA-23c2-gwp5-pxw9) | extends | Передать в параметр с глобальным идентификатором объекта (gid://app/Model/id) длинное специально построенное имя модели |
| [GHSA-vm74-j4wq-82xj](https://github.com/advisories/GHSA-vm74-j4wq-82xj) | extends | _только пруф_: Вариант с преобразованием HTML в текст уже есть у бага прошлой пачки источника |
| [GHSA-5x79-w82f-gw8w](https://github.com/advisories/GHSA-5x79-w82f-gw8w) | extends | Отправить в поле с санитизируемым HTML SVG-элемент с длинным специально построенным значением атрибута |
| [GHSA-486f-hjj9-9vhh](https://github.com/advisories/GHSA-486f-hjj9-9vhh) | extends | _только пруф_: Тот же вариант, что у GHSA-5x79-w82f-gw8w этой пачки |
| [GHSA-hxqx-xwvh-44m2](https://github.com/advisories/GHSA-hxqx-xwvh-44m2) | extends | _только пруф_: Вариант с multipart уже есть у GHSA-rqv2-275x-2jq5 этой пачки |

### INJ-SQL — SQL-инъекция во входных параметрах не исполняется (RWB-0089, багов: 9)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-jvqq-cvh4-xm37](https://github.com/advisories/GHSA-jvqq-cvh4-xm37) | extends | Передать SQL-полезную нагрузку в поисковом термине, который используется в сортировке по похожести, и сравнить время ответа |
| [GHSA-v529-vhwc-wfc5](https://github.com/advisories/GHSA-v529-vhwc-wfc5) | covered | _только пруф_: SQL-инъекция в параметре — ровно проверка записи |
| [GHSA-fwj4-6wgp-mpxm](https://github.com/advisories/GHSA-fwj4-6wgp-mpxm) | covered | _только пруф_: Инъекция в имени поля сортировки уже есть в шагах записи |
| [GHSA-5qw5-wf2q-f538](https://github.com/advisories/GHSA-5qw5-wf2q-f538) | covered | _только пруф_: Механизм входа не описан — запись проверяет описанное следствие |
| [GHSA-cxwf-qc32-375f](https://github.com/advisories/GHSA-cxwf-qc32-375f) | covered | _только пруф_: Обычная инъекция в значение параметра |
| [GHSA-hq7p-j377-6v63](https://github.com/advisories/GHSA-hq7p-j377-6v63) | extends | Передать в значение, которое попадает в комментарий SQL-запроса (аннотации, теги журналирования запросов), последовательность */ с SQL после неё |
| [GHSA-85gf-wr67-f83w](https://github.com/advisories/GHSA-85gf-wr67-f83w) | covered | _только пруф_: Механизм не описан; запись проверяет SQL-нагрузки во всех параметрах |
| [GHSA-33wh-w4m7-c6r8](https://github.com/advisories/GHSA-33wh-w4m7-c6r8) | covered | _только пруф_: Механизм — конкатенация SQL; запись проверяет нагрузки в body |
| [GHSA-9ggp-5rf4-x7q9](https://github.com/advisories/GHSA-9ggp-5rf4-x7q9) | covered | _только пруф_: Механизм не описан; запись покрывает нагрузки в параметрах |

### INJ-SSRF-PARAMETERS — Параметры с URL и хостами не дают доступа к внутренней сети (RWB-0090, багов: 5)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-33mh-2634-fwr2](https://github.com/advisories/GHSA-33mh-2634-fwr2) | extends | Передать в параметре, который сервер подставляет в путь исходящего запроса, протокол-относительный адрес //host/path |
| [GHSA-9pmc-p236-855h](https://github.com/advisories/GHSA-9pmc-p236-855h) | extends | Отправить содержимое с директивой импорта (@import url(...)) на внутренний адрес и на внешний адрес с редиректом на file:// |
| [GHSA-72f5-rr8c-r6gr](https://github.com/advisories/GHSA-72f5-rr8c-r6gr) | extends | Отправить данные, поле которых подставляется в шаблон адреса исходящей доставки, с внутренним хостом в этом поле |
| [GHSA-5rv5-xj5j-3484](https://github.com/advisories/GHSA-5rv5-xj5j-3484) | extends | _только пруф_: Тот же вариант, что GHSA-33mh-2634-fwr2 в этой партии |
| [GHSA-hm5p-x4rq-38w4](https://github.com/advisories/GHSA-hm5p-x4rq-38w4) | extends | Передать абсолютный URL в поле-идентификаторе, которое сервер подставляет в путь запроса к внешнему API, и проверить, что запрос с серверными заголовками не уходит на чужой хост |

### INJ-STORED-XSS — Сохранённые данные с HTML/JS не создают XSS у потребителей API (RWB-0244, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-533c-2vh9-4r86](https://github.com/advisories/GHSA-533c-2vh9-4r86) | extends | Сохранить от имени администратора HTML-блок с script и обработчиками событий и проверить, что на публичной странице они удалены |

### INJ-TEMPLATE-SSTI — Инъекция в серверные шаблоны не исполняется (RWB-0091, багов: 2)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-jjq7-m736-w977](https://github.com/advisories/GHSA-jjq7-m736-w977) | extends | Загрузить под учёткой без роли администратора файл конфигурации с шаблонным выражением в каталог, откуда сервер читает определения, и вызвать операцию, которая его читает |
| [GHSA-x487-866m-p8hr](https://github.com/advisories/GHSA-x487-866m-p8hr) | covered | _только пруф_: Инъекция шаблона в параметр |

### OBS-HEALTH-ENDPOINTS — Health-эндпоинты отражают состояние и не раскрывают детали (RWB-0093, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-pr7j-96cj-549h](https://github.com/advisories/GHSA-pr7j-96cj-549h) | extends | Запросить эндпоинты мониторинга компонентов и проверить, что в ответе нет паролей, токенов и ключей из их конфигурации |

### OBS-TRACE-PROPAGATION — Контекст трассировки принимается и передаётся дальше (RWB-0245, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-p5f6-rccc-jv98](https://github.com/advisories/GHSA-p5f6-rccc-jv98) | extends | Отправить заголовок baggage с десятками тысяч пар и огромным значением и проверить, что время ответа не растёт |

### REST-NUMERIC-BOUNDARIES — Числовые границы (RWB-0123, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-579w-22j4-4749](https://github.com/advisories/GHSA-579w-22j4-4749) | extends | Передать в числовой параметр фильтра или идентификатор значение больше 2^63-1 и дробное число, сравнить время ответа с обычным значением |

### REST-OBJECT-LEVEL-AUTHZ — Object-level authorization (RWB-0124, багов: 2)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-4825-p4xm-pcf2](https://github.com/advisories/GHSA-4825-p4xm-pcf2) | extends | Вызвать операцию привязки гостевого ресурса к своей учётке по чужому идентификатору без токена гостевого ресурса |
| [GHSA-c43c-rf7g-5xpg](https://github.com/advisories/GHSA-c43c-rf7g-5xpg) | covered | _только пруф_: Доступ к объекту вне разрешённых — ровно проверка записи |

### REST-OPEN-REDIRECT — Валидация redirect URL (RWB-0125, багов: 4)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-5jch-xhw4-r43v](https://github.com/advisories/GHSA-5jch-xhw4-r43v) | extends | Передать в адресе возврата после входа протокол-относительный URL //host/path |
| [GHSA-7pwc-wh6m-44q3](https://github.com/advisories/GHSA-7pwc-wh6m-44q3) | extends | Передать адрес возврата с CR/LF и @ перед чужим хостом и пустой адрес возврата |
| [GHSA-jp94-3292-c3xv](https://github.com/advisories/GHSA-jp94-3292-c3xv) | extends | Отправить не-GET запрос с истёкшей сессией и чужим Referer и проверить Location |
| [GHSA-9445-4cr6-336r](https://github.com/advisories/GHSA-9445-4cr6-336r) | covered | _только пруф_: Форма URL обхода в баге не описана |

### REST-REQUEST-SIZE-LIMIT — Лимит размера тела (RWB-0130, багов: 5)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-h669-8m4g-r2hc](https://github.com/advisories/GHSA-h669-8m4g-r2hc) | covered | _только пруф_: Лимит размера тела — ровно проверка записи |
| [GHSA-2jc5-xhx8-qj6h](https://github.com/advisories/GHSA-2jc5-xhx8-qj6h) | extends | Отправить тело с Content-Encoding: gzip, которое после распаковки превышает лимит в сотни раз |
| [GHSA-6xw4-3v39-52mm](https://github.com/advisories/GHSA-6xw4-3v39-52mm) | extends | Отправить тело application/x-www-form-urlencoded больше лимита и проверить отказ до чтения тела целиком |
| [GHSA-w9pc-fmgc-vxvw](https://github.com/advisories/GHSA-w9pc-fmgc-vxvw) | extends | Отправить multipart с одним текстовым полем (без filename) размером в сотни мегабайт |
| [GHSA-rrqh-93c8-j966](https://github.com/advisories/GHSA-rrqh-93c8-j966) | extends | Отправить сообщение больше лимита на эндпоинт с проверкой формата и убедиться по времени ответа, что лимит проверяется до разбора |

### REST-SENSITIVE-CACHE-CONTROL — Кэширование чувствительных ответов (RWB-0246, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-8h22-8cf7-hq6g](https://github.com/advisories/GHSA-8h22-8cf7-hq6g) | extends | Запросить публично кэшируемый ресурс (файл) с cookie сессии и проверить, что ответ с Cache-Control: public не содержит Set-Cookie |

### REST-SSRF-URL-FETCH — Контроль server-side URL fetch (RWB-0135, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-vx6p-q4gj-x6xx](https://github.com/advisories/GHSA-vx6p-q4gj-x6xx) | covered | _только пруф_: Запись проверяет server-side fetch по URL на внутренние адреса |

### SEC-AUTHZ-FUNCTION — User without required permission cannot invoke operation (RWB-0146, багов: 4)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-vq6j-hj8w-7v39](https://github.com/advisories/GHSA-vq6j-hj8w-7v39) | covered | _только пруф_: Пользователь без права вызывает операцию — ровно проверка записи |
| [GHSA-pqpw-cvm4-8mv9](https://github.com/advisories/GHSA-pqpw-cvm4-8mv9) | extends | Загрузить вложение в запись через отдельный эндпоинт вложений, когда политики запрещают изменение записи и загрузку в это поле |
| [GHSA-8fq9-273g-6mrg](https://github.com/advisories/GHSA-8fq9-273g-6mrg) | extends | Отправить напрямую изменяющий запрос, право на который проверяется только при открытии формы |
| [GHSA-639h-86hw-qcjq](https://github.com/advisories/GHSA-639h-86hw-qcjq) | covered | _только пруф_: Отсутствие проверки права на функцию |

### SEC-FAIL-CLOSED-INPUT — Неожиданный тип, пустое или отсутствующее поле проверки безопасности ведёт к отказу, а не к пропуску проверки (RWB-0006, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-33qg-7wpp-89cq](https://github.com/advisories/GHSA-33qg-7wpp-89cq) | extends | Отправить cookie сессии в незащищённом формате (без шифрования и подписи) и проверить, что она отклоняется |

### SEC-INTERNAL-CONTROL-PARAMS — Заголовки и параметры подключения клиента не задают внутренние управляющие параметры операции (RWB-0180, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-r657-rxjc-j557](https://github.com/advisories/GHSA-r657-rxjc-j557) | extends | Отправить на маршрут, отдаваемый через X-Sendfile/X-Accel-Redirect за прокси, заголовки X-Sendfile-Type и X-Accel-Mapping с подобранным отображением путей и проверить, что ответ и доступ к закрытым путям такие же, как без них |

### SEC-OWNERSHIP-DELETE — User cannot delete another owner’s resource (RWB-0149, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-9pm8-vwc5-w2hm](https://github.com/advisories/GHSA-9pm8-vwc5-w2hm) | covered | _только пруф_: Ровно проверка записи |

### SEC-OWNERSHIP-READ — User cannot read another owner’s resource (RWB-0150, багов: 2)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-p6pv-q7rc-g4h9](https://github.com/advisories/GHSA-p6pv-q7rc-g4h9) | extends | Запросить ресурс, созданный гостем, по его идентификатору без токена гостя и с токеном другого гостя |
| [GHSA-3ghg-3787-w2xr](https://github.com/advisories/GHSA-3ghg-3787-w2xr) | extends | Анонимно запросить по ID объект, созданный другим анонимным пользователем, — пустой владелец не должен совпадать с пустым текущим пользователем |

### SEC-OWNERSHIP-REFERENCE-INDIRECT — Indirect resource references preserve authorization (RWB-0151, багов: 3)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-87fh-rc96-6fr6](https://github.com/advisories/GHSA-87fh-rc96-6fr6) | extends | Передать в обновлении ресурса ID чужого связанного объекта плоским полем (*_id) вместо вложенного объекта и проверить, что проверка владения одинакова для обеих форм |
| [GHSA-g268-72p7-9j6j](https://github.com/advisories/GHSA-g268-72p7-9j6j) | extends | _только пруф_: Тот же вариант, что у GHSA-87fh-rc96-6fr6 в этой партии |
| [GHSA-79m3-q3wh-c3qm](https://github.com/advisories/GHSA-79m3-q3wh-c3qm) | extends | Анонимно создать дочерний объект (комментарий) у ресурса в непубличном состоянии (черновик) и проверить отказ, как при его чтении |

### SEC-OWNERSHIP-UPDATE — User cannot modify another owner’s resource (RWB-0152, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-c273-c6vg-4pv5](https://github.com/advisories/GHSA-c273-c6vg-4pv5) | extends | Подменить идентификатор ресурса в параметре тела формы (article[id]) на ID чужого ресурса при изменении и удалении |

### SEC-ROLE-LOW-TO-HIGH — Low-privilege role cannot perform privileged action (RWB-0247, багов: 3)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-q79h-67vx-m9xg](https://github.com/advisories/GHSA-q79h-67vx-m9xg) | covered | _только пруф_: Роль ниже выполняет привилегированное действие — ровно проверка записи |
| [GHSA-v46j-h43h-rwrm](https://github.com/advisories/GHSA-v46j-h43h-rwrm) | covered | _только пруф_: Механизм не описан — запись проверяет описанное следствие |
| [GHSA-f68m-q26r-64f6](https://github.com/advisories/GHSA-f68m-q26r-64f6) | covered | _только пруф_: Запись проверяет привилегированные операции от низкой роли |

### SEC-ROLE-MASS-ASSIGN — Mass assignment cannot elevate privileges (RWB-0248, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-rp28-mvq3-wf8j](https://github.com/advisories/GHSA-rp28-mvq3-wf8j) | covered | _только пруф_: Повышение привилегий через mass assignment — ровно проверка записи |

### SEC-TENANT-WRITE — Tenant A cannot mutate tenant B data (RWB-0159, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-86fh-w43w-338c](https://github.com/advisories/GHSA-86fh-w43w-338c) | covered | _только пруф_: Изменение данных другого арендатора по ID — ровно проверка записи |

### SEC-TOKEN-AUDIENCE — Token for another audience is rejected (RWB-0160, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-r3v7-5x4c-c69q](https://github.com/advisories/GHSA-r3v7-5x4c-c69q) | extends | Отправить токен, выданный на хосте одного арендатора, на хост другого арендатора того же сервиса |

### SEC-TOKEN-SIGNATURE — Token with invalid signature is rejected (RWB-0204, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-c32j-vqhx-rx3x](https://github.com/advisories/GHSA-c32j-vqhx-rx3x) | extends | Подписать токен HMAC пустым ключом, указав kid несуществующего ключа, и отправить его |

### SEC-VERTICAL-ESCALATION — Lower role cannot invoke higher-role route via alternate method (RWB-0249, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-qc5p-3mg5-9fh8](https://github.com/advisories/GHSA-qc5p-3mg5-9fh8) | extends | Вызвать через эндпоинт действий одного ресурса действие другого ресурса, указав его имя в параметре |

### VAL-DEEP-NESTING — Чрезмерно вложенный JSON отклоняется без деградации сервиса (RWB-0165, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-735f-pc8j-v9w8](https://github.com/advisories/GHSA-735f-pc8j-v9w8) | extends | Отправить protobuf-сообщение с неизвестным полем из тысяч вложенных групп |

### VAL-NUMBER-REPRESENTATION — Альтернативные записи чисел обрабатываются по контракту (RWB-0250, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-2j26-frm8-cmj9](https://github.com/advisories/GHSA-2j26-frm8-cmj9) | extends | Передать в числовое поле, которое сервер форматирует, значение 1e10000 и проверить время и размер ответа |

### WS-MESSAGE-LIMITS — Размер и частота сообщений ограничены (RWB-0205, багов: 2)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-33ph-fccm-39pj](https://github.com/advisories/GHSA-33ph-fccm-39pj) | extends | Отправить сообщение permessage-deflate, которое меньше лимита в сжатом виде и больше — после распаковки |
| [GHSA-ghhp-3qvg-889p](https://github.com/advisories/GHSA-ghhp-3qvg-889p) | extends | Отправить кадр с бесконечным полем длины (байты ≥0x80) и проверить закрытие соединения |

