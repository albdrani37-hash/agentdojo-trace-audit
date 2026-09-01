#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv,hashlib,json,platform,resource,statistics,time
from pathlib import Path
from trace_audit.agentdojo_adapter import GROUPS,REQ,selected

def q(values,p):
    x=sorted(values); k=(len(x)-1)*p; a=int(k); b=min(a+1,len(x)-1); return x[a]+(x[b]-x[a])*(k-a)
def timed(fn):
    c0=time.process_time(); t0=time.perf_counter(); value=fn(); return value,time.perf_counter()-t0,time.process_time()-c0,resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
def main():
    parser=argparse.ArgumentParser(); parser.add_argument('source',type=Path); parser.add_argument('out',type=Path); x=parser.parse_args(); x.out.mkdir(parents=True,exist_ok=False)
    rows=[]; paths=[]
    # Warm-up discovery.
    for g in GROUPS: paths.extend(sorted((x.source/'runs'/g).rglob('*.json')))
    for rep in range(10):
        def discover():
            z=[]
            for g in GROUPS: z.extend(sorted((x.source/'runs'/g).rglob('*.json')))
            return z
        found,wall,cpu,rss=timed(discover); rows.append({'stage':'tree_discovery','fraction':1.0,'records':len(found),'rep':rep+1,'wall_s':wall,'cpu_s':cpu,'peak_rss_kib':rss,'records_per_s':len(found)/wall})
        def hash_all():
            return [hashlib.sha256(p.read_bytes()).digest() for p in found]
        _,wall,cpu,rss=timed(hash_all); rows.append({'stage':'content_hashing','fraction':1.0,'records':len(found),'rep':rep+1,'wall_s':wall,'cpu_s':cpu,'peak_rss_kib':rss,'records_per_s':len(found)/wall})
    # Discover candidates once for scaling; no repeated full-tree scan per size.
    parsed=[]
    for p in paths:
        obj=json.loads(p.read_text(encoding='utf-8'))
        if selected(obj,'v1.2.1'): parsed.append((p,obj))
    for frac in (.1,.25,.5,.75,1.0):
        n=round(len(parsed)*frac); subset=parsed[:n]
        for rep in range(10):
            def transform():
                out=[]
                for p,obj in subset:
                    rel=p.relative_to(x.source).as_posix(); attack=obj.get('injection_task_id') is not None
                    out.append((rel,bool(obj['utility']),attack,bool(obj['security']) if attack else None))
                return out
            out,wall,cpu,rss=timed(transform); rows.append({'stage':'retained_record_transformation','fraction':frac,'records':len(out),'rep':rep+1,'wall_s':wall,'cpu_s':cpu,'peak_rss_kib':rss,'records_per_s':len(out)/wall})
    with (x.out/'PERFORMANCE_RAW_009.csv').open('w',newline='',encoding='utf-8') as f: w=csv.DictWriter(f,list(rows[0])); w.writeheader(); w.writerows(rows)
    summary=[]
    for key in sorted({(r['stage'],r['fraction'],r['records']) for r in rows}):
        vals=[r for r in rows if (r['stage'],r['fraction'],r['records'])==key]; ws=[r['wall_s'] for r in vals]; rates=[r['records_per_s'] for r in vals]
        summary.append({'stage':key[0],'fraction':key[1],'records':key[2],'n':len(vals),'median_wall_s':statistics.median(ws),'iqr_wall_s':q(ws,.75)-q(ws,.25),'min_wall_s':min(ws),'max_wall_s':max(ws),'median_records_per_s':statistics.median(rates),'max_peak_rss_kib':max(r['peak_rss_kib'] for r in vals)})
    (x.out/'PERFORMANCE_SUMMARY_009.json').write_text(json.dumps({'environment':{'python':platform.python_version(),'platform':platform.platform(),'processor':platform.processor()},'design':'full discovery and hashing measured separately; retained-record scaling reuses one discovery result','summaries':summary},indent=2,sort_keys=True)+'\n')
if __name__=='__main__': main()
