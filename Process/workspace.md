# Рабочее место и репозитории проектов

С чего начинать на любой машине: развернуть проект, который уже есть, или завести новый. Решения -
[ADR 0007](../docs/decisions/0007-autotest-workspace.md) (рабочее место, движок) и
[ADR 0013](../docs/decisions/0013-project-repos-tests-and-results.md) (репозитории проекта).

## Раскладка

```
C:\Git\
  Test-Library\                  библиотека проверок, правила процесса (Process/), реестр проектов projects.yaml
  Autotest\
    test-engine\                 движок: python autotest.py ...
    projects\
      <КОД>\
        tests\                   репозиторий <код>-tests: документация + тесты; ветки по версиям продукта
        results\                 репозиторий <код>-results: прогоны, отчёты, баги; без веток
```

| Репозиторий | Что в нём | Ветки |
|---|---|---|
| `<код>-tests` | `docs/sources/` - исходная документация (Markdown-копии, контракты, манифест `sources.yaml` со ссылками на оригиналы); `docs/reviews/` - ревью и анализ документации (наш, заказчика, встречи); `docs/modules/`, `docs/project/`, STATUS и ADR; коллекции `postman/`, наборы `suites/`, генератор `tools/`, `autotest.yaml`, `autotest.py` | `main` - текущая работа; принятая версия - тег `<код>-<версия>` и ветка `release/<версия>` только для исправлений |
| `<код>-results` | `runs/<YYYY>/<MM>/<RUN-ID>/` (`run.yaml`, `report.md`, `results.json`), индекс прогонов, `bugs/` и реестр багов, `history/` (тренды Allure), сводки | только `main`: прогоны с любой ветки тестов - сюда; версию прогона даёт `run.yaml` (`tests.commit`, `branch`, `tag`) |

Адреса репозиториев проектов - только в реестре [`projects.yaml`](projects.yaml); в правилах, памяти и навыках - ссылка
на него, не копия адресов.

## Подготовка

1. **Test-Library** - `C:\Git\Test-Library`. Нет клона - спросить у пользователя, откуда склонировать.
2. **Движок** - `C:\Git\Autotest\test-engine`. Нет клона - спросить у пользователя, откуда склонировать.
3. Инструменты (Python, Node, newman, Allure) - [`running-tests.md`](running-tests.md), «Подготовка машины».

Команды ниже - из движка напрямую (проекта на машине ещё может не быть):

```
python C:\Git\Autotest\test-engine\engine\autotest.py setup            # реестр и что из него уже есть на машине
```

## Проект уже есть

**Есть в реестре:**

```
python C:\Git\Autotest\test-engine\engine\autotest.py setup <КОД>
```

Клонирует недостающие `tests` и `results` в `projects\<КОД>\`, у существующих сверяет remote с реестром (расхождение -
не трогает, сообщает). Нужная ветка тестов (`release/<версия>`) - `git switch` в `tests`; результаты - всегда `main`.

**Нет в реестре, но пользователь про него знает** (команда сама подскажет) - спросить у пользователя адреса репозиториев
тестов и результатов и название, затем:

```
python C:\Git\Autotest\test-engine\engine\autotest.py setup <КОД> --tests <адрес> --results <адрес> --title "<название>"
```

Команда дописывает проект в `projects.yaml` и клонирует. Изменение реестра - коммит в Test-Library.

## Новый проект

1. **Код проекта** - короткий, латиницей, заглавными (`BFF`, `VPN13`): префикс RUN-ID и номеров багов `BUG-<КОД>-NNNN`.
   Предложить пользователю, утвердить.
2. **Репозитории** - предложить пользователю создать в GitLab, в группе `test/autotest`, два пустых проекта:
   `<код>-tests` и `<код>-results` (код - строчными). Проект другого отдела или с другим кругом доступа - группу
   уточнить у пользователя. Создаёт пользователь; ассистент даёт список действий и ждёт адреса.
3. **Клоны и заготовки:**

   ```
   python C:\Git\Autotest\test-engine\engine\autotest.py setup <КОД> --tests <адрес> --results <адрес> --title "<название>" --init
   ```

   `--init` в пустых клонах создаёт `autotest.yaml` (код, адреса, версия движка), `autotest.py`, каталоги `postman/`,
   `suites/`, `docs/sources/`, `docs/reviews/`, а в результатах - `.gitignore`, `runs/`, `bugs/`, `history/`.
   Существующие файлы не перезаписывает.
4. **Контекст проекта** - `CLAUDE.md`, `docs/STATUS.md`, `docs/ideas.md`, `docs/decisions/` в обоих репозиториях;
   документация, коллекция, первый прогон - навык `create-tests-api`.
5. Коммит в оба репозитория и в Test-Library (реестр), push.

## Другие места на машине

Рабочее место не в `C:\Git` - переменные `AUTOTEST_WORKSPACE` (каталог `Autotest`) и `AUTOTEST_LIBRARY` (Test-Library) для
`setup`; для прогонов - `AUTOTEST_ENGINE`, `AUTOTEST_RESULTS`, `AUTOTEST_LIBRARY` (README движка).
