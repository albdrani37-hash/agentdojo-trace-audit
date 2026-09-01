# Architecture

The generic core (`trace_audit.core`) validates file identity, selection, population, denominator, lineage and claim invariants. The AgentDojo adapter (`trace_audit.agentdojo_adapter`) maps source-native fields into the audit record schema. `trace_audit.stages` supplies CLI stages. Expected historical values occur only in downstream regression verification, never as reconstruction inputs.
