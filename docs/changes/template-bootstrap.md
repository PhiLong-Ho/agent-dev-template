# Change: reusable development workflow template

The user requested a GitHub template that future projects can generate from or
reference to adopt the established workflow. The user selected public visibility
and the name `PhiLong-Ho/agent-dev-template`. SPEC.md was written before tooling.
This is a new repository, not a change to DexDroid or a history migration.

## Scope and contract

FR-001 through FR-003 and NFR-001 through NFR-007 cover the replaceable reference
CLI, local initialization, explicit protection setup, upstream UI review/material
clarification, acceptance/coverage, exact-candidate review, evidence and release.
The template generalizes the workflow from DexDroid commit c5addcd; archive,
coverage and review tools retain their behavioral fault tests. No Android runtime,
credentials, global configuration, old approvals or device evidence is a prerequisite.

No product UI is introduced, so an upstream layout proposal is N/A here. The new
skills preserve the settled material-decision policy; final reviewers perform
independent skill table-top cases, separate from actual rendered app acceptance.

## Implementation

Project configuration uses argument arrays for quality/build adapters, structured
test results and artifact globs. Initialization clears inherited approvals and CI
checks actual repository identity. Local hooks and CI enforce the final digest;
remote protection is applied explicitly to the matching checkout. Attestations
remain records of actual sessions, not cryptographic reviewer identity.

CI checks Ubuntu/Windows, then exposes one required host check. Release build and
publish jobs independently validate reviews and main ancestry; local publication
validation binds current source, counts, reports, raw evidence and checksums before
GitHub calls. Interrupted drafts are not automatically overwritten. The reference
ZIP is source packaging; real signing/deployment/E2E adapters remain project-specific.

Onboarding and adoption instructions cover generated and existing projects.
Three Mermaid diagrams document workflow, ownership and the feature lifecycle.
README stays concise; release notes stay in CHANGELOG. No unattended AI service,
account subscription or unrestricted external authorization is installed.

## Verification and publication

See [compact evidence](../../testresults/0.1.0/template-bootstrap/summary.md) for
actual source fingerprints, commands, host outcomes, isolated initialization,
rendered diagram inspection, skill validation and raw archive availability.
Intentional failure/publication messages in unit fixtures are synthetic; inspect
the structured outer case outcomes. Unrun live-service/device/visual/performance
scenarios remain gaps. Final exact-candidate review identities/digest are in
[the approval record](../../reviews/approvals.json).

The initial review pair rejected an extension-filtered CI transfer that omitted
valid non-ZIP artifacts. The revised export transfers only the exact validated
publication set, independent of extension, with a wheel export/import acceptance
test. A stale skill guide path was corrected. Protection setup also refuses
existing or uninspectable rules instead of weakening another project's settings.
Changed contents require a new fresh review pair.

A later review identified Actions' default hidden-file exclusion. The dedicated
validated transfer now includes hidden files, and export/import acceptance uses a
dot-prefixed wheel. It still excludes unrelated raw/intermediate directories.

The first push may establish reviewed main only in the new empty remote, followed
by explicit protection and template activation. Subsequent changes use protected
PRs; no existing repository protection is weakened. Creating the template does
not authorize a version release or deployment.
