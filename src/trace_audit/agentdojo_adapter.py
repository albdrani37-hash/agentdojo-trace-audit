from __future__ import annotations
import collections, csv, hashlib, json
from pathlib import Path
GROUPS=("Meta-SecAlign-70B","Meta-SecAlign-70B-repeat_user_prompt","meta-llama_Llama-3.3-70B-Instruct","meta-llama_Llama-3.3-70B-Instruct-repeat_user_prompt")
REQ=("utility","security","duration")
def digest(p):
 h=hashlib.sha256(); h.update(Path(p).read_bytes()); return h.hexdigest()
def selected(x,version): return x.get('benchmark_version')==version and str(x.get('user_task_id','')).startswith('user_task_') and all(k in x and x[k] is not None for k in REQ)
def reconstruct(source_root:Path,output:Path,commit:str,version:str,fraction:float=1.0):
 rows=[]; counts=collections.Counter(); candidates=0; exclusions=[]
 for group in GROUPS:
  for p in sorted((source_root/'runs'/group).rglob('*.json')):
   candidates+=1; x=json.loads(p.read_text(encoding='utf-8')); rel=p.relative_to(source_root).as_posix()
   if not selected(x,version):
    reason='AUXILIARY_INJECTION_AS_USER_TASK' if not str(x.get('user_task_id','')).startswith('user_task_') else 'INCOMPLETE_PRIMARY_RESULT'; exclusions.append({'path':rel,'reason':reason}); continue
   attack=x.get('injection_task_id') is not None; task=bool(x['utility']); goal=bool(x['security']) if attack else None
   rows.append({'unit_id':hashlib.sha256(rel.encode()).hexdigest()[:20],'raw_path':rel,'raw_sha256':digest(p),'source_commit':commit,'benchmark_version':version,'population_id':'AGENTDOJO_V1_2_1_FROZEN','task_success':task,'attack_present':attack,'attack_goal_achieved':goal,'run_group':group})
 rows.sort(key=lambda x:x['raw_path'])
 if fraction < 1.0:
  strata=collections.defaultdict(list)
  for r in rows:
   cell=('NO_INJECTION' if not r['attack_present'] else ('TS' if r['task_success'] else 'TF')+('_AA' if r['attack_goal_achieved'] else '_AN'))
   strata[(r['run_group'],cell)].append(r)
  chosen=[]
  for key,items in sorted(strata.items()):
   n=max(1,round(len(items)*fraction)); chosen.extend(items[:n])
  rows=sorted(chosen,key=lambda x:x['raw_path'])
 attack=[r for r in rows if r['attack_present']]
 for r in attack:
  counts[('TASK_SUCCESS' if r['task_success'] else 'TASK_FAILURE')+'__'+('ATTACK_ACHIEVED' if r['attack_goal_achieved'] else 'ATTACK_NOT_ACHIEVED')]+=1
 output.mkdir(parents=True,exist_ok=False)
 (output/'records.json').write_text(json.dumps(rows,indent=2,sort_keys=True)+'\n')
 (output/'summary.json').write_text(json.dumps({'candidate_files':candidates,'selected_records':len(rows),'attack_present':len(attack),'no_injection':len(rows)-len(attack),'cells':dict(sorted(counts.items()))},indent=2,sort_keys=True)+'\n')
 (output/'exclusions.json').write_text(json.dumps(exclusions,indent=2,sort_keys=True)+'\n')
 return rows
