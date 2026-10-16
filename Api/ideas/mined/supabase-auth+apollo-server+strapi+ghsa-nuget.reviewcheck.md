# Перекрёстное ревью новых идей выгрузки багов

Партии `supabase-auth`, `apollo-server`, `strapi`, `ghsa-nuget`, идей: 13; вариант пакета — с предложениями модели Claude Opus 5.5 (`claude-opus-5-5`) — то же, что видит человек на ревью.
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

## Идея 1 (`supabase-auth`). Запрос авторизации, который сервис отправляет внешнему OAuth/OIDC-провайдеру, содержит в scope запрошенные клиентом значения и не добавляет устаревших или конфликтующих scope по умолчанию

- **Предложение Claude:** `accept` — `AUTH-OAUTH-OUTBOUND-SCOPE` в `checks/security/authentication-session.yaml`

### supabase/auth#1827 — Auth provider Figma uses deprecated scope

Ссылка: https://github.com/supabase/auth/issues/1827

- **Паттерн:** Запрос авторизации к внешнему провайдеру не содержит устаревших scope по умолчанию и не конфликтует с запрошенными
- **Условие:** Вход через встроенного внешнего OAuth-провайдера, клиент передаёт актуальный scope провайдера
- **Действие:** Вызвать начало входа через провайдера с параметром scopes; разобрать URL перенаправления к провайдеру (параметр scope)
- **Ожидание:** scope содержит только актуальные значения провайдера, запрошенные клиентом не конфликтуют с умолчанием
- **Источник ожидания:** Документация внешнего провайдера (актуальные scope), RFC 6749 §3.3
- **Почему не подошла ближайшая запись:** Ближайшая AUTH-OAUTH-REDIRECT-STATE проверяет redirect_uri, state и PKCE, а не состав scope в исходящем запросе к провайдеру

Первоисточник:

````text
# Bug report

- [x] I confirm this is a bug with Supabase, not with my own application. 
- [x] I confirm I have searched the [Docs](https://docs.supabase.com), GitHub [Discussions](https://github.com/supabase/supabase/discussions), and [Discord](https://discord.supabase.com). 

## Describe the bug

Figma API [deprecated](https://www.figma.com/developers/api#authentication-scopes) the scope `file_read` and replaced it with more granual controls over the permissions requested from user. The auth code still uses the outdated scope that requests all the available permissions during sign in:

https://github.com/supabase/auth/blob/a7129df4e1d91a042b56ff1f041b9c6598825475/internal/api/provider/figma.go#L40-L43



## To Reproduce
Setting up sign in with Figma and one of the currently supported scopes results in broken authentication showing `Cannot pass in both the file_read and files:read scopes` during redirect.

```js
const { error } = await supabase.auth.signInWithOAuth({
    provider: 'figma',
    options: {
      redirectTo: authRedirect,
      scopes: 'files:read',
    },
  });
```

## Expected behavior

Figma API doesn't seem to provide a more minimalistic scope than `files:read` so I guess that should be the new default.
````

## Идея 2 (`supabase-auth`). Пользователь, импортированный с готовым хешем пароля поддерживаемого алгоритма (bcrypt, scrypt, argon2, PBKDF2 из другой системы), входит по исходному паролю; неверный пароль отклоняется; формат хеша определяется по префиксу или параметрам

- **Предложение Claude:** `accept` — `AUTH-IMPORTED-PASSWORD-HASH` в `checks/security/authentication-session.yaml`

### supabase/auth#1750 — In Firebase, the password hash is stored in passwordHash and is hashed using SCRYPT with specific parameters. In Supabase, the password is stored in encrypted_password and is hashed using bcrypt. As a result, when migrating authenticated users, an error occurs due to the different password hashing algorithms.

Ссылка: https://github.com/supabase/auth/issues/1750

- **Паттерн:** Пользователь, импортированный с хешем пароля поддерживаемого алгоритма, входит по исходному паролю
- **Условие:** Учётка создана импортом с хешем пароля другой системы (scrypt Firebase) вместо bcrypt
- **Действие:** Создать пользователя через админ-API с готовым хешем поддерживаемого формата; войти по исходному паролю и по неверному
- **Ожидание:** Верный пароль даёт токен, неверный — invalid_grant; формат хеша определяется по префиксу
- **Источник ожидания:** Документация продукта (поддерживаемые форматы хешей при миграции), здравый смысл
- **Почему не подошла ближайшая запись:** AUTH-PASSWORD-POLICY и др. про политику пароля, записи про вход с импортированным хешем нет

Первоисточник:

````text
# Bug report

The difference between the newly created Supabase user and the migrated Firebase user is primarily in the password handling. Here’s a breakdown of the issues and potential reasons for the "invalid_grant" error:

Password Storage and Hashing Differences
Supabase User (newsupabase1@yopmail.com):

The password is stored in encrypted_password and is hashed using bcrypt ($2a$10$d31Fd//DLU.28P2H3.ywpOqkfrBODA74IlmuNtU3LbJPm/1hhYGhy).
This indicates that the password is correctly hashed and stored by Supabase's default bcrypt implementation.

Migrated Firebase User (newusersexperienced@yopmail.com):

The password hash is stored in passwordHash and uses SCRYPT with specific parameters.
This user’s encrypted_password is empty, and the passwordHash field contains the SCRYPT-based hash.
hash_parameters include details like rounds, mem_cost, algorithm, and base64 encoding, which indicates SCRYPT was used for hashing.


Due to this issue, we are unable to authenticate Firebase users in Supabase. As discussed, you mentioned that this is a bug and that you will soon update the password hashing in Supabase.
````

## Идея 3 (`supabase-auth`). Смена телефона или email на ранее использованный этим же пользователем (A → B → A) проходит обычным подтверждением кодом — код отправляется, принимается, значение обновляется

- **Предложение Claude:** `accept` — `AUTH-CONTACT-CHANGE-PREVIOUS-VALUE` в `checks/security/authentication-session.yaml`

### supabase/auth#1629 — Auth fails to update user phone number under common conditions

Ссылка: https://github.com/supabase/auth/issues/1629

- **Паттерн:** Смена телефона на ранее использованный номер проходит с подтверждением кодом
- **Условие:** Пользователь меняет номер A→B, затем B→A, или B уже использовался ранее
- **Действие:** Сменить телефон на B, подтвердить; сменить обратно на A; запросить и ввести код
- **Ожидание:** Код отправляется и проходит проверку, номер обновляется
- **Источник ожидания:** Здравый смысл
- **Почему не подошла ближайшая запись:** Механизм не описан; AUTH-OTP-BINDING про привязку кода к получателю (негативное направление), а не про успешную смену на прежний номер

Первоисточник:

````text
# Bug report
- [X] I confirm this is a bug with Supabase, not with my own application. 
- [X] I confirm I have searched the [Docs](https://docs.supabase.com), GitHub [Discussions](https://github.com/supabase/supabase/discussions), and [Discord](https://discord.supabase.com). 

## Describe the bug
User phone is not updated correctly under some common conditions.

To reproduce bug, just update use phone number. We are using flutter plugin, but issue will occur with every plugin.
```
await Supabase.instance.client.auth.updateUser(UserAttributes(phone: phone));
final response = await auth.updateUser(UserAttributes(phone: phone));
```

As consequence of above code, Supabase sends an OTP code to verify the user request.
However, below issue occurs:
- If user changes his number from numberA to numberB, and numberB was used recently or already used in the past, the OTP code is either not sent or it is sent but the verify will always fail.

## To Reproduce
1) Test with one user and two fixed phone numbers (numberA and numberB). 
2) Change user's phone number from numberA to numberB and soon after change back user phone number from numberB to numberA. OTP code won't be sent or verification will always fail.
3) If numberB was already used in the past, OTP is not sent or verification fails. Sometimes this error can also be seen on console:
```
updating 65819238034: AuthRetryableFetchError
```

## Expected behavior
1) User should be able to change his/her phone number smoothly as long as the new phone number is not already assigned to another user inside project's Auth table.
2) User should be able to change phone number from numberA to numberB and back from numberB to numberA. It can happen that user changes his mind soon after making his action and he must be able to reverse his action.

## System information

```
├── supabase_flutter 2.5.6
│   ├── supabase 2.2.2
│   │   ├── functions_client 2.2.0
│   │   ├── gotrue 2.8.1
│   │   ├── postgrest 2.1.2
│   │   ├── realtime_client 2.1.0
│   │   ├── storage_client 2.0.2
```

CC: @dshukertjr
````

## Идея 4 (`supabase-auth`). Вход через внешний OIDC-провайдер с ID-токеном на зарегистрированном алгоритме ES256K

- **Предложение Claude:** не новая запись, а шаг-вариант к `AUTH-JWT-VALID-ACCEPTED`: Подключить внешнего OIDC-провайдера с ключами JWKS на зарегистрированном алгоритме (ES256K, kty=EC, crv=secp256k1) и пройти вход до callback — ID-токен принимается, а неподдерживаемый ключ даёт контролируемую ошибку, не 500

### supabase/auth#2534 — Support for Telegram OIDC: Unsupported elliptic curve secp256k1 in JWKS

Ссылка: https://github.com/supabase/auth/issues/2534

- **Действие:** Настроить провайдера OIDC с такими ключами; пройти вход и callback
- **Ожидание:** ID-токен проверяется и вход завершается; неподдерживаемый ключ даёт контролируемую ошибку, а не 500

Первоисточник:

````text
### Describe the bug
When attempting to use the new Telegram OIDC / Custom OAuth provider, the authentication flow fails during the token exchange or profile retrieval phase. The error returned by Supabase Auth is: `Error getting user profile from external provider`.

After investigation, it appears that Telegram's OIDC implementation uses the **`secp256k1`** elliptic curve for its signing keys (JWKS), which seems to be unsupported by the underlying Go libraries used in the Auth server (likely `go-jose`).

### To Reproduce
1. Set up a Custom OAuth provider in Supabase Dashboard using Telegram's OIDC endpoints:
   - URL: `https://oauth.telegram.org/auth`
   - Token URL: `https://oauth.telegram.org/token`
2. Trigger the login flow from the client.
3. Complete the Telegram authorization.
4. On the redirect to `/auth/callback`, the process fails with an `unexpected_failure` or `server_error`.

### Expected behavior
Supabase Auth should be able to parse and validate the ID Token signed with the `secp256k1` curve provided in Telegram's JWKS (`https://oauth.telegram.org/jwks`).

### Technical Context
Telegram's JWKS (`https://oauth.telegram.org/jwks`) contains keys with the following parameters:
- `kty`: `EC`
- `crv`: `secp256k1`

The error logs indicate that the curve is not recognized or supported, preventing the validation of the identity token.

### Additional context
Telegram recently introduced this OIDC flow for bots. Many developers are moving towards this standard, but it seems that the `secp256k1` curve (commonly used in blockchain but less common in standard OIDC) is creating a bottleneck for Supabase users.
````

## Идея 5 (`supabase-auth`). Вход через каждого встроенного OIDC-провайдера проходит проверку issuer

- **Предложение Claude:** не новая запись, а шаг-вариант к `AUTH-JWT-VALID-ACCEPTED`: Пройти вход через каждого встроенного OIDC-провайдера с актуальным значением iss его ID-токена — законный токен принимается

### supabase/auth#1533 — Error when using oauth with provider linkedin_oidc - Error getting user profile from external provider

Ссылка: https://github.com/supabase/auth/issues/1533

- **Действие:** Пройти вход через провайдера до callback
- **Ожидание:** Законный токен провайдера принимается, вход завершается

Первоисточник:

````text
### Version
@nuxtjs/supabase: tried both v1.2.0 and v0.3.8
nuxt: v3.6.5

When using signInWithOAuth with linkedin_oidc

```
const client = useSupabaseClient()
const result = await client.auth.signInWithOAuth({
    provider: 'linkedin_oidc',
    options: {
        redirectTo: '...'
    }
})
```

It redirects back to the redirectTo URL with the following query params:
`error=server_error&error_code=500&error_description=Error+getting+user+profile+from+external+provider#error=server_error&error_code=500&error_description=Error+getting+user+profile+from+external+provider`

When checking the Auth logs in the Supabase platform I found this error:
`error: oidc: id token issued by a different provider, expected \"https://www.linkedin.com\" got \"https://www.linkedin.com/oauth\"","level":"error","method":"GET","msg":"500: Error getting user profile from external provider`
````

## Идея 6 (`supabase-auth`). Выход с токеном удалённого пользователя завершается успешно

- **Предложение Claude:** не новая запись, а шаг-вариант к `AUTH-LOGOUT-INVALIDATES`: Удалить пользователя администратором и выполнить выход с его ещё не истёкшим токеном — выход завершается успешно или не мешает клиенту завершить сеанс, сессии пользователя недействительны

### supabase/auth#1550 — Cant log out deleted user with supabase.auth.signOut()

Ссылка: https://github.com/supabase/auth/issues/1550

- **Действие:** Удалить пользователя через админ-API; отправить запрос выхода с его токеном
- **Ожидание:** Выход успешен (2xx) или возвращает ошибку, не мешающую завершить выход; сессии пользователя недействительны

Первоисточник:

````text
# Bug report

- [x ] I confirm this is a bug with Supabase, not with my own application. 
- [x ] I confirm I have searched the [Docs](https://docs.supabase.com), GitHub [Discussions](https://github.com/supabase/supabase/discussions), and [Discord](https://discord.supabase.com). 

here is a linked discussion
[delete user RPC causes subsequent signOut request to fail](https://github.com/orgs/supabase/discussions/9327)


## Describe the bug
If a user deletes their acccount using the javascript sdk, and the frontend calls supabase.auth.signOut() right after delete the account. The signOut will fail and the local cookie wont be deleted.

## To Reproduce

Steps to reproduce the behavior, please provide code snippets or a repository:
- create a cloud fn that can delete a user with a service key

```
const { data, error } = await supabase.auth.admin.deleteUser(
  'userr_id'
)
```
on the frontend now call

```
const { error } = await supabase.functions.invoke("delete-user");
const { error:} = await supabase.auth.signOut();
console.log(error);
```

this will throw the following error
```
AuthApiError: User from sub claim in JWT does not exist
    at handleError (fetch.ts:71:9)
    at async _handleRequest (fetch.ts:150:5)
    at async _request (fetch.ts:117:16)
    at async GoTrueAdminApi.signOut (GoTrueAdminApi.ts:65:7)
    at async GoTrueClient.ts:1491:27
    at async SupabaseAuthClient._useSession (GoTrueClient.ts:991:14)
    at async SupabaseAuthClient._signOut (GoTrueClient.ts:1484:12)
    at async GoTrueClient.ts:1477:14
```





## Expected behavior

user should be signed out and cookies / local session removed

## System information

- OS: [ Windows 11]
- Browser chrome/brave
- Version of supabase-js: 
    "@supabase/ssr": "^0.3.0",
    "@supabase/supabase-js": "^2.42.4",

```
        SERVICE IMAGE      │        LOCAL         │   LINKED
  ─────────────────────────┼──────────────────────┼─────────────
    supabase/postgres      │ 15.1.0.137           │ 15.1.0.137
    supabase/gotrue        │ v2.148.0             │ v2.148.0
    postgrest/postgrest    │ v11.2.2              │ v11.2.2
    supabase/realtime      │ v2.28.23             │ -
    supabase/storage-api   │ v1.0.10              │ v1.0.10
    supabase/edge-runtime  │ v1.43.2              │ -
    supabase/studio        │ 20240408-6bf3b81     │ -
    supabase/postgres-meta │ v0.80.0              │ -
    supabase/logflare      │ 1.4.0     
````

## Идея 7 (`apollo-server`). Поля extensions ошибки GraphQL (code и пользовательские) присутствуют по документированной структуре ровно в одном месте — без копий во вложенных объектах (exception, originalError)

- **Предложение Claude:** `accept` — `GQL-ERROR-EXTENSIONS-SHAPE` в `checks/graphql/graphql.yaml`

### apollographql/apollo-server#3835 — duplicate keys in error.extensions object

Ссылка: https://github.com/apollographql/apollo-server/issues/3835

- **Паттерн:** Расширения ошибки GraphQL не дублируются между extensions и вложенными объектами
- **Условие:** Ошибка с пользовательскими полями extensions (код и дополнительные свойства)
- **Действие:** Вызвать такую ошибку и сравнить ключи extensions и extensions.exception в ответе
- **Ожидание:** Каждое поле расширения присутствует в одном месте по документированной структуре, без копий во вложенном exception
- **Источник ожидания:** Спецификация GraphQL (Response, Errors: extensions); документация продукта о структуре ошибок; здравый смысл
- **Почему не подошла ближайшая запись:** GQL-ERRORS-NO-LEAK проверяет утечку внутренних деталей, REST-ERROR-SCHEMA — схему ошибок REST; записи о дублировании полей в структуре ошибки GraphQL нет

Первоисточник:

````text
## package name and version of Apollo showing the problem:
`apollo-server-errors@2.3.4`

I believe the problem lies in 1 of 2 places, or potentially both:
* The ApolloError constructor appears to copy the extensions it is passed to [`this`](https://github.com/apollographql/apollo-server/blob/master/packages/apollo-server-errors/src/index.ts#L40)
* `enrichError` [here](https://github.com/apollographql/apollo-server/blob/master/packages/apollo-server-errors/src/index.ts#L92) when it copies the extensions to a copy object (`expanded`) appears to spread `extensions` into an `expanded.extensions` object and spread it into the `expanded.extensions.exception` object, as well as any properties from `originalError`.

## description
To start, the only semi-related issue I could find was this one: https://github.com/apollographql/apollo-server/issues/2917
This issue does mention something relevant to this issue regarding the extensions passed to `ApolloError()` being replicated into the `extensions.exception` object: https://github.com/apollographql/apollo-server/issues/2917#issuecomment-516407421 which is true, albeit undersireable.

But overall, I'm part of an organization that is developing a set of error classes to standardize the errors we return to calling clients of our graphql APIs. These error classes extend from `ApolloError`. I've also been referencing the Apollo Error handling documentation, specifically the bit around customizing or creating [other errors](https://www.apollographql.com/docs/apollo-server/data/errors/#other-errors). Using the the `ApolloError` constructor has been problematic however. If you pass an object containing keys you want to appear in the `extensions` object to the `ApolloError()` constructor's third argument the keys in that object get duplicated into the `extensions` object and the `extensions.exception` object. This makes adhering to an error format difficult since keys are unecessarily duplicated. Especially when you consider Apollo Server creates `extensions.exception.stacktrace` in non-prod environments (ie. `debug: true` or `NODE_ENV !== 'production'`) and if you are in prod, and throw an `ApolloError` with the third argument populated, your error response will contain an `extensions.exception.<key you provided>` instead of not being present as one would expect

In summary `throw new ApolloError('some message', 'SOME_ERROR', { foo: 'bar'})` or if I define an error class like so: 
```javascript
class SomeCust …[обрезано]
````

## Идея 8 (`apollo-server`). Сразу после старта экземпляра (асинхронная загрузка схемы, прогрев) серия одинаковых корректных запросов обслуживается одинаково — либо все успешны, либо до готовности 503 с Retry-After и readiness «не готов»; механизм в баге не описан

- **Предложение Claude:** `accept` — `RESIL-COLD-START-REQUESTS` в `checks/common/resilience.yaml`

### apollographql/apollo-server#3416 — Graph Manager broken with apollo-server-lambda and serverless-offline

Ссылка: https://github.com/apollographql/apollo-server/issues/3416

- **Паттерн:** Повторные запросы после первого обслуживаются так же успешно, как первый
- **Условие:** Только что запущенный экземпляр сервиса (холодный старт), схема загружается асинхронно
- **Действие:** Сразу после старта отправить один и тот же корректный запрос несколько раз подряд и сравнить ответы
- **Ожидание:** Все ответы одинаково успешны
- **Источник ожидания:** Здравый смысл: результат корректного запроса не зависит от его порядкового номера
- **Почему не подошла ближайшая запись:** RESIL-GRACEFUL-SHUTDOWN и RESIL-DEPENDENCY-DOWN про перезапуск и отказ зависимостей; записи о стабильности ответов на серию одинаковых запросов после старта нет; механизм в баге не описан

Первоисточник:

````text
Package: `@apollo/gateway`
Version: tested every version since `v0.8.0` and all fail
Last known working version: `none`

Package: `apollo-server-lambda`
Version: tested every version since `v2.8.0` and all fail
Last known working version: `none`

When running `apollo-server-lambda` locally with [serverless-offline](https://github.com/dherault/serverless-offline) and using the [Graph Manager](https://www.apollographql.com/docs/graph-manager/federation/#managed-configuration), sometimes the first request to the server is successful. All subsequent requests fail with: `INTERNAL_SERVER_ERROR` `Invalid options provided to ApolloServer: Expected undefined to be a GraphQL schema.`, which will often lead to a crash.

When switching back to a locally configured `serviceList` things work fine.
Deploying the gateway to AWS Lambda also appears to work fine.

Similar issue, but not exactly the same: #3190

I'll have a repo demonstrating the reproduction soon (Bring Your Own ENGINE_API_KEY)
````

## Идея 9 (`apollo-server`). Ответ, для которого включено кэширование (подсказки max-age у всех полей, политика кэша маршрута), содержит Cache-Control по итоговой политике — max-age как минимум из подсказок, public или private; пара к REST-SENSITIVE-CACHE-CONTROL

- **Предложение Claude:** `accept` — `HTTP-CACHEABLE-RESPONSE-CACHE-CONTROL` в `checks/rest/http-protocol.yaml`

### apollographql/apollo-server#2918 — Cache Control headers not set when cacheControl extension is enabled

Ссылка: https://github.com/apollographql/apollo-server/issues/2918

- **Паттерн:** Ответ с подсказками кэширования содержит заголовок Cache-Control по итоговой политике
- **Условие:** Включено управление кэшированием, все поля запроса имеют подсказки max-age (без private)
- **Действие:** Отправить запрос к полям с подсказками кэширования и проверить заголовки ответа
- **Ожидание:** Cache-Control с max-age, равным минимальному из подсказок, и public/private по политике
- **Источник ожидания:** RFC 9111 §5.2; документация продукта о cache hints
- **Почему не подошла ближайшая запись:** REST-SENSITIVE-CACHE-CONTROL проверяет запрет кэширования чувствительного (обратное направление), REST-CACHE-CONDITIONAL-GET и HTTP-VARY-HEADER — другие заголовки; записи о наличии Cache-Control у кэшируемых ответов нет

Первоисточник:

````text
## Package Name & Version
The issue is present in `apollo-server-express`, the latest version (2.6.4).

## Latest version where the problem did not occur
I believe this issue was introduced with [this commit](https://github.com/apollographql/apollo-server/commit/ae14665aea126c0e6464dbabb34726534a3456c6), where a test was added explicitly for this behavior.

## Expected Behavior

When the `cacheControl` extension is enabled, the server should continue sending `Cache-Control` HTTP headers.

## Actual Behavior

When the `cacheControl` extension is enabled, the server no longer sends `Cache-Control` HTTP headers.

## Repo demonstrating the problem

https://github.com/blimmer/apollo-server-express-bug-report
````

## Идея 10 (`apollo-server`). Шлюз федерации выполняет допустимый запрос к общему типу из нескольких подграфов без ошибок

- **Предложение Claude:** не новая запись, а шаг-вариант к `GQL-GATEWAY-ROUTING`: В объединённой схеме выбрать поле общего типа-значения, объявленного в нескольких подграфах, у сущностей разных подграфов — данные возвращаются без ошибок

### apollographql/apollo-server#3141 — Fragment cannot be spread here as objects of type "_Entity" can never be of type "X"

Ссылка: https://github.com/apollographql/apollo-server/issues/3141

- **Действие:** Отправить запрос, выбирающий поле общего типа-значения у сущностей разных подграфов
- **Ожидание:** Данные возвращаются без ошибок

Первоисточник:

````text
Hi everyone!
From apollo-server v 2.8.0 we are able to use same Value Types in multiple services:
https://www.apollographql.com/docs/apollo-server/federation/core-concepts/#value-types

As an example I experimented with federation-demo:
https://github.com/apollographql/federation-demo

I've added object type (Logs) in **account service**:
```
extend type Query {
  me: User
}

type User @key(fields: "id") {
  id: ID!
  name: String
  username: String
  logs: [Logs]
}
type Logs {
  id: ID
  message: String
}
```
and the same type in **products service**:
```
extend type Query {
  topProducts(first: Int = 5): [Product]
}

type Product @key(fields: "upc") {
  upc: String!
  name: String
  price: Int
  weight: Int
  logs: [Logs]
}
type Logs {
  id: ID
  message: String
}
```
all project is compiled successfully and now we may use one object type (Logs) in multiple services (according the rule of value types in federated service is that the types **must be identical** in name and contents):
[image]

But when i try to prepare data for logs property: 
```
const users = [
  {
    id: "1",
    name: "Ada Lovelace",
    birthDate: "1815-12-10",
    username: "@ada",
    logs: [
      {
        id: 1,
        message: "Some Message"
      }
    ]
  }
];
```
I got the following error:
```
"errors": [
    {
      "message": "400: Bad Request",
      "extensions": {
        "code": "INTERNAL_SERVER_ERROR",
        "response": {
          "url": "http://localhost:4003/graphql",
          "status": 400,
          "statusText": "Bad Request",
          "body": {
            "errors": [
              {
                "message": "Fragment cannot be spread here as objects of type \"_Entity\" can never be of type \"Logs\".",
                "locations": [
                  {
                    "line": 3,
                    "column": 5
                  }
                ],
                "extensions": {
                  "code": "GRAPHQL_VALIDATION_FAILED",
                  "exception": {
                    "stacktrace": [
                      "GraphQLError: Fragment cannot be spread here as objects of type \"_Entity\" can never be of type \"Logs\".",
                      "    at Object.InlineFragment (C:\\_Redl\\temp\\federation-demo\\services\\products\\node_modules\\graphql\\validation\\rules\\PossibleFragmentSpreads.js:45:29)",
                      "    at Object.enter (C:\\_Re
````

## Идея 11 (`strapi`). Изменение упорядоченных связей, где в одном запросе connect ставит позицию относительно связи из disconnect (before/after удаляемой), выполняется с корректным порядком оставшихся связей или отклоняется 4xx с понятной ошибкой — без 5xx

- **Предложение Claude:** `accept` — `RES-RELATION-CONNECT-DISCONNECT-CONFLICT` в `checks/common/resource-lifecycle.yaml`

### strapi/strapi#25710 — Entity manager: disconnect processed before connect ordering causes sortConnectArray error

Ссылка: https://github.com/strapi/strapi/issues/25710

- **Паттерн:** Подключение связи с позицией относительно отключаемой в том же запросе обрабатывается
- **Условие:** Упорядоченные связи; в одном запросе изменения connect содержит позицию before/after относительно связи, которая есть в disconnect
- **Действие:** Отправить изменение с connect: [{id: A, position: {before: B}}] и disconnect: [{id: B}]
- **Ожидание:** Запрос выполняется, порядок оставшихся связей корректен (или 4xx с понятной ошибкой по контракту)
- **Источник ожидания:** Здравый смысл: перестановка и удаление в интерфейсе — штатный сценарий
- **Почему не подошла ближайшая запись:** RES-RELATION-ORDER-STABLE — про сохранность порядка у другой стороны, а не про конфликт connect и disconnect в одном запросе

Первоисточник:

````text
### Node Version

20

### NPM/Yarn/PNPM Version

npm 10

### Strapi Version

5.33.0

### Operating System

macOS / Linux

### Database

PostgreSQL

### Javascript or Typescript

Typescript

### Reproduction URL

_No response_

### Bug Description

When reordering and removing relations simultaneously in a component's relation field (e.g., drag-and-drop reorder + remove via Admin UI), the entity manager throws:

> There was a problem connecting relation with id **A** at position {"before":**B**,"status":"draft","locale":"en"}. The relation with id **B** needs to be connected first.

**Root cause:** The entity manager in `@strapi/database` processes `disconnect` before evaluating `connect` ordering. When a relation is both referenced by `position.before` in the connect array and present in the disconnect array, the following happens:

1. `disconnect` deletes the referenced relation (entity B) from the join table
2. `adjacentRelations` query looks for entity B — **not found** (just deleted)
3. `sortConnectArray` with `strictSort=true` throws the error

Additionally, `_.differenceWith(_.isEqual, disconnect, connect)` at [entity-manager/index.js L853](https://github.com/strapi/strapi/blob/main/packages/core/database/src/entity-manager/index.ts) always returns all disconnect items because disconnect items `{id}` and connect items `{id, position, __pivot, __type}` have structurally different shapes, so deep equality always fails. This means every disconnect item is unconditionally deleted regardless of whether it appears in the connect array.

### Steps to Reproduce

1. Create a content type with a component that has a `oneToMany` relation (e.g., a "PickUp" component with `articles`)
2. Add 3+ articles to the component and save
3. In the Admin UI, **drag** article A before article B (this creates `connect: [{A, position: {before: B}}]`)
4. **Remove** article B from the list (this creates `disconnect: [{B}]`)
5. Save → **Error: "The relation with id B needs to be connected first."**

**Key detail:** The error only occurs when steps 3 and 4 are done in the same save. Doing them separately (save after reorder, then save after delete) works fine.

### Diagnostic output

```
connect: [{ "id": 4, "documentId": "zmlc8gzg9ta3gnvnym26sxoy", "position": { "before": "hlvmnosjrfe4h7zqddwlhcil", "status": "draft" } }]
disconnect: [{ "id": 10, "documentId": "hlvmnosjrfe4h7zqddwlhcil" }]

Error: There was a problem connecting relation with id 4 at position {"before":10,"status" …[обрезано]
````

## Идея 12 (`strapi`). Массовая операция (публикация, изменение, удаление) применяет те же правила валидации, что одиночная, — запись, которую принимает одиночная операция, принимает и массовая, и наоборот, в том числе с вложенными компонентами

- **Предложение Claude:** `accept` — `RES-BULK-SINGLE-VALIDATION-PARITY` в `checks/common/resource-lifecycle.yaml`

### strapi/strapi#24576 — Bulk publish inside Content manager not working as expected when nested components inside dynamic zones are involved

Ссылка: https://github.com/strapi/strapi/issues/24576

- **Паттерн:** Массовая операция валидирует запись так же, как одиночная
- **Условие:** Запись с динамической зоной, в компоненте которой обязательный вложенный компонент заполнен
- **Действие:** Опубликовать запись одиночной операцией и массовой публикацией; сравнить результат валидации
- **Ожидание:** Обе операции признают запись готовой и публикуют её
- **Источник ожидания:** Здравый смысл: одно правило валидации для одиночной и массовой операции
- **Почему не подошла ближайшая запись:** RES-BULK-LIMITS — про лимиты и отчёт по элементам, а не про расхождение правил валидации массовой и одиночной операции

Первоисточник:

````text
### Node Version

22.17.0

### NPM/Yarn/PNPM Version

10.9.2

### Strapi Version

5.24.1

### Operating System

MacOS

### Database

PostgreSQL

### Javascript or Typescript

Typescript

### Reproduction URL

_No response_

### Bug Description

When having a required component, nested inside a component which is nested inside a dynamic zone, the publish bulk button inside the content manager will wrongly validate the entry as being not ready to publish, when in fact it is.

### Steps to Reproduce

1. Create a content type
2. Add a dynamic zone to the content type
3. Add a component to the dynamic zone
4. Inside the component, add another REQUIRED component
5. Create an entry, and add the required component to the entry
6. Try to publish the entry using the bulk publish option inside the content manager list

### Expected Behavior

The bulk publish should correctly validate the required component.

### Logs

```shell

```

### Code Snippets

_No response_

### Media

[image]

[image]

[image]

### Additional information

_No response_

### Confirmation Checklist

- [x] I have checked the existing [issues](https://github.com/strapi/strapi/issues) for duplicates.
- [x] I agree to follow this project's [Code of Conduct](https://github.com/strapi/strapi/blob/develop/CODE_OF_CONDUCT.md).
````

## Идея 13 (`ghsa-nuget`). Повторно предъявленное SAML-утверждение (или другой одноразовый токен входа — WS-Federation, OIDC ID-токен с nonce) в пределах срока действия отклоняется при включённой защите от повторов, в том числе на другом экземпляре сервиса

- **Предложение Claude:** `accept` — `AUTH-SAML-ASSERTION-REPLAY` в `checks/security/authentication-session.yaml`

### GHSA-9jr3-rj99-8jq3 — CoreWCF: SAML token replay protection is inoperative

Ссылка: https://github.com/advisories/GHSA-9jr3-rj99-8jq3

- **Паттерн:** Повторно предъявленный SAML-токен отклоняется при включённой защите от replay
- **Условие:** Сервис принимает SAML-токены и включено обнаружение повторов
- **Действие:** Предъявить один и тот же токен дважды в пределах срока действия
- **Ожидание:** Второе предъявление отклоняется ошибкой аутентификации
- **Источник ожидания:** OASIS SAML (OneTimeUse); OWASP API2:2023
- **Почему не подошла ближайшая запись:** Ближайшая SEC-TOKEN-REFRESH-REPLAY — про refresh-токены; записи о повторе одноразового утверждения при входе нет

Первоисточник:

````text
### Impact
When enabling DetectReplayedTokens, a token can be replayed and will be detected despite it being reused.

### Patches
Fixed in CoreWCF v1.8.1 and v1.9.1

### Workarounds
Provide your own implementation of `ITokenReplayCache` with the correct behavior.
````

## Индекс библиотеки

Все записи (497): ID | категория | заголовок.

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
AUTH-COOKIE-ATTRIBUTES | security | Сессионные cookie имеют Secure, HttpOnly, SameSite и узкие Domain/Path
AUTH-CSRF | security | Изменяющие операции с cookie-аутентификацией защищены от CSRF
AUTH-EXTERNAL-ID-EXACT-MATCH | security | Внешний идентификатор субъекта сравнивается побайтно в паре издатель и subject
AUTH-EXTERNAL-IDP-MISSING-ATTRIBUTES | security | Вход через внешний IdP без необязательных атрибутов профиля обрабатывается по требованиям
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
