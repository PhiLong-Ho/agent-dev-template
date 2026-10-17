# Local command supervision and read-only observation

[Code map and atlas](../README.md) | [Owning contract](../../specs/local-monitoring.md)

## Scope and source

Source owners: [run_monitor](../../../tools/run_monitor.py), [quality adapter](../../../tools/quality.py) and [project configuration](../../../tools/project.py). This page describes current source and intended
contracts; adopting projects must verify their own adapters and product behavior.

## Component overview

```mermaid
flowchart LR
    Runner[Owning quality or build runner] --> Supervisor[run_monitor.Session]
    Supervisor --> Child[Owned child process tree]
    Child --> Raw[Preserved raw streams]
    Raw --> Extraction[Bounded progress extraction]
    Extraction --> Status[Atomic status and events]
    Supervisor --> Status
    Status --> Viewer[Independent read-only viewer]
    Supervisor --> Outcome[Child, capture and finalization outcome]
    Outcome --> Runner
```

## Representative sequence

```mermaid
sequenceDiagram
    participant R as Runner
    participant S as Supervisor
    participant C as Owned child
    participant V as Viewer
    R->>S: Argument-array command with deadline
    S->>C: Start and own process tree
    C-->>S: Live stdout and stderr
    S->>S: Preserve bytes and bounded observation
    V->>S: Read atomic status
    S-->>V: Heartbeat, activity, progress or stale/unknown state
    alt Child exits
        C-->>S: Actual return code
    else Deadline or cancellation
        S->>C: Bounded owned-process cleanup
    end
    S-->>R: Outcome including capture/finalization faults
    R->>S: Final runner result
    Note over R,V: Viewer never launches, retries or cancels work
```

## Change and verification boundaries

Quality/build runners decide acceptance, including final monitoring faults. Heartbeat is not test progress or success. Windows process jobs and POSIX cleanup need their own platform verification; a generic adapter adds no product/device recovery unless explicitly implemented.

See [requirements and gaps](../../requirements.json); diagrams and syntax validation
do not establish runtime correctness or measured performance.
