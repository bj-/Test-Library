# Перекрёстная проверка пруфов выгрузки багов

Партия `ghsa-maven`, 3 записи библиотеки. Сопоставление сделала модель Claude Opus 5.5 (`claude-opus-5-5`).
Этот файл целиком отдаётся другой LLM. Ответ модели вставить в чат внутренней сессии.

## Задание для модели

Ты проверяешь качество сопоставления реальных багов с записями библиотеки шаблонов API-тестов.
Для каждой записи ниже даны её текст (YAML) и список багов, которые другая модель к ней привязала, с первоисточником.
Для каждого бага ответь по первоисточнику, а не по пересказу:

1. **Привязка** — `ok` (запись проверяет именно тот механизм, что сломан в баге), `doubt` (близко, но спорно) или `wrong`
   (механизм другой; укажи, какая проверка подошла бы — словами или ID, если видишь подходящую среди записей ниже).
2. **Тип** — `covered` верно, только если существующие шаги записи уже ловят этот баг; иначе должен быть `extends`.
3. **Вариант** (для `extends`) — `ok` (новый, полезный и следует из бага), `dup` (уже есть в шагах записи),
   `invented` (деталей нет в баге — додумано), `vague` (слишком общий, нельзя выполнить как шаг теста).
4. **Почему** — одна строка, с цитатой из бага, если спорно.

Правила, по которым делалось сопоставление (из промпта):

```
3. **Сопоставление** (только для `api`) с `library_index.txt`:
   - `covered` — существующая запись проверяет ровно это; `check_id` — её ID; `variant: null`;
   - `extends` — запись есть, но баг показывает неучтённый вариант; `check_id`, `note` — почему это вариант
     записи, `variant` — новый шаг проверки в повелительной форме, как `steps[].action` записи («Отправить …»,
     «Повторить … для …»), без «Добавить вариант»; если вариант уже есть в записи или у другого бага партии —
     `variant: null` (только пруф);
   - `new` — подходящей записи нет; `check_id: null`, `note` — почему не подходит ближайшая.

   Правила выбора записи (по разметке точности пилота: ошибки были в сопоставлении, не в триаже):
   - **Механизм, а не тема.** Запись выбирается по тому, что именно ломается, а не по общей области бага.
     Пример: медленный разбор без регулярных выражений (квадратичный парсер, бесконечный цикл) —
     `HARD-EXPENSIVE-OPERATION-LIMITS`; `INJ-REDOS` — только для regex. Обработчик не вызывается при массиве из
     нескольких значений — это валидация массивов, а не защитные заголовки.
   - **Только то, что есть в баге.** Способ атаки, которого нет в тексте бага или фикса, не додумывать — в том
     числе по меткам CWE: CWE говорит о классе, а не о сценарии. Детали варианта (алиасы, составные выражения,
     другие каналы) — только из бага, фикса или его тестов. Механизм не описан — запись, которая проверяет
     описанное следствие; такой нет — `new`, в `note` — «механизм не описан».
   - **Направление проверки.** Законный запрос отклоняется (позитивный баг) — не привязывать к негативной записи
     «лишнее/запрещённое отклоняется», и наоборот. Подходящей записи с тем же направлением нет — `new`.
   - **Баг из интерфейса — про запрос.** Если сервер ломается на том, что прислал интерфейс (скрытое или
     пустое поле формы, лишний параметр), это `api`: баг воспроизводится запросом. Сопоставлять его нужно по
     этому запросу (лишние и пустые поля), а не по виду поля в интерфейсе. Только вёрстка или тема без ошибки
     сервера — это `ui`.
```

Формат ответа — одна таблица на все записи:

| # | Баг | Привязка | Тип верен? | Вариант | Почему |
|---|---|---|---|---|---|
| P1 | GHSA-... | ok/doubt/wrong | да/нет | ok/dup/invented/vague/— | ... |

В конце — 2–3 строки общего вывода: систематические ошибки, если есть.

## Запись HARD-EXPENSIVE-OPERATION-LIMITS

```yaml
id: HARD-EXPENSIVE-OPERATION-LIMITS
title: Дорогие операции ограничены по ресурсам
preconditions:
- Есть экспорт, отчёты, поиск, массовые операции.
steps:
- action: Запросить максимальный limit, широкий период, тяжёлые фильтры, параллельные экспорты.
- action: Усиление памяти при разборе URL (числовые ключи параметров)
  notes: 'Real-world bug: RWB-0077 (GHSA-ff3f-86qr-9cv3)'
- action: Сверхдлинный пароль на auth-эндпоинтах (в том числе для несуществующего пользователя)
  notes: 'Real-world bug: RWB-0077 (GHSA-477h-4r7f-fvrx)'
- action: Алгоритмическая сложность парсеров ввода — плоский вход с большим числом элементов при нулевой вложенности
  notes: 'Real-world bug: RWB-0077 (GHSA-rj75-hqrm-r3gf)'
- action: YAML с алиасами и merge-ключами (включая пустые отображения) — стоимость разбора ограничена
  notes: 'Real-world bug: RWB-0077 (GHSA-r3ph-w7gj-g6xm)'
expected:
- Действуют лимиты на размер, время и параллельность; сервис доступен другим клиентам.
applicability:
  when:
  - Есть дорогие операции.
  skip_when:
  - Нет.
```

### P1. GHSA-cxp5-3px4-pw24 — jackson-databind quadratic forward-reference completion 

Ссылка: https://github.com/advisories/GHSA-cxp5-3px4-pw24

- **Решение модели:** `extends`
- **Заметка:** Квадратичный алгоритм разбора без регулярных выражений
- **Вариант (новый шаг):** Отправить коллекцию из N ссылок на объекты по ID, определяемые позже в обратном порядке, и сравнить время ответа для N и 2N
- **Паттерн бага:** Коллекция с отложенными ссылками на объекты по ID разбирается за линейное время

Первоисточник:

````text
### Summary

When an `@JsonIdentityInfo` collection or map first creates N unresolved
object-ID references and later resolves the same IDs in reverse order,
jackson-databind scans the remaining pending-reference accumulator for each
resolution. A shallow JSON document whose size grows linearly can therefore
cause quadratic CPU work during deserialization.

### Details

The affected path is forward-reference completion in
`CollectionDeserializer.CollectionReferringAccumulator.resolveForwardReference()`
and the corresponding map implementation. The implementation performs a
linear search of the pending accumulator for every resolved object ID.

The behavior is runtime-confirmed in jackson-databind 2.5.0, 2.22.1, and
3.2.1. Current 2.22 and 3.2 source branches retained the same design when
rechecked. A 2.4.0 control fails closed before successful reverse-order
completion, so 2.5.0 is the conservative runtime-confirmed affected floor.
The patched versions are: 2.18.11, 2.21.7, 2.22.3, 3.1.7 and 3.2.3.

The vulnerable application must deserialize attacker-influenced JSON into an
identity-enabled collection or map. The issue does not require deep nesting or
syntactically unusual JSON.

Suggested correction: replace repeated linear lookup/removal with a keyed
pending-reference structure or another design that provides linear or
amortized-linear completion. A regression should preserve input order,
duplicate-ID behavior, and unresolved-ID errors while bounding reverse-order
resolution work.

### PoC

The proof constructs a shallow collection containing N unresolved
`@JsonIdentityInfo` references followed by definitions of those same IDs in
reverse order. Its ID class counts `equals()` calls, giving a deterministic
work measure rather than a timing-dependent result.

With N=2,000, affected versions perform exactly 2,003,000 ID comparisons. An
equally sized control in which every reference is already resolved performs
zero comparisons in the pending-reference lookup path. The …[обрезано]
````

### P2. GHSA-q4xh-88c3-wmh7 — jackson-databind: Duration XMLGregorianCalendar Unbounded Number Parse DoS

Ссылка: https://github.com/advisories/GHSA-q4xh-88c3-wmh7

- **Решение модели:** `extends`
- **Заметка:** Квадратичный разбор большого числа внутри строкового значения, обход лимита длины числовых токенов
- **Вариант (новый шаг):** Отправить в строковое поле длительности или даты компоненту из миллиона цифр и проверить, что отказ приходит быстро по лимиту длины
- **Паттерн бага:** Строковое поле длительности или даты с компонентой из миллионов цифр не вызывает долгого разбора

Первоисточник:

````text
### Summary
`jackson-databind` 3.2.1 deserializes a JSON **string** bound to a `javax.xml.datatype.Duration` or `javax.xml.datatype.XMLGregorianCalendar` field by passing the raw string verbatim to `DatatypeFactory.newDuration(value)` / `newXMLGregorianCalendar(value)`. Per the XML-Schema lexical grammar these factory methods accept numeric components of arbitrary length, which the JDK materializes into `java.math.BigInteger` / `BigDecimal` using the native `BigInteger(String)` constructor (an O(n²) parser). Because the digits reside inside a JSON **string** token, jackson-core's `StreamReadConstraints.maxNumberLength` guard (which bounds only JSON *number* tokens) never fires, so there is no length limit anywhere on this path. An unauthenticated attacker can submit a single small request (e.g. ~1–5 MB) that forces tens of seconds to minutes of single-thread CPU consumption, yielding a denial of service under the default `JsonMapper.builder().build()` mapper with no polymorphic typing or special configuration.

### Details
`StreamReadConstraints.maxNumberLength` (jackson-core, default 1000) bounds the **text length of JSON number tokens** only; it does not apply to digits inside a JSON string token (`maxStringLength` default is 100,000,000). jackson's own value binders compensate for this gap elsewhere — `NumberDeserializers` explicitly call `streamReadConstraints().validateIntegerLength(text.length())` / `validateFPLength(text.length())` before parsing a *stringified* number (`NumberDeserializers.java:1063`, `:1139`). The XML-datatype deserializer omits this identical pre-check.

`CoreXMLDeserializers` registers `Std` deserializers **by default** for any field typed `javax.xml.datatype.Duration` or `XMLGregorianCalendar` (`findBeanDeserializer`), with no opt-in required. `Std._deserialize` hands the attacker string straight to the datatype factory:

```java
protected Object _deserialize(String value, DeserializationContext ctxt) {
    switch (_kind) {
    case TYPE …[обрезано]
````

### P3. GHSA-v74w-7mr3-4qg3 — Netty: Denial of Service in XmlFrameDecoder via CPU Exhaustion

Ссылка: https://github.com/advisories/GHSA-v74w-7mr3-4qg3

- **Решение модели:** `extends`
- **Заметка:** Квадратичное повторное сканирование при подаче данных порциями, без регулярных выражений
- **Вариант (новый шаг):** Отправлять XML из повторяющихся «</» мелкими порциями без закрывающей «>» и проверить, что время обработки не растёт квадратично, а сервис отвечает другим клиентам
- **Паттерн бага:** XML, присылаемый мелкими порциями без закрывающей скобки, не вызывает повторного сканирования всего буфера

Первоисточник:

````text
### Summary
An attacker can cause Denial of Service by sending a specially crafted malicious XML payload (e.g., repeated `</` characters) to a Netty server utilizing XmlFrameDecoder, causing the server's EventLoop thread to exhaust CPU resources and become unresponsive.

### Details
`io.netty.handler.codec.xml.XmlFrameDecoder` suffers from a vulnerability resulting in CPU exhaustion. When `<` followed by `/` is encountered, the decoder scans the remaining buffer for a closing `>`.
Because the parser state is not saved between `decode()` invocations, an attacker can trickle-feed a payload of `</` characters. This forces the decoder to repeatedly rescan the entire accumulated buffer. A 1MB `maxFrameLength` is enough to completely hang a server's thread while it loops endlessly.

### Impact
Denial of Service via CPU Exhaustion. Any application utilizing Netty's XmlFrameDecoder is impacted. An unauthenticated remote attacker can exploit this flaw by sending a modest amount of malformed XML data to an exposed port.
````

### P4. GHSA-r7wm-3cxj-wff9 — jackson-core: Async parser maxNumberLength bypass via chunked digit accumulation (incomplete fix for GHSA-72hv-8253-57qq)

Ссылка: https://github.com/advisories/GHSA-r7wm-3cxj-wff9

- **Решение модели:** `extends`
- **Заметка:** Обход лимита через потоковую подачу: проверка срабатывает только при завершении числа
- **Вариант (новый шаг):** Передать тело с числом из миллионов цифр потоково мелкими порциями без завершающего символа и проверить отказ по лимиту длины числа до конца передачи
- **Паттерн бага:** Лимит длины числа применяется и при потоковой передаче тела мелкими порциями

Первоисточник:

````text
## Summary

The fix released in jackson-core `2.18.6` and `2.21.1` for [GHSA-72hv-8253-57qq](https://github.com/FasterXML/jackson-core/security/advisories/GHSA-72hv-8253-57qq) (Number Length Constraint Bypass in Async Parser, published 2026-02-28) is incomplete. The fix commit `b0c428e6` (#1555) wired `validateIntegerLength` into a new `_setIntLength` helper and called it at every place where the integer portion of a number is *decided* (terminator byte arrived, `.` / `e/E` seen, end-of-feed inside a fully-buffered value). It did not call it on the much more attacker-relevant path: "ran out of input while still inside `MINOR_NUMBER_INTEGER_DIGITS`, return `NOT_AVAILABLE` to caller".

As a result, an attacker who streams JSON to a non-blocking parser in many small chunks, without ever sending a terminator byte, can keep the parser inside `MINOR_NUMBER_INTEGER_DIGITS` indefinitely. `_textBuffer.expandCurrentSegment()` grows on every chunk, and `validateIntegerLength` is never invoked. The accumulator is only gated by `maxStringLength` (20 MiB default) — a **~20,000x amplification** of the documented `maxNumberLength` (1000 default).

This is the same vulnerability class, same advisory wording ("Memory Exhaustion: Unbounded allocation in TextBuffer from excessively long numbers"), same parser class — just the streaming path the original fix didn't cover. The fix to the *fraction* path is correct (see `_finishFloatFraction` at line 1834-1837 of `NonBlockingUtf8JsonParserBase.java` in 2.18.6, where `_setFractLength(fractLen)` IS called before the `NOT_AVAILABLE` return); the equivalent call is missing from every integer-digit path.

## Affected versions

Verified on the patched releases:
- `com.fasterxml.jackson.core:jackson-core` **2.18.6**
- `com.fasterxml.jackson.core:jackson-core` **2.21.1**

Structurally identical code in `tools.jackson.core` 3.0.x / 3.1.x — same `NonBlockingUtf8JsonParserBase` class, same `_setIntLength` rollout, same NOT_AVAILABLE returns without  …[обрезано]
````

### P5. GHSA-w4cm-gvhj-cgw6 — Jawn: Quadratic parsing effort in AsyncParser

Ссылка: https://github.com/advisories/GHSA-w4cm-gvhj-cgw6

- **Решение модели:** `extends`
- **Заметка:** Квадратичное пересканирование при подаче тела порциями, без регулярных выражений
- **Вариант (новый шаг):** Передать JSON с одним длинным токеном очень мелкими порциями и сравнить время обработки для длины N и 2N
- **Паттерн бага:** Длинный JSON-токен, присылаемый мелкими порциями, разбирается за линейное время

Первоисточник:

````text
`AsyncParser` can be forced to perform O(n^2) work on the length of the input.  When a single JSON token arrives across many small chunks, each `absorb` call rescans the incomplete token from the start.

### Impact

Denial of service via CPU exhaustion when parsing untrusted JSON.

Preconditions:
- Application uses `AsyncParser`
- Attacker can send large tokens with control over chunk sizes.

### Patches

Fixed in jawn-parser-1.7.0.

### Workarounds

If you can't upgrade immediately:
- Use the synchronous `Parser`.
- Buffer incoming bytes into larger chunks before calling `absorb`
````

### P6. GHSA-4899-mpch-38p3 — netty-incubator-codec-ohttp BinaryHttpParser: Unauthenticated CPU-exhaustion DoS via infinite loop in field-section decoding

Ссылка: https://github.com/advisories/GHSA-4899-mpch-38p3

- **Решение модели:** `extends`
- **Заметка:** Бесконечный цикл парсера — дорогая операция по правилу выбора записи
- **Вариант (новый шаг):** Отправить бинарное сообщение (Binary HTTP) с заявленной длиной секции полей, не совпадающей с границами строк полей, и проверить, что разбор завершается ошибкой за ограниченное время
- **Паттерн бага:** Разбор бинарного сообщения с некорректной длиной секции завершается за ограниченное время

Первоисточник:

````text
# BinaryHttpParser: Unauthenticated CPU-exhaustion DoS via infinite loop in field-section decoding

- **ID:** BHTTP-LOOP-001
- **Severity:** High
- **CVSS v3.1:** 7.5 — `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H`
- **CWE:** CWE-835 (Loop with Unreachable Exit Condition) — secondary CWE-400 (Uncontrolled Resource Consumption)
- **Affected component:** `codec-bhttp` → `io.netty.incubator.codec.bhttp.BinaryHttpParser#readFieldSection`, file `codec-bhttp/src/main/java/io/netty/incubator/codec/bhttp/BinaryHttpParser.java:619-626`
- **Affected version:** netty-incubator-codec-ohttp HEAD `d3f2b49` (release `0.0.22.Final` + 3 commits). The loop has existed since the parser was introduced and is present in the latest code; all published advisory fixes are already applied.
- **Reachable from:** `io.netty.incubator.codec.ohttp.OHttpRequestResponseContext$ContentDecoder#decodeChunk` (`codec-ohttp/.../OHttpRequestResponseContext.java:214`), i.e. the auto-wired OHTTP server **and** client codecs.
- **Confidence:** High (empirically reproduced hang + thread dump against the unmodified parser).

## Summary

`BinaryHttpParser` decodes Binary HTTP (RFC 9292) messages. An OHTTP gateway/client built on this library feeds the **decrypted** OHTTP body straight into `BinaryHttpParser.parse(...)`. The field-section decoding loop terminates only on the exact condition `fieldSectionLength != 0` and relies on a Java `assert` to guarantee forward progress. Because (a) the loop counter can be driven negative and (b) `readFieldLine(...)` legitimately consumes **zero** bytes and returns `null` on a truncated/over-long field line, the loop can spin forever. Assertions are disabled in any normal production JVM, so the two `assert` statements meant to catch this provide no protection.

A single ~17-byte Binary HTTP message — encapsulated by an unauthenticated attacker inside a normal OHTTP request, using the gateway's **public** key configuration — pins one Netty event-loop thread at 100% CPU per …[обрезано]
````

### P7. GHSA-8cfx-wx3q-mh5q — netty-incubator-codec-ohttp: Binary HTTP parser infinite loop on known-length field section boundary

Ссылка: https://github.com/advisories/GHSA-8cfx-wx3q-mh5q

- **Решение модели:** `extends`
- **Заметка:** Тот же вариант, что у GHSA-4899-mpch-38p3
- **Вариант (новый шаг):** —
- **Паттерн бага:** Разбор бинарного сообщения с секцией полей на границе завершается

Первоисточник:

````text
## Summary

`io.netty.incubator:netty-incubator-codec-bhttp` can enter a non-terminating parse loop when a known-length Binary HTTP field section ends exactly after a complete field line. A remote peer that can send Binary HTTP input to a Netty pipeline using `BinaryHttpParser` / `BinaryHttpDecoder` can use a tiny malformed request or response to keep the parsing thread busy indefinitely, causing denial of service.

## Details

In `codec-bhttp/src/main/java/io/netty/incubator/codec/bhttp/BinaryHttpParser.java`, `readFieldSection(...)` tracks the remaining field-section length in `fieldSectionLength`, then repeatedly calls `readFieldLine(...)` until the length reaches zero:

- `readFieldSection(...)` parses the known-length field section and enters `while (fieldSectionLength != 0)` at `BinaryHttpParser.java:619`.
- Inside the loop, it records `readableBytes`, calls `readFieldLine(...)`, computes `read = readableBytes - in.readableBytes()`, asserts `read > 0`, and subtracts `read` from `fieldSectionLength` at `BinaryHttpParser.java:620-625`.
- `readFieldLine(...)` returns `null` without consuming bytes when the field line ends exactly at the end of the readable slice because it uses `if (sumBytes >= in.readableBytes()) return null` after adding the value length (`BinaryHttpParser.java:678-681`).
- With JVM assertions disabled (the production default), `assert read > 0` is not active. The parser therefore subtracts zero forever and never returns.

The boundary condition is reachable with a valid known-length field section containing exactly one complete field line and no extra byte after that line. Example field section: length `4`, then name length `1`, name `a`, value length `1`, value `b`.

## Proof of concept

Safe local verification performed in this repository:

1. Compile the module and classpath:

```bash
./mvnw -q -pl codec-bhttp -am compile test-compile
./mvnw -q -pl codec-bhttp dependency:build-classpath -Dmdep.outputFile=/tmp/codec-bhttp-cp.txt
printf '%s'  …[обрезано]
````

### P8. GHSA-6jqx-86gh-f27w — Netty SPDY SETTINGS frame count materializes unbounded settings map

Ссылка: https://github.com/advisories/GHSA-6jqx-86gh-f27w

- **Решение модели:** `extends`
- **Заметка:** Затраты ресурсов на один кадр без лимита
- **Вариант (новый шаг):** Отправить один кадр настроек соединения с сотнями тысяч уникальных параметров и проверить, что сервер его ограничивает
- **Паттерн бага:** Число параметров в кадре настроек соединения ограничено

Первоисточник:

````text
### Summary
Netty's SPDY SETTINGS decoder accepts a peer-declared SETTINGS entry count up to the 24-bit frame-length limit and materializes every unique setting ID in `DefaultSpdySettingsFrame` without an implementation-level count cap. A remote SPDY/3.1 peer can send one syntactically valid roughly 2 MiB SETTINGS frame that creates 262144 map entries, amplifying network input into heap growth and ordered-map insertion work.

### Details
Inbound SPDY bytes enter `SpdyFrameCodec.decode()` and are passed directly to the frame decoder. The decoder reads the peer-controlled flags and 24-bit frame length from the common header, then accepts SETTINGS frames with only `length >= 4`. For SETTINGS payloads, it reads the peer-controlled `numSettings` field and validates only that the remaining payload is divisible into 8-byte entries and exactly matches that count. Each accepted entry then supplies an attacker-controlled 24-bit ID and value, and the normal delegate path forwards it into `spdySettingsFrame.setValue()`. The sink is `DefaultSpdySettingsFrame`: it backs settings with a `TreeMap`, checks only that IDs fit the SPDY 24-bit maximum, and inserts a new `Setting` for each previously unseen ID. There is no count budget between the wire-format count validation and the TreeMap insertion site.

### PoC
[poc.zip](https://github.com/user-attachments/files/28445737/poc.zip)

run with
```bash
bash ./poc/run.sh
```

expected output:
```text
NETTY_SPDY_SETTINGS_COUNT_MAP_TRIGGERED settings_count=262144 wire_bytes=2097164 approx_heap_delta=17692272 first_value=1 last_value=262144
```

The `NETTY_SPDY_SETTINGS_COUNT_MAP_TRIGGERED` line means the harness decoded the crafted SETTINGS frame and observed all 262144 peer-selected IDs in the resulting settings map. The `wire_bytes=2097164`, `first_value=1`, and `last_value=262144` fields distinguish this from a setup failure: they show the exact oversized frame was accepted and fully materialized.

### Impact
 remote unauthenticated netw …[обрезано]
````

### P9. GHSA-74xj-wh4w-vqxc — dd-trace-java: Improper parsing of W3C baggage headers may lead to DoS

Ссылка: https://github.com/advisories/GHSA-74xj-wh4w-vqxc

- **Решение модели:** `extends`
- **Заметка:** Неограниченная стоимость разбора заголовка
- **Вариант (новый шаг):** Отправить заголовок baggage (или другой заголовок-список) с десятками тысяч элементов и проверить, что разбор ограничен лимитом
- **Паттерн бага:** Заголовок распространения контекста с огромным числом элементов разбирается в пределах лимита

Первоисточник:

````text
### Impact
Datadog tracing libraries that implement W3C baggage propagation parse incoming baggage HTTP headers without enforcing item-count or byte-size limits on the extract path. The DD_TRACE_BAGGAGE_MAX_ITEMS (default 64) and DD_TRACE_BAGGAGE_MAX_BYTES (default 8192) limits were applied only to baggage injection, not extraction. A remote, unauthenticated attacker can send a request whose baggage header contains an arbitrarily large number of comma-separated key-value pairs (or a single very large value). The tracer allocates a hash-map entry for each pair on every request, causing unbounded CPU and memory consumption and enabling a remote Denial of Service against any HTTP service that has the baggage propagation style enabled. The baggage propagation style is enabled by default in most affected tracers, so any internet-facing service that has been instrumented with an affected tracer version is exposed unless the propagation style has been explicitly narrowed.

### Patches
This is resolved in version 1.62.0 and later of the `dd-trace-java` library.

### Workarounds
If users cannot upgrade immediately:
1. Disable `baggage` extraction by removing `baggage` from `DD_TRACE_PROPAGATION_STYLE` (or `DD_TRACE_PROPAGATION_STYLE_EXTRACT` if set independently).
2. Cap the maximum HTTP request header size at an upstream proxy or web server (for example, Apache `LimitRequestFieldSize`, Nginx `large_client_header_buffers`, Envoy `max_request_headers_kb`).

### Resources
Related upstream advisories:
[opentelemetry-go GHSA-mh2q-q3fh-2475](https://github.com/open-telemetry/opentelemetry-go/security/advisories/GHSA-mh2q-q3fh-2475)
[opentelemetry-dotnet GHSA-g94r-2vxg-569j](https://github.com/open-telemetry/opentelemetry-dotnet/security/advisories/GHSA-g94r-2vxg-569j)
````

### P10. GHSA-ghvc-7hp8-2g2v — Apache cxf-core: No restriction on attachment headers per message

Ссылка: https://github.com/advisories/GHSA-ghvc-7hp8-2g2v

- **Решение модели:** `extends`
- **Заметка:** Ограничение дорогих операций; вариант — число вложений в одном сообщении
- **Вариант (новый шаг):** Отправить multipart-сообщение с тысячами частей-вложений
- **Паттерн бага:** Число частей-вложений в сообщении ограничено

Первоисточник:

````text
There is no restriction on the amount of attachment headers that a message can contain when being deserialized by Apache CXF, which can lead to uncontrolled resource consumption or a denial of service attack. Users are recommended to upgrade to versions 4.2.2 or 4.1.7 or 3.6.12, which fix this issue by imposing a maximum default of 500 attachments per message.
````

### P11. GHSA-5m4m-73w9-8433 — Spring Data Commons: Denial of Service via excessive memory allocation in projection binding

Ссылка: https://github.com/advisories/GHSA-5m4m-73w9-8433

- **Решение модели:** `covered`
- **Заметка:** Механизм не описан; запись проверяет описанное следствие
- **Вариант (новый шаг):** —
- **Паттерн бага:** Привязка тела запроса к проекции не выделяет память сверх лимитов

Первоисточник:

````text
Spring Data Commons contains a vulnerability that can lead to a Denial of Service (DoS) condition if Spring Data Web Support is enabled in conjunction with a Controller method using @ProjectedPayload, when an attacker sends a specially crafted HTTP request that causes the application to allocate lots of memory.

Affected versions:
Spring Data Commons 4.0.0 through 4.0.5; 3.5.0 through 3.5.11; 3.4.0 through 3.4.14; 3.3.0 through 3.3.16; 3.2.0 through 3.2.15; 3.1.0 through 3.1.14; 3.0.0 through 3.0.15; 2.7.0 through 2.7.19.
````

### P12. GHSA-83f7-v6px-pp3h — Spring Framework Denial of Service via Multipart Requests in WebFlux

Ссылка: https://github.com/advisories/GHSA-83f7-v6px-pp3h

- **Решение модели:** `covered`
- **Заметка:** Механизм не описан; запись проверяет следствие
- **Вариант (новый шаг):** —
- **Паттерн бага:** Multipart-запросы не исчерпывают ресурсы сервера

Первоисточник:

````text
Spring WebFlux applications are vulnerable to Denial of Service (DoS) attacks when processing multipart requests.

Affected versions:
Spring Framework 7.0.0 through 7.0.7; 6.2.0 through 6.2.18; 6.1.0 through 6.1.27; 5.3.0 through 5.3.48.
````

### P13. GHSA-x23c-287f-qqv5 — Spring Framework Denial of Service via Versioned Resources in Spring MVC and WebFlux

Ссылка: https://github.com/advisories/GHSA-x23c-287f-qqv5

- **Решение модели:** `covered`
- **Заметка:** Механизм не описан; запись проверяет следствие
- **Вариант (новый шаг):** —
- **Паттерн бага:** Запросы статических ресурсов с версиями не исчерпывают ресурсы

Первоисточник:

````text
Spring MVC and WebFlux applications are vulnerable to Denial of Service (DoS) attacks when resolving static resources.

Affected versions:
Spring Framework 7.0.0 through 7.0.7; 6.2.0 through 6.2.18; 6.1.0 through 6.1.27; 5.3.0 through 5.3.48.
````

## Запись INJ-SSRF-PARAMETERS

```yaml
id: INJ-SSRF-PARAMETERS
title: Параметры с URL и хостами не дают доступа к внутренней сети
preconditions:
- API принимает URL для загрузки, превью, импорта или вебхуков.
steps:
- action: Передать http://169.254.169.254/, http://localhost, внутренние DNS-имена, IPv6, десятичную запись IP,
    редирект на внутренний адрес, file://, gopher://.
- action: URL спрятан в base64/JSON сегменте пути; слепой SSRF с побочным каналом через статус ответа
  notes: 'Real-world bug: RWB-0090 (GHSA-q8hw-4fvp-9rwv)'
- action: Адрес задаётся заголовком запроса, сервер прикладывает к исходящему вызову свои учётные данные
  notes: 'Real-world bug: RWB-0090 (GHSA-2h44-8472-frjj)'
- action: URL приходит не из параметра запроса, а из конфигурации в пользовательском источнике (манифест, репозиторий)
  notes: 'Real-world bug: RWB-0090 (GHSA-q38j-6vcm-2f5m)'
- action: Параметр базового URL сторонней интеграции - проверять не только доступ к внутренней сети, но и утечку
    серверного токена интеграции на подконтрольный внешний адрес
  notes: 'Real-world bug: RWB-0090 (GHSA-g734-fhp4-7mfp)'
- action: Хост/адрес проверяется по allowlist уже на эндпоинте регистрации (запись), а не только там, где его потом
    используют
  notes: 'Real-world bug: RWB-0090 (keycloak/keycloak#52167)'
- action: allowlist типов/схем источника должен применяться и при фоновой обработке, и для ссылок, найденных внутри
    принятого источника
  notes: 'Real-world bug: RWB-0090 (GHSA-pcmq-25r3-5w9v)'
- action: Код языка/локали, подставляемый в шаблон URL серверной загрузки
  notes: 'Real-world bug: RWB-0090 (GHSA-xvq9-wjp8-hwqf)'
- action: Фрагмент хоста (регион, поддомен) из параметра — символы '#', ':', '/', '@' и утечка пересылаемых учётных
    данных
  notes: 'Real-world bug: RWB-0090 (GHSA-6mwv-4mrm-5p3m)'
- action: Доменное имя, резолвящееся во внутренний/метаданных адрес (wildcard-DNS), — не только IP-литералы
  notes: 'Real-world bug: RWB-0090 (GHSA-798p-78g2-v556)'
- action: Вложенные ссылки в загружаемых документах ($ref) и записи IPv4-mapped IPv6, DNS-имена, редиректы
  notes: 'Real-world bug: RWB-0090 (GHSA-65h7-9wrw-629c)'
- action: Расхождение парсеров URL — Unicode-пробелы (U+00A0, U+FEFF) перед // превращают относительный путь в внешний
    хост
  notes: 'Real-world bug: RWB-0090 (GHSA-f6mr-pjwc-34m4)'
expected:
- Запросы к внутренним адресам и неразрешённым схемам блокируются, в том числе после редиректа и DNS rebinding.
applicability:
  when:
  - Есть серверная загрузка по URL.
  skip_when:
  - URL не принимаются.
```

### P14. GHSA-vvgp-rfg2-7rr6 — jackson-databind: Incomplete fix for CVE-2026-54514: eager DNS resolution (SSRF) still present in InetAddress deserialization

Ссылка: https://github.com/advisories/GHSA-vvgp-rfg2-7rr6

- **Решение модели:** `extends`
- **Заметка:** Исходящий DNS-запрос возникает уже на этапе разбора типа поля, а не при запросе по URL
- **Вариант (новый шаг):** Отправить в поле типа IP-адреса имя хоста под контролем тестировщика и проверить по журналу DNS, что сервер не разрешает его при разборе
- **Паттерн бага:** Поле с IP-адресом не вызывает DNS-разрешения имени хоста при разборе запроса

Первоисточник:

````text
### Summary
CVE-2026-54514 (GHSA-hgj6-7826-r7m5) fixed an eager-DNS-resolution / SSRF issue in jackson-databind's deserialization of `java.net.InetSocketAddress` by switching to `InetSocketAddress.createUnresolved(...)` (PR #5951, commit 1f5a1037, released in 2.18.8 / 2.21.4 / 3.1.4). That fix did not cover the sibling `java.net.InetAddress` branch in the very same `FromStringDeserializer.Std._deserialize()` switch statement, which still calls `InetAddress.getByName(value)` and therefore performs an eager forward DNS lookup on attacker-controlled input at deserialization time. The fix is incomplete: the same vulnerability class remains reachable through `InetAddress`.

### Details
File: src/main/java/com/fasterxml/jackson/databind/deser/std/FromStringDeserializer.java

Sibling cases in the same switch:
- Line 357-358 (UNFIXED):
    case STD_INET_ADDRESS:
        return InetAddress.getByName(value);     // eager forward DNS lookup
- Line 359-381 + helper at 494-496 (FIXED by PR #5951):
    protected InetSocketAddress _inetSocketAddress(String host, int port) {
        // 05-May-2026, tatu: [databind#5951] Prevent DNS lookup:
        return InetSocketAddress.createUnresolved(host, port);   // no DNS
    }

`InetAddress` is a registered standard string-like scalar type (FromStringDeserializer.types() line 73; findDeserializer() maps it to STD_INET_ADDRESS at line 119-120). Any value deserialized into an `InetAddress`-typed target — a plain POJO field, a polymorphic subtype, or a default-typing-permitted slot — reaches `InetAddress.getByName(attackerControlledString)`, which invokes the OS/JVM resolver and performs forward DNS resolution before any application validation.

The parent fix's own added unit test asserts `address.isUnresolved()` with the comment "should NOT resolve address", confirming that performing DNS resolution during deserialization is precisely the behavior being treated as the vulnerability. The InetAddress branch still violates that property.

Veri …[обрезано]
````

### P15. GHSA-hgj6-7826-r7m5 — jackson-databind: InetSocketAddress deserialization triggers eager DNS resolution (SSRF)

Ссылка: https://github.com/advisories/GHSA-hgj6-7826-r7m5

- **Решение модели:** `extends`
- **Заметка:** Тот же вариант, что у GHSA-vvgp-rfg2-7rr6 (DNS-запрос при разборе)
- **Вариант (новый шаг):** —
- **Паттерн бага:** Поле с адресом и портом не вызывает DNS-разрешения при разборе запроса

Первоисточник:

````text
## Summary
`JDKFromStringDeserializer` constructed `InetSocketAddress` with `new InetSocketAddress(host, port)`, which performs eager DNS name resolution for hostname inputs at deserialization time. An application that binds untrusted JSON into a type containing an `InetSocketAddress` field issues an attacker-chosen DNS query during `readValue`, before any application-level validation or connect logic. The fix uses `InetSocketAddress.createUnresolved(host, port)`, deferring DNS to an explicit connect.

## Impact
An attacker controlling JSON deserialized into an `InetSocketAddress`-bearing type can force outbound DNS lookups for attacker-chosen hostnames at deserialization time (SSRF / DNS-based out-of-band interaction / internal-resolver probing), purely from binding.

## Affected / Patched (verified via `git tag --contains` on `1f5a103`)
- 2.18 line: `>= 2.18.0, < 2.18.8` -> fixed in **2.18.8**
- 2.19-2.21 line: `>= 2.19.0, < 2.21.4` -> fixed in **2.21.4**
- 3.x line: `>= 3.0.0, < 3.1.4` -> fixed in **3.1.4**

## Severity / CWE
Maintainer: minor. Reporter: LOW. CWE-918 (SSRF).

## Upstream fix
FasterXML/jackson-databind#5951 ("Improve InetSocketAddress deserialization"). Released 2026-06-04 in 2.18.8 / 2.21.4 / 3.1.4.

## Credits
Omkhar Arasaratnam (@omkhar) - finder.
````

### P16. GHSA-vqc2-c9jh-3jjv — Apache Fesod is vulnerable to Server-Side Request Forgery through its UrlImageConverter component

Ссылка: https://github.com/advisories/GHSA-vqc2-c9jh-3jjv

- **Решение модели:** `covered`
- **Заметка:** Параметр с URL, запрашиваемый сервером
- **Вариант (новый шаг):** —
- **Паттерн бага:** URL изображения в данных для формируемого документа не даёт доступа во внутреннюю сеть

Первоисточник:

````text
Server-Side Request Forgery (SSRF) in the UrlImageConverter component of Apache Fesod (Incubating) fesod-sheet before 2.0.2-incubating allows attackers to cause outbound network requests to internal or otherwise restricted resources via a user-supplied image URL. Users are recommended to upgrade to version 2.0.2-incubating, which fixes this issue.
````

### P17. GHSA-r56g-q4p6-m3p6 — Kestra: SSRF via Pebble http() function allows unauthenticated access to internal services & cloud metadata

Ссылка: https://github.com/advisories/GHSA-r56g-q4p6-m3p6

- **Решение модели:** `extends`
- **Заметка:** URL приходит не параметром запроса, а из функции шаблона в сохранённом сценарии
- **Вариант (новый шаг):** Создать и запустить сценарий, в шаблоне которого функция HTTP-запроса обращается к адресу облачных метаданных, и проверить отказ
- **Паттерн бага:** Функция HTTP-запроса в пользовательском шаблоне не обращается к внутренним адресам

Первоисточник:

````text
### Summary
The Pebble template engine's `http()` function in Kestra OSS accepts user-controlled URLs without any validation, allowing Server-Side Request Forgery (SSRF) attacks. An unauthenticated attacker can import a malicious Flow YAML and execute it to access internal services, cloud metadata endpoints (AWS 169.254.169.254), or localhost services. The vulnerability affects all Kestra OSS deployments with default configuration.

### Details
The root cause is in `core/src/main/java/io/kestra/core/runners/pebble/functions/HttpFunction.java` (lines 77-106):

1. **No URL validation**: User input is passed directly to `URI.create()` with no checks for private IPs, internal hosts, or restricted schemes
2. **No IP filtering**: Missing checks for 10.0.0.0/8, 192.168.0.0/16, 169.254.169.254, 127.0.0.1
3. **No scheme restriction**: `file://`, `gopher://` schemes are not blocked
4. **No authentication required**: `TenantValidationFilter.java` only checks tenant == "main" — no authentication
5. **Unconditional registration**: `HttpFunction` is registered without any feature flags in `Extension.java:180`

### PoC
**Prerequisites:**
```bash
docker run -d --name kestra-ssrf -p 8080:8080 kestra/kestra:latest server local
sleep 30
```

**Step 1: Create malicious Flow YAML**
```yaml
cat > /tmp/ssrf_poc.yaml << 'YAML'
id: ssrf_metadata
namespace: company.team
tasks:
  - id: exfiltrate
    type: io.kestra.plugin.core.log.Log
    message: |
      {{ http(uri='http://169.254.169.254/latest/meta-data/', method='GET') }}
YAML
```

**Step 2: Import without authentication**
```bash
curl -X POST http://localhost:8080/api/v1/main/flows/import \
  -F "fileUpload=@/tmp/ssrf_poc.yaml"
```

**Step 3: Execute the flow**
```bash
curl -X POST http://localhost:8080/api/v1/main/executions/company.team/ssrf_metadata
```

**Step 4: Verify** — the flow execution output contains AWS EC2 metadata (ami-id, instance-type, IAM credentials if available)

### Impact
- **CVSS 3.1**: 8.6 (HIGH) — AV:N/AC:L/PR: …[обрезано]
````

### P18. GHSA-68r5-9hpg-7qw9 — OpenDJ unauthenticated SSRF, local file read and unbounded-read DoS in the DSMLv2 gateway

Ссылка: https://github.com/advisories/GHSA-68r5-9hpg-7qw9

- **Решение модели:** `covered`
- **Заметка:** Внутренние адреса и file:// уже в шагах записи
- **Вариант (новый шаг):** —
- **Паттерн бага:** Значения типа URI в запросе не загружаются сервером на внутренние адреса и file:

Первоисточник:

````text
The DSMLv2 SOAP gateway (opendj-dsml-servlet) in OpenIdentityPlatform OpenDJ through 5.1.1 dereferences attacker-supplied xsd:anyURI values server-side without a scheme allowlist, egress filtering, or a size cap, and is reachable without authentication by default. A remote unauthenticated attacker can submit a DSML add/modify request whose value is a URI to (1) perform server-side request forgery against internal services and the cloud metadata endpoint (SSRF), (2) read local files via file: URIs, and (3) exhaust memory through an unbounded response read (DoS). Fixed in 5.1.2: anyURI dereferencing is disabled by default; when enabled it is limited to an http/https allowlist, rejects loopback/link-local/private/reserved targets, refuses HTTP redirects, and caps the bytes read. The gateway also now requires container-managed authentication by default.
````

### P19. GHSA-8w86-m9h8-hvqg — ArcadeDB: IMPORT DATABASE allows SSRF and arbitrary local file read by authenticated users

Ссылка: https://github.com/advisories/GHSA-8w86-m9h8-hvqg

- **Решение модели:** `covered`
- **Заметка:** Внутренние адреса и file:// уже в шагах записи
- **Вариант (новый шаг):** —
- **Паттерн бага:** Команда импорта по URL требует административных прав и не обращается к внутренним адресам и file:

Первоисточник:

````text
### Impact

The SQL `IMPORT DATABASE` statement did not require administrative privileges and passed its source URL to the importer without validation. Any authenticated user with SQL command access (not only `root`/administrators) could therefore:

- **Server-Side Request Forgery (CWE-918):** cause the server to issue HTTP(S) requests to arbitrary destinations, including cloud metadata endpoints (e.g. `169.254.169.254`) and internal-only services, and ingest the responses as queryable records.
- **Arbitrary local file read (CWE-22):** read local files reachable by the server process (e.g. `/etc/passwd`, credential files) by importing `file://` paths, exposing their contents as records.

The server administration endpoint (`/api/v1/server`) was already restricted to the `root` user and was **not** affected; the exposure was through the database SQL command/query endpoints (`/api/v1/command`, `/api/v1/query`).

A related lower-severity hardening gap (CWE-776): the XML importer did not disable DTD processing, leaving entity-expansion (Billion Laughs) possible.

### Affected component

`integration/src/main/java/com/arcadedb/integration/importer/SourceDiscovery.java` (no host allow-list for http(s); no path validation for `file://`), reached from `engine/.../query/sql/parser/ImportDatabaseStatement.java`.

### Patches

- `IMPORT DATABASE` now requires the administrative `updateSecurity` permission (no-op in embedded mode).
- Import sources are validated in `SourceDiscovery`: HTTP(S) hosts resolving to loopback / link-local / private (site-local) / wildcard / multicast addresses are blocked by default (`arcadedb.server.security.importBlockLocalNetworks`, default `true`), and an optional local-path allow-list (`arcadedb.server.security.importAllowedLocalPaths`) restricts `file://` reads.
- The XML importer now disables DTD processing and external entities.

Fixed in commit referenced by pull request [#4422](https://github.com/ArcadeData/arcadedb/pull/4422).

### Workarou …[обрезано]
````

### P20. GHSA-x939-7fq5-v9v6 — Payara Server Full has a Cross-Site Request Forgery vulnerability

Ссылка: https://github.com/advisories/GHSA-x939-7fq5-v9v6

- **Решение модели:** `covered`
- **Заметка:** Шаг записи «сервер прикладывает к исходящему вызову свои учётные данные»
- **Вариант (новый шаг):** —
- **Паттерн бага:** Исходящий запрос по адресу из запроса не несёт токен администратора на чужой хост

Первоисточник:

````text
A critical vulnerability in Admin GUI in Payara Server Full 4.x, 5.x, 6.x, 7.x, 7.2026.x, 6.2025.x, 6.2024.x on All platforms that allows the attacker to leak the admin gfresttoken to an attacker-controlled host that can result in a full unauthenticated takeover of Payara admin domain.

A Server-Side Request Forgery (SSRF) vulnerability in the DownloadServlet of the Admin GUI in Payara Server allows a remote attacker to exfiltrate the administrator's REST session token (gfresttoken) to an attacker-controlled host via a crafted request URL. Combined with the absence of CSRF protection on DownloadServlet, an unauthenticated attacker can trick a logged-in administrator into triggering the token leak, then replay the stolen token to gain full administrative access to the Payara domain, leading to arbitrary code execution via WAR deployment. The vulnerability exists in the DownloadServlet and associated ContentSource implementations (LogViewerContentSource, LogFilesContentSource, LBConfigContentSource, ClientStubsContentSource) within the admingui:console-common module.
````

### P21. GHSA-whpp-xv3h-rwxf — Spring Web Services: SSRF via unvalidated WS-Addressing reply destinations

Ссылка: https://github.com/advisories/GHSA-whpp-xv3h-rwxf

- **Решение модели:** `extends`
- **Заметка:** SSRF через параметр; вариант — адреса ответа в заголовках сообщения
- **Вариант (новый шаг):** Указать внутренний адрес в заголовках адреса ответа (WS-Addressing ReplyTo, FaultTo)
- **Паттерн бага:** Адреса ответа из заголовков запроса не ведут к запросам на недопустимые адреса

Первоисточник:

````text
When WS-Addressing is used with non-anonymous ReplyTo or FaultTo addresses, Spring WS may initiate outbound connections through configured WebServiceMessageSender instances to destinations taken directly from request headers without verifying that those destinations are safe to connect to.

Affected versions:
Spring Web Services 5.0.0 through 5.0.1; 4.1.0 through 4.1.3; 4.0.0 through 4.0.18; 3.1.0 through 3.1.8.
````

### P22. GHSA-7m2p-62gw-p8qq — Spring Framework Server-Side Request Forgery via UriComponentsBuilder

Ссылка: https://github.com/advisories/GHSA-7m2p-62gw-p8qq

- **Решение модели:** `extends`
- **Заметка:** SSRF; вариант — расхождение разбора хоста
- **Вариант (новый шаг):** Передать URL, хост которого неоднозначен для разных парсеров
- **Паттерн бага:** Проверка хоста URL не обходится расхождением парсеров

Первоисточник:

````text
Due to incorrect host parsing, applications that rely on UriComponentsBuilder to parse and validate an externally provided URL string may be exposed to a server-side request forgery (SSRF) attack.

Affected versions:
Spring Framework 7.0.0 through 7.0.7; 6.2.0 through 6.2.18.
````

## Запись REST-MASS-ASSIGNMENT

```yaml
id: REST-MASS-ASSIGNMENT
title: Mass assignment защищённых полей
preconditions:
- Подготовить тестовые данные и credentials согласно сценарию.
steps:
- action: Выполнить запрос по операции, удовлетворяющей условиям применимости.
- action: Добавить служебные флаги защиты, снятие которых отключает другие проверки
  notes: 'Real-world bug: RWB-0121 (keycloak/keycloak#52488)'
- action: 'Добавить варианты: точечные пути и операторы хранилища, обход полевых прав на конкретном бэкенде хранения'
  notes: 'Real-world bug: RWB-0121 (GHSA-4ww4-68q3-h7g5)'
- action: Учётные поля (password) в общем эндпоинте изменения пользователя при полевом запрете
  notes: 'Real-world bug: RWB-0121 (GHSA-fx49-4h83-wjv9)'
- action: Глобальные флаги безопасности в объекте настроек и проверка последствий для доступа
  notes: 'Real-world bug: RWB-0121 (GHSA-vmjq-hvgq-2wv4)'
expected:
- role/owner/status/balance нельзя менять через неразрешённые поля payload
applicability:
  when:
  - есть защищённые поля модели
  skip_when:
  - operation is not supported by the API
  - expected behavior is not specified and requires review
```

### P23. GHSA-5gvw-p9qm-jgwh — jackson-databind: @JsonView bypassed for @JsonUnwrapped container properties on deserialization

Ссылка: https://github.com/advisories/GHSA-5gvw-p9qm-jgwh

- **Решение модели:** `extends`
- **Заметка:** Защищённые поля приходят не отдельным ключом, а как развёрнутые поля вложенного объекта
- **Вариант (новый шаг):** Отправить на публичный эндпоинт привилегированные поля, которые модель разворачивает из вложенного объекта на верхний уровень JSON, и проверить, что они не записаны
- **Паттерн бага:** Привилегированные поля развёрнутого (flattened) вложенного объекта не записываются через публичный эндпоинт

Первоисточник:

````text
## Summary
`UnwrappedPropertyHandler.processUnwrapped()` replays the buffered JSON for a `@JsonUnwrapped` property by iterating its properties and calling `prop.deserializeAndSet()` with **no `prop.visibleInView(ctxt.getActiveView())` guard** — the exact guard `processUnwrappedCreatorProperties()` received in the #5971 / GHSA-rcqc-6cw3-h962 fix, and the guard `BeanDeserializer.deserializeWithUnwrapped` applies to directly-matched properties. As a result, a property annotated with both `@JsonView(PrivilegedView.class)` and `@JsonUnwrapped` is written from attacker JSON even when deserializing under a more-restrictive active view.

**Correction to the original framing (runtime-verified):** the gap is NOT a per-field inner `@JsonView` (the unwrapped sub-object's own `BeanDeserializer` gates inner fields correctly). The unchecked gate is the **view of the unwrapped CONTAINER property**.

## Intent proof (runtime, 2.x HEAD 21dd70dd and 3.x HEAD 7a5939d6)
An `@JsonView(AdminView)` property that is NOT `@JsonUnwrapped` → `null` under `PublicView` (correctly gated). The identical property WITH `@JsonUnwrapped` → fully populated (bypass). The fix the creator path already received, not applied to the regular-property method.

## Impact — write-side mass-assignment / privilege escalation
`@JsonView` is commonly used as a write-side authorization guard: a public endpoint binds the body under `readerWithView(PublicView.class)` and groups privileged state in a nested object whose container property is `@JsonView(AdminView)`. When that property is `@JsonUnwrapped`, an untrusted caller mass-assigns it. PoC: a self-service registration where `AccountFlags{role,approved,creditBalance}` is `@JsonView(AdminView) @JsonUnwrapped`; attacker JSON `{role:ADMIN,approved:true,creditBalance:1000000}` under `PublicView` binds all three → approved admin with arbitrary balance. The failing gate is a WRITE gate, hence integrity-high (`C:N/I:H/A:N`); no worse than the C:L/I:L parent and arguably hi …[обрезано]
````

### P24. GHSA-3pjw-73gf-8qr5 — jackson-databind: @JsonIgnore on a Record property is bypassed with a PropertyNamingStrategy

Ссылка: https://github.com/advisories/GHSA-3pjw-73gf-8qr5

- **Решение модели:** `extends`
- **Заметка:** Обход исключения поля через имя после стратегии именования
- **Вариант (новый шаг):** Отправить защищённое поле под именем в стиле именования API (snake_case) и под исходным именем и проверить, что оно не записано
- **Паттерн бага:** Игнорируемое при записи поле не принимается под переименованным ключом

Первоисточник:

````text
## Summary
For Java Records, `POJOPropertiesCollector._removeUnwantedIgnorals()` records a `@JsonIgnore`-annotated component under its original implicit name before `_renameUsing()` applies the `PropertyNamingStrategy`. After the rename, `_ignoredPropertyNames` still holds only the pre-rename name, so `_ignorableProps` is built from the stale key. The renamed JSON key passes `IgnorePropertiesUtil.shouldIgnore()` and is assigned to the Record's constructor parameter, defeating the `@JsonIgnore`.

## Impact
A Record using a naming strategy that relies on `@JsonIgnore` to keep an internal/privileged component out of deserialization can have that component set from the wire via its renamed key (e.g. a role/flag controlled by an untrusted client).

## Affected / Patched (verified via `git tag --contains`)
- 2.15-2.18 line: `>= 2.15.0, < 2.18.8` -> fixed in **2.18.8** (backport `c7c6783`)
- 2.19-2.21 line: `>= 2.19.0, < 2.21.4` -> fixed in **2.21.4**
- 3.x line: `>= 3.0.0, < 3.1.4` -> fixed in **3.1.4** (#5974, `baa2cdf`)

## Severity / CWE
Maintainer: minor. Reporter: Moderate. CWE-915; related CWE-345.

## Credits
Omkhar Arasaratnam (@omkhar) - finder.
````

### P25. GHSA-5hh8-q8hv-fr38 — jackson-databind has @JsonView bypass for setterless creator properties

Ссылка: https://github.com/advisories/GHSA-5hh8-q8hv-fr38

- **Решение модели:** `extends`
- **Заметка:** Защищённое поле — коллекция без сеттера, заполняемая слиянием
- **Вариант (новый шаг):** Отправить на публичный эндпоинт привилегированное поле-коллекцию (список ролей, словарь прав) и проверить, что она не заполнена
- **Паттерн бага:** Привилегированное поле-коллекция не заполняется через публичный эндпоинт

Первоисточник:

````text
## Summary
In `BeanDeserializer._deserializeUsingPropertyBased`, the active-view (`@JsonView`) filter was applied only to creator properties; the regular property-buffering branch performed no `prop.visibleInView(activeView)` check. A change making `SetterlessProperty.isMerging()` return `true` routed setterless Collection/Map properties through this unguarded path, so a setterless collection annotated with a restricted `@JsonView` is populated from attacker JSON even when the active view excludes it.

## Impact
View-restricted (e.g. admin-only) setterless collection/map properties can be written from untrusted JSON despite `@JsonView` gating — an access-control / mass-assignment bypass. No RCE or DoS.

## Affected / Patched (verified via `git tag --contains`)
- 2.21 line: `>= 2.21.0, < 2.21.4` -> fixed in **2.21.4** (backport `94c5d21`, #5970)
- 3.x line: `>= 3.0.0, < 3.1.4` -> fixed in **3.1.4** (#5969, `5bf23ed`)

## Severity / CWE
Maintainer: minor. Reporter: HIGH. CWE-863 (Incorrect Authorization); related CWE-1220.

## Credits
Omkhar Arasaratnam (@omkhar) - finder.
````

### P26. GHSA-rcqc-6cw3-h962 — jackson-databind has a @JsonView bypass for unwrapped creator parameters

Ссылка: https://github.com/advisories/GHSA-rcqc-6cw3-h962

- **Решение модели:** `extends`
- **Заметка:** Тот же вариант, что у GHSA-5gvw-p9qm-jgwh
- **Вариант (новый шаг):** —
- **Паттерн бага:** Привилегированные поля развёрнутого вложенного объекта не записываются через публичный эндпоинт

Первоисточник:

````text
## Summary
`UnwrappedPropertyHandler.processUnwrappedCreatorProperties()` replays buffered JSON into creator parameters but never consults `prop.visibleInView(activeView)`. The normal property-based creator path gates creator properties on the active view, but this unwrapped-creator replay path bypasses that check, so a constructor parameter annotated with both `@JsonView(AdminView.class)` and `@JsonUnwrapped` is populated from attacker JSON even when a more restrictive view is active.

## Impact
View-restricted unwrapped creator parameters can be set from untrusted input where `@JsonView` is used as a write-side authorization boundary.

## Affected / Patched (verified via `git tag --contains`)
- 2.21 line: `>= 2.21.0, < 2.21.4` -> fixed in **2.21.4** (backport `721fa07`, #5973)
- 3.x line: `>= 3.0.0, < 3.1.4` -> fixed in **3.1.4** (#5971, `d633bc0`)

## Severity / CWE
Maintainer: minor. Reporter: HIGH. CWE-863 (Incorrect Authorization); related CWE-284.

## Credits
Omkhar Arasaratnam (@omkhar) - finder.
````

### P27. GHSA-mhm7-754m-9p8w — jackson-databind: `@JsonView` bypass for creator properties with `@JsonTypeInfo(include=As.EXTERNAL_PROPERTY)`

Ссылка: https://github.com/advisories/GHSA-mhm7-754m-9p8w

- **Решение модели:** `extends`
- **Заметка:** Обход ограничения представления, как у GHSA-5hh8 и GHSA-rcqc в b-01, но для полиморфного поля с внешним типом
- **Вариант (новый шаг):** Отправить на публичный эндпоинт привилегированное полиморфное поле вместе с его внешним свойством-дискриминатором типа и проверить, что поле не записано
- **Паттерн бага:** Скрытое представлением полиморфное поле не записывается через публичный эндпоинт

Первоисточник:

````text
## Summary

In `BeanDeserializer.deserializeUsingPropertyBasedWithExternalTypeId`, the active-view (`@JsonView`) filter was applied only to the regular bean-property branch; the creator-property branch performed no `creatorProp.visibleInView(activeView)` check. A constructor parameter annotated with both `@JsonView(RestrictedView.class)` and `@JsonTypeInfo(use=Id.NAME,
  include=As.EXTERNAL_PROPERTY)` is populated from attacker JSON even when a more restrictive view is active.

  This is a patch gap. GHSA-5hh8 (CVE-2026-54517) and GHSA-rcqc (CVE-2026-54518) descriptions cover only the main property-based path and the unwrapped-creator path respectively; the external-type-id creator path was fixed on the 3.x line via #6004 ("Extend #5969/#5971 fixes to ... external-type-id case in regular BeanDeserializer", commit 7dc7a17, 2026-05-22) but
  **the fix was never backported to 2.21 or 2.18**. Users on 2.21.4 and 2.18.8 who upgraded per the published advisories remain vulnerable to the same `@JsonView` bypass technique via a different code path.

## Vulnerable Code Path

File: `com/fasterxml/jackson/databind/deser/BeanDeserializer.java`
Method: `deserializeUsingPropertyBasedWithExternalTypeId`

On 2.21.4 (and 2.18.8), the creator-property branch (around line 1125-1158) checks `creatorProp.isInjectionOnly()` and hands off to `ext.handlePropertyValue(...)` / `buffer.assignParameter(...)` without ever consulting `visibleInView(activeView)`:

 ```java
  if (creatorProp != null) {
      // [databind#1381]: if useInput=FALSE, skip deserialization from input
      if (creatorProp.isInjectionOnly()) { ... }
      // NO visibleInView(activeView) CHECK HERE
      if (!ext.handlePropertyValue(p, ctxt, propName, null)) {
          if (buffer.assignParameter(creatorProp, ...)) { ... }
      }
      continue;
  }
```

On 3.1.4, the same branch contains the additional guard (commit 7dc7a17):

 ```java
   if (creatorProp != null) {
      // [databind#5971]: must honor active view here t …[обрезано]
````

### P28. GHSA-5jmj-h7xm-6q6v — jackson-databind has case-insensitive deserialization bypasses per-property @JsonIgnoreProperties

Ссылка: https://github.com/advisories/GHSA-5jmj-h7xm-6q6v

- **Решение модели:** `extends`
- **Заметка:** Тот же класс, новый вариант — обход через регистр имени поля
- **Вариант (новый шаг):** Отправить защищённое поле с именем в другом регистре при регистронезависимом сопоставлении полей
- **Паттерн бага:** Игнорируемое при записи поле не устанавливается при регистронезависимом сопоставлении имён

Первоисточник:

````text
## Summary
In `BeanDeserializerBase.createContextual()`, per-property `@JsonIgnoreProperties` exclusions are applied by `_handleByNameInclusion()`, producing a `contextual` deserializer whose `BeanPropertyMap` has the ignored properties removed. The subsequent per-property case-insensitivity block (triggered by `@JsonFormat(ACCEPT_CASE_INSENSITIVE_PROPERTIES)`) rebuilds from `this._beanProperties` (the original, unfiltered map) instead of `contextual._beanProperties`, then overwrites the filtered map — restoring every property `_handleByNameInclusion` had just removed. The ignored property becomes writable again.

## Impact
An application that both enables case-insensitive matching and relies on per-property `@JsonIgnoreProperties` to keep a field unwritable can have that field set from untrusted JSON (mass-assignment-style write).

## Affected / Patched
Will be fixed in 2.18.9, 2.21.5, 2.22.1 and 3.1.4.

## Severity / CWE
Maintainer: minor. Reporter: Moderate. CWE-915.

## Upstream fix
FasterXML/jackson-databind#5962 (PR #5964, `0e1b0b2`), milestone 3.1.4. Released 2026-06-04.
````

### P29. GHSA-cv39-x4c6-hhp2 — Spring Data REST has Improper Access Control in its JSON Patch Implementation

Ссылка: https://github.com/advisories/GHSA-cv39-x4c6-hhp2

- **Решение модели:** `extends`
- **Заметка:** Запись защищённых полей; вариант — промежуточный сегмент JSON Pointer
- **Вариант (новый шаг):** Отправить JSON Patch с многосегментным путём через поле, закрытое для записи
- **Паттерн бага:** JSON Patch не меняет защищённые поля через многосегментный путь

Первоисточник:

````text
Spring Data REST's JSON Patch (application/json-patch+json) implementation does not apply the write-access filter to intermediate path segments when resolving a multi-segment JSON Pointer.

Affected versions:
Spring Data REST 3.7.0 through 3.7.19; 4.3.0 through 4.3.16; 4.4.0 through 4.4.14; 4.5.0 through 4.5.11; 5.0.0 through 5.0.5.
````

### P30. GHSA-7fxc-486f-32q9 — Spring HATEOAS Collection+JSON/UBER deserializers do not honor Jackson configuration

Ссылка: https://github.com/advisories/GHSA-7fxc-486f-32q9

- **Решение модели:** `extends`
- **Заметка:** Mass assignment; вариант — альтернативные медиатипы
- **Вариант (новый шаг):** Отправить защищённое поле в теле каждого поддерживаемого медиатипа (Collection+JSON, UBER)
- **Паттерн бага:** Защищённые поля не устанавливаются через альтернативные медиатипы

Первоисточник:

````text
Spring HATEOAS's internal PropertyUtils.createObjectFromProperties method, used by the Collection+JSON and UBER media type deserializers, performs bean property binding via reflection without consulting Jackson access-control annotations.

Affected versions:
Spring HATEOAS 1.5.0 through 1.5.6; 2.3.0 through 2.3.4; 2.4.0 through 2.4.1; 2.5.0 through 2.5.2; 3.0.0 through 3.0.3.
````

