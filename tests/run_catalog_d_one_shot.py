#!/usr/bin/env python3
from __future__ import annotations
import csv,hashlib,json,shutil,sys,tempfile,time
from pathlib import Path
REPO=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(REPO/"src")); from trace_audit.core import validate_bundle
F=Path(sys.argv[1]); OUT=Path(sys.argv[2]); OUT.mkdir(parents=True,exist_ok=False); FIX=F/"fixture"
def load(p): return json.loads(p.read_text(encoding="utf-8"))
def dump(p,o): p.write_text(json.dumps(o,indent=2,sort_keys=True)+"\n",encoding="utf-8")
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def mutate(root,op,i):
    rs=load(root/"records.json"); uid=f"d{i:02d}"; raw=root/"raw"/f"{uid}.json"
    if op=="missing_source": raw.unlink()
    elif op=="byte_drift": raw.write_bytes(raw.read_bytes()+b" ")
    elif op=="wrong_version": rs[i]["source_commit"]="other"; dump(root/"records.json",rs)
    elif op=="boolean_type": rs[i]["task_success"]=1; dump(root/"records.json",rs)
    elif op=="lineage_delete":
        lines=[json.loads(x) for x in (root/"lineage.jsonl").read_text().splitlines()]; lines=[x for x in lines if x["unit_id"]!=uid]; (root/"lineage.jsonl").write_text("".join(json.dumps(x,sort_keys=True)+"\n" for x in lines))
    elif op=="lineage_redirect":
        lines=[json.loads(x) for x in (root/"lineage.jsonl").read_text().splitlines()]; e=next(x for x in lines if x["unit_id"]==uid); e["source"]=rs[(i+7)%len(rs)]["raw_path"]; (root/"lineage.jsonl").write_text("".join(json.dumps(x,sort_keys=True)+"\n" for x in lines))
    elif op=="coordinated_raw_manifest_change":
        raw.write_bytes(raw.read_bytes()+b" "); m=load(root/"source_manifest.json"); x=next(x for x in m["files"] if x["path"]==rs[i]["raw_path"]); x["bytes"]=raw.stat().st_size; x["sha256"]=sha(raw); dump(root/"source_manifest.json",m)
    elif op=="swap_two_sources_with_manifest_update":
        j=(i+11)%len(rs); p2=root/rs[j]["raw_path"]; a,b=raw.read_bytes(),p2.read_bytes(); raw.write_bytes(b); p2.write_bytes(a); m=load(root/"source_manifest.json");
        for x in m["files"]:
            p=root/x["path"]; x["bytes"]=p.stat().st_size; x["sha256"]=sha(p)
        dump(root/"source_manifest.json",m)
    elif op=="summary_claim_coordinated_drift":
        s=load(root/"summary.json"); s["selected_records"]+=1; dump(root/"summary.json",s); c=load(root/"claims.json"); c[0]["target_sha256"]=sha(root/"summary.json"); dump(root/"claims.json",c)
    elif op=="claim_bad_pointer_valid_hash":
        c=load(root/"claims.json"); c[0]["target"]="records.json#/9999/unit_id"; c[0]["target_sha256"]=sha(root/"records.json"); dump(root/"claims.json",c)
    elif op=="delete_add_constant_count":
        rs[i]["unit_id"]=f"d_new_{i:02d}"; dump(root/"records.json",rs)
    elif op=="cross_field_inconsistency":
        rs[i]["attack_present"]=False; rs[i]["attack_goal_achieved"]=True; dump(root/"records.json",rs)
    else: raise ValueError(op)
def locmatch(issue,row):
    if issue["file"]!=row["expected_file"]: return False
    exp=row["expected_field"]; got=issue["field"]
    if not exp: return True
    if exp.startswith("unit_id="): return exp==got
    if exp in {"task_success","source_commit","selected_records","selected_unit_ids","target","attack_present","sha256"}: return got==exp or got.endswith("."+exp) or exp in got
    return exp==got or exp in got
rows=list(csv.DictReader((F/"CATALOG_D.csv").open(encoding="utf-8"))); results=[]
with tempfile.TemporaryDirectory() as td:
    td=Path(td)
    for row in rows:
        root=td/row["mutation_id"]; shutil.copytree(FIX,root); mutate(root,row["operator"],int(row["site"])); t=time.perf_counter_ns(); issues=validate_bundle(root); runtime=time.perf_counter_ns()-t
        codes={x["code"] for x in issues}; results.append({**row,"detected":bool(issues),"correctly_classified":row["expected_alarm_class"] in codes,"correctly_localized":any(x["code"]==row["expected_alarm_class"] and locmatch(x,row) for x in issues),"observed_codes":";".join(sorted(codes)),"runtime_ns":runtime,"diagnostic":json.dumps(issues,sort_keys=True)})
with (OUT/"CATALOG_D_RAW_RESULTS.csv").open("w",newline="",encoding="utf-8") as f: w=csv.DictWriter(f,list(results[0])); w.writeheader(); w.writerows(results)
summary={"catalog_size":len(results),"detected":sum(x["detected"] for x in results),"classified":sum(x["correctly_classified"] for x in results),"localized":sum(x["correctly_localized"] for x in results),"survivors":[x["mutation_id"] for x in results if not x["detected"]],"classification_failures":[x["mutation_id"] for x in results if not x["correctly_classified"]],"localization_failures":[x["mutation_id"] for x in results if not x["correctly_localized"]],"one_shot":True,"criteria_changed_after_run":False,"inference_ceiling":"exact performance on declared Catalog D only"}; summary["pass"]=not summary["survivors"] and not summary["classification_failures"] and not summary["localization_failures"]; dump(OUT/"CATALOG_D_ANALYSIS.json",summary); print(json.dumps(summary,indent=2)); raise SystemExit(0 if summary["pass"] else 2)

