#!/usr/bin/env python3
import csv,hashlib,json,sys
from pathlib import Path
OUT=Path(sys.argv[1]); OUT.mkdir(parents=True,exist_ok=False); rows=[]
for family in ('optional_metadata_line_endings','unicode_outer_wrapper'):
    for v in range(10): rows.append({'control_id':f'S{len(rows)+1:03d}','family':family,'variant':v,'eligible':'TRUE','expected_alarm':'NONE','seed':9041})
with (OUT/'BENIGN_CONTROLS_SUPPLEMENT.csv').open('w',newline='',encoding='utf-8') as f: w=csv.DictWriter(f,list(rows[0])); w.writeheader(); w.writerows(rows)
(OUT/'BENIGN_CONTROLS_SUPPLEMENT_ACCEPTANCE.json').write_text(json.dumps({'catalog_size':20,'pass':'zero alarms','seed':9041},indent=2)+'\n')
print(json.dumps({'controls':20},indent=2))
