# Testing and acceptance

`python tools/quality.py` runs requirement/coverage/link validation and configured
lint/format/test commands. Every attempt uses a new ignored evidence folder with
raw logs, source fingerprints, command exit codes and actual structured cases.
Failed/missing results fail the gate; skipped/expected failures remain separate.

Pure logic uses deterministic unit tests. Integrations/E2E use real observable
outcomes, explicit services/device/browser configuration and portable selectors.
Add stack-specific suites rather than describing the reference CLI as app coverage.
UI work needs representative actual renders, interactions, keyboard/input and
lifecycle states; maintain explicit exclusions. Reviewers inspect images, not only
assertion totals. Only a user/authorized reviewer can approve changed visual goldens.
Performance evidence needs declared setup, warmup, sample count, timing boundaries
and distributions; an eventual timeout is not a latency measurement.

After EVERY test source addition/edit/deletion, update concrete checks in
docs/requirements.json, run `python tools/coverage.py update`, inspect and commit
docs/coverage.md and docs/coverage-snapshot.json. Freshness hashes cover helpers too;
mapping status is never a pass rate. Keep manual/deferred gaps explicit.

Tooling fault tests use isolated temporary repositories/services and mock GitHub
publication. Messages printed by those fixtures are not actual remote publication.
Run shared device/environment suites sequentially and restore usability afterward.
Retain raw failures; follow [evidence policy](EVIDENCE.md).
