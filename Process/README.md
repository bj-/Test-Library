# Процесс тестирования

Как собирать коллекцию, запускать тесты, где хранить результаты и как оформлять баги. Правила общие для всех проектов
с тестами (сейчас - `postman`, `13vpn`); решение - [`../docs/decisions/0003-test-runs-and-bugs.md`](../docs/decisions/0003-test-runs-and-bugs.md).

| Документ | О чём |
|---|---|
| [`collections.md`](collections.md) | Создание коллекции: порядок работы, формат и расположение (Postman v3, Local Mode), структура, тест, обязательный набор тестов, безопасность стенда |
| [`running-tests.md`](running-tests.md) | Запуск: раннеры, окружение и секреты, наборы, отчёт о прогоне, разбор результатов |
| [`bugs.md`](bugs.md) | Правила оформления багов: когда заводить, классификация, серьёзность, жизненный цикл |
| [`templates/bug.md`](templates/bug.md) | Базовый шаблон бага (файл в `test-runs/bugs/`) |
| [`templates/trackers/`](templates/trackers/README.md) | Шаблоны под трекеры (сейчас YouTrack), выбор трекера |

## Репозитории

| Репозиторий | Что в нём |
|---|---|
| `Test-Library` (этот) | Библиотека проверок (`Api/`), правила процесса (`Process/`) |
| `postman` (gitlab.viiitech.ru/test/postman) | Коллекции, наборы тестов `tools/run/suites/`, скрипт запуска `tools/run/run.py` |
| `PostmanScripts` (github.com/bj-/PostmanScripts) | Фреймворк проверок (`utils.bind`, `test(...)`), вставлен в коллекции |
| `test-runs` (gitlab.viiitech.ru/test/test-runs) | Отчёты о прогонах `runs/` и баги `bugs/` |
| `13vpn` (локально, без remote) | Отдельный проект VPN-платформы: коллекция, свой фреймворк Bearer JWT, раннер, прогоны и баги внутри каталога |

Все репозитории клонируются рядом, в один каталог (`C:\Git\...`): скрипт запуска ищет `test-runs` по соседству.
