# Spec-driven development contract

Use the graph-first skill for coding and review: consult current CRG before broad
searches/edits; preserve diagnosed fallback. Graphify refreshes only at release.
Read SPEC.md, docs/DESIGN.md, docs/ARCHITECTURE.md and CONTRIBUTING.md.
Use `.agents/skills/project-change/SKILL.md` for project changes.

1. Work on a feature/chore branch. Update SPEC.md first and the owning Spec Kit-style
   feature contract; reconcile stable WF-* requirements, acceptance and gaps.
2. Before user-facing interaction changes, use the UI review skill to create a
   focused fresh expert. Present before/after task steps, meaningful states/tradeoffs
   and a sketch for layout/navigation. Clarify unresolved material choices with the
   user and wait before dependent work; continue independent work. Exact authorized
   or delegated corrections need no repeated approval. Record decisions and revisit
   material departures. Proposal review does not approve actual renders or latency.
3. Implement, then update behavior-focused acceptance/E2E tests. Preserve shared
   design/state and ownership invariants. Maintain affected high-level/feature diagrams.
4. Every test addition/edit/removal MUST reconcile concrete checks in
   docs/requirements.json, run `python tools/coverage.py update`, inspect and commit
   both generated coverage files. Mapping is not execution or scenario completion.
5. Maintain [latest approved UI references](docs/ui-reference/README.md) for every
   UI change; inspect renders and record real approval before updating hashes.
   Run `python tools/quality.py`, affected integration/device/E2E checks, inspect
   actual UI renders and measure performance where applicable. Record exclusions;
   fix causes instead of weakening tests or accepting unreviewed screenshot baselines.
6. Archive raw bytes under ignored testresults/<version>/runs/<run>/ and external
   verified ZIPs. Track only concise summaries, descriptors and reports. Preserve
   failed attempts/originals. Never force-add new raw evidence. Give reviewers archive
   access and actual source/configuration, commands/results, review scope and gaps.
7. Before ANY push or release, stage the completed candidate and obtain its digest.
   Create exactly TWO fresh independent review agents with no inherited history
   (`fork_turns: none` where supported). Give each the candidate/spec/tests/raw
   evidence and review instructions, not the author's or other review's conclusions.
   Each must inspect and explicitly approve that exact tree. Resolve blockers and
   obtain a NEW pair after any candidate change. Never fabricate/reuse approvals.
8. Record actual identities/timestamps/scope/verdicts in reviews/approvals.json,
   stage it and run `python tools/review_gate.py check`. Only then commit and perform
   authorized delivery. Protected main requires PR + up-to-date host check; no bypass.
   The sole bootstrap exception is the first reviewed push to a new empty repository,
   immediately followed by protection setup. Never use it for an existing repository.
9. Release only when requested. Generate current Markdown/JSON reports with explicit
   denominator/gaps and changelog/release/workflow links; verify evidence/artifact/
   source bindings before publication. Never overwrite a published release.

Use explicit UTF-8 and authoritative formatters. Keep README concise, release notes
in CHANGELOG, onboarding and diagrams current. No global configuration, secret,
human/visual approval, account permission or Codex Goal is implied by this policy.
Create a Goal only when explicitly requested. If fresh reviewers are unavailable,
leave work reviewable and do not push/release. CI validates attestations, not identity.

## Review focus

Flag missing requirement coverage, divergent surface behavior/style, UI-thread
blocking, unbounded work/input queues, stale lifecycle identities, swallowed
failures, unsafe rollback and unsupported visual/performance/pass claims.
