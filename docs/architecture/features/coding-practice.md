# Daily architecture screen and coding practice

[Code map and atlas](../README.md) | [Owning coding practice](../../CODING_PRACTICE.md)

## Scope and source

Source owners: [Coding practice](../../CODING_PRACTICE.md), [workflow](../../WORKFLOW.md) and [architecture skill](../../../.agents/skills/architecture-review/SKILL.md). This page describes current source and intended
contracts; adopting projects must verify their own adapters and product behavior.

## Component overview

```mermaid
flowchart LR
    Request[Spec and impact screen] --> Expert{Architecture impact or uncertainty?}
    Expert -->|Yes| Review[Fresh architecture expert]
    Expert -->|No with reason| Iterate[Targeted implementation loop]
    Review --> Iterate
    Iterate --> Complete[Required candidate gates]
    Complete --> Freeze[Source-bound evidence and freeze]
    Freeze --> Final[Two fresh final reviews]
```

## Representative sequence

```mermaid
sequenceDiagram
    participant A as Author
    participant E as Architecture expert
    participant T as Checks and evidence
    participant F as Final reviewers
    A->>A: Read source map and record outcome and impact
    opt Architectural or uncertain change
        A->>E: Current owners, diagrams, proposal and known gaps
        E-->>A: Explicit approach verdict and verification risks
        A->>A: Resolve blockers and consequential user questions
    end
    loop Focused iteration
        A->>T: Relevant reproduction and affected checks
        T-->>A: Actual result and rerun reason
    end
    A->>T: Complete all required candidate checks
    T-->>A: Current or valid reused evidence
    A->>A: Freeze docs, source, coverage and evidence
    A->>F: Two independent exact-candidate reviews
    Note over A,F: Changed candidate needs a new final pair
```

## Change and verification boundaries

No test gate is removed for speed. Reuse requires source/test/configuration compatibility; any candidate content change invalidates final approvals. Architecture preflight is an actual agent-session review, not an unauthenticated unattended CI reviewer.

See [requirements and gaps](../../requirements.json); diagrams and syntax validation
do not establish runtime correctness or measured performance.
