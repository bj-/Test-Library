# Кандидаты из баг-трекеров: партия `apollo-server`

Сгенерировано `tools/mining/cluster.py` из `build/mining/<batch>/batches/*.out.jsonl` и
`ideas/mined/apollo-server.review.yaml` — правки решений делаются в review-файле, затем пересборка.
План — `docs/BUG_MINING_PLAN.md`, шаги 6–7; применение — `tools/mining/apply_proofs.py`.

## Сводка

- Новых паттернов: 3 → идей: 3 (принять: 2, отклонить: 1, не решено: 0).
- Пруфы к существующим: 10 багов → 7 записей; новых шагов-вариантов: 5.

## Новые идеи

Принятые становятся записями `status: draft` с меткой `real-world-bug` и ссылкой на RWB.

| # | Решение | Запись / файл | Идея | Подтверждающие баги |
|---|---|---|---|---|
| 1 | accept | `GQL-ERROR-EXTENSIONS-SHAPE` (RWB-0316)<br>`checks/graphql/graphql.yaml` | Поля extensions ошибки GraphQL (code и пользовательские) присутствуют по документированной структуре ровно в одном месте — без копий во вложенных объектах (exception, originalError) | [apollographql/apollo-server#3835](https://github.com/apollographql/apollo-server/issues/3835) |
| 2 | reject | отклонено: Механизм в баге не описан, воспроизводится только в связке apollo-server-lambda и serverless-offline; ожидание (503, readiness) не обосновано первоисточником — перекрёстное ревью, обе модели | Сразу после старта экземпляра (асинхронная загрузка схемы, прогрев) серия одинаковых корректных запросов обслуживается одинаково — либо все успешны, либо до готовности 503 с Retry-After и readiness «не готов»; механизм в баге не описан | [apollographql/apollo-server#3416](https://github.com/apollographql/apollo-server/issues/3416) |
| 3 | accept | `HTTP-CACHEABLE-RESPONSE-CACHE-CONTROL` (RWB-0317)<br>`checks/rest/http-protocol.yaml` | Ответ, для которого включено кэширование (подсказки max-age у всех полей, политика кэша маршрута), содержит Cache-Control по итоговой политике — max-age как минимум из подсказок, public или private; пара к REST-SENSITIVE-CACHE-CONTROL | [apollographql/apollo-server#2918](https://github.com/apollographql/apollo-server/issues/2918) |

## Пруфы к существующим

Запись получает метку `real-world-bug` и `Real-world bug: RWB-NNNN`; статус не меняется. Для `extends`
текст варианта добавляется шагом (`steps[].action`, в `notes` — RWB). Неверное совпадение — ID бага в
`proofs.exclude`, вариант без нового шага — в `proofs.no_variant`.

### ERR-INTERNAL-ERROR-SHAPE — Внутренняя ошибка сервера возвращается в общей модели без утечек (RWB-0068, багов: 2)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [apollographql/apollo-server#313](https://github.com/apollographql/apollo-server/issues/313) | covered | _только пруф_: В записи есть шаг «ошибка в обработчике — ответ приходит без зависания и в общей модели» |
| [apollographql/apollo-server#23](https://github.com/apollographql/apollo-server/issues/23) | covered | _только пруф_: В записи есть шаг «ошибка, возникшая асинхронно в обработчике, — ответ приходит без зависания и в общей модели» |

### GQL-EQUIVALENT-SELECTION-FORMS — Эквивалентные формы выбора полей GraphQL дают одинаковые данные (RWB-0014, багов: 3)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [apollographql/apollo-server#3983](https://github.com/apollographql/apollo-server/issues/3983) | extends | Запросить поле типа union через фрагмент на член union, внутри которого фрагмент на сам union с фрагментами на каждый член, и сравнить с плоской формой |
| [apollographql/apollo-server#3253](https://github.com/apollographql/apollo-server/issues/3253) | extends | Запросить поле конкретного типа через inline-фрагмент на реализуемый им интерфейс и сравнить с прямым выбором поля |
| [apollographql/apollo-server#1724](https://github.com/apollographql/apollo-server/issues/1724) | covered | _только пруф_: Запись запрашивает поля через именованный фрагмент и под алиасом на разной глубине |

### GQL-GATEWAY-ROUTING — В объединённой схеме каждое поле направляется в свой upstream (RWB-0211, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [apollographql/apollo-server#3141](https://github.com/apollographql/apollo-server/issues/3141) | extends | В объединённой схеме выбрать поле общего типа-значения, объявленного в нескольких подграфах, у сущностей разных подграфов — данные возвращаются без ошибок |

### GQL-INPUT-VALIDATION — Входные типы и переменные валидируются (RWB-0318, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [apollographql/apollo-server#1410](https://github.com/apollographql/apollo-server/issues/1410) | extends | Передать переменную-объект без обязательного вложенного поля входного типа и проверить, что код ошибки — ошибка ввода, а не INTERNAL_SERVER_ERROR |

### RESIL-DEPENDENCY-DOWN — Недоступность зависимости даёт контролируемую ошибку (RWB-0107, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [apollographql/apollo-server#1510](https://github.com/apollographql/apollo-server/issues/1510) | extends | Получить от зависимости 4xx или 5xx на кэшируемый запрос, восстановить зависимость и повторить запрос в пределах ttl кэша |

### REST-REQUIRED-PARAM-MISSING — Отсутствует обязательный параметр (RWB-0131, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [apollographql/apollo-server#206](https://github.com/apollographql/apollo-server/issues/206) | covered | _только пруф_: В записи есть шаг «отсутствуют все поля сразу — пустой POST», ответ должен быть валидационным |

### REST-UNSUPPORTED-CONTENT-TYPE — Неподдерживаемый Content-Type запроса (RWB-0140, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [apollographql/apollo-server#1841](https://github.com/apollographql/apollo-server/issues/1841) | covered | _только пруф_: Запись отправляет корректное тело с text/plain и проверяет 415 и схему тела ошибки |

