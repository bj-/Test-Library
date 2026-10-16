# Кандидаты из баг-трекеров: партия `ghsa-nuget`

Сгенерировано `tools/mining/cluster.py` из `build/mining/<batch>/batches/*.out.jsonl` и
`ideas/mined/ghsa-nuget.review.yaml` — правки решений делаются в review-файле, затем пересборка.
План — `docs/BUG_MINING_PLAN.md`, шаги 6–7; применение — `tools/mining/apply_proofs.py`.

## Сводка

- Новых паттернов: 1 → идей: 1 (принять: 1, отклонить: 0, не решено: 0).
- Пруфы к существующим: 92 багов → 38 записей; новых шагов-вариантов: 60.

## Новые идеи

Принятые становятся записями `status: draft` с меткой `real-world-bug` и ссылкой на RWB.

| # | Решение | Запись / файл | Идея | Подтверждающие баги |
|---|---|---|---|---|
| 1 | accept | `AUTH-SAML-ASSERTION-REPLAY` (RWB-0311)<br>`checks/security/authentication-session.yaml` | Повторно предъявленное SAML-утверждение (или другой одноразовый токен входа — WS-Federation, OIDC ID-токен с nonce) в пределах срока действия отклоняется при включённой защите от повторов, в том числе на другом экземпляре сервиса | [GHSA-9jr3-rj99-8jq3](https://github.com/advisories/GHSA-9jr3-rj99-8jq3) |

## Пруфы к существующим

Запись получает метку `real-world-bug` и `Real-world bug: RWB-NNNN`; статус не меняется. Для `extends`
текст варианта добавляется шагом (`steps[].action`, в `notes` — RWB). Неверное совпадение — ID бага в
`proofs.exclude`, вариант без нового шага — в `proofs.no_variant`.

### ASYNC-WEBHOOK-URL-SSRF — URL вебхука не может указывать на внутренние адреса (RWB-0054, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-74p6-39f2-23v3](https://github.com/advisories/GHSA-74p6-39f2-23v3) | extends | Создать вебхуки на внутренние адреса и разные порты и проверить, что журнал неуспешных доставок не раскрывает ответ и различие открытого и закрытого порта |

### AUTH-LOGOUT-INVALIDATES — После выхода токен и сессия недействительны (RWB-0059, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-wxw9-6pv9-c3xc](https://github.com/advisories/GHSA-wxw9-6pv9-c3xc) | covered | _только пруф_: Выход не инвалидирует сессию — ровно запись |

### AUTH-PASSWORD-RESET-TOKEN — Токен сброса пароля одноразовый, ограничен по времени и привязан к пользователю (RWB-0307, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-x3vp-85cm-q97r](https://github.com/advisories/GHSA-x3vp-85cm-q97r) | extends | Запросить сброс пароля и подтверждение email с адресом, который сервер сопоставляет с пользователем, но дословно отличается от сохранённого, и проверить, что письмо уходит только на сохранённый адрес |

### AUTH-TOKEN-SENDER-CONSTRAINED — Обмен и обновление токена сохраняют привязку к отправителю (DPoP, mTLS) (RWB-0044, багов: 2)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-48pq-2xq3-c2m4](https://github.com/advisories/GHSA-48pq-2xq3-c2m4) | extends | Предъявить SAML-утверждение holder-of-key без KeyInfo и с нестандартным методом подтверждения и проверить отказ аутентификации |
| [GHSA-v9xq-2mvm-x8xc](https://github.com/advisories/GHSA-v9xq-2mvm-x8xc) | extends | Отправить DPoP-токен на собственные эндпоинты сервера авторизации без DPoP-доказательства и с доказательством другого ключа и проверить 401 |

### AUTH-USER-ENUMERATION — Ответы входа, регистрации и восстановления не раскрывают существование аккаунта (RWB-0193, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-hmg4-wwm5-p999](https://github.com/advisories/GHSA-hmg4-wwm5-p999) | covered | _только пруф_: Перечисление по коду и времени — ровно запись |

### ERR-INTERNAL-ERROR-SHAPE — Внутренняя ошибка сервера возвращается в общей модели без утечек (RWB-0068, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-77gj-crhp-3gvx](https://github.com/advisories/GHSA-77gj-crhp-3gvx) | extends | Отправить отрицательные значения параметров пагинации (skip, take) и проверить, что ответ 4xx и не содержит стек-трейса |

### FILE-ARCHIVE-BOMB — Архивные и графические бомбы не исчерпывают ресурсы (RWB-0069, багов: 6)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-qxrv-gp6x-rc23](https://github.com/advisories/GHSA-qxrv-gp6x-rc23) | covered | _только пруф_: Графическая бомба — изображение, заявляющее огромные размеры, ровно то, что проверяет запись |
| [GHSA-v72x-2h86-7f8m](https://github.com/advisories/GHSA-v72x-2h86-7f8m) | extends | Отправить сжатое LZ4 тело MessagePack с заявленной огромной длиной распакованных данных и проверить отказ без выделения памяти |
| [GHSA-g5mf-wqq5-vwg6](https://github.com/advisories/GHSA-g5mf-wqq5-vwg6) | extends | Загрузить многокадровое или многослойное изображение (MNG, PSD) с числом кадров сверх лимита и проверить отказ |
| [GHSA-cwpj-h54c-xjpx](https://github.com/advisories/GHSA-cwpj-h54c-xjpx) | extends | _только пруф_: Тот же вариант, что у GHSA-g5mf-wqq5-vwg6 этой партии; только пруф |
| [GHSA-v7g2-m8c5-mf84](https://github.com/advisories/GHSA-v7g2-m8c5-mf84) | covered | _только пруф_: Графическая бомба; конкретный элемент в бюллетене не раскрыт |
| [GHSA-g85r-6x2q-45w7](https://github.com/advisories/GHSA-g85r-6x2q-45w7) | covered | _только пруф_: Графическая бомба — ровно запись |

### FILE-DOWNLOAD-AUTHZ — Скачивание файлов проверяет права и срок действия ссылок (RWB-0070, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-24mc-gc52-47jv](https://github.com/advisories/GHSA-24mc-gc52-47jv) | extends | Запросить подписанную ссылку на файл со сроком жизни, отличным от значения по умолчанию, и проверить срок в ссылке и отказ сразу после него |

### FILE-MALFORMED-STRUCTURE — Повреждённый файл при разборе метаданных даёт 4xx, а не падение процесса (RWB-0031, багов: 7)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-qh5g-q395-cx4j](https://github.com/advisories/GHSA-qh5g-q395-cx4j) | covered | _только пруф_: Повреждённые метаданные файла роняют процесс — ровно то, что проверяет запись |
| [GHSA-mx48-2qq3-23hf](https://github.com/advisories/GHSA-mx48-2qq3-23hf) | extends | Загрузить векторное изображение (MVG) с глубоко вложенными элементами и проверить отказ 4xx без падения процесса |
| [GHSA-7gg8-qqx7-92g5](https://github.com/advisories/GHSA-7gg8-qqx7-92g5) | extends | Загрузить повреждённый файл редкого графического формата (MIFF) и проверить отказ 4xx за ограниченное время |
| [GHSA-j96m-mjp6-99xr](https://github.com/advisories/GHSA-j96m-mjp6-99xr) | extends | Загрузить SVG, который ссылается сам на себя через xlink:href, и проверить ответ 4xx, живой процесс и отсутствие временных файлов |
| [GHSA-v994-63cg-9wj3](https://github.com/advisories/GHSA-v994-63cg-9wj3) | extends | Загрузить изображение с некорректным IPTC-профилем, запросить выгрузку метаданных в текстовом виде и проверить завершение за ограниченное время |
| [GHSA-pqgj-2p96-rx85](https://github.com/advisories/GHSA-pqgj-2p96-rx85) | extends | Загрузить файл формата PCD без допустимого маркера и проверить завершение декодирования 4xx за ограниченное время |
| [GHSA-rxmq-m78w-7wmc](https://github.com/advisories/GHSA-rxmq-m78w-7wmc) | extends | Загрузить GIF с блоком расширения комментария без терминатора и проверить ответ 4xx за ограниченное время |

### HARD-CLIENT-IP-TRUSTED-PROXIES — IP клиента определяется по цепочке доверенных прокси одинаково на всех маршрутах (RWB-0030, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-fjhg-3mrh-mm7h](https://github.com/advisories/GHSA-fjhg-3mrh-mm7h) | covered | _только пруф_: Механизм не описан; запись проверяет определение IP клиента по доверенным прокси |

### HARD-DEBUG-ENDPOINTS — Отладочные и служебные эндпоинты недоступны извне (RWB-0075, багов: 3)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-8phw-xrj9-cpqp](https://github.com/advisories/GHSA-8phw-xrj9-cpqp) | extends | Отправить запрос с токеном в query-строке, затем прочитать служебный эндпоинт истории запросов и проверить, что секрет в поле uri замаскирован |
| [GHSA-227r-jm2g-7cp4](https://github.com/advisories/GHSA-227r-jm2g-7cp4) | extends | Запросить дамп памяти, окружение и дамп потоков от роли с правом только базового чтения и проверить 403 |
| [GHSA-q62h-354g-5r85](https://github.com/advisories/GHSA-q62h-354g-5r85) | extends | Прочитать служебный эндпоинт конфигурации и проверить, что пароли внутри строк подключения замаскированы, а не только значения с ключами password и secret |

### HARD-EXCESSIVE-DATA-EXPOSURE — Ответы не содержат внутренних полей сверх контракта (RWB-0076, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-m4mm-534h-5cp5](https://github.com/advisories/GHSA-m4mm-534h-5cp5) | extends | Запросить через параметр выбора полей (select) поле, помеченное как недоступное для выбора, и проверить, что оно не возвращается |

### HARD-EXPENSIVE-OPERATION-LIMITS — Дорогие операции ограничены по ресурсам (RWB-0077, багов: 19)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-7pxr-59rr-hqj2](https://github.com/advisories/GHSA-7pxr-59rr-hqj2) | extends | Отправить YAML из 8–9 уровней, где каждый уровень — массив алиасов на якорь предыдущего (billion laughs), и проверить отказ 4xx без роста памяти |
| [GHSA-3w5p-95mh-gq75](https://github.com/advisories/GHSA-3w5p-95mh-gq75) | extends | Отправить в поле-выражение, которое вычисляет сервер, факториал огромного или дробного числа (99999999999999!, 1.5e16!) и проверить отказ 4xx за ограниченное время |
| [GHSA-c399-9853-6jmj](https://github.com/advisories/GHSA-c399-9853-6jmj) | extends | Отправить подписанный XML (SAML, XML-DSig) с глубокой вложенностью, множеством атрибутов и пространств имён в канонизируемых узлах, DTD и множеством EncryptedData и проверить отказ 4xx без исчерпания ресурсов |
| [GHSA-w5qq-qrpp-rf4c](https://github.com/advisories/GHSA-w5qq-qrpp-rf4c) | extends | Отправить серию параллельных multipart-запросов и проверить, что память сервиса ограничена и запросы сверх лимита получают 4xx, а не отказ сервиса |
| [GHSA-8q5v-6pqq-x66h](https://github.com/advisories/GHSA-8q5v-6pqq-x66h) | extends | _только пруф_: Тот же класс, что GHSA-c399-9853-6jmj этой партии (EncryptedData); вариант уже есть, только пруф |
| [GHSA-23rf-6693-g89p](https://github.com/advisories/GHSA-23rf-6693-g89p) | extends | _только пруф_: Тот же класс, что GHSA-c399-9853-6jmj этой партии (EncryptedData); вариант уже есть, только пруф |
| [GHSA-cvvh-rhrc-wg4q](https://github.com/advisories/GHSA-cvvh-rhrc-wg4q) | extends | _только пруф_: Тот же класс, что GHSA-c399-9853-6jmj этой партии (EncryptedData); вариант уже есть, только пруф |
| [GHSA-q6rr-fm2g-g5x8](https://github.com/advisories/GHSA-q6rr-fm2g-g5x8) | extends | Отправить шаблон с умножением массива на огромное число ([1,2,3,4,5] * 50000000) и проверить отказ по лимиту без выделения памяти |
| [GHSA-24c8-4792-22hx](https://github.com/advisories/GHSA-24c8-4792-22hx) | extends | Отправить шаблон со вставкой элемента в массив по огромному индексу ({{ [1] / array.insert_at 200000000 'x' }}) и проверить отказ по лимиту |
| [GHSA-w3x6-4m5h-cxqf](https://github.com/advisories/GHSA-w3x6-4m5h-cxqf) | extends | _только пруф_: Тот же класс, что GHSA-c399-9853-6jmj этой партии (EncryptedData); вариант уже есть, только пруф |
| [GHSA-37gx-xxp4-5rgx](https://github.com/advisories/GHSA-37gx-xxp4-5rgx) | extends | Отправить XML с некорректно сформированным зашифрованным элементом (EncryptedData, EncryptedKey) и проверить отказ 4xx за ограниченное время |
| [GHSA-xw6w-9jjh-p9cr](https://github.com/advisories/GHSA-xw6w-9jjh-p9cr) | extends | Отправить пользовательский шаблон с умножением строки на очень большое число и сдвигом большого целого на миллионы бит и проверить отказ по лимиту |
| [GHSA-m2p3-hwv5-xpqw](https://github.com/advisories/GHSA-m2p3-hwv5-xpqw) | extends | Отправить шаблон из множества выражений, каждое чуть меньше лимита вывода, и проверить, что ограничен суммарный размер результата |
| [GHSA-v66j-x4hw-fv9g](https://github.com/advisories/GHSA-v66j-x4hw-fv9g) | extends | Вызвать во входном шаблоне функцию дополнения строки (pad_left, pad_right) с шириной около 10^9 и проверить отказ без выделения памяти |
| [GHSA-c875-h985-hvrc](https://github.com/advisories/GHSA-c875-h985-hvrc) | extends | Отправить шаблон с операцией над большим диапазоном (1..1000000 / array.size) при малом лимите циклов и проверить прерывание по лимиту |
| [GHSA-5rpf-x9jg-8j5p](https://github.com/advisories/GHSA-5rpf-x9jg-8j5p) | extends | Отправить шаблон, удваивающий строку в цикле из 30 итераций, и проверить отказ по лимиту размера при настройках по умолчанию |
| [GHSA-wg3g-gvx5-2pmv](https://github.com/advisories/GHSA-wg3g-gvx5-2pmv) | extends | Загрузить MVG с многоуровневой вложенностью, запросить конвертацию в SVG и проверить отказ по лимиту глубины за ограниченное время |
| [GHSA-q5r6-9qwq-g2wj](https://github.com/advisories/GHSA-q5r6-9qwq-g2wj) | extends | Отправить тело в формате Amazon Ion с синтаксической ошибкой и проверить отказ 4xx за ограниченное время |
| [GHSA-8xfc-gm6g-vgpv](https://github.com/advisories/GHSA-8xfc-gm6g-vgpv) | extends | Передать (загрузить или предъявить при mTLS) EC-сертификат с искусственными параметрами кривой F2m и проверить отказ за ограниченное время |

### HARD-HOST-HEADER — Подмена Host и X-Forwarded-Host не влияет на ссылки и маршрутизацию (RWB-0078, багов: 2)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-58f6-6rj2-3v8r](https://github.com/advisories/GHSA-58f6-6rj2-3v8r) | extends | Отправить на публичный порт запрос к служебному эндпоинту с Host, указывающим служебный порт, и проверить 404 или 403 |
| [GHSA-75x2-6h4m-h6mx](https://github.com/advisories/GHSA-75x2-6h4m-h6mx) | covered | _только пруф_: Отравление ссылки сброса через Host — ровно запись |

### HARD-SLOW-CLIENT-LIMITS — Медленные и неполные запросы и непрочитанные ответы не накапливаются без ограничения (RWB-0024, багов: 2)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-334f-vvp4-7g6p](https://github.com/advisories/GHSA-334f-vvp4-7g6p) | extends | Подключить к WebSocket-хабу клиента с восстановлением состояния, перестать читать сообщения и проверить, что рассылка остальным клиентам не блокируется |
| [GHSA-j8gr-8fp3-5q5h](https://github.com/advisories/GHSA-j8gr-8fp3-5q5h) | extends | _только пруф_: Тот же класс, что GHSA-334f-vvp4-7g6p этой партии; вариант уже есть, только пруф |

### HARD-UNSAFE-API-CONSUMPTION — Ответы сторонних API валидируются перед использованием (RWB-0080, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-vrgw-pc9c-qrrc](https://github.com/advisories/GHSA-vrgw-pc9c-qrrc) | extends | Указать в настройке источника данных URL внешнего WSDL с вредоносным содержимым и проверить, что сервер не генерирует и не исполняет код из него |

### HTTP-ACCEPT-LANGUAGE — Язык сообщений определяется Accept-Language с fallback (RWB-0312, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-f4g7-52wc-p8x7](https://github.com/advisories/GHSA-f4g7-52wc-p8x7) | extends | Отправить серию анонимных запросов с уникальными несуществующими именами культур в Accept-Language и параметре культуры и проверить, что память сервиса не растёт |

### INJ-OS-COMMAND — Инъекция команд ОС не исполняется (RWB-0085, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-2jh5-g5ch-43q5](https://github.com/advisories/GHSA-2jh5-g5ch-43q5) | extends | Передать в параметр, который сервер отдаёт внешней утилите, значение с метасимволами cmd.exe (&, /, ^) и проверить, что команда не исполняется на Windows |

### INJ-PATH-TRAVERSAL — Обход каталогов через параметры файлов и путей невозможен (RWB-0086, багов: 3)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-wxhm-2mq7-7697](https://github.com/advisories/GHSA-wxhm-2mq7-7697) | extends | Загрузить шаблон с директивой подключения файла по абсолютному пути и через ../ и проверить, что содержимое файлов вне каталога шаблона не попадает в ответ |
| [GHSA-xwc6-v6g8-pw2h](https://github.com/advisories/GHSA-xwc6-v6g8-pw2h) | extends | Передать в параметр имени или пути файла псевдоимена дескрипторов fd:0 и fd:1 и проверить отказ без доступа к потокам процесса |
| [GHSA-hfv2-pf68-m33x](https://github.com/advisories/GHSA-hfv2-pf68-m33x) | extends | Передать в параметр временного файла пути к существующему и несуществующему файлу вне каталога загрузки и проверить одинаковый ответ 4xx |

### INJ-REDOS — Пользовательский ввод не вызывает катастрофический backtracking в regex (RWB-0088, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-c2g3-c4gc-w5wg](https://github.com/advisories/GHSA-c2g3-c4gc-w5wg) | extends | Запросить путь, где сегмент с несколькими параметрами без разделителя / заполнен десятками тысяч дефисов, и проверить ответ за обычное время |

### INJ-SQL — SQL-инъекция во входных параметрах не исполняется (RWB-0089, багов: 4)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-rfx3-98h7-v3xp](https://github.com/advisories/GHSA-rfx3-98h7-v3xp) | extends | Передать одинарную кавычку и SQL-выражение в имени ключа атрибута фильтра и в идентификаторе арендатора и проверить, что лишние записи и данные других арендаторов не возвращаются |
| [GHSA-vmw2-qwm8-x84c](https://github.com/advisories/GHSA-vmw2-qwm8-x84c) | extends | Передать одинарную кавычку и SQL с pg_sleep в параметр языка полнотекстового поиска и проверить отказ без задержки ответа |
| [GHSA-x9vc-6hfv-hg8c](https://github.com/advisories/GHSA-x9vc-6hfv-hg8c) | extends | Отправить данные с суммарным размером параметров больше 2 ГБ и проверить отказ по лимиту размера, а не выполнение внедрённого SQL |
| [GHSA-287f-46j7-j4wh](https://github.com/advisories/GHSA-287f-46j7-j4wh) | covered | _только пруф_: Классическая SQL-инъекция |

### INJ-SSRF-PARAMETERS — Параметры с URL и хостами не дают доступа к внутренней сети (RWB-0090, багов: 2)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-h66j-xm43-47pp](https://github.com/advisories/GHSA-h66j-xm43-47pp) | covered | _только пруф_: Классический SSRF через параметр URL |
| [GHSA-3f7v-qx94-666m](https://github.com/advisories/GHSA-3f7v-qx94-666m) | covered | _только пруф_: SSRF через параметр; способ обхода в бюллетене не описан |

### INJ-STORED-XSS — Сохранённые данные с HTML/JS не создают XSS у потребителей API (RWB-0244, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-rw6c-xp26-225v](https://github.com/advisories/GHSA-rw6c-xp26-225v) | extends | Загрузить файл со строкой <script> в метаданных и запросить конвертацию в HTML; проверить экранирование в результате |

### INJ-TEMPLATE-SSTI — Инъекция в серверные шаблоны не исполняется (RWB-0091, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-7jvp-hj45-2f2m](https://github.com/advisories/GHSA-7jvp-hj45-2f2m) | extends | Отправить шаблон с присваиванием свойств переданного в контекст объекта ({{ user.is_admin = true }}) и проверить, что после рендеринга объект не изменился |

### OBS-TRACE-PROPAGATION — Контекст трассировки принимается и передаётся дальше (RWB-0245, багов: 3)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-38wr-vpc7-2mp4](https://github.com/advisories/GHSA-38wr-vpc7-2mp4) | extends | Отправить заголовок baggage с десятками тысяч пар ключ-значение и с одним очень большим значением и проверить, что лишнее отбрасывается без роста времени ответа |
| [GHSA-vc29-vg52-6643](https://github.com/advisories/GHSA-vc29-vg52-6643) | extends | Отправить запросы с заголовками traceparent и tracestate и проверить, что время и CPU обработки не отличаются от запросов без них |
| [GHSA-8785-wc3w-h8q6](https://github.com/advisories/GHSA-8785-wc3w-h8q6) | extends | _только пруф_: Тот же дефект, что GHSA-vc29-vg52-6643; вариант уже предложен — только пруф |

### PRIV-RESPONSE-FOREIGN-DATA — Ответ не содержит фрагментов данных других запросов и памяти процесса (RWB-0009, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-8g53-9m3c-69xg](https://github.com/advisories/GHSA-8g53-9m3c-69xg) | extends | Загрузить изображение MNG, кадры которого не покрывают полотно, повторить несколько раз и проверить, что непокрытые области результата одинаковы и не содержат данных памяти |

### REST-OPEN-REDIRECT — Валидация redirect URL (RWB-0125, багов: 5)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-2qjj-h6wp-c7h7](https://github.com/advisories/GHSA-2qjj-h6wp-c7h7) | covered | _только пруф_: Валидация адреса перенаправления — ровно то, что проверяет запись |
| [GHSA-vfm5-cr22-jg3m](https://github.com/advisories/GHSA-vfm5-cr22-jg3m) | covered | _только пруф_: Открытый редирект через параметр возврата |
| [GHSA-55p7-v223-x366](https://github.com/advisories/GHSA-55p7-v223-x366) | covered | _только пруф_: Открытый редирект; форма URL в бюллетене не раскрыта |
| [GHSA-ff4q-64jc-gx98](https://github.com/advisories/GHSA-ff4q-64jc-gx98) | covered | _только пруф_: Открытый редирект; форма URL в бюллетене не раскрыта |
| [GHSA-j74q-mv2c-rxmp](https://github.com/advisories/GHSA-j74q-mv2c-rxmp) | covered | _только пруф_: Открытый редирект |

### SEC-AUTHN-MISSING — Protected operation rejects missing credentials (RWB-0143, багов: 3)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-wjpq-6766-7f5j](https://github.com/advisories/GHSA-wjpq-6766-7f5j) | extends | Подключиться к сервису, пропустив шаг согласования безопасности транспорта, отправить сообщение и проверить, что операция не вызвана |
| [GHSA-86vq-ccwf-rm62](https://github.com/advisories/GHSA-86vq-ccwf-rm62) | covered | _только пруф_: Отсутствие аутентификации на эндпоинтах данных — ровно запись |
| [GHSA-6cwx-42hw-w69c](https://github.com/advisories/GHSA-6cwx-42hw-w69c) | covered | _только пруф_: Отсутствие аутентификации на защищённом эндпоинте |

### SEC-AUTHZ-CACHE-ISOLATION — Authorization context is respected by caches (RWB-0145, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-75vq-qvhr-7ffr](https://github.com/advisories/GHSA-75vq-qvhr-7ffr) | extends | Запросить ресурс с валидным API-ключом, затем тот же путь и query без ключа и с неверным ключом и проверить 401 вместо закэшированного ответа |

### SEC-AUTHZ-FUNCTION — User without required permission cannot invoke operation (RWB-0146, багов: 4)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-c8qj-jx8j-fg2w](https://github.com/advisories/GHSA-c8qj-jx8j-fg2w) | covered | _только пруф_: Пользователь без права вызывает операцию — ровно то, что проверяет запись |
| [GHSA-6ffg-mjg7-585x](https://github.com/advisories/GHSA-6ffg-mjg7-585x) | covered | _только пруф_: Функциональная авторизация — ровно запись |
| [GHSA-4gp9-ff99-j6vj](https://github.com/advisories/GHSA-4gp9-ff99-j6vj) | covered | _только пруф_: Функциональная авторизация — ровно запись |
| [GHSA-hrww-x3fq-xcvh](https://github.com/advisories/GHSA-hrww-x3fq-xcvh) | extends | Вызвать эндпоинты административного API с токеном пользователя другого типа (участника сайта, а не сотрудника) и проверить 403 |

### SEC-OWNERSHIP-DELETE — User cannot delete another owner’s resource (RWB-0149, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-wx5h-wqfq-v698](https://github.com/advisories/GHSA-wx5h-wqfq-v698) | extends | Удалить медиа-элемент из папки вне разрешённой пользователю части дерева, подставив его ID в URL, и проверить 403 |

### SEC-OWNERSHIP-READ — User cannot read another owner’s resource (RWB-0150, багов: 2)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-2hr5-cvwp-jr5w](https://github.com/advisories/GHSA-2hr5-cvwp-jr5w) | covered | _только пруф_: Классический IDOR чтения |
| [GHSA-hhcw-wwxv-g95c](https://github.com/advisories/GHSA-hhcw-wwxv-g95c) | covered | _только пруф_: Классический IDOR чтения |

### SEC-OWNERSHIP-REFERENCE-INDIRECT — Indirect resource references preserve authorization (RWB-0151, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-wr57-hqmp-fgvh](https://github.com/advisories/GHSA-wr57-hqmp-fgvh) | extends | Запросить анонимно публичный ресурс со ссылкой на защищённый без expand и с expand, в том числе во вложенных блоках, и проверить, что не возвращаются ни свойства, ни имя, маршрут и id защищённого |

### SEC-OWNERSHIP-UPDATE — User cannot modify another owner’s resource (RWB-0152, багов: 2)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-fpj4-9qhx-5m6m](https://github.com/advisories/GHSA-fpj4-9qhx-5m6m) | extends | Отправить запрос принятия заявки (в друзья, приглашения), адресованной другому пользователю, и проверить отказ 403 и неизменный статус заявки |
| [GHSA-fpvf-fvp5-996r](https://github.com/advisories/GHSA-fpvf-fvp5-996r) | extends | Назначить узлу контента вне разрешённой пользователю части дерева связанную настройку (домен) через отдельный эндпоинт и проверить 403 |

### SEC-ROLE-LOW-TO-HIGH — Low-privilege role cannot perform privileged action (RWB-0247, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-xhw7-j96h-c3g5](https://github.com/advisories/GHSA-xhw7-j96h-c3g5) | extends | Вызвать административную POST-операцию от минимальной роли и проверить не только ответ (403 или редирект), но и отсутствие её эффекта в данных |

### VAL-DEEP-NESTING — Чрезмерно вложенный JSON отклоняется без деградации сервиса (RWB-0165, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-f8h2-vmm9-qhj6](https://github.com/advisories/GHSA-f8h2-vmm9-qhj6) | extends | Отправить в WebSocket-хаб по протоколу MessagePack сообщение с глубоко вложенными массивами и проверить закрытие соединения с ошибкой без падения процесса |

### VAL-LARGE-COLLECTION-PAYLOAD — Массив с очень большим числом элементов отклоняется или обрабатывается в пределах лимитов (RWB-0169, багов: 2)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-cxmj-83gh-fp49](https://github.com/advisories/GHSA-cxmj-83gh-fp49) | extends | Отправить бинарное тело (MessagePack), заявляющее огромную длину или размерности массива при пустом содержимом, и проверить отказ 4xx без роста памяти |
| [GHSA-w567-gjr2-hm5j](https://github.com/advisories/GHSA-w567-gjr2-hm5j) | extends | _только пруф_: Тот же вариант, что у GHSA-cxmj-83gh-fp49 этой партии — заявленная длина без данных; только пруф |

### WS-MESSAGE-LIMITS — Размер и частота сообщений ограничены (RWB-0205, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-4vgm-c2wm-63mw](https://github.com/advisories/GHSA-4vgm-c2wm-63mw) | covered | _только пруф_: Механизм не описан; запись проверяет ограничение размера сообщений |

