#!/usr/bin/env python3
"""Commit one finished LLM batch of a source session (scaling, mining/sessions.md).

Usage (from Api/): commit_batch.py --batch ghsa-pip --name b-01

Several sessions share one working tree, so only the batch's own files are committed (`git commit --only`),
never `git add .`; waits while another git command or a rebase is running. Push is tried once: rejected
(the remote is ahead) — the commit stays local and the internal session pushes it after `pull --rebase`.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from library import setup_console  # noqa: E402

MINING = Path("build/mining")
TRAILER = "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"


def git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], capture_output=True, text=True, encoding="utf-8")


def wait_git_idle(git_dir: Path, timeout: int = 300) -> None:
    busy = [git_dir / "index.lock", git_dir / "rebase-merge", git_dir / "rebase-apply"]
    start = time.time()
    while any(p.exists() for p in busy):
        if time.time() - start > timeout:
            sys.exit(f"git занят дольше {timeout} с ({[p.name for p in busy if p.exists()]}) — повторить позже")
        time.sleep(3)


def main() -> int:
    setup_console()
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--batch", required=True)
    ap.add_argument("--name", required=True)
    args = ap.parse_args()

    base = MINING / args.batch / "batches"
    paths = [base / f"{args.name}.ids", base / f"{args.name}.out.jsonl"]
    if missing := [str(p) for p in paths if not p.exists()]:
        sys.exit(f"нет файлов партии: {missing}")
    rows = [json.loads(line) for line in paths[1].open(encoding="utf-8") if line.strip()]
    verdicts = Counter(r["verdict"] for r in rows)
    matches = Counter(r["match"]["type"] for r in rows if r["verdict"] == "api")
    msg = (f"Выгрузка багов: {args.batch} {args.name} — {len(rows)} багов, API {verdicts['api']} "
           f"(new {matches['new']}, extends {matches['extends']}, covered {matches['covered']})")

    git_dir = Path(git("rev-parse", "--absolute-git-dir").stdout.strip())
    for attempt in range(5):
        wait_git_idle(git_dir)
        add = git("add", "--", *map(str, paths))
        commit = add.returncode == 0 and git("commit", "-q", "-m", msg, "-m", TRAILER, "--only", "--", *map(str, paths))
        if commit and commit.returncode == 0:
            break
        err = (commit.stderr if commit else add.stderr) or (commit.stdout if commit else "")
        if "nothing to commit" in err or "no changes added" in err:
            print("уже закоммичено")
            break
        if "index.lock" not in err:
            sys.exit(f"git: {err.strip()}")
        time.sleep(5)
    else:
        sys.exit("git занят — повторить позже")
    print(msg)
    git("push", "-q")  # on Windows may exit 255 on success — compare with the upstream instead
    if git("rev-parse", "HEAD").stdout == git("rev-parse", "@{u}").stdout:
        print("push: ok")
    else:
        print("push отложен (remote впереди или нет сети) — коммит локальный, отправит внутренняя сессия")
    return 0


if __name__ == "__main__":
    sys.exit(main())
