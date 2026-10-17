# Public archive privacy verification

Windows local run on 2026-10-17, branch `chore/public-archive-privacy-20261017`,
base commit `083daa9da7cb7c4d0100f1f1d7941b2e740932a2` plus the dirty candidate
recorded in archived `host-results.json` and `source.json`. Source/tests/contracts
were frozen through this run. Later edits record outcomes/archive access and correct
the privacy documentation scope described below; implementation/tests are unchanged.
This is current local execution, not a hosted Actions or publication result.

`python tools/quality.py --evidence testresults/0.1.0/runs/public-archive-privacy-20261017`
passed its requirements/privacy/coverage/docs gates and configured lint, formatting,
UI-reference no-product scope and tests. Actual counts: 108 cases, 106 passed,
2 skipped (POSIX-only private-mode/umask and Windows symlink privilege), zero
failures/errors/unexpected successes. The test command took 38.841 seconds;
complete command outcomes/timings are in the host record.

Focused privacy tests: 9 cases, 8 passed and 1 symlink-privilege skip. Focused
pipeline: 32 passed in 15.854 seconds. Synthetic tests reject contaminated source
before sealing and validly rehashed capture/device-log/nested-archive members
before any GitHub call; clean archives validate without extraction. Generic
private evidence media round trips remain accepted. No device/product UI,
performance or semantic private-text detection is claimed.

The initial five privacy/component/workflow Mermaid renders were inspected by the
author against their original source; the corrected current set is recorded below. `renders.json` binds document, Mermaid block and PNG SHA-256.
Architecture preflight reviewer and approach verdict are recorded in the
[change record](../../../docs/changes/privacy-cleanup.md#verified-archive-publication-guard-2026-10-17).
This does not replace either fresh final review or a new-version release review.

Verified local external bundles:

- [Host descriptor](host/archive.json): 17 files; ZIP SHA-256
  `8d63981446572db6c6ca850372979609e7deba5270ec195a62ce7eb5884c4562`.
- [Initial diagram descriptor](diagrams/archive.json), retained historical render set:
  16 files; ZIP SHA-256
  `cb807d24fb2fcdd981df7a637957564cd08f6e6dda2180f69382971dd04f3cc4`.

The original ZIPs are under `D:/Workspace/evidence-archives/agent-dev-template/0.1.0/`,
in `public-archive-privacy-20261017-host` and `public-archive-privacy-20261017-diagrams`.
`python tools/evidence.py verify` passed for each descriptor/ZIP after creation.
They are local-only, available to local reviewers and retained until owner cleanup;
no remote upload or durable cloud availability is claimed. Original ignored runs
remain under `testresults/0.1.0/runs/` with their command logs and diagram sources.

## Documentation scope correction after final review

Final review identified that the privacy flow and sequence diagrams implied routine
CI performs release archive-member validation after sealing. Actual
`.github/workflows/quality.yml` checks the raw current-run directory before generic
`evidence.py` packing/upload; the post-seal path/signature check belongs to
`release.validate`, also used for export and publication. `docs/PRIVACY.md` now
states and depicts these separate paths explicitly. No implementation, workflow,
requirement or test source changed for this correction. Previous final approvals
cannot approve the changed candidate; two new fresh reviews remain required.

The existing host result above is reused for unchanged executable/test/configuration
inputs: it is not a fresh full-suite run of the corrected documentation. Current
requirements, coverage, documentation, Ruff and whitespace checks were rerun for
this documentation correction; command outcomes and source comparison are retained
in `testresults/0.1.0/runs/public-archive-privacy-doc-correction-20261017/`.
No device, runtime or performance verification is added by this correction.

All five diagrams were regenerated in a fresh ignored run; the two privacy diagrams
changed and the three unchanged diagrams retain their source bindings. Author
inspected both changed renders. The current source/block/PNG hashes are in
`testresults/0.1.0/runs/public-archive-privacy-diagrams-20261017-correction1/renders.json`.
Root and final reviewers can inspect these current PNGs before approval.

[Current corrected diagram descriptor](diagrams-correction1/archive.json): 16 files;
ZIP SHA-256 `c584a87c8f8b55a435b973a06751721f5b7f443e16500f76e2433260771633ee`.
External archive:
`D:/Workspace/evidence-archives/agent-dev-template/0.1.0/public-archive-privacy-20261017-diagrams-correction1/evidence.zip`.
Archive/member verification passed after creation. Initial diagrams and their ZIP
remain intact; neither corrected nor initial bundles have been uploaded. Local
review access and retention until owner cleanup remain unchanged.

[Documentation correction check descriptor](correction-checks/archive.json) retains
actual rerun commands/outcomes and source comparison. ZIP SHA-256
`b83fc0ca209ff19f0e2e07e28f576bebe87a7a9aa998dd26a094ae622b852fcc`; external path
`D:/Workspace/evidence-archives/agent-dev-template/0.1.0/public-archive-privacy-20261017-doc-correction1/evidence.zip`.
Archive/member verification passed. This local bundle has not been uploaded.
Architecture impact for this correction is N/A: documentation now reflects existing
CI and release ownership/check ordering; no behavior or boundary changed.
