# Кандидаты из баг-трекеров: партия `kubernetes`

Сгенерировано `tools/mining/cluster.py` из `build/mining/<batch>/batches/*.out.jsonl` и
`ideas/mined/kubernetes.review.yaml` — правки решений делаются в review-файле, затем пересборка.
План — `docs/BUG_MINING_PLAN.md`, шаги 6–7; применение — `tools/mining/apply_proofs.py`.

## Сводка

- Новых паттернов: 13 → идей: 12 (принять: 12, отклонить: 0, не решено: 0).
- Пруфы к существующим: 28 багов → 21 записей; новых шагов-вариантов: 26.

## Новые идеи

Принятые становятся записями `status: draft` с меткой `real-world-bug` и ссылкой на RWB.

| # | Решение | Запись / файл | Идея | Подтверждающие баги |
|---|---|---|---|---|
| 1 | accept | `HTTP-HEADER-REPEATED-LINES-ACCEPTED` (RWB-0217)<br>`checks/rest/http-protocol.yaml` | Законный запрос с сотнями повторяющихся строк одного заголовка (группы при имперсонации, от аутентифицирующего прокси) в пределах лимита размера обслуживается одинаково по HTTP/1.1 и HTTP/2; лимит числа строк, если есть, задокументирован, а отказ попадает в аудит или лог; позитивная пара к HTTP-HEADER-SIZE-LIMIT | [kubernetes/kubernetes#142606](https://github.com/kubernetes/kubernetes/issues/142606) |
| 2 | accept | `SEC-AUTHZ-FALLBACK-PATH` (RWB-0218)<br>`checks/security/access-control/SEC-AUTHZ-FALLBACK-PATH.yaml` | Если право выводится двумя путями (по цепочке связанных объектов или явным правом в авторизаторе), ошибка основного пути (связанный объект не найден) не отменяет запасной — решение по явному праву, без права — 403 с причиной; ни fail-open, ни ложного отказа | [kubernetes/kubernetes#140159](https://github.com/kubernetes/kubernetes/issues/140159) |
| 3 | accept | `RESIL-DEPENDENCY-TLS-RECOVERY` (RWB-0219)<br>`checks/common/resilience.yaml` | Проверка доступности внешнего бэкенда проверяет его сертификат (с заданным CA, без пропуска проверки TLS) и сама восстанавливается, когда на адрес вернулся настоящий бэкенд, — без перезапуска сервиса | [kubernetes/kubernetes#135883](https://github.com/kubernetes/kubernetes/issues/135883) |
| 4 | accept | `RESIL-TLS-CERT-RELOAD` (RWB-0220)<br>`checks/common/resilience.yaml` | Сервер подхватывает заменённые файлы TLS-сертификата и ключа (внешняя ротация) без перезапуска; после истечения старого сертификата соединения успешны; нужен доступ к файлам сертификата на стенде | [kubernetes/kubernetes#133001](https://github.com/kubernetes/kubernetes/issues/133001) |
| 5 | accept | `COMPAT-UPGRADE-STORED-DATA-STABLE` (RWB-0221)<br>`checks/common/compatibility.yaml` | Обновление сервера, в том числе поэтапное (старая и новая версии работают одновременно), не меняет сохранённые объекты без действий пользователя — ревизии не растут, производные действия не запускаются, общий служебный объект не перезаписывается версиями по кругу; нужна возможность развернуть две версии | [kubernetes/kubernetes#134773](https://github.com/kubernetes/kubernetes/issues/134773), [kubernetes/kubernetes#128986](https://github.com/kubernetes/kubernetes/issues/128986) |
| 6 | accept | `VAL-UPLOADED-SCHEMA-FORMATS` (RWB-0222)<br>`checks/rest/input-validation.yaml` | API, принимающий от клиента схемы данных (пользовательские типы, JSON Schema, OpenAPI), принимает все документированные форматы (int32, int64, float, double и т. п.) без ложных предупреждений в заголовке Warning и теле ответа | [kubernetes/kubernetes#133880](https://github.com/kubernetes/kubernetes/issues/133880) |
| 7 | accept | `OBS-CONFIG-ENDPOINT-ACCURATE` (RWB-0223)<br>`checks/common/observability.yaml` | Служебный эндпоинт текущей конфигурации (флаги запуска, flagz, configz, env) отражает фактически переданные значения; доступ к нему — по HARD-DEBUG-ENDPOINTS | [kubernetes/kubernetes#129994](https://github.com/kubernetes/kubernetes/issues/129994) |
| 8 | accept | `PERF-NO-UNNEEDED-DEPENDENCY-CALLS` (RWB-0224)<br>`checks/common/performance.yaml` | Внешняя зависимость (вебхук преобразования, валидации, обогащения) вызывается только тогда, когда её результат нужен; лишних вызовов по счётчику на заглушке нет | [kubernetes/kubernetes#129979](https://github.com/kubernetes/kubernetes/issues/129979) |
| 9 | accept | `COMPAT-LEGACY-FORM-PARITY` (RWB-0225)<br>`checks/common/compatibility.yaml` | Ресурс, заданный в устаревшей форме и переведённый на новую реализацию (migration), обрабатывается теми же правилами — права, выдача токенов, ограничения, — что и ресурс в новой форме | [kubernetes/kubernetes#129935](https://github.com/kubernetes/kubernetes/issues/129935) |
| 10 | accept | `VAL-TIGHTENED-RULES-STORED-DATA` (RWB-0226)<br>`checks/rest/input-validation.yaml` | После ужесточения правил валидации сохранённые ранее значения, которые им не соответствуют, обрабатываются одинаково на всех путях записи (основной эндпоинт, подресурс status, PATCH/PUT) — по документированному правилу (не перепроверять неизменённое или требовать исправления), без расхождения между путями | [kubernetes/kubernetes#129503](https://github.com/kubernetes/kubernetes/issues/129503) |
| 11 | accept | `AUTH-IDENTITY-ATTRIBUTES-ALL-SCHEMES` (RWB-0227)<br>`checks/security/authentication-session.yaml` | Идентичность содержит одинаковый набор атрибутов (UID, группы, extra) при любом способе аутентификации, если источник их содержит (UID из сертификата X.509, claims OIDC); сравнение через «кто я»; пара к AUTH-ACCOUNT-STATE-ALL-SCHEMES | [kubernetes/kubernetes#127860](https://github.com/kubernetes/kubernetes/issues/127860) |
| 12 | accept | `RES-ALLOCATED-VALUE-RELEASE` (RWB-0228)<br>`checks/common/resource-lifecycle.yaml` | Значение, выделенное объекту из пула (адрес, номер, уникальное имя), не выдаётся повторно, пока прежний владелец не удалён окончательно (отложенное удаление, финализаторы, мягкое удаление); дублей нет | [kubernetes/kubernetes#127792](https://github.com/kubernetes/kubernetes/issues/127792) |

## Пруфы к существующим

Запись получает метку `real-world-bug` и `Real-world bug: RWB-NNNN`; статус не меняется. Для `extends`
текст варианта добавляется шагом (`steps[].action`, в `notes` — RWB). Неверное совпадение — ID бага в
`proofs.exclude`, вариант без нового шага — в `proofs.no_variant`.

### ASYNC-JOB-LIFECYCLE — Фоновая задача проходит статусы и отдаёт результат (RWB-0052, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [kubernetes/kubernetes#140561](https://github.com/kubernetes/kubernetes/issues/140561) | extends | Удалить целевой тип ресурса, пока фоновая задача ожидает выполнения, и проверить, что задача переходит в статус ошибки, а остальные фоновые задачи продолжают обрабатываться |

### HARD-EXPENSIVE-OPERATION-LIMITS — Дорогие операции ограничены по ресурсам (RWB-0077, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [kubernetes/kubernetes#134580](https://github.com/kubernetes/kubernetes/issues/134580) | extends | Открыть много подписок на изменения без resourceVersion на большую коллекцию и проверить, что ограничитель учитывает их начальную выгрузку как дорогую операцию |

### OBS-AUDIT-TRAIL — Чувствительные действия фиксируются в журнале аудита (RWB-0092, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [kubernetes/kubernetes#135684](https://github.com/kubernetes/kubernetes/issues/135684) | extends | Выполнить запрос дольше порога медленного запроса и проверить, что его событие аудита содержит аннотации общей задержки и задержки по компонентам |

### OBS-HEALTH-ENDPOINTS — Health-эндпоинты отражают состояние и не раскрывают детали (RWB-0093, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [kubernetes/kubernetes#129417](https://github.com/kubernetes/kubernetes/issues/129417) | extends | Сделать недоступным дополнительное хранилище части ресурсов и проверить, что health- и ready-эндпоинты сообщают о неисправности |

### PERF-LATENCY-BASELINE — Задержка ключевых операций в пределах SLO при обычной нагрузке (RWB-0096, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [kubernetes/kubernetes#133600](https://github.com/kubernetes/kubernetes/issues/133600) | covered | _только пруф_: Регрессия задержки ключевой операции относительно SLO — ровно эта запись |

### RES-CACHE-KEY-COMPLETENESS — Серверный кэш различает ответы по всем значимым параметрам и по типу ресурса (RWB-0023, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [kubernetes/kubernetes#132802](https://github.com/kubernetes/kubernetes/issues/132802) | extends | Удалить и пересоздать учётную запись с тем же именем, запросить токен и проверить, что кэш выдаёт новый токен, а не токен прежней учётки |

### RES-DELETE-WITH-DEPENDENTS — Удаление ресурса с зависимыми объектами выполняется по правилам каскада (RWB-0102, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [kubernetes/kubernetes#136890](https://github.com/kubernetes/kubernetes/issues/136890) | extends | Удалить владельца, у которого сервер автоматически создал зависимые объекты, и проверить, что ссылка на владельца в них разрешается и зависимые удаляются |

### RES-READ-AFTER-WRITE — Чтение после записи соответствует модели согласованности (RWB-0229, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [kubernetes/kubernetes#135352](https://github.com/kubernetes/kubernetes/issues/135352) | extends | Создать родительский контейнер и сразу создать в нём объект, подпадающий под политику допуска, повторив много раз, и проверить отсутствие ложного 404 |

### RES-SERVER-GENERATED-FIELDS — Клиент не может задать серверные поля (id, createdAt, status, version) (RWB-0105, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [kubernetes/kubernetes#133388](https://github.com/kubernetes/kubernetes/issues/133388) | extends | Создать объект с заданной меткой удаления через серверное применение и через PUT несуществующего объекта и проверить, что сервер её отбрасывает |

### RESIL-DEPENDENCY-DOWN — Недоступность зависимости даёт контролируемую ошибку (RWB-0107, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [kubernetes/kubernetes#130690](https://github.com/kubernetes/kubernetes/issues/130690) | extends | Сделать недоступным вызываемый сервером вебхук (таймаут, обрыв, отказ соединения) и проверить, что ответ — 503 или 504, а не 400 |

### RESIL-GRACEFUL-SHUTDOWN — Перезапуск экземпляра не обрывает выполняющиеся запросы (RWB-0108, багов: 2)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [kubernetes/kubernetes#140242](https://github.com/kubernetes/kubernetes/issues/140242) | extends | Отправить SIGTERM экземпляру, у которого фоновая регистрация постоянно отклоняется, и проверить, что он завершается в пределах срока остановки |
| [kubernetes/kubernetes#127335](https://github.com/kubernetes/kubernetes/issues/127335) | extends | Вывести экземпляр вызываемого вебхука из эндпоинтов сервиса и проверить, что сервер в пределах срока прекращает слать ему запросы по старым соединениям |

### REST-API-VERSION-COMPATIBILITY — Совместимость версий API (RWB-0230, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [kubernetes/kubernetes#133704](https://github.com/kubernetes/kubernetes/issues/133704) | extends | Записать подресурс status через версию API, отличную от версии хранения, и проверить, что managedFields и spec объекта не изменились |

### REST-DECIMAL-PRECISION — Точность decimal (RWB-0231, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [kubernetes/kubernetes#140160](https://github.com/kubernetes/kubernetes/issues/140160) | extends | Отправить дробные min, max и шаг диапазона (0.5, 2.5) и проверить, что кратность шагу вычисляется без округления до целого |

### REST-NUMERIC-BOUNDARIES — Числовые границы (RWB-0123, багов: 3)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [kubernetes/kubernetes#138525](https://github.com/kubernetes/kubernetes/issues/138525) | extends | Отправить в поле с беззнаковым 32-битным диапазоном значения 2147483648 и 4294967295 и проверить, что они принимаются, а 4294967296 отклоняется |
| [kubernetes/kubernetes#136091](https://github.com/kubernetes/kubernetes/issues/136091) | extends | Отправить в поле со схемой type: integer, format: int32 значение 2147483648, а в поле type: number, format: float — 3.5e+38 и проверить отказ |
| [kubernetes/kubernetes#135487](https://github.com/kubernetes/kubernetes/issues/135487) | extends | Отправить в поле-количество строку 9223372036854775807 и проверить, что значение сохраняется, читается и используется в правилах валидации без искажения |

### REST-REQUIRED-PARAM-MISSING — Отсутствует обязательный параметр (RWB-0131, багов: 2)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [kubernetes/kubernetes#130896](https://github.com/kubernetes/kubernetes/issues/130896) | extends | Создать ресурс без поля, помеченного в контракте обязательным, и проверить, что сервер отклоняет запрос, а не подставляет значение по умолчанию молча |
| [kubernetes/kubernetes#127403](https://github.com/kubernetes/kubernetes/issues/127403) | extends | Опустить обязательный вложенный объект целиком и проверить, что ошибка называет его отсутствие, а не несовпадение его полей с полями родителя |

### REST-STATUS-CODE-CONTRACT — Статус ответа соответствует контракту (RWB-0136, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [kubernetes/kubernetes#132358](https://github.com/kubernetes/kubernetes/issues/132358) | extends | Запросить список с resourceVersion больше текущего вместе с limit и проверить документированный ответ 504, а не 500 с сообщением хранилища |

### REST-TYPE-MISMATCH — Несовпадение типа поля (RWB-0138, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [kubernetes/kubernetes#132359](https://github.com/kubernetes/kubernetes/issues/132359) | extends | Отправить DELETE с телом параметров удаления, где поля переданы неверного типа (apiVersion: true), и проверить ответ 400, а не 500 |

### VAL-DEFAULT-VALUES — Опущенные необязательные поля получают задокументированные значения по умолчанию (RWB-0166, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [kubernetes/kubernetes#128865](https://github.com/kubernetes/kubernetes/issues/128865) | covered | _только пруф_: Опущенное поле получает не документированное значение по умолчанию — ровно эта запись |

### VAL-DEFERRED-FAILURE — Принятые при записи данные не вызывают 5xx в зависимых операциях (RWB-0003, багов: 3)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [kubernetes/kubernetes#136472](https://github.com/kubernetes/kubernetes/issues/136472) | extends | Создать политику, ссылающуюся на тип параметров со схемой без type, и проверить, что фоновая проверка типов не падает и сервис продолжает работать |
| [kubernetes/kubernetes#135145](https://github.com/kubernetes/kubernetes/issues/135145) | extends | Создать политику, правила отбора которой указывают на тип со свойством type: object и additionalProperties: true, и проверить, что фоновая проверка типов не падает |
| [kubernetes/kubernetes#133651](https://github.com/kubernetes/kubernetes/issues/133651) | extends | Создать определение типа в устаревшей форме без схем по версиям и проверить, что PUT подресурса status его объектов через каждую версию не даёт 5xx |

### VAL-DEPENDENT-FIELDS — Взаимозависимые поля валидируются совместно (RWB-0167, багов: 2)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [kubernetes/kubernetes#131336](https://github.com/kubernetes/kubernetes/issues/131336) | extends | Отправить конфигурацию с запретом повышения привилегий и добавленными опасными возможностями (CAP_SYS_MODULE, CAP_SYS_PTRACE) и проверить, что сочетание отклоняется по политике |
| [kubernetes/kubernetes#130441](https://github.com/kubernetes/kubernetes/issues/130441) | extends | Отправить в связанные поля подсеть и вложенные в неё адреса с префиксом /32 и проверить, что правило вхождения их принимает, а адреса вне подсети отклоняет |

### VAL-STRING-FORMAT — Форматы строк (email, uuid, uri, date, phone) проверяются (RWB-0175, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [kubernetes/kubernetes#134320](https://github.com/kubernetes/kubernetes/issues/134320) | extends | Отправить в поле расписания cron значения «TZ=0», «TZ=», «CRON_TZ=UTC» и «TZ=Invalid/Timezone» и проверить 4xx валидации, а не 5xx или разрыв соединения |

