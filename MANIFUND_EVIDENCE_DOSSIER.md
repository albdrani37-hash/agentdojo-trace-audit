# Evidence dossier for the Manifund open-source research proposal

**Project:** [Open-Source Evidence Integrity for AI Agent Evaluations](https://manifund.org/projects/open-source-evidence-integrity-for-ai-agent-evaluations)  
**Researcher:** Abdullah Alharbi — independent researcher, Saudi Arabia  
**Last checked against repository and public proposal:** 16 November 2026  
**Fundraising:** $15,000 goal; $7,500 minimum; proposal closes 7 December 2026. These are **proposed funding terms**, not funds already received.

## A 60-second assessment

**Problem.** A benchmark score does not by itself show which execution records were included, why records were excluded, whether denominators were consistent, or whether every derived claim can be connected back to the evidence.

**Already public.** [AgentDojo Trace Audit v1.0.0](README.md) is **benchmark-specific research software**, with code, [quick-start instructions](QUICKSTART.md), [limitations](LIMITATIONS.md) and an [archived release](https://doi.org/10.5281/zenodo.22217485). It reconstructs a frozen AgentDojo v1.2.1 corpus and tests a defined set of evidence-provenance faults.

**What the grant pays for.** Making the underlying evidence-checking approach easier for independent evaluators and smaller research teams to inspect and reuse: documented schemas, a command-line audit tool, reproducible synthetic validation, clear PASS/HOLD/FAIL-type reporting where justified by the evidence, tests, and limits. This extension is **proposed, not delivered**.

**What it does NOT promise.** Authentication of every raw trace, proof of benchmark construct validity, deployment to customers, zero false positives, reliable performance across unrelated benchmarks, or certification that an AI agent is safe.

## Existing evidence: what was observed, and what was not

| Publicly reported observation | Scope of the claim | Direct evidence |
| --- | --- | --- |
| 11,624 selected records and 11,624 raw-to-derived links reconstructed | One frozen AgentDojo v1.2.1 snapshot; a demonstration of record-level lineage, not independently verified authenticity of raw source data | [Repository README](README.md) |
| Frozen Catalog B: 408/408 synthetic faults detected and classified; **336/408** correctly localized | A predefined synthetic-fault catalog; **72 localization misses retained and reported** | [README, Scope](README.md#scope) |
| Separately frozen, post-repair Catalog D: 360/360 detected, classified and localized in one shot | New **synthetic** catalog; no generalization claim; developmental Catalog C is not independent confirmation | [README, Scope](README.md#scope) |
| Two frozen benign-control suites: **0 alarms in 120 cases** | Specific benign fixtures only; not evidence of a zero real-world false-alarm rate | [README, Scope](README.md#scope) |

**Interpretation:** the interesting result is not a perfect score. It is that failures can be exposed and attributed to precisely defined stages instead of being silently transformed into confident evaluation claims. A detector can flag an anomaly correctly while still pointing to the wrong location; these are different capabilities. The published 72 misses remain important negative evidence.

### Reproduction path and evidence boundaries

1. Inspect the [public repository](https://github.com/albdrani37-hash/agentdojo-trace-audit) and the archived [v1.0.0 release](https://doi.org/10.5281/zenodo.22217485).
2. Follow [QUICKSTART.md](QUICKSTART.md). A separate local copy of the official AgentDojo upstream source at commit `089ed468cf3ed0322acc66b0211f26d9d90dbf60` is required. This repository does not redistribute official AgentDojo code, source traces, or model outputs.
3. Run the documented `./run_all` and `./verify_all` commands with the appropriate source archive and local work directory.
4. Compare derived counts, raw-to-derived lineage, classification versus localization, benign controls and any unresolved checks against the declared frozen conditions.

**Verification status:** the published results are those of the author's bounded implementation. Independent external replication has **not** been established. Source-native utility and security labels were not independently validated. See [LIMITATIONS.md](LIMITATIONS.md). The links and instructions are supplied for review; the project does not claim that an outside reviewer has completed the procedure.

## Small, dependency-free example for reviewers

A second, **separate** demonstration is available in the [FalconX portfolio](https://github.com/albdrani37-hash/FalconX/blob/main/examples/eval-evidence-demo/README.md): a standard-library-only [Python evidence checker](https://github.com/albdrani37-hash/FalconX/blob/main/examples/eval-evidence-demo/verify_evidence.py) and its [12 synthetic unit tests](https://github.com/albdrani37-hash/FalconX/blob/main/examples/eval-evidence-demo/test_verify_evidence.py). Its documented local Python 3.13 test run passed 12/12 on 27 October 2026; this is an **author-reported local run**, not independent verification. A reviewer can use Python 3.11+ to run it without proprietary benchmark data. It illustrates explicit `PASS`, `HOLD`, and `FAIL` responses when provided claims, included runs or artifact digests disagree.

This demonstration **is not** the AgentDojo frozen-corpus result, an authenticated source-of-truth proof, or a customer deployment. The ability to fabricate an internally consistent input remains outside the checker’s trust boundary.

## What is new in the proposed funded work?

The current system is tightly coupled to one research snapshot. The funded work would develop a more accessible, documented Python audit interface and controlled test corpus so researchers can inspect which parts of an agent-evaluation claim are supported by structurally consistent evidence.

The work is not a claim to create a universal verifier. In particular, a valid hash or a consistent record count does not prove that a run was genuine, a benchmark measured the right concept, or an agent was safe.

### Deliverables with $7,500 minimum funding: first six weeks after funding

- Documented evidence/lineage schema with explicit assumptions, examples and unresolved states.
- Usable Python command-line checker for structural consistency of inputs, exclusions, population counts and derived claims.
- At least **40 reproducible synthetic test cases**, including intentional missing/duplicate/inconsistent evidence cases and valid controls.
- Automated tests, reproducible command instructions and a public findings/limitations note.
- A public milestone report distinguishing what works, what fails and what was not tested.

**Acceptance criteria:** a reviewer can run the published checks against their documented synthetic fixtures; outputs distinguish a detected error from unknown or insufficient evidence; reported counts reconcile to included/excluded records; unresolved cases are not silently reported as passing. Results and negative cases will be published.

### Full $15,000 funding: twelve weeks after funding

In addition to the above:
- Expand to at least **150 controlled test cases**, with explicit classification, localization and false-alarm reporting.
- Versioned, machine-readable audit reports and a documented command-line interface.
- Investigate compatibility with **two publicly documented evaluation-data schemas**, contingent on licensing, access and technical fit.
- Publish the final release, reproducibility walkthrough, known limitations and failure analysis.

Compatibility **investigations** are planned, not promised integrations or production deployments. No specific customer, partner, external reviewer or downstream adopter has committed.

## Budget requested — not yet spent

| Planned allocation | USD |
| --- | ---: |
| Research engineering and documentation | 9,000 |
| Synthetic fixtures and validation | 1,750 |
| Documentation and release testing | 1,250 |
| External technical feedback and compatibility work (if available) | 1,700 |
| Testing and archival resources | 550 |
| Contingency and maintenance handover | 750 |
| **Total** | **15,000** |

If only the minimum is received, work is bounded to the six-week minimum-scope deliverables; the full twelve-week extension is contingent on full funding. External reviewers have not been contracted. Funding terms, milestones and disbursement remain subject to the platform's grant process.

## Decision-critical limitations and research integrity

- **Measurement boundary:** structural integrity and provenance consistency, not general model safety, cybersecurity certification, independent benchmark validity, or established scientific impact.
- **Risk:** required upstream source, schema changes, and tests that behave differently beyond the frozen benchmark. Mitigation: licensed upstream dependency stated explicitly, documented input assumptions, adversarial and benign fixtures, failure-first reporting.
- **Independence:** no outside replication or production adoption is claimed; the study should be judged on reproducibility and the quality of publicly inspectable failure reporting.
- **Open publication:** code, synthetic fixtures, results (including null or negative results), commands and limitations will be published subject to third-party licensing.
- **Other funding:** related applications may be pending. Before accepting any award, overlapping costs, hours and deliverables will be disclosed and partitioned; the same work will not be charged twice.
- **Fundraising status:** creating a public proposal or signing a grant agreement does not mean that money has been pledged or disbursed.

## Primary review links

- [AgentDojo Trace Audit — source and frozen outcomes](README.md)
- [Reproduction prerequisites and commands](QUICKSTART.md)
- [Explicit limitations](LIMITATIONS.md)
- [Archived citable software release, Zenodo DOI 10.5281/zenodo.22217485](https://doi.org/10.5281/zenodo.22217485)
- [Author's technical portfolio](https://github.com/albdrani37-hash/FalconX/blob/main/PORTFOLIO.md)
- [Researcher ORCID](https://orcid.org/0009-0009-7201-0295)

**For public-benefit funding questions:** abdullahalharbi@purelymail.com. Do not email private source traces, secrets, credentials or customer data. Any evidence review should use public or approved synthetic materials.

*This document supports assessment of the existing Manifund proposal. It is not a new funding application, an assurance certificate, or a declaration of successful fundraising.*
