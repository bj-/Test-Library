# Перекрёстное ревью новых идей выгрузки багов

Партия `directus`, идей: 10; вариант пакета — без решений Claude — независимое ревью.
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

## Идея 1. Один и тот же фильтр (в том числе по полиморфной связи и на нескольких уровнях вложенности) принимается и даёт согласованный результат во всех операциях — список, агрегация (count = числу записей списка), вложенная выборка (deep), экспорт

### directus/directus#25975 — Api / Graphql: Aggregation with filtering on M2A field does not work anymore

Ссылка: https://github.com/directus/directus/issues/25975

- **Паттерн:** Фильтр по полиморфной связи одинаково работает в списке, агрегации и вложенных выборках
- **Условие:** Фильтр по полю целевой коллекции связи many-to-any (item__collection), операции: список, агрегация, вложенный фильтр
- **Действие:** Применить один и тот же фильтр по полиморфной связи в запросе списка, в агрегации (count) и во вложенной выборке
- **Ожидание:** Во всех операциях фильтр принимается и результат согласован (count = число записей списка)
- **Источник ожидания:** Документация фильтров (одинаковы для всех операций чтения), здравый смысл
- **Почему не подошла ближайшая запись:** REST-FILTER-EQUIVALENT-FORMS сравнивает формы записи фильтра, а не один фильтр в разных операциях (список, агрегация, deep)

Первоисточник:

````text
### Describe the Bug

When we moved from version 11.8.0 to version 11.12.0 we noticed that aggregating results with filtering on an Many To Any (Builder / M2A) stopped working with the following error:
```
      "message": "You don't have permission to access fields \"item__footer\", \"title\" in collection \"pages_blocks\" or they do not exist. Queried in \"blocks\".",
```

It seems to be related to this issue: https://github.com/directus/directus/issues/25892

### To Reproduce

Run the following request:
```http
POST http://localhost:8055/graphql HTTP/1.1
X-Request-Type: GraphQL
Authorization: Bearer password
Content-Type: application/json

query {
  pages_aggregated(filter: {_and: [{blocks: {item__footer: {title: {_contains: "Home"}}}}]}) {
    count {
      id
    }
  }
}
```

on the attached database:
Email: admin@directus.io
Password: password

[issue_with_m2a.sql.zip](https://github.com/user-attachments/files/22885662/issue_with_m2a.sql.zip)

### Directus Version

11.12.0

### Hosting Strategy

Self-Hosted (Custom)

### Database

Postgres
````

### directus/directus#25892 — Deep filtering with M2A fields fails in since v11.9.0

Ссылка: https://github.com/directus/directus/issues/25892

- **Паттерн:** Фильтр по полиморфной связи одинаково работает в списке, агрегации и вложенных выборках
- **Условие:** Вложенная выборка через связь many-to-any с аргументом filter по полю целевой коллекции несколько уровней вглубь
- **Действие:** Выполнить запрос с вложенным фильтром item__collection на втором уровне вложенности
- **Ожидание:** 2xx, отфильтрованные данные
- **Источник ожидания:** Документация фильтров, здравый смысл
- **Почему не подошла ближайшая запись:** Нет записи о согласованности фильтра по полиморфной связи в разных операциях; кластер с directus#25975

Первоисточник:

````text
### Describe the Bug

When applying a GraphQL deep filter on a many-to-any (m2a) field, the query now returns a server error. This functionality worked as expected in version 11.8.0, and the issue appears to be related to a recent change in how filters are processed.

### To Reproduce

1. Create a collection with a m2a to a collection
You would want to have a graphql call that will have to look inside the m2a field and uses a deep filter

Credentials:
[admin@directus.io](mailto:admin@directus.io)
password
Grapqhl with issue
```{
  articles {
    articles {
      item {
        ... on articles {
          articles(
            filter: {item__articles: {articles: {item__articles: {title: {_eq: "Example 1"}}}}}
          ) {
            id
          }
        }
      }
    }
  }
}
```

[m2a_filter_deep_issue.sql.zip](https://github.com/user-attachments/files/22520609/m2a_filter_deep_issue.sql.zip)

### Directus Version

v11.9.0 -> 11.11.0 -> 11.12.0

### Hosting Strategy

Self-Hosted (Docker Image)

### Database

PostgreSQL 13+
````

## Идея 2. Каждая динамическая переменная в правилах доступа и валидации ($CURRENT_USER, его поля, $CURRENT_ROLES, $CURRENT_POLICIES) даёт тот же результат, что эквивалентное статическое значение, — в том числе для целочисленных полей и списков (_in); позитивная матрица переменных

### directus/directus#23695 — Item Permissions Not Working with $CURRENT_POLICIES

Ссылка: https://github.com/directus/directus/issues/23695

- **Паттерн:** Каждая динамическая переменная в правиле доступа даёт доступ так же, как эквивалентное статическое значение
- **Условие:** Правило изменения с фильтром по связи с политиками и {_in: [$CURRENT_POLICIES]}; аналогично $CURRENT_USER, $CURRENT_ROLES
- **Действие:** Для каждой динамической переменной задать правило и выполнить операцию пользователем, которому оно разрешает доступ
- **Ожидание:** Операция разрешена для всех переменных одинаково
- **Источник ожидания:** Документация динамических переменных
- **Почему не подошла ближайшая запись:** SEC-AUTHZ-ROLE-POSITIVE-MATRIX перебирает роли, а не механизмы правил; матрицы динамических переменных нет; кластер с directus#24848

Первоисточник:

````text
### Describe the Bug

We need a collection where each item is writable only by a specific group of users.

We attempted to implement this using update item permissions with a relation to `directus_policies`, but it didn't work. Only a relation to `directus_users` or `directus_roles` worked as expected.

### To Reproduce

Add a many-to-many (m2m) relation to `directus_policies` from a collection.
Create a Policy with an Custom Update Item Permission with $CURRENT_POLICIES.

```
{
    "write_policies": {
        "directus_policies_id": {
            "_in": [
                "$CURRENT_POLICIES"
            ]
        }
    }
}
```

Login with a user that has no other write policy than this for the collection you changed - It wont be writable, but it should.

## Write Permissions by Role or User works
If you repeat the same with a link to `directus_roles` and use `$CURRENT_ROLES` or if you link to `directus_users` and use `$CURRENT_USER` it works as expected. 

## Documentation is missing, too

If I take a look at the documentation of the Custom Permissions at https://docs.directus.io/user-guide/user-management/permissions.html#configure-custom-permissions I find a link to https://docs.directus.io/user-guide/content-module/filters.html#dynamic-variables which only has the variables listed, but not how to use them, but https://docs.directus.io/reference/filter-rules.html#logical-operators is linked and there I find an example. 
That is quite deeply nested hidden in the documentation and I only found it while writing this issue, not while searching for `$CURRENT_POLICIES` while trying to figure out how that _dynamic variable_ works. It would be great if that could be improved, too :-) 
 
 

### Directus Version

v11.1.0

### Hosting Strategy

Self-Hosted (Docker Image)

### Database

PostgreSQL 13.16
````

### directus/directus#24848 — Field validations in Create/Update policies doesnt work if it includes checking with primary integer key

Ссылка: https://github.com/directus/directus/issues/24848

- **Паттерн:** Правило валидации с динамической переменной сравнивает значения независимо от представления числа
- **Условие:** Правило валидации при создании сравнивает целочисленное поле с переменной текущего пользователя ($CURRENT_USER.company)
- **Действие:** Создать связанные записи, где поле равно значению переменной пользователя (целое число)
- **Ожидание:** 2xx: значение совпадает
- **Источник ожидания:** Документация правил валидации, здравый смысл
- **Почему не подошла ближайшая запись:** REST-TYPE-MISMATCH и VAL-BOOLEAN-COERCION проверяют отклонение неверного типа; позитивной проверки правил с динамическими переменными нет

Первоисточник:

````text
### Describe the Bug

#### **Description**  
I have the following collections in Directus:  
- `company`  (INT primary key)
- `specialization`  (INT primary key)
- `directus_users` (which includes a `company` field with a **many-to-one** relationship)  

Directus automatically created a **junction table** called `company_specializations` for the many-to-many relationship between `company` and `specialization`.  

I want to restrict users from creating **company specializations** for companies they don’t belong to. To enforce this, I set up a **field validation rule** on the `company_specializations` collection for the `create` operation:  

```json
{
    "_and": [
        {
            "company_id": {
                "_eq": "$CURRENT_USER.company"
            }
        }
    ]
}
```

However, when attempting to create a specialization for a company, the validation fails with the following error:  

#### **Steps to Reproduce**  
1. Send a **POST** request to create specializations for a company:  

   ```http
   POST /items/company/1
   Content-Type: application/json
   ```

   **Request Body:**  
   ```json
   {
       "specialization": [ 
           { "specialization_id": 2 },
           { "specialization_id": 1 }
       ]
   }
   ```

2. Directus returns the following error response:  

   ```json
   {
       "errors": [
           {
               "message": "Validation failed for field \"company_id\". Value has to be \"1\".",
               "extensions": {
                   "field": "company_id",
                   "type": "eq",
                   "valid": 1,
                   "code": "FAILED_VALIDATION"
               }
           }
       ]
   }
   ```

#### **Expected Behavior**  
- The validation rule should correctly compare the `company_id` field against the **current user's company ID** without type mismatches.  
- The specialization should be created successfully if the user belongs to the specified company.  

#### **Actual Behavior**  
- Directus appears to be comparing a **string value** (`"$CURRENT_USER.company"`) with an **integer value** (`company_id`).  
- This results in a validation failure, even though the values are logically equal.  

#### **Additional Information**  
- To confirm that the issue is **type-related**, I tested the same setup using collections where **all primary keys were UUIDs**, and the validation worked fine.  
- This suggests that Directus does not properly handle type conversions when validating **integer-based …[обрезано]
````

## Идея 3. Задача по расписанию продолжает срабатывать после длительной непрерывной работы процесса (больше 24,8 суток — предел 32-битного таймера в миллисекундах); проверка — длительная работа или сдвиг времени на стенде

### directus/directus#25855 — API: Schedule Flow not being triggered after some time running

Ссылка: https://github.com/directus/directus/issues/25855

- **Паттерн:** Плановая задача продолжает срабатывать после длительной непрерывной работы сервиса
- **Условие:** Задача по расписанию (cron), процесс работает без перезапуска дольше ~25 дней
- **Действие:** Создать ежедневную задачу по расписанию и наблюдать срабатывания при длительной работе (или со сдвигом времени)
- **Ожидание:** Задача срабатывает по расписанию независимо от времени работы процесса
- **Источник ожидания:** Здравый смысл
- **Почему не подошла ближайшая запись:** ASYNC-JOB-LIFECYCLE проверяет статусы одной задачи, а не регулярность срабатывания расписания при длительной работе

Первоисточник:

````text
### Describe the Bug

We have a Flow set to run every day at 23h (0 23 * * *) and for the last X days this Flow is being running as intended.
Although now it stopped and we cannot see it running anymore.
We haven't change anything so not sure what happened.
After restarting the project the Flow started running as intended again.

This seems to be a an issue with long running Scheduled Flows.
More specifically, it looks like `node-schedule`  may stop working when running for long time:
https://github.com/node-schedule/node-schedule/issues/494
https://github.com/node-schedule/node-schedule/issues/614

I have tried to create a Flow running every second (`* * * * *`) for about 40minutes and it ran as expected.
This seems to be tied for how long it is running. Maybe a tiny shift that is only noticeable after some days running.
Some people mentioned about 25 days:
https://github.com/node-schedule/node-schedule/issues/516

Also the project `node-schedule` seems to be abandoned, so maybe we could use `node-cron` 🤔

### To Reproduce

- Create a Schedule Flow to run daily
- Wait around 25 days
- Verify Flow does not run anymore

### Directus Version

v11.11.0

### Hosting Strategy

Self-Hosted (Custom)

### Database

Postgres
````

## Идея 4. Подписка на коллекцию (в том числе системную) после подтверждения получает события создания, изменения и удаления, сделанных через API любым способом; базовая доставка, а не права (WS-SUBSCRIPTION-AUTHZ) и не переподключение (WS-RECONNECT-RESUME)

### directus/directus#25457 — Can't subscribe to directus_comments through websockets

Ссылка: https://github.com/directus/directus/issues/25457

- **Паттерн:** Подписка WebSocket на коллекцию получает события создания, изменения и удаления
- **Условие:** Подписка на коллекцию, в том числе системную (комментарии)
- **Действие:** Подписаться на коллекцию, затем создать, изменить и удалить в ней запись через API
- **Ожидание:** После init приходят события create, update, delete
- **Источник ожидания:** Документация realtime-подписок
- **Почему не подошла ближайшая запись:** WS-* записи проверяют аутентификацию, лимиты и авторизацию, а не доставку событий изменений по подписке

Первоисточник:

````text
### Describe the Bug

Although you get an init event from the subscription to directus_comments, following create, update and delete events are not emitted via the websocket.

### To Reproduce

Create a simple subscription through the SDK like in the example: 
` const subscribe = async () => {
      const { subscription } = await client.subscribe("directus_comments", {
        query: { fields: ["*"]
         },
      });
    };`
The websocket responds with the init event:
`{"type":"subscription","event":"init","data":['...'],"uid":"1"}`
But no subsequent events are sent.

### Directus Version

v11.5.1

### Hosting Strategy

Self-Hosted (Docker Image)

### Database

_No response_
````

## Идея 5. Метаданные, переданные полями multipart вместе с файлом (имя для скачивания, заголовок, описание, папка), сохраняются и возвращаются при чтении записи файла — и при порядке полей до и после файла

### directus/directus#25055 — Respect the `filename_download` When Uploading Files Over API

Ссылка: https://github.com/directus/directus/issues/25055

- **Паттерн:** Метаданные, переданные полями multipart вместе с файлом, сохраняются
- **Условие:** Загрузка файла multipart/form-data с полями метаданных (имя для скачивания, заголовок, описание)
- **Действие:** Загрузить файл с полем filename_download и другими метаданными, затем прочитать запись файла
- **Ожидание:** Сохранены все переданные метаданные, включая заданное имя для скачивания
- **Источник ожидания:** Документация загрузки файлов, здравый смысл
- **Почему не подошла ближайшая запись:** FILE-FILENAME-SANITIZATION проверяет санитизацию имени, а не сохранение явно заданных метаданных; RES-CREATE-RESPONSE-MATCHES-READ — не про multipart

Первоисточник:

````text
### Describe the Bug

[image]

### To Reproduce

```
curl --location 'https://directus-staging.bwm.ch/files' \
--header 'Authorization: Bearer 7NwPxm7Gc6EJnn6sFNrOlG8nNfmEORlM' \
--form 'title="New PDF"' \
--form 'description="Test description"' \
--form 'filename_download="test.pdf"' \
--form 'file=@"postman-cloud:///XXXX"'
```

### Directus Version

v11.6.1

### Hosting Strategy

Self-Hosted (Docker Image)

### Database

_No response_
````

## Идея 6. Чтение связи многие-ко-многим возвращает все записи связующей таблицы, в том числе со ссылкой null или на удалённый объект (связанный объект — null), а не теряет их молча

### directus/directus#24145 — API Inconsistency with Many-to-Many Relations

Ссылка: https://github.com/directus/directus/issues/24145

- **Паттерн:** Связь многие-ко-многим возвращает все записи связующей таблицы, включая записи с пустой ссылкой
- **Условие:** M2M-связь; в связующей таблице есть запись без связанного объекта (ссылка null или объект удалён)
- **Действие:** Прочитать родительскую запись с полем связи и её вложенными полями
- **Ожидание:** Все записи связующей таблицы возвращены, связанный объект — null
- **Источник ожидания:** здравый смысл
- **Почему не подошла ближайшая запись:** RES-REFERENTIAL-INTEGRITY — про отклонение ссылки на несуществующее; здесь чтение теряет существующие записи связи

Первоисточник:

````text
### Describe the Bug

In a collection "books" with a many-to-many field nammed "shared_with" to directus_users (via the junction collection books_directus_users), the following issues occur:
1.	Creating a new book and adding a shared_with with empty user data creates an empty user record in directus_users. This behavior might need an option to prevent it.
2.	If i create a books_directus_users without directus_users or if the user is deleted, the books_directus_users entry remains in the database (expected) but is not returned by the /items/books API, even though it is visible in the books admin panel (only in the edition form not in the books list).

This issue impacts use cases where shared_with can reference both registered users (directus_users) and unregistered users (using optional additional fields like first_name, last_name, email). The API does not return the full shared_with entries in such cases, making it difficult to link a sharing with no attached user to a book.

My real use case is: 
people on my app can create wishlists that they can share to their family. family members may or may not have an account so my wishlists_sharings collection contains a relational field to the wishlist, a relational field to directus_users but also some other fields (first_name,...,custom_access_token) to allow these non registered users to access the wishlist .

### To Reproduce

1.	Create a books collection with a many-to-many relationship to directus_users (via books_directus_users) nammed shared_with.
2.	Add a new book and create a shared_with entry with empty user data.
3.	Delete the empty user record from directus_users.
4.	Fetch the book via the /items/books API. The books_directus_users entry remains in the database but is not included in the API response.

it worked before 11.3

### Directus Version

v11.3.2

### Hosting Strategy

Self-Hosted (Custom)

### Database

PostgreSQL
````

## Идея 7. Несколько связей ресурса через одну общую связующую таблицу (политика ↔ пользователи и политика ↔ роли) возвращают каждая только свои данные — значения связей не смешиваются и не подменяются

### directus/directus#23785 — REST API GET /policies returns duplicate content

Ссылка: https://github.com/directus/directus/issues/23785

- **Паттерн:** Разные связи ресурса с одной связующей таблицей возвращают разные данные
- **Условие:** У ресурса две связи (пользователи и роли) через общую связующую таблицу
- **Действие:** Связать политику с ролью и отдельно с пользователем, прочитать список политик с обеими связями
- **Ожидание:** users содержит только связи с пользователями, roles — только с ролями
- **Источник ожидания:** здравый смысл
- **Почему не подошла ближайшая запись:** CONTRACT-FIELD-SELECTION — про набор возвращаемых полей; здесь значения двух связей подменены

Первоисточник:

````text
### Describe the Bug

REST API `GET /policies` returns a list of policies.

Each policy contains 2 properties: `users` and `roles`.

Problems are:

1. The value of these fields are always the same.
2. When creating a new policy (through JS SDK), having two distinct values leads to inconsistent behavior

### To Reproduce

# Steps

1. Start a fresh instance
2. Check `GET /policies` output
3. Go to [`public` policy page](http://localhost:8055/admin/settings/policies/abf8a154-5b1c-4a46-ac9c-7300570f4f17), add default admin user in user list and save changes
4. Check `GET /policies` output again 

# Expected output

1. N/A
2. public policy should be associated with public role only. By default, no user is associated with public policy
3. saves OK
4. public policy should now be associated with:
    - public role (key `roles` in JSON output) -> value **should NOT** be changed from step 2. above
    - administrator user (key `users` in JSON output) -> this value should be changed

# Got output

1. N/A

## Studio

[image]

Note: public role is not listed, this is known bug https://github.com/directus/directus/issues/23257

2. :x: public policy has both keys `roles` and `users` set. Both properties have the exact same value

## api

[image]

Note: I used `/policies?fields=*,roles.*,users.*&filter[id][_eq]=abf8a154-5b1c-4a46-ac9c-7300570f4f17` request URL for better output, but same behavior occurs without query params `/policies`.

## json

```json
{
  "data": [
    {
      "id": "abf8a154-5b1c-4a46-ac9c-7300570f4f17",
      "name": "$t:public_label",
      "icon": "public",
      "description": "$t:public_description",
      "ip_access": null,
      "enforce_tfa": false,
      "admin_access": false,
      "app_access": false,
      "permissions": [],
      "users": [
        // ❌❌❌ users key should be empty
        {
          "id": "cacabcb6-2fa2-4121-925c-d100068c4dec",
          "role": null,
          "user": null,
          "policy": "abf8a154-5b1c-4a46-ac9c-7300570f4f17",
          "sort": 1
        }
        // ❌❌❌
      ],
      "roles": [
        {
          "id": "cacabcb6-2fa2-4121-925c-d100068c4dec",
          "role": null,
          "user": null,
          "policy": "abf8a154-5b1c-4a46-ac9c-7300570f4f17",
          "sort": 1
        }
      ]
    }
  ]
}
```

3. ✅ saves OK

## Studio

[image]

4. :x: both both keys `roles` and `users` are modified

[image]

## js …[обрезано]
````

## Идея 8. Вход через внешний IdP с профилем без необязательных атрибутов (email, имя) создаёт пользователя и пускает либо даёт понятную ошибку с причиной, а не 5xx; позитивная пара к AUTH-EXTERNAL-IDP-UNVERIFIED-EMAIL

### directus/directus#24099 — SSO "Log In with GitHub" fails if GitHub user doesn't have email in profile

Ссылка: https://github.com/directus/directus/issues/24099

- **Паттерн:** Вход через внешний IdP без email в профиле создаёт пользователя или даёт понятную ошибку
- **Условие:** Внешний провайдер возвращает профиль без email; email у пользователя необязателен
- **Действие:** Выполнить вход через внешний IdP учёткой без email
- **Ожидание:** Пользователь создан и вошёл, либо ответ с понятной причиной
- **Источник ожидания:** здравый смысл
- **Почему не подошла ближайшая запись:** AUTH-EXTERNAL-IDP-UNVERIFIED-EMAIL — негативная проверка связывания по email; здесь законный вход отклоняется

Первоисточник:

````text
### Describe the Bug

Since the deploy of v11, our users without email in the GitHub profile can't sign up. Error looks like these for them:

[image]



Looks like the reason is the `email` field, in the `user` object. It has `undefined` value and makes the validation fail:
https://github.com/directus/directus/blob/2991169f82ad5d0c461e82e7fdcb268ef737896c/api/src/services/users.ts#L164-L165

[image]

Also nothing related is logged even with TRACE level, only:
```
[17:23:10] GET /admin/login?reason=FAILED_VALIDATION 304 1ms
```

> 

### To Reproduce

- Set up github SSO in Directus v11.
- Sign up with user without email (e.g. https://github.com/test-user-bdf-2)

### Directus Version

v11.2.2

### Hosting Strategy

Self-Hosted (Docker Image)

### Database

_No response_
````

## Идея 9. Операции с файлами (загрузка, отдача, трансформации и пресеты, Range, удаление) работают одинаково на каждом поддерживаемом хранилище (локальный диск, S3, GCS, Azure и т. п.); нужны стенды с несколькими драйверами хранилища

### directus/directus#23955 — Api / Assets / Cloudinary: Images cannot be returned if "key" parameter is set

Ссылка: https://github.com/directus/directus/issues/23955

- **Паттерн:** Файл с предустановленной трансформацией отдаётся на каждом поддерживаемом хранилище
- **Условие:** Используется конкретный драйвер облачного хранилища; к файлу применяется пресет трансформации (key)
- **Действие:** Загрузить изображение и запросить его без параметров и с key пресета
- **Ожидание:** Обе формы отдают изображение
- **Источник ожидания:** здравый смысл
- **Почему не подошла ближайшая запись:** FILE-TRANSFORM-LIMITS — про лимиты трансформации; здесь законная трансформация не отдаёт файл на конкретном хранилище

Первоисточник:

````text
### Describe the Bug

After uploading an asset the image is not rendered on File Library.
I have found out that this only happens when parameter `key` is set.
In File Library, the "key"s used are: "system-medium-cover" and "system-large-contain" so that's why the images are not shown.
The error in the server logs is `No stream returned for file "364dd67d-a1a0-46e1-ab72-6b00294ff4c2.jpeg"`

### To Reproduce

Use Cloudinary for storage, upload an image and see that previews are not shown in File Library

### Directus Version

v11.1.2

### Hosting Strategy

Self-Hosted (Custom)

### Database

PostgreSQL
````

## Идея 10. Несколько WebSocket-эндпоинтов на разных путях (realtime, GraphQL subscriptions, служебные) работают независимо — включение одного не ломает рукопожатие, аутентификацию и сообщения другого

### directus/directus#23625 — Streaming logs is breaking the regular REST websocket

Ссылка: https://github.com/directus/directus/issues/23625

- **Паттерн:** Несколько WebSocket-эндпоинтов на разных путях работают независимо
- **Условие:** На сервере включены два WebSocket-эндпоинта на разных путях
- **Действие:** Подключиться к основному пути и пройти аутентификацию
- **Ожидание:** Приходит подтверждение аутентификации
- **Источник ожидания:** RFC 6455, здравый смысл
- **Почему не подошла ближайшая запись:** WS-HANDSHAKE-AUTH — про требование аутентификации; здесь корректная аутентификация ломается соседним эндпоинтом

Первоисточник:

````text
### Describe the Bug

The introduction of the logs streaming endpoint (on path `/websocket/logs`) is interfering with the pre-existing REST websocket endpoint (on path `/websocket`). When connecting to the old websocket no authentication confirmation is ever received!

Current workarounds:
- Disable streaming logs (`WEBSOCKETS_LOGS_ENABLED=false`)
- ~Change the REST websocket path (`WEBSOCKETS_REST_PATH="/different"`)~

Example code:
```js
const socket = new WebSocket("ws://localhost:8055/websocket");
console.log("Socket initialized");

socket.addEventListener("open", () => {
  console.log("Socket open");

  socket.send(
    JSON.stringify({
      type: "auth",
      access_token: "<credentials>",
    })
  );
});

socket.addEventListener("message", (msg) => console.log("message received", msg.data));
socket.addEventListener("close", () => console.log("socket closed"));
socket.addEventListener("error", () => console.log("socket error!"));
```

Expected result (version 11.0.2):
[image]

Current result (version 11.1.0):
[image]

### To Reproduce

- Ensure that both websockets REST and logs streaming are enabled (they are by default)
- use the above script (or any other method) to connect to the rest websocket
- no authentication confirmation will ever be received

### Directus Version

v11.1.0

### Hosting Strategy

Self-Hosted (Docker Image)

### Database

Postgress
````

## Индекс библиотеки

Все записи (463): ID | категория | заголовок.

```text
ASYNC-DEAD-LETTER | async | Необрабатываемые сообщения уходят в DLQ без блокировки очереди
ASYNC-EVENT-ORDERING | async | Нарушение порядка событий не портит состояние
ASYNC-EVENT-PATH-SAME-RULES | async | Событийный путь применяет те же фильтры и границы доступа, что и плановый
ASYNC-IDEMPOTENT-CONSUMER | async | Повторная доставка события обрабатывается однократно
ASYNC-JOB-CANCEL | async | Отмена фоновой задачи останавливает её и не оставляет частичных эффектов
ASYNC-JOB-LIFECYCLE | async | Фоновая задача проходит статусы и отдаёт результат
ASYNC-MESSAGE-VALIDATION | async | Входящие сообщения брокера валидируются по схеме так же, как HTTP-запросы
ASYNC-RPC-ERROR-PROPAGATION | async | Ошибка обработчика в схеме запрос-ответ через брокер возвращается вызывающему
ASYNC-SSE-STREAM | async | Потоковый ответ SSE работает для всех методов и отдаёт text/event-stream
ASYNC-WEBHOOK-RETRY | async | Неуспешная доставка вебхука повторяется с backoff и ограничением
ASYNC-WEBHOOK-SIGNATURE | async | Вебхуки подписаны, подпись проверяется, повтор отклоняется
ASYNC-WEBHOOK-URL-SSRF | async | URL вебхука не может указывать на внутренние адреса
AUTH-ACCOUNT-STATE-ALL-SCHEMES | security | Отключённая, заблокированная или истёкшая учётка не аутентифицируется ни одной схемой
AUTH-API-KEY-LIFECYCLE | security | API-ключи ограничены по правам, отзываются и не раскрываются
AUTH-BRUTE-FORCE-PROTECTION | security | Перебор паролей ограничивается
AUTH-CLIENT-ASSERTION-BINDING | security | Client assertion принимается только с ключом клиента, указанного в ней
AUTH-CLIENT-CERT-IDENTITY | security | Личность из сертификата клиента извлекается однозначно
AUTH-CONCURRENT-SESSIONS | security | Лимит одновременных сессий и устройств соблюдается
AUTH-COOKIE-ATTRIBUTES | security | Сессионные cookie имеют Secure, HttpOnly, SameSite и узкие Domain/Path
AUTH-CSRF | security | Изменяющие операции с cookie-аутентификацией защищены от CSRF
AUTH-EXTERNAL-IDP-UNVERIFIED-EMAIL | security | Вход через внешний IdP не связывается с учёткой по неподтверждённому email
AUTH-GENERATED-SECRET-STRENGTH | security | Сгенерированные сервером секреты имеют стойкость не ниже требуемой алгоритмом
AUTH-IDENTITY-ATTRIBUTES-ALL-SCHEMES | security | Атрибуты идентичности, которые даёт источник, сохраняются при любом способе аутентификации
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
FILE-RANGE-REQUESTS | files | Частичное скачивание через Range работает по контракту
FILE-TRANSFORM-LIMITS | files | Лимит трансформации файла пропускает допустимые комбинации и отклоняет превышение
FILE-UPLOAD-KEY-COLLISION | files | Загрузка не перезаписывает чужой файл с тем же именем или ключом хранилища
FILE-UPLOAD-SIZE-LIMIT | files | Лимит размера загружаемого файла соблюдается
FILE-UPLOAD-TYPE-VALIDATION | files | Тип файла проверяется по содержимому, а не только по расширению
GQL-ALIAS-BATCH-ABUSE | graphql | Алиасы и batch-запросы не обходят rate limit
GQL-COMPLEXITY-LIMIT | graphql | Стоимость запроса ограничена (поля, списки, first/last)
GQL-CSRF-GET-MUTATION | graphql | Мутации не выполняются через GET и простые Content-Type
GQL-DEPTH-LIMIT | graphql | Глубина запроса ограничена
GQL-EQUIVALENT-SELECTION-FORMS | graphql | Эквивалентные формы выбора полей GraphQL дают одинаковые данные
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
HARD-BUSINESS-FLOW-AUTOMATION | security | Чувствительные бизнес-потоки защищены от автоматизированного злоупотребления
HARD-CACHE-POISONING | security | Неключевые заголовки не отравляют общий кэш
HARD-CLIENT-IP-TRUSTED-PROXIES | security | IP клиента определяется по цепочке доверенных прокси одинаково на всех маршрутах
HARD-DEBUG-ENDPOINTS | security | Отладочные и служебные эндпоинты недоступны извне
HARD-EXCESSIVE-DATA-EXPOSURE | security | Ответы не содержат внутренних полей сверх контракта
HARD-EXPENSIVE-OPERATION-LIMITS | security | Дорогие операции ограничены по ресурсам
HARD-HOST-HEADER | security | Подмена Host и X-Forwarded-Host не влияет на ссылки и маршрутизацию
HARD-ID-PREDICTABILITY | security | Предсказуемые идентификаторы не позволяют собрать данные перебором
HARD-IP-ALLOWLIST | security | Ограничение доступа по адресам и подсетям работает на границах для IPv4 и IPv6
HARD-METHOD-OVERRIDE | security | Заголовки переопределения метода не обходят авторизацию
HARD-SENSITIVE-DATA-IN-URL | security | Персональные данные и секреты не передаются в URL
HARD-SHADOW-API-VERSIONS | security | Старые версии API и недокументированные маршруты не обходят защиту
HARD-SLOW-CLIENT-LIMITS | security | Медленные и неполные запросы и непрочитанные ответы не накапливаются без ограничения
HARD-TLS-ONLY | security | API доступен только по TLS с актуальными настройками
HARD-UNSAFE-API-CONSUMPTION | security | Ответы сторонних API валидируются перед использованием
HARD-VERSION-DISCLOSURE | security | Ответы не раскрывают версии ПО и инфраструктуры
HTTP-ABSOLUTE-URL-BASE-PATH | http-semantics | Абсолютные URL, которые формирует сервер, учитывают публичный адрес и базовый путь
HTTP-ACCEPT-LANGUAGE | http-semantics | Язык сообщений определяется Accept-Language с fallback
HTTP-BODY-ON-GET-DELETE | http-semantics | Тело в GET/DELETE игнорируется или отклоняется по контракту
HTTP-BODY-WITHOUT-CONTENT-TYPE | http-semantics | Тело без Content-Type обрабатывается предсказуемо
HTTP-COMPRESSION | http-semantics | Сжатие ответа согласуется через Accept-Encoding
HTTP-HEADER-REPEATED-LINES-ACCEPTED | http-semantics | Сотни повторяющихся строк одного заголовка в пределах лимита размера принимаются одинаково по HTTP/1.1 и HTTP/2
HTTP-HEADER-SIZE-LIMIT | http-semantics | Слишком большие заголовки отклоняются контролируемо
HTTP-HTTP2-RESOURCE-LIMITS | http-semantics | Параметры HTTP/2 со стороны клиента не заставляют сервер буферизовать и работать без предела
HTTP-OPTIONS-ALLOW | http-semantics | OPTIONS возвращает согласованный список методов
HTTP-PATH-PREFIX-SEGMENT-BOUNDARY | http-semantics | Правило по префиксу пути соблюдает границу сегмента
HTTP-REQUEST-SMUGGLING | http-semantics | Противоречивые Content-Length и Transfer-Encoding не приводят к request smuggling
HTTP-TRAILING-SLASH-CASE | http-semantics | Вариации пути (слэш в конце, регистр, двойной слэш) обрабатываются единообразно
HTTP-UNKNOWN-ROUTE | http-semantics | Неизвестный маршрут возвращает 404, а не 5xx или 200
HTTP-URL-LENGTH-LIMIT | http-semantics | Очень длинный URL отклоняется контролируемо
HTTP-VARY-HEADER | http-semantics | Кэшируемые ответы содержат корректный Vary
HTTP-VERSION-PARITY | http-semantics | Запросы по HTTP/2 и с предложением Upgrade h2c обслуживаются так же, как по HTTP/1.1
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
INJ-SQL | security | SQL-инъекция во входных параметрах не исполняется
INJ-SSRF-PARAMETERS | security | Параметры с URL и хостами не дают доступа к внутренней сети
INJ-STORED-XSS | security | Сохранённые данные с HTML/JS не создают XSS у потребителей API
INJ-TEMPLATE-SSTI | security | Инъекция в серверные шаблоны не исполняется
INJ-UNSAFE-DESERIALIZATION | security | Небезопасная десериализация пользовательских данных невозможна
INJ-USER-CODE-EXECUTION | security | Пользовательский код, исполняемый сервером, не получает доступа к ОС, файлам и сети
INJ-XXE | security | Внешние сущности XML не обрабатываются
OBS-AUDIT-TRAIL | observability | Чувствительные действия фиксируются в журнале аудита
OBS-CONFIG-ENDPOINT-ACCURATE | observability | Служебный эндпоинт конфигурации показывает фактические значения
OBS-HEALTH-ENDPOINTS | observability | Health-эндпоинты отражают состояние и не раскрывают детали
OBS-NO-SECRETS-IN-LOGS | observability | Логи не содержат паролей, токенов и ПДн в открытом виде
OBS-TELEMETRY-FORMAT | observability | Экспортируемая телеметрия соответствует документированной структуре и соглашениям OpenTelemetry
OBS-TRACE-PROPAGATION | observability | Контекст трассировки принимается и передаётся дальше
PAGE-BEYOND-LAST | pagination | Запрос страницы за последней возвращает пустой результат без ошибки
PAGE-CONCURRENT-MODIFICATION | pagination | Изменения коллекции во время обхода не приводят к дублям и пропускам сверх контракта
PAGE-CURSOR-TAMPERING | pagination | Подделанный или чужой курсор пагинации не раскрывает данные
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
RES-RELATION-ORDER-STABLE | resources | Изменение связанного ресурса не меняет ручной порядок связей у другой стороны
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
SEC-AUTHZ-ERROR-LEAK | security | Authorization failures do not disclose protected data
SEC-AUTHZ-FUNCTION | security | User without required permission cannot invoke operation
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
WS-ORIGIN-CHECK | websocket | Проверка Origin защищает от cross-site WebSocket hijacking
WS-RECONNECT-RESUME | websocket | Переподключение восстанавливает подписки без потери и дублей сверх контракта
WS-SLOW-CONSUMER-NO-SILENT-LOSS | websocket | Медленный клиент подписки не теряет сообщения молча
WS-SUBSCRIPTION-AUTHZ | websocket | Подписки и сообщения авторизуются по каждому каналу
WS-TOKEN-EXPIRY | websocket | Истечение или отзыв токена учитывается в открытом соединении
```
