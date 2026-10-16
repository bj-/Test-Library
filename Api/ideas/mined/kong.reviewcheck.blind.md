# Перекрёстное ревью новых идей выгрузки багов

Партия `kong`, идей: 11; вариант пакета — без решений Claude — независимое ревью.
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

## Идея 1. Заголовок WWW-Authenticate в ответе 401 разбирается строгим парсером — схема и параметры вызова через запятую с кавычками (Bearer realm="…", error="invalid_token", error_description="…"), по RFC 9110 §11.6.1 и RFC 6750 §3

### Kong/kong#14429 — Incorrect parameter delimiter in JWT plugin `WWW-Authenticate` header

Ссылка: https://github.com/Kong/kong/issues/14429

- **Паттерн:** Заголовок WWW-Authenticate в ответе 401 соответствует синтаксису RFC
- **Условие:** Запрос с отсутствующим или невалидным токеном, сервер отвечает 401 с вызовом и несколькими параметрами
- **Действие:** Отправить запрос с повреждённым токеном и разобрать заголовок WWW-Authenticate строгим парсером
- **Ожидание:** Параметры вызова разделены запятыми: Bearer realm="…", error="invalid_token"
- **Источник ожидания:** RFC 7235 §4.1, RFC 6750 §3
- **Почему не подошла ближайшая запись:** Ближайшая REST-AUTH-ERROR-NO-LEAK проверяет утечки в ошибке, а не синтаксис заголовка вызова

Первоисточник:

````text
### Is there an existing issue for this?

- [x] I have searched the existing issues

### Kong version (`$ kong version`)

3.9

### Description

I noticed that the `WWW-Authenticate` header in JWT plugin uses spaces to separate parameters.
https://github.com/Kong/kong/blob/ed117a6fe801a80ddaa07b5af30ed4c5daabf241/kong/plugins/jwt/handler.lua#L161

According to RFC 7235 (HTTP Authentication) ([Section 4.1](https://datatracker.ietf.org/doc/html/rfc7235#section-4.1)), the parameters in authentication headers should be comma-delimited. 

> ... and each challenge can contain a comma-separated list of authentication parameters.

The correct format should be:
`WWW-Authenticate: Bearer realm="auth-server", error="invalid_token"  `
(Note the comma , between realm and error parameters.)

If I misunderstood the RFC’s requirements for header formatting, kindly clarify or correct me.
````

## Идея 2. Исходящий HTTP-запрос сервера на настроенный пользователем адрес (вебхук, приёмник журналов, интеграция) содержит корректные заголовки — Host с нестандартным портом (имя:порт), Content-Type и Content-Length по телу

### Kong/kong#13067 — http-log plugin: Host header not including port

Ссылка: https://github.com/Kong/kong/issues/13067

- **Паттерн:** Исходящий HTTP-запрос сервера содержит Host с нестандартным портом
- **Условие:** Сервер отправляет запросы на настроенный пользователем URL с явным нестандартным портом (лог, вебхук)
- **Действие:** Настроить адрес приёмника с портом, вызвать отправку и проверить заголовок Host на приёмнике
- **Ожидание:** Host: имя:порт
- **Источник ожидания:** RFC 9110 §7.2
- **Почему не подошла ближайшая запись:** Записи о вебхуках проверяют подпись, повторы и SSRF, но не корректность заголовков исходящего запроса

Первоисточник:

````text
### Is there an existing issue for this?

- [X] I have searched the existing issues

### Kong version (`$ kong version`)

Kong 3.6

### Current Behavior

- use http-log plugin with config `http_endpoint="http://host_name:8080/log"`

- endpoint receive request with host head: `Host: host_name`

### Expected Behavior

endpoint receive request with host head: `Host: host_name:8080`

> The "Host" header field in a request provides the host and port information from the target URI ...

From the [RFC](https://www.rfc-editor.org/rfc/rfc9110.html#section-7.2) , we can see the Host header should include the port. 
If no port is included, the default port for the service requested is implied (e.g., 443 for an HTTPS URL, and 80 for an HTTP URL).

### Steps To Reproduce

_No response_

### Anything else?

_No response_
````

## Идея 3. Настроенные заголовки ответа (служебные, CORS, безопасности, трассировки) присутствуют во всех режимах обработки ответа — потоковом и буферизованном, сжатом и несжатом, из кэша и без

### Kong/kong#10031 — Response header 'X-Kong-Upstream-Status' is eliminated while custom plugin overwrite :response() function

Ссылка: https://github.com/Kong/kong/issues/10031

- **Паттерн:** Настроенные служебные заголовки ответа присутствуют и при буферизации ответа
- **Условие:** Включена отдача служебного заголовка, ответ обрабатывается в буферизованном режиме
- **Действие:** Отправить запрос в обычном и буферизованном режиме и сравнить заголовки
- **Ожидание:** Заголовок присутствует в обоих режимах
- **Источник ожидания:** Документация продукта
- **Почему не подошла ближайшая запись:** Нет записи о согласованности заголовков ответа между режимами обработки; HTTP-VERSION-PARITY — про версии протокола

Первоисточник:

````text
### Is there an existing issue for this?

- [X] I have searched the existing issues

### Kong version (`$ kong version`)

3.0.1

### Current Behavior

When I developed a helloworld level plugin with only `:access()` function,  I can see response header for both `X-Kong-Upstream-Status`  and `X-Kong-Upstream-Latency` by visiting the path I configured.

After I add a function `:response()` in the plugin, then `X-Kong-Upstream-Status` is dropped, but `X-Kong-Upstream-Latency` still present.

### Expected Behavior

Return `X-Kong-Upstream-Status` in response header

### Steps To Reproduce

```markdown
1. set `KONG_HEADERS="latency_tokens,X-Kong-Upstream-Status"`
2. Write a global custom plugin which do nothing. (only has `:access(conf)` and print something)
3. visit the service route and see `X-Kong-Upstream-Status` in response header
4. Add `:response()` in the custom plugin and do nothing as well.
5. visit the service route and cannot see `X-Kong-Upstream-Status` in response header
```

### Anything else?

_No response_
````

## Идея 4. Настройка более узкого уровня (маршрут, сервис, проект, арендатор, пользователь) имеет приоритет над глобальной; на объектах без своей настройки действует глобальная; удаление узкой настройки возвращает глобальную

### Kong/kong#9812 — Zipkin: Global sample ratio overrides route-specific

Ссылка: https://github.com/Kong/kong/issues/9812

- **Паттерн:** Настройка уровня маршрута имеет приоритет над глобальной
- **Условие:** Одна функция настроена глобально и на конкретном маршруте с разными параметрами
- **Действие:** Отправить запросы на маршрут с собственной настройкой и на маршрут без неё, сравнить поведение
- **Ожидание:** На маршруте действует его настройка, на остальных — глобальная
- **Источник ожидания:** Документация продукта
- **Почему не подошла ближайшая запись:** Нет записи о приоритете настроек разных уровней (глобальная, сервис, маршрут)

Первоисточник:

````text
### Is there an existing issue for this?

- [X] I have searched the existing issues

### Kong version (`$ kong version`)

2.8.1

### Current Behavior

I'm facing the same problem as https://github.com/Kong/kong-plugin-zipkin/issues/106

Configure:
```YAML
# global plugin
apiVersion: configuration.konghq.com/v1
config:
  default_header_type: b3
  header_type: b3
  sample_ratio: 0
kind: KongClusterPlugin
metadata:
  annotations:
    kubernetes.io/ingress.class: kong
  labels:
    global: "true"
  name: global-zipkin
plugin: zipkin
---
# route plugin
apiVersion: configuration.konghq.com/v1
config:
  default_header_type: b3-single
  header_type: b3-single
  sample_ratio: 0.5
kind: KongPlugin
metadata:
  name: rt-echo-service-api-zipkin
  namespace: taind-lab
plugin: zipkin
```
After configuring my service like this, I always get a **b3-single** ( not b3) trace id header with sample bit equals 0.

### Expected Behavior

_No response_

### Steps To Reproduce

_No response_

### Anything else?

_No response_
````

## Идея 5. Ссылка next (в теле или заголовке Link) ведёт на тот же путь коллекции, что и исходный запрос, сохраняет фильтры и работает — в том числе для коллекции, доступной по нескольким путям

### Kong/kong#8243 — use /upstreams/{upstream}/targets/all  "next" field to get next page occurred 500 when paging

Ссылка: https://github.com/Kong/kong/issues/8243

- **Паттерн:** Ссылка next пагинации ведёт на ту же коллекцию и работает
- **Условие:** Коллекция с несколькими страницами, доступная по разным путям (/targets и /targets/all)
- **Действие:** Запросить первую страницу и перейти по ссылке next
- **Ожидание:** Ссылка next ведёт на тот же путь, следующая страница 200
- **Источник ожидания:** RFC 8288, практика
- **Почему не подошла ближайшая запись:** Записи пагинации проверяют границы и порядок, но не корректность ссылки next

Первоисточник:

````text
### Is there an existing issue for this?

- [X] I have searched the existing issues

### Kong version (`$ kong version`)

Kong 2.1.3

### Current Behavior

There is no clear description of how to get next page data in doc. So I use http://${host}:${port}/${next} to get next page data.
When I want get all targets contains weight=0 with `/upstreams/{upstream}/targets/all` , I found the 'next' field in response is not correct. It will response 500 with http://${host}:${port}/${next} . 
I want to know is it a bug or use `offset` param is the right way.
ps: Under Kong 2.5.0 is same.

### Expected Behavior

When I call `/upstreams/test-1-Pool/targets/all`, the response return right 'next' field, like:
`/upstreams/test-1-Pool/targets/all?offset=xxx`

### Steps To Reproduce

```markdown
1. use api `0:8001/upstreams/test-1-Pool/targets` create 200 different targets.
2. call api `0:8001/upstreams/test-1-Pool/targets/all`, get response like:

{
    "offset": "WyI4Mjk5YWEzZC02M2QyLTQ4MDAtYjk1Ni1iOGViODJjMTc1ZmUiXQ",
    "data": [
     ...
    ],
    "next": "/upstreams/test-1-Pool/targets?offset=WyI4Mjk5YWEzZC02M2QyLTQ4MDAtYjk1Ni1iOGViODJjMTc1ZmUiXQ"
}
```
3. call `0:8001/upstreams/test-1-Pool/targets?offset=WyI4Mjk5YWEzZC02M2QyLTQ4MDAtYjk1Ni1iOGViODJjMTc1ZmUiXQ` occrur  500 Internal Server Error
 ```
{
    "message": "An unexpected error occurred"
}
```
```

### Anything else?

_No response_
````

## Идея 6. Шаблон домена с wildcard (*.example.com) в маршрутизации, списках разрешённых origin и redirect совпадает только с поддоменами указанного домена — не с abc.gw-example.com, example.com.evil.com и подобными

### Kong/kong#7834 — ACME plugin is not matching wildcard domain correctly

Ссылка: https://github.com/Kong/kong/issues/7834

- **Паттерн:** Шаблон домена с wildcard совпадает только с поддоменами указанного домена
- **Условие:** В настройке задан домен-шаблон *.alpha.example.com
- **Действие:** Отправить запросы с Host a.alpha.example.com и abc.gw-alpha.example.com
- **Ожидание:** Совпадает только первый, второй не обрабатывается
- **Источник ожидания:** RFC 6125 §6.4.3, здравый смысл
- **Почему не подошла ближайшая запись:** Нет записи о точности сопоставления шаблонов хостов; VAL-REGEX-PATTERN — про валидацию ввода по pattern

Первоисточник:

````text
### Is there an existing issue for this?

- [X] I have searched the existing issues

### Kong version (`$ kong version`)

2.4.1 (ACME plugin version: 0.2.14)

### Current Behavior

I am using the ACME plugin with following config (sorry for that domains are redacted since I think they are sensitive):
```yaml
plugin: acme
config:
  account_email: jacky96623@example.com
  tos_accepted: true
  domains:
    - '*.alpha.mydomain.com'
```

HTTP-01 challenge goes smoothly with domains like `www.alpha.mydomain.com`, `api.alpha.mydomain.com`, etc.
But I found that domains like `abc.gw-alpha.mydomain.com` are also matched with the above config.

And I could find debug log showing the case:
```
2021/09/12 07:13:58 [debug] 24#0: *18689 [lua] client.lua:297: post(): acme request: https://acme-v02.api.letsencrypt.org/acme/order/127728407/23840616100 response: {
  "status": "pending",
  "expires": "2021-09-19T07:13:56Z",
  "identifiers": [
    {
      "type": "dns",
      "value": "developer-abc.gw-alpha.mydomain.com"
    }
  ],
  "authorizations": [
    "https://acme-v02.api.letsencrypt.org/acme/authz-v3/30207163860"
  ],
  "finalize": "https://acme-v02.api.letsencrypt.org/acme/finalize/127728407/23840616100"
}
```

### Expected Behavior

ACME plugin should not help to initiate HTTP-01 challenge when the upper level domain does not match.

### Steps To Reproduce

_No response_

### Anything else?

Roughly went through the code of Kong acme plugin, suspect that the issue is related to https://github.com/Kong/kong-plugin-acme/blob/master/kong/plugins/acme/handler.lua#L27-L46. The wildcard domains are stored with initial '*.' removed. The regex matching afterwards do not handle the case that there are other domains similar - possibly with some prefix.
````

## Идея 7. Журнал запроса с повторами к зависимости содержит данные о каждой попытке, включая последнюю неуспешную (код, состояние, время); нужен доступ к журналу запросов

### Kong/kong#6820 — If final balancer retry fails, that try does not have the failure data recorded

Ссылка: https://github.com/Kong/kong/issues/6820

- **Паттерн:** Журнал запроса содержит данные о каждой попытке, включая последнюю
- **Условие:** Запрос к upstream с повторами, все попытки неуспешны (тайм-аут)
- **Действие:** Отправить запрос, превышающий тайм-аут, и проверить запись журнала о попытках
- **Ожидание:** У каждой попытки, включая последнюю, есть код и состояние
- **Источник ожидания:** Здравый смысл
- **Почему не подошла ближайшая запись:** Нет записи о полноте данных журнала запроса; OBS-AUDIT-TRAIL — про аудит чувствительных действий

Первоисточник:

````text
### Summary

This code records the failure details for the **previous** try:
https://github.com/Kong/kong/blob/2.3.1/kong/init.lua#L926-L928

As such, if the final retry is a failure, those details don't get recorded.

### Steps To Reproduce

1. Add service and route objects with artificial latency to force retries, e.g.
```yaml
routes:
- name: httpbin
  paths:
  - /
  preserve_host: true
  service: httpbin
  strip_path: false

services:
- name: httpbin
  host: httpbin
  protocol: http
  port: 80
  retries: 3
  connect_timeout: 1000
  read_timeout: 1000
  write_timeout: 1000
```

2. Make a request that will timeout, e.g. `/delay/2`

3. You'll see something like this in the logs:
```json
    "tries": [
        {
            "balancer_latency": 1,
            "port": 80,
            "ip": "172.20.0.4",
            "code": 504,
            "balancer_start": 1612821178453,
            "state": "failed"
        },
        {
            "balancer_latency": 0,
            "port": 80,
            "ip": "172.20.0.4",
            "code": 504,
            "balancer_start": 1612821179456,
            "state": "failed"
        },
        {
            "balancer_latency": 0,
            "port": 80,
            "ip": "172.20.0.4",
            "code": 504,
            "balancer_start": 1612821180457,
            "state": "failed"
        },
        {
            "balancer_latency": 0,
            "port": 80,
            "balancer_start": 1612821181457,
            "ip": "172.20.0.4"
        }
    ],
```

### Additional Details & Logs

- Kong version (2.3.1)
````

## Идея 8. Условие маршрута, неприменимое к протоколу (SNI для HTTP), не блокирует совпадение маршрута по этому протоколу

### Kong/kong#6425 — Dual stack HTTP+HTTPS routes cannot contain SNI match criteria while still honoring their protocols criteria

Ссылка: https://github.com/Kong/kong/issues/6425

- **Паттерн:** Условие, неприменимое к протоколу, не блокирует совпадение маршрута по этому протоколу
- **Условие:** Маршрут разрешает HTTP и HTTPS и содержит условие по SNI, которое есть только в TLS
- **Действие:** Отправить HTTP-запрос с подходящим Host и HTTPS-запрос с подходящим SNI
- **Ожидание:** Оба запроса совпадают с маршрутом; для HTTP условие SNI не учитывается
- **Источник ожидания:** Здравый смысл
- **Почему не подошла ближайшая запись:** Нет записи о совпадении маршрута при условиях, применимых только к одному из протоколов

Первоисточник:

````text
### Summary

Given a route that supports both HTTP and HTTPS requests, and has both hostname and SNI match criteria (for the same hostname), an HTTP request with the correct hostname will not match the given route. There is no way for _any_ HTTP request to match that route, because plaintext HTTP requests will never contain SNI because they have no TLS envelope by definition.

### Steps To Reproduce

1. Create a service.
2. Create two routes, one with hostname and SNI criteria for `sni.kong.example`, and one with hostname criteria only, for `nosni.kong.example`. As no protocol set is explicitly specified, these routes will default to `protocols=http,https`
3. Send an HTTP request to the first route, with the correct hostname, e.g. `curl -sv localhost:8000/anything -H "Host: sni.kong.example"`. Kong will return a 404.
4. Send an HTTP request to the second route, e.g. `curl -sv localhost:8000/anything -H "Host: nosni.kong.example"`. The route will proxy normally, and return a 200 (or whatever status the upstream service normally returns).

[sni-404-example.yaml.txt](https://github.com/Kong/kong/files/5320511/sni-404-example.yaml.txt) is a deck dump that covers the above. Github is silly and forced me to append the `.txt` extension.

Note that this also applies to HTTPS-only routes with an HTTPS redirect status code: once you add SNI criteria, those routes will no longer redirect to HTTPS when receiving an otherwise-matching HTTP request, and clients sending those requests will instead receive a 404.

### Additional Details & Logs

Tested on kong/2.2.0beta.1, Alpine Docker. Should affect any Kong version/platform that supports SNI match criteria.

### Why this matters

See previous internal discussion in FTI-1881 and comments on https://github.com/Kong/kubernetes-ingress-controller/pull/863. On the controller side, we would like to handle adding SNI criteria for users automatically, as we can reasonably assume that Ingresses with a hostname rule and TLS information will be HTTPS-accessible, and will receive HTTPS requests with SNI information that have a matching HTTP hostname. There are some caveats to this, but I won't re-tread them here.

However, many of those rules will also be dual-stack, i.e. they will allow HTTP traffic alongside HTTPS traffic. As-is, adding SNI criteria to these routes forces them to single-stack HTTPS, because adding SNI criteria to a route means _any_ request that wants to match that route must include a TLS  …[обрезано]
````

## Идея 9. Ответ сервера не содержит одновременно Content-Length и Transfer-Encoding (RFC 9112 §6.1), в том числе когда заголовки ответа задаёт приложение или upstream; пара к HTTP-REQUEST-SMUGGLING

### Kong/kong#8083 — kong.response.exit setting Content-Length when Transfer-Encoding is present

Ссылка: https://github.com/Kong/kong/issues/8083

- **Паттерн:** Ответ не содержит одновременно Content-Length и Transfer-Encoding
- **Условие:** Ответ формируется сервером с заголовком Transfer-Encoding: chunked
- **Действие:** Отправить запрос на маршрут, ответ которого задаёт Transfer-Encoding, и проверить заголовки
- **Ожидание:** Нет Content-Length при Transfer-Encoding
- **Источник ожидания:** RFC 9112 §6.2
- **Почему не подошла ближайшая запись:** HTTP-REQUEST-SMUGGLING — про противоречивые заголовки в запросе, а не в ответе сервера

Первоисточник:

````text
### Is there an existing issue for this?

- [X] I have searched the existing issues

### Kong version (`$ kong version`)

2.5.1.0

### Current Behavior

When calling `kong.response.exit()`, the function automatically sets the Content-Length header on the response even if the Transfer-Encoding header is present. This is in violation of RFC 7230 3.3.2: 
> A sender MUST NOT send a Content-Length header field in any message
   that contains a Transfer-Encoding header field.

### Expected Behavior

`kong.response.exit()` should not set Content-Length if the Transfer-Encoding header is present in the header list provided as the third method argument.

### Steps To Reproduce

```markdown
1. Create a new plugin or edit an existing one. In the access phase, call `kong.response.exit(200, {}, { ["Transfer-Encoding"] = "chunked" }`
2. Via the API, create an instance of the plugin and send it a request
3. Observe that the response contains both the Transfer-Encoding and Content-Length headers
```


### Anything else?

_No response_
````

## Идея 10. Basic-аутентификация принимает пароль с двоеточием, пробелами и не-ASCII (UTF-8) — логин отделяется по первому двоеточию (RFC 7617 §2); позитивная пара к SEC-AUTHN-MALFORMED

### Kong/kong#7968 — Kong authentication LDAP plugin is not decoding password correctly when containing colon

Ссылка: https://github.com/Kong/kong/issues/7968

- **Паттерн:** Пароль с двоеточием в Basic-учётных данных принимается
- **Условие:** Пароль содержит двоеточие, учётные данные передаются как base64(user:pass)
- **Действие:** Отправить запрос с Authorization для пароля pass:w0rd
- **Ожидание:** Логин отделяется по первому двоеточию, вход успешен
- **Источник ожидания:** RFC 7617 §2
- **Почему не подошла ближайшая запись:** Нет позитивной записи о разборе учётных данных со спецсимволами; SEC-AUTHN-MALFORMED — негативное направление

Первоисточник:

````text
### Is there an existing issue for this?

- [X] I have searched the existing issues

### Kong version (`$ kong version`)

2.6.0

### Current Behavior

When I send an HTTP request containing a header "Authorization base64(username:password)" where password contains colon, the LDAP plug-in wrongly decodes the username and the authorization fails.
Example:
username: tomas
password: pass:w0rd 

=> Header: Authorization: "LDAP dG9tYXM6cGFzczp3MHJk"
Plug-in decodes that as
username: tomaspass
password: w0rd (probably, as not verified)

### Expected Behavior

_No response_

### Steps To Reproduce

_No response_

### Anything else?

_No response_
````

## Идея 11. Активные проверки здоровья целей выполняются с настроенной частотой

### Kong/kong#6788 — Kong 2.3.1 healthcheck

Ссылка: https://github.com/Kong/kong/issues/6788

- **Паттерн:** Активные проверки здоровья выполняются с настроенной частотой
- **Условие:** Несколько процессов-обработчиков, активная проверка здоровья с интервалом 10 с
- **Действие:** Посчитать на цели число проверочных запросов за минуту
- **Ожидание:** 6 запросов в минуту на цель
- **Источник ожидания:** Документация продукта
- **Почему не подошла ближайшая запись:** Нет записи о частоте исходящих проверок здоровья; OBS-HEALTH-ENDPOINTS — про входящие health-эндпоинты

Первоисточник:

````text
In 2.2.1
1 instance， 8 worker， http health check interval 10， 4 target  the health check is 24 per min

In 2.3.1
1 instance， 8 worker， http health check interval 10， 4 target  the health check is 24 * 8 per min

I think it‘s a bug
[image]
````

## Индекс библиотеки

Все записи (474): ID | категория | заголовок.

```text
ASYNC-DEAD-LETTER | async | Необрабатываемые сообщения уходят в DLQ без блокировки очереди
ASYNC-EVENT-ORDERING | async | Нарушение порядка событий не портит состояние
ASYNC-EVENT-PATH-SAME-RULES | async | Событийный путь применяет те же фильтры и границы доступа, что и плановый
ASYNC-IDEMPOTENT-CONSUMER | async | Повторная доставка события обрабатывается однократно
ASYNC-JOB-CANCEL | async | Отмена фоновой задачи останавливает её и не оставляет частичных эффектов
ASYNC-JOB-LIFECYCLE | async | Фоновая задача проходит статусы и отдаёт результат
ASYNC-MESSAGE-VALIDATION | async | Входящие сообщения брокера валидируются по схеме так же, как HTTP-запросы
ASYNC-RPC-ERROR-PROPAGATION | async | Ошибка обработчика в схеме запрос-ответ через брокер возвращается вызывающему
ASYNC-SCHEDULE-LONG-UPTIME | async | Задача по расписанию срабатывает и после длительной непрерывной работы процесса
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
