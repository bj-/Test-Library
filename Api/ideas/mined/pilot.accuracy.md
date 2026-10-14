# Точность LLM-шагов: ручная выборка партии `pilot`

Этап 7 плана (`docs/BUG_MINING_PLAN.md`), цель — не меньше 85 % верных. Сгенерировано
`tools/mining/evaluate.py` (seed 7). В колонке «Верно» поставить `да` или `нет` (и кратко, почему).

## Триаж и абстракция (50: половина API, половина вне области)

Верно, если решение «API / вне области» правильное, а для API паттерн не додумывает того, чего нет в баге.

| # | Баг | Решение | Обоснование / паттерн | Верно |
|---|---|---|---|---|
| 1 | [GHSA-jx63-h26r-8cph](https://github.com/advisories/GHSA-jx63-h26r-8cph) | API: Регулярное выражение, заданное пользователем, не блокирует сервер | Регулярное выражение из запроса компилировалось без проверки, катастрофический backtracking блокировал сервер | |
| 2 | [GHSA-7mx3-vvmw-hjmv](https://github.com/advisories/GHSA-7mx3-vvmw-hjmv) | API: Алиасы GraphQL с именами __proto__, constructor, prototype не загрязняют прототип при слиянии результатов | Алиасы __proto__/constructor при слиянии ответов подграфов загрязняли прототип и ломали все запросы | |
| 3 | [keycloak/keycloak#50039](https://github.com/keycloak/keycloak/issues/50039) | API: Пустые и пробельные элементы в массиве строк отклоняются или отбрасываются одинаково | Пустая строка в массиве URI даёт 409 «дубликат» вместо 400 на одной из СУБД | |
| 4 | [GHSA-6mwv-4mrm-5p3m](https://github.com/advisories/GHSA-6mwv-4mrm-5p3m) | API: Параметры, из которых собирается адрес исходящего запроса (регион, поддомен, тенант), не меняют хост | Параметр region подставлялся в имя хоста — '#' и порт уводили запрос с API-ключом в Authorization на хост атакующего. | |
| 5 | [keycloak/keycloak#53117](https://github.com/keycloak/keycloak/issues/53117) | API: Новая версия API возвращает все публичные поля прежней (нет лишнего вырезания) | Публичное поле вырезалось из ответа новой версии API | |
| 6 | [GHSA-322m-ff4g-9vx9](https://github.com/advisories/GHSA-322m-ff4g-9vx9) | API: Проверка адреса для исходящего запроса выполняется в момент подключения (защита от DNS rebinding) | SSRF через подмену DNS между проверкой и подключением | |
| 7 | [GHSA-354h-gmhv-mr9c](https://github.com/advisories/GHSA-354h-gmhv-mr9c) | API: URL вебхука не может указывать на внутренние адреса | SSRF через URL вебхука — сотрудник опрашивает внутренние хосты с сервера. | |
| 8 | [expressjs/express#6580](https://github.com/expressjs/express/issues/6580) | API: API, доступный по HTTP/2, обрабатывает запросы так же, как по HTTP/1.1 | Сервер падал на любом запросе по HTTP/2 | |
| 9 | [GHSA-cw9w-vv67-hf73](https://github.com/advisories/GHSA-cw9w-vv67-hf73) | API: Обновление токена не расширяет аудиторию за пределы согласованного ресурса | Refresh-токен не был привязан к ресурсу согласия — обновление с другим resource давало токен к нему | |
| 10 | [GHSA-jp82-f5mq-hwhp](https://github.com/advisories/GHSA-jp82-f5mq-hwhp) | API: Объявленная длина в сериализованных данных не приводит к выделению без лимита | Маленький сериализованный payload с большим полем length выделяет огромный типизированный массив — исчерпание памяти и блокировка event loop. | |
| 11 | [expressjs/body-parser#119](https://github.com/expressjs/body-parser/issues/119) | API: Разные виды невалидного JSON дают ошибку одного класса и формата | Разные виды невалидного JSON дают разные ошибки | |
| 12 | [keycloak/keycloak#51527](https://github.com/keycloak/keycloak/issues/51527) | API: Явный null в PATCH для секрета не обходит политику ротации | PATCH с явным null в поле секрета генерирует новый секрет в обход политики ротации - старый перестаёт работать сразу. | |
| 13 | [nestjs/nest#13910](https://github.com/nestjs/nest/issues/13910) | API: Остановка сервиса с открытыми долгими соединениями завершается за отведённое время | Закрытие WebSocket-адаптера закрывало HTTP-сервер раньше времени и блокировало остановку при долгих соединениях | |
| 14 | [strapi/strapi#27395](https://github.com/strapi/strapi/issues/27395) | API: Схемы, которые API публикует (OpenAPI, JSON Schema, MCP tools), валидны в заявленном диалекте и проходят строгий валидатор | Опубликованные схемы инструментов не соответствуют заявленному диалекту JSON Schema | |
| 15 | [GHSA-v6q3-xqxm-6f5v](https://github.com/advisories/GHSA-v6q3-xqxm-6f5v) | API: Фильтр по скрытому секретному полю не позволяет подобрать его значение | Фильтр по скрытому полю token приглашений позволял подобрать секрет и повысить привилегии | |
| 16 | [keycloak/keycloak#49611](https://github.com/keycloak/keycloak/issues/49611) | API: Все задокументированные схемы Authorization принимаются на своих эндпоинтах | Расширения API после регресса принимают только Bearer/DPoP и отклоняют Basic | |
| 17 | [keycloak/keycloak#49909](https://github.com/keycloak/keycloak/issues/49909) | API: Просроченный токен отклоняется 401 на каждом защищённом эндпоинте | Просроченный токен на эндпоинте регистрации клиентов даёт 500 вместо 401 | |
| 18 | [expressjs/session#239](https://github.com/expressjs/session/issues/239) | API: Анонимный запрос без входа не получает cookie сессии и не создаёт сессию | Анонимный запрос получал cookie сессии | |
| 19 | [directus/directus#26768](https://github.com/directus/directus/issues/26768) | API: Агрегат общего количества равен реальному числу записей и не ограничен размером страницы по умолчанию | GraphQL-агрегат countAll выполнял выборку с лимитом по умолчанию вместо подсчёта | |
| 20 | [strapi/strapi#27235](https://github.com/strapi/strapi/issues/27235) | API: Логически эквивалентные фильтры с разной вложенностью $and/$or дают одинаковый ответ | Связи, выведенные из фильтра, терялись в ответе в зависимости от глубины вложенности $and/$or | |
| 21 | [GHSA-xgv3-crq2-6f69](https://github.com/advisories/GHSA-xgv3-crq2-6f69) | API: Ответы аутентификации применяют полевые права и скрытые поля | Ответы обновления токена и сброса пароля возвращали поля пользователя, закрытые полевыми правами. | |
| 22 | [GHSA-pj7x-6wpf-pgvp](https://github.com/advisories/GHSA-pj7x-6wpf-pgvp) | API: Путь к вложенному полю JSON в фильтре не позволяет SQL-инъекцию | SQL-инъекция через путь к вложенному полю JSON и операторы в запросе фильтрации | |
| 23 | [expressjs/session#340](https://github.com/expressjs/session/issues/340) | API: Скользящая сессия продлевается при активности: срок на сервере и в cookie обновляется | Скользящее продление сессии не обновляло срок | |
| 24 | [nestjs/nest#3939](https://github.com/nestjs/nest/issues/3939) | API: Политика CORS | После обновления CORS на Fastify-адаптере перестал работать — заголовки не отдаются. | |
| 25 | [strapi/strapi#26746](https://github.com/strapi/strapi/issues/26746) | API: Сортировка по вычисляемому полю вместе с фильтром по связи не даёт 5xx | Сортировка по вычисляемому статусу вместе с фильтром по связи давала 500 на PostgreSQL | |
| 26 | [GHSA-m8m8-qj5v-23w3](https://github.com/advisories/GHSA-m8m8-qj5v-23w3) | вне области (`other`) | Гаджет prototype pollution в HTTP-клиенте, требует примитива загрязнения в том же процессе — не обнаружить запросами | |
| 27 | [nestjs/nest#484](https://github.com/nestjs/nest/issues/484) | вне области (`other`) | Ошибка e2e-тестов GraphQL-приложения — тестовое окружение. | |
| 28 | [nestjs/nest#491](https://github.com/nestjs/nest/issues/491) | вне области (`memory`) | Обработчик сообщения навешивается на каждый запрос с неверным паттерном — рост памяти. | |
| 29 | [nestjs/nest#1320](https://github.com/nestjs/nest/issues/1320) | вне области (`other`) | Предупреждение об устаревании в тестах из-за мутации метаданных — тестовые утилиты. | |
| 30 | [expressjs/session#85](https://github.com/expressjs/session/issues/85) | вне области (`other`) | Сбой сохранения в пользовательском хранилище сессий из-за функций в объекте — внутренняя логика | |
| 31 | [GHSA-hx4r-w6wj-j8fg](https://github.com/advisories/GHSA-hx4r-w6wj-j8fg) | вне области (`other`) | devalue: CPU на разреженных массивах в uneval — по словам авторов практически неэксплуатируемо. | |
| 32 | [GHSA-wf3x-273g-mvxv](https://github.com/advisories/GHSA-wf3x-273g-mvxv) | вне области (`other`) | devalue: выделение памяти при исполнении вывода uneval у клиента — клиентская сторона. | |
| 33 | [nestjs/nest#10333](https://github.com/nestjs/nest/issues/10333) | вне области (`other`) | Поведение адаптера фреймворка при ручной асинхронной отправке ответа | |
| 34 | [strapi/strapi#27317](https://github.com/strapi/strapi/issues/27317) | вне области (`ui`) | Скачок высоты компонента в интерфейсе | |
| 35 | [directus/directus#26956](https://github.com/directus/directus/issues/26956) | вне области (`build`) | Типы TypeScript в SDK не дают операторы фильтра для date/time — проблема типизации клиента | |
| 36 | [nestjs/nest#16785](https://github.com/nestjs/nest/issues/16785) | вне области (`build`) | Каталог вывода сборки SWC | |
| 37 | [GHSA-c48m-32m9-vx93](https://github.com/advisories/GHSA-c48m-32m9-vx93) | вне области (`other`) | vm2: обход allowlist внешних модулей через совпадающее имя — изоляция песочницы. | |
| 38 | [expressjs/express#6275](https://github.com/expressjs/express/issues/6275) | вне области (`other`) | Браузер дополнительно запрашивает favicon — не баг | |
| 39 | [keycloak/keycloak#51131](https://github.com/keycloak/keycloak/issues/51131) | вне области (`other`) | Ложное предупреждение в логе при нагрузке — внутренняя логика закрытия сессий | |
| 40 | [nestjs/nest#9041](https://github.com/nestjs/nest/issues/9041) | вне области (`other`) | Поведение логгера фреймворка | |
| 41 | [nestjs/nest#14601](https://github.com/nestjs/nest/issues/14601) | вне области (`build`) | Ошибка запуска после обновления зависимостей (несовместимость адаптера и express) | |
| 42 | [GHSA-r273-hxvj-fxhp](https://github.com/advisories/GHSA-r273-hxvj-fxhp) | вне области (`other`) | vm2: util.getCallSites раскрывает стек хоста в песочнице. | |
| 43 | [directus/directus#27955](https://github.com/directus/directus/issues/27955) | вне области (`build`) | Неверная nullability в типах | |
| 44 | [GHSA-7q3f-wx44-378m](https://github.com/advisories/GHSA-7q3f-wx44-378m) | вне области (`other`) | vm2: префиксное сравнение путей модулей — изоляция песочницы. | |
| 45 | [expressjs/express#4899](https://github.com/expressjs/express/issues/4899) | вне области (`other`) | Лимит синхронного стека роутера ломает маршрутизацию — внутренняя логика фреймворка | |
| 46 | [nestjs/nest#2261](https://github.com/nestjs/nest/issues/2261) | вне области (`other`) | req.url в middleware показывает '/' — внутреннее поведение маршрутизации, на ответ не влияет. | |
| 47 | [expressjs/express#5999](https://github.com/expressjs/express/issues/5999) | вне области (`other`) | Нестроковый путь маршрута падает в новой версии библиотеки — ошибка запуска | |
| 48 | [directus/directus#27969](https://github.com/directus/directus/issues/27969) | вне области (`build`) | Несоответствие nullability в типах SDK | |
| 49 | [GHSA-mcm9-63f2-9j32](https://github.com/advisories/GHSA-mcm9-63f2-9j32) | вне области (`other`) | devalue: квадратичное раздувание uneval в очень узких условиях — внутренняя сериализация. | |
| 50 | [nestjs/nest#384](https://github.com/nestjs/nest/issues/384) | вне области (`docs`) | Вопрос по настройке wss в документации — не дефект поведения. | |

## Сопоставление с библиотекой (30)

Верно, если баг действительно относится к записи (covered — уже покрыт, extends — новый вариант той же записи).

| # | Баг | Тип | Запись | Заметка | Верно |
|---|---|---|---|---|---|
| 1 | [nestjs/nest#13360](https://github.com/nestjs/nest/issues/13360) | extends | `GRPC-STREAM-TERMINATION` | Добавить вариант: исключение в обработчике стрима — клиент получает ошибку, сервис после этого доступен | |
| 2 | [keycloak/keycloak#52378](https://github.com/keycloak/keycloak/issues/52378) | covered | `COMPAT-IMPLEMENTATION-MATCHES-CONTRACT` | Строгая валидация ответа по опубликованной схеме ловит расхождение | |
| 3 | [keycloak/keycloak#52568](https://github.com/keycloak/keycloak/issues/52568) | extends | `OBS-AUDIT-TRAIL` | Добавить отказы на всех ветках проверок выдачи токена, а не только успешные действия | |
| 4 | [nestjs/nest#288](https://github.com/nestjs/nest/issues/288) | covered | `RESIL-DEPENDENCY-DOWN` | Ровно недоступность зависимости | |
| 5 | [GHSA-v6q3-xqxm-6f5v](https://github.com/advisories/GHSA-v6q3-xqxm-6f5v) | extends | `INJ-FILTER-EXPRESSION` | Добавить фильтр по скрытым полям как оракул подбора секрета (без инъекции синтаксиса) | |
| 6 | [GHSA-53vv-xm9f-mm82](https://github.com/advisories/GHSA-53vv-xm9f-mm82) | extends | `REST-SORT-INVALID-FIELD` | Добавить сортировку по существующему, но скрытому полю как оракул, включая алиасы, суффиксы и составные выражения | |
| 7 | [nestjs/nest#13093](https://github.com/nestjs/nest/issues/13093) | extends | `REST-SECURITY-HEADERS` | Проверять заголовки и другие следы middleware во всех версиях API (вместе с вариантом про исключения из глобального префикса) | |
| 8 | [GHSA-f67j-2jqw-jpq7](https://github.com/advisories/GHSA-f67j-2jqw-jpq7) | extends | `INJ-REDOS` | Добавить вариант: незавершённая HTML-разметка в контенте с серверным разбором — зависание парсера, не regex | |
| 9 | [GHSA-798p-78g2-v556](https://github.com/advisories/GHSA-798p-78g2-v556) | extends | `INJ-SSRF-PARAMETERS` | Добавить вариант: доменное имя, резолвящееся во внутренний/метаданных адрес (wildcard-DNS), — не только IP-литералы | |
| 10 | [GHSA-2q76-m6w6-qgc6](https://github.com/advisories/GHSA-2q76-m6w6-qgc6) | extends | `AUTH-API-KEY-LIFECYCLE` | Добавить вариант: создание/отзыв ключа для чужой учётной записи (владение ключом) | |
| 11 | [keycloak/keycloak#49960](https://github.com/keycloak/keycloak/issues/49960) | extends | `AUTH-BRUTE-FORCE-PROTECTION` | Вариант: refresh токена или SSO по cookie из существующей сессии не должен сбрасывать блокировку | |
| 12 | [GHSA-prgh-xp8r-p3m5](https://github.com/advisories/GHSA-prgh-xp8r-p3m5) | extends | `INJ-REDOS` | Добавить вариант: email-адреса и почтовые заголовки (комментарии RFC 5322, длинные строки без '@') — квадратичный парсер, а не только regex | |
| 13 | [nestjs/nest#2557](https://github.com/nestjs/nest/issues/2557) | extends | `BIZ-SIDE-EFFECTS-ONCE` | Добавить вариант: обработчик WebSocket-события, зарегистрированный дважды (наследование) | |
| 14 | [GHSA-g734-fhp4-7mfp](https://github.com/advisories/GHSA-g734-fhp4-7mfp) | extends | `INJ-SSRF-PARAMETERS` | Добавить вариант: параметр базового URL сторонней интеграции - проверять не только доступ к внутренней сети, но и утечку серверного токена интеграции на подконтрольный внешний адрес | |
| 15 | [GHSA-v6pj-gxxw-phfw](https://github.com/advisories/GHSA-v6pj-gxxw-phfw) | extends | `INJ-SQL` | Вариант: инъекция в имени поля (ключе JSON), а не в значении; связано с REST-MASS-ASSIGNMENT | |
| 16 | [GHSA-g74q-6g2f-874x](https://github.com/advisories/GHSA-g74q-6g2f-874x) | extends | `SEC-TOKEN-AUDIENCE` | Вариант: аудитория/приложение для проверки берётся из параметра запроса — должна браться из конфигурации сервиса | |
| 17 | [keycloak/keycloak#51674](https://github.com/keycloak/keycloak/issues/51674) | extends | `AUTH-PASSWORD-POLICY` | Добавить вариант: режим с ограниченным криптопровайдером (FIPS), пароль короче его внутреннего минимума — ошибка политики, а не 5xx; проверить все пути (смена, сброс, обязательное обновление) | |
| 18 | [directus/directus#27844](https://github.com/directus/directus/issues/27844) | extends | `REQ-CROSS-CLIENT-CONSISTENCY` | Вариант: разные транспорты одного API (REST и WebSocket) — валидация параметров должна совпадать | |
| 19 | [keycloak/keycloak#52776](https://github.com/keycloak/keycloak/issues/52776) | extends | `VAL-ARRAY-ITEMS-BOUNDARIES` | Добавить обязательный массив с пустыми элементами среди непустых | |
| 20 | [GHSA-8xcj-9hfr-fh9j](https://github.com/advisories/GHSA-8xcj-9hfr-fh9j) | extends | `SEC-OWNERSHIP-READ` | Добавить вариант: косвенное чтение через clone/copy/duplicate — права проверяются и на источник, а не только на место назначения | |
| 21 | [GHSA-r3ph-w7gj-g6xm](https://github.com/advisories/GHSA-r3ph-w7gj-g6xm) | extends | `HARD-EXPENSIVE-OPERATION-LIMITS` | Добавить вариант: YAML с алиасами и merge-ключами (включая пустые отображения) — стоимость разбора ограничена | |
| 22 | [keycloak/keycloak#49388](https://github.com/keycloak/keycloak/issues/49388) | extends | `SEC-SCOPE-EXTRA-UNTRUSTED` | Вариант: согласованность проверки scope между grant type (позитивная и негативная сторона) | |
| 23 | [GHSA-jp82-f5mq-hwhp](https://github.com/advisories/GHSA-jp82-f5mq-hwhp) | extends | `VAL-LARGE-COLLECTION-PAYLOAD` | Добавить вариант: объявленная длина без самих данных (маленький запрос — большое выделение) | |
| 24 | [GHSA-2m6q-8v3h-jqww](https://github.com/advisories/GHSA-2m6q-8v3h-jqww) | extends | `REST-OPEN-REDIRECT` | Вариант: редирект на внутренний маршрут, где пользовательское значение — сегмент пути; проверить scheme-relative '//host' | |
| 25 | [directus/directus#28042](https://github.com/directus/directus/issues/28042) | extends | `RES-TIMESTAMPS` | Добавить проверку меток времени для всех альтернативных путей создания (resumable-загрузка и др.) | |
| 26 | [strapi/strapi#26606](https://github.com/strapi/strapi/issues/26606) | extends | `RES-CREATE-RESPONSE-MATCHES-READ` | Добавить вариант: поле-связь, заданное альтернативным идентификатором, на нестандартном эндпоинте ресурса — 200 без применения | |
| 27 | [nestjs/nest#437](https://github.com/nestjs/nest/issues/437) | covered | `FILE-UPLOAD-TYPE-VALIDATION` | — | |
| 28 | [GHSA-7c34-32v3-j575](https://github.com/advisories/GHSA-7c34-32v3-j575) | extends | `SEC-OWNERSHIP-REFERENCE-INDIRECT` | Добавить вариант: раскрытие связи и фильтр по полям связанной коллекции с условными правами чтения | |
| 29 | [strapi/strapi#26359](https://github.com/strapi/strapi/issues/26359) | extends | `REST-FILTER-SORT-COMPOSITION` | Добавить вариант: сортировка на уровне раскрываемой связи вместе с сортировкой верхнего уровня | |
| 30 | [directus/directus#27412](https://github.com/directus/directus/issues/27412) | extends | `RESIL-DEPENDENCY-DOWN` | Добавить вариант: ошибка зависимости не маппится в 403/404 (ложный отказ в доступе) | |
