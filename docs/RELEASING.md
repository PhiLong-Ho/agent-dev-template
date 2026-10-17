# Release procedure

Only release within user authorization, from reviewed contents merged into protected
main. Change project.json version and add a nonempty matching CHANGELOG section
on a branch; update specs/tests/coverage and complete quality + two fresh reviews.
Wait for protected PR checks and merge. Tags use stable `vMAJOR.MINOR.PATCH`.

```sh
git tag v0.1.0
git push origin v0.1.0
```

The release workflow checks the actual tag commit's approvals and main ancestry,
runs current host gates, executes configured build commands, and packages only
configured flat artifact globs. The default ZIP contains the reference Python CLI;
replace it with your real build/signing/verification adapter before product releases.
No Android signing/deployment behavior is implied by generic packaging.

It generates release-report.md/json with actual outcomes, denominator excluding
skips, mapping counts/gaps and changelog/release/workflow links; raw evidence ZIP,
descriptor and checksum manifest bind reports, test sources, coverage and source.
CI exports the exact validated flat publication set (all configured extensions,
including dot-prefixed files)
to a dedicated transfer directory; raw/build/intermediate folders are excluded.
Both build and publish jobs check approvals. Publish validates locally before any
GitHub call, creates a draft with verified assets, then publishes it. Existing
releases (including drafts after interruption) are never overwritten automatically;
inspect a partial draft and resolve deliberately, or use a new version.

Current CI failure logs are uploaded as Actions evidence only; they do not become
passing release evidence. Reports/raw ZIPs are attached to the release. Copy a
small report/descriptor into testresults/<version>/<change>/ in a separately
reviewed follow-up when a tracked index is needed; CI never commits to main.
Do not reuse old device/UI/performance runs as current passes.

Local dry runs use `python tools/release.py build --tag v0.1.0 --workflow-url URL --output artifacts/release`,
then `verify`; build requires clean tagged source.
Tests mock GitHub and do not authorize a real publish. Manual Actions dispatch
accepts an existing tag and applies the same gates.

## Release knowledge snapshot

The default release.knowledge_graph flag requires pinned graph dependencies and
[release-only Graphify](GRAPH_FIRST.md). The build creates code/doc graph ZIP and
input manifest, validates source/file coverage and includes both in sealed exports
and release checksums. Missing/failed extraction blocks publication. Never install
Graphify commit/checkout/watch hooks. The graph uses local AST and explicit document
headings/links; it does not claim semantic inference.
