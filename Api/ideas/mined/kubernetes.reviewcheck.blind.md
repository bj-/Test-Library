# Перекрёстное ревью новых идей выгрузки багов

Партия `kubernetes`, идей: 12; вариант пакета — без решений Claude — независимое ревью.
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

## Идея 1. Законный запрос с сотнями повторяющихся строк одного заголовка (группы при имперсонации, от аутентифицирующего прокси) в пределах лимита размера обслуживается одинаково по HTTP/1.1 и HTTP/2; лимит числа строк, если есть, задокументирован, а отказ попадает в аудит или лог; позитивная пара к HTTP-HEADER-SIZE-LIMIT

### kubernetes/kubernetes#142606 — kube-apiserver built with Go 1.27 returns 431 for impersonated or front-proxy users with about 500 groups

Ссылка: https://github.com/kubernetes/kubernetes/issues/142606

- **Паттерн:** Запрос с сотнями повторяющихся строк одного заголовка в пределах лимита размера принимается
- **Условие:** Заголовок передаёт по одному значению на строку (группы пользователя при имперсонации или от аутентифицирующего прокси), значений около 500 и больше, общий размер заголовков в пределах лимита
- **Действие:** Отправить запрос с 100, 495, 500 и 1000 повторами заголовка группы по HTTP/1.1 и по HTTP/2 и сравнить ответы
- **Ожидание:** Запрос в пределах документированного лимита размера заголовков обслуживается одинаково по обеим версиям HTTP; если действует лимит числа строк — он задокументирован, а отказ попадает в журнал аудита или лог
- **Источник ожидания:** RFC 9110 §5.3 (повторяющиеся строки поля равноценны списку); практика; здравый смысл
- **Почему не подошла ближайшая запись:** HTTP-HEADER-SIZE-LIMIT — негативная проверка отказа на слишком больших заголовках; здесь законный запрос отклоняется по числу строк заголовка, направление обратное

Первоисточник:

````text
### What happened?

We're reporting this ahead of v1.38 because it only appears when several conditions combine, and it's easy to miss until someone with a large group membership hits it.

Go 1.27 added `http.Server.MaxHeaderValueCount` with a default of 500 ([golang/go#79936](https://github.com/golang/go/issues/79936)). Repeated header lines are counted individually. kube-apiserver does not set this field, and the identity headers it accepts carry one group per header line:

- `Impersonate-Group` (user impersonation)
- `X-Remote-Group` (request-header authentication, used by authenticating proxies)

As a result, kube-apiserver v1.38.0-alpha.1 (go1.27.1) returns `431 Request Header Fields Too Large` for requests that impersonate, or are proxied on behalf of, a user with about 500 groups. For the curl request below, 495 groups produce 431 over HTTP/2 but 200 over HTTP/1.1, and 500 groups produce 431 over both; the exact threshold depends on the other request headers. v1.37.1 (go1.26.8) accepts the same requests, tested up to 1,000 groups.

The rejection happens in `net/http` before Kubernetes request handlers run. In our run with Metadata-level auditing and default log verbosity, the rejected requests had no audit record and no related kube-apiserver log message.

Go 1.27 has no `GODEBUG` override for this limit; one was proposed and declined ([golang/go#80020](https://github.com/golang/go/issues/80020)). Accepting the same repeated headers on a Go 1.27 server requires setting `MaxHeaderValueCount`.

Who is affected, as far as we can tell: only requests whose groups are carried in headers (impersonation, request-header authentication, and requests kube-apiserver proxies to aggregated API servers), for users with roughly 500 or more groups, on servers built with Go 1.27. Users with fewer groups are unaffected. Groups taken from client certificates, OIDC or webhook token authentication are not sent to kube-apiserver as headers, although aggregated API servers still receive them that way. We hit this with an enterprise directory in which some users belong to more than 1,000 groups.

### What did you expect to happen?

Requests for users with several hundred to over a thousand groups keep working through impersonation and request-header authentication, as they do with Go 1.26 builds, or the limit becomes explicit and documented rather than an implicit `net/http` default.

### How can we reproduce it (as minimally and precisely as possible)?

1. Start etcd (list …[обрезано]
````

## Идея 2. Если право выводится двумя путями (по цепочке связанных объектов или явным правом в авторизаторе), ошибка основного пути (связанный объект не найден) не отменяет запасной — решение по явному праву, без права — 403 с причиной; ни fail-open, ни ложного отказа

### kubernetes/kubernetes#140159 — Correctly fallback to token request audience authz check on error

Ссылка: https://github.com/kubernetes/kubernetes/issues/140159

- **Паттерн:** Запасная проверка прав через авторизатор применяется и после ошибки поиска связанного объекта
- **Условие:** Операция разрешается либо по связанным объектам (pod → pvc → pv → драйвер), либо явным правом в авторизаторе; один из связанных объектов не найден
- **Действие:** Выдать явное право на операцию, удалить связанный объект из цепочки и выполнить операцию
- **Ожидание:** Решение принимается по явному праву из авторизатора; без права — отказ 403 с причиной
- **Источник ожидания:** Документация функции (обход через авторизатор); здравый смысл
- **Почему не подошла ближайшая запись:** SEC-AUTHZ-ROLE-POSITIVE-MATRIX проверяет разрешённую операцию по ролям, а не запасной путь авторизации при ошибке основной проверки

Первоисточник:

````text
```
OK, yeah, I think this points to a (minor) bug in the token audience restriction:

These test cases fail:
* forbid create of token when audience in pod --> csi --> driver --> tokenrequest with audience and ServiceAccountNodeAudienceRestriction is enabled, csidriver not found
* forbid create of token when audience in pod --> pvc --> pv --> csi --> driver --> tokenrequest with audience and ServiceAccountNodeAudienceRestriction is enabled, pvc not found
* forbid create of token when audience in pod --> pvc --> pv --> csi --> driver --> tokenrequest with audience and ServiceAccountNodeAudienceRestriction is enabled, pv not found

The authorizer ends up not being called in these cases, which means that the authorizer-based bypass won't work for these cases.

I don't think you could hit these cases in a properly-functioning cluster, so I think it's fine for the bypass to not work.  I'll just take the authorizer out of those cases.
```

_Originally posted by @ahmedtd in https://github.com/kubernetes/kubernetes/pull/140006#discussion_r3502083211_
````

## Идея 3. Проверка доступности внешнего бэкенда проверяет его сертификат (с заданным CA, без пропуска проверки TLS) и сама восстанавливается, когда на адрес вернулся настоящий бэкенд, — без перезапуска сервиса

### kubernetes/kubernetes#135883 — APIService remains unhealthy due to kube-apiserver reusing connection to incorrect endpoint and not verifying server certificate

Ссылка: https://github.com/kubernetes/kubernetes/issues/135883

- **Паттерн:** Проверка доступности внешнего бэкенда проверяет его сертификат и восстанавливается после ответа чужого сервера
- **Условие:** Зарегистрирован внешний бэкенд с CA-сертификатом и запретом пропуска проверки TLS; на время проверка доступности попадает на другой сервер на том же адресе
- **Действие:** Подменить бэкенд сервером с чужим сертификатом, затем вернуть настоящий и следить за статусом доступности бэкенда без перезапуска сервиса
- **Ожидание:** Соединение с сервером с неверным сертификатом отклоняется; после возврата настоящего бэкенда статус становится доступным без перезапуска
- **Источник ожидания:** OWASP API10:2023; RFC 5280 (проверка цепочки); здравый смысл
- **Почему не подошла ближайшая запись:** RESIL-DEPENDENCY-DOWN проверяет контролируемую ошибку при недоступности зависимости, а не проверку её сертификата и восстановление после ответа чужого сервера

Первоисточник:

````text
### What happened?

When kube-apiserver is deployed on a new control-plane node before kube-proxy is running, the AvailableConditionController, which checks the availability of registered APIServices, may connect to the Service’s ClusterIP before it is proxied by kube-proxy. As a result, the connection can be routed to an external server that happens to be listening on the same IP, causing the APIService to be reported as unhealthy due to unexpected responses.

However, even after the kube-proxy runs and proxys the ClusterIP, because of transport-layer connection caching and the fact that kube-apiserver is hard-coded to skip server certificate validation (even when the APIService’s `insecureSkipTLSVerify` is set to false), the APIService can remain unhealthy until the kube-apiserver is restarted:
https://github.com/kubernetes/kubernetes/blob/5151f58ef08d9fb26931019d6d844292aeb57637/staging/src/k8s.io/kube-aggregator/pkg/controllers/status/remote/remote_available_controller.go#L179-L184

### What did you expect to happen?

kube-apiserver should be able to recover from corner cases where it mistakenly establishes a connection to an incorrect server that never returns the expected response during APIService availability checks. It can be addressed either by verifying the server’s certificate when the APIService’s caBundle is provided, or by avoiding reuse of cached connections when the server returns an unexpected response.

### How can we reproduce it (as minimally and precisely as possible)?

1. Install an APIService with a caBundle configured and backed by a ClusterIP Service.
2. Run an HTTPS API server outside the cluster that listens to the ClusterIP and is routable from the cluster and returns 404 for unknown paths.
3. Add a new control-plane node where kube-apiserver starts before kube-proxy is scheduled on the node.
4. Check the kube-apiserver logs: the APIService continues to be reported as unhealthy due to 404 status code even after kube-proxy is running on the node.

### Anything else we need to know?

_No response_

### Kubernetes version

<details>

```console
$ kubectl version
# paste output here
```

</details>

### Cloud provider

<details>

</details>

### OS version

<details>

```console
# On Linux:
$ cat /etc/os-release
# paste output here
$ uname -a
# paste output here

# On Windows:
C:\> wmic os get Caption, Version, BuildNumber, OSArchitecture
# paste output here
```

</details>

### Install tools

<details>

</details>

### Container r …[обрезано]
````

## Идея 4. Сервер подхватывает заменённые файлы TLS-сертификата и ключа (внешняя ротация) без перезапуска; после истечения старого сертификата соединения успешны; нужен доступ к файлам сертификата на стенде

### kubernetes/kubernetes#133001 — Kubelet certificate not reloaded after replacement

Ссылка: https://github.com/kubernetes/kubernetes/issues/133001

- **Паттерн:** Сервер подхватывает обновлённый TLS-сертификат без перезапуска
- **Условие:** Сертификат и ключ сервера заданы файлами и регулярно заменяются внешней системой ротации
- **Действие:** Заменить файлы сертификата действующим новым, подключиться к серверу и проверить срок и серийный номер отдаваемого сертификата
- **Ожидание:** После замены файлов сервер в разумный срок отдаёт новый сертификат, соединения после истечения старого успешны
- **Источник ожидания:** Практика ротации сертификатов; здравый смысл
- **Почему не подошла ближайшая запись:** HARD-TLS-ONLY проверяет наличие и настройки TLS, RESIL-ENCRYPTION-KEY-ROTATION — ключи шифрования данных; перечитывания сертификата при ротации нет

Первоисточник:

````text
### What happened?

I am running the kubelet with a custom TLS certificate, using:

```yaml
tlsCertFile: /etc/kubernetes/pki/kubelet.crt
tlsPrivateKeyFile: /etc/kubernetes/pki/kubelet.key
```

I am automatically rotating this certificate using OpenBao. After some time, I see an error about an expired certificate:

```
> kubectl logs -n kube-system kube-apiserver-node-0 
Error from server: Get "https://172.29.0.2:10250/containerLogs/kube-system/kube-apiserver-node-0/kube-apiserver": tls: failed to verify certificate: x509: certificate has expired or is not yet valid: current time 2025-07-16T19:47:40Z is after 2025-06-30T23:08:51Z
```

However, the certificate on disk is still valid:

```
# openssl x509 -noout -text < /etc/kubernetes/pki/kubelet.crt 
Certificate:
    Data:
        Version: 3 (0x2)
        Serial Number:
            7a:7a:b8:8e:ca:dc:61:19:f8:a7:07:ce:35:1a:ed:86:79:e8:21:bb
        Signature Algorithm: ecdsa-with-SHA384
        Issuer: CN = Cerai kubelet CA
        Validity
            Not Before: Jul 13 19:54:43 2025 GMT
            Not After : Jul 20 19:55:13 2025 GMT
        Subject: CN = kubelet
```

It seems the kubelet is not reloading the changed certificate. Running `systemctl restart kubelet` fixes the issue temporarily (until the certificate expires again).

### What did you expect to happen?

I expect the kubelet to function correctly, as long as the certificate on disk is valid.

### How can we reproduce it (as minimally and precisely as possible)?

I haven't tested this reproducer yet, I will do that tomorrow. But I think the following should be sufficient:

1. Start the kubelet with `tlsCertFile`
3. Overwrite the certificate on-disk with a new certificate
4. Observe that the kubelet is still using the old certificate

### Anything else we need to know?

I'm happy to work on a fix for this.

### Kubernetes version

<details>

```console
$ kubectl version
Client Version: v1.33.0
Kustomize Version: v5.6.0
Server Version: v1.33.1
```

</details>

### Cloud provider

<details>
Hetzner Cloud
</details>

### OS version

<details>

```console
# On Linux:
$ cat /etc/os-release
# paste output here
$ uname -a
# paste output here

# On Windows:
C:\> wmic os get Caption, Version, BuildNumber, OSArchitecture
# paste output here
```

</details>

### Install tools

<details>

</details>

### Container runtime (CRI) and version (if applicable)

<details>

</details>

### Related plugins (CNI, CSI, ...) and versions (if applicable)

<details>

< …[обрезано]
````

## Идея 5. Обновление сервера, в том числе поэтапное (старая и новая версии работают одновременно), не меняет сохранённые объекты без действий пользователя — ревизии не растут, производные действия не запускаются, общий служебный объект не перезаписывается версиями по кругу; нужна возможность развернуть две версии

### kubernetes/kubernetes#134773 — Upgrading from 1.33 → 1.34 triggers a spurious rollout of existing StatefulSets

Ссылка: https://github.com/kubernetes/kubernetes/issues/134773

- **Паттерн:** Обновление версии сервера не запускает побочных действий над неизменёнными объектами
- **Условие:** Объекты созданы на старой версии сервера; новая версия иначе сериализует пустые поля (убирает creationTimestamp: null)
- **Действие:** Создать объекты на старой версии, обновить сервер и проверить, что ревизии и производные объекты не изменились
- **Ожидание:** Без изменения спецификации пользователем ревизия не меняется и раскатка не запускается
- **Источник ожидания:** Здравый смысл; политика совместимости при обновлении
- **Почему не подошла ближайшая запись:** COMPAT-* проверяют изменения контракта для клиентов, а не изменение сериализации сохранённых данных, запускающее побочные действия после обновления

Первоисточник:

````text
### What happened?

Since 1.34 upgrade we detected pods rollout of all our statefulset in the cluster.

After checking the diff before/after it seems that the rollout is coming from the removal of this field `creationTimestamp: null` in spec.template.metadata part.

Related PR: https://github.com/kubernetes/kubernetes/pull/130989/files#diff-852b629be7dedc81069c59d93e421333ed7bba4f35fdca69dfad9d8ca9c16e8b

### What did you expect to happen?

No rollout of the pods.

### How can we reproduce it (as minimally and precisely as possible)?

Create a statefulset in a 1.33 cluster and upgrade it to 1.34.

### Anything else we need to know?

_No response_

### Kubernetes version

<details>

```console
Client Version: v1.34.1
Kustomize Version: v5.7.1
Server Version: v1.34.1-eks-d96d92f
```

</details>

### Cloud provider

<details>
AWS EKS
</details>

### OS version

<details>

```console
# On Linux:
$ cat /etc/os-release
# paste output here
$ uname -a
# paste output here

# On Windows:
C:\> wmic os get Caption, Version, BuildNumber, OSArchitecture
# paste output here
```

</details>

### Install tools

<details>

</details>

### Container runtime (CRI) and version (if applicable)

<details>

</details>

### Related plugins (CNI, CSI, ...) and versions (if applicable)

<details>

</details>
````

### kubernetes/kubernetes#128986 — Dueling writes to extension-apiserver-authentication configmap during 1.31 → 1.32.0-rc.1 upgrade

Ссылка: https://github.com/kubernetes/kubernetes/issues/128986

- **Паттерн:** Экземпляры разных версий при поэтапном обновлении не перезаписывают общий объект по кругу
- **Условие:** Поэтапное обновление: одновременно работают экземпляры старой и новой версии, оба поддерживают один общий служебный объект
- **Действие:** Запустить экземпляры двух версий и следить за resourceVersion и содержимым общего объекта
- **Ожидание:** Объект стабилизируется; новые поля не стираются старой версией и не дописываются по кругу
- **Источник ожидания:** Политика поэтапного обновления; здравый смысл
- **Почему не подошла ближайшая запись:** COMPAT-* проверяют совместимость для клиентов; конфликта записи общих данных экземплярами разных версий нет; CONC-LOST-UPDATE про пользовательские изменения

Первоисточник:

````text
### What happened?

We had an alert firing for high memory usage for 1.32. At the time of increase we changed the churn to create at v1.31 (So update to v1.32). Previously it was creating at v1.30 and updating to v1.31

We can see some etcd are using more memory than others
```
kubx-etcd-02          etcd-csprq8020q6fal7635s0-6zxcz72w5v                         24m          420Mi           
kubx-etcd-02          etcd-csprq8020q6fal7635s0-hm5px7dkc5                         19m          416Mi           
kubx-etcd-02          etcd-csprq8020q6fal7635s0-jhmsq75wc5                         60m          566Mi  

...

kubx-etcd-04          etcd-cssndj620tea3foqjl5g-5qqscgqp2g                         28m          101Mi           
kubx-etcd-04          etcd-cssndj620tea3foqjl5g-c45kz2lprz                         23m          117Mi           
kubx-etcd-04          etcd-cssndj620tea3foqjl5g-wsbwcb9fp8                         50m          103Mi 
```

### What did you expect to happen?

When a cluster updating to 1.32 from 1.31, we expected (roughly) th same etcd memory usage as 1.31

### How can we reproduce it (as minimally and precisely as possible)?

- Deploy a 1.31 cluster
- upgrade to 1.32
- Observer memory usage on etcd

### Anything else we need to know?

A cluster that was created at v1.32 has an etcd `container_memory_working_set_bytes` of around 130 MB.
A v1.31 cluster is also around 130 MB. After the upgrade to v1.32 it increased to around 450 MB (Caused by a short increase in etcd_mvcc_db_total_size_in_use_in_bytes to 430 MB). `etcd_mvcc_db_total_size_in_bytes` permanently increased to 450 MB at upgrade time too. Over time some of the etcds saw an increase in `container_memory_working_set_bytes` to 600MB, but `etcd_mvcc_db_total_size_in_bytes` did not change.

When it was defragged the `etcd_mvcc_db_total_size_in_bytes` dropped to 11 MB (Which is just above the value of `etcd_mvcc_db_total_size_in_use_in_bytes` but `container_memory_working_set_bytes` only dropped to around 450MB.

After further investigation it requires a defrag, followed by restart of etcd pods to return the memory usage to normal after an update to v1.32.

### Kubernetes version

<details>

```console
$ kubectl version
Client Version: v1.31.1
Kustomize Version: v5.4.2
Server Version: v1.32.0-beta.0+IKS
```

</details>

### Cloud provider

<details>
IBM Cloud
</details>

### OS version

<details>

```console
# On Linux:
$ cat /etc/os-release
PRETTY_NAME= …[обрезано]
````

## Идея 6. API, принимающий от клиента схемы данных (пользовательские типы, JSON Schema, OpenAPI), принимает все документированные форматы (int32, int64, float, double и т. п.) без ложных предупреждений в заголовке Warning и теле ответа

### kubernetes/kubernetes#133880 — CRD validation warning on valid formats

Ссылка: https://github.com/kubernetes/kubernetes/issues/133880

- **Паттерн:** Схема с документированными форматами принимается без ложных предупреждений
- **Условие:** Загружаемая схема (определение пользовательского ресурса) использует форматы int32, int64, float, double для числовых полей
- **Действие:** Создать определение с такими форматами и проверить заголовки Warning и тело ответа
- **Ожидание:** Определение создаётся без предупреждений о неизвестном формате
- **Источник ожидания:** OpenAPI 3.0 §4.7.1 (Data Types); документация продукта
- **Почему не подошла ближайшая запись:** VAL-STRING-FORMAT проверяет значения по формату, а не ответ сервера на сами форматы в загружаемой схеме; направление позитивное

Первоисточник:

````text
### What happened?

In #132532 and #133136 a warning was added for unrecognized formats. However, the `int32`, `int64`, `float`, and `double` formats are flagged ~~and this conflicts with public docs: https://kubernetes.io/docs/tasks/extend-kubernetes/custom-resources/custom-resource-definitions/#format which say that these values are supported formats~~. I believe this is also unintended behavior because there are no other formats that support numbers.

```bash
❯ kubectl apply -f https://raw.githubusercontent.com/kro-run/kro/refs/heads/main/helm/crds/kro.run_resourcegraphdefinitions.yaml
Warning: unrecognized format "int32"
Warning: unrecognized format "int64"
customresourcedefinition.apiextensions.k8s.io/resourcegraphdefinitions.kro.run created
```

### What did you expect to happen?

I expect that applying CRDs containing with `int32`, `int64`, `float`, and `double` formats to be accepted without warnings

### How can we reproduce it (as minimally and precisely as possible)?

```yaml
# crd.yaml
---
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
  name: warningformats.example.com
spec:
  group: example.com
  names:
    kind: WarningFormat
    listKind: WarningFormatList
    plural: warningformats
    singular: warningformat
  scope: Cluster
  versions:
  - name: v1alpha1
    schema:
      openAPIV3Schema:
        description: WarningFormat is the Schema for the warningformats API
        properties:
          apiVersion:
            description: |-
              APIVersion defines the versioned schema of this representation of an object.
              Servers should convert recognized schemas to the latest internal value, and
              may reject unrecognized values.
              More info: https://git.k8s.io/community/contributors/devel/sig-architecture/api-conventions.md#resources
            type: string
          kind:
            description: |-
              Kind is a string value representing the REST resource this object represents.
              Servers may infer this from the endpoint the client submits requests to.
              Cannot be updated.
              In CamelCase.
              More info: https://git.k8s.io/community/contributors/devel/sig-architecture/api-conventions.md#types-kinds
            type: string
          metadata:
            type: object
          spec:
            description: WarningFormatSpec defines the desired state of
              WarningFormat
            properties:
          …[обрезано]
````

## Идея 7. Служебный эндпоинт текущей конфигурации (флаги запуска, flagz, configz, env) отражает фактически переданные значения; доступ к нему — по HARD-DEBUG-ENDPOINTS

### kubernetes/kubernetes#129994 — Flagz on kube-apiserver doesn't return parsed flag values

Ссылка: https://github.com/kubernetes/kubernetes/issues/129994

- **Паттерн:** Служебный эндпоинт конфигурации отражает фактические параметры запуска
- **Условие:** Сервис отдаёт эндпоинт с текущими значениями флагов запуска (flagz)
- **Действие:** Запустить сервис с заданными флагами и сравнить ответ эндпоинта с переданными значениями
- **Ожидание:** Каждое значение в ответе совпадает с переданным при запуске
- **Источник ожидания:** Документация функции; поведение соседних компонентов
- **Почему не подошла ближайшая запись:** OBS-HEALTH-ENDPOINTS проверяет состояние здоровья, HARD-DEBUG-ENDPOINTS — доступ извне; корректности данных служебного эндпоинта нет

Первоисточник:

````text
### What happened?

When ComponentFlagz feature is enabled on kube-apiserver, the flag value is not return as expected.
kube-apiserver spec
```yaml
spec:
  containers:
  - command:
    - kube-apiserver
    - --advertise-address=192.168.8.5
    - --feature-gates=ComponentFlagz=true
    - --emulated-version=1.32
    ...
```
The `flagz/` returns
```
~ curl -k --cert /etc/kubernetes/pki/apiserver-kubelet-client.crt --key /etc/kubernetes/pki/apiserver-kubelet-client.key https://localhost:6443/flagz

kube-apiserver flags
Warning: This endpoint is not meant to be machine parseable, has no formatting compatibility guarantees and is for debugging purposes only.

admission-control:[]
admission-control-config-file:
advertise-address:192.168.8.5
aggregator-reject-forwarding-redirect:true
allow-metric-labels:[]
...
...
egress-selector-config-file:
emulated-version:[]
enable-admission-plugins:[NodeRestriction]
...
...
feature-gates:
...
```

### What did you expect to happen?

The response reflects the correct passed flag value. For example in kube-scheduler
kube-scheduler spec:
```yaml
spec:
  containers:
  - command:
    - kube-scheduler
    - --authentication-kubeconfig=/etc/kubernetes/scheduler.conf
    - --feature-gates=ComponentFlagz=true
    - --emulated-version=1.32
   ...
```
The `/flagz` response:
```curl -k --cert /etc/kubernetes/pki/apiserver-kubelet-client.crt --key /etc/kubernetes/pki/apiserver-kubelet-client.key https://localhost:10259/flagz

kube-scheduler flags
Warning: This endpoint is not meant to be machine parseable, has no formatting compatibility guarantees and is for debugging purposes only.

allow-metric-labels:[]
allow-metric-labels-manifest:
authentication-kubeconfig:/etc/kubernetes/scheduler.conf
...
...
emulated-version:[1.32]
feature-gates::ComponentFlagz=true
...
```

### How can we reproduce it (as minimally and precisely as possible)?

1. Enable the featuregate on kube-apiserver with `--feature-gates=ComponentFlagz=true`
1. request the kube-apiserver endpoint on path `/flagz` and check the response

### Anything else we need to know?

I believe it is due to the flags (instantiated by `s.Flags()`) passed into the options 
https://github.com/kubernetes/kubernetes/blob/925cf7db71c5e36072f99e8b7129523f659ee3a1/cmd/kube-apiserver/app/options/completion.go#L60
is not the same one that actually used by the cmd
https://github.com/kubernetes/kubernetes/blob/925cf7db71c5e36072f99e8b7129523f659ee3a1/cmd/kube-apiserver/app/server.go#L126

### Kubern …[обрезано]
````

## Идея 8. Внешняя зависимость (вебхук преобразования, валидации, обогащения) вызывается только тогда, когда её результат нужен; лишних вызовов по счётчику на заглушке нет

### kubernetes/kubernetes#129979 — CRD conversion webhooks should not be called for unused apiVersions

Ссылка: https://github.com/kubernetes/kubernetes/issues/129979

- **Паттерн:** Внешний обработчик преобразования вызывается только когда преобразование нужно
- **Условие:** У типа несколько версий, преобразование между ними делает внешний вебхук, клиенты работают только с версией хранения
- **Действие:** Создать и изменить объекты в версии хранения и подсчитать запросы к вебхуку по исходной и целевой версиям
- **Ожидание:** Вызовов нет, пока клиент не запросит объект в другой версии
- **Источник ожидания:** Документация функции (преобразование по запросу); здравый смысл
- **Почему не подошла ближайшая запись:** PERF-* меряют задержку и нагрузку сервиса, а не лишние вызовы внешних зависимостей; BIZ-SIDE-EFFECTS-ONCE про бизнес-эффекты, а не служебные вызовы

Первоисточник:

````text
### What happened?

We have CRDs with multiple apiVersions. Even if the old (non-storage) apiVersions are not used at all we regularly receive conversion requests for them.

We roughly get 1 conversion request for each non-storage apiVersion per kube-apiserver instance for every CR create/update (actually a little bit less than that, but not sure why).

So if we have a CRD with 5 old apiVersions and a cluster with 3 kube-apiservers

=> we get roughly 15 conversion requests for every create/update on a CR (it's slightly less than that - not sure why though)

### What did you expect to happen?

I would expect to only get conversion requests when conversion is required, e.g. if a client requests a CR in a different apiVersion than the one in which the object is stored in etcd.

### How can we reproduce it (as minimally and precisely as possible)?

Create a Kubernetes cluster via kind
```
kind create cluster
```

Deploy the Cluster CRD
```
$ kubectl apply -f ./crd_cluster.yaml
```

<details>

<summary>crd_cluster.yaml</summary>

```yaml
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
  annotations:
    controller-gen.kubebuilder.io/version: v0.17.0
  name: clusters.cluster.x-k8s.io
spec:
  conversion:
    strategy: Webhook
    webhook:
      conversionReviewVersions: ["v1", "v1beta1"]
      clientConfig:
        service:
          namespace: system
          name: webhook-service
          path: /convert
  group: cluster.x-k8s.io
  names:
    kind: Cluster
    listKind: ClusterList
    plural: clusters
    singular: cluster
  scope: Namespaced
  versions:
  - deprecated: true
    name: v1alpha3
    schema:
      openAPIV3Schema:
        properties:
          spec:
            properties:
              paused:
                type: boolean
            type: object
        type: object
    served: false
    storage: false
  - deprecated: true
    name: v1alpha4
    schema:
      openAPIV3Schema:
        properties:
          spec:
            properties:
              paused:
                type: boolean
            type: object
        type: object
    served: true
    storage: false
  - name: v1beta1
    schema:
      openAPIV3Schema:
        properties:
          spec:
            properties:
              paused:
                type: boolean
            type: object
        type: object
    served: true
    storage: true
```

</details>

Deploy the Cluster CR
```
$ kubectl apply -f ./cr_cluster.yaml
```

<details>

<summary>cr_ …[обрезано]
````

## Идея 9. Ресурс, заданный в устаревшей форме и переведённый на новую реализацию (migration), обрабатывается теми же правилами — права, выдача токенов, ограничения, — что и ресурс в новой форме

### kubernetes/kubernetes#129935 — CSI migration with in-tree azure-file provider fails to mount PVC to Pod

Ссылка: https://github.com/kubernetes/kubernetes/issues/129935

- **Паттерн:** Проверка прав учитывает ресурсы устаревшего типа, переведённые на новую реализацию
- **Условие:** Ресурс задан в устаревшей форме (встроенный тип тома), а обслуживается новой реализацией (CSI-драйвер) с разрешёнными аудиториями токена
- **Действие:** Создать ресурс устаревшего типа, переведённого на новый драйвер, и запросить токен с аудиторией, которую разрешает этот драйвер
- **Ожидание:** Токен выдаётся так же, как для ресурса, заданного сразу в новой форме
- **Источник ожидания:** Документация миграции; здравый смысл
- **Почему не подошла ближайшая запись:** SEC-TOKEN-AUDIENCE — негативная проверка отказа чужой аудитории; здесь законный запрос отклоняется из-за неучтённой устаревшей формы ресурса

Первоисточник:

````text
### What happened?

When mounting PVC to the Pod the volume will not mount and it will hang on
```
MountVolume.SetUp failed for volume "pvc-d9734ad3-26f5-4fb9-8918-7643d2bf8c75" : kubernetes.io/csi: mounter.SetUpAt failed to get service accoount token attributes: failed to fetch token: serviceaccounts "default" is forbidden: audience "api://AzureADTokenExchange" not found in pod spec volume
```

### What did you expect to happen?

Volume mounted successfully with Pod running.

### How can we reproduce it (as minimally and precisely as possible)?

1. Create Azure cluster with Kubernetes 1.32
2. Create PV claim
```yaml
kind: StorageClass
apiVersion: storage.k8s.io/v1
metadata:
  name: my-pv-claim 
provisioner: kubernetes.io/azure-file
parameters:
  skuName: Standard_LRS 
reclaimPolicy: Delete
volumeBindingMode: Immediate
```
3. Create Pod and mount PVC

### Anything else we need to know?

The error comes from https://github.com/kubernetes/kubernetes/blob/master/plugin/pkg/admission/noderestriction/admission.go#L654
which was introduced in https://github.com/kubernetes/kubernetes/pull/128077

Admission plugin will work for CSI
https://github.com/openshift/kubernetes/blob/master/plugin/pkg/admission/noderestriction/admission.go#L689-L690

But when using CSI migration with in-tree azure-file provider the PVC fails to mount.
https://github.com/kubernetes/kubernetes/blob/master/staging/src/k8s.io/api/core/v1/types.go#L141

CSIdriver contents
```yaml
apiVersion: storage.k8s.io/v1
kind: CSIDriver
metadata:
  annotations:
    csi.openshift.io/managed: "true"
    operator.openshift.io/spec-hash: 5c303d28061bd64a18ff9b79bd6b231293b3c1295db37e91d59160efe4611365
  creationTimestamp: "2025-01-31T13:10:35Z"
  labels:
    security.openshift.io/csi-ephemeral-volume-profile: privileged
  name: file.csi.azure.com
  resourceVersion: "9671"
  uid: 15b2ad34-60dc-4765-97cb-b91613dfa6d7
spec:
  attachRequired: false
  fsGroupPolicy: None
  podInfoOnMount: true
  requiresRepublish: false
  seLinuxMount: false
  storageCapacity: false
  tokenRequests:
  - audience: api://AzureADTokenExchange
  volumeLifecycleModes:
  - Persistent
  - Ephemeral 
```

### Kubernetes version

<details>

```console
$ kubectl version
Client Version: v1.32.1
Kustomize Version: v5.4.2
Server Version: v1.32.1
```

</details>

### Cloud provider

<details>
Azure
</details>

### OS version

<details>

```console
# On Linux:
$ cat /etc/os-release
# paste output here
$ uname -a
# paste output here

# On Windows …[обрезано]
````

## Идея 10. После ужесточения правил валидации сохранённые ранее значения, которые им не соответствуют, обрабатываются одинаково на всех путях записи (основной эндпоинт, подресурс status, PATCH/PUT) — по документированному правилу (не перепроверять неизменённое или требовать исправления), без расхождения между путями

### kubernetes/kubernetes#129503 — Ratcheting validation missing for CRD status subresources

Ссылка: https://github.com/kubernetes/kubernetes/issues/129503

- **Паттерн:** Послабление валидации для неизменённых сохранённых значений действует на всех путях записи
- **Условие:** Схема ужесточена после сохранения объекта (pattern заменён на enum), сохранённые значения в spec и status ей не соответствуют
- **Действие:** Изменить другое поле объекта через основной эндпоинт и другое поле status через подресурс status, не трогая несоответствующие значения
- **Ожидание:** Оба обновления проходят: неизменённые старые значения не перепроверяются
- **Источник ожидания:** Документация функции (validation ratcheting)
- **Почему не подошла ближайшая запись:** Нет записи о послаблении валидации для сохранённых данных и одинаковом её применении на разных путях записи; VAL-DEFERRED-FAILURE про 5xx

Первоисточник:

````text
### What happened?

Testing the new CRD [ratcheting validation](https://kubernetes.io/docs/tasks/extend-kubernetes/custom-resources/custom-resource-definitions/#validation-ratcheting) feature, I implemented a change of validation from `pattern` to `enum` in both a `spec` and `status` field on a CRD. Note, this CRD includes a status subresource.

I created the CRD with the `pattern` validation on the fields initially and then created a CR with field values in spec and status that matched the pattern, but did not match my intended enum.

Editing the CRD now to move to the `enum`, this would invalidate the stored data in the two fields, meaning ratcheting is required.

Updating fields such as metadata (adding an annotation) or other spec fields worked correctly, and no issues were returned.

Trying to update any status field using the status subresource path failed, complaining that my field did not match the expected enum.

### What did you expect to happen?

Values to the status should be ratcheted in the same way that the based endpoint is ratcheted.

### How can we reproduce it (as minimally and precisely as possible)?

1. Create a minimal CRD with a status subresource and a field with a pattern validation (and another field for testing)
2. Persist a CR with a value that does not match the pattern.
3. Update the CRD schema to move from `pattern` to `enum` with a value that does not match the persisted CR.
4. Update an annotation, observe success
5. Update the other CRD status field with a new value, observe that it errors complaining about the enum value being incorrect.

### Anything else we need to know?

Neither the [documentation](https://kubernetes.io/docs/tasks/extend-kubernetes/custom-resources/custom-resource-definitions/#validation-ratcheting) nor the [KEP](https://github.com/kubernetes/enhancements/tree/master/keps/sig-api-machinery/4008-crd-ratcheting) suggest that there should be any difference in behaviour.

I raised this [on slack](https://kubernetes.slack.com/archives/C0EG7JC6T/p1736187102623779) and it was suggested that this was a bug.

Looking at the code, I can see [ratcheting options](https://github.com/kubernetes/apiextensions-apiserver/blob/d72b6f721f9b3cf655cb545e59cfb5f4bc615b8f/pkg/registry/customresource/strategy.go#L287-L291) on the storage for the main path, but not in the [status strategy](https://github.com/kubernetes/apiextensions-apiserver/blob/d72b6f721f9b3cf655cb545e59cfb5f4bc615b8f/pkg/registry/customreso …[обрезано]
````

## Идея 11. Идентичность содержит одинаковый набор атрибутов (UID, группы, extra) при любом способе аутентификации, если источник их содержит (UID из сертификата X.509, claims OIDC); сравнение через «кто я»; пара к AUTH-ACCOUNT-STATE-ALL-SCHEMES

### kubernetes/kubernetes#127860 — x509 clients missing User.Uid info for authorization and admission

Ссылка: https://github.com/kubernetes/kubernetes/issues/127860

- **Паттерн:** Идентичность содержит одинаковый набор атрибутов при любом способе аутентификации
- **Условие:** Поддерживаются несколько способов аутентификации (токен, OIDC, клиентский сертификат X.509 с полем UID)
- **Действие:** Аутентифицироваться каждым способом и запросить «кто я», сравнить атрибуты
- **Ожидание:** UID и прочие атрибуты присутствуют, если источник их содержит (UID из сертификата)
- **Источник ожидания:** Поведение других способов аутентификации; здравый смысл
- **Почему не подошла ближайшая запись:** SEC-AUTHN-SCHEMES-SUPPORTED проверяет, что схемы принимаются, а не одинаковый набор атрибутов идентичности

Первоисточник:

````text
### What happened?

For all other authenticator types, the authenticator supplies a UID for the user. When an authorizer or admission validator evaluates a request, the uid for x509 users is an empty string.

### What did you expect to happen?

I expected a UID to be populated by the x509 authenticator if set in the certificate. I'd also expect `kubeadm` to have a flag in the `kubeadm kubeconfig user` subcommand to support setting it like `--client-name` and `--org` populate username and groups respectively, so something like `--client-uid`. 

For Kubernetes-created node client certs should probably have the node object's `uid`. Other client x509 certs such as Kube-apiserver client cert for node proxy or client certs from the CSR  API, its not clear if/what Kubernetes should set. 


### How can we reproduce it (as minimally and precisely as possible)?

1. Create a [kind](https://kind.sigs.k8s.io/) cluster
2. Run `kubectl auth whoami`. No UID is returned as it is for other auth formats

```
kubectl auth whoami
ATTRIBUTE   VALUE
Username    kubernetes-admin
Groups      [kubeadm:cluster-admins system:authenticated]
```

### Anything else we need to know?

As [discussed in #sig-auth](https://kubernetes.slack.com/archives/C0EN96KUY/p1727984474325949), x509 has an optional field for UID. Go's `crypto/x509` doesn't have a named field for it, but it can be set or accessed. 

### Kubernetes version

All versions

### Cloud provider

N/A

### OS version

N/A

### Install tools

_No response_

### Container runtime (CRI) and version (if applicable)

_No response_

### Related plugins (CNI, CSI, ...) and versions (if applicable)

_No response_
````

## Идея 12. Значение, выделенное объекту из пула (адрес, номер, уникальное имя), не выдаётся повторно, пока прежний владелец не удалён окончательно (отложенное удаление, финализаторы, мягкое удаление); дублей нет

### kubernetes/kubernetes#127792 — kube-controller-manager re-allocating already used PodCIDR (v1.31)

Ссылка: https://github.com/kubernetes/kubernetes/issues/127792

- **Паттерн:** Ресурс из пула не выдаётся повторно, пока прежний владелец не удалён полностью
- **Условие:** Сервер выделяет объектам значения из пула (диапазоны адресов), прежний владелец помечен на удаление, но ещё существует (финализаторы)
- **Действие:** Начать удаление объекта с выделенным значением, сразу создать новые объекты и проверить уникальность выделенных значений
- **Ожидание:** Значение освобождается только после окончательного удаления, дублей нет
- **Источник ожидания:** Здравый смысл
- **Почему не подошла ближайшая запись:** CONC-PARALLEL-CREATE-UNIQUE про уникальный ключ при параллельном создании; повторная выдача значения из пула при отложенном удалении владельца не покрыта

Первоисточник:

````text
### What happened?

Since upgrading to Kubernetes v1.31 we have occasional observed that `kube-controller-manager` allocates a PodCIDR for a new node which is already allocated for an existing node in the cluster. We have about 200 clusters with a combined number of ca. 6k-10k nodes (autoscaling). It has happened about 10 times since upgrading a week ago, so it's rather rare but breaks the networking between the affected nodes when it happens.

We use flannel as overlay network and it uses the podCIDR assigned by `kube-controller-manager`. When a new node gets an existing podCIDR assigned, then the new node doesn't get ready and it gets terminated after 10 min. We check that the node is routable by all other nodes before we mark the node ready. This never happens because the podCIDR already points to another node in the cluster. When the new node is deleted it has the very unfortunate side effect that all flannels detect the node is deleted and they delete the routes for the podCIDR, problem is just that most nodes will have routes for the other node with the same podCIDR and this then stops working.

Terminating the affected node is the best way to resolve the issue but obviously not sustainable.

### What did you expect to happen?

`kube-controller-manager` should _never_ allocate the same podCIDR to multiple nodes at the same time.

### How can we reproduce it (as minimally and precisely as possible)?

We haven't found a predictable way to reproduce it.

We run with the pod CIDR range: `10.2.0.0/15`.

### Anything else we need to know?

This is how we configure `kube-controller-manager`: https://github.com/zalando-incubator/kubernetes-on-aws/blob/dev/cluster/node-pools/master-default/userdata.yaml#L581-L648 (the image is vanilla Kubernetes built from source and hosted in a private registry)

Here is an example from one cluster with logs:

*Node 1 (original)*:
name: `ip-172-31-14-210.eu-central-1.compute.internal`
podCIDR: `10.2.4.0/24`

*Node 2 (new)*:
name: `ip-172-31-15-241.eu-central-1.compute.internal`
podCIDR: `10.2.4.0/24`

`kube-controller-manager`  logs filtered for the node `ip-172-31-14-210.eu-central-1.compute.internal`:

```
I1001 16:54:22.944453       1 actual_state_of_world.go:540] "Failed to update statusUpdateNeeded field in actual state of world" logger="persistentvolume-attach-detach-controller" err="Failed to set statusUpdateNeeded to needed true, because nodeName=\"ip-172-31-14-210.eu-central-1.comp …[обрезано]
````

## Индекс библиотеки

Все записи (445): ID | категория | заголовок.

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
RESIL-ENCRYPTION-KEY-ROTATION | resilience | Нерасшифровываемое после смены ключа значение не ломает чтение и сохранение остальных данных
RESIL-GRACEFUL-SHUTDOWN | resilience | Перезапуск экземпляра не обрывает выполняющиеся запросы
RESIL-PARTIAL-DEGRADATION | resilience | Отказ некритичной зависимости не ломает основной функционал
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
