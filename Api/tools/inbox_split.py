"""Переносит разобранные идеи из ideas/inbox.md в ideas/processed.md.

    python tools/inbox_split.py [--dry-run]

Разобранная - статус `→ ...` или `отклонено...`. Строка с неизвестным статусом остаётся в inbox: это повод посмотреть
на неё, а не потерять. Строка с наибольшим номером остаётся всегда: по ней считается следующий номер идеи.
"""
import argparse
import re
import sys
from pathlib import Path

INBOX = Path("ideas/inbox.md")
PROCESSED = Path("ideas/processed.md")
ROW = re.compile(r"^\| (\d+) \|")
DONE = re.compile(r"\| *(→|отклонено)[^|]*\|\s*$")
HEADER = ("# Разобранные идеи тестов\n\nАрхив `inbox.md`: номера те же, сквозные. Читать только по запросу, "
          "искать - grep.\n\n| # | Дата | Идея | Откуда | Пример / обоснование | Статус |\n|---|---|---|---|---|---|\n")


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    lines = INBOX.read_text(encoding="utf-8").splitlines(keepends=True)
    numbers = [int(m[1]) for m in map(ROW.match, lines) if m]
    last = max(numbers)
    keep, move = [], []
    for line in lines:
        m = ROW.match(line)
        (move if m and int(m[1]) != last and DONE.search(line) else keep).append(line)
    print(f"в inbox остаётся строк идей: {len(numbers) - len(move)}, переносится: {len(move)}, "
          f"размер inbox: {len(''.join(keep).encode())} байт")
    if args.dry_run or not move:
        return 0
    head = PROCESSED.read_text(encoding="utf-8") if PROCESSED.exists() else HEADER
    PROCESSED.write_text(head + "".join(move), encoding="utf-8", newline="\n")
    INBOX.write_text("".join(keep), encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
