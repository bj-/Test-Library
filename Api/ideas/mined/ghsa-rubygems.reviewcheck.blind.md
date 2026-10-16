# Перекрёстное ревью новых идей выгрузки багов

Партия `ghsa-rubygems`, идей: 8; вариант пакета — без решений Claude — независимое ревью.
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

## Идея 1. Закрытый ресурс (неопубликованный, приватный, защищённый паролем доступа) недоступен ни через одно альтернативное представление — встраивание (embed), превью, дерево и вложенные списки, ленты, поиск, метаданные; правила доступа и публикации такие же, как у основного маршрута

### GHSA-qcj6-vxwx-4rqv — Decidim vulnerable to data disclosure through the embed feature

Ссылка: https://github.com/advisories/GHSA-qcj6-vxwx-4rqv

- **Паттерн:** Альтернативное представление ресурса (embed, превью) соблюдает правила публикации и доступа
- **Условие:** Ресурс неопубликован или приватен; кроме основного маршрута есть маршрут встраивания …/embed
- **Действие:** Запросить …/embed для неопубликованного и приватного ресурса анонимно и пользователем без доступа
- **Ожидание:** 404/403, как у основного маршрута
- **Источник ожидания:** OWASP API1:2023; здравый смысл
- **Почему не подошла ближайшая запись:** SEC-OWNERSHIP-READ — про чужого владельца, RES-SOFT-DELETE-VISIBILITY — про удалённые; про неопубликованный ресурс через альтернативное представление записи нет

Первоисточник:

````text
### Impact

If an attacker can infer the slug or URL of an unpublished or private resource, and this resource can be embedded (such as a Participatory Process, an Assembly, a Proposal, a Result, etc), then some data of this resource could be accessed. 

### Patches

version 0.27.6

https://github.com/decidim/decidim/commit/1756fa639ef393ca8e8bb16221cab2e2e7875705

### Workarounds

Disallow access through your web server to the URLs finished with `/embed.html`
````

### GHSA-mqq5-j7w8-2hgh — AlchemyCMS: Unauthenticated nested page API leaks restricted & unpublished content

Ссылка: https://github.com/advisories/GHSA-mqq5-j7w8-2hgh

- **Паттерн:** Альтернативное представление коллекции (дерево, вложенный список) соблюдает правила публикации и доступа
- **Условие:** Есть отдельный маршрут дерева страниц рядом с show и index, которые фильтруют по доступу и публикации
- **Действие:** Анонимно запросить GET /api/pages/nested и с ?elements=true; сравнить с show той же закрытой страницы
- **Ожидание:** В дереве нет закрытых и неопубликованных страниц, их содержимое не отдаётся
- **Источник ожидания:** OWASP API1:2023
- **Почему не подошла ближайшая запись:** Тот же механизм, что GHSA-qcj6-vxwx-4rqv: ни одна запись не проверяет неопубликованные и закрытые ресурсы в альтернативном представлении

Первоисточник:

````text
# Unauthenticated nested page API leaks restricted & unpublished content

- **Location:** `app/controllers/alchemy/api/pages_controller.rb:28` (`Api::PagesController#nested`)
- **Affected version:** Alchemy CMS 8.3.0.dev (Rails 8.1.3)

## Description

The unauthenticated `GET /api/pages/nested` endpoint returns the full page tree to any anonymous caller, including restricted (member-only) pages and unpublished/draft pages that should be hidden.
Appending `?elements=true` additionally dumps the element/ingredient **content** of restricted pages, fully bypassing the access control the sibling `show` and `index` actions enforce.

## Root cause

`Api::PagesController#nested` calls no `authorize!` and applies no `published`/`restricted` scoping, unlike `show` (`authorize! :show`) and `index` (`accessible_by(current_ability, :index)`).
`PageTreePreloader` loads `page.self_and_descendants` unfiltered, and `PageTreeSerializer` emits every page's metadata (and, with `elements`, `public_version.elements`) with no ability check.

## Evidence

An unauthenticated `GET /api/pages/nested` returns HTTP 200 with the restricted page (`"restricted":true`) and an unpublished draft (`"public":false`); `?elements=true` leaks its content (e.g. `TOPSECRET_RESTRICTED_BODY_proof123`).
The same guest hitting `GET /api/pages/3` (`show`) gets HTTP **403** `{"error":"Not authorized"}`, proving `nested` returns what `show` correctly denies.

### Reproduction

```bash
# 1) Metadata leak (guest, no auth)
curl -s http://localhost:3000/api/pages/nested | python3 -m json.tool | grep -E '"name"|"restricted"|"public"'

# 2) Content leak of restricted page
curl -s "http://localhost:3000/api/pages/nested?elements=true" | grep -oE 'TOPSECRET_RESTRICTED_BODY_[A-Za-z0-9]+|RESTRICTED_RICHTEXT_[A-Za-z0-9]+'

# 3) Contrast — show denies the same guest
curl -s -o /dev/null -w "show /api/pages/3 -> HTTP %{http_code}\n" http://localhost:3000/api/pages/3
```

### Suggested fix

```ruby
def nested
  @page = Page.find_by(id: params[:page_id]) || Language.current_root_page
  authorize! :show, @page
  preloaded_page = PageTreePreloader.new(page: @page, user: current_alchemy_user, ability: current_ability).call
  render json: PageTreeSerializer.new(preloaded_page, ability: current_ability,
                                      user: current_alchemy_user, elements: params[:elements])
end
```

Additionally scope `PageTreePreloader`'s `self_and_descendants` via `accessible_by(current_ability)` and gate element em …[обрезано]
````

### GHSA-5jm7-g527-m694 — Publify exposes article metadata

Ссылка: https://github.com/advisories/GHSA-5jm7-g527-m694

- **Паттерн:** Содержимое ресурса, защищённого паролем, недоступно без пароля ни через одно представление
- **Условие:** Ресурс (статья) защищён паролем доступа
- **Действие:** Без ввода пароля запросить ресурс через все представления: страницу, метаданные, ленты, поиск, API
- **Ожидание:** Содержимое не возвращается
- **Источник ожидания:** OWASP API1:2023
- **Почему не подошла ближайшая запись:** Записи про владение и роли; защита ресурса паролем доступа без учётки не покрыта, механизм не описан

Первоисточник:

````text
Leaking password protected articles content due to improper access control in GitHub repository publify/publify prior to 9.2.8. Attackers can leverage this vulnerability to view the contents of any password-protected article present on the publify website, compromising confidentiality and integrity of users.
````

## Идея 2. Имена файлов внутри загруженного пользователем содержимого (git-репозиторий, архив, пакет) с переводом строки, кавычками и выражениями кода (#{...}, ${...}, $(...)) при перечислении и обработке остаются текстом и не исполняются; отличие от FILE-FILENAME-SANITIZATION — имена внутри содержимого, а не имя загружаемого файла

### GHSA-pphf-gfrm-v32r — Code injection in ruby git

Ссылка: https://github.com/advisories/GHSA-pphf-gfrm-v32r

- **Паттерн:** Имена файлов в загруженном пользователем репозитории или архиве не исполняются как код
- **Условие:** Сервис обрабатывает загруженный пользователем git-репозиторий и разбирает список файлов
- **Действие:** Загрузить репозиторий с файлом, имя которого содержит \n, кавычки и выражение кода (#{...}); вызвать операцию, перечисляющую файлы
- **Ожидание:** Список файлов корректен, имя отображается как текст, код не исполняется
- **Источник ожидания:** CWE-94; здравый смысл
- **Почему не подошла ближайшая запись:** INJ-UNSAFE-DESERIALIZATION — про формат сериализации, INJ-OS-COMMAND — про оболочку; исполнение имени файла из содержимого репозитория записью не покрыто

Первоисточник:

````text
ruby-git versions prior to v1.13.0 allows a remote authenticated attacker to execute an arbitrary ruby code by having a user to load a repository containing a specially crafted filename to the product. This vulnerability is different from CVE-2022-46648.
````

### GHSA-pfpr-3463-c6jh — ruby-git has potential remote code execution vulnerability

Ссылка: https://github.com/advisories/GHSA-pfpr-3463-c6jh

- **Паттерн:** Имена файлов со спецсимволами в загруженном репозитории не исполняются как код
- **Условие:** Сервис перечисляет файлы загруженного пользователем репозитория
- **Действие:** Загрузить репозиторий с файлом, имя которого содержит перевод строки и выражение кода; запросить список файлов
- **Ожидание:** Имя отображается как текст, код не исполняется
- **Источник ожидания:** CWE-94
- **Почему не подошла ближайшая запись:** Тот же механизм, что GHSA-pphf-gfrm-v32r: подходящей записи нет

Первоисточник:

````text
The git gem, between versions 1.2.0 and 1.12.0, incorrectly parsed the output of the `git ls-files` command using `eval()` to unescape quoted file names. If a file name was added to the git repository contained special characters, such as `\n`, then the `git ls-files` command would print the file name in quotes and escape any special characters. If the `Git#ls_files` method encountered a quoted file name it would use `eval()` to unquote and unescape any special characters, leading to potential remote code execution. Version 1.13.0 of the git gem was released which correctly parses any quoted file names.
````

## Идея 3. Идентификатор протокольной сессии (Mcp-Session-Id, ID потока SSE, ID сессии в пути) привязан к аутентифицированному владельцу — чужой ID с другой учёткой или без неё даёт 403/404, существующий поток владельца не перехватывается и не переключается

### GHSA-5p9g-j988-pcwv — MCP Ruby SDK: Ruby SSE Session Poisoning

Ссылка: https://github.com/advisories/GHSA-5p9g-j988-pcwv

- **Паттерн:** Идентификатор протокольной сессии привязан к аутентифицированному владельцу
- **Условие:** Сервер ведёт сессии по заголовку/пути (Mcp-Session-Id), запросы с ID сессии выполняются в её контексте
- **Действие:** Открыть сессию пользователем A; пользователем B (или без аутентификации) отправить вызов инструмента с ID сессии A
- **Ожидание:** 403/404: ID чужой сессии не принимается
- **Источник ожидания:** OWASP API1:2023; MCP spec (session management)
- **Почему не подошла ближайшая запись:** AUTH-SESSION-FIXATION — про смену ID после входа, SEC-OWNERSHIP-READ — про ресурсы; привязки транспортной сессии к владельцу в библиотеке нет

Первоисточник:

````text
### Summary
**Vulnerability**: Missing Session Ownership Validation in the Ruby MCP SDK's Streamable and SSE HTTP transport implementation. Any attacker with a stolen session ID can execute tools with the victim's session. This is a silent attack - the victim's session is compromised and being used for unauthorized actions, but it is hard to know for the victim

### Details
https://github.com/modelcontextprotocol/ruby-sdk/blob/main/lib/mcp/server/transports/streamable_http_transport.rb#L260-L278

**Victim** starts a legitimate MCP session and receives session ID abc-123
**Attacker** obtains the session ID (various means - network sniffing, logs, etc. out of scope for this analysis)
**Attacker** sends POST to /messages/abc-123 with a tool call
**Server** accepts the request (no ownership validation!)
**Server** executes the tool and sends response to victim's SSE stream
**Victim** receives attacker's response, thinking it's legitimate

### PoC
[attacker_client.py](https://github.com/user-attachments/files/26044817/attacker_client.py)
[legitimate_client.py](https://github.com/user-attachments/files/26044818/legitimate_client.py)

**Prerequisites**

1. Python 3.8+
2. Install dependencies: `requests`

**Running the Demo**

1. **Terminal 1:** Start the Ruby MCP Server

`ruby streamable_http_server.rb`

Makes use of https://github.com/modelcontextprotocol/ruby-sdk/blob/main/examples/streamable_http_server.rb
This server has a tool call notification_tool which the clients call

2. **Terminal 2:**  Start Victim Client

`python3 legitimate_client.py`

3.  **Terminal 3** - Attacker Client:

Copy the session ID from Terminal 1 and run:

```bash
python3 attacker_client.py abc-123-def-456
```
4. **Back to Terminal 2** - Victim sees the injected response:

### Impact

- **Integrity:** HIGH - Attacker can execute unauthorized tools and modify state
- **Availability:** LOW - Attacker can disrupt victim's session with injected responses

### Additional Details
Session Hijacking Protection in MCP Implementations

The MCP specification recommends - "[MCP servers SHOULD bind session IDs to user-specific information](https://modelcontextprotocol.io/docs/tutorials/security/security_best_practices#mitigation-4)".

#### User Binding - Comparison other SDKs
**csharp-sdk**

- https://github.com/modelcontextprotocol/csharp-sdk/blob/main/src/ModelContextProtocol.AspNetCore/SseHandler.cs#L36
- https://github.com/modelcontextprotocol/csharp-sdk/blob/main/src/ModelContextProtocol.AspNet …[обрезано]
````

### GHSA-qvqr-5cv7-wh35 — MCP Ruby SDK: Insufficient Session Binding Allows SSE Stream Hijacking via Session ID Replay

Ссылка: https://github.com/advisories/GHSA-qvqr-5cv7-wh35

- **Паттерн:** Подключение к потоку сессии требует владения сессией и не перехватывает существующий поток
- **Условие:** Сервер отдаёт SSE-поток по ID сессии из заголовка, на сессию хранится один поток
- **Действие:** Пользователем A открыть сессию и SSE-поток; с ID сессии A подключиться GET с другого клиента (другая учётка или без неё)
- **Ожидание:** 403/409; поток владельца не переключается
- **Источник ожидания:** OWASP API1:2023
- **Почему не подошла ближайшая запись:** Тот же механизм, что GHSA-5p9g-j988-pcwv: привязки протокольной сессии к владельцу в библиотеке нет

Первоисточник:

````text
### Summary

The Ruby SDK's [streamable_http_transport.rb](https://github.com/modelcontextprotocol/ruby-sdk/blob/main/lib/mcp/server/transports/streamable_http_transport.rb) implementation contains a session hijacking vulnerability. An attacker who obtains a valid session ID can completely hijack the victim's Server-Sent Events (SSE) stream and intercept all real-time data.

### Details
**Root Cause**
The StreamableHTTPTransport implementation stores only one SSE stream object per session ID and lacks:

- Session-to-user identity binding
- Ownership validation when establishing SSE connections
- Protection against multiple simultaneous connections to the same session

### PoC

#### Vulnerable Code

**File**: streamable_http_transport.rb - [L336-L339](https://github.com/modelcontextprotocol/ruby-sdk/blob/main/lib/mcp/server/transports/streamable_http_transport.rb#L336-L339):

```
def store_stream_for_session(session_id, stream)
  @mutex.synchronize do
    if @sessions[session_id]
      @sessions[session_id][:stream] = stream  # OVERWRITES existing stream
    else
      stream.close
    end
  end
end
```
#### Attack Scenario
**Step 1**: Legitimate Session Establishment
```
POST / (initialize) → receives session_id: "abc123"
GET / with Mcp-Session-Id: abc123 → SSE stream connected
```
Step 2: Session ID Compromise

- An attacker obtains the session ID through various means (out of scope for this analysis)

**Step 3**: Stream Hijacking

```
GET / with Mcp-Session-Id: abc123 
@sessions["abc123"][:stream] = attacker_stream `# Victim's stream is REPLACED (silently disconnected)
```

**Step 4**: Data Interception

- ALL subsequent tool responses/notifications go to the attacker
- The legitimate user receives no data and has no indication of the hijacking

#### Technical Details

The vulnerability happens:

**Client 1 connects (GET request)**

```
proc do |stream1|  # ← Rack server provides stream1 for client 1
 @sessions[session_id][:stream] = stream1  # Stored
end
```

**Client 2 connects with SAME session ID (Attack!)**
```
proc do |stream2|  # ← Rack provides stream2 for client 2
 @sessions[session_id][:stream] = stream2  # REPLACES stream1!
end
```

**Now when the server sends notifications:**

```
@sessions[session_id][:stream].write(data)  # Goes to stream2 (attacker!)
# stream1 (victim) receives nothing
```

**Comparison: Python SDK Protection**

The Python SDK prevents this vulnerability by rejecting duplicate SSE connections:

**Refer**: https://github.co …[обрезано]
````

## Идея 4. Для публичного OAuth-клиента (без секрета) повторный запрос авторизации показывает экран согласия, а не выдаёт код автоматически по прошлому одобрению — иначе любой, кто знает client_id и разрешённый redirect_uri, получает код без участия пользователя (RFC 9700 §4.15)

### GHSA-7w2c-w47h-789w — Doorkeeper Improper Authentication vulnerability

Ссылка: https://github.com/advisories/GHSA-7w2c-w47h-789w

- **Паттерн:** Повторная авторизация публичного OAuth-клиента не выполняется без участия пользователя
- **Условие:** Пользователь ранее одобрил публичного клиента (без секрета); приходит новый запрос авторизации с тем же client_id
- **Действие:** Под пользователем, уже одобрившим публичного клиента, отправить GET /authorize с его client_id и redirect_uri; сравнить с конфиденциальным клиентом
- **Ожидание:** Для публичного клиента показывается экран согласия; для конфиденциального допустим автоматический редирект
- **Источник ожидания:** RFC 8252 §8.6
- **Почему не подошла ближайшая запись:** AUTH-OAUTH-REDIRECT-STATE проверяет redirect_uri, state и PKCE, но не согласие пользователя для публичных клиентов

Первоисточник:

````text
OAuth RFC 8252 says  https://www.rfc-editor.org/rfc/rfc8252#section-8.6

> the authorization server SHOULD NOT process authorization requests automatically without user consent or interaction, except when the identity of the client can be assured. **This includes the case where the user has previously approved an authorization request for a given client id**

But Doorkeeper automatically processes authorization requests without user consent for public clients that have been previously approved. Public clients are inherently vulnerable to impersonation, their identity cannot be assured.

Issue https://github.com/doorkeeper-gem/doorkeeper/issues/1589

Fix https://github.com/doorkeeper-gem/doorkeeper/pull/1646
````

## Идея 5. Правило по префиксу пути (статика /css, /js, исключения из аутентификации, маршрутизация прокси) соблюдает границу сегмента — /css-config.env, /cssbackup.sql, /js.env не попадают под правило /css/, /js/

### GHSA-h2jq-g4cq-5ppq — Rack::Static prefix matching can expose unintended files under the static root

Ссылка: https://github.com/advisories/GHSA-h2jq-g4cq-5ppq

- **Паттерн:** Префикс статического маршрута соблюдает границу сегмента пути
- **Условие:** Сервер отдаёт статические файлы для префиксов вроде /css, /js
- **Действие:** Запросить /css-config.env, /cssbackup.sql, /js.env рядом с разрешёнными /css/…
- **Ожидание:** 404
- **Источник ожидания:** Здравый смысл; OWASP API8:2023
- **Почему не подошла ближайшая запись:** HTTP-TRAILING-SLASH-CASE — про единообразие вариаций пути, INJ-PATH-TRAVERSAL — про выход из каталога; совпадение префикса без границы сегмента не покрыто

Первоисточник:

````text
## Summary

`Rack::Static` determines whether a request should be served as a static file using a simple string prefix check. When configured with URL prefixes such as `"/css"`, it matches any request path that begins with that string, including unrelated paths such as `"/css-config.env"` or `"/css-backup.sql"`.

As a result, files under the static root whose names merely share the configured prefix may be served unintentionally, leading to information disclosure.

## Details

`Rack::Static#route_file` performs static-route matching using logic equivalent to:

```ruby
@urls.any? { |url| path.index(url) == 0 }
```

This checks only whether the request path starts with the configured prefix string. It does not require a path segment boundary after the prefix.

For example, with:

```ruby
use Rack::Static, urls: ["/css", "/js"], root: "public"
```

the following path is matched as intended:

```text
/css/style.css
```

but these paths are also matched:

```text
/css-config.env
/css-backup.sql
/csssecrets.yml
```

If such files exist under the configured static root, Rack forwards the request to the file server and serves them as static content.

This means a configuration intended to expose only directory trees such as `/css/...` and `/js/...` may also expose sibling files whose names begin with those same strings.

## Impact

An attacker can request files under the configured static root whose names share a configured URL prefix and obtain their contents.

In affected deployments, this may expose configuration files, secrets, backups, environment files, or other unintended static content located under the same root directory.

## Mitigation

* Update to a patched version of Rack that enforces a path boundary when matching configured static URL prefixes.
* Match only paths that are either exactly equal to the configured prefix or begin with `prefix + "/"`.
* Avoid placing sensitive files under the `Rack::Static` root directory.
* Prefer static URL mappings that cannot overlap with sensitive filenames.
````

## Идея 6. Служебные заголовки отдачи файлов прокси (X-Sendfile-Type, X-Accel-Mapping, X-Accel-Redirect, X-Sendfile), присланные клиентом, игнорируются — ответ и доступ к путям такие же, как без них

### GHSA-r657-rxjc-j557 — Rack has a Possible Information Disclosure Vulnerability

Ссылка: https://github.com/advisories/GHSA-r657-rxjc-j557

- **Паттерн:** Служебные заголовки ускорения отдачи (X-Sendfile-Type, X-Accel-Mapping) от клиента не влияют на ответ
- **Условие:** Приложение отдаёт файлы через X-Sendfile/X-Accel-Redirect за прокси, прокси не перезаписывает эти заголовки
- **Действие:** Запросить путь, отдаваемый через sendfile, с заголовками x-sendfile-type: x-accel-redirect и подобранным x-accel-mapping; проверить ответ и доступ к закрытым путям
- **Ожидание:** Клиентские служебные заголовки игнорируются, ответ как без них
- **Источник ожидания:** OWASP API8:2023
- **Почему не подошла ближайшая запись:** HARD-CLIENT-IP-TRUSTED-PROXIES — про IP клиента, HARD-HOST-HEADER — про Host; записи про служебные заголовки отдачи файлов нет

Первоисточник:

````text
## Summary

A possible information disclosure vulnerability existed in `Rack::Sendfile` when running behind a proxy that supports `x-sendfile` headers (such as Nginx). Specially crafted headers could cause `Rack::Sendfile` to miscommunicate with the proxy and trigger unintended internal requests, potentially bypassing proxy-level access restrictions.

## Details

When `Rack::Sendfile` received untrusted `x-sendfile-type` or `x-accel-mapping` headers from a client, it would interpret them as proxy configuration directives. This could cause the middleware to send a "redirect" response to the proxy, prompting it to reissue a new internal request that was **not subject to the proxy's access controls**.

An attacker could exploit this by:
1. Setting a crafted `x-sendfile-type: x-accel-redirect` header.
2. Setting a crafted `x-accel-mapping` header.
3. Requesting a path that qualifies for proxy-based acceleration.

## Impact

Attackers could bypass proxy-enforced restrictions and access internal endpoints intended to be protected (such as administrative pages). The vulnerability did not allow arbitrary file reads but could expose sensitive application routes.

This issue only affected systems meeting all of the following conditions:

* The application used `Rack::Sendfile` with a proxy that supports `x-accel-redirect` (e.g., Nginx).
* The proxy did **not** always set or remove the `x-sendfile-type` and `x-accel-mapping` headers.
* The application exposed an endpoint that returned a body responding to `.to_path`.

## Mitigation

* Upgrade to a fixed version of Rack which requires explicit configuration to enable `x-accel-redirect`:

  ```ruby
  use Rack::Sendfile, "x-accel-redirect"
  ```

* Alternatively, configure the proxy to always set or strip the headers (you should be doing this!):

  ```nginx
  proxy_set_header x-sendfile-type x-accel-redirect;
  proxy_set_header x-accel-mapping /var/www/=/files/;
  ```

* Or in Rails applications, disable sendfile completely:

  ```ruby
  config.action_dispatch.x_sendfile_header = nil
  ```
````

## Идея 7. Параметры запроса (фильтр, поиск, сообщения об ошибке) не отражаются в HTML-ответе без экранирования по контексту; Content-Type соответствует содержимому; пара к INJ-STORED-XSS

### GHSA-cmh9-rx85-xj38 — XSS sidekiq-unique-jobs UI server vulnerability

Ссылка: https://github.com/advisories/GHSA-cmh9-rx85-xj38

- **Паттерн:** Параметры запроса не отражаются в HTML-ответе без экранирования
- **Условие:** Эндпоинт возвращает HTML и вставляет в него значения query-параметров (фильтр, поиск)
- **Действие:** Запросить страницы списков с параметрами, содержащими <script> и закрывающие кавычки/теги; проверить тело ответа
- **Ожидание:** Значения экранированы по контексту, Content-Type соответствует содержимому
- **Источник ожидания:** OWASP, CWE-79
- **Почему не подошла ближайшая запись:** INJ-STORED-XSS — про сохранённые данные; записи про отражение параметров в ответе нет

Первоисточник:

````text
### Summary

Cross site scripting (XSS) potentially exposing cookies / sessions / localStorage, fixed by `sidekiq-unique-jobs` v8.0.7.

Specifically, this is a Reflected (Server-Side), Non-Self, Cross Site Scripting vulnerability, considered a **_P3_** on the BugCrowd [taxonomy](https://bugcrowd.com/vulnerability-rating-taxonomy) with the following categorization:
Cross-Site Scripting (XSS) > Reflected > Non-Self

It was initially thought there was a second vulnerability (RCE), but it was a false alarm.  Injection is impossible with Redis:

> String escaping and NoSQL injection
> The Redis protocol has no concept of string escaping, so injection is impossible under normal circumstances using a normal client library. The protocol uses prefixed-length strings and is completely binary safe.

Ref: https://redis.io/docs/management/security/

**XSS Vulnerability**

Specially crafted `GET` request parameters handled by any of the following endpoints of `sidekiq-unique-jobs`' "admin" web UI, allow a super-user attacker, or an unwitting, but authorized, victim, who has received a disguised / crafted link, to successfully execute malicious code, which could potentially steal cookies, session data, or local storage data from the app the `sidekiq-unique-jobs` web UI is mounted in.

1. `/changelogs`
2. `/locks`
3. `/expiring_locks`

This means if your `sidekiq-unique-jobs` web UI is mounted at `/sidekiq`, the vulnerable paths are:

1. `/sidekiq/changelogs`
2. `/sidekiq/locks`
3. `/sidekiq/expiring_locks`

XSS vulnerability is an instance of [CAPEC-32: XSS Through HTTP Query Strings](https://capec.mitre.org/data/definitions/32.html), which is related to [CWE-80](https://cwe.mitre.org/data/definitions/80.html). In certain cases where it results in a server error with status 500, it could be considered a vector for uncontrolled resource consumption, given that errors can be much more resource intensive that normal requests, and thus [CWE-400](https://cwe.mitre.org/data/definitions/400.html) & [CWE-754](https://cwe.mitre.org/data/definitions/754.html) may also be relevant.

### Details

Fix for the XSS vulnerability was released in `sidekiq-unique-jobs` [v8.0.7](https://github.com/mhenrixon/sidekiq-unique-jobs/releases/tag/v8.0.7).

This is an analogous attack vector to that which affected `sidekiq` gem from version v7.0.4 to v7.0.7, and was given identifiers [GHSA-h3r8-h5qw-4r35](https://github.com/advisories/GHSA-h3r8-h5qw-4r35) & [CVE-2023-1892](https://github.com/advis …[обрезано]
````

## Идея 8. Учётные данные из URL источника импорта или зеркалирования (https://user:token@host/...) после завершения импорта не сохраняются и не возвращаются в параметрах объекта (адрес источника, настройки зеркала, журнал задачи)

### GHSA-mmmm-chjf-jmvw — Gitaly Insufficient Session Expiration vulnerability

Ссылка: https://github.com/advisories/GHSA-mmmm-chjf-jmvw

- **Паттерн:** Учётные данные из URL импорта не сохраняются после завершения импорта
- **Условие:** Импорт репозитория/данных по URL с учётными данными (https://user:token@host/...)
- **Действие:** Импортировать по URL с учётными данными, дождаться завершения и прочитать через API параметры импортированного объекта (адрес источника, настройки зеркала)
- **Ожидание:** Учётные данные не сохранены и не возвращаются
- **Источник ожидания:** OWASP API3:2023, практика
- **Почему не подошла ближайшая запись:** HARD-SENSITIVE-DATA-IN-URL про передачу в URL, AUTH-TOKEN-IN-URL про приём токена; хранения после импорта нет

Первоисточник:

````text
When importing repos via URL, one time use git credentials were persisted beyond the expected time window in Gitaly 1.79.0 or above. Affected versions are: >=1.79.0, <13.3.9,>=13.4, <13.4.5,>=13.5, <13.5.2.
````

## Индекс библиотеки

Все записи (456): ID | категория | заголовок.

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
HTTP-REQUEST-SMUGGLING | http-semantics | Противоречивые Content-Length и Transfer-Encoding не приводят к request smuggling
HTTP-TRAILING-SLASH-CASE | http-semantics | Вариации пути (слэш в конце, регистр, двойной слэш) обрабатываются единообразно
HTTP-UNKNOWN-ROUTE | http-semantics | Неизвестный маршрут возвращает 404, а не 5xx или 200
HTTP-URL-LENGTH-LIMIT | http-semantics | Очень длинный URL отклоняется контролируемо
HTTP-VARY-HEADER | http-semantics | Кэшируемые ответы содержат корректный Vary
HTTP-VERSION-PARITY | http-semantics | Запросы по HTTP/2 и с предложением Upgrade h2c обслуживаются так же, как по HTTP/1.1
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
