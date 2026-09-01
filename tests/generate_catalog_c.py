#!/usr/bin/env python3
"""Generate Catalog C after preserving Catalog B's localization failure."""
from __future__ import annotations
import csv,hashlib,json,sys
from pathlib import Path
OUT=Path(sys.argv[1]); N=30; SEED=8017
def dump(p,o): p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(o,indent=2,sort_keys=True)+"\n",encoding="utf-8")
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
OUT.mkdir(parents=True,exist_ok=False); root=OUT/"fixture"; (root/"raw").mkdir(parents=True)
records=[]
for i in range(N):
 task=i%3!=0; goal=i%5==0; raw={"duration":2+i/100,"fixture":"holdout-c","i":200+i,"security":goal,"utility":task}; p=root/"raw"/f"c{i:02d}.json"; dump(p,raw); rel=p.relative_to(root).as_posix(); records.append({"unit_id":f"c{i:02d}","raw_path":rel,"raw_sha256":sha(p),"source_commit":"holdout-c-commit","benchmark_version":"v1.2.1","population_id":"AGENTDOJO_V1_2_1_FROZEN","task_success":task,"attack_present":True,"attack_goal_achieved":goal})
dump(root/"records.json",records); cells={k:0 for k in ("TASK_SUCCESS__ATTACK_NOT_ACHIEVED","TASK_SUCCESS__ATTACK_ACHIEVED","TASK_FAILURE__ATTACK_NOT_ACHIEVED","TASK_FAILURE__ATTACK_ACHIEVED")}
for r in records: cells[("TASK_SUCCESS" if r["task_success"] else "TASK_FAILURE")+"__"+("ATTACK_ACHIEVED" if r["attack_goal_achieved"] else "ATTACK_NOT_ACHIEVED")]+=1
dump(root/"summary.json",{"attack_present":N,"cells":cells,"no_injection":0,"selected_records":N}); (root/"lineage.jsonl").write_text("".join(json.dumps({"derived":f"records.json#{r['unit_id']}","source":r["raw_path"],"unit_id":r["unit_id"]},sort_keys=True)+"\n" for r in records),encoding="utf-8"); dump(root/"selection.json",{"benchmark_version":"v1.2.1","population_id":"AGENTDOJO_V1_2_1_FROZEN","selected_unit_ids":[r["unit_id"] for r in records],"source_commit":"holdout-c-commit"}); dump(root/"source_manifest.json",{"files":[{"bytes":(root/r["raw_path"]).stat().st_size,"path":r["raw_path"],"sha256":r["raw_sha256"]} for r in records]}); dump(root/"dependency_lock.json",{"dependencies":[],"schema_version":"1.0"}); dump(root/"claims.json",[{"claim_id":"c-claim","target":"summary.json#/selected_records","target_sha256":sha(root/"summary.json")}])
ops=[
 ("invalid_raw_json","BYTE_DRIFT","raw",""), ("manifest_entry_omission","SELECTION_MANIFEST","source_manifest.json","files"), ("manifest_duplicate_path","DUPLICATE_MANIFEST_PATH","source_manifest.json","files"), ("record_hash_blank","DERIVED_SUBSTITUTION","records.json","raw_sha256"), ("source_commit_blank","VERSION_MISMATCH","records.json","source_commit"), ("attack_present_integer","LABEL_CORRUPTION","records.json","attack_present"), ("attack_goal_null","LABEL_CORRUPTION","records.json","attack_goal_achieved"), ("selection_duplicate_id","SELECTION_DUPLICATE","selection.json","selected_unit_ids"),
 ("raw_manifest_changed_record_stale","DERIVED_SUBSTITUTION","records.json","raw_sha256"), ("summary_claim_coordinated_drift","RESULT_VALUE","summary.json","selected_records"), ("claim_redirect_existing_bad_pointer","CLAIM_POINTER","claims.json","target")]
rows=[]; k=0
for op,alarm,file_hint,field in ops:
 layer="COMPOUND_CHALLENGE" if op in {"raw_manifest_changed_record_stale","summary_claim_coordinated_drift","claim_redirect_existing_bad_pointer"} else "FRESH_INVARIANT_OR_BOUNDARY"
 for i in range(N):
  k+=1; target=f"raw/c{i:02d}.json" if file_hint=="raw" else file_hint; rows.append({"mutation_id":f"C{k:04d}","layer":layer,"operator":op,"site":i,"target":target,"expected_alarm_class":alarm,"expected_file":target if file_hint=="raw" else file_hint,"expected_field":field,"expected_outcome":"FAIL","classification":"IN_SCOPE_REQUIRED","seed":SEED})
with (OUT/"CATALOG_C.csv").open("w",newline="",encoding="utf-8") as f: w=csv.DictWriter(f,list(rows[0])); w.writeheader(); w.writerows(rows)
with (OUT/"CATALOG_C_ORACLE_FROZEN.csv").open("w",newline="",encoding="utf-8") as f: w=csv.DictWriter(f,["mutation_id","expected_alarm_class","expected_file","expected_field","expected_outcome"]); w.writeheader(); w.writerows([{x:r[x] for x in w.fieldnames} for r in rows])
dump(OUT/"CATALOG_C_ACCEPTANCE_CRITERIA.json",{"one_shot":True,"catalog_size":len(rows),"compound_challenge":90,"pass":"all detected, classified, and localized","inference_ceiling":"exact performance on declared Catalog C only","seed":SEED}); print(json.dumps({"catalog_c":len(rows),"compound_challenge":90},indent=2))
