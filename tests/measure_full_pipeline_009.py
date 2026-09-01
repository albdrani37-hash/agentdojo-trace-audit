#!/usr/bin/env python3
import csv,json,resource,statistics,sys,tempfile,time
from pathlib import Path
from trace_audit.agentdojo_adapter import reconstruct
from trace_audit.stages import validate_result
SRC=Path(sys.argv[1]); OUT=Path(sys.argv[2]); OUT.mkdir(parents=True,exist_ok=True)
rows=[]
with tempfile.TemporaryDirectory() as td:
    td=Path(td)
    # one unreported warm-up
    reconstruct(SRC,td/'warm','089ed468cf3ed0322acc66b0211f26d9d90dbf60','v1.2.1',1.0)
    for rep in range(1,11):
        result=td/f'r{rep}'; t=time.perf_counter(); c=time.process_time(); reconstruct(SRC,result,'089ed468cf3ed0322acc66b0211f26d9d90dbf60','v1.2.1',1.0); wall=time.perf_counter()-t; cpu=time.process_time()-c
        rows.append({'stage':'full_reconstruction','rep':rep,'records':11624,'wall_s':wall,'cpu_s':cpu,'peak_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'records_per_s':11624/wall})
        t=time.perf_counter(); c=time.process_time(); validate_result(SRC,result,td/f'v{rep}.json'); wall=time.perf_counter()-t; cpu=time.process_time()-c
        rows.append({'stage':'validation_and_receipt','rep':rep,'records':11624,'wall_s':wall,'cpu_s':cpu,'peak_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'records_per_s':11624/wall})
with (OUT/'FULL_PIPELINE_RAW_009.csv').open('w',newline='',encoding='utf-8') as f: w=csv.DictWriter(f,list(rows[0])); w.writeheader(); w.writerows(rows)
summ={}
for stage in sorted(set(r['stage'] for r in rows)):
    x=[r for r in rows if r['stage']==stage]; ws=sorted(r['wall_s'] for r in x)
    summ[stage]={'n':len(x),'median_wall_s':statistics.median(ws),'iqr_wall_s':statistics.median(ws[5:])-statistics.median(ws[:5]),'min_wall_s':min(ws),'max_wall_s':max(ws),'median_records_per_s':statistics.median(r['records_per_s'] for r in x),'max_peak_rss_kib':max(r['peak_rss_kib'] for r in x)}
(OUT/'FULL_PIPELINE_SUMMARY_009.json').write_text(json.dumps(summ,indent=2,sort_keys=True)+'\n')
print(json.dumps(summ,indent=2))
