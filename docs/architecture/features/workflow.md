# Reusable setup, verification and release lifecycle

[Code map and atlas](../README.md) | [Owning contract](../../specs/workflow.md)

## Scope and source

Source owners: [bootstrap](../../../tools/bootstrap.py), [quality](../../../tools/quality.py), [review gate](../../../tools/review_gate.py), [evidence](../../../tools/evidence.py) and [release](../../../tools/release.py). This page describes current source and intended
contracts; adopting projects must verify their own adapters and product behavior.

## Component overview

```mermaid
flowchart LR
    Setup[Explicit bootstrap and stack config] --> Contract[Specs and expert decisions]
    Contract --> Quality[Configured quality and test adapters]
    Quality --> Archive[Verified current evidence]
    Archive --> Review[Real reviews and digest attestation]
    Review --> PR[Protected PR and CI]
    PR --> Release[Authorized validated release package]
```

## Representative sequence

```mermaid
sequenceDiagram
    participant A as Agent session
    participant T as Configured tools
    participant R as Fresh reviewers
    participant G as GitHub
    A->>A: Settle spec and architectural or UI decisions
    A->>T: Run quality and source-bound test adapters
    T-->>A: Actual outcomes and preserved raw evidence
    alt Required results pass
        A->>T: Verify archive and freeze and snapshot candidate
        A->>R: Two independent final reviews
        R-->>A: Explicit candidate verdicts
        alt Both approve unchanged candidate
            A->>G: Authorized PR with required host gates
            A->>T: Authorized release build after merge
            T->>T: Validate current source, results, artifacts and evidence
            T->>G: Publish only validated package
        else Rejected or stale approvals
            A->>A: Resolve and obtain a new pair
        end
    else Failure or missing outcomes
        T-->>A: Block delivery and retain failure
    end
```

## Change and verification boundaries

Initialization invalidates inherited approvals and does not grant account permission. Release validation runs before publication API mutations and never overwrites published versions. Architecture/UI preflights and final reviewers are distinct roles; CI cannot authenticate their identities.

See [requirements and gaps](../../requirements.json); diagrams and syntax validation
do not establish runtime correctness or measured performance.
