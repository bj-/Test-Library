# Кандидаты из баг-трекеров: партия `ghsa-composer`

Сгенерировано `tools/mining/cluster.py` из `build/mining/<batch>/batches/*.out.jsonl` и
`ideas/mined/ghsa-composer.review.yaml` — правки решений делаются в review-файле, затем пересборка.
План — `docs/BUG_MINING_PLAN.md`, шаги 6–7; применение — `tools/mining/apply_proofs.py`.

## Сводка

- Новых паттернов: 7 → идей: 4 (принять: 4, отклонить: 0, не решено: 0).
- Пруфы к существующим: 179 багов → 54 записей; новых шагов-вариантов: 115.

## Новые идеи

Принятые становятся записями `status: draft` с меткой `real-world-bug` и ссылкой на RWB.

| # | Решение | Запись / файл | Идея | Подтверждающие баги |
|---|---|---|---|---|
| 1 | accept | `INJ-SCHEMA-IDENTIFIER-CODEGEN` (RWB-0302)<br>`checks/security/injection.yaml` | Идентификаторы из пользовательского определения схемы (имена полей, таблиц, индексов), по которым сервер генерирует исходный код или DDL, не внедряют код и SQL — символы, закрывающие объявление (;, кавычки, скобки, комментарии), отклоняются 4xx или экранируются по правилам целевого языка; пара к RES-DB-OBJECT-NAMES (законные имена со спецсимволами работают) | [GHSA-9x44-4gxf-8c25](https://github.com/advisories/GHSA-9x44-4gxf-8c25) |
| 2 | accept | `INJ-USER-DATA-CALLABLE` (RWB-0303)<br>`checks/security/injection.yaml` | Данные пользователя (поле формы, настройки, фронтматтер страницы), которые называют серверную функцию — источник данных, обработчик, callback, — не позволяют вызвать функцию вне allowlist в любой форме записи (строка, Класс::метод, массив класс-метод, вложенный callable) и с любыми аргументами; denylist опасных функций недостаточен | [GHSA-r94f-hx44-8jqf](https://github.com/advisories/GHSA-r94f-hx44-8jqf), [GHSA-f8wv-xp27-6gq7](https://github.com/advisories/GHSA-f8wv-xp27-6gq7), [GHSA-7pgq-cr25-xvc8](https://github.com/advisories/GHSA-7pgq-cr25-xvc8), [GHSA-fj2p-qj2f-74v5](https://github.com/advisories/GHSA-fj2p-qj2f-74v5) |
| 3 | accept | `HARD-OUTBOUND-CREDENTIALS-SCOPE` (RWB-0304)<br>`checks/security/api-hardening.yaml` | Учётные данные, настроенные сервером для своего сайта или интеграции (Authorization, Cookie, ключи), не уходят в исходящие запросы к другим хостам — при обходе ссылок, проверке битых ссылок, следовании редиректам, загрузке по URL | [GHSA-3mr9-p497-58f6](https://github.com/advisories/GHSA-3mr9-p497-58f6) |
| 4 | accept | `AUTH-EXTERNAL-ID-EXACT-MATCH` (RWB-0305)<br>`checks/security/authentication-session.yaml` | Внешний идентификатор субъекта (OIDC sub; SAML NameID и ID провайдера — если их семантика требует точного совпадения) сравнивается побайтно в паре «издатель + subject» — без нормализации регистра, диакритики и Unicode collation БД; subject, отличающийся от чужого только регистром или акцентом, даёт новую учётку или отказ, но не вход в чужую; пара к AUTH-LOGIN-IDENTIFIER-NORMALIZATION (там нормализация нужна) | [GHSA-cmwh-g2h8-c222](https://github.com/advisories/GHSA-cmwh-g2h8-c222) |

## Пруфы к существующим

Запись получает метку `real-world-bug` и `Real-world bug: RWB-NNNN`; статус не меняется. Для `extends`
текст варианта добавляется шагом (`steps[].action`, в `notes` — RWB). Неверное совпадение — ID бага в
`proofs.exclude`, вариант без нового шага — в `proofs.no_variant`.

### AUTH-CSRF — Изменяющие операции с cookie-аутентификацией защищены от CSRF (RWB-0190, багов: 9)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-9ff2-p842-45wq](https://github.com/advisories/GHSA-9ff2-p842-45wq) | extends | Выполнить изменяющее действие GET-запросом (действие выбрано параметром запроса) без CSRF-токена |
| [GHSA-m8r3-22v6-g877](https://github.com/advisories/GHSA-m8r3-22v6-g877) | extends | _только пруф_: Тот же вариант, что у GHSA-9ff2-p842-45wq: изменяющее действие по GET без токена |
| [GHSA-9hjf-w35w-6vx2](https://github.com/advisories/GHSA-9hjf-w35w-6vx2) | covered | _только пруф_: Изменяющий запрос без CSRF-токена с чужого Origin — ровно запись |
| [GHSA-68jx-f42c-7599](https://github.com/advisories/GHSA-68jx-f42c-7599) | extends | Вызвать бэкенд-маршрут с сессией администратора и Referer страницы фронтенда того же домена |
| [GHSA-p2ch-c2c3-4xm5](https://github.com/advisories/GHSA-p2ch-c2c3-4xm5) | extends | Вызвать изменяющий обработчик GET-запросом по URL без CSRF-токена и проверить, что изменение не выполнено |
| [GHSA-xpr4-8vp6-c87j](https://github.com/advisories/GHSA-xpr4-8vp6-c87j) | extends | Отправить изменяющий запрос без CSRF-токена на каждую отдельную точку входа (AJAX-эндпоинт) |
| [GHSA-r8vr-m544-qh4h](https://github.com/advisories/GHSA-r8vr-m544-qh4h) | extends | _только пруф_: CSRF через изменяющий GET; вариант уже у другого бага партии |
| [GHSA-pgcc-vfmc-7cw5](https://github.com/advisories/GHSA-pgcc-vfmc-7cw5) | extends | Выполнить с cookie сессии кросс-сайтовую GET-навигацию на маршрут, изменяющий данные или права, и проверить, что состояние не изменилось |
| [GHSA-hm42-q32m-vj4f](https://github.com/advisories/GHSA-hm42-q32m-vj4f) | extends | _только пруф_: Тот же вариант, что GHSA-pgcc-vfmc-7cw5 в партии: изменение через GET с Lax-cookie |

### AUTH-EXTERNAL-IDP-UNVERIFIED-EMAIL — Вход через внешний IdP не связывается с учёткой по неподтверждённому email (RWB-0041, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-93qh-5269-9wcf](https://github.com/advisories/GHSA-93qh-5269-9wcf) | covered | _только пруф_: Ровно сценарий записи |

### AUTH-MFA-STEP-UP — Операции, требующие второго фактора, недоступны без него (RWB-0060, багов: 4)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-7m6h-rg42-m449](https://github.com/advisories/GHSA-7m6h-rg42-m449) | extends | Подключить и отключить второй фактор, перевыпустить коды восстановления в существующей сессии без текущего пароля, передав только код фактора или код восстановления |
| [GHSA-7mgc-c7pq-3rr3](https://github.com/advisories/GHSA-7mgc-c7pq-3rr3) | covered | _только пруф_: Вызов чувствительной операции после первого фактора уже есть в записи |
| [GHSA-9fw9-8c49-qch8](https://github.com/advisories/GHSA-9fw9-8c49-qch8) | extends | Изменить email для входа в профиле без текущего пароля |
| [GHSA-v8hx-4vx8-wc96](https://github.com/advisories/GHSA-v8hx-4vx8-wc96) | extends | Использовать cookie сессии, выданную после пароля до ввода второго фактора, для запросов к API |

### AUTH-OTP-SEND-LIMIT — Частота отправки кодов ограничена (SMS bombing) (RWB-0306, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-mfxh-vp55-7gc6](https://github.com/advisories/GHSA-mfxh-vp55-7gc6) | extends | Многократно отправить POST на форму регистрации для адреса с неподтверждённой регистрацией без капчи и признака отправки формы; проверить лимит писем активации и одинаковость ответа с адресом без регистрации |

### AUTH-PASSWORD-RESET-TOKEN — Токен сброса пароля одноразовый, ограничен по времени и привязан к пользователю (RWB-0307, багов: 2)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-h854-c3m3-mh5v](https://github.com/advisories/GHSA-h854-c3m3-mh5v) | extends | Отправить запрос сброса пароля с параметром URL ссылки на чужой домен и проверить, что письмо ведёт только на настроенный домен, а вход по токену требует второй фактор |
| [GHSA-m492-gv72-xvxj](https://github.com/advisories/GHSA-m492-gv72-xvxj) | covered | _только пруф_: Одноразовость и отзыв токена сброса — сценарий записи |

### AUTH-TOKEN-IN-URL — Учётные данные не передаются и не принимаются в URL (RWB-0308, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-ffq7-hh2j-r24p](https://github.com/advisories/GHSA-ffq7-hh2j-r24p) | covered | _только пруф_: Токен в URL — ровно эта проверка |

### AUTH-USER-ENUMERATION — Ответы входа, регистрации и восстановления не раскрывают существование аккаунта (RWB-0193, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-225x-3jhx-wh4q](https://github.com/advisories/GHSA-225x-3jhx-wh4q) | extends | Вызвать служебный эндпоинт проверки существования email (мастер создания пользователя) от роли без права просмотра пользователей с существующим и несуществующим email |

### BIZ-WORKFLOW-STEP-SKIP — Нельзя пропустить обязательный шаг бизнес-процесса (RWB-0066, багов: 2)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-8gpw-xvpf-hvx5](https://github.com/advisories/GHSA-8gpw-xvpf-hvx5) | extends | Вызвать шаг проверки второго фактора без предшествующего входа по паролю, указав в запросе ID другого пользователя |
| [GHSA-c67f-gmxw-mj93](https://github.com/advisories/GHSA-c67f-gmxw-mj93) | extends | Отправить запрос шага второго фактора (логин и код TOTP) без предварительного успешного ввода пароля в этой сессии |

### FILE-ARCHIVE-BOMB — Архивные и графические бомбы не исчерпывают ресурсы (RWB-0069, багов: 5)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-m9xh-6747-9r6f](https://github.com/advisories/GHSA-m9xh-6747-9r6f) | extends | Загрузить SVG с глубоко вложенными элементами <use>, где атрибут ссылки записан в смешанном регистре (xlink:HrEf), и проверить скачанный результат |
| [GHSA-2mrg-gjxq-2gvr](https://github.com/advisories/GHSA-2mrg-gjxq-2gvr) | covered | _только пруф_: Декомпрессионная бомба — ровно эта проверка |
| [GHSA-f5gf-2cj8-52g2](https://github.com/advisories/GHSA-f5gf-2cj8-52g2) | extends | Встроить в рендеримый HTML base64-изображение огромных размеров со случайным шумом |
| [GHSA-8hg6-c449-896m](https://github.com/advisories/GHSA-8hg6-c449-896m) | extends | Встроить BMP с крошечным телом и огромными размерами в заголовке |
| [GHSA-xg43-5579-qw6v](https://github.com/advisories/GHSA-xg43-5579-qw6v) | covered | _только пруф_: Декомпрессионная бомба — ровно эта проверка |

### FILE-DOWNLOAD-AUTHZ — Скачивание файлов проверяет права и срок действия ссылок (RWB-0070, багов: 2)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-3hgv-jr5j-cg9x](https://github.com/advisories/GHSA-3hgv-jr5j-cg9x) | extends | Скачать чужой файл по имени через альтернативный маршрут (профиль пользователя), когда основной маршрут отвечает 403 |
| [GHSA-x76w-8c62-48mg](https://github.com/advisories/GHSA-x76w-8c62-48mg) | extends | Запросить превью или миниатюру приватного файла пользователем без права просмотра; ответ не содержит подписанной ссылки |

### FILE-MALFORMED-STRUCTURE — Повреждённый файл при разборе метаданных даёт 4xx, а не падение процесса (RWB-0031, багов: 2)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-v383-3rw5-q8rf](https://github.com/advisories/GHSA-v383-3rw5-q8rf) | extends | Загрузить SVG с DOCTYPE, объявляющим #FIXED-значение атрибута по умолчанию, и проверить живость сервиса |
| [GHSA-xh5m-36r6-47m3](https://github.com/advisories/GHSA-xh5m-36r6-47m3) | extends | Загрузить табличный файл с зацикленной цепочкой секторов (OLE) и проверить, что разбор завершается ошибкой без роста памяти |

### FILE-TRANSFORM-LIMITS — Лимит трансформации файла пропускает допустимые комбинации и отклоняет превышение (RWB-0012, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-4x9g-vw65-vvf9](https://github.com/advisories/GHSA-4x9g-vw65-vvf9) | covered | _только пруф_: Лимит трансформации файла — ровно эта проверка |

### HARD-EXCESSIVE-DATA-EXPOSURE — Ответы не содержат внутренних полей сверх контракта (RWB-0076, багов: 2)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-xgr6-pqjv-3pf8](https://github.com/advisories/GHSA-xgr6-pqjv-3pf8) | extends | Открыть без аутентификации страницу по ссылке-хэшу и проверить, что встроенные данные связанного объекта ограничены нужными полями |
| [GHSA-4vmm-5qvc-w5p7](https://github.com/advisories/GHSA-4vmm-5qvc-w5p7) | extends | Проверить, что поиск связанных объектов не возвращает секретные хэши-ссылки чужих объектов, и попытаться использовать их для изменения |

### HARD-EXPENSIVE-OPERATION-LIMITS — Дорогие операции ограничены по ресурсам (RWB-0077, багов: 3)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-3q6v-r5mr-hxv8](https://github.com/advisories/GHSA-3q6v-r5mr-hxv8) | covered | _только пруф_: Алгоритмическая сложность парсеров ввода на плоском большом входе уже есть в записи |
| [GHSA-f6v3-2qmr-vfjx](https://github.com/advisories/GHSA-f6v3-2qmr-vfjx) | extends | Отправить MIME-письмо с глубокой вложенностью multipart, тысячами соседних частей и мегабайтами строк заголовков; замерить время и память |
| [GHSA-5cjr-mxj5-wmrx](https://github.com/advisories/GHSA-5cjr-mxj5-wmrx) | extends | Отправить подписанное XML-сообщение (SAML) с XPath-преобразованиями и большим числом элементов Transform |

### HARD-HOST-HEADER — Подмена Host и X-Forwarded-Host не влияет на ссылки и маршрутизацию (RWB-0078, багов: 2)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-3735-5339-xfwx](https://github.com/advisories/GHSA-3735-5339-xfwx) | extends | Подменить Host при старте OIDC- и SAML-входа и при выходе; проверить redirect_uri, адреса ACS/SLO и редирект после выхода |
| [GHSA-4chg-4752-w88r](https://github.com/advisories/GHSA-4chg-4752-w88r) | extends | Отправить запрос с X-Forwarded-Host на контролируемый внешний хост и проверить, что сервер не обращается к этому хосту |

### INJ-FILTER-EXPRESSION — Выражения фильтрации (OData, RSQL, JSONPath, GraphQL where) не позволяют выйти за ограничения (RWB-0082, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-pcw8-m77r-2528](https://github.com/advisories/GHSA-pcw8-m77r-2528) | extends | Передать в выражении запроса (JMESPath) имя функции со спецсимволами и кодом и проверить отказ |

### INJ-OS-COMMAND — Инъекция команд ОС не исполняется (RWB-0085, багов: 5)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-mrc5-3mm3-45c5](https://github.com/advisories/GHSA-mrc5-3mm3-45c5) | extends | Отправить многократно запрос с метасимволами оболочки в заголовке Host (обработка может срабатывать выборочно) |
| [GHSA-jf24-8g2h-2wg7](https://github.com/advisories/GHSA-jf24-8g2h-2wg7) | extends | Задать в настройке пути к исполняемому файлу произвольную программу или скрипт и открыть страницу, которая её запускает |
| [GHSA-g3hq-hphg-8fhh](https://github.com/advisories/GHSA-g3hq-hphg-8fhh) | extends | Передать разрешённую команду с опциями, запускающими другие программы (find -exec, git -c), без метасимволов оболочки |
| [GHSA-wg4w-wr5q-6vjc](https://github.com/advisories/GHSA-wg4w-wr5q-6vjc) | covered | _только пруф_: Метасимволы оболочки — ровно эта проверка |
| [GHSA-9643-6xjp-vx57](https://github.com/advisories/GHSA-9643-6xjp-vx57) | covered | _только пруф_: Подстановка команд — ровно эта проверка |

### INJ-PATH-TRAVERSAL — Обход каталогов через параметры файлов и путей невозможен (RWB-0086, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-2223-f22x-24cq](https://github.com/advisories/GHSA-2223-f22x-24cq) | extends | Сохранить ресурс с директивой включения файла с ../ и запросить собранный результат |

### INJ-REDOS — Пользовательский ввод не вызывает катастрофический backtracking в regex (RWB-0088, багов: 4)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-37f3-6p89-6qr9](https://github.com/advisories/GHSA-37f3-6p89-6qr9) | covered | _только пруф_: Пользователь задаёт сам шаблон — уже есть в записи |
| [GHSA-j8pm-gj4c-rq4x](https://github.com/advisories/GHSA-j8pm-gj4c-rq4x) | covered | _только пруф_: Рендеринг Markdown пользователя с квадратичным разбором уже есть в записи |
| [GHSA-x7rj-f32v-7jjg](https://github.com/advisories/GHSA-x7rj-f32v-7jjg) | extends | Отправить запрос с путём из длинной серии слэшей, не совпадающим с маршрутом, и замерить время ответа |
| [GHSA-px5m-h76g-p7p8](https://github.com/advisories/GHSA-px5m-h76g-p7p8) | extends | Отправить в поле, проверяемое рекурсивным регулярным выражением, значение с тысячами вложенных скобок |

### INJ-SQL — SQL-инъекция во входных параметрах не исполняется (RWB-0089, багов: 16)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-vjqc-q4mp-2rvf](https://github.com/advisories/GHSA-vjqc-q4mp-2rvf) | extends | Передать SQL-фрагмент в параметр, который подставляется в запрос как ключевое слово: тип приведения, часть даты, единица интервала |
| [GHSA-79cw-hfcc-7mw9](https://github.com/advisories/GHSA-79cw-hfcc-7mw9) | covered | _только пруф_: Инъекция в имена полей фильтра уже есть в записи |
| [GHSA-rw77-vq4g-x3hp](https://github.com/advisories/GHSA-rw77-vq4g-x3hp) | covered | _только пруф_: Базовая инъекция в значение тела запроса |
| [GHSA-jg26-q8hg-3pq4](https://github.com/advisories/GHSA-jg26-q8hg-3pq4) | covered | _только пруф_: Инъекция в query-параметр с boolean-нагрузками; диалект запроса не меняет проверку |
| [GHSA-23rh-xw42-fq82](https://github.com/advisories/GHSA-23rh-xw42-fq82) | extends | Передать в поля конфигурации, принимающие SQL-фрагменты, UNION SELECT, INTO OUTFILE, комментарии /*!*/ и стековые запросы в обход чёрного списка ключевых слов, а в limit и offset — нечисловое значение |
| [GHSA-fxf7-vhh8-7vpq](https://github.com/advisories/GHSA-fxf7-vhh8-7vpq) | extends | Передать SQL-фрагмент в параметр пути внутри JSON-поля (jsonPath), по которому сервер фильтрует или выбирает данные |
| [GHSA-w27m-rmmf-g5w4](https://github.com/advisories/GHSA-w27m-rmmf-g5w4) | extends | Сохранить SQL-полезную нагрузку элементом массива в поле и вызвать операцию, которая использует сохранённое значение (инъекция второго порядка) |
| [GHSA-m7jc-g4rc-jmvh](https://github.com/advisories/GHSA-m7jc-g4rc-jmvh) | extends | Передать SQL в границах числового диапазона фильтра списка |
| [GHSA-c9w5-rwh3-7pm9](https://github.com/advisories/GHSA-c9w5-rwh3-7pm9) | extends | Передать SQL-полезную нагрузку в условие массового удаления и сравнить с одиночным удалением |
| [GHSA-mw6p-33vw-46cc](https://github.com/advisories/GHSA-mw6p-33vw-46cc) | extends | Сохранить SQL в параметре конфигурации, который подставляется в ORDER BY, и открыть страницу, которая его применяет |
| [GHSA-5qmh-x653-g8qj](https://github.com/advisories/GHSA-5qmh-x653-g8qj) | extends | Передать SQL в имени поля фильтра (ключе filter[...]) со скобками |
| [GHSA-4pf7-cc4r-g63h](https://github.com/advisories/GHSA-4pf7-cc4r-g63h) | covered | _только пруф_: Запись уже подставляет нагрузки в path, query, body и заголовки |
| [GHSA-8f2v-2qhj-gfwg](https://github.com/advisories/GHSA-8f2v-2qhj-gfwg) | extends | Создать ресурс со значением-SQL-фрагментом в имени или идентификаторе, затем вызвать операции, использующие сохранённое значение (удаление, связи, отчёты) |
| [GHSA-qg78-vmvc-fhjw](https://github.com/advisories/GHSA-qg78-vmvc-fhjw) | extends | Передать в фильтре по числовому полю булево SQL-выражение без кавычек (1 OR 1=1, 1 AND 1=0) и сравнить выборки |
| [GHSA-89v6-j5x6-cmj3](https://github.com/advisories/GHSA-89v6-j5x6-cmj3) | extends | Передать SQL-нагрузку в аргументе макроса в сохраняемом контенте, если тот же параметр в query проверяется whitelist, и открыть страницу |
| [GHSA-fcmw-wx57-9p75](https://github.com/advisories/GHSA-fcmw-wx57-9p75) | extends | Передать SQL-нагрузку на втором и более глубоком уровне вложенного параметра фильтра (массив в массиве) |

### INJ-SSRF-PARAMETERS — Параметры с URL и хостами не дают доступа к внутренней сети (RWB-0090, багов: 2)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-v3f3-cmj4-cvj9](https://github.com/advisories/GHSA-v3f3-cmj4-cvj9) | covered | _только пруф_: Параметр базового URL сторонней интеграции с утечкой серверного токена уже есть в записи |
| [GHSA-vw42-752g-5mrp](https://github.com/advisories/GHSA-vw42-752g-5mrp) | extends | Отправить заголовок Signature с keyId на внутренний адрес (127.0.0.1, 169.254.169.254) и проверить, что сервер не обращается к нему |

### INJ-STORED-XSS — Сохранённые данные с HTML/JS не создают XSS у потребителей API (RWB-0244, багов: 2)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-97jj-33gv-5xf9](https://github.com/advisories/GHSA-97jj-33gv-5xf9) | extends | Сохранить Markdown, где запрещённый тег (<script, <iframe) стоит в конце строки, а атрибуты — в следующем блоке, и прочитать отрендеренный HTML |
| [GHSA-7gww-x7fh-jf9j](https://github.com/advisories/GHSA-7gww-x7fh-jf9j) | extends | Вернуть из подменённой внешней интеграции поля с HTML/JS и проверить, что страница отдаёт их экранированными |

### INJ-TEMPLATE-SSTI — Инъекция в серверные шаблоны не исполняется (RWB-0091, багов: 10)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-g8wr-r2v2-vqc6](https://github.com/advisories/GHSA-g8wr-r2v2-vqc6) | covered | _только пруф_: Сохранение выражений шаблона и генерация письма уже есть в записи |
| [GHSA-hrwp-4hh9-c8r8](https://github.com/advisories/GHSA-hrwp-4hh9-c8r8) | covered | _только пруф_: Инъекция в серверный шаблон с исполнением кода — ровно запись; конкретный фильтр — деталь движка |
| [GHSA-p597-crqc-m349](https://github.com/advisories/GHSA-p597-crqc-m349) | extends | Сохранить в контенте с включённой песочницей шаблонные выражения, читающие системную конфигурацию (пароли, ключи), и открыть страницу |
| [GHSA-xv9m-fm3w-8w5x](https://github.com/advisories/GHSA-xv9m-fm3w-8w5x) | extends | В режиме песочницы вызвать в шаблоне методы доступных объектов фреймворка: запись в сессию и сырой SQL через построитель запросов |
| [GHSA-mc5q-6hpj-rp7j](https://github.com/advisories/GHSA-mc5q-6hpj-rp7j) | extends | _только пруф_: Тот же вариант, что у GHSA-p597-crqc-m349: чтение секретов конфигурации из песочницы |
| [GHSA-jppw-r5j3-xf7x](https://github.com/advisories/GHSA-jppw-r5j3-xf7x) | extends | Вставить в поле с динамическим рендерингом ссылку на секретные поля текущего пользователя (коды восстановления 2FA) и проверить, что они не выводятся |
| [GHSA-8737-2x9g-xjj7](https://github.com/advisories/GHSA-8737-2x9g-xjj7) | extends | Загрузить файл шаблона, в атрибуте которого значение с $ и командой в обратных кавычках, и вызвать его отрисовку |
| [GHSA-f74w-488g-8x5r](https://github.com/advisories/GHSA-f74w-488g-8x5r) | extends | Отправить изменяющий запрос с заголовком Referer, содержащим выражение шаблонизатора ({{7*7}}), и проверить URL перенаправления |
| [GHSA-287w-mxq6-x2cp](https://github.com/advisories/GHSA-287w-mxq6-x2cp) | extends | Вставить в пользовательский шаблон (письма, документа) разрешённую функцию чтения файла с путём к .env и проверить результат |
| [GHSA-h8vq-8gpg-mhcg](https://github.com/advisories/GHSA-h8vq-8gpg-mhcg) | extends | Через разрешённый фильтр выборки столбца (column) прочитать в пользовательском шаблоне свойство, запрещённое политикой песочницы |

### INJ-UNSAFE-DESERIALIZATION — Небезопасная десериализация пользовательских данных невозможна (RWB-0198, багов: 3)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-265m-7826-wjqm](https://github.com/advisories/GHSA-265m-7826-wjqm) | extends | Спрятать служебные ключи конфигурации объекта во вложенной JSON-строке параметра и проверить, что они отброшены |
| [GHSA-9369-69wj-7m2f](https://github.com/advisories/GHSA-9369-69wj-7m2f) | covered | _только пруф_: Небезопасная десериализация пользовательских данных — ровно сценарий записи |
| [GHSA-86vw-x4ww-x467](https://github.com/advisories/GHSA-86vw-x4ww-x467) | extends | Передать в параметре-конфигурации, из которой создаётся объект, служебные ключи фреймворка (обработчики событий вида 'on init', class) и проверить, что они отбрасываются |

### PAGE-SEARCH-SPECIAL-CHARS — Поиск со спецсимволами и wildcard не ломается и не расширяет выборку (RWB-0094, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-6pvm-2vjj-rx4w](https://github.com/advisories/GHSA-6pvm-2vjj-rx4w) | covered | _только пруф_: Wildcard в поиске расширяет выборку — ровно эта проверка |

### REQ-CROSS-CLIENT-CONSISTENCY — Одно правило продукта одинаково в API разных клиентов (RWB-0099, багов: 3)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-6p96-cfg5-4vhp](https://github.com/advisories/GHSA-6p96-cfg5-4vhp) | covered | _только пруф_: Разные пути создания одного объекта с одинаковыми политиками уже есть в записи |
| [GHSA-w79m-f3jx-779v](https://github.com/advisories/GHSA-w79m-f3jx-779v) | covered | _только пруф_: Тот же механизм, что у GHSA-6p96-cfg5-4vhp: разные пути создания объекта с разной проверкой |
| [GHSA-rw46-qg69-vg6h](https://github.com/advisories/GHSA-rw46-qg69-vg6h) | covered | _только пруф_: Одно правило в разных интерфейсах — ровно эта проверка |

### RES-REFERENTIAL-INTEGRITY — Ссылка на несуществующий или чужой связанный ресурс отклоняется (RWB-0104, багов: 8)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-rc52-c4hv-w89p](https://github.com/advisories/GHSA-rc52-c4hv-w89p) | covered | _только пруф_: Вариант «обе ссылки существуют, но не связаны между собой» уже есть в записи |
| [GHSA-575r-357h-fhch](https://github.com/advisories/GHSA-575r-357h-fhch) | extends | Изменить через PATCH и PUT ссылку существующего объекта на связанный ресурс другой компании |
| [GHSA-8w8c-8mx9-52cw](https://github.com/advisories/GHSA-8w8c-8mx9-52cw) | extends | Создать через API дочерний объект иерархии с родителем из другой компании и проверить, что запись не сохранилась, как и в веб-интерфейсе |
| [GHSA-42vx-43vc-x6pr](https://github.com/advisories/GHSA-42vx-43vc-x6pr) | extends | Передать при сохранении родителя в поле связи один-ко-многим ID дочерних записей другого родителя и проверить, что они не переназначены, не отвязаны и не удалены |
| [GHSA-3q6q-26vg-v97x](https://github.com/advisories/GHSA-3q6q-26vg-v97x) | covered | _только пруф_: Ссылка на чужой связанный ресурс при создании — ровно эта проверка |
| [GHSA-vrr2-g9gh-c3jc](https://github.com/advisories/GHSA-vrr2-g9gh-c3jc) | covered | _только пруф_: Ссылка на чужой связанный ресурс — ровно эта проверка |
| [GHSA-6955-hrm5-c4qp](https://github.com/advisories/GHSA-6955-hrm5-c4qp) | extends | Сменить связанный объект на недоступный в контексте ресурса (выключенный в канале) через каждый эндпоинт, который меняет эту связь, и сравнить ответы |
| [GHSA-q4rm-m6xh-5pv7](https://github.com/advisories/GHSA-q4rm-m6xh-5pv7) | extends | Создать ресурс со ссылкой на существующий объект инфраструктуры (сервер, пул), не входящий в разрешённый пользователю список |

### RES-SERVER-GENERATED-FIELDS — Клиент не может задать серверные поля (id, createdAt, status, version) (RWB-0105, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-5wx7-xq8j-v4qm](https://github.com/advisories/GHSA-5wx7-xq8j-v4qm) | extends | Передать в запросе импорта поле автора (created_by) с ID другого пользователя и прочитать созданный объект |

### RES-SOFT-DELETE-VISIBILITY — Мягко удалённые ресурсы не видны в обычных операциях (RWB-0297, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-mf8r-wm2w-f8c5](https://github.com/advisories/GHSA-mf8r-wm2w-f8c5) | extends | Запросить неактивный объект через все публичные эндпоинты: по ID, по категории, по тегу |

### REST-MASS-ASSIGNMENT — Mass assignment защищённых полей (RWB-0121, багов: 3)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-p8x7-9vfw-p7vc](https://github.com/advisories/GHSA-p8x7-9vfw-p7vc) | extends | Передать новый пароль в общем эндпоинте сохранения пользователя, минуя отдельную операцию смены пароля |
| [GHSA-x5m4-g2cq-52pq](https://github.com/advisories/GHSA-x5m4-g2cq-52pq) | extends | Передать id во вложенном объекте атрибутов (newAttributes) операции дублирования или массового изменения |
| [GHSA-qq2c-2q8j-jh27](https://github.com/advisories/GHSA-qq2c-2q8j-jh27) | extends | Сохранить свой ресурс с полем авторов (authors, author) на другого пользователя без права менять авторство |

### REST-OPEN-REDIRECT — Валидация redirect URL (RWB-0125, багов: 2)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-hw3m-8j5x-94ff](https://github.com/advisories/GHSA-hw3m-8j5x-94ff) | extends | Передать в сегмент пути резолвера префикс, который сервер разворачивает во внешний URL (интервики, алиас), и цель с user:pass@host; проверить Location |
| [GHSA-wg2f-x2c2-c4rp](https://github.com/advisories/GHSA-wg2f-x2c2-c4rp) | extends | Открыть форму с внешним заголовком Referer и отправить её с возвратом «назад»; проверить, что Location не ведёт на внешний адрес |

### REST-RATE-LIMIT — Ограничение частоты запросов (RWB-0281, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-xvc3-826v-xf47](https://github.com/advisories/GHSA-xvc3-826v-xf47) | extends | Исчерпать лимит запросов с одного IP и проверить, что запросы с другого IP и другой учётки не получают 429 |

### REST-SENSITIVE-DATA — Отсутствие чувствительных данных в ответах (RWB-0133, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-7788-ghfq-c6mh](https://github.com/advisories/GHSA-7788-ghfq-c6mh) | covered | _только пруф_: Чувствительные данные в ответах — ровно эта проверка |

### REST-SORT-INVALID-FIELD — Сортировка по неизвестному полю (RWB-0134, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-4f5f-j737-pm58](https://github.com/advisories/GHSA-4f5f-j737-pm58) | covered | _только пруф_: Сортировка по существующему, но скрытому полю как оракул уже есть в записи |

### REST-SSRF-URL-FETCH — Контроль server-side URL fetch (RWB-0135, багов: 12)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-cq55-c7wv-pxmq](https://github.com/advisories/GHSA-cq55-c7wv-pxmq) | covered | _только пруф_: Вариант с редиректом внешнего URL на внутренний адрес уже есть в записи |
| [GHSA-rjg7-r26h-cfp2](https://github.com/advisories/GHSA-rjg7-r26h-cfp2) | covered | _только пруф_: Переходные IPv6 и NAT64-префиксы уже есть в записи |
| [GHSA-jr4p-4xjh-fwvw](https://github.com/advisories/GHSA-jr4p-4xjh-fwvw) | extends | Создать объект с внутренним URL в поле, которое сервер проверяет запросом при валидации, и убедиться, что после отказа по адресу запрос к цели не уходит, а ошибки для доступного и недоступного хоста одинаковы |
| [GHSA-6qvr-wjmv-v8mm](https://github.com/advisories/GHSA-6qvr-wjmv-v8mm) | covered | _только пруф_: Редирект на внутренний адрес и DNS rebinding уже есть в записи |
| [GHSA-87mg-5grr-rhwh](https://github.com/advisories/GHSA-87mg-5grr-rhwh) | covered | _только пруф_: Базовая проверка серверной загрузки по URL |
| [GHSA-8x3q-jpjh-qh5c](https://github.com/advisories/GHSA-8x3q-jpjh-qh5c) | covered | _только пруф_: DNS rebinding уже есть в записи |
| [GHSA-pm5p-7w5h-jm5q](https://github.com/advisories/GHSA-pm5p-7w5h-jm5q) | covered | _только пруф_: Серверный запрос по URL пользователя — ровно эта проверка |
| [GHSA-6hq5-7373-42rg](https://github.com/advisories/GHSA-6hq5-7373-42rg) | extends | Указать URL разрешённого домена, который отвечает редиректом на внутренний адрес |
| [GHSA-j8qw-6jw8-r297](https://github.com/advisories/GHSA-j8qw-6jw8-r297) | extends | Встроить в рендеримый документ SVG со ссылкой file:// на существующий и несуществующий путь и сравнить результат |
| [GHSA-8q6q-m837-fv64](https://github.com/advisories/GHSA-8q6q-m837-fv64) | covered | _только пруф_: SSRF по URL пользователя; вариант с редиректом — у другого бага партии |
| [GHSA-pj8j-p4g4-4vw8](https://github.com/advisories/GHSA-pj8j-p4g4-4vw8) | extends | Сохранить в текстовом поле, которое рендерится в PDF, Markdown-изображение с внутренним URL и запросить генерацию документа |
| [GHSA-jmv8-8j9j-rcpc](https://github.com/advisories/GHSA-jmv8-8j9j-rcpc) | covered | _только пруф_: Сценарий записи; механизм в бюллетене не описан подробно |

### SEC-ALT-REPRESENTATION-ACCESS — Закрытый ресурс недоступен ни через одно альтернативное представление (RWB-0231, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-x2rp-9qf7-2fmq](https://github.com/advisories/GHSA-x2rp-9qf7-2fmq) | extends | Проиндексировать закрытый контент, затем выключить его индексацию или закрыть доступ и анонимно искать по словам из него — в результатах нет заголовков, URL и фрагментов закрытого контента |

### SEC-AUTHZ-CACHE-ISOLATION — Authorization context is respected by caches (RWB-0145, багов: 2)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-5974-gfqc-wrcm](https://github.com/advisories/GHSA-5974-gfqc-wrcm) | extends | В одном запросе обратиться сначала к разрешённому ресурсу, затем к запрещённому того же типа и проверить, что решение о доступе не переиспользуется |
| [GHSA-pjhx-3c3w-9v23](https://github.com/advisories/GHSA-pjhx-3c3w-9v23) | extends | Запросить ресурс с полем, видимым по правам, сначала привилегированным, затем непривилегированным пользователем в каждом поддерживаемом формате ответа (JSON, JSON:API, HAL, GraphQL) |

### SEC-AUTHZ-FUNCTION — User without required permission cannot invoke operation (RWB-0146, багов: 19)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-5mmc-8pc9-wggg](https://github.com/advisories/GHSA-5mmc-8pc9-wggg) | extends | Изменить собственный объект от роли без права публикации, передав статус «опубликован», и изменить свой уже опубликованный объект; сравнить с тем же действием через другой API продукта |
| [GHSA-67mx-6wf2-92xp](https://github.com/advisories/GHSA-67mx-6wf2-92xp) | extends | Отправить от роли без права загрузки незавершённые части chunked-загрузки и проверить, что они отклоняются до сохранения во временное хранилище |
| [GHSA-vmwx-m75v-qvch](https://github.com/advisories/GHSA-vmwx-m75v-qvch) | covered | _только пруф_: Проверка каждого маршрута отдельно, включая общие обработчики, уже есть в записи |
| [GHSA-9rg8-2wvr-fgjh](https://github.com/advisories/GHSA-9rg8-2wvr-fgjh) | covered | _только пруф_: Проверка каждого маршрута отдельно, а не по одному представителю, уже есть в записи |
| [GHSA-jr78-w6w5-m8f8](https://github.com/advisories/GHSA-jr78-w6w5-m8f8) | covered | _только пруф_: Вызов защищённой операции без права через отдельный маршрут |
| [GHSA-2cg9-97gq-9mqp](https://github.com/advisories/GHSA-2cg9-97gq-9mqp) | extends | Изменить в присылаемом клиентом состоянии серверного компонента ID привязанного объекта и вызвать изменяющее действие от роли только с правом просмотра |
| [GHSA-99h5-jhh7-v3r3](https://github.com/advisories/GHSA-99h5-jhh7-v3r3) | covered | _только пруф_: Проверка каждого маршрута отдельно уже есть в записи |
| [GHSA-g3f9-g5vj-p62f](https://github.com/advisories/GHSA-g3f9-g5vj-p62f) | extends | _только пруф_: Тот же вариант, что у GHSA-2cg9-97gq-9mqp: цель в изменяемом состоянии компонента |
| [GHSA-f7h9-qv4x-9x57](https://github.com/advisories/GHSA-f7h9-qv4x-9x57) | covered | _только пруф_: Вызов защищённой операции ролью без права, каждого маршрута отдельно |
| [GHSA-f97c-ph8j-8vff](https://github.com/advisories/GHSA-f97c-ph8j-8vff) | covered | _только пруф_: Пользователь без нужного права вызывает операцию |
| [GHSA-8frh-vhgh-64cf](https://github.com/advisories/GHSA-8frh-vhgh-64cf) | extends | Вызвать устаревший эндпоинт обратной операции (возврат) пользователем, у которого есть только право на прямую операцию (выдачу) |
| [GHSA-fm29-4mq3-phg6](https://github.com/advisories/GHSA-fm29-4mq3-phg6) | extends | Вызвать вспомогательные обработчики операции (загрузка формы, выполнение, скачивание результата) напрямую, минуя основной эндпоинт с проверкой права |
| [GHSA-j5jq-cr68-v2xx](https://github.com/advisories/GHSA-j5jq-cr68-v2xx) | extends | Передать в поле формы _handler имя внутреннего метода контроллера и проверить отказ, как при передаче через заголовок |
| [GHSA-xxpx-f366-4xpq](https://github.com/advisories/GHSA-xxpx-f366-4xpq) | extends | Открыть список с правом только на просмотр, затем изменить порядок и родителя элементов структуры |
| [GHSA-rvmm-v933-jgxq](https://github.com/advisories/GHSA-rvmm-v933-jgxq) | covered | _только пруф_: Отказ без права на операцию — ровно эта проверка |
| [GHSA-cvpc-hccg-wmw4](https://github.com/advisories/GHSA-cvpc-hccg-wmw4) | covered | _только пруф_: Операция без права — ровно эта проверка |
| [GHSA-3w32-23wj-rxg3](https://github.com/advisories/GHSA-3w32-23wj-rxg3) | extends | Выполнить перемещение с перезаписью (force=true) при конфликте имён пользователем без права удаления в месте назначения |
| [GHSA-qh45-9g5p-m2v4](https://github.com/advisories/GHSA-qh45-9g5p-m2v4) | extends | Заменить файл другим существующим файлом (assetId + sourceAssetId) без права удаления источника; источник не удаляется |
| [GHSA-43cq-c2gq-pfpw](https://github.com/advisories/GHSA-43cq-c2gq-pfpw) | extends | Переместить объект в раздел или контейнер, где у пользователя только право чтения |

### SEC-AUTHZ-METHOD-MATRIX — Authorization is enforced for every method (RWB-0147, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-r9r3-g9fp-3q4q](https://github.com/advisories/GHSA-r9r3-g9fp-3q4q) | covered | _только пруф_: Права проверяются на всех действиях, кроме одного — ровно матрица по методам |

### SEC-AUTHZ-REVOKE-ROLE — Role revocation takes effect within policy window (RWB-0298, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-c6w6-57jj-62vh](https://github.com/advisories/GHSA-c6w6-57jj-62vh) | extends | После отзыва доступа к проекту повторить и скопировать свою старую запись этого проекта |

### SEC-BOLA-BULK — Bulk endpoint enforces ownership per item (RWB-0148, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-6x7x-gcmf-7r8x](https://github.com/advisories/GHSA-6x7x-gcmf-7r8x) | covered | _только пруф_: Массовая операция без проверки прав на каждый элемент — сценарий записи |

### SEC-IDENTITY-PROOF-OF-POSSESSION — Заявленная клиентом идентичность без доказательства владения не даёт прав и льгот (RWB-0042, багов: 2)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-c2xg-qjqw-2v98](https://github.com/advisories/GHSA-c2xg-qjqw-2v98) | covered | _только пруф_: Заявленная идентичность без доказательства владения — ровно эта проверка |
| [GHSA-h9qx-v5xp-ph8p](https://github.com/advisories/GHSA-h9qx-v5xp-ph8p) | extends | Передать в теле запроса объект с участниками и собственной привилегированной ролью и проверить, что права определяются по серверным данным |

### SEC-OWNERSHIP-DELETE — User cannot delete another owner’s resource (RWB-0149, багов: 2)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-8xjm-wqrp-2f25](https://github.com/advisories/GHSA-8xjm-wqrp-2f25) | extends | Передать при изменении своей записи в параметре очистки файлов путь к файлу другой записи и проверить, что файл не удалён |
| [GHSA-7h62-6v23-v8fm](https://github.com/advisories/GHSA-7h62-6v23-v8fm) | extends | Удалить контейнер (папку) с объектами других пользователей пользователем без права удалять чужие; чужие объекты не удаляются каскадом |

### SEC-OWNERSHIP-READ — User cannot read another owner’s resource (RWB-0150, багов: 6)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-x83g-979r-f5fh](https://github.com/advisories/GHSA-x83g-979r-f5fh) | extends | Подставить чужой последовательный ID заказа в публичный эндпоинт без сессии и проверить, что ни заголовок Location редиректа, ни тело не содержат токен доступа к чужому заказу |
| [GHSA-q6wp-fr43-gm9v](https://github.com/advisories/GHSA-q6wp-fr43-gm9v) | extends | Запросить список объектов модуля от пользователя без прав администратора и проверить, что в нём нет объектов и подписанных ссылок других пользователей |
| [GHSA-mpmw-f6h6-3g26](https://github.com/advisories/GHSA-mpmw-f6h6-3g26) | extends | Передать ID другого пользователя в унаследованные действия эндпоинта «мой профиль» (просмотр, редактирование) |
| [GHSA-4m8q-55qv-9pwp](https://github.com/advisories/GHSA-4m8q-55qv-9pwp) | extends | Запросить список с фильтром по чужому владельцу (user=<id>, users[]=<id>) пользователем, которому чтение отдельных записей этого владельца запрещено |
| [GHSA-mr9r-h354-966r](https://github.com/advisories/GHSA-mr9r-h354-966r) | covered | _только пруф_: Классический BOLA: доступ по идентификатору без проверки владельца; непредсказуемость ID не заменяет проверку |
| [GHSA-2jrw-c95w-h43g](https://github.com/advisories/GHSA-2jrw-c95w-h43g) | extends | Повторить чтение и изменение чужого ресурса ролью «только свои» через каждую версию API |

### SEC-OWNERSHIP-REFERENCE-INDIRECT — Indirect resource references preserve authorization (RWB-0151, багов: 10)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-qh8c-7588-qfrv](https://github.com/advisories/GHSA-qh8c-7588-qfrv) | covered | _только пруф_: Вспомогательный эндпоинт с ID объекта, читающий его без проверки доступа, уже есть в записи |
| [GHSA-65cv-w493-7vhq](https://github.com/advisories/GHSA-65cv-w493-7vhq) | extends | Создать публичную ссылку (предпросмотр, шаринг) на объект без права его просмотра и открыть её без аутентификации |
| [GHSA-h6cx-gjxx-v25c](https://github.com/advisories/GHSA-h6cx-gjxx-v25c) | covered | _только пруф_: Несоответствие родителя из запроса и фактического владельца уже есть в записи |
| [GHSA-crv3-j83j-f3r6](https://github.com/advisories/GHSA-crv3-j83j-f3r6) | covered | _только пруф_: Ссылка на недоступный объект через другой ресурс — ровно проверка косвенных ссылок |
| [GHSA-fc33-6w3q-538h](https://github.com/advisories/GHSA-fc33-6w3q-538h) | extends | Запросить карточку и печатную форму связанного объекта с правом только на него и проверить, что вложенные данные модулей без права чтения не возвращаются |
| [GHSA-rm67-g9ch-vxff](https://github.com/advisories/GHSA-rm67-g9ch-vxff) | extends | Передать в одном запросе изменения ID своего родителя и ID дочернего объекта из чужого родителя |
| [GHSA-2xgg-2x8h-8xw4](https://github.com/advisories/GHSA-2xgg-2x8h-8xw4) | extends | _только пруф_: Пара родитель/дочерний без проверки связи; вариант уже у другого бага партии |
| [GHSA-xv4r-4885-gwpg](https://github.com/advisories/GHSA-xv4r-4885-gwpg) | covered | _только пруф_: Ссылка на недоступный объект при привязке — ровно эта проверка |
| [GHSA-j5mc-p8qg-39j7](https://github.com/advisories/GHSA-j5mc-p8qg-39j7) | extends | Отправить запросы добавления в избранное и удаления из избранного для записи другого пользователя по её ID и проверить, что его данные не изменились |
| [GHSA-mr9h-45p9-fg8h](https://github.com/advisories/GHSA-mr9h-45p9-fg8h) | extends | Запросить подтверждение удаления дочернего объекта своего ресурса с ID дочернего объекта другого пользователя |

### SEC-OWNERSHIP-UPDATE — User cannot modify another owner’s resource (RWB-0152, багов: 4)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-584p-f93j-wpgc](https://github.com/advisories/GHSA-584p-f93j-wpgc) | extends | Из другой анонимной сессии продолжить чужую незавершённую отправку формы, подставив её ID в каждую операцию продолжения (сохранение и финальная отправка) |
| [GHSA-53jc-27pc-x8r8](https://github.com/advisories/GHSA-53jc-27pc-x8r8) | extends | Передать в параметре пути флаг административного действия и ID другого пользователя от имени обычного пользователя |
| [GHSA-3277-h8g9-qj5f](https://github.com/advisories/GHSA-3277-h8g9-qj5f) | extends | Передать в обработчике вложений ID чужого файла и изменить его заголовок, описание и порядок сортировки |
| [GHSA-8hm4-r66f-29wr](https://github.com/advisories/GHSA-8hm4-r66f-29wr) | extends | Начать привязку внешней учётной записи (OAuth) с ID чужого объекта в URL и завершить callback |

### SEC-ROLE-BULK-ADMIN — Bulk admin actions require privilege for every target (RWB-0309, багов: 2)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-243p-f3cv-c5wh](https://github.com/advisories/GHSA-243p-f3cv-c5wh) | covered | _только пруф_: Массовые действия от вызывающего без прав уже есть в записи |
| [GHSA-vgx7-c78r-69w9](https://github.com/advisories/GHSA-vgx7-c78r-69w9) | extends | Выполнить удаление через эндпоинт массового сохранения пользователем с правом изменения, но без права удаления |

### SEC-ROLE-LOW-TO-HIGH — Low-privilege role cannot perform privileged action (RWB-0247, багов: 4)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-9p7c-v5x3-rfx8](https://github.com/advisories/GHSA-9p7c-v5x3-rfx8) | covered | _только пруф_: Низкая роль вызывает административное действие |
| [GHSA-h4hf-v6w5-897x](https://github.com/advisories/GHSA-h4hf-v6w5-897x) | extends | Изменить через API учётку суперпользователя и пароль другого пользователя ролью с правом правки пользователей без права смены паролей |
| [GHSA-3v2j-6fw9-f57c](https://github.com/advisories/GHSA-3v2j-6fw9-f57c) | extends | Установить через API значение поля, разрешённое только старшей роли (невыпущенная версия), ролью с обычным правом изменения |
| [GHSA-m7ph-9558-mrx3](https://github.com/advisories/GHSA-m7ph-9558-mrx3) | extends | Изменить через API статус объекта, требующий старшей роли, ролью с правом обычного изменения |

### SEC-ROLE-SELF-ASSIGN — User cannot grant self a higher role (RWB-0153, багов: 2)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-xhfv-7758-r9hx](https://github.com/advisories/GHSA-xhfv-7758-r9hx) | covered | _только пруф_: Изменение своей группы и назначений прав уже есть в записи |
| [GHSA-j328-xmgp-j4q3](https://github.com/advisories/GHSA-j328-xmgp-j4q3) | covered | _только пруф_: Изменение своих назначений прав и назначение высокой роли другим уже есть в записи |

### SEC-TENANT-CREATE — Client cannot assign resource to another tenant (RWB-0156, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-w8xc-8g92-v77h](https://github.com/advisories/GHSA-w8xc-8g92-v77h) | extends | Создать объект с полем владельца другого пользователя и при ответе с ошибкой проверить, что запись не сохранилась |

### SEC-TENANT-READ — Tenant A cannot read tenant B data (RWB-0157, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-c6w2-j4wq-mvwg](https://github.com/advisories/GHSA-c6w2-j4wq-mvwg) | extends | Запросить, изменить и удалить объекты без арендатора (company_id = null) пользователем, привязанным к арендатору |

### SEC-TENANT-WRITE — Tenant A cannot mutate tenant B data (RWB-0159, багов: 2)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-35cr-9hqq-p2mg](https://github.com/advisories/GHSA-35cr-9hqq-p2mg) | extends | Удалить через эндпоинт действия в отчёте запись другого арендатора по её глобальному ID |
| [GHSA-vgmv-8xjc-6rch](https://github.com/advisories/GHSA-vgmv-8xjc-6rch) | extends | Выполнить переупорядочивание (reorder) с ID записей другого арендатора |

### SEC-VERTICAL-ESCALATION — Lower role cannot invoke higher-role route via alternate method (RWB-0249, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-g2fm-8hr4-j82h](https://github.com/advisories/GHSA-g2fm-8hr4-j82h) | extends | Вызвать защищённый маршрут по имени через параметр общего диспетчера (routeName) от роли без доступа к его пути |

### VAL-REGEX-PATTERN — Поле с pattern принимает только совпадающие значения (RWB-0310, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-2mhj-fhvg-v428](https://github.com/advisories/GHSA-2mhj-fhvg-v428) | extends | Отправить значение с допустимым началом и недопустимым хвостом (пробел, SQL) в поле с шаблоном |

