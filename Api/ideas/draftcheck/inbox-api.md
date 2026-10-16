# Перекрёстная проверка черновых записей библиотеки

Пакет `inbox-api`, записей: 33. Записи и разбор входящих идей сделала модель Claude Opus 5.5.
Этот файл целиком отдаётся другой LLM. Ответ модели вставить в чат внутренней сессии.

## Задание для модели

Ты — ревьюер библиотеки шаблонов тестов (API, UI, БД). Ниже — черновые записи (`status: draft`), которые другая модель
написала по идеям из входящего списка. Для каждой записи суди по её тексту, исходным идеям и индексу библиотеки.

Для каждой записи ответь:

1. **Решение** — `approve` (можно утверждать как есть), `fix` (утверждать после правки — какой именно),
   `merge` (дублирует или почти дублирует запись из индекса — с какой и как объединить), `reject` (не проверка, слишком
   общая или продуктовая — почему).
2. **Шаги и ожидание** — исполнимы ли шаги как действия теста; проверяемо ли ожидание; не подогнано ли ожидание под одно
   поведение там, где источник допускает варианты (тогда — «по документации»).
3. **Применимость и условия** — верны ли протоколы и `when` / `skip_when`; указаны ли нужные доступы и инструменты.
4. **Почему** — одна-две строки.

Исходные идеи — мнение одного автора; если запись теряет или искажает смысл идеи, отметь это.

Принципы библиотеки (из README):

- Библиотека хранит **правила генерации проверок**, а не только готовые тест-кейсы.
- Одна запись = один проверяемый риск/инвариант.
- Протокол, полярность, набор тестов, приоритет и профиль запуска — независимые измерения.
- Цель - полноценное тестирование продукта, а не проверка соответствия контракту. Не доверяем никому: ни заказчику,
  ни аналитику, ни разработчику; контракт - лишь мнение разработчика о том, как работает продукт.
- Проверки соответствия контракту обязательны, но это лишь часть набора: к ним добавляются проверки по ТЗ,
  стандартам, практике и здравому смыслу.
- Ожидаемое поведение выводится из всех источников: ТЗ заказчика (ФТТ), внутренних ТЗ (ОТЗ, ЧТЗ), ПМИ, контракта,
  стандартов (RFC, OWASP), практики отрасли и здравого смысла - с указанием источника. Источник молчит - проверка всё
  равно выполняется; источники противоречат - это находка. Лучше завести баг о потенциальной проблеме, чем промолчать.
  Подробно - `../docs/decisions/0002-expected-behavior-sources.md`.
- Применимость определяется возможностями API, а не только названием метода.
- Для изменяющих операций проверяется не только ответ, но и состояние после операции.
- Неприменимость отличается от пробела покрытия.

Формат ответа — одна таблица на все записи:

| # | ID | Решение | Что исправить / с чем объединить | Почему |
|---|---|---|---|---|
| 1 | AUTH-… | approve/fix/merge/reject | … | … |

В конце — 2–3 строки общего вывода: систематические ошибки, если есть.

## 1. ASYNC-SCHEDULE-DST-TRANSITION

```yaml
id: ASYNC-SCHEDULE-DST-TRANSITION
title: Расписание на несуществующее или повторяющееся местное время срабатывает по правилу
category: async
protocols:
- generic
kind: boundary
priority: P3
preconditions:
- Есть задачи по расписанию в местном времени с переходом на летнее или зимнее время; можно сдвигать время стенда.
steps:
- action: Назначить задачу на 02:30 в день перехода на летнее время (времени нет) и в день перехода на зимнее (время
    повторяется).
expected:
- Задача срабатывает ровно один раз по задокументированному правилу; без пропуска и двойного срабатывания.
applicability:
  when:
  - Есть расписания в местном времени.
  skip_when:
  - Расписания только в UTC.
automation:
  level: partial
  deterministic: true
references:
- IANA tz database
- inbox №44
```

Исходные идеи (inbox):

- №44: **Расписание на несуществующее/дублирующееся местное время при переходе на летнее/зимнее время** (02:30 в день перехода) - срабатывает ровно один раз по задокументированному правилу

## 2. BIZ-AMBIGUOUS-ADDRESS

```yaml
id: BIZ-AMBIGUOUS-ADDRESS
title: Неоднозначный почтовый адрес не выбирается молча по первому совпадению
category: business-logic
protocols:
- generic
kind: boundary
priority: P3
preconditions:
- Адрес используется дальше (почта, геокодирование, доставка, зона обслуживания); есть справочник адресов (ФИАС,
  геокодер).
steps:
- action: Передать адрес, которому соответствует несколько объектов («Санкт-Петербург, Казанская улица, 20» — две
    Казанские улицы), одноимённые улицы разных населённых пунктов и улицу и переулок с одним названием.
expected:
- Система просит уточнить или возвращает варианты; сохраняется однозначный идентификатор (ФИАС, КЛАДР); геопозиция
  и отправка — на выбранный адрес.
applicability:
  when:
  - Есть ввод адресов.
  skip_when:
  - Нет.
automation:
  level: partial
  deterministic: true
references:
- Здравый смысл и практика работы с ФИАС; в ТЗ обычно не описано — REQ-UNSPECIFIED-BEHAVIOR-PROBE
- inbox №45
```

Исходные идеи (inbox):

- №45: **Неоднозначный почтовый адрес** (адрес потом используется: отправка почты, геокодирование, доставка, зона обслуживания): адрес, которому соответствует несколько объектов («Санкт-Петербург, Казанская улица, 20» — в городе две Казанские улицы, на каждой есть дом 20) — система не выбирает молча первый вариант: просит уточнить (район, индекс, ФИАС/КЛАДР-код), сохраняет однозначный идентификатор, геопозиция и почта уходят на выбранный адрес; плюс одноимённые улицы в разных населённых пунктах региона и улица/переулок/проспект с одним названием

## 3. BIZ-DIVISION-BY-ZERO

```yaml
id: BIZ-DIVISION-BY-ZERO
title: Входы с нулём в знаменателе не дают 500 и нечисловых значений
category: business-logic
protocols:
- generic
kind: boundary
priority: P2
preconditions:
- Есть расчёты с делением — средние, доли, цена за единицу, скорость, процент.
steps:
- action: 'Передать входы, дающие ноль в знаменателе: количество 0, цена 0, период 0, пустая выборка для среднего.'
expected:
- Определённое значение по документации или 400; без 500 и без NaN, Infinity, null в ответе.
applicability:
  when:
  - Есть расчёты.
  skip_when:
  - Нет.
automation:
  level: full
  deterministic: true
references:
- Чек-лист guru99 (пер. О. Алифановой)
- inbox №65
```

Исходные идеи (inbox):

- №65: **Деление на ноль в расчётах**: входы, которые дают ноль в знаменателе (количество 0, цена 0, период 0, пустая выборка для среднего) — не 500 и не `NaN`/`Infinity`/`null` в ответе, а определённое значение или 400

## 4. BIZ-EMAIL-NOTIFICATION-DELIVERY

```yaml
id: BIZ-EMAIL-NOTIFICATION-DELIVERY
title: Письма уходят нужному адресату с верными ссылками и без внедрения заголовков
category: business-logic
protocols:
- generic
kind: contract
priority: P2
preconditions:
- Сервис отправляет письма; нужен тестовый ящик или мок SMTP.
steps:
- action: Вызвать каждое действие, которое отправляет письмо; проверить адресата, тему, ссылки.
- action: 'Передать в поля, попадающие в письмо, значения с \r\nBcc: и повторить действие дважды.'
expected:
- Письмо одно, адресат и тема верные, ссылки работают; новых заголовков письма нет; повтор не дублирует письмо,
  если это не новое событие.
applicability:
  when:
  - Есть почтовые уведомления.
  skip_when:
  - Нет.
automation:
  level: partial
  deterministic: true
references:
- CWE-93
- Смежные — BIZ-SIDE-EFFECTS-ONCE, INJ-HEADER-CRLF
- inbox №73
```

Исходные идеи (inbox):

- №73: **Почтовые уведомления**: письмо уходит (тестовый ящик или мок SMTP), адресат, тема и ссылки верные, ссылки работают; нет инъекции заголовков через поля (`\r\nBcc:`); повторная отправка не дублирует

## 5. BIZ-FLAG-EFFECT-MATRIX

```yaml
id: BIZ-FLAG-EFFECT-MATRIX
title: Каждый флаг сущности влияет на поведение так, как описано
category: business-logic
protocols:
- generic
kind: contract
priority: P2
preconditions:
- У сущности есть флаги (boolean-поля), меняющие поведение.
steps:
- action: Для каждого флага выполнить затрагиваемые операции при true и false и в комбинациях с другими флагами.
expected:
- Поведение соответствует описанию; флаг, который ни на что не влияет, — находка.
applicability:
  when:
  - Есть флаги.
  skip_when:
  - Нет.
automation:
  level: full
  deterministic: true
references:
- Чек-лист guru99 (пер. О. Алифановой)
- inbox №79
```

Исходные идеи (inbox):

- №79: **Флаги сущности**: каждый boolean-флаг влияет на поведение так, как описано, в обоих значениях и в комбинациях; флаг, который ни на что не влияет, — находка

## 6. CONTRACT-RESPONSE-LINKS-RESOLVE

```yaml
id: CONTRACT-RESPONSE-LINKS-RESOLVE
title: URL в ответах открываются
category: contract
protocols:
- rest
- graphql
kind: contract
priority: P3
preconditions:
- Ответы содержат URL — ссылки на ресурсы, файлы, изображения, next и prev, Location.
steps:
- action: Собрать все URL из ответов основных операций и запросить каждый с теми же правами.
expected:
- Каждый URL отвечает 200 (или документированным статусом) с ожидаемым Content-Type; битых ссылок нет.
applicability:
  when:
  - Есть URL в ответах.
  skip_when:
  - Нет.
automation:
  level: full
  deterministic: true
references:
- Смежные — PAGE-NEXT-LINK-VALID, HTTP-ABSOLUTE-URL-BASE-PATH
- inbox №60
```

Исходные идеи (inbox):

- №60: **Нет битых ссылок в ответах**: все URL в ответах (ссылки на ресурсы, файлы, изображения, `next`/`prev` пагинации, `Location`) открываются: 200 и ожидаемый `Content-Type`

## 7. OBS-BUILD-VERSION-TRACEABLE

```yaml
id: OBS-BUILD-VERSION-TRACEABLE
title: Версия сборки доступна для трассировки на тестовых стендах и скрыта в production
category: observability
protocols:
- generic
kind: contract
priority: P3
preconditions:
- Известно, какой стенд тестовый, а какой production.
steps:
- action: На тестовом стенде запросить версию сборки (служебная ручка, заголовок, health).
- action: Повторить на production или по его конфигурации.
expected:
- На тестовом стенде версия сборки определяется — результат прогона привязан к версии.
- На production версия скрыта или доступна только авторизованно (HARD-VERSION-DISCLOSURE).
applicability:
  when:
  - Есть разные стенды.
  skip_when:
  - Нет.
automation:
  level: full
  deterministic: true
references:
- Здравый смысл — тестировать без знания версии нельзя
- Смежная — HARD-VERSION-DISCLOSURE
- inbox №6
```

Исходные идеи (inbox):

- №6: **Версия сборки доступна для трассировки** (заголовок или служебная ручка) на тестовых стендах и скрыта в production

## 8. RES-VALUE-ROUNDTRIP-EXACT

```yaml
id: RES-VALUE-ROUNDTRIP-EXACT
title: Сохранённое значение возвращается так, как введено, кроме документированной нормализации
category: resources
protocols:
- generic
kind: contract
priority: P2
preconditions:
- Есть строковые поля, которые сохраняются и читаются.
steps:
- action: Сохранить значения со спецсимволами, разным регистром, пробелами по краям, Unicode в разных формах нормализации,
    HTML и кавычками; прочитать.
expected:
- Значение совпадает с отправленным байт в байт, кроме задокументированной нормализации; незадокументированная трансформация
  (обрезка, замена, регистр, экранирование при хранении) — находка.
applicability:
  when:
  - Есть сохраняемые строки.
  skip_when:
  - Нет.
automation:
  level: full
  deterministic: true
references:
- Здравый смысл — система возвращает то, что ввёл пользователь
- Смежные — VAL-WHITESPACE-HANDLING, REST-UNICODE-NORMALIZATION, VAL-SPECIAL-CHARACTERS
- inbox №46
```

Исходные идеи (inbox):

- №46: **Данные хранятся так, как введены**: сохранённое и возвращённое значение совпадает с отправленным байт в байт, кроме документированной нормализации (максимум — `trim`, и то её фактическое наличие выясняется тестом). Незадокументированная трансформация (обрезка, замена символов, смена регистра, Unicode-нормализация, экранирование) — потенциальный баг; заодно риск инъекции, если трансформация «чистит» ввод вместо экранирования на выводе

## 9. RES-REFERENCE-DATA-COMPLETE

```yaml
id: RES-REFERENCE-DATA-COMPLETE
title: Справочники через API полные, упорядочены по документации и управляются без релиза
category: resources
protocols:
- generic
kind: contract
priority: P3
preconditions:
- API отдаёт справочники (значения для выбора в клиенте).
steps:
- action: Запросить справочник и сравнить с источником (ТЗ, админка); изменить справочник администратором и запросить
    снова.
expected:
- Значения полные и не обрезаны; порядок задокументирован; изменение администратором видно без релиза, если так
  заявлено.
applicability:
  when:
  - Есть справочники.
  skip_when:
  - Нет.
automation:
  level: full
  deterministic: true
references:
- Чек-лист guru99 (пер. О. Алифановой)
- inbox №59
```

Исходные идеи (inbox):

- №59: **Справочники через API полные и управляемые**: значения справочника (то, что идёт в выпадающие списки) не обрезаются по длине, порядок задокументирован; изменение справочника администратором видно без релиза (не зашито в код)

## 10. FILE-ROUNDTRIP-EXACT

```yaml
id: FILE-ROUNDTRIP-EXACT
title: Загруженный файл скачивается байт в байт
category: files
protocols:
- rest
kind: contract
priority: P2
preconditions:
- Есть загрузка и скачивание файлов.
steps:
- action: Загрузить файлы разных форматов и размеров с именами на кириллице и с пробелами; скачать и сравнить хэш.
expected:
- Хэш совпадает; Content-Type и Content-Disposition (с именем по RFC 6266) корректны.
applicability:
  when:
  - Есть загрузка файлов.
  skip_when:
  - Нет.
automation:
  level: full
  deterministic: true
references:
- RFC 6266
- Смежная — FILE-DOWNLOAD-HEADERS
- inbox №72
```

Исходные идеи (inbox):

- №72: **Загрузка и скачивание файла байт в байт**: загруженный файл скачивается без изменений (хэш совпадает), корректные `Content-Type`, `Content-Disposition` и имя (кириллица, пробелы), разные форматы

## 11. HTTP-REDIRECT-ENDPOINT-PARITY

```yaml
id: HTTP-REDIRECT-ENDPOINT-PARITY
title: Вызов через перенаправляющий адрес работает как прямой вызов
category: http-semantics
protocols:
- rest
kind: compatibility
priority: P3
preconditions:
- Старый адрес перенаправляет на новый (совместимость, смена версии, канонизация).
steps:
- action: Выполнить операции через старый адрес с 301, 302, 307, 308 и напрямую; сравнить метод, тело, права и побочные
    эффекты.
expected:
- Результат, права и побочные эффекты те же, что при прямом вызове; при 307 и 308 метод и тело сохраняются.
applicability:
  when:
  - Есть перенаправления.
  skip_when:
  - Нет.
automation:
  level: full
  deterministic: true
references:
- RFC 9110 §15.4
- inbox №56
```

Исходные идеи (inbox):

- №56: **Эндпоинт с редиректом = прямой вызов**: если старый адрес перенаправляет на новый (обратная совместимость), результат, права и побочные эффекты те же, что при прямом обращении; метод и тело не теряются при 301/302/307/308

## 12. VAL-OPTIONAL-FIELDS-COMBINATIONS

```yaml
id: VAL-OPTIONAL-FIELDS-COMBINATIONS
title: Любая комбинация и порядок необязательных полей обрабатываются без падения
category: validation
protocols:
- rest
- graphql
- grpc
kind: boundary
priority: P2
preconditions:
- У операции несколько необязательных полей или параметров.
steps:
- action: Перебрать комбинации необязательных полей (попарно или все), в разном порядке ключей, с пустыми значениями
    и без единого необязательного поля.
expected:
- Порядок ключей не влияет; ни одна комбинация не даёт 5xx; без полей — значения по умолчанию или «любое» для фильтра,
  как задокументировано.
applicability:
  when:
  - Есть необязательные поля.
  skip_when:
  - Нет.
automation:
  level: full
  deterministic: true
references:
- Смежные — REST-OPTIONAL-EMPTY-VALUE, VAL-DEFAULT-VALUES
- inbox №50
```

Исходные идеи (inbox):

- №50: **Комбинации необязательных ключей**: (1) поведение одинаково при любом порядке ключей; (2) ключ есть, значение пустое; (3) никакая комбинация необязательных ключей не роняет сервер; (4) ожидаемое поведение при разных значениях; (5) нет ни одного необязательного ключа — значение по умолчанию или «любое» для фильтра, как задокументировано

## 13. PAGE-SORT-FIELD-TYPE-MATRIX

```yaml
id: PAGE-SORT-FIELD-TYPE-MATRIX
title: Сортировка по каждому полю учитывает его тип, локаль и направление
category: pagination
protocols:
- rest
- graphql
kind: contract
priority: P2
preconditions:
- Список поддерживает сортировку по нескольким полям разных типов.
steps:
- action: Для каждого сортируемого поля запросить asc и desc на данных с числами, датами, строками в разном регистре
    и с буквами ё и е.
- action: Запросить без параметра сортировки.
expected:
- Числа сортируются как числа, даты как даты; регистр и локаль — по документации; null — в задокументированном месте;
  порядок по умолчанию задокументирован.
applicability:
  when:
  - Есть сортировка.
  skip_when:
  - Нет.
automation:
  level: full
  deterministic: true
references:
- Смежные — PAGE-SORT-NULLS-TIES, REST-SORT-INVALID-FIELD
- inbox №70
```

Исходные идеи (inbox):

- №70: **Сортировка**: каждое поле asc/desc; числа как числа, даты как даты, а не строки; `null` в задокументированном месте; регистр и локаль (ё, е); стабильность между страницами; порядок по умолчанию задокументирован

## 14. SEC-PRINCIPAL-TYPE-CONFUSION

```yaml
id: SEC-PRINCIPAL-TYPE-CONFUSION
title: Принципал одного типа не получает прав принципала другого типа с тем же числовым ID
category: security
protocols:
- generic
kind: security
priority: P1
preconditions:
- Есть принципалы разных типов (пользователь, ссылка-доступ, бот, сервисная учётка) с пересекающимися числовыми
  ID.
steps:
- action: Создать принципал одного типа с ID, равным ID пользователя, и выполнить от него операции, доступные этому
    пользователю (удаление из команды, владение, чтение состава).
expected:
- 'Отказ: права определяются по паре тип и ID.'
applicability:
  when:
  - Есть принципалы разных типов.
  skip_when:
  - Один тип принципалов.
automation:
  level: full
  deterministic: true
references:
- CWE-843
- Смежная — AUTH-TOKEN-TYPE-CONFUSION
- inbox №148 (GHSA-32r8-5843-4qw2)
```

Исходные идеи (inbox):

- №148: **Путаница типов принципала в проверках прав**: у принципалов разных типов (пользователь, ссылка-доступ, бот, сервисная учётка) пересекаются числовые ID — принципал одного типа с ID = N не получает прав пользователя с ID = N (удаление из команды, владение ботом, чтение состава)

## 15. SEC-CHECK-ORDER

```yaml
id: SEC-CHECK-ORDER
title: Аутентификация и авторизация проверяются раньше разбора и валидации тела
category: security
protocols:
- rest
- graphql
- grpc
kind: security
priority: P2
preconditions:
- Есть защищённые операции с телом запроса.
steps:
- action: Отправить без учётных данных запрос с битым телом, с Content-Type application/json и пустым телом, с неполным
    телом.
- action: Отправить ролью без доступа запрос с неполным или невалидным телом.
expected:
- Без учётных данных — 401 (или 404 для несуществующего маршрута), а не 400 от парсера.
- 'Без права — 403, а не 400 со списком полей: структура запроса не раскрывается неавторизованным.'
applicability:
  when:
  - Есть защищённые операции.
  skip_when:
  - Нет.
automation:
  level: full
  deterministic: true
references:
- OWASP API2:2023, API5:2023
- inbox №2, №34
```

Исходные идеи (inbox):

- №2: **Порядок обработки запроса: аутентификация раньше разбора тела и валидации.** Неаутентифицированный запрос с битым телом / `Content-Type: application/json` и пустым телом должен получать 401 (защищённый маршрут) или 404 (нет маршрута), а не 400 от парсера
- №34: **Проверка роли раньше валидации тела**: роль без доступа + неполное тело -> 403, а не 400 со списком полей

## 16. HARD-ENVIRONMENT-ISOLATION

```yaml
id: HARD-ENVIRONMENT-ISOLATION
title: Тестовый стенд не обращается к ресурсам production
category: security
protocols:
- generic
kind: security
priority: P1
preconditions:
- Есть описание стенда или служебные ответы с адресами зависимостей.
steps:
- action: Посмотреть идентификаторы окружения (имя БД, URL зависимостей, очереди) в служебных ответах и конфигурации;
    выполнить операции с внешними вызовами и проверить адресатов.
- action: Сравнить имена БД и строки подключения окружений QA, UAT и production — различаются и не пересекаются
  notes: inbox №141
expected:
- Тестовый стенд использует только свои БД, очереди и внешние API (песочницы); идентификаторы production не встречаются.
applicability:
  when:
  - Есть внешние зависимости.
  skip_when:
  - Нет.
automation:
  level: partial
  deterministic: true
references:
- Чек-лист guru99 (пер. О. Алифановой)
- inbox №82
```

Исходные идеи (inbox):

- №82: **Окружения изолированы**: тестовый стенд не обращается к БД, очередям и внешним API продакшена; идентификаторы окружения (имя БД, URL зависимостей) в служебных ответах — не прод
- №141: **DB** — **Уникальные имена БД окружений**: имена БД QA, UAT и прода различаются, строки подключения окружений не пересекаются

## 17. HARD-NOT-IMPLEMENTED-INERT

```yaml
id: HARD-NOT-IMPLEMENTED-INERT
title: Операция, помеченная в контракте как нереализованная, не выполняется
category: security
protocols:
- rest
- graphql
- grpc
kind: security
priority: P2
preconditions:
- В контракте есть операции, помеченные как нереализованные (описание, x-status, ответ 501).
steps:
- action: Отправить корректный запрос к такой операции и проверить состояние после.
expected:
- 501 или 404, побочного эффекта нет. Если операция выполняется — находка; серьёзность выше на stage и production.
applicability:
  when:
  - Есть такие операции.
  skip_when:
  - Нет.
automation:
  level: full
  deterministic: true
references:
- OWASP API9:2023 (Improper Inventory Management)
- Смежные — HARD-SHADOW-API-VERSIONS, ERR-STATUS-MATCHES-EFFECT
- inbox №142
```

Исходные идеи (inbox):

- №142: **Метод «не реализован» по контракту, а на деле работает**: операция помечена в контракте как не реализованная (описание, `x-status`, ответ 501) — запрос с корректными данными, проверить: 501 / 404, побочного эффекта нет. Отвечает и выполняет — находка; серьёзность зависит от стенда (dev/test/sandbox — низкая, stage/prod — высокая)

## 18. AUTH-SENSITIVE-CHANGE-REAUTH

```yaml
id: AUTH-SENSITIVE-CHANGE-REAUTH
title: Изменение защиты учётки требует свежей аутентификации
category: security
protocols:
- generic
kind: security
priority: P1
preconditions:
- Учётка может менять настройки защиты — MFA, коды восстановления, email, пароль.
steps:
- action: Только с токеном сессии (без текущего пароля или свежей аутентификации) включить, отключить и перенастроить
    MFA, перевыпустить коды восстановления, сменить email и пароль.
- action: Подтвердить отключение MFA и перевыпуск кодов кодом, уже использованным ранее (для входа или прошлой операции).
expected:
- Запросы без свежей аутентификации отклоняются 4xx; настройки не меняются, коды не выдаются; уже использованный
  код не принимается.
applicability:
  when:
  - Есть настройки защиты учётки.
  skip_when:
  - Нет.
automation:
  level: full
  deterministic: true
references:
- OWASP ASVS V2.8, V3.7
- Смежные — AUTH-MFA-STEP-UP, AUTH-PASSWORD-CHANGE-REQUIRES-CURRENT
- inbox №145, №146 (GHSA-7m6h-rg42-m449)
```

Исходные идеи (inbox):

- №145: **Повторная аутентификация для изменений защиты учётки**: включение, отключение и перенастройка MFA, выпуск и перевыпуск кодов восстановления, смена email и пароля требуют текущий пароль (или свежую аутентификацию) — запрос только с токеном сессии отклоняется 4xx, настройки не меняются, коды не выдаются
- №146: **Отключение и перенастройка второго фактора требуют свежий код**: отключение MFA, перевыпуск кодов восстановления и смена приложения-аутентификатора не принимают код, уже использованный ранее (для входа или прошлой операции), — 4xx, настройки не меняются; нужен новый код

## 19. AUTH-PATH-NORMALIZATION-BYPASS

```yaml
id: AUTH-PATH-NORMALIZATION-BYPASS
title: Вариации пути защищённого маршрута не обходят аутентификацию
category: security
protocols:
- rest
kind: security
priority: P1
preconditions:
- Есть защищённые маршруты.
steps:
- action: Без учётных данных запросить защищённый маршрут с завершающим слэшем, в другом регистре пути и префикса,
    с двойным слэшем, сегментами . и .., закодированным слэшем и закодированными символами.
expected:
- Ни одна вариация не даёт 2xx без учётных данных.
applicability:
  when:
  - Есть защищённые маршруты.
  skip_when:
  - Нет.
automation:
  level: full
  deterministic: true
references:
- Смежная — HTTP-TRAILING-SLASH-CASE
- CWE-22, CWE-647
- postman BFF-Admin-Auth — тесты ссылаются на ID (inbox №21)
```

Исходные идеи (inbox):

- №21: **Записи для проверок, на которые уже ссылаются тесты postman, но которых нет в библиотеке**: `AUTH-PATH-NORMALIZATION-BYPASS` (31 тест), `AUTH-CREDENTIAL-CHANNEL-STRICT` (25), `AUTH-SESSION-VALUE-EXACT-MATCH` (20), `AUTH-DUPLICATE-CREDENTIALS` (5), `AUTH-SESSION-ID-ENTROPY` (2), `AUTH-PASSWORD-CHANGE-REQUIRES-CURRENT`, `AUTH-NOSQL-OPERATOR-CREDENTIALS`, `INJ-NULL-BYTE`, `AUTH-REVOKED-COOKIE-RELOGIN`, `AUTH-LOGOUT-SCOPE`, `AUTH-SESSION-ID-NOT-EXPOSED`, `AUTH-SESSION-SLIDING-RENEWAL`, `AUTH-SESSION-FILTER-SCOPE`, `AUTH-LOGIN-CROSS-ACCOUNT-COOKIE`

## 20. AUTH-CREDENTIAL-CHANNEL-STRICT

```yaml
id: AUTH-CREDENTIAL-CHANNEL-STRICT
title: Учётные данные принимаются только по документированному каналу
category: security
protocols:
- rest
kind: security
priority: P2
preconditions:
- Аутентификация на cookie-сессии.
steps:
- action: Передать действующее значение сессии в cookie с другим именем, без префикса __Host-, с префиксом в нижнем
    регистре, в заголовке Authorization Bearer и в своём заголовке.
expected:
- '401: сессия принимается только из документированной cookie.'
applicability:
  when:
  - Cookie-сессии.
  skip_when:
  - Нет.
automation:
  level: full
  deterministic: true
references:
- RFC 6265bis §4.1.3
- postman BFF-Admin-Auth — тесты ссылаются на ID (inbox №21)
```

Исходные идеи (inbox):

- №21: **Записи для проверок, на которые уже ссылаются тесты postman, но которых нет в библиотеке**: `AUTH-PATH-NORMALIZATION-BYPASS` (31 тест), `AUTH-CREDENTIAL-CHANNEL-STRICT` (25), `AUTH-SESSION-VALUE-EXACT-MATCH` (20), `AUTH-DUPLICATE-CREDENTIALS` (5), `AUTH-SESSION-ID-ENTROPY` (2), `AUTH-PASSWORD-CHANGE-REQUIRES-CURRENT`, `AUTH-NOSQL-OPERATOR-CREDENTIALS`, `INJ-NULL-BYTE`, `AUTH-REVOKED-COOKIE-RELOGIN`, `AUTH-LOGOUT-SCOPE`, `AUTH-SESSION-ID-NOT-EXPOSED`, `AUTH-SESSION-SLIDING-RENEWAL`, `AUTH-SESSION-FILTER-SCOPE`, `AUTH-LOGIN-CROSS-ACCOUNT-COOKIE`

## 21. AUTH-SESSION-VALUE-EXACT-MATCH

```yaml
id: AUTH-SESSION-VALUE-EXACT-MATCH
title: Значение сессии сравнивается целиком и точно
category: security
protocols:
- rest
kind: security
priority: P1
preconditions:
- Аутентификация на cookie-сессии.
steps:
- action: Передать изменённое, усечённое, дополненное и в другом регистре значение действующей cookie сессии.
expected:
- 401 во всех вариантах.
applicability:
  when:
  - Cookie-сессии.
  skip_when:
  - Нет.
automation:
  level: full
  deterministic: true
references:
- CWE-287
- postman BFF-Admin-Auth — тесты ссылаются на ID (inbox №21)
```

Исходные идеи (inbox):

- №21: **Записи для проверок, на которые уже ссылаются тесты postman, но которых нет в библиотеке**: `AUTH-PATH-NORMALIZATION-BYPASS` (31 тест), `AUTH-CREDENTIAL-CHANNEL-STRICT` (25), `AUTH-SESSION-VALUE-EXACT-MATCH` (20), `AUTH-DUPLICATE-CREDENTIALS` (5), `AUTH-SESSION-ID-ENTROPY` (2), `AUTH-PASSWORD-CHANGE-REQUIRES-CURRENT`, `AUTH-NOSQL-OPERATOR-CREDENTIALS`, `INJ-NULL-BYTE`, `AUTH-REVOKED-COOKIE-RELOGIN`, `AUTH-LOGOUT-SCOPE`, `AUTH-SESSION-ID-NOT-EXPOSED`, `AUTH-SESSION-SLIDING-RENEWAL`, `AUTH-SESSION-FILTER-SCOPE`, `AUTH-LOGIN-CROSS-ACCOUNT-COOKIE`

## 22. AUTH-DUPLICATE-CREDENTIALS

```yaml
id: AUTH-DUPLICATE-CREDENTIALS
title: Повторяющиеся и пустые учётные данные не дают доступа
category: security
protocols:
- rest
kind: security
priority: P2
preconditions:
- Аутентификация на cookie-сессии.
steps:
- action: Передать две cookie сессии с одним именем — мусор первым, действующая второй; запросить все эндпоинты
    без cookie, с пустой и с мусорной cookie.
expected:
- 401 во всех вариантах, ответ одинаковый на всех эндпоинтах.
applicability:
  when:
  - Cookie-сессии.
  skip_when:
  - Нет.
automation:
  level: full
  deterministic: true
references:
- RFC 6265 §5.4
- postman BFF-Admin-Auth — тесты ссылаются на ID (inbox №21)
```

Исходные идеи (inbox):

- №21: **Записи для проверок, на которые уже ссылаются тесты postman, но которых нет в библиотеке**: `AUTH-PATH-NORMALIZATION-BYPASS` (31 тест), `AUTH-CREDENTIAL-CHANNEL-STRICT` (25), `AUTH-SESSION-VALUE-EXACT-MATCH` (20), `AUTH-DUPLICATE-CREDENTIALS` (5), `AUTH-SESSION-ID-ENTROPY` (2), `AUTH-PASSWORD-CHANGE-REQUIRES-CURRENT`, `AUTH-NOSQL-OPERATOR-CREDENTIALS`, `INJ-NULL-BYTE`, `AUTH-REVOKED-COOKIE-RELOGIN`, `AUTH-LOGOUT-SCOPE`, `AUTH-SESSION-ID-NOT-EXPOSED`, `AUTH-SESSION-SLIDING-RENEWAL`, `AUTH-SESSION-FILTER-SCOPE`, `AUTH-LOGIN-CROSS-ACCOUNT-COOKIE`

## 23. AUTH-SESSION-ID-ENTROPY

```yaml
id: AUTH-SESSION-ID-ENTROPY
title: Идентификатор сессии новый при каждом входе, уникален и непредсказуем
category: security
protocols:
- rest
kind: security
priority: P2
preconditions:
- Аутентификация на cookie-сессии.
steps:
- action: Выполнить серию входов одной учёткой и разными; собрать идентификаторы сессий.
expected:
- Каждый вход даёт новый идентификатор; повторов нет; длина и алфавит дают не меньше 128 бит энтропии.
applicability:
  when:
  - Cookie-сессии.
  skip_when:
  - Нет.
automation:
  level: full
  deterministic: true
references:
- OWASP Session Management Cheat Sheet
- Смежная — AUTH-SESSION-FIXATION
- postman BFF-Admin-Auth — тесты ссылаются на ID (inbox №21)
```

Исходные идеи (inbox):

- №21: **Записи для проверок, на которые уже ссылаются тесты postman, но которых нет в библиотеке**: `AUTH-PATH-NORMALIZATION-BYPASS` (31 тест), `AUTH-CREDENTIAL-CHANNEL-STRICT` (25), `AUTH-SESSION-VALUE-EXACT-MATCH` (20), `AUTH-DUPLICATE-CREDENTIALS` (5), `AUTH-SESSION-ID-ENTROPY` (2), `AUTH-PASSWORD-CHANGE-REQUIRES-CURRENT`, `AUTH-NOSQL-OPERATOR-CREDENTIALS`, `INJ-NULL-BYTE`, `AUTH-REVOKED-COOKIE-RELOGIN`, `AUTH-LOGOUT-SCOPE`, `AUTH-SESSION-ID-NOT-EXPOSED`, `AUTH-SESSION-SLIDING-RENEWAL`, `AUTH-SESSION-FILTER-SCOPE`, `AUTH-LOGIN-CROSS-ACCOUNT-COOKIE`

## 24. AUTH-PASSWORD-CHANGE-REQUIRES-CURRENT

```yaml
id: AUTH-PASSWORD-CHANGE-REQUIRES-CURRENT
title: Смена пароля требует верный текущий пароль
category: security
protocols:
- rest
kind: security
priority: P1
preconditions:
- Есть смена пароля пользователем.
steps:
- action: Сменить пароль с неверным и без текущего пароля.
expected:
- 403/400; пароль не меняется.
applicability:
  when:
  - Есть смена пароля.
  skip_when:
  - Нет.
automation:
  level: full
  deterministic: true
references:
- OWASP ASVS V2.1.5
- Смежная — AUTH-SENSITIVE-CHANGE-REAUTH
- postman BFF-Admin-Auth — тесты ссылаются на ID (inbox №21)
```

Исходные идеи (inbox):

- №21: **Записи для проверок, на которые уже ссылаются тесты postman, но которых нет в библиотеке**: `AUTH-PATH-NORMALIZATION-BYPASS` (31 тест), `AUTH-CREDENTIAL-CHANNEL-STRICT` (25), `AUTH-SESSION-VALUE-EXACT-MATCH` (20), `AUTH-DUPLICATE-CREDENTIALS` (5), `AUTH-SESSION-ID-ENTROPY` (2), `AUTH-PASSWORD-CHANGE-REQUIRES-CURRENT`, `AUTH-NOSQL-OPERATOR-CREDENTIALS`, `INJ-NULL-BYTE`, `AUTH-REVOKED-COOKIE-RELOGIN`, `AUTH-LOGOUT-SCOPE`, `AUTH-SESSION-ID-NOT-EXPOSED`, `AUTH-SESSION-SLIDING-RENEWAL`, `AUTH-SESSION-FILTER-SCOPE`, `AUTH-LOGIN-CROSS-ACCOUNT-COOKIE`

## 25. AUTH-NOSQL-OPERATOR-CREDENTIALS

```yaml
id: AUTH-NOSQL-OPERATOR-CREDENTIALS
title: Операторы NoSQL в учётных данных входа отклоняются
category: security
protocols:
- rest
kind: security
priority: P1
preconditions:
- Есть вход по логину и паролю.
steps:
- action: Передать в логин и пароль объекты с операторами ($ne, $gt, $regex) вместо строк.
expected:
- 400; вход не выполняется.
applicability:
  when:
  - Есть вход по паролю.
  skip_when:
  - Нет.
automation:
  level: full
  deterministic: true
references:
- Конкретизирует INJ-NOSQL для входа
- CWE-943
- postman BFF-Admin-Auth — тесты ссылаются на ID (inbox №21)
```

Исходные идеи (inbox):

- №21: **Записи для проверок, на которые уже ссылаются тесты postman, но которых нет в библиотеке**: `AUTH-PATH-NORMALIZATION-BYPASS` (31 тест), `AUTH-CREDENTIAL-CHANNEL-STRICT` (25), `AUTH-SESSION-VALUE-EXACT-MATCH` (20), `AUTH-DUPLICATE-CREDENTIALS` (5), `AUTH-SESSION-ID-ENTROPY` (2), `AUTH-PASSWORD-CHANGE-REQUIRES-CURRENT`, `AUTH-NOSQL-OPERATOR-CREDENTIALS`, `INJ-NULL-BYTE`, `AUTH-REVOKED-COOKIE-RELOGIN`, `AUTH-LOGOUT-SCOPE`, `AUTH-SESSION-ID-NOT-EXPOSED`, `AUTH-SESSION-SLIDING-RENEWAL`, `AUTH-SESSION-FILTER-SCOPE`, `AUTH-LOGIN-CROSS-ACCOUNT-COOKIE`

## 26. INJ-NULL-BYTE

```yaml
id: INJ-NULL-BYTE
title: NUL-байт во входных данных отклоняется или не обрезает значение
category: security
protocols:
- rest
kind: security
priority: P2
preconditions:
- Есть строковые поля.
steps:
- action: Передать значение с NUL-байтом в конце и в середине (email входа, имя, путь).
expected:
- 4xx или значение сохраняется целиком; обрезки по NUL и входа под чужим значением нет.
applicability:
  when:
  - Есть строковые поля.
  skip_when:
  - Нет.
automation:
  level: full
  deterministic: true
references:
- CWE-158
- Смежная — VAL-SPECIAL-CHARACTERS
- postman BFF-Admin-Auth — тесты ссылаются на ID (inbox №21)
```

Исходные идеи (inbox):

- №21: **Записи для проверок, на которые уже ссылаются тесты postman, но которых нет в библиотеке**: `AUTH-PATH-NORMALIZATION-BYPASS` (31 тест), `AUTH-CREDENTIAL-CHANNEL-STRICT` (25), `AUTH-SESSION-VALUE-EXACT-MATCH` (20), `AUTH-DUPLICATE-CREDENTIALS` (5), `AUTH-SESSION-ID-ENTROPY` (2), `AUTH-PASSWORD-CHANGE-REQUIRES-CURRENT`, `AUTH-NOSQL-OPERATOR-CREDENTIALS`, `INJ-NULL-BYTE`, `AUTH-REVOKED-COOKIE-RELOGIN`, `AUTH-LOGOUT-SCOPE`, `AUTH-SESSION-ID-NOT-EXPOSED`, `AUTH-SESSION-SLIDING-RENEWAL`, `AUTH-SESSION-FILTER-SCOPE`, `AUTH-LOGIN-CROSS-ACCOUNT-COOKIE`

## 27. AUTH-REVOKED-COOKIE-RELOGIN

```yaml
id: AUTH-REVOKED-COOKIE-RELOGIN
title: Вход с закрытой cookie сессии создаёт новую сессию
category: security
protocols:
- rest
kind: positive
priority: P3
preconditions:
- Аутентификация на cookie-сессии.
steps:
- action: Закрыть сессию (выход) и выполнить вход, отправив в запросе её cookie.
expected:
- Вход успешен, выдана новая cookie; закрытая сессия не возобновляется.
applicability:
  when:
  - Cookie-сессии.
  skip_when:
  - Нет.
automation:
  level: full
  deterministic: true
references:
- Смежная — AUTH-SESSION-FIXATION
- postman BFF-Admin-Auth — тесты ссылаются на ID (inbox №21)
```

Исходные идеи (inbox):

- №21: **Записи для проверок, на которые уже ссылаются тесты postman, но которых нет в библиотеке**: `AUTH-PATH-NORMALIZATION-BYPASS` (31 тест), `AUTH-CREDENTIAL-CHANNEL-STRICT` (25), `AUTH-SESSION-VALUE-EXACT-MATCH` (20), `AUTH-DUPLICATE-CREDENTIALS` (5), `AUTH-SESSION-ID-ENTROPY` (2), `AUTH-PASSWORD-CHANGE-REQUIRES-CURRENT`, `AUTH-NOSQL-OPERATOR-CREDENTIALS`, `INJ-NULL-BYTE`, `AUTH-REVOKED-COOKIE-RELOGIN`, `AUTH-LOGOUT-SCOPE`, `AUTH-SESSION-ID-NOT-EXPOSED`, `AUTH-SESSION-SLIDING-RENEWAL`, `AUTH-SESSION-FILTER-SCOPE`, `AUTH-LOGIN-CROSS-ACCOUNT-COOKIE`

## 28. AUTH-LOGOUT-SCOPE

```yaml
id: AUTH-LOGOUT-SCOPE
title: Выход завершает только текущую сессию
category: security
protocols:
- rest
kind: positive
priority: P2
preconditions:
- Аутентификация на cookie-сессии.
steps:
- action: Войти одной учёткой дважды; выйти в одной сессии; запросить защищённый ресурс другой.
expected:
- Другие сессии учётки продолжают работать, если выход «везде» не заявлен.
applicability:
  when:
  - Несколько сессий на учётку.
  skip_when:
  - Нет.
automation:
  level: full
  deterministic: true
references:
- Смежная — AUTH-LOGOUT-INVALIDATES
- postman BFF-Admin-Auth — тесты ссылаются на ID (inbox №21)
```

Исходные идеи (inbox):

- №21: **Записи для проверок, на которые уже ссылаются тесты postman, но которых нет в библиотеке**: `AUTH-PATH-NORMALIZATION-BYPASS` (31 тест), `AUTH-CREDENTIAL-CHANNEL-STRICT` (25), `AUTH-SESSION-VALUE-EXACT-MATCH` (20), `AUTH-DUPLICATE-CREDENTIALS` (5), `AUTH-SESSION-ID-ENTROPY` (2), `AUTH-PASSWORD-CHANGE-REQUIRES-CURRENT`, `AUTH-NOSQL-OPERATOR-CREDENTIALS`, `INJ-NULL-BYTE`, `AUTH-REVOKED-COOKIE-RELOGIN`, `AUTH-LOGOUT-SCOPE`, `AUTH-SESSION-ID-NOT-EXPOSED`, `AUTH-SESSION-SLIDING-RENEWAL`, `AUTH-SESSION-FILTER-SCOPE`, `AUTH-LOGIN-CROSS-ACCOUNT-COOKIE`

## 29. AUTH-SESSION-ID-NOT-EXPOSED

```yaml
id: AUTH-SESSION-ID-NOT-EXPOSED
title: Список сессий не раскрывает значение cookie сессии
category: security
protocols:
- rest
kind: security
priority: P1
preconditions:
- Аутентификация на cookie-сессии.
steps:
- action: Запросить список сессий учётки.
expected:
- В ответе нет значений cookie и других секретов сессий — только их идентификаторы и метаданные.
applicability:
  when:
  - Есть список сессий.
  skip_when:
  - Нет.
automation:
  level: full
  deterministic: true
references:
- OWASP API3:2023
- postman BFF-Admin-Auth — тесты ссылаются на ID (inbox №21)
```

Исходные идеи (inbox):

- №21: **Записи для проверок, на которые уже ссылаются тесты postman, но которых нет в библиотеке**: `AUTH-PATH-NORMALIZATION-BYPASS` (31 тест), `AUTH-CREDENTIAL-CHANNEL-STRICT` (25), `AUTH-SESSION-VALUE-EXACT-MATCH` (20), `AUTH-DUPLICATE-CREDENTIALS` (5), `AUTH-SESSION-ID-ENTROPY` (2), `AUTH-PASSWORD-CHANGE-REQUIRES-CURRENT`, `AUTH-NOSQL-OPERATOR-CREDENTIALS`, `INJ-NULL-BYTE`, `AUTH-REVOKED-COOKIE-RELOGIN`, `AUTH-LOGOUT-SCOPE`, `AUTH-SESSION-ID-NOT-EXPOSED`, `AUTH-SESSION-SLIDING-RENEWAL`, `AUTH-SESSION-FILTER-SCOPE`, `AUTH-LOGIN-CROSS-ACCOUNT-COOKIE`

## 30. AUTH-SESSION-SLIDING-RENEWAL

```yaml
id: AUTH-SESSION-SLIDING-RENEWAL
title: Активность продлевает сессию по правилам скользящего срока
category: security
protocols:
- rest
kind: positive
priority: P3
preconditions:
- Аутентификация на cookie-сессии.
steps:
- action: Проявлять активность в сессии с интервалами меньше срока простоя и сравнить срок жизни до и после.
expected:
- Срок продлевается по заявленному правилу, не превышая абсолютного срока (AUTH-SESSION-TIMEOUT).
applicability:
  when:
  - Скользящий срок сессии.
  skip_when:
  - Нет.
automation:
  level: full
  deterministic: true
references:
- OWASP Session Management Cheat Sheet
- postman BFF-Admin-Auth — тесты ссылаются на ID (inbox №21)
```

Исходные идеи (inbox):

- №21: **Записи для проверок, на которые уже ссылаются тесты postman, но которых нет в библиотеке**: `AUTH-PATH-NORMALIZATION-BYPASS` (31 тест), `AUTH-CREDENTIAL-CHANNEL-STRICT` (25), `AUTH-SESSION-VALUE-EXACT-MATCH` (20), `AUTH-DUPLICATE-CREDENTIALS` (5), `AUTH-SESSION-ID-ENTROPY` (2), `AUTH-PASSWORD-CHANGE-REQUIRES-CURRENT`, `AUTH-NOSQL-OPERATOR-CREDENTIALS`, `INJ-NULL-BYTE`, `AUTH-REVOKED-COOKIE-RELOGIN`, `AUTH-LOGOUT-SCOPE`, `AUTH-SESSION-ID-NOT-EXPOSED`, `AUTH-SESSION-SLIDING-RENEWAL`, `AUTH-SESSION-FILTER-SCOPE`, `AUTH-LOGIN-CROSS-ACCOUNT-COOKIE`

## 31. AUTH-SESSION-FILTER-SCOPE

```yaml
id: AUTH-SESSION-FILTER-SCOPE
title: Операции над сессиями ограничены сессиями своей учётки
category: security
protocols:
- rest
kind: security
priority: P1
preconditions:
- Аутентификация на cookie-сессии.
steps:
- action: Администратором или пользователем завершить сессию другой учётки по её идентификатору.
expected:
- 404 или 403; чужая сессия продолжает работать, если право на это не заявлено.
applicability:
  when:
  - Есть управление сессиями.
  skip_when:
  - Нет.
automation:
  level: full
  deterministic: true
references:
- OWASP API1:2023
- Смежная — SEC-OWNERSHIP-DELETE
- postman BFF-Admin-Auth — тесты ссылаются на ID (inbox №21)
```

Исходные идеи (inbox):

- №21: **Записи для проверок, на которые уже ссылаются тесты postman, но которых нет в библиотеке**: `AUTH-PATH-NORMALIZATION-BYPASS` (31 тест), `AUTH-CREDENTIAL-CHANNEL-STRICT` (25), `AUTH-SESSION-VALUE-EXACT-MATCH` (20), `AUTH-DUPLICATE-CREDENTIALS` (5), `AUTH-SESSION-ID-ENTROPY` (2), `AUTH-PASSWORD-CHANGE-REQUIRES-CURRENT`, `AUTH-NOSQL-OPERATOR-CREDENTIALS`, `INJ-NULL-BYTE`, `AUTH-REVOKED-COOKIE-RELOGIN`, `AUTH-LOGOUT-SCOPE`, `AUTH-SESSION-ID-NOT-EXPOSED`, `AUTH-SESSION-SLIDING-RENEWAL`, `AUTH-SESSION-FILTER-SCOPE`, `AUTH-LOGIN-CROSS-ACCOUNT-COOKIE`

## 32. AUTH-LOGIN-CROSS-ACCOUNT-COOKIE

```yaml
id: AUTH-LOGIN-CROSS-ACCOUNT-COOKIE
title: Вход другой учёткой с cookie действующей сессии обрабатывается по правилу
category: security
protocols:
- rest
kind: security
priority: P2
preconditions:
- Аутентификация на cookie-сессии.
steps:
- action: Войти учёткой A; выполнить вход учёткой B, отправив cookie сессии A.
expected:
- Документированное поведение (например, 409 и закрытие сессии A); сессия A не переходит к B, данные не смешиваются.
applicability:
  when:
  - Cookie-сессии.
  skip_when:
  - Нет.
automation:
  level: full
  deterministic: true
references:
- Смежная — AUTH-SESSION-FIXATION
- postman BFF-Admin-Auth — тесты ссылаются на ID (inbox №21)
```

Исходные идеи (inbox):

- №21: **Записи для проверок, на которые уже ссылаются тесты postman, но которых нет в библиотеке**: `AUTH-PATH-NORMALIZATION-BYPASS` (31 тест), `AUTH-CREDENTIAL-CHANNEL-STRICT` (25), `AUTH-SESSION-VALUE-EXACT-MATCH` (20), `AUTH-DUPLICATE-CREDENTIALS` (5), `AUTH-SESSION-ID-ENTROPY` (2), `AUTH-PASSWORD-CHANGE-REQUIRES-CURRENT`, `AUTH-NOSQL-OPERATOR-CREDENTIALS`, `INJ-NULL-BYTE`, `AUTH-REVOKED-COOKIE-RELOGIN`, `AUTH-LOGOUT-SCOPE`, `AUTH-SESSION-ID-NOT-EXPOSED`, `AUTH-SESSION-SLIDING-RENEWAL`, `AUTH-SESSION-FILTER-SCOPE`, `AUTH-LOGIN-CROSS-ACCOUNT-COOKIE`

## 33. INJ-DOWNSTREAM-BODY-INJECTION

```yaml
id: INJ-DOWNSTREAM-BODY-INJECTION
title: Значение поля не внедряет ключи в тело запроса к другой системе
category: security
protocols:
- generic
kind: security
priority: P1
preconditions:
- Сервис пересылает данные пользователя дальше — в другой API, очередь, XML- или JSON-сообщение; есть наблюдение
  за нижестоящим запросом.
steps:
- action: 'Передать значения вида x", "role": "admin", "y": " и </name><role>admin</role><name>; посмотреть тело
    нижестоящего запроса и результат.'
expected:
- Значение передаётся экранированным как одно поле; новых ключей и элементов в нижестоящем запросе нет.
applicability:
  when:
  - Есть пересылка данных в другие системы.
  skip_when:
  - Нет.
automation:
  level: partial
  deterministic: true
references:
- CWE-74, CWE-91
- inbox №47
```

Исходные идеи (inbox):

- №47: **Инъекция в тело запроса к третьей системе** (JSON/XML injection при пересылке): значение поля вида `x", "role": "admin", "y": "` — сервер, который пересылает его дальше (другой API, очередь сообщений), не собирает тело склейкой строк; в нижестоящий запрос не попадают новые ключи

## Индекс библиотеки

Все записи (550): ID | категория | заголовок.

```text
ASYNC-DEAD-LETTER | async | Необрабатываемые сообщения уходят в DLQ без блокировки очереди
ASYNC-EVENT-ORDERING | async | Нарушение порядка событий не портит состояние
ASYNC-EVENT-PATH-SAME-RULES | async | Событийный путь применяет те же фильтры и границы доступа, что и плановый
ASYNC-IDEMPOTENT-CONSUMER | async | Повторная доставка события обрабатывается однократно
ASYNC-JOB-CANCEL | async | Отмена фоновой задачи останавливает её и не оставляет частичных эффектов
ASYNC-JOB-LIFECYCLE | async | Фоновая задача проходит статусы и отдаёт результат
ASYNC-MESSAGE-VALIDATION | async | Входящие сообщения брокера валидируются по схеме так же, как HTTP-запросы
ASYNC-OUTBOUND-REQUEST-HEADERS | async | Исходящий запрос сервера содержит корректный Host, в том числе с нестандартным портом
ASYNC-RPC-ERROR-PROPAGATION | async | Ошибка обработчика в схеме запрос-ответ через брокер возвращается вызывающему
ASYNC-SCHEDULE-DST-TRANSITION | async | Расписание на несуществующее или повторяющееся местное время срабатывает по правилу
ASYNC-SCHEDULE-LONG-UPTIME | async | Задача по расписанию срабатывает и после длительной непрерывной работы процесса
ASYNC-SSE-STREAM | async | Потоковый ответ SSE работает для всех методов и отдаёт text/event-stream
ASYNC-WEBHOOK-RETRY | async | Неуспешная доставка вебхука повторяется с backoff и ограничением
ASYNC-WEBHOOK-SIGNATURE | async | Вебхуки подписаны, подпись проверяется, повтор отклоняется
ASYNC-WEBHOOK-URL-SSRF | async | URL вебхука не может указывать на внутренние адреса
AUTH-ACCOUNT-STATE-ALL-SCHEMES | security | Отключённая, заблокированная или истёкшая учётка не аутентифицируется ни одной схемой
AUTH-API-KEY-LIFECYCLE | security | API-ключи ограничены по правам, отзываются и не раскрываются
AUTH-BASIC-CREDENTIALS-SPECIAL-CHARS | security | Basic-аутентификация принимает пароль с двоеточием, пробелами и UTF-8
AUTH-BRUTE-FORCE-PROTECTION | security | Перебор паролей ограничивается
AUTH-CLIENT-ASSERTION-BINDING | security | Client assertion принимается только с ключом клиента, указанного в ней
AUTH-CLIENT-CERT-IDENTITY | security | Личность из сертификата клиента извлекается однозначно
AUTH-CONCURRENT-SESSIONS | security | Лимит одновременных сессий и устройств соблюдается
AUTH-CONTACT-CHANGE-PREVIOUS-VALUE | security | Смена телефона или email на ранее использованный этим пользователем проходит подтверждение
AUTH-COOKIE-ATTRIBUTES | security | Сессионные cookie имеют Secure, HttpOnly, SameSite и узкие Domain/Path
AUTH-CREDENTIAL-CHANNEL-STRICT | security | Учётные данные принимаются только по документированному каналу
AUTH-CSRF | security | Изменяющие операции с cookie-аутентификацией защищены от CSRF
AUTH-DUPLICATE-CREDENTIALS | security | Повторяющиеся и пустые учётные данные не дают доступа
AUTH-EXTERNAL-ID-EXACT-MATCH | security | Внешний идентификатор субъекта сравнивается побайтно в паре издатель и subject
AUTH-EXTERNAL-IDP-MISSING-ATTRIBUTES | security | Вход через внешний IdP без необязательных атрибутов профиля обрабатывается по требованиям
AUTH-EXTERNAL-IDP-UNVERIFIED-EMAIL | security | Вход через внешний IdP не связывается с учёткой по неподтверждённому email
AUTH-GENERATED-SECRET-STRENGTH | security | Сгенерированные сервером секреты имеют стойкость не ниже требуемой алгоритмом
AUTH-IDENTITY-ATTRIBUTES-ALL-SCHEMES | security | Атрибуты идентичности, которые даёт источник, сохраняются при любом способе аутентификации
AUTH-IMPORTED-PASSWORD-HASH | security | Пользователь, импортированный с хешем пароля поддерживаемого алгоритма, входит по исходному паролю
AUTH-JWT-ALG-CONFUSION | security | Подмена алгоритма RS256 на HS256 с публичным ключом не принимается
AUTH-JWT-ALG-NONE | security | JWT с alg=none отклоняется
AUTH-JWT-HEADER-INJECTION | security | Параметры kid, jku, x5u в заголовке JWT не позволяют подставить ключ
AUTH-JWT-TIME-CLAIMS | security | Токены с nbf/iat в будущем и без exp обрабатываются по политике
AUTH-JWT-VALID-ACCEPTED | security | Валидный токен принимается при всех поддерживаемых алгоритмах, наборах ключей и настройках claims
AUTH-LOGIN-CROSS-ACCOUNT-COOKIE | security | Вход другой учёткой с cookie действующей сессии обрабатывается по правилу
AUTH-LOGIN-IDENTIFIER-NORMALIZATION | validation | Логин (email, телефон) нормализуется одинаково при входе, создании и поиске
AUTH-LOGOUT-CLEARS-COOKIE | security | Выход снимает cookie сессии на клиенте
AUTH-LOGOUT-INVALIDATES | security | После выхода токен и сессия недействительны
AUTH-LOGOUT-SCOPE | security | Выход завершает только текущую сессию
AUTH-MFA-STEP-UP | security | Операции, требующие второго фактора, недоступны без него
AUTH-MFA-UNENROLLED-ERROR | security | Ошибка шага второго фактора у пользователя без зарегистрированного фактора — обычная 4xx
AUTH-NOSQL-OPERATOR-CREDENTIALS | security | Операторы NoSQL в учётных данных входа отклоняются
AUTH-OAUTH-OUTBOUND-SCOPE | security | Запрос авторизации к внешнему провайдеру содержит запрошенные scope без устаревших значений по умолчанию
AUTH-OAUTH-PAR | security | Pushed Authorization Request действует как прямой запрос авторизации и не ограничивает длительность входа
AUTH-OAUTH-PUBLIC-CLIENT-CONSENT | security | Повторная авторизация публичного OAuth-клиента не выполняется без участия пользователя
AUTH-OAUTH-REDIRECT-STATE | security | OAuth/OIDC flow проверяет redirect_uri, state и PKCE
AUTH-OAUTH-RESOURCE-INDICATOR | security | Индикатор ресурса, не соответствующий аудитории клиента, даёт 400 invalid_target
AUTH-OTP-ATTEMPT-LIMIT | security | Количество попыток ввода одноразового кода ограничено
AUTH-OTP-BINDING | security | Одноразовый код привязан к получателю и операции
AUTH-OTP-EXPIRY | security | Одноразовый код перестаёт действовать после истечения срока
AUTH-OTP-REUSE | security | Одноразовый код нельзя использовать повторно и после выдачи нового
AUTH-OTP-SEND-LIMIT | security | Частота отправки кодов ограничена (SMS bombing)
AUTH-PASSWORD-CHANGE-REQUIRES-CURRENT | security | Смена пароля требует верный текущий пароль
AUTH-PASSWORD-CHANGE-REVOKES | security | Смена или сброс пароля завершает другие сессии
AUTH-PASSWORD-POLICY | security | Политика паролей применяется на сервере
AUTH-PASSWORD-RESET-TOKEN | security | Токен сброса пароля одноразовый, ограничен по времени и привязан к пользователю
AUTH-PATH-NORMALIZATION-BYPASS | security | Вариации пути защищённого маршрута не обходят аутентификацию
AUTH-PROTOCOL-SESSION-OWNER-BINDING | security | Идентификатор протокольной сессии привязан к аутентифицированному владельцу
AUTH-REFRESH-PRESERVES-SCOPE | security | Refresh без параметра scope сохраняет scope исходной авторизации
AUTH-REVOKED-COOKIE-RELOGIN | security | Вход с закрытой cookie сессии создаёт новую сессию
AUTH-SAML-ASSERTION-REPLAY | security | Повторно предъявленное SAML-утверждение отклоняется
AUTH-SENSITIVE-CHANGE-REAUTH | security | Изменение защиты учётки требует свежей аутентификации
AUTH-SESSION-FILTER-SCOPE | security | Операции над сессиями ограничены сессиями своей учётки
AUTH-SESSION-FIXATION | security | Идентификатор сессии меняется после входа
AUTH-SESSION-ID-ENTROPY | security | Идентификатор сессии новый при каждом входе, уникален и непредсказуем
AUTH-SESSION-ID-NOT-EXPOSED | security | Список сессий не раскрывает значение cookie сессии
AUTH-SESSION-NOT-BEFORE-LOGIN | security | Анонимный запрос не получает cookie сессии и не создаёт серверную сессию
AUTH-SESSION-SLIDING-RENEWAL | security | Активность продлевает сессию по правилам скользящего срока
AUTH-SESSION-TIMEOUT | security | Сессия истекает после простоя и абсолютного срока
AUTH-SESSION-VALUE-EXACT-MATCH | security | Значение сессии сравнивается целиком и точно
AUTH-TOKEN-IN-URL | security | Учётные данные не передаются и не принимаются в URL
AUTH-TOKEN-INTROSPECTION | security | Интроспекция токена возвращает актуальное состояние и те же claims, что в токене
AUTH-TOKEN-RESERVED-CLAIMS | security | Пользовательские поля не переопределяют зарезервированные claims токена
AUTH-TOKEN-SENDER-CONSTRAINED | security | Обмен и обновление токена сохраняют привязку к отправителю (DPoP, mTLS)
AUTH-TOKEN-TYPE-CONFUSION | security | Refresh, ID или сервисный токен не принимается как access-токен
AUTH-USER-ENUMERATION | security | Ответы входа, регистрации и восстановления не раскрывают существование аккаунта
BIZ-AMBIGUOUS-ADDRESS | business-logic | Неоднозначный почтовый адрес не выбирается молча по первому совпадению
BIZ-CLIENT-PRICE-TAMPERING | business-logic | Цена, скидка и итог рассчитываются на сервере
BIZ-CONFIG-SCOPE-PRECEDENCE | business-logic | Настройка более узкого уровня имеет приоритет над глобальной
BIZ-CURRENCY-MISMATCH | business-logic | Смешение валют в операции обрабатывается явно
BIZ-DIVISION-BY-ZERO | business-logic | Входы с нулём в знаменателе не дают 500 и нечисловых значений
BIZ-DOUBLE-SPEND | business-logic | Параллельные списания не приводят к двойной трате
BIZ-EMAIL-LINK-CROSS-SESSION | business-logic | Ссылка-действие из письма работает в другой сессии и после перезапуска сервиса
BIZ-EMAIL-NOTIFICATION-DELIVERY | business-logic | Письма уходят нужному адресату с верными ссылками и без внедрения заголовков
BIZ-FLAG-EFFECT-MATRIX | business-logic | Каждый флаг сущности влияет на поведение так, как описано
BIZ-HIERARCHY-CYCLES | business-logic | Ссылка на себя и циклы в иерархии запрещены
BIZ-LIMITS-QUOTAS | business-logic | Лимиты и квоты соблюдаются на границе и не обходятся параллельно
BIZ-NEGATIVE-QUANTITY | business-logic | Отрицательные и нулевые количества и суммы не дают выгоды
BIZ-ONE-TIME-BENEFIT-REUSE | business-logic | Одноразовые промокоды, бонусы и приглашения нельзя использовать повторно
BIZ-ROUNDING | business-logic | Округление денежных величин корректно и не накапливает ошибку
BIZ-SIDE-EFFECTS-ONCE | business-logic | Побочные эффекты (письма, push, события) выполняются ровно один раз
BIZ-TIME-WINDOW | business-logic | Операции вне разрешённого временного окна отклоняются
BIZ-WORKFLOW-STEP-SKIP | business-logic | Нельзя пропустить обязательный шаг бизнес-процесса
COMPAT-ADDITIVE-CHANGE | compatibility | Добавление полей не ломает существующих клиентов
COMPAT-BREAKING-CHANGE-DIFF | compatibility | Изменения контракта проверяются на обратную несовместимость
COMPAT-DEFAULT-VERSION | compatibility | Запрос без указания версии обслуживается задокументированной версией
COMPAT-DEPRECATION-SIGNALS | compatibility | Устаревающие операции помечены Deprecation и Sunset
COMPAT-ENUM-EXTENSION | compatibility | Добавление значения enum не ломает клиентов
COMPAT-IMPLEMENTATION-MATCHES-CONTRACT | compatibility | Реализация соответствует опубликованному контракту
COMPAT-MIXED-VERSION-WRITE-STABILITY | compatibility | Экземпляры разных версий при поэтапном обновлении не перезаписывают общий объект по кругу
COMPAT-UPGRADE-STORED-DATA-STABLE | compatibility | Обновление сервера не меняет сохранённые объекты и не запускает побочных действий
CONC-COUNTER-INCREMENT | concurrency | Счётчики корректны при параллельных инкрементах
CONC-DELETE-VS-UPDATE | concurrency | Параллельные удаление и изменение не оставляют ресурс в противоречивом состоянии
CONC-DOUBLE-SUBMIT | concurrency | Двойная отправка формы не создаёт дубликат операции
CONC-LOST-UPDATE | concurrency | Параллельные изменения не теряют друг друга молча
CONC-PARALLEL-CREATE-UNIQUE | concurrency | Параллельное создание с одним уникальным ключом создаёт один объект
CONC-PARALLEL-INDEPENDENT | concurrency | Параллельные независимые запросы одной операции выполняются без 5xx
CONC-REQUEST-CONTEXT-ISOLATION | concurrency | Параллельные запросы разных пользователей получают только свой контекст и свой ответ
CONC-STATE-TRANSITION-RACE | concurrency | Параллельные переходы состояния не нарушают автомат состояний
CONTRACT-FIELD-SELECTION | contract | Выбор полей возвращает ровно запрошенные поля с правильными значениями
CONTRACT-PUBLISHED-SCHEMA-VALID | contract | Опубликованные сервисом описания API валидны в заявленном диалекте
CONTRACT-REQUIRED-FIELDS | contract | Successful response contains required contract fields
CONTRACT-RESPONSE-LINKS-RESOLVE | contract | URL в ответах открываются
CONTRACT-UNKNOWN-FIELD-POLICY | contract | Unknown fields follow the documented contract policy
DB-ACCESS-SCOPE-IN-QUERY | db | Граница доступа задаётся в самом запросе к БД
DB-API-DATA-MATCH | db | После операции API в БД изменены ровно ожидаемые строки с ожидаемыми значениями
DB-CATALOG-INTROSPECTION | db | Чтение каталога схемы корректно и укладывается во время на больших схемах
DB-COLLATION-COMPARISON | db | Сравнение строк в БД соответствует назначению колонки
DB-CONNECTION-HANDLING | db | Соединения с БД управляются предсказуемо
DB-DEFAULT-PRECEDENCE | db | Значения по умолчанию применяются по правилам СУБД при любом способе вставки
DB-DYNAMIC-SQL-PARAMETERIZED | db | Значения и идентификаторы из ввода и из БД попадают в SQL параметрами или по allowlist
DB-GENERATED-SQL-SHAPE | db | Генерируемый SQL не выполняет лишней работы
DB-IDENTIFIER-QUOTING | db | Имена объектов БД экранируются во всех служебных и генерируемых запросах
DB-IMPORT-CONSISTENCY | db | Импорт не оставляет частичного состояния вне документированной политики
DB-KEYS-AND-CONSTRAINTS | db | Ключи и ограничения защищают целостность независимо от приложения
DB-METADATA-CACHE-FRESH | db | Кэш метаданных схемы в сервисе актуален после изменений БД
DB-MIGRATIONS-SAFE | db | Миграции схемы применяются предсказуемо и не портят данные
DB-QUERY-INDEX-USAGE | db | Запросы приложения используют подходящие индексы на реалистичном объёме
DB-ROLES-AND-PRIVILEGES | db | Роли БД приложения имеют минимальные права, переключение ролей безопасно
DB-SCHEMA-MATCHES-SPEC | db | Схема БД совпадает со спецификацией и контрактом API
DB-SENSITIVE-DATA-PROTECTED | db | Чувствительные данные хранятся защищённо
DB-STORED-ROUTINES | db | Хранимые процедуры и функции установлены и работают по спецификации
DB-TRIGGERS | db | Триггеры срабатывают ровно на нужные события и изолированы
DB-TYPED-COMPARISONS | db | Значения сравниваются и приводятся в типе колонки
ERR-INTERNAL-ERROR-SHAPE | errors | Внутренняя ошибка сервера возвращается в общей модели без утечек
ERR-STABLE-ERROR-CODES | errors | Машиночитаемые коды ошибок стабильны и задокументированы
ERR-STATUS-MATCHES-EFFECT | errors | Код ответа соответствует фактическому результату операции
FILE-ABORTED-UPLOAD-CLEANUP | files | Прерванная загрузка не оставляет данных в хранилище и не учитывается в квоте
FILE-ARCHIVE-BOMB | files | Архивные и графические бомбы не исчерпывают ресурсы
FILE-DOWNLOAD-AUTHZ | files | Скачивание файлов проверяет права и срок действия ссылок
FILE-DOWNLOAD-HEADERS | files | Скачивание отдаёт корректные Content-Type, Content-Disposition и nosniff
FILE-EMPTY-AND-MALFORMED-MULTIPART | files | Пустой файл и некорректный multipart обрабатываются корректно
FILE-FILENAME-SANITIZATION | files | Имя загружаемого файла санитизируется
FILE-MALFORMED-STRUCTURE | files | Повреждённый файл при разборе метаданных даёт 4xx, а не падение процесса
FILE-MALICIOUS-CONTENT | files | Вредоносное содержимое обнаруживается или изолируется
FILE-METADATA-STRIP | files | Метаданные изображений с ПДн удаляются
FILE-MULTIPART-METADATA-SAVED | files | Метаданные из полей multipart сохраняются вместе с файлом
FILE-RANGE-REQUESTS | files | Частичное скачивание через Range работает по контракту
FILE-ROUNDTRIP-EXACT | files | Загруженный файл скачивается байт в байт
FILE-TRANSFORM-LIMITS | files | Лимит трансформации файла пропускает допустимые комбинации и отклоняет превышение
FILE-TRANSFORM-STORAGE-PARITY | files | Трансформации файла работают на каждом поддерживаемом хранилище
FILE-UPLOAD-KEY-COLLISION | files | Загрузка не перезаписывает чужой файл с тем же именем или ключом хранилища
FILE-UPLOAD-SIZE-LIMIT | files | Лимит размера загружаемого файла соблюдается
FILE-UPLOAD-TYPE-VALIDATION | files | Тип файла проверяется по содержимому, а не только по расширению
GQL-ALIAS-BATCH-ABUSE | graphql | Алиасы и batch-запросы не обходят rate limit
GQL-COMPLEXITY-LIMIT | graphql | Стоимость запроса ограничена (поля, списки, first/last)
GQL-CSRF-GET-MUTATION | graphql | Мутации не выполняются через GET и простые Content-Type
GQL-DEPTH-LIMIT | graphql | Глубина запроса ограничена
GQL-EQUIVALENT-SELECTION-FORMS | graphql | Эквивалентные формы выбора полей GraphQL дают одинаковые данные
GQL-ERROR-EXTENSIONS-SHAPE | graphql | Поля extensions ошибки GraphQL не дублируются во вложенных объектах
GQL-ERRORS-NO-LEAK | graphql | Ошибки GraphQL не раскрывают внутренние детали
GQL-FIELD-LEVEL-AUTHZ | graphql | Авторизация применяется на уровне полей и вложенных резолверов
GQL-FIELD-SUGGESTIONS | graphql | Подсказки «Did you mean» не раскрывают схему при закрытом introspection
GQL-GATEWAY-ROUTING | graphql | В объединённой схеме каждое поле направляется в свой upstream
GQL-INPUT-VALIDATION | graphql | Входные типы и переменные валидируются
GQL-INTROSPECTION | graphql | Introspection отключён или ограничен в продуктиве
GQL-PARTIAL-DATA | graphql | Частичные результаты с ошибками соответствуют спецификации nullability
GQL-REST-ENDPOINT-PARITY | graphql | Операция, опубликованная как REST-эндпоинт, выполняется так же, как исходный GraphQL-запрос
GRPC-BIDI-FLOW-CONTROL | grpc-contract | Двунаправленный стрим соблюдает flow control при медленном клиенте
GRPC-CANCELLATION | grpc-errors | Отмена клиентом прекращает обработку на сервере
GRPC-CLIENT-STREAM-PARTIAL-FAILURE | grpc-contract | Ошибка в середине клиентского стрима обрабатывается по контракту
GRPC-COMPRESSION | grpc-contract | Сжатие сообщений согласуется и неподдерживаемое отклоняется
GRPC-DEADLINE-EXCEEDED | grpc-errors | Превышение дедлайна возвращает DEADLINE_EXCEEDED без побочных эффектов сверх контракта
GRPC-DEADLINE-PROPAGATION | grpc-errors | Дедлайн передаётся в нижележащие вызовы
GRPC-ENUM-UNKNOWN-VALUE | grpc-contract | Неизвестное и нулевое значение enum обрабатывается явно
GRPC-ERROR-DETAILS | grpc-errors | Ошибки содержат структурированные детали google.rpc.Status
GRPC-FIELD-PRESENCE | grpc-contract | Значение по умолчанию отличается от неустановленного поля, где это важно
GRPC-HEALTH-PROTOCOL | grpc-contract | Стандартный health-протокол gRPC реализован корректно
GRPC-JSON-TRANSCODING | grpc-contract | HTTP/JSON транскодирование соответствует proto-аннотациям
GRPC-KEEPALIVE-POLICY | grpc-errors | Агрессивные keepalive-пинги клиента ограничиваются
GRPC-MAX-MESSAGE-SIZE | grpc-contract | Сообщения больше лимита отклоняются RESOURCE_EXHAUSTED
GRPC-METADATA-AUTH-MISSING | grpc-errors | Каждый RPC сервиса требует аутентификационные метаданные
GRPC-METADATA-MALFORMED | grpc-errors | Некорректные и чрезмерные метаданные отклоняются
GRPC-NOT-FOUND-ALREADY-EXISTS | grpc-errors | Отсутствующий и дублирующийся ресурс дают NOT_FOUND и ALREADY_EXISTS
GRPC-ONEOF | grpc-contract | Поля oneof валидируются и не установлены одновременно
GRPC-PRECONDITION-ABORTED | grpc-errors | FAILED_PRECONDITION и ABORTED используются согласно семантике повтора
GRPC-PROTO-BREAKING | grpc-contract | Изменения proto не ломают совместимость wire и JSON
GRPC-REFLECTION-EXPOSURE | grpc-contract | Server reflection отключён или защищён в продуктиве
GRPC-REPEATED-BOUNDARIES | grpc-contract | Repeated и map поля: пусто, много элементов, дубликаты ключей
GRPC-REQUEST-VALIDATION | grpc-contract | Invalid gRPC request is rejected predictably
GRPC-RESOURCE-EXHAUSTED | grpc-errors | Превышение квот возвращает RESOURCE_EXHAUSTED с RetryInfo
GRPC-RETRY-POLICY | grpc-errors | Автоматические повторы применяются только к безопасным методам и статусам
GRPC-SERVER-STREAM-COMPLETE | grpc-contract | Серверный стрим отдаёт все элементы по порядку и завершается OK
GRPC-STATUS-MAPPING | grpc-errors | RPC errors use documented gRPC status codes
GRPC-STREAM-AUTH-EXPIRY | grpc-errors | Длительный стрим учитывает истечение и отзыв токена
GRPC-STREAM-RESOURCE-LIMITS | grpc-errors | Число одновременных стримов и их длительность ограничены
GRPC-STREAM-TERMINATION | grpc-contract | Streaming RPC terminates correctly
GRPC-TLS-MTLS | grpc-errors | Транспорт защищён TLS, при mTLS клиентский сертификат обязателен
GRPC-UNAUTHENTICATED-VS-PERMISSION-DENIED | grpc-errors | Отсутствие аутентификации и отсутствие прав различаются по статусу
GRPC-UNKNOWN-FIELDS | grpc-contract | Неизвестные поля сообщения обрабатываются по политике совместимости
GRPC-WELL-KNOWN-TYPES | grpc-contract | Timestamp, Duration и другие well-known types валидируются по диапазонам
HARD-BACKUP-RESTORE-PROTECTED | security | Восстановление из резервной копии не обходит защиту записи
HARD-BUSINESS-FLOW-AUTOMATION | security | Чувствительные бизнес-потоки защищены от автоматизированного злоупотребления
HARD-CACHE-POISONING | security | Неключевые заголовки не отравляют общий кэш
HARD-CLIENT-IP-TRUSTED-PROXIES | security | IP клиента определяется по цепочке доверенных прокси одинаково на всех маршрутах
HARD-DEBUG-ENDPOINTS | security | Отладочные и служебные эндпоинты недоступны извне
HARD-DENYLIST-EVERY-ENTRY | security | Каждый элемент списка запрещённых значений отклоняется
HARD-ENVIRONMENT-ISOLATION | security | Тестовый стенд не обращается к ресурсам production
HARD-EXCESSIVE-DATA-EXPOSURE | security | Ответы не содержат внутренних полей сверх контракта
HARD-EXPENSIVE-OPERATION-LIMITS | security | Дорогие операции ограничены по ресурсам
HARD-HOST-HEADER | security | Подмена Host и X-Forwarded-Host не влияет на ссылки и маршрутизацию
HARD-ID-PREDICTABILITY | security | Предсказуемые идентификаторы не позволяют собрать данные перебором
HARD-IP-ALLOWLIST | security | Ограничение доступа по адресам и подсетям работает на границах для IPv4 и IPv6
HARD-METHOD-OVERRIDE | security | Заголовки переопределения метода не обходят авторизацию
HARD-NOT-IMPLEMENTED-INERT | security | Операция, помеченная в контракте как нереализованная, не выполняется
HARD-OUTBOUND-CREDENTIALS-SCOPE | security | Учётные данные своего сайта не уходят в исходящие запросы к другим хостам
HARD-ROUTE-SHARED-BACKEND-ISOLATION | security | Маршруты шлюза к одному бэкенду применяют каждый свои фильтры
HARD-SENSITIVE-DATA-IN-URL | security | Персональные данные и секреты не передаются в URL
HARD-SETUP-ENDPOINTS-PROTECTED | security | Эндпоинты первоначальной настройки не позволяют захватить экземпляр
HARD-SHADOW-API-VERSIONS | security | Старые версии API и недокументированные маршруты не обходят защиту
HARD-SLOW-CLIENT-LIMITS | security | Медленные и неполные запросы и непрочитанные ответы не накапливаются без ограничения
HARD-TLS-ONLY | security | API доступен только по TLS с актуальными настройками
HARD-UNSAFE-API-CONSUMPTION | security | Ответы сторонних API валидируются перед использованием
HARD-VERSION-DISCLOSURE | security | Ответы не раскрывают версии ПО и инфраструктуры
HARD-WILDCARD-DOMAIN-MATCH | security | Шаблон домена с wildcard совпадает только с поддоменами указанного домена
HTTP-ABSOLUTE-URL-BASE-PATH | http-semantics | Абсолютные URL, которые формирует сервер, учитывают публичный адрес и базовый путь
HTTP-ACCEPT-LANGUAGE | http-semantics | Язык сообщений определяется Accept-Language с fallback
HTTP-BODY-ON-GET-DELETE | http-semantics | Тело в GET/DELETE игнорируется или отклоняется по контракту
HTTP-BODY-WITHOUT-CONTENT-TYPE | http-semantics | Тело без Content-Type обрабатывается предсказуемо
HTTP-CACHEABLE-RESPONSE-CACHE-CONTROL | http-semantics | Кэшируемый ответ содержит Cache-Control по итоговой политике
HTTP-COMPRESSION | http-semantics | Сжатие ответа согласуется через Accept-Encoding
HTTP-HEADER-REPEATED-LINES-ACCEPTED | http-semantics | Сотни повторяющихся строк одного заголовка в пределах лимита размера принимаются одинаково по HTTP/1.1 и HTTP/2
HTTP-HEADER-SIZE-LIMIT | http-semantics | Слишком большие заголовки отклоняются контролируемо
HTTP-HTTP2-RESOURCE-LIMITS | http-semantics | Параметры HTTP/2 со стороны клиента не заставляют сервер буферизовать и работать без предела
HTTP-OPTIONS-ALLOW | http-semantics | OPTIONS возвращает согласованный список методов
HTTP-PATH-PREFIX-SEGMENT-BOUNDARY | http-semantics | Правило по префиксу пути соблюдает границу сегмента
HTTP-PREFERENCE-APPLIED-ACCURATE | http-semantics | Preference-Applied перечисляет ровно применённые предпочтения
HTTP-REDIRECT-ENDPOINT-PARITY | http-semantics | Вызов через перенаправляющий адрес работает как прямой вызов
HTTP-REQUEST-SMUGGLING | http-semantics | Противоречивые Content-Length и Transfer-Encoding не приводят к request smuggling
HTTP-RESPONSE-FRAMING-HEADERS | http-semantics | Ответ не содержит одновременно Content-Length и Transfer-Encoding
HTTP-RESPONSE-MODE-HEADER-PARITY | http-semantics | Настроенные заголовки ответа присутствуют во всех режимах обработки ответа
HTTP-ROUTE-PROTOCOL-CONDITION | http-semantics | Условие маршрута для одного протокола не блокирует маршрут по другому разрешённому протоколу
HTTP-TRAILING-SLASH-CASE | http-semantics | Вариации пути (слэш в конце, регистр, двойной слэш) обрабатываются единообразно
HTTP-UNKNOWN-ROUTE | http-semantics | Неизвестный маршрут возвращает 404, а не 5xx или 200
HTTP-URL-LENGTH-LIMIT | http-semantics | Очень длинный URL отклоняется контролируемо
HTTP-VARY-HEADER | http-semantics | Кэшируемые ответы содержат корректный Vary
HTTP-VERSION-PARITY | http-semantics | Запросы по HTTP/2 и с предложением Upgrade h2c обслуживаются так же, как по HTTP/1.1
HTTP-WWW-AUTHENTICATE-SYNTAX | http-semantics | Заголовок WWW-Authenticate в ответе 401 соответствует синтаксису RFC
INJ-ARCHIVE-ENTRY-NAME-EVAL | security | Имена файлов внутри загруженного репозитория или архива не исполняются как код
INJ-CSV-FORMULA | security | Экспорт в CSV/XLSX нейтрализует формулы
INJ-DOWNSTREAM-BODY-INJECTION | security | Значение поля не внедряет ключи в тело запроса к другой системе
INJ-FILTER-EXPRESSION | security | Выражения фильтрации (OData, RSQL, JSONPath, GraphQL where) не позволяют выйти за ограничения
INJ-HEADER-CRLF | security | CRLF в значениях не позволяет внедрять заголовки ответа
INJ-LLM-GENERATED-ACTIONS | security | Код и вызовы инструментов, сгенерированные LLM по вводу пользователя, не выполняют опасных действий
INJ-LOG-FORGING | security | Пользовательские данные не позволяют подделывать записи журналов
INJ-NOSQL | security | NoSQL-инъекция операторами запросов не исполняется
INJ-NULL-BYTE | security | NUL-байт во входных данных отклоняется или не обрезает значение
INJ-OS-COMMAND | security | Инъекция команд ОС не исполняется
INJ-PATH-TRAVERSAL | security | Обход каталогов через параметры файлов и путей невозможен
INJ-PROTOTYPE-POLLUTION | security | Специальные ключи __proto__ и constructor не меняют поведение сервера
INJ-REDOS | security | Пользовательский ввод не вызывает катастрофический backtracking в regex
INJ-REFLECTED-XSS | security | Параметры запроса не отражаются в HTML-ответе без экранирования
INJ-RESERVED-PATH-WRITE | security | Запись файлов через API не попадает в служебные каталоги
INJ-SCHEMA-IDENTIFIER-CODEGEN | security | Идентификаторы пользовательской схемы не внедряют код и SQL при генерации кода и DDL
INJ-SQL | security | SQL-инъекция во входных параметрах не исполняется
INJ-SSRF-PARAMETERS | security | Параметры с URL и хостами не дают доступа к внутренней сети
INJ-STORED-XSS | security | Сохранённые данные с HTML/JS не создают XSS у потребителей API
INJ-TEMPLATE-SSTI | security | Инъекция в серверные шаблоны не исполняется
INJ-UNSAFE-DESERIALIZATION | security | Небезопасная десериализация пользовательских данных невозможна
INJ-USER-CODE-EXECUTION | security | Пользовательский код, исполняемый сервером, не получает доступа к ОС, файлам и сети
INJ-USER-DATA-CALLABLE | security | Данные пользователя не позволяют вызвать серверную функцию вне allowlist
INJ-XXE | security | Внешние сущности XML не обрабатываются
OBS-AUDIT-TRAIL | observability | Чувствительные действия фиксируются в журнале аудита
OBS-BUILD-VERSION-TRACEABLE | observability | Версия сборки доступна для трассировки на тестовых стендах и скрыта в production
OBS-CONFIG-ENDPOINT-ACCURATE | observability | Служебный эндпоинт конфигурации показывает фактические значения
OBS-HEALTH-ENDPOINTS | observability | Health-эндпоинты отражают состояние и не раскрывают детали
OBS-LOG-ENTRY-INTEGRITY | observability | Записи журнала при всплеске параллельных запросов не склеиваются
OBS-METRICS-LABEL-CARDINALITY | observability | Значения из запроса не создают неограниченно новых серий метрик
OBS-METRICS-VALUE-RANGE | observability | Gauge-метрики с известными границами остаются в них после сбоев и восстановления
OBS-NO-SECRETS-IN-LOGS | observability | Логи не содержат паролей, токенов и ПДн в открытом виде
OBS-REQUEST-LOG-ALL-ATTEMPTS | observability | Журнал запроса с повторами содержит каждую попытку, включая последнюю
OBS-SERVER-TIMING-ACCURATE | observability | Server-Timing отражает фактическую длительность этапов
OBS-TELEMETRY-FORMAT | observability | Экспортируемая телеметрия соответствует документированной структуре и соглашениям OpenTelemetry
OBS-TRACE-PROPAGATION | observability | Контекст трассировки принимается и передаётся дальше
PAGE-BEYOND-LAST | pagination | Запрос страницы за последней возвращает пустой результат без ошибки
PAGE-CONCURRENT-MODIFICATION | pagination | Изменения коллекции во время обхода не приводят к дублям и пропускам сверх контракта
PAGE-CURSOR-TAMPERING | pagination | Подделанный или чужой курсор пагинации не раскрывает данные
PAGE-NEXT-LINK-VALID | pagination | Ссылка next ведёт на ту же коллекцию, сохраняет фильтры и работает
PAGE-SEARCH-SPECIAL-CHARS | pagination | Поиск со спецсимволами и wildcard не ломается и не расширяет выборку
PAGE-SORT-FIELD-TYPE-MATRIX | pagination | Сортировка по каждому полю учитывает его тип, локаль и направление
PAGE-SORT-MULTI-KEY-PRIORITY | pagination | Сортировка по нескольким ключам соблюдает заданный клиентом порядок приоритета
PAGE-SORT-NULLS-TIES | pagination | Сортировка по полю с null и одинаковыми значениями детерминирована
PAGE-TOTAL-COUNT | pagination | Общее число элементов согласовано с суммой страниц
PERF-DEEP-PAGINATION | performance | Глубокая пагинация и большие выборки не деградируют неприемлемо
PERF-LATENCY-BASELINE | performance | Задержка ключевых операций в пределах SLO при обычной нагрузке
PERF-LOAD-THROUGHPUT | performance | Сервис выдерживает целевую нагрузку
PERF-METADATA-RELOAD-NO-BLOCK | performance | Перезагрузка кэша метаданных не блокирует обслуживание запросов надолго
PERF-NO-UNNEEDED-DEPENDENCY-CALLS | performance | Внешняя зависимость вызывается только когда её результат нужен
PERF-PAYLOAD-SIZE | performance | Размер ответов разумен и не растёт неограниченно
PERF-SOAK | performance | Длительная нагрузка не вызывает утечек и деградации
PERF-SPIKE | performance | Резкий всплеск нагрузки обрабатывается деградацией, а не отказом
PRIV-CONSENT-ENFORCEMENT | privacy | Обработка, требующая согласия, не выполняется без него
PRIV-DATA-MASKING | privacy | Чувствительные данные маскируются в ответах по политике
PRIV-ERASURE | privacy | Удаление персональных данных по запросу выполняется полностью
PRIV-IMPORT-URL-CREDENTIALS-NOT-STORED | privacy | Учётные данные из URL источника импорта не сохраняются после завершения импорта
PRIV-RESPONSE-FOREIGN-DATA | privacy | Ответ не содержит фрагментов данных других запросов и памяти процесса
PRIV-SELF-DATA-EXPORT | privacy | Экспорт собственных данных содержит только данные пользователя
REQ-CONTRACT-CONTRADICTS-SPEC | requirements | Поведение по контракту не противоречит ТЗ
REQ-CONTRACT-SELF-CONSISTENCY | requirements | Контракт не противоречит сам себе и своей прежней версии
REQ-CROSS-CLIENT-CONSISTENCY | requirements | Одно правило продукта одинаково в API разных клиентов
REQ-SPEC-NOT-IN-CONTRACT | requirements | Требование ТЗ не потеряно по пути в контракт и реализацию
REQ-UNSPECIFIED-BEHAVIOR-PROBE | requirements | Неописанное поведение выясняется тестом и сравнивается со стандартом и здравым смыслом
RES-ALLOCATED-VALUE-RELEASE | resources | Выделенное из пула значение не выдаётся повторно, пока прежний владелец не удалён окончательно
RES-ARCHIVE-RESTORE | resources | Архивирование и восстановление сохраняют данные и связи
RES-BULK-LIMITS | resources | Массовые операции соблюдают лимиты и сообщают о каждом элементе
RES-BULK-SINGLE-VALIDATION-PARITY | resources | Массовая операция валидирует так же, как одиночная
RES-CACHE-EXPLICIT-INVALIDATION | resources | Явный сброс кэша через API удаляет закэшированные ответы
RES-CACHE-KEY-COMPLETENESS | resources | Серверный кэш различает ответы по всем значимым параметрам и по типу ресурса
RES-CREATE-RESPONSE-MATCHES-READ | resources | Ответ на создание и изменение совпадает с последующим чтением
RES-CRUD-CYCLE | resources | Полный жизненный цикл ресурса: создание, чтение, изменение, удаление
RES-DB-OBJECT-NAMES | resources | API по схеме БД работает с объектами в любом регистре, со спецсимволами и зарезервированными именами
RES-DELETE-WITH-DEPENDENTS | resources | Удаление ресурса с зависимыми объектами выполняется по правилам каскада
RES-DRAFT-PUBLISH-FIDELITY | resources | Публикация черновика переносит все изменения и не ломает связи других объектов
RES-EXPORT-IMPORT-ROUNDTRIP | resources | Данные, выгруженные API, принимаются им же обратно без изменений
RES-IMMUTABLE-FIELDS | resources | Неизменяемые поля нельзя изменить после создания
RES-LARGE-RELATION-SET | resources | Тысячи связанных объектов не дают 5xx из-за лимитов СУБД на параметры запроса
RES-LIST-REFLECTS-CHANGES | resources | Списки и счётчики отражают создание, изменение и удаление
RES-READ-AFTER-WRITE | resources | Чтение после записи соответствует модели согласованности
RES-REFERENCE-DATA-COMPLETE | resources | Справочники через API полные, упорядочены по документации и управляются без релиза
RES-REFERENTIAL-INTEGRITY | resources | Ссылка на несуществующий или чужой связанный ресурс отклоняется
RES-RELATION-CONNECT-DISCONNECT-CONFLICT | resources | Подключение с позицией относительно отключаемой в том же запросе связи обрабатывается корректно
RES-RELATION-NULL-TARGET-ROWS | resources | Связь многие-ко-многим возвращает записи связующей таблицы с пустой ссылкой
RES-RELATION-ORDER-STABLE | resources | Изменение связанного ресурса не меняет ручной порядок связей у другой стороны
RES-RELATIONS-SHARED-JUNCTION-ISOLATION | resources | Связи через общую связующую таблицу возвращают каждая только свои данные
RES-SERVER-GENERATED-FIELDS | resources | Клиент не может задать серверные поля (id, createdAt, status, version)
RES-SOFT-DELETE-VISIBILITY | resources | Мягко удалённые ресурсы не видны в обычных операциях
RES-SYSTEM-OBJECT-PROTECTED | resources | Встроенные системные объекты защищены от удаления и изменения при любой конфигурации
RES-TIMESTAMPS | resources | Метки времени создания и изменения ведут себя корректно
RES-UNIQUENESS-NORMALIZATION | resources | Уникальность не обходится вариациями значения
RES-UPDATE-MISSING | resources | Изменение несуществующего ресурса не создаёт его неявно
RES-VALUE-ROUNDTRIP-EXACT | resources | Сохранённое значение возвращается так, как введено, кроме документированной нормализации
RESIL-BROKER-DOWN | resilience | Недоступность брокера сообщений не теряет события
RESIL-CIRCUIT-BREAKER | resilience | Circuit breaker размыкается и восстанавливается по политике
RESIL-DEPENDENCY-DOWN | resilience | Недоступность зависимости даёт контролируемую ошибку
RESIL-DEPENDENCY-TLS-RECOVERY | resilience | Проверка доступности внешнего бэкенда проверяет его сертификат и восстанавливается без перезапуска
RESIL-ENCRYPTION-KEY-ROTATION | resilience | Нерасшифровываемое после смены ключа значение не ломает чтение и сохранение остальных данных
RESIL-GRACEFUL-SHUTDOWN | resilience | Перезапуск экземпляра не обрывает выполняющиеся запросы
RESIL-PARTIAL-DEGRADATION | resilience | Отказ некритичной зависимости не ломает основной функционал
RESIL-TLS-CERT-RELOAD | resilience | Сервер подхватывает заменённый TLS-сертификат без перезапуска
RESOURCE-CREATE-READ | resources | Created resource can be read back
RESOURCE-READ-MISSING | resources | Reading a missing resource returns a documented error
REST-204-NO-BODY | contract | Ответ 204 без тела
REST-ACCEPT-NEGOTIATION | contract | Согласование Accept
REST-ALIASED-EMBED-FILTER-INDEPENDENCE | pagination | Вложения одного ресурса под разными алиасами фильтруются независимо
REST-API-VERSION-COMPATIBILITY | contract | Совместимость версий API
REST-ASYNC-202 | contract | Асинхронное принятие задачи 202
REST-AUTH-ERROR-NO-LEAK | security | Ошибки аутентификации без утечки
REST-BATCH-PARTIAL-FAILURE | contract | Частичный сбой batch
REST-CACHE-CONDITIONAL-GET | contract | ETag/Last-Modified conditional GET
REST-CONCURRENT-UPDATE | resilience | Конкурентное обновление
REST-CONTENT-TYPE-JSON | contract | Content-Type и JSON-формат
REST-CORRELATION-ID | errors | Correlation ID
REST-CORS-POLICY | security | Политика CORS
REST-CUSTOM-MEDIA-TYPE-EMPTY-RESULT | contract | Пустой результат в пользовательском медиатипе не вызывает внутреннюю ошибку
REST-DATE-TIME-TZ | validation | Дата, время и timezone
REST-DECIMAL-PRECISION | resources | Точность decimal
REST-DELETE-REPEAT | contract | Повторное удаление
REST-DUPLICATE-UNIQUE-KEY | resources | Дублирование уникального ключа
REST-EMPTY-VALUES | validation | Пустые объект, массив и строка
REST-ENUM-VALUES | validation | Допустимые и неизвестные enum
REST-ERROR-RETRY-AFTER | contract | Retry-After при временной ошибке
REST-ERROR-SCHEMA | contract | Стабильная схема ошибок
REST-ERROR-STATUS-BODY | contract | Согласованность статуса и тела ошибки
REST-ETAG-IF-MATCH | resilience | Условное обновление If-Match
REST-FILTER-EQUIVALENT-FORMS | pagination | Логически эквивалентные формы фильтра дают одинаковый ответ
REST-FILTER-INVALID | pagination | Невалидный фильтр
REST-FILTER-NAME-COLLISION | pagination | Фильтр по полю с именем вложенного ресурса применяется к полю
REST-FILTER-OPERATION-PARITY | pagination | Один фильтр даёт согласованный результат в списке, агрегации и вложенной выборке
REST-FILTER-OPERATOR-TYPE-MATRIX | pagination | Каждый оператор фильтра работает для каждого допустимого типа поля и возвращает ровно подходящие записи
REST-FILTER-RELATION-NO-DUPLICATES | pagination | Фильтр по полю связанной коллекции возвращает каждую запись один раз
REST-FILTER-SORT-COMPOSITION | pagination | Filtering and sorting compose correctly
REST-FILTER-SORT-PAGINATION | pagination | Комбинация filter/sort/pagination
REST-FILTER-UNSELECTED-FIELD | pagination | Фильтр по полю, не входящему в выбор полей, работает
REST-HEAD-GET-CONSISTENCY | http-semantics | HEAD response is consistent with GET
REST-IDEMPOTENCY-KEY | contract | Повтор с Idempotency-Key
REST-IDEMPOTENCY-RETRY | idempotency | Retry does not duplicate an idempotent operation's effect
REST-JSON-DUPLICATE-KEYS | validation | Дублирующиеся ключи JSON
REST-MASS-ASSIGNMENT | security | Mass assignment защищённых полей
REST-METHOD-NOT-ALLOWED | http-semantics | Unsupported HTTP method is rejected
REST-NEGOTIATED-FORMAT-CONFORMANCE | contract | Ответ в согласованном формате соответствует спецификации формата
REST-NULL-VS-OMITTED | validation | Null и отсутствующее поле
REST-NUMERIC-BOUNDARIES | validation | Числовые границы
REST-OBJECT-LEVEL-AUTHZ | security | Object-level authorization
REST-OPEN-REDIRECT | security | Валидация redirect URL
REST-OPTIONAL-EMPTY-VALUE | validation | Отсутствующий и пустой параметр
REST-PAGINATION-BOUNDARIES | pagination | Pagination handles boundary values correctly
REST-PAGINATION-LIMITS | pagination | Границы размера страницы
REST-PAGINATION-STABLE-ORDER | pagination | Стабильный порядок пагинации
REST-PATCH-PARTIAL-UPDATE | contract | Семантика PATCH
REST-PATH-PARAM-ENCODING | contract | Кодирование path-параметров
REST-POST-LOCATION | contract | Location при создании
REST-PUT-REPLACEMENT | contract | Семантика PUT
REST-QUERY-ENCODING | contract | Кодирование query-параметров
REST-RATE-LIMIT | security | Ограничение частоты запросов
REST-READONLY-WRITEONLY | contract | Поля readOnly/writeOnly
REST-REQUEST-SIZE-LIMIT | validation | Лимит размера тела
REST-REQUIRED-PARAM-MISSING | validation | Отсутствует обязательный параметр
REST-RETRY-TRANSIENT-ERROR | contract | Retry после временной ошибки
REST-SECURITY-HEADERS | security | Защитные HTTP-заголовки
REST-SENSITIVE-CACHE-CONTROL | security | Кэширование чувствительных ответов
REST-SENSITIVE-DATA | security | Отсутствие чувствительных данных в ответах
REST-SORT-INVALID-FIELD | pagination | Сортировка по неизвестному полю
REST-SSRF-URL-FETCH | security | Контроль server-side URL fetch
REST-STATE-TRANSITIONS | resources | Переходы состояния ресурса
REST-STATUS-CODE-CONTRACT | contract | Статус ответа соответствует контракту
REST-STRING-LENGTH-BOUNDARIES | validation | Границы длины строки
REST-TIMEOUT-BUDGET | contract | Таймаут и бюджет времени
REST-TYPE-MISMATCH | validation | Несовпадение типа поля
REST-UNICODE-NORMALIZATION | validation | Unicode и нормализация
REST-UNKNOWN-FIELDS | contract | Политика неизвестных полей
REST-UNSUPPORTED-CONTENT-TYPE | validation | Неподдерживаемый Content-Type запроса
REST-VALIDATION-ATOMICITY | contract | Атомарность ошибки валидации
SEC-ALT-REPRESENTATION-ACCESS | security | Закрытый ресурс недоступен ни через одно альтернативное представление
SEC-AUTHN-MALFORMED | security | Malformed credential is rejected
SEC-AUTHN-MISSING | security | Protected operation rejects missing credentials
SEC-AUTHN-SCHEMES-SUPPORTED | security | Все задокументированные схемы Authorization принимаются на своих эндпоинтах
SEC-AUTHZ-ASYNC-JOB | security | Authorization is rechecked for asynchronous job access
SEC-AUTHZ-CACHE-ISOLATION | security | Authorization context is respected by caches
SEC-AUTHZ-DYNAMIC-VARIABLES | security | Динамические переменные в правилах доступа действуют как эквивалентные статические значения
SEC-AUTHZ-ERROR-LEAK | security | Authorization failures do not disclose protected data
SEC-AUTHZ-EXPLICIT-OVER-INHERITED | security | Явное пониженное право на дочерний объект имеет приоритет над унаследованным
SEC-AUTHZ-FUNCTION | security | User without required permission cannot invoke operation
SEC-AUTHZ-LIST-CHECK-CONSISTENCY | security | Перечисление субъектов и объектов с доступом согласовано с точечной проверкой
SEC-AUTHZ-METHOD-MATRIX | security | Authorization is enforced for every method
SEC-AUTHZ-PATH-RULE-PRECEDENCE | security | Правила доступа по путям применяются по наиболее точному совпадению, независимо от порядка объявления
SEC-AUTHZ-RECREATED-IDENTITY | security | Права и согласия не переходят к пересозданному пользователю с тем же логином
SEC-AUTHZ-REVOKE-ROLE | security | Role revocation takes effect within policy window
SEC-AUTHZ-ROLE-POSITIVE-MATRIX | security | Разрешённая операция работает для каждой роли с правом, а не только для администратора
SEC-AUTHZ-RULE-READ-WRITE-PARITY | security | Условие прав по связанной записи действует в записи так же, как в чтении
SEC-BOLA-BULK | security | Bulk endpoint enforces ownership per item
SEC-CHECK-ORDER | security | Аутентификация и авторизация проверяются раньше разбора и валидации тела
SEC-CLONE-FIELD-PERMISSIONS | security | Копирование ресурса соблюдает полевые права чтения и создания
SEC-CONFUSED-DEPUTY | security | Действия во внешней системе от имени пользователя выполняются только с его правами
SEC-DISABLED-FEATURE-ENFORCED | security | Отключённая настройкой функция недоступна через все API и не попадает в токены
SEC-FAIL-CLOSED-INPUT | security | Неожиданный тип, пустое или отсутствующее поле проверки безопасности ведёт к отказу, а не к пропуску проверки
SEC-HORIZONTAL-ESCALATION | security | Peer user cannot access peer-only protected action
SEC-IDENTITY-PROOF-OF-POSSESSION | security | Заявленная клиентом идентичность без доказательства владения не даёт прав и льгот
SEC-INTERNAL-CONTROL-PARAMS | security | Заголовки и параметры подключения клиента не задают внутренние управляющие параметры операции
SEC-OPAQUE-ID-INTEGRITY | security | Непрозрачный идентификатор, выданный сервером, проверяется на подлинность
SEC-OWNERSHIP-DELETE | security | User cannot delete another owner’s resource
SEC-OWNERSHIP-EXPORT | security | Export/report endpoints enforce ownership and tenant boundaries
SEC-OWNERSHIP-READ | security | User cannot read another owner’s resource
SEC-OWNERSHIP-REFERENCE-INDIRECT | security | Indirect resource references preserve authorization
SEC-OWNERSHIP-UPDATE | security | User cannot modify another owner’s resource
SEC-POLICY-TEMPLATE-USER-DATA | security | Данные пользователя, подставляемые в шаблон политики доступа, не работают как wildcard
SEC-PRINCIPAL-TYPE-CONFUSION | security | Принципал одного типа не получает прав принципала другого типа с тем же числовым ID
SEC-READONLY-MODE-ENFORCED | security | Режим только для чтения запрещает изменения любым запросом, а не по первому ключевому слову
SEC-ROLE-ADMIN-SELF-TARGET | security | Административная операция над собственной учёткой обрабатывается по политике без 5xx
SEC-ROLE-BULK-ADMIN | security | Bulk admin actions require privilege for every target
SEC-ROLE-LOW-TO-HIGH | security | Low-privilege role cannot perform privileged action
SEC-ROLE-MASS-ASSIGN | security | Mass assignment cannot elevate privileges
SEC-ROLE-SELF-ASSIGN | security | User cannot grant self a higher role
SEC-SCOPE-EXTRA-UNTRUSTED | security | Client cannot add scopes by request parameter
SEC-SCOPE-MISSING | security | Token without required scope is denied
SEC-TENANT-CREATE | security | Client cannot assign resource to another tenant
SEC-TENANT-HEADER-SPOOF | security | Untrusted tenant header cannot override identity context
SEC-TENANT-READ | security | Tenant A cannot read tenant B data
SEC-TENANT-SEARCH | security | Tenant filter cannot be bypassed in list/search
SEC-TENANT-WRITE | security | Tenant A cannot mutate tenant B data
SEC-TOKEN-AUDIENCE | security | Token for another audience is rejected
SEC-TOKEN-EXPIRED | security | Expired access token is rejected
SEC-TOKEN-ISSUER | security | Token from untrusted issuer is rejected
SEC-TOKEN-REFRESH-REPLAY | security | Refresh-token replay is rejected or rotated
SEC-TOKEN-REVOKED | security | Revoked token cannot be reused
SEC-TOKEN-SIGNATURE | security | Token with invalid signature is rejected
SEC-VERTICAL-ESCALATION | security | Lower role cannot invoke higher-role route via alternate method
SECURITY-AUTH-REQUIRED | security | Protected operation rejects unauthenticated requests
SECURITY-AUTHZ-CROSS-USER | security | User cannot access another user's resource
UI-ACTIONS-WORK-ONCE | ui | Каждое действие выполняется ровно один раз и меняет ровно своё
UI-AUTH-FLOWS | ui | Интерфейсные потоки входа и восстановления нельзя обойти и перенаправить наружу
UI-CHANGE-HISTORY | ui | История изменений показывает каждое изменение с автором
UI-CLIENT-CODE-NO-SECRETS | ui | Клиентский код и страницы не раскрывают секретов и лишних данных
UI-CLIENT-REQUEST-HYGIENE | ui | Клиент не шлёт лишних, дублирующих и бесконечных запросов
UI-CONFIRM-DESTRUCTIVE | ui | Удаление и изменение подтверждаются, отмена ничего не меняет
UI-DISABLED-AND-READONLY | ui | Недоступные и доступные только для чтения элементы видны и не выполняют действий
UI-DOCUMENTS-OPEN | ui | Загруженные документы открываются и скачиваются в каждом поддерживаемом формате
UI-DROPDOWN-VALUES | ui | Выпадающие списки показывают полные, разрешённые и упорядоченные значения
UI-ERROR-DISPLAY | ui | Ошибки сервера и сбои показываются понятно, без падения клиента
UI-FORM-REQUIRED-AND-HINTS | ui | Обязательные поля помечены и проверяются, подсказки объясняют формат
UI-FORM-STATE | ui | Форма сохраняет и сбрасывает состояние ожидаемо
UI-INPUT-VALUES | ui | Поля ввода принимают, показывают и сохраняют значения по своему типу
UI-KEYBOARD-ACCESS | ui | Интерфейс полностью управляется с клавиатуры в логическом порядке
UI-LEGAL-PAGES | ui | Условия использования и FAQ доступны там, где нужны
UI-LIST-SORT-FILTER | ui | Сортировка и фильтры списков работают и сбрасываются ожидаемо
UI-NAVIGATION | ui | Навигация последовательна: путь на главную, заголовки, рабочие пункты меню
UI-NETWORK-RESILIENCE | ui | Клиент работает при потере сети и без доступа в интернет
UI-NO-BROKEN-RESOURCES | ui | Ссылки, картинки и ресурсы страниц загружаются
UI-PLATFORM-COMPATIBILITY | ui | Интерфейс одинаково работает в поддерживаемых браузерах, ОС и режимах
UI-PLATFORM-SECURITY | ui | Настольный и мобильный клиенты не открывают недоверенный код и экраны входа другим приложениям
UI-RELATED-RECORDS | ui | Связанные записи редактируются в карточке так же, как отдельно
UI-RESPONSIVE-LAYOUT | ui | Интерфейс работает на всех поддерживаемых размерах экрана
UI-RICH-EDITOR | ui | Редактор содержимого сохраняет форматирование и вставки без искажений
UI-SAFE-RENDERING | ui | Данные отображаются экранированными и не роняют интерфейс
UI-SECRET-FIELDS | ui | Поля паролей и секретов не раскрывают и не теряют значение
UI-SESSION-EXPIRY | ui | Истечение и потеря сессии обрабатываются в интерфейсе понятно
UI-TEXTS-CORRECT | ui | Тексты интерфейса без ошибок и по назначению экрана
UI-USABILITY | ui | Частые сценарии короткие, ожидание и задержки понятны пользователю
UI-VISUAL-CONSISTENCY | ui | Вид элементов единообразен и ничего не налезает
VAL-ALL-ERRORS-REPORTED | validation | Ошибки валидации нескольких полей возвращаются по контракту (все сразу или первая)
VAL-ARRAY-ITEMS-BOUNDARIES | validation | Границы массивов: minItems, maxItems, uniqueItems
VAL-BODY-ENCODING | validation | Тело в неверной кодировке или с BOM обрабатывается предсказуемо
VAL-BOOLEAN-COERCION | validation | Неявное приведение типов для boolean не происходит
VAL-CASE-SENSITIVITY | validation | Чувствительность к регистру идентификаторов, email и enum соответствует контракту
VAL-DEEP-NESTING | validation | Чрезмерно вложенный JSON отклоняется без деградации сервиса
VAL-DEFAULT-VALUES | validation | Опущенные необязательные поля получают задокументированные значения по умолчанию
VAL-DEFERRED-FAILURE | validation | Принятые при записи данные не вызывают 5xx в зависимых операциях
VAL-DEPENDENT-FIELDS | validation | Взаимозависимые поля валидируются совместно
VAL-DYNAMIC-VARIABLES-TYPE | validation | Правило валидации с динамической переменной сравнивает значения по типу поля
VAL-JSON-TOP-LEVEL-TYPE | validation | Неожиданный тип корня JSON отклоняется
VAL-LARGE-COLLECTION-PAYLOAD | validation | Массив с очень большим числом элементов отклоняется или обрабатывается в пределах лимитов
VAL-MALFORMED-JSON | validation | Синтаксически некорректный JSON отклоняется
VAL-MONEY-AMOUNT | validation | Денежные суммы: знак, точность и валюта валидируются
VAL-NESTED-OBJECT-ERRORS | validation | Ошибка во вложенном объекте указывает точный путь к полю
VAL-NUMBER-REPRESENTATION | validation | Альтернативные записи чисел обрабатываются по контракту
VAL-OPTIONAL-FIELDS-COMBINATIONS | validation | Любая комбинация и порядок необязательных полей обрабатываются без падения
VAL-PATH-ID-FORMAT | validation | Неверный формат идентификатора в пути не вызывает 5xx
VAL-QUERY-ARRAY-FORMAT | validation | Массивы в query передаются в задокументированном формате
VAL-QUERY-PARAM-POLLUTION | validation | Дублирующиеся query-параметры обрабатываются однозначно
VAL-RANGE-ORDER | validation | Начало диапазона не может быть позже конца
VAL-REGEX-PATTERN | validation | Поле с pattern принимает только совпадающие значения
VAL-REQUIRED-HEADERS | validation | Обязательные и форматные заголовки валидируются
VAL-SPECIAL-CHARACTERS | validation | Спецсимволы, emoji и управляющие символы сохраняются или отклоняются корректно
VAL-STRING-FORMAT | validation | Форматы строк (email, uuid, uri, date, phone) проверяются
VAL-TIGHTENED-RULES-STORED-DATA | validation | Сохранённые до ужесточения валидации значения обрабатываются одинаково на всех путях записи
VAL-UPLOADED-SCHEMA-FORMATS | validation | Загружаемая клиентом схема с документированными форматами принимается без ложных предупреждений
VAL-WHITESPACE-HANDLING | validation | Пробелы по краям и строки из пробелов обрабатываются согласованно
WS-HANDSHAKE-AUTH | websocket | Установление соединения требует аутентификации
WS-MALFORMED-MESSAGE | websocket | Некорректные сообщения не рвут соединение без ответа
WS-MESSAGE-LIMITS | websocket | Размер и частота сообщений ограничены
WS-MULTIPLE-ENDPOINTS-INDEPENDENT | websocket | Несколько WebSocket-эндпоинтов на разных путях работают независимо
WS-ORIGIN-CHECK | websocket | Проверка Origin защищает от cross-site WebSocket hijacking
WS-RECONNECT-RESUME | websocket | Переподключение восстанавливает подписки без потери и дублей сверх контракта
WS-SLOW-CONSUMER-NO-SILENT-LOSS | websocket | Медленный клиент подписки не теряет сообщения молча
WS-SUBSCRIPTION-AUTHZ | websocket | Подписки и сообщения авторизуются по каждому каналу
WS-SUBSCRIPTION-EVENTS-DELIVERED | websocket | Подписка получает события создания, изменения и удаления
WS-TOKEN-EXPIRY | websocket | Истечение или отзыв токена учитывается в открытом соединении
```
