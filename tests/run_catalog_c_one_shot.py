#!/usr/bin/env python3
from __future__ import annotations
import csv,hashlib,json,shutil,sys,tempfile
from pathlib import Path
REPO=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(REPO/"src")); from trace_audit.core import validate_bundle
F=Path(sys.argv[1]); OUT=Path(sys.argv[2]); OUT.mkdir(parents=True,exist_ok=False); FIX=F/"fixture"
def load(p): return json.loads(p.read_text(encoding="utf-8"))
def dump(p,o): p.write_text(json.dumps(o,indent=2,sort_keys=True)+"\n",encoding="utf-8")
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def mutate(root,op,i):
 rs=load(root/"records.json"); raw=root/"raw"/f"c{i:02d}.json"
 if op=="invalid_raw_json": raw.write_text("{",encoding="utf-8")
 elif op=="manifest_entry_omission": x=load(root/"source_manifest.json"); x["files"]=[m for m in x["files"] if m["path"]!=rs[i]["raw_path"]]; dump(root/"source_manifest.json",x)
 elif op=="manifest_duplicate_path": x=load(root/"source_manifest.json"); x["files"].append(dict(x["files"][i])); dump(root/"source_manifest.json",x)
 elif op=="record_hash_blank": rs[i]["raw_sha256"]=""; dump(root/"records.json",rs)
 elif op=="source_commit_blank": rs[i]["source_commit"]=""; dump(root/"records.json",rs)
 elif op=="attack_present_integer": rs[i]["attack_present"]=1; dump(root/"records.json",rs)
 elif op=="attack_goal_null": rs[i]["attack_goal_achieved"]=None; dump(root/"records.json",rs)
 elif op=="selection_duplicate_id": x=load(root/"selection.json"); x["selected_unit_ids"].append(rs[i]["unit_id"]); dump(root/"selection.json",x)
 elif op=="raw_manifest_changed_record_stale":
  raw.write_bytes(raw.read_bytes()+b" "); x=load(root/"source_manifest.json"); m=next(m for m in x["files"] if m["path"]==rs[i]["raw_path"]); m["bytes"]=raw.stat().st_size; m["sha256"]=sha(raw); dump(root/"source_manifest.json",x)
 elif op=="summary_claim_coordinated_drift":
  x=load(root/"summary.json"); x["selected_records"]+=1; dump(root/"summary.json",x); c=load(root/"claims.json"); c[0]["target_sha256"]=sha(root/"summary.json"); dump(root/"claims.json",c)
 elif op=="claim_redirect_existing_bad_pointer": c=load(root/"claims.json"); c[0]["target"]="records.json#/not_a_field"; c[0]["target_sha256"]=sha(root/"records.json"); dump(root/"claims.json",c)
 else: raise ValueError(op)
rows=list(csv.DictReader((F/"CATALOG_C.csv").open(encoding="utf-8"))); results=[]
with tempfile.TemporaryDirectory() as td:
 td=Path(td)
 for row in rows:
  root=td/row["mutation_id"]; shutil.copytree(FIX,root); mutate(root,row["operator"],int(row["site"])); issues=validate_bundle(root); codes={x["code"] for x in issues}; detected=bool(issues); classified=row["expected_alarm_class"] in codes; localized=any(x["file"]==row["expected_file"] and (not row["expected_field"] or row["expected_field"] in x["field"]) for x in issues); results.append({**row,"detected":detected,"correctly_classified":classified,"correctly_localized":localized,"diagnostic":json.dumps(issues,sort_keys=True)})
with (OUT/"CATALOG_C_RAW_RESULTS.csv").open("w",newline="",encoding="utf-8") as f: w=csv.DictWriter(f,list(results[0])); w.writeheader(); w.writerows(results)
summary={"catalog_size":len(results),"detected":sum(x["detected"] for x in results),"correctly_classified":sum(x["correctly_classified"] for x in results),"correctly_localized":sum(x["correctly_localized"] for x in results),"survivors":[x["mutation_id"] for x in results if not x["detected"]],"classification_failures":[x["mutation_id"] for x in results if not x["correctly_classified"]],"localization_failures":[x["mutation_id"] for x in results if not x["correctly_localized"]],"inference_ceiling":"exact performance on declared Catalog C only"}; summary["pass"]=not summary["survivors"] and not summary["classification_failures"] and not summary["localization_failures"]; dump(OUT/"CATALOG_C_ANALYSIS.json",summary); print(json.dumps(summary,indent=2)); raise SystemExit(0 if summary["pass"] else 2)
