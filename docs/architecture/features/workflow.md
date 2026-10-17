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
    Archive --> RC{New version?}
    RC -->|Yes| AR[Fresh architecture approval and attestation]
    RC -->|No| Review[Two fresh final code reviews]
    AR --> Review
    Review --> PR[Protected PR and CI]
    PR --> Release[Authorized validated release package]
```

## Representative sequence

```mermaid
sequenceDiagram
    participant A as Agent session
    participant T as Quality and<br/>evidence tools
    participant AR as Fresh release<br/>architect
    participant R as Two fresh<br/>final reviewers
    participant G as GitHub
    A->>T: Run required checks and preserve evidence
    T-->>A: Source-bound outcomes and explicit gaps
    alt Required acceptance fails
        A->>A: Retain failure and block conditional delivery
    else Completed candidate verified
        A->>T: Freeze inspected snapshot
        opt Every new version candidate
            A->>AR: Cumulative release diff and current architecture
            AR-->>A: Actual approval or blockers and gaps
        end
        alt Release approval missing or blocking
            A->>A: Block release tag and dispatch,<br/>release signing and publication
        else Routine change or release architecture approved
            A->>A: For release record only<br/>faithful architecture attestation
            A->>T: Freeze final tree and canonical digest
            A->>R: Independent final candidate, contract and evidence
            R-->>A: Two actual verdicts
            alt Both approve unchanged final candidate
                A->>G: Authorized protected PR and required host check
                opt Authorized release
                    A->>G: Authorized merged-main release steps
                    G->>G: Validate current package and reports before publish
                end
            else Rejected or changed candidate
                A->>A: Resolve, reverify and renew affected reviews
            end
        end
    end
```

## Change and verification boundaries

Initialization invalidates inherited approvals and does not grant account permission. Release validation runs before publication API mutations and never overwrites published versions. Architecture/UI preflights and final reviewers are distinct roles; CI cannot authenticate their identities.

See [requirements and gaps](../../requirements.json); diagrams and syntax validation
do not establish runtime correctness or measured performance.

Every new version requires the [release architecture checkpoint](../../RELEASING.md#release-architecture-review).
The inspected snapshot precedes its attestation; final reviewers approve the full
canonical tree including that record. Missing approval blocks the release agent,
not a newly implemented CI architecture-judgment service.
