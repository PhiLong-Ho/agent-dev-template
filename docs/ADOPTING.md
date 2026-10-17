# Use this workflow in another project

For a new project, use the GitHub template and follow [onboarding](ONBOARDING.md).
For an existing repository, give your coding agent this prompt:

```text
Use https://github.com/PhiLong-Ho/agent-dev-template as the workflow reference
for this project. Read its AGENTS.md, docs/WORKFLOW.md and onboarding first.
Inspect our current stack, scripts, tests, CI, design conventions and repository
policies. Preserve working code/history and stricter existing rules. On a branch,
adapt the spec-first contracts, UI expert preflight/material-user-decision policy,
coverage freshness, shared design/architecture diagrams, evidence archiving,
developer onboarding, two fresh exact-candidate reviewer gate and protected PR/
release workflow to our actual stack. Do not copy template test outcomes,
historical approval records, product code, secrets or account configuration.
Add real behavior/failure tests for the adapters; run applicable checks and report
unverified cases. Clarify consequential unknowns before dependent work. Obtain
two fresh independent final approvals before any authorized push. Do not create
a Codex Goal or change external settings unless explicitly requested.
```

Do not overlay all template files blindly. Reconcile each existing command,
requirement ID, style component, test runner/report adapter, artifact/signing step
and branch rule. Keep existing pipeline capabilities; document what is replaced.
Inventory existing features using the Spec Kit-style template without treating
the backfill as new verification. Keep stable IDs, concrete mappings and scenario
gaps. Tests/frameworks outside the starter scanner need an explicit tested adapter.

Use [the architecture map](ARCHITECTURE.md) to identify reusable tools. Review the
copied tools as code: changes to assumptions, canonicalization, safe archive names,
review digest exclusions and release bindings require their acceptance tests.
Retain the target project's licensing/attribution requirements. Do not import
raw historical test trees or rewrite Git history during workflow adoption.

Local hooks, Actions permissions, branch protection, signing/deployment secrets,
agent access and billing are separate activation steps. Apply authorized remote
settings explicitly and inspect the result. Neither template generation nor this
prompt grants unrestricted publication or unattended external access.
