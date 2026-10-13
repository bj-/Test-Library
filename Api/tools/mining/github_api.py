"""Polite GitHub API client for bug mining: sequential requests, pacing, rate-limit reserve, backoff.

Token: GITHUB_TOKEN / GH_TOKEN, otherwise `gh auth token`. The token is never printed.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request

API = "https://api.github.com"


class StopCollection(Exception):
    """Limit cannot be waited out within max_wait_s: stop, continue on the next run."""


def get_token() -> str:
    for name in ("GITHUB_TOKEN", "GH_TOKEN"):
        if os.environ.get(name):
            return os.environ[name].strip()
    gh = shutil.which("gh")
    if not gh and os.path.exists(r"C:\Program Files\GitHub CLI\gh.exe"):
        gh = r"C:\Program Files\GitHub CLI\gh.exe"
    if gh:
        r = subprocess.run([gh, "auth", "token"], capture_output=True, text=True)
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout.strip()
    sys.exit("Нет токена GitHub: задайте GITHUB_TOKEN или выполните `gh auth login`.")


class GitHub:
    def __init__(self, politeness: dict, token: str | None = None):
        self.p = politeness
        self.token = token or get_token()
        self._last = 0.0
        self.requests = 0

    def _pace(self) -> None:
        wait = self.p.get("min_interval_s", 1.5) - (time.monotonic() - self._last)
        if wait > 0:
            time.sleep(wait)
        self._last = time.monotonic()

    def _wait_until(self, reset_epoch: float, why: str) -> None:
        wait = max(0.0, reset_epoch - time.time()) + 5
        if wait > self.p.get("max_wait_s", 3600):
            raise StopCollection(f"{why}: до сброса {int(wait)} с — продолжите позже")
        print(f"  [{why}] пауза {int(wait)} с", file=sys.stderr)
        time.sleep(wait)

    def _check_reserve(self, headers) -> None:
        limit, remaining = headers.get("X-RateLimit-Limit"), headers.get("X-RateLimit-Remaining")
        if not (limit and remaining):
            return
        if int(remaining) < int(limit) * self.p.get("rate_limit_reserve", 0.2):
            self._wait_until(float(headers.get("X-RateLimit-Reset", time.time() + 60)),
                             f"резерв лимита {remaining}/{limit}")

    def request(self, method: str, url: str, body: dict | None = None):
        """Returns (json, headers). Retries on secondary limits and 5xx with backoff."""
        if not url.startswith("http"):
            url = API + url
        data = json.dumps(body).encode() if body is not None else None
        backoff = list(self.p.get("backoff_s", [60, 120, 300]))
        while True:
            self._pace()
            req = urllib.request.Request(url, data=data, method=method, headers={
                "Authorization": f"Bearer {self.token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
                "User-Agent": self.p.get("user_agent", "Test-Library-bug-mining"),
            })
            self.requests += 1
            try:
                with urllib.request.urlopen(req, timeout=60) as resp:
                    payload = json.loads(resp.read().decode("utf-8") or "null")
                    self._check_reserve(resp.headers)
                    return payload, resp.headers
            except urllib.error.HTTPError as e:
                h = e.headers
                if e.code in (403, 429):
                    if h.get("Retry-After"):
                        self._wait_until(time.time() + int(h["Retry-After"]), f"HTTP {e.code} Retry-After")
                        continue
                    if h.get("X-RateLimit-Remaining") == "0":
                        self._wait_until(float(h.get("X-RateLimit-Reset", time.time() + 60)), "лимит исчерпан")
                        continue
                if (e.code in (403, 429) or e.code >= 500) and backoff:
                    pause = backoff.pop(0)
                    print(f"  [HTTP {e.code}] пауза {pause} с и повтор", file=sys.stderr)
                    time.sleep(pause)
                    continue
                raise RuntimeError(f"HTTP {e.code} {url}: {e.read()[:300]!r}") from None
            except (urllib.error.URLError, TimeoutError) as e:
                if backoff:
                    pause = backoff.pop(0)
                    print(f"  [сеть: {e}] пауза {pause} с и повтор", file=sys.stderr)
                    time.sleep(pause)
                    continue
                raise

    def graphql(self, query: str, variables: dict) -> dict:
        payload, _ = self.request("POST", API + "/graphql", {"query": query, "variables": variables})
        if payload.get("errors"):
            raise RuntimeError(f"GraphQL: {payload['errors']}")
        return payload["data"]

    def paginate(self, path: str):
        """REST pagination by Link header; yields items."""
        url = path
        while url:
            items, headers = self.request("GET", url)
            yield from items
            url = None
            for part in (headers.get("Link") or "").split(","):
                if 'rel="next"' in part:
                    url = part[part.find("<") + 1:part.find(">")]
