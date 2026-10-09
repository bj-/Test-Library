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
Checks: 152 | Unique IDs: 152 | Profiles: 6
JSON Schema validation: enabled
Errors: 0
```

Скрипт в текущей реализации принимает путь к корню библиотеки позиционным аргументом; `--help` не реализован.

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

Скрипт печатает приоритет, ID и заголовок выбранных проверок; количество выводится в stderr строкой `Selected: N`. Имя профиля соответствует файлу в `profiles/` и может указываться с `.yaml` или без расширения.

**Важно:** селектор использует пересечение тегов проверки с `include_tags`, исключает записи с `exclude_tags`, учитывает `max_priority` и при включённом `deterministic_only` исключает недетерминированные проверки. Наличие проверки в библиотеке не гарантирует её попадание в профиль.

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

## 5. Исправить имена/ссылки профилей при ошибках валидатора

```bash
python tools/repair_profiles.py
python tools/validate_library.py .
```

Используйте repair-скрипт только если ошибки действительно связаны с ID/именами профилей; после изменения проверьте diff.

## 6. Рекомендуемый локальный контроль перед commit

```bash
python tools/validate_library.py .
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
  - name: Select smoke checks
    run: python tools/select_checks.py . Smoke
  - name: Select CI checks
    run: python tools/select_checks.py . CI
```

Команды `select_checks.py` формируют выборку и печатают её в stdout; чтобы передать список раннеру, нужно отдельно согласовать формат экспорта и интеграцию с тестовой инфраструктурой.
