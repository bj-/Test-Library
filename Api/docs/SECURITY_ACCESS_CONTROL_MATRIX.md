# Этап 3 — Security access-control matrix

## Цель

Матрица моделирует пять независимых измерений контроля доступа. Она нужна для измеримого покрытия рисков, а не для механического перебора всех комбинаций. Генератор должен создавать только применимые комбинации, подтверждённые контрактом и моделью доступа.

## Измерения матрицы

| Измерение | Положительный контроль | Негативные классы | Обязательные проверки состояния |
|---|---|---|---|
| Authentication (AuthN) | Валидная identity получает предусмотренный доступ | отсутствующие/повреждённые credentials, истёкший/отозванный токен, неверные issuer/audience/signature | отказ не выполняет защищённую операцию |
| Authorization (AuthZ) | Разрешённое действие доступно субъекту с нужным правом | отсутствующее право, обход через метод/версию/alias, утечка ошибок | запрещённая операция не меняет состояние |
| Resource ownership | Владелец читает/изменяет собственный ресурс | горизонтальное повышение привилегий, подмена ID, nested/bulk/export bypass | данные и ресурс другого владельца неизменны/не раскрыты |
| Tenant isolation | Субъект работает в своём tenant | чужой tenant ID, подмена tenant header, list/search/cache/bulk leakage | нет чтения, мутации или создания в чужом tenant |
| Roles/Scopes | Роль/скоуп с нужными полномочиями разрешает действие | low-to-high escalation, self-assignment, mass assignment, missing scope, scope injection, revoke role | effective permissions не расширяются неавторизованно |

## Как читать комбинации

Для каждой операции строится вектор: `AuthN policy × AuthZ policy × Ownership policy × Tenant policy × Roles/Scopes policy`. Для каждого измерения используются значения `required / not_applicable / unknown`; для ownership/tenant/role допускаются конкретные policy identifiers. Неизвестная политика — это пробел спецификации, а не основание придумать ожидаемый статус. Помечать `needs_clarification` в отчёте генерации и не генерировать assertion до уточнения.

### Минимальная матрица комбинаций

| ID комбинации | Условия | Обязательные классы проверок |
|---|---|---|
| M1 Public | AuthN не требуется; ресурс публичный | доступ без credentials; проверка отсутствия случайной зависимости от identity |
| M2 Authenticated own | AuthN required; ownership enforced | valid/invalid/expired/revoked credential; собственный ресурс; нет права на чужой ресурс |
| M3 Same-tenant peer | AuthN required; общий tenant; разные owners/roles | horizontal escalation; role/scope enforcement; ownership read/write/delete |
| M4 Cross-tenant | tenant isolation enforced | cross-tenant read/write/create/list/search/cache/bulk/export; tenant-header spoof |
| M5 Privileged operation | admin/privileged role or scope required | low-to-high escalation; missing scope; self-role assignment; mass assignment; alternate method/version |
| M6 Token lifecycle | token/session lifecycle supports expiry/revocation/refresh | expired token; revoked token; refresh replay/rotation; role revocation propagation |
| M7 Async/export | job/export/download handle exists | ownership and tenant checks on poll/cancel/result/download; no bearer-handle leakage |
| M8 Shared resource | explicit sharing/cross-tenant grant exists | permitted grantee succeeds; non-grantee denied; revoke sharing and re-check |

## Принципы покрытия

1. Для каждой операции, требующей authentication, покрыть valid credentials и минимум один negative AuthN case; для токенов дополнительно expired/revoked, если такие механизмы есть.
2. Для каждой операции с authorization rule покрыть разрешённого субъекта и ближайший запрещённый класс (роль/скоуп/owner/tenant).
3. Для каждой операции чтения и изменения ресурса проверять ownership отдельно: read, update, delete, nested references и bulk — если поддерживаются.
4. Для multi-tenant API проверить не только прямой GET по ID, но и create, list/search, bulk, export, async jobs, cache и любые tenant-derived relationships, если применимы.
5. Для привилегированных операций проверять как минимум low-role denial, missing-scope denial (если scopes используются) и защиту от изменения привилегированных полей.
6. Не считать «401/403 получен» достаточным доказательством: для мутаций проверить неизменность состояния; для batch — атомарность/частичный результат по контракту; для read — отсутствие утечки тела, метаданных и вложенных ресурсов.
7. Проверять разрешённый путь рядом с отказом, чтобы исключить ложноположительный результат из-за сломанной тестовой учётной записи или некорректных данных.
8. Для каждой проверки хранить traceability: операция, policy ID, матричные измерения, риск, причина применимости, профиль и результат.
