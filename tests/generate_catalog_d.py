#!/usr/bin/env python3
"""Generate Catalog D without importing the verifier."""
from __future__ import annotations
import csv,hashlib,json,sys
from pathlib import Path

OUT=Path(sys.argv[1]); N=30; SEED=9029
def dump(p,o): p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(o,indent=2,sort_keys=True)+"\n",encoding="utf-8")
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
OUT.mkdir(parents=True,exist_ok=False); root=OUT/"fixture"; (root/"raw").mkdir(parents=True)
records=[]
for i in range(N):
    task=i%2==0; goal=i%4==0
    raw={"duration":3+i/100,"fixture":"confirmatory-d","i":400+i,"security":goal,"utility":task}
    p=root/"raw"/f"d{i:02d}.json"; dump(p,raw); rel=p.relative_to(root).as_posix()
    records.append({"unit_id":f"d{i:02d}","raw_path":rel,"raw_sha256":sha(p),"source_commit":"holdout-d-commit","benchmark_version":"v1.2.1","population_id":"AGENTDOJO_V1_2_1_FROZEN","task_success":task,"attack_present":True,"attack_goal_achieved":goal})
dump(root/"records.json",records)
cells={k:0 for k in ("TASK_SUCCESS__ATTACK_NOT_ACHIEVED","TASK_SUCCESS__ATTACK_ACHIEVED","TASK_FAILURE__ATTACK_NOT_ACHIEVED","TASK_FAILURE__ATTACK_ACHIEVED")}
for r in records: cells[("TASK_SUCCESS" if r["task_success"] else "TASK_FAILURE")+"__"+("ATTACK_ACHIEVED" if r["attack_goal_achieved"] else "ATTACK_NOT_ACHIEVED")]+=1
dump(root/"summary.json",{"attack_present":N,"cells":cells,"no_injection":0,"selected_records":N})
(root/"lineage.jsonl").write_text("".join(json.dumps({"derived":f"records.json#{r['unit_id']}","source":r["raw_path"],"unit_id":r["unit_id"]},sort_keys=True)+"\n" for r in records),encoding="utf-8")
dump(root/"selection.json",{"benchmark_version":"v1.2.1","population_id":"AGENTDOJO_V1_2_1_FROZEN","selected_unit_ids":[r["unit_id"] for r in records],"source_commit":"holdout-d-commit"})
dump(root/"source_manifest.json",{"files":[{"bytes":(root/r["raw_path"]).stat().st_size,"path":r["raw_path"],"sha256":r["raw_sha256"]} for r in records]})
dump(root/"dependency_lock.json",{"dependencies":[],"schema_version":"1.0"})
dump(root/"claims.json",[{"claim_id":"d-claim","target":"summary.json#/selected_records","target_sha256":sha(root/"summary.json")}])
dump(root/"notes.json",{"note":"non-scientific optional metadata"})
ops=[
 ("missing_source","INVARIANT_TARGETED","MISSING_SOURCE","raw",""),
 ("byte_drift","INVARIANT_TARGETED","BYTE_DRIFT","raw","sha256"),
 ("wrong_version","INVARIANT_TARGETED","VERSION_MISMATCH","records.json","source_commit"),
 ("boolean_type","BOUNDARY_ADVERSARIAL","LABEL_CORRUPTION","records.json","task_success"),
 ("lineage_delete","INVARIANT_TARGETED","LINEAGE_MISSING","lineage.jsonl","unit_id"),
 ("lineage_redirect","COMPOUND_CHALLENGE","LINEAGE_REDIRECT","lineage.jsonl","unit_id"),
 ("coordinated_raw_manifest_change","COMPOUND_CHALLENGE","DERIVED_SUBSTITUTION","records.json","raw_sha256"),
 ("swap_two_sources_with_manifest_update","COMPOUND_CHALLENGE","DERIVED_SUBSTITUTION","records.json","raw_sha256"),
 ("summary_claim_coordinated_drift","COMPOUND_CHALLENGE","RESULT_VALUE","summary.json","selected_records"),
 ("claim_bad_pointer_valid_hash","BOUNDARY_ADVERSARIAL","CLAIM_POINTER","claims.json","target"),
 ("delete_add_constant_count","COMPOUND_CHALLENGE","SELECTION_MANIFEST","selection.json","selected_unit_ids"),
 ("cross_field_inconsistency","COMPOUND_CHALLENGE","RESULT_VALUE","summary.json","attack_present"),
]
rows=[]; k=0
for op,layer,alarm,file_hint,field in ops:
    for i in range(N):
        k+=1; uid=f"d{i:02d}"; target=f"raw/{uid}.json" if file_hint=="raw" else file_hint
        expfield=(f"unit_id={uid}" if op=="lineage_delete" else uid if op=="lineage_redirect" else f"{uid}.{field}" if file_hint=="records.json" and field in {"raw_sha256"} else field)
        rows.append({"mutation_id":f"D{k:04d}","layer":layer,"operator":op,"site":i,"target":target,"eligible_sites":N,"expected_alarm_class":alarm,"expected_file":target if file_hint=="raw" else file_hint,"expected_field":expfield,"expected_outcome":"FAIL","classification":"IN_SCOPE_REQUIRED","seed":SEED})
fields=list(rows[0])
for name,data,keep in [("CATALOG_D.csv",rows,fields),("CATALOG_D_ORACLE_FROZEN.csv",rows,["mutation_id","expected_alarm_class","expected_file","expected_field","expected_outcome"])]:
    with (OUT/name).open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,keep); w.writeheader(); w.writerows([{x:r[x] for x in keep} for r in data])
dump(OUT/"CATALOG_D_ACCEPTANCE_CRITERIA.json",{"one_shot":True,"catalog_size":len(rows),"seed":SEED,"eligible_operator_site_pairs":len(rows),"compound_challenge":180,"pass":{"detected":len(rows),"classified":len(rows),"localized":len(rows),"survivors":0},"criteria_frozen_before_run":True,"inference_ceiling":"exact performance on declared Catalog D only"})
print(json.dumps({"catalog_d":len(rows),"compound_challenge":180,"seed":SEED},indent=2))

