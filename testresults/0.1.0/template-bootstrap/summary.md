# Template bootstrap evidence — 2026-10-17

Scope: initial uncommitted source tree before first template publication. Actual
source fingerprints are in the raw host-results/source metadata; final staged
digest and two fresh identities are in [approvals](../../../reviews/approvals.json).
`uncommitted-bootstrap` is a declared absence of HEAD, not a tested commit claim.

- Host quality: 55 cases passed; zero failures/errors/skips in the outer structured
  result. Internal negative fixtures deliberately print failure/release messages.
- Requirements/coverage, documentation links, Ruff format/lint and both skill
  metadata checks passed.
- Isolated generated-project initialization changed identity, cleared the inherited
  approval fixture, preserved source and ran the same host suite successfully.
- Three Mermaid diagrams rendered and were author-inspected for labels/arrows and
  checked against tool ownership/flow. Mermaid CLI 12.0.0, local Chrome and Node
  20.15.1 were used; renderer dependencies reported newer engine requirements, but
  these actual renders succeeded. No app screenshots or pixel baselines are supplied.

Raw command logs, outcomes, diagram sources/PNGs and source/configuration are in
the ZIP identified by [archive.json](archive.json). At this pre-publication capture
it is **local-only**, accessible to reviewers at the descriptor path. Verify ZIP
and member hashes before inspection; originals and earlier failed attempts remain
ignored on disk. Git retains this concise summary and descriptor only.

Unverified at capture: live Actions/Ubuntu execution, remote upload/expiry, real
protection response and release publication, novice onboarding, project-specific
build/signing/E2E/device/app-visual/performance adapters. Hosted quality outcomes
after publication are available on the repository's Actions page and do not rewrite
this earlier capture scope. No version release was authorized by template creation.

Ten requirement mappings describe coverage intent/gaps, not complete execution of
all platforms/scenarios. The generic template includes no product/device claims.

[Change record](../../../docs/changes/template-bootstrap.md) ·
[Evidence policy](../../../docs/EVIDENCE.md)
