# Кандидаты из баг-трекеров: партия `directus`

Сгенерировано `tools/mining/cluster.py` из `build/mining/<batch>/batches/*.out.jsonl` и
`ideas/mined/directus.review.yaml` — правки решений делаются в review-файле, затем пересборка.
План — `docs/BUG_MINING_PLAN.md`, шаги 6–7; применение — `tools/mining/apply_proofs.py`.

## Сводка

- Новых паттернов: 12 → идей: 11 (принять: 11, отклонить: 0, не решено: 0).
- Пруфы к существующим: 61 багов → 36 записей; новых шагов-вариантов: 57.

## Новые идеи

Принятые становятся записями `status: draft` с меткой `real-world-bug` и ссылкой на RWB.

| # | Решение | Запись / файл | Идея | Подтверждающие баги |
|---|---|---|---|---|
| 1 | accept | `REST-FILTER-OPERATION-PARITY` (RWB-0251)<br>`checks/rest/pagination.yaml` | Один и тот же фильтр (в том числе по полиморфной связи и на нескольких уровнях вложенности) принимается и даёт согласованный результат во всех операциях — список, агрегация (count = числу записей списка), вложенная выборка (deep), экспорт | [directus/directus#25975](https://github.com/directus/directus/issues/25975), [directus/directus#25892](https://github.com/directus/directus/issues/25892) |
| 2 | accept | `SEC-AUTHZ-DYNAMIC-VARIABLES` (RWB-0252)<br>`checks/security/access-control/SEC-AUTHZ-DYNAMIC-VARIABLES.yaml` | Каждая динамическая переменная в правилах доступа ($CURRENT_USER, $CURRENT_ROLES, $CURRENT_POLICIES) разрешает и запрещает доступ так же, как эквивалентное статическое значение, в том числе в списках (_in) и через связи | [directus/directus#23695](https://github.com/directus/directus/issues/23695) |
| 3 | accept | `VAL-DYNAMIC-VARIABLES-TYPE` (RWB-0253)<br>`checks/rest/input-validation.yaml` | Правило валидации с динамической переменной ($CURRENT_USER.company и т. п.) сравнивает значения по типу поля — целое поле совпадает с целым значением переменной; принятие и отклонение данных такие же, как со статическим значением | [directus/directus#24848](https://github.com/directus/directus/issues/24848) |
| 4 | accept | `ASYNC-SCHEDULE-LONG-UPTIME` (RWB-0254)<br>`checks/common/async-integration.yaml` | Задача по расписанию продолжает срабатывать после длительной непрерывной работы процесса (в первоисточнике — около 25 суток, библиотека node-schedule; вероятная причина — предел 32-битного таймера в миллисекундах, 24,8 суток); проверка — длительная работа или управляемый сдвиг времени на стенде | [directus/directus#25855](https://github.com/directus/directus/issues/25855) |
| 5 | accept | `WS-SUBSCRIPTION-EVENTS-DELIVERED` (RWB-0255)<br>`checks/websocket/websocket.yaml` | Подписка на коллекцию (в том числе системную) после подтверждения получает события создания, изменения и удаления, сделанных через API любым способом; базовая доставка, а не права (WS-SUBSCRIPTION-AUTHZ) и не переподключение (WS-RECONNECT-RESUME) | [directus/directus#25457](https://github.com/directus/directus/issues/25457) |
| 6 | accept | `FILE-MULTIPART-METADATA-SAVED` (RWB-0256)<br>`checks/rest/files.yaml` | Метаданные, переданные полями multipart вместе с файлом (имя для скачивания, заголовок, описание, папка), сохраняются и возвращаются при чтении записи файла — и при порядке полей до и после файла | [directus/directus#25055](https://github.com/directus/directus/issues/25055) |
| 7 | accept | `RES-RELATION-NULL-TARGET-ROWS` (RWB-0257)<br>`checks/common/resource-lifecycle.yaml` | Чтение связи многие-ко-многим возвращает все записи связующей таблицы, в том числе со ссылкой null или на удалённый объект (связанный объект — null), а не теряет их молча | [directus/directus#24145](https://github.com/directus/directus/issues/24145) |
| 8 | accept | `RES-RELATIONS-SHARED-JUNCTION-ISOLATION` (RWB-0258)<br>`checks/common/resource-lifecycle.yaml` | Несколько связей ресурса через одну общую связующую таблицу (политика ↔ пользователи и политика ↔ роли) возвращают каждая только свои данные — значения связей не смешиваются и не подменяются | [directus/directus#23785](https://github.com/directus/directus/issues/23785) |
| 9 | accept | `AUTH-EXTERNAL-IDP-MISSING-ATTRIBUTES` (RWB-0259)<br>`checks/security/authentication-session.yaml` | Вход через внешний IdP с профилем без необязательных атрибутов (email, имя) обрабатывается по требованиям — допустимый вход успешен, недопустимый даёт 4xx с понятной причиной, без 5xx; пара к AUTH-EXTERNAL-IDP-UNVERIFIED-EMAIL | [directus/directus#24099](https://github.com/directus/directus/issues/24099) |
| 10 | accept | `FILE-TRANSFORM-STORAGE-PARITY` (RWB-0260)<br>`checks/rest/files.yaml` | Поддерживаемые трансформации и пресеты изображений (key, параметры) отдают файл на каждом поддерживаемом драйвере хранилища так же, как на локальном диске; нужны стенды с несколькими драйверами, отсутствие драйвера — неприменимость | [directus/directus#23955](https://github.com/directus/directus/issues/23955) |
| 11 | accept | `WS-MULTIPLE-ENDPOINTS-INDEPENDENT` (RWB-0261)<br>`checks/websocket/websocket.yaml` | Несколько WebSocket-эндпоинтов на разных путях (realtime, GraphQL subscriptions, служебные) работают независимо — включение одного не ломает рукопожатие, аутентификацию и сообщения другого | [directus/directus#23625](https://github.com/directus/directus/issues/23625) |

## Пруфы к существующим

Запись получает метку `real-world-bug` и `Real-world bug: RWB-NNNN`; статус не меняется. Для `extends`
текст варианта добавляется шагом (`steps[].action`, в `notes` — RWB). Неверное совпадение — ID бага в
`proofs.exclude`, вариант без нового шага — в `proofs.no_variant`.

### BIZ-SIDE-EFFECTS-ONCE — Побочные эффекты (письма, push, события) выполняются ровно один раз (RWB-0065, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [directus/directus#24542](https://github.com/directus/directus/issues/24542) | extends | Загрузить файл через протокол возобновляемой загрузки (TUS) и проверить, что событие загрузки и связанные вебхуки срабатывают так же, как при обычной загрузке |

### COMPAT-IMPLEMENTATION-MATCHES-CONTRACT — Реализация соответствует опубликованному контракту (RWB-0067, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [directus/directus#25888](https://github.com/directus/directus/issues/25888) | extends | Сравнить обнуляемость полей в схеме GraphQL с ограничениями модели для полей NOT NULL со значением по умолчанию и без него |

### CONC-PARALLEL-INDEPENDENT — Параллельные независимые запросы одной операции выполняются без 5xx (RWB-0008, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [directus/directus#24239](https://github.com/directus/directus/issues/24239) | extends | Отправить множество параллельных запросов GraphQL сразу после изменения схемы или прав (сброса кэша схемы) |

### CONTRACT-FIELD-SELECTION — Выбор полей возвращает ровно запрошенные поля с правильными значениями (RWB-0026, багов: 3)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [directus/directus#25521](https://github.com/directus/directus/issues/25521) | extends | Запросить экспорт в CSV, поставив поля связанной сущности между прямыми полями, и проверить порядок колонок |
| [directus/directus#25138](https://github.com/directus/directus/issues/25138) | extends | Задать алиас поля с именем в синтаксисе функции (year(x)) и проверить ключ и значение в ответе |
| [directus/directus#25121](https://github.com/directus/directus/issues/25121) | extends | Запросить fields=* вместе с заданным алиасом и проверить, что алиас есть в ответе |

### CONTRACT-PUBLISHED-SCHEMA-VALID — Опубликованные сервисом описания API валидны в заявленном диалекте (RWB-0049, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [directus/directus#24155](https://github.com/directus/directus/issues/24155) | covered | _только пруф_: Запись проверяет ровно валидность опубликованного описания API |

### ERR-STATUS-MATCHES-EFFECT — Код ответа соответствует фактическому результату операции (RWB-0045, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [directus/directus#25871](https://github.com/directus/directus/issues/25871) | extends | Загрузить файл, затем прочитать его метаданные и скачать содержимое: успешная загрузка означает заполненные имя на диске и размер и доступный файл |

### FILE-DOWNLOAD-AUTHZ — Скачивание файлов проверяет права и срок действия ссылок (RWB-0070, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [directus/directus#24057](https://github.com/directus/directus/issues/24057) | extends | Запретить роли чтение поля имени файла и скачать файл: Content-Disposition не содержит запрещённого имени |

### FILE-DOWNLOAD-HEADERS — Скачивание отдаёт корректные Content-Type, Content-Disposition и nosniff (RWB-0262, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [directus/directus#23849](https://github.com/directus/directus/issues/23849) | extends | Скачать файл и проверить, что ответ успешный и содержит корректный Content-Security-Policy (default-src 'none') |

### GQL-EQUIVALENT-SELECTION-FORMS — Эквивалентные формы выбора полей GraphQL дают одинаковые данные (RWB-0014, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [directus/directus#26133](https://github.com/directus/directus/issues/26133) | extends | Повторить запрос с аргументом filter по полю связанной коллекции, запросив поле связи под алиасом |

### OBS-AUDIT-TRAIL — Чувствительные действия фиксируются в журнале аудита (RWB-0092, багов: 2)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [directus/directus#25720](https://github.com/directus/directus/issues/25720) | extends | Изменить несколько записей одним пакетным запросом и проверить, что ревизия каждой записи содержит её собственные значения |
| [directus/directus#25894](https://github.com/directus/directus/issues/25894) | extends | Отключить журналирование для коллекции и сохранить версию записи — записи активности и ревизий не создаются |

### OBS-HEALTH-ENDPOINTS — Health-эндпоинты отражают состояние и не раскрывают детали (RWB-0093, багов: 2)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [directus/directus#26191](https://github.com/directus/directus/issues/26191) | extends | Запустить несколько экземпляров с общим хранилищем и вызывать health-эндпоинт каждого: проверка не изменяет общий объект и не вызывает ошибок лимита хранилища |
| [directus/directus#23635](https://github.com/directus/directus/issues/23635) | extends | Запросить health при каждом поддерживаемом драйвере хранилища и проверить, что исправное хранилище даёт статус ok |

### OBS-NO-SECRETS-IN-LOGS — Логи не содержат паролей, токенов и ПДн в открытом виде (RWB-0263, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [directus/directus#24641](https://github.com/directus/directus/issues/24641) | extends | Использовать секрет со спецсимволами регулярных выражений ()[]{}/$^ в операции с журналированием и проверить, что запрос не падает, а секрет в журнале замаскирован |

### PAGE-TOTAL-COUNT — Общее число элементов согласовано с суммой страниц (RWB-0095, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [directus/directus#24719](https://github.com/directus/directus/issues/24719) | extends | Отфильтровать по полю связи многие-ко-многим, где у записи несколько подходящих связанных элементов, и сравнить filter_count с числом записей |

### PERF-DEEP-PAGINATION — Глубокая пагинация и большие выборки не деградируют неприемлемо (RWB-0264, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [directus/directus#24594](https://github.com/directus/directus/issues/24594) | extends | Выполнить поиск по строке в коллекции из 100 000+ записей со многими текстовыми полями и замерить время ответа |

### PERF-LATENCY-BASELINE — Задержка ключевых операций в пределах SLO при обычной нагрузке (RWB-0096, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [directus/directus#25581](https://github.com/directus/directus/issues/25581) | extends | Замерить время операций изменения схемы (создание коллекции, добавление поля) на каждой поддерживаемой СУБД |

### REQ-CROSS-CLIENT-CONSISTENCY — Одно правило продукта одинаково в API разных клиентов (RWB-0099, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [directus/directus#23898](https://github.com/directus/directus/issues/23898) | covered | _только пруф_: Запись уже сравнивает одну сущность через разные эндпоинты и протоколы |

### RES-DELETE-WITH-DEPENDENTS — Удаление ресурса с зависимыми объектами выполняется по правилам каскада (RWB-0102, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [directus/directus#23923](https://github.com/directus/directus/issues/23923) | extends | Удалить поле, указанное в настройках коллекции (поля для дублирования), и проверить, что ссылка на него удалена из настроек |

### RES-DRAFT-PUBLISH-FIDELITY — Публикация черновика переносит все изменения и не ломает связи других объектов (RWB-0015, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [directus/directus#26084](https://github.com/directus/directus/issues/26084) | extends | Опубликовать черновик, в котором удалены элементы связи (delete со списком первичных ключей), и проверить успех публикации |

### RES-EXPORT-IMPORT-ROUNDTRIP — Данные, выгруженные API, принимаются им же обратно без изменений (RWB-0029, багов: 7)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [directus/directus#24961](https://github.com/directus/directus/issues/24961) | extends | Изменить схему, затем применить снимок, удаляющий коллекцию и поля со связями, при включённом кэше схемы |
| [directus/directus#25453](https://github.com/directus/directus/issues/25453) | extends | Экспортировать в CSV записи со связью многие-к-одному (заголовки через точку) и импортировать файл обратно — связи заполнены |
| [directus/directus#24648](https://github.com/directus/directus/issues/24648) | extends | Выгрузить снимок схемы при наличии в БД таблиц, не зарегистрированных в API, и применить его к экземпляру без этих таблиц |
| [directus/directus#24440](https://github.com/directus/directus/issues/24440) | extends | Импортировать CSV, где значения разных колонок одной строки совпадают, и проверить, что значения сохранены без изменений |
| [directus/directus#24082](https://github.com/directus/directus/issues/24082) | extends | Передать числовой первичный ключ, полученный из API, в ссылочное поле item при создании версии одиночной записи |
| [directus/directus#23859](https://github.com/directus/directus/issues/23859) | extends | Выгрузить снимок схемы с проиндексированным полем и применить к другому экземпляру — индекс должен появиться |
| [directus/directus#23667](https://github.com/directus/directus/issues/23667) | extends | Изменить несущественное свойство поля первичного ключа, выгрузить снимок схемы и применить его к другому экземпляру |

### RES-LARGE-RELATION-SET — Тысячи связанных объектов не дают 5xx из-за лимитов СУБД на параметры запроса (RWB-0022, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [directus/directus#25066](https://github.com/directus/directus/issues/25066) | extends | Заменить набор связей M2M списком длиннее лимита выборки по умолчанию, включив уже существующие связи, и проверить отсутствие дублей |

### RES-READ-AFTER-WRITE — Чтение после записи соответствует модели согласованности (RWB-0228, багов: 2)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [directus/directus#25270](https://github.com/directus/directus/issues/25270) | extends | Выполнить изменение конфигурации (установку расширения) на одном экземпляре кластера и прочитать результат с каждого другого экземпляра |
| [directus/directus#25923](https://github.com/directus/directus/issues/25923) | extends | Изменить черновую версию одиночной записи (singleton) и прочитать её с параметром версии |

### RES-SYSTEM-OBJECT-PROTECTED — Встроенные системные объекты защищены от удаления и изменения при любой конфигурации (RWB-0035, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [directus/directus#24816](https://github.com/directus/directus/issues/24816) | extends | Изменить встроенное поле системной коллекции через API полей — отказ; создать пользовательское поле в той же коллекции — успех |

### REST-DATE-TIME-TZ — Дата, время и timezone (RWB-0113, багов: 2)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [directus/directus#25113](https://github.com/directus/directus/issues/25113) | extends | Сохранить дату с годом меньше 1000 и проверить, что ответ содержит год из четырёх цифр (0001-01-01) |
| [directus/directus#25060](https://github.com/directus/directus/issues/25060) | extends | Сравнить значение метки времени в агрегации (max, min) с обычным чтением той же записи при часовом поясе сервера не UTC |

### REST-DUPLICATE-UNIQUE-KEY — Дублирование уникального ключа (RWB-0114, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [directus/directus#25784](https://github.com/directus/directus/issues/25784) | extends | Нарушить составное уникальное ограничение из двух полей и проверить 4xx с кодом нарушения уникальности |

### REST-EMPTY-VALUES — Пустые объект, массив и строка (RWB-0115, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [directus/directus#23939](https://github.com/directus/directus/issues/23939) | extends | Создать коллекцию с пустым объектом schema и без полей |

### REST-FILTER-EQUIVALENT-FORMS — Логически эквивалентные формы фильтра дают одинаковый ответ (RWB-0002, багов: 3)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [directus/directus#24367](https://github.com/directus/directus/issues/24367) | extends | Записать условие диапазона по полю связанной коллекции как _and внутри поля и сравнить ответ с _and на верхнем уровне |
| [directus/directus#24190](https://github.com/directus/directus/issues/24190) | extends | Передать в query-строке фильтр с вложенностью групп $and/$or глубже лимита разбора query-параметров и сравнить с той же формой в теле запроса |
| [directus/directus#24038](https://github.com/directus/directus/issues/24038) | extends | Передать параметры чтения (version, fields) в теле запроса SEARCH и сравнить ответ с тем же запросом GET с query-строкой |

### REST-OPTIONAL-EMPTY-VALUE — Отсутствующий и пустой параметр (RWB-0265, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [directus/directus#25385](https://github.com/directus/directus/issues/25385) | extends | Запустить операцию без необязательного списка ключей и проверить 2xx, а не 403 |

### REST-PATCH-PARTIAL-UPDATE — Семантика PATCH (RWB-0127, багов: 2)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [directus/directus#24319](https://github.com/directus/directus/issues/24319) | extends | Изменить одно свойство столбца-автоинкремента (unique) через API схемы и проверить, что тип и значение по умолчанию не изменились |
| [directus/directus#23992](https://github.com/directus/directus/issues/23992) | extends | Изменить другое свойство строкового столбца с заданной длиной и проверить, что длина не сброшена к значению по умолчанию |

### REST-PATH-PARAM-ENCODING — Кодирование path-параметров (RWB-0266, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [directus/directus#23986](https://github.com/directus/directus/issues/23986) | extends | Запросить ресурс с первичным ключом, содержащим закодированный слэш (%2F), во всех маршрутах, принимающих ключ, включая служебные |

### REST-TYPE-MISMATCH — Несовпадение типа поля (RWB-0138, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [directus/directus#24442](https://github.com/directus/directus/issues/24442) | extends | Передать нечисловое значение в числовых query-параметрах трансформации файла (quality, width, height) |

### SEC-AUTHN-MALFORMED — Malformed credential is rejected (RWB-0142, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [directus/directus#23941](https://github.com/directus/directus/issues/23941) | extends | Отправить в сброс пароля строку, не являющуюся JWT, и в проверку хеша строку, не являющуюся хешем, без аутентификации |

### SEC-AUTHZ-ROLE-POSITIVE-MATRIX — Разрешённая операция работает для каждой роли с правом, а не только для администратора (RWB-0004, багов: 9)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [directus/directus#26118](https://github.com/directus/directus/issues/26118) | extends | Заменить существующий файл через возобновляемую загрузку (TUS) под не-администратором с правом обновления файлов |
| [directus/directus#25212](https://github.com/directus/directus/issues/25212) | extends | Запросить количество отфильтрованных записей ролью без права чтения первичного ключа, фильтр по разрешённому полю |
| [directus/directus#24257](https://github.com/directus/directus/issues/24257) | extends | Прочитать записи с вложенными полями связи под ролью без права на первичный ключ связанной коллекции |
| [directus/directus#24125](https://github.com/directus/directus/issues/24125) | extends | Выполнить запрос под ролью с правилом доступа по $CURRENT_USER, когда фильтр запроса содержит то же значение для поля другого типа |
| [directus/directus#24008](https://github.com/directus/directus/issues/24008) | extends | _только пруф_: Тот же механизм, что directus#24125: повтор значения в правиле доступа и фильтре запроса; вариант уже у #24125 |
| [directus/directus#23952](https://github.com/directus/directus/issues/23952) | extends | Задать собственное правило чтения для системной коллекции и проверить, что пользователь видит разрешённые этим правилом записи |
| [directus/directus#24336](https://github.com/directus/directus/issues/24336) | extends | Удалить файл под ролью с правом удаления, но без права чтения служебных полей файла (хранилище, имя на диске) |
| [directus/directus#24011](https://github.com/directus/directus/issues/24011) | covered | _только пруф_: Запись проверяет ровно это: разрешённая операция работает не только у администратора |
| [directus/directus#23876](https://github.com/directus/directus/issues/23876) | extends | Изменить связанную запись вложенным запросом через родителя под ролью без права изменять первичный ключ связанной коллекции |

### VAL-DEFAULT-VALUES — Опущенные необязательные поля получают задокументированные значения по умолчанию (RWB-0166, багов: 2)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [directus/directus#25977](https://github.com/directus/directus/issues/25977) | extends | Передать необязательный параметр явно со значением по умолчанию и сравнить ответ с запросом без параметра |
| [directus/directus#25914](https://github.com/directus/directus/issues/25914) | extends | Отправить агрегацию только с одной функцией, опустив остальные необязательные (sum, avg, min, max) |

### VAL-DEFERRED-FAILURE — Принятые при записи данные не вызывают 5xx в зависимых операциях (RWB-0003, багов: 2)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [directus/directus#25653](https://github.com/directus/directus/issues/25653) | extends | Сохранить правило доступа с фильтром {"_eq": null} и выполнить чтение под ролью с этим правилом |
| [directus/directus#23838](https://github.com/directus/directus/issues/23838) | extends | Сохранить правило доступа с фильтром по связанной коллекции политик и прочитать список пользователей под ролью с этим правилом |

### VAL-NESTED-OBJECT-ERRORS — Ошибка во вложенном объекте указывает точный путь к полю (RWB-0171, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [directus/directus#26197](https://github.com/directus/directus/issues/26197) | extends | Отправить запись с превышением длины одного строкового поля при валидных остальных и проверить, что ошибка не называет другое поле (например, первичный ключ) |

### WS-MALFORMED-MESSAGE — Некорректные сообщения не рвут соединение без ответа (RWB-0178, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [directus/directus#24147](https://github.com/directus/directus/issues/24147) | extends | Отправить сообщение подписки с необязательным полем, равным null, и сравнить с ответами при отсутствующем поле и пустом объекте |

