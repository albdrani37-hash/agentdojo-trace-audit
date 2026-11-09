# Epistemic Reliability of AI Agent Safety Claims: Cross-Benchmark Replication and Evidence-Provenance Tests

**Principal investigator:** Abdullah Alharbi — Independent Researcher, Riyadh, Saudi Arabia  
**ORCID:** [0009-0009-7201-0295](https://orcid.org/0009-0009-7201-0295)  
**Funding requested:** USD 60,000 for six months  
**Stage:** Proposed extension of an existing open-source reproducibility artifact

## Research question and contribution

Under which conditions can an AI-agent safety claim be reconstructed from its underlying evaluation records, and when do apparently plausible conclusions collapse under provenance, denominator, or evaluator inconsistencies?

This project will study the epistemic reliability of claims about tool-using AI agents, **not** attempt to certify their safety. It combines preregistered replication, blinded integrity challenges, transparent negative results, and a reusable claim-to-evidence protocol for alignment-relevant evaluations.

## Existing technical basis — evidence, not generalization

The public AgentDojo Trace Audit v1.0.0 software reconstructs **11,624 selected records** and their source-to-derived lineage from a frozen AgentDojo v1.2.1 corpus. In declared synthetic tests, a frozen catalog detected/classified **408/408** injected cases but localized **336/408** (72 localization failures); two benign-control suites produced **0/120 alarms**. These observations are restricted to the stated corpus, fault models, and controls. They do **not** demonstrate cross-benchmark generalization, external replication, or proof of agent alignment. The proposed research is designed specifically to test these missing properties.

## Falsifiable questions and primary outcomes

1. **Claim reconstruction:** How often do published or operational agent-evaluation claims survive independent reconstruction of population, denominators, exclusions, trace identities, and evaluator outputs?
2. **Integrity testing:** How well do provenance checks detect injected integrity faults while avoiding false alarms on genuine controls?
3. **Transferability:** Which parts of an audit protocol remain valid when datasets, trace schemas, and evaluation tasks change?

**Primary measures:** reproducible-claim rate; anomaly-detection sensitivity and benign-control false-positive rate; fault-localization accuracy; agreement with independently recomputed metrics. We will report uncertainty intervals and all failures, with predefined acceptance criteria and no selective post-hoc exclusions.

## Research method

1. **Preregister and freeze.** Define a claim taxonomy, assumptions, inclusion rules, benchmarks, outcome measures, adversarial perturbations, and analysis scripts before confirmatory testing.
2. **Replicate.** Independently reconstruct AgentDojo findings and attempt extensions to up to two additional public agent-security benchmarks, selected after assessing access, licensing, and schema compatibility. Target a small set of independently checkable published results; disclose inaccessible or non-reproducible cases rather than silently substituting them.
3. **Challenge.** Blind-test missing or duplicated records, modified identifiers, contradictory denominators, evaluator divergence, and incomplete provenance. Compare against simple checksum, aggregate-metric, and manual-review baselines.
4. **Validate and publish.** Solicit independent scrutiny, report successes and failures, and release reproducible code, non-sensitive fixtures, a documented audit protocol, and a research paper.

## Feasibility and six-month execution plan

| Period | Deliverable |
| --- | --- |
| Month 1 | Preregistration, baseline selection, claim ontology, frozen manifests and protocols |
| Months 2–3 | Independent AgentDojo reconstruction and licensing-dependent second-benchmark pilot |
| Month 4 | Blinded integrity experiments and evaluation against baselines |
| Month 5 | External replication attempt, robustness analysis and negative-results audit |
| Month 6 | Open reproducibility package, report/manuscript and dissemination |

## Indicative research budget

| Workstream | USD |
| --- | ---: |
| Investigator research and software implementation | 30,000 |
| Independent replication and specialist review (to be contracted) | 12,000 |
| Compute, test environments and data processing | 8,000 |
| Benchmark integration and reproducibility engineering | 6,000 |
| Publication, open-science maintenance and administration | 4,000 |
| **Total** | **60,000** |

## Scientific value and fit with Iliad

The field needs a disciplined way to distinguish verified evidence from confident narratives when reporting AI-agent safety. A replicable evaluation claim is not equivalent to safety or alignment, but it is a prerequisite for accumulating dependable evidence about alignment-relevant interventions. The study is a bounded test of empirical rigor, aligned with Iliad's interest in methodologically mature, theory-informed experiments and work that raises the epistemic standard of AI safety.

## Risks, limitations and research integrity

Benchmark transfer may fail because access, schemas or evaluators differ; independent replication may disagree with the original artifact; some published claims may lack adequate evidence. All are publishable outcomes under the proposed protocol. The project excludes claims of general safety certification, production deployment, or causality established solely from trace provenance. No unnamed collaborator, institutional sponsor, or third-party endorsement is represented as secured.

## Existing artifacts and contact

- **Public code:** https://github.com/albdrani37-hash/agentdojo-trace-audit
- **Archived software:** https://doi.org/10.5281/zenodo.22217485
- **ORCID:** https://orcid.org/0009-0009-7201-0295
- **Contact:** abdullahalharbi@purelymail.com

*Iliad Open Call — Research proposal — 9 November 2026*
