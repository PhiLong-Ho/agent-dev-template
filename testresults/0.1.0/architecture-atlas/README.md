# Architecture atlas verification

Documentation/policy only; runtime and test source are unchanged by this task.
The prior DexDroid release acceptance failures remain unresolved and unpublished.

- quality.py PASS; 95 passed, 1 skipped, zero failures/errors. Raw run: `testresults/0.1.0/runs/architecture-atlas-host/`.
- Coverage/requirements, document integrity, Ruff lint/format and skill validation
  PASS. The new architecture requirement is manual, not an automated expert gate.
- 15 current diagrams rendered with Mermaid CLI 12.0.0, neutral theme,
  size 1800 and Chrome. Exact source/block bindings and current PNG paths:
  `diagrams/final/current-inventory.json` within the bundle. Render artifacts include
  earlier failed/intermediate attempts; only the current inventory is approved.
- Reviewer `/root` inspected all 15 current PNGs. The architecture
  expert `/root/architecture_preflight` independently inspected source/policy and
  approved corrected semantics. This is diagram review, not product UI/golden,
  runtime/performance verification or either final-candidate approval.
- Feature inventory: 14 DexDroid owners and five template owners have overview and
  representative sequence pairs, linked source and failure/lifecycle boundaries.
  Manual workflow walkthrough covers local N/A, architectural impact, uncertain
  impact, consequential user questions, material departures and separate final reviews.
- No test edits or device reruns were needed for documentation-only work.
  The template Windows run skips the POSIX permissive-umask privacy case; this
  does not claim POSIX execution or broad platform acceptance.

[Archive descriptor](archive.json) records the verified ZIP/member hashes.
Actual ZIP: `artifacts/evidence/architecture-atlas-20261017/evidence.zip` in this
checkout. It is **local-only**, retained until explicit deletion; no upload or
remote durability is claimed. Both final reviewers have local access before the
template is published. Historical raw bytes and repaired render attempts stay
outside Git. Future Actions artifacts contain their own run, not this local bundle.

Commands: `python tools/coverage.py check`, requirement/document validators,
Ruff lint/format, `quick_validate.py .agents/skills/architecture-review`, and the
host command above. `validations.json`, raw streams and structured test outcomes
are retained. Source was unchanged during the template host run; subsequent
tracked edits are this concise evidence index, its descriptor, summary link and
a README navigation-separator correction. Prior host test/lint/format results are
reused because executable/test/configuration inputs are unchanged; document links
were revalidated on the corrected text. CI runs fresh host gates on the final commit.

[Change and expert decisions](../../../docs/changes/architecture-atlas.md) |
[Component map and feature atlas](../../../docs/architecture/README.md)
