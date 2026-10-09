# Отчёт сверки REST Expansion с текущей API Test Library

## Результат

- Базовая библиотека до интеграции: 14 checks, 6 профилей, 0 ошибок.
- REST Expansion: 57 YAML-шаблонов.
- Интегрированная версия после адаптации: 71 checks, 6 профилей, JSON Schema validation включена, 0 ошибок встроенного валидатора.

## Обнаруженные несовместимости исходной Expansion

1. Каждый YAML-шаблон был записан как одиночный объект, а `tools/validate_library.py` ожидает документ с верхнеуровневым списком `checks`.
2. `steps` в Expansion были списком строк; `schema/check.schema.json` требует элементы-объекты с обязательным полем `action`.
3. Поле `status: draft` не разрешено текущей JSON Schema (`additionalProperties: false`). Оно удалено из данных checks; черновой статус описан в документации.
4. Часть категорий и тегов отсутствовала в текущих справочниках `taxonomy/categories.yaml` и `taxonomy/tags.yaml`.
5. `expans/taxonomy.json` и `expans/profiles.json` являются отдельными справочниками Expansion и не совпадают по структуре/семантике с текущими YAML-справочниками и профилями проекта. В интегрированной версии авторитетными оставлены текущие справочники и профили проекта.

## Нормализация категорий

- `filtering` → `pagination`
- `data-integrity` → `resources`
- `concurrency` → `resilience`
- `observability` → `errors`
- `state-transition` → `resources`
- `compatibility` → `contract`

## Нормализация тегов

- `headers` → `http-semantics`
- `data-integrity` → `contract`
- `encoding` → `validation`
- `privacy` → `security`
- `concurrency`, `rate-limit`, `timeout`, `retry` → `resilience`
- `caching` → `http-semantics`
- `state-transition`, `consistency` → `contract`
- `compatibility` сохранён как допустимый тег

Эти отображения обеспечивают совместимость с текущим валидатором, но часть из них является семантическим приближением. Перед фиксацией taxonomy как стандарта рекомендуется отдельно согласовать категории/теги `observability`, `data-integrity`, `concurrency`, `compatibility` и связанные с ними различия.

## Важно

Успешная schema-валидация подтверждает структурную совместимость с библиотекой, но не означает, что тесты готовы к запуску. Все 57 checks — шаблоны: необходимо проверить применимость к конкретному API/OpenAPI, корректность предусловий, тестовых данных, ожидаемых статусов/заголовков и безопасное выполнение security-сценариев.
