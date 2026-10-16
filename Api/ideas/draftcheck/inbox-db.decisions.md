# Итог сверки пакета `inbox-db` (20 записей)

_Claude, 2026-10-17. Правило — `mining/README.md`, шаги 6–7, п. 7. Статус `approved` ставит bj._

## Правки (сделаны, статус draft)

| Запись | Кто | Что сделано |
|---|---|---|
| DB-IMPORT-CONSISTENCY | обе | Ожидание и шаг — по документированной политике импорта (откат или пропуск с отчётом) |
| DB-ROLES-AND-PRIVILEGES | обе | Шаг про SECURITY DEFINER и search_path перенесён в DB-STORED-ROUTINES; DDL — «по модели прав СУБД» |
| DB-DEFAULT-PRECEDENCE | обе | Шаги — через приложение: генератор не подставляет явный NULL; опущенная колонка и явный NULL различаются |
| DB-QUERY-INDEX-USAGE, DB-GENERATED-SQL-SHAPE, DB-TYPED-COMPARISONS, DB-TRIGGERS | ChatGPT | Оракулы смягчены: план и НФТ, а не «индекс используется»; результат и стоимость, а не EXISTS; приведения не меняют смысл; триггер — на каждое подходящее событие |
| DB-KEYS-AND-CONSTRAINTS, DB-SCHEMA-MATCHES-SPEC, DB-STORED-ROUTINES, DB-API-DATA-MATCH, DB-SENSITIVE-DATA-PROTECTED, DB-ACCESS-SCOPE-IN-QUERY, DB-CONNECTION-HANDLING | ChatGPT | Ограничения — где их требует модель данных; лимиты API и хранения согласованы; ошибка без параметров — если нет default; допустимые побочные изменения; ПДн — по классификации; граница доступа — условие, RLS или эквивалент; ограниченные повторы подключения; 2^31 — если стенд допускает |

## Решает bj

1. **Структура.** ChatGPT — разделить все 20 записей на независимые инварианты (по сути — запись на идею, ~90 записей);
   Gemini — утвердить как есть (16 из 20). Claude: часть записей — тематические сборники, а не один инвариант с
   вариантами; см. варианты в чате.
2. **DB-DYNAMIC-SQL-PARAMETERIZED.** Gemini — слить шаги в INJ-SQL и INJ-SCHEMA-IDENTIFIER-CODEGEN; ChatGPT — разделить и
   связать с ними. Claude — оставить DB-записью (проверка серого ящика по журналу запросов и коду отличается от
   чёрного ящика INJ-SQL), ссылки на INJ-SQL добавить.

## Польза от моделей

ChatGPT — все существенные замечания по оракулам (8 записей); Gemini — согласился по №4, №5, №16, своё — №12 (merge).

## Решения bj (2026-10-17)

1. **Структура** — разделены только 5 тематических сборников, остальные 15 записей — один инвариант с вариантами:
   - DB-MIGRATIONS-SAFE → DB-MIGRATION-STATE-TRACKED, DB-MIGRATION-CLEAN-INSTALL, DB-ALTER-PRESERVES-COLUMN,
     DB-MIGRATION-DATA-PRESERVED, DB-SCHEMA-CHANGE-VALIDATED;
   - DB-CONNECTION-HANDLING → DB-CONNECTION-POOL-LIFECYCLE, DB-CONNECTION-CONFIG-HANDLING, DB-DRIVER-LARGE-PARAMS;
   - DB-CATALOG-INTROSPECTION → DB-CATALOG-READ-PERFORMANCE, DB-CATALOG-READ-CORRECTNESS, DB-MIN-VERSION-COMPATIBILITY;
   - DB-METADATA-CACHE-FRESH → DB-METADATA-CACHE-FRESH (кэш и соединения пула), DB-IN-DB-CONFIG-APPLIED;
   - DB-ROLES-AND-PRIVILEGES → DB-SERVICE-ROLE-LEAST-PRIVILEGE, DB-ROLE-SWITCH-SETTINGS.
   Шаги перенесены без изменений, статусы идей в inbox обновлены. DB-записей — 30.
2. **DB-DYNAMIC-SQL-PARAMETERIZED** — оставлена DB-записью (серый ящик); в INJ-SQL — обратная ссылка.
