# Ответы моделей на `keycloak.reviewcheck.blind.md` (19 идей, без решений Claude)

_Получены от bj 2026-10-17. Тексты сокращены до решений и сути. Идеи 1–10 — кластеры (Claude: accept), 11–19 — переносы
в варианты (Claude: 11 SEC-TENANT-SEARCH, 12 AUTH-CLIENT-ASSERTION-BINDING, 13 SEC-FAIL-CLOSED-INPUT,
14 AUTH-CLIENT-CERT-IDENTITY, 15 AUTH-LOGOUT-INVALIDATES, 16 VAL-STRING-FORMAT, 17 REST-JSON-DUPLICATE-KEYS,
18 BIZ-FLAG-EFFECT-MATRIX, 19 AUTH-OAUTH-REDIRECT-STATE)._

| # | ChatGPT | Gemini 3.1 pro preview | Qwen |
|---|---|---|---|
| 1 | accept | accept | accept |
| 2 | accept | accept (extends BIZ-WORKFLOW-STEP-SKIP) | accept |
| 3 | разделить на два, оба принять | accept одной записью | accept |
| 4 | accept, сузить | accept | accept |
| 5 | accept после уточнения (в источнике USERS и CLIENTS противоречат) | accept | accept |
| 6 | accept | accept | accept |
| 7 | accept, сузить (доказан только rememberMe) | accept | accept |
| 8 | accept после проверки семантики RFC 8693 | accept | accept |
| 9 | accept после обобщения (приоритет — по документации) | accept | accept |
| 10 | accept после уточнения (зависит от области ролей) | accept (extends SEC-ROLE-ADMIN-SELF-TARGET) | accept |
| 11 | разделить: фильтр не снимает область + отрицательный кэш не переносится между областями | extends DB-ACCESS-SCOPE-IN-QUERY | новая REST-FILTER-SCOPE-PRESERVED |
| 12 | не принимать: зависит от модели доверия, спорит с AUTH-CLIENT-ASSERTION-BINDING | reject: специфика Kubernetes SA | reject: специфика RFC 7523 |
| 13 | новая SEC-AUTHZ-UNSUPPORTED-CHECK-FAIL-CLOSED | extends ERR-INTERNAL-ERROR-SHAPE | новая ERR-UNSUPPORTED-OPERATION-4XX |
| 14 | условно, профильная запись | extends AUTH-CLIENT-CERT-IDENTITY | новая AUTH-CLIENT-CERT-CHAIN-TRUNCATE |
| 15 | новая AUTH-OIDC-LOGOUT-WITHOUT-SESSION | новая AUTH-OAUTH-LOGOUT-STATELESS | новая AUTH-LOGOUT-NO-SESSION-REDIRECT |
| 16 | accept узко | reject: маркер Keycloak | reject: специфика Keycloak |
| 17 | extends REST-JSON-DUPLICATE-KEYS | extends REST-JSON-DUPLICATE-KEYS | reject: покрыто REST-JSON-DUPLICATE-KEYS |
| 18 | extends BIZ-FLAG-EFFECT-MATRIX | новая (extends RES-STATE-TRANSITIONS) | reject: покрыто BIZ-FLAG-EFFECT-MATRIX |
| 19 | extends REST-OPEN-REDIRECT | reject: покрыто VAL-STRING-FORMAT | reject: покрыто VAL-STRING-FORMAT |

Общие выводы моделей: ChatGPT — группировка по ключевым словам вместо инварианта и обратная ошибка — широкие правила из
одного бага (8, 10, 12, 14); Gemini — пропущен фильтр продуктовой специфики (12, 16), часть идей — частные случаи
существующих (11, 17); Qwen — 17–19 дублируют существующие, 12 и 16 — специфика.
