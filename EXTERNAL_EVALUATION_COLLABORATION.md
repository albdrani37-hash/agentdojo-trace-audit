# External AI Evaluation — Evidence Integrity Collaboration Brief

**Independent technical capability statement**  
**Abdullah Alharbi** — Independent Researcher & Python Developer, Saudi Arabia  
**Commercial contact:** abdullahalharbi@purelymail.com

> This document is an unsolicited, independent technical capability brief. It is **not authored, commissioned, endorsed or reviewed by OpenAI, ChatGPT, Global App Testing or any other named organization**. It does not imply a procurement relationship, certification, affiliation, access to nonpublic systems or availability of paid work.

## The focused problem

A model or agent benchmark may publish an aggregate success or safeguard result without presenting a sufficiently reviewable trail from the **declared evaluation population** through the actual executed runs, inclusion/exclusion decisions, transformations and reported findings.

An *evidence-integrity review* asks narrow, verifiable questions:

- Which executions, versions, source files, transformations, denominator definitions and exclusions actually support each selected outcome claim?
- Can someone rerun the checks under a documented frozen environment and obtain the declared results?
- Are missing records, contradictory identifiers, or unverifiable assertions retained as explicit unresolved findings rather than silently treated as passes?
- What is supported by the tested records — and what is **not** established about safety, robustness, generalisation or downstream deployment?

This is a complementary engineering component to human-led or institution-led evaluation. It is **not** a substitute for a model capability benchmark, safeguard effectiveness study, red-team engagement, independent assurance decision or regulatory sign-off.

## Inspectable public demonstration

The [AgentDojo Trace Audit project](README.md) is research software for one frozen AgentDojo v1.2.1 corpus. Its published implementation includes:

| Measured / recorded item | Public result | Essential qualification |
| --- | --- | --- |
| Record lineage | 11,624 selected records linked to derived outputs | Limited to a frozen benchmark snapshot |
| Frozen synthetic provenance-fault Catalog B | 408/408 detected and classified, **336/408 localized** | **72 localization misses preserved**; predefined synthetic fault model |
| Later frozen Catalog D | 360/360 detected, classified and localized | One specifically declared controlled run; cannot infer cross-domain accuracy |
| Frozen benign-control suites | 0/120 alarms in stated controls | Not a field false-positive rate |

The research-software release is archived at [Zenodo 10.5281/zenodo.22217485](https://doi.org/10.5281/zenodo.22217485). An independent, commercially tested product or external construct validation is **not** claimed.

A separate [FalconX synthetic Python QA demonstration](https://github.com/albdrani37-hash/FalconX/blob/main/CI_EVIDENCE.md) documents 25 distinct regression tests across Python 3.11–3.13 in a specific CI run. This is not a client case study.

## Bounded external engineering work package to discuss

For an authorised buyer running an agent evaluation, a **proposed** technical work package could comprise:

1. **Evaluation run manifest:** exact versions, input identifiers, hashes, record unit, population, exclusions and authorised sample inventory.
2. **Claim-to-execution linkage:** reproducible references between specified result tables and recorded runs with documented transformations.
3. **Automated consistency checks:** inspectable Python validation scripts, test fixtures, run instructions, and failure statuses for missing/inconsistent evidence.
4. **Exceptions and unknowns:** a machine-readable register of reproducible discrepancies, unresolved evidence and explicit limits.
5. **Decision-ready handover:** a concise summary explaining what can be verified from the sampled records, which issues remain open, and what further research would be required.

Initial scope is **one specified, frozen evaluation workflow**, subject to buyer-provided lawful data, schema agreement, security/privacy review, size assessment, review owner and written acceptance criteria. No non-public data should be emailed unsolicited.

## Why this could be relevant to external evaluation teams

OpenAI's public September 2026 [principles for effective third-party assessments](https://openai.com/index/priorities-principles-third-party-assessments/) emphasize independent assessment and clearly supported safety claims. The public [Frontier Assurance research engineering role](https://openai.com/careers/researcher-safety-frontier-assurance-san-francisco/) explicitly discusses evidence collection, reproducibility and tracing assessment limitations. These materials **motivate the general class of engineering problem**; they do not state that OpenAI needs or will purchase this service.

An evaluation delivery provider (including an OpenAI delivery partner) could consider evidence reconciliation as one separately scoped, conflict-managed quality-control component. Responsibility for the evaluation's scientific conclusions, release decision and client relationship remains with the authorised buyer.

## Commercial qualification / request

I am seeking a **paid, bounded, independently accepted engineering scope** only if there is a genuine buyer need. A procurement/delivery lead can email **abdullahalharbi@purelymail.com** with:

- The evaluation workflow and decision it supports (nonconfidential description);
- Desired technical outputs and approximate records/schemas;
- Named technical owner and authorised budget/procurement route;
- Eligibility to contract with a Saudi-based independent practitioner;
- Privacy, security, delivery, acceptance and payment milestones.

[Request a nonconfidential scope discussion](REQUEST_A_QUOTE.md) · [Enterprise service boundaries](ENTERPRISE_SERVICES.md) · [Detailed buyer case study](BUYER_CASE_STUDY.md).

No fixed price, timetable, guarantee, affiliation or contract is implied. No restricted dataset, credentials or private evaluation records should be sent until written authority and handling terms are agreed.
