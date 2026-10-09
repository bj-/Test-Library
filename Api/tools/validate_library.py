#!/usr/bin/env python3
"""Validate YAML checks, schema, taxonomy and profile references."""
from pathlib import Path
import json, sys, yaml
try:
 from jsonschema import Draft202012Validator
except ImportError:
 Draft202012Validator = None
RUN_TAGS={"smoke","regression","nightly","release","pr","ci"}
def load(p):
 with p.open(encoding="utf-8") as f: return yaml.safe_load(f) or {}
def main(root):
 root=Path(root); errors=[]; checks=[]; seen=set()
 schema=json.loads((root/"schema/check.schema.json").read_text(encoding="utf-8"))
 profiles={p.stem for p in (root/"profiles").glob("*.yaml")}
 tagsdoc=load(root/"taxonomy/tags.yaml"); tags={x for group in tagsdoc["tag_groups"].values() for x in group}
 cats=set(load(root/"taxonomy/categories.yaml")["categories"])
 for path in sorted((root/"checks").rglob("*.yaml")):
  try: doc=load(path)
  except Exception as e: errors.append(f"{path}: YAML error: {e}"); continue
  if not isinstance(doc.get("checks"),list): errors.append(f"{path}: missing checks list"); continue
  for c in doc["checks"]:
   cid=c.get("id","<missing-id>"); checks.append(c)
   if cid in seen: errors.append(f"duplicate id: {cid}")
   seen.add(cid)
   if Draft202012Validator:
    for e in Draft202012Validator(schema).iter_errors(c): errors.append(f"{cid}: schema {'/'.join(map(str,e.absolute_path))}: {e.message}")
   if c.get("category") not in cats: errors.append(f"{cid}: unknown category {c.get('category')}")
   for t in c.get("tags",[]):
    if t not in tags: errors.append(f"{cid}: unknown tag {t}")
   for p in c.get("profiles",[]):
    if p not in profiles: errors.append(f"{cid}: unknown profile {p}")
   app=c.get("applicability",{})
   if not app.get("when"): errors.append(f"{cid}: applicability.when must not be empty")
   if "skip_when" not in app: errors.append(f"{cid}: applicability.skip_when must be present")
   if c.get("automation",{}).get("level")=="full" and c.get("automation",{}).get("deterministic") is not True: errors.append(f"{cid}: full automation requires deterministic=true")
   if c.get("kind") in RUN_TAGS: errors.append(f"{cid}: kind must not be a run tag")
 for p in sorted((root/"profiles").glob("*.yaml")):
  try:
   d=load(p)
   if d.get("id")!=p.stem: errors.append(f"{p}: id must match filename")
   for t in d.get("include_tags",[])+d.get("exclude_tags",[]):
    if t not in tags: errors.append(f"{p}: unknown tag {t}")
  except Exception as e: errors.append(f"{p}: YAML error: {e}")
 print(f"Checks: {len(checks)} | Unique IDs: {len(seen)} | Profiles: {len(profiles)}")
 print(f"JSON Schema validation: {'enabled' if Draft202012Validator else 'fallback; install jsonschema for full checks'}")
 print(f"Errors: {len(errors)}")
 for e in errors: print("ERROR:",e)
 return 1 if errors else 0
if __name__=="__main__": raise SystemExit(main(sys.argv[1] if len(sys.argv)>1 else "."))
