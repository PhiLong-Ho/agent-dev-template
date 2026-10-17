# Graph-first workflow verification

Windows 11, Python 3.13.5, code-review-graph 2.3.6, Graphify 0.9.16;
Claude Code 2.1.181 and Codex CLI 0.162.1 installed locally.

- Candidate host run: 76 passed, 0 failed/errors and 1 explicitly skipped POSIX-only case; formatting, lint,
  requirement/coverage/document checks and UI reference scope passed. Raw
  source.json/host-results.json bind the actual dirty candidate file hashes from
  bae6bbc0373fd3c1d08c32e4d3fa1cebd7287ede; current files matched after the run.
- Real CRG fixtures verify edits/deletions and test relationships. Real Graphify
  fixtures verify curated release inputs, document-to-symbol paths and graph asset
  validation/export. Corrupt/resealed metadata is refused before remote mutation.
- Isolated settings fixtures verify idempotence, backups, preservation, malformed
  input and native shell execution with spaces. The authorized real installation
  preserves unrelated Claude settings; Codex native /hooks trust was reviewed.
- Actual Codex code-mode nested exec: first useful hit supplied context, repeat
  was denied, comment override ran. Final raw tool results/denial are retained.
  Repeated native Windows-backslash searches retain original execution and scoped
  graph hints. Host regression covers relative/absolute/quoted paths with a
  conflicting directory; resealed contradictory graph metadata is rejected.
  DexDroid's current graph includes 131 eligible source/config files; no product
  files were edited. Direct warmed-cache samples before build-config expansion
  measured 228-266 ms on DexDroid (five calls, excluding client shell/model time);
  these are limited samples, not a performance certification.
- Architecture/feature diagrams were rendered and inspected. No product UI exists
  in this starter; no product screenshot baseline/approval is claimed.

Commands: python tools/quality.py --evidence
 testresults/0.1.0/runs/20261017-graph-first-complete-host;
python tools/coverage.py check; python tools/check_docs.py;
python tools/install_graph_first.py; skill quick_validate.py; recorded Mermaid CLI
renders. Earlier captured host failure remains in the archive; subsequent runs are
separate. Fixture console publication messages use mocked remotes, not real releases.

[Archive descriptor](archive.json) identifies the local-only verified 112-file ZIP
at artifacts/evidence/graph-first-private/evidence.zip. Original bytes remain in
ignored runs. Verify with python tools/evidence.py verify --archive
artifacts/evidence/graph-first-private/evidence.zip --descriptor
 testresults/0.1.0/graph-first/archive.json. No upload is implied by local storage.

POSIX private-mode acceptance is explicitly skipped on Windows and must pass
required Ubuntu CI before merge. Windows checks also retain byte-identical UTF-8/CRLF
configuration backups.

Unverified: Claude native callbacks; Codex edit/Stop callbacks; cloud/specialized
paths; real product UI and full rotation/input/lifecycle matrix; hosted release
publication. Required Windows/Ubuntu host CI follows the reviewed PR and records its
own evidence. No release was requested. Existing client sessions may need restart.
