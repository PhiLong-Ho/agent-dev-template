# Evidence storage and retrieval

Raw logs, screenshots/traces, commands/outcomes and configuration/provenance live
under ignored `testresults/<version>/runs/<run>/`. Preserve bytes and failed attempts;
never force-add raw trees or ZIPs to Git. Track concise summary.md/README.md,
archive.json and release reports outside runs. CI bundles only its current run.

```sh
python tools/evidence.py pack --source testresults/0.1.0/runs/RUN --output artifacts/evidence/RUN --scope "Actual suites/configuration and gaps"
python tools/evidence.py verify --archive artifacts/evidence/RUN/evidence.zip --descriptor artifacts/evidence/RUN/archive.json
```

Use actual paths and a NEW output directory. Packing preserves originals, records
file/ZIP hashes and verifies its output; it rejects links, unsafe portable paths,
Windows aliases/device names, source mutation, existing output and empty runs.
A failed capture can leave an ignored .partial file; retry in a fresh directory.
Copy only archive.json into a tracked change folder and record source/build,
configuration, commands, outcomes, visual/performance scope and remaining gaps.
Packaging HEAD/dirty state describes packaging, not proof of the tested build.

The pack command does not upload. Descriptors identify local-only storage or a
target pending actual upload. Record real workflow/artifact/release locations and
availability after upload; unavailable/expired bytes remain a gap. Give both final
reviewers access and require ZIP/member verification before inspecting/extracting
into an ignored directory. Hashes prove consistency, not identity or test passes.

Actions artifacts request 14 days retention, subject to repository limits and run
deletion. Releases attach release-evidence.zip/json and report Markdown/JSON with
checksums; these outlive Actions retention until assets/releases are removed.
See [artifact retention](https://docs.github.com/en/actions/how-tos/writing-workflows/choosing-what-your-workflow-does/storing-and-sharing-data-from-a-workflow).
Local test bundles are not automatically uploaded by hosted CI. Transfer within
authorized scope; do not silently include unrelated content or rewrite originals.
