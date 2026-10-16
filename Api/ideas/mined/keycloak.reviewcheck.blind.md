# Перекрёстное ревью новых идей выгрузки багов

Партия `keycloak`, идей: 19; вариант пакета — без решений Claude — независимое ревью.
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

## Идея 1. URI, которые формирует сервер (otpauth, ссылки в письмах, Location, redirect), кодируют значения по правилам своей части (пробел — %20 в пути, + только в query по форме) — после декодирования значение совпадает с исходным

### keycloak/keycloak#52296 — OTP key URI encodes spaces in the account name as '+' instead of %20

Ссылка: https://github.com/keycloak/keycloak/issues/52296

- **Паттерн:** URI, сформированный сервером, кодирует пробел по правилам своей части (%20 в пути)
- **Условие:** Имя учётной записи с пробелом попадает в метку otpauth-URI (часть пути)
- **Действие:** Создать пользователя с пробелом в имени, начать настройку OTP и разобрать выданный otpauth-URI
- **Ожидание:** Пробел закодирован как %20, декодированное имя совпадает с исходным
- **Источник ожидания:** RFC 3986 §2.1, §3.3 (в пути «+» — литерал); формат Key Uri Google Authenticator
- **Почему не подошла ближайшая запись:** REST-PATH-PARAM-ENCODING и REST-QUERY-ENCODING проверяют разбор входящих URL, а не кодирование URI, которые выдаёт сервер

Первоисточник:

````text
### Describe the bug

`OTPPolicy#getKeyURI` builds the account-name half of the `otpauth://` label with `URLEncoder.encode`, which produces the `application/x-www-form-urlencoded` form where a space becomes `+`:

```java
String accountName = URLEncoder.encode(rawAccountName, UTF_8);          // space -> '+'
...
String issuerName = URLEncoder.encode(issuerName, UTF_8).replaceAll("\\+", "%20"); // issuer fixes it
String label = issuerName + ":" + accountName;
```

The label is a URI **path** component, in which `+` is a literal plus, not a space. The issuer half already rewrites `+` to `%20`; the adjacent account-name line does not.

### Version

main

### Expected behavior

An account name containing a space (e.g. username `john doe`) is percent-encoded as `john%20doe` in the label, so authenticator apps display `john doe`.

### Actual behavior

The account name is rendered as `john+doe` and shown verbatim (`john+doe`) by authenticator apps such as Google Authenticator and FreeOTP.

### How to Reproduce

`new OTPPolicy().getKeyURI("Realm", "john doe", "secret")` yields a label `Realm:john+doe` instead of `Realm:john%20doe`.
````

## Идея 2. Обязательный шаг процесса (подтверждение email, смена пароля, настройка второго фактора) не назначается пользователю, который не может его выполнить (нет email, нет нужного канала), — законная операция не блокируется невыполнимым шагом; позитивная пара к BIZ-WORKFLOW-STEP-SKIP

### keycloak/keycloak#48634 — Verify Email gets added to all the users in the realm and blocks getting a REST Token

Ссылка: https://github.com/keycloak/keycloak/issues/48634

- **Паттерн:** Обязательное действие не назначается пользователю, который не может его выполнить
- **Условие:** В области включено обязательное подтверждение email, у пользователя нет email
- **Действие:** Включить подтверждение email и запросить токен password grant для пользователя без email
- **Ожидание:** Токен выдан, действие подтверждения email не назначено
- **Источник ожидания:** Здравый смысл: нельзя требовать шаг, который невозможно выполнить
- **Почему не подошла ближайшая запись:** BIZ-WORKFLOW-STEP-SKIP проверяет негативное направление (шаг нельзя пропустить); здесь законный вход блокируется невыполнимым шагом

Первоисточник:

````text
### Before reporting an issue

- [x] I have read and understood the above terms for submitting issues, and I understand that my issue may be closed without action if I do not follow them.

### Area

authentication/webauthn

### Describe the bug

The Verify Email option in Realm Settings is getting added to any user that logs after its enabled, this works for GUI login as that action is ignored if the user has no email configured but causes a REST user to get blocked with no way to login unless that action is removed and the setting is toggled off. 

### Version

26.5.6

### Regression

- [ ] The issue is a regression

### Expected behavior

I think the proper expected behaviour here should be that the action only gets added if the user has an email configured which will not block REST users unless they configure an email.

### Actual behavior

The actual behavior is that the action gets added to all the users regardless of whether they have an email set or not. There are use cases where there could be an OSS only user that will never have an email configured, this blocks these kind of users from logging in.

### How to Reproduce?

Turn on Verify email toggle and try getting a REST token for a user that doesn't have an email configured

### Anything else?

_No response_
````

## Идея 3. Если во время многошагового входа (обязательные действия, второй фактор, согласие) пользователя или клиента отключили, последний шаг проверяет их состояние заново — понятная ошибка «отключён», токен не выдаётся, 5xx нет

### keycloak/keycloak#48487 — Improper Authentication for required actions allows front-channel token issuance for disabled user in implicit/hybrid flow

Ссылка: https://github.com/keycloak/keycloak/issues/48487

- **Паттерн:** Блокировка учётки во время многошагового входа не даёт выпустить токен
- **Условие:** Пользователь на шаге обязательного действия (смена пароля), администратор в это время отключает учётку
- **Действие:** Начать вход по implicit/hybrid flow, отключить пользователя, завершить шаг обязательного действия
- **Ожидание:** Ошибка «учётная запись отключена», токен не выдан
- **Источник ожидания:** OWASP API2:2023; здравый смысл
- **Почему не подошла ближайшая запись:** SEC-AUTHZ-REVOKE-ROLE про отзыв роли у выданного токена; здесь состояние учётки не перепроверяется на последнем шаге незавершённого входа

Первоисточник:

````text
### Area

oidc

### Describe the bug

If a user is required to update their password and the admin disable the account during the time frame where the user is updating their password, the account deactivation will be ignored and a valid access_token is emitted for the disabled account. This works for both implicit and hybrid authentication flow.

### Acknowledgement

We thank Evan Hendra (Slvrqn) for reporting this item in our bug bounty program. This was later triaged by the Keycloak security team to be handled as a regular bug. 

### Version

 26.5.3

### Expected behavior

No access tokens generated as the user is disabled.

### Actual behavior

Access tokens generated implicit and hybrid authentication flow.

### How to Reproduce?

See original hunter's report.

---
*This issue was originally tracked in the private repository. Migrated by @ahus1.*
````

### keycloak/keycloak#46738 — NullPointerException Crash in SessionCodeChecks When Client is Disabled During Authentication Flow

Ссылка: https://github.com/keycloak/keycloak/issues/46738

- **Паттерн:** Отключение клиента во время незавершённого входа даёт понятную ошибку, а не 5xx
- **Условие:** Пользователь на форме входа, администратор отключает клиента
- **Действие:** Открыть форму входа, отключить клиента через admin API, отправить логин и пароль
- **Ожидание:** Страница ошибки «клиент отключён», токен не выдан
- **Источник ожидания:** Здравый смысл
- **Почему не подошла ближайшая запись:** Записей об изменении состояния участника во время многошагового входа нет; ERR-INTERNAL-ERROR-SHAPE — про вид 5xx, а не его отсутствие

Первоисточник:

````text
When an administrator disables a client while a user has an active authentication session, submitting the login form causes an unhandled `NullPointerException` in `SessionCodeChecks.initialVerify()`. This crash occurs because the method correctly detects the disabled client but then attempts to call `this.clientCode.removeExpiredClientSession()` before `clientCode` has been initialized. While this triggers a localized server error, the crash occurs before authentication processing, meaning there is no token issuance, no data leakage, and no bypass of security controls.

## Version affected

Keycloak 26.1.4 and Keycloak 26.5.4.

## Expected behavior

The server should gracefully handle the disabled client state and return a proper error page to the user, rather than crashing with an unhandled exception.

## Actual behavior

The server crashes with an unhandled `NullPointerException` on the authentication endpoint. Users see a generic HTTP 500 error instead of a helpful message, and the error is logged as an `Uncaught server error` in the server logs.

## Steps to reproduce

1. Start Keycloak in dev mode and obtain an admin access token.
    
2. Create a test realm and an OIDC client with implicit flow enabled.
    
3. Create a test user with credentials.
    
4. Start the authentication flow to obtain the login form URL.
    
5. Disable the client via the admin API while the user's login session is still active.
    
6. Submit the credentials to the login form.
    
7. Observe the HTTP 500 status and the `NullPointerException` in the server logs.
````

## Идея 4. Регистрация на чужой email с живой незавершённой сессией не даёт входа в аккаунт после того, как владелец сбросил пароль и подтвердил email, — подтверждение и сброс завершают чужие незавершённые сессии регистрации (pre-account takeover)

### keycloak/keycloak#48206 — Registration with email verification - corner case scenario for pre-account takeover

Ссылка: https://github.com/keycloak/keycloak/issues/48206

- **Паттерн:** Подтверждение email владельцем не завершает вход в чужой незавершённой сессии регистрации
- **Условие:** Аккаунт зарегистрирован чужим email, регистрант держит сессию на шаге «письмо отправлено», владелец email сбрасывает пароль и подтверждает email
- **Действие:** Зарегистрироваться на чужой email, держать сессию живой; от имени владельца сбросить пароль, подтвердить email, войти; обновить страницу в сессии регистранта
- **Ожидание:** Сессия регистранта не получает входа в аккаунт
- **Источник ожидания:** OWASP: pre-account takeover; здравый смысл
- **Почему не подошла ближайшая запись:** AUTH-EXTERNAL-IDP-UNVERIFIED-EMAIL про связывание через внешний IdP, BIZ-EMAIL-LINK-CROSS-SESSION — про работу ссылки в другой сессии (позитив); записи о pre-account takeover нет

Первоисточник:

````text
### Before reporting an issue

- [x] I have read and understood the above terms for submitting issues, and I understand that my issue may be closed without action if I do not follow them.

### Area

authentication

### Describe the bug

This issue is a follow-up after #45568 . That issue is partially fixed, but still there can be a corner case allowing pre-account take-over as a variant of what is described in #45568 :

1. an attacker creates an account using someone else's email address (classic pre-account takeover attack)
2. an email verification message is sent to the victim
3. the attacker waits at the screen which tells that a confirmation email was sent - if this authentication session expire, attack is not possible. But assume that attacker is refreshing the screen periodically for a long time until victim came to her browser (and continue with step 4 and further below)
4. the victim gets the emails
5. the victim doesn't confirm the email, but goes directly to the application
6. tries to log in, but can't and also can't register (as account already registered)
7. the victim clicks forgot password
8. password reset email is sent and the victim completes the action
9. victim sees the email verification and gets another confirmation mail
10. the victim now verifies the email and sets the password
11. victim logs in
12. attacker (who is waiting all this time) refreshes the login page and gets logged in too

### Version

main (after PR for 45568 merged)

### Regression

- [ ] The issue is a regression

### Expected behavior

When email is verified after user's registration, but email verification happened in a different browser, the original browser (where user registration was triggered) should not continue with other actions. Authentication session should be either expired or should not be able to continue with next steps after "Verify email" .

### Actual behavior

See description

### How to Reproduce?

See description

### Anything else?

_No response_
````

### keycloak/keycloak#45568 — Pending auth flow waiting for email verification succeeds even after password reset - providing room for pre-account takeover attacks

Ссылка: https://github.com/keycloak/keycloak/issues/45568

- **Паттерн:** Подтверждение email владельцем не завершает вход в чужой незавершённой сессии регистрации
- **Условие:** Аккаунт зарегистрирован чужим email, регистрант ждёт на шаге подтверждения email, владелец сбрасывает пароль и подтверждает email
- **Действие:** Зарегистрироваться на чужой email; от имени владельца сбросить пароль и подтвердить email; обновить страницу в сессии регистранта
- **Ожидание:** Сброс пароля завершает чужие незавершённые сессии, регистрант не входит
- **Источник ожидания:** OWASP: pre-account takeover; здравый смысл
- **Почему не подошла ближайшая запись:** AUTH-PASSWORD-CHANGE-REVOKES про завершение готовых сессий после сброса; здесь незавершённая сессия регистрации, записи о pre-account takeover нет

Первоисточник:

````text
### Before reporting an issue

- [x] I have read and understood the above terms for submitting issues, and I understand that my issue may be closed without action if I do not follow them.

### Area

authentication

### Describe the bug

An attacker can silently get logged into and stay logged in to a victim's account even when email verification is turned on in the realm.

Attack steps:
1. an attacker creates an account using someone else's email address (classic pre-account takeover attack)
2. an email verification message is sent to the victim
3. the attacker waits at the screen which tells that a confirmation email was sent - this session might expire, but then the attacker logs in again and the email is re-sent
4. the victim gets the emails
5. the victim **doesn't confirm the email**, but goes directly to the application
6. tries to log in, but can't since only the attacker knows the password
7. the victim clicks forgot password
8. password reset email is sent and the victim completes the action
9. either before or after the new password is set (however it is configured) the user sees the email verification screen too and gets another confirmation mail
10. the victim now verifies the email
11. user logs in
12. attacker (who is waiting all this time) refreshes the login page and gets logged in too

Note that, this is possible only if the victim completes both the password reset and email confirmation within the time while the attacker's verify email session is still valid.

### Version

26.5.1 (latest)

### Regression

- [ ] The issue is a regression

### Expected behavior

When I use the password reset flow, all pending sessions that might result in a login are invalidated. Or, only that pending session should succeed and result in a login which sent the message that the user actually used to verify the email.

### Actual behavior

A pending authentication session succeeds despite that within its lifetime credentials were reset and a different email confirmation link was used.

### How to Reproduce?

1. set up a virgin Keycloak installation
2. log into the admin console and create a new realm
3. enable forgot password feature and enforce email verification upon registration (needs email server configuration too, of course)
4. open two different browsers, one for the attacker, one for the victim
6. use the built-in account UI as the "application" and follow the steps from the description

### Anything else?

_No response_
````

## Идея 5. Операция, где тип ресурса задан в пути (/{type}/{id}), находит идентификатор среди объектов указанного типа для каждого поддерживаемого типа — позитивная матрица по типам; объект другого типа с тем же id не подставляется

### keycloak/keycloak#48094 — Wrong referenced resource type in Workflow handling for clients

Ссылка: https://github.com/keycloak/keycloak/issues/48094

- **Паттерн:** Операция с типом ресурса в пути ищет идентификатор среди объектов указанного типа
- **Условие:** Эндпоинт принимает тип ресурса и id в пути (activate/CLIENTS/{id})
- **Действие:** Вызвать операцию для каждого поддерживаемого типа с id существующего объекта этого типа
- **Ожидание:** Операция применяется к объекту указанного типа
- **Источник ожидания:** Контракт эндпоинта; здравый смысл
- **Почему не подошла ближайшая запись:** RES-REFERENTIAL-INTEGRITY про ссылку на несуществующий объект; здесь существующий объект указанного типа не находится — позитивная матрица по типам

Первоисточник:

````text
### Before reporting an issue

- [x] I have read and understood the above terms for submitting issues, and I understand that my issue may be closed without action if I do not follow them.

### Area

core

### Describe the bug

ClientResourceTypeWorkflowProvider.java line 72
 
    public Object resolveResource(String resourceId) {
        return ResourceType.USERS.resolveResource(session, resourceId);  // BUG: should be CLIENTS
    }

### Acknowledgement

Thank you to @Medoedus for reporting this. 

### Version

26.6.0

### Regression

- [ ] The issue is a regression

### Expected behavior

POST /admin/realms/{realm}/workflows/{id}/activate/CLIENTS/{resourceId} works with users.

### Actual behavior

It should work with clients.

### How to Reproduce?

tbd

### Anything else?

_No response_
````

## Идея 6. Выданные токены остаются действительными после перезапуска сервера (и между экземплярами) — идентификатор ключа подписи (kid) стабилен, ключ публикуется в JWKS, интроспекция и userinfo принимают токен до истечения

### keycloak/keycloak#47495 — JavaKeystoreKeyProvider generates a new random KID for symmetric keys (HMAC) on every restart or config change

Ссылка: https://github.com/keycloak/keycloak/issues/47495

- **Паттерн:** Выданные токены остаются действительными после перезапуска сервера
- **Условие:** Подпись HMAC ключом из keystore, сервер перезапускается или меняется конфигурация провайдера
- **Действие:** Получить токен, перезапустить сервер, проверить токен (интроспекция, userinfo) и kid в списке ключей
- **Ожидание:** kid стабилен, токен принимается
- **Источник ожидания:** RFC 7517 §4.5 (kid идентифицирует ключ); здравый смысл
- **Почему не подошла ближайшая запись:** RESIL-ENCRYPTION-KEY-ROTATION про смену ключа шифрования; здесь ключ не меняется, а теряется его идентификатор при перезапуске

Первоисточник:

````text
### Before reporting an issue

- [x] I have read and understood the above terms for submitting issues, and I understand that my issue may be closed without action if I do not follow them.

### Area

authorization-services

### Describe the bug

When using the java-keystore provider with symmetric keys (e.g., HS512, HS256), the KID (Key ID) is not stable. If the Keycloak server restarts or the java key provider config changes, the provider generates a new random KID.

In JavaKeystoreKeyProvider.java, the createKeyWrapper method initializes the KeyWrapper:
`keyWrapper.setKid(model.get(Attributes.KID_KEY, KeycloakModelUtils.generateId()));`

The logic checks if Attributes.KID_KEY exists in the component model. For symmetric key keystore configurations, this attribute is not persisted or explicitly set during the initial setup of the java-keystore provider. ConsequentlykeyWrapper.setKid(model.get(Attributes.KID_KEY, KeycloakModelUtils.generateId()));, it falls back to KeycloakModelUtils.generateId(), which creates a new UUID every time the provider is instantiated.

This causes all previously issued tokens signed with that secret to fail validation, as the ServerMacSignatureVerifierContext cannot find a matching KID in the current realm keys.

### Version

26.4.7 but it also same in latest version

### Regression

- [ ] The issue is a regression

### Expected behavior

The KID should be stable. It should ideally be derived from the alias name in the keystore or be persisted in the component configuration (KID_KEY attribute) upon the first load so that it remains identical across server restarts.

### Actual behavior

A new random KID is generated on every provider initialization, breaking token transition and validation.

### How to Reproduce?

- Create a Java Keystore (JKS) containing a SecretKey (for HS512).
- In Keycloak, go to Realm Settings -> Keys -> Providers.
- Add a java-keystore provider pointing to your JKS.
- Observe the KID of the HS512 key in the Active keys tab.
- Restart the Keycloak server or update the java-keystore provider configuration.
- Observe the KID again. It will have changed.
- Any tokens issued before the restart will now result in a VerificationException: Key not found during validation.

### Anything else?

_No response_
````

## Идея 7. Параметры входа, заданные на первом шаге (запомнить меня, locale, scope, prompt), сохраняются через все шаги аутентификации (выбор организации, второй фактор) и влияют на результат — длительная сессия и cookie remember me при rememberMe

### keycloak/keycloak#47017 — Remember me does not work when organization scope is enabled on login session.

Ссылка: https://github.com/keycloak/keycloak/issues/47017

- **Паттерн:** Параметры входа (remember me) сохраняются через все шаги аутентификации
- **Условие:** Вход с дополнительным шагом (scope organization) и отмеченным remember me
- **Действие:** Пройти вход с rememberMe=on и scope organization, проверить cookie и тип сессии
- **Ожидание:** Cookie remember me установлена, сессия длительная
- **Источник ожидания:** Документация remember me; здравый смысл
- **Почему не подошла ближайшая запись:** AUTH-SESSION-TIMEOUT и AUTH-COOKIE-ATTRIBUTES не проверяют сохранение параметров входа между шагами аутентификации

Первоисточник:

````text
### Before reporting an issue

- [x] I have read and understood the above terms for submitting issues, and I understand that my issue may be closed without action if I do not follow them.

### Area

authentication

### Describe the bug

When a user login using the keycloak-js client with the organization scope added and he decide to click the remember me button. The remember me tag from the authorization is ignored by the OrganizationAuthenticator and silently dropped from the authentication session. It then gets cleaned up by AbstractUsernameFormAuthenticator because rememberMe is not sent to it.

### Version

nightly (originally on 26.5.3, test done locally with main branch)

### Regression

- [ ] The issue is a regression

### Expected behavior

The person will see "Hello, ${name}! You are authenticated. Your organization is ${organizationName}." on the page
The user will receive a remember me cookie being set.

### Actual behavior

The person will see "You are not authenticated. Please log in."

### How to Reproduce?

1. Front-end :
Clone the sample front-end from here : [Esurnir/keycloak-org-remberme-repro](https://github.com/Esurnir/keycloak-org-remberme-repro)
run `npm install`
`npm run dev` to start frontend.
2. Keycloak backend (to match the /src/keycloak.ts settings) :
Start a keycloak instance on port 8080.
Create a realm named realm-with-orgs in keycloak (you can use the realm export json from the frontend to skip everything up to Create a user in keycloak).
Enable Organization on the realm.
Enable Add organization Id to the organization client scope mapper.
Enable Remember me.
Create a public client with standard-flow enabled named public-client. authorizing redirect to http://localhost:5173/* and origin http://localhost:5173
Create a user in keycloak.
Create two organization in keycloak.
Attach the user inside the two organization.

The test sequence:
1. Connect to http://localhost:5173 on a fresh session.
2. Click the login button
3. Enter your username and click remember me.
4. Select an organization
5. Close the browser entirely (or clear the session cookies).
6. Reopen the browser on http://localhost:5173
<Expected/VsActual case here>

### Anything else?

Because of the organization scope OrganizationAuthenticator is the handler setting the notes for the first request and need to handle the remember me note.
````

## Идея 8. Обмен токена (RFC 8693) без явного scope выдаёт области по умолчанию клиента, запросившего обмен, по документированному правилу — не области исходного или другого клиента

### keycloak/keycloak#45716 — Problem with Standard Token Exchange with Dynamic Scopes feature enabled (Wrong default scopes)

Ссылка: https://github.com/keycloak/keycloak/issues/45716

- **Паттерн:** Обмен токенов выдаёт области по умолчанию клиента, запросившего обмен
- **Условие:** Включена функция динамических областей доступа, выполняется обмен токенов
- **Действие:** Выполнить обмен токена клиентом-посредником без явного scope и сравнить scope результата с настройками этого клиента
- **Ожидание:** Scope по умолчанию — от клиента, запросившего обмен
- **Источник ожидания:** RFC 8693 §2.1; документация продукта
- **Почему не подошла ближайшая запись:** SEC-SCOPE-EXTRA-UNTRUSTED — про добавление scope параметром, AUTH-REFRESH-PRESERVES-SCOPE — про refresh; здесь обмен берёт scope по умолчанию от другого клиента при включённой функции

Первоисточник:

````text
### Before reporting an issue

- [x] I have read and understood the above terms for submitting issues, and I understand that my issue may be closed without action if I do not follow them.

### Area

token-exchange

### Describe the bug

Standard Token Exchange does not work well with Dynamic Scopes feature enabled.
The problem is that you need to set in AuthorizationRequestContext the new client (method `getRequestedScope`).
So, the default scopes is the scopes of the client of access token.

### Version

26.5.1

### Regression

- [ ] The issue is a regression

### Expected behavior

Return token exchange client default scopes

### Actual behavior

Return client  of access token default scopes

### How to Reproduce?

You could run `StandardTokenExchangeV2Test` tests with `@EnableFeature(value = Profile.Feature.DYNAMIC_SCOPES, skipRestart = true)`. So, token exchange tests will run with Dynamic Scopes feature enabled.
You will observe many fails due to the bug.

### Anything else?

_No response_
````

## Идея 9. Итог нескольких правил над одним значением в одном запросе (маппинг групп и ролей при входе, правила скидок, политики) детерминирован и соответствует документированному приоритету — повтор операции даёт тот же результат

### keycloak/keycloak#44480 — Wrong persistent group permissions when multiple group membership changes happen in the same request

Ссылка: https://github.com/keycloak/keycloak/issues/44480

- **Паттерн:** Итог нескольких правил над одним значением в одном запросе детерминирован
- **Условие:** Два правила сопоставления при входе через внешний IdP относятся к одной группе: одно добавляет пользователя, другое убирает
- **Действие:** Несколько раз выполнить вход и прочитать членство пользователя в группе
- **Ожидание:** Результат одинаков при каждом входе и соответствует правилу «добавление побеждает»
- **Источник ожидания:** Ожидание разработчиков в баге; здравый смысл
- **Почему не подошла ближайшая запись:** CONC-* — про параллельные запросы; здесь недетерминизм из-за порядка правил внутри одного запроса, подходящей записи нет

Первоисточник:

````text
### Before reporting an issue

- [x] I have read and understood the above terms for submitting issues, and I understand that my issue may be closed without action if I do not follow them.

### Area

core

### Describe the bug

When two IDP group mappers assign the same group and one decides to map the group and the other doesnt, there is currently a condition where sometimes the user is in the group and sometimes it is not. This is due to the following change: https://github.com/keycloak/keycloak/commit/bb9015a1f26ada048610e8b89f34c0f3959ac9a9 / #43682
Where `joinGroup()` is missing the condition `&& updated == null` causing it to miss other updates to the user done in the same request.

### Version

26.4.5

### Regression

- [x] The issue is a regression

### Expected behavior

If two group mappers map the same group and one wants to join and one wants to leave, the join always wins.

### Actual behavior

Race condition, sometimes user joins, sometimes he doesn't, depending on mapper execution order.

### How to Reproduce?

Skipping as discussed with @ahus1 

### Anything else?

_No response_
````

## Идея 10. Ограничения системных и административных ролей применяются по идентичности роли (id, область), а не по совпадению имени — пользовательская роль с таким же именем назначается законно, настоящая административная — по правилам

### keycloak/keycloak#43578 — "admin" client role now requires server admin user

Ссылка: https://github.com/keycloak/keycloak/issues/43578

- **Паттерн:** Ограничения системных ролей применяются по идентичности роли, а не по совпадению имени
- **Условие:** В обычной области у клиента создана собственная роль с именем, совпадающим с системной ролью администратора
- **Действие:** Назначить эту роль пользователю от имени сервисной учётки с правами управления пользователями
- **Ожидание:** Назначение проходит; ограничение действует только на настоящие административные роли
- **Источник ожидания:** Здравый смысл; поведение предыдущей версии
- **Почему не подошла ближайшая запись:** SEC-ROLE-SELF-ASSIGN и SEC-ROLE-LOW-TO-HIGH — негативные; здесь законное назначение отклоняется из-за совпадения имени, записи с этим направлением нет

Первоисточник:

````text
### Before reporting an issue

- [x] I have read and understood the above terms for submitting issues, and I understand that my issue may be closed without action if I do not follow them.

### Area

admin/api

### Describe the bug

Hi, 

after upgrading from 26.2 to 26.4.1, the changes made in https://github.com/keycloak/keycloak/issues/39956, also affect client roles named `admin` in non-admin realms.

This means the local realm-management account (service-account of the backend client) can no longer give the client role `admin` (no other roles or mappings associated to it) to other users.

It seems unlikely to me that this is intended behaviour as this role is only an admin role within the app the client is for, and not for the keycloak realm / master realm.

### Version

26.4.1

### Regression

- [ ] The issue is a regression

### Expected behavior

Only restrict actual admin (realm) roles.

### Actual behavior

`403 Forbidden`

### How to Reproduce?

* Create a new realm
* Create a new client with service-account and realm-management roles
* Create a new client role `admin`
* Create a dummy user
* Try to have the service-account give that user the `admin` client role

### Anything else?

_No response_
````

## Идея 11. Дополнительный фильтр списка не снимает ограничение по родительскому контейнеру

### keycloak/keycloak#48324 — UMA IS_ADMIN filter breaks ticket finding

Ссылка: https://github.com/keycloak/keycloak/issues/48324

- **Действие:** Создать тикеты в двух серверах ресурсов, запросить список первого с IS_ADMIN=true, затем список второго
- **Ожидание:** Каждый запрос возвращает только тикеты своего сервера ресурсов, второй запрос находит свои тикеты

Первоисточник:

````text
### Before reporting an issue

- [x] I have read and understood the above terms for submitting issues, and I understand that my issue may be closed without action if I do not follow them.

### Area

_No response_

### Describe the bug

Hello, 

I think this new `IS_ADMIN` UMA permission ticket filter broke the caching functionality. 
The MR: https://github.com/keycloak/keycloak/pull/47210
I'm talking about specifically this change: https://github.com/keycloak/keycloak/pull/47210/changes#diff-1e921492f31a55b4f93aaafdc92b2107801175e16b15e895108b213b9211d037R90

We have the following use case in our project as an ADMIN API: We want to retrieve all granted tickets within the system independently from their owner, requester, resource servers or anything else. This is what we do:

1. We retrieve all Resource Servers in the system
2. Iterate over the Resource Servers, and pull their tickets with (filters include `IS_ADMIN=true`, because we want to retrieve all tickets with the current user which is not either owner or requester):
`ticketStore.find(rs, filters, null, null)`

The above change causes Keycloak to pull **ALL tickets independently from their actual resource servers**, because it **does not** put this one: 

`predicates.add(builder.equal(root.get("resourceServer").get("id"), resourceServer.getId()));`

Then, if the first resource server is not the ticket's corresponding resource server, cache sets this ticket id as "not existing". So, when the actual resource server is queried in the next iteration, cache directly returns `null`, so we don't receive the ticket from this function call.

I think this should have been kept without touched:

```
if (resourceServer != null) {
            predicates.add(builder.equal(root.get("resourceServer").get("id"), resourceServer.getId()));
```

And, all other `IS_ADMIN` logic should be inside a separate if check.

### Version

26.5.7

### Regression

- [ ] The issue is a regression

### Expected behavior

Expected behavior is:
filter contains IS_ADMIN=true

When I run ticketStore.find(rs, filter, null, null), it should **only** care about the tickets that belong to that RS, not all tickets. So that, it won't do some caching for tickets that do not belong to that RS. In other words,

This should be added regardless of IS_ADMIN filter when resource server is not null:

`predicates.add(builder.equal(root.get("resourceServer").get("id"), resourceServer.getId()));`

### Actual behavior

filter contains IS_ADMIN=true

When I
````

## Идея 12. Client assertion с client_id внутреннего клиента и внешним sub принимается

### keycloak/keycloak#48024 — Relax Client ID validation for the Signed JWT - Federated (Kubernetes Service Accounts)

Ссылка: https://github.com/keycloak/keycloak/issues/48024

- **Действие:** Отправить client_credentials с client_assertion и client_id, отличным от sub
- **Ожидание:** Токен выдан, client_id сопоставлен с настроенным клиентом

Первоисточник:

````text
### Before reporting an issue

- [x] I have read and understood the above terms for submitting issues, and I understand that my issue may be closed without action if I do not follow them.

### Area

oidc

### Describe the bug

⚠️ This ticket is the complementary part of https://github.com/keycloak/terraform-provider-keycloak/issues/1542

The existing Keycloak Terraform Provider requires adding Client ID for the JWT authentication (`jwt_token` or `jwt_token_file`). When Client ID is sent, Keycloak ensures it needs to match the `sub` claim of a token ([code](https://github.com/keycloak/keycloak/blob/main/services/src/main/java/org/keycloak/authentication/authenticators/client/AbstractJWTClientValidator.java#L105-L108)). This leads to a very unfortunate requirement that Client IDs in Keycloak need to match a Kubernetes Token's sub, which is in the following form: `system:serviceaccount:my-namespace:my-serviceaccount`.

At the same time the [JSON Web Token (JWT) Profile for OAuth 2.0 Client Authentication and Authorization Grants RFC](https://datatracker.ietf.org/doc/html/rfc7523) also highlights that with Client Assertions, sending the `client_id` is optional:

> Authentication of the client is optional, as described in [Section 3.2.1](https://datatracker.ietf.org/doc/html/rfc7523#section-3.2.1) of OAuth 2.0 [[RFC6749](https://datatracker.ietf.org/doc/html/rfc6749)] and consequently, the "client_id" is only needed when a form of client authentication that relies on the parameter is used.

>  B.  For client authentication, the subject MUST be the "client_id" of the OAuth client.

The goal of this ticket is to relax the Client ID validation for the Signed JWTs (for Kubernetes Service Accounts)

### Version

nightly

### Regression

- [ ] The issue is a regression

### Expected behavior

As per RFC, the Client ID is optional so it shouldn't be validated. 

### Actual behavior

Client ID is required to match the `sub` claim which enforces the Clients to use Kubernetes Service Accounts notation. 

### How to Reproduce?

1) Setup Signed JWT - Federated scenario as usual
2) Try to obtain a token and send the `client_id` request param
3) Observe the error

### Discussion

https://github.com/keycloak/keycloak/discussions/48130

### Anything else?

I'm more than happy to contribute a patch for this. Please assign this ticket to me.
````

## Идея 13. Проверка прав, не поддерживаемая в текущей модели прав, отказывает 4xx, а не 5xx

### keycloak/keycloak#46718 — UnsupportedOperationException in V1 Token Exchange Audience Validation (FGAPv2 Incompatibility)

Ссылка: https://github.com/keycloak/keycloak/issues/46718

- **Действие:** Отправить token exchange с audience другого клиента
- **Ожидание:** Отказ 403/400 по правилам

Первоисточник:

````text
### Before reporting an issue

- [x] I have read and understood the above terms for submitting issues, and I understand that my issue may be closed without action if I do not follow them.

### Area

token-exchange

### Describe the bug

Thank you for binreaper for submitting this to our bug bounty program in YWH-PGM40475-143

## Summary

Keycloak 26.5.3 crashes with `UnsupportedOperationException` when performing a V1 token exchange with an `audience` parameter targeting a different client. The `V1TokenExchangeProvider.validateAudience()` calls `AdminPermissions.management().clients().canExchangeTo()`, which dispatches to `ClientPermissionsV2` when FGAPv2 is enabled (default in 26.5.3). `ClientPermissionsV2.canExchangeTo()` throws `UnsupportedOperationException("Not supported in V2")` instead of performing the authorization check, resulting in an HTTP 500 error.

## Vulnerability Type

Denial of Service / Improper Error Handling (CWE-754: Improper Check for Unusual or Exceptional Conditions)

## Affected Component(s)

- `services/src/main/java/org/keycloak/services/resources/admin/fgap/ClientPermissionsV2.java` — line 142-143
- Called from: `V1TokenExchangeProvider.validateAudience()` — line 254

## Keycloak Configuration Context

- TOKEN_EXCHANGE feature enabled (`--features=preview` or `--features=token-exchange`)
- FGAPv2 (Fine-Grained Admin Permissions V2) enabled — this is `Type.DEFAULT` in 26.5.3, so it applies to ALL default installations
- Any realm with at least two clients

### Version

26.5.3 

### Regression

- [ ] The issue is a regression

### Expected behavior

Do not log exceptions in the server log. 

Suggestions from the hunter: 

**Option 1** (preferred): Implement `canExchangeTo()` in `ClientPermissionsV2` using the V2 permission evaluation framework.

**Option 2**: Graceful fallback — return `false` (deny) instead of throwing:
```java
@Override
public boolean canExchangeTo(ClientModel authorizedClient, ClientModel to, AccessToken token) {
    return false; // V2 does not yet support client exchange permissions
}
```

**Option 3**: Guard in `V1TokenExchangeProvider` with try-catch around the `canExchangeTo()` call, returning HTTP 403 on `UnsupportedOperationException`.

### Actual behavior

500 response code, and an exception in the server log. 

### How to Reproduce?

## Steps to Reproduce (PoC)

1. Start Keycloak 26.5.3 with token exchange enabled:
```
docker run -p 8080:8080 -e KC_BOOTSTRAP_ADMIN_USERNAME=admin -e KC_BOOTSTRAP_ADMIN_
````

## Идея 14. Цепочка клиентских сертификатов длиннее настроенной обрезается, а не ломает аутентификацию

### keycloak/keycloak#46647 — Rfc9440 cert lookup should not treat exceeding the cert length as an error

Ссылка: https://github.com/keycloak/keycloak/issues/46647

- **Действие:** Отправить запрос с mTLS-аутентификацией клиента через прокси с цепочкой из 2+ сертификатов
- **Ожидание:** Используются первые N сертификатов, аутентификация по клиентскому сертификату проходит

Первоисточник:

````text
### Before reporting an issue

- [x] I have read and understood the above terms for submitting issues, and I understand that my issue may be closed without action if I do not follow them.

### Area

core

### Describe the bug

If the proxy sends a cert chain with multiple certs and the certificateChainLength is left as the default of 1, an exception will be thrown.

### Version

26.5

### Regression

- [ ] The issue is a regression

### Expected behavior

Instead only at most certificateChainLength should be returned - this is consistent with the nginx behavior.

### Actual behavior

An exception.

### How to Reproduce?

Leave the certificateChainLength as 1 and have a request with multiple certs in the chain.

### Anything else?

_No response_
````

## Идея 15. Выход без активной SSO-сессии перенаправляет на post_logout_redirect_uri

### keycloak/keycloak#46379 — Unexpected error when logging out with offline session and external IDP

Ссылка: https://github.com/keycloak/keycloak/issues/46379

- **Действие:** Вызвать logout с id_token_hint и post_logout_redirect_uri
- **Ожидание:** Перенаправление на post_logout_redirect_uri без ошибки

Первоисточник:

````text
### Before reporting an issue

- [x] I have read and understood the above terms for submitting issues, and I understand that my issue may be closed without action if I do not follow them.

### Area

oidc

### Describe the bug

When a client starts a flow with only offline_access, no SSO session is generated. When the user used an external IDP to authenticate, Keycloak will still try to do a logout at the external IDP if one was used. The logout redirect to the external IDP works but it fails on the `logout_response` endpoint since no session is found.

### Version

26.5.3

### Regression

- [x] The issue is a regression

### Expected behavior

If the user tries to logout with valid ID token and post_logout_redirect_uri without an SSO session, Keycloak should just redirect back to the post_logout_redirect_uri.

### Actual behavior

Keycloak forwards to the external IDP for logout but fails to handle the logout_response from the external IDP.

### How to Reproduce?

https://github.com/user-attachments/assets/0d6320e7-a5f8-421a-b942-b630057d3bda

[docker-compose.yml](https://github.com/user-attachments/files/25341109/docker-compose.yml)

[test_setup.tf.txt](https://github.com/user-attachments/files/25341123/test_setup.tf.txt)

1. Install terraform (https://developer.hashicorp.com/terraform/install)
2. Install oauth2c (https://github.com/SecureAuthCorp/oauth2c)
3. Download the two attached files and put them into a directory, remove the `.txt` ending from `test_setup_tf_txt`.
4. Run `docker compose up`
5. Run `terraform init`
6. Run `terraform apply` and confirm with entering `yes`
7. Run: 
`echo "http://localhost:8080/realms/B/protocol/openid-connect/logout?client_id=test&post_logout_redirect_uri=http%3A%2F%2Flocalhost%3A8803%2Fcallback-logout&id_token_hint=$(oauth2c http://localhost:8080/realms/B \
  --client-id test \
  --grant-type authorization_code \
  --redirect-url http://localhost:8803/callback \
  --auth-method none \
  --response-types code \
  --response-mode query \
  --scopes "openid offline_access" \
  --pkce | grep '{"access_token":"ey' | jq -r .id_token)"`
8. Click "Realm A", login with user `test` password `test`
9. Copy the logout URL from the terminal window and paste it into the browser to trigger the logout.

Please also check the attached video.

### Anything else?

The full related code is quite complex but a related snippet is definitely https://github.com/keycloak/keycloak/blob/51010315168f8d59c246b60104ff6b67bb1e322d/services/src/mai
````

## Идея 16. Специальное значение-маркер в поле URI принимается проверкой формата

### keycloak/keycloak#45587 — SecureClientUrisExecutor doesn't allow for "+" weborigin

Ссылка: https://github.com/keycloak/keycloak/issues/45587

- **Действие:** Создать или обновить клиента с webOrigins=["+"]
- **Ожидание:** Клиент сохранён

Первоисточник:

````text
### Before reporting an issue

- [x] I have read and understood the above terms for submitting issues, and I understand that my issue may be closed without action if I do not follow them.

### Area

oidc

### Describe the bug

When adding a `secure-client-uris` policy check, this does not allow a Web Origins setting of `+` even though those URLs are secure.

### Version

main

### Regression

- [ ] The issue is a regression

### Expected behavior

A `+` should be accepted if the `rootUrl` and `redirectUris` are secure.

### Actual behavior

A `+` leads to a validation error in the frontend: 

> Invalid webOrigins

### How to Reproduce?

* Create a client policy that contains `secure-client-uris`
* Enter `+` in the WebOrigins

### Anything else?

The problematic code is somewhere about here: 

https://github.com/keycloak/keycloak/blob/a2c1055f8df21b53b969f922fb9a044a76d22604/services/src/main/java/org/keycloak/services/clientpolicy/executor/SecureClientUrisExecutor.java#L106-L108

The WebOrigins are usually resolved as shown here: 

https://github.com/keycloak/keycloak/blob/a2c1055f8df21b53b969f922fb9a044a76d22604/services/src/main/java/org/keycloak/protocol/oidc/utils/WebOriginsUtils.java#L39-L46
````

## Идея 17. JSON ответа и токена не содержит дублирующихся ключей

### keycloak/keycloak#45250 — IDToken contains duplicate address claims

Ссылка: https://github.com/keycloak/keycloak/issues/45250

- **Действие:** Получить ID-токен, разобрать payload парсером со строгой проверкой дублей
- **Ожидание:** Ключ address один

Первоисточник:

````text
### Before reporting an issue

- [x] I have read and understood the above terms for submitting issues, and I understand that my issue may be closed without action if I do not follow them.

### Area

oidc

### Describe the bug

When an IDToken with an `address` claim is generated, the `address` is added twice

### Version

26.5.0

### Regression

- [x] The issue is a regression

### Expected behavior

There should only be one `address` claim.

### Actual behavior

The `address` claim is duplicated.

### How to Reproduce?

Create an ID Token with an address claim mapper.

### Anything else?

This is a regression.

// ID Token from Keycloak 26.4.7
```
eyJhbGciOiJFUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJBb2pxdlJURGJucmhqeUxjcEl1V0p3MzNKRy1Pd3loeW8xMEF4U0JfdDFzIn0.eyJleHAiOjE3Njc4NDY5MDEsImlhdCI6MTc2Nzg0NjYwMSwiYXV0aF90aW1lIjoxNzY3ODQ2NTgxLCJqdGkiOiJhMTVhOTQ5Ny0zYTQwLTY2YTYtYjFmNi0yNjIxNGVkNmQxNTkiLCJpc3MiOiJodHRwczovL2FzLmtleWNsb2FrLWZhcGkub3JnL2F1dGgvcmVhbG1zL3Rlc3QiLCJhdWQiOiJjbGllbnQxLW9pZGNjLWJhc2ljIiwic3ViIjoiMDkzZjJiYWUtOTBhNS00NzlhLWJmOTItMTVhYWQ1OTJkZTI5IiwidHlwIjoiSUQiLCJhenAiOiJjbGllbnQxLW9pZGNjLWJhc2ljIiwibm9uY2UiOiJxVkdXeXBTSURxIiwic2lkIjoiZGQ5YWRhMTctMWI1ZC1lYTMyLWZhOWQtNGZkMmY3NjdhNGQxIiwiYXRfaGFzaCI6IlJ6SEVzcjNHZm16TGFWbVBDWDFxMWciLCJhZGRyZXNzIjp7ImNvdW50cnkiOiJVSyJ9fQ.BG79Y_Oqvj6N1nSHG2aF2YJh64CHHh6y5UG0dC214yGwEmNs0WQz1uuhawPhk9Uv0VLx7dC6wscM_Tt2tMFlRA
```

// ID Token from Keycloak 26.5.0 
```
eyJhbGciOiJFUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJZMGpLbkhWTDYzSjZCNGxVSERmQ3FIZHBtdFlkVWxneVlZY080QVdHcERZIn0.eyJleHAiOjE3Njc4NDc3NTIsImlhdCI6MTc2Nzg0NzQ1MiwiYXV0aF90aW1lIjoxNzY3ODQ3NDUxLCJqdGkiOiJmYmYzMGIzYi0zZWVlLThjOTEtYTVhYy00NWZhMDgyM2QwOTAiLCJpc3MiOiJodHRwczovL2FzLmtleWNsb2FrLWZhcGkub3JnL2F1dGgvcmVhbG1zL3Rlc3QiLCJhdWQiOiJjbGllbnQxLW9pZGNjLWJhc2ljIiwic3ViIjoiYTdlMWExYTktNjYzYy00ZWE3LThjOTMtYTQ3Mzc0YzE4NzNhIiwidHlwIjoiSUQiLCJhenAiOiJjbGllbnQxLW9pZGNjLWJhc2ljIiwibm9uY2UiOiI1RXNycWZHNTdMIiwic2lkIjoiTkpBV2MtWHQzZGF0NndUZlFRbldSZWdEIiwiYXRfaGFzaCI6IjBtYzh6Q3JLZHh2WTloYmJEZDlxeGciLCJhZGRyZXNzIjp7ImNvdW50cnkiOiJVSyJ9LCJhZGRyZXNzIjp7ImNvdW50cnkiOiJVSyJ9fQ.n3luMHu7Ee6UGpZroQDkRNflCdV6ZHm2tBzISGS2SF1Gl2lE-tEwrqg10Mszyu4zs0uDsAOakTUPqrKTY2pwFA
```

This issue was found while running the OIDF Conformance Tests by @tnorimat.

The conformance tests use GSON instead of Jackson for serialization which is more sensible to duplicate Keys.

[image]

The intelliJ debugger and jackson doesn't detect this as it's json object parsing ignores duplicate keys in json objec
````

## Идея 18. Включение флага при изменении создаёт зависимые объекты так же, как при создании

### keycloak/keycloak#44257 — OIDC Dynamic Client Registration update problem when Service Account was enabled/ disabled

Ссылка: https://github.com/keycloak/keycloak/issues/44257

- **Действие:** Изменить флаг через DCR и проверить наличие служебного пользователя
- **Ожидание:** Служебный пользователь создаётся при включении и удаляется при выключении

Первоисточник:

````text
### Before reporting an issue

- [x] I have read and understood the above terms for submitting issues, and I understand that my issue may be closed without action if I do not follow them.

### Area

oidc

### Describe the bug

During OIDC Dynamic Client Registration update,  when the Service Account was enabled/ disabled, Keycloak does not do create/ delete service account user.

### Version

26.4.5

### Regression

- [ ] The issue is a regression

### Expected behavior

During OIDC Dynamic Client Registration update,  when the Service Account was enabled/ disabled, Keycloak is expected to create/ delete service account user.

### Actual behavior

Service account user does not create/ delete OIDC Dynamic Client Registration update even if Service account client was enabled/ disabled.

### How to Reproduce?

- Create with dynamic client registration a no service account client.
- Update the client with dynamic client registration enabling service account.

### Anything else?

_No response_
````

## Идея 19. Политика проверки redirect URI принимает корректные адреса

### keycloak/keycloak#51315 — Invalid URI Type for a valid URI when using "oauth-2-1-for-public-client"

Ссылка: https://github.com/keycloak/keycloak/issues/51315

- **Действие:** Сохранить клиент с корректным redirect URI через административный API
- **Ожидание:** Клиент сохраняется; отклоняются только адреса, нарушающие политику, и причина отказа указывает введённое значение

Первоисточник:

````text
### Before reporting an issue

- [x] I have read and understood the above terms for submitting issues, and I understand that my issue may be closed without action if I do not follow them.

### Area

admin/api

### Describe the bug

A public client policy using the built-in profile "oauth-2-1-for-public-client" prevents saving clients with valid redirect URIs.

Example redirect URI:
https://example.org/callback

Without the policy the client can be saved successfully.

Server log:
DEBUG org.keycloak.services.clientpolicy.executor.SecureRedirectUrisEnforcerExecutor
Invalid URI Type - input =

The log is unusual because the URI value appears to be empty in contrast to, for example, the absence of https: 
Invalid LoopbackAddress: HTTP not allowed - input = http://127.0.0.1:8080/callback

In 26.4.7 the behavior was different. The URI was parsed and classified
correctly. This looks like a regression between 26.4.7 and 26.7.0.

### Version

26.7.0

### Regression

- [x] The issue is a regression

### Expected behavior

1. It should be possible to save valid redirect URLs in combination with the profile "oauth-2-1-for-public-client"
2. Invalid URls should be logged properly

### Actual behavior

1. A valid redirect URLs is rejected when using the profile "oauth-2-1-for-public-client"
2. The actual URL is not logged 

### How to Reproduce?

1. Assing the the profile "oauth-2-1-for-public-client" to a client
2. Save with a valid redirect URL

### Anything else?

It seems to be an error in the admin UI. We could save the change using the admin REST service. But it is not possible to save it in the UI.

Workaround exists to configure also non-empty Post-logout-redirect URIs (See comment below): https://github.com/keycloak/keycloak/issues/51315#issuecomment-5758504510

_No response_
````

## Индекс библиотеки

Все записи (620): ID | категория | заголовок.

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
ASYNC-SCHEDULE-DST-TRANSITION | async | Расписание на несуществующее или повторяющееся местное время срабатывает по правилу
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
AUTH-CREDENTIAL-CHANNEL-STRICT | security | Учётные данные принимаются только по документированному каналу
AUTH-CSRF | security | Изменяющие операции с cookie-аутентификацией защищены от CSRF
AUTH-DUPLICATE-CREDENTIALS | security | Повторяющиеся и пустые учётные данные не дают доступа
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
AUTH-LOGIN-CROSS-ACCOUNT-COOKIE | security | Вход другой учёткой с cookie действующей сессии обрабатывается по правилу
AUTH-LOGIN-IDENTIFIER-NORMALIZATION | validation | Логин (email, телефон) нормализуется одинаково при входе, создании и поиске
AUTH-LOGOUT-CLEARS-COOKIE | security | Выход снимает cookie сессии на клиенте
AUTH-LOGOUT-INVALIDATES | security | После выхода токен и сессия недействительны
AUTH-LOGOUT-SCOPE | security | Выход завершает только текущую сессию
AUTH-MFA-STEP-UP | security | Операции, требующие второго фактора, недоступны без него
AUTH-MFA-UNENROLLED-ERROR | security | Ошибка шага второго фактора у пользователя без зарегистрированного фактора — обычная 4xx
AUTH-NOSQL-OPERATOR-CREDENTIALS | security | Операторы NoSQL в учётных данных входа отклоняются
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
AUTH-PASSWORD-CHANGE-REQUIRES-CURRENT | security | Смена пароля требует верный текущий пароль
AUTH-PASSWORD-CHANGE-REVOKES | security | Смена или сброс пароля завершает другие сессии
AUTH-PASSWORD-POLICY | security | Политика паролей применяется на сервере
AUTH-PASSWORD-RESET-TOKEN | security | Токен сброса пароля одноразовый, ограничен по времени и привязан к пользователю
AUTH-PATH-NORMALIZATION-BYPASS | security | Вариации пути защищённого маршрута не обходят аутентификацию
AUTH-PROTOCOL-SESSION-OWNER-BINDING | security | Идентификатор протокольной сессии привязан к аутентифицированному владельцу
AUTH-REFRESH-PRESERVES-SCOPE | security | Refresh без параметра scope сохраняет scope исходной авторизации
AUTH-REVOKED-COOKIE-RELOGIN | security | Вход с закрытой cookie сессии создаёт новую сессию
AUTH-SAML-ASSERTION-REPLAY | security | Повторно предъявленное SAML-утверждение отклоняется
AUTH-SENSITIVE-CHANGE-REAUTH | security | Изменение защиты учётки требует свежей аутентификации
AUTH-SESSION-FILTER-SCOPE | security | Операции над сессиями ограничены сессиями своей учётки
AUTH-SESSION-FIXATION | security | Идентификатор сессии меняется после входа
AUTH-SESSION-ID-ENTROPY | security | Идентификатор сессии новый при каждом входе, уникален и непредсказуем
AUTH-SESSION-ID-NOT-EXPOSED | security | Список сессий не раскрывает значение cookie сессии
AUTH-SESSION-NOT-BEFORE-LOGIN | security | Анонимный запрос не получает cookie сессии и не создаёт серверную сессию
AUTH-SESSION-SLIDING-RENEWAL | security | Активность продлевает сессию по правилам скользящего срока
AUTH-SESSION-TIMEOUT | security | Сессия истекает после простоя и абсолютного срока
AUTH-SESSION-VALUE-EXACT-MATCH | security | Значение сессии сравнивается целиком и точно
AUTH-TOKEN-IN-URL | security | Учётные данные не передаются и не принимаются в URL
AUTH-TOKEN-INTROSPECTION | security | Интроспекция токена возвращает актуальное состояние и те же claims, что в токене
AUTH-TOKEN-RESERVED-CLAIMS | security | Пользовательские поля не переопределяют зарезервированные claims токена
AUTH-TOKEN-SENDER-CONSTRAINED | security | Обмен и обновление токена сохраняют привязку к отправителю (DPoP, mTLS)
AUTH-TOKEN-TYPE-CONFUSION | security | Refresh, ID или сервисный токен не принимается как access-токен
AUTH-USER-ENUMERATION | security | Ответы входа, регистрации и восстановления не раскрывают существование аккаунта
BIZ-AMBIGUOUS-ADDRESS | business-logic | Неоднозначный почтовый адрес не выбирается молча по первому совпадению
BIZ-CLIENT-PRICE-TAMPERING | business-logic | Цена, скидка и итог рассчитываются на сервере
BIZ-CONFIG-SCOPE-PRECEDENCE | business-logic | Настройка более узкого уровня имеет приоритет над глобальной
BIZ-CURRENCY-MISMATCH | business-logic | Смешение валют в операции обрабатывается явно
BIZ-DIVISION-BY-ZERO | business-logic | Входы с нулём в знаменателе не дают 500 и нечисловых значений
BIZ-DOUBLE-SPEND | business-logic | Параллельные списания не приводят к двойной трате
BIZ-EMAIL-LINK-CROSS-SESSION | business-logic | Ссылка-действие из письма работает в другой сессии и после перезапуска сервиса
BIZ-EMAIL-NOTIFICATION-DELIVERY | business-logic | Письма уходят нужному адресату с верными ссылками и без внедрения заголовков
BIZ-FLAG-EFFECT-MATRIX | business-logic | Каждый флаг сущности влияет на поведение так, как описано
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
CONTRACT-RESPONSE-LINKS-RESOLVE | contract | URL в ответах открываются
CONTRACT-UNKNOWN-FIELD-POLICY | contract | Unknown fields follow the documented contract policy
DB-ACCESS-SCOPE-IN-QUERY | db | Граница доступа задаётся в самом запросе к БД
DB-ALTER-PRESERVES-COLUMN | db | Изменение столбца или ограничения сохраняет его остальные свойства
DB-API-DATA-MATCH | db | После операции API в БД изменены ровно ожидаемые строки с ожидаемыми значениями
DB-CASCADE-SCOPE | db | Каскадные изменения ограничены областью удаляемой записи
DB-CATALOG-READ-CORRECTNESS | db | Чтение каталога схемы даёт точную модель объектов
DB-CATALOG-READ-PERFORMANCE | db | Чтение каталога схемы быстрое и не повторяется без нужды
DB-COLLATION-COMPARISON | db | Сравнение строк в БД соответствует назначению колонки
DB-CONNECTION-CONFIG-HANDLING | db | Ошибки и формы настройки подключения к БД обрабатываются предсказуемо
DB-CONNECTION-POOL-LIFECYCLE | db | Соединения пула освобождаются и не оставляют фоновой нагрузки
DB-DEFAULT-PRECEDENCE | db | Значения по умолчанию применяются по правилам СУБД при любом способе вставки
DB-DRIVER-LARGE-PARAMS | db | Драйвер БД обрабатывает параметры очень большого размера
DB-DYNAMIC-SQL-PARAMETERIZED | db | Значения и идентификаторы из ввода и из БД попадают в SQL параметрами или по allowlist
DB-GENERATED-SQL-SHAPE | db | Генерируемый SQL не выполняет лишней работы
DB-IDENTIFIER-QUOTING | db | Имена объектов БД экранируются во всех служебных и генерируемых запросах
DB-IMPORT-CONSISTENCY | db | Импорт не оставляет частичного состояния вне документированной политики
DB-IN-DB-CONFIG-APPLIED | db | Настройки сервиса, хранящиеся в БД, применяются ко всем видам ресурсов
DB-KEYS-AND-CONSTRAINTS | db | Ключи и ограничения защищают целостность независимо от приложения
DB-METADATA-CACHE-FRESH | db | Кэш метаданных схемы в сервисе актуален после изменений БД
DB-MIGRATION-CLEAN-INSTALL | db | Миграции разворачиваются на чистой БД, в том числе в нестандартной схеме
DB-MIGRATION-DATA-PRESERVED | db | Миграции переносят данные и связи без искажений
DB-MIGRATION-STATE-TRACKED | db | Применённые миграции учитываются, повторный запуск безопасен
DB-MIN-VERSION-COMPATIBILITY | db | Сервис работает на минимальной поддерживаемой версии СУБД
DB-MUTATION-SCOPE | db | Операция API меняет в БД только ожидаемые таблицы и строки
DB-QUERY-INDEX-USAGE | db | Запросы приложения используют подходящие индексы на реалистичном объёме
DB-ROLE-SWITCH-SETTINGS | db | При переключении роли применяются только допустимые для неё настройки
DB-SCHEMA-CHANGE-VALIDATED | db | Запрос изменения схемы проверяется до выполнения DDL
DB-SCHEMA-MATCHES-SPEC | db | Схема БД совпадает со спецификацией и контрактом API
DB-SENSITIVE-DATA-PROTECTED | db | Чувствительные данные хранятся защищённо
DB-SERVICE-ROLE-LEAST-PRIVILEGE | db | Роль подключения сервиса имеет минимальные права
DB-STORED-ROUTINES | db | Хранимые процедуры и функции установлены и работают по спецификации
DB-TRIGGERS | db | Триггеры срабатывают ровно на нужные события и изолированы
DB-TYPED-COMPARISONS | db | Значения сравниваются и приводятся в типе колонки
DB-VISIBILITY-CHANGE-CLEANUP | db | Смена видимости ресурса очищает производные данные пользователей без доступа
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
FILE-ROUNDTRIP-EXACT | files | Загруженный файл скачивается байт в байт
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
HARD-ENVIRONMENT-ISOLATION | security | Тестовый стенд не обращается к ресурсам production
HARD-EXCESSIVE-DATA-EXPOSURE | security | Ответы не содержат внутренних полей сверх контракта
HARD-EXPENSIVE-OPERATION-LIMITS | security | Дорогие операции ограничены по ресурсам
HARD-HOST-HEADER | security | Подмена Host и X-Forwarded-Host не влияет на ссылки и маршрутизацию
HARD-ID-PREDICTABILITY | security | Предсказуемые идентификаторы не позволяют собрать данные перебором
HARD-IP-ALLOWLIST | security | Ограничение доступа по адресам и подсетям работает на границах для IPv4 и IPv6
HARD-METHOD-OVERRIDE | security | Заголовки переопределения метода не обходят авторизацию
HARD-NOT-IMPLEMENTED-INERT | security | Операция, помеченная в контракте как нереализованная, не выполняется
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
HTTP-PREFERENCE-APPLIED-ACCURATE | http-semantics | Preference-Applied перечисляет ровно применённые предпочтения
HTTP-REDIRECT-ENDPOINT-PARITY | http-semantics | Вызов через перенаправляющий адрес работает как прямой вызов
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
INJ-DOWNSTREAM-BODY-INJECTION | security | Значение поля не внедряет ключи в тело запроса к другой системе
INJ-FILTER-EXPRESSION | security | Выражения фильтрации (OData, RSQL, JSONPath, GraphQL where) не позволяют выйти за ограничения
INJ-HEADER-CRLF | security | CRLF в значениях не позволяет внедрять заголовки ответа
INJ-LLM-GENERATED-ACTIONS | security | Код и вызовы инструментов, сгенерированные LLM по вводу пользователя, не выполняют опасных действий
INJ-LOG-FORGING | security | Пользовательские данные не позволяют подделывать записи журналов
INJ-NOSQL | security | NoSQL-инъекция операторами запросов не исполняется
INJ-NULL-BYTE | security | NUL-байт во входных данных отклоняется или не обрезает значение
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
OBS-BUILD-VERSION-TRACEABLE | observability | Версия сборки доступна для трассировки на тестовых стендах и скрыта в production
OBS-CONFIG-ENDPOINT-ACCURATE | observability | Служебный эндпоинт конфигурации показывает фактические значения
OBS-HEALTH-ENDPOINTS | observability | Health-эндпоинты отражают состояние и не раскрывают детали
OBS-LOG-ENTRY-INTEGRITY | observability | Записи журнала при всплеске параллельных запросов не склеиваются
OBS-METRICS-LABEL-CARDINALITY | observability | Значения из запроса не создают неограниченно новых серий метрик
OBS-METRICS-VALUE-RANGE | observability | Gauge-метрики с известными границами остаются в них после сбоев и восстановления
OBS-NO-SECRETS-IN-LOGS | observability | Логи не содержат паролей, токенов и ПДн в открытом виде
OBS-REQUEST-LOG-ALL-ATTEMPTS | observability | Журнал запроса с повторами содержит каждую попытку, включая последнюю
OBS-SERVER-TIMING-ACCURATE | observability | Server-Timing отражает фактическую длительность этапов
OBS-TELEMETRY-FORMAT | observability | Экспортируемая телеметрия соответствует документированной структуре и соглашениям OpenTelemetry
OBS-TRACE-PROPAGATION | observability | Контекст трассировки принимается и передаётся дальше
PAGE-BEYOND-LAST | pagination | Запрос страницы за последней возвращает пустой результат без ошибки
PAGE-CONCURRENT-MODIFICATION | pagination | Изменения коллекции во время обхода не приводят к дублям и пропускам сверх контракта
PAGE-CURSOR-TAMPERING | pagination | Подделанный или чужой курсор пагинации не раскрывает данные
PAGE-NEXT-LINK-VALID | pagination | Ссылка next ведёт на ту же коллекцию, сохраняет фильтры и работает
PAGE-SEARCH-SPECIAL-CHARS | pagination | Поиск со спецсимволами и wildcard не ломается и не расширяет выборку
PAGE-SORT-FIELD-TYPE-MATRIX | pagination | Сортировка по каждому полю учитывает его тип, локаль и направление
PAGE-SORT-MULTI-KEY-PRIORITY | pagination | Сортировка по нескольким ключам соблюдает заданный клиентом порядок приоритета
PAGE-SORT-NULLS-TIES | pagination | Сортировка по полю с null и одинаковыми значениями детерминирована
PAGE-TOTAL-COUNT | pagination | Общее число элементов согласовано с суммой страниц
PERF-DEEP-PAGINATION | performance | Глубокая пагинация и большие выборки не деградируют неприемлемо
PERF-LATENCY-BASELINE | performance | Задержка ключевых операций в пределах SLO при обычной нагрузке
PERF-LOAD-THROUGHPUT | performance | Сервис выдерживает целевую нагрузку
PERF-METADATA-RELOAD-NO-BLOCK | performance | Перезагрузка кэша метаданных не блокирует обслуживание запросов надолго
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
RES-REFERENCE-DATA-COMPLETE | resources | Справочники через API полные, упорядочены по документации и управляются без релиза
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
RES-VALUE-ROUNDTRIP-EXACT | resources | Сохранённое значение возвращается так, как введено, кроме документированной нормализации
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
REST-ALIASED-EMBED-FILTER-INDEPENDENCE | pagination | Вложения одного ресурса под разными алиасами фильтруются независимо
REST-API-VERSION-COMPATIBILITY | contract | Совместимость версий API
REST-ASYNC-202 | contract | Асинхронное принятие задачи 202
REST-AUTH-ERROR-NO-LEAK | security | Ошибки аутентификации без утечки
REST-BATCH-PARTIAL-FAILURE | contract | Частичный сбой batch
REST-CACHE-CONDITIONAL-GET | contract | ETag/Last-Modified conditional GET
REST-CONCURRENT-UPDATE | resilience | Конкурентное обновление
REST-CONTENT-TYPE-JSON | contract | Content-Type и JSON-формат
REST-CORRELATION-ID | errors | Correlation ID
REST-CORS-POLICY | security | Политика CORS
REST-CUSTOM-MEDIA-TYPE-EMPTY-RESULT | contract | Пустой результат в пользовательском медиатипе не вызывает внутреннюю ошибку
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
REST-FILTER-NAME-COLLISION | pagination | Фильтр по полю с именем вложенного ресурса применяется к полю
REST-FILTER-OPERATION-PARITY | pagination | Один фильтр даёт согласованный результат в списке, агрегации и вложенной выборке
REST-FILTER-OPERATOR-TYPE-MATRIX | pagination | Каждый оператор фильтра работает для каждого допустимого типа поля и возвращает ровно подходящие записи
REST-FILTER-RELATION-NO-DUPLICATES | pagination | Фильтр по полю связанной коллекции возвращает каждую запись один раз
REST-FILTER-SORT-COMPOSITION | pagination | Filtering and sorting compose correctly
REST-FILTER-SORT-PAGINATION | pagination | Комбинация filter/sort/pagination
REST-FILTER-UNSELECTED-FIELD | pagination | Фильтр по полю, не входящему в выбор полей, работает
REST-HEAD-GET-CONSISTENCY | http-semantics | HEAD response is consistent with GET
REST-IDEMPOTENCY-KEY | contract | Повтор с Idempotency-Key
REST-IDEMPOTENCY-RETRY | idempotency | Retry does not duplicate an idempotent operation's effect
REST-JSON-DUPLICATE-KEYS | validation | Дублирующиеся ключи JSON
REST-MASS-ASSIGNMENT | security | Mass assignment защищённых полей
REST-METHOD-NOT-ALLOWED | http-semantics | Unsupported HTTP method is rejected
REST-NEGOTIATED-FORMAT-CONFORMANCE | contract | Ответ в согласованном формате соответствует спецификации формата
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
SEC-CHECK-ORDER | security | Аутентификация и авторизация проверяются раньше разбора и валидации тела
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
SEC-PRINCIPAL-TYPE-CONFUSION | security | Принципал одного типа не получает прав принципала другого типа с тем же числовым ID
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
UI-ACTIONS-WORK-ONCE | ui | Каждое действие выполняется ровно один раз и меняет ровно своё
UI-AUTH-FLOWS | ui | Интерфейсные потоки входа и восстановления нельзя обойти и перенаправить наружу
UI-CHANGE-HISTORY | ui | История изменений показывает каждое изменение с автором
UI-CLIENT-BASE-PATH-URLS | ui | Клиент под подпутём строит все URL с учётом базового пути
UI-CLIENT-CODE-NO-SECRETS | ui | Клиентский код и страницы не раскрывают секретов и лишних данных
UI-CLIENT-REQUEST-HYGIENE | ui | Клиент не шлёт лишних, дублирующих и бесконечных запросов
UI-CONDITIONAL-FORMATTING | ui | Условное оформление работает для всех операторов сравнения
UI-CONFIRM-DESTRUCTIVE | ui | Удаление и изменение подтверждаются, отмена ничего не меняет
UI-DISABLED-AND-READONLY | ui | Недоступные и доступные только для чтения элементы видны и не выполняют действий
UI-DOCUMENTS-OPEN | ui | Загруженные документы открываются и скачиваются в каждом поддерживаемом формате
UI-DROPDOWN-VALUES | ui | Выпадающие списки показывают полные, разрешённые и упорядоченные значения
UI-ERROR-DISPLAY | ui | Ошибки сервера при сохранении показываются понятным сообщением
UI-FAILURE-ROBUSTNESS | ui | Клиент не падает при сбое и неполных данных
UI-FIELD-LABELS-MATCH-FORM | ui | Подписи и подсказки полей соответствуют назначению формы
UI-FORM-REQUIRED-AND-HINTS | ui | Обязательные поля помечены и проверяются, подсказки объясняют формат
UI-FORM-STATE | ui | Форма сохраняет и сбрасывает состояние ожидаемо
UI-INPUT-VALUES | ui | Поля ввода принимают, показывают и сохраняют значения по своему типу
UI-KEYBOARD-ACCESS | ui | Интерфейс полностью управляется с клавиатуры в логическом порядке
UI-LAYOUT-OVERFLOW | ui | Длинные тексты и раскрывающиеся элементы не выходят за границы и не перекрываются
UI-LEGAL-PAGES | ui | Условия использования и FAQ доступны там, где нужны
UI-LIST-COUNTERS-CONSISTENCY | ui | Счётчики элементов совпадают с фактическим числом записей
UI-LIST-FILTER-STATE | ui | Фильтры снимаются и не переносятся между списками
UI-LIST-FILTER-VALUES | ui | Фильтры принимают и показывают значения своего типа
UI-LIST-SORT | ui | Сортировка списков работает и сохраняется
UI-NAVIGATION | ui | Навигация последовательна: путь на главную, заголовки, рабочие пункты меню
UI-NETWORK-RESILIENCE | ui | Клиент работает при потере сети и без доступа в интернет
UI-NO-BROKEN-RESOURCES | ui | Ссылки, картинки и ресурсы страниц загружаются
UI-PLATFORM-COMPATIBILITY | ui | Интерфейс одинаково работает в поддерживаемых браузерах, ОС и режимах
UI-PLATFORM-SECURITY | ui | Настольный и мобильный клиенты не открывают недоверенный код и экраны входа другим приложениям
UI-RELATED-RECORDS | ui | Связанные записи редактируются во вложенной форме так же, как отдельно
UI-RESPONSIVE-LAYOUT | ui | Интерфейс работает на всех поддерживаемых размерах экрана
UI-RICH-EDITOR | ui | Редактор содержимого сохраняет форматирование и вставки без искажений
UI-SAFE-RENDERING | ui | Данные отображаются экранированными и не роняют интерфейс
UI-SECRET-FIELDS | ui | Поля паролей и секретов не раскрывают и не теряют значение
UI-SESSION-EXPIRY | ui | Истечение и потеря сессии обрабатываются в интерфейсе понятно
UI-STATE-CHANGE-METHODS | ui | Изменения состояния отправляются небезопасными методами, а не GET
UI-TEXTS-CORRECT | ui | Тексты интерфейса без ошибок и на языке интерфейса
UI-USABILITY | ui | Частые сценарии короткие, ожидание и задержки понятны пользователю
UI-VISUAL-CONSISTENCY | ui | Шрифты, отступы и кнопки единообразны по макету и гайдлайнам
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
VAL-OPTIONAL-FIELDS-COMBINATIONS | validation | Любая комбинация и порядок необязательных полей обрабатываются без падения
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
