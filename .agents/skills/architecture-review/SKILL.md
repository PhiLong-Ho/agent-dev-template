---
name: architecture-review
description: Review architectural impact before implementation when a change may affect ownership, interfaces, lifecycle, concurrency, persistence, shared behavior or delivery boundaries. Also use for source-based architecture documentation and design reviews.
---

Read AGENTS.md, docs/ARCHITECTURE.md, docs/architecture/README.md and the owning
spec/feature architecture page. Consult current code-review-graph, then inspect
actual source and tests. Graphify is a release snapshot, not current truth.

Every task records an architecture-impact note. A clearly local wording, style
or implementation correction can record N/A with its source-based reason. If the
change may affect boundaries, state ownership, IPC/API contracts, lifecycle,
threading/queues, persistence/migration, shared input/geometry, security/privacy,
dependencies/build topology or release/evidence bindings, create a fresh read-only
architecture expert before dependent implementation. Uncertain impact needs review.

Give the expert the request, constraints, source/diff, current diagrams, requirements,
known failures and test/evidence gaps. Ask for:
- affected owners, trust/process/thread boundaries and invariants;
- current/proposed overview and sequence, including failure, cancellation, stale
  work, rollback and teardown; viable alternatives and consequential tradeoffs;
- compatibility/migration impact and affected verification, with exclusions;
- explicit approve-approach, changes-needed or unresolved-questions conclusion.

Record the expert identity, inspected scope, findings, chosen approach and decision
in the existing change record. Resolve blockers before dependent work. Clarify
consequential unclear requirements with the user; proceed on authorized routine
technical choices without repeated permission. Re-review material departures.

Maintain source-linked system/component and feature overview/sequence diagrams.
Use docs/templates/feature-architecture.md; render and inspect changed diagrams
against actual source. Label intended contracts, historical/deferred/debug scope
and known failures; a diagram does not establish runtime correctness. Add an ADR
only for a material lasting decision, recording alternatives and consequences.

This preflight does not approve rendered UI or replace either of the two fresh
final-candidate reviewers. It creates no unattended service or CI-authenticated
expert gate; the agent session must perform and record the real review.
