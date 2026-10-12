# Процесс тестирования

Как запускать тесты, где хранить результаты и как оформлять баги. Правила общие для всех проектов с тестами
(сейчас - `postman`); решение - [`../docs/decisions/0003-test-runs-and-bugs.md`](../docs/decisions/0003-test-runs-and-bugs.md).

| Документ | О чём |
|---|---|
| [`running-tests.md`](running-tests.md) | Запуск: раннеры, окружение и секреты, наборы, отчёт о прогоне, разбор результатов |
| [`bugs.md`](bugs.md) | Правила оформления багов: когда заводить, классификация, серьёзность, жизненный цикл |
| [`templates/bug.md`](templates/bug.md) | Шаблон бага |

## Репозитории

| Репозиторий | Что в нём |
|---|---|
| `Test-Library` (этот) | Библиотека проверок (`Api/`), правила процесса (`Process/`) |
| `postman` (gitlab.viiitech.ru/test/postman) | Коллекции, наборы тестов `tools/run/suites/`, скрипт запуска `tools/run/run.py` |
| `PostmanScripts` (github.com/bj-/PostmanScripts) | Фреймворк проверок (`utils.bind`, `test(...)`), вставлен в коллекции |
| `test-runs` (gitlab.viiitech.ru/test/test-runs) | Отчёты о прогонах `runs/` и баги `bugs/` |

Все репозитории клонируются рядом, в один каталог (`C:\Git\...`): скрипт запуска ищет `test-runs` по соседству.
