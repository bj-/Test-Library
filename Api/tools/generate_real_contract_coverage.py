from pathlib import Path
import yaml, json, re, shutil, subprocess, sys, zipfile, os
# Standalone mode: run from an extracted library; inputs are the checked-in real contracts.
api=Path(__file__).resolve().parents[1]
contracts=api/'examples'/'real-contracts'
if not (contracts/'bff-admin-api.openapi.yaml').exists() or not (contracts/'mobile-client-api.openapi.yaml').exists():
 raise FileNotFoundError('Expected both real OpenAPI contracts under examples/real-contracts/')

# Models intentionally encode only facts supported by the contracts; unknown policies remain questions.
models={
'bff-admin-api.access-model.yaml': {
 'version':2,'api':'Bff Admin API documentation','defaults':{'ownership':'unknown','tenant_isolation':'unknown','resource':'admin-managed-resource','roles':[],'scopes':[],'roles_model':'unknown'},
 'policy':{'deny_by_default':True,'mutation_must_leave_state_unchanged':True,'access_for_operations_without_security':'unknown_until_operation_review'},
 'operations':{
  'AuthController_login':{'public':True,'ownership':'not_applicable','tenant_isolation':'not_applicable','roles':[],'scopes':[],'resource':'admin-session'},
  'AuthController_logout':{'public':False,'ownership':'required','tenant_isolation':'not_applicable','roles':[],'scopes':[],'resource':'admin-session'},
  'AuthController_changePassword':{'public':False,'ownership':'required','tenant_isolation':'not_applicable','roles':[],'scopes':[],'resource':'account'},
  'AuthController_getSessions':{'public':False,'ownership':'unknown','tenant_isolation':'not_applicable','roles':[],'scopes':[],'resource':'admin-session'},
  'AuthController_deleteSession':{'public':False,'ownership':'required','tenant_isolation':'not_applicable','roles':[],'scopes':[],'resource':'admin-session'},
  'LayoutsController_publish':{'public':None,'access_policy_status':'needs_operation_review','ownership':'not_applicable','tenant_isolation':'unknown','roles':[],'scopes':[],'resource':'layout','action':'publish'},
  'LayoutsController_archive':{'public':None,'access_policy_status':'needs_operation_review','ownership':'not_applicable','tenant_isolation':'unknown','roles':[],'scopes':[],'resource':'layout','action':'archive'},
  'LayoutsController_toggleLanguage':{'public':None,'access_policy_status':'needs_operation_review','ownership':'not_applicable','tenant_isolation':'unknown','roles':[],'scopes':[],'resource':'layout','action':'update'},
  'LayoutsController_updateComponent':{'public':None,'access_policy_status':'needs_operation_review','ownership':'not_applicable','tenant_isolation':'unknown','roles':[],'scopes':[],'resource':'layout','action':'update'},
  'LayoutsController_saveTranslation':{'public':None,'access_policy_status':'needs_operation_review','ownership':'not_applicable','tenant_isolation':'unknown','roles':[],'scopes':[],'resource':'layout','action':'update'},
  'ContentController_createItem':{'public':None,'access_policy_status':'needs_operation_review','ownership':'not_applicable','tenant_isolation':'unknown','roles':[],'scopes':[],'resource':'content-item','action':'create'},
  'ContentController_updateItem':{'public':None,'access_policy_status':'needs_operation_review','ownership':'not_applicable','tenant_isolation':'unknown','roles':[],'scopes':[],'resource':'content-item','action':'update'},
  'ContentController_removeItem':{'public':None,'access_policy_status':'needs_operation_review','ownership':'not_applicable','tenant_isolation':'unknown','roles':[],'scopes':[],'resource':'content-item','action':'delete'},
  'AuditController_getEntries':{'public':None,'access_policy_status':'needs_operation_review','ownership':'not_applicable','tenant_isolation':'unknown','roles':[],'scopes':[],'resource':'audit-log','action':'read'},
 }
},
'mobile-client-api.access-model.yaml': {
 'version':2,'api':'API мобильного клиента','defaults':{'ownership':'unknown','tenant_isolation':'unknown','resource':'mobile-resource','roles':[],'scopes':[],'roles_model':'unknown'},
 'policy':{'deny_by_default':True,'mutation_must_leave_state_unchanged':True,'isolation_model':'unknown_until_owner_confirmation'},
 'operations':{
  'onStart':{'public':None,'access_policy_status':'needs_owner_confirmation','ownership':'not_applicable','tenant_isolation':'unknown','roles':[],'scopes':[],'resource':'app-start'},
  'sendCode':{'public':True,'ownership':'not_applicable','tenant_isolation':'not_applicable','roles':[],'scopes':[],'resource':'authentication-challenge'},
  'verifyCode':{'public':True,'ownership':'not_applicable','tenant_isolation':'not_applicable','roles':[],'scopes':[],'resource':'authentication-challenge'},
  'refresh':{'public':True,'ownership':'not_applicable','tenant_isolation':'not_applicable','roles':[],'scopes':[],'resource':'token-session'},
  'logout':{'public':False,'ownership':'required','tenant_isolation':'not_applicable','roles':[],'scopes':[],'resource':'token-session'},
  'getUnsignedDocuments':{'public':True,'ownership':'required','tenant_isolation':'unknown','roles':[],'scopes':[],'resource':'document-acceptance'},
  'acceptDocuments':{'public':True,'ownership':'required','tenant_isolation':'unknown','roles':[],'scopes':[],'resource':'document-acceptance','action':'accept'},
  'getDocumentsHistory':{'public':True,'ownership':'required','tenant_isolation':'unknown','roles':[],'scopes':[],'resource':'document-acceptance'},
  'getOnboardingStory':{'public':True,'ownership':'not_applicable','tenant_isolation':'unknown','roles':[],'scopes':[],'resource':'regional-content'},
  'getWidgetStories':{'public':True,'ownership':'not_applicable','tenant_isolation':'unknown','roles':[],'scopes':[],'resource':'regional-content'},
  'getFaqStories':{'public':True,'ownership':'not_applicable','tenant_isolation':'unknown','roles':[],'scopes':[],'resource':'regional-content'},
 }
}}
# Populate every admin operation lacking an effective security declaration as an explicit unresolved per-operation policy.
# Keep the login operation explicitly public because that is the known authentication entry point.
admin_doc=yaml.safe_load((contracts/'bff-admin-api.openapi.yaml').read_text(encoding='utf-8'))
admin_model=models['bff-admin-api.access-model.yaml']
for path,pathitem in (admin_doc.get('paths',{}) or {}).items():
 for method,op in pathitem.items():
  if method.lower() not in {'get','post','put','patch','delete','head','options'} or not isinstance(op,dict): continue
  opid=op.get('operationId',f'{method}_{path}')
  security=op.get('security',admin_doc.get('security',None))
  if security is None and opid!='AuthController_login':
   entry=admin_model['operations'].setdefault(opid, {'public':None,'access_policy_status':'needs_operation_review','ownership':'unknown' if '{' in path else 'not_applicable','tenant_isolation':'unknown','roles':[],'scopes':[],'resource':'admin-managed-resource'})
   entry['public']=None
   entry['access_policy_status']='needs_operation_review'
   entry['roles']=[]; entry['scopes']=[]
for fn,data in models.items():
 (contracts/fn).write_text(yaml.safe_dump(data,sort_keys=False,allow_unicode=True),encoding='utf-8')

# Build grounded inventory, clarification questions, and high-value candidates.
valid_tags=set()
tagsdoc=yaml.safe_load((api/'taxonomy/tags.yaml').read_text(encoding='utf-8'))
for group in tagsdoc['tag_groups'].values(): valid_tags.update(group)
profiles=['Smoke','CI','Regression','Release','Nightly','PR']
checks=[]; inventory=[]; questions=[]; ids=set()

def slug(s): return re.sub(r'[^A-Z0-9]+','-',s.upper()).strip('-')[:65].strip('-')
def add_check(prefix, opid, path, method, title, case, priority, dimension, assertion, tags, profile_list, preconditions=None, notes=None):
 cid=slug(f'REAL-{prefix}-{opid}-{case}')
 if cid in ids:
  i=2
  while f'{cid}-{i}' in ids: i+=1
  cid=f'{cid}-{i}'
 ids.add(cid)
 tags=list(dict.fromkeys(['security','negative']+tags+[p.lower() for p in profile_list]))
 tags=[t for t in tags if t in valid_tags]
 c={'id':cid,'title':title,'description':f'Кандидат сгенерирован по реальному OpenAPI-контракту. Политику доступа и тестовые данные подтвердить перед исполнением.','category':'security','protocols':['rest'],'kind':'security','priority':priority,'tags':tags,'preconditions':preconditions or ['Изолированное тестовое окружение и синтетические учётные записи доступны','Ожидаемая политика доступа подтверждена'],'steps':[{'action':f'Подготовить тестовые данные для {method.upper()} {path}; сценарий: {case}.','data':{'operationId':opid,'method':method.upper(),'path':path,'dimension':dimension}},{'action':f'Отправить {method.upper()} запрос на {path} с заданными credentials/ролью/ресурсом.','notes':notes or 'Не использовать production credentials или реальные пользовательские данные.'}],'expected':[assertion,'При отказе защищённые данные не раскрываются, а запрещённая мутация не меняет состояние.'],'applicability':{'when':[f'Операция присутствует в OpenAPI: {method.upper()} {path}',f'Политика для измерения {dimension} подтверждена'],'skip_when':['Политика явно помечена как неприменимая к операции']},'automation':{'level':'partial','deterministic':True,'notes':'Требуется привязка fixtures и фактического transport/client.'},'profiles':profile_list,'risk':{'impact':'critical' if priority=='P0' else 'high' if priority=='P1' else 'medium','likelihood':'high' if priority in ('P0','P1') else 'medium'},'references':[f'OpenAPI operationId={opid}',f'Contract: {prefix}']}
 checks.append(c)

specs=[('bff-admin-api','bff-admin-api.openapi.yaml','bff-admin-api.access-model.yaml'),('mobile-client-api','mobile-client-api.openapi.yaml','mobile-client-api.access-model.yaml')]
for prefix,specfile,modelfile in specs:
 doc=yaml.safe_load((contracts/specfile).read_text(encoding='utf-8')); model=yaml.safe_load((contracts/modelfile).read_text(encoding='utf-8'))
 opmodel=model['operations']; opcount=0
 for path,pathitem in doc.get('paths',{}).items():
  for method,op in pathitem.items():
   if method.lower() not in {'get','post','put','patch','delete','head','options'} or not isinstance(op,dict): continue
   opcount+=1; opid=op.get('operationId',f'{method}_{path}'); ac=opmodel.get(opid,{})
   # OpenAPI security alternatives: each array item is OR; schemes inside one item are AND.
   security=op.get('security',doc.get('security',None))
   sec_explicit=security is not None
   alternatives=security or []
   anonymous=any(isinstance(x,dict) and len(x)==0 for x in alternatives)
   scheme_names=sorted({s for alt in alternatives if isinstance(alt,dict) for s in alt})
   schemes=doc.get('components',{}).get('securitySchemes',{})
   user_token_schemes=[s for s in scheme_names if (schemes.get(s,{}) or {}).get('type')=='http' and (schemes.get(s,{}) or {}).get('scheme','').lower()=='bearer']
   cookie_schemes=[s for s in scheme_names if (schemes.get(s,{}) or {}).get('type')=='apiKey' and (schemes.get(s,{}) or {}).get('in')=='cookie']
   api_key_schemes=[s for s in scheme_names if (schemes.get(s,{}) or {}).get('type')=='apiKey' and (schemes.get(s,{}) or {}).get('in')=='header']
   sensitive=method.lower() in {'post','put','patch','delete'} and not any(x in path.lower() for x in ['/auth/login','/auth/send-code','/auth/verify-code','/auth/refresh'])
   roles=ac.get('roles',[]); scopes=ac.get('scopes',[])
   inv={'api':doc.get('info',{}).get('title'), 'operationId':opid,'method':method.upper(),'path':path,'tags':op.get('tags',[]),'security_declared':sec_explicit,'security_alternatives':alternatives,'security_schemes':scheme_names,'public_anonymous_alternative':anonymous,'access_model_entry':opid in opmodel,'ownership':ac.get('ownership',model['defaults'].get('ownership','unknown')),'tenant_isolation':ac.get('tenant_isolation',model['defaults'].get('tenant_isolation','unknown')),'roles':roles,'scopes':scopes,'public_policy':ac.get('public','unknown'),'access_policy_status':ac.get('access_policy_status','as_declared_or_unknown'),'roles_model':model['defaults'].get('roles_model','unknown')}
   inventory.append(inv)
   if not sec_explicit:
    questions.append({'type':'contract_security_gap','operation':f'{method.upper()} {path}','operationId':opid,'question':'OpenAPI does not declare a security requirement. Confirm this endpoint is intentionally public or add the actual cookie/Bearer/API-key security requirement.','risk':'high' if sensitive else 'medium'})
   if prefix=='mobile-client-api' and opid=='onStart' and anonymous:
    questions.append({'type':'contract_contradiction','operation':f'{method.upper()} {path}','operationId':opid,'question':'OpenAPI security includes an empty alternative {}, which permits anonymous access, while description says missing/invalid api-key returns 403. Confirm intended behavior and fix either security declaration or description.','risk':'high'})
   if ac.get('ownership','unknown')=='unknown' and ('{' in path or opid in {'getDocumentsHistory','acceptDocuments','getUnsignedDocuments'}):
    questions.append({'type':'needs_clarification','operation':f'{method.upper()} {path}','operationId':opid,'question':'Confirm whether resource ownership applies and how the principal/installation_id is bound to the resource.','risk':'high'})
   if ac.get('tenant_isolation',model['defaults'].get('tenant_isolation','unknown'))=='unknown':
    questions.append({'type':'needs_clarification','operation':f'{method.upper()} {path}','operationId':opid,'question':'Confirm whether regional/tenant isolation applies and identify the trusted tenant/region context. Do not assume installation_id or locale is a tenant boundary.','risk':'high' if sensitive else 'medium'})
   if sensitive and not roles and not scopes and opid not in {'logout','acceptDocuments','onStart'}:
    questions.append({'type':'needs_clarification','operation':f'{method.upper()} {path}','operationId':opid,'question':'Role/permission model is unknown. Confirm whether roles/scopes exist and specify the minimum privilege, or explicitly document that any authenticated principal may perform this action.','risk':'high'})
   if prefix=='mobile-client-api' and opid=='onStart':
    questions.append({'type':'owner_confirmation_required','operation':f'{method.upper()} {path}','operationId':opid,'question':'API owner must resolve whether api-key is mandatory. OpenAPI permits anonymous access via security alternative {}, while the description says missing/invalid api-key returns 403. Keep the definitive expected result blocked until confirmed.','risk':'high'})
   # Generate an explicit per-operation access-policy review candidate for each admin operation
   # whose OpenAPI operation has no effective security declaration (mixed policy must be reviewed operation by operation).
   if prefix=='bff-admin-api' and not sec_explicit and opid not in {'AuthController_login'}:
    add_check(prefix,opid,path,method,'Confirm operation-specific authentication and authorization policy','operation-access-policy-unresolved','P1','authorization','Expected authentication, authorization, and minimum privilege must be confirmed for this exact operation before converting this candidate into an executable assertion.', ['authz','roles-scopes'],['CI','Regression','Release'],notes='Blocked candidate: OpenAPI has no effective security requirement and policy is intentionally unresolved pending operation-by-operation review.')
   # Generate high-value checks grounded in contract security and operation behavior.
   if prefix=='bff-admin-api':
    if opid=='AuthController_login':
     add_check(prefix,opid,path,method,'Login rejects invalid credentials','invalid-credentials','P1','authentication','Invalid credentials are rejected without creating a session.', ['authn'],['Smoke','CI','Regression','Release'],['Test account exists with known test password'],'Assert documented response shape; do not assert rate limiting unless configured.')
    elif opid in {'AuthController_logout','AuthController_changePassword','AuthController_getSessions','AuthController_deleteSession'}:
     add_check(prefix,opid,path,method,'Cookie-authenticated endpoint rejects missing/invalid session', 'missing-or-invalid-cookie','P1','authentication','Request without a valid session cookie is rejected and no protected data/state is exposed.', ['authn','token-lifecycle'],['Smoke','CI','Regression','Release'])
     if opid in {'AuthController_getSessions','AuthController_deleteSession'}:
      add_check(prefix,opid,path,method,'Session endpoint enforces session ownership','cross-account-session','P1','resource_ownership','A principal cannot enumerate or terminate another account’s session unless explicitly authorized.', ['authz','ownership'],['CI','Regression','Release'])
     if opid=='AuthController_changePassword':
      add_check(prefix,opid,path,method,'Password change verifies current password','wrong-current-password','P1','authorization','Wrong current password is rejected and account credentials remain unchanged.', ['authz'],['CI','Regression','Release'])
    elif sensitive:
     if roles:
      add_check(prefix,opid,path,method,'Sensitive operation rejects insufficient role','insufficient-role','P1','roles_scopes','A principal without the required role cannot perform the operation; state remains unchanged.', ['authz','roles-scopes','privilege-escalation'],['CI','Regression','Release'])
   else:
    if opid in {'sendCode','verifyCode','refresh'}:
     case={'sendCode':'invalid-api-key','verifyCode':'invalid-api-key','refresh':'expired-or-invalid-refresh-token'}[opid]
     assertion={'sendCode':'Missing/invalid API key is rejected according to the contract and no challenge is sent.','verifyCode':'Missing/invalid API key is rejected; invalid/expired one-time code does not issue tokens.','refresh':'Expired, malformed, invalid-signature, or wrong-type refresh token is rejected and no new token pair is issued.'}[opid]
     add_check(prefix,opid,path,method,'Authentication endpoint rejects invalid credentials',case,'P1','authentication',assertion,['authn','token-lifecycle'] if opid=='refresh' else ['authn'],['Smoke','CI','Regression','Release'])
    elif opid=='logout':
     add_check(prefix,opid,path,method,'Logout requires a valid access token','missing-expired-or-refresh-token','P1','authentication','Missing, expired, malformed, or refresh token is rejected; valid access token logs out only its own session.', ['authn','token-lifecycle','ownership'],['Smoke','CI','Regression','Release'])
    elif opid in {'getUnsignedDocuments','acceptDocuments','getDocumentsHistory'}:
     add_check(prefix,opid,path,method,'Guest and authenticated document access follow distinct policies','guest-vs-authenticated','P1','authorization','Guest context is bound to installation_id; authenticated context is bound to the user, and one principal cannot read or mutate another principal’s acceptance/history.', ['authz','ownership'],['Smoke','CI','Regression','Release'] if opid=='acceptDocuments' else ['CI','Regression','Release'])
     if opid=='acceptDocuments':
      add_check(prefix,opid,path,method,'Document acceptance is bound to the correct principal and revision','cross-principal-or-stale-revision','P1','resource_ownership','Acceptance is recorded only for the intended principal and current document revision; rejected requests do not create acceptance records.', ['authz','ownership'],['CI','Regression','Release'])
    elif opid=='onStart':
     add_check(prefix,opid,path,method,'Startup endpoint matches the documented API-key policy','anonymous-vs-api-key','P1','authentication','Behavior for missing/invalid api-key matches the resolved contract policy; this test remains blocked until the security-description contradiction is resolved.', ['authn'],['CI','Regression','Release'])
   # role checks for admin sensitive endpoints even if security annotation missing, only when model declares roles
   if sensitive and not roles and not scopes and opid not in {'logout','acceptDocuments','onStart'}:
    add_check(prefix,opid,path,method,'Confirm minimum privilege policy for sensitive operation','role-model-unresolved','P1','roles_scopes','The operation must reject callers lacking the confirmed minimum role/scope; exact expected status and role fixture remain blocked until the API owner defines the authorization model.', ['authz','roles-scopes','privilege-escalation'],['CI','Regression','Release'],notes='Blocked candidate: role model is unknown; do not assume the role names or privileges from earlier draft models.')
 # add operation inventory stats in model file

# Write generated checks in library's expected wrapper format.
generated=api/'checks'/'generated'/'real-contracts'; generated.mkdir(parents=True,exist_ok=True)
for c in checks:
 p=generated/(c['id']+'.yaml')
 p.write_text(yaml.safe_dump({'checks':[c]},sort_keys=False,allow_unicode=True,width=110),encoding='utf-8')
# Outputs
reports=api/'build'/'real-contract-coverage'; reports.mkdir(parents=True,exist_ok=True)
(reports/'operation_inventory.json').write_text(json.dumps(inventory,ensure_ascii=False,indent=2),encoding='utf-8')
(reports/'clarification_questions.json').write_text(json.dumps(questions,ensure_ascii=False,indent=2),encoding='utf-8')
# Deduplicate questions by operation + text
uniq=[]; seenq=set()
for q in questions:
 key=(q['operationId'],q['type'],q['question'])
 if key not in seenq: seenq.add(key); uniq.append(q)
questions=uniq
(reports/'clarification_questions.json').write_text(json.dumps(questions,ensure_ascii=False,indent=2),encoding='utf-8')
by_api={}
for i in inventory: by_api.setdefault(i['api'],[]).append(i)
summary={'contracts':[],'operations_total':len(inventory),'generated_checks':len(checks),'unique_check_ids':len(ids),'clarification_items':len(questions),'security_gap_operations':sum(q['type']=='contract_security_gap' for q in questions),'contract_contradictions':sum(q['type']=='contract_contradiction' for q in questions)}
for api_title,items in by_api.items():
 summary['contracts'].append({'title':api_title,'operations':len(items),'security_declared':sum(x['security_declared'] for x in items),'security_missing':sum(not x['security_declared'] for x in items),'anonymous_alternative':sum(x['public_anonymous_alternative'] for x in items),'generated_checks':sum(1 for c in checks if any(r==f'Contract: {"bff-admin-api" if "Bff Admin" in api_title else "mobile-client-api"}' for r in c['references']))})
(reports/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
lines=['# Coverage analysis from real OpenAPI contracts','','## Summary',f"- Operations inventoried: **{len(inventory)}**",f"- Generated candidate checks: **{len(checks)}**",f"- Clarification items after deduplication: **{len(questions)}**",f"- Missing OpenAPI security declarations: **{summary['security_gap_operations']}**",f"- Explicit security contradictions: **{summary['contract_contradictions']}**",'', '## Contracts','']
for c in summary['contracts']:
 lines += [f"### {c['title']}",f"- Operations: {c['operations']}",f"- Operations with security declared: {c['security_declared']}",f"- Operations without security declared: {c['security_missing']}",f"- Operations with anonymous alternative: {c['anonymous_alternative']}",'']
lines += ['## High-priority findings','', '1. **Bff Admin API:** access is reviewed per operation. Operations without an OpenAPI `security` declaration remain unresolved individually; do not infer that they are public or protected until each operation is confirmed.', '2. **Mobile API `onStart`:** `security` contains `{}` as an alternative, which permits anonymous access, while the description says a missing/invalid `api-key` returns 403.', '3. **Mobile document endpoints:** security alternatives mean `Api-Key + Bearer` OR `Api-Key` only. Ownership/installation binding remains unconfirmed; do not treat installation ID as a proven isolation boundary.', '4. **Role model and mobile isolation:** role model and region/installation isolation remain unknown by request; related checks are candidates blocked on owner clarification, not confirmed policy.', '', '## Clarification queue','']
for q in questions:
 lines.append(f"- **{q['type']}** · `{q['operationId']}` · {q['question']}")
lines += ['', '## Generated candidates','']
for c in checks: lines.append(f"- `{c['id']}` — {c['title']} [{', '.join(c['profiles'])}]")
lines += ['', '## Interpretation','', 'Generated checks are reviewable candidates, not executed tests. A `needs_clarification` item is a blocker for a definitive expected result. Coverage counts are generated candidates, not runtime pass coverage.', '']
(reports/'REAL_CONTRACT_COVERAGE_REPORT.md').write_text('\n'.join(lines),encoding='utf-8')
# machine-readable mapping of generated checks to operation
(reports/'generated_check_index.json').write_text(json.dumps([{'id':c['id'],'title':c['title'],'profiles':c['profiles'],'priority':c['priority'],'references':c['references']} for c in checks],ensure_ascii=False,indent=2),encoding='utf-8')
# README
(api/'docs'/'REAL_CONTRACTS_STAGE4.md').write_text('''# Stage 4 — analysis of real contracts\n\nInput contracts are preserved in `examples/real-contracts/`. Access models in the same folder are deliberately conservative. Admin endpoints lacking security are marked for per-operation review; role model and mobile isolation remain unknown; POST /onStart is blocked on API-owner confirmation.\n\nRun the generator prototype against synthetic/demo inputs as before; for the supplied real contracts, review `build/real-contract-coverage/REAL_CONTRACT_COVERAGE_REPORT.md`, `operation_inventory.json`, `clarification_questions.json`, and generated candidates under `checks/generated/real-contracts/`.\n\nThe generated candidates are schema-shaped YAML records and should be reviewed before execution. They are not evidence of runtime behavior.\n''',encoding='utf-8')
# Keep this real-contract generator reproducible inside the library.
# Generator is already this checked-in file; no copy step needed.

# Run validator and separately schema-validate generated checks
val=subprocess.run([sys.executable,str(api/'tools'/'validate_library.py'),str(api)],capture_output=True,text=True)
(reports/'library_validation.txt').write_text(val.stdout+val.stderr,encoding='utf-8')
try:
 import jsonschema
 schema=json.loads((api/'schema/check.schema.json').read_text(encoding='utf-8'))
 errors=[]
 for c in checks:
  errors += [(c['id'],e.message) for e in jsonschema.Draft202012Validator(schema).iter_errors(c)]
except Exception as e: errors=[('validator-exception',str(e))]
(reports/'generated_schema_validation.json').write_text(json.dumps({'generated_checks':len(checks),'schema_errors':len(errors),'errors':errors},ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'summary':summary,'library_validator_exit':val.returncode,'library_validator_output':val.stdout[-2000:],'generated_schema_errors':len(errors),'reports':str(reports)},ensure_ascii=False,indent=2))
# zip package
zip_path=api.parent.parent/'API_Test_Library_Stage4_Real_Contracts.zip'
if zip_path.exists(): zip_path.unlink()
with zipfile.ZipFile(zip_path,'w',zipfile.ZIP_DEFLATED) as z:
 for p in api.rglob('*'):
  if p.is_file(): z.write(p,Path('api-test-library-stage4-real-contracts')/p.relative_to(api))
print('ZIP',zip_path,zip_path.stat().st_size)
