# Кандидаты из баг-трекеров: партия `keycloak`

Сгенерировано `tools/mining/cluster.py` из `build/mining/<batch>/batches/*.out.jsonl` и
`ideas/mined/keycloak.review.yaml` — правки решений делаются в review-файле, затем пересборка.
План — `docs/BUG_MINING_PLAN.md`, шаги 6–7; применение — `tools/mining/apply_proofs.py`.

## Сводка

- Новых паттернов: 15 → идей: 13 (принять: 11, отклонить: 2, не решено: 0).
- Пруфы к существующим: 89 багов → 65 записей; новых шагов-вариантов: 84.

## Новые идеи

Принятые становятся записями `status: draft` с меткой `real-world-bug` и ссылкой на RWB.

| # | Решение | Запись / файл | Идея | Подтверждающие баги |
|---|---|---|---|---|
| 1 | accept | `CONTRACT-GENERATED-URI-ENCODING` (RWB-0341)<br>`checks/common/contract.yaml` | URI, которые формирует сервер (otpauth, ссылки в письмах, Location, redirect), кодируют значения по правилам своей части (пробел — %20 в пути, + только в query по форме) — после декодирования значение совпадает с исходным | [keycloak/keycloak#52296](https://github.com/keycloak/keycloak/issues/52296) |
| 2 | accept | `BIZ-IMPOSSIBLE-STEP-NOT-ASSIGNED` (RWB-0342)<br>`checks/common/business-logic.yaml` | Обязательный шаг процесса (подтверждение email, смена пароля, настройка второго фактора) не назначается пользователю, который не может его выполнить (нет email, нет нужного канала), — законная операция не блокируется невыполнимым шагом; позитивная пара к BIZ-WORKFLOW-STEP-SKIP | [keycloak/keycloak#48634](https://github.com/keycloak/keycloak/issues/48634) |
| 3 | accept | `AUTH-MULTISTEP-LOGIN-STATE-RECHECK` (RWB-0343)<br>`checks/security/authentication-session.yaml` | Если во время многошагового входа (обязательные действия, второй фактор, согласие) пользователя или клиента отключили, последний шаг проверяет их состояние заново — понятная ошибка «отключён», токен не выдаётся, 5xx нет | [keycloak/keycloak#48487](https://github.com/keycloak/keycloak/issues/48487), [keycloak/keycloak#46738](https://github.com/keycloak/keycloak/issues/46738) |
| 4 | accept | `AUTH-PRE-ACCOUNT-TAKEOVER` (RWB-0344)<br>`checks/security/authentication-session.yaml` | Регистрация на чужой email с живой незавершённой сессией не даёт входа в аккаунт после того, как владелец сбросил пароль и подтвердил email, — подтверждение и сброс завершают чужие незавершённые сессии регистрации (pre-account takeover) | [keycloak/keycloak#48206](https://github.com/keycloak/keycloak/issues/48206), [keycloak/keycloak#45568](https://github.com/keycloak/keycloak/issues/45568) |
| 5 | accept | `RES-TYPED-PATH-LOOKUP` (RWB-0345)<br>`checks/common/resource-lifecycle.yaml` | Операция, где тип ресурса задан в пути (/{type}/{id}), находит идентификатор среди объектов указанного типа для каждого поддерживаемого типа — позитивная матрица по типам; объект другого типа с тем же id не подставляется | [keycloak/keycloak#48094](https://github.com/keycloak/keycloak/issues/48094) |
| 6 | accept | `RESIL-TOKENS-SURVIVE-RESTART` (RWB-0346)<br>`checks/common/resilience.yaml` | Выданные токены остаются действительными после перезапуска сервера (и между экземплярами) — идентификатор ключа подписи (kid) стабилен, ключ публикуется в JWKS, интроспекция и userinfo принимают токен до истечения | [keycloak/keycloak#47495](https://github.com/keycloak/keycloak/issues/47495) |
| 7 | accept | `AUTH-LOGIN-PARAMS-PRESERVED` (RWB-0347)<br>`checks/security/authentication-session.yaml` | Параметры входа, заданные на первом шаге (запомнить меня, locale, scope, prompt), сохраняются через все шаги аутентификации (выбор организации, второй фактор) и влияют на результат — длительная сессия и cookie remember me при rememberMe | [keycloak/keycloak#47017](https://github.com/keycloak/keycloak/issues/47017) |
| 8 | accept | `AUTH-TOKEN-EXCHANGE-DEFAULT-SCOPE` (RWB-0348)<br>`checks/security/authentication-session.yaml` | Обмен токена (RFC 8693) без явного scope выдаёт области по умолчанию клиента, запросившего обмен, по документированному правилу — не области исходного или другого клиента | [keycloak/keycloak#45716](https://github.com/keycloak/keycloak/issues/45716) |
| 9 | accept | `BIZ-RULES-DETERMINISTIC` (RWB-0349)<br>`checks/common/business-logic.yaml` | Итог нескольких правил над одним значением в одном запросе (маппинг групп и ролей при входе, правила скидок, политики) детерминирован и соответствует документированному приоритету — повтор операции даёт тот же результат | [keycloak/keycloak#44480](https://github.com/keycloak/keycloak/issues/44480) |
| 10 | accept | `SEC-ROLE-IDENTITY-NOT-NAME` (RWB-0350)<br>`checks/security/access-control/SEC-ROLE-IDENTITY-NOT-NAME.yaml` | Ограничения системных и административных ролей применяются по идентичности роли (id, область), а не по совпадению имени — пользовательская роль с таким же именем назначается законно, настоящая административная — по правилам | [keycloak/keycloak#43578](https://github.com/keycloak/keycloak/issues/43578) |
| 11 | accept | `AUTH-OIDC-LOGOUT-WITHOUT-SESSION` (RWB-0351)<br>`checks/security/authentication-session.yaml` | Выход по OIDC (RP-Initiated Logout) без активной сессии на сервере — истекла, offline-доступ, вход через внешний IdP — с валидным id_token_hint и зарегистрированным post_logout_redirect_uri завершается перенаправлением на него без ошибки; недоверенный URI по-прежнему отклоняется | [keycloak/keycloak#46379](https://github.com/keycloak/keycloak/issues/46379) |
| 12 | reject | отклонено: Перекрёстное ревью (все три модели) — допустимость client_id ≠ sub зависит от модели доверия федерации (Kubernetes service accounts); правило не универсально и спорит с AUTH-CLIENT-ASSERTION-BINDING | Client assertion с client_id внутреннего клиента и внешним sub принимается | [keycloak/keycloak#48024](https://github.com/keycloak/keycloak/issues/48024) |
| 13 | reject | отклонено: Перекрёстное ревью (Gemini, Qwen) — маркер «+» в webOrigins — специфика Keycloak; общая часть покрыта VAL-STRING-FORMAT | Специальное значение-маркер в поле URI принимается проверкой формата | [keycloak/keycloak#45587](https://github.com/keycloak/keycloak/issues/45587) |

## Пруфы к существующим

Запись получает метку `real-world-bug` и `Real-world bug: RWB-NNNN`; статус не меняется. Для `extends`
текст варианта добавляется шагом (`steps[].action`, в `notes` — RWB). Неверное совпадение — ID бага в
`proofs.exclude`, вариант без нового шага — в `proofs.no_variant`.

### AUTH-BRUTE-FORCE-PROTECTION — Перебор паролей ограничивается (RWB-0056, багов: 2)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [keycloak/keycloak#46634](https://github.com/keycloak/keycloak/issues/46634) | extends | Сделать неудачные попытки, дождаться сброса счётчика по времени, повторить и проверить, что счётчик и время последней ошибки ведут себя как в первом цикле |
| [keycloak/keycloak#44474](https://github.com/keycloak/keycloak/issues/44474) | extends | Несколько раз войти с верным паролем при превышенном лимите сессий и проверить, что учётка не блокируется защитой от перебора |

### AUTH-CLIENT-CERT-IDENTITY — Личность из сертификата клиента извлекается однозначно (RWB-0187, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [keycloak/keycloak#46647](https://github.com/keycloak/keycloak/issues/46647) | extends | Передать через прокси цепочку клиентских сертификатов длиннее настроенной — используются первые N, аутентификация по сертификату проходит |

### AUTH-JWT-ALG-NONE — JWT с alg=none отклоняется (RWB-0352, багов: 2)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [keycloak/keycloak#48744](https://github.com/keycloak/keycloak/issues/48744) | extends | Отправить JWT с alg=none на каждый эндпоинт с Bearer-аутентификацией (в том числе userinfo) и проверить 401, а не 5xx |
| [keycloak/keycloak#48137](https://github.com/keycloak/keycloak/issues/48137) | extends | Передать неподписанный JWT в параметре ссылки-действия и ожидать 4xx без 5xx и без исключения в журнале |

### AUTH-JWT-TIME-CLAIMS — Токены с nbf/iat в будущем и без exp обрабатываются по политике (RWB-0291, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [keycloak/keycloak#46303](https://github.com/keycloak/keycloak/issues/46303) | extends | Отправить assertion с iat в прошлом в пределах настроенного максимального возраста и ожидать, что оно принимается |

### AUTH-LOGOUT-INVALIDATES — После выхода токен и сессия недействительны (RWB-0059, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [keycloak/keycloak#43853](https://github.com/keycloak/keycloak/issues/43853) | extends | Выполнить выход по id_token_hint без cookie сразу после входа и проверить, что следующий вход создаёт новую сессию аутентификации, а не продолжает прежнюю |

### AUTH-OAUTH-PAR — Pushed Authorization Request действует как прямой запрос авторизации и не ограничивает длительность входа (RWB-0020, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [keycloak/keycloak#46926](https://github.com/keycloak/keycloak/issues/46926) | extends | Включить у клиента требование request_uri only и отправить PAR без request_uri — запрос должен быть принят по RFC 9126 §2.1 |

### AUTH-OAUTH-REDIRECT-STATE — OAuth/OIDC flow проверяет redirect_uri, state и PKCE (RWB-0061, багов: 2)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [keycloak/keycloak#48430](https://github.com/keycloak/keycloak/issues/48430) | extends | Зарегистрировать redirect_uri со * сразу после имени хоста и отправить redirect_uri с тем же префиксом в другом домене (app.example.com.evil.com) — должен быть отклонён |
| [keycloak/keycloak#51315](https://github.com/keycloak/keycloak/issues/51315) | extends | Сохранить клиент с корректным redirect URI через административный API — принимается; отказ — только для адресов, нарушающих политику, с указанием отвергнутого значения |

### AUTH-REFRESH-PRESERVES-SCOPE — Refresh без параметра scope сохраняет scope исходной авторизации (RWB-0018, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [keycloak/keycloak#47776](https://github.com/keycloak/keycloak/issues/47776) | extends | Обновить offline refresh-токен с параметром scope без offline_access, завершить онлайн-сессию и проверить, что новый access-токен принимается userinfo |

### AUTH-SESSION-FIXATION — Идентификатор сессии меняется после входа (RWB-0191, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [keycloak/keycloak#46239](https://github.com/keycloak/keycloak/issues/46239) | extends | Войти пользователем A, затем в том же клиенте с той же cookie сессии аутентификации войти пользователем B и проверить, что sid токенов B отличается от A |

### AUTH-SESSION-TIMEOUT — Сессия истекает после простоя и абсолютного срока (RWB-0063, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [keycloak/keycloak#43328](https://github.com/keycloak/keycloak/issues/43328) | extends | Создать сессию с «запомнить меня», выключить эту настройку и проверить, что сессия истекает по обычному сроку |

### AUTH-TOKEN-SENDER-CONSTRAINED — Обмен и обновление токена сохраняют привязку к отправителю (DPoP, mTLS) (RWB-0044, багов: 2)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [keycloak/keycloak#48428](https://github.com/keycloak/keycloak/issues/48428) | extends | Запросить токены по implicit и hybrid flow у клиента с обязательной привязкой DPoP и проверить отказ unauthorized_client |
| [keycloak/keycloak#43505](https://github.com/keycloak/keycloak/issues/43505) | extends | Повторно отправить тот же DPoP-proof с iat в будущем в пределах допуска рассинхрона часов и ожидать отказ как повтор |

### AUTH-USER-ENUMERATION — Ответы входа, регистрации и восстановления не раскрывают существование аккаунта (RWB-0193, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [keycloak/keycloak#46517](https://github.com/keycloak/keycloak/issues/46517) | extends | Отправить неверный пароль для отключённой учётки через каждый поток входа (форма, password grant) и проверить одинаковую ошибку без раскрытия статуса |

### BIZ-EMAIL-LINK-CROSS-SESSION — Ссылка-действие из письма работает в другой сессии и после перезапуска сервиса (RWB-0017, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [keycloak/keycloak#44488](https://github.com/keycloak/keycloak/issues/44488) | extends | Завершить действие по ссылке из письма, запущенное запросом авторизации, и проверить, что перенаправление на callback содержит code и state исходного запроса |

### BIZ-FLAG-EFFECT-MATRIX — Каждый флаг сущности влияет на поведение так, как описано (RWB-0353, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [keycloak/keycloak#44257](https://github.com/keycloak/keycloak/issues/44257) | extends | Включить флаг изменением существующего объекта, а не при создании (в том числе через DCR), — зависимые объекты создаются так же, при выключении — удаляются |

### BIZ-LIMITS-QUOTAS — Лимиты и квоты соблюдаются на границе и не обходятся параллельно (RWB-0293, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [keycloak/keycloak#48040](https://github.com/keycloak/keycloak/issues/48040) | extends | Превысить общий лимит через одного клиента и выполнить операцию через другого, у которого частный лимит не превышен, — проверить поведение по политике без 5xx |

### CONC-DELETE-VS-UPDATE — Параллельные удаление и изменение не оставляют ресурс в противоречивом состоянии (RWB-0354, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [keycloak/keycloak#45561](https://github.com/keycloak/keycloak/issues/45561) | extends | Удалять правила доступа параллельно с запросами оценки разрешений и проверять, что оценка не возвращает 5xx |

### CONC-PARALLEL-INDEPENDENT — Параллельные независимые запросы одной операции выполняются без 5xx (RWB-0008, багов: 2)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [keycloak/keycloak#53238](https://github.com/keycloak/keycloak/issues/53238) | extends | Отправить параллельно несколько первых запросов одного ресурса с Accept-Encoding: gzip на холодном кэше и проверить, что все получают 200 с телом |
| [keycloak/keycloak#46172](https://github.com/keycloak/keycloak/issues/46172) | extends | Параллельно удалить несколько независимых арендаторов и ожидать успешные ответы без 5xx |

### CONTRACT-FIELD-SELECTION — Выбор полей возвращает ровно запрошенные поля с правильными значениями (RWB-0026, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [keycloak/keycloak#46296](https://github.com/keycloak/keycloak/issues/46296) | extends | Запросить список с параметром краткого представления и проверить отсутствие полей полного представления (атрибуты, служебные поля) |

### CONTRACT-PUBLISHED-SCHEMA-VALID — Опубликованные сервисом описания API валидны в заявленном диалекте (RWB-0049, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [keycloak/keycloak#46015](https://github.com/keycloak/keycloak/issues/46015) | covered | _только пруф_: Запись проверяет валидность опубликованных описаний API |

### CONTRACT-REQUIRED-FIELDS — Successful response contains required contract fields (RWB-0314, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [keycloak/keycloak#47452](https://github.com/keycloak/keycloak/issues/47452) | extends | Развернуть объект с описанием в дескрипторе и проверить, что список типов и созданный объект возвращают это описание |

### ERR-STABLE-ERROR-CODES — Машиночитаемые коды ошибок стабильны и задокументированы (RWB-0315, багов: 3)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [keycloak/keycloak#48721](https://github.com/keycloak/keycloak/issues/48721) | extends | Отправить на эндпоинт интроспекции неверные учётные данные клиента и проверить error=invalid_client по RFC 7662 §2.3 |
| [keycloak/keycloak#43270](https://github.com/keycloak/keycloak/issues/43270) | extends | Отправить запрос на эндпоинты token и backchannel-аутентификации без client_assertion от клиента с private_key_jwt и ожидать error=invalid_client |
| [keycloak/keycloak#43269](https://github.com/keycloak/keycloak/issues/43269) | extends | _только пруф_: Тот же вариант, что у keycloak/keycloak#43270 (эндпоинт токена) — только пруф |

### HARD-DEBUG-ENDPOINTS — Отладочные и служебные эндпоинты недоступны извне (RWB-0075, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [keycloak/keycloak#44132](https://github.com/keycloak/keycloak/issues/44132) | extends | Запустить сервер с настройками по умолчанию и проверить, что экспериментальные (preview) функции и их эндпоинты недоступны |

### HARD-EXCESSIVE-DATA-EXPOSURE — Ответы не содержат внутренних полей сверх контракта (RWB-0076, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [keycloak/keycloak#47036](https://github.com/keycloak/keycloak/issues/47036) | extends | Найти другого пользователя через эндпоинт предоставления доступа к ресурсу и проверить, что ответ содержит только идентификационные поля без атрибутов и служебных полей |

### HTTP-ABSOLUTE-URL-BASE-PATH — Абсолютные URL, которые формирует сервер, учитывают публичный адрес и базовый путь (RWB-0027, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [keycloak/keycloak#43166](https://github.com/keycloak/keycloak/issues/43166) | extends | Запросить discovery через прокси с префиксом пути при динамическом backend-адресе и проверить, что token_endpoint и другие backend-адреса содержат базовый путь |

### HTTP-ACCEPT-LANGUAGE — Язык сообщений определяется Accept-Language с fallback (RWB-0324, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [keycloak/keycloak#53999](https://github.com/keycloak/keycloak/issues/53999) | extends | Отправить параметр выбора языка с неподдерживаемым значением и проверить, что cookie языка не установлена и не изменена |

### HTTP-UNKNOWN-ROUTE — Неизвестный маршрут возвращает 404, а не 5xx или 200 (RWB-0336, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [keycloak/keycloak#48806](https://github.com/keycloak/keycloak/issues/48806) | extends | Запросить эндпоинт функции, отключённой в конфигурации сервера, и проверить 404, а не 5xx |

### INJ-LOG-FORGING — Пользовательские данные не позволяют подделывать записи журналов (RWB-0083, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [keycloak/keycloak#47681](https://github.com/keycloak/keycloak/issues/47681) | extends | Отправить в параметре, который попадает в журнал, ANSI escape-последовательности (\u001b[32m) и управляющие символы 0–31 и проверить, что в журнале они экранированы |

### INJ-SSRF-PARAMETERS — Параметры с URL и хостами не дают доступа к внутренней сети (RWB-0090, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [keycloak/keycloak#45694](https://github.com/keycloak/keycloak/issues/45694) | extends | Задать URL, к которому сервер дописывает путь, с «;» или «?» в конце и проверить, что исходящий запрос не уходит на произвольный путь |

### INJ-STORED-XSS — Сохранённые данные с HTML/JS не создают XSS у потребителей API (RWB-0244, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [keycloak/keycloak#48241](https://github.com/keycloak/keycloak/issues/48241) | extends | Сохранить в настраиваемом тексте (сообщение, заголовок) кавычку и </script> и проверить, что страница, встраивающая его в JavaScript, экранирует значение для JS-контекста |

### OBS-AUDIT-TRAIL — Чувствительные действия фиксируются в журнале аудита (RWB-0092, багов: 2)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [keycloak/keycloak#48645](https://github.com/keycloak/keycloak/issues/48645) | extends | Выполнить каждую операцию одного типа события (создание, приглашение, удаление) и проверить, что событие аудита содержит объект и детали пользователя одинаково |
| [keycloak/keycloak#46792](https://github.com/keycloak/keycloak/issues/46792) | extends | Выполнить создание, изменение и удаление через каждую версию API и проверить, что для каждой операции создаётся событие аудита |

### PAGE-SEARCH-SPECIAL-CHARS — Поиск со спецсимволами и wildcard не ломается и не расширяет выборку (RWB-0094, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [keycloak/keycloak#44678](https://github.com/keycloak/keycloak/issues/44678) | extends | Выполнить поиск со строками «_», «%», «*» в каждом эндпоинте поиска (пользователи, группы, члены организации) и проверить одинаковую обработку |

### PAGE-TOTAL-COUNT — Общее число элементов согласовано с суммой страниц (RWB-0095, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [keycloak/keycloak#45219](https://github.com/keycloak/keycloak/issues/45219) | extends | Вызвать эндпоинт количества и список с каждым параметром фильтра (в том числе exact=true) и проверить совпадение чисел |

### PERF-LATENCY-BASELINE — Задержка ключевых операций в пределах SLO при обычной нагрузке (RWB-0096, багов: 3)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [keycloak/keycloak#47157](https://github.com/keycloak/keycloak/issues/47157) | extends | Измерить задержку чтения эффективных ролей пользователя при сотнях и тысячах ролей в системе и проверить, что она не растёт пропорционально общему числу ролей |
| [keycloak/keycloak#47139](https://github.com/keycloak/keycloak/issues/47139) | extends | Изменить настройку, сбрасывающую кэш, в инсталляции с сотнями арендаторов и проверить, что время ответа не растёт с их числом |
| [keycloak/keycloak#46542](https://github.com/keycloak/keycloak/issues/46542) | extends | Обновить объект, связанный с тысячами других, без изменения влияющего на связи свойства и сравнить время с обновлением обычного объекта |

### RES-CREATE-RESPONSE-MATCHES-READ — Ответ на создание и изменение совпадает с последующим чтением (RWB-0101, багов: 3)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [keycloak/keycloak#44586](https://github.com/keycloak/keycloak/issues/44586) | extends | Создать объект со всеми полями представления и проверить, что чтение возвращает каждое переданное значение |
| [keycloak/keycloak#44403](https://github.com/keycloak/keycloak/issues/44403) | extends | Зарегистрировать клиента с token_endpoint_auth_method=client_secret_post и проверить, что ответ и чтение содержат запрошенный метод |
| [keycloak/keycloak#48432](https://github.com/keycloak/keycloak/issues/48432) | extends | Задать независимые логические флаги ресурса противоположными значениями и проверить, что повторное (кэшированное) чтение возвращает каждое сохранённое значение |

### RES-DELETE-WITH-DEPENDENTS — Удаление ресурса с зависимыми объектами выполняется по правилам каскада (RWB-0102, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [keycloak/keycloak#43516](https://github.com/keycloak/keycloak/issues/43516) | extends | Удалить объект с миллионами зависимых записей и проверить, что удаление завершается успешно за время жизни токена |

### RES-EXPORT-IMPORT-ROUNDTRIP — Данные, выгруженные API, принимаются им же обратно без изменений (RWB-0029, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [keycloak/keycloak#43867](https://github.com/keycloak/keycloak/issues/43867) | extends | Включить функцию, создающую объекты по умолчанию, выгрузить конфигурацию и импортировать её обратно; убедиться, что импорт проходит |

### RES-IMMUTABLE-FIELDS — Неизменяемые поля нельзя изменить после создания (RWB-0103, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [keycloak/keycloak#47733](https://github.com/keycloak/keycloak/issues/47733) | extends | Отправить обновление на путь с альтернативным идентификатором (внутренний id вместо alias) и проверить, что неизменяемый ключ не перезаписан значением из пути |

### RES-SYSTEM-OBJECT-PROTECTED — Встроенные системные объекты защищены от удаления и изменения при любой конфигурации (RWB-0035, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [keycloak/keycloak#47923](https://github.com/keycloak/keycloak/issues/47923) | extends | Отправить DELETE на каждый встроенный объект из полного списка создаваемых по умолчанию, а не только на основные, и ожидать отказ |

### RESIL-GRACEFUL-SHUTDOWN — Перезапуск экземпляра не обрывает выполняющиеся запросы (RWB-0108, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [keycloak/keycloak#43561](https://github.com/keycloak/keycloak/issues/43561) | extends | Повторить остановку по SIGTERM для каждого режима запуска сервиса (в том числе оптимизированного) и проверить, что запросы не обрываются по таймауту |

### RESOURCE-CREATE-READ — Created resource can be read back (RWB-0279, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [keycloak/keycloak#43718](https://github.com/keycloak/keycloak/issues/43718) | extends | Зарегистрировать пользователя при запрете редактировать атрибут, который служит логином, и проверить, что атрибут сохранён и возвращается при чтении |

### REST-DUPLICATE-UNIQUE-KEY — Дублирование уникального ключа (RWB-0114, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [keycloak/keycloak#45747](https://github.com/keycloak/keycloak/issues/45747) | extends | Создать два провайдера идентификации с одинаковым issuer и проверить, что второй отклонён 4xx |

### REST-ERROR-STATUS-BODY — Согласованность статуса и тела ошибки (RWB-0339, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [keycloak/keycloak#45812](https://github.com/keycloak/keycloak/issues/45812) | extends | Отправить password grant с неверным паролем и проверить статус 400 при error=invalid_grant по RFC 6749 §5.2 |

### REST-JSON-DUPLICATE-KEYS — Дублирующиеся ключи JSON (RWB-0355, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [keycloak/keycloak#45250](https://github.com/keycloak/keycloak/issues/45250) | extends | Разобрать JSON ответа и payload выданного токена строгим парсером — дублирующихся ключей нет |

### REST-PUT-REPLACEMENT — Семантика PUT (RWB-0356, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [keycloak/keycloak#44163](https://github.com/keycloak/keycloak/issues/44163) | extends | Отправить полное представление ресурса, изменив только разрешённое поле, и проверить, что обновление принято, а остальные поля сохранены |

### REST-REQUIRED-PARAM-MISSING — Отсутствует обязательный параметр (RWB-0131, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [keycloak/keycloak#48459](https://github.com/keycloak/keycloak/issues/48459) | covered | _только пруф_: Отсутствие обязательного поля в теле обновления — ровно проверка записи |

### REST-SENSITIVE-CACHE-CONTROL — Кэширование чувствительных ответов (RWB-0246, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [keycloak/keycloak#46750](https://github.com/keycloak/keycloak/issues/46750) | extends | Вызвать эндпоинты с токенами (userinfo, token) с недействительными данными и проверить Cache-Control: no-store в ответах-ошибках |

### REST-SENSITIVE-DATA — Отсутствие чувствительных данных в ответах (RWB-0133, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [keycloak/keycloak#45728](https://github.com/keycloak/keycloak/issues/45728) | extends | Перевести клиент, отражаемый публичным эндпоинтом конфигурации, в конфиденциальный режим и проверить, что ответ без аутентификации не содержит секрет |

### REST-STATUS-CODE-CONTRACT — Статус ответа соответствует контракту (RWB-0136, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [keycloak/keycloak#44540](https://github.com/keycloak/keycloak/issues/44540) | covered | _только пруф_: Код ответа создания — ровно проверка записи |

### SEC-AUTHN-MALFORMED — Malformed credential is rejected (RWB-0142, багов: 3)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [keycloak/keycloak#46848](https://github.com/keycloak/keycloak/issues/46848) | extends | Отправить DPoP-доказательство с jwk неподдерживаемого типа (kty) и проверить 400 invalid_dpop_proof, а не 5xx |
| [keycloak/keycloak#46669](https://github.com/keycloak/keycloak/issues/46669) | extends | Отправить федеративное client assertion, по которому не находится клиент, и ожидать invalid_client без 5xx |
| [keycloak/keycloak#45003](https://github.com/keycloak/keycloak/issues/45003) | extends | Отправить client_assertion с несовпадающими iss и sub и ожидать invalid_client без 5xx |

### SEC-AUTHN-SCHEMES-SUPPORTED — Все задокументированные схемы Authorization принимаются на своих эндпоинтах (RWB-0036, багов: 2)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [keycloak/keycloak#48628](https://github.com/keycloak/keycloak/issues/48628) | extends | Вызвать эндпоинт регистрации и отмены регистрации узла клиента с учётными данными в теле формы (client_secret_post, client_secret_jwt) и проверить успех, как при Basic |
| [keycloak/keycloak#44940](https://github.com/keycloak/keycloak/issues/44940) | extends | _только пруф_: Запись про работу каждой задокументированной схемы аутентификации; вариант с перебором методов аутентификации клиента уже есть у keycloak/keycloak#48628 — только пруф |

### SEC-AUTHZ-ERROR-LEAK — Authorization failures do not disclose protected data (RWB-0340, багов: 2)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [keycloak/keycloak#48143](https://github.com/keycloak/keycloak/issues/48143) | extends | Отправить от пользователя без прав запрос к существующему объекту с данными, не проходящими валидацию, и проверить 403, а не 400 |
| [keycloak/keycloak#46010](https://github.com/keycloak/keycloak/issues/46010) | extends | Запросить несуществующий и существующий объект от пользователя без права на список и проверить одинаковый 403 |

### SEC-AUTHZ-METHOD-MATRIX — Authorization is enforced for every method (RWB-0147, багов: 2)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [keycloak/keycloak#46933](https://github.com/keycloak/keycloak/issues/46933) | extends | Запросить токен со scope, на который настроена политика, каждым типом гранта (code, password, client_credentials, refresh) и проверить, что политика срабатывает во всех |
| [keycloak/keycloak#45740](https://github.com/keycloak/keycloak/issues/45740) | extends | Для каждого типа условия политики клиента (тип доступа, scope, тип гранта) запросить токен и проверить, что исполнитель политики применён к ответу |

### SEC-AUTHZ-ROLE-POSITIVE-MATRIX — Разрешённая операция работает для каждой роли с правом, а не только для администратора (RWB-0004, багов: 2)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [keycloak/keycloak#43883](https://github.com/keycloak/keycloak/issues/43883) | extends | Выполнить операцию учёткой с минимально достаточными ролями при каждой модели прав администратора и проверить успех |
| [keycloak/keycloak#43736](https://github.com/keycloak/keycloak/issues/43736) | extends | Выполнить чтение пользователя администратором, которому права выданы только через группу, и ожидать 200 без 5xx |

### SEC-FAIL-CLOSED-INPUT — Неожиданный тип, пустое или отсутствующее поле проверки безопасности ведёт к отказу, а не к пропуску проверки (RWB-0006, багов: 2)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [keycloak/keycloak#46718](https://github.com/keycloak/keycloak/issues/46718) | extends | Запросить операцию, проверка прав которой не поддерживается текущей моделью прав (token exchange с audience другого клиента при выключенной функции), — отказ 4xx, а не 5xx |
| [keycloak/keycloak#43723](https://github.com/keycloak/keycloak/issues/43723) | extends | Завершить регистрацию аутентификатора ответом без аттестации (формат none) при политике, требующей аттестацию, и ожидать отказ |

### SEC-OWNERSHIP-UPDATE — User cannot modify another owner’s resource (RWB-0152, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [keycloak/keycloak#46658](https://github.com/keycloak/keycloak/issues/46658) | extends | Отправить PUT на доступный ресурс с id другого ресурса в теле и проверить 400, другой ресурс не изменён |

### SEC-ROLE-MASS-ASSIGN — Mass assignment cannot elevate privileges (RWB-0248, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [keycloak/keycloak#47536](https://github.com/keycloak/keycloak/issues/47536) | extends | Изменить поле групп при PUT/PATCH пользователя через альтернативный API (SCIM) от администратора без права на членство и проверить 403 |

### SEC-TENANT-SEARCH — Tenant filter cannot be bypassed in list/search (RWB-0158, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [keycloak/keycloak#48324](https://github.com/keycloak/keycloak/issues/48324) | extends | Передать в список флаг или дополнительный фильтр (IS_ADMIN=true и т. п.) и проверить, что ограничение по родительскому контейнеру (серверу ресурсов, проекту) сохраняется, а следующий запрос другого контейнера находит свои объекты |

### SEC-TOKEN-AUDIENCE — Token for another audience is rejected (RWB-0160, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [keycloak/keycloak#46717](https://github.com/keycloak/keycloak/issues/46717) | extends | Передать в грант (UMA claim_token, subject_token) ID-токен, выданный другому клиенту, и проверить отказ по несовпадению azp/aud |

### SEC-TOKEN-EXPIRED — Expired access token is rejected (RWB-0161, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [keycloak/keycloak#46716](https://github.com/keycloak/keycloak/issues/46716) | extends | Передать просроченный ID-токен в параметре claim_token запроса разрешения и ожидать отказ |

### SEC-TOKEN-ISSUER — Token from untrusted issuer is rejected (RWB-0202, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [keycloak/keycloak#45590](https://github.com/keycloak/keycloak/issues/45590) | extends | Настроить у внешнего провайдера issuer, отличный от iss его токенов, и проверить, что обмен токена и вход отклоняются |

### SEC-TOKEN-REVOKED — Revoked token cannot be reused (RWB-0203, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [keycloak/keycloak#43218](https://github.com/keycloak/keycloak/issues/43218) | extends | Отозвать access-токен, полученный через обмен токенов, от имени клиента, который его получил, и проверить, что отзыв успешен и интроспекция даёт active:false |

### SEC-TOKEN-SIGNATURE — Token with invalid signature is rejected (RWB-0204, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [keycloak/keycloak#44217](https://github.com/keycloak/keycloak/issues/44217) | extends | Отключить проверку подписи у внешнего провайдера и отправить JWT authorization grant — запрос должен быть отклонён |

### VAL-DEFAULT-VALUES — Опущенные необязательные поля получают задокументированные значения по умолчанию (RWB-0166, багов: 2)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [keycloak/keycloak#44785](https://github.com/keycloak/keycloak/issues/44785) | extends | Создать пользователя через внешний IdP при атрибуте со значением по умолчанию, который пользователь не может редактировать, и проверить, что значение установлено и вход завершён |
| [keycloak/keycloak#44807](https://github.com/keycloak/keycloak/issues/44807) | extends | Создать объект с пустыми строками в необязательных полях и проверить, что подставлены задокументированные значения по умолчанию, а не пустые строки |

### VAL-DEFERRED-FAILURE — Принятые при записи данные не вызывают 5xx в зависимых операциях (RWB-0003, багов: 5)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [keycloak/keycloak#46132](https://github.com/keycloak/keycloak/issues/46132) | extends | Сохранить пустое значение атрибута, который маппер переводит в claim числового типа, и запросить токен — без 5xx |
| [keycloak/keycloak#44455](https://github.com/keycloak/keycloak/issues/44455) | extends | Настроить два маппера, пишущих в один составной claim (address и address.<поле>), и запросить токен — без 5xx |
| [keycloak/keycloak#43331](https://github.com/keycloak/keycloak/issues/43331) | extends | Включить и затем выключить настройку прав, после чего выполнить операции чтения с обычными ролями и ожидать ответ без 5xx |
| [keycloak/keycloak#47063](https://github.com/keycloak/keycloak/issues/47063) | extends | Создать политику с условием по контексту изменяющего и вызвать служебные операции над объектом (перегенерация секрета); ожидать ответ без 5xx |
| [keycloak/keycloak#44156](https://github.com/keycloak/keycloak/issues/44156) | extends | Сохранить поток входа, где шаг, требующий пользователя, стоит до его идентификации, и проверить, что вход отвечает контролируемой ошибкой без 5xx |

### VAL-STRING-FORMAT — Форматы строк (email, uuid, uri, date, phone) проверяются (RWB-0175, багов: 1)

| Баг | Тип | Новый шаг (вариант) / заметка сопоставления |
|---|---|---|
| [keycloak/keycloak#46192](https://github.com/keycloak/keycloak/issues/46192) | extends | Сохранить настройки почты с некорректными адресами отправителя и reply-to и проверить 400 |

