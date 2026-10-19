# Процесс тестирования

Как собирать коллекцию, запускать тесты, где хранить результаты и как оформлять баги. Правила общие для всех проектов
с тестами (сейчас - BFF, VPN13); решения - [`../docs/decisions/0003-test-runs-and-bugs.md`](../docs/decisions/0003-test-runs-and-bugs.md),
[`../docs/decisions/0007-autotest-workspace.md`](../docs/decisions/0007-autotest-workspace.md) (раскладка `C:\Git\Autotest`, движок).

| Документ | О чём |
|---|---|
| [`collections.md`](collections.md) | Создание коллекции: порядок работы, формат и расположение (Postman v3, Local Mode), структура, тест, обязательный набор тестов, безопасность стенда |
| [`running-tests.md`](running-tests.md) | Запуск: раннеры, окружение и секреты, наборы, отчёт о прогоне, разбор результатов |
| [`bugs.md`](bugs.md) | Правила оформления багов: когда заводить, классификация, серьёзность, жизненный цикл |
| [`templates/bug.md`](templates/bug.md) | Базовый шаблон бага (файл в `bugs/` репозитория результатов) |
| [`templates/trackers/`](templates/trackers/README.md) | Шаблоны под трекеры (сейчас YouTrack), выбор трекера |

## Репозитории

| Репозиторий | Что в нём |
|---|---|
| `Test-Library` (этот) | Библиотека проверок (`Api/`), правила процесса (`Process/`) |
| `test-engine` | Движок: запуск наборов, отчёты, Allure, сверка с контрактом, баги в трекер (`python autotest.py ...`) |
| BFF: `tests` (gitlab.viiitech.ru/test/postman) | Коллекции, окружения, наборы `suites/`, `autotest.yaml` |
| BFF: `results` (gitlab.viiitech.ru/test/autotest/bff) | Прогоны `runs/`, баги `bugs/`, история Allure `history/` |
| `PostmanScripts` | Фреймворк проверок (`utils.bind`, `test(...)`), вставлен в коллекции |
| `13vpn` (локально, без remote) | Отдельный проект VPN13: коллекция, свой фреймворк Bearer JWT, раннер, прогоны и баги внутри каталога (на движок ещё не переведён) |

Раскладка:

```
C:\Git\Autotest\test-engine\
C:\Git\Autotest\projects\<КОД>\tests\     autotest.yaml - пути к движку, результатам и Test-Library
C:\Git\Autotest\projects\<КОД>\results\
C:\Git\Test-Library\
```
