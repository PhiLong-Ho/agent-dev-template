---
name: graph-first
description: Consult current code-review-graph for coding, debugging, refactoring and code reviews; use release-only Graphify snapshots for code/document navigation and maintain approved UI references. Use for code work, not unrelated conversation.
---

The shared Claude/Codex hooks automatically refresh the local code-review-graph
before prompts, simple code searches and edits, and once at Stop. Use bounded
queries and direct-neighbor impact before implementation and independent review:

```sh
python tools/graph_first.py query SymbolName
python tools/graph_first.py impact src/example.py
```

Run from the intended repository (subdirectories are supported). The index excludes
evidence, screenshots, local configuration, secrets, generated/vendor outputs and
unsupported formats. A hit is a navigation hint; read current source and tests.
For literals, complete match lists, complex/cross-repo searches, misses or diagnosed
graph failure use scoped normal tools. Shell override is the comment
`# --graph-tried`, never an rg flag. A repeated useful simple search redirects at
most once per query/session; precise tool options retain their semantics.

Graphify is a versioned **release snapshot**, not current development truth. Query
an available release graph with `graphify query "question" --graph <graph.json>`.
Inspect its manifest/commit/scope first. Never run Graphify watch/update/extract or
install its git hooks during ordinary development. Only the release pipeline builds
the graph from curated tracked code/docs. The default uses local AST plus explicit
document headings/links, not semantic LLM inference or embeddings/API billing.

Before UI work inspect the project's latest approved reference catalog. After
implementation inspect actual renders, reconcile all affected screen/state entries
with source fingerprints and real approval metadata, then run its reference gate.
Never auto-approve a changed screenshot. Preserve previous raw evidence externally.
Follow the project's spec, coverage, UI expert, final review and release policies.
