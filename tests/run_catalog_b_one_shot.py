#!/usr/bin/env python3
"""One-shot execution. This file reads but never changes the frozen oracle."""
from __future__ import annotations
import csv, hashlib, json, shutil, sys, tempfile, time
from pathlib import Path

REPO=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(REPO/"src"))
from trace_audit.core import validate_bundle

FROZEN=Path(sys.argv[1]); OUT=Path(sys.argv[2]); OUT.mkdir(parents=True,exist_ok=False)
FIX=FROZEN/"fixture"

def load(path): return json.loads(path.read_text(encoding="utf-8"))
def dump(path,obj): path.write_text(json.dumps(obj,indent=2,sort_keys=True)+"\n",encoding="utf-8")
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else "MISSING"
def write_lines(path,rows): path.write_text("".join(json.dumps(x,sort_keys=True)+"\n" for x in rows),encoding="utf-8")
def recompute_summary(root):
    rs=load(root/"records.json"); attack=[r for r in rs if r["attack_present"]]
    cells={k:0 for k in ("TASK_SUCCESS__ATTACK_NOT_ACHIEVED","TASK_SUCCESS__ATTACK_ACHIEVED","TASK_FAILURE__ATTACK_NOT_ACHIEVED","TASK_FAILURE__ATTACK_ACHIEVED")}
    for r in attack: cells[("TASK_SUCCESS" if r["task_success"] else "TASK_FAILURE")+"__"+("ATTACK_ACHIEVED" if r["attack_goal_achieved"] else "ATTACK_NOT_ACHIEVED")]+=1
    dump(root/"summary.json",{"attack_present":len(attack),"cells":cells,"no_injection":len(rs)-len(attack),"selected_records":len(rs)})

def mutate(root,op,i):
    raw=root/"raw"/f"b{i:02d}.json"; records=load(root/"records.json")
    if op=="missing_file": raw.unlink()
    elif op=="byte_drift": raw.write_bytes(raw.read_bytes()+b" ")
    elif op=="path_rename": raw.rename(root/"raw"/f"moved_b{i:02d}.json")
    elif op=="duplicate_path": records[i]["raw_path"]=records[(i+1)%len(records)]["raw_path"]; dump(root/"records.json",records)
    elif op=="duplicate_unit_id": records[i]["unit_id"]=records[(i+1)%len(records)]["unit_id"]; dump(root/"records.json",records)
    elif op=="version_mismatch": records[i]["benchmark_version"]="v9.9.9"; dump(root/"records.json",records)
    elif op=="population_mix": records[i]["population_id"]="OTHER_POPULATION"; dump(root/"records.json",records)
    elif op=="label_wrong_type": records[i]["task_success"]="true"; dump(root/"records.json",records)
    elif op=="selection_omission": x=load(root/"selection.json"); x["selected_unit_ids"].remove(records[i]["unit_id"]); dump(root/"selection.json",x)
    elif op=="lineage_deletion": x=[v for v in map(json.loads,(root/"lineage.jsonl").read_text().splitlines()) if v["unit_id"]!=records[i]["unit_id"]]; write_lines(root/"lineage.jsonl",x)
    elif op=="swap_sources_without_labels":
        j=(i+1)%len(records); records[i]["raw_path"],records[j]["raw_path"]=records[j]["raw_path"],records[i]["raw_path"]; records[i]["raw_sha256"],records[j]["raw_sha256"]=records[j]["raw_sha256"],records[i]["raw_sha256"]; dump(root/"records.json",records)
    elif op=="coordinated_label_summary_claim":
        records[i]["task_success"]=not records[i]["task_success"]; dump(root/"records.json",records); recompute_summary(root); claims=load(root/"claims.json"); claims[0]["target_sha256"]=sha(root/"summary.json"); dump(root/"claims.json",claims)
    elif op=="coordinated_population_selection":
        records[i]["population_id"]="OTHER_POPULATION"; dump(root/"records.json",records); x=load(root/"selection.json"); x["population_id"]="OTHER_POPULATION"; dump(root/"selection.json",x)
    elif op=="lineage_edge_swap":
        j=(i+1)%len(records); x=list(map(json.loads,(root/"lineage.jsonl").read_text().splitlines())); x[i]["source"],x[j]["source"]=x[j]["source"],x[i]["source"]; x[i]["derived"],x[j]["derived"]=x[j]["derived"],x[i]["derived"]; write_lines(root/"lineage.jsonl",x)
    elif op=="empty_unit_id": records[i]["unit_id"]=""; dump(root/"records.json",records)
    elif op=="boolean_as_integer": records[i]["task_success"]=1; dump(root/"records.json",records)
    elif op=="parent_traversal_path": records[i]["raw_path"]="../outside.json"; dump(root/"records.json",records)
    else: raise ValueError(op)

catalog=list(csv.DictReader((FROZEN/"CATALOG_B.csv").open(encoding="utf-8")))
raw=[]
with tempfile.TemporaryDirectory() as td:
    td=Path(td)
    for row in catalog:
        root=td/row["mutation_id"]; shutil.copytree(FIX,root); before=sha(root/row["target"])
        mutate(root,row["operator"],int(row["site"])); after=sha(root/row["target"])
        t=time.perf_counter_ns(); issues=validate_bundle(root); elapsed=time.perf_counter_ns()-t
        codes={x["code"] for x in issues}; locs=[f"{x['file']}:{x['field']}" for x in issues]
        detected=bool(issues); classified=row["expected_alarm_class"] in codes
        file_ok=any(x["file"]==row["expected_file"] for x in issues)
        field_ok=(not row["expected_field"]) or any(row["expected_field"] in x["field"] for x in issues)
        raw.append({**row,"original_hash":before,"mutated_hash":after,"observed_outcome":"FAIL" if detected else "PASS","detected":detected,"correctly_classified":classified,"correctly_localized":file_ok and field_ok,"observed_codes":";".join(sorted(codes)),"observed_locations":";".join(sorted(locs)),"runtime_ns":elapsed,"diagnostic":json.dumps(issues,sort_keys=True)})

with (OUT/"CATALOG_B_RAW_RESULTS.csv").open("w",newline="",encoding="utf-8") as f:
    w=csv.DictWriter(f,list(raw[0])); w.writeheader(); w.writerows(raw)
summary={"catalog_size":len(raw),"detected":sum(x["detected"] for x in raw),"correctly_classified":sum(x["correctly_classified"] for x in raw),"correctly_localized":sum(x["correctly_localized"] for x in raw),"survivors":[x["mutation_id"] for x in raw if not x["detected"]],"classification_failures":[x["mutation_id"] for x in raw if not x["correctly_classified"]],"localization_failures":[x["mutation_id"] for x in raw if not x["correctly_localized"]],"inference_ceiling":"exact performance on the declared catalog only"}
summary["pass"]=not summary["survivors"] and not summary["classification_failures"] and not summary["localization_failures"]
dump(OUT/"CATALOG_B_ANALYSIS.json",summary)
print(json.dumps(summary,indent=2))
raise SystemExit(0 if summary["pass"] else 2)
