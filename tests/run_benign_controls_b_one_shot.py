#!/usr/bin/env python3
from __future__ import annotations
import csv,json,random,shutil,sys,tempfile
from pathlib import Path
REPO=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(REPO/"src"))
from trace_audit.core import validate_bundle
FROZEN=Path(sys.argv[1]); OUT=Path(sys.argv[2]); OUT.mkdir(parents=True,exist_ok=False); FIX=FROZEN/"fixture"
def load(p): return json.loads(p.read_text(encoding="utf-8"))
def dump(p,o,sort=True): p.write_text(json.dumps(o,indent=2,sort_keys=sort)+"\n",encoding="utf-8")
def apply(root,row):
    v=int(row["variant"]); family=row["family"]; rnd=random.Random(int(row["seed"]))
    if family=="record_order": x=load(root/"records.json"); rnd.shuffle(x); dump(root/"records.json",x)
    elif family=="lineage_order": x=list(map(json.loads,(root/"lineage.jsonl").read_text().splitlines())); rnd.shuffle(x); (root/"lineage.jsonl").write_text("".join(json.dumps(z,sort_keys=True)+"\n" for z in x),encoding="utf-8")
    elif family=="json_key_order": x=load(root/"records.json"); dump(root/"records.json",x,sort=False)
    elif family=="ignored_notes": dump(root/"notes.json",{"variant":v,"comment":"non-scientific note"})
    elif family=="container_metadata": dump(root/"container.json",{"archive_name":f"variant-{v}.zip","compression":["store","deflate"][v%2],"timestamp":v,"comment":"outside content identity"})
    else: raise ValueError(family)
rows=list(csv.DictReader((FROZEN/"BENIGN_CONTROLS_B.csv").open(encoding="utf-8"))); results=[]
with tempfile.TemporaryDirectory() as td:
    td=Path(td)
    for row in rows:
        root=td/row["control_id"]; shutil.copytree(FIX,root); apply(root,row); issues=validate_bundle(root)
        results.append({**row,"observed_outcome":"PASS" if not issues else "FAIL","false_alarm":bool(issues),"diagnostic":json.dumps(issues,sort_keys=True)})
with (OUT/"BENIGN_CONTROLS_B_RAW_RESULTS.csv").open("w",newline="",encoding="utf-8") as f:
    w=csv.DictWriter(f,list(results[0])); w.writeheader(); w.writerows(results)
summary={"controls":len(results),"families":len(set(x["family"] for x in results)),"false_alarms":sum(x["false_alarm"] for x in results),"failed_controls":[x["control_id"] for x in results if x["false_alarm"]],"claim":"false alarms on the declared benign-control suite only"}; summary["pass"]=summary["false_alarms"]==0
dump(OUT/"BENIGN_CONTROLS_B_ANALYSIS.json",summary); print(json.dumps(summary,indent=2)); raise SystemExit(0 if summary["pass"] else 2)
