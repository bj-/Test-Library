# Итог сверки пакета `inbox-ui` (30 записей)

_Claude, 2026-10-17. Правило — `mining/README.md`, шаги 6–7, п. 7; разделяются сборники разных рисков, на которые
указали две и более модели (как решение bj по DB). Статус `approved` ставит bj._

## Разделены (6 записей → 15)

| Было | Стало | Кто |
|---|---|---|
| UI-TEXTS-CORRECT | UI-TEXTS-CORRECT (№99, 180), UI-FIELD-LABELS-MATCH-FORM (№168) | Grok, ChatGPT |
| UI-VISUAL-CONSISTENCY | UI-VISUAL-CONSISTENCY (№100, 101, 103), UI-LAYOUT-OVERFLOW (№279, 284) | Grok, ChatGPT |
| UI-RELATED-RECORDS | UI-RELATED-RECORDS (№204, 210, 214), UI-LIST-COUNTERS-CONSISTENCY (№216) | Grok, ChatGPT |
| UI-LIST-SORT-FILTER | UI-LIST-SORT (№120), UI-LIST-FILTER-VALUES (№206, 207, 224), UI-LIST-FILTER-STATE (№265, 269), UI-CONDITIONAL-FORMATTING (№209) | Gemini, Grok, ChatGPT |
| UI-ERROR-DISPLAY | UI-ERROR-DISPLAY (№200, 220, 286, 301), UI-FAILURE-ROBUSTNESS (№123, 161, 169) | Grok, ChatGPT |
| UI-CLIENT-REQUEST-HYGIENE | UI-CLIENT-REQUEST-HYGIENE (№170, 185, 192, 225), UI-CLIENT-BASE-PATH-URLS (№227, 261), UI-STATE-CHANGE-METHODS (№187); №166 → UI-USABILITY | Gemini, Grok, ChatGPT |

UI-записей — 39; протоколы пересчитаны по пометкам идей (UI-RELATED-RECORDS — только `ui-web`).

## Правки

| Запись | Кто | Что сделано |
|---|---|---|
| UI-AUTH-FLOWS | ChatGPT (Claude согласен) | Ожидание: OIDC — только redirect_uri из списка клиента (может быть на другом origin), redirectTo — внутрь своего |
| UI-SECRET-FIELDS | ChatGPT | Менеджеры паролей допустимы; защита от снимков — где платформа поддерживает |
| UI-CLIENT-CODE-NO-SECRETS | ChatGPT | Source maps; кандидаты проверяются вручную, публичные ключи — не секреты |
| UI-PLATFORM-SECURITY | ChatGPT | Android — экспорт активностей, iOS — URL-схемы и deep links |
| UI-CHANGE-HISTORY | Gemini, Grok, Mistral | Ожидание — любые неявные изменения; время — если требуется |
| UI-ERROR-DISPLAY | ChatGPT | Поле и причина — когда сервер их сообщает |
| UI-STATE-CHANGE-METHODS | ChatGPT | PATCH тоже допустим |
| UI-USABILITY | ChatGPT, Mistral | deterministic: false; предусловие — список частых сценариев и критерии оценки |
| UI-TEXTS-CORRECT, UI-VISUAL-CONSISTENCY, UI-FIELD-LABELS-MATCH-FORM | ChatGPT | deterministic: false (экспертная оценка) |
| `when` у 26 записей | Gemini, ChatGPT | Конкретное условие вместо «есть клиент» |

## Не принято

| Предложение | Кто | Почему |
|---|---|---|
| Разделить все записи до уровня идеи | ChatGPT | Решение bj по структуре (DB, 2026-10-17) |
| reject UI-USABILITY и UI-LEGAL-PAGES | Gemini | Grok, Mistral — approve, ChatGPT — fix; условия применимости уточнены |
| kind usability | Grok | Такого значения нет в схеме; не меняю без решения |
| Убрать серверные проверки из UI-AUTH-FLOWS | Gemini | UI-записи проверяют путь через интерфейс; ссылки на серверные записи есть |
| Убрать шаг №191 из UI-ACTIONS-WORK-ONCE | Gemini | Шаг — вариант (дублирование записи); ChatGPT, наоборот, просит его сохранить |

## Польза от моделей (четыре)

ChatGPT 5.5 instant — самый подробный: одна критическая ошибка (OIDC), шесть замечаний по ожиданиям; разделения — по своему
постоянному порогу. Grok — конкретные разбиения (совпали с ChatGPT в пяти записях). Gemini — `when` и обобщение, две
reject не приняты. Mistral — почти всё approve, одно совпадение (№10). Для UI полезны ChatGPT и Grok; Gemini — как третий.
