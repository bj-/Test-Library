# Кандидаты из баг-трекеров: партия `ghsa-go`

Сгенерировано `tools/mining/cluster.py` из `build/mining/<batch>/batches/*.out.jsonl` и
`ideas/mined/ghsa-go.review.yaml` — правки решений делаются в review-файле, затем пересборка.
План — `docs/BUG_MINING_PLAN.md`, шаги 6–7; применение — `tools/mining/apply_proofs.py`.

## Сводка

- Новых паттернов: 10 → идей: 10 (принять: 10, отклонить: 0, не решено: 0).
- Пруфы к существующим: 201 багов → 70 записей; новых шагов-вариантов: 149.

## Новые идеи

Принятые становятся записями `status: draft` с меткой `real-world-bug` и ссылкой на RWB.

| # | Решение | Запись / файл | Идея | Подтверждающие баги |
|---|---|---|---|---|
| 1 | accept | `OBS-METRICS-LABEL-CARDINALITY` (RWB-0282)<br>`checks/common/observability.yaml` | Значения из запроса (метод, путь, заголовки, коды) не создают неограниченно новых серий метрик — неизвестные значения сводятся в одну серию (other), шаблоны пути — в маршрут; размер /metrics и память не растут | [GHSA-6r69-c6wg-7g8m](https://github.com/advisories/GHSA-6r69-c6wg-7g8m) |
| 2 | accept | `SEC-POLICY-TEMPLATE-USER-DATA` (RWB-0283)<br>`checks/security/access-control/SEC-POLICY-TEMPLATE-USER-DATA.yaml` | Данные, которые пользователь задаёт сам (имя, атрибуты, метаданные сущности) и которые подставляются в шаблон политики доступа (<username>/*, *.{name}.example.com), не работают как wildcard и метасимволы — экранируются или отклоняются при создании | [GHSA-59w7-v8rr-pr4p](https://github.com/advisories/GHSA-59w7-v8rr-pr4p) |
| 3 | accept | `HARD-DENYLIST-EVERY-ENTRY` (RWB-0284)<br>`checks/security/api-hardening.yaml` | Каждый элемент списка запрещённых значений (ключи меток и аннотаций, имена полей, домены, команды) отклоняется — проверка перебором всех элементов списка, в том числе в разном регистре и при любом составе и порядке списка | [GHSA-gjw4-3v3v-rqxg](https://github.com/advisories/GHSA-gjw4-3v3v-rqxg) |
| 4 | accept | `INJ-RESERVED-PATH-WRITE` (RWB-0285)<br>`checks/security/injection.yaml` | Запись файлов пользователем через API (патч, загрузка в репозиторий, распаковка, синхронизация) не попадает в служебные каталоги и файлы с особым смыслом (.git/, hooks/, конфигурация, .htaccess) даже по законному относительному пути — без ../; служебный файл не исполняется | [GHSA-rcr6-4jqh-j84m](https://github.com/advisories/GHSA-rcr6-4jqh-j84m) |
| 5 | accept | `HARD-ROUTE-SHARED-BACKEND-ISOLATION` (RWB-0286)<br>`checks/security/api-hardening.yaml` | В шлюзе или прокси несколько маршрутов (в том числе разных арендаторов и пространств имён) к одному бэкенду применяют каждый свои фильтры и заголовки (идентичность арендатора) — конфигурация маршрутов не смешивается | [GHSA-6p8f-p8j2-rqmv](https://github.com/advisories/GHSA-6p8f-p8j2-rqmv) |
| 6 | accept | `SEC-AUTHZ-EXPLICIT-OVER-INHERITED` (RWB-0287)<br>`checks/security/access-control/SEC-AUTHZ-EXPLICIT-OVER-INHERITED.yaml` | В иерархии объектов (проект → подпроект, папка → файл) явное право на дочерний объект — в том числе пониженное — имеет приоритет над унаследованным от родителя, по документированному правилу ближайшего назначения | [GHSA-pjr3-86v4-5p7w](https://github.com/advisories/GHSA-pjr3-86v4-5p7w) |
| 7 | accept | `HARD-BACKUP-RESTORE-PROTECTED` (RWB-0288)<br>`checks/security/api-hardening.yaml` | Восстановление из резервной копии через API не обходит защиту записи — доступно только администратору, подлинность копии проверяется ключом сервера (а не ключом из запроса), защищённые настройки (команды, секреты, роли) подделанной копией не перезаписываются | [GHSA-p393-cf76-4jmr](https://github.com/advisories/GHSA-p393-cf76-4jmr) |
| 8 | accept | `INJ-USER-SCRIPT-SANDBOX` (RWB-0289)<br>`checks/security/injection.yaml` | Пользовательские скрипты, которые сервер штатно исполняет (потоки, правила, хуки, формулы), изолированы — загрузка модулей и чтение файлов хоста, сеть и переменные окружения недоступны, содержимое файлов не попадает в результат | [GHSA-fgmf-7rf8-m6vf](https://github.com/advisories/GHSA-fgmf-7rf8-m6vf) |
| 9 | accept | `SEC-AUTHZ-LIST-CHECK-CONSISTENCY` (RWB-0290)<br>`checks/security/access-control/SEC-AUTHZ-LIST-CHECK-CONSISTENCY.yaml` | Перечисление субъектов или объектов с доступом (кто имеет отношение, какие объекты доступны) согласовано с точечной проверкой каждого — с пересечением, исключением и wildcard в модели прав исключённый не попадает в список | [GHSA-g3pg-frfm-pr2m](https://github.com/advisories/GHSA-g3pg-frfm-pr2m) |
| 10 | accept | `HARD-SETUP-ENDPOINTS-PROTECTED` (RWB-0291)<br>`checks/security/api-hardening.yaml` | Эндпоинты первоначальной настройки (создание первого администратора, восстановление базы в окне инициализации) не позволяют захватить экземпляр без доказательства владения — секрета настройки или локального доступа; после настройки закрыты | [GHSA-x626-fcwx-f5pc](https://github.com/advisories/GHSA-x626-fcwx-f5pc) |

## Пруфы к существующим

Запись получает метку `real-world-bug` и `Real-world bug: RWB-NNNN`; статус не меняется. Для `extends`
текст варианта добавляется шагом (`steps[].action`, в `notes` — RWB). Неверное совпадение — ID бага в
`proofs.exclude`, вариант без нового шага — в `proofs.no_variant`.

### ASYNC-WEBHOOK-SIGNATURE — Вебхуки подписаны, подпись проверяется, повтор отклоняется (RWB-0053, багов: 2)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-c5f6-2rm9-2w8g](https://github.com/advisories/GHSA-c5f6-2rm9-2w8g) | extends | Отправить входящий вебхук с заголовками другого провайдера без подписи и проверить отказ |
| [GHSA-fjwv-jf2v-j499](https://github.com/advisories/GHSA-fjwv-jf2v-j499) | extends | Подменить в подписанном входящем сообщении поле, не входящее в подпись, и проверить, что сервер его не использует |

### ASYNC-WEBHOOK-URL-SSRF — URL вебхука не может указывать на внутренние адреса (RWB-0054, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-p2w3-6x73-2f6x](https://github.com/advisories/GHSA-p2w3-6x73-2f6x) | extends | Указать URL вебхука с IPv6-адресом перехода (6to4, NAT64, Teredo, IPv4-compatible), встраивающим loopback или 169.254.169.254, и проверить отказ |

### AUTH-API-KEY-LIFECYCLE — API-ключи ограничены по правам, отзываются и не раскрываются (RWB-0055, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-qfwc-vx6f-3g6g](https://github.com/advisories/GHSA-qfwc-vx6f-3g6g) | extends | Прочитать одиночную запись секрета доступа пользователем с минимальными правами и проверить, что секрет не возвращается, как в списке |

### AUTH-CSRF — Изменяющие операции с cookie-аутентификацией защищены от CSRF (RWB-0190, багов: 3)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-33rr-wq23-g6gg](https://github.com/advisories/GHSA-33rr-wq23-g6gg) | covered | _только пруф_: Ровно этот сценарий |
| [GHSA-hxjg-93wc-h8p8](https://github.com/advisories/GHSA-hxjg-93wc-h8p8) | covered | _только пруф_: Ровно этот сценарий |
| [GHSA-8cj9-r88m-8945](https://github.com/advisories/GHSA-8cj9-r88m-8945) | extends | Отправить JSON-тело изменяющего запроса из HTML-формы с enctype=text/plain и проверить, что сервер его не принимает |

### AUTH-EXTERNAL-IDP-UNVERIFIED-EMAIL — Вход через внешний IdP не связывается с учёткой по неподтверждённому email (RWB-0041, багов: 3)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-xv7q-fvmc-jx96](https://github.com/advisories/GHSA-xv7q-fvmc-jx96) | covered | _только пруф_: Ровно этот сценарий |
| [GHSA-992q-9gwp-7r79](https://github.com/advisories/GHSA-992q-9gwp-7r79) | covered | _только пруф_: Ровно этот сценарий |
| [GHSA-29rf-f4vv-pvq6](https://github.com/advisories/GHSA-29rf-f4vv-pvq6) | extends | Создать локальную учётку с email X без подтверждения, войти через IdP с подтверждённым email X и проверить, что пароль локальной учётки не даёт доступа |

### AUTH-JWT-TIME-CLAIMS — Токены с nbf/iat в будущем и без exp обрабатываются по политике (RWB-0292, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-v77h-2w3m-94hx](https://github.com/advisories/GHSA-v77h-2w3m-94hx) | covered | _только пруф_: Токен без exp |

### AUTH-MFA-STEP-UP — Операции, требующие второго фактора, недоступны без него (RWB-0060, багов: 3)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-45gv-9wjv-xh7p](https://github.com/advisories/GHSA-45gv-9wjv-xh7p) | extends | Войти паролем в учётку, у которой второй фактор — только passkey, и проверить, что сервер требует второй фактор |
| [GHSA-h246-wpgf-vmq5](https://github.com/advisories/GHSA-h246-wpgf-vmq5) | extends | Вызвать без свежего второго фактора каждую операцию из всех модулей с чувствительными действиями, а не только из исправленных, и проверить отказ |
| [GHSA-hp74-gm6m-2qm5](https://github.com/advisories/GHSA-hp74-gm6m-2qm5) | extends | Пройти повторную аутентификацию свежим токеном, полученным более слабым способом входа (одноразовая ссылка), и проверить, что требование фактора не считается выполненным |

### AUTH-OAUTH-REDIRECT-STATE — OAuth/OIDC flow проверяет redirect_uri, state и PKCE (RWB-0061, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-phg3-3g28-wq9v](https://github.com/advisories/GHSA-phg3-3g28-wq9v) | extends | После завершённого OAuth-входа отправить callback с пустым state и проверить отказ |

### AUTH-OTP-REUSE — Одноразовый код нельзя использовать повторно и после выдачи нового (RWB-0293, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-hf33-q6cf-c66f](https://github.com/advisories/GHSA-hf33-q6cf-c66f) | covered | _только пруф_: Ровно повторное использование одноразового кода |

### AUTH-SESSION-NOT-BEFORE-LOGIN — Анонимный запрос не получает cookie сессии и не создаёт серверную сессию (RWB-0011, багов: 2)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-4595-rvpx-4q34](https://github.com/advisories/GHSA-4595-rvpx-4q34) | extends | Отправить серию неаутентифицированных запросов инициализации сессии с разными ID и проверить, что серверное состояние не накапливается |
| [GHSA-xpxj-f2fm-rqch](https://github.com/advisories/GHSA-xpxj-f2fm-rqch) | extends | Отправить множество анонимных запросов начала OAuth-входа и проверить, что серверное состояние ограничено по числу и сроку жизни |

### AUTH-TOKEN-TYPE-CONFUSION — Refresh, ID или сервисный токен не принимается как access-токен (RWB-0192, багов: 3)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-vfxw-3x8p-2vjr](https://github.com/advisories/GHSA-vfxw-3x8p-2vjr) | extends | Вызвать эндпоинты пользователей токеном гостевой ссылки во всех версиях API и проверить отказ |
| [GHSA-32r8-5843-4qw2](https://github.com/advisories/GHSA-32r8-5843-4qw2) | extends | Токеном ссылки-доступа, чей ID совпадает с ID пользователя, вызвать операции над ресурсами этого пользователя (API-токены, команды, боты) и проверить отказ |
| [GHSA-vvcv-vpph-h844](https://github.com/advisories/GHSA-vvcv-vpph-h844) | extends | _только пруф_: Тот же вариант, что у GHSA-32r8-5843-4qw2 этой партии |

### BIZ-LIMITS-QUOTAS — Лимиты и квоты соблюдаются на границе и не обходятся параллельно (RWB-0294, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-xj3h-wwxq-gfcj](https://github.com/advisories/GHSA-xj3h-wwxq-gfcj) | covered | _только пруф_: Квота обходится параллельно |

### CONC-REQUEST-CONTEXT-ISOLATION — Параллельные запросы разных пользователей получают только свой контекст и свой ответ (RWB-0007, багов: 2)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-qqjf-53cj-pwvv](https://github.com/advisories/GHSA-qqjf-53cj-pwvv) | extends | Через HTTP/3 к бэкенду с привязанной к соединению аутентификацией отправить запрос другим клиентом после входа первого и проверить 401 |
| [GHSA-6765-c87h-8mrf](https://github.com/advisories/GHSA-6765-c87h-8mrf) | extends | Параллельно с успешной аутентификацией пользователя отправить запрос с неизвестным логином и подобранным паролем и проверить 401 |

### ERR-INTERNAL-ERROR-SHAPE — Внутренняя ошибка сервера возвращается в общей модели без утечек (RWB-0068, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-gwfq-86j8-7qhv](https://github.com/advisories/GHSA-gwfq-86j8-7qhv) | covered | _только пруф_: Внутренняя ошибка с утечкой деталей |

### FILE-ARCHIVE-BOMB — Архивные и графические бомбы не исчерпывают ресурсы (RWB-0069, багов: 4)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-w7jp-mf2v-8342](https://github.com/advisories/GHSA-w7jp-mf2v-8342) | covered | _только пруф_: Классическая zip-бомба в загрузке |
| [GHSA-4vh2-39rq-rq8j](https://github.com/advisories/GHSA-4vh2-39rq-rq8j) | extends | Загрузить крошечное изображение с экстремальным соотношением сторон (20000×10) в каждый путь загрузки изображений и проверить отказ |
| [GHSA-75mr-qw9x-3r39](https://github.com/advisories/GHSA-75mr-qw9x-3r39) | covered | _только пруф_: Графическая бомба при обработке изображения |
| [GHSA-g9j2-8w95-3vwv](https://github.com/advisories/GHSA-g9j2-8w95-3vwv) | covered | _только пруф_: В записи уже есть загрузка изображения 50000x50000 пикселей — ровно этот механизм |

### FILE-DOWNLOAD-AUTHZ — Скачивание файлов проверяет права и срок действия ссылок (RWB-0070, багов: 5)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-3cm4-ccvw-6xr6](https://github.com/advisories/GHSA-3cm4-ccvw-6xr6) | extends | Запросить защищённый файл через эндпоинты истории версий и сравнения снимков и проверить тот же отказ, что у прямого чтения |
| [GHSA-fgmr-7w36-9qfq](https://github.com/advisories/GHSA-fgmr-7w36-9qfq) | extends | Запросить через статические маршруты данные, закрытые в файловом API, и проверить тот же отказ |
| [GHSA-v7ph-r5r6-4jcj](https://github.com/advisories/GHSA-v7ph-r5r6-4jcj) | extends | Запросить через служебный эндпоинт сопутствующие данные файла (аннотации, превью) закрытого документа и проверить тот же отказ, что у скачивания самого файла |
| [GHSA-vx2m-jpxr-xv7w](https://github.com/advisories/GHSA-vx2m-jpxr-xv7w) | extends | Получить подсказку контекста при действующем доступе по общей ссылке, отозвать доступ и повторить получение ссылки на файл с той же подсказкой; проверить отказ |
| [GHSA-rmxw-pq4x-3fvh](https://github.com/advisories/GHSA-rmxw-pq4x-3fvh) | extends | Скачать защищённый файл через маршрут массового скачивания архивом и проверить тот же отказ, что у прямого скачивания |

### GRPC-METADATA-AUTH-MISSING — Каждый RPC сервиса требует аутентификационные метаданные (RWB-0295, багов: 2)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-2v6v-25fm-p4fg](https://github.com/advisories/GHSA-2v6v-25fm-p4fg) | covered | _только пруф_: Ровно RPC без аутентификационных метаданных |
| [GHSA-rrwh-6jrq-wp5v](https://github.com/advisories/GHSA-rrwh-6jrq-wp5v) | extends | Вызвать без метаданных аутентификации каждый потоковый RPC сервиса и проверить UNAUTHENTICATED до любых изменений |

### HARD-DEBUG-ENDPOINTS — Отладочные и служебные эндпоинты недоступны извне (RWB-0075, багов: 4)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-9v8p-frvj-2pcm](https://github.com/advisories/GHSA-9v8p-frvj-2pcm) | extends | Подключиться без аутентификации к служебному WebSocket журналов, отправить изменяющее сообщение и проверить отказ и неизменность настроек |
| [GHSA-rh53-xvx2-j327](https://github.com/advisories/GHSA-rh53-xvx2-j327) | extends | Обратиться к внутреннему прокси управления без клиентского сертификата и токена, в том числе изменяющими методами, и проверить отказ |
| [GHSA-mhc4-g3wh-cw7m](https://github.com/advisories/GHSA-mhc4-g3wh-cw7m) | covered | _только пруф_: Отладочный эндпоинт без проверки доступа |
| [GHSA-qh9r-j7rp-4x2m](https://github.com/advisories/GHSA-qh9r-j7rp-4x2m) | extends | Обратиться без учётных данных к управляющим API на внешнем порту, через который подключаются агенты, и проверить отказ |

### HARD-EXCESSIVE-DATA-EXPOSURE — Ответы не содержат внутренних полей сверх контракта (RWB-0076, багов: 2)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-hgfg-j9pg-43xw](https://github.com/advisories/GHSA-hgfg-j9pg-43xw) | extends | Запросить конфигурацию ролью читателя и проверить, что в ней нет состояния сеанса администратора (открытые документы, поисковые запросы, пути) |
| [GHSA-jv8v-xq2h-657v](https://github.com/advisories/GHSA-jv8v-xq2h-657v) | extends | Запросить ролью читателя эндпоинты, разрешающие пути ресурсов, и проверить, что в ответе нет абсолютных путей файловой системы и имени пользователя ОС |

### HARD-EXPENSIVE-OPERATION-LIMITS — Дорогие операции ограничены по ресурсам (RWB-0077, багов: 8)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-jw42-f3rr-4cc3](https://github.com/advisories/GHSA-jw42-f3rr-4cc3) | extends | Загрузить xlsx с номером строки далеко за пределом формата после обычной строки и проверить быстрый отказ |
| [GHSA-jrfj-fhj2-jjvm](https://github.com/advisories/GHSA-jrfj-fhj2-jjvm) | extends | Загрузить зашифрованный OOXML-файл с завышенным spinCount и проверить быстрый отказ |
| [GHSA-q5j5-6p94-4gwc](https://github.com/advisories/GHSA-q5j5-6p94-4gwc) | extends | _только пруф_: Тот же вариант, что у GHSA-jw42-f3rr-4cc3 этой пачки — только пруф |
| [GHSA-rp9v-7xv3-r6g3](https://github.com/advisories/GHSA-rp9v-7xv3-r6g3) | extends | Отправить multipart-запрос с десятками тысяч минимальных файловых частей и проверить отказ по числу частей и что следующие запросы обслуживаются |
| [GHSA-pg57-6jwg-q645](https://github.com/advisories/GHSA-pg57-6jwg-q645) | extends | Запросить загрузку внешнего объекта с глубоко вложенным и ветвящимся графом ссылок с повторами и проверить отказ по лимиту глубины и ширины |
| [GHSA-jr34-h97m-9hpx](https://github.com/advisories/GHSA-jr34-h97m-9hpx) | extends | Отправить длинный заголовок Accept-Language из некорректных тегов с разными разделителями и проверить обычное время ответа |
| [GHSA-mrg3-qvqr-jw29](https://github.com/advisories/GHSA-mrg3-qvqr-jw29) | extends | Отправить через каждый транспорт сервиса сообщение с некорректными счётчиками секций и проверить ранний отказ |
| [GHSA-g35j-m5xg-vh3q](https://github.com/advisories/GHSA-g35j-m5xg-vh3q) | extends | Отправить в потоке кадр неизвестного типа с большой заявленной длиной и проверить, что сервер отбрасывает его тело без накопления в памяти |

### HARD-HOST-HEADER — Подмена Host и X-Forwarded-Host не влияет на ссылки и маршрутизацию (RWB-0078, багов: 2)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-5gm3-9crp-6g3v](https://github.com/advisories/GHSA-5gm3-9crp-6g3v) | extends | Отправить запрос к локальному служебному эндпоинту с посторонним Host и Origin и проверить отказ |
| [GHSA-rf68-8gjr-36q7](https://github.com/advisories/GHSA-rf68-8gjr-36q7) | covered | _только пруф_: Подмена Host в ссылках |

### HARD-ID-PREDICTABILITY — Предсказуемые идентификаторы не позволяют собрать данные перебором (RWB-0296, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-q9c5-pp7m-fm2g](https://github.com/advisories/GHSA-q9c5-pp7m-fm2g) | extends | Перебрать последовательные ID на эндпоинтах, доступных без сессии, и проверить, что без случайного токена в URL данные не отдаются |

### HARD-METHOD-OVERRIDE — Заголовки переопределения метода не обходят авторизацию (RWB-0297, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-6wcg-mqvh-fcvg](https://github.com/advisories/GHSA-6wcg-mqvh-fcvg) | extends | Отправить запрос к закрытому пути с заголовком X-Original-URI или X-Forwarded-Uri, совпадающим с разрешающим правилом, и проверить, что политика применяется к фактическому пути |

### HARD-SLOW-CLIENT-LIMITS — Медленные и неполные запросы и непрочитанные ответы не накапливаются без ограничения (RWB-0024, багов: 2)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-7ghq-v6jf-g56c](https://github.com/advisories/GHSA-7ghq-v6jf-g56c) | extends | Медленно передавать тело запроса по HTTP/3 и проверить, что таймаут чтения срабатывает так же, как для HTTP/1.1 |
| [GHSA-6vch-q96h-7gc3](https://github.com/advisories/GHSA-6vch-q96h-7gc3) | extends | Открыть множество TCP-соединений к TLS-порту без отправки ClientHello и проверить, что они закрываются по тайм-ауту рукопожатия |

### HARD-UNSAFE-API-CONSUMPTION — Ответы сторонних API валидируются перед использованием (RWB-0080, багов: 2)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-wq92-8x3r-fm38](https://github.com/advisories/GHSA-wq92-8x3r-fm38) | extends | Указать в импорте или миграции внешний сервер, отдающий много вложений допустимого размера, и проверить суммарный лимит задачи |
| [GHSA-fmgp-q6jx-gg3x](https://github.com/advisories/GHSA-fmgp-q6jx-gg3x) | extends | Указать во внешнем репозитории файл конфигурации в виде символьной ссылки на /dev/zero или файл вне репозитория и проверить отказ без неограниченного чтения |

### HTTP-HTTP2-RESOURCE-LIMITS — Параметры HTTP/2 со стороны клиента не заставляют сервер буферизовать и работать без предела (RWB-0189, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-vp52-pcj8-j9qc](https://github.com/advisories/GHSA-vp52-pcj8-j9qc) | extends | Открыть несколько стримов HTTP/2 и отправлять тело кадрами DATA по 1 байту в пределах окон управления потоком; наблюдать память сервера и доступность |

### HTTP-TRAILING-SLASH-CASE — Вариации пути (слэш в конце, регистр, двойной слэш) обрабатываются единообразно (RWB-0197, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-964w-f6gj-5236](https://github.com/advisories/GHSA-964w-f6gj-5236) | extends | Запросить заблокированный файл с косой чертой в конце пути и проверить, что ответ — тот же отказ, что без слэша |

### HTTP-VERSION-PARITY — Запросы по HTTP/2 и с предложением Upgrade h2c обслуживаются так же, как по HTTP/1.1 (RWB-0013, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-w4v4-9rw7-5326](https://github.com/advisories/GHSA-w4v4-9rw7-5326) | covered | _только пруф_: Запись проверяет обслуживание с предложением Upgrade h2c так же, как HTTP/1.1 |

### INJ-OS-COMMAND — Инъекция команд ОС не исполняется (RWB-0085, багов: 8)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-5jpj-293f-rhvj](https://github.com/advisories/GHSA-5jpj-293f-rhvj) | covered | _только пруф_: Классическая инъекция команд через поля ресурса |
| [GHSA-m3c6-2p7h-cfr3](https://github.com/advisories/GHSA-m3c6-2p7h-cfr3) | covered | _только пруф_: Классическая инъекция команд через поля ресурса |
| [GHSA-2mw5-23gm-pccq](https://github.com/advisories/GHSA-2mw5-23gm-pccq) | covered | _только пруф_: Классическая инъекция команд через параметры |
| [GHSA-f5pj-2738-996m](https://github.com/advisories/GHSA-f5pj-2738-996m) | extends | Вызвать выполнение разрешённого интерпретатора (bash -c, sh -c) с командой вне allowlist и проверить отказ |
| [GHSA-3x77-wg38-92r3](https://github.com/advisories/GHSA-3x77-wg38-92r3) | extends | _только пруф_: Тот же вариант, что у GHSA-f5pj-2738-996m этой пачки — только пруф |
| [GHSA-74hp-mggr-hv58](https://github.com/advisories/GHSA-74hp-mggr-hv58) | extends | Передать разрешённой программе опции, запускающие вложенную команду (git -c alias.x=!cmd), и проверить отказ |
| [GHSA-j6cw-g6p4-7hch](https://github.com/advisories/GHSA-j6cw-g6p4-7hch) | extends | Сохранить URL прокси с метасимволами оболочки в хосте, затем вызвать проверку соединения и проверить, что команда не выполняется |
| [GHSA-xc5w-4v5w-7x65](https://github.com/advisories/GHSA-xc5w-4v5w-7x65) | extends | Передать подстановку команды $(…) в аргумент каждого типа, допустимого для действия, выполняемого через shell, и проверить, что она не исполняется |

### INJ-PATH-TRAVERSAL — Обход каталогов через параметры файлов и путей невозможен (RWB-0086, багов: 4)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-hf8h-97gm-4x2p](https://github.com/advisories/GHSA-hf8h-97gm-4x2p) | extends | Передать абсолютный путь вне рабочего каталога в параметр, по которому сервер проверяет существование файла, и сравнить ответы для существующего и несуществующего пути |
| [GHSA-w5fv-7x5q-g8qp](https://github.com/advisories/GHSA-w5fv-7x5q-g8qp) | extends | Отправить в путь WebDAV закодированные сегменты %2e%2e и %2f учёткой, ограниченной папкой, и проверить, что доступ не выходит за её корень |
| [GHSA-fqj9-69pf-6pjg](https://github.com/advisories/GHSA-fqj9-69pf-6pjg) | extends | Отправить путь вида /<свой>/../<чужой>/объект, где первый сегмент проходит проверку владельца, и проверить 403 |
| [GHSA-86cx-wwf4-phq4](https://github.com/advisories/GHSA-86cx-wwf4-phq4) | extends | Указать путь соседнего каталога с тем же префиксом имени (/base2 при корне /base) и проверить отказ |

### INJ-SQL — SQL-инъекция во входных параметрах не исполняется (RWB-0089, багов: 6)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-f46q-3v67-fmm4](https://github.com/advisories/GHSA-f46q-3v67-fmm4) | extends | Отправить в поле сырого запроса каждого эндпоинта, принимающего SQL, изменяющий оператор и чтение системного каталога и проверить отказ |
| [GHSA-33jq-p8c2-q3q4](https://github.com/advisories/GHSA-33jq-p8c2-q3q4) | covered | _только пруф_: Ровно этот сценарий |
| [GHSA-r8cr-4f9w-7r75](https://github.com/advisories/GHSA-r8cr-4f9w-7r75) | covered | _только пруф_: SQL-инъекция во входном параметре |
| [GHSA-q2vg-7qgx-x5fc](https://github.com/advisories/GHSA-q2vg-7qgx-x5fc) | extends | Сохранить объект с одинарной кавычкой и SQL-фрагментом в названии и выполнить операцию, которая подставляет это название в запрос; проверить, что SQL не исполняется |
| [GHSA-h89q-4j2h-7h88](https://github.com/advisories/GHSA-h89q-4j2h-7h88) | extends | Внедрить в параметр-массив путей UNION SELECT с разрешёнными значениями полей, по которым фильтруется доступ, и проверить, что скрытые записи не возвращаются |
| [GHSA-7q96-f8xw-jv5j](https://github.com/advisories/GHSA-7q96-f8xw-jv5j) | extends | _только пруф_: Инъекция второго порядка через сохранённое значение; вариант уже предложен другим багом партии |

### INJ-SSRF-PARAMETERS — Параметры с URL и хостами не дают доступа к внутренней сети (RWB-0090, багов: 5)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-w98g-5w9p-p3rc](https://github.com/advisories/GHSA-w98g-5w9p-p3rc) | extends | Передать URL с адресами CGNAT (100.64.0.0/10), IPv6 site-local (fec0::/10) и IPv6 перехода, встраивающими 169.254.169.254, и проверить отказ |
| [GHSA-87fv-vqqr-m4jr](https://github.com/advisories/GHSA-87fv-vqqr-m4jr) | extends | Вызвать RPC загрузки по URL без аутентификации с внутренним адресом и проверить отказ и отсутствие ответа цели в сохранённых данных |
| [GHSA-4p3g-4hcj-wpvx](https://github.com/advisories/GHSA-4p3g-4hcj-wpvx) | extends | Передать в параметре-хосте, который сервер подставляет в шаблон исходящего URL, значения с путём, схемой, userinfo, query, fragment и «//внешний.хост» и проверить отказ на валидации |
| [GHSA-r2v3-8gwf-7ghm](https://github.com/advisories/GHSA-r2v3-8gwf-7ghm) | extends | Создать объект с аннотацией адреса внешнего сервиса, указывающей на подконтрольный адрес, и проверить, что сервер туда не обращается и не передаёт токены |
| [GHSA-2wm4-vwp6-v7xc](https://github.com/advisories/GHSA-2wm4-vwp6-v7xc) | extends | _только пруф_: В записи уже есть allowlist для ссылок внутри принятого источника и file:// — только пруф |

### INJ-TEMPLATE-SSTI — Инъекция в серверные шаблоны не исполняется (RWB-0091, багов: 3)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-j8px-rmrx-76h9](https://github.com/advisories/GHSA-j8px-rmrx-76h9) | extends | Отправить в заголовке, подставляемом в шаблон URL, синтаксис плейсхолдера окружения и проверить, что он не раскрывается |
| [GHSA-x67c-8pwr-m8g3](https://github.com/advisories/GHSA-x67c-8pwr-m8g3) | extends | Импортировать данные с шаблонным выражением, вызывающим функцию запроса к БД, отобразить их и проверить, что внедрённый SQL не исполняется |
| [GHSA-pfvc-3p5h-x7h6](https://github.com/advisories/GHSA-pfvc-3p5h-x7h6) | extends | Передать в пользовательскую переменную плейсхолдер чтения конфигурации сервиса ({{config.token}}) и проверить, что секрет не подставляется в результат |

### PRIV-DATA-MASKING — Чувствительные данные маскируются в ответах по политике (RWB-0098, багов: 2)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-8wvg-r2j4-3737](https://github.com/advisories/GHSA-8wvg-r2j4-3737) | extends | Запросить объекты пользователей через каждый эндпоинт, где они встраиваются, и сравнить маскирование email |
| [GHSA-88p2-jj8w-j8qg](https://github.com/advisories/GHSA-88p2-jj8w-j8qg) | extends | Запросить ролью с ограниченным доступом вспомогательные эндпоинты (поиск, подбор целей), возвращающие объект с секретами, и проверить ту же маскировку, что в основных |

### REQ-CROSS-CLIENT-CONSISTENCY — Одно правило продукта одинаково в API разных клиентов (RWB-0099, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-g38j-7v97-x298](https://github.com/advisories/GHSA-g38j-7v97-x298) | extends | Выполнить операцию через альтернативный протокол (CalDAV, WebDAV) и сравнить проверку прав с REST |

### RES-REFERENTIAL-INTEGRITY — Ссылка на несуществующий или чужой связанный ресурс отклоняется (RWB-0104, багов: 4)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-39p5-2wrr-xh29](https://github.com/advisories/GHSA-39p5-2wrr-xh29) | extends | Привязать к своему ресурсу чужую группу пользователей по ID и проверить отказ и отсутствие её состава в ответах |
| [GHSA-w39f-h553-h2mx](https://github.com/advisories/GHSA-w39f-h553-h2mx) | extends | Передать в теле запроса к своему ресурсу ID вспомогательного объекта (представление, колонка) чужого проекта и проверить отказ |
| [GHSA-42cj-m3vj-89wv](https://github.com/advisories/GHSA-42cj-m3vj-89wv) | extends | Сослаться из ресурса другого вида (TCP вместо HTTP) на запрещённый объект другого провайдера или пространства и проверить такой же отказ |
| [GHSA-w7c2-w76w-5hmj](https://github.com/advisories/GHSA-w7c2-w76w-5hmj) | extends | Создать маршрут, зеркалирующий трафик на сервис другого пространства имён без разрешения, и проверить отказ |

### RES-SOFT-DELETE-VISIBILITY — Мягко удалённые ресурсы не видны в обычных операциях (RWB-0298, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-8r7f-r8hj-r3rv](https://github.com/advisories/GHSA-8r7f-r8hj-r3rv) | extends | Заблокировать или деактивировать учётку и проверить, что поиск и списки пользователей её не возвращают, как и чтение по ID |

### REST-MASS-ASSIGNMENT — Mass assignment защищённых полей (RWB-0121, багов: 2)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-569v-q83c-3j3g](https://github.com/advisories/GHSA-569v-q83c-3j3g) | extends | Передать в теле обновления своего объекта поле родителя с ID чужого проекта и проверить, что объект не переносится |
| [GHSA-48p8-g2fx-3wwm](https://github.com/advisories/GHSA-48p8-g2fx-3wwm) | extends | Передать защищённое поле вложенным в разрешённый объект верхнего уровня и проверить, что оно отклоняется или не применяется |

### REST-READONLY-WRITEONLY — Поля readOnly/writeOnly (RWB-0129, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-3r5c-2xxx-h872](https://github.com/advisories/GHSA-3r5c-2xxx-h872) | extends | Задать в вебхуке секретный заголовок авторизации и проверить, что список, чтение и ответ на изменение не содержат его значения |

### REST-REQUEST-SIZE-LIMIT — Лимит размера тела (RWB-0130, багов: 2)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-j3hg-9rp3-5hw9](https://github.com/advisories/GHSA-j3hg-9rp3-5hw9) | extends | Отправить без валидной подписи большое тело на эндпоинт с подписью тела и проверить отказ до приёма всего тела и отсутствие временных файлов |
| [GHSA-v828-m3pf-vq9q](https://github.com/advisories/GHSA-v828-m3pf-vq9q) | extends | Отправить на публичный эндпоинт вебхука тело больше лимита с неверной подписью и проверить 413 и отсутствие тела в логах |

### REST-SENSITIVE-DATA — Отсутствие чувствительных данных в ответах (RWB-0133, багов: 2)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-32gc-wf3m-78w9](https://github.com/advisories/GHSA-32gc-wf3m-78w9) | covered | _только пруф_: Секрет в ответе API |
| [GHSA-6x2c-phff-wx57](https://github.com/advisories/GHSA-6x2c-phff-wx57) | covered | _только пруф_: Учётные данные в ответе API |

### REST-SORT-INVALID-FIELD — Сортировка по неизвестному полю (RWB-0134, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-rxhg-vcww-2mpw](https://github.com/advisories/GHSA-rxhg-vcww-2mpw) | extends | Передать в параметре сортировки имя столбца, которого нет в ответе, и SQL-выражение и проверить 400 |

### REST-SSRF-URL-FETCH — Контроль server-side URL fetch (RWB-0135, багов: 4)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-x8gv-g2g3-65fj](https://github.com/advisories/GHSA-x8gv-g2g3-65fj) | extends | Передать домен с чередующимся резолвом во внешний и внутренний адрес (DNS rebinding) и проверить, что запрос во внутреннюю сеть не выполняется |
| [GHSA-jvh5-97xg-v99f](https://github.com/advisories/GHSA-jvh5-97xg-v99f) | extends | Передать URL, хост которого резолвится в IPv6-обёртку внутреннего IPv4 (NAT64, IPv4-compatible, 6to4), и проверить отказ |
| [GHSA-jgh3-fggc-mcpm](https://github.com/advisories/GHSA-jgh3-fggc-mcpm) | covered | _только пруф_: Ровно этот сценарий |
| [GHSA-pqqc-8v73-9gg2](https://github.com/advisories/GHSA-pqqc-8v73-9gg2) | covered | _только пруф_: Ровно этот сценарий |

### SEC-AUTHN-MALFORMED — Malformed credential is rejected (RWB-0142, багов: 3)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-xwwr-4h3p-r22c](https://github.com/advisories/GHSA-xwwr-4h3p-r22c) | extends | Подписать запрос для произвольного ключа доступа пустым секретом и проверить отказ |
| [GHSA-5fqm-cc34-fcf5](https://github.com/advisories/GHSA-5fqm-cc34-fcf5) | covered | _только пруф_: Некорректные учётные данные принимаются |
| [GHSA-c3jm-gv5r-9wcp](https://github.com/advisories/GHSA-c3jm-gv5r-9wcp) | extends | Подставить в токен сессии верный ID сессии с произвольной секретной частью и проверить отказ |

### SEC-AUTHN-MISSING — Protected operation rejects missing credentials (RWB-0143, багов: 5)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-rqcc-94gv-wjm9](https://github.com/advisories/GHSA-rqcc-94gv-wjm9) | extends | Вызвать защищённые маршруты без учётных данных на установке с настройками по умолчанию (пустой секрет подписи) и проверить 401 |
| [GHSA-p378-jp5r-gpgw](https://github.com/advisories/GHSA-p378-jp5r-gpgw) | extends | _только пруф_: Тот же вариант, что у GHSA-rqcc-94gv-wjm9 этой пачки (пустой секрет по умолчанию) — только пруф |
| [GHSA-pr6h-vr44-xq8j](https://github.com/advisories/GHSA-pr6h-vr44-xq8j) | extends | При включённой аутентификации запросить без учётных данных маршруты каждого верхнеуровневого префикса и проверить 401 |
| [GHSA-p569-5gjg-9cmj](https://github.com/advisories/GHSA-p569-5gjg-9cmj) | extends | Запустить сервер через API управления с опцией аутентификации и проверить, что анонимный вход отклоняется |
| [GHSA-r277-6w6q-xmqw](https://github.com/advisories/GHSA-r277-6w6q-xmqw) | extends | Отправить без учётных данных запрос к каждой операции, у которой в спецификации задан security, и проверить 401 |

### SEC-AUTHZ-METHOD-MATRIX — Authorization is enforced for every method (RWB-0147, багов: 21)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-xp3c-3jw3-4vcr](https://github.com/advisories/GHSA-xp3c-3jw3-4vcr) | extends | Запретить подпуть с завершающим wildcard при разрешённом списке на родительском пути, выполнить LIST по подпути и проверить отказ |
| [GHSA-fmmf-xq98-g327](https://github.com/advisories/GHSA-fmmf-xq98-g327) | extends | Участником с правом записи удалить объект повышенного уровня, который он не может создать, и проверить отказ и сохранность объекта |
| [GHSA-4vpg-gwqq-w44c](https://github.com/advisories/GHSA-4vpg-gwqq-w44c) | extends | Пройти все эндпоинты чтения одного ресурса (текст, метаданные, ссылки, существование) ролью без доступа к объекту и проверить единый отказ |
| [GHSA-9cqf-hhrq-7v45](https://github.com/advisories/GHSA-9cqf-hhrq-7v45) | extends | _только пруф_: Тот же вариант, что у GHSA-4vpg-gwqq-w44c этой партии |
| [GHSA-j4ph-9xwf-wcj4](https://github.com/advisories/GHSA-j4ph-9xwf-wcj4) | extends | Ролью с ограниченным доступом запросить агрегаты (уникальные метки, счётчики) и проверить, что значения недоступных объектов не входят |
| [GHSA-53fp-9jmv-227g](https://github.com/advisories/GHSA-53fp-9jmv-227g) | extends | _только пруф_: Тот же вариант, что у GHSA-4vpg-gwqq-w44c этой партии |
| [GHSA-74pj-6g7r-j55c](https://github.com/advisories/GHSA-74pj-6g7r-j55c) | extends | _только пруф_: Тот же вариант, что у GHSA-4vpg-gwqq-w44c этой партии |
| [GHSA-57v5-wqx3-cgj4](https://github.com/advisories/GHSA-57v5-wqx3-cgj4) | extends | _только пруф_: Тот же вариант, что у GHSA-4vpg-gwqq-w44c этой партии |
| [GHSA-mp7r-57w4-5qm3](https://github.com/advisories/GHSA-mp7r-57w4-5qm3) | extends | _только пруф_: Тот же вариант, что у GHSA-j4ph-9xwf-wcj4 этой партии |
| [GHSA-f2rw-w22v-54vh](https://github.com/advisories/GHSA-f2rw-w22v-54vh) | extends | _только пруф_: Тот же вариант, что у GHSA-4vpg-gwqq-w44c этой партии |
| [GHSA-5w7r-f4cg-rqq7](https://github.com/advisories/GHSA-5w7r-f4cg-rqq7) | extends | _только пруф_: Соседние эндпоинты одного ресурса фильтруют доступ, служебные — нет; вариант «пройти все эндпоинты чтения» уже есть у бага прошлой пачки |
| [GHSA-5fhr-f75j-8wr9](https://github.com/advisories/GHSA-5fhr-f75j-8wr9) | extends | _только пруф_: Парный эндпоинт фильтрует, вариант по ID — нет; тот же механизм, вариант уже есть |
| [GHSA-qvq9-hq6p-v378](https://github.com/advisories/GHSA-qvq9-hq6p-v378) | extends | _только пруф_: Один из эндпоинтов чтения ресурса без фильтра; вариант уже есть |
| [GHSA-vpjw-wf5h-cgpq](https://github.com/advisories/GHSA-vpjw-wf5h-cgpq) | extends | Повторить проверку каждого эндпоинта чтения для объектов каждого уровня защиты (скрыт, запрещён к публикации, защищён паролем без ввода пароля) |
| [GHSA-67x2-mq63-v9vm](https://github.com/advisories/GHSA-67x2-mq63-v9vm) | extends | _только пруф_: Тот же механизм — часть эндпоинтов чтения без фильтра; вариант уже есть |
| [GHSA-6mcf-g667-w3qv](https://github.com/advisories/GHSA-6mcf-g667-w3qv) | extends | _только пруф_: Пропущен уровень защиты паролем в одном фильтре; вариант по уровням защиты — у другого бага партии |
| [GHSA-pm3w-vxp9-ccwc](https://github.com/advisories/GHSA-pm3w-vxp9-ccwc) | extends | _только пруф_: Соседний эндпоинт фильтрует, этот — нет; вариант уже есть |
| [GHSA-36v8-mpjm-8j5r](https://github.com/advisories/GHSA-36v8-mpjm-8j5r) | extends | _только пруф_: Список и содержимое одного ресурса фильтруются по-разному; вариант уже есть |
| [GHSA-69mh-gvh4-8gp7](https://github.com/advisories/GHSA-69mh-gvh4-8gp7) | extends | Вызвать ролью читателя эндпоинты, которые рассчитывают изменение без применения (предпросмотр транзакции), и проверить, что в ответе нет содержимого недоступных объектов |
| [GHSA-jm28-2wcr-qf3h](https://github.com/advisories/GHSA-jm28-2wcr-qf3h) | extends | Запустить действие синхронным методом «запустить и дождаться» пользователем с правом запуска без права чтения результата и проверить, что вывод не возвращается |
| [GHSA-xg4h-6gfc-h4m8](https://github.com/advisories/GHSA-xg4h-6gfc-h4m8) | extends | Пользователем с правом чтения одного ключа открыть подписку на изменения с открытым диапазоном и проверить отказ или события только по разрешённому ключу |

### SEC-AUTHZ-REVOKE-ROLE — Role revocation takes effect within policy window (RWB-0299, багов: 3)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-hjx8-qv73-f7cm](https://github.com/advisories/GHSA-hjx8-qv73-f7cm) | extends | Удалить участника из проекта всеми способами (из проекта, из команды, удаление команды) и проверить, что его вебхуки и ссылки-доступа больше не отдают данные |
| [GHSA-w6p7-2fxx-4f44](https://github.com/advisories/GHSA-w6p7-2fxx-4f44) | extends | Отозвать согласие клиента, отключить пользователя и исключить его из разрешённой группы, затем обновить токен по refresh-токену и проверить отказ в каждом случае |
| [GHSA-q423-49rw-g9mh](https://github.com/advisories/GHSA-q423-49rw-g9mh) | extends | Сделать публичный ресурс приватным через API и проверить, что подписки и списки пользователей без доступа его больше не возвращают |

### SEC-CLONE-FIELD-PERMISSIONS — Копирование ресурса соблюдает полевые права чтения и создания (RWB-0047, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-f27p-pw2p-9pr4](https://github.com/advisories/GHSA-f27p-pw2p-9pr4) | extends | Скопировать доступный ресурс в чужой родительский контейнер без права записи в него и проверить отказ, как при обычном создании |

### SEC-CONFUSED-DEPUTY — Действия во внешней системе от имени пользователя выполняются только с его правами (RWB-0043, багов: 3)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-79gf-7frw-68m9](https://github.com/advisories/GHSA-79gf-7frw-68m9) | extends | Создать в своём пространстве имён политику или шаблон, порождающий ресурсы в чужом пространстве, и проверить отказ |
| [GHSA-6f2p-296r-cc28](https://github.com/advisories/GHSA-6f2p-296r-cc28) | extends | Сослаться из ресурса своего репозитория на файл приватного репозитория той же установки интеграции и проверить, что сервис его не загружает |
| [GHSA-jr6p-8pjj-mfx6](https://github.com/advisories/GHSA-jr6p-8pjj-mfx6) | extends | Передать объект, недоступный пользователю, через каждый путь описания ресурсов для контроллера и проверить, что он не создаётся правами контроллера |

### SEC-FAIL-CLOSED-INPUT — Неожиданный тип, пустое или отсутствующее поле проверки безопасности ведёт к отказу, а не к пропуску проверки (RWB-0006, багов: 6)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-hrxh-6v49-42gf](https://github.com/advisories/GHSA-hrxh-6v49-42gf) | extends | Настроить политику доступа с неподдерживаемым условием, в том числе под NOT и в составном правиле, и проверить, что запросы, которые она должна запрещать, отклоняются |
| [GHSA-fprf-r6rv-xg99](https://github.com/advisories/GHSA-fprf-r6rv-xg99) | extends | Пользователем без доступных проектов выполнить операцию, строящую выборку по его проектам, с пустым фильтром и проверить, что чужие объекты не возвращаются и не изменяются |
| [GHSA-6r3q-mjv7-xr8m](https://github.com/advisories/GHSA-6r3q-mjv7-xr8m) | extends | Отправить запрос с числом параметров сверх лимита фильтра и вредоносным значением среди них и проверить отказ, а не пропуск без проверки |
| [GHSA-5gpm-rgj3-9q76](https://github.com/advisories/GHSA-5gpm-rgj3-9q76) | extends | Отправить тело больше лимита проверки без Content-Length (chunked, HTTP/2) и проверить отказ политики, зависящей от тела |
| [GHSA-v684-q882-jgmq](https://github.com/advisories/GHSA-v684-q882-jgmq) | extends | Ролью читателя запросить объект, не упомянутый в правилах доступа, и проверить отказ |
| [GHSA-44v6-7fxq-vgf4](https://github.com/advisories/GHSA-44v6-7fxq-vgf4) | extends | Передать в поле ссылки на родителя нулевое значение (отвязка к корню) пользователем без нужных прав и проверить, что проверка прав не пропускается |

### SEC-IDENTITY-PROOF-OF-POSSESSION — Заявленная клиентом идентичность без доказательства владения не даёт прав и льгот (RWB-0042, багов: 3)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-w3rp-4cm2-4wgc](https://github.com/advisories/GHSA-w3rp-4cm2-4wgc) | extends | Привязать к своей учётке чужой идентификатор счёта без подтверждения его владельца и выполнить списание с этого счёта |
| [GHSA-cp3j-m783-3ph5](https://github.com/advisories/GHSA-cp3j-m783-3ph5) | extends | Завершить подключение внешней интеграции с чужим ID установки и проверить отказ |
| [GHSA-jq8w-8q2f-ffm9](https://github.com/advisories/GHSA-jq8w-8q2f-ffm9) | extends | Изменить свой email или телефон с запросом возврата кода подтверждения в ответе и проверить, что код не возвращается без отдельного права |

### SEC-OWNERSHIP-DELETE — User cannot delete another owner’s resource (RWB-0149, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-gg93-x632-9ccv](https://github.com/advisories/GHSA-gg93-x632-9ccv) | extends | Удалить через путь своего проекта объект с ID чужого проекта и проверить 404 и сохранность связанных данных чужого проекта |

### SEC-OWNERSHIP-REFERENCE-INDIRECT — Indirect resource references preserve authorization (RWB-0151, багов: 12)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-w2ch-4xgr-22ww](https://github.com/advisories/GHSA-w2ch-4xgr-22ww) | extends | Удалить связь своего объекта с объектом недоступного проекта и проверить отказ и сохранность связи у второй стороны |
| [GHSA-3hc7-r24j-rpwc](https://github.com/advisories/GHSA-3hc7-r24j-rpwc) | extends | Запросить список с раскрытием связанных объектов (expand) и проверить, что объекты недоступных проектов, включая вложенные уровни, не возвращаются |
| [GHSA-52gf-6rpq-fgmx](https://github.com/advisories/GHSA-52gf-6rpq-fgmx) | extends | Указать в запросе свой проект и имя объекта чужого проекта для действия над ним и проверить отказ |
| [GHSA-qq9q-x9w4-chhj](https://github.com/advisories/GHSA-qq9q-x9w4-chhj) | extends | Сослаться по имени на объект в ресурсе с межпространственной ссылкой и проверить, что имя разрешается в пространстве ссылающегося ресурса |
| [GHSA-rj9j-8772-4h6c](https://github.com/advisories/GHSA-rj9j-8772-4h6c) | extends | Запросить данные своего проекта, подставив в путь ID вложенного объекта чужого проекта, и проверить отказ без его данных |
| [GHSA-vg99-7gj7-2fr5](https://github.com/advisories/GHSA-vg99-7gj7-2fr5) | extends | Ролью без пароля документа запросить обратные ссылки на открытый объект и проверить, что ссылки из защищённых документов не возвращаются |
| [GHSA-4227-9989-jrhx](https://github.com/advisories/GHSA-4227-9989-jrhx) | extends | Создать объект со ссылкой на секрет, к которому нет права чтения, и проверить отказ |
| [GHSA-h6w7-xxcf-w2mq](https://github.com/advisories/GHSA-h6w7-xxcf-w2mq) | extends | Запросить доступный объект, встраивающий содержимое других объектов, и проверить, что содержимое недоступных объектов не возвращается |
| [GHSA-mfrj-v65r-979c](https://github.com/advisories/GHSA-mfrj-v65r-979c) | extends | _только пруф_: Тот же вариант, что у GHSA-h6w7-xxcf-w2mq этой партии |
| [GHSA-c9f5-j9c3-mhrg](https://github.com/advisories/GHSA-c9f5-j9c3-mhrg) | extends | Создать ресурс копированием, указав в источнике ресурс недоступного проекта, и проверить отказ |
| [GHSA-64f3-v33m-w89f](https://github.com/advisories/GHSA-64f3-v33m-w89f) | extends | _только пруф_: Та же ссылка на чужой источник копирования, что у другого бага партии; вариант уже предложен |
| [GHSA-62fc-8686-hfmq](https://github.com/advisories/GHSA-62fc-8686-hfmq) | extends | Повторить ссылку на ресурс другого пространства имён для каждого типа ссылок конфигурации и проверить единый отказ |

### SEC-OWNERSHIP-UPDATE — User cannot modify another owner’s resource (RWB-0152, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-5pg6-m483-7vrg](https://github.com/advisories/GHSA-5pg6-m483-7vrg) | extends | Передать в теле операции над своим контейнером ID чужого объекта и проверить отказ и отсутствие его данных в ответе |

### SEC-READONLY-MODE-ENFORCED — Режим только для чтения запрещает изменения любым запросом, а не по первому ключевому слову (RWB-0028, багов: 2)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-wgwx-479j-23vq](https://github.com/advisories/GHSA-wgwx-479j-23vq) | extends | Вызвать ролью читателя служебную операцию пересчёта (индексов, ссылок) и проверить отказ и отсутствие записей в хранилище |
| [GHSA-hq33-8jgp-8qq3](https://github.com/advisories/GHSA-hq33-8jgp-8qq3) | extends | При запрете удаления выполнить MOVE файла и MOVE с перезаписью существующего и проверить 403 и сохранность файлов |

### SEC-ROLE-LOW-TO-HIGH — Low-privilege role cannot perform privileged action (RWB-0247, багов: 2)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-hgpf-8634-g44c](https://github.com/advisories/GHSA-hgpf-8634-g44c) | extends | Вызвать операции управления смежного API (другой сервис подписи, каталог) учёткой только с правом чтения объектов и проверить отказ |
| [GHSA-p845-629j-rcj6](https://github.com/advisories/GHSA-p845-629j-rcj6) | extends | Администратором низшего уровня вызвать сброс фактора защиты (passkey, 2FA) у пользователя того же и более высокого уровня и проверить отказ |

### SEC-ROLE-SELF-ASSIGN — User cannot grant self a higher role (RWB-0153, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-gfjv-gqf2-c888](https://github.com/advisories/GHSA-gfjv-gqf2-c888) | extends | Включить в участники субъект другого вида (группа, сервисный аккаунт, «все аутентифицированные») без права управления участниками и проверить отказ |

### SEC-SCOPE-EXTRA-UNTRUSTED — Client cannot add scopes by request parameter (RWB-0154, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-vrh8-c9cm-wh8v](https://github.com/advisories/GHSA-vrh8-c9cm-wh8v) | extends | Обменять токен через token exchange на токен другого приложения с более широкими scope и проверить отказ |

### SEC-SCOPE-MISSING — Token without required scope is denied (RWB-0155, багов: 6)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-9rg3-v78m-26q8](https://github.com/advisories/GHSA-9rg3-v78m-26q8) | extends | Запросить ресурс токеном с узким scope и параметром expand, встраивающим данные других групп прав, и проверить их отсутствие |
| [GHSA-qg67-7m6v-qg25](https://github.com/advisories/GHSA-qg67-7m6v-qg25) | extends | Отправить DELETE токеном со scope записи без права удаления и проверить отказ |
| [GHSA-fq2p-5p22-8g6j](https://github.com/advisories/GHSA-fq2p-5p22-8g6j) | extends | Токеном с ограничением «только публичные ресурсы» запросить списочные эндпоинты и эндпоинты прав своего аккаунта и проверить отсутствие приватных объектов |
| [GHSA-w89x-c962-c44g](https://github.com/advisories/GHSA-w89x-c962-c44g) | extends | Токеном только со scope чтения вызвать каждую операцию с побочным эффектом (отправка письма, проверка подключения) и проверить отказ |
| [GHSA-v6w6-358x-2433](https://github.com/advisories/GHSA-v6w6-358x-2433) | extends | Вызвать токеном только со scope чтения операции, выполняющие действия (тест подключения, исходящий запрос), и проверить отказ |
| [GHSA-hq88-5x99-x3gf](https://github.com/advisories/GHSA-hq88-5x99-x3gf) | covered | _только пруф_: Запись проверяет ровно это: валидный токен без нужного scope на операции |

### SEC-TENANT-HEADER-SPOOF — Untrusted tenant header cannot override identity context (RWB-0300, багов: 2)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-cjgj-2fwf-4c2w](https://github.com/advisories/GHSA-cjgj-2fwf-4c2w) | extends | Запросить ресурсы своего проекта с query-параметром другого проекта и проверить, что чужие данные не возвращаются |
| [GHSA-2rx5-2g7j-2659](https://github.com/advisories/GHSA-2rx5-2g7j-2659) | extends | Отправить заголовки идентичности forward-auth по каждому пути прокси, включая ветки обхода аутентификации, и проверить, что backend их не получает |

### SEC-TENANT-READ — Tenant A cannot read tenant B data (RWB-0157, багов: 5)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-p5vg-v7mj-f6q4](https://github.com/advisories/GHSA-p5vg-v7mj-f6q4) | extends | Запросить объект чужого арендатора по ID через путь своего родительского ресурса и проверить 404 |
| [GHSA-gv5w-hfx8-8cwq](https://github.com/advisories/GHSA-gv5w-hfx8-8cwq) | extends | Запросить токеном, ограниченным префиксом пути арендатора, соседние пути с тем же началом (/tenant1234, /tenant1-old) и проверить отказ |
| [GHSA-992g-9cr3-vm5x](https://github.com/advisories/GHSA-992g-9cr3-vm5x) | covered | _только пруф_: Чтение данных другого арендатора |
| [GHSA-9q4h-f4x5-ffq8](https://github.com/advisories/GHSA-9q4h-f4x5-ffq8) | extends | Зарегистрировать в стриме ID задачи другого арендатора и проверить, что после отказа проверки владения результаты этой задачи в стрим не приходят |
| [GHSA-g26x-m427-f48f](https://github.com/advisories/GHSA-g26x-m427-f48f) | covered | _только пруф_: Ровно этот сценарий |

### SEC-TENANT-SEARCH — Tenant filter cannot be bypassed in list/search (RWB-0158, багов: 3)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-p6ph-3jx2-3337](https://github.com/advisories/GHSA-p6ph-3jx2-3337) | extends | Выполнить поиск пользователем с ограниченной областью и проверить, что общее число результатов считается только по доступным ему объектам |
| [GHSA-w8x7-h2px-xmq8](https://github.com/advisories/GHSA-w8x7-h2px-xmq8) | extends | Подписаться на поток событий по общему доступу к одному файлу, изменить соседние неразделённые объекты владельца и проверить, что события о них не приходят |
| [GHSA-frpw-3h2q-4jj6](https://github.com/advisories/GHSA-frpw-3h2q-4jj6) | extends | Запросить список на уровне организации и проверить, что он не содержит элементов из дочерних объектов, к которым у пользователя нет доступа |

### SEC-TENANT-WRITE — Tenant A cannot mutate tenant B data (RWB-0159, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-8x7x-83cf-c3pg](https://github.com/advisories/GHSA-8x7x-83cf-c3pg) | extends | Вызвать gRPC-методы служебного сервиса (метки, отписка воркера) с ID объекта другого тенанта в теле и проверить PERMISSION_DENIED или NOT_FOUND |

### SEC-TOKEN-AUDIENCE — Token for another audience is rejected (RWB-0160, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-xwmw-prc4-v3cr](https://github.com/advisories/GHSA-xwmw-prc4-v3cr) | covered | _только пруф_: Токен чужой аудитории |

### VAL-CASE-SENSITIVITY — Чувствительность к регистру идентификаторов, email и enum соответствует контракту (RWB-0164, багов: 2)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-328g-jx67-v94g](https://github.com/advisories/GHSA-328g-jx67-v94g) | extends | Отправить запрос с именем хоста в смешанном регистре и проверить, что правило доступа приложения применяется |
| [GHSA-qc2q-p7wx-3px3](https://github.com/advisories/GHSA-qc2q-p7wx-3px3) | extends | Настроить запрещающее правило по заголовку с именем в смешанном регистре, отправить запрос с этим заголовком и проверить отказ |

### VAL-LARGE-COLLECTION-PAYLOAD — Массив с очень большим числом элементов отклоняется или обрабатывается в пределах лимитов (RWB-0169, багов: 3)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-pqf9-h8g4-8gmh](https://github.com/advisories/GHSA-pqf9-h8g4-8gmh) | extends | Загрузить CSV в пределах лимита размера с миллионами крошечных строк и проверить лимит по числу строк |
| [GHSA-4jfq-pmq9-257h](https://github.com/advisories/GHSA-4jfq-pmq9-257h) | covered | _только пруф_: Ровно этот сценарий |
| [GHSA-xhj3-7xw9-vr34](https://github.com/advisories/GHSA-xhj3-7xw9-vr34) | extends | Передать в query-параметре массива элемент с огромным индексом (param[items][50000000]=x) и проверить быстрый 4xx без роста памяти |

### WS-MESSAGE-LIMITS — Размер и частота сообщений ограничены (RWB-0205, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-4fwh-wrm6-97xm](https://github.com/advisories/GHSA-4fwh-wrm6-97xm) | extends | Открыть много WebSocket-соединений с одного IP и подписаться на неограниченный список объектов, проверить лимиты соединений и размера подписки |

### WS-ORIGIN-CHECK — Проверка Origin защищает от cross-site WebSocket hijacking (RWB-0301, багов: 2)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-3cc2-h3v6-rqpq](https://github.com/advisories/GHSA-3cc2-h3v6-rqpq) | covered | _только пруф_: Ровно этот сценарий |
| [GHSA-8r62-w5wh-fc5m](https://github.com/advisories/GHSA-8r62-w5wh-fc5m) | extends | Отправить upgrade на путь WebSocket с процентно-закодированными символами (/%61pi/events) и чужим Origin и проверить отказ |

### WS-SUBSCRIPTION-AUTHZ — Подписки и сообщения авторизуются по каждому каналу (RWB-0179, багов: 2)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-xcw9-qmmf-vqxj](https://github.com/advisories/GHSA-xcw9-qmmf-vqxj) | extends | Подписаться на поток событий пользователем с ограничивающим фильтром и проверить фильтрацию каждого типа сообщений потока |
| [GHSA-mw8r-mw84-88v2](https://github.com/advisories/GHSA-mw8r-mw84-88v2) | extends | Держать открытым WebSocket-соединение ролью читателя, изменить недоступный ему объект от другого пользователя и проверить, что событие с его содержимым не приходит |

### WS-TOKEN-EXPIRY — Истечение или отзыв токена учитывается в открытом соединении (RWB-0302, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [GHSA-4hv6-xc92-j86g](https://github.com/advisories/GHSA-4hv6-xc92-j86g) | extends | Отозвать сессию и открыть новое WebSocket-соединение с токеном этой сессии — проверить отказ при аутентификации |

