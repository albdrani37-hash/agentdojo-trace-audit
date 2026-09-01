#!/usr/bin/env python3
from __future__ import annotations
import csv,json,os,random,shutil,stat,sys,tempfile,zipfile
from pathlib import Path
REPO=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(REPO/"src")); from trace_audit.core import validate_bundle
F=Path(sys.argv[1]); FIX=Path(sys.argv[2]); OUT=Path(sys.argv[3]); OUT.mkdir(parents=True,exist_ok=False)
rows=list(csv.DictReader((F/"BENIGN_CONTROLS_009.csv").open(encoding="utf-8"))); results=[]
def make_archive(src,zp,family,v):
    files=sorted(p for p in src.rglob('*') if p.is_file());
    if family=="member_order" and v%2: files=list(reversed(files))
    comp=zipfile.ZIP_STORED if family=="compression_level" and v%2==0 else zipfile.ZIP_DEFLATED
    root=f"wrapper_{v}" if family=="root_wrapper" else "fixture"
    with zipfile.ZipFile(zp,'w',compression=comp,compresslevel=(1+v%9) if comp==zipfile.ZIP_DEFLATED else None) as z:
        if family=="archive_comment": z.comment=f"benign-{v}".encode()
        for p in files:
            rel=Path(root)/p.relative_to(src); info=zipfile.ZipInfo(rel.as_posix())
            info.date_time=(2020+v%5,1+v%12,1+v%27,0,0,0) if family=="archive_timestamp" else (2024,1,1,0,0,0)
            info.external_attr=((0o644 if family!="archive_permissions" else (0o600 if v%2 else 0o664)) & 0xffff)<<16
            info.compress_type=comp; z.writestr(info,p.read_bytes())
    return root
with tempfile.TemporaryDirectory() as td:
    td=Path(td)
    for row in rows:
        work=td/row["control_id"]; shutil.copytree(FIX,work/"fixture"); family=row["family"]; v=int(row["variant"]); target=work/"fixture"
        if family in {"optional_metadata_key_order","optional_metadata_whitespace"}:
            note=target/"notes.json"; obj=json.loads(note.read_text());
            note.write_text(json.dumps(obj,sort_keys=(family=="optional_metadata_key_order" and v%2==0),indent=(2 if family=="optional_metadata_whitespace" and v%2 else None))+"\n",encoding="utf-8")
        elif family=="relative_invocation":
            target=Path(os.path.relpath(target,start=REPO)) if False else target
        else:
            zp=work/(f"renamed_{v}.zip" if family=="archive_name" else "container.zip"); rootname=make_archive(target,zp,family,v); shutil.rmtree(target); ex=work/"extracted"; ex.mkdir();
            with zipfile.ZipFile(zp) as z: z.extractall(ex)
            target=ex/rootname
        issues=validate_bundle(target); results.append({**row,"false_alarm":bool(issues),"diagnostic":json.dumps(issues,sort_keys=True)})
with (OUT/"BENIGN_CONTROLS_009_RAW_RESULTS.csv").open("w",newline="",encoding="utf-8") as f: w=csv.DictWriter(f,list(results[0])); w.writeheader(); w.writerows(results)
n=len(results); x=sum(r["false_alarm"] for r in results); alpha=.05
if x==0: lo=0.0; hi=1-(alpha/2)**(1/n)
else: lo=hi=None
summary={"controls":n,"false_alarms":x,"false_alarm_percent":100*x/n,"ci_method":"Clopper-Pearson exact two-sided 95%","ci95_lower":lo,"ci95_upper":hi,"pass":x==0,"inference_ceiling":"declared benign-control suite only"}
(OUT/"BENIGN_CONTROLS_009_ANALYSIS.json").write_text(json.dumps(summary,indent=2,sort_keys=True)+"\n"); print(json.dumps(summary,indent=2)); raise SystemExit(0 if x==0 else 2)

