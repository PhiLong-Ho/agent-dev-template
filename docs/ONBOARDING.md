# Developer onboarding

Use [coding practice](CODING_PRACTICE.md) for daily implementation and test selection.
Attach [local monitoring](LOCAL_MONITORING.md) to observe long commands independently.

## Generate, install and understand

Use [GitHub templates](https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-repository-from-a-template)
or `gh repo create OWNER/NAME --template PhiLong-Ho/agent-dev-template --public --clone`.
Choose your own visibility. Templates copy files, not account permissions, secrets
or protection settings. Work on a branch before initialization:

```sh
git switch -c chore/project-setup
python tools/bootstrap.py init --name my-project --repository OWNER/NAME
python -m pip install -r requirements-dev.txt -r requirements-graph.txt
git config core.hooksPath .githooks
python tools/quality.py
python -m src.example Ada
```

Python 3.11+ and Git are required for tooling; Windows and Ubuntu run in CI.
Use a virtual environment if needed. Commands are the same in PowerShell/bash.
Initialization validates identity and replaces inherited approvals with an empty
unapproved record (the gate remains closed); it never resets
Git history, removes source or silently changes remote settings. Existing generated
baseline commits may carry historical template evidence; do not count it as your
project's testing or fresh approval. CI rejects an inherited repository identity
until initialization, then requires fresh reviews of the changed setup.

Read SPEC.md, [design](DESIGN.md), [architecture](ARCHITECTURE.md),
[feature index](specs/README.md), [workflow](WORKFLOW.md) and [coverage](coverage.md).
`src/` is replaceable example code; `tools/` implements workflow gates; tests live
in `tests/` and `tools/tests/`; `.agents/skills/` routes agent work.

Read the [code map and feature diagram atlas](architecture/README.md) before
choosing files to change. Every task records architecture impact; use the
[expert preflight](WORKFLOW.md#architecture-before-implementation) for possible or
uncertain architectural changes. Add the new feature to both inventories and
maintain its overview/sequence with its source, failure paths and verification gaps.

## Adapt to your stack

Edit project.json: project identity/version, `commands` (format/lint/build/test),
`test_results` and `release.build`/`release.artifacts`. Commands are argument arrays,
run without a shell; `{python}`, `{evidence}`, `{output}` and `{version}` are literal
supported replacements in their relevant context. Wrapper scripts can call npm,
Gradle, Cargo or other tools. Install those runtimes/dependencies in both CI files;
the Python tooling alone cannot validate your product build. Quality commands run
from the repository root; result filenames are relative to the fresh evidence folder.

Test adapters emit JSON schema 1: `source_commit` is `git rev-parse HEAD`; `cases`
contains unique nonblank IDs and statuses passed/failed/error/skipped/
expected_failure/unexpected_success. See tools/run_tests.py. Preserve real runner
outcomes including missing final status/crashes; do not turn timeout into a pass.

The supplied coverage scanner inventories Python unittest methods (and can parse
Java entrypoints via its helper). Adapt `TEST_ROOTS`/`cases()` for your test languages
and add behavioral tests for the adapter; reconcile every test addition/removal.
This is explicit stack adaptation, not automatic universal language discovery.
Replace the greeting requirement with real product requirements before claiming
application coverage. Maintain diagrams and product-specific design tokens/invariants.

## First reviewed change and repository activation

1. Configure your project/spec/design/tests, refresh coverage and run quality.
2. Complete two fresh independent reviews of the final staged digest; record real
   approvals and commit. Push the branch, open a PR and check CI. The template's
   historical approvals do not approve your changed setup.
3. On an authorized new repository, run `python tools/bootstrap.py protect` to
   require PRs, strict `host` checks and administrator enforcement. Check the API
   response/readback. A private repository may need an eligible GitHub plan.
   The command refuses existing protection or an uninspectable state. Reconcile
   existing stronger rules explicitly instead of replacing them with the starter.
4. Merge the reviewed setup PR only after `host` passes. Later changes always use
   protected PRs. Do not disable protection or bypass CI to merge.

The template publisher alone initially pushes the reviewed root commit to an
empty repository, then applies protection. This exception never applies to an
existing generated project, which already has a main branch.

No secret is required for quality CI or its recorded-review gate. Actual AI agent
sessions require your own enabled tools/account; CI does not spawn them. Signing,
deployment and external test services require project-specific secrets/permissions;
configure them explicitly rather than copying personal configuration.

## Daily commands and troubleshooting

Use [CONTRIBUTING](../CONTRIBUTING.md), [testing](TESTING.md),
[evidence](EVIDENCE.md) and [release instructions](RELEASING.md).
Stale coverage: reconcile checks then regenerate. Stale approvals: new pair of
reviewers. Missing test JSON: fix runner adapter/source identity. Unavailable raw
archive: report the gap; hashes cannot restore lost files. Permission/plan errors
applying protection are not successful setup. Never fix gates by forging results.

## Optional local graph setup and UI adaptation

Follow [graph-first setup](GRAPH_FIRST.md) once per machine for both clients;
restart and review Codex /hooks. Global settings/permissions are preserved and
backed up. Enable actual [UI references](ui-reference/README.md) when replacing
the CLI with a UI; declare source patterns/states before claiming freshness.

Before any version release, complete the
[release architecture checkpoint](RELEASING.md#release-architecture-review), even
for patches or docs-only. A fresh expert approves inspected inputs before the two
final reviewers; a task-level no-impact note cannot waive this release obligation.
