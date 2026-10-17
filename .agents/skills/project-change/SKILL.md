---
name: project-change
description: Implement or maintain this repository using spec-first contracts, requirement coverage, evidence archiving and exact-candidate independent review. Use for project features, fixes, tests, tooling, documentation and releases.
---

Use the sibling graph-first skill for coding and review. Refresh/consult CRG;
Graphify is generated only at release, never per commit/turn.

Read docs/architecture/README.md and the owning feature architecture before
implementation. Record impact for every task; use the sibling architecture-review
skill and a fresh expert for possible architectural or uncertain impact. Record
findings/decision and revisit material departures; this is separate from UI and
the two final approvals.

Use docs/CODING_PRACTICE.md for targeted iteration, complete candidate checks,
source-bound evidence reuse, timings/rerun reasons and a freeze before final reviews.
Keep reusable guidance aligned with adopting projects and platform details there.

Read AGENTS.md, relevant SPEC/feature contract, docs/WORKFLOW.md, DESIGN.md,
ARCHITECTURE.md and CONTRIBUTING.md. Honor the user's scope and prior decisions.
Work on a feature/chore branch. Write observable spec/acceptance first; reconcile
stable requirements, dimensions and gaps. Invoke the sibling ui-review skill for
user-facing interaction work before dependent implementation. Resolve material
ambiguity with the user; exact authorized corrections need no repeated approval.

Implement shared behavior/state/style, then behavior-focused acceptance/E2E tests.
Every test addition/edit/removal reconciles concrete checks and refreshes both
generated coverage files. Run configured quality gates and applicable integration/
device/visual/performance checks; mappings and historical evidence are not passes.
For UI changes reconcile docs/ui-reference/catalog.json and affected master PNGs
after actual rendered approval; stale references block the reference gate.
Maintain onboarding, concise README/changelog separation and rendered architecture/
feature diagrams. Use explicit UTF-8 and authoritative formatters.

Follow docs/EVIDENCE.md. Preserve raw failures/bytes in ignored versioned runs;
commit concise summaries/descriptors, never raw trees/ZIPs. Verify archive/member
hashes and give reviewers access with actual source/configuration/scope/gaps.
Local files and future URLs do not imply uploaded availability.

Before any push/release, follow docs/REVIEWS.md: stage all candidate contents,
snapshot digest, create exactly two fresh independent reviewers without inherited
history, and obtain explicit approvals of that exact candidate. Do not provide
the author's or other review's conclusions. Resolve blockers, rerun affected
checks, and use a new pair after content changes. Record actual identities/scope/
timestamps/verdicts in reviews/approvals.json, stage it, check gate, then commit.
Protected main requires PR + current host check; never bypass. The first reviewed
push into a NEW EMPTY repo may establish main before protection, never an existing repo.

Only perform authorized publication. Release builds need current structured counts,
coverage/gaps and linked Markdown/JSON reports with verified artifact/raw evidence/
source bindings. No credentials, unattended service, global config or Codex Goal
is implied. If fresh reviewers are unavailable, leave local work reviewable and
report the explicit missing gate instead of fabricating approvals.
