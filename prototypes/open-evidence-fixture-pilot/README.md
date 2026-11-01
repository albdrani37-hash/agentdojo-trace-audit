# Open Evidence Integrity Pilot — synthetic research prototype

This is an **independent, bounded, reproducible Python prototype**, created as a preliminary demonstration of a proposed Manifund public-benefit project, **Open Evidence Integrity Fixtures and Audit Reports for AI Agent Evaluations**. It uses Python 3.10+ standard library and toy input schemas. **No grant has been awarded, and the proposed 12-week project has not been completed.**

## Reproduce

From this directory, run:

    python3 -m unittest discover -s tests -v
    python3 audit.py examples/valid.json
    python3 audit.py examples/tampered.json

The last command is *expected* to return an exit status of 1 and report HOLD.

- Schema: flat-v1 uses records; wrapped-v1 uses data.entries.
- Source record: id (unique, nonempty), status (included/excluded), and payload (arbitrary JSON).
- Derived link: trace_id, source_sha256 (SHA-256 over canonically sorted and compact UTF-8 JSON payload).
- Claim: raw_total, included, excluded (integer counts).

Checks include missing and duplicate rows, links from excluded or nonexistent records, inconsistent reported populations, and altered payloads. Two tiny schemas are defined purely to exercise the interface; **these are not existing vendor integrations**.

PASS means only that the supplied file is structurally self-consistent for this limited model. HOLD means missing information or inconsistencies. Source hashes are untrusted input and do not authenticate provenance. This prototype is *not* an AI safety certification, external replication, formal proof, production security control, or evidence of a customer deployment.

The previous published [AgentDojo Trace Audit](https://github.com/albdrani37-hash/agentdojo-trace-audit) addresses one benchmark-specific frozen corpus. This prototype does *not* claim to reproduce the published 11,624-record demonstration. Its future funded work would be broader public fixture sets, schema integrations, documentation, and independent review. That scope is distinct from the AI Alignment Foundation proposal on action authorization under planner revision.

Creator: Abdullah Alharbi, independent researcher, Saudi Arabia. Contact for proposed public-benefit project: falconxintelligence@gmail.com. Proposed Manifund target (not yet published): USD 15,000. The parent repository's Apache-2.0 license applies.