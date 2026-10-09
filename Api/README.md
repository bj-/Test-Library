# API Test Library

Версионируемая библиотека шаблонов проверок для генерации API-тестов REST и gRPC.

## Принципы

- Библиотека хранит **правила генерации проверок**, а не только готовые тест-кейсы.
- Одна запись = один проверяемый риск/инвариант.
- Протокол, полярность, набор тестов, приоритет и профиль запуска — независимые измерения.
- Ожидаемое поведение выводится из API-контракта и явно заданных бизнес-правил; агент не должен его выдумывать.
- Применимость определяется возможностями API, а не только названием метода.
- Для изменяющих операций проверяется не только ответ, но и состояние после операции.
- Неприменимость отличается от пробела покрытия.

## Структура

- `schema/` — JSON Schema для валидации записей и профилей.
- `taxonomy/` — контролируемые словари категорий, меток, приоритетов и профилей.
- `checks/common/` — проверки, общие для REST и gRPC.
- `checks/rest/` и `checks/grpc/` — протокольные проверки.
- `profiles/` — наборы и параметры запуска.
- `selection-rules/` — правила отбора и ранжирования.
- `validation/` — критерии качества библиотеки и покрытия.

## Быстрый старт агента

1. Прочитать контракт API (например, OpenAPI или protobuf descriptors).
2. Построить модель операций, полей, статусов, прав, состояний и возможностей.
3. Выбрать записи, у которых совпадают `applies_to.protocols` и `include_if`, и не срабатывает `exclude_if`.
4. Если обязательная предпосылка или ожидаемое поведение неизвестны — пометить проверку как `needs_clarification`, не генерировать ложное ожидание.
5. Сгенерировать варианты из `test_variants`, применяя классы эквивалентности, граничные значения и ограничения риска.
6. Назначить наборы, приоритет и профиль запуска.
7. Удалить семантические дубликаты, сохранив traceability до `check.id`.
8. Проверить покрытие и подготовить отчёт по включённым, исключённым и требующим уточнения проверкам.

## Формат записи

См. `schema/check.schema.json` и примеры в `checks/`.

## Статусы ожидаемого поведения

- `contract`: поведение должно быть определено контрактом.
- `business_rule`: поведение должно быть определено явным бизнес-правилом.
- `standard`: поведение задано применимым стандартом/протоколом.
- `needs_clarification`: не генерировать утверждение об ожидаемом результате, пока правило не уточнено.

## Замечание о статус-кодах

Не фиксируйте универсально HTTP-код или gRPC status для всех сервисов. Конкретное соответствие ошибок берётся из контракта и принятой в проекте модели ошибок.

## Исправление конфликтов имён профилей
Если валидатор сообщает `unknown profile CI` или `id must match filename`, выполните из корня библиотеки:
```powershell
python tools/repair_profiles.py
python tools/validate_library.py .
```
Файл `tools/repair_profiles.py` приводит имена профилей к `PR.yaml`, `Smoke.yaml`, `CI.yaml`, `Regression.yaml`, `Nightly.yaml`, `Release.yaml` и устанавливает совпадающие `id`.

## Stage 4: OpenAPI access-control coverage generator

See `docs/COVERAGE_GENERATOR_STAGE4.md`. Run `python tools/generate_coverage.py --openapi examples/openapi.sample.yaml --access-model examples/access-model.sample.yaml --out build/coverage` to generate candidate security checks and coverage reports. Generated candidates require review and should be validated before merging.

## Документация проекта и отчёты

- `docs/PROJECT_ORIGIN.md` — исходная идея и принципы.
- `docs/IMPLEMENTATION_PLAN.md` — этапы реализации и следующие шаги.
- `docs/STAGE_REPORTS.md` — отчёты по этапам и зафиксированные результаты валидации.
- `docs/PROJECT_OVERVIEW.md` — итоговое описание архитектуры, процесса и ограничений.
- `docs/TEST_SELECTION_AND_COMMANDS.md` — команды проверки схемы, генерации покрытия и подбора проверок.
- `build/real-contract-coverage/REAL_CONTRACT_COVERAGE_REPORT.md` — подробный отчёт по анализу контрактов, включая вопросы и противоречия.

## Быстрые команды

Из корня `Api/`:

```bash
# Проверка структуры каталога и JSON Schema
python tools/validate_library.py .

# Выборка по профилям
python tools/select_checks.py . Smoke
python tools/select_checks.py . CI
python tools/select_checks.py . Regression

# Генерация кандидатов и матрицы покрытия для примера
python tools/generate_coverage.py --openapi examples/openapi.sample.yaml --access-model examples/access-model.sample.yaml --out build/coverage

# Пересборка анализа контрактов в examples/real-contracts/
python tools/generate_real_contract_coverage.py
```

Валидация схемы подтверждает структурную совместимость, но не означает, что кандидат соответствует реальному поведению API или готов к запуску. Все неопределённости из отчётов должны быть разрешены до фиксации окончательных ожиданий теста.
