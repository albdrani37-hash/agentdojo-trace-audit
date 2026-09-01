from __future__ import annotations
import argparse,hashlib,json,tarfile
from pathlib import Path,PurePosixPath
from .agentdojo_adapter import reconstruct
COMMIT='089ed468cf3ed0322acc66b0211f26d9d90dbf60'; VERSION='v1.2.1'; CONTENT_ID='6a901ddfede209b3da16b3c00e0ad212e098d66618668375e6adcaf50cc830cd'
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1<<20),b''): h.update(b)
 return h.hexdigest()
def emit(p,o): Path(p).parent.mkdir(parents=True,exist_ok=True); Path(p).write_text(json.dumps(o,indent=2,sort_keys=True)+'\n')
def safe_extract(a,d):
 with tarfile.open(a) as t:
  ms=t.getmembers()
  for m in ms:
   q=PurePosixPath(m.name)
   if q.is_absolute() or '..' in q.parts or m.issym() or m.islnk(): raise SystemExit(f'unsafe archive member: {m.name}')
  t.extractall(d,members=ms,filter='data')
def tree_rows(root): return [('file',p.relative_to(root).as_posix(),p.stat().st_size,sha(p)) for p in sorted(root.rglob('*'),key=lambda x:x.relative_to(root).as_posix()) if p.is_file()]
def tree_id(rows): return hashlib.sha256(''.join(f'{k}\0{p}\0{n}\0{h}\n' for k,p,n,h in rows).encode()).hexdigest()
def prepare(a):
 if not a.archive.is_file(): raise SystemExit('missing source archive')
 a.work.mkdir(parents=True,exist_ok=False); safe_extract(a.archive,a.work/'source')
 roots=[p.parent for p in (a.work/'source').rglob('runs') if (p.parent/'pyproject.toml').is_file()]
 if len(roots)!=1: raise SystemExit('source root ambiguous')
 rows=tree_rows(roots[0]); observed=tree_id(rows)
 if observed!=CONTENT_ID: raise SystemExit(f'source content drift: expected {CONTENT_ID}; observed {observed}')
 emit(a.work/'prepared_source.json',{'source_root':roots[0].relative_to(a.work).as_posix(),'source_container_sha256':sha(a.archive),'source_content_id':observed,'source_commit':COMMIT,'benchmark_version':VERSION,'files':len(rows)}); print(roots[0])
def validate_result(source,result,report):
 s=json.loads((result/'summary.json').read_text()); rs=json.loads((result/'records.json').read_text()); issues=[]
 if len(rs)!=s['selected_records']: issues.append('selected_records')
 if s['attack_present']+s['no_injection']!=len(rs): issues.append('denominator_partition')
 if sum(s['cells'].values())!=s['attack_present']: issues.append('cell_partition')
 for r in rs:
  p=source/r['raw_path']
  if not p.is_file(): issues.append('missing:'+r['raw_path'])
  elif sha(p)!=r['raw_sha256']: issues.append('hash:'+r['raw_path'])
 emit(report,{'status':'PASS' if not issues else 'FAIL','issues':issues,'selected_records':len(rs),'raw_to_derived':f'{len(rs)-sum(x.startswith(("missing:","hash:")) for x in issues)}/{len(rs)}'})
 if issues: raise SystemExit(2)
def render(result,report): report.write_text('# Reconstruction report\n\n'+json.dumps(json.loads((result/'summary.json').read_text()),indent=2,sort_keys=True)+'\n')
def verify(result,report):
 s=json.loads((result/'summary.json').read_text()); ok=s['selected_records']==11624 and s['attack_present']==11236 and s['no_injection']==388 and s['cells']=={'TASK_FAILURE__ATTACK_ACHIEVED':416,'TASK_FAILURE__ATTACK_NOT_ACHIEVED':3727,'TASK_SUCCESS__ATTACK_ACHIEVED':200,'TASK_SUCCESS__ATTACK_NOT_ACHIEVED':6893}
 emit(report,{'status':'PASS' if ok else 'FAIL','scope':'regression receipt; expected values are not inputs to reconstruction','external_replicability':'NOT_ESTABLISHED'})
 if not ok: raise SystemExit(2)
def main():
 p=argparse.ArgumentParser(); s=p.add_subparsers(dest='cmd',required=True)
 q=s.add_parser('prepare'); q.add_argument('archive',type=Path); q.add_argument('work',type=Path)
 q=s.add_parser('analyze'); q.add_argument('source',type=Path); q.add_argument('output',type=Path); q.add_argument('--fraction',type=float,default=1.0)
 q=s.add_parser('validate'); q.add_argument('source',type=Path); q.add_argument('result',type=Path); q.add_argument('report',type=Path)
 q=s.add_parser('render'); q.add_argument('result',type=Path); q.add_argument('report',type=Path)
 q=s.add_parser('verify'); q.add_argument('result',type=Path); q.add_argument('report',type=Path)
 a=p.parse_args()
 if a.cmd=='prepare': prepare(a)
 elif a.cmd=='analyze': reconstruct(a.source,a.output,COMMIT,VERSION,a.fraction)
 elif a.cmd=='validate': validate_result(a.source,a.result,a.report)
 elif a.cmd=='render': render(a.result,a.report)
 else: verify(a.result,a.report)
if __name__=='__main__': main()
