# Feature Specification: Graph-first development and current UI references

**Branch**: feat/graph-first-workflow **Status**: Implemented; evidence scoped separately
**Input**: CRG hooks for Claude/Codex, release-only Graphify, latest approved UI references.

## User Scenarios & Testing

### User Story 1 — Navigate current code before coding/review (Priority: P1)

**Why this priority**: Reduce broad searches without breaking literal work.
**Independent Test**: Real CRG parses a fixture; hook payloads exercise both clients,
edits/deletions, hits/misses, session routing and failure recovery.
**Acceptance Scenarios**: Given a fresh useful match, when a simple search repeats,
then return locations/relations and at most one denial with an override. Given
unavailable/stale data, diagnose fallback and permit scoped source tools.

### User Story 2 — Inspect release knowledge and current approved UI (Priority: P1)

**Why this priority**: Maintain code/document and visual context without noisy evidence.
**Independent Test**: Real Graphify extracts a tagged fixture and release validation
requires checksummed graph assets. Changed UI sources/images/states must fail freshness.
**Acceptance Scenarios**: Given a release build, then graph assets bind eligible tracked
code/docs to its source. Given a UI change, reconcile approved references against
actual renders before final review.

### Edge Cases

Native trust/restart, missing graphs/dependencies, malformed settings, duplicate hooks,
permission preservation, complex/cross-repo searches, worker timeout/lock contention;
no-UI starter, missing approval/state, altered images, excluded tracked evidence,
dirty release source and graph/source mismatch.

## Requirements

### Functional Requirements

Baseline FR-004/WF-GRAPH-001, FR-005/WF-INSTALL-001, FR-006/WF-SNAPSHOT-001 and
FR-007/WF-REFERENCE-001 own criteria. See [commands/limits](../GRAPH_FIRST.md) and
[master reference protocol](../ui-reference/README.md).

### Key Entities

Current root-isolated CRG cache, bounded hook event/result, installation backup,
release graph/input manifest and latest approved UI-state catalog.

## Experience review

No product interaction changes. Native trust uses the client's existing review UI.
Reference approval requires actual rendered inspection and follows the existing
UI expert/material-decision workflow.

## Feature flow

~~~mermaid
flowchart LR
    Prompt[Prompt, search or edit] --> CRG[Bounded current CRG refresh]
    CRG --> Hints[Locations and direct neighbors]
    CRG --> Fallback[Diagnosed scoped fallback]
    Tag[Authorized reviewed release] --> Corpus[Curated tracked code and docs]
    Corpus --> Graphify[Local Graphify AST and explicit document index]
    Graphify --> Assets[Checksummed snapshot and manifest]
    UI[UI change] --> Renders[Inspect and approve actual renders]
    Renders --> Catalog[Latest per-state reference catalog]
    Catalog --> Gate[Source and image freshness gate]
~~~

## Success Criteria

### Measurable Outcomes

Real tool fixtures verify current symbol/test relationships and release code/doc
coverage. Tests verify bounded valid hook outputs, fallback, settings preservation,
archive/source validation and stale reference rejection. Native activation, product
renders and hosted release execution require separate evidence.

## Assumptions

Python 3.11+, Git, pinned dependencies, local command-hook support and native Codex
trust. Structural indexing needs no paid provider; semantic extraction is excluded.
UI adopters must declare their actual reference matrix.
