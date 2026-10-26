# Case study: from AI-agent execution records to reviewable evaluation evidence

**Public technical demonstration. Not a client deployment or a safety certification.**

## The evaluation problem

A reported AI-agent success or failure rate can be correct as a calculation while leaving important questions unanswered: What are the actual units counted? Which recorded executions were included or excluded? Can a reviewer trace the output table back to the raw events? What happens when evidence references are missing or inconsistent?

The objective of this research implementation is to make those questions testable on a **fixed, version-specific AgentDojo corpus**.

## Published implementation and observed results

| Testable element | Publicly documented evidence | Boundary |
| --- | --- | --- |
| Trace-to-derived linkage | 11,624 selected records and 11,624 raw-to-derived links within the archived frozen corpus | One AgentDojo v1.2.1 snapshot; not an external customer dataset |
| Population and denominator accounting | Explicit record selection, version identifiers, unit definitions, provenance links and exclusion checks | Does not prove scientific construct validity |
| Synthetic provenance-fault detection | Frozen Catalog B: 408/408 detected and classified, 336/408 localized; **72 localization misses remain** | Faults are synthetic and predefined; do not extrapolate an operational detection rate |
| Later synthetic development / freeze | Post-repair Catalog C: 330/330 localized; new frozen Catalog D: 360/360 detected, classified and localized in the declared run | Different catalogs are not interchangeable independent trials |
| Benign synthetic controls | Two frozen suites: 0/120 alarms in the declared controlled runs | Not a field-measured false-alarm rate |

Source, command instructions, frozen configurations and negative findings are documented in the [main repository README](README.md) and [Quickstart](QUICKSTART.md). The 1.0.0 research-software release is archived under [Zenodo DOI 10.5281/zenodo.22217485](https://doi.org/10.5281/zenodo.22217485).

## Commercially useful output — subject to a separately signed scope

For a buyer with an existing AI-agent evaluation workflow, a bounded technical work package **may** deliver:

1. A frozen data and run manifest with hashes, counts, units, exclusions and missingness.
2. A source-to-claim map for selected evaluation results and the transformations that generated them.
3. Repeatable Python checks and a reproducibility guide tailored to an agreed schema.
4. A findings register retaining contradicted, missing and unverified records as explicit **HOLD / UNKNOWN** outcomes.
5. A decision brief that distinguishes what evidence supports from what it cannot establish.

This would be **engineering evidence review**, not comprehensive penetration testing, legal compliance, cryptographic authentication, human scientific validation or a promise that an agent is safe.

## Example buyer-fit test

A relevant buyer can answer yes to most of these questions:

- Our team already runs agent evaluations and records executions.
- We have a specific report, release gate or evaluation claim that someone must defend.
- We can lawfully provide a permitted frozen test subset and field/schema definitions.
- We need a reproducible review with defined acceptance criteria.
- An approved budget owner can contract for a **substantial paid** independent review from Saudi Arabia.

If those conditions are absent, do not initiate an unbounded unpaid pilot.

## Procurement enquiry

**Abdullah Alharbi — Independent Researcher & Technology Developer, Saudi Arabia**

For a confidential, non-sensitive technical-fit conversation, send the scope, expected outputs, budget owner and contractor eligibility requirements to **abdullahalharbi@purelymail.com**.

**Next step for a real buyer:** [Request a scoped paid evaluation-evidence review](REQUEST_A_QUOTE.md). See also the [enterprise service description and exclusions](ENTERPRISE_SERVICES.md). No fixed fee, timeline or customer acceptance is implied until agreed in writing.
