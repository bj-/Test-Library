#!/usr/bin/env python3
"""Select candidate checks by profile tags and priority."""
from pathlib import Path
import sys,yaml
R={"P0":0,"P1":1,"P2":2,"P3":3}
def read(p):
 with p.open(encoding="utf-8") as f:return yaml.safe_load(f) or {}
def main(root,name):
 root=Path(root); p=root/"profiles"/(name if name.endswith(".yaml") else name+".yaml")
 if not p.exists(): print("Unknown profile",name,file=sys.stderr);return 2
 profile=read(p); inc=set(profile["include_tags"]); exc=set(profile["exclude_tags"]); maxrank=R[profile["max_priority"]]; selected=[]
 for f in sorted((root/"checks").rglob("*.yaml")):
  for c in read(f).get("checks",[]):
   tags=set(c.get("tags",[]))
   if not tags&inc or tags&exc or R.get(c.get("priority","P3"),3)>maxrank:continue
   if profile["selection"]["deterministic_only"] and not c.get("automation",{}).get("deterministic",False):continue
   selected.append(c)
 for c in sorted(selected,key=lambda x:(R.get(x["priority"],3),x["id"])):print(f"{c['priority']}\t{c['id']}\t{c['title']}")
 print(f"Selected: {len(selected)}",file=sys.stderr);return 0
if __name__=="__main__":
 if len(sys.argv)!=3:print("Usage: select_checks.py <library-root> <profile>",file=sys.stderr);raise SystemExit(2)
 raise SystemExit(main(sys.argv[1],sys.argv[2]))
