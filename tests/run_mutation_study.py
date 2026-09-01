from __future__ import annotations
import copy,csv,hashlib,json,shutil,sys,tempfile,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from trace_audit.core import sha256,validate_bundle

OUT=Path(sys.argv[1]); OUT.mkdir(parents=True,exist_ok=True)
def dump(p,o): p.write_text(json.dumps(o,indent=2,sort_keys=True)+'\n',encoding='utf-8')
def make_fixture(root):
 root.mkdir(); (root/'raw').mkdir(); records=[]
 cells=[(True,False),(True,True),(False,False),(False,True)]
 for i in range(16):
  task,goal=cells[i%4]; raw={'fixture':True,'i':i,'utility':task,'security':goal,'duration':1+i/10}
  p=root/'raw'/f'r{i:02d}.json'; dump(p,raw); rel=p.relative_to(root).as_posix()
  records.append({'unit_id':f'u{i:02d}','raw_path':rel,'raw_sha256':sha256(p),'source_commit':'fixture-commit','benchmark_version':'v1.2.1','population_id':'AGENTDOJO_V1_2_1_FROZEN','task_success':task,'attack_present':True,'attack_goal_achieved':goal})
 dump(root/'records.json',records)
 cellsd={k:0 for k in ('TASK_SUCCESS__ATTACK_NOT_ACHIEVED','TASK_SUCCESS__ATTACK_ACHIEVED','TASK_FAILURE__ATTACK_NOT_ACHIEVED','TASK_FAILURE__ATTACK_ACHIEVED')}
 for r in records: cellsd[('TASK_SUCCESS' if r['task_success'] else 'TASK_FAILURE')+'__'+('ATTACK_ACHIEVED' if r['attack_goal_achieved'] else 'ATTACK_NOT_ACHIEVED')]+=1
 dump(root/'summary.json',{'selected_records':16,'attack_present':16,'no_injection':0,'cells':cellsd})
 (root/'lineage.jsonl').write_text(''.join(json.dumps({'unit_id':r['unit_id'],'source':r['raw_path'],'derived':f"records.json#{r['unit_id']}"},sort_keys=True)+'\n' for r in records))
 dump(root/'selection.json',{'source_commit':'fixture-commit','benchmark_version':'v1.2.1','population_id':'AGENTDOJO_V1_2_1_FROZEN','selected_unit_ids':[r['unit_id'] for r in records]})
 dump(root/'source_manifest.json',{'files':[{'path':r['raw_path'],'bytes':(root/r['raw_path']).stat().st_size,'sha256':r['raw_sha256']} for r in records]})
 dump(root/'dependency_lock.json',{'schema_version':'1.0','dependencies':[]})
 dump(root/'claims.json',[{'claim_id':'c1','target':'summary.json#/selected_records','target_sha256':sha256(root/'summary.json')}])
 dump(root/'container.json',{'packing_order':'canonical'}); dump(root/'notes.json',{'comment':'clean'})
 return records
def load(p): return json.loads(p.read_text())
def mutate(root,op,idx=None):
 target=''; field=''; expected='FAIL'
 if op=='missing_file': target=f'raw/r{idx:02d}.json'; (root/target).unlink()
 elif op=='file_truncation': target=f'raw/r{idx:02d}.json'; (root/target).write_bytes((root/target).read_bytes()[:5])
 elif op=='single_byte_drift': target=f'raw/r{idx:02d}.json'; b=bytearray((root/target).read_bytes()); b[-2]^=1; (root/target).write_bytes(b)
 elif op=='path_rename': target=f'raw/r{idx:02d}.json'; (root/target).rename(root/'raw'/f'renamed{idx:02d}.json')
 elif op in ('duplicate_path','duplicate_unit_identifier','version_mismatch','label_corruption','population_identifier_mix','derived_record_substitution','result_value_alteration'):
  target='records.json'; r=load(root/target)
  if op=='duplicate_path': field='raw_path'; r[idx][field]=r[(idx+1)%16][field]
  elif op=='duplicate_unit_identifier': field='unit_id'; r[idx][field]=r[(idx+1)%16][field]
  elif op=='version_mismatch': field='benchmark_version'; r[idx][field]='v0'
  elif op=='label_corruption': field='task_success'; r[idx][field]='yes'
  elif op=='population_identifier_mix': field='population_id'; r[idx][field]='OTHER'
  elif op=='derived_record_substitution': field='raw_sha256'; r[idx][field]='0'*64
  else: field='task_success'; r[idx][field]=not r[idx][field]
  dump(root/target,r)
 elif op in ('denominator_increment','denominator_decrement'):
  target='summary.json'; field='attack_present'; x=load(root/target); x[field]+=1 if op.endswith('increment') else -1; dump(root/target,x)
 elif op=='selection_manifest_alteration': target='selection.json'; field='selected_unit_ids'; x=load(root/target); x[field].remove(f'u{idx:02d}'); dump(root/target,x)
 elif op in ('lineage_edge_deletion','lineage_edge_redirection'):
  target='lineage.jsonl'; field=f'u{idx:02d}'; lines=[json.loads(x) for x in (root/target).read_text().splitlines()]
  if op.endswith('deletion'): lines=[x for x in lines if x['unit_id']!=field]
  else: next(x for x in lines if x['unit_id']==field)['source']='raw/wrong.json'
  (root/target).write_text(''.join(json.dumps(x,sort_keys=True)+'\n' for x in lines))
 elif op=='claim_locator_hash_alteration': target='claims.json'; field='[0].target_sha256'; x=load(root/target); x[0]['target_sha256']='0'*64; dump(root/target,x)
 elif op=='claim_locator_target_alteration': target='claims.json'; field='[0].target'; x=load(root/target); x[0]['target']='missing.json#/x'; dump(root/target,x)
 elif op=='dependency_schema_version_alteration': target='dependency_lock.json'; field='schema_version'; x=load(root/target); x[field]='9.9'; dump(root/target,x)
 elif op=='order_only_change': target='records.json'; x=load(root/target); x.reverse(); dump(root/target,x); expected='PASS'
 elif op=='archive_repackaging': target='container.json'; dump(root/target,{'packing_order':'reversed','timestamp':'changed'}); expected='PASS'
 elif op=='benign_metadata_change': target='notes.json'; dump(root/target,{'comment':'changed outside scientific identity'}); expected='PASS'
 else: raise ValueError(op)
 return target,field,expected

with tempfile.TemporaryDirectory() as td:
 td=Path(td); clean=td/'clean'; make_fixture(clean)
 catalog=[]; mid=0
 record_ops=['missing_file','file_truncation','single_byte_drift','path_rename','duplicate_path','duplicate_unit_identifier','version_mismatch','label_corruption','population_identifier_mix','selection_manifest_alteration','lineage_edge_deletion','lineage_edge_redirection','derived_record_substitution','result_value_alteration']
 for op in record_ops:
  for i in range(16): mid+=1; catalog.append((f'M{mid:04d}',op,i,'IN_SCOPE_REQUIRED'))
 for op in ['denominator_increment','denominator_decrement','claim_locator_hash_alteration','claim_locator_target_alteration','dependency_schema_version_alteration']:
  mid+=1; catalog.append((f'M{mid:04d}',op,None,'IN_SCOPE_REQUIRED'))
 for op in ['order_only_change','archive_repackaging','benign_metadata_change']:
  mid+=1; catalog.append((f'C{mid:04d}',op,None,'NEGATIVE_CONTROL'))
 results=[]
 # clean control
 issues=validate_bundle(clean); results.append({'mutation_id':'CLEAN','operator':'clean','target':'bundle','original_hash':'','mutated_hash':'','expected_outcome':'PASS','observed_outcome':'PASS' if not issues else 'FAIL','expected_location':'','observed_location':'','exit_code':0 if not issues else 2,'diagnostic':json.dumps(issues,sort_keys=True),'runtime_seconds':0,'classification':'NEGATIVE_CONTROL'})
 for mid,op,i,cls in catalog:
  work=td/mid; shutil.copytree(clean,work); target,field,expected=mutate(work,op,i); before=sha256(clean/target) if (clean/target).is_file() else 'MISSING'; after=sha256(work/target) if (work/target).is_file() else 'MISSING'
  t=time.perf_counter(); issues=validate_bundle(work); elapsed=time.perf_counter()-t; observed='FAIL' if issues else 'PASS'; locations=';'.join(sorted({f"{x['file']}:{x['field']}" for x in issues}))
  results.append({'mutation_id':mid,'operator':op,'target':target,'original_hash':before,'mutated_hash':after,'expected_outcome':expected,'observed_outcome':observed,'expected_location':target+((':'+field) if field else ''),'observed_location':locations,'exit_code':2 if issues else 0,'diagnostic':json.dumps(issues,sort_keys=True),'runtime_seconds':f'{elapsed:.6f}','classification':cls})
 fields=list(results[0])
 with (OUT/'MUTATION_RESULTS.csv').open('w',newline='') as f: w=csv.DictWriter(f,fields); w.writeheader(); w.writerows(results)
 with (OUT/'MUTATION_CATALOG.csv').open('w',newline='') as f: w=csv.DictWriter(f,fields); w.writeheader(); w.writerows([{**r,'observed_outcome':'','observed_location':'','exit_code':'','diagnostic':'','runtime_seconds':''} for r in results])
 ops=sorted({r['operator'] for r in results}); km=[]
 for op in ops:
  rr=[r for r in results if r['operator']==op]; required=[r for r in rr if r['expected_outcome']=='FAIL']; controls=[r for r in rr if r['expected_outcome']=='PASS']
  km.append({'operator':op,'cases':len(rr),'required_cases':len(required),'detected':sum(r['observed_outcome']=='FAIL' for r in required),'false_successes':sum(r['observed_outcome']=='PASS' for r in required),'controls':len(controls),'false_alarms':sum(r['observed_outcome']=='FAIL' for r in controls)})
 with (OUT/'MUTATION_KILL_MATRIX.csv').open('w',newline='') as f: w=csv.DictWriter(f,list(km[0])); w.writeheader(); w.writerows(km)
 required=[r for r in results if r['expected_outcome']=='FAIL']; controls=[r for r in results if r['expected_outcome']=='PASS']
 analysis={'space':'exhaustive over 16-record declared fixture and singleton structured objects','required_mutants':len(required),'detected':sum(r['observed_outcome']=='FAIL' for r in required),'survivors':[r['mutation_id'] for r in required if r['observed_outcome']=='PASS'],'controls':len(controls),'false_alarms':sum(r['observed_outcome']=='FAIL' for r in controls),'file_localized':sum(r['target'] in r['observed_location'] for r in required),'field_localized_when_declared':sum((not r['expected_location'].partition(':')[2]) or r['expected_location'].partition(':')[2] in r['observed_location'] for r in required),'exact_rates_are_within_declared_space_only':True}
 analysis['pass']=analysis['detected']==analysis['required_mutants'] and not analysis['survivors'] and analysis['false_alarms']==0 and analysis['file_localized']==analysis['required_mutants'] and analysis['field_localized_when_declared']==analysis['required_mutants']
 dump(OUT/'MUTATION_ANALYSIS.json',analysis); dump(OUT/'NEGATIVE_CONTROL_REPORT.json',{'controls':[r for r in controls],'false_alarms':analysis['false_alarms'],'pass':analysis['false_alarms']==0})
 if not analysis['pass']: raise SystemExit(json.dumps(analysis))
 print(json.dumps(analysis,indent=2))
