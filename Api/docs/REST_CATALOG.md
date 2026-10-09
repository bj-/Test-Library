# REST API Test Catalog — coverage map

Количество сценариев: **57**. Все записи имеют `status: draft` и требуют адаптации к контракту API.

| Область | Примеры покрытия |
|---|---|
| HTTP и контракт | Статусы, Content-Type, Accept, Location, 204, ошибки, conditional GET |
| Валидация | Required, type, null/empty, длины, числовые границы, enum, unknown fields |
| Изменение состояния | PUT/PATCH/DELETE, уникальность, атомарность, переходы состояний |
| Надёжность | Idempotency-Key, retry, timeout, rate limit, batch, async |
| Коллекции | Pagination, filter, sort, стабильный порядок |
| Безопасность | AuthN/AuthZ, mass assignment, sensitive data, CORS, SSRF, open redirect, cache |
| Совместимость/данные | Версии API, Unicode, даты/время, decimal precision, correlation ID |

## Принцип назначения

- `kind` — поведение: `positive`, `negative`, `boundary` и другие согласованные типы.
- `category` — область проверки.
- `tags` — независимые признаки для фильтрации.
- `profiles` — назначение в прогоне. `Smoke` не является синонимом `positive`.
- `P0–P3` — риск/приоритет, не замена профиля.

## Правила перед генерацией

1. Включать сценарий только при выполнении `applicability.when`.
2. Пропускать с объяснением, если выполняется `skip_when`.
3. Неизвестную семантику помечать для review; не угадывать статус или формат ошибки.
4. Подтверждать поведение по OpenAPI/контракту: статусы, unknown fields, nullability, повторный DELETE, retry и т.д.
5. Изменяющие состояние сценарии должны использовать изолированные данные и cleanup.
6. Проверки SSRF, redirect, rate limit и security запускать только в разрешённом тестовом окружении.
7. Перед интеграцией сверить поля YAML с JSON Schema и каноническими значениями текущей библиотеки.