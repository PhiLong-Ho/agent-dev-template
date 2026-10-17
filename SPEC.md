# Feature Specification: Agent development workflow template

**Created**: 2026-10-17
**Status**: Initial reusable contract; execution evidence is recorded separately.
**Input**: Reuse the spec-driven development and release workflow in future projects.

## User Scenarios & Testing

### User Story 1 — Start a project (Priority: P1)

Generate a repository, configure project commands and follow a concise onboarding
route without carrying Android code, credentials or historical approvals.

**Independent Test**: Initialize a temporary copy, run host checks and inspect the
changed configuration. Apply protection to an authorized GitHub repository.

**Acceptance Scenarios**:

1. **Given** a fresh checkout, **When** host checks run, **Then** real reference
   tests, formatting, lint, document links and requirement freshness are checked.
2. **Given** a generated project, **When** initialized, **Then** its name/repository
   change and inherited approvals are removed; new contents need fresh reviews.
3. **Given** an authorized repository, **When** protection is applied, **Then** PRs,
   an up-to-date `host` check, resolved conversations and administrator enforcement
   are required, and force pushes/deletions remain disabled.

### User Story 2 — Develop with traceable decisions (Priority: P1)

Write a spec, resolve consequential design decisions, implement and verify the
result before independent review. Preserve concise, inspectable evidence.

**Independent Test**: Introduce unmapped/stale tests, alter an approved candidate,
and corrupt archived evidence; gates must reject each case.

**Acceptance Scenarios**:

1. **Given** a UI change, **When** a material decision remains after expert review,
   **Then** present the proposal and ask the user before dependent implementation.
2. **Given** an exact authorized correction, **When** no material ambiguity emerges,
   **Then** a brief expert proposal permits implementation without repeated approval.
3. **Given** changed tests, **When** coverage has not been reconciled/refreshed,
   **Then** validation fails; mapping never implies execution or visual approval.
4. **Given** fewer than two fresh approvals or changed candidate contents,
   **When** push/release checks run, **Then** publication is blocked.

### User Story 3 — Publish inspectable releases (Priority: P1)

Build a configured artifact and publish it with current test results, coverage,
changelog notes and durable raw evidence, only after passing release gates.

**Independent Test**: Build a local release fixture, inspect reports and alter
source/result/artifact hashes; publication must refuse before remote mutations.

**Acceptance Scenarios**:

1. **Given** a matching version tag/changelog and passing current checks, **When**
   packaging runs, **Then** Markdown/JSON reports, artifacts, raw ZIP, descriptor
   and checksums bind to the same source and workflow run.
2. **Given** failed/skipped/unrun checks, **When** reporting runs, **Then** actual
   counts and gaps remain explicit; failed/missing results block publication.
3. **Given** corrupt/missing/mismatched evidence or an existing published release,
   **When** publish runs, **Then** no release is overwritten or made public.

### User Story 4 — Use graph-first development (Priority: P1)

**Independent Test**: Feed Claude/Codex hook payloads to an isolated repository,
change/delete code and exercise useful hits, misses, overrides and tool failures.
Release fixtures must index current code/documents and reject excluded inputs.

**Acceptance Scenarios**:

1. Given any coding/review session, when a prompt, code search or edit occurs,
   then code-review-graph refreshes locally within a bound and supplies navigation
   and change-impact context; unavailable/stale graphs disclose fallback.
2. Given a simple repeated symbol search with a fresh graph hit, when the hook
   redirects it, then it returns valid deny JSON and useful locations, with an
   explicit comment override and bounded retries. Literal/complex/cross-repository
   searches and graph misses remain available. Hooks never approve permissions.
3. Given an authorized local installation, when run twice, then both clients use
   one maintained implementation, existing unrelated settings survive, backups
   exist, and Codex's native hook trust remains a separate user action.
4. Given a release build, when Graphify runs, then only current eligible tracked
   code/documents enter a checksummed release snapshot. Routine hooks never
   regenerate Graphify. Documentation indexing states its structural scope.
5. Given a UI change, when preparing acceptance and final review, then the latest
   approved reference catalog is reconciled for affected screens/states; missing
   or stale references block the configured reference gate. The starter declares
   that no product UI exists rather than fabricating screenshots or approval.

### Edge Cases

- Templates copy files, not account authorization, secrets or repository settings.
- CI validates attestations; it cannot authenticate reviewer independence or run
  AI reviewers without a configured agent session/provider. Never fabricate them.
- Unavailable agent/device/service checks remain unverified. Missing permissions
  or plan support can prevent GitHub branch protection; report the actual error.
- Local archives remain local until an authorized upload; target URLs are pending.

## Requirements

### Functional Requirements

- **FR-001**: A small working CLI example MUST greet a trimmed nonempty name,
  preserve Unicode and reject blank input. It demonstrates acceptance testing;
  it is replaceable project code.
- **FR-002**: Initialization MUST validate project/repository identifiers, update
  project configuration and invalidate inherited approval records without deleting
  user source or changing repository history/settings implicitly. CI MUST reject
  a configured repository identity that differs from its actual repository.
- **FR-003**: GitHub setup MUST apply the configured strict PR/host protection
  within the authorized repository and expose failures rather than claim success.
  Existing protection MUST be preserved for explicit reconciliation, not overwritten.

- **FR-004**: Shared Claude/Codex hooks MUST automatically consult locally refreshed
  code-review-graph for prompts, code searches/edits and review impact. Bound time,
  context, traversal, file sizes and concurrency. Parameterized search results are
  hints, never exhaustive literal results. Windows path separators MUST survive parsing; ambiguous scopes MUST NOT deny
  the original search. Missing, failed, corrupt or concurrently
  updating graphs MUST allow explicit diagnosed fallback; no permanent search loop.
- **FR-005**: User-scope installation MUST be idempotent, preserve unrelated settings
  and permission policy, preserve existing file modes, create private backups and
  private new configuration files, avoid repository-controlled command
  execution and leave native hook trust intact. Both clients use valid event JSON.
- **FR-006**: Graphify generation MUST run only during explicit release builds from
  current tracked eligible code/docs and project build configuration, with source/hash provenance and required
  checksum-bound assets. Exclude evidence, screenshots, local/secret configuration,
  binaries, caches and generated/vendor output even if tracked. AST extraction and
  deterministic document headings/links MUST connect to referenced code nodes and
  be labeled distinctly from optional
  LLM semantic extraction. No automatic paid provider calls are introduced.
- **FR-007**: A master UI reference catalog MUST identify latest approved renders
  per screen/state/configuration, source fingerprints, raw evidence location and
  actual reviewer identity/date. Validation MUST reject missing/altered references
  or changed relevant UI sources. Updates require inspection and actual approval;
  preserve history in evidence archives. No-UI projects explicitly declare scope.

### Nonfunctional Requirements

- **NFR-001**: Spec and observable acceptance precede implementation. UI expert
  proposals precede dependent UI work; material ambiguity waits for user decisions.
  Shared design/state, accessibility, recovery and performance constraints apply
  across relevant surfaces. Rendered acceptance and performance remain separate.
- **NFR-002**: Stable requirement IDs, concrete checks, dimensions and gaps MUST
  stay reconciled. Every test edit/addition/removal refreshes generated inventory
  and canonical source fingerprints; stale or unmapped checks fail validation.
- **NFR-003**: Exactly two fresh independent reviewers MUST approve the completed
  candidate digest before each push/release, including initial template publication.
  Any content change except the approval record invalidates both. Protected main
  requires a PR after the first reviewed creation of an empty repository.
- **NFR-004**: Raw runs MUST preserve bytes in ignored versioned folders and verified
  archives. Git stores concise summaries/descriptors/reports. Reject corrupt,
  missing/unexpected/unsafe members, Windows sanitization aliases/device names,
  source mutations and overwrites. Preserve failures and originals; disclose scope,
  local-only/pending/expired availability and configured retention.
- **NFR-005**: Host execution MUST validate configured argument-array commands,
  preserve raw logs and structured outcomes/source provenance, and return failure
  for nonzero commands or invalid/missing test outcomes. No shell interpolation.
- **NFR-006**: Release MUST require current successful host checks and validated
  test counts, tag/version/changelog agreement, source/coverage/report/artifact/
  archive bindings and checksums before remote calls. Attach Markdown/JSON reports
  and raw evidence, link changelog/release/workflow, and refuse published overwrite.
  CI transfer MUST preserve the exact validated publication file set regardless
  of artifact extension or dot-prefixed filename, excluding intermediate/raw directories.
- **NFR-007**: README stays concise; maintain onboarding, design, architecture and
  owning feature diagrams. Check links, lint/format and documentation integrity.
  Documentation paths MUST normalize filesystem aliases consistently; Windows
  short/long path forms MUST return link findings rather than crash validation.
  Mark device/E2E/visual/performance gaps; never silently bless screenshot baselines.

### Key Entities

- **Project configuration**: replaceable argument-array gates/build commands and artifacts.
- **Requirement mapping**: stable criterion, concrete checks, dimensions and explicit gaps.
- **Candidate**: canonical Git path/mode/blob digest excluding only its approval record.
- **Evidence run**: commands, outcomes, source fingerprints, configuration and raw bytes.
- **Release package**: artifacts, current report/evidence and verified checksum manifest.

## Success Criteria

### Measurable Outcomes

- **SC-001**: A fresh checkout runs the documented host command without a device.
- **SC-002**: Fault tests reject stale coverage/approvals and altered evidence/releases.
- **SC-003**: Generated repositories have an explicit adaptation/activation checklist.
- **SC-004**: Current release reports show actual counts and remaining requirement gaps.

## Assumptions

Python 3.11+ runs workflow tooling; project languages may differ. GitHub CLI handles
authorized repository setup/publication. The agent environment must support fresh
independent reviewers. The optional explicitly invoked local installer configures user hooks and graph
skills; it installs no credentials, API billing or unattended agent loop. Project-specific build,
signing, E2E/device and visual adapters must be configured and verified explicitly.
