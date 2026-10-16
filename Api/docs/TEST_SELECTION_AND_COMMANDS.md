# 5. Проверка схемы и подбор тестов: команды и примеры

Все команды запускаются из корня каталога `Api/`. Требуется Python 3.10+; зависимости для генерации перечислены в `requirements-generator.txt`.

## Установка зависимостей

```bash
python -m pip install -r requirements-generator.txt
```

## 1. Проверить библиотеку и JSON Schema

```bash
python tools/validate_library.py .
```

Ожидаемый результат для текущего архива:

```text
Checks: 631 | Unique IDs: 631 | Profiles: 6
Status: approved=583, draft=32, needs_clarification=16
JSON Schema validation: enabled
Errors: 0 | Warnings: 0
```

Скрипт принимает путь к корню библиотеки позиционным аргументом. Профили сопоставляются по `id` без учёта регистра; предупреждение `differs in case` не считается ошибкой.

PowerShell:

```powershell
python tools/validate_library.py .
```

## 2. Подобрать проверки по профилю

```bash
python tools/select_checks.py . Smoke
python tools/select_checks.py . PR
python tools/select_checks.py . CI
python tools/select_checks.py . Regression
python tools/select_checks.py . Nightly
python tools/select_checks.py . Release
```

Скрипт печатает приоритет, ID и заголовок выбранных проверок; итог выводится в stderr строкой `Selected: N | Excluded: M | Truncated by max_checks: K`. Имя профиля — это `id` профиля, регистр не важен, суффикс `.yaml` допускается.

Параметры:

- `--status approved,draft,needs_clarification` — какие статусы включать (по умолчанию только `approved`);
- `--explain` — дополнительно вывести исключённые проверки с причиной;
- `--format json` — машиночитаемый результат: выбранные и исключённые проверки с причинами.

**Порядок отбора:** статус → членство в профиле (профиль указан в `check.profiles`; для проверок без этого поля — пересечение тегов с `include_tags`) → `exclude_tags` → `max_priority` → `deterministic_only` → сортировка по приоритету и ID → обрезка до `max_checks`. Наличие проверки в библиотеке не гарантирует её попадание в профиль.

## 3. Сгенерировать кандидаты по учебному OpenAPI

```bash
python tools/generate_coverage.py \
  --openapi examples/openapi.sample.yaml \
  --access-model examples/access-model.sample.yaml \
  --out build/coverage
```

PowerShell:

```powershell
python tools/generate_coverage.py `
  --openapi examples/openapi.sample.yaml `
  --access-model examples/access-model.sample.yaml `
  --out build/coverage
```

Ожидаемые артефакты: `generated_checks/`, `coverage_matrix.json`, `coverage_report.json`, `coverage_report.md`.

## 4. Пересобрать анализ включённых реальных контрактов

```bash
python tools/generate_real_contract_coverage.py
```

Скрипт читает контракты из `examples/real-contracts/` и формирует артефакты в `build/real-contract-coverage/`, а также кандидаты в `checks/generated/real-contracts/`. Сначала сохраните текущие результаты, если они нужны для сравнения.

## 5. Имена файлов профилей

Регистр имён файлов в `profiles/` на работу инструментов не влияет. Чтобы всё же переименовать файл с изменением регистра так, чтобы git это зафиксировал (Windows, `core.ignorecase=true`), делайте два шага:

```bash
git mv profiles/ci.yaml profiles/ci.tmp.yaml
git mv profiles/ci.tmp.yaml profiles/CI.yaml
```

## 6. Рекомендуемый локальный контроль перед commit

```bash
python tools/assign_profiles.py .
python tools/validate_library.py .
python tools/build_catalog.py .
python tools/select_checks.py . Smoke
python tools/select_checks.py . CI
python tools/select_checks.py . Regression
```

После изменения схем, таксономий, профилей или генератора дополнительно сравните сгенерированные отчёты с предыдущими результатами и проверьте вопросы/противоречия.

## Пример CI-пайплайна

```yaml
# Пример последовательности команд; адаптируйте под CI-систему репозитория.
steps:
  - name: Install dependencies
    run: python -m pip install -r requirements-generator.txt
  - name: Validate library
    run: python tools/validate_library.py .
  - name: Profiles and catalog are up to date
    run: |
      python tools/assign_profiles.py . --check
      python tools/build_catalog.py . --check
  - name: Select smoke checks
    run: python tools/select_checks.py . Smoke
  - name: Select CI checks
    run: python tools/select_checks.py . CI
```

Команды `select_checks.py` формируют выборку и печатают её в stdout; чтобы передать список раннеру, нужно отдельно согласовать формат экспорта и интеграцию с тестовой инфраструктурой.
