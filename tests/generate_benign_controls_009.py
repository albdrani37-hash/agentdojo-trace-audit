#!/usr/bin/env python3
"""Freeze 100 eligible benign controls without importing the verifier."""
import csv,json,sys
from pathlib import Path
OUT=Path(sys.argv[1]); OUT.mkdir(parents=True,exist_ok=False); seed=9031
families=["archive_name","compression_level","member_order","archive_timestamp","archive_permissions","root_wrapper","archive_comment","relative_invocation","optional_metadata_key_order","optional_metadata_whitespace"]
rows=[]
for family in families:
    for variant in range(10):
        rows.append({"control_id":f"N{len(rows)+1:03d}","family":family,"variant":variant,"eligible":"TRUE","predeclared_semantic_effect":"NONE","expected_alarm":"NONE","seed":seed})
with (OUT/"BENIGN_CONTROLS_009.csv").open("w",newline="",encoding="utf-8") as f:
    w=csv.DictWriter(f,list(rows[0])); w.writeheader(); w.writerows(rows)
(OUT/"BENIGN_CONTROLS_009_ACCEPTANCE.json").write_text(json.dumps({"catalog_size":100,"families":families,"seed":seed,"pass":"zero validator alarms on all eligible controls","inference":"false-alarm count on declared suite; exact two-sided 95% binomial interval"},indent=2)+"\n")
print(json.dumps({"controls":len(rows),"families":len(families)},indent=2))

