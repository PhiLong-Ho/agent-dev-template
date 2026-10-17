# Contributing

Read [onboarding](docs/ONBOARDING.md), [workflow](docs/WORKFLOW.md), SPEC.md and
the owning [feature contract](docs/specs/README.md). Python 3.11+, Git and pip are
needed for the starter. GitHub CLI is needed only for authorized remote operations.

```sh
python -m pip install -r requirements-dev.txt
python -m ruff format .
python tools/coverage.py update
python tools/quality.py
python tools/check_requirements.py
python tools/coverage.py check
python tools/check_docs.py
```

The quality runner prints its actual gates and retains ignored raw logs/results.
After every test change reconcile concrete checks in docs/requirements.json before
refreshing both coverage files. New format/lint findings fail; do not loosen gates
or snapshots to hide regressions. Actual E2E/visual/performance needs stack-specific
adapters and rendered/measured evidence; see [testing](docs/TESTING.md).

Stage all intended source/docs/compact evidence, follow [reviews](docs/REVIEWS.md),
record two actual fresh-agent approvals and check the gate before commit/push.
Use PRs for protected main. No deployment/release is implied by a code request.
