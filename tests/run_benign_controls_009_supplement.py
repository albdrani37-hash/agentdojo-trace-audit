#!/usr/bin/env python3
"""One-shot supplementary benign controls: optional metadata line endings and wrapper Unicode."""
import csv,json,shutil,sys,tempfile,unicodedata,zipfile
from pathlib import Path
REPO=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(REPO/'src')); from trace_audit.core import validate_bundle
CAT=Path(sys.argv[1]); FIX=Path(sys.argv[2]); OUT=Path(sys.argv[3]); OUT.mkdir(parents=True,exist_ok=False)
rows=list(csv.DictReader(CAT.open(encoding='utf-8'))); results=[]
with tempfile.TemporaryDirectory() as td:
    td=Path(td)
    for row in rows:
        w=td/row['control_id']; shutil.copytree(FIX,w/'fixture'); target=w/'fixture'
        if row['family']=='optional_metadata_line_endings':
            # notes.json is declared outside scientific identity and ignored by the validator.
            b=(target/'notes.json').read_bytes().replace(b'\n',b'\r\n'); (target/'notes.json').write_bytes(b)
        else:
            form='NFC' if int(row['variant'])%2==0 else 'NFD'; wrapper=unicodedata.normalize(form,'caf\u00e9')+str(row['variant']); zp=w/'u.zip'
            with zipfile.ZipFile(zp,'w') as z:
                for p in sorted(target.rglob('*')):
                    if p.is_file(): z.write(p,(Path(wrapper)/p.relative_to(target)).as_posix())
            shutil.rmtree(target); ex=w/'x'; z=zipfile.ZipFile(zp); z.extractall(ex); z.close(); target=ex/wrapper
        issues=validate_bundle(target); results.append({**row,'false_alarm':bool(issues),'diagnostic':json.dumps(issues,sort_keys=True)})
with (OUT/'BENIGN_CONTROLS_SUPPLEMENT_RAW.csv').open('w',newline='',encoding='utf-8') as f: w=csv.DictWriter(f,list(results[0])); w.writeheader(); w.writerows(results)
s={'controls':len(results),'false_alarms':sum(x['false_alarm'] for x in results),'pass':not any(x['false_alarm'] for x in results),'families':sorted(set(x['family'] for x in results)),'scope':'optional metadata line endings and outer wrapper Unicode only'}
(OUT/'BENIGN_CONTROLS_SUPPLEMENT_ANALYSIS.json').write_text(json.dumps(s,indent=2,sort_keys=True)+'\n'); print(json.dumps(s,indent=2)); raise SystemExit(0 if s['pass'] else 2)
