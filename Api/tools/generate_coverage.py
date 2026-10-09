#!/usr/bin/env python3
"""Generate API access-control coverage candidates from OpenAPI + access model.

Inputs use OpenAPI 3.x YAML/JSON and a small YAML access model. The generator
creates reviewable test candidates; it does not execute requests or infer policy
that is absent from the inputs.
"""
from __future__ import annotations
import argparse, json, re, sys
from pathlib import Path
from collections import Counter, defaultdict
import yaml

DIMENSIONS = ["authentication", "authorization", "resource_ownership", "tenant_isolation", "roles_scopes"]
PRIORITY_ORDER = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}
PROFILE_TAGS = {"Smoke": ["smoke"], "CI": ["ci"], "PR": ["pr"], "Regression": ["regression"], "Release": ["release"], "Nightly": ["nightly"]}

def load_doc(path):
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict): raise ValueError(f"Expected YAML/JSON object in {path}")
    return data

def slug(s):
    s = re.sub(r"[^A-Za-z0-9]+", "-", s).strip("-").upper()
    return s[:48].strip("-") or "OP"

def resolve_ref(doc, obj):
    if not isinstance(obj, dict) or "$ref" not in obj: return obj or {}
    ref = obj["$ref"]
    if not ref.startswith("#/components/"): return {}
    cur = doc
    for part in ref[2:].split("/"): cur = cur.get(part, {}) if isinstance(cur, dict) else {}
    return cur if isinstance(cur, dict) else {}

def operation_auth(doc, op):
    sec = op.get("security", doc.get("security", []))
    if sec == []: return False, []
    schemes = sorted({name for entry in (sec or []) for name in entry.keys()})
    return bool(sec), schemes

def determine_cells(op, path, method, model, doc):
    ac = op.get("x-access-control", {}) or {}
    global_ac = model.get("defaults", {}) or {}
    resource = ac.get("resource", global_ac.get("resource", ""))
    ownership = ac.get("ownership", global_ac.get("ownership", "unknown"))
    tenant = ac.get("tenant_isolation", global_ac.get("tenant_isolation", "unknown"))
    roles = ac.get("roles", global_ac.get("roles", [])) or []
    scopes = ac.get("scopes", global_ac.get("scopes", [])) or []
    action = ac.get("action", method.lower())
    authenticated, schemes = operation_auth(doc, op)
    public = ac.get("public", not authenticated)
    out, questions = [], []
    if not public:
        out.append(("authentication", "missing_or_invalid_credentials", "P1", "high", "Reject absent or invalid credentials"))
        out.append(("authentication", "expired_or_revoked_token", "P1", "high", "Reject expired/revoked credentials where token auth applies"))
    elif ac.get("public") is True and authenticated:
        questions.append({"type":"contradiction", "operation":f"{method.upper()} {path}", "question":"Operation marked public in access model but OpenAPI declares security requirements."})
    out.append(("authorization", "disallowed_action", "P1", "high", "Reject action not granted by policy"))
    if "{" in path and "}" in path:
        if ownership == "required":
            out.append(("resource_ownership", "other_users_resource", "P1", "high", "Deny access to a resource owned by another subject"))
        elif ownership == "not_applicable": pass
        else:
            questions.append({"type":"needs_clarification", "operation":f"{method.upper()} {path}", "question":"Does this operation enforce resource ownership? Set x-access-control.ownership to required or not_applicable."})
    if tenant == "required":
        out.append(("tenant_isolation", "cross_tenant_resource", "P0", "high", "Deny cross-tenant read/write and prevent state changes"))
    elif tenant == "not_applicable": pass
    else:
        questions.append({"type":"needs_clarification", "operation":f"{method.upper()} {path}", "question":"Is this operation tenant-scoped? Set x-access-control.tenant_isolation to required or not_applicable."})
    if roles or scopes:
        out.append(("roles_scopes", "insufficient_role_or_scope", "P1", "high", "Reject caller lacking the required role/scope"))
        if any(str(r).lower() in ("admin", "owner", "superuser") for r in roles):
            out.append(("roles_scopes", "vertical_privilege_escalation", "P1", "medium", "Prevent lower-privilege subject from performing privileged action"))
    else:
        questions.append({"type":"needs_clarification", "operation":f"{method.upper()} {path}", "question":"No roles/scopes declared. Add x-access-control.roles/scopes or explicitly set authorization_policy: any_authenticated."})
    return out, questions, {"resource":resource,"ownership":ownership,"tenant_isolation":tenant,"roles":roles,"scopes":scopes,"action":action,"security_schemes":schemes,"authenticated":authenticated,"public":public}

def profiles_for(priority, dimension, deterministic=True):
    profiles = []
    if priority in ("P0", "P1") and deterministic:
        profiles += ["CI", "Regression", "Release"]
        if priority == "P0" or dimension in ("authentication", "resource_ownership", "tenant_isolation"):
            profiles.append("Smoke")
    else:
        profiles += ["Regression", "Nightly"]
    return list(dict.fromkeys(profiles))

def build_check(opid, path, method, cell, metadata, op):
    dim, case, priority, likelihood, assertion = cell
    cid = "GEN-" + slug(f"{opid}-{dim}-{case}")
    tags = ["security", "negative"]
    if dim == "authentication": tags += ["authn", "token-lifecycle"]
    if dim == "authorization": tags += ["authz"]
    if dim == "roles_scopes": tags += ["roles-scopes", "privilege-escalation"]
    if dim == "resource_ownership": tags += ["ownership"]
    if dim == "tenant_isolation": tags += ["tenant-isolation"]
    tags += [p.lower() for p in profiles_for(priority, dim)]
    target = path
    steps = [{"action":"Prepare principal and resource fixtures for the selected access-control case", "data":{"operation":f"{method.upper()} {path}","dimension":dim,"case":case,"resource":metadata.get("resource"),"roles":metadata.get("roles",[]),"scopes":metadata.get("scopes",[]) }},
             {"action":f"Send {method.upper()} request to {target} with the negative access-control fixture", "notes":"Use isolated test identities and synthetic data; do not use production credentials or data."}]
    expected = [assertion, "No protected data is disclosed and no unauthorized state change occurs."]
    return {"id":cid,"title":f"Generated {dim.replace('_',' ')} check: {case.replace('_',' ')} for {method.upper()} {path}","description":"Generated candidate from OpenAPI operation metadata and access model. Review before execution.","category":"security","protocols":["rest"],"kind":"security","priority":priority,"tags":list(dict.fromkeys(tags)),"preconditions":["Test environment and synthetic principals are available", "Expected access policy has been confirmed"],"steps":steps,"expected":expected,"applicability":{"when":[f"OpenAPI operation exists: {method.upper()} {path}", f"Access-control dimension {dim} is applicable"],"skip_when":["Operation is explicitly marked not applicable for this dimension"]},"automation":{"level":"partial","deterministic":True,"notes":"Candidate requires fixture binding and policy-specific expected status configuration."},"profiles":profiles_for(priority,dim),"risk":{"impact":"critical" if priority=="P0" else "high" if priority=="P1" else "medium","likelihood":likelihood},"references":["OpenAPI operation metadata", "x-access-control access model"]}

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--openapi", required=True, help="OpenAPI 3.x YAML or JSON")
    ap.add_argument("--access-model", required=True, help="Access model YAML")
    ap.add_argument("--out", required=True, help="Output directory")
    args=ap.parse_args()
    doc=load_doc(args.openapi); model=load_doc(args.access_model)
    if not str(doc.get("openapi","3.")).startswith("3."):
        raise ValueError("OpenAPI document must declare OpenAPI 3.x")
    out=Path(args.out); checks_dir=out/"generated_checks"; checks_dir.mkdir(parents=True,exist_ok=True)
    checks=[]; questions=[]; cells=[]; operation_count=0
    paths=doc.get("paths",{}) or {}
    for path,pathitem in paths.items():
        if not isinstance(pathitem,dict): continue
        for method,rawop in pathitem.items():
            if method.lower() not in {"get","post","put","patch","delete","options","head"} or not isinstance(rawop,dict): continue
            op=resolve_ref(doc,rawop); operation_count+=1
            opid=op.get("operationId",f"{method}_{path}")
            opcells, oq, meta=determine_cells(op,path,method,model,doc)
            questions.extend(oq)
            for cell in opcells:
                check=build_check(opid,path,method,cell,meta,op)
                checks.append(check); cells.append({"operation":f"{method.upper()} {path}","dimension":cell[0],"case":cell[1],"priority":cell[2],"status":"candidate","check_id":check["id"]})
    # Deduplicate IDs safely if operation IDs collide.
    seen=Counter()
    for c in checks:
        seen[c["id"]]+=1
        if seen[c["id"]]>1: c["id"] += f"-{seen[c['id']]}"
        with open(checks_dir/(c["id"]+".yaml"),"w",encoding="utf-8") as f: yaml.safe_dump(c,f,sort_keys=False,allow_unicode=True)
    dim_counts=Counter(c["dimension"] for c in cells); priority_counts=Counter(c["priority"] for c in cells)
    summary={"openapi_title":doc.get("info",{}).get("title","Untitled API"),"openapi_version":doc.get("openapi"),"operations_discovered":operation_count,"candidate_checks":len(checks),"coverage_candidates_by_dimension":dict(dim_counts),"candidate_risks_by_priority":dict(priority_counts),"needs_clarification":len([q for q in questions if q["type"]=="needs_clarification"]),"contradictions":len([q for q in questions if q["type"]=="contradiction"]),"profiles":{"Smoke":sum("Smoke" in c["profiles"] for c in checks),"CI":sum("CI" in c["profiles"] for c in checks),"Regression":sum("Regression" in c["profiles"] for c in checks),"Release":sum("Release" in c["profiles"] for c in checks),"PR":sum("PR" in c["profiles"] for c in checks),"Nightly":sum("Nightly" in c["profiles"] for c in checks)},"limitations":["Candidate generation is not proof that policy is correct or complete.","Unknown policy is reported for clarification, not silently inferred.","Coverage counts are candidate counts, not execution/pass coverage."]}
    (out/"coverage_matrix.json").write_text(json.dumps(cells,indent=2,ensure_ascii=False),encoding="utf-8")
    (out/"coverage_report.json").write_text(json.dumps({"summary":summary,"questions":questions,"cells":cells},indent=2,ensure_ascii=False),encoding="utf-8")
    lines=["# API access-control coverage report", "", f"- API: **{summary['openapi_title']}**",f"- OpenAPI: `{summary['openapi_version']}`",f"- Operations discovered: **{operation_count}**",f"- Generated candidates: **{len(checks)}**",f"- Requirements needing clarification: **{summary['needs_clarification']}**",f"- Contradictions: **{summary['contradictions']}**","", "## Candidate coverage by dimension", "", "| Dimension | Candidate cells |", "|---|---:|"]
    for d in DIMENSIONS: lines.append(f"| {d} | {dim_counts.get(d,0)} |")
    lines += ["", "## Candidate checks by risk priority", "", "| Priority | Count |", "|---|---:|"]
    for p in ["P0","P1","P2","P3"]: lines.append(f"| {p} | {priority_counts.get(p,0)} |")
    lines += ["", "## Profile selection counts", "", "| Profile | Checks selected by metadata |", "|---|---:|"]
    for p,n in summary["profiles"].items(): lines.append(f"| {p} | {n} |")
    lines += ["", "## Questions and contradictions", ""]
    if not questions: lines.append("No clarification questions detected by the current rules.")
    else:
        for q in questions: lines.append(f"- **{q['type']}** — `{q['operation']}`: {q['question']}")
    lines += ["", "## Interpretation", "", "These are generated candidate cells, not verified runtime coverage. Confirm each policy, expected status/body, test fixture, and operation-specific exception before execution.", ""]
    (out/"coverage_report.md").write_text("\n".join(lines),encoding="utf-8")
    print(json.dumps(summary,indent=2,ensure_ascii=False))
    print(f"Artifacts written to: {out.resolve()}")
if __name__=="__main__":
    try: main()
    except Exception as e: print(f"ERROR: {e}",file=sys.stderr); sys.exit(2)
