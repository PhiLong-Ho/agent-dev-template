# Agent development template

Spec-driven, agent-assisted development with usability review, requirement coverage,
two fresh final reviewers, protected PRs, CI and inspectable releases. Includes a
small replaceable Python CLI; application languages/build tools are configurable.

## Start a project

Click **Use this template**, clone your new repository, then:

```sh
git switch -c chore/project-setup
python tools/bootstrap.py init --name my-project --repository OWNER/REPO
python -m pip install -r requirements-dev.txt
git config core.hooksPath .githooks
python tools/quality.py
```

Follow [onboarding](docs/ONBOARDING.md) to adapt the stack, obtain fresh reviews,
open a PR and activate branch protection. Repository settings/secrets and global
agent configuration are not copied. AI reviews run in your agent session; CI
validates their recorded candidate approvals, not reviewer identity.

[Workflow](docs/WORKFLOW.md) · [Architecture](docs/ARCHITECTURE.md) ·
[Design](docs/DESIGN.md) · [Coverage](docs/coverage.md) ·
[Release guide](docs/RELEASING.md) · [Changelog](CHANGELOG.md)

For an existing project, use [the adoption guide and ready-to-use prompt](docs/ADOPTING.md).
