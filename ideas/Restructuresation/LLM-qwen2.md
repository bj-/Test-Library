Изучил репозиторий — текущая структура выросла из API-фокуса и уже трещит по швам (ADR 0006 добавил `checks/ui/` и `checks/db/` внутрь `Api/`, что логически неправильно). Ниже — развёрнутое предложение по реорганизации.

---

## 1. Что не так с текущей структурой

```
Test-Library/
├── Api/                    ← название стало неверным: внутри уже ui/, db/, security/
│   ├── checks/             ← контент смешан с инфраструктурой
│   ├── schema/             ← это инфраструктура, а не контент API
│   ├── taxonomy/           ← тоже инфраструктура
│   ├── tools/              ← инфраструктура
│   ├── validation/         ← инфраструктура
│   ├── selection-rules/    ← процесс генерации
│   ├── profiles/           ← рантайм-конфиг
│   ├── mining/             ← инструмент сбора
│   └── ...
├── Process/
└── docs/
```

**Три ключевые проблемы:**
1. **`Api/` как корень** — ограничивает расширение. Добавление `load/`, `mobile-ui/`, `pentest/` внутрь `Api/checks/` превратит папку в помойку.
2. **Смешение слоёв** — контент (проверки), инфраструктура (схемы, валидация), процесс (правила подбора) лежат вперемешку.
3. **Нет места для новых генераторов** — если завтра появится генератор Mobile-UI тестов на Appium, ему некуда встать рядом с генератором Postman-коллекций.

---

## 2. Принципы новой структуры

1. **Домены верхнего уровня** — каждый тип тестирования = отдельная папка на корне.
2. **Разделение слоёв** — `checks/` (что проверять), `generators/` (как генерировать), `runners/` (как запускать).
3. **Shared infrastructure** — общая таксономия, схемы, инструменты доступны всем доменам.
4. **Единообразие записей** — один `check.schema.json` для всех доменов (с опциональными расширениями).
5. **Process и docs не трогаем** — они ортогональны контенту.

---

## 3. Предлагаемая структура

```
Test-Library/
│
├── checks/                         ← ВСЕ проверки (бывший Api/checks/)
│   ├── api/                        ← API-тесты
│   │   ├── rest/
│   │   ├── grpc/
│   │   ├── graphql/
│   │   └── websocket/
│   ├── ui/                         ← UI-тесты
│   │   ├── web/                    ← Web-UI (Playwright, Cypress, Selenium)
│   │   ├── mobile-android/         ← Mobile UI (Appium, Espresso)
│   │   ├── mobile-ios/
│   │   └── desktop/
│   ├── data/                       ← SQL и БД
│   │   ├── sql/                    ← SELECT/INSERT/UPDATE/DELETE проверки
│   │   ├── migration/              ← проверки миграций
│   │   └── nosql/
│   ├── security/                   ← Pentest и безопасность
│   │   ├── auth/                   ← OAuth, JWT, сессии
│   │   ├── injection/              ← SQLi, XSS, SSRF, RCE
│   │   ├── misconfig/              ← CORS, заголовки, TLS
│   │   └── pentest/                ← комплексные сценарии
│   ├── performance/                ← Нагрузочные
│   │   ├── load/                   ← профили нагрузки
│   │   ├── stress/
│   │   ├── endurance/
│   │   └── assertions/             ← что проверять после прогона
│   ├── contract/                   ← Контрактное тестирование
│   │   ├── schema/
│   │   └── consumer-driven/
│   └── common/                     ← Кросс-доменные проверки (бывший common)
│       ├── status-codes/
│       ├── headers/
│       └── timing/
│
├── generators/                     ← Генераторы тестов (код)
│   ├── postman/                    ← текущий генератор Postman v3
│   ├── playwright/                 ← Web-UI генератор
│   ├── appium/                     ← Mobile-UI генератор
│   ├── pytest/                     ← pytest-based генератор (SQL, integration)
│   ├── k6/                         ← Нагрузочные (k6)
│   ├── nuclei/                     ← Pentest (nuclei templates)
│   └── shared/                     ← общие хелперы для генераторов
│       ├── selection-rules/        ← правила подбора (бывший selection-rules/)
│       └── profiles/               ← профили выполнения (бывший profiles/)
│
├── runners/                        ← Скрипты запуска и отчётности
│   ├── collections/                ← генерация коллекций
│   ├── executors/                  ← обёртки над раннерами
│   └── reporters/                  ← сбор и агрегация результатов
│
├── infra/                          ← Инфраструктура библиотеки
│   ├── schema/                     ← JSON-схемы (check.schema.json и др.)
│   ├── taxonomy/                   ← categories.yaml, tags.yaml, priorities.yaml
│   ├── validation/                 ← валидаторы записей
│   ├── mining/                     ← сбор данных из баг-трекеров
│   ├── build/                      ← отчёты покрытия
│   └── traceability/               ← трассировка проверок ↔ реальные баги
│
├── examples/                       ← Примеры сгенерированных тестов
│   ├── api/postman/
│   ├── ui/playwright/
│   ├── data/pytest/
│   └── ...
│
├── process/                        ← Процесс (бывший Process/)
│   ├── collections.md
│   ├── running-tests.md
│   ├── bugs.md
│   └── templates/
│
├── docs/                           ← Управление проектом
│   ├── STATUS.md
│   ├── ideas.md
│   └── decisions/
│
├── tools/                          ← CLI-утилиты (бывший Api/tools/)
│   ├── assign_profiles.py
│   └── validate.py
│
├── CLAUDE.md
└── requirements-generator.txt
```

---

## 4. Как это решает задачу развития

| Новое направление | Куда встаёт | Что нужно добавить |
|---|---|---|
| **Web-UI** | `checks/ui/web/` + `generators/playwright/` | Шаблоны проверок UI + генератор тестов Playwright |
| **Mobile-UI** | `checks/ui/mobile-*/` + `generators/appium/` | Шаблоны Appium-проверок + генератор |
| **SQL** | `checks/data/sql/` + `generators/pytest/` | Шаблоны SQL-проверок + генератор pytest-тестов |
| **Pentest** | `checks/security/pentest/` + `generators/nuclei/` | Шаблоны уязвимостей + генератор nuclei-шаблонов |
| **Нагрузочные** | `checks/performance/` + `generators/k6/` | Профили нагрузки + генератор k6-скриптов |
| **IoT / GraphQL subscriptions / gRPC streaming** | `checks/api/*` | Новая подпапка — без изменения инфраструктуры |

**Ключевое преимущество:** чтобы добавить новое направление, нужно сделать только две вещи:
1. Создать папку в `checks/<domain>/`
2. Создать генератор в `generators/<tool>/`

Вся инфраструктура (схемы, таксономия, валидация) уже готова и переиспользуется.

---

## 5. Что общего у всех направлений — единый формат check

Текущий `check.schema.json` расширяется полем `domain`, чтобы один формат работал везде:

```yaml
# checks/ui/web/login-form-required-fields.yaml
id: UI-WEB-LOGIN-REQUIRED-001
domain: ui            # api | ui | data | security | performance | contract
subdomain: web
title: "Все обязательные поля формы логина валидируются на клиенте"
category: functional
priority: high
tags: [ui, web, login, validation]
assertion: |
  Оставить каждое обязательное поле пустым → получить inline-ошибку
  без отправки формы на сервер
targets:
  - playwright
  - cypress
  - selenium
```

```yaml
# checks/data/sql/null-handling.yaml
id: DATA-SQL-NULL-001
domain: data
subdomain: sql
title: "NULL в WHERE-условии не возвращает неожиданные строки"
category: edge-case
priority: medium
assertion: |
  SELECT ... WHERE column = NULL должен возвращать 0 строк
  (IS NULL используется отдельно)
targets:
  - pytest
  - sqlcmd
```

```yaml
# checks/security/pentest/sql-injection-login.yaml
id: SEC-PENTEST-SQLI-001
domain: security
subdomain: pentest
title: "SQL-инъекция в форме логина"
category: owasp-top-10
priority: critical
assertion: |
  Логин: ' OR 1=1 -- → вход без пароля невозможен
targets:
  - nuclei
  - burp
```

Генератор читает `targets` и выбирает только записи, релевантные его инструменту.

---

## 6. План миграции (безопасный, без слома существующего)

```
Шаг 1. Создать infra/, generators/, runners/ параллельно Api/
        ├── infra/schema/         ← скопировать из Api/schema/
        ├── infra/taxonomy/       ← скопировать из Api/taxonomy/
        └── ...

Шаг 2. Распаковать Api/checks/ на домены
        ├── checks/api/rest/      ← из Api/checks/rest/
        ├── checks/api/grpc/      ← из Api/checks/grpc/
        ├── checks/ui/web/        ← из Api/checks/ui/ (если там web)
        ├── checks/data/sql/      ← из Api/checks/db/
        └── checks/security/      ← из Api/checks/security/

Шаг 3. Вынести генератор Postman
        └── generators/postman/   ← из Api/ (Python-код генерации)

Шаг 4. Перенести selection-rules и profiles
        └── generators/shared/

Шаг 5. Обновить references в коде
        └── все пути Api/checks → checks/, Api/schema → infra/schema/

Шаг 6. Удалить Api/ (когда всё работает)
```

**Совет:** сделать это через PR с ADR (как вы уже делаете в `docs/decisions/`). Описать решение в `docs/decisions/0007-restructuring.md`.

---

## 7. Риски и как их избежать

| Риск | Митигация |
|---|---|
| Поломать существующие коллекции Postman | Шаг 5 делать после прогона полной регрессии; держать `Api/` как git-tag до полной миграции |
| `check.schema.json` не покроет новые домены | Добавить `domain`-специфичные optional-поля (например, `selector` для UI, `query` для SQL) |
| Два формата записей разведутся | Один `validate.py` для всех доменов, один `assign_profiles.py` |
| Потеря трассировки (traceability) | Мигрировать `infra/traceability/` целиком, обновить пути в отчётах |

---

## 8. Итог

Новая структура превращает **API-библиотеку** в **Test Generation Platform**:

- `checks/` — *что* проверять (знания, не зависят от инструмента)
- `generators/` — *как* превратить знание в исполняемый тест
- `runners/` — *как* запустить и собрать результат
- `infra/` — фундамент, общий для всех
- `process/` + `docs/` — управление

Такой подход позволяет добавлять новые направления (например, Accessibility-тесты, Chaos Engineering) **без рефакторинга инфраструктуры** — просто создавая новые папки в `checks/` и `generators/`.