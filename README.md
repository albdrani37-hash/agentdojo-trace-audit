# AgentDojo Trace Audit

A benchmark-specific research-software layer that reconstructs a frozen AgentDojo v1.2.1 corpus and links source identity, record selection, population accounting, denominators, derived records, results and claim locators. It also validates a declared provenance-fault model.

## Quick start

See `QUICKSTART.md`. A local copy of the official AgentDojo commit `089ed468cf3ed0322acc66b0211f26d9d90dbf60` is required; no AgentDojo code, raw trace, or model-output byte is redistributed here.

## Scope

The verified results describe one frozen finite corpus. Evaluator replay establishes agreement with the official evaluator, not construct validity. Development Catalog A is post-repair conformance evidence. Frozen Catalog B detected and classified 408/408 cases but localized 336/408; its 72 localization failures are preserved. Post-repair Catalog C was developmental and localized 330/330 cases. The newly frozen Catalog D detected, classified, and localized 360/360 cases in its one-shot run. Two frozen benign-control suites produced 0/120 alarms. These exact results apply only to the declared synthetic catalogs and controls. External replicability has not been established.
