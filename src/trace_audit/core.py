from __future__ import annotations
import hashlib, json
from pathlib import Path, PurePosixPath

REQUIRED=("records.json","summary.json","lineage.jsonl","claims.json","selection.json","source_manifest.json","dependency_lock.json")

def sha256(path:Path)->str:
 h=hashlib.sha256()
 with path.open('rb') as f:
  for b in iter(lambda:f.read(1<<20),b''): h.update(b)
 return h.hexdigest()

def load_json(path:Path): return json.loads(path.read_text(encoding='utf-8'))

def validate_bundle(root:Path)->list[dict]:
 root=Path(root); issues=[]
 def issue(code,file,field,detail): issues.append({'code':code,'file':file,'field':field,'detail':detail})
 for name in REQUIRED:
  if not (root/name).is_file(): issue('MISSING_FILE',name,'','required audit input is absent')
 if issues: return issues
 try:
  records=load_json(root/'records.json'); summary=load_json(root/'summary.json'); claims=load_json(root/'claims.json'); selection=load_json(root/'selection.json'); sm=load_json(root/'source_manifest.json'); dep=load_json(root/'dependency_lock.json')
  lineage=[json.loads(x) for x in (root/'lineage.jsonl').read_text(encoding='utf-8').splitlines() if x]
 except Exception as e:
  issue('PARSE_ERROR','bundle','',f'{type(e).__name__}: {e}'); return issues
 if dep.get('schema_version')!='1.0': issue('SCHEMA_VERSION','dependency_lock.json','schema_version','expected 1.0')
 required={'unit_id','raw_path','raw_sha256','source_commit','benchmark_version','population_id','task_success','attack_present','attack_goal_achieved'}
 for i,r in enumerate(records):
  if not isinstance(r,dict): issue('SCHEMA_TYPE','records.json',f'[{i}]','record must be an object'); continue
  miss=required-set(r)
  if miss: issue('SCHEMA_FIELD','records.json',f'[{i}]','missing '+','.join(sorted(miss)))
 if not isinstance(records,list): issue('SCHEMA_TYPE','records.json','','expected a JSON array'); return issues
 if not isinstance(summary,dict) or not isinstance(claims,list) or not isinstance(selection,dict) or not isinstance(sm,dict) or not isinstance(dep,dict):
  issue('SCHEMA_TYPE','bundle','','top-level JSON types do not match the declared schemas'); return issues
 paths=[r.get('raw_path') for r in records]; ids=[r.get('unit_id') for r in records]
 if len(paths)!=len(set(paths)): issue('DUPLICATE_PATH','records.json','raw_path','raw paths are not unique')
 if len(ids)!=len(set(ids)): issue('DUPLICATE_UNIT_ID','records.json','unit_id','unit identifiers are not unique')
 for i,r in enumerate(records):
  if not isinstance(r,dict): issue('SCHEMA_TYPE','records.json',f'[{i}]','record must be an object'); continue
  uid=r.get('unit_id'); raw_path=r.get('raw_path')
  if not isinstance(uid,str) or not uid: issue('SCHEMA_FIELD','records.json',f'[{i}].unit_id','non-empty string required')
  if not isinstance(raw_path,str) or not raw_path:
   issue('SCHEMA_FIELD','records.json',f'[{i}].raw_path','non-empty relative POSIX path required')
  else:
   q=PurePosixPath(raw_path)
   if q.is_absolute() or '..' in q.parts or '\\' in raw_path: issue('UNSAFE_PATH','records.json',f'[{i}].raw_path','path must be relative, normalized POSIX without parent traversal')
  if r.get('source_commit')!=selection.get('source_commit'): issue('VERSION_MISMATCH','records.json',f'[{i}].source_commit','record/source commit differs')
  if r.get('benchmark_version')!=selection.get('benchmark_version'): issue('VERSION_MISMATCH','records.json',f'[{i}].benchmark_version','record/benchmark version differs')
  if r.get('population_id')!=selection.get('population_id'): issue('POPULATION_MIX','records.json',f'[{i}].population_id','population guard failed')
  if not isinstance(r.get('task_success'),bool): issue('LABEL_CORRUPTION','records.json',f'[{i}].task_success','Boolean required')
  if not isinstance(r.get('attack_present'),bool): issue('LABEL_CORRUPTION','records.json',f'[{i}].attack_present','Boolean required')
  if r.get('attack_present') and not isinstance(r.get('attack_goal_achieved'),bool): issue('LABEL_CORRUPTION','records.json',f'[{i}].attack_goal_achieved','Boolean required for attack-present records')
 manifest_rows=sm.get('files',[])
 if not isinstance(manifest_rows,list): issue('SCHEMA_TYPE','source_manifest.json','files','expected an array'); manifest_rows=[]
 manifest_paths=[x.get('path') for x in manifest_rows if isinstance(x,dict)]
 if len(manifest_paths)!=len(set(manifest_paths)): issue('DUPLICATE_MANIFEST_PATH','source_manifest.json','files','manifest paths are not unique')
 manifest={x.get('path'):x for x in manifest_rows if isinstance(x,dict)}
 for r in records:
  if not isinstance(r,dict) or not isinstance(r.get('raw_path'),str): continue
  q=PurePosixPath(r['raw_path'])
  if q.is_absolute() or '..' in q.parts or '\\' in r['raw_path']: continue
  p=root/r['raw_path']; m=manifest.get(r['raw_path'])
  if not p.is_file(): issue('MISSING_SOURCE',r['raw_path'],'','source file missing'); continue
  actual=sha256(p)
  if not m: issue('SELECTION_MANIFEST','source_manifest.json','files','selected path absent from source manifest')
  elif actual!=m.get('sha256') or p.stat().st_size!=m.get('bytes'): issue('BYTE_DRIFT',r['raw_path'],'sha256','source bytes differ from manifest')
  if actual!=r.get('raw_sha256'): issue('DERIVED_SUBSTITUTION','records.json',f"{r['unit_id']}.raw_sha256",'derived source hash differs')
  try:
   raw=load_json(p)
   expected_task=bool(raw['utility'])
   expected_attack='security' in raw and raw.get('security') is not None
   expected_goal=bool(raw['security']) if expected_attack else None
   if r.get('task_success')!=expected_task: issue('DERIVED_VALUE_MISMATCH','records.json',f"{r['unit_id']}.task_success",'derived task label differs from raw fixture')
   if r.get('attack_present')!=expected_attack: issue('DERIVED_VALUE_MISMATCH','records.json',f"{r['unit_id']}.attack_present",'derived attack-presence label differs from raw fixture')
   if r.get('attack_goal_achieved')!=expected_goal: issue('DERIVED_VALUE_MISMATCH','records.json',f"{r['unit_id']}.attack_goal_achieved",'derived attack-goal label differs from raw fixture')
  except Exception:
   # Parse errors are already detected by the manifest byte-identity check.
   pass
 chosen=selection.get('selected_unit_ids',[])
 if not isinstance(chosen,list): issue('SCHEMA_TYPE','selection.json','selected_unit_ids','expected an array'); chosen=[]
 if len(chosen)!=len(set(chosen)): issue('SELECTION_DUPLICATE','selection.json','selected_unit_ids','selection contains duplicate unit identifiers')
 if set(chosen)!=set(ids) or len(chosen)!=len(ids): issue('SELECTION_MANIFEST','selection.json','selected_unit_ids','selection does not bijectively match records')
 attack=[r for r in records if r.get('attack_present')]; no=[r for r in records if not r.get('attack_present')]
 cells={'TASK_SUCCESS__ATTACK_NOT_ACHIEVED':0,'TASK_SUCCESS__ATTACK_ACHIEVED':0,'TASK_FAILURE__ATTACK_NOT_ACHIEVED':0,'TASK_FAILURE__ATTACK_ACHIEVED':0}
 for r in attack:
  k=('TASK_SUCCESS' if r['task_success'] else 'TASK_FAILURE')+'__'+('ATTACK_ACHIEVED' if r['attack_goal_achieved'] else 'ATTACK_NOT_ACHIEVED'); cells[k]+=1
 expected={'selected_records':len(records),'attack_present':len(attack),'no_injection':len(no),'cells':cells}
 for key,val in expected.items():
  if summary.get(key)!=val: issue('RESULT_VALUE','summary.json',key,f'expected {val!r}; observed {summary.get(key)!r}')
 ledges={x.get('unit_id'):x for x in lineage if isinstance(x,dict)}
 if len(lineage)!=len(ledges): issue('LINEAGE_DUPLICATE','lineage.jsonl','unit_id','duplicate lineage unit id')
 for r in records:
  e=ledges.get(r['unit_id'])
  if not e: issue('LINEAGE_MISSING','lineage.jsonl',f"unit_id={r['unit_id']}",'no lineage edge'); continue
  if e.get('source')!=r['raw_path'] or e.get('derived')!=f"records.json#{r['unit_id']}": issue('LINEAGE_REDIRECT','lineage.jsonl',r['unit_id'],'edge target differs')
 for i,c in enumerate(claims):
  if not isinstance(c,dict): issue('SCHEMA_TYPE','claims.json',f'[{i}]','claim must be an object'); continue
  target=c.get('target',''); expected_hash=c.get('target_sha256')
  f,sep,pointer=target.partition('#'); p=root/f
  if not p.is_file(): issue('CLAIM_TARGET','claims.json',f'[{i}].target','target file missing')
  elif expected_hash!=sha256(p): issue('CLAIM_HASH','claims.json',f'[{i}].target_sha256','target hash differs')
  elif not sep or not pointer.startswith('/'):
   issue('CLAIM_POINTER','claims.json',f'[{i}].target','JSON pointer is missing or malformed')
  else:
   try:
    value=load_json(p)
    for token in pointer[1:].split('/'):
     token=token.replace('~1','/').replace('~0','~')
     value=value[int(token)] if isinstance(value,list) else value[token]
   except Exception:
    issue('CLAIM_POINTER','claims.json',f'[{i}].target','JSON pointer does not resolve')
 return issues
