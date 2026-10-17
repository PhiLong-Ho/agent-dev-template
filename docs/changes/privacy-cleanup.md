# Private evidence cleanup and prevention

## Contract and architecture preflight

Owner requested removal of private app screenshots and explanation of historical
cleanup. WF-PRIVACY-001 owns privacy prevention. Spec/mapping updated before code.
Architecture expert `/root/privacy_architecture` inspected the actual remote-derived
DexDroid candidate and approved bounded delivery/tooling changes. Published DexDroid
workflows upload all testresults, unlike its newer unpublished dirty workspace;
that is the confirmed exposure path. The template already scopes current runs.
New flow: device capture stays private; safe source/current host results pass
indexed-path plus actual-input guard, then upload. Failure withholds upload.
No app/UI/state/IPC changes; UI preflight is N/A. Existing dirty app work is untouched.

DexDroid: historical testresults purged in a separate mirror, not pushed. Schema-2
withdrawal records unavailable evidence honestly, preserving schema-1/retained-byte
checks. Broken historical links now point to an explicit withdrawal notice.
Template: guard current host inputs before existing packaging, including release
preparation; private local pack remains generic. Public synthetic references still
require actual content review. Guard is a bounded path/signature backstop.

## Remote containment and remaining authorization

DexDroid audit found 2,145 tracked test PNGs on published main; all 26 potentially
affected Actions evidence artifacts were deleted. One downloaded artifact confirmed
2,145 PNGs. Six remaining Android release artifacts contain binaries/reports, and
release assets list no screenshots. Template has no historical tracked images.
A fresh mirror rewrite removes the entire historical testresults tree, including
potentially private logs/metadata/Markdown. Only inspected safe current notices
are restored. Local private audit/backups are not public Git.

The history replacement is PREPARED, NOT PUBLISHED. Main blocks force pushes.
A user-approved maintenance exception, two fresh current-candidate approvals,
controlled release-trigger suspension/restoration, leased ref replacement and
remote verification are required. Historical review digests/commit bindings become
stale; published APKs are not rebuilt or falsely resealed. GitHub Support must
purge cached/PR references, and old clones must not reintroduce tainted history.
No third-party message or Support ticket has been sent.

## Verification plan and exclusions

Run new negative/positive privacy and withdrawal tests, complete host quality,
requirements/coverage/docs/Ruff checks and inspect the privacy flow render. No
device suite is needed for tooling-only changes. Record actual outcomes, source
fingerprints and evidence access for reviewers before requesting final approval.
No semantic DLP or proof of deletion from third-party clones is claimed.

## Recorded local verification

Configured quality: 104 cases, 102 passed and two platform skips (private-mode/umask and Windows symlink privilege); no failures/errors.
Requirements/coverage/docs/Ruff and native Git-hook negative/positive checks pass.
Two privacy diagrams were rendered and visually inspected; identical Mermaid
source is maintained in both repositories. No Android runtime tests are needed
for these delivery/documentation-only changes. Dex app source remains unchanged.

Initial host checks exposed a hook fixture missing the new helper module and
its bytecode ignore; both were fixed to model the real installed hook. Removing
historical evidence also required honest withdrawn release-note links, with
separate tests preserving retained-version summaries. Failures remain in local
review evidence; no assertions were weakened. The template final host run is
privacy-candidate-final2; later edits are only YAML trailing-space cleanup and
recorded outcomes, with no executable/test changes.

Publication and history replacement remain pending; final approvals are recorded
separately rather than predicted here. The cleanup local clone has zero original
testresults object paths over all rewritten refs; only packaged application icons
remain as historical PNGs. Four read-only PR refs require GitHub Support cleanup.

## Verified archive publication guard, 2026-10-17

The reusable release path already checked current-host files before sealing, but
its later validate/export/publish path checked integrity without member privacy.
WF-PRIVACY-001 now requires both boundaries. `check_privacy.public_member_errors`
owns the existing path/signature policy; release validation inspects the verified
manifest's relative paths and first 16 uncompressed bytes without extracting files.
The general private-local archive tool remains governed by integrity checks.

Architecture preflight `/root/release_archive_privacy/template_archive_preflight`
approved this approach at `2026-10-17 14:06:58 UTC`, after inspecting current graph,
contracts, source/tests and diagrams. No schema, product state, process, persistence
or UI boundary changes. It required preservation of integrity/safe-name/link/empty
checks and separate directory/member guards. No material departure was introduced.
This is implementation preflight, not a release or final-candidate approval.

Synthetic checks cover clean archives without extraction, contaminated source
rejected before sealing, and validly rehashed capture/device-log/nested-archive
members rejected before any GitHub call. Focused privacy tests: 9 total, 8 passed,
1 Windows symlink-privilege skip; pipeline tests: 32 passed in 15.854 seconds.
Requirements, generated coverage, documentation and targeted Ruff checks passed.
The existing generic evidence round-trip retains synthetic media privately.

Raw diagram sources/PNGs/logs and SHA-256 bindings are local-only at
`testresults/0.1.0/runs/public-archive-privacy-diagrams-20261017/renders.json`; author inspected the five
privacy/component/workflow renders against source. They are available to local
reviewers, retained until owner cleanup, and have not been uploaded. Complete host
verification passed: 106 cases passed, 2 platform skips, no failures/errors; the
test command took 38.841 seconds. [Current local reviewer evidence](../../testresults/0.1.0/public-archive-privacy/summary.md)
records verified external archives, source binding and remaining gaps before final reviews.
No device, product UI, performance or semantic private-text detection is claimed.
