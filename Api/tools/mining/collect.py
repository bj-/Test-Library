#!/usr/bin/env python3
"""Step 1 of bug mining: collect closed bugs from sources.yaml into build/mining/<batch>/raw/.

Usage: collect.py [--batch pilot] [--source ID ...] [--sources mining/sources.yaml]
A batch named after a source (--batch ghsa-pip) collects only that source.
Run from Api/. Resumable: a finished source is skipped (state.json) unless max_items was raised and it is not
exhausted (history ran out); an unfinished one continues
from the saved cursor. Requests are sequential and paced (politeness in sources.yaml).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from library import load_yaml, setup_console  # noqa: E402
from github_api import GitHub, StopCollection  # noqa: E402

ISSUES_QUERY = """
query($owner:String!,$name:String!,$labels:[String!],$type:String,$after:String){
  repository(owner:$owner,name:$name){
    issues(first:50,after:$after,states:CLOSED,labels:$labels,filterBy:{type:$type},orderBy:{field:CREATED_AT,direction:DESC}){
      pageInfo{hasNextPage endCursor}
      nodes{
        number title url body createdAt closedAt stateReason
        labels(first:30){nodes{name}}
        comments{totalCount} reactions{totalCount}
        timelineItems(first:40,itemTypes:[CLOSED_EVENT,CONNECTED_EVENT,CROSS_REFERENCED_EVENT]){nodes{
          __typename
          ... on ClosedEvent{closer{__typename
            ... on PullRequest{url merged repository{nameWithOwner}}
            ... on Commit{url}}}
          ... on ConnectedEvent{subject{__typename ... on PullRequest{url merged repository{nameWithOwner}}}}
          ... on CrossReferencedEvent{willCloseTarget source{__typename
            ... on PullRequest{url merged repository{nameWithOwner}}}}
        }}
      }
    }
  }
}"""

LABELS_QUERY = """
query($owner:String!,$name:String!,$after:String){
  repository(owner:$owner,name:$name){labels(first:100,after:$after){
    pageInfo{hasNextPage endCursor} nodes{name}}}
}"""


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def rx(pattern: str | None):
    return re.compile(" ".join(pattern.split())) if pattern else None


def repo_labels(gh: GitHub, owner: str, name: str) -> list[str]:
    out, after = [], None
    while True:
        d = gh.graphql(LABELS_QUERY, {"owner": owner, "name": name, "after": after})["repository"]["labels"]
        out += [n["name"] for n in d["nodes"]]
        if not d["pageInfo"]["hasNextPage"]:
            return out
        after = d["pageInfo"]["endCursor"]


def fix_refs(node: dict, repo: str) -> dict:
    """Merged PRs / commits of the same repo that fixed the issue."""
    prs, commits = [], []
    for ev in node["timelineItems"]["nodes"]:
        t = ev["__typename"]
        if t == "ClosedEvent" and ev.get("closer"):
            c = ev["closer"]
            if c["__typename"] == "PullRequest" and c["merged"]:
                prs.append(c["url"])
            elif c["__typename"] == "Commit":
                commits.append(c["url"])
        elif t == "ConnectedEvent" and ev["subject"].get("__typename") == "PullRequest":
            s = ev["subject"]
            if s["merged"] and s["repository"]["nameWithOwner"].lower() == repo.lower():
                prs.append(s["url"])
        elif t == "CrossReferencedEvent" and ev.get("willCloseTarget"):
            s = ev["source"]
            if s.get("__typename") == "PullRequest" and s["merged"]:
                prs.append(s["url"])
    return {"prs": sorted(set(prs)), "commits": sorted(set(commits))}


def collect_github(gh: GitHub, src: dict, defaults: dict, out: Path, state: dict) -> None:
    owner, name = src["repo"].split("/")
    all_labels = state.get("labels") or repo_labels(gh, owner, name)
    state["labels"] = all_labels
    inc = rx(src.get("include_labels", defaults["include_labels"]))
    exc_patterns = [p for p in (defaults.get("exclude_labels"), src.get("exclude_labels")) if p]
    exc = [rx(p) for p in exc_patterns]
    req = rx(src.get("require_labels"))
    # issue_type — репозиторий размечает баги типом issue (GitHub Issue Types), а не меткой: запрос по типу
    issue_type = src.get("issue_type")
    if issue_type:
        query_labels = None
        print(f"  тип issue: {issue_type}")
    else:
        query_labels = [lb for lb in all_labels if inc.search(lb) and not any(e.search(lb) for e in exc)]
        if not query_labels:
            raise RuntimeError(f"{src['id']}: ни одна метка не подошла под include_labels; метки: {all_labels}")
        print(f"  метки запроса: {query_labels}")
    state["query_labels"] = query_labels

    kept, after, scanned = state.get("kept", 0), state.get("cursor"), state.get("scanned", 0)
    # max_items raised after a finished run: the cursor may point at a partly read page, skip what is saved
    seen = {json.loads(line)["id"] for line in out.open(encoding="utf-8")} if out.exists() else set()
    with out.open("a", encoding="utf-8") as f:
        while kept < src["max_items"]:
            d = gh.graphql(ISSUES_QUERY, {"owner": owner, "name": name, "labels": query_labels,
                                             "type": issue_type, "after": after})
            page = d["repository"]["issues"]
            page_start, cut_short = after, False
            for n in page["nodes"]:
                if f"{src['repo']}#{n['number']}" in seen:
                    continue
                scanned += 1
                labels = [lb["name"] for lb in n["labels"]["nodes"]]
                if req and not any(req.search(lb) for lb in labels):
                    continue
                rec = {
                    "source": src["id"], "kind": "issue", "id": f"{src['repo']}#{n['number']}",
                    "url": n["url"], "title": n["title"], "body": n["body"] or "", "labels": labels,
                    "created": n["createdAt"], "closed": n["closedAt"], "state_reason": n["stateReason"],
                    "fix": fix_refs(n, src["repo"]), "comments": n["comments"]["totalCount"],
                    "reactions": n["reactions"]["totalCount"], "collected": now(),
                }
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
                kept += 1
                if kept >= src["max_items"]:
                    cut_short = n is not page["nodes"][-1]
                    break
            # stopped mid-page: keep the page start so a later run with a higher max_items reads the rest
            after = page_start if cut_short else page["pageInfo"]["endCursor"]
            state.update(kept=kept, cursor=after, scanned=scanned)
            f.flush()
            yield_state(state)
            if not cut_short and not page["pageInfo"]["hasNextPage"]:
                state["exhausted"] = True  # nothing older to collect even if max_items is raised
                break
    print(f"  просмотрено {scanned}, сохранено {kept}")


def collect_ghsa(gh: GitHub, src: dict, out: Path, state: dict) -> None:
    kept = state.get("kept", 0)
    seen = set()
    if out.exists():
        seen = {json.loads(line)["id"] for line in out.open(encoding="utf-8")}
    path = (f"/advisories?type=reviewed&ecosystem={src['ecosystem']}&per_page=100"
            f"&cwes={','.join(str(c) for c in src['cwes'])}&sort=published&direction=desc")
    with out.open("a", encoding="utf-8") as f:
        for a in gh.paginate(path):
            if kept >= src["max_items"]:
                break
            if a["ghsa_id"] in seen or a.get("withdrawn_at"):
                continue
            refs = a.get("references") or []
            rec = {
                "source": src["id"], "kind": "advisory", "id": a["ghsa_id"], "url": a["html_url"],
                "title": a["summary"], "body": a.get("description") or "",
                "labels": [f"CWE-{c['cwe_id'].split('-')[-1]}" for c in a.get("cwes") or []],
                "created": a.get("published_at"), "closed": a.get("published_at"), "state_reason": "PUBLISHED",
                "severity": a.get("severity"), "cve": a.get("cve_id"),
                "packages": sorted({v["package"]["name"] for v in a.get("vulnerabilities") or [] if v.get("package")}),
                "fix": {"prs": [r for r in refs if "/pull/" in r], "commits": [r for r in refs if "/commit/" in r]},
                "collected": now(),
            }
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            kept += 1
            state["kept"] = kept
            yield_state(state)
    if kept < src["max_items"]:
        state["exhausted"] = True  # advisories ran out before max_items
    print(f"  сохранено {kept}")


_state_saver = None


def yield_state(_state: dict) -> None:
    if _state_saver:
        _state_saver()


def main() -> int:
    global _state_saver
    setup_console()
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--batch", default="pilot")
    ap.add_argument("--source", action="append", help="только эти id источников")
    ap.add_argument("--sources", default="mining/sources.yaml")
    args = ap.parse_args()

    cfg = load_yaml(Path(args.sources))
    base = Path("build/mining") / args.batch
    raw = base / "raw"
    raw.mkdir(parents=True, exist_ok=True)
    state_path = base / "state.json"
    states = json.loads(state_path.read_text(encoding="utf-8")) if state_path.exists() else {}

    def save():
        state_path.write_text(json.dumps(states, ensure_ascii=False, indent=1), encoding="utf-8")
    _state_saver = save

    if not args.source and args.batch in {s["id"] for s in cfg["sources"]}:
        args.source = [args.batch]  # batch per source (scaling, one session per source)
    gh = GitHub(cfg["politeness"])
    for src in cfg["sources"]:
        if args.source and src["id"] not in args.source:
            continue
        st = states.setdefault(src["id"], {})
        if st.get("done") and (st.get("exhausted") or st.get("kept", 0) >= src["max_items"]):
            print(f"{src['id']}: уже собран ({st.get('kept')}{', исчерпан' if st.get('exhausted') else ''}), пропуск")
            continue
        if st.get("done"):
            print(f"{src['id']}: досбор {st.get('kept')} → {src['max_items']}")
            st.pop("done", None)
        print(f"{src['id']}:")
        out = raw / f"{src['id']}.jsonl"
        try:
            if src["type"] == "github":
                collect_github(gh, src, cfg["defaults"], out, st)
            elif src["type"] == "ghsa":
                collect_ghsa(gh, src, out, st)
            else:
                print(f"  тип {src['type']} пока не поддерживается")
                continue
            st.update(done=True, finished=now())
        except StopCollection as e:
            print(f"Остановка: {e}")
            save()
            return 2
        finally:
            save()
    print(f"Запросов к API: {gh.requests}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
