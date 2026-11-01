"""Synthetic provenance and population auditor, not an authenticity or safety guarantee."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

SCHEMAS = {"flat-v1", "wrapped-v1"}
MAX_RECORDS = 10000

def digest(payload: Any) -> str:
    data = json.dumps(payload, sort_keys=True, ensure_ascii=False,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")
    return hashlib.sha256(data).hexdigest()

def issue(items: list[dict], code: str, identifier: str = "", detail: str = "") -> None:
    items.append({"code": code, "item": identifier, "detail": detail})

def audit(document: Any) -> dict[str, Any]:
    problems: list[dict] = []
    if not isinstance(document, dict):
        return {"status": "HOLD", "issues": [{"code": "INVALID_ROOT", "item": "", "detail": "Object required"}], "counts": {}}
    schema = document.get("schema")
    if schema not in SCHEMAS:
        return {"status": "HOLD", "issues": [{"code": "UNSUPPORTED_SCHEMA", "item": "", "detail": str(schema)}], "counts": {}}
    if schema == "flat-v1":
        raw = document.get("records")
    else:
        wrapper = document.get("data")
        raw = wrapper.get("entries") if isinstance(wrapper, dict) else None
    derived, claim = document.get("derived"), document.get("claim")
    if not isinstance(raw, list) or not isinstance(derived, list) or not isinstance(claim, dict):
        return {"status": "HOLD", "issues": [{"code": "MISSING_SECTIONS", "item": "", "detail": "records, derived and claim required"}], "counts": {}}
    if len(raw) > MAX_RECORDS or len(derived) > MAX_RECORDS:
        return {"status": "HOLD", "issues": [{"code": "TOO_MANY_RECORDS", "item": "", "detail": str(MAX_RECORDS)}], "counts": {}}

    sources: dict[str, tuple[str, str]] = {}
    for index, record in enumerate(raw):
        if not isinstance(record, dict) or not isinstance(record.get("id"), str) or not record["id"].strip() or "payload" not in record:
            issue(problems, "INVALID_RAW_RECORD", str(index))
            continue
        rid, status = record["id"], record.get("status")
        if rid in sources:
            issue(problems, "DUPLICATE_RAW_ID", rid)
            continue
        if status not in ("included", "excluded"):
            issue(problems, "INVALID_SELECTION", rid)
            continue
        try:
            fingerprint = digest(record["payload"])
        except (TypeError, ValueError):
            issue(problems, "INVALID_PAYLOAD", rid)
            continue
        sources[rid] = (status, fingerprint)

    mapped: set[str] = set()
    for index, record in enumerate(derived):
        if not isinstance(record, dict) or not isinstance(record.get("trace_id"), str) or not isinstance(record.get("source_sha256"), str):
            issue(problems, "INVALID_DERIVED_RECORD", str(index))
            continue
        rid, claimed = record["trace_id"], record["source_sha256"]
        if rid in mapped:
            issue(problems, "DUPLICATE_DERIVED_ID", rid)
        mapped.add(rid)
        if rid not in sources:
            issue(problems, "ORPHAN_DERIVED", rid)
        elif sources[rid][0] == "excluded":
            issue(problems, "EXCLUDED_IN_DERIVED", rid)
        elif sources[rid][1] != claimed:
            issue(problems, "HASH_MISMATCH", rid)

    included = {key for key, val in sources.items() if val[0] == "included"}
    excluded = {key for key, val in sources.items() if val[0] == "excluded"}
    for missing in sorted(included - mapped):
        issue(problems, "MISSING_DERIVED", missing)
    counts = {"raw_total": len(raw), "included": len(included),
              "excluded": len(excluded), "derived_total": len(derived)}
    for key in ("raw_total", "included", "excluded"):
        if type(claim.get(key)) is not int or claim[key] != counts[key]:
            issue(problems, "CLAIM_COUNT_MISMATCH", key,
                  f"reported={claim.get(key)!r}; observed={counts[key]}")
    problems.sort(key=lambda item: (item["code"], item["item"], item["detail"]))
    return {"status": "PASS" if not problems else "HOLD", "issues": problems,
            "counts": counts, "scope_note": "Structural consistency of declared data only; no independent source authentication."}

def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect synthetic agent-evaluation evidence")
    parser.add_argument("file", type=Path)
    args = parser.parse_args()
    try:
        with args.file.open(encoding="utf-8") as stream:
            result = audit(json.load(stream))
    except (OSError, UnicodeError, ValueError) as err:
        result = {"status": "HOLD", "issues": [{"code": "INPUT_ERROR", "item": "", "detail": str(err)}], "counts": {}}
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "PASS" else 1

if __name__ == "__main__":
    raise SystemExit(main())
