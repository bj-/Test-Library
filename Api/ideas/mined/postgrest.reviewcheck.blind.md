# Перекрёстное ревью новых идей выгрузки багов

Партия `postgrest`, идей: 15; вариант пакета — без решений Claude — независимое ревью.
Этот файл целиком отдаётся другой LLM. Ответ модели вставить в чат внутренней сессии.

## Задание для модели

Ты — ревьюер библиотеки шаблонов API-тестов. Из реальных закрытых багов открытого проекта выделены паттерны,
для которых в библиотеке нет подходящей записи (`new`). Паттерны склеены в идеи (кластеры). Для каждой идеи реши,
становится ли она новой записью библиотеки. Суди по первоисточнику бага, а не по пересказу, и по индексу библиотеки
в конце файла.

Для каждой идеи ответь:

1. **Решение** — `accept` (новая запись) или `reject` (с причиной). Причины отказа, которые уже применялись:
   специфика конфигурации или внутренней логики одного продукта, не воспроизводимая тестом API другого продукта;
   идея уже покрыта существующей записью (назови её ID — тогда это пруф к ней, а не новая запись);
   слишком общая, чтобы стать шагом теста.
2. **Пересечение** — ID существующих записей, с которыми идея пересекается или дублирует их, и предложение:
   новая запись, шаг-вариант в существующей (`extends` к ID) или объединение с другой идеей этого списка.
3. **ID и файл** — подходят ли (ID: префикс файла, суть проверки, латиница и дефисы); если нет — твой вариант.
4. **Формулировка** — обобщена ли идея до проверки любого API (а не продукта из бага), верно ли направление
   (позитивная / негативная), нужны ли особые условия (инструменты, доступ к БД, к файлам стенда, две версии сервиса).
5. **Почему** — одна-две строки; при сомнении — цитата из бага.

Отдельно (после таблицы): идеи, которые стоит разбить на несколько записей или склеить, и паттерны, которые, по-твоему,
вообще не про API.

Принципы библиотеки (из README):

- Библиотека хранит **правила генерации проверок**, а не только готовые тест-кейсы.
- Одна запись = один проверяемый риск/инвариант.
- Протокол, полярность, набор тестов, приоритет и профиль запуска — независимые измерения.
- Цель - полноценное тестирование продукта, а не проверка соответствия контракту. Не доверяем никому: ни заказчику,
  ни аналитику, ни разработчику; контракт - лишь мнение разработчика о том, как работает продукт.
- Проверки соответствия контракту обязательны, но это лишь часть набора: к ним добавляются проверки по ТЗ,
  стандартам, практике и здравому смыслу.
- Ожидаемое поведение выводится из всех источников: ТЗ заказчика (ФТТ), внутренних ТЗ (ОТЗ, ЧТЗ), ПМИ, контракта,
  стандартов (RFC, OWASP), практики отрасли и здравого смысла - с указанием источника. Источник молчит - проверка всё
  равно выполняется; источники противоречат - это находка. Лучше завести баг о потенциальной проблеме, чем промолчать.
  Подробно - `../docs/decisions/0002-expected-behavior-sources.md`.
- Применимость определяется возможностями API, а не только названием метода.
- Для изменяющих операций проверяется не только ответ, но и состояние после операции.
- Неприменимость отличается от пробела покрытия.

Формат ответа — одна таблица на все идеи:

| # | Решение | Пересечение (ID) и что сделать | ID и файл | Формулировка / условия | Почему |
|---|---|---|---|---|---|
| 1 | accept/reject | — / extends ID / объединить с №N | ok / свой вариант | ok / замечание | ... |

В конце — 2–3 строки общего вывода: систематические ошибки кластеризации, если есть.

## Идея 1. Значения метрик остаются в допустимом диапазоне и восстанавливаются после сбоев — gauge доступных соединений в пределах от 0 до размера пула при обрывах и переподключениях к БД, счётчики не уменьшаются

### PostgREST/postgrest#4622 — Race condition in pool_available metric causes negative values during network instability

Ссылка: https://github.com/PostgREST/postgrest/issues/4622

- **Паттерн:** Метрики-gauge на эндпоинте метрик остаются в допустимом диапазоне при сбоях
- **Условие:** Соединения с БД обрываются и переподключаются (сетевая нестабильность)
- **Действие:** Вызвать обрывы соединений с БД, затем прочитать эндпоинт метрик и сравнить метрику доступных соединений с размером пула
- **Ожидание:** Значение метрики в пределах от 0 до максимального размера пула и восстанавливается после сбоя
- **Источник ожидания:** Здравый смысл: число доступных соединений не может быть отрицательным
- **Почему не подошла ближайшая запись:** OBS-HEALTH-ENDPOINTS про состояние здоровья, проверки корректности значений метрик нет

Первоисточник:

````text
## Problem Description

The `pgrst_db_pool_available` metric can drift into negative values during network instability or connection pool disruptions. We observed values as low as **-233** with `pgrst_db_pool_max: 80`, which is clearly incorrect.

## Root Cause

The race condition is in `src/PostgREST/Metrics.hs:35-41`:

```haskell
(HasqlPoolObs (SQL.ConnectionObservation _ status)) -> case status of
  SQL.ReadyForUseConnectionStatus  -> do
    incGauge poolAvailable
  SQL.InUseConnectionStatus        -> do
    decGauge poolAvailable
  SQL.TerminatedConnectionStatus  _ -> do
    decGauge poolAvailable
  SQL.ConnectingConnectionStatus -> pure ()
```

The `incGauge` and `decGauge` operations from `prometheus-client` are **not atomic**. During network instability:

1. Multiple connections transition states simultaneously
2. `decGauge` operations can occur before corresponding `incGauge` operations
3. Connections that terminate before becoming "ready" decrement without ever incrementing
4. The gauge drifts negative over time

## Impact

- **Metrics are unreliable** - monitoring/alerting based on `pool_available` produces false negatives
- **No actual pool impact** - the underlying pool works correctly; only the metric is corrupted
- **Persists until restart** - the counter never self-corrects; requires PostgREST restart

## Environment

- PostgREST version: v12.2.12
- `prometheus-client` constraint: `>= 1.1.1 && < 1.2.0`
- `hasql-pool` constraint: `>= 1.0.1 && < 1.1`
- Trigger: Network instability during Google GCE incident

## Suggested Fix

The gauge updates need to be atomic. Options include:

1. **Use STM** - Wrap the gauge in an `TVar` for atomic updates
2. **Use atomic operations** - If `prometheus-client` supports atomic inc/dec
3. **Track absolute count** - Calculate available from (total - in_use) instead of incrementing
4. **Add mutex/lock** - Protect gauge updates with a lock (less ideal for performance)

## Workaround

Restart PostgREST to reset the counter to correct values.
````

## Идея 2. Заголовок Server-Timing отражает фактическую длительность этапов — значения в миллисекундах, сумма согласуется с измеренным временем ответа при запросе с известной задержкой

### PostgREST/postgrest#4522 — Logs and server timing not showing the correct elapsed time

Ссылка: https://github.com/PostgREST/postgrest/issues/4522

- **Паттерн:** Заголовок Server-Timing отражает фактическую длительность этапов обработки
- **Условие:** Включена отдача Server-Timing, запрос выполняется заметное время (например, функция с задержкой)
- **Действие:** Выполнить запрос с известной задержкой и сравнить сумму длительностей Server-Timing с измеренным временем ответа
- **Ожидание:** Длительности в Server-Timing в миллисекундах и согласуются с фактическим временем ответа
- **Источник ожидания:** W3C Server Timing: dur — длительность в миллисекундах
- **Почему не подошла ближайшая запись:** OBS-TRACE-PROPAGATION про контекст трассировки; проверки значений Server-Timing нет

Первоисточник:

````text
### Environment

* PostgreSQL version: v17
* PostgREST version: 14.1
* Operating system: MacOS 15

### Description of issue

The logs are printing incorrect timings as shown here https://github.com/PostgREST/postgrest/issues/4462#issuecomment-3528745046. It seems the library has some kind of problem when calculating or getting the system time. The [`timeItT` function ](https://hackage.haskell.org/package/timeit-2.0/docs/src/System-TimeIt.html#timeIt) should return the time in seconds but it doesn't seem to be that way, it needs to be multiplied by 100 to have the correct value.

This also happens when returning the server timing, e.g. this is what's currently showing:

```
curl localhost:3000/rpc/sleep?seconds=4 -i
...
Server-Timing: jwt;dur=0.1, parse;dur=0.3, plan;dur=0.3, transaction;dur=47.1, response;dur=0.6
```

But after I multiply it by 100 it returns a reasonable value (the transaction at least):

```
Server-Timing: jwt;dur=7.0, parse;dur=32.2, plan;dur=31.4, transaction;dur=4697.8, response;dur=54.4
```

However once the elapsed time is big enough the values are not accurate:

```
time curl localhost:3000/rpc/sleep?seconds=100 -i
...
Server-Timing: jwt;dur=8.3, parse;dur=38.7, plan;dur=35.8, transaction;dur=112025.0, response;dur=55.7
________________________________________________________
Executed in  100.03 secs      fish           external
   usr time    6.84 millis    0.38 millis    6.45 millis
   sys time   10.06 millis    1.62 millis    8.44 millis
```

The transaction shows 112 seconds vs the 100.03 it actually took. In contrast, replacing the process with a function that uses the `Date.Time` library logs the correct time:

```haskell
    timeItT' p = do
      s <- liftIO getCurrentTime
      x <- p
      e <- liftIO getCurrentTime
      let time = realToFrac $ diffUTCTime e s
      return (time, x)

```
```
Server-Timing: jwt;dur=0.1, parse;dur=0.3, plan;dur=0.3, transaction;dur=100003.1, response;dur=0.6

________________________________________________________
Executed in  100.02 secs      fish           external
```

### Solution

Fixing upstream would be one solution, but the `Date.Time` library mentioned above could be an alternative (I'm not aware of the drawbacks yet).
````

## Идея 3. Один связанный ресурс, вложенный в ответ несколько раз под разными алиасами со своими фильтрами (REST-вложения, алиасы GraphQL), фильтруется независимо — каждое вложение совпадает с отдельным запросом с его фильтром

### PostgREST/postgrest#4075 — Unexpected results when embedding and filtering the same table twice

Ссылка: https://github.com/PostgREST/postgrest/issues/4075

- **Паттерн:** Фильтры вложений одного ресурса под разными алиасами применяются независимо
- **Условие:** В запросе один связанный ресурс вложен дважды под разными алиасами, у каждого свои фильтры
- **Действие:** Запросить ресурс с двумя вложениями одного связанного ресурса под алиасами и разными фильтрами, сравнить каждое вложение с отдельным запросом
- **Ожидание:** Каждое вложение содержит ровно записи, подходящие под его фильтры
- **Источник ожидания:** Здравый смысл; документация продукта о фильтрах вложений
- **Почему не подошла ближайшая запись:** REST-FILTER-SORT-COMPOSITION про композицию фильтра и сортировки, CONTRACT-FIELD-SELECTION про состав полей; независимости фильтров алиасов нет

Первоисточник:

````text
### Environment

* PostgreSQL version: v17
* PostgREST version: v10.2.0 to v13.0.0
* Operating system: MacOS

### Description of issue

This happened to a user in v10.2.0 but I could reproduce it in later versions including v13.0.0. Taking these tables and data:

```sql
create type visit_type as enum ('vacation', 'work');

create table places (
  id int primary key generated always as identity,
  name text not null
);

create table visits (
  id int primary key generated always as identity,
  place_id int not null references places(id),
  start_time timestamp,
  end_time timestamp,
  visit_type visit_type
);

insert into places (name) values ('Lake'), ('Mountain'), ('Beach');
insert into visits (place_id, start_time, end_time, visit_type)
values (1, '2025-01-01 10:00','2025-01-01 11:00', 'vacation'),
       (1, '2025-01-01 15:00','2025-01-01 16:00', 'vacation'),
       (1, '2025-01-01 20:00', '2025-01-01 21:00', 'work'),
       (2, '2024-11-01 09:00','2024-11-01 10:00', 'vacation'),
       (3, '2024-12-02 13:00','2024-12-02 14:00', 'vacation'),
       (1, '2023-01-02 20:00','2023-01-01 21:00', 'work');
```

If we take `places` and embed `visits` twice (one for work and others for non-work `visits`) we get the following response:

```bash
curl --get 'localhost:3030/places'\
  -d 'select=name,visits(*),work_visits:visits(*)' \
  -d 'id=eq.1' \
  -d 'visits.start_time=gt.20250101+00:00' \
  -d 'visits.end_time=lt.20250101+24:00' \
  -d 'visits.visit_type=neq.work' \
  -d 'work_visits.start_time=gt.20250101+00:00' \
  -d 'work_visits.end_time=lt.20250101+24:00' \
  -d 'work_visits.visit_type=eq.work'
```
```json
[
  {
    "name": "Lake",
    "work_visits": [],
    "visits": [
      {
        "id": 1,
        "end_time": "2025-01-01T11:00:00",
        "place_id": 1,
        "start_time": "2025-01-01T10:00:00",
        "visit_type": "vacation"
      },
      {
        "id": 2,
        "end_time": "2025-01-01T16:00:00",
        "place_id": 1,
        "start_time": "2025-01-01T15:00:00",
        "visit_type": "vacation"
      },
      {
        "id": 3,
        "end_time": "2025-01-01T21:00:00",
        "place_id": 1,
        "start_time": "2025-01-01T20:00:00",
        "visit_type": "work"
      },
      {
        "id": 6,
        "end_time": "2023-01-01T21:00:00",
        "place_id": 1,
        "start_time": "2023-01-02T20:00:00",
        "visit_type": "work"
      }
    ]
  }
]
```

The `work_vists` embed doesn't show anything (it should show the one with `"id" …[обрезано]
````

## Идея 4. Фильтр по полю, не входящему в выбор полей (select, fields, sparse fieldsets), работает для любых источников — таблица, представление, результат функции — и для простого, логического и вложенного фильтра; ответ содержит только выбранные поля

### PostgREST/postgrest#3965 — Cannot use filters that are not selected in Table-Valued Functions

Ссылка: https://github.com/PostgREST/postgrest/issues/3965

- **Паттерн:** Фильтр по полю, не входящему в выбор полей, работает для любых источников данных
- **Условие:** Выбор полей (select) не включает поле, по которому идёт фильтр; источник — результат функции, возвращающей таблицу
- **Действие:** Вызвать функцию с select без поля фильтра и с фильтром по этому полю (простым, логическим, по вложенному ресурсу)
- **Ожидание:** 200, отфильтрованные записи только с выбранными полями
- **Источник ожидания:** Здравый смысл; согласованность с фильтрацией таблиц
- **Почему не подошла ближайшая запись:** CONTRACT-FIELD-SELECTION проверяет состав полей, REST-FILTER-* — операторы; фильтра по невыбранному полю нет

Первоисточник:

````text
> [...] when using an rpc i cant filter for fields not in the select. I wanted to build an csv out of an filtered rpc, but i only want to include cols which are not part of a filter. 

 _Originally posted by @pebosi in [#3627](https://github.com/PostgREST/postgrest/issues/3627#issuecomment-2742476686)_

For example:

```bash
curl 'localhost:3000/rpc/getallprojects?select=id,client_id&name=like.OSX'
```
```json
{"code":"42703","details":null,"hint":null,"message":"column projects.name does not exist"} 
```
````

## Идея 5. Фильтр по полю, имя которого совпадает с именем вложенного (встраиваемого) ресурса или связи, применяется к значению поля — совпадение имён не меняет смысл фильтра и не даёт ошибку

### PostgREST/postgrest#2862 — v11.0.0 bug/breaking change: null filtering on embedded resource and disambiguation

Ссылка: https://github.com/PostgREST/postgrest/issues/2862

- **Паттерн:** Фильтр по колонке, имя которой совпадает с именем вложения, применяется к колонке
- **Условие:** Колонка внешнего ключа используется и как имя вложения связанного ресурса, и как поле фильтра
- **Действие:** Запросить ресурс с вложением по имени колонки и фильтром eq по той же колонке
- **Ожидание:** 200, фильтр применён к значению колонки
- **Источник ожидания:** Прежнее поведение продукта; здравый смысл
- **Почему не подошла ближайшая запись:** REST-FILTER-* не рассматривают совпадение имени поля и вложения

Первоисточник:

````text
Having:

```sql
create table profiles (
  id uuid not null,
  username text null,
  constraint profiles_pkey primary key (id)
);

create table user_friend (
  id bigint generated by default as identity not null,
  user1 uuid null,
  user2 uuid null,
  constraint user_friend_pkey primary key (id),
  constraint user_friend_user1_fkey foreign key (user1) references profiles (id) on delete cascade,
  constraint user_friend_user2_fkey foreign key (user2) references profiles (id) on delete cascade
);
```

The following now fails.

```
curl 'localhost:3000/user_friend?select=*,user1(*),user2(*)&user1=eq.a02fb934-3a4d-469b-a6b6-4fcd88b973cf'

{"code":"PGRST120","details":"Only is null or not is null filters are allowed on embedded resources","hint":null,"message":"Bad operator on the 'user1' embedded resource"}stevechavez@pop-os:~/
```

Because the filter is interpreted as a [null filter on an embed](https://postgrest.org/en/stable/references/api/resource_embedding.html#null-filtering-on-embedded-resources).

A workaround is:


```
curl 'localhost:3000/user_friend?select=*,profile1:profiles!user1(*),profile2:profiles!user2(*)&user1=eq.a02fb934-3a4d-469b-a6b6-4fcd88b973cf'
```
````

### PostgREST/postgrest#2588 — Bad operator on embedded resource

Ссылка: https://github.com/PostgREST/postgrest/issues/2588

- **Паттерн:** Фильтр по колонке работает, когда эта же колонка указана как имя встраиваемой связи
- **Условие:** В выборке колонка внешнего ключа и встраивание связи по имени этой колонки
- **Действие:** Запросить коллекцию с выбором колонки FK и встраиванием по её имени и фильтром eq по этой колонке
- **Ожидание:** Фильтр применяется к колонке, ответ 200 с отфильтрованными записями
- **Источник ожидания:** Документация продукта; здравый смысл
- **Почему не подошла ближайшая запись:** REST-FILTER-OPERATOR-TYPE-MATRIX — про типы полей, а здесь конфликт имени колонки и имени связи

Первоисточник:

````text
### Description of issue

I believe the latest version introduced a regression:

```
inbox_id,inbox:inbox_id(id,name)
```
with filter
```
inbox_id: eq.37ec27a7-4bec-420a-b6a7-5837e755451b
```
now returns 
```json
{"code":"PGRST120","details":"Only is null or not is null filters are allowed on embedded resources","hint":null,"message":"Bad operator on the 'inbox_id' embedded resource"}
```

The query can be fixed by filtering on `inbox.id` instead.
````

## Идея 6. Настройки, хранящиеся в БД, применяются при старте ко всем видам ресурсов

### PostgREST/postgrest#3660 — 404 on RPCs after upgrading to 12.2.2 when using the in-db config

Ссылка: https://github.com/PostgREST/postgrest/issues/3660

- **Паттерн:** Настройки, хранящиеся в БД, применяются при старте ко всем видам ресурсов
- **Условие:** Список схем и другие параметры заданы в БД (in-db config), сервис перезапущен или обновлён
- **Действие:** Перезапустить сервис и запросить таблицы, представления и функции настроенных схем
- **Ожидание:** Все ресурсы настроенных схем доступны так же, как до перезапуска
- **Источник ожидания:** Обратная совместимость; документация продукта
- **Почему не подошла ближайшая запись:** COMPAT-* про контракт и версии API; проверки применения конфигурации из БД при старте нет

Первоисточник:

````text
### Environment

* PostgreSQL version: 13
* PostgREST version: 12.2.2
* Operating system: SLES 15

### Description of issue

I've upgraded from release 12.2.1 to 12.2.2. 
After restarting the server the functions (RPC) are not working anymore. 
Getting 404 from my web server.
Tables seam to work and are reachable.

Didn't change anything on the configuration or something else, just replaced the binary and restarted.

12.2.1 worked, functions and views were reachable
````

## Идея 7. Настройки, заданные на уровне функции (SET search_path), не меняют окружение остальной части запроса

### PostgREST/postgrest#3242 — Regression / breaking change for RPCs with SET

Ссылка: https://github.com/PostgREST/postgrest/issues/3242

- **Паттерн:** Настройки, заданные на уровне функции, не меняют окружение остальной части запроса
- **Условие:** Вызываемая функция объявлена с SET параметров (search_path, роль и т. п.), ответ использует вычисляемые поля или другие объекты
- **Действие:** Вызвать функцию с собственным search_path и выбрать в ответе вычисляемые поля и вложения
- **Ожидание:** Настройки функции действуют только внутри неё (кроме явно разрешённых), ответ формируется как раньше
- **Источник ожидания:** Документация PostgreSQL: SET в определении функции действует на время её выполнения
- **Почему не подошла ближайшая запись:** Записей про изоляцию настроек выполнения функции от остального запроса нет

Первоисточник:

````text
### Environment

* PostgreSQL version: 15.x
* PostgREST version: 12.1-dev
* Operating system: Linux

### Description of issue

#3142 introduced quite a big breaking change - which I would consider a regression / bug. Applying **all** settings is never going to be correct / expected.

Take this for example:

```sql
create function do_something_dangerous() returns something
security definer
set search_path to pg_catalog, pg_temp
language plpgsql as $$
...
$$;
```

I have a few `SECURITY DEFINER` functions in my api. Best practice for security reasons is to add `pg_catalog, pg_temp` as a search_path for those kind of functions. After #3142, this suddenly changes the search_path for the **whole transaction**. This breaks, for example, computed fields on the returned value - and probably more.

I do have other cases of `SET`tings that I **don't want to have applied on the transaction level**. There is a reason I set them on the function and not for the authenticator role or so.

While I like the idea of hoisting some `SET`tings to the transaction level.. the current implementation is a problem. I don't even see a check for `role`, so will a `CREATE FUNCTION xxx SET ROLE TO y` be hoisted, too? Bad.

I think we should do at least one of, but possibly both of:
- Have an allowlist of explicitly named parameters instead of just setting all of them.
- Prefix those settings with `pgrst.xxx` or `tx.xxx` - and then set it without that prefix on the transaction level.

This needs to happen before we make the next release, otherwise we can't release a minor. In the current form, this is quite a breaking change.
````

## Идея 8. Настройки роли подключения не ломают запросы пользователей с меньшими правами

### PostgREST/postgrest#2896 — Request fails if impersonated role doesn't have permission to set GUC from authenticator role

Ссылка: https://github.com/PostgREST/postgrest/issues/2896

- **Паттерн:** Настройки роли подключения не ломают запросы пользователей с меньшими правами
- **Условие:** Роль подключения сервиса имеет настройки, требующие повышенных прав (log_min_duration_statement), запрос выполняется от переключённой роли пользователя
- **Действие:** Задать роли подключения привилегированную настройку и выполнить запрос от непривилегированной роли
- **Ожидание:** Запрос выполняется; к роли пользователя применяются только допустимые для неё настройки
- **Источник ожидания:** Прежнее поведение продукта; документация PostgreSQL о правах на параметры
- **Почему не подошла ближайшая запись:** Записей про применение настроек ролей БД при переключении роли нет

Первоисточник:

````text
### Environment

* PostgreSQL version: 13.10 (Ubuntu)
* PostgREST version: `postgrest/postgrest:v11.1.0`
* Operating system: AWS ECS / Docker

### Description of issue

If the authenticator role has a custom config applied to it (in our case `log_min_duration_statement = -1`), requests fail with the following permissions error:

```json
{
  "code": "42501",
  "details": null,
  "hint": null,
  "message": "permission denied to set parameter \"log_min_duration_statement\""
}
```

This seems to be a regression on v11 (specifically I think related to https://github.com/PostgREST/postgrest/issues/2561), because we've had no issues running against the same database using v10.2.0.

It _feels_ like what's happening is that PostgREST is switching to a less-privileged role (e.g. from `api_authenticator` -> `api_user`), and then trying to apply the superset of GUCs from both the authenticator and user roles. Then, if the user role doesn't have permission to apply the config change, it errors.
````

## Идея 9. Перегруженные функции разрешаются по типу аргумента во всех местах использования

### PostgREST/postgrest#2963 — Ressource embedding with stored procedures: Error recognising unique overloaded functions

Ссылка: https://github.com/PostgREST/postgrest/issues/2963

- **Паттерн:** Перегруженные функции разрешаются по типу аргумента во всех местах использования
- **Условие:** Несколько функций с одним именем для разных типов (вычисляемые связи), используются во вложении к таблицам и к результатам функций
- **Действие:** Запросить вложение вычисляемой связи для каждого типа, для которого есть перегрузка, у таблиц и у функций
- **Ожидание:** Для каждого типа вызывается своя перегрузка, ответ 200 с правильными данными
- **Источник ожидания:** Документация продукта о вычисляемых связях; документация PostgreSQL о перегрузке функций
- **Почему не подошла ближайшая запись:** Записей про разрешение перегруженных операций по типу нет

Первоисточник:

````text
### Environment

* PostgreSQL version: PostgreSQL 14.9 
* PostgREST version: Docker postgrest/postgrest:v11.2.0
* Operating system: Ubuntu 22.04.1

### Description of issue

According to docs ressource embedding in RPC's is supported when returning a table type.  I want to use this with computed relations and overloaded functions (same function name with different table types) . I can only get this to work with only one unique function name.

### Steps to reproduce


#### Create table types
```sql
CREATE TABLE api.test as 
SELECT'test' as desc;
CREATE TABLE api.test1 as 
SELECT
'test1' as desc
;
CREATE TABLE api.embedthis AS
SELECT * FROM generate_series(1,10) AS id;
```
#### Create computed relation embed(api.test) 

```sql
CREATE FUNCTION api.embed(api.test) RETURNS SETOF api.embedthis  AS  $$
    SELECT * FROM api.embedthis limit 1;
$$ STABLE LANGUAGE sql;
```
#### Test in basic table type:
```
http://localhost:3000/test?select=*,embed(*)
```
Response ok
```json
[
  {
    "desc": "test",
    "embed": [
      {
        "id": 1
      }
    ]
  }
]
```
#### Use computed relation in a stored procedure

```sql
DROP FUNCTION IF EXISTS api.myrpc(); 
CREATE FUNCTION  api.myrpc() RETURNS setof api.test
 LANGUAGE sql
AS $function$
  SELECT  * from api.test;
$function$;
```
```
http://localhost:3000/rpc/myrpc?select=*,embed(*)
```
Embbeded response is working as expected
```json
[
  {
    "desc": "test",
    "embed": [
      {
        "id": 1
      }
    ]
  }
]
```

#### create overloaded function embed(api.test1) 

```sql
CREATE FUNCTION api.embed(api.test1) RETURNS SETOF api.embedthis  AS  $$
    SELECT * FROM api.embedthis limit 2;
$$ STABLE LANGUAGE sql;
```
#### Test overloaded function embed(api.test1) 
```
http://localhost:3000/test1?select=*,embed(*)
```
Embedded response working as expected
```json
[
  {
    "desc": "test1",
    "embed": [
      {
        "id": 1
      },
      {
        "id": 2
      }
    ]
  }
]
```
Test embedded relation in RPC:
```
http://localhost:3000/rpc/myrpc?select=*,embed(*)
```
Embedded relation not working anymore
```json
{
  "code": "42725",
  "details": null,
  "hint": "Could not choose a best candidate function. You might need to add explicit type casts.",
  "message": "function api.embed(record) is not unique"
}
```
````

## Идея 10. Функции с любым поддерживаемым видом возвращаемого значения вызываются через API

### PostgREST/postgrest#2881 — v11.0.0:  RPC with function returning setof record no longer works 

Ссылка: https://github.com/PostgREST/postgrest/issues/2881

- **Паттерн:** Функции с любым поддерживаемым видом возвращаемого значения вызываются через API
- **Условие:** Функция возвращает record, setof record, скаляр, составной тип, таблицу
- **Действие:** Вызвать функции с каждым видом возвращаемого значения (с параметрами и без) и проверить ответ
- **Ожидание:** 200 и данные функции; ограничения (например, select по колонкам record) описаны и дают понятную ошибку
- **Источник ожидания:** Прежнее поведение продукта
- **Почему не подошла ближайшая запись:** COMPAT-* про контракт API, проверки видов возвращаемых значений процедур нет

Первоисточник:

````text
## Problem

The following:

```sql
create or replace function setof_record() returns setof record as $$
  select * from projects;
$$ language sql;
```

Fails on RPC:

```
curl localhost:3000/rpc/setof_record
{"code":"42601","details":null,"hint":null,"message":"a column definition list is required for functions returning \"record\""}
```

On v10.2.0, it worked:

```
curl localhost:3000/rpc/setof_record
[{"id":1,"name":"Windows 7","client_id":1}, 
 {"id":2,"name":"Windows 10","client_id":1}, 
 {"id":3,"name":"IOS","client_id":2}, 
 {"id":4,"name":"OSX","client_id":2}, 
 {"id":5,"name":"Orphan","client_id":null}]
```

Because it was treated as a scalar, i.e. it was called like `select setof_record()`.

## Solution

Treat `setof record` as scalar again. However this has the drawback of not being able to `select` a column:

```
curl 'localhost:3000/rpc/setof_record?select=id'
{"code":"42703","details":null,"hint":null,"message":"column setof_record.id does not exist"}
```

We should document this capability plus the limitation.
````

## Идея 11. Ответ в согласованном формате (GeoJSON, CSV, NDJSON, пользовательский бинарный медиатип) соответствует спецификации этого формата — структура по RFC 7946 для GeoJSON — в том числе для пустого результата и null (200 с пустым телом того же Content-Type или документированный 404, без 5xx); пара к REST-ACCEPT-NEGOTIATION

### PostgREST/postgrest#2699 — geojson structure: crs inside each feature instead on level type and features

Ссылка: https://github.com/PostgREST/postgrest/issues/2699

- **Паттерн:** Ответ в формате GeoJSON соответствует спецификации формата
- **Условие:** Клиент запрашивает коллекцию в формате application/geo+json
- **Действие:** Запросить коллекцию с Accept: application/geo+json и проверить структуру FeatureCollection
- **Ожидание:** Структура соответствует RFC 7946: FeatureCollection, Feature, geometry без нестандартных членов, повторяющихся в каждом объекте
- **Источник ожидания:** RFC 7946
- **Почему не подошла ближайшая запись:** REST-ACCEPT-NEGOTIATION проверяет выбор формата, а не соответствие тела ответа спецификации выбранного формата

Первоисточник:

````text
Hello, 
we are using postgREST for crud functions on our ai-geodata.  

we saw that the geo+json header responses a featurecollection with coordinate reference systems (crs). 

the crs is in each feature instead outside the features. 

can you reproduce this behavior and if yes is it possible that the structure of the response is adjusted by you?

### Environment

* PostgreSQL version: 12
* PostgREST version: 10
* PostGIS version: 3.1 USE_GEOS=1 USE_PROJ=1 USE_STATS=1
* Operating system: Kubernetes/Ubuntu20


### actual behavior

#### request: 
`curl -X GET https://url.com//result_frame_field?run_uuid=eq.11341ed6-4713-c28c-0d70-d290032abd73 -H "Accept: application/geo+json"`

#### response:

`{"type" : "FeatureCollection", 
"features" : [{
"type": "Feature", 
"geometry": {"type":"Polygon",
"crs":{"type":"name","properties":{"name":"EPSG:25832"}},"coordinates":[[[489633.9,5888000],[489634.042248535,5887995.982175827],[489636.885974121,5887995.468318176],[489637.14420166,5887997.19841671],[489637.2,5888000],[489633.9,5888000]]]}, "properties": {"id": 321386, "run_uuid": "11341ed6-4713-c28c-0d70-d290032abd73", "confidence": 0.8387449445279349, "date": "2023-03-03T13:58:01+00:00", "path": null}}, {"type": "Feature", "geometry": {"type":"Polygon","crs":{"type":"name","properties":{"name":"EPSG:25832"}},"coordinates":[[[489999.9,5887952.3],[489998.616845703,5887949.44701233],[489998.868896484,5887949.294552612],[489997.822460938,5887946.764746094],[489998.847167969,5887945.881781006],[489999.085253906,5887944.549810791],[489999.283007812,5887946.699108886],[489999.9,5887949.4],[489999.9,5887952.3]]]}, "properties": {"id": 321387, "run_uuid": "11341ed6-4713-c28c-0d70-d290032abd73", "confidence": 0.5394721098729639, "date": "2023-03-03T13:58:01+00:00", "path": null}}]}`

### expected behavior

#### request: 
`curl -X GET https://url.com//result_frame_field?run_uuid=eq.11341ed6-4713-c28c-0d70-d290032abd73 -H "Accept: application/geo+json"`

#### response:

`{
"type": "FeatureCollection",
"crs": { "type": "name", "properties": { "name": "urn:ogc:def:crs:EPSG::25832" } },
"features": [
{ "type": "Feature", "properties": { "confidence": 0.53121434123160771, "date": "2023-02-23 13:55:18" }, "geometry": { "type": "Polygon", "coordinates": [ [ [ 484484.773486328136642, 5837965.500375365838408 ], [ 484484.663623046886642, 5837966.349154663272202 ], [ 484482.207666015601717, 5837966.085598754696548 ], [ 484482.021044921886642, 58379 …[обрезано]
````

### PostgREST/postgrest#3126 — Error on Handler Function

Ссылка: https://github.com/PostgREST/postgrest/issues/3126

- **Паттерн:** Пустой результат в пользовательском формате ответа не вызывает внутреннюю ошибку
- **Условие:** Ресурс отдаёт данные в пользовательском медиатипе (бинарный формат), запрос не находит ни одной строки или значение null
- **Действие:** Запросить ресурс с Accept пользовательского медиатипа по идентификатору, которого нет
- **Ожидание:** 200 с пустым телом и тем же Content-Type (или задокументированный 404), без внутренней ошибки
- **Источник ожидания:** Здравый смысл; согласованность с JSON-ответом на пустой результат
- **Почему не подошла ближайшая запись:** REST-ACCEPT-NEGOTIATION про выбор формата, а не про пустой результат в выбранном формате

Первоисточник:

````text
## Problem

On https://postgrest.org/en/latest/references/api/media_type_handlers.html#handler-function

```sql
create or replace function get_line (id int)
returns "application/vnd.twkb" as $$
  select extensions.st_astwkb(geom) from lines where id = get_line.id;
$$ language sql;
```

When obtaining a null row:

```bash
curl "localhost:3000/rpc/get_line?id=3" -H "Accept: application/vnd.twkb" 
{"code":"PGRSTX00","details":null,"hint":null,"message":"RowError 0 2 UnexpectedNull"}
```

non-null rows work normally:

```
curl "localhost:3000/rpc/get_line?id=1" -H "Accept: application/vnd.twkb" 
HTTP/1.1 200 OK
```
````

## Идея 12. Заголовок Preference-Applied перечисляет ровно применённые предпочтения из Prefer (return, count, handling, tx и др.) — нет неприменённых, в том числе в ответе с ошибкой (RFC 7240)

### PostgREST/postgrest#2939 — Inconsistencies with the `Preference-Applied` header

Ссылка: https://github.com/PostgREST/postgrest/issues/2939

- **Паттерн:** Preference-Applied перечисляет ровно те предпочтения, которые применены
- **Условие:** Запрос с несколькими Prefer (count, return, tx и др.), часть которых применяется, часть нет из-за ошибки или настроек
- **Действие:** Отправить запросы с разными сочетаниями Prefer, включая завершившиеся ошибкой, и сравнить Preference-Applied с фактическим поведением
- **Ожидание:** В Preference-Applied есть все применённые предпочтения и нет неприменённых
- **Источник ожидания:** RFC 7240 §3
- **Почему не подошла ближайшая запись:** Записей про согласованность Prefer и Preference-Applied нет

Первоисточник:

````text
- `Prefer: tx=commit` gets inside `Preference-Applied` despite an uncommitted transaction:

```bash
$ PGRST_DB_TX_END="rollback-allow-override" postgrest-with-postgresql-15 postgrest-run
```

```bash
$ curl -D - -H "Content-Type: application/json" \-D - -H "Content-Type: application/json" \
    -H "Prefer: tx=commit" -H "Accept: application/vnd.pgrst.object"\
    'localhost:3000/rpc/setprojects' \
    -d @- <<JSON
{"id_l": 1, "id_h": 2, "name": "changed"}
JSON

HTTP/1.1 406 Not Acceptable
Transfer-Encoding: chunked
Date: Tue, 12 Sep 2023 04:24:23 GMT
Server: postgrest/11.2.0 (c5a9ed1)
Preference-Applied: tx=commit
Content-Type: application/vnd.pgrst.object+json; charset=utf-8

{"code":"PGRST116","details":"The result contains 2 rows","hint":null,"message":"JSON object requested, multiple (or no) rows returned"}
```

- `Prefer: count=exact` never gets into `Preference-Applied`:

```bash
$ curl -D - -H "Content-Type: application/json" \
  -H "Prefer: count=exact, return=representation" \
 "localhost:3000/projects" -d @- <<JSON
{"id":180, "name": "new"}
JSON

HTTP/1.1 201 Created
Transfer-Encoding: chunked
Date: Tue, 12 Sep 2023 04:21:52 GMT
Server: postgrest/11.2.0 (c5a9ed1)
Content-Range: */1
Preference-Applied: return=representation
Content-Type: application/json; charset=utf-8

[{"id":180,"name":"new","client_id":null}]
```
````

## Идея 13. Записи журнала при всплеске параллельных запросов не склеиваются и не разрываются — каждая запись отдельной строкой с собственной меткой времени, структурированный журнал разбирается построчно; нужен доступ к журналу

### PostgREST/postgrest#5234 — Wrong formatting of log messages under high traffic

Ссылка: https://github.com/PostgREST/postgrest/issues/5234

- **Паттерн:** Записи журнала при всплеске параллельных запросов не склеиваются
- **Условие:** Много одновременных запросов, каждый пишет запись в журнал
- **Действие:** Отправить пачку параллельных запросов и разобрать журнал построчно
- **Ожидание:** Каждая запись — отдельная строка с собственной меткой времени
- **Источник ожидания:** Здравый смысл; практика сбора логов
- **Почему не подошла ближайшая запись:** OBS-REQUEST-LOG-ALL-ATTEMPTS — о полноте журнала повторов, INJ-LOG-FORGING — о данных пользователя; целостность записей при параллельности не покрыта

Первоисточник:

````text
### Problem

> 2026-06-01T15:25:03.487885068+02:00 18/May/2026:08:59:30 +0000: Looked up a JWT in JWT cache18/May/2026:08:59:30 +0000: Looked up a JWT in JWT cache01/Jun/2026:13:25:03 +0000: Looked up a JWT in JWT cache18/May/2026:08:59:30 +0000: Looked up a JWT in JWT cache
> 2026-06-01T15:25:03.488149694+02:00
> 2026-06-01T15:25:03.488154271+02:00
> 2026-06-01T15:25:03.488156745+02:00
 
If we look at this log line closely, there are three additional log messages with timestamps, which should have appeared in the _empty_ log lines.
 
So maybe the bug here is wrong formatting of log messages which happens when many concurrent requests come in burst? 

 _Originally posted by @taimoorzaeem in [#5212](https://github.com/PostgREST/postgrest/issues/5212#issuecomment-5521679672)_
````

## Идея 14. Перезагрузка кэша метаданных (схема, конфигурация, маршруты) на большом объёме не блокирует обслуживание запросов надолго — запросы идут по старому состоянию или с короткой задержкой в пределах SLO

### PostgREST/postgrest#4360 — Schema cache reload with large relationship count causes 100+ second API blocking

Ссылка: https://github.com/PostgREST/postgrest/issues/4360

- **Паттерн:** Перезагрузка кэша метаданных на большой схеме не блокирует обслуживание запросов надолго
- **Условие:** Схема с сотнями таблиц и тысячей связей, запускается перезагрузка кэша (миграция)
- **Действие:** Запустить перезагрузку кэша схемы и параллельно отправлять запросы, замеряя задержку
- **Ожидание:** Запросы обслуживаются (по старой схеме или с короткой задержкой в пределах SLO)
- **Источник ожидания:** Здравый смысл; SLO сервиса
- **Почему не подошла ближайшая запись:** PERF-LATENCY-BASELINE — задержка при обычной работе, RESIL-GRACEFUL-SHUTDOWN — о перезапуске; перезагрузка метаданных под нагрузкой не покрыта

Первоисточник:

````text
### Environment

* PostgreSQL version: 15.8.1.040 (Supabase local)
* PostgREST version: v12.2.3 (Supabase local)
* Operating system: Docker on macOS 15.7

### Description of issue

**Expected:** Schema cache reloads complete within seconds.
**Actual:** 100-second delay with 100% CPU usage, blocking all API requests.

**This is a production-blocking issue for us.** Every database schema migration triggers a PostgREST schema cache reload, which blocks our entire API for 100+ seconds. This makes deployments extremely disruptive. 

#### Evidence

```
$ docker logs -f --timestamps supabase_rest_arcip

2025-09-26T08:37:29.866368343Z 26/Sep/2025:08:37:29 +0000: Starting PostgREST 12.2.3 (519615d)...
2025-09-26T08:37:29.866582885Z 26/Sep/2025:08:37:29 +0000: Admin server listening on port 3001
2025-09-26T08:37:29.866985885Z 26/Sep/2025:08:37:29 +0000: Listening on port 3000
2025-09-26T08:37:29.896365301Z 26/Sep/2025:08:37:29 +0000: Listening for notifications on the "pgrst" channel
2025-09-26T08:37:29.906531260Z 26/Sep/2025:08:37:29 +0000: Successfully connected to PostgreSQL 15.8 on aarch64-unknown-linux-gnu, compiled by gcc (GCC) 13.2.0, 64-bit
2025-09-26T08:37:29.933404135Z 26/Sep/2025:08:37:29 +0000: Config reloaded
2025-09-26T08:37:33.235558095Z 26/Sep/2025:08:37:33 +0000: Schema cache queried in 404.1 milliseconds
2025-09-26T08:39:07.222539597Z 26/Sep/2025:08:37:33 +0000: Schema cache loaded 161 Relations, 1026 Relationships, 18 Functions, 0 Domain Representations, 4 Media Type Handlers, 1194 Timezones
```

```
$ docker stats supabase_rest_arcip --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}\t{{.NetIO}}\t{{.BlockIO}}"

supabase_rest_arcip   100.29%   224MiB / 2.845GiB   7.69%     209MB / 4.01MB   28.3MB / 0B
```

#### Related Issues
- https://github.com/PostgREST/postgrest/issues/3046
- https://github.com/PostgREST/postgrest/issues/2450
````

## Идея 15. Роль из claim-массива токена извлекается по настроенному пути при любом числе элементов

### PostgREST/postgrest#4039 — Issue when using `.aud[0]` inside `jwt-role-claim-key`

Ссылка: https://github.com/PostgREST/postgrest/issues/4039

- **Действие:** Отправить запросы с токенами, где claim с ролью — массив из одного элемента, из нескольких элементов и строка
- **Ожидание:** Роль определяется по пути одинаково; неподходящее значение даёт 401, а не тихий переход к анонимной роли

Первоисточник:

````text
## Problem

PostgREST version: v12.2.8

A user cannot modify the JWT, they want to use the `aud` as `role`. The format of the `aud` sent in the JWT is:

```javascript
{
  "aud": ["some_value"],
  ...
}
```

So they set `pgrst.jwt_role_claim_key = '.aud[0]'`. But this doesn't work and a request with JWT defaults to the `anonymous` role. However, setting `pgrst.jwt_role_claim_key = '.aud'` works and sets "some_value" as role.

Now, if the `aud` has more than one key then the original setup works:

```javascript
{
  "aud": ["some_value", "other_value"],
  ...
}
```

That is, `pgrst.jwt_role_claim_key = '.aud[0]'` sets "some_value" as role, and `pgrst.jwt_role_claim_key = '.aud'` no longer works.

We need to determine if we should support operating the `aud` claim on `jwt-role-claim-key`. 

If we don't, I think we should fail if the config contains the `aud` claim.
````

## Индекс библиотеки

Все записи (505): ID | категория | заголовок.

```text
ASYNC-DEAD-LETTER | async | Необрабатываемые сообщения уходят в DLQ без блокировки очереди
ASYNC-EVENT-ORDERING | async | Нарушение порядка событий не портит состояние
ASYNC-EVENT-PATH-SAME-RULES | async | Событийный путь применяет те же фильтры и границы доступа, что и плановый
ASYNC-IDEMPOTENT-CONSUMER | async | Повторная доставка события обрабатывается однократно
ASYNC-JOB-CANCEL | async | Отмена фоновой задачи останавливает её и не оставляет частичных эффектов
ASYNC-JOB-LIFECYCLE | async | Фоновая задача проходит статусы и отдаёт результат
ASYNC-MESSAGE-VALIDATION | async | Входящие сообщения брокера валидируются по схеме так же, как HTTP-запросы
ASYNC-OUTBOUND-REQUEST-HEADERS | async | Исходящий запрос сервера содержит корректный Host, в том числе с нестандартным портом
ASYNC-RPC-ERROR-PROPAGATION | async | Ошибка обработчика в схеме запрос-ответ через брокер возвращается вызывающему
ASYNC-SCHEDULE-LONG-UPTIME | async | Задача по расписанию срабатывает и после длительной непрерывной работы процесса
ASYNC-SSE-STREAM | async | Потоковый ответ SSE работает для всех методов и отдаёт text/event-stream
ASYNC-WEBHOOK-RETRY | async | Неуспешная доставка вебхука повторяется с backoff и ограничением
ASYNC-WEBHOOK-SIGNATURE | async | Вебхуки подписаны, подпись проверяется, повтор отклоняется
ASYNC-WEBHOOK-URL-SSRF | async | URL вебхука не может указывать на внутренние адреса
AUTH-ACCOUNT-STATE-ALL-SCHEMES | security | Отключённая, заблокированная или истёкшая учётка не аутентифицируется ни одной схемой
AUTH-API-KEY-LIFECYCLE | security | API-ключи ограничены по правам, отзываются и не раскрываются
AUTH-BASIC-CREDENTIALS-SPECIAL-CHARS | security | Basic-аутентификация принимает пароль с двоеточием, пробелами и UTF-8
AUTH-BRUTE-FORCE-PROTECTION | security | Перебор паролей ограничивается
AUTH-CLIENT-ASSERTION-BINDING | security | Client assertion принимается только с ключом клиента, указанного в ней
AUTH-CLIENT-CERT-IDENTITY | security | Личность из сертификата клиента извлекается однозначно
AUTH-CONCURRENT-SESSIONS | security | Лимит одновременных сессий и устройств соблюдается
AUTH-CONTACT-CHANGE-PREVIOUS-VALUE | security | Смена телефона или email на ранее использованный этим пользователем проходит подтверждение
AUTH-COOKIE-ATTRIBUTES | security | Сессионные cookie имеют Secure, HttpOnly, SameSite и узкие Domain/Path
AUTH-CSRF | security | Изменяющие операции с cookie-аутентификацией защищены от CSRF
AUTH-EXTERNAL-ID-EXACT-MATCH | security | Внешний идентификатор субъекта сравнивается побайтно в паре издатель и subject
AUTH-EXTERNAL-IDP-MISSING-ATTRIBUTES | security | Вход через внешний IdP без необязательных атрибутов профиля обрабатывается по требованиям
AUTH-EXTERNAL-IDP-UNVERIFIED-EMAIL | security | Вход через внешний IdP не связывается с учёткой по неподтверждённому email
AUTH-GENERATED-SECRET-STRENGTH | security | Сгенерированные сервером секреты имеют стойкость не ниже требуемой алгоритмом
AUTH-IDENTITY-ATTRIBUTES-ALL-SCHEMES | security | Атрибуты идентичности, которые даёт источник, сохраняются при любом способе аутентификации
AUTH-IMPORTED-PASSWORD-HASH | security | Пользователь, импортированный с хешем пароля поддерживаемого алгоритма, входит по исходному паролю
AUTH-JWT-ALG-CONFUSION | security | Подмена алгоритма RS256 на HS256 с публичным ключом не принимается
AUTH-JWT-ALG-NONE | security | JWT с alg=none отклоняется
AUTH-JWT-HEADER-INJECTION | security | Параметры kid, jku, x5u в заголовке JWT не позволяют подставить ключ
AUTH-JWT-TIME-CLAIMS | security | Токены с nbf/iat в будущем и без exp обрабатываются по политике
AUTH-JWT-VALID-ACCEPTED | security | Валидный токен принимается при всех поддерживаемых алгоритмах, наборах ключей и настройках claims
AUTH-LOGIN-IDENTIFIER-NORMALIZATION | validation | Логин (email, телефон) нормализуется одинаково при входе, создании и поиске
AUTH-LOGOUT-CLEARS-COOKIE | security | Выход снимает cookie сессии на клиенте
AUTH-LOGOUT-INVALIDATES | security | После выхода токен и сессия недействительны
AUTH-MFA-STEP-UP | security | Операции, требующие второго фактора, недоступны без него
AUTH-MFA-UNENROLLED-ERROR | security | Ошибка шага второго фактора у пользователя без зарегистрированного фактора — обычная 4xx
AUTH-OAUTH-OUTBOUND-SCOPE | security | Запрос авторизации к внешнему провайдеру содержит запрошенные scope без устаревших значений по умолчанию
AUTH-OAUTH-PAR | security | Pushed Authorization Request действует как прямой запрос авторизации и не ограничивает длительность входа
AUTH-OAUTH-PUBLIC-CLIENT-CONSENT | security | Повторная авторизация публичного OAuth-клиента не выполняется без участия пользователя
AUTH-OAUTH-REDIRECT-STATE | security | OAuth/OIDC flow проверяет redirect_uri, state и PKCE
AUTH-OAUTH-RESOURCE-INDICATOR | security | Индикатор ресурса, не соответствующий аудитории клиента, даёт 400 invalid_target
AUTH-OTP-ATTEMPT-LIMIT | security | Количество попыток ввода одноразового кода ограничено
AUTH-OTP-BINDING | security | Одноразовый код привязан к получателю и операции
AUTH-OTP-EXPIRY | security | Одноразовый код перестаёт действовать после истечения срока
AUTH-OTP-REUSE | security | Одноразовый код нельзя использовать повторно и после выдачи нового
AUTH-OTP-SEND-LIMIT | security | Частота отправки кодов ограничена (SMS bombing)
AUTH-PASSWORD-CHANGE-REVOKES | security | Смена или сброс пароля завершает другие сессии
AUTH-PASSWORD-POLICY | security | Политика паролей применяется на сервере
AUTH-PASSWORD-RESET-TOKEN | security | Токен сброса пароля одноразовый, ограничен по времени и привязан к пользователю
AUTH-PROTOCOL-SESSION-OWNER-BINDING | security | Идентификатор протокольной сессии привязан к аутентифицированному владельцу
AUTH-REFRESH-PRESERVES-SCOPE | security | Refresh без параметра scope сохраняет scope исходной авторизации
AUTH-SAML-ASSERTION-REPLAY | security | Повторно предъявленное SAML-утверждение отклоняется
AUTH-SESSION-FIXATION | security | Идентификатор сессии меняется после входа
AUTH-SESSION-NOT-BEFORE-LOGIN | security | Анонимный запрос не получает cookie сессии и не создаёт серверную сессию
AUTH-SESSION-TIMEOUT | security | Сессия истекает после простоя и абсолютного срока
AUTH-TOKEN-IN-URL | security | Учётные данные не передаются и не принимаются в URL
AUTH-TOKEN-INTROSPECTION | security | Интроспекция токена возвращает актуальное состояние и те же claims, что в токене
AUTH-TOKEN-RESERVED-CLAIMS | security | Пользовательские поля не переопределяют зарезервированные claims токена
AUTH-TOKEN-SENDER-CONSTRAINED | security | Обмен и обновление токена сохраняют привязку к отправителю (DPoP, mTLS)
AUTH-TOKEN-TYPE-CONFUSION | security | Refresh, ID или сервисный токен не принимается как access-токен
AUTH-USER-ENUMERATION | security | Ответы входа, регистрации и восстановления не раскрывают существование аккаунта
BIZ-CLIENT-PRICE-TAMPERING | business-logic | Цена, скидка и итог рассчитываются на сервере
BIZ-CONFIG-SCOPE-PRECEDENCE | business-logic | Настройка более узкого уровня имеет приоритет над глобальной
BIZ-CURRENCY-MISMATCH | business-logic | Смешение валют в операции обрабатывается явно
BIZ-DOUBLE-SPEND | business-logic | Параллельные списания не приводят к двойной трате
BIZ-EMAIL-LINK-CROSS-SESSION | business-logic | Ссылка-действие из письма работает в другой сессии и после перезапуска сервиса
BIZ-HIERARCHY-CYCLES | business-logic | Ссылка на себя и циклы в иерархии запрещены
BIZ-LIMITS-QUOTAS | business-logic | Лимиты и квоты соблюдаются на границе и не обходятся параллельно
BIZ-NEGATIVE-QUANTITY | business-logic | Отрицательные и нулевые количества и суммы не дают выгоды
BIZ-ONE-TIME-BENEFIT-REUSE | business-logic | Одноразовые промокоды, бонусы и приглашения нельзя использовать повторно
BIZ-ROUNDING | business-logic | Округление денежных величин корректно и не накапливает ошибку
BIZ-SIDE-EFFECTS-ONCE | business-logic | Побочные эффекты (письма, push, события) выполняются ровно один раз
BIZ-TIME-WINDOW | business-logic | Операции вне разрешённого временного окна отклоняются
BIZ-WORKFLOW-STEP-SKIP | business-logic | Нельзя пропустить обязательный шаг бизнес-процесса
COMPAT-ADDITIVE-CHANGE | compatibility | Добавление полей не ломает существующих клиентов
COMPAT-BREAKING-CHANGE-DIFF | compatibility | Изменения контракта проверяются на обратную несовместимость
COMPAT-DEFAULT-VERSION | compatibility | Запрос без указания версии обслуживается задокументированной версией
COMPAT-DEPRECATION-SIGNALS | compatibility | Устаревающие операции помечены Deprecation и Sunset
COMPAT-ENUM-EXTENSION | compatibility | Добавление значения enum не ломает клиентов
COMPAT-IMPLEMENTATION-MATCHES-CONTRACT | compatibility | Реализация соответствует опубликованному контракту
COMPAT-MIXED-VERSION-WRITE-STABILITY | compatibility | Экземпляры разных версий при поэтапном обновлении не перезаписывают общий объект по кругу
COMPAT-UPGRADE-STORED-DATA-STABLE | compatibility | Обновление сервера не меняет сохранённые объекты и не запускает побочных действий
CONC-COUNTER-INCREMENT | concurrency | Счётчики корректны при параллельных инкрементах
CONC-DELETE-VS-UPDATE | concurrency | Параллельные удаление и изменение не оставляют ресурс в противоречивом состоянии
CONC-DOUBLE-SUBMIT | concurrency | Двойная отправка формы не создаёт дубликат операции
CONC-LOST-UPDATE | concurrency | Параллельные изменения не теряют друг друга молча
CONC-PARALLEL-CREATE-UNIQUE | concurrency | Параллельное создание с одним уникальным ключом создаёт один объект
CONC-PARALLEL-INDEPENDENT | concurrency | Параллельные независимые запросы одной операции выполняются без 5xx
CONC-REQUEST-CONTEXT-ISOLATION | concurrency | Параллельные запросы разных пользователей получают только свой контекст и свой ответ
CONC-STATE-TRANSITION-RACE | concurrency | Параллельные переходы состояния не нарушают автомат состояний
CONTRACT-FIELD-SELECTION | contract | Выбор полей возвращает ровно запрошенные поля с правильными значениями
CONTRACT-PUBLISHED-SCHEMA-VALID | contract | Опубликованные сервисом описания API валидны в заявленном диалекте
CONTRACT-REQUIRED-FIELDS | contract | Successful response contains required contract fields
CONTRACT-UNKNOWN-FIELD-POLICY | contract | Unknown fields follow the documented contract policy
ERR-INTERNAL-ERROR-SHAPE | errors | Внутренняя ошибка сервера возвращается в общей модели без утечек
ERR-STABLE-ERROR-CODES | errors | Машиночитаемые коды ошибок стабильны и задокументированы
ERR-STATUS-MATCHES-EFFECT | errors | Код ответа соответствует фактическому результату операции
FILE-ABORTED-UPLOAD-CLEANUP | files | Прерванная загрузка не оставляет данных в хранилище и не учитывается в квоте
FILE-ARCHIVE-BOMB | files | Архивные и графические бомбы не исчерпывают ресурсы
FILE-DOWNLOAD-AUTHZ | files | Скачивание файлов проверяет права и срок действия ссылок
FILE-DOWNLOAD-HEADERS | files | Скачивание отдаёт корректные Content-Type, Content-Disposition и nosniff
FILE-EMPTY-AND-MALFORMED-MULTIPART | files | Пустой файл и некорректный multipart обрабатываются корректно
FILE-FILENAME-SANITIZATION | files | Имя загружаемого файла санитизируется
FILE-MALFORMED-STRUCTURE | files | Повреждённый файл при разборе метаданных даёт 4xx, а не падение процесса
FILE-MALICIOUS-CONTENT | files | Вредоносное содержимое обнаруживается или изолируется
FILE-METADATA-STRIP | files | Метаданные изображений с ПДн удаляются
FILE-MULTIPART-METADATA-SAVED | files | Метаданные из полей multipart сохраняются вместе с файлом
FILE-RANGE-REQUESTS | files | Частичное скачивание через Range работает по контракту
FILE-TRANSFORM-LIMITS | files | Лимит трансформации файла пропускает допустимые комбинации и отклоняет превышение
FILE-TRANSFORM-STORAGE-PARITY | files | Трансформации файла работают на каждом поддерживаемом хранилище
FILE-UPLOAD-KEY-COLLISION | files | Загрузка не перезаписывает чужой файл с тем же именем или ключом хранилища
FILE-UPLOAD-SIZE-LIMIT | files | Лимит размера загружаемого файла соблюдается
FILE-UPLOAD-TYPE-VALIDATION | files | Тип файла проверяется по содержимому, а не только по расширению
GQL-ALIAS-BATCH-ABUSE | graphql | Алиасы и batch-запросы не обходят rate limit
GQL-COMPLEXITY-LIMIT | graphql | Стоимость запроса ограничена (поля, списки, first/last)
GQL-CSRF-GET-MUTATION | graphql | Мутации не выполняются через GET и простые Content-Type
GQL-DEPTH-LIMIT | graphql | Глубина запроса ограничена
GQL-EQUIVALENT-SELECTION-FORMS | graphql | Эквивалентные формы выбора полей GraphQL дают одинаковые данные
GQL-ERROR-EXTENSIONS-SHAPE | graphql | Поля extensions ошибки GraphQL не дублируются во вложенных объектах
GQL-ERRORS-NO-LEAK | graphql | Ошибки GraphQL не раскрывают внутренние детали
GQL-FIELD-LEVEL-AUTHZ | graphql | Авторизация применяется на уровне полей и вложенных резолверов
GQL-FIELD-SUGGESTIONS | graphql | Подсказки «Did you mean» не раскрывают схему при закрытом introspection
GQL-GATEWAY-ROUTING | graphql | В объединённой схеме каждое поле направляется в свой upstream
GQL-INPUT-VALIDATION | graphql | Входные типы и переменные валидируются
GQL-INTROSPECTION | graphql | Introspection отключён или ограничен в продуктиве
GQL-PARTIAL-DATA | graphql | Частичные результаты с ошибками соответствуют спецификации nullability
GQL-REST-ENDPOINT-PARITY | graphql | Операция, опубликованная как REST-эндпоинт, выполняется так же, как исходный GraphQL-запрос
GRPC-BIDI-FLOW-CONTROL | grpc-contract | Двунаправленный стрим соблюдает flow control при медленном клиенте
GRPC-CANCELLATION | grpc-errors | Отмена клиентом прекращает обработку на сервере
GRPC-CLIENT-STREAM-PARTIAL-FAILURE | grpc-contract | Ошибка в середине клиентского стрима обрабатывается по контракту
GRPC-COMPRESSION | grpc-contract | Сжатие сообщений согласуется и неподдерживаемое отклоняется
GRPC-DEADLINE-EXCEEDED | grpc-errors | Превышение дедлайна возвращает DEADLINE_EXCEEDED без побочных эффектов сверх контракта
GRPC-DEADLINE-PROPAGATION | grpc-errors | Дедлайн передаётся в нижележащие вызовы
GRPC-ENUM-UNKNOWN-VALUE | grpc-contract | Неизвестное и нулевое значение enum обрабатывается явно
GRPC-ERROR-DETAILS | grpc-errors | Ошибки содержат структурированные детали google.rpc.Status
GRPC-FIELD-PRESENCE | grpc-contract | Значение по умолчанию отличается от неустановленного поля, где это важно
GRPC-HEALTH-PROTOCOL | grpc-contract | Стандартный health-протокол gRPC реализован корректно
GRPC-JSON-TRANSCODING | grpc-contract | HTTP/JSON транскодирование соответствует proto-аннотациям
GRPC-KEEPALIVE-POLICY | grpc-errors | Агрессивные keepalive-пинги клиента ограничиваются
GRPC-MAX-MESSAGE-SIZE | grpc-contract | Сообщения больше лимита отклоняются RESOURCE_EXHAUSTED
GRPC-METADATA-AUTH-MISSING | grpc-errors | Каждый RPC сервиса требует аутентификационные метаданные
GRPC-METADATA-MALFORMED | grpc-errors | Некорректные и чрезмерные метаданные отклоняются
GRPC-NOT-FOUND-ALREADY-EXISTS | grpc-errors | Отсутствующий и дублирующийся ресурс дают NOT_FOUND и ALREADY_EXISTS
GRPC-ONEOF | grpc-contract | Поля oneof валидируются и не установлены одновременно
GRPC-PRECONDITION-ABORTED | grpc-errors | FAILED_PRECONDITION и ABORTED используются согласно семантике повтора
GRPC-PROTO-BREAKING | grpc-contract | Изменения proto не ломают совместимость wire и JSON
GRPC-REFLECTION-EXPOSURE | grpc-contract | Server reflection отключён или защищён в продуктиве
GRPC-REPEATED-BOUNDARIES | grpc-contract | Repeated и map поля: пусто, много элементов, дубликаты ключей
GRPC-REQUEST-VALIDATION | grpc-contract | Invalid gRPC request is rejected predictably
GRPC-RESOURCE-EXHAUSTED | grpc-errors | Превышение квот возвращает RESOURCE_EXHAUSTED с RetryInfo
GRPC-RETRY-POLICY | grpc-errors | Автоматические повторы применяются только к безопасным методам и статусам
GRPC-SERVER-STREAM-COMPLETE | grpc-contract | Серверный стрим отдаёт все элементы по порядку и завершается OK
GRPC-STATUS-MAPPING | grpc-errors | RPC errors use documented gRPC status codes
GRPC-STREAM-AUTH-EXPIRY | grpc-errors | Длительный стрим учитывает истечение и отзыв токена
GRPC-STREAM-RESOURCE-LIMITS | grpc-errors | Число одновременных стримов и их длительность ограничены
GRPC-STREAM-TERMINATION | grpc-contract | Streaming RPC terminates correctly
GRPC-TLS-MTLS | grpc-errors | Транспорт защищён TLS, при mTLS клиентский сертификат обязателен
GRPC-UNAUTHENTICATED-VS-PERMISSION-DENIED | grpc-errors | Отсутствие аутентификации и отсутствие прав различаются по статусу
GRPC-UNKNOWN-FIELDS | grpc-contract | Неизвестные поля сообщения обрабатываются по политике совместимости
GRPC-WELL-KNOWN-TYPES | grpc-contract | Timestamp, Duration и другие well-known types валидируются по диапазонам
HARD-BACKUP-RESTORE-PROTECTED | security | Восстановление из резервной копии не обходит защиту записи
HARD-BUSINESS-FLOW-AUTOMATION | security | Чувствительные бизнес-потоки защищены от автоматизированного злоупотребления
HARD-CACHE-POISONING | security | Неключевые заголовки не отравляют общий кэш
HARD-CLIENT-IP-TRUSTED-PROXIES | security | IP клиента определяется по цепочке доверенных прокси одинаково на всех маршрутах
HARD-DEBUG-ENDPOINTS | security | Отладочные и служебные эндпоинты недоступны извне
HARD-DENYLIST-EVERY-ENTRY | security | Каждый элемент списка запрещённых значений отклоняется
HARD-EXCESSIVE-DATA-EXPOSURE | security | Ответы не содержат внутренних полей сверх контракта
HARD-EXPENSIVE-OPERATION-LIMITS | security | Дорогие операции ограничены по ресурсам
HARD-HOST-HEADER | security | Подмена Host и X-Forwarded-Host не влияет на ссылки и маршрутизацию
HARD-ID-PREDICTABILITY | security | Предсказуемые идентификаторы не позволяют собрать данные перебором
HARD-IP-ALLOWLIST | security | Ограничение доступа по адресам и подсетям работает на границах для IPv4 и IPv6
HARD-METHOD-OVERRIDE | security | Заголовки переопределения метода не обходят авторизацию
HARD-OUTBOUND-CREDENTIALS-SCOPE | security | Учётные данные своего сайта не уходят в исходящие запросы к другим хостам
HARD-ROUTE-SHARED-BACKEND-ISOLATION | security | Маршруты шлюза к одному бэкенду применяют каждый свои фильтры
HARD-SENSITIVE-DATA-IN-URL | security | Персональные данные и секреты не передаются в URL
HARD-SETUP-ENDPOINTS-PROTECTED | security | Эндпоинты первоначальной настройки не позволяют захватить экземпляр
HARD-SHADOW-API-VERSIONS | security | Старые версии API и недокументированные маршруты не обходят защиту
HARD-SLOW-CLIENT-LIMITS | security | Медленные и неполные запросы и непрочитанные ответы не накапливаются без ограничения
HARD-TLS-ONLY | security | API доступен только по TLS с актуальными настройками
HARD-UNSAFE-API-CONSUMPTION | security | Ответы сторонних API валидируются перед использованием
HARD-VERSION-DISCLOSURE | security | Ответы не раскрывают версии ПО и инфраструктуры
HARD-WILDCARD-DOMAIN-MATCH | security | Шаблон домена с wildcard совпадает только с поддоменами указанного домена
HTTP-ABSOLUTE-URL-BASE-PATH | http-semantics | Абсолютные URL, которые формирует сервер, учитывают публичный адрес и базовый путь
HTTP-ACCEPT-LANGUAGE | http-semantics | Язык сообщений определяется Accept-Language с fallback
HTTP-BODY-ON-GET-DELETE | http-semantics | Тело в GET/DELETE игнорируется или отклоняется по контракту
HTTP-BODY-WITHOUT-CONTENT-TYPE | http-semantics | Тело без Content-Type обрабатывается предсказуемо
HTTP-CACHEABLE-RESPONSE-CACHE-CONTROL | http-semantics | Кэшируемый ответ содержит Cache-Control по итоговой политике
HTTP-COMPRESSION | http-semantics | Сжатие ответа согласуется через Accept-Encoding
HTTP-HEADER-REPEATED-LINES-ACCEPTED | http-semantics | Сотни повторяющихся строк одного заголовка в пределах лимита размера принимаются одинаково по HTTP/1.1 и HTTP/2
HTTP-HEADER-SIZE-LIMIT | http-semantics | Слишком большие заголовки отклоняются контролируемо
HTTP-HTTP2-RESOURCE-LIMITS | http-semantics | Параметры HTTP/2 со стороны клиента не заставляют сервер буферизовать и работать без предела
HTTP-OPTIONS-ALLOW | http-semantics | OPTIONS возвращает согласованный список методов
HTTP-PATH-PREFIX-SEGMENT-BOUNDARY | http-semantics | Правило по префиксу пути соблюдает границу сегмента
HTTP-REQUEST-SMUGGLING | http-semantics | Противоречивые Content-Length и Transfer-Encoding не приводят к request smuggling
HTTP-RESPONSE-FRAMING-HEADERS | http-semantics | Ответ не содержит одновременно Content-Length и Transfer-Encoding
HTTP-RESPONSE-MODE-HEADER-PARITY | http-semantics | Настроенные заголовки ответа присутствуют во всех режимах обработки ответа
HTTP-ROUTE-PROTOCOL-CONDITION | http-semantics | Условие маршрута для одного протокола не блокирует маршрут по другому разрешённому протоколу
HTTP-TRAILING-SLASH-CASE | http-semantics | Вариации пути (слэш в конце, регистр, двойной слэш) обрабатываются единообразно
HTTP-UNKNOWN-ROUTE | http-semantics | Неизвестный маршрут возвращает 404, а не 5xx или 200
HTTP-URL-LENGTH-LIMIT | http-semantics | Очень длинный URL отклоняется контролируемо
HTTP-VARY-HEADER | http-semantics | Кэшируемые ответы содержат корректный Vary
HTTP-VERSION-PARITY | http-semantics | Запросы по HTTP/2 и с предложением Upgrade h2c обслуживаются так же, как по HTTP/1.1
HTTP-WWW-AUTHENTICATE-SYNTAX | http-semantics | Заголовок WWW-Authenticate в ответе 401 соответствует синтаксису RFC
INJ-ARCHIVE-ENTRY-NAME-EVAL | security | Имена файлов внутри загруженного репозитория или архива не исполняются как код
INJ-CSV-FORMULA | security | Экспорт в CSV/XLSX нейтрализует формулы
INJ-FILTER-EXPRESSION | security | Выражения фильтрации (OData, RSQL, JSONPath, GraphQL where) не позволяют выйти за ограничения
INJ-HEADER-CRLF | security | CRLF в значениях не позволяет внедрять заголовки ответа
INJ-LLM-GENERATED-ACTIONS | security | Код и вызовы инструментов, сгенерированные LLM по вводу пользователя, не выполняют опасных действий
INJ-LOG-FORGING | security | Пользовательские данные не позволяют подделывать записи журналов
INJ-NOSQL | security | NoSQL-инъекция операторами запросов не исполняется
INJ-OS-COMMAND | security | Инъекция команд ОС не исполняется
INJ-PATH-TRAVERSAL | security | Обход каталогов через параметры файлов и путей невозможен
INJ-PROTOTYPE-POLLUTION | security | Специальные ключи __proto__ и constructor не меняют поведение сервера
INJ-REDOS | security | Пользовательский ввод не вызывает катастрофический backtracking в regex
INJ-REFLECTED-XSS | security | Параметры запроса не отражаются в HTML-ответе без экранирования
INJ-RESERVED-PATH-WRITE | security | Запись файлов через API не попадает в служебные каталоги
INJ-SCHEMA-IDENTIFIER-CODEGEN | security | Идентификаторы пользовательской схемы не внедряют код и SQL при генерации кода и DDL
INJ-SQL | security | SQL-инъекция во входных параметрах не исполняется
INJ-SSRF-PARAMETERS | security | Параметры с URL и хостами не дают доступа к внутренней сети
INJ-STORED-XSS | security | Сохранённые данные с HTML/JS не создают XSS у потребителей API
INJ-TEMPLATE-SSTI | security | Инъекция в серверные шаблоны не исполняется
INJ-UNSAFE-DESERIALIZATION | security | Небезопасная десериализация пользовательских данных невозможна
INJ-USER-CODE-EXECUTION | security | Пользовательский код, исполняемый сервером, не получает доступа к ОС, файлам и сети
INJ-USER-DATA-CALLABLE | security | Данные пользователя не позволяют вызвать серверную функцию вне allowlist
INJ-XXE | security | Внешние сущности XML не обрабатываются
OBS-AUDIT-TRAIL | observability | Чувствительные действия фиксируются в журнале аудита
OBS-CONFIG-ENDPOINT-ACCURATE | observability | Служебный эндпоинт конфигурации показывает фактические значения
OBS-HEALTH-ENDPOINTS | observability | Health-эндпоинты отражают состояние и не раскрывают детали
OBS-METRICS-LABEL-CARDINALITY | observability | Значения из запроса не создают неограниченно новых серий метрик
OBS-NO-SECRETS-IN-LOGS | observability | Логи не содержат паролей, токенов и ПДн в открытом виде
OBS-REQUEST-LOG-ALL-ATTEMPTS | observability | Журнал запроса с повторами содержит каждую попытку, включая последнюю
OBS-TELEMETRY-FORMAT | observability | Экспортируемая телеметрия соответствует документированной структуре и соглашениям OpenTelemetry
OBS-TRACE-PROPAGATION | observability | Контекст трассировки принимается и передаётся дальше
PAGE-BEYOND-LAST | pagination | Запрос страницы за последней возвращает пустой результат без ошибки
PAGE-CONCURRENT-MODIFICATION | pagination | Изменения коллекции во время обхода не приводят к дублям и пропускам сверх контракта
PAGE-CURSOR-TAMPERING | pagination | Подделанный или чужой курсор пагинации не раскрывает данные
PAGE-NEXT-LINK-VALID | pagination | Ссылка next ведёт на ту же коллекцию, сохраняет фильтры и работает
PAGE-SEARCH-SPECIAL-CHARS | pagination | Поиск со спецсимволами и wildcard не ломается и не расширяет выборку
PAGE-SORT-MULTI-KEY-PRIORITY | pagination | Сортировка по нескольким ключам соблюдает заданный клиентом порядок приоритета
PAGE-SORT-NULLS-TIES | pagination | Сортировка по полю с null и одинаковыми значениями детерминирована
PAGE-TOTAL-COUNT | pagination | Общее число элементов согласовано с суммой страниц
PERF-DEEP-PAGINATION | performance | Глубокая пагинация и большие выборки не деградируют неприемлемо
PERF-LATENCY-BASELINE | performance | Задержка ключевых операций в пределах SLO при обычной нагрузке
PERF-LOAD-THROUGHPUT | performance | Сервис выдерживает целевую нагрузку
PERF-NO-UNNEEDED-DEPENDENCY-CALLS | performance | Внешняя зависимость вызывается только когда её результат нужен
PERF-PAYLOAD-SIZE | performance | Размер ответов разумен и не растёт неограниченно
PERF-SOAK | performance | Длительная нагрузка не вызывает утечек и деградации
PERF-SPIKE | performance | Резкий всплеск нагрузки обрабатывается деградацией, а не отказом
PRIV-CONSENT-ENFORCEMENT | privacy | Обработка, требующая согласия, не выполняется без него
PRIV-DATA-MASKING | privacy | Чувствительные данные маскируются в ответах по политике
PRIV-ERASURE | privacy | Удаление персональных данных по запросу выполняется полностью
PRIV-IMPORT-URL-CREDENTIALS-NOT-STORED | privacy | Учётные данные из URL источника импорта не сохраняются после завершения импорта
PRIV-RESPONSE-FOREIGN-DATA | privacy | Ответ не содержит фрагментов данных других запросов и памяти процесса
PRIV-SELF-DATA-EXPORT | privacy | Экспорт собственных данных содержит только данные пользователя
REAL-BFF-ADMIN-API-AUDITCONTROLLER-GETENTRIES-OPERATION-ACCESS-PO | security | Confirm operation-specific authentication and authorization policy
REAL-BFF-ADMIN-API-AUTHCONTROLLER-CHANGEPASSWORD-MISSING-OR-INVAL | security | Cookie-authenticated endpoint rejects missing/invalid session
REAL-BFF-ADMIN-API-AUTHCONTROLLER-CHANGEPASSWORD-ROLE-MODEL-UNRES | security | Confirm minimum privilege policy for sensitive operation
REAL-BFF-ADMIN-API-AUTHCONTROLLER-CHANGEPASSWORD-WRONG-CURRENT-PA | security | Password change verifies current password
REAL-BFF-ADMIN-API-AUTHCONTROLLER-DELETESESSION-CROSS-ACCOUNT-SES | security | Session endpoint enforces session ownership
REAL-BFF-ADMIN-API-AUTHCONTROLLER-DELETESESSION-MISSING-OR-INVALI | security | Cookie-authenticated endpoint rejects missing/invalid session
REAL-BFF-ADMIN-API-AUTHCONTROLLER-DELETESESSION-ROLE-MODEL-UNRESO | security | Confirm minimum privilege policy for sensitive operation
REAL-BFF-ADMIN-API-AUTHCONTROLLER-GETSESSIONS-CROSS-ACCOUNT-SESSI | security | Session endpoint enforces session ownership
REAL-BFF-ADMIN-API-AUTHCONTROLLER-GETSESSIONS-MISSING-OR-INVALID | security | Cookie-authenticated endpoint rejects missing/invalid session
REAL-BFF-ADMIN-API-AUTHCONTROLLER-LOGIN-INVALID-CREDENTIALS | security | Login rejects invalid credentials
REAL-BFF-ADMIN-API-AUTHCONTROLLER-LOGOUT-MISSING-OR-INVALID-COOKI | security | Cookie-authenticated endpoint rejects missing/invalid session
REAL-BFF-ADMIN-API-AUTHCONTROLLER-LOGOUT-ROLE-MODEL-UNRESOLVED | security | Confirm minimum privilege policy for sensitive operation
REAL-BFF-ADMIN-API-COMPONENTTYPESCONTROLLER-GETTYPES-OPERATION-AC | security | Confirm operation-specific authentication and authorization policy
REAL-BFF-ADMIN-API-CONTENTCONTROLLER-CREATEITEM-OPERATION-ACCESS | security | Confirm operation-specific authentication and authorization policy
REAL-BFF-ADMIN-API-CONTENTCONTROLLER-CREATEITEM-ROLE-MODEL-UNRESO | security | Confirm minimum privilege policy for sensitive operation
REAL-BFF-ADMIN-API-CONTENTCONTROLLER-GETITEMS-OPERATION-ACCESS-PO | security | Confirm operation-specific authentication and authorization policy
REAL-BFF-ADMIN-API-CONTENTCONTROLLER-GETSOURCES-OPERATION-ACCESS | security | Confirm operation-specific authentication and authorization policy
REAL-BFF-ADMIN-API-CONTENTCONTROLLER-REMOVEITEM-OPERATION-ACCESS | security | Confirm operation-specific authentication and authorization policy
REAL-BFF-ADMIN-API-CONTENTCONTROLLER-REMOVEITEM-ROLE-MODEL-UNRESO | security | Confirm minimum privilege policy for sensitive operation
REAL-BFF-ADMIN-API-CONTENTCONTROLLER-UPDATEITEM-OPERATION-ACCESS | security | Confirm operation-specific authentication and authorization policy
REAL-BFF-ADMIN-API-CONTENTCONTROLLER-UPDATEITEM-ROLE-MODEL-UNRESO | security | Confirm minimum privilege policy for sensitive operation
REAL-BFF-ADMIN-API-LAYOUTSCONTROLLER-ARCHIVE-OPERATION-ACCESS-POL | security | Confirm operation-specific authentication and authorization policy
REAL-BFF-ADMIN-API-LAYOUTSCONTROLLER-ARCHIVE-ROLE-MODEL-UNRESOLVE | security | Confirm minimum privilege policy for sensitive operation
REAL-BFF-ADMIN-API-LAYOUTSCONTROLLER-GETCURRENTVERSIONS-OPERATION | security | Confirm operation-specific authentication and authorization policy
REAL-BFF-ADMIN-API-LAYOUTSCONTROLLER-GETLANGUAGES-OPERATION-ACCES | security | Confirm operation-specific authentication and authorization policy
REAL-BFF-ADMIN-API-LAYOUTSCONTROLLER-GETNODES-OPERATION-ACCESS-PO | security | Confirm operation-specific authentication and authorization policy
REAL-BFF-ADMIN-API-LAYOUTSCONTROLLER-GETSCREEN-OPERATION-ACCESS-P | security | Confirm operation-specific authentication and authorization policy
REAL-BFF-ADMIN-API-LAYOUTSCONTROLLER-GETSCREENS-OPERATION-ACCESS | security | Confirm operation-specific authentication and authorization policy
REAL-BFF-ADMIN-API-LAYOUTSCONTROLLER-GETVERSIONS-OPERATION-ACCESS | security | Confirm operation-specific authentication and authorization policy
REAL-BFF-ADMIN-API-LAYOUTSCONTROLLER-PUBLISH-OPERATION-ACCESS-POL | security | Confirm operation-specific authentication and authorization policy
REAL-BFF-ADMIN-API-LAYOUTSCONTROLLER-PUBLISH-ROLE-MODEL-UNRESOLVE | security | Confirm minimum privilege policy for sensitive operation
REAL-BFF-ADMIN-API-LAYOUTSCONTROLLER-SAVETRANSLATION-OPERATION-AC | security | Confirm operation-specific authentication and authorization policy
REAL-BFF-ADMIN-API-LAYOUTSCONTROLLER-SAVETRANSLATION-ROLE-MODEL-U | security | Confirm minimum privilege policy for sensitive operation
REAL-BFF-ADMIN-API-LAYOUTSCONTROLLER-TOGGLELANGUAGE-OPERATION-ACC | security | Confirm operation-specific authentication and authorization policy
REAL-BFF-ADMIN-API-LAYOUTSCONTROLLER-TOGGLELANGUAGE-ROLE-MODEL-UN | security | Confirm minimum privilege policy for sensitive operation
REAL-BFF-ADMIN-API-LAYOUTSCONTROLLER-UPDATECOMPONENT-OPERATION-AC | security | Confirm operation-specific authentication and authorization policy
REAL-BFF-ADMIN-API-LAYOUTSCONTROLLER-UPDATECOMPONENT-ROLE-MODEL-U | security | Confirm minimum privilege policy for sensitive operation
REAL-BFF-ADMIN-API-LAYOUTSCONTROLLER-VALIDATE-OPERATION-ACCESS-PO | security | Confirm operation-specific authentication and authorization policy
REAL-BFF-ADMIN-API-LAYOUTSCONTROLLER-VALIDATE-ROLE-MODEL-UNRESOLV | security | Confirm minimum privilege policy for sensitive operation
REAL-MOBILE-CLIENT-API-ACCEPTDOCUMENTS-CROSS-PRINCIPAL-OR-STALE-R | security | Document acceptance is bound to the correct principal and revision
REAL-MOBILE-CLIENT-API-ACCEPTDOCUMENTS-GUEST-VS-AUTHENTICATED | security | Guest and authenticated document access follow distinct policies
REAL-MOBILE-CLIENT-API-GETDOCUMENTSHISTORY-GUEST-VS-AUTHENTICATED | security | Guest and authenticated document access follow distinct policies
REAL-MOBILE-CLIENT-API-GETUNSIGNEDDOCUMENTS-GUEST-VS-AUTHENTICATE | security | Guest and authenticated document access follow distinct policies
REAL-MOBILE-CLIENT-API-LOGOUT-MISSING-EXPIRED-OR-REFRESH-TOKEN | security | Logout requires a valid access token
REAL-MOBILE-CLIENT-API-ONSTART-ANONYMOUS-VS-API-KEY | security | Startup endpoint matches the documented API-key policy
REAL-MOBILE-CLIENT-API-REFRESH-EXPIRED-OR-INVALID-REFRESH-TOKEN | security | Authentication endpoint rejects invalid credentials
REAL-MOBILE-CLIENT-API-SENDCODE-INVALID-API-KEY | security | Authentication endpoint rejects invalid credentials
REAL-MOBILE-CLIENT-API-VERIFYCODE-INVALID-API-KEY | security | Authentication endpoint rejects invalid credentials
REQ-CONTRACT-CONTRADICTS-SPEC | requirements | Поведение по контракту не противоречит ТЗ
REQ-CONTRACT-SELF-CONSISTENCY | requirements | Контракт не противоречит сам себе и своей прежней версии
REQ-CROSS-CLIENT-CONSISTENCY | requirements | Одно правило продукта одинаково в API разных клиентов
REQ-SPEC-NOT-IN-CONTRACT | requirements | Требование ТЗ не потеряно по пути в контракт и реализацию
REQ-UNSPECIFIED-BEHAVIOR-PROBE | requirements | Неописанное поведение выясняется тестом и сравнивается со стандартом и здравым смыслом
RES-ALLOCATED-VALUE-RELEASE | resources | Выделенное из пула значение не выдаётся повторно, пока прежний владелец не удалён окончательно
RES-ARCHIVE-RESTORE | resources | Архивирование и восстановление сохраняют данные и связи
RES-BULK-LIMITS | resources | Массовые операции соблюдают лимиты и сообщают о каждом элементе
RES-BULK-SINGLE-VALIDATION-PARITY | resources | Массовая операция валидирует так же, как одиночная
RES-CACHE-EXPLICIT-INVALIDATION | resources | Явный сброс кэша через API удаляет закэшированные ответы
RES-CACHE-KEY-COMPLETENESS | resources | Серверный кэш различает ответы по всем значимым параметрам и по типу ресурса
RES-CREATE-RESPONSE-MATCHES-READ | resources | Ответ на создание и изменение совпадает с последующим чтением
RES-CRUD-CYCLE | resources | Полный жизненный цикл ресурса: создание, чтение, изменение, удаление
RES-DB-OBJECT-NAMES | resources | API по схеме БД работает с объектами в любом регистре, со спецсимволами и зарезервированными именами
RES-DELETE-WITH-DEPENDENTS | resources | Удаление ресурса с зависимыми объектами выполняется по правилам каскада
RES-DRAFT-PUBLISH-FIDELITY | resources | Публикация черновика переносит все изменения и не ломает связи других объектов
RES-EXPORT-IMPORT-ROUNDTRIP | resources | Данные, выгруженные API, принимаются им же обратно без изменений
RES-IMMUTABLE-FIELDS | resources | Неизменяемые поля нельзя изменить после создания
RES-LARGE-RELATION-SET | resources | Тысячи связанных объектов не дают 5xx из-за лимитов СУБД на параметры запроса
RES-LIST-REFLECTS-CHANGES | resources | Списки и счётчики отражают создание, изменение и удаление
RES-READ-AFTER-WRITE | resources | Чтение после записи соответствует модели согласованности
RES-REFERENTIAL-INTEGRITY | resources | Ссылка на несуществующий или чужой связанный ресурс отклоняется
RES-RELATION-CONNECT-DISCONNECT-CONFLICT | resources | Подключение с позицией относительно отключаемой в том же запросе связи обрабатывается корректно
RES-RELATION-NULL-TARGET-ROWS | resources | Связь многие-ко-многим возвращает записи связующей таблицы с пустой ссылкой
RES-RELATION-ORDER-STABLE | resources | Изменение связанного ресурса не меняет ручной порядок связей у другой стороны
RES-RELATIONS-SHARED-JUNCTION-ISOLATION | resources | Связи через общую связующую таблицу возвращают каждая только свои данные
RES-SERVER-GENERATED-FIELDS | resources | Клиент не может задать серверные поля (id, createdAt, status, version)
RES-SOFT-DELETE-VISIBILITY | resources | Мягко удалённые ресурсы не видны в обычных операциях
RES-SYSTEM-OBJECT-PROTECTED | resources | Встроенные системные объекты защищены от удаления и изменения при любой конфигурации
RES-TIMESTAMPS | resources | Метки времени создания и изменения ведут себя корректно
RES-UNIQUENESS-NORMALIZATION | resources | Уникальность не обходится вариациями значения
RES-UPDATE-MISSING | resources | Изменение несуществующего ресурса не создаёт его неявно
RESIL-BROKER-DOWN | resilience | Недоступность брокера сообщений не теряет события
RESIL-CIRCUIT-BREAKER | resilience | Circuit breaker размыкается и восстанавливается по политике
RESIL-DEPENDENCY-DOWN | resilience | Недоступность зависимости даёт контролируемую ошибку
RESIL-DEPENDENCY-TLS-RECOVERY | resilience | Проверка доступности внешнего бэкенда проверяет его сертификат и восстанавливается без перезапуска
RESIL-ENCRYPTION-KEY-ROTATION | resilience | Нерасшифровываемое после смены ключа значение не ломает чтение и сохранение остальных данных
RESIL-GRACEFUL-SHUTDOWN | resilience | Перезапуск экземпляра не обрывает выполняющиеся запросы
RESIL-PARTIAL-DEGRADATION | resilience | Отказ некритичной зависимости не ломает основной функционал
RESIL-TLS-CERT-RELOAD | resilience | Сервер подхватывает заменённый TLS-сертификат без перезапуска
RESOURCE-CREATE-READ | resources | Created resource can be read back
RESOURCE-READ-MISSING | resources | Reading a missing resource returns a documented error
REST-204-NO-BODY | contract | Ответ 204 без тела
REST-ACCEPT-NEGOTIATION | contract | Согласование Accept
REST-API-VERSION-COMPATIBILITY | contract | Совместимость версий API
REST-ASYNC-202 | contract | Асинхронное принятие задачи 202
REST-AUTH-ERROR-NO-LEAK | security | Ошибки аутентификации без утечки
REST-BATCH-PARTIAL-FAILURE | contract | Частичный сбой batch
REST-CACHE-CONDITIONAL-GET | contract | ETag/Last-Modified conditional GET
REST-CONCURRENT-UPDATE | resilience | Конкурентное обновление
REST-CONTENT-TYPE-JSON | contract | Content-Type и JSON-формат
REST-CORRELATION-ID | errors | Correlation ID
REST-CORS-POLICY | security | Политика CORS
REST-DATE-TIME-TZ | validation | Дата, время и timezone
REST-DECIMAL-PRECISION | resources | Точность decimal
REST-DELETE-REPEAT | contract | Повторное удаление
REST-DUPLICATE-UNIQUE-KEY | resources | Дублирование уникального ключа
REST-EMPTY-VALUES | validation | Пустые объект, массив и строка
REST-ENUM-VALUES | validation | Допустимые и неизвестные enum
REST-ERROR-RETRY-AFTER | contract | Retry-After при временной ошибке
REST-ERROR-SCHEMA | contract | Стабильная схема ошибок
REST-ERROR-STATUS-BODY | contract | Согласованность статуса и тела ошибки
REST-ETAG-IF-MATCH | resilience | Условное обновление If-Match
REST-FILTER-EQUIVALENT-FORMS | pagination | Логически эквивалентные формы фильтра дают одинаковый ответ
REST-FILTER-INVALID | pagination | Невалидный фильтр
REST-FILTER-OPERATION-PARITY | pagination | Один фильтр даёт согласованный результат в списке, агрегации и вложенной выборке
REST-FILTER-OPERATOR-TYPE-MATRIX | pagination | Каждый оператор фильтра работает для каждого допустимого типа поля и возвращает ровно подходящие записи
REST-FILTER-RELATION-NO-DUPLICATES | pagination | Фильтр по полю связанной коллекции возвращает каждую запись один раз
REST-FILTER-SORT-COMPOSITION | pagination | Filtering and sorting compose correctly
REST-FILTER-SORT-PAGINATION | pagination | Комбинация filter/sort/pagination
REST-HEAD-GET-CONSISTENCY | http-semantics | HEAD response is consistent with GET
REST-IDEMPOTENCY-KEY | contract | Повтор с Idempotency-Key
REST-IDEMPOTENCY-RETRY | idempotency | Retry does not duplicate an idempotent operation's effect
REST-JSON-DUPLICATE-KEYS | validation | Дублирующиеся ключи JSON
REST-MASS-ASSIGNMENT | security | Mass assignment защищённых полей
REST-METHOD-NOT-ALLOWED | http-semantics | Unsupported HTTP method is rejected
REST-NULL-VS-OMITTED | validation | Null и отсутствующее поле
REST-NUMERIC-BOUNDARIES | validation | Числовые границы
REST-OBJECT-LEVEL-AUTHZ | security | Object-level authorization
REST-OPEN-REDIRECT | security | Валидация redirect URL
REST-OPTIONAL-EMPTY-VALUE | validation | Отсутствующий и пустой параметр
REST-PAGINATION-BOUNDARIES | pagination | Pagination handles boundary values correctly
REST-PAGINATION-LIMITS | pagination | Границы размера страницы
REST-PAGINATION-STABLE-ORDER | pagination | Стабильный порядок пагинации
REST-PATCH-PARTIAL-UPDATE | contract | Семантика PATCH
REST-PATH-PARAM-ENCODING | contract | Кодирование path-параметров
REST-POST-LOCATION | contract | Location при создании
REST-PUT-REPLACEMENT | contract | Семантика PUT
REST-QUERY-ENCODING | contract | Кодирование query-параметров
REST-RATE-LIMIT | security | Ограничение частоты запросов
REST-READONLY-WRITEONLY | contract | Поля readOnly/writeOnly
REST-REQUEST-SIZE-LIMIT | validation | Лимит размера тела
REST-REQUIRED-PARAM-MISSING | validation | Отсутствует обязательный параметр
REST-RETRY-TRANSIENT-ERROR | contract | Retry после временной ошибки
REST-SECURITY-HEADERS | security | Защитные HTTP-заголовки
REST-SENSITIVE-CACHE-CONTROL | security | Кэширование чувствительных ответов
REST-SENSITIVE-DATA | security | Отсутствие чувствительных данных в ответах
REST-SORT-INVALID-FIELD | pagination | Сортировка по неизвестному полю
REST-SSRF-URL-FETCH | security | Контроль server-side URL fetch
REST-STATE-TRANSITIONS | resources | Переходы состояния ресурса
REST-STATUS-CODE-CONTRACT | contract | Статус ответа соответствует контракту
REST-STRING-LENGTH-BOUNDARIES | validation | Границы длины строки
REST-TIMEOUT-BUDGET | contract | Таймаут и бюджет времени
REST-TYPE-MISMATCH | validation | Несовпадение типа поля
REST-UNICODE-NORMALIZATION | validation | Unicode и нормализация
REST-UNKNOWN-FIELDS | contract | Политика неизвестных полей
REST-UNSUPPORTED-CONTENT-TYPE | validation | Неподдерживаемый Content-Type запроса
REST-VALIDATION-ATOMICITY | contract | Атомарность ошибки валидации
SEC-ALT-REPRESENTATION-ACCESS | security | Закрытый ресурс недоступен ни через одно альтернативное представление
SEC-AUTHN-MALFORMED | security | Malformed credential is rejected
SEC-AUTHN-MISSING | security | Protected operation rejects missing credentials
SEC-AUTHN-SCHEMES-SUPPORTED | security | Все задокументированные схемы Authorization принимаются на своих эндпоинтах
SEC-AUTHZ-ASYNC-JOB | security | Authorization is rechecked for asynchronous job access
SEC-AUTHZ-CACHE-ISOLATION | security | Authorization context is respected by caches
SEC-AUTHZ-DYNAMIC-VARIABLES | security | Динамические переменные в правилах доступа действуют как эквивалентные статические значения
SEC-AUTHZ-ERROR-LEAK | security | Authorization failures do not disclose protected data
SEC-AUTHZ-EXPLICIT-OVER-INHERITED | security | Явное пониженное право на дочерний объект имеет приоритет над унаследованным
SEC-AUTHZ-FUNCTION | security | User without required permission cannot invoke operation
SEC-AUTHZ-LIST-CHECK-CONSISTENCY | security | Перечисление субъектов и объектов с доступом согласовано с точечной проверкой
SEC-AUTHZ-METHOD-MATRIX | security | Authorization is enforced for every method
SEC-AUTHZ-PATH-RULE-PRECEDENCE | security | Правила доступа по путям применяются по наиболее точному совпадению, независимо от порядка объявления
SEC-AUTHZ-RECREATED-IDENTITY | security | Права и согласия не переходят к пересозданному пользователю с тем же логином
SEC-AUTHZ-REVOKE-ROLE | security | Role revocation takes effect within policy window
SEC-AUTHZ-ROLE-POSITIVE-MATRIX | security | Разрешённая операция работает для каждой роли с правом, а не только для администратора
SEC-AUTHZ-RULE-READ-WRITE-PARITY | security | Условие прав по связанной записи действует в записи так же, как в чтении
SEC-BOLA-BULK | security | Bulk endpoint enforces ownership per item
SEC-CLONE-FIELD-PERMISSIONS | security | Копирование ресурса соблюдает полевые права чтения и создания
SEC-CONFUSED-DEPUTY | security | Действия во внешней системе от имени пользователя выполняются только с его правами
SEC-DISABLED-FEATURE-ENFORCED | security | Отключённая настройкой функция недоступна через все API и не попадает в токены
SEC-FAIL-CLOSED-INPUT | security | Неожиданный тип, пустое или отсутствующее поле проверки безопасности ведёт к отказу, а не к пропуску проверки
SEC-HORIZONTAL-ESCALATION | security | Peer user cannot access peer-only protected action
SEC-IDENTITY-PROOF-OF-POSSESSION | security | Заявленная клиентом идентичность без доказательства владения не даёт прав и льгот
SEC-INTERNAL-CONTROL-PARAMS | security | Заголовки и параметры подключения клиента не задают внутренние управляющие параметры операции
SEC-OPAQUE-ID-INTEGRITY | security | Непрозрачный идентификатор, выданный сервером, проверяется на подлинность
SEC-OWNERSHIP-DELETE | security | User cannot delete another owner’s resource
SEC-OWNERSHIP-EXPORT | security | Export/report endpoints enforce ownership and tenant boundaries
SEC-OWNERSHIP-READ | security | User cannot read another owner’s resource
SEC-OWNERSHIP-REFERENCE-INDIRECT | security | Indirect resource references preserve authorization
SEC-OWNERSHIP-UPDATE | security | User cannot modify another owner’s resource
SEC-POLICY-TEMPLATE-USER-DATA | security | Данные пользователя, подставляемые в шаблон политики доступа, не работают как wildcard
SEC-READONLY-MODE-ENFORCED | security | Режим только для чтения запрещает изменения любым запросом, а не по первому ключевому слову
SEC-ROLE-ADMIN-SELF-TARGET | security | Административная операция над собственной учёткой обрабатывается по политике без 5xx
SEC-ROLE-BULK-ADMIN | security | Bulk admin actions require privilege for every target
SEC-ROLE-LOW-TO-HIGH | security | Low-privilege role cannot perform privileged action
SEC-ROLE-MASS-ASSIGN | security | Mass assignment cannot elevate privileges
SEC-ROLE-SELF-ASSIGN | security | User cannot grant self a higher role
SEC-SCOPE-EXTRA-UNTRUSTED | security | Client cannot add scopes by request parameter
SEC-SCOPE-MISSING | security | Token without required scope is denied
SEC-TENANT-CREATE | security | Client cannot assign resource to another tenant
SEC-TENANT-HEADER-SPOOF | security | Untrusted tenant header cannot override identity context
SEC-TENANT-READ | security | Tenant A cannot read tenant B data
SEC-TENANT-SEARCH | security | Tenant filter cannot be bypassed in list/search
SEC-TENANT-WRITE | security | Tenant A cannot mutate tenant B data
SEC-TOKEN-AUDIENCE | security | Token for another audience is rejected
SEC-TOKEN-EXPIRED | security | Expired access token is rejected
SEC-TOKEN-ISSUER | security | Token from untrusted issuer is rejected
SEC-TOKEN-REFRESH-REPLAY | security | Refresh-token replay is rejected or rotated
SEC-TOKEN-REVOKED | security | Revoked token cannot be reused
SEC-TOKEN-SIGNATURE | security | Token with invalid signature is rejected
SEC-VERTICAL-ESCALATION | security | Lower role cannot invoke higher-role route via alternate method
SECURITY-AUTH-REQUIRED | security | Protected operation rejects unauthenticated requests
SECURITY-AUTHZ-CROSS-USER | security | User cannot access another user's resource
VAL-ALL-ERRORS-REPORTED | validation | Ошибки валидации нескольких полей возвращаются по контракту (все сразу или первая)
VAL-ARRAY-ITEMS-BOUNDARIES | validation | Границы массивов: minItems, maxItems, uniqueItems
VAL-BODY-ENCODING | validation | Тело в неверной кодировке или с BOM обрабатывается предсказуемо
VAL-BOOLEAN-COERCION | validation | Неявное приведение типов для boolean не происходит
VAL-CASE-SENSITIVITY | validation | Чувствительность к регистру идентификаторов, email и enum соответствует контракту
VAL-DEEP-NESTING | validation | Чрезмерно вложенный JSON отклоняется без деградации сервиса
VAL-DEFAULT-VALUES | validation | Опущенные необязательные поля получают задокументированные значения по умолчанию
VAL-DEFERRED-FAILURE | validation | Принятые при записи данные не вызывают 5xx в зависимых операциях
VAL-DEPENDENT-FIELDS | validation | Взаимозависимые поля валидируются совместно
VAL-DYNAMIC-VARIABLES-TYPE | validation | Правило валидации с динамической переменной сравнивает значения по типу поля
VAL-JSON-TOP-LEVEL-TYPE | validation | Неожиданный тип корня JSON отклоняется
VAL-LARGE-COLLECTION-PAYLOAD | validation | Массив с очень большим числом элементов отклоняется или обрабатывается в пределах лимитов
VAL-MALFORMED-JSON | validation | Синтаксически некорректный JSON отклоняется
VAL-MONEY-AMOUNT | validation | Денежные суммы: знак, точность и валюта валидируются
VAL-NESTED-OBJECT-ERRORS | validation | Ошибка во вложенном объекте указывает точный путь к полю
VAL-NUMBER-REPRESENTATION | validation | Альтернативные записи чисел обрабатываются по контракту
VAL-PATH-ID-FORMAT | validation | Неверный формат идентификатора в пути не вызывает 5xx
VAL-QUERY-ARRAY-FORMAT | validation | Массивы в query передаются в задокументированном формате
VAL-QUERY-PARAM-POLLUTION | validation | Дублирующиеся query-параметры обрабатываются однозначно
VAL-RANGE-ORDER | validation | Начало диапазона не может быть позже конца
VAL-REGEX-PATTERN | validation | Поле с pattern принимает только совпадающие значения
VAL-REQUIRED-HEADERS | validation | Обязательные и форматные заголовки валидируются
VAL-SPECIAL-CHARACTERS | validation | Спецсимволы, emoji и управляющие символы сохраняются или отклоняются корректно
VAL-STRING-FORMAT | validation | Форматы строк (email, uuid, uri, date, phone) проверяются
VAL-TIGHTENED-RULES-STORED-DATA | validation | Сохранённые до ужесточения валидации значения обрабатываются одинаково на всех путях записи
VAL-UPLOADED-SCHEMA-FORMATS | validation | Загружаемая клиентом схема с документированными форматами принимается без ложных предупреждений
VAL-WHITESPACE-HANDLING | validation | Пробелы по краям и строки из пробелов обрабатываются согласованно
WS-HANDSHAKE-AUTH | websocket | Установление соединения требует аутентификации
WS-MALFORMED-MESSAGE | websocket | Некорректные сообщения не рвут соединение без ответа
WS-MESSAGE-LIMITS | websocket | Размер и частота сообщений ограничены
WS-MULTIPLE-ENDPOINTS-INDEPENDENT | websocket | Несколько WebSocket-эндпоинтов на разных путях работают независимо
WS-ORIGIN-CHECK | websocket | Проверка Origin защищает от cross-site WebSocket hijacking
WS-RECONNECT-RESUME | websocket | Переподключение восстанавливает подписки без потери и дублей сверх контракта
WS-SLOW-CONSUMER-NO-SILENT-LOSS | websocket | Медленный клиент подписки не теряет сообщения молча
WS-SUBSCRIPTION-AUTHZ | websocket | Подписки и сообщения авторизуются по каждому каналу
WS-SUBSCRIPTION-EVENTS-DELIVERED | websocket | Подписка получает события создания, изменения и удаления
WS-TOKEN-EXPIRY | websocket | Истечение или отзыв токена учитывается в открытом соединении
```
