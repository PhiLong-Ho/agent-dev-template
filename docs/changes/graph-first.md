# Change: graph-first development and current UI references

## Contract

SPEC.md Story 4 and FR-004–FR-007 define shared local Claude/Codex hooks, bounded
current code-review-graph navigation, release-only Graphify and approved master
UI references. Stable WF mappings and concrete checks are in requirements.json;
the [feature contract](../specs/graph-first.md) owns scenarios and exclusions.
No product UI changes or new material layout decisions are introduced.

## Implementation

The shared stdlib hook uses the pinned CRG parser/store in an isolated interpreter,
hashes only curated eligible inputs, serializes refreshes with an OS lock, applies
time/size/context limits and permits diagnosed scoped fallback. Common literal and
line-number search options keep their results; only repeated bare-symbol searches
with useful in-scope hits redirect, at most once per query/session. No permission
approval is granted. Windows backslash paths retain their separators, including
relative, absolute and quoted paths; conflicting-directory acceptance prevents
redirecting a search using unrelated matches. The installer preflights existing settings, backs up changed
files with private backup modes/directories, preserves existing configuration modes
and unrelated policy, and uses a PowerShell-specific Codex command.

Graphify runs only in release builds from clean tagged reviewed tracked input.
Local AST plus explicit document headings/relative links connect through file
nodes to symbols. Release manifests distinguish AST and document file scope;
unsupported code retains a file node. Assets are source/checksum bound and required
by export/publication validation. No semantic LLM provider or embeddings are used.

The UI catalog tracks latest approved state/configuration PNGs with relevant source
hashes, dimensions, raw evidence and actual approval metadata. Its quality gate
checks integrity/freshness, not pixel correctness or reviewer identity. This starter
declares no product UI; adopting UI projects must configure actual sources/states.
No product baseline or human approval is manufactured.

## Acceptance and evidence

See [compact results and raw archive descriptor](../../testresults/0.1.0/graph-first/summary.md).
Tests use real pinned CRG/Graphify in isolated Git repositories and synthetic hook,
settings, reference and release-fault fixtures. They do not modify real user settings.
The separate explicitly requested local installation was exercised on this machine;
unrelated Claude settings were compared against backup, Codex native hook trust was
reviewed through its UI, and DexDroid was indexed without product-file edits.
Actual Codex nested exec callbacks exercised first-hit context, native denial on
a repeat and explicit comment override. The two successful tool results and actual
denial error are retained in raw evidence.

New architecture/feature diagrams were rendered and inspected for legibility and
correct separation of current-code, release-snapshot and visual-reference flows.
That inspection is not a product screenshot approval.

Initial attempts exposed SQLite handle leaks on Windows and non-idempotent spacing;
fixes preserve cleanup and repeat-install assertions. A Graphify query test initially
assumed more than its depth-two traversal. Acceptance now verifies linked file
discovery and an actual longer document-to-symbol path, rather than pretending
one query traverses an unlimited graph. Earlier failing host evidence remains raw.

## Delivery and remaining scope

Feature branch from bae6bbc0373fd3c1d08c32e4d3fa1cebd7287ede. Two fresh independent
exact-candidate reviews and the staged gate precede push; protected PR/host CI
precede merge. No release is requested here. Hosted release publication, Claude native callback E2E, Codex edit/Stop callbacks, cloud orchestration and actual product UI/reference
acceptance remain outside this change's verified scope. Existing sessions may
need restart; new users must review native Codex hook trust themselves.
