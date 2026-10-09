# API Test Library

YAML-справочник проверок для генерации API-тестов. Первая версия включает единый формат `Check`, JSON Schema, таксономию, профили запуска, правила выбора, каталог примеров и CLI-валидатор/селектор.

## Проверка и выбор
```bash
pip install pyyaml jsonschema
python tools/validate_library.py .
python tools/select_checks.py . PR
python tools/select_checks.py . Regression
```

```PowerShell
python -m pip install pyyaml jsonschema
ИЛИ
py -m pip install pyyaml jsonschema

python tools/validate_library.py .
python tools/select_checks.py . PR
python tools/select_checks.py . Regression
```


## Формат и метки
- `kind`: поведенческий класс (`positive`, `negative`, `boundary`, `contract` и т. п.).
- `tags`: ортогональные метки домена и запуска (`security`, `smoke`, `regression`, `nightly` и т. д.).
- `priority`: риск/важность P0–P3, не равно частоте запуска.
- `applicability.when` и `skip_when`: условия включения/пропуска. Неизвестная применимость не считается истинной автоматически.
- `automation.level` и `deterministic`: пригодность для автозапуска.

Smoke — только быстрые, детерминированные проверки критических потоков; Regression — функциональные, негативные, граничные и контрактные сценарии; Nightly — расширенные/дорогие/длительные сценарии; Release — критические security, contract, compatibility и бизнес-потоки.

Селектор — базовый фильтр по тегам, приоритету и детерминированности. Он не заменяет интерпретатор условий `applicability` и интеграцию с OpenAPI/Protobuf: это следующий этап реализации.
