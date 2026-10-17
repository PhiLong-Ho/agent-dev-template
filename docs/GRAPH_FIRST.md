# Graph-first coding and review

The shared Python hook works with Claude Code and local Codex sessions. It uses
code-review-graph 2.3.6 for current code structure. Graphify 0.9.16 creates a separate
code/document snapshot **only during release builds**. Graphs guide source selection;
they do not replace reading code, requirements, tests or two independent reviews.

Install explicitly on a developer machine (never run the user installer in CI):

~~~sh
python -m pip install -r requirements-graph.txt
python tools/install_graph_first.py
~~~

Alternatively isolate CLIs with uv tool install code-review-graph==2.3.6 and
uv tool install graphifyy==0.9.16; the installer finds the CRG environment. It copies
three maintained Python files into ~/.local/share/agent-graph-first/, merges
~/.claude/settings.json and ~/.codex/hooks.json, and installs the graph-first
skill/instructions for both clients. Unrelated handlers, permissions, config.toml,
plugins and notifications survive. Recognized legacy unconditional CRG-update and
copied smart-grep handlers are migrated. Existing file modes are retained; new configuration files and backup files use
private modes, and backup run directories are private on POSIX. Windows ACLs beyond
normal user-directory inheritance are not certified. Changed originals are backed up under
the runtime's backups/timestamp-id/. Rerunning is idempotent; source updates
require rerunning the installer.

Restart clients. In Codex use **/hooks** to inspect and trust the four installed
definitions. New/changed definitions need native review; installation neither edits
trust state nor bypasses it. Command hooks are for local orchestration; cloud and
specialized tool paths may not support them. Verify actual client events before
claiming enforcement. Instructions do not prove a hook executed.

## Development behavior

SessionStart supplies guidance. UserPromptSubmit refreshes CRG and shows bounded
direct neighbors for changed tracked files. PreToolUse refreshes before supported
edit tools and simple symbol searches. Stop refreshes without requesting continuation.
The worker parses changed content, removes deleted file nodes and rebuilds FTS with
the CRG parser/store. No embeddings, LLM calls, background watcher or repository-
controlled shell command is run.

~~~sh
python tools/graph_first.py refresh
python tools/graph_first.py query SymbolName
python tools/graph_first.py impact src/example.py
~~~

Run in the intended repository or subdirectory. Global skills contain an absolute
installed command usable in other repositories, including existing projects.
Root/worktree-isolated caches live under ~/.cache/agent-graph-first/; GRAPH_FIRST_HOME
can relocate them. An OS lock serializes access without stale PID locks or queues.
Workers have an eight-second timeout and one parser worker. Inputs are capped at
5,000 files, 2 MiB per file and 40 MiB total; context is capped at 6,500 characters,
node/edge counts and SQLite VM work. Freshness binds eligible content hashes.
Failed, timed-out or changed builds never become fresh. Unsupported formats are
listed in fresh.json and retain file-level coverage in release snapshots. Inspect
refresh.log on failure.

Backslash search targets preserve separators and add scoped context; their original
tool execution is retained because Git Bash and PowerShell escaping can differ.

Only bare identifiers in simple rg/grep/ripgrep commands or Claude Grep pattern/path
requests are redirected. First hit adds context and allows search; the second same-
symbol hit per session returns valid deny JSON with locations and neighbors. A
further retry is allowed. Common line-number/case/literal options add context while preserving search results.
Other precise options, regex/compound commands, non-code file reads,
non-code and cross-repository searches retain their semantics. Append the shell
**comment # --graph-tried**, never a command flag, to override. Misses, missing
dependencies, corrupt DBs, lock contention and timeouts allow diagnosed scoped
fallback. No hook grants permission. Hits are hints, not exhaustive literal results.

## Release-only code/document graph

The template enables release.knowledge_graph in project.json. The release build
first validates clean reviewed tagged source and current checks, then copies only
eligible **tracked** files to an isolated corpus and invokes Graphify local AST.
It adds deterministic file nodes, Markdown headings and explicit relative links.
RST/TXT/AsciiDoc are inventoried; unsupported code retains a file node.
**This is structural document indexing, not LLM semantic extraction.** Semantic
inference needs an explicitly configured provider and a separate cost/data decision.

The release attaches knowledge-graph.zip (graph.json and manifest.json) plus
knowledge-graph-manifest.json, covered by publication checksums. The manifest lists
input hashes, commit, tag, tool version and scope; the report links the graph.
Download and verify checksums, extract into an ignored directory, then query:

~~~sh
graphify query "question" --graph graphify-out/graph.json --budget 1500
~~~

Graphify query uses a bounded depth-two neighborhood; follow the linked file or
use graphify path between document/symbol labels for a longer route. Explicit
document links connect through file nodes to AST symbols.

Inspect the manifest: releases may lag the working tree. Hooks never run Graphify,
download releases, or install post-commit/post-checkout/watch automation. Do not use
those upstream auto-update installers with this policy. Disabling release graphs
is a reviewed project adaptation, never a workaround for failed extraction.

## Exclusions and scope

Both graphs exclude testresults, screenshots/UI references, local agent/editor
configuration, secret filenames, caches, vendor/generated output and binaries,
even if tracked. Images are excluded by the text-extension allowlist. Source, versioned build/workflow configuration and
design/spec/onboarding documents remain eligible. Dependency lockfiles are excluded. The .graphignore file adds
relative case-sensitive fnmatch exclusions; it cannot re-include mandatory exclusions.
Filename rules do not sanitize a repository: never commit credentials. Linked,
non-UTF-8 or over-budget inputs cause explicit fallback/failure.

Primary references: [article](https://dev.to/mir_mursalin_ankur/graphify-code-review-graph-build-a-self-updating-knowledge-graph-for-claude-code-and-other-ai-j1m),
[CRG](https://github.com/tirth8205/code-review-graph),
[Graphify](https://github.com/Graphify-Labs/graphify),
[Codex hook events and trust](https://learn.chatgpt.com/docs/hooks),
[Claude hook protocol](https://code.claude.com/docs/en/hooks).
