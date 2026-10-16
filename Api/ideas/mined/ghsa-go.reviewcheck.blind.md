# Перекрёстное ревью новых идей выгрузки багов

Партия `ghsa-go`, идей: 10; вариант пакета — без решений Claude — независимое ревью.
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

## Идея 1. Значения из запроса (метод, путь, заголовки, коды) не создают неограниченно новых серий метрик — неизвестные значения сводятся в одну серию (other), шаблоны пути — в маршрут; размер /metrics и память не растут

### GHSA-6r69-c6wg-7g8m — yopass Prometheus metrics middleware allows remote memory exhaustion through unbounded method labels

Ссылка: https://github.com/advisories/GHSA-6r69-c6wg-7g8m

- **Паттерн:** Произвольные значения из запроса не создают неограниченно новые серии метрик
- **Условие:** Метрики помечаются значением метода (или другого поля) запроса как есть
- **Действие:** Отправить запросы с уникальными нестандартными методами (M1, M2, …) и сравнить /metrics до и после
- **Ожидание:** Неизвестные значения сводятся в одну серию (other), размер /metrics не растёт
- **Источник ожидания:** OWASP API4:2023; практика Prometheus по кардинальности меток
- **Почему не подошла ближайшая запись:** HARD-EXPENSIVE-OPERATION-LIMITS и OBS-HEALTH-ENDPOINTS не проверяют кардинальность меток метрик

Первоисточник:

````text
The Prometheus metrics middleware in pkg/server/server.go used r.Method directly as a label value on request counter and duration histogram metrics. Since the mux catch-all route matches any HTTP method, an unauthenticated attacker can send requests with arbitrary method strings (e.g. curl -X "M1" http://host/), each creating new counter and histogram time series in the Prometheus registry. The registry's internal maps never evict entries.

An attacker issuing requests with unique method values causes monotonic memory growth until the process is OOM-killed. Additionally, /metrics scrape latency degrades proportionally, eventually timing out and blinding monitoring.

Remediation: Upgrade to 14.7.0 or later, which clamps the method label to a fixed allowlist (GET, POST, PUT, DELETE, OPTIONS, HEAD, CONNECT, TRACE) and maps everything else to other.
````

## Идея 2. Данные, которые пользователь задаёт сам (имя, атрибуты, метаданные сущности) и которые подставляются в шаблон политики доступа (<username>/*, *.{name}.example.com), не работают как wildcard и метасимволы — экранируются или отклоняются при создании

### GHSA-59w7-v8rr-pr4p —  OpenBao's Templated Policies Allow Privilege Escalation via Wildcard Characters

Ссылка: https://github.com/advisories/GHSA-59w7-v8rr-pr4p

- **Паттерн:** Пользовательские данные, подставляемые в шаблон политики доступа, не работают как wildcard
- **Условие:** Политика шаблонная (доступ к <username>/*); пользователь сам выбирает имя и может использовать *, +, /
- **Действие:** Создать пользователя или сущность с именем «*» и запросить данные других пользователей или сертификат на *.example.com
- **Ожидание:** Отказ: спецсимволы в подставленных данных экранируются или имя отклоняется
- **Источник ожидания:** OWASP API5:2023
- **Почему не подошла ближайшая запись:** INJ-FILTER-EXPRESSION — про выражения фильтров в запросе, а не про подстановку атрибутов пользователя в шаблоны политик

Первоисточник:

````text
## Impact

### ACL Policies

OpenBao supports "templated polices": Policies with placeholders that are replaced at evaluation time.

This allows you to write a single policy which e.g. grants user "alice" access to all entries in a key value engine prefixed with `alice/` while granting "bob" access to `bob/`, "carol" access to `carol/`, etc.

If the data used in the template can be controlled by an attacker (e.g. your system allows the user to freely select their username) and "globbing" characters are considered valid ( e.g. `*` is a valid username) they will be able to escalate their privileges.

The problematic characters are `*`, `+` and `/`.

### PKI Secrets Engine `allowed_uri_sans_template` and `allowed_domains` Polices

The PKI secrets engine allows you to limit the "common names" a user can requests a TLS certificate for. Similar to the ACL polices this allows you to restrict e.g. "alice" to  `alice.example.com`, "bob" to  `bob.example.com`, etc. via templates.

Again, if an attacker can control this data freely, they can trick the PKI engine into using e.g. the `*.example.com` glob effectively allowing them to issue certificates for any subdomain of `example.com`

The problematic character in this case is `*`.

### SSH Secrets Engine `allowed_users` and `allowed_domains` Polices

The SSH secrets engine allows you to limit the "principal" a user can request as SSH certificate for. Similar to ACL and PKI, this allows templates.

The problematic character in this case is `,` as the template result is split at all commas and each entry will be allowed.

## Am I affected?

You are affected, if a) you use a templated policy (ACL, PKI or SSH) and b) your users can modify data used by your template freely.

If you can guarantee that the data used in your templates will never contain the problematic characters, you are not affected. For example, if you use `{{ identity.entity.id }}` in your policy, you are not affected, because `identity.entity.id` is randomly generated by OpenBao.

Even with this vulnerability patched: Using user controllable data in your policies is probably not the best idea.

## Patches

All three have been patched in OpenBao v2.6.0.
````

## Идея 3. Каждый элемент списка запрещённых значений (ключи меток и аннотаций, имена полей, домены, команды) отклоняется — проверка перебором всех элементов списка, в том числе в разном регистре и при любом составе и порядке списка

### GHSA-gjw4-3v3v-rqxg — Capsule: Tenant owner bypasses Capsule's forbidden namespace/service/node label and annotation enforcement

Ссылка: https://github.com/advisories/GHSA-gjw4-3v3v-rqxg

- **Паттерн:** Каждый ключ из списка запрещённых отклоняется при любом составе списка
- **Условие:** Список запрещённых меток/аннотаций содержит ключи в разном регистре
- **Действие:** Поочерёдно установить на свои ресурсы каждый ключ из списка запрещённых
- **Ожидание:** Каждый запрещённый ключ отклоняется (403/422)
- **Источник ожидания:** Документация продукта; OWASP API5:2023
- **Почему не подошла ближайшая запись:** VAL-CASE-SENSITIVITY — про регистр входного значения; здесь ломается поиск в самом списке запретов, проверка — перебор всех элементов списка

Первоисточник:

````text
## Summary

Capsule lets a cluster administrator forbid specific metadata keys that tenant owners must not place on their own resources: `Tenant.spec.namespaceOptions.forbiddenLabels` / `forbiddenAnnotations` (namespaces), `Tenant.spec.serviceOptions.forbiddenLabels` / `forbiddenAnnotations` (Services), and the cluster-wide forbidden worker-node labels/annotations. These lists are an isolation control — they exist to stop a tenant owner from setting metadata that other controllers or admission plugins key on (Pod Security Admission labels, `kubernetes.io/metadata.name`, LoadBalancer/externalIP service annotations, scheduler annotations, vendor labels that grant network reach, etc.). The validating webhooks enforce them through `api.ValidateForbidden`, which calls `ForbiddenListSpec.ExactMatch(key)` for every key the tenant submits.

`ExactMatch` is broken. It sorts the denied list **case-insensitively** (`sort.SliceStable` with a `strings.ToLower` comparator) and then performs a **byte-order binary search** (`sort.SearchStrings`) over the result. `sort.SearchStrings` is only correct on a slice sorted in plain byte-ascending order. Whenever the denied list contains an entry whose case-insensitive position differs from its byte position — which happens any time the list mixes a capitalised key with lowercase keys, because ASCII uppercase letters (0x41–0x5A) sort *before* lowercase (0x61–0x7A) by byte but are interleaved by `ToLower` — the binary search lands on the wrong index and `ExactMatch` returns **false for a key that is literally present in the denied list**. The webhook then *allows* the forbidden metadata.

A tenant owner (who legitimately holds patch/create rights on their own tenant-owned namespaces and Services) can therefore set a metadata key the administrator explicitly forbade, defeating the control and reaching metadata-driven cross-tenant / system effects of exactly the kind Capsule's forbidden lists are meant to prevent. The bug is deterministic, requires no race, and is present unchanged on `main` HEAD.

## Affected code (v0.13.5)

`pkg/api/forbidden_list.go` — the comparison primitive:

```go
func (in ForbiddenListSpec) ExactMatch(value string) (ok bool) {
	if len(in.Exact) > 0 {
		sort.SliceStable(in.Exact, func(i, j int) bool {
			return strings.ToLower(in.Exact[i]) < strings.ToLower(in.Exact[j]) // case-INSENSITIVE order
		})

		i := sort.SearchStrings(in.Exact, value) // binary search assuming BYTE order

		ok = i < len(in.Exact) &&  …[обрезано]
````

## Идея 4. Запись файлов пользователем через API (патч, загрузка в репозиторий, распаковка, синхронизация) не попадает в служебные каталоги и файлы с особым смыслом (.git/, hooks/, конфигурация, .htaccess) даже по законному относительному пути — без ../; служебный файл не исполняется

### GHSA-rcr6-4jqh-j84m — Gitea: Remote Code Execution via diffpatch Git Hook Installation

Ссылка: https://github.com/advisories/GHSA-rcr6-4jqh-j84m

- **Паттерн:** Применение патча через API не записывает файлы в служебный каталог репозитория
- **Условие:** Пользователь с правом записи в свой репозиторий отправляет патч в эндпоинт diffpatch
- **Действие:** Дважды отправить патч, добавляющий исполняемый файл hooks/post-index-change
- **Ожидание:** Файл попадает только в дерево репозитория, хук не исполняется
- **Источник ожидания:** OWASP API8:2023
- **Почему не подошла ближайшая запись:** INJ-PATH-TRAVERSAL — про выход за каталог через ../; здесь путь законный, но совпадает со служебным каталогом git

Первоисточник:

````text
### Summary

Gitea's `diffpatch` endpoint can be abused to install and execute a Git hook from repository-controlled content.

An attacker with ordinary write access to a repository can execute arbitrary shell commands as the Gitea OS user. With default open registration, an unauthenticated visitor can obtain the required write access by registering an account and creating a repository.

### Details

`services/repository/files/patch.go` applies attacker-controlled patches in a shared bare temporary clone:

```go
cmdApply := gitcmd.NewCommand("apply", "--index", "--recount", "--cached", "--binary")
if git.DefaultFeatures().CheckVersionAtLeast("2.32") {
    cmdApply.AddArguments("-3")
}
````

Submitting the same patch twice creates an add/add collision. Git's three-way fallback checks the indexed path out even though the operation is performed with `--cached`.

In a bare clone, the repository root is `$GIT_DIR`. As a result, an executable entry named:

```text
hooks/post-index-change
```

becomes a live Git hook.

Git invokes the hook while writing the index, allowing repository-controlled content to execute arbitrary commands as the Gitea service account.

The hook's return value is not propagated to the `diffpatch` response.

The attached PoC stores command output in Git objects and creates a branch containing the result, so no outbound connection is required. The result is fetched through authenticated smart HTTP.

### PoC

The supplied `gitea_diffpatch_rce_poc.py` uses an existing Gitea account. Run it against a test instance where the account can create a repository.

Set the account password:

```bash
export GITEA_PASSWORD='account-password'
```

Execute a command through the `diffpatch` chain:

```bash
python3 ./gitea_diffpatch_rce_poc.py \
  https://gitea.example \
  pocuser \
  'id; uname -srm; pwd'
```

The script:

* Creates an initialized private repository.
* Submits the same executable-hook patch twice.
* Fetches the result branch.
* Prints the command's combined stdout, stderr, and exit status.
* Prints the evidence repository, ref, and commit IDs to stderr.

Expected output resembles:

```text
uid=1000(git) gid=1000(git) groups=1000(git)
Linux ...
/data/gitea/tmp/...

[exit-status=0]
```

The trigger requires:

* Git 2.32 or newer.
* An enabled `diffpatch` route.
* A writable and executable temporary filesystem.

Open registration is required only for the no-prior-credentials attack path.

### Impact

This is remote command execution as the G …[обрезано]
````

## Идея 5. В шлюзе или прокси несколько маршрутов (в том числе разных арендаторов и пространств имён) к одному бэкенду применяют каждый свои фильтры и заголовки (идентичность арендатора) — конфигурация маршрутов не смешивается

### GHSA-6p8f-p8j2-rqmv — Traefik: Gateway HTTPRoute backendRef filters can leak backend context across routes sharing a Service:port

Ссылка: https://github.com/advisories/GHSA-6p8f-p8j2-rqmv

- **Паттерн:** Маршруты к одному бэкенду с разными фильтрами применяют каждый свои фильтры
- **Условие:** Два маршрута (в т.ч. из разных пространств имён) ведут на один Service:port с разными фильтрами заголовков (идентичность арендатора)
- **Действие:** Создать второй маршрут со своим фильтром к тому же бэкенду и отправить запросы по обоим маршрутам, сравнив заголовки на бэкенде
- **Ожидание:** Каждый маршрут передаёт свои заголовки
- **Источник ожидания:** Kubernetes Gateway API (backendRef filters); OWASP API5:2023
- **Почему не подошла ближайшая запись:** RES-CACHE-KEY-COMPLETENESS — про кэш ответов; здесь неполный ключ конфигурации маршрута смешивает контекст

Первоисточник:

````text
## Summary

There is a medium severity vulnerability in Traefik's Kubernetes Gateway API provider.
When two accepted HTTPRoutes target the same backend Service:port but configure different
`backendRef` filters, Traefik may resolve both routes to the same child service and apply
only one route's filter set to all requests reaching that backend. In Gateway deployments
where `backendRef` filters set security-sensitive headers — such as tenant identity,
authorization context, or values the backend trusts — an attacker who can create an
accepted HTTPRoute sharing the same backend Service:port may cause their route's filter
context to be applied to another route's requests, potentially crossing namespace
boundaries when a `ReferenceGrant` permits cross-namespace targeting.

## Patches

- https://github.com/traefik/traefik/releases/tag/v3.7.6

## For more information

If you have any questions or comments about this advisory, please [open an issue](https://github.com/traefik/traefik/issues).

<details>
<summary>Original Description</summary>

# Traefik Gateway HTTPRoute backendRef filter context collision across routes sharing Service:port

## Summary

Traefik's Kubernetes Gateway API provider builds the dynamic HTTP backend service key for a Gateway `HTTPRoute` backendRef from only the backend namespace, Service name, protocol, and port. It does not include the HTTPRoute, listener, rule, or backendRef filter identity in that key.

When two accepted HTTPRoutes point to the same backend `Service:port` but define different backendRef filters, Traefik can make both route WRR services reference the same child service. The child service then carries only one backendRef filter set, so one route can send requests to the backend with another route's backend context.

This is security-relevant when backendRef filters set, remove, or rewrite security-sensitive context, such as tenant, identity, auth, sanitization, Host, or path headers trusted by the backend.

Credit: Qican Ma, Ding Luo @XiaoMi ShadowBlade Security Lab

## Suggested Severity

Suggested severity: Medium/High, configuration-dependent.

Suggested CVSS 3.1:

```text
CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:L/I:H/A:N
```

Notes:

- Requires Gateway API routes sharing the same backend Service:port with different security-sensitive backendRef filters trusted by the backend.
- Cross-namespace impact is possible when route attachment and ReferenceGrant policy allow an attacker route to target the shared backend.
- No RCE …[обрезано]
````

## Идея 6. В иерархии объектов (проект → подпроект, папка → файл) явное право на дочерний объект — в том числе пониженное — имеет приоритет над унаследованным от родителя, по документированному правилу ближайшего назначения

### GHSA-pjr3-86v4-5p7w — Vikunja: Explicit lower-permission share on a sub-project is silently overridden by an inherited parent permission (broken access control / privilege-management regression in v2.6.0)

Ссылка: https://github.com/advisories/GHSA-pjr3-86v4-5p7w

- **Паттерн:** Явное пониженное право на дочерний объект имеет приоритет над унаследованным от родителя
- **Условие:** Пользователь имеет право записи на родительский проект, а на дочерний ему явно выдано только чтение
- **Действие:** Этим пользователем изменить, удалить и расшарить дочерний проект
- **Ожидание:** 403: действует явное право на дочерний объект (ближайшее назначение)
- **Источник ожидания:** Поведение прошлой версии продукта; здравый смысл
- **Почему не подошла ближайшая запись:** Записи о приоритете явного и наследуемого права в иерархии нет; SEC-ROLE-LOW-TO-HIGH — про роль и привилегированное действие, не про наследование

Первоисточник:

````text
## Description

### Summary

In Vikunja v2.6.0 the project-permission engine resolves a user's effective permission on a project as
the **MAX over the entire reachable project subtree**. As a result, when a user has been granted a
**higher** permission on a parent project and the owner *explicitly* shares a **child** project with
that same user at a **lower** permission (an intended down-restriction), the explicit lower grant is
**silently ignored** and the user receives the higher, inherited permission on the child. A user
who was deliberately restricted to **read-only** on a sensitive sub-project can therefore modify it,
delete it, and re-share it (including granting other users admin) - none of which the owner intended.
This is a behavior regression from v2.5.0, whose engine used "nearest-ancestor-grant-wins" semantics
that honored the explicit child grant.

### Details

Effective permissions are computed by a single recursive CTE in
`pkg/models/project_access.go` (`getProjectAccessForUser`):

```sql
WITH RECURSIVE grants (project_id, permission) AS (
    SELECT project_id, MAX(permission) FROM (
        SELECT id AS project_id, 2 AS permission FROM projects WHERE owner_id = ?
        UNION ALL SELECT project_id, permission FROM users_projects WHERE user_id = ?
        UNION ALL SELECT tp.project_id, tp.permission FROM team_projects tp
                  INNER JOIN team_members tm ON tm.team_id = tp.team_id WHERE tm.user_id = ?
    ) direct_grants GROUP BY project_id
),
tree (id, permission) AS (
    SELECT p.id, g.permission FROM projects p INNER JOIN grants g ON g.project_id = p.id
    UNION
    SELECT p.id, t.permission FROM projects p INNER JOIN tree t ON p.parent_project_id = t.id
)
SELECT id, MAX(permission) AS permission FROM tree GROUP BY id
```

For a parent `P` where the user has a direct ADMIN(2) grant and a child `C` (with
`parent_project_id = P`) where the user has a direct READ(0) grant, the `tree` CTE produces the rows
`(P,2)`, `(C,0)` (direct grants) **and** `(C,2)` (the parent grant propagated down the recursion). The
final `SELECT id, MAX(permission) ... GROUP BY id` collapses the child to `MAX(0, 2) = 2 (ADMIN)`. The
explicit READ grant on `C` is discarded.

In v2.5.0 the equivalent resolution used `ROW_NUMBER() OVER (... ORDER BY priority)` (nearest-ancestor
wins), so the child's own direct grant took precedence and the down-restriction was honored. The switch
to `MAX(...)` in v2.6.0 introduces the override. Code comments in `project_ …[обрезано]
````

## Идея 7. Восстановление из резервной копии через API не обходит защиту записи — доступно только администратору, подлинность копии проверяется ключом сервера (а не ключом из запроса), защищённые настройки (команды, секреты, роли) подделанной копией не перезаписываются

### GHSA-p393-cf76-4jmr — Nginx UI: Authenticated Remote Code Execution via Backup Restore App Config Overwrite

Ссылка: https://github.com/advisories/GHSA-p393-cf76-4jmr

- **Паттерн:** Восстановление из резервной копии не меняет защищённые настройки и не принимает копию с ключом от клиента
- **Условие:** Эндпоинт восстановления доступен обычному пользователю и принимает ключ шифрования вместе с копией
- **Действие:** Загрузить подделанную копию с изменёнными защищёнными настройками (команды, секреты) и своим ключом, затем вызвать операцию, использующую эти настройки
- **Ожидание:** Отказ: восстановление только для администратора, подлинность копии проверяется ключом сервера, защищённые настройки не перезаписываются
- **Источник ожидания:** OWASP API5:2023; согласованность с API настроек
- **Почему не подошла ближайшая запись:** REST-MASS-ASSIGNMENT — про поля тела запроса; INJ-OS-COMMAND — про ввод в команду; записи о восстановлении копии как обходном канале записи нет

Первоисточник:

````text
## Summary

An authenticated nginx-ui user can call `POST /api/restore`, upload a forged encrypted backup, restore `app.ini`, set nginx command settings such as `TestConfigCmd`, and then trigger command execution with `POST /api/nginx/test`.

This was validated on nginx-ui `2.3.11 2(523) 6c86e5a5` in the local Docker container `uozi/nginx-ui:latest`.

## Impact

An authenticated user can overwrite nginx-ui application configuration and database state through restore, including protected settings that are normally not writable through the settings API. By setting nginx command fields in the restored `app.ini`, the attacker can execute commands in the nginx-ui runtime context. This affects confidentiality, integrity, and availability because the attacker can read or replace secrets, change node/JWT secrets, corrupt application state, and execute arbitrary commands.

## Affected Version / Environment

- Version: `nginx-ui 2.3.11 2(523) 6c86e5a5`
- Deployment: local Docker, `uozi/nginx-ui:latest`
- Base URL used in validation: `http://127.0.0.1:8080`

## Root Cause

`/api/restore` is reachable through normal authenticated-user authorization. The restore handler accepts attacker-supplied backup key material, validates the manifest with a key derived from that supplied AES key, decrypts attacker-controlled backup contents, and copies restored `app.ini` into the live nginx-ui config path.

Relevant code paths:

- `api/backup/router.go`: `POST /api/restore`
- `api/backup/restore.go`: accepts `security_token` and uploaded backup file
- `internal/backup/manifest.go`: derives backup signing key from supplied AES key
- `internal/backup/restore.go`: `restoreNginxUIConfig` overwrites live `app.ini`
- `internal/nginx/exec.go`: nginx command settings execute through shell-backed command paths

## Proof of Concept

Assumptions:

- nginx-ui is already running.
- `$TOKEN` is a valid user JWT.
- `$CONTAINER` is the local disposable Docker container name for cleanup and evidence checks.

```bash
export BASE='http://127.0.0.1:8080'
export TOKEN='<valid nginx-ui JWT>'
export CONTAINER='nginx-ui'
```

Run only against a disposable local instance.

```bash
set -eu

TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

docker cp "$CONTAINER":/etc/nginx-ui/app.ini "$TMP/app.ini.original"

curl -sS -D "$TMP/backup.headers" -o "$TMP/backup.zip" \
  -H "Authorization: $TOKEN" \
  "$BASE/api/backup"

SEC=$(awk 'BEGIN{IGNORECASE=1} /^X-Backup-Security:/{gsub("\r",""); print $2}' "$TMP/backup.heade …[обрезано]
````

## Идея 8. Пользовательские скрипты, которые сервер штатно исполняет (потоки, правила, хуки, формулы), изолированы — загрузка модулей и чтение файлов хоста, сеть и переменные окружения недоступны, содержимое файлов не попадает в результат

### GHSA-fgmf-7rf8-m6vf — ZITADEL: Actions V1 sandbox escape: host file read via require()

Ссылка: https://github.com/advisories/GHSA-fgmf-7rf8-m6vf

- **Паттерн:** Пользовательские скрипты, исполняемые сервером, изолированы от файловой системы хоста
- **Условие:** Администратор арендатора может загружать скрипты, которые сервер выполняет в своём процессе
- **Действие:** Сохранить скрипт, пытающийся загрузить файл хоста как модуль, и запустить поток, где он вызывается
- **Ожидание:** Загрузка модуля из файловой системы запрещена, содержимое файлов не попадает в результат
- **Источник ожидания:** Документация изоляции арендаторов; здравый смысл
- **Почему не подошла ближайшая запись:** INJ-TEMPLATE-SSTI — про внедрение в шаблон; записи об изоляции штатных пользовательских скриптов нет

Первоисточник:

````text
### Summary

A vulnerability in ZITADEL Actions V1 allows an organization Action author to read files from the ZITADEL host filesystem through the JavaScript `require()` module loader. On common self-hosted deployments this can be chained to steal bootstrap credentials (including the Login Client PAT) and escalate from a single-tenant organization owner to instance administrator.

### Impact

ZITADEL Actions V1 run custom JavaScript inside the ZITADEL server process at OIDC, SAML, and login-flow trigger points. The runtime enables the goja Node-compatible `require()` registry without restricting the source loader, so Action scripts can load host files readable by the ZITADEL process (notably `.js` and `.json`, and in some cases other file contents via error channels).

An attacker with **ORG_OWNER** on any organization (which includes `org.action.write` and `org.flow.write`) can therefore:

* Read process-readable host files, including configuration or secrets mounted into the API container (for example service-account material, projected secrets, or config carrying sensitive values).
* On deployments that follow ZITADEL’s documented bootstrap paths (`ZITADEL_FIRSTINSTANCE_LOGINCLIENTPATPATH`, `ZITADEL_FIRSTINSTANCE_MACHINEKEYPATH`), recover instance-wide credentials such as the **IAM_LOGIN_CLIENT** PAT or the **IAM_OWNER** service-account key, enabling escalation to full instance control.

This collapses the expected multi-tenant isolation boundary: a tenant organization administrator is not meant to access host filesystem secrets or instance-wide credentials.

**Scope note:** This issue affects **Actions V1**. Host command execution was not identified as part of this vulnerability. Impact depends on what the ZITADEL process can read on disk and on deployment layout — documented Compose and quick-start setups that write bootstrap PATs or machine keys into the API container amplify severity.

### Affected Versions

Systems running one of the following versions are affected:

* **4.x:** `4.0.0` through `4.16.0` (including RC versions)
* **3.x:** `3.0.0` through `3.4.12` (including RC versions)

### Patches

The vulnerability has been addressed in the latest releases. The patch disables filesystem-backed module loading for Action scripts so that only the intended native `zitadel/*` modules can be required.

* **4.x**: Upgrade to $\ge$ [4.16.1](https://github.com/zitadel/zitadel/releases/tag/v4.16.1)
* **3.x**: Upgrade to $\ge$ [3.4.13](https://github.com/zit …[обрезано]
````

## Идея 9. Перечисление субъектов или объектов с доступом (кто имеет отношение, какие объекты доступны) согласовано с точечной проверкой каждого — с пересечением, исключением и wildcard в модели прав исключённый не попадает в список

### GHSA-g3pg-frfm-pr2m — OpenFGA: ListUsers returns a deliberately-excluded user when a `but not` exclusion under a type-bound wildcard is intersected (`and`) with another relation that also grants that user

Ссылка: https://github.com/advisories/GHSA-g3pg-frfm-pr2m

- **Паттерн:** Перечисление субъектов с доступом согласовано с точечной проверкой
- **Условие:** Модель прав сочетает пересечение, исключение и wildcard
- **Действие:** Для объекта получить список пользователей с отношением и сравнить с точечной проверкой каждого
- **Ожидание:** Исключённый пользователь не попадает в список
- **Источник ожидания:** Семантика модели прав продукта; здравый смысл
- **Почему не подошла ближайшая запись:** Записи о согласованности перечисления и точечной проверки прав нет

Первоисточник:

````text
### Description

In OpenFGA, the ListUsers API could incorrectly return a user who should have been excluded.

### Preconditions

This applies if all of the following are present:

- The authorization model contains a relation defined as an intersection (and) where at least one operand is an exclusion of the form base but not excluded: e.g. `rel1: (public_user but not blocked) and rel2`
- The base side of that exclusion is granted through a type-bound public wildcard (e.g. user:*).
- A user excluded by the but not clause is also granted, via a concrete tuple, through another operand of the intersection.
- Your application uses ListUsers to enumerate or enforce access

### Fix

Upgrade to OpenFGA v1.18.1 or greater.

### Acknowledgements

OpenFGA would like to thank @5ud0er for the detailed report.
````

## Идея 10. Эндпоинты первоначальной настройки (создание первого администратора, восстановление базы в окне инициализации) не позволяют захватить экземпляр без доказательства владения — секрета настройки или локального доступа; после настройки закрыты

### GHSA-x626-fcwx-f5pc — Portainer has Unauthenticated Restore Endpoint that Allows Admin Takeover on Uninitialized Instances

Ссылка: https://github.com/advisories/GHSA-x626-fcwx-f5pc

- **Паттерн:** Эндпоинты первоначальной настройки не позволяют захватить экземпляр без доказательства владения
- **Условие:** Экземпляр не инициализирован, открыто окно настройки после запуска; эндпоинты восстановления и создания администратора без аутентификации
- **Действие:** Без учётных данных отправить архив восстановления с подготовленной базой и запрос создания первого администратора
- **Ожидание:** Отказ без секрета настройки или локального доступа; база не заменяется
- **Источник ожидания:** OWASP API2:2023; здравый смысл
- **Почему не подошла ближайшая запись:** SECURITY-AUTH-REQUIRED — про штатно защищённые операции; здесь эндпоинты открыты намеренно на время настройки, проверка — про защиту окна инициализации

Первоисточник:

````text
## Summary
Portainer supports restoring an instance from a backup archive via the /api/restore endpoint. This endpoint is intentionally unauthenticated to allow restoring before the first admin account is created, and remains accessible for the five-minute initialization window that opens each time Portainer starts. Any unauthenticated attacker with network access to a Portainer instance that has not yet been initialised can exploit this window to replace the Portainer database with a crafted archive containing attacker-controlled credentials and gain full administrative access. The same unauthenticated setup window also exposes the administrator-account-creation endpoint (`/api/users/admin/init`), which an attacker can call to create the first administrator directly; the fix gates both endpoints.

The attack requires the instance to be uninitialized, reachable by the attacker, and within the five-minute window. Once that window expires without initialization, Portainer locks its API and requires a restart to re-enable setup — each restart opens a fresh window. No credentials, session tokens, or local access are required.

## Severity
**High**

The endpoint requires no authentication and no user interaction, but successful exploitation depends on three conditions holding simultaneously: the instance must be uninitialized, reachable from the attacker's network, and within the five-minute setup window that Portainer enforces before locking the instance pending a restart. Once those conditions are met, the attack itself is straightforward — no specialized tooling or elevated privileges are needed. The vulnerable system impact is limited by the precondition: a brand new instance carries no confidential data, no existing users, and no running workloads, so the direct integrity and availability impact is low. The severity is driven entirely by the subsequent-system chain — Portainer CE is typically bound to a Docker socket that grants root-equivalent access to the host, and the compromised admin account inherits credentials and API access for every Docker host, Kubernetes cluster, and edge agent registered in the instance.

## Affected Versions

The unauthenticated initialization path has been present since the backup/restore feature was introduced.

Fixes are included in the following releases:

| Branch       | First vulnerable | Fixed in   |
|--------------|------------------|------------|
| 2.39.x (LTS) | 2.39.0           | **2.39.4** |
| 2.43.x (STS) | all  …[обрезано]
````

## Идея 11. Тело, разбитое на множество крошечных кадров HTTP/2 DATA, не вызывает непропорционального роста памяти

### GHSA-vp52-pcj8-j9qc — gRPC-Go: Heap Memory Exhaustion (OOM) via HTTP/2 DATA Frame Fragmentation

Ссылка: https://github.com/advisories/GHSA-vp52-pcj8-j9qc

- **Действие:** Открыть несколько стримов и отправлять сообщения кадрами DATA по 1 байту
- **Ожидание:** Память растёт пропорционально объёму данных, сервер доступен

Первоисточник:

````text
### Impact
An unauthenticated remote attacker can initiate a gRPC stream and purposefully fragment their payload into millions of tiny (e.g., 1-byte) HTTP/2 DATA frames. Even if the total payload volume falls within the configured connection and stream flow-control windows, each independent fragment incurs memory overhead due to internal tracking structures and queue allocation.

Repeated fragmentation massively inflates the heap space consumed by the stream. An attacker multiplexing multiple concurrent streams can exhaust the memory bounds of the runtime, forcing a runtime panic or OutOfMemory condition and leading to a remote Denial of Service (DoS).

### Patches
The change to fix this issue is merged in `master` and a patch release, 1.83.1, has been published that contains this fix.

### Workarounds
This vulnerability is mitigated by implementing receive buffer compaction. Consecutive small data buffers are automatically coalesced into larger buffers from a shared pool once the overhead is perceived to be excessive relative to actual payload data, drastically minimizing per-frame memory overheads.

This behavior is enabled by default. A temporary escape hatch is provided via the environment variable `GRPC_GO_EXPERIMENTAL_ENABLE_RECEIVE_BUFFER_COMPACTION=false` to disable the feature if unforeseen issues arise, but it will be removed in a future release.
````

## Индекс библиотеки

Все записи (484): ID | категория | заголовок.

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
