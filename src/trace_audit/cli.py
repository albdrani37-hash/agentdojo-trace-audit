from __future__ import annotations
import argparse,json,sys
from pathlib import Path
from .core import validate_bundle
from .agentdojo_adapter import reconstruct
def main():
 p=argparse.ArgumentParser(prog='trace-audit'); s=p.add_subparsers(dest='cmd',required=True)
 v=s.add_parser('validate-bundle'); v.add_argument('root',type=Path); v.add_argument('--report',type=Path)
 r=s.add_parser('reconstruct-agentdojo'); r.add_argument('source_root',type=Path); r.add_argument('output',type=Path); r.add_argument('--commit',required=True); r.add_argument('--version',required=True)
 a=p.parse_args()
 if a.cmd=='validate-bundle':
  issues=validate_bundle(a.root); payload={'status':'PASS' if not issues else 'FAIL','issues':issues}
  if a.report: a.report.write_text(json.dumps(payload,indent=2,sort_keys=True)+'\n')
  print(json.dumps(payload,sort_keys=True)); raise SystemExit(0 if not issues else 2)
 reconstruct(a.source_root,a.output,a.commit,a.version)
if __name__=='__main__': main()
