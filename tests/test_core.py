from __future__ import annotations
import copy,json,shutil,tempfile,unittest
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from trace_audit.core import validate_bundle
FIX=Path(__file__).resolve().parents[1]/"examples/synthetic_fixture"
class CoreTests(unittest.TestCase):
 def run_case(self,fn=None):
  with tempfile.TemporaryDirectory() as td:
   p=Path(td)/"f"; shutil.copytree(FIX,p)
   if fn: fn(p)
   return validate_bundle(p)
 def test_clean(self): self.assertEqual(self.run_case(),[])
 def test_missing(self): self.assertTrue(self.run_case(lambda p:(p/"raw/example.json").unlink()))
 def test_drift(self): self.assertTrue(self.run_case(lambda p:(p/"raw/example.json").write_text("{}")))
 def test_denominator(self):
  def f(p): x=json.loads((p/"summary.json").read_text()); x["attack_present"]=2; (p/"summary.json").write_text(json.dumps(x))
  self.assertTrue(self.run_case(f))
 def test_version(self):
  def f(p): x=json.loads((p/"records.json").read_text()); x[0]["benchmark_version"]="bad"; (p/"records.json").write_text(json.dumps(x))
  self.assertTrue(self.run_case(f))
 def test_population(self):
  def f(p): x=json.loads((p/"records.json").read_text()); x[0]["population_id"]="other"; (p/"records.json").write_text(json.dumps(x))
  self.assertTrue(self.run_case(f))
 def test_duplicate_identity(self):
  def f(p): x=json.loads((p/"records.json").read_text()); x.append(dict(x[0])); (p/"records.json").write_text(json.dumps(x))
  self.assertTrue(self.run_case(f))
 def test_order_invariance(self):
  def f(p): x=json.loads((p/"records.json").read_text()); x.reverse(); (p/"records.json").write_text(json.dumps(x))
  self.assertEqual(self.run_case(f),[])
if __name__=="__main__": unittest.main()
