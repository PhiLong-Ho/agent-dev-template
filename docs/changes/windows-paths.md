# Change: Windows short-path documentation validation

## Contract

The first hosted quality run passed Ubuntu but failed Windows. The retained
[run](https://github.com/PhiLong-Ho/agent-dev-template/actions/runs/39013106332)
contains 55 passing Ubuntu cases and 54 passing/one error on Windows. Its real
Windows temporary directory used RUNNER~1 while root.resolve() expanded the long
name. The checker called relative_to() on an unresolved document path and crashed
instead of reporting the two deliberately invalid links in its acceptance fixture.

NFR-007 / WF-DOC-001 now explicitly requires consistent alias normalization.
This is validation tooling; no UI proposal or product behavior change applies.

## Implementation and acceptance

Resolve each document path before comparing/reporting it against the resolved
repository root. Reject outside document inputs before reading them. Preserve
the existing broken/outside-link assertions; add a deterministic short/long alias
fixture that requires actual link findings without a crash. Reconcile requirement
checks and both generated coverage files for the test change.

See [current compact evidence](../../testresults/0.1.0/windows-paths/summary.md)
for local commands/source fingerprints and original hosted archive bytes. Prior
failures remain failures. Hosted verification after this capture is recorded in
the PR/Actions run, not inferred from local counts.

## Delivery

Work on fix/windows-test-portability from fe5117ccfa84ced629b391823b3a9eac3b258bc2;
new fresh reviews and the candidate gate precede push. Merge through a PR only
after required host succeeds. Main protection remains enforced; no bypass or
direct main push. Actual identities/digest are in reviews/approvals.json.
