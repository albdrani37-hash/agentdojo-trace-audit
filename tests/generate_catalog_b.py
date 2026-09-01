#!/usr/bin/env python3
"""Generate frozen Catalog B inputs and an oracle separated from validator calls."""
from __future__ import annotations
import csv, hashlib, json, random, sys
from pathlib import Path

OUT = Path(sys.argv[1])
SEED = 8008
N = 24

def dump(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def make_fixture(root):
    root.mkdir(parents=True)
    (root / "raw").mkdir()
    records=[]
    cells=[(True,False),(True,True),(False,False),(False,True)]
    for i in range(N):
        task,goal=cells[i%4]
        raw={"duration": round(1+i/10,1), "fixture":"holdout-b", "i":100+i, "security":goal, "utility":task}
        p=root/"raw"/f"b{i:02d}.json"; dump(p,raw)
        rel=p.relative_to(root).as_posix()
        records.append({"unit_id":f"b{i:02d}","raw_path":rel,"raw_sha256":sha(p),"source_commit":"holdout-b-commit","benchmark_version":"v1.2.1","population_id":"AGENTDOJO_V1_2_1_FROZEN","task_success":task,"attack_present":True,"attack_goal_achieved":goal})
    dump(root/"records.json",records)
    cellsd={k:0 for k in ("TASK_SUCCESS__ATTACK_NOT_ACHIEVED","TASK_SUCCESS__ATTACK_ACHIEVED","TASK_FAILURE__ATTACK_NOT_ACHIEVED","TASK_FAILURE__ATTACK_ACHIEVED")}
    for r in records:
        cellsd[("TASK_SUCCESS" if r["task_success"] else "TASK_FAILURE")+"__"+("ATTACK_ACHIEVED" if r["attack_goal_achieved"] else "ATTACK_NOT_ACHIEVED")]+=1
    dump(root/"summary.json",{"attack_present":N,"cells":cellsd,"no_injection":0,"selected_records":N})
    (root/"lineage.jsonl").write_text("".join(json.dumps({"derived":f"records.json#{r['unit_id']}","source":r["raw_path"],"unit_id":r["unit_id"]},sort_keys=True)+"\n" for r in records),encoding="utf-8")
    dump(root/"selection.json",{"benchmark_version":"v1.2.1","population_id":"AGENTDOJO_V1_2_1_FROZEN","selected_unit_ids":[r["unit_id"] for r in records],"source_commit":"holdout-b-commit"})
    dump(root/"source_manifest.json",{"files":[{"bytes":(root/r["raw_path"]).stat().st_size,"path":r["raw_path"],"sha256":r["raw_sha256"]} for r in records]})
    dump(root/"dependency_lock.json",{"dependencies":[],"schema_version":"1.0"})
    dump(root/"claims.json",[{"claim_id":"b-claim","target":"summary.json#/selected_records","target_sha256":sha(root/"summary.json")}])
    dump(root/"notes.json",{"comment":"excluded from scientific identity"})
    dump(root/"container.json",{"archive_name":"holdout-b.tar.gz","compression":"gzip","timestamp":0})

OUT.mkdir(parents=True,exist_ok=False)
make_fixture(OUT/"fixture")

targeted = [
 ("missing_file","MISSING_SOURCE","raw", ""),
 ("byte_drift","BYTE_DRIFT","raw", "sha256"),
 ("path_rename","MISSING_SOURCE","raw", ""),
 ("duplicate_path","DUPLICATE_PATH","records.json","raw_path"),
 ("duplicate_unit_id","DUPLICATE_UNIT_ID","records.json","unit_id"),
 ("version_mismatch","VERSION_MISMATCH","records.json","benchmark_version"),
 ("population_mix","POPULATION_MIX","records.json","population_id"),
 ("label_wrong_type","LABEL_CORRUPTION","records.json","task_success"),
 ("selection_omission","SELECTION_MANIFEST","selection.json","selected_unit_ids"),
 ("lineage_deletion","LINEAGE_MISSING","lineage.jsonl","unit_id"),
]
challenge = [
 ("swap_sources_without_labels","DERIVED_VALUE_MISMATCH","records.json","task_success"),
 ("coordinated_label_summary_claim","DERIVED_VALUE_MISMATCH","records.json","task_success"),
 ("coordinated_population_selection","POPULATION_MIX","records.json","population_id"),
 ("lineage_edge_swap","LINEAGE_REDIRECT","lineage.jsonl","unit_id"),
]
boundary = [
 ("empty_unit_id","SCHEMA_FIELD","records.json","unit_id"),
 ("boolean_as_integer","LABEL_CORRUPTION","records.json","task_success"),
 ("parent_traversal_path","UNSAFE_PATH","records.json","raw_path"),
]
rows=[]; k=0
for layer, ops in (("INVARIANT_TARGETED_HOLDOUT",targeted),("COMPOUND_CHALLENGE",challenge),("BOUNDARY_ADVERSARIAL",boundary)):
    for op,alarm,file_hint,field in ops:
        for i in range(N):
            k+=1
            target=f"raw/b{i:02d}.json" if file_hint=="raw" else file_hint
            rows.append({"mutation_id":f"B{k:04d}","layer":layer,"operator":op,"site":i,"target":target,"rationale":"tests a declared trust-chain invariant on a unit not used in Catalog A","precondition":"clean holdout fixture validates","expected_outcome":"FAIL","expected_alarm_class":alarm,"expected_file":target if file_hint=="raw" else file_hint,"expected_field":field,"localization_granularity":"file_and_field" if field else "file","classification":"IN_SCOPE_REQUIRED","seed":SEED})

fields=list(rows[0])
with (OUT/"CATALOG_B.csv").open("w",newline="",encoding="utf-8") as f:
    w=csv.DictWriter(f,fields); w.writeheader(); w.writerows(rows)
with (OUT/"CATALOG_B_ORACLE_FROZEN.csv").open("w",newline="",encoding="utf-8") as f:
    w=csv.DictWriter(f,["mutation_id","expected_outcome","expected_alarm_class","expected_file","expected_field","localization_granularity"]); w.writeheader(); w.writerows([{x:r[x] for x in w.fieldnames} for r in rows])

families=["record_order","lineage_order","json_key_order","ignored_notes","container_metadata"]
controls=[]; c=0
for family in families:
    for variant in range(8):
        c+=1; controls.append({"control_id":f"BC{c:03d}","family":family,"variant":variant,"expected_outcome":"PASS","identity_contract_basis":"transformation is outside declared semantic identity or canonicalized before comparison","seed":SEED+variant})
with (OUT/"BENIGN_CONTROLS_B.csv").open("w",newline="",encoding="utf-8") as f:
    w=csv.DictWriter(f,list(controls[0])); w.writeheader(); w.writerows(controls)

criteria={"protocol_version":"B-1.0","seed":SEED,"catalog_size":len(rows),"minimum_valid_mutants":300,"compound_challenge_min_fraction":0.20,"required_detection":"all IN_SCOPE_REQUIRED","required_classification":"expected alarm class present","required_localization":"expected file and declared field token present","benign_controls":len(controls),"required_false_alarms":0,"inference_ceiling":"exact performance on the declared catalog only","one_shot":True}
dump(OUT/"CATALOG_B_ACCEPTANCE_CRITERIA.json",criteria)
print(json.dumps({"catalog_b":len(rows),"compound_challenge":sum(r["layer"]=="COMPOUND_CHALLENGE" for r in rows),"compound_fraction":sum(r["layer"]=="COMPOUND_CHALLENGE" for r in rows)/len(rows),"benign_controls":len(controls)},indent=2))
