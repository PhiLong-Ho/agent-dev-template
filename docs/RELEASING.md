# Release procedure

Only release within user authorization, from reviewed contents merged into protected
main. Change project.json version and add a nonempty matching CHANGELOG section
on a branch; update specs/tests/coverage, complete quality, obtain
[release architecture approval](#release-architecture-review), then complete two
fresh final reviews.
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

## Release architecture review

Every new version candidate needs a **fresh read-only architecture expert** after
checks/evidence and before the two fresh final code reviewers. This includes
patch, prerelease and documentation-only versions. Task-level N/A and earlier
implementation preflights do not waive it. The expert cannot serve as a final
reviewer for that candidate.

Review cumulative changes since the preceding published tag/commit (or the full
baseline for a first release), current whole-product/component/feature diagrams
and actual source/tests. Inspect ownership, interfaces/trust boundaries,
lifecycle/cancellation/stale work/rollback, queues/concurrency, persistence,
compatibility, security/privacy, performance, dependencies and delivery/evidence.
Identify diagram drift, known failures, verification gaps and blocking findings.
Use private local device evidence and reviewed synthetic public references.

Freeze and stage the inspected inputs first; record their exact pre-attestation
Git tree/digest and reviewed scope. Record actual expert identity/UTC time, target
version, previous release baseline, findings, explicit verdict, blockers and
residual gaps in the release change record using
[the review template](templates/release-architecture-review.md). Missing approval
or unresolved blockers prohibits the agent from creating/pushing the release tag,
dispatching release, release signing or publishing. Resolve consequential uncertainty
with the user; a documentation record alone is not an approval.

After approval, add only its faithful attestation and freeze the final candidate.
Both fresh final reviewers verify that this is the only change from the inspected
snapshot, then approve the final canonical digest **including** the architecture
record. `reviews/approvals.json` remains the sole digest exclusion. Any other
changed input (including version/spec/docs) requires renewed fresh architecture
review; any changed final candidate requires a new final review pair. Do not
claim the architecture record reviewed a digest that includes itself.

A transport/publication retry may reuse the real approval only for the same
version and byte-identical candidate, with exact identity and retry reason
recorded. A new version or changed inputs need fresh approval. Existing draft/
published-release retry restrictions still apply; this never permits overwriting
a published version. Keep the concise architecture verdict/findings available to
final reviewers and link its safe record from release evidence/notes as applicable.
Do not edit sealed generated reports to invent architecture verification.

This is a mandatory **agent-session** checkpoint. Existing CI still runs its
current automated gates; this change adds no unattended reviewer or CI system
that authenticates architectural judgment.
