import copy
import unittest
from audit import audit, digest

def sample(schema="flat-v1"):
    raw = [{"id": "a", "status": "included", "payload": {"success": False, "latency": 120}},
           {"id": "b", "status": "excluded", "payload": {"success": True}}]
    doc = {"schema": schema,
           "derived": [{"trace_id": "a", "source_sha256": digest(raw[0]["payload"])}],
           "claim": {"raw_total": 2, "included": 1, "excluded": 1}}
    if schema == "flat-v1":
        doc["records"] = raw
    else:
        doc["data"] = {"entries": raw}
    return doc

class EvidenceAuditTests(unittest.TestCase):
    def test_flat_pass(self): self.assertEqual(audit(sample())["status"], "PASS")
    def test_wrapped_pass(self): self.assertEqual(audit(sample("wrapped-v1"))["status"], "PASS")
    def test_cross_schema_counts(self):
        self.assertEqual(audit(sample())["counts"], audit(sample("wrapped-v1"))["counts"])
    def test_unrecognized_schema(self):
        x = sample(); x["schema"] = "random"
        self.assertIn("UNSUPPORTED_SCHEMA", [p["code"] for p in audit(x)["issues"]])
    def test_missing_derived(self):
        x = sample(); x["derived"] = []
        self.assertIn("MISSING_DERIVED", [p["code"] for p in audit(x)["issues"]])
    def test_orphan_derived(self):
        x = sample(); x["derived"].append({"trace_id": "unknown", "source_sha256": "00"})
        self.assertIn("ORPHAN_DERIVED", [p["code"] for p in audit(x)["issues"]])
    def test_fingerprint_tampering(self):
        x = sample(); x["records"][0]["payload"]["latency"] = 121
        self.assertIn("HASH_MISMATCH", [p["code"] for p in audit(x)["issues"]])
    def test_duplicate_raw(self):
        x = sample(); x["records"].append(copy.deepcopy(x["records"][0]))
        self.assertIn("DUPLICATE_RAW_ID", [p["code"] for p in audit(x)["issues"]])
    def test_duplicate_derived(self):
        x = sample(); x["derived"].append(copy.deepcopy(x["derived"][0]))
        self.assertIn("DUPLICATE_DERIVED_ID", [p["code"] for p in audit(x)["issues"]])
    def test_excluded_in_derived(self):
        x = sample(); x["derived"].append({"trace_id": "b", "source_sha256": digest(x["records"][1]["payload"])})
        self.assertIn("EXCLUDED_IN_DERIVED", [p["code"] for p in audit(x)["issues"]])
    def test_denominator_mismatch(self):
        x = sample(); x["claim"]["included"] = 2
        self.assertIn("CLAIM_COUNT_MISMATCH", [p["code"] for p in audit(x)["issues"]])
    def test_missing_metadata(self):
        x = sample(); del x["claim"]
        self.assertIn("MISSING_SECTIONS", [p["code"] for p in audit(x)["issues"]])
    def test_invalid_status(self):
        x = sample(); x["records"][0]["status"] = "unknown"
        self.assertIn("INVALID_SELECTION", [p["code"] for p in audit(x)["issues"]])
    def test_no_boolean_counts(self):
        x = sample(); x["claim"]["raw_total"] = True
        self.assertIn("CLAIM_COUNT_MISMATCH", [p["code"] for p in audit(x)["issues"]])
    def test_deterministic_report(self):
        x = sample(); self.assertEqual(audit(x), audit(x))

if __name__ == "__main__":
    unittest.main()
