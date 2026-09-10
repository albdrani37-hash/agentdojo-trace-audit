# AgentDojo Trace Audit

Version 1.0.0 is archived at https://doi.org/10.5281/zenodo.22217485.

A benchmark-specific research-software layer that reconstructs a frozen AgentDojo v1.2.1 corpus and links source identity, record selection, population accounting, denominators, derived records, results and claim locators. It also validates a declared provenance-fault model.

## Quick start

See `QUICKSTART.md`. A local copy of the official AgentDojo commit `089ed468cf3ed0322acc66b0211f26d9d90dbf60` is required; no AgentDojo code, raw trace, or model-output byte is redistributed here.

## Scope

The verified results describe one frozen finite corpus. Evaluator replay establishes agreement with the official evaluator, not construct validity. Development Catalog A is post-repair conformance evidence. Frozen Catalog B detected and classified 408/408 cases but localized 336/408; its 72 localization failures are preserved. Post-repair Catalog C was developmental and localized 330/330 cases. The newly frozen Catalog D detected, classified, and localized 360/360 cases in its one-shot run. Two frozen benign-control suites produced 0/120 alarms. These exact results apply only to the declared synthetic catalogs and controls. External replicability has not been established.

## CTVI Agent Evidence Audit

### Make every evaluation claim traceable

Agent systems generate traces. Product and risk teams need evidence they can defend.

CTVI Agent Evidence Audit adds an evidence layer between execution logs and release decisions. It reconstructs the path from raw traces to reported findings and checks population integrity, denominators, exclusions, missing evidence and joint functional-security states.

The output is a decision-ready evidence bundle:

- frozen system and evaluation snapshot
- raw-to-derived trace lineage
- population and denominator integrity checks
- explicit UNKNOWN and HOLD states
- concurrent failure classification
- reproducibility checks with fail-closed validation
- executive findings and machine-readable results

The public reference implementation contains 11,624 selected records and 11,624 raw-to-derived links from a fixed AgentDojo v1.2.1 snapshot. It is a reproducibility demonstration rather than a general certification.

### Founding pilot

One agent system. One benchmark. Up to 1,500 traces. Delivered in 7–10 business days after data intake.

Designed for agent builders, evaluation and assurance teams, observability platforms and enterprises preparing high-consequence agent deployments.

For a technical fit discussion or partnership inquiry:

**Abdullah Alharbi**  
Independent Researcher — Saudi Arabia  
ORCID: https://orcid.org/0009-0009-7201-0295  
Email: albdrani37@gmail.com
