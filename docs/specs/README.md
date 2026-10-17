# Feature contracts

[Workflow lifecycle](workflow.md) covers setup, review, evidence and release.
SPEC.md owns stable numbered requirements; [coverage](../coverage.md) owns concrete
checks/gaps. Add product features with [the Spec Kit-style template](../templates/spec.md).
Keep architecture/technical plans separate from observable product contracts.

[Graph-first development](graph-first.md) owns client hooks, release graph snapshots
and latest approved UI-reference behavior.

[Local development monitoring](local-monitoring.md) owns live observation, deadlines,
raw-stream preservation and an independent read-only status view.

[Reference CLI](../architecture/features/reference-cli.md) owns replaceable FR-001 behavior;
[coding practice](../CODING_PRACTICE.md) owns NFR-008/WF-PRACTICE-001.
The [complete architecture atlas](../architecture/README.md) links every current
feature owner to its component overview and sequence.
