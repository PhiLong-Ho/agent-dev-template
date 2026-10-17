# Development graph, release graph and UI references

[Code map and atlas](../README.md) | [Owning contract](../../specs/graph-first.md)

## Scope and source

Source owners: [graph hook](../../../tools/graph_first.py), [worker](../../../tools/graph_worker.py), [release graph](../../../tools/graph_release.py) and [reference gate](../../../tools/ui_reference.py). This page describes current source and intended
contracts; adopting projects must verify their own adapters and product behavior.

## Component overview

```mermaid
flowchart TB
    Client[Claude or Codex events] --> Hook[Installed shared graph-first hook]
    Hook --> CRG[Root-isolated incremental CRG cache]
    CRG --> Hints[Bounded navigation hints and diagnosed fallback]
    Tag[Authorized release build] --> Corpus[Curated tracked code and docs]
    Corpus --> Snapshot[Graphify snapshot and sealed manifest]
    Actual[Inspected actual UI captures and sources] --> Catalog[Approved reference catalog]
    Catalog --> Gate[Source and PNG freshness gate]
```

## Representative sequence

```mermaid
sequenceDiagram
    participant C as Coding client
    participant H as Installed hook
    participant W as CRG worker
    C->>H: Prompt, search or edit event
    H->>W: Refresh eligible current inputs within budget
    alt Fresh useful graph
        W-->>H: Root-scoped nodes and neighbors
        H-->>C: Bounded hints or one bounded redirect
    else Missing, stale, failed or ambiguous
        H-->>C: Diagnosed normal-search fallback
    end
    Note over C,W: No routine Graphify update or paid provider calls
    opt Explicit release build
        participant R as Release graph builder
        R->>R: Index curated tracked source and structural document links
        R->>R: Seal and validate snapshot/source bindings
    end
    opt UI implementation changed
        C->>C: Inspect actual render and record real reference approval
        C->>C: Validate source and PNG freshness
    end
```

## Change and verification boundaries

Current CRG is navigation context, Graphify is an immutable release snapshot, and UI references are approved artifacts; none substitutes for another. Exclude local config, screenshots/evidence and generated/vendor files from graph inputs. Do not auto-approve a changed render or install Graphify watch/git hooks.

See [requirements and gaps](../../requirements.json); diagrams and syntax validation
do not establish runtime correctness or measured performance.
