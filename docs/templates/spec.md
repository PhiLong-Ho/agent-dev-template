# Feature Specification: <feature>

**Branch**: <feature/name> **Status**: Draft **Input**: <requested outcome>

## User Scenarios & Testing

### User Story 1 — <outcome> (Priority: P1)

**Why this priority**: <user impact>
**Independent Test**: <observable check>
**Acceptance Scenarios**: Given <state>, When <action>, Then <observable result>.

### Edge Cases

<cancel/failure/recovery, bounds, input, lifecycle, accessibility, persistence>

## Architecture links

Link the feature overview and sequence in `docs/architecture/features/` using
[the architecture template](feature-architecture.md). Keep technical ownership
there and observable acceptance here. Record architectural impact and expert
review in the change plan before dependent implementation.

## Requirements

### Functional Requirements

Assign stable numbered requirements and WF-* map IDs in the owning baseline;
state observable behavior and explicit exclusions, not implementation details.

### Key Entities

<domain entities and state>

## Experience review

For UI changes, link the expert proposal, before/after tasks, representative sketch,
material questions, actual user decision/authorization and acceptance consequences.

## Feature flow

Add a small Mermaid state/task flow when helpful; render/inspect against source.
Keep component diagrams and technical plans in architecture/change docs.

## Success Criteria

### Measurable Outcomes

<functional outcomes, latency/visual criteria and actual verification method>

## Assumptions

<compatibility, dependencies, unverified/manual/deferred scenarios>
