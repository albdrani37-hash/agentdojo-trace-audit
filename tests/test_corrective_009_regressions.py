from pathlib import Path
import json, shutil, tempfile, unittest
from trace_audit.core import validate_bundle

def _fixture():
    return Path(__file__).parents[1] / "examples" / "synthetic_fixture"

class Corrective009Regressions(unittest.TestCase):
    def test_validator_has_no_catalog_or_oracle_dependency(self):
        source=(Path(__file__).parents[1]/"src"/"trace_audit"/"core.py").read_text(encoding="utf-8").lower()
        self.assertNotIn("catalog_b",source); self.assertNotIn("catalog_c",source); self.assertNotIn("oracle",source)

    def test_lineage_diagnostics_include_unit_id_locator(self):
        with tempfile.TemporaryDirectory() as td:
            target=Path(td)/"x"; shutil.copytree(_fixture(),target)
            rows=(target/"lineage.jsonl").read_text(encoding="utf-8").splitlines(); uid=json.loads(rows[0])["unit_id"]
            (target/"lineage.jsonl").write_text("\n".join(rows[1:])+"\n",encoding="utf-8")
            issues=validate_bundle(target)
            self.assertTrue(any(i["code"]=="LINEAGE_MISSING" and uid in i["field"] for i in issues))

    def test_boolean_type_location_is_semantically_specific(self):
        with tempfile.TemporaryDirectory() as td:
            target=Path(td)/"x"; shutil.copytree(_fixture(),target)
            records=json.loads((target/"records.json").read_text()); records[0]["task_success"]=1
            (target/"records.json").write_text(json.dumps(records),encoding="utf-8")
            issues=validate_bundle(target)
            self.assertTrue(any(i["code"]=="LABEL_CORRUPTION" and i["field"].endswith(".task_success") for i in issues))

if __name__=="__main__": unittest.main()
